#!/usr/bin/env python3
"""ROUND 3 WS1 diagnosis #2: compression features (entry-known) for all
adopted + difference legs, and the weekly-carriage diagnostic for the
3 August legs."""
import sys, csv, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r3_harness import score_r3, adopted_set, candles_exact
from nifty_engine_score import nsrc

TR = Path.home() / "workspace/trading"
spot5 = defaultdict(list)
with open(TR / "data/full_hist/NIFTY/spot_5m.csv") as f:
    for r in csv.DictReader(f):
        d = r["timestamp"][:10]
        if d.startswith("2026"):
            spot5[d].append((r["timestamp"][11:16], float(r["open"]), float(r["high"]),
                             float(r["low"]), float(r["close"])))
daily_rows = list(csv.DictReader(open(TR / "data/full_hist/NIFTY/spot_daily.csv")))
daily = {r["date"]: r for r in daily_rows}
dates_sorted = sorted(daily)
didx = {d: i for i, d in enumerate(dates_sorted)}

def feats(l, net):
    sp = spot5.get(l["date"], [])
    et = l["entry_time"]
    morning = [b for b in sp if b[0] <= et]
    se = next((b for b in sp if b[0] == et), None)
    morn_rng = ((max(b[2] for b in morning) - min(b[3] for b in morning)) / se[4] * 100) if morning and se else None
    i = didx.get(l["date"])
    pdr = None
    if i and i > 0:
        pr = daily[dates_sorted[i - 1]]
        pdr = (float(pr["high"]) - float(pr["low"])) / float(pr["close"]) * 100
    # 3-day realised vol of daily closes before trade date
    vol3 = None
    if i and i >= 3:
        import math
        rets = []
        for k in range(i - 3, i):
            c0 = float(daily[dates_sorted[k - 1]]["close"]) if k > 0 else None
            c1 = float(daily[dates_sorted[k]]["close"])
            if c0: rets.append(abs(c1 / c0 - 1) * 100)
        vol3 = sum(rets) / len(rets) if rets else None
    return dict(date=l["date"], dir=l["direction"], et=et, net=net,
                morn_rng=(round(morn_rng, 3) if morn_rng is not None else None),
                pd_range=(round(pdr, 3) if pdr is not None else None),
                vol3=(round(vol3, 3) if vol3 is not None else None))

EXP0, CH3R, DIFF = adopted_set()
resA, _, _ = score_r3(CH3R, lock=50.0, tgt2=175.0, arm=50.0)
netA = {(r["date"], r["direction"]): r["net"] for r in resA}
FA = [feats(l, netA[(l["date"], l["direction"])]) for l in CH3R]
resD, _, _ = score_r3(DIFF, lock=50.0, tgt2=175.0, arm=50.0)
netD = {(r["date"], r["direction"]): r["net"] for r in resD}
FD = [feats(l, netD[(l["date"], l["direction"])]) for l in DIFF]

print("=== AUGUST LEGS compression features ===")
for f in FA:
    if f["date"][:7] == "2026-08": print(f)
print("\n=== ALL ADOPTED LEGS: date dir et net morn_rng pd_range vol3 ===")
for f in sorted(FA, key=lambda x: x["date"]):
    print(f"{f['date']} {f['dir']} {f['et']} net={f['net']:>+10.2f} morn={f['morn_rng']} pdr={f['pd_range']} vol3={f['vol3']}")

def scan(name, pred, universe=FA):
    hit = [f for f in universe if pred(f)]
    print(f"SIG {name}: hits {len(hit)} net {round(sum(f['net'] for f in hit),2):+,.2f} dates {[f['date'] for f in hit]}")
print("\n=== COMPRESSION SCANS (adopted book) ===")
for th in (0.30, 0.35, 0.40, 0.45, 0.50):
    scan(f"morning spot range <= {th}%", lambda f, th=th: f["morn_rng"] is not None and f["morn_rng"] <= th)
for th in (0.60, 0.70, 0.80, 0.90):
    scan(f"prior-day spot range <= {th}%", lambda f, th=th: f["pd_range"] is not None and f["pd_range"] <= th)
scan("PE & morning range <= 0.40%", lambda f: f["dir"] == "PE" and f["morn_rng"] is not None and f["morn_rng"] <= 0.40)
scan("PE & prior-day range <= 0.80%", lambda f: f["dir"] == "PE" and f["pd_range"] is not None and f["pd_range"] <= 0.80)
scan("vol3 <= 0.45", lambda f: f["vol3"] is not None and f["vol3"] <= 0.45)

# weekly-carriage diagnostic for the 3 August legs (candles fetched in cycle 20)
wmap = json.loads((TR / "nifty_engine_run3_fetch_c19c20_report.json").read_text())["weekly_map"]
print("\n=== WEEKLY-CARRIAGE DIAGNOSTIC — the 3 August legs ===")
from nifty_engine_r3_harness import replay_r3
for l in CH3R:
    if l["date"][:7] != "2026-08": continue
    wexp = wmap[f"{l['date']}|{l['direction']}"]
    cs = candles_exact("NIFTY", l["strike"], l["direction"], l["date"], wexp)
    r = replay_r3(cs, l["entry_time"], lock=50.0, tgt2=175.0, arm=50.0) if cs else None
    print(l["date"], l["direction"], "monthly exp", l["expiry"], "-> weekly exp", wexp,
          "| weekly net:", (r["net"] if r else "NO CANDLES"), (r["exit_reason"] if r else ""))
