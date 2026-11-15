#!/usr/bin/env python3
"""ROUND 4 — TIMING-AUDIT REPAIR (same-run correction).

R4-07 (entry at the 09:15 open, entry_bar 0) was banked by
stocks_engine_r4_ws2.py with the harness's default timing_violations=0.
That default is wrong for this one cell: the sleeve's signal IS the gap,
gap = bars[0].open / prior close - 1, so a fill at bars[0].open is a
fill at the very print that first reveals the qualifying information —
entry before the information existed, on every sleeve trade. (The
engine's open-entry convention is legitimate only when the signal is
fully known before the open, as with the reaction families.) The bar-0
sleeve's standalone (+67,392.17 / +22,054.04 vs the bar-1 sleeve's
+26,165.55 / -4,080.76) is the first-bar snap-back harvested at the
signal print — the look-ahead signature. R4-07's banking is VOID on
leg (i); the incumbent reverts to the R4-03 banked book.

This script: (1) rebuilds the R4-03 banked book from the Round-2 CSVs
+ the regenerated DOWN+FLAT sleeve and asserts it to the paisa;
(2) appends the void record to r4_results.json; (3) re-runs the two
cells that were gated against the voided base (entry 09:35, exits
T150/S080) against the corrected base, as R4-08R / R4-09R.
"""
import sys, json
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_floor_lib as FL
import stocks_engine_r2_lib as R
import stocks_engine_r4_lib as R4

g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay = g["STOCKS_E"], g["replay"]
SYMBOLS = g["SYMBOLS"]
LABELS = R.LABELS
COST = 40.0

def net_of(direction, entry, exit_price):
    sign = 1 if direction == "LONG" else -1
    return round(sign * (exit_price - entry) * 100 - COST, 2)

def gap_rows(mode, thr, entry_bar=1, tgt=1.25, stp=0.5, only_dir=None,
             cells=None):
    out = []
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            if cells is not None and LABELS.get(day) not in cells:
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

# (1) rebuild the R4-03 banked book ---------------------------------------
books = {yr: FL.load(f"stocks_engine_r2_book{yr}_trades.csv")
         for yr in (2025, 2026)}
sleeve = gap_rows("fade", 1.5, entry_bar=1, cells={"DOWN", "FLAT"},
                  only_dir="LONG")
books = R4.add_comp(books, "GAP-FADE", sleeve)
jo = {yr: round(sum(t["net"] for t in books[yr]
                    if t["date"] <= f"{yr}-10-31"), 2) for yr in (2025, 2026)}
assert jo == {2025: 77806.57, 2026: 223293.34}, jo
assert (len(books[2025]), len(books[2026])) == (857, 899)
R4.save_books(books)
print("corrected incumbent rebuilt + asserted:", jo,
      "trades:", {yr: len(books[yr]) for yr in (2025, 2026)})

# (2) void record ----------------------------------------------------------
bar0 = gap_rows("fade", 1.5, entry_bar=0, only_dir="LONG")
n_viol = len(bar0[2025]) + len(bar0[2026])
data = json.load(open(R4.RESULTS_PATH))
data.append({
    "cycle": "R4-07-VOID", "type": "timing_audit_correction",
    "label": "R4-07 banking VOID on leg (i): entry at bars[0].open is a "
             "fill at the print that defines the signal (gap = bar-0 "
             "open / prior close); every sleeve trade enters before its "
             "qualifying information existed",
    "timing_violations": n_viol,
    "sleeve_trades_bar0": {str(yr): len(bar0[yr]) for yr in (2025, 2026)},
    "voided_standalone": {"2025": 67392.17, "2026": 22054.04},
    "honest_bar1_standalone": {"2025": 26165.55, "2026": -4080.76},
    "effect": "incumbent reverts to the R4-03 banked book (2025 JO "
              "77,806.57; 2026 JO 2,23,293.34); R4-08/R4-09 as originally "
              "recorded were gated against the voided base and are "
              "superseded by R4-08R/R4-09R",
    "banked": False})
json.dump(data, open(R4.RESULTS_PATH, "w"), indent=1)
print(f"void recorded: {n_viol} timing violations (all bar-0 sleeve "
      f"trades)")

# (3) re-run the two contaminated cells against the corrected base --------
def apply_sleeve(base_books, rows):
    present = any(t["comp"] == "GAP-FADE" for yr in (2025, 2026)
                  for t in base_books[yr])
    return (R4.swap(base_books, "GAP-FADE", rows) if present
            else R4.add_comp(base_books, "GAP-FADE", rows))

def run_cell(cyc, label, thr=1.5, entry_bar=1, tgt=1.25, stp=0.5):
    global books
    rows = gap_rows("fade", thr, entry_bar, tgt, stp, only_dir="LONG")
    mirror = gap_rows("follow", thr, entry_bar, tgt, stp,
                      only_dir="SHORT")
    late = gap_rows("fade", thr, entry_bar + 1, tgt, stp,
                    only_dir="LONG")
    var = apply_sleeve(books, rows)
    base_no = {yr: [t for t in books[yr] if t["comp"] != "GAP-FADE"]
               for yr in (2025, 2026)}
    pl = [R4.full_total(R4.add_comp(base_no, "GAP-FOLLOW", mirror)),
          R4.full_total(R4.add_comp(base_no, "GAP-FADE", late))]
    out = R4.gate(books, var, pl)
    R4.record(cyc, label, out,
              note=f"RE-RUN against the corrected R4-03 base (the "
                   f"original {cyc[:-1]} record was gated against the "
                   f"voided R4-07 base and is superseded); placebos: "
                   f"mirror book {pl[0]}; one-bar-late book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in rows[yr]), 2) for yr in rows}})
    if out["verdict"]:
        books = var
        R4.save_books(books)
        print("    -> BANKED; incumbent updated")

run_cell("R4-08R", "GAP-FADE LONG >=1.5%, entry 09:35 open (T125/S050) "
                   "— swap vs banked DOWN+FLAT sleeve", entry_bar=4)
run_cell("R4-09R", "GAP-FADE LONG >=1.5%, exits T150/S080 (09:20) "
                   "— swap vs banked DOWN+FLAT sleeve",
         tgt=1.50, stp=0.80)
print("repair done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
