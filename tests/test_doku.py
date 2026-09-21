"""Hält die Dokumentation am Bestand fest.

Dokumentation veraltet leise: Eine Datei wird umbenannt, und drei Absätze
nennen weiter den alten Namen. Für Menschen ist das ärgerlich, für einen
KI-Assistenten eine falsche Anweisung. Diese Datei prüft deshalb, dass jede
genannte Datei existiert und jeder Verweis ein Ziel hat.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from site_support import REPO

DOCUMENTS = [REPO / "AGENTS.md", REPO / "README.md", *sorted((REPO / "docs").glob("*.md"))]

# Verzeichnisse, in denen ein ohne Pfad genannter Dateiname liegen darf.
SEARCH_DIRECTORIES = [
    "", "src", "src/pages", "src/partials", "src/grafik", "public", "tools",
    "tools/hooks", "tests", "docs", ".github", ".github/workflows",
]
# Entsteht erst beim Build und liegt deshalb in keinem Quellverzeichnis.
GENERATED = {"sitemap.xml"}
# Unversioniert und lokal; darf fehlen.
LOCAL_PREFIXES = ("dist/", "docs/lokal/", "reports/", "tmp/")
FILE_NAME = re.compile(r"[\w.-]+\.(?:html|css|json|py|sh|yml|md|svg|png|ico|vcf|txt|xml)")
REPO_PATH = re.compile(r"(?:src|public|tools|tests|docs|\.github)/[\w./-]*")


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


if __name__ == "__main__":
    unittest.main()
