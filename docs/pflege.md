# Pflege von bb-limen.de

Wie das Repository funktioniert, worauf sich die Texte stützen und warum
einiges so ist, wie es ist. Die Handgriffe für häufige Änderungen stehen im
[README](../README.md), die verbindlichen Regeln in [AGENTS.md](../AGENTS.md).

## Aufbau

```text
src/pages/              Seiten als Quellen, mit Include-Zeilen statt Bausteinen
src/partials/           gemeinsame HTML-Bausteine: Kopf, Sprunglink, Kolumne, Fuß, Anrufleiste
src/style.css           ein Stylesheet; alle Farbwerte im Block PALETTE
src/grafik/             bearbeitbare SVG-Originale für Signet und Vorschaubild
src/seiten.json         Katalog: Seitenbestand, Sitemap, öffentliche Dateien
src/bureauangaben.json  Betreiber, Zentrale, E-Mail, Anschriften, Sprechzeiten
src/betreuende.json     die betreuenden Personen; je Eintrag ein Abschnitt in buero.html und eine vCard
src/betreuende/         Vorstellungstext und gegebenenfalls Porträt je Person
public/                 bewusst öffentliche Dateien, unverändert kopiert
dist/                   die Ausgabe: vollständig erzeugt, unversioniert
tools/                  Build, Prüfung, Bildexport, Verweisprüfung, Commit-Hook
tests/                  technische Tests
.github/                Workflows für Prüfung, Veröffentlichung, Verweise; Dependabot
docs/lokal/, reports/   persönliche Unterlagen und Berichte, unversioniert — können fehlen
```

`tools/build.sh` ruft `tools/build.py` auf und erzeugt `dist/`; ausgeliefert
wird ausschließlich dieser Ordner. Der Build braucht nur die
Python-Standardbibliothek, der Browser erhält ausschließlich statische
Dateien. Die öffentliche Adresse hängt am Namen in der Ausgabe:
`src/pages/betreuung.html` ist unter `/betreuung.html` erreichbar.

## Katalog und Includes

`src/seiten.json` enthält `pages` und `public_files`. Ein Seiteneintrag hat
`file` (flacher HTML-Dateiname), `sitemap` (bewusste Entscheidung über die
Aufnahme) und, nur für Sitemap-Seiten, `lastmod` als `YYYY-MM-DD`.

Jede Seite enthält genau diese Include-Zeilen, in dieser Reihenfolge und
jeweils allein auf einer Zeile:

```html
<!-- @include head -->
<!-- @include skip -->
<!-- @include rail -->
<!-- @include foot -->
<!-- @include callbar -->
```

In der Ausgabe umschließen die Marken `<!-- #rail -->` und `<!-- /#rail -->`
den eingesetzten Baustein. In `rail.html` markiert der Build über
`%%CUR-<seitenname>%%` den aktuellen Navigationspunkt.

## Büroangaben

`src/bureauangaben.json` ist die einzige Quelle für Telefon, E-Mail, Anschrift
und Sprechzeiten (R-ANGABEN-1). Der Build setzt die Werte ein und erzeugt die
Sprachfassungen der Sprechzeiten; die Datei selbst wird nicht veröffentlicht.

- `betreiber` hat den `name` der Person, die das Büro bereitstellt und für
  den Inhalt der Website verantwortlich ist. Er steht in `buero.html`, im
  Impressum und in der Datenschutzerklärung. Die Anbieter nach § 5 DDG kommen
  aus `src/betreuende.json`.
- `telefon` ist die Zentrale. `telefon.e164` ist die technische Nummer mit internationaler Vorwahl,
  `telefon.sichtbar` ihre lesbare Schreibweise; beide müssen dieselben Ziffern
  enthalten.
- `email` ist die Büroadresse, `email_datenschutz` die Adresse, die nur die
  Datenschutzerklärung nennt.
- `anschrift` hat `strasse`, `plz`, `ort`, `bundesland` und `land` (DE). Sie
  ist die Büroanschrift und steht nur im Impressum.
- `postanschrift` hat `postfach` (nur Ziffern), `plz`, `ort`, `bundesland` und
  `land` (DE). Sie steht überall, wo „Post“ steht, in der Datenschutzerklärung,
  im JSON-LD und in der Visitenkarte.
