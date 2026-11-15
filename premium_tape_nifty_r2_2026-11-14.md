# PREMIUM-TAPE — NIFTY · ROUND 2: THE RETEST TURN · RESULTS · 2026-11-14

Spec: `premium_tape_nifty_r2_SPEC.md` (frozen before scoring) · Build: `premium_tape_nifty_r2_build.py` · Numbers: `premium_tape_nifty_r2_results.json` · Trades: `premium_tape_nifty_r2_trades.csv`.
Basis: **paper only, real money Rs0 · option buying only · 1 lot (65) · Rs220/trade.** Data, contract selection, premium VWAP and opening range are identical to Round 1 (same store, same frozen strike/expiry, NC counted per day-side, never substituted).

Coverage: 203 gate days (Jan-Oct 2026) · NC gate: 27 day-sides `nc_no_file` of 406, 0 partial · NC November: 4 day-sides of 18. Premium VWAP volume-weighted throughout (no proxy day-sides).

## Control — Round-1 P1-X1 reproduced exactly

| Control | Trades | Net |
|---|---|---|
| P1-X1 (Round 1, rebuilt) | 168 | **-Rs75,995.75** |

Matches the Round-1 line to the paisa before the turn was scored.

## The turn — P-RET (enter on the retest of the break, not the break)

Break event = a contract's premium closes above its own 09:15-09:45 premium range high while above its premium VWAP (no entry). Entry only when a later bar's low touches that contract's premium VWAP and the bar closes back above it — within 60 minutes, by 14:25, and only if no bar has closed below VWAP in between. One trade per day: the first completed retest across both contracts.

**Selectivity (gate window, contract-days):**

| Break events | Completed retests | Expired: closed below VWAP | Expired: 60-min / 14:30 window ended |
|---|---|---|---|
| 192 | 48 (25.0%) | 48 | 96 |

48 contract-day retests produced 47 day trades (one day both contracts completed a retest; the earlier one was taken).

## Gate results — Jan-Oct 2026 (Rs/trade-day in brackets)

| Book — exit | Jan-Jun | Jul-Oct | Full Jan-Oct |
|---|---|---|---|
| P-RET-X1 (stop -50 / target +90) | 35 tr · **+6,278.25** · WR 40.0% [+179.38] | 12 tr · **-19,974.85** · WR 25.0% [-1,664.57] | 47 tr · **-13,696.60** · WR 36.2% [-291.42] |
| P-RET-X2 (VWAP-loss exit, -60 hard stop) | 35 tr · **-3,430.15** · WR 17.1% [-98.00] | 12 tr · **-4,595.85** · WR 16.7% [-382.99] | 47 tr · **-8,026.00** · WR 17.0% [-170.77] |

## Placebo (best full-year row = P-RET-X2)

Random-entry placebo, 1000 draws x 47 trades (random gate day-side, random entry bar, same X2 exits): real total -Rs8,026.00 sits at the **67.3rd percentile** of random (draw mean -Rs13,373.07, p95 +Rs8,009.14). Better than the median random draw, well short of the p95 bar — and the total itself is still negative.

## Timing audit

PASS. Every scored trade re-checked: entry bar = retest bar + 5 min, entry premium = the stored open of that bar. Premium VWAP recomputed from truncated series by an independent code path at 25 sampled retest bars: max difference ~5.7e-14 (exact).

## November counterfactual (descriptive — Nov 2-13, 9 trading days)

Selectivity: 6 break events · 4 completed retests · 1 expired on a close below VWAP · 1 expired on the window.

| Book — exit | Trades | Net | WR |
|---|---|---|---|
| P-RET-X1 | 4 | **+3,026.50** | 50.0% |
| P-RET-X2 | 4 | **-2,449.75** | 0.0% |

Four trades; a sample too small to read.

## Plain reading

The retest turn cuts the Round-1 bleed hard — 47 trades instead of 168, -Rs8,026 (X2) / -Rs13,697 (X1) instead of -Rs59,300 / -Rs75,996 — because three of every four break events never complete a retest and are never traded. But it does not turn the channel positive: both exits are negative on the full year, X1's positive Jan-Jun (+Rs6,278) reverses in Jul-Oct (-Rs19,975 on only 12 trades), and the best row beats only the 67th percentile of random entries into the same contracts. Waiting for the retest removes most of the chase damage; what remains still has no edge.
