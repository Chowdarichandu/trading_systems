#!/usr/bin/env python3
"""Diagnosis: spot-state alignment for C3L + G7L75 legs.
For each leg: spot day open (09:15 bar open), spot close of the bar just before
entry, move = entry_spot_prevclose - day_open. Aligned: CE & move>0, PE & move<0.
Nifty ONLY."""
import csv, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score

TR = Path.home() / "workspace/trading"
spot = defaultdict(list)
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day, tm = r["timestamp"][:10], r["timestamp"][11:16]
        spot[day].append((tm, float(r["open"]), float(r["close"])))
for d in spot: spot[d].sort()

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=150.0)
res, nc = score(C3L, geom)
key2leg = {(l["date"], l["direction"]): l for l in C3L}
groups = defaultdict(lambda: [0, 0.0])
missing = 0
for r in res:
    l = key2leg[(r["date"], r["direction"])]
    bars = spot.get(r["date"])
    if not bars: missing += 1; continue
    day_open = bars[0][1]
    prev = [b for b in bars if b[0] < l["entry_time"]]
    ref = prev[-1][2] if prev else day_open
    move = ref - day_open
    aligned = (l["direction"] == "CE" and move > 0) or (l["direction"] == "PE" and move < 0)
    g = "ALIGNED" if aligned else "AGAINST"
    groups[g][0] += 1; groups[g][1] += round(r["net"], 2)
    groups[g + "|" + r["date"][:7]][0] += 1; groups[g + "|" + r["date"][:7]][1] += round(r["net"], 2)
print("missing spot days:", missing)
for k in sorted(groups): print(k, groups[k])
