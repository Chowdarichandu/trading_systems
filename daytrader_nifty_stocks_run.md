# Clubbed Day Trader + v4 — NIFTY + stocks (new work, 2026-10-29)

PROPRIETARY WORKING FILE for Chandu only. Keep in this workspace only.
Do not publish, share, or describe the unified engine below as a public system.

Paper / historical replay only. No orders placed. No live trading claimed.
No result in this file is a live trade, and no blocked run is claimed as a result.

## What this file is — and what it is not
This file is the NEW work ordered 2026-10-29 07:30 IST. It does NOT redo
the Bank Nifty October result in
[daytrader_october_stocks_run.md](sandbox://workspace/trading/daytrader_october_stocks_run.md).
That old file remains audit-only. Nothing from it is carried into a
combined total in this file.

## (a) Bank Nifty Jul–Oct 2026 — REMOVED / EXCLUDED going forward
Per Chandu's 2026-10-29 07:30 IST instruction, the Jul–Oct 2026 period
for Bank Nifty is excluded from all analysis going forward in this
new work. "If possible" is answered: yes, exclusion is possible, and
it is applied here as a scope rule, not by deleting history.

Exactly what was removed from forward use (all from the old file,
kept there for audit only, NOT reused as baseline, tuning, or
validation, and NOT added to any total here):
- Bank Nifty cash, Jul–Oct 2026 validation period: Run 1 Skill own,
  75 days, 75 trades, 32.0% win, net +Rs 17,200, max DD Rs 149,295,
  5.0 trades/week; Run 2 V4 cash, 75 days, 19 trades, 31.6% win,
  net +Rs 5,550, max DD Rs 77,820, 1.27 trades/week.
- Bank Nifty cash, Jan–Oct 2026 combined totals: Run 1, 185 trades,
  26.5% win, net -Rs 169,825; Run 2, 41 trades, 31.7% win,
  net -Rs 19,955. These combined totals are NOT carried forward.
- All tuning validation that used Jul–Oct 2026: V4 candidate
  (ratio 3, stop 0.5x, room 0%) Jul–Oct validation -Rs 11,513;
  Skill candidate (ratio 3, stop 1.5x) Jul–Oct validation
  +Rs 12,280 at 14.7% win; bias-off / signal-end sensitivities
  that flipped on Jul–Oct validation. None of those validation
  verdicts is reused here.
- Bank Nifty October 2026 cash and options results (Run 1:
  17 trades, +Rs 89,085 provisional cash; Run 2: 5 trades,
  +Rs 67,690 provisional cash; options baseline: 6 trades,
  +Rs 12,180) are also NOT a baseline for this new work, because
  October falls inside Jul–Oct. They remain in the old file for
  audit only. No Bank Nifty number in this new file is a new result.

Replacement focus: NIFTY (not Bank Nifty), with the unified engine
below, plus the 25 stocks, in the order in section (c).

## X — the target, unchanged (all three together)
- 2–3 quality trades per week, PORTFOLIO total (not per stock,
  not per instrument, not hundreds).
- Good net profit.
- Good win rate.
A version that hits net by taking many trades, or win rate by
taking tiny wins, does NOT count as X. X is assessed on
out-of-sample data, never on the period a variant was tuned on.
In this file, X is NOT ASSESSABLE for any run that did not run —
absence of trades is not a pass and not a performance fail.

## Upstox check — single check only, as instructed
- Checked once, 2026-10-29 07:31 IST, after Chandu had already said
  yes to reconnect in the main chat. He is NOT asked again here.
- Commands: `upstox.py search --query BANKNIFTY --segment INDEX`
  and `upstox.py profile`.
- Result: both returned `ERROR: HTTP Error 401: Unauthorized`.
  This matches the earlier 07:22 and 07:25 IST 401s in the old file.
- Action taken: stock and Nifty fetch STOPPED immediately. No loop,
  no retry loop, no fabricated candles, no substituted source
  (no Yahoo, no public OHLC, no other broker).
- Local data check: `~/workspace/trading/data/` holds Bank Nifty
  months only (banknifty-2026-01 to -10, jan-oct, jul-oct). There
  is NO local Nifty 5-min data and NO local stock 5-min data.
  Therefore Nifty and stocks cannot be run from local data either.
- Parent action required (not a new question to the user):
  execute the Upstox reconnect, then resume in the exact order
  in section (c). The engines from the old file are ready and
  need no other change except adding the equity instrument
  search / historical-candle route for stocks and the Nifty
  index-key route for Nifty, which were never reached because
  search itself returned 401.

## Unified engine — the clubbed v4 + Day Trader skill engine to run
This is the proposal from the old file, carried forward unchanged
as the engine to test (NOT adopted as proven):
- FROM SKILL: morning scanner discipline — list OR, flag, and
  oversold candidates every morning; exit-planner discipline —
  stop/target set before entry, square-off before 15:15 IST
  (15:10 in the provisional cash runs below).
- FROM V4: entry filters that create quality over quantity —
  bias gating, PD-level cross for Setup 2, room to the next PD
  level (0.36% of price in the Bank Nifty cash runs), Setup 3
  bounce rejection, Setup 4 reclaim/pullback, one trade per
  instrument per day.
- DROPPED as first-signal entries: flag breakout and oversold
  bounce (flag added losing trades in the old Jan–Jun ablation;
  oversold never fired first). Keep oversold as context only.
- UNIFIED EXIT (provisional, to be validated, NOT Chandu's rule):
  baseline 2x target / 1x signal-candle stop, NOT the tuned
  exits (both won Jan–Jun in the old file and failed or weakened
  on Jul–Oct validation, which is now excluded — so they must be
  re-validated on the new periods, not assumed good or bad).
- FREQUENCY toward X: a portfolio cap, max 2–3 trades/week total,
  best setups first, is part of the unified engine. Unfiltered
  skill signals on 25 stocks would be ~25 trades/week at
  1/day each and would destroy X on frequency alone.

## Provisional rules for every cash run in this new work
(NOT Chandu's rules, labelled as such everywhere — same as old file)
- Size: 100 shares / 100-share equivalent per trade, every
  instrument, solely to convert price points to rupees.
  Not capital-based; capital was not shared, so no risk % is
  computed.
- Cost: Rs 40 flat per trade, assumed, not actual brokerage.
- Exit: signal candle low (long) / high (short) as stop, target =
  2x stop distance (baseline), square-off at 15:10, stop priority
  if both stop and target are hit in one candle. If entry == stop
  level, the trade is skipped as invalid.
- One trade per instrument per day. Short signals are paper
  signals only; live shorting needs Chandu's explicit approval
  and MIS rules.
- V4 point thresholds are scaled by (prev close / reference
  price) so a Rs 259 stock and a Rs 4,239 stock use the same
  relative rules. For Nifty, the reference is its own prev close
  and room is 0.36% of price, as in the old Bank Nifty cash runs
  — do not copy Bank Nifty's 55,000 reference or its absolute
  point thresholds to Nifty or to stocks.
- V4 Setup 1 is skipped for every instrument here (no Red Bands
  supplied for stocks or for Nifty in this new work). Other
  setups run on PD/OR only.
- Nifty is an index: all Nifty numbers in this new work are
  cash-equivalent provisional numbers (100-share equivalent,
  labelled). They are NEVER mixed with any options baseline.
  Nifty options data was not attempted in this check (Upstox
  401 came before any search), so NO Nifty options baseline
  is claimed here — cash-equivalent only, once data is available.

## (b) NIFTY — Run 1 vs Run 2 + unified result
Status: NOT RUN. Blocked by the single Upstox 401 check above
and by the absence of local Nifty data. No Nifty trade, net, win
rate, or drawdown is claimed.

Planned, in order (do not run before stocks October, see section c):
- Nifty October 2026 FIRST: Run 1 (Day Trader skill own entries:
  OR breakout/breakdown 09:30–11:30, flag, oversold bounce, with
  the fixed provisional definitions from the old file) vs Run 2
  (V4 entries: Setups 2/3/4, bias gating, room 0.36%, Setup 2 to
  11:30, others to 14:30, same provisional exit/size/cost, so
  the comparison is ENTRY only), then the unified engine on
  the same October window.
- Then Nifty next periods, in the same order as stocks:
  Jan–Jun 2026 as tune, Jul–Sep 2026 as validation. October is
  the first/reporting period, NOT the tuning period. Jul–Oct
  is NOT used as validation in this new work.
- Report, when run, in the same table format as the old file:
  days, trades, targets, stops, square-offs, win %, net Rs
  (cash-equivalent, provisional), expectancy, max DD,
  trades/week, plus X assessment (all three measures together).

| Run | Period | Days | Trades | Win % | Net Rs | Max DD Rs | Trades/week | X assessment |
|---|---|---|---|---|---|---|---|---|
| Nifty Run 1 Skill own | Oct 2026 | 0 | 0 | — | — | — | — | NOT ASSESSABLE: not run, Upstox 401 2026-10-29 07:31 IST, no local data |
| Nifty Run 2 V4 | Oct 2026 | 0 | 0 | — | — | — | — | NOT ASSESSABLE: not run, same block |
| Nifty Unified | Oct 2026 | 0 | 0 | — | — | — | — | NOT ASSESSABLE: not run, same block |
| Nifty Run 1 / Run 2 / Unified | Jan–Jun 2026 (tune) | 0 | 0 | — | — | — | — | NOT RUN YET: after October, in order |
| Nifty Run 1 / Run 2 / Unified | Jul–Sep 2026 (validation) | 0 | 0 | — | — | — | — | NOT RUN YET: after tune, in order |

## (c) STOCKS — October FIRST, then next periods, in this exact order
Order is binding. Do NOT run stocks out of order, and do NOT run
Nifty October before stocks October.

1. STOCKS, October 2026, FIRST: Run 1 (skill own entries), then
   Run 2 (V4), then unified — per stock, cash intraday only,
   NOT options, same provisional rules as above.
2. STOCKS, Jan–Jun 2026, NEXT: tune period, same Run 1 / Run 2 /
   unified reporting.
3. STOCKS, Jul–Sep 2026, NEXT: validation period, same reporting.
   Jul–Sep is the validation window in this new order. Jul–Oct
   is NOT used.
4. Then Nifty, in the same period order (October, Jan–Jun,
   Jul–Sep), then unified validation / November forward paper,
   paper only.

### Stocks October 2026 — Run 1 vs Run 2 per stock
Status for every stock: NOT RUN, 0 days, 0 trades. Reason for
every stock is identical: Upstox HTTP 401 on the single check
2026-10-29 07:31 IST (plus earlier 07:22 / 07:25 IST), no local
stock data, no fabricated data, no substituted source.

| Stock | Days | Run 1 trades / win % / net Rs | Run 2 trades / win % / net Rs | Unified trades / win % / net Rs | Status |
|---|---|---|---|---|---|
| GODREJCP | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| GLENMARK | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| ITC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| RECLTD | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| TVSMOTOR | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| UNITDSPR | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| OBEROIRLTY | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| NTPC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| INDUSTOWER | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| KALYANKJIL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| HDFCBANK | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| NHPC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| PFC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| IRCTC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| WIPRO | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| NATIONALUM | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| VEDL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| HINDCOPPER | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| HINDZINC | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| HINDALCO | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| TATASTEEL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| ASTRAL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| BDL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| OIL | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |
| HINDUNILVR | 0 | — | — | — | NOT RUN: Upstox 401, 2026-10-29 07:31 IST |

### Stocks next periods — not run yet, in order
- Jan–Jun 2026 (tune): NOT RUN YET — only after stocks October.
- Jul–Sep 2026 (validation): NOT RUN YET — only after Jan–Jun.
- No stock result for any later period is claimed, and no
  October stock result may be inferred from Bank Nifty.

## (d) X assessment per run — this new work
| Run | Trades/week | Net Rs | Win % | X (all three together) |
|---|---|---|---|---|
| Nifty Run 1, Oct 2026 | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Nifty Run 2, Oct 2026 | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Nifty Unified, Oct 2026 | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Stocks Run 1, Oct 2026 (all 25) | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Stocks Run 2, Oct 2026 (all 25) | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Stocks Unified, Oct 2026 (all 25) | — (0 trades) | — | — | NOT ASSESSABLE — not run |
| Any Jan–Jun / Jul–Sep run | — | — | — | NOT RUN YET — after October, in order |

No run in this file passes or fails X on performance, because
no run in this file has any trades. The old Bank Nifty X
assessment is NOT carried here, because its Jul–Oct period
is excluded.

## Combined summary — what is true in this file
- Ran in this new work: NOTHING new. No Nifty trade, no stock
  trade, no combined Nifty + stocks result exists yet, and
  none is claimed.
- Removed: Bank Nifty Jul–Oct 2026 from forward analysis
  (details in section a). The old file is audit-only.
- Blocked solely by: Upstox 401 on the single check
  2026-10-29 07:31 IST, with no local Nifty/stock data to
  fall back on. No data was fabricated and no other source
  was substituted.
- Next steps, in exact order, after the parent executes the
  Upstox reconnect (user already said yes; do not ask again):
  1. Stocks October 2026: Run 1, then Run 2, then unified,
     per stock, cash intraday.
  2. Stocks Jan–Jun 2026: tune, same reporting.
  3. Stocks Jul–Sep 2026: validation, same reporting.
  4. Nifty October 2026: Run 1, then Run 2, then unified,
     cash-equivalent provisional only (no options baseline
     claimed unless options data is actually obtained).
  5. Nifty Jan–Jun 2026: tune, then Jul–Sep 2026: validation.
  6. Unified validation / November forward paper, paper only,
     with the portfolio cap (max 2–3 trades/week total).
- Engines ready (from old file, no other change except the
  equity/Nifty fetch routes noted above):
  V4 cash: ~/workspace/trading/daytrader_cash_backtest.py
  Skill Run 1: ~/workspace/trading/daytrader_skill_run.py
  Tuning: ~/workspace/trading/daytrader_cash_tuning.py
