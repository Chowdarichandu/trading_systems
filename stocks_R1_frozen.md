# LINE R1 — THE HONEST MOVER NEIGHBOURHOOD — FROZEN WORKPLAN

**Frozen BEFORE any R1 cell is scored** (controls-first protocol,
mandated after the 2026-10-31 Morning-Mover retraction: B4/B5
proved the flagship's profits were a look-ahead artefact — the
engine qualified a stock-day on the move through the measurement
time, then searched the whole day's signal stream from 09:15).
No cell definition below may change after scoring starts. Any
change = a new line, not an edit.

Equity cash intraday, LONG/SHORT only, paper only, real money
₹0. All figures provisional per 100 shares, net = gross −
₹40/trade. Window Jan–Oct 2026 (Oct = 1–28). **Pooled 50
primary** (home = original 25, ext = new 25; splits reported).

## Fixed setup (all cells)

- **Qualifying stock-day:** |pre-move| ≥ 1.0%, where pre-move =
  close of the last 5-min bar with time < measurement, divided
  by the day open, minus 1 (`premise` machinery:
  `stocks_tuning_mover.premove`, identical to every prior mover
  line). Measurement ∈ {**10:00**, **10:15**} — each cell is
  scored at both.
- **Signal stream:** the frozen V5 re-entry heads (home:
  `stocks_equity_reentry.py`; ext:
  `stocks_equity_reentry_ext.py`), via
  `stocks_tuning_mover.pick`. Identical to Lines 2b/5/B2–B5.
- **Honest search start:** the signal search starts at the
  first bar with time ≥ measurement (the `honest=True` switch
  of `stocks_moverB5.build_b5`, validated below). NO part of
  any cell may look at a signal, bar, or exit before the
  measurement time for qualification or entry.
- **Entry mechanics (signal cells):** entry at the open of the
  bar after the signal bar (machinery standard). Exits via
  `replay_plain`: stop checked before target inside a bar
  (stop-first), square-off at the 15:10 bar close.
- **Anchor validation (must pass before scoring):** the B5
  honest second-signal machinery must reproduce, pooled 50:
  10:00 → 614 chains / 946 trades / **−₹117,200.13**;
  10:15 → 894 chains / 1,299 trades / **−₹167,156.86**.
  If either fails, the line aborts — no R1 number is quoted.

## Cells

### R1-A — FIRST-SIGNAL (any direction)
On a qualifying stock-day: trade the **first** V5 signal found
at/after the measurement (NO discard — this is the cell B5
never tested; B5's honest cells all discarded the first
post-measurement signal). Any direction. After the trade
exits, re-enter on the next signal at/after the exit bar,
**cap 2 trades** per stock-day. Exits: **T125/S050** (target
+1.25% / stop −0.50%), 15:10 square-off.

### R1-B — FIRST-SIGNAL SAME-DIRECTION
As R1-A, except a signal is only eligible if its direction
matches the pre-move's sign (LONG if pre-move > 0, SHORT if
< 0). Non-matching signals are skipped (search continues from
the next bar; they do not count as the first signal and do not
end the day). The direction rule applies to the re-entry leg
identically. Cap 2, exits T125/S050.

### R1-C — FIXED-TIME SMALL-TARGET (no signals)
On a qualifying stock-day: enter **once**, at the open of the
bar labelled measurement+5 min ("10:05" for the 10:00
measurement; "10:20" for 10:15), in the **pre-move's
direction** (LONG if up, SHORT if down). No signal stream is
consulted. Two exit sub-cells, scored separately:
- **R1-C1:** target +0.50% / stop −0.50%
- **R1-C2:** target +1.00% / stop −0.50%
Square-off 15:10 (machinery standard). If no bar exists
at/after measurement+5, no trade.

### R1-D — SECOND-SIGNAL ANCHORS (from Line B5, not re-run)
The honest second-signal cells (discard first post-measurement
signal, trade the next), T125/S050, cap 2, any direction —
already scored by B5 and carried into the R1 table for
comparison only: 10:00 pooled **−₹117,200.13** (614 chains /
946 trades, Jan–May −₹74,380.44 / Jun–Oct −₹42,819.69, Oct
−₹18,487.89, breadth 15/50); 10:15 pooled **−₹167,156.86**
(894 / 1,299, −₹100,793.47 / −₹66,363.39, Oct −₹29,590.72,
breadth 17/50). The anchor-validation run above re-derives
them in-process as the audit trail.

## Controls — SAME RUN as first scoring (non-negotiable)

1. **Leak audit (programmatic, printed):** for every cell ×
   measurement × universe, assert **every** trade's
   `entry_time ≥ measurement time` (string compare on HH:MM).
   Report trades checked, violations found, and the minimum
   entry_time seen. Any violation → the cell is void, quoted
   nowhere, and the line stops to diagnose.
2. **Placebo (best cell only):** "best" = highest pooled net
   among R1-A, R1-B, R1-C1, R1-C2 across both measurements;
   tie-break by frozen order A < B < C1 < C2, then 10:00
   before 10:15. Re-run that exact cell with qualification
   AND direction taken from **yesterday's** pre-move: the
   previous trading day in the universe's day list, same
   symbol, same measurement window, |pm_yesterday| ≥ 1.0%,
   direction = sign(pm_yesterday). Today's bars/signals/entry
   mechanics unchanged (entries still at/after today's
   measurement). If yesterday's ctx or pre-move is missing,
   the stock-day does not qualify. A real effect must beat
   its placebo clearly (placebo pooled net < cell pooled net,
   and the placebo must not itself pass the gate).

## Gate toward candidacy

A cell (at a stated measurement) is a candidate only if ALL
hold on pooled 50: **Jan–May > 0 AND Jun–Oct > 0 AND breadth
≥ 35/50 AND October > 0 AND leak audit clean AND (for the
best cell) placebo beaten.** A passing cell is frozen as
`stocks_R1_candidate_spec.md` with a December fresh-window
judging rule (mirror of the standing convention: frozen rule,
no re-tuning on the fresh window; judged on net-positive
fresh month with adequate chain count). If no cell passes,
the report says so plainly and states the neighbourhood's
honest ceiling (the best cell's pooled net and per-month
average vs the ~₹25k/month target bar).

## Reporting

Every cell × measurement: chains, trades, net, Jan–May,
Jun–Oct, October, breadth, expectancy per chain and per trade,
home/ext nets — reported regardless of sign. Target bar for
context: ~₹25k/month pooled per 100 shares ≈ +₹250,000 over
the 10-month window.
