#!/bin/sh
# Einmal nach dem Klonen aufrufen. Schaltet die Hooks aus tools/hooks ein.
#
#     tools/einrichten.sh
#
# Git sucht Hooks normalerweise in .git/hooks, und das laesst sich nicht
# versionieren. core.hooksPath zeigt stattdessen auf ein Verzeichnis im
# Repository — damit gilt fuer jeden dieselbe Pruefung.
set -eu
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath tools/hooks
echo "  Hooks eingeschaltet: $(git config core.hooksPath)"
echo "  Ausschalten mit:  git config --unset core.hooksPath"
