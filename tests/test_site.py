from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import xml.etree.ElementTree as ET


from site_support import (
    EMAIL, SITE as ROOT, SOURCE, TELEFON_SICHTBAR, TELEFON_TECHNISCH,
)
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

# R-BESTAND-4: Diese Seiten bleiben aus Suchindex und Sitemap.
NOINDEX_PAGES = {"404.html", "datenschutz.html", "impressum.html"}
# R-FARBE-2: Salbei bedeutet Entlastung; mehr Stellen nehmen ihm die Bedeutung.
RELIEF_BLOCKS = {"index.html": 1, "betreuung.html": 1, "aufgaben.html": 2}
# R-BESTAND-3: Der Hinweis verschwindet erst mit der Registrierung, dann überall.
FOUNDING_NOTICE_PAGES = {
    "index.html", "betreuung.html", "aufgaben.html", "vorsorge.html",
    "fachkreise.html",
}
FOUNDING_NOTICE = "<strong>Büro in Gründung.</strong>"
FOUNDING_NOTICE_IMPRINT = "Registrierung nach § 23 BtOG beantragt, noch nicht erteilt"


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
        # R-BESTAND-2: Die Adressen bleiben.
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

    def test_sitemap_lists_the_intended_urls_with_catalog_dates(self) -> None:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = ET.parse(ROOT / "sitemap.xml").findall("s:url", ns)
        self.assertEqual({url.findtext("s:loc", namespaces=ns) for url in urls}, {
            "https://bb-limen.de/", "https://bb-limen.de/betreuung.html",
            "https://bb-limen.de/aufgaben.html", "https://bb-limen.de/vorsorge.html",
            "https://bb-limen.de/fachkreise.html", "https://bb-limen.de/leichte-sprache.html",
        })
        # R-ORDNUNG-6: lastmod ist der redaktionelle Stand aus dem Katalog,
        # kein Builddatum — und liegt deshalb nie in der Zukunft.
        catalog = json.loads((SOURCE / "seiten.json").read_text(encoding="utf-8"))
        editorial = {
            "https://bb-limen.de/" + ("" if page["file"] == "index.html" else page["file"]): page["lastmod"]
            for page in catalog["pages"] if page["sitemap"]
        }
        for url in urls:
            loc = url.findtext("s:loc", namespaces=ns)
            lastmod = url.findtext("s:lastmod", namespaces=ns)
            with self.subTest(url=loc):
                self.assertEqual(lastmod, editorial[loc])
                self.assertLessEqual(date.fromisoformat(lastmod), date.today())

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
        # R-VERBOT-1, R-PRUEFUNG-4: Die eng begrenzte Validator-Ausnahme darf
        # kein JavaScript verdecken.
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

    def test_theme_colors_are_the_only_media_meta_elements(self) -> None:
        # R-PRUEFUNG-4: Gegentest zur theme-color-Ausnahme des Validators.
        expected = [
            {
                "name": "theme-color",
                "content": "#fbfaf7",
                "media": "(prefers-color-scheme: light)",
            },
            {
                "name": "theme-color",
                "content": "#111312",
                "media": "(prefers-color-scheme: dark)",
            },
        ]
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                media_meta = [
                    attrs for tag, attrs in page.elements
                    if tag == "meta" and "media" in attrs
                ]
                self.assertEqual(media_meta, expected)

    def test_content_security_policy_keeps_the_existing_restrictions(self) -> None:
        # R-VERBOT-1: Die Richtlinie darf nicht gelockert werden.
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
        # R-QUELLE-2, R-BESTAND-2.
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

    def test_json_ld_is_valid_and_claims_no_business_location(self) -> None:
        # R-VERBOT-6: Die Anschrift ist eine angemietete, nicht ständig besetzte
        # Geschäftsadresse. LocalBusiness und seine Untertypen (darunter
        # ProfessionalService) behaupten einen Standort mit Publikumsverkehr.
        # Der Typ bleibt Organization mit PostalAddress.
        for path in PAGES:
            scripts = re.findall(
                r'<script type="application/ld\+json">(.*?)</script>',
                path.read_text(encoding="utf-8"),
                re.DOTALL,
            )
            for script in scripts:
                data = json.loads(script)
                self.assertEqual([node["@type"] for node in data["@graph"]],
                                 ["Organization", "WebSite"])
                for forbidden in ("LocalBusiness", "ProfessionalService", "LegalService"):
                    self.assertNotIn(forbidden, json.dumps(data))
                # Erfundene Werte: Bewertungen gibt es nicht (R-VERBOT-4).
                for forbidden in ("aggregateRating", '"review"'):
                    self.assertNotIn(forbidden, json.dumps(data))

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
        text = (ROOT / "index.html").read_text(encoding="utf-8")
        callbar = re.search(r"<!-- #callbar -->(.*?)<!-- /#callbar -->", text, re.S)[1]
        self.assertIn(f'href="tel:{TELEFON_TECHNISCH}"', callbar)
        self.assertIn(f'href="mailto:{EMAIL}"', callbar)
        self.assertIn(f'aria-label="Büro BB Limen unter {TELEFON_SICHTBAR} anrufen"', callbar)
        self.assertIn(f'aria-label="E-Mail an {EMAIL} schreiben"', callbar)

    def test_legal_links_are_on_every_page(self) -> None:
        # R-BESTAND-1, § 5 DDG: wörtlich benannt, auf jeder Seite, im Seitenfuß
        # und in der Kolumne — also mindestens zweimal.
        for path in PAGES:
            text = path.read_text(encoding="utf-8")
            for target, label in (("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz")):
                with self.subTest(page=path.name, link=label):
                    self.assertGreaterEqual(text.count(f'<a href="{target}">{label}</a>'), 2)

    def test_only_the_mandatory_pages_are_noindex(self) -> None:
        for name, page in self.parsed.items():
            robots = [attrs.get("content") for tag, attrs in page.elements
                      if tag == "meta" and attrs.get("name") == "robots"]
            with self.subTest(page=name):
                self.assertEqual(robots, ["noindex"] if name in NOINDEX_PAGES else [])

    def test_every_page_declares_german(self) -> None:
        for name, page in self.parsed.items():
            html = [attrs for tag, attrs in page.elements if tag == "html"]
            with self.subTest(page=name):
                self.assertEqual(html, [{"lang": "de"}])

    def test_relief_colour_stays_at_four_places(self) -> None:
        for name, page in self.parsed.items():
            blocks = sum("gut" in (attrs.get("class") or "").split() for _, attrs in page.elements)
            with self.subTest(page=name):
                self.assertEqual(blocks, RELIEF_BLOCKS.get(name, 0))

    def test_founding_notice_is_everywhere_or_nowhere(self) -> None:
        with_notice = {path.name for path in PAGES
                       if FOUNDING_NOTICE in path.read_text(encoding="utf-8")}
        imprint = FOUNDING_NOTICE_IMPRINT in (ROOT / "impressum.html").read_text(encoding="utf-8")
        if with_notice or imprint:
            self.assertEqual(with_notice, FOUNDING_NOTICE_PAGES)
            self.assertTrue(imprint, "Hinweis steht auf den Seiten, fehlt aber im Impressum")


if __name__ == "__main__":
    unittest.main()
