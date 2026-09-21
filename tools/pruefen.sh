#!/bin/sh
# Gemeinsame Prüfung für Menschen, Hook und CI; Quellen, Index und dist/ bleiben unverändert.
#
#     tools/pruefen.sh                      beim Arbeiten: Platzhalter sind ein Hinweis
#     tools/pruefen.sh --veroeffentlichung  vor der Auslieferung: Platzhalter sind ein Fehler
set -eu
STRENG=nein
case "${1:-}" in
  "") ;;
  --veroeffentlichung) STRENG=ja ;;
  *) echo "FEHLER: unbekanntes Argument $1" >&2; exit 2 ;;
esac
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
ARBEITSVERZEICHNIS=$(mktemp -d)
trap 'rm -rf "$ARBEITSVERZEICHNIS"' EXIT HUP INT TERM
BB_LIMEN_TEST_SITE="$ARBEITSVERZEICHNIS/site"
export BB_LIMEN_TEST_SITE
python3 tools/build.py --output "$BB_LIMEN_TEST_SITE"
python3 -m unittest discover -s tests -v
python3 tools/pruefe_sprache.py --site-dir "$BB_LIMEN_TEST_SITE"
if grep -rn '\[[A-ZÄÖÜ]' -- "$BB_LIMEN_TEST_SITE"/*.html; then
  if [ "$STRENG" = ja ]; then
    echo 'FEHLER: offene Platzhalter dürfen nicht veröffentlicht werden.' >&2
    exit 1
  fi
  echo 'Hinweis: offene Platzhalter vor der Veröffentlichung klären.'
fi
echo 'Geprüft: Build, Ausgabebestand, Regressionen und Satzlängen.'
