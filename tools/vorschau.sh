#!/bin/sh
# Rendert die drei Bilddateien der Website aus ihren SVG-Quellen:
#
#     vorschau.png          1200x630, Open Graph — aus tools/vorschau.svg
#     apple-touch-icon.png   180x180, iOS-Startbildschirm — aus tools/signet.svg
#     favicon.ico             32x32, Browserleiste — aus tools/signet.svg
#
#     tools/vorschau.sh
#
# Braucht chromium und python3. Die erzeugten Dateien sind versioniert,
# damit die Website ohne Werkzeugkette auslieferbar bleibt.
set -eu
cd "$(dirname "$0")/.."

rendere() {
  # $1 Quelle, $2 Ziel, $3 Breite, $4 Hoehe
  chromium --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=1 --window-size="$3,$4" \
    --screenshot="$2" "file://$PWD/$1" 2>/dev/null
  echo "  $2  $(stat -c%s "$2") B"
}

rendere tools/vorschau.svg vorschau.png          1200 630
rendere tools/signet.svg   apple-touch-icon.png   180 180
rendere tools/signet.svg   .favicon-32.png         32  32

# ICO ist ein Behaelter; seit Vista darf darin ein PNG stehen.
python3 - <<'PY'
import struct
from pathlib import Path

png = Path(".favicon-32.png")
daten = png.read_bytes()
kopf = struct.pack("<HHH", 0, 1, 1)
eintrag = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(daten), 6 + 16)
Path("favicon.ico").write_bytes(kopf + eintrag + daten)
png.unlink()
PY
echo "  favicon.ico  $(stat -c%s favicon.ico) B"
