# EKAM-INTRADAY — BANK NIFTY · SPEC (frozen before scoring, 2026-11-14)

Programme: EKAM-INTRADAY v1 — standard indicators only, clubbed by
votes. Owner's correction 2026-11-14 20:53: EKAM means INTRADAY
indicators clubbed together (not the daily swing build). Research
only — no existing book, ledger or job is changed by this run.
Buying only, 1 lot (30), Rs220/trade, paper only.

Core identical across segments; this file is the Bank Nifty instance.
Data, expiry, premium resolution, VWAP basis and money conventions
are the DIAL-Bank house conventions (dial_bank_SPEC.md), copied
unchanged unless stated.

## 1. Data

- Spot: data/progressive/BANKNIFTY/spot_5m.csv, continuous 5-min
  series 2026-01-01 → 2026-11-13. Gate window Jan 1–Oct 31 = 203
  stored trading days (Oct 29–30 absent from the store, outside the
  basis). November CF days: Nov 2,3,4,5,6,9,11,12,13 (75 bars each).
- Expiry: in-force expiry from oi_history/banknifty_daily_oi.csv;
  November override 2026-11-23 (house convention). Strike step 100;
  strike = step nearest the SIGNAL bar's spot close, exact half
  rounds up. CE for long signals, PE for short signals.
- Premium resolution order (house): (a) round5_history
  C5_{expiry}_{strike}{type}.json; (b) daily2leg/prem_bank.json;
  (c) per-day candles_BANKNIFTY files in btst_data,
  november_shadow_data, nifty_weekly_expiry_chain, oi_buildup_data.
  Missing everywhere → NC (counted, never substituted).
- Session VWAP: the spot series carries no volume, so session VWAP =
  session VWAP of the in-force Bank Nifty FUTURES contract
  (round5_history/FUT7_{expiry}.json), cumulative typical-price x
  volume / volume; mapped to a spot bar as the futures VWAP at the
  latest futures bar at or before the spot bar's time (the DIAL
  day_vwap mapping). If undefined at a bar, the VWAP vote is 0 for
  both sides at that bar (bars counted as VWAP-unavailable).

## 2. Indicators (continuous 5-min spot series, causal; house code)

- EMA(p): k = 2/(p+1), seeded with SMA of first p closes at index
  p-1 (atlas ema_series). Used: EMA(9), EMA(21).
- Supertrend(7,3): Wilder ATR(7), standard final-band carry (DIAL /
  atlas supertrend). Direction "up"/"down" per bar.
- MACD(12,26,9): line = EMA12 - EMA26; signal = EMA(9) applied to
  the MACD line values with the same SMA seeding (atlas
  macd_series).
- RSI(14): Wilder (DIAL rsi_wilder).
- ADX(14): Wilder (atlas adx_wilder): +DM/-DM/TR Wilder-smoothed,
  DX from bar 14, ADX seeded at bar 27 with the SMA of DX[14..27],
  then Wilder-averaged.
An indicator that is still undefined (warmup) at a bar contributes
no vote for either side at that bar. Votes are additive; a bar can
reach the entry threshold with some indicators undefined.

## 3. Votes (per completed bar i)

Directional votes, each 0/1 per side:
1. VWAP: LONG +1 if close > session VWAP; SHORT +1 if close <
   VWAP; equal or VWAP undefined → neither.
2. EMA trend: LONG +1 if EMA9 > EMA21; SHORT +1 if EMA9 < EMA21;
   equal/undefined → neither.
3. Supertrend: LONG +1 if direction is up; SHORT +1 if down.
4. MACD: LONG +1 if MACD line > signal line; SHORT +1 if line <
   signal; equal/undefined → neither.
5. RSI: LONG +1 if 50 <= RSI < 70; SHORT +1 if 30 < RSI <= 50
   (literal inequalities; RSI exactly 50.0 would satisfy both — a
   measure-zero boundary, recorded as written); undefined →
   neither.
L_dir = LONG directional votes (0..5); S_dir = SHORT directional
votes (0..5).
6. ADX vote: if ADX(14) is defined and >= 20, add +1 to the side
   that LEADS on directional votes (L_dir > S_dir → LONG total
   L = L_dir + 1; S_dir > L_dir → S = S_dir + 1). If L_dir == S_dir
   (tie), ADX adds to neither. If ADX < 20 or undefined, no ADX
   vote. Final counts: L, S (each 0..6).

