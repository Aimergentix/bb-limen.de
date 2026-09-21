# Redaktion

Wie auf bb-limen.de geschrieben wird, wie sich das messen lässt und welche
Rechtsstände den Texten zugrunde liegen. Die verbindlichen Regeln stehen in
[AGENTS.md](../AGENTS.md) unter R-SPRACHE und R-RECHT.

## Sprachebenen

Die Seite hat vier Sprachebenen (R-SPRACHE-1). Wer Text ändert, sollte wissen,
auf welcher er sich befindet:

- **`leichte-sprache.html`** — Leichte Sprache. Kurze Sätze,
  ein Satz je Zeile, Binde-Striche in zusammengesetzten Wörtern, schwere
  Wörter erklärt. Eigene Typografie über `body class="ls"`. Kurze Sätze sind
  eine redaktionelle Hilfe, aber keine numerische A1-Zertifizierung.
- **`fachkreise.html`** — Fachsprache für Gerichte, Behörden, Kliniken
  und Ärzte. Paragraphen ohne Erklärung der Grundlagen. Hier ist
  Genauigkeit wichtiger als Einfachheit. Das Sprungmenü oben muss zu den
  `id`-Attributen der Überschriften passen.
- **`index.html`, `betreuung.html`, `aufgaben.html`, `vorsorge.html`** —
  Einfache Sprache (etwa A2 bis B1).
  Kurze Sätze, aktiv statt passiv, Verben statt Substantivierungen,
  Fachwörter bei der ersten Nennung erklärt. Aber mit Rhythmus: Sätze
  dürfen unterschiedlich lang sein, nur nicht verschachtelt.
- **`impressum.html`, `datenschutz.html`** — juristisches Standarddeutsch;
  warum, steht in [entscheidungen.md](entscheidungen.md) unter E-03.

Zum Begriffspaar Aufgabenkreis und Aufgabenbereich gilt R-RECHT-2. Eine
abschließende Liste der Aufgabenbereiche gibt es nicht — Register VI auf
`aufgaben.html` sagt das ausdrücklich.

## Satzlängen messen

Messen lässt sich ein Teil davon:

    python3 tools/pruefe-sprache.py                 alle Seiten
    python3 tools/pruefe-sprache.py vorsorge.html   mit den zu langen Sätzen

Der Parser betrachtet nur den Fließtext in `main`; Überschriften,
Beschriftungen, Kontakt- und Ortslisten werden getrennt gehalten. `<br>` ist
ein Layoutumbruch und kein Satzende. Das A2/B1-Ziel gilt für die Seiten mit
dem Sprachprofil `einfach`; die Zielwerte stehen als `ZIEL_MITTEL` und
`ZIEL_MAX` im Werkzeug selbst. Fachseite, Pflichttexte und Leichte Sprache
werden separat als Statistik ausgegeben. Das ersetzt weder Sprachgefühl noch
die Prüfgruppe.

Die Messung liest `dist/`; vorher `tools/build.sh` aufrufen.
`tools/pruefen.sh` erledigt beides von selbst.

## Prüfung der Leichten Sprache

`leichte-sprache.html` folgt den
üblichen Regeln — kurze Sätze, ein Satz je Zeile, Binde-Striche in
zusammengesetzten Wörtern, schwere Wörter erklärt. Nach dem Standard des
Netzwerks Leichte Sprache gehört ein Text aber von einer **Prüfgruppe**
aus Menschen mit Lernschwierigkeiten gegengelesen, bevor er als Leichte
Sprache gilt. Das steht noch aus. Lebenshilfe und Diakonie vermitteln
solche Prüfgruppen; die Betreuungsbehörde weiß meist, wer es vor Ort
macht. Erst danach das Europäische Leichte-Sprache-Logo verwenden — es
ist lizenziert und setzt die Prüfung voraus.

## Verweise nach außen pflegen

Die Seiten `vorsorge.html` und `leichte-sprache.html` verweisen auf fremde
Seiten — Ministerien, Behörden, Bundesnotarkammer, Lebenshilfe, KVJS. Fremde
Formulare werden verlinkt, nicht gehostet (R-VERBOT-2, Begründung E-02).

