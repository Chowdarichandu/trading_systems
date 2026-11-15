#!/usr/bin/env python3
"""V3 CYCLE 17 DIAG — candidate COUNTS ONLY (no P&L read) for the
P2F-MIDBAND-R1 challenger: results reactions with |reaction_ret| in
[1.5%, 2.0%), followed at R+1 (P2F machinery, score_lag lag=1).
Anchors: the >=2.5% candidate sets must match the build's recorded
counts (2026: 39); the [2.0,2.5) 2026 candidate count must match
SAT-32's recorded 9. Counts by year and by month of the ENTRY day
(entry day = R+1 trading day, from the daily series — dates only)."""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, WS

g, LABELS = boot()
print("BUILD CONTROLS ALL PASS in this pass")
rc, STOCKS_E = g["reaction_candidates"], g["STOCKS_E"]
CAL = {"2025": (g["CAL25"], g["LO25"], g["HI25"]),
       "2026": (g["CAL26"], g["LO26"], g["HI26"])}

out = {}
for yr, (cal, lo, hi) in CAL.items():
    cands = rc(cal, lo, hi)
    bands = {"ge25": [c for c in cands if abs(c["reaction_ret_pct"]) >= 2.5],
             "b2025": [c for c in cands if 2.0 <= abs(c["reaction_ret_pct"]) < 2.5],
             "b1512": [c for c in cands if 1.5 <= abs(c["reaction_ret_pct"]) < 2.0],
             "b1015": [c for c in cands if 1.0 <= abs(c["reaction_ret_pct"]) < 1.5]}
    months = {}
    for c in bands["b1512"]:
        daily = STOCKS_E[c["symbol"]][1]
        entry_day = daily[c["ri"] + 2]["date"] if c["ri"] + 2 < len(daily) else None
        # lag-1 entry day is ri+1 for the trade; ri+2 shown is R+2 -- use ri+1:
        entry_day = daily[c["ri"] + 1]["date"]
        months[entry_day[:7]] = months.get(entry_day[:7], 0) + 1
    out[yr] = {"total_candidates": len(cands),
               "counts": {k: len(v) for k, v in bands.items()},
               "midband_entry_months": months,
               "midband_rows": [{"symbol": c["symbol"], "R": c["R"],
                                 "reaction_ret_pct": c["reaction_ret_pct"],
                                 "direction": c["direction"]}
                                for c in bands["b1512"]]}
    print(f"{yr}: total {len(cands)} | >=2.5 {len(bands['ge25'])} | "
          f"[2.0,2.5) {len(bands['b2025'])} | [1.5,2.0) {len(bands['b1512'])} | "
          f"[1.0,1.5) {len(bands['b1015'])}")
    print(f"   midband entry months: {months}")
assert out["2026"]["counts"]["ge25"] == 39, "2026 >=2.5 anchor failed"
assert out["2026"]["counts"]["b2025"] == 9, "2026 [2.0,2.5) anchor failed (SAT-32)"
json.dump(out, open(f"{WS}/v3_out/v3_cycle17_diag.json", "w"), indent=1)
print("anchors OK; wrote v3_out/v3_cycle17_diag.json")
