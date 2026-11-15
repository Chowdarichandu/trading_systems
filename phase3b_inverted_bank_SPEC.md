# PHASE-3B TUNING — BANK NIFTY · INVERTED CONDITIONING (QUIET-VOLUME + SPECULATION-FADE) · SPEC (FROZEN BEFORE SCORING)

Frozen: 2026-11-14 09:09 IST, before any phase-3B scoring was run.
Owner's standing orders (2026-11-14): tuning does NOT stop until the result
is got; every failure rolls into the next tune from its diagnosis; tuning =
adjusting parameters in small turns on the data on hand.
Research only — no book, ledger, or job is changed by this run. Buying
only, 1 lot, Bank only.

## The diagnosis this run tests (from phase 3, phase3_buildup_bank_2026-11-14.md)
Phase 3 froze confirmation-style conditioning and all 22 grid points
FAILED. Two of its dials measured INVERTED on the full Jan–Oct year:
1. VOLUME — gating on relative volume ≥ threshold amputated earners
   (dropped sets worth +₹28k…+₹88k at every volume point; the book earns
   on its QUIET mornings). Futures/volume state was complete 205/205 days.
2. SPECULATION — where testable (116/205 days; 44 post-read legs at 10:00,
   27 at 11:00), the flipped books beat the kept books at both reads
   (+₹122,845.50 vs +₹94,295.00 @10:00; +₹134,630.50 vs +₹109,802.00
   @11:00): legs the call/put lean AGREED with did worse; the profitable
   side was the lean opposing or flat.
