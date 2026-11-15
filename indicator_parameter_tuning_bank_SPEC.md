# DIAL — BANK NIFTY · INDICATOR PARAMETER TUNING ATLAS · SPEC
# (frozen before scoring, 2026-11-14)

Programme: DIAL (registry: dial_programme.md). This is the dial turn
after DIAL-Bank Round 1 FAILED on default parameters (combined
−₹33,719, dial_bank_2026-11-14.md). Owner's order 2026-11-14 15:43:
tune the top indicators and their value parameters, with entry and
exit defined, including long term. Research only — no running book,
ledger or job is changed. Option BUYING only, 1 lot (30),
₹220/trade, paper only, real money ₹0.

Data, contract selection, premium resolution, contiguity and NC
rules are inherited VERBATIM from dial_bank_SPEC.md (same spot store
`data/progressive/BANKNIFTY/spot_5m.csv`, same expiry map with the
November 2026-11-23 override, strike = 100-step nearest the SIGNAL
bar's spot close, half rounds up, entry premium = entry bar's stored
open, missing contract/bars = NC counted never substituted, futures
session VWAP from FUT7 store for the EMA family's side test).

## 1. Indicator families and parameter grids (frozen)

All indicators on the continuous 5-min spot series, causal by
construction (value at bar i uses bars ≤ i only). Signal evaluated
at a COMPLETED bar close; entry = NEXT bar at the stored contract
open; signals considered at bar closes 09:15..15:10 only (a signal
whose entry bar would be past 15:15 is LATE, counted, never a
trade). FIRST qualifying signal per day per variant row — each
(family × signal params × ADX filter × exit set) combination is a
standalone variant row and takes its own first signal of the day.

- **EMA-CROSS** (trend; ADX dimension applies): pairs (9,21),
  (13,34), (20,50). EMA seeded with SMA of the first p closes,
  k = 2/(p+1). Up-cross at bar i: EMAf[i−1] ≤ EMAs[i−1] and
  EMAf[i] > EMAs[i]; AND spot close at bar i on the cross side of
  the futures session VWAP (up-cross: close > VWAP; down-cross:
  close < VWAP). Up-cross → CE, down-cross → PE. If VWAP is
  undefined at bar i, the cross cannot qualify there.
- **SUPERTREND** (trend; ADX applies): period 7/10/14 × multiplier
  2/3/4. Wilder ATR, final-band carry rules exactly as Round 1.
  Entry on a direction FLIP at bar close, in the new direction
  (up → CE, down → PE). No VWAP test.
- **RSI-MOMENTUM**: period 7/14/21 (Wilder). Cross up through 50
  (RSI[i−1] ≤ 50, RSI[i] > 50) → CE; cross down through 50
  (RSI[i−1] ≥ 50, RSI[i] < 50) → PE.
- **RSI-REVERSION**: period 7/14/21 × threshold pair
  (OS,OB) ∈ {(25,75), (30,70), (35,65)}. Episode state machine on
  the continuous series: a LONG episode opens when RSI crosses
  below 50 from above; during it track the RSI minimum; if the
  minimum ≤ OS and RSI turns up at bar i (RSI[i] > RSI[i−1],
  RSI[i] ≤ 50) the episode fires its one CE signal at bar i and is
  consumed; the episode ends when RSI crosses back above 50.
  SHORT episode mirrors (opens crossing above 50, maximum ≥ OB,
  turn down RSI[i] < RSI[i−1] with RSI[i] ≥ 50 → PE).
- **MACD** (trend; ADX applies): (fast,slow,signal) ∈
  {(8,21,5), (12,26,9), (19,39,9)}. MACD = EMAf − EMAs (house EMA
  seeding), signal = EMA of MACD seeded with the SMA of its first
  `signal` values. Signal-line cross up → CE, cross down → PE.
- **BOLLINGER-BREAKOUT**: period 14/20/30 × sd 1.5/2/2.5 (SMA ±
  sd × population stdev of last `period` closes incl. current).
  Close above upper band → CE; close below lower band → PE.
- **BOLLINGER-REVERSION**: same grid. A close at/beyond a band
  ARMS the fade on that side (close ≥ upper arms short-fade,
  close ≤ lower arms long-fade); the signal fires at the first
  later bar whose close is back INSIDE the band on that side
  (short-fade → PE, long-fade → CE). An arm expires after 30 bars
  or when a close arms the opposite side; after a signal fires the
  arm is consumed.
- **DONCHIAN** (trend; ADX applies): channel N ∈ {10, 20, 55}
  bars, computed from the N bars BEFORE the signal bar (upper =
  max high, lower = min low of bars i−N..i−1). Close > upper →
  CE; close < lower → PE.

**ADX(14) FILTER dimension (trend families only — EMA-CROSS,
SUPERTREND, MACD, DONCHIAN):** Wilder ADX on spot. Levels: NONE /
20 / 25. A signal qualifies only if ADX at the signal bar ≥ the
level (NONE = no test).

## 2. Exit sets (scored for every family)

Walk over the day's stored premium bars from the entry bar, every
5-min timestamp entry..exit present (contiguity), else NC. Stop
checked before target within a bar; fills AT the level; the 15:20
bar is itself level-checked first, else exit at its close; bars
after 15:20 ignored; entry bar can trigger an exit.

- **E1**: stop −40 / target +70, 15:20 square-off.
- **E2**: stop −50 / target +90, 15:20 square-off.
- **E3**: stop −60 / target +120, 15:20 square-off.
- **E4** (trend families only): indicator-flip exit with a −60
  hard stop and 15:20 square-off backstop. Flip event = the
  family's own RAW opposite direction event on spot (EMA: opposite
  cross, no VWAP/ADX test; Supertrend: direction flip; MACD:
  opposite signal-line cross; Donchian: close beyond the opposite
  channel edge). Walk: at each premium bar from the entry bar —
  (1) if a flip event occurred at the PREVIOUS spot bar's close
  (or any earlier unconsumed bar), exit at this bar's OPEN;
  (2) else if the bar's low ≤ entry − 60, exit at entry − 60;
  (3) if the bar is 15:20, exit at its close. First trigger wins;
  the flip event at the entry bar's own close acts at the next bar.

