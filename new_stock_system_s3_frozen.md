# S3 — Intraday STOCK system (cash, NOT options) — FROZEN for scoring, NOT adopted

**Status: FROZEN 2026-10-29, NOT adopted, NOT a live system. Paper only, no orders.**
- S3 is the first iteration after S2 failed the satisfaction bar (see continuation report).
- Exactly ONE change from S2, everything else identical to S2 (which is identical to S1
  except S2-1/S2-2).

## The one S3 change
- **Room: finite AND ≥ 1.25 × risk** (was ≥ 1.5 × risk in S2, ≥ 2 × risk in S1).
  Target stays entry ± 2 × risk. Finite-room rule retained: no PD level beyond entry = fail.
- Nifty confirmation stays bias-only (CE allowed on bullish/neutral, PE on bearish/neutral,
  block only directly opposed, bias bands bearish <35%, neutral 35–79%, bullish ≥80%).
- Cap ranking stays target-net DESC, then room ratio, then setup rank.
- All other rules unchanged: setups 2/3/4 only, second-close confirmation, structural stop
  (OR low −0.1% / OR high +0.1% of prev close), give-back partial 50 at 1 × risk with rest
  trailed to breakeven, no re-entry, cap 3/week, 1/stock/week, prospective target ≥ ₹500,
  100 shares, ₹40/trade, 15:10 square-off, cash intraday only.

## Engine
`stock_system_continued.py` with `room_min=1.25`, `nifty_mode='bias_only'`, `cap_rank='target'`.
Trade CSV: `s3_trades_jan_oct_2026.csv`, uncapped `s3_uncapped_jan_oct_2026.csv`.
Jan–Oct 2026 run is in-sample context only; S3 is NOT adopted on it.
