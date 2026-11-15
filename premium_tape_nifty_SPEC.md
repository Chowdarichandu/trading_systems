# PREMIUM-TAPE — NIFTY · SPEC · FROZEN BEFORE SCORING · 2026-11-14

Owner's call (2026-11-14 20:57): try something different — every prior family signals off indicators on the SPOT chart. This test signals off the OPTION PREMIUM's own chart: the traded instrument's own tape. Spot ORB / prior-day-level rules are NOT re-run (measured dead in early November); spot is used ONLY for the frozen strike selection below.

Research only. Nothing running is changed. Option BUYING only, 1 lot (65), Rs220/trade, paper only, real money Rs0.

## Data
- Premium candles: `oi_buildup_data/candles_NIFTY_{strike}{CE|PE}_{expiry}_{day}.json` (7-field candles: OHLC + volume + OI). Volume is present in the store, so premium VWAP is genuinely volume-weighted (fallback frozen below anyway).
- Spot: `data/progressive/NIFTY/spot_5m.csv` — used ONLY to pick the day's strike.
- Bar grid: 75 bars, start times 09:15..15:25 (5-min).

## Frozen contract selection (per day)
- Strike = round(spot close of the 09:15 bar / 50) x 50.
- Expiry = smallest expiry in the store's filename calendar that is >= the day.
- The day's two contracts: that strike's CE and PE at that expiry.
- A side is AVAILABLE only if its file exists AND its bars cover every bar-start 09:15..15:20 contiguously. Missing file = NC `nc_no_file`; present but incomplete = NC `nc_partial`. Counted per day-side, never substituted.

## Frozen premium indicators (trailing only, within the day, per contract)
- Premium VWAP at bar t: cumulative sum(typical price x volume) / sum(volume) over bars 09:15..t; typical price = (H+L+C)/3. If a contract-day's total volume is 0, VWAP = equal-weighted cumulative mean of typical price (proxy), and the day-side is flagged `vwap_proxy`.
- Premium opening range (OR): premium high / low over bars 09:15..09:40 (6 bars, i.e. 09:15-09:45 clock time).
- Premium RSI(14): Wilder, computed within the day's premium closes only; seed = SMA of the first 14 close-to-close changes; valid from bar index 14.
- 3-bar premium momentum at t: close[t] - close[t-3].

## Signal rules (evaluated per available contract, on completed bars 09:45..15:10)
- P1 (premium range break): first bar with close > OR high AND close > premium VWAP at that bar -> buy THAT contract. (A PE trade comes only from the PE contract's own break — never from a CE fall.)
- P2 (premium momentum): first bar with close > premium VWAP AND 3-bar momentum > 0 AND premium RSI crosses up through 50 (RSI[t-1] <= 50 < RSI[t]) -> buy that contract.
- Books: P1 alone, P2 alone, and COMBINED (first trigger among P1/P2). One trade per day per book.
- Within a book, the day's trade is the earliest trigger across the two contracts. Same-bar ties: P1 before P2 (combined book); then the larger break/momentum size relative to the contract's own scale; then CE before PE.
- Entry: open of the bar after the signal bar (entry bar <= 15:15).

## Exits (premium points)
- X1: stop -50 / target +90. Scan bars entry..15:15; within a bar the stop is checked first (low <= stop -> exit at the stop level; else high >= target -> exit at the target level). No trigger -> exit at the open of the 15:20 bar.
- X2: hard stop -60 scanned intrabar (low <= entry-60 -> exit at entry-60, precedence within the bar); otherwise exit at the CLOSE of the first bar (entry..15:15) whose close is below that bar's premium VWAP; if none, exit at the open of the 15:20 bar.
- Net per trade = (exit - entry) x 65 - Rs220. Win = net > 0. Rs/trade-day = total / distinct trade days.

## Windows and reporting
- Gate: spot days 2026-01-01..2026-10-31. Windows: Jan-Jun (<= 2026-06-30), Jul-Oct (>= 2026-07-01), full Jan-Oct.
- November CF (descriptive): spot days 2026-11-02..2026-11-13.
- Per rule (P1 / P2 / COMBINED) per exit (X1 / X2): trades, net, WR, Rs/trade-day per window; NC counts; November CF.
- Timing audit: every scored trade re-checked (entry bar = signal bar + 5 min; entry = stored open); premium VWAP and RSI recomputed from truncated series by an independent code path at sampled signal bars and compared.
- Random-entry placebo on the best full-year book (by total): 1000 draws; each draw takes the book's trade count, each trade = a random gate day (uniform over days with >= 1 available side), a random available side that day, a random entry bar 09:20..15:15, the book's own exit rule; percentile = share of draws <= the real total.

No parameter is tuned after scoring begins; the four rule/exit combinations above are the whole test.
