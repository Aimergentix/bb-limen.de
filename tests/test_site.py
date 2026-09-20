from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


from site_support import SITE as ROOT, SOURCE
EXPECTED_PAGE_NAMES = {
    "404.html",
    "aufgaben.html",
    "betreuung.html",
    "datenschutz.html",
    "fachkreise.html",
    "impressum.html",
    "index.html",
    "leichte-sprache.html",
    "vorsorge.html",
}
PAGES = sorted(ROOT.glob("*.html"))


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.tags: Counter[str] = Counter()
        self.headings: list[int] = []
        self.elements: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.tags[tag] += 1
        self.elements.append((tag, dict(attrs)))
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

    def test_public_page_inventory_uses_the_intended_names(self) -> None:
        self.assertEqual({path.name for path in PAGES}, EXPECTED_PAGE_NAMES)

    def test_output_contains_only_the_expected_public_files(self) -> None:
        expected = EXPECTED_PAGE_NAMES | {
            "style.css", "sitemap.xml", "robots.txt", "CNAME", "bb-limen.vcf",
            "favicon.ico", "apple-touch-icon.png", "vorschau.png",
        }
        self.assertEqual({path.name for path in ROOT.iterdir()}, expected)
        for path in ROOT.iterdir():
            self.assertTrue(path.is_file())
            self.assertFalse(path.is_symlink())

    def test_sitemap_preserves_urls_and_editorial_dates(self) -> None:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = ET.parse(ROOT / "sitemap.xml").findall("s:url", ns)
        self.assertEqual({url.findtext("s:loc", namespaces=ns) for url in urls}, {
            "https://bb-limen.de/", "https://bb-limen.de/betreuung.html",
            "https://bb-limen.de/aufgaben.html", "https://bb-limen.de/vorsorge.html",
            "https://bb-limen.de/fachkreise.html", "https://bb-limen.de/leichte-sprache.html",
        })
        for url in urls:
            self.assertRegex(url.findtext("s:lastmod", namespaces=ns), r"^\d{4}-\d{2}-\d{2}$")

    def test_error_page_base_precedes_relative_resources(self) -> None:
        text = (ROOT / "404.html").read_text(encoding="utf-8")
        self.assertEqual(text.count('<base href="/">'), 1)
        self.assertLess(text.index('<base href="/">'), text.index('<link '))
        self.assertLess(text.index('<base href="/">'), text.index('</head>'))

    def test_local_assets_exist(self) -> None:
        for path in PAGES:
            text = path.read_text(encoding="utf-8")
            for value in re.findall(r'(?:src|href)="([^"#]+)"', text):
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path or url.path == "/":
                    continue
                self.assertTrue((ROOT / url.path).is_file(), f"{path.name}: {value}")
            self.assertNotIn("@include", text)
            self.assertNotIn("%%CUR-", text)

    def test_scripts_are_only_the_index_json_ld_data_block(self) -> None:
        # Die eng begrenzte Validator-Ausnahme darf kein JavaScript verdecken.
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                scripts = [attrs for tag, attrs in page.elements if tag == "script"]
                expected = [{"type": "application/ld+json"}] if name == "index.html" else []
                self.assertEqual(scripts, expected)
                for _, attrs in page.elements:
                    self.assertFalse(any(key.startswith("on") for key in attrs))
                    for key in ("href", "src", "action"):
                        value = re.sub(r"[\x00-\x20]", "", attrs.get(key) or "")
                        self.assertFalse(value.lower().startswith("javascript:"))

    def test_stylesheet_is_the_single_local_file(self) -> None:
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                styles = [attrs.get("href") for tag, attrs in page.elements
                          if tag == "link" and "stylesheet" in (attrs.get("rel") or "").split()]
                self.assertEqual(styles, ["style.css"])
                self.assertEqual(page.tags["style"], 0)
                self.assertFalse(any("style" in attrs for _, attrs in page.elements))

    def test_content_security_policy_keeps_the_existing_restrictions(self) -> None:
        expected = {
            "default-src": ["'self'"], "img-src": ["'self'", "data:"],
            "style-src": ["'self'"], "font-src": ["'self'"],
            "script-src": ["'none'"], "object-src": ["'none'"],
            "frame-src": ["'none'"], "connect-src": ["'none'"],
            "form-action": ["'none'"], "base-uri": ["'self'"],
        }
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                policies = [attrs.get("content") for tag, attrs in page.elements
                            if tag == "meta" and (attrs.get("http-equiv") or "").lower()
                            == "content-security-policy"]
                self.assertEqual(len(policies), 1)
                directives = [part.split() for part in policies[0].split(";") if part.strip()]
                self.assertEqual(len(directives), len(expected))
                self.assertEqual({parts[0]: parts[1:] for parts in directives}, expected)

    def test_canonical_and_og_urls_follow_page_names(self) -> None:
        for path in PAGES:
            if path.name == "404.html":
                continue
            address = "https://bb-limen.de/" if path.name == "index.html" else f"https://bb-limen.de/{path.name}"
            source = path.read_text(encoding="utf-8")
            with self.subTest(page=path.name):
                self.assertIn(f'<link rel="canonical" href="{address}">', source)
                self.assertIn(f'<meta property="og:url" content="{address}">', source)

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
        rail = (SOURCE / "partials" / "rail.html").read_text(encoding="utf-8")
        links = re.findall(r'<a href="([^"]+)"[^>]*>([^<]+)</a>', rail)
        self.assertEqual(
            links[0:5],
            [
                ("leichte-sprache.html", "Leichte Sprache"),
                ("index.html", "BB Limen"),
                ("betreuung.html", "Betreuung"),
                ("aufgaben.html", "Aufgaben"),
                ("vorsorge.html", "Vorsorge"),
            ],
        )
        self.assertEqual(links[5], ("fachkreise.html", "Für Fachkreise"))

    def test_footer_uses_the_short_office_name(self) -> None:
        foot = (SOURCE / "partials" / "foot.html").read_text(encoding="utf-8")
        self.assertIn("BB Limen · A+M Möller · Berufliche Betreuung", foot)
        self.assertNotIn("Berufliche Betreuung, Binzen", foot)

    def test_mobile_contactbar_uses_direct_contact_links(self) -> None:
        callbar = (SOURCE / "partials" / "callbar.html").read_text(encoding="utf-8")
        self.assertIn('href="tel:+4917642904270"', callbar)
        self.assertIn('href="mailto:info@bb-limen.de"', callbar)
        self.assertIn('aria-label="Büro BB Limen unter +49 176 42904270 anrufen"', callbar)
        self.assertIn('aria-label="E-Mail an info@bb-limen.de schreiben"', callbar)


if __name__ == "__main__":
    unittest.main()
