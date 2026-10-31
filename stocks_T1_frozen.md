# Line T1 — The Combined Real Book — FROZEN combination rules

Frozen 2026-10-31, BEFORE any combined figure is computed.
Equity cash intraday, LONG/SHORT. Paper only, real money ₹0, no orders.
All figures provisional per 100 shares, ₹40/trade cost already deducted
(the dumps' net columns are post-cost). Window Jan–Oct 2026
(October = 1–28 Oct in the 5-min work). HOME 25 universe only —
no ext pooling (INV-LONG and P2F both failed transfer to the ext 25).

## Components (existing dumps, exact subset definitions)

1. **INV-LONG** — dump `tuning_inv_T1_T125_S050_trades.csv`,
   subset: rows with `direction == LONG`.
   Published: 249 trades, **+₹24,185.73**.
   Net column: `net_rs_provisional_per100`. Stock column: `stock`.
2. **N4-V3 at T125** — dump `eq_n4deep_v3_trades_T125_janoct.csv`, all rows.
   Published: 56 trades, **+₹7,990.43**.
   Net column: `net_rs_provisional_per100`. Stock column: `stock`.
3. **P2F at the 2.5% band** — dump
   `stocks_tuning_event_V1_combined_trades.csv`,
   subset: rows with `leg == P2F` AND `|reaction_ret_pct| >= 2.5`.
   Published: 39 trades, **+₹15,489.08**.
   Net column: `net_rs`. Stock column: `symbol`.

## Validation gate (before use)

Each subset must reproduce its published trade count and total to the
paisa (±₹0.01). If any subset fails, the run HALTS and the report says
so — no substitute numbers, no regeneration unless a dump is missing
(none is missing).

## Combination rule (pre-declared)

The three systems run as independent books sharing one report.
If two systems trade the same stock on the same day, BOTH trades count
in full — no netting, no de-duplication, no position interaction.
Report alongside the combined totals:
- total combined trades;
- **collision count**: number of (date, stock) pairs traded by ≥2
  different systems, the number of trades involved in those pairs,
  broken down by system pair, and the net of the colliding trades.

## Reported metrics (definitions fixed here)

- Combined net = sum of all component nets.
- Halves: H1 = Jan–May 2026 (dates 2026-01-01…2026-05-31),
  H2 = Jun–Oct 2026 (2026-06-01…2026-10-31).
- Full month table Jan…Oct: trades + net per month.
- October net (2026-10).
- Breadth: distinct stocks with combined per-stock net > 0, reported
  as x / (distinct stocks traded) and x / 25.
- Expectancy = combined net / combined trades.
- Monthly run-rate = combined net / 10 (months in window), plus the
  median month. Target bar: ~₹25,000/month (≈ ₹250,000 over the
  window), the level of the retracted Morning-Mover claims.

## Stress battery (the tests that killed the EventBook)

EventBook reference (its own frozen stress, for comparison):
+₹20,826.31 in-sample; ex-top-3 stocks −₹3,046.87;
winsorised H1 −₹1,805.21 → KILLED.

1. **Ex-top-3 stocks**: rank stocks by combined per-stock net,
   descending; remove ALL trades of the top 3 stocks; recompute
   net, H1, H2, October.
2. **Winsorised at +₹2,000/stock**: (a) total — each stock's combined
   net contribution capped at +₹2,000 (stocks at or below the cap,
   including negatives, unchanged); (b) halves — within each half,
   each stock's half-net capped at +₹2,000 by the same rule.
   Recompute net, H1, H2.
3. **Ex-top-3 trades**: remove the 3 individual trades with the
   largest net from the combined book; recompute net, H1, H2, October.

## Verdict rule (fixed here)

The combined book **SURVIVES stress** iff under test 1 (ex-top-3
stocks) the net is positive AND both halves are positive — the exact
leg the EventBook failed. Tests 2 and 3 are supporting evidence and
are reported in full either way.
- Survives → freeze `stocks_T1_combined_candidate_spec.md` with a
  December fresh-window judging rule.
- Falls → no candidate; the report names which component's
  concentration does the damage (per-component ex-top-3 diagnostics:
  each component's own top stocks and their share of the combined net).

## What this line may NOT do

No re-tuning, no subset changes, no exit changes, no adding or
dropping a component after seeing combined numbers. One combination,
computed once, judged by the rule above.
