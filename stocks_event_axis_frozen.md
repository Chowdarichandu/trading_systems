# Stocks EQUITY — EVENT-AXIS invention (Workstream A) — FROZEN 2026-10-31, BEFORE SCORING

**Status: FROZEN 2026-10-31, before any Workstream A scoring run.
NOT adopted, NOT a live system. Paper only, no orders.**
**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Every rupee figure: provisional per 100 shares.
Cost: ₹40 per completed round trip (one entry + one exit = one
trade = ₹40 total) — the identical convention used in every
engine in this workspace (net = gross − ₹40 per round trip).**
Window: Jan–Oct 2026 (Oct = 1–28 Oct), 25 stocks, 203 trading
days. Halves: Jan–May (99 days) / Jun–Oct (104 days).

## Why this workstream exists

Every prior round keeps producing the same observation:
event-window trades are net-positive even inside losing families
(Part 3: D1 kept +₹8,714.61, D2 +₹7,829.61, X2-T10 +₹13,384.53,
X2-HOLD +₹20,356.67 provisional per 100 shares) while no-event
trades carry the losses. The only both-halves net-positive
families on record (N4-V3, INV1 in-sample) live on the event
axis. This workstream tests the event axis directly, three ways.

## Event windows — exact definitions (shared by EA1)

Built from `stock_event_calendar_jan_oct_2026.csv` per stock,
using the stock's own daily-candle trading-day list and index —
byte-identical construction to `stocks_hunt1.build_windows`:

- Effective reaction date `eff` = the calendar `reaction_date`
  if it exists and event_date ≤ reaction_date ≤ event_date + 7
  calendar days, else the `event_date` itself.
- **WIDE window** = trading days from (index of event_date − 7)
  through (index of eff + 7). This is exactly the `event_status`
  / `event` tag already frozen into the source trade CSVs; EA1
  re-derives it and must reproduce the CSV tag with **0
  mismatches** per pool before any subset is scored (validation
  gate — mismatches, if any, are reported and the CSV tag is
  canonical).
- **NARROW window** = trading days from (index of eff − 2)
  through (index of eff + 2) — "reaction ±2 trading days".

## EA1 — event-only restriction of the strongest existing pools

Pools (frozen trade sets, nets already include the ₹40 cost):

- **P-V3**: ladder+volume V3 (Part 2) —
  `newstratvol_V3_trades.csv` (3,275 trades; published total
  −₹16,284.00 provisional per 100 shares — must reproduce).
- **P-P2**: the full P2 pool at its primary exit T125/S050 —
  `eq_round8_P2_T125_S050.csv` (918 trades; published total
  +₹10,657.81 — must reproduce).
- **P-INV1**: the INV1 subset of P2 at T125/S050 —
  `eq_round10_INV1_trades_T125.csv` (694 trades; published
  total +₹22,964.30 — must reproduce).

Families: each pool × {WIDE-only, NARROW-only} = 6 families.
The no-event complement of each pool is reported for context
only (not a family). Metrics per family: trades, win % (net>0),
net Jan–May, net Jun–Oct, net Jan–Oct, net October, gross
expectancy/trade (= mean net + ₹40), breadth = number of the 25
stocks with positive family net over Jan–Oct, top-3 share of
family total net (reported only when total > 0).

**Gate (same bar as the rest of this work):** a family passes
only if net > 0 in BOTH halves AND breadth ≥ 10/25 stocks
positive AND (when total > 0) top-3 share ≤ 75%. A pass earns a
frozen paper spec; anything else is reported as a near-miss or
rejection with its numbers, not smoothed over.

## EA2 — event-proximity drift (NEW; scheduled RESULTS only)

- Chain: for each stock, its `results` rows in the calendar in
  event_date order. An event is scorable only if a PREVIOUS
  results event for the same stock exists in the calendar
  (in-file chain). Skips are counted by reason: no previous
  in-file event; previous event's eff reaction day missing from
  the stock's daily candles; previous reaction-day close == open
  (zero sign); current anchor days missing (below).
- Direction (ex-ante): sign of (close − open) on the PREVIOUS
  event's eff reaction day, from the stock's daily candles.
  Positive → LONG this event's drift window; negative → SHORT.
- Anchor: R = index of the CURRENT event's eff reaction date in
  the stock's daily trading-day list. **Enter at the OPEN of
  trading day R−2; exit at the CLOSE of trading day R−1.**
  Trade half assignment: by entry date (R−2).
- P&L per trade: sign × (exit close − entry open) × 100 − ₹40
  (ONE round trip = ₹40 total, stated per the workspace
  convention above).
- **This is a 2-trading-day hold with overnight exposure — NOT
  intraday.** It is scored and judged separately from every
  intraday family, and any paper spec earned must say so.
- Metrics + gate: identical to EA1 (both halves > 0, breadth
  ≥ 10/25, top-3 ≤ 75% when total > 0).

## EA3 — reaction-day volume confirmation on N4-V3

- Trades: N4-V3 combined reaction trades from the frozen
  n4deep run — `eq_n4deep_v3_trades_T125_janoct.csv` (56
  trades, PRIMARY exit T125) and `eq_n4deep_v3_trades_T10_janoct.csv`
  (same entries at T10, secondary).
- Volume pace for a trade (stock s, reaction day D), from
  `data/progressive_vol/<s>/spot_5m_vol.csv`:
  pace = (Σ volume of the 09:15, 09:20 and 09:25 bars on D) ÷
  (mean of the same 3-bar sum over the 20 trading days
  immediately before D present in the vol file).
  The trigger itself is fixed by the 09:25 bar close, so volume
  through the 09:25 bar is known before the 09:30-bar-close
  entry — the filter is ex-ante. Days with < 10 prior vol days,
  a missing 09:15/09:20/09:25 bar, or a zero denominator are
  **unclassifiable**: counted, excluded from KEPT, listed with
  the DROPPED set in reporting (never silently dropped).
- KEPT = pace ≥ 1.0. Report KEPT vs DROPPED vs full set:
  trades, win %, net both halves, net total, expectancy/trade,
  at T125 (primary) and T10 (secondary).
- **EA3 pass bar (frozen):** KEPT net > 0 in both halves AND
  KEPT expectancy ≥ full-set expectancy in EACH half AND KEPT
  sample ≥ 20 trades total with ≥ 5 in each half. Failing the
  sample floor = "insufficient sample" observation, not a pass
  and not a kill.

## What this spec does NOT do

- No re-scoring or re-tuning of the source pools; EA1 subsets
  frozen trade sets, EA3 filters frozen trades, EA2 is the only
  new trade generator.
- No direction filters built from the LONG/SHORT diagnostics of
  prior rounds.
- No pooling with index work; no November claims (Workstream B
  is a dry run on 2026-10-30 data only and writes only dry-run
  files).
