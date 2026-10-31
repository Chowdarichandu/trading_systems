#!/usr/bin/env python3
"""RUN 2 diagnosis 8 — entry-bar premium microstructure (never examined):
(a) premium gap at entry = entry bar open - previous bar close of the same
contract (chasing vs discount); (b) premium realised range of the 3 bars
before entry (premium volatility state); (c) entry premium vs the contract's
pre-entry premium VWAP (premium-side, on the CURRENT EXP0 book). Causal.
Nifty ONLY."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, score

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
C3L = [l for l in C3L if l["date"] != l["expiry"]]  # EXP0 book
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
tot = round(sum(r["net"] for r in res), 2)
print("EXP0 book check:", len(res), tot, "NC", nc, "expect 59 / 98001.0 / 0")
assert tot == 98001.0
key2leg = {(l["date"], l["direction"]): l for l in C3L}

rows = []
for r in res:
    l = key2leg[(r["date"], r["direction"])]
    cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    idx = [i for i, b in enumerate(cs) if b[0] == l["entry_time"]]
    if not idx: continue
    i0 = idx[0]
    entry_open = cs[i0][1]
    prev_close = cs[i0-1][4] if i0 >= 1 else entry_open
    gap = entry_open - prev_close
    pre3 = cs[max(0, i0-3):i0]
    rng = (max(b[2] for b in pre3) - min(b[3] for b in pre3)) if pre3 else 0.0
    pre = cs[:i0]
    vols = sum(b[5] for b in pre)
    vwap = (sum(((b[2]+b[3]+b[4])/3.0)*b[5] for b in pre)/vols) if vols > 0 else (sum(b[4] for b in pre)/len(pre) if pre else entry_open)
    rows.append(dict(date=r["date"], net=r["net"], gap=gap, rng=rng, vdist=entry_open - vwap))

def split(name, fn):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for x in rows:
        k = fn(x); g[k][0] += 1; g[k][1] += x["net"]
        if x["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += x["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    for k in sorted(gw, key=str): print(" WEAK", k, gw[k][0], round(gw[k][1], 2))

split("premium gap at entry (pts)", lambda x: "CHASE>=+15" if x["gap"] >= 15 else ("DISCOUNT<=-10" if x["gap"] <= -10 else "FLAT -10..+15"))
split("pre-entry premium range 3 bars (pts)", lambda x: "PVOL_HI>=60" if x["rng"] >= 60 else ("PVOL_MID 30-60" if x["rng"] >= 30 else "PVOL_LO<30"))
split("entry premium vs contract VWAP (pts)", lambda x: "ABOVE>=+20" if x["vdist"] >= 20 else ("BELOW<=-20" if x["vdist"] <= -20 else "NEAR -20..+20"))
print("\nrows:", len(rows))
