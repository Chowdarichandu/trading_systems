#!/usr/bin/env python3
"""Forward-paper daily runner — the four gated candidates
(owner-approved 2026-11-18; see forward_candidates_pack.md):

  TARANG-C1  T25-C frozen          (tarang25c_scorer.py)
  TARANG-C2  T25-C+TRAIL           (tarang25c_trail_scorer.py)
  SAPTA-C1   Design 16 UNION       (sapta_forward_scorer.py)
  SAPTA-C2   Design 13 GAPFADE-TRAIL (sapta_forward_scorer.py)

For one trading day (default: today, Asia/Kolkata) it:
  1. refreshes the day's 5-min bars into the family stores via
     the established Upstox v3 route (sapta_fetch_vol.call —
     browser User-Agent, token read at runtime from
     upstox_refresh/.env, never printed). HTTP 429 = HARD STOP:
     nothing is scored, all four lines report NC, exit code 3;
     the next run catches up (fetches are range-based per name).
  2. runs the four scorers for the date;
  3. appends taken trades to the per-line forward ledgers
     (idempotent by trade key LINE|date|sym);
  4. prints per-line day results and running forward totals.

--dry-run scores and prints but writes NO ledger rows (past-day
machinery checks; dry-run output never counts in forward
tallies). Scoring a same-day date before 15:35 IST is refused
(bars incomplete) unless --force.

Paper only, real money Rs 0. Equity cash, PROVISIONAL per 100
shares, Rs 40/trade. No stock options. No orders of any kind.
"""
import argparse
import csv
import json
import os
import subprocess
import sys
import tempfile
import time
import urllib.parse
from datetime import date as ddate, datetime, timedelta

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)

import sapta_fetch_vol as SF          # call(), candles(), RateLimited
import sapta_owner_engine as E
import sapta_d3_run as D3R
import tarang23_score as T23

LINES = [
    ('TARANG-C1', 'forward_tarang_c1_log.csv',
     ['tarang25c_scorer.py', '--date']),
    ('TARANG-C2', 'forward_tarang_c2_log.csv',
     ['tarang25c_trail_scorer.py', '--date']),
    ('SAPTA-C1', 'forward_sapta_c1_log.csv',
     ['sapta_forward_scorer.py', '--book', 'SAPTA-C1', '--date']),
    ('SAPTA-C2', 'forward_sapta_c2_log.csv',
     ['sapta_forward_scorer.py', '--book', 'SAPTA-C2', '--date']),
]

LEDGER_COLS = ['trade_key', 'line', 'date', 'sym', 'side',
               'entry_time', 'exit_time', 'entry_price',
               'exit_price', 'exit_reason', 'gap_pct', 'vol_ratio',
               'union_src', 'net_inr']
HEADER = ['timestamp', 'open', 'high', 'low', 'close', 'volume']


def store_path(sym):
    p = E.find_5m_store(sym)
    if p:
        return p
    root = 'data/tarang_vol' if sym in T23.NAMES23 else 'data/sapta_vol'
    return os.path.join(WS, root, sym, 'spot_5m_vol.csv')


def refresh(names, target):
    """Append missing bars (store's last date .. target) per name.
    Returns (updated_names, names_with_target_bars).
    Fix (2026-11-25, feed_fix_report FIX 2): when target == today (IST) and
    the v3 historical range route omits today (1-day publication lag), fall
    back to /v3/historical-candle/intraday/{enc}/minutes/5 and merge."""
    uni = {r['symbol']: r['instrument_key'] for r in
           csv.DictReader(open(os.path.join(WS, 'universe_daily',
                                            'universe.csv')))}
    today_s = datetime.now().astimezone().strftime('%Y-%m-%d')
    updated, have = [], 0
    for sym in names:
        path = store_path(sym)
        bars = {}
        if os.path.exists(path):
            for r in csv.DictReader(open(path)):
                bars[r['timestamp']] = [r['timestamp'], r['open'],
                                        r['high'], r['low'],
                                        r['close'], r['volume']]
        last = max(bars)[:10] if bars else None
        if last is None or last < target:
            if sym not in uni:
                print(f'  refresh: {sym} has no instrument key — '
                      f'skipped')
                continue
            frm = last or target
            enc = urllib.parse.quote(uni[sym], safe='')
            payload = SF.call(f'/v3/historical-candle/{enc}'
                              f'/minutes/5/{target}/{frm}')
            rows = SF.candles(payload)
            for row in rows:
                bars[row[0]] = [str(x) for x in row]
            if target == today_s and not any(k[:10] == target for k in bars):
                time.sleep(0.35)
                ip = SF.call(f'/v3/historical-candle/intraday/{enc}/minutes/5')
                for row in SF.candles(ip):
                    if str(row[0])[:10] == target:
                        bars[row[0]] = [str(x) for x in row]
            os.makedirs(os.path.dirname(path), exist_ok=True)
            SF.write_csv_atomic(path, HEADER,
                                [bars[k] for k in sorted(bars)])
            updated.append(sym)
            time.sleep(0.35)
        if any(k[:10] == target for k in bars):
            have += 1
    return updated, have


