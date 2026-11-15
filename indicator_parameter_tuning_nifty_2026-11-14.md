# DIAL PARAMETER ATLAS — NIFTY · indicator & parameter tuning run 2026-11-14

Spec: `indicator_parameter_tuning_nifty_SPEC.md` (frozen before scoring) · Numbers:
`indicator_parameter_tuning_nifty_results.json` · All 306 configurations:
`indicator_parameter_tuning_nifty_heatmap.csv` · Build:
`indicator_param_tuning_nifty_build.py`.
Standalone research — signals from spot candles only; not a filter on any book.
Buying only, 1 lot (65), ₹220/trade, paper only, real money ₹0. This run does not
touch the separately running DIAL-Nifty Round 2 (R-PE seed).

## Verdict up front
**No indicator, at any parameter values in the grid, is ROBUST on Nifty intraday.
Zero of 306 configurations pass.** Not one configuration even clears the screen
before the placebo leg: only 23 of 306 are validation-positive at all, only 9 are
positive in both windows, the best validation total in the whole atlas is
+₹19,726 (below the ₹30,000 pace floor), and **no configuration anywhere reaches
a 60% win rate in validation** (best: 52.4% on 21 trades). The median
configuration loses ₹22,977 in validation. Discovery winners invert in
validation — the single best discovery row (+₹55,343, Jan–Jun) loses ₹25,533 in
Jul–Oct at a 21.4% win rate. That sign-flip pattern is the fingerprint of noise,
not of a mistuned edge: the dial was turned through 306 positions and there is
no channel at any of them.

## Method in one paragraph
Discovery Jan–Jun 2026, validation Jul–Oct 2026, identical stores and fill rules
to DIAL Round 1 (signal on completed 5-min bar close, entry next bar at the
stored contract open, weekly strike nearest spot, level fills with stop-first,
15:20 square-off, basis-consistent futures VWAP for the EMA family). ROBUST
(frozen) requires: both windows positive · ≥2 one-step parameter neighbours
validation-positive (plateau, not spike) · validation ex-top-3 positive ·
validation random-entry placebo ≥ 95th pct · validation pace ≥ ₹7,500/mo ·
≤1 red month in Jul–Oct · validation WR ≥ 60%. Because **zero** configurations
passed the non-placebo legs, the placebo leg was never reached — no config
earned the right to be placebo-tested. November is counterfactual-only.

## Coverage / NC (denominators never hidden)
The premium store was built for other books' leg days, so roughly a third of
signals in every family are NC (`nc_no_file` — the exact contract-day was never
stored; never substituted). Family totals below are sums over the family's
signal sets (params × ADX where applicable); every scored total stands next to
these counts.

| Family | Disc signals → scored (NC) | Val signals → scored (NC) |
|---|---|---|
| EMA cross | 643 → 338 (305) | 443 → 259 (184) |
| Supertrend | 2,472 → 1,595 (877) | 1,644 → 1,122 (522) |
| RSI momentum | 349 → 255 (94) | 243 → 174 (69) |
| RSI reversion | 892 → 521 (371) | 604 → 399 (205) |
| MACD | 1,054 → 682 (372) | 727 → 503 (224) |
| Bollinger breakout | 1,033 → 736 (297) | 714 → 487 (227) |
| Bollinger reversion | 1,030 → 590 (440) | 721 → 490 (231) |
| Donchian | 1,027 → 665 (362) | 698 → 463 (235) |

Timing audit: PASSED (600 sampled trades across all configurations — every
entry bar is exactly signal bar + 5 min, every entry premium equals the stored
bar open). Independent RSI(14) recomputation at a check bar matched the main
path to the printed digit (34.058 = 34.058).

## PARAMETER CARDS

### 1. EMA cross — **NONE ROBUST** (36 configs; 11 validation-positive)
- Best robust parameters: **none**.
- Entry rule (frozen): fast EMA crosses slow EMA at a bar close, with price on
  the cross side of session VWAP (basis-consistent) → buy CE (up-cross) / PE
  (down-cross), next bar open. Exits E1 −40/+70 · E2 −50/+90 · E3 −60/+120 ·
  E4 flip exit, −60 hard stop. ADX(14) filter none/20/25.
- Best raw row in family: **EMA(9,21), ADX 25, E4** — discovery **−₹18,358**
  (34 trades) · validation **+₹19,726** (18 trades, WR 38.9%, ex-top-3 −₹6,589,
  2 red months). A validation-only mirage: the same row lost money for the
  entire first half of the year. The family's discovery champion,
  EMA(20,50)/no-ADX/E4 (+₹55,343), inverted to −₹25,533 in validation.

