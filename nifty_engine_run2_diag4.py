#!/usr/bin/env python3
"""RUN 2 diagnosis 4 — spot impulse ACCELERATION into entry, weekday state,
and premium paid per spot point of directional move. All causal (pre-entry
bars only). Nifty ONLY."""
import csv, sys
from pathlib import Path
from collections import defaultdict
from datetime import date as ddate
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score

TR = Path.home() / "workspace/trading"
spot = {}
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day, tm = r["timestamp"][:10], r["timestamp"][11:16]
        spot.setdefault(day, []).append((tm, float(r["open"]), float(r["close"])))
for d in spot: spot[d].sort()

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
tot = round(sum(r["net"] for r in res), 2)
print("best book check:", len(res), tot, "NC", nc)
assert tot == 92437.75
key2leg = {(l["date"], l["direction"]): l for l in C3L}

def t2m(t): return int(t[:2]) * 60 + int(t[3:5])

rows = []
for r in res:
    l = key2leg[(r["date"], r["direction"])]
    bars = spot.get(r["date"], [])
    pre = [b for b in bars if b[0] < l["entry_time"]]
    if len(pre) < 4: continue
    sgn = 1.0 if r["direction"] == "CE" else -1.0
    em = t2m(l["entry_time"])
    ref = pre[-1][2]
    def close_at(mins_ago):
        cand = [b for b in pre if t2m(b[0]) <= em - mins_ago]
        return cand[-1][2] if cand else pre[0][1]
    m_recent = sgn * (ref - close_at(30))     # signed spot move, last ~30 min
    m_prior = sgn * (close_at(30) - close_at(60))  # signed move, prior ~30 min
    move_pts = sgn * (ref - bars[0][1])
    rows.append(dict(date=r["date"], net=r["net"], m_recent=m_recent, m_prior=m_prior,
                     move_pts=move_pts, entry_prem=r["entry"],
                     wd=ddate.fromisoformat(r["date"]).strftime("%a")))

def split(name, fn):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for x in rows:
        k = fn(x); g[k][0] += 1; g[k][1] += x["net"]
        if x["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += x["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    for k in sorted(gw, key=str): print(" WEAK", k, gw[k][0], round(gw[k][1], 2))

split("impulse acceleration (recent30 vs prior30, signed pts)",
      lambda x: "ACCEL" if x["m_recent"] > x["m_prior"] else "DECEL")
split("recent30 impulse sign", lambda x: "RECENT_WITH" if x["m_recent"] > 0 else "RECENT_AGAINST/FLAT")
split("weekday", lambda x: x["wd"])
split("premium per spot point moved (entry_prem/move_pts)",
      lambda x: "NO_MOVE" if x["move_pts"] <= 20 else ("CHEAP<0.8" if x["entry_prem"] / x["move_pts"] < 0.8 else ("MID 0.8-1.5" if x["entry_prem"] / x["move_pts"] <= 1.5 else "RICH>1.5")))
print("\nrows used:", len(rows), "of 63")
