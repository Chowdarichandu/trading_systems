# DIAL — BANK NIFTY · INDICATOR PARAMETER ATLAS · 2026-11-14

Owner's order 2026-11-14 15:43: tune the top indicators and their
value parameters, with entry and exit defined, including long term.
Spec frozen before scoring: `indicator_parameter_tuning_bank_
SPEC.md`. Build: `indicator_parameter_tuning_bank_build.py`.
Numbers: `indicator_parameter_tuning_bank_results.json` · full
306-row grid: `indicator_parameter_tuning_bank_grid.csv`.
Research only — nothing running changed. Paper only, real money
₹0. Buying only, 1 lot (30), ₹220/trade.

Windows: **Discovery Jan–Jun 2026 (120 days)** · **Validation
Jul–Oct 2026 (83 days)** · November CF computed after the robust
set was frozen. Timing audit **PASS** (240 fired signal bars
recomputed from truncated series). **306 variant rows scored.**

## Headline verdict

**No robust row in any family. Zero of 306.** Only 26 rows were
positive in both windows (Supertrend 22, EMA cross 3, Bollinger
breakout 1; RSI momentum, RSI reversion, MACD, Bollinger reversion
and Donchian have none), and every one of the 26 fails at least one
frozen leg — so no row ever reached the placebo stage (the placebo
is leg 4; each candidate was already dead on an earlier leg). No
bar was moved. Nothing is selected, adopted or armed.

There is exactly one real structure in the atlas, and it is named
in full below as the best raw row: **wide-band Supertrend flips,
ADX-filtered, ridden to the opposite flip**. It earns in both
windows on a broad plateau — but it is payoff-shaped money at a
33% win rate, it misses the ₹7,500/month pace bar by ₹208.50 of
validation total, and it is nowhere near the owner's 60% WR bar.
It is recorded as NOT SELECTED, exactly as the protocol requires.

## Parameter cards

Shared exit sets: **E1** stop −40 / target +70 · **E2** stop −50 /
target +90 · **E3** stop −60 / target +120 · **E4** (trend families
only) exit on the family's own opposite signal, −60 hard stop. All
with 15:20 square-off. Entry (all families): signal on a completed
5-min bar close, first qualifying signal of the day, entry at the
next bar's open of the weekly strike nearest spot.

### 1. EMA cross — NONE ROBUST
- **Entry:** EMA(fast) crosses EMA(slow) at a bar close, with the
  spot close on the cross side of the futures session VWAP
  (up-cross + close above VWAP → CE; mirror → PE), ADX(14) filter
  where the row carries one.
- **Grid:** pairs (9,21), (13,34), (20,50) × ADX none/20/25 ×
  E1–E4 = 36 rows. 3 rows positive in both windows.
- **Best both-positive row:** EMA 9/21, ADX 25, E4 — discovery
  +₹5,096.50 (44 trades) · validation +₹6,986.00 (19 trades,
  WR 36.8%). Fails: plateau (only 1 of 3 neighbours validation-
  positive), validation ex-top-3 −₹13,148.50, pace ₹1,746.50/mo.
- **The warning inside the family:** EMA 20/50, no ADX, E4 made
  +₹65,155.50 in discovery — the largest discovery line in the
  whole atlas — and **−₹2,465.50 in validation**. The family's
  money flips sign between windows in both directions.
- **Verdict: NONE ROBUST.**

### 2. Supertrend — NONE ROBUST (the atlas's one real structure)
- **Entry:** Supertrend direction flips at a bar close → buy in
  the new direction (up = CE, down = PE), ADX(14) filter where the
  row carries one.
- **Grid:** period 7/10/14 × multiplier 2/3/4 × ADX none/20/25 ×
  E1–E4 = 108 rows. **22 rows positive in both windows — every one
  of them Supertrend, clustered at multiplier 4 with the E4 flip
  exit.** Fixed-target exits (E1–E3) on the same flips are worth
  far less: the money is in letting the flip run, not in booking
  a target.
- **Headline row (= best raw row, full detail below):** ST 7 ×4,
  ADX 25, E4 — discovery +₹37,579.70 · validation +₹29,791.50,
  plateau 4/4 neighbours validation-positive, ex-top-3 +₹544.50,
  1 red validation month — fails pace (₹7,447.88 vs ₹7,500) and
  carries WR 33.3%.
