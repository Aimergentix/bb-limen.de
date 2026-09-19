#!/bin/sh
# BB Limen — setzt die gemeinsamen Bausteine aus partials/ in die Seiten ein.
#
# Die Seiten im Wurzelverzeichnis bleiben vollstaendiges, direkt im Browser
# lesbares HTML. Dieses Skript ueberschreibt nur die Bereiche zwischen den
# Marken <!-- #name --> und <!-- /#name -->. Wer Telefonnummer, Navigation
# oder Anschrift aendert, aendert sie in partials/ und ruft hier auf:
#
#     ./build.sh
#
# Keine Abhaengigkeiten ausser sh und awk.

set -eu
cd "$(dirname "$0")"

SEITEN="index.html buero.html leistungen.html vorsorge.html fachkreise.html leichte-sprache.html impressum.html datenschutz.html"
BAUSTEINE="head skip rail foot callbar"

einsetzen() {
  # $1 Seite, $2 Name des Bausteins
  awk -v part="partials/$2.html" -v tag="$2" '
    index($0, "<!-- #" tag " -->")  { print; while ((getline z < part) > 0) print z; close(part); weg=1; next }
    index($0, "<!-- /#" tag " -->") { weg=0 }
    !weg { print }
  ' "$1" > "$1.neu"
  mv "$1.neu" "$1"
}

for seite in $SEITEN; do
  for baustein in $BAUSTEINE; do
    einsetzen "$seite" "$baustein"
  done

  # aria-current auf den eigenen Navigationspunkt setzen, alle anderen leeren
  hier="${seite%.html}"
  sed -e "s/%%CUR-$hier%%/ aria-current=\"page\"/" -e "s/%%CUR-[a-z-]*%%//g" \
      "$seite" > "$seite.neu"
  mv "$seite.neu" "$seite"

  echo "  $seite"
done

# Kontrolle: kein Platzhalter darf uebrig bleiben
if grep -l '%%CUR-' $SEITEN 2>/dev/null; then
  echo "FEHLER: Navigationsplatzhalter nicht ersetzt." >&2
  exit 1
fi
echo "Fertig."
