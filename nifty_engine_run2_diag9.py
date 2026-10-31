#!/usr/bin/env python3
"""RUN 2 diagnosis 9 — day-type states from the PRIOR day's spot range:
(a) today open inside vs outside prior day's [low, high] range;
(b) prior-day range width vs its own trailing 5-day median (volatility
compression / expansion state). Causal (prior day complete before entries).
On the current EXP0 book. Nifty ONLY."""
import csv, sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score

TR = Path.home() / "workspace/trading"
spot = {}
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day = r["timestamp"][:10]
        spot.setdefault(day, []).append((float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
days_sorted = sorted(spot)
daystat = {}
for d in days_sorted:
    bars = spot[d]
    daystat[d] = dict(open=bars[0][0], high=max(b[1] for b in bars), low=min(b[2] for b in bars),
                      rng=max(b[1] for b in bars) - min(b[2] for b in bars))

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
C3L = [l for l in C3L if l["date"] != l["expiry"]]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
assert round(sum(r["net"] for r in res), 2) == 98001.0
print("EXP0 book check:", len(res), 98001.0, "NC", nc)

def split(name, fn):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for r in res:
        k = fn(r); g[k][0] += 1; g[k][1] += r["net"]
        if r["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += r["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    for k in sorted(gw, key=str): print(" WEAK", k, gw[k][0], round(gw[k][1], 2))

def daytype(r):
    i = days_sorted.index(r["date"])
    if i == 0: return "NOPREV"
    prev = daystat[days_sorted[i-1]]; cur = daystat[r["date"]]
    if cur["open"] > prev["high"]: return "OPEN_ABOVE_PREV_RANGE"
    if cur["open"] < prev["low"]: return "OPEN_BELOW_PREV_RANGE"
    return "OPEN_INSIDE_PREV_RANGE"
split("today open vs prior-day range", daytype)

def compression(r):
    i = days_sorted.index(r["date"])
    if i < 5: return "SHORT_HISTORY"
    prev = daystat[days_sorted[i-1]]["rng"]
    trail = sorted(daystat[days_sorted[j]]["rng"] for j in range(i-5, i))
    med = trail[2]
    return "PREV_NARROW<0.8xMED" if prev < 0.8 * med else ("PREV_WIDE>1.25xMED" if prev > 1.25 * med else "PREV_NORMAL")
split("prior-day range vs trailing 5d median", compression)
