# Arbeitsregeln für bb-limen.de

Diese Datei ist der **Vertrag**: kurze, prüfbare Regeln für alle, die an
diesem Repository arbeiten — Menschen wie Sprachmodelle.

`README.md` ist das **Handbuch**: es erklärt das Warum. Wo eine Regel eine
Begründung hat, steht hier der Verweis statt einer Wiederholung. Wer eine
Regel ändert, ändert beide Dateien im selben Commit.

Diese Website gehört einem Büro für rechtliche Betreuung. Sie wird von
Gerichten, Behörden, Kliniken und von Menschen in einer Ausnahmesituation
gelesen. Ein falscher Paragraph ist hier kein Schönheitsfehler.

---

## 1. Die Regel, die am leichtesten bricht

Zwischen den Marken `<!-- #rail -->` und `<!-- /#rail -->` steht
**generierter** Inhalt. Dasselbe gilt für `#head`, `#skip`, `#foot` und
`#callbar`.

**Ändere dort nie direkt in der Seite.** Ändere `partials/`, dann:

    tools/build.sh

Eine Änderung direkt in `index.html` sieht richtig aus, besteht sogar die
Tests — und ist beim nächsten Build spurlos verschwunden. Das ist der
Fehler, den bisher jedes Modell mindestens einmal gemacht hat.

Titel, `description`, `canonical` und die `og:`-Angaben stehen dagegen
**einzeln in jeder Seite**, weil sie sich unterscheiden. Sie gehören nicht
in einen Baustein.

---

## 2. Was niemals hinzukommt

- **Kein JavaScript.** Keine Webfonts, kein CDN, keine Karte, kein
  Analytics, kein Kontaktformular, kein Cookie-Banner.

  Das ist keine Geschmacksfrage: `datenschutz.html` behauptet, dass es
  nichts davon gibt. Jede Einbindung macht die Datenschutzerklärung unwahr
  und aus einem Gestaltungswunsch ein Rechtsproblem. Die Content-Security-
  Policy in `partials/head.html` setzt das technisch durch — wer sie
  lockern muss, baut gerade etwas ein, das hier nicht hingehört.

- **Keine fremden Formulare im Repo.** Verlinken, nicht hosten. Eine
  veraltete Vorsorgevollmacht versagt genau dann, wenn sie gebraucht wird
  (Begründung: `README.md` §2a).

- **Keine neue Datei im Wurzelverzeichnis**, ohne zu entscheiden, ob sie
  ausgeliefert werden soll. Wenn nicht, gehört sie in `_config.yml` unter
  `exclude`.

- **Kein Schmuckzeichen, das nicht in der Serifenschrift steht.** Zeichen
  wie ❦ ❧ ✦ ❖ kommen weder in Noto Serif noch in Georgia oder Times New
  Roman vor. Der Browser greift dann zu irgendeiner Symbol- oder
  Farb-Emoji-Schrift, und auf jedem Gerät steht etwas anderes auf der Seite
  — meist ein bunter Fleck. Ornamente gehören als SVG ins Markup
  (`.zierblatt`), nicht als Buchstabe. Wer doch ein Textzeichen braucht:
  U+00B7 ist in jeder Schrift, U+2042 und U+2058 immerhin in Noto Serif.

---

## 3. Recht

- **Jede Paragraphenangabe vor der Änderung nachschlagen** unter
  <https://www.gesetze-im-internet.de/>. **Nie aus dem Gedächtnis
  paraphrasieren.** Genau so ist der schwerste Fehler dieser Seite
  entstanden: eine erfundene Aufzählung zu § 1820 Abs. 2 BGB, die im Gesetz
  nicht steht.
- **Betreuungsrecht seit 01.01.2023:** Ein Betreuer hat *einen*
  Aufgabenkreis, und der besteht aus einem oder mehreren *Aufgabenbereichen*
  (§ 1815 Abs. 1 BGB). Der Plural „Aufgabenkreise" ist die alte Fassung und
  darf nirgends auftauchen.
- **Vergütung** nach VBVG in der Fassung vom 01.01.2026.
- Ändert sich ein Gesetz, ändern sich auch die Jahreszahlen im Text. Ein
  Stand, der nicht mehr gilt, ist schlimmer als kein Stand.

### Platzhalter

Text in `[eckigen Klammern]` ist ein **bewusster** Platzhalter für eine
Angabe, die noch niemand entschieden hat.

- Nie erfinden.
- Nie die Klammern entfernen, damit es fertig aussieht.
- Offene Stellen finden: `grep -rn '\[[A-ZÄÖÜ]' -- *.html partials/`

Besonders: Mika Möllers Telefonnummer ist **kein** `tel:`-Link, sondern
reiner Text. Ein leeres `href="tel:"` war schon einmal der schwerste
technische Fehler dieser Seite. Beim Eintragen die Nummer zugleich
verlinken.

---

## 4. Sprache

Vier Ebenen. **Nicht vermischen, und niemals den Stil einer Seite nach dem
Maßstab einer anderen „verbessern".**

| Datei | Ebene |
| --- | --- |
| `leichte-sprache.html` | Leichte Sprache (etwa A1), ein Satz je Zeile |
| `fachkreise.html` | Fachsprache, Paragraphen ohne Erklärung |
| `impressum.html`, `datenschutz.html` | juristisches Standarddeutsch |
| alle übrigen Inhaltsseiten | Einfache Sprache (A2–B1) |

