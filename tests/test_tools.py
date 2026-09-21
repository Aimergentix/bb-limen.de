"""Fehlerfälle der Hilfswerkzeuge ohne Browser- oder Netzabhängigkeit.

Sie laufen gegen die erfundene Test-Website aus fixture_site.py, nie gegen die
echten Seiten, Bilder oder die echte Domain (R-REDAKTION-3).
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

from fixture_site import write_site
from site_support import REPO


class ToolTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bb-limen-tools-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        shutil.copytree(REPO / "tools", self.work / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        write_site(self.work)

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
        before = {p.name: p.read_bytes() for p in (self.work / "public").iterdir()}
        header = struct.pack(">II", 1, 1) + bytes([8, 2, 0, 0, 0])
        (self.work / "klein.png").write_bytes(
            b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(header)) + b"IHDR" + header
            + struct.pack(">I", zlib.crc32(b"IHDR" + header)))
        browser = self.executable("browser", '''
for arg do
  case "$arg" in --screenshot=*) target=${arg#--screenshot=} ;; esac
done
cp klein.png "$target"
''')
        result = subprocess.run(["sh", str(self.work / "tools/bilder-erzeugen.sh")],
                                env={**os.environ, "BROWSER": str(browser)},
                                text=True, capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FEHLER:", result.stderr)
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.work / "public").iterdir()})

    def test_link_check_parses_html_and_distinguishes_hosts(self) -> None:
        site = self.work / "site"
        site.mkdir()
        # Die eigene Domain steht in der CNAME-Datei der Test-Website: example.org.
        (site / "index.html").write_text('''<a href="https://example.org/">Büro</a>
<a href='https://extern.example.net/?a=1&amp;b=2'>Extern</a>
<a href="https://example.org.example.net/">Andere Domain</a>
<a href="https://incomplete.example.net/">Abgebrochener Abruf</a>''', encoding="utf-8")
        self.executable("curl", '''
for arg do address=$arg; done
case "$address" in
  https://example.org/) exit 99 ;;
  https://incomplete.example.net/) printf 200; exit 18 ;;
  *) printf 200 ;;
esac
''')
        result = subprocess.run(["sh", str(self.work / "tools/verweise-pruefen.sh"), str(site)],
                                env={**os.environ, "PATH": str(self.work) + os.pathsep + os.environ["PATH"]},
                                text=True, capture_output=True)
        self.assertIn("Geprüfte Adressen: 3", result.stderr)
        self.assertIn("https://extern.example.net/?a=1&b=2", result.stderr)
        self.assertIn("https://example.org.example.net/", result.stderr)
        self.assertEqual(result.returncode, 1)
        self.assertIn("https://incomplete.example.net/", result.stdout)


if __name__ == "__main__":
    unittest.main()
