# NOVEMBER FIX, PART 1 — GAP-REGIME GUARD — 2026-11-13

**Owner order 2026-11-13 05:58 IST:** "I want the fix of November also, since October is
profitable." Evidence base: `november_failure_audit_2026-11-13.md`, money-cause #1 — November's
Bank days had median opening gaps at the top of the year's distribution (Nov median |gap| 0.508%
vs Jan–Oct 0.303%) and 4/8 days reversed ≥0.7% after 11:00; the deduped Bank losses concentrated
in PE legs (1W/3L) while CE legs made money.

**Verdict up front: NOTHING PASSES. All six variant×index combinations FAIL the standing
Jan–Oct gate, and the November lens is worse than neutral — the guard would have changed
nothing at all for the Bank stack in November (Δ ₹0 under every variant) and would have made
Nifty TUNED v1's November worse under G-2 (Δ −₹3,036.50). No December candidate arises from
this programme. No bar was moved.**

Paper only, real money ₹0. Index figures = option premiums per 1 lot, net of ₹220/trade
(costs are inside the recorded leg nets). Frozen November books untouched; this was a
December-candidate overlay test on the frozen Jan–Oct leg streams.

Computation: `november_fix_gapguard_2026-11-13.py` → `november_fix_gapguard_2026-11-13_results.json`;
kept/removed leg CSVs per variant alongside (`november_fix_gapguard_2026-11-13_{bank,nifty}_{G1,G2,G3}_{kept,removed}.csv`).

---

## 1. FROZEN SPEC (registered before scoring)

**Incumbents (anchors re-verified in-run, asserted):**
- Bank = TUNED STACK v2 leg stream (`bank_positive_tuning_2026-11-10_eve19_trades.csv`):
  **+₹127,351.50 / 111 legs**; months Jan +24,028.00 · Feb +15,284.00 · Mar +8,560.00 ·
  Apr +9,810.00 · May +25,400.00 · Jun +3,040.00 · Jul +4,224.00 · Aug +2,059.50 ·
  Sep +15,056.50 · Oct +19,889.50 (all positive); H1 +86,122.00 · H2 +41,229.50;
  ex-top-3 legs +100,528.50 · ex-top-3 days +100,528.50.
- Nifty = TUNED v1 = DEC-S1 stream (`nifty_next_phase_trades.csv`, +₹91,168.50 / 97 legs)
  minus (component B & PE) legs: **+₹103,050.25 / 74 legs**; months Jan +15,531.25 ·
  Feb +9,229.25 · Mar −1,216.50 · Apr +24,411.25 · May +4,364.00 · Jun +4,828.00 ·
  Jul +10,463.00 · Aug +1,911.75 · Sep +13,367.75 · Oct +20,160.50; H1 +57,147.25 ·
  H2 +45,903.00; ex-top-3 legs +69,585.25 · ex-top-3 days +69,585.25.

**Gap (audit-exact definition):** sessions = days with ≥70 bars in the stored 5-minute spot
series (`data/progressive/{BANKNIFTY,NIFTY}/spot_5m.csv`, which spans 2025-01-01 → 2026-10-28,
plus `data/banknifty-2026-11/spot_5m.csv` and `oi_history/spot_nov_bars.json` for November);
gap_t = (open_t − close_{t−1}) / close_{t−1} × 100, prior session = previous stored session,
close = last bar's close.

**Threshold (causal):** thr_t = 85th percentile (numpy, linear) of |gap| over the **prior 60
stored sessions, strictly prior** to day t. The 2025 sessions in the store provide the
warm-up — every 2026 session, January included, has a full 60-session prior window. No
full-sample statistic touches any day's trigger.

**Variants (day-level overlay; the skip decision is complete at 09:15 — the gap is the open
print vs the prior close, and the threshold uses only prior sessions):**
- **G-1:** |gap_t| ≥ thr_t → skip that day's **PE legs** (CE legs run).
- **G-2:** |gap_t| ≥ thr_t → skip **all legs** that day.
- **G-3:** gap_t ≥ +thr_t (large gap-**up** — the direction adverse to a PE entry) → skip that
  day's **PE legs**.

**Scoring convention (house precedent — TUNED v1/v2 and BV-1/BV-2 were gated exactly this
way):** drop-only filter on the frozen assembled leg stream; kept legs keep their recorded
`net_inr`. Independent re-sum asserted in-run for every variant: candidate total ≡ incumbent
total − removed-leg sum, to the paisa.

