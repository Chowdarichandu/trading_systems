# V-LINE v2 CANDIDATE — Pre-moved skip-first-signal rule — FROZEN 2026-10-31

**STATUS: DIAGNOSTIC-DERIVED CANDIDATE — NOT a scored family
pass, NOT adopted.** This rule was observed as a pre-declared
diagnostic subset inside family U5b of Line 2 (see
`stocks_tuning_vline_report.md`, U5 section). The subset
definition was frozen ex-ante in `stocks_tuning_vline_frozen.md`
before U5 was scored, and the subset is both-halves positive
with breadth 16/25 in-sample — but the decision to elevate it
comes from reading scored output, so under this project's
discipline it earns a **fresh-window test only**. It must not
be re-fitted, filtered, or otherwise adjusted on Jan–Oct 2026
data. November 2026's frozen exams (N4-V3 primary; INV1 and
P2F shadows) are already running and are NOT modified by this
spec — this candidate's first possible window is the next one
after those judgements (December 2026), under a separately
created logging schedule, if the parent thread decides to run
it.

**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders.
Real money ₹0. All figures provisional per 100 shares,
₹40/trade flat.**

## The rule (verbatim from the U5b qualifying-day construction)

Universe: the 25 watchlist stocks; signal stream = the frozen
V5 re-entry stream (`stocks_equity_reentry.py` pool_pick over
v4_head/skor_head, chained as in Round 8: entry = next bar's
open after the signal; next search starts at the previous
exit bar).

For each stock-day:
1. **Pre-moved test (ex-ante, known at 10:00):** let day open =
   the first 5-min bar's open, and pre-close = the close of the
   last bar with time < 10:00. The day qualifies iff
   |pre-close / day open − 1| ≥ 1.0%.
2. **Non-qualifying days: NO TRADES AT ALL under this rule.**
   (This is what distinguishes the candidate from U5b-as-frozen,
   which traded non-qualifying days with the probe construction
   and failed as a whole.)
3. **Qualifying days:** discard the first V5-stream signal of
   the day entirely (no trade, no cost). Trade the next signal
   at **T125 (target +1.25% / stop −0.5%)**, entry at the next
   bar's open, exit replay per the frozen convention (scan from
   the entry bar; stop checked before target within a bar;
   15:10 square-off at that bar's close). After that trade
   exits, ONE further re-entry is allowed if another signal
   occurs (also T125). **Chain cap = 2 trades per stock-day.**
4. If a qualifying day has a first signal but no second signal,
   no trade is taken that day.
5. No ADR filter, no morning-entry cutoff, no event filter,
   no per-stock exclusions. Both directions traded.

## In-sample record (Jan–Oct 2026, reported, NOT a pass)

424 chains, 698 trades, net **+₹84,671.74** provisional per
100 shares (Jan–May +₹52,884.19 on 272 chains; Jun–Oct
+₹31,787.55 on 152 chains; October +₹16,825.42), chain win
rate 55.0%, chain expectancy +₹199.70, breadth 16/25 stocks
net-positive by chain total. Leg split (diagnostic): direct
entries 424 trades +₹93,575.31; second-leg re-entries 274
trades −₹8,903.57. Source: `vline_U5b-SKIP_trades.csv`
(premoved = True rows), analysis in
`stocks_tuning_vline_report.md`.

## Pre-registered judging rule for the fresh window

To be fixed when a logging schedule is created, and stated
here so it cannot drift: over the fresh window, the rule is
**upgraded to candidate** only if its chain-total net at T125
accounting (₹40/trade, per 100 shares) is positive AND it
produced ≥40 qualifying chains; **killed** if the net is
negative; **inconclusive** (extend one more window, identical
rules) if positive but fewer than 40 qualifying chains.
No parameter changes during the window. The negative
second-leg observation is NOT acted on in this version: the
rule above includes the second leg exactly as observed; a
direct-only variant would be a new hypothesis requiring its
own frozen spec, not an edit to this one.

## Honesty clauses

- In-sample only. The Jan–Oct window was used to discover this
  subset; its in-sample figures are evidence for testing it,
  not evidence it works.
- The subset is 424 of 4,111 signal stock-days (~10%): most
  days this rule does nothing.
- Concentration is moderate, not absent: top-3 stocks
  (GLENMARK, BDL, TVSMOTOR) ≈ 61% of the subset net.
