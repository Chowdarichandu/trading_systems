#!/usr/bin/env python3
"""V2 CYCLE 26 — CH-V2-11 "INV-ABOVE-LATE" (frozen in
stocks_engine_frozen.md BEFORE this run).

Additive challenger: the INV chain machinery verbatim (PLAIN T125/S050,
ADR >= 3.0, LONG, RF-1, base exclusions, v2 INV law, above-trend gate
g1 — INV-ABOVE's gate) with the entry-time leg flipped to >= 10:30
(round <= 2 kept). Frozen counts from the cycle diagnosis: 72 (2025) /
27 (2026). Anchor asserted in-pass: the incumbent entry leg on g1 with
the v2 law equals the incumbent book's INV-ABOVE rows exactly.
Decision (Cycle-6 additive standard + C24 cell guard): bank iff the
cross-year gate passes AND component combined expectancy > 0 AND it
beats the flip placebo (SHORT side of the identical late above-trend
population) per-trade AND no regime cell flips negative in either year.
Basis: equity cash LONG/SHORT, home 25, provisional per 100 shares,
Rs40/trade, paper only, real Rs0.
"""
import csv, json
from collections import Counter, defaultdict
from statistics import pstdev

WS = "/home/hatch/workspace/trading"
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}
FROZEN_COUNT = {"2025": 72, "2026": 27}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
g1, SYMBOLS = g["g1"], g["SYMBOLS"]
days25, days26 = g["days25"], g["days26"]

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

