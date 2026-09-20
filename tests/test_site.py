from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
PAGES = sorted(ROOT.glob("*.html"))


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.tags: Counter[str] = Counter()
        self.headings: list[int] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        if re.fullmatch(r"h[1-6]", tag):
            self.headings.append(int(tag[1]))
        for name, value in attrs:
            if name == "id" and value:
                self.ids.append(value)
            # Nur echte Verweise. <base href="/"> und <link rel="canonical">
            # zeigen nicht auf eine Datei im Verzeichnis.
            if name == "href" and value and tag == "a":
                self.hrefs.append(value)


def parse_page(path: Path) -> PageParser:
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


class SiteStructureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.parsed = {path.name: parse_page(path) for path in PAGES}

    def test_each_page_has_one_main_and_one_h1(self) -> None:
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                self.assertEqual(page.tags["main"], 1)
                self.assertEqual(page.tags["h1"], 1)

    def test_ids_are_unique(self) -> None:
        for name, page in self.parsed.items():
            duplicates = [item for item, count in Counter(page.ids).items() if count > 1]
            with self.subTest(page=name):
                self.assertEqual(duplicates, [])

    def test_heading_levels_do_not_jump(self) -> None:
        for name, page in self.parsed.items():
            jumps = [pair for pair in zip(page.headings, page.headings[1:]) if pair[1] > pair[0] + 1]
            with self.subTest(page=name):
                self.assertEqual(jumps, [])

    def test_internal_links_and_fragments_exist(self) -> None:
        for source_name, page in self.parsed.items():
            for href in page.hrefs:
                target = urlsplit(href)
                if target.scheme or target.netloc or href.startswith(("mailto:", "tel:")):
                    continue
                target_name = target.path or source_name
                target_path = ROOT / target_name
                with self.subTest(source=source_name, href=href):
                    self.assertTrue(target_path.is_file())
                    if target.fragment:
                        self.assertIn(target.fragment, self.parsed[target_name].ids)

    def test_json_ld_is_valid_and_uses_current_types(self) -> None:
        for path in PAGES:
            scripts = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                path.read_text(encoding="utf-8"),
                re.DOTALL,
            )
            for script in scripts:
                data = json.loads(script)
                self.assertNotIn("ProfessionalService", json.dumps(data))

    def test_navigation_has_the_intended_names_and_order(self) -> None:
        rail = (ROOT / "partials" / "rail.html").read_text(encoding="utf-8")
        links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', rail)
        self.assertEqual(
            links[0:5],
            [
                ("leichte-sprache.html", "Leichte Sprache"),
                ("index.html", "BB Limen"),
                ("buero.html", "Betreuung"),
                ("leistungen.html", "Aufgaben"),
                ("vorsorge.html", "Vorsorge"),
            ],
        )
        self.assertEqual(links[5], ("fachkreise.html", "Für Fachkreise"))

    def test_footer_uses_the_short_office_name(self) -> None:
        foot = (ROOT / "partials" / "foot.html").read_text(encoding="utf-8")
        self.assertIn("BB Limen · A+M Möller · Berufliche Betreuung", foot)
        self.assertNotIn("Berufliche Betreuung, Binzen", foot)

    def test_mobile_contactbar_uses_direct_contact_links(self) -> None:
        callbar = (ROOT / "partials" / "callbar.html").read_text(encoding="utf-8")
        self.assertIn('href="tel:+4917642904270"', callbar)
        self.assertIn('href="mailto:info@bb-limen.de"', callbar)
        self.assertIn('aria-label="Aranda Möller unter +49 176 42904270 anrufen"', callbar)
        self.assertIn('aria-label="E-Mail an info@bb-limen.de schreiben"', callbar)


if __name__ == "__main__":
    unittest.main()
