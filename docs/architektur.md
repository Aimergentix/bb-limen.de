# Architektur von bb-limen.de

Wie das Repository funktioniert: Verzeichnisse, Build, Prüfkette. Die Regeln
dazu stehen in [AGENTS.md](../AGENTS.md), die Gründe in
[entscheidungen.md](entscheidungen.md).

## Verzeichnisse

```text
src/pages/         Seiten als Quellen, mit Include-Zeilen statt Bausteinen
src/partials/      gemeinsame HTML-Bausteine
src/style.css      ein Stylesheet; alle Farbwerte im Block PALETTE
src/grafik/        bearbeitbare SVG-Originale für Signet und Vorschaubild
src/seiten.json    Katalog: Seitenbestand, Sprachprofile, Sitemap, öffentliche Dateien
src/bureauangaben.json  gemeinsame Kontaktangaben und strukturierte Sprechzeiten
public/            bewusst öffentliche Dateien, unverändert kopiert
dist/              die Ausgabe: vollständig erzeugt, unversioniert
tools/             Build, Prüfung, Bildexport und Commit-Hook
tests/             Regressionstests
docs/              diese Dokumentation, versioniert
docs/lokal/        persönliche Unterlagen und offene Punkte, unversioniert — kann fehlen
reports/           Auditberichte, unversioniert — kann fehlen
.github/           Workflows für Prüfung, Veröffentlichung, Verweise; Dependabot
```

Vertrag, README, Lizenz sowie Git- und Editor-Konfiguration liegen im
Wurzelverzeichnis. `.gitignore` bestimmt, was versioniert wird; ausgeliefert
wird ausschließlich `dist/`.

## Dateifluss

```text
src/pages/*.html + src/partials/*.html ──> vollständige HTML-Seiten
src/bureauangaben.json ─────────────────> Büroplatzhalter in HTML und JSON-LD
erzeugtes JSON-LD der Startseite ───────> bb-limen.vcf
src/style.css ──────────────────────────> style.css
src/seiten.json + public/CNAME ─────────> sitemap.xml
public/* (laut Katalog) ────────────────> unveränderte öffentliche Dateien
                                         │
                                         └── dist/ ──> Pages-Artefakt
```

`tools/build.sh` ruft `tools/build.py` auf; `tools/site_config.py` prüft den
Katalog. Beides braucht nur die Python-Standardbibliothek. Der Browser erhält
ausschließlich statische Dateien; zur Laufzeit gibt es keine Abhängigkeit vom
Buildwerkzeug.

| Aufgabe | Quelle | Ausgabe |
| --- | --- | --- |
| Individueller Text und Seitenmetadaten | `src/pages/<name>.html` | `dist/<name>.html` |
| Gemeinsame Navigation und Kontakt | `src/partials/` | eingebaut in jede Seite |
| Gestaltung | `src/style.css` | `dist/style.css` |
| Signet und Vorschaubild gestalten | `src/grafik/*.svg` | gezielter Export nach `public/` |
| Fertige Bilder und robots.txt | `public/` | unverändert in `dist/` |
| Telefon, E-Mail, Anschrift und Sprechzeiten | `src/bureauangaben.json` | sprach- und formatgerechte Werte in den HTML-Seiten |
| Bürovisitenkarte | erzeugter Organization-Knoten der Startseite | `dist/bb-limen.vcf` |
| Seitenbestand und Sprachprofil | `src/seiten.json` | Build und Prüfwerkzeuge |
| Sitemap und Inhaltsstand | `src/seiten.json`, `public/CNAME` | `dist/sitemap.xml` |

Die öffentliche Adresse hängt am Namen in der Ausgabe, nicht am Quellpfad:
`src/pages/betreuung.html` wird zu `dist/betreuung.html` und ist unter
`/betreuung.html` erreichbar.

## Katalog und Includes

`src/seiten.json` enthält `pages` und `public_files`. Ein Seiteneintrag hat:

