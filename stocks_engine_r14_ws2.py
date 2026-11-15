#!/usr/bin/env python3
"""ROUND 14 — WS2: INV geometry neighbours (R14-03 INV-LONG,
R14-04 INV-ABOVE), each T125/S050 -> T150/S050 (target step
only).

Populations are re-formed by run_chain at the candidate
geometry under the current law (INV-LONG: ADR >= 3.0, rounds
<= 3, entry < 11:00, FLAT stand-aside; INV-ABOVE: ADR >= 3.0,
rounds <= 2, entry < 10:30, PLUS the R12-02 hard-dip
exclusion re-applied to the new rows). Anchors asserted
first: the cached T125/S050 pop under the same law (plus the
exclusion) reproduces each comp's banked rows exactly, the
exclusion drops the R12 census counts (23 / 16), and round-1
entry identity holds across geometries (run_chain picks never
read exit outcomes — the r2_cells capture note). Placebo:
the chain's SHORT side at the candidate geometry under the
same law (R2-25/26 precedent).
"""
import sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r14_lib as R14
import stocks_engine_r14_builders as B14

books = R14.load_books()

def keyset(rows):
    return Counter(R14.row_id(t) for t in rows)

# ------------------------------------------------------- anchors --
real_l0, _s = B14.inv_long_geo(1.25, 0.50)
book_l = B14.comp_rows(books, "INV-LONG")
for yr in (2025, 2026):
    assert keyset(real_l0[yr]) == keyset(book_l[yr]), yr
print("anchor OK: INV-LONG law on the T125/S050 pop == banked "
      "INV-LONG rows")

real_a0, _s2, dropped0 = B14.inv_above_geo(1.25, 0.50)
book_a = B14.comp_rows(books, "INV-ABOVE")
for yr in (2025, 2026):
    assert keyset(real_a0[yr]) == keyset(book_a[yr]), yr
assert dropped0 == {2025: 23, 2026: 16}, dropped0
print("anchor OK: INV-ABOVE law + hard-dip exclusion on the "
      "T125/S050 pop == banked INV-ABOVE rows (exclusion drops "
      "23 / 16, the R12 census counts)")

pop_b = B14.inv_pop(1.25, 0.50)
pop_c = B14.inv_pop(1.50, 0.50)
k_b = {(r["date"], r["stock"], r["entry_time"])
       for r in pop_b if r["round"] == 1}
k_c = {(r["date"], r["stock"], r["entry_time"])
       for r in pop_c if r["round"] == 1}
assert k_b == k_c, "INV round-1 identity mismatch across geometries"
print("anchor OK: INV round-1 entry identity holds across "
      "geometries (chain picks are exit-blind)")

# ------------------------------------------------------ R14-03 --
def gate_inv(cycle, comp, real, side, base_rows, extra_note):
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    jo = {yr: round(sum(t["net"] for t in real[yr]
                        if t["date"] <= f"{yr}-10-31"), 2)
          for yr in (2025, 2026)}
    base_sa = {yr: round(sum(t["net"] for t in base_rows[yr]), 2)
               for yr in (2025, 2026)}
    var = R14.swap(books, comp, real)
    pl = [R14.full_total(R14.swap(books, comp, side))]
    out = R14.gate(books, var, pl, timing_violations=0)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    R14.record(
        cycle,
        f"{comp} geometry swap T125/S050 -> T150/S050 (target "
        f"step only)", out,
        note=f"Sleeve standalone {sa[2025]} / {sa[2026]} (JO "
             f"{jo[2025]} / {jo[2026]}) on {len(real[2025])}/"
             f"{len(real[2026])} rows vs the banked cell's "
             f"{base_sa[2025]} / {base_sa[2026]}. {extra_note} "
             f"Placebo: SHORT-side swap book {pl[0]} (chain's "
             f"own opposite side at the candidate geometry, "
             f"R2-25/26 precedent). Timing violations 0 — "
             f"run_chain picks never read exit outcomes; "
             f"round-1 identity asserted. Failed legs: "
             f"{failed}.",
        extra={"sleeve_standalone": {str(k): v
                                     for k, v in sa.items()},
               "sleeve_jo": {str(k): v for k, v in jo.items()},
               "failed_legs": failed})
    return out

real_l, side_l = B14.inv_long_geo(1.50, 0.50)
gate_inv("R14-03", "INV-LONG", real_l, side_l, book_l,
         "Population re-formed at the candidate geometry "
         "under the R2-07 law (rounds <= 3, < 11:00).")

# ------------------------------------------------------ R14-04 --
real_a, side_a, dropped = B14.inv_above_geo(1.50, 0.50)
gate_inv("R14-04", "INV-ABOVE", real_a, side_a, book_a,
         f"Population re-formed at the candidate geometry "
         f"under the incumbent law; the R12-02 hard-dip "
         f"exclusion re-applied to the new rows drops "
         f"{dropped[2025]} / {dropped[2026]} rows (book cell: "
         f"23 / 16). This cell decomposes the flagged R2-26 "
         f"swap (T150/S080): the wider target at the "
         f"incumbent stop.")
print("WS2 done.")
