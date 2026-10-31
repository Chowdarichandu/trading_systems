#!/usr/bin/env python3
"""RUN 2 diagnosis 10 — (a) spot opening-range breakout confirmation: at entry,
is the last pre-entry spot close beyond the 09:15-09:45 opening-range extreme
in the trade direction (for entries before 09:45, the range so far)?
(b) pre-entry spot range as a ratio of the prior day's full range (expansion
state). (c) nsrc composition of the 4 EXP0-dropped DTE0 legs (for the record).
On the EXP0 book (a)/(b). Causal. Nifty ONLY."""
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
days_sorted = sorted(spot)

B = pool()
ALL = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
C3L = [l for l in ALL if l["date"] != l["expiry"]]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
assert round(sum(r["net"] for r in res), 2) == 98001.0
key2leg = {(l["date"], l["direction"]): l for l in C3L}
full, _ = score(ALL, geom)
print("== (c) DTE0 dropped legs composition ==")
for r in full:
    l = [x for x in ALL if x["date"] == r["date"] and x["direction"] == r["direction"]][0]
    if r["date"] == l["expiry"]:
        print(r["date"], r["direction"], "nsrc", nsrc(l), "sources", l["sources"], "net", r["net"], r["exit_reason"])

def split(name, fn):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for r in res:
        l = key2leg[(r["date"], r["direction"])]
        k = fn(r, l); g[k][0] += 1; g[k][1] += r["net"]
        if r["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += r["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    for k in sorted(gw, key=str): print(" WEAK", k, gw[k][0], round(gw[k][1], 2))

def orbrk(r, l):
    bars = spot.get(r["date"], [])
    orb = [b for b in bars if b[0] < "09:45" and b[0] < l["entry_time"]] or [b for b in bars if b[0] < l["entry_time"]]
    pre = [b for b in bars if b[0] < l["entry_time"]]
    if not orb or not pre: return "NODATA"
    ref = pre[-1][4]
    if r["direction"] == "CE":
        return "BEYOND_OR" if ref > max(b[2] for b in orb) else "INSIDE_OR"
    return "BEYOND_OR" if ref < min(b[3] for b in orb) else "INSIDE_OR"
split("spot beyond opening-range extreme at entry", orbrk)

def expratio(r, l):
    bars = spot.get(r["date"], [])
    pre = [b for b in bars if b[0] < l["entry_time"]]
    i = days_sorted.index(r["date"])
    if not pre or i == 0: return "NODATA"
    prev = spot[days_sorted[i-1]]
    prng = max(b[2] for b in prev) - min(b[3] for b in prev)
    rng = max(b[2] for b in pre) - min(b[3] for b in pre)
    ratio = rng / prng if prng > 0 else 0
    return "EXPAND>=0.5" if ratio >= 0.5 else ("MID 0.25-0.5" if ratio >= 0.25 else "COMPRESSED<0.25")
split("pre-entry range / prior-day range", expratio)
