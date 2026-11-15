#!/usr/bin/env python3
"""Session diagnosis #4 on book v11: <400 target2 curve points +270/+300,
and the trailing-15 state-window challenger flip census. Diagnosis only."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
from aggressive_score import candles
from bank_engine_run2 import book_v4_legs, score_all
from bank_engine_run2_cycle16 import runner_replay
from bank_engine_session_harness import build as hbuild

legs = book_v4_legs()
legs_by_key = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
v11, _, _ = hbuild(delay=0, lt400_tgt2=240.0, ge400_lock=90.0)
assert len(v11) == 82 and abs(sum(r["net"] for r in v11) - 91146.5) < 0.005
print("v11 sanity OK")

for t2 in (270.0, 300.0):
    tot, reach, fall = 0.0, 0, 0
    for r in v11:
        if r["entry"] < 400.0 and r["exit_reason"] in ("runner_target180", "runner_stop"):
            l = legs_by_key[r["leg_key"]]
            cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
            v = runner_replay(cs, l["entry_time"], delay=0, lock_pts=75.0, target2_pts=t2)
            if v is not None and abs(v["net"] - r["net"]) > 0.005:
                tot += v["net"] - r["net"]
                if v["net"] > r["net"]: reach += 1
                else: fall += 1
    print(f"<400 tgt2 {t2:.0f}: delta={tot:+.2f} (reach {reach}, fall back {fall})")

# trailing-15 window: rebuild state decisions on the v4 signal stream
scored, _ = score_all(legs, delay=0)
stream = sorted(scored.values(), key=lambda x: (x["date"], x["entry_time"]))
def state_w(stream, row, w):
    known = []
    for s in stream:
        if s["leg_key"] == row["leg_key"]: break
        if s["date"] < row["date"] or (s["date"] == row["date"] and s["exit_time"] <= row["entry_time"]):
            known.append(s)
    last = known[-w:]
    return len(last), round(sum(x["net"] for x in last), 2)
flips_skip, flips_warm = [], []
taken_keys = {(r["date"], r["direction"], r["entry_time"]) for r in v11}
for row in stream:
    n10, net10 = state_w(stream, row, 10)
    n15, net15 = state_w(stream, row, 15)
    cold10 = n10 >= 10 and net10 < 0
    cold15 = n15 >= 10 and net15 < 0
    if row["rep"] == "(lA) v2" and cold10 != cold15:
        flips_skip.append((row["date"], "skip@10" if cold10 else "take@10", "skip@15" if cold15 else "take@15", row["net"]))
    # warm flips matter for taken >=400 legs
    if row["leg_key"] in taken_keys:
        from bank_engine_cycle import _entry_premium
        ep = _entry_premium(legs_by_key[row["leg_key"]])
        if ep is not None and ep >= 400.0:
            warm10 = (n10 < 10) or (net10 >= 0)
            warm15 = (n15 < 10) or (net15 >= 0)
            if warm10 != warm15:
                flips_warm.append((row["date"], row["direction"], ep, "warm@10" if warm10 else "cold@10", "warm@15" if warm15 else "cold@15"))
print(f"\nW15 challenger census: (lA)-skip flips={len(flips_skip)} {flips_skip}")
print(f"W15 challenger census: >=400 warm/cold flips on taken legs={len(flips_warm)} {flips_warm}")
