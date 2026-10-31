# Stocks EQUITY — Line G1 — FROZEN cell plan (written BEFORE any G1 cell is scored)

**Frozen: 2026-10-31.** Equity cash intraday only, LONG/SHORT, no
options language. Paper only — real money ₹0, no orders. Every
figure: provisional per 100 shares, ₹40/trade flat cost deducted.
**Home 25 only.** Jan–Oct 2026 (October full month, Oct 29/30 from
the validated 1-min aggregation, as in Lines O1/H1/M1/M2).

## Question

Line M2 found the H1 October cell's edge lives in ONE joint state:
morning move capped at [0.5%, 1.0%) AND Nifty prior close ≤ 50DMA.
Does that state (or its mirror) revive or strengthen OTHER entry
streams on Chandu's 25 that were flat/weak ungated?

## Machinery (all previously audited, reused verbatim)

- Fixed-time entries, premove, replay: `stocks_H1.build_cell` /
  `collect_window` (the H1 engine; its grid reproduces the home
  11:00-fade October slice +₹341.29 exactly, as in Line H1).
- Regime: `H1.below50(day)` — Nifty prior close ≤ 50DMA, the
  INV/H1 regime map verbatim. **A50 (above50) := NOT below50(day).**
- M2 F4 book: `stocks_M2_F4_trades.csv` (717 trades, anchor
  **+₹42,418.91**, October +₹36,166.23, Jan–May +₹3,003.36,
  Jun–Sep +₹3,249.32 — asserted before use). Its placebo is
  rebuilt with `stocks_M2_fix.collect2` (F4 cfg, lag=True);
  anchor: F4 placebo Jan–Sep = **−₹906.88** (Line M2 record).
- S-a anchor (asserted before use): home 11:00 fade ungated =
  **+₹4,243.18**, 1,073 trades, October +₹341.29, breadth 8/25
  (Line O2 home control record).

## Band-filter exactness note (fixed-time streams)

Fixed-time entries are at most one trade per stock-day and their
entry does not depend on the qualifier beyond qualification
itself; qualification is a pure stock-day property. Filtering the
built trade list by the recorded `premove_pct` band is therefore
identical to a gated rebuild. The same filter applies to the
lag-placebo build (whose recorded premove is the lagged
qualifier), so real and placebo books are treated symmetrically.

## The cells (complete list — nothing else will be scored)

All fixed-time cells: exits **T125/S065** (target +1.25% /
stop −0.65%, stop-first, 15:10 square-off), entry at the open of
the first 5-min bar ≥ measurement time T.

- **SA-ALL** (anchor): 11:00 FADE, |pm| ≥ 1.0%, all days.
- **SA-B50**: SA × below50 days only.
- **SA-A50**: SA × above50 days only (the mirror).
- **SB-ALL**: 10:00 FADE, band 0.5% ≤ |pm| < 1.0%, all days
  (the fade twin of M2's follow discovery).
- **SB-B50**: SB × below50 days only (the M2 state, faded).
- **SC-ALL** (comparison anchor): 10:00 FOLLOW, band
  0.5% ≤ |pm| < 1.0%, all days, fixed-time.
- **SC-A50**: SC × above50 days only (the mirror state M2 did
  not test; M2's follow used signal entries, not fixed-time).
- **SD-EV**: M2 F4 book restricted to event-window days
  (trade's recorded `event` == "event_window").
- **SD-NE**: M2 F4 book restricted to no-event days.

## Placebo (programme convention, per cell, same run)

Qualifier lagged one trading day, scored on **Jan–Sep**, under the
SAME band/state/event restriction as the cell. A cell beats its
placebo iff cell Jan–Sep net > placebo Jan–Sep net.

## Timing audit (same run, per cell)

1. Built-in H1 audit counters (entry_time ≥ T; signal rules)
   — delta per cell.
2. Independent audit on every scored trade: pm re-derived from
   raw bars (trade day; lag day for placebos); threshold/band,
   fade/follow direction vs pm sign, entry bar == first bar ≥ T,
   and the cell's state/event restriction re-verified from source
   data. Any violation voids the cell.

## Gate (per cell, all legs required)

1. Jan–Oct net > 0;
2. Both halves > 0 (Jan–May > 0 AND Jun–Sep > 0);
3. October > 0;
4. Breadth ≥ 15/25 (per-stock full-period net > 0, of 25);
5. Beats own placebo (Jan–Sep);
6. Audit clean (0 violations, both audits).

Passers are frozen in `stocks_G1_candidate_spec.md` with a
December 2026 fresh-window judging rule. Full month tables are
published for EVERY cell; months-green count (of 10) is reported
per cell and 9–10/10 cells are flagged (the user's every-month-
positive spec).

## Disclosure rule (from M2's lesson — mandatory)

M2's gate was itself selected on this same Jan–Oct data. Every
G1 pass is therefore a **provisional December-judged hypothesis,
never a confirmed system**, and the report + candidate spec must
carry that statement verbatim in substance. If nothing passes,
the verdict is that the state gate was an M2-local phenomenon.
