# PHASE-2B TUNING — NIFTY · FAMILY-WISE CONFIDENCE (SELECTIVITY) ON TUNED v1

**Run:** 2026-11-14, under the owner's radio principle of 09:00 IST — "if
something is failing, you need to work on the thing and why it is failing
and you need to tune." Spec frozen before scoring:
`phase2b_tuning_nifty_SPEC.md` (09:02 IST). Script:
`phase2b_tuning_nifty_2026-11-14.py` → `phase2b_tuning_nifty_results.json`.
**Research only — no book, ledger or job changed.** Paper basis
throughout: Nifty premiums per 1 lot (65), cost ₹220/trade inside every
stored net, buying only.

**The diagnosis being tuned (from phase 2's failure):** phase 2's single
composite confidence score anti-selected this book (placebo 0.24–0.385,
score-to-outcome correlation −0.06) because the book mixes families with
opposite confidence geometry — the gap-fade legs earn by trading AGAINST
the gap at expensive premiums, which a global score marks down, while
other legs earn with-trend. One dial was used for two stations. **This
run measured confidence WITHIN each family only** — raw phase-2 factors
unchanged, each converted to a percentile inside the leg's own family,
keep-grid applied per family, placebo = random thinning inside each
family at the same proportions.

## VERDICT — FAIL AT ALL THREE LEVELS. SEPARATING THE STATIONS DID NOT FIX THE TUNING.

Family-wise ranking is less bad than the global score — totals at
comparable sizes are slightly higher, placebo percentiles rise from
0.24–0.385 to 0.185–0.435, and the strictest level's win rate (60.5%)
clears the 60% bar no phase-2 level cleared. But **random thinning inside
each family still usually beats the score**, the total bar fails at every
level, and a new red month (June) appears at every level. The deeper
finding: inside the gap-fade family itself, the score is *inverted* —
its correlation with outcomes there is **−0.354**, and at every level the
fade legs the score idles out-earn the ones it keeps by 2–9× per leg.
The fade family's money sits in its own most extreme legs (biggest gaps,
richest premiums), and "typical for this family = confident" marks those
down just as surely as the global score did. In the other two families
the score has essentially no shape at all (correlations +0.008, +0.068 —
noise). **This book's edge is not confidence-shaped; it is event-shaped —
fixed-point geometry paying on extremes — and no re-centring of these
entry factors makes a confidence dial for it.**

## Control (Step 0 — reproduced exactly before any scoring)

From `november_books_fix_repair_nifty_legs.csv`: **74 legs · +₹103,050.25
· WR 51.4% (38 wins) · 66 trade-days · ₹1,561.37/trade-day · March 2026
−₹1,216.50, the only red month.** N-FIX-1 anchors reproduced: 8
stood-down legs −₹14,119.75, repaired total +₹117,170.00. Median premium
₹213.025 verified. Day profile of the full book: 37 green / 29 red / 139
no-trade of 205 calendar days.

## Family split (Step 1 — by the store's `family` column; all ≥ 8 legs, all gated)

| Family | Producing rep(s) | Legs | Net Jan–Oct | Character |
|---|---|---|---|---|
| A | (lA) v2 (19) · V5 v2 (9) · Volrix (b) (7) | 35 | +₹54,102.00 | with-trend / continuation |
| B | R8-GAP-FADE | 26 | +₹45,506.50 | gap-fade — 26/26 counter-aligned by construction; median premium ₹301.23 |
| C | R8-EXP-SLEEVE | 13 | +₹3,441.75 | weekly-expiry sleeve; median premium ₹36.05 |

No family fell under the < 8-leg ungated rule, and the split is
non-degenerate (largest family 47.3% of legs). No leg ever competes with
a leg of another family in this run.

## Results (Steps 3 + 4)

| | Full book | F70 (keep 52) | F60 (keep 45) | F50 (keep 38) |
|---|---|---|---|---|
| Total | +₹103,050.25 | +₹56,150.25 | +₹58,844.00 | +₹51,917.75 |
| Win rate | 51.4% | 50.0% | 55.6% | **60.5%** |
| ₹/trade-day | ₹1,561.37 | ₹1,220.66 | ₹1,435.22 | ₹1,483.36 |
| Trade-days | 66 | 46 | 41 | 35 |
| Green / red / no-trade days | 37 / 29 / 139 | 25 / 21 / 159 | 24 / 17 / 164 | 22 / 13 / 170 |
| Halves H1 / H2 | — | +₹23,528.75 / +₹32,621.50 | +₹19,313.75 / +₹39,530.25 | +₹12,320.25 / +₹39,597.50 |
| Ex-top-3 | — | +₹22,685.25 | +₹25,379.00 | +₹21,442.75 |
| **Placebo percentile (within-family random)** | — | **0.185** | **0.395** | **0.435** |
| Red months | Mar | Mar, **Jun new** | **Jun new** (Mar repaired to +₹4,425) | Mar, **Jun new** |
| **Verdict** | — | **FAIL** | **FAIL** | **FAIL** |

Failing legs of the pre-registered bar, named:
- **F70:** WR 50.0% < 60% · total +₹56,150.25 < ₹61,830.15 · placebo
  0.185 < 0.95 · new red month (Jun −₹2,461.50; Mar deepens to −₹2,515).
