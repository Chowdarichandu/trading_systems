#!/usr/bin/env python3
"""ROUND 2 shared library: law filters, component builders from the cached
populations, book swaps, and the frozen Round-1 session gate (floor_lib).
Basis: equity cash, home 25, provisional per 100 shares, Rs40/trade, paper.
"""
import pickle, json, os
from collections import defaultdict
import stocks_engine_floor_lib as FL

WS = "/home/hatch/workspace/trading"
LABELS = FL.LABELS

EXCL_DIR = {("GODREJCP", "SHORT"), ("INDUSTOWER", "LONG"),
            ("HINDUNILVR", "SHORT"), ("UNITDSPR", "SHORT"),
            ("HINDCOPPER", "SHORT"), ("OIL", "SHORT"),
            ("IRCTC", "SHORT"), ("HINDALCO", "LONG"),
            ("TATASTEEL", "LONG"), ("NHPC", "SHORT"),
            ("PFC", "SHORT"), ("RECLTD", "SHORT")}
EXCL_V2 = {("F4", "GLENMARK", "SHORT"), ("N4-V3", "GLENMARK", "SHORT"),
           ("N4-V3", "BDL", "SHORT"), ("F4", "HDFCBANK", "SHORT"),
           ("F4", "KALYANKJIL", "LONG"), ("N4-V3", "HINDALCO", "SHORT"),
           ("N4-V3", "HINDZINC", "LONG"), ("N4-V3", "UNITDSPR", "LONG"),
           ("N4-V3", "RECLTD", "LONG"), ("N4-V3", "WIPRO", "SHORT"),
           ("P2F-R2", "KALYANKJIL", "LONG")}
V3_DROP = {
    ("INV-ABOVE", "PFC", "LONG"), ("INV-ABOVE", "RECLTD", "LONG"),
    ("N4-V3", "INDUSTOWER", "LONG"), ("N4-V3", "OIL", "SHORT"),
    ("N4-V3", "VEDL", "SHORT"),
    ("P2F", "OBEROIRLTY", "LONG"), ("P2F", "GODREJCP", "LONG"),
    ("P2F", "UNITDSPR", "LONG"),
    ("P2F-R2", "OBEROIRLTY", "LONG"), ("P2F-R2", "BDL", "LONG"),
    ("P2F-R2", "GODREJCP", "LONG"), ("P2F-R2", "TVSMOTOR", "SHORT"),
    ("P2F-R2", "GLENMARK", "LONG"),
    ("R2-LOWBAND", "TVSMOTOR", "LONG"),
}
BASE_EXCL = {"BDL", "VEDL", "HINDZINC", "INDUSTOWER", "KALYANKJIL"}
V2_INV_LAW = {"HINDALCO", "UNITDSPR", "TATASTEEL"}

def _wk(d):
    from datetime import date
    return date.fromisoformat(d).weekday() >= 5

def norm(comp, date, stock, dir_, entry_time, net):
    return {"comp": comp, "date": date, "stock": stock, "dir": dir_,
            "entry_time": entry_time, "net": round(float(net), 2)}

# ---------------------------------------------------------------- books ----
def load_books(path=f"{WS}/r2_books.pkl"):
    if os.path.exists(path):
        with open(path, "rb") as f:
            return pickle.load(f)
    books = {yr: FL.load(f"stocks_engine_floor_c4_book{yr}_trades.csv")
             for yr in (2025, 2026)}
    save_books(books, path)
    return books

def save_books(books, path=f"{WS}/r2_books.pkl"):
    with open(path, "wb") as f:
        pickle.dump(books, f)

def swap(books, comp, new_rows):
    """new_rows: {yr: [rows]} replacing comp entirely in both years."""
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

# ---------------------------------------------------------------- gate -----
def gate(books_base, books_var, placebos_combined, timing_violations=0):
    base = {yr: FL.scorecard(books_base[yr], yr) for yr in (2025, 2026)}
    var = {yr: FL.scorecard(books_var[yr], yr) for yr in (2025, 2026)}
    bc = {yr: FL.cells(books_base[yr])[0] for yr in (2025, 2026)}
    vc = {yr: FL.cells(books_var[yr])[0] for yr in (2025, 2026)}
    verdict, legs, sums = FL.gate_eval(base, var, bc, vc,
                                       placebos_combined, timing_violations)
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

RESULTS_PATH = f"{WS}/r2_results.json"

def record(cycle, label, gate_out, note="", extra=None):
    rec = {"cycle": cycle, "label": label, "verdict":
           "BANKED" if gate_out["verdict"] else "REJECTED",
           "note": note, **gate_out}
    if extra:
        rec.update(extra)
    data = []
    if os.path.exists(RESULTS_PATH):
        data = json.load(open(RESULTS_PATH))
    data.append(rec)
    json.dump(data, open(RESULTS_PATH, "w"), indent=1)
    b, v = gate_out["base"], gate_out["var"]
    print(f"[{cycle}] {label}: {rec['verdict']} | "
          f"2025 JO {b['2025']['jan_oct']} -> {v['2025']['jan_oct']} | "
          f"2026 JO {b['2026']['jan_oct']} -> {v['2026']['jan_oct']} | "
          f"combined {gate_out['sums']['base_combined']} -> "
          f"{gate_out['sums']['variant_combined']}")
    failed = [k for k, val in gate_out["legs"].items()
              if isinstance(val, bool) and not val]
    if failed:
        print(f"    failed legs: {failed}; flips: {gate_out['legs']['flip_detail']}")
    return rec

