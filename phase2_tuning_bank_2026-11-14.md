# PHASE-2 TUNING — BANK NIFTY · CONFIDENCE GATING ON TUNED STACK v2 · 2026-11-14

Spec: `phase2_tuning_bank_SPEC.md` (frozen before scoring). Numbers: `phase2_tuning_bank_results.json`.
Script: `phase2_tuning_bank_build.py`. Research only — no book, ledger, or job changed.
Basis: paper, 1 lot, costs as in the gated store. Owner's principle: idle beats a marginal trade.

## Control (reproduced before any scoring)
Full book Jan–Oct from the gated store (solid60 features ⨝ books-fix anatomy, join 111/111):
**111 legs · +₹127,351.50 · WR 59.5% · 89 trade-days · ₹1,430.92/trade-day · 60G/29R/116NT of 205 ·
H1 +₹83,082.00 / H2 +₹44,269.50 · ex-top-3 +₹100,528.50 · zero red months** — exact match,
plus an independent raw-column re-sum (+₹127,351.50). Control OK.

## Method in one paragraph
Every leg got a composite confidence score from six entry-bar-knowable factors with weights
frozen in the spec (agreeing sources; entry premium vs the book median ₹692.50; entry-time
bucket; overnight gap aligned with side; second-leg flag; anchor/base outcome for second legs —
resolved for 16 of 28 second legs, the rest scored neutral). Room ratio and VIX were audited
and DROPPED: neither is carried per-leg in the gated stack store (recorded in the spec).
Weights were fixed before scoring but informed by prior gated findings on this same window —
Jan–Oct is the tuning window, so a PASS below is a tuning result, not forward proof.

## Results per threshold
Note on the grid: scores move in 0.25 steps and the pre-registered tie rule keeps every leg
sitting on the cut score. The 70% and 60% cuts land on the same score (0.5), so T70 and T60
are the SAME kept set — the grid effectively tested two selectivity levels, not three.

| Cut | Kept | Total | WR | ₹/trade-day | Trade-days | G/R/NT | Halves | Ex-top-3 | Placebo | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| Full book | 111 | +₹127,351.50 | 59.5% | ₹1,430.92 | 89 | 60/29/116 | +83,082 / +44,270 | +₹100,528.50 | — | baseline |
| T70 (= T60), score ≥ 0.5 | 88 | +₹122,337.50 | **62.5%** | **₹1,609.70** | 76 | 53/23/129 | +75,047 / +47,291 | +₹95,514.50 | **97th pct** (p95 ₹118,112) | **PASS** |
| T50, score ≥ 1.0 | 63 | +₹82,911.00 | 60.3% | ₹1,507.47 | 55 | 36/19/150 | +57,507 / +25,404 | +₹56,088.00 | 79th pct (p95 ₹95,487) | **FAIL — placebo leg** |

- **T70/T60 PASS — all seven pre-registered legs.** It keeps 96.1% of the book's money on
  79.3% of its legs, lifts WR from 59.5% to 62.5% (over the owner's 60% line) and ₹/trade-day
  from ₹1,430.92 to ₹1,609.70, with no red month (weakest kept month: Jun +₹1,520, Aug +₹2,059.50)
  and both halves positive — H2 actually improves (+₹47,290.50 vs +₹44,269.50). The 23 dropped
  legs netted +₹5,014 in aggregate: the gate gives up a little total to buy a cleaner book,
  and the placebo (97th percentile vs 200 same-size random subsets) says this specific
  selection preserves money far better than random thinning — the score carries real signal
  at this cut. Month table (kept set): Jan +21,513 · Feb +15,284 · Mar +8,760 · Apr +9,050 ·
  May +20,440 · Jun +1,520 · Jul +9,525 · Aug +2,059.50 · Sep +16,776.50 · Oct +17,409.50.
- **T50 FAIL — placebo leg named.** Every other bar passes (WR 60.3%, ₹1,507.47/trade-day,
  total 65.1% of book, halves and ex-top-3 positive, no red month), but the kept ₹82,911 sits
  at only the 79th percentile of random 63-leg subsets (random p95 = ₹95,487): at the deep cut
  the score drops big winners faster than chance does. Deeper confidence-gating destroys value.

## Distinctness vs B-FIX-1
B-FIX-1 (already running as the repaired lead) keeps 94 legs. The T70/T60 kept set shares 71
of its 88 legs with B-FIX-1's kept set (80.7% of the kept set; Jaccard 64.0%) — overlapping
but not a relabel: B-FIX-1 is a single hard skip rule (PE + down-gap + ₹500–800 premium);
this is a six-factor rank that also drops legs B-FIX-1 keeps and keeps 17 legs B-FIX-1 drops.
It is not any closed route: no exit change, no single admission class, premium enters only
as a ratio-to-median term, gap only as a ±0.5 alignment term — never as a skip rule.

## November counterfactual (descriptive only — November sets no rule)
*agree* is not carried in the November shadow log, so F1 is neutral (0) for November legs.
- **Cut ≥ 0.5 (T70/T60):** keeps Nov 4 (+₹2,480) and Nov 13 (−₹1,720); stays idle on Nov 9 and
  Nov 12 (two −₹1,720 stops skipped) → **November would have been +₹760 instead of −₹2,680.**
- **Cut ≥ 1.0 (T50):** keeps nothing → **₹0, fully idle** — also better than −₹2,680, and the
  purest expression of the owner's principle, but its Jan–Oct placebo failure stands.

## Honest bottom line
Confidence-gating earns something real but modest, and only as a LIGHT filter: at the mild
cut it beats random thinning (97th percentile), raises WR past 60% and lifts ₹/trade-day
~12.5% while keeping 96% of the money — it does not create money (kept total is ₹5,014 below
the full book), and at the deep cut the same score is worse than chance at preserving money.
Any adoption is the owner's call at the Nov 30 verdicts, judged on forward evidence — this
run changes nothing that is running.
