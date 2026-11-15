# DIAL — STOCKS · ROUND 2 (FREQUENCY TEST) · GATE REPORT · 2026-11-14

Programme: DIAL (one roof, one name). Member: standalone indicator system, Stocks segment.
Spec: `dial_stocks_r2_SPEC.md` (frozen before scoring). Build: `dial_stocks_r2_build.py`
(reuses `dial_stocks_build.py` verbatim for data/indicators/exits).
Numbers: `dial_stocks_r2_results.json` · Selected trades: `dial_stocks_r2_trades.csv`.
Basis: **equity cash intraday · frozen 25-name Stock Book watchlist · per 100 shares
PROVISIONAL · ₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
This system is STANDALONE — it does not condition or filter the Stock Book.

## VERDICT — FAIL, both components, both years, on every gate leg

Cutting the dose ~16× (from ~32 trades/day to exactly 2) shrank the loss almost exactly
in proportion and changed nothing else: the selected book still loses in both years, its
win rate went *down* slightly, and it sits mid-pack against random entries taken at the
same one-per-day frequency. **Frequency was not the poison.** Nothing passes, nothing is
adopted, nothing arms.

## What Round 2 changed (and only this)

Round 1 took the first qualifying signal per stock per day (~6,700 trades/year). Round 2
takes, per component per day across all 25 names, **at most one trade — the day's most
extreme signal** (DIAL-R: largest Bollinger %B excursion past the trigger, either side;
DIAL-T: largest signal-bar move % in the flip direction; ties → earliest bar, then
alphabetical). Signals, entries, exits (+1.0% / −0.5% / square-off 15:15), the VWAP
EW-proxy basis for DIAL-T (the stores carry no volume — same disclosed basis as Round 1),
and the ₹40/trade cost are Round 1's, verbatim.

## Control — the pool is Round 1's signal set, proven

Before any R2 number was scored, the unselected candidate pool was checked against
Round 1: **all 15,176 published Round 1 trade rows reproduce identically** (symbol, date,
component, side, signal/entry stamps, net), and every published total ties exactly —
T 2025 −₹125,217.24 (4,254) · T 2026 −₹127,459.09 (4,274) · R 2025 −₹68,420.73 (2,438) ·
R 2026 −₹165,302.21 (2,465) · Combined 2025 −₹193,637.97 (6,692) · Combined 2026
−₹292,761.31 (6,739) · November Combined −₹20,466.44 (293). (Round 1's year totals are
sums of rounded monthly nets; the pool reproduces them under that same convention — raw
float sums differ by ≤ ₹0.04 of monthly rounding.) Timing audit asserted in the build:
entry bar strictly follows the signal bar on every candidate.

## Results — per year, per component (Jan–Oct)

### DIAL-T (most extreme Supertrend flip of the day)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 207 | **−₹10,600.60** | 35.75% | −₹1,060.06 | 41.5 | −3,132.97 / −7,467.63 | −₹20,300.40 | 5/10 | FAIL — every leg |
| 2026 | 205 | **−₹3,902.08** | 33.66% | −₹390.21 | 62.5 | −6,403.19 / +2,501.11 | −₹14,815.68 | 5/10 | FAIL — every leg |

Months 2025: Jan +1,302.82 · Feb +991.15 · Mar −1,521.97 · Apr +2,647.33 · May −6,552.30 ·
Jun −2,244.98 · Jul −1,833.27 · Aug −7,109.87 · Sep +2,339.48 · Oct +1,381.01.
Months 2026: Jan +820.37 · Feb +1,951.34 · Mar −1,267.28 · Apr −8,454.96 · May +547.34 ·
Jun +4,303.15 · Jul −158.36 · Aug −2,337.52 · Sep +2,232.08 · Oct −1,538.24.

### DIAL-R (most extreme RSI + %B excursion of the day)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 207 | **−₹3,124.40** | 35.27% | −₹312.44 | 74.5 | −1,495.57 / −1,628.83 | −₹11,458.80 | 6/10 | FAIL — every leg |
| 2026 | 205 | **−₹18,735.87** | 31.71% | −₹1,873.59 | 13.0 | +491.45 / −19,227.32 | −₹29,359.77 | 8/10 | FAIL — every leg |

Months 2025: Jan +272.74 · Feb +2,763.00 · Mar −1,673.92 · Apr −653.62 · May −2,203.77 ·
Jun −4,814.42 · Jul −491.98 · Aug +5,132.12 · Sep +906.14 · Oct −2,360.69.
Months 2026: Jan −4,842.65 · Feb +1,907.06 · Mar −3,142.53 · Apr −1,056.09 · May +7,625.66 ·
Jun −10.77 · Jul −4,977.50 · Aug −7,900.37 · Sep −981.28 · Oct −5,357.40.

