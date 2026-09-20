# Meta-Prompt für Review und Audit von bb-limen.de

> Übergib diesen Auftrag vollständig an das prüfende Modell und gib ihm
> lesenden Zugriff auf das gesamte Repository. Das Ergebnis ist ein Audit,
> keine automatische Reparatur.
>
> Letzte Anpassung an den Repositorystand: 20.09.2026.

## 0. Auftragsmodus — zuerst festlegen

Dieses Repository ist klein, aber bereits zweimal vollständig auditiert
worden. Ein drittes Vollaudit, das dieselben Fundstellen neu entdeckt, kostet
mehr als es einbringt. Kläre deshalb als Erstes, welcher Modus gilt. Wenn der
Auftraggeber nichts sagt, gilt **Delta-Audit**.

| Modus | Auftrag | Umfang |
|---|---|---|
| **Vollaudit** | alle Phasen A–I | nur bei grundlegendem Umbau oder vor der ersten Veröffentlichung |
| **Delta-Audit** | Phasen A, B, J plus die von der Änderung berührten Phasen | Standard nach einer Arbeitsstrecke |
| **Themenaudit** | eine benannte Phase, vollständig | wenn der Auftraggeber ein Thema nennt (Recht, Accessibility, Deployment …) |

Beim Delta-Audit ist die Vergleichsbasis der letzte auditierte Commit. Ermittle
ihn aus den vorhandenen Berichten (siehe §1.3) und nenne ihn im Bericht. Prüfe
dann:

```sh
git diff --stat <letzter-auditierter-commit>..HEAD
git log --date=iso-strict --pretty=format:'%h%x09%ad%x09%s' <letzter-auditierter-commit>..HEAD
```

Alles, was in diesem Diff liegt, wird vollständig geprüft. Alles außerhalb
wird nur dort geprüft, wo die Änderung hineinwirkt — und **immer** dort, wo
Phase J eine frühere Freigabe als möglicherweise überholt ausweist.

## 1. Rolle, Ziel und Grundlagen

### 1.1 Rolle

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

### 1.2 `AGENTS.md` ist der Vertrag

`AGENTS.md` ist keine Hintergrundlektüre, sondern der normative Maßstab
dieses Projekts; `README.md` ist das Handbuch mit den Begründungen. Beide
sind vollständig zu lesen, bevor ein Befund formuliert wird.

Daraus folgen zwei getrennte Prüffragen, die nicht vermischt werden dürfen:

- **Konformität:** Hält der Checkout die Regeln aus `AGENTS.md` ein?
- **Selbstwahrheit:** Sind die Aussagen in `AGENTS.md` und `README.md` über
  den Checkout selbst noch wahr? Zahlenangaben (Testanzahl, Anzahl der
  Fundstellen, Seitenmenge, Datumsangaben) altern still. **Zähle jede nach,
  die in diesen beiden Dateien steht.** Eine falsche Zahl im Vertrag ist ein
  eigener Befund, kein Nebensatz zu einem anderen.

Eine Regel darf kritisiert werden. Aber trenne „die Regel ist unklug" von
„die Regel wird verletzt" von „die Regel beschreibt den Ist-Zustand falsch".

### 1.3 Frühere Berichte

In `docs/` können Berichte früherer Audits liegen (`review-*.md`,
`bestandsaufnahme-*.md`). Sie sind **unversioniert** und können fehlen; nur
`docs/review-prompt.md` ist versioniert (`.gitignore`).

Wenn Berichte vorhanden sind:

- Lies sie und entnimm ihnen die Befund-IDs und den auditierten Commit.
- Behandle ihre Befunde als **Behauptungen, nicht als Wahrheit** — auch die
  positiven.
- Prüfe jeden offenen Befund erneut gegen den heutigen Checkout und weise ihn
  in Phase J als behoben, offen, verschoben oder als Fehlbefund aus.
- Melde einen bereits gemeldeten, unveränderten Befund nicht als neuen Fund,
  sondern unter seiner alten ID mit dem Vermerk „unverändert offen".

Wenn keine Berichte vorhanden sind, halte das im Bericht fest und arbeite
ohne Delta-Teil.

## 2. Strikte Arbeitsgrenzen

Arbeite grundsätzlich **read-only**.

- Ändere, verschiebe, lösche, formatiere oder stage keine Datei des
  Projekts.
- Führe keinen Commit, Push, Merge, Rebase oder Deployment aus.
- Führe kein `git init`, `git reset`, `git checkout --`, `git clean`,
  `git stash` oder andere wiederherstellende beziehungsweise destruktive
  Befehle aus.
- Installiere keine Abhängigkeiten und ändere keine globale oder lokale
  Konfiguration.
- Aktiviere keine Git-Hooks und führe `tools/einrichten.sh` nicht aus; es
  schreibt `core.hooksPath`.
- Trage keine Platzhalter aus Vermutungen ein.
- Veröffentliche die Website nicht und löse keinen Workflow aus
  (`workflow_dispatch` bleibt unangetastet).
