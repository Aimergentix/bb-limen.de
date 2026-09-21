"""Gemeinsamer, streng geprüfter Seitenkatalog. Nur Python-Standardbibliothek."""
from __future__ import annotations

from datetime import date
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
LANGUAGES = {
    "einfach": "A2/B1-Ziel",
    "fach": "Fachsprache, nur Statistik",
    "recht": "Pflichttext, nur Statistik",
    "leicht": "Leichte Sprache, Zielgruppenprüfung bleibt nötig",
    "fehler": "Fehlerseite, nur Statistik",
}
PARTIALS = ("head", "skip", "rail", "foot", "callbar")


def read_source(path: Path) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{path}: reguläre Datei fehlt oder ist ein Symlink")
    data = path.read_bytes()
    if not data:
        raise ValueError(f"{path}: Datei ist leer")
    return data


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"seiten.json: doppelter Schlüssel {key}")
        result[key] = value
    return result


def load_catalog(root: Path = ROOT) -> dict:
    path = root / "src/seiten.json"
    catalog = json.loads(read_source(path), object_pairs_hook=unique_object)
    if not isinstance(catalog, dict) or set(catalog) != {"pages", "public_files"}:
        raise ValueError(f"{path}: erwartet pages und public_files")
    pages = catalog["pages"]
    if not isinstance(pages, list) or not pages:
        raise ValueError(f"{path}: pages muss eine nicht leere Liste sein")
    names = []
    for page in pages:
        if not isinstance(page, dict) or set(page) - {"file", "language", "sitemap", "lastmod"}:
            raise ValueError(f"{path}: ungültiger Seiteneintrag")
        name = page.get("file")
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.html", name):
            raise ValueError(f"{path}: ungültiger Dateiname {name!r}")
        if not isinstance(page.get("language"), str) or page["language"] not in LANGUAGES or type(page.get("sitemap")) is not bool:
            raise ValueError(f"{path}: {name}: language oder sitemap ist ungültig")
        if page["sitemap"]:
            value = page.get("lastmod")
            if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
                raise ValueError(f"{path}: {name}: lastmod muss YYYY-MM-DD sein")
            date.fromisoformat(value)
        elif "lastmod" in page:
            raise ValueError(f"{path}: {name}: lastmod ohne Sitemap-Eintrag")
        names.append(name)
    if len(names) != len(set(names)) or "index.html" not in names or "404.html" not in names:
        raise ValueError(f"{path}: doppelte Seiten oder fehlende index.html/404.html")
    public = catalog["public_files"]
    if not isinstance(public, list) or not public or any(
        not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", name)
        for name in public
    ):
        raise ValueError(f"{path}: ungültige public_files")
    if len(public) != len(set(public)) or set(public) & {*names, "style.css", "sitemap.xml", "bb-limen.vcf"}:
        raise ValueError(f"{path}: doppelte oder kollidierende öffentliche Dateien")
    if "CNAME" not in public:
        raise ValueError(f"{path}: CNAME fehlt")
    return catalog


def base_url(root: Path = ROOT) -> str:
    domain = read_source(root / "public/CNAME").decode("utf-8").strip()
    if not re.fullmatch(r"[a-z0-9]+(?:[.-][a-z0-9]+)*\.[a-z]{2,}", domain):
        raise ValueError("public/CNAME: ungültiger Domainname")
    return f"https://{domain}/"
