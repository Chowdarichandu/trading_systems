# LINE RSI1 — FROZEN SPEC (written BEFORE any scoring, 2026-10-31)

RSI as an entry mechanism on Chandu's own 25 stocks. Never tested in this
programme before (user asked 2026-10-31: "Rsi is working?").
Equity cash, LONG/SHORT language only, no options/premiums. Paper only,
real ₹0. Provisional per 100 shares, net = gross − ₹40/trade.
Universe: HOME 25 only. Window: Jan–Oct 2026 (5-min caches in
data/progressive/; Oct 29–30 from Line O1's validated 1-min aggregation,
via stocks_H1.build_extra_ctx).

## RSI definitions (causal — completed bars only)
- RSI = the programme's own `rsi_wilder` (daytrader_skill_run.py): Wilder
  smoothing, seeded by the simple average of the first `period` changes;
  first value at index `period`.
- INTRADAY RSI(14): computed once per symbol on the CONTINUOUS 5-min close
  series (all trading days Jan–Oct concatenated chronologically, 75 bars/day
  from ctx["raw"], 09:15–15:25). RSI at a bar uses only closes up to and
  including that bar. Crosses are evaluated on in-day bars j = 1..73 using
  the same day's predecessor bar j−1.
- DAILY RSI(2): `rsi_wilder(daily closes, 2)` on the per-symbol daily close
  series (cache daily 2025-01-01→2026-10-28, extended with Oct 29/30 closes
  from the validated 1-min aggregation). The value used for day D is the
  RSI(2) at the close of day D−1 — fully known before D opens.

## Cells (3 mechanisms × 3 exits × 2 contexts = 18)
Entries at the OPEN of the bar after the signal bar. Exits by
stocks_tuning_universe.replay_plain on the day's raw bars; square-off 15:10.
Re-entry: after a trade exits at bar x, the next signal bar must satisfy
j > x; max 4 entries/stock/day (RSI-C: single daily event → max 1/day).

- **RSI-A (intraday reversion):** RSI(14) crosses UP through 30
  (RSI[j−1] ≤ 30 < RSI[j]) → LONG. Crosses DOWN through 70
  (RSI[j−1] ≥ 70 > RSI[j]) → SHORT.
- **RSI-B (intraday continuation):** crosses UP through 50 AND the day's
  move at bar j (close_j / day_open − 1) > 0 → LONG. Crosses DOWN through
  50 AND day move < 0 → SHORT.
- **RSI-C (daily extreme → intraday):** prior-day daily RSI(2) ≤ 10 →
  LONG at the 09:35 bar open; prior-day RSI(2) ≥ 90 → SHORT at 09:35.
  One trade per stock-day.

Exits: T05/S050 (+0.5%/−0.5%), T10/S050 (+1.0%/−0.5%), T125/S065
(+1.25%/−0.65%). Contexts: all days; below50 only (Nifty prior close ≤
50DMA, stocks_H1.below50 — the same map as H1/M2).

## Placebo (same run, per cell)
Identical entries/exits, but the RSI series is shifted ONE TRADING DAY
back: for day D, RSI-A/B signals come from day D−1's RSI(14) values at the
same in-day bar indices, applied to day D's prices (RSI-B's day-move
condition still uses day D's actual move — only the RSI is stale). RSI-C
placebo: bias from RSI(2) as of D−2. The real cell must beat its placebo.

## Timing audit (same run, mechanical)
Every A/B trade: entry bar index == signal bar index + 1 and the signal
RSI uses closes ≤ signal bar close. Every C trade: the daily RSI index
used is strictly before day D. Violations counted across ALL trades
(real + placebo); must be 0.

## Gate (frozen)
A cell is a CANDIDATE only if ALL hold: Jan–Oct net > 0; both halves
(Jan–May AND Jun–Oct) > 0; October > 0; breadth ≥ 15/25; expectancy
≥ +₹100/trade; real net > its placebo net; timing audit clean.
FULL MONTH TABLE published for every cell; any cell with 9–10 of 10
months green is flagged as a month-repair / recursive-engine target even
if another gate leg fails. A passing cell is frozen in
stocks_RSI1_candidate_spec.md with a December 2026 fresh-window judging
rule and noted as an add-component candidate for the recursive engine.
If nothing passes, this line reports RSI's honest ceiling per cell —
no re-tuning of thresholds inside this line.