- `sprechzeiten.regulaer` hat `tage` als Liste deutscher Wochentage und `von`
  sowie `bis` als HH:MM; `nach_vereinbarung` nennt die Termintage. Beide Listen
  sind nicht leer. Die Reihenfolge der Tage bestimmt die Ausgabe. Geteilte oder
  je Wochentag verschiedene Zeiten brauchen eine Erweiterung von Datenformat
  und Sprachvorlagen.

Seiten verwenden Platzhalter wie `%%BUREAU:telefon.e164%%` oder
`%%BUREAU:anschrift.strasse%%`. Die Sprechzeiten gibt es in drei Fassungen:
`sprechzeiten.kurz` für die Kolumne, `sprechzeiten.text` für den Fließtext und
`sprechzeiten.leicht` für die Leichte Sprache. Im JSON-LD steht ein
vollständiger String wie `"%%BUREAU_JSON:telefon.e164%%"`. Der Build maskiert
die Werte passend für HTML, JSON und vCard. Fehlende Felder, unbekannte
Schlüssel und nicht aufgelöste Platzhalter brechen ihn vor dem Schreiben ab.

`dist/bb-limen.vcf` entsteht aus dem erzeugten Organization-Knoten der
Startseite (R-ANGABEN-6); Name und Websiteadresse sind dort redaktionell
festgelegt, die Kontaktwerte kommen aus den Büroangaben. Alle Visitenkarten
sind UTF-8 mit CRLF-Zeilenenden und nach 75 Bytes gefaltet.

## Betreuende Personen

Die Bürogemeinschaft vermietet an selbständige Berufsbetreuer; Registrierung,
Haftpflicht und Verantwortung liegen bei jeder Person einzeln. Deshalb hat
jede Person einen eigenen Abschnitt auf `buero.html` und eine eigene
Visitenkarte, und die Website wächst mit einem Datensatz statt mit einem
Umbau. Eigene Seiten je Person gibt es vorerst nicht.

Ein Eintrag in `src/betreuende.json` hat genau diese Felder:

- `kennung` — Name in ASCII-Kleinbuchstaben mit Bindestrichen (ä → ae,
  ß → ss). Sie ist die Sprungmarke `buero.html#<kennung>` und bestimmt
  `<kennung>.vcf` und den Vorstellungstext `src/betreuende/<kennung>.html`.
- `name`, `beruf` — wie im Personenabschnitt und im Impressum.
- `registrierung` — die kurze Standzeile, wörtlich im Personenabschnitt und
  im Impressum.
- `haftpflicht` — Versicherer und Vertragsnummer; wird derzeit auf keiner
  Seite ausgegeben.
- `telefon` — `null` oder `e164` und `sichtbar` wie bei den Büroangaben; eine
  eigene Nummer erscheint im Personenabschnitt als „Direkt", die vCard nennt
  zusätzlich die Zentrale.
- `email` — `null` oder eine eigene Adresse; sonst gilt die des Büros.
- `anschrift` — `null` oder die Anschrift als einzeiliger Text; erscheint im
  Personenabschnitt als „Post“ und ersetzt in der persönlichen Visitenkarte
  die Postanschrift des Büros.
- `bild` — `null` oder der Dateiname eines Porträts `<kennung>.jpg`, `.webp`
  oder `.png` in `src/betreuende/`; der Build kopiert es in die Ausgabe. Die
  Karte schneidet es auf 3:4 (Hochformat) zu, das Gesicht im oberen Drittel; 600 × 800
  Pixel genügen. Ohne Foto zeigt die Karte einen gezeichneten Platzhalter.

Der Vorstellungstext ist ein HTML-Ausschnitt ohne Platzhalter; er gehört dem
Büro und wird unverändert eingesetzt (R-REDAKTION-1). Die Seiten beziehen die
Personenangaben über Platzhalter: `%%BETREUENDE:personen%%` (Abschnitte in
`buero.html`), `%%BETREUENDE:anbieter%%` (Name, Beruf und Registrierung je
Person im Impressum), `%%BETREUENDE:namen%%` (die Namen als Aufzählung in der
Datenschutzerklärung), `"%%BETREUENDE_JSON:personen%%"` (JSON-LD `member` der
Startseite). Eine Änderung in `src/betreuende.json` ändert deshalb
`buero.html` und die Pflichtseiten; nachgezogen werden das `lastmod` von
`buero.html` und das sichtbare Datum der betroffenen Pflichtseite
(R-ANGABEN-5).