def append_ledger(line, fname, rows):
    path = os.path.join(WS, fname)
    seen = set()
    total = 0.0
    n_old = 0
    if os.path.exists(path):
        for r in csv.DictReader(open(path)):
            seen.add(r['trade_key'])
            total += float(r['net_inr'])
            n_old += 1
    new = []
    for r in rows:
        key = f"{line}|{r['date']}|{r['sym']}"
        if key in seen:
            continue
        seen.add(key)
        new.append({'trade_key': key, 'line': line,
                    'date': r['date'], 'sym': r['sym'],
                    'side': r['side'], 'entry_time': r['entry_time'],
                    'exit_time': r['exit_time'],
                    'entry_price': r['entry_price'],
                    'exit_price': r['exit_price'],
                    'exit_reason': r['exit_reason'],
                    'gap_pct': r['gap_pct'],
                    'vol_ratio': r['vol_ratio'],
                    'union_src': r.get('union_src', ''),
                    'net_inr': r['net_inr']})
        total += float(r['net_inr'])
    if new:
        write_header = not os.path.exists(path)
        with open(path, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=LEDGER_COLS)
            if write_header:
                w.writeheader()
            w.writerows(new)
    return new, total, n_old + len(new)


def ledger_total(fname):
    path = os.path.join(WS, fname)
    if not os.path.exists(path):
        return 0.0, 0
    tot, n = 0.0, 0
    for r in csv.DictReader(open(path)):
        tot += float(r['net_inr'])
        n += 1
    return tot, n


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--date', help='trading day YYYY-MM-DD '
                                   '(default: today, Asia/Kolkata)')
    ap.add_argument('--dry-run', action='store_true',
                    help='score and print only; write no ledger rows')
    ap.add_argument('--force', action='store_true',
                    help='allow scoring today before 15:35 IST')
    ap.add_argument('--no-fetch', action='store_true',
                    help='skip the bar refresh (stores already current)')
    args = ap.parse_args()
    now_ist = datetime.now().astimezone()
    target = args.date or now_ist.strftime('%Y-%m-%d')
    if (target == now_ist.strftime('%Y-%m-%d') and not args.force
            and now_ist.strftime('%H:%M') < '15:35'):
        print(f'REFUSED: {target} bars incomplete before 15:35 IST '
              f'(now {now_ist.strftime("%H:%M")}). Nothing scored.')
        return 2
    print(f'FORWARD CANDIDATES — {target}'
          f'{" (DRY RUN — no ledger writes)" if args.dry_run else ""}')
    names = sorted(set(T23.NAMES23) | set(D3R.UNION))
    if not args.no_fetch:
        try:
            updated, have = refresh(names, target)
        except SF.RateLimited as e:
            print(f'NC — Upstox 429 hard stop during refresh ({e}). '
                  f'No line scored for {target}; the next run '
                  f'catches up.')
            return 3
        print(f'refresh: {len(updated)} stores updated, '
              f'{have}/{len(names)} names have bars on {target}')
        if have == 0:
            print(f'no bars on {target} for any name — non-trading '
                  f'day or feed missing. Nothing scored.')
            return 0
    results = {}
    for line, fname, cmd in LINES:
        tmp = tempfile.NamedTemporaryFile(
            'w', suffix='.json', delete=False).name
        full = [sys.executable, os.path.join(WS, cmd[0])] + cmd[1:] \
            + [target, '--json', tmp]
        p = subprocess.run(full, capture_output=True, text=True,
                           cwd=WS)
        if p.returncode != 0:
            tail = (p.stderr or p.stdout).strip().splitlines()
            print(f'{line}: NC — scorer failed: '
                  f'{tail[-1] if tail else "no output"}')
            results[line] = None
            continue
        rows = json.load(open(tmp))
        day_net = round(sum(float(r['net_inr']) for r in rows), 2)
        if args.dry_run:
            tot, n = ledger_total(fname)
            print(f'{line}: {len(rows)} taken, day net '
                  f'{day_net:+.2f} (dry run; ledger unchanged at '
                  f'{n} trades, {tot:+.2f})')
        else:
            new, tot, n = append_ledger(line, fname, rows)
            print(f'{line}: {len(rows)} taken ({len(new)} new), '
                  f'day net {day_net:+.2f}; forward total '
                  f'{tot:+.2f} over {n} trades')
        results[line] = day_net
    scored = sum(1 for v in results.values() if v is not None)
    print(f'done: {scored}/4 lines scored for {target}.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
