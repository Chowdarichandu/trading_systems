#!/usr/bin/env python3
"""
SAPTA (owner spec) — INDEPENDENT-PATH audit of sapta_owner_trades.csv.

Written separately from sapta_owner_engine.py: plain-list indicator loops,
own-day exit re-derivation from the raw bars, entry-fill check, net check,
and the square-off-price regression check (every 'squareoff' exit must equal
the close of the 15:15 bar of its own date). No engine code is imported.

Exit scan order re-derived independently (frozen by the SPEC): from the fill
bar — target/stop first (stop-first), then 15:15 square-off, then Supertrend
flip at next bar open; scan resumes are irrelevant here (each recorded trade
is verified on its own).
"""
import csv, json, os, sys
from collections import defaultdict

import numpy as np
import pandas as pd

BASE = os.path.expanduser('~/workspace/trading')
TOL = 0.011
issues = []
checked = {'intra': 0, 'daily': 0, 'sqoff': 0}

# ---------------------------------------------------------------- raw loads
def load_bars(sym):
    for store in ('tarang_vol', 'sapta_vol', 'tarang_wide_vol'):
        for p in (os.path.join(BASE, 'data', store, sym, 'spot_5m_vol.csv'),
                  os.path.join(BASE, 'data', store, f'{sym}_5m.csv')):
            if os.path.exists(p):
                df = pd.read_csv(p)
                tcol = 'ts' if 'ts' in df.columns else 'timestamp'
                df = df.rename(columns={tcol: 'ts'})[['ts', 'open', 'high', 'low', 'close', 'volume']]
                df['ts'] = pd.to_datetime(df['ts'])
                return df.sort_values('ts').reset_index(drop=True)
    return None

def supertrend_dir_plain(H, L, C, mult, period=7):
    """Plain-loop Wilder ATR Supertrend. Returns list of +1/-1/0."""
    n = len(C)
    tr = [0.0] * n
    for i in range(n):
        if i == 0:
            tr[i] = H[i] - L[i]
        else:
            tr[i] = max(H[i] - L[i], abs(H[i] - C[i - 1]), abs(L[i] - C[i - 1]))
    # ATR: EMA recurrence seeded at the first TR (alpha = 1/period),
    # independently coded here from the indicator's definition.
    atr = [0.0] * n
    for i in range(n):
        atr[i] = tr[i] if i == 0 else atr[i - 1] + (tr[i] - atr[i - 1]) / period
    fu = [np.nan] * n; fl = [np.nan] * n; d = [0] * n
    for i in range(n):
        if np.isnan(atr[i]):
            continue
        hl2 = (H[i] + L[i]) / 2.0
        bu = hl2 + mult * atr[i]; bl = hl2 - mult * atr[i]
        if i == 0 or np.isnan(fu[i - 1]):
            fu[i], fl[i] = bu, bl
        else:
            fu[i] = bu if (bu < fu[i - 1] or C[i - 1] > fu[i - 1]) else fu[i - 1]
            fl[i] = bl if (bl > fl[i - 1] or C[i - 1] < fl[i - 1]) else fl[i - 1]
        if d[i - 1] == -1:
            d[i] = 1 if C[i] > fu[i] else -1
        elif d[i - 1] == 1:
            d[i] = -1 if C[i] < fl[i] else 1
        else:
            d[i] = 1 if C[i] > fl[i] else (-1 if C[i] < fu[i] else 0)
    return d

def macd_plain(C, fast=12, slow=26, sig=9):
    n = len(C)
    def ema(x, p):
        out = [np.nan] * n; k = 2.0 / (p + 1)
        s = None
        for i in range(n):
            if np.isnan(x[i]):
                continue
            s = x[i] if s is None else x[i] * k + s * (1 - k)
            out[i] = s
        return out
    ef, es = ema(C, fast), ema(C, slow)
    line = [np.nan if (np.isnan(ef[i]) or np.isnan(es[i])) else ef[i] - es[i]
            for i in range(n)]
    sgn = ema(line, sig)
    return line, sgn

