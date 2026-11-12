# bb-limen.de — statische Website

Die Website von BB Limen, einem Büro für rechtliche Betreuung.
Statische HTML-Seiten, ein Stylesheet, keine externen Ressourcen und kein
JavaScript im Browser. Bearbeitet werden `src/` und `public/`;
`tools/build.sh` erzeugt daraus die Ausgabe in `dist/`.

> **Zuerst [AGENTS.md](AGENTS.md) lesen.** Dort stehen die verbindlichen
> Regeln. Wie alles funktioniert und warum, steht in
> [docs/pflege.md](docs/pflege.md).

## Schnellstart

Voraussetzungen: Python 3.12 oder neuer, eine POSIX-Shell und Git.

```sh
python3 -m venv .venv-documents
.venv-documents/bin/python -m pip install -r tools/requirements-qrcodes.txt
tools/einrichten.sh     # einmalig: schaltet die Prüfung vor jedem Commit ein
tools/build.sh          # erzeugt dist/
python3 -m http.server 8391 --bind 127.0.0.1 --directory dist
```

Dann <http://localhost:8391> öffnen — breit, schmal (390 px) und in
Dunkeldarstellung. Die Dateien unter `src/pages/` sind Vorlagen und lassen
sich nicht selbst im Browser öffnen. Nach jeder Änderung:

```sh
tools/pruefen.sh
```

Der Befehl prüft Technik, nie Wortlaut: Er wird nur rot, wenn etwas kaputt
ist — ein Verweis ohne Ziel, ein falsch geschriebener Platzhalter, ungültiges
HTML. Was auf den Seiten steht, entscheidet das Büro.

## Häufige Änderungen

