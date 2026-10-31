#!/usr/bin/env python3
"""V2 CYCLE 22 — CH-V2-9 "INV-ABOVE" (frozen in stocks_engine_frozen.md
BEFORE this run).

Additive challenger aimed at the UP regime cell (mandate 2, objective (a);
UP x 2025 = -Rs4,665.03 is the book's named weakness): the audited
build_inv machinery verbatim (PLAIN chains T125/S050, p2 filters, LONG,
RF-1, base exclusions) with the regime gate flipped from cond_inv1 to g1
(above-trend days), plus the v2 INV law {HINDALCO, UNITDSPR, TATASTEEL}.
Anchors asserted in-pass: build controls ALL PASS; the same code path with
gate=cond_inv1 reproduces build_inv per-trade in both years and, minus the
v2-law names, equals the incumbent book's INV-LONG rows exactly; mirror
rows are day-disjoint from incumbent INV rows.
Decision (pre-registered additive standard, Cycle 6): bank iff the
cross-year gate passes AND component combined expectancy > 0 AND it beats
the flip placebo (SHORT side of the identical gated population) per-trade.
Basis: equity cash LONG/SHORT, home 25, provisional per 100 shares,
Rs40/trade, paper only, real Rs0.
"""
import csv, json
from collections import Counter, defaultdict
from statistics import pstdev

WS = "/home/hatch/workspace/trading"
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
run_chain, ADR, wk = g["run_chain"], g["ADR"], g["wk"]
cond_inv1, g1, SYMBOLS = g["cond_inv1"], g["g1"], g["SYMBOLS"]
days25, days26 = g["days25"], g["days26"]

# regime labels from the machinery's NIFTY_REG (REGIME-CLASSIFIER-1)
NIFTY_REG = g["NIFTY_REG"]
axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
LABELS = {}
for j, d in enumerate(axis):
    if j < 5:
        continue
    pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
    s = m - NIFTY_REG[axis[j - 5]]["ma50"]
    LABELS[d] = "UP" if (pc > m and s >= 0) else ("DOWN" if (pc <= m and s <= 0) else "FLAT")

def p2_population(days):
    rows = []
    for sym in SYMBOLS:
        for day in days:
            rs = run_chain(sym, day, ("PLAIN", 1.25, 0.5))
            for r in rs:
                r["adr"] = ADR.get((sym, day))
            rows.extend(rs)
    return [r for r in rows if r["round"] <= 2 and r["entry_time"] < "10:30"
            and (r["adr"] or 0) >= 3.0]

def pick(pop, gate, direction, law):
    return [r for r in pop if gate(r["date"]) and r["direction"] == direction
            and not wk(r["date"]) and r["stock"] not in BASE_EXCL
            and r["stock"] not in law]

def key(r):
    return (r["date"], r["stock"], r["entry_time"], r["net"],
            r.get("direction") or r.get("dir"))

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
book25 = load(state["book_files"]["2025"])
book26 = load(state["book_files"]["2026"])
inc25 = round(sum(t["net"] for t in book25), 2)
inc26 = round(sum(t["net"] for t in book26), 2)
assert (len(book25), inc25) == (state["best_trades"]["2025"], state["best_by_year"]["2025"])
assert (len(book26), inc26) == (state["best_trades"]["2026"], state["best_by_year"]["2026"])
print(f"incumbent asserted: 2025 {inc25} ({len(book25)} tr) | 2026 {inc26} ({len(book26)} tr)")

out = {"cycle": 22, "challenger": "CH-V2-9 INV-ABOVE"}
for yr, days, inv_mine, book in (("2025", days25, g["inv_mine25"], book25),
                                 ("2026", days26, g["inv_mine26"], book26)):
    pop = p2_population(days)
    anchor = pick(pop, cond_inv1, "LONG", set())
    assert Counter(map(key, anchor)) == Counter(map(key, inv_mine)), \
        f"{yr} anchor mismatch vs build_inv: {len(anchor)} vs {len(inv_mine)}"
    book_inv = [t for t in book if t["comp"] == "INV-LONG"]
    anchor_law = [r for r in anchor if r["stock"] not in V2_LAW]
    assert Counter(map(key, anchor_law)) == Counter(map(key, book_inv)), \
        f"{yr} anchor-minus-law != incumbent INV rows"
    mirror = pick(pop, g1, "LONG", V2_LAW)
    placebo = pick(pop, g1, "SHORT", V2_LAW)
    assert not ({r["date"] for r in mirror} & {t["date"] for t in book_inv}), \
        f"{yr} mirror days overlap incumbent INV days"
    def summ(rs):
        net = round(sum(r["net"] for r in rs), 2)
        cells = {}
        for cell in ("UP", "DOWN", "FLAT"):
            ts = [r for r in rs if LABELS.get(r["date"]) == cell]
            cells[cell] = [len(ts), round(sum(r["net"] for r in ts), 2)]
        return {"trades": len(rs), "net": net,
                "expectancy": round(net / len(rs), 2) if rs else None,
                "winners": sum(r["net"] > 0 for r in rs), "cells": cells,
                "months": {m: round(sum(r["net"] for r in rs if r["date"][:7] == m), 2)
                           for m in sorted({r["date"][:7] for r in rs})}}
    out[yr] = {"mirror": summ(mirror), "placebo": summ(placebo),
               "mirror_rows": [{k: r[k] for k in ("date", "stock", "direction", "entry_time", "net", "setup")}
                               for r in mirror]}
    print(f"{yr} mirror : {out[yr]['mirror']['trades']} tr net {out[yr]['mirror']['net']} "
          f"exp {out[yr]['mirror']['expectancy']} cells {out[yr]['mirror']['cells']}")
    print(f"{yr} placebo: {out[yr]['placebo']['trades']} tr net {out[yr]['placebo']['net']} "
          f"exp {out[yr]['placebo']['expectancy']}")

