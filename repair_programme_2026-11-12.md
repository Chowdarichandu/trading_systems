# REPAIR PROGRAMME — 2026-11-12 (owner order 16:12 IST)

Gated research only. Frozen November primaries untouched; outputs are December
candidates / shadow definitions. Gate = the project standard (EVE-07…20):
candidate FAILS if total ≤ incumbent, any month flips green→red, H1 or H2 <
incumbent, ex-top-3 legs or days ≤ incumbent, or a placebo is not beaten.
Independent re-sum asserted in-run for every battery. All figures paper, 1 lot.
Computation: `repair_programme_2026-11-12.py` → `repair_programme_2026-11-12_results.json`.

## HEADLINE

**Nothing passed.** Every fix variant built from November's losses failed the
Jan–Oct gate — in each case because the class November indicts is *net positive*
across Jan–Oct. November's index losses are, on the stored evidence, bad draws
inside positive classes plus one real, already-fixed leak (Nifty B PE). The
December route to a second green segment is therefore not a new variant: it is
the already-gate-passed Nifty TUNED line (B PE removed), ranked below.

## 0. CORRECTIONS TO THE BRIEF'S EVIDENCE (from the logs, direct)

- Bank November is **not** "4 PE base stop-outs, NS1 2/2". The primary log shows
  6 legs, −₹1,920: **2 Skill V3 PE base legs** (Nov 2, Nov 9; −₹1,720 each) and
  **4 NS1 CE second legs — 2 stops (Nov 3, Nov 4) and 2 targets (Nov 11, Nov 12),
  net +₹1,520**. NS1 is 2/4, not 2/2.
- DEC-S1 Component B is **not** "0-for-3, −₹7,160" over the full November
  record. That was the state through Nov 5. All four B legs (log-reconciled):
  Nov 2 PE be_stop −₹220 · Nov 3 PE stop −₹3,470 · Nov 5 PE stop −₹3,470 ·
  Nov 11 PE runner_stop **+₹3,680** → **B net −₹3,480, 1 win in 4**. The real
  indictment of B PE is Jan–Oct: **23 legs, −₹11,881.75, 8 full stops**
  (vs B CE **+₹45,506.50 / 26 legs**, the book's best cell — the flaw is
  PE-specific, not B-specific).

## B1 — BANK PE-STOP FLAW CYCLE

### Diagnosis (November primary log + journal; only what the data shows)
The four −₹1,720 losses share exactly this:
1. All four are **full −50 premium stops under G0** — none reached +90. Shapes
   differ: Nov 9 PE never developed (MFE +3.35, stopped on its own entry bar);
   Nov 4 NS1 flickered +24.6 and faded; Nov 3 NS1 *developed* (+33.4 by 10:30)
   then gave everything back to the full stop; Nov 2 PE stopped within 5 min.
2. The two PE losses are the same admission class: **Skill V3 PE solo**, kept
   only by B2's after-09:55 clause, entries **10:20 and 10:45**.
3. The two NS1 losses are CE second legs whose S1 base had exited **by stop**
   (10:00, 09:35).
Non-separators, stated plainly: base-exit reason does **not** separate NS1
(Nov 12's winner also followed a stop-exit base, 12:05); NS1 entry times
interleave (L 10:20/13:40, W 12:45/14:00); room_ratio was inf on both NS1
losers *and* on the Nov 11 winner. And the historical check reverses the PE
impression: Jan–Oct, Skill V3 PE legs entering ≥10:15 are **+₹10,646.50 over
14 legs**; the negative Skill PE cell is the *early* one (<10:15: −₹2,360 / 8).
November indicted a positive class on a 2-leg sample.

### Variants (gated on the v21 frame — the primary's own Jan–Oct record,
99 legs / +₹83,650.50, re-verified in-run; admission filters only, so the
filter definition is geometry-independent; incumbent months: Jan +22,748,
Feb +20,480, Mar +1,120, Apr −90, May +17,680, Jun +560, Jul −3,680,
Aug −873.5, Sep +10,776.5, Oct +14,929.5; H1 +62,498 / H2 +21,152.5;
ex-top-3 +54,610.50)

**BV-1 — drop Skill V3 PE base legs entering ≥ 10:15 → FAIL (gate, 6 legs).**
Jan–Oct: 85 legs, **+₹73,004.00** vs incumbent +₹83,650.50 (the dropped 14 legs
are worth +₹10,646.50). H1 +53,768 / H2 +19,236 (both below incumbent);
ex-top-3 +₹43,964 (below); chrono placebo (drop first-14 Skill PE) +₹77,280.50
also beats it. November counterfactual: full month +₹1,520 (both PE losses
removed, NS1 winners untouched) — but on the four losing days it still leaves
−₹3,440 (the NS1 days), so it fails the pre-registered November leg as well.

**BV-2 — drop all Skill V3 PE legs → FAIL (gate, 6 legs).**
Jan–Oct: 77 legs, **+₹75,364.00** (dropped class is worth +₹8,286.50).
H1 below incumbent; ex-top-3 below; chrono placebo ties it exactly
(+₹75,364.00 — not beaten); mirror placebo (drop Skill CE) is a no-op at
+₹83,650.50 because the v21 frame contains **zero** Skill CE legs — Skill's
entire v21 contribution is PE, and it is positive. November counterfactual
identical to BV-1 (+₹1,520 month; −₹3,440 on the losing days) → November leg
also fails.

