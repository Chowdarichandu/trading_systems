#!/usr/bin/env python3
"""RUN 2 diagnosis 2 — (a) both-direction days & leg order within day,
(b) days-to-expiry buckets, (c) SPOT day-open recross behaviour per leg:
first post-entry spot bar closing on the wrong side of the day open, and the
premium outcome if exited at that bar's premium close. Causal throughout.
Nifty ONLY."""
import csv, sys
from pathlib import Path
from collections import defaultdict
from datetime import date as ddate
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
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
tot = round(sum(r["net"] for r in res), 2)
print("best book check:", len(res), tot, "NC", nc)
assert tot == 92437.75
key2leg = {(l["date"], l["direction"]): l for l in C3L}
res_sorted = sorted(res, key=lambda x: (x["date"], x["entry_time"]))

# (a) leg order within day / both-direction days
byday = defaultdict(list)
for r in res_sorted: byday[r["date"]].append(r)
g = defaultdict(lambda: [0, 0.0])
for day, legs in byday.items():
    both = len({x["direction"] for x in legs}) > 1
    for i, x in enumerate(legs):
        tag = ("BOTH" if both else "SINGLE") + f"_leg{i+1}"
        g[tag][0] += 1; g[tag][1] += x["net"]
        g["BOTH_all" if both else "SINGLE_all"][0] += 1; g["BOTH_all" if both else "SINGLE_all"][1] += x["net"]
print("\n== day structure ==")
for k in sorted(g): print(k, g[k][0], round(g[k][1], 2))

# (b) days to expiry
g2 = defaultdict(lambda: [0, 0.0])
for r in res_sorted:
    l = key2leg[(r["date"], r["direction"])]
    dte = (ddate.fromisoformat(l["expiry"]) - ddate.fromisoformat(r["date"])).days
    bucket = "0-4" if dte <= 4 else ("5-9" if dte <= 9 else "10+")
    g2[bucket][0] += 1; g2[bucket][1] += r["net"]
    if r["date"][5:7] in ("05", "08"): g2[bucket + "|weak"] [0] += 1; g2[bucket + "|weak"][1] += r["net"]
print("\n== days-to-expiry ==")
for k in sorted(g2): print(k, g2[k][0], round(g2[k][1], 2))

# (c) spot day-open recross: for each leg, scan spot bars from entry bar to the
# leg's best-book exit time; first bar whose CLOSE is on the wrong side of the
# day open (CE: close < open; PE: close > open). Premium exit at that bar =
# close of the option candle at the same timestamp.
print("\n== spot recross of day open (within best-book holding window) ==")
tripped = []
for r in res_sorted:
    l = key2leg[(r["date"], r["direction"])]
    bars = spot.get(r["date"], [])
    if not bars: continue
    dopen = bars[0][1]
    sgn = 1.0 if r["direction"] == "CE" else -1.0
    cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    prem = {b[0]: b[4] for b in cs}
    entry_prem = [b for b in cs if b[0] == l["entry_time"]][0][1]
    trip = None
    for (tm, o, h, lo, cl) in bars:
        if tm < l["entry_time"] or tm > r["exit_time"]: continue
        if sgn * (cl - dopen) < 0:
            if tm in prem:
                alt = round((prem[tm] - entry_prem) * 65 - 220.0, 2)
                trip = (tm, alt)
            break
    if trip:
        tripped.append((r["date"], r["direction"], r["net"], trip[0], trip[1], round(trip[1] - r["net"], 2), r["exit_reason"]))
for t in tripped: print(t)
print("tripped legs:", len(tripped), "of", len(res_sorted),
      "| delta if exited at recross:", round(sum(t[5] for t in tripped), 2))
print("winners (net>3000) tripped:", [t for t in tripped if t[2] > 3000])
