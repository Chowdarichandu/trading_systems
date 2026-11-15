#!/usr/bin/env python3
"""ROUND 2 — INV CYCLES: full permutation crosses for INV-LONG and INV-ABOVE
(ADR {2.5,3.0,3.5} x round cap {<=2,<=3} x cutoff {10:30,11:00}), plus the
merged INV-LONG+INV-R3 round-law cells. Every cell gated individually
against the same base; the best passing cell per comp banks at grid end.
Placebos per cell: (i) SHORT side of the same cell + day gate, (ii) LONG
side of the same cell on the opposite day gate. Gate: Round-1 session gate.
"""
import sys, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R

cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
POP = cache["inv_pop"]
books = R.load_books()

def ms(rows):
    return Counter((t["comp"], t["date"], t["stock"], t["dir"],
                    t["entry_time"], round(float(t["net"]), 2)) for t in rows)

# ---- lib anchors ------------------------------------------------------------
inc_long = R.inv_long_rows(POP)
inc_above = R.inv_above_rows(POP)
for yr in (2025, 2026):
    cur_l = [t for t in books[yr] if t["comp"] == "INV-LONG"]
    cur_a = [t for t in books[yr] if t["comp"] == "INV-ABOVE"]
    assert ms(inc_long[yr]) == ms(cur_l), f"INV-LONG anchor failed {yr}"
    assert ms(inc_above[yr]) == ms(cur_a), f"INV-ABOVE anchor failed {yr}"
print("INV anchors OK (lib defaults == FLOOR-C4 INV-LONG / INV-ABOVE)")

def cell_rows(comp, adr, rmax, cutoff):
    if comp == "INV-LONG":
        return R.inv_long_rows(POP, adr_min=adr, round_max=rmax, cutoff=cutoff)
    return R.inv_above_rows(POP, adr_min=adr, round_max=rmax, cutoff=cutoff)

def placebo_books(comp, adr, rmax, cutoff):
    """Two placebo books vs the CURRENT books: SHORT-side same cell+gate;
    LONG same cell on the opposite gate. Returned as combined totals."""
    gate_below = (comp == "INV-LONG")
    out = []
    for direction, below in (("SHORT", gate_below), ("LONG", not gate_below)):
        rows = R._inv_base(POP, adr, rmax, cutoff, direction)
        rows = [r for r in rows if R.BELOW.get(r["date"]) is below]
        if comp == "INV-LONG":
            rows = [r for r in rows if R.LABELS.get(r["date"]) != "FLAT"]
        if comp == "INV-ABOVE" and direction == "LONG":
            rows = [r for r in rows
                    if ("INV-ABOVE", r["stock"], "LONG") not in R.V3_DROP]
        prow = R.split_years([R.norm(comp, r["date"], r["stock"], direction,
                                     r["entry_time"], r["net"]) for r in rows])
        pb = R.swap(books, comp, prow)
        out.append(round(sum(t["net"] for yr in (2025, 2026)
                             for t in pb[yr]), 2))
    return out

