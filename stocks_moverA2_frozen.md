# MOVER-A → A2 TUNING — FROZEN SPEC — 2026-10-31

**FROZEN BEFORE SCORING.** Equity cash intraday only. LONG/SHORT.
Paper only, no orders. Real money ₹0. All figures provisional per
100 shares, ₹40/trade flat. Window Jan–Oct 2026 (Oct 1–28).
This file may not be edited after scoring begins; any change of
mind is a new spec, not an edit.

## Base system — MOVER-A (frozen, from stocks_vline_v2_candidate_spec.md)

Universe: pooled 50 = the 25 watchlist ("home", signal stream from
`stocks_equity_reentry.py`) + the 25 large-cap extension ("ext",
signal stream from `stocks_equity_reentry_ext.py`). Signal stream =
frozen V5 re-entry stream (pool_pick over v4_head/skor_head; entry =
next bar's open after the signal; next search starts at the previous
exit bar).

For each stock-day:
1. Pre-move test (known at 10:00): day open = first 5-min bar's
   open; pre-close = close of the last bar with time < 10:00. Day
   qualifies iff |pre-close / day open − 1| ≥ 1.0%.
2. Non-qualifying days: no trades.
3. Qualifying days: discard the day's first signal entirely (no
   trade, no cost). Trade the next signal at T125 (target +1.25% /
   stop −0.5%; replay scans from the entry bar, stop checked before
   target within a bar, 15:10 square-off at that bar's close).
   After that trade exits, ONE further re-entry is allowed if
   another signal occurs (also T125). **Chain cap = 2 trades per
   stock-day.** Traded signals may be in EITHER direction
   (any-direction definition), regardless of the pre-move's sign.
4. No ADR filter, no morning-entry cutoff, no event filter, no
   per-stock exclusions.

### Base anchors (must reproduce to the paisa before any scoring)

- Home: 424 chains, 698 trades, net **+₹84,671.74** (Jan–May
  +₹52,884.19 / Jun–Oct +₹31,787.55; October +₹16,825.42; breadth
  16/25; direct leg 424 trades +₹93,575.31; re-entry leg 274
  trades −₹8,903.57).
- Ext: 199 chains, 300 trades, net **+₹164,483.29** (Jan–May
  +₹73,142.55 / Jun–Oct +₹91,340.74; October +₹39,984.55; breadth
  22/25).
- Pooled 50: 623 chains, 998 trades, net **+₹249,155.03** (Jan–May
  +₹126,026.74 / Jun–Oct +₹123,128.29; October +₹56,809.97;
  breadth 38/50; top-3 share 34.1%).
- Base pooled losing months (3): Jan −₹9,886.28, Feb −₹190.30,
  May −₹2,312.51.

## Scoring convention (all families)

Primary book = **pooled 50**; home and ext splits also reported.
Per family report: chains, trades, net, Jan–May net, Jun–Oct net,
full month table (chains + net per month Jan–Oct), losing months
count, October net, breadth (stocks net-positive by chain total,
of 50), top-3 share of net, expectancy per chain. Chain accounting:
a chain = one qualifying stock-day's trades; chain net = sum of
its trade nets.

## IMPROVER GATE for A2 candidacy (all legs must hold, pooled 50)

1. Pooled net **> +₹249,155.03** (beats base).
2. Jan–May net > 0 AND Jun–Oct net > 0.
3. Breadth ≥ 35/50.
4. Losing months ≤ 3 (base's count).
5. October net > 0.

A family passing all five legs is frozen as
`stocks_moverA2_candidate_spec.md` for a fresh window. November
2026's frozen shadows (incl. Morning-Mover home/ext A/B) are NOT
touched by anything in this tuning line.

## Families (scored in this order, one structural change at a time)

### A2-1 — DIRECT-ONLY
Base rule with chain cap = 1: after the direct (post-discard)
trade exits, the stock-day is done; the re-entry leg is dropped
entirely. Everything else identical to base.

### A2-2 — SAME-DIRECTION
Base rule (cap 2) plus: a traded signal counts only if its
direction matches the pre-move's sign (pre-move up → LONG signals
only; pre-move down → SHORT signals only). A non-matching signal
is consumed (search continues after its signal bar; no entry, no
cost, does not use the chain cap) — identical consumption
semantics to the Line 2b `same_dir` mode. The first-signal
discard is unchanged and applies before this test.

### A2-3 — DIRECT-ONLY + SAME-DIRECTION
A2-1 and A2-2 combined: cap 1 AND same-direction requirement.

### A2-4 — MEASUREMENT MICRO-STEPS
Base rule (cap 2, any-direction, T125) with the pre-move measured
to the close of the last bar with time < **10:05** (cell A2-4a)
and < **10:10** (cell A2-4b) instead of < 10:00. Threshold stays
1.0%. (Both cells sit strictly between MOVER-A 10:00 and MOVER-B
10:15.)

### A2-5 — EXIT VARIANTS
Applied to the best configuration among {A2-1, A2-2, A2-3, A2-4a,
A2-4b}, where "best" = highest pooled net (ties: higher breadth,
then earlier family order). That family's exact builder
configuration (window, cap, direction mode) is kept; only the
exit changes:
- Cell A2-5a: target +1.5% / stop −0.5%.
- Cell A2-5b: target +1.25% / stop −0.65%.
Replay convention unchanged (scan from entry bar; stop before
target within a bar; 15:10 square-off).

### A2-6 — FLANK RULE (asymmetric)
Base rule (cap 2, T125, 10:00 measurement) plus an asymmetric
direction test on traded signals:
- Mover-UP days (pre-move > 0): a signal counts only if it is
  same-direction (LONG); a SHORT signal is consumed exactly as
  in A2-2 (search continues, no cost, no cap use).
- Mover-DOWN days (pre-move < 0): unchanged — signals of either
  direction count, exactly as base.
The first-signal discard is unchanged.

## Honesty clauses

- Everything here is in-sample on Jan–Oct 2026, the same window
  the base rule was discovered on. A gate pass earns a
  fresh-window test only — it is not adoption and not evidence
  the improvement is real.
- All six families are reported, including failures; no family
  is dropped from the report because it lost.
- No per-trade hindsight filters, no per-stock exclusions, no
  parameter outside the frozen lists above.
