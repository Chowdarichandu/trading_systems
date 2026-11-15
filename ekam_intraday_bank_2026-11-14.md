# EKAM-INTRADAY — BANK NIFTY · RESULTS · 2026-11-14

Spec: ekam_intraday_bank_SPEC.md (frozen before scoring). Basis: paper, buying only, 1 lot (30), Rs220/trade.
Gate days: 203 (Jan-Oct 2026). Timing audit: PASS (300 signal bars recomputed from truncated series).
VWAP-unavailable bars (gate + November): 0.

## Rows — windows

| Row | Jan-Jun trades | Jan-Jun net | Jan-Jun WR | Jul-Oct trades | Jul-Oct net | Jul-Oct WR | Full trades | Full net | Full WR | Full Rs/trade-day |
|---|---|---|---|---|---|---|---|---|---|---|
| T4-X1 | 119 | -9378.50 | 38.7 | 83 | 9103.00 | 43.4 | 202 | -275.50 | 40.6 | -1.36 |
| T4-X2 | 119 | -7874.00 | 26.9 | 83 | -32442.50 | 26.5 | 202 | -40316.50 | 26.7 | -199.59 |
| T5-X1 | 120 | 5829.00 | 41.7 | 82 | -10204.00 | 37.8 | 202 | -4375.00 | 40.1 | -21.66 |
| T5-X2 | 120 | -7215.00 | 27.5 | 82 | -29570.50 | 25.6 | 202 | -36785.50 | 26.7 | -182.11 |

## Counts (gate window)

| Row | Signals | Late | NC |
|---|---|---|---|
| T4-X1 | 203 | 0 | 1 |
| T4-X2 | 203 | 0 | 1 |
| T5-X1 | 202 | 0 | 0 |
| T5-X2 | 202 | 0 | 0 |

## Vote-count distribution (gate days by the day's max final vote count)

| Max votes M | 0 | 1 | 2 | 3 | 4 | 5 | 6 |
|---|---|---|---|---|---|---|---|
| Days | 0 | 0 | 0 | 0 | 1 | 17 | 185 |

## Placebo (best full-year row)

Best row: T4-X1 (full net Rs-275.50). Random-entry placebo (500 iterations, same count/geometry): percentile 99.8; median Rs-68633.50; p95 Rs-30404.50; max Rs11553.50; dropped draws 0.

## November CF (Nov 2-13, descriptive)

| Row | Trades | Net | WR | Signals | Late | NC |
|---|---|---|---|---|---|---|
| T4-X1 | 8 | -5360.00 | 25.0 | 8 | 0 | 0 |
| T4-X2 | 8 | -9254.00 | 12.5 | 8 | 0 | 0 |
| T5-X1 | 8 | -13760.00 | 0.0 | 8 | 0 | 0 |
| T5-X2 | 8 | -11721.50 | 12.5 | 8 | 0 | 0 |
