#!/usr/bin/env python3
"""RUN 2 diagnosis 6 — (a) moneyness offset at entry: signed spot-minus-strike
in the trade direction (ATM nearest-100 rounding leaves -50..+50 of natural
variation, never examined); (b) previous-day |return| volatility state;
(c) expiry-day (DTE=0) legs alone. Causal. Nifty ONLY."""
import csv, sys
from pathlib import Path
from collections import defaultdict
from datetime import date as ddate
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_score import pool, nsrc, score

TR = Path.home() / "workspace/trading"
spot = {}
entry_spot = {}
entry_time_map = {}
for r in csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv")):
    entry_time_map[(r["date"], r["direction"])] = r["entry_time"]
    if r["entry_spot"]:
        entry_spot[(r["date"], r["direction"])] = float(r["entry_spot"])
spot_t = {}
for d in ("nifty_janjun", "nifty_julsep", "nifty_october"):
    for r in csv.DictReader(open(TR / d / "data" / "NIFTY_spot_5m.csv")):
        day = r["timestamp"][:10]
        spot.setdefault(day, []).append((float(r["open"]), float(r["close"])))
        spot_t.setdefault(day, []).append((r["timestamp"][11:16], float(r["open"])))
for k, t in entry_time_map.items():
    if k not in entry_spot:
        bars = dict(spot_t.get(k[0], []))
        entry_spot[k] = bars[t]  # spot open of the entry bar (scorer's fallback source)
days_sorted = sorted(spot)

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
assert round(sum(r["net"] for r in res), 2) == 92437.75
key2leg = {(l["date"], l["direction"]): l for l in C3L}

def split(name, fn):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for r in res:
        k = fn(r); g[k][0] += 1; g[k][1] += r["net"]
        if r["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += r["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    for k in sorted(gw, key=str): print(" WEAK", k, gw[k][0], round(gw[k][1], 2))

def offset(r):
    l = key2leg[(r["date"], r["direction"])]
    sgn = 1.0 if r["direction"] == "CE" else -1.0
    fav = sgn * (entry_spot[(r["date"], r["direction"])] - l["strike"])
    return "FAV>=+25" if fav >= 25 else ("AGAINST<=-25" if fav <= -25 else "MID -25..+25")
split("moneyness offset (directional spot-strike)", offset)

def prevvol(r):
    i = days_sorted.index(r["date"])
    if i == 0: return "NOPREV"
    prev = spot[days_sorted[i-1]]
    pr = abs((prev[-1][1] - prev[0][0]) / prev[0][0] * 100)
    return "PREVVOL_HI>=0.8" if pr >= 0.8 else ("PREVVOL_MID 0.4-0.8" if pr >= 0.4 else "PREVVOL_LO<0.4")
split("previous-day |return| %", prevvol)

def dte0(r):
    l = key2leg[(r["date"], r["direction"])]
    d = (ddate.fromisoformat(l["expiry"]) - ddate.fromisoformat(r["date"])).days
    return "DTE0" if d == 0 else "DTE>0"
split("expiry day", dte0)
