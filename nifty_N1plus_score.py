#!/usr/bin/env python3
"""NIFTY ONLY upgrade tuning vs U1-N1. Paper only, no orders, no stocks.
Frozen definitions (stated in index_upgrade_nifty_N1plus.md before results):
- VIOLENT-DAY: Nifty spot daily high-low >= 300 points (progressive spot_daily).
- RUNNER: violent days only; after premium +90 (Oct) stop->entry, 2nd target +150,
  else 15:10 close / breakeven stop. Spot translation Jan-Sep: target-exit legs only,
  continue after original exit for one more equal favourable leg, BE stop = entry spot.
- VOLATILE-STOP: violent days only, premium stop -65 (VS65) or -75 (VS75), target +90.
  Jan-Sep native spot stops are not -50 premium stops: unchanged, labelled.
- PREMIUM GATE: Oct only; skip leg if entry premium bar closes < its open.
"""
import csv, json
from pathlib import Path
from collections import defaultdict

B = Path.home() / "workspace/trading"
LOT, COST = 65, 220.0
LEGACY = {"NIFTY_22500PE_2026-10-23_2026-10-27": "candles_Nifty_50_22500PE_2026-10-23.json",
          "NIFTY_22600CE_2026-10-26_2026-10-27": "candles_Nifty_50_22600CE_2026-10-26.json",
          "NIFTY_22500PE_2026-10-28_2026-11-03": "candles_Nifty_50_22500PE_2026-10-28.json"}
OUTD = B / "v4_options_oct_data"

def premium_candles(r):
    strike = str(int(float(r['strike'])))
    tag = f"NIFTY_{strike}{r['direction']}_{r['date']}_{r['expiry']}"
    p = OUTD / LEGACY.get(tag, f"candles_premium_{tag}.json")
    if not p.exists(): return None
    d = json.loads(p.read_text())
    cs = sorted(d["data"]["candles"], key=lambda c: c[0])
    return [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs]

# spot data
spot5 = defaultdict(list)
with open(B / "data/progressive/NIFTY/spot_5m.csv") as f:
    for r in csv.DictReader(f):
        spot5[r['timestamp'][:10]].append((r['timestamp'][11:16], float(r['open']), float(r['high']), float(r['low']), float(r['close'])))
