"""Schlägt bei Formulierungen an, die hier schon einmal falsch waren.

Kein Stilwächter — nur eine kurze Liste benannter Fehler, jeder mit seiner
Begründung. Wer eine Zeile ergänzt, schreibt dazu, warum. Wer eine Zeile
streicht, sollte sicher sein, dass der Fehler nicht wiederkommen kann.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


from site_support import SITE as ROOT, SOURCE
DATEIEN = sorted(ROOT.glob("*.html")) + sorted((SOURCE / "partials").glob("*.html"))

# (Muster, Begründung). Die Muster laufen über den Quelltext der Seiten.
VERBOTEN = [
    (
        r"Aufgabenkreise\b",
        "R-RECHT-2: Plural aus der Fassung vor dem 01.01.2023. Seither hat ein Betreuer "
        "einen Aufgabenkreis aus mehreren Aufgabenbereichen (§ 1815 Abs. 1 BGB).",
    ),
    (
        r'href="tel:\s*"',
        "R-RECHT-6: Leerer Telefonverweis. Das war schon einmal der schwerste technische "
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
        "Unverschlüsselter Verweis nach außen. Behörden und Ministerien "
        "liefern durchweg über HTTPS aus.",
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
        # Die Unicode-Blöcke Verschiedene Symbole, Dingbats, Verschiedene Symbole
        # und Pfeile sowie Emoji samt Variantenwähler. Früher standen hier nur
        # vier Beispielzeichen; die Regel gilt aber für die ganzen Blöcke.
        r"[\u2600-\u27BF\u2B00-\u2BFF\uFE0F\U0001F000-\U0001FAFF]",
        "R-VERBOT-3: Schmuckzeichen, das die Serifenschriften des Projekts nicht "
        "verlässlich enthalten. Der Browser fällt auf eine Symbol- oder "
        "Farb-Emoji-Schrift zurück, und auf jedem Gerät steht etwas anderes. "
        "Ornamente gehören als SVG ins Markup (.zierblatt).",
    ),
    (
        r"(?i)\b(kompetent\w*|individuell\w*|Ihr Partner|professionell\w*|"
        r"zuverlässig\w*|engagiert\w*|vertrauensvoll\w*|maßgeschneidert\w*|"
        r"ganzheitlich\w*|aus einer Hand|jahrelange Erfahrung|Experten?|"
        r"Spezialist\w*)\b",
        "R-SPRACHE-3: Vertrauensfloskel. Die Seite belegt, statt zu beteuern; "
        "der Web-Audit vom 20.09.2026 fand keine einzige, und das soll so bleiben.",
    ),
    (
        r"(?i)>\s*(hier|mehr|weiterlesen|mehr erfahren|klicken Sie hier)\s*</a>",
        "R-SPRACHE-4: Verweistext ohne Ziel. Screenreader lesen Verweise auch "
        "als Liste vor; dort sagt 'hier' nichts. Der Verweis nennt sein Ziel.",
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
        """Gegenprobe: die richtige Form muss vorkommen, sonst prüft die
        Verbotsliste oben etwas, das es gar nicht mehr gibt."""
        gesamt = " ".join(p.read_text(encoding="utf-8") for p in DATEIEN)
        self.assertIn("Aufgabenbereich", gesamt)


if __name__ == "__main__":
    unittest.main()
