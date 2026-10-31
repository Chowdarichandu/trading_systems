# Stocks EQUITY — Line O1 — FROZEN scan plan (written BEFORE any scanning)

**Frozen: 2026-10-31, before Phase 1 ran.** Equity cash intraday only,
LONG/SHORT. Paper only — real money ₹0, no orders. Every figure:
provisional per 100 shares, ₹40/trade flat cost deducted.

## Mandate

User bar (2026-10-31 09:28 IST): at least ₹50,000/month. Method:
**October 2026 first** (discovery), then **Jan–Sep 2026 validation**
before anything is called real. October-only wins have died before
(V5×T10 October +₹6,502.57 → Jan–Sep −₹178,594.99); an October hit
is a hypothesis, never a result.

## Verdict rules (fixed here, applied in the report header)

- A cell is an **OCTOBER HIT** if its pooled-50 October net ≥ **+₹50,000**.
- A hit is **REAL** only if, on Jan–Sep 2026: net positive in **BOTH**
  halves (Jan–May AND Jun–Sep) **AND** breadth ≥ 35/50 **AND** it beats
  its lag-placebo. Only then is a candidate spec frozen (December
  fresh-window judging; November's frozen board is not disturbed).
- A hit that validates below the ₹50k/month run-rate is reported at
  its true run-rate, plainly.
- If nothing validates: the report says October's ₹50k was not
  honestly reachable in these families, and gives the best validated
  run-rate found.

## Data and October coverage

- 5-min caches `data/progressive/` (home 25) + `data/progressive_ext/`
  (ext 25): October = **Oct 1–28, 18 trading days**.
- Oct 29–30: aggregate from the already-fetched 1-min cache
  `data/1min_stocks_oct2026/<old|ext>/<SYM>.csv` (all 50 stocks
  verified present, full 375-bar days). Aggregation = plain OHLC
  5-min buckets from 09:15. Before use, the aggregation is
  spot-validated against the cached 5-min bars for Oct 28
  (a day present in both). DAYCTX entries for Oct 29/30 are built
  with the frozen re-entry head's own construction (OR from bars
  < 09:30, prev-day daily OHLC, `bias_of(prev)`, event WINDOWS);
  Oct 30's prev-day is Oct 29's aggregated daily.
- Final coverage is stated in the report. If aggregation validation
  fails, October stays Oct 1–28 and that is stated instead.

## Definitions (exact; machinery = stocks_tuning_mover.py / universe)

