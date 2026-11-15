#!/usr/bin/env python3
"""
BREAK->TREND probability study (2026-11-08) — descriptive only.
Bank Nifty + Nifty 5-min spot, Jan-Oct 2026 primary, Jan-Oct 2025 stability.
Pre-registered definitions (do not alter after seeing results):
- OR = bars starting 09:15/09:20/09:25; ORH/ORL = high/low of those bars.
- UP-BREAK: first bar starting >=09:30 with CLOSE > ORH. DOWN-BREAK mirrors.
- Extension-before-failure: max high (up) from the bar AFTER the break bar
  until the first subsequent close back below ORH (failure bar's own high
  NOT included), or day end. Down mirrors with min low / close back above ORL.
- Clean trend (up): no failure close AND full remaining-day extension >= mid
  threshold (Bank 300 / Nifty 100).
- HOLD-60: no failure close within 60 minutes of the break bar start
  (failure at exactly +60 counts as failed).
- Capture (spot points only, NOT option money): entry at break price;
  (a) exit at day close; (b) exit at failure close else day close.
Days with <70 bars excluded and counted.
"""
import json, csv, statistics, random
from collections import defaultdict

THRESH = {'BANKNIFTY': [150, 300, 500], 'NIFTY': [50, 100, 175]}
MIN_BARS = 70

def tmin(t):
    h, m = t.split(':'); return int(h) * 60 + int(m)

def analyse_day(bars, thresh):
    """bars: list of [time, o, h, l, c]. Returns dict or None."""
    or_bars = [b for b in bars if b[0] in ('09:15', '09:20', '09:25')]
    if len(or_bars) < 3:
        return None
    orh = max(b[2] for b in or_bars); orl = min(b[3] for b in or_bars)
    day_close = bars[-1][4]
    out = {'orh': orh, 'orl': orl, 'day_close': day_close, 'up': None, 'down': None}

    def scan(direction):
        # find break bar
        bi = None
        for i, b in enumerate(bars):
            if tmin(b[0]) < tmin('09:30'):
                continue
            if direction == 'up' and b[4] > orh:
                bi = i; break
            if direction == 'down' and b[4] < orl:
                bi = i; break
        if bi is None:
            return None
        bp = bars[bi][4]; bt = bars[bi][0]
        mid = thresh[1]; small = thresh[0]
        ext_bf = 0.0; fail_min = None; fail_close = None
        time_to_small = None
        for k in range(bi + 1, len(bars)):
            b = bars[k]
            failed = (b[4] < orh) if direction == 'up' else (b[4] > orl)
            if failed:
                fail_min = tmin(b[0]) - tmin(bt); fail_close = b[4]
                break
            fav = (b[2] - bp) if direction == 'up' else (bp - b[3])
            if fav > ext_bf:
                ext_bf = fav
            if time_to_small is None and fav >= small:
                time_to_small = tmin(b[0]) - tmin(bt)
        full_ext = 0.0
        for k in range(bi + 1, len(bars)):
            fav = (bars[k][2] - bp) if direction == 'up' else (bp - bars[k][3])
            if fav > full_ext:
                full_ext = fav
        clean = (fail_min is None) and (full_ext >= mid)
        hold60 = (fail_min is None) or (fail_min > 60)
        cap_a = (day_close - bp) if direction == 'up' else (bp - day_close)
        exit_b = fail_close if fail_close is not None else day_close
        cap_b = (exit_b - bp) if direction == 'up' else (bp - exit_b)
        bstart = tmin(bt)
        bucket = '<=10:00' if bstart <= tmin('10:00') else ('10:05-12:00' if bstart <= tmin('12:00') else '>=12:05')
        return {'break_time': bt, 'break_price': bp, 'ext_bf': ext_bf,
                'full_ext': full_ext, 'fail_min': fail_min, 'clean': clean,
                'hold60': hold60, 'bucket': bucket, 'cap_a': cap_a,
                'cap_b': cap_b, 'time_to_small': time_to_small}
    out['up'] = scan('up')
    out['down'] = scan('down')
    # first break of the day + opposite later
    ups = out['up']; dns = out['down']
    out['first'] = None; out['opposite_later'] = False
    if ups and dns:
        if tmin(ups['break_time']) <= tmin(dns['break_time']):
            out['first'] = 'up'
        else:
            out['first'] = 'down'
        out['opposite_later'] = True
    elif ups:
        out['first'] = 'up'
    elif dns:
        out['first'] = 'down'
    return out

def pct(n, d):
    return round(100.0 * n / d, 1) if d else None

