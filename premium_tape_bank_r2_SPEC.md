# PREMIUM-TAPE — BANK NIFTY · ROUND 2: THE RETEST TURN · SPEC · FROZEN BEFORE SCORING · 2026-11-14

Round-1 diagnosis: P1-X2 was the only positive full-year line
(+Rs1,791.00), but it window-flipped (Jan–Jun +Rs33,046.00 /
Jul–Oct −Rs31,255.00) and lost every November trade
(−Rs18,180.00, WR 0%). The suspect is the chase entry at the break.
**The turn: enter on the RETEST of the break, not the break.**

Research only. Nothing running is changed. Option BUYING only,
1 lot (30), Rs220/trade, paper only, real money Rs0.

## Data, contract selection, indicators — IDENTICAL to Round 1

- `premium_tape_bank_SPEC.md` governs unchanged: same spot store
  (09:15 strike selection only), same in-force expiry map with the
  November 2026-11-23 override, same CE and PE of the strike nearest
  spot at 09:15 (100-step, exact half rounds up), same premium-store
  priority, same completeness test (all bars labelled 09:15..15:20;
  a missing side is NC, counted, never substituted), same premium
  VWAP (volume-weighted typical price where volume is carried; the
  equal-weighted proxy only on a no-volume source), and same premium
  opening-range high (bars labelled 09:15..09:45, 7 bars).
- Round 1 had CE NC 0 days, PE NC 0 days in the gate and in November;
  any change from 0 is reported, not hidden.
- Premium momentum and premium RSI are NOT used in Round 2.

## CONTROL (must reproduce before the turn is scored)

- The Round-1 P1-X2 book, rebuilt with the identical Round-1
  machinery: **174 trades, full Jan–Oct net +Rs1,791.00**
  (Jan–Jun 110 trades / +Rs33,046.00; Jul–Oct 64 trades /
  −Rs31,255.00). If the control does not reproduce exactly, the run
  stops and reports the mismatch — the turn is not scored.

## THE TURN — RULE P-RET (one rule, both contracts, symmetric)

Per scoreable contract-day:

1. **BREAK EVENT** (no entry): the first bar i labelled in
   09:50..14:20 whose premium close > premium opening-range high AND
   close > premium VWAP at bar i. Only the FIRST break event per
   contract-day is tracked. (The 09:50 start is the Round-1 P1
   eligibility, because the Bank opening range includes the 09:45
   bar; the 14:20 cap leaves a watch bar before the 14:30 expiry.)
2. **WATCH**: bars j = i+1 .. min(i+12, the 14:25 bar) — twelve
   5-minute watch bars is the 60-minute limit, and no retest may
   complete after the 14:25 bar (entry by 14:30). For each watch
   bar j, in order:
   - **RETEST HOLD**: low[j] <= VWAP[j] AND close[j] > VWAP[j] →
     the retest held. This contract's retest completes at bar j.
   - **FAIL**: close[j] <= VWAP[j] (without the hold condition) →
     the event expires, reason `close_below_vwap`.
   - Otherwise the watch continues. If the watch window ends with
     no hold, the event expires, reason `window_end`.
3. **DAY TRADE**: the earliest completed retest across the two
   contracts. Same-bar tie: larger touch depth (VWAP[j] − low[j])
   first; then CE before PE. One trade per day. Entry = open of
   bar j+1 (the 14:30 bar at the latest).

## Exits (carried from Round 1, premium points)

Walk from the entry bar through the 15:20 bar in time order. The
entry bar itself can trigger an exit (Round-1 house convention).

- X1: stop −50 checked before target +90 on each bar (fills AT the
  level); if neither is hit through the 15:20 bar, exit at the
  15:20 close (the 15:20 bar is itself checked for level fills first).
- X2: hard stop −60 checked first on each bar (fill AT entry−60);
  then, if the bar's close is below premium VWAP at that bar, exit
  at that bar's close; if neither happens through 15:20, exit at
  the 15:20 close.
- Net per trade = (exit − entry) × 30 − Rs220. Win = net > 0.
  Rs/trade-day = total / distinct trade days.

## Reporting

- Gate: the 203 stored days 2026-01-01..2026-10-31; windows
  Jan–Jun (<= 2026-06-30), Jul–Oct (>= 2026-07-01), full Jan–Oct.
  Per exit (X1 / X2): trades, net, WR, Rs/trade-day per window.
- **Selectivity**: break events (contract-days with a tracked event)
  vs completed retests (contract-days whose event held), with expiry
  reasons (`close_below_vwap` / `window_end`) counted — gate and
  November separately.
- NC counts (gate + November), identical accounting to Round 1.
- November CF (descriptive): Nov 2,3,4,5,6,9,11,12,13.
- Timing audit: every completed retest (traded or not) re-checked —
  premium opening-range high and premium VWAP recomputed from the
  contract-day series truncated at the event / retest bar by an
  independent code path; the event and hold conditions re-asserted;
  and for every scored trade, entry bar = retest bar + 5 min and
  entry premium = the stored open of that bar.
- Random-entry placebo on the best exit row (by full-year total):
  1,000 draws × the row's trade count; RNG seed 20261114; each trade
  = a uniform random scoreable gate day, a uniform random scoreable
  side of that day, a uniform random entry bar 09:20..15:15, the
  row's own exit rule; percentile = % of draw totals strictly below
  the real total (the Round-1 Bank convention).

No parameter is tuned after scoring begins; P-RET with X1/X2 is the
whole test.

Frozen 2026-11-14, before scoring. Build: premium_tape_bank_r2_build.py.
Outputs: premium_tape_bank_r2_2026-11-14.md +
premium_tape_bank_r2_results.json (+ premium_tape_bank_r2_trades.csv).
