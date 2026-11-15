# NIFTY LONG HOLDS — SPEC (FROZEN 2026-11-15, before any scoring)

Owner's order 2026-11-15: "buy today and hold for two months in Nifty, seeing the
projection for the long months." Research only; nothing armed. OPTION BUYING ONLY.
Nifty, 1 lot (65) per position.

## 1. Trend rule (the "projection")
- Source: daily Nifty spot, `volrix/nifty_daily_2019_2026.csv` (2019-07-01 onward).
- Signal day = the LAST trading day of each month (per that store).
- State at the signal-day close:
  - UP: close > 50-DMA AND 50-DMA > 200-DMA.
  - DOWN: close < 50-DMA AND 50-DMA < 200-DMA.
  - FLAT: anything else — no trade.
- 200-DMA fallback (only binds in the annex's early months, never in the premium
  window): if fewer than 200 bars precede the signal day, UP = close > 50-DMA AND
  50-DMA above its own value 20 trading days earlier; DOWN = mirror; else FLAT.

## 2. Execution (premium window)
- Entry day = first trading day of the month after the signal month.
- Contract = that month's MONTHLY expiry, side CE if UP / PE if DOWN, strike =
  nearest 50 to the signal-day spot close.
- Entry premium = OPEN of the contract's first 5-minute bar on the entry day
  (Upstox expired-instruments route, browser User-Agent; 429 = hard stop, NC).
- HOLD-1M: exit at the CLOSE of the contract's last 5-minute bar on expiry day.
- HOLD-2M: at the first expiry's close, recompute the trend with that day's spot
  close. FLAT → position ends there (one round trip). Otherwise roll: buy the
  NEXT monthly expiry's ATM contract on the SAME side (strike = nearest 50 to
  the first-expiry-day spot close) at the NEXT trading day's open; exit at the
  second expiry's close (last 5-minute bar).
- Positions are independent, 1 lot each; HOLD-2M positions may overlap the next
  month's fresh position. No intra-hold stops of any kind.
- Monthly expiry dates: 2026 taken from the stored Bank key files (shared NSE
  monthly calendar); 2025 by the NSE rule (last Thursday Jan–Aug, last Tuesday
  Sep–Dec), each verified against the expired-instruments contract list, stepping
  back a day at a time if a date returns no contracts (holiday shift).

## 3. Money basis (labelled)
- Net per contract round trip = (exit − entry) × 65 − Rs220.
- HOLD-1M position = 1 round trip (Rs220). HOLD-2M full roll = 2 round trips
  (Rs440); HOLD-2M stopped at a FLAT roll = 1 round trip (Rs220).
- WORST CASE per position = the full premium paid + costs. A bought monthly
  option held to expiry can expire worthless; there is no stop. Stated plainly
  wherever results are reported.

## 4. Scoring window and NC rules
- Signals Dec 2024 onward; a position is scored only when its exit day's premium
  exists in fetched data (the last monthly expiry already expired at build time
  is 2026-10-27; later exits are NC — not estimated, not carried).
- A position whose contract/day data cannot be fetched is NC and counted, never
  substituted. The achieved premium window is stated in the report.
- Reporting per hold (1M / 2M) per calendar year (by ENTRY year): positions,
  net, WR (net > 0 share), best / worst position, worst drawdown of the
  cumulative-net line ordered by exit date, and calendar halves (entries
  Jan–Jun vs Jul–Dec).

## 4B. Bank Nifty arm (extension ordered 2026-11-15 10:45, before any scoring)
Identical rules, second index. Differences only:
- Spot: `volrix_banknifty/banknifty_daily_2019_2026.csv` (2019-07-01 onward).
- Lot 30. Net per contract round trip = (exit − entry) × 30 − Rs220.
- Strike step 100 (ATM = nearest 100 to the reference close).
- Expired-instruments index key `NSE_INDEX|Nifty Bank`.
- Monthly expiries: 2026 from the stored key files (2026-01-27 … 2026-11-23);
  2025 by the same NSE rule (last Thursday Jan–Aug, last Tuesday Sep–Dec),
  each verified against the contract list with day step-back on holidays.
- The annex (§5) is computed for Bank Nifty spot as well.
- Both indices are reported side by side, never pooled.

## 5. Annex — the long-months projection evidence (signal study, NOT option money)
- Every signal month Aug 2019 → the last month with forward bars in the store.
- For non-FLAT signals: direction-signed forward spot return at +20 / +40 / +60
  trading days (for a DOWN signal the sign is flipped — it "wins" when spot
  falls). Per horizon: events, average signed return %, win share (signed > 0).
- Labelled a spot signal study wherever quoted; no premium, no costs.
