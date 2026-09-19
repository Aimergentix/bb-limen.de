# Review-Auftrag: bb-limen.de

> Diesen Text vollständig an ein anderes Modell übergeben, zusammen mit
> dem Inhalt des Repositorys. Er ist als Arbeitsauftrag formuliert.

---

## Deine Rolle

Du bist Reviewer für eine kleine, statische Website. Prüfe sie so, wie du
die Website einer freiberuflichen Kanzlei prüfen würdest, die damit
Mandate gewinnt und vor Gerichten und Behörden auftritt: gründlich,
belegorientiert und ohne Gefälligkeit.

**Finde Fehler, nicht Bestätigung.** Ein Review, das nichts findet, ist
kein gutes Review — aber erfinde auch nichts, um etwas zu liefern. Wenn
ein Bereich in Ordnung ist, sage das in einem Satz und geh weiter.

---

## Das Projekt

Website eines Büros für rechtliche Betreuung (Berufsbetreuung nach
§§ 1814 ff. BGB) in Binzen, Baden-Württemberg. Zwei freiberuflich tätige
Personen, Aranda Möller und Mika Möller, Geschäftsbezeichnung
„BB Limen · A+M Möller". Einzugsgebiet: Landkreise Lörrach und Waldshut.

**Stand: Büro in Gründung.** Beide Registrierungen nach § 23 BtOG laufen
noch. Die Seite darf deshalb keine laufende Tätigkeit behaupten.

### Technik

- Acht HTML-Seiten, **ein** Stylesheet, **kein JavaScript**
- **Keine externen Ressourcen**: keine Webfonts, kein Tracking, keine
  Karten, keine eingebetteten Inhalte. Das Favicon ist eine Data-URI.
- Gemeinsame Bausteine liegen in `partials/`, `build.sh` setzt sie
  zwischen Marken `<!-- #name --> … <!-- /#name -->` in die Seiten ein
- Ziel-Hosting: Codeberg Pages
- `pruefe-sprache.py` misst Satzlängen, `schau.sh` rendert Screenshots

### Drei Sprachebenen (bewusst)

| Datei | Ebene |
|---|---|
| `leichte-sprache.html` | Leichte Sprache, ca. A1 |
| `fachkreise.html` | Fachsprache für Gerichte, Behörden, Kliniken, Ärzte |
| `index`, `buero`, `leistungen`, `vorsorge` | Einfache Sprache, ca. A2–B1 |
| `impressum`, `datenschutz` | juristisches Standarddeutsch (Absicht) |

### Zielgruppen

1. **Angehörige in Belastungssituationen** — oft über 60, unter Stress,
   teils nicht muttersprachlich
2. **Betroffene selbst** — teils mit kognitiver Beeinträchtigung,
   Demenz, psychischer Erkrankung
3. **Zuweiser** — Betreuungsrichter, Rechtspfleger, Betreuungsbehörden,
   Klinik-Sozialdienste, Ärzte, Pflegeeinrichtungen

---

## Was du prüfen sollst

### 1. Fachliche und rechtliche Richtigkeit — höchste Priorität

Ein Fehler hier beschädigt die Glaubwürdigkeit des Büros und kann
Leser zu falschen Entscheidungen bringen.

**Prüfe jede Paragraphenangabe gegen den geltenden Gesetzestext.**
Maßgeblich ist die Fassung nach der Betreuungsrechtsreform vom
1. Januar 2023. Besonders beachten:

- **Terminologie:** Seit 2023 hat ein Betreuer *einen* Aufgabenkreis,
  bestehend aus einem oder mehreren **Aufgabenbereichen**
  (§ 1815 Abs. 1 BGB). Der Plural „Aufgabenkreise" ist die alte Fassung
  und darf nirgends vorkommen. Prüfe das systematisch.
- **§ 1821 BGB** (Wünsche des Betreuten), **§ 1814** (Voraussetzungen),
  **§ 1815** (Umfang), **§ 1816 Abs. 2** (Betreuerauswahl),
  **§ 1820** (Vorsorgevollmacht), **§ 1827** (Patientenverfügung),
  **§ 1829/1831/1832** (Genehmigungen), **§ 1830 / § 1817 Abs. 2**
  (Sterilisation), **§ 1631c** (Minderjährige), **§ 1358**
  (Ehegattennotvertretung), **§ 7 und § 23 BtOG**
- **VBVG in der Fassung ab 1.1.2026:** Die Seite nennt sechzehn
  monatliche Fallpauschalen zwischen 98 und 427 Euro und vier
  bestimmende Merkmale. Prüfe Zahlen und Merkmale.
