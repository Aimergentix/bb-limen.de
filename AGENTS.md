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

## 1. Quellen bearbeiten, Ausgabe erzeugen

**Bearbeite ausschließlich die Quellen unter `src/` und die bewusst
öffentlichen Dateien unter `public/`, wenn du Website-Inhalte änderst.
`dist/` ist vollständig generiert.**

Individuelle Seiten stehen in `src/pages/`. Sie enthalten je einen Include
für `head`, `skip`, `rail`, `foot`, `callbar`, in dieser Reihenfolge und
jeweils allein auf einer Zeile, etwa `<!-- @include rail -->`.
Gemeinsame Inhalte stehen in `src/partials/`. Danach:

    tools/build.sh

Die vollständigen Seiten entstehen in `dist/`; dort bleiben die bisherigen
Marken `<!-- #rail -->` und `<!-- /#rail -->` zur Orientierung erhalten.
Direkte Änderungen an der Ausgabe gehen beim nächsten Build verloren.
`tools/build.sh --check` meldet eine Abweichung, ohne Dateien zu verändern.

Titel, `description`, `canonical` und die individuellen `og:`-Angaben
bleiben in der jeweiligen Quelle unter `src/pages/`.

---

## 2. Was niemals hinzukommt

- **Kein JavaScript.** Keine Webfonts, kein CDN, keine Karte, kein
  Analytics, kein Kontaktformular, kein Cookie-Banner.

  Das ist keine Geschmacksfrage: `datenschutz.html` behauptet, dass es
  nichts davon gibt. Jede Einbindung macht die Datenschutzerklärung unwahr
  und aus einem Gestaltungswunsch ein Rechtsproblem. Die Content-Security-
  Policy in `src/partials/head.html` setzt das technisch durch — wer sie
  lockern muss, baut gerade etwas ein, das hier nicht hingehört.

- **Keine fremden Formulare im Repo.** Verlinken, nicht hosten. Eine
  veraltete Vorsorgevollmacht versagt genau dann, wenn sie gebraucht wird
  (Begründung: `README.md` §2a).

- **Jede neue Datei erhält eine eindeutige Rolle.** Seitenquellen gehören
  nach `src/pages/` und in `src/seiten.json`, öffentliche Kopierdateien nach
  `public/` und in dessen `public_files`. Der Build lehnt nicht registrierte
  Dateien in diesen Bereichen ab. Projektkonfiguration bleibt im Root;
  veröffentlicht wird ausschließlich das erzeugte `dist/`.

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
- Offene Stellen finden: `grep -rn '\[[A-ZÄÖÜ]' -- src/pages/*.html src/partials/`

BB Limen veröffentlicht genau **eine gemeinsame Büro-Telefonnummer**. Sie
wird keiner Person zugeordnet. Eine zweite persönliche Telefonnummer und ein
leeres `href="tel:"` dürfen nicht hinzukommen.

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

- Alle Werte stehen im Block `PALETTE` in `src/style.css`. Ein Rückbau ist immer
  dieser eine Block, nie eine Suche durchs Stylesheet.
- **`--gut` (Salbei) steht an genau vier Stellen im Fließtext**
  (`index` 1, `betreuung` 1, `aufgaben` 2). Die Farbe bedeutet Entlastung;
  eine fünfte Stelle nimmt ihr die Bedeutung.
- **Stahlblau bedeutet anklickbar:** `--link-ink` auf Papier,
  `--link-on-carrier` auf Graphit. Nicht anklickbare Nebenangaben in der
  Kolumne verwenden `--meta-on-carrier`. Ausnahmen sind die Wortmarke, der
  goldene aktuelle Standort und die goldene primäre Aktion „Anrufen“.
- **Kein Hell-/Dunkel-Schalter.** Die Darstellung folgt ausschließlich
  `prefers-color-scheme`; ohne JavaScript wäre die Wahl nicht verlässlich
  über alle `.html`-Seiten haltbar.
- Nach jeder Änderung an `PALETTE` **WCAG AA neu rechnen, hell und dunkel.**
  Die schwächste Paarung liegt bei 4,61:1 — es ist wenig Luft.

Begründung: `README.md` §2c.

---

## 6. Doppelt gepflegte Angaben

Kurze Seitennamen in diesem Vertrag beziehen sich auf `src/pages/`.

Die klassische Bruchstelle: ein Suchen-und-Ersetzen erwischt die Hälfte.

| Angabe | Steht in |
| --- | --- |
| Telefonnummer | `src/partials/rail.html`, `src/partials/callbar.html`, `index`, `fachkreise`, `leichte-sprache`, `impressum`, `datenschutz`, `404`, `public/bb-limen.vcf` |
| Einzugsgebiet (67 Gemeinden) | im Fließtext von `index`, `betreuung` und `fachkreise` **und** in `index.html` im JSON-LD unter `areaServed` |
| Anschrift | `src/partials/rail.html`, `index`, `fachkreise`, `leichte-sprache`, `impressum`, `datenschutz`, JSON-LD `address`, `public/bb-limen.vcf` |
| Sprechzeiten | `src/partials/rail.html`, `index`, `fachkreise`, `leichte-sprache` |
| Datum des Stands | `impressum.html`, `datenschutz.html`, `lastmod` in `src/seiten.json`; gesonderter Prüfstand für Rückrufe und Abwesenheit in `fachkreise.html` |

Nach einer solchen Änderung immer gegenzählen, nicht schätzen.

