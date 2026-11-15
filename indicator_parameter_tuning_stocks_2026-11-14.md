# INDICATOR PARAMETER ATLAS — STOCKS · 2026-11-14

Programme: DIAL. Owner's order 2026-11-14 15:43 — tune the top indicators and their value
parameters, entry and exit defined, even for long term. Spec frozen before scoring:
`indicator_parameter_tuning_stocks_SPEC.md`. Build: `indicator_parameter_tuning_stocks_build.py`.
Numbers: `indicator_parameter_tuning_stocks_results.json` · Trades of every one-year-robust
row (none) and all Part B trades: `indicator_parameter_tuning_stocks_trades.csv`.
Basis: **equity cash · frozen 25 names · per 100 shares PROVISIONAL · ₹40/trade · paper
only, real money ₹0.** Judged PER YEAR, never pooled. Research only — nothing running was
touched. This atlas does not duplicate the separate Round 2 frequency test; frequency
discipline (≤ 1 trade/stock/day, ≤ 5/day across the watchlist, ranked by signal extremity)
is built into every Part A config.

## VERDICT

- **Part A (intraday, 414 configs): NO robust parameter set exists — in either year, in
  any family.** Zero configs were robust in 2025, zero in 2026, so no family passes and,
  per the frozen spec, no November CF is produced. The failure is structural, not a near
  miss: discovery (Jan–Jun) totals are negative for nearly every family's best row in both
  years, and the few validation winners flip sign between years.
- **Part B (daily swing, 9 systems × 4 exit overlays): the earners are the two daily
  REVERSION systems and daily MACD.** Bollinger daily reversion and RSI daily reversion
  are positive in both years at their native exits; MACD(12,26,9) daily is positive in
  both years. Every daily TREND system (EMA50/100 cross, RSI-50 cross, Supertrend daily)
  makes its money in 2025 and gives back more in 2026. These Part B rows pass the frozen
  Part B bar (both years positive, ≥ 10 trades/year) — they are COUNTED, i.e. candidates
  for forward evidence, not proven edges: Part B's frozen design has no placebo leg, and
  several counted rows carry equity-curve drawdowns larger than their total profit.

# PART A — INTRADAY PARAMETER CARDS

