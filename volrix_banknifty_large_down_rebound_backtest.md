# Volrix Large Down Rebound — BANK NIFTY version (separate system, paper only, no orders)

**Status: separate system only. NOT mixed into v4 / (lA) totals, NOT mixed into the Nifty rebound totals (futures/spot or options), NOT adopted.** Same logic as the Nifty test, applied to a different index. No improvement, no re-tuning.

## 1. Logic replicated (identical to the Nifty test)

- Entry at >=09:16 once/day: if `reopen`, buy monthly expiry 0 regardless of trigger/cool/skip. Else if not in position and `cool == 0`, and yesterday's Bank Nifty spot daily close / day-before close - 1 <= -0.02 (and `not skip_yday`), then `cool = 10`, `sess = 1`, buy monthly expiry 0, 1 lot FUT, **no stop loss, no target**.
- Exit at >=15:15: if `sess >= 5`, square off (entry day = sess 1, so exit = entry day + 4 trading days). Else if held monthly expiry <= today, square off and set `reopen = True` (re-buy next trading day; 5-session clock does NOT reset).
- Skip quirk: `skip_yday` = previous day's `skip_today`, where `skip_today = True` if the monthly-expiry-0 date changed versus the previous day. So an entry is skipped on the day after the first trading day following a monthly expiry.

## 2. Data actually used — and what was NOT available

- **Futures continuous history: NOT available through the Upstox helper** (same limitation as the Nifty test: search returns only live contracts). **The primary result therefore uses BANK NIFTY SPOT as a labelled proxy.** Futures basis and roll gaps are unquantifiable from spot alone and are NOT estimated.
- Spot daily closes: Upstox `NSE_INDEX|Nifty Bank`, 2019-07-01 to 2026-10-28, 1,818 trading days (same calendar count as the Nifty series).
- Spot intraday: Upstox 1-min bars return 0 bars for 2019–2021 (same pattern as Nifty) and full data from 2022-01-03 onward. So 2022+ legs use the close of the 09:16 1-min bar (entry) and the close of the 15:15 1-min bar (exit); pre-2022 legs use daily open (entry) / daily close (exit), labelled as an approximation in every row.
- Monthly expiry calendar: **last Thursday of each month, as in the Nifty test — NOT verified month-by-month against the actual Bank Nifty expiry calendar, and the options section below shows this calendar is wrong for 2024–2026** (actual Bank monthly expiries retrieved from Upstox include 2024-10-30 Wed, 2024-11-27 Wed, 2025-01-30 Thu, 2025-04-24 Thu, 2026-02-24 Tue, 2026-03-30 Mon, 2026-07-28 Tue). Impact: skip/roll timing in the primary test may shift by days in 2024–2026, most visibly the 2026-03-24 position (primary calendar rolls it on 2026-03-27; the actual monthly expiry is 2026-03-30). The primary points total is therefore indicative, not an exact futures reproduction. This limitation is stated, not hidden.
- Lot size (by held-contract expiry, from public NSE revision history + live Upstox contract confirming 30 for Nov 2026): expiry < Jul 2023: 25; Jul 2023–Jan 2025 expiries: 15; Feb 2025–Jul 2025 expiries: 30; Jul 2025–Dec 2025 expiries: 35; Jan 2026+ expiries: 30. Transition boundaries are approximate by expiry date; a leg or two near a boundary could carry a different lot in reality. **Points are therefore the lot-independent headline; rupee totals scale with the lot schedule above.**
- Charges (per leg, same current-rate approximation as the Nifty test): brokerage Rs 40 round trip + STT 0.02% of sell value + exchange 0.0019% of (entry + exit) value + SEBI Rs 10/crore of (entry + exit) value + stamp 0.002% of buy value + GST 18% on (brokerage + exchange + SEBI).

## 3. Headline results — primary (spot proxy, 1-min 2022+, daily open/close pre-2022)

| Metric | Value |
|---|---|
| Period (actual data used) | 2019-07-01 to 2026-10-28 (first entry 2019-07-09, last exit 2026-07-15) |
| Positions (1 lot each, continuous holding incl. rolls) | 48 |
| Legs (initial buys + roll re-buys) | 60 (48 initial + 12 roll re-buys) |
| Wins / losses (position net > 0) | 21 / 27 |
| Win rate | 43.75% |
| Total points (sum of leg exit - entry, spot proxy) | +2,705.25 |
| Gross profit (points x lot) | +Rs 78,795.50 |
| Charges | -Rs 16,058.35 |
| Net profit (1 lot throughout, lot schedule above) | +Rs 62,737.15 |
| Profit factor, gross | 1.17 (gross wins Rs 543,618.25 / gross losses Rs 464,822.75) |
| Profit factor, net of charges | 1.13 (net wins Rs 536,053.35 / net losses Rs 473,316.20) |
| Expectancy, net | +Rs 1,307.02 per position (56.36 points per position) |
| Average net win / average net loss | +Rs 25,526.35 / -Rs 17,530.23 |
| Largest win / largest loss (net, per position) | +Rs 75,838.52 (2025-04-08 entry) / -Rs 98,463.30 (2020-03-09 entry) |
| Max drawdown, net Rs (chronological peak-to-trough on cumulative position net) | Rs 130,109.34 (peak after trade 6, trough after trade 10) |
| Max drawdown, points (same peak/trough) | 5,168.05 points |
| Frequency | ~6.6 positions/year |

