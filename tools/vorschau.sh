#!/bin/sh
# Rendert die drei Bilddateien der Website aus ihren SVG-Quellen:
#
#     vorschau.png          1200x630, Open Graph — aus src/grafik/vorschau.svg
#     apple-touch-icon.png   180x180, iOS-Startbildschirm — aus src/grafik/signet.svg
#     favicon.ico             32x32, Browserleiste — aus src/grafik/signet.svg
#
#     tools/vorschau.sh
#
# Braucht chromium und python3. Die erzeugten Dateien sind versioniert,
# damit der normale Build keinen Browser braucht.
set -eu
# shellcheck source=tools/browser.sh
. "$(dirname "$0")/browser.sh"
cd "$(dirname "$0")/.."

rendere() {
  # $1 Quelle, $2 Ziel, $3 Breite, $4 Hoehe
  "$BROWSER" --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=1 --window-size="$3,$4" \
    --screenshot="$2" "file://$PWD/$1" 2>/dev/null
  echo "  $2  $(stat -c%s "$2") B"
}

rendere src/grafik/vorschau.svg public/vorschau.png          1200 630
rendere src/grafik/signet.svg   public/apple-touch-icon.png   180 180
rendere src/grafik/signet.svg   .favicon-32.png         32  32

# ICO ist ein Behaelter; seit Vista darf darin ein PNG stehen.
python3 - <<'PY'
import struct
from pathlib import Path

png = Path(".favicon-32.png")
daten = png.read_bytes()
kopf = struct.pack("<HHH", 0, 1, 1)
eintrag = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(daten), 6 + 16)
Path("public/favicon.ico").write_bytes(kopf + eintrag + daten)
png.unlink()
PY
echo "  favicon.ico  $(stat -c%s public/favicon.ico) B"
