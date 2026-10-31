#!/usr/bin/env python3
"""RUN 2 diagnosis — pre-entry SPOT-state variables for the 63 best-book legs.
All variables computed only from spot bars strictly before the entry bar
(causal). No candidate frozen here. Nifty ONLY, premiums (leg nets from the
banked geometry), 1 lot 65, cost 220, UNIQUE-ONCE."""
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
        spot.setdefault(day, []).append((tm, float(r["open"]), float(r["high"]),
                                         float(r["low"]), float(r["close"]), float(r.get("volume") or 0)))
for d in spot: spot[d].sort()
days_sorted = sorted(spot)

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
geom = dict(stop_pts=50.0, tgt1=90.0, lock_pts=75.0, tgt2=180.0, be_arm=50.0)
res, nc = score(C3L, geom)
tot = round(sum(r["net"] for r in res), 2)
print("best book check:", len(res), tot, "NC", nc, "expect 63 / 92437.75 / 0")
assert len(res) == 63 and tot == 92437.75 and nc == 0
key2leg = {(l["date"], l["direction"]): l for l in C3L}

rows = []
for r in res:
    l = key2leg[(r["date"], r["direction"])]
    day = r["date"]; bars = spot.get(day, [])
    pre = [b for b in bars if b[0] < l["entry_time"]]
    if not pre: print("NO PRE BARS", day); continue
    dopen = bars[0][1]
    sgn = 1.0 if l["direction"] == "CE" else -1.0
    ref = pre[-1][4]  # spot close of last bar before entry
    # intraday spot VWAP up to pre-entry (typical price * volume; fall back to close mean if vol=0)
    vols = sum(b[5] for b in pre)
    if vols > 0:
        vwap = sum(((b[2]+b[3]+b[4])/3.0) * b[5] for b in pre) / vols
    else:
        vwap = sum(b[4] for b in pre) / len(pre)
    hi = max(b[2] for b in pre); lo = min(b[3] for b in pre)
    pctile = (ref - lo) / (hi - lo) if hi > lo else 0.5
    # previous trading day
    i = days_sorted.index(day)
    prev = spot[days_sorted[i-1]] if i > 0 else []
    prev_ret = (prev[-1][4] - prev[0][1]) / prev[0][1] * 100 if prev else None
    gap = (dopen - prev[-1][4]) / prev[-1][4] * 100 if prev else None
    rows.append(dict(date=day, dir=l["direction"], t=l["entry_time"], net=r["net"],
                     reason=r["exit_reason"], ft=r["ft"],
                     prevdir_aligned=(prev_ret is not None and sgn * prev_ret > 0),
                     prev_ret=prev_ret, gap_dir=sgn * gap if gap is not None else None,
                     vwap_aligned=(sgn * (ref - vwap) > 0), vwap_dist_pct=sgn * (ref - vwap) / ref * 100,
                     pctile_dir=pctile if l["direction"] == "CE" else 1 - pctile,
                     move_dir_pct=sgn * (ref - dopen) / dopen * 100))

def split(name, keyfn, subsets=("ALL", "08", "05")):
    print(f"\n== {name} ==")
    for sub in subsets:
        rr = rows if sub == "ALL" else [x for x in rows if x["date"][5:7] == sub]
        groups = defaultdict(lambda: [0, 0.0])
        for x in rr:
            g = keyfn(x); groups[g][0] += 1; groups[g][1] += x["net"]
        print(f" [{sub}] " + " | ".join(f"{k}: n={v[0]} net={round(v[1],2)}" for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))))

split("prev-day direction alignment", lambda x: "PREV_ALIGNED" if x["prevdir_aligned"] else "PREV_AGAINST")
split("overnight gap in direction", lambda x: "GAP_WITH" if x["gap_dir"] > 0.05 else ("GAP_AGAINST" if x["gap_dir"] < -0.05 else "GAP_FLAT"))
split("spot vs intraday VWAP", lambda x: "VWAP_ALIGNED" if x["vwap_aligned"] else "VWAP_AGAINST")
split("directional range percentile", lambda x: "TOP_TERCILE" if x["pctile_dir"] > 2/3 else ("BOT_TERCILE" if x["pctile_dir"] < 1/3 else "MID_TERCILE"))
split("signed move from open at entry (%)", lambda x: ">=0.30" if x["move_dir_pct"] >= 0.30 else ("0.15-0.30" if x["move_dir_pct"] >= 0.15 else "<0.15"))

print("\n== August + May legs detail ==")
for x in sorted(rows, key=lambda x: x["date"]):
    if x["date"][5:7] in ("08", "05"):
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in x.items()})
