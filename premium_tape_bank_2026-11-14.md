# PREMIUM-TAPE — BANK NIFTY · premium-chart signals · Jan–Oct 2026 gate + Nov 2–13 CF

Spec frozen before scoring: `premium_tape_bank_SPEC.md`. Build: `premium_tape_bank_build.py`. Numbers: `premium_tape_bank_results.json`, trades: `premium_tape_bank_trades.csv`. Research only — no book, ledger or job changed. Paper only, real money Rs0. Buying only, 1 lot (30), Rs220/trade. Signals come off each selected contract's OWN premium candles (CE and PE of the strike nearest spot at 09:15, fixed for the day); spot is used only for that 09:15 strike selection.

**Premium VWAP basis:** volume-weighted from the contract's own candles on every scored day (sources: round5 C5 store, per-day files — both carry volume). The equal-weighted proxy fallback never occurred in the gate or November (0 scored trades on the proxy basis).

## Coverage / NC
- Gate days: 203 (Jan 1–Oct 31 2026 stored days). Side NC: CE 0 days, PE 0 days; both-sides-NC days 0. Every selected contract-day carried all 74 bars 09:15–15:20.
- LATE first triggers (after 15:10, never traded): P1 0, P2 3, COMB 0. Triggered-but-unscored trades: 0 in every book.
- November: 9 days, side NC 0/0, late 0, unscored 0.

## Timing audit
**PASS (363 triggers)** — premium VWAP, opening range, momentum and RSI recomputed from each contract-day series truncated at the signal bar; entry is exactly the bar after the signal bar in every trade.

## Results — full Jan–Oct 2026
| Book | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| P1-X1 | 174 | -62,364.00 | 32.8% | -358.41 |
| P1-X2 | 174 | +1,791.00 | 22.4% | +10.29 |
| P2-X1 | 172 | -45,410.50 | 36.0% | -264.01 |
| P2-X2 | 172 | -55,096.00 | 17.4% | -320.33 |
| COMB-X1 | 199 | -64,649.50 | 33.7% | -324.87 |
| COMB-X2 | 199 | -23,281.00 | 19.6% | -116.99 |

## Results — Jan–Jun 2026
| Book | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| P1-X1 | 110 | -19,917.50 | 36.4% | -181.07 |
| P1-X2 | 110 | +33,046.00 | 23.6% | +300.42 |
| P2-X1 | 102 | -30,382.50 | 35.3% | -297.87 |
| P2-X2 | 102 | -10,885.50 | 20.6% | -106.72 |
| COMB-X1 | 119 | -27,548.00 | 35.3% | -231.50 |
| COMB-X2 | 119 | +10,549.00 | 20.2% | +88.65 |

## Results — Jul–Oct 2026
| Book | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| P1-X1 | 64 | -42,446.50 | 26.6% | -663.23 |
| P1-X2 | 64 | -31,255.00 | 20.3% | -488.36 |
| P2-X1 | 70 | -15,028.00 | 37.1% | -214.69 |
| P2-X2 | 70 | -44,210.50 | 12.9% | -631.58 |
| COMB-X1 | 80 | -37,101.50 | 31.2% | -463.77 |
| COMB-X2 | 80 | -33,830.00 | 18.8% | -422.88 |

## November CF (descriptive, Nov 2–13)
| Book | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| P1-X1 | 9 | -7,080.00 | 22.2% | -786.67 |
| P1-X2 | 9 | -18,180.00 | 0.0% | -2,020.00 |
| P2-X1 | 8 | -9,560.00 | 12.5% | -1,195.00 |
| P2-X2 | 8 | -11,541.50 | 0.0% | -1,442.69 |
| COMB-X1 | 9 | -7,080.00 | 22.2% | -786.67 |
| COMB-X2 | 9 | -14,686.50 | 0.0% | -1,631.83 |

## Month table (net Rs, Jan–Oct)
| Book | 01 | 02 | 03 | 04 | 05 | 06 | 07 | 08 | 09 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| P1-X1 | -9,960 | +4,360 | +5,120 | -5,000 | -12,878 | -1,560 | -18,876 | -12,490 | +3,840 | -14,920 |
| P1-X2 | -16,527 | +14,908 | +20,520 | +8,726 | -13,486 | +18,904 | -8,288 | -15,507 | +7,080 | -14,539 |
| P2-X1 | -2,660 | +2,452 | -10,720 | -12,134 | +14,480 | -21,800 | -2,628 | -12,322 | +4,722 | -4,800 |
| P2-X2 | -10,476 | -6,719 | +266 | +1,182 | +7,926 | -3,065 | -10,790 | -9,342 | -10,694 | -13,386 |
| COMB-X1 | -3,386 | +6,718 | +5,120 | -9,200 | -11,680 | -15,120 | -14,370 | -20,194 | +7,423 | -9,960 |
| COMB-X2 | -11,912 | +16,540 | +25,895 | -2,496 | -15,931 | -1,546 | -13,598 | -18,560 | +7,250 | -8,924 |

## Placebo (best full-year book)
Best book by Jan–Oct total: **P1-X2** (+1,791.00). Random-entry placebo (500 iterations, same trade count, random scoreable day/side/entry bar, same exit): real total at the **93.2th percentile** (placebo median -39,643.50, p95 +7,612.50, max +54,004.50; drops 0).

## Reading of the numbers
- P1 (premium range break) with the fixed -50/+90 exit loses in both windows (-19,917.50 / -42,446.50). With the premium-VWAP-loss exit it is +33,046.00 in Jan-Jun and -31,255.00 in Jul-Oct — the year's only positive full-year book (+1,791.00, +Rs10.29/trade-day, WR 22.4%) is a window flip, and its placebo percentile (93.2) sits below the 95 bar this programme uses elsewhere.
- P2 (premium momentum) loses under both exits in both windows (-45,410.50 X1 / -55,096.00 X2 full-year).
- Combined first-trigger loses under both exits (-64,649.50 X1 / -23,281.00 X2); adding P2's earlier triggers to P1 makes P1-X2's near-zero into a clear loss.
- November agrees with the gate: every book negative, P1-X2 worst (-18,180.00, 0 wins in 9 trades).
