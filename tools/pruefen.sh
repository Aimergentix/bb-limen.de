#!/bin/sh
# Gemeinsame Prüfung für Menschen, Hook und CI; Quellen, Index und dist/ bleiben unverändert.
# Geprüft wird Technik, nie Wortlaut: Build, Verweise, Struktur (R-REDAKTION-3).
#
#     tools/pruefen.sh
set -eu
[ "$#" -eq 0 ] || { echo "FEHLER: unbekanntes Argument $1" >&2; exit 2; }
cd "$(dirname "$0")/.."
export PYTHONDONTWRITEBYTECODE=1
ARBEITSVERZEICHNIS=$(mktemp -d)
trap 'rm -rf "$ARBEITSVERZEICHNIS"' EXIT HUP INT TERM
BB_LIMEN_TEST_SITE="$ARBEITSVERZEICHNIS/site"
export BB_LIMEN_TEST_SITE
python3 tools/build.py --output "$BB_LIMEN_TEST_SITE"
python3 -m unittest discover -s tests
echo 'Geprüft: Build, Verweise und Struktur.'
