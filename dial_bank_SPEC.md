# DIAL — BANK NIFTY · SPEC (frozen before scoring, 2026-11-14)

Programme: DIAL (registry: dial_programme.md). This file records the
owner-facing core spec VERBATIM, plus the data/fill details fixed
before any scoring. Research only — no existing book, ledger or job
is changed by this run. Buying only, 1 lot (30), paper only.

## Core spec (verbatim from the owner-facing brief — not altered)

- Data: Bank Nifty 5-min spot candles Jan–Oct 2026 from the persisted
  stores; signal on a COMPLETED bar's close; entry at the NEXT bar.
  Instrument: buy the weekly-expiry strike nearest spot at entry, CE
  for up-signals, PE for down-signals (the contract-selection
  convention the stack scorers use); entry premium = open of the
  entry bar of that contract from the stored premium candles; if the
  needed contract's candles are missing, the signal is NC (counted,
  never substituted).
- DIAL-T (trend): Supertrend(7,3) on 5-min spot flips direction at a
  bar close AND spot closes on the same side of session VWAP ->
  signal in the flip direction. First qualifying signal of the day
  only.
- DIAL-R (reversion): at a bar close, RSI(14) <= 30 AND Bollinger %B
  <= 0.05 AND EMA50 slope over the last 6 bars > -0.1% -> LONG
  signal; mirror: RSI >= 70 AND %B >= 0.95 AND slope < +0.1% ->
  SHORT signal. First qualifying signal of the day only.
- Exits (both components): stop -50 premium points, target +90,
  square-off 15:20. Cost Rs220/trade. A day can carry one T trade
  and one R trade (report components separately AND combined as the
  DIAL-Bank book).
- GATE (same run, frozen): timing audit (proof every signal uses
  only completed bars); random-entry placebo (same trade count,
  random days/bars, same geometry — combined book must beat the 95th
  percentile); +30-min time-shift placebo (must also beat); halves;
  full month table; ex-top-3.
- PASS BAR (combined book): placebo conditions met AND both halves
  positive AND ex-top-3 positive AND Rs/trade-day >= 900
  (trade-days = days with >= 1 DIAL trade) AND WR >= 60% AND
  average monthly pace >= Rs7,500 AND no more than 2 red months.
  Report each component against the same bars descriptively
  (components do not pass/fail separately). Name failing legs.
- NOVEMBER CF (descriptive): run the frozen system over Nov 2–13
  stored candles; report signals and net.

## Data / fill details (fixed before scoring)

1. SPOT STORE: data/progressive/BANKNIFTY/spot_5m.csv — one
   continuous 5-min series, 2026-01-01 → 2026-11-13. Gate window
   Jan 1–Oct 31 = 203 stored trading days, every one a full 75-bar
   day. Oct 29–30 are absent from this store and are outside the
   gate basis (this is the same spot store and basis as the
   REGIME-REV gate). November CF days Nov 2,3,4,5,6,9,11,12,13 are
   in the same series (75 bars each).
2. EXPIRY: "weekly-expiry" is implemented as the in-force expiry
   from oi_history/banknifty_daily_oi.csv (date -> expiry) — the
   only expiry series the persisted stores carry for 2026 Bank
   Nifty, and the same contract the stack scorers trade (November
   override: 2026-11-23, as in the house scorers). Strike step 100;
   strike = step nearest the SIGNAL bar's spot close; an exact half
   rounds up. CE for up-signals, PE for down-signals.
3. SESSION VWAP (fill detail, flagged wherever reported): the spot
   series carries no volume in any persisted store (house finding,
   familyB_indicators.py) and an index has no traded volume, so
   session VWAP = the session VWAP of the in-force Bank Nifty
   FUTURES contract (round5_history/FUT7_{expiry}.json, rows
   [date, time, O,H,L,C, volume, OI]), cumulative
   typical-price x volume / volume through the signal bar
   inclusive. The side test compares the SPOT close against that
   futures session VWAP at the same bar. If the futures series
   lacks the day (or the bar), VWAP is undefined there and DIAL-T
   cannot signal at that bar (counted as VWAP-unavailable).
