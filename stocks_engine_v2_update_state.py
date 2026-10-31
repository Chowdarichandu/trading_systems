#!/usr/bin/env python3
"""Post-cycle state updater for engine v2 (mechanical bookkeeping only).
Usage: python3 stocks_engine_v2_update_state.py <cycle> <law_line_or_dash>
Reads v2_out/v2_cycle<cycle>_result.json (must carry 'banked'; on a bank,
the score script must already have written the c<cycle> book CSVs and the
result must carry per-year before/after + trades)."""
import json, sys

WS = "/home/hatch/workspace/trading"
cyc = int(sys.argv[1])
law = sys.argv[2] if len(sys.argv) > 2 else "-"
res = json.load(open(f"{WS}/v2_out/v2_cycle{cyc}_result.json"))
sp = f"{WS}/stocks_engine_state.json"
s = json.load(open(sp))
v2 = s["v2"]
v2["cycles_completed"] = cyc
if res["banked"]:
    for yr in ("2025", "2026"):
        v2["best_by_year"][yr] = res[yr]["after"]
        v2["best_trades"][yr] = res[yr]["trades"]
        v2["book_files"][yr] = f"stocks_engine_v2_c{cyc}_book{yr}_trades.csv"
    v2["combined_best"] = round(v2["best_by_year"]["2025"] + v2["best_by_year"]["2026"], 2)
    v2["monthly_avg_22mo"] = round(v2["combined_best"] / 22, 2)
    v2["no_beat_cycles"] = 0
    if law != "-":
        v2.setdefault("book_law_added", []).append(law)
else:
    v2["no_beat_cycles"] = v2.get("no_beat_cycles", 0) + 1
fp = v2["floor_position"]
fp["current"] = dict(v2["best_by_year"])
fp["gap"] = {yr: round(fp["floor"][yr] - v2["best_by_year"][yr], 2) for yr in ("2025", "2026")}
v2["cycle_lock"] = "v2-cycle-24-chain (subagent chain, 2026-10-31)"
json.dump(s, open(sp, "w"), indent=1)
print(f"state updated: cycle {cyc} banked={res['banked']} | combined_best {v2['combined_best']} "
      f"| by_year {v2['best_by_year']} | trades {v2['best_trades']} | no_beat {v2['no_beat_cycles']} "
      f"| floor gap {fp['gap']}")
