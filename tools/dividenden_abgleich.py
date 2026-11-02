#!/usr/bin/env python3
"""Automatischer Abgleich der Dividendendaten fuer cleverfaktor.de.

Liest dividenden.json und tools/tickers.json, holt je Aktie den Dividendenverlauf
(kostenlose Datenquelle: Yahoo Finance ueber die Bibliothek yfinance) und
- aktualisiert NUR Schaetzbetraege (schaetzung_betrag / schaetzung_nach_monat), wenn der neue
  Betrag um hoechstens 30 % vom bisherigen abweicht,
- entfernt vergangene Zahlungen (Zahltag vor dem laufenden Monat),
- setzt abgerufen/updated/stand,
- schreibt alles Auffaellige nach auffaelligkeiten.md (Kuerzung/Erhoehung, starke Abweichung,
  ausbleibende Zahlung, Waehrung, nicht abrufbar). Diese Liste prueft Claude (quartalsweise).

Nicht automatisch geaendert werden: bestaetigte Zahlungen und Termine, Dividendenhinweise
(aenderung), Quellensteuer, ISIN, Namen. Nie werden Eintraege entfernt oder hinzugefuegt.

Datenquelle austauschbar: nur die Funktion fetch_history() ersetzen.
Test ohne Netz: Umgebungsvariable CF_MOCK=pfad/zu/mock.json (id -> Liste [ex, betrag, waehrung]).
"""
import json, os, sys, time, datetime as dt

HEUTE = dt.date.fromisoformat(os.environ['CF_HEUTE']) if os.environ.get('CF_HEUTE') else dt.date.today()
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATEI = os.path.join(ROOT, 'dividenden.json')
TICKER = os.path.join(ROOT, 'tools', 'tickers.json')
BERICHT = os.path.join(ROOT, 'auffaelligkeiten.md')
MAX_ABWEICHUNG = 0.30   # darueber nur melden, nicht uebernehmen
MAX_FEHLER_ANTEIL = 0.25  # mehr Abrufausfaelle: Lauf abbrechen, nichts schreiben


def fetch_history(ticker):
    """Liste (ex_datum, betrag_je_aktie, waehrung) der letzten ~3 Jahre, aelteste zuerst."""
    mock = os.environ.get('CF_MOCK')
    if mock:
        m = json.load(open(mock))
        if ticker not in m:
            raise RuntimeError('kein Mock')
        return [(dt.date.fromisoformat(a), float(b), c) for a, b, c in m[ticker]]
    import yfinance as yf
    t = yf.Ticker(ticker)
    s = t.dividends
    if s is None or len(s) == 0:
        return []
    cur = (t.fast_info.get('currency') if hasattr(t, 'fast_info') else None) or ''
    out = []
    for idx, val in s.items():
        d = idx.date() if hasattr(idx, 'date') else idx
        if d >= HEUTE - dt.timedelta(days=3 * 365):
            out.append((d, float(val), cur))
    return sorted(out)


def norm_cur(c):
    return {'GBp': 'GBP', 'GBX': 'GBP', 'GBP': 'GBP'}.get(c, c)


def fmt(x):
    return ('%.4f' % x).rstrip('0').rstrip('.').replace('.', ',')


def lade():
    return json.load(open(DATEI, encoding='utf-8')), json.load(open(TICKER, encoding='utf-8'))


def gueltig(d):
    if not isinstance(d.get('aktien'), list) or len(d['aktien']) < 10:
        return False
    ids = set()
    for a in d['aktien']:
        if not (a.get('id') and a.get('name') and a.get('waehrung') and isinstance(a.get('zahlungen'), list)):
            return False
        if a['id'] in ids:
            return False
        ids.add(a['id'])
    return True


def zahlmonat(a, ex):
    """Passender Zahlmonat der Schaetzung zum Ex-Tag (gleicher Monat bis +2 Monate)."""
    ms = a.get('schaetzung_monate') or []
    for off in (0, 1, 2):
        m = (ex.month - 1 + off) % 12 + 1
        if m in ms:
            return m
    return None


