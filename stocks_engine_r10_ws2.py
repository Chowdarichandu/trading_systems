#!/usr/bin/env python3
"""ROUND 10 — WS2: NE-REV-NOTCHCELL standalone (R10-04).

The composed form frozen in the Round-10 pre-registration
(R10-01 verified the literal set-combinations of IDXCELL and
NOTCH collapse to already-gated forms): CERT rows admitted iff
NOTCH passes (NIFTY 10:25 move not in (-0.30%, 0)) AND the
trade day's frozen regime cell is DOWN or FLAT. Built by
filtering the anchored CERT / flipped / late rows on the
composed date-level condition — state depends only on the
trade date, so all three row sets filter identically.
State-unknown dates are counted and never admitted.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r10_lib as R10
import stocks_engine_r9_ingredients as ING

books = R10.load_books()
ing = ING.build_all()
viol = ing["viol_c"]
assert viol == 0, viol
LABELS = R10.LABELS

def ok_notchcell(day):
    if LABELS.get(day) not in ("DOWN", "FLAT"):
        return False
    ok = ING._state_ok_notch(day)
    return ok            # True / False / None (unknown)

def filt(rows):
    kept = {2025: [], 2026: []}
    unknown = 0
    for yr in (2025, 2026):
        for t in rows[yr]:
            ok = ok_notchcell(t["date"])
            if ok is None:
                unknown += 1
            elif ok:
                kept[yr].append(dict(t, comp="NE-REV-NOTCHCELL"))
    return kept, unknown

real, unk_r = filt(ing["cert"])
flip, _ = filt(ing["cert_f"])
late, _ = filt(ing["cert_l"])
COMP = "NE-REV-NOTCHCELL"

# distinctness vs the already-gated forms, verified in code
nu_ids = {yr: {R10.row_id(t)
               for t in ING.build_cond()["notchup"]["real"][yr]}
          for yr in (2025, 2026)}
idxcell_ids = {yr: {R10.row_id(t)
                    for t in ING.build_cond()["idxcell"]["real"][yr]}
               for yr in (2025, 2026)}
nc_ids = {yr: {R10.row_id(t) for t in real[yr]} for yr in (2025, 2026)}
for yr in (2025, 2026):
    assert idxcell_ids[yr] < nc_ids[yr], (yr, "idxcell not proper "
                                          "subset of notchcell")
    assert nc_ids[yr] != nu_ids[yr], (yr, "notchcell == NU")

var = R10.add_comp(books, COMP, real)
pl = [R10.full_total(R10.add_comp(books, COMP, flip)),
      R10.full_total(R10.add_comp(books, COMP, late))]
out = R10.gate(books, var, pl, timing_violations=viol)
failed = [k for k, v in out["legs"].items()
          if isinstance(v, bool) and not v]
sa = {yr: round(sum(t["net"] for t in real[yr]), 2)
      for yr in (2025, 2026)}
R10.record(
    "R10-04",
    "NE-REV-NOTCHCELL standalone (NOTCH x DOWN+FLAT-cell "
    "restriction on the CERT population)", out,
    note=f"composed form standalone: {sa[2025]} (2025) / "
         f"{sa[2026]} (2026) on {len(real[2025])}/"
         f"{len(real[2026])} rows of CERT 291/370; "
         f"state-unknown rows dropped {unk_r} (counted, never "
         f"guessed). Distinctness verified in code: IDXCELL is "
         f"a proper subset in both years and the form differs "
         f"from NE-REV-NU's row set in both years. Placebos "
         f"(identical composed condition): flipped book "
         f"{pl[0]}; one-bar-late book {pl[1]}. Timing "
         f"violations {viol}. Failed legs: {failed}.",
    extra={"standalone": {str(k): v for k, v in sa.items()},
           "population_trades": {"2025": len(real[2025]),
                                 "2026": len(real[2026])},
           "failed_legs": failed})
print("WS2 done.")
