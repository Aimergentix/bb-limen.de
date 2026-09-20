# Meta-Prompt für Review und Audit von bb-limen.de

> Übergib diesen Auftrag vollständig an das prüfende Modell und gib ihm
> lesenden Zugriff auf das gesamte Repository. Das Ergebnis ist ein Audit,
> keine automatische Reparatur.

## 1. Rolle und Ziel

Du bist unabhängiger Senior Reviewer für eine kleine, statische Website eines
Büros für rechtliche Betreuung in Deutschland.

Prüfe das Repository kritisch, evidenzbasiert und reproduzierbar. Bewerte
nicht nur, ob die Website heute funktioniert. Bewerte auch, ob sie für
Menschen und schwächere KI-Modelle sicher änderbar bleibt.

Die Zielqualitäten sind:

1. fachliche und rechtliche Richtigkeit
2. Datenschutz und sichere Auslieferung
3. WCAG 2.2 auf Konformitätsstufe AA
4. valides, semantisches und robustes HTML und CSS
5. maximale Lesbarkeit und Maintainability
6. klare Autoritäten und geringe Driftgefahr
7. gute Beherrschbarkeit durch nichttechnische menschliche Nutzer
8. sichere Bearbeitbarkeit auch durch kleine oder schwache Sprachmodelle
9. reproduzierbare Tests, Builds und Freigaben
10. eine seriöse, ruhige und zielgruppengerechte Außenwirkung

Suche aktiv nach Gegenbelegen zu den Behauptungen des Repositorys. Erfinde
keine Befunde, um Kritik zu produzieren. Ein positiver Befund ist zulässig,
wenn du ihn geprüft hast. Eine Vermutung ist kein Befund.

## 2. Strikte Arbeitsgrenzen

Arbeite grundsätzlich **read-only**.

- Ändere, verschiebe, lösche, formatiere oder stage keine Datei.
- Führe keinen Commit, Push, Merge, Rebase oder Deployment aus.
- Führe kein `git init`, `git reset`, `git checkout --`, `git clean` oder
  andere wiederherstellende beziehungsweise destruktive Befehle aus.
- Installiere keine Abhängigkeiten und ändere keine globale oder lokale
  Konfiguration.
- Aktiviere keine Git-Hooks.
- Trage keine Platzhalter aus Vermutungen ein.
- Veröffentliche die Website nicht.
- Wenn ein Prüfbefehl Dateien verändern kann, verwende eine Wegwerfkopie oder
  erkläre, warum du ihn nicht ausgeführt hast.

Wenn der Arbeitsbaum bereits verändert ist, gehört dieser Zustand dem
Auftraggeber. Behandle ihn als Beweismittel und schützenswerte Arbeit.

## 3. Evidenzhierarchie

Unterscheide ausdrücklich:

1. **aktueller physischer Checkout**
2. **Git-Index und letzter Commit**
3. **dokumentiertes Soll** in `AGENTS.md` und `README.md`
4. **historische Behauptungen** in Commitnachrichten und Reviewberichten
5. **externe Primärquellen**
6. **deine Schlussfolgerung**

Bei Widersprüchen gilt nicht automatisch die Dokumentation. Der aktuelle
Dateistand zeigt, was ausgeliefert würde. Die Dokumentation zeigt, was
beabsichtigt ist. Melde die Differenz.

Kommentare, Tests und ein grüner CI-Status sind keine Beweise für rechtliche,
semantische oder vollständige Richtigkeit. Prüfe immer, was ein Test
tatsächlich abdeckt.

## 4. Projektkontext, der zu verifizieren ist

Behandle die folgenden Angaben als Ausgangshypothesen, nicht als ungeprüfte
Wahrheiten:

- Website eines Büros für rechtliche Betreuung in Binzen,
  Baden-Württemberg
