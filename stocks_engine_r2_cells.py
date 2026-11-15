#!/usr/bin/env python3
"""ROUND 2 — REGIME-CELL COMBINATIONS: per-cell exit geometry and
stand-asides, gated like everything else. F4 lives in DOWN/FLAT cells;
INV-LONG (banked cell) is DOWN-only after the FLAT stand-aside; INV-ABOVE
lives in FLAT/UP cells. Placebo for a geometry cell = the same geometry
applied to the WRONG cell (same change, wrong place). Stand-aside placebo
= chronological first-N removal. Gate: Round-1 session gate.
"""
import sys, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R

books = R.load_books()
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))

# ---- (comp x cell x year) slices of the incumbent ---------------------------
print("incumbent slices (Jan-Oct):")
for comp in sorted({t["comp"] for yr in (2025, 2026) for t in books[yr]}):
    for yr in (2025, 2026):
        cells = {}
        for t in books[yr]:
            if t["comp"] == comp and t["date"] <= f"{yr}-10-31":
                c = R.LABELS.get(t["date"], "?")
                n, s = cells.get(c, (0, 0.0))
                cells[c] = (n + 1, s + float(t["net"]))
        print(f"  {comp} {yr}: " + ", ".join(
            f"{c} {n}tr/{s:+,.0f}" for c, (n, s) in sorted(cells.items())))

# ---- capture INV population at T150/S080 exits ------------------------------
if "inv_pop_T150S080" not in cache:
    g = L.load_machinery(L.FULLHIST, "2026-10-28")
    ALLDAYS = sorted({d for (_, d) in g["DAYCTX"]})
    rows = []
    for sym in g["SYMBOLS"]:
        for day in ALLDAYS:
            rs = g["run_chain"](sym, day, ("PLAIN", 1.50, 0.80))
            for r in rs:
                r["adr"] = g["ADR"].get((sym, day))
            rows.extend(rs)
    cache["inv_pop_T150S080"] = [
        {kk: r[kk] for kk in ("date", "stock", "direction", "setup", "round",
                              "entry_time", "entry", "exit_price", "net",
                              "adr", "event_status")} for r in rows]
    pickle.dump(cache, open(f"{WS}/r2_cache.pkl", "wb"))
    print(f"inv_pop_T150S080 captured: {len(rows)} rows")
    # NOTE: run_chain restarts each round at the previous exit, so a new
    # exit geometry legitimately re-forms later rounds (causal: picks
    # never read exit outcomes). Round-1 trades must be identical though.
    k_old = {(r["date"], r["stock"], r["entry_time"])
             for r in cache["inv_pop"] if r["round"] == 1}
    k_new = {(r["date"], r["stock"], r["entry_time"])
             for r in cache["inv_pop_T150S080"] if r["round"] == 1}
    assert k_old == k_new, "INV round-1 identity mismatch across geometries"
    print("INV T150S080 round-1 identity check OK")
POP150 = cache["inv_pop_T150S080"]

def f4_cell_rows(geo_pop, cell):
    base = R.f4_rows(cache["f4_1000_T150S095"], 0.5, 1.0, excl_dir=True)
    geo = R.f4_rows(geo_pop, 0.5, 1.0, excl_dir=True)
    out = {}
    for yr in (2025, 2026):
        gm = {(t["date"], t["stock"]): t for t in geo[yr]}
        rows = []
        for t in base[yr]:
            if R.LABELS.get(t["date"]) == cell and (t["date"], t["stock"]) in gm:
                rows.append(gm[(t["date"], t["stock"])])
            else:
                rows.append(t)
        out[yr] = rows
    return out

def geo_cycle(cyc, label, comp, var_rows, placebo_var_rows_list):
    global books
    var_books = R.swap(books, comp, var_rows)
    pl = []
    for prow in placebo_var_rows_list:
        pb = R.swap(books, comp, prow)
        pl.append(round(sum(t["net"] for yr in (2025, 2026) for t in pb[yr]), 2))
    out = R.gate(books, var_books, pl)
    R.record(cyc, label, out, note=f"placebos {pl}")
    if out["verdict"]:
        books = var_books
        R.save_books(books)
        print("    -> BANKED; incumbent updated")
    return out

P125 = cache["f4_1000_T125S065"]
P175 = cache["f4_1000_T175S095"]

import json as _json, os as _os
DONE = set()
if _os.path.exists(f"{WS}/r2_results.json"):
    DONE = {r["cycle"] for r in _json.load(open(f"{WS}/r2_results.json"))}

if "R2-20" not in DONE:
    geo_cycle("R2-20", "F4 DOWN-cell exits T125/S065", "F4",
              f4_cell_rows(P125, "DOWN"), [f4_cell_rows(P125, "FLAT")])
if "R2-21" not in DONE:
    geo_cycle("R2-21", "F4 DOWN-cell exits T175/S095", "F4",
              f4_cell_rows(P175, "DOWN"), [f4_cell_rows(P175, "FLAT")])
if "R2-22" not in DONE:
    geo_cycle("R2-22", "F4 FLAT-cell exits T125/S065", "F4",
              f4_cell_rows(P125, "FLAT"), [f4_cell_rows(P125, "DOWN")])
if "R2-23" not in DONE:
    geo_cycle("R2-23", "F4 FLAT-cell exits T175/S095", "F4",
              f4_cell_rows(P175, "FLAT"), [f4_cell_rows(P175, "DOWN")])

# R2-24: F4 x FLAT stand-aside (delete the FLAT-cell F4 population)
if "R2-24" not in DONE:
    var = {yr: [t for t in books[yr]
                if not (t["comp"] == "F4" and R.LABELS.get(t["date"]) == "FLAT")]
           for yr in (2025, 2026)}
    var_books = {yr: var[yr] for yr in (2025, 2026)}
    n_removed = sum(1 for yr in (2025, 2026) for t in books[yr]
                    if t["comp"] == "F4" and R.LABELS.get(t["date"]) == "FLAT")
    pl = [R.chrono_placebo(books, "F4", n_removed)]
    out = R.gate(books, var_books, pl)
    R.record("R2-24", "F4 x FLAT stand-aside (delete FLAT-cell F4)", out,
             note=f"placebos {pl} (chrono first-N of F4, N={n_removed})")
    if out["verdict"]:
        books = var_books
        R.save_books(books)
        print("    -> BANKED; incumbent updated")

def side_split(comp, rows):
    return R.split_years([R.norm(comp, r["date"], r["stock"], r["direction"],
                                 r["entry_time"], r["net"]) for r in rows])

# R2-25: INV-LONG at T150/S080 exits (banked settings ADR3.0 r<=3 <11:00)
var_long = R.inv_long_rows(POP150, adr_min=3.0, round_max=3, cutoff="11:00")
pl_long = side_split("INV-LONG", R.inv_side_rows(
    POP150, "SHORT", below=True, adr_min=3.0, round_max=3, cutoff="11:00"))
geo_cycle("R2-25", "INV-LONG exits T150/S080 (banked cell settings)", "INV-LONG",
          var_long, [pl_long])

# R2-26: INV-ABOVE at T150/S080 exits (incumbent settings ADR3.0 r<=2 <10:30)
var_above = R.inv_above_rows(POP150)
pl_above = side_split("INV-ABOVE", R.inv_side_rows(
    POP150, "SHORT", below=False, flat_aside=False))
geo_cycle("R2-26", "INV-ABOVE exits T150/S080", "INV-ABOVE",
          var_above, [pl_above])

print("cell cycles done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