Money: net = (exit − entry) × 30 − ₹220. Win = net > 0.

## 3. Windows (frozen)

- **Discovery** = trading days 2026-01-01..2026-06-30.
- **Validation** = trading days 2026-07-01..2026-10-31.
  (Gate spot store: 203 days Jan 1–Oct 31; Oct 29–30 absent from
  the store, outside the basis — same as Round 1.)
- **November CF** = Nov 2–13, computed ONLY AFTER the robust set
  is frozen, descriptive, never used to select anything.

## 4. Robustness rules (frozen — a row is ROBUST only if ALL hold)

1. Discovery total > 0 AND validation total > 0 (after costs).
2. **Plateau**: at least 2 one-step neighbours of the row in its
   family grid are also validation-positive. One-step neighbour =
   differs in exactly ONE dimension by exactly one adjacent level,
   dimensions and level orders being: the family's signal-param
   axes (EMA pair order (9,21)<(13,34)<(20,50); Supertrend period
   7<10<14 and multiplier 2<3<4; RSI period 7<14<21; RSI-reversion
   threshold (25,75)<(30,70)<(35,65); MACD order (8,21,5)<(12,26,9)
   <(19,39,9); Bollinger period 14<20<30 and sd 1.5<2<2.5;
   Donchian 10<20<55), ADX NONE<20<25 where the family has the
   dimension, exit E1<E2<E3<E4 where the family has E4 else
   E1<E2<E3.
3. Validation ex-top-3 > 0.
4. Validation random-entry placebo ≥ 95th percentile: 500
   iterations, seed 20261114, per Round-1 convention (for each
   real validation trade: random validation day, same side, entry
   bar uniform in 09:20..15:15, strike nearest the close of the
   bar before entry, same exit set — for E4 rows the flip series
   is the family's raw direction-event series on the drawn day;
   NC draws redrawn up to 50 times then dropped and counted;
   percentile = % of iteration totals strictly below the real
   validation total).
5. Validation pace ≥ ₹7,500/month (validation total / 4 ≥ 7,500)
   and ≤ 1 red month inside Jul–Oct.
6. Win rate reported for both windows; a family PASS requires a
   robust row whose VALIDATION WR ≥ 60%.

The single best raw row overall (highest validation total) is
listed separately and labelled **NOT SELECTED** unless it is itself
robust. No row is adopted, armed or promoted by this report —
robust rows are candidates for a forward paper shadow only, at the
owner's word.

## 5. Timing audit

Indicators are causal recursions/trailing windows and entry is the
bar AFTER the signal bar by construction. In addition, for each
family the build recomputes the family's signal-defining values at
a sample of fired signal bars (first 25 per family across its
variants) from the series truncated at that bar and asserts
equality; a mismatch aborts the run and is reported instead of
results.

## 6. Long-term annex (signal quality only — NOT options P&L)

Daily Bank Nifty spot from `volrix_banknifty/banknifty_daily_
2019_2026.csv` (2019-07-01 → 2026-11-03, 1,822 bars). Signals on
daily closes, event-based (each cross/flip counted once):
EMA(20,50) cross, EMA(50,200) cross, RSI(14) cross through 50,
MACD(12,26,9) signal-line cross, Supertrend(10,3) flip (daily
bars, same construction as intraday). For each directional event,
the following 5/10/20-TRADING-day spot moves are measured
close-to-close from the signal day's close, signed in the signal's
direction (down-signals scored on the inverted move). Report per
signal: event count, and per horizon the average signed move % and
the win rate (% of events with a positive signed move). Events
without a full forward window are excluded per horizon and
counted. This annex is a spot signal study — no options, no costs,
no traded book.

## 7. Deliverables

- `indicator_parameter_tuning_bank_results.json` — every variant
  row (family, params, ADX, exit, discovery stats, validation
  stats, neighbours, robust flags, placebo where run), robust set,
  November CF for robust rows + best raw row, annex numbers.
- `indicator_parameter_tuning_bank_grid.csv` — one row per variant
  with discovery/validation totals, WR, trades.
- `indicator_parameter_tuning_bank_2026-11-14.md` — parameter card
  per family + best raw row + annex + verdicts.

Frozen 2026-11-14, before scoring. Build:
indicator_parameter_tuning_bank_build.py.