**Gate (project standard, EVE-07…20 / repair programme):** a candidate FAILS if total ≤
incumbent, any month flips green→red, H1 < incumbent H1, H2 < incumbent H2, ex-top-3 legs ≤
incumbent, ex-top-3 days ≤ incumbent, or a placebo is not beaten. Placebos registered:
(a) **random-day skip** — same removed-leg class on the same number of fired days, 1,000
seeds, candidate must exceed the 95th percentile; (b) **shuffled-gap** — the gap series
permuted across sessions (dates fixed), thresholds and triggers recomputed through the
identical rolling machinery, 200 permutations, candidate must exceed p95; (c) **mirror** —
G-1: skip CE instead of PE on the guard days; G-3: skip PE on large gap-**down** days
(gap_t ≤ −thr_t); candidate must exceed the mirror total. G-2 has no mirror (skip-all is
direction-symmetric); the random-day placebo binds.

**November lens (owner's question — reported, cannot promote):** the same guard applied to
the incumbents' actual November legs (Bank stack log: Nov 4 PE +2,480 · Nov 9 PE −1,720 ·
Nov 12 PE −1,720 = −960; TUNED v1 derived leg-for-leg from the DEC-S1 shadow log minus B-PE:
Nov 3 C CE +3,036.50 = +3,036.50), with thresholds rolled causally through October into
November.

**Series validation against the audit:** Nifty Jan–Oct median |gap| = **0.262%** (audit:
0.262% ✓); Bank Jan–Oct median |gap| = **0.300%** (audit: 0.303% — a one-session median
granularity difference; every published day value reproduces exactly); Bank November gaps
**Nov 2 +1.05 · Nov 5 +2.13 · Nov 11 +1.31** ✓✓✓ and November median |gap| **0.508%** ✓;
Nifty November Nov 4 −0.29 ✓ · Nov 5 +1.74 ✓ · Nov 6 +0.01 ✓ · Nov 12 −0.16 ✓ (Nov 12 has no
stored bars anywhere; its −0.16% is the DEC-S1 shadow scorer's own recorded gap, flagged
where used — it touches no leg and no leg-day threshold).

---

## 2. RESULTS — BANK NIFTY (incumbent: TUNED STACK v2, +₹127,351.50 / 111)

| Variant | Removed | Candidate | Δ vs incumbent | Gate |
|---|---|---|---|---|
| G-1 (skip PE, \|gap\|≥thr) | 15 legs / 13 days, net **+18,376.50** | +108,975.00 / 96 | **−18,376.50** | **FAIL — 8 of 9 legs** |
| G-2 (skip all, \|gap\|≥thr) | 20 legs / 16 days, net **+30,626.50** | +96,725.00 / 91 | **−30,626.50** | **FAIL — 8 of 8 legs** |
| G-3 (skip PE, gap-up ≥thr) | 6 legs / 5 days, net **−2,370.00** | +129,721.50 / 105 | **+2,370.00** | **FAIL — 3 of 9 legs** |

**G-1** removes PE legs across BASE (8), NS1_second (3), NS3_gapclass (2), EVE06_REENTRY (2) —
and those legs were worth **+₹18,376.50**. The candidate (+108,975.00) is below the random-day
placebo's *median* (p50 113,392.75; p95 126,072.68), below the shuffled-gap p95 (129,977.48),
and below its own mirror (skip-CE on the same days: +115,101.50). On extreme-gap days the
stack's PE legs are, across ten months, a profit centre — November's three PE stops are not
the class's character.

**G-2** removes +₹30,626.50 of legs (BASE 11, NS3 4, NS1 3, EVE06 2) → +96,725.00. Fails
every scored leg (random-day p95 120,958.90; shuffled p95 127,059.13). Sitting out the
year's biggest-gap days wholesale is the most destructive variant tested.

**G-3** is the only variant whose removed set is net-negative: Jan 13 NS3 PE −1,720 ·
Jan 22 NS1 PE +2,030 · Mar 5 NS1 PE −1,720 · Mar 5 EVE06 PE −1,720 · Apr 1 BASE PE −1,720 ·
Oct 5 BASE PE +2,480 → net −2,370. Candidate +129,721.50 **passes** total, no-month-flip,
H1 (90,972.00 ≥ 86,122.00), ex-top-3 legs and days, and beats its mirror decisively (the
gap-down mirror removes 9 PE legs worth +20,746.50 → 106,605.00). It **fails**:
- **H2:** 38,749.50 < incumbent 41,229.50 — the entire shortfall is one leg, the Oct 5
  +₹2,480 BASE PE winner, removed on a gap-up day in H2 while all the H1 removals were losers;
