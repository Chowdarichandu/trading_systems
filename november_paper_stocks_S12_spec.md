# November 2026 Paper — STOCKS channel — CANDIDATE: S12 — PREPARED, NOT ACTIVATED (2026-10-30)

**Paper only. No live orders. Cash intraday stocks only, never pooled with index options. Real money = ₹0.**
**Every figure provisional per 100 shares, ₹40/trade cost — NOT option premiums, NOT a futures/options lot profit.**

## Status — read first

This spec and its log were **prepared in advance on 2026-10-30 so a weekend approval loses no trading days**. S12 is **NOT activated**: no logging runs, no cron covers stocks paper, and nothing is scored until Chandu approves S12 for November paper **in the Stocks chat**. If he does not approve, this file stays unused and S12 stays a stage pass only.

Source definition: `new_stock_system_s12_frozen.md` (consolidation of Family E combo F3, frozen before scoring). Results and verdict: `stocks_october_highly_optimized.md`. Take the definition from those files; do not re-derive or re-tune it.

## S12 definition (exactly as frozen)

- Entry pool B8: prospective floor ₹250, room floor 1.25×, OR width 0.15–4.0%, second-close confirmation dropped (entry = open of candle after signal; PE stop = signal-candle high), Nifty bias block ON.
- PE legs only (in practice all scored legs are setup3 bounce-rejection PE).
- S9 G-TIERED event gate unchanged, gate-filter before cap.
- Cap: max 1 trade/day, max 1/stock/week, gate-ranked.
- Exit E4: partial 50% at 1R, rest to breakeven, target 3R, square-off 15:10, bar order stop → partial → target.
- Costs/size: 100 shares, ₹40/trade, provisional.

## Reference results (in-sample, from stocks_october_highly_optimized.md)

- October 2026: 8 trades, 62.5% win, 50.0% full targets, **+₹1,885 provisional per 100 shares**, 2.22/week, October max drawdown −₹1,395 provisional per 100 shares.
- Jan–Sep 2026 check (same frozen rules): 93 trades, 55.9% win, **+₹3,607.50 provisional per 100 shares**, max drawdown −₹9,007.50 provisional per 100 shares.
- Honest limits, carried into November judging: frequency is still well below Chandu's 1 valuable trade/day standard; the Jan–Sep drawdown is deep; the no-event leg lost over Jan–Oct and the post-reaction tier carried the total. **Stage pass only — NOT adopted.**

## November judging (if approved)

- Judged on November's own net + win rate + frequency together, provisional per 100 shares, in the Stocks chat only — never combined with Bank or Nifty paper.
- No re-tuning during November. A version is adopted only on validation progress, not on October in-sample results.
- Events checked first, per the standing rule: watchlist `stock_event_watchlist_nov2026.md` — ITC + NATIONALUM results Mon 2 Nov, NHPC 4 Nov, GLENMARK 5 Nov, HINDALCO 6 Nov, TATASTEEL Sat 7 Nov (reaction Mon 9 Nov), OIL 12 Nov; NTPC's Sat 31 Oct results put Mon 2 Nov inside its reaction window.
- Log: `november_paper_stocks_S12_log.csv`, one row per trade, filled after 15:10 on the trade day.

## What activation still needs (Chandu's decision, then one step)

1. Chandu approves S12 for November paper in the Stocks chat (or says keep tuning instead — his standing instruction there was "until I am satisfied you need to tune", and he has not yet said he is satisfied with S12).
2. On approval only: set up daily after-15:10 logging for this log, Mon–Fri, November only, reporting only in the Stocks chat.
