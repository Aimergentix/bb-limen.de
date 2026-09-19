# bb-limen.de — statische Website

Acht Seiten, ein Stylesheet, keine Abhängigkeiten, keine externen Ressourcen,
kein JavaScript. Was im Browser ankommt, ist genau das, was hier im
Verzeichnis liegt.

    index.html        Startseite, Einzugsgebiet, Kontakt
    buero.html        Das Büro, Exkurs zum Namen, Haltung nach § 1821 BGB
    leistungen.html   Aufgabenbereiche, Ablauf, Kosten
    vorsorge.html     Vollmacht, Betreuungs- und Patientenverfügung
    fachkreise.html   Fachsprache: Gerichte, Behörden, Kliniken, Ärzte
    leichte-sprache.html  dieselben Inhalte in Leichter Sprache

    pruefe-sprache.py Misst die Satzlänge im Fließtext
    impressum.html    Pflichtangaben nach § 5 DDG
    datenschutz.html  Information nach Art. 13 DSGVO
    style.css         gemeinsames Stylesheet
    robots.txt        Indexierungsregeln
    sitemap.xml       Seitenverzeichnis für Suchmaschinen
    _redirects        Weiterleitung von www auf die kanonische Hauptdomain

    partials/         die Bausteine, die auf jeder Seite gleich sind
    build.sh          setzt diese Bausteine in die acht Seiten ein
    tests/            Regressionstests für Build, Sprache und Seitenstruktur
    docs/             Quellenmaterial, nicht Teil der Website (.gitignore)

## 1. Gemeinsame Bausteine ändern

Kolumne, Navigation, Telefonnummer, Anschrift, Seitenfuß und Anrufleiste
stehen **nur** in `partials/`. Die acht Seiten enthalten Kopien davon
zwischen Marken wie

    <!-- #rail -->   … generierter Inhalt …   <!-- /#rail -->

Also: in `partials/` ändern, dann

    ./build.sh

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

**Telefonnummer von Mika Möller** — die maßgebliche Stelle ist
`partials/rail.html`; nach dem Build steht deren Kopie in allen acht Seiten.
Zusätzliche direkte Kontaktangaben gibt es in `index.html`,
`fachkreise.html`, `leichte-sprache.html` und im Impressum. Achtung: Der
Platzhalter ist bewusst **kein** `tel:`-Link — ein leeres `href="tel:"` war
schon einmal der schwerste Fehler dieser Seite. Beim Eintragen die Nummer an
allen direkten Kontaktstellen zugleich verlinken und anschließend bauen.

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

**Vereinbarung nach Art. 26 DSGVO.** Die Datenschutzerklärung nennt
Aranda Möller und Mika Möller als *gemeinsam Verantwortliche* für diese
Website. Diese Einordnung passt nur, wenn beide tatsächlich gemeinsam Zwecke
und Mittel der Verarbeitung festlegen. Art. 26 Abs. 1 DSGVO verlangt dann eine
Vereinbarung zwischen beiden, wer welche Pflichten erfüllt. Die vollständige
Vereinbarung muss nicht veröffentlicht werden.
Ihr wesentlicher Inhalt muss betroffenen Personen aber zugänglich sein.
`datenschutz.html` enthält deshalb einen offenen Block für die tatsächliche
Verteilung von Informationspflichten, Betroffenenanfragen und technischem
Betrieb. Diesen Block erst nach Abschluss der wirklichen Vereinbarung
ausfüllen; keine Zuständigkeiten erfinden.

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
`leistungen.html` sagt das ausdrücklich.
- **alle übrigen Inhaltsseiten** — Einfache Sprache (etwa A2 bis B1).
  Kurze Sätze, aktiv statt passiv, Verben statt Substantivierungen,
  Fachwörter bei der ersten Nennung erklärt. Aber mit Rhythmus: Sätze
  dürfen unterschiedlich lang sein, nur nicht verschachtelt.

`impressum.html` und `datenschutz.html` bleiben bewusst in juristischem
Standarddeutsch. Art. 12 DSGVO verlangt zwar Verständlichkeit, aber eine
vereinfachte Datenschutzerklärung wird schnell unvollständig — und
Unvollständigkeit ist der teurere Fehler.

