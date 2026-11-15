# PREMIUM-TAPE — BANK NIFTY · SPEC (frozen before scoring, 2026-11-14)

Programme: SOMETHING DIFFERENT (owner's call 2026-11-14 20:57) — signals
off the OPTION PREMIUM's own chart, not off spot indicators. This is a
different data source from the spot-level families measured dead in
early November; no spot ORB / PD-level rule is re-run here. Research
only — no existing book, ledger or job is changed. Buying only,
1 lot (30), Rs220/trade, paper only.

## Data and contract selection (frozen)

- Spot: data/progressive/BANKNIFTY/spot_5m.csv (house store). Gate
  window = the 203 stored trading days 2026-01-01 → 2026-10-31;
  November CF = Nov 2,3,4,5,6,9,11,12,13 in the same series.
- Expiry: the in-force expiry from oi_history/banknifty_daily_oi.csv
  (date -> expiry), the same map the DIAL/stack scorers use; November
  override 2026-11-23 (house convention).
- Each day, TWO contracts are selected: the CE and the PE of the
  strike nearest spot at 09:15 — strike = 100-step nearest the 09:15
  bar's spot CLOSE, an exact half rounds up (floor(x/100 + 0.5) * 100).
  The selection is fixed for the whole day; spot is used ONLY for
  this 09:15 selection and for nothing else.
- Premium candles: 5-min bars of the selected contracts from the
  house stores, first source that carries the contract-day wins:
  (a) round5_history/C5_{expiry}_{strike}{type}.json (rows carry
  volume); (b) per-day files candles_BANKNIFTY_{strike}{type}_
  {expiry}_{day}.json in btst_data, november_shadow_data,
  nifty_weekly_expiry_chain, oi_buildup_data (rows carry volume);
  (c) daily2leg/prem_bank.json (OHLC only, no volume).
- A side (one contract on one day) is SCOREABLE only if its series
  carries every bar labelled 09:15..15:20 (74 bars, 5-min steps).
  Otherwise that side is NC for the day — counted, never substituted,
  never estimated. Bars after 15:20 are ignored.

## Premium indicators (per contract-day, trailing only)

All indicators are computed WITHIN the contract-day, from that
contract's own premium bars, using bars up to and including the
signal bar only.
- Premium VWAP at bar i: cumulative through bar i. If the day's
  source carries volume (sources a/b) and cumulative volume > 0:
  sum(typical price x volume) / sum(volume), typical price =
  (H + L + C) / 3. If the source carries no volume (source c) or
  cumulative volume is 0: the equal-weighted cumulative mean of the
  typical price (DISCLOSED per day in the results as vwap_mode).
- Premium opening range: high / low of the bars labelled
  09:15, 09:20, 09:25, 09:30, 09:35, 09:40, 09:45 (7 bars).
- Premium momentum at bar i: close[i] - close[i-3].
- Premium RSI(14): Wilder RSI on the contract-day's premium closes;
  first value at the 15th close; a cross up through 50 at bar i
  means RSI[i-1] <= 50 and RSI[i] > 50.

## Signals (completed bars; first trigger only)

- RULE P1 (premium range break): the first bar labelled >= 09:50
  whose CLOSE is above the premium opening-range HIGH while the
  premium close is also above premium VWAP at that bar -> buy THAT
  contract. Each contract breaks only its own range upward: a PE is
  bought on the PE contract's own break, never on a CE fall.
- RULE P2 (premium momentum): the first bar where the contract's
  premium close is above premium VWAP AND its 3-bar premium momentum
  is positive AND premium RSI(14) crosses up through 50 -> buy that
  contract.
- Books: P1 alone, P2 alone, and COMBINED (the first trigger across
  both contracts and both rules). Each book takes at most ONE trade
  per day. Within a book, triggers are ordered by (signal time,
  rule priority P1 before P2, side CE before PE) and the first wins.
- A signal is tradeable only if its bar is labelled <= 15:10 (so the
  entry bar is <= 15:15); a later first trigger is counted LATE,
  never a trade. Entry = the NEXT bar's stored open of the same
  contract.

## Exits (premium points, native to the contract)

Walk from the entry bar through the 15:20 bar in time order. The
entry bar itself can trigger an exit (house convention).
- X1: stop -50 checked before target +90 on each bar (fills AT the
  level); if neither is hit through the 15:20 bar, exit at the
  15:20 close (the 15:20 bar is itself checked for level fills
  first).
- X2 (premium-VWAP loss): hard stop -60 checked first on each bar
  (fill AT entry-60); then, if the bar's close is below premium
  VWAP at that bar, exit at that bar's close; if neither happens
  through 15:20, exit at the 15:20 close.

## Money, windows, reporting (frozen)

- Net = (exit - entry) x 30 - Rs220. A win is net > 0.
- Windows: Jan-Jun 2026, Jul-Oct 2026, full Jan-Oct 2026; November
  CF (Nov 2-13) descriptive. Per rule (P1 / P2 / combined) per exit
  (X1 / X2): trades, net, WR, Rs/trade-day (trade-day = a day with
  >= 1 scored trade in that book). Month detail in the JSON.
- NC counts reported: side-NC days per side (CE / PE), days with
  both sides NC, LATE first triggers per book, and any triggered
  but unscored trades per book (expected 0 under the completeness
  rule — reported, not hidden).
- TIMING AUDIT: for every trigger used by any book, premium VWAP,
  opening range, momentum and RSI are recomputed from the
  contract-day series TRUNCATED at the signal bar and asserted
  equal to the full-series values; entry must be exactly the bar
  after the signal bar. Any mismatch aborts the run and is reported
  instead of results.
- PLACEBO: on the best full-year book (highest Jan-Oct total among
  the six rule x exit books; ties broken in the order P1-X1, P1-X2,
  P2-X1, P2-X2, COMB-X1, COMB-X2): 500 iterations, RNG seed
  20261114. Each iteration replays the book's trade count: for each
  trade, draw a uniform random scoreable gate day, a uniform random
  scoreable side of that day, and a uniform random entry bar with
  entry time in 09:20..15:15; enter at that bar's open of the drawn
  contract and apply the book's exit rule. An NC draw is redrawn up
  to 50 times, then dropped (drops counted). Percentile = % of
  iteration totals strictly below the real total.

Frozen 2026-11-14, before scoring. Build: premium_tape_bank_build.py.
Outputs: premium_tape_bank_2026-11-14.md + premium_tape_bank_results.json.