### By year (position net, 1 lot)
| Year | Positions | Wins | Net Rs |
|---|---|---|---|
| 2019 | 4 | 1 | +6,446.40 |
| 2020 | 17 | 8 | +17,436.90 |
| 2021 | 7 | 3 | +11,086.85 |
| 2022 | 6 | 1 | -94,924.23 |
| 2023 | 3 | 1 | +6,232.95 |
| 2024 | 5 | 3 | +41,208.35 |
| 2025 | 2 | 1 | +43,931.42 |
| 2026 | 4 | 3 | +31,318.51 |

### Sensitivity: uniform daily open/close basis for ALL legs
If entry = daily open and exit = daily close for every leg (ignoring intraday timing entirely): **48 positions, 20 wins, net +Rs 31,426.93** — Rs -31,310.22 versus the primary basis. The conclusion (barely positive total, sub-50% win rate) does not depend on the timing basis. Per-position sensitivity nets are in the last column of the trade table.

### Trigger days that did NOT become entries (for audit)
Across the 1,818 days there are **101 days whose prior-day close fell >= 2%** (the down day itself; entry would be the next trading day). Only **48 became entries**. The rest were blocked by the code's own rules: an open position, the 10-day cooldown, or the `skip_yday` expiry quirk. Unlike Nifty's March 2020 cluster, Bank Nifty did keep buying into March 2020 — its 2020-03-09 entry (after a -3.52% down day) lost -Rs 98,463.30, the largest loss in the test, and its 2020-03-24 entry (after a -16.73% down day) first leg gained +1,908.05 points to the 2020-03-26 roll, then the roll leg lost -2,019.20 points, for a small net loss.

