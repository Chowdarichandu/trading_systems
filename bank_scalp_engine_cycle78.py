#!/usr/bin/env python3
"""Cycles 7-8 — Charter: trailing-stop variants (act +8, trail 5, stop -9)."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_charter as H

SPEC = ("T", 8.0, 5.0, 9.0)
if __name__ == "__main__":
    out = {}
    for label, fn in (("OR1-TRAIL", H.or_signals_1m), ("OR3-TRAIL", H.or_signals_3m),
                      ("LR1-TRAIL", H.lr_signals_1m), ("LR3-TRAIL", H.lr_signals_3m)):
        out[label] = H.run_variant(label, fn, SPEC)
        s = out[label]
        print(f"{label}: n={s['trades']} total={s['total_inr']} gross={s['gross_inr']} "
              f"H1={s['h1_inr']} H2={s['h2_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
              f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} audit={s['audit_violations']}", flush=True)
    json.dump(out, open("/home/hatch/workspace/trading/bank_scalp_engine_cycle78_summary.json", "w"), indent=1)
