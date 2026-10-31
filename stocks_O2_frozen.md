# Stocks EQUITY — Line O2 — FROZEN plan (written BEFORE any O2 scoring)

**Frozen: 2026-10-31, before Line O2 scored a single cell.**
Equity cash intraday only, LONG/SHORT. Paper only — real money ₹0,
no orders. Every figure: provisional per 100 shares, ₹40/trade flat
cost deducted. Window: **Jan–Oct 2026, full** (October = 20 trading
days, Oct 1–30, incl. 29–30 via the validated 1-min aggregation O1
built — see Data).

## What this line is

Line O1 (October-first scan of 1,344 frozen cells) found exactly one
near-validated effect: **the 11:00 fade on the 25 large caps** —
measure a stock's morning move at 11:00; if it has already moved
≥1%, enter at a fixed time AGAINST the move (fade), exits
T125/S065. O1's numbers (pooled 50): October +₹98,494.46, Jan–Sep
+₹210,175.73 with both halves positive and its lag-placebo beaten —
but it **failed O1's pooled breadth leg (31/50)** because the home
25 contributed ~nothing (Jan–Sep home +₹3,901.89 vs ext
+₹206,273.84), and the pooled book is concentrated (MARUTI +
EICHERMOT + M&M = 72.3% of pooled Jan–Sep).

O1's verdict was NO candidate, and O1 explicitly refused to re-cut
the cell to ext-only after the fact. **O2 is the legitimate way to
ask the ext-only question**: a new line, frozen here in advance,
with the ext universe as the system universe from the start, its
own pre-declared gate, and a stress battery. Nothing from O1's
verdict is altered by anything O2 finds.

## SELECTION DISCLOSURE (mandatory, part of the frozen record)

**This system was selected from a 1,344-cell October-first scan
(Line O1). It is the single best cell of that scan on the ext
universe. Every in-sample number in O2 is therefore an UPPER
BOUND, not an expectation. The December fresh window is the real
judge; O2's in-sample gate is a necessary screen, not proof.**

## Definitions (exact; machinery = Line O1 verbatim)

Engine: `stocks_O1.py` builders (`build_cell`, `collect_window`,
`ctx_filter`, `below50`, regime map) over `stocks_tuning_mover.py`.
O2 reuses them unchanged; it does not re-derive the rule.

- **Pre-move** `pm(sym, day, T)` = `M.premove(candles, T)`: close of
  the last 5-min bar with time < T, divided by the open of the day's
  first post-09:30 bar, − 1. (Bars are labelled by start time; for
  T = 11:00 the measurement uses bars up to the 10:55 bar, whose
  close is the 11:00 price.)
- **Qualification:** |pm| ≥ threshold. Move direction = sign(pm).
- **Entry (fixed mode):** the open of the first bar with time ≥ T
  (for T = 11:00: the 11:00 bar's open — strictly after the
  measurement window closes). One trade per qualifying stock-day.
- **Direction: FADE** — trade direction = −sign(pm). A stock up
  ≥ threshold by T is SHORTED; down ≥ threshold is BOUGHT.
- **Exits** (`replay_plain`, stop checked before target within a
  bar, square-off at the 15:10 bar close): T125/S065 → target
  +1.25% / stop −0.65%; T125/S050 → +1.25% / −0.50%; T10/S065 →
  +1.00% / −0.65%.
- **below50 context:** trade date D qualifies when Nifty's previous
  close ≤ its 50DMA (INV regime map verbatim, as in O1:
  `data/progressive/NIFTY/spot_daily.csv`, extended to Oct 30 by
  O1's verified live fetch).

## Data and coverage

- Ext 25: `data/progressive_ext/` via the mover machinery's ext
  namespace. October = Oct 1–28 from the 5-min cache + Oct 29–30
  aggregated from the 1-min cache by O1's `build_extra_ctx`
  (validated in O1: 1,875 bars/universe checked vs cached Oct 28,
  0 mismatches).
- Home 25 (`data/progressive/`): **control read only** — the base
  cell is scored once on home and reported; home is NOT part of
  the system, its gate, or any candidate.

## Cells (the frozen list — no others)

**BASE (O2-BASE):** T = 11:00, threshold 1.0%, fade, fixed entry,
exits T125/S065, context all days, universe ext 25.

**Anchor validation (must run first):** O2-BASE ext slices must
reproduce O1's published numbers or the difference is explained
before anything else is believed:
- ext October = **+₹98,153.17**
- ext Jan–Sep = **+₹206,273.84** (98.1% of pooled +₹210,175.73)
- home control: Jan–Sep +₹3,901.89, October +₹341.29.

**NEIGHBOURHOOD** (one change from base each; the brief enumerates
7 variations — 2 threshold + 2 measurement + 2 exits + 1 context —
and all 7 are frozen here; the brief's "6 cells" count is noted as
an arithmetic slip, the enumerated list governs):
- O2-N1: threshold 1.25%
- O2-N2: threshold 1.5%
- O2-N3: measurement 10:45
- O2-N4: measurement 11:15
- O2-N5: exits T125/S050
- O2-N6: exits T10/S065
- O2-N7: context below50 days only

Neighbourhood cells are sensitivity reads. The candidate, if any,
is judged on the gate below applied to the cell in question; the
base cell is the primary subject.

## Timing audit (asserted in the same run, reported)

For every trade in every cell: (1) O1's built-in audit counters
(entry_time ≥ T; fixed mode has no signal bar) must show **0
violations**; (2) an independent re-derivation from each trade
dump: pm recomputed from bars with time < T only must satisfy
|pm| ≥ threshold and the trade direction must equal −sign(pm),
and entry_time must equal the first bar time ≥ T. Any violation
voids the cell.

## Placebo (base cell)

Lagged qualifier, O1's construction verbatim (`collect_window`,
lag=True): the qualifier is the same stock's pre-move at T = 11:00
on the **previous trading day** (same 1.0% threshold; fade
direction from the lagged sign), trades executed on the current
day with base exits. Scored on ext, Jan–Oct. The base cell must
beat it (higher net).

## Stress battery (on O2-BASE and on any gate-passer)

- **Ex-top-3:** remove the 3 best stocks by net; recompute net
  (total and halves reported).
- **Winsorised:** per-stock net capped at +₹2,000
  (Σ min(stock net, +2000)); recompute total.
- **Month table** Jan…Oct; **worst month** named.
- **Max drawdown:** daily-aggregated net, peak-to-trough of the
  cumulative curve.

## GATE — O2 candidate (ext-only, pre-declared)

A cell is the **O2 CANDIDATE** only if ALL of these hold on the
ext 25, Jan–Oct 2026:
1. Net > 0;
2. BOTH halves > 0 (Jan–May AND Jun–Oct);
3. Ext breadth ≥ 15/25 stocks net-positive;
4. October net > 0;
5. Placebo beaten (base cell; for a neighbourhood passer, its own
   lag-placebo, same construction, must also be beaten — the
   placebo is a control, not a new cell);
6. Ex-top-3 stress net still > 0.

**Pass** → freeze `stocks_O2_candidate_spec.md` with a DECEMBER
2026 fresh-window judging rule (net positive at a pre-stated
minimum trade count derived from the in-sample monthly trade
rate → confirmed candidate; negative → killed; below the count
→ extends). November's frozen board is NOT disturbed.
**Fail** → the report names the leg(s) that killed it and the
effect returns to observation status. No re-cutting (no
sub-universe, no direction split, no exit change) after the fact.
