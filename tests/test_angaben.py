"""Hält die Angaben zusammen, die an mehreren Stellen stehen.

R-ANGABEN verlangt übereinstimmende Werte an jeder vorgesehenen Stelle.
Unabhängige Erwartungen prüfen die erzeugten Inhalte einschließlich JSON-LD
und Bürovisitenkarte. Die Bausteine werden für Seitentests ausgeblendet.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


from site_support import (
    EMAIL, GEMEINDEN, KREISE, PLZ_ORT, SITE as ROOT, SOURCE, STRASSE,
    TELEFON_SICHTBAR, TELEFON_TECHNISCH,
)
SEITEN = sorted(ROOT.glob("*.html"))
BAUSTEINE = sorted((SOURCE / "partials").glob("*.html"))
ALLE = SEITEN

# Fremde Nummern, die bewusst auf der Seite stehen. Wer eine hinzufügt,
# trägt sie hier ein — sonst fällt sie auf, und das ist der Sinn.
FREMDE_NUMMERN = {
    "+497751864950": "Betreuungsbehörde Landkreis Waldshut",
}

# Wo jede Angabe laut AGENTS.md (R-ANGABEN) stehen MUSS. Geprüft wird die
# erzeugte Seite ohne Bausteine: Die Kolumne mit Nummer und Anschrift
# würde sonst jede Lücke im eigentlichen Seiteninhalt verdecken.
STELLEN_TELEFON = [
    "partials/rail.html", "partials/callbar.html", "pages/index.html",
    "pages/fachkreise.html", "pages/leichte-sprache.html",
    "pages/impressum.html", "pages/datenschutz.html", "pages/404.html",
]
STELLEN_ANSCHRIFT = [
    "partials/rail.html", "pages/index.html", "pages/fachkreise.html",
    "pages/leichte-sprache.html", "pages/impressum.html",
    "pages/datenschutz.html",
]
STELLEN_GEMEINDEZAHL = [
    "pages/index.html", "pages/betreuung.html", "pages/fachkreise.html",
]
# Die Sprechzeiten stehen je Sprachebene in anderem Wortlaut. Festgehalten
# ist deshalb der Wortlaut je Stelle, nicht ein gemeinsamer.
SPRECHZEITEN = {
    "partials/rail.html": [
        "Di, Do 10–12 Uhr", "So, Mo, Mi nach Vereinbarung"],
    "pages/index.html": [
        "Dienstag und Donnerstag von 10 bis 12 Uhr.",
        "Sonntag, Montag und Mittwoch nach Vereinbarung."],
    "pages/fachkreise.html": [
        "Dienstag und Donnerstag von 10 bis 12 Uhr.",
        "Sonntag, Montag und Mittwoch nach Vereinbarung."],
    "pages/leichte-sprache.html": [
        "Am Dienstag und Donnerstag.", "Von 10 Uhr bis 12 Uhr.",
        "Am Sonntag, am Montag und am Mittwoch geht es auch.", "Aber nur mit einem Termin."],
}


def quelle(stelle: str) -> str:
    kind, name = stelle.split("/")
    text = (ROOT / ("index.html" if kind == "partials" else name)).read_text(encoding="utf-8")
    if kind == "partials":
        block = name.removesuffix(".html")
        return re.search(rf"<!-- #{block} -->(.*?)<!-- /#{block} -->", text, re.S)[1]
    return re.sub(r"<!-- #([a-z-]+) -->.*?<!-- /#\1 -->", "", text, flags=re.S)


def organisation() -> dict:
    """Der Organization-Knoten aus dem JSON-LD der Startseite."""
    s = (ROOT / "index.html").read_text(encoding="utf-8")
    roh = re.search(r'<script type="application/ld\+json">(.*?)</script>', s, re.S)
    daten = json.loads(roh.group(1))
    knoten = daten["@graph"] if "@graph" in daten else [daten]
    return next(k for k in knoten if k["@type"] == "Organization")


class AngabenTests(unittest.TestCase):
    def test_buero_hat_genau_eine_eigene_telefonnummer(self) -> None:
        # R-RECHT-6.
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
                        "FREMDE_NUMMERN eintragen und dazuschreiben, wem sie gehört.",
                    )
                    self.assertEqual(treffer, treffer.replace(" ", ""),
                                     "tel: braucht die Nummer ohne Leerzeichen")

    def test_sichtbare_nummer_ist_ueberall_gleich_geschrieben(self) -> None:
        """Findet Schreibweisen wie 0176/42904270 neben der kanonischen.

        Geprüft wird nur der sichtbare Text: Attributwerte und das JSON-LD
        führen die Nummer bewusst in der technischen Form ohne Leerzeichen.
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

        for stelle in ("partials/rail.html", "pages/impressum.html"):
            text = quelle(stelle)
            with self.subTest(datei=stelle):
                self.assertIn(STRASSE, text)
                self.assertIn(PLZ_ORT[0], text)
                self.assertIn(PLZ_ORT[1], text)

    def test_telefon_und_mail_stehen_auch_im_json_ld(self) -> None:
        org = organisation()
        self.assertEqual(org["telephone"], TELEFON_TECHNISCH)
        self.assertEqual(org["email"], EMAIL)

    def test_visitenkarte_stimmt_mit_dem_buero_ueberein(self) -> None:
        # R-ANGABEN-6.
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

        # Dieselben zwei Landkreise müssen auch sichtbar auf der Seite stehen.
        rail = (SOURCE / "partials" / "rail.html").read_text(encoding="utf-8")
        for kreis in KREISE:
            with self.subTest(kreis=kreis):
                self.assertIn(kreis, rail)

    def test_telefon_steht_an_jeder_vertragsstelle(self) -> None:
        """R-ANGABEN-1. Die übrigen Tests prüfen nur, dass vorhandene
        Nummern gleich sind — nicht, dass die Nummer überhaupt dasteht."""
        for stelle in STELLEN_TELEFON:
            with self.subTest(stelle=stelle):
                self.assertIn(f'href="tel:{TELEFON_TECHNISCH}"', quelle(stelle))
                self.assertIn(f'href="mailto:{EMAIL}"', quelle(stelle))
        karte = (ROOT / "bb-limen.vcf").read_text(encoding="utf-8")
        self.assertIn(TELEFON_TECHNISCH, karte)

    def test_anschrift_steht_an_jeder_vertragsstelle(self) -> None:
        """R-ANGABEN-3."""
        for stelle in STELLEN_ANSCHRIFT:
            text = quelle(stelle)
            with self.subTest(stelle=stelle):
                self.assertIn(STRASSE, text)
                self.assertIn(PLZ_ORT[0], text)
                self.assertIn(PLZ_ORT[1], text)

    def test_sprechzeiten_stehen_an_jeder_vertragsstelle(self) -> None:
        """R-ANGABEN-4."""
        for stelle, zeilen in SPRECHZEITEN.items():
            text = quelle(stelle)
            for zeile in zeilen:
                with self.subTest(stelle=stelle, zeile=zeile):
                    self.assertIn(zeile, text)

    def test_keine_weitere_uhrzeit_neben_den_sprechzeiten(self) -> None:
        """R-ANGABEN-4, Gegenprobe: Eine neue Stelle mit Uhrzeit fällt auf
        und gehört dann in SPRECHZEITEN und in AGENTS.md."""
        for pfad in sorted((SOURCE / "pages").glob("*.html")) + BAUSTEINE:
            stelle = f"{pfad.parent.name}/{pfad.name}"
            text = quelle(stelle)
            for zeile in SPRECHZEITEN.get(stelle, []):
                text = text.replace(zeile, "")
            with self.subTest(stelle=stelle):
                self.assertNotRegex(text, r"\d{1,2}(?:[:.]\d{2})? Uhr\b")

    def test_gemeindezahl_steht_im_fliesstext(self) -> None:
        """R-ANGABEN-2."""
        for stelle in STELLEN_GEMEINDEZAHL:
            with self.subTest(stelle=stelle):
                self.assertRegex(quelle(stelle), rf"\b{GEMEINDEN} Städten? und Gemeinden")
        for pfad in ALLE:
            for zahl in re.findall(r"\b(\d+) Städten? und Gemeinden", pfad.read_text(encoding="utf-8")):
                with self.subTest(datei=pfad.name):
                    self.assertEqual(int(zahl), GEMEINDEN)


if __name__ == "__main__":
    unittest.main()
