# EKAM-INTRADAY — STOCKS · ROUND 5 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 5: the selection turn.
Round 4 (`ekam_intraday_stocks_r4_2026-11-14.md`) required the full 6 of 6 votes at
entry (CAND-T6). The trade count did NOT fall — 1,035 (2025) / 1,025 (2026), exactly
the control's counts — because the 5-trades/day cap is saturated in both books: on
essentially every trading day at least five names reach a 6-vote bar. The turn only
**re-selected** the book, and made it worse (CAND-T6 +₹54,052.39 / +₹17,521.36 vs
control CAND-T5 +₹62,164.57 / +₹63,883.60; November +₹962.75 vs +₹24,528.65).

Diagnosis carried into this round: **the binding constraint is WHICH 5 trades a day
get picked.** The day cap binds every day; the selection rule that fills it is the
untested dial. This round tunes the selection itself. Everything else — votes,
entries, exits, caps per stock — is R1/R2 verbatim, reused from
`ekam_intraday_stocks_build.py` (R1) and `ekam_intraday_stocks_r2_build.py` (R2).
Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR, never pooled.
VWAP remains the equal-weighted typical-price proxy (stores carry no volume).

## CONTROL (must reproduce before anything else)

**S0 = CAND-T5 exactly** as published in `ekam_intraday_stocks_r2_results.json`:
T=5 post-cap contexts (R2 `build_contexts`, day cap = earliest 5 qualifying
first-signals, sorted by (signal_stamp, sym)), exit D=3, S=1.00%, C=none:
every window block (trades, total, WR) for 2025 and 2026, the month tables,
ex-top-3, and the November CF line (2025 **+₹62,164.57** · 2026 **+₹63,883.60** ·
November **+₹24,528.65**). Any mismatch stops the run.

## THE ROWS — only the day-cap selection changes

Every row uses the SAME pre-cap candidate set (each stock-day's first ≥5-vote
signal, R1 `day_candidates` at T=5), the SAME contexts, the SAME CAND-T5 exit
stack (vote-decay exit at own votes ≤ 3, hard stop −1.00%, no cap, square-off at
the 15:10 bar's close), and ≤ 1 trade per stock per day. Only the rule that picks
the day's trades out of the candidate list changes:

- **S0 — EARLIEST-5 (control).** Candidates sorted by (signal_stamp, sym); take
  the first 5. (R2 verbatim.)
- **S1 — PRIORITY-5 (causal bucket cap).** Partition the day's candidates by
  signal stamp: bucket A = signal_stamp < "11:00" (signals stamped 09:15–10:55),
  bucket B = signal_stamp ≥ "11:00". Take the earliest 3 of bucket A and the
  earliest 2 of bucket B (earliest = (signal_stamp, sym) order within the bucket);
  day total ≤ 5. **Causality:** a signal's admission depends only on its own
  timestamp and on how many *earlier* signals in its own bucket have already been
  admitted; no signal is ever displaced by a later one and no end-of-day
  information is used. (Ranking the day's signals by strength after the fact —
  "strongest-5" — would be look-ahead for intraday entries and is NOT scored.)
- **S2 — EARLIEST-3.** Candidates sorted by (signal_stamp, sym); take the first 3.
- **S3 — FIRST-HOUR-ONLY.** Only candidates with signal_stamp ≤ "10:30" (the
  10:30 bar included) are eligible; take the earliest 5 of those.

## REPORTING (per row, per year — 2025, 2026 separately, never pooled)

Windows Jan–Jun / Jul–Oct / full Jan–Oct: trades, net, WR, expectancy per trade
(window net ÷ trades). Plus, per year: ex-top-3 (full-year total minus the 3
largest trade nets), November CF (the R1 nine November dates), and a random-entry
placebo by the R2 design verbatim (200 draws, fresh `random.Random(20261114)` per
row-year; each draw = the row's real trade count for that year; each placebo
trade = uniform random tradable stock-day of that year × uniform random entry bar
09:20–15:10 × uniform random side; exit by the CAND exit stack D=3 / S=1.00% /
C=none on that stock-day's real bars and real vote series; percentile = % of
draws below the real total). Month table (Jan–Oct) reported for the **best row**:
the non-control row (S1/S2/S3) with the highest combined two-year full total
(tie-break: higher minimum year, then S1 before S2 before S3).

**Timing audit:** entry stamp > signal stamp asserted on every trade of every
row (structural in the context builder); plus the R2 truncated-series vote
recompute (every 37th pre-cap T=5 candidate) must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, re-checked for EVERY row, S0 included)

A row is the channel only if: positive in both years AND in both windows of each
year AND full-year expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND placebo
≥ 95th percentile in both years. The report states the checklist verdict plainly,
line by line, per row per year.