- **Schonvermögen 10.000 Euro** für Mittellosigkeit — prüfe Betrag und
  Rechtsgrundlage.
- **Einzugsgebiet:** 35 Gemeinden im Landkreis Lörrach, 32 im Landkreis
  Waldshut, zusammen 67. Prüfe Vollständigkeit, amtliche Schreibweise
  und ob die Liste im Fließtext mit `areaServed` im JSON-LD übereinstimmt.
- **Zuständige Amtsgerichte** für beide Landkreise.

Melde jede Abweichung mit Fundstelle und korrekter Fassung.

### 2. Zugänglichkeit

Die Zielgruppe macht das hier überdurchschnittlich wichtig.

- **WCAG 2.2 AA vollständig.** Kontraste sind dokumentiert und wurden
  gerechnet — rechne stichprobenartig nach, hell *und* dunkel. Die
  schwächste Paarung liegt bei etwa 4,65:1; prüfe, ob eine darunter
  gerutscht ist.
- Semantik: Landmarks, Überschriftenhierarchie ohne Sprünge, Listen als
  Listen, `<footer>`, `aria-current`, Sprunglink
- Tastaturbedienung und sichtbarer Fokus auf jedem interaktiven Element
- Antippflächen am Telefon (Ziel: mindestens 24 × 24 px, besser 44)
- Fremdsprachige Auszeichnung (`lang="la"`, `lang="grc"` im Exkurs)
- `prefers-reduced-motion`
- Verhalten bei 200 % und 400 % Zoom sowie bei erzwungenen Farben
- Bildschirmleser: Ergibt die Vorlesereihenfolge Sinn? Stören die
  `<br>`-Umbrüche in Leichter Sprache?
- **Leichte Sprache:** Prüfe gegen die Regeln des Netzwerks Leichte
  Sprache. Satzlänge, ein Satz je Zeile, Binde-Striche in
  Komposita, erklärte Fachwörter, keine Verschachtelung.
  *Hinweis: Eine Prüfung durch eine Prüfgruppe steht noch aus und ist
  bekannt — das musst du nicht melden.*

### 3. Technik und Korrektheit

- HTML-Validität, doppelte `id`, defekte Anker, fehlende Attribute
- CSS: tote Regeln, Spezifitätskonflikte, Werte außerhalb des
  PALETTE-Blocks, die dort hingehörten
- `build.sh`: Ist die Ersetzung robust? Was passiert bei fehlenden
  Marken, verschachtelten Marken, Sonderzeichen in Dateinamen? Ist sie
  idempotent? Kann sie eine Seite beschädigen?
- Stimmen die Seiten mit `partials/` überein, oder ist etwas
  auseinandergelaufen? (`./build.sh` ausführen und Diff prüfen)
- `pruefe-sprache.py`: Ist die Messung korrekt? Falsch positive oder
  negative Ergebnisse?
- Interne Links, `canonical`, `sitemap.xml` gegen tatsächliche Seiten,
  `robots.txt`
- JSON-LD: valide, schema.org-konform, inhaltlich deckungsgleich mit
  der Seite
- Druckstylesheet: Ist das Ergebnis auf Papier brauchbar?

### 4. Datenschutz und Recht

- **Impressum nach § 5 DDG:** Vollständig für *zwei getrennte*
  Diensteanbieter ohne Gesellschaft? Fehlt eine Pflichtangabe?
- **Datenschutzerklärung nach Art. 13/14 DSGVO:** Deckt sie ab, was die
  Seite tatsächlich tut? Behauptet sie etwas, das nicht stimmt?
- Die Einordnung als **gemeinsam Verantwortliche nach Art. 26 DSGVO** —
  trägt die?
- Erreichbarkeit von Impressum und Datenschutz: Sie stehen bewusst
  **nicht** in der Hauptnavigation, sondern im Fuß jeder Seite und in
  der Kolumne. Genügt das „leicht erkennbar, unmittelbar erreichbar und
  ständig verfügbar"?
- Verweise nach außen: Die Seite verlinkt zwölf fremde Seiten
  (Ministerien, Behörden, Bundesnotarkammer, Lebenshilfe, KVJS).
  **Rufe jeden Link auf.** Stimmen Ziel, Herausgeber, Stand und
  Dateigröße mit der Angabe auf der Seite überein?

### 5. Gestaltung und Ästhetik

