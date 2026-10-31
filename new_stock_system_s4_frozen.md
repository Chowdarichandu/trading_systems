# S4 — Intraday STOCK system (cash, NOT options) — FROZEN for scoring, NOT adopted

**Status: FROZEN 2026-10-29, NOT adopted, NOT a live system. Paper only, no orders.**
- S4 is the second iteration after S2 and S3 both failed the satisfaction bar.
- Exactly ONE change from S3, everything else identical to S3.

## The one S4 change
- **Nifty confirmation relaxed:** bias-only rule from S2/S3, EXCEPT an opposed-direction
  trade is now allowed when the stock's room ratio is ≥ 2.0 × risk.
  I.e. CE on a bearish Nifty day or PE on a bullish Nifty day passes ONLY if room ≥ 2 × risk;
  otherwise the bias-only block stands. Non-opposed trades follow S3 unchanged.
- Room stays finite AND ≥ 1.25 × risk (S3). Target stays entry ± 2 × risk.
- Cap ranking stays target-net DESC, then room ratio, then setup rank.
- All other rules unchanged: setups 2/3/4 only, second-close confirmation, structural stop
  (OR low −0.1% / OR high +0.1% of prev close), give-back partial 50 at 1 × risk with rest
  trailed to breakeven, no re-entry, cap 3/week, 1/stock/week, prospective target ≥ ₹500,
  100 shares, ₹40/trade, 15:10 square-off, cash intraday only.

## Engine
`stock_system_continued.py` with `room_min=1.25`, `nifty_mode='bias_relaxed_room2'`, `cap_rank='target'`.
Trade CSV: `s4_trades_jan_oct_2026.csv`, uncapped `s4_uncapped_jan_oct_2026.csv`.
Jan–Oct 2026 run is in-sample context only; S4 is NOT adopted on it.
