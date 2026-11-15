#!/usr/bin/env python3
"""Cycle 4 — Charter: OR micro-burst 3-min x target ladder."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_charter as H

if __name__ == "__main__":
    out = {}
    for tgt in (2.5, 10.0, 12.0, 15.0, 20.0):
        label = f"OR3-T{str(tgt).replace('.','p')}"
        out[label] = H.run_variant(label, H.or_signals_3m, ("F", tgt, 9.0))
        s = out[label]
        print(f"{label}: n={s['trades']} total={s['total_inr']} gross={s['gross_inr']} "
              f"H1={s['h1_inr']} H2={s['h2_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
              f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} audit={s['audit_violations']}", flush=True)
    json.dump(out, open("/home/hatch/workspace/trading/bank_scalp_engine_cycle4_summary.json", "w"), indent=1)
