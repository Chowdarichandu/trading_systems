# Stocks EQUITY — V5 validation + deeper tuning — FROZEN 2026-10-30, BEFORE SCORING

**User instruction 2026-10-30 19:33 IST: do NOT wait for approval
between steps — proceed autonomously. EQUITY CASH intraday only.
LONG/SHORT language only — no options, no premiums anywhere.
Paper only, no orders. Real money: ₹0. Every rupee figure is
provisional per 100 shares, ₹40/trade flat cost.**

## Portfolio rule (user correction 19:33 IST, binding)

- **NO 1-trade/day portfolio cap.** If several watchlist stocks meet
  the setup on a day, ALL are traded — 10 trades in a day is fine.
  Max 1 trade per stock per day (by signal construction).
- The uncapped per-stock view is the PRIMARY view. Capped views are
  not headlined.
- The user's floor is a **MINIMUM of ~2 valuable trades/day** across
  the portfolio. Compliance is reported as a trades/day distribution
  (trading days with 0 / 1 / 2+ qualifying trades, mean trades/day),
  never as a cap.

## Base system (unchanged from stocks_equity_smalltarget_frozen.md)

- **V5-stock**: pool of V4 signals (`daytrader_cash_tuning.find_signal`,
  BASE params, setups 2/3/4, Setup 1 skipped) + Skill-v2 OR-only
  signals; dedup same stock+day by setup rank (setup4=3 > setup3=2 >
  setup2=1 > skill_or=0), then prospective net, then earlier signal.
  Entry = open of next 5-min candle after signal candle.
- **(lA)-stock check**: pooled signal at/after Nifty's first OR break
  of the day, ≤ 11:30, same direction as the break (morning legs only,
  as frozen in the October run).
- Events tagged from `stock_event_calendar_jan_oct_2026.csv` with the
  frozen gate-v1 window (±7 trading days around event / effective
  reaction date): `event_window` or `no_event`, reported separately.
- **T10 (reference combo)**: target +1.0% from entry, stop −0.5%,
  first hit wins on 5-min candles, stop wins a same-candle tie,
  else 15:10 square-off. Net = direction × (exit − entry) × 100 − ₹40,
  provisional per 100 shares.

## Work 1 — Validation (frozen rules, no tuning)

Run V5-stock × T10 on **Jan–Sep 2026** (185 NIFTY trading days,
data/progressive cache). Report per month and total, split
no-event vs event-window: trades, win%, target-hit%, net provisional
per 100 shares, expectancy, max drawdown of the daily-cumulative net
(peak-to-trough over trading days in date order), trades/day
distribution vs the minimum-2/day floor.
Reproduction gate: the same engine must reproduce the October V5 ×
T10 figures from the October run (378 trades, +₹6,502.57 provisional
per 100 shares; no-event 270 trades, +₹11,666.99; event-window
−₹5,164.42) before Jan–Sep numbers are trusted.

## Work 2 — Tuning grid (frozen before scoring)

Target/stop grid, scored on October AND Jan–Sep, all-days and
no-event-only: targets **0.75% / 1.0% / 1.25%** × stops
**0.4% / 0.5% / 0.75%** = 9 combos (T10 = 1.0%/0.5% included).
Same first-hit / stop-wins-tie / 15:10 rules for every combo.
A combo is "best" only if it does not destroy Jan–Sep to win
October: ranked on Jan–Sep no-event net + October no-event net
together, with win% and drawdown shown. No combo is adopted —
stage results only, November 2026 paper validates.

## Diagnostics (labelled diagnostics, NOT rules)

- Per-stock quality table for the best combo, Jan–Oct combined:
  trades, win%, net provisional per 100 shares per stock. Reported
  only; **no stock is dropped by hindsight** — a per-stock filter
  may only be proposed as a November-paper question.
- Entry-timing split (entry before 11:00 vs 11:00 and after) and
  LONG/SHORT split, Jan–Oct, best combo.
- (lA)-stock × T10, Jan–Sep, no-event vs event-window: second-
  candidate check.

## Verdict rule

If Jan–Sep no-event kills V5 × T10 (net ≤ 0 or drawdown swamps the
net), that is stated plainly, and the grid is checked for anything
that survives Jan–Sep. Nothing is adopted on in-sample data.
