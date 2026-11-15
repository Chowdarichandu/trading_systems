# PHASE-3B TUNING — BANK NIFTY · INVERTED CONDITIONING (QUIET-VOLUME + SPECULATION-FADE) ON TUNED STACK v2 · 2026-11-14

Spec: `phase3b_inverted_bank_SPEC.md` (frozen 2026-11-14 09:09 IST, before scoring).
Numbers: `phase3b_inverted_bank_results.json`. Script: `phase3b_inverted_bank_build.py`.
Research only — no book, ledger, or job changed.
Basis: paper, 1 lot, costs as in the gated store.

This run is the frozen test of phase 3's post-hoc observation. Phase 3's confirmation
gates all failed, and two dials *looked* inverted in its tables: the volume gates'
dropped sets were worth +₹28k…+₹88k, and the speculation lean's flipped books beat its
kept books at both reads. Phase 3 refused to flip a failed conditioner after seeing the
result; this run froze the flip first, then scored it. Alignment was not retested
(it measured a coin flip both ways).

## Control + validation (all before any phase-3B scoring)
- Control reproduced exactly: **111 legs · +₹127,351.50 · WR 59.5% · 89 trade-days ·
  ₹1,430.92/trade-day · 60G/29R/116NT of 205 · H1 +₹83,082.00 / H2 +₹44,269.50 ·
  ex-top-3 +₹100,528.50 · zero red months**, plus independent raw re-sum +₹127,351.50.
- State validation: phase 3's own points A / B / C1.0 / C5-1.0 recomputed from this
  run's state matched phase 3's published kept counts, dropped counts, dropped totals
  and kept totals **exactly at both reads (8/8)**. Coverage matched: futures state
  complete 205/205 Jan–Oct days at both reads; speculation complete 116/205; post-read
  legs 76 @10:00 / 42 @11:00; post-read spec-ok legs 44 @10:00 / 27 @11:00.
- Reference sets reproduced with phase 2's own code: confidence gate (≥ 0.5) kept 88
  legs, +₹122,337.50, WR 62.5%; B-FIX-1 kept 94 legs, +₹131,510.00; their intersection
  71 legs (80.7% of the phase-2 set, Jaccard 64.0%).

Pass bar (unmoved): WR ≥ 60% · ₹/trade-day ≥ ₹900 · total ≥ ₹76,410.90 (60% of book) ·
both halves > 0 · ex-top-3 > 0 · placebo ≥ 95th pct · kept total > flipped total ·
kept total > dropped total · no red month.

## Results — every grid point FAILS the frozen pass bar

### Read 10:00 (76 post-read legs; 35 pre-read legs worth +₹26,650.00 are always kept)
| Point | Kept | Dropped (₹) | Total | WR | ₹/TD | Placebo pct | Flipped | Verdict — failing legs |
|---|---|---|---|---|---|---|---|---|
| QVP-1.0 | 91 | 20 (+46,984.00) | +₹80,367.50 | 54.9% | 1,100.92 | 3.0 | +₹73,634.00 | FAIL — WR, placebo, red Jun |
| QVP-0.9 | 82 | 29 (+57,967.00) | +₹69,384.50 | 54.9% | 1,051.28 | 3.0 | +₹84,617.00 | FAIL — WR, total, placebo, flipped, red Jun |
| QVP-0.8 | 71 | 40 (+60,756.50) | +₹66,595.00 | 56.3% | 1,128.73 | 14.5 | +₹87,406.50 | FAIL — WR, total, placebo, flipped |
| QV5-1.0 | 93 | 18 (+23,574.00) | +₹103,777.50 | 58.1% | 1,365.49 | 31.5 | +₹51,504.00 | FAIL — WR, placebo |
| QV5-0.9 | 86 | 25 (+34,506.50) | +₹92,845.00 | 58.1% | 1,326.36 | 29.5 | +₹62,436.50 | FAIL — WR, placebo, red Aug |
| QV5-0.8 | 73 | 38 (+71,246.50) | +₹56,105.00 | 54.8% | 967.33 | 0.5 | +₹99,176.50 | FAIL — WR, total, placebo, flipped, dropped, red Aug |
| SF fade | 96 | 15 (+3,969.00) | +₹123,382.50 | 61.5% | 1,581.83 | 93.0 | +₹93,758.00 | FAIL — placebo, red Aug |
| QFP-0.9 | 89 | 22 (+20,111.00) | +₹107,240.50 | 59.6% | 1,489.45 | 68.5 | +₹109,900.00 | FAIL — WR, placebo, flipped, red Jun+Aug |
| QF5-0.9 | 87 | 24 (+16,671.00) | +₹110,680.50 | 60.9% | 1,558.88 | 82.5 | +₹107,740.00 | FAIL — placebo, red Aug |

