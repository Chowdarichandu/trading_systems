# Stocks EQUITY — Line H1 — FROZEN scan plan (written BEFORE any scanning)

**Frozen: 2026-10-31, before Phase 1 ran.** Equity cash intraday only,
LONG/SHORT. Paper only — real money ₹0, no orders. Every figure:
provisional per 100 shares, ₹40/trade flat cost deducted.

## Mandate

User scope directive (2026-10-31 11:32 IST): "Run only on my stocks."
The hunt is restricted to **Chandu's own 25-stock watchlist (the home
25)**. User bar: at least ₹50,000/month, **October 2026 first**
(discovery), then **Jan–Sep 2026 validation** before anything is
called real. This line follows the Line O1 protocol exactly, home
universe only. **No ext, no pooled numbers anywhere in this line's
report.**

Known home facts (given, not re-discovered): the 11:00 fade is flat
at home (+₹4,243.18 Jan–Oct); the verified home systems are INV-LONG
+₹24,185.73, N4-V3 +₹7,990.43, P2F 2.5% +₹15,489.08, with Octobers
+₹7,691.08 / −₹530.69 / −₹315.00 — October was hard for all of them.
October-only wins have died before (V5×T10 October +₹6,502.57 →
Jan–Sep −₹178,594.99); an October hit is a hypothesis, never a
result.

## Verdict rules (fixed here, applied in the report header)

- A cell is an **OCTOBER HIT** if its home October net ≥ **+₹50,000**.
- A hit is **REAL** only if, on Jan–Sep 2026: net positive in **BOTH**
  halves (Jan–May AND Jun–Sep) **AND** breadth ≥ 15/25 **AND** it
  beats its lag-placebo. Only then is a candidate spec frozen
  (`stocks_H1_candidate_spec.md`, December fresh-window judging;
  November's frozen board is not disturbed).
- A hit that validates below the ₹50k/month run-rate is reported at
  its true run-rate, plainly.
- If nothing validates: the report states October's honest ceiling
  on his 25 and the best validated run-rate found — no dressing up.

## Data and October coverage

- 5-min cache `data/progressive/` (home 25): October = **Oct 1–28,
  18 trading days**.
- Oct 29–30: aggregate from the already-fetched 1-min cache
  `data/1min_stocks_oct2026/old/<SYM>.csv` (all 25 stocks, full
  375-bar days), exactly as in Line O1. Aggregation = plain OHLC
  5-min buckets from 09:15, spot-validated against the cached 5-min
  bars for Oct 28 before use (O1's validation: 1,875 bars, 0
  mismatches; H1 re-runs the same check in its own prep and reports
  it). DAYCTX entries for Oct 29/30 are built with the frozen
  re-entry head's own construction (OR from bars < 09:30, prev-day
  daily OHLC, `bias_of(prev)`, event WINDOWS); Oct 30's prev-day is
  Oct 29's aggregated daily.
- Final coverage is stated in the report. If aggregation validation
  fails, October stays Oct 1–28 and that is stated instead.

## Definitions (exact; machinery = stocks_tuning_mover.py, home head)

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
  (machinery convention). The first signal is TRADED, not discarded
  (differs from the retracted mover's discard-first rule; that rule
  is not re-tested here).
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
    `data/progressive/NIFTY/spot_daily.csv`, extended to Oct 29/30
    with live-fetched closes verified against the cached Oct 28
    close, exactly as Line O1 did).
  - `event` — the stock-day's frozen `event_status == event_window`.
  - `noevent` — `event_status == no_event`.
- **Breadth** = home stocks with net > 0, out of 25.

## Phase 1 — October discovery scan (the full grid, nothing else)

- Times T ∈ {09:45, 10:00, 10:30, 11:00, 11:30, 12:00, 13:00, 14:00}
- Thresholds ∈ {0.5%, 1.0%, 1.5%}
- Direction ∈ {follow, fade}
- Signal mode ∈ {sig, fixed}
- Exits ∈ {T05/S050, T10/S050, T125/S050, T125/S065}
- → 384 base cells × 4 contexts = **1,536 reported cells**.
- Report: every cell with home October net ≥ +₹20,000 (near zone),
  plus the best cell of each (mode × direction) family regardless.
  The full grid is saved to `stocks_H1_results.json`.

