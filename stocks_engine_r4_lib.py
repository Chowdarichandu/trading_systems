#!/usr/bin/env python3
"""ROUND 4 shared library. Same books, same frozen nine-leg gate + the
cross-year floor rule as Round 3 (stocks_engine_r3_lib.gate). Records go
to r4_results.json so the Round-3 evidence file stays untouched.
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import json, os
import stocks_engine_r3_lib as R3

WS = "/home/hatch/workspace/trading"
RESULTS_PATH = f"{WS}/r4_results.json"
gate = R3.gate
load_books = R3.load_books
save_books = R3.save_books
swap = R3.swap
add_comp = R3.add_comp
split_years = R3.split_years

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

def book_total(bk):
    return round(sum(sum(t["net"] for t in bk[yr]
                         if t["date"] <= f"{yr}-10-31")
                     for yr in (2025, 2026)), 2)

def full_total(bk):
    return round(sum(t["net"] for yr in (2025, 2026) for t in bk[yr]), 2)
