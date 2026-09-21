"""Fehlerfälle der Hilfswerkzeuge ohne Browser- oder Netzabhängigkeit."""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from site_support import REPO


class ToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bb-limen-tools-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        for directory in ("tools", "src", "public"):
            shutil.copytree(REPO / directory, self.work / directory,
                            ignore=shutil.ignore_patterns("__pycache__"))

    def executable(self, name: str, code: str) -> Path:
        path = self.work / name
        path.write_text("#!/bin/sh\nset -eu\n" + code, encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_failed_image_export_preserves_all_existing_assets(self) -> None:
        """R-QUELLE-1: Ein abgebrochener Export darf keinen halben Satz hinterlassen."""
        before = {p.name: p.read_bytes() for p in (self.work / "public").iterdir()}
        browser = self.executable("browser", '''
for arg do
  case "$arg" in --screenshot=*) target=${arg#--screenshot=} ;; esac
done
case "$target" in
  *vorschau.png) printf changed >> "$target" ;;
  *apple-touch-icon.png) exit 1 ;;
esac
''')
        result = subprocess.run(["sh", str(self.work / "tools/bilder-erzeugen.sh")],
                                env={**os.environ, "BROWSER": str(browser)},
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.work / "public").iterdir()})

    def test_image_export_rejects_wrong_dimensions(self) -> None:
        browser = self.executable("browser", '''
for arg do
  case "$arg" in --screenshot=*) target=${arg#--screenshot=} ;; esac
done
cp public/apple-touch-icon.png "$target"
''')
        result = subprocess.run(["sh", str(self.work / "tools/bilder-erzeugen.sh")],
                                env={**os.environ, "BROWSER": str(browser)},
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FEHLER:", result.stderr)

    def test_link_check_parses_html_and_distinguishes_hosts(self) -> None:
        site = self.work / "site"
        site.mkdir()
        (site / "index.html").write_text('''<a href="https://bb-limen.de/">Büro</a>
<a href='https://example.org/?a=1&amp;b=2'>Extern</a>
<a href="https://bb-limen.de.example.org/">Andere Domain</a>
<a href="https://incomplete.example.org/">Abgebrochener Abruf</a>''', encoding="utf-8")
        self.executable("curl", '''
for arg do address=$arg; done
case "$address" in
  https://bb-limen.de/) exit 99 ;;
  https://incomplete.example.org/) printf 200; exit 18 ;;
  *) printf 200 ;;
esac
''')
        result = subprocess.run(["sh", str(self.work / "tools/verweise-pruefen.sh"), str(site)],
                                env={**os.environ, "PATH": str(self.work) + os.pathsep + os.environ["PATH"]},
                                text=True, capture_output=True)
        self.assertIn("Geprüfte Adressen: 3", result.stderr)
        self.assertIn("https://example.org/?a=1&b=2", result.stderr)
        self.assertIn("https://bb-limen.de.example.org/", result.stderr)
        self.assertEqual(result.returncode, 1)
        self.assertIn("https://incomplete.example.org/", result.stdout)


if __name__ == "__main__":
    unittest.main()
