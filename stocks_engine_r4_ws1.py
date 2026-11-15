#!/usr/bin/env python3
"""ROUND 4 — WS1: COMBINED FLAGS, GATED WHOLE (decision support only).

Applies BOTH flagged variants to the Round-2 ending book as ONE candidate:
  R2-26: INV-ABOVE exits T150/S080 (swap, inv_above_rows on the cached
         T150/S080 INV population — the exact Round-2 construction).
  R3-10: GAP-FADE LONG-only >=1.5% sleeve (add — the exact Round-3
         construction: entry 09:20 open, T125/S050).
Neither variant is adopted by this script even if the combination passes:
both await Chandu's decision, so the gate result is recorded with
banked=False (decision_support_only). The question answered: does the
interaction differ from the sum of the two deltas?

Ingredient anchors are verified to the paisa BEFORE the combination is
scored (deltas vs the current base must reproduce the recorded ones):
  R2-26: 2025 JO +7,534.00; gate-combined +13,089.83.
  R3-10: 2025 JO +26,979.39; 2026 JO -4,080.76; gate-combined +22,084.79.

Pre-registered placebos for the combination (combined totals):
  P1 both-placebo: INV-ABOVE SHORT-side T150 swap + GAP-FOLLOW SHORT-only.
  P2 R2-26 real + GAP-FADE LONG one bar late (entry 09:25).
  P3 INV-ABOVE SHORT-side swap + GAP-FADE LONG one bar late.
"""
import sys, pickle
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r4_lib as R4

books = R4.load_books()
base_jo = {yr: round(sum(t["net"] for t in books[yr]
                         if t["date"] <= f"{yr}-10-31"), 2)
           for yr in (2025, 2026)}
assert base_jo == {2025: 56336.30, 2026: 221801.13}, base_jo
assert (len(books[2025]), len(books[2026])) == (776, 680)
print("base anchors OK:", base_jo, "full combined:",
      R4.full_total(books))

cache = pickle.load(open(f"{WS}/r2_cache.pkl", "rb"))
POP150 = cache["inv_pop_T150S080"]
above150 = R.inv_above_rows(POP150)
above150_short = R.split_years([R.norm(
    "INV-ABOVE", r["date"], r["stock"], r["direction"], r["entry_time"],
    r["net"]) for r in R.inv_side_rows(POP150, "SHORT", below=False,
                                       flat_aside=False)])

g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
SYMBOLS = g["SYMBOLS"]
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            bars = spot.get(day, [])
            if len(bars) <= entry_bar:
                continue
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            gap = (bars[0]["open"] / prev_close - 1) * 100
            if abs(gap) < thr:
                continue
            natural = "LONG" if gap > 0 else "SHORT"
            direction = natural if mode == "follow" else (
                "SHORT" if natural == "LONG" else "LONG")
            if only_dir and direction != only_dir:
                continue
            entry = bars[entry_bar]["open"]
            r = replay(bars, entry_bar, entry, direction, tgt, stp)
            if r is None:
                continue
            er, ep, et = r
            comp = "GAP-FOLLOW" if mode == "follow" else "GAP-FADE"
            out.append(R.norm(comp, day, sym, direction,
                              bars[entry_bar]["time"],
                              net_of(direction, entry, ep)))
    return R.split_years(out)

fade_long = gap_rows("fade", 1.5, only_dir="LONG")
fade_long_late = gap_rows("fade", 1.5, entry_bar=2, only_dir="LONG")
follow_short = gap_rows("follow", 1.5, only_dir="SHORT")

def jo(bk, yr):
    return round(sum(t["net"] for t in bk[yr]
                     if t["date"] <= f"{yr}-10-31"), 2)

# ---- ingredient anchors (verification only, not new cycles) -------------
var_r226 = R4.swap(books, "INV-ABOVE", above150)
d = (round(jo(var_r226, 2025) - base_jo[2025], 2),
     round(R4.full_total(var_r226) - R4.full_total(books), 2))
print("R2-26 anchor: 2025 JO delta", d[0], "| combined delta", d[1])
assert d == (7534.00, 13089.83), d

var_r310 = R4.add_comp(books, "GAP-FADE", fade_long)
d = (round(jo(var_r310, 2025) - base_jo[2025], 2),
     round(jo(var_r310, 2026) - base_jo[2026], 2),
     round(R4.full_total(var_r310) - R4.full_total(books), 2))
print("R3-10 anchor: 2025 JO delta", d[0], "| 2026 JO delta", d[1],
      "| combined delta", d[2])
assert d == (26979.39, -4080.76, 22084.79), d
print("ingredient anchors reproduce the recorded deltas to the paisa")

# ---- the combination, gated whole ---------------------------------------
combo = R4.add_comp(var_r226, "GAP-FADE", fade_long)
p1 = R4.add_comp(R4.swap(books, "INV-ABOVE", above150_short),
                 "GAP-FOLLOW", follow_short)
p2 = R4.add_comp(var_r226, "GAP-FADE", fade_long_late)
p3 = R4.add_comp(R4.swap(books, "INV-ABOVE", above150_short),
                 "GAP-FADE", fade_long_late)
pl = [R4.full_total(p1), R4.full_total(p2), R4.full_total(p3)]
out = R4.gate(books, combo, pl)
R4.record("R4-01", "COMBINED FLAGS: R2-26 (INV-ABOVE T150/S080) + R3-10 "
                   "(GAP-FADE LONG-only >=1.5%) applied together, gated "
                   "whole — DECISION SUPPORT, not a banking", out,
          note=f"placebos: P1 both-placebo {pl[0]}; P2 R2-26 + fade-late "
               f"{pl[1]}; P3 placebo-swap + fade-late {pl[2]}. Expected "
               f"2025 JO if purely additive: 90849.69. Both ingredients "
               f"await Chandu's adoption decision; nothing banked here "
               f"regardless of verdict.",
          extra={"standalone_deltas": {"R2-26": 13089.83,
                                       "R3-10": 22084.79}},
          force_no_bank=True)
print("combo 2025 JO:", jo(combo, 2025), "| combo 2026 JO:", jo(combo, 2026))
print("WS1 done.")