def run_grid(cyc, comp):
    global books
    cells = []
    best = None
    for adr in (2.5, 3.0, 3.5):
        for rmax in (2, 3):
            for cutoff in ("10:30", "11:00"):
                if (adr, rmax, cutoff) == (3.0, 2, "10:30"):
                    continue  # the incumbent cell itself
                var_rows = cell_rows(comp, adr, rmax, cutoff)
                pl = placebo_books(comp, adr, rmax, cutoff)
                var_books = R.swap(books, comp, var_rows)
                if comp == "INV-LONG" and rmax == 3:
                    # the round-3 rows the variant absorbs already live in
                    # INV-R3 (non-FLAT ones) — remove them there so the
                    # variant book never double-counts a trade.
                    r3 = R._inv_base(POP, adr, 3, cutoff, "LONG")
                    r3 = [r for r in r3 if r["round"] == 3
                          and R.BELOW.get(r["date"])
                          and R.LABELS.get(r["date"]) != "FLAT"]
                    r3k = {(r["date"], r["stock"], r["entry_time"],
                            round(float(r["net"]), 2)) for r in r3}
                    for yr in (2025, 2026):
                        var_books[yr] = [
                            t for t in var_books[yr]
                            if not (t["comp"] == "INV-R3"
                                    and (t["date"], t["stock"],
                                         t["entry_time"],
                                         round(float(t["net"]), 2)) in r3k)]
                out = R.gate(books, var_books, pl)
                cell = {"adr": adr, "round_max": rmax, "cutoff": cutoff,
                        "verdict": "PASS" if out["verdict"] else "FAIL",
                        "combined": out["sums"]["variant_combined"],
                        "jo2025": out["var"]["2025"]["jan_oct"],
                        "jo2026": out["var"]["2026"]["jan_oct"],
                        "trades": {yr: out["var"][yr]["trades"] for yr in ("2025", "2026")},
                        "failed_legs": [kk for kk, vv in out["legs"].items()
                                        if isinstance(vv, bool) and not vv],
                        "placebos": pl}
                cells.append(cell)
                print(f"  {comp} ADR{adr} r<={rmax} <{cutoff}: {cell['verdict']} "
                      f"comb {cell['combined']} (25JO {cell['jo2025']}, "
                      f"26JO {cell['jo2026']}) fails {cell['failed_legs']}")
                if out["verdict"] and (best is None or
                                       out["sums"]["variant_combined"] >
                                       best[0]["sums"]["variant_combined"]):
                    best = (out, var_books, cell)
    # grid summary record (base gate output = incumbent vs itself shape)
    base_gate = R.gate(books, books, [])
    R.record(cyc, f"{comp} permutation grid (11 cells)", base_gate,
             note=f"{comp}: {sum(1 for c in cells if c['verdict'] == 'PASS')} "
                  f"of 11 cells pass the full gate",
             extra={"cells": cells, "grid_comp": comp})
    if best is not None:
        out, var_books, cell = best
        books = var_books
        R.save_books(books)
        print(f"  -> BANKED best {comp} cell: ADR{cell['adr']} "
              f"r<={cell['round_max']} <{cell['cutoff']} "
              f"(combined {cell['combined']})")
    else:
        print(f"  -> no {comp} cell passed; incumbent kept")
    return cells

run_grid("R2-07", "INV-LONG")
run_grid("R2-08", "INV-ABOVE")

# ---- merged round-law cells (INV-LONG + INV-R3 unified) ---------------------
def merged_rows(flat_aside):
    rows = R._inv_base(POP, 3.0, 99, "10:30", "LONG")
    rows = [r for r in rows if R.BELOW.get(r["date"])]
    if flat_aside:
        rows = [r for r in rows if R.LABELS.get(r["date"]) != "FLAT"]
    return R.split_years([R.norm("INV-LONG", r["date"], r["stock"], "LONG",
                                 r["entry_time"], r["net"]) for r in rows])

def merged_placebos(flat_aside):
    out = []
    for direction, below in (("SHORT", True), ("LONG", False)):
        rows = R._inv_base(POP, 3.0, 99, "10:30", direction)
        rows = [r for r in rows if R.BELOW.get(r["date"]) is below]
        if flat_aside:
            rows = [r for r in rows if R.LABELS.get(r["date"]) != "FLAT"]
        prow = R.split_years([R.norm("INV-LONG", r["date"], r["stock"],
                                     direction, r["entry_time"], r["net"])
                              for r in rows])
        pb = {yr: [t for t in books[yr] if t["comp"] not in ("INV-LONG", "INV-R3")]
              + prow[yr] for yr in (2025, 2026)}
        out.append(round(sum(t["net"] for yr in (2025, 2026)
                             for t in pb[yr]), 2))
    return out

for cyc, label, fa in (("R2-09", "INV merged rounds>=1, FLAT stand-aside ON", True),
                       ("R2-10", "INV merged rounds>=1, FLAT stand-aside OFF", False)):
    var_rows = merged_rows(fa)
    var_books = {yr: [t for t in books[yr]
                      if t["comp"] not in ("INV-LONG", "INV-R3")] + var_rows[yr]
                 for yr in (2025, 2026)}
    pl = merged_placebos(fa)
    out = R.gate(books, var_books, pl)
    R.record(cyc, label, out, note=f"placebos {pl}",
             extra={"merged_trades": {str(yr): len(var_rows[yr])
                                      for yr in var_rows}})
    if out["verdict"]:
        books = var_books
        R.save_books(books)
        print("    -> BANKED; incumbent updated")
print("INV cycles done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr] if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
