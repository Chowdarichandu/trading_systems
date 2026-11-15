#!/usr/bin/env python3
"""ROUND 8 stage 3: WS3 Cycle 147 (afternoon-range sleeve) + WS4 closure
(Cycle 148 closure re-gate vs the ROUND-OPEN baseline; Cycle 149
candidate freeze verification — the Round-7 C139/C140 pattern; used
because fewer than 2 workstreams banked). Freeze: ROUND 8 section,
nifty_engine_frozen.md."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
from nifty_engine_r8_stage1 import save_state, load_state, fetch_missing

TR = Path.home() / "workspace/trading"
ROUND_OPEN = {"total": 54102.00, "ft_pct": 34.3, "per_week": 0.86,
              "months": {"2026-01": 17096.75, "2026-02": 12789.25, "2026-03": 7895.00,
                         "2026-04": 210.00, "2026-05": -10410.00, "2026-06": -3910.00,
                         "2026-07": 10998.75, "2026-08": -1701.00, "2026-09": 4652.75,
                         "2026-10": 16480.50}}

def main():
    standing, label = load_state()
    print(f"gate baseline: {label} = {R6.CURRENT['total']:+,.2f}")

    # ---------- Cycle 147: WS3 afternoon-range sleeve ----------
    skeys = R7.keys_of(standing)
    sleeve, excluded = R8.afternoon_legs(skeys)
    print(f"\n[r8_c147_ws3_afternoon] sleeve legs {len(sleeve)}, excluded {len(excluded)}")
    for e in excluded: print(f"  excluded: {e}")
    fetch_missing(sleeve, weekly=False)
    combined = standing + sleeve
    c147, res147 = R7.run_r7("r8_c147_ws3_afternoon", combined)
    banked147 = c147.get("gate_relative", {}).get("banked", False)
    tot, _ = R7.score_sleeve_alone("afternoon sleeve", sleeve)
    print(f"  sleeve standalone {tot:+,.2f} over {len(sleeve)} legs; "
          f"{'BANKED' if banked147 else 'not banked'}")
    if banked147:
        standing = combined
        save_state(standing, c147, "standing after r8_c147_ws3_afternoon")

    # ---------- WS4: combinations / closure ----------
    bankings = ["r8_c147_ws3_afternoon"] if banked147 else []
    print(f"\nWS4: Round-8 bankings = {bankings if bankings else 'none'} "
          f"-> combinations close by statement (freeze rule: fewer than 2).")

    # Cycle 148: closure re-gate of the ending standing book vs ROUND-OPEN baseline
    R6.CURRENT.update(total=ROUND_OPEN["total"], ft_pct=ROUND_OPEN["ft_pct"],
                      per_week=ROUND_OPEN["per_week"], label="Round-8 open baseline",
                      months=ROUND_OPEN["months"])
    c148, _ = R7.run_r7("r8_c148_ws4_closure", standing)
    # Cycle 149: candidate freeze verification (full controls, ungated print)
    c149, _ = R7.run_r7("r8_c149_candidate_freeze_verify", standing, gate=False)
    ok = (c149["total"] == c148["total"] and c149["not_computed"] == 0 and c149["resum_ok"]
          and c149["timing_audit"]["violations"] == 0)
    print(f"\nCYCLE 149 FREEZE VERIFICATION: {'VALID' if ok else 'MISMATCH'} — "
          f"standing book {c149['total']:+,.2f}, n {c149['n']}, FT {c149['ft_pct']}%, "
          f"{c149['per_week']}/wk, audit {c149['timing_audit']['checked']}/"
          f"{c149['timing_audit']['violations']}, NC {c149['not_computed']}, resum {c149['resum_ok']}")

if __name__ == "__main__":
    main()
