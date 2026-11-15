#!/usr/bin/env python3
"""ROUND 2 Cycle 38: Jun/Jul PE bleed pocket. Signature (frozen in
bank_engine_frozen.md after diagnosis, before scoring): PE leg with anchored
state cold. Variants: signature legs get plain (-50/+90) / (-60/+90) /
(-40/+90); all other legs keep the v16 assembly (v15 segments + expiry-day
plain override). Full controls vs v16."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
from bank_r2_core import controls, full_run, gen_replay, seg_of
from bank_r2_ns1 import V15
from bank_r2_expiry import LBK, KEYS, STATES
from bank_engine_cycle import _entry_premium
from aggressive_score import candles

def build(sig_geo, delay):
    out, nc = [], 0
    for key in KEYS[delay]:
        l = LBK[key]
        ep = _entry_premium(l)
        n, tnet = STATES[delay].get(key, (0, 0.0))
        seg = seg_of(ep, n, tnet)
        cold = n >= 10 and tnet < 0
        if l["date"] == l["expiry"]:
            p = dict(stop=50.0, trig=90.0, lock=None, tgt2=None)
        else:
            p = V15[seg]
        if sig_geo is not None and l["direction"] == "PE" and cold:
            p = dict(stop=sig_geo[0], trig=sig_geo[1], lock=None, tgt2=None)
        cs = candles(l["index"], l["strike"], l["direction"], l["date"], l["expiry"])
        r = gen_replay(cs, l["entry_time"], delay=delay, stop_pts=p["stop"],
                       trig_pts=p["trig"], lock_pts=p["lock"], tgt2_pts=p["tgt2"])
        if r is None: nc += 1; continue
        out.append({**r, "date": l["date"], "direction": l["direction"],
                    "family": l["family"], "rep": l["rep"],
                    "entry_time": l["entry_time"], "leg_key": key, "segment": seg})
    return sorted(out, key=lambda x: (x["date"], x["entry_time"])), nc, LBK

if __name__ == "__main__":
    ref_rows, ref_nc, ref_lbk = build(None, 0)
    ref_prows, ref_pnc, _ = build(None, 6)
    REF = controls(ref_rows, ref_nc, ref_lbk, ref_prows, ref_pnc)
    assert REF["net"] == 106517.00, REF["net"]
    print(f"REF v16 reproduced via bleed builder: {REF['net']}")
    out = {}
    for name, geo in (("r2c38_bleed_plain", (50.0, 90.0)), ("r2c38_bleed_s60", (60.0, 90.0)),
                      ("r2c38_bleed_s40", (40.0, 90.0))):
        c, _ = full_run(lambda d, g=geo: build(g, d), REF, cycle_name=name)
        out[name] = {k: c[k] for k in ("n", "net", "ft_pct", "ft90_pct", "per_week_raw",
                                       "halves", "months", "ex_top3_total", "not_computed",
                                       "gate_pass", "gate_failed_legs")}
        out[name]["placebo_net"] = c["placebo"]["net"]
        print(f"{name}: geo={geo} n={c['n']} net={c['net']} ft90={c['ft90_pct']} pl={c['placebo']['net']} "
              f"jun={c['months']['06']} jul={c['months']['07']} PASS={c['gate_pass']} fail={c['gate_failed_legs'][:3]}")
    json.dump(out, open("/home/hatch/workspace/trading/bank_r2_bleed_results.json", "w"), indent=1)
    print("saved bank_r2_bleed_results.json")
