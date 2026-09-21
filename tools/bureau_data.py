"""Prüft Büroangaben und erzeugt ihre festgelegten Sprachfassungen."""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

from site_config import read_source

DAYS = ("Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag")
TOKEN = re.compile(r"%%BUREAU:([a-z0-9_.-]+)%%")
JSON_TOKEN = re.compile(r'"%%BUREAU_JSON:([a-z0-9_.-]+)%%"')
JSON_SCRIPT = re.compile(r'(<script type="application/ld\+json">)(.*?)(</script>)', re.S)


def require_keys(value: object, keys: set[str], field: str) -> None:
    if not isinstance(value, dict) or set(value) != keys:
        raise ValueError(f"bureauangaben.json: {field}: erwartet {', '.join(sorted(keys))}")


def unique_object(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"bureauangaben.json: doppelter Schlüssel {key}")
        result[key] = value
    return result


def load_office(root: Path) -> dict:
    data = json.loads(read_source(root / "src/bureauangaben.json"), object_pairs_hook=unique_object)
    require_keys(data, {"sprechzeiten", "telefon", "email", "anschrift"}, "Wurzel")
    require_keys(data["telefon"], {"e164", "sichtbar"}, "telefon")
    require_keys(data["anschrift"], {"strasse", "plz", "ort", "bundesland", "land"}, "anschrift")
    for field, value in {"email": data["email"], **data["telefon"], **data["anschrift"]}.items():
        if (not isinstance(value, str) or not value.strip() or value != value.strip()
                or any(ord(char) < 32 or ord(char) == 127 for char in value)
                or "%%" in value):
            raise ValueError(f"bureauangaben.json: {field}: erwartet nicht leeren, einzeiligen Text")
    phone = data["telefon"]
    if (not re.fullmatch(r"\+[1-9]\d{1,14}", phone["e164"])
            or not re.fullmatch(r"\+[\d ]+", phone["sichtbar"])
            or phone["sichtbar"].replace(" ", "") != phone["e164"]):
        raise ValueError("bureauangaben.json: technische und sichtbare Telefonnummer widersprechen sich")
    if not re.fullmatch(r"[A-Za-z0-9._+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+", data["email"]):
        raise ValueError("bureauangaben.json: ungültige E-Mail-Adresse")
    if not re.fullmatch(r"\d{5}", data["anschrift"]["plz"]) or data["anschrift"]["land"] != "DE":
        raise ValueError("bureauangaben.json: erwartet deutsche Anschrift mit fünfstelliger PLZ und Land DE")
    hours = data["sprechzeiten"]
    require_keys(hours, {"regulaer", "nach_vereinbarung"}, "sprechzeiten")
    regular = hours["regulaer"]
    require_keys(regular, {"tage", "von", "bis"}, "regulaer")
    for days in (regular["tage"], hours["nach_vereinbarung"]):
        if (not isinstance(days, list) or not days
                or any(not isinstance(day, str) or day not in DAYS for day in days)
                or len(days) != len(set(days))):
            raise ValueError("bureauangaben.json: Tage müssen eindeutige deutsche Wochentage sein")
    if set(regular["tage"]) & set(hours["nach_vereinbarung"]):
        raise ValueError("bureauangaben.json: reguläre Tage und Termintage überschneiden sich")
    for key in ("von", "bis"):
        if not isinstance(regular[key], str) or not re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", regular[key]):
            raise ValueError(f"bureauangaben.json: {key}: erwartet HH:MM")
    if regular["von"] >= regular["bis"]:
        raise ValueError("bureauangaben.json: Beginn muss vor Ende liegen")
    return data


def join_days(days: list[str]) -> str:
    return days[0] if len(days) == 1 else ", ".join(days[:-1]) + " und " + days[-1]


def hour_label(value: str) -> str:
    hour, minute = value.split(":")
    return str(int(hour)) + (f":{minute}" if minute != "00" else "")


def office_values(data: dict) -> dict[str, str]:
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
    values.update({"email": data["email"]})
    for group in ("telefon", "anschrift"):
        values.update({f"{group}.{key}": value for key, value in data[group].items()})
    return values


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
            # JSON-Escaping und Schutz vor einem eingeschleusten </script>.
            return json.dumps(values[token[1]], ensure_ascii=False).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

        body = JSON_TOKEN.sub(replace_json, match[2])
        if "%%BUREAU" in body:
            raise ValueError("JSON-LD benötigt vollständige JSON-Büroplatzhalter")
        json.loads(body)
        return match[1] + body + match[3]

    result = JSON_SCRIPT.sub(replace_script, source)
    result = TOKEN.sub(replace, result)
    if "%%BUREAU" in result:
        raise ValueError("Ungültiger Büroplatzhalter")
    return result


def vcard(index: str) -> bytes:
    """R-ANGABEN-6: Bürovisitenkarte aus dem erzeugten Organization-Knoten."""
    scripts = JSON_SCRIPT.findall(index)
    if len(scripts) != 1:
        raise ValueError("Startseite: genau ein JSON-LD-Block für die Bürovisitenkarte erwartet")
    document = json.loads(scripts[0][1])
    graph = document.get("@graph") if isinstance(document, dict) else None
    if not isinstance(graph, list):
        raise ValueError("Startseite: JSON-LD benötigt @graph")
    offices = [node for node in graph if isinstance(node, dict) and node.get("@type") == "Organization"]
    if len(offices) != 1:
        raise ValueError("Startseite: genau eine Organization für die Bürovisitenkarte erwartet")
    office = offices[0]
    address = office.get("address")
    if not isinstance(address, dict) or address.get("@type") != "PostalAddress":
        raise ValueError("Startseite: PostalAddress fehlt")

    def field(record: dict, key: str) -> str:
        value = record.get(key)
        if not isinstance(value, str) or not value or any(ord(char) < 32 for char in value):
            raise ValueError(f"Startseite: ungültiges vCard-Feld {key}")
        return value

    def text(value: str) -> str:
        return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,")

    name = text(field(office, "name"))
    lines = ["BEGIN:VCARD", "VERSION:3.0", "N:;;;;", f"FN:{name}", f"ORG:{name}",
             "TEL;TYPE=WORK,VOICE:" + text(field(office, "telephone")),
             "EMAIL;TYPE=INTERNET,WORK:" + text(field(office, "email")),
             "ADR;TYPE=WORK:;;" + ";".join(text(field(address, key)) for key in (
                 "streetAddress", "addressLocality", "addressRegion", "postalCode", "addressCountry")),
             "URL:" + field(office, "url"), "END:VCARD"]
    folded = []
    for line in lines:
        part = ""
        for char in line:
            if len((part + char).encode("utf-8")) > 75:
                folded.append(part)
                part = " "
            part += char
        folded.append(part)
    return ("\r\n".join(folded) + "\r\n").encode("utf-8")
