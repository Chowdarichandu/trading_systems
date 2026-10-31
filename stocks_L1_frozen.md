# LINE L1 — FROZEN SPEC (written BEFORE any scoring)

**Line:** L1 — LEVEL-NATIVE ENTRIES on Chandu's own 25 stocks.
**Design source:** Chandu's own level philosophy from his index setups — identify
the levels (PDH/PDC/PDL + multi-day structural levels), take an entry AT the
level, book a small profit, stop. Never before tested as a standalone
stock-native design (all prior stock work used V5/Skill signal streams or
morning-move qualifiers).
**Basis:** equity cash intraday, LONG/SHORT, no options/premiums, paper only,
real ₹0. Provisional per 100 shares. Net = gross − ₹40/trade. Jan–Oct 2026.
**Universe:** HOME 25 ONLY — GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR,
UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC,
IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL,
ASTRAL, BDL, OIL, HINDUNILVR. No ext, no pooled numbers anywhere in this line.

## Data
- 5-min bars: `data/progressive/<SYM>/spot_5m.csv` (09:15–15:25, 75 bars/day),
  Jan 1 – Oct 28, 2026.
- Oct 29–30, 2026: aggregated from the verified 1-min cache
  `data/1min_stocks_oct2026/old/<SYM>.csv` (O1/H1 method: bucket 1-min bars to
  5-min from 09:15). Aggregation is re-validated in-run against the cached
  Oct 28 bars (tolerance 0.051) and the counts reported; any mismatch aborts.
- Daily levels: `data/progressive/<SYM>/spot_daily.csv` (history incl. 2025),
  plus a derived daily row for 2026-10-29 from the aggregated bars (needed as
  the prior day for Oct 30), exactly as H1 constructed it.
- Nifty regime: NIFTY daily closes from `data/progressive/NIFTY/spot_daily.csv`
  extended for Oct 29/30 exactly as Line H1 (connector fetch, closeness-checked
  against the last cached close); 50DMA from closes strictly before the day.

## Levels (per symbol, per trading day D; all from daily rows BEFORE D)
- **PDH / PDL / PDC** = prior trading day's high / low / close.
- **H5 / L5** = max high / min low of the prior 5 trading days (part of the
  philosophy; no cell below trades them — stated so the omission is visible).
- **H20 / L20** = max high / min low of the prior 20 trading days.

## Common execution rules (all cells)
- Triggers are evaluated on the full 5-min bar series from 09:15.
- Entry = OPEN of the bar immediately after the trigger bar. Entry bar time
  must be ≤ 15:10, else no trade.
- Exit = the established `replay_plain` convention: target/stop on bar
  extremes from the entry bar onward (stop checked before target inside a
  bar), square-off at the 15:10 bar's close. The entry bar itself can stop
  out / target out — same convention as every prior line, stated openly.
- **Re-entry ALLOWED** (user's rule for stocks): after a trade completes, the
  same stock may be traded again the same day if it sets up again.
  **Safety cap: max 4 entries per stock per day per cell.**
- One open position per stock at a time within a cell run. Setup state
  machines advance only on bars while flat; bars inside an open position do
  not advance any state machine; after an exit on bar xi, scanning resumes at
  bar xi+1 with fresh states (L1-C consumed flags excepted — see below).

## Cells (3 mechanisms × 3 exits × 2 contexts = 18 cells)
Exits: **T05/S050** = target +0.5% / stop −0.5% · **T10/S050** = +1.0% / −0.5% ·
**T125/S065** = +1.25% / −0.65%. Contexts: **all** · **below50** (Nifty prior
close ≤ its 50DMA). Square-off 15:10 everywhere.

### L1-A BREAKOUT-RETEST (his Filter-4 shape, on PDH/PDL)
Independent state machine per level.
- LONG (PDH): WAIT_BREAK — a bar that CLOSES above PDH is the break bar.
  RETEST — the first later bar with low ≤ PDH×1.002 AND low ≥ PDH×0.999 AND
  close ≥ PDH (the bar comes back to within +0.2% of the level, does not
  undercut it by more than 0.1%, and closes holding it) is the trigger;
  enter LONG at the next bar's open.
  INVALIDATION — any bar after the break bar (before a retest trigger) that
  closes below PDH×0.999 returns the machine to WAIT_BREAK.
- SHORT (PDL): mirror — break bar closes below PDL; retest bar has
  high ≥ PDL×0.998 AND high ≤ PDL×1.001 AND close ≤ PDL; invalidation is a
  close above PDL×1.001.
- (The +0.2% approach band operationalises "retest": without it, every bar
  that merely stays above the level would count as a retest. Disclosed here,
  frozen, not tuned.)

### L1-B LEVEL REJECTION (touch-and-close-back-inside, against the touch)
- At PDL → LONG: a bar with low ≤ PDL×1.001 AND close > PDL triggers;
  enter LONG at the next bar's open.
- At PDH → SHORT: a bar with high ≥ PDH×0.999 AND close < PDH triggers;
  enter SHORT at the next bar's open.
- Any qualifying bar triggers (subject to sequencing + the 4/day cap).

### L1-C MULTI-DAY BREAK (first intraday break of the 20-day level)
- LONG: the FIRST bar of the day with high > H20 triggers; enter LONG at the
  next bar's open. SHORT: the FIRST bar with low < L20 triggers; enter SHORT
  at the next bar's open. No retest wait.
- First-break bars are determined on the full day per level and are CONSUMED
  for the day once they occur (a re-break later is not a new trigger; if a
  position is open when a first break occurs, that trigger is skipped and
  still consumed). A single bar crossing BOTH H20 and L20 triggers neither
  and consumes both. Max 2 triggers/day by construction.

## Placebo (same run, mandatory)
Lag-placebo: every cell is re-run identically but with the levels shifted
+1 day — on day D it uses the levels that were valid for the PREVIOUS trading
day in the window (computed from daily data through D−2). Same convention as
the H1/M2 lag-placebos (the reference input is taken one day late, so a real
level effect must collapse). A cell must beat its own placebo's net.

## Timing audit (same run, mandatory)
Every trade of every cell (real + placebo) is independently re-verified
against levels re-derived from `spot_daily.csv`:
1. the stored trigger bar satisfies the cell's frozen trigger conditions
   against those levels (for L1-A: break-bar close, retest-bar bands, and no
   invalidation bar and no earlier qualifying retest bar in between; for
   L1-C: no earlier bar of the day crossed that level);
2. entry_time is exactly the bar after the trigger bar and entry equals that
   bar's open (±0.011);
3. trades of a stock-day within a cell never overlap (each entry bar is after
   the previous trade's exit bar) and entries per stock-day ≤ 4;
4. placebo trades use exactly the previous trading day's levels.
Violation counts are published with the results. NO number leaves this line
without the audit and placebo attached.

## GATE (frozen)
A cell is a **CANDIDATE** only if ALL hold: Jan–Oct net > 0 · Jan–May > 0 ·
Jun–Oct > 0 · October > 0 · breadth ≥ 15/25 · expectancy ≥ +₹100/trade ·
cell net > its placebo net · timing audit clean (0 violations).
Additionally, EVERY cell's full month table (Jan–Oct) is published, and any
cell with **10/10 or 9/10 positive months** is flagged as a month-repair
target even if another gate leg fails (the user's standing spec is every
month positive). If a candidate passes, `stocks_L1_candidate_spec.md` is
frozen with a December fresh-window judging rule. If none passes, the report
states the level family's honest ceiling and the per-cell month tables.
