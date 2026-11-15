# PHASE-3 TUNING — NIFTY · BUILDUP / SPECULATION STATE CONDITIONING ON TUNED v1

**Run:** 2026-11-14, under the owner's order of 09:02 IST — tuning does
not stop until the result is got; tuning = adjusting parameters in small
turns, on his named surface: long buildup / unwinding and the other
buildup classes, previous-day volume vs today's, call rates vs put
rates (where the speculation is positioning), and whether our trades go
in the correct direction relative to all that. Spec frozen before
scoring: `phase3_buildup_nifty_SPEC.md` (09:09 IST). Script:
`phase3_buildup_nifty_score.py` → `phase3_buildup_nifty_results.json`.
**Research only — no book, ledger or job changed.** Paper basis
throughout: Nifty premiums per 1 lot (65), cost ₹220/trade inside every
stored net, buying only.

**What was tuned:** not entries, not exits, not another confidence
score (phases 2/2B closed that dial with measured reasons). This round
conditions TUNED v1's own 74 legs on the **morning buildup/speculation
state** — futures buildup class (price × OI since open), futures
relative volume (today vs previous day, same clock), and the near-band
call-minus-put OI shift (the crowd's positioning) — read at 10:00 and
11:00, conditioning only legs entered at/after the read.

## VERDICT — FAIL AT ALL 20 GRID POINTS. THE STATE DOES NOT SEPARATE THIS BOOK'S LEGS THROUGH ANY FROZEN DIAL.

No conditioner passes the unmoved bar. The reasons are measured, and
they are different per dial:

- **The futures buildup quadrant barely resolves on this book's
  mornings.** Of the 45 legs the 10:00 read conditions, **32 sat on
  NEUTRAL mornings** (futures OI moved < 0.50% from the open by 09:55)
  and only 13 on a resolved quadrant (11 SHORT_BUILDUP, 1 LONG_BUILDUP,
  1 LONG_UNWINDING, 0 SHORT_COVERING). A direction-alignment rule
  therefore mostly idles the book for having no signal, not for being
  wrong — ALIGN at 10:00 keeps 3 of 45 conditioned legs — and what it
  keeps still fails WR and placebo.
- **Volume is U-shaped against this book's profit** (10:00 conditioned
  legs, RELVOL tercile means: low ₹1,296.67 · mid ₹400.75 · high
  ₹1,576.60). No monotone gate at 1.0 / 1.1 / 1.25 — on either volume
  definition — can capture a U; all six volume points fail the
  placebo (0.435–0.88).
- **The crowd reading skews LONG and agrees too cheaply.** Among
  scorable 10:00-conditioned legs the crowd was LONG on 30, SHORT on
  10, FLAT on 0. Adding speculation agreement to alignment produces
  the day's highest ₹/trade-day (₹2,200.35) on a kept-conditioned
  population of **two legs** — and still fails WR (55.6%) and placebo
  (0.79).
- **The one genuine shape the state shows is where family B's money
  already sits:** fade legs on NEUTRAL-buildup mornings average
  **+₹2,131.48** (15 legs, +₹31,972.25) — the fade earns when the
  morning has *not* resolved into a buildup at all. Every rule that
  keeps those legs keeps them unconditionally; no state dial is doing
  that work.

## Data build (disclosed; upstream of the frozen spec)

The Bank intraday-OI dataset's Nifty counterpart did not exist: Nifty
futures were stored price-only (fields 6–7 stripped in round 4), and
the fetched option cache held only scattered traded strikes.
`phase3_fetch.py` completed the dataset via the same expired-
instruments route as the Bank build (browser UA, 0.3 s pacing, **no
HTTP 429**): 11 in-force monthly futures contracts in full 7-field
form (`phase3_buildup_data/futures/`), and **1,531 of 1,574 needed
near-band option contract-days** fetched into the shared cache (43
were already complete); **20 contract-days were unserved by the
source** and stand as NC below — never filled, never estimated.

## Control (Step 0 — reproduced exactly before any scoring)

