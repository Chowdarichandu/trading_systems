# PHASE-2B TUNING — NIFTY · FAMILY-WISE CONFIDENCE (SELECTIVITY) · SPEC FROZEN BEFORE SCORING

**Frozen:** 2026-11-14 09:02 IST — before any phase-2B subset was scored.
Nothing in this spec may be edited after the run; deviations are reported,
not absorbed.

**Order:** owner's radio principle, 2026-11-14 09:00 IST — "if something
is failing, you need to work on the thing and why it is failing and you
need to tune." Phase 2's global confidence score FAILED on this book; this
run tunes from that diagnosis. Research only: no book, ledger or job is
changed. Buying only, 1 lot (65), premiums basis, cost ₹220/trade already
inside every stored net.

## The diagnosis this run tunes from (phase 2, 2026-11-14)

Phase 2 ranked all 74 TUNED v1 legs by one composite confidence score and
kept the top 70/60/50%. It failed at every threshold (placebo percentiles
0.24 / 0.385 / 0.32 against a 0.95 bar; score-to-outcome correlation
−0.06). The failure report identified the mechanism: **the book mixes
families with opposite confidence geometry.** The gap-fade family earns by
trading AGAINST the overnight gap at expensive premiums — both facts the
global score marked as "unconfident" (counter-gap = 0.20; premium far from
the book median = penalised) — so the score systematically idled the
book's earners. One dial was used for two stations. The data confirms the
split before any tuning: all 26 family-B legs are counter-aligned by
construction (26/26) and their median premium (₹301.23) sits far above the
book median (₹213.03); family C's median premium (₹36.05) sits far below
it. A global score can only read these family traits as defects.

**This run's one change: confidence is measured WITHIN each family, never
across families.** A gap-fade leg is ranked against gap-fade legs only;
"against the gap" is that family's normal and differentiates nothing
inside it.

## Subject book and leg store

Identical to phase 2: **Nifty TUNED v1 (EVE-07) = DEC-S1 − B PE**, store
`november_books_fix_repair_nifty_legs.csv` (74 rows, no B-PE rows).
Columns include `family` (A/B/C) and `rep`.

## Step 0 — Control (gate to everything else)

Reproduce from the store, exactly as phase 2 did: **74 legs · total
+₹103,050.25 · WR 51.4% (38 wins) · 66 trade-days · ₹1,561.37/trade-day ·
March 2026 −₹1,216.50 (the only red month)**; N-FIX-1 anchors (8
stood-down legs, −₹14,119.75; repaired total +₹117,170.00); median premium
₹213.025. If any figure does not reproduce, STOP and report — no scoring.

## Step 1 — Family split (pre-registered)

Partition the 74 legs by the store's `family` column:

| Family | Producing rep(s) | Legs | Character |
|---|---|---|---|
| A | (lA) v2 (19) · V5 v2 (9) · Volrix (b) (7) | 35 | with-trend / continuation |
| B | R8-GAP-FADE (26) | 26 | gap-fade — counter-gap by construction |
| C | R8-EXP-SLEEVE (13) | 13 | weekly-expiry sleeve |

Any family with **< 8 legs is left UNGATED** (always kept, named in the
report) — a percentile inside a handful of legs is noise. As frozen, all
three families have ≥ 8 legs (35 / 26 / 13), so **all three are gated and
no family is left ungated**; this is recorded here so the rule, not the
outcome, decided it. The split is non-degenerate (largest family = 47.3%
of legs); if it had been degenerate the run would say so and score anyway
— it does not arise.

## Step 2 — Within-family confidence score (pre-registered)

Raw factor values are computed with the **phase-2 formulas unchanged**:
F_time (bucket: pre-11:00 = 1.00 · 11:00–12:30 = 0.60 · post-12:30 =
0.30), F_gap (aligned = 1.00 · |gap| < 0.10% = 0.50 · counter-aligned =
0.20), F_prem (1 − 0.7·min(1, |ln(premium/213.025)|/ln 4), frozen book
median), F_exp (0.70 if Tuesday and family ≠ C, else 1.00). The two
phase-2-dropped factors stay dropped for the same reasons (no agreement
field in the store; v1 has no second-leg structure) — not approximated.

The change is solely the ranking universe. For each leg, each factor value
is converted to its **percentile within the leg's own family** by the
midrank formula over that family's legs:

