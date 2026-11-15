#!/usr/bin/env python3
"""ROUND 13 shared builders — pre-registered in
stocks_engine_round13_2026-11-02.md before any scoring.

- sweep_rows(mode): WS1, the new mechanism. mode="reclaim":
  prior-day-LOW sweep + reclaim, LONG. mode="reject": the
  pre-registered symmetric variant — prior-day-HIGH sweep +
  rejection, SHORT. Morning window = bars timestamped 09:15
  through 10:30; entry at the open of the bar after the
  reclaim/rejection bar (entry timestamp <= 10:35); T125/S050
  via replay_plain. Returns (real, flipped, late, violations,
  stats), each split by year — the engine convention.
- nu_geo(tgt, stp): WS3. The anchored NE-REV-NU population
  (stocks_engine_r9_ingredients.build_cond()["notchup"] real /
  flip / late row sets) re-scored from its own entry bars at
  the given geometry. At (1.00, 0.65) it must reproduce the
  banked NU rows exactly — the callers assert that anchor.
All entries are strictly after every input is knowable;
violations are counted per construction and returned, never
defaulted. Basis: equity cash, home 25, provisional per 100
shares, Rs40/trade, paper only, real Rs0.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r6_builders as B6
import stocks_engine_r9_ingredients as ING

COST = 40.0
WINDOW_END = "10:30"        # last bar that may sweep / reclaim
ENTRY_LATEST = "10:35"      # last admissible entry-bar timestamp

def machinery():
    return B6.machinery()

# ------------------------------------------------------------- SWEEP ---
def sweep_rows(mode, tgt=1.25, stp=0.50):
    """mode='reclaim' (LONG): first morning bar trading below the
    prior day's low, then the first close back above that low at
    or after the sweep bar (the sweep bar may reclaim itself);
    entry at the next bar's open. mode='reject' (SHORT): mirror
    on the prior day's high. One trade per stock-day."""
    assert mode in ("reclaim", "reject")
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    long_form = mode == "reclaim"
    sign = 1 if long_form else -1
    direction = "LONG" if long_form else "SHORT"
    comp = "SWEEP-RECLAIM" if long_form else "SWEEP-REJECT"

    def score(bars, ei, s):
        entry = float(bars[ei]["open"])
        er, ep, et, xi, gross = replay_plain(bars, ei, s, entry,
                                             tgt, stp)
        return round(gross - COST, 2)

    real, flipped, late = [], [], []
    violations = 0
    stats = {"population_days": 0, "sweep_days": 0,
             "signal_days": 0, "no_reclaim": 0, "no_entry_bar": 0}
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        for i in range(1, len(daily)):
            day = daily[i]["date"]
            if R._wk(day):
                continue
            stats["population_days"] += 1
            level = (daily[i - 1]["low"] if long_form
                     else daily[i - 1]["high"])
            if not level:
                continue
            bars = spot.get(day, [])
            win = [k for k, b in enumerate(bars)
                   if b["time"] <= WINDOW_END]
            if not win:
                continue
            sweep_k = None
            for k in win:
                b = bars[k]
                swept = (b["low"] < level if long_form
                         else b["high"] > level)
                if swept:
                    sweep_k = k
                    break
            if sweep_k is None:
                continue
            stats["sweep_days"] += 1
            reclaim_k = None
            for k in win:
                if k < sweep_k:
                    continue
                c = bars[k]["close"]
                if (c > level if long_form else c < level):
                    reclaim_k = k
                    break
            if reclaim_k is None:
                stats["no_reclaim"] += 1
                continue
            ei = reclaim_k + 1
            if ei >= len(bars) or bars[ei]["time"] > ENTRY_LATEST:
                stats["no_entry_bar"] += 1
                continue
            # timing audit: entry strictly after the reclaim bar;
            # the level is prior-session data by construction.
            if ei <= reclaim_k or reclaim_k < sweep_k:
                violations += 1
                continue
            stats["signal_days"] += 1
            etime = bars[ei]["time"]
            real.append(R.norm(comp, day, sym, direction, etime,
                               score(bars, ei, sign)))
            flipped.append(R.norm(
                comp, day, sym,
                "SHORT" if long_form else "LONG", etime,
                score(bars, ei, -sign)))
            if ei + 1 < len(bars):
                li = ei + 1
                late.append(R.norm(comp, day, sym, direction,
                                   bars[li]["time"],
                                   score(bars, li, sign)))
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations, stats)

# ---------------------------------------------------------------- NU ---
def nu_geo(tgt, stp):
    """Re-score the anchored NE-REV-NU population at (tgt, stp).
    Returns (real, flipped, late), each split by year, every row
    labelled NE-REV-NU and scored from its own recorded entry
    bar (open) in its own recorded direction."""
    g = machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    cond = ING.build_cond()
    nu = cond["notchup"]

    def rescore(rows_by_year):
        out = {}
        for yr in (2025, 2026):
            rows = []
            for t in rows_by_year[yr]:
                spot, _daily = STOCKS_E[t["stock"]]
                bars = spot.get(t["date"], [])
                idx = {b["time"]: k for k, b in enumerate(bars)}
                assert t["entry_time"] in idx, t
                ei = idx[t["entry_time"]]
                sign = 1 if t["dir"] == "LONG" else -1
                entry = float(bars[ei]["open"])
                er, ep, et, xi, gross = replay_plain(
                    bars, ei, sign, entry, tgt, stp)
                rows.append(R.norm("NE-REV-NU", t["date"],
                                   t["stock"], t["dir"],
                                   t["entry_time"],
                                   round(gross - COST, 2)))
            out[yr] = rows
        return out

    return (rescore(nu["real"]), rescore(nu["flip"]),
            rescore(nu["late"]))
