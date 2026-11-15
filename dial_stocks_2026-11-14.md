# DIAL — STOCKS · GATE REPORT · 2026-11-14

Programme: DIAL (one roof, one name). Member: standalone indicator system, Stocks segment.
Spec: `dial_stocks_SPEC.md` (core frozen verbatim before scoring; data/fill details recorded there).
Build: `dial_stocks_build.py` · Numbers: `dial_stocks_results.json` · Trades: `dial_stocks_trades.csv`.
Basis: **equity cash intraday · frozen 25-name Stock Book watchlist · per 100 shares
PROVISIONAL · ₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
This system is STANDALONE — it does not condition or filter the Stock Book. The Stock Book
itself is untouched and stands as it was.

## VERDICT — FAIL, both components, both years, on essentially every gate leg

There is no standalone indicator channel in the 25 names under this frozen core. DIAL-T and
DIAL-R both lose money in 2025 and 2026; the combined DIAL-Stocks book is negative in
**all 20 months** of the two gate windows. Nothing passes, nothing is adopted, nothing arms.

## Coverage / NC

- Gate windows (Jan–Oct): 2025 = 5,200 stock-days, 2026 = 5,125 stock-days; 25 names ×
  every trading day present in the store, no duplicate bars.
- NC: 25 stock-days, all on **2025-10-21** (Diwali Muhurat session, 13:45–14:40, 12 bars,
  no 15:10 bar → untradable under the frozen square-off rule). 2026: 0 NC. Partial days
  containing the 15:10 bar (ITC 2025-01-06, VEDL 2026-04-30) traded on their present bars.
- November CF: 9 book trading days scored; the 14 bars stamped 2026-11-08 (Sunday stub)
  are NC (25 stock-days), excluded.
- Timing audit: entry bar strictly follows the signal bar on every trade (asserted in the
  build); every indicator at bar t is a trailing function of bars ≤ t; entry fills are the
  next bar's open. Hand-check: ASTRAL 2026-11-02 DIAL-R SHORT, entry 09:25 @1350.50,
  stop level 1350.50 × 1.005 = 1357.2525 = recorded exit, net −₹715.25 ✓.

## Fill detail that matters (from the SPEC)

The persisted full-history stock stores carry **no volume** (OHLC only), so session VWAP is
the equal-weighted cumulative mean of bar typical price — "session VWAP (EW proxy)". Every
DIAL-T figure below is on that basis. All other indicators (Supertrend(7,3), RSI(14),
Bollinger(20,2), EMA50) are standard constructions on the continuous per-stock 5-min series.

## Results — per year, per component (Jan–Oct)

### DIAL-T (Supertrend flip + VWAP side)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 4,254 | **−₹125,217.24** | 35.71% | −₹12,521.72 | 83.0 | −65,618.76 / −59,598.48 | −₹135,752.84 | 10/10 | FAIL — placebo, halves, ex-top-3, pace, red months (every leg) |
| 2026 | 4,274 | **−₹127,459.09** | 36.10% | −₹12,745.91 | 77.5 | −84,131.44 / −43,327.65 | −₹140,507.09 | 8/10 | FAIL — every leg |

Months 2025: Jan −3,576.50 · Feb −14,100.12 · Mar −25,606.13 · Apr −8,166.93 · May −14,169.08 ·
Jun −13,214.21 · Jul −4,214.37 · Aug −8,491.55 · Sep −8,464.06 · Oct −25,214.29.
Months 2026: Jan +880.01 · Feb −3,868.43 · Mar −30,377.05 · Apr −35,960.05 · May −14,805.92 ·
Jun −15,616.88 · Jul −14,929.04 · Aug −23,347.28 · Sep +22,564.93 · Oct −11,999.38.

### DIAL-R (RSI + %B extreme, EMA50 slope guard)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 2,438 | **−₹68,420.73** | 37.33% | −₹6,842.07 | 75.0 | −22,272.60 / −46,148.13 | −₹78,930.63 | 7/10 | FAIL — every leg |
| 2026 | 2,465 | **−₹165,302.21** | 35.29% | −₹16,530.22 | **2.5** | −58,461.24 / −106,840.97 | −₹178,080.11 | 9/10 | FAIL — every leg; worse than random entry |

