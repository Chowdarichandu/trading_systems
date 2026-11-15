#!/usr/bin/env python3
"""ROUND 12 — WS2: SINGLE-LEG FLAG RE-TESTS.

R12-03 (gate): the R5-03-clean swap applied verbatim to the
Round-11 ending book (ING.apply_r503: GAP-FADE -> the
>=1.25% DOWN+FLAT fade-LONG sleeve at 09:20, T125/S050;
GAP-FADE-INC retired). Birth record (R5-03, Round-4 book):
every leg true except (e). Placebos (the birth convention):
the same swap with the mirror sleeve (follow-SHORT >=1.25%)
and with the one-bar-late sleeve (fade >=1.25% at bar 2),
GAP-FADE-INC retired in both; full combined totals.
Timing 0 by construction: the gap signal completes at the
bar-0 open print (open vs prior close, printed 09:15);
entries at bar 1 (09:20) — the R4-L2-compliant form.

R12-04 (audit): the pre-registered screening arithmetic for
the single-leg flags NOT re-gated — every (c)-only flag is a
replacement/restriction whose 2026 delta vs the banked form
it displaces is negative by row identity, and every NE-REV
slot alternative is non-additive with the banked NU rows and
fails a delta leg as a slot swap. Printed from the anchored
builders; no candidate is scored.
"""
import sys, json, os
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r12_lib as R12
import stocks_engine_r9_ingredients as ING
import stocks_engine_r7_builders as B7

books = R12.load_books()
ing = ING.build_all()

# ------------------------------------------------------ R12-03 --
_done = set()
if os.path.exists(R12.RESULTS_PATH):
    _done = {r["cycle"] for r in json.load(open(R12.RESULTS_PATH))}
if "R12-03" in _done:
    print("R12-03 already recorded — skipped (idempotent re-run "
          "for R12-04).")
else:
    var = ING.apply_r503(books, ing)
    def swapped(rows_by_comp):
        return ING.without(R12.swap(books, "GAP-FADE",
                                    rows_by_comp),
                           "GAP-FADE-INC")
    pl = [R12.full_total(swapped(ing["sleeve125_mirror"])),
          R12.full_total(swapped(ing["sleeve125_late"]))]
    out = R12.gate(books, var, pl, timing_violations=0)
    failed = [k for k, v in out["legs"].items()
              if isinstance(v, bool) and not v]
    gf_old = {yr: round(sum(t["net"] for t in books[yr]
                            if t["comp"] in ("GAP-FADE",
                                             "GAP-FADE-INC")), 2)
              for yr in (2025, 2026)}
    gf_new = {yr: round(sum(t["net"] for t in ing["sleeve125"][yr]), 2)
              for yr in (2025, 2026)}
    R12.record(
        "R12-03",
        "R5-03-clean re-gated on the Round-11 ending book "
        "(GAP-FADE thr 1.25% swap, DOWN+FLAT, 09:20; "
        "GAP-FADE-INC retired)", out,
        note=f"banked fade rows replaced: GAP-FADE + GAP-FADE-INC "
             f"netting {gf_old[2025]} / {gf_old[2026]}; sleeve125 "
             f"anchored {gf_new[2025]} / {gf_new[2026]} on "
             f"{len(ing['sleeve125'][2025])}/"
             f"{len(ing['sleeve125'][2026])} rows. Birth record: "
             f"fails (e) only (R5-03). Placebos: mirror-swapped "
             f"book {pl[0]}; late-swapped book {pl[1]}. Timing "
             f"violations 0 (gap completes at the bar-0 open "
             f"print; entries at bar 1). Failed legs: {failed}.",
        extra={"fade_old": {str(k): v for k, v in gf_old.items()},
               "sleeve125": {str(k): v for k, v in gf_new.items()},
               "failed_legs": failed})

# ------------------------------------------------------ R12-04 --
cond = ING.build_cond()
nu_sa = {yr: round(sum(t["net"] for t in cond["notchup"]["real"][yr]), 2)
         for yr in (2025, 2026)}
assert nu_sa == {2025: 12596.19, 2026: 23744.40}, nu_sa

# (c)-only flags: 2026 net of the displacing form vs the
# banked form it would displace (REXP-DOWN T100/S065 banked
# at -5,899.72 Jan-Oct = full; all REXP rows are Jan-Oct).
rexp_fullpop, _, _, v_fp = B7.rexp_rows("SHORT", cells=None)
assert v_fp == 0
rexp_df, _, _, v_df = B7.rexp_rows("SHORT", cells={"DOWN", "FLAT"})
assert v_df == 0
sa = lambda rows: {yr: round(sum(t["net"] for t in rows[yr]), 2)
                   for yr in (2025, 2026)}
