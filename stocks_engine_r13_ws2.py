#!/usr/bin/env python3
"""ROUND 13 — WS2: REXP geometry neighbours (swaps).

The banked REXP sleeve (comp REXP: SHORT, DOWN cells, entry
10:20) wears T100/S065. Anchor first: rexp_geo at the frozen
cell must reproduce the banked rows exactly (multiset identity
on date/stock/dir/entry_time/net + Jan-Oct sums +10,243.45 /
-5,899.72). Then R13-04 gates the T125/S065 swap and R13-05
the T100/S050 swap, each replacing the banked rows whole-book.
Placebos: the same swap with the flipped / late row sets at
the candidate geometry.
"""
import sys
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r13_lib as R13
import stocks_engine_r8_builders as B8

books = R13.load_books()

def keyset(rows):
    return Counter(R13.row_id(t) for t in rows)

# ------------------------------------------------------- anchor --
real0, flip0, late0, viol0 = B8.rexp_geo("SHORT", cells={"DOWN"},
                                         tgt=1.00, stp=0.65)
assert viol0 == 0, viol0
for yr in (2025, 2026):
    banked = [t for t in books[yr] if t["comp"] == "REXP"]
    assert keyset(banked) == keyset(real0[yr]), yr
    jo = round(sum(t["net"] for t in real0[yr]
                   if t["date"] <= f"{yr}-10-31"), 2)
    assert jo == {2025: 10243.45, 2026: -5899.72}[yr], (yr, jo)
print("anchor OK: rexp_geo T100/S065 reproduces the banked "
      "REXP rows exactly (41/86 rows; JO +10,243.45 / -5,899.72)")

# ------------------------------------------------------ swaps ----
def gate_swap(cycle, tgt, stp):
    real, flip, late, viol = B8.rexp_geo("SHORT", cells={"DOWN"},
                                         tgt=tgt, stp=stp)
    assert viol == 0, viol
    sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
          for yr in (2025, 2026)}
    jo = {yr: round(sum(t["net"] for t in real[yr]
                        if t["date"] <= f"{yr}-10-31"), 2)
          for yr in (2025, 2026)}
    var = R13.swap(books, "REXP", real)
    pl = [R13.full_total(R13.swap(books, "REXP", flip)),
          R13.full_total(R13.swap(books, "REXP", late))]
    out = R13.gate(books, var, pl, timing_violations=viol)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    R13.record(
        cycle,
        f"REXP-DOWN geometry swap T{int(tgt*100):03d}/"
        f"S{int(stp*100):03d} (banked cell T100/S065)", out,
        note=f"Sleeve standalone {sa[2025]} / {sa[2026]} (JO "
             f"{jo[2025]} / {jo[2026]}) on {len(real[2025])}/"
             f"{len(real[2026])} rows vs the banked cell's JO "
             f"+10,243.45 / -5,899.72. Placebos: flipped swap "
             f"book {pl[0]}; late swap book {pl[1]}. Timing "
             f"violations {viol}. Failed legs: {failed}.",
        extra={"sleeve_standalone": {str(k): v
                                     for k, v in sa.items()},
               "sleeve_jo": {str(k): v for k, v in jo.items()},
               "failed_legs": failed})
    return out

gate_swap("R13-04", 1.25, 0.65)
gate_swap("R13-05", 1.00, 0.50)
print("WS2 done.")
