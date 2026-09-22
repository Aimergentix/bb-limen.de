"""Erzeugt eine vollständige statische Website, ohne Quellen zu überschreiben.

Includes werden nur zeilenweise und in der festgelegten Reihenfolge eingesetzt.
Alle Eingaben werden vor dem Ersetzen der bisherigen Ausgabe verarbeitet.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
from pathlib import Path
import re
import sys
import tempfile
from urllib.parse import urlsplit, urljoin

from site_config import ROOT, PARTIALS, base_url, load_catalog, read_source
from bureau_data import load_office, render_office, vcard

INCLUDE = re.compile(r"<!-- @include ([a-z-]+) -->\n?")
CURRENT = re.compile(r"%%CUR-([a-z0-9-]+)%%")


def error_page_links(source: str) -> str:
    """Dateiziele der 404-Seite bleiben auch unter tiefen Fehleradressen gültig.

    Ein base-Element würde auch den Sprunglink auf die Startseite umlenken.
    Deshalb werden nur relative Dateiziele in HTML-Tags absolut zur Domain.
    """
    # HTMLParser zählt Zeilen nur an \n. str.splitlines trennt auch an \r,
    # \x85 oder U+2028 und verschöbe dann jede folgende Ersetzung.
    offsets = [0]
    for line in source.split("\n"):
        offsets.append(offsets[-1] + len(line) + 1)
    replacements = []

    def replace(match: re.Match) -> str:
        value = match[3]
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path or value.startswith("/"):
            return match[0]
        return match[1] + match[2] + urljoin("/", value) + match[2]

    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            raw = self.get_starttag_text()
            updated = re.sub(r'''(\b(?:href|src)\s*=\s*)(["'])(.*?)\2''', replace, raw)
            if raw != updated:
                line, column = self.getpos()
                start = offsets[line - 1] + column
                if source[start:start + len(raw)] != raw:
                    raise ValueError(f"404.html:{line}: Verweis nicht eindeutig zu verankern")
                replacements.append((start, start + len(raw), updated))

    parser = Links(convert_charrefs=False)
    parser.feed(source)
    parser.close()
    for start, end, updated in reversed(replacements):
        source = source[:start] + updated + source[end:]
    return source


def sitemap(catalog: dict, root: Path) -> bytes:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    base = base_url(root)
    for page in catalog["pages"]:
        if page["sitemap"]:
            url = base + ("" if page["file"] == "index.html" else page["file"])
            lines.extend(["  <url>", f"    <loc>{url}</loc>",
                          f"    <lastmod>{page['lastmod']}</lastmod>", "  </url>"])
    return ("\n".join([*lines, "</urlset>"]) + "\n").encode("utf-8")


def render(root: Path = ROOT) -> dict[str, bytes]:
    catalog = load_catalog(root)
    office = load_office(root)
    pages = catalog["pages"]
    names = {page["file"] for page in pages}
    # R-QUELLE-1, R-QUELLE-3: Root-Kopien sehen wie Quellen aus, werden aber
    # nicht veröffentlicht. Eine Änderung dort darf nicht unbemerkt bleiben.
    misplaced = sorted(path.name for path in root.iterdir()
                       if path.name in names | set(catalog["public_files"]) |
                       {"style.css", "sitemap.xml", "bb-limen.vcf"})
    if misplaced:
        raise ValueError(f"{root}: öffentliche Dateien am falschen Ort: {misplaced}; Quellen gehören nach src/ oder public/")
    for directory, expected in (
        (root / "src/pages", names),
        (root / "src/partials", {f"{name}.html" for name in PARTIALS}),
        (root / "public", set(catalog["public_files"])),
    ):
        if directory.is_symlink() or not directory.is_dir():
            raise ValueError(f"{directory}: reguläres Verzeichnis fehlt")
        actual = {path.name for path in directory.iterdir()}
        if actual != expected:
            raise ValueError(f"{directory}: fehlt {sorted(expected - actual)}, unerwartet {sorted(actual - expected)}")
    partials = {}
    for name in PARTIALS:
        path = root / "src/partials" / f"{name}.html"
        text = read_source(path).decode("utf-8")
        if "@include" in text or "<!-- #" in text or "<!-- /#" in text:
            raise ValueError(f"{path}: verschachtelte Includes oder alte Bausteinmarken")
        partials[name] = text
    result = {}
    for page in pages:
        path = root / "src/pages" / page["file"]
        source = read_source(path).decode("utf-8")
        output = []
        seen = []
        for number, line in enumerate(source.splitlines(keepends=True), 1):
            match = INCLUDE.fullmatch(line)
            if match:
                name = match[1]
                if len(seen) >= len(PARTIALS) or name != PARTIALS[len(seen)]:
                    raise ValueError(f"{path}:{number}: unbekanntes, doppeltes oder falsch angeordnetes Include {name}")
                seen.append(name)
                output.append(f"<!-- #{name} -->\n{partials[name]}<!-- /#{name} -->\n")
            else:
                if "@include" in line or "<!-- #" in line or "<!-- /#" in line:
                    raise ValueError(f"{path}:{number}: Include muss allein stehen; generierte Blöcke gehören nicht in Quellen")
                output.append(line)
        if tuple(seen) != PARTIALS:
            raise ValueError(f"{path}: fehlende Includes, erwartet {', '.join(PARTIALS)}")
        text = "".join(output)
        for match in CURRENT.finditer(text):
            if match[1] + ".html" not in names:
                raise ValueError(f"{path}: unbekanntes Navigationsziel {match[1]}")
        text = CURRENT.sub(lambda match: ' aria-current="page"' if match[1] + ".html" == page["file"] else "", text)
        if "%%CUR-" in text:
            raise ValueError(f"{path}: ungültiger Navigationsplatzhalter")
        text = render_office(text, office)
        if page["file"] == "404.html":
            text = error_page_links(text)
        result[page["file"]] = text.encode("utf-8")
    result["style.css"] = read_source(root / "src/style.css")
    result["sitemap.xml"] = sitemap(catalog, root)
    result["bb-limen.vcf"] = vcard(result["index.html"].decode("utf-8"))
    for name in catalog["public_files"]:
        result[name] = read_source(root / "public" / name)
    return result


def check_output(files: dict[str, bytes], output: Path) -> None:
    if output.is_symlink() or not output.is_dir():
        raise ValueError(f"{output}: Ausgabe fehlt; zuerst tools/build.sh ausführen")
    actual = {path.name for path in output.iterdir()}
    if actual != set(files):
        raise ValueError(f"{output}: fehlende oder unerwartete Dateien: {sorted(actual ^ set(files))}")
    for name, data in files.items():
        if read_source(output / name) != data:
            raise ValueError(f"{output / name}: weicht von den Quellen ab; tools/build.sh ausführen")


def write_output(files: dict[str, bytes], output: Path, root: Path = ROOT) -> None:
    # Fremde Verzeichnisse werden niemals geleert. Nur das definierte dist/
    # darf ersetzt werden; --output ist für neue temporäre Verzeichnisse da.
    if output.is_symlink():
        raise ValueError(f"{output}: Ausgabe darf kein Symlink sein")
    output = output.resolve()
    root = root.resolve()
    if (output == root or root in output.parents) and output != root / "dist":
        raise ValueError(f"{output}: im Repository ist ausschließlich dist/ als Ausgabe erlaubt")
    if output.exists() and (output != root / "dist" or not output.is_dir()):
        raise ValueError(f"{output}: vorhandene Ausgabe außerhalb von dist/ wird nicht ersetzt")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".build.", dir=output.parent) as temp:
        stage = Path(temp) / "neu"
        stage.mkdir()
        for name, data in files.items():
            (stage / name).write_bytes(data)
        old = Path(temp) / "alt"
        if output.exists():
            output.rename(old)
        try:
            stage.rename(output)
        except OSError:
            if old.exists():
                old.rename(output)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="bestehende Ausgabe nur prüfen")
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="neues Ausgabe-Verzeichnis (Standard: dist/)")
    args = parser.parse_args()
    try:
        files = render()
        if args.check:
            check_output(files, args.output)
            print(f"Geprüft: {len(files)} Dateien entsprechen den Quellen.")
        else:
            write_output(files, args.output)
            print(f"Erzeugt: {len(files)} Dateien in {args.output}")
    except (OSError, ValueError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
