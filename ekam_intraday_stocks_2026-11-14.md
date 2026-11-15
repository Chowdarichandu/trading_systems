# EKAM-INTRADAY — STOCKS · RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment. Spec: `ekam_intraday_stocks_SPEC.md`
(frozen before scoring). Build: `ekam_intraday_stocks_build.py` · Numbers:
`ekam_intraday_stocks_results.json` · Trades: `ekam_intraday_stocks_trades.csv`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (the persisted stores carry no volume).
This system is STANDALONE — intraday only, nothing daily in it.

## The core (one line)

Six standard indicators clubbed as votes on completed 5-min bars — VWAP side, EMA(9) vs
EMA(21), Supertrend(7,3), MACD(12,26,9), RSI(14) zone, ADX(14) ≥ 20 to the leading side.
First bar of the day per stock reaching the vote threshold is the entry (next bar's open);
max 1 trade per stock per day, max 5 per day across the list. Rows: threshold T ∈ {4, 5}
× exit X1 (fixed +1.0% / −0.5%) or X2 (vote-decay to ≤ 2, hard stop −0.75%); square-off
15:15 either way.

## Coverage / audit

- Gate windows (Jan–Oct): 2025 = 5,200 stock-days, 25 NC (2025-10-21 Muhurat, all names);
  2026 = 5,125 stock-days, 0 NC. Identical coverage to DIAL-Stocks.
- Timing audit: entry stamp strictly after signal stamp asserted on all 4,620 trades;
  vote counts recomputed from truncated series (bars ≤ t only) on 625 sampled signal
  bars — **0 mismatches**.
- The 5-per-day cap binds on every trading day of both years (207 × 5 = 1,035 trades in
  2025; 205 × 5 = 1,025 in 2026, at both thresholds) — row differences are signal
  selection and exit effects, not trade-count effects.

## Results — per row, per year (trades · net ₹ · WR)

### 2025

| Row | Jan–Jun | Jul–Oct | Full Jan–Oct |
|---|---|---|---|
| T4-X1 | 615 · −29,967.29 · 34.31% | 420 · −25,603.98 · 33.81% | 1,035 · **−55,571.28** · 34.11% |
| T4-X2 | 615 · +39,924.74 · 33.66% | 420 · −19,365.34 · 31.19% | 1,035 · **+20,559.40** · 32.66% |
| T5-X1 | 615 · −21,266.30 · 35.45% | 420 · −12,098.40 · 33.57% | 1,035 · **−33,364.70** · 34.69% |
| T5-X2 | 615 · +40,469.38 · 32.85% | 420 · −3,634.81 · 33.57% | 1,035 · **+36,834.57** · 33.14% |

### 2026

| Row | Jan–Jun | Jul–Oct | Full Jan–Oct |
|---|---|---|---|
| T4-X1 | 600 · −9,372.75 · 34.67% | 425 · −8,918.68 · 35.29% | 1,025 · **−18,291.43** · 34.93% |
| T4-X2 | 600 · +36,131.93 · 32.33% | 425 · +15,321.45 · 34.82% | 1,025 · **+51,453.37** · 33.37% |
| T5-X1 | 600 · −736.62 · 35.17% | 425 · −14,522.02 · 33.65% | 1,025 · **−15,258.65** · 34.54% |
| T5-X2 | 600 · +47,056.05 · 33.67% | 425 · −12,089.39 · 33.65% | 1,025 · **+34,966.66** · 33.66% |

## Placebo (best full-year row per year; 200 random-entry draws, same count and exit rule)

| Year | Row | Real total | Placebo pct | Draw min / median / max |
|---|---|---|---|---|
| 2025 | T5-X2 | +₹36,834.57 | **100.0** | −77,360.94 / −36,414.63 / +3,269.50 |
| 2026 | T4-X2 | +₹51,453.37 | **100.0** | −72,813.65 / −34,220.01 / +7,062.86 |

## November CF (descriptive — Nov 2–13, 9 trading days, 45 trades per row)

| Row | Trades | Net ₹ | WR |
|---|---|---|---|
| T4-X1 | 45 | +763.05 | 37.78% |
| T4-X2 | 45 | +13,261.40 | 40.00% |
| T5-X1 | 45 | +5,251.50 | 46.67% |
| T5-X2 | 45 | **+18,563.30** | 44.44% |

(The 2026-11-08 Sunday stub, 25 stock-days, is NC and excluded.)

## Plain facts from the tables

- The exit rule is the whole difference: at both thresholds and in both years, X1
  (fixed +1.0%/−0.5%) loses money (−₹55,571 / −₹33,365 in 2025; −₹18,291 / −₹15,259 in
  2026) and X2 (vote-decay) makes money (+₹20,559 / +₹36,835 in 2025; +₹51,453 /
  +₹34,967 in 2026) on the same entries.
- T4-X2 is the only row positive in both windows of 2026 and the best 2026 row
  (+₹51,453.37, placebo 100.0). T5-X2 is the best 2025 row (+₹36,834.57, placebo 100.0).
- Both X2 rows earn their year in Jan–Jun and give some back in Jul–Oct in 2025
  (−₹19,365 / −₹3,635) and at T5 in 2026 (−₹12,089); T4-X2's Jul–Oct 2026 stays positive
  (+₹15,321.45).
- Win rates sit at 32–35% in every row and window — the vote entries pay through the
  decay exit letting winners run past +1.0%, not through hit rate.
- November's 9 days are positive on all four rows (+₹763 to +₹18,563).