Phase 3 stated, and did not act on: "flipping a failed conditioner into
its opposite after seeing the result is a new hypothesis, not a finding."
THIS RUN is that new hypothesis, frozen here before scoring. Alignment is
NOT retested — it measured a coin flip both ways (kept sets at the
39th–47.5th placebo percentile; dropped legs' average ≥ kept average).

## Book under test (control)
TUNED STACK v2, Jan–Oct 2026, loaded exactly as phases 2/3:
features store solid60_programme_2026-11-13_bank_A_stack_features.csv
joined to november_books_fix_anatomy_legs.csv (book=BANK_STACK) on
(date, entry_time, entry_premium), 111/111.
Control to reproduce BEFORE scoring: 111 legs · +₹127,351.50 · WR 59.5% ·
89 trade-days · ₹1,430.92/trade-day · 60G/29R/116NT of 205 · H1 +₹83,082.00 /
H2 +₹44,269.50 · ex-top-3 +₹100,528.50 · zero red months · independent raw
re-sum +₹127,351.50. If the control fails, stop and report.

## Morning state (identical to phase 3 — same code, same definitions)
Reads R = 10:00 and R = 11:00. State at R uses only 5-min bars starting
before R; base bar 09:15. A leg is conditioned by read R iff
entry_time >= R; pre-read legs are always kept.
- RELATIVE VOLUME (futures, in-force near-month FUT7): cumulative volume
  09:15..R−5 today ÷ same window previous trading day (ratio_prev), and ÷
  mean of same window over previous 5 trading days (ratio_5d).
- CALL/PUT SPECULATION (options): band = 11 strikes nearest the day's
  opening spot (close of spot 09:15 bar); ΔOI per type summed over the band
  from 09:15 to the last state bar; index = (ΔOI_CE − ΔOI_PE) /
  (|ΔOI_CE| + |ΔOI_PE|), 0 denominator → FLAT; lean LONG if index > +0.15,
  SHORT if < −0.15, else FLAT.
- NC RULES (phase 3's, unchanged): a missing band contract / futures bar /
  volume window makes that component NC for the day-read. A grid point
  whose needed component(s) are NC for a leg's day-read leaves the leg
  KEPT unconditionally, counted NC-kept (idle only on positive evidence).
  For combination points, if ANY needed component is NC the leg is
  NC-kept (the phase-3 all-or-nothing convention).

## State validation (run before the grid; if any check fails, stop and report)
The state code must reproduce phase 3 exactly on its own points:
- Coverage: futures complete 205/205 Jan–Oct days at both reads;
  speculation complete 116/205; post-read legs 76 @10:00 / 42 @11:00;
  post-read spec-ok legs 44 @10:00 / 27 @11:00.
- Points @10:00 — A: kept 93, dropped 18 (+₹24,603.00), kept total
  +₹102,748.50 · B: kept 82, dropped 29 (+₹33,056.50), kept +₹94,295.00 ·
  C1.0: kept 55, dropped 56 (+₹53,717.50), kept +₹73,634.00 · C5-1.0:
  kept 54, dropped 57 (+₹75,847.50), kept +₹51,504.00.
- Points @11:00 — A: kept 100, dropped 11 (+₹13,469.50), kept +₹113,882.00 ·
  B: kept 94, dropped 17 (+₹17,549.50), kept +₹109,802.00 · C1.0: kept 76,
  dropped 35 (+₹29,051.50), kept +₹98,300.00 · C5-1.0: kept 77, dropped 34
  (+₹27,771.50), kept +₹99,580.00.
Reference-set validation (for the overlap section): phase-2 confidence
score recomputed with phase 2's own code → kept set at cut ≥ 0.5 = 88 legs,
total +₹122,337.50, WR 62.5%; B-FIX-1 rule kept set = 94 legs, repaired
total +₹131,510.00; their intersection = 71 (80.7% of the phase-2 kept set,
Jaccard 64.0%).

## Tuning grid (small turns — all frozen here; per read R ∈ {10:00, 11:00})
Kept set = pre-read legs + NC-kept legs + post-read legs passing the rule.
(i) QUIET-VOL — keep a post-read leg iff its relative volume is LOW:
  QVP-1.0 / QVP-0.9 / QVP-0.8   ratio_prev ≤ t
  QV5-1.0 / QV5-0.9 / QV5-0.8   ratio_5d  ≤ t
  (6 points per read, 12 total. Boundary: ratio exactly == t is KEPT.)
(ii) SPEC-FADE — keep a post-read leg iff the call/put lean does NOT agree
  with the leg's side: agreement = (lean LONG and side CE) or (lean SHORT
  and side PE) → DROP; lean opposing the side, or lean FLAT → KEEP.
  NC speculation days: leg KEPT (pre-registered: a conditioner that cannot
  judge does not idle); the NC share of the kept set is reported.
  SF (1 point per read, 2 total)
(iii) QUIET+FADE — both conditions together:
  QFP-0.9 = QVP-0.9 AND SF · QF5-0.9 = QV5-0.9 AND SF
  (2 points per read, 4 total)
18 grid points total. No other combinations will be scored.

## Scoring per grid point
Kept legs, dropped legs + dropped total, NC-kept count, total, WR,
trade-days, ₹/trade-day, green/red/no-trade days (205-day universe), full
month table (months fully idled are listed), halves (Jan–May / Jun–Oct),
ex-top-3.

## Placebos + dropped-set controls (per grid point, pre-registered)
- 200 random subsets of the SAME kept size from all 111 legs (seed 42);
  kept total must exceed the draws' 95th percentile.
- Flipped book (phase-3 definition): all legs EXCEPT the post-read legs
  the conditioner kept. Kept total must exceed the flipped total.
- Dropped-set control: kept total must exceed the dropped legs' standalone
  total (the conditioner must beat the legs it drops).
- Mirror control for QUIET-VOL: phase 3's high-volume kept sets are
  already measured (same state, opposite inequality) — they are CITED in
  the report, not re-run. Note the partition identity: on vol-ok post-read
  legs, QUIET-VOL's kept set and phase 3's C/C5 dropped set differ only by
  legs sitting exactly on the threshold ratio.

## Pass bar (pre-registered, NOT to be moved — identical to phases 2/3)
A grid point PASSES only if ALL hold: WR ≥ 60% · ₹/trade-day ≥ ₹900 ·
total ≥ 60% of +₹127,351.50 (≥ ₹76,410.90) · both halves positive ·
ex-top-3 positive · placebo percentile ≥ 95 (kept > p95 of draws) ·
kept total > flipped total · kept total > dropped total · no red month.
Any failing leg is named per grid point.

## Distinctness / overlap (pre-registered)
- vs phase 3: same state surface, OPPOSITE inequality on volume and
  opposite polarity on speculation; alignment untouched. This is the
  frozen test of phase 3's post-hoc observation — if it passes, it passes
  as a new hypothesis that was frozen before its own scoring, and it
  still earns nothing until forward evidence exists.
- Overlap: for every QUIET+FADE point (and, for context, every point),
  report the kept set's intersection with (a) the phase-2 confidence
  gate's kept set (≥ 0.5, 88 legs) and (b) the B-FIX-1 kept set (94 legs):
  intersection count, share of this point's kept set, Jaccard. If a
  QUIET+FADE kept set is nearly the confidence gate's, that is stated
  plainly — a second name for the same selection is not a new channel.
- vs closed routes (IOI/FLOW-VOL/day-OI/phase-2): this run still
  generates no entries and changes no exits; it only keeps/idles the
  stack's own legs on morning positioning state.

## November counterfactual (descriptive only)
Apply every grid point to the stack's 4 actual November legs
(Nov 4 S3-R1 PE 09:55 +₹2,480 · Nov 9 Skill V3 PE 10:45 −₹1,720 ·
Nov 12 S3-R1 PE 11:30 −₹1,720 · Nov 13 NS3 PE 12:20 −₹1,720; total
−₹2,680), state from November data (expiry 2026-11-23). The speculation
state is NC on all 4 November leg days (to be re-verified from state):
SPEC-FADE therefore cannot fire in November — its CF equals the volume
component alone for QF points and the actual −₹2,680 for SF points; this
is stated, not scored around. Nov 4 (09:55) is pre-read for both reads →
always kept. November sets no rule; description only.

## Deliverables
phase3b_inverted_bank_2026-11-14.md + phase3b_inverted_bank_results.json.
Script: phase3b_inverted_bank_build.py.
