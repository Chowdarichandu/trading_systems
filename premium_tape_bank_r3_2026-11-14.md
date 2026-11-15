# PREMIUM-TAPE — BANK NIFTY · ROUND 3: WIDEN THE RETEST · RESULTS · 2026-11-14

Spec frozen before scoring: `premium_tape_bank_r3_SPEC.md`. Build: `premium_tape_bank_r3_build.py`. Numbers: `premium_tape_bank_r3_results.json`, trades: `premium_tape_bank_r3_trades.csv`. Research only — no book, ledger or job changed. Paper only, real money Rs0. Buying only, 1 lot (30), Rs220/trade, X1 exits only (stop −50 / target +90, square-off 15:20). Signals come off each selected contract's OWN premium candles, identical data and contract selection to Rounds 1–2.

## Control — Round-2 P-RET-X1 reproduced exactly

**PASS** — 46 trades, +12,132.50 full Jan–Oct, WR 47.8% (Jan–Jun 28 trades / +5,724.50; Jul–Oct 18 trades / +6,408.00; gate events 199, completed retests 49; November 3 trades / -960.00). Steps were scored only after this reproduction.

## Coverage / NC

- Gate days: 203. Side NC: CE 0 days, PE 0 days; both-sides-NC days 0 (identical for control and all steps — same selection).
- November days: 9. Side NC: CE 0 days, PE 0 days; both-sides-NC days 0.

## Selectivity — break events vs completed retests (contract-days)

| Config | Window | Break events | Completed retests | Expired: close below VWAP | Expired: window end | No-event contract-days |
|---|---|---|---|---|---|---|
| Control (60m, 1/day) | Gate | 199 | 49 | 30 | 120 | 207 |
| A | Gate | 199 | 63 | 41 | 95 | 207 |
| B | Gate | 199 | 49 | 30 | 120 | 207 |
| C | Gate | 199 | 63 | 41 | 95 | 207 |
| Control (60m, 1/day) | November | 9 | 3 | 1 | 5 | 9 |
| A | November | 9 | 3 | 2 | 4 | 9 |
| B | November | 9 | 3 | 1 | 5 | 9 |
| C | November | 9 | 3 | 2 | 4 | 9 |

Second pass (Steps B/C, gate):

| Config | Days with trade 1 | Second events | Completed second retests | Second expired: close below VWAP | Second expired: window end | Second trades taken |
|---|---|---|---|---|---|---|
| B | 46 | 26 | 7 | 3 | 16 | 7 |
| C | 58 | 37 | 15 | 3 | 19 | 15 |

## Results — X1 exits

| Window | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| Control — Full Jan–Oct | 46 | +12,132.50 | 47.8% | +263.75 |
| Control — Jan–Jun | 28 | +5,724.50 | 46.4% | +204.45 |
| Control — Jul–Oct | 18 | +6,408.00 | 50.0% | +356.00 |
| A — Full Jan–Oct | 58 | +16,692.50 | 48.3% | +287.80 |
| A — Jan–Jun | 37 | +11,244.50 | 48.6% | +303.91 |
| A — Jul–Oct | 21 | +5,448.00 | 47.6% | +259.43 |
| B — Full Jan–Oct | 53 | +8,492.50 | 45.3% | +184.62 |
| B — Jan–Jun | 33 | +1,324.50 | 42.4% | +47.30 |
| B — Jul–Oct | 20 | +7,168.00 | 50.0% | +398.22 |
| C — Full Jan–Oct | 73 | +3,492.50 | 42.5% | +60.22 |
| C — Jan–Jun | 49 | -995.50 | 40.8% | -26.91 |
| C — Jul–Oct | 24 | +4,488.00 | 45.8% | +213.71 |

- **A**: Step A — window widened to 120 min (24 watch bars), 1 trade/day.
- **B**: Step B — 60-min window, second trade allowed after the first closes (max 2/day).
- **C**: Step C — A+B combined: 120-min window + second trade (max 2/day).

## November CF (descriptive, Nov 2–13)

| Config | Trades | Net Rs | WR | Rs/trade-day |
|---|---|---|---|---|
| Control | 3 | -960.00 | 33.3% | -320.00 |
| A | 3 | -960.00 | 33.3% | -320.00 |
| B | 3 | -960.00 | 33.3% | -320.00 |
| C | 3 | -960.00 | 33.3% | -320.00 |

## Timing audit

**PASS (258 completed retests re-verified from truncated series across control + steps A/B/C, gate + November; 230 gate trade entries re-checked)** — premium opening-range high and premium VWAP recomputed from each contract-day series truncated at the event and retest bars by an independent code path; each event asserted as the first eligible break inside its search range; no fail and no earlier hold inside any watch; the watch-length bound and 14:25 cap asserted; second-pass events asserted strictly after the day's first-trade exit bar; every scored trade's entry is exactly the bar after its retest bar at that bar's stored open.

## Placebo (random entry, X1, 1,000 draws × each row's trade count)

| Config | Real total Rs | Percentile | Placebo median | Placebo p95 | Placebo max | Drops |
|---|---|---|---|---|---|---|
| A | +16,692.50 | 99.4th | -19,471.00 | +2,942.00 | +28,544.00 | 0 |
| B | +8,492.50 | 98.3th | -17,838.50 | +3,679.00 | +16,979.50 | 0 |
| C | +3,492.50 | 96.6th | -24,824.50 | +254.00 | +22,647.50 | 0 |

## Desired-result bar

A step IS the channel only if ALL of: Jan–Jun net > 0 AND Jul–Oct net > 0 AND placebo percentile >= 95th AND full-year net above the control's +Rs12,132.50.

| Config | Both windows positive | Placebo >= 95th | Above control | Clears the bar |
|---|---|---|---|---|
| A | YES | YES (99.4th) | YES | **YES** |
| B | YES | YES (98.3th) | no | **NO** |
| C | no | YES (96.6th) | no | **NO** |

**Step(s) clearing the bar: A.**
