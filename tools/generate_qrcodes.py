"""Erzeugt die QR-Code-PNGs für das Büro und die betreuenden Personen.

Aufruf:

    .venv-documents/bin/python tools/generate_qrcodes.py           erzeugt neu
    .venv-documents/bin/python tools/generate_qrcodes.py --check   prüft nur

Die Kontaktdaten kommen aus denselben Quellen wie die Website
(src/bureauangaben.json, src/betreuende.json); kodiert wird exakt die vCard,
die tools/build.py als .vcf in dist/ erzeugt. Ausgabe je Kontakt:

    public/<kennung>-qr.png          Website (in src/seiten.json registriert)
    dokumente/assets/<kennung>-qr.png  Handouts (PDF, HTML, EML)

Bestehende Dateien werden nur überschrieben, wenn sich der Inhalt ändert
(Hash-Vergleich der PNG-Daten); Codes entfallener Personen werden entfernt.
Nach dem Schreiben wird jeder Code mit OpenCV testweise zurückgelesen und
mit der vCard verglichen. --check schreibt nichts und endet mit 1, sobald
ein Code fehlt oder veraltet ist (Hook und CI).

Benötigt qrcode, Pillow, cairosvg (Signet als SVG) und opencv-python-headless:
.venv-documents/bin/python -m pip install -r tools/requirements-qrcodes.txt
"""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build import (ROOT, base_url, load_office, load_people, office_vcard,
                   person_vcard, read_source, render_office)

import cairosvg
import qrcode
from PIL import Image

# ---------------------------------------------------------------- Konfiguration

PUBLIC_DIR = ROOT / "public"                  # Website; in src/seiten.json unter public_files
ASSETS_DIR = ROOT / "dokumente" / "assets"   # Handouts in dokumente/
LOGO = ROOT / "src" / "grafik" / "signet.svg"  # Signet, Quelle der Favicons
TARGET_PX = 296        # PNG-Kantenlänge in Pixeln: 2x der Anzeige mit 148 px (Retina)
BORDER = 4             # Ruhezone in Modulen
LOGO_RATIO = 0.20      # Signet maximal 20 % der Kantenlänge, mit weißem Pad
FILL = "#14181c"       # --ink aus PALETTE: dunkle Module auf weiß
BACK = "#ffffff"
OFFICE_SLUG = "bb-limen"
QR_SUFFIX = "-qr.png"


def payloads() -> dict[str, bytes]:
    """vCard je Kontakt als Bytes — dieselben, die der Website-Build als .vcf schreibt."""
    office = load_office(ROOT)
    people = load_people(ROOT)
    # Die vCard liest das erzeugte JSON-LD; dafür die Büro-Platzhalter auflösen.
    index = render_office(read_source(ROOT / "src" / "pages" / "index.html").decode("utf-8"), office)
    base = base_url(ROOT)
    result = {OFFICE_SLUG: office_vcard(index, office)}
    for person in people:
        result[person["kennung"]] = person_vcard(person, index, office, base)
    for slug, payload in result.items():
        text = payload.decode("utf-8")
        # Pflichtfelder: Name und mindestens Telefon oder E-Mail.
        if "FN:" not in text or ("TEL" not in text and "EMAIL" not in text):
            raise ValueError(f"{slug}: vCard ohne FN oder ohne TEL/EMAIL — src/bureauangaben.json bzw. src/betreuende.json prüfen")
    return result


def render_png(payload: bytes) -> bytes:
    """QR-Code als PNG mit Fehlerkorrektur H (wegen des Logos) und Signet mittig."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=BORDER)
    qr.add_data(payload)  # Bytes: 8-bit-Modus, UTF-8 bleibt erhalten
    qr.make(fit=True)
    qr.box_size = max(1, round(TARGET_PX / (len(qr.modules) + 2 * BORDER)))
    img = qr.make_image(fill_color=FILL, back_color=BACK).convert("RGB")
    logo_px = max(1, int(img.width * LOGO_RATIO))
    logo_png = cairosvg.svg2png(url=str(LOGO), output_width=logo_px, output_height=logo_px)
    logo = Image.open(BytesIO(logo_png)).convert("RGBA")
    pad = max(2, logo_px // 6)
    plate = Image.new("RGB", (logo.width + 2 * pad, logo.height + 2 * pad), BACK)
    plate.paste(logo, (pad, pad), logo)
    img.paste(plate, ((img.width - plate.width) // 2, (img.height - plate.height) // 2))
    buffer = BytesIO()
    img.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def verify(path: Path, payload: bytes) -> None:
    """Liest den geschriebenen Code zurück und vergleicht ihn mit der vCard.

    Der OpenCV-Detektor ist größen- und interpolationabhängig; deshalb wird
    das PNG in mehreren Stufen vergrößert, bis der Inhalt stimmt.
    """
    import cv2  # opencv-python-headless; erst beim Lesen laden
    detector = cv2.QRCodeDetector()
    image = cv2.imread(str(path))
    if image is None:
        raise RuntimeError(f"{path}: PNG nicht lesbar")
    want = payload.decode("utf-8")
    for interpolation in (cv2.INTER_NEAREST, cv2.INTER_LINEAR):
        for scale in (1, 2, 3, 4):
            scaled = cv2.resize(image, None, fx=scale, fy=scale, interpolation=interpolation)
            ok, decoded, _, _ = detector.detectAndDecodeMulti(scaled)
            if any(text == want for text in decoded if text):
                return
            text, _, _ = detector.detectAndDecode(scaled)
            if text == want:
                return
    raise RuntimeError(f"{path}: zurückgelesener Inhalt weicht von der vCard ab")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="nichts schreiben; exit 1, sobald ein Code fehlt oder veraltet ist")
    args = parser.parse_args()
    try:
        cards = payloads()
        expected = {slug: render_png(payload) for slug, payload in cards.items()}
    except (OSError, ValueError, RuntimeError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1

    directories = (PUBLIC_DIR, ASSETS_DIR)
    stale = [path for directory in directories
             for path in sorted(directory.glob(f"*{QR_SUFFIX}"))
             if path.name.removesuffix(QR_SUFFIX) not in expected]
    outdated = [directory / f"{slug}{QR_SUFFIX}"
                for directory in directories
                for slug, data in sorted(expected.items())
                if not (directory / f"{slug}{QR_SUFFIX}").exists()
                or (directory / f"{slug}{QR_SUFFIX}").read_bytes() != data]

    if args.check:
        for path in outdated:
            print(f"veraltet oder fehlend: {path.relative_to(ROOT)}")
        for path in stale:
            print(f"übrig (Person entfallen): {path.relative_to(ROOT)}")
        if outdated or stale:
            print("FEHLER: QR-Codes neu erzeugen mit "
                  ".venv-documents/bin/python tools/generate_qrcodes.py", file=sys.stderr)
            return 1
        print(f"QR-Codes aktuell: {len(expected)} Kontakte.")
        return 0

    for path in outdated:
        path.write_bytes(expected[path.name.removesuffix(QR_SUFFIX)])
        print(f"erzeugt: {path.relative_to(ROOT)}")
    for path in stale:
        path.unlink()
        print(f"entfernt: {path.relative_to(ROOT)}")
    try:
        for directory in directories:
            for slug, payload in sorted(cards.items()):
                verify(directory / f"{slug}{QR_SUFFIX}", payload)
    except RuntimeError as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1
    print(f"QR-Codes geprüft: {len(cards)} Kontakte, je 2 Dateien, Rücklesen erfolgreich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
