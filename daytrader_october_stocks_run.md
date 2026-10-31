# Clubbed Day Trader + v4 historical backtest — October 2026, Bank Nifty + stocks

PROPRIETARY WORKING FILE for Chandu only. Keep in this workspace only.
Do not publish, share, or describe the unified engine below as a public system.

Paper / historical replay only. No orders placed. No live trading claimed.

## X — the target, as defined by Chandu (all three together)
- 2–3 quality trades per week, PORTFOLIO total (not per stock, not hundreds).
- Good net profit.
- Good win rate.
A version that hits net by taking many trades, or win rate by taking tiny
wins, does NOT count as X. X is assessed on out-of-sample data, never on
the period a variant was tuned on.

## What could and could not run, and why
- Bank Nifty: RAN, on locally held Upstox spot 5-min data Jan–Oct 2026.
- All 25 stocks: NOT RUN. Upstox returned HTTP 401 Unauthorized on
  2026-10-29 at 07:22 IST and again at 07:25 IST, on both the equity search
  and the previously verified index search. The stored Upstox token
  (connected 2026-10-28) appears expired — Upstox tokens are daily.
  No candles were fabricated, no alternative source was substituted, and
  no stock result is claimed. Reconnect Upstox (parent agent) and re-run
  the ready engines below; no other change is needed.
- Bank Nifty "cash" numbers in this file are index points x 100 shares
  (provisional size) for comparison with stocks. The Bank Nifty index
  itself is not cash-traded; the tradeable Bank Nifty baseline remains
  the OPTIONS run below. Do not mix the two nets.

## Provisional rules used for every cash run (NOT Chandu's rules)
- Size: 100 shares per trade, every instrument, solely to convert price
  points to rupees. Not capital-based; capital was not shared, so no
  risk % is computed.
- Cost: Rs 40 flat per trade, assumed, not actual brokerage.
- Exit: signal candle low (long) / high (short) as stop, target =
  2x stop distance (baseline), square-off at 15:10, stop priority if
  both stop and target are hit in one candle. If entry == stop level,
  the trade is skipped as invalid.
- One trade per instrument per day. Short signals are paper signals
  only; live shorting needs Chandu's explicit approval and MIS rules.
- V4 point thresholds are scaled by (prev close / 55,000) so a Rs 259
  stock and a Rs 4,239 stock use the same relative rules. Bank Nifty
  scale is ~1.0, so its cash numbers are directly comparable to v4.
- V4 Setup 1 is skipped for every instrument here (no Red Bands
  supplied for stocks, and no bands file was passed for this cash run).
  Other setups run on PD/OR only.

## Stage 1 baseline — Bank Nifty OPTIONS (reuse, not redone)
From daytrader_october_run.md, v4 pure, target +90, stop -50 premium
points, 1 lot of 30, activation-candle +1 trail:
18 days (30 Sep–27 Oct), 6 trades, 5 targets, 1 trail, 0 stops,
net +Rs 12,180 after Rs 220/trade assumed costs, expectancy +Rs 2,030.
This is an 18-day, 6-trade pilot only — not proof of edge.

