# Stocks EQUITY — DBL-LONG — v2 CANDIDATE spec (frozen 2026-10-31)

**CANDIDATE ONLY — not adopted, not a system, no orders. Paper
only, real money ₹0. EQUITY CASH intraday, LONG/SHORT language.
Every rupee figure: provisional per 100 shares, ₹40/trade flat
cost. Source: INV tuning loop Line 1b, `stocks_tuning_inv_report.md`
(spec `stocks_tuning_inv_frozen.md`, Line 1b section frozen before
scoring; anchors reproduced Line 1 figures to the paisa).**

## Status — what this is, and what it does NOT change

The November 2026 INV1 shadow runs **exactly as frozen** in
`stocks_p2inv_november_shadow_spec.md`. This candidate changes
nothing about November. The DBL condition was Line 1's recorded
near-miss (both halves positive and balanced, breadth 9/25 — one
stock short of the gate). Line 1b applied the one structural step
Line 1 itself proved on INV1 — LONG-only — and DBL-LONG passes
the full pass gate. Like INV-LONG, it was selected on the same
Jan–Oct data that suggested it: a *hypothesis with a frozen
shape*, whose verdict requires a fresh window, pre-declared
below.

## The rule — exact

1. **Entry pool: P2, exactly as Rounds 6–9** — frozen V5
   re-entry signal stream (`stocks_equity_reentry.py`
   `pool_pick` over v4 + skill_or detectors); chain round ≤ 2
   under the exit's own timing; entry_time < 10:30; ADR≥3%
   stock-day (prior-10-day mean (high−low)/close×100, min 5
   prior rows, trade day excluded).
2. **DBL condition (both legs, bars strictly before the trade
   day; equality = met):** Nifty previous close ≤ its 50DMA
   (mean of the 50 closes ending at the previous bar) **AND**
   the traded stock's own previous close ≤ its own 20DMA
   (mean of the 20 closes ending at the previous bar). If
   either average cannot be computed, no trades that day.
3. **DIRECTION: LONG entries only.** SHORT signals in the pool
   are not taken.
4. **Exits: primary T125/S050** — target +1.25% / stop −0.5%,
   stop-first on a same-candle tie, 15:10 square-off.
   **Shadow column T100/S050** (+1.0% / −0.5%) recorded per
   trade; the LONG-only set is both-halves positive at T100
   as well (see below).
5. All qualifying LONG trades are taken; no portfolio cap, no
   per-stock cap beyond chain round ≤ 2 and one open position
   per stock at a time.

## In-sample record (Jan–Oct 2026 — hypothesis-generation only)

At **T125/S050**: 133 trades, win 37.6%, gross expectancy
+₹222.91/trade, net expectancy **+₹182.91/trade**, net
**+₹24,327.37** provisional per 100 shares — halves
**Jan–May +₹15,426.61 (92 trades) / Jun–Oct +₹8,900.76
(41 trades)**, October +₹7,957.95. Breadth **10/25** stocks
net-positive (exactly at the gate minimum); top-3 share 129.0%.
At **T100/S050** (shadow reading): 139 trades, net +₹20,848.40,
halves +₹8,669.52 / +₹12,178.88, breadth 10/25 — also passes.

Reference points: DBL both-directions at T125 = 390 trades,
+₹16,548.78, expectancy +₹42.43, breadth 9/25 (the Line 1
near-miss). INV-LONG at T125 = 249 trades, +₹24,185.73,
expectancy +₹97.13. The DBL leg drops 116 of INV-LONG's 249
trades; those dropped trades netted **−₹141.64 combined** — the
stock-below-its-own-20DMA leg removed a breakeven-to-negative
chunk and nearly doubled expectancy at the same total. That is
the entire claim of this candidate, and it is in-sample.

**Concentration disclosure (must travel with this candidate):**
TVSMOTOR (+₹15,287.54) and GLENMARK (+₹11,666.52) together are
**110.8%** of the candidate's Jan–Oct net — more than the whole
total; the remaining 23 stocks net ≈ −₹2,627 combined. ASTRAL
(+₹4,426.39) is third. This is the same concentration disease
as INV-LONG (97% in two names), in slightly worse form, and
breadth sits exactly at the gate minimum. The fresh-window
test exists to judge precisely this.

## Recorded alternates — NOT carried (with reasons)

- **DBL both-directions @ T100/S050**: also passes the full
  gate in Line 1b S3 — 407 trades, +₹18,186.37, halves
  +₹6,501.77 / +₹11,684.60, breadth 10/25, October +₹12,478.18
  — but expectancy is +₹44.68 against the carried candidate's
  +₹182.91, and it reintroduces the SHORT side that both
  Line 1 (INV1) and Line 1b (DBL) show as the weak leg.
  Recorded, not carried.
- **DBL both-directions @ T125/S065**: fails — breadth 8/25
  (376 trades, +₹6,650.43, halves +₹2,176.91 / +₹4,473.52).
  A wider stop does not buy breadth on this condition.
- **DBL LONG-only @ T100/S050** is the carried candidate's
  shadow reading, not a separate candidate.

## Judging rule — fresh window (pre-declared)

- This candidate earns its own frozen fresh-window test
  (window and logging to be set by a separate frozen decision
  after November's judgement — e.g. December 2026), judged on
  the primary exit T125: **positive net with ≥ 10 trades
  upgrades DBL-LONG to a second candidate window; negative net
  kills it.** (Threshold set at 10, not 20: the condition is
  restrictive — 133 qualifying trades in 10 months in-sample,
  41 of them in Jun–Oct — so a single month may fairly produce
  fewer than 20.) A window with < 10 qualifying trades is
  inconclusive.
- No re-tuning of this candidate on Jan–Oct data: the pool,
  the DBL condition, the direction restriction and the exits
  above are frozen as of this file.

Stage work only. Nothing here is adopted; nothing here is a
live-trading instruction.
