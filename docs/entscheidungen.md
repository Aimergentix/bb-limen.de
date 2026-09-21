# Entscheidungen

Warum etwas so ist, wie es ist. Jeder Eintrag hat eine feste Kennung und ein
Datum. **Hier wird nur ergänzt, nie umgeschrieben** (R-ORDNUNG-2): Wird eine
Entscheidung aufgehoben, bekommt sie einen neuen Eintrag, der auf den alten
verweist. Deshalb dürfen hier auch Dateien genannt sein, die es nicht mehr
gibt.

Die Regeln, die aus den Entscheidungen folgen, stehen in
[AGENTS.md](../AGENTS.md).

---

## E-01 · Kein JavaScript, keine fremden Ressourcen

Aufgezeichnet am 21.09.2026; die Entscheidung ist älter. Regel: R-VERBOT-1.

Das ist keine Geschmacksfrage: `datenschutz.html` behauptet, dass es nichts
davon gibt. Jede Einbindung macht die Datenschutzerklärung unwahr und aus
einem Gestaltungswunsch ein Rechtsproblem. Die Content-Security-Policy in
`src/partials/head.html` setzt das technisch durch — wer sie lockern muss,
baut gerade etwas ein, das hier nicht hingehört.

## E-02 · Fremde Formulare werden verlinkt, nicht gehostet

Aufgezeichnet am 21.09.2026; die Entscheidung ist älter. Regel: R-VERBOT-2.

**Absichtlich werden keine fremden Formulare im Repo gehostet:** ein
Vordruck für eine Vorsorgevollmacht veraltet mit dem Gesetz, und eine
veraltete Vollmacht versagt genau dann, wenn sie gebraucht wird. Wer die
Datei selbst ausliefert, übernimmt diese Verantwortung; wer verlinkt,
lässt sie bei der herausgebenden Stelle. Dazu kommt, dass weder das BMJ
noch das Justizministerium Baden-Württemberg Nutzungsbedingungen für die
Weiterverbreitung angibt.

## E-03 · Pflichttexte bleiben juristisches Standarddeutsch

Aufgezeichnet am 21.09.2026; die Entscheidung ist älter. Regel: R-SPRACHE-1.

`impressum.html` und `datenschutz.html` bleiben bewusst in juristischem
Standarddeutsch. Art. 12 DSGVO verlangt zwar Verständlichkeit, aber eine
vereinfachte Datenschutzerklärung wird schnell unvollständig — und
Unvollständigkeit ist der teurere Fehler.

## E-04 · Das Ornament ist ein SVG, kein Schriftzeichen

20.09.2026. Regel: R-VERBOT-3.

Bis zum 20.09.2026 stand dort U+2766 ❦ — ein Zeichen, das in keiner
Serifenschrift des Projekts vorkommt und deshalb auf eine Symbol- oder
Farb-Emoji-Schrift zurückfiel: auf jedem Gerät ein anderes Bild. Zeichen wie
❦ ❧ ✦ ❖ kommen weder in Noto Serif noch in Georgia oder Times New Roman vor.
Der Browser greift dann zu irgendeiner Symbol- oder Farb-Emoji-Schrift, und
auf jedem Gerät steht etwas anderes auf der Seite — meist ein bunter Fleck.
Schmuckzeichen also nie als Buchstabe.

## E-05 · Die Adressen bleiben bei `.html`

20.09.2026. Regel: R-BESTAND-2.

Keine Verzeichnisform und keine spätere Umbenennung ohne Entscheidung über
bestehende Verweise. Die öffentliche Adresse hängt seit E-09 am Namen in der
Ausgabe, nicht am Quellpfad; die Quellen können also umziehen, ohne dass sich
eine Adresse ändert.

## E-06 · Pflichtseiten tragen `noindex`

Aufgezeichnet am 21.09.2026; die Entscheidung ist älter. Regel: R-BESTAND-4.

Impressum und Datenschutz stehen bewusst nicht in der Sitemap — beide tragen
`noindex`, weil § 5 DDG Erreichbarkeit verlangt, nicht Auffindbarkeit.

Der Web-Audit vom 20.09.2026 sieht das anders: Das Impressum sei die stärkste
Quelle dafür, wer hinter der Seite steht, und solle auffindbar sein. Die Frage
ist offen; bis zu einer neuen Entscheidung gilt diese.