# ---------------------------------------------------------------- intraday
bars_cache = {}
def get_day(sym, date):
    if sym not in bars_cache:
        df = load_bars(sym)
        if df is None:
            return None
        days = {}
        for dstr, g in df.groupby(df['ts'].dt.strftime('%Y-%m-%d')):
            g = g.sort_values('ts')
            days[dstr] = {'stamps': [t.strftime('%H:%M') for t in g['ts']],
                          'o': g['open'].tolist(), 'h': g['high'].tolist(),
                          'l': g['low'].tolist(), 'c': g['close'].tolist()}
        bars_cache[sym] = (df, days)
    return bars_cache[sym][1].get(date)

def get_full_dir(sym, mult):
    key = (sym, mult)
    if key not in bars_cache:
        pass
    df = load_bars(sym)
    H, L, C = df['high'].tolist(), df['low'].tolist(), df['close'].tolist()
    d = supertrend_dir_plain(H, L, C, mult)
    stamps = [t.strftime('%Y-%m-%d %H:%M') for t in df['ts']]
    return {s: d[i] for i, s in enumerate(stamps)}

dir_cache = {}
def audit_intraday(t):
    sym, date = t['sym'], t['date']
    day = get_day(sym, date)
    if day is None:
        issues.append(f'{sym} {date}: no bars for trade date')
        return
    stamps = day['stamps']
    sig_stamp = t['signal_stamp'][11:16]
    if sig_stamp not in stamps:
        issues.append(f'{sym} {date}: signal stamp {sig_stamp} not a bar')
        return
    si = stamps.index(sig_stamp)
    if si + 1 >= len(stamps):
        issues.append(f'{sym} {date}: signal on last bar, no fill bar')
        return
    fill = si + 1
    if t['entry_stamp'][11:16] != stamps[fill]:
        issues.append(f"{sym} {date}: entry stamp {t['entry_stamp']} != next bar {stamps[fill]}")
        return
    ep = day['o'][fill]
    if abs(ep - float(t['entry_price'])) > TOL:
        issues.append(f"{sym} {date}: entry price {t['entry_price']} != next-bar open {ep}")
        return
    side = 1 if t['side'] == 'LONG' else -1
    tgt = float(t['geom_tgt']) / 100.0; stp = float(t['geom_stp']) / 100.0  # percents
    tlevel = ep * (1 + tgt) if side > 0 else ep * (1 - tgt)
    slevel = ep * (1 - stp) if side > 0 else ep * (1 + stp)
    key = (sym, float(t['st_mult']))
    if key not in dir_cache:
        dir_cache[key] = get_full_dir(sym, float(t['st_mult']))
    dmap = dir_cache[key]
    want_dir = 1 if side > 0 else -1
    exp = None  # (exit_stamp_time, price, reason)
    for j in range(fill, len(stamps)):
        hit_t = day['h'][j] >= tlevel if side > 0 else day['l'][j] <= tlevel
        hit_s = day['l'][j] <= slevel if side > 0 else day['h'][j] >= slevel
        if hit_s:
            exp = (stamps[j], slevel, 'stop'); break
        if hit_t:
            exp = (stamps[j], tlevel, 'target'); break
        if stamps[j] == '15:15':
            exp = (stamps[j], day['c'][j], 'squareoff'); break
        if dmap.get(f'{date} {stamps[j]}', 0) == -want_dir:
            if j + 1 < len(stamps):
                exp = (stamps[j + 1], day['o'][j + 1], 'st_flip')
            else:
                exp = (stamps[j], day['c'][j], 'st_flip')
            break
    if exp is None:
        last = len(stamps) - 1
        exp = (stamps[last], day['c'][last], 'squareoff')
    got_reason = t['exit_reason']
    if got_reason != exp[2]:
        issues.append(f"{sym} {date} {t['entry_stamp']}: exit reason {got_reason} != re-derived {exp[2]}")
        return
    if t['exit_stamp'][11:16] != exp[0]:
        issues.append(f"{sym} {date}: exit stamp {t['exit_stamp']} != re-derived {exp[0]}")
        return
    if abs(float(t['exit_price']) - exp[1]) > max(TOL, 0.001 * exp[1]):
        issues.append(f"{sym} {date}: exit price {t['exit_price']} != re-derived {exp[1]:.4f} ({exp[2]})")
        return
    if got_reason == 'squareoff':
        checked['sqoff'] += 1
        i15 = stamps.index('15:15') if '15:15' in stamps else None
        if i15 is not None and abs(float(t['exit_price']) - day['c'][i15]) > TOL:
            issues.append(f"{sym} {date}: SQUARE-OFF REGRESSION — exit {t['exit_price']} != own-day 15:15 close {day['c'][i15]}")
            return
    net = (float(t['exit_price']) - float(t['entry_price'])) * side * 100 - 40.0
    if abs(net - float(t['net'])) > 0.51:
        issues.append(f"{sym} {date}: net {t['net']} != recomputed {net:.2f}")
        return
    checked['intra'] += 1

