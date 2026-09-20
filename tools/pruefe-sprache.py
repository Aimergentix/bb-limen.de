#!/usr/bin/env python3
"""Misst Satzlaengen im eigentlichen Fliesstext der Seiten.

Der Parser betrachtet nur ``main``. Navigation, Kontaktlisten, Ortslisten,
Ueberschriften und Beschriftungen bleiben getrennt vom Fliesstext. Ein ``br``
ist nur ein Layoutumbruch und beendet keinen Satz.

Fuer die allgemein verstaendlichen Inhaltsseiten gilt das redaktionelle Ziel:
im Mittel hoechstens 15 Woerter und kein Satz ueber 25 Woerter. Fachseite,
Pflichttexte und Leichte Sprache werden separat ausgewiesen, aber nicht an
diesem A2/B1-Ziel gemessen. Die Statistik ersetzt weder eine redaktionelle
Pruefung noch die Pruefung Leichter Sprache durch die vorgesehene Zielgruppe.

    ./pruefe-sprache.py               alle Seiten
    ./pruefe-sprache.py index.html    eine Seite, mit den langen Saetzen
"""

from __future__ import annotations

import glob
import re
import sys
from html.parser import HTMLParser
from pathlib import Path


ZIEL_MITTEL = 15.0
ZIEL_MAX = 25

EINFACHE_SPRACHE = {
    "index.html",
    "betreuung.html",
    "aufgaben.html",
    "vorsorge.html",
}
PROFILE = {
    "fachkreise.html": "Fachsprache, nur Statistik",
    "impressum.html": "Pflichttext, nur Statistik",
    "datenschutz.html": "Pflichttext, nur Statistik",
    "leichte-sprache.html": "Leichte Sprache, Zielgruppenpruefung bleibt noetig",
    "404.html": "Fehlerseite, nur Statistik",
}

ABKUERZUNG = re.compile(
    r"(?<![\wäöüßÄÖÜ])"
    r"(?:z\.\s?B|u\.\s?a|Abs|Nr|Art|ff|lit|bzw|ca|vgl|Dr|S|Tel)\.",
    re.IGNORECASE,
)
SATZGRENZE = re.compile(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„»§\d])")
WORT = re.compile(r"[0-9A-Za-zÄÖÜäöüß]+(?:[-‑][0-9A-Za-zÄÖÜäöüß]+)*")

