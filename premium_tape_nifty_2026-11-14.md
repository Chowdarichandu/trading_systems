# PREMIUM-TAPE — NIFTY · RESULTS · 2026-11-14

Spec: `premium_tape_nifty_SPEC.md` (frozen before scoring) · Build: `premium_tape_nifty_build.py` · Numbers: `premium_tape_nifty_results.json` · Trades: `premium_tape_nifty_trades.csv`.
Basis: **paper only, real money Rs0 · option buying only · 1 lot (65) · Rs220/trade.** Signals are read off each contract's OWN premium chart (premium VWAP, the contract's own 09:15-09:45 premium range, premium RSI/momentum). Spot is used only for the frozen 09:15 strike selection. Contracts: the day's nearest-strike CE and PE at the weekly expiry; a missing file makes that side unavailable that day (NC, counted, never substituted).

Coverage: 203 gate days (Jan-Oct 2026) · NC gate: 27 day-sides `nc_no_file` of 406, 0 partial · NC November: 4 day-sides of 18. Premium VWAP is genuinely volume-weighted (volume present in every stored contract-day; the proxy fallback never fired).

## Gate results — Jan-Oct 2026 (Rs/trade-day in brackets)

| Book — exit | Jan-Jun | Jul-Oct | Full Jan-Oct |
|---|---|---|---|
| P1-X1 (stop -50 / target +90) | 104 tr · **-61,707.75** · WR 32.7% [-593.34] | 64 tr · **-14,288.00** · WR 40.6% [-223.25] | 168 tr · **-75,995.75** · WR 35.7% [-452.36] |
| P1-X2 (VWAP-loss exit, -60 hard stop) | 104 tr · **-87,304.10** · WR 19.2% [-839.46] | 64 tr · **-7,381.75** · WR 26.6% [-115.34] | 168 tr · **-94,685.85** · WR 22.0% [-563.61] |
| P2-X1 | 102 tr · **-55,998.85** · WR 37.3% [-549.01] | 66 tr · **-37,679.50** · WR 30.3% [-570.90] | 168 tr · **-93,678.35** · WR 34.5% [-557.61] |
| P2-X2 | 102 tr · **-38,500.85** · WR 16.7% [-377.46] | 66 tr · **-20,799.00** · WR 18.2% [-315.14] | 168 tr · **-59,299.85** · WR 17.3% [-352.98] |
| COMB-X1 | 114 tr · **-80,160.35** · WR 32.5% [-703.16] | 75 tr · **-32,844.25** · WR 37.3% [-437.92] | 189 tr · **-113,004.60** · WR 34.4% [-597.91] |
| COMB-X2 | 114 tr · **-94,956.95** · WR 13.2% [-832.96] | 75 tr · **-14,862.00** · WR 20.0% [-198.16] | 189 tr · **-109,818.95** · WR 15.9% [-581.05] |

Every book, every exit, both windows: negative. The least-bad row is P2-X2 at -Rs59,299.85 on 168 trades.

## Placebo (best full-year book = P2-X2)

Random-entry placebo, 1000 draws x 168 trades (random gate day-side, random entry bar, same X2 exits): real total -Rs59,299.85 sits at the **34.6th percentile** of random (draw mean -Rs48,523.71, p95 -Rs5,388.10). The premium-momentum entries are mid-pack random — no edge over entering the same contracts at random bars.

## Timing audit

PASS. Every scored trade re-checked: entry bar = signal bar + 5 min, entry premium = the stored open of that bar. Premium VWAP and premium RSI recomputed from truncated series by an independent code path at 25 sampled signal bars: max differences ~1e-14 (exact). One audit-path bug was found and fixed during the run (the first recompute indexed the raw candle fields wrongly — open/high/low in place of high/low/close); the scoring path was unaffected, and the corrected audit passes to the digit.

## November counterfactual (descriptive — Nov 2-13, 9 trading days)

| Book — exit | Trades | Net | WR |
|---|---|---|---|
| P1-X1 | 6 | **+4,643.75** | 50.0% |
| P1-X2 | 6 | **+9,375.75** | 16.7% |
| P2-X1 | 6 | **-2,473.75** | 33.3% |
| P2-X2 | 6 | **+5,453.00** | 33.3% |
| COMB-X1 | 7 | **+1,173.75** | 42.9% |
| COMB-X2 | 7 | **+8,284.75** | 14.3% |

Six to seven trades per row; the positive November rows ride one or two large winners at 14-50% win rates — the same payoff shape as the gate window, on a sample too small to read.

## Plain reading

The premium's own tape carries no standalone channel either: premium range breaks (P1) and premium momentum crosses (P2) both lose in both halves of the year under both exit rules, the combined first-trigger book loses most of all (-Rs1.13 lakh / -Rs1.10 lakh), and the best row cannot beat the 35th percentile of random entries into the same contracts. Changing the data source from the spot chart to the premium chart did not change the answer.