def main():
    d, T = lade()
    vorher = json.dumps(d, ensure_ascii=False, sort_keys=True)
    n0 = len(d['aktien'])
    flags, geaendert, ok, fehler = [], [], 0, []
    ersten = HEUTE.replace(day=1)
    for a in d['aktien']:
        # 1) vergangene Zahlungen entfernen (Zahltag vor dem laufenden Monat)
        neu = []
        for z in a['zahlungen']:
            try:
                zd = dt.date.fromisoformat(z['datum'] if len(z['datum']) == 10 else z['datum'] + '-28')
            except Exception:
                neu.append(z); continue
            if zd >= ersten:
                neu.append(z)
        a['zahlungen'] = neu
        cfg = T.get(a['id'])
        if not cfg or not cfg.get('t'):
            flags.append(('manuell', a['id'], a['name'], (cfg or {}).get('grund', 'kein Ticker hinterlegt') + ' - nicht automatisch geprueft'))
            continue
        try:
            h = fetch_history(cfg['t'])
            time.sleep(float(os.environ.get('CF_PAUSE', '0.4')))
        except Exception as e:
            fehler.append(a['id']); flags.append(('abruf', a['id'], a['name'], 'Abruf fehlgeschlagen (%s)' % cfg['t'])); continue
        if not h:
            fehler.append(a['id']); flags.append(('abruf', a['id'], a['name'], 'keine Dividendendaten bei der Quelle (%s)' % cfg['t'])); continue
        ok += 1
        h = sorted(h)
        f = cfg.get('f', 1.0)
        h = [(ex, (b / 100.0 if c in ('GBp', 'GBX') else b) * f, norm_cur(c)) for ex, b, c in h]
        quell_cur = h[-1][2]
        if quell_cur and quell_cur != a['waehrung']:
            flags.append(('waehrung', a['id'], a['name'], 'Quelle liefert %s, Eintrag steht in %s - nicht automatisch geprueft' % (quell_cur, a['waehrung']))); continue
        ex, betrag, _ = h[-1]
        # ausbleibende Zahlung
        if len(h) >= 3:
            abst = [(h[i][0] - h[i - 1][0]).days for i in range(max(1, len(h) - 4), len(h))]
            mittel = sum(abst) / len(abst)
            if mittel > 20 and (HEUTE - ex).days > mittel * 1.5 + 30:
                flags.append(('ausgeblieben', a['id'], a['name'], 'letzter Ex-Tag %s, ueblicher Abstand ca. %d Tage - Aussetzung/Kuerzung moeglich' % (ex.isoformat(), mittel)))
        # Betragsvergleich
        pm = zahlmonat(a, ex)
        nach = a.get('schaetzung_nach_monat') or {}
        ref = nach.get(str(pm)) if (pm and str(pm) in nach) else a.get('schaetzung_betrag')
        if not ref or ref <= 0:
            continue
        quot = betrag / ref
        if abs(quot - 1) < 0.005:
            a['abgerufen'] = HEUTE.isoformat(); continue
        if (HEUTE - ex).days > 150:
            continue  # alter Ex-Tag: keine Aenderung der Schaetzung
        txt = '%s -> %s %s (Ex-Tag %s, %+.1f %%)' % (fmt(ref), fmt(betrag), a['waehrung'], ex.isoformat(), (quot - 1) * 100)
        if abs(quot - 1) <= MAX_ABWEICHUNG:
            if str(pm) in nach:
                nach[str(pm)] = round(betrag, 4); a['schaetzung_nach_monat'] = nach
            if str(pm) not in nach or a.get('rhythmus') in ('monatlich', 'quartalsweise'):
                a['schaetzung_betrag'] = round(betrag, 4)
            a['abgerufen'] = HEUTE.isoformat()
            geaendert.append((a['id'], a['name'], txt))
            if abs(quot - 1) >= 0.10:
                flags.append(('hinweis', a['id'], a['name'], ('Erhoehung' if quot > 1 else 'Kuerzung') + ' ab 10 %%: %s - Dividendenhinweis (aenderung) pruefen' % txt))
        else:
            flags.append(('abweichung', a['id'], a['name'], 'starke Abweichung, NICHT uebernommen (Sonderzahlung, Kuerzung, Split?): ' + txt))
    n_ges = len(d['aktien'])
    if fehler and len(fehler) / max(1, n_ges) > MAX_FEHLER_ANTEIL:
        print('ABBRUCH: zu viele Abruffehler (%d von %d), nichts geschrieben.' % (len(fehler), n_ges))
        with open(BERICHT, 'w', encoding='utf-8') as fh:
            fh.write('# Auffaelligkeiten Dividendenabgleich %s\n\nLauf abgebrochen: %d von %d Aktien nicht abrufbar. Es wurde nichts geaendert.\n' % (HEUTE.strftime('%d.%m.%Y'), len(fehler), n_ges))
        return 2
    assert len(d['aktien']) == n0 and gueltig(d), 'Datei nach Abgleich ungueltig'
    nachher = json.dumps(d, ensure_ascii=False, sort_keys=True)
    if nachher != vorher:
        d['updated'] = dt.datetime.now(dt.timezone(dt.timedelta(hours=1))).replace(microsecond=0).isoformat()
        d['stand'] = HEUTE.isoformat()
        with open(DATEI, 'w', encoding='utf-8') as fh:
            json.dump(d, fh, ensure_ascii=False, indent=2); fh.write('\n')
    # Bericht
    zeilen = ['# Auffaelligkeiten Dividendenabgleich %s' % HEUTE.strftime('%d.%m.%Y'), '',
              'Geprueft: %d von %d Aktien automatisch. Automatisch angepasste Schaetzbetraege: %d.' % (ok, n_ges, len(geaendert)), '']
    titel = {'hinweis': 'Erhoehung/Kuerzung ab 10 % (Hinweis pruefen)', 'abweichung': 'Starke Abweichung (nicht uebernommen)', 'ausgeblieben': 'Zahlung ausgeblieben?', 'waehrung': 'Waehrung weicht ab', 'abruf': 'Nicht abrufbar', 'manuell': 'Nicht automatisch geprueft'}
    for art in ('abweichung', 'ausgeblieben', 'hinweis', 'waehrung', 'abruf', 'manuell'):
        z = [x for x in flags if x[0] == art]
        if z:
            zeilen += ['## %s (%d)' % (titel[art], len(z)), ''] + ['- %s (%s): %s' % (n, i, t) for _, i, n, t in z] + ['']
    if geaendert:
        zeilen += ['## Automatisch angepasste Schaetzbetraege (%d)' % len(geaendert), ''] + ['- %s (%s): %s' % (n, i, t) for i, n, t in geaendert] + ['']
    open(BERICHT, 'w', encoding='utf-8').write('\n'.join(zeilen))
    kritisch = [x for x in flags if x[0] in ('abweichung', 'ausgeblieben', 'hinweis')]
    print('fertig: %d geprueft, %d angepasst, %d kritische Auffaelligkeiten' % (ok, len(geaendert), len(kritisch)))
    gh = os.environ.get('GITHUB_OUTPUT')
    if gh:
        open(gh, 'a').write('kritisch=%d\nangepasst=%d\n' % (len(kritisch), len(geaendert)))
    return 0


if __name__ == '__main__':
    sys.exit(main())
