# S12 candidate — consolidation of Family E combo F3 — documented 2026-10-30

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade cost, NOT premiums, NOT a lot profit.

S12 is NOT a new tuning idea. It is exactly combo **F3**, frozen before
scoring in `stocks_oct_familyE_combos_frozen.md` (Family E), consolidated
under one name so it can be run as a single engine and taken to November
paper if the user approves. Its scored results are the F3 results in
`stocks_oct_familyE_results.json`; the engine `stock_system_s12.py` must
reproduce them, and any mismatch voids the consolidation.

## Definition (exactly F3)

- Entry pool: Family B variant B8 — S8/S9 price design with prospective
  floor ₹250, room floor 1.25×, OR width 0.15–4.0%, second-close
  confirmation DROPPED (PE stop = signal-candle high, entry = open of
  candle after signal; CE pullback stop = pullback low, entry = open of
  candle after pullback candle), Nifty bias block on.
- Setup mix: PE legs only (Family C1 filter — setup3/setup2 PE; in
  practice all scored legs are setup3 bounce-rejection PE).
- Event gate: S9 G-TIERED unchanged, gate-filter before cap.
- Cap: gate-ranked, max 1 trade/day, max 1/stock/week (S9 ranking).
- Exit: Family A variant E4 — partial 50% at 1R, remaining 50% stop to
  breakeven, target 3R (instead of 2R), square-off 15:10, bar order
  stop → partial → target.
- Costs/size: 100 shares, ₹40/trade, provisional — NOT a lot profit.

## Status

Stage pass only, in-sample (Jan–Oct 2026). NOT adopted. Validation =
November 2026 paper, no re-tuning during November. Frequency, net and
win rate must be judged on November paper, separately from index work.
