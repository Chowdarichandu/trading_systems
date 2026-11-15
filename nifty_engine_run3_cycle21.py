#!/usr/bin/env python3
"""RUN 3 Cycle 6 (engine Cycle 21) — SQ1525: square-off at the 15:25 bar
close instead of 15:10, both phases. Frozen in nifty_engine_frozen.md
before scoring (2026-11-02). Exact-tag candle loading; best-book
geometry otherwise (stop -50, BE50 arm, tgt1 +90, lock +75, tgt2 +180,
stop before target). Controls in same run: incumbent re-validation,
timing audit, +30-min placebo, halves, month table, ex-top-3, re-sum.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, controls

TR = Path.home() / "workspace/trading"
DIRS = A.DIRS
COST, LOT = 220.0, 65

def candles_exact(sym, strike, typ, day, exp):
    tag = f"{sym}_{int(strike)}{typ}_{day}_{exp}"
    for d in DIRS:
        for name in (f"candles_{tag}.json", f"candles_premium_{tag}.json"):
            p = d / name
            if p.exists():
                try:
                    data = json.loads(p.read_text()).get("data", {}).get("candles", [])
                except Exception:
                    continue
                rows = [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4]),
                         float(c[5]) if len(c) > 5 else 0.0)
                        for c in sorted(data, key=lambda c: c[0]) if c[0][:10] == day]
                if rows: return rows
    return None

def replay_sq(cs, entry_time, sq_time="15:10", delay_bars=0):
    if not cs: return None
    idxs = [i for i, b in enumerate(cs) if b[0] >= entry_time]
    if not idxs: return None
    i0 = idxs[0] + delay_bars
    if i0 >= len(cs): return None
    bars = cs[i0:]
    if bars[0][0] > sq_time: return None
    entry = bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    def out(net_pts, reason, t, ft, exit_px):
        return dict(net=round(net_pts * LOT - COST, 2), exit_reason=reason,
                    exit_time=t, ft=ft, entry=entry, exit=exit_px)
    cur_stop = stop
    for i, b in enumerate(bars):
        t, o, h, l, cl, v = b
        if t > sq_time: break
        if l <= cur_stop:
            rsn = "be_stop" if cur_stop == entry else "stop"
            return out(cur_stop - entry, rsn, t, 0, cur_stop)
        if h >= target:
            stop2, target2 = entry + 75.0, entry + 180.0
            for b2 in bars[i + 1:]:
                t2, o2, h2, l2, cl2, v2 = b2
                if t2 > sq_time: break
                if l2 <= stop2: return out(stop2 - entry, "runner_stop", t2, 1, stop2)
                if h2 >= target2: return out(target2 - entry, "runner_target", t2, 1, target2)
                if t2 == sq_time: return out(cl2 - entry, "runner_square_off", t2, 1, cl2)
            lb = bars[-1]
            return out(lb[4] - entry, "runner_square_off", lb[0], 1, lb[4])
        if (h - entry) >= 50.0:
            cur_stop = max(cur_stop, entry)
        if t == sq_time:
            return out(cl - entry, "square_off", t, 0, cl)
    lb = bars[-1]
    return out(lb[4] - entry, "square_off", lb[0], 0, lb[4])

def score_sq(legs, sq_time="15:10", delay_bars=0):
    res, nc = [], 0
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs: nc += 1; continue
        r = replay_sq(cs, l["entry_time"], sq_time=sq_time, delay_bars=delay_bars)
        if r is None: nc += 1; continue
        res.append({**r, "date": l["date"], "direction": l["direction"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "sources": l["sources"]})
    return res, nc

def audit_exact(legs):
    bad = checked = 0
    for l in legs:
        cs = candles_exact(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        if not cs or not any(b[0] == l["entry_time"] for b in cs): bad += 1
        else: checked += 1
    return {"checked": checked, "violations": bad}

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]

chk, nc_chk = score_sq(EXP0, sq_time="15:10")
ctot = round(sum(r["net"] for r in chk), 2)
print("incumbent check (sq 15:10):", len(chk), ctot, "NC", nc_chk, "expect 59 / 98001.0 / 0")
assert len(chk) == 59 and ctot == 98001.0 and nc_chk == 0
base_by_key = {(r["date"], r["direction"]): r for r in chk}

# how many legs are even open at 15:10 (affected population)
open_at_1510 = [r for r in chk if r["exit_reason"] in ("square_off", "runner_square_off")]
print("legs open at 15:10 in incumbent:", len(open_at_1510),
      "| their net:", round(sum(r["net"] for r in open_at_1510), 2))

res, nc = score_sq(EXP0, sq_time="15:25")
pl, _ = score_sq(EXP0, sq_time="15:25", delay_bars=6)
c = controls("run3_cycle21_sq1525", EXP0, res, nc, pl)
c["timing_audit"] = audit_exact(EXP0)
c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
c["changed_legs"] = [dict(date=r["date"], dir=r["direction"],
                          base_net=base_by_key[(r["date"], r["direction"])]["net"],
                          base_reason=base_by_key[(r["date"], r["direction"])]["exit_reason"],
                          cand_net=r["net"], cand_reason=r["exit_reason"])
                     for r in res if base_by_key[(r["date"], r["direction"])]["net"] != r["net"]]
print(json.dumps(c, indent=1, default=str))
Path(TR / "nifty_engine_run3_cycle21_summary.json").write_text(json.dumps(c, indent=1, default=str))