## 4. Entry

Per row (threshold T in {4, 5}): scan the day's bars in time order.
A bar is an eligible signal bar if its time <= 15:10 and it is not
the day's last bar. The FIRST eligible bar with L >= T (long) or
S >= T (short) is the day's signal; direction = the side reaching
T. (Both sides >= T at the same bar is arithmetically impossible
for T >= 4 because L + S <= 6; if it nevertheless occurred, the
higher count wins and an exact tie is no trade.) If the first
qualifying bar of the day is after 15:10 or is the day's last bar,
count one LATE signal for the row and take no trade. Entry = the
NEXT bar's open of the weekly nearest-strike contract (strike from
the signal bar's spot close). One trade per day per row, maximum.
Premium missing at entry, or a non-contiguous/missing bar in the
exit walk → NC, counted per row.

## 5. Exits

- X1 (fixed): identical to the DIAL exit walk. From the entry bar
  onward over the contract's stored bars in time order, contiguity
  required (every 5-min timestamp from entry through exit must be
  present, else NC). Per bar: stop (-50) checked before target
  (+90); fills AT the level. If no level is hit through the 15:20
  bar, exit at the 15:20 bar's close (the 15:20 bar is itself
  checked for level fills first). Missing 15:20 bar → NC. The entry
  bar itself can trigger an exit. Bars after 15:20 are ignored.
- X2 (vote-decay): walk the contract's stored bars from the entry
  bar in time order, contiguity required (else NC). Per bar t:
  (a) if the bar's low <= entry - 60 → exit at entry - 60
  (hard stop); (b) else if t == 15:20 → exit at the bar's close
  (square-off); (c) else if the position's own-direction final vote
  count at the spot bar with timestamp t is <= 2 → exit at the
  bar's close (vote decay). The entry bar itself is checked (its
  close follows the entry at its open, so the check is causal).
  Missing 15:20 bar → NC. Bars after 15:20 are ignored.

## 6. Rows (only these four)

T4-X1, T4-X2, T5-X1, T5-X2.

## 7. Money and reporting

- Net = (exit - entry) x 30 - Rs220. A win is net > 0.
- Windows: W1 = Jan–Jun 2026 (months 01–06), W2 = Jul–Oct 2026
  (months 07–10), FULL = Jan–Oct 2026. Per row per window: trades,
  net, WR, Rs/trade-day (trade-days = distinct days with a scored
  trade in the window; at most one trade/day, so = trades).
- November CF (descriptive): the four rows over Nov 2–13, same
  rules; report trades/net/WR per row.
- Vote-count distribution (gate window): for each gate day,
  M = max over all of the day's bars of max(L, S) using final
  counts; report the number of days with M = 0,1,2,3,4,5,6.
- Counts reported: signals, late signals, NC, VWAP-unavailable bars.

## 8. Placebo (best full-year row only)

Best row = highest FULL net; ties broken in row order T4-X1, T4-X2,
T5-X1, T5-X2. Random-entry placebo, DIAL design: 500 iterations,
RNG seed 20261114. For each real trade of the best row: same side;
a random gate day; entry bar drawn uniformly from that day's bars
with entry time in 09:20..15:15; strike = step nearest the close of
the bar before the drawn entry bar; identical exit rule (for X2,
the decay check uses the RANDOM day's own vote series and the
trade's side); identical cost. An NC draw is redrawn up to 50
times, then dropped (drops counted). Percentile = % of iteration
totals strictly below the real total.

## 9. Timing audit

All indicators are causal recursions or trailing windows and entry
is the bar AFTER the signal bar. In addition, the build recomputes
EMA9, EMA21, Supertrend direction, MACD line and signal, RSI and
ADX for every scored signal bar (all rows, gate + November) from
the series truncated at that bar and asserts equality with the
full-series values (ST exact; RSI tolerance 1e-9; EMA/MACD/ADX
tolerance 1e-6). Any mismatch aborts the run and is reported
instead of results.

Frozen 2026-11-14, before scoring. Build: ekam_intraday_bank_build.py.
Outputs: ekam_intraday_bank_2026-11-14.md +
ekam_intraday_bank_results.json.