## Timing audit (both phases, asserted, reported)

For every trade generated: (1) entry_time ≥ T; (2) in `sig` mode the
signal bar time ≥ T and the entry bar is strictly after the signal
bar; (3) the qualification uses `M.premove`, which reads only bars
with time < T. Violations are counted by the engine as it builds
(assertion counters, printed in the report); any violation voids
the affected cell.

## Phase 2 — validation (definitions frozen in the addendum below
BEFORE Jan–Sep is touched)

- Take the **top 2 distinct cells** (base × context) by home October
  net (a context twin producing the identical October trade set as
  the #1 cell is the same cell in substance and is not
  double-counted — pass to the next distinct cell). Their exact
  definitions are written into the Phase-2 addendum of this file
  after Phase 1, before any Jan–Sep scoring. If fewer than 2 cells
  reach the near zone, take what exists and say so.
- Score each on **Jan–Sep 2026**: full month table (Jan…Sep),
  halves Jan–May / Jun–Sep, breadth /25, expectancy, plus an
  **October re-check** (must reproduce the Phase-1 number).
- **Lag-placebo:** identical cell except the qualifier is the same
  stock's pre-move on the **previous trading day** (same T and
  threshold; direction from the lagged sign), trades executed on
  the current day; context filters unchanged (below50/event refer
  to the trade day itself). Scored on Jan–Sep.
- Apply the verdict rules above exactly.

## Phase-2 addendum — top-2 cell definitions

Filled 2026-10-31 after Phase 1, BEFORE any Jan–Sep scoring.
Phase-1 timing audit: 37,767 trades generated, **0 violations**.
**Phase 1 found ZERO October hits** — no cell reached +₹50,000.
October's best cell on his 25 is +₹34,124.43; that is the month's
honest ceiling in this grid, stated plainly. Per the frozen plan,
the top-2 distinct cells are still validated (a context twin with
the identical October trade set is the same cell in substance —
the `below50` twins of both cells below posted identical trades
and nets, because every qualifying October trade in them fell on a
below-50DMA day; they are not double-counted).

**HIT-1 — `10:00 | thr 0.5% | follow | sig | T125/S065 | all`**
- Qualify: |pre-move to 10:00| ≥ 0.5% (machinery `premove`
  definition). Trade the FIRST V5 pooled signal at/after 10:00
  whose direction matches the pre-move's sign (follow); entry at
  the next bar's open; chain cap 2 per stock-day, re-entry search
  resumes at the previous exit bar.
- Exits: target +1.25% / stop −0.65%, stop-first, 15:10
  square-off. No context filter. Home 25.
- October (Phase 1): **182 trades, +₹34,124.43**, breadth 19/25.
  NOT an October hit (< +₹50,000) — validated as the month's best.

**HIT-2 — `09:45 | thr 0.5% | follow | fixed | T125/S065 | noevent`**
- Qualify: |pre-move to 09:45| ≥ 0.5%. Enter at the open of the
  first bar ≥ 09:45 in the pre-move's direction (follow). One
  trade per stock-day. Only stock-days whose frozen event status
  is `no_event`.
- Exits: target +1.25% / stop −0.65%, stop-first, 15:10
  square-off. Home 25.
- October (Phase 1): **92 trades, +₹24,380.09**, breadth 14/25.
  NOT an October hit — validated as the month's #2 distinct cell.

Phase 2 scores both on Jan–Sep 2026 (months Jan…Sep; halves
Jan–May / Jun–Sep; breadth /25; October re-check) plus the
lag-placebo defined in the frozen plan, exactly as pre-declared.
REAL gate (frozen): both halves > 0 AND breadth ≥ 15/25 AND
placebo beaten.

