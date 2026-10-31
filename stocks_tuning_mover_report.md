# Stocks EQUITY — Tuning Loop LINE 5: Morning-Mover Deepening (EXT + Pooled 50)

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money ₹0.**
**Every rupee figure is provisional per 100 shares. Net = gross −
₹40/trade flat. Window Jan–Oct 2026 (October = 1–28 Oct).**

**STATUS OF THIS LINE: DIAGNOSTICS ONLY.** Everything below is an
observation on in-sample data. No pass is claimed, no frozen rule
is changed, nothing is adopted. The Line 4 verdict — the
Morning-Mover Second Signal TRANSFERS to the new 25 — already
stands and is not re-judged here. Family list frozen BEFORE
scoring in `stocks_tuning_mover_frozen.md`. Engine:
`stocks_tuning_mover.py`. Results JSON:
`stocks_tuning_mover_results.json`. Trade dumps:
`mover_<FAMILY>_trades.csv`.

**MOVER-A (the frozen rule):** pre-move |last close before 10:00 ÷
first-bar open − 1| ≥ 1.0% → discard the day's first V5-stream
signal, trade the next, one re-entry allowed (cap 2), T125 exits
(+1.25% / −0.5%). Home anchor: 424 chains, +₹84,671.74, breadth
16/25. Ext anchor: 199 chains, +₹164,483.29, breadth 22/25.
Pooled anchor: 623 chains, +₹249,155.03, breadth 38/50.

## Validation — ALL SIX ANCHORS PASS to the paisa

The Line 5 builder (Line 2b parametrized chain builder run per
universe over the frozen V5 heads) reproduces, exactly: home
MOVER-A (424 chains / 698 trades / +₹84,671.74, halves +₹52,884.19
/ +₹31,787.55, Oct +₹16,825.42, breadth 16/25); ext MOVER-A (199 /
300 / +₹164,483.29, +₹73,142.55 / +₹91,340.74, Oct +₹39,984.55,
22/25); pooled MOVER-A (623 / 998 / +₹249,155.03, +₹126,026.74 /
+₹123,128.29, Oct +₹56,809.97, 38/50, top-3 34.1%); home MOVER-B
10:15 (589 / 941 / +₹169,328.31, breadth 24/25); home
SAME-direction (385 / 639 / +₹92,923.38, breadth 18/25); home
mover-DOWN partition (221 chains / +₹58,812.88, breadth 19/25).
Every Line 5 number below is anchored to this reproduction.

---
## M1 — MOVER-B (10:15 measurement) off-home — **REPLICATES**

Home reference (Line 2b R4, OBS-2b-1): measuring the pre-move at
10:15 instead of 10:00 doubled the home net (+₹84,671.74 →
+₹169,328.31), lifted breadth 16/25 → 24/25, both halves up. The
question here: does that advantage exist on stocks the rule never
saw, and on the pooled 50?

| Universe | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|
| NEW 25 @10:00 (A) | 199 | 300 | +164,483.29 | +826.55 | +73,142.55 | +91,340.74 | +39,984.55 | 22/25 |
| **NEW 25 @10:15 (B)** | **328** | **481** | **+295,288.72** | **+900.27** | **+151,540.58** | **+143,748.14** | **+81,933.52** | **25/25** |
| POOLED 50 @10:00 (A) | 623 | 998 | +249,155.03 | +399.93 | +126,026.74 | +123,128.29 | +56,809.97 | 38/50 |
| **POOLED 50 @10:15 (B)** | **917** | **1,422** | **+464,617.03** | **+506.67** | **+243,806.97** | **+220,810.06** | **+118,748.54** | **49/50** |

(All figures provisional per 100 shares.)

Reading: the 10:15 advantage **replicates off-home on every
dimension the home battery used** — net (+80% on the new 25,
+86% pooled), expectancy per chain, both halves (each roughly
doubles), October, and breadth. On the new 25 the breadth is
**25/25 — every single stock net-positive** (the weakest,
KOTAKBANK, is still +₹498.88); pooled breadth is 49/50 with
top-3 share *falling* to 29.0%. Chain win rate rises to 62.5%
(ext-B) / 59.9% (pooled-B). The later measurement admits more
qualifying days (328 vs 199 chains on ext) and they are better,
not diluted — the same shape as at home, stronger.

