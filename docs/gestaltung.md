# Gestaltung

Was die Farben bedeuten und woher das Ornament kommt. Die verbindlichen Regeln
stehen in [AGENTS.md](../AGENTS.md) unter R-FARBE und R-VERBOT-3; die Werte
selbst im Block PALETTE in `src/style.css`.

## Farbe als Funktion

Die Farben benennen Funktionen, nicht einzelne Seiten.

- **Gold** (`--accent`, `--accent-on-carrier`) — Ordnung: Rubriken,
  Ziffern, Zierlinien, aktueller Standort und die primäre Aktion „Anrufen“.
  Auf dem hellen Papier steht ein kontraststarkes Goldocker, auf Graphit eine
  zweite, hellere Goldstufe. In der Navigation zeigt zusätzlich eine Linie
  den aktuellen Standort; Farbe allein trägt diese Information nicht.
- **Stahlblau** (`--link-ink`, `--link-on-carrier`) — Bedienung. Anklickbare
  Textstellen stehen dunkel auf Papier und hell auf Graphit. Fließtext-,
  Kontakt- und Rechtsverweise bleiben zusätzlich unterstrichen; frei stehende
  Verweistitel stehen in der Sans-Serif-Schrift. Die Kartuschen „Leichte
  Sprache“ und „Für Fachkreise“ verwenden dieselbe Bedienfarbe.
- **Warmes Steingrau** (`--meta-on-carrier`) — nicht anklickbare Nebenangaben
  in der Kolumne: Rollenbezeichnung, Beschriftungen und Namen. So sieht ein
  statischer Text nicht wie ein Verweis aus.
- **Salbei** (`--gut`) — Entlastung. Im Fließtext nur für den Block
  `.gut`, und nur dort, wo die Nachricht wirklich entlastet: keine
  Entmündigung, eigene Wahl des Betreuers, keine Kosten bei
  Mittellosigkeit, der Weg zurück. Wie viele Stellen es sind und bleiben,
  regelt R-FARBE-2. `--st-2` der Leichte-Sprache-Liste hat
  denselben Wert.
- **Papierwärme** (`--paper`, `--surface`) — keine Farbe, die man sieht,
  sondern eine Temperatur. `#fbfaf7` statt neutralem Grau.
- **Mint** (`--brand-leaf`) — gehört nur zur Blattkontur des Signets. Es ist
  Markenfarbe, keine Bedienfarbe.
- **Terrakotta** (`--leicht-ink`) — trägt auf der Leichte-Sprache-Seite
  Überschriften und Farbrhythmus, nicht die Navigation.

Dazu `--hauch` für den Farbton, der nur bei Berührung erscheint, und
`--st-1` bis `--st-5` ausschließlich für die Leichte-Sprache-Seite: dort
hilft Farbe an Listen und Überschriften beim Wiederfinden und ist damit
Funktion, keine bloße Dekoration.

Die Fachseite bleibt bewusst nüchtern.

## Ornament

Das Zierzeichen zwischen den Haarlinien ist kein Buchstabe, sondern
dasselbe Blatt wie die Marke der Kolumne (`.zierblatt`, siehe `src/style.css`).
Als SVG ist es überall dasselbe und folgt über `currentColor` der Farbe des
Ornaments. Warum es kein Schriftzeichen mehr ist, steht in
[entscheidungen.md](entscheidungen.md) unter E-04.

## Am Telefon

Auf schmalen Bildschirmen wird aus der stehenden Kolumne ein Kopfband; die
Anrufleiste bleibt unten stehen. Deshalb gehört die schmale Ansicht zu jeder
Sichtprüfung (R-PRUEFUNG-2).