daily_range = {}
with open(B / "data/progressive/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        daily_range[r['date'][:10]] = float(r['high']) - float(r['low'])

with open(B / "index_options_U1_N1_nifty_trades.csv") as f:
    n1 = list(csv.DictReader(f))
for r in n1:
    r['violent'] = daily_range.get(r['date'], 0) >= 300
    r['base_net'] = float(r['net_rs'])

oct_legs = [r for r in n1 if r['month'] == '10']
jansep = [r for r in n1 if r['month'] != '10']

def replay_premium(r, stop_pts=50.0, runner=False):
    cs = premium_candles(r)
    if cs is None: return None
    bars = [c for c in cs if c[0] >= r['entry_time']]
    if not bars: return None
    entry = float(r['entry_value'])
    stop, target = entry - stop_pts, entry + 90.0
    for i, (t, o, h, l, cl) in enumerate(bars):
        if t > "15:10": break
        if l <= stop:
            return dict(net=round((stop - entry) * LOT - COST, 2), exit_reason='stop', exit_time=t, ft=0)
        if h >= target:
            if not runner:
                return dict(net=round((target - entry) * LOT - COST, 2), exit_reason='target', exit_time=t, ft=1)
            # runner: continue after this bar, BE stop, 2nd target +150
            stop2, target2 = entry, entry + 150.0
            for (t2, o2, h2, l2, cl2) in bars[i+1:]:
                if t2 > "15:10": break
                if l2 <= stop2:
                    return dict(net=round((stop2 - entry) * LOT - COST, 2), exit_reason='runner_be_stop', exit_time=t2, ft=1)
                if h2 >= target2:
                    return dict(net=round((target2 - entry) * LOT - COST, 2), exit_reason='runner_target150', exit_time=t2, ft=1)
                if t2 == "15:10":
                    return dict(net=round((cl2 - entry) * LOT - COST, 2), exit_reason='runner_square_off', exit_time=t2, ft=1)
            last = bars[-1]
            return dict(net=round((last[4] - entry) * LOT - COST, 2), exit_reason='runner_square_off', exit_time=last[0], ft=1)
        if t == "15:10":
            return dict(net=round((cl - entry) * LOT - COST, 2), exit_reason='square_off', exit_time=t, ft=0)
    last = bars[-1]
    return dict(net=round((last[4] - entry) * LOT - COST, 2), exit_reason='square_off', exit_time=last[0], ft=0)

# 0. baseline reproduction (Oct)
print("=== OCT baseline replay check (-50/+90) ===")
for r in oct_legs:
    s = replay_premium(r)
    ok = s and abs(s['net'] - r['base_net']) < 0.01 and s['exit_reason'] == r['exit_reason']
    print(r['date'], r['direction'], "violent" if r['violent'] else "-", "replay", s, "base", r['base_net'], r['exit_reason'], "OK" if ok else "** MISMATCH **")

def oct_variant(name, fn):
    tot, ft, n = 0.0, 0, 0
    details = []
    for r in oct_legs:
        res = fn(r)
        if res is None:  # skipped by gate
            details.append((r, None)); continue
        n += 1; tot += res['net']; ft += res['ft']; details.append((r, res))
    print(f"\n--- {name}: Oct {n} trades net {tot:.2f} FT {ft}/{n} = {ft/n*100 if n else 0:.1f}%")
    for r, res in details:
        print(" ", r['date'], r['direction'], "V" if r['violent'] else "-", "base", r['base_net'], "->", res)
    return tot, ft, n

# RUNNER Oct
run_oct = oct_variant("RUNNER Oct", lambda r: replay_premium(r, runner=True) if r['violent'] else replay_premium(r))
# VS65 / VS75 Oct
vs65_oct = oct_variant("VS65 Oct", lambda r: replay_premium(r, stop_pts=65) if r['violent'] else replay_premium(r))
vs75_oct = oct_variant("VS75 Oct", lambda r: replay_premium(r, stop_pts=75) if r['violent'] else replay_premium(r))

# PREMIUM GATE Oct: entry bar close >= open?
print("\n=== GATE diagnosis: entry premium bar ===")
gate_keep = {}
for r in oct_legs:
    cs = premium_candles(r)
    bar = [c for c in cs if c[0] == r['entry_time']][0] if cs else None
    keep = bar and bar[4] >= bar[1]
    gate_keep[r['date'] + r['direction']] = keep
    print(r['date'], r['direction'], "entry bar", bar, "close>=open:", keep, "base net", r['base_net'], r['exit_reason'])
gate_oct = oct_variant("GATE Oct", lambda r: replay_premium(r) if gate_keep[r['date'] + r['direction']] else None)

# RUNNER Jan-Sep spot translation
print("\n=== RUNNER Jan-Sep spot translation ===")
runner_extra = {}  # id -> extra net
n_nc = 0
for i, r in enumerate(jansep):
    if not r['violent'] or r['exit_reason'] != 'target':
        continue
    if not r['entry_value'] or not r['exit_time'] or not r['exit_value']:
        n_nc += 1; print("NOT_COMPUTED (no entry/exit spot/time)", r['date'], r['representative_system'], r['direction']); continue
    entry, exitv = float(r['entry_value']), float(r['exit_value'])
    dist = abs(exitv - entry)
    if dist == 0: continue
    sgn = 1 if r['direction'] == 'CE' else -1
    target2 = exitv + sgn * dist
    bars = [c for c in spot5[r['date']] if c[0] > r['exit_time']]
    extra_pts, reason = None, 'square_off'
    for (t, o, h, l, cl) in bars:
        if t > "15:10": break
        if sgn == 1:
            if l <= entry: extra_pts, reason = 0.0, 'runner_be_stop'; break
            if h >= target2: extra_pts, reason = dist, 'runner_target2'; break
        else:
            if h >= entry: extra_pts, reason = 0.0, 'runner_be_stop'; break
            if l <= target2: extra_pts, reason = dist, 'runner_target2'; break
        if t == "15:10":
            extra_pts = sgn * (cl - exitv); reason = 'runner_square_off'; break
    if extra_pts is None and bars:
        extra_pts = sgn * (bars[-1][4] - exitv); reason = 'runner_square_off'
    if extra_pts is None:
        n_nc += 1; print("NOT_COMPUTED (no spot bars)", r['date']); continue
    extra = round(extra_pts * 100, 2)
    runner_extra[i] = extra
    print(r['date'], r['direction'], r['representative_system'], "entry", entry, "exit", exitv, "extra_pts", round(extra_pts,2), reason, "extra_rs", extra)
print("runner NOT_COMPUTED count:", n_nc, "applied legs:", len(runner_extra), "total extra:", sum(runner_extra.values()))

# Monthly summaries per variant
def monthly(nets_by_month):
    cum, out = 0.0, []
    for m in range(1, 11):
        v = nets_by_month.get(m, 0.0); cum += v
        out.append((m, round(v,2), round(cum,2), cum > 0))
    return out

def summarise(name, jansep_nets, oct_result):
    # jansep_nets: list aligned with jansep; oct_result: (tot, ft, n)
    tot_j = sum(jansep_nets); ft_j = sum(1 for r, net in zip(jansep, jansep_nets) if False)
    months = defaultdict(float)
    ft_by = defaultdict(int); n_by = defaultdict(int)
    for r, net in zip(jansep, jansep_nets):
        months[int(r['month'])] += net; n_by[int(r['month'])] += 1
        ft_by[int(r['month'])] += int(r['full_target'])
    months[10] += oct_result[0]; n_by[10] += oct_result[2]; ft_by[10] += oct_result[1]
    total = tot_j + oct_result[0]
    ft_total = sum(ft_by.values()); n_total = sum(n_by.values())
    print(f"\n### {name}: Jan-Oct {n_total} trades net {total:.2f} FT {ft_total}/{n_total}={ft_total/n_total*100:.1f}% freq {n_total/40.6*5:.2f}/wk | Oct {oct_result[2]} net {oct_result[0]:.2f} FT {oct_result[1]}/{oct_result[2]} freq {oct_result[2]/3.6*5:.2f}/wk")
    for m, v, cum, green in monthly(months):
        print(f"  month {m}: n={n_by[m]} net {v:.2f} cum {cum:.2f} {'green' if green else 'RED'}")
    return total

base_jan = [r['base_net'] for r in jansep]
base_oct = (sum(r['base_net'] for r in oct_legs), sum(int(r['full_target']) for r in oct_legs), len(oct_legs))
summarise("BASELINE N1", base_jan, base_oct)
run_jan = [r['base_net'] + runner_extra.get(i, 0.0) for i, r in enumerate(jansep)]
summarise("RUNNER", run_jan, run_oct)
summarise("VS65 (Jan-Sep unchanged by construction)", base_jan, vs65_oct)
summarise("VS75 (Jan-Sep unchanged by construction)", base_jan, vs75_oct)
# Gate Jan-Oct: gate is Oct-only rule, Jan-Sep unchanged
summarise("GATE (Oct only; Jan-Sep unchanged)", base_jan, gate_oct)

# Diagnosis: spot target / premium miss, all U1 Oct Nifty legs
print("\n=== DIAGNOSIS all U1 Oct Nifty legs: spot vs premium ===")
with open(B / "index_options_U1_janoct_trades.csv") as f:
    u1oct = [r for r in csv.DictReader(f) if r['index'] == 'NIFTY' and r['date'] >= '2026-10-01']
with open(B / "index_options_premium_october_trades.csv") as f:
    prem = [r for r in csv.DictReader(f) if r['index'] == 'NIFTY']
spot_by_key = {}
for r in prem:
    spot_by_key[(r['date'], r['direction'])] = (r['version'], float(r['spot_net']), r['spot_exit'])
for r in u1oct:
    in_n1 = any(x['date'] == r['date'] and x['direction'] == r['direction'] for x in n1)
    print(r['date'], r['direction'], r['representative_system'], "in_N1" if in_n1 else "dropped_by_N1",
          "premium_exit", r['exit_reason'], "premium_net", r['net_rs'], "| component spot legs:", spot_by_key.get((r['date'], r['direction'])))

import pickle
with open('/tmp/n1plus.pkl','wb') as f:
    pickle.dump(dict(run_oct=run_oct, vs65_oct=vs65_oct, vs75_oct=vs75_oct, gate_oct=gate_oct, runner_extra=runner_extra, gate_keep=gate_keep), f)