BLOCK_TAGS = {"p", "li", "dd", "blockquote"}
LABEL_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "dt", "figcaption"}
SKIP_TAGS = {"nav", "footer", "script", "style", "svg"}
SKIP_CLASSES = {"contact", "rail-contact", "orte", "zitat"}
LABEL_CLASSES = {"titel", "quelle", "wer", "gramm"}
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class MainTextParser(HTMLParser):
    """Sammelt Fliesstextbloecke innerhalb des main-Elements."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.in_main = False
        self.skip_depth = 0
        self.label_depth = 0
        self.block_buffers: list[list[str]] = []
        self.stack: list[tuple[str, bool, bool, bool]] = []
        self.bloecke: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag == "main" and not self.in_main:
            self.in_main = True
            return
        if not self.in_main:
            return
        if tag == "br":
            if self.block_buffers and not self.skip_depth and not self.label_depth:
                self.block_buffers[-1].append(" ")
            return

        klassen = set()
        for name, value in attrs:
            if name == "class" and value:
                klassen.update(value.split())

        skip_started = tag in SKIP_TAGS or bool(klassen & SKIP_CLASSES)
        label_started = tag in LABEL_TAGS or bool(klassen & LABEL_CLASSES)
        if skip_started:
            self.skip_depth += 1
        if label_started:
            self.label_depth += 1

        block_started = False
        if tag in BLOCK_TAGS and not self.skip_depth and not self.label_depth:
            self.block_buffers.append([])
            block_started = True

        if tag not in VOID_TAGS:
            self.stack.append((tag, skip_started, label_started, block_started))

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag == "main" and self.in_main:
            if self.block_buffers:
                raise ValueError("main endet innerhalb eines offenen Textblocks")
            self.in_main = False
            return
        if not self.in_main or tag in VOID_TAGS:
            return

        if not self.stack:
            return

        start_tag, skip_started, label_started, block_started = self.stack.pop()
        if start_tag != tag:
            # Die Produktionsseiten werden gesondert als HTML geprueft. Hier
            # vermeiden wir bei fehlerhaftem Eingabe-HTML falsche Statistiken.
            raise ValueError(f"nicht passend geschlossene HTML-Tags: <{start_tag}> und </{tag}>")

        if block_started:
            self._speichere_block(self.block_buffers.pop())
        if label_started:
            self.label_depth -= 1
        if skip_started:
            self.skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self.in_main and self.block_buffers and not self.skip_depth and not self.label_depth:
            self.block_buffers[-1].append(data)

    def _speichere_block(self, buffer: list[str]) -> None:
        if not buffer:
            return
        text = re.sub(r"\s+", " ", "".join(buffer)).strip()
        if text:
            self.bloecke.append(text)


def fliesstext(datei: str | Path) -> list[str]:
    parser = MainTextParser()
    parser.feed(Path(datei).read_text(encoding="utf-8"))
    parser.close()
    if parser.in_main:
        raise ValueError(f"{datei}: main wurde nicht geschlossen")
    if not parser.bloecke:
        raise ValueError(f"{datei}: kein Fliesstext in main gefunden")
    return parser.bloecke


def saetze(bloecke: list[str] | str) -> list[str]:
    if isinstance(bloecke, str):
        bloecke = [bloecke]
    ergebnis: list[str] = []
    for block in bloecke:
        geschuetzt = ABKUERZUNG.sub(lambda treffer: treffer.group(0).replace(".", "<P>"), block)
        for satz in SATZGRENZE.split(geschuetzt):
            satz = satz.replace("<P>", ".").strip()
            if len(WORT.findall(satz)) > 2:
                ergebnis.append(satz)
    return ergebnis


def pruefe(datei: str, zeige: bool = False) -> bool:
    ss = saetze(fliesstext(datei))
    laengen = [len(WORT.findall(satz)) for satz in ss]
    mittel = sum(laengen) / len(laengen)
    groesste = max(laengen)
    lang = sorted(((laenge, satz) for laenge, satz in zip(laengen, ss) if laenge > ZIEL_MAX), reverse=True)

    name = Path(datei).name
    hat_ziel = name in EINFACHE_SPRACHE
    bestanden = not hat_ziel or (mittel <= ZIEL_MITTEL and groesste <= ZIEL_MAX)
    marke = "ok " if hat_ziel and bestanden else "!! " if hat_ziel else "-- "
    profil = "A2/B1-Ziel" if hat_ziel else PROFILE.get(name, "nur Statistik")

    print(
        f"  {marke}{datei:22s} {len(ss):3d} Sätze · Mittel {mittel:5.1f}"
        f" · längster {groesste:3d} · über {ZIEL_MAX}: {len(lang)} · {profil}"
    )
    if zeige:
        for laenge, satz in lang:
            kuerzung = "…" if len(satz) > 155 else ""
            print(f"        {laenge:3d}  {satz[:155]}{kuerzung}")
    return bestanden


def main(argumente: list[str]) -> int:
    ziele = argumente or sorted(glob.glob("*.html"))
    print(f"Redaktionelles A2/B1-Ziel: Mittel ≤ {ZIEL_MITTEL:.0f} Wörter, kein Satz > {ZIEL_MAX}\n")
    try:
        ergebnisse = [pruefe(datei, zeige=bool(argumente)) for datei in ziele]
    except (OSError, ValueError) as fehler:
        print(f"FEHLER: {fehler}", file=sys.stderr)
        return 2
    return 0 if all(ergebnisse) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
