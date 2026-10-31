#!/usr/bin/env python3
"""Cycle 11 diagnosis (no candidate): pre-entry spot realised range for best-book legs.
Range = spot high-low from 09:15 up to (not incl.) entry bar, as % of day open.
Also absolute points. Split nets by range bucket, and list August legs."""
import csv, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score

TR = Path.home() / "workspace/trading"
spot = {}
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day, tm = r["timestamp"][:10], r["timestamp"][11:16]
        spot.setdefault(day, []).append((tm, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
for d in spot: spot[d].sort()

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
print("best book check:", len(res), round(sum(r["net"] for r in res),2), "NC", nc)
key2leg = {(l["date"], l["direction"]): l for l in C3L}
rows=[]
for r in sorted(res, key=lambda x: x["date"]):
    l = key2leg[(r["date"], r["direction"])]
    bars = spot.get(r["date"], [])
    pre = [b for b in bars if b[0] < l["entry_time"]]
    if not pre: print("no pre bars", r["date"]); continue
    hi = max(b[2] for b in pre); lo = min(b[3] for b in pre); op = pre[0][1]
    rng = hi-lo; rngpct = 100*rng/op
    rows.append((r["date"], r["direction"], l["entry_time"], round(rng,1), round(rngpct,3), r["net"], r["exit_reason"]))
print("\n== August legs ==")
for row in rows:
    if row[0][5:7]=="08": print(row)
print("\n== May legs ==")
for row in rows:
    if row[0][5:7]=="05": print(row)
for thr in (0.15,0.20,0.25,0.30,0.35,0.40):
    low=[r for r in rows if r[4]<thr]; high=[r for r in rows if r[4]>=thr]
    print(f"thr {thr}%: LOW n={len(low)} net={round(sum(r[5] for r in low),2)} | HIGH n={len(high)} net={round(sum(r[5] for r in high),2)}")
    la=[r for r in low if r[0][5:7]=="08"]; print(f"   August in LOW: n={len(la)} net={round(sum(r[5] for r in la),2)}")
