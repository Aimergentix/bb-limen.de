#!/bin/sh
# Schreibt sitemap.xml neu. Das Datum je Seite stammt aus der Git-Historie,
# damit es nicht von Hand gepflegt werden muss und nicht still veraltet.
#
#     tools/sitemap.sh
#
# Aufgenommen wird nur, was auch indexiert werden soll. Nicht aufgenommen:
# impressum.html und datenschutz.html (beide stehen bewusst auf noindex,
# § 5 DDG verlangt Erreichbarkeit, nicht Auffindbarkeit) sowie 404.html.
set -eu
cd "$(dirname "$0")/.."

SEITEN="index.html buero.html leistungen.html vorsorge.html fachkreise.html leichte-sprache.html"

{
  echo '<?xml version="1.0" encoding="UTF-8"?>'
  echo '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
  for seite in $SEITEN; do
    stand=$(git log -1 --format=%cs -- "$seite" 2>/dev/null || true)
    [ -n "$stand" ] || stand=$(date +%F)

    if [ "$seite" = "index.html" ]; then
      adresse="https://bb-limen.de/"
    else
      adresse="https://bb-limen.de/$seite"
    fi

    printf '  <url>\n    <loc>%s</loc>\n    <lastmod>%s</lastmod>\n  </url>\n' \
      "$adresse" "$stand"
  done
  echo '</urlset>'
} > sitemap.xml

echo "  sitemap.xml  $(grep -c '<loc>' sitemap.xml) Adressen"
