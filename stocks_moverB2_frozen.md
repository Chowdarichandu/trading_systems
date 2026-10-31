# Stocks EQUITY — MOVER-B2 Tuning: FROZEN SPEC

**Frozen BEFORE scoring: 2026-10-31. Families B2-1 through B2-6 below are
the complete list, in order. No family may be added, removed, or
re-parameterised after scoring begins.**

Equity cash intraday only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders, real money ₹0. Every rupee figure is
provisional per 100 shares; net = gross − ₹40/trade flat. Window
Jan–Oct 2026 (October = 1–28 Oct in both universes).

## Base: MOVER-B (frozen, NOT modified by this line)

Pre-move measured on the stock's own 5-min candles: |close of last bar
before 10:15 ÷ open of the first bar of the day − 1| ≥ 1.0%. On
qualifying stock-days: the first V5 re-entry-stream signal is
DISCARDED, the next signal is traded (any direction), one further
re-entry allowed (chain cap 2 trades). Entry = next bar's open after
the signal bar; exits T125 (target +1.25% / stop −0.5%, stop-first
within a bar, 15:10 square-off); after an exit (or a discard/block)
the signal search restarts at the exit bar (signal bar + 1 after a
discard/block). Tradable unit = the stock-day chain. Signal stream:
the frozen V5 re-entry heads (home `stocks_equity_reentry.py`, ext
`stocks_equity_reentry_ext.py`); chain builder = the Line 5
parametrised `build_batt` machinery, extended only with a chain-cap
parameter where a family states one.

## Validation anchors (must reproduce to the paisa BEFORE scoring)

- HOME-B (10:15): 589 chains, 941 trades, +₹169,328.31, Jan–May
  +₹92,266.39 / Jun–Oct +₹77,061.92, Oct +₹36,815.02, breadth 24/25.
- EXT-B (10:15): 328 chains, 481 trades, +₹295,288.72, Jan–May
  +₹151,540.58 / Jun–Oct +₹143,748.14, Oct +₹81,933.52, breadth 25/25.
- POOLED-B (50): 917 chains, 1,422 trades, +₹464,617.03, Jan–May
  +₹243,806.97 / Jun–Oct +₹220,810.06, Oct +₹118,748.54, breadth
  49/50. Max drawdown by the risk-card method (daily-aggregated net,
  cumulative from 0 over traded days): −₹17,471.45. Base pooled
  monthly nets (₹): Jan +20,654.74 · Feb +18,593.73 · Mar
  +113,901.46 · Apr +56,999.06 · May +33,657.98 · Jun +49,709.85 ·
  Jul +9,747.90 · Aug +12,887.79 · Sep +29,715.98 · Oct +118,748.54
  — no losing month.

## Scoring

- PRIMARY score = POOLED 50 (home chains + ext chains). Home and ext
  splits are also reported for every family.
- Every family reports: chains, trades, net, halves (Jan–May /
  Jun–Oct chain nets), losing months (pooled month table), October
  net, breadth (stocks with positive total net ÷ universe size),
  top-3 share (top-3 positive per-stock nets ÷ total net, Line 5
  `chain_stats` convention), expectancy per chain.
- Max drawdown (risk-card method above) is computed for the best
  two families by pooled net among B2-1..B2-6 (and for the base).

## IMPROVER GATE for B2 candidacy (all legs, pooled 50)

1. Pooled net **> +₹464,617.03** (strictly greater than base B), AND
2. both halves net-positive, AND
3. breadth ≥ 45/50, AND
4. max drawdown no worse than −₹25,000 (risk-card method), AND
5. no losing month in the pooled month table.

A family passing all five legs is frozen as the B2 candidate
(`stocks_moverB2_candidate_spec.md`) for a FRESH window. November's
frozen A/B shadows are NOT touched by this line, whatever the
outcome. If several families pass, the candidate is the passing
family with the highest pooled net (ties broken by the lower
family number); the others are recorded as passing alternates.

## Families (complete list, scored in this order)

- **B2-1 DIRECT-ONLY.** Base B with chain cap 1 — the re-entry
  (round-2) leg is dropped entirely. Everything else frozen
  (10:15, 1.0%, any direction, T125).
- **B2-2 SAME-DIRECTION.** Base B (cap 2) with the traded signals
  required to match the sign of the pre-10:15 move; non-matching
  post-discard signals are consumed without entry, cost or cap
  (Line 2b/5 `same_dir` semantics).
- **B2-3 COMBINED.** B2-1 + B2-2 together: cap 1 AND same-direction.
- **B2-4 MEASUREMENT MICRO-STEPS.** Base B (cap 2, any direction,
  T125, 1.0%) with the measurement window end moved to (a) 10:20
  and (b) 10:30 — two cells, reported separately.
- **B2-5 THRESHOLD.** Base B (10:15, cap 2, any direction, T125)
  with the pre-move threshold at (a) 0.75% and (b) 1.25% — two
  cells, reported separately.
- **B2-6 EXIT VARIANTS.** Applied to the best configuration among
  B2-1..B2-5 (best = highest pooled net; ties broken by lower
  family/cell order) — that configuration rebuilt with (a) target
  +1.5% / stop −0.5% and (b) target +1.25% / stop −0.65%. Chains
  re-form under each exit (the signal search restarts at each exit
  bar), so each cell is a full rebuild, not a repricing. If the
  best of B2-1..B2-5 is the unmodified base configuration reached
  via no family, B2-6 applies to the base itself. Both cells are
  scored against the same improver gate.

## Reporting discipline

- Report: `stocks_moverB2_report.md`, written incrementally — the
  anchor-validation section first, then one section per family
  with a gate verdict per family/cell.
- Trade dumps: `moverB2_<FAMILY>_trades.csv` per family/cell;
  results JSON: `stocks_moverB2_results.json`; engine:
  `stocks_moverB2.py`.
- In-sample Jan–Oct tuning only. A B2 candidate, if any, is a
  candidate for a fresh window — it is NOT adopted, and November's
  frozen exams proceed exactly as already scheduled.
