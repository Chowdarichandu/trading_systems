#!/usr/bin/env python3
"""ROUND 3 — WS1 (Cycle 40) and WS2 (Cycles 41-45), frozen in
nifty_engine_frozen.md Run 3 Round 3 section before this run."""
import sys, csv, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r3_harness import run_r3, adopted_set, TR
from nifty_engine_score import nsrc

rows = list(csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_daily.csv")))
daily = {r["date"]: float(r["close"]) for r in rows}
order = [r["date"] for r in rows]
prev = {order[i]: order[i - 1] for i in range(1, len(order))}
def pdret(d):
    p = prev.get(d)
    return (daily[d] / daily[p] - 1) * 100 if p else None

EXP0, CH3R, DIFF = adopted_set()
wmap = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]

# ---- Cycle 40: WS1 weekly carriage for signature legs ----
def is_sig(l):
    pd = pdret(l["date"])
    return l["direction"] == "PE" and pd is not None and -0.50 < pd < -0.25
C40 = []
for l in CH3R:
    if is_sig(l):
        nl = dict(l); nl["expiry"] = wmap[f"{l['date']}|{l['direction']}"]
        C40.append(nl)
    else:
        C40.append(l)
print(f"Cycle 40 leg set: {len(C40)} legs, {sum(1 for l in CH3R if is_sig(l))} signature legs on weekly")
run_r3("run3r3_cycle40", C40)

# ---- Cycle 41: UNION (EXP0 at adopted geometry) ----
print(f"\nCycle 41 leg set: {len(EXP0)} legs")
run_r3("run3r3_cycle41", EXP0)

# ---- Cycle 42: DIFF standalone ----
print(f"\nCycle 42 leg set: {len(DIFF)} legs")
run_r3("run3r3_cycle42", DIFF)

# ---- Cycles 43-45: single-condition admissions ----
from nifty_engine_r3_harness import candles_exact
def entry_premium(l):
    cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    bars = [b for b in cs if b[0] == l["entry_time"]] if cs else []
    return bars[0][1] if bars else None
from datetime import date
def dte(l):
    y, m, dd = l["expiry"].split("-"); e = date(int(y), int(m), int(dd))
    y, m, dd = l["date"].split("-"); t = date(int(y), int(m), int(dd))
    return (e - t).days

conds = {
    "run3r3_cycle43": ("premium<=200", lambda l: (entry_premium(l) or 1e9) <= 200.0),
    "run3r3_cycle44": ("entry<=10:30", lambda l: l["entry_time"] <= "10:30"),
    "run3r3_cycle45": ("DTE>=7", lambda l: dte(l) >= 7),
}
for name, (label, cond) in conds.items():
    adm = [l for l in DIFF if cond(l)]
    print(f"\n{name} ({label}): admits {len(adm)} of 15 diff legs -> book {len(CH3R) + len(adm)} legs")
    run_r3(name, CH3R + adm)
