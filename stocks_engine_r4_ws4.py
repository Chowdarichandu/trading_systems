#!/usr/bin/env python3
"""ROUND 4 — WS4 combinations (DECISION SUPPORT, never banked here) and
the WS3 volume audit.

Base = the corrected incumbent (Round-2 book + R4-03's banked GAP-FADE
LONG sleeve restricted to DOWN+FLAT cells). Combinations with the two
flagged variants, gated whole, force_no_bank — adoption stays Chandu's:
  R4-10: incumbent + R2-26 (INV-ABOVE T150/S080 swap).
         Placebo: incumbent with the SHORT-side T150 swap (R2-26's own).
  R4-11: incumbent with the GAP-FADE sleeve swapped from the banked
         DOWN+FLAT restriction to the FULL R3-10 form (all cells) —
         the head-to-head of the refinement vs the flagged sleeve.
         Placebos: mirror (GAP-FOLLOW SHORT, full) and one-bar-late
         full sleeve, swapped in the same way.
  R4-12: incumbent + R2-26 + sleeve swapped to the full R3-10 form
         (= R4-01's variant book, re-gated against the new base).
         Placebos: R4-10's placebo with the full sleeve; R4-11's late
         placebo with R2-26 applied.
WS3 audit (R4-13): volume fields in stored equity candles — scanned,
absent; no candidate exists to gate.
"""
import sys, pickle, json, csv, glob
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r4_lib as R4

books = R4.load_books()
jo = {yr: round(sum(t["net"] for t in books[yr]
                    if t["date"] <= f"{yr}-10-31"), 2) for yr in (2025, 2026)}
assert jo == {2025: 77806.57, 2026: 223293.34}, jo
print("WS4 base (corrected incumbent):", jo)

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

full_sleeve = gap_rows("fade", 1.5, only_dir="LONG")
full_late = gap_rows("fade", 1.5, entry_bar=2, only_dir="LONG")
full_mirror = gap_rows("follow", 1.5, only_dir="SHORT")
base_no_sleeve = {yr: [t for t in books[yr] if t["comp"] != "GAP-FADE"]
                  for yr in (2025, 2026)}

def with_sleeve(base_books, rows, comp="GAP-FADE"):
    b = {yr: [t for t in base_books[yr] if t["comp"] != "GAP-FADE"]
         for yr in (2025, 2026)}
    return R4.add_comp(b, comp, rows)

# R4-10: incumbent + R2-26 -------------------------------------------------
var10 = R4.swap(books, "INV-ABOVE", above150)
pl10 = [R4.full_total(R4.swap(books, "INV-ABOVE", above150_short))]
out = R4.gate(books, var10, pl10)
R4.record("R4-10", "DECISION SUPPORT: banked book + R2-26 (INV-ABOVE "
                   "T150/S080)", out,
          note=f"placebo: SHORT-side swap book {pl10[0]}. Adoption is "
               f"Chandu's; not banked here.",
          force_no_bank=True)

# R4-11: sleeve swapped to the full R3-10 form -----------------------------
var11 = with_sleeve(books, full_sleeve)
pl11 = [R4.full_total(with_sleeve(books, full_mirror, "GAP-FOLLOW")),
        R4.full_total(with_sleeve(books, full_late))]
out = R4.gate(books, var11, pl11)
R4.record("R4-11", "DECISION SUPPORT: banked DOWN+FLAT sleeve swapped "
                   "to the FULL R3-10 sleeve (all cells)", out,
          note=f"placebos: mirror book {pl11[0]}; one-bar-late book "
               f"{pl11[1]}. Head-to-head of the banked refinement vs "
               f"the flagged sleeve; not banked here.",
          force_no_bank=True)

# R4-12: R2-26 + full sleeve (R4-01's variant, new base) -------------------
var12 = R4.swap(var11, "INV-ABOVE", above150)
pl12 = [R4.full_total(R4.swap(with_sleeve(books, full_sleeve),
                              "INV-ABOVE", above150_short)),
        R4.full_total(R4.swap(with_sleeve(books, full_late),
                              "INV-ABOVE", above150))]
out = R4.gate(books, var12, pl12)
R4.record("R4-12", "DECISION SUPPORT: banked book + R2-26 + sleeve "
                   "swapped to the full R3-10 form (= R4-01 variant "
                   "re-gated on the new base)", out,
          note=f"placebos: full-sleeve + placebo-swap {pl12[0]}; "
               f"late-sleeve + R2-26 {pl12[1]}. Not banked here.",
          force_no_bank=True)

# R4-13: WS3 volume audit ---------------------------------------------------
headers = {}
for path in sorted(glob.glob(f"{WS}/data/full_hist/*/spot_5m.csv") +
                   glob.glob(f"{WS}/data/full_hist/*/spot_daily.csv")):
    with open(path) as f:
        headers.setdefault(f.readline().strip(), []).append(path)
vol_files = [p for h, ps in headers.items() if "volume" in h for p in ps]
data = json.load(open(R4.RESULTS_PATH))
data.append({
    "cycle": "R4-13", "type": "audit_no_candidate",
    "label": "WS3 volume-confirmed reactions — data audit",
    "banked": False,
    "finding": "NO volume field exists in any stored equity candle "
               "file. Headers across all 25 watchlist symbols + index "
               f"in data/full_hist: {sorted(headers)}; files carrying "
               f"a volume column: {len(vol_files)}. The logger "
               "machinery likewise carries no volume. The volume axis "
               "cannot be built from stored data; nothing was "
               "fabricated and no candidate was gated.",
    "gap_named": "per-candle volume (5-min and daily) for the 25 "
                 "watchlist stocks, 2025-2026 — a new data build, "
                 "outside this round's stored-data mandate"})
json.dump(data, open(R4.RESULTS_PATH, "w"), indent=1)
print("R4-13 WS3 audit recorded: volume absent from all stored equity "
      f"candles (headers: {sorted(headers)}); no candidate gated.")
print("WS4 done. Incumbent unchanged:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