Einzelheiten und Begründung: `README.md` §2b. Messen:

    python3 tools/pruefe-sprache.py

Die Leichte Sprache gilt erst dann als geprüft, wenn eine **Prüfgruppe** aus
Menschen mit Lernschwierigkeiten sie gegengelesen hat. Das steht aus. Bis
dahin kein Europäisches Leichte-Sprache-Logo verwenden.

---

## 5. Farbe

- Alle Werte stehen im Block `PALETTE` in `style.css`. Ein Rückbau ist immer
  dieser eine Block, nie eine Suche durchs Stylesheet.
- **`--gut` (Salbei) steht an genau vier Stellen im Fließtext**
  (`index` 1, `buero` 1, `leistungen` 2). Die Farbe bedeutet Entlastung;
  eine fünfte Stelle nimmt ihr die Bedeutung.
- Nach jeder Änderung an `PALETTE` **WCAG AA neu rechnen, hell und dunkel.**
  Die schwächste Paarung liegt bei 4,65:1 — es ist wenig Luft.

Begründung: `README.md` §2c.

---

## 6. Doppelt gepflegte Angaben

Die klassische Bruchstelle: ein Suchen-und-Ersetzen erwischt die Hälfte.

| Angabe | Steht in |
| --- | --- |
| Telefonnummer | `partials/rail.html`, `partials/callbar.html`, `index`, `fachkreise`, `leichte-sprache`, `impressum`, `datenschutz` |
| Einzugsgebiet (67 Gemeinden) | `index.html` im Fließtext **und** im JSON-LD unter `areaServed` |
| Anschrift | `partials/rail.html`, `partials/foot.html`, `index`, `impressum` |
| Sprechzeiten | `partials/rail.html`, `index`, JSON-LD `openingHours` |
| Datum des Stands | `impressum.html`, `datenschutz.html`, `sitemap.xml` |

Nach einer solchen Änderung immer gegenzählen, nicht schätzen.

---

## 7. Was nicht angetastet wird

- **Impressum und Datenschutz** stehen im Seitenfuß jeder Seite und in der
  Kolumne, nicht in der Hauptnavigation. § 5 DDG verlangt „leicht erkennbar,
  unmittelbar erreichbar und ständig verfügbar". Das ist erfüllt, solange
  die Verweise wörtlich *Impressum* und *Datenschutz* heißen, auf jeder
  Seite stehen und ohne JavaScript funktionieren. Beim Umbau der Navigation
  nicht anfassen.
- **Die Adressen bleiben bei `.html`.** Keine Verzeichnisform, keine
  Umbenennung. Entschieden am 20.09.2026.
- **Der Gründungshinweis** steht auf allen fünf Inhaltsseiten und im
  Impressum, solange die Registrierung nach § 23 BtOG nicht erteilt ist. Er
  verschwindet erst mit der Registrierungsnummer, und dann überall
  gleichzeitig.

---

## 8. Nach jeder Änderung, ohne Ausnahme

    python3 -m unittest discover -s tests -v   # 14 Tests
    tools/build.sh && git diff --exit-code     # kein Drift zwischen partials/ und Seiten
    python3 tools/pruefe-sprache.py            # Satzlängen

Alle drei laufen auch in der CI (`.github/workflows/pruefung.yml`). Wer sie
vorher lokal ausführt, erfährt dasselbe nur früher.

Ansehen — unbedingt auch am Telefon, dort wird aus der stehenden Kolumne
ein schmales Kopfband:

    python3 -m http.server 8391
    tools/schau.sh index.html 1280 1500 start
    tools/schau.sh index.html  390 1400 start-mobil
    tools/schau.sh index.html 1280 1500 start-dunkel dunkel

---

## 9. Ordnung im Repository

    *.html          acht Inhaltsseiten und 404.html — das ist die Website
    style.css       ein Stylesheet, keine Abhängigkeiten
    vorschau.png    Open-Graph-Bild, erzeugt aus tools/vorschau.svg
    partials/       Bausteine für build.sh, nicht ausgeliefert
    tools/          Werkzeuge, nicht ausgeliefert
    tests/          Regressionstests, nicht ausgeliefert
    docs/           Arbeitsmaterial, grösstenteils unversioniert
    _config.yml     bestimmt, was GitHub Pages NICHT ausliefert

Zwei verschiedene Schranken, die oft verwechselt werden:

- **`.gitignore`** hält Dateien aus der *Versionierung*.
- **`_config.yml`** hält versionierte Dateien aus der *Auslieferung*.

`partials/`, `tools/` und `tests/` sind versioniert, aber nicht im Netz.
Deshalb **kein `.nojekyll` anlegen** — das würde Jekyll abschalten und damit
genau diesen Ausschluss aufheben.

---

## 10. Commits

- Deutsch, beschreibend, in der Reihe der bisherigen.
- Modellgestützte Änderungen kenntlich machen, wie bisher: `(claude code)`,
  `(chatgpt)`.
- Eine Regel geändert? `AGENTS.md` **und** die betroffene README-Stelle im
  selben Commit nachziehen. Eine Regel, die nur noch in einer von beiden
  Dateien steht, ist ab da falsch.
