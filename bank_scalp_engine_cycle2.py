#!/usr/bin/env python3
"""Cycle 2 — F4 PV1: premium-velocity trigger. Frozen in log before run."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_core as C

TGT, STP, CAP, SPACING, VEL = 12.0, 9.0, 4, 10, 10.0

def main():
    spot = C.load_spot(); trades, sig_ends, nc, capped = [], [], 0, 0
    for day in C.days():
        sp = spot[day]; exp = C.exp_for(day)
        taken, last_entry = 0, -10**9
        for t in range(15, 341):
            if taken >= CAP: break
            if (t + 1) - last_entry < SPACING: continue
            sc, sc2 = sp["c"][t], sp["c"][t-2]
            if not (np.isfinite(sc) and np.isfinite(sc2)): continue
            strike = C.atm(sc)
            fired = None
            for typ, agree in (("CE", sc > sc2), ("PE", sc < sc2)):
                bars = C.opt_day(exp, strike, typ, day)
                if bars is None: continue
                pc, pc2 = bars["c"][t], bars["c"][t-2]
                if np.isfinite(pc) and np.isfinite(pc2) and (pc - pc2) >= VEL and agree:
                    fired = typ; break
            if fired is None: continue
            tr = C.score_signal(day, t + 1, fired, TGT, STP)
            if tr is None: nc += 1; continue
            tr["mech"] = "PV1"; trades.append(tr); sig_ends.append(t + 1)
            taken += 1; last_entry = t + 1
    resum = C.write_trades(trades, "/home/hatch/workspace/trading/bank_scalp_engine_cycle2_trades.csv")
    s = C.summarise(trades, sig_ends, TGT, STP, "PV1")
    s.update({"not_computed": nc, "capped_out": capped, "resum_inr": resum,
              "resum_match": bool(abs(resum - s["total_inr"]) < 0.01)})
    print(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
