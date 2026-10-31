# Day Trader skill run — October 2026 pilot (Bank Nifty)

Run: 2026-10-29, day-trader-india skill, paper only, no orders.
Scope: 18 trading days, 2026-09-30 to 2026-10-27, expiry 2026-10-27.
Data: Upstox 5-min spot + option candles in data/banknifty-2026-10/.
Engine: v4 pure with activation-candle +1 trail rule (trade_log_v4_pure_actplus1.csv).
Signal check re-run 2026-10-29 with live_setup_identifier.py reproduced all 6 signal days/times/setups.
Note: identifier prints ATM 54500 for Oct 27; v4 pure uses 54400 CE, ATM-or-100-ITM on expiry day, per the system rule.

## Scanner — patterns found
- 6 signals in 18 days, 12 no_trade days. Low frequency, about 1.7 signals/week in this window.
- Signals:
  - 2026-10-01 09:55 setup4 reclaim CE, entry spot 54,925.20
  - 2026-10-13 10:35 setup3 bounce rejection PE, entry spot 55,181.80
  - 2026-10-21 11:15 setup2 OR breakdown PE, entry spot 55,248.55
  - 2026-10-23 09:55 setup2 OR breakdown PE, entry spot 54,442.05
  - 2026-10-26 10:15 setup3 bounce rejection PE, entry spot 54,272.90
  - 2026-10-27 09:35 setup1 breakout retest CE, entry spot 54,523.10
- Pattern note: 5 of 6 signals were PE except Oct 01 CE; winning days were neutral/bearish bias, the only bullish-bias signal (Oct 27) was the loss. OR widths on signal days: 181–580 points. This is an observation on 6 trades, not a filter to adopt.

## News / analyst
- Not re-scored for October in this run. No October news flag is claimed here. For forward days, check Bank Nifty heavyweight results/announcements before the open.

## Entry
- v4 only, no new setups invented. Entry at next 5-min open after signal close, one-and-done per day.

## Exit / timemachine
- Stop -50 option points, target +90, activation-candle +1 trail, square-off before 15:15, assumed costs Rs 220/trade.
- Result: 6 trades, 5 targets, 1 trail, 0 stops.
- Gross +Rs 13,500, costs 6 x Rs 220 = Rs 1,320, net +Rs 12,180.
- Expectancy +Rs 2,030 per trade, max drawdown Rs 220 in this window.
- Per trade net: Oct 01 +2,480; Oct 13 +2,480; Oct 21 +2,480; Oct 23 +2,480; Oct 26 +2,480; Oct 27 -220.

## Budget / risk
- 1 lot of 30 only. Max gross loss at stop Rs 1,500 per trade, plus costs.
- Target win net Rs 2,480 per trade after assumed costs.
- Trading capital not shared, so risk % cannot be computed. Do not invent a capital figure.
- Daily loss limit / monthly breaker not locked as Chandu's rule yet.

## Broker
- Paper only. No order placed, no Upstox order placement verified. No trade goes through without Chandu's yes for that exact trade.

## Limit — read before reusing
- 18 days / 6 trades only. This October result does NOT prove the system works.
- July–September v4 (same engine, no bands) was 15 trades / 0 wins / -Rs 22,800, and Jan–Oct v4 target 50 was -Rs 1,740 on 42 trades. October was the outlier.
- Reuse this run as the October baseline for the day-trader workflow; do not carry its net forward as an expected return.