- `file`: flacher HTML-Dateiname, zugleich Name in der Ausgabe;
- `language`: das Sprachprofil — `einfach`, `fach`, `recht`, `leicht` oder `fehler`;
- `sitemap`: bewusste Entscheidung über die Aufnahme;
- `lastmod`: nur für Sitemap-Seiten, geprüfter Inhaltsstand als `YYYY-MM-DD`.

Der Build benötigt keine Git-Historie. `tools/build.sh --sitemap` zeigt die
Sitemap zur Kontrolle, ohne zu schreiben.

Jede Seite enthält genau diese Include-Zeilen, in dieser Reihenfolge und
jeweils allein auf einer Zeile:

```html
<!-- @include head -->
<!-- @include skip -->
<!-- @include rail -->
<!-- @include foot -->
<!-- @include callbar -->
```

Zwischen ihnen stehen die individuellen Metadaten, die HTML-Struktur und der
Inhalt. Includes dürfen nicht verschachtelt werden. In der Ausgabe umschließen
die Marken `<!-- #rail -->` und `<!-- /#rail -->` den eingesetzten Baustein. In
`rail.html` markiert der Build über `%%CUR-<seitenname>%%` den aktuellen
Navigationspunkt.

## Büroangaben

`src/bureauangaben.json` enthält die fachlichen Werte. `tools/bureau_data.py`
prüft sie und erzeugt die Darstellungen beim Build, ausschließlich mit der
Python-Standardbibliothek. Die Datendatei wird nicht veröffentlicht.

`telefon.e164` ist die technische Nummer mit internationaler Vorwahl,
`telefon.sichtbar` ihre lesbare Schreibweise. Beide müssen dieselben Ziffern
enthalten. `email` enthält die Büro-E-Mail-Adresse. `anschrift` hat die Felder
`strasse`, `plz`, `ort`, `bundesland` und `land` (DE).

Unter `sprechzeiten.regulaer` stehen `tage` als Liste deutscher Wochentage
und `von` sowie `bis` als HH:MM. `nach_vereinbarung` enthält die Termintage.
Beide Tageslisten sind nicht leer, enthalten keine Wiederholungen und
überschneiden sich nicht. Ein reguläres Zeitfenster gilt für alle regulären
Tage. Geteilte oder je Wochentag verschiedene Zeiten benötigen eine bewusste
Erweiterung des Datenformats und der Sprachvorlagen. Die Reihenfolge der
Wochentage bestimmt die Ausgabe. Die Leichte Sprache behält ihre kurzen,
zeilenweise getrennten Sätze. Ihre Zielgruppenprüfung bleibt davon unabhängig.

HTML verwendet beispielsweise `%%BUREAU:telefon.e164%%`,
`%%BUREAU:email%%` oder `%%BUREAU:anschrift.strasse%%`.
Sprechzeiten verwenden die Fassungen `sprechzeiten.kurz`, `sprechzeiten.text`
und `sprechzeiten.leicht`; die vorhandenen Seiten zeigen deren einzelne
Textfelder. Werte werden für HTML einschließlich Attributen maskiert.
Im JSON-LD steht ein vollständiger String wie
`"%%BUREAU_JSON:telefon.e164%%"`. Der Build setzt einen korrekt maskierten
JSON-String ein und schützt den umgebenden Script-Block. Fehlende Felder,
unbekannte Schlüssel, widersprüchliche Werte und nicht aufgelöste
Büroplatzhalter brechen den Build vor dem Schreiben ab.

Die vCard wird aus dem erzeugten Organization-Knoten aufgebaut. Name und
Websiteadresse bleiben dort redaktionell festgelegt, die Kontaktwerte kommen
aus den Büroangaben. Der Generator maskiert vCard-Sonderzeichen, faltet lange
Zeilen an UTF-8-Zeichengrenzen und schreibt CRLF. Die öffentliche Adresse der
Visitenkarte bleibt gleich. Sie gehört zu den erzeugten Dateien und steht
deshalb nicht unter `public_files`.

