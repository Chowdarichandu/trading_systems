#!/usr/bin/env python3
"""Session diagnosis #3 on book v10: curve completions and state variants.
Premiums, lot 30. Diagnosis only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_run2 import book_v4_legs, score_all, trailing_state
from bank_engine_run2_cycle14 import be_replay
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_session_harness import build as hbuild

legs = book_v4_legs()
legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
v10, _, _ = hbuild(delay=0, lt400_tgt2=210.0, ge400_lock=90.0)
assert len(v10) == 82 and abs(sum(r["net"] for r in v10) - 84846.5) < 0.005
states = anchored_states(delay=0)

def seg(r):
    n, net = states.get(r["leg_key"], (0, 0.0))
    warm = (n < 10) or (net >= 0)
    return "<400" if r["entry"] < 400 else (">=400warm" if warm else ">=400cold")

def replay(r, kind, **kw):
    l = legs_by_key[r["leg_key"]]
    cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
    return be_replay(cs, l["entry_time"], delay=0, arm=False) if kind == "g0" else \
        runner_replay(cs, l["entry_time"], delay=0, **kw)

def delta(label, pred, kind, **kw):
    tot, ch = 0.0, []
    for r in v10:
        if pred(r):
            v = replay(r, kind, **kw)
            if v is not None and abs(v["net"] - r["net"]) > 0.005:
                ch.append((r["date"], r["direction"], r["net"], v["net"], round(v["net"] - r["net"], 2)))
                tot += v["net"] - r["net"]
    print(f"{label}: changed={len(ch)} delta={tot:+.2f}")
    for c in ch: print("   ", c)

# 1. <400 TGT2 +240 (curve completion above banked +210)
delta("1. <400 tgt2 240 (lock75)", lambda r: seg(r) == "<400", "runner", lock_pts=75.0, target2_pts=240.0)
# 3. <400 lock +90 at tgt2 210 (interaction re-measure; C17 rejected lock90 at tgt2 180)
delta("3. <400 lock90 (tgt2 210)", lambda r: seg(r) == "<400", "runner", lock_pts=90.0, target2_pts=210.0)
# 4. >=400 cold legs given the runner (lock90/tgt2 180)
delta("4. >=400cold -> runner lock90/180", lambda r: seg(r) == ">=400cold", "runner", lock_pts=90.0, target2_pts=180.0)
# 8. skipped (lA) legs: their states and v4-stream outcomes (deep-cold variant check)
scored, _ = score_all(legs, delay=0)
stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
print("\n8. (lA) legs and their anchored states (v4 stream):")
for row in stream:
    if row["rep"] == "(lA) v2":
        n, net, _ = trailing_state(stream, row)
        taken = row["leg_key"] in {(r["date"], r["direction"], r["entry_time"]) for r in v10}
        print(f"    {row['date']} n_known={n} state={net:+.2f} v4net={row['net']:+.2f} taken_in_v10={taken}")