def chrono_placebo(books, comp, n_remove):
    """Book minus the chronologically first n_remove trades of comp
    (combined total across years) — the Round-1 style null for removals."""
    out = {}
    removed = 0
    allt = sorted((t for yr in (2025, 2026) for t in books[yr]
                   if t["comp"] == comp), key=lambda t: t["date"])
    drop_keys = set()
    for t in allt[:n_remove]:
        drop_keys.add((t["date"], t["stock"], t["dir"], t["entry_time"],
                       t["net"]))
    for yr in (2025, 2026):
        rows = []
        for t in books[yr]:
            k = (t["date"], t["stock"], t["dir"], t["entry_time"], t["net"])
            if t["comp"] == comp and k in drop_keys:
                removed += 1
                continue
            rows.append(t)
        out[yr] = rows
    return round(sum(t["net"] for yr in (2025, 2026) for t in out[yr]), 2)

# ------------------------------------------------------------- F4 rows -----
def f4_rows(pop, lo, hi, excl_dir=True):
    """pop: cached raw build2_p rows (one exit config, one meas time).
    Band filter on |premove_pct| in [lo, hi) (percent units; hi=None = open).
    Law: wk, no setup3, direct legs, EXCL_DIR (toggle), EXCL_V2 F4 rows."""
    out = []
    for t in pop:
        if t["leg"] != "direct":
            continue
        pm = abs(t["premove_pct"])
        if pm < lo or (hi is not None and pm >= hi):
            continue
        if _wk(t["date"]):
            continue
        if t["setup"] == "setup3_bounce_rejection":
            continue
        if excl_dir and (t["symbol"], t["dir"]) in EXCL_DIR:
            continue
        if ("F4", t["symbol"], t["dir"]) in EXCL_V2:
            continue
        out.append(norm("F4", t["date"], t["symbol"], t["dir"],
                        t["entry_time"], t["net"]))
    return split_years(out)

# ------------------------------------------------------------- INV rows ----
# Day gates exactly as the machinery defines them: cond_inv1 = Nifty prior
# close <= 50DMA (INV-LONG / INV-R3 days); g1 = prior close > 50DMA
# (INV-ABOVE days). Computed with floor_lib's own ma50 convention.
def _below_map():
    import csv as _csv
    daily = []
    with open(f"{WS}/data/full_hist/NIFTY/spot_daily.csv") as f:
        for r in _csv.DictReader(f):
            daily.append({"date": r["date"][:10], "close": float(r["close"])})
    have = {d["date"] for d in daily}
    with open(f"{WS}/data/sarvaritu_fwd/NIFTY/spot_daily.csv") as f:
        for r in _csv.DictReader(f):
            d = r["date"][:10]
            if d not in have:
                daily.append({"date": d, "close": float(r["close"])})
    daily.sort(key=lambda x: x["date"])
    closes = [d["close"] for d in daily]
    out = {}
    for i, d in enumerate(daily):
        if i < 50:
            continue
        ma50 = sum(closes[i - 50:i]) / 50
        out[d["date"]] = closes[i - 1] <= ma50
    return out

BELOW = _below_map()   # day -> True if prior close <= 50DMA (cond_inv1 day)

def _inv_base(pop, adr_min, round_max, cutoff, direction):
    rows = []
    for r in pop:
        if r["round"] > round_max or r["round"] < 1:
            continue
        if not (r["entry_time"] < cutoff):
            continue
        if (r["adr"] or 0) < adr_min:
            continue
        if r["direction"] != direction:
            continue
        if _wk(r["date"]):
            continue
        if r["stock"] in BASE_EXCL or r["stock"] in V2_INV_LAW:
            continue
        rows.append(r)
    return rows

def inv_long_rows(pop, adr_min=3.0, round_max=2, cutoff="10:30",
                  flat_aside=True, comp="INV-LONG"):
    rows = _inv_base(pop, adr_min, round_max, cutoff, "LONG")
    rows = [r for r in rows if BELOW.get(r["date"])]            # cond_inv1
    if flat_aside:
        rows = [r for r in rows if LABELS.get(r["date"]) != "FLAT"]  # C24
    return split_years([norm(comp, r["date"], r["stock"], "LONG",
                             r["entry_time"], r["net"]) for r in rows])

def inv_above_rows(pop, adr_min=3.0, round_max=2, cutoff="10:30"):
    rows = _inv_base(pop, adr_min, round_max, cutoff, "LONG")
    rows = [r for r in rows if BELOW.get(r["date"]) is False]       # g1
    rows = [r for r in rows
            if ("INV-ABOVE", r["stock"], "LONG") not in V3_DROP]
    return split_years([norm("INV-ABOVE", r["date"], r["stock"], "LONG",
                             r["entry_time"], r["net"]) for r in rows])

def inv_side_rows(pop, direction, below, adr_min=3.0, round_max=2,
                  cutoff="10:30", flat_aside=True):
    """Placebo populations from the chain's other side / other day gate."""
    rows = _inv_base(pop, adr_min, round_max, cutoff, direction)
    rows = [r for r in rows if BELOW.get(r["date"]) is below]
    if flat_aside:
        rows = [r for r in rows if LABELS.get(r["date"]) != "FLAT"]
    return rows
