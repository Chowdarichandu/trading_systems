#!/usr/bin/env python3
"""RUN 3 Cycles 2-3 (engine Cycles 17-18), frozen in nifty_engine_frozen.md
before scoring (2026-11-02):
- Cycle 17 C3L+EV5: EXP0 incumbent + the 5 fetched dropped solo non-Skill
  U1 legs (4 Volrix CE 09:20, 1 (lA) PE 2026-08-10).
- Cycle 18 S1-44: EXP0 incumbent + the 44 BASE_S1 NIFTY legs outside the
  N1 premium pool (candles completed 2026-11-02), EXP0 book-wide.
Geometry: BE50 + lock75 + TGT2-180 (the validated best-book replay).
Controls in same run per candidate: incumbent self-validation first,
timing audit, +30-min placebo, halves, month table, ex-top-3, re-sum.
Nifty ONLY, premiums, 1 lot 65, cost 220, UNIQUE-ONCE."""
import sys, csv, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import aggressive_score as A
from nifty_engine_score import pool, nsrc, controls, timing_audit

TR = Path.home() / "workspace/trading"
COST, LOT = 220.0, 65

def replay_best(cs, entry_time, delay_bars=0):
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

def run(name, legs, added_keys):
    res, nc = score_best(legs)
    pl, _ = score_best(legs, delay_bars=6)
    c = controls(name, legs, res, nc, pl)
    c["timing_audit"] = timing_audit(legs)
    c["august"] = c["month_table"].get("2026-08", [0, 0])[0]
    c["may"] = c["month_table"].get("2026-05", [0, 0])[0]
    added = [r for r in res if (r["date"], r["direction"]) in added_keys]
    c["added_legs"] = [dict(date=r["date"], dir=r["direction"], entry_time=r["entry_time"],
                            rep=r["rep"], entry=r["entry"], exit_reason=r["exit_reason"],
                            net=r["net"]) for r in added]
    c["added_sum"] = round(sum(r["net"] for r in added), 2)
    c["added_n"] = len(added)
    print(json.dumps(c, indent=1, default=str))
    Path(TR / f"nifty_engine_{name}_summary.json").write_text(json.dumps(c, indent=1, default=str))
    return c

B = pool()
C3L = [l for l in B if nsrc(l) >= 2 or (nsrc(l) == 1 and l["rep"] == "(lA) v2")]
EXP0 = [l for l in C3L if l["date"] != l["expiry"]]

chk, nc_chk = score_best(EXP0)
ctot = round(sum(r["net"] for r in chk), 2)
print("incumbent check:", len(chk), ctot, "NC", nc_chk, "expect 59 / 98001.0 / 0")
assert len(chk) == 59 and ctot == 98001.0 and nc_chk == 0

def mkleg(date, direction, entry_time, strike, expiry, rep):
    return dict(date=date, index="NIFTY", direction=direction, entry_time=entry_time,
                strike=strike, expiry=expiry, lot=65, rep=rep, sources=rep, family="ADD")

# ---- Cycle 17: EV5 ----
EV5 = [mkleg("2026-01-09", "CE", "09:20", 25900, "2026-01-27", "Volrix (b)"),
       mkleg("2026-05-12", "CE", "09:20", 23700, "2026-05-26", "Volrix (b)"),
       mkleg("2026-06-01", "CE", "09:20", 23600, "2026-06-30", "Volrix (b)"),
       mkleg("2026-09-16", "CE", "09:20", 23200, "2026-09-29", "Volrix (b)"),
       mkleg("2026-08-10", "PE", "09:45", 24500, "2026-08-25", "(lA) v2")]
ev_keys = {(l["date"], l["direction"]) for l in EV5}
assert not (ev_keys & {(l["date"], l["direction"]) for l in EXP0})
run("run3_cycle17_ev5", EXP0 + EV5, ev_keys)

# ---- Cycle 18: S1-44 ----
n1keys = {(r["date"], r["direction"]) for r in csv.DictReader(open(TR / "historical_proof_nifty_N1_trades.csv"))}
S1 = []
for r in csv.DictReader(open(TR / "index_options_newsetup_base_s1_trades_jan_oct_2026.csv")):
    if r["index"] != "NIFTY" or (r["date"], r["direction"]) in n1keys: continue
    strike = int(round(float(r["entry_spot"]) / 100.0) * 100)
    expiry = next(e for e in A.EXPIRIES if e >= r["date"])
    S1.append(mkleg(r["date"], r["direction"], r["entry_time"], strike, expiry, "BASE_S1"))
print("S1 legs assembled:", len(S1))
s1_all_keys = {(l["date"], l["direction"]) for l in S1}
S1_kept = [l for l in S1 if l["date"] != l["expiry"]]  # EXP0 book-wide
print("S1 legs after EXP0:", len(S1_kept), "| dropped by EXP0:", len(S1) - len(S1_kept))
s1_keys = {(l["date"], l["direction"]) for l in S1_kept}
assert not (s1_keys & {(l["date"], l["direction"]) for l in EXP0})
run("run3_cycle18_s144", EXP0 + S1_kept, s1_keys)
