#!/usr/bin/env python3
"""V2 CYCLE 24 — INV-LONG stands aside on FLAT days (frozen BEFORE scoring
in stocks_engine_frozen.md, V2 CYCLE 24).

Frozen diagnosis (REGIME-CLASSIFIER-1 cells, C23 book): (INV-LONG x FLAT)
2025 9 tr -Rs2,739.25 | 2026 11 tr -Rs2,600.72 — negative in both years,
combined -Rs5,339.97, under the Cycle-23 cell-exclusion bar; the only
remaining (comp x cell) both-negative pair on the book. Deletion-only
cycle: deleted set asserted == the frozen set exactly. Cell guard
(mandate 2 (a)): any cell flipping negative in either year = reject.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from statistics import pstdev

WS = "/home/hatch/workspace/trading"
FROZEN = {"2025": (9, -2739.25), "2026": (11, -2600.72)}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
NIFTY_REG, below50 = g["NIFTY_REG"], g["below50"]
axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
LABELS = {}
for j, d in enumerate(axis):
    if j < 5:
        continue
    pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
    s = m - NIFTY_REG[axis[j - 5]]["ma50"]
    LABELS[d] = "UP" if (pc > m and s >= 0) else ("DOWN" if (pc <= m and s <= 0) else "FLAT")
for d in axis:
    if "2025-01-01" <= d <= "2026-10-30":
        assert (NIFTY_REG[d]["prev_close"] <= NIFTY_REG[d]["ma50"]) == below50(d)
print("classifier asserted: price leg == below50 on all window days")

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
def dump(rows, fn):
    rows = sorted(rows, key=lambda t: (t["date"], t.get("entry_time", "09:15"),
                                       t["stock"], t["comp"]))
    with open(f"{WS}/{fn}", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["comp", "date", "stock", "dir",
                                          "entry_time", "net"])
        w.writeheader(); w.writerows(rows)
def cells(book):
    o = {}
    for cell in ("UP", "DOWN", "FLAT"):
        ts = [t for t in book if LABELS.get(t["date"]) == cell]
        o[cell] = [len(ts), round(sum(t["net"] for t in ts), 2)]
    return o
def months(book, ms):
    m = defaultdict(float)
    for t in book:
        m[t["date"][:7]] += t["net"]
    return {k: round(m.get(k, 0.0), 2) for k in ms}
def extop3(book):
    p = defaultdict(float)
    for t in book:
        p[t["stock"]] += t["net"]
    top = {k for k, _ in sorted(p.items(), key=lambda kv: -kv[1])[:3]}
    return round(sum(t["net"] for t in book if t["stock"] not in top), 2)

out = {"cycle": 24, "change": "INV-LONG stands aside on FLAT days"}
new_books, cells_before, cells_after = {}, {}, {}
for yr in ("2025", "2026"):
    book = load(state["book_files"][yr])
    tot = round(sum(t["net"] for t in book), 2)
    assert (len(book), tot) == (state["best_trades"][yr], state["best_by_year"][yr])
    cells_before[yr] = cells(book)
    kill = [t for t in book if t["comp"] == "INV-LONG" and LABELS.get(t["date"]) == "FLAT"]
    ktot = round(sum(t["net"] for t in kill), 2)
    assert (len(kill), ktot) == FROZEN[yr], f"{yr} deleted set != freeze: {(len(kill), ktot)}"
    rest = [t for t in book if not (t["comp"] == "INV-LONG" and LABELS.get(t["date"]) == "FLAT")]
    ntot = round(sum(t["net"] for t in rest), 2)
    assert round(tot - ktot, 2) == ntot
    out[yr] = {"deleted": [len(kill), ktot], "before": tot, "after": ntot,
               "trades": len(rest)}
    new_books[yr] = rest
    cells_after[yr] = cells(rest)
    print(f"{yr}: deleted {len(kill)} tr ({ktot}) | {tot} -> {ntot} ({len(rest)} tr)")

old_c = round(state["best_by_year"]["2025"] + state["best_by_year"]["2026"], 2)
new_c = round(out["2025"]["after"] + out["2026"]["after"], 2)
gate = {"combined_rises": new_c > old_c,
        "y2025_not_fall": out["2025"]["after"] >= state["best_by_year"]["2025"],
        "y2026_not_fall": out["2026"]["after"] >= state["best_by_year"]["2026"],
        "neither_negative": out["2025"]["after"] >= 0 and out["2026"]["after"] >= 0}
cell_guard = all(v[1] > 0 for yr in ("2025", "2026") for v in cells_after[yr].values())
banked = all(gate.values()) and cell_guard
out.update({"gate": gate, "cell_guard_all_positive": cell_guard, "banked": banked,
            "cells_before": cells_before, "cells_after": cells_after,
            "combined": {"before": old_c, "after": new_c}})
print(f"gate: {gate} | cell guard: {cell_guard} | combined {old_c} -> {new_c} | BANKED: {banked}")

if banked:
    dump(new_books["2025"], "stocks_engine_v2_c24_book2025_trades.csv")
    dump(new_books["2026"], "stocks_engine_v2_c24_book2026_trades.csv")
    m25 = months(new_books["2025"], [f"2025-{i:02d}" for i in range(1, 13)])
    m26 = months(new_books["2026"], [f"2026-{i:02d}" for i in range(1, 11)])
    av = list(m25.values()) + list(m26.values())
    inband = sum(1 for v in av if 19000 <= v <= 21000)
    out["new_book"] = {"cells2025": cells_after["2025"], "cells2026": cells_after["2026"],
                       "months2025": m25, "months2026": m26,
                       "red_months2025": [k for k, v in m25.items() if v < 0],
                       "red_months2026": [k for k, v in m26.items() if v < 0],
                       "spread": {"min": min(av), "max": max(av),
                                  "range": round(max(av) - min(av), 2),
                                  "stdev": round(pstdev(av), 2),
                                  "months_in_band_20k_pm1k": inband},
                       "ex_top3": {"2025": extop3(new_books["2025"]),
                                   "2026": extop3(new_books["2026"])}}
    print(f"cells 2025 {cells_after['2025']} | 2026 {cells_after['2026']}")
    print(f"spread {out['new_book']['spread']} | red 2025 {out['new_book']['red_months2025']}")
    print("wrote c24 book CSVs")
json.dump(out, open(f"{WS}/v2_out/v2_cycle24_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle24_result.json")
