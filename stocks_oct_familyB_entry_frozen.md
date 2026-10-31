# Stocks October tuning — Family B: entry filters — FROZEN 2026-10-30 BEFORE SCORING

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade cost, NOT premiums, NOT a lot profit.

Diagnosis first: October candidate scarcity is the binding failure, not
the cap and not room alone (S10 finding: prospective ≥₹500 floor and the
second-close confirmation chain cut far more candidates than room).
October S8 funnel produced only 3 uncapped candidates in 18 trading days.
Each variant below changes ONE entry-filter parameter of the S8/S9 price
design (gate G-TIERED and cap 1/day, 1/stock/week unchanged), except the
two pre-registered combos at the end. No per-trade or per-date deletions,
no hindsight filters.

Variants:
- B0 baseline S8/S9 (prospective ≥₹500, room ≥1.5×, OR width 0.25–3.0%, second-close required, Nifty bias block on)
- B1 prospective floor ₹500 → ₹250
- B2 room floor 1.5× → 1.25×
- B3 room floor 1.5× → 1.0×
- B4 OR width 0.25–3.0% → 0.15–4.0%
- B5 second-close confirmation dropped (PE: entry = open after signal candle, stop = signal high; CE pullback: entry = open after pullback candle, stop = pullback low; all other rules unchanged)
- B6 Nifty bias block removed (PE allowed on bullish Nifty days, CE allowed on bearish Nifty days; stock's own bias filter unchanged)
- B7 combo loose: B1 + B2 + B4 together
- B8 combo no-second-close + loose: B5 + B1 + B2 + B4 together

Scored on: October 2026 slice AND Jan–Sep 2026 separately (anti-overfit).
Progress required on net + win rate + frequency together vs S9 October,
with Jan–Sep not destroyed. Stage pass only; November paper validates.
