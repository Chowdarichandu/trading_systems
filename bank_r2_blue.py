#!/usr/bin/env python3
"""ROUND 2 Cycle 40 (Family 4c): Blue-Line wide-candle rejection (setup3)
legs as a STANDALONE add-on family on book v16. Admission (frozen): setup_type
contains 'setup3'; (date, direction) unused by the book's pool; entry premium
outside [400,550); premium series present in the Blue-Line option_5m.csv.
Exits = v16 assembly (segment by entry premium; >=400 uses the anchored state
at the leg's entry on the book stream; expiry-day legs plain). Cycle 15
scored setup3 only inside the pooled Blue-Line mix on book v6 - standalone
on the current book is a different cell. Full controls vs v16, add-on timing
audit incl. entry >= signal_time and entry-premium cross-check vs the log."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import controls, gate, gen_replay, seg_of, write_trades
from bank_r2_ns1 import V15
from bank_r2_expiry import build_geo
from bank_engine_run2 import book_v4_legs, score_all, trailing_state
from bank_engine_run2_cycle15 import blue_legs, opt_candles
from aggressive_score import EXPIRIES

USED = {(l["date"], l["direction"]) for l in book_v4_legs()}

def addon_rows(delay):
    stream_scored, _ = score_all(book_v4_legs(), delay=delay)
    stream = sorted(stream_scored.values(), key=lambda x: (x["date"], x["entry_time"]))
    out, nc, viol, admitted = [], 0, [], []
    for bl in blue_legs():
        if "setup3" not in (bl["setup"] or ""): continue
        if (bl["date"], bl["direction"]) in USED: continue
        cs = opt_candles(bl["month"], bl["strike"], bl["direction"], bl["date"])
        if not cs: nc += 1; continue
        bars = [b for b in cs if b[0] == bl["entry_time"]]
        if not bars: nc += 1; continue
        ep = bars[0][1]
        if 400.0 <= ep < 550.0: continue
        if bl["entry_time"] < bl["signal_time"]:
            viol.append((bl["date"], bl["entry_time"], "entry before signal"))
        if bl["log_entry_premium"] is not None and abs(bl["log_entry_premium"] - ep) > 0.51:
            viol.append((bl["date"], bl["entry_time"], "entry premium vs log mismatch"))
        pseudo = {"date": bl["date"], "entry_time": bl["entry_time"],
                  "leg_key": (bl["date"], bl["direction"], bl["entry_time"])}
        n, tnet, _ = trailing_state(stream, pseudo)
        seg = seg_of(ep, n, tnet)
        expiry = next(e for e in EXPIRIES if e >= bl["date"])
        if bl["date"] == expiry:
            p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
        else:
            p = V15[seg]
        r = gen_replay(cs, bl["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        admitted.append((bl["date"], bl["direction"], bl["entry_time"], ep, r["net"]))
        out.append({**r, "date": bl["date"], "direction": bl["direction"],
                    "family": "BlueLine_v4", "rep": "BlueLine v4 " + (bl["setup"] or ""),
                    "entry_time": bl["entry_time"], "leg_key": pseudo["leg_key"],
                    "segment": seg})
    return out, nc, viol, admitted

if __name__ == "__main__":
    ref_rows, ref_nc, ref_lbk = build_geo((50.0, 90.0), 0)
    ref_prows, ref_pnc, _ = build_geo((50.0, 90.0), 6)
    REF = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
    assert REF["net"] == 106517.00, REF["net"]
    a0, nc0, viol0, admitted = addon_rows(0)
    a6, nc6, _, _ = addon_rows(6)
    print(f"setup3 add-ons admitted: {len(a0)} (delay-0) | nc={nc0} | audit violations: {viol0}")
    for a in admitted: print("   ", a)
    rows = sorted(ref_rows + a0, key=lambda x: (x["date"], x["entry_time"]))
    prows = sorted(ref_prows + a6, key=lambda x: (x["date"], x["entry_time"]))
    c = controls(rows, nc0, ref_lbk, prows, nc6)
    c["timing_violations"] = c["timing_violations"] + viol0
    resum = write_trades(rows, "bank_engine_r2c40_setup3_trades.csv")
    c["independent_resum"] = resum
    ok, failed = gate(c, REF, resum=resum)
    if viol0: ok, failed = False, failed + [f"addon audit violations {viol0}"]
    c["gate_pass"], c["gate_failed_legs"] = ok, failed
    print(f"COMBINED: n={c['n']} net={c['net']} ft90={c['ft90_pct']} pw={c['per_week_raw']} "
          f"pl={c['placebo']['net']} ex3={c['ex_top3_total']} halves={c['halves']} "
          f"PASS={ok} fail={failed[:4]}")
    json.dump({k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw", "halves",
                                 "months", "ex_top3_total", "not_computed", "gate_pass",
                                 "gate_failed_legs")} | {"placebo_net": c["placebo"]["net"],
                                 "addons": admitted},
              open("/home/hatch/workspace/trading/bank_r2_blue_results.json", "w"), indent=1)
    print("saved bank_r2_blue_results.json")
