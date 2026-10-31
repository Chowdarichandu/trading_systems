# Clubbed plan — Day Trader skill + 3-Blue-Line strategy, level by level

Agreed 2026-10-29 morning by Chandu. Paper only, no orders without his yes for that exact trade.

## Stages
- Stage 1: Bank Nifty — DONE for October. Run saved at daytrader_october_run.md: 18 days, 6 trades, +Rs 12,180 net (v4 pure, target 90, stop 50, 1 lot).
- Stage 2: Stocks he sends — CASH intraday only, NOT options. One result per stock, same clubbed workflow.
- Stage 2 list as sent 2026-10-29 via TradingView watchlist screenshots (to be confirmed as final):
  GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER,
  KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC,
  HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR
  (25 names; first screenshot price for Godrej Consumer was cut off, name only.)

## Level-by-level match — skill step = strategy rule
- Scanner = Blue Lines + structural levels, per instrument:
  Bank Nifty: PDH/PDC/PDL + Red Band + ledges.
  Stocks (cash): PDH/PDC/PDL for that stock + its own Red Band/ledges. Room filter must be scaled to the stock price — 200 index points does NOT apply to a Rs 259 stock. Scaling rule to be confirmed, not assumed.
- News / Analyst = results, announcements, corporate actions for that stock; flat before a results announcement it is exposed to, unless Chandu accepts the risk. Result-trap test applies for stocks.
- Entry = v4 setups only, no new setups without backtest:
  Setup 1 breakout + retest hold, Setup 2 opening-range breakout/breakdown, Setup 3 bounce rejection, Setup 4 reclaim/pullback.
  Timing: 09:15–09:30 opening range, first signal from 09:30 5-min close, entry at next 5-min open, one-and-done per instrument per day.
- Exit = set before entry, square-off before 15:15.
  Bank Nifty options (Stage 1): stop -50 premium points, target +90, activation-candle +1 trail after 100 index points in favour.
  Stocks cash (Stage 2): stop/target in share-price terms, NOT premium points. Values to be confirmed by Chandu — do not copy -50/+90 as rupees per share.
- Timemachine = backtest engine replay, per instrument, with sample size stated: trades, win rate, expectancy, profit factor, max drawdown after costs. October is the Stage 1 baseline; Stage 2 period to be confirmed (assumed October unless Chandu says otherwise).
- Budget = INR sizing per instrument.
  Bank Nifty options: 1 lot of 30.
  Stocks cash: quantity by capital and per-trade risk, NOT a lot. Capital and per-trade risk % not yet shared, so quantity cannot be computed yet.
- Risk = PASS/BLOCK: 1 trade per instrument per day, stop/target set, square-off before 15:15, daily/monthly breaker to be confirmed. No margin/leverage/shorting unless explicitly turned on.
- Broker = paper only. Upstox order placement not verified. No trade without Chandu's yes for that exact trade.
- Alerts = stop hit, target hit, flat by 15:15, on 5-min closes (no live websocket in Muse).
- Pelosi replacement = promoter trades, bulk/block deals, FII/DII flows, NSE/BSE insider disclosures, where relevant to a stock.

## Versioning + progression rule 2026-10-29 08:10 IST — user, pro
- Use Day Trader skill + V4, check results; if tuning is needed, make V5, then Day Trader skill v1, v2, etc., in an iterative loop. Assistant has freedom to choose tuning/versioning methods within paper-only, proprietary, workspace-only work.
- A new version is adopted ONLY if it progresses on validation (unseen period) — net, win rate, and frequency together per X — never on in-sample alone.
- A decreasing result is NOT adopted: keep the previous best version, log the failure, fix, and try again.
- When Chandu asks a question, just report status/numbers plainly, no blocking lectures.
- Results Intelligence layer (same day): last 4 quarterly results per stock, pre-week (T-5 to T-1) accumulation, during (after-market announcement → next open gap), post-week (T+1 to T+5); continuous loop identifying → learning → fixing, not a 15:30-only job.

## X defined 2026-10-29 07:25 IST — target to solve for
X = combined, not any one number alone:
- 2–3 quality trades per week (portfolio total, not hundreds, not per stock multiplied out)
- Good net profit
- Good win rate
All three together. A version that hits net by taking many trades, or win rate by taking tiny wins, does NOT count as X.

## Sequence 2026-10-29 07:25 IST — user clarified
1. First run: Day Trader skill entries alone (skill's own scanner/entry/exit patterns).
2. Next run: V4 with stocks (cash intraday).
3. Then compare, tune the Day Trader skill, and/or merge the two into ONE unified engine.
That unified engine is proprietary to Chandu — do not publish or share it externally.

## Correction 2026-10-29 07:19 IST — user clarified, superseding the block above
- This is a HISTORICAL BACKTEST, not a live/day-ahead parameter request.
- Start using the Day Trader skill for stocks AND Bank Nifty TOGETHER.
- Chandu did NOT say he will give cash stop/target or other new parameters. Do NOT block Stage 2 on user-supplied parameters.
- Use the skill's own documented rules, and state any cash translation clearly as a provisional, labelled assumption — never as Chandu's rule.
- Bank Nifty October run is Stage 1 baseline; Stage 2 stocks are run in the same historical backtest, not after a separate parameter approval.

## Open items (do not block the historical run)
1. Confirm the 25-name screenshot list is the final Stage 2 list, or if more names are coming.
2. Red Bands/ledges per stock: if not available, Setup 1 is skipped and other setups run on PD/OR only, as in v4 — do not wait for user bands to start the signal replay.