- **F60:** WR 55.6% < 60% · total +₹58,844.00 < ₹61,830.15 (short by
  ₹2,986.15) · placebo 0.395 · new red month (Jun −₹2,461.50).
- **F50:** total +₹51,917.75 < ₹61,830.15 · placebo 0.435 · new red
  months (Jun −₹2,461.50 alongside Mar). WR (60.5%), ₹/trade-day, halves
  and ex-top-3 all pass at this level — the only level in phase 2 or 2B
  to clear the WR bar — but the bar is all-legs, and it fails.

Month tables (₹): F70 — Jan +14,153.50 · Feb +4,582.00 · Mar −2,515.00 ·
Apr +420.00 · May +6,888.25 · Jun −2,461.50 · Jul +10,683.00 · Aug
+1,911.75 · Sep +6,007.75 · Oct +16,480.50. F60 — Jan +2,998.50 · Feb
+4,582.00 · Mar +4,425.00 · Apr +420.00 · May +6,888.25 · Jun −2,461.50 ·
Jul +15,890.75 · Aug +3,612.75 · Sep +6,007.75 · Oct +16,480.50. F50 —
Jan +3,680.00 · Feb +4,582.00 · Mar −3,260.00 · Apr +210.00 · May
+7,108.25 · Jun −2,461.50 · Jul +15,890.75 · Aug +3,680.00 · Sep
+6,007.75 · Oct +16,480.50.

## Why it still failed — the separation worked, the shape isn't there

Per-family kept vs idled (average net per leg), the direct test of
whether the score separates anything *inside* a family:

| Family | F70 kept / idled | F60 kept / idled | F50 kept / idled | Score↔net corr |
|---|---|---|---|---|
| A (35) | ₹1,705 / ₹1,147 | ₹1,745 / ₹1,247 | ₹1,647 / ₹1,439 | **+0.008** — no shape |
| B (26) | ₹501 / **₹4,561** | ₹952 / **₹3,028** | ₹1,172 / **₹2,329** | **−0.354** — inverted |
| C (13) | ₹500 / −₹265 | ₹871 / −₹706 | ₹1,005 / −₹599 | +0.068 — noise on 13 legs |

- **Family B is the book's second station and its anti-station.** At F70
  the 8 fade legs the score idles made +₹36,489.25 — four times the
  +₹9,017.25 of the 18 it keeps. Within the family, F_prem's percentile
  still ranks the family's richest premiums lowest, and the richest
  premiums are the biggest gap-down mornings — exactly where the fade's
  +90/+175 fixed-point geometry pays most. Normalising inside the family
  removed the cross-family penalty; it cannot remove this, because the
  inversion is *inside* the family's own distribution.
- **Families A and C** separate in the right direction (kept averages
  above idled at every level) but far too weakly to beat their own
  random-thinning placebo once combined with B, and A's correlation is
  zero to two decimal places.
- Pooled score-to-outcome correlation: **−0.084** — no better than phase
  2's global −0.06. Two dials, three stations, same silence.

## Distinctness (Step 5)

Mechanically different from the failed global construction: identical raw
factors, but each is converted to a within-family midrank percentile
before averaging, and the keep grid binds per family — family traits
(counter-gap construction, family premium level) can no longer act as
leg-level penalties. Overlap with N-FIX-1's 66 kept legs: F70 keeps 45 of
them and 7 of the 8 legs N-FIX-1 stands down (idling 21 N-FIX-1 keeps);
F60 keeps 39 + 6 of 8 (idles 27); F50 keeps 33 + 5 of 8 (idles 33). The
constructions disagree substantially in both directions; nothing here is
a relabel of N-FIX-1, and no exit, admission, assembly or single-cell
rule was touched or reused.

## November counterfactual (Step 6 — descriptive only)

v1's one November leg — **Nov 3, CE 23600, family C, in 09:50 @ ₹75.90,
out 13:20 @ ₹126.00, +₹3,036.50** — scores **0.6731** within family C
(percentiles: time 0.5385 · gap 0.6538 · premium 1.0000 — the leg's raw
premium factor is the highest in the sleeve's own distribution · expiry
0.5000), above family C's cutoff at every level (0.4327 / 0.5289 /
0.5289): **KEPT at F70, F60 and F50.** As in phase 2, the idling would
not have cost November's only Nifty win — and as in phase 2, one leg sets
no rule and rescues nothing: the score fails on the 74-leg year.

## Bottom line

Separating the stations was the right repair to *try* — it fixed the
specific cross-family penalty phase 2 diagnosed, and the numbers moved
the right way (placebos up, one level's WR over the bar, March repaired
at F60). It did not fix the tuning: at every level the family-wise book
still loses to randomly idling the same number of legs inside the same
families (placebo 0.185–0.435 against a 0.95 bar), still misses the total
bar, and still opens a new red month. The reason is now sharper than
phase 2 left it: **the fade family's edge is concentrated in its own
least typical legs, and the trend family's outcomes carry no
entry-confidence signal at all (correlation +0.008).** The edge is not
confidence-shaped — on this book, at entry time, there is no dial of this
kind to tune. TUNED v1 stands exactly as it stands; nothing is adopted
from this phase.
