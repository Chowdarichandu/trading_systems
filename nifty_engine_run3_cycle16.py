#!/usr/bin/env python3
"""RUN 3 Cycle 1 (engine Cycle 16) — CH3-R: opening-window confirmation on the
EXP0 incumbent. Confirmed legs (nsrc>=2) taken only if entry_time <= 09:55;
solo-(lA) unchanged; EXP0 retained; geometry BE50 + lock75 + TGT2-180.
Frozen in nifty_engine_frozen.md before scoring (2026-11-02).
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE.
Controls in same run: self-validation must reproduce the EXP0 best book
(+98001.00, 59 legs, 0 NC); timing audit; +30-min placebo; halves; month
table; ex-top-3; independent re-sum."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, controls, timing_audit

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65

def replay_best(cs, entry_time, delay_bars=0):
    """Best-book geometry: stop -50, BE50 arm, tgt1 +90, lock +75, tgt2 +180,
    stop before target on every bar incl. entry bar, square-off 15:10."""
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > "15:10": return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > "15:10": break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= target:
            stop2, target2 = entry + 75.0, entry + 180.0
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > "15:10": break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == "15:10": return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= 50.0:
            cur_stop = max(cur_stop, entry)
        if t == "15:10":
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_best(legs, delay_bars=0):
    res, nc = [], 0
    for l in legs:
        cs = A.candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs: nc += 1; continue
        r = replay_best(cs, l["entry_time"], delay_bars=delay_bars)
        if r is None: nc += 1; continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"]})
    return res, nc

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]

# self-validation: reproduce the incumbent exactly
chk, nc_chk = score_best(EXP0)
ctot = round(sum(r["net"] for r in chk), 2)
print("incumbent check:", len(chk), ctot, "NC", nc_chk, "expect 59 / 98001.0 / 0")
assert len(chk) == 59 and ctot == 98001.0 and nc_chk == 0

# candidate: CH3-R leg filter on the EXP0 book
CH3 = [l for l in EXP0 if nsrc(l) == 1 or l["entry_time"] <= "09:55"]
dropped = [l for l in EXP0 if nsrc(l) >= 2 and l["entry_time"] > "09:55"]
base_by_key = {(r["date"], r["direction"]): r for r in chk}
dropped_detail = [dict(date=l["date"], dir=l["direction"], entry_time=l["entry_time"],
                       rep=l["rep"], base_net=base_by_key[(l["date"], l["direction"])]["net"])
                  for l in dropped]

res, nc = score_best(CH3)
pl, _ = score_best(CH3, delay_bars=6)  # placebo: same legs, entry +30 min
c = controls("run3_cycle16_ch3r", CH3, res, nc, pl)
c["timing_audit"] = timing_audit(CH3)
c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
c["dropped_legs"] = dropped_detail
c["dropped_sum"] = round(sum(d["base_net"] for d in dropped_detail), 2)
print(json.dumps(c, indent=1, default=str))
Path(TR / "nifty_engine_run3_cycle16_summary.json").write_text(json.dumps(c, indent=1, default=str))
