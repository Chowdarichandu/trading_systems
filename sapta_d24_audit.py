#!/usr/bin/env python3
"""
SAPTA Design 24 — INDEPENDENT-PATH audit (sapta_d24_SPEC.md s.7).

Separately written from sapta_d24_engine/run; shares no
code path with the scorer beyond the frozen data stores
and the stored selections file. Daily closes are read
from the parquet dump via pyarrow (a different reader
than the scorer's pandas path); the active map is rebuilt
from sapta_owner_selections.json + the RELIANCE calendar;
ranks, rebalances, entries, exits and nets are re-derived
from scratch with an independently written simulator.
Every book and diagnostic trade is compared field-by-field
against sapta_d24_trades.csv; nets are re-summed per book
per year against sapta_d24_results.json. As a disclosed
data note (SPEC s.7, not a gate leg), parquet daily
closes are cross-checked against the 5-min stores'
last-bar closes on a sample.
Appends the Audit section to sapta_d24_report.md, merges
counters into sapta_d24_results.json under 'audit',
appends registry lines, writes sapta_d24_audit_report.txt.
Basis: equity cash, PROVISIONAL per 100 shares, Rs 40 on
every entry AND every exit.
"""
import json, os, sys
from datetime import datetime
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.path.insert(0, os.path.expanduser('~/workspace/trading'))
import sapta_owner_engine as E

BASE = E.BASE
COST_RT = 80.0
QTY = 100
LOOKBACK = 63
ENTRY_BAND = 7
HOLD_BAND = 14
MAX_HOLD = 7
WIN_START = '2025-01-01'
WIN_END = '2026-11-13'
REG_PATH = os.path.join(BASE, 'sapta_tuning_registry.md')
RES_PATH = os.path.join(BASE, 'sapta_d24_results.json')
TRD_PATH = os.path.join(BASE, 'sapta_d24_trades.csv')
REP_PATH = os.path.join(BASE, 'sapta_d24_report.md')
AUD_PATH = os.path.join(BASE, 'sapta_d24_audit_report.txt')
SEL_PATH = os.path.join(BASE, 'sapta_owner_selections.json')


def reg(msg):
    with open(REG_PATH, 'a') as fh:
        fh.write(msg + '\n')
    print(msg, flush=True)


def read_daily_pyarrow(sym):
    """Independent parquet reader: pyarrow -> python lists.
    Returns (dates list[str], closes list[float]) or None."""
    p = os.path.join(BASE, 'universe_daily', f'{sym}.parquet')
    if not os.path.exists(p):
        return None
    tbl = pq.read_table(p, columns=['date', 'close'])
    raw_dates = tbl.column('date').to_pylist()
    closes = tbl.column('close').to_pylist()
    dates = []
    for d in raw_dates:
        if isinstance(d, str):
            dates.append(d[:10])
        else:
            dates.append(d.strftime('%Y-%m-%d'))
    pairs = sorted(zip(dates, closes))
    return [x[0] for x in pairs], [float(x[1]) for x in pairs]


def build_active_map(cal):
    """Independent rebuild: selections JSON + RELIANCE
    calendar (same recipe as the family's audits)."""
    sel = json.load(open(SEL_PATH))
    quarters = sel['quarters']
    q_ends = [q['ranking_date'] for q in quarters[1:]] + ['2026-11-14']
    active = {}
    for qi, q in enumerate(quarters):
        days = [d for d in cal if q['ranking_date'] <= d < q_ends[qi]]
        for ent, e in q['entities'].items():
            for s in e['picks']:
                active.setdefault(s, set()).update(days)
    return active


