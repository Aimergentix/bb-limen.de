#!/usr/bin/env python3
"""Vergleicht zwei mit tools/ansicht.sh erzeugte Bilderordner.

    tools/vergleiche.py <alt> <neu> [<diffordner>]

Gibt je Seite den Anteil geaenderter Bildpunkte aus und schreibt, wenn ein
Diffordner genannt ist, fuer jede Abweichung ein Bild: unveraendertes
blass, Geaendertes rot.

Gedacht fuer zwei Faelle. Lokal: vorher und nachher derselben Aenderung —
sieht man sofort, ob eine Regel mehr getroffen hat als beabsichtigt. In der
CI: der Stand vor und nach dem Push, beide im selben Lauf gerendert. Beides
vergleicht nur Bilder aus derselben Umgebung; Vorlagen von einem anderen
Rechner waeren wegen Schriftglaettung und Chromium-Fassung wertlos.

Rueckgabewert ist immer 0: das Werkzeug urteilt nicht, es zeigt.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image, ImageChops


SCHWELLE = 0.001  # 0,1 % der Bildpunkte — darunter ist es Rauschen


def vergleiche(alt: Path, neu: Path, diff: Path | None) -> list[tuple[str, float, str]]:
    ergebnis: list[tuple[str, float, str]] = []
    namen = sorted({p.name for p in alt.glob("*.png")} | {p.name for p in neu.glob("*.png")})

    for name in namen:
        a, b = alt / name, neu / name
        if not a.exists():
            ergebnis.append((name, 1.0, "neu"))
            continue
        if not b.exists():
            ergebnis.append((name, 1.0, "entfallen"))
            continue

        bild_a = Image.open(a).convert("RGB")
        bild_b = Image.open(b).convert("RGB")
        if bild_a.size != bild_b.size:
            ergebnis.append((name, 1.0, f"Groesse {bild_a.size} → {bild_b.size}"))
            continue

        unterschied = ImageChops.difference(bild_a, bild_b).convert("L")
        maske = unterschied.point(lambda w: 255 if w > 12 else 0)
        geaendert = sum(maske.histogram()[1:])
        anteil = geaendert / (bild_a.width * bild_a.height)
        ergebnis.append((name, anteil, "gleich" if anteil <= SCHWELLE else "geaendert"))

        if diff and anteil > SCHWELLE:
            diff.mkdir(parents=True, exist_ok=True)
            blass = Image.blend(bild_b, Image.new("RGB", bild_b.size, "white"), 0.72)
            blass.paste(Image.new("RGB", bild_b.size, (200, 30, 30)), mask=maske)
            blass.save(diff / name)

    return ergebnis


def main(argumente: list[str]) -> int:
    if len(argumente) < 2:
        print(__doc__.strip(), file=sys.stderr)
        return 2

    alt, neu = Path(argumente[0]), Path(argumente[1])
    diff = Path(argumente[2]) if len(argumente) > 2 else None
    zeilen = vergleiche(alt, neu, diff)

    auffaellig = [z for z in zeilen if z[2] != "gleich"]
    for name, anteil, bemerkung in zeilen:
        marke = "   " if bemerkung == "gleich" else "!! "
        print(f"  {marke}{name:28s} {anteil * 100:6.2f} %  {bemerkung}")

    print()
    if auffaellig:
        print(f"  {len(auffaellig)} von {len(zeilen)} Ansichten weichen ab.")
        if diff:
            print(f"  Diffbilder in {diff}")
    else:
        print(f"  Alle {len(zeilen)} Ansichten unveraendert.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
