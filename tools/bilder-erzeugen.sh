#!/bin/sh
# Rendert die drei Bilddateien der Website aus ihren SVG-Quellen:
#
#     public/vorschau.png          1200x630, Open Graph — aus src/grafik/vorschau.svg
#     public/apple-touch-icon.png   180x180, iOS-Startbildschirm — aus src/grafik/signet.svg
#     public/favicon.ico             32x32, Browserleiste — aus src/grafik/signet.svg
#
#     tools/bilder-erzeugen.sh
#
# Braucht Chromium oder Chrome und python3. Die erzeugten Dateien sind
# versioniert, damit der normale Build keinen Browser braucht.
set -eu
cd "$(dirname "$0")/.."

# Der Browser heißt je nach System anders: unter Debian und Ubuntu chromium
# oder chromium-browser, auf den GitHub-Läufern google-chrome.
BROWSER=${BROWSER:-}
if [ -z "$BROWSER" ]; then
  for kandidat in chromium chromium-browser google-chrome google-chrome-stable chrome; do
    if command -v "$kandidat" >/dev/null 2>&1; then
      BROWSER=$kandidat
      break
    fi
  done
fi
[ -n "$BROWSER" ] || { echo "FEHLER: kein Chromium oder Chrome gefunden." >&2; exit 1; }

# Im Repository statt in /tmp: Ein als Snap installiertes Chromium darf dort
# nicht schreiben. Das Muster .build.*/ steht in .gitignore.
ARBEITSVERZEICHNIS=$(mktemp -d "$PWD/.build.bilder.XXXXXX")
trap 'rm -rf "$ARBEITSVERZEICHNIS"' EXIT HUP INT TERM

rendere() {
  # $1 Quelle, $2 Ziel, $3 Breite, $4 Höhe
  "$BROWSER" --headless --no-sandbox --disable-gpu --hide-scrollbars \
    --force-device-scale-factor=1 --window-size="$3,$4" \
    --screenshot="$2" "file://$PWD/$1" 2>/dev/null
  echo "  $2  $(stat -c%s "$2") B"
}

rendere src/grafik/vorschau.svg public/vorschau.png          1200 630
rendere src/grafik/signet.svg   public/apple-touch-icon.png   180 180
rendere src/grafik/signet.svg   "$ARBEITSVERZEICHNIS/favicon-32.png" 32 32

# ICO ist ein Behälter; seit Vista darf darin ein PNG stehen.
python3 - "$ARBEITSVERZEICHNIS/favicon-32.png" <<'PY'
import struct
import sys
from pathlib import Path

daten = Path(sys.argv[1]).read_bytes()
kopf = struct.pack("<HHH", 0, 1, 1)
eintrag = struct.pack("<BBBBHHII", 32, 32, 0, 0, 1, 32, len(daten), 6 + 16)
Path("public/favicon.ico").write_bytes(kopf + eintrag + daten)
PY
echo "  public/favicon.ico  $(stat -c%s public/favicon.ico) B"
