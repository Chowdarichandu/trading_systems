# V6 November 2026 Paper Spec — PREPARED, NOT RUN

Status: PREPARED 2026-10-29. November 2026 has NOT happened yet.
No November data exists in this spec, no November result is claimed,
and no November trade is to be invented from October data.
Run this spec forward, day by day, only as November trading days
actually arrive. Paper only, no orders, no live trading.

## Candidate to paper (exactly one, frozen)

V6-B: pooled, Nifty first, conviction-only, prospective target
≥ ₹1,000, NO stop floor in the real P&L.
- Pool: V4 index + Skill index candidates, NIFTY and BANKNIFTY only,
  NO stocks, deduped by symbol+date keeping higher conviction
  (setup4=3 > setup3=2 > setup2=1 > skill OR=0, then higher
  prospective net target).
- Filter: setup_rank ≥ 2 only (setup4 reclaim/pullback, setup3
  bounce rejection). setup2 and skill OR are dropped.
- Ranking (signal-time only, never realised outcome): setup_rank,
  then Nifty before Bank Nifty, then bias-strong, then room ratio,
  then prospective net target.
- Filter: original prospective net target ≥ ₹1,000 (net of ₹40 cost).
  (₹1,500 gave identical picks Jan–Oct, so ₹1,000 is the frozen
  threshold; do not re-pick it mid-November.)
- Cap: max 3 index trades/ISO week, max 1 trade/symbol/week.
  With 2 symbols the practical max is 2/week — report actual.
- Cash rules (provisional, NOT Chandu's live options rules):
  100 shares equivalent (index points × 100), ₹40/trade, signal-
  candle stop, 2× target, square-off 15:10, short paper-only.
- Data route: Upstox 5-min candles. For a day in progress, use the
  INTRADAY endpoint (`upstox.py intraday`), NOT the historical
  endpoint — historical returns empty for today while the market
  is open (fixed 2026-10-29). For completed days, historical is fine.
  No signal is claimed until its 5-min signal candle has CLOSED.

## Shadow logs (record, do NOT count as real P&L)

- Stop-floor shadow: for each V6-B trade, also record what its net
  would be floored at −₹5,040. This is an upper-bound sensitivity
  only (see `v6_aggressive_history.md` for why a true 50-point
  stop needs its own bar-by-bar re-run).
- V5 control: run V5 index (pool, ₹500 filter, setup2/OR included)
  in parallel, same days, same caps, paper only, for comparison.
  Do NOT merge V5 and V6-B trades.

## Daily log format (one row per V6-B trade, plus a no-trade row)

```
date, symbol, setup, direction, signal_time, entry, stop, target,
exit_reason, exit_price, exit_time, net_rs, net_rs_floored_shadow,
week, cap_blocked (yes/no, with reason if a candidate ranked out)
```

Plus a daily header: day's PDH/PDC/PDL, bias, OR high/low, and
whether any candidate was dropped by the conviction filter or the
₹1,000 filter (count only, not outcome-based re-picking).

## Weekly and monthly summary (same columns as history)

Per week and for November as a whole, for V6-B and for the V5
control separately, split Bank Nifty vs Nifty:
trades, targets, win %, net, expectancy/trade, trades/week,
largest win, largest loss, number of trades below −₹5,040.

## Pre-registered pass rule (frozen before November, do not move it)

V6-B is adopted ONLY if ALL of these hold on November paper:
1. Net > ₹0 for November as a whole.
2. Win rate ≥ 40% (targets ÷ trades).
3. At least 5 V6-B trades in November — fewer than 5 is
   INCONCLUSIVE, not a pass, however good the net looks.
   (History warns this is likely: V6-B traded 15 times in 10
   months, and 0 times in March and September 2026.)
4. V6-B beats the V5 control on net AND on win rate for November,
   at no more trades than the control.
5. No single trade accounts for more than 50% of November's net
   (otherwise the month is March-like: one-trade dependent).

If any leg fails, or if November has < 5 V6-B trades: DO NOT ADOPT.
Keep V4 index as the previous best, paper only, log why V6-B
failed, and do not re-tune on November and re-claim it as a pass.

## What to do when November starts

1. Each trading day, after 15:10 square-off, compute that day's
   V4 and Skill index candidates from Upstox intraday/historical
   5-min candles, dedup, filter, rank, and cap exactly as above.
2. Append the day's rows to
   `data/progressive/v6_index_summary_2026-11.json` (new file,
   do not overwrite October).
3. At month end, write `v6_november_paper.md` with the weekly and
   monthly tables above and the pass/fail verdict against this
   spec, then report it to Chandu plainly.
4. Until then, say only: "November paper spec prepared, not run."