One nuance that does **not** replicate: at home, the 10:15
window uniquely turned the re-entry leg positive (+₹10,642.17).
Off-home the re-entry leg stays negative at 10:15 (ext-B
−₹16,671.52; pooled-B −₹6,029.35 on 505 trades, ≈breakeven and
much less negative than pooled-A's −₹26,640.48). The off-home
10:15 gain is carried entirely by the direct leg (ext-B direct
+₹311,960.24, exp +₹951.10/trade).

- **OBS-5-1:** the 10:15 measurement advantage (OBS-2b-1)
  replicates and strengthens off-home — pooled 50: +₹464,617.03,
  breadth 49/50, top-3 29.0%. Observation only; the frozen
  candidate remains the 10:00 rule and nothing is re-specified
  from in-sample data.
- **OBS-5-2:** the home property "re-entry leg turns positive
  at 10:15" does not replicate on the new 25; off-home, later
  measurement improves the direct leg and merely shrinks the
  re-entry leak.

**Verdict M1: REPLICATES.**

---
## M2 — Threshold plateau on the NEW 25 — **MIXED**

Home reference (Line 2b R1): a smooth plateau — every threshold
{0.75, 1.0, 1.25, 1.5%} both-halves positive, breadth ≥16/25,
total falling monotonically and expectancy rising monotonically
as the threshold rises; the frozen 1.0% an interior point.

| Threshold | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 |
|---|---|---|---|---|---|---|---|---|---|
| 0.75% | 451 | 647 | +156,786.54 | +347.64 | +76,029.57 | +80,756.97 | +18,767.48 | 19/25 | 62.3% |
| **1.0% (frozen)** | **199** | **300** | **+164,483.29** | **+826.55** | **+73,142.55** | **+91,340.74** | **+39,984.55** | **22/25** | 48.8% |
| 1.25% | 82 | 129 | +49,392.98 | +602.35 | +8,768.40 | +40,624.58 | +25,965.74 | 19/25 | 95.9% |
| 1.5% | 30 | 52 | +30,775.76 | +1,025.86 | +23,755.60 | +7,020.16 | +18,083.57 | 12/25 | 75.6% |

(All figures provisional per 100 shares.)

What replicates: **there is no cliff at the frozen point.**
Every threshold is net-positive in **both halves** on the new
universe too, and lowering to 0.75% roughly preserves the total
(+₹156,786.54 on 451 chains) — the frozen 1.0% is not a fitted
spike off-home either.

What does not: **the smooth plateau shape.** At home the total
fell monotonically with the threshold; off-home the total
*peaks at the frozen 1.0%* (0.75% adds 252 chains but slightly
*less* money — heavier dilution than at home). Expectancy is
non-monotonic (₹826.55 at 1.0% → ₹602.35 at 1.25% → ₹1,025.86
at 1.5%), and the high end thins out fast: large caps rarely
pre-move ≥1.25% before 10:00 (82 and 30 chains), breadth drops
to 12/25 at 1.5% and top-3 share balloons (95.9% at 1.25% —
a few chains carrying the cell). The working region is real
off-home; the tidy gradient is a home-universe feature.

- **OBS-5-3:** off-home, the threshold response is a *region
  with a peak at the frozen 1.0%*, not the home plateau —
  0.75–1.0% is the usable band on liquid large caps; ≥1.25%
  starves the rule and concentrates it.

**Verdict M2: MIXED** — the both-halves-positive region
replicates (no cliff); the smooth plateau shape does not.

---

## M3 — SAME-direction variant on the NEW 25 — **REPLICATES**

Home reference (Line 2b R5, OBS-2b-2): requiring the traded
signal to match the pre-move's sign modestly helped at home
(+₹84,671.74 → +₹92,923.38, exp/chain +₹199.70 → +₹241.36,
breadth 16 → 18).

| Variant (NEW 25) | Chains | Trades | Net ₹ | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 |
|---|---|---|---|---|---|---|---|---|---|
| ANY (frozen MOVER-A) | 199 | 300 | +164,483.29 | +826.55 | +73,142.55 | +91,340.74 | +39,984.55 | 22/25 | 48.8% |
| **SAME-direction** | **186** | **284** | **+168,145.99** | **+904.01** | **+77,413.15** | **+90,732.84** | **+38,882.95** | **23/25** | 47.2% |

(All figures provisional per 100 shares.)

The same-direction restriction **helps off-home too, in the
same modest way**: +₹3,662.70 more total (+2.2%) on 13 fewer
chains, expectancy +9.4% per chain, breadth 22 → 23, both
halves up or flat (Jan–May +₹77,413.15 vs +₹73,142.55; Jun–Oct
+₹90,732.84 vs +₹91,340.74), October essentially unchanged.
The direct leg strengthens (exp +₹1,009.22/trade); the
re-entry leg stays negative (−₹19,568.09), as it does in every
ANY/SAME cell off-home. The effect is smaller than at home
(+2.2% vs +9.7% on total) but the same sign on every read —
this is now the same observation on two independent universes.

- **OBS-5-4:** OBS-2b-2 replicates off-home — same-direction
  restriction is mildly positive on total, expectancy and
  breadth on both universes. Still an observation: the frozen
  candidate is the ANY-direction rule, and no re-specification
  is made from in-sample data.

**Verdict M3: REPLICATES (modest help, same as home).**

---
## M4 — MOVER-DOWN ONLY on the pooled 50 (the "half-rule" read)

Home reference (Line 2b R2): the down flank was the engine at
home — 221 chains, +₹58,812.88, exp +₹266.12/chain vs the up
flank's +₹127.38, breadth 19/25 vs 13/25.

| Subset (POOLED 50) | Chains | Trades | Net ₹ | Share of pooled net | Exp/chain ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Top-3 |
|---|---|---|---|---|---|---|---|---|---|---|
| **Mover-DOWN only** | **306** | **483** | **+114,459.33** | **45.9%** | **+374.05** | **+53,057.54** | **+61,401.79** | **+32,374.72** | **36/50** | 36.7% |
| Mover-UP only (context) | 317 | 515 | +134,695.70 | 54.1% | +424.91 | +72,969.20 | +61,726.50 | +24,435.25 | 33/50 | 49.3% |
| Full pooled MOVER-A | 623 | 998 | +249,155.03 | 100% | +399.93 | +126,026.74 | +123,128.29 | +56,809.97 | 38/50 | 34.1% |

(All figures provisional per 100 shares.)

The down-only subset **stands on its own at scale**: 306
chains, +₹114,459.33, both halves solidly positive (+₹53,057.54
/ +₹61,401.79), breadth 36/50 — as a standalone book it would
be the second-strongest result in this entire search. But the
home story about *why* does not survive pooling:

| Flank exp/chain | Home 25 | New 25 |
|---|---|---|
| Mover-DOWN | +₹266.12 (221 ch) | +₹654.66 (85 ch) |
| Mover-UP | +₹127.38 (203 ch) | **+₹954.71 (114 ch)** |

The flank asymmetry **reverses** between universes: at home the
down flank pays 2.1× the up flank per chain; on the liquid
large caps the **up** flank pays 1.5× the down flank. Pooled,
the two flanks are near-equal (down ₹374.05 vs up ₹424.91 per
chain; 45.9% vs 54.1% of the net). "Stocks that fell in the
morning keep falling" is a home-watchlist behaviour; on large
caps, morning strength follows through at least as well.

- **OBS-5-5:** the mover-down dominance (Line 2b R2) is a
  home-universe property, not a market-wide one — flank
  asymmetry flips sign on the new 25. A down-only half-rule
  would still be a strong book pooled (+₹114,459.33, 36/50),
  but it is not "the engine" of the pooled result; the pooled
  edge is two-sided.

**Verdict M4: the down-only subset is strong standalone
(45.9% of the pooled net, both halves, 36/50 breadth), but the
home claim that the down flank is the dominant flank does NOT
replicate at scale — pooled, the flanks are near-equal and the
up flank leads per chain.**

---

## M5 — POOLED-50 month table, MOVER-A

| Month | Chains | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| Jan | 74 | 126 | −9,886.28 | −9,886.28 |
| Feb | 69 | 112 | −190.30 | −10,076.58 |
| Mar | 105 | 166 | +67,883.49 | +57,806.91 |
| Apr | 73 | 121 | +70,532.34 | +128,339.25 |
| May | 77 | 121 | −2,312.51 | +126,026.74 |
| Jun | 39 | 59 | +38,821.76 | +164,848.50 |
| Jul | 51 | 82 | +3,442.52 | +168,291.02 |
| Aug | 33 | 53 | +1,071.97 | +169,362.99 |
| Sep | 26 | 35 | +22,982.07 | +192,345.06 |
| Oct (1–28) | 76 | 123 | +56,809.97 | +249,155.03 |

(All figures provisional per 100 shares.)

Read: **7 of 10 months positive.** The three negative months
are small and early (Jan −₹9,886.28 is the worst month; Feb
−₹190.30 is a scratch; May −₹2,312.51). The cumulative turns
positive in March and never returns below zero. Two
disclosures the home-only table (Line 2b R3) understated:
(1) **time concentration is higher pooled** — the top-2 months
(Mar + Apr = +₹138,415.83) are **55.6%** of the total net,
versus April alone ≈30% at home; the pooled book leans on the
Mar–Apr stretch. (2) The pooled worst month (Jan, −₹9,886.28)
is worse than the home worst month (Sep, −₹2,272.08) — the
new universe started the year cold. Against that: no single
month carries the book (removing April still leaves
+₹178,622.69), the second half contributes steadily rather
than in one spike (Jun +₹38,821.76, Sep +₹22,982.07, Oct
+₹56,809.97), and both halves clear +₹123k.

**Verdict M5: a broad, mostly-positive month profile with a
real Mar–Apr concentration (top-2 = 55.6%) — recorded as the
pooled book's main time-concentration caveat.**

---

## M6 — Exit check on the pooled 50: T10 vs T125

Same qualifying days and chain mechanics; only the exit target
changes (1.0% vs 1.25%, stop −0.5% both). Chains re-form under
T10 (faster exits restart the signal search earlier), so this
is a true system variant, not a repricing.

| Exit (POOLED 50) | Chains | Trades | Net ₹ | Exp/chain ₹ | Chain win % | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|---|
| T10 (+1.0%) | 623 | 1,051 | +217,701.39 | +349.44 | 61.5 | +121,838.20 | +95,863.19 | +45,160.49 | 37/50 |
| **T125 (+1.25%, frozen)** | **623** | **998** | **+249,155.03** | **+399.93** | 56.5 | **+126,026.74** | **+123,128.29** | **+56,809.97** | **38/50** |

(All figures provisional per 100 shares.)

**The T125 preference is stable at scale.** T10 wins more
chains (61.5% vs 56.5%) but banks less per chain — net
−₹31,453.64 (−12.6%) versus T125, with the gap concentrated in
Jun–Oct (+₹95,863.19 vs +₹123,128.29) and October. Per-universe
context: at home T10 is much worse (+₹59,658.18 vs +₹84,671.74);
on the new 25 T10 is close (+₹158,043.21 vs +₹164,483.29) and
even a touch broader (23/25 vs 22/25) — but pooled, the frozen
exit remains the better one on net, both halves, October and
breadth. Nothing here argues for touching the frozen exit.

**Verdict M6: exit preference stable at scale — T125 > T10 on
the pooled 50, as at home.**

---

## Line 5 summary (diagnostics only — nothing adopted)

| Family | Question | Verdict |
|---|---|---|
| M1 | Does the 10:15 advantage replicate off-home? | **REPLICATES** — ext-B +₹295,288.72, breadth 25/25; pooled-B +₹464,617.03, 49/50 (OBS-5-1). Nuance: the positive re-entry leg at 10:15 is home-only (OBS-5-2). |
| M2 | Is the threshold a plateau off-home? | **MIXED** — both-halves-positive region replicates (no cliff at 1.0%); the smooth plateau shape does not (total peaks at 1.0%, high end starves) (OBS-5-3). |
| M3 | Does same-direction help off-home? | **REPLICATES** — +2.2% total, +9.4% exp/chain, breadth 23/25 on the new 25 (OBS-5-4). |
| M4 | Is mover-down the engine of the pooled book? | **NO** — down-only is a strong standalone book (+₹114,459.33, 36/50) but flank dominance reverses on the new 25; pooled flanks are near-equal (OBS-5-5). |
| M5 | Pooled month profile? | 7/10 months positive, worst Jan −₹9,886.28; **top-2 months (Mar+Apr) = 55.6%** — the pooled book's main caveat. |
| M6 | Is the T125 exit preference stable at scale? | **YES** — pooled T10 +₹217,701.39 < T125 +₹249,155.03; frozen exit stands. |

Net read of Line 5: the two home observations that mattered
most — the 10:15 measurement (OBS-2b-1) and the same-direction
restriction (OBS-2b-2) — both replicate on stocks the rule was
never tuned on, which strengthens the Morning-Mover's claim to
be a market-wide behaviour rather than a watchlist fit. The two
home colour notes (down-flank dominance, smooth threshold
plateau) do not generalise and are corrected above. The frozen
candidate spec (`stocks_vline_v2_candidate_spec.md`, 10:00 /
ANY-direction / T125) is **unchanged** — OBS-5-1 and OBS-5-4
would each need their own frozen spec and fresh window before
they could be claimed as anything, exactly as OBS-2b-1/2 did.

**Files:** this report; frozen list
`stocks_tuning_mover_frozen.md`; engine
`stocks_tuning_mover.py`; results
`stocks_tuning_mover_results.json`; trade dumps
`mover_A_old_trades.csv`, `mover_A_ext_trades.csv`,
`mover_M1_extB_trades.csv`, `mover_M1_poolB_trades.csv`,
`mover_M2_T075/T125/T150_trades.csv`, `mover_M3_extSD_trades.csv`,
`mover_M4_poolDown_trades.csv`, `mover_M6_poolT10_trades.csv`.

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.
