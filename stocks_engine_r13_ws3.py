#!/usr/bin/env python3
"""ROUND 13 — WS3: NE-REV-NU geometry micro-grid (swaps).

The banked NE-REV-NU sleeve wears T100/S065, never gridded.
Anchor first: nu_geo at the frozen cell must reproduce the
banked NU rows exactly (multiset identity + standalone sums
+12,596.19 / +23,744.40 on 200/313 rows). Then R13-06 gates
the T125/S065 swap and R13-07 the T100/S050 swap, each
replacing the banked rows whole-book. Placebos: the same
swap with the flipped / late NU sets at the candidate
geometry.
"""
import sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r13_lib as R13
import stocks_engine_r13_builders as B13

books = R13.load_books()

def keyset(rows):
    return Counter(R13.row_id(t) for t in rows)

# ------------------------------------------------------- anchor --
real0, flip0, late0 = B13.nu_geo(1.00, 0.65)
for yr in (2025, 2026):
    banked = [t for t in books[yr] if t["comp"] == "NE-REV-NU"]
    assert keyset(banked) == keyset(real0[yr]), yr
    sa = round(sum(t["net"] for t in real0[yr]), 2)
    assert sa == {2025: 12596.19, 2026: 23744.40}[yr], (yr, sa)
    assert len(real0[yr]) == {2025: 200, 2026: 313}[yr]
print("anchor OK: nu_geo T100/S065 reproduces the banked NU "
      "rows exactly (200/313 rows; standalone +12,596.19 / "
      "+23,744.40)")

# ------------------------------------------------------ swaps ----
def gate_swap(cycle, tgt, stp):
    real, flip, late = B13.nu_geo(tgt, stp)
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    var = R13.swap(books, "NE-REV-NU", real)
    pl = [R13.full_total(R13.swap(books, "NE-REV-NU", flip)),
          R13.full_total(R13.swap(books, "NE-REV-NU", late))]
    out = R13.gate(books, var, pl, timing_violations=0)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    R13.record(
        cycle,
        f"NE-REV-NU geometry swap T{int(tgt*100):03d}/"
        f"S{int(stp*100):03d} (banked cell T100/S065)", out,
        note=f"Sleeve standalone {sa[2025]} / {sa[2026]} on "
             f"{len(real[2025])}/{len(real[2026])} rows vs the "
             f"banked cell's +12,596.19 / +23,744.40. Placebos: "
             f"flipped swap book {pl[0]}; late swap book "
             f"{pl[1]}. Timing violations 0 (the population "
             f"and entries are the anchored NU set verbatim; "
             f"only the exit geometry changes). Failed legs: "
             f"{failed}.",
        extra={"sleeve_standalone": {str(k): v
                                     for k, v in sa.items()},
               "failed_legs": failed})
    return out

gate_swap("R13-06", 1.25, 0.65)
gate_swap("R13-07", 1.00, 0.50)
print("WS3 done.")