## 4. Full trade list (positions; legs in the leg columns)
| # | Entry | Trigger down % | Leg entry -> exit (reason) | Entry price (basis) | Exit price (basis) | Lot | Leg points | Position net Rs | Sens. net Rs (daily basis) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 2019-07-09 | -2.77% | 2019-07-09 -> 2019-07-15 (5th_session_close) | 30533.4 (daily) | 30445.95 (daily) | 25 | -87.45 | -2,436.92 | -2,436.92 |
| 2 | 2019-08-14 | -2.47% | 2019-08-14 -> 2019-08-21 (5th_session_close) | 27885.5 (daily) | 27719.05 (daily) | 25 | -166.45 | -4,393.79 | -4,393.79 |
| 3 | 2019-09-04 | -2.20% | 2019-09-04 -> 2019-09-11 (5th_session_close) | 26785.95 (daily) | 27776.2 (daily) | 25 | +990.25 | +24,524.58 | +24,524.58 |
| 4 | 2019-10-01 | -2.59% | 2019-10-01 -> 2019-10-09 (5th_session_close) | 29226.15 (daily) | 28785.85 (daily) | 25 | -440.30 | -11,247.47 | -11,247.47 |
| 5 | 2020-01-07 | -2.59% | 2020-01-07 -> 2020-01-13 (5th_session_close) | 31598.05 (daily) | 32177.65 (daily) | 25 | +579.60 | +14,228.49 | +14,228.49 |
| 6 | 2020-02-03 | -3.28% | 2020-02-03 -> 2020-02-07 (5th_session_close) | 29811.75 (daily) | 31201.95 (daily) | 25 | +1,390.20 | +34,500.89 | +34,500.89 |
| 7 | 2020-03-09 | -3.52% | 2020-03-09 -> 2020-03-16 (5th_session_close) | 27031.45 (daily) | 23101.15 (daily) | 25 | -3,930.30 | -98,463.30 | -98,463.30 |
| 8 | 2020-03-24 | -16.73% | 2020-03-24 -> 2020-03-26 (expiry_roll)<br>2020-03-27 -> 2020-03-30 (5th_session_close) | 17705.85 (daily) | 18782.4 (daily) | 25, 25 | -111.15 | -3,129.76 | -3,129.76 |
| 9 | 2020-04-15 | -2.14% | 2020-04-15 -> 2020-04-21 (5th_session_close) | 20096.35 (daily) | 19409.35 (daily) | 25 | -687.00 | -17,352.60 | -17,352.60 |
| 10 | 2020-05-06 | -2.39% | 2020-05-06 -> 2020-05-12 (5th_session_close) | 19302.45 (daily) | 18862.85 (daily) | 25 | -439.60 | -11,163.68 | -11,163.68 |
| 11 | 2020-05-26 | -2.57% | 2020-05-26 -> 2020-05-28 (expiry_roll)<br>2020-05-29 -> 2020-06-01 (5th_session_close) | 17537.65 (daily) | 19959.9 (daily) | 25, 25 | +2,630.05 | +65,398.33 | +65,398.33 |
| 12 | 2020-06-10 | -2.18% | 2020-06-10 -> 2020-06-16 (5th_session_close) | 20760.95 (daily) | 20296.7 (daily) | 25 | -464.25 | -11,789.54 | -11,789.54 |
| 13 | 2020-06-25 | -3.76% | 2020-06-25 -> 2020-06-25 (expiry_roll)<br>2020-06-26 -> 2020-07-01 (5th_session_close) | 21218.05 (daily) | 21977.6 (daily) | 25, 25 | +530.65 | +12,881.96 | +12,881.96 |
| 14 | 2020-07-13 | -2.22% | 2020-07-13 -> 2020-07-17 (5th_session_close) | 22613.25 (daily) | 21966.8 (daily) | 25 | -646.45 | -16,355.89 | -16,355.89 |
| 15 | 2020-07-28 | -3.59% | 2020-07-28 -> 2020-07-30 (expiry_roll)<br>2020-07-31 -> 2020-08-03 (5th_session_close) | 21940.15 (daily) | 21072.1 (daily) | 25, 25 | -951.75 | -24,174.55 | -24,174.55 |
| 16 | 2020-08-17 | -2.33% | 2020-08-17 -> 2020-08-21 (5th_session_close) | 21906.95 (daily) | 22299.6 (daily) | 25 | +392.65 | +9,620.52 | +9,620.52 |
| 17 | 2020-09-01 | -3.14% | 2020-09-01 -> 2020-09-07 (5th_session_close) | 23893.8 (daily) | 22945.05 (daily) | 25 | -948.75 | -23,920.26 | -23,920.26 |
| 18 | 2020-09-22 | -3.02% | 2020-09-22 -> 2020-09-24 (expiry_roll)<br>2020-09-25 -> 2020-09-28 (5th_session_close) | 21445.25 (daily) | 21665.5 (daily) | 25, 25 | -63.70 | -1,968.35 | -1,968.35 |
| 19 | 2020-10-16 | -3.36% | 2020-10-16 -> 2020-10-22 (5th_session_close) | 23219.85 (daily) | 24484.15 (daily) | 25 | +1,264.30 | +31,398.12 | +31,398.12 |
| 20 | 2020-11-20 | -2.85% | 2020-11-20 -> 2020-11-26 (5th_session_close) | 28935.75 (daily) | 29549.75 (daily) | 25 | +614.00 | +15,106.08 | +15,106.08 |
| 21 | 2020-12-22 | -4.10% | 2020-12-22 -> 2020-12-29 (5th_session_close) | 29607.5 (daily) | 31322.5 (daily) | 25 | +1,715.00 | +42,620.44 | +42,620.44 |
| 22 | 2021-01-25 | -3.17% | 2021-01-25 -> 2021-01-28 (expiry_roll)<br>2021-01-29 -> 2021-02-01 (5th_session_close) | 31507.15 (daily) | 33089.05 (daily) | 25, 25 | +1,239.55 | +30,471.87 | +30,471.87 |
| 23 | 2021-02-22 | -2.04% | 2021-02-22 -> 2021-02-25 (expiry_roll)<br>2021-02-26 -> 2021-02-26 (5th_session_close) | 35874.3 (daily) | 34803.6 (daily) | 25, 25 | -328.35 | -8,780.14 | -8,780.14 |
| 24 | 2021-03-25 | -2.61% | 2021-03-25 -> 2021-03-25 (expiry_roll)<br>2021-03-26 -> 2021-04-01 (5th_session_close) | 33420.75 (daily) | 33858.0 (daily) | 25, 25 | -161.35 | -4,574.98 | -4,574.98 |
| 25 | 2021-04-13 | -5.10% | 2021-04-13 -> 2021-04-20 (5th_session_close) | 30901.8 (daily) | 31112.7 (daily) | 25 | +210.90 | +5,017.70 | +5,017.70 |
| 26 | 2021-10-29 | -3.34% | 2021-10-29 -> 2021-11-04 (5th_session_close) | 39424.55 (daily) | 39573.7 (daily) | 25 | +149.15 | +3,417.36 | +3,417.36 |
| 27 | 2021-11-23 | -2.23% | 2021-11-23 -> 2021-11-25 (expiry_roll)<br>2021-11-26 -> 2021-11-29 (5th_session_close) | 36787.0 (daily) | 35976.45 (daily) | 25, 25 | -276.70 | -7,502.12 | -7,502.12 |
| 28 | 2021-12-20 | -2.54% | 2021-12-20 -> 2021-12-24 (5th_session_close) | 35124.35 (daily) | 34857.05 (daily) | 25 | -267.30 | -6,962.84 | -6,962.84 |
| 29 | 2022-02-08 | -2.05% | 2022-02-08 -> 2022-02-14 (5th_session_close) | 38138.2 (1min) | 36923.7 (1min) | 25 | -1,214.50 | -30,657.67 | -31,983.88 |
| 30 | 2022-02-25 | -5.79% | 2022-02-25 -> 2022-03-04 (5th_session_close) | 36061.8 (1min) | 34379.55 (1min) | 25 | -1,682.25 | -42,334.94 | -37,626.17 |
| 31 | 2022-04-25 | -2.10% | 2022-04-25 -> 2022-04-28 (expiry_roll)<br>2022-04-29 -> 2022-04-29 (5th_session_close) | 35633.95 (1min) | 36088.9 (1min) | 25, 25 | +381.70 | +8,964.27 | +5,520.25 |
| 32 | 2022-05-13 | -3.35% | 2022-05-13 -> 2022-05-19 (5th_session_close) | 33918.55 (1min) | 33311.1 (1min) | 25 | -607.45 | -15,456.63 | -15,527.91 |
| 33 | 2022-06-14 | -3.13% | 2022-06-14 -> 2022-06-20 (5th_session_close) | 33228.4 (1min) | 32725.3 (1min) | 25 | -503.10 | -12,843.85 | -12,661.07 |
| 34 | 2022-09-26 | -2.67% | 2022-09-26 -> 2022-09-29 (expiry_roll)<br>2022-09-30 -> 2022-09-30 (5th_session_close) | 38917.7 (1min) | 38600.65 (1min) | 25, 25 | -79.65 | -2,595.41 | -10,808.14 |
| 35 | 2023-01-27 | -2.54% | 2023-01-27 -> 2023-02-02 (5th_session_close) | 41097.45 (1min) | 40619.2 (1min) | 25 | -478.25 | -12,275.31 | -18,145.90 |
| 36 | 2023-03-14 | -2.27% | 2023-03-14 -> 2023-03-20 (5th_session_close) | 39465.9 (1min) | 39389.65 (1min) | 25 | -76.25 | -2,216.66 | -4,321.56 |
| 37 | 2023-05-08 | -2.34% | 2023-05-08 -> 2023-05-12 (5th_session_close) | 42952.6 (1min) | 43795.15 (1min) | 25 | +842.55 | +20,724.92 | +24,578.85 |
| 38 | 2024-01-18 | -4.28% | 2024-01-18 -> 2024-01-24 (5th_session_close) | 45510.05 (1min) | 45140.75 (1min) | 15 | -369.30 | -5,767.87 | -6,383.41 |
| 39 | 2024-06-05 | -7.95% | 2024-06-05 -> 2024-06-11 (5th_session_close) | 47108.7 (1min) | 49678.65 (1min) | 15 | +2,569.95 | +38,304.62 | +33,042.28 |
| 40 | 2024-08-06 | -2.45% | 2024-08-06 -> 2024-08-12 (5th_session_close) | 50569.8 (1min) | 50591.7 (1min) | 15 | +21.90 | +78.54 | +1,865.93 |
| 41 | 2024-10-04 | -2.04% | 2024-10-04 -> 2024-10-10 (5th_session_close) | 51708.4 (1min) | 51501.0 (1min) | 15 | -207.40 | -3,364.75 | -1,946.56 |
| 42 | 2024-11-14 | -2.09% | 2024-11-14 -> 2024-11-22 (5th_session_close) | 50277.35 (1min) | 51091.3 (1min) | 15 | +813.95 | +11,957.81 | +15,977.81 |
| 43 | 2025-01-07 | -2.09% | 2025-01-07 -> 2025-01-13 (5th_session_close) | 50206.1 (1min) | 48095.05 (1min) | 15 | -2,111.05 | -31,907.10 | -30,540.32 |
| 44 | 2025-04-08 | -3.19% | 2025-04-08 -> 2025-04-16 (5th_session_close) | 50551.25 (1min) | 53094.85 (1min) | 30 | +2,543.60 | +75,838.52 | +81,406.58 |
| 45 | 2026-02-02 | -2.00% | 2026-02-02 -> 2026-02-06 (5th_session_close) | 58261.05 (1min) | 60132.45 (1min) | 30 | +1,871.40 | +55,615.23 | +55,910.83 |
| 46 | 2026-03-09 | -2.15% | 2026-03-09 -> 2026-03-13 (5th_session_close) | 55745.4 (1min) | 53772.1 (1min) | 30 | -1,973.30 | -59,679.82 | -71,387.71 |
| 47 | 2026-03-24 | -3.72% | 2026-03-24 -> 2026-03-27 (expiry_roll)<br>2026-03-30 -> 2026-04-01 (5th_session_close) | 52183.75 (1min) | 51428.2 (1min) | 30, 30 | +547.25 | +15,492.45 | -6,609.59 |
| 48 | 2026-07-09 | -2.51% | 2026-07-09 -> 2026-07-15 (5th_session_close) | 57085.0 (1min) | 57765.0 (1min) | 30 | +680.00 | +19,890.65 | +26,096.47 |

