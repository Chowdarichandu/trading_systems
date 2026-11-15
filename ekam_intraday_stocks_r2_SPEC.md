# EKAM-INTRADAY — STOCKS · ROUND 2 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 2: tune the vote-decay exit (X2).
Round 1 (`ekam_intraday_stocks_SPEC.md`, `ekam_intraday_stocks_2026-11-14.md`) found X2
positive in both years at both thresholds while fixed X1 lost in both years. Round 2 moves
ONLY the X2 exit dials, one at a time, from the two published X2 bases. Everything else —
entries, votes, data, fills, caps — is Round 1 verbatim, reused from
`ekam_intraday_stocks_build.py`.
Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares PROVISIONAL** ·
₹40/trade · paper only, real money ₹0. Judged PER YEAR, never pooled.
VWAP remains the equal-weighted typical-price proxy (stores carry no volume).

## CONTROL (must reproduce before any dial moves)

T4-X2 and T5-X2 exactly as published in `ekam_intraday_stocks_results.json` — every
window block (trades, total, WR) for 2025 and 2026, plus the November CF lines.
Any mismatch stops the run.

## BASES

- **T4-X2:** threshold T=4; exit = own-direction votes ≤ 2 at a bar's close → exit at that
  close; hard stop −0.75%; square-off 15:15 (15:10 bar close, per R1 construction).
- **T5-X2:** same with T=5.
Entries identical to R1: first bar per stock per day at ≥ T votes, next bar's open;
≤ 1 trade/stock/day, ≤ 5 trades/day across the list (signal-stamp order, symbol tie-break).

## PARAMETERISED X2 EXIT (the only new machinery)

Exit parameters: decay level D, hard-stop fraction S, optional profit cap C.
Per monitored bar (entry bar → 15:10 bar incl.), in this order:
1. Gap fills at the bar's open: LONG open ≤ stop level → fill at open; if C set, open ≥
   cap level → fill at open (SHORT mirrored).
2. Stop inside the bar's range → fill at the stop level (stop wins over cap if both
   levels are inside the same bar's range — the R1 X1 stop-first convention).
3. If C set, cap level inside the range → fill at the cap level.
4. Decay test at the bar's close: own-direction votes at that bar ≤ D → exit at the close.
If nothing triggers by the 15:10 bar, square-off at its close.
LONG: stop = E·(1−S), cap = E·(1+C). SHORT mirrored. Net: R1 formula, ₹40/trade.
With (D=2, S=0.75%, C=none) this reduces exactly to R1's X2 — that is the control.

## DIALS — one at a time from each base (every step scored, both bases)

1. **Decay level:** D ∈ {1 (later), 2 (base), 3 (earlier)} at S=0.75%, C=none.
2. **Hard stop:** S ∈ {0.50%, 0.75% (base), 1.00%} at D=2, C=none.
3. **Profit cap:** C ∈ {none (base), +1.5%} at D=2, S=0.75%.

## CANDIDATE (combined-after-steps, NOT a fresh discovery)

Per base, one candidate setting = (winning D, winning S, winning C) from the three steps.
**Frozen selection rule, per dial step and per base:** let N25(s), N26(s) be a setting's
full Jan–Oct nets. Eligible settings = those with N25 > 0 AND N26 > 0; if none is
eligible, all settings in the step are eligible. Winner = eligible setting with the
highest (N25 + N26); tie → highest min(N25, N26); further tie → the base level.
The candidate is then scored in full and labelled CAND-T4 / CAND-T5.

## REPORTING (frozen)

- Every scored row (bases, all step settings, candidates), PER YEAR (2025, 2026
  separately): windows Jan–Jun / Jul–Oct / full Jan–Oct — trades, net, WR,
  expectancy per trade (full-year net ÷ trades).
- Candidate rows additionally, per year: month table (Jan–Oct: trades, net), ex-top-3
  (full-year total minus the 3 largest trade nets), November CF (the R1 nine November
  dates), timing audit, and a random-entry placebo.
- **Placebo (candidates only):** 200 draws, fresh `random.Random(20261114)` per
  candidate-year. Each draw = the candidate's real trade count for that year; each placebo
  trade = uniform random tradable stock-day of that year (Jan–Oct) × uniform random entry
  bar (stamps 09:20–15:10 present that day) × uniform random side; exit by the
  candidate's own exit stack on that stock-day's real bars and real vote series.
  Percentile = % of draws whose total is below the real total.
- **Timing audit (candidates):** entry stamp > signal stamp asserted on every trade;
  truncated-series vote recompute on the R1 sample design (every 37th pre-cap candidate,
  T4+T5 combined) must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, stated verbatim in the report)

A candidate is the channel only if: positive in both years AND in both windows of each
year AND expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND placebo ≥ 95th percentile in
both years. The report states plainly whether any row reaches it.
