# Arbeitsregeln für bb-limen.de

Diese Datei ist der **Vertrag**: kurze Regeln für alle, die an diesem
Repository arbeiten — Menschen wie Sprachmodelle.

Diese Website gehört einem Büro für rechtliche Betreuung. Sie wird von
Gerichten, Behörden, Kliniken und von Menschen in einer Ausnahmesituation
gelesen. Ein falscher Paragraph ist hier kein Schönheitsfehler.

**Verbindlichkeit.** MUSS und DARF NICHT gelten ohne Ausnahme. SOLL gilt im
Regelfall; wer abweicht, begründet es im Commit. KANN ist erlaubt.

**Kennungen.** Jede Regel hat eine feste Kennung wie `R-RECHT-2`. Tests und
Kommentare nennen dieselbe Kennung: `grep -rn R-RECHT-2` findet alles dazu.
Kennungen werden nie neu vergeben; eine fehlende Nummer ist eine entfallene
Regel.

Hier stehen nur Regeln. Die Handgriffe für häufige Änderungen stehen im
[README](README.md); wie etwas funktioniert und warum es so entschieden wurde,
in [docs/pflege.md](docs/pflege.md).

## Begriffe

| Begriff | Bedeutung |
| --- | --- |
| Seite | eine HTML-Datei unter `src/pages/`; der Bestand steht im Katalog |
| Personenabschnitt | der erzeugte Abschnitt einer betreuenden Person aus `src/betreuende.json` in `buero.html` |
| Katalog | `src/seiten.json` |
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
  und in dessen `public_files`, Vorstellungstexte und Porträts nach
  `src/betreuende/` mit einem Eintrag in `src/betreuende.json`. Der Build lehnt nicht eingetragene
  Dateien ab.

