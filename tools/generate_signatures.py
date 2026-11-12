"""Erzeugt lokale Thunderbird-Signaturen aus den aktuellen Website-Builddaten.

    python tools/generate_signatures.py

Vorlage: src/signatures/; Ausgabe: dokumente/signaturen/.
"""
from __future__ import annotations

import argparse
import base64
from html import escape
from io import BytesIO
import json
from pathlib import Path
import re
import sys
from urllib.parse import urljoin

from PIL import Image
import qrcode
import zxingcpp

ROOT = Path(__file__).resolve().parents[1]


def address_lines(address):
    first = (f"Postfach {address['postfach']}" if "postfach" in address
             else address["strasse"])
    return "<br>".join(escape(line) for line in
                        (first, f"{address['plz']} {address['ort']}"))


def qr_display_size(png, payload):
    """Ganze QR-Module anzeigen und auch die verkleinerte Fassung zurücklesen."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=4)
    qr.add_data(payload, optimize=0)
    qr.make(fit=True)
    modules = len(qr.get_matrix())
    with Image.open(BytesIO(png)) as source:
        for scale in (1, 2, 3):
            size = modules * scale
            resized = source.resize((size, size), Image.Resampling.LANCZOS)
            result = zxingcpp.read_barcode(resized)
            if result is not None and result.bytes == payload:
                return size
    raise ValueError("Signatur-QR-Code ist in keiner Anzeigegröße lesbar")


def render(root=ROOT, website=None):
    """Alle lokalen Ausgaben vorbereiten; dabei keine Dateien schreiben."""
    from build import base_url, load_office, load_people, render as render_website

    root = Path(root).resolve()
    website = render_website(root) if website is None else website
    office, people = load_office(root), load_people(root)
    # Die Bürokarte hat eine eigene Identität und keine persönliche Funktionszeile.
    contacts = [*people, {
        "kennung": "bb-limen", "name": office["geschaeftsbezeichnung"],
        "beruf": "", "registrierung": "", "telefon": office["telefon"],
        "email": office["email"], "anschrift": office["postanschrift"],
    }]
    base = base_url(root)
    source = root / "src/signatures"
    template = (source / "signature.html").read_text(encoding="utf-8")
    settings = json.loads((source / "settings.json").read_text(encoding="utf-8"))
    css = (root / "src/style.css").read_text(encoding="utf-8")
    palette = dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})",
                              css.split(":root {", 1)[1].split("}", 1)[0]))
    output = {}
    folder = Path("dokumente/signaturen")
    for person in contacts:
        slug = person["kennung"]
        is_office = slug == "bb-limen"
        role = "" if is_office else settings.get("roles", {}).get(slug, person["beruf"])
        phone = person["telefon"] or office["telefon"]
        png = website[f"qrcodes/{slug}.png"]
        vcard = website[f"{slug}.vcf"]
        size = qr_display_size(png, vcard)
        image_path = folder / "assets" / f"{slug}.png"
        values = {
            "NAME": escape(person["name"]),
            "ROLE_LINE": "<br>\n          " + escape(role) if role else "",
            "ORGANIZATION": escape(office["betreiber"]["name"] if is_office
                                   else office["geschaeftsbezeichnung"]),
            "ADDRESS": address_lines(person["anschrift"] or office["postanschrift"]),
            "EMAIL": escape(person["email"] or office["email"], quote=True),
            "PHONE_URI": escape(phone["e164"], quote=True),
            "PHONE": escape(phone["sichtbar"]),
            "VCARD_URL": escape(urljoin(base, f"{slug}.vcf"), quote=True),
            "BASE_URL": escape(base, quote=True),
            "QR_URI": "data:image/png;base64," + base64.b64encode(png).decode("ascii"),
            "QR_SIZE": str(size), "QR_COLUMN": str(size + 34),
            **{f"COLOR:{key}": value for key, value in palette.items()},
        }
        def replace(match):
            try:
                return values[match[1]]
            except KeyError:
                raise ValueError(f"Unbekannter Signaturplatzhalter: {match[1]}") from None
        variant = re.sub(r"<!-- @office-only -->(.*?)<!-- /@office-only -->",
                         lambda match: match[1] if is_office else "", template, flags=re.S)
        html = re.sub(r"%%([A-Za-z0-9:_-]+)%%", replace, variant).encode("utf-8")
        output[str(folder / f"{slug}.html")] = html
        output[str(image_path)] = png
        output[str(folder / f"{slug}.vcf")] = vcard
    return output


def install(files, directory):
    """Eigenständige HTML-Dateien ohne Begleitbilder in den gewählten Ordner kopieren."""
    directory = Path(directory).expanduser().resolve()
    directory.mkdir(parents=True, exist_ok=True)
    for name, data in files.items():
        if not name.endswith(".html"):
            continue
        target = directory / Path(name).name
        if not target.exists() or target.read_bytes() != data:
            temporary = target.with_name(target.name + ".neu")
            temporary.write_bytes(data)
            temporary.replace(target)


def write_output(files, root=ROOT):
    """Nur generierte Dateien ersetzen; andere Repository-Dateien bleiben erhalten."""
    root = Path(root)
    for name, data in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        if not path.exists() or path.read_bytes() != data:
            temporary = path.with_name(path.name + ".neu")
            temporary.write_bytes(data)
            temporary.replace(path)
    config = root / ".signature-output.json"
    if config.exists():
        directory = json.loads(config.read_text(encoding="utf-8"))["directory"]
        install(files, directory)


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--install-dir", type=Path,
                        help="HTML-Dateien hier ablegen und den Zielordner lokal für künftige Builds merken")
    args = parser.parse_args()
    try:
        files = render()
        write_output(files)
        if args.install_dir is not None:
            directory = args.install_dir.expanduser().resolve()
            install(files, directory)
            config = ROOT / ".signature-output.json"
            temporary = config.with_name(config.name + ".neu")
            temporary.write_text(json.dumps({"directory": str(directory)}, ensure_ascii=False,
                                            indent=2) + "\n", encoding="utf-8")
            temporary.replace(config)
            print(f"Signaturen installiert: {directory}")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1
    print(f"Lokale Signaturen erzeugt: {ROOT / 'dokumente/signaturen'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