pct_f(x) = ( #{legs in f with factor < x} + 0.5 · #{legs in f with factor = x} ) / n_f

**Within-family score = equal-weight mean of the four within-family
percentiles** (in (0, 1]). Consequences, stated in advance: a factor that
is constant inside a family (e.g. F_gap inside family B, all counter) sits
at percentile 0.5 for every leg of that family — it differentiates
nothing and penalises nothing; F_prem's percentile re-centres each family
on its own premium distribution, so a fade leg's ₹300 premium is judged
against fade premiums, not against the book.

Ranking inside each family: score descending; ties broken by (date asc,
entry_time asc) — deterministic, as phase 2.

## Step 3 — Keep grid (pre-registered)

Within EACH gated family, keep the top 70% / 60% / 50% by within-family
score; the three combined books are the union over families. Kept counts
use round-half-up per family, k_f = floor(frac · n_f + 0.5):

| Level | A (35) | B (26) | C (13) | Combined kept |
|---|---|---|---|---|
| F70 | 25 | 18 | 9 | 52 |
| F60 | 21 | 16 | 8 | 45 |
| F50 | 18 | 13 | 7 | 38 |

(The combined totals need not equal phase 2's global k; the grid is
defined per family.) Each family's cutoff score (the k_f-th leg's
within-family score) is recorded per level.

Per combined book, report: total, legs, distinct trade-days, WR (legs),
₹/trade-day, green/red/no-trade days over the 205-day Jan–Oct 2026
calendar (calendar = `volrix/nifty_daily_2019_2026.csv`), full month
table (Jan–Oct nets), halves (H1 = Jan–May legs, H2 = Jun–Oct legs),
ex-top-3. Also report, per level and per family, kept vs idled net — the
direct test of whether the score separates anything inside a family.

## Step 4 — Placebo (pre-registered; within-family random)

Per level: 200 draws; each draw thins **every family by the same
proportion** — sample k_f legs uniformly without replacement from family
f, independently per family (family order A, B, C), combine, total. RNG:
Python `random.Random(20261114)`, draws in level order F70, F60, F50.
Placebo percentile = fraction of the 200 whose total is strictly below
the tuned book's total.

A global random placebo is NOT the right control here: it would let the
draw change the family mix itself, so it would test family allocation —
which this tuning deliberately does not touch — instead of testing
whether within-family ranking carries information. The null for "ranking
inside a family is informative" is "random ranking inside the same
family, same kept counts."

## Step 5 — Distinctness (pre-registered)

- Mechanical difference from the failed phase-2 construction: phase 2
  ranked raw factor composites across all 74 legs, so family traits
  (counter-gap construction, family premium level) acted as leg-level
  penalties. Here raw factors are computed identically but converted to
  within-family percentiles before averaging, and the keep grid is applied
  per family — no leg ever competes with a leg of another family.
- N-FIX-1 (the repaired lead already running) keeps 66 legs, idles 8
  CE-on-gap-up legs. Per level report: |kept ∩ N-FIX-1 kept|,
  |kept \ N-FIX-1 kept|, and how many of N-FIX-1's 8 idled legs the level
  keeps. Not a relabel of any closed route: no exit, admission, assembly
  or single-cell rule is touched or reused as a factor.

## Step 6 — November counterfactual (descriptive only)

v1's actual November = 1 leg: **Nov 3, CE 23600, family C (weekly
sleeve), entry 09:50 @ ₹75.90, square-off 13:20 @ ₹126.00, +₹3,036.50**,
overnight gap +0.6034%. Raw factors as phase 2 (F_time 1.00 · F_gap 1.00
aligned · F_prem from r = 75.90/213.025 · F_exp 1.00, family C is
expiry-native). Each factor is percentiled against family C's 13 stored
legs with the same midrank formula (reference set = the stored legs,
denominator 13); the mean is the leg's within-family score. Per level:
KEPT if that score ≥ family C's cutoff at that level, else IDLED. One leg
sets no rule in either direction.

## Diagnostics (reported, not gated)

Pooled correlation between the within-family score and leg net (phase 2's
global score posted −0.06); per-family correlations. These describe
whether "confidence" has any shape inside families at all.

## PASS BAR (per level, pre-registered, identical to phase 2 — do not move)

ALL of: WR ≥ 60% · ₹/trade-day ≥ ₹900 · total ≥ ₹61,830.15 (60% of the
full book's +₹103,050.25) · H1 > 0 AND H2 > 0 · ex-top-3 > 0 · placebo
percentile ≥ 0.95 · no new red month (the book's red months ⊆ {2026-03},
the baseline's only red month). Any leg failed = FAIL for that level,
with the failing leg(s) named.

## Deliverables

`phase2b_tuning_nifty_2026-11-14.md` + `phase2b_tuning_nifty_results.json`,
produced by `phase2b_tuning_nifty_2026-11-14.py`. The verdict must state
honestly whether separating the stations fixed the tuning, or whether the
book's edge is simply not confidence-shaped.