### Leg detail (every leg, for audit)
| Position entry | Leg | Entry date | Entry price | Exit date | Exit reason | Exit price | Lot | Points | Gross Rs | Charges Rs | Net Rs |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2019-07-09 | 1 (initial, expiry 2019-07-25) | 2019-07-09 | 30533.4 | 2019-07-15 | 5th_session_close | 30445.95 | 25 | -87.45 | -2,186.25 | 250.67 | -2,436.92 |
| 2019-08-14 | 1 (initial, expiry 2019-08-29) | 2019-08-14 | 27885.5 | 2019-08-21 | 5th_session_close | 27719.05 | 25 | -166.45 | -4,161.25 | 232.54 | -4,393.79 |
| 2019-09-04 | 1 (initial, expiry 2019-09-26) | 2019-09-04 | 26785.95 | 2019-09-11 | 5th_session_close | 27776.2 | 25 | +990.25 | +24,756.25 | 231.67 | +24,524.58 |
| 2019-10-01 | 1 (initial, expiry 2019-10-31) | 2019-10-01 | 29226.15 | 2019-10-09 | 5th_session_close | 28785.85 | 25 | -440.30 | -11,007.50 | 239.97 | -11,247.47 |
| 2020-01-07 | 1 (initial, expiry 2020-01-30) | 2020-01-07 | 31598.05 | 2020-01-13 | 5th_session_close | 32177.65 | 25 | +579.60 | +14,490.00 | 261.51 | +14,228.49 |
| 2020-02-03 | 1 (initial, expiry 2020-02-27) | 2020-02-03 | 29811.75 | 2020-02-07 | 5th_session_close | 31201.95 | 25 | +1,390.20 | +34,755.00 | 254.11 | +34,500.89 |
| 2020-03-09 | 1 (initial, expiry 2020-03-26) | 2020-03-09 | 27031.45 | 2020-03-16 | 5th_session_close | 23101.15 | 25 | -3,930.30 | -98,257.50 | 205.80 | -98,463.30 |
| 2020-03-24 | 1 (initial, expiry 2020-03-26) | 2020-03-24 | 17705.85 | 2020-03-26 | expiry_roll | 19613.9 | 25 | +1,908.05 | +47,701.25 | 176.14 | +47,525.11 |
| 2020-03-24 | 2 (roll_rebuy, expiry 2020-04-30) | 2020-03-27 | 20801.6 | 2020-03-30 | 5th_session_close | 18782.4 | 25 | -2,019.20 | -50,480.00 | 174.87 | -50,654.87 |
| 2020-04-15 | 1 (initial, expiry 2020-04-30) | 2020-04-15 | 20096.35 | 2020-04-21 | 5th_session_close | 19409.35 | 25 | -687.00 | -17,175.00 | 177.60 | -17,352.60 |
| 2020-05-06 | 1 (initial, expiry 2020-05-28) | 2020-05-06 | 19302.45 | 2020-05-12 | 5th_session_close | 18862.85 | 25 | -439.60 | -10,990.00 | 173.68 | -11,163.68 |
| 2020-05-26 | 1 (initial, expiry 2020-05-28) | 2020-05-26 | 17537.65 | 2020-05-28 | expiry_roll | 19169.8 | 25 | +1,632.15 | +40,803.75 | 173.48 | +40,630.27 |
| 2020-05-26 | 2 (roll_rebuy, expiry 2020-06-25) | 2020-05-29 | 18962.0 | 2020-06-01 | 5th_session_close | 19959.9 | 25 | +997.90 | +24,947.50 | 179.44 | +24,768.06 |
| 2020-06-10 | 1 (initial, expiry 2020-06-25) | 2020-06-10 | 20760.95 | 2020-06-16 | 5th_session_close | 20296.7 | 25 | -464.25 | -11,606.25 | 183.29 | -11,789.54 |
| 2020-06-25 | 1 (initial, expiry 2020-06-25) | 2020-06-25 | 21218.05 | 2020-06-25 | expiry_roll | 21506.15 | 25 | +288.10 | +7,202.50 | 190.55 | +7,011.95 |
| 2020-06-25 | 2 (roll_rebuy, expiry 2020-07-30) | 2020-06-26 | 21735.05 | 2020-07-01 | 5th_session_close | 21977.6 | 25 | +242.55 | +6,063.75 | 193.75 | +5,870.00 |
| 2020-07-13 | 1 (initial, expiry 2020-07-30) | 2020-07-13 | 22613.25 | 2020-07-17 | 5th_session_close | 21966.8 | 25 | -646.45 | -16,161.25 | 194.64 | -16,355.89 |
| 2020-07-28 | 1 (initial, expiry 2020-07-30) | 2020-07-28 | 21940.15 | 2020-07-30 | expiry_roll | 21646.85 | 25 | -293.30 | -7,332.50 | 192.12 | -7,524.62 |
| 2020-07-28 | 2 (roll_rebuy, expiry 2020-08-27) | 2020-07-31 | 21730.55 | 2020-08-03 | 5th_session_close | 21072.1 | 25 | -658.45 | -16,461.25 | 188.68 | -16,649.93 |
| 2020-08-17 | 1 (initial, expiry 2020-08-27) | 2020-08-17 | 21906.95 | 2020-08-21 | 5th_session_close | 22299.6 | 25 | +392.65 | +9,816.25 | 195.73 | +9,620.52 |
| 2020-09-01 | 1 (initial, expiry 2020-09-24) | 2020-09-01 | 23893.8 | 2020-09-07 | 5th_session_close | 22945.05 | 25 | -948.75 | -23,718.75 | 201.51 | -23,920.26 |
| 2020-09-22 | 1 (initial, expiry 2020-09-24) | 2020-09-22 | 21445.25 | 2020-09-24 | expiry_roll | 20456.85 | 25 | -988.40 | -24,710.00 | 184.93 | -24,894.93 |
| 2020-09-22 | 2 (roll_rebuy, expiry 2020-10-29) | 2020-09-25 | 20740.8 | 2020-09-28 | 5th_session_close | 21665.5 | 25 | +924.70 | +23,117.50 | 190.92 | +22,926.58 |
| 2020-10-16 | 1 (initial, expiry 2020-10-29) | 2020-10-16 | 23219.85 | 2020-10-22 | 5th_session_close | 24484.15 | 25 | +1,264.30 | +31,607.50 | 209.38 | +31,398.12 |
| 2020-11-20 | 1 (initial, expiry 2020-11-26) | 2020-11-20 | 28935.75 | 2020-11-26 | 5th_session_close | 29549.75 | 25 | +614.00 | +15,350.00 | 243.92 | +15,106.08 |
| 2020-12-22 | 1 (initial, expiry 2020-12-31) | 2020-12-22 | 29607.5 | 2020-12-29 | 5th_session_close | 31322.5 | 25 | +1,715.00 | +42,875.00 | 254.56 | +42,620.44 |
| 2021-01-25 | 1 (initial, expiry 2021-01-28) | 2021-01-25 | 31507.15 | 2021-01-28 | expiry_roll | 30358.3 | 25 | -1,148.85 | -28,721.25 | 251.25 | -28,972.50 |
| 2021-01-25 | 2 (roll_rebuy, expiry 2021-02-25) | 2021-01-29 | 30700.65 | 2021-02-01 | 5th_session_close | 33089.05 | 25 | +2,388.40 | +59,710.00 | 265.63 | +59,444.37 |
| 2021-02-22 | 1 (initial, expiry 2021-02-25) | 2021-02-22 | 35874.3 | 2021-02-25 | expiry_roll | 36549.0 | 25 | +674.70 | +16,867.50 | 290.61 | +16,576.89 |
| 2021-02-22 | 2 (roll_rebuy, expiry 2021-03-25) | 2021-02-26 | 35806.65 | 2021-02-26 | 5th_session_close | 34803.6 | 25 | -1,003.05 | -25,076.25 | 280.78 | -25,357.03 |
| 2021-03-25 | 1 (initial, expiry 2021-03-25) | 2021-03-25 | 33420.75 | 2021-03-25 | expiry_roll | 33006.45 | 25 | -414.30 | -10,357.50 | 268.13 | -10,625.63 |
| 2021-03-25 | 2 (roll_rebuy, expiry 2021-04-29) | 2021-03-26 | 33605.05 | 2021-04-01 | 5th_session_close | 33858.0 | 25 | +252.95 | +6,323.75 | 273.10 | +6,050.65 |
| 2021-04-13 | 1 (initial, expiry 2021-04-29) | 2021-04-13 | 30901.8 | 2021-04-20 | 5th_session_close | 31112.7 | 25 | +210.90 | +5,272.50 | 254.80 | +5,017.70 |
| 2021-10-29 | 1 (initial, expiry 2021-11-25) | 2021-10-29 | 39424.55 | 2021-11-04 | 5th_session_close | 39573.7 | 25 | +149.15 | +3,728.75 | 311.39 | +3,417.36 |
| 2021-11-23 | 1 (initial, expiry 2021-11-25) | 2021-11-23 | 36787.0 | 2021-11-25 | expiry_roll | 37364.75 | 25 | +577.75 | +14,443.75 | 296.17 | +14,147.58 |
| 2021-11-23 | 2 (roll_rebuy, expiry 2021-12-30) | 2021-11-26 | 36830.9 | 2021-11-29 | 5th_session_close | 35976.45 | 25 | -854.45 | -21,361.25 | 288.45 | -21,649.70 |
| 2021-12-20 | 1 (initial, expiry 2021-12-30) | 2021-12-20 | 35124.35 | 2021-12-24 | 5th_session_close | 34857.05 | 25 | -267.30 | -6,682.50 | 280.34 | -6,962.84 |
| 2022-02-08 | 1 (initial, expiry 2022-02-24) | 2022-02-08 | 38138.2 | 2022-02-14 | 5th_session_close | 36923.7 | 25 | -1,214.50 | -30,362.50 | 295.17 | -30,657.67 |
| 2022-02-25 | 1 (initial, expiry 2022-03-31) | 2022-02-25 | 36061.8 | 2022-03-04 | 5th_session_close | 34379.55 | 25 | -1,682.25 | -42,056.25 | 278.69 | -42,334.94 |
| 2022-04-25 | 1 (initial, expiry 2022-04-28) | 2022-04-25 | 35633.95 | 2022-04-28 | expiry_roll | 36402.4 | 25 | +768.45 | +19,211.25 | 289.53 | +18,921.72 |
| 2022-04-25 | 2 (roll_rebuy, expiry 2022-05-26) | 2022-04-29 | 36475.65 | 2022-04-29 | 5th_session_close | 36088.9 | 25 | -386.75 | -9,668.75 | 288.70 | -9,957.45 |
| 2022-05-13 | 1 (initial, expiry 2022-05-26) | 2022-05-13 | 33918.55 | 2022-05-19 | 5th_session_close | 33311.1 | 25 | -607.45 | -15,186.25 | 270.38 | -15,456.63 |
| 2022-06-14 | 1 (initial, expiry 2022-06-30) | 2022-06-14 | 33228.4 | 2022-06-20 | 5th_session_close | 32725.3 | 25 | -503.10 | -12,577.50 | 266.35 | -12,843.85 |
| 2022-09-26 | 1 (initial, expiry 2022-09-29) | 2022-09-26 | 38917.7 | 2022-09-29 | expiry_roll | 37698.45 | 25 | -1,219.25 | -30,481.25 | 300.35 | -30,781.60 |
| 2022-09-26 | 2 (roll_rebuy, expiry 2022-10-27) | 2022-09-30 | 37461.05 | 2022-09-30 | 5th_session_close | 38600.65 | 25 | +1,139.60 | +28,490.00 | 303.81 | +28,186.19 |
| 2023-01-27 | 1 (initial, expiry 2023-02-23) | 2023-01-27 | 41097.45 | 2023-02-02 | 5th_session_close | 40619.2 | 25 | -478.25 | -11,956.25 | 319.06 | -12,275.31 |
| 2023-03-14 | 1 (initial, expiry 2023-03-30) | 2023-03-14 | 39465.9 | 2023-03-20 | 5th_session_close | 39389.65 | 25 | -76.25 | -1,906.25 | 310.41 | -2,216.66 |
| 2023-05-08 | 1 (initial, expiry 2023-05-25) | 2023-05-08 | 42952.6 | 2023-05-12 | 5th_session_close | 43795.15 | 25 | +842.55 | +21,063.75 | 338.83 | +20,724.92 |
| 2024-01-18 | 1 (initial, expiry 2024-01-25) | 2024-01-18 | 45510.05 | 2024-01-24 | 5th_session_close | 45140.75 | 15 | -369.30 | -5,539.50 | 228.37 | -5,767.87 |
| 2024-06-05 | 1 (initial, expiry 2024-06-27) | 2024-06-05 | 47108.7 | 2024-06-11 | 5th_session_close | 49678.65 | 15 | +2,569.95 | +38,549.25 | 244.63 | +38,304.62 |
| 2024-08-06 | 1 (initial, expiry 2024-08-29) | 2024-08-06 | 50569.8 | 2024-08-12 | 5th_session_close | 50591.7 | 15 | +21.90 | +328.50 | 249.96 | +78.54 |
| 2024-10-04 | 1 (initial, expiry 2024-10-31) | 2024-10-04 | 51708.4 | 2024-10-10 | 5th_session_close | 51501.0 | 15 | -207.40 | -3,111.00 | 253.75 | -3,364.75 |
| 2024-11-14 | 1 (initial, expiry 2024-11-28) | 2024-11-14 | 50277.35 | 2024-11-22 | 5th_session_close | 51091.3 | 15 | +813.95 | +12,209.25 | 251.44 | +11,957.81 |
| 2025-01-07 | 1 (initial, expiry 2025-01-30) | 2025-01-07 | 50206.1 | 2025-01-13 | 5th_session_close | 48095.05 | 15 | -2,111.05 | -31,665.75 | 241.35 | -31,907.10 |
| 2025-04-08 | 1 (initial, expiry 2025-04-24) | 2025-04-08 | 50551.25 | 2025-04-16 | 5th_session_close | 53094.85 | 30 | +2,543.60 | +76,308.00 | 469.48 | +75,838.52 |
| 2026-02-02 | 1 (initial, expiry 2026-02-26) | 2026-02-02 | 58261.05 | 2026-02-06 | 5th_session_close | 60132.45 | 30 | +1,871.40 | +56,142.00 | 526.77 | +55,615.23 |
| 2026-03-09 | 1 (initial, expiry 2026-03-26) | 2026-03-09 | 55745.4 | 2026-03-13 | 5th_session_close | 53772.1 | 30 | -1,973.30 | -59,199.00 | 480.82 | -59,679.82 |
| 2026-03-24 | 1 (initial, expiry 2026-03-26) | 2026-03-24 | 52183.75 | 2026-03-27 | expiry_roll | 52285.35 | 30 | +101.60 | +3,048.00 | 466.19 | +2,581.81 |
| 2026-03-24 | 2 (roll_rebuy, expiry 2026-04-30) | 2026-03-30 | 50982.55 | 2026-04-01 | 5th_session_close | 51428.2 | 30 | +445.65 | +13,369.50 | 458.87 | +12,910.63 |
| 2026-07-09 | 1 (initial, expiry 2026-07-30) | 2026-07-09 | 57085.0 | 2026-07-15 | 5th_session_close | 57765.0 | 30 | +680.00 | +20,400.00 | 509.35 | +19,890.65 |

