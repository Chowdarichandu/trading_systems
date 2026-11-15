#!/usr/bin/env python3
"""ROUND 14 — WS3: GAP-FADE family geometry neighbour
(R14-05, T125/S050 -> T125/S065, both comps) and N4-V3
geometry swap (R14-06, T150/S080 -> T125/S050, the November
scorecard cell).

Anchors asserted first: gap_rows at the book cell reproduces
both fade comps' banked rows exactly; the parameterised N4
builder at (1.50, 0.80) — thr 0.8%, std entry, full law +
FLOOR-2 cap, minus the four R6-11 voided signals —
reproduces the banked N4 rows exactly. Placebos at the
candidate geometry: fade mirror (follow) + one-bar-late
books; N4 flipped + one-bar-late (09:35-close entry) books.
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

# ------------------------------------------------------ R14-05 --
fg0 = B14.fade_geo(1.25, 0.50)
for comp in ("GAP-FADE", "GAP-FADE-INC"):
    bk = B14.comp_rows(books, comp)
    for yr in (2025, 2026):
        assert keyset(fg0[comp]["real"][yr]) == keyset(bk[yr]), \
            (comp, yr)
print("anchor OK: gap_rows at T125/S050 == banked GAP-FADE "
      "and GAP-FADE-INC rows")

fg = B14.fade_geo(1.25, 0.65)
def swap2(bk, sets, kind):
    out = R14.swap(bk, "GAP-FADE", sets["GAP-FADE"][kind])
    return R14.swap(out, "GAP-FADE-INC",
                    sets["GAP-FADE-INC"][kind])
var = swap2(books, fg, "real")
pl = [R14.full_total(swap2(books, fg, "flip")),
      R14.full_total(swap2(books, fg, "late"))]
out = R14.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
sa = {c: {yr: round(sum(t["net"] for t in fg[c]["real"][yr]), 2)
          for yr in (2025, 2026)}
      for c in ("GAP-FADE", "GAP-FADE-INC")}
base_sa = {c: {yr: round(sum(t["net"]
                             for t in B14.comp_rows(books, c)[yr]), 2)
               for yr in (2025, 2026)}
           for c in ("GAP-FADE", "GAP-FADE-INC")}
R14.record(
    "R14-05",
    "GAP-FADE family geometry swap T125/S050 -> T125/S065 "
    "(stop step only, both comps)", out,
    note=f"Sleeve standalone: GAP-FADE {sa['GAP-FADE'][2025]} / "
         f"{sa['GAP-FADE'][2026]} (banked cell "
         f"{base_sa['GAP-FADE'][2025]} / "
         f"{base_sa['GAP-FADE'][2026]}); GAP-FADE-INC "
         f"{sa['GAP-FADE-INC'][2025]} / "
         f"{sa['GAP-FADE-INC'][2026]} (banked cell "
         f"{base_sa['GAP-FADE-INC'][2025]} / "
         f"{base_sa['GAP-FADE-INC'][2026]}). Cell chosen by "
         f"the frozen excursion diagnostic (stop-axis rough "
         f"swing +12,157.87 vs target-axis -1,556.33; "
         f"stocks_engine_r14_diag.py). Placebos: mirror "
         f"(follow) swap book {pl[0]}; one-bar-late swap book "
         f"{pl[1]}. Timing violations 0 — entries are the "
         f"banked ones; exits only. Failed legs: {failed}.",
    extra={"sleeve_standalone": sa,
           "failed_legs": failed})

# ------------------------------------------------------ R14-06 --
real0, _f0, _l0 = B14.n4_geo(1.50, 0.80)
book_n4 = B14.comp_rows(books, "N4-V3")
for yr in (2025, 2026):
    assert keyset(real0[yr]) == keyset(book_n4[yr]), yr
print("anchor OK: parameterised N4 at T150/S080 (thr 0.8%, "
      "law + cap, voids removed) == banked N4-V3 rows "
      f"({len(real0[2025])}/{len(real0[2026])} rows)")

real, flip, late = B14.n4_geo(1.25, 0.50)
sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
jo = {yr: round(sum(t["net"] for t in real[yr]
                    if t["date"] <= f"{yr}-10-31"), 2)
      for yr in (2025, 2026)}
base_sa = {yr: round(sum(t["net"] for t in book_n4[yr]), 2)
           for yr in (2025, 2026)}
var = R14.swap(books, "N4-V3", real)
pl = [R14.full_total(R14.swap(books, "N4-V3", flip)),
      R14.full_total(R14.swap(books, "N4-V3", late))]
out = R14.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R14.record(
    "R14-06",
    "N4-V3 geometry swap T150/S080 -> T125/S050 (the November "
    "scorecard cell)", out,
    note=f"Sleeve standalone {sa[2025]} / {sa[2026]} (JO "
         f"{jo[2025]} / {jo[2026]}) on {len(real[2025])}/"
         f"{len(real[2026])} rows vs the banked cell's "
         f"{base_sa[2025]} / {base_sa[2026]}. Population: the "
         f"current one (thr 0.8%, law + FLOOR-2 cap, four "
         f"R6-11 voids removed in every set). Placebos: "
         f"flipped swap book {pl[0]}; one-bar-late (09:35-"
         f"close entry) swap book {pl[1]}. Timing violations "
         f"0. Failed legs: {failed}.",
    extra={"sleeve_standalone": {str(k): v for k, v in sa.items()},
           "sleeve_jo": {str(k): v for k, v in jo.items()},
           "failed_legs": failed})
print("WS3 done.")