Shared frame: signal at a completed 5-min bar's close, entry next bar's open; exits
X1 +0.8%/−0.4% · X2 +1.0%/−0.5% · X3 +1.5%/−0.75% · FLIP (trend families: exit at the
first opposite-signal bar's close, −0.75% hard stop), square-off at the 15:10 close.
Discovery = Jan–Jun, Validation = Jul–Oct, per year. ROBUST (per year) = discovery AND
validation positive, ≥ 2 one-step neighbours validation-positive, validation ex-top-3
positive, validation placebo ≥ 95th pct at the same frequency, validation pace
≥ ₹7,500/mo (2026) / ₹5,000/mo (2025), ≤ 1 red validation month.

### EMA-X — EMA cross + VWAP-proxy side — NONE ROBUST (36 configs)
Entry: fast EMA crosses slow EMA at bar close AND close is on the cross's side of the
session VWAP-proxy (EW typical-price — the stores carry no volume) → next bar open.
Best raw (NOT SELECTED): EMA(13,34), ADX ≥ 20, FLIP exit — 2025: disc −₹22,934 /
val −₹21,044 · 2026: disc −₹52,263 / val +₹20,500 (placebo 96.0 but ex-top-3 −₹8,890,
pace ₹5,125 < ₹7,500). The best 2026-validation row (EMA(20,50), ADX 25, FLIP, val
+₹20,744) is −₹39,469 in 2025 validation; the best 2025 row is −₹12,352 in 2026.

### ST — Supertrend flip — NONE ROBUST (108 configs)
Entry: Supertrend direction flip at bar close → next bar open (atlas drops Round 1's
VWAP condition). Best raw (NOT SELECTED): ST(14,4), no ADX, FLIP — 2025: disc −₹26,164 /
val +₹14,047 (ex-top-3 −₹5,623, pace ₹3,512 < ₹5,000) · 2026: disc −₹32,389 / val −₹302.
No Supertrend setting survives its own discovery window in either year.

### RSI-M — RSI 50-cross momentum — NONE ROBUST (36 configs)
Entry: RSI crosses through 50 at bar close → next bar open. Best raw (NOT SELECTED):
RSI(21), ADX ≥ 20, X3 — 2025: disc −₹24,704 / val −₹1,773 · 2026: disc −₹22,911 /
val +₹18,313 (fails only discovery and pace there — the closest trend row in the atlas,
and still dead on its Jan–Jun window in both years).

### MACD — signal cross — NONE ROBUST (36 configs)
Entry: MACD line crosses its signal line at bar close → next bar open. Best raw
(NOT SELECTED): MACD(12,26,9), ADX ≥ 25, X1 — 2025: disc −₹20,426 / val −₹4,874 ·
2026: disc −₹14,469 / val +₹4,926 (ex-top-3 −₹4,918, 3 red validation months).

### BB-BO — Bollinger breakout — NONE ROBUST (108 configs)
Entry: close crosses outside the band at bar close → next bar open. Best raw
(NOT SELECTED): BB(14, 2.5), ADX ≥ 20, FLIP — 2025 val +₹1,957 · 2026 val +₹11,906,
discovery negative in 2025 and ex-top-3 negative both years.
**The atlas's single all-four-windows-positive config** sits here: BB(30, 2.5), no ADX,
X3 — disc +₹23,129 / val +₹3,808 (2025), disc +₹21,095 / val +₹7,051 (2026). It is still
NOT SELECTED: its validation ex-top-3 is negative in both years (−₹10,498 / −₹11,211 —
the validation profit is carried by three or fewer trades), validation pace is ₹952/mo
and ₹1,763/mo against ₹5,000/₹7,500 bars, and it has 2 red validation months each year.

### DC — Donchian breakout — NONE ROBUST (36 configs)
Entry: close beyond the prior-period channel edge → next bar open. Best raw
(NOT SELECTED): DC(10), no ADX, X3 — 2025: disc −₹27,426 / val −₹7,626 · 2026:
disc +₹41,651 / val +₹13,929 (ex-top-3 −₹4,304, pace ₹3,482 < ₹7,500). A 2026-only
shape; its 2025 twin loses.

### RSI-R — RSI reversion — NONE ROBUST (27 configs)
Entry: RSI crosses back through the low threshold (25/30/35) after an excursion →
LONG next bar open; mirror SHORT at the high threshold. Best raw (NOT SELECTED):
RSI(21), thresholds 30/70, X1 — 2025 validation +₹21,311 passes EVERY validation leg
(placebo 100.0, ex-top-3 +₹12,741, pace ₹5,328, 1 red month) and fails only on its
discovery window (−₹39,010); 2026: disc −₹53,404 / val −₹8,528. Intraday reversion in
these names was a second-half-2025 event, not a parameter set.

### BB-R — Bollinger reversion (intraday) — NONE ROBUST (27 configs)
Entry: close crosses back inside the band after a close outside → next bar open.
Best raw (NOT SELECTED): BB(14, 1.5), X2 — 2025: disc −₹43,944 / val +₹18,345 ·
2026: disc −₹76,595 / val +₹2,710. Same shape as RSI-R: validation-only life, dead
discovery in both years.

**Part A structural read:** with the churn removed (≤ 5 trades/day), the intraday
indicator entries in these 25 names are still not a channel: 414 configs, only 6 are
validation-positive in both years, only 13 discovery-positive in both years, only 1
positive in all four windows — and that one's validation rests on ≤ 3 trades. The
Jan–Jun windows contradict the Jul–Oct windows in both years, in both directions,
across all eight families. No parameter turn inside this grid fixes a contradiction
between the halves of the data itself.

# PART B — LONG-TERM (DAILY SWING) PARAMETER CARDS

Frame: daily candles (`spot_daily.csv`, Oct 2024 warm-up), LONG only, one position per
name, signal at day close → entry next day open, ₹40/trade, per 100 shares provisional.
COUNTED = positive in BOTH years AND ≥ 10 trades in each year. Max DD = peak-to-trough
of the combined closed-trade equity curve (₹). FORCED = position closed at the data edge
(2026-11-13 close) because its exit rule had not fired — marked, not a rule exit.

### BB-REV-D — Bollinger(20,2) daily reversion — COUNTED ✓ (the strongest card)
Entry: daily close back ≥ lower band after a close below it → next open.
Exit (BASE): first close ≥ middle band → next open. No stop.
- BASE: 2025 — 91 trades, **+₹28,946**, WR 72.5%, avg hold 12.4 d, worst −₹41,345 ·
  2026 — 119 trades, **+₹100,067**, WR 58.8%, avg hold 13.5 d, worst −₹10,840 ·
  max DD −₹46,235.
- TIME60: identical trades (the 60-day stop never binds at ~13-day holds) — COUNTED ✓.
- TRAIL3 (native + trailing stop highest-close − 3×ATR(14)): 2025 +₹40,182 (110t,
  WR 71.8%) · 2026 +₹40,010 (141t, WR 60.3%) · DD −₹72,585 — COUNTED ✓, but it halves
  the 2026 total versus BASE and deepens the drawdown; the native exit is better.
- TRAIL2: −₹11,722 / −₹39,528 — the tight trail kills it. NOT SELECTED.
Caution: BASE has no downside stop — its worst 2025 trade (−₹41,345) rode a falling
name down until a middle-band close finally fired.

### RSI-REV — RSI(14) daily reversion + 60-day time stop — COUNTED ✓
Entry: RSI(14) crosses back up through 30 after RSI ≤ 30 → next open.
Exit (native): first close with RSI ≥ 70 → next open, or +10% from entry intraday,
whichever first. No downside stop in BASE.
- TIME60 (native + exit at the open of the 60th trading day after entry): 2025 —
  33 trades, **+₹63,576**, WR 60.6%, avg hold 45.5 d, worst −₹22,630 · 2026 —
  43 trades, **+₹108,109**, WR 55.8%, avg hold 35.1 d, worst −₹15,040 ·
  max DD −₹99,432 — COUNTED ✓ and strictly better than BASE on total AND drawdown
  (the time stop frees names for re-entry and caps the ride-down tail).
- BASE: 2025 +₹47,222 (23t, WR 82.6%, hold 93.3 d, worst −₹69,730) · 2026 +₹86,095
  (28t, WR 67.9%, hold 53.5 d) · DD −₹217,124 — COUNTED ✓ by the bar, but 11 of its 28
  trades in 2026 are FORCED marks at the data edge (long holds still open on
  2026-11-13), and its drawdown is 1.6× its combined profit. The TIME60 row is the
  honest version of this system.
- TRAIL2 −₹33,520 / +₹4,253 · TRAIL3 −₹3,328 / +₹64,960 — NOT SELECTED.

### MACD-D — MACD(12,26,9) daily — COUNTED ✓ (thin)
Entry: MACD line crosses above signal → next open. Exit: cross below → next open.
- BASE: 2025 — 216 trades, **+₹64,237**, WR 31.5%, avg hold 13.2 d, worst −₹19,175 ·
  2026 — 193 trades, **+₹14,101**, WR 32.6%, avg hold 11.8 d, worst −₹14,740 ·
  max DD −₹159,640. TIME60 near-identical (2026 +₹13,691) — COUNTED ✓.
- Caution: payoff-shaped (WR ~32%), and the equity-curve drawdown (−₹159,640) is twice
  the combined profit (+₹78,338); 8 of the 2026 trades are FORCED marks.
- TRAIL2/TRAIL3 turn 2025 negative — NOT SELECTED.

### EMA200-X + TRAIL3 — counted by the letter of the bar; weakest row in Part B
Entry: close crosses above EMA(200) → next open. Exit: close crosses below EMA(200)
→ next open, or trailing stop highest-close − 3×ATR(14).
- TRAIL3: 2025 +₹10,082 (27t, WR 22.2%) · 2026 +₹4,822 (101t, WR 15.8%) · DD −₹114,557.
- Why it is flagged: EMA(200) is only defined from ~Jul 2025 on this store, so its
  2025 is a half-window; the BASE system loses in both years (−₹6,339 / −₹48,084) and
  the overlay, not the signal, produces the positive sign; drawdown is 7.7× the combined
  profit. COUNTED ✓ mechanically — treated here as an artefact, NOT SELECTED as a card.

### The rest of Part B — NOT SELECTED (BASE lines; overlays in the JSON)
- EMA50-X: +₹125,239 (2025) / **−₹296,359** (2026) — the year's biggest flip.
- EMA100-X: +₹108,764 / −₹95,289. RSI50: +₹116,400 / −₹181,127.
  ST-D (Supertrend(10,3) daily): +₹104,932 / −₹219,337.
  Daily trend-following in these names was a 2025 trade; in 2026 the same entries bleed.
- GCROSS (EMA 50/200): 6 trades in 2025 (170-day avg hold), 10 in 2026 — below the
  10-trades-in-2025 bar on count and negative at BASE (−₹17,250 / −₹66,610).
- EMA200-X BASE/TRAIL2/TIME60 and all TRAIL overlays of the trend systems: negative in
  at least one year — full rows in the results JSON.

**Part B structural read:** on daily candles the direction of the edge reverses versus
the intraday grid: trend entries are the unstable ones (2025-only), and the two
reversion entries — buy the close back inside the lower Bollinger band, buy RSI's turn
up out of oversold — are the only systems positive in both years at their native exits.
The 60-trading-day time stop is the one overlay that clearly improves its system
(RSI-REV); ATR trailing stops damage every reversion system they touch at ×2 and do
not help at ×3 except cosmetically.

## NOVEMBER CF
None. Per the frozen spec, a November counterfactual is produced only for a Part A
PASS config; there is none. (Part B's frozen design has no November leg — its windows
are the Jan–Oct years.)

## Honest one-liner

**Intraday, no indicator at any tested value earns robustly in these 25 names — 414
parameter sets, zero robust in even one year; but on daily candles two reversion
systems do earn in both years: Bollinger(20,2) band-return (+₹28,946 / +₹100,067) and
RSI(14) oversold-turn with a 60-day time stop (+₹63,576 / +₹108,109), with MACD(12,26,9)
daily a thin third (+₹64,237 / +₹14,101) — all payoff- or patience-shaped, all carrying
drawdowns that demand forward evidence before a rupee follows them.**