## 5. Honest comparison — Bank Nifty vs Nifty, same logic, same method, spot proxy
| Figure | Nifty rebound (spot proxy) | Bank Nifty rebound (spot proxy) |
|---|---|---|
| Positions | 30 | 48 |
| Win rate | 66.7% (20/30) | 43.75% (21/48) |
| Total points | +4,827.45 | +2,705.25 |
| Net (1 lot, own lot schedule) | +Rs 3,37,730.11 | +Rs 62,737.15 |
| Profit factor, net | 2.24 | 1.13 |
| Expectancy, net per position | +Rs 11,257.67 | +Rs 1,307.02 |
| Max drawdown | Rs 1,40,336.12 | Rs 130,109.34 |

**Reading:** the same logic does NOT transfer to Bank Nifty. Bank Nifty triggers far more often (48 positions vs 30; 101 down days vs 51) because Bank Nifty is more volatile day-to-day, but wins less than half its trades (43.75% vs 66.7%) and its profit factor collapses from 2.24 to 1.13. The total is barely positive (+Rs 62,737 on 48 trades, expectancy +Rs 1,307 per position) and the max drawdown (Rs 1,30,109) is more than twice the net profit — a drawdown-to-profit profile the Nifty version does not have (Nifty DD Rs 1,40,336 vs net Rs 3,37,730). The two big Bank Nifty years that keep the total positive are 2025 (+Rs 43,931 on 2 trades, dominated by the Apr 2025 rebound) and 2024 (+Rs 41,208 on 5 trades); 2022 alone is -Rs 94,924 on 6 trades (only 1 win). No return % or return/DD is claimed against the Volrix card here: the card is a Nifty card, its capital base and definitions are undisclosed, and a Bank Nifty % would need a separate base.