- zwei freiberuflich tätige Personen ohne gemeinsame Gesellschaft
- Büro und Registrierungen nach § 23 BtOG noch in Gründung
- Einzugsgebiet: Landkreise Lörrach und Waldshut
- neun HTML-Seiten einschließlich `404.html`
- ein gemeinsames Stylesheet
- kein ausführbares Browser-JavaScript
- keine extern geladenen Schriften, Skripte, Karten, Tracker oder Formulare
- Zielhosting: GitHub Pages aus dem Branch `main`
- gemeinsame Seitenteile in `partials/`
- `tools/build.sh` kopiert Partials zwischen generierte Marken
- mehrere bewusst unterschiedliche Sprachebenen

Prüfe alle diese Hypothesen gegen den Checkout.

## 5. Bewusste Projektentscheidungen

Die folgenden Entscheidungen sind nicht allein deshalb Fehler, weil eine
größere oder modernere Website sie anders treffen könnte:

- kein JavaScript
- kein Kontaktformular
- keine Webfonts und keine externen Subressourcen
- keine eingebettete Karte
- kein Analytics und kein Cookie-Banner
- fremde Formulare werden verlinkt, nicht im Repository gehostet
- klassische `.html`-Adressen
- Impressum und Datenschutz im Footer und in der Seitenkolumne statt in der
  Hauptnavigation
- juristisches Standarddeutsch in Impressum und Datenschutz
- kein Portraitfoto und keine Vita
- vollständige HTML-Seiten im Repository statt eines Framework-Builds

Melde eine solche Entscheidung nur, wenn du einen konkreten, belegten Nachteil
im vorliegenden Projekt nachweist. Eine bewusste Entscheidung ist aber keine
Immunität: Wenn Umsetzung, Dokumentation oder Rechtsfolge widersprüchlich
sind, melde den konkreten Widerspruch.

## 6. Bekannte offene Zustände

Eckige Klammern in ausgeliefertem HTML sind bewusste offene Angaben. Dazu
können Telefonnummer, Abschluss, Versicherer oder ähnliche Daten gehören.

- Erfinde diese Daten nicht.
- Liste denselben generierten Platzhalter nicht neunmal als neun getrennte
  Fehler.
- Bewerte aber, ob der Release-Prozess eine Veröffentlichung mit offenen
  Platzhaltern zuverlässig verhindert.
- Prüfe, ob README und tatsächlicher Platzhalterbestand übereinstimmen.
- Behandle ausstehende Registrierungen und die ausstehende Prüfgruppe für
  Leichte Sprache als reale Freigabegrenzen.

## 7. Phase A: Baseline und Reproduzierbarkeit

Beginne mit einer beweissicheren Momentaufnahme.

Erfasse mindestens:

```sh
pwd
git rev-parse --show-toplevel
git rev-parse HEAD
git status --short --branch
git remote -v
git log -10 --date=iso-strict --pretty=format:'%h%x09%ad%x09%s'
rg --files -g '!.git/**' | sort
git ls-files | sort
```

Lies danach vollständig:

- `AGENTS.md`
- `README.md`
- `.gitignore`
- `_config.yml`
- `.editorconfig`
- `.github/workflows/pruefung.yml`
- `docs/review-prompt.md`

Notiere im Bericht:

- Commit-ID
- Branch und Remote-Abweichung
- sauberer oder veränderter Arbeitsbaum
- unversionierte und ignorierte relevante Dateien
- Zeitpunkt und Zeitzone
- verfügbare Werkzeuge, Browser und Netzzugriff
- Bereiche, die du deshalb nicht prüfen kannst

Wenn sich der Checkout während des Audits verändert, stoppe die
Vergleichsbehauptungen, erfasse den neuen Zustand und kennzeichne das Audit
als Snapshot. Vermische keine Ergebnisse verschiedener Stände unbemerkt.

## 8. Phase B: Architektur- und Autoritätskarte

Erstelle vor der Detailkritik eine kompakte Karte:

| Gegenstand | Autoritative Quelle | Generierte Kopien | Prüfmechanismus |
|---|---|---|---|

Erfasse mindestens:

- Seitenmenge
- gemeinsame Head-Angaben
- Navigation und Kontaktkolumne
- Footer und mobile Callbar
- Telefonnummern
- Anschrift
- Sprechzeiten
- Gründungs- und Registrierungsstatus
- Einzugsgebiet und Gemeinden
- zuständige Gerichte
- Seitentitel, Description, Canonical und Open Graph
- JSON-LD
- Farben und Bildquellen
- Sitemap und `lastmod`
- Hosting- und Datenschutzangaben
- rechtliche und fachliche Aussagen

