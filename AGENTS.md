# Arbeitsregeln für bb-limen.de

Diese Datei ist der **Vertrag**: kurze, prüfbare Regeln für alle, die an
diesem Repository arbeiten — Menschen wie Sprachmodelle.

Diese Website gehört einem Büro für rechtliche Betreuung. Sie wird von
Gerichten, Behörden, Kliniken und von Menschen in einer Ausnahmesituation
gelesen. Ein falscher Paragraph ist hier kein Schönheitsfehler.

**Verbindlichkeit.** MUSS und DARF NICHT gelten ohne Ausnahme. SOLL gilt im
Regelfall; wer abweicht, begründet es im Commit. KANN ist erlaubt.

**Kennungen.** Jede Regel hat eine feste Kennung wie `R-RECHT-2`. Tests,
Kommentare und Begründungen nennen dieselbe Kennung: `grep -rn R-RECHT-2`
findet alles dazu. Kennungen werden nie neu vergeben.

Hier stehen nur Regeln. Wie etwas funktioniert und warum es so entschieden
wurde, steht in den Dokumenten, die das [README](README.md#wo-steht-was)
aufführt.

## Begriffe

| Begriff | Bedeutung |
| --- | --- |
| Seite | eine HTML-Datei unter `src/pages/`; der Bestand steht im Katalog |
| Katalog | `src/seiten.json` |
| Sprachprofil | der Wert `language` einer Seite im Katalog |
| Pflichtseiten | `impressum.html` und `datenschutz.html` |
| Baustein | Datei unter `src/partials/`, über eine Include-Zeile in jede Seite eingesetzt |
| Kolumne | die stehende linke Spalte mit Navigation und Kontakt, Baustein `rail`; am Telefon ein Kopfband |
| Anrufleiste | die untere Leiste am Telefon, Baustein `callbar` |
| Ausgabe | `dist/`, vollständig erzeugt |
| Vorschaubild | `public/vorschau.png` für Open Graph; die Ausgabe im Browser heißt „lokale Ansicht" |

Kurze Seitennamen wie `index.html` meinen die Quelle unter `src/pages/`.

## 1. Quellen und Ausgabe

- **R-QUELLE-1** Inhalte MÜSSEN in `src/` und `public/` geändert werden.
  `dist/` DARF NICHT von Hand bearbeitet werden; `tools/build.sh` erzeugt es
  neu, und jede Änderung dort geht verloren.
- **R-QUELLE-2** Titel, `description`, `canonical` und die individuellen
  `og:`-Angaben MÜSSEN in der jeweiligen Seite stehen, nicht in einem Baustein.
- **R-QUELLE-3** Jede neue Datei MUSS eine eindeutige Rolle haben: Seiten nach
  `src/pages/` und in den Katalog, öffentliche Kopierdateien nach `public/`
  und in dessen `public_files`. Der Build lehnt nicht eingetragene Dateien ab.

Mechanik: [docs/architektur.md](docs/architektur.md).

## 2. Was nicht hinzukommt

- **R-VERBOT-1** Es DARF kein JavaScript hinzukommen, ebenso keine Webfonts,
  kein CDN, keine Karte, kein Analytics, kein Kontaktformular, kein
  Cookie-Banner. `datenschutz.html` behauptet, dass es nichts davon gibt; jede
  Einbindung macht die Datenschutzerklärung unwahr. Die
  Content-Security-Policy in `src/partials/head.html` setzt das durch und DARF
  NICHT gelockert werden.
- **R-VERBOT-2** Fremde Formulare DÜRFEN NICHT im Repository liegen. Verlinken,
  nicht hosten.
- **R-VERBOT-3** Schmuckzeichen wie ❦ ❧ ✦ ❖ DÜRFEN NICHT als Textzeichen
  stehen. Ornamente gehören als SVG ins Markup (`.zierblatt`). Wer ein
  Textzeichen braucht: U+00B7 ist in jeder Schrift, U+2042 und U+2058 immerhin
  in Noto Serif.
- **R-VERBOT-4** Es DARF kein Fallbeispiel, keine Klientengeschichte, kein
  Zitat einer betreuten Person und keine Bewertung auf der Website stehen,
  auch nicht anonymisiert.
- **R-VERBOT-5** Es DÜRFEN keine Ortsseiten entstehen, also keine
  Seitenvarianten mit getauschtem Ortsnamen. Die Gemeinden stehen im JSON-LD.
- **R-VERBOT-6** Das JSON-LD MUSS beim Typ `Organization` mit `PostalAddress`
  bleiben. `LocalBusiness` und seine Untertypen DÜRFEN NICHT verwendet werden.

Begründungen: [docs/entscheidungen.md](docs/entscheidungen.md).

## 3. Recht

- **R-RECHT-1** Jede Paragraphenangabe MUSS vor der Änderung nachgeschlagen
  werden unter <https://www.gesetze-im-internet.de/>. Sie DARF NICHT aus dem
  Gedächtnis paraphrasiert werden. Genau so ist der schwerste Fehler dieser
  Seite entstanden: eine erfundene Aufzählung zu § 1820 Abs. 2 BGB, die im
  Gesetz nicht steht.
- **R-RECHT-2** Betreuungsrecht seit 01.01.2023: Ein Betreuer hat *einen*
  Aufgabenkreis, und der besteht aus einem oder mehreren *Aufgabenbereichen*
  (§ 1815 Abs. 1 BGB). Der Plural „Aufgabenkreise" ist die alte Fassung und
  DARF NICHT auftauchen.
- **R-RECHT-3** Vergütung nach VBVG in der Fassung vom 01.01.2026.
- **R-RECHT-4** Ändert sich ein Gesetz, MÜSSEN sich auch die Jahreszahlen im
  Text ändern. Ein Stand, der nicht mehr gilt, ist schlimmer als kein Stand.
- **R-RECHT-5** Text in `[eckigen Klammern]` ist ein bewusster Platzhalter für
  eine Angabe, die noch niemand entschieden hat. Er DARF NICHT erfunden
  ausgefüllt werden, die Klammern DÜRFEN NICHT entfernt werden, damit es
  fertig aussieht, und er DARF NICHT veröffentlicht werden. Finden:
  `grep -rn '\[[A-ZÄÖÜ]' -- src/pages/*.html src/partials/`
- **R-RECHT-6** BB Limen veröffentlicht genau eine gemeinsame
  Büro-Telefonnummer. Sie DARF keiner Person zugeordnet werden. Eine zweite
  persönliche Telefonnummer und ein leeres `href="tel:"` DÜRFEN NICHT
  hinzukommen.

Geltende Rechtsstände: [docs/redaktion.md](docs/redaktion.md#rechtsstände).

## 4. Sprache und redaktionelle Hoheit

- **R-REDAKTION-1** Sichtbare Website-Texte, die das Büro selbst geändert
  oder ausdrücklich als final bezeichnet hat, haben redaktionellen Vorrang.
  Assistenten DÜRFEN sie ohne einen ausdrücklichen Auftrag zur Änderung der
  konkret betroffenen Textstelle NICHT umformulieren, ergänzen, kürzen,
  entfernen oder durch eine vermeintlich sicherere Aussage ersetzen. Ein
  allgemeiner Auftrag zum Prüfen, Fertigstellen, Committen, Mergen oder zu den
  „nötigen Maßnahmen" ist keine solche Erlaubnis.
- **R-REDAKTION-2** Bedenken gegen einen redaktionell gesetzten Text MÜSSEN
  mit genauer Fundstelle und Begründung getrennt von der Umsetzung berichtet
  und dem Büro zur Entscheidung vorgelegt werden. Eine Quelle, die einem
  Assistenten nicht vorliegt, ist kein Beleg dafür, dass eine Aussage
  unbegründet oder falsch ist. Das Fehlen einer solchen Quelle im Repository
  oder im Arbeitskontext DARF allein weder eine Textänderung noch eine
  Veröffentlichungssperre auslösen.
- **R-REDAKTION-3** Messwerte zu Satzlänge und Sprachniveau sind
  redaktionelle Hinweise, keine Freigabesperren. Eine Überschreitung der
  Zielwerte DARF `tools/pruefen.sh` nicht fehlschlagen lassen und berechtigt
  Assistenten nicht zur Änderung eines sichtbaren Textes. Fehler im
  Seitenbestand oder bei der technischen Auswertung bleiben Fehler.

- **R-SPRACHE-1** Die vier Sprachebenen DÜRFEN NICHT vermischt werden, und der
  Stil einer Seite DARF NICHT nach dem Maßstab einer anderen „verbessert"
  werden.

  | Seite | Ebene | Sprachprofil |
  | --- | --- | --- |
  | `leichte-sprache.html` | Leichte Sprache (etwa A1), ein Satz je Zeile | `leicht` |
  | `fachkreise.html` | Fachsprache, Paragraphen ohne Erklärung | `fach` |
  | `impressum.html`, `datenschutz.html` | juristisches Standarddeutsch | `recht` |
  | `index.html`, `betreuung.html`, `aufgaben.html`, `vorsorge.html` | Einfache Sprache (A2–B1) | `einfach` |
  | `404.html` | kurz und einfach, wird nur gezählt | `fehler` |

- **R-SPRACHE-2** Die Leichte Sprache gilt erst als geprüft, wenn eine
  Prüfgruppe aus Menschen mit Lernschwierigkeiten sie gegengelesen hat. Das
  steht aus. Bis dahin DARF das Europäische Leichte-Sprache-Logo NICHT
  verwendet werden.
- **R-SPRACHE-3** Vertrauensfloskeln DÜRFEN NICHT auf der Website stehen:
  kompetent, individuell, professionell, zuverlässig, vertrauensvoll,
  ganzheitlich und ihresgleichen. Die Seite belegt, statt zu beteuern.
- **R-SPRACHE-4** Jeder Verweis MUSS sein Ziel nennen. „hier" und „mehr" sind
  keine Verweistexte.

Einzelheiten und Messung: [docs/redaktion.md](docs/redaktion.md).

## 5. Farbe

- **R-FARBE-1** Alle Farbwerte MÜSSEN im Block `PALETTE` in `src/style.css`
  stehen. Ein Rückbau ist immer dieser eine Block, nie eine Suche durchs
  Stylesheet.
- **R-FARBE-2** `--gut` (Salbei) steht an genau vier Stellen im Fließtext:
  `index.html` 1, `betreuung.html` 1, `aufgaben.html` 2. Die Farbe bedeutet
  Entlastung; eine fünfte Stelle DARF NICHT hinzukommen.
- **R-FARBE-3** Stahlblau bedeutet anklickbar: `--link-ink` auf Papier,
  `--link-on-carrier` auf Graphit. Nicht anklickbare Nebenangaben in der
  Kolumne MÜSSEN `--meta-on-carrier` verwenden. Ausnahmen sind die Wortmarke,
  der goldene aktuelle Standort und die goldene primäre Aktion „Anrufen".
- **R-FARBE-4** Es DARF keinen Hell-/Dunkel-Schalter geben. Die Darstellung
  folgt ausschließlich `prefers-color-scheme`; ohne JavaScript wäre die Wahl
  nicht verlässlich über alle Seiten haltbar.
- **R-FARBE-5** Jede Textpaarung MUSS WCAG AA erfüllen, hell und dunkel. Wer
  eine neue Paarung einführt, trägt sie in `tests/test_kontrast.py` ein.

Bedeutung der Farben: [docs/gestaltung.md](docs/gestaltung.md).

## 6. Gemeinsame Angaben

Telefonnummer, E-Mail, Anschrift und Sprechzeiten MÜSSEN ausschließlich in
`src/bureauangaben.json` gepflegt werden. Seiten und Bausteine MÜSSEN diese
Werte über Büroplatzhalter beziehen. Jede Angabe MUSS in der erzeugten Ausgabe
an allen genannten Stellen stehen und übereinstimmen. Nach einer Änderung
MÜSSEN die unabhängigen Erwartungswerte in `tests/site_support.py` und
`tests/test_angaben.py` nachgezogen und die betroffenen Inhaltsstände geprüft
werden (R-ORDNUNG-6).

| Kennung | Angabe | Steht in |
| --- | --- | --- |
| **R-ANGABEN-1** | Telefonnummer und E-Mail | `src/partials/rail.html`, `src/partials/callbar.html`, `index.html`, `fachkreise.html`, `leichte-sprache.html`, `impressum.html`, `datenschutz.html`, `404.html`, `dist/bb-limen.vcf`, JSON-LD `telephone` und `email` |
| **R-ANGABEN-2** | Einzugsgebiet, 67 Gemeinden | im Fließtext von `index.html`, `betreuung.html` und `fachkreise.html` und in `index.html` im JSON-LD unter `areaServed` |
| **R-ANGABEN-3** | Anschrift | `src/partials/rail.html`, `index.html`, `fachkreise.html`, `leichte-sprache.html`, `impressum.html`, `datenschutz.html`, JSON-LD `address`, `dist/bb-limen.vcf` |
| **R-ANGABEN-4** | Sprechzeiten | `src/partials/rail.html`, `index.html`, `fachkreise.html`, `leichte-sprache.html` — je Sprachebene im eigenen Wortlaut |
| **R-ANGABEN-5** | Datum des Stands | `impressum.html`, `datenschutz.html`, `lastmod` im Katalog; gesonderter Prüfstand für Rückrufe und Abwesenheit in `fachkreise.html` |

- **R-ANGABEN-6** `dist/bb-limen.vcf` ist eine erzeugte gemeinsame Bürovisitenkarte.
  Name, Telefonnummer, E-Mail, Anschrift und Website MÜSSEN mit dem JSON-LD der
  Startseite übereinstimmen. Die Datei MUSS in UTF-8 mit CRLF-Zeilenenden
  bleiben; eine zweite, manuell gepflegte vCard DARF NICHT hinzukommen.

## 7. Bestand, der bleibt

- **R-BESTAND-1** Impressum und Datenschutz stehen im Seitenfuß jeder Seite
  und in der Kolumne, nicht in der Hauptnavigation. § 5 DDG verlangt „leicht
  erkennbar, unmittelbar erreichbar und ständig verfügbar". Das ist erfüllt,
  solange die Verweise wörtlich *Impressum* und *Datenschutz* heißen, auf jeder
  Seite stehen und ohne JavaScript funktionieren. Sie DÜRFEN beim Umbau der
  Navigation NICHT angefasst werden.
- **R-BESTAND-2** Die Adressen bleiben bei `.html`. Der Dateiname bezeichnet
  das Sachthema in Kleinbuchstaben; mehrere Wörter werden mit Bindestrichen
  verbunden. Menütexte dürfen eine grammatische Ergänzung enthalten, aber kein
  anderes Sachthema verwenden. `index.html` ist die technische Startdatei für
  `https://bb-limen.de/`. Eine Seite DARF NICHT umbenannt oder in eine
  Verzeichnisform überführt werden ohne Entscheidung über bestehende Verweise.
- **R-BESTAND-3** Der Gründungshinweis steht auf `index.html`,
  `betreuung.html`, `aufgaben.html`, `vorsorge.html` und `fachkreise.html` und
  im Impressum, solange die Registrierung nach § 23 BtOG nicht erteilt ist. Er
  verschwindet erst mit der Registrierungsnummer, und dann MUSS er überall
  gleichzeitig verschwinden.
- **R-BESTAND-4** Die Pflichtseiten und `404.html` tragen `noindex` und stehen
  nicht in der Sitemap; alle anderen Seiten DÜRFEN `noindex` NICHT tragen.

## 8. Prüfen und fertig werden

- **R-PRUEFUNG-1** Nach jeder Änderung MUSS `tools/pruefen.sh` bestehen. Der
  Befehl baut in ein temporäres Verzeichnis und verändert weder Quellen noch
  `dist/` noch den Git-Index. `tools/einrichten.sh` schaltet ihn einmalig als
  Commit-Hook ein.
- **R-PRUEFUNG-2** Wer Seiten, Bausteine oder das Stylesheet ändert, MUSS das
  Ergebnis ansehen: breit, schmal (390 px) und in Dunkeldarstellung. Das ist
  Handarbeit und bleibt es.
- **R-PRUEFUNG-3** Nach jedem Push MUSS das Ergebnis der CI angesehen werden:
  `gh run list --limit 3`. Eine rote CI heißt: nicht fertig.
- **R-PRUEFUNG-4** Ausnahmen in `tools/html5validator.yml` MÜSSEN eng gefasst
  sein, und jede braucht einen Gegentest in `tests/test_site.py`. Warnungen
  DÜRFEN NICHT pauschal unterdrückt werden.
- **R-PRUEFUNG-5** Eine neue Regel, die sich prüfen lässt, SOLL einen Test
  bekommen, der ihre Kennung nennt. Eine neue Seite MUSS in den Katalog, in die
  Navigationsentscheidung und in die Bestandstests.

**Fertig heißt:** `tools/pruefen.sh` besteht · die Änderung ist angesehen ·
mehrfach gepflegte Angaben sind gegengezählt · die CI ist grün.

## 9. Ordnung

- **R-ORDNUNG-1** Jede Aussage MUSS genau ein Zuhause haben. Regeln stehen
  hier, alles andere in dem Dokument, das das README dafür nennt. Wer etwas ein
  zweites Mal aufschreiben will, setzt stattdessen einen Verweis.
- **R-ORDNUNG-2** Vertrag und Handbücher beschreiben den Zustand, nicht den
  Weg dorthin. Geschichte gehört in Git, Entscheidungen mit Datum nach
  `docs/entscheidungen.md`; dort wird nur ergänzt, nie umgeschrieben.
- **R-ORDNUNG-3** Zahlen in der Dokumentation SOLLEN nur dort stehen, wo ein
  Test sie nachzählt.
- **R-ORDNUNG-4** Verzeichnisse heißen nach Web-Konvention englisch (`src`,
  `public`, `dist`, `tools`, `tests`, `docs`), Fachliches heißt deutsch.
  Dateinamen sind ASCII in Kleinbuchstaben: HTML und Shell mit Bindestrich,
  Python mit Unterstrich.
- **R-ORDNUNG-5** Alle Textdateien sind UTF-8. Kommentare und Dokumentation
  MÜSSEN echte Umlaute verwenden, keine Umschrift; Bezeichner im Code bleiben
  ASCII und je Datei in einer Sprache, in neuen Dateien englisch.
- **R-ORDNUNG-6** `lastmod` im Katalog bezeichnet eine tatsächliche
  Inhaltsänderung. Builddatum, Dateiverschiebung oder eine technische
  Formatierung DÜRFEN es NICHT neu setzen.

## 10. Commits und Zweige

- **R-COMMIT-1** Commit-Nachrichten sind deutsch und beschreibend, in der
  Reihe der bisherigen.
- **R-COMMIT-2** Modellgestützte Änderungen MÜSSEN kenntlich sein, wie bisher:
  `(claude code)`, `(chatgpt)`.
- **R-COMMIT-3** Jeder Push nach `main` veröffentlicht die Website.
  Assistenten MÜSSEN deshalb auf einem eigenen Zweig arbeiten; nach `main`
  gelangt nur, was das Büro freigegeben hat.
