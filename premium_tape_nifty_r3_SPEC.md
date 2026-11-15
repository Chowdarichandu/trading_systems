# PREMIUM-TAPE — NIFTY · ROUND 3: THE FADE TURN · SPEC · FROZEN BEFORE SCORING · 2026-11-14

Diagnosis chain: Round 1 chased the premium's own range break and bled all year (P1-X1 -Rs75,995.75 · P2-X2 -Rs59,299.85 · COMB-X2 -Rs109,818.95). Round 2 waited for the retest of the break and still bled both exits (P-RET-X1 -Rs13,696.60 · P-RET-X2 -Rs8,026.00 on 47 trades, placebo 67.3). Every continuation shape on this tape loses; the cross-programme finding of the day is that reversal is the only side that ever shows a pulse. **The turn: trade the premium spike's EXHAUSTION — when one contract's premium spikes to overbought, buy the OPPOSITE contract.**

Research only. Nothing running is changed. Option BUYING only (the bought contract is always bought, never sold), 1 lot (65), Rs220/trade, paper only, real money Rs0.

## Data, contract selection, indicators — IDENTICAL to Rounds 1-2
- `premium_tape_nifty_SPEC.md` governs unchanged: same premium store (`oi_buildup_data/candles_NIFTY_*.json`, 7-field candles), same frozen strike (round of the 09:15 spot close / 50 x 50), same weekly expiry rule, same availability test (bars 09:15..15:20 contiguous; missing = `nc_no_file`, incomplete = `nc_partial`, counted per day-side, never substituted), same premium VWAP (volume-weighted, typical price), same premium opening range (premium high/low over bars 09:15..09:40, i.e. 09:15-09:45 clock time), same premium RSI(14) (Wilder, within the day's premium closes only; seed = SMA of the first 14 close-to-close changes; valid from bar index 14).
- Bar grid: 75 bars, starts 09:15..15:25.

## CONTROL (must reproduce before the turn is scored)
- The Round-1 P1-X1 book, rebuilt with the identical machinery: **168 trades, full Jan-Oct net -Rs75,995.75**. If the control does not reproduce exactly, the run stops and reports the mismatch — the turn is not scored.

## THE TURN — RULE P-FADE (one rule)
Per day, across the day's two available contracts:
1. **SPIKE EVENT**: the first bar i with start time in 09:45..14:30 on which a contract's premium **close > its premium OR high** AND that contract's **premium RSI(14) at bar i >= 70**. (RSI is NaN before bar index 14, so no spike can fire before 10:25. No VWAP condition — the spike is defined by the range break plus overbought RSI only.) Per contract-day only the FIRST spike is tracked. The day's spike is the earliest across the two contracts; same-bar tie: larger relative break size (close - OR high) / OR high first, then CE before PE.
2. **ENTRY**: buy the **OPPOSITE side's** contract (CE spiked -> buy the day's PE contract; PE spiked -> buy the day's CE contract) at the open of bar i+1 (14:35 at the latest). One trade per day: the first spike event. If the opposite side is unavailable that day (NC), the spike is counted but no trade is taken (counted as `spike_blocked_opposite_nc`). No spike by 14:30 = no trade.

## Exits (on the BOUGHT contract, carried from Round 1, premium points)
- X1: stop -50 / target +90; within a bar the stop is checked first; scan bars entry..15:15; no trigger -> exit at the open of the 15:20 bar.
- X2: hard stop -60 scanned intrabar (precedence within the bar); otherwise exit at the CLOSE of the first bar (entry..15:15) whose close is below the **bought contract's own** premium VWAP at that bar; if none, exit at the open of the 15:20 bar.
- Net per trade = (exit - entry) x 65 - Rs220. Win = net > 0. Rs/trade-day = total / distinct trade days.

## Reporting
- Gate: spot days 2026-01-01..2026-10-31; windows Jan-Jun (<= 2026-06-30), Jul-Oct (>= 2026-07-01), full Jan-Oct. Per exit (X1 / X2): trades, net, WR, Rs/trade-day per window.
- **Spike events**: contract-days with a tracked spike, days with >= 1 spike, trades taken, spikes blocked by opposite-side NC.
- NC counts (gate + November), identical accounting to Rounds 1-2.
- November CF (descriptive): spot days 2026-11-02..2026-11-13, same reporting.
- Timing audit: every scored trade re-checked (entry bar = spike bar + 5 min; entry = stored open of the bought contract); premium VWAP and premium RSI recomputed from truncated series by an independent code path at sampled spike bars (VWAP/RSI of the spiking contract; VWAP of the bought contract).
- Random-entry placebo on the best exit row (by full-year total): 1000 draws x the row's trade count; each trade = a randomly chosen one of a random gate day's two contracts (uniform over available day-sides), a random entry bar 09:20..15:15, the row's own exit rule; percentile = share of draws <= the real total.

No parameter is tuned after scoring begins; P-FADE with X1/X2 is the whole test.
