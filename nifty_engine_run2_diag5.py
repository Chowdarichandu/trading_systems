#!/usr/bin/env python3
"""RUN 2 diagnosis 5 — SPOT-arm incidence. For each best-book leg: maximum
signed spot excursion (points, from the entry bar's spot close, in the trade
direction) reached BEFORE (a) the premium -50 stop bar, (b) the +90 target
bar, (c) the leg's exit. Question: does spot progress exist where premium
progress does not (May pathology, lesson 18)? Incidence only — no candidate
total computed. Nifty ONLY."""
import csv, sys
from pathlib import Path
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
assert round(sum(r["net"] for r in res), 2) == 92437.75
key2leg = {(l["date"], l["direction"]): l for l in C3L}

print("date dir net reason | spot excursion (pts, directional) before stop-bar / before exit")
armable = 0
for r in sorted(res, key=lambda x: x["date"]):
    l = key2leg[(r["date"], r["direction"])]
    sb = spot.get(r["date"], [])
    sgn = 1.0 if r["direction"] == "CE" else -1.0
    entry_spot_close = [b[4] for b in sb if b[0] == l["entry_time"]]
    if not entry_spot_close: continue
    esc = entry_spot_close[0]
    window = [b for b in sb if l["entry_time"] <= b[0] <= r["exit_time"]]
    # directional spot extreme: CE uses highs, PE uses lows
    ext = max((sgn * ((b[2] if sgn > 0 else b[3]) - esc)) for b in window) if window else 0.0
    tag = ""
    if r["exit_reason"] == "stop" and ext >= 75: tag = " <-- stop leg, spot ran +75 first?"; armable += 1
    if r["date"][5:7] in ("05", "08") or tag:
        print(r["date"], r["direction"], r["net"], r["exit_reason"], "| max spot dir excursion in window:", round(ext, 1), tag)
print("\nstop legs whose spot excursion in window >= +75 pts:", armable)
# NOTE: window includes the exit bar itself; the frozen rule (if any) arms on
# bars strictly before the stop executes within the same bar ordering as BE50.
