"""Gemeinsame Grundlage der Tests: eine frisch erzeugte Website und die
erwarteten Büroangaben.

Die Website wird immer neu erzeugt, auch ohne vorhandenes dist/.

Die Büroangaben stehen hier bewusst ein zweites Mal, unabhängig von den
Quellen unter src/: Ein Test, der seinen Erwartungswert aus der geprüften
Datei liest, bestätigt jeden Fehler. Wer eine Angabe ändert, ändert sie in
den Quellen und genau einmal hier.
"""
from __future__ import annotations

import atexit
import os
from pathlib import Path
import sys
import tempfile

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "tools"))
from build import check_output, render, write_output

SOURCE = REPO / "src"
if os.environ.get("BB_LIMEN_TEST_SITE"):
    SITE = Path(os.environ["BB_LIMEN_TEST_SITE"])
else:
    TEMP = tempfile.TemporaryDirectory(prefix="bb-limen-tests-")
    atexit.register(TEMP.cleanup)
    SITE = Path(TEMP.name) / "site"
    write_output(render(), SITE)
check_output(render(), SITE)

# Erwartete Büroangaben (AGENTS.md, R-ANGABEN).
TELEFON_TECHNISCH = "+4917642904270"
TELEFON_SICHTBAR = "+49 176 42904270"
EMAIL = "info@bb-limen.de"
STRASSE = "Am Dreispitz 6/6-1"
PLZ_ORT = ("79589", "Binzen")
KREISE = ["Landkreis Lörrach", "Landkreis Waldshut"]
GEMEINDEN = 67  # Lörrach 35 + Waldshut 32