Bewerte für jeden Gegenstand:

- Gibt es genau eine echte Autorität?
- Ist die Autorität für einen neuen Menschen auffindbar?
- Kann ein schwaches Modell erkennen, welche Kopie es nicht direkt ändern
  darf?
- Wird Drift automatisch erkannt?
- Ist die Aktualisierung reversibel und klein?

## 9. Phase C: Technische Prüfungen

Führe mindestens diese nichtdestruktiven Prüfungen aus:

```sh
python3 -m unittest discover -s tests -v
python3 tools/pruefe-sprache.py
shellcheck tools/*.sh tools/hooks/*
git diff --check
rg -n '\[[A-ZÄÖÜ]' -- *.html partials/*.html
rg -n -i 'codeberg|github pages|http\.server|build\.sh|schau\.sh|pruefe-sprache\.py' -- .
```

Wenn ein Pfad nicht existiert, passe nur den lesenden Befehl an und
dokumentiere die Abweichung.

### Buildprüfung

`tools/build.sh` kann HTML-Dateien schreiben. Führe es im Originalcheckout
nur aus, wenn der Arbeitsbaum nachweislich sauber ist und der Auftraggeber
dies erlaubt hat. Andernfalls:

- verlasse dich nicht nur auf einen Kommentar,
- nutze den vorhandenen temporären Buildtest,
- oder kopiere die nötigen Dateien in ein Wegwerfverzeichnis und führe den
  Build dort aus.

Prüfe:

- Idempotenz
- fehlende, doppelte, vertauschte und verschachtelte Marken
- unbekannte Marken
- fehlende Partials und Seiten
- Lesefehler und Schreibfehler
- Verhalten bei einer neuen Root-HTML-Datei
- vollständige Ersetzung der `%%CUR-*%%`-Platzhalter
- mögliche Teilaktualisierung in der abschließenden Schreibphase
- Seitensatz in Skript, Tests, README und Sitemap

### Pythonwerkzeug

Prüfe `tools/pruefe-sprache.py` mit Gegenbeispielen, nicht nur mit den
Produktionsseiten:

- Abkürzungen
- Namen mit Punktnähe
- Dezimalzahlen
- Paragraphen und Ziffern
- verschachtelte Inline-Tags
- `<br>`
- unvollständiges HTML
- leere oder extrem kurze Blöcke
- Satzende mit Kleinbuchstaben oder Anführungszeichen

Erkläre klar: Satzlängen sind ein Redaktionssignal, kein Nachweis für A2,
B1 oder Leichte Sprache.

### HTML, CSS und Assets

Prüfe mit verfügbaren Standardwerkzeugen:

- HTML-Konformität zum WHATWG HTML Living Standard
- eindeutige IDs und vorhandene Fragmente
- genau ein sinnvolles `main` und `h1` je Seite
- Überschriftenhierarchie
- Landmarks und zugängliche Namen
- fremdsprachige `lang`-Attribute
- tote CSS-Selektoren und nicht verwendete Klassen
- extrem lange Zeilen und wiederholtes Markup
- progressive CSS-Funktionen und brauchbare Fallbacks
- SVG-Zugänglichkeit und deterministische Darstellung
- tatsächliche Maße, Dateitypen und Dateigrößen der Bilddateien
- Übereinstimmung generierter Bilder mit ihren SVG-Quellen
- Druckstylesheet

Ein HTML-Parser, der eine Datei lesen kann, ist noch kein vollständiger
Konformitätsvalidator. Benenne die Reichweite des verwendeten Werkzeugs.

## 10. Phase D: Accessibility und inklusive Nutzung

Ziel ist WCAG 2.2 AA. Nutze die normative W3C-Fassung und nenne bei jedem
Verstoß das konkrete Erfolgskriterium.

Prüfe automatisiert und manuell:

- 1.1.1 Nicht-Text-Inhalte
- 1.3.1 Informationen und Beziehungen
- 1.3.2 sinnvolle Reihenfolge
- 1.4.1 Farbe nicht als einziges Mittel
- 1.4.3 Textkontrast
- 1.4.4 Textvergrößerung
- 1.4.10 Reflow bei 320 CSS-Pixeln beziehungsweise 400 Prozent
- 1.4.11 Nicht-Text-Kontrast
- 1.4.12 Textabstände
- 1.4.13 Hover- und Fokusinhalt
- 2.1.1 Tastaturbedienung
- 2.1.2 keine Tastaturfalle
- 2.3.3 Animation aus Interaktionen, soweit einschlägig
- 2.4.1 Sprungmechanismus
- 2.4.3 Fokusreihenfolge
- 2.4.7 sichtbarer Fokus
- 2.4.11 Fokus nicht verdeckt
- 2.5.8 Mindestzielgröße
- 3.1.1 Seitensprache
- 3.1.2 Sprache von Teilen
- 3.2.3 konsistente Navigation
- 3.2.4 konsistente Bezeichnung
- 4.1.2 Name, Rolle, Wert

Prüfe mindestens folgende Darstellungen:

- 320 × 800
- 390 × 844
- 768 × 1024
- 1280 × 800
- 2560 × 1440
- Hellmodus
- Dunkelmodus
- 200 Prozent Zoom
- 400 Prozent Zoom beziehungsweise 320-CSS-Pixel-Reflow
- `prefers-reduced-motion: reduce`
- erzwungene Farben beziehungsweise High Contrast
- Druckvorschau

Prüfe mit Tastatur:

- Sprunglink
- Hauptnavigation
- alle Textlinks
- mobile Callbar
- sichtbaren, nicht verdeckten Fokus
- sinnvolle Reihenfolge

Prüfe die Vorlesereihenfolge konzeptionell oder mit Screenreader. Achte
besonders auf die vor dem Hauptinhalt stehende Seitenkolumne, wiederholte
Kontaktdaten und die vielen `<br>`-Umbrüche in Leichter Sprache.

Rechne Kontraste selbst. Übernimm keine Kommentarwerte ungeprüft. Prüfe Hell-
und Dunkelmodus sowie Text, Fokusrahmen, Grenzen und Zustandsanzeige.

Eine vollständige WCAG-AA-Konformitätsaussage ist nur zulässig, wenn alle
einschlägigen A- und AA-Kriterien geprüft wurden. Sonst formuliere präzise:
„in den geprüften Kriterien kein Verstoß gefunden“.

## 11. Phase E: Fachliche und rechtliche Prüfung

Hier gilt die höchste Belegpflicht.

### Quellenregel

- Schlage jede genannte Norm in der am Prüftag geltenden Fassung nach.
- Nutze für Bundesrecht vorrangig `gesetze-im-internet.de` oder eine andere
  amtliche Primärquelle.
- Nutze für Gerichte, Behörden, Gemeinden und Zuständigkeiten amtliche
  Seiten.
- Nutze für Dokumentstände die herausgebende Stelle und das konkrete PDF.
- Behaupte keine Normbedeutung aus dem Gedächtnis.
- Gib Abrufdatum, URL und genaue Fundstelle an.
- Wenn sich eine Rechtsfrage nicht sicher klären lässt, markiere sie als
  offen und empfehle fachkundige Prüfung. Erfinde keine Gewissheit.

Prüfe insbesondere alle Aussagen zu:

- § 1814 BGB: Voraussetzungen, Erforderlichkeit und freier Wille
- § 1815 BGB: ein Aufgabenkreis und mehrere Aufgabenbereiche
- § 1816 BGB: Auswahl und Wünsche
- § 1820 BGB: Vorsorgevollmacht und Kontrollbetreuung
- § 1821 BGB: Wünsche, Grenzen, Kontakt und Wiedererlangung eigener
  Handlungsfähigkeit
- §§ 1827 und 1829 BGB: Patientenverfügung und Genehmigung
- §§ 1831 und 1832 BGB: Unterbringung, freiheitsentziehende und ärztliche
  Zwangsmaßnahmen