## E-07 · Vier Verzichte, die der Web-Audit vorfand

20.09.2026. Regeln: R-VERBOT-4, R-VERBOT-5, R-VERBOT-6, R-SPRACHE-3, R-SPRACHE-4.

Der Audit hat diese Eigenschaften nicht empfohlen, sondern vorgefunden und für
richtig erklärt. Sie standen bis zum 21.09.2026 nirgends geschrieben; ein
Assistent mit dem Auftrag „mach die Seite auffindbarer" hätte sie verletzt.

- **Kein Fallbeispiel, keine Klientengeschichte, kein Zitat.** Für ein
  Betreuungsbüro ist das der wichtigste Verzicht überhaupt. Auch eine
  anonymisierte Schilderung berührt die Verschwiegenheit.
- **Keine Vertrauensfloskeln.** Gesucht wurde nach *kompetent, individuell,
  Ihr Partner, professionell, zuverlässig, engagiert, vertrauensvoll,
  maßgeschneidert, ganzheitlich, aus einer Hand, jahrelange Erfahrung,
  Experte, Spezialist* — null Treffer. Das ist für eine Geschäftswebsite dieser
  Branche ungewöhnlich und soll so bleiben.
- **Keine Ortsseiten.** Die 67 Gemeinden stehen ausschließlich im JSON-LD,
  nicht als 67 Seitenvarianten mit getauschtem Ortsnamen.
- **Kein `LocalBusiness`.** Bei einer angemieteten, nicht ständig besetzten
  Geschäftsadresse ist `Organization` mit `PostalAddress` die richtige Wahl:
  Anschrift ohne Standortbehauptung. Aus demselben Grund wäre ein Eintrag bei
  einem Kartendienst ein Risiko — Verifizierung, Richtlinien zu unbesetzten
  Standorten, und im Konfliktfall eine Angabe, die sich nicht halten lässt.
- **Verweise nennen ihr Ziel.** Gesucht nach „hier", „mehr", „weiterlesen",
  „mehr erfahren" — null Treffer.

## E-08 · Kein maschineller Bildvergleich

21.09.2026. Regel: R-PRUEFUNG-2.

Der Bildvergleich verglich den Stand vor und nach jedem Push Bild für Bild,
brach nie ab und kostete drei Skripte, einen Chromium-Lauf und den längsten
CI-Job. Für eine Website ohne JavaScript, deren Layout sich selten ändert, ist
das zu viel Werkzeugkette. Er wird nicht wieder eingeführt; die Sichtprüfung
bleibt Handarbeit.

## E-09 · Quellen und Ausgabe sind getrennt

21.09.2026, Commit `fcddb79`; Ausgangsstand war `c2064ce`. Regeln: R-QUELLE-1,
R-QUELLE-3, R-ORDNUNG-6.

Vorher lagen die Seiten im Wurzelverzeichnis, und der Build schrieb die
Bausteine zwischen Marken in dieselben Dateien. Eine Änderung zwischen den
Marken sah richtig aus, bestand die Tests und war beim nächsten Build
verschwunden — der Fehler, den jedes Modell mindestens einmal gemacht hat.
Seit der Trennung gibt es ihn nicht mehr: Quellen enthalten nur Include-Zeilen,
und `dist/` ist vollständig erzeugt. Beim Umzug blieben 16 von 17
ausgelieferten Dateien bytegleich; in `404.html` rückte die `base`-Zeile vor
die Ressourcenverweise, was einen Validierungsfehler behob.

`lastmod` wurde bei der Migration aus der bestehenden Sitemap übernommen.
Die frühere automatische Datierung über den Git-Pfad wurde ersetzt, damit
Dateiumzüge, flache Klone und Builds ohne Git keinen falschen Stand erzeugen.
Git bleibt der Nachweis für die Änderung.

## E-10 · Veröffentlicht wird über GitHub Actions

21.09.2026.

GitHub Pages baut nicht mehr aus dem Zweig, sondern erhält `dist/` als Artefakt
aus `.github/workflows/veroeffentlichung.yml`. Jekyll ist damit nicht mehr
beteiligt. `_config.yml`, das Quellen vom Jekyll-Weg ausschloss, und das Verbot
einer Datei `.nojekyll` sind gegenstandslos und entfallen.

