#!/usr/bin/env python3
"""ROUND 8 stage 2: WS2 Cycle 146 — expiry sleeve on its own geometry.
First validates the rebuilt sleeve against the Round-7 Cycle-138 record
under standing geometry (freeze requirement), then gates the mixed book
(standing legs at standing geometry + sleeve legs at expiry geometry)
under BOTH FT readings. Freeze: ROUND 8 section, nifty_engine_frozen.md."""
import sys, json
from pathlib import Path
sys.path.insert(0, str(Path.home() / "workspace/trading"))
import nifty_engine_r7_harness as R7
import nifty_engine_r6_harness as R6
import nifty_engine_r8_harness as R8
from nifty_engine_r8_stage1 import save_state, load_state, fetch_missing

TR = Path.home() / "workspace/trading"

def main():
    standing, label = load_state()
    print(f"gate baseline: {label} = {R6.CURRENT['total']:+,.2f}")
    skeys = R7.keys_of(standing)
    sleeve, excluded = R8.expiry_sleeve_legs(skeys)
    print(f"expiry sleeve rebuilt: {len(sleeve)} legs; excluded {len(excluded)}: {excluded}")
    for l in sleeve:
        print(f"  {l['date']} {l['direction']} entry {l['entry_time']} strike {l['strike']} exp {l['expiry']}")
    fetch_missing(sleeve, weekly=True)

    # --- freeze-required validation vs Round-7 Cycle 138 (standing geometry) ---
    cv, _ = R7.run_r7("r8_c146_ws2_rebuild_validate", standing + sleeve, gate=False)
    tot, _ = R7.score_sleeve_alone("rebuilt expiry sleeve", sleeve)
    ok = (cv["total"] == 57753.75 and cv["n"] == 50 and cv["ft_pct"] == 32.0 and tot == 3651.75)
    print("CYCLE 146 REBUILD VALIDATION vs C138:", "VALID" if ok else "MISMATCH — cycle does not score")
    if not ok: sys.exit(1)

    # --- Cycle 146: mixed geometry, gated under the FT90 reading ---
    spec = [(l, "standing") for l in standing] + [(l, "expiry") for l in sleeve]
    c, res = R8.run_r8_mixed("r8_c146_ws2_expiry_own_geom", spec)
    banked = c.get("gate_relative_FT90_reading", {}).get("banked", False)
    print(f"  sleeve legs under expiry geometry: "
          f"{round(sum(r['net'] for r in res if r['kind'] == 'expiry'), 2):+,.2f} over "
          f"{sum(1 for r in res if r['kind'] == 'expiry')} legs; "
          f"their FT90 count {sum(r['ft'] for r in res if r['kind'] == 'expiry')}, "
          f"own-target FT count {sum(r['ft_own'] for r in res if r['kind'] == 'expiry')}")
    if banked:
        combined = standing + sleeve
        save_state(combined, c, "standing after r8_c146 (NOTE: sleeve legs at expiry geometry)")
        print("  BANKED under the FT90 reading — supersession (mixed-geometry book)")
    else:
        print("  not banked under the FT90 reading (the only banking basis); "
              "own-geometry form goes to the flagged list at round close")

if __name__ == "__main__":
    main()
