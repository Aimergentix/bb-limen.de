"""Hält die Dokumentation am Bestand fest.

Dokumentation veraltet leise: Eine Datei wird umbenannt, und drei Absätze
nennen weiter den alten Namen. Für Menschen ist das ärgerlich, für einen
KI-Assistenten eine falsche Anweisung. Diese Datei prüft deshalb, dass jede
genannte Datei existiert, jeder Verweis ein Ziel hat, jede Regelkennung
definiert ist und mehrdeutige Begriffe draußen bleiben (R-ORDNUNG-1 bis -3).
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from site_support import REPO

DOCUMENTS = [REPO / "AGENTS.md", REPO / "README.md", *sorted((REPO / "docs").glob("*.md"))]
# Das Entscheidungsprotokoll ist Geschichte und darf Dateien nennen, die es
# nicht mehr gibt. Seine Verweise und Kennungen werden trotzdem geprüft.
HISTORY = {"entscheidungen.md"}

# Alles Versionierte, in dem eine Regelkennung oder ein Abschnittsverweis
# stehen kann. Die Seiten selbst gehören nicht dazu: Sie sind Inhalt.
REFERENCING_DIRECTORIES = ["tests", "tools", "docs", ".github", "src/partials", "public"]
TEXT_SUFFIXES = {".py", ".sh", ".yml", ".md", ".html", ".txt", ".json", ""}

RULE_ID = re.compile(r"\bR-[A-Z]+-\d+\b")
DECISION_ID = re.compile(r"\bE-\d{2}\b")
# Abschnittsnummern verrutschen beim ersten Umbau. Verwiesen wird über
# Kennungen, Dateien und Überschriften.
SECTION_REFERENCE = re.compile(r"(?:README|AGENTS)(?:\.md)?`?,? ?§ ?\d")
# Wörter, die hier schon Verschiedenes bedeutet haben. Der Vertrag definiert
# unter „Begriffe" je ein Wort; diese Nebenformen bleiben draußen.
AMBIGUOUS_TERMS = {
    "Inhaltsseite": "meinte vier, fünf oder acht Seiten; Seiten beim Namen oder Sprachprofil nennen",
    "Seitenkatalog": "heißt Katalog",
    "Kontaktleiste": "heißt Anrufleiste",
    "Aufgabenkreise": "R-RECHT-2",
}

# Verzeichnisse, in denen ein ohne Pfad genannter Dateiname liegen darf.
SEARCH_DIRECTORIES = [
    "", "src", "src/pages", "src/partials", "src/grafik", "public", "tools",
    "tools/hooks", "tests", "docs", ".github", ".github/workflows",
]
# Entsteht erst beim Build und liegt deshalb in keinem Quellverzeichnis.
GENERATED = {"sitemap.xml", "bb-limen.vcf"}
# Unversioniert und lokal; darf fehlen.
LOCAL_PREFIXES = ("dist/", "docs/lokal/", "reports/", "tmp/")
FILE_NAME = re.compile(r"[\w.-]+\.(?:html|css|json|py|sh|yml|md|svg|png|ico|vcf|txt|xml)")
REPO_PATH = re.compile(r"(?:src|public|tools|tests|docs|\.github)/[\w./-]*")


def referencing_files() -> list[Path]:
    files = [REPO / "AGENTS.md", REPO / "README.md"]
    for directory in REFERENCING_DIRECTORIES:
        files += [path for path in sorted((REPO / directory).rglob("*"))
                  if path.is_file() and path.suffix in TEXT_SUFFIXES
                  and "__pycache__" not in path.parts and "lokal" not in path.parts]
    return files


def code_spans(text: str) -> list[str]:
    text = re.sub(r"^(```|~~~).*?^\1", "", text, flags=re.S | re.M)
    return re.findall(r"`([^`\n]+)`", text)


def slug(heading: str) -> str:
    """Sprungmarke, wie GitHub sie aus einer Überschrift bildet."""
    heading = re.sub(r"[`*_]", "", heading.strip().lower())
    return re.sub(r"[^\w\- ]", "", heading).replace(" ", "-")


def anchors(path: Path) -> set[str]:
    text = re.sub(r"^(```|~~~).*?^\1", "", path.read_text(encoding="utf-8"), flags=re.S | re.M)
    return {slug(match) for match in re.findall(r"^#{1,6} +(.+)$", text, flags=re.M)}


class DocumentationTests(unittest.TestCase):
    def test_named_files_exist(self) -> None:
        for document in DOCUMENTS:
            for span in code_spans(document.read_text(encoding="utf-8")):
                token = span.strip().rstrip(".,;:")
                if any(sign in token for sign in "<>*{}$ ") or token.startswith(LOCAL_PREFIXES):
                    continue
                if document.name in HISTORY:
                    continue
                with self.subTest(document=document.name, named=token):
                    if REPO_PATH.fullmatch(token):
                        self.assertTrue((REPO / token).exists(), "genannter Pfad fehlt")
                    elif FILE_NAME.fullmatch(token) and token not in GENERATED:
                        self.assertTrue(
                            any((REPO / directory / token).is_file() for directory in SEARCH_DIRECTORIES),
                            "genannte Datei gibt es in keinem Quellverzeichnis",
                        )

    def test_relative_links_and_anchors_resolve(self) -> None:
        for document in DOCUMENTS:
            text = document.read_text(encoding="utf-8")
            for target in re.findall(r"\[[^\]]*\]\(([^)\s]+)\)", text):
                if re.match(r"[a-z]+:", target):
                    continue
                file_part, _, anchor = target.partition("#")
                path = (document.parent / file_part).resolve() if file_part else document
                with self.subTest(document=document.name, link=target):
                    self.assertTrue(path.exists(), "Verweisziel fehlt")
                    if anchor:
                        self.assertIn(anchor, anchors(path), "Sprungmarke fehlt im Ziel")

    def test_rule_and_decision_ids_are_defined_exactly_once(self) -> None:
        contract = (REPO / "AGENTS.md").read_text(encoding="utf-8")
        decisions = (REPO / "docs/entscheidungen.md").read_text(encoding="utf-8")
        rules = re.findall(r"\*\*(R-[A-Z]+-\d+)\*\*", contract)
        entries = re.findall(r"^## (E-\d{2}) ", decisions, flags=re.M)
        self.assertEqual(sorted(rules), sorted(set(rules)), "Regelkennung doppelt vergeben")
        self.assertEqual(sorted(entries), sorted(set(entries)), "Entscheidungskennung doppelt vergeben")
        for path in referencing_files():
            text = path.read_text(encoding="utf-8")
            for rule in set(RULE_ID.findall(text)):
                with self.subTest(file=str(path.relative_to(REPO)), rule=rule):
                    self.assertIn(rule, rules, "Kennung ist in AGENTS.md nicht definiert")
            if path.suffix == ".md":
                for entry in set(DECISION_ID.findall(text)):
                    with self.subTest(file=str(path.relative_to(REPO)), entry=entry):
                        self.assertIn(entry, entries, "Kennung fehlt in docs/entscheidungen.md")

    def test_no_references_by_section_number(self) -> None:
        for path in referencing_files():
            with self.subTest(file=str(path.relative_to(REPO))):
                self.assertNotRegex(path.read_text(encoding="utf-8"), SECTION_REFERENCE)

    def test_documents_avoid_ambiguous_terms(self) -> None:
        for document in DOCUMENTS:
            if document.name in HISTORY:
                continue
            text = document.read_text(encoding="utf-8")
            for term, reason in AMBIGUOUS_TERMS.items():
                with self.subTest(document=document.name, term=term):
                    self.assertNotIn(term, text.replace("„Aufgabenkreise\"", ""), reason)


if __name__ == "__main__":
    unittest.main()