## E-11 · Der HTML-Validator bleibt, mit fester Version

21.09.2026. Regel: R-PRUEFUNG-4.

Das Paket `html5validator` ist seit 2022 unverändert und bündelt einen alten
Nu Html Checker, der das gültige `media` auf `meta name="theme-color"` als
Fehler meldet. Statt zu wechseln, gilt eine eng gefasste Ausnahme mit
Gegentest, und die Version ist auf 0.4.2 festgeschrieben.

Gegen den Wechsel sprach: Der Hersteller des Checkers veröffentlicht seit 2020
nur noch ein laufend überschriebenes „latest" — eine CI darauf kann ohne
eigenen Commit rot werden. Lokal fehlt Java, jeder Versuch liefe über einen
Push, und an dieser Prüfung hängt die Veröffentlichung.

**Gewechselt wird,** sobald eine vierte Ausnahme nötig würde oder das Paket
auf einem neuen CI-Läufer ausfällt. Dann auf das npm-Paket `vnu-jar` in fester
Version; es trägt datierte Versionsnummern.

Python ist in der CI auf 3.12 festgelegt, den Mindeststand aus dem README.
Python 3.10 erreicht im Oktober 2026 das Ende seiner Pflege.

## E-12 · Eine Aussage, ein Ort

21.09.2026. Regeln: R-ORDNUNG-1 bis R-ORDNUNG-3.

Dieselbe Aussage stand bis zu siebenmal im Repository: in Vertrag, README,
Architektur, Kommentaren. Die Regel „Vertrag und README im selben Commit
ändern" war das Eingeständnis, dass beides auseinanderlaufen kann — und es
lief auseinander: Dieselbe Regel stand einmal als „sollte" und einmal als
„darf nicht" da, „Inhaltsseiten" meinte drei verschiedene Mengen.

Seitdem hat jede Aussage ein Zuhause, bestimmt durch die Frage, die sie
beantwortet; Regeln tragen Kennungen und die Wörter MUSS, DARF NICHT, SOLL,
KANN; `tests/test_doku.py` hält Pfade, Verweise, Kennungen und Begriffe fest.
Der Gedanke dahinter steht im
[Anhang der Architektur](architektur.md#anhang-arbeitsgrundsätze).

Offene Punkte liegen in `docs/lokal/offen.md` und damit nur lokal: Das
Repository ist öffentlich, und offene Rechts- und Geschäftsfragen eines Büros
gehören nicht hinein. Der Preis: Assistenten in der Cloud sehen sie nicht.

## E-13 · Büroangaben als gemeinsame Datenquelle

21.09.2026. Regeln: R-ANGABEN-1, R-ANGABEN-3, R-ANGABEN-4 und R-ANGABEN-6.

Telefonnummer, E-Mail, Anschrift und Sprechzeiten wurden an mehreren Stellen
von Hand gepflegt. Auf Wunsch des Büros wurden zuerst die Sprechzeiten und
danach die übrigen Kontaktangaben nach `src/bureauangaben.json` überführt.
Der vorhandene Python-Build erzeugt daraus die passenden Sprachfassungen und
maskiert Werte nach ihrem Ausgabeformat. Die vCard entsteht aus dem erzeugten
Organization-Knoten; die bisherige Kopierdatei unter `public/` entfällt.

Die unabhängigen Erwartungswerte der Tests bleiben erhalten. Zusätzlich
prüfen Änderungen an Testdaten, ob alle Verwendungen nachgezogen werden und
fehlerhafte Eingaben die letzte erfolgreiche Ausgabe erhalten. Die Migration
ändert weder die veröffentlichten Inhalte noch deren redaktionelle Standdaten.
Der Datenfluss steht unter [Büroangaben](architektur.md#büroangaben).

Im Anschluss hat das Büro die Sprechzeiten in der neuen Datendatei geändert
und die sichtbare Telefonnummer neu gruppiert. Diese Inhaltsänderung ist
getrennt von der Migration zu bewerten; die betroffenen Inhaltsstände werden
auf den 21.09.2026 gesetzt. Die Prüferwartungen folgen den geänderten Angaben.
