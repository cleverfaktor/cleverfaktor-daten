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

## dividenden.json

Daten des Dividendenkalenders (https://cleverfaktor.de/dividendenkalender/).
Monatlich am 20. automatisch geprüft. Schema je Aktie unverändert wie im
früheren PHP-Datenblock (id, name, isin, waehrung, land, qst, rhythmus,
zahlungen, schaetzung_monate, schaetzung_betrag, optional schaetzung_nach_monat,
zusatz_monate, zusatz_betrag, aenderung, quelle, abgerufen).
Die `id` einer Aktie nie ändern (Besucher verlieren sonst ihren Eintrag).

## amex.json

Inhalte des Amex-Kreditkarten-Vergleichs. Monatlich am 5. automatisch geprüft.
Immer genau 4 Zellen je Zeile in fester Reihenfolge: American Express Card,
Blue Card, Gold Card aus Metall, Platinum Card. Zelltypen: offer, main, yes,
no, chips, yeslist. Affiliate-Links, Bilder und Affiliate-Hinweis stehen fest
im Code auf der Website und gehören nicht in diese Datei.