screen_c = {
    "R6-10 REXP full population T125/S050": sa(rexp_fullpop),
    "R7-02 REXP DOWN+FLAT T125/S050": sa(rexp_df),
    "R7-03/R8-07 REXP-DOWN T125/S050": sa(ing["rexp"]),
}
# R6-10's recorded +16,015.00 is its Jan-Oct figure; the full
# population carries Nov/Dec-2025 rows netting -1,605.46, so
# the full-year sum is +14,409.54. The 2026 figure (the leg
# the screen turns on) matches exactly. Assert both readings.
_jo_fp = {yr: round(sum(t["net"] for t in rexp_fullpop[yr]
                        if t["date"] <= f"{yr}-10-31"), 2)
          for yr in (2025, 2026)}
assert _jo_fp == {2025: 16015.00, 2026: -10286.95}, _jo_fp
assert screen_c["R6-10 REXP full population T125/S050"] == \
    {2025: 14409.54, 2026: -10286.95}, screen_c
assert screen_c["R7-02 REXP DOWN+FLAT T125/S050"] == \
    {2025: 12153.17, 2026: -10930.18}, screen_c
assert screen_c["R7-03/R8-07 REXP-DOWN T125/S050"] == \
    {2025: 14870.39, 2026: -8399.33}, screen_c
BANKED_REXP_2026 = -5899.72
c_lines = "; ".join(
    f"{k}: 2026 {v[2026]} vs banked form {BANKED_REXP_2026} "
    f"-> delta {round(v[2026] - BANKED_REXP_2026, 2)}"
    for k, v in screen_c.items())

# NE-REV slot alternatives: standalone full-year sums vs NU.
def cond_sa(name):
    return {yr: round(sum(t["net"] for t in cond[name]["real"][yr]), 2)
            for yr in (2025, 2026)}
r602, _, _, v_602, _ = B7.nerev_gen(
    signal_time="10:25", entry_time="10:35", thr=2.25,
    excl=B7.certified_exclusions()[0])
assert v_602 == 0
slot = {
    "NU (banked)": nu_sa,
    "R10-03 NOTCH": cond_sa("notch"),
    "R10-04 NOTCHCELL": None,   # computed below from R10-04 form
    "R9-07 IDXCELL": {yr: round(sum(t["net"] for t in
                                    cond["idxcell"]["real"][yr]), 2)
                      for yr in (2025, 2026)},
    "R6-02 thr 2.25 (CERT rebuild)": sa(r602),
}
# NOTCHCELL rows: the R10-04 / R11-04 construction verbatim —
# CERT rows admitted iff NOTCH passes AND the day's regime
# cell is DOWN or FLAT.
LABELS = R12.LABELS
def _ok_notchcell(day):
    if LABELS.get(day) not in ("DOWN", "FLAT"):
        return False
    return ING._state_ok_notch(day)
ncell = {yr: [t for t in ing["cert"][yr]
              if _ok_notchcell(t["date"]) is True]
         for yr in (2025, 2026)}
slot["R10-04 NOTCHCELL"] = sa(ncell)
assert slot["R10-04 NOTCHCELL"] == {2025: 6566.49, 2026: 27213.39}, \
    slot["R10-04 NOTCHCELL"]
# R6-04 (DOWN+FLAT cells on the birth population) is not
# rebuilt here: its recorded birth deltas (2025 JO +544.11)
# already sit below NU's 2025 standalone on any reading; it
# is named in the note from the flagged list, not re-derived.
slot_lines = "; ".join(
    f"{k}: {v[2025]} / {v[2026]}" for k, v in slot.items())
R12.record_audit(
    "R12-04",
    "WS2 screening arithmetic for the single-leg flags NOT "
    "re-gated (audit — no candidate scored)",
    f"(c)-only flags displace the banked REXP-DOWN T100/S065 "
    f"leg (2026 {BANKED_REXP_2026}): {c_lines}; R8-06 FADE-IDX "
    f"removes banked fade legs netting +2,477.24 in 2026 "
    f"(recorded) -> delta -2,477.24. Every (c)-only variant's "
    f"2026 delta is negative by row identity, so leg (c) "
    f"fails on ANY baseline — pre-refused, not scored. "
    f"NE-REV slot standalone full-year sums (2025 / 2026): "
    f"{slot_lines}. Every alternative is non-additive with "
    f"the banked NU rows (shared certified population); as "
    f"slot swaps, IDXCELL / NOTCHCELL / R6-02-CERT price 2025 "
    f"below NU's {nu_sa[2025]} (leg (b) fails arithmetically) "
    f"and NOTCH prices 2026 below NU's {nu_sa[2026]} (leg "
    f"(c) fails arithmetically); R6-04's recorded 2025 delta "
    f"(+544.11 JO) is below NU's on its face. Pre-refused, "
    f"not scored. R5-03-clean (R12-03) is the only flagged "
    f"ingredient whose sole failing leg is an interaction "
    f"leg on a disjoint family.",
    extra={"screen_c_only": {k: {str(y): v[y] for y in v}
                             for k, v in screen_c.items()},
           "slot_standalone": {k: {str(y): v[y] for y in v}
                               for k, v in slot.items()}})
print("WS2 done.")