Messen lässt sich ein Teil davon:

    ./pruefe-sprache.py                 alle Seiten
    ./pruefe-sprache.py vorsorge.html   mit den zu langen Sätzen

Der Parser betrachtet nur den Fließtext in `main`; Überschriften,
Beschriftungen, Kontakt- und Ortslisten werden getrennt gehalten. `<br>` ist
ein Layoutumbruch und kein Satzende. Das A2/B1-Ziel — im Mittel höchstens 15
Wörter je Satz, kein Satz über 25 — gilt für `index`, `buero`, `leistungen`
und `vorsorge`. Fachseite, Pflichttexte und Leichte Sprache werden separat als
Statistik ausgegeben. Das ersetzt weder Sprachgefühl noch die Prüfgruppe.

Regressionstests für Build und Sprachmessung:

    python3 -m unittest discover -s tests -v

## 2c. Farbe

Die Seite hat drei Farbstimmen, und jede bedeutet etwas. Alle Werte
stehen im Block PALETTE in `style.css`; ein Rückbau ist immer dieser
eine Block, nie eine Suche durchs Stylesheet.

- **Bernstein** (`--accent`) — Ordnung: Rubriken, Ziffern, Zierlinien.
- **Salbei** (`--gut`) — Entlastung. Im Fließtext nur für den Block
  `.gut`, und nur dort, wo die Nachricht wirklich entlastet: keine
  Entmündigung, eigene Wahl des Betreuers, keine Kosten bei
  Mittellosigkeit, der Weg zurück. **Vier Stellen auf der ganzen
  Website** (`index` 1, `buero` 1, `leistungen` 2). Wer mehr hinzufügt,
  nimmt der Farbe ihre Bedeutung. Eine einzige Ausnahme: die Blattkontur
  des Signets in der Kolumne (`.rail-brand .leaf .blatt`) steht ebenfalls
  in Salbei — sie ist kein Text, sondern das Zeichen selbst. Auch `--st-2`
  der Leichte-Sprache-Liste hat denselben Wert.
- **Papierwärme** (`--paper`, `--surface`) — keine Farbe, die man sieht,
  sondern eine Temperatur. `#fbfaf7` statt neutralem Grau.

Dazu `--hauch` für den Farbton, der nur bei Berührung erscheint, und
`--st-1` bis `--st-5` ausschließlich für die Leichte-Sprache-Seite: dort
hilft Farbe beim Wiederfinden und ist damit Funktion, keine Dekoration.

**Jede Farbe ist gegen WCAG AA geprüft, hell und dunkel.** Nach jeder
Änderung am PALETTE-Block neu rechnen — die schwächste Paarung liegt bei
4,65:1, es ist also wenig Luft. Die Fachseite bleibt bewusst nüchtern.

## 3. Lokal ansehen

    python3 -m http.server 8000

Dann `http://localhost:8000` öffnen. Für Bilder zum Nachsehen:

    ./schau.sh index.html 1280 1500 start          # hell
    ./schau.sh index.html 390 1400 start-mobil     # Telefon
    ./schau.sh index.html 1280 1500 start-d dunkel # Dunkelmodus

Das legt PNG unter `~/bb-shots` ab; der Server muss auf Port 8391 laufen.
Chromium im Snap darf nicht nach `/tmp` schreiben — deshalb der Home-Pfad. Unbedingt auch am Telefon ansehen: dort
wird aus der stehenden Kolumne ein schmales Kopfband, und der Kontakt steht
in der festen Anrufleiste am unteren Rand.

## 4. Bei Codeberg veröffentlichen

Die Website verwendet `https://bb-limen.de/` als kanonische Adresse. Für das
aktuelle Webhook-Verfahren von Codeberg Pages sind Branch, Webhook und
Zieladresse ausdrücklich einzurichten; ein Push allein veröffentlicht noch
nichts.

1. Auf codeberg.org ein öffentliches Repository `pages` anlegen. Im Repository
   muss ein Branch namens `pages` vorhanden sein. Den aktuellen lokalen Stand
   zum Beispiel so dorthin übertragen:

       git remote add codeberg https://codeberg.org/BENUTZERNAME/pages.git
       git push codeberg main:pages

