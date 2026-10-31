# Line S3 — Volatility-Compression Breakout — FROZEN CELLS (pre-scoring)

Frozen 2026-10-31 BEFORE any scoring. Equity cash intraday, LONG/SHORT
language only, no options. Paper only, real ₹0. All figures provisional
per 100 shares, net = gross − ₹40/trade. Window Jan–Oct 2026 (trade day
must fall in 2026-01-01..2026-10-31; home Oct as cached 1–28, ext Oct as
cached). POOLED 50 primary; home (25) / ext (25) splits reported.

## Patterns (qualifier day D — all information complete at D's close)

Daily OHLC derived from the same 5-min cache used for triggers
(open = first bar open, high = max bar high, low = min bar low,
close = last bar close).

- **P-A NR7:** range(D) = high(D) − low(D) is the smallest of the last 7
  sessions including D: range(D) ≤ min(range(D−6..D−1)). Ties qualify.
  Requires 6 prior sessions of history.
- **P-B INSIDE DAY:** high(D) ≤ high(D−1) AND low(D) ≥ low(D−1).
- **P-A∪P-B:** union of the two qualifier sets (a stock-day qualifying
  under either or both counts once, with D's high/low as levels).

## Trade construction (trade day = D+1, the next session)

- Levels: resistance = high(D), support = low(D).
- Scan D+1's 5-min bars in time order. The FIRST bar whose CLOSE is
  above high(D) triggers a LONG; the FIRST bar whose CLOSE is below
  low(D) triggers a SHORT. Only the first trigger of the day counts
  (if both levels break, the earlier close-trigger wins). One trade
  per stock per pattern day.
- Entry = open of the bar immediately AFTER the trigger bar. If the
  trigger bar is the day's last bar, no trade.
- Exits (programme `replay_plain`, stop checked before target within a
  bar, 15:10 square-off at that bar's close; if no 15:10 bar, last
  bar's close):
  - **T125/S050:** target +1.25%, stop −0.50%
  - **T10/S050:** target +1.00%, stop −0.50%

## Cells (6)

| Cell | Pattern | Exits |
|------|---------|-------|
| S3-A1 | P-A NR7 | T125/S050 |
| S3-A2 | P-A NR7 | T10/S050 |
| S3-B1 | P-B Inside | T125/S050 |
| S3-B2 | P-B Inside | T10/S050 |
| S3-U1 | P-A∪P-B | T125/S050 |
| S3-U2 | P-A∪P-B | T10/S050 |

## Timing audit (same run as scoring — abort before printing scores if it fails)

For EVERY trade in EVERY cell, assert programmatically:
1. trade_date is a strictly later session than pattern_date D
   (information complete at D's close; entry is on a later day);
2. entry bar timestamp is strictly after the trigger bar timestamp on
   the trade day (entry = following bar's open);
3. entry price equals the open of the bar following the trigger bar.
Violation count must be 0 across all trades.

## Placebo (same run, on the best cell by pooled net)

Identical machinery and exits, but the trade day is **D+6** — the 6th
session after D (D+1..D+5 skipped) — still using D's high/low as
levels. A real compression-expansion effect must beat the placebo
clearly (placebo pooled net < candidate pooled net, and placebo must
not itself pass the gate).

## Gate → candidate

Pooled: both halves (Jan–May / Jun–Oct, by trade date) > 0 AND
breadth ≥ 35/50 AND October > 0 AND timing audit clean AND placebo
beaten. A passing cell is frozen as `stocks_S3_candidate_spec.md`
with a December fresh-window judging rule. All cells reported fully
regardless: trades, net, halves, October, breadth, expectancy,
top-3 share.
