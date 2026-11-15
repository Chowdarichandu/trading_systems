#!/usr/bin/env python3
"""ROUND 9 shared builders — pre-registered in
stocks_engine_round9_2026-11-02.md before any scoring.

ath_rows(): the ATH-proximity momentum sleeve (WS2). Trigger:
session T with >= 252 sessions of history in the stock's daily
series and close[T] >= 0.98 * max(high[T-251..T]); entry the
next session at the open of the 09:35 bar, LONG, T125/S050 via
replay_plain. NO event exclusion (frozen). Returns (real,
flipped, late, violations, stats); flipped = SHORT at the same
entry bar; late = LONG at the 09:40 open.
All inputs are known at T's close; the entry session is strictly
after T by series construction — violations counted from the
series indices, never defaulted.
Basis: equity cash, home 25, provisional per 100 shares,
Rs40/trade, paper only, real Rs0.
"""
import sys
WS = "/home/hatch/workspace/trading"
sys.path.insert(0, WS)
import stocks_engine_r2_lib as R
import stocks_engine_r7_builders as B7

COST = 40.0
WIN = 252

def _score(replay_plain, bars, ei, sign, tgt=1.25, stp=0.50):
    entry = float(bars[ei]["open"])
    er, ep, et, xi, gross = replay_plain(bars, ei, sign, entry,
                                         tgt, stp)
    return round(gross - COST, 2)

def ath_rows():
    g = B7.machinery()
    STOCKS_E, replay_plain = g["STOCKS_E"], g["replay_plain"]
    SYMBOLS = g["SYMBOLS"]
    real, flipped, late = [], [], []
    violations = 0
    stats = {"trigger_days": 0, "no_next_session": 0,
             "weekend_entry": 0, "no_0935_bar": 0,
             "no_0940_bar": 0, "trades": 0}
    for sym in SYMBOLS:
        spot, daily = STOCKS_E[sym]
        highs = [d["high"] for d in daily]
        for i in range(WIN - 1, len(daily) - 1):
            h = max(highs[i - WIN + 1:i + 1])
            if not h or daily[i]["close"] < 0.98 * h:
                continue
            stats["trigger_days"] += 1
            eday = daily[i + 1]["date"]
            if R._wk(eday):
                stats["weekend_entry"] += 1
                continue
            bars = spot.get(eday, [])
            idx = {b["time"]: k for k, b in enumerate(bars)}
            if "09:35" not in idx:
                stats["no_0935_bar"] += 1
                continue
            ei = idx["09:35"]
            if eday <= daily[i]["date"]:
                violations += 1
                continue
            stats["trades"] += 1
            etime = bars[ei]["time"]
            real.append(R.norm("ATH-PROX", eday, sym, "LONG",
                               etime, _score(replay_plain, bars,
                                             ei, 1)))
            flipped.append(R.norm("ATH-PROX", eday, sym, "SHORT",
                                  etime, _score(replay_plain, bars,
                                                ei, -1)))
            if "09:40" in idx:
                li = idx["09:40"]
                late.append(R.norm("ATH-PROX", eday, sym, "LONG",
                                   bars[li]["time"],
                                   _score(replay_plain, bars,
                                          li, 1)))
            else:
                stats["no_0940_bar"] += 1
    return (R.split_years(real), R.split_years(flipped),
            R.split_years(late), violations, stats)