- Wenn ein Prüfbefehl Dateien verändern kann, verwende eine Wegwerfkopie oder
  erkläre, warum du ihn nicht ausgeführt hast.

**Einzige Schreibausnahme:** die Berichtsdatei selbst, und nur dann, wenn der
Auftraggeber einen Pfad nennt. Sie gehört nach `docs/` und ist dort
unversioniert. Lege keine weiteren Dateien an — auch keine Notizen, Skripte
oder Zwischenstände im Projektverzeichnis. Temporäres gehört außerhalb des
Repositorys, etwa unter `/tmp`.

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

Eine Besonderheit dieses Repositorys: die Bereiche zwischen den Marken
`<!-- #name -->` und `<!-- /#name -->` in den Seiten sind **generierte
Kopien**. Ein Befund, der dort eine Zeilennummer nennt, ohne die Autorität in
`partials/` zu benennen, führt zu einer Korrektur, die der nächste Build
löscht. Nenne bei generiertem Inhalt immer beides: die Fundstelle und die
Quelle.

## 4. Projektkontext, der zu verifizieren ist

Behandle die folgenden Angaben als Ausgangshypothesen, nicht als ungeprüfte
Wahrheiten. Sie beschreiben den Stand vom 20.09.2026 und können überholt
sein — prüfe jede gegen den Checkout und melde jede Abweichung.

**Büro und Personen**

- Büro für rechtliche Betreuung in Binzen, Baden-Württemberg
- zwei freiberuflich tätige Personen (Aranda Möller, Mika Möller) ohne
  gemeinsame Gesellschaft
- Registrierungen nach § 23 BtOG personenbezogen beantragt bei der
  Betreuungsbehörde des Landratsamts Lörrach, beide noch nicht erteilt
- Einzugsgebiet: Landkreise Lörrach und Waldshut

**Technik**

- neun HTML-Seiten einschließlich `404.html`: `index`, `betreuung`,
  `aufgaben`, `vorsorge`, `fachkreise`, `leichte-sprache`, `impressum`,
  `datenschutz`, `404`
- ein gemeinsames Stylesheet `style.css`, keine Abhängigkeiten
- kein ausführbares Browser-JavaScript
- keine extern geladenen Schriften, Skripte, Karten, Tracker oder Formulare;
  durchgesetzt per Meta-CSP in `partials/head.html`
- Zielhosting: GitHub Pages aus dem Branch `main`, eigene Domain über `CNAME`
- fünf Bausteine in `partials/`: `head`, `skip`, `rail`, `foot`, `callbar`
- `tools/build.sh` setzt sie zwischen die generierten Marken und ersetzt die
  `%%CUR-*%%`-Navigationsplatzhalter
- ausgelieferte Wurzeldateien außer den Seiten: `style.css`, `robots.txt`,
  `sitemap.xml`, `vorschau.png`, `favicon.ico`, `apple-touch-icon.png`,
  `CNAME`, `LICENSE`
- `_config.yml` hält `README.md`, `AGENTS.md`, `CLAUDE.md`, `docs/`,
  `partials/`, `tests/` und `tools/` aus der Auslieferung
- `CLAUDE.md` ist eine Weiche auf `AGENTS.md`, kein eigener Inhalt

**Prüfung**

- Regressionstests in `tests/`, sechs Dateien: `test_site`, `test_build`,
  `test_angaben`, `test_begriffe`, `test_kontrast`, `test_pruefe_sprache`
- zwei CI-Workflows: `.github/workflows/pruefung.yml` (Tests, Build-Drift,
  Satzlängen, Assets, Platzhalterwarnung, HTML-Validierung, Bildvergleich)
  und `.github/workflows/verweise.yml` (monatliche Prüfung externer Verweise,
  legt ein Issue an)
- lokale Werkzeuge: `build.sh`, `pruefe-sprache.py`, `sitemap.sh`,
  `ansicht.sh`, `schau.sh`, `browser.sh`, `vorschau.sh`, `vergleiche.py`,
  `einrichten.sh`, `hooks/pre-commit`
- mehrere bewusst unterschiedliche Sprachebenen

**Ausdrücklich nachzuzählen, nicht zu übernehmen:** Anzahl der Tests, Anzahl
der Gemeinden im Einzugsgebiet, Anzahl der Seiten in Skript, Tests, README
und Sitemap, Anzahl der Fundstellen jeder doppelt gepflegten Angabe aus
`AGENTS.md` §6.

## 5. Bewusste Projektentscheidungen

Die folgenden Entscheidungen sind nicht allein deshalb Fehler, weil eine
größere oder modernere Website sie anders treffen könnte:

- kein JavaScript
- kein Kontaktformular
- keine Webfonts und keine externen Subressourcen
- keine eingebettete Karte
- kein Analytics und kein Cookie-Banner
- fremde Formulare werden verlinkt, nicht im Repository gehostet
- klassische `.html`-Adressen (entschieden am 20.09.2026)
- Impressum und Datenschutz im Footer und in der Seitenkolumne statt in der
  Hauptnavigation
