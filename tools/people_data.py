"""Prüft die Angaben der betreuenden Personen und erzeugt ihre Darstellungen.

Die Werte stehen nur in src/betreuende.json (R-ANGABEN-1). Seiten beziehen sie
über %%BETREUENDE:…%%; Büroangaben in den erzeugten Blöcken bleiben
%%BUREAU:…%%-Platzhalter und werden danach wie überall aufgelöst.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

from bureau_data import email_ok, node_field, office_node, phone_ok, single_line, vcard_bytes, vcard_text
from site_config import load_json, read_source

SOURCE = "betreuende.json"
KEYS = {"kennung", "name", "beruf", "registrierung", "haftpflicht", "telefon", "email", "anschrift"}
# Die Personen stehen als Abschnitte auf dieser Seite; die Kennung ist ihre Sprungmarke.
PAGE = "buero.html"
PEOPLE_TOKEN = re.compile(r"%%BETREUENDE:([a-z]+)%%")
PEOPLE_JSON = '"%%BETREUENDE_JSON:personen%%"'


def person_url(person: dict, base: str) -> str:
    return f"{base}{PAGE}#{person['kennung']}"


def vcard_name(person: dict) -> str:
    return f"{person['kennung']}.vcf"


def text_ok(value: object) -> bool:
    return (isinstance(value, str) and bool(value.strip()) and value == value.strip()
            and single_line(value) and "%%" not in value)


def load_people(root: Path) -> list[dict]:
    path = root / "src" / SOURCE
    data = load_json(path)
    if not isinstance(data, dict) or set(data) != {"personen"} or not isinstance(data["personen"], list):
        raise ValueError(f"{SOURCE}: erwartet eine Liste personen")
    people = data["personen"]
    for person in people:
        if not isinstance(person, dict) or set(person) != KEYS:
            raise ValueError(f"{SOURCE}: jeder Eintrag braucht genau {', '.join(sorted(KEYS))}")
        label = person.get("kennung")
        if not isinstance(label, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", label):
            raise ValueError(f"{SOURCE}: ungültige kennung {label!r}")
        for key in ("name", "beruf", "registrierung", "haftpflicht"):
            if not text_ok(person[key]):
                raise ValueError(f"{SOURCE}: {label}: {key}: erwartet nicht leeren, einzeiligen Text")
        phone = person["telefon"]
        if phone is not None:
            if (not isinstance(phone, dict) or set(phone) != {"e164", "sichtbar"}
                    or not all(text_ok(value) for value in phone.values()) or not phone_ok(phone)):
                raise ValueError(f"{SOURCE}: {label}: telefon: erwartet null oder e164 und sichtbar mit denselben Ziffern")
        if person["email"] is not None and not (text_ok(person["email"]) and email_ok(person["email"])):
            raise ValueError(f"{SOURCE}: {label}: email: erwartet null oder eine gültige Adresse")
        address = person["anschrift"]
        if address is not None:
            if (not isinstance(address, dict) or set(address) != {"strasse", "plz", "ort"}
                    or not all(text_ok(value) for value in address.values())
                    or not re.fullmatch(r"\d{5}", address["plz"])):
                raise ValueError(f"{SOURCE}: {label}: anschrift: erwartet null oder strasse, plz (fünfstellig), ort")
    labels = [person["kennung"] for person in people]
    if len(labels) != len(set(labels)):
        raise ValueError(f"{SOURCE}: doppelte kennung")
    for person in people:
        person["vorstellung"] = read_source(root / "src/betreuende" / f"{person['kennung']}.html").decode("utf-8")
        if "%%" in person["vorstellung"] or "@include" in person["vorstellung"]:
            raise ValueError(f"src/betreuende/{person['kennung']}.html: Platzhalter und Includes gehören in die Vorlage")
    return people


def html(value: str) -> str:
    return escape(value, quote=True)


def address_lines(person: dict) -> str:
    address = person["anschrift"]
    if address is None:
        return "%%BUREAU:anschrift.strasse%%<br>\n          %%BUREAU:anschrift.plz%% %%BUREAU:anschrift.ort%%"
    return f"{html(address['strasse'])}<br>\n          {html(address['plz'])} {html(address['ort'])}"


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


def initials(name: str) -> str:
    words = name.split()
    return (words[0][0] + (words[-1][0] if len(words) > 1 else "")).upper()


def section(person: dict) -> str:
    """Eine Karte je Person; ohne eigene Nummer oder Adresse gilt der Kontakt des Büros."""
    label = person["kennung"]
    lines = [f'      <article class="person" aria-labelledby="{label}">',
             '        <header class="person-kopf">',
             f'          <span class="monogramm" aria-hidden="true">{html(initials(person["name"]))}</span>',
             "          <div>",
             f'            <h3 id="{label}">{html(person["name"])}</h3>',
             f'            <p class="rolle">{html(person["beruf"])}</p>',
             "          </div>",
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
    """Blöcke über alle Personen: Übersicht, Impressum, JSON-LD."""
    def sections() -> str:
        return '    <div class="team">\n' + "\n".join(section(person) for person in people) + "\n    </div>"

    def providers() -> str:
        blocks = []
        for person in people:
            blocks.append(f"""      <div>
        <h3>{html(person["name"])}</h3>
        <p>
          {html(person["beruf"])}<br>
          {html(person["registrierung"])}<br>
          {address_lines(person)}<br>
          Deutschland
        </p>
      </div>""")
        return '    <div class="anbieter">\n' + "\n".join(blocks) + "\n    </div>"

    def insurance() -> str:
        return "\n".join(f"      <strong>{html(person['name'])}:</strong> {html(person['haftpflicht'])}<br>"
                         for person in people)

    blocks = {"personen": sections, "anbieter": providers, "haftpflicht": insurance}

    def replace(match: re.Match) -> str:
        if match[1] not in blocks:
            raise ValueError(f"{name}: unbekannter Personenplatzhalter {match[0]}")
        return blocks[match[1]]()

    result = PEOPLE_TOKEN.sub(replace, source)
    if PEOPLE_JSON in result:
        nodes = [{"@type": "Person", "name": person["name"], "jobTitle": person["beruf"],
                  "url": person_url(person, base)} for person in people]
        # JSON-Escaping und Schutz vor einem eingeschleusten </script>.
        value = json.dumps(nodes, ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
        result = result.replace(PEOPLE_JSON, value)
    if "%%BETREUENDE" in result:
        raise ValueError(f"{name}: ungültiger Personenplatzhalter")
    return result


def person_vcard(person: dict, index: str, office: dict, base: str) -> bytes:
    """R-ANGABEN-6: persönliche Visitenkarte; ohne eigene Angabe gilt die des Büros."""
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
