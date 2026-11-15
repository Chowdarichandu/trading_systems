#!/usr/bin/env python3
"""ROUND 6 — WS0: TRIPLE-COMBINATION DECISION SUPPORT (R6-01).

Gates R2-26 + R5-03 + R5-07 together on the Round-5 ending book,
whole-book, all nine legs + leg (x). NOT a banking: recorded with
force_no_bank regardless of verdict — adoption is Chandu's.

Ingredients (exact prior constructions):
  R2-26: swap INV-ABOVE rows for the cached T150/S080 population.
  R5-03: swap GAP-FADE rows for the >=1.25% DOWN+FLAT sleeve.
  R5-07: add NE-REV LONG rows (thr 2.0, entry 10:35, T100/S065).
Every ingredient is re-anchored on THIS base to its recorded Jan-Oct
totals before the combination is scored (the R4-01 / R5-15 discipline):
  R2-26 -> 2025 JO 85,340.57 / 2026 JO 2,27,415.67 (R4-10)
  R5-03 -> 2025 JO 88,401.23 / 2026 JO 2,26,071.55 (R5-03)
  R5-07 -> 2025 JO 90,121.11 / 2026 JO 2,47,599.90 (R5-07)
Placebos (frozen in the Round-6 pre-registration):
  P1 all-placebo: SHORT-side T150 swap + gap mirror in the GAP-FADE
     slot + NE-REV opposite direction.
  P2 real swaps + NE-REV one bar late.
  P3 real R2-26 + gap sleeve one bar late + real NE-REV.
"""
import sys, pickle
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r6_lib as R6
import stocks_engine_r6_builders as B

books = R6.load_books()

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

# ---------------------------------------------------------- ingredients
cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
POP150 = cache["inv_pop_T150S080"]
above150 = R.inv_above_rows(POP150)
above150_short = R.split_years([R.norm(
    "INV-ABOVE", r["date"], r["stock"], r["direction"], r["entry_time"],
    r["net"]) for r in R.inv_side_rows(POP150, "SHORT", below=False,
                                       flat_aside=False)])

sleeve125 = B.gap_rows("fade", 1.25, 1, 1.25, 0.5, only_dir="LONG",
                       cells={"DOWN", "FLAT"})
sleeve125_mirror = B.gap_rows("follow", 1.25, 1, 1.25, 0.5,
                              only_dir="SHORT", cells={"DOWN", "FLAT"})
sleeve125_late = B.gap_rows("fade", 1.25, 2, 1.25, 0.5, only_dir="LONG",
                            cells={"DOWN", "FLAT"})

nerev, nerev_flip, nerev_late, viol = B.nerev_rows(2.0, "10:35", None)
assert viol == 0, viol
nerev = {yr: [dict(t, comp="NE-REV-LONG") for t in nerev[yr]]
         for yr in nerev}
nerev_flip = {yr: [dict(t, comp="NE-REV-SHORT") for t in nerev_flip[yr]]
              for yr in nerev_flip}
nerev_late = {yr: [dict(t, comp="NE-REV-LONG") for t in nerev_late[yr]]
              for yr in nerev_late}

# -------------------------------------------------------------- anchors
sa = {yr: round(sum(t["net"] for t in nerev[yr]), 2) for yr in (2025, 2026)}
assert sa == {2025: 12209.45, 2026: 24306.56}, sa
assert (len(nerev[2025]), len(nerev[2026])) == (303, 388)
print("R5-07 anchor OK (standalone +12,209.45 / +24,306.56; 303/388 rows)")

var_r226 = R6.swap(books, "INV-ABOVE", above150)
assert (jo(var_r226, 2025), jo(var_r226, 2026)) == (85340.57, 227415.67), \
    (jo(var_r226, 2025), jo(var_r226, 2026))
print("R2-26 anchor OK (2025 JO 85,340.57 / 2026 JO 2,27,415.67)")

