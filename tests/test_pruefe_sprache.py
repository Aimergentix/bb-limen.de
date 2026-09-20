from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


from site_support import REPO as ROOT
SPEC = importlib.util.spec_from_file_location("pruefe_sprache", ROOT / "tools" / "pruefe-sprache.py")
assert SPEC and SPEC.loader
SPRACHE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SPRACHE)


class SprachpruefungTests(unittest.TestCase):
    def test_empty_site_directory_is_an_error(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/pruefe-sprache.py"),
                                     "--site-dir", temp], cwd=temp, text=True, capture_output=True)
            self.assertEqual(result.returncode, 2)
            self.assertIn("unvollständiger Seitenbestand", result.stderr)

    def test_unknown_page_is_an_error(self) -> None:
        from site_support import SITE
        result = subprocess.run([sys.executable, "-B", str(ROOT / "tools/pruefe-sprache.py"),
                                 "--site-dir", str(SITE), "unbekannt.html"],
                                cwd="/tmp", text=True, capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unbekannte Seiten", result.stderr)

    def test_name_ending_in_a_does_not_hide_sentence_boundary(self) -> None:
        self.assertEqual(
            SPRACHE.saetze("Ich spreche mit Mika. Danach komme ich."),
            ["Ich spreche mit Mika.", "Danach komme ich."],
        )

    def test_br_is_layout_not_sentence_boundary(self) -> None:
        html = "<main><p>Dieser Satz steht vor dem Umbruch<br>und geht danach weiter.</p></main>"
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "seite.html"
            path.write_text(html, encoding="utf-8")
            self.assertEqual(
                SPRACHE.saetze(SPRACHE.fliesstext(path)),
                ["Dieser Satz steht vor dem Umbruch und geht danach weiter."],
            )

    def test_only_main_prose_is_measured(self) -> None:
        html = """
        <header><p>Dieser Kopftext wird nicht gemessen.</p></header>
        <main>
          <h1>Auch diese Überschrift bleibt getrennt.</h1>
          <p>Dieser Fließtext wird gemessen.</p>
          <dl class="fakten"><dt>Beschriftung</dt><dd>Auch dieser Fachtext wird gemessen.</dd></dl>
          <dl class="contact"><dt>Telefon</dt><dd>Null eins zwei drei.</dd></dl>
        </main>
        """
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "seite.html"
            path.write_text(html, encoding="utf-8")
            self.assertEqual(
                SPRACHE.saetze(SPRACHE.fliesstext(path)),
                ["Dieser Fließtext wird gemessen.", "Auch dieser Fachtext wird gemessen."],
            )


if __name__ == "__main__":
    unittest.main()
