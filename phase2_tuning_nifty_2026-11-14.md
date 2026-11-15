# PHASE-2 TUNING — NIFTY · SELECTIVITY (CONFIDENCE-GATING) ON TUNED v1

**Run:** 2026-11-14, under the owner's direct order of 08:54 IST ("the next
phase of tuning to be started now for both entities"). Spec frozen before
scoring: `phase2_tuning_nifty_SPEC.md` (08:56 IST). Script:
`phase2_tuning_nifty_2026-11-14.py` → `phase2_tuning_nifty_results.json`.
**Research only — no book, ledger or job changed.** Paper basis throughout:
Nifty premiums per 1 lot (65), cost ₹220/trade inside every stored net,
buying only.

**The idea tested (owner's principle):** if the system is not confident
about a trade, keep hands idle. So: score every TUNED v1 leg on
entry-knowable confidence factors, keep only the top 70% / 60% / 50%, idle
the rest — and check whether the kept subset is actually better, against a
placebo of random subsets of the same size (trading less, blindly).

## VERDICT — FAIL AT ALL THREE THRESHOLDS

**The confidence score does not find better trades. It finds slightly
worse ones.** At every threshold the kept subset's win rate is at or below
the full book's 51.4%, its ₹/trade-day falls, random subsets of the same
size usually beat it, and the legs it idles include the book's biggest
winners. Correlation between the confidence score and what a leg actually
made: **−0.06 — no relationship at all.** The "unconfident" half of the
book out-earned the "confident" half (+₹1,581.82 vs +₹1,203.32 per leg).

## Control (Step 0 — reproduced exactly before any scoring)

From `november_books_fix_repair_nifty_legs.csv` (the gated store):
**74 legs · +₹103,050.25 · WR 51.4% (38 wins) · 66 trade-days ·
₹1,561.37/trade-day · March 2026 −₹1,216.50, the only red month.**
N-FIX-1 anchors also reproduced from the same store: 8 stood-down legs
−₹14,119.75, repaired total +₹117,170.00. Day profile of the full book:
37 green / 29 red / 139 no-trade of 205 calendar days.

## The score (Step 1)

Equal-weight mean of four entry-knowable factors (audit in the spec):
entry-time bucket (morning = confident), signed gap aligned with side
(with the overnight flow = confident), entry premium vs the book's frozen
median ₹213.025 (mid-band = confident), weekly-expiry-day discount for
non-sleeve legs. Two specified factors were **not** used, as pre-registered:
agreeing-source count — the store carries only one producing source per
leg, no agreement field exists; second-leg base outcome — TUNED v1 has no
second-leg structure. Neither was approximated.

## Results (Step 2 + 3)

| | Full book | T70 (keep 52) | T60 (keep 44) | T50 (keep 37) |
|---|---|---|---|---|
| Total | +₹103,050.25 | +₹61,863.75 | +₹56,594.00 | +₹44,523.00 |
| Win rate | 51.4% | **50.0%** | 52.3% | **48.6%** |
| ₹/trade-day | ₹1,561.37 | ₹1,316.25 | ₹1,347.48 | ₹1,236.75 |
| Trade-days | 66 | 47 | 42 | 36 |
| Green / red / no-trade days | 37 / 29 / 139 | 25 / 22 / 158 | 22 / 20 / 163 | 17 / 19 / 169 |
| Halves H1 / H2 | — | +₹20,794.50 / +₹41,069.25 | +₹12,173.75 / +₹44,420.25 | +₹18,554.75 / +₹25,968.25 |
| Ex-top-3 | — | +₹28,398.75 | +₹23,129.00 | +₹11,058.00 |
| **Placebo percentile** | — | **0.24** | **0.385** | **0.32** |
| Red months | Mar | Mar✓ but **Apr, Jun new** | **Apr, Jun new** | **Apr, Jun new** |
| **Verdict** | — | **FAIL** | **FAIL** | **FAIL** |

Failing legs of the pre-registered bar, named:
- **T70:** WR 50.0% < 60% · placebo 0.24 < 0.95 · new red months (Apr
  −₹3,260, Jun −₹2,681.50). (Its total clears the 60%-of-book bar by
  ₹33.60 — the only near-miss anywhere in this run.)
- **T60:** WR 52.3% < 60% · total +₹56,594 < ₹61,830.15 · placebo 0.385 ·
  new red months.
- **T50:** WR 48.6% < 60% · total +₹44,523 < ₹61,830.15 · placebo 0.32 ·
  new red months.

Month tables (kept subsets, ₹): T70 — Jan +14,153.50 · Feb +4,582.00 ·
Mar +955.00 · Apr −3,260.00 · May +4,364.00 · Jun −2,681.50 · Jul
+15,670.75 · Aug +1,911.75 · Sep +9,687.75 · Oct +16,480.50. T60 — Jan
+2,998.50 · Feb +4,582.00 · Mar +4,425.00 · Apr −3,260.00 · May +3,428.25 ·
Jun −2,461.50 · Jul +15,670.75 · Aug +1,911.75 · Sep +12,818.75 · Oct
+16,480.50. T50 — Jan +2,998.50 · Feb +7,493.00 · Mar +7,895.00 · Apr
−3,260.00 · May +3,428.25 · Jun −2,461.50 · Jul +6,311.00 · Aug +1,911.75 ·
Sep +7,406.50 · Oct +12,800.50.

## Why it failed — the idled legs were the earners

The score systematically marks this book's real earners "unconfident":
- T50 idles 37 legs worth **+₹58,527.25 — more than the +₹44,523 it
  keeps** — including **two +₹11,155 full-target wins** (Jan 20 (lA) v2;
  Apr 2 gap-fade) and five more winners ≥ +₹5,000.
- The pattern is structural, not noise: the book's gap-fade family earns
  **by trading against the overnight gap**, and big-gap days carry the
  expensive premiums. Both score as "low confidence" (counter-gap = 0.20,
  premium far from median = penalised) — so the score idles exactly the
  legs the book exists for. "Trade with the flow, at a normal price, in
  the morning" describes a comfortable trade; this book's money was made
  on the uncomfortable ones.

## Distinctness (Step 4)

Not a relabel of N-FIX-1 or any closed route. The disagreement is maximal
where it was predicted: F_gap rewards the gap alignment that N-FIX-1's
single-cell rule idles — **T70 keeps all 8 of the legs N-FIX-1 stands
down** (T60/T50 keep 7 of 8), while idling 22 / 29 / 36 legs N-FIX-1
keeps. Overlap of kept sets with N-FIX-1's 66 kept legs: 44 / 37 / 30.
No exit, admission or assembly rule was touched (T-N, EVE, C3 routes
untouched).

## November counterfactual (Step 5 — descriptive only)

v1's one November leg — **Nov 3, CE 23600 weekly sleeve, in 09:50 @
₹75.90, out 13:20 @ ₹126.00, +₹3,036.50** — scores **0.8697** (morning
entry 1.00, gap-aligned 1.00, expiry-native 1.00, cheap premium 0.4789),
above every threshold's cutoff (0.725 / 0.7666 / 0.7868): **KEPT at T70,
T60 and T50.** The idling this score prescribes would not have cost
November's only Nifty win. One leg sets no rule in either direction — and
it does not rescue the score, which fails on the 74-leg year, not on
November.

## Bottom line

Confidence-gating, built from the obvious entry-knowable factors, earns
**nothing** beyond trading less — it earns less than trading less
blindly: at every size, a random subset of the same size usually made
more money (placebo percentiles 0.24–0.385 against a 0.95 bar). On this
book, at entry time, there is no visible difference between a confident
trade and a marginal one — the score's correlation with outcomes is
−0.06. The owner's idle-hands principle is not wrong; it is this
measurement of "confidence" that carries no information. TUNED v1 stays
exactly as it stands; nothing is adopted from this phase.
