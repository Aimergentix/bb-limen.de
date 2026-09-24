"""Technische Eigenschaften der fertigen Seiten: Verweise, Struktur, Kopfangaben.

Kein Test hier hängt an Wortlaut, Zahlen oder Büroangaben. Was eine Seite
sagt, entscheidet das Büro; geprüft wird, ob sie funktioniert (R-REDAKTION-3).
"""
from __future__ import annotations

import json
import re
import unittest
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, urljoin
import xml.etree.ElementTree as ET


from site_support import REPO, SITE as ROOT, SOURCE
from bureau_data import load_office
from people_data import load_people

PAGES = sorted(ROOT.glob("*.html"))
CATALOG = json.loads((SOURCE / "seiten.json").read_text(encoding="utf-8"))["pages"]
BASE = "https://" + (SOURCE.parent / "public/CNAME").read_text(encoding="utf-8").strip() + "/"


def address(name: str) -> str:
    return BASE if name == "index.html" else BASE + name


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

    def test_sitemap_follows_the_catalog(self) -> None:
        ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = ET.parse(ROOT / "sitemap.xml").findall("s:url", ns)
        # R-ORDNUNG-6: lastmod ist der redaktionelle Stand aus dem Katalog,
        # kein Builddatum — und liegt deshalb nie in der Zukunft.
        editorial = {address(page["file"]): page["lastmod"] for page in CATALOG if page["sitemap"]}
        self.assertEqual({url.findtext("s:loc", namespaces=ns) for url in urls}, set(editorial))
        for url in urls:
            loc = url.findtext("s:loc", namespaces=ns)
            lastmod = url.findtext("s:lastmod", namespaces=ns)
            with self.subTest(url=loc):
                self.assertEqual(lastmod, editorial[loc])
                self.assertLessEqual(date.fromisoformat(lastmod), date.today())

    def test_error_page_links_work_under_nested_missing_addresses(self) -> None:
        page = self.parsed["404.html"]
        self.assertEqual(page.tags["base"], 0, "base würde den Sprunglink umleiten")
        missing = BASE + "ein/tiefer/pfad/"
        skip = next(attrs["href"] for tag, attrs in page.elements
                    if tag == "a" and attrs.get("class") == "skip")
        self.assertEqual(urljoin(missing, skip), missing + "#inhalt")
        for tag, attrs in page.elements:
            for key in ("href", "src"):
                value = attrs.get(key)
                if not value or value.startswith("#") or urlsplit(value).scheme:
                    continue
                with self.subTest(tag=tag, value=value):
                    self.assertTrue(value.startswith("/"))
                    self.assertTrue((ROOT / urlsplit(urljoin(missing, value)).path.lstrip("/")).is_file())

    def test_local_assets_exist(self) -> None:
        for path in PAGES:
            text = path.read_text(encoding="utf-8")
            for value in re.findall(r'(?:src|href)="([^"#]+)"', text):
                url = urlsplit(value)
                if url.scheme or url.netloc or not url.path or url.path == "/":
                    continue
                self.assertTrue((ROOT / url.path.lstrip("/")).is_file(), f"{path.name}: {value}")
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
                self.assertEqual(styles, ["/style.css" if name == "404.html" else "style.css"])
                self.assertEqual(page.tags["style"], 0)
                self.assertFalse(any("style" in attrs for _, attrs in page.elements))

    def test_theme_colors_are_the_only_media_meta_elements(self) -> None:
        # R-PRUEFUNG-4: Gegentest zur theme-color-Ausnahme des Validators.
        # Geprüft wird die Form, nicht der Farbwert (R-REDAKTION-3).
        expected = [
            ("theme-color", "(prefers-color-scheme: light)"),
            ("theme-color", "(prefers-color-scheme: dark)"),
        ]
        for name, page in self.parsed.items():
            with self.subTest(page=name):
                media_meta = [
                    attrs for tag, attrs in page.elements
                    if tag == "meta" and "media" in attrs
                ]
                self.assertEqual([(attrs.get("name"), attrs.get("media")) for attrs in media_meta], expected)
                for attrs in media_meta:
                    self.assertEqual(set(attrs), {"name", "content", "media"})
                    self.assertTrue((attrs["content"] or "").strip())

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
            source = path.read_text(encoding="utf-8")
            with self.subTest(page=path.name):
                self.assertIn(f'<link rel="canonical" href="{address(path.name)}">', source)
                self.assertIn(f'<meta property="og:url" content="{address(path.name)}">', source)

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
                target_name = "index.html" if target.path == "/" else target.path.lstrip("/") or source_name
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

    def test_legal_links_are_on_every_page(self) -> None:
        # R-BESTAND-1, § 5 DDG: wörtlich benannt, auf jeder Seite, im Seitenfuß
        # und in der Kolumne — also mindestens zweimal.
        for path in PAGES:
            text = path.read_text(encoding="utf-8")
            for target, label in (("impressum.html", "Impressum"), ("datenschutz.html", "Datenschutz")):
                with self.subTest(page=path.name, link=label):
                    prefix = "/" if path.name == "404.html" else ""
                    self.assertGreaterEqual(text.count(f'<a href="{prefix}{target}">{label}</a>'), 2)

    def test_noindex_and_sitemap_agree(self) -> None:
        # R-BESTAND-4: Was nicht in der Sitemap steht, trägt noindex — und umgekehrt.
        in_sitemap = {page["file"] for page in CATALOG if page["sitemap"]}
        for name, page in self.parsed.items():
            robots = [attrs.get("content") for tag, attrs in page.elements
                      if tag == "meta" and attrs.get("name") == "robots"]
            with self.subTest(page=name):
                self.assertEqual(robots, [] if name in in_sitemap else ["noindex"])

    def test_every_page_declares_german(self) -> None:
        for name, page in self.parsed.items():
            html = [attrs for tag, attrs in page.elements if tag == "html"]
            with self.subTest(page=name):
                self.assertEqual(html, [{"lang": "de"}])

    def test_vcards_keep_the_exchange_format(self) -> None:
        # R-ANGABEN-6: UTF-8, CRLF, keine Zeile über 75 Bytes.
        cards = sorted(ROOT.glob("*.vcf"))
        self.assertIn(ROOT / "bb-limen.vcf", cards)
        for path in cards:
            raw = path.read_bytes()
            with self.subTest(card=path.name):
                raw.decode("utf-8")
                self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
                self.assertTrue(raw.startswith(b"BEGIN:VCARD\r\nVERSION:3.0\r\n"))
                self.assertTrue(raw.endswith(b"END:VCARD\r\n"))
                for line in raw.split(b"\r\n"):
                    self.assertLessEqual(len(line), 75)

    def test_contact_literals_are_not_maintained_in_templates(self) -> None:
        # R-ANGABEN-1: Die Werte kommen aus der Quelle selbst. Geprüft wird
        # nicht, ob sie stimmen, sondern dass sie nur an einer Stelle stehen.
        live = load_office(REPO)
        values = (*live["telefon"].values(), live["email"], live["email_datenschutz"], live["anschrift"]["strasse"],
                  live["postanschrift"]["postfach"])
        for person in load_people(REPO):
            values += (*(person["telefon"] or {}).values(), person["email"], person["haftpflicht"],
                       (person["anschrift"] or {}).get("strasse"))
        values = tuple(filter(None, values))
        for path in [*(SOURCE / "pages").glob("*.html"), *(SOURCE / "partials").glob("*.html"),
                     *(SOURCE / "betreuende").glob("*.html")]:
            text = path.read_text(encoding="utf-8")
            for value in values:
                with self.subTest(path=path.name, value=value):
                    self.assertNotIn(value, text)


if __name__ == "__main__":
    unittest.main()
