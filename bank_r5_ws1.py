#!/usr/bin/env python3
"""Cycle 116 — WS1 wound diagnosis on the AUDITED baseline trades.
Separator test per the Round-5 freeze: a binary causal feature qualifies
only if (a) its share of the wound (negative legs in the two worst months)
is >= 2x its share of book legs, (b) it holds >= half the wound legs,
(c) its share of full-target legs < 60%."""
import csv, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import bank_r5_core as c
import newsetups_score as ns
from daytrader_cash_backtest import bias_of

TR = Path.home() / "workspace/trading"
rows = list(csv.DictReader(open(TR / "bank_engine_r5_causal_trades.csv")))
for r in rows:
    r["net"] = float(r["net_inr"]); r["ft"] = int(r["full_target"])
print(f"audited rows {len(rows)} net {sum(r['net'] for r in rows):+,.2f}")

daily = ns.DATA["BANKNIFTY"][1]
D = {str(d)[:10]: dict(open=float(o), high=float(h), low=float(l), close=float(cl))
     for d, o, h, l, cl in zip(daily["date"], daily["open"], daily["high"],
                               daily["low"], daily["close"])}
DL = sorted(D)
def bias_state(date):
    i = DL.index(date)
    if i == 0: return "none"
    return bias_of(D[DL[i - 1]])[0]
for r in rows:
    r["bias"] = bias_state(r["date"])
    r["hour"] = "early" if r["entry_time"] < "10:00" else ("mid" if r["entry_time"] < "12:00" else "late")
    ep = float(r["entry_premium"])
    r["band"] = "lt200" if ep < 200 else ("200-400" if ep < 400 else "ge400")

months = defaultdict(float)
for r in rows: months[r["date"][:7]] += r["net"]
worst_months = [m for m, _ in sorted(months.items(), key=lambda kv: kv[1])[:2]]
print("months:", {k: round(v, 2) for k, v in sorted(months.items())})
print("two worst months:", worst_months)
worst10 = sorted(rows, key=lambda r: r["net"])[:10]
print("worst 10 legs:")
for r in worst10:
    print(f"  {r['date']} {r['direction']} {r['entry_time']} {r['family']}/{r['rep']} "
          f"bias={r['bias']} net={r['net']:+,.2f} exit={r['exit_reason']}")

wound = [r for r in rows if r["net"] < 0 and r["date"][:7] in worst_months]
ft_legs = [r for r in rows if r["ft"] == 1]
print(f"\nwound legs (negatives in {worst_months}): {len(wound)} net {sum(r['net'] for r in wound):+,.2f}")
print(f"all negative legs: {sum(1 for r in rows if r['net'] < 0)} net "
      f"{sum(r['net'] for r in rows if r['net'] < 0):+,.2f}")
for dim in ("family", "direction", "bias", "hour", "band"):
    agg = defaultdict(lambda: [0, 0.0])
    for r in rows:
        if r["net"] < 0: agg[r[dim]][0] += 1; agg[r[dim]][1] += r["net"]
    print(f"negatives by {dim}:", {k: (v[0], round(v[1])) for k, v in sorted(agg.items())})

print("\nseparator test (wound = negatives in the two worst months):")
feats = {}
for dim in ("family", "direction", "bias", "hour", "band"):
    for val in sorted({r[dim] for r in rows}):
        feats[f"{dim}={val}"] = lambda r, d=dim, v=val: r[d] == v
feats["family=BASE & dir=PE"] = lambda r: r["family"] == "BASE" and r["direction"] == "PE"
feats["family=BASE & dir=CE"] = lambda r: r["family"] == "BASE" and r["direction"] == "CE"
feats["bias=bearish & dir=CE"] = lambda r: r["bias"] == "bearish" and r["direction"] == "CE"
feats["bias=bullish & dir=PE"] = lambda r: r["bias"] == "bullish" and r["direction"] == "PE"
passed = []
for name, f in feats.items():
    grp = [r for r in rows if f(r)]
    if not grp: continue
    w_share = sum(1 for r in wound if f(r)) / max(len(wound), 1)
    b_share = len(grp) / len(rows)
    ft_share = sum(1 for r in ft_legs if f(r)) / max(len(ft_legs), 1)
    ok = (w_share >= 2 * b_share) and (w_share >= 0.5) and (ft_share < 0.60)
    print(f"  {name}: book {len(grp)} ({b_share:.0%}) wound share {w_share:.0%} "
          f"FT share {ft_share:.0%} net {sum(r['net'] for r in grp):+,.0f} -> {'QUALIFIES' if ok else 'no'}")
    if ok: passed.append(name)
print("qualifying separators:", passed)