new25 = inc25 + out["2025"]["mirror"]["net"]
new26 = inc26 + out["2026"]["mirror"]["net"]
comb_old = round(inc25 + inc26, 2)
comb_new = round(new25 + new26, 2)
ntr = out["2025"]["mirror"]["trades"] + out["2026"]["mirror"]["trades"]
nnet = round(out["2025"]["mirror"]["net"] + out["2026"]["mirror"]["net"], 2)
ptr = out["2025"]["placebo"]["trades"] + out["2026"]["placebo"]["trades"]
pnet = round(out["2025"]["placebo"]["net"] + out["2026"]["placebo"]["net"], 2)
comp_exp = round(nnet / ntr, 2) if ntr else None
pla_exp = round(pnet / ptr, 2) if ptr else None
gate = {"combined_rises": comb_new > comb_old, "y2025_not_fall": new25 >= inc25,
        "y2026_not_fall": new26 >= inc26,
        "neither_negative": new25 >= 0 and new26 >= 0}
gate_pass = all(gate.values())
l21 = {"component_expectancy_positive": (comp_exp or -1) > 0,
       "beats_flip_placebo_per_trade": (comp_exp or -1e9) > (pla_exp if pla_exp is not None else -1e9)}
banked = gate_pass and all(l21.values())
out.update({"incumbent": {"2025": inc25, "2026": inc26, "combined": comb_old},
            "if_added": {"2025": round(new25, 2), "2026": round(new26, 2),
                         "combined": comb_new},
            "component_combined": {"trades": ntr, "net": nnet, "expectancy": comp_exp},
            "placebo_combined": {"trades": ptr, "net": pnet, "expectancy": pla_exp},
            "gate": gate, "l21_standard": l21, "banked": banked})
print(f"gate: {gate} | L21 standard: {l21}")
print(f"component combined {ntr} tr {nnet} exp {comp_exp} | placebo {ptr} tr {pnet} exp {pla_exp}")
print(f"combined {comb_old} -> {comb_new} | BANKED: {banked}")

if banked:
    def dump(book, mirror_rows_raw, fn):
        rows = list(book)
        for r in mirror_rows_raw:
            rows.append({"comp": "INV-ABOVE", "date": r["date"], "stock": r["stock"],
                         "dir": r["direction"], "entry_time": r["entry_time"],
                         "net": r["net"]})
        rows.sort(key=lambda t: (t["date"], t.get("entry_time", "09:15"), t["stock"], t["comp"]))
        with open(f"{WS}/{fn}", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["comp", "date", "stock", "dir",
                                              "entry_time", "net"])
            w.writeheader(); w.writerows(rows)
        return rows
    # re-derive raw mirror rows for the dump (full fields)
    dump25 = dump(book25, [r for r in p2_population(days25)
                           if g1(r["date"]) and r["direction"] == "LONG"
                           and not wk(r["date"]) and r["stock"] not in BASE_EXCL
                           and r["stock"] not in V2_LAW],
                  "stocks_engine_v2_c22_book2025_trades.csv")
    dump26 = dump(book26, [r for r in p2_population(days26)
                           if g1(r["date"]) and r["direction"] == "LONG"
                           and not wk(r["date"]) and r["stock"] not in BASE_EXCL
                           and r["stock"] not in V2_LAW],
                  "stocks_engine_v2_c22_book2026_trades.csv")
    assert (len(dump25), round(sum(t["net"] for t in dump25), 2)) == \
           (len(book25) + out["2025"]["mirror"]["trades"], round(new25, 2))
    assert (len(dump26), round(sum(t["net"] for t in dump26), 2)) == \
           (len(book26) + out["2026"]["mirror"]["trades"], round(new26, 2))
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
    m25 = months(dump25, [f"2025-{i:02d}" for i in range(1, 13)])
    m26 = months(dump26, [f"2026-{i:02d}" for i in range(1, 11)])
    av = list(m25.values()) + list(m26.values())
    out["new_book"] = {"cells2025": cells(dump25), "cells2026": cells(dump26),
                       "months2025": m25, "months2026": m26,
                       "spread": {"min": min(av), "max": max(av),
                                  "range": round(max(av) - min(av), 2),
                                  "stdev": round(pstdev(av), 2)}}
    print(f"new book cells 2025 {out['new_book']['cells2025']} | 2026 {out['new_book']['cells2026']}")
    print("wrote c22 book CSVs")
json.dump(out, open(f"{WS}/v2_out/v2_cycle22_result.json", "w"), indent=1, default=str)
print("wrote v2_out/v2_cycle22_result.json")