## Run 1 — Day Trader skill's OWN entries, Bank Nifty cash, October 2026
Skill patterns, fixed provisional definitions (skill doc gives no
numeric thresholds for flag / oversold, so these are documented
translations, not the skill's literal text):
- OR breakout/breakdown: first 5-min close beyond ORH/ORL, 09:30–11:30.
- Flag: 3 consecutive candles each <=0.30% range and total <=0.50%,
  then a close beyond flag high/low, up to 14:30.
- Oversold bounce: RSI(14, Wilder) on 5-min closes <30 at the prior
  candle, current candle closes above the prior candle's high, to 14:30.
- Earliest pattern per day wins; one trade per day.

October 2026 (17 days, 1–27 Oct): 17 trades, 8 targets, 9 stops,
0 square-offs, win rate 47.1% (targets/trades), net +Rs 89,085
(100-share provisional, Rs 40/trade), expectancy +Rs 5,240,
max drawdown Rs 20,900, trades/week 5.0.
By pattern, October first-signals: OR breakout 9, OR breakdown 6,
flag breakdown 2, oversold bounce 0. Oversold never fired first in
October or in Jan-Jun (see ablation below) — it added no trades.

Run 1 October trades (Bank Nifty cash, provisional):
- 01 Oct OR breakout CE target +16,640; 05 Oct OR breakdown PE target +25,690;
  06 Oct OR breakout CE stop -1,435; 07 Oct OR breakdown PE stop -7,475;
  08 Oct OR breakdown PE stop -11,070; 09 Oct OR breakout CE target +27,270;
  12 Oct OR breakdown PE stop -4,640; 13 Oct OR breakout CE target +10,170;
  14 Oct OR breakout CE stop -16,660; 15 Oct OR breakout CE target +17,370;
  16 Oct OR breakdown PE stop -6,725; 19 Oct flag breakdown PE stop -6,650;
  21 Oct OR breakout CE stop -7,525; 22 Oct OR breakout CE target +29,760;
  23 Oct OR breakdown PE target +14,860; 26 Oct flag breakdown PE target +16,740;
  27 Oct OR breakout CE stop -7,235.

## Run 2 — V4 entries, Bank Nifty cash, October 2026 (same window, same exit)
V4 setups 2/3/4 only (Setup 1 skipped, no bands), bias gating on,
room 0.36% of price, Setup 2 to 11:30, others to 14:30, same
provisional exit/size/cost as Run 1, so the comparison is ENTRY only.

October 2026 (17 days): 5 trades, 4 targets, 1 stop, 0 square-offs,
win rate 80.0%, net +Rs 67,690, expectancy +Rs 13,538,
max drawdown Rs 3,730, trades/week 1.47.
Trades: 01 Oct setup4 reclaim CE target +16,640; 13 Oct setup3 PE
stop -3,730; 21 Oct setup2 breakdown PE target +20,200;
23 Oct setup2 breakdown PE target +24,060; 26 Oct setup3 PE
target +10,520. (Oct 07 and Oct 14 reclaim signals in an earlier
uncorrected run were removed by fixing a room-check precedence bug
in the tuning script; the numbers here are the corrected ones and
match the standalone cash engine's 5 October trades.)

## Run 1 vs Run 2 comparison — Bank Nifty cash, October 2026
| Instrument | Run | Days | Trades | Targets | Stops | Win % | Net Rs* | Expectancy Rs | Max DD Rs | Trades/week |
|---|---|---|---|---|---|---|---|---|---|---|
| Bank Nifty cash | 1 Skill own | 17 | 17 | 8 | 9 | 47.1 | +89,085 | +5,240 | 20,900 | 5.0 |
| Bank Nifty cash | 2 V4 | 17 | 5 | 4 | 1 | 80.0 | +67,690 | +13,538 | 3,730 | 1.47 |
| Bank Nifty options | V4 baseline (Stage 1) | 18 | 6 | 5 | 1 trail | 83.3 targets | +12,180 | +2,030 | 220 | ~1.7 |

*Cash nets are 100-share provisional, Rs 40/trade. Options net is
1 lot, Rs 220/trade. The two nets are NOT comparable in rupees;
compare win rate, frequency, and drawdown, not the net column.

October reading, and its limit: Run 1 made more rupees in October
by trading every day, but at 5.0 trades/week it already breaks X's
frequency on Bank Nifty alone, before any stock is added, and with
a much larger drawdown. Run 2 hit X's frequency (1.47/week) and win
rate (80%) in October, but October alone is 5 trades — it is
context, never proof, and the longer periods below overturn it.

## Run 1 vs Run 2 — longer periods (Bank Nifty cash, same rules)
| Run | Period | Days | Trades | Win % | Net Rs | Expectancy Rs | Max DD Rs | Trades/week |
|---|---|---|---|---|---|---|---|---|
| 1 Skill own | Jan-Jun (tune) | 110 | 110 | 22.7 | -187,025 | -1,700 | 215,960 | 5.0 |
| 1 Skill own | Jul-Oct (validate) | 75 | 75 | 32.0 | +17,200 | +229 | 149,295 | 5.0 |
| 1 Skill own | Jan-Oct | 185 | 185 | 26.5 | -169,825 | -918 | 339,025 | 5.0 |
| 2 V4 cash | Jan-Jun (tune) | 110 | 22 | 31.8 | -25,505 | -1,159 | 68,655 | 1.0 |
| 2 V4 cash | Jul-Oct (validate) | 75 | 19 | 31.6 | +5,550 | +292 | 77,820 | 1.27 |
| 2 V4 cash | Jan-Oct | 185 | 41 | 31.7 | -19,955 | -487 | 130,795 | 1.11 |

Neither run is profitable over Jan-Oct in cash terms, and neither
hits X over a full period: Run 1 fails frequency and win rate;
Run 2 hits frequency but fails net and win rate over Jan-Oct.

## Tuning note — what moves Y toward X, and what does not survive
Tune period Jan-Jun 2026, validate period Jul-Oct 2026, October
never used to pick a candidate. Full grids are in
daytrader_cash_tuning_grid_janjun.csv (v4) and
daytrader_skill_tuning_grid_janjun.csv (skill).

### V4 tuning (target ratio x stop scale x room)
- Strongest single effect: stop scale. At every target ratio and
  room, stop_scale 0.5 (tight stop) beat 1.0, which beat 1.5 by a
  wide margin in Jan-Jun. Example at ratio 2, room 0.36%:
  0.5x net +41,715 (22 trades, win 40.9%), 1.0x net -25,505
  (22 trades, win 31.8%), 1.5x net -107,888 (22 trades, win 27.3%).
- Target ratio: higher ratio raised Jan-Jun net only when the stop
  was tight. At stop 0.5x, room 0%: ratio 1 net +18,838 (win 48.3%),
  ratio 2 net +48,470 (win 37.9%), ratio 3 net +81,238 (win 34.5%).
  At stop 1.0x, raising the ratio lowered win rate without
  rescuing net (ratio 3, stop 1.0x, room 0.36%: net -40,745, win 22.7%).
- Room: raising room from 0% to 0.72% cut trades (29 -> 21 in the
  grid) and usually raised win rate by 2–9 points, but did not
  reliably raise net. It is a frequency/quality filter, not a
  profit source on its own.
- Bias and signal window (Jan-Jun sensitivity, baseline = -25,505):
  bias OFF -33,965 (32 trades, win 28.1%); signal end 11:30 for all
  -25,505 (identical to baseline, because v4's late signals are
  already Setup 2-limited in this data); signal end 14:30 for all
  +16,055 (32 trades, win 31.2%). All three sensitivities FLIPPED
  on Jul-Oct validation: bias OFF +11,510, signal 14:30 -14,330,
  baseline +5,550. None is a reliable lever.
- Pre-stated v4 candidate (highest Jan-Jun net, trades >= 15):
  ratio 3, stop 0.5x, room 0%. Jan-Jun: 29 trades, win 34.5%,
  net +81,238, DD 26,418, 1.32/week. Jul-Oct validation: 24 trades,
  win 25.0%, net -11,513, DD 62,465, 1.60/week. Jan-Oct: 53 trades,
  win 30.2%, net +69,725, DD 68,060.
  VERDICT: candidate FAILS validation on net (negative in
  Jul-Oct, worse than baseline's +5,550) even though drawdown
  improved. Do NOT adopt it. The Jan-Jun gain was in-sample.

### Skill tuning (target ratio x stop scale, all patterns)
- Pattern ablation, Jan-Jun: OR only 95 trades, net -143,230,
  win 22.1%; OR+flag 110 trades, net -187,025, win 22.7%;
  OR+oversold 101 trades, net -187,940, win 20.8%; all patterns
  110 trades, net -187,025. Flag ADDS trades and LOSES money
  in Jan-Jun. Oversold adds trades and loses money, and never
  fired first when OR/flag were also active.
- Grid: the only Jan-Jun positive cells are at stop 1.5x, ratio 2
  (+68,300, win 29.1%) and ratio 3 (+157,793, win 18.2%).
  Pre-stated skill candidate (highest Jan-Jun net, trades >= 20):
  ratio 3, stop 1.5x. Jan-Jun: 110 trades, win 18.2%,
  net +157,793, DD 123,500, 5.0/week. Jul-Oct validation:
  75 trades, win 14.7%, net +12,280, DD 155,183, 5.0/week.
  Oct context: 17 trades, win 11.8%, net -18,690.
  VERDICT: candidate FAILS X on every count except a barely
  positive validation net: win rate collapsed (18.2% -> 14.7%),
  drawdown is the largest in the file, frequency is 5.0/week,
  and October is negative. This is the exact trap X forbids:
  net from a few very large wins at a low win rate, not a
  quality system. Do NOT adopt it.
- What moves skill Y toward X: nothing in the grid moves all
  three X measures together. Tightening the stop (0.5x) raises
  win rate (to 40–48% at ratio 1) but keeps Jan-Jun net
  negative (-102,683 to -143,355). Raising the ratio raises
  net only by cutting win rate to ~18%. The lever that moves
  frequency toward X is NOT in the exit at all — it is the
  v4 entry filters (bias, PD cross, room), which cut skill's
  5.0/week to v4's ~1.1/week.

## Unified engine proposal (PROPRIETARY — workspace only)
Survives from each run, for validation on fresh data (NOT adopted yet):
- FROM SKILL: the scanner discipline — list OR, flag, and oversold
  candidates every morning, and the exit-planner discipline
  (stop/target set before entry, square-off before 15:15).
  The skill's UNFILTERED entry does NOT survive: it trades
  every day, breaks X frequency, and loses over Jan-Oct.
- FROM V4: the entry filters that create quality over quantity —
  bias gating, PD-level cross for Setup 2, room to the next PD
  level, Setup 3 bounce rejection, Setup 4 reclaim/pullback,
  one trade per instrument per day. These are what cut
  5.0/week to ~1.1/week and raised win rate from ~27% to ~32%
  over Jan-Oct (and to 80% in October alone, on 5 trades).
- DROPPED as entries: flag breakout (adds losing trades in
  Jan-Jun) and oversold bounce as a first signal (never fired
  first; keep it as context only, not an entry, unless a
  different definition is supplied and backtested).
- EXIT for the unified engine (provisional, to be validated):
  keep the baseline 2x ratio / 1x signal-candle stop, NOT the
  tuned 3x / 0.5x or 3x / 1.5x exits. Both tuned exits won
  Jan-Jun and failed or weakened on Jul-Oct validation.
  Any exit change must be validated on Nov forward paper
  before adoption.
- FREQUENCY toward X: Bank Nifty v4 alone runs ~1.0–1.6/week,
  leaving room for roughly 1–2 stock trades/week to reach a
  portfolio 2–3/week. Stock trades must use the same filters;
  unfiltered skill signals on 25 stocks would be ~25 trades/
  week at 1/day each and would destroy X on frequency alone.
  A portfolio cap (max 2–3 trades/week total, best setups
  first) is therefore part of the unified engine, to be
  validated, not an afterthought.

Still needs validation before any live use (in order):
1. Upstox reconnect, then Run 1 and Run 2 for all 25 stocks in
   October, with the same tables as Bank Nifty above.
2. The unified engine (v4 filters + skill scanner/exit
   discipline + baseline exit) on stocks, October, then on
   Nov forward paper — paper only, 1 trade/instrument/day.
3. Regime filters R1–R3 (atlas_regime_filter_addendum.md) on
   2024–2025, which may explain why Jan-Jun and Jul-Oct
   flip sign for the same variables.
4. Cash shorting, quantity/capital, and actual brokerage —
   all still unconfirmed; no live order until Chandu approves
   the exact trade and these are locked.

## Per-stock results — October 2026, cash intraday
Window: same as Stage 1 (trading days 30 Sep–27 Oct 2026 where
data allows; see Bank Nifty rows). Exit/size/cost as in
"Provisional rules" above. All stock rows are NOT RUN for the
reason stated; they are listed so the gap is explicit, not hidden.

| Stock | Days checked | Signals by setup | Trades | Targets | Stops | Square-offs | Win % | Net Rs | Expectancy Rs | Max DD Rs | Trades/week | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Bank Nifty (cash proxy, Run 2 V4) | 17 | S4:1, S3:2, S2:2 | 5 | 4 | 1 | 0 | 80.0 | +67,690 | +13,538 | 3,730 | 1.47 | Ran (cash proxy) |
| Bank Nifty (cash proxy, Run 1 Skill) | 17 | OR:15, Flag:2, Oversold:0 | 17 | 8 | 9 | 0 | 47.1 | +89,085 | +5,240 | 20,900 | 5.0 | Ran (cash proxy) |
| Bank Nifty (options, Stage 1 baseline) | 18 | S4:1, S3:2, S2:2, S1:1 | 6 | 5 | 0 (+1 trail) | 0 | 83.3* | +12,180 | +2,030 | 220 | ~1.7 | Ran (options, reused) |
| GODREJCP | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| GLENMARK | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| ITC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| RECLTD | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| TVSMOTOR | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| UNITDSPR | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| OBEROIRLTY | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| NTPC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| INDUSTOWER | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| KALYANKJIL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| HDFCBANK | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| NHPC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| PFC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| IRCTC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| WIPRO | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| NATIONALUM | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| VEDL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| HINDCOPPER | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| HINDZINC | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| HINDALCO | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| TATASTEEL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| ASTRAL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| BDL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| OIL | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |
| HINDUNILVR | 0 | — | 0 | 0 | 0 | 0 | — | — | — | — | — | NOT RUN: Upstox 401, 29 Oct 07:22 & 07:25 IST |

*Options win % = targets / trades (5/6); the 6th trade was a trail to cost.

## Combined summary
- Ran: Bank Nifty only. Run 1 (skill) October: 17 trades, 47.1% win, +Rs 89,085 provisional cash, 5.0/week.
  Run 2 (v4) October: 5 trades, 80.0% win, +Rs 67,690 provisional cash, 1.47/week.
  Combined Bank Nifty cash October (Run 1 + Run 2) is NOT a portfolio
  result — the two runs trade the same days and would double-count;
  do not add them.
- Not ran: all 25 stocks, for the Upstox 401 reason above. No
  combined Bank Nifty + stocks result exists yet, and none is claimed.
- October is a small sample (17 days, 5–17 trades) and is NOT proof
  of edge. Over Jan-Oct, both runs lose in cash terms (Run 1
  -Rs 169,825 on 185 trades; Run 2 -Rs 19,955 on 41 trades), and
  every tuned candidate failed or weakened on Jul-Oct validation.
- Next step, in order: (1) Upstox reconnect, (2) Run 1 + Run 2 for
  the 25 stocks in October with this same reporting, (3) unified
  engine on stocks + Nov forward paper, paper only.

## Engines (ready to re-run after reconnect)
- V4 cash: ~/workspace/trading/daytrader_cash_backtest.py
  (single stock: --symbol, --spot5m, --daily, --out; qty 100, cost Rs 40 provisional)
- Tuning (v4): ~/workspace/trading/daytrader_cash_tuning.py
  (Bank Nifty Jan-Oct spot; grid + sensitivity CSVs in ~/workspace/trading/)
- Skill Run 1: ~/workspace/trading/daytrader_skill_run.py
  (OR / flag / oversold definitions as above; grid CSV in ~/workspace/trading/)
- Upstox fetch (read-only): ~/workspace/trading/fetch_upstox_via_connector.py
  (Bank Nifty index/options route; equity instrument search + historical
  candle must be added for stocks after reconnect — the equity endpoint
  was never reached because search itself returned 401)