var_r503 = R6.swap(books, "GAP-FADE", sleeve125)
assert (jo(var_r503, 2025), jo(var_r503, 2026)) == (88401.23, 226071.55), \
    (jo(var_r503, 2025), jo(var_r503, 2026))
ss = {yr: round(sum(t["net"] for t in sleeve125[yr]), 2)
      for yr in (2025, 2026)}
assert ss == {2025: 32064.93, 2026: 4270.42}, ss
print("R5-03 anchor OK (2025 JO 88,401.23 / 2026 JO 2,26,071.55; sleeve "
      "standalone +32,064.93 / +4,270.42)")

var_r507 = R6.add_comp(books, "NE-REV-LONG", nerev)
assert (jo(var_r507, 2025), jo(var_r507, 2026)) == (90121.11, 247599.90)
print("R5-07 book anchor OK (2025 JO 90,121.11 / 2026 JO 2,47,599.90)")

# ---------------------------------------------------------- combination
combo = R6.add_comp(var_r503_swapped := R6.swap(var_r226, "GAP-FADE",
                                                sleeve125),
                    "NE-REV-LONG", nerev)

base_no_fade = without(books, "GAP-FADE")
p1 = R6.add_comp(R6.add_comp(R6.swap(books, "INV-ABOVE", above150_short),
                             "GAP-FOLLOW", sleeve125_mirror),
                 "NE-REV-SHORT", nerev_flip)
p1 = {yr: [t for t in p1[yr] if t["comp"] != "GAP-FADE"]
      for yr in (2025, 2026)}
p2 = R6.add_comp(R6.swap(var_r226, "GAP-FADE", sleeve125),
                 "NE-REV-LONG", nerev_late)
p3 = R6.add_comp(R6.swap(var_r226, "GAP-FADE", sleeve125_late),
                 "NE-REV-LONG", nerev)
pl = [R6.full_total(p1), R6.full_total(p2), R6.full_total(p3)]

out = R6.gate(books, combo, pl, timing_violations=viol)
exp25 = round(77806.57 + 7534.00 + 10594.66 + 12314.54, 2)
exp26 = round(223293.34 + 4122.33 + 2778.21 + 24306.56, 2)
got25, got26 = jo(combo, 2025), jo(combo, 2026)
R6.record("R6-01",
          "DECISION SUPPORT: TRIPLE — R2-26 (INV-ABOVE T150/S080) + "
          "R5-03 (gap-fade thr 1.25% swap) + R5-07 (NE-REV LONG), gated "
          "whole — NOT a banking", out,
          note=f"ingredients re-anchored to the paisa on this base "
               f"before scoring. Purely-additive expectation: 2025 JO "
               f"{exp25} / 2026 JO {exp26}; actual: {got25} / {got26} "
               f"(additive: {got25 == exp25 and got26 == exp26}). "
               f"2025 pace if adopted: Rs{round(got25/10, 2)}/month; "
               f"gap would fall to Rs{round(150000 - got25, 2)}. "
               f"Placebos: P1 all-placebo {pl[0]}; P2 swaps + NE-REV "
               f"late {pl[1]}; P3 R2-26 + sleeve late + NE-REV {pl[2]}. "
               f"Timing violations {viol} (gap entries bar>=1 after the "
               f"bar-0 print; NE-REV entries 10:35 strictly after the "
               f"10:25 signal bar, counted in code). Adoption is "
               f"Chandu's; nothing banked here regardless of verdict.",
          extra={"expected_if_additive": {"2025_JO": exp25,
                                          "2026_JO": exp26},
                 "actual": {"2025_JO": got25, "2026_JO": got26}},
          force_no_bank=True)
print("WS0 done. Triple 2025 JO:", got25, "| 2026 JO:", got26,
      "| pace 2025:", round(got25 / 10, 2), "/mo | gap:",
      round(150000 - got25, 2))
