#!/usr/bin/env python3
"""Session diagnosis #2 on book v8: (1) runner value by premium sub-band;
(2) exact replay of the no-progress time-stop family (diagnosis grid).
Premiums, lot 30, cost Rs220. Diagnosis only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_run2_cycle14 import be_replay
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_run2_cycle20 import build as build20

LOT, COST = 30.0, 220.0
v8, nc, legs_by_key = build20(delay=0, fast_t2=180.0)
assert len(v8) == 82 and abs(sum(r["net"] for r in v8) - 77196.5) < 0.005
states = anchored_states(delay=0)

def seg(r):
    n, net = states.get(r["leg_key"], (0, 0.0))
    warm = (n < 10) or (net >= 0)
    if r["entry"] < 400.0: return "<400"
    return ">=400warm" if warm else ">=400cold"

def g0(r):
    l = legs_by_key[r["leg_key"]]
    cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    return be_replay(cs, l["entry_time"], delay=0, arm=False)

# (1) runner value by premium sub-band (v8 net minus G0 net, runner legs only)
from collections import defaultdict
bands = defaultdict(lambda: [0, 0.0])
for r in v8:
    s = seg(r)
    if s in ("<400", ">=400warm"):
        g = g0(r)
        band = "<250" if r["entry"] < 250 else ("[250,400)" if r["entry"] < 400 else
               ("[550,750)" if r["entry"] < 750 else ("[750,1000)" if r["entry"] < 1000 else ">=1000")))
        bands[(s, band)][0] += 1
        bands[(s, band)][1] += round(r["net"] - g["net"], 2)
print("Runner value vs G0 by segment x premium sub-band:")
for k in sorted(bands): print(f"    {k}: n={bands[k][0]} value={bands[k][1]:+.2f}")

# (2) time-stop replay: exit at close of bar index (horizon_bars-1) if the leg
# is still open, has not touched +90, and its MFE over bars [0..horizon-1] < prog.
def timestop_replay(r, horizon_bars, prog):
    l = legs_by_key[r["leg_key"]]
    cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= r["entry_time"]]
    if not idxs: return None
    bars = cs[idxs[0]:]
    entry = bars[0][1]
    stop = entry - 50.0
    win = bars[:horizon_bars]
    # stop can fire inside the window before the time-stop bar's close
    for b in win[:-1]:
        if b[0] > "15:10": break
        if b[3] <= stop: return None  # already resolved by stop -> v8 row stands
        if b[2] >= entry + 90.0: return None  # triggered -> runner owns it
    last = win[-1]
    if last[3] <= stop or last[2] >= entry + 90.0: return None
    mfe = max(b[2] for b in win) - entry
    if mfe >= prog: return None
    return round((last[4] - entry) * LOT - COST, 2)

print("\nTime-stop diagnosis grid (delta vs v8 total, all 82 legs):")
for hb, prog in ((3, 40.0), (3, 25.0), (4, 40.0), (4, 25.0), (2, 40.0)):
    tot_delta, changed = 0.0, []
    for r in v8:
        v = timestop_replay(r, hb, prog)
        if v is not None:
            changed.append((r["date"], r["direction"], r["exit_reason"], r["net"], v, round(v - r["net"], 2)))
            tot_delta += v - r["net"]
    print(f"  horizon={hb} bars prog=+{prog:.0f}: changed={len(changed)} delta={tot_delta:+.2f}")
    if (hb, prog) == (3, 40.0):
        for c in changed: print("     ", c)
