# Stocks EQUITY — CANDIDATE SPEC — O2 "11:00 Fade" (ext 25)

**FROZEN 2026-10-31, before December begins. Paper only, no
orders. Real money: ₹0. NO changes during December — any change
to the measurement time, the threshold, the fade direction, the
entry, the exits, the universe, or the cost voids the month as a
hypothesis test.**

**EQUITY CASH intraday only. LONG/SHORT language only — no
options, no premiums. Every rupee figure: provisional per 100
shares, ₹40/trade flat cost.**

## Status — CANDIDATE, and why it exists

This is the **11:00 fade on the 25 large caps**, discovered by
Line O1's October-first scan (1,344 frozen cells) and frozen as
an ext-only system by Line O2 under a gate declared before O2
scored anything (`stocks_O2_frozen.md`, `stocks_O2_report.md`).
It passed all six legs of that gate in-sample. It now faces the
only test that counts: **fresh December 2026 data it was not
selected from.** November's frozen board (N4-V3 primary, INV1
and P2F shadows) is NOT disturbed by this spec; this candidate's
window is December.

## SELECTION DISCLOSURE (part of the frozen record)

**This system was selected from a 1,344-cell October-first scan.
It is that scan's single best ext-universe cell. Its in-sample
numbers are an UPPER BOUND, not an expectation. December is the
real judge.** In-sample average (+₹30,443/month) is also below
the user's ₹50,000/month bar even at face value — the candidate
is carried at its true size.

## The rule — exact (engine-faithful, = Line O2 base cell)

Machinery: `stocks_O2.py` over Line O1's builders
(`stocks_O1.py` / `stocks_tuning_mover.py`); the engine is the
authority.

1. **Universe:** the 25 ext large caps only —
   RELIANCE, TCS, ICICIBANK, INFY, BHARTIARTL, SBIN, LT,
   AXISBANK, KOTAKBANK, BAJFINANCE, HCLTECH, MARUTI, SUNPHARMA,
   TITAN, M&M, ULTRACEMCO, NESTLEIND, POWERGRID, ONGC,
   COALINDIA, JSWSTEEL, GRASIM, CIPLA, DRREDDY, EICHERMOT.
   The home watchlist is NOT part of this system.
2. **Measurement (11:00):** pre-move = close of the last 5-min
   bar with time < 11:00, divided by the open of the day's first
   post-09:30 bar, − 1 (the machinery's `premove` convention).
3. **Qualification:** |pre-move| ≥ **1.0%** on that stock-day.
4. **Direction: FADE** — pre-move positive → **SHORT**;
   pre-move negative → **LONG**.
5. **Entry:** the open of the first bar with time ≥ 11:00 (the
   11:00 bar's open — strictly after the measurement completes).
   **One trade per qualifying stock-day.** No re-entry, no
   signal confirmation, no context filter (all days).
6. **Exits:** target **+1.25%** / stop **−0.65%** from entry
   (mirrored for SHORT), stop checked before target within a
   bar; if neither is touched, exit at the close of the 15:10
   bar (or the last bar at or before 15:10).
7. **Net per trade** = sign × (exit − entry) × 100 shares
   − **₹40** flat cost.

## In-sample record (Jan–Oct 2026, discovery + screen — not proof)

| | |
|---|---|
| Trades | 700 (70/month, ~3.3/trading day) |
| Net | **+₹304,427.01** |
| Halves | Jan–May +₹170,988.68 / Jun–Oct +₹133,438.33 |
| October | +₹98,153.17 |
| Breadth | 17/25 |
| Expectancy | +₹434.90/trade |
| Lag-placebo | +₹38,437.66 (beaten ~7.9×) |
| Ex-top-3 stress | +₹95,157.68 (halves +₹75,169.74 / +₹19,987.94) |
| Winsorised (+₹2,000/stock) | +₹11,638.40 — positive but thin |
| Worst month | July −₹22,467.91 (8 of 10 months positive) |
| Max drawdown | −₹72,977.52 (daily-aggregated) |

Mandatory disclosures:
- **Concentration:** MARUTI +₹91,453.90 and EICHERMOT
  +₹77,319.78 alone are 55.4% of the net; top-3 share 68.7%.
  This is an auto/cement-heavy large-cap phenomenon.
- **The home 25 shows nothing** (same rule: Jan–Oct +₹4,243.18,
  breadth 8/25). The effect is ext-only in-sample.
- Neighbourhood (O2): thr 1.25%, T125/S050 exits, and the
  below-50DMA-day variant also passed the gate; 11:15
  measurement and thr 1.5% failed it. The candidate is the base
  configuration as discovered — no neighbourhood swap is part
  of this freeze.

## December judging rule — pre-registered, judged once at month-end

Judged once, after the last December 2026 trading day, on the
rule exactly as frozen above (December data built the same way:
5-min cache, with any cache-missing days aggregated from 1-min
only if the aggregation validates against a cached overlap day,
as in Line O1/O2):

- **December net positive with ≥ 40 trades:** the candidate is
  **CONFIRMED** — it has survived fresh data at a trade rate
  consistent with its in-sample frequency (70/month expected;
  40 is the pre-set floor for a short/quiet month). Confirmation
  earns the next frozen decision (adoption sizing discussion /
  a second fresh window); it is not by itself an adoption.
- **December net negative with ≥ 40 trades:** the candidate is
  **KILLED** — recorded as a selection artefact of the O1 scan,
  no re-tuning, no threshold/measurement/exit change, no
  universe re-cut after the fact.
- **Fewer than 40 qualifying trades in December:** the test is
  **inconclusive** — neither passed nor failed — and the test
  **extends to January 2027** under these same frozen rules,
  judged at January month-end on the combined Dec+Jan sample
  against the same ≥40-trade / positive-net bar.
- **December net exactly ₹0 with ≥ 40 trades:** not positive,
  so no confirmation; not negative, so no kill — inconclusive,
  extends as above.

**No parameter changes during the test window.** Observations
may be logged; they change nothing until the month-end
judgement.

## Validation of this freeze (2026-10-31)

Line O2's run reproduced Line O1's published anchors to the
paisa before scoring (ext October +₹98,153.17, ext Jan–Sep
+₹206,273.84; home control +₹3,901.89 / +₹341.29), and the
timing audit — built-in counters plus an independent
re-derivation of every trade's qualifier, direction, and entry
bar — showed **0 violations** on all 700 base trades. Nothing
in this spec differs from what was scored.
