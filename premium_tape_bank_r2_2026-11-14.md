# PREMIUM-TAPE — BANK NIFTY · ROUND 2: THE RETEST TURN · RESULTS · 2026-11-14

Spec frozen before scoring: `premium_tape_bank_r2_SPEC.md`. Build: `premium_tape_bank_r2_build.py`. Numbers: `premium_tape_bank_r2_results.json`, trades: `premium_tape_bank_r2_trades.csv`. Research only — no book, ledger or job changed. Paper only, real money Rs0. Buying only, 1 lot (30), Rs220/trade. Signals come off each selected contract's OWN premium candles (CE and PE of the strike nearest spot at 09:15, fixed for the day), identical data and contract selection to Round 1.

## Control — Round-1 P1-X2 reproduced exactly

**PASS** — 174 trades, +1,791.00 full Jan–Oct (Jan–Jun 110 trades / +33,046.00; Jul–Oct 64 trades / -31,255.00; November 9 trades / -18,180.00). The turn below was scored only after this reproduction.

## Coverage / NC

- Gate days: 203. Side NC: CE 0 days, PE 0 days; both-sides-NC days 0.
- November days: 9. Side NC: CE 0 days, PE 0 days; both-sides-NC days 0.

## Selectivity — break events vs completed retests (contract-days)

| Window | Break events | Completed retests | Expired: close below VWAP | Expired: window end | No-event contract-days |
|---|---|---|---|---|---|
| Gate Jan–Oct | 199 | 49 | 30 | 120 | 207 |
| November CF | 9 | 3 | 1 | 5 | 9 |

Gate events by side: CE 97, PE 102; completed retests by side: CE 21, PE 28.

## Results — P-RET

| Window — exit | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| Full Jan–Oct — X1 | 46 | +12,132.50 | 47.8% | +263.75 |
| Jan–Jun — X1 | 28 | +5,724.50 | 46.4% | +204.45 |
| Jul–Oct — X1 | 18 | +6,408.00 | 50.0% | +356.00 |
| Full Jan–Oct — X2 | 46 | -5,996.50 | 21.7% | -130.36 |
| Jan–Jun — X2 | 28 | -17,396.50 | 17.9% | -621.30 |
| Jul–Oct — X2 | 18 | +11,400.00 | 27.8% | +633.33 |

## November CF (descriptive, Nov 2–13)

| Exit | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| X1 | 3 | -960.00 | 33.3% | -320.00 |
| X2 | 3 | -984.00 | 33.3% | -328.00 |

## Timing audit

**PASS (52 completed retests re-verified from truncated series; 98 trade entries re-checked)** — premium opening-range high and premium VWAP recomputed from each contract-day series truncated at the event and retest bars by an independent code path; the first-break, watch and hold conditions re-asserted; every scored trade's entry is exactly the bar after its retest bar at that bar's stored open.

## Placebo (best full-year exit row)

Best row: **P-RET-X1** (+12,132.50). Random-entry placebo (1,000 iterations, same trade count, random scoreable day/side/entry bar, same exit): real total at the **98.9th percentile** (placebo median -15,163.00, p95 +5,045.00, max +27,872.00; drops 0).
