# PHASE-2 TUNING — BANK NIFTY · SELECTIVITY / CONFIDENCE GATING · SPEC (FROZEN BEFORE SCORING)

Frozen: 2026-11-14 (IST), before any phase-2 scoring was run.
Owner's order: 2026-11-14 08:54 — next tuning phase for Bank + Nifty starts now.
Owner's principle: if the system is not confident about a trade, it keeps its hands
idle — idle is better than a marginal trade. This phase tunes SELECTIVITY only:
no exit changes, no new signals, no admission-class filters. Research only —
no book, ledger, or job is changed by this run.

## Book under test
TUNED STACK v2, Jan–Oct 2026 gated leg store:
- Features store: solid60_programme_2026-11-13_bank_A_stack_features.csv (111 legs)
- Anatomy store: november_books_fix_anatomy_legs.csv, book=BANK_STACK (111 legs)
- Join key: (date, entry_time, entry_premium) — verified 111/111 matches,
  net sum ₹127,351.50 before freezing this spec.
- Baseline to reproduce (control): 111 legs · +₹127,351.50 · WR 59.5% ·
  89 trade-days · ₹1,430.92/trade-day · 60 green / 29 red / 116 no-trade of 205
  days · halves H1 (Jan–May) +₹83,082.00 / H2 (Jun–Oct) +₹44,269.50 ·
  ex-top-3 +₹100,528.50 · zero red months. If the control does not reproduce
  exactly, the run stops and reports instead of scoring.

## Composite confidence score (entry-bar knowable factors only)
Each factor is audited: (a) present in the gated store, (b) knowable at the
entry bar. Points are FIXED HERE, before scoring (weights are judgment-fixed,
informed by prior gated findings on this same window — Jan–Oct is the tuning
window, so any PASS is a tuning result, not forward proof).

- F1 Agreeing sources (`agree` in features store): ≥2 → +1.0 · =1 → +0.5 · =0 → 0.
  Knowable at entry: YES (the key's source agreement is what admits the leg).
- F2 Entry premium vs book median (book median premium = ₹692.50, a fixed
  constant of the gated store): ratio r = premium/692.50: r<0.75 → +1.0 ·
  0.75≤r<1.0 → +0.5 · 1.0≤r<1.45 → 0 · r≥1.45 → −0.5.
  Knowable at entry: YES (premium is the entry fill; median is a book constant).
- F3 Entry-time bucket (`tod`): early → +0.5 · mid → 0 · late → −0.5
  (mechanical rationale: later entries have less room before the 15:20
  square-off; not fitted). Knowable at entry: YES.
- F4 Overnight gap aligned with side (anatomy `gap_pct`): CE with gap>0 or PE
  with gap<0 = aligned. Aligned & |gap|≥0.30% → +0.5 · aligned & 0.05%≤|gap|<0.30%
  → +0.25 · |gap|<0.05% → 0 · against side → −0.5.
  Knowable at entry: YES (overnight gap is known at the open).
- F5 Second-leg flag (`second`): =1 → +0.5 · =0 → 0.
  Knowable at entry: YES (a second leg knows it is one).
- F6 Anchor/base outcome (second legs only): the leg this leg follows had a
  positive net → +0.5 · negative → −0.5 · not a second leg or unresolvable → 0.
  Resolution rule: EVE06_REENTRY — the earlier same-day stack leg in this store;
  NS1_second — the same-date v21-frame BASE leg (bank_engine_r6_v21_trades.csv)
  with the latest exit_time ≤ this leg's entry_time. Resolution count is logged.
  Knowable at entry: YES when resolvable (the anchor has already exited).

### Factors audited and DROPPED (recorded, not silently omitted)
- Room ratio: NOT carried per-leg in the gated stack store (exists only in
  per-signal s1–s5 logs, which do not cover NS1/NS3/EVE06/S3 legs uniformly).
  A partial join would bias the score. DROPPED.
- India VIX at entry: the gated stack store carries no per-leg VIX field.
  DROPPED (per spec allowance: "where the store carries it" — it does not).

## Threshold grid (pre-registered)
Rank all 111 legs by composite score, descending. Keep:
- T70: top 70% (≈78 legs) · T60: top 60% (≈67 legs) · T50: top 50% (≈56 legs).
Ties at a cut: all legs sitting on the cut score are kept; actual kept counts
are reported. Thresholds are also recorded as score cut values so the same
cuts can be applied to November legs.

## Scoring per kept subset
Total, legs, trade-days, WR, ₹/trade-day, green/red/no-trade days (day universe
= 205 Jan–Oct trading days), full month table, halves (Jan–May / Jun–Oct),
ex-top-3 (3 largest legs of the subset removed), red-month list.

## Placebo (pre-registered)
200 random subsets of the SAME kept size drawn from the 111 legs (seed 42).
Statistic = subset total. PASS requires the kept subset's total to exceed the
95th percentile of the placebo draws (beats ≥95% of them). A kept subset that
merely matches random thinning is not confidence — it is just fewer trades.

## Pass bar (pre-registered, NOT to be moved)
A threshold PASSES only if ALL hold: WR ≥ 60% · ₹/trade-day ≥ ₹900 ·
total ≥ 60% of +₹127,351.50 (≥ ₹76,410.90) · both halves positive ·
ex-top-3 positive · placebo condition met · no red month (baseline has none).
Any leg failing = FAIL for that threshold, with the failing leg named.

## Distinctness (pre-registered statement)
This is a multi-factor composite rank, not a single-factor filter. It is not:
single signal-class/admission filters (closed), PB premium bands standalone
(closed — premium enters only as one of six factors, as a ratio to the book
median, not as a hard band), the gap-guard (closed — gap enters only as a
±0.5 alignment term, never as a skip rule), the T-B exit set, FE fast exits,
or ladder exits (all exit-side; this phase changes no exit). Overlap of each
kept set with B-FIX-1's kept set (B-FIX-1 drops PE legs with gap<0 and entry
premium ₹500–800; 17 legs dropped, 94 kept) is computed and stated explicitly.

## November counterfactual (descriptive only)
Apply each threshold's score cut to the stack's 4 actual November legs
(Nov 4 S3-R1 PE +₹2,480 · Nov 9 BASE Skill V3 PE −₹1,720 · Nov 12 S3-R1 PE
−₹1,720 · Nov 13 NS3-GD PE −₹1,720; month −₹2,680). November factor values:
premium, entry time, family/second flag from november_shadow_stack_bank_log.csv;
gap_pct from november_regime_days_bank.csv. `agree` is not carried in the
November shadow log — F1 is set to its neutral 0 for November legs and this
limitation is stated wherever the November numbers appear. November sets no
rule; it is reported as description only.

## Deliverables
phase2_tuning_bank_2026-11-14.md + phase2_tuning_bank_results.json.
