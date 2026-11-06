"""Erzeugt und prüft QR-PNGs aus den vCard-Bytes des Website-Builds.

Der Build verwendet generate() und schreibt die geprüften Bilder nach
dist/qrcodes/. Die CLI exportiert gesondert Kopien für Handouts und E-Mails:

    python tools/generate_qrcodes.py          aktualisiert dokumente/assets/
    python tools/generate_qrcodes.py --check  liest die Dokumentbilder zurück

Website-Build, Hook und CI benötigen keine versionierten QR-Bilder.
Benötigt die Pakete aus tools/requirements-qrcodes.txt.
"""
from __future__ import annotations

import argparse
from io import BytesIO
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

ROOT = Path(__file__).resolve().parents[1]

import qrcode
from PIL import Image

# ---------------------------------------------------------------- Konfiguration

ASSETS_DIR = ROOT / "dokumente" / "assets"   # Handouts in dokumente/
LOGO = ROOT / "public" / "apple-touch-icon.png"
TARGET_PX = 360        # Mindestens 2x der Anzeige mit 180 px; ganze Module erhalten.
BORDER = 4             # Ruhezone in Modulen
LOGO_RATIO = 0.20      # Signet maximal 20 % der Kantenlänge, mit weißem Pad
FILL = "black"        # Scanfläche bleibt unabhängig von Hell-/Dunkeldarstellung.
BACK = "white"
QR_SUFFIX = "-qr.png"


def render_png(payload: bytes, logo_path: Path = LOGO) -> bytes:
    """QR-Code als PNG mit Fehlerkorrektur H (wegen des Logos) und Signet mittig."""
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, border=BORDER)
    qr.add_data(payload, optimize=0)  # Bytes: 8-bit-Modus, UTF-8 bleibt erhalten
    qr.make(fit=True)
    qr.box_size = max(4, -(-TARGET_PX // (len(qr.modules) + 2 * BORDER)))
    img = qr.make_image(fill_color=FILL, back_color=BACK).convert("RGB")
    # Das weiße Pad zählt zur maximalen Abdeckung von 20 Prozent.
    plate_px = max(5, int(img.width * LOGO_RATIO))
    pad = max(2, plate_px // 8)
    with Image.open(logo_path) as source:
        if source.format == "ICO":
            source = source.ico.getimage(max(source.ico.sizes(), key=lambda size: size[0] * size[1]))
        logo = source.convert("RGBA")
    logo.thumbnail((plate_px - 2 * pad, plate_px - 2 * pad), Image.Resampling.LANCZOS)
    plate = Image.new("RGB", (plate_px, plate_px), BACK)
    plate.paste(logo, ((plate_px - logo.width) // 2, (plate_px - logo.height) // 2), logo)
    img.paste(plate, ((img.width - plate.width) // 2, (img.height - plate.height) // 2))
    buffer = BytesIO()
    img.save(buffer, "PNG", optimize=True)
    return buffer.getvalue()


def verify_bytes(data: bytes, payload: bytes, name: str) -> None:
    """ZXing decodiert die PNG-Datei; auch Umlaute und CRLF müssen bytegleich sein."""
    import zxingcpp
    try:
        with Image.open(BytesIO(data)) as source:
            image = source.convert("RGB")
    except OSError as error:
        raise RuntimeError(f"{name}: PNG nicht lesbar") from error
    decoded = zxingcpp.read_barcode(image, formats=zxingcpp.BarcodeFormat.QRCode)
    if decoded is None or decoded.bytes != payload:
        raise RuntimeError(f"{name}: zurückgelesener Inhalt weicht von der vCard ab")


def generate(cards: dict[str, bytes], logo_path: Path = LOGO) -> dict[str, bytes]:
    """Alle PNGs im Speicher erzeugen und vor jeder Ausgabe zurücklesen."""
    result = {}
    for slug, payload in cards.items():
        try:
            data = render_png(payload, logo_path)
            verify_bytes(data, payload, slug)
        except ImportError as error:
            raise ValueError("QR-Rücklesetest: Abhängigkeiten fehlen; "
                             "python -m pip install -r tools/requirements-qrcodes.txt ausführen") from error
        except (OSError, ValueError, RuntimeError) as error:
            raise ValueError(f"QR-Code {slug}: {error}") from error
        result[slug] = data
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="Dokumentbilder nur zurücklesen und mit aktuellen vCards vergleichen")
    args = parser.parse_args()
    # Nur der eigenständige Dokument-Export braucht den Build; kein Importkreis.
    from build import render
    try:
        files = render()
        cards = {Path(name).stem: data for name, data in files.items() if name.endswith(".vcf")}
        if args.check:
            for slug, payload in cards.items():
                path = ASSETS_DIR / f"{slug}{QR_SUFFIX}"
                verify_bytes(path.read_bytes(), payload, str(path))
        else:
            ASSETS_DIR.mkdir(parents=True, exist_ok=True)
            # render() hat bereits jedes Bild geprüft. Nur geänderte Kopien ersetzen.
            for slug in cards:
                path = ASSETS_DIR / f"{slug}{QR_SUFFIX}"
                data = files[f"qrcodes/{slug}.png"]
                if not path.exists() or path.read_bytes() != data:
                    temporary = path.with_suffix(".png.neu")
                    temporary.write_bytes(data)
                    temporary.replace(path)
                    print(f"erzeugt: {path.relative_to(ROOT)}")
            for path in ASSETS_DIR.glob(f"*{QR_SUFFIX}"):
                if path.name.removesuffix(QR_SUFFIX) not in cards:
                    path.unlink()
                    print(f"entfernt: {path.relative_to(ROOT)}")
    except (OSError, ValueError, RuntimeError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1
    print(f"Dokument-QR-Codes geprüft: {len(cards)} Kontakte, Rücklesen erfolgreich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
