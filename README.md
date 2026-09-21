# bb-limen.de — statische Website

Die Website von BB Limen · A+M Möller, einem Büro für rechtliche Betreuung.
Statische HTML-Seiten, ein Stylesheet, keine externen Ressourcen und kein
JavaScript im Browser. Bearbeitet werden `src/` und `public/`;
`tools/build.sh` erzeugt daraus die Ausgabe in `dist/`.

> **Zuerst [AGENTS.md](AGENTS.md) lesen.** Dort stehen die verbindlichen
> Regeln. Wie alles funktioniert und warum, steht in
> [docs/pflege.md](docs/pflege.md).

## Schnellstart

Voraussetzungen: Python 3.12 oder neuer, eine POSIX-Shell und Git.

```sh
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
| eine Seite hinzufügen | [docs/pflege.md](docs/pflege.md#eine-seite-hinzufügen) |

### Nach jeder inhaltlichen Änderung

- Den Stand nachziehen: `lastmod` der Seite in `src/seiten.json`; bei
  `impressum.html` und `datenschutz.html` das sichtbare Datum im Text.
- Bei Paragraphen: vorher unter <https://www.gesetze-im-internet.de/>
  nachschlagen (R-RECHT-1).

### Registrierung eintragen

Die Registrierung wird jeder Person einzeln erteilt. Diese Stellen nennen den
Stand und sind dann zu ändern — kein Test erinnert daran:

1. `impressum.html`: unter „Anbieter" der Absatz „… bereiten … ihre Tätigkeit
   … vor. Jede Person wird ihren Beruf eigenständig ausüben …", im
   Personenblock die Zeile „Registrierung … beantragt", darunter der Absatz
   der Person mit Stand-Datum und Registrierungsnummer, und der Satz „Bis zur
   Erteilung …".
2. Der Kasten „Büro in Gründung" auf `index.html`, `betreuung.html`,
   `aufgaben.html`, `vorsorge.html` und `fachkreise.html` (R-BESTAND-3).
3. `fachkreise.html`: die Einträge „Stammbehörde" („Dort ist die Registrierung
   … beantragt") und „Vorschlagslisten" („sobald die Registrierung erteilt
   ist").
4. `aufgaben.html`: Register VI, „übernehmen wir nach Aufnahme der Tätigkeit".
5. `leichte-sprache.html`: der Kasten „Wichtig: Unser Büro ist noch neu …".
6. `index.html`: im JSON-LD die Zeile `description` („Büro in Gründung …").

### Wenn sich ein Gesetz ändert

Die Rechtsstände, auf die sich die Texte stützen, und die offenen
Wiedervorlagen stehen in
[docs/pflege.md](docs/pflege.md#rechtsstände-und-wiedervorlagen). Mit dem
Gesetz ändern sich auch die Jahreszahlen im Text (R-RECHT-4).

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