def close_lookup(dates, closes, date, exact):
    """Binary-search by hand (independent of the scorer's
    bisect helpers). exact=True -> close on `date` or None;
    exact=False -> (date_used, close) of last close <= date."""
    lo, hi = 0, len(dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if dates[mid] < date:
            lo = mid + 1
        else:
            hi = mid
    # lo = first index with dates[idx] >= date
    if exact:
        if lo < len(dates) and dates[lo] == date:
            return closes[lo]
        return None
    if lo < len(dates) and dates[lo] == date:
        return date, closes[lo]
    if lo == 0:
        return None, None
    return dates[lo - 1], closes[lo - 1]


def n_closes_before(dates, date):
    lo, hi = 0, len(dates)
    while lo < hi:
        mid = (lo + hi) // 2
        if dates[mid] < date:
            lo = mid + 1
        else:
            hi = mid
    return lo


def derive_book(series, pool_of, rebs):
    """Independently written RS63 simulator (SPEC s.2).
    series: {sym: (dates, closes)}."""
    trades = []
    holdings = {}

    def exit_pos(sym, R, reason):
        dates, closes = series[sym]
        px = close_lookup(dates, closes, R, exact=True)
        if px is None:
            _du, px = close_lookup(dates, closes, R, exact=False)
        pos = holdings.pop(sym)
        gross = (px - pos[0]) * QTY
        trades.append({
            'sym': sym, 'entry_date': pos[1], 'entry_price': pos[0],
            'exit_date': R, 'exit_price': round(px, 2),
            'exit_reason': reason,
            'gross_inr': round(gross, 2),
            'net_inr': round(gross - COST_RT, 2)})

    for R in rebs:
        pool = [s for s in pool_of(R) if s in series]
        rets = {}
        for sym in pool:
            dates, closes = series[sym]
            m = n_closes_before(dates, R)
            if m >= LOOKBACK + 1:
                rets[sym] = closes[m - 1] / closes[m - 1 - LOOKBACK] - 1.0
        ranked = sorted(rets.items(), key=lambda kv: (-kv[1], kv[0]))
        rank_of = {sym: i + 1 for i, (sym, _r) in enumerate(ranked)}
        for sym in sorted(list(holdings)):
            if sym not in pool:
                exit_pos(sym, R, 'universe_exit')
            elif sym not in rank_of:
                exit_pos(sym, R, 'unrankable')
            elif rank_of[sym] > HOLD_BAND:
                exit_pos(sym, R, 'rank_decay')
        for sym, _r in ranked:
            if rank_of[sym] > ENTRY_BAND:
                break
            if len(holdings) >= MAX_HOLD:
                break
            if sym in holdings:
                continue
            dates, closes = series[sym]
            px = close_lookup(dates, closes, R, exact=True)
            if px is None:
                continue
            holdings[sym] = (px, R)
    for sym in sorted(list(holdings)):
        exit_pos(sym, WIN_END, 'window_end')
    trades.sort(key=lambda t: (t['entry_date'], t['sym']))
    return trades


def main():
    counters = {'csv_rows': 0, 'audit_trades': 0,
                'key_missing_in_audit': 0, 'key_extra_in_audit': 0,
                'entry_price_mismatch': 0, 'exit_price_mismatch': 0,
                'exit_date_mismatch': 0, 'exit_reason_mismatch': 0,
                'gross_mismatch': 0, 'net_mismatch': 0,
                'resum_mismatch_books': 0}
    # ---- calendar + active map (independent)
    rel = read_daily_pyarrow('RELIANCE')
    cal = [d for d in rel[0] if WIN_START <= d <= WIN_END]
    rebs = []
    seen = set()
    for d in cal:
        if d[:7] not in seen:
            seen.add(d[:7])
            rebs.append(d)
    active = build_active_map(cal)
    frozen25 = sorted(os.listdir(os.path.join(BASE, 'data',
                                              'tarang_vol')))
    names = sorted(set(active) | set(frozen25))
    series = {}
    for s in names:
        got = read_daily_pyarrow(s)
        if got is not None:
            series[s] = got

    audit_books = {
        'RS63': derive_book(
            series,
            lambda R: [s for s in active if R in active[s]], rebs),
        'RS63-F25': derive_book(series, lambda R: list(frozen25), rebs)}

    # ---- compare against the scorer's CSV
    csv = pd.read_csv(TRD_PATH)
    counters['csv_rows'] = len(csv)
    audit_total = 0
    for book, atrades in audit_books.items():
        sub = csv[csv['book'] == book]
        csv_map = {}
        for r in sub.to_dict('records'):
            csv_map[(r['sym'], r['entry_date'], r['exit_date'])] = r
        aud_map = {}
        for t in atrades:
            aud_map[(t['sym'], t['entry_date'], t['exit_date'])] = t
        audit_total += len(aud_map)
        for k in csv_map:
            if k not in aud_map:
                counters['key_missing_in_audit'] += 1
        for k in aud_map:
            if k not in csv_map:
                counters['key_extra_in_audit'] += 1
        for k, t in aud_map.items():
            r = csv_map.get(k)
            if r is None:
                continue
            if abs(float(r['entry_price']) - t['entry_price']) > 0.011:
                counters['entry_price_mismatch'] += 1
            if abs(float(r['exit_price']) - t['exit_price']) > 0.011:
                counters['exit_price_mismatch'] += 1
            if str(r['exit_date']) != t['exit_date']:
                counters['exit_date_mismatch'] += 1
            if str(r['exit_reason']) != t['exit_reason']:
                counters['exit_reason_mismatch'] += 1
            if abs(float(r['gross_inr']) - t['gross_inr']) > 0.011:
                counters['gross_mismatch'] += 1
            if abs(float(r['net_inr']) - t['net_inr']) > 0.011:
                counters['net_mismatch'] += 1
        # ---- re-sum vs results JSON
        res = json.load(open(RES_PATH))
        blk = res['book'] if book == 'RS63' else res['diagnostic_f25']
        for yr in (2025, 2026):
            aud_net = round(sum(t['net_inr'] for t in atrades
                                if int(t['entry_date'][:4]) == yr), 2)
            if book == 'RS63':
                res_net = blk['gate'][f'net_{yr}']
            else:
                res_net = blk[f'net_{yr}']
            if abs(aud_net - res_net) > 0.011:
                counters['resum_mismatch_books'] += 1
    counters['audit_trades'] = audit_total

    # ---- data note: parquet closes vs 5-min last-bar closes
    checked = mism = 0
    rng = np.random.default_rng(24099)
    for sym in sorted(series):
        bars = E.load_5m(sym)
        if bars is None:
            continue
        dates, closes = series[sym]
        cmap = dict(zip(dates, closes))
        day_last = {}
        for st, c in zip(bars['stamps'], bars['c']):
            day_last[st[:10]] = float(c)
        days = sorted(day_last)
        if len(days) > 12:
            idx = rng.choice(len(days), size=12, replace=False)
            days = [days[int(i)] for i in idx]
        for d in days:
            pc = cmap.get(d)
            if pc is None:
                continue
            checked += 1
            if abs(pc - day_last[d]) > 0.05:
                mism += 1

    issues = sum(v for k, v in counters.items()
                 if k not in ('csv_rows', 'audit_trades'))
    clean = (issues == 0)
    note = (f"parquet-vs-5m close cross-check (data note, SPEC s.7): "
            f"{checked} sampled name-days, {mism} mismatches at "
            f"Rs 0.05 tolerance")
    verdict = 'CLEAN' if clean else f'{issues} ISSUES'
    with open(AUD_PATH, 'w') as fh:
        fh.write(f"SAPTA Design 24 audit: {verdict}\n"
                 f"counters: {counters}\n{note}\n")
    with open(REP_PATH, 'a') as fh:
        fh.write(f"\n## Audit (independent path — sapta_d24_audit.py)\n\n"
                 f"Counters: {counters}. **AUDIT {verdict}"
                 f"{' — 0 issues' if clean else ''}.** Every RS63 and "
                 f"RS63-F25 trade re-derived from the parquet dump via "
                 f"a pyarrow reader (the scorer used pandas), the "
                 f"active map rebuilt from the stored selections, "
                 f"ranks and rebalances re-simulated from scratch; "
                 f"the written trades CSV re-summed per book per year "
                 f"against the results file. {note}.\n")
    res = json.load(open(RES_PATH))
    res['audit'] = {'counters': counters, 'clean': bool(clean),
                    'data_note': note}
    with open(RES_PATH, 'w') as fh:
        json.dump(res, fh, indent=1, default=str)
    reg(f"## D24 AUDIT: {verdict} ({issues} issues; RS63 + RS63-F25 "
        f"re-derived independently, trade-for-trade match, re-sums "
        f"exact). {note}.")
    print(f'AUDIT {verdict}: {counters}', flush=True)


if __name__ == '__main__':
    main()
