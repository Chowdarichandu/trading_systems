# Stocks EQUITY — RE-ENTRY re-run — FROZEN 2026-10-30, BEFORE SCORING

**User rule 2026-10-30 19:47 IST, binding and superseding all prior
caps for stocks: stocks have NO trade-count restriction.** A stock
that hits its target can be traded AGAIN the same day when it sets
up again — re-entry is the norm for equity. The one-and-done rule
belonged to index options (premium decay) and was wrongly applied
to stocks. With ~25–30 watchlist stocks, dozens of entries per day
are expected. **NO portfolio cap, NO per-stock/day cap.** The
minimum-2-valuable/day figure was a floor, never a cap.

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0.**
**Every rupee figure is provisional per 100 shares, ₹40/trade flat
cost, labelled in every figure sentence.**

Window: Jan–Oct 2026 (Oct = 1–28 Oct in cache, 18 trading days;
29 Oct missing from cache — stated, not a zero day). Universe:
25 screenshot stocks, data `data/progressive/`.

## Why this re-run exists

All prior equity small-target verdicts (V5 / Skill / (lA) ×
0.5–1.25% targets, Rounds 1–3) were computed under a construction
limit of max 1 trade per stock per day — the signal engines only
ever took the earliest signal of each stock-day. Those verdicts do
not stand until re-checked under the user's actual rule: re-entry.
This run re-scores the same signal sources, same exits, with
re-entry enabled, and compares expectancy per trade (not just
totals) against the 1-per-day numbers. Re-entry multiplies trades
AND costs; a verdict flips only if expectancy/half-signs change,
not if a loss merely scales.

N4 / N4-V3 event-reaction is NOT part of this re-run (day-level
event trigger, one reaction move per event by construction); its
November paper spec stays exactly as frozen.

## Signal sources (faithful reuse, streaming form)

The base detectors (`daytrader_cash_tuning.find_signal`,
`daytrader_skill_run.find_skill_signal`) return only the first
signal of a day. For this run they are wrapped in streaming form:
the identical per-candle conditions, evaluated with FULL day
context (09:15–09:30 OR, previous-day high/close/low, day bias,
and the detectors' internal day state — reclaim level, bounce
flag, flag windows, RSI series — all computed from the day open),
but the scan returns the first signal whose signal candle is at or
after a given start candle. Detector priority inside a candle is
unchanged (V4: setup4 pullback → setup4 reclaim → setup2 → setup3;
Skill: OR pattern has priority over flag/oversold within a round,
exactly as the original function returns).

- **V5-stock:** per round, the next V4-mode signal and the next
  Skill-OR-mode signal from the round start; pooled and deduped by
  the frozen rank (setup rank desc — setup4=3, setup3=2, setup2=1,
  skill_or=0 — then prospective T10 net desc, then earlier signal),
  exactly as in the prior engines. The winning candidate is traded;
  the losing candidate is NOT blacklisted — if its signal candle is
  at/after the next round's start and the detector still fires
  there, it may be taken in a later round.
- **Skill:** per round, `find_skill_signal` streaming form with
  patterns (or, flag, oversold), same priority as the original.
- **(lA)-stock:** Nifty's first OR break of the day (OR 09:15–09:30,
  first close beyond OR after 09:30, break time and direction fixed
  for the day, as in prior engines). Per round, the earliest pooled
  V4 / Skill-OR candidate with signal time ≥ Nifty break time and
  ≤ 11:30, in the SAME direction as Nifty's break. (lA) re-entry =
  the next such candidate after the previous (lA) trade exits.
  Morning legs only, as before (the (lA) afternoon re-entry leg of
  the index design is not part of the frozen stock adaptation).
- **Volrix-stock: SKIPPED, stated reason.** Its trigger is the
  stock's own previous-day close ≤ −2.0% and its entry is the next
  session's 09:15 open, with a 10-session cooldown — it is one-shot
  per trigger day by construction; its signal cannot recur
  intraday, so there is nothing to re-enter.

## Re-entry mechanics (frozen)

- One open position per stock at a time (per system): no
  overlapping trades on the same stock within a system.
- A round starts at candle index `start` (0 for the first round).
  The detector returns the first signal with signal-candle index
  ≥ start. Entry = open of the candle AFTER the signal candle.
- After a trade exits on candle j (target, stop, or 15:10
  square-off), the next round's start = j: the next signal must
  have its signal candle at or after the exit candle. No re-entry
  on the same signal candle. A signal candle equal to the exit
  candle enters at the following candle's open, so trades never
  overlap.
- No limit on entries per stock per day, per system per day, or
  portfolio per day.
- Each exit variant runs its OWN sequence: exit times differ by
  variant, so the re-entry chain for T05, T10 and T125 is generated
  independently per variant.

## Exits (frozen, unchanged from prior rounds)

- **T05:** target = entry ± 0.5%, stop = entry ∓ 0.5%.
- **T10:** target = entry ± 1.0%, stop = entry ∓ 0.5%.
- **T125:** target = entry ± 1.25%, stop = entry ∓ 0.5%.
- LONG uses +, SHORT uses −. First hit on 5-min candles wins; if
  stop and target are both hit in the same candle, STOP first
  (conservative). Otherwise square off at the 15:10 candle close
  (last candle if 15:10 absent).
- Net per trade (provisional per 100 shares) = direction ×
  (exit − entry) × 100 − ₹40.

## Events

Every trade tagged `event_window` / `no_event` from
`stock_event_calendar_jan_oct_2026.csv` using the frozen gate-v1
window (±7 trading days around event / effective reaction date,
same code as prior engines). Every system × exit is reported
all-days AND no-event-only.

## Scoring and comparison (frozen)

- Periods: Jan–Oct total, halves Jan–May / Jun–Oct, and October
  alone. Survivor rule unchanged: a system × exit is a survivor
  only if BOTH halves are net positive (provisional per 100
  shares). No-event-only is judged by the same rule, separately.
- Entries/day distribution per system × exit: mean entries/day
  over the 203 trading days, max single-day entries, count of days
  with ≥30 entries, and mean entries per stock-day traded.
- **Validation gate (must pass before any number is reported):**
  the same engine run with re-entry DISABLED (first trade per
  stock-day only) must reproduce the published Round-3 base
  numbers for V5 × T10, V5 × T125, Skill × T10, Skill × T125
  (Jan–Oct, all-days) to the paisa. If it does not, the streaming
  wrapper is wrong and the run is void.
- Comparison: every re-entry result is shown beside its
  1-per-day result (same engine, re-entry off — cross-checked
  against the published figures above where they exist) with
  expectancy per trade in both modes. The report must state
  plainly, per system, whether re-entry flips the verdict or
  merely scales the outcome.

## Outputs

Engine `stocks_equity_reentry.py`; results
`stocks_equity_reentry_results.json`; trade CSVs per system × exit
(re-entry mode) plus the re-entry-off baseline CSVs for V5/Skill;
report `stocks_equity_reentry.md`. Stage results only — nothing is
adopted on Jan–Oct in-sample data; November paper validates
anything that survives both halves.
