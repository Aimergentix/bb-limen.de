"""Prüft immer eine frisch erzeugte Website, auch ohne vorhandenes dist/."""
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
