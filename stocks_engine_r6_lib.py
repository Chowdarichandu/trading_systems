#!/usr/bin/env python3
"""ROUND 6 shared library. Books loaded from the Round-5 ending CSVs
(identical to the Round-4 books — Round 5 banked nothing) and verified
against the recorded totals before anything is scored (2025 Jan-Oct
Rs77,806.57 / 857 rows; 2026 Jan-Oct Rs2,23,293.34 / 899 rows).
Gate: the frozen nine-leg session gate (stocks_engine_r3_lib.gate)
+ cross-year leg (x): variant 2026 Jan-Oct must stay >= Rs1,50,000.
Records go to r6_results.json so earlier evidence files stay untouched.
Timing violations are DERIVED per construction in each workstream and
passed explicitly — never defaulted silently (lesson R4-L2).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import json, os, pickle
import stocks_engine_floor_lib as FL
import stocks_engine_r3_lib as R3

WS = "/home/hatch/workspace/trading"
RESULTS_PATH = f"{WS}/r6_results.json"
BOOKS_PATH = f"{WS}/r6_books.pkl"
gate = R3.gate
swap = R3.swap
add_comp = R3.add_comp
split_years = R3.split_years
LABELS = FL.LABELS

JO_BASE = {2025: 77806.57, 2026: 223293.34}
ROWS_BASE = {2025: 857, 2026: 899}

def load_books():
    if os.path.exists(BOOKS_PATH):
        with open(BOOKS_PATH, "rb") as f:
            return pickle.load(f)
    books = {yr: FL.load(f"stocks_engine_r5_book{yr}_trades.csv")
             for yr in (2025, 2026)}
    for yr in (2025, 2026):
        jo = round(sum(t["net"] for t in books[yr]
                       if t["date"] <= f"{yr}-10-31"), 2)
        assert jo == JO_BASE[yr], (yr, jo, JO_BASE[yr])
        assert len(books[yr]) == ROWS_BASE[yr], (yr, len(books[yr]))
    save_books(books)
    return books

def save_books(books):
    with open(BOOKS_PATH, "wb") as f:
        pickle.dump(books, f)

def record(cycle, label, gate_out, note="", extra=None, force_no_bank=False):
    banked = bool(gate_out["verdict"]) and not force_no_bank
    rec = {"cycle": cycle, "label": label, "note": note, **gate_out,
           "banked": banked}
    if force_no_bank and gate_out["verdict"]:
        rec["verdict"] = False
        rec["decision_support_only"] = True
    if extra:
        rec.update(extra)
    data = []
    if os.path.exists(RESULTS_PATH):
        data = json.load(open(RESULTS_PATH))
    data.append(rec)
    json.dump(data, open(RESULTS_PATH, "w"), indent=1)
    b, v = gate_out["base"], gate_out["var"]
    print(f"[{cycle}] {label}: "
          f"{'BANKED' if banked else 'REJECTED'} | "
          f"2025 JO {b['2025']['jan_oct']} -> {v['2025']['jan_oct']} | "
          f"2026 JO {b['2026']['jan_oct']} -> {v['2026']['jan_oct']} | "
          f"combined {gate_out['sums']['base_combined']} -> "
          f"{gate_out['sums']['variant_combined']}")
    failed = [k for k, val in gate_out["legs"].items()
              if isinstance(val, bool) and not val]
    if failed:
        print(f"    failed legs: {failed}; flips: "
              f"{gate_out['legs']['flip_detail']}")
    return rec

def record_audit(cycle, label, note, extra=None):
    rec = {"cycle": cycle, "type": "audit", "label": label, "note": note,
           "banked": False}
    if extra:
        rec.update(extra)
    data = []
    if os.path.exists(RESULTS_PATH):
        data = json.load(open(RESULTS_PATH))
    data.append(rec)
    json.dump(data, open(RESULTS_PATH, "w"), indent=1)
    print(f"[{cycle}] AUDIT {label}: {note[:120]}")
    return rec

def book_total(bk):
    return round(sum(sum(t["net"] for t in bk[yr]
                         if t["date"] <= f"{yr}-10-31")
                     for yr in (2025, 2026)), 2)

def full_total(bk):
    return round(sum(t["net"] for yr in (2025, 2026) for t in bk[yr]), 2)
