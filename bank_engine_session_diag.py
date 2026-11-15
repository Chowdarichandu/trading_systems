#!/usr/bin/env python3
"""Session 2026-11-02 diagnosis on book v8 (BANKNIFTY ONLY, premiums, lot 30).
Exact per-leg deltas for the candidate mechanisms not yet scored on v8:
A runner-gate refinement (<250 -> G0); B TGT2+210 segment splits;
C lock+90 on >=400-warm; D >=400 runner value by state-strength band;
E stop-leg early-path stats (time-stop feasibility); F Jun/Jul state record.
Diagnosis only - no cycle is scored here."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_run2 import book_v4_legs
from bank_engine_run2_cycle14 import be_replay
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_run2_cycle20 import build as build20

TR = Path.home() / "workspace/trading"

v8, nc, legs_by_key = build20(delay=0, fast_t2=180.0)
tot = round(sum(r["net"] for r in v8), 2)
assert len(v8) == 82 and abs(tot - 77196.5) < 0.005, f"v8 sanity failed: {len(v8)} {tot}"
print(f"v8 sanity OK: 82 legs, +{tot}")
states = anchored_states(delay=0)

def seg(r):
    n, net = states.get(r["leg_key"], (0, 0.0))
    warm = (n < 10) or (net >= 0)
    if r["entry"] < 400.0: return "<400", warm, n, net
    return (">=400warm" if warm else ">=400cold"), warm, n, net

def replay(r, kind, **kw):
    l = legs_by_key[r["leg_key"]]
    cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    if kind == "g0":
        return be_replay(cs, l["entry_time"], delay=0, arm=False)
    return runner_replay(cs, l["entry_time"], delay=0, **kw)

# ---- A: <250 -> G0
dA = []
for r in v8:
    if r["entry"] < 250.0:
        g = replay(r, "g0")
        dA.append((r["date"], r["direction"], r["exit_reason"], r["net"], g["exit_reason"], g["net"], round(g["net"] - r["net"], 2)))
print(f"\nA. <250 legs -> G0: n={len(dA)} delta_total={round(sum(x[6] for x in dA),2):+.2f}")
for x in dA: print("   ", x)

# ---- B: TGT2 +210 segment splits
for label, pred in ((">=400warm", lambda s: s == ">=400warm"), ("<400", lambda s: s == "<400")):
    d = []
    for r in v8:
        s, *_ = seg(r)
        if pred(s) and r["exit_reason"] in ("runner_target180", "runner_stop", "runner_square_off"):
            v = replay(r, "runner", lock_pts=75.0, target2_pts=210.0)
            if abs(v["net"] - r["net"]) > 0.005:
                d.append((r["date"], r["direction"], r["net"], v["exit_reason"], v["net"], round(v["net"] - r["net"], 2)))
    print(f"\nB. TGT2+210 on {label}: changed={len(d)} delta_total={round(sum(x[5] for x in d),2):+.2f}")
    for x in d: print("   ", x)

# ---- C: lock +90 on >=400warm
d = []
for r in v8:
    s, *_ = seg(r)
    if s == ">=400warm" and r["exit_reason"] in ("runner_target180", "runner_stop", "runner_square_off"):
        v = replay(r, "runner", lock_pts=90.0, target2_pts=180.0)
        if abs(v["net"] - r["net"]) > 0.005:
            d.append((r["date"], r["direction"], r["net"], v["exit_reason"], v["net"], round(v["net"] - r["net"], 2)))
print(f"\nC. lock+90 on >=400warm: changed={len(d)} delta_total={round(sum(x[5] for x in d),2):+.2f}")
for x in d: print("   ", x)

# ---- D: >=400 runner value (v8 minus G0) by state-strength band
bands = {}
for r in v8:
    s, warm, n, net = seg(r)
    if s == ">=400warm":
        g = replay(r, "g0")
        band = "warmup(n<10)" if n < 10 else ("state [0,3000)" if net < 3000 else ("state [3000,8000)" if net < 8000 else "state >=8000"))
        b = bands.setdefault(band, [0, 0.0])
        b[0] += 1; b[1] += round(r["net"] - g["net"], 2)
print("\nD. >=400 warm runner value vs G0 by state band:")
for k in sorted(bands): print(f"    {k}: n={bands[k][0]} runner_value={bands[k][1]:+.2f}")

# ---- segment counts
from collections import Counter
print("\nSegments:", Counter(seg(r)[0] for r in v8))
print("Runner exits by direction:", Counter((r["direction"], r["exit_reason"]) for r in v8 if "runner" in r["exit_reason"]))

# ---- E: stop legs early path
print("\nE. v8 stop legs (n=36): close@+15min minus entry (pts), MFE first 3 bars (pts):")
vals = []
for r in v8:
    if r["exit_reason"] == "stop":
        l = legs_by_key[r["leg_key"]]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        idx = [i for i, b in enumerate(cs) if b[0] == r["entry_time"]][0]
        first3 = cs[idx:idx + 3]
        c15 = round(first3[-1][4] - r["entry"], 2)
        mfe = round(max(b[2] for b in first3) - r["entry"], 2)
        vals.append((r["date"], c15, mfe))
better = [v for v in vals if v[1] > -50]
print(f"    stop legs whose +15min close was above the -50 stop: {len(better)}/36; "
      f"sum of (close15 - (-50))*30 over those = {round(sum((v[1] + 50) * 30 for v in better), 2):+.2f} (gross saving if exited at that close, before counting legs that would have recovered)")
rec = [v for v in vals if v[2] >= 45]
print(f"    stop legs that had touched >= +45 within 3 bars (progress-then-died): {len(rec)}/36")

# ---- F: Jun/Jul legs with state
print("\nF. Jun/Jul v8 legs (state at entry):")
for r in v8:
    if r["date"][5:7] in ("06", "07"):
        s, warm, n, net = seg(r)
        print(f"    {r['date']} {r['direction']} {r['rep']} ep={r['entry']} seg={s} state_n={n} state_net={net} exit={r['exit_reason']} net={r['net']:+.2f}")
