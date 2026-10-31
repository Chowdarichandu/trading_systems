# Line S2 — VOLUME-SHOCK ENTRIES — frozen BEFORE scoring (2026-10-31)

Equity cash intraday only, LONG/SHORT. Paper only — real money
₹0, no orders. Every figure provisional per 100 shares, ₹40/trade
cost deducted. Window Jan–Oct 2026 (days as cached: home to
28 Oct, ext to 30 Oct — the price/volume join defines the days).

## Why this line

Volume has only ever been tested as a confirmation gate on other
systems' entries (it hurt N4-V3, EA3). It has never been the
entry signal itself. This line tests it as the signal, under the
controls-first protocol: this freeze precedes any scoring, and
the timing audit + placebo run in the SAME run as first scoring.

## Data (verified before this freeze)

- Price: `data/progressive/` (home 25) + `data/progressive_ext/`
  (ext 25), `spot_5m.csv`.
- Volume: `data/progressive_vol/` + `data/progressive_vol_ext/`,
  `spot_5m_vol.csv`, joined to price on timestamp.
- Verification (2026-10-31, pre-scoring): join coverage in-window
  = 100.00% of price bars in BOTH universes (home 380,616 bars /
  203 days; ext 384,375 bars / 205 days); zero-volume joined bars
  0.73% home / 0.81% ext; open/close agreement between the vol
  file's OHLC and the price cache = 0 mismatches on sampled
  symbols in both universes. Both universes usable.

## The rule (frozen)

Bars are 5-minute, timestamp = bar start. For each stock-day,
scan bars in time order. Bar *i* is a **shock bar** when ALL of:

1. bar time ≥ 09:30 (scan start), and
2. at least 20 bars precede it the same day (i ≥ 20) — the
   binding constraint, so the earliest possible shock bar is the
   day's 21st bar (10:55), and
3. volume(i) ≥ MULT × mean(volume of the 20 bars immediately
   before it, same day), where the prior-20 mean must be > 0
   (a zero-mean window cannot qualify a bar), and
4. the bar's own move qualifies direction: close/open − 1 ≥
   +0.30% → LONG shock; ≤ −0.30% → SHORT shock. (A bar cannot
   be both.)

**Entry:** at the open of bar *i+1* (the bar immediately after
the shock bar), in the shock bar's direction. The shock bar has
fully closed before entry — no intrabar information is used.

**Sequencing:** one position at a time per stock-day. After an
exit at bar *j* (per the frozen replay), scanning resumes at bar
*j+1*. **Max 2 entries per stock-day** (the user's no-cap
philosophy bounded by the frozen test design: cap 2, stated
here, not discovered after the fact). A shock bar at 15:05 or
later cannot produce an entry (no bar after it before the 15:10
square-off bar).

**Exits:** the programme's frozen `replay_plain`
(stocks_tuning_universe.py): stop-first within a bar, square-off
at the 15:10 bar's close.

## Cells (frozen — these three, no others)

| Cell | MULT | Target | Stop |
|---|---|---|---|
| S2-A | 3.0× | +0.50% | −0.50% |
| S2-B | 3.0× | +1.25% | −0.50% |
| S2-C | 4.0× | +1.25% | −0.50% |

S2-A carries the user's small-target style; S2-B the programme
standard; S2-C asks whether a rarer, bigger shock is cleaner.

## Controls (same run as scoring — mandatory)

1. **Timing audit, over ALL trades in ALL cells:** every trade
   must satisfy entry bar index = shock bar index + 1 within its
   stock-day (entry is exactly the next bar's open, shock fully
   closed), and the shock's prior-20 window must lie strictly
   before the shock bar. Any violation aborts the run before
   scores are quoted.
2. **Placebo (best cell only, chosen by pooled net; tie → lower
   cell letter): shifted-volume placebo.** The identical
   machinery, except the volume series is the PREVIOUS trading
   day's (same stock, aligned by bar clock time; a bar whose
   clock time is absent from the previous day cannot qualify),
   while the price-move condition, entries and exits use today.
   A real volume effect must beat this placebo's pooled net.
   If the previous day is unavailable for a stock-day, that
   stock-day is skipped in the placebo only.

## Gate toward candidacy (all legs required)

Pooled 50: Jan–May net > 0 AND Jun–Oct net > 0 AND breadth
≥ 35/50 stocks net-positive AND October net > 0 AND timing
audit clean AND placebo pooled net < the cell's pooled net.

A cell passing every leg is frozen as
`stocks_S2_candidate_spec.md` with a December 2026 fresh-window
judging rule (mirroring the programme pattern: judged once at
December month-end; positive December at the frozen exits with
≥ 40 trades → confirmed candidate earning a further frozen
decision, NOT adoption; negative → killed as an in-sample
artefact; < 40 trades or exactly ₹0 → inconclusive, extends one
further month on the combined sample). A cell failing any leg
is reported with its numbers and closed — no re-tuning inside
this line, no threshold or direction rescue after the fact.

## Reporting

Per cell: pooled (trades, net, expectancy/trade, win %,
Jan–May, Jun–Oct, October, breadth, LONG/SHORT split, best/worst
5 stocks), home and ext splits (trades, net, halves, October,
breadth), the audit result, and — for the best cell — the
placebo's pooled net beside the real one.