`public/bb-limen.vcf` ist eine gemeinsame Bürovisitenkarte. Name, Telefonnummer,
E-Mail, Anschrift und Website müssen mit dem JSON-LD der Startseite
übereinstimmen. Die Datei bleibt in UTF-8 mit CRLF-Zeilenenden;
`.editorconfig` und `.gitattributes` sichern das beim Bearbeiten und in Git.

---

## 7. Was nicht angetastet wird

- **Impressum und Datenschutz** stehen im Seitenfuß jeder Seite und in der
  Kolumne, nicht in der Hauptnavigation. § 5 DDG verlangt „leicht erkennbar,
  unmittelbar erreichbar und ständig verfügbar". Das ist erfüllt, solange
  die Verweise wörtlich *Impressum* und *Datenschutz* heißen, auf jeder
  Seite stehen und ohne JavaScript funktionieren. Beim Umbau der Navigation
  nicht anfassen.
- **Die Adressen bleiben bei `.html`.** Der Dateiname bezeichnet das
  Sachthema in Kleinbuchstaben; mehrere Wörter werden mit Bindestrichen
  verbunden. Menütexte dürfen eine grammatische Ergänzung enthalten, aber
  kein anderes Sachthema verwenden. `index.html` ist die technische
  Startdatei für `https://bb-limen.de/`. Keine Verzeichnisform und keine
  spätere Umbenennung ohne Entscheidung über bestehende Verweise.
  Entschieden am 20.09.2026.
- **Der Gründungshinweis** steht auf allen fünf Inhaltsseiten und im
  Impressum, solange die Registrierung nach § 23 BtOG nicht erteilt ist. Er
  verschwindet erst mit der Registrierungsnummer, und dann überall
  gleichzeitig.

---

## 8. Nach jeder Änderung, ohne Ausnahme

    tools/pruefen.sh
    tools/build.sh
    tools/build.sh --check

Der gemeinsame Prüfbefehl erzeugt seine Ausgabe temporär und verändert weder
Quellen noch `dist/` noch Git-Index. Er führt Buildprüfung, Regressionstests
und Sprachmessung aus. Einzelaufrufe bleiben möglich:

    python3 -m unittest discover -s tests -v
    python3 tools/pruefe-sprache.py

Die Sprachprüfung verwendet standardmäßig `dist/` und bricht bei fehlendem
oder unvollständigem Seitenbestand ab. Die Tests erzeugen unabhängig davon
eine frische temporäre Ausgabe. `tools/einrichten.sh` aktiviert den Hook,
der ebenfalls `tools/pruefen.sh` ausführt; er merkt keine Dateien vor.
Bei teilweise vorgemerkten Änderungen prüft er den gesamten Arbeitsbaum.

Die CI verwendet denselben Prüfbefehl und zusätzlich die HTML-Validierung.
Die zwei begrenzten CSP-Ausnahmen in `tools/html5validator.yml` benötigen die
Gegenkontrollen in `tests/test_site.py`; Begründung: README §3a und
`docs/architektur.md`. Keine pauschale Unterdrückung von Warnungen.
Die Veröffentlichung darf erst nach erfolgreicher Prüfung erfolgen und nur
`dist/` hochladen. Eine neue Seite erfordert den Eintrag im Seitenkatalog,
ihre bewusst gewählte Navigation und angepasste unabhängige Bestandstests.

Ansehen — breit, schmal (390 px) und in Dunkeldarstellung:

    python3 -m http.server 8391 --bind 127.0.0.1 --directory dist

Dann http://localhost:8391 öffnen. Die Sichtprüfung bleibt Handarbeit.

---

## 9. Ordnung im Repository

    src/pages/       acht Inhaltsseiten und 404.html als Quellen
    src/partials/    gemeinsame HTML-Bausteine
    src/style.css    ein Stylesheet, PALETTE bleibt ein Block
    src/grafik/      bearbeitbare SVG-Originale
    src/seiten.json  Seitenbestand, Sprachprofile, Sitemap und öffentliche Dateien
    public/          unverändert kopierte öffentliche Dateien, auch bb-limen.vcf
    dist/            vollständig erzeugte Website, unversioniert
    tools/           Werkzeuge und Commit-Hook, nicht ausgeliefert
    tests/           Regressionstests, nicht ausgeliefert
    docs/            technische Projektdokumentation, versioniert
    docs/lokal/      persönliche Arbeitsunterlagen, unversioniert — kann fehlen
    reports/         Auditberichte, unversioniert — kann fehlen

`.gitignore` steuert die Versionierung. Die Auslieferung wird durch den
Workflow begrenzt: Nur `dist/` wird hochgeladen. `_config.yml` bleibt als
Übergangsschutz, bis GitHub Pages bestätigt auf **GitHub Actions** umgestellt
ist; vorher darf die Migration nicht nach `main` gepusht werden. Siehe README
§4. Kein `.nojekyll` anlegen. Die alte Veröffentlichung aus dem Root ist mit
der neuen Quellstruktur nicht kompatibel.

`lastmod` im Katalog bezeichnet eine tatsächliche Inhaltsänderung. Builddatum,
Dateiverschiebung oder eine technische Formatierung setzen es nicht neu.
Weitere Datenzentralisierung wird als eigener inhaltlicher Umbau behandelt.

---

## 10. Commits

- Deutsch, beschreibend, in der Reihe der bisherigen.
- Modellgestützte Änderungen kenntlich machen, wie bisher: `(claude code)`,
  `(chatgpt)`.
- Eine Regel geändert? `AGENTS.md` **und** die betroffene README-Stelle im
  selben Commit nachziehen. Eine Regel, die nur noch in einer von beiden
  Dateien steht, ist ab da falsch.