- juristisches Standarddeutsch in Impressum und Datenschutz
- kein Portraitfoto und keine Vita
- vollständige HTML-Seiten im Repository statt eines Framework-Builds
- Ornamente als Inline-SVG (`.zierblatt`) statt als Schmuckzeichen im Text
- kein `.nojekyll`, weil Jekyll den Auslieferungsausschluss durchsetzt

Melde eine solche Entscheidung nur, wenn du einen konkreten, belegten Nachteil
im vorliegenden Projekt nachweist. Eine bewusste Entscheidung ist aber keine
Immunität: Wenn Umsetzung, Dokumentation oder Rechtsfolge widersprüchlich
sind, melde den konkreten Widerspruch.

## 6. Bekannte offene Zustände

**Platzhalter.** Text in eckigen Klammern (`[ANGABE]`) ist ein bewusster
offener Posten. Zum Stand 20.09.2026 ist **keiner mehr vorhanden**; die
Telefonnummer ist eingetragen und verlinkt. Prüfe das nach:

```sh
grep -rn '\[[A-ZÄÖÜ]' -- *.html partials/
```

- Wenn der Befehl nichts findet: die Warnstufe in `pruefung.yml` ist jetzt
  eine Regressionsbremse, kein Freigabehindernis mehr. Prüfe, ob README und
  `AGENTS.md` noch von offenen Platzhaltern sprechen, und melde den
  Widerspruch.
- Wenn er etwas findet: erfinde die Daten nicht, liste denselben generierten
  Platzhalter nicht neunmal als neun Fehler, und bewerte, ob der
  Release-Prozess eine Veröffentlichung mit offenen Stellen zuverlässig
  verhindert.

**Echte Freigabegrenzen**, die fortbestehen:

- Die Registrierungen nach § 23 BtOG sind nicht erteilt. Der Gründungshinweis
  muss auf allen fünf Inhaltsseiten und im Impressum stehen und verschwindet
  erst mit der Registrierungsnummer, dann überall gleichzeitig
  (`AGENTS.md` §7). Zähle die Fundstellen.
- Die Prüfgruppe aus Menschen mit Lernschwierigkeiten hat
  `leichte-sprache.html` nicht gegengelesen. Bis dahin kein Europäisches
  Leichte-Sprache-Logo.
