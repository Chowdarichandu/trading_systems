# Stocks EQUITY — LINE T2: EVENT-AXIS DEEPENING (P2F extensions) — FROZEN SPEC

**FROZEN 2026-10-31 BEFORE any T2 cell is scored. Cells scored in
order T2-A → T2-B → T2-C. No hindsight filters; rejects are
reported, not buried.**

**EQUITY CASH only. LONG/SHORT language only — no options, no
premiums. Paper only, no orders. Real money: ₹0. Every rupee
figure: provisional per 100 shares, ₹40/trade flat cost.**

**Scope note:** the frozen November specs — N4-V3 primary and
the P2F shadow (`stocks_p2f_november_shadow_spec.md`, R+1 entry
at the 2.0% band) — are NOT changed by anything here. T2 builds
candidate variants only, for a December fresh-window decision.

## Common ground (frozen)

- Window: Jan–Oct 2026 (October = 1–28 Oct; 29 Oct absent from
  the 5-min caches, never a zero day). Halves by each trade's own
  trade date: H1 = trade date ≤ 2026-05-31, H2 = ≥ 2026-06-01.
  October slice = trade date in 2026-10.
- Universes, reported SEPARATELY: **HOME 25** (the watchlist in
  `stocks_tuning_event.py`, calendar
  `stock_event_calendar_jan_oct_2026.csv`, cache
  `data/progressive/`) and **POOLED 50** = HOME 25 + EXT 25
  (folders of `data/progressive_ext/`, calendar
  `stock_event_calendar_ext_jan_oct_2026.csv`, cache
  `data/progressive_ext/`). The two symbol sets are disjoint
  (verified at freeze: no name appears in both).
- **P2F candidate construction — verbatim from the frozen P2F
  spec / `stocks_tuning_event.py`:** RESULTS events only
  (`event_type = results`); reaction day R = the calendar
  `reaction_date` when announcement ≤ reaction_date ≤
  announcement + 7 days, else the announcement date; R must lie
  in [2026-01-01, 2026-10-28] and in the stock's own daily data
  with a previous trading day; reaction return =
  close(R)/close(prev trading day) − 1, %, **rounded to 2 dp**;
  threshold test on the rounded |return|; direction = sign of
  the reaction return (LONG if positive, SHORT if negative);
  corporate-action artefacts are traded and NOT excluded
  (verbatim P2F rule — e.g. the VEDL demerger artefact sits
  inside the base anchors).
- **Exit engine (T2-A, T2-B):** the round-5 N4 engine exactly as
  in `stocks_tuning_event.py:replay` — exit scan starts on the
  bar AFTER the entry bar (entry bar = the 09:15 bar of the
  entry day); within a bar the stop is checked before the
  target; else exit at the close of the 15:10 bar (or the last
  bar at/before 15:10). **T125**: target +1.25% / stop −0.5%
  from entry, mirrored for SHORT. Net per trade =
  sign × (exit − entry) × 100 − ₹40.
- **Anchors that must reproduce before any cell is believed**
  (HOME, in-engine regeneration):
  - P2F 2.0% R+1 T125: **48 trades, +₹12,835.88**, halves
    +₹3,498.10 / +₹9,337.78, breadth 14/25.
  - P2F 2.5% R+1 T125: **39 trades, +₹15,489.08**, expectancy
    **+₹397.16**, halves +₹6,702.84 / +₹8,786.24.
  - Cross-check vs Line 3 V2 published HOME bands: 3.0% →
    33 trades / +₹14,231.75; 4.0% → 22 trades / +₹8,399.06.
    (Disclosure: T2-A's HOME cells re-score Line 3 V2's 3.0/4.0
    bands with identical machinery — the new content of T2-A is
    the POOLED-50 scoring and the October slices, which Line 3
    did not publish per band. Any discrepancy vs Line 3 is
    reported as a discrepancy, not rounded away.)

## Timing audit (same run as scoring — controls-first)

