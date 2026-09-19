#!/usr/bin/env python3
"""Misst die Satzlaenge im Fliesstext der Seiten.

Einfache Sprache liegt etwa bei A2 bis B1. Ein mechanisch pruefbarer Teil
davon ist die Satzlaenge: im Mittel rund 15 Woerter, kein Satz ueber 25.
Das ersetzt kein Sprachgefuehl — es findet nur die Saetze, die zu lang
geraten sind. Gemessen wird der Satzspiegel ohne Kolumne, Navigation,
Kontaktlisten und Ortsliste.

    ./pruefe-sprache.py               alle Seiten
    ./pruefe-sprache.py index.html    eine Seite, mit den langen Saetzen
"""
import io, re, sys, glob

ZIEL_MITTEL, ZIEL_MAX = 15.0, 25
ABK = r"(§+\s?\d+[a-z]?|Abs|Nr|Art|ff|lit|bzw|ca|vgl|Dr|zum Beispiel|z|B|u|a|S|Tel)\."

def fliesstext(datei):
    h = io.open(datei, encoding="utf-8").read()
    # Alles wegnehmen, was kein Fliesstext des Satzspiegels ist
    for muster in (r'<aside class="rail".*?</aside>', r"<footer.*?</footer>",
                   r"<script.*?</script>", r"<style.*?</style>",
                   r'<ul class="orte">.*?</ul>', r'<dl class="contact">.*?</dl>',
                   r'<dl class="fakten">.*?</dl>', r'<dl class="rail-contact">.*?</dl>',
                   # Titelzeile und Quellenangabe der Verweisliste sind
                   # Beschriftungen, keine Saetze
                   r'<a class="titel".*?</a>', r'<span class="quelle">.*?</span>',
                   r'<span class="wer">.*?</span>', r'<p class="gramm">.*?</p>',
                   r"<!--.*?-->"):
        h = re.sub(muster, " ", h, flags=re.S)
    # Blockgrenzen sind Satzgrenzen — sonst laufen Listenpunkte zusammen
    h = re.sub(r"</(p|li|h1|h2|h3|dd|dt|blockquote|figcaption)>|<br\s*/?>", " ‖ ", h)
    h = re.sub(r"<[^>]+>", " ", h)
    h = h.replace("&nbsp;", " ").replace("&amp;", "&")
    return re.sub(r"[ \t]+", " ", h)

def saetze(t):
    stuecke = []
    for block in t.split("‖"):
        block = re.sub(ABK, lambda m: m.group(0).replace(".", "<P>"), block).strip()
        if not block:
            continue
        for s in re.split(r"(?<=[.!?])\s+(?=[A-ZÄÖÜ„»§\d])", block):
            s = s.replace("<P>", ".").strip()
            if len(s.split()) > 2:
                stuecke.append(s)
    return stuecke

def pruefe(datei, zeige=False):
    ss = saetze(fliesstext(datei))
    if not ss:
        return
    laengen = [len(s.split()) for s in ss]
    mittel, groesste = sum(laengen) / len(laengen), max(laengen)
    lang = sorted(((l, s) for l, s in zip(laengen, ss) if l > ZIEL_MAX), reverse=True)
    marke = "ok " if mittel <= ZIEL_MITTEL and groesste <= ZIEL_MAX else "!! "
    print(f"  {marke}{datei:22s} {len(ss):3d} Sätze · Mittel {mittel:5.1f}"
          f" · längster {groesste:3d} · über {ZIEL_MAX}: {len(lang)}")
    if zeige:
        for l, s in lang:
            print(f"        {l:3d}  {s[:155]}{'…' if len(s) > 155 else ''}")

if __name__ == "__main__":
    ziel = sys.argv[1:] or sorted(glob.glob("*.html"))
    print(f"Ziel: Mittel ≤ {ZIEL_MITTEL:.0f} Wörter, kein Satz > {ZIEL_MAX}\n")
    for d in ziel:
        pruefe(d, zeige=len(sys.argv) > 1)
