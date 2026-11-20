# TARANG Design 23 — STREAM-GROSS SURVEY — SPEC (pre-registered)

Pre-registered 2026-11-17, before any Design 23 scoring.
Programme status: CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the
owner's stop). Research only: nothing armed, no paper run,
NO BOOK is built in this design.

## S.0 Why a survey

Both prior TARANG families are measured-exhausted, and both
died the same death: designs were spent tuning streams whose
raw gross never reached the ₹40/trade cost levy (excursion
family ceiling ~₹27/trade; vote family best stream-year
+₹22.91, best taken year +₹26.08). Design 23 changes the
method: **no family earns a book until its RAW STREAM gross
clears ₹40/trade in BOTH years.** This design only surveys.
A family that passes the survey earns a Design 24 book
under the full unmoved gate; a family that fails is closed
at survey cost, with no book, filter, gate or allocator
built on it.

## S.1 Basis and universe

- Equity cash, PROVISIONAL per 100 shares, ₹40/trade cost
  levy, paper only, real money ₹0. No stock options.
- Universe: the 127 verified F&O names of Designs 7–22
  (`tarang6_universe.json` verified_universe), 5-min bars
  from the same stores (`data/tarang_vol` incumbents,
  `data/tarang_wide_vol` wide names), 2025-01-01 to
  2026-11-13, loaded by the family's own loader
  (`tarang6_score.load_name6`).