- § 1830 BGB und § 1817 Abs. 2 BGB: Sterilisation und besondere Bestellung
- § 1631c BGB: Minderjährige
- § 1358 BGB: Ehegattennotvertretung
- §§ 1863 und 1864 BGB: Berichte und Mitteilungen
- §§ 7 und 23 BtOG sowie BtRegV
- VBVG in der am Prüftag geltenden Fassung, insbesondere Änderungen ab
  1. Januar 2026
- Mittellosigkeit, geschütztes Vermögen und Kostenfolgen
- Umsatzsteuerdarstellung
- Abgrenzung zulässiger Betreuungstätigkeit von Rechtsberatung
- zuständige Betreuungsgerichte und Behörden

Prüfe Widersprüche zwischen einfacher Sprache, Leichter Sprache,
Fachkreisseite, Impressum und README. Eine fachlich richtige Fachseite heilt
keine falsche Kurzfassung auf der Startseite.

### Impressum und Datenschutz

Prüfe mindestens:

- § 5 DDG für zwei getrennte Diensteanbieter
- Berufsbezeichnung und Registrierungsstatus
- Berufshaftpflichtangaben
- Umsatzsteuerangabe
- inhaltlich Verantwortliche
- Art. 13 und 14 DSGVO
- tatsächliche gemeinsame Verantwortlichkeit nach Art. 26 DSGVO
- wesentliche Inhalte und tatsächliche Existenz der Vereinbarung
- tatsächlichen Hoster und dessen reale Verarbeitung
- Serverprotokolle, IP-Adressen und Speicherfristen
- E-Mail-Dienstleister und Auftragsverarbeitung
- Betroffenenrechte und Aufsichtsbehörde
- Gleichlauf von Datenschutzerklärung und realer Technik

Verifiziere zuerst den tatsächlichen Hostingzustand. Eine alte, an sich
korrekte Datenschutzerklärung eines früheren Hosters ist für den neuen Hoster
falsch.

## 12. Phase F: Inhalt, Sprache und Zielgruppen

Prüfe die vier bewusst verschiedenen Sprachebenen getrennt:

| Bereich | Erwartung |
|---|---|
| `leichte-sprache.html` | Leichte Sprache; menschliche Prüfgruppe bleibt erforderlich |
| `fachkreise.html` | präzise Fachsprache |
| `index`, `buero`, `leistungen`, `vorsorge` | Einfache Sprache, etwa A2 bis B1 |
| `impressum`, `datenschutz` | juristisches Standarddeutsch |

Prüfe:

- personenzentrierte Sprache
- keine unnötige Dramatisierung oder Bevormundung
- keine Behauptung laufender Tätigkeit vor Registrierung
- konsistente Rolle beider Personen
- konsistente Sprechzeiten, Anschrift und Erreichbarkeit
- elegante statt abgehackte Einfache Sprache
- erklärte Fachbegriffe
- klare Handlungsoptionen für Menschen unter Stress
- keine irreführende Nähe zu individueller Rechtsberatung
- keine bloße numerische Behauptung, ein Text sei A1, A2 oder B1

Für Leichte Sprache prüfe zusätzlich gegen ein benanntes Regelwerk. Ein
automatischer Satzlängentest und deine eigene Einschätzung ersetzen keine
Prüfgruppe aus Menschen mit Lernschwierigkeiten.

## 13. Phase G: Metadaten, Suche und strukturierte Daten

Prüfe für jede Seite:

- eindeutigen, passenden Titel
- Meta-Description oder begründetes Fehlen
- Canonical
- `robots`
- Open-Graph-Titel, Beschreibung, URL und Bild
- Bildmaß, Format und Alternativbeschreibung
- Deckungsgleichheit mit sichtbarem Inhalt und Gründungsstand

Prüfe zusammenhängend:

- `robots.txt`
- `sitemap.xml`
- tatsächliche indexierbare Seiten
- noindex-Seiten
- `.html`-Adressvertrag
- www-Weiterleitung
- 404-Verhalten
- `lastmod`-Werte und ihre Erzeugung