### 2. Supertrend — **NONE ROBUST** (108 configs; 7 validation-positive)
- Best robust parameters: **none**.
- Entry rule: direction flip at bar close → buy CE/PE next bar open. Grid:
  period 7/10/14 × multiplier 2/3/4, ADX none/20/25, exits E1–E4.
- Best raw row in family: **ST(7,4), ADX 25, E4** — discovery +₹1,048
  (31 trades) · validation +₹10,577 (21 trades, WR 47.6%, ex-top-3 −₹15,738).
  Cross-check: ST(7,3) with no ADX and E2 geometry (Round-1-like, minus the
  VWAP condition) totals −₹60,535 across the year — consistent with Round 1's
  DIAL-T verdict. The widest multiplier (4) with the ADX 25 filter loses the
  least; nothing earns.

### 3. RSI momentum — **NONE ROBUST** (9 configs; 0 validation-positive)
- Best robust parameters: **none**.
- Entry rule: RSI crosses through 50 (up = CE, down = PE), next bar open.
  Periods 7/14/21, exits E1–E3.
- Best raw row in family: **RSI(14), E1** — discovery **+₹21,138** ·
  validation **−₹34,990** (57 trades, WR 31.6%). The cleanest sign-flip in the
  atlas: the 50-cross follows strength straight into reversal, in both halves,
  in opposite directions.

### 4. RSI reversion — **NONE ROBUST** (27 configs; 0 validation-positive)
- Best robust parameters: **none**.
- Entry rule: RSI exits the extreme zone turning back (≤25/30/35 then up = CE;
  ≥65/70/75 then down = PE), next bar open. Periods 7/14/21, exits E1–E3.
- Best raw row in family: **RSI(21), band 30/70, E3** — discovery −₹7,698 ·
  validation −₹1,097 (30 trades, WR 33.3%). "Least bad" is the ceiling here;
  every other row is worse in validation. (The Round-1 observation that the
  overbought put side alone was positive is being tested separately in Round 2;
  inside this full two-sided family it does not survive.)

### 5. MACD — **NONE ROBUST** (36 configs; 0 validation-positive)
- Best robust parameters: **none**.
- Entry rule: MACD line crosses its signal line at bar close → buy CE/PE next
  bar open. Triples (8,21,5), (12,26,9), (19,39,9); ADX none/20/25; exits E1–E4.
- Best raw row in family: **MACD(19,39,9), ADX 25, E4** — discovery −₹48,588 ·
  validation −₹1,949 (43 trades, WR 34.9%). The slowest MACD with the strictest
  filter merely bleeds slowest. All 36 rows are validation-negative.

### 6. Bollinger breakout — **NONE ROBUST** (27 configs; 2 validation-positive)
- Best robust parameters: **none**.
- Entry rule: close crosses beyond the band → follow (above upper = CE, below
  lower = PE), next bar open. Periods 14/20/30 × sd 1.5/2/2.5, exits E1–E3.
- Best raw row in family: **BB(14,2.5), E1** — discovery +₹7,843 (69 trades) ·
  validation +₹8,645 (48 trades, WR 39.6%, ex-top-3 −₹4,345, 0 validation-
  positive neighbours). Positive in both windows — one of only 9 such rows in
  the atlas — but the win rate (39.6% against a −40/+70 geometry), the negative
  ex-top-3 and the isolated plateau kill it. A curiosity, not a candidate.

### 7. Bollinger reversion — **NONE ROBUST** (27 configs; 0 validation-positive)
- Best robust parameters: **none**.
- Entry rule: previous close beyond the band, current close back inside →
  fade (was above upper = PE, was below lower = CE), next bar open. Same grid,
  exits E1–E3.
- Best raw row in family: **BB(20,2.5), E2** — discovery −₹19,922 · validation
  −₹21,168 (48 trades, WR 31.2%). Fading band touches loses in both windows at
  every parameter set — band extremes on Nifty continue more often than they
  snap back, at 5-minute scale.

### 8. Donchian breakout — **NONE ROBUST** (36 configs; 3 validation-positive)
- Best robust parameters: **none**.
- Entry rule: fresh close beyond the prior-N-bar channel (N = 10/20/55) →
  follow, next bar open. ADX none/20/25, exits E1–E4.
