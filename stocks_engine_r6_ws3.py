#!/usr/bin/env python3
"""ROUND 6 — WS3: RANGE-EXPANSION FOLLOW (R6-09 LONG, R6-10 SHORT).

Construction EXACTLY as pre-registered in
stocks_engine_round6_2026-11-02.md before scoring:
- First hour = bars starting 09:15..10:10 (all 12 required); range =
  max(high) - min(low); close = close of the 10:10 bar.
- Ratio = today's range / median range of the previous 20
  data-bearing trading days of the same stock; signal needs >= 2.0.
- pos = (close - low) / (high - low) over the first hour:
  >= 0.75 -> LONG candidate; <= 0.25 -> SHORT candidate.
- Entry at the open of the 10:20 bar (10:15 bar skipped); exits
  T125/S050 via replay_plain (entry bar checked), square-off 15:10.
  One trade per stock-day; weekend bars excluded. No price levels
  are used anywhere — volatility state only.
- Placebos per direction (whole books, identical population):
  opposite direction at the same entry bar; same direction one bar
  later (10:25 open).
- Timing audit: violations = rows whose entry bar index is not
  strictly after the 10:10 signal bar's index — counted, asserted 0.
"""
import sys
from statistics import median
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_sarvaritu_logger as L
import stocks_engine_r2_lib as R
import stocks_engine_r6_lib as R6

books = R6.load_books()
g = L.load_machinery(L.FULLHIST, "2026-10-28")
STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
SYMBOLS = g["SYMBOLS"]
COST = 40.0
FH_TIMES = ["09:15", "09:20", "09:25", "09:30", "09:35", "09:40",
            "09:45", "09:50", "09:55", "10:00", "10:05", "10:10"]

def score(bars, ei, sign):
    entry = float(bars[ei]["open"])
    er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry,
                                         1.25, 0.50)
    return round(gross - COST, 2)

def build(direction):
    sign = 1 if direction == "LONG" else -1
    real, flipped, late = [], [], []
    violations = 0
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        fh = []  # (date, range) for data-bearing days, in order
        for d in daily:
            day = d["date"]
            bars = spot.get(day, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if all(t in idx for t in FH_TIMES):
                seg = [bars[idx[t]] for t in FH_TIMES]
                rng = (max(b["high"] for b in seg)
                       - min(b["low"] for b in seg))
                fh.append((day, rng, bars, idx))
            else:
                fh.append((day, None, bars, idx))
        ranges = [r for _, r, _, _ in fh if r is not None]
        seen = 0
        for day, rng, bars, idx in fh:
            if rng is None:
                continue
            pos_in_ranges = seen
            seen += 1
            if R._wk(day) or pos_in_ranges < 20 or rng <= 0:
                continue
            window = ranges[pos_in_ranges - 20:pos_in_ranges]
            med = median(window)
            if not med or rng / med < 2.0:
                continue
            seg = [bars[idx[t]] for t in FH_TIMES]
            hi = max(b["high"] for b in seg)
            lo = min(b["low"] for b in seg)
            if hi <= lo:
                continue
            pos = (seg[-1]["close"] - lo) / (hi - lo)
            if direction == "LONG" and pos < 0.75:
                continue
            if direction == "SHORT" and pos > 0.25:
                continue
            if "10:20" not in idx:
                continue
            si, ei = idx["10:10"], idx["10:20"]
            if ei <= si:
                violations += 1
                continue
            etime = bars[ei]["time"]
            real.append(R.norm("REXP", day, sym, direction, etime,
                               score(bars, ei, sign)))
            flipped.append(R.norm(
                "REXP", day, sym,
                "SHORT" if direction == "LONG" else "LONG", etime,
                score(bars, ei, -sign)))
            if "10:25" in idx and idx["10:25"] > ei:
                li = idx["10:25"]
                late.append(R.norm("REXP", day, sym, direction,
                                   bars[li]["time"],
                                   score(bars, li, sign)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations)

def without(bk, comp):
    return {yr: [t for t in bk[yr] if t["comp"] != comp]
            for yr in (2025, 2026)}

for cyc, direction in (("R6-09", "LONG"), ("R6-10", "SHORT")):
    comp = f"REXP-{direction}"
    real, flipped, late, viol = build(direction)
    assert viol == 0, (cyc, viol)
    real = {yr: [dict(t, comp=comp) for t in real[yr]] for yr in real}
    flipped = {yr: [dict(t, comp=f"REXP-"
                        f"{'SHORT' if direction == 'LONG' else 'LONG'}")
                    for t in flipped[yr]] for yr in flipped}
    late = {yr: [dict(t, comp=comp) for t in late[yr]] for yr in late}
    present = any(t["comp"] == comp for yr in (2025, 2026)
                  for t in books[yr])
    var = (R6.swap(books, comp, real) if present
           else R6.add_comp(books, comp, real))
    base_wo = without(books, comp)
    pl = [R6.full_total(R6.add_comp(base_wo, flipped[2025][0]["comp"]
                                    if flipped[2025] else "REXP-X",
                                    flipped)),
          R6.full_total(R6.add_comp(base_wo, comp, late))]
    out = R6.gate(books, var, pl, timing_violations=viol)
    n = {str(yr): len(real[yr]) for yr in (2025, 2026)}
    R6.record(cyc, f"RANGE-EXPANSION FOLLOW {direction} (first-hour "
                   f"range >= 2x trailing 20-day median, hour close in "
                   f"{'top' if direction == 'LONG' else 'bottom'} "
                   f"quartile, entry 10:20, T125/S050)", out,
              note=f"population trades {n}; timing audit: entry bar "
                   f"(10:20) strictly after the signal bar (10:10) on "
                   f"every row, violations counted = {viol}; placebos: "
                   f"opposite-direction book {pl[0]}; one-bar-late "
                   f"book {pl[1]}",
              extra={"standalone": {str(yr): round(
                  sum(t['net'] for t in real[yr]), 2) for yr in real},
                  "population_trades": n})
    if out["verdict"]:
        books = var
        R6.save_books(books)
        print("    -> BANKED; incumbent updated")

print("WS3 done. Incumbent Jan-Oct:",
      {yr: round(sum(t['net'] for t in books[yr]
                     if t['date'] <= f'{yr}-10-31'), 2)
       for yr in (2025, 2026)})