- **random-day placebo:** p95 = **130,031.50** > candidate 129,721.50 (p50 121,856.50) —
  skipping PE on 5 random days beats the guard's chosen days at the 95th percentile;
- **shuffled-gap placebo:** p95 = **130,612.90** > candidate (p50 121,975.50).
Sensitivity (not part of the registered gate): the placebo shortfall is robust to the
frequency definition — G-3 fired on exactly 5 traded days under both readings (removal days =
trigger days among traded days = 5), and a leg-count-matched placebo (drop 6 random PE legs,
1,000 seeds) gives p95 = 130,614.75, also above the candidate. **The +₹2,370 (+1.9%)
improvement is inside the noise of skipping almost any five days.** Directionally the
least-wrong variant; statistically indistinguishable from chance; and negative in H2. FAIL
stands, bars unmoved.

**November lens — Bank: Δ ₹0.00 under G-1, G-2 and G-3.** Guard states for the stack's leg
days: Nov 4 gap −0.10% (thr 0.491, no fire) · Nov 9 gap **+0.23%** (thr 0.503, no fire) ·
Nov 12 gap +0.02% (thr 0.590, no fire). The guard *did* fire on Nov 2 (+1.05%), Nov 3 (+0.79%),
Nov 5 (+2.13%) and Nov 11 (+1.31%) — precisely the audit's hostile days — but the stack held
**no legs on any of those days**. The stack's actual November losses were ordinary-gap-day PE
stops: the Nov 9 catastrophe (entry-bar stop, then +835 pts against) happened on a +0.23% gap
day that no gap-regime rule keyed at the open can see. For this incumbent, the protection and
the losses simply never intersected in November.

## 3. RESULTS — NIFTY (incumbent: TUNED v1, +₹103,050.25 / 74)

| Variant | Removed | Candidate | Δ vs incumbent | Gate |
|---|---|---|---|---|
| G-1 (skip PE, \|gap\|≥thr) | 5 legs / 5 days, net **+25,745.00** | +77,305.25 / 69 | **−25,745.00** | **FAIL — 8 of 9 legs** |
| G-2 (skip all, \|gap\|≥thr) | 21 legs / 17 days, net **+41,799.75** | +61,250.50 / 53 | **−41,799.75** | **FAIL — 8 of 8 legs** |
| G-3 (skip PE, gap-up ≥thr) | 1 leg / 1 day, net **+3,680.00** | +99,370.25 / 73 | **−3,680.00** | **FAIL — 6 of 9 legs** |

**G-1** removes exactly 5 legs — all Component A PE — worth **+₹25,745.00** (H1 collapses
57,147.25 → 38,762.25; March deepens −1,216.50 → −16,051.50, already red so not a "flip", but
the half-year legs catch it). The candidate is below every placebo (random-day p95
107,920.39; shuffled p95 107,320.60; mirror 86,995.50 — the mirror removes 16 CE legs worth
+16,054.75 and still lands above the candidate). In TUNED v1, the PE legs that survive the
B-PE removal earn their most on extreme-gap days.

**G-2** removes 21 legs (B 14, A 7) worth **+₹41,799.75** → +61,250.50, failing everything
(random-day p95 100,116.35; shuffled p95 106,370.84). Structural note: DEC-S1's Component B
is itself gap-triggered (the gap-fade fires on |gap| ≥ 0.50% days), so G-2 on this frame
partly amounts to switching the fade off on its biggest days — and in v1's retained
population those days are profitable. Recorded as an interaction, not an identity (see §4).

**G-3** fires on exactly **one** traded day all year and removes one leg — Oct 21, Component
A PE, **+₹3,680.00**, a winner. Candidate 99,370.25 fails total, H2 (42,223.00 < 45,903.00),
both ex-top-3 legs, and both statistical placebos (random-day p95 106,520.25 — with k=1 the
placebo is "delete one random traded day's PE legs"; shuffled p95 107,205.33). It beats only
its mirror (gap-down PE skip: 80,985.25) and the H1/no-flip legs. A one-leg variant cannot
carry a fix.

**November lens — Nifty:** G-1 Δ ₹0.00 · G-3 Δ ₹0.00 (v1's only November leg is a CE; both
variants skip PE only) · **G-2 Δ −₹3,036.50**: Nov 3's gap was +0.60% vs thr 0.480 → G-2 fires
and skips the Nov 3 Component C CE leg, TUNED v1's only November trade and its only November
win (candidate November total ₹0 vs incumbent +₹3,036.50). The one variant that touches
Nifty's November makes it worse.