def p2_all(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    return rows

def pick(pop, direction, early):
    return [r for r in pop if r["direction"] == direction and r["round"] <= 2
            and ((r["entry_time"] < "10:30") if early else (r["entry_time"] >= "10:30"))
            and g1(r["date"]) and not wk(r["date"])
            and (r["adr"] or 0) >= 3.0
            and r["stock"] not in BASE_EXCL and r["stock"] not in V2_LAW]

def key(r):
    return (r["date"], r["stock"], r["entry_time"], r["net"],
            r.get("direction") or r.get("dir"))

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
books = {yr: load(state["book_files"][yr]) for yr in ("2025", "2026")}
inc = {}
for yr in ("2025", "2026"):
    inc[yr] = round(sum(t["net"] for t in books[yr]), 2)
    assert (len(books[yr]), inc[yr]) == (state["best_trades"][yr], state["best_by_year"][yr])
print(f"incumbent asserted: 2025 {inc['2025']} ({len(books['2025'])} tr) | 2026 {inc['2026']} ({len(books['2026'])} tr)")

def cells(book):
    o = {}
    for cell in ("UP", "DOWN", "FLAT"):
        ts = [t for t in book if LABELS.get(t["date"]) == cell]
        o[cell] = [len(ts), round(sum(t["net"] for t in ts), 2)]
    return o
def summ(rs):
    net = round(sum(r["net"] for r in rs), 2)
    return {"trades": len(rs), "net": net,
            "expectancy": round(net / len(rs), 2) if rs else None,
            "winners": sum(r["net"] > 0 for r in rs)}

out = {"cycle": 26, "challenger": "CH-V2-11 INV-ABOVE-LATE", "detail": {}}
late_rows = {}
for yr, days in (("2025", days25), ("2026", days26)):
    pop = p2_all(days)
    anchor = pick(pop, "LONG", True)
    book_above = [t for t in books[yr] if t["comp"] == "INV-ABOVE"]
    assert Counter(map(key, anchor)) == Counter(map(key, book_above)), \
        f"{yr} anchor != incumbent INV-ABOVE rows: {len(anchor)} vs {len(book_above)}"
    late = pick(pop, "LONG", False)
    placebo = pick(pop, "SHORT", False)
    assert len(late) == FROZEN_COUNT[yr], f"{yr} late count {len(late)} != frozen {FROZEN_COUNT[yr]}"
    kept_keys = {(r["date"], r["stock"], r["entry_time"]) for r in anchor}
    assert not ({(r["date"], r["stock"], r["entry_time"]) for r in late} & kept_keys), \
        f"{yr} late population overlaps incumbent INV-ABOVE rows"
    late_rows[yr] = late
    out["detail"][yr] = {"component": summ(late), "placebo": summ(placebo)}
    print(f"{yr} INV-ABOVE-LATE: {len(late)} tr net {out['detail'][yr]['component']['net']} "
          f"exp {out['detail'][yr]['component']['expectancy']} | "
          f"placebo: {len(placebo)} tr net {out['detail'][yr]['placebo']['net']} "
          f"exp {out['detail'][yr]['placebo']['expectancy']}")

new_books, out_y = {}, {}
for yr in ("2025", "2026"):
    nb = books[yr] + [{"comp": "INV-ABOVE-LATE", "date": r["date"], "stock": r["stock"],
                       "dir": r["direction"], "entry_time": r["entry_time"],
                       "net": r["net"]} for r in late_rows[yr]]
    new_books[yr] = nb
    out_y[yr] = {"before": inc[yr], "after": round(sum(t["net"] for t in nb), 2),
                 "trades": len(nb)}
    out[yr] = out_y[yr]

comb_old = round(inc["2025"] + inc["2026"], 2)
comb_new = round(out_y["2025"]["after"] + out_y["2026"]["after"], 2)
ntr = sum(out["detail"][yr]["component"]["trades"] for yr in ("2025", "2026"))
nnet = round(sum(out["detail"][yr]["component"]["net"] for yr in ("2025", "2026")), 2)
ptr = sum(out["detail"][yr]["placebo"]["trades"] for yr in ("2025", "2026"))
pnet = round(sum(out["detail"][yr]["placebo"]["net"] for yr in ("2025", "2026")), 2)
comp_exp = round(nnet / ntr, 2) if ntr else None
pla_exp = round(pnet / ptr, 2) if ptr else None
gate = {"combined_rises": comb_new > comb_old,
        "y2025_not_fall": out_y["2025"]["after"] >= inc["2025"],
        "y2026_not_fall": out_y["2026"]["after"] >= inc["2026"],
        "neither_negative": out_y["2025"]["after"] >= 0 and out_y["2026"]["after"] >= 0}
l21 = {"component_expectancy_positive": (comp_exp or -1) > 0,
       "beats_flip_placebo_per_trade": (comp_exp or -1e9) > (pla_exp if pla_exp is not None else -1e9)}
cells_after = {yr: cells(new_books[yr]) for yr in ("2025", "2026")}
cell_guard = all(v[1] > 0 for yr in ("2025", "2026") for v in cells_after[yr].values())
banked = all(gate.values()) and all(l21.values()) and cell_guard
out.update({"gate": gate, "l21_standard": l21, "cell_guard_all_positive": cell_guard,
            "component_combined": {"trades": ntr, "net": nnet, "expectancy": comp_exp},
            "placebo_combined": {"trades": ptr, "net": pnet, "expectancy": pla_exp},
            "combined": {"before": comb_old, "after": comb_new}, "banked": banked})
print(f"gate: {gate} | L21: {l21} | cell guard: {cell_guard}")
print(f"component combined {ntr} tr {nnet} exp {comp_exp} | placebo {ptr} tr {pnet} exp {pla_exp}")
print(f"combined {comb_old} -> {comb_new} | BANKED: {banked}")

if banked:
    def dump(rows, fn):
        rows = sorted(rows, key=lambda t: (t["date"], t.get("entry_time", "09:15"),
                                           t["stock"], t["comp"]))
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["comp", "date", "stock", "dir",
                                              "entry_time", "net"])
            w.writeheader(); w.writerows(rows)
    dump(new_books["2025"], "stocks_engine_v2_c26_book2025_trades.csv")
    dump(new_books["2026"], "stocks_engine_v2_c26_book2026_trades.csv")
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
    m25 = months(new_books["2025"], [f"2025-{i:02d}" for i in range(1, 13)])
    m26 = months(new_books["2026"], [f"2026-{i:02d}" for i in range(1, 11)])
    av = list(m25.values()) + list(m26.values())
    out["new_book"] = {"cells2025": cells_after["2025"], "cells2026": cells_after["2026"],
                       "months2025": m25, "months2026": m26,
                       "red_months2025": [k for k, v in m25.items() if v < 0],
                       "red_months2026": [k for k, v in m26.items() if v < 0],
                       "spread": {"min": min(av), "max": max(av),
                                  "range": round(max(av) - min(av), 2),
                                  "stdev": round(pstdev(av), 2),
                                  "months_in_band_20k_pm1k": sum(1 for v in av if 19000 <= v <= 21000)},
                       "ex_top3": {"2025": extop3(new_books["2025"]),
                                   "2026": extop3(new_books["2026"])}}
    print(f"new book cells 2025 {cells_after['2025']} | 2026 {cells_after['2026']}")
    print("wrote c26 book CSVs")
json.dump(out, open(f"{WS}/v2_out/v2_cycle26_result.json", "w"), indent=1, default=str)
print("wrote v2_out/v2_cycle26_result.json")
