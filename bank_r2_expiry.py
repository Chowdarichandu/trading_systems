#!/usr/bin/env python3
"""ROUND 2: expiry-day cells.
C37 (Family 3c): expiry-day legs (date == expiry) re-scored at 100 ITM under
working-book (v15) exits; all other legs unchanged.
C39 (Family 4b): expiry-day legs get special geometry regardless of
segment/state: plain G0 (-50/+90); (-40/+90); (-50/+75).
Fixed v15 stream; full controls per cell vs v15."""
import sys, json, copy
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import build_fixed, controls, full_run, rescore_keys, seg_of
from bank_r2_ns1 import V15
from bank_engine_run2 import book_v4_legs
from bank_engine_run2_cycle14 import stream_keys
from bank_engine_run2_cycle18 import anchored_states
from bank_engine_cycle import _entry_premium
from aggressive_score import candles
from bank_r2_core import gen_replay

legs = book_v4_legs()
LBK = {(l["date"], l["direction"], l["entry_time"]): l for l in legs}
KEYS = {0: stream_keys(delay=0), 6: stream_keys(delay=6)}
STATES = {0: anchored_states(delay=0), 6: anchored_states(delay=6)}

def build_itm(delay):
    lbk2 = {}
    for k, l in LBK.items():
        l2 = dict(l)
        if l2["date"] == l2["expiry"]:
            l2["strike"] = l2["strike"] + (-100 if l2["direction"] == "CE" else 100)
        lbk2[k] = l2
    rows, nc = rescore_keys(KEYS[delay], lbk2, STATES[delay], V15, delay=delay)
    return rows, nc, lbk2

def build_geo(geo, delay):
    out, nc = [], 0
    for key in KEYS[delay]:
        l = LBK[key]
        ep = _entry_premium(l)
        seg = seg_of(ep, *STATES[delay].get(key, (0, 0.0)))
        if l["date"] == l["expiry"]:
            p = dict(stop=geo[0], trig=geo[1], lock=None, tgt2=None)
        else:
            p = V15[seg]
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = gen_replay(cs, l["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        out.append({**r, "date": l["date"], "direction": l["direction"],
                    "family": l["family"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "leg_key": key, "segment": seg})
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc, LBK

if __name__ == "__main__":
    ref_rows, ref_nc, ref_lbk = build_fixed(V15, delay=0)
    ref_prows, ref_pnc, _ = build_fixed(V15, delay=6)
    REF = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
    assert REF["net"] == 105167.00
    out = {}
    c, rows = full_run(build_itm, REF, cycle_name="r2c37_expiry_itm")
    out["r2c37_expiry_itm"] = {k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw",
                                                "halves", "months", "ex_top3_total", "not_computed",
                                                "gate_pass", "gate_failed_legs")}
    out["r2c37_expiry_itm"]["placebo_net"] = c["placebo"]["net"]
    base = {(r["date"], r["direction"], r["entry_time"]): r["net"] for r in ref_rows}
    out["r2c37_expiry_itm"]["leg_deltas"] = [
        (r["date"], r["direction"], base[(r["date"], r["direction"], r["entry_time"])], r["net"])
        for r in rows if abs(r["net"] - base[(r["date"], r["direction"], r["entry_time"])]) > 0.005]
    print(f"r2c37_expiry_itm: n={c['n']} net={c['net']} ft90={c['ft90_pct']} pl={c['placebo']['net']} "
          f"PASS={c['gate_pass']} fail={c['gate_failed_legs'][:3]}")
    print("  expiry leg deltas (ATM net -> ITM net):", out["r2c37_expiry_itm"]["leg_deltas"])
    for name, geo in (("r2c39_exp_plain", (50.0, 90.0)), ("r2c39_exp_s40", (40.0, 90.0)),
                      ("r2c39_exp_t75", (50.0, 75.0))):
        c, _ = full_run(lambda d, g=geo: build_geo(g, d), REF, cycle_name=name)
        out[name] = {k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw",
                                       "halves", "months", "ex_top3_total", "not_computed",
                                       "gate_pass", "gate_failed_legs")}
        out[name]["placebo_net"] = c["placebo"]["net"]
        print(f"{name}: geo={geo} n={c['n']} net={c['net']} ft90={c['ft90_pct']} pl={c['placebo']['net']} "
              f"PASS={c['gate_pass']} fail={c['gate_failed_legs'][:3]}")
    json.dump(out, open("/home/hatch/workspace/trading/bank_r2_expiry_results.json", "w"), indent=1)
    print("saved bank_r2_expiry_results.json")
