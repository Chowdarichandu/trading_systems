#!/usr/bin/env python3
"""V3 DELETION CYCLE — generic scorer for mechanism-scoped slice deletions
frozen in stocks_engine_frozen.md BEFORE scoring. The freeze JSON (argv 1)
is the machine-readable twin of the frozen-file entry: {cycle, label,
slice: [comp, stock, dir], rows: {"2025": [[date, entry_time, net], ...],
"2026": [...]}}. The deleted set found in the current book is asserted ==
the frozen set EXACTLY (v2 deletion-cycle pattern); any mismatch stops
the run before any decision. Decision: v3 maximin beat + hard constraints
(lib decide()). Deletion cycles carry no expectancy/placebo legs — the
Cycle-6 standard binds additive challengers; deletions are judged on the
gate, as in every prior registry cycle.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import json, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, load_books, dump_books, score, decide, WS

fz = json.load(open(sys.argv[1]))
g, LABELS = boot()
print("BUILD CONTROLS ALL PASS in this pass; classifier asserted")
state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
books = load_books(state["book_files"])
old = score(books, LABELS)
assert old["years"] == state["best_by_year"] and old["combined"] == state["combined_best"]
assert old["vector_sorted"] == state["month_vector_sorted_asc"]
print(f"incumbent asserted: {old['years']} combined {old['combined']}")

comp, stock, direc = fz["slice"]
new_books, deleted = {}, {}
for yr in ("2025", "2026"):
    kill = [t for t in books[yr]
            if t["comp"] == comp and t["stock"] == stock and t["dir"] == direc]
    frozen = sorted((d, e, float(n)) for d, e, n in fz["rows"][yr])
    found = sorted((t["date"], t["entry_time"], float(t["net"])) for t in kill)
    assert found == frozen, f"{yr} deleted set != freeze:\nfound {found}\nfrozen {frozen}"
    deleted[yr] = [len(kill), round(sum(t["net"] for t in kill), 2)]
    new_books[yr] = [t for t in books[yr]
                     if not (t["comp"] == comp and t["stock"] == stock and t["dir"] == direc)]
    print(f"{yr}: deleted {deleted[yr][0]} tr ({deleted[yr][1]})")

new = score(new_books, LABELS)
banked, checks = decide(old, new)
out = {"cycle": fz["cycle"], "change": fz["label"], "slice": fz["slice"],
       "deleted": deleted, "checks": checks, "banked": banked,
       "old": {"years": old["years"], "combined": old["combined"],
               "bottom5": old["bottom5"], "cells": old["cells"]},
       "new": {"years": new["years"], "combined": new["combined"],
               "bottom5": new["bottom5"], "cells": new["cells"],
               "months": new["months"], "vector_sorted": new["vector_sorted"],
               "ex_top3": new["ex_top3"], "trades": new["trades"]}}
print(f"checks: {checks}")
print(f"bottom5 before {old['bottom5']}")
print(f"bottom5 after  {new['bottom5']}")
print(f"combined {old['combined']} -> {new['combined']} | BANKED: {banked}")
n = fz["cycle"]
if banked:
    dump_books(new_books, f"stocks_engine_v3_c{n}_book2025_trades.csv",
               f"stocks_engine_v3_c{n}_book2026_trades.csv")
    out["new_book_files"] = {"2025": f"stocks_engine_v3_c{n}_book2025_trades.csv",
                             "2026": f"stocks_engine_v3_c{n}_book2026_trades.csv"}
    print(f"wrote v3 c{n} book CSVs")
json.dump(out, open(f"{WS}/v3_out/v3_cycle{n}_result.json", "w"), indent=1)
print(f"wrote v3_out/v3_cycle{n}_result.json")