def summarise(records, thresh, direction):
    """records: list of scan dicts for one direction (non-None)."""
    n = len(records)
    if n == 0:
        return {'n': 0}
    s = {'n': n}
    for t in thresh:
        s[f'p_ext_bf_{t}'] = pct(sum(1 for r in records if r['ext_bf'] >= t), n)
        s[f'p_full_{t}'] = pct(sum(1 for r in records if r['full_ext'] >= t), n)
    s['p_clean'] = pct(sum(1 for r in records if r['clean']), n)
    s['p_fail_30'] = pct(sum(1 for r in records if r['fail_min'] is not None and r['fail_min'] <= 30), n)
    s['p_fail_60'] = pct(sum(1 for r in records if r['fail_min'] is not None and r['fail_min'] <= 60), n)
    s['med_ext_bf'] = round(statistics.median(r['ext_bf'] for r in records), 1)
    s['mean_ext_bf'] = round(statistics.mean(r['ext_bf'] for r in records), 1)
    s['med_full'] = round(statistics.median(r['full_ext'] for r in records), 1)
    tts = [r['time_to_small'] for r in records if r['time_to_small'] is not None]
    s['med_min_to_small'] = round(statistics.median(tts), 1) if tts else None
    s['n_reach_small'] = len(tts)
    s['cap_a_mean'] = round(statistics.mean(r['cap_a'] for r in records), 1)
    s['cap_a_med'] = round(statistics.median(r['cap_a'] for r in records), 1)
    s['cap_a_win'] = pct(sum(1 for r in records if r['cap_a'] > 0), n)
    s['cap_b_mean'] = round(statistics.mean(r['cap_b'] for r in records), 1)
    s['cap_b_med'] = round(statistics.median(r['cap_b'] for r in records), 1)
    s['cap_b_win'] = pct(sum(1 for r in records if r['cap_b'] > 0), n)
    h60 = [r for r in records if r['hold60']]
    s['hold60_n'] = len(h60)
    if h60:
        s['hold60_p_clean'] = pct(sum(1 for r in h60 if r['clean']), len(h60))
        for t in thresh:
            s[f'hold60_p_ext_bf_{t}'] = pct(sum(1 for r in h60 if r['ext_bf'] >= t), len(h60))
        s['hold60_cap_a_mean'] = round(statistics.mean(r['cap_a'] for r in h60), 1)
        s['hold60_cap_b_mean'] = round(statistics.mean(r['cap_b'] for r in h60), 1)
    return s

