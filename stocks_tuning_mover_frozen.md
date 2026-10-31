# Stocks EQUITY — Tuning Loop LINE 5: Morning-Mover Deepening — FROZEN FAMILY LIST

**Frozen BEFORE scoring: 2026-10-31. This file lists the families; no
family may be added, removed, or re-parameterised after scoring
begins. All results are DIAGNOSTICS / observations on in-sample
data (Jan–Oct 2026). Nothing in Line 5 can produce a pass claim,
a rule change, or an adoption — the Line 4 transfer verdict
(Morning-Mover TRANSFERS) already stands and is not re-judged here.**

Equity cash intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders, real money ₹0. Every rupee
figure provisional per 100 shares; net = gross − ₹40/trade flat.
Window Jan–Oct 2026 (October = 1–28 Oct).

## Base rule (MOVER-A, frozen in `stocks_vline_v2_candidate_spec.md`)

Pre-move measured on the stock's own 5-min candles: |close of last
bar before the measurement window end ÷ open of the first DAYCTX
bar − 1| ≥ threshold (frozen 1.0%, window end 10:00). On qualifying
stock-days: the first V5 re-entry-stream signal is DISCARDED, the
next signal is traded, one further re-entry allowed (chain cap 2
trades). Entry = next bar's open after the signal bar; exits T125
(target +1.25% / stop −0.5%, stop-first within a bar, 15:10
square-off) via `replay_plain`; after an exit (or a discard/block)
the signal search restarts at the exit bar (signal bar + 1 after a
discard/block). Tradable unit = the stock-day chain.

## Machinery (reuse, no new signal logic)

- Signal stream: frozen V5 re-entry heads — `stocks_equity_reentry.py`
  (home 25) and `stocks_equity_reentry_ext.py` (new 25), loaded via
  the same head-split as Lines 2b/4.
- Chain builder: the Line 2b parametrized builder (`build_batt`:
  threshold / window_end / same_dir / exit-target parameters),
  run per universe; `replay_plain` and `chain_stats` copied from
  `stocks_tuning_universe.py` (breadth denominator parametrized).
- Validation gates (must reproduce to the paisa BEFORE any Line 5
  number is reported):
  - Home MOVER-A: 424 chains, 698 trades, +₹84,671.74, JM
    +₹52,884.19 / JO +₹31,787.55, Oct +₹16,825.42, breadth 16/25.
  - Ext MOVER-A: 199 chains, 300 trades, +₹164,483.29, JM
    +₹73,142.55 / JO +₹91,340.74, Oct +₹39,984.55, breadth 22/25.
  - Pooled MOVER-A: 623 chains, +₹249,155.03, JM +₹126,026.74 /
    JO +₹123,128.29, Oct +₹56,809.97, breadth 38/50, top-3 34.1%.
  - Home MOVER-B (10:15): 589 chains, 941 trades, +₹169,328.31,
    JM +₹92,266.39 / JO +₹77,061.92, Oct +₹36,815.02, breadth 24/25.
  - Home SAME-direction: 385 chains, 639 trades, +₹92,923.38, JM
    +₹58,622.78 / JO +₹34,300.60, Oct +₹16,885.05, breadth 18/25.
  - Home mover-DOWN partition: 221 chains, +₹58,812.88, JM
    +₹30,199.64 / JO +₹28,613.24, Oct +₹14,421.94, breadth 19/25.

## Families (the complete list — nothing else is scored)

- **M1 — MOVER-B (10:15 measurement) off-home.** Window end 10:15,
  threshold 1.0%, ANY direction, T125, cap 2. Scored on (i) the NEW
  25 alone and (ii) the POOLED 50 (home 10:15 chains + ext 10:15
  chains). Read: chains, net, halves, October, breadth,
  expectancy/chain. Verdict language: replicates / does not
  replicate / mixed, judged against the home read (10:15 stronger
  than 10:00 on net, halves and breadth).
- **M2 — Threshold plateau on the NEW 25.** Window 10:00, ANY
  direction, T125, cap 2; thresholds {0.75%, 1.0% (anchor), 1.25%,
  1.5%}. Read per threshold: chains, net, halves, October,
  breadth, expectancy/chain. Verdict: plateau or cliff, off-home,
  by the same read as home Line 2b R1.
- **M3 — SAME-direction variant on the NEW 25.** Window 10:00,
  threshold 1.0%, post-discard signals must match the sign of the
  pre-10:00 move (others consumed without entry/cost/cap), T125,
  cap 2. Read vs ext MOVER-A (ANY). Verdict: helps / hurts /
  neutral off-home.
- **M4 — MOVER-DOWN ONLY on the POOLED 50.** MOVER-A pooled
  chains partitioned by the sign of the pre-10:00 move; the
  pre-move-DOWN subset alone. Read: chains, net, halves, October,
  breadth of 50, top-3 share. (Mover-UP subset reported as context
  only.) This is the "half-rule" read: how much of the pooled
  book is the down flank alone.
- **M5 — POOLED-50 month table for MOVER-A.** Per month Jan–Oct:
  chains, trades, net, cumulative net. Plus worst month and the
  top-2 months' share of the total net.
- **M6 — Exit check on the POOLED 50.** MOVER-A rebuilt on both
  universes with exit target 1.0% (T10, stop −0.5% unchanged —
  chains re-form because the search restarts at each exit bar)
  vs the frozen T125 anchor. One cell each. Read: chains, trades,
  net, halves, October, breadth, expectancy/chain. Verdict: is
  the exit preference stable at scale?

## Reporting discipline

- Report: `stocks_tuning_mover_report.md`, written incrementally,
  one section per family, each with a verdict line (replicates /
  does not replicate / mixed for M1–M3; descriptive reads for
  M4–M6).
- Any pattern worth naming gets an observation name OBS-5-x.
  Observations are NOT adopted, NOT written into any candidate
  spec, and earn nothing beyond a possible future line with its
  own frozen spec and fresh window.
- No frozen rule changes. No new pass claims. The November exams
  (N4-V3 primary, INV1 + P2F shadows) are untouched by this line.
