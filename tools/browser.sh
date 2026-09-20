# Wird von den Renderwerkzeugen eingebunden, nicht selbst aufgerufen.
#
# Der Browser heisst je nach System anders: unter Debian und Ubuntu
# chromium oder chromium-browser, auf den GitHub-Laeufern google-chrome.
# Ohne diese Suche liefe tools/vorschau.sh auf dem einen System und nicht
# auf dem anderen.
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
