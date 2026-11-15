#!/usr/bin/env python3
"""ROUND 5 — WS3: NON-EVENT INTRADAY REVERSAL (new mechanism, new
population). Construction EXACTLY as pre-registered in
stocks_engine_round5_2026-11-02.md before scoring:

- Contamination: stock-day excluded if in {R, R+1, R+2} (stock's own
  trading days) of any results event (machinery reaction_candidates
  over both calendars, pooled).
- Signal: close of the 10:25 bar vs prior daily close. <= -2.00% ->
  LONG candidate (R5-07); >= +2.00% -> SHORT candidate (R5-08).
- Entry: open of the 10:35 bar (the 10:30 bar is skipped entirely).
  Exits T100/S065 via replay_plain (entry bar checked), square-off
  15:10. One trade per stock-day. Weekend bars excluded.
- Placebos per direction (whole books): opposite direction on the
  identical population/entry bar; same direction one bar later
  (10:40 open).
- Timing audit: violations counted as rows whose entry bar index is
  not strictly after the signal bar index — asserted 0 in code.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r5_lib as R5

books = R5.load_books()
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
SYMBOLS = g["SYMBOLS"]
rc = g["reaction_candidates"]
COST = 40.0
CALS = [(f"{WS}/stock_event_calendar_2025.csv", "2025-01-01", "2025-12-31"),
        (f"{WS}/stock_event_calendar_jan_oct_2026.csv", "2026-01-01",
         "2026-12-31")]

# ------------------------------------------------ contamination set ----
contaminated = set()
n_events = 0
for cal, lo, hi in CALS:
    for c in rc(cal, lo, hi):
        n_events += 1
        sym, ri = c["symbol"], c["ri"]
        daily = STOCKS_E[sym][1]
        for j in (0, 1, 2):
            if ri + j < len(daily):
                contaminated.add((sym, daily[ri + j]["date"]))
print(f"reaction candidates pooled: {n_events}; contaminated "
      f"stock-days: {len(contaminated)}")

# ------------------------------------------------------ population -----
def score(sym, bars, ei, sign):
    entry = float(bars[ei]["open"])
    er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry, 1.00, 0.65)
    return round(gross - COST, 2)

def build(direction):
    """direction: the REAL trade direction of this sleeve ('LONG' feeds
    on down-moves, 'SHORT' on up-moves). Returns (real, flipped, late)
    row sets split by year, plus the timing-violation count."""
    real, flipped, late = [], [], []
    violations = 0
    want_down = (direction == "LONG")
    sign = 1 if direction == "LONG" else -1
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day) or (sym, day) in contaminated:
                continue
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "10:25" not in idx or "10:35" not in idx:
                continue
            si, ei = idx["10:25"], idx["10:35"]
            prev_close = daily[i - 1]["close"]
            if not prev_close:
                continue
            move = (bars[si]["close"] / prev_close - 1) * 100
            if want_down and move > -2.0:
                continue
            if not want_down and move < 2.0:
                continue
            if ei <= si:
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("NE-REV", day, sym, direction, etime,
                               score(sym, bars, ei, sign)))
            flipped.append(R.norm("NE-REV", day, sym,
                                  "SHORT" if direction == "LONG" else "LONG",
                                  etime, score(sym, bars, ei, -sign)))
            if "10:40" in idx and idx["10:40"] > ei:
                li = idx["10:40"]
                late.append(R.norm("NE-REV", day, sym, direction,
                                   bars[li]["time"],
                                   score(sym, bars, li, sign)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations)

for cyc, direction in (("R5-07", "LONG"), ("R5-08", "SHORT")):
    real, flipped, late, viol = build(direction)
    assert viol == 0, (cyc, viol)
    comp = f"NE-REV-{direction}"
    real = {yr: [dict(t, comp=comp) for t in real[yr]] for yr in real}
    var = R5.add_comp(books, comp, real)
    pl = [R5.full_total(R5.add_comp(books, comp, flipped)),
          R5.full_total(R5.add_comp(books, comp, late))]
    out = R5.gate(books, var, pl, timing_violations=viol)
    n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
    R5.record(cyc, f"NON-EVENT REVERSAL {direction} (|move by 10:30| "
                   f">=2.0% on non-event days, entry 10:35, T100/S065)",
              out,
              note=f"population trades {n}; timing audit: entry bar "
                   f"(10:35) strictly after signal bar (10:25) on every "
                   f"row, violations counted = {viol}; placebos: "
                   f"opposite-direction book {pl[0]}; one-bar-late book "
                   f"{pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in real[yr]), 2) for yr in real},
                  "population_trades": n})
    if out["verdict"]:
        books = var
        R5.save_books(books)
        print("    -> BANKED; incumbent updated")

print("WS3 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