## Verhalten des Builds

`tools/build.py` ist der ganze Build. Bevor er schreibt, prüft er, was eine
Seite technisch zerstören würde: Aufbau der JSON-Dateien, Dateibestand,
Include-Reihenfolge, Platzhalter, Telefon- und E-Mail-Ziele. Ob eine Angabe
inhaltlich stimmt, prüft er nicht (R-REDAKTION-3). Dateien in `src/pages/`,
`src/partials/`, `src/betreuende/` oder `public/`, die nicht eingetragen sind,
führen zum Fehler. Er erzeugt erst ein vollständiges Arbeitsverzeichnis und
ersetzt dann `dist/`; bei fehlerhaften Eingaben bleibt die letzte Ausgabe
erhalten. Ein anderes vorhandenes Verzeichnis ersetzt er nie. Bei einem
Buildfehler die genannte Quelldatei und Zeile bearbeiten.

GitHub Pages liefert `404.html` für jede unbekannte Adresse aus, auch für
`/ein/tiefer/pfad/`. Der Build setzt deshalb in dieser einen Seite alle
relativen Dateiverweise an die Domainwurzel (`/style.css`, `/index.html`); der
Sprunglink `#inhalt` bleibt auf der Fehlerseite. Lokal lässt sie sich nur über
einen Server ansehen, nicht als Datei.

## Prüfkette

`tools/pruefen.sh` ist der gemeinsame Einstieg für Menschen, Commit-Hook und
CI: Er baut in ein temporäres Verzeichnis, führt die Tests aus und räumt auf.

**Geprüft wird Technik, nie Inhalt** (R-REDAKTION-3). Kein Test kennt einen
Wortlaut, eine Zahl oder eine Büroangabe der Website; eine Änderung an Text,
Sprechzeiten oder Telefonnummer kann deshalb nichts rot machen. Rot wird es,
wenn etwas kaputt ist: ein Verweis ohne Ziel, ein falsch geschriebener
Platzhalter, ungültiges JSON-LD, ein beschädigtes Werkzeug.

`tests/test_site.py` prüft die frisch erzeugte Website: Verweise,
Sprungmarken, Überschriftenfolge, Kopfangaben, CSP, Pflichtverweise und
`noindex`; dass keine Büro- oder Personenangabe wörtlich in einer Quelle
steht; und WCAG AA für jede Textpaarung, hell und dunkel. Die
Werkzeuge selbst haben keine eigenen Tests: Der Build prüft seine
Eingaben vor dem Schreiben (siehe oben), und was er ausgibt, prüfen die Tests
der Seiten. Wer `tools/` ändert, sieht das Ergebnis deshalb selbst an.

**Vor jedem Commit** läuft nach `tools/einrichten.sh` derselbe Befehl als Hook;
geprüft wird der Arbeitsbaum. **Bei jedem Pull Request und auf `main`** führt
`.github/workflows/website.yml` ihn aus und validiert danach das fertige HTML;
ein Zweig ohne Pull Request wird nicht geprüft. **Einmal im Monat** ruft
`.github/workflows/verweise.yml` mit `tools/verweise-pruefen.sh` die Verweise
nach außen ab; ein toter Verweis macht den Lauf rot, und GitHub meldet das per
E-Mail. Das Skript läuft genauso lokal. In einem öffentlichen Repository
schaltet GitHub geplante Läufe nach 60 Tagen ohne Aktivität ab; dann unter
Actions → „Verweise nach außen" wieder einschalten.

### HTML-Validierung

Die CI führt `html5validator --config tools/html5validator.yml` auf `dist/`
aus, in der festen Version 0.4.2. Alle Fehler und Warnungen blockieren,
ausgenommen drei genau bezeichnete Befunde:

