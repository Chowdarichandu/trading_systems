#!/usr/bin/env python3
"""V3 CYCLE 2 — CH-V3-2 "INV-ABOVE-R3" (frozen in stocks_engine_frozen.md
BEFORE this run; recorded v2 queue, second item).

Additive challenger: the audited INV machinery verbatim with the p2 round
leg at round >= 3 and the regime gate flipped to g1 (above-trend days) —
entry < 10:30, ADR >= 3.0, LONG only, T125/S050, RF-1, base exclusions +
the v2 INV law {HINDALCO, UNITDSPR, TATASTEEL}. Placebo = SHORT side of
the identical gated population. Decision: v3 maximin beat + hard
constraints + Cycle-6 additive standard. Anchors asserted in-pass (build
controls; g1 + round<=2 path == incumbent INV-ABOVE rows exactly; frozen
counts 28/4).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import json, sys
from collections import Counter
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, load_books, dump_books, score, decide, WS

g, LABELS = boot()
print("BUILD CONTROLS ALL PASS in this pass; classifier asserted")
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
cond_inv1, g1, SYMBOLS = g["cond_inv1"], g["g1"], g["SYMBOLS"]
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}
FROZEN_COUNTS = {"2025": 28, "2026": 4}

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
books = load_books(state["book_files"])
old = score(books, LABELS)
assert old["years"] == state["best_by_year"] and old["combined"] == state["combined_best"]
assert old["vector_sorted"] == state["month_vector_sorted_asc"]
print(f"incumbent asserted: {old['years']} combined {old['combined']}")

def population(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    return rows

def pick(pop, round_pred, gate, direction, law):
    return [r for r in pop if round_pred(r["round"]) and r["entry_time"] < "10:30"
            and (r["adr"] or 0) >= 3.0 and gate(r["date"])
            and r["direction"] == direction and not wk(r["date"])
            and r["stock"] not in BASE_EXCL and r["stock"] not in law]

def key(r):
    return (r["date"], r["stock"], r["entry_time"], r["net"], r["direction"])

out = {"cycle": 2, "challenger": "CH-V3-2 INV-ABOVE-R3 (above-trend, round>=3)"}
new_books = {}
for yr, days in (("2025", g["days25"]), ("2026", g["days26"])):
    pop = population(days)
    anchor = pick(pop, lambda n: n <= 2, g1, "LONG", V2_LAW)
    book_abv = [t for t in books[yr] if t["comp"] == "INV-ABOVE"]
    inc_key = Counter((t["date"], t["stock"], t["entry_time"], t["net"], t["dir"])
                      for t in book_abv)
    assert Counter(map(key, anchor)) == inc_key, \
        f"{yr} anchor (g1, round<=2, law) != incumbent INV-ABOVE rows"
    r3 = pick(pop, lambda n: n >= 3, g1, "LONG", V2_LAW)
    placebo = pick(pop, lambda n: n >= 3, g1, "SHORT", V2_LAW)
    assert len(r3) == FROZEN_COUNTS[yr], f"{yr} R3 count {len(r3)} != frozen {FROZEN_COUNTS[yr]}"
    assert not ({(r["date"], r["stock"], r["entry_time"], r["round"]) for r in r3}
                & {(t["date"], t["stock"], t["entry_time"], t.get("round")) for t in book_abv}), \
        f"{yr} R3 overlaps incumbent INV-ABOVE rows"
    def summ(rs):
        net = round(sum(r["net"] for r in rs), 2)
        return {"trades": len(rs), "net": net,
                "expectancy": round(net / len(rs), 2) if rs else None,
                "winners": sum(r["net"] > 0 for r in rs),
                "months": {m: round(sum(r["net"] for r in rs if r["date"][:7] == m), 2)
                           for m in sorted({r["date"][:7] for r in rs})}}
    out[yr] = {"r3": summ(r3), "placebo": summ(placebo),
               "rows": [{k: r[k] for k in ("date", "stock", "direction",
                                           "entry_time", "net", "round")} for r in r3]}
    print(f"{yr} INV-ABOVE-R3: {out[yr]['r3']['trades']} tr net {out[yr]['r3']['net']} "
          f"exp {out[yr]['r3']['expectancy']} months {out[yr]['r3']['months']}")
    print(f"{yr} placebo     : {out[yr]['placebo']['trades']} tr net {out[yr]['placebo']['net']} "
          f"exp {out[yr]['placebo']['expectancy']}")
    add = [{"comp": "INV-ABOVE-R3", "date": r["date"], "stock": r["stock"],
            "dir": r["direction"], "entry_time": r["entry_time"], "net": r["net"]}
           for r in r3]
    new_books[yr] = books[yr] + add

new = score(new_books, LABELS)
banked, checks = decide(old, new)
n_tr = out["2025"]["r3"]["trades"] + out["2026"]["r3"]["trades"]
n_net = round(out["2025"]["r3"]["net"] + out["2026"]["r3"]["net"], 2)
p_tr = out["2025"]["placebo"]["trades"] + out["2026"]["placebo"]["trades"]
p_net = round(out["2025"]["placebo"]["net"] + out["2026"]["placebo"]["net"], 2)
exp_c = round(n_net / n_tr, 2) if n_tr else None
pexp_c = round(p_net / p_tr, 2) if p_tr else None
checks["component_expectancy_positive"] = exp_c is not None and exp_c > 0
checks["beats_flip_placebo_per_trade"] = exp_c is not None and pexp_c is not None and exp_c > pexp_c
banked = banked and checks["component_expectancy_positive"] and checks["beats_flip_placebo_per_trade"]
out.update({"checks": checks, "banked": banked,
            "component_combined": {"trades": n_tr, "net": n_net, "expectancy": exp_c},
            "placebo_combined": {"trades": p_tr, "net": p_net, "expectancy": pexp_c},
            "old": {"years": old["years"], "combined": old["combined"],
                    "bottom5": old["bottom5"], "cells": old["cells"]},
            "new": {"years": new["years"], "combined": new["combined"],
                    "bottom5": new["bottom5"], "cells": new["cells"],
                    "months": new["months"], "vector_sorted": new["vector_sorted"],
                    "ex_top3": new["ex_top3"]}})
print(f"checks: {checks}")
print(f"bottom5 before {old['bottom5']}")
print(f"bottom5 after  {new['bottom5']}")
print(f"combined {old['combined']} -> {new['combined']} | BANKED: {banked}")
if banked:
    dump_books(new_books, "stocks_engine_v3_c2_book2025_trades.csv",
               "stocks_engine_v3_c2_book2026_trades.csv")
    out["new_book_files"] = {"2025": "stocks_engine_v3_c2_book2025_trades.csv",
                             "2026": "stocks_engine_v3_c2_book2026_trades.csv"}
    print("wrote v3 c2 book CSVs")
json.dump(out, open(f"{WS}/v3_out/v3_cycle2_result.json", "w"), indent=1)
print("wrote v3_out/v3_cycle2_result.json")