4. INDICATORS — continuous 5-min spot series, causal by
   construction (each value at bar i uses bars <= i only):
   - Supertrend(7,3): Wilder ATR(7) seeded with the SMA of the
     first 7 true ranges; standard final-band carry rules
     (final upper = basic upper if basic upper < prev final upper
     or prev close > prev final upper, else prev final upper;
     final lower mirrored); direction starts at the ATR seed bar
     (up if close >= HL/2 midpoint band side, else down) and flips
     when the close crosses the opposite final band.
   - RSI(14): Wilder.
   - Bollinger(20, 2.0): SMA +/- 2 population stdev of the last 20
     closes incl. current; %B = (close - lower)/(upper - lower);
     if upper == lower, %B := 0.5.
   - EMA50: k = 2/51, seeded with the SMA of the first 50 closes;
     slope% = (EMA[i] - EMA[i-6]) / EMA[i-6] * 100.
   A component cannot signal at a bar where an indicator it needs
   is still undefined (warmup).
5. SIGNAL ACTIONABILITY: signals are evaluated at bar closes
   09:15..15:10; the entry bar is the next bar (<= 15:15). A signal
   whose bar is later than 15:10 is counted as a late signal, never
   a trade. DIAL-T uses the strict event reading: the flip must
   occur AT that bar's close and the VWAP side test must pass at
   the same bar; a later bar riding an earlier flip does not
   qualify. First qualifying signal per component per day; T and R
   are independent (a day may carry both).
6. PREMIUM RESOLUTION (house convention, copied from
   november_regime_family.py): (a) round5_history
   C5_{expiry}_{strike}{type}.json; (b) daily2leg/prem_bank.json;
   (c) per-day files candles_BANKNIFTY_{strike}{type}_{expiry}_{day}
   .json in btst_data, november_shadow_data,
   nifty_weekly_expiry_chain, oi_buildup_data. First store that
   carries the contract-day wins. Missing everywhere -> NC.
7. EXIT WALK: from the entry bar onward over the day's stored bars
   in time order. Every 5-min timestamp from the entry bar through
   the exit bar must be present (contiguity), else NC. Per bar:
   stop (-50) checked before target (+90); fills AT the level
   (entry-50 / entry+90). If no level is hit through the 15:20 bar,
   exit at the 15:20 bar's close (the 15:20 bar is itself checked
   for level fills first, stop before target). If no level is hit
   and the 15:20 bar is absent -> NC. Bars after 15:20 are ignored.
   The entry bar itself can trigger an exit (house convention).
8. MONEY: net = (exit - entry) x 30 - Rs220. A win is net > 0.
   Trade-days (combined) = distinct days with >= 1 scored DIAL
   trade; per component likewise. Halves: H1 = Jan–May 2026,
   H2 = Jun–Oct 2026. Monthly pace = combined total / 10. Red
   month = combined month net < 0. Ex-top-3 = combined total minus
   the 3 largest trade nets, must be > 0.
9. PLACEBOS: (a) Random-entry: 500 iterations, RNG seed 20261114.
   For each real combined trade: same day, same side; entry bar
   drawn uniformly from that day's bars with entry time in
   09:20..15:15; strike = step nearest the close of the bar before
   the drawn entry bar; identical premium resolution, exits, cost.
   An NC draw is redrawn up to 50 times, then dropped (drops
   counted and reported). Percentile = % of placebo iteration
   totals strictly below the real combined total; the placebo leg
   passes at >= 95.0. (b) +30-min shift: same contract as the real
   trade, entry at the bar 6 bars after the real entry bar,
   identical exits from the shifted entry, same cost; shifted
   trades whose entry bar is past 15:15 or NC are dropped and
   counted; the leg passes if the real combined total exceeds the
   shifted combined total.
10. TIMING AUDIT: by construction all indicators are causal
    recursions or trailing windows and the entry is the bar AFTER
    the signal bar. In addition, the build re-computes RSI,
    Supertrend direction, Bollinger %B and EMA50 for every scored
    signal bar from the series truncated at that bar and asserts
    equality with the full-series values; any mismatch aborts the
    run and is reported instead of results.
11. NC TAXONOMY (all counted, never estimated or substituted):
    NC_premium (signal fired; contract/entry/exit bars missing or
    non-contiguous), VWAP-unavailable bars (T only), late signals
    (after 15:10), warmup bars (indicator undefined).

Frozen 2026-11-14, before scoring. Build: dial_bank_build.py.
Outputs: dial_bank_2026-11-14.md + dial_bank_results.json.
