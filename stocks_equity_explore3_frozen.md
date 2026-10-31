# Stocks EQUITY — Exploration Round 3 — FROZEN BEFORE SCORING — 2026-10-30

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0.**
**Every rupee figure is provisional per 100 shares, ₹40/trade flat
cost. Portfolio view: UNCAPPED — every qualifying stock trades,
max 1 trade per stock per day. The minimum-2-valuable/day rule is a
floor, never a cap.**

## Question

Round 2 established that V5-stock and (lA)-stock entries with
0.5–1.25% targets have negative Jan–Sep expectancy (no-event gross
is even negative for V5), and event-window days are consistently
the worst days. Frequency is ample (~20 signals/day). This round
tests ONE thing: can a SELECTION LAYER — using only information
knowable before entry — turn the V5 or the Skill entry pool into a
Jan–Oct-positive small-target equity system?

## Pools (unchanged entries, reused engines)

- **V5 pool:** stocks_equity_v5_deep.py signal logic exactly
  (tuning find_signal, entry_mode v4 + skill_or deduped by frozen
  RANK, entry = next candle open after signal).
- **Skill pool:** daytrader_skill_run.find_skill_signal with
  patterns ("or","flag","oversold"), as in
  stocks_equity_systems_oct.py, entry = next candle open.
- Window: Jan–Oct 2026 (Oct = 1–28), 25 stocks,
  data/progressive cache. Oct 29 missing from cache — stated, not
  a zero day.

## Exits (frozen)

- Primary: target +1.0%, stop −0.5% (T10). Secondary: target
  +1.25%, stop −0.5% (T125). Percentage of entry price, direction
  applied. Stop wins a same-candle tie; otherwise 15:10 square-off
  at close. ₹40/trade, per 100 shares provisional.

## Selection families (all knowable before entry)

- **F1 VOLATILITY/ROOM:** keep the signal only if the stock's
  average daily range over the PRIOR 10 trading days
  ((high−low)/prior close, mean) is (a) ≥ 2.0% — F1a — or
  (b) ≥ 3.0% — F1b — of price. Computed strictly from daily bars
  before the trade day.
- **F2 NIFTY REGIME:** Nifty bias for the day = bias_of(Nifty
  previous trading day) (close position in prev-day range:
  bullish ≥ 80%, bearish < 35%, else neutral) — the same bias
  series the base systems already use, applied to Nifty. LONG
  signals only on bullish days, SHORT signals only on bearish
  days; neutral days: no trade.
- **F3 TIMING (diagnostic):** entries with entry_time in
  09:15–11:00 vs 11:00–15:10, scored separately over Jan–Oct and
  per half. A timing edge counts only if positive in BOTH halves.
- **F4 DIRECTION (diagnostic):** LONG-only vs SHORT-only over
  Jan–Oct with both-halves split. A direction rule may only be
  PROPOSED if positive in both halves.
- **F5 EVENT:** no_event days only (event windows from
  stock_event_calendar_jan_oct_2026.csv, ±7 trading days as in
  prior engines), run for the Skill pool and for the F1-filtered
  pools of both systems.
- **F6 STACK:** F1a + no_event + F2 regime alignment, per pool.

## Scoring and verdict rule (frozen)

Every family × pool × exit reports: trades, win %, target-hit %,
net provisional per 100 shares, expectancy, trades/day, and a
split into **Jan–May 2026** and **Jun–Oct 2026** halves (each with
trades and net). A family is INTERESTING only if BOTH halves are
positive — or Jun–Oct positive with Jan–May near-flat (defined:
Jan–May expectancy ≥ −₹10/trade provisional per 100 shares) and a
stated reason. Both-halves-negative = REJECTED, listed as such.
No filter may be invented from the results of this round inside
this round.

## Split-half per-stock persistence (diagnostic only)

From the V5 pool at T10: per-stock net for Jan–May and Jun–Oct,
Pearson correlation across the 25 stocks, count of stocks positive
in both halves / one half / neither. Payers that do not persist
must be reported as non-persistent. NO stock whitelist may be
claimed from one half; a whitelist from both halves is still only
a November-paper question, not a conclusion.

## Outputs

Engine stocks_equity_explore3.py; results
stocks_equity_explore3_results.json; trade CSVs for both pools
(T10) and for F6; persistence CSV; report
stocks_equity_explore3.md. Stage results only — November paper
validates anything that survives both halves.