- **Verdict: NONE ROBUST.** Nearest family to the bar; still not
  over it, and the WR shape (best both-positive ST row: 52.0%)
  never approaches the 60% family-pass requirement.

### 3. RSI momentum — NONE ROBUST
- **Entry:** RSI crosses through 50 at a bar close (up → CE,
  down → PE).
- **Grid:** period 7/14/21 × E1–E3 = 9 rows. **Zero rows positive
  in both windows.** Least-bad combined row: RSI(14), E1 —
  discovery −₹18,545.50 · validation −₹16,236.00. The 50-cross is
  a lagging confirmation of a move already spent; on 5-min Bank
  Nifty it loses in every parameterisation tried.
- **Verdict: NONE ROBUST — dead at every value.**

### 4. RSI reversion — NONE ROBUST
- **Entry:** after RSI crosses below 50, if it first touches
  ≤ 25/30/35 and then ticks up while still ≤ 50 → CE; mirror
  (≥ 75/70/65, tick down) → PE.
- **Grid:** period 7/14/21 × thresholds (25,75)/(30,70)/(35,65) ×
  E1–E3 = 27 rows. **Zero rows positive in both windows.** The
  best validation row (RSI(21), 35/65, E2: +₹6,993.50) sits on a
  discovery of −₹45,273.00. Fading 5-min extremes in Bank Nifty
  options keeps paying the trend, same as Round 1's DIAL-R.
- **Verdict: NONE ROBUST — dead at every value.**

### 5. MACD — NONE ROBUST
- **Entry:** MACD line crosses its signal line at a bar close
  (up → CE, down → PE), ADX(14) filter where carried.
- **Grid:** (8,21,5), (12,26,9), (19,39,9) × ADX none/20/25 ×
  E1–E4 = 36 rows. **Zero rows positive in both windows.**
  Least-bad combined row: MACD 19,39,9, ADX 25, E4 — discovery
  −₹6,108.50 · validation −₹13,617.00. Even the slowest MACD,
  which should behave like the EMA family, cannot hold both
  windows.
- **Verdict: NONE ROBUST — dead at every value.**

### 6. Bollinger breakout — NONE ROBUST
- **Entry:** close beyond the band follows the move (above upper
  → CE, below lower → PE).
- **Grid:** period 14/20/30 × sd 1.5/2/2.5 × E1–E3 = 27 rows.
  Exactly **one** both-positive row: BB 14/1.5, E3 — discovery
  +₹4,694.00 (118 trades) · validation +₹11,432.50 (83 trades,
  WR 41.0%), plateau passes (2/3), ex-top-3 +₹1,292.50 — fails
  pace (₹2,858.12/mo) and red months (2 in Jul–Oct). The family's
  biggest validation line (BB 20/2.0, E1: +₹25,133.50) sits on a
  discovery of −₹47,627.00 — a pure window flip.
- **Verdict: NONE ROBUST.**

### 7. Bollinger reversion — NONE ROBUST
- **Entry:** a close at/beyond a band arms the fade; the first
  close back inside fires it (from above → PE, from below → CE).
- **Grid:** same 27 rows shape. **Zero rows positive in both
  windows**, and the family is deeply negative overall (least-bad
  combined row: BB 14/2.5, E3 — discovery −₹19,085.00 ·
  validation −₹32,655.00). Fading band extremes is the single
  worst idea in the atlas.
- **Verdict: NONE ROBUST — dead at every value.**

### 8. Donchian breakout — NONE ROBUST
- **Entry:** close above the prior N-bar high → CE, below the
  prior N-bar low → PE, ADX(14) filter where carried.
- **Grid:** N = 10/20/55 × ADX none/20/25 × E1–E4 = 36 rows.
  **Zero rows positive in both windows.** Signature row: DON 10,
  ADX 20, E3 — discovery **+₹31,754.00** · validation
  **−₹29,330.50**, an almost perfect mirror image. Channel
  breakouts chase exactly the moves that reverse in the second
  window.
