# Stocks EQUITY — Line M2 — Root-cause repair of the H1 October cell

Equity cash intraday only, LONG/SHORT. **Paper only — real money
₹0, no orders.** Every figure: **provisional per 100 shares,
₹40/trade** flat cost deducted. **Home 25 only**, Jan–Oct 2026
(October = full month Oct 1–30 via the validated 1-min
aggregation). User's order: the October cell (+₹34,124.43) is
"not bad" — find **why** it fails the other months, fix the root
cause, apply the fix. Protocol: anchors first, diagnosis before
any fix, fix families frozen in `stocks_M2_frozen.md` before
scoring.

## The cell

10:00 measurement · |pre-move| ≥ 0.5% · FOLLOW · first V5 pooled
signal at/after 10:00 in the move's direction · chain cap 2 ·
exits +1.25% / −0.65%, 15:10 square-off. (H1 HIT-1, exact.)

## Anchors — reproduced before anything was believed

Regenerated end-to-end with the H1 engine (`stocks_M2_diag.py`),
asserted to the paisa: October **182 trades / +₹34,124.43**
(breadth 19/25; event +₹14,360.75 / no-event +₹19,763.68) ·
Jan–Sep **1,431 trades / −₹63,538.43** (Jan–May −₹38,658.84 ·
Jun–Sep −₹24,879.59) · lag-placebo Jan–Sep **−₹18,135.89** ·
timing audit **2,374 trades, 0 violations**.

## Step 1 — Root-cause diagnosis

October's population vs the Jan–Sep population, trade by trade,
on ex-ante dimensions only (full tables: `stocks_M2_diag.json`;
base trades: `stocks_M2_base_trades.csv`).

### What does NOT explain it

- **Direction.** October won on both sides (LONG +₹11,490.68,
  SHORT +₹22,633.75). Jan–Sep lost on both — and the guilty side
  flips by half: SHORT is the Jan–May hole (−₹43,440.93), LONG is
  the Jun–Sep hole (−₹19,766.29). No direction restriction can
  fix both halves.
- **Market volatility.** The "October was just a wild month"
  story fails its own numbers: correlation between monthly mean
  stock ADR% and the cell's monthly expectancy is **−0.018**
  (zero). March 2026 was *more* volatile than October on both
  measures (stock ADR 3.27% vs 2.71%; Nifty daily range 1.54% vs
  1.38%) and the cell **lost** ₹4,413.11 in March. September had
  the *lowest* ADR of the year and was the cell's second-best
  month. Volatility is not the separator.
- **Trend regime alone.** October was indeed 100% below-50DMA
  days — but below50 Jan–Sep is the cell's *worst* bucket
  (−₹40,693.78), and above50 is also negative (−₹22,844.65).
  "Trade only below-trend" by itself keeps most of the hole.
- **Setup mix, event context, entry time, stocks.** The dominant
  setup (skill_or_breakdown) is both October's payer (+₹25,086.08)
  and Jan–Sep's biggest loser (−₹41,654.58) in the same
  proportion. Event and no-event trades both win in October and
  both lose Jan–Sep. October's breadth is genuine (19/25) but
  top-heavy: TVSMOTOR alone is +₹18,550.22 of the +₹34,124.43.
  October's winners are not a different stock set — GLENMARK,
  Jan–Sep's worst (−₹28,182.08), *made* money in October.
- **Exit geometry.** Targets pay ~+₹1,028/trade and stops cost
  ~−₹637/trade in every period. What changes is the ratio:
  October reached target 64 times vs 77 stops; Jan–Sep, 363 vs
  776. Same exits — the followed moves simply kept going in
  October and reversed the rest of the year. That is a population
  fact, not an exit fact.

### The separator: qualifier strength × trend regime

| Jan–Sep 2026 | below50 (979 tr) | above50 (452 tr) | all |
|---|---|---|---|
| **move 0.5–1.0%** | **+₹6,830.03** (598 tr, exp +₹11.42) | −₹29,836.04 (303 tr, exp −₹98.5) | −₹23,006.01 |
| **move ≥1.0%** | −₹47,523.81 (381 tr, exp −₹124.7) | +₹6,991.39 (149 tr, exp +₹46.9) | −₹40,532.42 |
| **all** | −₹40,693.78 | −₹22,844.65 | −₹63,538.43 |

October (all 182 trades on below50 days): 0.5–1.0% band
**+₹36,166.23** (117 trades, exp +₹309); ≥1.0% band **−₹2,041.80**
— the violent-move bucket lost money *even in the cell's best
month*.

### Root cause (one statement)

**The cell has no cap on qualifier strength and no market-state
condition, so most of the year it follows moves that are already
exhausted.** A ≥1% move by 10:00 is the single largest loss
bucket in the book — 64% of the Jan–Sep hole on 37% of trades,
negative in both halves and in October — and moderate-move
follow-through only pays on below-trend days (its October
habitat, where a morning move is a weak-tape continuation);
on above-trend days the same moderate signals lose −₹98.5/trade.
October did not make the cell good; October was the one month
whose tape sat entirely inside the cell's only profitable state.
Remove that state-match and the rule is a −₹44/trade bleed.

