# bb-limen.de — statische Website

Neun Seiten, ein Stylesheet, keine externen Ressourcen und kein JavaScript
im Browser. Bearbeitet werden `src/` und `public/`; `tools/build.sh` erzeugt
alle 17 öffentlichen Dateien in `dist/`.

> **Zuerst [AGENTS.md](AGENTS.md) lesen.** Dort stehen die verbindlichen
> Regeln. Dieses Handbuch erklärt die Gründe und die Arbeitsabläufe.

## Schnellstart

Voraussetzungen: Python 3.10 oder neuer und eine POSIX-Shell. Der normale
Build und die Regressionstests verwenden nur die Python-Standardbibliothek.
Git wird für die Versionsverwaltung und den optionalen Commit-Hook gebraucht.

```sh
tools/build.sh
python3 -m http.server 8391 --bind 127.0.0.1 --directory dist
```

Dann <http://localhost:8391> öffnen. Ein zweites Terminal für die Prüfung:

```sh
tools/pruefen.sh
```

`tools/pruefen.sh` erzeugt eine frische Ausgabe in einem temporären Ordner,
prüft sie und räumt sie wieder auf. Quellen, `dist/` und Git-Index bleiben
unverändert. `tools/build.sh --check` vergleicht dagegen das vorhandene
`dist/` mit den aktuellen Quellen und meldet Drift, ohne ihn zu berichtigen.

| Ich möchte … | Maßgebliche Datei | Danach |
| --- | --- | --- |
| einen Seitentext oder Seitentitel ändern | `src/pages/<seite>.html` | Build, Prüfung, ansehen |
| Navigation, Kolumne oder Kontaktleiste ändern | `src/partials/rail.html`, `callbar.html` | Build, Prüfung, alle Seiten beachten |
| Farben oder Abstände ändern | `src/style.css` | Build, Prüfung inklusive Kontrast, hell/dunkel/mobil ansehen |
| Telefonnummer oder Anschrift ändern | Fundstellen in AGENTS §6 | alle Angaben abgleichen, einschließlich `public/bb-limen.vcf` |
| eine Seite hinzufügen | `src/pages/`, `src/seiten.json`, Navigation und erwarteter Testbestand | Build, Prüfung, neue Verweise ansehen |
| einen Sitemap-Stand ändern | `lastmod` in `src/seiten.json` | Build und Prüfung |
| Signet oder Vorschaubild ändern | `src/grafik/` | `tools/vorschau.sh`, dann Build und Prüfung |

Die [Architekturbeschreibung](docs/architektur.md) erklärt Datenfluss,
Verantwortlichkeiten, Katalog und Erweiterungsweg.

```text
src/pages/         neun individuelle Seitenquellen mit Include-Verweisen
src/partials/      fünf gemeinsame HTML-Bausteine
src/style.css      ein Stylesheet mit zentralem PALETTE-Block
src/grafik/        SVG-Originale für Signet und Vorschaubild
src/seiten.json    Seitenbestand, Sprachprofile, Sitemap-Stände, öffentliche Dateien
public/            bewusst öffentliche, unverändert kopierte Dateien
dist/              erzeugte Website, nicht versioniert, niemals von Hand bearbeiten
tools/             Build, Prüfung, Bildexport und Commit-Hook
tests/             Regressionstests
docs/              gemeinsame technische Dokumentation, versioniert
docs/lokal/        persönliche Arbeitsunterlagen, ignoriert
reports/           lokale Auditberichte, ignoriert
.github/workflows/ automatische Prüfung, Verweise und Veröffentlichung
```

Projektregeln (`AGENTS.md`, `CLAUDE.md`), dieses Handbuch, `LICENSE` sowie
Git- und Editor-Konfiguration bleiben im Root. `.gitignore` bestimmt die
Versionierung; der Veröffentlichungsworkflow lädt ausschließlich `dist/` hoch.
`_config.yml` ist bis zur bestätigten Pages-Umstellung ein Übergangsschutz,
kein Teil des neuen Builds. Ein `.nojekyll` wird nicht benötigt.

## 1. Seiten und gemeinsame Bausteine ändern

Die Inhalte stehen in `src/pages/`. An den fünf Einfügestellen steht jeweils
allein auf einer Zeile ein Include, beispielsweise:

```html
<!-- @include rail -->
```