Qualifier for every T2 trade = the reaction-day CLOSE (complete
at R's 15:30 close). Entry for every T2 trade = the 09:15 open
of the stated entry day (R+1 for T2-A/T2-C, R+2 for T2-B). The
engine asserts programmatically over ALL trades in ALL cells,
both universes:
`entry_date > R` AND `entry_time == "09:15"` AND
`direction == sign(reaction_ret)` AND `|reaction_ret| ≥ cell
threshold`. Violation count must be **0**; any violation voids
the cell. The audit result is printed in the report next to the
scores, not after them.

## T2-A — MAGNITUDE CURVE at R+1 (2 cells)

P2F exactly as frozen, entry **R+1 09:15 open**, T125 exits,
thresholds **3.0%** and **4.0%**. One change only vs the base:
the threshold.

## T2-B — SECOND-DAY DRIFT (2 cells)

P2F exactly as frozen EXCEPT the entry day: **skip R+1
entirely; enter at the R+2 09:15 open** (R+2 = the stock's
second trading day after R), reaction direction, T125 exits,
thresholds **2.0%** and **2.5%**. Candidates are drawn from the
same base population (which requires R+1 to exist in the data);
a candidate whose R+2 does not exist, falls after 2026-10-28,
or has no bars is dropped and counted.

## T2-C — TWO-DAY HOLD (1 cell) — ⚠ NON-INTRADAY, labelled

This cell BREAKS the intraday-only convention (a position is
held overnight). It is labelled NON-INTRADAY everywhere it
appears and cannot be adopted as an intraday system; it is
scored so the deviation is priced honestly. (Distinct from
Line 3 V3a: band 2.5% not 2.0%, and NO target — stop-only.)

- Population: P2F candidates at the **2.5%** band. Entry
  **R+1 09:15 open**, reaction direction.
- **Stop-only exits:** stop price fixed from entry at
  entry × (1 − sign × 0.5%). NO target on either day.
- Day R+1: scan bars after the entry bar with time ≤ 15:10; if
  the stop is touched (LONG: low ≤ stop; SHORT: high ≥ stop)
  exit AT the stop price on R+1 (`stop`). The 15:10 bar's range
  is checked for the stop before the day ends (mirrors the
  standard engine). If not stopped by the end of the 15:10 bar
  (or the last bar ≤ 15:10), the position is HELD overnight.
- R+2 open: if the R+2 opening bar's open is through the stop
  (LONG: open ≤ stop; SHORT: open ≥ stop) exit AT THE OPEN
  (`gap_stop`).
- Day R+2: scan all bars with time ≤ 15:10; stop touch → exit
  AT the stop price (`stop`). Otherwise exit at the close of
  the 15:10 bar (or last bar ≤ 15:10) on R+2 (`square_off`).
- A candidate whose R+2 does not exist in the data or has no
  bars is dropped and counted. Cost ₹40 flat kept for
  comparability (real overnight charges would differ — flagged,
  not modelled).

## Pass gate (per cell, HOME and POOLED judged separately)

A cell PASSES on a universe iff ALL of:
1. Net > 0 in **both halves** on that universe;
2. **October net > 0** on that universe;
3. Timing audit clean (0 violations);
4. **HOME cells only:** expectancy ≥ **+₹397.16** (P2F-2.5%
   HOME expectancy). Pooled expectancy is reported but is not
   a gate leg (the +₹397.16 bar is a home-basis figure).

A passing cell is frozen as `stocks_T2_candidate_spec.md` with
a December fresh-window judging rule. A cell passing on one
universe only is recorded as passing on that universe only.

## Reporting (every cell, both universes)

Trades, win %, net, H1 net (n), H2 net (n), October net (n),
expectancy ₹/trade, breadth (stocks net-positive / universe
size — untraded stocks count as not positive), top-3 share
(sum of the 3 largest positive per-stock nets ÷ total net;
reported as n/a when total net ≤ 0), direction split.

## Deliverables

- This frozen spec: `stocks_T2_frozen.md`
- Engine: `stocks_T2.py`; results: `stocks_T2_results.json`;
  trade CSVs: `stocks_T2_<cell>_trades.csv` (leg column marks
  HOME / EXT membership for pooled cells).
- Report, written incrementally: `stocks_T2_report.md`
- On a pass only: `stocks_T2_candidate_spec.md`