### Read 11:00 (42 post-read legs; 69 pre-read legs are always kept)
| Point | Kept | Dropped (₹) | Total | WR | ₹/TD | Placebo pct | Flipped | Verdict — failing legs |
|---|---|---|---|---|---|---|---|---|
| QVP-1.0 | 104 | 7 (+12,471.50) | +₹114,880.00 | 58.7% | 1,335.81 | 19.0 | +₹98,300.00 | FAIL — WR, placebo |
| QVP-0.9 | 101 | 10 (+21,711.50) | +₹105,640.00 | 57.4% | 1,272.77 | 13.5 | +₹107,540.00 | FAIL — WR, placebo, flipped |
| QVP-0.8 | 92 | 19 (+22,347.50) | +₹105,004.00 | 59.8% | 1,363.69 | 47.5 | +₹108,176.00 | FAIL — WR, placebo, flipped |
| QV5-1.0 | 104 | 7 (+12,471.50) | +₹114,880.00 | 58.7% | 1,335.81 | 20.5 | +₹99,580.00 | FAIL — WR, placebo |
| QV5-0.9 | 102 | 9 (+13,231.50) | +₹114,120.00 | 58.8% | 1,358.57 | 33.5 | +₹100,340.00 | FAIL — WR, placebo |
| QV5-0.8 | 93 | 18 (+18,814.50) | +₹108,537.00 | 60.2% | 1,391.50 | 57.0 | +₹105,923.00 | FAIL — placebo |
| SF fade | 104 | 7 (+6,116.00) | +₹121,235.50 | 58.7% | 1,426.30 | 61.5 | +₹123,197.00 | FAIL — WR, placebo, flipped |
| QFP-0.9 | 101 | 10 (+9,356.00) | +₹117,995.50 | 58.4% | 1,404.71 | 55.0 | +₹126,437.00 | FAIL — WR, placebo, flipped |
| QF5-0.9 | 101 | 10 (+6,356.00) | +₹120,995.50 | 59.4% | 1,440.42 | 72.5 | +₹124,717.00 | FAIL — WR, placebo, flipped |

Halves and ex-top-3 were positive at **every** grid point (weakest: QV5-0.8 @10:00 halves
+₹37,448/+₹18,657, ex-top-3 +₹33,782) — no point failed on those two legs. No month was
fully idled at any point. Boundary ties: **zero** legs sat exactly on any volume
threshold, so each QUIET-VOL kept set is the exact mirror partition of phase 3's
opposite gate on the conditioned legs (e.g. QVP-1.0's kept total +₹80,367.50 *is*
phase 3 C1.0's flipped total, to the paisa). Month table for the nearest miss,
SF @10:00: Jan +24,028 · Feb +10,324 · Mar +12,000 · Apr +9,810 · May +22,920 ·
Jun +3,040 · Jul +9,525 · Aug **−420.50** · Sep +14,746.50 · Oct +17,409.50.

## What each dial actually did

- **QUIET-VOL — the "inversion" was an aggregate-size illusion, and it is now refuted
  on a frozen test.** Phase 3's dropped sets summed large because they were large:
  at 10:00 the ≥1.0 gate dropped **56 legs worth +₹53,717.50 = +₹959/leg**, while the
  20 loud-morning legs it *kept* made **+₹46,984.00 = +₹2,349/leg**. Both sides of the
  split earn (the book earns); per leg, the loud mornings pay ~2.4× the quiet ones —
  the volume dial was never inverted per leg, and phase 3's own table already contained
  both rates. Frozen the other way, quiet-keeping systematically holds the lower-rate
  legs: kept books land at the **0.5th–31.5th placebo percentile** at 10:00 (worse than
  random thinning — the selection is actively bad), WR falls to 54.8–58.1%, and the
  tighter cuts lose to their own flipped books. At 11:00 only 42 legs are in play, so
  the damage dilutes (percentiles 13.5–57.0) but every point still fails WR and/or
  placebo; the family's cleanest point, QV5-0.8 @11:00, fails *only* the placebo —
  a kept set indistinguishable from random thinning is not a conditioner.
- **SPEC-FADE — a real pulse at one read, a reversal at the other; not a channel.**
  @10:00 it is the run's nearest miss: it drops only the 15 legs the crowd lean agreed
  with (of 44 testable), and those legs netted just **+₹3,969.00 (+₹265/leg)** against
  the book's +₹1,148/leg average — kept WR 61.5%, ₹1,581.83/trade-day (best in this
  run), +₹123,382.50 = 96.9% of the book, beats flipped and dropped. It fails on two
  legs: placebo **93.0** (bar 95 — it beats 186 of 200 random 96-leg subsets, not
  enough), and August flips red by ₹420.50 because the fade removes +₹2,480 of a month
  whose whole cushion was +₹2,059.50. Two structural cautions ride on top: only 44 of
  76 post-read legs were testable — **32 of its 96 kept legs (33.3%) are NC-kept, never
  judged by the fade at all** — and at 11:00 the same rule *reverses*: WR 58.7%,
  placebo 61.5, and its flipped book **beats** it (+₹123,197.00 vs +₹121,235.50) on a
  27-leg testable population. A dial that selects well at 10:00 and against the book
  at 11:00, on overlapping legs in the same year, is a coincidence window, not signal.
