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
# bleibt Handarbeit; siehe docs/redaktion.md.
set -eu
SITE=${1:-"$(dirname "$0")/../dist"}
ls "$SITE"/*.html >/dev/null 2>&1 || {
  echo "FEHLER: keine Seiten in $SITE; zuerst tools/build.sh ausführen." >&2
  exit 2
}

LISTE=$(mktemp)
trap 'rm -f "$LISTE"' EXIT HUP INT TERM
grep -ho 'href="https\?://[^"]*"' -- "$SITE"/*.html \
  | sed 's/href="//; s/"$//; s/&amp;/\&/g' \
  | grep -v '//bb-limen\.de' | sort -u > "$LISTE"
echo "Geprüfte Adressen: $(wc -l < "$LISTE")" >&2

ERGEBNIS=0
while read -r adresse; do
  status=$(curl -sSL --max-time 30 --retry 2 --retry-delay 5 \
    -o /dev/null -w '%{http_code}' \
    -A 'bb-limen.de Linkpruefung (+https://bb-limen.de/)' \
    "$adresse" 2>/dev/null) || status=${status:-000}
  printf '  %s  %s\n' "$status" "$adresse" >&2
  case "$status" in
    2*|3*) ;;
    *)
      # Backticks sind hier absichtliches Markdown, keine Shell-Ausdrücke.
      # shellcheck disable=SC2016
      printf -- '- `%s` → HTTP %s\n' "$adresse" "$status"
      ERGEBNIS=1 ;;
  esac
done < "$LISTE"
exit "$ERGEBNIS"
