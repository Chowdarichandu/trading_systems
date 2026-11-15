#!/usr/bin/env python3
"""ROUND 15 — WS1: the two frozen second steps.
R15-02 INV-ABOVE T150/S050 -> T175/S050 (target step only,
the direction R14-04 banked); R15-03 GAP-FADE family
T125/S065 -> T125/S080 (stop step only, both comps, the
direction R14-05 banked). Pre-registered in
stocks_engine_round15_2026-11-02.md before scoring.

Anchors asserted first: the chain pop at the BOOK geometry
(1.50, 0.50) under the current law + hard-dip exclusion
reproduces the Round-14 book's INV-ABOVE rows exactly
(exclusion drops 22 / 15, the R14 counts); round-1 entry
identity holds between the (1.50, 0.50) and (1.75, 0.50)
pops; gap_rows at the book cell (1.25, 0.65) reproduces
both fade comps' banked rows exactly. Placebos at the
candidate geometry: INV chain SHORT side (R2-25/26
precedent); fade mirror (follow) + one-bar-late books.
"""
import sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r15_lib as R15
import stocks_engine_r14_builders as B14

books = R15.load_books()

# ------------------------------------------------ R15-01 audit --
jul = R15.month_net(books[2025], "2025-07")
oct_ = R15.month_net(books[2025], "2025-10")
assert jul == -2733.21, jul
assert oct_ == -4152.19, oct_
R15.record_audit(
    "R15-01",
    "Starting-book verification (Round-14 ending book)",
    "Books re-summed from stocks_engine_r14_book{2025,2026}"
    "_trades.csv: 2025 JO 105987.24 / full 107589.18 / 1101 "
    "rows; 2026 JO 257300.30 / full 257300.30 / 1352 rows — "
    "exact vs the Round-14 record. Red 2025 Jan-Oct months "
    "asserted: Jul -2733.21, Oct -4152.19. No scoring "
    "preceded this audit.")

def keyset(rows):
    return Counter(R15.row_id(t) for t in rows)

# ------------------------------------------------------ anchors --
real_a0, _s0, dropped0 = B14.inv_above_geo(1.50, 0.50)
book_a = B14.comp_rows(books, "INV-ABOVE")
for yr in (2025, 2026):
    assert keyset(real_a0[yr]) == keyset(book_a[yr]), yr
assert dropped0 == {2025: 22, 2026: 15}, dropped0
print("anchor OK: INV-ABOVE law + hard-dip exclusion on the "
      "T150/S050 pop == banked INV-ABOVE rows (exclusion "
      "drops 22 / 15, the R14 counts)")

pop_b = B14.inv_pop(1.50, 0.50)
pop_c = B14.inv_pop(1.75, 0.50)
k_b = {(r["date"], r["stock"], r["entry_time"])
       for r in pop_b if r["round"] == 1}
k_c = {(r["date"], r["stock"], r["entry_time"])
       for r in pop_c if r["round"] == 1}
assert k_b == k_c, "INV round-1 identity mismatch across geometries"
print("anchor OK: INV round-1 entry identity holds between "
      "the T150 and T175 pops (chain picks are exit-blind)")

fg0 = B14.fade_geo(1.25, 0.65)
for comp in ("GAP-FADE", "GAP-FADE-INC"):
    bk = B14.comp_rows(books, comp)
    for yr in (2025, 2026):
        assert keyset(fg0[comp]["real"][yr]) == keyset(bk[yr]), \
            (comp, yr)
print("anchor OK: gap_rows at T125/S065 == banked GAP-FADE "
      "and GAP-FADE-INC rows")

# ------------------------------------------------------ R15-02 --
real_a, side_a, dropped = B14.inv_above_geo(1.75, 0.50)
sa = {yr: round(sum(t["net"] for t in real_a[yr]), 2)
      for yr in (2025, 2026)}
jo_a = {yr: round(sum(t["net"] for t in real_a[yr]
                      if t["date"] <= f"{yr}-10-31"), 2)
        for yr in (2025, 2026)}
base_sa = {yr: round(sum(t["net"] for t in book_a[yr]), 2)
           for yr in (2025, 2026)}
var = R15.swap(books, "INV-ABOVE", real_a)
pl = [R15.full_total(R15.swap(books, "INV-ABOVE", side_a))]
out = R15.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R15.record(
    "R15-02",
    "INV-ABOVE geometry swap T150/S050 -> T175/S050 (target "
    "step only, second step in the R14-04 direction)", out,
    note=f"Sleeve standalone {sa[2025]} / {sa[2026]} (JO "
         f"{jo_a[2025]} / {jo_a[2026]}) on {len(real_a[2025])}/"
         f"{len(real_a[2026])} rows vs the banked cell's "
         f"{base_sa[2025]} / {base_sa[2026]}. Population "
         f"re-formed at the candidate geometry under the "
         f"incumbent law; the R12-02 hard-dip exclusion "
         f"re-applied to the new rows drops {dropped[2025]} / "
         f"{dropped[2026]} rows (book cell: 22 / 15). Placebo: "
         f"SHORT-side swap book {pl[0]} (chain's own opposite "
         f"side at the candidate geometry, R2-25/26 "
         f"precedent). Timing violations 0 — run_chain picks "
         f"never read exit outcomes; round-1 identity "
         f"asserted. Failed legs: {failed}.",
    extra={"sleeve_standalone": {str(k): v for k, v in sa.items()},
           "sleeve_jo": {str(k): v for k, v in jo_a.items()},
           "failed_legs": failed})

# ------------------------------------------------------ R15-03 --
fg = B14.fade_geo(1.25, 0.80)
def swap2(bk, sets, kind):
    out = R15.swap(bk, "GAP-FADE", sets["GAP-FADE"][kind])
    return R15.swap(out, "GAP-FADE-INC",
                    sets["GAP-FADE-INC"][kind])
var = swap2(books, fg, "real")
pl = [R15.full_total(swap2(books, fg, "flip")),
      R15.full_total(swap2(books, fg, "late"))]
out = R15.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
sa = {c: {yr: round(sum(t["net"] for t in fg[c]["real"][yr]), 2)
          for yr in (2025, 2026)}
      for c in ("GAP-FADE", "GAP-FADE-INC")}
base_sa = {c: {yr: round(sum(t["net"]
                             for t in B14.comp_rows(books, c)[yr]), 2)
               for yr in (2025, 2026)}
           for c in ("GAP-FADE", "GAP-FADE-INC")}
R15.record(
    "R15-03",
    "GAP-FADE family geometry swap T125/S065 -> T125/S080 "
    "(stop step only, both comps, second step in the R14-05 "
    "direction)", out,
    note=f"Sleeve standalone: GAP-FADE {sa['GAP-FADE'][2025]} / "
         f"{sa['GAP-FADE'][2026]} (banked cell "
         f"{base_sa['GAP-FADE'][2025]} / "
         f"{base_sa['GAP-FADE'][2026]}); GAP-FADE-INC "
         f"{sa['GAP-FADE-INC'][2025]} / "
         f"{sa['GAP-FADE-INC'][2026]} (banked cell "
         f"{base_sa['GAP-FADE-INC'][2025]} / "
         f"{base_sa['GAP-FADE-INC'][2026]}). Placebos: mirror "
         f"(follow) swap book {pl[0]}; one-bar-late swap book "
         f"{pl[1]}. Timing violations 0 — entries are the "
         f"banked ones; exits only. Failed legs: {failed}.",
    extra={"sleeve_standalone": sa,
           "failed_legs": failed})
print("WS1 done.")
