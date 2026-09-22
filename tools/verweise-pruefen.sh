#!/bin/sh
# Ruft jeden Verweis nach außen ab und meldet, was nicht erreichbar ist.
#
#     tools/verweise-pruefen.sh                prüft dist/
#     tools/verweise-pruefen.sh VERZEICHNIS    prüft eine andere Ausgabe
#
# Auf stderr steht der Status jeder Adresse, auf stdout eine Markdown-Liste
# der toten Verweise. Rückgabe: 0 alles erreichbar, 1 tote Verweise, 2 Fehler.
#
# Was es NICHT prüft: ob der genannte Stand eines Dokuments noch stimmt. Ein
# Ministerium kann dieselbe Adresse behalten und den Inhalt austauschen. Das
# bleibt Handarbeit; siehe docs/pflege.md.
set -eu
WURZEL=$(dirname "$0")/..
SITE=${1:-"$WURZEL/dist"}
ls "$SITE"/*.html >/dev/null 2>&1 || {
  echo "FEHLER: keine Seiten in $SITE; zuerst tools/build.sh ausführen." >&2
  exit 2
}
EIGENE_DOMAIN=$(tr -d '[:space:]' < "$WURZEL/public/CNAME")

LISTE=$(mktemp)
trap 'rm -f "$LISTE"' EXIT HUP INT TERM
# Ein HTML-Parser statt eines Zeilenmusters: Er liest beide Arten von
# Anführungszeichen, löst &amp; auf und vergleicht den Rechnernamen genau —
# bb-limen.de.example.org ist eine fremde Adresse.
python3 - "$EIGENE_DOMAIN" "$SITE"/*.html > "$LISTE" <<'PY' || { echo "FEHLER: Verweise nicht lesbar." >&2; exit 2; }
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

own = {sys.argv[1], "www." + sys.argv[1]}
found = set()


class Links(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ("href", "src") and value:
                url = urlsplit(value.strip())
                if url.scheme in ("http", "https") and url.hostname not in own:
                    found.add(value.strip())


for name in sys.argv[2:]:
    parser = Links(convert_charrefs=True)
    parser.feed(Path(name).read_text(encoding="utf-8"))
    parser.close()
for address in sorted(found):
    print(address)
PY
echo "Geprüfte Adressen: $(wc -l < "$LISTE")" >&2

ERGEBNIS=0
while read -r adresse; do
  # Ein abgebrochener Abruf zählt als Fehler, auch wenn der Server vorher
  # schon 200 gemeldet hat: curl schreibt den Status und scheitert danach.
  ausgang=0
  status=$(curl -sSL --max-time 30 --retry 2 --retry-delay 5 \
    -o /dev/null -w '%{http_code}' \
    -A 'bb-limen.de Linkpruefung (+https://bb-limen.de/)' \
    "$adresse" 2>/dev/null) || ausgang=$?
  [ "$ausgang" -eq 0 ] || status="${status:-000}, Abruf abgebrochen (curl $ausgang)"
  printf '  %s  %s\n' "$status" "$adresse" >&2
  case "$status" in
    2??|3??) ;;
    *)
      # Backticks sind hier absichtliches Markdown, keine Shell-Ausdrücke.
      # shellcheck disable=SC2016
      printf -- '- `%s` → HTTP %s\n' "$adresse" "$status"
      ERGEBNIS=1 ;;
  esac
done < "$LISTE"
exit "$ERGEBNIS"
