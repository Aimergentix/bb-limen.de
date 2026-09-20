"""Schlaegt bei Formulierungen an, die hier schon einmal falsch waren.

Kein Stilwaechter — nur eine kurze Liste benannter Fehler, jeder mit seiner
Begruendung. Wer eine Zeile ergaenzt, schreibt dazu, warum. Wer eine Zeile
streicht, sollte sicher sein, dass der Fehler nicht wiederkommen kann.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


from site_support import SITE as ROOT, SOURCE
DATEIEN = sorted(ROOT.glob("*.html")) + sorted((SOURCE / "partials").glob("*.html"))

# (Muster, Begruendung). Die Muster laufen ueber den Quelltext der Seiten.
VERBOTEN = [
    (
        r"Aufgabenkreise\b",
        "Plural aus der Fassung vor dem 01.01.2023. Seither hat ein Betreuer "
        "einen Aufgabenkreis aus mehreren Aufgabenbereichen (§ 1815 Abs. 1 BGB).",
    ),
    (
        r'href="tel:\s*"',
        "Leerer Telefonverweis. Das war schon einmal der schwerste technische "
        "Fehler dieser Seite: ein Anruf, der ins Nichts geht.",
    ),
    (
        r'href="mailto:\s*"',
        "Leerer E-Mail-Verweis.",
    ),
    (
        r'href=""',
        "Leerer Verweis.",
    ),
    (
        r'href="http://(?!127\.0\.0\.1|localhost)',
        "Unverschluesselter Verweis nach aussen. Behoerden und Ministerien "
        "liefern durchweg ueber HTTPS aus.",
    ),
    (
        r"\b(TODO|FIXME|XXX|Lorem ipsum)\b",
        "Arbeitsnotiz oder Blindtext im ausgelieferten Bestand.",
    ),
    (
        r"\bEntmuendigung\b",
        "Falsche Schreibung ohne Umlaut.",
    ),
    (
        r"[❦❧✦❖]",
        "Schmuckzeichen, das in keiner Serifenschrift des Projekts vorkommt. "
        "Der Browser faellt auf eine Symbol- oder Farb-Emoji-Schrift zurueck. "
        "Ornamente gehoeren als SVG ins Markup (.zierblatt), siehe AGENTS.md.",
    ),
]


class BegriffsTests(unittest.TestCase):
    def test_keine_bekannten_fehlformulierungen(self) -> None:
        for pfad in DATEIEN:
            text = pfad.read_text(encoding="utf-8")
            for muster, grund in VERBOTEN:
                with self.subTest(datei=pfad.name, muster=muster):
                    treffer = [
                        f"Zeile {nr}: {zeile.strip()[:90]}"
                        for nr, zeile in enumerate(text.splitlines(), 1)
                        if re.search(muster, zeile)
                    ]
                    self.assertEqual(treffer, [], f"{grund}\n  " + "\n  ".join(treffer))

    def test_aufgabenbereich_wird_verwendet(self) -> None:
        """Gegenprobe: die richtige Form muss vorkommen, sonst prueft die
        Verbotsliste oben etwas, das es gar nicht mehr gibt."""
        gesamt = " ".join(p.read_text(encoding="utf-8") for p in DATEIEN)
        self.assertIn("Aufgabenbereich", gesamt)


if __name__ == "__main__":
    unittest.main()