Nach einer Datenänderung werden die unabhängigen Testwerte aktualisiert und
die erzeugten Verwendungen geprüft. Ein reiner Umbau der Vorlagen ändert
keinen Inhaltsstand; eine geänderte Büroangabe erfordert dagegen die Prüfung
der betroffenen Standdaten nach R-ANGABEN-5 und R-ORDNUNG-6.

## Verhalten des Builds

Der Build prüft Katalog, Büroangaben, Dateibestand, Bausteine, Include-Reihenfolge
und Platzhalter, bevor er schreibt. Er erzeugt erst ein vollständiges
Arbeitsverzeichnis und ersetzt dann `dist/`. Bei fehlerhaften Eingaben bleiben
die Quellen und die letzte erfolgreiche Ausgabe erhalten. Nicht mehr benötigte
Ausgabedateien verschwinden beim nächsten erfolgreichen Build. Dateien, die in
`src/pages/`, `src/partials/` oder `public/` liegen, aber nicht eingetragen
sind, führen zum Fehler; innerhalb des Repositorys ist ausschließlich `dist/`
als Ausgabe erlaubt. Dasselbe gilt für eine Datei im Wurzelverzeichnis, die
wie eine Seite, eine öffentliche oder eine erzeugte Datei heißt — etwa
`robots.txt` oder `sitemap.xml`: Sie sähe wie eine Quelle aus, würde aber nie
veröffentlicht (R-QUELLE-1, R-QUELLE-3).

GitHub Pages liefert `404.html` für jede unbekannte Adresse aus, auch für
`/ein/tiefer/pfad/`. Der Build setzt deshalb in dieser einen Seite alle
relativen Dateiverweise an die Domainwurzel (`/style.css`, `/index.html`).
Der Sprunglink `#inhalt` bleibt unverändert und damit auf der Fehlerseite;
warum kein `base`-Element, steht in [entscheidungen.md](entscheidungen.md)
unter E-14. Lokal lässt sich die Fehlerseite deshalb nur über einen Server
ansehen, nicht als Datei.

Bei einem Buildfehler zuerst die genannte Quelldatei und Zeile bearbeiten.
`tools/build.sh --check` meldet eine veränderte oder unvollständige Ausgabe,
ohne sie zu berichtigen.

## Prüfkette

`tools/pruefen.sh` ist der gemeinsame Einstieg für Menschen, Commit-Hook und
CI. Er baut in ein temporäres Verzeichnis, führt die Tests und die
Sprachmessung aus und räumt auf. Mit `--veroeffentlichung` sind offene
Platzhalter ein Fehler statt eines Hinweises; so ruft ihn der
Veröffentlichungsworkflow auf.

Die Tests prüfen immer eine frisch erzeugte Ausgabe, auch wenn `dist/` fehlt;
`tests/site_support.py` stellt sie bereit. Erwartete Seitennamen, Adressen,
Büroangaben und öffentliche Dateien stehen dort und in den Tests ein zweites
Mal, unabhängig von den Quellen. Dadurch bestätigt eine falsche Angabe nicht
ihre eigene Richtigkeit.

| Testdatei | Gegenstand |
| --- | --- |
| `tests/test_build.py` | Build: Wiederholbarkeit, Fehleingaben, Schutz der Quellen und fremder Verzeichnisse |
| `tests/test_site.py` | fertige Seiten: Bestand, Verweise, Überschriften, CSP, JSON-LD, Pflichtverweise |
| `tests/test_angaben.py` | Verwendungen der gemeinsamen Büroangaben |
| `tests/test_bureau_data.py` | Sprachvarianten, Formatmaskierung und Schutz vor erneuter Mehrfachpflege |
| `tests/test_begriffe.py` | Formulierungen und Zeichen, die hier schon einmal falsch waren |
| `tests/test_kontrast.py` | WCAG AA für jede Textpaarung, hell und dunkel |
| `tests/test_pruefe_sprache.py` | die Sprachmessung selbst |
| `tests/test_doku.py` | genannte Dateien, Verweise, Kennungen und Begriffe der Dokumentation |
| `tests/test_tools.py` | Fehlerfälle von Bildexport und Verweisprüfung, mit nachgestelltem Browser und `curl` statt Netz |

