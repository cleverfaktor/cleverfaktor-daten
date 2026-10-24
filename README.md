# cleverfaktor-daten

Marktdaten für cleverfaktor.de

## wochenkalender.json

Wird täglich automatisch aktualisiert und vom Marktüberblick auf
https://cleverfaktor.de/marktueberblick/ abgerufen.

- `week_start` / `week_end`: angezeigte Börsenwoche (Montag bis Freitag).
  Montag bis Freitag die laufende Woche, am Wochenende die kommende.
- `rates`: aktuelle Leitzinsen (EZB-Einlagensatz, Fed-Zielspanne, Bank-of-Japan-Leitzins).
- `events`: wichtige Termine. `time` in deutscher Ortszeit (leer = ohne Uhrzeit).
  `type`: `notenbank`, `inflation`, `konjunktur`, `arbeitsmarkt`, `politik`.
  `region`: `US`, `EU`, `DE`, `JP`.
- `earnings`: Quartalszahlen bekannter Unternehmen, nur Datum.

Nur bestätigte Termine aus offiziellen oder etablierten Quellen. Im Zweifel weglassen.
Keine Anlageberatung.
