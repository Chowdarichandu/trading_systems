# Round 9 — Ex-ante regime gates on the P2 (M5) V5 re-entry pool — FROZEN 2026-10-30, BEFORE SCORING

**Status: FROZEN 2026-10-30, before any Round 9 scoring. Paper only,
no orders. Equity cash, LONG/SHORT, no options language.**
**Basis: provisional per 100 shares. Gross = before the frozen
₹40/trade flat cost; net = gross − ₹40/trade. Window Jan–Oct 2026
(203 trading days, October = 1–28 Oct), 25 stocks, data in
`data/progressive/`. N4-V3 and its November spec are NOT touched.**

## Why this round

Round 8 established: the P2 pool (V5 re-entry, chain round ≤ 2,
entry before 10:30, ADR≥3% stock-days) at its best exit T125/S050
is net-positive Jun–Oct (+₹15,693.31) and net-negative Jan–May
(−₹5,035.50) — and that half-split holds at EVERY exit in the grid.
The entries' second-half edge and first-half hole are
exit-invariant, so the remaining hypothesis is REGIME: Jan–May's
failure may be concentrated in market/stock states that are
knowable BEFORE the trading day from previous days' data only.
A gate that merely deletes calendar months is FORBIDDEN (that is
fitting). Every gate below is an indicator computed from daily
bars strictly before the trade day, applied identically in both
halves.

## Pool and exits (unchanged from Rounds 6–8)

- Pool = P2 entries exactly, as published: the frozen V5 re-entry
  signal stream of `stocks_equity_reentry.py`, chains rebuilt per
  exit cell (Round 8 machinery, `stocks_equity_round8.py`), kept
  rows = chain round ≤ 2 AND entry_time < 10:30 AND ADR≥3%
  stock-day (Round 3/6 ADR formula, prior-10-day, trade day
  excluded).
- Gates FILTER pool rows. Chain construction is unchanged (a
  dropped round-1 row does not rebuild its round-2 row) — the
  same filter-on-pool method as Rounds 6–8.
- Primary exit: **T125/S050** (target +1.25% / stop −0.5%,
  stop-first tie, 15:10 square-off). Secondary: **T10/S050**
  (+1.0% / −0.5%). Gross and net are both reported; the survivor
  rule uses NET at ₹40.
- **Validation gate (must pass before any Round 9 number is
  used):** rebuilt P2 pools must reproduce Round 8's published
  figures exactly — T125/S050: 918 trades, net +₹10,657.81;
  T10/S050: 947 trades, net +₹5,772.37 (provisional per
  100 shares). If the gate fails, the round stops and reports
  the failure instead of results.

## Regime data (ex-ante, stated exactly)

Daily bars: `data/progressive/<SYM>/spot_daily.csv` (series start
2025-01-01, so all indicators have full history before Jan 2026).
For a trade day D, the "previous bar" is the last daily row with
date < D in that series. An N-day moving average for D is the mean
of closes of the N daily bars ending at the previous bar
(inclusive). No bar dated D or later is ever used. If a required
value cannot be computed, the trade is DROPPED (unclassifiable)
and counted as dropped.

## Gates (each scored separately)

- **G1 NIFTY TREND (direction-agnostic):** keep the trade iff
  Nifty's previous close > Nifty 50DMA. The inverse state
  (previous close ≤ 50DMA) is reported separately as its own
  subset — it is exactly G1's dropped set, shown, not hidden.
- **G2 NIFTY SHORT TREND:** keep iff Nifty's previous close >
  Nifty 20DMA.
- **G3 STOCK TREND ALIGNMENT (per-stock):** LONG trades kept iff
  that stock's previous close > its own 20DMA; SHORT trades kept
  iff previous close < its own 20DMA. Equality → dropped.
- **G4 MARKET VOLATILITY STATE:** Nifty ATR%(D) = mean of
  (high−low)/close×100 over the 10 daily bars ending at the
  previous bar (same formula family as the stock ADR). Its
  expanding distribution = every ATR% value computable for days
  strictly before D (series start 2025; minimum 60 prior values,
  else unclassifiable → dropped; in practice >200 values exist
  before Jan 2026). Percentile(D) = 100 × (share of prior values
  ≤ ATR%(D)). Keep iff Percentile(D) ≤ 75 — i.e. the trade day is
  NOT in the top volatility quartile of its own history to date.
  The top-quartile subset (the dropped set) is reported
  separately. (Interpretation frozen here: "middle band" is
  implemented as the task's parenthetical defines it — top
  quartile excluded; no bottom-quartile exclusion.)
- **G5 DIRECTION-IN-REGIME (full alignment):** LONG trades kept
  iff Nifty previous close > 50DMA; SHORT trades kept iff Nifty
  previous close < 50DMA. Equality → dropped.
- **STACK:** rank the five gates by min(Jan–May net, Jun–Oct net)
  at the primary exit; AND-combine the top two and score the
  stack identically. If fewer than two gates pass the survivor
  rule individually, the stack is still scored and labelled
  exploratory.

## Scoring (frozen)

For every gate (and the stack), at BOTH exits:
- Kept set and dropped set, each with: trades, win % (net > 0),
  target-hit %, GROSS expectancy/trade, NET totals for Jan–May,
  Jun–Oct, Jan–Oct and October — all provisional per 100 shares.
  The dropped set is shown in full: a gate that "works" by
  dropping winners in either half is exposed here.
- Kept share: kept trades as % of the P2 pool, per half.
- **Survivor rule:** a gate survives iff its KEPT set is NET
  positive at ₹40 in BOTH halves at the primary exit AND it
  keeps ≥ 40% of P2 trades in EACH half. (Secondary-exit results
  are reported; they do not create a survivor.)
- A survivor additionally gets concentration checks (largest
  month's share of Jan–Oct net; top-5 trades' share), flagged if
  carried by one month (>50%) or its top 5.

## Diagnosis (report only, no rule built from it)

P2 at T125/S050, Jan–May rows only: net and gross expectancy by
calendar month, by direction (LONG/SHORT), and by stock (all 25,
sorted) — where exactly the first-half hole sits.

## What this round does NOT do

- No calendar/month deletions, no per-stock whitelist, no new
  entries, no new exits, no cost other than the frozen ₹40 for
  scoring. Diagnosis builds no rule.
- No schedules created. A survivor is FLAGGED as earning a frozen
  paper spec for the next available window; creating it is a
  separate step. N4-V3 unchanged.

## Engine and outputs

`stocks_equity_round9.py`; results
`stocks_equity_round9_results.json`; kept/dropped dumps
`eq_round9_P2_{gate}_{kept,dropped}_{T125,T10}.csv`; report
`stocks_equity_round9.md`.