| Ich möchte … | Datei |
| --- | --- |
| einen Seitentext oder Seitentitel ändern | `src/pages/<seite>.html` |
| Telefonnummer, E-Mail, Anschrift oder Sprechzeiten ändern | `src/bureauangaben.json` — nur dort, alle Seiten folgen |
| Navigation, Kolumne oder Anrufleiste ändern | `src/partials/rail.html`, `src/partials/callbar.html` — wirkt auf alle Seiten |
| Farben oder Abstände ändern | `src/style.css`, Block PALETTE; die Kopien der Werte in `src/partials/head.html` und `src/grafik/` nachziehen ([docs/pflege.md](docs/pflege.md#gestaltung)); danach hell, dunkel und schmal ansehen |
| eine Gemeinde ergänzen oder streichen | JSON-LD in `src/pages/index.html`, Liste `areaServed` |
| Signet oder Vorschaubild ändern | `src/grafik/`, danach `tools/bilder-erzeugen.sh` (braucht Chromium) |
| Seitenübersicht für Assistenzsysteme ändern | `public/llms.txt` |
| eine Seite hinzufügen | [docs/pflege.md](docs/pflege.md#eine-seite-hinzufügen) |
| Angaben einer betreuenden Person ändern | `src/betreuende.json`, Vorstellungstext in `src/betreuende/<kennung>.html` |
| ein Porträt einsetzen | Foto quadratisch im Format 600 × 600 Pixel als `src/betreuende/<kennung>.webp` ablegen (`.jpg` und `.png` gehen auch), in `src/betreuende.json` bei `bild` den Dateinamen eintragen |
| eine betreuende Person aufnehmen oder entfernen | siehe unten |

### Nach jeder inhaltlichen Änderung

- Den Stand nachziehen: `lastmod` der Seite in `src/seiten.json`; bei
  `impressum.html` und `datenschutz.html` das sichtbare Datum im Text.
- Bei Paragraphen: vorher unter <https://www.gesetze-im-internet.de/>
  nachschlagen (R-RECHT-1).

### Registrierung eintragen

Die Registrierung wird jeder Person einzeln erteilt. Diese Stellen nennen den
Stand und sind dann zu ändern — kein Test erinnert daran:

1. `src/betreuende.json`: die Felder `registrierung` und `beruf` („beantragt")
   der Person. Sie erscheinen im Personenabschnitt auf `index.html`, in
   `fachkreise.html` und, bei der Betreiberin, im Impressum; dessen Stand
   nachziehen.
2. `fachkreise.html`: der Eintrag „Stammbehörde" („… ist beantragt").

### Eine betreuende Person aufnehmen

1. In `src/betreuende.json` einen Eintrag anlegen; die Felder erklärt
   [docs/pflege.md](docs/pflege.md#betreuende-personen).
2. Den Vorstellungstext als `src/betreuende/<kennung>.html` anlegen.
3. `lastmod` von `index.html` in `src/seiten.json` nachziehen,
   `tools/pruefen.sh`, danach `index.html` ansehen. Abschnitt und
   Visitenkarte folgen von selbst; Impressum und Datenschutzerklärung
   verweisen auf die Startseite und bleiben unverändert.

### Eine betreuende Person entfernen

Eintrag und Vorstellungstext löschen, die Porträtgruppen in
`leichte-sprache.html` und `fachkreise.html` anpassen, `lastmod` der drei
Seiten nachziehen, `tools/pruefen.sh`.

### Wenn sich ein Gesetz ändert

Die Rechtsstände, auf die sich die Texte stützen, und die offenen
Wiedervorlagen stehen in
[docs/pflege.md](docs/pflege.md#rechtsstände-und-wiedervorlagen). Mit dem
Gesetz ändern sich auch die Jahreszahlen im Text (R-RECHT-4).

## Dokumentvarianten als PDF und E-Mail bauen

Die bearbeitbaren Vorlagen sind
[Stammdaten](dokumente/vorlagen/bb-limen-stammdaten.md) und
[Vorstellung](dokumente/vorlagen/bb-limen-vorstellung.md) sowie die persönlichen
Vorstellungen von [Mika Möller](dokumente/vorlagen/mika-moeller-vorstellung.md) und
[Aranda Möller](dokumente/vorlagen/aranda-moeller-vorstellung.md). Einmalig eine lokale
Python-Umgebung mit ReportLab einrichten:

```sh
python3 -m venv .venv-documents
.venv-documents/bin/python -m pip install reportlab -r tools/requirements-qrcodes.txt
```

Der PDF-Satz benötigt die Systemschriften aus `fonts-noto-core`
(Debian/Ubuntu: `sudo apt install fonts-noto-core`). Nach Änderungen an den
Markdown-Vorlagen alle Dokumente neu erzeugen:

```sh
.venv-documents/bin/python tools/build_documents.py
```

Die bearbeitbaren Markdown-Vorlagen liegen versioniert in `dokumente/vorlagen/`.
Die Ausgabe landet ausschließlich in `dokumente/handouts/`: pro Vorlage ein
einseitiges A4-PDF, eine HTML-Datei und ein unadressierter EML-Entwurf. Dieser
Ausgabeordner wird wie `signaturen/` von Git ignoriert. Vorhandene Ausgaben
werden überschrieben; die Markdown-Quellen bleiben unverändert.
Ohne Dateiangaben werden alle `.md`-Dateien mit kleingeschriebenen Dateinamen
direkt in `dokumente/vorlagen/` gebaut. Das Unterverzeichnis `archiv/` und
Dateien in weiteren Unterverzeichnissen werden dabei nicht verarbeitet.
Ein Porträt wird als eigener Markdown-Absatz eingebunden, zum Beispiel
`![Porträt von Mika Möller](../assets/mika.png)`. Der Build setzt es klein und rund.
Ein QR-Code mit den Kontaktdaten wird ebenfalls als eigener Markdown-Absatz
eingebunden, am Alt-Text `QR-Code:` erkennbar, zum Beispiel
`![QR-Code: Kontaktdaten von Mika Möller](../assets/mika-moeller-qr.png)`;
der Build setzt ihn quadratisch (im PDF neben einem Porträt oder Text).
HTML und EML enthalten die Bilddaten und benötigen keine externen Bilddateien.
PDF-Seitenumbrüche und E-Mails nach Änderungen ansehen.
Vor dem Versand den Namensplatzhalter durch die zuständige Person ersetzen.

Ein einzelnes Dokument bauen:

```sh
.venv-documents/bin/python tools/build_documents.py dokumente/vorlagen/bb-limen-stammdaten.md
```

Mit `--output-dir /absoluter/pfad` lässt sich ein anderer Ausgabeordner wählen.
Die älteren Aufrufe `tools/generate_pdfs.py` und `tools/generate_emails.py`
verwenden denselben gemeinsamen Build und dieselben Ordner.

Die lokale Python-Umgebung wird nicht versioniert.
Dieser Dokument-Build ist unabhängig von `tools/build.sh` für die Website.

## Thunderbird-Signaturen

Der normale Aufruf von `tools/build.sh` aktualisiert zusätzlich die lokalen
HTML-Signaturen aller Personen aus `src/betreuende.json`:

- `dokumente/signaturen/<kennung>.html`
- `dokumente/signaturen/bb-limen.html` für das Büro, mit Büro-vCard und Büro-QR-Code
- passende QR-Bilder in `dokumente/signaturen/assets/` und vCards daneben

Jede HTML-Datei enthält ihr QR-Bild vollständig als Bilddaten. Sie kann allein
in einen beliebigen Ordner kopiert werden; es gibt keine Bildpfade ins
Repository und keine erzeugte `signature.html` im Hauptverzeichnis.

Nur die Signaturen neu erzeugen:

```sh
.venv-documents/bin/python tools/generate_signatures.py
```

In Thunderbird unter Konten-Einstellungen das betreffende Konto auswählen,
„Stattdessen eine Datei als Signatur anhängen“ aktivieren und die persönliche
HTML-Datei auswählen. Eine neue Nachricht öffnen und eine Testmail an sich
selbst senden; auch als Reintext ansehen.

Für die Ablage außerhalb des Repositories, beispielsweise in einem Ordner
`signatures/bb-limen` im Thunderbird-Profil, einmalig den gewünschten Zielordner
angeben:

```sh
.venv-documents/bin/python tools/generate_signatures.py --install-dir /absoluter/pfad/zum/signaturordner
```

Der Zielordner wird ausschließlich lokal in `.signature-output.json` gemerkt.
Künftige normale Builds und Signatur-Exporte aktualisieren auch die dortigen
HTML-Dateien. In Thunderbird einmalig die Datei aus diesem Zielordner auswählen.
Eine alte `signature.html` im Hauptverzeichnis kann nach Umstellung aller
betroffenen Konten entfernt werden. Eine bereits ausgewählte Datei wird
weiterhin über ihren Pfad gefunden; beim
Verschieben dieser Datei muss sie neu ausgewählt werden. Alternativ den
HTML-Code in das Signaturtextfeld mit aktiviertem „HTML verwenden“ kopieren:
Dann liegt die Signatur direkt in den Kontoeinstellungen; spätere Exporte
müssen dort erneut eingefügt werden.

Kontaktdaten weiterhin ausschließlich in den bestehenden JSON-Dateien ändern.
Die gemeinsame Gestaltung steht in `src/signatures/signature.html`, optionale
abweichende Funktionsbezeichnungen in `src/signatures/settings.json` unter
`roles` mit der Personenkennung als Schlüssel. Die erzeugten Dateien nicht
von Hand bearbeiten. Eine installierte Signatur funktioniert auch nach dem
Verschieben oder Entfernen des Repositories. Für weitere automatische Updates
die lokale `.signature-output.json` beim Umzug mitnehmen. Entfernte Personen benötigen
auch eine manuelle Entfernung ihrer alten Signaturdateien und Kontozuordnung.

Die Datenquellen und die Trennung von Website und lokalen Signaturen stehen
in [docs/pflege.md](docs/pflege.md#thunderbird-signaturen).

## QR-Codes für die Kontaktdaten

`tools/build.sh` erzeugt die vCards und die zugehörigen QR-PNGs gemeinsam.
Installation und erster Lauf stehen im [Schnellstart](#schnellstart).
`tools/pruefen.sh` und die GitHub-Workflows verwenden denselben Build.
Die Shell-Befehle nutzen `.venv-documents/bin/python`, sofern vorhanden,
sonst `python3`; mit `PYTHON` lässt sich ein anderer Interpreter wählen.

Nach Änderungen an Kontaktdaten genügt für die Website der normale Build.
Für bestehende Handouts und E-Mails werden die separaten Bildkopien bei Bedarf
aktualisiert und anschließend die betroffenen Dokumente neu gebaut:

```sh
.venv-documents/bin/python tools/generate_qrcodes.py
.venv-documents/bin/python tools/generate_qrcodes.py --check
.venv-documents/bin/python tools/build_documents.py
```

Der Dokument-Check liest die vorhandenen Dokumentbilder zurück. Er ist ein
manueller Pflegeschritt und keine Voraussetzung für Website-Build oder CI.
Dokumente vor Verwendung ansehen; die Website-Kolumne lässt sich am Desktop
scrollen, am Telefon stehen die Speicherlinks ohne QR-Bilder bereit.

## Veröffentlichen

Jeder Push nach `main` veröffentlicht die Website; `main` ist geschützt.

```sh
git switch -c mein-thema                # eigener Zweig
# … ändern, ansehen, tools/pruefen.sh …
git add -A && git commit -m "Was sich geändert hat"
git push -u origin mein-thema
gh pr create --fill                     # Pull Request; die Prüfung läuft von selbst
gh pr merge --merge                     # nach grüner Prüfung: veröffentlicht
git switch main && git pull
```

Was danach zu prüfen ist, steht in
[docs/pflege.md](docs/pflege.md#veröffentlichen).

## Wo steht was

| Frage | Dokument |
| --- | --- |
| Was muss, was darf nie? | [AGENTS.md](AGENTS.md) |
| Wie ändere ich etwas? | dieses README |
| Wie funktioniert es, welche Rechtsstände gelten, warum ist es so? | [docs/pflege.md](docs/pflege.md) |
| Was fehlt noch? | `docs/lokal/offen.md` — lokal und unversioniert, weil dieses Repository öffentlich ist |

## Rechte

Alle Rechte vorbehalten; siehe [LICENSE](LICENSE).
