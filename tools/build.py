"""Erzeugt die statische Website aus src/ und public/. Nur Python-Standardbibliothek.

    tools/build.sh                     erzeugt dist/
    tools/build.sh --output VERZ       erzeugt ein neues Verzeichnis (für die Prüfung)

Alle Eingaben werden gelesen und geprüft, bevor die bisherige Ausgabe ersetzt
wird. Geprüft wird nur, was eine Seite technisch zerstören würde — nie, ob eine
Angabe inhaltlich stimmt (R-REDAKTION-3).
"""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import tempfile
import unicodedata
from urllib.parse import urlsplit, urljoin

ROOT = Path(__file__).resolve().parents[1]
PARTIALS = ("head", "skip", "rail", "foot", "callbar")
INCLUDE = re.compile(r"<!-- @include ([a-z-]+) -->\n?")
CURRENT = re.compile(r"%%CUR-([a-z0-9-]+)%%")
OFFICE_TOKEN = re.compile(r"%%BUREAU:([a-z0-9_.-]+)%%")
OFFICE_JSON = re.compile(r'"%%BUREAU_JSON:([a-z0-9_.-]+)%%"')
JSON_SCRIPT = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)
PEOPLE_TOKEN = re.compile(r"%%BETREUENDE:([a-z]+)%%")
PEOPLE_JSON = '"%%BETREUENDE_JSON:personen%%"'
# Die Personen stehen als Abschnitte auf dieser Seite; die Kennung ist ihre Sprungmarke.
PEOPLE_PAGE = "buero.html"
PEOPLE_KEYS = {"kennung", "name", "beruf", "registrierung", "haftpflicht", "telefon", "email", "anschrift", "bild"}
SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DAYS = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")


# ---------------------------------------------------------------- Eingaben

def read_source(path: Path) -> bytes:
    if not path.is_file():
        raise ValueError(f"{path}: Datei fehlt")
    data = path.read_bytes()
    if not data:
        raise ValueError(f"{path}: Datei ist leer")
    return data


def load_json(path: Path) -> object:
    try:
        return json.loads(read_source(path))
    except ValueError as error:
        raise ValueError(f"{path}: {error}") from None


def single_line(value: str) -> bool:
    """Keine Steuerzeichen und keine Zeilen- oder Absatztrenner wie U+2028."""
    return not any(unicodedata.category(char) in ("Cc", "Zl", "Zp") for char in value)


def text_ok(value: object) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and value == value.strip()
            and single_line(value) and "%%" not in value)


def phone_ok(phone: object) -> bool:
    """Sichtbare und technische Nummer müssen dieselben Ziffern haben, sonst wählt tel: falsch."""
    return (isinstance(phone, dict) and set(phone) == {"e164", "sichtbar"}
            and all(text_ok(value) for value in phone.values())
            and bool(re.fullmatch(r"\+[1-9]\d{1,14}", phone["e164"]))
            and phone["sichtbar"].replace(" ", "") == phone["e164"])