Months 2025: Jan +586.78 · Feb +2,591.07 · Mar −14,932.55 · Apr −1,396.47 · May −9,121.43 ·
Jun −17,323.02 · Jul −10,681.12 · Aug +6,035.26 · Sep −22,250.71 · Oct −1,928.54.
Months 2026: Jan −29,387.73 · Feb −15,929.80 · Mar −15,196.83 · Apr −6,725.33 · May +8,778.45 ·
Jun −12,835.33 · Jul −33,880.62 · Aug −23,053.65 · Sep −30,549.59 · Oct −6,521.78.

### DIAL-Stocks combined (T ∪ R)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 6,692 | **−₹193,637.97** | 36.30% | −₹19,363.80 | 93.5 | −87,891.36 / −105,746.61 | −₹204,227.57 | 10/10 | FAIL — every leg (placebo closest at 93.5, bar 95) |
| 2026 | 6,739 | **−₹292,761.31** | 35.81% | −₹29,276.13 | 26.5 | −142,592.68 / −150,168.63 | −₹305,861.91 | 10/10 | FAIL — every leg |

Months 2025: Jan −2,989.72 · Feb −11,509.05 · Mar −40,538.68 · Apr −9,563.40 · May −23,290.51 ·
Jun −30,537.23 · Jul −14,895.49 · Aug −2,456.29 · Sep −30,714.77 · Oct −27,142.83.
Months 2026: Jan −28,507.72 · Feb −19,798.23 · Mar −45,573.88 · Apr −42,685.38 · May −6,027.47 ·
Jun −28,452.21 · Jul −48,809.66 · Aug −46,400.93 · Sep −7,984.66 · Oct −18,521.17.

## The structural finding (why the placebo matters here)

The frozen exit geometry itself bleeds on these names at this frequency. Across 200
random-entry draws per series-year, even the **best** random draw loses heavily
(combined 2026: best −₹93,128, median −₹252,100; DIAL-T 2025: best −₹47,610). The signals
do beat the random median in five of six series-years — the indicators are not pure noise —
but the edge is far smaller than the drag of ~13–18 trades a day × ₹40 plus square-off
slippage against a +1.0%/−0.5% frame. The one series that cannot even claim that is
**DIAL-R 2026 (2.5th percentile)**: faded extremes kept running in 2026, and the reversion
dial picked worse entries than a coin flip. Win rates sit at 35–37% against the ~33%
breakeven the 2:1 payoff implies before costs — close enough to look alive, far enough
to bleed steadily after costs and square-offs.

## November counterfactual (descriptive — Nov 2–13, the book's 9 trading days)

| Series | Trades | Net | vs Stock Book actual |
|---|---|---|---|
| DIAL-T | 184 | −₹12,625.28 | — |
| DIAL-R | 109 | −₹7,841.15 | — |
| **DIAL combined** | **293** | **−₹20,466.44** | **Stock Book +₹7,517.94** |

By day (combined): Nov 2 −4,257.03 · Nov 3 +434.04 · Nov 4 −6,978.40 · Nov 5 −5,485.06 ·
Nov 6 +1,063.76 · Nov 9 −6,601.61 · Nov 11 +2,090.80 · Nov 12 −943.47 · Nov 13 +210.57.
On the very days the Stock Book made +₹7,517.94 with 32 trades, DIAL would have fired
293 trades and lost ₹20,466.44. The forward window agrees with the gate.

## Honest one-liner

**There is no standalone indicator channel in the 25 names under this core** — neither the
trend dial nor the reversion dial carries it: both lose in both years, the reversion dial
is worse than random in 2026, and the frozen +1.0%/−0.5% geometry at first-signal-per-day
frequency is itself a losing frame on these names before any signal quality is even asked.
The Stock Book's channel stays where it already was — its own construction — and DIAL-Stocks
is recorded as a measured dead end, not a near miss.
