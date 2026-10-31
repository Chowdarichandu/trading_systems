# MOVER-B4 — FROZEN FAMILY LIST (frozen 2026-10-31, BEFORE scoring)

Equity cash intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders, real money ₹0. Every rupee
figure provisional per 100 shares; net = gross − ₹40/trade flat.
Window Jan–Oct 2026 (Oct = 1–28). Scoring on POOLED 50 primary;
home/ext splits reported where the machinery gives them.

## Why this line exists

The B-line's measurement slope never turned: pooled net rose at
every scored measurement step 10:00 → 10:15 → 10:20 → 10:30 →
10:45 → 11:00 → 11:30, and the B3 candidate (measurement 11:30)
sits at the end of that untested slope. Before +₹1.62M is
believed, this line asks what actually causes the profit: the
signal machinery, or simply "stocks that moved ≥1% by late
morning keep drifting in that direction".

## Base and anchor (validate first, before any family is believed)

**B3 candidate** (`stocks_moverB3_candidate_spec.md`): measurement
**11:30**, threshold |pre-move| ≥ 1.0%, discard first signal,
trade the next **same-direction** signal only, chain **cap 1**,
exits **T125/S065** (target +1.25% / stop −0.65%, stop before
target, square-off 15:10). Machinery: `stocks_moverB2.py build()`
(Line 5 `build_batt` semantics + cap parameter), frozen V5
re-entry signal heads, pooled 50 (25 home + 25 ext).

Anchor to reproduce exactly before scoring anything:
pooled 1,694 chains / 1,694 trades / net **+₹1,623,905.15**,
halves Jan–May **+₹951,573.84** / Jun–Oct **+₹672,331.31**,
October **+₹190,471.72**, breadth **49/50**, expectancy
+₹958.62/chain, max DD **−₹11,557.03** (daily-aggregated,
risk-card method), no losing month; home +₹489,399.84 (24/25),
ext +₹1,134,505.31 (25/25).

## Families (score in this order; controls are not candidates)

- **C1 EXTENSION** — B3 candidate configuration with the
  measurement time only changed: **12:00**, **12:30**, **13:00**
  (three cells). Full read per cell: chains, trades, net,
  halves, losing months, October, breadth, expectancy/chain,
  max DD, home/ext splits. Question: does the slope EVER turn?
- **C2 FIXED-TIME CONTROL** — on the SAME qualifying stock-days
  as the B3 candidate (pre-move measured at 11:30, |pre-move|
  ≥ 1.0%), ignore the signal stream entirely: enter at **11:35**
  (open of the first bar after 11:30 — bars are start-labelled,
  so the candle timed "11:35") in the **pre-move's direction**,
  exits T125/S065, one trade per qualifying stock-day, ₹40
  cost. Compared against the B3 candidate on the identical
  qualifying-day set three ways: (i) control net over ALL
  qualifying stock-days vs candidate net (candidate's
  untraded qualifying days count ₹0); (ii) expectancy per
  qualifying stock-day for both; (iii) the control restricted
  to the exact stock-days the candidate traded (isolates the
  entry mechanism on identical days). If the control captures
  most of the profit, the verdict must say plainly that the
  edge is "big morning moves keep drifting", not the signal
  machinery.
- **C3 PLACEBO** — qualify stock-days using **yesterday's**
  full-day move: |close of previous trading day ÷ close of the
  trading day before it − 1| ≥ 1.0% (both closes from the
  stock's own 5-min candle series in the same namespace;
  known at today's open — no information from today is used).
  Then run the B3 candidate's exact intraday machinery with
  the measurement replaced by the placebo: measure nothing
  today; discard the day's first signal; trade the next signal
  **only if its direction agrees with yesterday's move
  direction** (opposite-direction signals skipped, search
  restarts at that signal bar + 1 — identical semantics to
  `build()`); chain cap 1; exits T125/S065. A genuine
  intraday-confirmation effect should collapse under the
  placebo; if the placebo also makes big money, the verdict
  must say plainly that the machinery is harvesting something
  else (e.g. volatile-stock selection).
- **C4 SIGNAL-VALUE DECOMPOSITION** — the B3 candidate's own
  chains split by entry time: (a) entry **before 12:30**,
  (b) entry **12:30–14:00**, (c) entry **after 14:00**
  (entry_time is the entry bar's start label). Chains, net
  and expectancy per bucket. Question: where in the day is
  the candidate's money actually made?

## Verdict and candidate rules for this line

- No new candidate may be frozen from C1 unless the cell beats
  the B3 candidate on the B-line gate (pooled net greater than
  +₹1,623,905.15, both halves positive, breadth ≥ 47/50,
  max DD ≥ −₹25,000, no losing month) **AND** the C2/C3
  controls do not undermine the candidate's mechanism.
- If C2 or C3 undermines the mechanism (control or placebo
  captures most of the candidate's profit on its comparison
  set), the report must state plainly that the **B3 candidate
  is downgraded to UNPROVEN-MECHANISM**, and why — regardless
  of what C1 scores.
- Controls (C2, C3) are diagnostics. Neither may be frozen as
  a candidate from this line, whatever it scores: each was
  defined after the candidate, on the same window.

November's frozen A/B shadows are untouched by this line.
No parameter outside the frozen cells above may be tried.
