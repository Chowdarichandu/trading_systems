# LINE B5 — FREEZE (written BEFORE any B5 scoring)

Equity cash intraday, LONG/SHORT only, no options language.
Paper only, real money ₹0. All figures provisional per
100 shares, net = gross − ₹40/trade flat. Window Jan–Oct 2026
(Oct = 1–28). POOLED 50 primary; home (original 25) / ext
(new 25) splits reported.

## Why this line exists

Line B4 (`stocks_moverB4_report.md`) proved the B3 candidate's
profit sits in entries placed BEFORE the measurement time that
qualifies the stock-day: the mover engine qualifies a day on
the pre-move through `window_end` (`premove` uses bars with
time < window_end) but then searches the WHOLE day's V5
re-entry signal stream from bar 0 (`build_batt` / B2 `build`
start at index 0). At 11:30, 99.3% of net was pre-measurement.
This line (1) measures exactly how much of the FROZEN
flagship configurations (MOVER-A 10:00, MOVER-B 10:15) was
untradable, and (2) rebuilds the machinery honestly and
re-scores it. No other purpose. No new families.

## Machinery

Engine `stocks_moverB5.py`. Its `build_b5` is `stocks_moverB2.py`'s
`build` copied verbatim (same pick/premove/replay via
`stocks_tuning_mover.py`), with ONE added switch:

- `honest=False` → initial signal-search start = 0 (the leaky
  original; used for validation + Part 1 only).
- `honest=True` → initial signal-search start = the first
  candle index whose time >= window_end. The discarded
  "first signal" is then the first signal at/after the
  measurement time; the traded signal is the next one
  at/after it; re-entry searches proceed exactly as in the
  original builder (restart at the previous exit bar — which
  is necessarily at/after the measurement). Qualification
  (pre-move) is UNCHANGED: bars with time < window_end,
  |pre-move| >= 1.0% — that quantity is genuinely known at
  window_end, since the last included bar closes at
  window_end. If no bar has time >= window_end, no trades.

Everything else is frozen at the flagship parameters unless a
cell says otherwise: threshold 1.0%, V5 re-entry signal
stream, exits T125 (target +1.25% / stop −0.5%, stop checked
before target, 15:10 square-off), chain cap 2, ANY direction.

## Validation gate (must pass before anything is believed)

`build_b5` with honest=False must reproduce, to the paisa:

- MOVER-A (10:00): home 424 chains / 698 trades / +₹84,671.74
  (JM +₹52,884.19, JO +₹31,787.55, Oct +₹16,825.42, breadth
  16/25); ext 199 / 300 / +₹164,483.29 (JM +₹73,142.55,
  JO +₹91,340.74, Oct +₹39,984.55, breadth 22/25); pooled
  623 / 998 / **+₹249,155.03** (JM +₹126,026.74,
  JO +₹123,128.29, Oct +₹56,809.97, breadth 38/50).
- MOVER-B (10:15): home 589 / 941 / +₹169,328.31
  (JM +₹92,266.39, JO +₹77,061.92, Oct +₹36,815.02, breadth
  24/25); ext 328 / 481 / +₹295,288.72 (JM +₹151,540.58,
  JO +₹143,748.14, Oct +₹81,933.52, breadth 25/25); pooled
  917 / 1,422 / **+₹464,617.03** (JM +₹243,806.97,
  JO +₹220,810.06, Oct +₹118,748.54, breadth 49/50);
  pooled max DD −₹17,471.45 (daily-aggregated, risk-card
  method).

If validation fails, the line stops; nothing is scored.

## Part 1 — Leak audit (frozen configurations, NO rule changes)

For MOVER-A (window_end 10:00) and MOVER-B (10:15), on home,
ext and pooled, using the honest=False chains:

- A trade is **pre-measurement** iff its entry_time <
  window_end; **at/after** iff entry_time >= window_end
  (the B4 C4 convention).
- For (a) the full book, (b) the pre-measurement slice,
  (c) the at/after slice, report: chains, trades, net,
  Jan–May net, Jun–Oct net, October net, breadth.
  - Slice "chains" = distinct (date, symbol) pairs
    contributing ≥ 1 trade to the slice (a chain is one
    stock-day; its ≤2 trades share one date, so halves and
    October split identically at trade level and chain
    level).
  - Slice breadth = # symbols whose slice net > 0.
- Also partition the full book's chains into **all-pre**
  (every trade pre-measurement), **all-post** (every trade
  at/after), **mixed**; report chain counts and nets.
- The headline leak share = pre-measurement slice net ÷ full
  book net, stated plainly, per configuration and universe.
  The at/after slice is an UPPER bound on any honest version,
  not the honest rule itself: in a mixed chain the at/after
  trade's existence depends on a pre-measurement trade having
  been taken and exited first, and the honest discard is the
  first signal at/after measurement, not the day's first
  signal. Part 2 computes the honest rule itself.

## Part 2 — Honest rebuild scoring

honest=True, frozen flagship parameters, measurement times
**10:00, 10:15, 10:30, 11:30** — pooled 50 primary, home/ext
splits also reported. Per cell: chains, trades, net,
Jan–May, Jun–Oct, losing months (month table), October,
breadth, expectancy/chain, max DD (daily-aggregated).

Then ONE stack cell: at the **best honest measurement time**
(selection rule frozen here: highest pooled net among the
four honest base cells; tie → the earlier time), apply the
B3 stack honestly rebuilt: **same-direction ON, chain cap 1,
exits T125/S065 (target +1.25% / stop −0.65%)**, honest=True.
Same metrics. No other stack cells. No further tuning.

## Part 3 — Verdict gate (frozen)

An honest configuration (any of the four base cells, or the
stack cell) **passes** iff, pooled 50: Jan–May net > 0 AND
Jun–Oct net > 0 AND breadth ≥ 35/50 AND October net > 0.

- If at least one honest configuration passes → freeze
  `stocks_mover_honest_candidate_spec.md` for the passing
  configuration with the highest pooled net (tie → base cell
  over stack cell, then earlier measurement time), carrying
  a December 2026 fresh-window judging rule mirroring the
  B2 candidate spec's (≥ 80 chains: positive → confirmed
  candidate; negative → killed; fewer / exactly ₹0 →
  inconclusive, extend one month).
- If none passes → the report states plainly that the
  Morning-Mover line is dead in honest form, and what (if
  anything) remains.

## November shadow section (analysis only — this line changes nothing)

The report closes with a short section on the two frozen
November shadow specs (`stocks_morningmover_november_shadow_spec.md`,
`stocks_morningmover_ext_november_shadow_spec.md`), whose
logging machinery is the same leaky whole-day search,
stating a recommendation (re-freeze honest before the
Mon 2026-11-02 launch, leaky variants kept only as labelled
controls — or the alternative) grounded in the Part 1 / 2
numbers. This line itself edits no November spec and no
November log.

## Outputs

- `stocks_moverB5.py`, `stocks_moverB5_results.json`
- Trade dumps: `moverB5_AUDIT_A_trades.csv`,
  `moverB5_AUDIT_B_trades.csv` (with a `slice` column),
  `moverB5_HONEST_<time>_trades.csv`, `moverB5_STACK_trades.csv`
- `stocks_moverB5_report.md` (written incrementally)
- `stocks_mover_honest_candidate_spec.md` — ONLY if the
  Part 3 gate passes.