# ---------------------------------------------------------------- daily
daily_cache = {}
def audit_daily(t):
    sym = t['sym']
    if sym not in daily_cache:
        df = pd.read_parquet(os.path.join(BASE, 'universe_daily', f'{sym}.parquet'))
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        daily_cache[sym] = df.reset_index(drop=True)
    df = daily_cache[sym]
    dates = df['date'].tolist()
    O, H, L, C = (df[c].tolist() for c in ('open', 'high', 'low', 'close'))
    sig_date = t['signal_stamp'][:10]
    if sig_date not in dates:
        issues.append(f'{sym}: signal date {sig_date} not in daily bars')
        return
    si = dates.index(sig_date)
    mult = float(t['st_mult'])
    d = supertrend_dir_plain(H, L, C, mult)
    line, sgn = macd_plain(C)
    ok = (d[si] == 1 and line[si] > sgn[si])
    if str(t.get('ema50_on')) in ('True', '1'):
        # EMA-50, alpha 2/51 seeded at first close, coded independently
        k = 2.0 / 51.0
        e = C[0]
        for i in range(1, si + 1):
            e = C[i] * k + e * (1 - k)
        ok = ok and (C[si] > e)
    if not ok:
        issues.append(f'{sym} {sig_date}: daily entry state fails re-derivation (ST/MACD/EMA50)')
        return
    if t['entry_stamp'][:10] != dates[si + 1] or abs(O[si + 1] - float(t['entry_price'])) > TOL:
        issues.append(f"{sym} {sig_date}: entry {t['entry_stamp']} @ {t['entry_price']} != next open {dates[si+1]} @ {O[si+1]}")
        return
    ei = si + 1
    exp = None
    for j in range(ei, len(dates)):
        cross_down = line[j] < sgn[j] and line[j - 1] >= sgn[j - 1]
        if d[j] == -1 or cross_down:
            if j + 1 < len(dates):
                exp = (dates[j + 1], O[j + 1], 'st_flip' if d[j] == -1 else 'macd_cross')
            break
    if exp is None:
        exp = ('2026-11-13', C[dates.index('2026-11-13')], 'window_end')
    if t['exit_reason'] != exp[2] or t['exit_stamp'][:10] != exp[0] or \
       abs(float(t['exit_price']) - exp[1]) > max(TOL, 0.001 * exp[1]):
        issues.append(f"{sym} {sig_date}: exit {t['exit_stamp']} @ {t['exit_price']} ({t['exit_reason']}) "
                      f"!= re-derived {exp[0]} @ {exp[1]:.2f} ({exp[2]})")
        return
    net = (float(t['exit_price']) - float(t['entry_price'])) * 100 - 40.0
    if abs(net - float(t['net'])) > 0.51:
        issues.append(f"{sym} {sig_date}: net {t['net']} != recomputed {net:.2f}")
        return
    checked['daily'] += 1

def main():
    path = os.path.join(BASE, 'sapta_owner_trades.csv')
    rows = list(csv.DictReader(open(path)))
    print(f'trade rows: {len(rows)}')
    for t in rows:
        if t['book'] in ('C1', 'C2'):
            audit_intraday(t)
        else:
            audit_daily(t)
    print(f"checked intraday OK: {checked['intra']}, daily OK: {checked['daily']}, "
          f"square-off regression checks: {checked['sqoff']}")
    print(f'issues: {len(issues)}')
    for i in issues[:40]:
        print('  ISSUE:', i)
    verdict = 'AUDIT CLEAN' if not issues else 'AUDIT ISSUES FOUND'
    print(verdict)
    with open(os.path.join(BASE, 'sapta_audit_report.txt'), 'w') as fh:
        fh.write(f'{verdict}\nchecked: {checked}\nissues: {len(issues)}\n')
        for i in issues:
            fh.write(f'ISSUE: {i}\n')
    return 0 if not issues else 1

if __name__ == '__main__':
    sys.exit(main())