From `november_books_fix_repair_nifty_legs.csv`: **74 legs ·
+₹103,050.25 · WR 51.4% (38 wins) · 66 trade-days · ₹1,561.37/trade-day
· March 2026 −₹1,216.50, the only red month.** Halves +₹52,319.25 /
+₹50,731.00; ex-top-3 +₹69,585.25; day profile 37 green / 29 red / 139
no-trade of 205. N-FIX-1 anchors reproduced: 8 stood-down legs
−₹14,119.75, repaired total +₹117,170.00. Median premium ₹213.025
verified.

## Coverage / NC (Step 1)

States were computed for all 66 leg-days at both reads (plus Nov 3):

| Component | NC leg-days @10:00 | NC leg-days @11:00 |
|---|---|---|
| Futures buildup (a) | **0 / 66** | **0 / 66** |
| Relative volume (b) | **0 / 66** | **0 / 66** |
| RELVOL5 (b-variant) | **0 / 66** | **0 / 66** |
| Call/put speculation (c) | **7 / 66** | **8 / 66** |

The futures surface is complete. The speculation surface is NC
wherever an unserved band contract sits in that day's band — those
legs are kept and flagged, per the freeze (ALIGN+SPEC carries 5
NC-kept legs at 10:00, 1 at 11:00; PF-ALIGN+SPEC 1 and 1). The
conditioned populations: **45 legs at the 10:00 read** (entries
≥ 10:00), **8 legs at the 11:00 read** — the 11:00 grid is thin by
construction and its verdicts are correspondingly weak evidence.

## Results (Steps 2 + 3) — all 20 grid points FAIL

**10:00 read** (45 conditioned legs; structural base = 29 legs,
+₹53,940.00):

| Rule | Kept | Total | WR | ₹/TD | Placebo | Dropped (n · total · mean) | Verdict |
|---|---|---|---|---|---|---|---|
| ALIGN | 32 | +₹61,232.75 | 53.1% | ₹1,913.52 | 0.715 | 42 · +₹41,817.50 · ₹995.65 | FAIL — WR, total (short ₹597.40), placebo, new red Jun/Aug |
| ALIGN+SPEC | 36 | +₹77,012.25 | 55.6% | **₹2,200.35** | 0.790 | 38 · +₹26,038.00 · ₹685.21 | FAIL — WR, placebo, new red Jun/Aug |
| VOL-1.0 | 56 | +₹81,390.50 | 51.8% | ₹1,661.03 | 0.435 | 18 · +₹21,659.75 · ₹1,203.32 | FAIL — WR, placebo, dropped-set, new red Aug |
| VOL-1.1 | 52 | +₹83,716.75 | 53.8% | ₹1,781.21 | 0.650 | 22 · +₹19,333.50 · ₹878.80 | FAIL — WR, placebo, new red Aug |
| VOL-1.25 | 45 | +₹81,269.00 | **57.8%** | ₹1,934.98 | 0.815 | 29 · +₹21,781.25 · ₹751.08 | FAIL — WR, placebo, new red Jun/Aug |
| VOL5-1.1 | 46 | +₹76,528.25 | 52.2% | ₹1,779.73 | 0.650 | 28 · +₹26,522.00 · ₹947.21 | FAIL — WR, placebo, new red Aug |
| PF-ALIGN | 57 | **+₹103,059.25** | 56.1% | ₹1,981.91 | **0.920** | 17 · −₹9.00 · −₹0.53 | FAIL — WR, placebo, new red Aug |
| PF-ALIGN+SPEC | 57 | +₹100,313.00 | 56.1% | ₹1,929.10 | 0.905 | 17 · +₹2,737.25 · ₹161.01 | FAIL — WR, placebo, new red Aug |
| FB-ONLY | 73 | +₹99,370.25 | 50.7% | ₹1,528.77 | 0.210 | 1 · +₹3,680.00 · ₹3,680.00 | FAIL — WR, placebo, dropped-set |
| FB-COMBO | 56 | +₹99,379.25 | 55.4% | ₹1,948.61 | 0.900 | 18 · +₹3,671.00 · ₹203.94 | FAIL — WR, placebo, new red Aug |

