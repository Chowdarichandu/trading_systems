# S5 — Intraday STOCK system (cash, NOT options) — FROZEN for scoring, NOT adopted

**Status: FROZEN 2026-10-29, NOT adopted, NOT a live system. Paper only, no orders.**
- S5 is the third and final iteration in this continuation round (S3, S4, S5),
  after S2, S3 and S4 all failed the satisfaction bar.
- Exactly ONE change from S4, everything else identical to S4.

## The one S5 change
- **Cap ranking: room ratio DESC first, then prospective target net, then setup rank**
  (was target-net DESC, then room ratio, then setup rank in S1–S4).
  Cap itself unchanged: max 3 stock trades/week, max 1/stock/week, prospective target ≥ ₹500.
- Room stays finite AND ≥ 1.25 × risk (S3/S4). Nifty confirmation stays bias-relaxed:
  opposed direction allowed only when room ≥ 2 × risk (S4). Target stays entry ± 2 × risk.
- All other rules unchanged: setups 2/3/4 only, second-close confirmation, structural stop
  (OR low −0.1% / OR high +0.1% of prev close), give-back partial 50 at 1 × risk with rest
  trailed to breakeven, no re-entry, 100 shares, ₹40/trade, 15:10 square-off, cash intraday only.

## Engine
`stock_system_continued.py` with `room_min=1.25`, `nifty_mode='bias_relaxed_room2'`, `cap_rank='room'`.
Trade CSV: `s5_trades_jan_oct_2026.csv`, uncapped `s5_uncapped_jan_oct_2026.csv`.
Jan–Oct 2026 run is in-sample context only; S5 is NOT adopted on it.
