# EKAM-INTRADAY — NIFTY · GATE REPORT · 2026-11-14

Programme: EKAM-INTRADAY v1 (standard indicators clubbed by votes — intraday, NOT the
daily EKAM swing book). Spec: `ekam_intraday_nifty_SPEC.md` (frozen before scoring).
Build: `ekam_intraday_nifty_build.py` · Numbers: `ekam_intraday_nifty_results.json` ·
Trades: `ekam_intraday_nifty_trades.csv`.
Basis: **option buying only · 1 lot (65) · Rs220/trade · paper only, real money Rs0.**
203 trading days, Jan–Oct 2026. Research only — nothing running was changed.

## The core (as frozen)

Per completed 5-min bar, LONG votes (mirror SHORT), +1 each: (1) futures close vs
session VWAP (basis-consistent), (2) EMA(9) > EMA(21), (3) Supertrend(7,3) bullish,
(4) MACD(12,26,9) line > signal, (5) RSI(14) in [50,70) (short: (30,50)), (6) ADX(14)
≥ 20 adds +1 to the leading side. Entry = first bar of the day at ≥ T votes, next bar
at the stored weekly nearest-strike contract open. One trade/day. X1 = stop −50 /
target +90 / square-off 15:20. X2 = vote-decay exit (own votes ≤ 2 → next bar open),
hard stop −60, square-off 15:20.

## Results — all four rows, all windows

| Row | Window | Trades | Net (Rs) | WR % | Rs/trade-day |
|---|---|---|---|---|---|
| T4-X1 | Jan–Jun | 110 | −76,660.85 | 34.5 | −696.92 |
| T4-X1 | Jul–Oct | 75 | −37,568.45 | 36.0 | −500.91 |
| **T4-X1** | **Jan–Oct** | **185** | **−114,229.30** | **35.1** | **−617.46** |
| T4-X2 | Jan–Jun | 110 | −77,500.65 | 25.5 | −704.55 |
| T4-X2 | Jul–Oct | 75 | −34,780.60 | 22.7 | −463.74 |
| **T4-X2** | **Jan–Oct** | **185** | **−112,281.25** | **24.3** | **−606.93** |
| T5-X1 | Jan–Jun | 99 | −53,417.45 | 34.3 | −539.57 |
| T5-X1 | Jul–Oct | 68 | −32,772.60 | 39.7 | −481.95 |
| **T5-X1** | **Jan–Oct** | **167** | **−86,190.05** | **36.5** | **−516.11** |
| T5-X2 | Jan–Jun | 99 | −57,062.00 | 29.3 | −576.38 |
| T5-X2 | Jul–Oct | 68 | −25,031.75 | 26.5 | −368.11 |
| **T5-X2** | **Jan–Oct** | **167** | **−82,093.75** | **28.1** | **−491.58** |

Every row loses in both windows. Best full-year row = **T5-X2** (−Rs82,093.75).
Direction split is balanced (T4 rows: 95 CE / 90 PE; T5 rows: 84 CE / 83 PE) — both
sides lose. X1 exit mix (T5): 30 targets / 72 stops / 65 square-offs. X2 exit mix
(T5): 153 decay exits / 7 hard stops / 7 square-offs — the decay rule fires early on
almost every trade.

## Coverage / NC

- T4 rows: 203 signals (a signal fired on **every** trading day; 0 no-signal days),
  18 NC — all `nc_no_file` → 185 scored.
- T5 rows: 203 signals, 36 NC — all `nc_no_file` → 167 scored.
- NC counted, never substituted (the exact nearest-strike weekly contract-day file
  was never stored).

## Vote-count distribution

- Daily maximum votes reach 6 on 149 of 203 days (LONG) and 153 of 203 days
  (SHORT); the daily max is ≥ 5 on 186 days (LONG) and 188 days (SHORT). The six
  voters are state indicators on a continuous series, so the vote count is already
  saturated at the open on most days.
- Signal bars: 99.5% of T4 scored signals are at 09:15–09:20; 86.2% for T5. The
  "first bar at ≥ T votes" is, in practice, the opening bar.
- Scored signal vote pairs (LONG,SHORT) — T5 rows: (0,5) 41 · (1,5) 37 · (5,0) 40 ·
  (5,1) 29 · (6,0) 15 · (0,6) 5. T4 rows add the 4-vote pairs: (4,1) 25 · (1,4) 19 ·
  (4,2) 5 · (2,4) 7 · (4,0) 3 · (0,4) 6 on top of the same 5–6-vote pairs.

## Timing audit

PASS — all 704 scored trades across the four rows verified: entry bar = signal bar
+ 5 min and entry premium = stored open of the entry bar. Independent recomputation
at the T5-X2 first scored signal bar (2026-01-02, 09:20) matched the main path on
RSI(14) (65.597), EMA(9)/EMA(21) (26,162.18 / 26,158.21), MACD line/signal
(2.894 / 0.425) and Supertrend direction (+1).

## Random-entry placebo (best row T5-X2)

1,000 iterations, same 167-trade count, random scorable contract-day files and entry
bars, same X2 exits and cost: placebo mean **−Rs9,583.31**, p95 **+Rs47,095.89**.
The real T5-X2 total (−Rs82,093.75) sits at the **0.6th percentile** — below 99.4%
of random-entry books. (Random books also lose on average under this geometry; the
vote-clubbed entries lose far more, concentrated at the open.)

## November CF (descriptive, Nov 2–13, 9 trading days)

All rows: 9 signals, 2 NC (`nc_no_file`), 7 scored trades — every signal at
09:15–09:20, all CE except one PE (T5 rows, Nov 6).

| Row | Trades | Net (Rs) | WR % |
|---|---|---|---|
| T4-X1 | 7 | +6,604.50 | 57.1 |
| T4-X2 | 7 | +1,654.75 | 28.6 |
| T5-X1 | 7 | −2,186.75 | 42.9 |
| T5-X2 (best Jan–Oct row) | 7 | +120.75 | 28.6 |

T5-X2 November trades: Nov 2 CE 23250 −853.75 (decay) · Nov 3 CE 23600 +2,571.75
(decay) · Nov 4 CE 23850 −2,894.75 (decay) · Nov 5 CE 24350 +8,330.75 (square-off) ·
Nov 6 PE 24500 −3,037.75 (decay) · Nov 9 CE 24900 −2,820.00 (decay) · Nov 12 CE 25300
−1,175.50 (decay).

## Plain reading

The vote club does not separate anything on Nifty intraday: the voters agree with
each other (they are five readings of the same trend state), the count saturates by
the open, and the resulting opening entries bleed through both exit rules in both
halves of the year — worse than random entry at the same trade count. Nothing here
is a candidate to arm.
