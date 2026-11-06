#!/bin/sh
# Erzeugt dist/ aus src/ und public/. Von jedem Arbeitsverzeichnis aufrufbar.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname "$0")/.." && pwd)
if [ -z "${PYTHON:-}" ]; then
  PYTHON="$ROOT/.venv-documents/bin/python"
  [ -x "$PYTHON" ] || PYTHON=python3
fi
exec "$PYTHON" -B "$ROOT/tools/build.py" "$@"