- Years: calendar year of the trade date. 2025 is the full
  year in store; 2026 runs 2026-01-01 to 2026-11-13 (the
  store's end), the same convention as Designs 7–22.

## S.2 Common survey protocol (every family, no exceptions)

- **Stream**: every signal the family's rule produces, but
  at most ONE trade per name-day per family — the FIRST
  qualifying signal of the day. No caps, no allocation, no
  filters, no ranking. (GAP-GO and GAP-FADE are two separate
  sub-streams of one family; each takes its own one trade
  per name-day.)
- **Entry**: the open of the bar AFTER the signal bar
  (next-bar-open fill), except the two families whose signal
  is defined at a session boundary (GAP: entry is the day's
  first-bar open, the gap being known at the open from the
  previous close and the opening print; FH-MOM: entry is
  the open of the 10:15 bar, the first-hour return being
  complete at 10:15). An entry that would fall after the
  square-off bar is not taken (the signal is counted as
  unfilled and disclosed).
- **Exit — ONE standard exit for all families** (the drift
  form of Designs 14/20): disaster stop at entry × 0.99
  (LONG) / entry × 1.01 (SHORT), stop-first, a bar that
  opens through the stop fills at the bar's open, otherwise
  the position exits at the CLOSE of the square-off bar.
  The square-off bar is the day's last bar with timestamp
  ≤ 15:15 (the family's `day_maps` convention). The exit
  scan starts at the entry bar itself. Implementation:
  `tarang20_score.exit20_engine`, unchanged.
- **Money**: gross = (exit − entry) × side × 100 shares.
  net = gross − ₹40. Win rate = share of trades with
  net > 0.
- **Score per family per year**: trades taken (and raw
  signals / unfilled count), gross ₹, gross/trade, net ₹,
  net/trade, win rate, LONG gross/trade and SHORT
  gross/trade (side split), stop share, square-off mean
  gross/trade.
- **SURVEY PASS**: gross/trade STRICTLY greater than
  ₹40.00 in BOTH 2025 and 2026. Anything else is a survey
  fail, whatever its net, win rate or single-year figure.

## S.3 The seven families (exact signal definitions)

Bars are 5-minute bars timestamped by bar start; a day's
bars normally run 09:15–15:25. "Close" of a bar is its
close; all comparisons use closes unless stated.

1. **ORB-30** — The opening range is the high/low over the
   day's bars timestamped 09:15, 09:20, 09:25, 09:30,
   09:35, 09:40 (the first 30 minutes). A day missing any
   of those six bars is skipped (counted). From the 09:45
   bar onward, the first bar whose close is above the range
   high is a LONG signal; the first whose close is below
   the range low is a SHORT signal; whichever occurs first
   in the day is the day's signal.
2. **PDHL** — The previous trading day (for that name, in
   the store) supplies PDH = its maximum high and PDL =
   its minimum low over all its bars. From the day's first
   bar onward, the first bar whose close is above PDH is a
   LONG signal; the first whose close is below PDL is a
   SHORT signal; first in the day wins. A name's first
   store day has no previous day and is skipped.
3. **VWAP-SNAP** — Session VWAP is the cumulative
   volume-weighted typical price ((H+L+C)/3) from 09:15,
   the family's own construction (`tarang_score`
   add_indicators). A bar is deviated-up if its close
   ≥ VWAP × 1.005 and deviated-down if its close
   ≤ VWAP × 0.995 (VWAP of that same bar). An up-deviation
   sets the up-flag; the first later bar whose close
   ≤ VWAP (price closing back through VWAP) is a SHORT
   signal — the reclaim direction is down. Symmetrically a
   down-deviation followed by a close ≥ VWAP is a LONG
   signal. The flag persists until it fires or the day
   ends; first signal of the day only. Bars where VWAP is
   undefined (zero cumulative volume) are ignored.
4. **GAP** — gap% = (today's first-bar open / previous
   trading day's last bar close) − 1. If gap% ≥ +1.0% or
   ≤ −1.0% the day qualifies. **GAP-GO** enters at the
   first bar's open in the gap's direction (up-gap LONG,
   down-gap SHORT). **GAP-FADE** enters at the same price
   in the opposite direction. Each sub-stream is scored
   separately under the standard exit (the exit scan
   starts at the first bar).
5. **RSI2** — RSI(2) on 5-min closes, Wilder smoothing,
   continuous over the name's whole series: deltas seeded
   by the SMA of the first 2 deltas at bar 2, then
   avg = (avg × 1 + new) / 2 per bar; RSI = 100 when the
   average loss is 0 and average gain > 0, 50 when both
   are 0. The first bar of a day with RSI(2) < 5 is a LONG
   signal; the first with RSI(2) > 95 is a SHORT signal;
   first in the day wins.
6. **FH-MOM** — First-hour return = (close of the 10:10
   bar / open of the 09:15 bar) − 1, the 09:15–10:15
   hour being bars 09:15…10:10. Return > 0 → LONG,
   < 0 → SHORT, = 0 → no trade. Entry is the open of the
   10:15 bar. A day missing the 09:15, 10:10 or 10:15 bar
   is skipped (counted).
7. **VOLSHOCK** — For a bar j (day-local position ≥ 20):
   the trailing window is the 20 bars immediately before j
   in the same session. A shock requires volume[j] ≥ 3 ×
   mean(volume over the window). If in addition close[j]
   is above the window's maximum high → LONG signal; if
   below the window's minimum low → SHORT signal. First
   shock of the day only.

## S.4 Controls (run before / alongside, reported first)

1. **EKAM machinery control FIRST** — `tarang19_score
   .ekam_control()`: EKAM's own imported machinery on the
   frozen 25 must reproduce the published CAND-T5
   (+₹62,164.57 / +₹63,883.60) and S2 (+₹45,300.64 /
   +₹72,605.30) Jan–Oct lines exactly. If it fails, no
   Design 23 number is quoted.
2. **Signal parity** — every family's signal set is
   re-derived by an independent second implementation
   (pandas groupby/rolling path over the raw frames) and
   must match the engine's set exactly (name, date, side,
   signal bar) on all 127 names.
3. **Exit parity** — every taken trade's exit is
   re-simulated by the independent audit exit
   (`tarang20_score.exit20_audit`) and must match on bar,
   price and reason.
4. **Truncation spot-check** — 30 sampled trades: the
   signal is recomputed from bars cut at the signal bar
   and must be present and identical (no look-ahead).
5. **Independent re-sum** — the written
   `tarang23_trades.csv` re-sums to the reported gross and
   net per family per year to the paisa.

## S.5 What this design does not do

No gate table (the 9-leg book gate does not apply to a
survey), no placebo (a stream has no allocation to
placebo-test; timing proof belongs to the Design 24 book
if a family earns one), no per-entity tuning, no November
slice verdict (November days are inside the 2025/2026
streams like any other days). The survey's only verdict
per family is PASS (gross/trade > ₹40 both years) or FAIL,
with the anatomy reported either way.
