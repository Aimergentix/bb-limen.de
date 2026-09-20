#!/bin/sh
# Gemeinsame Prüfung für Menschen, Hook und CI; Quellen, Index und dist/ bleiben unverändert.
set -eu
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
ARBEITSVERZEICHNIS=$(mktemp -d)
trap 'rm -rf "$ARBEITSVERZEICHNIS"' EXIT HUP INT TERM
BB_LIMEN_TEST_SITE="$ARBEITSVERZEICHNIS/site"
export BB_LIMEN_TEST_SITE
python3 tools/build.py --output "$BB_LIMEN_TEST_SITE"
python3 -m unittest discover -s tests -v
python3 tools/pruefe-sprache.py --site-dir "$BB_LIMEN_TEST_SITE"
if grep -rn '\[[A-ZÄÖÜ]' -- "$BB_LIMEN_TEST_SITE"/*.html; then
  echo 'Hinweis: offene Platzhalter vor der Veröffentlichung klären.'
fi
echo 'Geprüft: Build, Ausgabebestand, Regressionen und Satzlängen.'
