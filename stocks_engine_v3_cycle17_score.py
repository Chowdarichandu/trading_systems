#!/usr/bin/env python3
"""V3 CYCLE 17 — CH-V3-3 "P2F-MIDBAND-R1" (frozen in stocks_engine_frozen.md
BEFORE this run).

Additive challenger: component P2F-MIDBAND — P2F machinery verbatim
(reaction_candidates + score_lag lag=1) on results reactions with
|reaction_ret| in [1.5%, 2.0%); T125/S050; RF-1; full standing P2F law
(no ASTRAL / HINDUNILVR / HINDALCO-LONG; v3: no OBEROIRLTY-LONG /
GODREJCP-LONG / UNITDSPR-LONG). Placebo = flip direction on identical
candidates. Decision: v3 maximin beat + hard constraints + Cycle-6
additive standard. Anchors asserted in-pass (build controls; >=2.5%
p2f_book minus v3 law == incumbent P2F rows per-trade, both years;
frozen candidate counts 10/7; every entry date > its R date).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import json, sys
from collections import Counter
sys.path.insert(0, "/home/hatch/workspace/trading")
from stocks_engine_v3_lib import boot, load_books, dump_books, score, decide, WS

g, LABELS = boot()
print("BUILD CONTROLS ALL PASS in this pass; classifier asserted")
rc, score_lag, p2f_book, wk = g["reaction_candidates"], g["score_lag"], g["p2f_book"], g["wk"]
CAL = {"2025": (g["CAL25"], g["LO25"], g["HI25"]),
       "2026": (g["CAL26"], g["LO26"], g["HI26"])}
FROZEN_COUNTS = {"2025": 10, "2026": 7}
V3_P2F_LAW = {("OBEROIRLTY", "LONG"), ("GODREJCP", "LONG"), ("UNITDSPR", "LONG")}

def law_ok(sym, direc):
    return (sym not in ("ASTRAL", "HINDUNILVR")
            and not (sym == "HINDALCO" and direc == "LONG")
            and (sym, direc) not in V3_P2F_LAW)

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v3"]
books = load_books(state["book_files"])
old = score(books, LABELS)
assert old["years"] == state["best_by_year"] and old["combined"] == state["combined_best"]
assert old["vector_sorted"] == state["month_vector_sorted_asc"]
print(f"incumbent asserted: {old['years']} combined {old['combined']}")

out = {"cycle": 17, "challenger": "CH-V3-3 P2F-MIDBAND-R1 [1.5,2.0) x R+1"}
new_books = {}
for yr, (cal, lo, hi) in CAL.items():
    cands = rc(cal, lo, hi)
    # anchor: p2f_book minus v3 law == incumbent P2F rows
    anchor = [t for t in p2f_book(cands) if (t["stock"], t["dir"]) not in V3_P2F_LAW]
    inc = [t for t in books[yr] if t["comp"] == "P2F"]
    ka = Counter((t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2)) for t in anchor)
    ki = Counter((t["date"], t["stock"], t["dir"], t["entry_time"], round(float(t["net"]), 2)) for t in inc)
    assert ka == ki, f"{yr} P2F anchor mismatch:\nonly-anchor {list((ka - ki).items())[:3]}\nonly-inc {list((ki - ka).items())[:3]}"
    mid = [c for c in cands if 1.5 <= abs(c["reaction_ret_pct"]) < 2.0]
    assert len(mid) == FROZEN_COUNTS[yr], f"{yr} midband candidates {len(mid)} != frozen {FROZEN_COUNTS[yr]}"
    def build(cs, flip=False):
        rows = []
        for c in cs:
            cc = {**c, "direction": ("SHORT" if c["direction"] == "LONG" else "LONG")} if flip else c
            t = score_lag(cc, 1)
            if t is None: continue
            if wk(t["date"]) or not law_ok(t["symbol"], t["direction"]): continue
            assert t["date"] > t["R"], f"entry not after R: {t}"
            rows.append(t)
        return rows
    real, plac = build(mid), build(mid, flip=True)
    assert not ({(t["date"], t["symbol"]) for t in real}
                & {(t["date"], t["stock"]) for t in inc}), f"{yr} midband overlaps incumbent P2F"
    def summ(rs):
        net = round(sum(t["net_rs"] for t in rs), 2)
        return {"trades": len(rs), "net": net,
                "expectancy": round(net / len(rs), 2) if rs else None,
                "winners": sum(t["net_rs"] > 0 for t in rs),
                "months": {m: round(sum(t["net_rs"] for t in rs if t["date"][:7] == m), 2)
                           for m in sorted({t["date"][:7] for t in rs})}}
    out[yr] = {"real": summ(real), "placebo": summ(plac),
               "rows": [{"date": t["date"], "stock": t["symbol"], "dir": t["direction"],
                         "entry_time": t["entry_time"], "net": t["net_rs"], "R": t["R"],
                         "reaction_ret_pct": t["reaction_ret_pct"]} for t in real]}
    print(f"{yr} MIDBAND: {out[yr]['real']['trades']} tr net {out[yr]['real']['net']} "
          f"exp {out[yr]['real']['expectancy']} months {out[yr]['real']['months']}")
    print(f"{yr} placebo: {out[yr]['placebo']['trades']} tr net {out[yr]['placebo']['net']} "
          f"exp {out[yr]['placebo']['expectancy']}")
    new_books[yr] = books[yr] + [{"comp": "P2F-MIDBAND", "date": t["date"], "stock": t["symbol"],
                                  "dir": t["direction"], "entry_time": t["entry_time"],
                                  "net": t["net_rs"]} for t in real]

new = score(new_books, LABELS)
banked, checks = decide(old, new)
n_tr = out["2025"]["real"]["trades"] + out["2026"]["real"]["trades"]
n_net = round(out["2025"]["real"]["net"] + out["2026"]["real"]["net"], 2)
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
                    "ex_top3": new["ex_top3"], "trades": new["trades"]}})
print(f"checks: {checks}")
print(f"bottom5 before {old['bottom5']}")
print(f"bottom5 after  {new['bottom5']}")
print(f"combined {old['combined']} -> {new['combined']} | BANKED: {banked}")
if banked:
    dump_books(new_books, "stocks_engine_v3_c17_book2025_trades.csv",
               "stocks_engine_v3_c17_book2026_trades.csv")
    out["new_book_files"] = {"2025": "stocks_engine_v3_c17_book2025_trades.csv",
                             "2026": "stocks_engine_v3_c17_book2026_trades.csv"}
    print("wrote v3 c17 book CSVs")
json.dump(out, open(f"{WS}/v3_out/v3_cycle17_result.json", "w"), indent=1)
print("wrote v3_out/v3_cycle17_result.json")
