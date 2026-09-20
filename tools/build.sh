#!/bin/sh
# BB Limen — setzt die gemeinsamen Bausteine aus partials/ in die Seiten ein.
#
# Das Skript liegt in tools/, arbeitet aber im Wurzelverzeichnis: es wechselt
# selbst dorthin und laesst sich deshalb von ueberall aufrufen.
#
# Die Seiten im Wurzelverzeichnis bleiben vollstaendiges, direkt im Browser
# lesbares HTML. Dieses Skript ueberschreibt nur die Bereiche zwischen den
# Marken <!-- #name --> und <!-- /#name -->. Wer Telefonnummer, Navigation
# oder Anschrift aendert, aendert sie in partials/ und ruft hier auf:
#
#     tools/build.sh
#
# Benoetigt uebliche Unix-Werkzeuge: sh, awk, sed, grep, cmp, mktemp,
# cp, mv und rm.

set -eu
cd "$(dirname "$0")/.."

SEITEN="index.html betreuung.html aufgaben.html vorsorge.html fachkreise.html leichte-sprache.html impressum.html datenschutz.html 404.html"
BAUSTEINE="head skip rail foot callbar"

ARBEITSVERZEICHNIS=$(mktemp -d "./.build.XXXXXX")
aufraeumen() {
  rm -rf "$ARBEITSVERZEICHNIS"
}
trap aufraeumen EXIT HUP INT TERM

fehler() {
  echo "FEHLER: $*" >&2
  exit 1
}

validiere_seite() {
  awk -v bausteine="$BAUSTEINE" -v datei="$1" '
    BEGIN {
      anzahl = split(bausteine, reihenfolge, " ")
      for (i = 1; i <= anzahl; i++) erwartet[reihenfolge[i]] = i
      naechster = 1
    }

    function abbrechen(text) {
      print "FEHLER: " datei ":" NR ": " text > "/dev/stderr"
      kaputt = 1
      exit 1
    }

    {
      zeile = $0

      if (zeile ~ /^[[:space:]]*<!--[[:space:]]*#[a-z-]+[[:space:]]*-->[[:space:]]*$/) {
        tag = zeile
        sub(/^[[:space:]]*<!--[[:space:]]*#/, "", tag)
        sub(/[[:space:]]*-->[[:space:]]*$/, "", tag)

        if (!(tag in erwartet)) abbrechen("unbekannte Anfangsmarke #" tag)
        if (offen != "") abbrechen("verschachtelte Anfangsmarke #" tag " in #" offen)
        if (start[tag]++) abbrechen("zweite Anfangsmarke #" tag)
        if (erwartet[tag] != naechster) abbrechen("Baustein #" tag " steht nicht in der erwarteten Reihenfolge")
        offen = tag
        next
      }

      if (zeile ~ /^[[:space:]]*<!--[[:space:]]*\/#([a-z-]+)[[:space:]]*-->[[:space:]]*$/) {
        tag = zeile
        sub(/^[[:space:]]*<!--[[:space:]]*\/#/, "", tag)
        sub(/[[:space:]]*-->[[:space:]]*$/, "", tag)

        if (!(tag in erwartet)) abbrechen("unbekannte Schlussmarke /#" tag)
        if (offen == "") abbrechen("Schlussmarke /#" tag " ohne Anfangsmarke")
        if (offen != tag) abbrechen("Schlussmarke /#" tag " schliesst den offenen Baustein #" offen " nicht")
        if (ende[tag]++) abbrechen("zweite Schlussmarke /#" tag)
        offen = ""
        naechster++
        next
      }

      if (index(zeile, "<!-- #") || index(zeile, "<!-- /#")) {
        abbrechen("Bausteinmarken muessen jeweils allein in einer Zeile stehen")
      }
    }

    END {
      if (kaputt) exit 1
      if (offen != "") {
        print "FEHLER: " datei ": Schlussmarke /#" offen " fehlt" > "/dev/stderr"
        exit 1
      }
      for (i = 1; i <= anzahl; i++) {
        tag = reihenfolge[i]
        if (start[tag] != 1 || ende[tag] != 1) {
          print "FEHLER: " datei ": fuer #" tag " wird genau ein vollstaendiges Markenpaar erwartet" > "/dev/stderr"
          exit 1
        }
      }
    }
  ' "$1"
}

einsetzen() {
  seite=$1
  baustein=$2
  quelle=$3
  ziel=$4

  awk -v part="partials/$baustein.html" -v tag="$baustein" '
    BEGIN {
      anfang = "^[[:space:]]*<!--[[:space:]]*#" tag "[[:space:]]*-->[[:space:]]*$"
      ende = "^[[:space:]]*<!--[[:space:]]*/#" tag "[[:space:]]*-->[[:space:]]*$"
    }

    $0 ~ anfang {
      print
      status = 0
      while ((status = (getline zeile < part)) > 0) print zeile
      if (status < 0) {
        print "FEHLER: " part " konnte nicht vollstaendig gelesen werden" > "/dev/stderr"
        exit 1
      }
      close(part)
      auslassen = 1
      next
    }

    $0 ~ ende {
      auslassen = 0
      print
      next
    }

    !auslassen { print }
  ' "$quelle" > "$ziel" || fehler "Baustein $baustein konnte in $seite nicht eingesetzt werden."
}

# Vor dem ersten moeglichen Ersetzen werden alle Eingaben geprueft.
for baustein in $BAUSTEINE; do
  [ -f "partials/$baustein.html" ] || fehler "partials/$baustein.html fehlt."
  [ -r "partials/$baustein.html" ] || fehler "partials/$baustein.html ist nicht lesbar."
done

for seite in $SEITEN; do
  [ -f "$seite" ] || fehler "$seite fehlt."
  [ -r "$seite" ] || fehler "$seite ist nicht lesbar."
  validiere_seite "$seite"
done

# Alle Ergebnisse entstehen zuerst im Arbeitsverzeichnis. Ein Fehler an einer
# spaeteren Seite laesst die Originaldateien dadurch unveraendert.
for seite in $SEITEN; do
  cp "$seite" "$ARBEITSVERZEICHNIS/$seite"

  for baustein in $BAUSTEINE; do
    einsetzen "$seite" "$baustein" "$ARBEITSVERZEICHNIS/$seite" "$ARBEITSVERZEICHNIS/$seite.neu"
    mv "$ARBEITSVERZEICHNIS/$seite.neu" "$ARBEITSVERZEICHNIS/$seite"
  done

  hier=${seite%.html}
  sed -e "s/%%CUR-$hier%%/ aria-current=\"page\"/" -e "s/%%CUR-[a-z-]*%%//g" \
      "$ARBEITSVERZEICHNIS/$seite" > "$ARBEITSVERZEICHNIS/$seite.neu"
  mv "$ARBEITSVERZEICHNIS/$seite.neu" "$ARBEITSVERZEICHNIS/$seite"
done

if grep -l '%%CUR-' "$ARBEITSVERZEICHNIS"/*.html >/dev/null 2>&1; then
  fehler "Navigationsplatzhalter wurden nicht vollstaendig ersetzt."
fi

for seite in $SEITEN; do
  if ! cmp -s "$ARBEITSVERZEICHNIS/$seite" "$seite"; then
    mv "$ARBEITSVERZEICHNIS/$seite" "$seite"
  fi
  echo "  $seite"
done

echo "Fertig."
