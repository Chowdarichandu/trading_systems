#!/usr/bin/env python3
"""V2 CYCLE 23 — R2-LOWBAND stands aside on UP days (frozen BEFORE scoring).

Frozen diagnosis (REGIME-CLASSIFIER-1 cells, C22 book): (R2-LOWBAND x UP)
2025 9 tr -Rs3,506.17 | 2026 4 tr -Rs22.58 — negative in both years,
combined -Rs3,528.75, under the pre-registered cell-exclusion bar (both
years negative AND combined <= -Rs500). Deletion-only cycle: the deleted
set is asserted == the frozen set exactly; labels recomputed in-pass from
the machinery's NIFTY_REG with the price leg asserted == below50.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from statistics import pstdev

WS = "/home/hatch/workspace/trading"
FROZEN = {"2025": (9, -3506.17), "2026": (4, -22.58)}

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

out = {"cycle": 23, "change": "R2-LOWBAND stands aside on UP days"}
new_books = {}
for yr in ("2025", "2026"):
    book = load(state["book_files"][yr])
    tot = round(sum(t["net"] for t in book), 2)
    assert (len(book), tot) == (state["best_trades"][yr], state["best_by_year"][yr])
    kill = [t for t in book if t["comp"] == "R2-LOWBAND" and LABELS.get(t["date"]) == "UP"]
    ktot = round(sum(t["net"] for t in kill), 2)
    assert (len(kill), ktot) == FROZEN[yr], f"{yr} deleted set != freeze: {(len(kill), ktot)}"
    rest = [t for t in book if not (t["comp"] == "R2-LOWBAND" and LABELS.get(t["date"]) == "UP")]
    ntot = round(sum(t["net"] for t in rest), 2)
    assert round(tot - ktot, 2) == ntot
    out[yr] = {"deleted": [len(kill), ktot], "before": tot, "after": ntot,
               "trades": len(rest)}
    new_books[yr] = rest
    print(f"{yr}: deleted {len(kill)} tr ({ktot}) | {tot} -> {ntot} ({len(rest)} tr)")

old_c = round(state["best_by_year"]["2025"] + state["best_by_year"]["2026"], 2)
new_c = round(out["2025"]["after"] + out["2026"]["after"], 2)
gate = {"combined_rises": new_c > old_c,
        "y2025_not_fall": out["2025"]["after"] >= state["best_by_year"]["2025"],
        "y2026_not_fall": out["2026"]["after"] >= state["best_by_year"]["2026"],
        "neither_negative": out["2025"]["after"] >= 0 and out["2026"]["after"] >= 0}
banked = all(gate.values())
out.update({"gate": gate, "banked": banked,
            "combined": {"before": old_c, "after": new_c}})
print(f"gate: {gate} | combined {old_c} -> {new_c} | BANKED: {banked}")

if banked:
    dump(new_books["2025"], "stocks_engine_v2_c23_book2025_trades.csv")
    dump(new_books["2026"], "stocks_engine_v2_c23_book2026_trades.csv")
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
    m25 = months(new_books["2025"], [f"2025-{i:02d}" for i in range(1, 13)])
    m26 = months(new_books["2026"], [f"2026-{i:02d}" for i in range(1, 11)])
    av = list(m25.values()) + list(m26.values())
    per = defaultdict(float)
    for t in new_books["2025"] + new_books["2026"]:
        pass
    def extop3(book):
        p = defaultdict(float)
        for t in book:
            p[t["stock"]] += t["net"]
        top = {k for k, _ in sorted(p.items(), key=lambda kv: -kv[1])[:3]}
        return round(sum(t["net"] for t in book if t["stock"] not in top), 2)
    out["new_book"] = {"cells2025": cells(new_books["2025"]),
                       "cells2026": cells(new_books["2026"]),
                       "months2025": m25, "months2026": m26,
                       "red_months2025": [k for k, v in m25.items() if v < 0],
                       "spread": {"min": min(av), "max": max(av),
                                  "range": round(max(av) - min(av), 2),
                                  "stdev": round(pstdev(av), 2)},
                       "ex_top3": {"2025": extop3(new_books["2025"]),
                                   "2026": extop3(new_books["2026"])}}
    print(f"cells 2025 {out['new_book']['cells2025']} | 2026 {out['new_book']['cells2026']}")
    print(f"spread {out['new_book']['spread']} | red 2025 {out['new_book']['red_months2025']}")
    print("wrote c23 book CSVs")
json.dump(out, open(f"{WS}/v2_out/v2_cycle23_result.json", "w"), indent=1)
print("wrote v2_out/v2_cycle23_result.json")
