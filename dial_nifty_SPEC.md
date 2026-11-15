# DIAL — NIFTY · SPEC (frozen 2026-11-14, before scoring)

Programme: DIAL (registry `dial_programme.md`). Segment: Nifty only. STANDALONE — this
system generates its own signals from spot candles; it does not condition or filter
TUNED v1 or any other book. Research only: no existing book, ledger, or job is changed.
Buying only, 1 lot (65), paper only, real money ₹0.

## CORE SPEC (verbatim from the owner's re-scope, 2026-11-14 15:37 — not altered)

- Data: Nifty 5-min spot candles Jan-Oct 2026 from the persisted stores (the Jan-Oct spot stores from the gated runs); signal on a COMPLETED bar's close; entry at the NEXT bar. Instrument: buy the weekly-expiry strike nearest spot at entry, CE for up-signals, PE for down-signals; entry premium = open of the entry bar from stored premium candles; missing contract candles = NC (counted, never substituted).
- DIAL-T (trend): Supertrend(7,3) flip at a bar close AND spot on the same side of session VWAP -> signal in the flip direction. First qualifying signal of the day only.
- DIAL-R (reversion): RSI(14) <= 30 AND Bollinger %B <= 0.05 AND EMA50 slope (6 bars) > -0.1% -> LONG; mirror RSI >= 70 AND %B >= 0.95 AND slope < +0.1% -> SHORT. First qualifying signal of the day only.
- Exits: stop -50 premium points, target +90, square-off 15:20. Cost Rs220/trade. One T and one R trade may share a day; report components separately AND combined as the DIAL-Nifty book.
- GATE (same run, frozen): timing audit; random-entry placebo (same count/geometry, beat 95th pct); +30-min shift placebo (must also beat); halves; month table; ex-top-3.
- PASS BAR (combined): placebos met AND halves positive AND ex-top-3 positive AND Rs/trade-day >= 900 AND WR >= 60% AND monthly pace >= Rs7,500 AND no more than 2 red months. Name failing legs.
- NOVEMBER CF (descriptive): frozen system over Nov 2-13 stored candles — signals and net.

## DATA / FILL DETAILS (recorded by the builder; the core above is untouched)

- Spot: `data/progressive/NIFTY/spot_5m.csv` (OHLC, no volume; 2025-01-01 → 2026-11-13).
  Indicators are computed on the CONTINUOUS 5-min series (no session reset), warmed up on
  the 2025 bars in the same store; signals are evaluated only on the window in force.
- Session VWAP: the spot store carries no volume, so session VWAP is computed from the
  near-month Nifty FUTURES 5-min candles (`phase3_buildup_data/futures/FUT7_NIFTY_*`,
  7-field candles with volume): cumulative Σ(typical price × volume)/Σ(volume) within the
  session, typical price = (H+L+C)/3. Contract in force for a day = nearest monthly
  expiry ≥ that day.
  CORRECTION (2026-11-14, found by this run's own direction-split audit before the
  gate was finalised; the CORE above is untouched): the first fill compared the SPOT
  close directly with the FUTURES-price VWAP. Futures trade at a basis above spot, so
  that comparison is not like-for-like — measured over Jan–Oct, the spot close sits
  above the futures VWAP on only 22.5% of bars, while a futures close sits above its
  own VWAP on 49.0%. The first fill therefore starved DIAL-T of CE signals (79 PE vs
  17 CE scored) for a purely mechanical reason. Corrected fill: the VWAP-side test is
  basis-consistent — the futures close at the signal bar is compared with the futures
  session VWAP at the same bar (algebraically identical to comparing the spot close
  with the basis-adjusted VWAP). The Supertrend flip itself remains on spot candles,
  per the core. The gate was re-run in full under the corrected fill; the report
  discloses the first fill's headline result alongside the final one.