Die Reihenfolge lautet `head`, `skip`, `rail`, `foot`, `callbar`. Bearbeitet
wird der Baustein in `src/partials/`, anschließend läuft `tools/build.sh`.
Die vollständigen Seiten entstehen ausschließlich in `dist/`. Ihre bisherigen
Kommentargrenzen `<!-- #rail -->` und `<!-- /#rail -->` bleiben zur Orientierung
erhalten. Die Ausgabe darf jederzeit neu erzeugt werden.

Der Build prüft den Katalog, Dateibestand, Bausteine, Include-Reihenfolge und
Navigationsplatzhalter vor dem Schreiben. Er erzeugt erst ein vollständiges
Arbeitsverzeichnis und ersetzt dann `dist/`. Bei fehlerhaften Eingaben bleiben
Quellen und die letzte erfolgreiche Ausgabe erhalten. Nicht mehr benötigte
Ausgabedateien verschwinden beim nächsten erfolgreichen Build.

Seitentitel, Beschreibung, `canonical` und individuelle `og:`-Angaben bleiben
bei der jeweiligen Seite. Die öffentliche Adresse bleibt unabhängig vom
Quellpfad: `src/pages/betreuung.html` wird zu `dist/betreuung.html` und ist
weiterhin unter `/betreuung.html` erreichbar. Der Dateiname benennt das
Sachthema in Kleinbuchstaben und mit Bindestrichen. Menütexte dürfen eine
grammatische Ergänzung enthalten, aber kein anderes Sachthema verwenden.
`index.html` ist die technische Startdatei für `https://bb-limen.de/`.

Kurze HTML-Dateinamen in den folgenden fachlichen Abschnitten bezeichnen die
jeweilige Quelle unter `src/pages/`. Gemeinsame Texte liegen in `src/partials/`.

## 2. Noch offen