**11:00 read** (8 conditioned legs; the book barely moves — every
point keeps 67–74 legs):

| Rule | Kept | Total | WR | ₹/TD | Placebo | Dropped (n · total · mean) | Verdict |
|---|---|---|---|---|---|---|---|
| ALIGN | 68 | +₹95,124.00 | 51.5% | ₹1,534.26 | 0.380 | 6 · +₹7,926.25 · ₹1,321.04 | FAIL — WR, placebo, dropped-set |
| ALIGN+SPEC | 67 | +₹91,444.00 | 50.7% | ₹1,499.08 | 0.000 | 7 · +₹11,606.25 · ₹1,658.04 | FAIL — WR, placebo, dropped-set |
| VOL-1.0 / 1.1 / 1.25 | 69 | +₹98,147.50 | 52.2% | ₹1,608.98 | 0.480 / 0.540 / 0.435 | 5 · +₹4,902.75 · ₹980.55 | FAIL — WR, placebo |
| VOL5-1.1 | 68 | +₹101,617.50 | 52.9% | ₹1,665.86 | 0.880 | 6 · +₹1,432.75 · ₹238.79 | FAIL — WR, placebo |
| PF-ALIGN | 68 | +₹95,124.00 | 51.5% | ₹1,534.26 | 0.365 | 6 · +₹7,926.25 · ₹1,321.04 | FAIL — WR, placebo, dropped-set |
| PF-ALIGN+SPEC | 67 | +₹91,444.00 | 50.7% | ₹1,499.08 | 0.000 | 7 · +₹11,606.25 · ₹1,658.04 | FAIL — WR, placebo, dropped-set |
| FB-ONLY | 74 | +₹103,050.25 | 51.4% | ₹1,561.37 | 0.000 | 0 · ₹0 · — | FAIL — WR, placebo, dropped-set (rule never binds at 11:00; placebo is 0.000 mechanically — every draw equals the total) |
| FB-COMBO | 68 | +₹95,124.00 | 51.5% | ₹1,534.26 | 0.400 | 6 · +₹7,926.25 · ₹1,321.04 | FAIL — WR, placebo, dropped-set |

Notes on the near misses, honestly: **PF-ALIGN at 10:00 is the
closest point of the phase** — it preserves 99.99% of the book's
total (+₹103,059.25 vs +₹103,050.25) because the 17 A/C legs
alignment idles netted **−₹9.00 in aggregate** — a coin flip, not a
separation (kept-conditioned mean ₹1,754.26 vs dropped mean −₹0.53
looks dramatic and is carried by a handful of legs; the placebo at
0.920 and WR at 56.1% both miss the bar, and August still turns
red). **VOL-1.25 at 10:00** posts the phase's best WR (57.8%) and
still misses 60%. No point clears the WR leg and the placebo leg
together; most clear neither.

## Family B — the inverted readings, called out separately

