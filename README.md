# bb-limen.de — statische Website

Neun Seiten, ein Stylesheet, keine Abhängigkeiten, keine externen Ressourcen,
kein JavaScript. Was im Browser ankommt, ist genau das, was hier im
Verzeichnis liegt.

> **Wer hier etwas ändert — Mensch oder Sprachmodell — liest zuerst
> [`AGENTS.md`](AGENTS.md).** Dort stehen die Regeln in kurzer, prüfbarer
> Form. Dieses README erklärt sie: es ist das Handbuch, `AGENTS.md` ist der
> Vertrag.

    index.html        BB Limen, Exkurs zum Namen, Haltung nach § 1821 BGB, Kontakt
    betreuung.html    Betreuung, Einordnung, Verfahren und Einzugsgebiet
    aufgaben.html     Aufgabenbereiche, Ablauf, Kosten
    vorsorge.html     Vollmacht, Betreuungs- und Patientenverfügung
    fachkreise.html   Fachsprache: Gerichte, Behörden, Kliniken, Ärzte
    leichte-sprache.html  dieselben Inhalte in Leichter Sprache

    impressum.html    Pflichtangaben nach § 5 DDG
    datenschutz.html  Information nach Art. 13 DSGVO
    404.html          Fehlerseite, nicht in der sitemap.xml
    style.css         gemeinsames Stylesheet
    vorschau.png      Vorschaubild für geteilte Verweise (Open Graph)
    favicon.ico       Symbol in der Browserleiste
    apple-touch-icon.png  Symbol auf dem iOS-Startbildschirm
    robots.txt        Indexierungsregeln
    sitemap.xml       Seitenverzeichnis für Suchmaschinen
    CNAME             die kanonische Domain für GitHub Pages
    _config.yml       was GitHub Pages **nicht** ausliefert

    AGENTS.md         Arbeitsregeln für Mensch und Modell — erst lesen
    CLAUDE.md         Einzeiler, der auf AGENTS.md verweist

    partials/         die Bausteine, die auf jeder Seite gleich sind
    tools/build.sh    setzt diese Bausteine in die neun Seiten ein
    tools/schau.sh    rendert Bildschirmfotos mit Chromium
    tools/pruefe-sprache.py  misst die Satzlänge im Fließtext
    tools/sitemap.sh  schreibt sitemap.xml aus der Git-Historie
    tools/vorschau.sh rendert Vorschaubild und Symbole aus zwei SVG
    tools/ansicht.sh  rendert alle Seiten in einen Ordner
    tools/vergleiche.py  vergleicht zwei solche Ordner Bild für Bild
    tools/hooks/      läuft vor jedem Commit — tools/einrichten.sh schaltet es an
    tests/            Regressionstests: Build, Sprache, Struktur, Angaben,
                      Begriffe, Kontraste
    docs/             Quellenmaterial, grösstenteils unversioniert
    .github/          die Prüfungen, die bei jedem Push laufen
    LICENSE           alle Rechte vorbehalten
    .editorconfig     UTF-8, LF, zwei Leerzeichen

Zwei Schranken, die nicht dasselbe tun: `.gitignore` hält Dateien aus der
**Versionierung**, `_config.yml` hält versionierte Dateien aus der
**Auslieferung**. `partials/`, `tools/` und `tests/` liegen im Repository,
aber nicht im Netz.

## 1. Gemeinsame Bausteine ändern

Kolumne, Navigation, Telefonnummer, Anschrift, Seitenfuß und Anrufleiste
stehen **nur** in `partials/`. Die neun Seiten enthalten Kopien davon
zwischen Marken wie

    <!-- #rail -->   … generierter Inhalt …   <!-- /#rail -->

Also: in `partials/` ändern, dann

    tools/build.sh

Das Skript überschreibt ausschließlich den Bereich zwischen den Marken und
setzt `aria-current="page"` auf den jeweils eigenen Navigationspunkt. Vor dem
Schreiben prüft es alle Seiten, Marken und Partials. Alle Ergebnisse entstehen
zuerst in einem Arbeitsverzeichnis; ein Fehler an einer späteren Seite lässt
die Originaldateien unverändert. Benötigt werden nur übliche Unix-Werkzeuge
(`sh`, `awk`, `sed`, `grep`, `cmp`, `mktemp`, `cp`, `mv`, `rm`). Die Seiten bleiben dabei
vollständiges HTML und lassen sich jederzeit direkt im Browser öffnen — der
Build ist kein Zwischenschritt, sondern nur ein Abgleich.