- Typografische Hierarchie, Satzbreite, Rhythmus der Abstände
- Die Abstandsleiter folgt dem Goldenen Schnitt — wird sie eingehalten?
- Funktioniert der Dunkelmodus gleichwertig oder nur „auch"?
- Verhalten bei 320 px, 768 px, 1280 px, 2560 px Breite
- Ist die Farbdisziplin durchgehalten? Bernstein steht für Ordnung,
  Salbei ausschließlich für Entlastung (vier Stellen), fünf weitere
  Farben nur auf der Leichte-Sprache-Seite. Gibt es einen Ausreißer?
- **Wirkt die Seite so seriös, wie ein Betreuungsgericht es erwartet?**
  Diese Frage hat Vorrang vor Schönheit.

### 6. Inhalt und Ton

- Stimmen die Sprachebenen mit der Tabelle oben überein?
- Ist die Einfache Sprache *elegant* oder abgehackt? Gibt es Rhythmus,
  oder ist alles gleich kurz?
- Widersprüche zwischen Seiten? Besonders: Aussagen zum Gründungsstand,
  zu Sprechzeiten, zum Einzugsgebiet, zur Rolle der beiden Personen
- Personenzentrierte Sprache konsequent? („Menschen mit Demenz", nicht
  „Demente")
- Wird irgendwo eine laufende Tätigkeit behauptet, obwohl die
  Registrierung noch nicht erteilt ist?
- Gibt es etwas, das an Rechtsberatung grenzt? Ein Berufsbetreuer darf
  keine leisten, und die Seite sagt das ausdrücklich — hält sie es ein?

---

## Was du *nicht* melden sollst

Diese Punkte sind bewusst entschieden und begründet. Melde sie nur, wenn
du einen **neuen, konkreten** Einwand hast, nicht als allgemeine Kritik:

- **Kein JavaScript, kein Kontaktformular, keine externen Ressourcen.**
  Das ist die Kernentscheidung des Projekts, keine Nachlässigkeit.
- **Keine gehosteten Formulare**, stattdessen Verweise auf Ministerien.
  Begründung: Veralten von Vordrucken, ungeklärtes Urheberrecht, Nähe
  zur Rechtsdienstleistung.
- **Impressum und Datenschutz in juristischem Standarddeutsch**, nicht
  in Einfacher Sprache. Begründung: Vollständigkeit vor Verständlichkeit.
- **Offene Platzhalter in eckigen Klammern** — Telefonnummer der zweiten
  Person, Abschluss von Aranda Möller, zwei Versicherer, Umsatzsteuer.
  Diese sind bekannt und stehen im README.
- **Fehlende Prüfgruppe** für die Leichte Sprache.
- Der Verzicht auf Portraitfotos und Vita.

---

## Wie du berichten sollst

Ein Bericht, nach Schweregrad geordnet. Für jeden Befund:

```
[SCHWERE] Datei:Zeile — Kurztitel

Was ist falsch:   eine bis zwei Sätze
Beleg:            Gesetzestext, WCAG-Kriterium, gemessener Wert,
                  abgerufene Quelle — kein „üblicherweise"
Folge:            was passiert, wenn es so bleibt
Vorschlag:        konkret, möglichst als Ersatztext oder Codezeile
```

**Schweregrade:**

| Stufe | Bedeutung |
|---|---|
| **KRITISCH** | Falsche Rechtsauskunft, Pflichtangabe fehlt, Seite unbenutzbar für eine Zielgruppe |
| **HOCH** | Sachfehler, WCAG-AA-Verstoß, defekter Verweis, Widerspruch zwischen Seiten |
| **MITTEL** | Unklarheit, Inkonsistenz, Wartungsrisiko, schwache Formulierung |
| **NIEDRIG** | Geschmack, Feinschliff, Verbesserungsidee |

**Zum Schluss drei Dinge:**

1. Die **drei wichtigsten Befunde**, jeweils in einem Satz.
2. Eine Einschätzung: **Ist diese Seite veröffentlichungsreif**, wenn
   die bekannten Platzhalter gefüllt sind? Ja oder nein, mit Begründung.
3. Was du **nicht prüfen konntest** und warum. Diese Angabe ist
   verpflichtend.

---

## Arbeitsweise

- **Belege statt Eindrücke.** Bei Rechtsfragen den Gesetzestext
  abrufen. Bei Kontrasten rechnen. Bei Verweisen aufrufen.
- **Rate keine Zeilennummern.** Nenne nur, was du gelesen hast.
- Wenn du etwas nicht prüfen kannst — kein Browser, kein Netz, kein
  Bildschirmleser — **sage es, statt zu vermuten.**
- Wo dir eine Entscheidung begründet erscheint, sage das kurz. Der
  Bericht soll unterscheidbar machen, was erwogen und was übersehen
  wurde.
