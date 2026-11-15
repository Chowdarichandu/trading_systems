#!/usr/bin/env python3
"""ROUND 2 — INV-ABOVE geometry per regime cell (follow-on to R2-26, which
passed every leg except one green-month flip). run_chain is per (stock,
day), so selecting a day's whole chain from one geometry population is
exact. Cells: T150/S080 on UP days only; on FLAT days only. Placebos:
SHORT-side per-cell books. Gate: Round-1 session gate.
"""
import sys, pickle
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R

books = R.load_books()
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
POP125, POP150 = cache["inv_pop"], cache["inv_pop_T150S080"]

def above_by_cell(cell):
    hi = R.inv_above_rows(POP150)
    lo = R.inv_above_rows(POP125)
    out = {}
    for yr in (2025, 2026):
        rows = [t for t in lo[yr] if R.LABELS.get(t["date"]) != cell]
        rows += [t for t in hi[yr] if R.LABELS.get(t["date"]) == cell]
        out[yr] = rows
    return out

def side_by_cell(cell):
    hi = R.inv_side_rows(POP150, "SHORT", below=False, flat_aside=False)
    lo = R.inv_side_rows(POP125, "SHORT", below=False, flat_aside=False)
    def norm(rows):
        return [R.norm("INV-ABOVE", r["date"], r["stock"], r["direction"],
                       r["entry_time"], r["net"]) for r in rows]
    out = {}
    for yr in (2025, 2026):
        rows = [t for t in norm(lo) if t["date"].startswith(str(yr))
                and R.LABELS.get(t["date"]) != cell]
        rows += [t for t in norm(hi) if t["date"].startswith(str(yr))
                 and R.LABELS.get(t["date"]) == cell]
        out[yr] = rows
    return out

for cyc, cell in (("R2-27", "UP"), ("R2-28", "FLAT")):
    var = above_by_cell(cell)
    pl_books = R.swap(books, "INV-ABOVE", side_by_cell(cell))
    pl = [round(sum(t["net"] for yr in (2025, 2026) for t in pl_books[yr]), 2)]
    out = R.gate(books, R.swap(books, "INV-ABOVE", var), pl)
    R.record(cyc, f"INV-ABOVE exits T150/S080 on {cell}-cell days only", out,
             note=f"placebos {pl} (SHORT-side per-cell book)")
    if out["verdict"]:
        books = R.swap(books, "INV-ABOVE", var)
        R.save_books(books)
        print("    -> BANKED; incumbent updated")

print("cells2 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
