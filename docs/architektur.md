# Architektur von bb-limen.de

Stand der Strukturentscheidung: 21.09.2026. Verbindliche Regeln stehen in
[AGENTS.md](../AGENTS.md), die Arbeitsabläufe im [Handbuch](../README.md).

## Dateifluss

```text
src/pages/*.html + src/partials/*.html ──> vollständige HTML-Seiten
src/style.css ──────────────────────────> style.css
src/seiten.json + public/CNAME ─────────> sitemap.xml
public/* (laut Katalog) ────────────────> unveränderte öffentliche Dateien
                                         │
                                         └── dist/ ──> Pages-Artefakt
```

Der Build wird über `tools/build.sh` aufgerufen. `tools/build.py` verarbeitet
UTF-8, Includes und die Ausgabe; `tools/site_config.py` validiert den Katalog.
Python ist schon für die Projektprüfungen nötig und verarbeitet JSON ohne
zusätzliche Pakete. Der Browser erhält weiterhin ausschließlich statische
Dateien. Es gibt keine Laufzeitabhängigkeit vom Buildwerkzeug.

## Maßgebliche Quellen

| Aufgabe | Quelle | Ausgabe |
| --- | --- | --- |
| Individueller Text und Seitenmetadaten | `src/pages/<name>.html` | `dist/<name>.html` |
| Gemeinsame Navigation und Kontakt | `src/partials/` | eingebaut in jede Seite |
| Gestaltung | `src/style.css` | `dist/style.css` |
| Signet und Vorschaubild gestalten | `src/grafik/*.svg` | gezielter Export nach `public/` |
| Fertige Bilder, vCard und robots.txt | `public/` | unverändert in `dist/` |
| Seitenbestand und Sprachprofil | `src/seiten.json` | Build und Prüfwerkzeuge |
| Sitemap und Inhaltsstand | `src/seiten.json`, `public/CNAME` | `dist/sitemap.xml` |

Die Bildexporte bleiben versioniert. Sie entstehen mit `tools/vorschau.sh`,
der Chromium/Chrome und Python benötigt. Der normale Build kopiert sie nur.
Büroangaben werden weiterhin an den in AGENTS §6 genannten Stellen gepflegt;
die Strukturmigration hat diese inhaltliche Mehrfachpflege nicht verändert.

## Katalog und Includes

`src/seiten.json` enthält `pages` und `public_files`. Ein Seiteneintrag hat:

- `file`: flacher HTML-Dateiname, zugleich Name in der Ausgabe;
- `language`: `einfach`, `fach`, `recht`, `leicht` oder `fehler`;
- `sitemap`: bewusste Entscheidung über die Aufnahme;
- `lastmod`: nur für Sitemap-Seiten, geprüfter Inhaltsstand als `YYYY-MM-DD`.

`lastmod` wurde bei der Migration aus der bestehenden Sitemap übernommen.
Es wird redaktionell bei einer tatsächlichen Inhaltsänderung aktualisiert.
Die frühere automatische Datierung über den Git-Pfad wurde ersetzt, damit
Dateiumzüge, flache Klone und Builds ohne Git keinen falschen Stand erzeugen.
Git bleibt der Nachweis für die Änderung; der Build benötigt seine Historie
nicht. `tools/sitemap.sh` zeigt die Sitemap zur Kontrolle, ohne zu schreiben.

Alle Seiten enthalten genau diese Include-Zeilen in dieser Reihenfolge:

```html
<!-- @include head -->
<!-- @include skip -->
<!-- @include rail -->
<!-- @include foot -->
<!-- @include callbar -->
```

Zwischen ihnen stehen die individuellen Metadaten, HTML-Struktur und Inhalte.
Includes dürfen nicht verschachtelt werden. In `rail.html` markiert der Build
über `%%CUR-<seitenname>%%` den aktuellen Navigationspunkt. Unbekannte Ziele,
fehlende oder doppelte Includes sowie alter generierter Inhalt in einer
Quellseite führen vor dem Schreiben zum Fehler.

## Prüfung und Fehlerbehebung

`tools/pruefen.sh` ist der gemeinsame Einstieg. Er baut temporär, führt die
Tests und Sprachmessung aus und räumt auf. Er verändert keine bearbeiteten
Dateien, keine bestehende Vorschau und keinen Git-Index. Die HTML-Validierung
läuft zusätzlich in der CI. Visuell wird nach README §3 von Hand geprüft.

Die Tests nutzen eine frisch erzeugte Ausgabe, auch wenn `dist/` fehlt.
`tests/site_support.py` stellt sie bereit. Fest erwartete Seitennamen, URLs,
Kontaktangaben und öffentliche Dateien bleiben unabhängig vom Katalog in
Regressionstests festgehalten. Dadurch bestätigt eine falsche Katalogangabe
nicht automatisch ihre eigene Richtigkeit.

Bei einem Buildfehler zuerst die genannte Quelldatei und Zeile bearbeiten.
Bei veralteter Vorschau `tools/build.sh` aufrufen und neu laden.
`tools/build.sh --check` meldet eine veränderte oder unvollständige Ausgabe.
Ein fehlgeschlagener Build erhält die letzte erfolgreiche Ausgabe.

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

## Erweiterung und Benennung

Eine neue Seite erhält einen sachbezogenen Namen in Kleinbuchstaben mit
Bindestrichen, eine Quelle unter `src/pages/`, einen Katalogeintrag und eine
bewusste Navigationsentscheidung. Ihre Metadaten bleiben in der Seite.
Danach unabhängige Bestands- und Navigationstests nachziehen, bauen, prüfen
und ansehen. Neue öffentliche Kopierdateien gehören nach `public/` und in
`public_files`. Unerwartete Dateien in diesen Bereichen werden abgelehnt.

Die öffentliche URL hängt am Ausgabepfad, nicht am Quellpfad. Daher bleiben
alle bisherigen `.html`-Adressen, Asset-Adressen und Downloads erhalten.

## Veröffentlichung und lokale Unterlagen

Nur `dist/` wird veröffentlicht. Vor der ersten Übertragung der Migration
muss Pages auf GitHub Actions umgestellt sein; der Ablauf steht in README §4.
Bis zur bestätigten Umstellung bleibt `_config.yml` als Übergangsschutz.
`docs/lokal/`, `reports/`, `tmp/` und lokale KI-Einstellungen sind ignoriert.
Gemeinsame technische Dokumentation unter `docs/` wird dagegen versioniert.