- **QUIET+FADE — inherits both parents' wounds.** QF5-0.9 @10:00 (kept 87,
  +₹110,680.50, WR 60.9%, ₹1,558.88/TD, beats flipped and dropped) still fails placebo
  (82.5) and carries SF's red August; QFP-0.9 @10:00 fails WR and flipped as well.
  At 11:00 both combinations fail WR, placebo and flipped. Adding a refuted dial to a
  near-miss dilutes the near-miss; it does not rescue it.

## Overlap — is QUIET+FADE the confidence gate under a second name?
Substantially, yes in membership, no in value — stated plainly:
- QFP-0.9 @10:00: 76 of its 89 kept legs (85.4%) are also phase-2 confidence-gate legs;
  Jaccard 75.2%. QF5-0.9 @10:00: 87.4% share, Jaccard 76.8%. At 11:00 the shares are
  83–84% (Jaccard 80.0–81.7%). SF alone overlaps similarly (85.4% @10:00).
- Part of that overlap is mechanical: pre-read legs (35 @10:00, 69 @11:00) are kept by
  every conditioner, so any two mild conditioners share most of a kept set by
  construction. The discriminating comparison is money on the difference: the
  confidence gate keeps 88 legs for **+₹122,337.50 at WR 62.5% and passed its gate**
  (placebo 97th pct); QF5-0.9 keeps 87 legs for **+₹110,680.50** and fails. Where the
  two selections differ, the fade combination is ~₹11.7k worse. A kept set that is
  four-fifths the same list, earns less on the fifth that differs, and fails bars the
  original passed is not a new channel.

## November counterfactual (descriptive only — November sets no rule)
Actual November: **−₹2,680** (Nov 4 S3-R1 PE 09:55 +₹2,480, pre-read at both reads;
Nov 9 PE 10:45 −₹1,720; Nov 12 PE 11:30 −₹1,720; Nov 13 PE 12:20 −₹1,720).
- **SPEC-FADE: −₹2,680 at both reads — it never fires.** Speculation state re-verified
  NC on all 4 November leg-days at both reads; every conditioned leg is KEPT-NC. The
  fade has no November evidence, in either direction.
- **QUIET+FADE: −₹2,680 at both reads, all four points.** The combination inherits the
  NC wall: a combo point needs every component present, so on spec-NC days the volume
  component is disarmed too — even the one November idle the quiet dial achieves alone
  (below) disappears inside the combination.
- **QUIET-VOL: −₹2,680 at most points; −₹960 at three.** November's three losers were
  quiet-morning legs (ratio_prev 0.897 / 0.638 / 0.798 @10:00) — exactly the mornings
  this dial prefers, and Nov 12 (0.638 / 0.593, the quietest loser) is kept by every
  point at both reads. The exceptions: @10:00 the 0.8 cuts idle Nov 9 (0.897 > 0.8)
  → −₹960; @11:00 QVP-0.9/0.8 idle Nov 13 (0.989) → −₹960. Phase 3's November flattery
  belonged to the confirmation gates; the inverted dial keeps November's bleed almost
  in full. Four legs set no rule — but they vote the same way as the year's 111.

## Honest bottom line
**The inversion is phase 3's noise read backwards.** The volume "inversion" never
existed per leg — it was 56 positive legs summing louder than 20 better legs
(+₹959/leg vs +₹2,349/leg) — and frozen the other way, quiet-keeping is worse than
random thinning (placebo 0.5–31.5th percentile at 10:00). The speculation fade is the
only fragment with a pulse: at the 10:00 read it removes a genuinely poor set
(15 legs, +₹265/leg) and posts the run's best ₹/trade-day — but it misses the frozen
placebo bar (93.0 < 95), breaks August by ₹420.50, stands on 44 testable legs with a
third of its kept set unjudged, and reverses at 11:00 where its flipped book wins.
That is a story about 44 legs, not a property of the book. All 18 grid points FAIL;
TUNED STACK v2 stands unchanged, and the buildup/speculation surface is now closed in
**both** directions — confirmation (phase 3) and inversion (this run) — for
conditioning this book.