- **Pre-move** `pm(sym, day, T)` = `M.premove`: close of the last
  5-min bar with time < T, divided by the open of the day's first
  post-09:30 bar (the machinery's own convention), − 1.
- **Qualification:** |pm| ≥ threshold. Move direction = sign(pm).
- **Signal mode `sig` (first-signal-after):** signal search starts at
  the first bar with time ≥ T (honest build, as in Line B5). The
  FIRST V5 pooled signal (frozen `pool_pick` over v4/skor heads) at
  or after T whose direction is accepted is traded: entry at the
  next bar's open. Direction acceptance: `follow` → signal sign =
  move sign; `fade` → signal sign = −move sign. Non-accepted signals
  are skipped (search advances past them). Chain cap **2** trades
  per stock-day; re-entry search resumes at the previous exit bar
  (machinery convention). This is the first-signal variant — the
  first signal is TRADED, not discarded (differs from the retracted
  mover's discard-first rule; that rule is not re-tested here).
- **Signal mode `fixed` (fixed-time):** one trade per qualifying
  stock-day; entry at the open of the first bar with time ≥ T;
  direction = move sign (`follow`) or −move sign (`fade`).
- **Exits** (frozen `replay_plain`, stop checked before target
  within a bar, square-off at the 15:10 bar close):
  T05/S050 → target +0.5% / stop −0.5%; T10/S050 → +1.0% / −0.5%;
  T125/S050 → +1.25% / −0.5%; T125/S065 → +1.25% / −0.65%.
- **Contexts** (filters over the same trades; not separate runs):
  - `all` — every trade.
  - `below50` — trade date D qualifies when Nifty's previous close
    ≤ its 50DMA, using the INV lines' regime map verbatim
    (`stocks_tuning_inv.regime_maps`: prev_close = close(D−1);
    ma50 = mean of the 50 closes ending at D−1; from
    `data/progressive/NIFTY/spot_daily.csv`).
  - `event` — the stock-day's frozen `event_status == event_window`.
  - `noevent` — `event_status == no_event`.
- **Pooled 50** = home trades + ext trades summed; home/ext reported
  alongside. Breadth = stocks with net > 0.

## Phase 1 — October discovery scan (the full grid, nothing else)

- Times T ∈ {09:45, 10:00, 10:30, 11:00, 12:00, 13:00, 14:00}
- Thresholds ∈ {0.5%, 1.0%, 1.5%}
- Direction ∈ {follow, fade}
- Signal mode ∈ {sig, fixed}
- Exits ∈ {T05/S050, T10/S050, T125/S050, T125/S065}
- → 336 base cells × 4 contexts = **1,344 reported cells**.
- Report: every cell with pooled October net ≥ +₹20,000 (near zone),
  plus the best cell of each (mode × direction) family regardless.
  The full grid is saved to `stocks_O1_results.json`.

## Timing audit (both phases, asserted, reported)

For every trade: (1) entry_time ≥ T; (2) in `sig` mode the signal
bar time ≥ T and entry bar is strictly after the signal bar;
(3) pm re-derived from bars with time < T only, and its sign /
threshold test must match the recorded qualification. Any violation
voids the cell. Violation counts are printed in the report.

## Phase 2 — validation (definitions frozen in the addendum below
BEFORE Jan–Sep is touched)

- Take the **top 2 cells** (base × context) by pooled October net.
  Their exact definitions are written into the Phase-2 addendum of
  this file after Phase 1, before any Jan–Sep scoring.
- Score each on **Jan–Sep 2026**: full month table (Jan…Sep),
  halves Jan–May / Jun–Sep, breadth /50, expectancy, plus an
  **October re-check** (must reproduce the Phase-1 number).
- **Lag-placebo:** identical cell except the qualifier is the same
  stock's pre-move on the **previous trading day** (same T and
  threshold; direction from the lagged sign), trades executed on
  the current day; context filters unchanged (below50/event refer
  to the trade day itself). Scored on Jan–Sep, pooled.
- Apply the verdict rules above exactly.

## Phase-2 addendum — top-2 cell definitions

Filled 2026-10-31 after Phase 1, BEFORE any Jan–Sep scoring.
Phase-1 timing audit: 58,494 trades generated, **0 violations**.

Ranking note: the #1 cell's `below50` twin posted the identical
+₹98,494.46 with the identical 231 trades (every qualifying October
trade fell on a below-50DMA day), so it is the same cell in substance
and is not double-counted. The top-2 distinct cells are:

**HIT-1 — `11:00 | thr 1.0% | fade | fixed | T125/S065 | all`**
- Qualify: |pre-move to 11:00| ≥ 1.0% (machinery `premove`
  definition). Enter at the open of the first bar ≥ 11:00 in the
  direction OPPOSITE the pre-move (fade). One trade per stock-day.
- Exits: target +1.25% / stop −0.65%, stop-first, 15:10 square-off.
  No context filter. Pooled 50.
- October (Phase 1): **231 trades, +₹98,494.46** (home +₹341.29 /
  ext +₹98,153.17), breadth 22/50. OCTOBER HIT (≥ +₹50,000).

**HIT-2 — `11:00 | thr 1.0% | fade | fixed | T125/S050 | all`**
- Identical to HIT-1 except the stop is −0.50% (same entries,
  tighter stop). No context filter. Pooled 50.
- October (Phase 1): **231 trades, +₹93,914.68** (home −₹2,534.25 /
  ext +₹96,448.93), breadth 21/50. OCTOBER HIT (≥ +₹50,000).

Phase 2 scores both on Jan–Sep 2026 (months Jan…Sep; halves
Jan–May / Jun–Sep; breadth /50; October re-check) plus the
lag-placebo defined in the frozen plan, exactly as pre-declared.
