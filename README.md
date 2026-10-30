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

## depot.json

Inhalte des Depot-Vergleichs und des Broker-Finders (eine Datei für beide,
damit Tabelle und Finder nie auseinanderlaufen). Monatlich am 10. automatisch geprüft.

- `stand`: Datenstand als JJJJ-MM-TT (wird auf der Website als TT.MM.JJJJ angezeigt).
- `rows`: Abschnitte (`{"section": "..."}`) und Zeilen (`label`, optional `hint`,
  optional `highlight` für die Aktionszeile). Immer genau 11 Zellen in fester
  Reihenfolge: Trade Republic, Traders Place, SMARTBROKER+, comdirect,
  Consorsbank, finanzen.net ZERO, S Broker, tradegate.direct, XTB, justTRADE, eToro.
- Zelle = Liste von Teilen `{"t": Typ, "v": Text}`; Zeilenumbruch mit `\n`.
  Typen: `main`, `best` (günstigster Wert, grün), `sub`, `offer`, `nooffer`,
  `check`, `neutral`, `text`, `chips` (mit `items`).
- `finder.broker`: je Broker-ID (`tr`, `tp`, `sb`, `cd`, `cb`, `fz`, `sbr`, `tg`, `xtb`, `jt`, `et`)
  Kosten (`kosten1000`, `sparplanMin`), Punkte (−1 bis 3) und Begründungstexte, `minus`,
  Merkmale für den Finder: `typ` (`neo` oder `bank`), `steuer` (steuereinfach), `giro` (Girokonto beim
  selben Anbieter), `krypto` (echte Kryptos), `kinder` (Kinder-/Junior-Depot), `copy` (CopyTrading) – jeweils true/false.
- `finder.profile`: Empfehlungsprofile.
- Muss zur Tabelle passen: `kosten1000` = Zeile „Beispiel: Aktienkauf für 1.000 €“,
  `sparplanMin` und Sparplan-Texte = Zeile „ETF-Sparplan“, Zinstexte = „Zinsen auf Guthaben“.

## krypto.json

Inhalte des Kryptobörsen-Vergleichs und des Kryptobörsen-Finders. Monatlich am 15.
automatisch geprüft.

- `rows`: Zeilen mit `label`, optional `highlight`, immer genau 8 Zellen: OKX, Bitvavo,
  BISON, Crypto.com, Kraken, Trade Republic, Coinbase, 21bitcoin.
  Zelltypen: `main`, `sub`, `offer`, `yes`, `no`, `text`, `chips`, `pros`, `cons`.
- `hinweis`, `footnotes` (¹–⁴): Texte unter der Tabelle.
- `finder.ex`: je Börse `kosten500`, `kostenText` (Kraken zusätzlich `kosten500Pro`,
  `kostenTextPro`), `pay` (`sepa`, `card`, `paypal`), `minus`.
- `finder.punkte`: Bewertung je Antwort `[Punkte, Begründung]`.
- `finder.einzahlung_hinweis`: Gebührenbeispiele für Karte (`card`) und PayPal (`sonst`).
- Muss zur Tabelle passen: `kosten500` = Zeile „Kosten pro 500 € Kauf“,
  Gebührenbeispiele = Fußnote ⁴.

Für beide gilt: Affiliate- und Partnerlinks, Logos, Überschriften und Werbehinweise
stehen fest im Code auf der Website und gehören nicht in diese Dateien. Anbieter
nicht hinzufügen, entfernen oder umsortieren (das geht nur zusammen mit dem Code).
Nur Angaben aus offiziellen Preis- und Leistungsverzeichnissen bzw. Gebührenseiten
der Anbieter übernehmen. Im Zweifel den bisherigen Wert stehen lassen.
