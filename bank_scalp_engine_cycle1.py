#!/usr/bin/env python3
"""Cycle 1 — F1 OR1: 1-min opening-range micro-burst. Frozen in log before run."""
import sys, json
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_core as C

TGT, STP, CAP, SPACING = 12.0, 9.0, 4, 10

def signals(day, spot):
    o, h, l, c = spot["o"], spot["h"], spot["l"], spot["c"]
    orh, orl = np.nanmax(h[:15]), np.nanmin(l[:15])
    out = []
    for i in range(15, 256):
        if not (np.isfinite(c[i]) and np.isfinite(c[i-1])): continue
        if c[i] > orh and c[i-1] <= orh: out.append((i, "CE"))
        elif c[i] < orl and c[i-1] >= orl: out.append((i, "PE"))
    return out

def main():
    spot = C.load_spot(); trades, sig_ends, nc, capped = [], [], 0, 0
    for day in C.days():
        taken, last_entry = 0, -10**9
        for i, direction in signals(day, spot[day]):
            if taken >= CAP or (i + 1) - last_entry < SPACING:
                capped += 1; continue
            t = C.score_signal(day, i + 1, direction, TGT, STP)
            if t is None: nc += 1; continue
            t["mech"] = "OR1"
            trades.append(t); sig_ends.append(i + 1)
            taken += 1; last_entry = i + 1
    resum = C.write_trades(trades, "/home/hatch/workspace/trading/bank_scalp_engine_cycle1_trades.csv")
    s = C.summarise(trades, sig_ends, TGT, STP, "OR1")
    s.update({"not_computed": nc, "capped_out": capped, "resum_inr": resum,
              "resum_match": bool(abs(resum - s["total_inr"]) < 0.01)})
    print(json.dumps(s, indent=1))

if __name__ == "__main__":
    main()