**BV-3 — NS1 second legs only when the S1 base exited by target → FAIL.**
November: removes both NS1 losses but also kills Nov 12's winner (+₹2,480,
stop-exit base) — violates the "do not kill the NS1 winners" clause outright;
losing-days counterfactual −₹3,440 (PE days remain); full month −₹960 < 0.
Jan–Oct: **not gateable** — the base leg's exit reason is not a field in the
stored leg list, so no controlled score exists. (Observation, not a candidate:
the only perfect November separator found — NS1 admitted only if the base
exited ≥10:40 — is a threshold fitted between two points on n=4 and is equally
ungateable from stored data. It is recorded so the idea is evidence, not silence;
it earns nothing until a causal, stored feature exists.)

## B2 — BANK NS1-CENTRIC ASSEMBLY (from TUNED STACK v2, 111 legs / +₹127,351.50)

Second-leg families in the stack: NS1_second, NS3_gapclass, S3-R1, S3-PDC,
EVE06_REENTRY (59 legs, +₹62,405.50 standalone). BASE = 52 legs, +₹64,946.00.

**B2-LITERAL** (BASE kept only on days where a second-leg structure exists
that day): **timing audit FAIL** — a morning BASE leg cannot know a second leg
will trigger later that day. Scored as an observation only: +₹55,635.50 — it
would fail the gate anyway.

**B2-FOLLOWER** (causal version: BASE kept only if a second-leg-family leg
entered *earlier* the same day) → **FAIL (gate, all legs).**
60 legs, **+₹64,885.50** vs incumbent +₹127,351.50. The 51 dropped BASE legs
are worth +₹62,466. H1 +38,042 / H2 +26,843.50, ex-top-3 +₹48,862.50 — all far
below incumbent; latest-skip placebo +₹72,085.50 beats it; **anti-rule placebo
+₹134,121.50 beats everything, including the incumbent** — i.e. the association
runs the other way: stack BASE legs earn *more* on days with no second-leg
structure (BASE on quiet days ≈ +₹71,716 of the book; BASE on second-leg days
≈ −₹6,770). The anti-rule itself uses day-level knowledge and is **an
observation, not a candidate** — but it kills the centring premise with data:
second legs are not where the stack's strength concentrates. November
counterfactual for FOLLOWER: +₹2,480 (Nov 4 S3-R1 kept; Nov 9 BASE dropped) —
the November leg passes in isolation; the Jan–Oct gate failure stands.

## N1 — NIFTY B-LEG

Reconciled B record above (§0). The B-PE fix **already exists and already
passed**: NIFTY-EVE-07 (DEC-S1 minus B PE → TUNED v1, +₹103,050.25 / 74 legs,
GATE PASS 2026-11-05) and EVE-11 (→ TUNED v2, +₹115,950.75 / 59 legs, GATE
PASS). Neither is re-gated here.

**TUNED v2 November forward score** (derived leg-for-leg from the
candle-scored DEC-S1 shadow log — drop-only filter on component + direction,
fixed at the entry bar, timing clean): DEC-S1's November legs are B PE ×4 and
C CE ×1 — v2 excludes both classes → **TUNED v2 Nov 2–12: 0 legs, ₹0.**
**TUNED v1 November forward:** keeps only the C CE leg → **+₹3,036.50 / 1 leg**
— the only positive November forward record in the Nifty tuned line.
DEC-S1 itself: −₹443.50 / 5 legs. Primary C3G7: −₹3,470 / 1 leg.

**NB-1 — B PE conditioned on gap size → NOT TESTABLE.** The scored DEC-S1 leg
store carries no per-leg gap field (the leg file has component/direction/
entry only; nets live in the engine's candle scoring). Building the feature
means a full DEC-S1 re-derivation — no controlled score is quoted. The gap
evidence that does exist argues against a size rule anyway: November's B PE
fired on gap-ups of +1.74% (lost) and on the Nov 11 gap-up (won +₹3,680);
the journal's named cause for the losses is gap-*continuation*, a post-entry
property, not an admission-time one.

## RANKED DECEMBER CANDIDATES

**Bank Nifty**
1. **TUNED STACK v2 (unchanged)** — +₹127,351.50 Jan–Oct gate PASS, all 10
   months positive; November backfill +₹760; its live ledger is the
   operational gap (repair already running separately). Nothing in this
   programme came within ₹60,000 of it.
2. v22 frame (+₹91,450.50) — control lineage if the stack's live record fails.
3. Legacy BNF-PAPER-V1 — November −₹1,920; its two indictable classes are
   historically positive; no filtered version of it is promotable.

**Nifty**
1. **TUNED SHADOW v1 (DEC-S1 − B PE)** — gate PASS (+₹103,050.25) *and* the
   only positive November forward record (+₹3,036.50). The B-PE leak
   (−₹11,881.75 Jan–Oct; −₹3,480 November) is removed by construction.
2. **TUNED SHADOW v2 (EVE-11)** — strongest gate (+₹115,950.75, no red month)
   but zero November trades: chosen, if chosen, on gate evidence alone.
3. **DEC-S1 (frozen candidate)** — November −₹443.50; carries the B-PE leak.
   Primary C3G7 (−₹3,470 / 1 trade in 8 days) is not a December candidate
   on this record.

**On the owner's condition (≥2 of 3 segments green):** Stocks is green
(+₹8,391.28 MTD). No variant in this programme manufactures a second green
segment — the honest second segment is Nifty under TUNED v1/v2, whose edge is
precisely the removal of the one leak (B PE) that both the Jan–Oct gate and
November forward data independently indict. Bank's December case rests on the
stack's live record once scoring is repaired; forcing a Bank variant through
on November's 6 legs would repeat the exact error the controls gate exists
to prevent.

*Caveats: B1 gating uses the v21 regen leg list (runner geometry) as the
primary frame's historical record — the project's own bookkeeping convention;
filters are admission-side only. B2/N1 derivations are drop-only filters on
candle-scored leg lists; no leg was re-priced. All November counterfactuals
recomputed from the primary/shadow logs as written.*
