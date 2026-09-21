"""Eine kleine erfundene Website für die Tests der Werkzeuge.

Die Werkzeugtests laufen gegen diese Dateien, nie gegen die echten Seiten:
Eine Änderung an Text, Büroangaben oder Sprechzeiten der Website kann sie
deshalb nicht rot machen (R-REDAKTION-3).
"""
from __future__ import annotations

import copy
import json
from pathlib import Path

OFFICE = {
    "telefon": {"e164": "+4930111111", "sichtbar": "+49 30 111111"},
    "email": "buero@example.org",
    "anschrift": {"strasse": "Musterweg 1", "plz": "10115", "ort": "Musterstadt",
                  "bundesland": "Musterland", "land": "DE"},
    "sprechzeiten": {"regulaer": {"tage": ["Dienstag", "Donnerstag"], "von": "10:00", "bis": "12:00"},
                     "nach_vereinbarung": ["Montag"]},
}

CATALOG = {
    "pages": [
        {"file": "index.html", "sitemap": True, "lastmod": "2026-01-01"},
        {"file": "zweite.html", "sitemap": True, "lastmod": "2026-01-01"},
        {"file": "404.html", "sitemap": False},
    ],
    "public_files": ["robots.txt", "CNAME", "favicon.ico"],
}

PARTIALS = {
    "head": '<meta charset="utf-8">\n<link rel="icon" href="favicon.ico">\n<link rel="stylesheet" href="style.css">\n',
    "skip": '<a class="skip" href="#inhalt">Zum Inhalt springen</a>\n',
    "rail": ('<nav><a href="index.html"%%CUR-index%%>Start</a> <a href="zweite.html"%%CUR-zweite%%>Zweite</a></nav>\n'
             '<p><a href="tel:%%BUREAU:telefon.e164%%">%%BUREAU:telefon.sichtbar%%</a> '
             '%%BUREAU:sprechzeiten.kurz.regulaer%% %%BUREAU:sprechzeiten.kurz.termin%% '
             '%%BUREAU:anschrift.strasse%%, %%BUREAU:anschrift.plz%% %%BUREAU:anschrift.ort%%</p>\n'),
    "foot": '<footer><a href="zweite.html">Zweite</a></footer>\n',
    "callbar": '<nav><a href="mailto:%%BUREAU:email%%">E-Mail</a></nav>\n',
}

JSON_LD = """<script type="application/ld+json">
{"@context": "https://schema.org", "@graph": [{
  "@type": "Organization", "name": "Testbüro", "url": "https://example.org/",
  "telephone": "%%BUREAU_JSON:telefon.e164%%", "email": "%%BUREAU_JSON:email%%",
  "address": {"@type": "PostalAddress",
    "streetAddress": "%%BUREAU_JSON:anschrift.strasse%%", "postalCode": "%%BUREAU_JSON:anschrift.plz%%",
    "addressLocality": "%%BUREAU_JSON:anschrift.ort%%", "addressRegion": "%%BUREAU_JSON:anschrift.bundesland%%",
    "addressCountry": "%%BUREAU_JSON:anschrift.land%%"}}]}
</script>
"""

HOURS = ("<p>%%BUREAU:sprechzeiten.text.regulaer%% %%BUREAU:sprechzeiten.text.termin%%</p>\n"
         "<p>%%BUREAU:sprechzeiten.leicht.tage%% %%BUREAU:sprechzeiten.leicht.zeit%% "
         "%%BUREAU:sprechzeiten.leicht.termin%% %%BUREAU:sprechzeiten.leicht.hinweis%%</p>\n")


def page(title: str, head: str = "", body: str = "") -> str:
    return ('<!DOCTYPE html>\n<html lang="de">\n<head>\n<!-- @include head -->\n'
            f"<title>{title}</title>\n{head}</head>\n<body>\n<!-- @include skip -->\n<!-- @include rail -->\n"
            f'<main id="inhalt">\n<h1>{title}</h1>\n{body}<!-- @include foot -->\n</main>\n'
            "<!-- @include callbar -->\n</body>\n</html>\n")


def office() -> dict:
    return copy.deepcopy(OFFICE)


def write_site(root: Path) -> None:
    """Schreibt src/ und public/ der Test-Website unter root."""
    (root / "src/pages").mkdir(parents=True)
    (root / "src/partials").mkdir()
    (root / "public").mkdir()
    (root / "src/seiten.json").write_text(json.dumps(CATALOG, indent=2), encoding="utf-8")
    (root / "src/bureauangaben.json").write_text(json.dumps(OFFICE, ensure_ascii=False, indent=2), encoding="utf-8")
    (root / "src/style.css").write_text("body { margin: 0; }\n", encoding="utf-8")
    for name, text in PARTIALS.items():
        (root / "src/partials" / f"{name}.html").write_text(text, encoding="utf-8")
    (root / "src/pages/index.html").write_text(page("Start", JSON_LD, HOURS), encoding="utf-8")
    (root / "src/pages/zweite.html").write_text(page("Zweite"), encoding="utf-8")
    (root / "src/pages/404.html").write_text(page("Nicht gefunden"), encoding="utf-8")
    (root / "public/CNAME").write_text("example.org\n", encoding="utf-8")
    (root / "public/robots.txt").write_text("User-agent: *\nAllow: /\n", encoding="utf-8")
    (root / "public/favicon.ico").write_bytes(b"\x00\x00\x01\x00")