The pre-registered inverted hypothesis (from phase 2B's diagnosis):
the fade should earn more when buildup opposes it or is neutral, and
less when the crowd is already positioned for the fade's move. The
10:00 split of family B's 26 conditioned legs:

| Buildup vs the fade leg | Legs | Total | Mean/leg |
|---|---|---|---|
| **Agrees** (crowd positioned for the fade's move) | 1 | +₹3,680.00 | +₹3,680.00 |
| **Opposes** | 10 | +₹9,854.25 | +₹985.42 |
| **Neutral** | 15 | **+₹31,972.25** | **+₹2,131.48** |

The inverted rule therefore binds exactly **once** at 10:00 — and
the leg it removes is a +₹3,680 winner (FB-ONLY's entire dropped
set). With n = 1 on the "agrees" cell, the hypothesis is not
disproved; it is **unsupported** — the data contains essentially no
mornings where the crowd had pre-positioned for a fade, because on
fade days the morning buildup is usually NEUTRAL (15 of 26) or
opposing (10 of 26). The fade's edge lives in the neutral cell,
where the inverted rule — correctly, by its own design — does
nothing. At 11:00 the rule never binds at all. There is no
family-B buildup dial to tune: the conditioning event the rule
waits for does not occur in this book's year.

## Diagnostics (Step 4 — 10:00 conditioned legs, not gated)

Mean net by futures buildup class (pooled · family B · families A/C):

| Class | Pooled | Family B | Families A/C |
|---|---|---|---|
| LONG_BUILDUP | 1 leg · +₹3,680.00 | 1 · +₹3,680.00 | 0 |
| SHORT_COVERING | 0 legs | 0 | 0 |
| SHORT_BUILDUP | 11 · +₹889.73 | 10 · +₹985.42 | 1 · −₹67.25 |
| LONG_UNWINDING | 1 leg · +₹3,680.00 | 0 | 1 · +₹3,680.00 |
| NEUTRAL | 32 · +₹998.85 | 15 · **+₹2,131.48** | 17 · **−₹0.53** |

The pooled NEUTRAL mean (+₹998.85) is entirely family B: on neutral
mornings the A/C legs netted −₹9.00 across 17 legs — dead scratch —
while the fade legs made ₹2,131 a leg. By crowd class: LONG mornings
30 legs, mean +₹746.12; SHORT mornings 10 legs, mean +₹1,101.45;
FLAT never occurred among scorable legs (the ±0.25 band-OI band is
rarely inhabited — the crowd reading is decisive in % terms because
the band's base OI is small). RELVOL terciles are U-shaped (above).
Nothing here contradicts the grid verdicts; the diagnostics explain
them.

## November counterfactual (Step 5 — descriptive only)

v1's one November leg — **Nov 3, CE 23600 weekly, family C, entry
09:50, +₹3,036.50** — entered before both reads, so it is
unconditioned and **KEPT at all 20 grid points by construction**.
Its morning state: at 10:00 **NEUTRAL** (futures dP +0.288%, dOI
−0.252% — inside the OI dead-band), RELVOL 1.1082, RELVOL5 1.3331;
at 11:00 **SHORT_COVERING** (dP +0.4475%, dOI −0.91%), RELVOL
1.1471, RELVOL5 1.1759. The speculation component is **NC on Nov 3
at both reads** (one band contract unserved that morning) — stated,
not estimated. Descriptively: had the leg entered after the 10:00
read, ALIGN would have **dropped** November's only Nifty win
(NEUTRAL drops); after the 11:00 read, ALIGN would have kept it
(SHORT_COVERING = BULL, CE aligned). One leg, two reads, opposite
answers — which is the phase in miniature.

## Distinctness and disclosures

- No standalone signal was built: nothing here fires a trade;
  IOI-1/IOI-2's band-quadrant entries, FLOW-VOL's volume-thrust
  entries and the day-level OI V1–V3 next-day signals are different
  mechanisms (they generate legs; this round only keeps/idles
  TUNED v1's). No phase-2/2B factor, percentile or composite is
  used. No rule collapsed into a closed mechanism, so none was
  dropped on distinctness grounds.
- Implementation reading, disclosed: RELVOL/RELVOL5 compare
  today's in-force futures contract against **the same contract**
  on the previous trading days (the spec pins the days; the
  same-contract reading avoids the front-switch volume artefact).
- Spec wording slip, recorded not edited: the frozen spec's Step-2
  intro says "nine rules — 18 grid points"; its own table lists
  ten rules and the operative count is **10 rules × 2 reads = 20
  grid points**, as scored.

## Bottom line

The buildup/speculation surface is now measured on every one of
this book's 66 days — the dataset exists, complete on the futures
side — and it knows one true thing about TUNED v1: **the fade
family earns on mornings when no buildup has formed** (NEUTRAL,
+₹2,131/leg), which is a description of the book, not a dial:
every rule that exploits a resolved state either idles the book
for silence (alignment), chases a U-shape (volume), agrees too
cheaply (crowd), or waits for an event that occurs once a year
(family-B inversion). **No grid point passes; TUNED v1 stands
exactly as it stands; nothing is adopted from this phase.** The
owner's question — are we going in the correct direction relative
to the buildup and the speculation — now has a measured answer for
this book: direction-relative conditioning does not separate its
winners from its losers at either read, at any frozen threshold.