- Supertrend(7,3): Wilder ATR(7) on spot; basic bands (H+L)/2 ± 3×ATR with the standard
  final-band ratchet; direction from close vs final bands. A flip = direction change vs
  the previous bar, detected at the flip bar's close. DIAL-T qualifying signal = first
  flip of the day whose VWAP side also agrees.
- RSI(14): Wilder smoothing on spot closes, continuous. Bollinger: 20-bar SMA ± 2σ
  (σ = sample stdev, ddof=1); %B = (close − lower)/(upper − lower); if upper == lower,
  %B := 0.5 (no extreme). EMA50: k = 2/51, seeded at series start; slope = % change of
  EMA50 over the last 6 bars. DIAL-R qualifying signal = first bar close of the day
  satisfying the full LONG or SHORT condition set.
- Entry timing: signal bar = the bar whose close qualifies; entry bar = the next bar.
  A signal is actionable only if the entry bar starts ≤ 15:15 (the position must be
  able to square off at 15:20). Strike = the 50-grid strike nearest the SPOT CLOSE of
  the signal bar. Weekly expiry = the smallest expiry in the stored expiry calendar
  ≥ the signal day (weekly expiries, Tuesdays with holiday-shifted Mondays; the
  last-Tuesday monthly coincides). CE for up/LONG, PE for down/SHORT.
- Premium candles: `oi_buildup_data/candles_NIFTY_{strike}{CE|PE}_{expiry}_{day}.json`
  (7-field). A signal is SCORED only if that exact contract-day file exists AND its bars
  cover the entry bar through the 15:20 bar contiguously (5-min steps). Otherwise the
  signal is NC (counted per component, never substituted with a neighbour strike or
  another expiry). Entry premium = open of the entry bar.
- Exits: scan the contract's bars from the entry bar onward (entry bar included).
  Stop level = entry − 50, target = entry + 90, level fills: a bar whose low ≤ stop
  exits AT the stop level; else a bar whose high ≥ target exits AT the target level;
  if both levels fall inside one bar, the STOP fills first (conservative). If neither
  level is touched by the 15:20 bar, square-off = OPEN of the 15:20 bar.
- Money: net per trade = (exit − entry) × 65 − ₹220. A trade is a win iff net > 0.
  Trade-day = a day with ≥ 1 scored combined trade. ₹/trade-day = combined total /
  combined trade-days. Monthly pace = combined Jan–Oct total / 10. Halves: H1 = trades
  dated before 2026-06-01, H2 = on/after. Ex-top-3 = combined total − the 3 largest
  trade nets.
- T and R are independent: one T and one R trade may share a day; if both pick the
  same contract and entry bar they still count as two component trades. Combined book
  = T trades + R trades.
- Placebos (combined book): (i) RANDOM-ENTRY — 1,000 iterations; each rebuilds the book
  with the same per-component scored-trade counts, each trade drawn as a uniformly
  random scorable contract-day file (from the Jan–Oct availability universe of files
  whose bars cover an entry through 15:20) with a uniformly random feasible entry bar
  in it; same exits and cost. Percentile = share of placebo totals ≤ the real total;
  the bar needs percentile ≥ 0.95. (ii) +30-MIN SHIFT — every scored real entry moved
  6 bars later the same day, same contract and direction; trades whose shifted entry
  bar does not exist or starts after 15:15 are dropped (counted); the real combined
  total must exceed the shifted book's total.
- Timing audit: for every scored trade, assert entry bar timestamp = signal bar
  timestamp + 5 min and entry premium = that bar's open in the stored file; plus an
  independent recomputation (separate code path) of RSI(14), EMA50 and the Supertrend
  direction at the first scored signal bar of each component, compared to the main
  path's values.
- November CF: the identical frozen system over 2026-11-02 → 2026-11-13 (9 trading
  days), same stores and NC rules; descriptive only, not gated.
- Known coverage caveat (stated, not hidden): the premium store was built for other
  books' leg days and band fetches, so DIAL signals on other days are often NC. The
  scored book is therefore the subset of signals whose exact contracts were stored;
  NC counts are reported per component next to every total.