- Datumsangaben („Stand 19. September 2026") altern. Prüfe, ob sie zueinander
  und zum letzten inhaltlichen Commit passen.

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
git ls-files | sort
find . -path ./.git -prune -o -type f -print | sort
git config --get core.hooksPath
```

Der Unterschied zwischen den letzten beiden Auflistungen ist wichtig:
unversionierte Verzeichnisse wie `tmp/`, `.agents/`, `.codex/` oder
`__pycache__/` liegen im Arbeitsbaum, sind aber weder versioniert noch
ausgeliefert. Verwechsle sie nicht mit Projektinhalt.

Lies danach vollständig:

- `AGENTS.md`
- `README.md`
- `CLAUDE.md`
- `.gitignore`
- `_config.yml`
- `.editorconfig`
- `.github/workflows/pruefung.yml`
- `.github/workflows/verweise.yml`
- `docs/review-prompt.md` (diese Datei)
- vorhandene Berichte in `docs/` (siehe §1.3)

Notiere im Bericht:

- Commit-ID und Modus (§0)
- Branch und Remote-Abweichung
- sauberer oder veränderter Arbeitsbaum
- unversionierte und ignorierte relevante Dateien
- Zeitpunkt und Zeitzone
- verfügbare Werkzeuge (`rg`, `shellcheck`, `html5validator`, `python3`,
  Browser, Pillow) und ob Netzzugriff besteht
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
- gemeinsame Head-Angaben und CSP
- Navigation, `aria-current` und Kontaktkolumne
- Footer und mobile Callbar
- Telefonnummer
- Anschrift
- Sprechzeiten
- Gründungs- und Registrierungsstatus
- Einzugsgebiet und Gemeinden
- zuständige Gerichte und Behörden
- Seitentitel, Description, Canonical und Open Graph
- JSON-LD
- Farben (`PALETTE` in `style.css`) und Bildquellen
- Signet und Zierblatt-SVG
- Sitemap und `lastmod`
- Hosting- und Datenschutzangaben
- rechtliche und fachliche Aussagen

Bewerte für jeden Gegenstand:

- Gibt es genau eine echte Autorität?
- Ist die Autorität für einen neuen Menschen auffindbar?
- Kann ein schwaches Modell erkennen, welche Kopie es nicht direkt ändern
  darf?
- Wird Drift automatisch erkannt — durch Test, Hook oder CI?
- Ist die Aktualisierung reversibel und klein?

Gleiche die Karte ausdrücklich gegen die Tabelle der doppelt gepflegten
Angaben in `AGENTS.md` §6 ab. Jede Angabe dort muss in deiner Karte
auftauchen; jede Angabe in deiner Karte mit mehr als einer Fundstelle, die
dort fehlt, ist ein Befund gegen den Vertrag.

## 9. Phase C: Technische Prüfungen

Führe mindestens diese nichtdestruktiven Prüfungen aus:

```sh
python3 -m unittest discover -s tests -v
python3 tools/pruefe-sprache.py
shellcheck tools/*.sh tools/hooks/pre-commit
python3 -m py_compile tools/pruefe-sprache.py tools/vergleiche.py
git diff --check
grep -rn '\[[A-ZÄÖÜ]' -- *.html partials/
grep -rn -i 'codeberg\|github pages\|http\.server\|build\.sh\|schau\.sh\|pruefe-sprache\.py' .
```

`rg` ist schneller, aber nicht überall vorhanden; die `grep`-Fassungen oben
sind der Rückfallweg. Wenn ein Pfad oder Werkzeug fehlt, passe nur den
lesenden Befehl an und dokumentiere die Abweichung.

Zähle die tatsächlich gelaufenen Tests und vergleiche sie mit der Zahl in
`AGENTS.md` §8.

### Buildprüfung

`tools/build.sh` schreibt HTML-Dateien. Führe es im Originalcheckout **nicht**
aus. Es gibt drei gangbare Wege, in dieser Reihenfolge:

1. `tests/test_build.py` prüft das Skript bereits in einem Wegwerfverzeichnis
   — lies, was es abdeckt, und schließe die Lücken.
2. Kopiere Seiten, `partials/` und `tools/` in ein Verzeichnis außerhalb des
   Repositorys und lasse den Build dort laufen.
3. Nur wenn der Arbeitsbaum nachweislich sauber ist **und** der Auftraggeber
   es ausdrücklich erlaubt hat: ausführen und anschließend
   `git diff --exit-code` zeigen.

Verlasse dich nie auf einen Kommentar im Skript als Beleg für sein Verhalten.

Prüfe:

- Idempotenz (zweiter Lauf erzeugt keinen Diff)
- fehlende, doppelte, vertauschte und verschachtelte Marken
- unbekannte Marken und Marken, die nicht allein in ihrer Zeile stehen
- erzwungene Reihenfolge `head skip rail foot callbar`
- fehlende Partials und Seiten
- Lesefehler und Schreibfehler
- Verhalten bei einer neuen Root-HTML-Datei, die nicht in `SEITEN` steht
- vollständige Ersetzung der `%%CUR-*%%`-Platzhalter und korrektes
  `aria-current="page"` je Seite
- die abschließende Schreibphase: bleibt der Originalstand bei einem Fehler
  an einer späten Seite unverändert?
- Aufräumen des `.build.*`-Verzeichnisses, auch bei Abbruch
- Seitensatz in Skript, Tests, README und Sitemap — vier Listen, eine
  Wahrheit

### Pythonwerkzeuge

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

Prüfe `tools/vergleiche.py` und `tools/ansicht.sh` darauf, ob ein Fehlschlag
sichtbar wird oder als Erfolg durchgeht: nicht gestarteter Server, leeres
Ausgabeverzeichnis, null verglichene Bilder, fehlender Browser, fehlendes
Pillow. Ein Bildvergleich, der bei null Bildern „keine Unterschiede" meldet,
ist schlimmer als keiner.

### Shellwerkzeuge

`ansicht.sh`, `schau.sh`, `browser.sh`, `vorschau.sh`, `sitemap.sh` und
`einrichten.sh` starten Server, Browser oder schreiben Dateien. Lies sie,
führe sie nicht aus. Prüfe:

- `set -eu`, Quoting, Umgang mit Pfaden mit Leerzeichen
- gebundene Ports und was bei belegtem Port geschieht
- Aufräumen gestarteter Hintergrundprozesse
- welche Dateien geschrieben werden und wohin
- ob `sitemap.sh` `lastmod` aus Git oder aus der Systemzeit ableitet und ob
  das reproduzierbar ist
- ob `einrichten.sh` `core.hooksPath` setzt und ob das dokumentiert ist
- ob `hooks/pre-commit` genau dieselben Prüfungen ausführt wie CI und
  `AGENTS.md` §8

### HTML, CSS und Assets

Prüfe mit verfügbaren Standardwerkzeugen:

- HTML-Konformität zum WHATWG HTML Living Standard
- eindeutige IDs und vorhandene Fragmente
- genau ein sinnvolles `main` und `h1` je Seite
- Überschriftenhierarchie
- Landmarks und zugängliche Namen
- fremdsprachige `lang`-Attribute
- tote CSS-Selektoren und nicht verwendete Klassen
- den `PALETTE`-Block als einzige Farbautorität: stehen Farbwerte auch
  außerhalb, etwa in Inline-SVG, `theme-color`, `favicon`-Data-URI oder
  `tools/*.svg`? Jede Fundstelle außerhalb ist eine zweite Autorität.
- die Regel aus `AGENTS.md` §5: `--gut` genau viermal im Fließtext
  (`index` 1, `betreuung` 1, `aufgaben` 2) — nachzählen, nicht schätzen
- die Regel aus `AGENTS.md` §2: kein Schmuckzeichen, das nicht in der
  Serifenschrift steht. Suche nach Zeichen außerhalb von Latin-1 und der
  üblichen Typografie (❦ ❧ ✦ ❖ und Verwandte) im ausgelieferten Text.
- extrem lange Zeilen und wiederholtes Markup; besonders die mehrfach inline
  wiederholten SVGs
- progressive CSS-Funktionen und brauchbare Fallbacks
- SVG-Zugänglichkeit (`aria-hidden`, `focusable`) und deterministische
  Darstellung
- tatsächliche Maße, Dateitypen und Dateigrößen von `vorschau.png`,
  `favicon.ico`, `apple-touch-icon.png`
- Übereinstimmung der generierten Bilder mit ihren SVG-Quellen in `tools/`
  und ob der Weg dorthin reproduzierbar dokumentiert ist
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

Achte besonders auf den Umschlagpunkt, an dem aus der stehenden Kolumne ein
schmales Kopfband wird, und auf die mobile Callbar: überdeckt sie Inhalt oder
Fokus am unteren Rand (2.4.11), und ist ihre Zielgröße ausreichend (2.5.8)?

Prüfe mit Tastatur:

- Sprunglink
- Hauptnavigation und die gesondert gestellte Sondernavigation
- alle Textlinks
- mobile Callbar
- sichtbaren, nicht verdeckten Fokus
- sinnvolle Reihenfolge

Prüfe die Vorlesereihenfolge konzeptionell oder mit Screenreader. Achte
besonders auf die vor dem Hauptinhalt stehende Seitenkolumne, wiederholte
Kontaktdaten und die vielen `<br>`-Umbrüche in Leichter Sprache.

Rechne Kontraste selbst; `tests/test_kontrast.py` prüft eine Auswahl, nicht
alles. Übernimm keine Kommentarwerte ungeprüft. Prüfe Hell- und Dunkelmodus
sowie Text, Fokusrahmen, Grenzen und Zustandsanzeige. `AGENTS.md` §5 nennt
4,65:1 als schwächste Paarung — verifiziere diese Zahl und suche nach einer
schwächeren, die der Test nicht abdeckt.

Eine vollständige WCAG-AA-Konformitätsaussage ist nur zulässig, wenn alle
einschlägigen A- und AA-Kriterien geprüft wurden. Sonst formuliere präzise:
„in den geprüften Kriterien kein Verstoß gefunden".

## 11. Phase E: Fachliche und rechtliche Prüfung

Hier gilt die höchste Belegpflicht.

### Quellenregel

- Schlage jede genannte Norm in der am Prüftag geltenden Fassung nach.
- Nutze für Bundesrecht vorrangig `gesetze-im-internet.de` oder eine andere
  amtliche Primärquelle.
- Nutze für Gerichte, Behörden, Gemeinden und Zuständigkeiten amtliche
  Seiten.
- Nutze für Dokumentstände die herausgebende Stelle und das konkrete PDF.
- Behaupte keine Normbedeutung aus dem Gedächtnis. Genau so ist der schwerste
  Fehler dieser Seite entstanden: eine erfundene Aufzählung zu § 1820 Abs. 2
  BGB, die im Gesetz nicht steht.
- Gib Abrufdatum, URL und genaue Fundstelle an.
- Wenn sich eine Rechtsfrage nicht sicher klären lässt, markiere sie als
  offen und empfehle fachkundige Prüfung. Erfinde keine Gewissheit.
- Ohne Netzzugriff wird Phase E **nicht** durchgeführt. Melde sie als nicht
  prüfbar, statt aus dem Gedächtnis zu urteilen.

Prüfe insbesondere alle Aussagen zu:

- § 1814 BGB: Voraussetzungen, Erforderlichkeit und freier Wille
- § 1815 BGB: ein Aufgabenkreis, bestehend aus einem oder mehreren
  Aufgabenbereichen. Der Plural „Aufgabenkreise" ist die Fassung vor dem
  01.01.2023 und darf nirgends stehen — auch nicht in README, Kommentaren
  oder Tests.
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
- §§ 7 und 23 BtOG sowie BtRegV, einschließlich der Beglaubigungsbefugnis
  und der genannten Gebühr
- VBVG in der am Prüftag geltenden Fassung, insbesondere Änderungen ab
  1. Januar 2026
- Mittellosigkeit, geschütztes Vermögen und Kostenfolgen
- Umsatzsteuerdarstellung
- Abgrenzung zulässiger Betreuungstätigkeit von Rechtsberatung
- zuständige Betreuungsgerichte und Behörden — Zahl und Namen müssen über
  alle Seiten hinweg dieselben sein

Prüfe Widersprüche zwischen einfacher Sprache, Leichter Sprache,
Fachkreisseite, Impressum und README. Eine fachlich richtige Fachseite heilt
keine falsche Kurzfassung auf der Startseite.

### Impressum und Datenschutz

Prüfe mindestens:

- § 5 DDG für zwei getrennte Diensteanbieter
- Berufsbezeichnung und Registrierungsstatus je Person
- Berufshaftpflichtangaben je Person (§ 23 Abs. 1 Nr. 3 BtOG)
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

Verifiziere zuerst den tatsächlichen Hostingzustand: `CNAME`, `_config.yml`,
die CI-Kommentare und die Commit-Geschichte sagen, wer ausliefert. Eine alte,
an sich korrekte Datenschutzerklärung eines früheren Hosters ist für den
neuen Hoster falsch. Das war bereits ein Befund — prüfe, ob er geschlossen
ist und ob die Angabe jetzt an **allen** Stellen dieselbe ist.

## 12. Phase F: Inhalt, Sprache und Zielgruppen

Prüfe die vier bewusst verschiedenen Sprachebenen getrennt, und verbessere
niemals den Stil einer Seite nach dem Maßstab einer anderen:

| Bereich | Erwartung |
|---|---|
| `leichte-sprache.html` | Leichte Sprache, etwa A1, ein Satz je Zeile; menschliche Prüfgruppe bleibt erforderlich |
| `fachkreise.html` | präzise Fachsprache, Paragraphen ohne Erklärung |
| `index`, `betreuung`, `aufgaben`, `vorsorge`, `404` | Einfache Sprache, etwa A2 bis B1 |
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

Titel, Description, Canonical und `og:`-Angaben stehen bewusst **einzeln in
jeder Seite** und nicht in `partials/head.html` (`AGENTS.md` §1). Melde es
nicht als Duplikation; prüfe stattdessen, ob ein Werkzeug ihre Vollständigkeit
und Eindeutigkeit überwacht.

Prüfe zusammenhängend:

- `robots.txt`
- `sitemap.xml`: enthaltene und fehlende Seiten. Zum Stand 20.09.2026 fehlen
  `impressum`, `datenschutz` und `404`. Kläre, ob das gewollt ist, ob es
  irgendwo begründet steht, und ob ein Test die Menge bewacht.
- tatsächliche indexierbare Seiten und noindex-Seiten
- `.html`-Adressvertrag
- www-Weiterleitung und `CNAME`
- 404-Verhalten unter GitHub Pages mit eigener Domain
- `lastmod`-Werte, ihre Erzeugung durch `tools/sitemap.sh` und ob sie mit den
  letzten inhaltlichen Änderungen übereinstimmen

Prüfe JSON-LD auf:

- gültiges JSON
- aktuelle Schema.org-Typen und erlaubte Eigenschaften
- korrekte Identität der beschriebenen Organisation beziehungsweise Personen
- Deckungsgleichheit von Telefon, Adresse, Sprechzeiten, Status und Gebiet
  mit dem sichtbaren Text
- `areaServed`: zähle die Einträge und gleiche sie mit der Zahl im Fließtext
  und der Zahl in `AGENTS.md` §6 ab. Drei Quellen, eine Wahrheit.
- semantisch passende Typen für Landkreise, Städte und Gemeinden
- sichtbare Belegbarkeit der strukturierten Angaben
- unnötige oder irreführende Detailtiefe
- ob `openingHours` maschinell dasselbe sagt wie die Kolumne im Klartext

Ein Parserfolg beweist nur Syntax, nicht Schema.org-Semantik.

## 14. Phase H: Security, Supply Chain und Deployment

Prüfe ohne pauschalen Sicherheitsalarmismus:

- reale externe Ressourcen und Datenabflüsse aus den ausgelieferten Seiten
- Wirksamkeit und Grenzen der Meta-CSP: welche Direktiven ein `<meta>`
  überhaupt durchsetzen kann und welche nur im HTTP-Header wirken
- verbotene oder unnötig gelockerte CSP-Direktiven; die Data-URI im
  `favicon`-`link` gegen `img-src 'self' data:`
- HTTPS- und Mixed-Content-Risiken
- publizierte Root-Dateien und Jekyll-Ausschlüsse
- Gefahr durch ein nachträglich angelegtes `.nojekyll`
- Offenlegung interner Partials, Tests und Tools
- GitHub-Actions-Berechtigungen: `pruefung.yml` hat `contents: read`,
  `verweise.yml` zusätzlich `issues: write`. Ist das das Minimum?
- Pinning von Actions an vollständige Commit-SHAs statt an bewegliche Tags
  (`actions/checkout@v4`, `actions/setup-java@v4`,
  `actions/upload-artifact@v4`)
- ungepinnte Installationen zur Laufzeit (`pip install html5validator`,
  `pip install pillow`, `apt-get install`) und was ein kompromittiertes
  Upstream-Paket im CI-Kontext erreichen könnte
- festgelegte Runner- und Python-Version
- mögliche Secret-Nutzung; `GH_TOKEN` in `verweise.yml`
- den ausgehenden Netzverkehr der Verweisprüfung: sie ruft fremde Adressen
  aus dem Repository mit einem erkennbaren User-Agent ab. Kann ein
  eingeschleuster Link dort etwas auslösen, und ist der Fallback
  `gh issue create ... --label ""` robust?
- DNS-, CNAME- und Redirectdokumentation
- reale Hostingkonfiguration gegenüber README und Datenschutz

Prüfe nach möglicher Veröffentlichung ausdrücklich, dass diese Adressen nicht
erreichbar sind:

```text
/tools/build.sh
/partials/rail.html
/tests/test_site.py
/AGENTS.md
/CLAUDE.md
/README.md
/docs/review-prompt.md
```

Prüfe auch, welche nicht ausgeschlossenen Root-Dateien absichtlich öffentlich
sind — `LICENSE`, `CNAME`, `robots.txt`, `sitemap.xml`, die Bilddateien — und
ob `AGENTS.md` §2 („keine neue Datei im Wurzelverzeichnis ohne Entscheidung")
für jede davon eingehalten wurde.

## 15. Phase I: Maintainability für Menschen und schwache Modelle

Führe einen Änderbarkeitstest als Gedankenexperiment durch. Ändere nichts,
sondern beschreibe für jede Aufgabe die nötigen Fundstellen, Schritte und
Fehlermöglichkeiten:

1. Telefonnummer ändern
2. zweite, persönliche Telefonnummer hinzufügen
3. Anschrift ändern
4. Sprechzeiten ändern
5. neue Inhaltsseite hinzufügen
6. Seite aus der Sitemap entfernen
7. Hoster wechseln
8. Gesetzesstand aktualisieren
9. Einzugsgebiet ändern
10. Farbpalette ändern
11. Signet oder Vorschaubild ändern
12. Gründungshinweis entfernen, sobald die Registrierungsnummern vorliegen
13. Website zur Veröffentlichung freigeben

Bewerte je Szenario:

- Zahl der Autoritäten und Kopien
- klare Reihenfolge
- automatischer Driftcheck
- Risiko stiller Teilerledigung
- Rückbaubarkeit
- Verständlichkeit ohne Vorwissen

Prüfe außerdem:

- Kann ein neuer Mensch in zehn Minuten das Repositorymodell erklären?
- Kann ein kleines Modell erkennen, welche Bereiche generiert sind — allein
  aus der Datei, die es geöffnet hat, ohne `AGENTS.md` gelesen zu haben?
- Sind Dateinamen, Variablen, Kommentare und Befehle konsistent?
- Gibt es lange, verrauschte oder wiederholte Blöcke, die Diffs und Kontext
  unnötig vergrößern?
- Gibt es genau einen read-only Prüfentrypoint?
- Tun lokale Prüfung (`AGENTS.md` §8), Hook (`tools/hooks/pre-commit`) und CI
  (`pruefung.yml`) tatsächlich dasselbe? Benenne jede Prüfung, die nur an
  einer der drei Stellen läuft.
- Verändert ein Prüfbefehl unerwartet Dateien oder den Git-Index? Der Hook
  darf laut `AGENTS.md` §8 eine vergessene Bausteinübertragung berichtigen
  und vormerken — prüfe, ob das gewollt transparent geschieht.
- Sind Voraussetzungen und unterstützte Toolversionen dokumentiert?
- Ist ein Rollback ohne Spezialwissen möglich?
- Ziehen `AGENTS.md` und `README.md` bei einer Regeländerung tatsächlich
  gemeinsam nach, wie §10 es verlangt? Stichprobe über die Commit-Geschichte.

Bevorzuge für dieses kleine Projekt einfache Lösungen. Empfehle kein
Framework, Paketmanagement oder CMS ohne nachgewiesenen Nutzen, klare Kosten
und eine kleinere Gesamtrisikooberfläche. Jede vorgeschlagene neue Datei,
jedes neue Werkzeug und jede neue Prüfung ist zugleich neue Wartungslast —
benenne sie.

## 16. Phase J: Regressionen und Stand früherer Befunde

Nur wenn frühere Berichte vorliegen (§1.3).

Erstelle eine Tabelle:

| Alte ID | Titel | Schwere damals | Stand heute | Beleg |
|---|---|---|---|---|

Zulässige Werte für „Stand heute": **behoben**, **teilweise behoben**,
**unverändert offen**, **verschlimmert**, **gegenstandslos**,
**Fehlbefund**. Jeder Wert braucht einen Beleg aus dem heutigen Checkout —
nicht aus einer Commitnachricht.

Prüfe zusätzlich auf **Regressionen**: Stellen, die ein früherer Bericht
ausdrücklich als in Ordnung bezeichnet hat und die seither geändert wurden.
Die drei jüngsten Arbeitsstrecken betrafen Startseite, Navigation,
Kontaktwege, Sondernavigation, Mobilansicht und Farbpalette — dort ist die
Regressionswahrscheinlichkeit am höchsten, besonders bei Kontrast,
Fokussichtbarkeit und der Zahl der `--gut`-Fundstellen.

## 17. Geforderte Befundqualität

Jeder Befund muss dieses Format haben:

```text
[SCHWERE] ID · Datei:Zeile — präziser Kurztitel

Beobachtung:
Was im aktuellen Checkout tatsächlich steht oder passiert.

Autorität:
Nur bei generiertem Inhalt: die Datei in partials/, in der die Korrektur
vorgenommen werden muss.

Beleg:
Reproduzierbarer Befehl, Messwert, Testausgabe oder externe Primärquelle.

Standard oder Vertrag:
Konkretes WCAG-Kriterium, Gesetz, HTML-Regel, Regel aus AGENTS.md mit
Paragraphennummer oder begründetes Maintainability-Prinzip. Keine Floskel
wie „Best Practice" ohne Inhalt.

Folge:
Konkretes Risiko für Leser, Recht, Veröffentlichung, Wartung oder Änderung.

Empfehlung:
Kleinste tragfähige Korrektur. Keine unaufgeforderte Implementierung.
Nenne, ob AGENTS.md oder README mitzuziehen sind.

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

## 18. Geforderter Abschlussbericht

Liefere den Bericht in dieser Reihenfolge:

1. **Executive Summary** mit klarem Gesamturteil
2. **geprüfter Snapshot**: Modus nach §0, Commit, Vergleichsbasis,
   Git-Zustand, Datum, verfügbare Werkzeuge, Grenzen
3. **Repositorykarte** mit Rollen und Autoritäten
4. **Prüfmatrix**: Bereich, Methode, Ergebnis, Abdeckung
5. **Vertragskonformität**: Regel aus `AGENTS.md` → eingehalten / verletzt /
   Regel selbst überholt, mit Beleg
6. **Befunde**, absteigend nach Schwere
7. **Stand früherer Befunde und Regressionen** (Phase J)
8. **nachweislich positive Eigenschaften**
9. **Maintainability für Menschen**
10. **Maintainability für schwache Modelle**
11. **Veröffentlichungsurteil**:
    - jetzt veröffentlichungsreif: ja oder nein
    - nach Schließen der benannten P0-Punkte veröffentlichungsreif: ja oder
      nein
    - jeweils mit Begründung
12. **priorisierter Maßnahmenplan**:
    - P0 vor Veröffentlichung
    - P1 kurzfristig
    - P2 nach Stabilisierung
13. **nicht geprüfte oder nicht prüfbare Punkte** mit Grund
14. **Quellenverzeichnis** nur mit tatsächlich verwendeten Quellen

Trenne bei den Empfehlungen:

- zwingende Korrektur
- sinnvolle Härtung
- optionale Verbesserung

Gib keine pauschale Prozentnote. Eine Ampel oder Teilbewertung ist nur
zulässig, wenn ihre Kriterien vorher definiert sind.

## 19. Qualitätskontrolle vor Abgabe

Prüfe deinen eigenen Bericht vor der Abgabe:

- Ist jeder schwere Befund durch Primärbeleg oder reproduzierbaren Test
  getragen?
- Hast du aktuelle Realität und dokumentierte Absicht getrennt?
- Hast du bei generiertem Inhalt jedes Mal die Autorität in `partials/`
  genannt, statt eine Korrektur in der Seite vorzuschlagen?
- Hast du jede Zahl, die du aus `AGENTS.md` oder `README.md` übernommen hast,
  selbst nachgezählt?
- Hast du einen grünen Test nicht als vollständige Freigabe missverstanden?
- Hast du bekannte offene Punkte gebündelt statt dupliziert?
- Hast du bereits gemeldete Befunde unter ihrer alten ID geführt?
- Hast du bewusste Entscheidungen respektiert, aber konkrete Folgen trotzdem
  geprüft?
- Hast du keine Rechtsnorm aus dem Gedächtnis behauptet, und bei fehlendem
  Netzzugriff Phase E als nicht prüfbar ausgewiesen?
- Hast du keine nicht ausgeführte Browser- oder Screenreaderprüfung als
  bestanden dargestellt?
- Hast du keine Datei außer der Berichtsdatei verändert und keine Hooks
  eingerichtet?
- Sind Empfehlungen proportional zur kleinen statischen Architektur, und hast
  du die Wartungslast jeder vorgeschlagenen Neuerung benannt?
- Kann der Auftraggeber jeden Befund ohne Rückfrage nachvollziehen?

Wenn eine dieser Fragen mit Nein beantwortet wird, überarbeite den Bericht
vor der Abgabe.
