# LINE S1 — THE SHORT-SIDE CONTINUATION BOOK — FROZEN BEFORE SCORING
Frozen: 2026-10-31, before any S1 cell was scored. No cell may be
added, removed or re-parametrised after scoring begins; any change
requires a new line.

## Basis (programme-standard, unchanged)
- Equity cash intraday, SHORT entries (direction language LONG/SHORT
  only; no options anywhere). Paper only, real money Rs 0, no orders.
- Provisional per 100 shares; net = gross - Rs 40/trade flat.
- Window Jan-Oct 2026. Universes: home 25 (data/progressive/) +
  new 25 large caps (data/progressive_ext/). POOLED 50 is primary;
  home/ext splits always reported alongside.
- Halves split by ENTRY date: Jan-May = entry <= 2026-05-31,
  Jun-Oct = entry >= 2026-06-01. October = entry month 2026-10.
- One trade per stock per qualifying day.
- Entry for every cell: NEXT trading day (in that stock's own cached
  calendar) at the 09:15 bar open. Exit replay scans to the 15:10
  square-off. Target/stop are % of entry price, stop-first within a
  bar.

## Why this book exists (hypothesis, stated ex-ante)
Two independent honest lines pointed the same way: (1) P2F's profit
is essentially all SHORT-side (+Rs 13,109.45 SHORT vs -Rs 273.57 LONG
of its +Rs 12,835.88, home); (2) inside R2's FAILED generalised
follow-through, continuation after big DOWN days paid +Rs 91,090.73
while the LONG side was the hole. S1 isolates the short-side
continuation as its own book and judges it on its own gate. This is
a hypothesis test, not a rescue of R2: no R2 cell is re-scored here
except under the new frozen definitions below.

## Qualifiers
- DAY MOVE (cells A-D, placebo): close-to-close return of a stock-day
  = last 5-min bar close of day d / last 5-min bar close of the
  previous cached trading day - 1 (R2 build_ft construction,
  verbatim). The qualifier is COMPLETE at day d's 15:30 close.
- EVENT REACTION DAY (cell E): per the frozen P2F construction
  (stocks_tuning_event.py, verbatim): results events from
  stock_event_calendar_jan_oct_2026.csv (home) and
  stock_event_calendar_ext_jan_oct_2026.csv (ext); effective reaction
  day R = reaction_date if event_date <= reaction_date <=
  event_date + 7 days, else event_date; reaction_ret_pct =
  round((daily_close(R) / daily_close(prev trading day) - 1) * 100, 2)
  from spot_daily.csv. COMPLETE at R's 15:30 close. Duplicate
  (symbol, R) calendar rows are de-duplicated (first kept) so the
  one-trade-per-stock-per-day rule holds.

## Cells (all frozen)
- S1-A DOWN-CONTINUATION: day move <= -2.0% -> SHORT next day.
  Exits T125/S050 (target +1.25% / stop -0.50% for the SHORT).
- S1-B DOWN-CONTINUATION 2.5: day move <= -2.5% -> SHORT next day.
  Exits T125/S050.
- S1-C = S1-A with T10/S050 exits (target +1.00%).
- S1-D UP-FADE: day move >= +2.0% -> SHORT next day (fade).
  Exits T125/S050.
- S1-E EVENT-ONLY DOWN-CONTINUATION: reaction day with
  reaction_ret_pct <= -2.0 -> SHORT next trading day. Exits
  T125/S050. This is the P2F-short core, isolated and re-judged
  pooled across both universes.

## Exit engines (disclosed, per lineage)
- Cells A-D and their placebo: replay_plain from
  stocks_tuning_universe.py, verbatim (the R2 engine; scan starts at
  the entry bar, stop-first, 15:10 square-off at that bar's close).
- Cell E and its placebo: the P2F replay from
  stocks_tuning_event.py, verbatim (scan starts at the bar AFTER the
  09:15 entry bar, bars after 15:10 ignored, 15:10 square-off).
  Reason: S1-E claims to BE the P2F-short core; it must use P2F's
  own frozen exit engine so the anchor below is an exact test.

## Anchor validation (runs BEFORE pooled scoring is trusted)
S1-E restricted to the home universe MUST reproduce the published
P2F SHORT subset exactly: 32 trades, net +Rs 13,109.45 (from
stocks_tuning_event_V1_combined_trades.csv, leg=P2F, SHORT rows).
If the anchor fails, S1-E is reported as FAILED VALIDATION and its
pooled number is not quoted as a result.

## Controls (same run as scoring — controls-first protocol)
1. TIMING AUDIT: for EVERY trade in EVERY cell (and the placebo),
   assert entry_datetime > info_complete_datetime, where
   info_complete = qualifier day (move day d / reaction day R) at
   15:30 and entry = entry date at 09:15. Print trade count,
   violations, and >= 10 sample rows per cell. If any violation:
   abort before printing scores.
2. PLACEBO (two-day lag): mirrors the BEST cell (by pooled net):
   same qualifier day and same rule, but entry delayed one extra
   session — entry = qualifier day + 2 trading sessions (at entry
   time the qualifying move is the day-before-yesterday's). Same
   direction, same exits, same engine as the mirrored cell. A real
   next-day effect must BEAT the placebo: placebo pooled net <
   best-cell pooled net is required by the gate; both numbers are
   printed regardless.

## Reporting (every cell, pass or fail)
Trades, net, Jan-May net, Jun-Oct net, October net, breadth
(stocks with net > 0, /50 pooled and /25 per universe), expectancy
per trade, top-3 share (sum of the 3 largest per-stock nets /
pooled net x 100; flagged n/m if pooled net <= 0), win %.
Month-by-month table for the best cell.

## Gate toward candidacy (standing gate; the ~Rs 25k/month pooled
figure is the programme's aspiration, NOT this gate)
A cell is a candidate only if ALL hold, pooled 50:
both halves > 0 AND breadth >= 35/50 AND October > 0 AND timing
audit clean AND (for the best cell) placebo beaten.
A passing cell is frozen as stocks_S1_candidate_spec.md with this
December 2026 fresh-window judging rule: run the frozen rule
verbatim on December data, pooled 50 — >= 8 trades AND net > 0 ->
confirmed candidate (continues as paper shadow); net < 0 -> killed;
< 8 trades -> inconclusive, extends to January 2027.
If no cell passes, the report says so plainly and no spec is frozen.