- **Verdict: NONE ROBUST.**

## Best raw row — NOT SELECTED

**Supertrend period 7 × multiplier 4 · ADX(14) ≥ 25 · exit E4
(ride to the opposite flip, −60 hard stop, 15:20 square-off).**

| | Discovery (Jan–Jun) | Validation (Jul–Oct) |
|---|---|---|
| Trades | 46 | 33 |
| Net | **+₹37,579.70** | **+₹29,791.50** |
| Win rate | 30.4% | 33.3% |
| Months | Feb +₹28,104 carries it; Jan/Mar red | Jul +₹10,426 · Aug −₹45 · Sep +₹8,616 · Oct +₹10,794.50 |
| Ex-top-3 | −₹12,022.30 | +₹544.50 |

- Plateau: **passes** — all 4 one-step neighbours validation-
  positive (ST 10×4/ADX25/E4 +₹20,557 · ST 7×3/ADX25/E4
  +₹12,067.70 · ST 7×4/ADX20/E4 +₹5,969.50 · ST 7×4/ADX25/E3).
  This is a region, not a spike.
- **Why it is NOT robust:** validation pace ₹7,447.88/month vs
  the ₹7,500 bar — short by ₹208.50 of validation total; and the
  placebo leg was never reached because an earlier leg failed.
  For a family PASS it would also need WR ≥ 60%; it has 33.3%.
  Its discovery total leans on its top-3 runners (ex-top-3
  negative in discovery): this is payoff-shaped money — many
  −₹2,020 stops, a few large flip-ride runners — the same shape
  as TUNED v1 and the Stock Book, not the selection shape of the
  Bank stack.
- **November CF (descriptive, frozen after selection):** 3
  trades, +₹1,459.50 — Nov 6 PE stop −₹2,020 · Nov 11 PE
  square-off runner +₹5,499.50 · Nov 12 CE stop −₹2,020. One
  runner paying for two stops: the book's whole character in
  three trades.
- NC: 1 signal across the gate (counted, never substituted).

## Long-term annex — daily spot signal study (NOT a traded book)

Daily Bank Nifty spot, `volrix_banknifty/banknifty_daily_2019_
2026.csv`, 2019-07-01 → 2026-11-03, 1,822 bars. Event-based
signals on daily closes; forward moves measured close-to-close,
signed in the signal's direction. No options, no costs.

| Signal | Events | +5d avg / win | +10d avg / win | +20d avg / win |
|---|---|---|---|---|
| **EMA(20,50) cross** | 36 | +0.297% / 55.6% | +0.492% / 55.6% | **+0.816% / 58.3%** |
| EMA(50,200) cross | 8 | +0.474% / 62.5% | −1.131% / 37.5% | +0.695% / 50.0% |
| MACD(12,26,9) cross | 134 | +0.231% / 54.1% | −0.079% / 48.5% | +0.422% / 51.9% |
| RSI(14) 50-cross | 179 | +0.173% / 51.7% | +0.156% / 51.7% | +0.312% / 52.3% |
| Supertrend(10,3) flip | 60 | +0.221% / 53.3% | +0.194% / 51.7% | +0.227% / 50.0% |

Best two by 20-day expectancy: **EMA(20,50) cross (+0.816%,
58.3% win, 36 events)** and EMA(50,200) cross (+0.695%, 50.0%
win — but only 8 events in 7 years and its 10-day line is
negative, so it is a thin second). All five daily signals lean
positive at 20 days; none is large. This is direction-signal
quality on spot only — it says daily trend crosses are worth
respecting as a bias, nothing more.

## Honest one-liner

Intraday, no tuned classic indicator earns robustly on Bank
Nifty at any value in this atlas — the single money-making
structure, wide-band (×4) Supertrend flips with ADX ≥ 25 ridden
to the opposite flip, is real in both windows and on a plateau,
but it pays like a payoff book (33% WR, runner-dependent), misses
the pace bar by ₹208.50, and fails the owner's 60% WR standard
outright, so it stays NOT SELECTED; long-term, the daily
EMA(20,50) cross is the one signal with a measurable forward
edge (+0.82% average over the next 20 days, 58% win rate) — a
bias worth respecting, not a book.