- Beim Prüfen lokaler Dateien fehlt die Web-Origin für `'self'`; ausgenommen
  ist nur die Meldung über das eigene `style.css`
  ([Erläuterung des Maintainers](https://github.com/validator/validator/issues/2062#issuecomment-4173094350)).
- Der JSON-LD-Block der Startseite wird irrtümlich wie JavaScript gemeldet;
  `application/ld+json` ist nach dem
  [HTML-Standard](https://html.spec.whatwg.org/multipage/scripting.html#data-block)
  ein Datenblock.
- Der gebündelte Prüfstand kennt `media` auf `meta name="theme-color"` nicht,
  obwohl der
  [HTML-Standard](https://html.spec.whatwg.org/multipage/semantics.html#meta-theme-color)
  es erlaubt.

Die Gegenkontrollen in `tests/test_site.py` verlangen genau einen lokalen
Stylesheet-Verweis, als einzigen Script-Tag den JSON-LD-Block der Startseite,
die unveränderten CSP-Direktiven und genau die zwei `theme-color`-Elemente.

Gewechselt wird der Validator, sobald eine vierte Ausnahme nötig würde oder
das Paket auf einem neuen CI-Läufer ausfällt — dann auf das npm-Paket
`vnu-jar` in fester Version. Python ist in der CI auf 3.12 festgelegt.

## Bilder neu erzeugen

Vorschaubild und die beiden Symbole entstehen aus den SVG-Quellen in
`src/grafik/` und liegen fertig in `public/`, damit der Build keinen Browser
braucht. Die SVG-Quellen tragen die Farben der Palette als feste Werte (siehe
„Gestaltung"); nach jeder Änderung an ihnen:

```sh
tools/bilder-erzeugen.sh
```

Das Skript braucht Chromium oder Chrome. Es rendert in ein Arbeitsverzeichnis,
prüft die Maße und ersetzt `public/` erst danach.

## Eine Seite hinzufügen

Sachbezogener Name nach R-BESTAND-2, Quelle unter `src/pages/` mit den fünf
Include-Zeilen, Katalogeintrag und eine bewusste Navigationsentscheidung.
Titel, `description`, `canonical` und `og:`-Angaben bleiben in der Seite
(R-QUELLE-2). Eine neue öffentliche Kopierdatei gehört nach `public/` und in
`public_files`.

## Schreiben

Die Seite hat vier Sprachebenen (R-SPRACHE-1):

- **`leichte-sprache.html`** — Leichte Sprache: kurze Sätze, ein Satz je Zeile,
  Binde-Striche in zusammengesetzten Wörtern, schwere Wörter erklärt. Eigene
  Typografie über `body class="ls"`.
- **`fachkreise.html`** — Fachsprache; Genauigkeit vor Einfachheit. Das
  Sprungmenü oben muss zu den `id`-Attributen der Überschriften passen.
- **`index.html`, `betreuung.html`, `aufgaben.html`, `vorsorge.html` und
  `buero.html`** —
  Einfache Sprache (etwa A2 bis B1): kurze Sätze, aktiv, Verben statt
  Substantivierungen, Fachwörter bei der ersten Nennung erklärt.
- **`impressum.html`, `datenschutz.html`** — juristisches Standarddeutsch. Eine
  vereinfachte Datenschutzerklärung wird schnell unvollständig, und
  Unvollständigkeit ist der teurere Fehler.

**Prüfung der Leichten Sprache.** Nach dem Standard des Netzwerks Leichte
Sprache gehört ein Text von einer Prüfgruppe aus Menschen mit
Lernschwierigkeiten gegengelesen, bevor er als Leichte Sprache gilt. Das steht
aus (R-SPRACHE-2). Lebenshilfe und Diakonie vermitteln Prüfgruppen; die
Betreuungsbehörde weiß meist, wer es vor Ort macht.

**Verweise nach außen.** `vorsorge.html` und `leichte-sprache.html` verweisen
auf Ministerien, Behörden, Bundesnotarkammer, Lebenshilfe und KVJS. Fremde
Formulare werden verlinkt, nicht gehostet (R-VERBOT-2): Ein Vordruck veraltet
mit dem Gesetz. Bei jeder Angabe steht der Stand des Dokuments. Die monatliche
Prüfung sieht nur, ob eine Adresse erreichbar ist — nicht, ob der genannte
Stand noch stimmt. Deshalb **zweimal im Jahr von Hand prüfen** und bei einer
Änderung Adresse und Standangabe gemeinsam nachziehen.

**Externe Profile.** Laut Betreiberangabe vom 20.09.2026 bestehen keine
öffentlichen Profile für BB Limen, Aranda Möller oder Mika Möller; deshalb gibt
es keine Profil-Links und kein `sameAs`.

## Rechtsstände und Wiedervorlagen

Worauf sich die Texte stützen. Vor jeder Änderung gilt R-RECHT-1: nachschlagen,
nicht aus dem Gedächtnis schreiben.

**Registrierungen.** Beide Personen sind freiberuflich und einzeln
registrierungspflichtig (§ 23 BtOG, personenbezogen, nicht bürobezogen).
Solange eine Registrierung fehlt, darf die betreffende Person keine berufliche
Betreuung führen. Welche Stellen bei der Erteilung zu ändern sind, steht im
[README](../README.md#registrierung-eintragen).

**Berufshaftpflicht.** Zwei getrennte Verträge, je einer pro Person
(§ 23 Abs. 1 Nr. 3 BtOG), eingetragen in `src/betreuende.json`. Das
Impressum nennt sie nicht: Die Angaben gehen an die Stammbehörde, das hat
das Büro am 24.09.2026 entschieden.

**Anbieter.** Diensteanbieter nach § 5 DDG sind alle Personen aus
`src/betreuende.json`, jede freiberuflich und unabhängig von den anderen, ohne
Eintragung im Handelsregister und ohne Umsatzsteuer- oder
Wirtschafts-Identifikationsnummer; wer aufgenommen wird, steht damit auch als
Anbieter im Impressum. Für den Inhalt verantwortlich ist der Betreiber aus
`src/bureauangaben.json`. Das Impressum nennt ihn ohne Verweis auf § 18 Abs. 2
MStV, denn die Vorschrift gilt nur für journalistisch-redaktionell gestaltete
Angebote. Die Datenschutzerklärung nennt alle Personen als gemeinsam
Verantwortliche nach Art. 26 DSGVO; der Betreiber übernimmt die
Informationspflichten und die Anfragen. Das Impressum nennt die Stammbehörde
als Aufsichtsbehörde, weil die Registrierung nach § 24 BtOG als behördliche
Zulassung im Sinne von § 5 Abs. 1 Nr. 3 DDG behandelt wird. All das hat das
Büro am 25.09.2026 so entschieden. Eine UG (haftungsbeschränkt) ist nicht gegründet; nach § 11
Abs. 1 GmbHG besteht sie vor der Eintragung nicht und darf deshalb nicht als
Anbieterin stehen.

**Bürogemeinschaft — Wiedervorlage.** Vor der Veröffentlichung klären: ob
die DL-InfoV für berufliche Betreuer gilt und damit Angaben zur
Berufshaftpflicht (§ 2 Abs. 1 Nr. 11 DL-InfoV: Versicherer, Anschrift,
räumlicher Geltungsbereich) nötig werden, die Ausnahme in Art. 2 Abs. 2 lit. j
der Richtlinie 2006/123/EG spricht womöglich dagegen; ob der Satz zur
unabhängigen Tätigkeit im Impressum den Anschein einer Gesellschaft
ausschließt; und wie die Betreuungsbehörde die Bürogemeinschaft einordnet.

**Vergütung.** Maßgeblich ist das zum 1. Januar 2026 geänderte VBVG: sechzehn
reguläre Fallpauschalen von 98 bis 427 Euro in der Anlage zu § 8 Abs. 1 VBVG
(Fundstelle BGBl. 2025 I Nr. 109); die Bemessung regelt § 9 VBVG.
`aufgaben.html` nennt feste Monatspauschalen und einen Mittelwert. Der
Mittelwert ist eine redaktionelle Angabe des Büros; er stützt sich nach dessen
Angabe vom 21.09.2026 auf Erhebungen und ist nicht aus der Anlage errechnet
(R-REDAKTION-1, R-REDAKTION-2). `fachkreise.html` nennt die seit 1. Januar 2026
geltende Fassung und die Vergütung nach Zeitaufwand für Sterilisations- und
Ergänzungsbetreuer (§ 11 Abs. 1 in Verbindung mit § 3 VBVG). Der Geldbetrag von
grundsätzlich 10.000 Euro ist nur ein Teil des geschützten Vermögens.

**Ärztliche Zwangsmaßnahmen — Wiedervorlage.** Der Krankenhausvorbehalt in
§ 1832 Abs. 1 Satz 1 Nr. 7 BGB ist nach dem Beschluss des
Bundesverfassungsgerichts vom 26.11.2024 (1 BvL 1/24) mit dem Grundgesetz
unvereinbar. Das bisherige Recht gilt fort, bis der Gesetzgeber neu regelt; die
Frist dafür endet am 31.12.2026 (amtliche Fußnote zu § 1832 BGB, nachgeschlagen
am 21.09.2026). Sobald die Neuregelung in Kraft tritt, die Aussagen zu § 1832
BGB in `fachkreise.html` und zu § 1820 Abs. 2 BGB samt Formularhinweis in
`vorsorge.html` neu nachschlagen (R-RECHT-4).

**Gemeinsame Verantwortung.** Die veröffentlichte Aufgabenverteilung nach
Art. 26 DSGVO entspricht der tatsächlichen Vereinbarung: Aranda Möller
übernimmt für die gemeinsame Website die Informationspflichten, die Bearbeitung
von Betroffenenanfragen und die Koordination von Hosting beziehungsweise
technischem Betrieb. Änderungen immer zugleich in der Vereinbarung und in
`datenschutz.html` nachziehen.

**Einzugsgebiet.** Landkreise Lörrach (35 Gemeinden) und Waldshut
(32 Gemeinden), zusammen 67. Die vollständige Liste steht an genau einer Stelle:
im JSON-LD der Startseite unter `areaServed` (R-ANGABEN-2). Die Kurzfassung mit
den beiden Landkreisnamen steht in `src/partials/rail.html`.

## Gestaltung

Die Farben benennen Funktionen, nicht Seiten. Die Werte stehen im Block
PALETTE in `src/style.css` (R-FARBE-1).

- **Gold** (`--accent`, `--accent-on-carrier`) — Ordnung: Rubriken, Ziffern,
  Zierlinien, aktueller Standort und die primäre Aktion „Anrufen". In der
  Navigation zeigt zusätzlich eine Linie den Standort; Farbe allein trägt diese
  Information nicht.
- **Stahlblau** (`--link-ink`, `--link-on-carrier`) — Bedienung: alles
  Anklickbare, dunkel auf Papier und hell auf Graphit. Fließtext-, Kontakt- und
  Rechtsverweise bleiben zusätzlich unterstrichen.
- **Warmes Steingrau** (`--meta-on-carrier`) — nicht anklickbare Nebenangaben in
  der Kolumne, damit statischer Text nicht wie ein Verweis aussieht.
- **Salbei** (`--gut`) — Entlastung, im Fließtext nur im Block `.gut` und nur
  dort, wo die Nachricht wirklich entlastet (R-FARBE-2). `--st-2` der
  Leichte-Sprache-Liste hat denselben Wert.
- **Papierwärme** (`--paper`, `--surface`) — eine Temperatur, keine sichtbare
  Farbe: `#fbfaf7` statt neutralem Grau.
- **Mint** (`--brand-leaf`) — nur die Blattkontur des Signets; Markenfarbe,
  keine Bedienfarbe.
- **Terrakotta** (`--leicht-ink`) und `--st-1` bis `--st-5` — nur auf der
  Leichte-Sprache-Seite; Farbe hilft dort beim Wiederfinden.

Einige Stellen können den Block PALETTE nicht lesen und tragen seine Werte
als Kopie: `theme-color` in `src/partials/head.html` (`--paper`, hell und
dunkel) und die SVG-Quellen in `src/grafik/` für Signet und Vorschaubild. Wer
die Palette ändert, zieht diese Kopien nach und erzeugt die Bilder neu. Das
Favicon als Datei-URI in `head.html` hat einen eigenen Farbton, der zu keiner
Variablen gehört. Der Druck hat im Block PALETTE einen eigenen Satz in Schwarz
und Weiß.

Das Zierzeichen zwischen den Haarlinien ist dasselbe Blatt wie die Marke der
Kolumne, als SVG (`.zierblatt`). Auf schmalen Bildschirmen wird aus der
Kolumne ein Kopfband, die Anrufleiste steht unten; deshalb gehört die schmale
Ansicht zu jeder Sichtprüfung (R-PRUEFUNG-2).

## Veröffentlichen

Kanonische Adresse ist `https://bb-limen.de/`, das Repository
<https://github.com/Aimergentix/bb-limen.de>.
`.github/workflows/website.yml` läuft bei jedem Push nach `main`: Er prüft,
baut `dist/`, lädt genau diesen Ordner als Pages-Artefakt hoch und
veröffentlicht ihn. Schlägt die Prüfung fehl, bleibt
die bisherige Fassung online.

Bei GitHub ist dazu eingerichtet: Pages-Quelle „GitHub Actions", eigene Domain
mit „Enforce HTTPS" und ein Schutz für `main` — Pull Request und die
Statusprüfung `pruefung` sind Pflicht, erzwungene Pushes gesperrt. Wer die
Regel neu anlegt: GitHub bietet nur Checks an, die schon einmal auf einem Pull
Request liefen; gesucht wird der Job-Name `pruefung`.

Vor einer Veröffentlichung von Hand ansehen, was kein Test sehen kann: die
Standdaten (R-ANGABEN-5), die Rechtsstände oben, das Vorschaubild und die
Seiten selbst — breit, schmal und dunkel.

Danach:

```sh
gh run list --limit 3                                   # Lauf grün?
curl -sI https://bb-limen.de/ | head -1                 # 200 über HTTPS
curl -sI http://bb-limen.de/ | grep -i '^location'      # leitet auf https um
curl -s -o /dev/null -w '%{http_code}\n' https://bb-limen.de/gibt-es-nicht.html   # 404
curl -s -o /dev/null -w '%{http_code}\n' https://bb-limen.de/AGENTS.md            # 404: Quellen nicht ausgeliefert
```

Dependabot schlägt einmal im Monat neue Versionen der GitHub Actions als einen
gebündelten Pull Request vor. Die Pages-Actions laufen nur auf `main`; nach dem
Übernehmen den nächsten Veröffentlichungslauf ansehen.

## Entscheidungen in Kürze

Warum etwas so ist, in je einem Satz.

- **Kein JavaScript, keine fremden Ressourcen.** `datenschutz.html` behauptet,
  dass es nichts davon gibt; jede Einbindung macht sie unwahr (R-VERBOT-1).
- **Kein Fallbeispiel, kein Zitat, keine Bewertung.** Auch eine anonymisierte
  Schilderung berührt die Verschwiegenheit (R-VERBOT-4).
- **Keine Ortsseiten, kein `LocalBusiness`.** Die Anschrift ist eine
  angemietete, nicht ständig besetzte Geschäftsadresse; `Organization` mit
  `PostalAddress` nennt sie, ohne einen Standort mit Publikumsverkehr zu
  behaupten. Aus demselben Grund wäre ein Eintrag bei einem Kartendienst ein
  Risiko (R-VERBOT-5, R-VERBOT-6).
- **Kein Hell-/Dunkel-Schalter.** Ohne JavaScript ließe sich die Wahl nicht
  über alle Seiten halten; die Darstellung folgt `prefers-color-scheme`.
- **Das Ornament ist ein SVG.** Zeichen wie U+2766 fehlen in den
  Serifenschriften; der Browser zeigte auf jedem Gerät etwas anderes
  (R-VERBOT-3).
- **Die Adressen bleiben bei `.html`**, damit bestehende Verweise gelten
  (R-BESTAND-2).
- **Personenabschnitte aus Daten.** Bei vier bis acht Personen, die kommen und
  gehen, wäre jeder handgeschriebene Abschnitt eine weitere Stelle für dieselbe
  Angabe (R-ORDNUNG-1).
- **Pflichtseiten tragen `noindex`.** § 5 DDG verlangt Erreichbarkeit, nicht
  Auffindbarkeit (R-BESTAND-4).
- **Quellen und Ausgabe sind getrennt.** Früher schrieb der Build Bausteine in
  dieselben Dateien; eine Änderung zwischen den Marken verschwand beim nächsten
  Build (R-QUELLE-1).
- **Kein maschineller Bildvergleich.** Zu viel Werkzeugkette für eine Website,
  deren Layout sich selten ändert; die Sichtprüfung bleibt Handarbeit
  (R-PRUEFUNG-2).
- **Die Fehlerseite kommt ohne `base` aus.** Das Element lenkte auch „Zum
  Inhalt springen" auf die Startseite um.
- **Keine Inhaltsprüfungen.** Tests, die Gemeinden zählen oder Satzlängen
  messen, halten nur redaktionelle Änderungen auf; die Texte verantwortet das
  Büro (R-REDAKTION-3).
