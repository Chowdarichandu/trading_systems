# EKAM-INTRADAY — NIFTY · SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1 — standard indicators only, clubbed by votes. Segment: Nifty
only. INTRADAY system on 5-min bars (this is NOT the daily EKAM swing book). Research
only: no existing book, ledger, or job is changed. Buying only, 1 lot (65), paper only,
real money Rs0. Cost Rs220/trade.

## DATA (identical stores/conventions to DIAL-Nifty)

- Spot: `data/progressive/NIFTY/spot_5m.csv` (OHLC, no volume; 2025-01-01 → 2026-11-13).
  All indicators computed on the CONTINUOUS 5-min series (no session reset), warmed up
  on the 2025 bars in the same store; signals evaluated only on the window in force.
- Session VWAP: spot carries no volume, so VWAP is from the near-month Nifty FUTURES
  5-min candles (`phase3_buildup_data/futures/FUT7_NIFTY_*`, 7-field): cumulative
  Σ(typical price × volume)/Σ(volume) within the session. The VWAP vote is
  basis-consistent, exactly as in the corrected DIAL-Nifty fill: the FUTURES close at
  the bar is compared with the futures session VWAP at the same bar. If a bar has no
  futures VWAP value, the VWAP vote is absent for that bar (neither side).
- Contracts: `oi_buildup_data/candles_NIFTY_{strike}{CE|PE}_{expiry}_{day}.json`
  (7-field). Strike = 50-grid strike nearest the SPOT CLOSE of the signal bar.
  Expiry = smallest expiry in the stored expiry calendar ≥ the signal day (weekly).
  A signal is SCORED only if that exact contract-day file exists AND its bars cover
  the entry bar through the 15:20 bar contiguously (5-min steps). Otherwise NC
  (counted per row, never substituted).

## INDICATORS (on spot, at each completed bar close)

1. VWAP vote: futures close > futures VWAP → LONG vote; < → SHORT vote; equal/absent → none.
2. EMA trend: EMA(9) vs EMA(21) on spot closes (k = 2/(p+1), seeded at series start,
   continuous). EMA9 > EMA21 → LONG; < → SHORT.
3. Supertrend(7,3): Wilder ATR(7) on spot, final-band ratchet exactly as in the
   DIAL-Nifty build. Bullish state (dir +1) → LONG; bearish (−1) → SHORT.
4. MACD(12,26,9): EMA12 − EMA26 on spot closes; signal = EMA(9) of the MACD line
   (seeded at the first MACD value). MACD > signal → LONG; < → SHORT.
5. RSI(14): Wilder on spot closes, continuous. 50 ≤ RSI < 70 → LONG; 30 < RSI < 50 →
   SHORT; otherwise none. (RSI exactly 50 counts LONG only — the long range's stated
   lower bound is inclusive; the short range is read as 30 < RSI < 50 so no bar can
   vote both sides.)
6. ADX(14): Wilder ADX on spot OHLC (TR/+DM/−DM Wilder-smoothed over 14; DX from the
   smoothed DIs; ADX = Wilder smoothing of DX, first value = mean of the first 14 DX
   values). If ADX ≥ 20 at the bar, +1 vote is added to the LEADING side — the side
   with the higher count from votes 1–5 at that bar. If votes 1–5 are tied, ADX adds
   to neither side. If ADX < 20 or not yet defined, no ADX vote.

Vote totals: LONG votes and SHORT votes are counted separately at every bar
(each of votes 1–5 gives at most one side a vote; ADX adds at most +1 to one side;
maximum per side = 6).

## ENTRY

- Evaluate bars of the day in order, signal-bar time ≤ 15:10 (entry bar must start
  ≤ 15:15). The FIRST bar of the day where LONG votes ≥ T (buy CE) or SHORT votes ≥ T
  (buy PE) is the signal bar. One trade per day maximum. (Both sides ≥ T on the same
  bar is arithmetically impossible here — votes 1–5 total ≤ 5 plus one ADX vote — so
  no tie-break is needed; if it somehow occurred, the day is no-trade.)
- Entry: next bar at the stored contract's OPEN (entry premium). Signal on a
  completed bar's close only — no intrabar signals.

## EXITS

- X1 (fixed): stop −50 premium points, target +90, scanned from the entry bar onward
  through the 15:15 bar, level fills (bar low ≤ stop → exit AT stop; else bar high ≥
  target → exit AT target; both in one bar → STOP first). If neither level is touched,
  square-off = OPEN of the 15:20 bar.
- X2 (vote-decay): hard stop −60 (same level-fill scan, stop level = entry − 60,
  checked on every bar from the entry bar onward, stop fills before any decay exit on
  the same bar). Decay: at the close of every bar from the entry bar through the 15:15
  bar, recompute the position's OWN-direction vote total (same 6-vote count, same
  definitions, data up to that bar's close; a bar whose spot votes are unavailable
  cannot trigger decay). If own votes ≤ 2, exit at the OPEN of the NEXT bar in the
  contract (decay on the 15:15 bar therefore exits at the 15:20 open). No target.
  If neither stop nor decay fires, square-off = OPEN of the 15:20 bar.

## ROWS (only these four)

T4-X1 · T4-X2 · T5-X1 · T5-X2 (T = vote threshold, X = exit rule).

## MONEY / METRICS

- Net per trade = (exit − entry) × 65 − Rs220. Win iff net > 0.
- Per row, per window: trades, net (Rs), WR %, Rs/trade-day (trade-day = a day with a
  scored trade in that row+window). Windows: Jan–Jun 2026 (trades dated < 2026-07-01),
  Jul–Oct 2026 (≥ 2026-07-01), full Jan–Oct 2026.
- Also per row: signals generated, NC count (by reason), days with no signal.
- Vote-count distribution: (a) the (LONG, SHORT) vote pair at every scored signal bar
  of the row; (b) the distribution of each day's maximum LONG votes and maximum SHORT
  votes across all trading days in Jan–Oct.
- Timing audit: for every scored trade in every row — entry bar timestamp = signal
  bar timestamp + 5 min AND entry premium = the stored open of the entry bar; plus an
  independent recomputation (separate code path) of RSI(14), EMA(9)/EMA(21), MACD and
  Supertrend direction at the first scored signal bar of the best full-year row,
  compared with the main path.
- Random-entry placebo on the BEST full-year row only: 1,000 iterations, seed
  20261114; each iteration rebuilds the book with the same scored-trade count, each
  trade drawn as a uniformly random scorable contract-day file from the Jan–Oct
  availability universe (files whose bars cover an entry through 15:20) with a
  uniformly random feasible entry bar in it and the file's own direction (CE/PE);
  exits = the best row's exit rule (for X2, vote-decay computed on the drawn contract
  day's spot votes for the drawn direction); same cost. Percentile = share of placebo
  totals ≤ the real full-year total.
- November CF (descriptive): the identical frozen system over 2026-11-02 → 2026-11-13
  (9 trading days), same stores and NC rules; per row: signals, NC, trades, net, WR.

## KNOWN COVERAGE CAVEAT (stated, not hidden)

The premium store was built for other books' leg days and band fetches, so EKAM
signals on other days are often NC. The scored book is the subset of signals whose
exact contracts were stored; NC counts are reported per row next to every total.
