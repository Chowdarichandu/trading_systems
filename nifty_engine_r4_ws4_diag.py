#!/usr/bin/env python3
"""ROUND 4 WS4 diagnosis — day-state features + tercile nets on the
current candidate book (frozen method, Round-4 WS4). Diagnosis only;
the boundaries + chosen terciles are frozen in frozen.md before the
WS4 cycles score."""
import sys, json, statistics
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r4_harness import (candidate_legs, score_r4, DAILY, DORDER,
                                     DIDX, PREV, spot5m)

S5 = spot5m()
print("spot_5m coverage:", min(S5), "->", max(S5), "| days:", len(S5))

def range30(d):
    sb = S5.get(d)
    if not sb: return None
    bars = [b for b in sb if "09:15" <= b[0] < "09:45"]
    if len(bars) < 6: return None
    pc = DAILY[PREV[d]]["c"]
    return (max(b[2] for b in bars) - min(b[3] for b in bars)) / pc * 100

def dailyrange(d):
    r = DAILY[d]
    return (r["h"] - r["l"]) / r["c"] * 100

def prior_vals(d, fn, n=20):
    i = DIDX[d]; out = []
    for k in range(i - 1, max(-1, i - 1 - 3 * n), -1):
        v = fn(DORDER[k])
        if v is not None: out.append(v)
        if len(out) >= n: break
    return out

def features(d):
    sb = S5.get(d, [])
    day_open = sb[0][1] if sb else DAILY[d]["o"]
    gap = (day_open / DAILY[PREV[d]]["c"] - 1) * 100
    r30 = range30(d)
    med30 = prior_vals(d, range30)
    ratio30 = r30 / statistics.median(med30) if (r30 is not None and len(med30) >= 10) else None
    pd = PREV[d]
    pdr = dailyrange(pd)
    medp = prior_vals(pd, dailyrange)
    pdr_ratio = pdr / statistics.median(medp) if len(medp) >= 10 else None
    return dict(gap_pct=round(gap, 4), ratio30=round(ratio30, 4) if ratio30 else None,
                pdr_ratio=round(pdr_ratio, 4) if pdr_ratio else None,
                n_med30=len(med30))

legs = candidate_legs()
res, nc, _ = score_r4(legs)
rows = []
for r in res:
    f = features(r["date"])
    rows.append(dict(date=r["date"], direction=r["direction"], net=r["net"], **f))
for r in rows: print(json.dumps(r))

out = {}
for k in ("gap_pct", "ratio30", "pdr_ratio"):
    have = sorted([r for r in rows if r[k] is not None], key=lambda x: x[k])
    missing = [r["date"] for r in rows if r[k] is None]
    b1 = have[14][k]; b2 = have[29][k]
    terc = {"low": [r for r in have if r[k] <= b1],
            "mid": [r for r in have if b1 < r[k] <= b2],
            "high": [r for r in have if r[k] > b2]}
    out[k] = dict(b1=b1, b2=b2, missing=missing,
                  nets={t: round(sum(r["net"] for r in v), 2) for t, v in terc.items()},
                  counts={t: len(v) for t, v in terc.items()},
                  members={t: [r["date"] for r in v] for t, v in terc.items()})
    print(f"\n{k}: b1={b1} b2={b2} missing={missing}")
    for t in ("low", "mid", "high"):
        print(f"  {t}: {out[k]['counts'][t]} legs net {out[k]['nets'][t]:+,.2f}")
Path("nifty_engine_r4_ws4_diag.json").write_text(json.dumps(out, indent=1))
print("\nwrote nifty_engine_r4_ws4_diag.json")
