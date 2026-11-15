#!/usr/bin/env python3
"""ROUND 11 shared library. Books loaded from the Round-10 ending
CSVs (stocks_engine_r10_book{yr}_trades.csv — the causality-audited
banked book, unchanged since Round 6/7/8 bankings) and verified
against the recorded totals before anything is scored (2025
Jan-Oct Rs78,420.04 / 887 rows; 2026 Jan-Oct Rs2,29,696.21 / 969
rows). Gate: the frozen nine-leg session gate
(stocks_engine_r3_lib.gate) + cross-year leg (x): variant 2026
Jan-Oct >= Rs1,50,000. Records go to r11_results.json so earlier
evidence files stay untouched. Timing violations are DERIVED per
construction and passed explicitly — never defaulted silently
(lesson R4-L2). Basis: equity cash, home 25, provisional per 100
shares, Rs40/trade, paper only, real Rs0.
"""
import json, os
import stocks_engine_floor_lib as FL
import stocks_engine_r3_lib as R3

WS = "/home/hatch/workspace/trading"
RESULTS_PATH = f"{WS}/r11_results.json"
gate = R3.gate
swap = R3.swap
add_comp = R3.add_comp
split_years = R3.split_years
LABELS = FL.LABELS

JO_BASE = {2025: 78420.04, 2026: 229696.21}
ROWS_BASE = {2025: 887, 2026: 969}
FULL_BASE = {2025: 77041.31, 2026: 229696.21}

_books = None

def load_books():
    global _books
    if _books is not None:
        return _books
    books = {yr: FL.load(f"stocks_engine_r10_book{yr}_trades.csv")
             for yr in (2025, 2026)}
    for yr in (2025, 2026):
        jo = round(sum(t["net"] for t in books[yr]
                       if t["date"] <= f"{yr}-10-31"), 2)
        full = round(sum(t["net"] for t in books[yr]), 2)
        assert jo == JO_BASE[yr], (yr, jo, JO_BASE[yr])
        assert full == FULL_BASE[yr], (yr, full, FULL_BASE[yr])
        assert len(books[yr]) == ROWS_BASE[yr], (yr, len(books[yr]))
    _books = books
    return books

def _append(rec):
    data = []
    if os.path.exists(RESULTS_PATH):
        data = json.load(open(RESULTS_PATH))
    data.append(rec)
    json.dump(data, open(RESULTS_PATH, "w"), indent=1)

def record(cycle, label, gate_out, note="", extra=None,
           force_no_bank=False):
    banked = bool(gate_out["verdict"]) and not force_no_bank
    rec = {"cycle": cycle, "label": label, "note": note, **gate_out,
           "banked": banked}
    if force_no_bank and gate_out["verdict"]:
        rec["verdict"] = False
        rec["decision_support_only"] = True
    if extra:
        rec.update(extra)
    _append(rec)
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
    rec = {"cycle": cycle, "type": "audit", "label": label,
           "note": note, "banked": False}
    if extra:
        rec.update(extra)
    _append(rec)
    print(f"[{cycle}] AUDIT {label}: {note[:120]}")
    return rec

def full_total(bk):
    return round(sum(t["net"] for yr in (2025, 2026) for t in bk[yr]), 2)

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

def month_net(rows, ym):
    return round(sum(t["net"] for t in rows
                     if t["date"][:7] == ym), 2)

def row_id(t):
    """Identity of an underlying trade across form labels."""
    return (t["date"], t["stock"], t["dir"], t["entry_time"],
            round(float(t["net"]), 2))
