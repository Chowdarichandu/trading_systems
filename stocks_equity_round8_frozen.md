# Round 8 — Exit sweep on the structured V5 re-entry pools (R5a / M5 entries) — FROZEN 2026-10-30, BEFORE SCORING

**Status: FROZEN 2026-10-30, before any Round 8 scoring. Paper only,
no orders. Equity cash, LONG/SHORT, no options language.**
**Basis: provisional per 100 shares. Gross = before the frozen
₹40/trade flat cost; net = gross − ₹40/trade. Window Jan–Oct 2026
(203 trading days, October = 1–28 Oct), 25 stocks, data in
`data/progressive/`. N4-V3 and its November spec are NOT touched.**

## Why this round

Rounds 1–7 established: structured V5 re-entry pools carry real
gross edges (₹15–52/trade per 100 shares) that sit near or under the
₹40 frozen cost. The unstructured pool had its target/stop grid
swept (targets 0.5–1.25%, stops 0.4–0.75%); the STRUCTURED pools
below were only ever run at T10/T125 with stop 0.5%. This round
sweeps exits on the structured entries only. Entries do not change.

## Entry pools (identical signal definitions to Rounds 5–7)

Signals: the frozen V5 re-entry signal stream of
`stocks_equity_reentry.py` (`pool_pick` over the v4 + skill_or
detectors, verbatim), chained under the user's re-entry rule: after
a trade exits, the next fresh signal on the same stock the same day
may enter again; one open position per stock at a time; chain
`round` = the entry's sequence number within its stock-day UNDER
THAT CELL'S OWN EXIT RULE (exit timing re-sequences chains, so
rounds are computed per exit cell — this is the tradable form).

- **P1 = R5a entries:** chain round ≤ 2 AND ADR≥3% stock-day.
  ADR = Round 3/6 formula, unchanged: prior-10-trading-day mean of
  (high−low)/close×100 from spot_daily.csv, minimum 5 prior rows,
  trade day excluded; stock-days with no ADR value are excluded.
- **P2 = M5 entries:** chain round ≤ 2 AND entry_time < 10:30
  (recorded 5-minute bar time) AND ADR≥3% stock-day.

### Validation gate (must pass before any Round 8 number is used)

Rebuilding chains at target 1.0% / stop 0.5% and at target 1.25% /
stop 0.5% and applying the pool filters must reproduce the
published Round 6/7 pool figures exactly (trades and net):
- P1 × T125: 1,421 trades, net −₹19,541.85
- P1 × T10: 1,471 trades, net −₹27,493.49
- P2 × T125: 918 trades, net +₹10,657.81
- P2 × T10: 947 trades, net +₹5,772.37
(all provisional per 100 shares). If the gate fails, the round
stops and the failure is reported instead of results.

## Exit grid (the ONLY thing that changes)

Plain exits — stop-first on a same-candle tie, 15:10 square-off at
the candle close, exactly as in the earlier engines' `replay`:

- targets {1.25%, 1.5%, 2.0%} × stops {0.4%, 0.5%, 0.75%} = 9 cells
  per pool. (The 1.25%/0.5% cell is the gate cell above.)

Runner variant (1 per pool), bar-order rules stated exactly:
- Full target +2.0%; partial trigger +1.0%; position 100 shares.
- On each candle, in this order: (1) if the partial has NOT yet
  triggered and the candle touches the initial stop (−0.5%), the
  full 100 shares exit at the stop; (2) else if the partial has NOT
  yet triggered and the candle touches +1.0%, 50 shares book at
  +1.0% and the remaining 50 shares' stop moves to breakeven
  (entry price); the remainder's target/stop are NOT evaluated on
  that same candle — its remaining range is not re-used;
  (3) after the partial, on each later candle: breakeven stop
  first, then the +2.0% target, then 15:10 square-off of the
  remainder at the close.
- If the partial never triggers, the trade is a plain
  target-2.0% / stop-0.5% trade on 100 shares with the same
  stop-first order.
- Gross = 50×(partial exit move) + 50×(remainder exit move) in
  rupees per 100 shares (a plain trade is 100× its move).
- "Target-hit" for the runner = the remainder reached +2.0%.

## Scoring (frozen)

- Every cell × pool: trades, win % (net > 0), target-hit %,
  GROSS expectancy/trade, NET totals at ₹40 for Jan–May, Jun–Oct,
  Jan–Oct and October — all provisional per 100 shares.
- **Survivor rule (unchanged): NET positive at ₹40 in BOTH halves.**
- Any survivor additionally gets: a per-month net table (Jan–Oct)
  and concentration checks — largest single month's share of
  Jan–Oct net, and the top-5 trades' combined share of Jan–Oct
  net. A pass carried by one month (>50% of net) or by its top-5
  trades is flagged as concentrated, not celebrated.
- Cost-realism note (report section, no invented broker data):
  the structured pools' average entry price (per pool, at the
  gate-cell chains), and what the flat ₹40 represents as a % of
  the average one-side 100-share value and of round-trip
  turnover, with the qualitative point that a real all-in
  intraday equity cost has a % component that scales with
  turnover, so the flat-₹40 approximation's accuracy depends on
  share price. No broker rates are quoted or assumed.

## What this round does NOT do

- No new entry signals, no new entry filters, no per-stock
  whitelist, no cost other than the frozen ₹40 for scoring.
- No November-paper creation: a survivor is FLAGGED as earning a
  frozen November/December paper spec; creating schedules/specs
  is a separate step, not part of this round. N4-V3 unchanged.

## Engine and outputs

`stocks_equity_round8.py`; results
`stocks_equity_round8_results.json`; kept-trade dumps
`eq_round8_{P1,P2}_{cell}.csv`; report
`stocks_equity_round8.md`.
