"""Haelt die Angaben zusammen, die an mehreren Stellen stehen.

AGENTS.md §6 nennt sie die klassische Bruchstelle: ein Suchen-und-Ersetzen
erwischt die Haelfte, und danach steht in der Kolumne eine andere Nummer
als im Impressum. Diese Datei zaehlt nach, statt zu schaetzen.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SEITEN = sorted(ROOT.glob("*.html"))
BAUSTEINE = sorted((ROOT / "partials").glob("*.html"))
ALLE = SEITEN + BAUSTEINE

TELEFON_TECHNISCH = "+4917642904270"

# Fremde Nummern, die bewusst auf der Seite stehen. Wer eine hinzufuegt,
# traegt sie hier ein — sonst faellt sie auf, und das ist der Sinn.
FREMDE_NUMMERN = {
    "+497751864950": "Betreuungsbehörde Landkreis Waldshut",
}
TELEFON_SICHTBAR = "+49 176 42904270"
EMAIL = "info@bb-limen.de"
STRASSE = "Am Dreispitz 6/6-1"
PLZ_ORT = ("79589", "Binzen")
KREISE = ["Landkreis Lörrach", "Landkreis Waldshut"]
GEMEINDEN = 67  # Lörrach 35 + Waldshut 32


def organisation() -> dict:
    """Der Organization-Knoten aus dem JSON-LD der Startseite."""
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    roh = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    daten = json.loads(roh.group(1))
    knoten = daten["@graph"] if "@graph" in daten else [daten]
    return next(k for k in knoten if k["@type"] == "Organization")


class AngabenTests(unittest.TestCase):
    def test_buero_hat_genau_eine_eigene_telefonnummer(self) -> None:
        eigene_nummern = set()
        for pfad in ALLE:
            text = pfad.read_text(encoding="utf-8")
            eigene_nummern.update(
                nummer
                for nummer in re.findall(r'href="tel:([^"]*)"', text)
                if nummer not in FREMDE_NUMMERN
            )

            with self.subTest(datei=pfad.name):
                self.assertNotRegex(text, r"\[Telefonnummer [^\]]+\]")

        self.assertEqual(eigene_nummern, {TELEFON_TECHNISCH})

    def test_jeder_telefonverweis_ist_bekannt(self) -> None:
        erlaubt = {TELEFON_TECHNISCH, *FREMDE_NUMMERN}
        for pfad in ALLE:
            for treffer in re.findall(r'href="tel:([^"]*)"', pfad.read_text(encoding="utf-8")):
                with self.subTest(datei=pfad.name, nummer=treffer):
                    self.assertIn(
                        treffer,
                        erlaubt,
                        "Unbekannte Telefonnummer. Wenn sie richtig ist, in "
                        "FREMDE_NUMMERN eintragen und dazuschreiben, wem sie gehoert.",
                    )
                    self.assertEqual(treffer, treffer.replace(" ", ""),
                                     "tel: braucht die Nummer ohne Leerzeichen")

    def test_sichtbare_nummer_ist_ueberall_gleich_geschrieben(self) -> None:
        """Findet Schreibweisen wie 0176/42904270 neben der kanonischen.

        Geprueft wird nur der sichtbare Text: Attributwerte und das JSON-LD
        fuehren die Nummer bewusst in der technischen Form ohne Leerzeichen.
        """
        muster = re.compile(r"(?<!\d)(?:\+49|0)[\s/()\-]*1\d{2}[\s/()\-]*\d[\d\s/()\-]{5,}")
        for pfad in ALLE:
            text = pfad.read_text(encoding="utf-8")
            text = re.sub(r"<script.*?</script>", " ", text, flags=re.S)
            text = re.sub(r'="[^"]*"', "", text)
            for treffer in muster.findall(text):
                with self.subTest(datei=pfad.name, gefunden=treffer.strip()):
                    self.assertEqual(treffer.strip(), TELEFON_SICHTBAR)

    def test_jede_mailadresse_ist_dieselbe(self) -> None:
        for pfad in ALLE:
            text = pfad.read_text(encoding="utf-8")
            for treffer in re.findall(r'href="mailto:([^"]*)"', text):
                with self.subTest(datei=pfad.name):
                    self.assertEqual(treffer, EMAIL)
            for treffer in re.findall(r"[\w.+-]+@bb-limen\.de", text):
                with self.subTest(datei=pfad.name, gefunden=treffer):
                    self.assertEqual(treffer, EMAIL)

    def test_anschrift_stimmt_mit_dem_json_ld_ueberein(self) -> None:
        anschrift = organisation()["address"]
        self.assertEqual(anschrift["streetAddress"], STRASSE)
        self.assertEqual(anschrift["postalCode"], PLZ_ORT[0])
        self.assertEqual(anschrift["addressLocality"], PLZ_ORT[1])

        for name in ("partials/rail.html", "impressum.html"):
            text = (ROOT / name).read_text(encoding="utf-8")
            with self.subTest(datei=name):
                self.assertIn(STRASSE, text)
                self.assertIn(PLZ_ORT[0], text)
                self.assertIn(PLZ_ORT[1], text)

    def test_telefon_und_mail_stehen_auch_im_json_ld(self) -> None:
        org = organisation()
        self.assertEqual(org["telephone"], TELEFON_TECHNISCH)
        self.assertEqual(org["email"], EMAIL)

    def test_visitenkarte_stimmt_mit_dem_buero_ueberein(self) -> None:
        org = organisation()
        zeilen = (ROOT / "bb-limen.vcf").read_text(encoding="utf-8").splitlines()
        werte = {}
        for zeile in zeilen:
            name, wert = zeile.split(":", 1)
            werte.setdefault(name.split(";", 1)[0], []).append(wert)

        self.assertEqual(werte["FN"], [org["name"]])
        self.assertEqual(werte["ORG"], [org["name"]])
        self.assertEqual(werte["TEL"], [org["telephone"]])
        self.assertEqual(werte["EMAIL"], [org["email"]])
        self.assertEqual(werte["URL"], [org["url"]])
        anschrift = org["address"]
        self.assertEqual(werte["ADR"], [";".join([
            "", "", anschrift["streetAddress"], anschrift["addressLocality"],
            anschrift["addressRegion"], anschrift["postalCode"],
            anschrift["addressCountry"],
        ])])

    def test_visitenkarte_behaelt_das_austauschformat(self) -> None:
        roh = (ROOT / "bb-limen.vcf").read_bytes()
        self.assertNotIn(b"\n", roh.replace(b"\r\n", b""))
        self.assertTrue(roh.startswith(b"BEGIN:VCARD\r\nVERSION:3.0\r\n"))
        self.assertTrue(roh.endswith(b"END:VCARD\r\n"))
        self.assertIn(b"\r\nN:;;;;\r\n", roh)
        for zeile in roh.split(b"\r\n"):
            self.assertLessEqual(len(zeile), 75)

    def test_einzugsgebiet_ist_vollstaendig_und_widerspruchsfrei(self) -> None:
        gebiet = organisation()["areaServed"]
        kreise = [a["name"] for a in gebiet if a["@type"] == "AdministrativeArea"]
        orte = [a["name"] for a in gebiet if a["@type"] == "City"]

        self.assertEqual(sorted(kreise), sorted(KREISE))
        self.assertEqual(len(orte), GEMEINDEN)
        self.assertEqual(len(set(orte)), len(orte), "Gemeinde doppelt im JSON-LD")

        # Dieselben zwei Landkreise muessen auch sichtbar auf der Seite stehen.
        rail = (ROOT / "partials" / "rail.html").read_text(encoding="utf-8")
        for kreis in KREISE:
            with self.subTest(kreis=kreis):
                self.assertIn(kreis, rail)


if __name__ == "__main__":
    unittest.main()
