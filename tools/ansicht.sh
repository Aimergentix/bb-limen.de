#!/bin/sh
# Rendert die Seiten in einen Ordner — Grundlage fuer den Bildvergleich.
#
#     tools/ansicht.sh <zielordner> [port] [quellordner]
#
# Der Quellordner ist voreingestellt das eigene Projektverzeichnis. Fuer
# einen Vergleich mit einem frueheren Stand zeigt er auf ein git worktree —
# ohne diesen Schalter wuerde zweimal derselbe Stand gerendert.
#
# Zwei Breiten je Seite: 1280 fuer den Schreibtisch, 390 fuer das Telefon,
# wo aus der stehenden Kolumne ein Kopfband wird. Braucht chromium und
# startet sich einen eigenen Webserver.
#
# Chromium im Snap darf nicht nach /tmp schreiben — der Zielordner sollte
# deshalb unterhalb von $HOME oder im Projekt liegen.
set -eu
. "$(dirname "$0")/browser.sh"
WURZEL=$(cd "$(dirname "$0")/.." && pwd)

ZIEL=$(mkdir -p "${1:?Zielordner fehlt}" && cd "$1" && pwd)
PORT=${2:-8392}
QUELLE=${3:-$WURZEL}
cd "$QUELLE"
SEITEN="index.html buero.html leistungen.html vorsorge.html fachkreise.html leichte-sprache.html impressum.html datenschutz.html 404.html"

python3 -m http.server "$PORT" >/dev/null 2>&1 &
SERVER=$!
trap 'kill $SERVER 2>/dev/null || true' EXIT
until curl -sf -o /dev/null "http://127.0.0.1:$PORT/index.html"; do sleep 0.1; done

for seite in $SEITEN; do
  name=${seite%.html}
  for breite in 1280 390; do
    hoehe=$([ "$breite" = 1280 ] && echo 2600 || echo 3400)
    "$BROWSER" --headless --no-sandbox --disable-gpu --hide-scrollbars \
      --force-device-scale-factor=1 --window-size="$breite,$hoehe" \
      --screenshot="$ZIEL/$name-$breite.png" \
      "http://127.0.0.1:$PORT/$seite" 2>/dev/null
  done
done

echo "  $(ls -1 "$ZIEL"/*.png | wc -l) Bilder in $ZIEL"
