"""Formatgrenzen und Sprachvarianten der zentralen Büroangaben."""
from __future__ import annotations

import json
import unittest

from fixture_site import office
from site_support import REPO
from bureau_data import load_office, office_values, render_office, vcard


class BureauDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.data = office()

    def test_disjoint_days_do_not_become_a_range(self) -> None:
        """R-ANGABEN-1: Keine erfundenen Zwischentage."""
        self.data["sprechzeiten"]["regulaer"] = {
            "tage": ["Dienstag", "Donnerstag", "Samstag"], "von": "10:00", "bis": "18:00",
        }
        self.data["sprechzeiten"]["nach_vereinbarung"] = ["Montag", "Mittwoch", "Freitag"]
        values = office_values(self.data)
        self.assertEqual(values["sprechzeiten.kurz.regulaer"], "Di, Do, Sa 10–18 Uhr")
        self.assertEqual(values["sprechzeiten.leicht.termin"],
                         "Am Montag, am Mittwoch und am Freitag geht es auch.")

    def test_html_json_and_vcard_escape_the_same_address(self) -> None:
        """R-ANGABEN-1, R-ANGABEN-6: Sonderzeichen bleiben Daten."""
        street = 'Äußere "Straße" & Hof; Eingang, \\ </script>' + "ö" * 60
        self.data["anschrift"]["strasse"] = street
        html = render_office('<p title="%%BUREAU:anschrift.strasse%%">Adresse</p>', self.data)
        self.assertIn("&quot;Straße&quot; &amp; Hof; Eingang, \\ &lt;/script&gt;", html)
        script = '<script type="application/ld+json">{"address":"%%BUREAU_JSON:anschrift.strasse%%"}</script>'
        rendered = render_office(script, self.data)
        self.assertEqual(rendered.count("</script>"), 1)
        self.assertEqual(json.loads(rendered.split(">", 1)[1].rsplit("<", 1)[0])["address"], street)
        office = {"@type": "Organization", "name": "Büro, Test; West", "url": "https://example.org/",
                  "telephone": "+4930123456", "email": "kontakt@example.org",
                  "address": {"@type": "PostalAddress", "streetAddress": street,
                              "addressLocality": "Testort", "addressRegion": "Testland",
                              "postalCode": "12345", "addressCountry": "DE"}}
        payload = json.dumps({"@graph": [office]}).replace("<", "\\u003c")
        index = '<script type="application/ld+json">' + payload + '</script>'
        card = vcard(index)
        self.assertNotIn(b"\n", card.replace(b"\r\n", b""))
        for line in card.split(b"\r\n"):
            self.assertLessEqual(len(line), 75)
            line.decode("utf-8")
        unfolded = card.replace(b"\r\n ", b"").decode("utf-8")
        self.assertIn("FN:Büro\\, Test\\; West\r\n", unfolded)
        self.assertIn('Äußere "Straße" & Hof\\; Eingang\\, \\\\ </script>', unfolded)
        self.assertIn("ö" * 60 + ";Testort;Testland;12345;DE\r\n", unfolded)

    def test_contact_literals_are_not_maintained_in_templates(self) -> None:
        """R-ANGABEN-1: Keine erneute Mehrfachpflege.

        Die Werte kommen hier aus der Quelle selbst: Geprüft wird nicht, ob
        sie stimmen, sondern dass sie nur an einer Stelle stehen.
        """
        live = load_office(REPO)
        values = (*live["telefon"].values(), live["email"], live["anschrift"]["strasse"])
        for path in [*(REPO / "src/pages").glob("*.html"), *(REPO / "src/partials").glob("*.html")]:
            text = path.read_text(encoding="utf-8")
            for value in values:
                with self.subTest(path=path.name, value=value):
                    self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
