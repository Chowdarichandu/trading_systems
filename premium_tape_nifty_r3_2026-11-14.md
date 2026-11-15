# PREMIUM-TAPE — NIFTY · ROUND 3: THE FADE TURN · RESULTS · 2026-11-14

Spec: `premium_tape_nifty_r3_SPEC.md` (frozen before scoring) · Build: `premium_tape_nifty_r3_build.py` · Numbers: `premium_tape_nifty_r3_results.json` · Trades: `premium_tape_nifty_r3_trades.csv`.
Basis: **paper only, real money Rs0 · option buying only (the bought contract is always bought, never sold) · 1 lot (65) · Rs220/trade.** Data, contract selection, premium VWAP, opening range and premium RSI are identical to Rounds 1-2 (same store, same frozen strike/expiry, NC counted per day-side, never substituted).

Coverage: 203 gate days (Jan-Oct 2026) · NC gate: 27 day-sides `nc_no_file` of 406, 0 partial · NC November: 4 day-sides of 18. Premium VWAP volume-weighted throughout (no proxy day-sides).

## Control — Round-1 P1-X1 reproduced exactly

| Control | Trades | Net |
|---|---|---|
| P1-X1 (Round 1, rebuilt) | 168 | **-Rs75,995.75** |

Matches the Round-1 line to the paisa before the turn was scored.

## The turn — P-FADE (buy the opposite contract at the spike's exhaustion)

Spike event = a contract's premium closes above its own 09:15-09:45 premium range high with that contract's premium RSI(14) >= 70 on the same bar (bars 09:45..14:30). Entry = buy the OPPOSITE side's contract at the next bar's open. One trade per day: the first spike event. Exits sit on the bought contract.

**Selectivity (gate window):**

| Contract-day spikes | Spike days | Trades taken | Spikes blocked (opposite side NC) |
|---|---|---|---|
| 121 | 110 | 110 | 0 |

## Gate results — Jan-Oct 2026 (Rs/trade-day in brackets)

| Book — exit | Jan-Jun | Jul-Oct | Full Jan-Oct |
|---|---|---|---|
| P-FADE-X1 (stop -50 / target +90) | 62 tr · **+13,032.75** · WR 35.5% [+210.21] | 48 tr · **-27,141.50** · WR 25.0% [-565.45] | 110 tr · **-14,108.75** · WR 30.9% [-128.26] |
| P-FADE-X2 (bought-contract VWAP-loss exit, -60 hard stop) | 62 tr · **-9,857.00** · WR 24.2% [-158.98] | 48 tr · **-9,529.75** · WR 16.7% [-198.54] | 110 tr · **-19,386.75** · WR 20.9% [-176.24] |

## Placebo (best full-year row = P-FADE-X1)

Random-entry placebo, 1000 draws x 110 trades (random gate day, randomly chosen one of the day's two contracts, random entry bar, same X1 exits): real total -Rs14,108.75 sits at the **70.0th percentile** of random (draw mean -Rs29,097.65, p95 +Rs22,613.16). Better than the median random draw, short of the p95 bar — and the total itself is still negative.

## Timing audit

PASS. Every scored trade re-checked: entry bar = spike bar + 5 min, entry premium = the bought contract's stored open at that bar (verified against the raw files). Premium VWAP and premium RSI recomputed from truncated series by an independent code path at 25 sampled spike bars: max VWAP difference ~5.7e-14, max RSI difference 0.0 (exact).

## November counterfactual (descriptive — Nov 2-13, 9 trading days)

Selectivity: 3 contract-day spikes · 3 spike days · 3 trades taken · 0 blocked.

| Book — exit | Trades | Net | WR |
|---|---|---|---|
| P-FADE-X1 | 3 | **-6,877.25** | 0.0% |
| P-FADE-X2 | 3 | **-835.50** | 33.3% |

Three trades; a sample too small to read.

## Plain reading

The fade is the least-bad shape this tape has produced — 110 trades, -Rs14,108.75 (X1) / -Rs19,386.75 (X2) against Round 1's -Rs75,995.75 and Round 2's -Rs13,696.60 / -Rs8,026.00 on fewer trades — and it owns the tape's first positive half-year window under a fixed exit (X1 Jan-Jun +Rs13,032.75). But it does not turn the channel positive: X1's first-half gain reverses in Jul-Oct (-Rs27,141.50, the worst single window of the round), X2 loses in both windows, and the best row beats only the 70th percentile of random entries into the same contracts. Fading the spike removes most of the chase damage, like the retest did; what remains still has no edge.