### DIAL-Stocks combined R2 (T ∪ R, ≤ 2 trades/day)

| Year | Trades | Total | WR | Pace/mo | Placebo pct | Halves H1/H2 | Ex-top-3 | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| 2025 | 414 | **−₹13,725.01** | 35.51% | −₹1,372.50 | 55.5 | −4,628.54 / −9,096.47 | −₹23,541.71 | 6/10 | FAIL — every leg |
| 2026 | 410 | **−₹22,637.96** | 32.68% | −₹2,263.80 | 39.0 | −5,911.74 / −16,726.22 | −₹34,019.76 | 6/10 | FAIL — every leg |

Months 2025: Jan +1,575.56 · Feb +3,754.15 · Mar −3,195.89 · Apr +1,993.71 · May −8,756.07 ·
Jun −7,059.40 · Jul −2,325.25 · Aug −1,977.76 · Sep +3,245.62 · Oct −979.68.
Months 2026: Jan −4,022.28 · Feb +3,858.40 · Mar −4,409.81 · Apr −9,511.05 · May +8,173.00 ·
Jun +4,292.38 · Jul −5,135.86 · Aug −10,237.90 · Sep +1,250.80 · Oct −6,895.64.

## The structural finding — the bleed is per trade, not per day

| Combined | Round 1 (flood) | Round 2 (one-a-day extremes) |
|---|---|---|
| 2025 trades / total / per trade | 6,692 · −₹193,637.97 · **−₹28.94** | 414 · −₹13,725.01 · **−₹33.15** |
| 2026 trades / total / per trade | 6,739 · −₹292,761.31 · **−₹43.44** | 410 · −₹22,637.96 · **−₹55.21** |
| Win rate 2025 / 2026 | 36.30% / 35.81% | 35.51% / 32.68% |

Every trading day in both windows produced at least one candidate in each component
(207 candidate days in 2025, 205 in 2026), so the dose fell from ~32 trades/day to
exactly 2. The total loss fell ~93% (2025) and ~92% (2026) — almost exactly the dose
reduction — while the loss **per trade rose** in both years and the win rate fell. Picking
the day's *most extreme* signal did not pick a better trade: for DIAL-R in 2026 the
extreme pick is actively worse than a random one-a-day entry (13.0th percentile — the
day's deepest fade kept running, the same disease Round 1 found in the flood, now
concentrated into a single daily dose). The frequency-matched placebo confirms the frame
itself is the problem: random entries at the same one-per-day dose also lose heavily
(combined draw medians −₹14,796.26 in 2025 and −₹18,861.08 in 2026) — the +1.0%/−0.5%
geometry on these names bleeds per trade at any dose, and no selection of these signals
at any frequency tested separates the real book from that bleed (best percentile anywhere
in this round: 74.5, DIAL-R 2025, against the 95 bar).

## November counterfactual (descriptive — Nov 2–13, the book's 9 trading days)

| Series | Trades | Net | vs Stock Book actual |
|---|---|---|---|
| DIAL-T R2 | 9 | −₹510.28 | — |
| DIAL-R R2 | 9 | −₹1,699.99 | — |
| **DIAL combined R2** | **18** | **−₹2,210.27** | **Stock Book +₹7,517.94** |
| (memo) DIAL combined Round 1 | 293 | −₹20,466.44 | — |

By day (combined R2): Nov 2 +223.83 · Nov 3 −1,444.27 · Nov 4 −227.00 · Nov 5 +321.76 ·
Nov 6 +172.64 · Nov 9 −466.00 · Nov 11 −647.30 · Nov 12 −34.65 · Nov 13 −109.27.
The one-a-day dose cut November's loss ~9× versus the flood — and it is still negative
on 6 of 9 days, with a single trade (the Nov 3 GLENMARK extreme fade, −₹1,241.85) making
over half the month's loss. The Stock Book made +₹7,517.94 on the same days. The forward
window agrees with the gate, again.

## Honest one-liner

**Frequency was not the poison — the poison is per trade.** Round 2 took the same signals
at 1/16th the dose and the loss shrank in proportion while the per-trade bleed grew and
the win rate fell: there is no indicator channel in the 25 names under this core at any
dose — flood or single daily extreme — because the frame loses on the average trade
before frequency is even asked. DIAL-Stocks R2 is recorded as a measured dead end next to
Round 1; the Stock Book's channel stays where it already was — its own construction.
