# PREMIUM-TAPE — NIFTY · ROUND 2: THE RETEST TURN · SPEC · FROZEN BEFORE SCORING · 2026-11-14

Round-1 diagnosis: chasing the premium's own range break bled all year (P1-X1 -Rs75,995.75 · P2-X2 -Rs59,299.85 · COMB-X2 -Rs109,818.95, best row at the 34.6th percentile of random). The break itself is the chase. **The turn: enter on the RETEST of the break, not the break.**

Research only. Nothing running is changed. Option BUYING only, 1 lot (65), Rs220/trade, paper only, real money Rs0.

## Data, contract selection, indicators — IDENTICAL to Round 1
- `premium_tape_nifty_SPEC.md` governs unchanged: same premium store (`oi_buildup_data/candles_NIFTY_*.json`, 7-field candles), same frozen strike (round of the 09:15 spot close / 50 x 50), same weekly expiry rule, same availability test (bars 09:15..15:20 contiguous; missing = `nc_no_file`, incomplete = `nc_partial`, counted per day-side, never substituted), same premium VWAP (volume-weighted, typical price), same premium opening range (09:15..09:40 bars). Premium RSI / momentum are NOT used in Round 2.
- Bar grid: 75 bars, starts 09:15..15:25.

## CONTROL (must reproduce before the turn is scored)
- The Round-1 P1-X1 book, rebuilt with the identical machinery: **168 trades, full Jan-Oct net -Rs75,995.75**. If the control does not reproduce exactly, the run stops and reports the mismatch — the turn is not scored.

## THE TURN — RULE P-RET (one rule, both contracts, symmetric)
Per available contract-day:
1. **BREAK EVENT** (no entry): the first bar i with start time in 09:45..14:20 whose premium close > premium OR high AND close > premium VWAP at bar i. Only the FIRST break event per contract-day is tracked. (The 14:20 cap leaves at least two watch bars before the 14:30 expiry below.)
2. **WATCH**: bars j = i+1 .. min(i+12, the 14:25 bar) — i.e. the event dies 60 minutes after the event bar's start, and no retest may complete after 14:25 (entry by 14:30). For each watch bar j, in order:
   - **RETEST HOLD**: low[j] <= VWAP[j] AND close[j] > VWAP[j] → the retest held. This contract's retest completes at bar j.
   - **FAIL**: close[j] <= VWAP[j] (without the hold condition) → the event expires, reason `close_below_vwap`.
   - Otherwise the watch continues. If the watch window ends with no hold, the event expires, reason `window_end`.
3. **DAY TRADE**: the earliest completed retest across the two contracts. Same-bar tie: larger touch depth (VWAP[j] − low[j]) first; then CE before PE. One trade per day. Entry = open of bar j+1 (must be <= 15:15).

## Exits (carried from Round 1, premium points)
- X1: stop -50 / target +90; within a bar the stop is checked first; no trigger → exit at the open of the 15:20 bar.
- X2: hard stop -60 scanned intrabar (precedence within the bar); otherwise exit at the CLOSE of the first bar (entry..15:15) whose close is below that bar's premium VWAP; if none, exit at the open of the 15:20 bar.
- Net per trade = (exit − entry) x 65 − Rs220. Win = net > 0. Rs/trade-day = total / distinct trade days.

## Reporting
- Gate: spot days 2026-01-01..2026-10-31; windows Jan-Jun (<= 2026-06-30), Jul-Oct (>= 2026-07-01), full Jan-Oct. Per exit (X1 / X2): trades, net, WR, Rs/trade-day per window.
- **Selectivity**: break events (contract-days with a tracked event) vs completed retests (contract-days whose event held), with expiry reasons (`close_below_vwap` / `window_end`) counted.
- NC counts (gate + November), identical accounting to Round 1.
- November CF (descriptive): spot days 2026-11-02..2026-11-13.
- Timing audit: every scored trade re-checked (entry bar = retest bar + 5 min; entry = stored open); premium VWAP recomputed from truncated series by an independent code path at sampled retest bars.
- Random-entry placebo on the best exit row (by full-year total): 1000 draws × the row's trade count; each trade = a random gate day-side (uniform over available day-sides), a random entry bar 09:20..15:15, the row's own exit rule; percentile = share of draws <= the real total.

No parameter is tuned after scoring begins; P-RET with X1/X2 is the whole test.
