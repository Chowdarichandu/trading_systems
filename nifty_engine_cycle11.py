#!/usr/bin/env python3
"""Cycle 11 challenger CH4 — RATCHET150: runner stop +75 -> +130 for subsequent
bars once a runner-phase bar high >= entry+150. Nifty ONLY, premiums, 1 lot 65,
cost 220, UNIQUE-ONCE. Controls in same run. Self-contained replay; validated
by reproducing the best book (+92437.75) with the ratchet disabled."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, controls, timing_audit

COST, LOT = 220.0, 65

def replay_ratchet(cs, entry_time, ratchet=True, delay_bars=0):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def out(pts, reason, t, ft, px):
        return dict(net=round(pts * LOT - COST, 2), exit_reason=reason, exit_time=t, ft=ft, entry=entry, exit=px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= cur_stop:
            return out(cur_stop - entry, "be_stop" if cur_stop == entry else "stop", t, 0, cur_stop)
        if h >= target:
            stop2 = entry + 75.0; target2 = entry + 180.0
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2:
                    return out(stop2 - entry, "runner_stop_ratchet" if stop2 > entry + 75.0 else "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(180.0, "runner_target", t2, 1, target2)
                if ratchet and h2 - entry >= 150.0: stop2 = max(stop2, entry + 130.0)
                if t2 == "15:10": return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= 50.0: cur_stop = max(cur_stop, entry)  # BE50 arm, subsequent bars
        if t == "15:10": return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_r(legs, ratchet, delay_bars=0):
    res, nc = [], 0
    for l in legs:
        cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs: nc += 1; continue
        r = replay_ratchet(cs, l["entry_time"], ratchet=ratchet, delay_bars=delay_bars)
        if r is None: nc += 1; continue
        r = {**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"], "entry_time": l["entry_time"], "sources": l["sources"]}
        res.append(r)
    return res, nc

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
# validation: ratchet off must reproduce best book exactly
base, nc0 = score_r(C3L, ratchet=False)
base_total = round(sum(r["net"] for r in base), 2)
print("validation ratchet-off:", len(base), base_total, "NC", nc0, "expect 63 / 92437.75 / 0")
assert len(base) == 63 and base_total == 92437.75 and nc0 == 0, "REPLAY INVALID"

res, nc = score_r(C3L, ratchet=True)
pl, _ = score_r(C3L, ratchet=True, delay_bars=6)
c = controls("cycle11_ratchet150", C3L, res, nc, pl)
c["timing_audit"] = timing_audit(C3L)
key = lambda x: (x["date"], x["direction"])
changed = [(b["date"], b["direction"], b["net"], r["net"], r["exit_reason"]) for b, r in zip(sorted(base, key=key), sorted(res, key=key)) if b["net"] != r["net"]]
c["changed_legs"] = changed
print(json.dumps(c, indent=1, default=str))
Path.home().joinpath("workspace/trading/nifty_engine_cycle11_summary.json").write_text(json.dumps(c, indent=1, default=str))