Mechanik: [docs/pflege.md](docs/pflege.md#aufbau).

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

Begründungen: [docs/pflege.md](docs/pflege.md#entscheidungen-in-kürze).

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
- **R-RECHT-4** Ändert sich ein Gesetz, MÜSSEN sich auch die Jahreszahlen im
  Text ändern. Ein Stand, der nicht mehr gilt, ist schlimmer als kein Stand.
- **R-RECHT-5** Text in `[eckigen Klammern]` ist ein bewusster Platzhalter für
  eine Angabe, die noch niemand entschieden hat. Er DARF NICHT erfunden
  ausgefüllt werden, die Klammern DÜRFEN NICHT entfernt werden, damit es
  fertig aussieht, und er DARF NICHT veröffentlicht werden. Finden:
  `grep -rn '\[[A-ZÄÖÜ]' src/`
- **R-RECHT-6** BB Limen veröffentlicht eine gemeinsame Zentrale. Sie DARF
  keiner Person zugeordnet werden. Jede betreuende Person DARF zusätzlich
  höchstens eine eigene Nummer haben; sie steht nur in `src/betreuende.json`
  und erscheint nur im Personenabschnitt und in der persönlichen
  Visitenkarte. Ein leeres `href="tel:"` DARF NICHT hinzukommen.

Geltende Rechtsstände: [docs/pflege.md](docs/pflege.md#rechtsstände-und-wiedervorlagen).

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
- **R-REDAKTION-3** Geprüft wird Technik, nie Inhalt. Eine Prüfung DARF bei
  einer reinen Änderung von Text, Zahlen, Büroangaben oder Gestaltung der
  Seiten NICHT fehlschlagen können. Tests und CI DÜRFEN deshalb keine
  Erwartungen zum Inhalt führen: keinen Wortlaut, keine Wortliste, keine
  Satzlänge, keine Büroangabe, keine Zählung. Zulässig ist, was nur bei einem
  Defekt anschlägt — Build, Verweise, HTML-Struktur, Kopfangaben.
  Assistenten DÜRFEN eine Inhaltsprüfung NICHT wieder einführen; die Regeln
  dieses Vertrags gelten auch ohne Test.

- **R-SPRACHE-1** Die vier Sprachebenen DÜRFEN NICHT vermischt werden, und der
  Stil einer Seite DARF NICHT nach dem Maßstab einer anderen „verbessert"
  werden.

  | Seite | Ebene |
  | --- | --- |
  | `leichte-sprache.html` | Leichte Sprache (etwa A1), ein Satz je Zeile |
  | `fachkreise.html` | Fachsprache, Paragraphen ohne Erklärung |
  | `impressum.html`, `datenschutz.html` | juristisches Standarddeutsch |
  | `index.html`, `betreuung.html`, `aufgaben.html`, `vorsorge.html` | Einfache Sprache (A2–B1) |
  | `buero.html` | Einfache Sprache (A2–B1) |
  | `404.html` | kurz und einfach |

- **R-SPRACHE-2** Die Leichte Sprache gilt erst als geprüft, wenn eine
  Prüfgruppe aus Menschen mit Lernschwierigkeiten sie gegengelesen hat. Das
  steht aus. Bis dahin DARF das Europäische Leichte-Sprache-Logo NICHT
  verwendet werden.
- **R-SPRACHE-3** Vertrauensfloskeln DÜRFEN NICHT auf der Website stehen:
  kompetent, individuell, professionell, zuverlässig, vertrauensvoll,
  ganzheitlich und ihresgleichen. Die Seite belegt, statt zu beteuern.
- **R-SPRACHE-4** Jeder Verweis MUSS sein Ziel nennen. „hier" und „mehr" sind
  keine Verweistexte.

Einzelheiten: [docs/pflege.md](docs/pflege.md#schreiben).

## 5. Farbe

- **R-FARBE-1** Alle Farbwerte MÜSSEN im Block `PALETTE` in `src/style.css`
  stehen. Ein Rückbau ist immer dieser eine Block, nie eine Suche durchs
  Stylesheet.
- **R-FARBE-2** `--gut` (Salbei) bedeutet Entlastung und steht im Fließtext nur
  im Block `.gut`. Assistenten DÜRFEN keine weitere Stelle hinzufügen; ob eine
  hinzukommt, entscheidet das Büro.
- **R-FARBE-3** Stahlblau bedeutet anklickbar: `--link-ink` auf Papier,
  `--link-on-carrier` auf Graphit. Nicht anklickbare Nebenangaben in der
  Kolumne MÜSSEN `--meta-on-carrier` verwenden. Ausnahmen sind die Wortmarke,
  der goldene aktuelle Standort und die goldene primäre Aktion „Anrufen".
- **R-FARBE-5** Jede Textpaarung MUSS WCAG AA erfüllen, hell und dunkel. Wer
  eine neue Paarung einführt, trägt sie in `tests/test_kontrast.py` ein.

Bedeutung der Farben: [docs/pflege.md](docs/pflege.md#gestaltung).

## 6. Gemeinsame Angaben

- **R-ANGABEN-1** Telefonnummer, E-Mail, Anschrift und Sprechzeiten MÜSSEN
  ausschließlich in `src/bureauangaben.json` gepflegt werden, die Angaben der
  betreuenden Personen ausschließlich in `src/betreuende.json`. Seiten und
  Bausteine MÜSSEN diese Werte über Platzhalter beziehen; wörtlich DÜRFEN sie
  dort NICHT stehen.
- **R-ANGABEN-2** Die vollständige Liste der Gemeinden des Einzugsgebiets steht
  an genau einer Stelle: in `index.html` im JSON-LD unter `areaServed`.
- **R-ANGABEN-5** Ändert sich der Inhalt einer Seite, MUSS ihr Stand
  nachgezogen werden: `lastmod` im Katalog, bei einer Änderung in
  `src/betreuende.json` das von `buero.html`, bei `impressum.html` und
  `datenschutz.html` das sichtbare Datum, in `fachkreise.html` der gesonderte
  Stand für Rückrufe und Abwesenheit (R-ORDNUNG-6).
- **R-ANGABEN-6** `dist/bb-limen.vcf` ist eine erzeugte gemeinsame
  Bürovisitenkarte aus dem JSON-LD der Startseite, `dist/<kennung>.vcf` die
  erzeugte Visitenkarte je betreuender Person aus `src/betreuende.json`; alle
  in UTF-8 mit CRLF-Zeilenenden. Eine manuell gepflegte vCard DARF NICHT
  hinzukommen.

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
  Eigene Seiten je Person gibt es vorerst nicht; die Personen stehen als
  Abschnitte in `buero.html`, Sprungmarke ist ihre Kennung.
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

**Fertig heißt:** `tools/pruefen.sh` besteht · die Änderung ist angesehen ·
die CI ist grün.

## 9. Ordnung

- **R-ORDNUNG-1** Jede Aussage MUSS genau ein Zuhause haben: Regeln hier,
  Handgriffe im README, Funktionsweise, Rechtsstände und Gründe in
  `docs/pflege.md`. Wer etwas ein zweites Mal aufschreiben will, setzt
  stattdessen einen Verweis.
- **R-ORDNUNG-2** Die Dokumente beschreiben den Zustand, nicht den Weg dorthin.
  Geschichte gehört in Git.
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
