"""Der Build gegen eine erfundene Test-Website: Fehleingaben, Schutz der Quellen
und fremder Verzeichnisse. Die echten Seiten sind hier nicht beteiligt."""
from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from fixture_site import OFFICE, page, write_site
from site_support import REPO


class BuildTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="bb-limen-build-test-")
        self.addCleanup(self.temp.cleanup)
        self.work = Path(self.temp.name)
        shutil.copytree(REPO / "tools", self.work / "tools", ignore=shutil.ignore_patterns("__pycache__"))
        write_site(self.work)
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)

    def run_build(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["sh", str(self.work / "tools/build.sh"), *args],
                              cwd="/tmp", text=True, capture_output=True, check=False)

    def snapshot(self, directory: str) -> dict[str, bytes]:
        base = self.work / directory
        return {str(path.relative_to(base)): path.read_bytes()
                for path in base.rglob("*") if path.is_file()}

    def change_page(self, old: str, new: str) -> None:
        path = self.work / "src/pages/index.html"
        path.write_text(path.read_text(encoding="utf-8").replace(old, new, 1), encoding="utf-8")

    def change_catalog(self, change) -> None:
        path = self.work / "src/seiten.json"
        catalog = json.loads(path.read_text())
        change(catalog)
        path.write_text(json.dumps(catalog))

    def change_office(self, change) -> None:
        path = self.work / "src/bureauangaben.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        change(data)
        path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def test_office_change_reaches_pages_json_ld_and_vcard(self) -> None:
        """R-ANGABEN-1, R-ANGABEN-6: Eine Quelle, alle Verwendungen."""
        self.change_office(lambda data: data.update(
            telefon={"e164": "+4930123456", "sichtbar": "+49 30 123456"},
            email="kontakt@example.org",
            anschrift={"strasse": "Teststraße 42", "plz": "12345", "ort": "Testort",
                       "bundesland": "Testland", "land": "DE"},
            sprechzeiten={"regulaer": {"tage": ["Freitag"], "von": "09:30", "bis": "12:45"},
                          "nach_vereinbarung": ["Samstag"]},
        ))
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        for path in (self.work / "dist").glob("*.html"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(page=path.name):
                self.assertIn('href="tel:+4930123456"', text)
                self.assertIn('href="mailto:kontakt@example.org"', text)
                self.assertIn("Teststraße 42", text)
                self.assertIn("12345 Testort", text)
                self.assertIn("Fr 9:30–12:45 Uhr", text)
                self.assertIn("Sa nach Vereinbarung", text)
                for old in (OFFICE["telefon"]["e164"], OFFICE["email"], OFFICE["anschrift"]["strasse"],
                            OFFICE["anschrift"]["plz"], "10–12", "%%BUREAU"):
                    self.assertNotIn(old, text)
        index = (self.work / "dist/index.html").read_text(encoding="utf-8")
        for sentence in ("Freitag von 9:30 bis 12:45 Uhr. Samstag nach Vereinbarung.",
                         "Am Freitag. Von 9:30 Uhr bis 12:45 Uhr. Am Samstag geht es auch."):
            self.assertIn(sentence, index)
        for field in ('"telephone": "+4930123456"', '"email": "kontakt@example.org"',
                      '"addressLocality": "Testort"', '"addressRegion": "Testland"'):
            self.assertIn(field, index)
        card = (self.work / "dist/bb-limen.vcf").read_bytes().decode("utf-8")
        for field in ("TEL;TYPE=WORK,VOICE:+4930123456\r\n", "EMAIL;TYPE=INTERNET,WORK:kontakt@example.org\r\n",
                      "ADR;TYPE=WORK:;;Teststraße 42;Testort;Testland;12345;DE\r\n"):
            self.assertIn(field, card)

    def test_invalid_office_data_preserves_last_good_output(self) -> None:
        path = self.work / "src/bureauangaben.json"
        original = path.read_bytes()
        changes = [
            lambda d: d.pop("email"),
            lambda d: d.update(unbekannt="Wert"),
            lambda d: d.update(telefon=[]),
            lambda d: d["telefon"].update(sichtbar="+49 123"),
            lambda d: d.update(email="mail@example.org?subject=test"),
            lambda d: d["anschrift"].update(strasse="Straße\nZusatz"),
            lambda d: d["anschrift"].update(strasse="Straße\u2028Zusatz"),
            lambda d: d["anschrift"].update(ort="%%BUREAU:email%%"),
            lambda d: d["anschrift"].update(plz="1234"),
            lambda d: d["sprechzeiten"]["regulaer"].update(von="24:00"),
            lambda d: d["sprechzeiten"]["regulaer"].update(bis="09:00"),
            lambda d: d["sprechzeiten"]["regulaer"].update(tage=[]),
            lambda d: d["sprechzeiten"]["regulaer"].update(tage=["Dienstag", "Dienstag"]),
            lambda d: d["sprechzeiten"]["regulaer"].update(tage=[{}]),
            lambda d: d["sprechzeiten"].update(nach_vereinbarung=["Dienstag"]),
        ]
        for number, change in enumerate(changes):
            with self.subTest(case=number):
                path.write_bytes(original)
                self.change_office(change)
                self.assert_build_fails_without_writes()
        path.write_text('{"email": "eins", "email": "zwei"}', encoding="utf-8")
        self.assert_build_fails_without_writes()
        path.unlink()
        self.assert_build_fails_without_writes()

    def test_unknown_or_wrong_context_office_tokens_are_rejected(self) -> None:
        path = self.work / "src/pages/index.html"
        original = path.read_bytes()
        for token in ("%%BUREAU:unbekannt%%", "%%BUREAU:email%", '"%%BUREAU_JSON:email%%"'):
            with self.subTest(token=token):
                path.write_bytes(original)
                self.change_page("</main>", token + "</main>")
                self.assert_build_fails_without_writes()
        path.write_bytes(original)
        self.change_page("%%BUREAU_JSON:email%%", "%%BUREAU:email%%")
        self.assert_build_fails_without_writes()

    def test_vcard_cannot_be_shadowed_by_public_copy(self) -> None:
        """R-ANGABEN-6: Keine zweite Quelle für die Bürovisitenkarte."""
        (self.work / "public/bb-limen.vcf").write_text("fremde Karte", encoding="utf-8")
        self.change_catalog(lambda data: data["public_files"].append("bb-limen.vcf"))
        self.assert_build_fails_without_writes()

    def assert_build_fails_without_writes(self) -> None:
        before = {name: self.snapshot(name) for name in ("src", "public", "dist")}
        result = self.run_build()
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("FEHLER:", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        for name in before:
            self.assertEqual(before[name], self.snapshot(name))

    def test_error_page_links_are_anchored_at_the_domain_root(self) -> None:
        """404.html wird auch unter /ein/tiefer/pfad/ ausgeliefert."""
        text = (self.work / "dist/404.html").read_text(encoding="utf-8")
        for link in ('href="/style.css"', 'href="/favicon.ico"', 'href="/index.html"', 'href="/zweite.html"',
                     'href="#inhalt"'):
            self.assertIn(link, text)
        self.assertIn('href="style.css"', (self.work / "dist/index.html").read_text(encoding="utf-8"))

    def test_error_page_links_survive_unusual_line_separators(self) -> None:
        """Aus Word oder PDF eingefügte Zeilentrenner verschieben keine Verweise."""
        text = "Absatz\u2028Zeile\x85Zeile\rZeile\x0cEnde"
        (self.work / "src/pages/404.html").write_bytes(
            page("Nicht gefunden", body=f"<p>{text}</p>\n").encode("utf-8"))
        result = self.run_build()
        self.assertEqual(result.returncode, 0, result.stderr)
        output = (self.work / "dist/404.html").read_bytes().decode("utf-8")
        self.assertIn(f"<p>{text}</p>\n", output)
        for link in ('href="/style.css"', 'href="/favicon.ico"', 'href="/index.html"', 'href="/zweite.html"'):
            self.assertIn(link, output)
        self.assertIn("<h1>Nicht gefunden</h1>", output)

    def test_build_is_repeatable_and_preserves_sources(self) -> None:
        before = {name: self.snapshot(name) for name in ("src", "public", "dist")}
        self.assertEqual(self.run_build().returncode, 0)
        for name in before:
            self.assertEqual(before[name], self.snapshot(name))
        self.assertEqual(self.run_build("--check").returncode, 0)

    def test_missing_partial_preserves_last_good_output(self) -> None:
        (self.work / "src/partials/rail.html").unlink()
        self.assert_build_fails_without_writes()

    def test_missing_include_preserves_last_good_output(self) -> None:
        self.change_page("<!-- @include rail -->", "")
        self.assert_build_fails_without_writes()

    def test_duplicate_include_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- @include rail -->\n<!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_same_line_include_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "Text <!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_wrong_order_is_rejected(self) -> None:
        self.change_page("<!-- @include skip -->", "<!-- @include rail -->")
        self.assert_build_fails_without_writes()

    def test_nested_include_is_rejected(self) -> None:
        (self.work / "src/partials/rail.html").write_text("<!-- @include foot -->\n")
        self.assert_build_fails_without_writes()

    def test_old_generated_blocks_are_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- #rail -->\nalt\n<!-- /#rail -->")
        self.assert_build_fails_without_writes()

    def test_unknown_navigation_target_is_rejected(self) -> None:
        self.change_page("<!-- @include rail -->", "<!-- @include rail -->\n%%CUR-unbekannt%%")
        self.assert_build_fails_without_writes()

    def test_unregistered_page_is_rejected(self) -> None:
        shutil.copy2(self.work / "src/pages/index.html", self.work / "src/pages/neu.html")
        self.assert_build_fails_without_writes()

    def test_missing_page_is_rejected(self) -> None:
        (self.work / "src/pages/zweite.html").unlink()
        self.assert_build_fails_without_writes()

    def test_empty_catalog_is_rejected(self) -> None:
        self.change_catalog(lambda data: data.update(pages=[]))
        self.assert_build_fails_without_writes()

    def test_duplicate_catalog_page_is_rejected(self) -> None:
        self.change_catalog(lambda data: data["pages"].append(data["pages"][0]))
        self.assert_build_fails_without_writes()

    def test_duplicate_catalog_keys_are_rejected(self) -> None:
        """R-QUELLE-3: Mehrdeutige Katalogwerte dürfen nicht still gewinnen."""
        path = self.work / "src/seiten.json"
        path.write_text(path.read_text().replace('"sitemap": true',
                                               '"sitemap": false, "sitemap": true', 1))
        self.assert_build_fails_without_writes()

    def test_misplaced_public_files_are_rejected(self) -> None:
        """R-QUELLE-1, R-QUELLE-3: Keine wirkungslosen Zweitfassungen im Root."""
        for name in ("robots.txt", "sitemap.xml", "index.html", "style.css"):
            with self.subTest(file=name):
                path = self.work / name
                path.write_text("versehentlich hier geändert", encoding="utf-8")
                self.assert_build_fails_without_writes()
                path.unlink()

    def test_invalid_catalog_values_are_rejected(self) -> None:
        original = (self.work / "src/seiten.json").read_bytes()
        for field, value in (("file", "../index.html"), ("unbekannt", "Wert"),
                             ("sitemap", "ja"), ("lastmod", "2026-02-30")):
            with self.subTest(field=field):
                (self.work / "src/seiten.json").write_bytes(original)
                self.change_catalog(lambda data: data["pages"][0].update({field: value}))
                self.assert_build_fails_without_writes()

    def test_unlisted_public_file_is_rejected(self) -> None:
        (self.work / "public/notiz.txt").write_text("privat")
        self.assert_build_fails_without_writes()

    def test_public_symlink_is_rejected(self) -> None:
        file = self.work / "public/robots.txt"
        file.unlink()
        file.symlink_to(self.work / "src/seiten.json")
        self.assert_build_fails_without_writes()

    def test_empty_public_file_is_rejected(self) -> None:
        (self.work / "public/favicon.ico").write_bytes(b"")
        self.assert_build_fails_without_writes()

    def test_check_detects_drift_without_repairing(self) -> None:
        (self.work / "dist/index.html").write_text("manuell")
        before = self.snapshot("dist")
        self.assertNotEqual(self.run_build("--check").returncode, 0)
        self.assertEqual(before, self.snapshot("dist"))

    def test_stale_output_is_removed_on_next_build(self) -> None:
        (self.work / "dist/alt.html").write_text("alt")
        self.assertNotEqual(self.run_build("--check").returncode, 0)
        self.assertEqual(self.run_build().returncode, 0)
        self.assertFalse((self.work / "dist/alt.html").exists())

    def test_existing_foreign_output_directory_is_preserved(self) -> None:
        before = self.snapshot("src")
        self.assertNotEqual(self.run_build("--output", str(self.work / "src")).returncode, 0)
        self.assertEqual(before, self.snapshot("src"))

    def test_new_output_inside_source_tree_is_rejected(self) -> None:
        output = self.work / "src/ausgabe"
        self.assertNotEqual(self.run_build("--output", str(output)).returncode, 0)
        self.assertFalse(output.exists())

    def test_output_symlink_is_rejected(self) -> None:
        shutil.rmtree(self.work / "dist")
        (self.work / "dist").symlink_to(self.work / "public", target_is_directory=True)
        before = self.snapshot("public")
        self.assertNotEqual(self.run_build().returncode, 0)
        self.assertEqual(before, self.snapshot("public"))


if __name__ == "__main__":
    unittest.main()
