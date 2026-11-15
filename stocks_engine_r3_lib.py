#!/usr/bin/env python3
"""ROUND 3 shared library. Books loaded from the Round-2 ending CSVs and
verified against the Round-2 report totals before anything is scored.
Gate: the frozen nine-leg session gate (stocks_engine_floor_lib.gate_eval)
+ cross-year rule (2026 Jan-Oct must stay >= Rs1,50,000).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import pickle, json, os
import stocks_engine_floor_lib as FL

WS = "/home/hatch/workspace/trading"
LABELS = FL.LABELS
FLOOR = 150000.0

def load_books(path=f"{WS}/r3_books.pkl"):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    books = {yr: FL.load(f"stocks_engine_r2_book{yr}_trades.csv")
             for yr in (2025, 2026)}
    save_books(books, path)
    return books

def save_books(books, path=f"{WS}/r3_books.pkl"):
    with open(path, "wb") as f:
        pickle.dump(books, f)

def swap(books, comp, new_rows):
    out = {}
    for yr in (2025, 2026):
        kept = [t for t in books[yr] if t["comp"] != comp]
        out[yr] = kept + [dict(t) for t in new_rows[yr]]
    return out

def add_comp(books, comp, new_rows):
    out = {}
    for yr in (2025, 2026):
        out[yr] = [dict(t) for t in books[yr]] + [dict(t) for t in new_rows[yr]]
    return out

def split_years(rows):
    return {2025: [t for t in rows if t["date"].startswith("2025")],
            2026: [t for t in rows if t["date"].startswith("2026")]}

def gate(books_base, books_var, placebos_combined, timing_violations=0):
    """Frozen nine-leg gate + the Round-3 cross-year floor rule:
    variant 2026 Jan-Oct must stay >= FLOOR (leg x)."""
    base = {yr: FL.scorecard(books_base[yr], yr) for yr in (2025, 2026)}
    var = {yr: FL.scorecard(books_var[yr], yr) for yr in (2025, 2026)}
    bc = {yr: FL.cells(books_base[yr])[0] for yr in (2025, 2026)}
    vc = {yr: FL.cells(books_var[yr])[0] for yr in (2025, 2026)}
    verdict, legs, sums = FL.gate_eval(base, var, bc, vc,
                                       placebos_combined, timing_violations)
    legs["x_2026_floor_holds"] = var[2026]["jan_oct_total"] >= FLOOR
    verdict = verdict and legs["x_2026_floor_holds"]
    return {"verdict": verdict, "legs": legs, "sums": sums,
            "base": {str(yr): {"total": base[yr]["total"],
                               "jan_oct": base[yr]["jan_oct_total"],
                               "ex_top3": base[yr]["ex_top3_stocks"],
                               "trades": base[yr]["trades"]} for yr in base},
            "var": {str(yr): {"total": var[yr]["total"],
                              "jan_oct": var[yr]["jan_oct_total"],
                              "ex_top3": var[yr]["ex_top3_stocks"],
                              "trades": var[yr]["trades"]} for yr in var},
            "base_cells": {str(yr): bc[yr] for yr in bc},
            "var_cells": {str(yr): vc[yr] for yr in vc}}

RESULTS_PATH = f"{WS}/r3_results.json"

def record(cycle, label, gate_out, note="", extra=None):
    rec = {"cycle": cycle, "label": label, "note": note, **gate_out,
           "banked": bool(gate_out["verdict"])}
    if extra:
        rec.update(extra)
    data = []
    if os.path.exists(RESULTS_PATH):
        data = json.load(open(RESULTS_PATH))
    data.append(rec)
    json.dump(data, open(RESULTS_PATH, "w"), indent=1)
    b, v = gate_out["base"], gate_out["var"]
    print(f"[{cycle}] {label}: {'BANKED' if rec['banked'] else 'REJECTED'} | "
          f"2025 JO {b['2025']['jan_oct']} -> {v['2025']['jan_oct']} | "
          f"2026 JO {b['2026']['jan_oct']} -> {v['2026']['jan_oct']} | "
          f"combined {gate_out['sums']['base_combined']} -> "
          f"{gate_out['sums']['variant_combined']}")
    failed = [k for k, val in gate_out["legs"].items()
              if isinstance(val, bool) and not val]
    if failed:
        print(f"    failed legs: {failed}; flips: {gate_out['legs']['flip_detail']}")
    return rec

def chrono_placebo_total(books, n_remove):
    """Combined Jan-Oct total after removing the chronologically first
    n_remove Jan-Oct trades of the whole book (both years pooled by date)."""
    allt = []
    for yr in (2025, 2026):
        for i, t in enumerate(books[yr]):
            if t["date"] <= f"{yr}-10-31":
                allt.append((t["date"], yr, i))
    allt.sort()
    drop = {(yr, i) for _, yr, i in allt[:n_remove]}
    tot = 0.0
    for yr in (2025, 2026):
        for i, t in enumerate(books[yr]):
            if t["date"] <= f"{yr}-10-31" and (yr, i) not in drop:
                tot += t["net"]
    return round(tot, 2)
