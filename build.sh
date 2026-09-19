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
  #
  # Jeder Fehlerfall loescht sonst still Inhalt: fehlt die Bausteindatei,
  # bliebe der Bereich leer; fehlt die Schlussmarke, waere der Rest der
  # Seite weg. Deshalb wird jeder Fall geprueft und die Seite erst
  # ersetzt, wenn awk ohne Fehler durchgelaufen ist.
  if [ ! -f "partials/$2.html" ]; then
    echo "FEHLER: partials/$2.html fehlt." >&2
    return 1
  fi
  awk -v part="partials/$2.html" -v tag="$2" '
    index($0, "<!-- #" tag " -->")  {
      print
      if (auf) { print "FEHLER: zweite Anfangsmarke #" tag > "/dev/stderr"; exit 1 }
      auf = 1
      while ((getline z < part) > 0) print z
      close(part)
      weg = 1
      next
    }
    index($0, "<!-- /#" tag " -->") { if (!weg) { print "FEHLER: Schlussmarke /#" tag " ohne Anfang" > "/dev/stderr"; exit 1 } weg = 0; zu = 1 }
    !weg { print }
    END {
      if (!auf) { print "FEHLER: Anfangsmarke #" tag " fehlt" > "/dev/stderr"; exit 1 }
      if (!zu)  { print "FEHLER: Schlussmarke /#" tag " fehlt" > "/dev/stderr"; exit 1 }
    }
  ' "$1" > "$1.neu" || { echo "  in $1" >&2; rm -f "$1.neu"; return 1; }
  mv "$1.neu" "$1"
}

for seite in $SEITEN; do
  for baustein in $BAUSTEINE; do
    einsetzen "$seite" "$baustein"
  done

  # aria-current auf den eigenen Navigationspunkt setzen, alle anderen leeren
  hier="${seite%.html}"
  sed -e "s/%%CUR-$hier%%/ aria-current=\"page\"/" -e "s/%%CUR-[a-z-]*%%//g" \
      "$seite" > "$seite.neu" || { rm -f "$seite.neu"; exit 1; }
  mv "$seite.neu" "$seite"

  echo "  $seite"
done

# Kontrolle: kein Platzhalter darf uebrig bleiben
if grep -l '%%CUR-' $SEITEN 2>/dev/null; then
  echo "FEHLER: Navigationsplatzhalter nicht ersetzt." >&2
  exit 1
fi
echo "Fertig."