## 6. SECONDARY TEST — Bank Nifty OPTIONS translation (clearly separated, provisional, NOT the pasted code)

**Translation (frozen before premiums were observed, same as the Nifty options test):** LONG ATM Bank Nifty CALL, monthly expiry 0, 1 lot, no stop, no target. Same trigger/cooldown/skip (entry dates reused from the primary test). Strike = nearest 100-point strike to the previous trading day's spot close (Bank Nifty strike step is 100, not Nifty's 50). Entry premium = close of the 09:16 1-min bar on entry day; exit premium = close of the 15:15 1-min bar on the 5th session. Expiry inside a hold = exit at expiry with no roll (defined before results). Costs on premium turnover only (brokerage Rs 40 round trip, STT 0.0625% of sell premium value, exchange 0.03503% of (buy + sell) premium value, SEBI Rs 10/crore, stamp 0.003% of buy premium value, GST 18% on brokerage + exchange + SEBI). No Black-Scholes backfill anywhere.

**Data reality:** Upstox's expired-instruments expiries list for Bank Nifty runs 2024-10-01 to 2026-10-27 (31 expiries). Result: **only 8 of 48 entries are testable (2024-10-04 to 2026-07-15)** — and those 8 are exactly the 8 primary positions dated Oct 2024 or later, so there are no post-Oct-2024 dropouts; **40 dropouts are all pre-Oct-2024 entries** (2019–Sep 2024), listed in `options_trades.json` with reasons. A first-pass run of this options script that still pointed at the Nifty files (strikes like 25300 CE) was caught and discarded; the numbers below are from the corrected Bank Nifty run only.