**Vor jedem Commit** läuft nach `tools/einrichten.sh` derselbe Befehl als Hook.
Geprüft wird der Arbeitsbaum, nicht nur der Git-Index; der Hook verändert und
merkt nichts vor. `git commit --no-verify` überspringt nur den lokalen Hook.

**Bei Push und Pull Request** führt `.github/workflows/pruefung.yml` den
Prüfbefehl aus und validiert danach das fertige HTML. Auf `main` ruft
`.github/workflows/veroeffentlichung.yml` diese Prüfung als Voraussetzung auf.

**Einmal im Monat** baut `.github/workflows/verweise.yml` die Website und ruft
mit `tools/verweise-pruefen.sh` ihre Verweise nach außen ab; das Skript läuft
genauso lokal. Es liest die Verweise mit einem HTML-Parser aus der Ausgabe,
lässt nur die eigene Domain aus `public/CNAME` aus und wertet auch einen
abgebrochenen Abruf als Fehler. Bei nicht erreichbaren Adressen entsteht ein
Issue. Was dann zu tun ist, steht in
[redaktion.md](redaktion.md#verweise-nach-außen-pflegen).

### HTML-Validierung

Die CI führt nach den Regressionstests `html5validator --config
tools/html5validator.yml` auf `dist/` aus. Alle HTML-Fehler und Warnungen
blockieren die Prüfung, ausgenommen drei genau bezeichnete Befundgruppen:

- Beim Prüfen lokaler Dateien fehlt die Web-Origin für `'self'`. Deshalb
  wird nur die Meldung über das eigene `style.css` ausgenommen; siehe die
  [Erläuterung des Validator-Maintainers](https://github.com/validator/validator/issues/2062#issuecomment-4173094350).
- Auf `index.html` wird der JSON-LD-Datenblock irrtümlich wie ausführbares
  JavaScript gemeldet. `application/ld+json` ist nach dem
  [HTML-Standard](https://html.spec.whatwg.org/multipage/scripting.html#data-block)
  ein Datenblock. Nur diese Inline-CSP-Meldung der Startseite wird ausgenommen.
- Der gebündelte Prüfstand meldet `media` auf `meta` pauschal als Fehler.
  Für `meta name="theme-color"` erlaubt der
  [HTML-Standard](https://html.spec.whatwg.org/multipage/semantics.html#meta-theme-color)
  das Attribut ausdrücklich. Ausgenommen wird nur diese Fehlermeldung auf den
  erzeugten Seiten.

Die Gegenkontrollen in `tests/test_site.py` verlangen genau einen lokalen
Stylesheet-Verweis, den einzigen Script-Tag als JSON-LD ohne `src` auf der
Startseite, gültiges JSON, die unveränderten CSP-Direktiven und genau die zwei
vorgesehenen `theme-color`-Elemente für Hell- und Dunkeldarstellung. Sie
verbieten andere `meta`-Elemente mit `media`, Inline-Stile,
Ereignisattribute und JavaScript-Verweise. Andere Ressourcen, Seiten oder
Validator-Meldungen werden durch die Ausnahmen nicht verdeckt. Die CSP selbst
wird dafür nicht gelockert.

Mit installiertem Java und `html5validator` läuft dieselbe Prüfung lokal:

```sh
tools/build.sh
html5validator --config tools/html5validator.yml
```

## Bildexport

Vorschaubild und die beiden Symbole entstehen aus den zwei SVG-Quellen in
`src/grafik/`. Die fertigen Bilder liegen versioniert in `public/`, damit der
normale Build keinen Browser braucht. Nach einer Änderung an Signet oder
Palette neu rendern; das Skript braucht Chromium oder Chrome und Python:

```sh
tools/bilder-erzeugen.sh
```

Das Skript rendert in ein Arbeitsverzeichnis, prüft die Maße der drei Bilder
und ersetzt die Dateien in `public/` erst danach. Bricht der Export ab, bleibt
der versionierte Satz unverändert.

## Erweiterung

Eine neue Seite erhält einen sachbezogenen Namen nach R-BESTAND-2, eine Quelle
unter `src/pages/` mit den fünf Include-Zeilen, einen Katalogeintrag und eine
bewusste Navigationsentscheidung. Ihre Metadaten bleiben in der Seite
(R-QUELLE-2). Danach die Bestandstests in `tests/test_site.py` nachziehen, bei
einer Seite mit Büroangaben auch `tests/test_angaben.py` und die Tabelle unter
R-ANGABEN; dann bauen, prüfen und ansehen. Neue öffentliche Kopierdateien
gehören nach `public/` und in `public_files`.

## Anhang: Arbeitsgrundsätze

Eine Erinnerung für Menschen, nach welchen bewährten Verfahren dieses
Repository gepflegt wird — und warum. Verbindlich sind die Regeln in
[AGENTS.md](../AGENTS.md); hier steht der Gedanke dahinter.

| Grundsatz | Herkunft | Hier heißt das |
| --- | --- | --- |
| **Eine Quelle der Wahrheit** | „Don't repeat yourself", Hunt und Thomas, *The Pragmatic Programmer* | Jede Aussage hat ein Zuhause; wer sie zweimal braucht, verweist (R-ORDNUNG-1). Was doppelt steht, widerspricht sich irgendwann. |
| **Dokumente nach der Frage trennen** | Diátaxis (Daniele Procida) | Regeln, Funktionsweise, Anleitung und Begründung sind vier Dinge. Die Tabelle „Wo steht was" im README ordnet jeder Frage ein Dokument zu. |
| **Entscheidungen datiert festhalten** | Architecture Decision Records, Michael Nygard | `entscheidungen.md` wird nur ergänzt. Wer in einem Jahr fragt „warum kein Kartendienst?", findet Antwort und Datum. |
| **Eindeutige Verbindlichkeit** | RFC 2119 | MUSS, DARF NICHT, SOLL, KANN statt „sollte möglichst". Ein Mensch überliest die Unschärfe, ein Sprachmodell rät. |
| **Rückverfolgbarkeit** | Anforderungsmanagement | Jede Regel trägt eine Kennung, die auch im Test steht. Eine Suche zeigt Regel, Prüfung und Begründung zusammen. |
| **Ausführbare Regeln** | testgetriebene Entwicklung | Was sich prüfen lässt, prüft ein Test; die Prosa dazu entfällt. Bei Widerspruch gilt: Test vor Code vor Vertrag vor Erklärung. |
| **Unabhängiger Erwartungswert** | Test-Orakel | Tests lesen ihre Sollwerte nicht aus der geprüften Datei. Sonst bestätigt jeder Fehler sich selbst. |
| **Jeder Test muss rot werden können** | Mutationstest | Ein neuer Test wird einmal gegen eine absichtlich beschädigte Kopie ausgeführt. Bleibt er grün, prüft er nichts. |
| **Fehler früh und laut** | „fail fast", Poka Yoke | Der Build lehnt Unbekanntes ab, statt zu raten, und nennt in der Meldung den nächsten Schritt. |
| **Reproduzierbarkeit** | hermetische Builds | Feste Versionen in der CI, keine Netzabhängigkeit im Build. Eine rote CI muss sich aus einem Commit erklären lassen. |
| **Sparsamer Kontext** | Kontextgestaltung für Sprachmodelle | `AGENTS.md` wird in jede KI-Sitzung geladen. Deshalb nur Regeln dort, Wichtiges oben, Einzelheiten hinter Verweisen — lange Texte werden in der Mitte unzuverlässiger gelesen. |
| **Ein Befehl für „stimmt alles?"** | agentisches Arbeiten | `tools/pruefen.sh` gibt Mensch und Assistent dasselbe eindeutige Signal. |
| **Der Mensch gibt frei** | „human in the loop" | Assistenten arbeiten auf einem Zweig; veröffentlicht wird erst nach Freigabe (R-COMMIT-3). |