Auf jeder Angabe steht der Stand des Dokuments. Ob die Adressen erreichbar
sind, prüft einmal im Monat ein Workflow und legt bei einem toten Verweis ein
Issue an. Was er nicht prüft: ob der genannte Stand noch stimmt. Ein
Ministerium kann dieselbe Adresse behalten und den Inhalt austauschen. Deshalb
**zweimal im Jahr von Hand prüfen**, ob Verweis und Stand noch stimmen.

Ändert eine Stelle den Stand ihres Dokuments, die Angabe auf der Seite
mitziehen — sonst steht dort eine Jahreszahl, die nicht mehr gilt.

## Externe Profile

Laut Betreiberangabe vom 20.09.2026 bestehen noch
keine öffentlichen Profile für BB Limen, Aranda Möller oder Mika Möller.
Deshalb gibt es derzeit keine Profil-Links und kein `sameAs`. Wenn Profile
hinzukommen, die genaue URL und Identität prüfen: persönliche Profile der
jeweiligen Person zuordnen, gemeinsame Büroprofile dem Büro.

## Rechtsstände

Worauf sich die Texte stützen. Vor jeder Änderung gilt R-RECHT-1: nachschlagen,
nicht aus dem Gedächtnis schreiben.

**Registrierungen.** Beide Personen sind freiberuflich und einzeln
registrierungspflichtig (§ 23 BtOG, personenbezogen, nicht bürobezogen).
Sobald eine Registrierung erteilt ist: Nummer und Datum im Impressum
eintragen und den jeweiligen Gründungshinweis entfernen. Solange eine
Registrierung fehlt, darf die betreffende Person keine berufliche
Betreuung führen. Wo der Gründungshinweis steht, regelt R-BESTAND-3.

**Berufshaftpflicht.** Zwei getrennte Verträge, je einer pro Person
(§ 23 Abs. 1 Nr. 3 BtOG). Im Impressum sind beide Zeilen angelegt.

**Umsatzsteuer.** Im Impressum steht die
Befreiung nach § 4 Nr. 16 Satz 1 Buchstabe k UStG mit der Ausnahme für
Leistungen nach § 1877 Abs. 3 BGB.

**Vergütung.** Die Vergütungsangaben in `aufgaben.html` (sechzehn reguläre
Fallpauschalen, 98 bis 427 Euro; Sondervergütung für Sterilisations- und
Ergänzungsbetreuer) gelten nach dem zum 1. Januar 2026 geänderten VBVG.
Die Tabelle ist die Anlage zu § 8 Abs. 1 VBVG (Fundstelle BGBl. 2025 I
Nr. 109), die Bemessung regelt § 9 VBVG. Der Geldbetrag von
grundsätzlich 10.000 Euro ist nur ein Teil des geschützten
Vermögens. Bei der nächsten Anpassung der Gesetze alle Angaben nachziehen.

**Gemeinsame Verantwortung.** Die veröffentlichte Aufgabenverteilung nach
Art. 26 DSGVO entspricht der
tatsächlichen Vereinbarung: Aranda Möller übernimmt für die gemeinsame
Website die Informationspflichten, die Bearbeitung von Betroffenenanfragen
und die Koordination von Hosting beziehungsweise technischem Betrieb.
Änderungen immer zugleich in der Vereinbarung und in `datenschutz.html`
nachziehen.

**Einzugsgebiet.** Das Einzugsgebiet umfasst die Landkreise Lörrach
(35 Gemeinden) und
Waldshut (32 Gemeinden), zusammen 67. Die vollständige Liste steht an genau
einer Stelle im JSON-LD unter `areaServed`. Bei einer Gebietsänderung bitte
anpassen. Wo die Zahl außerdem steht, regelt R-ANGABEN-2; die Kurzfassung ohne
Zahl — nur die beiden Landkreisnamen — steht in `src/partials/rail.html`.