| Entry | Strike / monthly expiry | Entry -> exit premium | Spot move (entry 09:16 -> exit 15:15, primary basis) | Net Rs | Spot-proxy position net Rs (same entry date) |
|---|---|---|---|---|---|
| 2024-10-04 | 51800 CE / 2024-10-30, lot 15 | 1050.0 -> 676.4 | -207.40 | -5,668.75 | -3,364.75 |
| 2024-11-14 | 50100 CE / 2024-11-27, lot 15 | 837.6 -> 1063.5 | +813.95 | +3,319.13 | +11,957.81 |
| 2025-01-07 | 49900 CE / 2025-01-30, lot 15 | 1177.5 -> 231.15 | -2,111.05 | -14,253.91 | -31,907.10 |
| 2025-04-08 | 49900 CE / 2025-04-24, lot 30 | 1453.7 -> 3168.0 | +2,543.60 | +51,263.62 | +75,838.52 |
| 2026-02-02 | 58400 CE / 2026-02-24, lot 30 | 1020.4 -> 1981.0 | +1,871.40 | +28,695.41 | +55,615.23 |
| 2026-03-09 | 57800 CE / 2026-03-30, lot 30 | 659.9 -> 105.7 | -1,973.30 | -16,685.30 | -59,679.82 |
| 2026-03-24 | 51400 CE / 2026-03-30, lot 30 | 1460.6 -> 0.15 (expiry exit) | -1,900.05 (to expiry 2026-03-30; -755.55 to 2026-04-01, the spot-proxy exit, is NOT the call's holding period) | -43,880.18 | +15,492.45 |
| 2026-07-09 | 56700 CE / 2026-07-28, lot 30 | 1192.85 -> 1422.65 | +680.00 | +6,786.53 | +19,890.65 |

**Options totals: 8 trades, 4 wins (50.0%), gross +Rs 10,290.75, charges Rs 714.20, net +Rs 9,576.55, profit factor (net) 1.12, expectancy +Rs 1,197.07 per trade, max drawdown (chronological, from a 0 start) Rs 60,565.48.**
**Comparison on the same 8 entries:** spot-proxy positions net +Rs 83,842.99 (5/8 wins) vs options net +Rs 9,576.55 (4/8 wins) — options keep only 11% of the spot-proxy net, a shortfall of Rs 74,266.44.
- **Flagged, not hidden — the 2026-03-24 trade is not a like-for-like comparison:** the call exited at its monthly expiry on 2026-03-30 for 0.15 (net -Rs 43,880.18) under the no-roll rule, while the spot-proxy position rolled on its (last-Thursday) calendar and exited 2026-04-01 for +Rs 15,492.45. That single holding-period difference accounts for Rs 59,372.63 of the options-vs-spot gap. Excluding that one trade, options net would be +Rs 53,456.73 vs spot-proxy +Rs 68,350.54 on the remaining 7 entries — still behind, but by Rs 14,893.81, not Rs 74,266.44.
- **Spot rose but the call lost:** no clean case on the 8 traded entries once the Mar 2026 expiry case is separated — there the spot-proxy position is positive (+Rs 15,492.45) despite spot falling overall, because it re-bought at 50,982.55 on 2026-03-30 and gained +445.65 points to 2026-04-01, while the call had already expired worthless (0.15) on 2026-03-30. On the other 7, call sign follows spot sign in every case; the loss is in magnitude — calls capture only part of rebounds (e.g. Apr 2025: spot +2,543.60 points, call premium +1,714.30 points x lot 30 = +Rs 51,429 gross vs spot-proxy +Rs 75,838.52 net) and lose more than spot on falls in premium terms where IV/decay bites (e.g. Jan 2025: spot -2,111.05, call -946.35 premium points x lot 15 = -Rs 14,195.25 gross, smaller in rupees only because the lot is 15).
- **Verdict on options:** INCONCLUSIVE overall (n=8, no pre-Oct-2024 history), and BEHIND spot-proxy on the testable window even after the Mar 2026 expiry adjustment. It is not a rescue for the weak primary result: the primary Bank Nifty result is already barely positive, and options do not improve it on the available data.

## 7. What this does and does not prove

- It proves the code, as written, is a **barely-positive, low-win-rate rebound system on Bank Nifty spot proxy data**: 21 wins / 48, PF ~1.1–1.2, net +Rs 62,737 per 1 lot over Jul 2019–Oct 2026, with a max drawdown more than twice the net profit. It does NOT transfer Nifty's edge (PF 2.24, 66.7% wins) to Bank Nifty.
- It does NOT prove futures profitability: futures basis, roll gaps, and the actual (non-last-Thursday) monthly expiry calendar in 2024–2026 are not in this proxy, and the primary roll/skip timing may be off by days in that period.
- It does NOT make this system adopted, and it does NOT change the (lA) / v4 verdicts. Separate system, reported separately, paper only, no orders, no live trading, no lot increase.
- Next validation, if this system were ever considered for use (not adopted here): reproduce it on **actual monthly futures prices** (contract-by-contract, with real roll prices and the real expiry calendar) and on a frozen out-of-sample window, before any paper-trading decision. The Cluster 2/3 forward-paper log spec does not cover this system; a separate log would be needed.

## 8. Files

- This report: `volrix_banknifty_large_down_rebound_backtest.md`
- Daily spot data (Upstox): `banknifty_daily_2019_2026.csv` (1,818 days)
- 1-min entry/exit prices (Upstox, 2022+): `intraday_1min_prices.json` (44 days)
- Simulation: `simulate.py`, positions at `positions_daily.json`; P&L: `compute.py`, results at `results.json`; fetch: `fetch_daily.py`, `fetch_1min.py`
- Options: `volrix_banknifty_options/fetch_and_compute.py`, `options_trades.json` (8 traded, 40 dropouts), `expiries.json`, per-contract 1-min candle files