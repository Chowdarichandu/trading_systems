#!/usr/bin/env python3
"""ROUND 5 WS1 diagnosis (Cycle 101 record): August causal rescan on the
CAUSAL book. Features are certified causal (as-of time in the report):
TRUE prior-day return, overnight gap, pre-entry morning range/move,
entry premium, DTE, prior-day bias state. Method (frozen): a separator
exists only if a band / PE-conjunction contains ALL causal August legs,
is net-negative book-wide and contains no winning leg. Diagnosis only —
no candidate is scored here."""
import sys, json
from pathlib import Path
from collections import defaultdict
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from nifty_engine_r5_harness import score_r5
from nifty_engine_r5_ws0 import causal_legs
from nifty_engine_r4_harness import spot5m, DAILY, PREV, pdret_prior

TR = Path.home() / "workspace/trading"

def features(leg, entry_premium):
    d = leg["date"]
    p = PREV.get(d)
    day = DAILY[d]; prev = DAILY[p]
    gap = (day["o"] / prev["c"] - 1) * 100
    rng = prev["h"] - prev["l"]
    bias_pos = (prev["c"] - prev["l"]) / rng * 100 if rng else 50.0
    bias = "bearish" if bias_pos < 35 else "bullish" if bias_pos >= 80 else "neutral"
    bars = [b for b in spot5m().get(d, []) if b[0] < leg["entry_time"]]
    if bars:
        mrange = (max(b[2] for b in bars) - min(b[3] for b in bars)) / prev["c"] * 100
        mmove = (bars[-1][4] / day["o"] - 1) * 100
    else:
        mrange, mmove = None, None
    from datetime import date as _d
    y, m, dd = map(int, d.split("-")); ey, em, ed = map(int, leg["expiry"].split("-"))
    dte = (_d(ey, em, ed) - _d(y, m, dd)).days
    return dict(pdret_prior=pdret_prior(d), gap=round(gap, 3), mrange=round(mrange, 3) if mrange is not None else None,
                mmove=round(mmove, 3) if mmove is not None else None, premium=entry_premium,
                dte=dte, bias=bias, bias_pos=round(bias_pos, 1))

if __name__ == "__main__":
    legs = causal_legs()
    res, nc, _ = score_r5(legs)
    assert nc == 0
    rows = []
    for l, r in zip(sorted(legs, key=lambda x: (x["date"], x["entry_time"])),
                    sorted(res, key=lambda x: (x["date"], x["entry_time"]))):
        assert l["date"] == r["date"] and l["entry_time"] == r["entry_time"]
        f = features(l, r["entry"])
        rows.append(dict(date=l["date"], direction=l["direction"], entry_time=l["entry_time"],
                         rep=l["rep"], net=r["net"], ft=r["ft"], **f))
    aug = [r for r in rows if r["date"].startswith("2026-08")]
    print("CAUSAL AUGUST legs:")
    for r in aug: print(" ", r)
    print("\nAll causal legs (date dir net | pdret gap mrange mmove prem dte bias):")
    for r in rows:
        print(f"  {r['date']} {r['direction']} {r['net']:+9.2f} | {r['pdret_prior']} {r['gap']} {r['mrange']} {r['mmove']} {r['premium']} {r['dte']} {r['bias']}")
    # ---- band scan: bands anchored on the August legs' feature values ----
    feats = ["pdret_prior", "gap", "mrange", "mmove", "premium", "dte"]
    print("\nBAND SCAN (sets containing ALL causal August legs):")
    found = []
    for f in feats:
        vals = sorted(r[f] for r in rows if r[f] is not None)
        lo = min(r[f] for r in aug); hi = max(r[f] for r in aug)
        # candidate bands: [lo,hi] widened to each pair of observed values spanning it
        cands = set()
        for a in vals:
            for b in vals:
                if a <= lo and b >= hi and a <= b: cands.add((a, b))
        for (a, b) in sorted(cands):
            for conj in (False, True):
                s = [r for r in rows if r[f] is not None and a <= r[f] <= b and (not conj or r["direction"] == "PE")]
                if not all(x in s for x in aug): continue
                net = round(sum(r["net"] for r in s), 2)
                wins = sum(1 for r in s if r["net"] > 0)
                tag = "PE & " if conj else ""
                print(f"  {tag}{f} in [{a}, {b}]: {len(s)} legs, net {net:+,.2f}, winners {wins}")
                if net < 0 and wins == 0 and len(s) >= len(aug):
                    found.append((tag + f, a, b, len(s), net))
    # bias conjunction
    for bstate in ("bearish", "neutral", "bullish"):
        s = [r for r in rows if r["bias"] == bstate]
        if all(x in s for x in aug):
            print(f"  bias == {bstate}: {len(s)} legs, net {sum(r['net'] for r in s):+,.2f}, winners {sum(1 for r in s if r['net'] > 0)}")
        s = [r for r in rows if r["bias"] == bstate and r["direction"] == "PE"]
        if all(x in s for x in aug):
            print(f"  PE & bias == {bstate}: {len(s)} legs, net {sum(r['net'] for r in s):+,.2f}, winners {sum(1 for r in s if r['net'] > 0)}")
    print("\nSEPARATORS (negative, winner-free, contain all August legs):", found)
    Path(TR / "nifty_engine_r5_ws1_diag.json").write_text(json.dumps(
        {"legs": rows, "august": aug, "separators": found}, indent=1, default=str))
