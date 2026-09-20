#!/bin/sh
# Zeigt die Sitemap aus src/seiten.json. tools/build.sh schreibt sie in dist/.
# lastmod ist ein geprüfter Inhaltsstand, kein Build- oder Verschiebedatum.
set -eu
exec python3 -B "$(dirname "$0")/build.py" --sitemap "$@"