- Best raw row in family: **DON(20), ADX 25, E4** — discovery **−₹60,221**
  (63 trades) · validation +₹8,953 (39 trades, WR 41.0%, ex-top-3 −₹26,741).
  The worst discovery row among family champions: pure second-half luck.

## Single best raw row overall — NOT SELECTED
**EMA(9,21) cross, ADX(14) ≥ 25 filter, E4 flip exit (−60 hard stop):**
validation **+₹19,726** on 18 trades. It is labelled **NOT SELECTED** because it
is not robust — discovery **−₹18,358**, validation WR **38.9%**, validation
ex-top-3 **−₹6,589**, 2 red validation months, validation pace ₹4,932/mo against
the ₹7,500 floor. Its exact entry rule: EMA(9) crosses EMA(21) at a 5-min bar
close with the futures close on the cross side of the futures session VWAP and
ADX(14) ≥ 25 → buy the weekly strike nearest spot (CE up / PE down) at the next
bar's open; exit at the open after the first opposite cross, −60 hard stop,
15:20 square-off. November CF for this row (descriptive, post-freeze): 1 scored
trade — Nov 12, CE 25300, in 09:25 @216.50, flip exit 190.75 → **−₹1,893.75**.
November agrees with the discovery half, not the validation half.

Texture worth recording (descriptive, not findings): the flip exit E4 tops the
validation table in every trend family — exiting on the indicator's own reversal
loses less than fixed −40/+70…−60/+120 targets — and ADX 25 sits on every top
trend row. Both are damage-reducers on losing signals, not edges: with them,
the best rows still fail on win rate, ex-top-3 and pace simultaneously.

## LONG-TERM ANNEX — spot signal study, NOT a traded book
Daily Nifty spot, events counted from 2025-07-01 (uniform warm-up; EMA200 is
seeded at the 2025 start, so its early values are approximations). Directed
forward return = signal direction × spot move over the next 5/10/20 trading
days, from the signal day's close. No costs, no options, no P&L claim.

| Signal | Events (L/S) | 5-day mean · WR | 10-day mean · WR | 20-day mean · WR |
|---|---|---|---|---|
| EMA(20,50) cross | 8 (4/4) | +0.03% · 42.9% (n=7) | −0.64% · 14.3% (n=7) | **+0.36% · 57.1%** (n=7) |
| EMA(50,200) cross | 1 (0/1) | +3.70% · 100% (n=1) | +2.79% · 100% (n=1) | −4.33% · 0% (n=1) |
| RSI(14) 50-cross | 42 (21/21) | +0.21% · 54.8% (n=42) | −0.15% · 48.8% (n=41) | +0.14% · 48.7% (n=39) |
| MACD(12,26,9) cross | 26 (13/13) | **+0.44% · 69.2%** (n=26) | +0.32% · 50.0% (n=26) | +0.20% · 44.0% (n=25) |
| Supertrend(10,3) flip | 12 (6/6) | +0.65% · 75.0% (n=12) | **+1.08% · 66.7%** (n=12) | +0.35% · 45.5% (n=11) |

Reading: the long-term signals are weak tea, not channels. At the 20-day
horizon the two least-weak are EMA(20,50) (+0.36%) and Supertrend(10,3)
(+0.35%) — on 7 and 11 usable events respectively, far too few to call an edge.
The strongest cells in the whole annex are short-horizon: Supertrend flips at
5/10 days (+0.65%/+1.08%, WR 75%/67%) and the MACD cross at 5 days (+0.44%,
WR 69%) — directionally interesting for swing context, decaying to coin-flips
by day 20. EMA(50,200) fired once in the entire window; its row is anecdote,
not evidence. Nothing here justifies a long-term traded book on its own.

## Verdict
**FAIL for the whole atlas — no family passes, no parameter set is selected,
nothing is adopted or armed, and nothing that runs was changed.** Round 1 said
the default dial position is dead; this run turned the dial through EMA,
Supertrend, RSI (both modes), MACD, Bollinger (both modes) and Donchian —
306 configurations, three exit geometries plus a flip exit, with and without
ADX filtering — and every position is dead the same way: sub-53% win rates,
negative ex-top-3, discovery winners inverting in validation. On 5-minute
Nifty, the classic indicator moments are not mistuned; they are anti-predictive
to neutral, exactly as Round 1's shift placebo showed. The only place any
indicator shows a pulse at all is the daily timeframe at 5–10 day horizons
(Supertrend flip, MACD cross) — as context signals, on small samples, not as a
book.