2. Optional für eine zusätzliche Codeberg-Unterdomain: Unter
   **Einstellungen → Webhooks → Webhook hinzufügen → Forgejo** einen
   Webhook anlegen. Für die Codeberg-Unterdomain lautet die Zieladresse
   `https://BENUTZERNAME.codeberg.page/`; der Branchfilter lautet `pages`.
   Die Schaltfläche „Test delivery“ ist dafür nicht geeignet. Mit einem Push
   in den Branch `pages` testen und anschließend die Webhook-Auslieferung
   kontrollieren.
3. Für die eigene Domain läuft die Autorisierung über DNS. Bei inwx eintragen:

       www.bb-limen.de                         CNAME  codeberg.page.
       bb-limen.de                             ALIAS  codeberg.page
       _git-pages-repository.bb-limen.de       TXT    https://codeberg.org/BENUTZERNAME/pages.git
       _git-pages-repository.www.bb-limen.de   TXT    https://codeberg.org/BENUTZERNAME/pages.git

   Bietet inwx für den Apex kein ALIAS, stattdessen A auf `217.197.84.141`
   und AAAA auf `2a0a:4580:103f:c0de::2` setzen. Die TXT-Einträge sind
   zwingend — ohne sie liefert Codeberg die eigene Domain nicht aus.

   Die MX- und TXT-Einträge für mailbox.org bleiben unverändert. Falls
   CAA-Einträge gesetzt sind, muss `letsencrypt.org` darin erlaubt sein.

4. Für die Hauptdomain einen eigenen Webhook mit Branchfilter `pages` anlegen.
   Die Zieladresse muss beim **ersten** Deployment `http://bb-limen.de/`
   lauten. Nach dem ersten erfolgreichen Lauf auf `https://bb-limen.de/`
   umstellen.
5. Auch `www.bb-limen.de` muss separat deployt werden: zweiter Webhook,
   ebenfalls zunächst mit `http://www.bb-limen.de/`, danach HTTPS. Die Datei
   `_redirects` leitet diese Variante bewusst auf die kanonische Hauptdomain
   um. Soll die Codeberg-Unterdomain zusätzlich erreichbar sein, braucht auch
   sie den optionalen eigenen Webhook aus Schritt 2.
6. Die aktuelle Codeberg-Dokumentation vor jeder Einrichtung gegenlesen, da
   sich das Verfahren ändern kann:

   <https://docs.codeberg.org/codeberg-pages/>

   <https://docs.codeberg.org/codeberg-pages/using-custom-domain/>

Das TLS-Zertifikat holt der Pages-Server automatisch über Let's Encrypt.

## 5. Vor dem Onlinegehen prüfen

- Die beiden offenen Angaben aus Abschnitt 2 eingetragen.
- Registrierung nach § 23 BtOG noch nicht erteilt: Der Hinweis auf den
  Gründungsstand steht auf allen fünf Inhaltsseiten (`index`, `buero`,
  `leistungen`, `vorsorge`, `fachkreise`) und im Impressum. Nach Erteilung
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
- Die Vergütungsangaben in `leistungen.html` (sechzehn reguläre
  Fallpauschalen, 98 bis 427 Euro; Sondervergütung für Sterilisations- und
  Ergänzungsbetreuer) gelten nach dem zum 1. Januar 2026 geänderten VBVG. Der
  Geldbetrag von grundsätzlich 10.000 Euro ist nur ein Teil des geschützten
  Vermögens. Bei der nächsten Anpassung der Gesetze alle Angaben nachziehen.
- Das Einzugsgebiet umfasst die Landkreise Lörrach (35 Gemeinden) und
  Waldshut (32 Gemeinden). Die Liste steht an genau zwei Stellen in
  `index.html`: im Abschnitt „Wo ich arbeite" und im JSON-LD unter
  `areaServed`. Bei einer Gebietsänderung beide anpassen. Die Kurzfassung
  steht in `partials/rail.html` und in `leistungen.html`.
- Keine externen Schriften, Skripte oder Karten nachträglich einbauen. Die
  Datenschutzerklärung behauptet, dass es keine gibt.
