# bb-limen.de — statische Website

Die Website von BB Limen · A+M Möller, einem Büro für rechtliche Betreuung.
Statische HTML-Seiten, ein Stylesheet, keine externen Ressourcen und kein
JavaScript im Browser. Bearbeitet werden `src/` und `public/`;
`tools/build.sh` erzeugt daraus die Ausgabe in `dist/`.

> **Zuerst [AGENTS.md](AGENTS.md) lesen.** Dort stehen die verbindlichen
> Regeln. Dieses README ist Einstieg und Wegweiser.

## Schnellstart

Voraussetzungen: Python 3.12 oder neuer, eine POSIX-Shell und Git. Build und
Tests verwenden nur die Python-Standardbibliothek.

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

## Ich möchte …

| Ich möchte … | Maßgebliche Datei | Beachten |
| --- | --- | --- |
| einen Seitentext oder Seitentitel ändern | `src/pages/<seite>.html` | Sprachebene der Seite: R-SPRACHE-1; Paragraphen: R-RECHT-1 |
| Navigation, Kolumne oder Anrufleiste ändern | `src/partials/rail.html`, `src/partials/callbar.html` | wirkt auf alle Seiten; R-BESTAND-1 |
| Farben oder Abstände ändern | `src/style.css` | R-FARBE-1 bis R-FARBE-5; hell, dunkel und schmal ansehen |
| Telefonnummer, E-Mail, Anschrift oder Sprechzeiten ändern | `src/bureauangaben.json` | unabhängige Erwartungen in `tests/site_support.py` und `tests/test_angaben.py`; [Büroangaben](docs/architektur.md#büroangaben) |
| eine Seite hinzufügen | `src/pages/`, `src/seiten.json`, Navigation, Bestandstests | [Erweiterung](docs/architektur.md#erweiterung) |
| einen Sitemap-Stand ändern | `lastmod` in `src/seiten.json` | R-ORDNUNG-6 |
| Signet oder Vorschaubild ändern | `src/grafik/` | danach `tools/bilder-erzeugen.sh`; braucht Chromium |
| veröffentlichen | Zweig, Freigabe, `main` | [Betrieb](docs/betrieb.md); R-COMMIT-3 |

## Wo steht was

Jede Aussage hat genau ein Zuhause (R-ORDNUNG-1). Das Zuhause ergibt sich aus
der Frage:

| Frage | Dokument |
| --- | --- |
| Was muss, was darf nie? Was heißt welcher Begriff? | [AGENTS.md](AGENTS.md) |
| Wie funktioniert es: Verzeichnisse, Build, Prüfkette? | [docs/architektur.md](docs/architektur.md) |
| Wie wird geschrieben, welche Rechtsstände gelten? | [docs/redaktion.md](docs/redaktion.md) |
| Was bedeuten die Farben, woher kommt das Ornament? | [docs/gestaltung.md](docs/gestaltung.md) |
| Wie wird veröffentlicht und live geprüft? | [docs/betrieb.md](docs/betrieb.md) |
| Warum wurde so entschieden? | [docs/entscheidungen.md](docs/entscheidungen.md) |
| Was fehlt noch? | `docs/lokal/offen.md` — lokal und unversioniert, weil dieses Repository öffentlich ist |

## Rechte

Alle Rechte vorbehalten; siehe [LICENSE](LICENSE).