def email_ok(value: object) -> bool:
    return text_ok(value) and bool(re.fullmatch(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", value))


def require_keys(value: object, keys: set[str], field: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"{field}: erwartet {', '.join(sorted(keys))}")


def load_catalog(root: Path) -> dict:
    path = root / "src/seiten.json"
    catalog = load_json(path)
    require_keys(catalog, {"pages", "public_files"}, str(path))
    names = []
    for page in catalog["pages"]:
        name = page.get("file") if isinstance(page, dict) else None
        if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*\.html", name):
            raise ValueError(f"{path}: ungültiger Seiteneintrag {page!r}")
        if type(page.get("sitemap")) is not bool:
            raise ValueError(f"{path}: {name}: sitemap muss true oder false sein")
        if page["sitemap"] and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(page.get("lastmod"))):
            raise ValueError(f"{path}: {name}: lastmod muss YYYY-MM-DD sein")
        names.append(name)
    if len(names) != len(set(names)) or not {"index.html", "404.html"} <= set(names):
        raise ValueError(f"{path}: doppelte Seiten oder fehlende index.html/404.html")
    public = catalog["public_files"]
    if (not isinstance(public, list) or "CNAME" not in public
            or not all(isinstance(name, str) and re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*", name) for name in public)):
        raise ValueError(f"{path}: public_files muss einfache Dateinamen und CNAME enthalten")
    return catalog


def base_url(root: Path) -> str:
    return "https://" + read_source(root / "public/CNAME").decode("utf-8").strip() + "/"


def load_office(root: Path) -> dict:
    """src/bureauangaben.json (R-ANGABEN-1)."""
    name = "bureauangaben.json"
    data = load_json(root / "src" / name)
    require_keys(data, {"ug", "sprechzeiten", "telefon", "email", "email_datenschutz", "anschrift", "postanschrift"}, name)
    require_keys(data["ug"], {"firma", "registergericht", "registernummer", "geschaeftsfuehrung"}, f"{name}: ug")
    require_keys(data["anschrift"], {"strasse", "plz", "ort", "bundesland", "land"}, f"{name}: anschrift")
    require_keys(data["postanschrift"], {"postfach", "plz", "ort", "bundesland", "land"}, f"{name}: postanschrift")
    for group in ("ug", "anschrift", "postanschrift"):
        for key, value in data[group].items():
            if not text_ok(value):
                raise ValueError(f"{name}: {group}.{key}: erwartet nicht leeren, einzeiligen Text")
    if not phone_ok(data["telefon"]):
        raise ValueError(f"{name}: telefon: erwartet e164 und sichtbar mit denselben Ziffern")
    if not (email_ok(data["email"]) and email_ok(data["email_datenschutz"])):
        raise ValueError(f"{name}: ungültige E-Mail-Adresse")
    hours = data["sprechzeiten"]
    require_keys(hours, {"regulaer", "nach_vereinbarung"}, f"{name}: sprechzeiten")
    require_keys(hours["regulaer"], {"tage", "von", "bis"}, f"{name}: regulaer")
    for days in (hours["regulaer"]["tage"], hours["nach_vereinbarung"]):
        if not isinstance(days, list) or not days or any(day not in DAYS for day in days):
            raise ValueError(f"{name}: Tage müssen deutsche Wochentage sein")
    for key in ("von", "bis"):
        if not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", str(hours["regulaer"][key])):
            raise ValueError(f"{name}: {key}: erwartet HH:MM")
    return data


def load_people(root: Path) -> list[dict]:
    """src/betreuende.json und je Person der Vorstellungstext (R-ANGABEN-1)."""
    name = "betreuende.json"
    data = load_json(root / "src" / name)
    require_keys(data, {"personen"}, name)
    people = data["personen"]
    for person in people:
        require_keys(person, PEOPLE_KEYS, f"{name}: Eintrag")
        label = person["kennung"]
        if not isinstance(label, str) or not SLUG.fullmatch(label):
            raise ValueError(f"{name}: ungültige kennung {label!r}")
        for key in ("name", "beruf", "registrierung", "haftpflicht"):
            if not text_ok(person[key]):
                raise ValueError(f"{name}: {label}: {key}: erwartet nicht leeren, einzeiligen Text")
        if person["telefon"] is not None and not phone_ok(person["telefon"]):
            raise ValueError(f"{name}: {label}: telefon: erwartet null oder e164 und sichtbar mit denselben Ziffern")
        if person["email"] is not None and not email_ok(person["email"]):
            raise ValueError(f"{name}: {label}: email: erwartet null oder eine gültige Adresse")
        photo = person["bild"]
        if photo is not None and not (isinstance(photo, str) and re.fullmatch(re.escape(label) + r"\.(?:jpg|webp|png)", photo)):
            raise ValueError(f"{name}: {label}: bild: erwartet null oder {label}.jpg, .webp oder .png")
        person["vorstellung"] = read_source(root / "src/betreuende" / f"{label}.html").decode("utf-8")
        if "%%" in person["vorstellung"] or "@include" in person["vorstellung"]:
            raise ValueError(f"src/betreuende/{label}.html: Platzhalter und Includes gehören in die Vorlage")
    labels = [person["kennung"] for person in people]
    if len(labels) != len(set(labels)):
        raise ValueError(f"{name}: doppelte kennung")
    return people


# ---------------------------------------------------------------- Büroangaben

def join_days(days: list[str]) -> str:
    return days[0] if len(days) == 1 else ", ".join(days[:-1]) + " und " + days[-1]


def hour_label(value: str) -> str:
    hour, minute = value.split(":")
    return str(int(hour)) + (f":{minute}" if minute != "00" else "")


def office_values(data: dict) -> dict[str, str]:
    """Alle %%BUREAU:…%%-Werte, die Sprechzeiten in ihren festgelegten Sprachfassungen."""
    hours = data["sprechzeiten"]
    regular = hours["regulaer"]
    days = regular["tage"]
    appointments = hours["nach_vereinbarung"]
    start, end = (hour_label(regular[key]) for key in ("von", "bis"))
    indices = [DAYS.index(day) for day in days]
    consecutive = len(days) > 2 and all(b == a + 1 for a, b in zip(indices, indices[1:]))
    short_days = days[0][:2] + "–" + days[-1][:2] if consecutive else ", ".join(day[:2] for day in days)
    appointment_text = join_days(["am " + day for day in appointments])
    values = {
        "sprechzeiten.kurz.regulaer": f"{short_days} {start}–{end} Uhr",
        "sprechzeiten.kurz.termin": ", ".join(day[:2] for day in appointments) + " nach Vereinbarung",
        "sprechzeiten.text.regulaer": f"{join_days(days)} von {start} bis {end} Uhr.",
        "sprechzeiten.text.termin": f"{join_days(appointments)} nach Vereinbarung.",
        "sprechzeiten.leicht.tage": f"Am {join_days(days)}.",
        "sprechzeiten.leicht.zeit": f"Von {start} Uhr bis {end} Uhr.",
        "sprechzeiten.leicht.termin": "A" + appointment_text[1:] + " geht es auch.",
        "sprechzeiten.leicht.hinweis": "Aber nur mit einem Termin.",
    }
    values.update({key: data[key] for key in ("email", "email_datenschutz")})
    for group in ("ug", "telefon", "anschrift", "postanschrift"):
        values.update({f"{group}.{key}": value for key, value in data[group].items()})
    return values


def json_value(value: object) -> str:
    """JSON-Escaping und Schutz vor einem eingeschleusten </script>."""
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_office(source: str, data: dict) -> str:
    values = office_values(data)

    def replace(match: re.Match) -> str:
        if match[1] not in values:
            raise ValueError(f"Unbekannter Büroplatzhalter: {match[0]}")
        return escape(values[match[1]], quote=True)

    def replace_script(match: re.Match) -> str:
        def replace_json(token: re.Match) -> str:
            if token[1] not in values or token[1].startswith("sprechzeiten."):
                raise ValueError(f"Unbekannter JSON-LD-Büroplatzhalter: {token[0]}")
            return json_value(values[token[1]])

        body = OFFICE_JSON.sub(replace_json, match[2])
        if "%%BUREAU" in body:
            raise ValueError("JSON-LD benötigt vollständige JSON-Büroplatzhalter")
        json.loads(body)
        return match[1] + body + match[3]

    result = OFFICE_TOKEN.sub(replace, JSON_SCRIPT.sub(replace_script, source))
    if "%%BUREAU" in result:
        raise ValueError("Ungültiger Büroplatzhalter")
    return result


# ---------------------------------------------------------------- Betreuende Personen

def html(value: str) -> str:
    return escape(value, quote=True)


def person_url(person: dict, base: str) -> str:
    return f"{base}{PEOPLE_PAGE}#{person['kennung']}"


def source_files(person: dict) -> set[str]:
    """Dateien der Person in src/betreuende/: Vorstellung und gegebenenfalls Foto."""
    return {f"{person['kennung']}.html", *filter(None, [person["bild"]])}


def vcard_name(person: dict) -> str:
    return f"{person['kennung']}.vcf"


# Dasselbe Blatt wie Signet und .zierblatt; hier als Trenner in der Karte.
LEAF = ('<svg class="zierblatt" viewBox="0 0 24 26" aria-hidden="true" focusable="false" fill="none" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        '<path d="M12 1.2c4.6 4.7 7.4 9 7.4 13.1 0 5-3.3 8.9-7.4 8.9s-7.4-3.9-7.4-8.9C4.6 10.2 7.4 5.9 12 1.2Z"/>'
        '<path d="M12 3.6v21.2"/><path d="M12 9.4 7.3 12.6M12 9.4l4.7 3.2M12 14.6l-4.5 3.3M12 14.6l4.5 3.3"/></svg>')
# Karteikarte für den Verweis auf die Visitenkarte.
CARD = ('<svg class="symbol" viewBox="0 0 24 24" aria-hidden="true" focusable="false" fill="none" '
        'stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">'
        '<rect x="2.5" y="5" width="19" height="14" rx="2"/><circle cx="8.5" cy="11" r="2.2"/>'
        '<path d="M5.2 16.2c.7-1.6 1.9-2.4 3.3-2.4s2.6.8 3.3 2.4M14.5 10h4M14.5 13.5h4"/></svg>')


def portrait(person: dict) -> str:
    """Foto der Person; solange keines vorliegt, ein gezeichneter Platzhalter.

    Der Platzhalter zeigt eine Gestalt unter einem Türbogen über der
    Schwelle — das Motiv des Namens. Seine Farben kommen über Klassen aus
    PALETTE (R-FARBE-1) und folgen damit auch der Dunkeldarstellung.
    """
    if person["bild"] is not None:
        return (f'<img src="{person["bild"]}" alt="Porträt von {html(person["name"])}" '
                'width="800" height="600" loading="lazy" decoding="async">')
    return ('<svg class="platzhalter" viewBox="0 0 400 300" preserveAspectRatio="xMidYMid slice" role="img" '
            f'aria-label="Platzhalter, noch kein Porträt von {html(person["name"])}">'
            '<rect class="grund" width="400" height="300"/>'
            '<path class="bogen" d="M104 300V158a96 96 0 0 1 192 0v142"/>'
            '<path class="bogen" d="M122 300V160a78 78 0 0 1 156 0v140"/>'
            '<circle class="figur" cx="200" cy="146" r="40"/>'
            '<path class="figur" d="M122 300c3-58 37-94 78-94s75 36 78 94Z"/>'
            '<path class="schwelle" d="M70 299h260"/></svg>')


def section(person: dict) -> str:
    """Eine Karte je Person; ohne eigene Nummer oder Adresse gilt der Kontakt des Büros."""
    label = person["kennung"]
    lines = [f'      <article class="person" aria-labelledby="{label}">',
             f'        <figure class="portrait">{portrait(person)}</figure>',
             '        <header class="person-kopf">',
             f'          <h3 id="{label}">{html(person["name"])}</h3>',
             f'          <p class="rolle">{html(person["beruf"])}</p>',
             "        </header>",
             f'        <p class="stand"><span>Stand</span> {html(person["registrierung"])}</p>',
             f'        <div class="ornament" aria-hidden="true">{LEAF}</div>',
             '        <div class="vorstellung">',
             person["vorstellung"].rstrip("\n"),
             "        </div>",
             '        <footer class="person-fuss">']
    if person["telefon"] is not None:
        lines.append(f'          <p>Telefon direkt: <a href="tel:{html(person["telefon"]["e164"])}">{html(person["telefon"]["sichtbar"])}</a></p>')
    if person["email"] is not None:
        lines.append(f'          <p>E-Mail direkt: <a href="mailto:{html(person["email"])}">{html(person["email"])}</a></p>')
    lines += [f'          <p><a class="karte" href="{vcard_name(person)}" download>{CARD}Kontaktdaten von {html(person["name"])} speichern (Visitenkarte)</a></p>',
              "        </footer>",
              "      </article>"]
    return "\n".join(lines)


def render_people(source: str, people: list[dict], name: str, base: str) -> str:
    """%%BETREUENDE:personen%% (Abschnitte in buero.html) und das JSON-LD der Personen."""
    def replace(match: re.Match) -> str:
        if match[1] != "personen":
            raise ValueError(f"{name}: unbekannter Personenplatzhalter {match[0]}")
        return '    <div class="team">\n' + "\n".join(section(person) for person in people) + "\n    </div>"

    result = PEOPLE_TOKEN.sub(replace, source)
    if PEOPLE_JSON in result:
        nodes = [{"@type": "Person", "name": person["name"], "jobTitle": person["beruf"],
                  "url": person_url(person, base)} for person in people]
        result = result.replace(PEOPLE_JSON, json_value(nodes))
    if "%%BETREUENDE" in result:
        raise ValueError(f"{name}: ungültiger Personenplatzhalter")
    return result


# ---------------------------------------------------------------- Visitenkarten (R-ANGABEN-6)

def vcard_text(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")


def vcard_bytes(lines: list[str]) -> bytes:
    """UTF-8, CRLF und Zeilenfaltung nach 75 Bytes."""
    folded = []
    for line in ["BEGIN:VCARD", "VERSION:3.0", *lines, "END:VCARD"]:
        part = ""
        for char in line:
            if len((part + char).encode("utf-8")) > 75:
                folded.append(part)
                part = " "
            part += char
        folded.append(part)
    return ("\r\n".join(folded) + "\r\n").encode("utf-8")


def office_node(index: str) -> dict:
    """Der erzeugte Organization-Knoten der Startseite."""
    try:
        graph = json.loads(JSON_SCRIPT.search(index)[2])["@graph"]
        (office,) = [node for node in graph if node.get("@type") == "Organization"]
    except (AttributeError, TypeError, KeyError, ValueError):
        raise ValueError("Startseite: JSON-LD mit genau einer Organization in @graph erwartet") from None
    return office


def node_field(record: dict, key: str) -> str:
    value = record.get(key)
    if not isinstance(value, str) or not value or not single_line(value):
        raise ValueError(f"Startseite: ungültiges vCard-Feld {key}")
    return value


def office_vcard(index: str) -> bytes:
    """Bürovisitenkarte aus dem erzeugten Organization-Knoten."""
    office = office_node(index)
    address = office.get("address")
    if not isinstance(address, dict) or address.get("@type") != "PostalAddress":
        raise ValueError("Startseite: PostalAddress fehlt")
    name = vcard_text(node_field(office, "name"))
    return vcard_bytes([
        "N:;;;;", f"FN:{name}", f"ORG:{name}",
        "TEL;TYPE=WORK,VOICE:" + vcard_text(node_field(office, "telephone")),
        "EMAIL;TYPE=INTERNET,WORK:" + vcard_text(node_field(office, "email")),
        # Postfach als Straßenzeile, weil viele Programme das eigene Postfachfeld nicht anzeigen.
        "ADR;TYPE=WORK:;;" + ";".join(vcard_text(value) for value in (
            "Postfach " + node_field(address, "postOfficeBoxNumber"),
            *(node_field(address, key) for key in (
                "addressLocality", "addressRegion", "postalCode", "addressCountry")))),
        "URL:" + node_field(office, "url")])


def person_vcard(person: dict, index: str, office: dict, base: str) -> bytes:
    """Persönliche Visitenkarte; ohne eigene Angabe gilt die des Büros."""
    organization = vcard_text(node_field(office_node(index), "name"))
    lines = ["N:;;;;", "FN:" + vcard_text(person["name"]), f"ORG:{organization}",
             "TITLE:" + vcard_text(person["beruf"])]
    if person["telefon"] is not None:
        lines.append("TEL;TYPE=WORK,VOICE,PREF:" + vcard_text(person["telefon"]["e164"]))
    lines.append("TEL;TYPE=WORK,VOICE:" + vcard_text(office["telefon"]["e164"]))
    lines.append("EMAIL;TYPE=INTERNET,WORK:" + vcard_text(person["email"] or office["email"]))
    post = office["postanschrift"]
    lines.append("ADR;TYPE=WORK:;;" + ";".join(vcard_text(value) for value in (
        "Postfach " + post["postfach"], post["ort"], post["bundesland"], post["plz"], post["land"])))
    lines.append("URL:" + person_url(person, base))
    return vcard_bytes(lines)


# ---------------------------------------------------------------- Seiten

def error_page_links(source: str) -> str:
    """Dateiziele der 404-Seite bleiben auch unter tiefen Fehleradressen gültig.

    Ein base-Element würde auch den Sprunglink auf die Startseite umlenken.
    Deshalb werden nur relative Dateiziele in HTML-Tags absolut zur Domain.
    """
    # HTMLParser zählt Zeilen nur an \n. str.splitlines trennt auch an \r,
    # \x85 oder U+2028 und verschöbe dann jede folgende Ersetzung.
    offsets = [0]
    for line in source.split("\n"):
        offsets.append(offsets[-1] + len(line) + 1)
    replacements = []

    def replace(match: re.Match) -> str:
        value = match[3]
        url = urlsplit(value)
        if url.scheme or url.netloc or not url.path or value.startswith("/"):
            return match[0]
        return match[1] + match[2] + urljoin("/", value) + match[2]

    class Links(HTMLParser):
        def handle_starttag(self, tag, attrs):
            raw = self.get_starttag_text()
            updated = re.sub(r'''(\b(?:href|src)\s*=\s*)(["'])(.*?)\2''', replace, raw)
            if raw != updated:
                line, column = self.getpos()
                start = offsets[line - 1] + column
                if source[start:start + len(raw)] != raw:
                    raise ValueError(f"404.html:{line}: Verweis nicht eindeutig zu verankern")
                replacements.append((start, start + len(raw), updated))

    parser = Links(convert_charrefs=False)
    parser.feed(source)
    parser.close()
    for start, end, updated in reversed(replacements):
        source = source[:start] + updated + source[end:]
    return source


def sitemap(pages: list[dict], base: str) -> bytes:
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for page in pages:
        if page["sitemap"]:
            url = base + ("" if page["file"] == "index.html" else page["file"])
            lines.extend(["  <url>", f"    <loc>{url}</loc>",
                          f"    <lastmod>{page['lastmod']}</lastmod>", "  </url>"])
    return ("\n".join([*lines, "</urlset>"]) + "\n").encode("utf-8")


def assemble(path: Path, source: str, partials: dict[str, str]) -> str:
    """Setzt die Bausteine zeilenweise und in fester Reihenfolge ein."""
    output = []
    seen = []
    for number, line in enumerate(source.splitlines(keepends=True), 1):
        match = INCLUDE.fullmatch(line)
        if match:
            name = match[1]
            if len(seen) >= len(PARTIALS) or name != PARTIALS[len(seen)]:
                raise ValueError(f"{path}:{number}: unbekanntes, doppeltes oder falsch angeordnetes Include {name}")
            seen.append(name)
            output.append(f"<!-- #{name} -->\n{partials[name]}<!-- /#{name} -->\n")
        else:
            if "@include" in line:
                raise ValueError(f"{path}:{number}: Include muss allein auf der Zeile stehen")
            output.append(line)
    if tuple(seen) != PARTIALS:
        raise ValueError(f"{path}: fehlende Includes, erwartet {', '.join(PARTIALS)}")
    return "".join(output)


def render(root: Path = ROOT) -> dict[str, bytes]:
    catalog = load_catalog(root)
    office = load_office(root)
    people = load_people(root)
    pages = catalog["pages"]
    names = {page["file"] for page in pages}
    # R-QUELLE-3: Jede Datei hat eine eingetragene Rolle; was nicht eingetragen ist, fällt auf.
    for directory, expected in (
        (root / "src/pages", names),
        (root / "src/partials", {f"{name}.html" for name in PARTIALS}),
        (root / "src/betreuende", set().union(*map(source_files, people))),
        (root / "public", set(catalog["public_files"])),
    ):
        actual = {path.name for path in directory.iterdir()} if directory.is_dir() else set()
        if actual != expected:
            raise ValueError(f"{directory}: fehlt {sorted(expected - actual)}, unerwartet {sorted(actual - expected)}")
    partials = {name: read_source(root / "src/partials" / f"{name}.html").decode("utf-8") for name in PARTIALS}
    base = base_url(root)
    result = {}
    for page in pages:
        path = root / "src/pages" / page["file"]
        text = assemble(path, read_source(path).decode("utf-8"), partials)
        for match in CURRENT.finditer(text):
            if match[1] + ".html" not in names:
                raise ValueError(f"{path}: unbekanntes Navigationsziel {match[1]}")
        text = CURRENT.sub(lambda match: ' aria-current="page"' if match[1] + ".html" == page["file"] else "", text)
        text = render_people(text, people, str(path), base)
        text = render_office(text, office)
        if page["file"] == "404.html":
            text = error_page_links(text)
        result[page["file"]] = text.encode("utf-8")
    result["style.css"] = read_source(root / "src/style.css")
    result["sitemap.xml"] = sitemap(pages, base)
    index = result["index.html"].decode("utf-8")
    result["bb-limen.vcf"] = office_vcard(index)
    for person in people:
        result[vcard_name(person)] = person_vcard(person, index, office, base)
        if person["bild"]:
            result[person["bild"]] = read_source(root / "src/betreuende" / person["bild"])
    for name in catalog["public_files"]:
        result[name] = read_source(root / "public" / name)
    return result


# ---------------------------------------------------------------- Ausgabe

def write_output(files: dict[str, bytes], output: Path, root: Path = ROOT) -> None:
    """Schreibt erst vollständig in ein Arbeitsverzeichnis, dann wird getauscht.

    Ein vorhandenes Verzeichnis wird nur ersetzt, wenn es dist/ ist; so kann
    ein vertipptes --output nie Quellen löschen.
    """
    output = output.resolve()
    if output.exists() and output != (root / "dist").resolve():
        raise ValueError(f"{output}: vorhandenes Verzeichnis außerhalb von dist/ wird nicht ersetzt")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".build.", dir=output.parent) as temp:
        stage = Path(temp) / "neu"
        stage.mkdir()
        for name, data in files.items():
            (stage / name).write_bytes(data)
        old = Path(temp) / "alt"
        if output.exists():
            output.rename(old)
        try:
            stage.rename(output)
        except OSError:
            if old.exists():
                old.rename(output)
            raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, default=ROOT / "dist", help="Ausgabe-Verzeichnis (Standard: dist/)")
    args = parser.parse_args()
    try:
        files = render()
        write_output(files, args.output)
    except (OSError, ValueError) as error:
        print(f"FEHLER: {error}", file=sys.stderr)
        return 1
    print(f"Erzeugt: {len(files)} Dateien in {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