def main():
    spot = json.load(open('daily2leg/spot.json'))
    windows = {'2026': ('2026-01-01', '2026-10-31'), '2025': ('2025-01-01', '2025-10-31')}
    results = {}
    csv_rows = []
    all_break_days = []  # (index, window, date, bars, analysis) for spot-check
    for idx in ('BANKNIFTY', 'NIFTY'):
        thresh = THRESH[idx]
        for wname, (lo, hi) in windows.items():
            days = {d: b for d, b in sorted(spot[idx].items()) if lo <= d <= hi}
            excluded = [d for d, b in days.items() if len(b) < MIN_BARS]
            used = {d: b for d, b in days.items() if len(b) >= MIN_BARS}
            base = {'days_total': len(days), 'days_used': len(used), 'excluded': excluded,
                    'n_up_days': 0, 'n_down_days': 0, 'n_neither': 0, 'n_both': 0,
                    'n_first_up': 0, 'n_first_down': 0}
            ups, dns = [], []
            for d, bars in used.items():
                a = analyse_day(bars, thresh)
                if a is None:
                    continue
                if a['up']: ups.append(a['up'])
                if a['down']: dns.append(a['down'])
                if a['up'] and a['down']: base['n_both'] += 1
                if not a['up'] and not a['down']: base['n_neither'] += 1
                if a['first'] == 'up': base['n_first_up'] += 1
                if a['first'] == 'down': base['n_first_down'] += 1
                if a['up']:
                    all_break_days.append((idx, wname, d, 'up'))
                    r = a['up']
                    csv_rows.append({'index': idx, 'window': wname, 'date': d, 'direction': 'up',
                                     'orh': a['orh'], 'orl': a['orl'], 'break_time': r['break_time'],
                                     'break_price': r['break_price'], 'ext_before_failure': round(r['ext_bf'], 2),
                                     'full_ext': round(r['full_ext'], 2),
                                     'failure_minutes': r['fail_min'] if r['fail_min'] is not None else '',
                                     'clean_trend': r['clean'], 'hold60': r['hold60'], 'bucket': r['bucket'],
                                     'capture_close_pts': round(r['cap_a'], 2),
                                     'capture_failclose_pts': round(r['cap_b'], 2),
                                     'opposite_break_later': bool(a['down'])})
                if a['down']:
                    all_break_days.append((idx, wname, d, 'down'))
                    r = a['down']
                    csv_rows.append({'index': idx, 'window': wname, 'date': d, 'direction': 'down',
                                     'orh': a['orh'], 'orl': a['orl'], 'break_time': r['break_time'],
                                     'break_price': r['break_price'], 'ext_before_failure': round(r['ext_bf'], 2),
                                     'full_ext': round(r['full_ext'], 2),
                                     'failure_minutes': r['fail_min'] if r['fail_min'] is not None else '',
                                     'clean_trend': r['clean'], 'hold60': r['hold60'], 'bucket': r['bucket'],
                                     'capture_close_pts': round(r['cap_a'], 2),
                                     'capture_failclose_pts': round(r['cap_b'], 2),
                                     'opposite_break_later': bool(a['up'])})
            base['n_up_days'] = len(ups); base['n_down_days'] = len(dns)
            base['p_up'] = pct(len(ups), len(used)); base['p_down'] = pct(len(dns), len(used))
            base['p_neither'] = pct(base['n_neither'], len(used)); base['p_both'] = pct(base['n_both'], len(used))
            # buckets for up-breaks
            buckets = {}
            for bname in ('<=10:00', '10:05-12:00', '>=12:05'):
                sub = [r for r in ups if r['bucket'] == bname]
                bs = summarise(sub, thresh, 'up') if sub else {'n': 0}
                buckets[bname] = bs
            results[f'{idx}|{wname}'] = {'base': base, 'up': summarise(ups, thresh, 'up'),
                                        'down': summarise(dns, thresh, 'down'), 'up_buckets': buckets}
    with open('break_trend_days.csv', 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(csv_rows[0].keys()))
        w.writeheader(); w.writerows(csv_rows)
    json.dump(results, open('/tmp/break_trend_results.json', 'w'), indent=1, default=str)
    print(json.dumps(results, indent=1, default=str))

    # ---- spot-check: 3 random break days, independent recomputation ----
    print('\n=== SPOT CHECKS ===')
    random.seed(20261108)
    picks = random.sample(all_break_days, 3)
    spot_by = spot
    for idx, wname, d, direction in picks:
        bars = spot_by[idx][d]
        a = analyse_day(bars, THRESH[idx])
        rec = a[direction]
        # independent recompute
        orh = max(b[2] for b in bars[:3]); orl = min(b[3] for b in bars[:3])
        bi = next(i for i, b in enumerate(bars) if tmin(b[0]) >= tmin('09:30') and
                  ((b[4] > orh) if direction == 'up' else (b[4] < orl)))
        ext = 0.0; fail = None
        for k in range(bi + 1, len(bars)):
            if (bars[k][4] < orh) if direction == 'up' else (bars[k][4] > orl):
                fail = tmin(bars[k][0]) - tmin(bars[bi][0]); break
            ext = max(ext, (bars[k][2] - bars[bi][4]) if direction == 'up' else (bars[bi][4] - bars[k][3]))
        ok = (rec['break_time'] == bars[bi][0] and abs(rec['ext_bf'] - ext) < 0.01
              and rec['fail_min'] == fail)
        print(f"{idx} {d} {direction}: break {rec['break_time']} @ {rec['break_price']} "
              f"ext_bf {rec['ext_bf']:.2f} fail_min {rec['fail_min']} | independent: ext {ext:.2f} fail {fail} | MATCH={ok}")
        print('  bars around break:', bars[max(0, bi-1):bi+4])

    # ---- Friday 2026-11-06 Bank check from the intraday watcher spot file ----
    print('\n=== FRIDAY 2026-11-06 BANKNIFTY ===')
    import glob
    fpath = sorted(glob.glob('/home/hatch/workspace/goals/3-blue-line-bank-nifty-backtest/hidden_files/spot_bank_5m_2026-11-06_*.json'))[-1]
    raw = json.load(open(fpath))
    bars = [[r[0][11:16], r[1], r[2], r[3], r[4]] for r in raw]
    a = analyse_day(bars, THRESH['BANKNIFTY'])
    u = a['up']
    print('file:', fpath, 'bars:', len(bars))
    print(f"ORH {a['orh']} ORL {a['orl']} | up-break {u['break_time']} @ {u['break_price']} | "
          f"ext_bf {u['ext_bf']:.2f} full_ext {u['full_ext']:.2f} fail_min {u['fail_min']} "
          f"clean={u['clean']} hold60={u['hold60']} bucket={u['bucket']} capA={u['cap_a']:.2f} capB={u['cap_b']:.2f}")
    print('down-break:', a['down'])

if __name__ == '__main__':
    main()