## Step 2 — Fix loop results

All four families rebuilt with the engine over the full Jan–Oct
2026 (`stocks_M2_fix.py`; each family's count includes its own
lag-placebo; audits all clean). Full detail:
`stocks_M2_results.json`.

| Family | Trades | Net ₹ | Jan–May ₹ | Jun–Sep ₹ | Oct ₹ | Breadth | Own placebo (Jan–Sep) | Verdict |
|---|---|---|---|---|---|---|---|---|
| F1 band cap [0.5,1.0) | 1,020 | +12,582.87 | −12,317.38 | −11,265.98 | +36,166.23 | 11/25 | −5,011.87 (not beaten) | **FAIL** |
| F2 below50 gate | 1,161 | −6,569.35 | −38,257.57 | −2,436.21 | +34,124.43 | 11/25 | −5,943.08 (not beaten) | **FAIL** |
| F3 prior-day vol gate | 869 | −14,377.57 | −23,633.96 | −20,382.98 | +29,639.37 | 13/25 | −20,881.97 (beaten, moot) | **FAIL** |
| **F4 state gate** | **717** | **+42,418.91** | **+3,003.36** | **+3,249.32** | **+36,166.23** | **16/25** | **−906.88 (beaten)** | **ACCEPTED** |

- **F1** removes the violent-move bucket exactly as diagnosed
  (October even improves to +₹36,166.23) but the residual book
  still bleeds in both halves — the above-trend moderate-move
  population (−₹29,836.04 Jan–Sep) is untouched by a band cap.
- **F2** keeps all of October (the month was 100% below50) and
  still fails: below-trend days carry the ≥1% carnage
  (Jan–May −₹38,257.57). A regime gate without the band cap
  keeps the primary hole.
- **F3** fails both halves decisively. The volatility story,
  already rejected at month level (corr −0.018), is now rejected
  at day level too: gating on prior-day Nifty range ≥1% keeps a
  −₹44,016.94 Jan–Sep. **Volatility is not the root cause.**
- **F4** — the joint state — passes **all six acceptance legs**:
  October +₹36,166.23 ≥ +₹25,000 · Jan–May +₹3,003.36 > 0 ·
  Jun–Sep +₹3,249.32 > 0 · audit 1,081 trades / 0 violations ·
  own placebo −₹906.88 beaten (book Jan–Sep +₹6,252.68) ·
  breadth 16/25 ≥ 15.

### F4 month table (the repaired book)

| Month | Trades | Net ₹ |
|---|---|---|
| Jan | — | +9,167.30 |
| Feb | — | −4,716.39 |
| Mar | — | +2,670.25 |
| Apr | — | −11,047.96 |
| May | — | +6,930.16 |
| Jun | — | −3,402.16 |
| Jul | — | −1,130.92 |
| Aug | — | −4,657.75 |
| Sep | — | +12,440.15 |
| Oct | 117 | +36,166.23 |
| **Jan–Oct** | **717** | **+42,418.91** |

## Step 3 — Verdict

**A fix is accepted and frozen: F4, the state gate** —
`stocks_M2_candidate_spec.md` (December 2026 fresh-window
judging pre-registered: ≥40 trades, positive → confirmed,
negative → killed, <40 or ₹0 → extends to January).

Stated without dressing, because the user has been burned by
dressed numbers before:

1. **The repair is real against the frozen acceptance test** —
   the same test the base cell failed on every leg. October
   keeps its edge (+₹36,166.23, in fact slightly above the
   ungated cell, because the gate deletes October's own ≥1%
   losers), and both Jan–Sep halves turn positive.
2. **But the margin is thin and the shape is narrow.** Jan–Sep
   expectancy is only +₹10.42/trade; five months (Feb, Apr, Jun,
   Jul, Aug) remain negative — this repair does **not** deliver
   an every-month-green book. TVSMOTOR alone is ~60% of the
   full-period net (TVSMOTOR + ASTRAL ≈ 97%), and October is
   ~85% of it. Breadth on Jan–Sep alone is 11/25 (the 16/25 leg
   is the full-period figure, as frozen).
3. **The gate's components fail standalone** (F1, F2 above) —
   the pass belongs to the joint state the diagnosis identified,
   and a two-condition gate chosen from diagnosis splits carries
   more selection risk than a single mechanism. That is exactly
   what the December fresh window is for: the candidate is
   frozen to be judged there, not believed here.

**Root cause, delivered as ordered:** the October cell was never
a generally good rule — it is a moderate-move follow-through
that only pays on below-trend days. Ungated, it spent the year
following ≥1% exhaustion moves (64% of its Jan–Sep loss, losing
even in October) and chasing moderate moves in uptrend tape.
October was simply the month the market stayed in its one
profitable state. The state gate confines the rule to that
state — and December decides whether the state, or the selection
of it, was the real thing.

