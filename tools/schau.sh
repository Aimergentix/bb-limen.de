#!/bin/sh
# Rendert Seiten mit Chromium und legt PNG unter ~/bb-shots ab.
#   ./schau.sh <seite.html> <breite> <hoehe> <name> [dunkel]
set -eu
SEITE="${1:-index.html}"; B="${2:-1280}"; H="${3:-1400}"; NAME="${4:-schau}"; MODUS="${5:-hell}"
PORT=8391
mkdir -p "$HOME/bb-shots"
DUNKEL=""
[ "$MODUS" = "dunkel" ] && DUNKEL="--force-dark-mode --enable-features=WebContentsForceDark"
# shellcheck disable=SC2086
timeout 90 chromium --headless --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size="$B,$H" $DUNKEL \
  --screenshot="$HOME/bb-shots/$NAME.png" "http://127.0.0.1:$PORT/$SEITE" 2>/dev/null || true
[ -f "$HOME/bb-shots/$NAME.png" ] && echo "  $NAME.png  $(stat -c%s "$HOME/bb-shots/$NAME.png") B" || echo "  $NAME FEHLT"
