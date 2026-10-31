# Stocks October 2026 — clubbed backtest (Run 1, Run 2, Unified)

Paper only. No orders placed. No live trading claimed. October is 18 trading
days only and is NOT proof of edge.

## Provisional cash rules — NOT Chandu's rules, labelled everywhere
100 shares/trade for comparison only; Rs 40/trade assumed cost (not actual
brokerage); stop = signal-candle low (long) / high (short); target = 2x stop
distance; square-off 15:10; one trade/instrument/day; V4 point thresholds
scaled by prev-close/55,000; Setup 1 skipped (no bands); short signals
paper-only. Capital not shared, so no risk % is computed.
Win rate = targets / all trades (square-offs count as non-wins, as in the
earlier Bank Nifty cash reports). Bank Nifty Jul-Oct 2026 numbers are NOT
carried into this file (removed from forward use as a scope rule).

## Data — verified, not fabricated
Upstox connector helper (search + new read-only V3 candles route added to
~/workspace/custom-connectors/custom.upstox/bin/upstox.py; the helper
previously truncated candle JSON at 8,000 chars, which broke the first
fetch — fixed before any numbers were taken). 25/25 stocks fetched,
1,425 5-min candles each, 19 calendar days 2026-09-30..2026-10-28 in the
file (30 Sep is the prior day only). Trading days in October window: 18
(1, 5-9, 12-16, 19, 21-23, 26-28 Oct; 2 and 20 Oct are absent from Upstox
returns). Daily OHLC derived from the same 5-min bars, as in the Bank
Nifty cash engine. Trade files:
stocks_october/run1_skill_october_trades.csv (450 rows),
stocks_october/run2_v4_october_trades.csv (94 rows),
stocks_october/unified_capped_october_trades.csv (15 rows),
stocks_october/per_stock_october.csv, stocks_october/october_summary.json,
stocks_october/data/*_spot_5m.csv and *_spot_daily.csv,
stocks_october/data/fetch_manifest.json (25/25 ok).

## Headline — portfolio, 18 days, 25 stocks
| Run | Trades | Targets | Stops | Sq-off | Win % | Net Rs | Expectancy Rs | Max DD Rs | Trades/week* |
|---|---|---|---|---|---|---|---|---|---|
| Run 1 — Day Trader skill entries alone | 450 | 144 | 289 | 17 | 32.0 | -33,527 | -74.50 | 33,902 | 125.00 |
| Run 2 — V4 entries, cash | 94 | 32 | 61 | 1 | 34.0 | -7,984 | -84.94 | 9,984 | 26.11 |
| Unified, per stock (= Run 2 entries) | 94 | 32 | 61 | 1 | 34.0 | -7,984 | -84.94 | 9,984 | 26.11 |
| Unified, portfolio-capped (max 3 / ISO week, earliest first) | 15 | 7 | 8 | 0 | 46.7 | +160 | +10.67 | 1,590 | 4.17 |

*Trades/week in this table = trades / (18/5) = trades / 3.6, the same
convention as the earlier cash reports. The capped run held at most 3
trades in each ISO week (weeks 40-44: 3+3+3+3+3), but 4.17 by the
trading-days/5 convention because the first and last ISO weeks are
partial in this window. Either way the capped net (+Rs 160) is flat,
not a good profit.

## X verdict — October, all three together
X = (1) 2-3 quality trades/week portfolio total, (2) good net profit,
(3) good win rate.
- Run 1: FAILS all three — 125/week, -Rs 33,527, 32.0%.
- Run 2: FAILS all three — 26.11/week, -Rs 7,984, 34.0%.
- Unified capped: FAILS — frequency is capped per ISO week but the
  net is +Rs 160 (flat) and win rate 46.7% is not good. The cap does
  not create an edge; it only drops 79 of 94 V4 trades.
No run hits X in October. Do NOT adopt any of them on this window.

## Run 1 composition (450 trades)
OR breakout 194, OR breakdown 167, flag breakout 46, flag breakdown 41,
oversold bounce 2. Long 242, short (paper) 208. The skill entry fires on
essentially every stock every day (450 = 25 x 18), so its October
frequency failure is structural, not a bad week.

## Run 2 composition (94 trades)
Setup 3 bounce rejection 65, Setup 4 reclaim 25, Setup 2 OR breakdown 4.
No Setup 2 breakout and no Setup 4 pullback fired in October. Long 25,
short (paper) 69. Only 7 of 25 stocks were net-positive on Run 2:
OBEROIRLTY +970, ASTRAL +980, BDL +1,160, HINDCOPPER +435, INDUSTOWER +50,
HINDZINC +25, HINDUNILVR +100. Largest Run 2 loser: TVSMOTOR -2,930
(2 trades, both stops).

## Per-stock table
| Symbol | R1 trades | R1 win % | R1 net Rs | R2 trades | R2 win % | R2 net Rs |
|---|---|---|---|---|---|---|
| GODREJCP | 18 | 27.8 | -1,815 | 3 | 33.3 | -655 |
| GLENMARK | 18 | 11.1 | -9,420 | 4 | 25.0 | -1,260 |
| ITC | 18 | 38.9 | -640 | 3 | 33.3 | -115 |
| RECLTD | 18 | 27.8 | -795 | 8 | 37.5 | -380 |
| TVSMOTOR | 18 | 33.3 | -470 | 2 | 0.0 | -2,930 |
| UNITDSPR | 18 | 33.3 | +1,050 | 3 | 0.0 | -930 |
| OBEROIRLTY | 18 | 38.9 | -160 | 4 | 75.0 | +970 |
| NTPC | 18 | 33.3 | -985 | 5 | 40.0 | -270 |
| INDUSTOWER | 18 | 27.8 | -1,660 | 2 | 50.0 | +50 |
| KALYANKJIL | 18 | 22.2 | -3,280 | 5 | 20.0 | -825 |
| HDFCBANK | 18 | 33.3 | -520 | 7 | 0.0 | -1,385 |
| NHPC | 18 | 33.3 | -547 | 6 | 50.0 | -197 |
| PFC | 18 | 33.3 | -225 | 4 | 25.0 | -160 |
| IRCTC | 18 | 16.7 | -2,065 | 5 | 20.0 | -1,370 |
| WIPRO | 18 | 27.8 | -365 | 4 | 25.0 | -211 |
| NATIONALUM | 18 | 44.4 | +795 | 1 | 0.0 | -130 |
| VEDL | 18 | 55.6 | +355 | 3 | 33.3 | -280 |
| HINDCOPPER | 18 | 33.3 | -245 | 3 | 66.7 | +435 |
| HINDZINC | 18 | 33.3 | -1,315 | 5 | 40.0 | +25 |
| HINDALCO | 18 | 38.9 | +1,060 | 2 | 0.0 | -500 |
| TATASTEEL | 18 | 33.3 | -550 | 3 | 66.7 | -96 |
| ASTRAL | 18 | 33.3 | -3,030 | 4 | 25.0 | +980 |
| BDL | 18 | 38.9 | -250 | 3 | 66.7 | +1,160 |
| OIL | 18 | 27.8 | -1,030 | 3 | 66.7 | -10 |
| HINDUNILVR | 18 | 22.2 | -7,420 | 2 | 50.0 | +100 |
| TOTAL | 450 | 32.0 | -33,527 | 94 | 34.0 | -7,984 |

## Unified capped trades (15, chronological, max 3/ISO week)
GLENMARK 2026-10-01 setup3 PE +1,060; NHPC 2026-10-01 setup2 PE -10;
UNITDSPR 2026-10-01 setup2 PE -320; KALYANKJIL 2026-10-05 setup3 PE -140;
RECLTD 2026-10-05 setup3 PE +30; NTPC 2026-10-05 setup3 PE -125;
ASTRAL 2026-10-12 setup3 PE -380; WIPRO 2026-10-13 setup3 PE -88;
GODREJCP 2026-10-13 setup4 CE -425; KALYANKJIL 2026-10-19 setup3 PE +460;
TATASTEEL 2026-10-19 setup3 PE -12; RECLTD 2026-10-19 setup3 PE +60;
GLENMARK 2026-10-26 setup4 CE -400; NTPC 2026-10-26 setup4 CE -240;
HINDCOPPER 2026-10-26 setup4 CE +690. Total +160.

## What this does NOT show
October alone does not validate or invalidate the unified engine.
The next legs in the binding order are stocks Jan-Jun (tune), stocks
Jul-Sep (validation), then Nifty October / Jan-Jun / Jul-Sep, then
unified validation. November forward paper cannot be reported yet
(November has not happened).
