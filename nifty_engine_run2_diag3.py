#!/usr/bin/env python3
"""RUN 2 diagnosis 3 — confirmation COMPOSITION and contested-day state.
(a) nets by source-count and by which systems are in the source set (esp.
(lA) participation); (b) contested day: an opposite-direction pool leg with
entry_time <= this leg's entry_time (causal at entry); (c) entry-bar option
volume vs mean pre-entry bar volume of the same contract. Nifty ONLY."""
import sys
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, score

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
tot = round(sum(r["net"] for r in res), 2)
print("best book check:", len(res), tot, "NC", nc)
assert tot == 92437.75
key2leg = {(l["date"], l["direction"]): l for l in C3L}
res_sorted = sorted(res, key=lambda x: (x["date"], x["entry_time"]))

def split(name, fn, weak=True):
    g = defaultdict(lambda: [0, 0.0]); gw = defaultdict(lambda: [0, 0.0])
    for r in res_sorted:
        l = key2leg[(r["date"], r["direction"])]
        k = fn(r, l)
        g[k][0] += 1; g[k][1] += r["net"]
        if r["date"][5:7] in ("05", "08"): gw[k][0] += 1; gw[k][1] += r["net"]
    print(f"\n== {name} ==")
    for k in sorted(g, key=str): print(" ALL", k, g[k][0], round(g[k][1], 2))
    if weak:
        for k in sorted(gw, key=str): print(" WEAK(May+Aug)", k, gw[k][0], round(gw[k][1], 2))

split("source count", lambda r, l: f"nsrc={nsrc(l)}" if nsrc(l) > 1 else "solo-(lA)")
split("(lA) in source set", lambda r, l: "LA_IN" if "(lA) v2" in l["sources"] else "LA_OUT")
for sysname in ("Skill V3", "V5 v2", "Volrix"):
    split(f"{sysname} in source set", lambda r, l, s=sysname: "IN" if s in l["sources"] else "OUT")

pool_by_day = defaultdict(list)
for l in B: pool_by_day[l["date"]].append(l)
def contested(r, l):
    opp = [p for p in pool_by_day[r["date"]] if p["direction"] != r["direction"] and p["entry_time"] <= l["entry_time"]]
    return "CONTESTED_BEFORE" if opp else "CLEAN"
split("opposite pool leg fired at/before entry", contested)

def vol_bucket(r, l):
    cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    if not cs: return "NC"
    pre = [b for b in cs if b[0] < l["entry_time"]]
    cur = [b for b in cs if b[0] == l["entry_time"]]
    if not pre or not cur: return "NOPRE"
    meanv = sum(b[5] for b in pre) / len(pre)
    if meanv <= 0: return "ZEROVOL"
    ratio = cur[0][5] / meanv
    return "VOL_HI>=2" if ratio >= 2 else ("VOL_MID 1-2" if ratio >= 1 else "VOL_LO<1")
split("entry-bar option volume ratio", vol_bucket)
