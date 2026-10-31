# Volrix NiftyLargeDownRebound — separate-system backtest (paper only, no orders)

**Status: separate system only. NOT mixed into v4 / (lA) totals, NOT netted against PE losses, NOT adopted.**
This report replicates the Volrix code pasted by the user exactly as written. No improvement, no re-tuning, no parameter change.

## 1. Logic replicated (from the pasted code, verbatim in intent)

- `onNewDay`: if in position, `sess += 1`; if `cool > 0`, `cool -= 1`. `skip_today = True` if the monthly-expiry-0 date changed versus the previous day; `prev_e0` updated.
- Entry check at >= 09:16, once per day (`checked` flag): if `reopen` flag is set, buy monthly expiry 0 regardless of trigger/cool/skip. Else if not in position and `cool == 0`, take daily NIFTY closes before today (code window: last 12 calendar days); if >= 2 closes and `not skip_yday` and yesterday's close / day-before close - 1 <= -0.02, then `cool = 10`, `sess = 1`, buy monthly expiry 0, 1 lot FUT.
- Buy has **no stop loss and no target** (`isSL: False`, `isTarget: False`). Exit check at >= 15:15 if in position: if `sess >= 5`, square off, `in_pos = False`. Else if held monthly expiry <= today, square off, `in_pos` stays True, `reopen = True` (re-buy next day at 09:16).
- After the 09:16 check, `skip_yday = skip_today`. Consequence, replicated exactly: an entry is skipped on the day after the first trading day following a monthly expiry (because that first day sets `skip_today = True`, which becomes the next day's `skip_yday`). One real case: entry on 2026-03-30 was blocked by this quirk (expiry changed on 2026-03-27); the next entry was 2026-04-01, from the 2026-03-30 down close.
- Session counting: entry day = sess 1, so the 5th-session exit is the entry day + 4 trading days. Cooldown: `cool = 10` on entry, decremented once per trading day, so the next entry is at least 10 trading days after the previous entry (and only after the position has exited).

## 2. Data actually used — and what was NOT available

- **Futures continuous history: NOT available through the Upstox helper.** The helper's search returns only live futures contracts (e.g. NIFTY FUT 23 NOV 26, lot 65); expired monthly contracts' instrument keys are not retrievable through it, so a Jul 2019–Oct 2026 front-month futures series could not be built from this route. **Therefore the whole backtest uses NIFTY SPOT as a labelled proxy.** Futures would differ by basis, by the futures premium/discount on entry and exit days, and by the roll gap on the 4 expiry rolls below. Those differences are unquantifiable from spot alone and are NOT estimated here.
- **Spot daily closes: Upstox, NSE_INDEX|Nifty 50, 2019-07-01 to 2026-10-28, 1,818 trading days**, fetched in yearly chunks and saved at `nifty_daily_2019_2026.csv`. Trigger days are computed from these closes.
- **Spot intraday: Upstox 1-minute bars.** Tested: 1-min/5-min intraday returns **0 bars for 2019, 2020 and 2021** (e.g. 2019-08, 2021-06, 2021-12 all empty) and full data from **2022-01-03 onward** (375 bars/day). So: entry/exit prices for 2022+ legs are the **close of the 1-min bar starting 09:16** (entry) and the **close of the 1-min bar starting 15:15** (exit), fetched per day and saved at `intraday_1min_prices.json` (30 days, all present). For pre-2022 legs, no intraday exists via this route, so entry = **daily open** and exit = **daily close**, labelled as an approximation in every row.
- **Monthly expiry calendar: last Thursday of each month**, used for both the skip rule and the roll rule. It was NOT verified month-by-month against the NSE holiday calendar; a holiday-shifted expiry could move a skip/roll date by a day in a few months. Impact is limited to skip/roll timing on a small number of trades, and is stated here rather than hidden.
- **Lot size (stated, not assumed silently): 75 for entries before the January 2026 monthly expiry, 65 from the January 2026 expiry onward** — NSE reduced Nifty lot 75 -> 65 with effect from the December 30, 2025 expiry cycle (monthly contracts migrating with the January 2026 expiry), confirmed by the live Upstox contract showing lot 65. No backtest entry falls in the Oct 2025–Jan 2026 transition window, so the boundary is clean in this sample.

## 3. Headline results (primary basis: 1-min spot 2022+, daily open/close pre-2022)

| Metric | Value |
|---|---|
| Period (actual data used) | 2019-07-01 to 2026-10-28 (first entry 2019-07-09, last exit 2026-07-15) |
| Positions (1 lot each, continuous holding incl. rolls) | 30 |
| Legs (initial buys + roll re-buys) | 34 (30 initial + 4 roll re-buys) |
| Wins / losses (position net > 0) | 20 / 10 |
| Win rate | 66.7% |
| Total points (sum of leg exit - entry, spot proxy) | +4,827.45 |
| Gross profit (points x lot, lot schedule above) | +Rs 3,49,737.25 |
| Charges (formula below) | -Rs 12,007.14 |
| Net profit (1 lot throughout, lot schedule above) | +Rs 3,37,730.11 |
| Profit factor, gross | 2.30 (gross wins Rs 6,18,825.50 / gross losses Rs 2,69,088.25) |
| Profit factor, net of charges | 2.24 (net wins Rs 6,10,704.01 / net losses Rs 2,72,973.90) |
| Expectancy, net | +Rs 11,257.67 per position (160.91 points per position, gross points basis) |
| Average net win / average net loss | +Rs 30,535.20 / -Rs 27,297.39 |
| Largest win / largest loss (net, per position) | +Rs 86,130.65 (2024-06-05 entry) / -Rs 1,02,775.12 (2020-03-11 entry, COVID crash continuation) |
| Max drawdown, net Rs (peak-to-trough on cumulative position net) | Rs 1,40,336.12 — peak after trade 3 (2020-02-03 entry, cumulative +Rs 57,136.35), trough after trade 5 (2020-03-11 entry, cumulative -Rs 83,199.77) |
| Max drawdown, points (same peak/trough) | 1,860.70 points (peak cumulative +772.95, trough -1,087.75) |
| Trades per year (positions) | ~4.1 per year on average; 2023 had ZERO positions (no -2% close-to-close down day in the spot data between 2022-06-16 and 2024-01-17) |

### Charges formula (applied per leg, current-rate approximation applied across the whole window; historical rates differed slightly)
Brokerage Rs 20 per order (Rs 40 per leg round trip) + STT 0.02% of sell value + exchange transaction 0.0019% of (entry + exit) value + SEBI Rs 10 per crore of (entry + exit) value + stamp duty 0.002% of buy value + GST 18% on (brokerage + exchange + SEBI). Total charges across 34 legs: Rs 12,007.14 (3.4% of gross profit). Taxes/fees beyond this formula are not included.

### By year (position net, 1 lot)

| Year | Positions | Wins | Net Rs |
|---|---|---|---|
| 2019 | 2 | 2 | +22,106.96 |
| 2020 | 11 | 6 | +3,623.56 |
| 2021 | 3 | 2 | +31,034.09 |
| 2022 | 6 | 4 | +60,113.71 |
| 2023 | 0 | 0 | 0.00 |
| 2024 | 4 | 3 | +75,768.47 |
| 2025 | 1 | 1 | +66,367.49 |
| 2026 (to 28 Oct) | 3 | 2 | +78,715.83 |

### Sensitivity: uniform daily open/close basis for ALL legs
If entry = daily open and exit = daily close for every leg (ignoring intraday timing entirely), the result is: **30 positions, 20 wins, net +Rs 3,65,836.74** — Rs 28,106.63 higher than the primary basis. The win count is identical and the conclusion (positive total, ~2/3 win rate) does not depend on the entry/exit timing basis. Per-position sensitivity nets are in the last column of the trade table.

## 4. Full trade list (positions; legs indented in the leg columns)

Entry price basis: `1min` = close of the 09:16 1-min spot bar (entry) / close of the 15:15 1-min spot bar (exit); `daily` = daily open (entry) / daily close (exit). Points and Rs are per leg; position net is the sum of its legs minus leg charges. Roll legs: the first leg exits at 15:15 on the monthly expiry day and the position re-buys at 09:16 on the next trading day; the position's 5-session clock does NOT reset (sess keeps counting, exactly as the code does).

| # | Entry | Trigger down % | Leg entry -> exit (reason) | Entry price (basis) | Exit price (basis) | Lot | Leg points | Leg net Rs | Position net Rs | Sens. net Rs (daily basis) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2019-07-09 | -2.14% | 2019-07-09 -> 2019-07-15 (5th_session_close) | 11531.6 (daily) | 11588.35 (daily) | 75 | 56.75 | 3,977.01 | 3,977.01 | 3,977.01 |
| 2 | 2019-09-04 | -2.04% | 2019-09-04 -> 2019-09-11 (5th_session_close) | 10790.4 (daily) | 11035.7 (daily) | 75 | 245.30 | 18,129.95 | 18,129.95 | 18,129.95 |
| 3 | 2020-02-03 | -2.51% | 2020-02-03 -> 2020-02-07 (5th_session_close) | 11627.45 (daily) | 12098.35 (daily) | 75 | 470.90 | 35,029.39 | 35,029.39 | 35,029.39 |
| 4 | 2020-02-25 | -2.08% | 2020-02-25 -> 2020-02-27 (expiry_roll)<br>2020-02-28 -> 2020-03-02 (5th_session_close) | 11877.5 (daily) | 11132.75 (daily) | 75,75 | -493.45 | -37,561.00 | -37,561.00 | -37,561.00 |
| 5 | 2020-03-11 | -4.90% | 2020-03-11 -> 2020-03-17 (5th_session_close) | 10334.29 (daily) | 8967.04 (daily) | 75 | -1367.25 | -102,775.12 | -102,775.12 | -102,775.12 |
| 6 | 2020-03-31 | -4.38% | 2020-03-31 -> 2020-04-08 (5th_session_close) | 8529.35 (daily) | 8748.75 (daily) | 75 | 219.40 | 16,233.19 | 16,233.19 | 16,233.19 |
| 7 | 2020-04-22 | -3.03% | 2020-04-22 -> 2020-04-28 (5th_session_close) | 9026.75 (daily) | 9380.9 (daily) | 75 | 354.15 | 26,327.21 | 26,327.21 | 26,327.21 |
| 8 | 2020-05-15 | -2.57% | 2020-05-15 -> 2020-05-21 (5th_session_close) | 9182.4 (daily) | 9106.25 (daily) | 75 | -76.15 | -5,941.19 | -5,941.19 | -5,941.19 |
| 9 | 2020-06-12 | -2.12% | 2020-06-12 -> 2020-06-18 (5th_session_close) | 9544.95 (daily) | 10091.65 (daily) | 75 | 546.70 | 40,754.85 | 40,754.85 | 40,754.85 |
| 10 | 2020-09-01 | -2.23% | 2020-09-01 -> 2020-09-07 (5th_session_close) | 11464.3 (daily) | 11355.05 (daily) | 75 | -109.25 | -8,468.86 | -8,468.86 | -8,468.86 |
| 11 | 2020-09-22 | -2.21% | 2020-09-22 -> 2020-09-24 (expiry_roll)<br>2020-09-25 -> 2020-09-28 (5th_session_close) | 11301.75 (daily) | 11227.55 (daily) | 75,75 | -179.05 | -13,965.28 | -13,965.28 | -13,965.28 |
| 12 | 2020-10-16 | -2.43% | 2020-10-16 -> 2020-10-22 (5th_session_close) | 11727.4 (daily) | 11896.45 (daily) | 75 | 169.05 | 12,393.70 | 12,393.70 | 12,393.70 |
| 13 | 2020-12-22 | -3.14% | 2020-12-22 -> 2020-12-29 (5th_session_close) | 13373.65 (daily) | 13932.6 (daily) | 75 | 558.95 | 41,596.67 | 41,596.67 | 41,596.67 |
| 14 | 2021-02-23 | -2.04% | 2021-02-23 -> 2021-02-25 (expiry_roll)<br>2021-02-26 -> 2021-03-01 (5th_session_close) | 14782.25 (daily) | 14761.55 (daily) | 75,75 | 188.05 | 13,411.59 | 13,411.59 | 13,411.59 |
| 15 | 2021-04-13 | -3.53% | 2021-04-13 -> 2021-04-20 (5th_session_close) | 14364.9 (daily) | 14296.4 (daily) | 75 | -68.50 | -5,471.42 | -5,471.42 | -5,471.42 |
| 16 | 2021-12-21 | -2.18% | 2021-12-21 -> 2021-12-27 (5th_session_close) | 16773.15 (daily) | 17086.25 (daily) | 75 | 313.10 | 23,093.92 | 23,093.92 | 23,093.92 |
| 17 | 2022-01-25 | -2.66% | 2022-01-25 -> 2022-01-27 (expiry_roll)<br>2022-01-28 -> 2022-02-01 (5th_session_close) | 16914.0 (1min) | 17576.05 (1min) | 75,75 | 524.10 | 38,519.33 | 38,519.33 | 34,997.53 |
| 18 | 2022-02-15 | -3.06% | 2022-02-15 -> 2022-02-21 (5th_session_close) | 16966.9 (1min) | 17188.65 (1min) | 75 | 221.75 | 16,240.31 | 16,240.31 | 20,113.87 |
| 19 | 2022-03-08 | -2.35% | 2022-03-08 -> 2022-03-14 (5th_session_close) | 15827.15 (1min) | 16852.1 (1min) | 75 | 1024.95 | 76,489.69 | 76,489.69 | 83,884.62 |
| 20 | 2022-05-05 | -2.29% | 2022-05-05 -> 2022-05-11 (5th_session_close) | 16834.95 (1min) | 16161.4 (1min) | 75 | -673.55 | -50,889.53 | -50,889.53 | -51,947.19 |
| 21 | 2022-05-20 | -2.65% | 2022-05-20 -> 2022-05-26 (5th_session_close) | 16059.9 (1min) | 16176.2 (1min) | 75 | 116.30 | 8,351.51 | 8,351.51 | 9,105.41 |
| 22 | 2022-06-14 | -2.64% | 2022-06-14 -> 2022-06-20 (5th_session_close) | 15741.75 (1min) | 15365.2 (1min) | 75 | -376.55 | -28,597.60 | -28,597.60 | -24,663.38 |
| 23 | 2024-01-18 | -2.09% | 2024-01-18 -> 2024-01-24 (5th_session_close) | 21414.1 (1min) | 21466.15 (1min) | 75 | 52.05 | 3,426.54 | 3,426.54 | 2,504.24 |
| 24 | 2024-06-05 | -5.93% | 2024-06-05 -> 2024-06-11 (5th_session_close) | 22094.6 (1min) | 23249.8 (1min) | 75 | 1155.20 | 86,130.65 | 86,130.65 | 84,727.79 |
| 25 | 2024-08-06 | -2.68% | 2024-08-06 -> 2024-08-12 (5th_session_close) | 24318.8 (1min) | 24359.0 (1min) | 75 | 40.20 | 2,479.78 | 2,479.78 | 11,251.65 |
| 26 | 2024-10-04 | -2.12% | 2024-10-04 -> 2024-10-10 (5th_session_close) | 25190.4 (1min) | 24980.8 (1min) | 75 | -209.60 | -16,268.50 | -16,268.50 | -14,307.52 |
| 27 | 2025-04-08 | -3.24% | 2025-04-08 -> 2025-04-16 (5th_session_close) | 22535.2 (1min) | 23426.95 (1min) | 75 | 891.75 | 66,367.49 | 66,367.49 | 73,770.11 |
| 28 | 2026-03-16 | -2.06% | 2026-03-16 -> 2026-03-20 (5th_session_close) | 23133.0 (1min) | 23093.2 (1min) | 65 | -39.80 | -3,035.40 | -3,035.40 | -552.66 |
| 29 | 2026-04-01 | -2.14% | 2026-04-01 -> 2026-04-08 (5th_session_close) | 22824.1 (1min) | 23986.9 (1min) | 65 | 1162.80 | 75,121.49 | 75,121.49 | 70,931.88 |
| 30 | 2026-07-09 | -2.12% | 2026-07-09 -> 2026-07-15 (5th_session_close) | 23965.05 (1min) | 24074.2 (1min) | 65 | 109.15 | 6,629.74 | 6,629.74 | 9,255.78 |

### Leg detail (every leg, for audit)

| Position entry | Leg | Entry date | Entry price | Exit date | Exit reason | Exit price | Lot | Points | Gross Rs | Charges Rs | Net Rs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019-07-09 | 1 (initial, expiry 2019-07-25) | 2019-07-09 | 11531.6 | 2019-07-15 | 5th_session_close | 11588.35 | 75 | 56.75 | 4,256.25 | 279.24 | 3,977.01 |
| 2019-09-04 | 1 (initial, expiry 2019-09-26) | 2019-09-04 | 10790.4 | 2019-09-11 | 5th_session_close | 11035.7 | 75 | 245.30 | 18,397.50 | 267.55 | 18,129.95 |
| 2020-02-03 | 1 (initial, expiry 2020-02-27) | 2020-02-03 | 11627.45 | 2020-02-07 | 5th_session_close | 12098.35 | 75 | 470.90 | 35,317.50 | 288.11 | 35,029.39 |
| 2020-02-25 | 1 (initial, expiry 2020-02-27) | 2020-02-25 | 11877.5 | 2020-02-27 | expiry_roll | 11633.3 | 75 | -244.20 | -18,315.00 | 281.13 | -18,596.13 |
| 2020-02-25 | 2 (roll_rebuy, expiry 2020-03-26) | 2020-02-28 | 11382.0 | 2020-03-02 | 5th_session_close | 11132.75 | 75 | -249.25 | -18,693.75 | 271.12 | -18,964.87 |
| 2020-03-11 | 1 (initial, expiry 2020-03-26) | 2020-03-11 | 10334.29 | 2020-03-17 | 5th_session_close | 8967.04 | 75 | -1367.25 | -102,543.75 | 231.37 | -102,775.12 |
| 2020-03-31 | 1 (initial, expiry 2020-04-30) | 2020-03-31 | 8529.35 | 2020-04-08 | 5th_session_close | 8748.75 | 75 | 219.40 | 16,455.00 | 221.81 | 16,233.19 |
| 2020-04-22 | 1 (initial, expiry 2020-04-30) | 2020-04-22 | 9026.75 | 2020-04-28 | 5th_session_close | 9380.9 | 75 | 354.15 | 26,561.25 | 234.04 | 26,327.21 |
| 2020-05-15 | 1 (initial, expiry 2020-05-28) | 2020-05-15 | 9182.4 | 2020-05-21 | 5th_session_close | 9106.25 | 75 | -76.15 | -5,711.25 | 229.94 | -5,941.19 |
| 2020-06-12 | 1 (initial, expiry 2020-06-25) | 2020-06-12 | 9544.95 | 2020-06-18 | 5th_session_close | 10091.65 | 75 | 546.70 | 41,002.50 | 247.65 | 40,754.85 |
| 2020-09-01 | 1 (initial, expiry 2020-09-24) | 2020-09-01 | 11464.3 | 2020-09-07 | 5th_session_close | 11355.05 | 75 | -109.25 | -8,193.75 | 275.11 | -8,468.86 |
| 2020-09-22 | 1 (initial, expiry 2020-09-24) | 2020-09-22 | 11301.75 | 2020-09-24 | expiry_roll | 10805.55 | 75 | -496.20 | -37,215.00 | 265.37 | -37,480.37 |
| 2020-09-22 | 2 (roll_rebuy, expiry 2020-10-29) | 2020-09-25 | 10910.4 | 2020-09-28 | 5th_session_close | 11227.55 | 75 | 317.15 | 23,786.25 | 271.16 | 23,515.09 |
| 2020-10-16 | 1 (initial, expiry 2020-10-29) | 2020-10-16 | 11727.4 | 2020-10-22 | 5th_session_close | 11896.45 | 75 | 169.05 | 12,678.75 | 285.05 | 12,393.70 |
| 2020-12-22 | 1 (initial, expiry 2020-12-31) | 2020-12-22 | 13373.65 | 2020-12-29 | 5th_session_close | 13932.6 | 75 | 558.95 | 41,921.25 | 324.58 | 41,596.67 |
| 2021-02-23 | 1 (initial, expiry 2021-02-25) | 2021-02-23 | 14782.25 | 2021-02-25 | expiry_roll | 15097.35 | 75 | 315.10 | 23,632.50 | 348.72 | 23,283.78 |
| 2021-02-23 | 2 (roll_rebuy, expiry 2021-03-25) | 2021-02-26 | 14888.6 | 2021-03-01 | 5th_session_close | 14761.55 | 75 | -127.05 | -9,528.75 | 343.44 | -9,872.19 |
| 2021-04-13 | 1 (initial, expiry 2021-04-29) | 2021-04-13 | 14364.9 | 2021-04-20 | 5th_session_close | 14296.4 | 75 | -68.50 | -5,137.50 | 333.92 | -5,471.42 |
| 2021-12-21 | 1 (initial, expiry 2021-12-30) | 2021-12-21 | 16773.15 | 2021-12-27 | 5th_session_close | 17086.25 | 75 | 313.10 | 23,482.50 | 388.58 | 23,093.92 |
| 2022-01-25 | 1 (initial, expiry 2022-01-27) | 2022-01-25 | 16914.0 | 2022-01-27 | expiry_roll | 17128.65 | 75 | 214.65 | 16,098.75 | 389.76 | 15,708.99 |
| 2022-01-25 | 2 (roll_rebuy, expiry 2022-02-24) | 2022-01-28 | 17266.6 | 2022-02-01 | 5th_session_close | 17576.05 | 75 | 309.45 | 23,208.75 | 398.41 | 22,810.34 |
| 2022-02-15 | 1 (initial, expiry 2022-02-24) | 2022-02-15 | 16966.9 | 2022-02-21 | 5th_session_close | 17188.65 | 75 | 221.75 | 16,631.25 | 390.94 | 16,240.31 |
| 2022-03-08 | 1 (initial, expiry 2022-03-31) | 2022-03-08 | 15827.15 | 2022-03-14 | 5th_session_close | 16852.1 | 75 | 1024.95 | 76,871.25 | 381.56 | 76,489.69 |
| 2022-05-05 | 1 (initial, expiry 2022-05-26) | 2022-05-05 | 16834.95 | 2022-05-11 | 5th_session_close | 16161.4 | 75 | -673.55 | -50,516.25 | 373.28 | -50,889.53 |
| 2022-05-20 | 1 (initial, expiry 2022-05-26) | 2022-05-20 | 16059.9 | 2022-05-26 | 5th_session_close | 16176.2 | 75 | 116.30 | 8,722.50 | 370.99 | 8,351.51 |
| 2022-06-14 | 1 (initial, expiry 2022-06-30) | 2022-06-14 | 15741.75 | 2022-06-20 | 5th_session_close | 15365.2 | 75 | -376.55 | -28,241.25 | 356.35 | -28,597.60 |
| 2024-01-18 | 1 (initial, expiry 2024-01-25) | 2024-01-18 | 21414.1 | 2024-01-24 | 5th_session_close | 21466.15 | 75 | 52.05 | 3,903.75 | 477.21 | 3,426.54 |
| 2024-06-05 | 1 (initial, expiry 2024-06-27) | 2024-06-05 | 22094.6 | 2024-06-11 | 5th_session_close | 23249.8 | 75 | 1155.20 | 86,640.00 | 509.35 | 86,130.65 |
| 2024-08-06 | 1 (initial, expiry 2024-08-29) | 2024-08-06 | 24318.8 | 2024-08-12 | 5th_session_close | 24359.0 | 75 | 40.20 | 3,015.00 | 535.22 | 2,479.78 |
| 2024-10-04 | 1 (initial, expiry 2024-10-31) | 2024-10-04 | 25190.4 | 2024-10-10 | 5th_session_close | 24980.8 | 75 | -209.60 | -15,720.00 | 548.50 | -16,268.50 |
| 2025-04-08 | 1 (initial, expiry 2025-04-24) | 2025-04-08 | 22535.2 | 2025-04-16 | 5th_session_close | 23426.95 | 75 | 891.75 | 66,881.25 | 513.76 | 66,367.49 |
| 2026-03-16 | 1 (initial, expiry 2026-03-26) | 2026-03-16 | 23133.0 | 2026-03-20 | 5th_session_close | 23093.2 | 65 | -39.80 | -2,587.00 | 448.40 | -3,035.40 |
| 2026-04-01 | 1 (initial, expiry 2026-04-30) | 2026-04-01 | 22824.1 | 2026-04-08 | 5th_session_close | 23986.9 | 65 | 1162.80 | 75,582.00 | 460.51 | 75,121.49 |
| 2026-07-09 | 1 (initial, expiry 2026-07-30) | 2026-07-09 | 23965.05 | 2026-07-15 | 5th_session_close | 24074.2 | 65 | 109.15 | 7,094.75 | 465.01 | 6,629.74 |

### Trigger days that did NOT become entries (for audit)
Across the 1,818 days there are 51 days whose prior-day close fell >= 2% (the down day itself; entry would be the next trading day). Only 30 became entries. The rest were blocked by the code's own rules: an open position, the 10-day cooldown, or the `skip_yday` expiry quirk — most notably the March 2020 crash cluster (down days on 2020-03-06, -09, -12, -16, -17, -18, -19, -23 all blocked while positions/cooldowns from earlier entries were still running, so the system did NOT keep buying into the crash; its one March 2020 loss came from the 2020-03-11 entry, entered after the 2020-03-09 -4.90% close, which then fell a further -1,367.25 points over its 5 sessions). Full down-day list was checked against the entry list during the build; the simulation reproduces the code's state machine day by day rather than filtering triggers after the fact.

## 5. Honest comparison to the Volrix card figures

Card figures shown to the user: Return +15.6% since Jul 2019, Return/DD +0.30, Profit factor 2.00, Expectancy +0.39, Max DD 8.3%, Win rate 60.6%.

| Figure | Volrix card | This backtest (spot proxy) | Match? |
|---|---|---|---|
| Win rate | 60.6% | 66.7% (20/30) | Same ballpark, not identical. Note: 60.6% is exactly 20/33 — Volrix's engine may have produced 33 entries to our 30 (e.g. different skip/cool/expiry-calendar handling or a different daily data calendar adding 3 entries, with the same 20 wins). That is a hypothesis, not a verified explanation; their trade count is not shown on the card. |
| Profit factor | 2.00 | 2.30 gross / 2.24 net | Same ballpark, ours slightly higher. PF is the least sensitive figure to the futures-vs-spot difference, since both numerator and denominator scale similarly. |
| Expectancy | +0.39 (no unit on the card) | +160.91 points / +Rs 11,257.67 per position (net) | **Cannot be matched.** No unit is given for +0.39 (points? percent? ratio?). It is not forced into agreement here. For scale only: our average net win is Rs 30,535 and average net loss Rs 27,297, so expectancy is dominated by the win rate, not by a large per-trade edge. |
| Max drawdown | 8.3% | Rs 1,40,336.12 (1,860.70 points) | **Cannot be matched as a %.** A drawdown % needs a capital base, which the card does not disclose. Our Rs drawdown is reported in full so it can be converted once a capital base is known. |
| Return | +15.6% since Jul 2019 | Net +Rs 3,37,730.11 per 1 lot (lot schedule above); +4,827.45 points | **Cannot be matched as a % without a capital base.** For scale ONLY (illustrative, not Volrix's definition): on a hypothetical Rs 2,00,000 starting capital, +Rs 3,37,730 is +168.9% total, CAGR = (537730/200000)^(1/7.25) - 1 = +14.6% per year over Jul 2019–Oct 2026 (~7.25 years). If Volrix's +15.6% is a TOTAL return, ours is far above it on that illustrative base; if it is an ANNUALISED return, ours (14.6% illustrative CAGR) is close — but the capital base is invented here, so neither reading is a reproduction. |
| Return/DD | +0.30 | Capital-independent analogue: total net / max DD = 337730 / 140336 = 2.41 (gross: 349737 / ~140000 ≈ 2.5) | **Does NOT match, and the card is internally inconsistent on a simple reading:** 15.6 / 8.3 = 1.88, not 0.30. So their Return/DD is not return% / DD%. One hypothesis that lands near 0.30: if +15.6% is a total return, simple annualised return ≈ 15.6 / 7.25 = 2.15% per year, and 2.15 / 8.3 = 0.26 ≈ 0.30. That is a hypothesis only; their definition is not disclosed and is not reverse-engineered into a claim here. |

### Why the mismatch is expected, not a sign of an error in either direction

1. **Futures vs spot proxy.** Volrix trades monthly futures; this backtest trades spot. Futures basis, the premium on entry/exit days, and the 4 roll gaps (2020-02-27, 2020-09-24, 2021-02-25, 2022-01-27 expiries) all move futures P&L away from spot P&L, leg by leg.
2. **Entry/exit timing.** Volrix's engine buys at its 09:16 trigger evaluation price and squares off at 15:15; this backtest uses 09:16/15:15 1-min spot closes where available and daily open/close before 2022. The sensitivity run shows timing moves the total by ~Rs 28,000 (8%), not enough to explain a return-% gap, but enough to move individual trades.
3. **Expiry/skip/cool handling.** The code's skip quirk and 10-day cooldown are replicated exactly here, but Volrix's `get_expiry_date` may resolve monthly expiry on holiday-shifted dates differently from the last-Thursday calendar used here, which would change a small number of entries and rolls.
4. **Unknown Volrix definitions.** Return %, drawdown %, expectancy unit, and Return/DD definition are not disclosed on the card. Any backtest that claims to 'match' them exactly without those definitions would be forcing the match.
5. **Small sample.** 30 positions over 7+ years (and zero in 2023) means one trade — the 2020-03-11 loss of -Rs 1,02,775, 30% of the net total — swings every summary statistic. Volrix's figures rest on their own (undisclosed) trade count and will differ for this reason alone.

## 6. What this does and does not prove

- It proves the code, as written, is a **positive-expectancy, low-frequency rebound system on Nifty spot proxy data**: 20 wins / 30, PF ~2.2–2.3, net +Rs 3.38 lakh per 1 lot over Jul 2019–Oct 2026, with a single-trade worst loss larger than the average win and a drawdown driven by the March 2020 crash continuation.
- It does **not** prove the Volrix card figures, which cannot be reproduced without their capital base, futures prices, and metric definitions (see Section 5).
- It does **not** prove futures profitability: futures basis and roll costs are not in this proxy, and the 4 rolls are the places where futures and spot diverge most.
- It does **not** make this system adopted, and it does **not** change the (lA) / v4 verdicts. This is a separate system, reported separately, paper only, no orders, no live trading, no lot increase.
- Next validation, if this system is ever considered for use (not adopted here): reproduce it on **actual monthly futures prices** (contract-by-contract, with real roll prices) and on a frozen out-of-sample window, before any paper-trading decision. The forward-paper log spec for Cluster 2/3 does not cover this system; a separate log would be needed.

## 7. Files

- This report: `volrix_nifty_large_down_rebound_backtest.md`
- Daily spot data (Upstox): `nifty_daily_2019_2026.csv` (1,818 days)
- 1-min entry/exit prices (Upstox, 2022+): `intraday_1min_prices.json` (30 days)
- Simulation (daily state machine): `simulate.py`, positions at `positions_daily.json`
- P&L computation: `compute.py`, results at `results.json`
- Fetch scripts: `fetch_daily.py`, `fetch_1min.py`
