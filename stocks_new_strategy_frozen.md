# NEW STOCK STRATEGY — three invented mechanisms — FROZEN 2026-10-30 (night), BEFORE SCORING of Mechanisms 2–3 and of M1 families F9–F10

**Invented from scratch per the user's mandate. Equity cash intraday,
LONG/SHORT, paper only, no orders, real money ₹0. All rupee figures
provisional per 100 shares, ₹40/trade. Window Jan–Oct 2026 (Oct 1–28),
25 stocks, 203 trading days, `data/progressive` 5-min cache.
NOTE: the cache has OHLC only — NO volume column exists, so no
volume-based mechanism is possible on this data (checked 2026-10-30).**

## User's correction (2026-10-30 23:30 IST), verbatim in substance

"I told invent a new which works with all the stocks." The HDFC
breakout story was ONLY an example of the style — small targets,
trailing, repeat entries on the same stock in a day, hunting. The
strategy must NOT be anchored on the breakout trigger just because
the example mentioned one.

## Pass gates for EVERY mechanism (both must hold)

1. **Both halves**: net after ₹40 positive in Jan–May AND Jun–Oct.
2. **Breadth (the user's "works with all the stocks")**: report the
   number of the 25 stocks individually net-positive, the share of
   total net contributed by the top-3 stocks, and the worst-5 stocks.
   A mechanism that only works on a few stocks FAILS even if gate 1
   passes, and is labelled exactly that.

Style properties kept across mechanisms where the design allows:
small targets in the 0.5–1.25% zone, trailing variants, repeat entries
the same day on the same stock (one open position per stock at a time,
no other caps except where a family states a chain cap).

---

## MECHANISM 1 — "EXTREME-HUNT" (breakout / trail / re-entry) — candidate, not "the" strategy

Full spec: `stocks_hunt1_frozen.md` (frozen before its scoring).
Rolling day-so-far extreme close breakout, trail exit (activate +0.5%,
trail 0.35%), re-entry on each fresh extreme close, cap 4 (variants:
fixed exits, 60-min-range trigger, uncapped, stop-out rule, ADR≥2%
filter, 14:30 cutoff, reclaim re-entries). Families F0–F8 scored
under that spec; results in the report.

**Diagnosis-driven M1 families frozen HERE, before their runs** (from
F0's diagnostics: marginal-clearance breakouts are the worst cohort,
gross expectancy rises with clearance; the trail books +₹428 gross/trade
on trail-stop exits while hard stops bleed −₹473 gross/trade):
- **F9**: F0 + clearance filter — LONG close must be ≥ level × 1.001
  (0.10% clearance), SHORT close ≤ level × 0.999.
- **F10**: F0 + wider trail — activation +0.75%, trail distance 0.50%,
  initial stop −0.5% unchanged.

## MECHANISM 2 — "LADDER" (momentum-step laddering from the day anchor) — NEW, frozen here

Structurally different from M1: entries are keyed to a fixed % grid
from the day's anchor, exits are keyed to grid retracement — no
day-extreme trigger, no fixed % target in the primary variant.

- **Anchor** = open of the 09:15 bar. **Step** = 0.4%. Band index of a
  price P = floor( ln(P/anchor) / ln(1.004) ) (negative below anchor).
- Seed: day band-high / band-low from closes of bars before 09:45.
- **Entry**: a close (bar starting ≥09:45) whose band index exceeds the
  day band-high → LONG at that close (entry band = that index); band
  index below the day band-low → SHORT. One position at a time; chain
  cap 6/stock/day (variant L-b: cap 4).
- **Primary exit (grid retrace)**: from the bar after entry — exit at
  the close of the first bar whose band index is ≤ entry_band − 2
  (LONG; ≥ entry_band + 2 for SHORT). **Hard stop** −0.6% from entry,
  intrabar, stop-first (exit at stop or open if through). Square-off
  at the 15:10 bar close. No entries after the 15:05 bar.
- **Variant L-trail**: same entries, M1 trail exit instead (activate
  +0.5%, distance 0.35%, initial stop −0.5%).

## MECHANISM 3 — "SNAP" (climax-stretch fade with reversal confirmation) — NEW, frozen here

Structurally opposite to M1/M2: it fades an intraday climax stretch,
but only after the stretch stalls — mean-reversion with confirmation,
not blind fading. Uses the session average price SAP = running mean
of typical price (H+L+C)/3 over all bars BEFORE the current bar
(unweighted — no volume exists in the cache).

- **Stretch event** (bar i, start ≥09:45, at least 6 prior bars): the
  bar's high is ≥ 1.2% above SAP_i (up-stretch) AND the bar's range is
  ≥ 1.5× the mean range of all prior bars today. Extreme = that high.
  Mirror: low ≥ 1.2% below SAP_i (down-stretch), extreme = that low.
- **Confirmation / entry**: the first later bar j that closes below
  its open AND below bar i's close (up-stretch) → SHORT at bar j's
  close. Mirror for LONG. If no confirmation bar by 14:30, no trade.
- **Exit (primary S-a)**: target +0.75% from entry in the fade
  direction, stop = stretch extreme ∓ 0.3% beyond it (for a SHORT:
  stop = extreme × 1.003). Stop checked first, exit at stop/target or
  the open if through; square-off 15:10 close. No entries after 15:05.
- **Variant S-b**: target = halfway back from entry toward SAP at
  entry (target price = entry − 0.5·(entry − SAP) for a SHORT; skip
  the trade if that target is < 0.4% away), same stop.
- **Re-entry**: after any exit, a FRESH stretch event (after the exit
  bar) can generate the next entry; chain cap 2/stock/day (variant
  S-cap4: cap 4).

## Reporting (frozen)

Per mechanism and family: trades, win%, net ₹ provisional per 100
shares, expectancy, trades/day, both halves, October alone, chain-round
expectancy, LONG/SHORT split, event-window split, and the BREADTH
block: # stocks net-positive /25, top-3 share of net, worst-5 stocks.
Verdicts must apply BOTH pass gates. Near-misses report breakeven
cost/trade. Nothing is adopted on Jan–Oct alone; a double-pass earns a
frozen November/December paper spec.

## ADDENDUM — diagnosis-driven families, frozen BEFORE their runs (2026-10-30 night, after L/S base scoring)

Diagnosis: (i) LADDER entries capture real drift — trades surviving to
square-off average +₹689/+₹506 gross per trade (JM/JO) — but the
grid-retrace exit (−₹451/−₹433 gross) and the −0.6% hard stop
(−₹536/−₹553 gross) churn them out; (ii) SNAP fades get run over —
480 stops (−₹590 gross) vs 340 targets (+₹682 gross): climax stretches
CONTINUE more than they snap on this universe.
- **L-c**: LADDER entries (cap 6), exit = square-off only, hard stop
  −1.0% (disaster protection), no grid retrace.
- **L-d**: LADDER entries (cap 6), exit = trail with initial stop
  −1.0%, activation +1.0%, trail distance 0.50%.
- **S-f (SURGE-FOLLOW)**: SNAP's stretch event + confirmation in the
  stretch direction (first later bar closing beyond the stretch bar's
  close, in-direction close) → enter WITH the stretch; M1 trail exit
  (init −0.5%, act +0.5%, dist 0.35%); chain cap 2; square-off 15:10.

---

## PART 2 — VOLUME AXIS — FROZEN 2026-10-30 (night), BEFORE ANY PART 2 SCORING

Part 1 established that price-structure entries alone fail both gates.
Part 2 thesis: the entries were blind to participation. Data:
`data/progressive_vol/<SYM>/spot_5m_vol.csv` — 5-min candles fetched
fresh from the Upstox v3 historical endpoint WITH the volume column
(the original progressive fetch discarded it), Jan–Oct 2026, 25
stocks. Verification (coverage, zero-volume share, OHLC match vs the
Part 1 cache) is reported in the report's Part 2 verification section;
scoring uses a day only when its volume series exists.

**Volume ratio (all Part 2 mechanisms)**: for bar i of a stock-day,
vr(i) = volume(i) / median(volume of the 20 bars immediately before i
on the same stock-day). Bars with fewer than 20 prior bars today have
no ratio and cannot be signal bars.

- **V1 VOLUME-CONFIRMED HUNT**: EXTREME-HUNT F0 rules exactly (rolling
  day-so-far extreme close breakout from 09:45, trail exit act +0.5% /
  dist 0.35% / initial stop −0.5%, re-entry, chain cap 4), PLUS the
  entry is taken only if the signal candle's vr ≥ 1.5 (variant V1a)
  or ≥ 2.0 (variant V1b). A breakout candle failing the volume bar is
  skipped (the level/extremes keep updating as in F0; the next fresh
  extreme close can still trigger).
- **V2 VOLUME SURGE FOLLOW** (new mechanism): signal bar i (start
  ≥09:45, ≥20 prior bars today) with vr(i) ≥ 3.0, range
  (high−low)/close ≥ 0.4%, and close in the top quartile of its range
  (LONG) or bottom quartile (SHORT): (close−low)/(high−low) ≥ 0.75 or
  ≤ 0.25. Entry at the OPEN of bar i+1 in the signal direction.
  Primary exit = M1 trail (init −0.5%, act +0.5%, dist 0.35%);
  control exit = fixed target +1.0% / stop −0.5% (T10). One open
  position per stock; after an exit, a FRESH surge bar (after the exit
  bar) can re-enter — no chain cap (variant V2-cap4: chain cap 4).
  No entries after 15:05; square-off 15:10.
- **V3 LADDER + VOLUME**: LADDER L-c rules exactly (0.4% log-grid from
  the 09:15 anchor, chain cap 6, exit = square-off only with −1.0%
  disaster stop), PLUS entries only when the signal candle's vr ≥ 1.5.

Pass gates unchanged: net positive in BOTH halves (Jan–May / Jun–Oct)
at ₹40/trade AND breadth (report # of 25 stocks individually
net-positive, top-3 share of total net, worst-5). Per mechanism:
trades, entries/day, win%, gross expectancy, chain-round expectancy
where re-entry applies, October alone, event-window split.

---

## PART 3 — EX-ANTE ADAPTATION vs THE DRIFT-FLIP — FROZEN 2026-10-30 (night), BEFORE ANY PART 3 SCORING

Part 2's diagnosis: intraday directional drift flips sign between
halves (V3 LONGs +₹43,171 Jan–May → −₹52,032 Jun–Oct), so any
fixed-direction rule dies on the flip. Part 3 tests whether EX-ANTE
adaptation — rules using ONLY data available before the trade (trailing
windows ending the previous trading day, or same-day data up to the
decision time) — beats fixed rules. NO calendar-month logic anywhere:
no rule may reference the month or half a trade falls in.

**Breadth gate, made numeric here (frozen before scoring):** a family
passes overall only if (a) net > 0 in BOTH halves at ₹40, AND
(b) ≥ 10 of 25 stocks individually net-positive (the best breadth
recorded anywhere in Parts 1–2), AND (c) when the Jan–Oct total is
positive, the top-3 stocks contribute ≤ 75% of it.

**Trailing intraday drift (D1/D2)**: for stock s on day t,
drift_N(s,t) = mean over the N trading days of s immediately BEFORE t
(from s's own daily series in `data/progressive/<SYM>/spot_daily.csv`)
of (close − open)/open × 100. If fewer than N prior days exist, no
drift → no entries that day under D1/D2.

- **D1 TRAILING-DRIFT GATE on V3**: the V3 mechanism exactly as scored
  in Part 2 (LADDER 0.4% log-grid from the 09:15 anchor, volume gate
  vr ≥ 1.5 on the signal candle, chain cap 6, hold-to-close exit with
  −1.0% disaster stop, data `data/progressive_vol/`), PLUS: a LONG
  entry is taken only if drift_20(s,t) > 0 and a SHORT entry only if
  drift_20(s,t) < 0 (drift exactly 0 → neither direction that day).
  A direction-blocked signal is skipped exactly the way a
  volume-blocked signal is in V3 (band extremes keep updating, scan
  continues). **D1b**: same with drift_10. Validation gate: the same
  engine with the drift gate disabled must reproduce the published V3
  result (3,275 trades, net −₹16,284.00) before D1/D1b numbers are
  trusted. Kept AND dropped sets are both reported per half.
- **D2 DRIFT-FOLLOW LADDER**: the V3 mechanism with the direction rule
  inverted in construction — ladder entries are generated ONLY in the
  direction of drift_20(s,t)'s sign for the whole stock-day (drift up
  → only LONG steps may trigger; drift down → only SHORT steps; drift
  0 or <20 prior days → no trades that stock-day). Volume gate,
  chain cap 6, hold-to-close exit with −1.0% disaster stop: identical
  to V3.

**X1 CROSS-SECTIONAL RELATIVE STRENGTH (new mechanism).** Data: 5-min
bars (OHLC identical in both caches; volume from the vol cache for X2).
For each trading day, two ranking sets:
- **Set 1**: rank every stock with data that day by r = close of the
  bar starting 10:30 ÷ open of the 09:15 bar − 1. LONG the top 3 and
  SHORT the bottom 3 among stocks with |r| ≥ 0.5% (fewer if fewer
  qualify). Entry at the OPEN of the bar starting 10:35.
- **Set 2**: rank by r2 = close of the bar starting 13:00 ÷ open of
  the 09:15 bar − 1, entry at the OPEN of the bar starting 13:05,
  same top-3/bottom-3 and |r2| ≥ 0.5% rules, BUT restricted to stocks
  NOT traded in Set 1 that day (frozen choice: exclusion, so the two
  sets never overlap and breadth spreads).
- **Exits**: **X1-T10** = fixed target +1.0% / stop −0.5% (stop-first
  on the same bar, exit at the level or the open if gapped through),
  square-off at the 15:10 bar close. **X1-HOLD** = hold to the 15:10
  bar close with a −1.0% disaster stop (same intrabar convention).
  One position per stock per set by construction.
- **X2 RS + VOLUME**: X1 entries (both sets, both exits — reported as
  X2-T10 and X2-HOLD) kept only if the stock's volume pace at the
  ranking bar is ≥ 1.0×: pace = cumulative volume from 09:15 through
  the ranking bar (10:30 set / 13:00 set) today ÷ the mean of the same
  clock-window cumulative volume over the stock's prior 20 trading
  days (vol cache). Fewer than 20 prior days with volume data → entry
  not kept.

Reporting per family: trades, entries/day, win%, net both halves +
October, gross expectancy, breadth block (# positive /25, top-3
share, worst-5), per-direction (LONG/SHORT) net per half, per-stock
net table, event-window split where the trade tagging allows.
A double-gate pass earns `stocks_new_strategy_paper_spec.md`; a fail
is reported with what the adaptation test proved (adaptation vs the
unadapted base — V3 for D-families — on identical windows).
