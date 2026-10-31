#!/usr/bin/env python3
"""V2 REGIME DIAGNOSIS — incumbent book P&L by REGIME-CLASSIFIER-1 cell x year.

The classifier is frozen in stocks_engine_frozen.md (REGIME-CLASSIFIER-1)
BEFORE this run: UP = prior close > 50DMA(prior) AND 5-day 50DMA slope >= 0;
DOWN = prior close <= 50DMA AND slope <= 0; FLAT = disagreement. All inputs
known at the prior close. Causality cross-check asserted in-pass: the
classifier's (PC <= M) must equal the audited machinery's below50(day) on
every day of both windows. Read-only diagnosis: no fix is scored here.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade,
paper only, real Rs0.
"""
import csv, json
from collections import defaultdict
from statistics import pstdev

WS = "/home/hatch/workspace/trading"

g = {"__name__": "v2_build_exec"}
exec(compile(open(f"{WS}/stocks_engine_v2_build.py").read(),
             "stocks_engine_v2_build.py", "exec"), g)
assert g["RESULTS"]["controls"]["ALL_PASS"], "build controls failed in-pass"
print("BUILD CONTROLS ALL PASS in this pass")
below50 = g["below50"]

# --- classifier from the machinery's own NIFTY_REG (extended series) ----
# The raw spot_daily.csv ends 2026-10-28; the machinery extends NIFTY to
# 2026-10-30 (trades exist on those days). Labels are computed from
# NIFTY_REG so every book trade date is covered. The price leg was
# independently cross-checked against raw closes in this script's first
# run (452 days, exact); the slope uses the same map's ma50 series.
NIFTY_REG = g["NIFTY_REG"]
axis = sorted(d for d in NIFTY_REG if NIFTY_REG[d]["ma50"] is not None)
labels = {}
for j, d in enumerate(axis):
    if j < 5:
        continue
    pc, m = NIFTY_REG[d]["prev_close"], NIFTY_REG[d]["ma50"]
    s = m - NIFTY_REG[axis[j - 5]]["ma50"]
    if pc > m and s >= 0:
        labels[d] = "UP"
    elif pc <= m and s <= 0:
        labels[d] = "DOWN"
    else:
        labels[d] = "FLAT"
chk = 0
for d in axis:
    if "2025-01-01" <= d <= "2026-10-30":
        assert (NIFTY_REG[d]["prev_close"] <= NIFTY_REG[d]["ma50"]) == below50(d)
        chk += 1
print(f"classifier on NIFTY_REG (extended): {len(labels)} labelled days; "
      f"price leg == below50 on {chk} window days")

state = json.load(open(f"{WS}/stocks_engine_state.json"))["v2"]
def load(fn):
    return [{**t, "net": float(t["net"])} for t in csv.DictReader(open(f"{WS}/{fn}"))]
book25 = load(state["book_files"]["2025"])
book26 = load(state["book_files"]["2026"])
assert (len(book25), round(sum(t["net"] for t in book25), 2)) == \
       (state["best_trades"]["2025"], state["best_by_year"]["2025"])
assert (len(book26), round(sum(t["net"] for t in book26), 2)) == \
       (state["best_trades"]["2026"], state["best_by_year"]["2026"])
print(f"incumbent asserted: 2025 {state['best_by_year']['2025']} | 2026 {state['best_by_year']['2026']}")

# trading-day counts per cell (days present in the book data root windows)
def day_counts(lo, hi):
    c = defaultdict(int)
    for d, lab in labels.items():
        if lo <= d <= hi:
            c[lab] += 1
    return dict(c)
dc25, dc26 = day_counts("2025-01-01", "2025-12-31"), day_counts("2026-01-01", "2026-10-30")
print(f"trading days 2025: {dc25} | 2026: {dc26}")

def cells(book):
    out = {}
    for cell in ("UP", "DOWN", "FLAT"):
        ts = [t for t in book if labels.get(t["date"]) == cell]
        out[cell] = {"trades": len(ts), "net": round(sum(t["net"] for t in ts), 2),
                     "winners": sum(t["net"] > 0 for t in ts)}
    un = [t for t in book if t["date"] not in labels]
    out["UNCLASSIFIED"] = {"trades": len(un), "net": round(sum(t["net"] for t in un), 2)}
    return out
c25, c26 = cells(book25), cells(book26)
print("\n== REGIME CELLS x YEAR (incumbent, post-C19) ==")
for cell in ("UP", "DOWN", "FLAT"):
    print(f"{cell:<5} | 2025 {c25[cell]['trades']:>4} tr {c25[cell]['net']:>11.2f} ({c25[cell]['winners']} w) | "
          f"2026 {c26[cell]['trades']:>4} tr {c26[cell]['net']:>11.2f} ({c26[cell]['winners']} w)")
print(f"UNCLASSIFIED: 2025 {c25['UNCLASSIFIED']} | 2026 {c26['UNCLASSIFIED']}")

def comp_cells(book):
    out = defaultdict(lambda: [0, 0.0])
    for t in book:
        e = out[(t["comp"], labels.get(t["date"], "UNCL"))]
        e[0] += 1; e[1] += t["net"]
    return {f"{k[0]}|{k[1]}": [v[0], round(v[1], 2)] for k, v in sorted(out.items())}
cc25, cc26 = comp_cells(book25), comp_cells(book26)
print("\n== COMPONENT x CELL ==")
for k in sorted(set(cc25) | set(cc26)):
    print(f"{k:<18} | 2025 {cc25.get(k, [0, 0.0])} | 2026 {cc26.get(k, [0, 0.0])}")

def months(book, ms):
    m = defaultdict(float)
    for t in book:
        m[t["date"][:7]] += t["net"]
    return {k: round(m.get(k, 0.0), 2) for k in ms}
M25 = [f"2025-{i:02d}" for i in range(1, 13)]
M26 = [f"2026-{i:02d}" for i in range(1, 11)]
m25, m26 = months(book25, M25), months(book26, M26)
allm = list(m25.values()) + list(m26.values())
spread = {"2025": {"min": min(m25.values()), "max": max(m25.values()),
                   "stdev": round(pstdev(list(m25.values())), 2)},
          "2026": {"min": min(m26.values()), "max": max(m26.values()),
                   "stdev": round(pstdev(list(m26.values())), 2)},
          "combined_22mo": {"min": min(allm), "max": max(allm),
                            "range": round(max(allm) - min(allm), 2),
                            "stdev": round(pstdev(allm), 2),
                            "months_within_20k_pm1k": sum(19000 <= v <= 21000 for v in allm)}}
print(f"\nmonth spread: {spread}")
json.dump({"labels_day_counts": {"2025": dc25, "2026": dc26},
           "cells": {"2025": c25, "2026": c26},
           "comp_cells": {"2025": cc25, "2026": cc26},
           "months": {"2025": m25, "2026": m26}, "spread": spread},
          open(f"{WS}/v2_out/v2_regime_diag.json", "w"), indent=1)
print("wrote v2_out/v2_regime_diag.json")