Seitentitel, Beschreibung und `canonical` stehen dagegen einzeln in jeder
Seite, weil sie sich unterscheiden.

Die öffentlichen Adressen bleiben klassische `.html`-Adressen. Der Dateiname
bezeichnet das eindeutige Sachthema der Seite in Kleinbuchstaben; mehrere
Wörter werden mit Bindestrichen verbunden. Menütexte dürfen eine grammatische
Ergänzung enthalten, aber kein anderes Sachthema verwenden. `index.html` ist
die technische Startdatei für die öffentliche Adresse `https://bb-limen.de/`.

## 2. Noch offen

Suche in den ausgelieferten HTML-Dateien und Partials nach `[` — solange dort
etwas gefunden wird, ist die Seite nicht veröffentlichungsfertig:

    rg -n '\[[A-ZÄÖÜ]' -- *.html partials/*.html

Offen sind:

**Im Impressum** (zwei Angaben, beide brauchen eine Entscheidung):

- **Umsatzsteuer.** Entweder eine USt-IdNr. nach § 27a UStG, oder der
  Hinweis auf § 19 UStG (Kleinunternehmer). Für Betreuungsleistungen ist
  zusätzlich § 4 Nr. 16 UStG einschlägig — das bitte mit dem Steuerbüro
  klären und dann genau eine der Varianten eintragen.
- **Berufshaftpflichtversicherung.** Versicherer und Anschrift. Die
  Versicherung ist ohnehin Voraussetzung der Registrierung nach
  § 23 Abs. 1 Nr. 3 BtOG.

**Büro-Telefon** — BB Limen veröffentlicht genau eine gemeinsame Nummer und
ordnet sie keiner einzelnen Person zu. Die maßgeblichen Stellen für Kolumne
und mobile Anrufleiste liegen in `partials/rail.html` und
`partials/callbar.html`; nach dem Build stehen deren Kopien in allen neun
Seiten. Zusätzliche direkte Kontaktangaben gibt es in `index.html`,
`fachkreise.html`, `leichte-sprache.html`, `impressum.html` und
`datenschutz.html`. Eine zweite persönliche Telefonnummer und ein leeres
`href="tel:"` dürfen nicht hinzukommen.

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

    grep -ho 'href="https\?://[^"]*"' *.html | sed 's/href="//;s/"$//' \
      | grep -v bb-limen.de | sed 's/&amp;/\&/g' | sort -u \
      | while read u; do echo "$(curl -sLo /dev/null -w '%{http_code}' "$u")  $u"; done

Ändert eine Stelle den Stand ihres Dokuments, die Angabe auf der Seite
mitziehen — sonst steht dort eine Jahreszahl, die nicht mehr gilt.

## 2b. Sprachebenen

Die Seite hat drei Sprachebenen. Wer Text ändert, sollte wissen, auf
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
zwei SVG-Quellen in `tools/` und sind versioniert, damit die Website ohne
Werkzeugkette auslieferbar bleibt. Nach einer Änderung an Signet oder
Palette neu rendern:

    tools/vorschau.sh

## 2c. Farbe

Die Farben benennen Funktionen, nicht einzelne Seiten. Alle Werte stehen im
Block PALETTE in `style.css`; ein Rückbau ist immer dieser eine Block, nie
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
dasselbe Blatt wie die Marke der Kolumne (`.zierblatt`, siehe `style.css`).
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

    python3 -m http.server 8000

Dann `http://localhost:8000` öffnen. Für Bilder zum Nachsehen:

    tools/schau.sh index.html 1280 1500 start          # hell
    tools/schau.sh index.html 390 1400 start-mobil     # Telefon
    tools/schau.sh index.html 1280 1500 start-d dunkel # Dunkelmodus

Das legt PNG unter `~/bb-shots` ab; der Server muss auf Port 8391 laufen.
Chromium im Snap darf nicht nach `/tmp` schreiben — deshalb der Home-Pfad. Unbedingt auch am Telefon ansehen: dort
wird aus der stehenden Kolumne ein schmales Kopfband, und der Kontakt steht
in der festen Anrufleiste am unteren Rand.

## 3a. Was von selbst läuft

Drei Ebenen, von früh nach spät:

**Vor jedem Commit** — einmalig einschalten mit

    tools/einrichten.sh

Danach setzt `tools/hooks/pre-commit` die Bausteine ein, merkt eine dabei
berichtigte Seite gleich mit vor, lässt die Tests laufen und misst die
Satzlängen. Wer `partials/` ändert und `tools/build.sh` vergisst, merkt es
hier statt zwei Tage später. Notausgang: `git commit --no-verify` — dann
fällt es in der CI auf.

**Bei jedem Push** (`.github/workflows/pruefung.yml`), drei Aufgaben:

- dieselben Prüfungen wie der Hook, dazu der Abgleich, dass die Seiten
  wirklich zu `partials/` passen,
- **HTML-Validierung** der neun Seiten mit dem W3C-Validator,
- **Bildvergleich**: der Stand vor und nach dem Push wird gerendert und Bild
  für Bild verglichen. Das Ergebnis steht in der Zusammenfassung des Laufs,
  die Bilder liegen vierzehn Tage als Artefakt bereit. Er bricht nie ab — er
  zeigt nur, was sich in der Ansicht geändert hat, auch das Unbeabsichtigte.

  Verglichen wird gegen den Vorgängerstand, nicht gegen hinterlegte
  Vorlagenbilder. Beide Stände entstehen dadurch in derselben Umgebung;
  Vorlagen von einem anderen Rechner wären wegen Schriftglättung und
  Chromium-Fassung wertlos.

Dasselbe lässt sich lokal machen — nützlich vor einer größeren Änderung am
Stylesheet:

    tools/ansicht.sh ~/bb-shots/vorher
    …Änderung…
    tools/ansicht.sh ~/bb-shots/nachher
    tools/vergleiche.py ~/bb-shots/vorher ~/bb-shots/nachher ~/bb-shots/diff

**Einmal im Monat** (`.github/workflows/verweise.yml`) werden die zwölf
Verweise nach außen abgerufen. Ist einer tot, entsteht ein Issue. Das
ersetzt die halbjährliche Handarbeit aus Abschnitt 2a — aber nur deren
mechanischen Teil: ob der genannte **Stand** eines Dokuments noch stimmt,
sieht kein Abruf.

## 4. Bei GitHub Pages veröffentlichen

Kanonische Adresse ist `https://bb-limen.de/`. Ausgeliefert wird der Branch
`main` aus <https://github.com/Aimergentix/bb-limen.de>.

1. **Pages einschalten.** Im Repository unter **Settings → Pages**:
   *Source* = „Deploy from a branch", *Branch* = `main`, *Folder* = `/ (root)`.
   Ein Push nach `main` veröffentlicht danach automatisch.

2. **Was ausgeliefert wird**, steuert `_config.yml`. Pages veröffentlicht
   sonst alles, was im Branch liegt — auch `tools/`, `tests/` und die
   Bausteine aus `partials/`. Letztere sind kein vollständiges HTML; einzeln
   aufgerufen ergäben sie ein kaputtes Dokument mit der vollen Anschrift.
   Die `exclude`-Liste verhindert das.

   **Kein `.nojekyll` anlegen.** Das schaltet Jekyll ab und hebt damit genau
   diesen Ausschluss wieder auf. Die Seiten enthalten keine Liquid-Syntax,
   Jekyll reicht sie also unverändert durch.

3. **Eigene Domain.** Die Datei `CNAME` im Wurzelverzeichnis enthält die
   kanonische Domain (`bb-limen.de`) und wird von Pages ausgewertet. Bei
   inwx einzutragen:

       bb-limen.de      A      185.199.108.153
       bb-limen.de      A      185.199.109.153
       bb-limen.de      A      185.199.110.153
       bb-limen.de      A      185.199.111.153
       bb-limen.de      AAAA   2606:50c0:8000::153
       bb-limen.de      AAAA   2606:50c0:8001::153
       bb-limen.de      AAAA   2606:50c0:8002::153
       bb-limen.de      AAAA   2606:50c0:8003::153
       www.bb-limen.de  CNAME  aimergentix.github.io.

   Eine eigene Weiterleitungsdatei für `www` wird nicht gebraucht: Pages
   leitet die nicht-kanonische der beiden Varianten selbst auf die im
   `CNAME` stehende um, sobald beide DNS-Einträge stehen.

   Die MX- und TXT-Einträge für mailbox.org bleiben unverändert. Falls
   CAA-Einträge gesetzt sind, muss `letsencrypt.org` darin erlaubt sein.

4. **HTTPS.** Nach erfolgreicher DNS-Prüfung unter **Settings → Pages** den
   Haken bei *Enforce HTTPS* setzen. Das Zertifikat holt GitHub selbst über
   Let's Encrypt; bis es ausgestellt ist, können einige Minuten vergehen.

5. **Die IP-Adressen und das Verfahren vor der Einrichtung gegenlesen** — sie
   ändern sich selten, aber sie ändern sich:

   <https://docs.github.com/pages/configuring-a-custom-domain-for-your-github-pages-site>

6. **Danach einmal prüfen**, dass die Werkstatt nicht mit im Netz steht:

       curl -sI https://bb-limen.de/tools/build.sh      # muss 404 sein
       curl -sI https://bb-limen.de/partials/rail.html  # muss 404 sein
       curl -sI https://www.bb-limen.de/                # muss auf bb-limen.de umleiten

## 5. Vor dem Onlinegehen prüfen

- Die beiden offenen Angaben aus Abschnitt 2 eingetragen.
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
- Das Datum in `impressum.html`, `datenschutz.html` und `sitemap.xml`
  stimmt noch.
- Die veröffentlichte Aufgabenverteilung nach Art. 26 DSGVO entspricht der
  tatsächlichen Vereinbarung: Aranda Möller übernimmt für die gemeinsame
  Website die Informationspflichten, die Bearbeitung von Betroffenenanfragen
  und die Koordination von Hosting beziehungsweise technischem Betrieb.
  Änderungen immer zugleich in der Vereinbarung und in `datenschutz.html`
  nachziehen.
- Die Vergütungsangaben in `aufgaben.html` (sechzehn reguläre
  Fallpauschalen, 98 bis 427 Euro; Sondervergütung für Sterilisations- und
  Ergänzungsbetreuer) gelten nach dem zum 1. Januar 2026 geänderten VBVG. Der
  Geldbetrag von grundsätzlich 10.000 Euro ist nur ein Teil des geschützten
  Vermögens. Bei der nächsten Anpassung der Gesetze alle Angaben nachziehen.
- Das Einzugsgebiet umfasst die Landkreise Lörrach (35 Gemeinden) und
  Waldshut (32 Gemeinden). Die Liste steht an genau einer Stelle im JSON-LD unter
  `areaServed`. Bei einer Gebietsänderung bitte anpassen. Die Kurzfassung
  steht in `partials/rail.html` und in `aufgaben.html`.
- Keine externen Schriften, Skripte oder Karten nachträglich einbauen. Die
  Datenschutzerklärung behauptet, dass es keine gibt — und die
  Content-Security-Policy in `partials/head.html` setzt das durch. Wer sie
  lockern muss, baut gerade etwas ein, das hier nicht hingehört.
- Das Vorschaubild `vorschau.png` zeigt noch den richtigen Anspruch. Es
  erscheint überall dort, wo jemand den Verweis weiterschickt, und wird aus
  `tools/vorschau.svg` erzeugt: `tools/vorschau.sh`.
- `sitemap.xml` ist neu geschrieben: `tools/sitemap.sh`. Impressum und
  Datenschutz stehen bewusst nicht darin — beide tragen `noindex`, weil
  § 5 DDG Erreichbarkeit verlangt, nicht Auffindbarkeit.
- Die Liste der offenen Platzhalter ist leer:

      grep -rn '\[[A-ZÄÖÜ]' -- *.html partials/
