"""Rechnet die Farbpaarungen des Stylesheets gegen WCAG AA durch.

AGENTS.md (R-FARBE-5) verlangt WCAG AA für jede Textpaarung, hell und dunkel.
Diese Datei macht daraus eine Prüfung: sie liest die Werte aus style.css,
bildet die Paarungen, die auf der Seite tatsächlich vorkommen, und fällt
unter 4,5:1. Die schwächste Paarung liegt bei 4,61:1 — es ist wenig Luft,
und deshalb fällt eine Verschlechterung sofort auf.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path


from site_support import SITE as ROOT
CSS = (ROOT / "style.css").read_text(encoding="utf-8")

# Fließtext und Beschriftungen — der Schwellenwert für normalen Text.
AA_TEXT = 4.5

# Jede Paarung, die auf der Seite als Text auf Fläche vorkommt.
PAARE = [
    ("--ink", "--paper"),
    ("--body", "--paper"),
    ("--muted", "--paper"),
    ("--accent-ink", "--paper"),
    ("--accent", "--paper"),
    ("--gut-ink", "--paper"),
    ("--body", "--surface"),
    ("--muted", "--surface"),
    ("--accent-ink", "--surface"),
    ("--accent", "--surface"),
    ("--gut-ink", "--gut-flaeche"),
    ("--on-carrier", "--carrier"),
    ("--meta-on-carrier", "--carrier"),
    ("--link-ink", "--paper"),
    ("--link-ink", "--surface"),
    ("--link-on-carrier", "--carrier"),
    ("--accent-on-carrier", "--carrier"),
    ("--brand-leaf", "--carrier"),
    ("--leicht-ink", "--paper"),
    ("--st-1", "--surface"),
    ("--st-2", "--surface"),
    ("--st-3", "--surface"),
    ("--st-4", "--surface"),
    ("--st-5", "--surface"),
]


def _block(text: str, start: str) -> str:
    """Gibt den Inhalt des geschweiften Blocks nach `start` zurück."""
    i = text.index(start) + len(start)
    tiefe, j = 1, i
    while tiefe:
        if text[j] == "{":
            tiefe += 1
        elif text[j] == "}":
            tiefe -= 1
        j += 1
    return text[i : j - 1]


def _farben(text: str) -> dict[str, str]:
    return dict(re.findall(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,8})\s*;", text))


def palette(dunkel: bool) -> dict[str, str]:
    werte = _farben(_block(CSS, ":root {"))
    if dunkel:
        werte.update(_farben(_block(CSS[CSS.index("prefers-color-scheme: dark") :], ":root {")))
    return werte


def leuchtdichte(hex_wert: str) -> float:
    h = hex_wert.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    kanal = [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in kanal]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def kontrast(vorn: str, hinten: str) -> float:
    a, b = leuchtdichte(vorn), leuchtdichte(hinten)
    return (max(a, b) + 0.05) / (min(a, b) + 0.05)


class KontrastTests(unittest.TestCase):
    def test_alle_paarungen_erfuellen_wcag_aa(self) -> None:
        for modus, dunkel in (("hell", False), ("dunkel", True)):
            werte = palette(dunkel)
            for vorn, hinten in PAARE:
                with self.subTest(modus=modus, vorn=vorn, hinten=hinten):
                    self.assertIn(vorn, werte, f"{vorn} fehlt im Block PALETTE")
                    self.assertIn(hinten, werte, f"{hinten} fehlt im Block PALETTE")
                    wert = kontrast(werte[vorn], werte[hinten])
                    # Ungerundet: 4,496:1 ist nicht bestanden.
                    self.assertGreaterEqual(
                        wert,
                        AA_TEXT,
                        f"{vorn} auf {hinten} ({modus}) trägt nur {wert:.2f}:1, "
                        f"nötig sind {AA_TEXT}:1",
                    )

    def test_palette_hat_hellen_und_dunklen_satz(self) -> None:
        hell, dunkel = palette(False), palette(True)
        self.assertNotEqual(hell["--paper"], dunkel["--paper"],
                            "Der Dunkelmodus überschreibt --paper nicht mehr")
        self.assertEqual(sorted(hell), sorted(dunkel),
                         "Hell und dunkel kennen nicht dieselben Farbnamen")


if __name__ == "__main__":
    unittest.main()