Suche in den ausgelieferten HTML-Dateien und Partials nach `[` — solange dort
etwas gefunden wird, ist die Seite nicht veröffentlichungsfertig:

    rg -n '\[[A-ZÄÖÜ]' -- src/pages/*.html src/partials/*.html

Offen sind:

**Im Impressum** (eine Angabe braucht noch eine Entscheidung):

- **Umsatzsteuer — erledigt am 20.09.2026.** Im Impressum steht die
  Befreiung nach § 4 Nr. 16 Satz 1 Buchstabe k UStG mit der Ausnahme für
  Leistungen nach § 1877 Abs. 3 BGB. Offen bleibt allein, ob eine
  USt-IdNr. nach § 27a UStG besteht; § 5 DDG verlangt sie nur, soweit
  vorhanden. Falls ja, einen Satz ergänzen — nicht ins Blaue behaupten,
  dass keine besteht.
- **Berufshaftpflichtversicherung.** Versicherer und Anschrift. Die
  Versicherung ist ohnehin Voraussetzung der Registrierung nach
  § 23 Abs. 1 Nr. 3 BtOG.

**Büro-Telefon** — BB Limen veröffentlicht genau eine gemeinsame Nummer und
ordnet sie keiner einzelnen Person zu. Die maßgeblichen Stellen für Kolumne
und mobile Anrufleiste liegen in `src/partials/rail.html` und
`src/partials/callbar.html`; nach dem Build stehen deren Kopien in allen neun
Seiten. Zusätzliche direkte Kontaktangaben gibt es in `index.html`,
`fachkreise.html`, `leichte-sprache.html`, `impressum.html` und
`datenschutz.html`. Eine zweite persönliche Telefonnummer und ein leeres
`href="tel:"` dürfen nicht hinzukommen.

**Bürovisitenkarte** — `public/bb-limen.vcf` wird öffentlich ausgeliefert und ist
im Kontaktabschnitt der Startseite und der Fachseite verlinkt. Sie enthält
den gemeinsamen Bürokontakt, keine persönliche Telefonnummer. Name,
Telefonnummer, E-Mail, Anschrift und Website stimmen mit dem JSON-LD der
Startseite überein; `tests/test_angaben.py` prüft diesen Abgleich.
Die Datei verwendet vCard 3.0, UTF-8 und CRLF-Zeilenenden. `.editorconfig`
bewahrt die Zeilenenden beim Bearbeiten, `.gitattributes` verhindert eine
Umwandlung durch Git und wird selbst nicht ausgeliefert. Bei einer Änderung
der Kontaktdaten auch die Visitenkarte aktualisieren.

**Rückrufe und Abwesenheit** — Laut Betreiberangabe vom 20.09.2026 noch
nicht geregelt. Die Fachseite nennt diesen offenen Stand im Kontaktabschnitt;
sie verspricht keine feste Rückruffrist und keine telefonische Erreichbarkeit
außerhalb der Sprechzeiten. Sobald die Abläufe feststehen, Beschreibung und
Prüfdatum dort gemeinsam aktualisieren. Dieses Datum bezieht sich nur auf
die Rückruf- und Abwesenheitsregelung, nicht auf eine Prüfung aller Fachtexte.

**Externe Profile** — Laut Betreiberangabe vom 20.09.2026 bestehen noch
keine öffentlichen Profile für BB Limen, Aranda Möller oder Mika Möller.
Deshalb gibt es derzeit keine Profil-Links und kein `sameAs`. Wenn Profile
hinzukommen, die genaue URL und Identität prüfen: persönliche Profile der
jeweiligen Person zuordnen, gemeinsame Büroprofile dem Büro.

**Registrierungen.** Beide Personen sind freiberuflich und einzeln
registrierungspflichtig (§ 23 BtOG, personenbezogen, nicht bürobezogen).
Sobald eine Registrierung erteilt ist: Nummer und Datum im Impressum
eintragen und den jeweiligen Gründungshinweis entfernen. Solange eine
Registrierung fehlt, darf die betreffende Person keine berufliche
Betreuung führen.

**Berufshaftpflicht.** Zwei getrennte Verträge, je einer pro Person
(§ 23 Abs. 1 Nr. 3 BtOG). Im Impressum sind beide Zeilen angelegt.

**Prüfung der Leichten Sprache.** `leichte-sprache.html` folgt den
üblichen Regeln — kurze Sätze, ein Satz je Zeile, Binde-Striche in
zusammengesetzten Wörtern, schwere Wörter erklärt. Nach dem Standard des
Netzwerks Leichte Sprache gehört ein Text aber von einer **Prüfgruppe**
aus Menschen mit Lernschwierigkeiten gegengelesen, bevor er als Leichte
Sprache gilt. Das steht noch aus. Lebenshilfe und Diakonie vermitteln
solche Prüfgruppen; die Betreuungsbehörde weiß meist, wer es vor Ort
macht. Erst danach das Europäische Leichte-Sprache-Logo verwenden — es
ist lizenziert und setzt die Prüfung voraus.

## 2a. Verweise nach außen pflegen

Die Seiten `vorsorge.html` und `leichte-sprache.html` verweisen auf zwölf
fremde Seiten — Ministerien, Behörden, Bundesnotarkammer, Lebenshilfe,
KVJS. **Absichtlich werden keine fremden Formulare im Repo gehostet:** ein
Vordruck für eine Vorsorgevollmacht veraltet mit dem Gesetz, und eine
veraltete Vollmacht versagt genau dann, wenn sie gebraucht wird. Wer die
Datei selbst ausliefert, übernimmt diese Verantwortung; wer verlinkt,
lässt sie bei der herausgebenden Stelle. Dazu kommt, dass weder das BMJ
noch das Justizministerium Baden-Württemberg Nutzungsbedingungen für die
Weiterverbreitung angibt.

Auf jeder Angabe steht der Stand des Dokuments. **Zweimal im Jahr prüfen**,
ob Link und Stand noch stimmen:

    grep -ho 'href="https\?://[^"]*"' dist/*.html | sed 's/href="//;s/"$//' \
      | grep -v bb-limen.de | sed 's/&amp;/\&/g' | sort -u \
      | while read u; do echo "$(curl -sLo /dev/null -w '%{http_code}' "$u")  $u"; done

Ändert eine Stelle den Stand ihres Dokuments, die Angabe auf der Seite
mitziehen — sonst steht dort eine Jahreszahl, die nicht mehr gilt.

## 2b. Sprachebenen

Die Seite hat vier Sprachebenen. Wer Text ändert, sollte wissen, auf
welcher er sich befindet:

- **`leichte-sprache.html`** — Leichte Sprache. Kurze Sätze,
  ein Satz je Zeile, Binde-Striche in zusammengesetzten Wörtern, schwere
  Wörter erklärt. Eigene Typografie über `body class="ls"`. Kurze Sätze sind
  eine redaktionelle Hilfe, aber keine numerische A1-Zertifizierung.
- **`fachkreise.html`** — Fachsprache für Gerichte, Behörden, Kliniken
  und Ärzte. Paragraphen ohne Erklärung der Grundlagen. Hier ist
  Genauigkeit wichtiger als Einfachheit. Das Sprungmenü oben muss zu den
  `id`-Attributen der Überschriften passen.

**Begriffe, die leicht falsch werden.** Seit dem 1. Januar 2023 hat ein
Betreuer *einen* Aufgabenkreis, und der besteht aus einem oder mehreren
*Aufgabenbereichen* (§ 1815 Abs. 1 BGB). Der Plural „Aufgabenkreise" ist
die alte Fassung und sollte nirgends mehr auftauchen. Eine abschließende
Liste der Aufgabenbereiche gibt es nicht — Register VI auf
`aufgaben.html` sagt das ausdrücklich.
- **alle übrigen Inhaltsseiten** — Einfache Sprache (etwa A2 bis B1).
  Kurze Sätze, aktiv statt passiv, Verben statt Substantivierungen,
  Fachwörter bei der ersten Nennung erklärt. Aber mit Rhythmus: Sätze
  dürfen unterschiedlich lang sein, nur nicht verschachtelt.

`impressum.html` und `datenschutz.html` bleiben bewusst in juristischem
Standarddeutsch. Art. 12 DSGVO verlangt zwar Verständlichkeit, aber eine
vereinfachte Datenschutzerklärung wird schnell unvollständig — und
Unvollständigkeit ist der teurere Fehler.

Messen lässt sich ein Teil davon:

    python3 tools/pruefe-sprache.py                 alle Seiten
    python3 tools/pruefe-sprache.py vorsorge.html   mit den zu langen Sätzen

Der Parser betrachtet nur den Fließtext in `main`; Überschriften,
Beschriftungen, Kontakt- und Ortslisten werden getrennt gehalten. `<br>` ist
ein Layoutumbruch und kein Satzende. Das A2/B1-Ziel — im Mittel höchstens 15
Wörter je Satz, kein Satz über 25 — gilt für `index`, `betreuung`, `aufgaben`
und `vorsorge`. Fachseite, Pflichttexte und Leichte Sprache werden separat als
Statistik ausgegeben. Das ersetzt weder Sprachgefühl noch die Prüfgruppe.

Regressionstests für Build, Sprachmessung, Seitenstruktur, doppelt
gepflegte Angaben, bekannte Fehlformulierungen und die WCAG-Kontraste:

    python3 -m unittest discover -s tests -v

Dieselben Prüfungen laufen bei jedem Push in GitHub Actions
(`.github/workflows/pruefung.yml`). Wer sie vorher lokal ausführt, erfährt
dasselbe nur früher.

Die drei Bilddateien — Vorschaubild und die beiden Symbole — entstehen aus
zwei SVG-Quellen in `src/grafik/` und sind versioniert, damit der normale
Build keinen Browser braucht. Der Bildexport benötigt Chromium oder Chrome
und Python; die fertigen Bilder liegen in `public/`. Nach einer Änderung
an Signet oder Palette neu rendern:

    tools/vorschau.sh

## 2c. Farbe

Die Farben benennen Funktionen, nicht einzelne Seiten. Alle Werte stehen im
Block PALETTE in `src/style.css`; ein Rückbau ist immer dieser eine Block, nie
eine Suche durchs Stylesheet.

- **Gold** (`--accent`, `--accent-on-carrier`) — Ordnung: Rubriken,
  Ziffern, Zierlinien, aktueller Standort und die primäre Aktion „Anrufen“.
  Auf dem hellen Papier steht ein kontraststarkes Goldocker, auf Graphit eine
  zweite, hellere Goldstufe. In der Navigation zeigt zusätzlich eine Linie
  den aktuellen Standort; Farbe allein trägt diese Information nicht.
- **Stahlblau** (`--link-ink`, `--link-on-carrier`) — Bedienung. Anklickbare
  Textstellen stehen dunkel auf Papier und hell auf Graphit. Fließtext-,
  Kontakt- und Rechtsverweise bleiben zusätzlich unterstrichen; frei stehende
  Verweistitel stehen in der Sans-Serif-Schrift. Die Kartuschen „Leichte
  Sprache“ und „Für Fachkreise“ verwenden dieselbe Bedienfarbe.
- **Warmes Steingrau** (`--meta-on-carrier`) — nicht anklickbare Nebenangaben
  in der Kolumne: Rollenbezeichnung, Beschriftungen und Namen. So sieht ein
  statischer Text nicht wie ein Verweis aus.
- **Salbei** (`--gut`) — Entlastung. Im Fließtext nur für den Block
  `.gut`, und nur dort, wo die Nachricht wirklich entlastet: keine
  Entmündigung, eigene Wahl des Betreuers, keine Kosten bei
  Mittellosigkeit, der Weg zurück. **Vier Stellen auf der ganzen
  Website** (`index` 1, `betreuung` 1, `aufgaben` 2). Wer mehr hinzufügt,
  nimmt der Farbe ihre Bedeutung. `--st-2` der Leichte-Sprache-Liste hat
  denselben Wert.
- **Papierwärme** (`--paper`, `--surface`) — keine Farbe, die man sieht,
  sondern eine Temperatur. `#fbfaf7` statt neutralem Grau.
- **Mint** (`--brand-leaf`) — gehört nur zur Blattkontur des Signets. Es ist
  Markenfarbe, keine Bedienfarbe.
- **Terrakotta** (`--leicht-ink`) — trägt auf der Leichte-Sprache-Seite
  Überschriften und Farbrhythmus, nicht die Navigation.

Das Zierzeichen zwischen den Haarlinien ist kein Buchstabe, sondern
dasselbe Blatt wie die Marke der Kolumne (`.zierblatt`, siehe `src/style.css`).
Bis zum 20.09.2026 stand dort U+2766 ❦ — ein Zeichen, das in keiner
Serifenschrift des Projekts vorkommt und deshalb auf eine Symbol- oder
Farb-Emoji-Schrift zurückfiel: auf jedem Gerät ein anderes Bild. Als SVG
ist es überall dasselbe und folgt über `currentColor` der Farbe des
Ornaments. Schmuckzeichen also nie als Buchstabe.

Dazu `--hauch` für den Farbton, der nur bei Berührung erscheint, und
`--st-1` bis `--st-5` ausschließlich für die Leichte-Sprache-Seite: dort
hilft Farbe an Listen und Überschriften beim Wiederfinden und ist damit
Funktion, keine bloße Dekoration.

Hell und dunkel folgen ausschließlich der Systemeinstellung über
`prefers-color-scheme`. Einen Schalter auf der Seite gibt es bewusst nicht:
ohne JavaScript ließe sich seine Wahl beim Wechsel zwischen den neun
HTML-Seiten nicht verlässlich bewahren.

**Jede Farbe ist gegen WCAG AA geprüft, hell und dunkel.** Nach jeder
Änderung am PALETTE-Block neu rechnen — die schwächste Paarung liegt bei
4,61:1, es ist also wenig Luft. Die Fachseite bleibt bewusst nüchtern.

## 3. Lokal ansehen

```sh
tools/build.sh
python3 -m http.server 8391 --bind 127.0.0.1 --directory dist
```

<http://localhost:8391> breit, schmal (390 px) und in Dunkeldarstellung ansehen.
Nach Quellenänderungen erneut bauen und die Seite neu laden. Auf dem Telefon
wird aus der stehenden Kolumne ein Kopfband; die Kontaktleiste bleibt unten.
Die Quellen in `src/pages/` sind Vorlagen und nicht als vollständige Seiten
im Browser zu öffnen.

## 3a. Was von selbst läuft

**Vor jedem Commit:** `tools/einrichten.sh` aktiviert einmalig den Hook.
Er ruft denselben Befehl `tools/pruefen.sh` auf wie die CI. Geprüft wird der
Arbeitsbaum, nicht nur der Git-Index; der Hook verändert und staged nichts.
Bei teilweise vorgemerkten Änderungen prüft die CI anschließend den
committeten Stand. `git commit --no-verify` überspringt nur den lokalen Hook.

**Bei Push und Pull Request:** `.github/workflows/pruefung.yml` führt den
Prüfbefehl aus und validiert danach das fertige HTML mit `html5validator`
(Java 21 und Python-Paket, nur für diese zusätzliche Prüfung). Auf `main`
ruft der Veröffentlichungsworkflow diese Prüfung als Voraussetzung auf;
andere Branches und Pull Requests werden ohne Veröffentlichung geprüft.

`tools/html5validator.yml` lässt Warnungen fehlschlagen und nimmt nur zwei
bekannte CSP-Meldungen sowie den bekannten `theme-color`-Fehltreffer des
gebündelten Prüfstands aus. Separate Regressionen sichern Stylesheet, JSON-LD,
CSP und die zwei erlaubten `theme-color`-Elemente ab; Begründung und Quellen
stehen in der [Architekturbeschreibung](docs/architektur.md#html-validierung).
Mit installiertem Java und `html5validator` läuft dieselbe Zusatzprüfung lokal:

```sh
tools/build.sh
html5validator --config tools/html5validator.yml
```

**Einmal im Monat:** `.github/workflows/verweise.yml` baut die Website und
prüft ihre externen Verweise. Bei nicht erreichbaren Adressen entsteht ein
Issue. Der Dokumentstand bleibt halbjährlich von Hand zu prüfen (§2a).

Der seit 21.09.2026 entfernte maschinelle Bildvergleich wird nicht wieder
eingeführt. Die Sichtprüfung aus Abschnitt 3 bleibt Handarbeit.

## 4. Bei GitHub Pages veröffentlichen

Kanonische Adresse bleibt `https://bb-limen.de/`, Repository
<https://github.com/Aimergentix/bb-limen.de>. Die neue Struktur benötigt
**Settings → Pages → Source: GitHub Actions**. Die frühere Einstellung
`Deploy from a branch`, `main`, `/ (root)` ist damit nicht mehr kompatibel.

### Einmaliger Übergang

1. Den lokalen Stand prüfen und die Änderung als zusammengehörige Migration
   bereitstellen. Vor dem ersten Push nach `main` die Pages-Einstellungen
   und die Domain prüfen. Ist Pages noch nicht eingerichtet oder für das
   Repository nicht verfügbar, muss das zuerst geklärt werden.
2. Pages auf **GitHub Actions** umstellen. Die Domain `bb-limen.de` und HTTPS
   in den Pages-Einstellungen erhalten beziehungsweise bestätigen. Die Datei
   `public/CNAME` bleibt Teil der Ausgabe; beim eigenen Workflow ersetzt sie
   nicht die Domain-Einstellung bei GitHub.
3. Erst dann die Migration nach `main` übertragen. Der Workflow
   `veroeffentlichung.yml` prüft den Stand, baut `dist/`, lädt genau diesen
   Ordner als Pages-Artefakt hoch und veröffentlicht ihn. Ein fehlgeschlagener
   Prüflauf blockiert die Veröffentlichung. Manueller Start ist auf `main`
   ebenfalls möglich.
4. Die öffentlichen Seiten, Downloads, Domainweiterleitung und HTTPS prüfen.
   `src/`, `tools/`, `tests/`, `docs/` und `README.md` dürfen nicht ausgeliefert
   werden. Die HTML-Adressen bleiben unverändert.
5. Erst nach bestätigter Umstellung kann `_config.yml` entfallen. Bis dahin
   schließt die Datei auch `src/`, `public/` und `dist/` vom alten Jekyll-Weg
   aus. Sie verhindert die Auslieferung von Quellen, macht den alten Weg
   aber nicht mit der neuen Struktur kompatibel. Kein `.nojekyll` anlegen.

Der lokale Refactor allein ändert keine GitHub-Einstellung. Ein erfolgreicher
lokaler Test bestätigt weder Pages-Zugriff noch einen erfolgten Deploy.

### Rückweg

Der Ausgangsstand dieser Migration ist Commit
`c2064ceac1a0c7bc7505c640b120ee69ba4d4428`. Ein Rückbau muss die vollständige
alte Dateistruktur und die dazu passende Veröffentlichung aus `main / (root)`
wieder zusammenherstellen. Nur die Pages-Einstellung zurückzustellen reicht
nicht. Lokale Änderungen vorher sichern; kein pauschales `reset --hard`.

Offizielle Anleitungen:

- [Veröffentlichungsquelle konfigurieren](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Eigene Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Eigene Domain konfigurieren](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

## 5. Vor dem Onlinegehen prüfen

- Die offene Angabe aus Abschnitt 2 eingetragen: Firma und Anschrift des
  Berufshaftpflichtversicherers.
- Registrierung nach § 23 BtOG noch nicht erteilt: Der Hinweis auf den
  Gründungsstand steht auf allen fünf Inhaltsseiten (`index`, `betreuung`,
  `aufgaben`, `vorsorge`, `fachkreise`) und im Impressum. Nach Erteilung
  Registrierungsnummer eintragen, das Datum im Impressum aktualisieren und
  die Hinweisblöcke entfernen.
- Impressum und Datenschutzerklärung stehen bewusst nicht mehr in der
  Hauptnavigation, sondern im Seitenfuß jeder Seite und in der Kolumne.
  § 5 DDG verlangt „leicht erkennbar, unmittelbar erreichbar und ständig
  verfügbar“ — das ist erfüllt, solange die Verweise wörtlich Impressum
  und Datenschutz heißen, auf jeder Seite stehen und ohne JavaScript
  funktionieren. Beim Umbau der Navigation nicht antasten.
- Die Datumsangaben in `impressum.html` und `datenschutz.html` sowie der
  Inhaltsstand `lastmod` in `src/seiten.json` stimmen noch.
- Die veröffentlichte Aufgabenverteilung nach Art. 26 DSGVO entspricht der
  tatsächlichen Vereinbarung: Aranda Möller übernimmt für die gemeinsame
  Website die Informationspflichten, die Bearbeitung von Betroffenenanfragen
  und die Koordination von Hosting beziehungsweise technischem Betrieb.
  Änderungen immer zugleich in der Vereinbarung und in `datenschutz.html`
  nachziehen.
- Die Vergütungsangaben in `aufgaben.html` (sechzehn reguläre
  Fallpauschalen, 98 bis 427 Euro; Sondervergütung für Sterilisations- und
  Ergänzungsbetreuer) gelten nach dem zum 1. Januar 2026 geänderten VBVG.
  Die Tabelle ist die Anlage zu § 8 Abs. 1 VBVG (Fundstelle BGBl. 2025 I
  Nr. 109), die Bemessung regelt § 9 VBVG. Der Geldbetrag von
  grundsätzlich 10.000 Euro ist nur ein Teil des geschützten
  Vermögens. Bei der nächsten Anpassung der Gesetze alle Angaben nachziehen.
- Das Einzugsgebiet umfasst die Landkreise Lörrach (35 Gemeinden) und
  Waldshut (32 Gemeinden), zusammen 67. Die vollständige Liste steht an genau
  einer Stelle im JSON-LD unter `areaServed`. Bei einer Gebietsänderung bitte
  anpassen. Die Zahl 67 steht zusätzlich im Fließtext von `index.html`,
  `betreuung.html` und `fachkreise.html`; die Kurzfassung ohne Zahl — nur die
  beiden Landkreisnamen — in `src/partials/rail.html`.
- Keine externen Schriften, Skripte oder Karten nachträglich einbauen. Die
  Datenschutzerklärung behauptet, dass es keine gibt — und die
  Content-Security-Policy in `src/partials/head.html` setzt das durch. Wer sie
  lockern muss, baut gerade etwas ein, das hier nicht hingehört.
- Das Vorschaubild `vorschau.png` zeigt noch den richtigen Anspruch. Es
  erscheint überall dort, wo jemand den Verweis weiterschickt, und wird aus
  `src/grafik/vorschau.svg` erzeugt: `tools/vorschau.sh`.
- `dist/sitemap.xml` ist aktuell erzeugt: `tools/build.sh`.
  `tools/sitemap.sh` zeigt sie zur Kontrolle auf stdout; `lastmod` wird als
  geprüfter Inhaltsstand in `src/seiten.json` gepflegt. Impressum und
  Datenschutz stehen bewusst nicht darin — beide tragen `noindex`, weil
  § 5 DDG Erreichbarkeit verlangt, nicht Auffindbarkeit.
- `public/bb-limen.vcf` stimmt mit dem JSON-LD der Startseite überein — Name,
  Telefonnummer, E-Mail, Anschrift und Website. `tests/test_angaben.py`
  prüft das mit, einschließlich der CRLF-Zeilenenden des Formats.
- Die Liste der offenen Platzhalter ist leer:

      grep -rn '\[[A-ZÄÖÜ]' -- src/pages/*.html src/partials/