Prüfe JSON-LD auf:

- gültiges JSON
- aktuelle Schema.org-Typen und erlaubte Eigenschaften
- korrekte Identität der beschriebenen Organisation beziehungsweise Personen
- Deckungsgleichheit von Telefon, Adresse, Status und Gebiet
- semantisch passende Typen für Landkreise, Städte und Gemeinden
- sichtbare Belegbarkeit der strukturierten Angaben
- unnötige oder irreführende Detailtiefe

Ein Parserfolg beweist nur Syntax, nicht Schema.org-Semantik.

## 14. Phase H: Security, Supply Chain und Deployment

Prüfe ohne pauschalen Sicherheitsalarmismus:

- reale externe Ressourcen und Datenabflüsse
- Wirksamkeit und Grenzen der Meta-CSP
- verbotene oder unnötig gelockerte CSP-Direktiven
- HTTPS- und Mixed-Content-Risiken
- publizierte Root-Dateien und Jekyll-Ausschlüsse
- Gefahr durch `.nojekyll`
- Offenlegung interner Partials, Tests und Tools
- GitHub-Actions-Berechtigungen
- Pinning von Actions an vollständige Commit-SHAs
- festgelegte Runner- und Python-Version
- mögliche Secret-Nutzung
- DNS-, CNAME- und Redirectdokumentation
- reale Hostingkonfiguration gegenüber README und Datenschutz

Prüfe nach möglicher Veröffentlichung ausdrücklich:

```text
/tools/build.sh
/partials/rail.html
/tests/test_site.py
/AGENTS.md
/README.md
/docs/review-prompt.md
```

Diese Werkstattdateien sollen nicht öffentlich ausgeliefert werden. Prüfe
auch, welche nicht ausgeschlossenen Root-Dateien absichtlich öffentlich sind.

## 15. Phase I: Maintainability für Menschen und schwache Modelle

Führe zusätzlich einen Änderbarkeitstest als Gedankenexperiment durch. Ändere
nichts, sondern beschreibe für jede Aufgabe die nötigen Fundstellen, Schritte
und Fehlermöglichkeiten:

1. Telefonnummer einer Person ändern
2. Anschrift ändern
3. Sprechzeiten ändern
4. neue Inhaltsseite hinzufügen
5. Seite aus der Sitemap entfernen
6. Hoster wechseln
7. Gesetzesstand aktualisieren
8. Einzugsgebiet ändern
9. Farbpalette ändern
10. Website zur Veröffentlichung freigeben

Bewerte je Szenario:

- Zahl der Autoritäten und Kopien
- klare Reihenfolge
- automatischer Driftcheck
- Risiko stiller Teilerledigung
- Rückbaubarkeit
- Verständlichkeit ohne Vorwissen

Prüfe außerdem:

- Kann ein neuer Mensch in zehn Minuten das Repositorymodell erklären?
- Kann ein kleines Modell erkennen, welche Bereiche generiert sind?
- Sind Dateinamen, Variablen, Kommentare und Befehle konsistent?
- Gibt es lange, verrauschte oder wiederholte Blöcke, die Diffs und Kontext
  unnötig vergrößern?
- Gibt es genau einen read-only Prüfentrypoint?
- Tun lokale Prüfung, Hook und CI tatsächlich dasselbe?
- Verändert ein Prüfbefehl unerwartet Dateien oder den Git-Index?
- Sind Voraussetzungen und unterstützte Toolversionen dokumentiert?
- Ist ein Rollback ohne Spezialwissen möglich?

Bevorzuge für dieses kleine Projekt einfache Lösungen. Empfehle kein
Framework, Paketmanagement oder CMS ohne nachgewiesenen Nutzen, klare Kosten
und eine kleinere Gesamtrisikooberfläche.

## 16. Geforderte Befundqualität

Jeder Befund muss dieses Format haben:

```text
[SCHWERE] ID · Datei:Zeile — präziser Kurztitel

Beobachtung:
Was im aktuellen Checkout tatsächlich steht oder passiert.

Beleg:
Reproduzierbarer Befehl, Messwert, Testausgabe oder externe Primärquelle.

Standard oder Vertrag:
Konkretes WCAG-Kriterium, Gesetz, HTML-Regel, Projektregel oder begründetes
Maintainability-Prinzip. Keine Floskel wie „Best Practice“ ohne Inhalt.

Folge:
Konkretes Risiko für Leser, Recht, Veröffentlichung, Wartung oder Änderung.

Empfehlung:
Kleinste tragfähige Korrektur. Keine unaufgeforderte Implementierung.

Vertrauen:
hoch, mittel oder niedrig, mit kurzer Begründung.
```

Verwende aktuelle Zeilennummern, zum Beispiel mit `nl -ba`. Rate keine
Zeilennummern. Fasse gleiche Ursachen in einem Befund zusammen.

### Schweregrade

| Stufe | Definition |
|---|---|
| **KRITISCH** | akute falsche Rechts- oder Pflichtinformation, erheblicher Datenschutzfehler, Veröffentlichung gefährdet Betroffene oder wesentliche Zielgruppe kann die Seite nicht nutzen |
| **HOCH** | Release-Blocker, belegter Sachfehler, WCAG-A/AA-Verstoß, defekter Kernworkflow oder erheblicher Widerspruch |
| **MITTEL** | reales Wartungs-, Drift-, Verständlichkeits- oder Qualitätsrisiko ohne unmittelbaren schweren Schaden |
| **NIEDRIG** | begrenzter Feinschliff mit nachvollziehbarem Nutzen |

Geschmack ohne nachweisbare Folge ist kein Befund.

## 17. Geforderter Abschlussbericht

Liefere den Bericht in dieser Reihenfolge:

1. **Executive Summary** mit klarem Gesamturteil
2. **geprüfter Snapshot** mit Commit, Git-Zustand, Datum und Grenzen
3. **Repositorykarte** mit Rollen und Autoritäten
4. **Prüfmatrix**: Bereich, Methode, Ergebnis, Abdeckung
5. **Befunde**, absteigend nach Schwere
6. **nachweislich positive Eigenschaften**
7. **Maintainability für Menschen**
8. **Maintainability für schwache Modelle**
9. **Veröffentlichungsurteil**:
   - jetzt veröffentlichungsreif: ja oder nein
   - nach Füllen bekannter Platzhalter veröffentlichungsreif: ja oder nein
   - jeweils mit Begründung
10. **priorisierter Maßnahmenplan**:
    - P0 vor Veröffentlichung
    - P1 kurzfristig
    - P2 nach Stabilisierung
11. **nicht geprüfte oder nicht prüfbare Punkte** mit Grund
12. **Quellenverzeichnis** nur mit tatsächlich verwendeten Quellen

Trenne bei den Empfehlungen:

- zwingende Korrektur
- sinnvolle Härtung
- optionale Verbesserung

Gib keine pauschale Prozentnote. Eine Ampel oder Teilbewertung ist nur
zulässig, wenn ihre Kriterien vorher definiert sind.

## 18. Qualitätskontrolle vor Abgabe

Prüfe deinen eigenen Bericht vor der Abgabe:

- Ist jeder schwere Befund durch Primärbeleg oder reproduzierbaren Test
  getragen?
- Hast du aktuelle Realität und dokumentierte Absicht getrennt?
- Hast du einen grünen Test nicht als vollständige Freigabe missverstanden?
- Hast du bekannte offene Punkte gebündelt statt dupliziert?
- Hast du bewusste Entscheidungen respektiert, aber konkrete Folgen trotzdem
  geprüft?
- Hast du keine Rechtsnorm aus dem Gedächtnis behauptet?
- Hast du keine nicht ausgeführte Browser- oder Screenreaderprüfung als
  bestanden dargestellt?
- Hast du keine Datei verändert?
- Sind Empfehlungen proportional zur kleinen statischen Architektur?
- Kann der Auftraggeber jeden Befund ohne Rückfrage nachvollziehen?

Wenn eine dieser Fragen mit Nein beantwortet wird, überarbeite den Bericht
vor der Abgabe.
