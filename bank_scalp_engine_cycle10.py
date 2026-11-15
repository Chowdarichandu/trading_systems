#!/usr/bin/env python3
"""Cycle 10 — OR1-TRAIL-T4: trail distance 4 (act +8, stop -9). Frozen in log."""
import sys, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import bank_scalp_engine_charter as H

if __name__ == "__main__":
    s = H.run_variant("OR1-TRAILT4", H.or_signals_1m, ("T", 8.0, 4.0, 9.0))
    print(f"OR1-TRAILT4: n={s['trades']} total={s['total_inr']} gross={s['gross_inr']} "
          f"H1={s['h1_inr']} H2={s['h2_inr']} WR={s['win_rate']} DG={s['days_green_pct']} "
          f"lag={s['lag_placebo_inr']} rand={s['random_placebo']['mean']} audit={s['audit_violations']}", flush=True)
    json.dump(s, open("/home/hatch/workspace/trading/bank_scalp_engine_cycle10_summary.json", "w"), indent=1)
