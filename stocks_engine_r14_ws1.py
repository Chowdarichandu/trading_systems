#!/usr/bin/env python3
"""ROUND 14 — R14-01 audit + WS1: F4 geometry neighbour (R14-02).

Anchor first (three-way): (i) f4_rows on the cached T150/S095
pop == the banked F4 rows; (ii) entry-bar re-scoring at the
book cell (1.50, 0.95) reproduces the banked nets exactly —
the replay flavour is IDENTIFIED by this anchor, not assumed;
(iii) re-scoring at (1.75, 0.95) reproduces f4_rows on the
cached T175/S095 pop exactly. Only then is the whole-sleeve
T175/S095 swap gated. Placebos: flipped / one-bar-late sets
at the candidate geometry (R13 swap convention).
"""
import sys, csv, pickle
from collections import Counter
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r14_lib as R14
import stocks_engine_r14_builders as B14
import stocks_engine_r2_lib as R

# ------------------------------------------------------- R14-01 --
raw = {}
for yr in (2025, 2026):
    rows = list(csv.DictReader(
        open(f"{WS}/stocks_engine_r13_book{yr}_trades.csv")))
    jo = round(sum(float(r["net"]) for r in rows
                   if r["date"] <= f"{yr}-10-31"), 2)
    full = round(sum(float(r["net"]) for r in rows), 2)
    raw[yr] = (len(rows), jo, full)
    assert jo == R14.JO_BASE[yr] and full == R14.FULL_BASE[yr], \
        (yr, jo, full)
    assert len(rows) == R14.ROWS_BASE[yr], (yr, len(rows))
books = R14.load_books()
jul = R14.month_net(books[2025], "2025-07")
oct_ = R14.month_net(books[2025], "2025-10")
assert jul == -2000.01, jul
assert oct_ == -3751.28, oct_
R14.record_audit(
    "R14-01", "Starting-book verification (Round-13 ending book)",
    f"Books re-summed from stocks_engine_r13_book{{2025,2026}}"
    f"_trades.csv: 2025 JO 103357.44 / full 103354.23 / 1105 "
    f"rows; 2026 JO 253068.45 / full 253068.45 / 1352 rows — "
    f"exact vs the Round-13 record. Red 2025 Jan-Oct months "
    f"asserted: Jul -2000.01, Oct -3751.28. No scoring "
    f"preceded this audit.")
print("R14-01 audit OK")

# ------------------------------------------------------- anchor --
def keyset(rows):
    return Counter(R14.row_id(t) for t in rows)

book_f4 = B14.comp_rows(books, "F4")
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
pop150 = R.f4_rows(cache["f4_1000_T150S095"], 0.5, 1.0,
                   excl_dir=True)
for yr in (2025, 2026):
    assert keyset(pop150[yr]) == keyset(book_f4[yr]), yr
print("anchor (i) OK: f4_rows(T150/S095 pop) == banked F4 rows")

pop175 = R.f4_rows(cache["f4_1000_T175S095"], 0.5, 1.0,
                   excl_dir=True)
flavour, real175, flip175, late175 = None, None, None, None
for fl in ("plain", "v2"):
    real, _f, _l, miss = B14.f4_geo(books, 1.50, 0.95, fl)
    if miss != 0 or not all(keyset(real[yr]) == keyset(book_f4[yr])
                            for yr in (2025, 2026)):
        continue
    r175, f175, l175, miss = B14.f4_geo(books, 1.75, 0.95, fl)
    if miss != 0 or not all(keyset(r175[yr]) == keyset(pop175[yr])
                            for yr in (2025, 2026)):
        continue
    flavour, real175, flip175, late175 = fl, r175, f175, l175
    break
assert flavour is not None, "no replay flavour reproduces F4"
print(f"anchor (ii)+(iii) OK: F4 rows are '{flavour}'-replay "
      f"rows — re-score exact at the book cell AND at T175/S095 "
      f"vs the cached pop (0 missing; the 8 Oct-29/30 rows score "
      f"from the forward root, per R6-L4)")

# ------------------------------------------------------ R14-02 --
sa = {yr: round(sum(t["net"] for t in real175[yr]), 2)
      for yr in (2025, 2026)}
jo = {yr: round(sum(t["net"] for t in real175[yr]
                    if t["date"] <= f"{yr}-10-31"), 2)
      for yr in (2025, 2026)}
base_sa = {yr: round(sum(t["net"] for t in book_f4[yr]), 2)
           for yr in (2025, 2026)}
var = R14.swap(books, "F4", real175)
pl = [R14.full_total(R14.swap(books, "F4", flip175)),
      R14.full_total(R14.swap(books, "F4", late175))]
out = R14.gate(books, var, pl, timing_violations=0)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
R14.record(
    "R14-02",
    "F4 geometry swap T150/S095 -> T175/S095 (target step only, "
    "whole sleeve)", out,
    note=f"Sleeve standalone {sa[2025]} / {sa[2026]} (JO "
         f"{jo[2025]} / {jo[2026]}) on {len(real175[2025])}/"
         f"{len(real175[2026])} rows vs the banked cell's "
         f"{base_sa[2025]} / {base_sa[2026]}. Anchors: pop, "
         f"re-score (flavour '{flavour}') and T175 cross-check "
         f"all exact. Placebos: flipped swap book {pl[0]}; "
         f"late swap book {pl[1]}. Timing violations 0 — the "
         f"population is the audited banked population; exits "
         f"only. Failed legs: {failed}.",
    extra={"sleeve_standalone": {str(k): v for k, v in sa.items()},
           "sleeve_jo": {str(k): v for k, v in jo.items()},
           "failed_legs": failed})
print("WS1 done.")
