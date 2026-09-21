# Betrieb

Wie bb-limen.de veröffentlicht und danach geprüft wird. Die Regel dazu ist
R-COMMIT-3 in [AGENTS.md](../AGENTS.md): Jeder Push nach `main` veröffentlicht.

## Veröffentlichung

Kanonische Adresse ist `https://bb-limen.de/`, das Repository
<https://github.com/Aimergentix/bb-limen.de>.

`.github/workflows/veroeffentlichung.yml` läuft bei jedem Push nach `main` und
auf Zuruf. Er ruft die Prüfung auf, lehnt offene Platzhalter ab, baut `dist/`,
lädt genau diesen Ordner als Pages-Artefakt hoch und veröffentlicht ihn. Ein
fehlgeschlagener Prüflauf blockiert die Veröffentlichung; die bisherige
Fassung bleibt dann online.

Einstellungen bei GitHub, die dazu gehören:

- **Settings → Pages → Source: GitHub Actions.**  > Ok vom user gemacht!
- **Custom domain** `bb-limen.de` und **Enforce HTTPS**. `public/CNAME` bleibt
  Teil der Ausgabe, ersetzt beim eigenen Workflow aber nicht die
  Domain-Einstellung bei GitHub.   > Ok vom user gemacht!
- **Settings → Branches → Schutz für `main`:** Pull Request erforderlich,
  Statusprüfung `pruefung` erforderlich, kein erzwungener Push. So gelangt
  nichts ungeprüft und ohne Freigabe auf die Website. > Ok vom user gemacht!

  GitHub bietet beim Einrichten nur Checks zur Auswahl an, die schon einmal
  auf einem Pull Request gemeldet wurden — der Anzeigename „Prüfung" des
  Workflows zählt dafür nicht, gesucht wird der Job-Name `pruefung`. Vor der
  ersten Einrichtung deshalb einmal einen Pull Request nach `main` öffnen
  (auch ohne Änderung), den Lauf abwarten und danach die Regel anlegen.

Offizielle Anleitungen:

- [Veröffentlichungsquelle konfigurieren](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site)
- [Eigene Pages-Workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)
- [Eigene Domain konfigurieren](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)

## Vor einer Veröffentlichung von Hand prüfen

Was kein Test sehen kann:

- Die Datumsangaben in `impressum.html` und `datenschutz.html` und der
  Inhaltsstand `lastmod` im Katalog stimmen noch (R-ANGABEN-5).
- Die Rechtsstände in [redaktion.md](redaktion.md#rechtsstände) gelten noch.
- Das Vorschaubild `public/vorschau.png` zeigt noch den richtigen Anspruch. Es
  erscheint überall dort, wo jemand den Verweis weiterschickt.
- Die offenen Punkte in `docs/lokal/offen.md` sind durchgesehen.
- Die Änderung ist breit, schmal und dunkel angesehen (R-PRUEFUNG-2).

## Nach einer Veröffentlichung prüfen

```sh
gh run list --limit 3                                   # Lauf grün?
curl -sI https://bb-limen.de/ | head -1                 # 200 über HTTPS
curl -sI http://bb-limen.de/ | grep -i '^location'      # leitet auf https um
curl -sI https://www.bb-limen.de/ | grep -i '^location' # leitet auf die Hauptdomain um
curl -s -o /dev/null -w '%{http_code}\n' https://bb-limen.de/gibt-es-nicht.html   # 404
for p in AGENTS.md src/style.css tools/build.py; do     # Quellen nicht ausgeliefert: dreimal 404
  curl -s -o /dev/null -w "%{http_code} $p\n" "https://bb-limen.de/$p"
done
```

## Von selbst

Dependabot schlägt einmal im Monat neue Versionen der GitHub Actions als Pull
Request vor. Die drei Pages-Actions laufen nur auf `main` und lassen sich auf
einem Zweig nicht erproben; nach dem Übernehmen eines solchen Vorschlags den
nächsten Veröffentlichungslauf ansehen.