## 4. DISTINCTION FROM CLOSED ROUTES (mandatory)

BV-1/BV-2 (repair programme, 2026-11-12) and the closed stack admission filters key on
**which signal fired**: BV-1 deletes Skill V3 PE base legs entering ≥10:15, BV-2 deletes all
Skill V3 PE legs — a leg class, on every day it occurs, regardless of market state. The gap
guard keys on **no signal at all**: it reads one day-level market-state variable (the opening
gap against its own trailing 60-day distribution), observable in full at 09:15 before any
entry exists, and is blind to family, system and entry time.

The computation confirms the instruments are not functionally identical on the leg
population (identity check in the results JSON):
- On the stack stream, the BV-1/BV-2 removed set is the same 13 legs under both definitions
  (all 13 Skill V3 PE legs in this stream enter ≥10:15), worth +₹12,366.50. G-1's removed set
  overlaps it by **2 legs of 15**; G-3's by **1 leg of 6**; 11 of the 13 BV-class legs are
  never touched by any guard variant, and the guard removes BASE/NS1/NS3/EVE06 legs that no
  BV filter can see. Not identical — not close.
- On Nifty, EVE-07's removed class (Component B PE) **cannot recur** on the TUNED v1 stream:
  the stream contains zero B-PE legs by construction (verified in-run). Every guard removal
  on Nifty is an A-component leg (G-1/G-3) or an A/B leg removed by day state, not identity
  (G-2).
- The one genuine adjacency: DEC-S1's Component B entries are themselves gap-triggered, so a
  day-state gap overlay interacts with that component's population (G-2 removes 14 B legs on
  extreme days). Interaction is not identity — the guard never reads the component field;
  it removes A legs on the same days by the same rule — and the interaction is reported, not
  hidden.

The guard was therefore a legitimately new instrument. It fails on evidence, not on
resemblance to a closed route.

## 5. TIMING AUDIT

The overlay's full information set at decision time (09:15): today's open print (the first
5-minute bar's open) and the prior session's close — the gap is complete at the open print —
and a threshold computed from the 60 strictly-prior sessions. No intraday bar, no signal, no
leg information from day t enters the decision. Causality holds by construction; the rolling
percentile was recomputed per day from prior sessions only (code + the November table's
monotone threshold path 0.471 → 0.590 for Bank are inspectable in the results JSON).
Two data-boundary disclosures, both immaterial and neither touching a leg day:
(i) the spot store ends 2026-10-28, so the stored-chain gap for 2026-11-02 spans the missing
Oct 29–30 sessions (Nifty reads +2.31% vs the shadow scorer's +0.73% against the official
Oct 30 close; Bank's +1.05% is the audit's own stored-chain figure). Neither incumbent held a
Nov 2 leg; the value enters later November thresholds only as 1 of 60.
(ii) Nifty Nov 9 reads +0.18% from the reconstructed bars vs the DEC-S1 scorer's +0.36%
(a different Nov 6 close source) — both sit far below Nov 9's threshold (0.544), so the guard
state is identical either way, and v1 held no Nov 9 leg.

## 6. CONCLUSION

The audit's diagnosis was correct about the month and wrong as a repair manual — or rather,
the repair it suggests does not survive contact with the ten months. November's Bank patch
really was gap-heavy and reversal-prone, and PE really is where the books bleed on such a
patch. But across Jan–Oct, extreme-gap days are **good** days for these books' PE legs
(Bank G-1 removed set: +₹18,376.50; Nifty G-1: +₹25,745.00 on five legs), because the same
volatility that reversed on four November mornings trends, and pays, on most others. The
single directionally-right variant (Bank G-3, skip PE only after large gap-**ups**) buys
+₹2,370 across ten months — a sum the placebos reproduce by skipping random days — and pays
for it in H2 with one October winner. And on the days November actually hurt the incumbent
Bank book (Nov 4, 9, 12), the gap at the open was −0.10%, +0.23% and +0.02%: there was
nothing at 09:15 to guard against.

**No variant is promoted. No December candidate arises. The incumbents stand.** The November
losses this fix was aimed at are, on the full evidence, the H5 draw the audit also recorded —
a below-average 8-day window inside each book's normal distribution — and the gap-regime
overlay joins the closed routes: never retest identically.
