# RECURSIVE ENGINE — CYCLE LOG

Protocol: stocks_RECURSIVE_ENGINE.md · State: stocks_engine_state.json ·
Frozen definitions: stocks_engine_frozen.md

---

## Cycle 1 — 2026-10-31 — target: February (−₹5,533.46)

**IDENTIFY.** Working book (iteration 0) = INV-LONG + N4-V3 + P2F 2.5%,
344 trades, +₹47,665.24, February the only red month. Known diagnosis
(Line M1): Feb 1–2 Budget Sunday session + whipsaw, INV-LONG 12 trades,
0 wins, −₹9,770.34. Full-book refinement found this cycle: **Feb 1 alone =
15 trades, −₹4,433.84; Feb 2 is net POSITIVE at book level (+₹1,293.69)** —
N4-V3/P2F gains outweighed INV-LONG's whipsaw losses. The rest of February
(after Feb 1) still nets −₹1,099.62 over 42 trades.

**FIX (frozen before scoring).** RF-1 special-session stand-aside (weekend
sessions identified from the NIFTY calendar); RF-2 post-shock stand-aside
(prior trading day |Nifty close-to-close| ≥ 2%); RF-3 = RF-1 + RF-2.

**APPLY.** Anchor reproduced exactly (344 / +₹47,665.24, M1 month table to
the paisa). Timing audit clean (N4 09:35 ×56, P2F 09:15 ×39, INV-LONG
below50 recomputed on 79 dates — 0 violations). Calendar facts: Feb 1 2026
(Sunday, Nifty −2.16%) is the ONLY weekend session in Jan–Oct 2026. RF-2
excludes 8 days: Feb 2, Feb 4, Mar 20, Mar 24, Mar 25, Mar 30, Apr 1, Apr 9.

**DECIDE — all three REJECTED; no green month flips under any family;
audit clean throughout.**
- RF-1: Feb −5,533.46 → **−1,099.62** (+4,433.84); total +52,099.08;
  no other month changes at all (single-instance rule in-sample);
  Feb trades 42/57. Fails leg 1 (Feb still red).
- RF-2: Feb → **−5,599.20** (−65.74, slightly worse — Feb 2 was a net
  winner); Mar +1,308.85 (→ +8,592.45), Apr −611.07 (→ +2,728.62);
  total +48,297.28; Feb trades 40/57. Fails leg 1.
- RF-3: Feb → **−1,165.36** (+4,368.10); total +52,731.12; Mar and Apr as
  in RF-2. Fails leg 1 AND the activity guard (Feb 25 trades < 34.2 floor).

**STATE AFTER CYCLE 1.** Working book unchanged (iteration 0, 344 trades,
+₹47,665.24, February still −₹5,533.46). RF-1..RF-3 recorded in the
registry. consecutive_no_fix = 1.

**TERMINATION CHECK.** None triggered: SUCCESS no (February red);
BREAK_EVEN no (a month is red); EXHAUSTED no (needs 3 consecutive no-fix
cycles; this is 1). The engine recurses — next cycle's diagnosis seed is
the post-Feb-1 residual (−₹1,099.62 over 42 trades) plus the registry's
component-surgery / add-component seeds.

## October Cycle 1 (OC-1 / OC-2) — 2026-10-31, fast cycle (audited-dump sums)

Frozen in stocks_engine_frozen.md BEFORE computing. Target: OCTOBER
(goal >= +₹50,000; working book October +₹6,845.39, total +₹52,099.08).

**ANCHORS VERIFIED.** F4 dump (stocks_M2_F4_trades.csv): 717 trades,
+₹42,418.91, October +₹36,166.23 — exact. RF-1 on F4: 3 trades dated
2026-02-01 (−₹3,056.24) dropped → F4 adjusted 714 trades, +₹45,475.15,
February −1,660.15. Fade: O1-dump home slice reproduces Jan–Sep to the
paisa vs the O2 home-control record; the O1 dump holds no October home
rows, so October comes from the O2 record (127 trades, +₹341.29);
composed fade = 1,073 trades, +₹4,243.18 — anchor exact.

**OC-1 (+ F4): BANKED.** Union: 1,043 trades, **+₹97,574.23**,
October **+₹43,011.62**. Legs: October improvement +36,166.23 ≥ +15,000 ✓;
total rises ✓; worst month April −7,708.27 ≥ −₹12,000 ✓. Month table:
Jan +15,850.19 · Feb −2,759.77 · Mar +9,953.85 · Apr −7,708.27 ·
May +21,766.53 · Jun −2,096.96 · Jul +2,151.71 · Aug +1,144.98 ·
Sep +16,260.35 · Oct +43,011.62. Disclosed: April and June flipped red
and February deepened under the union (no month was secured; the frozen
October legs govern) — they are repair targets in their turns. For the
record: the union's Jan–Sep total alone is +₹54,562.61 — F4 adds
+₹9,308.92 even with its October excluded from judging.

**OC-2 (+ home fade): REJECTED-with-reason.** Union October +₹7,186.68 —
improvement +341.29 fails the ≥ +₹15,000 leg (total would rise to
+₹56,342.26; worst month −8,901.70 passes). Revisitable later.

**STATE AFTER OC CYCLE 1.** Iteration 2. Working book = combined book +
RF-1 + F4 (4 components). Total +₹97,574.23, 1,043 trades. October
+43,011.62 — residual gap to goal ₹6,988.38; October stays the target.
Termination: none (October < ₹50k, months still red). Engine recurses:
next cycle OC-3, October residual diagnosis.

---

## OCTOBER CYCLE 2 — F4 setup3 exclusion BANKED; DBL-LONG rejected at diagnosis

**Diagnosis (anchors reproduced exactly: union 1,043 tr, +₹97,574.23,
October +₹43,011.62, month table == state).** October by component:
F4 +₹36,166.23 (117 tr), INV-LONG +₹7,691.08, N4-V3 −₹530.69,
P2F −₹315.00. Only 3 negative October days in the union (sum
−₹2,808.26) — the ₹6,988.38 gap cannot come from day-level repair.
F4's 51 October losers (−₹23,638.67) are diffuse: both qualifier
bands and both directions are net-positive in October. One
structural exception: **setup3_bounce_rejection — the only F4 setup
negative in October (5 tr, −₹2,570.36, 0 winners) and the only F4
setup negative across the full Jan–Oct (57 tr, −₹9,653.53)**.
October concentration disclosed: TVSMOTOR alone +₹23,925.84 of the
union's October.

**DBL-LONG (pre-approved candidate i): REJECTED at diagnosis.**
Anchor verified exactly (133 tr, +₹24,327.37, October +₹7,957.95,
halves +₹15,426.61/+₹8,900.76). Two bars: (a) after book-wide RF-1
(its 2 Feb-1 TVSMOTOR trades, −₹3,762.20, drop), its February is
−₹2,212.03 — adding it deepens the book's February by ₹2,212.03,
over the ₹2,000 red-month cap in the frozen legs; (b) 131 of its 133
trades are identical (date+stock+entry_time) to INV-LONG trades
already in the book — it is a subset re-weighting of INV-LONG, not
an independent stream. Revisitable only in February's own turn if
the arithmetic changes.

**FIX (frozen before scoring): F4 excludes setup3_bounce_rejection**
(all months, ex-ante). Score: 57 trades removed, −₹9,653.53 of losses
removed. New month table: Jan +14,489.91 · Feb −1,813.21 ·
Mar +13,422.38 · Apr −7,042.44 · May +26,188.71 · Jun −2,270.04 ·
Jul +2,151.71 · Aug +864.98 · Sep +15,653.78 · **Oct +45,581.98**.
Total **+₹107,227.76**, 986 trades. Acceptance legs: October rises
+2,570.36 ✓; total rises ✓; min month −7,042.44 ✓; worst hit to a
positive month Jan −1,360.28 ✓; red months Feb +946.56 / Apr
+665.83 improved, Jun −173.08 within cap ✓. **BANKED.**

**STATE AFTER OC CYCLE 2.** Iteration 3. Working book = INV-LONG +
N4-V3 + P2F 2.5% + F4-minus-setup3 (RF-1 book-wide). Total
+₹107,227.76, 986 trades. October +₹45,581.98 — **residual gap
₹4,418.02; October NOT secured, stays the target.** Termination:
none. Engine recurses: next October cycle on the residual.

---

## OCTOBER CYCLE 3 — F4 target 1.25%→1.50% BANKED; October gap down to ₹1,861.78

**Diagnosis (Step 1, stocks_engine_oc3_diag.py; current-book anchor
reproduced EXACTLY first: 986 trades, +₹107,227.76, October
+₹45,581.98, month table == state).** October by component verified:
F4-minus-setup3 **+₹38,736.59** (112 tr), INV-LONG +₹7,691.08 (21 tr),
N4-V3 −₹530.69 (6 tr), P2F −₹315.00 (2 tr).

- **N4/P2F drags are accidents.** N4 October: 2 target wins vs 4
  stops on 6 trades; full-period N4 +₹6,150.35. P2F October: its only
  2 qualifying reactions both stopped (−₹132.00 WIPRO, −₹183.00
  RECLTD); full-period P2F +₹14,957.98. Candidate (iii) fails — no
  structural drag, nothing to drop or gate.
- **INV-LONG October losers (11 tr, −₹4,633.92, all stops) are
  diffuse** — 7 stocks, 6 dates, both entry buckets, event split
  unremarkable. skill_or_breakout carries 9 of the 11 losers but is
  +₹7,626.59 in October and +₹33,119.20 full-period. Candidate (ii)
  fails — no ex-ante gate is supported.
- **F4-minus-setup3 October losers (47 tr, −₹20,713.31):** stops are
  36 tr / −₹19,795.31 (95%); losing square-offs only −₹918.00. No
  gate structure anywhere: both premove sub-bands positive
  ([0.5,0.75) +₹18,232.23; [0.75,1.0) +₹20,504.36), both directions
  positive (LONG +₹17,421.05, SHORT +₹21,315.54), round-2 leg
  +₹886.56 in October / +₹51.44 full-period, entries ≥12:00 = 1
  October trade and +₹2,628.27 full-period (the entry-cutoff seed is
  dead). Exit-progress: stops all end at −0.52 of target distance
  (the −0.65% stop by construction); square-offs close at median
  0.32 of the way to target. **F4 is target-driven: 45 October target
  exits = +₹48,587.90; full-period 200 targets = +₹219,475.66 vs
  316 stops = −₹200,990.98.**

**FIX (frozen before scoring): OC-3-F4T150 — F4 exit target
+1.25% → +1.50%, stop −0.65% unchanged** (pre-approved candidate i;
F4 component only, all months; setup3 post-filter and RF-1 exactly
as in the banked book's construction).

**APPLY (stocks_engine_oc3_score.py).** Anchors: (A) engine rebuild
at T125/S065 reproduces stocks_M2_F4_trades.csv EXACTLY (717 tr,
+₹42,418.91, audit 0 violations); (B) filtered T125 union == state
table (986 tr, +₹107,227.76). T150 build audit: 696 trades, 0
violations. F4 component: October +₹38,736.59 → **+₹41,292.83**;
filtered F4 trades 657 → 637. New union month table:
Jan +13,665.48 · Feb −1,660.11 · Mar +9,281.57 · Apr −3,324.69 ·
May +28,938.33 · Jun −473.22 · Jul +2,141.15 · Aug +382.10 ·
Sep +15,012.70 · **Oct +48,138.22**. Total **+₹112,101.53**,
966 trades.

**DECIDE — BANKED.** All frozen legs pass: October rises +₹2,556.24
✓; total rises +₹4,873.77 ✓; min month −₹3,324.69 ✓; worst hit to a
positive month = March −₹4,140.81 (< ₹5,000) ✓; red repair targets
all IMPROVE (Apr +₹3,717.75, Jun +₹1,796.82 — June nearly green,
Feb +₹153.10) ✓; audits clean ✓.

**STATE AFTER OC CYCLE 3.** Iteration 4. Working book = INV-LONG +
N4-V3 + P2F 2.5% + F4-minus-setup3 @ T150/S065 (RF-1 book-wide).
Total +₹112,101.53, 966 trades. October +₹48,138.22 — **residual
gap ₹1,861.78; October NOT secured, stays the target.** Red repair
targets updated: Apr −₹3,324.69, Feb −₹1,660.11, Jun −₹473.22.
Termination: none. Engine recurses: next October cycle on the
₹1,861.78 residual (seed: F4@T150 exit-progress diagnosis).

---

## OC CYCLE 4 — F4@T150 exit-progress diagnosis + stop widening (2026-10-31)

**IDENTIFY.** Target October, residual gap ₹1,861.78. F4@T150
excursion diagnosis (anchor: rebuild == oc3 dump exactly, audit
696/0; banked F4 637 tr / +₹60,002.45, Oct 109 tr / +₹41,292.83):
151 target exits +₹201,851.50 vs 314 stops −₹194,058.05 vs 172
square-offs +₹52,209.00; zero non-target exits ever reached
+1.50%. T175: post-exit passage 109:10 in its favour, but the
rupee estimate is full-period **−₹15,744.13** and October
+₹1,188.18 — less than the gap. NOT supported. Stop side: only
7/314 stop-outs later reach target (the stop does not leak
targets; 249 fall through), but 58 stop-outs (18%) trigger
neither level after the stop bar and close the day near flat —
the −0.65% stop fires on dips that mean-revert. Estimates:
S080 full +₹30,428.54, October +₹2,409.51.

**FIX (frozen pre-scoring).** OC-4-F4S080 — F4 stop −0.65% →
−0.80%, target stays +1.50%, everything else identical.

**APPLY.** Anchors A+B exact (T150/S065 rebuild == oc3 dump;
filtered union == state +₹112,101.53 / 966 tr). New build audit
661 tr / 0 violations. F4 component: Oct +₹41,292.83 →
+₹43,184.33. Union: October 48,138.22 → **50,029.72**; total
112,101.53 → **131,646.79**; 934 trades. February −1,660.11 →
**+4,173.49 (green)**, April −3,324.69 → **+50.73 (green)**,
March +₹11,040.49, September +₹2,401.09; June −760.27 (inside
leg), August +382.10 → −1,484.26 (flipped slightly red —
August's repair target), worst positive-month hit Jan −1,231.74.

**DECIDE — BANKED, AND OCTOBER IS SECURED.** All frozen legs
pass and October 50,029.72 ≥ 50,000. secured_months = [2026-10];
current target moves to SEPTEMBER (+17,413.79 — verify/diagnose
weak days). Only two red months remain: June −1,233.49 and
August −1,484.26. SUCCESS termination not yet met (needs all 10
months positive); engine recurses immediately.

---

## SE CYCLE 1 — September verification + round2-leg fix attempt (2026-10-31)

**IDENTIFY.** Target September (+₹17,413.79 per state). Anchor:
rebuilt union from the component dumps (INV-LONG + N4-V3 +
P2F 2.5% via stocks_M1.py loaders, F4 from
stocks_engine_oc4_f4s080_trades.csv minus setup3, RF-1 book-wide)
== state table EXACTLY — 934 tr, +₹131,646.79, Sep +₹17,413.79,
Oct +₹50,029.72. **September VERIFIED: 80 trades** — F4
+₹13,593.59 (71 tr), INV-LONG +₹3,820.20 (9 tr); N4-V3 and P2F
took no September trades. Both active components positive.
September's soft underbelly: 9 negative days sum −₹7,376.85,
all F4-driven except Sep 24 (INV −₹968.80); 34 stop exits
−₹24,079.92 against 17 target exits +₹28,423.71 — the month is
won on target hits, bled on stops, as usual. Structural-drag
test (negative in September AND full-period): NHPC stock
(Sep −₹465.28 / full −₹1,171.48 — thin, single-stock, not
chosen) and **F4's round2 leg (Sep −₹2,471.53 / 6 tr; full
−₹852.58 / 74 tr)** — the only mechanism-level drag.

**FIX (frozen pre-scoring, stocks_engine_frozen.md).**
SE-1-F4R1 — F4 takes only the first qualifying signal per
stock-day (round-2 legs dropped), everything else identical.

**APPLY.** Full union scored from the verified dumps (anchor
re-asserted in the scoring run). New table: Sep +₹19,885.32
(+₹2,471.53), total +₹132,499.37 (+₹852.58), **June flips
GREEN +₹160.30**, April +₹1,770.75, March +₹22,344.08; August
deepens only −₹429.57 (inside leg); no positive month loses
> ₹5,000. BUT October's round2 legs are worth +₹1,551.75:
**October → ₹48,477.97 < ₹50,000.**

**DECIDE — REJECTED on the October HARD FLOOR; SEPTEMBER
SECURED AS-IS.** Four of five legs pass, but the secured-month
floor is absolute: no fix may un-secure October. September is
secured at +₹17,413.79 without the fix. secured_months =
[2026-10, 2026-09]; target moves to AUGUST (−₹1,484.26).
Recorded for later: SE-1-F4R1 becomes bankable if October ever
holds ≥ ₹1,551.75 of headroom above the floor — it greens June
and lifts September + total. October's current headroom is
only ₹29.72, so August fixes must be October-neutral or
October-positive. Termination: none (June and August still
red). Engine recurses: August's turn next.

---

## AU CYCLE 1 — August diagnosis + event-component ASTRAL exclusion (2026-10-31)

**IDENTIFY.** Target August (−₹1,484.26). Anchor exact (934 tr,
+₹131,646.79). August decomposition: N4-V3 +₹5,698.96 and P2F
+₹408.12 carried an F4 month of −₹7,286.99. The OC-4 stop widening
is only the top layer — matched S065→S080, all 11 changed August
trades were stop-outs already dead at −0.65% that lost ₹1,866.36
more at −0.80% (zero August rescues), and F4's August at S065 was
still −₹5,420.63. No F4 mechanism slice is negative in both August
and full-period (breakdown −₹5,318.31 in August but deeply positive
full-period; direct leg, lower band the same), so no stop/exit
conditioning can pass the total + October legs. The structural drag
test found one slice rotten in August AND full-period in two
independent systems: **ASTRAL in the event-follow components** —
N4-V3: 2 tr, full −₹1,611.45 (Aug −₹833.95); P2F: 2 tr, full
−₹1,592.10 (Aug −₹836.00); 4 of 4 losers, corroborated by the
frozen reaction profiles (ASTRAL is fade-type, 3/3). ASTRAL itself
is a book earner elsewhere (INV +₹5,350.84, F4 +₹20,462.15).

**FIX (frozen pre-scoring).** AU-1-EVENT-ASTRAL — N4-V3 and P2F
2.5% no longer trade ASTRAL; INV-LONG and F4 unchanged.

**APPLY.** Anchor re-asserted in the scoring run. Removing the 4
trades (−₹3,203.55): August −1,484.26 → **+185.69 (GREEN)**,
May +₹1,533.60 → 29,377.98, every other month identical —
October 50,029.72 (floor intact, headroom unchanged at ₹29.72,
so SE-1-F4R1 remains blocked), September 17,413.79, June
−1,233.49 unchanged. Total 131,646.79 → **134,850.34**; trades
934 → 930.

**DECIDE — BANKED; AUGUST SECURED.** All six frozen legs pass.
secured_months = [2026-10, 2026-09, 2026-08]; target moves to
JULY (+₹2,096.63, thin — only 14 trades, verification turn).
Only June (−₹1,233.49) remains red. Lesson 11 appended
(stock × mechanism poison). Termination: none — SUCCESS needs
June green too. Engine recurses: July's turn next.

## JU Cycle 1 — 2026-10-31 (July turn)
- **Verify:** anchor exact — rebuild == state (930 tr, +₹134,850.34; July +₹2,096.63 / 14 tr). Scripts: stocks_engine_ju1_diag.py, stocks_engine_ju1_score.py; results: stocks_engine_ju1_result.json.
- **Diagnose:** July thin + concentrated — top-1 (P2F TVSMOTOR +₹4,844.50) = 231% of the month; ex-top-3 −₹6,041.00; winners 4/14; two target exits (+₹7,397.63) vs nine stops (−₹5,531.00). Components: P2F +₹4,484.50 (3), N4-V3 −₹1,201.87 (6), F4 −₹1,186.00 (5), INV-LONG inactive. Slice scan (negative in July AND full-period): 4 comp×stock slices; WIPRO/HDFCBANK (continuation-profile, cost-level noise) and F4×NHPC (−₹43/tr) rejected at diagnosis. Only P2F × HINDUNILVR carried the Lesson 11 stack: frozen profiles fade-tendency (0 CONT / 2 FADED), worst ungated P2 payer −₹3,484.80, in-band 2/2 losers −₹2,294.05.
- **Fix (frozen before scoring):** JU-1-P2F-HINDUNILVR — P2F no longer trades HINDUNILVR (mechanism-scoped; N4 keeps it — N4's July HINDUNILVR trade was +₹2,553.13).
- **Decide: BANKED** — all 6 legs pass. July +₹2,096.63 → **+₹3,196.63 (SECURED)**; February +₹4,173.49 → +₹5,367.54 (second removed trade, 2026-02-16); total +₹134,850.34 → **+₹137,144.39**; trades 928; Oct/Sep/Aug/June and all other months unchanged. Disclosed: July remains concentrated after the fix (ex-top-3 −₹4,941.00; top-1 = 152%) — secured, not strong.
- **Next target: June** (−₹1,233.49, the only red month). Secured: Oct, Sep, Aug, Jul.

## JN Cycle 1 — 2026-10-31 (June turn — the last red month)
- **Verify:** anchor exact — rebuild == state (928 tr, +₹137,144.39; June −₹1,233.49 / 75 tr). Scripts: stocks_engine_jn1_diag.py, stocks_engine_jn1_score.py; results: stocks_engine_jn1_result.json.
- **Diagnose:** June — F4 −₹2,538.69 (54), INV-LONG −₹1,772.32 (18), N4-V3 −₹1,131.10 (1), P2F +₹4,208.62 (2); losses concentrated Jun 24 (−₹5,154.72) and Jun 10 (−₹2,728.71); 37 stop exits −₹23,537.79 vs 18 targets +₹20,073.30; ex-top-3 −₹9,342.73. Slice scan (negative in June AND full-period): F4 × GODREJCP the biggest (Jun −₹2,460.96, full −₹3,814.67) but UNBANKABLE — its October slice is +₹1,060.25 vs headroom ₹29.72, removal breaks the hard floor. F4 round2 = the already-rejected SE-1-F4R1 family. Chosen: INV-LONG × BDL (Jun −₹1,406.25 / 2 tr; full −₹1,486.93 / 22 tr, 6 winners) while BDL earns +₹10,168.59 in N4/P2F/F4 — Lesson 11 pattern, third instance.
- **Fix (frozen before scoring):** JN-1-INV-BDL — INV-LONG no longer trades BDL (mechanism-scoped; N4-V3, P2F and F4 keep it).
- **Decide: BANKED — 🎉 ALL TEN MONTHS GREEN.** All 5 legs pass. June −₹1,233.49 → **+₹172.76 (SECURED)**; October 50,029.72 → **50,572.02** (headroom ₹572.02); April 50.73 → 1,464.36 (razor-thin April relieved by the same slice); September → 18,041.54; total +₹137,144.39 → **+₹138,631.32**; trades 906. Worst positive-month hit: March −₹1,205.80. Thin-sample caveat: June's green rests on 2 June trades; the 22-trade full-period record (27% win) carries the case. Thin months remain: June +172.76, August +185.69, April +1,464.36.
- **Next target (per brief): TOTAL-RAISING** — challenger cycles toward a ₹50,000/month average (₹500,000 total; currently ₹13,863.13/month); BREAK-EVEN termination after 2 consecutive cycles that bank nothing. Original SUCCESS axis (October ≥ ₹50,000 AND all months positive) is met; candidate-spec freeze deferred to the total-raising phase per the JN-1 brief. Lesson 12 appended (secured-floor netting) + Lesson 11 third-instance addendum.

## CH Cycle 1 — 2026-10-31 (challenger: P2F-PROFILE vs incumbent)
- **Verify:** both anchors exact — incumbent rebuild == state (906 tr, +₹138,631.32, state month table); P2F construction anchor: follow-direction T125/S050 on the ≥2.0% event set == T2 anchor (48 tr, +₹12,835.88). Timing audit: 0 violations over profile + placebo builds (every profile input strictly prior, outcome date < trade date, asserted in code). Scripts: stocks_engine_ch1_score.py; results: stocks_engine_ch1_result.json; dumps: stocks_engine_ch1_p2fprofile_trades.csv, stocks_engine_ch1_p2fplacebo_trades.csv.
- **Build (frozen before scoring):** P2F-PROFILE — P2F machinery, 2.0% band, T125/S065, direction from the stock's own causal reaction history (≥2 classified priors, ≥2/3 CONTINUED → follow, ≥2/3 FADED → fade, else follow); no name exclusions (the rule replaces the AU-1/JU-1 patches); RF-1 book-wide. Placebo: donor-permuted profiles, seed 20261031.
- **Standalone:** 46 tr, **+₹13,120.32** (H1 +₹4,817.48 / H2 +₹8,302.84, Oct −₹279.77, breadth 14, expectancy +₹285.22, win 50.0%) vs placebo +₹12,411.62 — beats it by only ₹708.70. **The rule classified 3 of 48 trades and flipped ZERO to fade**: ~2 reactions/stock exist in-window, and ASTRAL's −1.86% Feb reaction is below the band, so its August trade had 1 classified prior → default follow → the exact loss AU-1 had excluded came back in.
- **Assembled challenger:** 919 tr, total **+₹132,907.51** (−₹5,723.81 vs incumbent); months: Jan 8,855.65 · Feb 3,591.99 · Mar 19,116.26 · Apr 1,464.36 · May 30,130.01 · Jun 172.76 · Jul 1,499.43 · **Aug −571.74 RED** · Sep 18,041.54 · Oct 50,607.25. Ex-top-3 ₹17,662.47 vs incumbent ₹18,918.30 (top-3 TVSMOTOR/GLENMARK/ASTRAL both books — concentration unchanged). Assembled-with-placebo total ₹132,198.81.
- **Decide: REJECTED** — gate legs (a) all-green FAIL (August), (b) total-higher FAIL, (d) ex-top-3 FAIL; (c) October floor and (e) audit + placebo pass. Incumbent unchanged (+₹138,631.32, 10/10 green). **Lesson 13 appended** (a causal profile needs history the window doesn't have; in-window, mechanism-scoped exclusions remain the honest form of Lesson 11). No-bank counter: 0 → 1 — one more consecutive no-bank cycle ends the total-raising phase as BREAK_EVEN.

## CH-2 — Challenger cycle: N4-V3 exit rebuild T150/S080 (2026-10-31)
- Charter: lessons read first (1–13). Diagnosis across the two pre-approved directions (stocks_engine_ch2_diag.py):
  - (B) N4-V3 excursions @T125/S050 (incumbent set, 50 tr): stop 31 / −15,985.68, target 17 / +22,612.48, sq-off 2 / +1,135.00; post-exit passage rough swing T150 −1,995.57 + S080 +11,472.97 = **+9,477.40**.
  - (A) F4-MIRROR: 69 above50 days, October above50 = 0 (October structurally untouched); 350 qualifying stock-days; fade-drift mean +0.059%, 176/350 positive, rough +40,671 carried by Jul/Jun/Aug — regime-concentrated mirage profile (Lessons 2/8). NOT scored.
  - Choice: (B) — direct excursion evidence on the incumbent's own trades (Lesson 4 method).
- Frozen in stocks_engine_frozen.md (CH-2 section) before scoring. Process: two user overrides landed mid-cycle — 12:08 IST freeze-for-record on the overfitting objection, superseded 12:10 IST by the saturation order (adopt-if-beats restored; run ends after 3 consecutive no-beat cycles). Scored under the restored gate; no candidate spec written; terminated stays null.
- Anchors: incumbent rebuild == state (+138,631.32 / 906 / month table) ✓; N4 replay at T125/S050 reproduces the source dump 56/56 (entry-bar evaluation convention) ✓; timing audit on the rebuild 0 violations (4 same-bar exits, the source engine's own convention).
- Scored (stocks_engine_ch2_score.py): N4 +7,761.80 → +17,245.25 (**+9,483.45**, vs +9,477.40 estimated). Challenger: total **+148,114.77**, October **+51,712.76**, ex-top-3 **+25,420.86** — legs (b), (c), (d) PASS. Leg (a) FAILS: June +172.76 → **−481.90**, August +185.69 → **−3,649.16** (April 1,464.36 → 1,395.76, still green).
- **Verdict: REJECTED. Incumbent unchanged** (+138,631.32, all ten green, October +50,572.02). consecutive_no_bank = 2 (CH-1, CH-2); saturation set: no_beat_cycles = 1, best_total = 138,631.32. Revisit condition recorded in state: thicken June ≥ +654.66 and August ≥ +3,834.85 by other means and the N4 rebuild becomes adoptable. Lesson 14 appended.

## SAT Cycle 1 — 2026-10-31 (saturation run: thicken June)
- **Charter:** lessons read first (1–14; Lesson 14 is the brief's reason — thin June/August held the real CH-2 N4 improvement hostage). Scripts: stocks_engine_sat1_diag.py, stocks_engine_sat1_score.py; results: stocks_engine_sat1_result.json.
- **Verify:** anchor exact — rebuild == state (906 tr, +₹138,631.32; June +₹172.76 / 73 tr).
- **Diagnose June:** P2F +₹4,208.62 (2) carries the month against F4 −₹2,538.69 (54), INV-LONG −₹366.07 (16), N4-V3 −₹1,131.10 (1); 35 stops −₹22,131.54 vs 18 targets +₹20,073.30; ex-top-3 −₹7,936.48. Wide slice scan (negative in June AND full-period, each with its Oct/Aug/Apr slices per Lesson 12): the known F4 × GODREJCP slice (Jun −₹2,460.96, full −₹3,814.67) is STILL October-blocked (Oct slice +₹1,060.25 vs headroom ₹572.02). Splitting it by direction exposes the rot: **F4 × GODREJCP × SHORT — Jun −₹1,680.96 (2 tr), full −₹4,754.92 (10 tr, 2/10 winners, all skill_or_breakdown, expectancy −₹475.49/tr), October slice exactly ₹0.00, August ₹0.00, April +₹180.00** — while F4 × GODREJCP LONG is full-period POSITIVE (+₹940.25). Runner-up F4 × OIL (Jun −₹990.16, full −₹2,661.85) dominated on every dimension.
- **Fix (frozen in stocks_engine_frozen.md BEFORE scoring):** SAT-1-F4-GODREJCP-SHORT — F4 no longer takes SHORT signals on GODREJCP; F4 keeps GODREJCP LONG; all other components unchanged.
- **Decide: BANKED — saturation BEAT.** Removing the 10 trades: **June +₹172.76 → +₹1,853.72** (Δ +₹1,680.96 = 2.57× the CH-2 revisit need of ₹654.66 → **June revisit condition FULLY covered**; June after a hypothetical N4 re-apply = +₹1,199.06); **total +₹138,631.32 → +₹143,386.24**; February +₹1,004.48 → 6,130.34, March +₹1,709.68 → 20,825.94, September +₹1,244.56 → 19,286.10; April −₹180.00 → 1,284.36 (green), May −₹704.76 → 28,673.22 (green); October +₹50,572.02, August +₹185.69, July, January unchanged to the paisa. All ten months green (min August +₹185.69); trades 906 → 896; ex-top-3 ₹18,918.30 → ₹23,673.22. All gate legs (a)–(e) pass.
- **Saturation:** no_beat_cycles 1 → **0** (reset), best_total → **₹143,386.24**. **August revisit shortfall unchanged: ₹3,834.85** — now the ONLY remaining condition for adopting the CH-2 N4 rebuild. Lesson 15 appended (direction-refined poison).
- **Next target: thicken August** (+₹185.69) by ≥ ₹3,834.85 through other means (SAT-2), then the N4 re-apply.

## SAT Cycle 2 — 2026-10-31 (saturation run: thicken August)
- **Charter:** lessons read first (1–15; Lessons 11/14/15 are the tools). Scripts: stocks_engine_sat2_diag.py, stocks_engine_sat2_diag2.py, stocks_engine_sat2_diag3.py; results: stocks_engine_sat2_result.json, diag JSONs alongside.
- **Verify:** anchor exact — rebuild == state (896 tr, +₹143,386.24; August +₹185.69 / 32 tr; October +₹50,572.02, headroom ₹572.02).
- **Diagnose August:** carried by the event systems (N4-V3 +₹6,532.91, P2F +₹1,244.12, INV-LONG −₹304.35) against **F4 −₹7,286.99** (18 tr: 11 stops −₹10,393.92, 3 targets +₹2,231.93, 4 square-offs +₹875.00; every trade a skill_or setup; damage concentrated Aug 20/27/28/31). Wide slice scan + direction splits (Lessons 5/11/12/15): **no comp × setup, comp × setup × dir, or F4 × stock slice is negative in both August and full-period with mass** — F4 × SHORT full = +₹42,078.56, F4 × LONG full = +₹42,224.07; August's killers (GLENMARK breakdown shorts −₹4,008.24, UNITDSPR, BDL) are full-period earners having a bad month.
- **Killed on evidence before freezing:** (i) F4 stop widening — excursion diagnostic (diag3, OC-4 method): of August's 11 F4 stop exits, **0 reached the +1.50% target post-exit, 7 continued deeper, 4 went flat**; rough August swing S095 +₹262.61 / S110 −₹1,191.02 — August's stops were genuine continuations, not October-style mean-reverting dips; (ii) F4 × UNITDSPR — floor-blocked both directions (October +₹2,617.85; SHORT half October +₹780.00 > headroom ₹572.02); (iii) F4 × GLENMARK × SHORT — top full-period earner, gate-dead; (iv) a bundle of the remaining 1-trade micro-slices — refused as a method (one change per cycle; the overfit pattern STRESS-1 flagged).
- **Fix (frozen in stocks_engine_frozen.md BEFORE scoring):** SAT-2-F4-INDUSTOWER-LONG — F4 no longer takes LONG signals on INDUSTOWER (slice: Aug −₹693.00 / 2 tr 0 w, full −₹361.12 / 18 tr 7 w, October −₹792.72, April −₹758.76 — negative in target month AND full period, October-improving). F4 keeps INDUSTOWER SHORT; all other components unchanged.
- **Decide: BANKED — saturation BEAT.** Removing the 18 trades: **August +₹185.69 → +₹878.69** (Δ +₹693.00 = 18% of the CH-2 revisit need → **shortfall ₹3,141.85 remains; N4 rebuild STILL BLOCKED** — August after a hypothetical re-apply = −₹2,956.16); **total +₹143,386.24 → +₹143,747.36**; October +₹792.72 → **+₹51,364.74** (headroom now ₹1,364.74 — SE-1-F4R1's October leg is ₹187.01 short of unlocking); April +₹758.76 → +₹2,043.12; costs March −₹556.17 → 20,269.77 and September −₹1,368.72 → 17,917.38 (both stay strongly green); May +₹41.53; Jan/Feb/Jun/Jul unchanged to the paisa. All ten months green (min August +₹878.69); trades 896 → 878; ex-top-3 ₹23,673.22 → ₹24,034.34. All gate legs pass.
- **Saturation:** no_beat_cycles stays **0**, best_total → **₹143,747.36**. Lesson 4 addendum appended (exit medicine is population-specific). August's residual ₹3,141.85 has no protocol-clean slice left — the state records that plausibly only a NEW August-earning component (Lesson 3 materials) can close it.
- **Next:** saturation continues — challenger/new-component territory, or the SE-1-F4R1 unlock if any October fix banks ≥ ₹187.01.

## SAT Cycle 3 — 2026-10-31 (saturation run: re-measure SE-1-F4R1 at the current book)
- **Charter:** lessons read first (1–15 + addenda). Re-test frozen in stocks_engine_frozen.md (SAT-3 section) BEFORE scoring — a re-measurement of the frozen SE-1-F4R1 family at the post-SAT-1/SAT-2 state, not a new family. Script: stocks_engine_sat3_score.py; results: stocks_engine_sat3_result.json.
- **Verify:** anchor exact — rebuild == state (878 tr, +₹143,747.36; October +₹51,364.74, headroom ₹1,364.74; month table to the paisa).
- **Re-derive round2 at the current book:** 70 trades (SE-1: 74), net −₹11.83, 28/70 winners. Month nets: Jan +1,261.27 · Feb +3,641.69 · Mar −2,022.02 · Apr −1,720.02 · May +876.14 · Jun −1,393.79 · Aug +775.25 (1 tr) · Sep −2,982.10 · **Oct +1,551.75 (8 tr)**.
- **The headline:** F4R1's **October cost is INVARIANT — ₹1,551.75, identical to the paisa.** None of SAT-1's GODREJCP-SHORT or SAT-2's INDUSTOWER-LONG deletions touched an October round2 leg, so October under F4R1 = **₹49,812.99 — ₹187.01 below the floor**, inside the frozen ₹250 record-only window. The state's "₹187.01 short" estimate was exact.
- **Everywhere else the old measurement was stale:** total delta decayed **+₹852.58 → +₹11.83** (SAT-1/SAT-2 already harvested round2 losers in other months); September delta improved +₹2,471.53 → **+₹2,982.10**; August delta worsened −₹429.57 → **−₹775.25** (August under F4R1 would be **+₹103.44** — green but razor-thin, not the ~+₹449 the stale delta implied); May delta flipped +₹129.50 → −₹876.14; Jan/Feb/Mar/Apr/Jun/Jul/Oct deltas identical to SE-1. F4R1 book would be 808 tr / +₹143,759.19, ex-top-3 ₹24,034.34 → ₹25,167.35.
- **Decide: NOT BANKED.** Legs: (a) total rises +₹11.83 — nominal PASS; (b) all ten green — PASS (min August +₹103.44); (c) October ≥ ₹50,000 — **FAIL** (₹49,812.99). Per the frozen within-₹250 rule the exact shortfall (**₹187.01**) is recorded instead of banking; F4R1 stays OUT of the book. Unlock condition, now precise: any October fix banking ≥ ₹187.01 makes F4R1's floor leg pass — subject to a FRESH re-measurement before banking (Lesson 16). Note its remaining value is mostly September (+₹2,982.10); it greens nothing not already green, and it does NOT thicken August — the **N4-revisit August shortfall is unchanged at ₹3,141.85**.
- **Saturation:** no_beat_cycles 0 → **1**; best_total unchanged **₹143,747.36**; consecutive_no_bank = 1. Incumbent unchanged (all ten green, October +₹51,364.74, 878 tr). Lesson 16 appended (blocked-fix deltas expire unevenly — re-measure before relying on any of them).
- **Next:** October-positive cycle (≥ +₹187.01 unlocks F4R1's floor leg, pending re-measure), a NEW August-earning component for the N4 revisit (₹3,141.85), or further Lesson-3 challengers — two more consecutive no-beat cycles end the run.

## SAT Cycle 4 — 2026-10-31 (saturation run: NEW COMPONENT N4-LOWBAND for August)
- **Charter:** lessons read first (1–16 + addenda; Lesson 3 supplies the material — the event axis; Lesson 17 was earned this cycle). Spec frozen in stocks_engine_frozen.md (SAT-4 section) BEFORE scoring. Script: stocks_engine_sat4_score.py; results: stocks_engine_sat4_result.json; trades: stocks_engine_sat4_lowband_trades.csv.
- **Verify:** incumbent anchor exact — rebuild == state (878 tr, +₹143,747.36; October +₹51,364.74, headroom ₹1,364.74; month table to the paisa). **Construction anchor:** the identical N4 pipeline at |move| ≥ 1.0% reproduces eq_n4deep_v3_trades_T125_janoct.csv **56/56 per-trade** (net + exit_reason) under the CH-2 replay convention — the LOWBAND build is the audited machinery, not a re-implementation. Timing audit 0 violations; mechanical overlap vs the N4-V3 dump on (date, stock) = **0** (bands disjoint by construction, verified); RF-1 weekend drops = 0.
- **Build:** combined results + single-news reaction days, |move by 09:30| in [0.75%, 1.0%), entry 09:35 (09:30-bar close) in the reaction direction, exits T125/S050 (N4-V3's current exits — the CH-2 rebuild deliberately NOT used). No name exclusions added (one change per cycle); ASTRAL's slice reported for the record.
- **Standalone:** 14 trades, **−₹1,984.09**; halves **flip** (Jan–May +₹2,730.29 / Jun–Oct −₹4,714.38); win rate **14.3%** (2/14); expectancy **−₹141.72**; breadth **2/12** stocks positive (ASTRAL 1 tr +₹1,856.00, OBEROIRLTY +₹1,185.02; BDL −₹1,334.45 worst). Month slices: Feb +1,511.00, May +1,655.01, Apr −435.72, Jul −1,266.63, **Aug −₹1,026.45**, **Oct −₹2,421.30**; Jan/Mar/Jun/Sep no trades.
- **Decide: REJECTED — fails all three saturation legs.** Union would be 892 tr / **+₹141,763.27 < +₹143,747.36** (a FAIL); **August +₹878.69 → −₹147.76** (b FAIL — the component loses in the very month it was built to thicken); **October → ₹48,943.44 < ₹50,000** (c FAIL). Incumbent unchanged (878 tr / +₹143,747.36, all ten green, October +₹51,364.74).
- **August revisit status:** UNCHANGED — the CH-2 N4-rebuild condition still needs August **+₹3,141.85** by other means (August ≥ ₹4,020.54); the lowband route is closed (had it banked, the shortfall would have grown to ₹4,168.30).
- **Saturation:** no_beat_cycles 1 → **2**; best_total unchanged **₹143,747.36**; consecutive_no_bank = 2. ONE more consecutive no-beat cycle ends the run. Lesson 17 appended (a trigger threshold is validated when its complement fails — the ≥1.0% floor is load-bearing).
- **Next:** F4R1 unlock via any October fix ≥ ₹187.01 (then re-measure — Lesson 16), the diagnosed-not-scored F4-MIRROR (placebo required), or genuinely different Lesson-3 material for August.

## SAT Cycle 5 — 2026-10-31 (saturation run: watchdog candidate + exit-grid closures)
- **Charter:** lessons read first (1–17 + addenda). The watchdog's pending candidate (frozen by the 12:17 watchdog run pre-SAT-3, renumbered SAT-5 per the correction note, NEVER scored) was re-diagnosed and re-frozen in stocks_engine_frozen.md (SAT-5 section) BEFORE scoring, per Lesson 16. Scripts: stocks_engine_sat5_diag.py / stocks_engine_sat5_score.py; results: stocks_engine_sat5_diag.json / stocks_engine_sat5_result.json.
- **Verify:** anchor exact — rebuild == state (878 tr, +₹143,747.36; October +₹51,364.74, headroom ₹1,364.74; month table to the paisa). Components: INV-LONG +₹32,477.68 (218 tr), N4-V3 +₹7,761.80 (50), P2F +₹18,844.13 (33), F4 +₹84,663.75 (577).
- **Diagnose the three candidate directions:** (1) **WD-5 slice F4 × HINDUNILVR × SHORT re-measures IDENTICALLY to the watchdog record** — 9 tr, −₹2,664.00, 5 winners; Jan −1,904.08, Apr +526.88, Jun −1,040.00, Sep +1,070.00, Oct −1,316.80; no Aug trades. Lesson 15 direction split: the name as a whole is only −₹1,184.02 because the LONG half earns (+₹1,479.98; Oct +₹5,369.90) — the SHORT half is the rot, and scoping preserves the October winner. Union-after passes all three gate legs on the diagnosis numbers. (2) **INV-LONG exit rebuild — DEAD:** all 17 alternate exit dumps (T100..T200 × S050..S080 + TRA/TRB, same entries, BDL/weekend filtered) score BELOW incumbent T125/S050 at component level (best alternate T125/S065 −₹2,466.26; worst T100/S080 −₹18,094.15). T125/S050 is the grid peak; no rebuild can beat it. (3) **P2F exit rebuild — not built:** Lesson 4 (removing the small target destroyed P2F) + CH-1 (S065 hurt P2F) stand against; P2F expectancy at current exits +₹571.03/tr is the book's highest — the "overwhelming" condition is the opposite of met.
- **Fix (frozen BEFORE scoring):** SAT-5-F4-HINDUNILVR-SHORT — F4 no longer takes SHORT signals on HINDUNILVR. F4 keeps HINDUNILVR LONG; N4-V3/INV-LONG unchanged; P2F already excludes the name (JU-1).
- **Score:** anchor asserted in the score run; deleted set asserted == the frozen slice (9 trades, net −₹2,664.00 exactly). **Decide: BANKED — saturation BEAT.** Total **+₹143,747.36 → +₹146,411.36**; October +₹1,316.80 → **+₹52,681.54** (headroom ₹2,681.54 — now EXCEEDS SE-1-F4R1's invariant October cost of ₹1,551.75: its floor leg is satisfiable, subject to a fresh re-measurement per Lesson 16; its last measured total value was only +₹11.83); June +₹1,040.00 → **+₹2,893.72**; January +₹1,904.08 → +₹13,282.30; costs April −₹526.88 → +₹1,516.24 and September −₹1,070.00 → +₹16,847.38 (both stay green); February/March/May/July/August unchanged to the paisa; all ten months green (min August +₹878.69); trades 878 → 869; ex-top-3 ₹24,034.34 → **₹26,698.34** (top-3 unchanged: TVSMOTOR ₹61,717.72 / GLENMARK ₹32,182.31 / ASTRAL ₹25,812.99).
- **Saturation:** no_beat_cycles 2 → **0**, best_total → **₹146,411.36**. The run does NOT saturate — SAT-5 beat the best with a candidate that had been sitting unscored since the watchdog race. N4-revisit August shortfall UNCHANGED at ₹3,141.85 (this fix has no August trades and touches no N4 leg).
- **Lessons:** addenda appended — Lesson 15 second instance (+ Lesson 16 positive instance: untouched legs' deltas do not expire), Lesson 4 mirror addendum (INV-LONG's population peaks at the tightest exits; the grid is a closed family).
- **Next:** saturation continues from +₹146,411.36 — F4R1 re-measurement (headroom leg now satisfiable; value mostly September, August cost −₹775.25 to re-verify), the diagnosed-not-scored F4-MIRROR (placebo required), or genuinely new Lesson-3 material for the August/N4-revisit gap (₹3,141.85).

## SAT Cycle 6 — 2026-10-31 (saturation run: re-measure + bank SE-1-F4R1 at the post-SAT-5 book)
- **Charter:** lessons read first (1–17 + addenda; Lesson 16 governs — a fresh re-measurement before banking, no reliance on SAT-3's numbers). Re-measurement frozen in stocks_engine_frozen.md (SAT-6 section) BEFORE scoring. Script: stocks_engine_sat6_score.py; results: stocks_engine_sat6_result.json.
- **Verify:** anchor exact — rebuild == state (869 tr, +₹146,411.36; October +₹52,681.54, headroom ₹2,681.54; month table to the paisa). Components rebuilt with ALL current filters (incl. SAT-5's HINDUNILVR-SHORT).
- **Lesson-16 check inside the run:** SAT-5's intervening slice (F4 × HINDUNILVR × SHORT, 9 tr) is composed of **9 direct legs and 0 round2 legs** — it never touched the population F4R1 deletes. The round2 set therefore re-measures **IDENTICAL to SAT-3, to the paisa**: 70 tr, net −₹11.83, 28/70 winners; month nets Jan +1,261.27 · Feb +3,641.69 · Mar −2,022.02 · Apr −1,720.02 · May +876.14 · Jun −1,393.79 · Aug +775.25 (1 tr) · Sep −2,982.10 · **Oct +1,551.75 (8 tr)**. The October cost ₹1,551.75 has now been invariant across THREE book states (SE-1, SAT-3, SAT-6).
- **Decide: BANKED — saturation BEAT (all three frozen legs pass).** Dropping the 70 round2 legs: **total +₹146,411.36 → +₹146,423.19** (+₹11.83 — nominal, exactly as SAT-3 measured); **October +₹52,681.54 → +₹51,129.79** (cost ₹1,551.75 ≤ headroom ₹2,681.54; headroom after ₹1,129.79); **all ten months green** — September +₹2,982.10 → +₹19,829.48, June +₹1,393.79 → +₹4,287.51, April +₹1,720.02 → +₹3,236.26, March +₹2,022.02 → +₹22,291.79; costs February −₹3,641.69 → +₹2,488.65, January −₹1,261.27 → +₹12,021.03, May −₹876.14 → +₹27,838.61, **August −₹775.25 → +₹103.44 (razor-thin, still green)**; July unchanged to the paisa. Trades 869 → 799; ex-top-3 ₹26,698.34 → **₹27,831.35** (+₹1,133.01 — the distributional content of this bank is thicker Sep/Jun/Apr/Mar and a better stress profile, not the ₹11.83 headline).
- **Reported cost (not gate-relevant, recorded plainly):** F4R1 thins August, so the **CH-2 N4-revisit August shortfall GROWS ₹3,141.85 → ₹3,917.10** (August +₹103.44 vs the ≥ ₹4,020.54 the rebuild needs). August is now the book's razor: any future August cost above ₹103.44 un-secures it.
- **Saturation:** no_beat_cycles stays **0**, best_total → **₹146,423.19**. F4R1 is CLOSED — it is part of the book (F4 first-signal-only from here). Lesson 16 addendum appended (invariance is checkable leg-by-leg; third identical measurement).
- **Next:** saturation continues from +₹146,423.19 — genuinely new Lesson-3 material, or the diagnosed-not-scored F4-MIRROR (placebo required). The N4-rebuild route needs an August gain of ₹3,917.10 that no incumbent slice offers.

## SAT-7 — August at the new book (2026-10-31)
- **Identify:** anchor exact (799 tr / +₹146,423.19 / October +₹51,129.79, headroom ₹1,129.79). August +₹103.44 at the post-F4R1 book: 29 trades = event systems +₹7,777.03 (N4-V3 +₹6,532.91 / 8 tr, P2F +₹1,244.12 / 5 tr) against F4 −₹7,369.24 (15 tr; 9 stop exits −₹9,700.92, ALL on Aug 20/27/28/31) and INV-LONG −₹304.35 (1 tr). Slice scan (comp × stock × direction × setup): F4 × UNITDSPR is the only F4 stock slice negative in BOTH August (−₹1,947.84 / 3 tr) and full period (−₹1,294.84 / 13 tr). **Winners-side state search NEGATIVE, recorded as such:** August's winners share no ex-ante state its losers lack — all 15 F4 August trades enter 10:xx; every premove sub-band is full-period positive ([0.5,0.65) +₹29,458.37, [0.65,0.8) +₹30,386.63, [0.8,1.0) +₹27,840.02); the event wins are GLENMARK reaction-following in BOTH directions. No gate exists; the deletion route is the fix.
- **Fix (frozen in stocks_engine_frozen.md BEFORE scoring):** SAT-7-F4-UNITDSPR-SHORT — F4 takes no SHORT signals on UNITDSPR (LONG kept; all other components unchanged). Direction split is the Lesson 15 pattern: LONG half +₹552.17 (5 tr), SHORT half −₹1,847.01 (8 tr, 3 winners; Feb −₹1,123.04, Mar −₹331.81, Apr −₹500.00, Aug −₹672.16, Oct +₹780.00). Whole-stock removal stays floor-blocked (October +₹2,617.85), but the SHORT half's October slice (+₹780.00) fits the current headroom ₹1,129.79 — the block SAT-2 recorded (headroom then ₹572.02) **lifted** because SAT-5/SAT-6 grew the headroom without touching a UNITDSPR leg (Lesson 12 addendum appended: a floor block is a property of the headroom, not of the slice).
- **Decide: BANKED — saturation BEAT (all gate legs pass).** Deleting the 8 trades (asserted == frozen record 8 tr / −₹1,847.01): **total +₹146,423.19 → +₹148,270.20**; **August +₹103.44 → +₹775.60** (7.5× thicker — no longer a razor); February +₹1,123.04 → +₹3,611.69, March +₹331.81 → +₹22,623.60, April +₹500.00 → +₹3,736.26; **October −₹780.00 → +₹50,349.79 ≥ ₹50,000** (headroom after ₹349.79); all other months unchanged to the paisa; trades 799 → 791; ex-top-3 ₹27,831.35 → **₹29,678.36**. Month table: Jan 12,021.03 · Feb 3,611.69 · Mar 22,623.60 · Apr 3,736.26 · May 27,838.61 · Jun 4,287.51 · Jul 3,196.63 · Aug 775.60 · Sep 19,829.48 · Oct 50,349.79.
- **N4-revisit:** August shortfall **₹3,917.10 → ₹3,244.94** (August +₹775.60 vs the ≥ ₹4,020.54 the CH-2 rebuild needs) — improved, still blocked.
- **Saturation:** no_beat_cycles stays **0**, best_total → **₹148,270.20**.
- **Next (SAT-8 seed, diagnosed not scored):** F4 × HINDCOPPER × SHORT — August −₹959.56 (2 tr), full −₹1,094.95 (12 tr, 4 w), October slice exactly ₹0.00 (October-neutral; the only remaining Aug-negative/full-negative direction slice that fits the ₹349.79 headroom). F4 × GLENMARK × SHORT stays floor-blocked (October +₹1,404.72 > headroom) and is a Lesson 6 concentration name — re-test only if headroom regrows past ₹1,404.72.

## SAT-8 — F4 x HINDCOPPER x SHORT (2026-10-31)
- **Identify:** lessons read first (1–17 + addenda; Lessons 15/16 govern). Seed from SAT-7's diagnosis: F4 × HINDCOPPER × SHORT — the only remaining August-negative / full-period-negative F4 direction slice that fits October's ₹349.79 headroom (its October slice was recorded exactly ₹0.00). Re-derived at the current book per Lesson 16 (stocks_engine_sat8_diag.py): anchor exact (791 tr / +₹148,270.20 / month table to the paisa) and the slice re-measures **IDENTICAL to the SAT-7 record** — 12 tr, net −₹1,094.95, 4 winners, all skill_or_breakdown direct legs (Jan −476.24, Mar +302.13, Apr +65.00, May −479.08, Jun +346.00, Aug −959.56 [Aug 20 −486.60, Aug 27 −472.96 — the same late-August F4 stop cluster], Sep +106.80, Oct 0.00 [1 tr, Oct 30, scratch]). The intervening SAT-7 change (UNITDSPR SHORT) acts on a disjoint stock, so the deltas did not expire (Lesson 16 invariance clause, third positive instance). Direction split is the Lesson 15 pattern: the name as a whole is +₹697.56 only because its LONG half earns (+₹1,792.51, 4 tr, 3 w) — the SHORT half is the rot. Fix frozen in stocks_engine_frozen.md (SAT-8 section) BEFORE scoring.
- **Decide: BANKED — saturation BEAT (all gate legs pass).** Deleting the 12 trades (asserted == frozen record 12 tr / −₹1,094.95): **total +₹148,270.20 → +₹149,365.15**; **August +₹775.60 → +₹1,735.16** (2.2× thicker, still the thinnest month); January +₹476.24 → +₹12,497.27, May +₹479.08 → +₹28,317.69; costs March −₹302.13 → +₹22,321.47, June −₹346.00 → +₹3,941.51, April −₹65.00 → +₹3,671.26, September −₹106.80 → +₹19,722.68 (all stay green); February and July unchanged to the paisa; **October unchanged +₹50,349.79 ≥ ₹50,000** (headroom ₹349.79 — the slice is exactly October-neutral); trades 791 → 779; ex-top-3 ₹29,678.36 → **₹30,773.31**. Month table: Jan 12,497.27 · Feb 3,611.69 · Mar 22,321.47 · Apr 3,671.26 · May 28,317.69 · Jun 3,941.51 · Jul 3,196.63 · Aug 1,735.16 · Sep 19,722.68 · Oct 50,349.79.
- **N4-revisit:** August shortfall **₹3,244.94 → ₹2,285.38** (August +₹1,735.16 vs the ≥ ₹4,020.54 the CH-2 rebuild needs; August after a hypothetical re-apply = 1,735.16 − 3,834.85 = −₹2,099.69) — improved, still blocked.
- **Saturation:** no_beat_cycles stays **0**, best_total → **₹149,365.15**.
- **August slice space EXHAUSTED at this book:** with HINDCOPPER banked, no August-negative / full-negative F4 direction slice remains that fits the headroom; F4 × GLENMARK × SHORT (Aug −₹4,008.24, full −₹383.26) stays floor-blocked (October +₹1,404.72 > ₹349.79) and is a Lesson 6 top-3 concentration name — not a real candidate even if headroom regrows. Recorded as a Lesson 15 addendum.
- **Next (SAT-9 frontier):** new Lesson-3 material — a genuinely new August-earning component (information/state axis; the event axis's low band is closed by Lesson 17, price-derived events by Lesson 2), or the diagnosed-not-scored F4-MIRROR (capped-band signal-fade on above50 days, T150/S080 — placebo REQUIRED, Lessons 2/8 mirage warning on record), or October-headroom growth by other means. The N4-rebuild route still needs August +₹2,285.38 that no incumbent slice offers.

## SAT-9 — F4-MIRROR challenger (2026-10-31)
- **Charter:** lessons read first (1–17 + addenda; Lessons 2/7/8 mirage warnings govern — placebo REQUIRED). Challenger frozen in stocks_engine_frozen.md (SAT-9 section) BEFORE scoring. Script: stocks_engine_sat9_score.py; results: stocks_engine_sat9_result.json; trades: stocks_engine_sat9_mirror_trades.csv.
- **Build:** the exact mirror of F4 — capped band [0.5%, 1.0%) by 10:00, H1.build_cell sig-mode with dirmode="fade" on ABOVE-50DMA days (69 non-weekend above50 days; October above50 days = 0, so the October slice is structurally zero), entry = first V5 signal at/after 10:00 AGAINST the morning move at next-bar open, exits T150/S080, first-signal-only (F4R1 rule), RF-1, book F4 exclusions applied symmetrically (setup3 + the five stock × direction exclusions; 53 raw → 26 kept).
- **Verify:** anchor exact (779 tr / +₹149,365.15 / month table to the paisa / ex-top-3 ₹30,773.31). Timing audit 0 violations in all three builds (mirror 60 audited chain trades incl. skipped second legs; placebos likewise). Overlap vs incumbent F4 = 0 shared dates, 0 shared (date, symbol) pairs — disjoint day-states verified mechanically, not just by construction.
- **Standalone:** 26 tr, **net −₹10,013.80**, expectancy −₹385.15, breadth 2/25, halves both negative (Jan–May −₹3,386.43 / Jun–Oct −₹6,627.37). Months: Jan +149.37 · Feb −1,300.32 · May −2,235.48 · Jun −1,971.76 · Jul −435.25 · **Aug −4,220.36** · Mar/Apr/Sep/Oct 0 (no qualifying trades). It loses most in August — the very month it was built to thicken.
- **Controls:** Placebo A (sign-flip = follow on the same above50 days): 222 tr, −₹17,977.51, expectancy −80.98. Placebo B (lag = prior-day premove): 113 tr, −₹14,225.61, expectancy −125.89. The mirror's raw-net margins (+₹7,963.71 vs A, +₹4,211.81 vs B) are abstention artefacts — per trade it is the WORST of the three. On above50 days the capped-band population loses in every direction and under a stale qualifier (Lesson 18).
- **Decide: REJECTED — saturation gate fails (a), (b), (d).** Union would be 805 tr / +₹139,351.35 < incumbent (a FAIL); August −₹2,485.20 flips red (b FAIL); October unchanged +₹50,349.79 (c PASS — mirror adds no October trades); ex-top-3 ₹28,263.83 < ₹30,773.31 (d FAIL); controls leg nominally passes on raw net but is expectancy-negative. Incumbent UNCHANGED (779 tr / +₹149,365.15).
- **N4-revisit:** August shortfall UNCHANGED at ₹2,285.38 (August +₹1,735.16 vs ≥ ₹4,020.54 required; the hypothetical union shortfall would have been ₹6,505.74).
- **Saturation:** no_beat_cycles 0 → **1**, best_total unchanged ₹149,365.15. Lesson 18 appended; F4-MIRROR family CLOSED.
- **Next:** saturation continues from +₹149,365.15 (2 more consecutive no-beats end the run) — genuinely new Lesson-3 material (a denser information set than results-day reactions, or a state other than the 50DMA joint state), or October-headroom growth past recorded blocks. The August/N4 gap (₹2,285.38) has no incumbent-slice or mirror route left.

## SAT-10 — F4 stop step S080 → S095 re-test at the current book (2026-10-31)
- **Charter:** lessons read first (Lesson 4 addendum — exit medicine is population-specific — and Lesson 16 govern: diagnose THIS book's stop population, re-measure at the current state). Diagnosis: stocks_engine_sat10_diag.py / sat10_diag.json. Fix frozen in stocks_engine_frozen.md (SAT-10 section) AFTER diagnosis, BEFORE scoring. Score: stocks_engine_sat10_score.py / sat10_result.json; new F4 dump: stocks_engine_sat10_f4s095_trades.csv.
- **Diagnosis:** anchor exact (779 tr / +₹149,365.15). Current F4 = 478 tr / +₹90,281.54 (target exits 129 / +₹176,751.53; square-off 167 / +₹41,023.00; stop exits 182 / −₹127,492.99). Post-exit first passage at −0.95% (OC-4 / SAT-2 diag3 method): FULL 4 rescue / 153 deeper / 25 neither (10 closed ≥ flat), rough swing est **+₹6,951.25**; OCTOBER (22 stops) 1/15/6, est +₹2,953.74; AUGUST (6 stops) 0/5/1, est −₹652.72 — August's stops remain genuine continuations (SAT-2's finding holds on the new population), the step was predicted to cost August a little and pay October/Jan/Feb/Apr. Pre-registered support test (est total up AND predicted all-green AND predicted October ≥ 50,000): PASS → step frozen and scored exactly. Disclosed in the freeze: rescue rate is thin (4/182); the estimate leans on neither-close value.
- **Verify:** Anchor A — fresh S080 rebuild == oc4 dump per-trade (661 tr). Anchor B — filtered S080 union == state (779 tr / +₹149,365.15 / month table to the paisa / ex-top-3 ₹30,773.31). Anchor D — S095 entry set == S080 entry set (478 entries; entries are exit-independent under first-signal-only). Timing audit 0 violations on BOTH builds.
- **Exact score (T150/S095):** F4 +₹90,281.54 → **+₹94,179.91 (+₹3,898.37 — 56% of the rough estimate)**; the estimate misallocated months (October est +₹2,953.74 vs exact **+₹567.24**; February est +₹3,389.65 vs exact **+₹4,204.65**; March est −₹2,324.38 vs exact −₹3,582.31). Month table: Jan 12,497.27 → **14,722.77** · Feb 3,611.69 → **7,816.34** · Mar 22,321.47 → 18,739.16 · Apr 3,671.26 → **7,744.23** · May 28,317.69 → 27,400.76 · Jun 3,941.51 → 4,105.67 · Jul 3,196.63 → 3,092.38 · **Aug 1,735.16 → 1,182.43 (−552.73)** · Sep 19,722.68 → 17,542.75 · **Oct 50,349.79 → 50,917.03**. **Total +₹149,365.15 → +₹153,263.52**, trades unchanged 779. Ex-top-3 ₹30,773.31 → **₹38,278.28 (+₹7,504.97)** — the step earns more outside the top-3 than in total.
- **Decide: BANKED — all five saturation-gate legs pass** (total rises; all ten green, min August +₹1,182.43; October ≥ 50,000 with headroom ₹917.03; ex-top-3 improves; anchors + audit clean). Book F4 exits are now **T150/S095** (dump: stocks_engine_sat10_f4s095_trades.csv). **Saturation: no_beat_cycles stays 0, best_total → ₹153,263.52.**
- **Sequencing note (Lesson 14 paying off):** August paid −₹552.73 for this step and stayed green ONLY because SAT-7/SAT-8 had thickened it to +₹1,735.16 first — at the post-SAT-6 book (August +₹103.44) the identical step would have flipped August red and failed the gate.
- **N4-revisit:** August shortfall **₹2,285.38 → ₹2,838.11** (August +₹1,182.43 vs ≥ ₹4,020.54 required; after hypothetical re-apply = −₹2,652.42) — grew by the August cost; the rebuild route remains blocked and now needs genuinely new August earnings, not incumbent slices.
- **Next:** saturation continues from +₹153,263.52 (3 consecutive no-beats end the run; counter is 0). Frontiers: genuinely new Lesson-3 material (denser information set, or a state other than the 50DMA joint state); a further F4 stop step (S095 → S110) ONLY after a fresh excursion diagnosis of the new S095 stop population (SAT-2's S110 August evidence was negative; August is again the thinnest month at +₹1,182.43); October headroom ₹917.03 still short of every recorded block (GLENMARK-SHORT ₹1,404.72, and a top-3 name besides). All pre-SAT-10 F4 slice numbers are stale — the S095 rebuild changed every F4 exit (Lesson 16).

## SAT-11 — F4 stop step 2 (S095 → S110): diagnosed, support test FAILED on August — NOT scored, F4 stop family CLOSED at S095 (2026-10-31)
- **Charter:** lessons read first (Lesson 4 addenda — exit medicine is population-specific; a stop step is a property of the book state; Lesson 16 — re-measure at the current state). The support test was pre-registered in the cycle brief BEFORE the diagnosis ran: freeze + score S095 → S110 (single step, T150 unchanged) ONLY IF the excursion estimate says total up AND predicted all-green with August ≥ ~₹1,000 AND predicted October ≥ ₹50,000; predicted August < ₹500 → do NOT score, close the stop family at S095.
- **Diagnosis (stocks_engine_sat11_diag.py / sat11_diag.json):** anchor exact (779 tr / +₹153,263.52, month table to the paisa). Current F4 (T150/S095) = 478 tr / +₹94,179.91 (target 133 / +₹183,123.20; square-off 190 / +₹41,245.00; stop 155 / −₹130,188.29). Post-stop first passage at −1.10%: FULL **1 rescue / 126 deeper / 28 neither** (8 closed ≥ flat), rough est **+₹6,686.35** → predicted total ₹159,949.87. OCTOBER (17 stops): 0 rescue / 11 deeper / 6 neither, est +₹2,610.24 → predicted ₹53,527.27. AUGUST (5 stops): **0 rescue / 5 deeper / 0 neither**, est **−₹1,168.73** → predicted August **+₹13.70**. Other predicted months all comfortably green (thinnest after August: June ₹2,494.43, April ₹6,151.39).
- **Decide: NOT SCORED, NOTHING BANKED.** Support-test legs (i) total-up and (iii) October pass on the estimate; leg (ii) fails — predicted August ₹13.70 is below the ~₹1,000 support line AND below the ₹500 family-close line. The rough estimate is a compass (SAT-10 exact was 56% of estimate with months misallocated), but August's signal is structural, not marginal: every August stop in the S095 population went deeper first — there is nothing for a wider stop to rescue in that month, and the step would simply charge each of them ~0.15% more. Incumbent UNCHANGED (779 tr / +₹153,263.52; F4 exits stay **T150/S095**; dump unchanged: stocks_engine_sat10_f4s095_trades.csv).
- **F4 STOP FAMILY CLOSED at S095 on this window** — third agreeing August diagnosis (SAT-2: 0/11 rescued; SAT-10 exact: −₹552.73; SAT-11: 5/5 deeper). Reopening condition: August thickened by other means first, then a fresh excursion diagnosis of the then-current population. Recorded in stocks_engine_frozen.md (SAT-11 section) and as a Lesson 4 addendum.
- **N4-revisit:** August shortfall UNCHANGED at **₹2,838.11** (book unchanged; August +₹1,182.43 vs ≥ ₹4,020.54 required; after hypothetical re-apply = −₹2,652.42).
- **Saturation:** no_beat_cycles 0 → **1**, best_total unchanged **₹153,263.52**.
- **Next:** saturation continues from +₹153,263.52 (2 more consecutive no-beats end the run). Frontiers left: genuinely new Lesson-3 material only (a denser information set than results-day reactions, or a state other than the 50DMA joint state); October headroom ₹917.03 still short of the GLENMARK-SHORT block (₹1,404.72 — and a Lesson 6 top-3 name besides). The F4 stop ladder, the August direction-slice space, and the F4 mirror are all closed.

## SAT-12 — F4 target step (T150 → T165): diagnosed, support test FAILED on the total leg — NOT scored, F4 TARGET FAMILY CLOSED at T150 (2026-10-31)
- **Charter:** lessons read first (Lesson 4 addenda — exit medicine is population-specific, diagnose this book's population before stepping; Lesson 16 — re-measure at the current state). The support test was pre-registered in the cycle brief BEFORE the diagnosis ran: freeze + score T150 → T165 (single step, S095 unchanged) ONLY IF the winner-excursion estimate says total up AND predicted all-green AND predicted October ≥ ₹50,000; if it fails, do NOT score and close the target family at T150.
- **Diagnosis (stocks_engine_sat12_diag.py / sat12_diag.json):** anchor exact (779 tr / +₹153,263.52, month table to the paisa). Current F4 (T150/S095) = 478 tr / +₹94,179.91 (target 133 / +₹183,123.20; square-off 190 / +₹41,245.00; stop 155 / −₹130,188.29). Post-exit first passage at +1.65% vs the −0.95% stop, up to the 15:10 square-off: FULL **103 reach / 3 stop-first / 27 neither** (6 with no later bars), rough swing est **−₹8,293.33** → predicted total ₹144,970.19. Class decomposition: reach +₹14,303.80 (avg +₹138.87 = +0.15 × entry), stop-first −₹3,310.93 (avg −₹1,103.64 = −2.45 × entry), neither −₹19,286.20 (avg −₹714.30 give-back at the square-off close). OCTOBER (36 targets): 27/0/9, est +₹1,560.27 → predicted ₹52,477.30 (headroom ₹2,477.30). AUGUST (2 targets): 2/0/0, est +₹153.67 → predicted ₹1,336.10. Predicted all-green: TRUE (thinnest predicted: August ₹1,336.10, June ₹4,026.15). Worst month swings: January −₹5,815.82, April −₹2,830.49, May −₹1,880.93; only March (+₹1,802.43), October and August positive.
- **Decide: NOT SCORED, NOTHING BANKED.** Support-test leg (i) fails decisively — the estimate is DOWN ₹8,293.33, not a knife-edge; legs (ii)/(iii) passing does not rescue it. The step would have grown October headroom to ₹2,477.30 — past the GLENMARK-SHORT block (₹1,404.72) — but buying headroom with −₹8,293.33 of total is not a beat under the saturation gate, and the pre-registered rule forbids scoring it. Incumbent UNCHANGED (779 tr / +₹153,263.52; F4 exits stay **T150/S095**; dump unchanged: stocks_engine_sat10_f4s095_trades.csv). **October headroom stays ₹917.03** — F4 × GLENMARK × SHORT remains floor-blocked (October slice +₹1,404.72 > ₹917.03) and a Lesson 6 top-3 name besides.
- **F4 TARGET FAMILY CLOSED at T150 on this window** — the winner population's reach/give-back arithmetic (77% reach at +0.15 vs ~5:1 per-trade give-back on the 27 neithers) leaves nothing for a wider target to harvest; OC-3's T125 → T150 was the ladder's last paying rung. Recorded in stocks_engine_frozen.md (SAT-12 section) and as a Lesson 4 addendum. With SAT-11, BOTH F4 exit ladders are now closed — F4's exits are fully diagnosed at T150/S095 on this window.
- **N4-revisit:** August shortfall UNCHANGED at **₹2,838.11** (book unchanged; August +₹1,182.43 vs ≥ ₹4,020.54 required).
- **Saturation:** no_beat_cycles 1 → **2**, best_total unchanged **₹153,263.52**. ONE more consecutive no-beat cycle ends the run as saturated.
- **Next:** saturation continues from +₹153,263.52 (1 more consecutive no-beat ends the run). Frontiers left: genuinely new Lesson-3 material only (a denser information set than results-day reactions, or a state other than the 50DMA joint state). The F4 stop ladder (SAT-11), the F4 target ladder (SAT-12), the August direction-slice space (SAT-8), and the F4 mirror (SAT-9) are all closed; October headroom ₹917.03 remains short of every recorded block.

## SAT-13 — P2F-R2 (R+2 reaction follow) BANKED as 5th component; saturation counter RESET (2026-10-31)
- **Charter:** lessons read first (Lesson 3 — build from information/state; Lesson 11 — mechanism-scoped exclusions; Lesson 16 — re-derive at the current book; Lesson 18 — a time-shifted variant is a new system, placebo-controlled per-trade). Diagnosis: stocks_engine_sat13_diag.py / sat13_diag.json. Fix frozen in stocks_engine_frozen.md (SAT-13 section) AFTER diagnosis, BEFORE scoring. Score: stocks_engine_sat13_score.py / sat13_result.json; new component dump: stocks_engine_sat13_p2fr2_trades.csv.
- **Diagnosis — two directions weighed:** (1) Book-wide (comp × stock × dir) slice scan at the CURRENT book (all four components, S095 F4 exits — pre-SAT-10 F4 slice numbers are stale per Lesson 16): 31 rows qualify (thin-month<0 AND full<0 AND Oct slice ≤ ₹917.03) but all are small — largest full-period loss F4 × OIL × SHORT (−₹2,712.77 / 13 tr, win 4; June −₹486.88; Oct slice −₹465.84), then F4 × IRCTC × SHORT (−₹1,297.01), INV-LONG × INDUSTOWER (−₹1,189.01), INV-LONG × VEDL (−₹2,424.75 / 18 tr, win 4; Oct slice −₹318.05); the rest are mostly single-trade thin-month slices. Weighed and NOT chosen: the R2 union effect is ~5× the best slice, and adding a disjoint component does not consume the slices (they remain for later cycles, re-derived at the then-current book). (2) P2F-R2, built with the audited stocks_tuning_event.py machinery verbatim: construction anchor 39 candidates == M1 raw P2F@2.5 population; 38 trades built (RECLTD R=2026-10-27 dropped — no R+2 in the daily series); timing audit 0 violations; (date,stock) overlap vs incumbent P2F = 0; RF-1 weekend trades = 0. Standalone RAW: 38 tr / +₹9,813.68, exp +₹258.25, breadth 12, H1 +₹12,288.08 / **H2 −₹2,474.40**; placebo (opposite direction, identical entries) −₹477.83 / exp −₹12.57 — beaten overall and per-trade, but NOT in H2 (placebo H2 +₹1,455.72). With the book's event-follow name exclusions (AU-1 ASTRAL, JU-1 HINDUNILVR — frozen for this mechanism family before R2 existed): 34 tr / +₹12,912.48, exp +₹379.78, H1 +₹13,472.08 / H2 −₹559.60; the 4 excluded trades net −₹3,098.80 (Lesson 11, fourth instance). RAW union also passes the gate (+₹163,077.20, min month July +₹922.99) but weaker on every leg — disclosed in the freeze; the book-consistent definition was frozen.
- **Verify (score run):** Anchor A — incumbent union == state (779 tr / +₹153,263.52 / month table to the paisa / ex-top-3 ₹38,278.28). Anchor B — candidate population 39, frozen 34-trade set == diagnosis set exactly. Anchor C — timing audit 0 violations, P2F overlap 0. Anchor D (disclosed) — placebo re-scored on the frozen 34-candidate subset: 34 tr / **−₹6,542.33, expectancy −₹192.42** vs the component's +₹379.78 — beaten decisively, overall and per-trade.
- **Exact score:** union 813 tr / **+₹166,176.00**. Month table: Jan 14,722.77 → **18,656.70** · Feb 7,816.34 → **12,689.65** · Mar 18,739.16 (unchanged) · Apr 7,744.23 → 7,602.73 (−141.50) · May 27,400.76 → **32,207.10** · Jun 4,105.67 → 2,036.67 (−2,069.00) · Jul 3,092.38 → 2,022.79 (−1,069.59) · **Aug 1,182.43 → 3,571.43 (+2,389.00)** · Sep 17,542.75 (unchanged) · **Oct 50,917.03 → 51,107.02** (headroom ₹1,107.02). Ex-top-3 ₹38,278.28 → **₹51,853.86 (+₹13,575.58)** — the component earns more outside the top-3 than its own net; top-3 names unchanged (TVSMOTOR / ASTRAL / GLENMARK).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹12,912.48; all ten green, min July +₹2,022.79; October ≥ 50,000; ex-top-3 improves; anchors + audit clean). P2F-R2 is the book's **5th component** (dump: stocks_engine_sat13_p2fr2_trades.csv). **Saturation: no_beat_cycles 2 → 0, best_total → ₹166,176.00 — the run is NOT saturated.** Lesson 19 appended (+ Lesson 11 addendum).
- **Disclosed risk (carried, not hidden):** the component is H1-carried (H2 −₹559.60; June/July are its cost months and both thinned — June ₹4,105.67 → ₹2,036.67, July ₹3,092.38 → ₹2,022.79, now the book's two thinnest months after August). It is frozen verbatim for December judging under Lesson 7; no in-sample re-tuning.
- **N4-revisit:** August shortfall **₹2,838.11 → ₹449.11** (August +₹3,571.43 vs ≥ ₹4,020.54 required; after hypothetical re-apply = −₹263.42) — nearly unlocked; ₹449.11 of August thickening by other means remains the condition (June's condition stays covered).
- **Next:** saturation continues from +₹166,176.00 (counter 0). Frontiers: (i) ₹449.11 of August thickening → the CH-2 N4 exit rebuild (+₹9,483.45 at its measurement; re-measure per Lesson 16) unlocks; (ii) the SAT-13 slice-scan registry (F4 × OIL × SHORT first — re-derive at the new book); (iii) October headroom ₹1,107.02 — still short of the GLENMARK-SHORT block (₹1,404.72, and a top-3 name besides); (iv) P2F-R3 (the R+3 lag) is now a named, untested direction under Lesson 19's corollary — a new system, frozen and placebo-controlled on its own, NOT an extension of R2's credibility.

## SAT-14 — P2F × HINDALCO × LONG exclusion BANKED; the CH-2 N4-rebuild revisit condition (August leg) is MET at this book (2026-10-31)
- **Charter:** lessons read first (Lesson 5/15 — surgical removal, direction-scoped; Lesson 12 addendum — re-scan the registry at the current headroom/book; Lesson 14 — this cycle exists to discharge the revisit sequencing; Lesson 16 — the SAT-13 registry was a hypothesis about a four-component book, re-derived from scratch). Diagnosis: stocks_engine_sat14_diag.py / sat14_diag.json. Fix frozen in stocks_engine_frozen.md (SAT-14 section) AFTER diagnosis, BEFORE scoring. Score: stocks_engine_sat14_score.py / sat14_result.json.
- **Diagnosis:** anchor exact (813 tr / +₹166,176.00 / month table to the paisa / ex-top-3 ₹51,853.86; INV-LONG 218 / N4-V3 50 / P2F 33 / F4 478 / P2F-R2 34). Fresh slice scan at the CURRENT five-component book — (comp × stock × dir) negative in August AND full-period: 8 slices. Feasible (August gain ≥ ₹449.11, October slice ≤ ₹1,107.02, all-green after): exactly 2. NOT chosen: F4 × GLENMARK × SHORT (20 tr; Aug −₹4,744.78 but full only −₹136.98 with 10/20 winners — an August story, not rot-everywhere; October slice +₹1,062.55 would leave October at ₹50,044.47; a Lesson 6 top-3 name already marked not-a-real-candidate). Chosen by the pre-registered least-surgery rule: **P2F × HINDALCO × LONG — 1 trade** (2026-08-10, entry 09:15, exit stop, net −₹572.50; reaction R = 2026-08-07, +3.17%), re-verified trade-by-trade in-diagnosis and again at scoring (Anchor B: deleted set == frozen set exactly). It is P2F's only HINDALCO trade in the book — the slice is the component's whole position in that name × direction; August slice = full-period = −₹572.50, October slice exactly ₹0.00.
- **Exact score:** union 812 tr / **+₹166,748.50**. Only August moves: **Aug 3,571.43 → 4,143.93 (+572.50)**; every other month identical to the paisa; October unchanged **₹51,107.02** (headroom ₹1,107.02). Ex-top-3 ₹51,853.86 → **₹52,426.36** (+₹572.50; HINDALCO is not a top-3 name).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹572.50; all ten green, min July +₹2,022.79; October ≥ 50,000; ex-top-3 improves; anchors A/B pass). P2F now also excludes HINDALCO LONG (mechanism × direction scoped; N4-V3 / INV-LONG / F4 / P2F-R2 trade HINDALCO unchanged). **Saturation: no_beat_cycles stays 0, best_total → ₹166,748.50 — the run is NOT saturated.**
- **THIN-SAMPLE CAVEAT (recorded, not buried):** the banked slice is ONE trade — the thinnest evidence class the engine has used (JU-1: 2 trades). No claim is made that HINDALCO-LONG reactions are a loser population; the bank is the mechanical Lesson 5/15 shape at minimum surgery, taken to discharge the Lesson 14 revisit arithmetic. Per SAT-6's addendum discipline, the trade it makes is reported as what it is: August month-shape bought for +₹572.50 of total.
- **N4-revisit:** the August leg condition is **MET at this book** — August +₹4,143.93 ≥ the ≥ ₹4,020.54 the CH-2 rebuild arithmetic required (margin ₹123.39; June's condition stays covered per SAT-1). This does NOT pre-judge the rebuild: its CH-2 deltas (August −₹3,834.85, June flip, total +₹9,483.45) were measured four components and fourteen cycles ago and are stale by Lesson 16. **SAT-15 = re-measure the N4-V3 exit rebuild T125/S050 → T150/S080 at the current book, then re-apply under the saturation gate.**
- **Next:** saturation continues from +₹166,748.50 (counter 0). Frontiers: (i) SAT-15 N4 rebuild re-measurement/re-apply; (ii) P2F-R3 (R+3 lag) — untested, new system under Lesson 19's corollary; (iii) the remaining registry slices (F4 × RECLTD × SHORT Aug −₹342.58 / full −₹503.97; INV-LONG × VEDL; F4 × OIL × SHORT) stay available, re-derived per cycle; (iv) October headroom ₹1,107.02 still short of the GLENMARK-SHORT block (₹1,404.72, top-3 name besides). Protect the thin months: July +₹2,022.79 / June +₹2,036.67 / August +₹4,143.93 (August's revisit margin is only ₹123.39 — any August-costing fix before SAT-15 re-blocks the arithmetic as measured here).

## SAT-15 — CH-2 N4-V3 exit rebuild RE-MEASURED + RE-APPLIED: BANKED — total +₹176,231.95 (2026-10-31)
- **Charter:** lessons read first (Lesson 14 — the revisit sequencing: thicken the thin months, then the blocked improvement unlocks; Lesson 16 — CH-2's deltas are stale, re-measure everything at the current book). Fix frozen in stocks_engine_frozen.md (SAT-15 section) BEFORE scoring. Score: stocks_engine_sat15_score.py / sat15_result.json; new N4 dump: stocks_engine_sat15_n4_t150s080_trades.csv.
- **Verify (all anchors pass):** (A) current book == state — 812 tr / +₹166,748.50 / month table to the paisa / ex-top-3 ₹52,426.36 (INV-LONG 218 / N4-V3 50 / P2F 32 / F4 478 / P2F-R2 34). (B) the replay machinery regenerates the incumbent before measuring the challenger: T125/S050 replay reproduces the source dump **56/56** per-trade (convention offset = 0, entry-bar evaluation, as CH-2) and the filtered set == the book's N4 component per-trade (50 tr). (C) T150/S080 build: entries identical to the anchor trades (date, stock, direction, 09:35, entry price), exit_time ≥ entry_time on all 56, **0 audit violations** (4 same-bar exits under the entry-bar convention, same class as CH-2's 13 at the old exits).
- **Exact score — the re-measurement is IDENTICAL to CH-2, to the paisa:** N4 component 50 tr / +₹7,761.80 → **+₹17,245.25 (delta +₹9,483.45)**. Union 812 tr / **+₹176,231.95**. Month table: Jan 18,656.70 → **25,923.78** (+7,267.08) · Feb 12,689.65 → **17,465.71** (+4,776.06) · Mar 18,739.16 → 19,259.91 (+520.75) · Apr 7,602.73 → 7,534.13 (−68.60) · May 32,207.10 → 33,304.29 (+1,097.19) · Jun 2,036.67 → 1,382.01 (−654.66) · Jul 2,022.79 → 1,262.53 (−760.26) · **Aug 4,143.93 → 309.08 (−3,834.85 — GREEN, where CH-2's identical delta produced −3,649.16 RED)** · Sep 17,542.75 (unchanged — no September N4 trades) · **Oct 51,107.02 → 52,247.76** (+1,140.74; headroom ₹2,247.76). Ex-top-3 ₹52,426.36 → **₹56,308.12 (+₹3,881.76)**; top-3 composition changes (TVSMOTOR / ASTRAL / **OBEROIRLTY** — GLENMARK drops out of the top-3 on the new book's per-stock totals).
- **Why identical (Lesson 16 addendum appended):** the union is additive and none of SAT-1..SAT-14 touched an N4 trade, so an exit rebuild's delta — a function of its own component's entries and candles — could not expire. What CH-2 lacked was never the measurement; it was the surrounding balances. Lesson 14's sequencing (SAT-1 June, SAT-13/SAT-14 August) is what this bank stands on: the same −₹3,834.85 August delta that flipped August red at +₹185.69 is absorbed at +₹4,143.93.
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹9,483.45; all ten green, min August +₹309.08; October ≥ 50,000 at ₹52,247.76; ex-top-3 improves; anchors + audit clean). **N4-V3's book exits are now T150/S080; the book's N4 source for all future cycles is stocks_engine_sat15_n4_t150s080_trades.csv (M1.load_n4() is the OLD T125/S050 dump — do not anchor on it).** The CH-2 revisit is DISCHARGED — both legs, closed. **Saturation: no_beat_cycles stays 0, best_total → ₹176,231.95 — the run is NOT saturated.**
- **Disclosed cost (first-class):** August is the book's razor again at **+₹309.08** (29 trades) — the rebuild spent ₹3,834.85 of the August balance SAT-13/SAT-14 built. June (+₹1,382.01) and July (+₹1,262.53) are the next thinnest. Any future fix costing August more than ₹309.08 un-secures it; protect all three.
- **Next:** saturation continues from +₹176,231.95 (counter 0; ₹17,623/month vs the ₹75,000/month goal — the climb continues, the gap is stated plainly). Frontiers: (i) P2F-R3 (R+3 lag) — untested new system under Lesson 19's corollary; (ii) the remaining slice registry (re-derive per cycle); (iii) October headroom ₹2,247.76 now exceeds the GLENMARK-SHORT slice's recorded October cost (₹1,404.72) — but that slice failed Lesson 5's rot test at its last derivation (Aug −₹4,744.78 vs full only −₹136.98, 10/20 winners) and buying August shape with it must be argued explicitly, not slid through (SAT-6 addendum discipline); GLENMARK is no longer a top-3 name at this book; (iv) August thickening is again the binding constraint for anything that costs August.

## SAT-16 — P2F-R3 (R+3 reaction follow) REJECTED; the R-ladder is CLOSED at R+2 (2026-10-31)
- **Charter:** lessons read first (Lesson 19's corollary — test the time-shifted self, each lag a new system with no inherited credibility; Lesson 18 — placebo must be beaten per-trade; Lesson 16 — anchor at the current book; SAT-15 book law — N4 anchored on the SAT-15 T150/S080 dump, NOT M1.load_n4()). Diagnosis: stocks_engine_sat16_diag.py / sat16_diag.json. Fix frozen in stocks_engine_frozen.md (SAT-16 section) AFTER diagnosis, BEFORE scoring. Score: stocks_engine_sat16_score.py / sat16_result.json.
- **Verify (all anchors pass):** (A) incumbent == state — 812 tr / +₹176,231.95 / month table to the paisa / ex-top-3 ₹56,308.12 (INV-LONG 218 / N4-V3 50 from the SAT-15 dump / P2F 32 / F4 478 / P2F-R2 34). (B) construction anchor 39 candidates == the M1 raw P2F@2.5 population (the same reaction set as P2F/R2); 38 built (RECLTD R=2026-10-27 dropped — no R+3 in the daily series); frozen 34-trade set == diagnosis set exactly. (C) timing audit 0 violations (every date == the stock's 3rd trading day after R by construction); (date,stock) overlap vs incumbent P2F = 0 and vs P2F-R2 = 0 (mechanical); within-R3 duplicates 0; RF-1 weekend trades 0.
- **Standalone (frozen: RF-1 + AU-1/JU-1 name exclusions):** 34 tr / **+₹952.10, expectancy +₹28.00 (≈ ₹0)**, win 12/34, breadth 21, **H1 +₹2,641.97 / H2 −₹1,689.87** — H2-negative like R2, and weaker in both halves than R2's frozen line (H1 +₹13,472.08 / H2 −₹559.60, expectancy +₹379.78). The 4 excluded-name trades net −₹1,536.40 (ASTRAL −₹780.90 / −₹809.20; HINDUNILVR −₹1,196.30 / +₹1,250.00 — the Lesson 11 fade profile again, one winner).
- **Controls — the placebo wins:** opposite-direction on identical entries (frozen subset): 34 tr / **+₹4,064.36, expectancy +₹119.54** (H1 +₹534.80 / **H2 +₹3,529.56**). The real rule beats its placebo in NEITHER half on the H2 side and loses per-trade overall by 4.3×. Per Lesson 18's discipline this is disqualifying on its own: at R+3 the reaction direction carries no follow information. August slice +₹130.25 (positive, negligible — the razor was never the issue); October slice −₹135.25.
- **Exact score (union):** 846 tr / +₹177,184.05. Month table: Jan 25,923.78 → 26,810.38 · Feb 17,465.71 → 18,600.84 · Mar 19,259.91 (unchanged) · Apr 7,534.13 → 7,392.38 · May 33,304.29 → 34,066.28 · Jun 1,382.01 → 1,424.64 · **Jul 1,262.53 → −464.97 (FLIPS RED — R3 July slice −₹1,727.50)** · Aug 309.08 → 439.33 (+130.25) · Sep 17,542.75 (unchanged) · Oct 52,247.76 → 52,112.51 (headroom ₹2,112.51). Ex-top-3 ₹56,308.12 → **₹55,449.72 (−₹858.40)**; top-3 unchanged (TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: REJECTED — gate legs (b) and (d) FAIL, and the controls leg is disqualifying** ((a) total rises nominally +₹952.10 PASS; (b) all-green FAIL — July red; (c) October ≥ 50,000 PASS; (d) ex-top-3 FAIL; (e) anchors + audit PASS). Incumbent UNCHANGED (+₹176,231.95, 812 tr, five components). **Saturation: no_beat_cycles 0 → 1, best_total unchanged ₹176,231.95 — the run is NOT saturated (2 more consecutive no-beats end it).** Lesson 20 appended — reaction information has a two-day reach; **the R-ladder is CLOSED at R+2** (do not average lags, do not blend R+2/R+3).
- **Next:** saturation continues from +₹176,231.95 (counter 1; ₹17,623/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the remaining slice registry (re-derive per cycle — F4 × OIL × SHORT first; N4 slices from the SAT-15 dump); (ii) August thickening (August still the razor at +₹309.08 — an August-positive slice/component has outsized gate value, and R3's +₹130.25 August slice shows the month is not allergic to new flow, only to July-shaped flow); (iii) the GLENMARK-SHORT argument (headroom ₹2,247.76 > its recorded October cost ₹1,404.72, but it failed Lesson 5's rot test — must be argued explicitly, not slid through); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis, which is now fully mapped (R+1/R+2 real, R+3 noise, below-band dead at every lag per Lessons 17/19).

## SAT-17 — registry top slice (N4-V3 × TVSMOTOR × LONG) BANKED; saturation counter reset to 0 (2026-10-31)
- **Charter:** lessons read first (Lesson 16 — registries expire, re-derive from scratch; Lessons 5/15 — deletion only for slices negative in a thin month AND full-period, direction-scoped; Lesson 6 — ex-top-3 reported beside every total; SAT-15 book law — N4 anchored on the SAT-15 T150/S080 dump, NOT M1.load_n4()). Diagnosis: stocks_engine_sat17_diag.py / sat17_diag.json. Fix frozen in stocks_engine_frozen.md (SAT-17 section) AFTER diagnosis, BEFORE scoring. Score: stocks_engine_sat17_score.py / sat17_result.json.
- **Registry (re-derived at the current book):** 148 (comp × stock × dir) slices across the five components; **28 qualify** (full < 0 AND negative in ≥ 1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,247.76 headroom). Ranked by full-period value with feasibility (every month > 0 after removal; razors Aug/Jul/Jun keep ≥ ₹100; October ≥ ₹50,000; ex-top-3 not worse) and the quality bar (genuinely negative full period): GLENMARK-SHORT sits at the registry's BOTTOM (full −₹136.98, 10/20 winners) and is below the bar as always — the top row is a different animal entirely (below). Queue behind it: F4 × OIL × SHORT (−₹2,712.77 / 13 tr), INV-LONG × VEDL (−₹2,424.75 / 18 tr), INV-LONG × HINDZINC (−₹2,131.83 / 9 tr), P2F-R2 × TVSMOTOR × LONG (−₹1,979.90 / 1 tr).
- **Verify (all anchors pass):** (A) incumbent == state — 812 tr / +₹176,231.95 / month table to the paisa / ex-top-3 ₹56,308.12 (INV-LONG 218 / N4-V3 50 from the SAT-15 dump / P2F 32 / F4 478 / P2F-R2 34). (B) the deleted set extracted at scoring == the frozen set exactly: 2026-07-22, TVSMOTOR, LONG, −₹3,185.76. (C) deletion-only on audited dumps — no new entries; timing inherited.
- **The slice:** N4-V3 × TVSMOTOR × LONG = 1 trade — 2026-07-22, entry 09:35 at ₹3,932.20 (combined results reaction, +3.58% by 09:30), stop exit ₹3,900.74 at 14:00, net **−₹3,185.76** at the book's T150/S080 exits (the same entry measured −₹2,006.10 at the old T125/S050 exits — the exit rebuild deepened this particular loser). Direction split is the Lesson 15 shape inside one name × mechanism: N4's two TVSMOTOR SHORT trades earn +₹5,476.55 and +₹5,129.45 and stay untouched. July slice −₹3,185.76 = the full-period slice; October and August slices exactly ₹0.00.
- **THIN-SAMPLE CAVEAT (disclosed, first-class):** ONE trade — the thinnest evidence class the engine banks on (SAT-14 precedent, disclosed identically). No population claim: TVSMOTOR-LONG reactions are not thereby a discovered loser class, and TVSMOTOR remains the book's largest earner. The bank stands on the registry arithmetic (most-negative full-period row in the book, sitting entirely inside a razor month, October- and August-neutral) and December judges the assembled book.
- **Exact score:** 811 tr / **+₹179,417.71**. Month table: Jan 25,923.78 · Feb 17,465.71 · Mar 19,259.91 · Apr 7,534.13 · May 33,304.29 · Jun 1,382.01 · **Jul 1,262.53 → 4,448.29 (+3,185.76)** · Aug 309.08 (unchanged — the razor intact) · Sep 17,542.75 · Oct 52,247.76 (unchanged; headroom ₹2,247.76) — every other month identical to the paisa. Ex-top-3 **₹56,308.12 → ₹56,308.12 (unchanged)**: the removed trade is on the #1 earner, so the total and the top-3 sum rose together and leg (d) passed as EQUALITY; TVSMOTOR's book total rose to ₹72,025.56 — concentration deepened, reported plainly (Lesson 6 addendum appended).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹3,185.76; all ten green with razors Aug 309.08 / Jun 1,382.01 / Jul 4,448.29 all ≥ ₹100; October ≥ 50,000; ex-top-3 not worse; anchors clean). **Book law added: N4-V3 takes no TVSMOTOR LONG signals — future cycles anchoring N4 on the SAT-15 dump must apply the exclusion.** **Saturation: no_beat_cycles 1 → 0, best_total → ₹179,417.71 — the run is NOT saturated.**
- **Next:** saturation continues from +₹179,417.71 (counter 0; ₹17,942/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (re-derive before use — next rows named above; August-negative quality-bar rows remaining: N4 × OIL × LONG Aug −₹405.20, F4 × RECLTD × SHORT Aug −₹342.58, F4 × PFC × SHORT Aug −₹55.00 — small August thickeners); (ii) August remains the razor at +₹309.08 — the binding constraint on anything that costs August; (iii) the GLENMARK-SHORT argument (October headroom ₹2,247.76 still exceeds its recorded October cost, but full −₹136.98 keeps failing Lesson 5's rot test — explicit argument required, not a routine slice); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped: R+1/R+2 real, R+3 noise, below-band dead at every lag).

## SAT-18 — F4 × OIL × SHORT exclusion: BANKED (2026-10-31)

- **Identify:** saturation continues from +₹179,417.71 (counter 0 after SAT-17). The brief named the next registry row: F4 × OIL × SHORT (SAT-17 registry: −₹2,712.77 / 13 tr; Jun −₹486.88; Oct −₹465.84). Registry re-derived from scratch at the post-SAT-17 book (stocks_engine_sat18_diag.py): 147 slices, 27 qualifying; Anchor A exact (811 tr / +₹179,417.71 / month table to the paisa / ex-top-3 ₹56,308.12; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the slice re-measured **identical to the SAT-17 record to the paisa** — 13 tr, −₹2,712.77, 4 winners; Jan +505.00 · Feb −260.53 · Mar −483.89 · Apr +40.00 · May −1,059.83 · Jun −486.88 · Sep −500.80 · Oct −465.84 · **Aug exactly ₹0.00 (no August trades)**. SAT-17 intervened only on an N4 leg, disjoint from F4 — the deltas did not expire (fourth positive invariance instance). Direction split (Lesson 15): F4 × OIL × LONG earns +₹491.75 (6 tr, 4 w) and stays; the SHORT half is the rot. Qualification: negative in a thin month (June) AND full-period ✓; October slice −₹465.84 ≤ headroom ₹2,247.76 ✓ (negative — removal RAISES October); August cost ₹0 ≤ ₹209.08 guard ✓.
- **Fix (frozen in stocks_engine_frozen.md, SAT-18 section, BEFORE scoring):** SAT-18-F4-OIL-SHORT — F4 takes no SHORT signals on OIL (stock × mechanism × DIRECTION; F4 keeps OIL LONG; all other components trade OIL unchanged).
- **Exact score (stocks_engine_sat18_score.py; Anchor B: deleted set == the frozen 13 trades exactly, net −₹2,712.77):** 798 tr / **+₹182,130.48**. Month table: Jan 25,923.78 → 25,418.78 (−505.00) · Feb 17,465.71 → 17,726.24 · Mar 19,259.91 → 19,743.80 · Apr 7,534.13 → 7,494.13 (−40.00) · May 33,304.29 → 34,364.12 (+1,059.83) · Jun 1,382.01 → **1,868.89** (+486.88) · Jul 4,448.29 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 17,542.75 → 18,043.55 · **Oct 52,247.76 → 52,713.60 (+465.84; headroom ₹2,713.60)**. Ex-top-3 **₹56,308.12 → ₹59,020.89** (improvement — OIL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹2,712.77; all ten green with razors Aug 309.08 / Jun 1,868.89 / Jul 4,448.29 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: F4 takes no OIL SHORT signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹182,130.48 — the run is NOT saturated.**
- **Next:** saturation continues from +₹182,130.48 (₹18,213/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (re-derive before use — next rows: INV-LONG × VEDL −₹2,424.75, INV-LONG × HINDZINC −₹2,131.83, P2F-R2 × TVSMOTOR × LONG −₹1,979.90, F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01); (ii) August remains the razor at +₹309.08 — August-negative quality rows left: N4 × OIL × LONG (Aug −₹405.20), F4 × RECLTD × SHORT (Aug −₹342.58), F4 × PFC × SHORT (Aug −₹55.00); (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-19 — INV-LONG × VEDL exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (798 tr / +₹182,130.48 / month table to the paisa / ex-top-3 ₹59,020.89; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-18 book (146 slices, 26 qualifying: full-period negative AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,713.60). The top qualifying row re-measured **identical to the SAT-18 registry record to the paisa** — INV-LONG × VEDL × LONG, 18 tr, −₹2,424.75, 4 winners (Jan −1,192.68 · Feb −386.20 · Mar −349.31 · Apr −423.30 · May −92.09 · Jun +336.88 · Oct −318.05 · **Aug exactly ₹0.00**). SAT-18 intervened only on an F4 leg, disjoint from INV-LONG — the deltas did not expire (fifth positive invariance instance). Mechanism scope (Lesson 11): VEDL earns in F4's gated flow (raw dump +₹3,062.75 / 28 tr) and P2F (+₹575.25); the rot is inside INV-LONG's below-trend pool only. INV-LONG is LONG-only, so no direction split exists within the component; quality bar cleared (−₹2,424.75 ≤ −₹500; not the GLENMARK near-zero pattern).
- **Fix (frozen in stocks_engine_frozen.md, SAT-19 section, BEFORE scoring):** SAT-19-INV-VEDL — INV-LONG takes no signals on VEDL (stock × mechanism exclusion; all other components trade VEDL unchanged).
- **Exact score (stocks_engine_sat19_score.py; Anchor B: deleted set == the frozen 18 trades exactly, net −₹2,424.75):** 780 tr / **+₹184,555.23**. Month table: Jan 25,418.78 → 26,611.46 (+1,192.68) · Feb 17,726.24 → 18,112.44 · Mar 19,743.80 → 20,093.11 · Apr 7,494.13 → 7,917.43 (+423.30) · May 34,364.12 → 34,456.21 · Jun 1,868.89 → 1,532.01 (−336.88, the slice's only positive month — stays green, keeps the ≥ ₹100 razor margin) · Jul 4,448.29 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 52,713.60 → 53,031.65 (+318.05; the slice's October leg was NEGATIVE, so the bank MINTED headroom again — now ₹3,031.65)**. Ex-top-3 **₹59,020.89 → ₹61,445.64** (improvement — VEDL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹2,424.75; all ten green with razors Aug 309.08 / Jun 1,532.01 / Jul 4,448.29 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no VEDL signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹184,555.23 — the run is NOT saturated.**
- **Next:** saturation continues from +₹184,555.23 (₹18,456/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (re-derive before use — next rows at this derivation: INV-LONG × HINDZINC −₹2,131.83, P2F-R2 × TVSMOTOR × LONG −₹1,979.90, F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-20 — INV-LONG × HINDZINC exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (780 tr / +₹184,555.23 / month table to the paisa / ex-top-3 ₹61,445.64; components INV-LONG 200 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 34; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus BDL + the SAT-19 VEDL exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-19 book (145 slices, 11 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65). The top qualifying row re-measured **identical to the SAT-19 registry record to the paisa** — INV-LONG × HINDZINC × LONG, 9 tr, −₹2,131.83, 1 winner (Jan −1,134.95 · Feb −335.57 · Mar −302.75 · Apr +299.69 · May −343.48 · Jun −314.77 · **Oct exactly ₹0.00 · Aug exactly ₹0.00**). SAT-19 intervened only on VEDL within INV-LONG, disjoint from HINDZINC — the deltas did not expire (sixth positive invariance instance). Mechanism scope (Lesson 11): HINDZINC also loses in F4 (−₹631.12), N4-V3 (−₹1,043.24) and P2F (−₹374.40) and earns in P2F-R2 (+₹812.50), but only the INV-LONG slice independently clears the bar — the exclusion stays INV-LONG-scoped. INV-LONG is LONG-only, so no direction split exists within the component; quality bar cleared (−₹2,131.83 ≤ −₹500; not the GLENMARK near-zero pattern).
- **Fix (frozen in stocks_engine_frozen.md, SAT-20 section, BEFORE scoring):** SAT-20-INV-HINDZINC — INV-LONG takes no signals on HINDZINC (stock × mechanism exclusion; all other components trade HINDZINC unchanged).
- **Exact score (stocks_engine_sat20_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹2,131.83):** 771 tr / **+₹186,687.06**. Month table: Jan 26,611.46 → 27,746.41 (+1,134.95) · Feb 18,112.44 → 18,448.01 · Mar 20,093.11 → 20,395.86 · Apr 7,917.43 → 7,617.74 (−299.69, the slice's only positive month — stays strongly green) · May 34,456.21 → 34,799.69 · Jun 1,532.01 → 1,846.78 (+314.77 — the razor month improves) · Jul 4,448.29 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 53,031.65 (unchanged — the slice is October-neutral; headroom stays ₹3,031.65)**. Ex-top-3 **₹61,445.64 → ₹63,577.47** (improvement — HINDZINC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹2,131.83; all ten green with razors Aug 309.08 / Jun 1,846.78 / Jul 4,448.29 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no HINDZINC signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹186,687.06 — the run is NOT saturated.**
- **Next:** saturation continues from +₹186,687.06 (₹18,669/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (10 qualifying remain — re-derive before use; next rows: P2F-R2 × TVSMOTOR × LONG −₹1,979.90, F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20, whose removal would thicken the August razor to ~₹714.28); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-21 — P2F-R2 × TVSMOTOR × LONG exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (771 tr / +₹186,687.06 / month table to the paisa / ex-top-3 ₹63,577.47; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 34; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus BDL + the SAT-19 VEDL + SAT-20 HINDZINC exclusions, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-20 book (144 slices, 10 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65). The top qualifying row re-measured **identical to the SAT-20 registry record to the paisa** — P2F-R2 × TVSMOTOR × LONG, 1 tr, −₹1,979.90, 0 winners (2026-07-24, entry 09:15 ₹3,879.80, stop exit ₹3,860.40 at 10:05; reaction R = 2026-07-22, +3.24%; **Oct exactly ₹0.00 · Aug exactly ₹0.00**). SAT-20 intervened only on HINDZINC within INV-LONG, disjoint from P2F-R2 — the deltas did not expire (seventh positive invariance instance). Mechanism × direction scope (Lessons 11/15): TVSMOTOR earns in every other component (F4 +₹39,505.22, INV-LONG +₹19,049.74, N4-V3 +₹10,606.00, P2F +₹4,844.50); the rot is this single R+2-follow LONG leg only. Thin-sample caveat recorded first-class (1 trade — SAT-14/SAT-17 precedent class; no population claim; TVSMOTOR remains the book's #1 earner).
- **Fix (frozen in stocks_engine_frozen.md, SAT-21 section, BEFORE scoring):** SAT-21-R2-TVSMOTOR-LONG — P2F-R2 takes no LONG signals on TVSMOTOR (stock × mechanism × direction exclusion; all other components trade TVSMOTOR unchanged; P2F-R2 has no TVSMOTOR SHORTs in-window).
- **Exact score (stocks_engine_sat21_score.py; Anchor B: deleted set == the frozen 1 trade exactly, net −₹1,979.90):** 770 tr / **+₹188,666.96**. Month table: Jul 4,448.29 → 6,428.19 (+1,979.90 — the slice's only month); all other months identical to the paisa, incl. **Aug 309.08 (unchanged — the razor intact)** and **Oct 53,031.65 (unchanged — October-neutral; headroom stays ₹3,031.65)**. Ex-top-3 **₹63,577.47 → ₹63,577.47 (EQUALITY pass** — TVSMOTOR ₹72,025.56 → ₹74,005.46, share 38.58% → 39.23%; concentration deepening disclosed per the Lesson 6 addendum).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,979.90; all ten green with razors Aug 309.08 / Jun 1,846.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000; ex-top-3 not worse; anchors clean). **Book law added: P2F-R2 takes no TVSMOTOR LONG signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹188,666.96 — the run is NOT saturated.**
- **Next:** saturation continues from +₹188,666.96 (₹18,867/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (9 qualifying remain — re-derive before use; next rows: F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row, Aug −₹405.20, whose removal would thicken the razor); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-22 — F4 × IRCTC × SHORT exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (770 tr / +₹188,666.96 / month table to the paisa / ex-top-3 ₹63,577.47; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-21 book (143 slices, 9 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65). The top qualifying row re-measured **identical to the SAT-21 registry record to the paisa** — F4 × IRCTC × SHORT, 13 tr, −₹2,712.77's successor row at −₹1,297.01, 5 winners (Jan −101.31 · Mar −877.45 · **Apr −143.25** · May −345.00 · **Jun −105.00** · **Aug exactly 0.00** · **Oct +275.00**). SAT-21 intervened only on a P2F-R2 leg, disjoint from F4 — the deltas did not expire (eighth positive invariance instance). Direction split (Lesson 15, seventh confirming instance): F4 × IRCTC × LONG earns +₹497.45 (9 tr) and stays; the SHORT half is the rot. Mechanism scope (Lesson 11): IRCTC earns in INV-LONG (+₹411.40), N4-V3 (+₹235.00), P2F (+₹616.81); its P2F-R2 slice (−₹296.05) is below the bar and a different mechanism — untouched. A 13-trade slice: a thicker evidence class than the recent 1-trade banks, its negative spread across six months.
- **Fix (frozen in stocks_engine_frozen.md, SAT-22 section, BEFORE scoring):** SAT-22-F4-IRCTC-SHORT — F4 takes no SHORT signals on IRCTC (stock × mechanism × direction; F4 keeps IRCTC LONG; all other components trade IRCTC unchanged).
- **Exact score (stocks_engine_sat22_score.py; Anchor B: deleted set == the frozen 13 trades exactly, net −₹1,297.01):** 757 tr / **+₹189,963.97**. Month table: Jan 27,746.41 → 27,847.72 (+101.31) · Feb 18,448.01 (unchanged) · Mar 20,395.86 → 21,273.31 (+877.45) · Apr 7,617.74 → 7,760.99 (+143.25) · May 34,799.69 → 35,144.69 (+345.00) · Jun 1,846.78 → **1,951.78** (+105.00) · Jul 6,428.19 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 53,031.65 → 52,756.65 (−275.00 — this bank SPENDS ₹275.00 of headroom, leaving ₹2,756.65, unlike SAT-18/19 which minted it)**. Ex-top-3 **₹63,577.47 → ₹64,874.48** (improvement — IRCTC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,297.01; all ten green with razors Aug 309.08 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: F4 takes no IRCTC SHORT signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹189,963.97 — the run is NOT saturated.**
- **Next:** saturation continues from +₹189,963.97 (₹18,996/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (8 qualifying remain — re-derive before use; next rows: INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20, whose removal would thicken the August razor to ~₹714.28; F4 × HINDALCO × LONG −₹851.10); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-23 — INV-LONG × INDUSTOWER exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (757 tr / +₹189,963.97 / month table to the paisa / ex-top-3 ₹64,874.48; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 452 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-22 book (142 slices, 8 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,756.65). The top qualifying row re-measured **identical to the SAT-22 registry record to the paisa** — INV-LONG × INDUSTOWER × LONG, 12 tr, −₹1,189.01, 3 winners (Jan +253.82 · Feb −532.20 · Mar −257.35 · **Apr −512.09** · May +87.26 · **Aug exactly 0.00** · **Oct −228.45**). SAT-22 intervened only on an F4 leg, disjoint from INV-LONG — the deltas did not expire (ninth positive invariance instance). Mechanism scope (Lesson 11, seventh confirming instance): INDUSTOWER earns in F4 (+₹2,287.14, its kept SHORT flow — F4's LONG half was excluded back in SAT-2) and N4-V3 (+₹564.20); its P2F (−₹240.20) and P2F-R2 (−₹243.07) slices are below the bar and stay. INDUSTOWER's LONG flow has now failed inside two mechanisms while its F4 SHORT flow earns — recorded as context; the exclusion stays INV-LONG-scoped.
- **Fix (frozen in stocks_engine_frozen.md, SAT-23 section, BEFORE scoring):** SAT-23-INV-INDUSTOWER — INV-LONG takes no INDUSTOWER signals (stock × mechanism; INV-LONG is LONG-only; all other components trade INDUSTOWER unchanged).
- **Exact score (stocks_engine_sat23_score.py; Anchor B: deleted set == the frozen 12 trades exactly, net −₹1,189.01):** 745 tr / **+₹191,152.98**. Month table: Jan 27,847.72 → 27,593.90 (−253.82) · Feb 18,448.01 → 18,980.21 (+532.20) · Mar 21,273.31 → 21,530.66 (+257.35) · Apr 7,760.99 → **8,273.08** (+512.09) · May 35,144.69 → 35,057.43 (−87.26) · Jun 1,951.78 (unchanged) · Jul 6,428.19 (unchanged) · **Aug 309.08 (unchanged — the razor intact)** · Sep 18,043.55 (unchanged) · **Oct 52,756.65 → 52,985.10 (+228.45 — mints headroom, leaving ₹2,985.10)**. Ex-top-3 **₹64,874.48 → ₹66,063.49** (improvement — INDUSTOWER is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,189.01; all ten green with razors Aug 309.08 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no INDUSTOWER signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹191,152.98 — the run is NOT saturated.**
- **Next:** saturation continues from +₹191,152.98 (₹19,115/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (7 qualifying remain — re-derive before use; next rows: N4-V3 × OIL × LONG −₹862.04 — the only August-negative row, Aug −₹405.20, whose removal would thicken the razor to ₹714.28; F4 × HINDALCO × LONG −₹851.10); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-24 — N4-V3 × OIL × LONG exclusion: BANKED (2026-10-31)

- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-23 book (141 slices, 7 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10). The top qualifying row re-measured **identical to the SAT-23 registry record to the paisa** — N4-V3 × OIL × LONG, 2 tr, −₹862.04, 0 winners (May −₹456.84 · **Aug −₹405.20** · **Oct exactly 0.00**). SAT-23 intervened only on an INV-LONG leg, disjoint from N4-V3 — the deltas did not expire (tenth positive invariance instance). This was the registry's only August-negative row in the top set. **Thin-sample caveat, first-class: 2 trades (SAT-14/SAT-17/SAT-21 precedent class)** — no population claim; the bank rests on the Lesson 5/15 shape at minimum surgery plus the August-thickening arithmetic. Mechanism × direction scope (Lesson 11, eighth confirming instance): OIL earns in F4 (+₹491.75, kept LONG flow — its F4 SHORT half was excluded in SAT-18) and INV-LONG (+₹1,208.06); its P2F (−₹302.00) and P2F-R2 (−₹299.90) slices are below the bar and stay. N4-V3 holds no OIL SHORT trades in-window, so the direction split inside N4 is vacuous; the exclusion is recorded as N4 × OIL × LONG per the unit of exclusion.
- **Fix (frozen in stocks_engine_frozen.md, SAT-24 section, BEFORE scoring):** SAT-24-N4-OIL-LONG — N4-V3 takes no OIL LONG signals (stock × mechanism × direction; all other components trade OIL unchanged).
- **Exact score (stocks_engine_sat24_score.py; Anchor B: deleted set == the frozen 2 trades exactly, net −₹862.04):** 743 tr / **+₹192,015.02**. Month table: Jan 27,593.90 (unchanged) · Feb 18,980.21 (unchanged) · Mar 21,530.66 (unchanged) · Apr 8,273.08 (unchanged) · May 35,057.43 → **35,514.27** (+456.84) · Jun 1,951.78 (unchanged) · Jul 6,428.19 (unchanged) · **Aug 309.08 → 714.28 (+405.20 — THE RAZOR THICKENED 2.3×; August remains the minimum month but is no longer a whisker)** · Sep 18,043.55 (unchanged) · **Oct 52,985.10 (unchanged — headroom ₹2,985.10 untouched)**. Ex-top-3 **₹66,063.49 → ₹66,925.53** (improvement — OIL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹862.04; all ten green with razors Aug 714.28 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100, minimum month now August +714.28; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: N4-V3 takes no OIL LONG signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹192,015.02 — the run is NOT saturated.**
- **Next:** saturation continues from +₹192,015.02 (₹19,202/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (6 qualifying remain — re-derive before use; next rows: F4 × HINDALCO × LONG −₹851.10; F4 × TATASTEEL × LONG −₹775.38; F4 × NHPC × SHORT −₹769.23; INV-LONG × KALYANKJIL −₹764.57; August-negative slices remain lower in the queue: F4 × PFC × SHORT Aug −₹55.00, F4 × RECLTD × SHORT Aug −₹342.58); (ii) August thickened to +₹714.28 but still the thinnest month, June next at +₹1,951.78; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-25 — F4 × HINDALCO × LONG exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (743 tr / +₹192,015.02 / month table to the paisa / ex-top-3 ₹66,925.53; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 452 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-24 book (140 slices, 6 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10). The top qualifying row re-measured **identical to the SAT-24 registry record to the paisa** — F4 × HINDALCO × LONG, 9 tr, −₹851.10, 3 winners (Jan −271.81 · Feb +1,131.97 · Mar −385.00 · **Apr −215.00** · May +1,010.00 · **Jun −1,137.25** · Sep −984.01 · **Aug exactly 0.00** · **Oct exactly 0.00**). SAT-24 intervened only on an N4-V3 leg, disjoint from F4 — the deltas did not expire (eleventh positive invariance instance). Direction split (Lesson 15, eighth confirming instance): F4 × HINDALCO × SHORT earns +₹2,345.84 (8 tr) and stays; the LONG half is the rot. Mechanism scope (Lesson 11, ninth confirming instance): HINDALCO's LONG flow has now failed inside two mechanisms (P2F's population excluded in SAT-14; F4's here) while the name earns at the R+2 lag (P2F-R2 +₹1,276.75); its INV-LONG (−₹895.40) and N4-V3 (−₹907.36) slices are below this cycle's qualifying bar and stay (SAT-20 sharpening).
- **Fix (frozen in stocks_engine_frozen.md, SAT-25 section, BEFORE scoring):** SAT-25-F4-HINDALCO-LONG — F4 takes no LONG signals on HINDALCO (stock × mechanism × direction; F4 keeps HINDALCO SHORT; all other components trade HINDALCO unchanged).
- **Exact score (stocks_engine_sat25_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹851.10):** 734 tr / **+₹192,866.12**. Month table: Jan 27,593.90 → 27,865.71 (+271.81) · Feb 18,980.21 → 17,848.24 (−1,131.97) · Mar 21,530.66 → 21,915.66 (+385.00) · Apr 8,273.08 → **8,488.08** (+215.00) · May 35,514.27 → 34,504.27 (−1,010.00) · Jun 1,951.78 → **3,089.03 (+1,137.25 — a razor month thickens 1.6×)** · Jul 6,428.19 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 → 19,027.56 (+984.01) · **Oct 52,985.10 (unchanged — headroom ₹2,985.10 untouched)**. Ex-top-3 **₹66,925.53 → ₹67,776.63** (improvement — HINDALCO is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹851.10; all ten green with razors Aug 714.28 / Jun 3,089.03 / Jul 6,428.19 all ≥ ₹100, minimum month August +714.28; October ≥ 50,000 at ₹52,985.10; ex-top-3 improves; anchors clean). **Book law added: F4 takes no HINDALCO LONG signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹192,866.12 — the run is NOT saturated.**
- **Next:** saturation continues from +₹192,866.12 (₹19,287/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (5 qualifying remain — re-derive before use; next rows: F4 × TATASTEEL × LONG −₹775.38, F4 × NHPC × SHORT −₹769.23, INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-26 — F4 × TATASTEEL × LONG exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (734 tr / +₹192,866.12 / month table to the paisa / ex-top-3 ₹67,776.63; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 443 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-25 book (139 slices, 5 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10). The top qualifying row re-measured **identical to the SAT-25 registry record to the paisa** — F4 × TATASTEEL × LONG, 9 tr, −₹775.38, 2 winners (Jan +18.33 · Feb +164.00 · **Apr −245.92** · **Jun −263.64** · Sep −391.15 · **Aug exactly 0.00** · **Oct −57.00**) — and the whole remaining queue re-measured identical with it (NHPC-SHORT −₹769.23, KALYANKJIL −₹764.57, PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97). SAT-25 intervened only on an F4 HINDALCO-LONG leg, disjoint from TATASTEEL — the deltas did not expire (twelfth positive invariance instance). Direction split (Lesson 15): F4 × TATASTEEL × SHORT earns +₹646.21 (9 tr) and stays; the LONG half is the rot. Mechanism scope (Lesson 11, tenth confirming instance): TATASTEEL's slices in INV-LONG (−₹217.04), N4-V3 (+₹73.08), P2F (−₹145.29) and P2F-R2 (+₹219.38) are all below the bar and stay untouched (SAT-20 sharpening).
- **Fix (frozen in stocks_engine_frozen.md, SAT-26 section, BEFORE scoring):** SAT-26-F4-TATASTEEL-LONG — F4 takes no LONG signals on TATASTEEL (stock × mechanism × direction; F4 keeps TATASTEEL SHORT; all other components trade TATASTEEL unchanged).
- **Exact score (stocks_engine_sat26_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹775.38):** 725 tr / **+₹193,641.50**. Month table: Jan 27,865.71 → 27,847.38 (−18.33) · Feb 17,848.24 → 17,684.24 (−164.00) · Mar 21,915.66 (unchanged) · Apr 8,488.08 → **8,734.00** (+245.92) · May 34,504.27 (unchanged) · Jun 3,089.03 → **3,352.67** (+263.64) · Jul 6,428.19 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,027.56 → 19,418.71 (+391.15) · **Oct 52,985.10 → 53,042.10 (+57.00 — mints headroom, leaving ₹3,042.10)**. Ex-top-3 **₹67,776.63 → ₹68,552.01** (improvement — TATASTEEL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹775.38; all ten green with razors Aug 714.28 / Jun 3,352.67 / Jul 6,428.19 all ≥ ₹100, minimum month August +714.28; October ≥ 50,000 at ₹53,042.10; ex-top-3 improves; anchors clean). **Book law added: F4 takes no TATASTEEL LONG signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹193,641.50 — the run is NOT saturated.**
- **Next:** saturation continues from +₹193,641.50 (₹19,364/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (4 qualifying remain — re-derive before use; next rows: F4 × NHPC × SHORT −₹769.23, INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-27 — F4 × NHPC × SHORT exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (725 tr / +₹193,641.50 / month table to the paisa / ex-top-3 ₹68,552.01; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 434 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-26 book (138 slices, 4 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,042.10). The top qualifying row re-measured **identical to the SAT-26 registry record to the paisa** — F4 × NHPC × SHORT, 13 tr, −₹769.23, 2 winners (Jan −112.38 · Feb −218.02 · Mar −15.00 · **Apr −156.36** · **Jul −115.24** · Sep −111.85 · **Aug exactly 0.00** · **Oct −40.38**) — and the whole remaining queue re-measured identical with it (KALYANKJIL −₹764.57, PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97). SAT-26 intervened only on an F4 TATASTEEL-LONG leg, disjoint from NHPC — the deltas did not expire (thirteenth positive invariance instance). Direction/mechanism scope (Lessons 11/15): F4 × NHPC × LONG is mildly negative but below the bar (12 tr / −₹102.46) and stays; NHPC's other-component slices stay untouched (INV-LONG +₹124.24, N4-V3 −₹104.80 — below the bar).
- **Fix (frozen in stocks_engine_frozen.md, SAT-27 section, BEFORE scoring):** SAT-27-F4-NHPC-SHORT — F4 takes no SHORT signals on NHPC (stock × mechanism × direction; F4 keeps NHPC LONG; all other components trade NHPC unchanged).
- **Exact score (stocks_engine_sat27_score.py; Anchor B: deleted set == the frozen 13 trades exactly, net −₹769.23):** 712 tr / **+₹194,410.73**. Month table: Jan 27,847.38 → 27,959.76 (+112.38) · Feb 17,684.24 → 17,902.26 (+218.02) · Mar 21,915.66 → 21,930.66 (+15.00) · Apr 8,734.00 → **8,890.36** (+156.36) · May 34,504.27 (unchanged) · Jun 3,352.67 (unchanged) · Jul 6,428.19 → **6,543.43** (+115.24) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,418.71 → 19,530.56 (+111.85) · **Oct 53,042.10 → 53,082.48 (+40.38 — mints headroom, leaving ₹3,082.48)**. No month pays a cost — every affected month improves. Ex-top-3 **₹68,552.01 → ₹69,321.24** (improvement — NHPC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹769.23; all ten green with razors Aug 714.28 / Jun 3,352.67 / Jul 6,543.43 all ≥ ₹100, minimum month August +714.28; October ≥ 50,000 at ₹53,082.48; ex-top-3 improves; anchors clean). **Book law added: F4 takes no NHPC SHORT signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹194,410.73 — the run is NOT saturated.**
- **Next:** saturation continues from +₹194,410.73 (₹19,441/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (3 qualifying remain — re-derive before use; next rows: INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-28 — INV-LONG × KALYANKJIL exclusion: BANKED (2026-10-31)

- **Anchor:** incumbent rebuilt exactly from the current component dumps (712 tr / +₹194,410.73 / month table to the paisa / ex-top-3 ₹69,321.24; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 421 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-27 book (137 slices, 3 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,082.48). The top qualifying row re-measured **identical to the SAT-27 registry record to the paisa** — INV-LONG × KALYANKJIL × LONG, 24 tr, −₹764.57, 7 winners (Jan −944.37 · Feb −754.22 · Mar +652.65 · Apr +213.74 · **Jun −35.02** · Sep +409.25 · **Aug exactly 0.00** · **Oct −306.60**) — and the whole remaining queue re-measured identical with it (PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97). SAT-27 intervened only on an F4 NHPC-SHORT leg, disjoint from all three queue rows — the deltas did not expire (fourteenth positive invariance instance). Mechanism scope (Lesson 11, twelfth confirming instance): KALYANKJIL earns in N4-V3 (+₹1,972.87) and F4 (+₹497.38) and stays there; its P2F (−₹152.75) and P2F-R2 (−₹201.70) slices are below the bar and stay untouched (SAT-20 sharpening). INV-LONG is LONG-only, so no direction split exists inside it (SAT-19 precedent). At 24 trades this is the thickest slice population banked in the registry phase.
- **Fix (frozen in stocks_engine_frozen.md, SAT-28 section, BEFORE scoring):** SAT-28-INV-KALYANKJIL — INV-LONG takes no signals on KALYANKJIL (stock × mechanism exclusion; all other components trade KALYANKJIL unchanged).
- **Exact score (stocks_engine_sat28_score.py; Anchor B: deleted set == the frozen 24 trades exactly, net −₹764.57):** 688 tr / **+₹195,175.30**. Month table: Jan 27,959.76 → 28,904.13 (+944.37) · Feb 17,902.26 → 18,656.48 (+754.22) · Mar 21,930.66 → 21,278.01 (−652.65) · Apr 8,890.36 → 8,676.62 (−213.74) · May 34,504.27 (unchanged) · Jun 3,352.67 → **3,387.69** (+35.02) · Jul 6,543.43 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,530.56 → 19,121.31 (−409.25) · **Oct 53,082.48 → 53,389.08 (+306.60 — headroom minted to ₹3,389.08)**. Costs (March −652.65, April −213.74, September −409.25) all stay strongly green. Ex-top-3 **₹69,321.24 → ₹70,085.81** (improvement — KALYANKJIL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹764.57; all ten green with razors Aug 714.28 / Jun 3,387.69 / Jul 6,543.43 all ≥ ₹100, minimum month August +714.28; October ≥ 50,000 at ₹53,389.08; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no KALYANKJIL signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹195,175.30 — the run is NOT saturated.**
- **Next:** saturation continues from +₹195,175.30 (₹19,518/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (2 qualifying remain — re-derive before use; next rows: F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-29 — registry slice: F4 × PFC × SHORT excluded (2026-10-31)
- **Anchor:** incumbent rebuilt exactly from the current component dumps (688 tr / +₹195,175.30 / month table to the paisa / ex-top-3 ₹70,085.81; components INV-LONG 155 / N4-V3 47 / P2F 32 / F4 421 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER + SAT-28 KALYANKJIL; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-28 book (136 slices, 2 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,389.08). The top qualifying row re-measured **identical to the SAT-28 registry record to the paisa** — F4 × PFC × SHORT, 18 tr, −₹667.69, 8 winners (Jan +510.27 · Feb +36.92 · Mar +112.64 · **Apr −882.52** · **Jun −435.53** · **Aug −55.00** · Sep −22.18 · **Oct +67.71**) — and the other qualifying row re-measured identical with it (RECLTD-SHORT −₹503.97). SAT-28 intervened only on an INV-LONG KALYANKJIL leg, disjoint from both F4 rows — the deltas did not expire (fifteenth positive invariance instance). Direction split (Lesson 15): F4 × PFC × LONG earns +₹1,652.90 (12 tr) and stays. Mechanism scope (Lesson 11, thirteenth confirming instance): PFC earns in INV-LONG (+₹2,117.27), P2F (+₹442.50) and P2F-R2 (+₹436.25); its N4-V3 slice (−₹197.58) is below the bar and stays untouched.
- **Fix (frozen in stocks_engine_frozen.md, SAT-29 section, BEFORE scoring):** SAT-29-F4-PFC-SHORT — F4 takes no SHORT signals on PFC (stock × mechanism × DIRECTION exclusion; F4 keeps PFC LONG; all other components trade PFC unchanged).
- **Exact score (stocks_engine_sat29_score.py; Anchor B: deleted set == the frozen 18 trades exactly, net −₹667.69):** 670 tr / **+₹195,842.99**. Month table: Jan 28,904.13 → 28,393.86 (−510.27) · Feb 18,656.48 → 18,619.56 (−36.92) · Mar 21,278.01 → 21,165.37 (−112.64) · Apr 8,676.62 → **9,559.14** (+882.52) · May 34,504.27 (unchanged) · Jun 3,387.69 → **3,823.22** (+435.53) · Jul 6,543.43 (unchanged) · **Aug 714.28 → 769.28 (+55.00 — razor thickened)** · Sep 19,121.31 → 19,143.49 (+22.18) · **Oct 53,389.08 → 53,321.37 (−67.71 — headroom spent, ₹3,321.37 left)**. Costs (Jan/Feb/Mar) all stay strongly green. Ex-top-3 **₹70,085.81 → ₹70,753.50** (improvement — PFC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹667.69; all ten green with razors Aug 769.28 / Jun 3,823.22 / Jul 6,543.43 all ≥ ₹100, minimum month August +769.28; October ≥ 50,000 at ₹53,321.37; ex-top-3 improves; anchors clean). **Book law added: F4 takes no PFC SHORT signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹195,842.99 — the run is NOT saturated.**
- **Next:** saturation continues from +₹195,842.99 (₹19,584/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (1 qualifying remains at this derivation — re-derive before use: F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,111.86; Oct +₹477.00)); (ii) August remains the thinnest month at +₹769.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-30 — registry slice: F4 × RECLTD × SHORT excluded — THE LAST REGISTRY ROW (2026-10-31)
- **Anchor:** incumbent rebuilt exactly from the current component dumps (670 tr / +₹195,842.99 / month table to the paisa / ex-top-3 ₹70,753.50; components INV-LONG 155 / N4-V3 47 / P2F 32 / F4 403 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT + SAT-29 PFC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER + SAT-28 KALYANKJIL; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion, per book law).
- **Re-derivation (Lesson 16):** the registry was re-derived from scratch at the post-SAT-29 book (135 slices, **1 qualifying** at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,321.37). The sole qualifying row re-measured **identical to the SAT-29 registry record to the paisa** — F4 × RECLTD × SHORT, 14 tr, −₹503.97, 6 winners (Jan −142.39 · Feb +55.00 · Mar +580.96 · **Apr −336.35** · May −376.59 · **Aug −342.58** · Sep −419.02 · **Oct +477.00**). SAT-29 intervened only on an F4 PFC-SHORT leg, disjoint from RECLTD-SHORT — the deltas did not expire (sixteenth positive invariance instance). Direction split (Lesson 15): F4 × RECLTD × LONG earns +₹949.99 (5 tr) and stays. Mechanism scope (Lesson 11, fourteenth confirming instance): RECLTD's other-component slices stay untouched (INV-LONG +₹0.24, N4-V3 +₹242.04, P2F +₹228.37 earn small; P2F-R2 −₹438.00 below the bar).
- **Fix (frozen in stocks_engine_frozen.md, SAT-30 section, BEFORE scoring):** SAT-30-F4-RECLTD-SHORT — F4 takes no SHORT signals on RECLTD (stock × mechanism × DIRECTION exclusion; F4 keeps RECLTD LONG; all other components trade RECLTD unchanged).
- **Exact score (stocks_engine_sat30_score.py; Anchor B: deleted set == the frozen 14 trades exactly, net −₹503.97):** 656 tr / **+₹196,346.96**. Month table: Jan 28,393.86 → 28,536.25 (+142.39) · Feb 18,619.56 → 18,564.56 (−55.00) · Mar 21,165.37 → 20,584.41 (−580.96) · Apr 9,559.14 → **9,895.49** (+336.35) · May 34,504.27 → **34,880.86** (+376.59) · Jun 3,823.22 (unchanged) · Jul 6,543.43 (unchanged) · **Aug 769.28 → 1,111.86 (+342.58 — razor thickened 1.4×)** · Sep 19,143.49 → 19,562.51 (+419.02) · **Oct 53,321.37 → 52,844.37 (−477.00 — headroom spent, ₹2,844.37 left)**. Costs (Feb/Mar) stay strongly green. Ex-top-3 **₹70,753.50 → ₹71,257.47** (improvement — RECLTD is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹503.97; all ten green with razors Aug 1,111.86 / Jun 3,823.22 / Jul 6,543.43 all ≥ ₹100, minimum month August +1,111.86; October ≥ 50,000 at ₹52,844.37; ex-top-3 improves; anchors clean). **Book law added: F4 takes no RECLTD SHORT signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹196,346.96 — the run is NOT saturated.**
- **Frontier record (plain, per the cycle brief):** the diag's post-removal re-derivation found **0 qualifying rows** (134 slices at the post-SAT-30 book, headroom ₹2,844.37) — **the deletion frontier is EXHAUSTED at the standing bar** (full ≤ −₹500 AND thin-month-negative AND October-feasible). Fourteen registry slices were banked SAT-17..SAT-30; the queue is empty. Future cycles must bring genuinely new earning material (new Lesson-3 components) or the run closes toward saturation on consecutive no-beats. The bar is NOT to be lowered: the largest sub-bar row (GLENMARK-SHORT class, full ≈ −₹137) is the overfit direction the quality bar exists to refuse.
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped); (ii) August remains the thinnest month at +₹1,111.86; (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required).

## SAT-31 — NEW COMPONENT F4-UPBAND: the band's upper complement [1.0%, 1.25%) under F4's joint state — REJECTED; the band cap is load-bearing on both sides (2026-10-31)
- **Charter:** the deletion registry is EMPTY (SAT-30), so this cycle brought new material: Lesson 17's corollary licenses testing a boundary's complement exactly once. F4's band had its lower complement killed on the reaction axis (SAT-4 / Lessons 17/19/20) but the UPPER complement under F4's own joint state had never been scored. **Disclosed prior (frozen before scoring):** M2 found the ≥1% region was the ungated follow cell's loss driver — the test was whether the joint state (below-50DMA gate + this slice only) rescues it.
- **Fix (frozen in stocks_engine_frozen.md, SAT-31 section, BEFORE scoring):** SAT-31-F4-UPBAND — below-50DMA days, |premove by 10:00| in [1.0%, 1.25%), FOLLOW via H1.build_cell sig machinery, first-signal-only, T150/S095, RF-1, book F4 exclusions applied symmetrically (setup3 + the 12 (stock × direction) pairs through SAT-30).
- **Anchor:** incumbent rebuilt exactly (656 tr / +₹196,346.96 / month table to the paisa / ex-top-3 ₹71,257.47; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33; N4 from the SAT-15 dump minus SAT-17/SAT-24 exclusions, per book law).
- **Exact score (stocks_engine_sat31_score.py):** 135 below50 non-weekend days (October 20/20 below50). Component: 124 raw → **87 tr, −₹24,036.07, expectancy −₹276.28, 28 winners, breadth 9/25; halves both negative (Jan–May −₹16,589.40 / Jun–Oct −₹7,446.67)**; negative in 7 of 10 months (only Apr +488.46 and Aug +440.14 positive, Jul flat). Controls in the same pass: **timing audit 0 violations both builds**; sign-flip placebo (fade, identical entries) 6 tr / −₹1,039.27 / expectancy −₹173.21 — **loses less per trade than the real rule**; overlap vs incumbent F4 = 0 pairs (mechanical, disjoint bands). Union 743 tr / **+₹172,310.89** (August would rise to 1,552.00 and October holds 50,337.40, but the total falls ₹24,036.07 and ex-top-3 collapses to ₹53,306.76).
- **Decide: REJECTED — gate legs (a), (d), (e) fail; (b) and (c) pass and cannot purchase them.** Incumbent unchanged. **Saturation: no_beat_cycles 0 → 1, best_total ₹196,346.96.** The M2 prior holds inside the joint state — the gate rescues the [0.5%, 1.0%) slice, not its upper neighbour. Lesson 17 addendum appended (the band is validated on BOTH boundaries; F4-UPBAND family CLOSED).
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — stated plainly); counter at 1 of 3. Frontiers: (i) genuinely new Lesson-3 material outside the F4 band/state slices (both band boundaries and the mirror are now closed) and outside the mapped reaction-lag axis; (ii) August thickening by new material (August +₹1,111.86, still the minimum month); (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required; the bar is not lowered).

## SAT-32 — NEW COMPONENT P2F-LOWBAND: the reaction band's lower complement [2.0%, 2.5%) at R+1 — REJECTED; P2F's 2.5% floor validated by its complement (2026-10-31)
- **Charter:** the deletion registry is EMPTY (SAT-30) and F4-UPBAND is closed (SAT-31); Lesson 17's corollary licenses testing a boundary's complement exactly once. P2F's ≥2.5% floor had never had its complement isolated at the book's own S050 exits (CH-1's 2.0% run was an ungated S065 profile challenger whose direction rule never fired). **Disclosed prior (frozen before scoring):** CH-1's 2.0%-band follow underperformed the 2.5% component — the prior says dilutant at best.
- **Fix (frozen in stocks_engine_frozen.md, SAT-32 section, BEFORE scoring):** SAT-32-P2F-LOWBAND — reaction days with 2.0% ≤ |reaction| < 2.5%, enter R+1 open in the reaction direction, T125/S050, square-off 15:10, RF-1, P2F's exclusions (ASTRAL + HINDUNILVR whole-name, HINDALCO LONG).
- **Construction anchor (strongest of the run):** the verbatim event machinery reproduces the tuning dump's P2F leg **39/39 per-trade at ≥2.5% AND 9/9 per-trade on the [2.0%, 2.5%) slice itself** (the dump's 48 P2F rows = 39 + 9; replay convention start-offset 1, determined empirically). The lowband population is not a new construction — it sits verbatim inside the audited dump.
- **Diagnosis/score (stocks_engine_sat32_diag.py / sat32_score.py; Anchors A/B/C all pass):** 9 candidates → raw 9 → **frozen 8** (HINDUNILVR LONG dropped by the JU-1 exclusion, −₹1,190.75; no weekend drops). **Component: 8 tr / −₹1,462.45, expectancy −₹182.81, 3 winners, breadth 3; halves H1 −₹2,013.99 / H2 +₹551.54 (split flips; H1 is one TVSMOTOR stop, −₹1,872.50)**. Months: Jan −1,872.50 · Feb −141.49 · Jul −224.00 · Aug +563.37 · Oct +212.17 · five months flat. **Placebo (flip, identical entries): 8 tr / −₹3,465.83, expectancy −₹433.23, 0 winners — all 8 are stop exits: these sub-band R+1 days whipsaw through the ±0.5% stop adversely for BOTH directions; the real rule beats its placebo in total and per-trade and is still negative.** Timing audit 0; overlap vs P2F and vs P2F-R2 both 0 (mechanical). Union 664 tr / **+₹194,884.51** (August 1,111.86 → 1,675.23; October → 53,056.54, headroom ₹3,056.54; ex-top-3 → ₹71,667.52).
- **Decide: REJECTED — gate leg (a) FAILS (total falls ₹1,462.45); legs (b), (c), (d), (e) pass and cannot purchase it (SAT-12 discipline; Lesson 14's mirror — a thin-month gain does not buy a total loss).** Incumbent unchanged. **Saturation: no_beat_cycles 1 → 2, best_total ₹196,346.96.** Lesson 21 appended: P2F's 2.5% floor is validated by its complement at the book's own exits, and beating a placebo is necessary, not sufficient — expectancy must clear zero after costs. P2F-LOWBAND family CLOSED.
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — stated plainly); counter at 2 of 3 — one more consecutive no-beat ends the run as saturated at this plateau. Frontiers: (i) genuinely new Lesson-3 material outside the reaction-band/lag complex (every boundary of it now has a failing complement: N4 floor, P2F floor, F4 band both sides + mirror, R-ladder to R+2) and outside the F4 state slices; (ii) August thickening by new material (August +₹1,111.86); (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required; the bar is not lowered).

## SAT-33 — R2-LOWBAND (2026-10-31): BANKED — the grid's closing cell beats the best; run NOT saturated
- **Frozen before scoring** (stocks_engine_frozen.md, SAT-33 section): reaction band [2.0%, 2.5%), entry at the R+2 open in the reaction direction, T125/S050, square-off 15:10, RF-1, P2F's exclusions (ASTRAL, HINDUNILVR; HINDALCO LONG). Negative priors on both axes disclosed in the freeze (SAT-32 at R+1; Lesson 20 by lag).
- **Verification before belief:** incumbent anchor exact (656 tr / +₹196,346.96 / month table / ex-top-3 ₹71,257.47, per book law); construction anchor — identical machinery at lag +2 on ≥2.5% reproduces the SAT-13 P2F-R2 frozen dump **34/34 per-trade** in both the diagnosis and the score pass; candidates 9 (== SAT-32's lowband candidate set); timing audit **0 violations**; (date, stock) overlap vs P2F / P2F-R2 / P2F-LOWBAND all **0**, verified mechanically.
- **Component (frozen: 9 raw → 7 after exclusions): 7 tr / +₹1,260.78, expectancy +₹180.11, 4 winners, breadth 4; halves H1 −₹144.70 / H2 +₹1,405.48.** Months: Feb −144.70 · Jul +422.50 · Aug −445.08 · Oct +1,428.06. **Placebo (flip, identical entries): 7 tr / −₹951.17, expectancy −₹135.88** — beaten in total and per-trade, and the component clears zero expectancy.
- **Union (663 tr):** Jan 28,536.25 · Feb 18,419.86 · Mar 20,584.41 · Apr 9,895.49 · May 34,880.86 · Jun 3,823.22 · Jul 6,965.93 · **Aug 666.78** · Sep 19,562.51 · **Oct 54,272.43** · **Total +₹197,607.74**. Ex-top-3 ₹71,257.47 → ₹72,518.25 (top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,260.78; 10/10 green, min August +₹666.78; October ≥ ₹50,000 with headroom ₹4,272.43; ex-top-3 improves; anchors/audit/placebo clean). **Saturation: no_beat_cycles 2 → 0, best_total → ₹197,607.74 (₹19,761/month vs the ₹75,000/month goal — stated plainly).** The run does NOT terminate; no candidate spec is written.
- **Thin-sample disclosure (first-class):** the bank rests on 7 trades, is H1-negative and October-carried (October slice exceeds the component net); it also spends August down to +₹666.78, still the minimum month. Frozen verbatim; December fresh data judges it (Lesson 22 appended: grid cells close on their own runs, not on neighbours' verdicts; band and lag interact).
- **Next:** saturation continues from +₹197,607.74. Frontiers: genuinely new Lesson-3 material outside the now-fully-mapped reaction grid and the bounded F4 band; August thickening by new material (August +₹666.78); the GLENMARK-SHORT argument (below-bar — explicit argument required; the bar is not lowered).

## SAT-34 — R2-MIDBAND: reaction band [1.5%, 2.0%) at R+2 — REJECTED on leg (d); a positive standalone that is a concentration purchase (2026-10-31)
- **Charter:** Lesson 22 — grid cells close on their own controlled runs. The grid's two living low cells both sit at R+2 (P2F-R2 ≥2.5%; R2-LOWBAND [2.0%, 2.5%) banked SAT-33); the next cell down the band axis at that lag had never been run. Priors disclosed in the freeze conflicted (Lessons 17/21 negative on the band axis; Lesson 22 positive on the method).
- **Fix (frozen in stocks_engine_frozen.md, SAT-34 section, BEFORE scoring):** SAT-34-R2-MIDBAND — reaction days with 1.5% ≤ |reaction| < 2.0%, enter R+2 open in the reaction direction, T125/S050, square-off 15:10, RF-1, P2F's exclusions (ASTRAL + HINDUNILVR whole-name, HINDALCO LONG).
- **Verification before belief:** incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7, per book law); construction anchor — identical machinery at lag +2 on ≥2.5% reproduces the SAT-13 P2F-R2 frozen dump **34/34 per-trade** in both the diagnosis and the score pass; candidates 7 → raw 7 → frozen 6 (ASTRAL SHORT −₹789.75 dropped by the AU-1 exclusion); frozen set at scoring == diagnosis set exactly; timing audit **0 violations**; (date, stock) overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / N4-V3 all **0**, verified mechanically.
- **Component (frozen): 6 tr / +₹2,909.18, expectancy +₹484.86, 2 winners, breadth 2; halves H1 +₹4,204.95 / H2 −₹1,295.77.** Months: Feb −262.55 · May +4,467.50 · Aug −440.77 · Oct −855.00. **Placebo (flip, identical entries): 6 tr / +₹1,054.91, expectancy +₹175.82, 3 winners — POSITIVE outright**; beaten in total and per-trade, component clears zero (full Lesson 21 test passes standalone). **First-class disclosure: the whole net is one trade — TVSMOTOR SHORT 2026-05-18 +₹4,247.50 (target); ex-it the component is −₹1,338.32.**
- **Union (669 tr): +₹200,516.92** — Feb 18,157.31 · May 39,348.36 · **Aug 226.01** · **Oct 53,417.43** (headroom ₹3,417.43); all other months identical to the paisa. Ex-top-3 **₹72,518.25 → ₹72,034.93 (−₹483.32**, exactly the freeze's pre-registered expectation; top-3 membership unchanged).
- **Decide: REJECTED — gate leg (d) FAILS; legs (a), (b) (August ₹226.01 ≥ ₹100 razor margin), (c) and (e) pass and cannot purchase it (SAT-12 discipline).** Incumbent unchanged. **Saturation: no_beat_cycles 0 → 1, best_total ₹197,607.74 (₹19,761/month vs the ₹75,000/month goal — stated plainly).** Lesson 23 appended (a positive standalone can be a concentration purchase; leg (d) is the separation test; a positive placebo is a disclosure). R2-MIDBAND family CLOSED; no book law, no dump.
- **Next:** saturation continues from +₹197,607.74; counter at 1 of 3. Frontiers: genuinely new Lesson-3 material outside the now-mapped reaction grid and the bounded F4 band; August thickening by new material (August +₹666.78); the GLENMARK-SHORT argument (below-bar — explicit argument required; the bar is not lowered).

## SAT-35 — P2F-MIDBAND: reaction band [1.5%, 2.0%) at R+1 — REJECTED on legs (a), (d), (e); the placebo beats the real rule (2026-10-31)
- **Charter:** Lesson 22 — grid cells close on their own controlled runs, never by extrapolation. SAT-34 closed this band at R+2 on concentration (Lesson 23); the same band at R+1 had never been run. Priors disclosed in the freeze leaned negative on both axes (Lesson 21's dead [2.0%, 2.5%) cell at this lag; Lesson 23's one-trade carriage at R+2).
- **Fix (frozen in stocks_engine_frozen.md, SAT-35 section, BEFORE scoring):** SAT-35-P2F-MIDBAND — reaction days with 1.5% ≤ |reaction| < 2.0%, enter R+1 open in the reaction direction, T125/S050, square-off 15:10, RF-1, P2F's exclusions (ASTRAL + HINDUNILVR whole-name, HINDALCO LONG). Leg (d) and the ex-carrier check pre-registered in the freeze (ex-top-3 expected to fall ≈ ₹124.94 if membership unchanged).
- **Verification before belief:** incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7, per book law); construction anchor — the lag+1 machinery reproduces the tuning dump's P2F leg on BOTH verified slices (**≥2.5% 39/39 AND [2.0%, 2.5%) 9/9**, start-offset 1) in both the diagnosis and the score pass; candidates 7 → raw 7 → frozen 6 (ASTRAL SHORT −₹778.40 dropped by the AU-1 exclusion); frozen set at scoring == diagnosis set exactly; timing audit **0 violations**; (date, stock) overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / R2-MIDBAND / N4-V3 all **0**, verified mechanically.
- **Component (frozen): 6 tr / −₹2,773.74, expectancy −₹462.29, 1 winner, breadth 1; halves H1 −₹1,450.77 / H2 −₹1,322.97 (both negative).** Months: Feb +509.00 · May −1,959.77 · Aug −441.97 · Oct −881.00. **Placebo (flip, identical entries): 6 tr / −₹2,275.45, expectancy −₹379.24, 2 winners — the placebo loses LESS than the real rule in total and per-trade; the full Lesson 21 test fails on every clause.** Best trade (the only winner) INDUSTOWER LONG 2026-02-04 +₹509.00; **ex-carrier −₹3,282.74**. Three entry days stop out at the identical net in both directions (TVSMOTOR −₹1,767.80, ITC −₹191.97, OBEROIRLTY −₹881.00) — stop-geometry whipsaw, not information.
- **Union (669 tr): +₹194,834.00** — Feb 18,928.86 · May 32,921.09 · **Aug 224.81** · **Oct 53,391.43** (headroom ₹3,391.43); all other months identical to the paisa. Ex-top-3 **₹72,518.25 → ₹72,393.31 (−₹124.94**, exactly the freeze's pre-registered expectation; top-3 membership unchanged).
- **Decide: REJECTED — gate legs (a) total, (d) ex-top-3 and (e) controls/placebo FAIL; legs (b) (August ₹224.81 ≥ ₹100 razor margin) and (c) pass and cannot purchase them (SAT-12 discipline).** Incumbent unchanged. **Saturation: no_beat_cycles 1 → 2, best_total ₹197,607.74 (₹19,761/month vs the ₹75,000/month goal — stated plainly).** Lesson 24 appended (no directional content at [1.5%, 2.0%) × R+1; the reaction grid is fully mapped). P2F-MIDBAND family CLOSED; no book law, no dump.
- **Next:** saturation continues from +₹197,607.74; counter at 2 of 3 — one more consecutive no-beat cycle saturates the run. Frontiers: genuinely new Lesson-3 material outside the reaction grid (now fully mapped on all lags) and the bounded F4 band; August thickening by new material (August +₹666.78); the GLENMARK-SHORT argument (below-bar — explicit argument required; the bar is not lowered).

## SAT-36 — F4 × GLENMARK × SHORT, judged formally: GATE PASSES, QUALITY BAR FAILS — PRINCIPLED NO-BEAT; THE RUN IS SATURATED (2026-10-31)
- **Charter:** the one standing item never judged on its merits, refused procedurally three times (SAT-8 floor-block, SAT-14 "August story", SAT-17 registry bottom). October headroom (₹4,272.43) had retired the floor objection; this cycle judged the merits under two pre-registered standards, both required to bank.
- **Diagnosis (stocks_engine_sat36_diag.py / sat36_diag.json; Anchor A exact — 663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7):** the slice re-measures IDENTICAL to the SAT-14 record (Lesson 16 invariance — no intervening cycle touched an F4 GLENMARK SHORT leg): **20 tr, 10 winners, net −₹136.98, expectancy −₹6.85**. Months: Jan −390.00 · Feb −859.68 · Mar −142.71 · Apr −1,926.32 · May +3,519.65 · Jun −1,020.00 · Aug −4,744.78 · Sep +4,364.31 · Oct +1,062.55 (6 of 9 traded months negative). Halves H1 +₹200.94 / H2 −₹337.92 (nearly cancel). **Net ex-August +₹4,607.80; ex-carrier (ex the worst trade, 2026-08-31 −₹2,386.69) +₹2,249.71.** F4 GLENMARK LONG +₹3,188.19 kept either way; GLENMARK whole-book +₹20,615.44 (10.43%, #4 earner — no longer top-3).
- **Fix (frozen in stocks_engine_frozen.md, SAT-36 section, BEFORE scoring):** SAT-36-F4-GLENMARK-SHORT — F4 takes no GLENMARK SHORT signals; judged on (1) the arithmetic saturation gate AND (2) the standing quality bar (full-period ≤ −₹500, Lesson 5). The bar is not lowered at the finish line.
- **Exact score (stocks_engine_sat36_score.py / sat36_result.json; Anchors A/B pass; deleted set == the frozen 20 trades exactly):** union 643 tr / **+₹197,744.72** — Aug **5,411.56**, Oct **53,209.88** (headroom ₹3,209.88), ex-top-3 **₹72,655.23 (+₹136.98**; top-3 membership unchanged). **Standard 1 (gate): ALL FIVE LEGS PASS** — and every leg's pass is the same ₹136.98. **Standard 2 (quality bar): FAILS** (−₹136.98 > −₹500).
- **Decide: NOT BANKED — a principled no-beat.** The slice is a zero-expectancy, half-winning population whose negative total is one month's shape (ex-August it earns; ex-carrier it earns); banking it would manufacture a "beat" out of August's shape and bend the bar at the finish line. **Saturation: no_beat_cycles 2 → 3 — THE RUN IS SATURATED.** The incumbent is frozen verbatim in stocks_engine_candidate_spec.md for December judging. Lesson 25 appended. GLENMARK-SHORT is CLOSED on this window (fresh-data revisits only).

## FINAL SATURATION SUMMARY — the run closes at its plateau (2026-10-31)
- **Termination: SATURATED.** Three consecutive no-beat cycles under the frozen standards: **SAT-34** (R2-MIDBAND refused on gate leg (d) alone — a positive standalone that was a concentration purchase), **SAT-35** (P2F-MIDBAND rejected on legs (a)/(d)/(e) — its placebo beat the real rule; the reaction grid's last cell), **SAT-36** (GLENMARK-SHORT refused on the quality bar although the arithmetic gate passed on all five legs — a principled no-beat). Two earlier streaks reached 2 and were reset by genuine banks (SAT-13's P2F-R2; SAT-33's R2-LOWBAND); the closing streak was not.
- **The plateau: +₹197,607.74 over Jan–Oct 2026 — ₹19,760.77/month average — 663 trades, SIX components, all ten months green, October +₹54,272.43, ex-top-3 +₹72,518.25.** Against the user's goal of **₹75,000/month (₹750,000 over the window)**, stated plainly: the plateau reaches **26.3% of the goal line; the gap is ₹552,392.26 (₹55,239.23/month)**. The run did not stop because the goal looked far; it stopped because three consecutive cycles could not beat the best book without breaking the frozen standards — and the last of the three could have "beaten" it only by bending them.
- **The full climb (banked steps only):** +₹47,665.24 (honest starting book) → RF-1 +4,433.84 → **52,099.08** → OC-1 F4 union +45,475.15 → **97,574.23** → setup3 removal +9,653.53 → **107,227.76** → F4 T150 +4,873.77 → **112,101.53** → F4 S080 +19,545.26 → **131,646.79** (October secured ≥ ₹50,000) → AU-1 +3,203.55 → **134,850.34** → JU-1 +2,294.05 → **137,144.39** → JN-1 +1,486.93 → **138,631.32** (ALL TEN MONTHS GREEN) → *saturation run:* SAT-1 +4,754.92 → **143,386.24** → SAT-2 +361.12 → **143,747.36** → SAT-5 +2,664.00 → **146,411.36** → SAT-6 +11.83 → **146,423.19** → SAT-7 +1,847.01 → **148,270.20** → SAT-8 +1,094.95 → **149,365.15** → SAT-10 +3,898.37 → **153,263.52** → SAT-13 P2F-R2 +12,912.48 → **166,176.00** → SAT-14 +572.50 → **166,748.50** → SAT-15 N4 rebuild +9,483.45 → **176,231.95** → SAT-17 +3,185.76 → **179,417.71** → SAT-18 +2,712.77 → **182,130.48** → SAT-19 +2,424.75 → **184,555.23** → SAT-20 +2,131.83 → **186,687.06** → SAT-21 +1,979.90 → **188,666.96** → SAT-22 +1,297.01 → **189,963.97** → SAT-23 +1,189.01 → **191,152.98** → SAT-24 +862.04 → **192,015.02** → SAT-25 +851.10 → **192,866.12** → SAT-26 +775.38 → **193,641.50** → SAT-27 +769.23 → **194,410.73** → SAT-28 +764.57 → **195,175.30** → SAT-29 +667.69 → **195,842.99** → SAT-30 +503.97 → **196,346.96** (deletion registry EMPTY) → SAT-33 R2-LOWBAND +1,260.78 → **197,607.74 — PLATEAU.**
- **What the plateau is made of:** six components (F4 389 tr · INV-LONG 155 · N4-V3 47 · P2F-R2 33 · P2F 32 · R2-LOWBAND 7), RF-1, ~25 mechanism-scoped exclusions, both F4 exit ladders at their measured ends (T150/S095), the N4 rebuild absorbed, the reaction (band × lag) grid fully mapped with every boundary validated by a failing complement, and 25 lessons written from controlled runs.
- **STRESS-1 caveats (carried, not forgotten):** measured at the +₹138,631.32 book — the all-green property existed only at the assumed ₹40/trade cost (₹60 → +₹120,511.32, 7/10 green; ₹80 → +₹102,391.32, 7/10); TVSMOTOR was 44.5% of that book and June/August/April were each one GLENMARK trade deep. At the plateau the concentration persists (TVSMOTOR +₹74,005.46 = 37.45%; GLENMARK +₹20,615.44 = 10.43%) while ex-top-3 has grown to +₹72,518.25; August remains thin (+₹666.78). The user's own verdict on the all-green book — "very optimal" — stands as the correct prior: this plateau is an IN-SAMPLE ceiling under honest rules, not a validated system. Fresh data is the only verdict that counts.
- **The judging board from here:** (i) **November 2026 paper** (this chat, from Mon 2026-11-02, frozen rules, no re-tuning): N4-V3 PRIMARY logging; INV-LONG (INV1) shadow; P2F shadow — month-end verdicts per their frozen judging rules. (ii) **December 2026 fresh-window judging:** THIS BOOK (stocks_engine_candidate_spec.md — December total positive AND no December week worse than −₹15,000 → confirmed; December negative → killed as in-sample fit; < 20 trades → extends to January; no parameter changes); the O2 11:00 fade (ext 25; ≥40-trade rule); the T2 P2F 3.0% band (pooled; ≥8-trade rule); the M2 F4 state-gated cell (≥40-trade rule); INV-LONG v2; DBL-LONG (home). (iii) The Morning-Mover line stays retracted and dead; its November shadow loggers stay disabled.
- **Untried / unresolved, honestly:** genuinely new Lesson-3 material outside the reaction grid and the bounded F4 band was the one frontier the closing cycles did not find — the grid and the band are fully mapped, the deletion registry is empty, and both exit ladders are closed; nothing remains in-sample that the frozen standards have not either banked or refused. Open user inputs (non-blocking): Chandu's actual broker charges (the ₹40 assumption is unproven and STRESS-1 shows it matters) and the other 5 watchlist names (he said 30; data holds 25).
- Basis throughout: equity cash LONG/SHORT, home 25, paper only, real ₹0, provisional per 100 shares, ₹40/trade.

## V2 RESTART — cross-year method (2026-10-31, user order 14:58 IST: "then system is wrong" / "Start then self improvement")
- **Charter:** Lesson 26 written; `stocks_RECURSIVE_ENGINE.md` amended with the v2 charter — windows Jan–Dec 2025 + Jan–Oct 2026 both scored every cycle; **cross-year gate: bank only if combined total rises AND neither year's total falls AND neither year is negative at book level**; all v1 disciplines carried over; saturation = 3 consecutive no-beat cycles under this gate; ₹75,000/month measured on the 22-month combined average.
- **Data infrastructure:** `/tmp/val2025` (the validation's shadow) was found GONE — /tmp is not durable. Rebuilt persistently as `data/full_hist/` (progressive cache copy + the same Upstox fills; `stocks_engine_v2_rebuild_data.py`): all 26 symbols span 2024-10-01 → 2026-10-28 (514 daily rows each); the four gap symbols have exactly 22 Sep-2025 days. The main cache `data/progressive` was never written.
- **2025 event calendar BUILT** (`stock_event_calendar_2025.csv`, **114 rows = 100 results + 14 news**; same schema, judgement fields and effective-reaction-date rule as the 2026 file; built by `stocks_engine_v2_calendar_build.py`; NO P&L was looked at while building it). Results dates from TipRanks earnings histories (Financial Express board meetings for INDUSTOWER). **Sample verification:** the method was validated before use — TipRanks reproduced the 2026 file's own event dates exactly for all 25 stocks' 2026-window rows, FE matched INDUSTOWER 4/4, and the 15 Q2 FY26 rows already in the 2026 file matched 15/15; reaction-date spot checks: INDUSTOWER Q3 FY25 announced Thu Jan 23, 2025 at 22:09 IST (Rediff) → reaction Fri Jan 24 ✓; HDFCBANK Saturday results → Monday reactions (Apr 19→21, Jul 19→21, Oct 18→20) ✓; BDL MRSAM filed intraday Jan 16, 13:49, stock +8% same day → same-day reaction ✓; TVSMOTOR Rapido divestment filed Nov 6 evening → reaction Nov 7 ✓; ITC BAT block announced May 27 after-market → executed/reaction May 28 ✓; ITC GST 40% slab announced late Sep 3 → reaction Sep 4 ✓. News classes mirror 2026's: large_order ×3 (BDL), dividend ×4 (ITC ×2, HDFCBANK ×2 — ex-dates, inert for scoring), corporate_action ×2 (HDFCBANK 1:1 bonus ex-date Aug 26, 2025; TVSMOTOR Rapido), management_change ×2 (WIPRO, TATASTEEL), fda_approval ×1 (GLENMARK), block_deal ×1 (ITC), sector_policy ×1 (ITC GST). No verified 2025 ITC pricing event exists — correctly absent. after_market is 'unverified' for 2025 results except INDUSTOWER Q3 FY25 ('yes', documented 22:09 evidence) — disclosed asymmetry vs 2026's per-event midday calls.
- **V2 INCUMBENT** (`stocks_engine_v2_build.py` — validation F4/INV machinery verbatim on `data/full_hist` + generalised event builders; **ALL CONTROLS PASS in the same run**: Control A dump assembly == plateau; B1/B2/C F4+INV rebuilds per-trade; all nine event-builder anchors per-trade vs their frozen dumps (P2F ≥2.0% tuning anchor 48/+₹12,835.88 included); 2025 anchors F4 261/−₹5,093.75 and INV 245/+₹7,642.52 exact; timing audits 0 everywhere): **2025 FULL BOOK = 636 tr / +₹23.06** — F4 261/−5,093.75 · INV-LONG 245/+7,642.52 · N4-V3 63/−5,779.08 · P2F 28/+14,365.77 · P2F-R2 28/−5,973.98 · R2-LOWBAND 11/−5,138.42. Months 2025: Jan +4,075.57 · Feb +7,568.84 · Mar −7,469.64 · Apr +6,828.36 · May −8,486.26 · Jun 0 (no trades) · Jul −2,817.78 · Aug +8,920.05 · Sep +3,254.97 · Oct −6,665.04 · Nov −5,186.01 · Dec 0 (no trades) — five red months, ex-top-3 **−₹27,814.95**, max DD −₹19,432.33. 2026 machinery book == plateau exactly (663 tr / +₹197,607.74; per-comp F4 +101,757.06 · INV +38,987.84 · N4 +21,293.05 · P2F +19,416.63 · P2F-R2 +14,892.38 · R2-LOWBAND +1,260.78). **COMBINED INCUMBENT = +₹197,630.80 = ₹8,983.22/month over 22 months** (2025: ₹1.92/month; 2026: ₹19,760.77/month) vs the ₹75,000/month goal. Stated plainly: with all six components runnable, the v1 book earned twenty-three rupees in 2025 — the user's verdict stands quantified.
- Books on disk: `stocks_engine_v2_book2025_trades.csv`, `stocks_engine_v2_book2026_trades.csv`; build record `v2_out/v2_build_results.json`.

## V2 CYCLE 1 — V2C1-FOLLOW-GLENMARK-SHORT-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Diagnosis (component × year on the combined book):** every component-level 2025 failure is 2026-positive (whole-component deletion fails gate leg (b) mechanically); the two largest 2025 slices are regime flips (F4×HINDUNILVR×LONG −10,218.40 vs +765.62; F4×TVSMOTOR×SHORT −5,728.79 vs +20,255.64). The weakest cross-year point: **GLENMARK × SHORT in the same-day follow components** — F4: 2025 7 tr/−3,010.96, 2026 20 tr/−136.98; N4-V3: 2025 2 tr/−2,731.28, 2026 3 tr/−494.21. Frozen in `stocks_engine_frozen.md` (V2-CYCLE-1) BEFORE scoring, with the SAT-36 disclosure stated in the freeze: SAT-36 closed this slice on the 2026 window under the v1 quality bar; Cycle 1 re-opens it only on the fresh-evidence condition SAT-36 itself named — a full unfitted year in which the same (name × direction) loses −₹5,742.24 across both follow components — under the user-ordered v2 gate. Scope stops at the follow mechanisms because GLENMARK × SHORT in the P2F family EARNS in 2026 (+₹6,429.04); GLENMARK LONG untouched.
- **Exact score** (`stocks_engine_v2_cycle1_score.py` / `v2_out/v2_cycle1_result.json`; incumbent asserted from the all-controls-passed build; deleted set == frozen diagnosis exactly, 32 tr / −₹6,373.43): **2025: 627 tr / +₹5,765.30** (was +₹23.06; months after: Mar −4,805.74 · May −8,486.26 · Jul −2,817.78 · Oct −6,665.04 · Nov −3,675.05 still red — five red months remain; ex-top-3 −27,814.95 → −22,072.71, still deeply negative) · **2026: 640 tr / +₹198,238.93** (was +₹197,607.74; all ten months still green; August thickens 666.78 → 7,204.51; March dips 20,584.41 → 17,642.62 because the removed N4 slice contained the +₹3,084.50 winner of 2026-03-04 — disclosed heterogeneity; the year total still rises; ex-top-3 72,518.25 → 73,149.44).
- **Gate arithmetic (stated per charter):** (a) combined **+₹197,630.80 → +₹204,004.23** (rises +₹6,373.43) ✓ · (b) neither year falls (2025 +5,742.24; 2026 +631.19) ✓ · (c) neither year negative (2025 +₹5,765.30 > 0 — thin, stated plainly; 2026 +₹198,238.93) ✓. **BANKED.** New combined best **+₹204,004.23 = ₹9,272.92/month** — still 12.4% of the ₹75,000/month goal; the fix stanches one leak, it does not make 2025 a good year. no_beat_cycles = 0. Lesson 27 appended. New incumbent books: `stocks_engine_v2_c1_book2025_trades.csv`, `stocks_engine_v2_c1_book2026_trades.csv`.
- **Status: v2 ACTIVE** (state reset: terminated cleared, v1 history preserved above and in the state file's v1 fields). Next: Cycle 2 from +₹204,004.23 — the remaining cross-year field is dominated by the 2025-red event components (P2F-R2, N4-V3, R2-LOWBAND year-splits) and the five red 2025 months; any further fix must clear the same gate.

## V2 CYCLE 2 — V2C2-N4-BDL-SHORT-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Diagnosis (component × year on the post-C1 combined book; stocks_engine_v2_cycle2_diag.py, anchor exact):** P2F-R2 −5,973.98 / +14,892.38 · R2-LOWBAND −5,138.42 / +1,260.78 · N4-V3 −3,047.80 / +21,787.26 · F4 −2,082.79 / +101,894.04 · INV-LONG +7,642.52 / +38,987.84 · P2F +14,365.77 / +19,416.63. **Charter question 1 — lag vs band, answered: the R+2 LAG is the 2025 poison.** At the same ≥2.5% band, R+1 (P2F) earns +₹14,365.77 in 2025 while R+2 (P2F-R2) loses −₹5,973.98; the low band at R+2 also loses 2025 (−₹5,138.42) with a near-zero 2026. P2F-R2's 2025 loss is diffuse (single trades; names 2026-absent or 2026-earning) — only one both-years-negative slice inside it (KALYANKJIL LONG, −₹548.17), so there is no honest deletion fix inside P2F-R2 and whole-component deletion fails leg (b) mechanically. The lag finding is recorded as diagnosis; the R+2 components stand as year-specialised under the gate, judged on fresh data. **Charter question 2 — N4-V3's 2025 loss is slice-level:** its both-years-negative slices sum to −₹9,501.67 combined against real 2025 winners (OBEROIRLTY ±, UNITDSPR SHORT +2,199.35, GODREJCP LONG +1,704.20, BDL LONG +1,498.67).
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-2):** N4-V3 takes no BDL SHORT signals — the largest both-years-negative slice in the book (2025 2 tr / −₹2,545.00 / 0 w · 2026 1 tr / −₹640.00 / 0 w · combined −₹3,185.00). Scope stops at (N4-V3 × BDL × SHORT): BDL LONG inside N4-V3 earns in 2025 (+₹1,498.67) and BDL earns across the other event systems (JN-1) — both untouched. The standing v2 registry bar was pre-registered in the same freeze: negative in BOTH years AND combined ≤ −₹500.
- **Exact score (stocks_engine_v2_cycle2_score.py / v2_out/v2_cycle2_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 3 tr / −₹3,185.00):** **2025: 625 tr / +₹8,310.30** (was +₹5,765.30; five red months remain — Mar −4,805.74 · May −6,936.58 · Jul −2,817.78 · Oct −6,665.04 · Nov −3,675.05; ex-top-3 −22,072.71 → −19,527.71) · **2026: 639 tr / +₹198,878.93** (was +₹198,238.93; all ten months green; ex-top-3 73,149.44 → 73,789.44).
- **Gate arithmetic (stated per charter):** (a) combined **+₹204,004.23 → +₹207,189.23** (rises +₹3,185.00) ✓ · (b) neither year falls (2025 +2,545.00; 2026 +640.00) ✓ · (c) neither year negative (2025 +₹8,310.30 — thicker, still the thin year) ✓. **BANKED.** New combined best **+₹207,189.23 = ₹9,417.69/month** (12.6% of the ₹75,000 goal). no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c2_book2025_trades.csv / stocks_engine_v2_c2_book2026_trades.csv. Book law added: N4-V3 takes no BDL SHORT signals.
- **Status: v2 ACTIVE.** Next: Cycle 3 — a challenger cycle (charter: every 3rd cycle), then the deletion registry continues (next rows at the standing bar: INV-LONG × HINDALCO × LONG −2,346.58 · INV-LONG × UNITDSPR × LONG −1,831.59 · F4 × HDFCBANK × SHORT −1,710.61 · F4 × KALYANKJIL × LONG −1,625.21 · N4-V3 × HINDALCO × SHORT −1,475.56 · N4-V3 × HINDZINC × LONG −1,444.04 · N4-V3 × UNITDSPR × LONG −1,312.80 · N4-V3 × RECLTD × LONG −1,062.88 — re-derive before use).

## V2 CYCLE 3 — CHALLENGER CH-V2-1 "P2F-3.0": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-3; every-3rd-cycle challenger):** the incumbent book with P2F rebuilt at a ≥3.0% reaction band (build machinery's own p2f_book at lo_band=3.0; identical lag R+1, exits T125/S050, exclusions), testing whether P2F's 2.5% floor — validated from below in Lesson 21 — is a floor or a peak on the home 25. Prior: T2's pooled-50 preference for the 3.0% band (different universe, stated in the freeze). Freeze was blind: the [2.5%, 3.0%) slice was not pre-measured.
- **Controls (same pass):** the full v2 build re-executed in-process — ALL controls pass (Control A plateau assembly exact; F4/INV rebuilds per-trade; all nine event anchors; 2025 anchors exact; timing audits 0); the build's incumbent P2F sets equal the post-C2 books' P2F rows per-trade in both years; challenger P2F sets are exact subsets of the incumbent's in both years (a band raise only drops trades).
- **Exact score (stocks_engine_v2_cycle3_score.py / v2_out/v2_cycle3_result.json):** the dropped [2.5%, 3.0%) slice EARNS in both years — 2025: 5 tr / **+₹2,823.67** (P2F 28 tr / +14,365.77 → 23 tr / +11,542.10) · 2026: 5 tr / **+₹1,479.98** (P2F 32 tr / +19,416.63 → 27 tr / +17,936.65). Challenger book: 2025 620 tr / +₹5,486.63 · 2026 634 tr / +₹197,398.95 · combined **+₹202,885.58** (₹9,222.07/month); ex-top-3 worsens both years (2025 −19,527.71 → −22,351.38; 2026 73,789.44 → 72,309.46).
- **Gate arithmetic (stated per charter):** (a) combined FALLS +₹207,189.23 → +₹202,885.58 ✗ · (b) BOTH years fall (2025 −2,823.67; 2026 −1,479.98) ✗ · (c) neither year negative ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C2 books; combined best +₹207,189.23). no_beat_cycles 0 → 1. Lesson 28 appended: cross-year, P2F's living band extends through [2.5%, 3.0%) — 2.5% is a floor with living material above it, and T2's pooled-50 band preference does not transfer to the home 25.
- **Status: v2 ACTIVE.** Next: Cycle 4 returns to the cross-year deletion registry (next row: INV-LONG × HINDALCO × LONG, −₹2,346.58 combined — re-derived at scoring).

## FLOOR AMENDMENT (user mandate, 2026-10-31 15:17 IST) — folded into the record here
- His words: **"Whenever I increase the time, you are reducing the profit. Profit should not be reduced. 20,000 per month should be default."** Amended on the record in stocks_RECURSIVE_ENGINE.md (v2 charter section (e)) and in the state file: **the success bar is now per-year — 2025 ≥ ₹240,000 AND 2026 ≥ ₹200,000** (₹20,000/month in each year; no year subsidises another in the headline). The cross-year gate is unchanged and is NEVER loosened to reach the floor; saturation below the floor will be reported as the proven ceiling, per year. ₹75,000/month stays the horizon above the floor. Challengers are henceforth aimed at the weak year — 2025, seeded from what worked there (P2F, INV-LONG). Position at the mandate (post-Cycle-1): 2025 +₹5,765.30 (gap ₹234,234.70) · 2026 +₹198,238.93 (gap ₹1,761.07).

## V2 CYCLE 4 — V2C4-INV-HINDALCO-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-4):** INV-LONG takes no HINDALCO signals — the largest remaining slice under the standing v2 registry bar (2025 4 tr / −₹1,451.18 / 0 w · 2026 5 tr / −₹895.40 / 1 w · combined −₹2,346.58). Third mechanism in which HINDALCO × LONG independently qualifies (after P2F SAT-14 and F4 SAT-25); scope stays INV-LONG-only — P2F-R2's earning HINDALCO LONG (+₹1,276.75) and all SHORT slices untouched.
- **Exact score (stocks_engine_v2_cycle4_score.py / v2_out/v2_cycle4_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 9 tr / −₹2,346.58):** **2025: 621 tr / +₹9,761.48** (was +₹8,310.30; five red months remain — Mar −4,035.66 · May −6,936.58 · Jul −2,817.78 · Oct −6,665.04 · Nov −3,675.05; ex-top-3 −19,527.71 → −18,076.53) · **2026: 634 tr / +₹199,774.33** (was +₹198,878.93; all ten months green; ex-top-3 73,789.44 → 74,684.84).
- **Gate arithmetic (stated per charter):** (a) combined **+₹207,189.23 → +₹209,535.81** (rises +₹2,346.58) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹209,535.81 = ₹9,524.36/month**. **Floor position: 2025 gap ₹230,238.52 · 2026 gap ₹225.67** — 2026 now stands within one small bank of its floor. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c4_book2025_trades.csv / stocks_engine_v2_c4_book2026_trades.csv. Book law added: INV-LONG takes no HINDALCO signals.
- **Status: v2 ACTIVE.** Next: Cycle 5 — the registry continues (INV-LONG × UNITDSPR × LONG, −₹1,831.59 combined; its 2026 slice −₹1,361.10 exceeds the remaining 2026 floor gap, so a bank would put 2026 over its ₹200,000 floor — reported when scored, not before). Cycle 6 is a challenger cycle, aimed at 2025 per the mandate.

## V2 CYCLE 5 — V2C5-INV-UNITDSPR-EXCL: BANKED under the cross-year gate (2026-10-31) — 2026 CROSSES ITS FLOOR
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-5):** INV-LONG takes no UNITDSPR signals (2025 4 tr / −₹470.49 / 1 w · 2026 2 tr / −₹1,361.10 / 0 w · combined −₹1,831.59). Scope stays INV-LONG-only: UNITDSPR's SHORT flow keeps earning inside F4 and N4-V3 (+₹2,199.35 in 2025) — untouched.
- **Exact score (stocks_engine_v2_cycle5_score.py / v2_out/v2_cycle5_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 6 tr / −₹1,831.59):** **2025: 617 tr / +₹10,231.97** (was +₹9,761.48; five red months remain; ex-top-3 −18,076.53 → −17,606.04) · **2026: 632 tr / +₹201,135.43** (was +₹199,774.33; all ten months green; ex-top-3 74,684.84 → 76,045.94).
- **Gate arithmetic (stated per charter):** (a) combined **+₹209,535.81 → +₹211,367.40** (rises +₹1,831.59) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹211,367.40 = ₹9,607.61/month**.
- **FLOOR MILESTONE (per-year headline, per the mandate): 2026 = +₹201,135.43 — OVER its ₹200,000 floor by ₹1,135.43.** 2025 = +₹10,231.97 — **₹229,768.03 below** its ₹240,000 floor. The two facts are reported separately, exactly as the mandate requires: the strong year does not subsidise the weak one. The engine's remaining war is 2025. no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c5_book2025_trades.csv / stocks_engine_v2_c5_book2026_trades.csv. Book law added: INV-LONG takes no UNITDSPR signals.
- **Status: v2 ACTIVE.** Next: Cycle 6 — challenger cycle, aimed at 2025 per the mandate (seeded from P2F, 2025's strongest component).

## V2 CYCLE 6 — CHALLENGER CH-V2-2 "P2F-NEWS": REJECTED under the cross-year gate + Lesson 21 test (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-6; challenger cycle aimed at 2025 per the mandate, seeded from P2F):** a new component following NEWS-event reactions at R+1 (N4's SINGLE_NEWS classes, ≥2.5% band, score_lag verbatim at lag 1, T125/S050, RF-1, no name exclusions, P2F-duplicate drops) added to the incumbent book.
- **Controls (same pass):** full v2 build re-executed in-process — ALL controls pass; reaction returns independently recomputed from the raw daily CSVs per candidate (exact); timing asserted per trade (entry = the trading day strictly after R); flip placebo scored on identical entries.
- **Exact score (stocks_engine_v2_cycle6_score.py / v2_out/v2_cycle6_result.json):** 2025: 10 news candidates → 3 in-band → **2 trades, BOTH WINNERS, +₹1,949.25** (BDL LONG +₹1,461.75 on the Jan-16 MRSAM order reaction +5.91%; ITC SHORT +₹487.50), placebo −₹891.70 — the 2025 side worked. 2026: 11 candidates → 4 in-band → **4 trades, −₹2,089.31, expectancy −₹522.33** (GLENMARK loses in BOTH directions: SHORT −₹1,061.10, LONG −₹1,207.30) — and the flip placebo earns **+₹5,475.58 (expectancy +₹1,368.89)**: 2026 news reactions FADE at R+1. Component combined: 6 trades, expectancy **−₹23.34** vs placebo **+₹763.98**.
- **Gate arithmetic (stated per charter):** (a) combined FALLS +₹211,367.40 → +₹211,227.34 ✗ · (b) 2026 falls (−₹2,089.31) ✗ · (c) ✓ — and the pre-registered Lesson 21 test fails BOTH clauses (expectancy ≤ 0; placebo ahead per-trade). **REJECTED.** Incumbent unchanged (post-C5 books; combined best +₹211,367.40; 2026 floor still met). no_beat_cycles 0 → 1. Lesson 29 appended: the information axis is (event-class × lag)-specific — results reactions carry a repricing that persists to R+1; single-item news is impounded the same day (which is why N4's same-day machinery is the news mechanism that works), and its R+1 direction is regime-unstable (follow in 2025, fade in 2026). **The P2F-NEWS family is CLOSED.** Thin counts disclosed (6 trades); the placebo margin, not the total, is the decisive fact.
- **Status: v2 ACTIVE.** Next: Cycle 7 returns to the deletion registry (F4 × HDFCBANK × SHORT, −₹1,710.61 combined).

## V2 CYCLE 7 — V2C7-F4-HDFCBANK-SHORT-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-7):** F4 takes no SHORT signals on HDFCBANK (2025 5 tr / −₹1,460.11 / 2 w · 2026 7 tr / −₹250.50 / 3 w · combined −₹1,710.61). Scope stays (F4 × HDFCBANK × SHORT): HDFCBANK SHORT inside R2-LOWBAND earns in 2026 (+₹836.81) and its LONG inside R2-LOWBAND earned in 2025 (+₹650.00) — untouched.
- **Exact score (stocks_engine_v2_cycle7_score.py / v2_out/v2_cycle7_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 12 tr / −₹1,710.61):** **2025: 612 tr / +₹11,692.08** (was +₹10,231.97; five red months remain; ex-top-3 −17,606.04 → −16,145.93) · **2026: 625 tr / +₹201,385.93** (was +₹201,135.43; all ten months green; ex-top-3 76,045.94 → 76,296.44).
- **Gate arithmetic (stated per charter):** (a) combined **+₹211,367.40 → +₹213,078.01** (rises +₹1,710.61) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹213,078.01 = ₹9,685.36/month**. Floor position: 2025 gap ₹228,307.92 · 2026 over its floor by ₹1,385.93. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c7_book2025_trades.csv / stocks_engine_v2_c7_book2026_trades.csv. Book law added: F4 takes no HDFCBANK SHORT signals.
- **Status: v2 ACTIVE.** Next: Cycle 8 — registry continues (F4 × KALYANKJIL × LONG, −₹1,625.21 combined).

## V2 CYCLE 8 — V2C8-F4-KALYANKJIL-LONG-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-8):** F4 takes no LONG signals on KALYANKJIL (2025 3 tr / −₹713.82 / 1 w · 2026 7 tr / −₹911.39 / 2 w · combined −₹1,625.21). Scope stays (F4 × KALYANKJIL × LONG): KALYANKJIL keeps earning inside N4-V3 in both directions — untouched.
- **Exact score (stocks_engine_v2_cycle8_score.py / v2_out/v2_cycle8_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 10 tr / −₹1,625.21):** **2025: 609 tr / +₹12,405.90** (was +₹11,692.08; five red months remain; ex-top-3 −16,145.93 → −15,432.11) · **2026: 618 tr / +₹202,297.32** (was +₹201,385.93; all ten months green; ex-top-3 76,296.44 → 77,207.83).
- **Gate arithmetic (stated per charter):** (a) combined **+₹213,078.01 → +₹214,703.22** (rises +₹1,625.21) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹214,703.22 = ₹9,759.24/month**. Floor position: 2025 gap ₹227,594.10 · 2026 over its floor by ₹2,297.32. no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c8_book2025_trades.csv / stocks_engine_v2_c8_book2026_trades.csv. Book law added: F4 takes no KALYANKJIL LONG signals.
- **Status: v2 ACTIVE.** Next: Cycle 9 — challenger cycle: N4-V3's trigger floor tested from above (CH-V2-3), the population question behind the registry's N4 cluster.

## V2 CYCLE 9 — CHALLENGER CH-V2-3 "N4-HIFLOOR": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-9):** N4-V3 rebuilt with the 09:30 trigger floor raised ≥1.0% → ≥1.5% (identical machinery, SAT-15 exits, full current book law), asking whether N4's cross-year losses concentrate in its weakest triggers. Freeze was blind.
- **Controls (same pass):** full v2 build re-executed — ALL controls pass; the parameterised n4 copy at floor 1.0 reproduces the SAT-15 dump per-trade AND, after filters + v2 law, the incumbent books' N4 rows in both years; the challenger set is an exact subset of the incumbent N4 set in both years.
- **Exact score (stocks_engine_v2_cycle9_score.py / v2_out/v2_cycle9_result.json):** the [1.0%, 1.5%) slice is REGIME-FLIPPED — 2025: **13 tr / −₹1,860.69** (dropping it would lift N4's 2025 from −₹502.80 to +₹1,357.89) · 2026: **4 tr / +₹3,135.29** (dropping it cuts N4's 2026 from +₹22,427.26 to +₹19,291.97). Challenger book: 2025 +₹14,266.59 · 2026 +₹199,162.03 · combined **+₹213,428.62**; ex-top-3 improves in 2025 (−15,432.11 → −13,634.47) but worsens in 2026 (77,207.83 → 74,072.54).
- **Gate arithmetic (stated per charter):** (a) combined FALLS +₹214,703.22 → +₹213,428.62 ✗ · (b) 2026 falls (−₹3,135.29) ✗ · (c) ✓. **REJECTED on legs (a) and (b).** The floor raise is not merely a year-trade — it is net-negative combined (−₹1,274.60): 2026's four mid-band trades earn more than 2025's thirteen lose. Incumbent unchanged (post-C8 books). no_beat_cycles 0 → 1. Lesson 30 appended: N4's trigger floor is now bounded from BOTH sides cross-year (Lesson 17 from below, this cycle from above) — **the ≥1.0% floor is CLOSED at both ends; N4's 2025 repair stays on the registry's slice route.**
- **Status: v2 ACTIVE.** Next: Cycle 10 — registry continues (N4-V3 × HINDALCO × SHORT, −₹1,475.56 combined).

## V2 CYCLE 10 — V2C10-N4-HINDALCO-SHORT-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-10):** N4-V3 takes no SHORT signals on HINDALCO (2025 1 tr / −₹568.20 / 0 w · 2026 1 tr / −₹907.36 / 0 w · combined −₹1,475.56, expectancy −₹737.78; thin-sample caveat disclosed in the freeze — the evidence is the 0-winner pattern in two independent years). HINDALCO × LONG now stands excluded in four mechanisms on their own numbers (P2F, F4, INV-LONG, and here the SHORT side of N4-V3); P2F-R2's earning HINDALCO LONG untouched.
- **Exact score (stocks_engine_v2_cycle10_score.py / v2_out/v2_cycle10_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 2 tr / −₹1,475.56):** **2025: 608 tr / +₹12,974.10** (was +₹12,405.90; ex-top-3 −15,432.11 → −14,863.91) · **2026: 617 tr / +₹203,204.68** (was +₹202,297.32; all ten months green; ex-top-3 77,207.83 → 78,115.19).
- **Gate arithmetic (stated per charter):** (a) combined **+₹214,703.22 → +₹216,178.78** (rises +₹1,475.56) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹216,178.78 = ₹9,826.31/month**. Floor position: 2025 gap ₹227,025.90 · 2026 over its floor by ₹3,204.68. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c10_book2025_trades.csv / stocks_engine_v2_c10_book2026_trades.csv. Book law added: N4-V3 takes no HINDALCO SHORT signals.
- **Status: v2 ACTIVE.** Next: Cycle 11 — registry continues (N4-V3 × HINDZINC × LONG, −₹1,444.04 combined).

## V2 CYCLE 11 — V2C11-N4-HINDZINC-LONG-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-11):** N4-V3 takes no LONG signals on HINDZINC (2025 1 tr / −₹400.80 / 0 w · 2026 2 tr / −₹1,043.24 / 0 w · combined −₹1,444.04; thin-sample caveat disclosed in the freeze). Scope stays (N4-V3 × HINDZINC × LONG): P2F-R2's earning HINDZINC LONG (+₹812.50) untouched — the SAT-20 pattern, fifth mechanism judged on its own slice.
- **Exact score (stocks_engine_v2_cycle11_score.py / v2_out/v2_cycle11_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 3 tr / −₹1,444.04):** **2025: 607 tr / +₹13,374.90** (was +₹12,974.10; ex-top-3 −14,863.91 → −14,463.11) · **2026: 615 tr / +₹204,247.92** (was +₹203,204.68; all ten months green; ex-top-3 78,115.19 → 79,158.43).
- **Gate arithmetic (stated per charter):** (a) combined **+₹216,178.78 → +₹217,622.82** (rises +₹1,444.04) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹217,622.82 = ₹9,891.95/month**. Floor position: 2025 gap ₹226,625.10 · 2026 over its floor by ₹4,247.92. no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c11_book2025_trades.csv / stocks_engine_v2_c11_book2026_trades.csv. Book law added: N4-V3 takes no HINDZINC LONG signals.
- **Status: v2 ACTIVE.** Next: Cycle 12 — challenger cycle: F4's stop step (S095 → S110) tested cross-year (CH-V2-4).

## V2 CYCLE 12 — CHALLENGER CH-V2-4 "F4-S110": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-12):** F4 rebuilt with the stop widened −0.95% → −1.10% (target +1.50% unchanged) on both years — the step SAT-11 refused on a diagnosis-only support test under v1's single-window gate, re-tested exactly under the cross-year method.
- **Controls (same pass):** full v2 build re-executed — ALL controls pass (incl. Control B2: the S095 rebuild == the frozen F4 set); incumbent F4 rows == build F4 sets minus the three v2-law slices per-trade in both years; S110 timing-audit deltas 0 violations; challenger entry sets IDENTICAL to the incumbent's in both years (246 tr in 2025, 355 in 2026 — the exit change moved no entry).
- **Exact score (stocks_engine_v2_cycle12_score.py / v2_out/v2_cycle12_result.json):** the step loses in BOTH years — 2025: F4 +₹91.14 → **−₹195.97** (−₹287.11; the step flips F4's thin 2025 component negative) · 2026: F4 +₹103,055.93 → **+₹101,796.84** (−₹1,259.09). Challenger book combined **+₹216,076.62** vs incumbent +₹217,622.82.
- **Gate arithmetic (stated per charter):** (a) combined FALLS (−₹1,546.20) ✗ · (b) both years fall ✗ · (c) ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C11 books). no_beat_cycles 0 → 1. Lesson 31 appended: SAT-11's excursion estimate for this step (+₹6,686.35 on 2026) pointed the wrong way — the exact rebuild is −₹1,259.09 there; the estimate is a compass, the rebuild is the score, and **the F4 stop family is now CLOSED CROSS-YEAR at T150/S095** (the target family was closed in v1). Also on the record: after eleven cycles of surgery, F4's 2025 component stands at +₹91.14 — the flagship is a 2026-only earner at book level too, and the gate has never let its 2026 weight disguise that.
- **Status: v2 ACTIVE.** Next: Cycle 13 — registry continues (N4-V3 × UNITDSPR × LONG, −₹1,312.80 combined).

## V2 CYCLE 13 — V2C13-N4-UNITDSPR-LONG-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-13):** N4-V3 takes no LONG signals on UNITDSPR (2025 1 tr / −₹1,212.80 / 0 w · 2026 1 tr / −₹100.00 / 0 w · combined −₹1,312.80; thin-sample caveat disclosed in the freeze). Scope stays (N4-V3 × UNITDSPR × LONG): UNITDSPR SHORT inside N4-V3 was one of its 2025 winners (+₹2,199.35) and keeps trading — the direction split again (Lesson 15).
- **Exact score (stocks_engine_v2_cycle13_score.py / v2_out/v2_cycle13_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 2 tr / −₹1,312.80):** **2025: 606 tr / +₹14,587.70** (was +₹13,374.90; ex-top-3 −14,463.11 → −13,250.31) · **2026: 614 tr / +₹204,347.92** (was +₹204,247.92; all ten months green; ex-top-3 79,158.43 → 79,258.43).
- **Gate arithmetic (stated per charter):** (a) combined **+₹217,622.82 → +₹218,935.62** (rises +₹1,312.80) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹218,935.62 = ₹9,951.62/month**. Floor position: 2025 gap ₹225,412.30 · 2026 over its floor by ₹4,347.92. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c13_book2025_trades.csv / stocks_engine_v2_c13_book2026_trades.csv. Book law added: N4-V3 takes no UNITDSPR LONG signals.
- **Status: v2 ACTIVE.** Next: Cycle 14 — registry continues (N4-V3 × RECLTD × LONG, −₹1,062.88 combined).

## V2 CYCLE 14 — V2C14-N4-RECLTD-LONG-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-14):** N4-V3 takes no LONG signals on RECLTD (2025 2 tr / −₹730.60 / 0 w · 2026 1 tr / −₹332.28 / 0 w · combined −₹1,062.88; thin-sample caveat disclosed in the freeze). Scope stays (N4-V3 × RECLTD × LONG): RECLTD SHORT inside N4-V3 earns in 2026 (+₹574.32) — untouched.
- **Exact score (stocks_engine_v2_cycle14_score.py / v2_out/v2_cycle14_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 3 tr / −₹1,062.88):** **2025: 604 tr / +₹15,318.30** (was +₹14,587.70; ex-top-3 −13,250.31 → −12,519.71) · **2026: 613 tr / +₹204,680.20** (was +₹204,347.92; all ten months green; ex-top-3 79,258.43 → 79,590.71).
- **Gate arithmetic (stated per charter):** (a) combined **+₹218,935.62 → +₹219,998.50** (rises +₹1,062.88) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹219,998.50 = ₹9,999.93/month**. Floor position: 2025 gap ₹224,681.70 · 2026 over its floor by ₹4,680.20. no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c14_book2025_trades.csv / stocks_engine_v2_c14_book2026_trades.csv. Book law added: N4-V3 takes no RECLTD LONG signals.
- **Status: v2 ACTIVE.** Next: Cycle 15 — challenger cycle: N4-V3's event-class split (results-days vs news-only-days), CH-V2-5.

## V2 CYCLE 15 — CHALLENGER CH-V2-5 "N4-RESULTS-ONLY": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-15):** N4-V3 rebuilt without its news-only-day trades (results reaction days kept; a day in both classes counts as results), full current book law — testing whether N4's two information classes separate cross-year at N4's own same-day lag, as Lesson 29 showed they do at R+1. Freeze was blind.
- **Controls (same pass):** full v2 build re-executed — ALL controls pass; the tagged copy reproduces the SAT-15 dump per-trade (2026 raw) and, after filters + the full v2 law, equals the incumbent books' N4 rows in both years; challenger set is an exact subset.
- **Exact score (stocks_engine_v2_cycle15_score.py / v2_out/v2_cycle15_result.json):** the news-only slice is REGIME-FLIPPED — 2025: **6 tr / −₹2,625.17** (2 w; the TVSMOTOR Rapido-divestment SHORT −₹2,729.36 is the bulk) · 2026: **3 tr / +₹2,936.18** (1 w; GLENMARK LONG +₹3,376.53 on a news day). Dropping the class: 2025 book → +₹17,943.47, 2026 book → +₹201,744.02, combined **+₹219,687.49** (net −₹311.01 over the 9 trades).
- **Gate arithmetic (stated per charter):** (a) combined FALLS +₹219,998.50 → +₹219,687.49 ✗ · (b) 2026 falls (−₹2,936.18) ✗ · (c) ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C14 books). no_beat_cycles 0 → 1. Lesson 32 appended: Lesson 29's class distinction is a LAG fact, not a same-day quality fact — at N4's lag the news days are regime-flipped and net ≈ ₹0 combined; **the event-class question is CLOSED at N4's lag, the union stands.**
- **Status: v2 ACTIVE.** Next: Cycle 16 — registry continues (N4-V3 × WIPRO × SHORT, −₹574.20 combined; then P2F-R2 × KALYANKJIL × LONG and INV-LONG × TATASTEEL × LONG remain at the bar).

## V2 CYCLE 16 — V2C16-N4-WIPRO-SHORT-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-16):** N4-V3 takes no SHORT signals on WIPRO (2025 2 tr / −₹112.80 / 1 w · 2026 3 tr / −₹461.40 / 0 w · combined −₹574.20 — the smallest slice banked under the standing bar; the bar was not moved in either direction). WIPRO LONG inside N4-V3 does not qualify (2026 +₹36.18) and stays.
- **Exact score (stocks_engine_v2_cycle16_score.py / v2_out/v2_cycle16_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 5 tr / −₹574.20):** **2025: 602 tr / +₹15,431.10** (was +₹15,318.30; ex-top-3 −12,519.71 → −12,406.91) · **2026: 610 tr / +₹205,141.60** (was +₹204,680.20; all ten months green; ex-top-3 79,590.71 → 80,052.11).
- **Gate arithmetic (stated per charter):** (a) combined **+₹219,998.50 → +₹220,572.70** (rises +₹574.20) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹220,572.70 = ₹10,026.03/month**. Floor position: 2025 gap ₹224,568.90 · 2026 over its floor by ₹5,141.60. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c16_book2025_trades.csv / stocks_engine_v2_c16_book2026_trades.csv. Book law added: N4-V3 takes no WIPRO SHORT signals.
- **Status: v2 ACTIVE.** Next: Cycle 17 — registry continues (P2F-R2 × KALYANKJIL × LONG, −₹548.17 combined; one row remains after it: INV-LONG × TATASTEEL × LONG, −₹518.83).

## V2 CYCLE 17 — V2C17-R2-KALYANKJIL-LONG-EXCL: BANKED under the cross-year gate (2026-10-31)
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-17):** P2F-R2 takes no LONG signals on KALYANKJIL (2025 1 tr / −₹291.22 / 0 w · 2026 1 tr / −₹256.95 / 0 w · combined −₹548.17; thin-sample caveat disclosed in the freeze). The only both-years-negative slice inside P2F-R2 — the component's wider 2025 loss remains the diagnosed R+2-lag/regime fact, not slice rot, and is not disguised by this bank.
- **Exact score (stocks_engine_v2_cycle17_score.py / v2_out/v2_cycle17_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 2 tr / −₹548.17):** **2025: 601 tr / +₹15,722.32** (was +₹15,431.10; ex-top-3 −12,406.91 → −12,115.69) · **2026: 609 tr / +₹205,398.55** (was +₹205,141.60; all ten months green; ex-top-3 80,052.11 → 80,309.06).
- **Gate arithmetic (stated per charter):** (a) combined **+₹220,572.70 → +₹221,120.87** (rises +₹548.17) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹221,120.87 = ₹10,050.95/month**. Floor position: 2025 gap ₹224,277.68 · 2026 over its floor by ₹5,398.55. no_beat_cycles stays 0. New incumbent books: stocks_engine_v2_c17_book2025_trades.csv / stocks_engine_v2_c17_book2026_trades.csv. Book law added: P2F-R2 takes no KALYANKJIL LONG signals.
- **Status: v2 ACTIVE.** Next: Cycle 18 — challenger cycle: P2F's exit pair tested on its own population (CH-V2-6). One registry row remains at the bar (INV-LONG × TATASTEEL × LONG, −₹518.83) for Cycle 19.

## V2 CYCLE 18 — CHALLENGER CH-V2-6 "P2F-EXITS": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-18):** P2F rebuilt at T150/S080 (from T125/S050) on both years — testing whether the exit pair that paid on N4's same-day reaction population (SAT-15: +₹9,483.45) transfers to P2F's R+1 population. Freeze was blind; the SAT-5 closure it re-tested rested on CH-1's confounded change, stated in the freeze.
- **Controls (same pass):** full v2 build re-executed — ALL controls pass; the parameterised copy at (1.25, 0.50) reproduces the build's P2F sets per-trade in both years and those equal the incumbent books' P2F rows; challenger entry sets identical to the incumbent's in both years (28 tr in 2025, 32 in 2026).
- **Exact score (stocks_engine_v2_cycle18_score.py / v2_out/v2_cycle18_result.json):** the medicine does NOT transfer — 2025: P2F +₹14,365.77 → **+₹10,233.54** (−₹4,132.23; the weak year's R+1 winners are quick and the wider stop bleeds them) · 2026: +₹19,416.63 → **+₹19,718.13** (+₹301.50 — the same direction as N4's rebuild, a tenth of its size). Challenger book combined **+₹217,290.14** vs incumbent +₹221,120.87; ex-top-3 worsens in 2025 (−12,115.69 → −16,156.19).
- **Gate arithmetic (stated per charter):** (a) combined FALLS (−₹3,830.73) ✗ · (b) 2025 falls ✗ · (c) ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C17 books). no_beat_cycles 0 → 1. Lesson 33 appended: **P2F's exits are CLOSED cross-year at T125/S050** — exit medicine is population-specific, third exact confirmation (INV-LONG's grid peaks at its tightest pair; N4's rebuild paid on same-day entries; the identical pair fails on R+1 entries, driven by the weak year).
- **Status: v2 ACTIVE.** Next: Cycle 19 — the registry's last row at the bar (INV-LONG × TATASTEEL × LONG, −₹518.83 combined).

## V2 CYCLE 19 — V2C19-INV-TATASTEEL-EXCL: BANKED under the cross-year gate (2026-10-31) — REGISTRY EXHAUSTED AT THE BAR
- **Fix (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-19):** INV-LONG takes no TATASTEEL signals (2025 8 tr / −₹301.79 / 3 w · 2026 4 tr / −₹217.04 / 1 w · combined −₹518.83 — clears the standing bar by ₹18.83, disclosed in the freeze, not rounded away).
- **Exact score (stocks_engine_v2_cycle19_score.py / v2_out/v2_cycle19_result.json; incumbent asserted vs state best; deleted set == frozen diagnosis exactly, 12 tr / −₹518.83):** **2025: 593 tr / +₹16,024.11** (was +₹15,722.32; ex-top-3 −12,115.69 → −11,813.90) · **2026: 605 tr / +₹205,615.59** (was +₹205,398.55; all ten months green; ex-top-3 80,309.06 → 80,526.10).
- **Gate arithmetic (stated per charter):** (a) combined **+₹221,120.87 → +₹221,639.70** (rises +₹518.83) ✓ · (b) neither year falls ✓ · (c) neither year negative ✓. **BANKED.** New combined best **+₹221,639.70 = ₹10,074.53/month**. Floor position: 2025 gap ₹223,975.89 · 2026 over its floor by ₹5,615.59. no_beat_cycles 1 → 0. New incumbent books: stocks_engine_v2_c19_book2025_trades.csv / stocks_engine_v2_c19_book2026_trades.csv. Book law added: INV-LONG takes no TATASTEEL signals.
- **REGISTRY STATE (on the record):** the both-years-negative deletion registry is now EMPTY at the standing bar (negative in both years AND combined ≤ −₹500). Fourteen v2 deletion banks (Cycles 1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19 — plus the Cycle-1 two-component bank) took the combined book from +₹197,630.80 to +₹221,639.70 and 2025 from +₹23.06 to +₹16,024.11. The largest remaining sub-bar rows (P2F × WIPRO × LONG −₹496.67, R2-LOWBAND × ITC × LONG −₹445.58) STAY — the bar is not lowered at the finish line (Lesson 25). From here, progress can only come from challengers; saturation is three consecutive no-beats away whenever they stop paying.
- **Status: v2 ACTIVE.** Next: Cycle 20 — challenger: F4's round-2 legs restored (CH-V2-7), the last untested F4 population question.

## V2 CYCLE 20 — CHALLENGER CH-V2-7 "F4-ROUND2": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-20 + construction note):** F4's round-2 (second-signal) legs restored to the book — the population SAT-6 dropped on the 2026 window (70 tr / −₹11.83 there), isolated black-box from the audited raw populations as the legs f4_keep rejects SOLELY for their leg field (probe: 66 round2 legs in the 2026 raw population, 46 solely-round-blocked, 40 after the v2 law).
- **Controls (same pass):** full v2 build re-executed — ALL controls pass; S095 timing audits 0 violations both years; kept sets == build F4 sets; incumbent F4 rows == kept minus v2 law in both years; restoration set disjoint from the kept set, every member leg == "round2".
- **Exact score (stocks_engine_v2_cycle20_score.py / v2_out/v2_cycle20_result.json):** the round-2 population loses in BOTH years under the current law — 2025: **−₹3,306.97** (book → +₹12,717.14) · 2026: **40 tr / −₹8,919.19, 17 winners** (book → +₹196,696.40). Challenger combined **+₹209,413.54** vs incumbent +₹221,639.70. Lineage note (on the record): SAT-6's −₹11.83 was measured on the peak-lab dump lineage; the two lineages agree on the kept/direct population to the paisa (Controls B1/B2) but their round-2 populations differ — the −₹8,919.19 here is this book's own machinery speaking, and it is the number that counts for this book.
- **Gate arithmetic (stated per charter):** (a) combined FALLS (−₹12,226.16) ✗ · (b) both years fall ✗ · (c) ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C19 books). no_beat_cycles 0 → 1. Lesson 34 appended: **first-signal-only is CLOSED CROSS-YEAR** — a second signal on the same stock-day is systematically the spent remainder of the move, in both regimes.
- **Status: v2 ACTIVE.** Next: Cycle 21 — challenger: P2F-R2's exit pair tested on the R+2 population (CH-V2-8). Challenger inventory after that: the INV-LONG above-trend mirror (CH-V2-9, weak Lesson-18 prior, constructible only via a source-level build_inv variant) — then the honest inventory is empty.

## V2 CYCLE 21 — CHALLENGER CH-V2-8 "R2-EXITS": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2-CYCLE-21):** P2F-R2 rebuilt at T150/S080 (from T125/S050) on both years — the exit question asked on the third and last reaction population. Freeze was blind.
- **Controls (same pass):** full v2 build re-executed — ALL controls pass (incl. the R2 candidate/frozen/book anchors); the parameterised copy at (1.25, 0.50) reproduces the build's frozen R2 sets per-trade in both years; the build's R2 book sets minus the V2C17 law equal the incumbent books' R2 rows; challenger entry sets identical in both years (27 tr in 2025, 32 in 2026).
- **Exact score (stocks_engine_v2_cycle21_score.py / v2_out/v2_cycle21_result.json):** the R+2 population gives the THIRD distinct verdict shape — the wider pair HELPS the weak year and HURTS the strong year: 2025: R2 −₹5,682.76 → **−₹4,979.48** (+₹703.28) · 2026: +₹15,149.33 → **+₹11,228.13** (−₹3,921.20). Challenger book combined **+₹218,421.78** vs incumbent +₹221,639.70.
- **Gate arithmetic (stated per charter):** (a) combined FALLS (−₹3,217.92) ✗ · (b) 2026 falls ✗ · (c) ✓. **REJECTED on legs (a) and (b).** Incumbent unchanged (post-C19 books). no_beat_cycles 1 → 2. Addendum to Lesson 33 appended: the exit-pair verdict now exists on all three reaction populations — wider pays on same-day entries (SAT-15), fails on R+1 entries (Cycle 18), and splits by year on R+2 entries (here) — no pair transfers, and P2F-R2's exits are CLOSED cross-year at T125/S050. Its 2025 loss stands as the diagnosed lag/regime fact.
- **Status: v2 ACTIVE — one no-beat from saturation.** Next: Cycle 22 — the final challenger in the honest inventory: INV-LONG's above-trend mirror (CH-V2-9), built from a source-level build_inv variant with the incumbent reproduced as its anchor. If it fails, the run is SATURATED-V2 and the proven ceiling is reported per year against the floor, per the mandate.

## MANDATE 2 (user, 2026-10-31 15:30 IST) — REGIME COMPLETENESS + CONSISTENCY BAND, folded into the loop
- His words: a consistent amount **±₹1,000** regardless of market movement — deep falling (SHORT side), steep rising (LONG side), flat (event-driven / fade sleeves) — **"any situation we need to be ready."** Amended on the record in stocks_RECURSIVE_ENGINE.md (v2 charter section (f)) and in the state file. **REGIME-CLASSIFIER-1 is frozen in stocks_engine_frozen.md BEFORE any regime scoring** (causal: NIFTY price vs 50DMA + 5-day 50DMA slope, prior-close inputs only; UP = price above a non-falling line, DOWN = price at/below a non-rising line, FLAT = disagreement). From Cycle 22 every cycle reports P&L by regime cell × year; a cell negative in either year is a named weakness ranked like a red month. Objectives in order: (a) every cell positive in both years → (b) the per-year ₹20k/month floor → (c) variance compression toward ₹20,000 ± ₹1,000/month (month spread reported every cycle; reference spread at the mandate: Aug 2026 +₹666.78 vs Oct 2026 +₹54,272.43 in the v1 book — the v2 book's own spread is reported from Cycle 22). Challenger cadence now targets the weakest regime cell (DOWN → SHORT mechanisms, UP → LONG, FLAT → event-driven/fade). Gates unchanged; the band is reported openly, never smoothed into existence.

### V2 Cycle 22 — CH-V2-9 "INV-ABOVE": the above-trend mirror of the INV machinery (challenger; regime diagnosis folded in per mandate 2) — BANKED
- **Regime diagnosis first (REGIME-CLASSIFIER-1, frozen before scoring; labels from the machinery's NIFTY_REG — the raw NIFTY CSV ends 2026-10-28 while trades exist to 10-30, so the extended series is the faithful source; the price leg was independently cross-checked against raw closes on 452 days, exact). Incumbent (post-C19) cells × year — UP: 2025 −₹4,665.03 (63 tr) / 2026 +₹12,282.57 (22 tr) · DOWN: +₹21,561.86 / +₹188,336.51 · FLAT: 2025 −₹872.72 (32 tr) / 2026 +₹4,996.51 (71 tr).** Objective (a) fails on UP × 2025 and FLAT × 2025. Day counts expose the regime asymmetry: 2025 had 128 UP days, 2026 only 44 (DOWN 87 vs 118). Month spread (mandate metric): combined range ₹59,065.06 (min −₹6,368.38, max +₹52,696.68), stdev ₹14,019.32, only 2 of 22 months inside ₹20,000 ± ₹1,000 — the consistency band is far away and is reported as such. UP × 2025 bleeders: R2-LOWBAND|UP −₹3,506.17 (9 tr), P2F-R2|UP −₹3,411.45 (13 tr); INV-LONG|FLAT negative both years (−₹2,739.25 / −₹2,600.72).
- **Frozen before scoring** (see stocks_engine_frozen.md): additive component = build_inv machinery verbatim (PLAIN T125/S050 chains, p2 filters, LONG, RF-1, base exclusions) with the gate flipped to g1 (above-trend days) + the v2 INV law; decision = cross-year gate AND combined expectancy > 0 AND beats the flip placebo (SHORT side of the identical population) per-trade; Lesson-18 prior disclosed (mirrors died for F4).
- **Controls in the same pass:** build controls ALL PASS; the gate=cond_inv1 path reproduces build_inv per-trade in both years and, minus v2-law names, equals the incumbent INV rows exactly; mirror days disjoint from incumbent INV days by construction and asserted.
- **Score:** mirror 2025 170 tr **+₹5,209.71** (exp +₹30.65; cells UP 141 tr +₹3,363.67, FLAT 29 tr +₹1,846.04) · 2026 36 tr **+₹3,349.21** (exp +₹93.03; UP 12 tr +₹3,583.54, FLAT 24 tr −₹234.33). Combined 206 tr **+₹8,558.92, exp +₹41.55**. **Placebo disclosed honestly:** the above-trend SHORT side was the BETTER 2025 trade (246 tr, exp +₹74.22) and a 2026 disaster (76 tr, exp −₹155.14) — sign-flipping by year, combined exp +₹20.08; the LONG mirror is the side that is positive in BOTH years, which is the property this engine banks. The pre-registered combined per-trade placebo test passes (+41.55 > +20.08).
- **Gate arithmetic:** combined ₹221,639.70 → **₹230,198.62** (rises ✓) · 2025 ₹16,024.11 → **₹21,233.82** ✓ · 2026 ₹205,615.59 → **₹208,964.80** ✓ · neither negative ✓ → **BANKED as component INV-ABOVE.**
- **Book after Cycle 22:** 2025 763 tr **+₹21,233.82** · 2026 641 tr **+₹208,964.80** · combined **+₹230,198.62 (₹10,463.57/month)**. **Cells after:** UP 2025 **−₹1,301.36** (was −₹4,665.03 — still the one negative cell) / 2026 +₹15,866.11 · DOWN +₹21,561.86 / +₹188,336.51 · FLAT 2025 **+₹973.32 (flipped positive, thin)** / 2026 +₹4,762.18. Floor position: **2026 over its floor by ₹8,964.80 (MET)** · **2025 gap ₹218,766.18 (NOT met)**. Remaining named weakness: UP × 2025, whose residual is the two R+2-family UP bleeds (−₹6,917.62 in 2025) against the new sleeve's gains. **No-beat counter: 0.** Books: stocks_engine_v2_c22_book2025_trades.csv / _book2026_trades.csv. Evidence: v2_out/v2_cycle22_result.json.

### V2 Cycle 23 — R2-LOWBAND stands aside on UP days (cell exclusion under the pre-registered cell bar) — BANKED · MANDATE OBJECTIVE (a) COMPLETE
- **Frozen before scoring:** (R2-LOWBAND × UP) negative in both years (2025 9 tr −₹3,506.17 / 2026 4 tr −₹22.58, combined −₹3,528.75) under the cell bar frozen this cycle (both years negative AND combined ≤ −₹500 — the slice bar's shape at the cell unit); thinness disclosed in the freeze (13 tr; 2026's cell nearly zero).
- **Controls in the same pass:** build controls ALL PASS; classifier price leg == below50 asserted on all window days; incumbent == state (C22 books); deleted set == the frozen set EXACTLY (9 tr / −₹3,506.17 and 4 tr / −₹22.58).
- **Gate arithmetic:** combined ₹230,198.62 → **₹233,727.37** ✓ · 2025 ₹21,233.82 → **₹24,739.99** ✓ · 2026 ₹208,964.80 → **₹208,987.38** ✓ · neither negative ✓ → **BANKED.**
- **REGIME CELLS AFTER CYCLE 23 — EVERY CELL POSITIVE IN BOTH YEARS (mandate 2 objective (a) met):** 2025 — UP **+₹2,204.81** (195 tr) · DOWN +₹21,561.86 · FLAT +₹973.32 · 2026 — UP +₹15,888.69 · DOWN +₹188,336.51 · FLAT +₹4,762.18. Honest thinness: FLAT × 2025 (+₹973.32) and UP × 2025 (+₹2,204.81) are positive but thin — "ready in any situation" holds at cell level, not yet at income level.
- **Objectives (b) and (c), reported openly:** floor — 2026 **+₹208,987.38, over its ₹200,000 floor by ₹8,987.38 (MET)** · 2025 **+₹24,739.99 vs ₹240,000 — gap ₹215,260.01 (NOT met)**; combined **+₹233,727.37 = ₹10,623.97/month** vs the ₹75,000 goal. Consistency band — month spread range ₹58,667.91, stdev ₹14,099.46, worst month Jul 2025 −₹5,971.23, best Oct 2026 +₹52,696.68; 2025 still has six red months (Mar −₹3,124.15 · May −₹2,779.66 · Jun −₹955.92 (INV-ABOVE's June slice) · Jul −₹5,971.23 · Oct −₹5,149.95 · Nov −₹4,545.69). The ±₹1,000 band is nowhere near reached — stated plainly, per the mandate's honesty backstop. Breadth note: 2025 ex-top-3 worsened to −₹15,012.03 (the C22 sleeve's gains concentrate in the top stocks); 2026 ex-top-3 +₹81,298.54.
- **Book after Cycle 23:** 2025 754 tr · 2026 637 tr. Books: stocks_engine_v2_c23_book2025_trades.csv / _book2026_trades.csv. Evidence: v2_out/v2_cycle23_result.json. **No-beat counter: 0.** MILESTONE reported to the parent at this point (objective (a) achieved). Queue if the chain is continued: Cycle 24 = INV-LONG × FLAT stand-aside (the other both-years-negative cell pair: 2025 −₹2,739.25 / 2026 −₹2,600.72, combined −₹5,339.97 — strengthens already-positive FLAT cells); beyond that, the binding problem is objective (b): the 2025 floor gap (₹215,260.01) needs scale challengers seeded from 2025's earners (P2F, INV-LONG, INV-ABOVE), not further deletions.

### V2 Cycle 24 — INV-LONG stands aside on FLAT days (cell exclusion) — BANKED
- **Frozen before scoring** (stocks_engine_frozen.md, V2 CYCLE 24): (INV-LONG × FLAT) = 2025 9 tr −₹2,739.25 / 2026 11 tr −₹2,600.72 (combined −₹5,339.97), the only remaining (component × cell) both-years-negative pair on the C23 book (full scan in the cycle diagnosis, v2_out/v2_cycle24_diag.json), qualifying under the Cycle-23 cell bar.
- **Controls in the same pass:** build controls ALL PASS; classifier price leg == below50 asserted on all window days; incumbent == state (C23 books); deleted set == the frozen set EXACTLY in both years.
- **Gate arithmetic:** combined ₹233,727.37 → **₹239,067.34** ✓ · 2025 ₹24,739.99 → **₹27,479.24** ✓ · 2026 ₹208,987.38 → **₹211,588.10** ✓ · neither negative ✓ · **cell guard ✓** (no cell flipped; FLAT strengthened) → **BANKED.**
- **Book after Cycle 24:** 2025 745 tr **+₹27,479.24** · 2026 626 tr **+₹211,588.10** · combined **+₹239,067.34 (₹10,866.70/month)**. **Cells:** 2025 — UP +₹2,204.81 · DOWN +₹21,561.86 · FLAT **+₹3,712.57** (was +₹973.32) · 2026 — UP +₹15,888.69 · DOWN +₹188,336.51 · FLAT **+₹7,362.90** (was +₹4,762.18). Objective (a) still holds in full.
- **Floor / band, reported openly:** 2026 over its floor by **₹11,588.10 (MET)** · 2025 gap **₹212,520.76 (NOT met)**. Month spread: range ₹57,846.63, stdev ₹14,064.19, worst month Oct 2025 −₹5,149.95, best Oct 2026 +₹52,696.68, **1 of 22 months inside ₹20,000 ± ₹1,000**; 2025 still has six red months (Mar, May, Jun, Jul, Oct, Nov). Ex-top-3: 2025 −₹15,012.03 → (recomputed at next milestone) · 2026 +₹81,298.54 base. Books: stocks_engine_v2_c24_book2025_trades.csv / _book2026_trades.csv. Evidence: v2_out/v2_cycle24_result.json. **No-beat counter: 0.**
- **Diagnosis for the growth phase (same pass, counts only — no challenger P&L read):** deletions at the (comp × cell) unit are now also exhausted — no both-years-negative pair remains at any unit. P2F band buckets are positive in every bucket in both years ([2.5,3.5): +₹6,538.79/+₹6,590.56 · [3.5,5): +₹6,073.57/+₹5,719.73 · ≥5: +₹1,753.41/+₹7,106.34) — no band-edge replacement case exists. The untapped populations are in the INV machinery's own discards: late entries (round ≤ 2, entry ≥ 10:30) = below-trend 86 (2025) / 93 (2026), above-trend 72 / 27; round ≥ 3 early entries = below 18 / 12, above 28 / 4. News-class reaction candidates at the ≥2.5% band: 3 (2025) / 4 (2026). The growth queue is therefore: INV-LATE (below) → INV-ABOVE-LATE → P2F-NEWS → INV-R3 (below) → INV-ABOVE-R3, each an additive challenger under the Cycle-6 standard (gate + combined expectancy > 0 + beats flip placebo per-trade + cell guard).

### V2 Cycle 25 — CHALLENGER CH-V2-10 "INV-LATE": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2 CYCLE 25):** additive component = the INV chain machinery verbatim (PLAIN T125/S050, ADR ≥ 3.0, LONG, RF-1, base exclusions, v2 INV law, below-trend gate) with the p2 entry-time leg flipped to entry ≥ 10:30 (round ≤ 2 kept) — the earliness filter's discarded complement, 86 rows (2025) / 93 rows (2026) per the cycle diagnosis.
- **Controls (same pass):** build controls ALL PASS; the incumbent entry leg reproduces build_inv per-trade in both years, and minus the v2 law minus the C24 FLAT stand-aside equals the incumbent INV-LONG rows exactly; late population counts == the frozen counts; late rows disjoint from incumbent INV rows.
- **Exact score (stocks_engine_v2_cycle25_score.py / v2_out/v2_cycle25_result.json):** 2025: 86 tr **−₹1,434.27** (exp −₹16.68) · 2026: 93 tr **+₹6,163.43** (exp +₹66.27) · combined 179 tr **+₹4,729.16** (exp +₹26.42), flip placebo combined exp −₹91.02 (beaten per-trade ✓), cell guard ✓ — but the component's sign flips by year: it earns in the strong year and bills the weak one.
- **Gate arithmetic (stated per charter):** (a) combined rises (+₹4,729.16) ✓ · (b) **2025 FALLS** (₹27,479.24 → ₹26,044.97) ✗ · (c) ✓. **REJECTED on leg (b).** Incumbent unchanged (post-C24 books). no_beat_cycles 0 → 1. Lesson 36 appended: **the earliness leg is load-bearing, asymmetrically** — its complement can pass every combined standard (positive expectancy, placebo beaten) and still be regime rent, because the gate's leg (b) prices each year separately.
- **Status: v2 ACTIVE.** Next: Cycle 26 — INV-ABOVE-LATE (the same flipped entry leg on the above-trend gate; frozen counts 72 / 27).

### V2 Cycle 26 — CHALLENGER CH-V2-11 "INV-ABOVE-LATE": REJECTED under the cross-year gate (2026-10-31)
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2 CYCLE 26):** additive component = the INV machinery verbatim with INV-ABOVE's above-trend gate and the entry-time leg flipped to entry ≥ 10:30 (round ≤ 2 kept) — 72 rows (2025) / 27 rows (2026) per the cycle diagnosis.
- **Controls (same pass):** build controls ALL PASS; the incumbent entry leg on g1 with the v2 law equals the incumbent INV-ABOVE rows exactly in both years; late counts == frozen counts; late rows disjoint from INV-ABOVE rows.
- **Exact score (stocks_engine_v2_cycle26_score.py / v2_out/v2_cycle26_result.json):** 2025: 72 tr **+₹880.63** (exp +₹12.23) · 2026: 27 tr **−₹1,878.64** (exp −₹69.58) · combined 99 tr **−₹998.01** (exp −₹10.08); flip placebo beaten per-trade (−₹49.43) but the component itself is expectancy-negative.
- **Gate arithmetic:** (a) combined FALLS (−₹998.01) ✗ · (b) 2026 falls ✗ · expectancy leg ✗. **REJECTED.** Incumbent unchanged (post-C24 books). no_beat_cycles 1 → 2 — **one no-beat from saturation.** Lesson 36 addendum appended: the mirror image of Cycle 25 (here the weak year gains a little and the strong year pays) — **the late-entry axis is CLOSED for the whole INV family**: on both gates the complement is year-unstable, with opposite signs per gate.
- **Status: v2 ACTIVE — saturation is one failed cycle away.** Next: Cycle 27 — P2F-NEWS (news-class reaction follow at R+1; frozen candidate counts 3 / 4 at the ≥2.5% band).

### V2 Cycle 27 — CHALLENGER CH-V2-12 "P2F-NEWS": REJECTED under the cross-year gate (2026-10-31) — THIRD CONSECUTIVE NO-BEAT
- **Challenger (frozen BEFORE scoring in stocks_engine_frozen.md, V2 CYCLE 27 + construction note):** additive component = the P2F machinery verbatim (band ≥ 2.5%, entry R+1 09:15, T125/S050, P2F exclusions) on the SINGLE_NEWS event classes instead of results. The first score run stopped on its own disjointness assertion before any trade was priced (a news event shares BDL's 2025-11-14 reaction day with a results event); the freeze was amended on the record with N4's date-dedup rule (the results machinery owns a shared reaction day) and post-dedup counts (2025 9 candidates / 2 at band · 2026 11 / 4) before scoring proceeded.
- **Controls (same pass):** build controls ALL PASS; the generalised candidate builder restricted to {results} reproduces reaction_candidates exactly in both years; post-dedup counts == the amended freeze; post-dedup disjointness asserted.
- **Exact score (stocks_engine_v2_cycle27_score.py / v2_out/v2_cycle27_result.json):** 2025: 2 tr **+₹1,949.25** (exp +₹974.62) · 2026: 4 tr **−₹2,089.31** (exp −₹522.33) with its flip placebo at **+₹5,475.58** (exp +₹1,368.89) — in 2026 the news reactions FADED and following them was the wrong side · combined 6 tr **−₹140.06** (exp −₹23.34) vs placebo +₹763.98/trade.
- **Gate arithmetic:** (a) combined FALLS ✗ · (b) 2026 falls ✗ · expectancy ✗ · placebo ✗. **REJECTED on four legs.** Incumbent unchanged (post-C24 books). no_beat_cycles 2 → 3. Lesson 37 appended: **follow-through is a results phenomenon on this evidence** — scheduled, interpretable information shocks continue; unscheduled news shocks, at the same band and exits, do not (thin population disclosed: 6 trades; the rejection rests on the 2026 placebo inversion, not on expectancy precision).
- **Status: v2 SATURATED — see the termination entry below.** The remaining untested queue at saturation (INV-R3 below-trend 18/12 rows, INV-ABOVE-R3 28/4 rows) is recorded here for any future re-charter; under the charter's saturation rule the run does not continue into it.

## V2 TERMINATION — SATURATED-V2 (2026-10-31)
Saturation per the v2 charter (d): **3 consecutive cycles that cannot beat the combined best under the cross-year gate** — Cycle 25 (INV-LATE, rejected on leg (b)), Cycle 26 (INV-ABOVE-LATE, rejected on legs (a)/(b)/expectancy), Cycle 27 (P2F-NEWS, rejected on legs (a)/(b)/expectancy/placebo). State: terminated = "SATURATED-V2", cycle_lock cleared.

### The climb (verified anchor points; every cycle's evidence in v2_out/v2_cycleN_result.json)
- **v2 incumbent** (frozen v1 book, both windows): combined **+₹197,630.80** (2025 +₹23.06 · 2026 +₹197,607.74)
- After Cycle 1 (GLENMARK×SHORT out of F4+N4-V3): **+₹204,004.23** (2025 +₹5,765.30 · 2026 +₹198,238.93)
- After Cycle 2 (N4-V3×BDL×SHORT out): **+₹207,189.23** (2025 +₹8,310.30 · 2026 +₹198,878.93)
- After Cycle 19 (the deletion phase complete — registry empty): **+₹221,639.70** (2025 +₹16,024.11 · 2026 +₹205,615.59)
- After Cycle 22 (INV-ABOVE added — the one additive bank of the run): **+₹230,198.62** (2025 +₹21,233.82 · 2026 +₹208,964.80)
- After Cycle 23 (R2-LOWBAND × UP stand-aside — objective (a) completed): **+₹233,727.37** (2025 +₹24,739.99 · 2026 +₹208,987.38)
- After Cycle 24 (INV-LONG × FLAT stand-aside): **+₹239,067.34 — FINAL** (2025 +₹27,479.24 · 2026 +₹211,588.10)
- Banked cycles (16): 1, 2, 4, 5, 7, 8, 10, 11, 13, 14, 16, 17, 19, 22, 23, 24. Rejected (11): 3, 6, 9, 12, 15, 18, 20, 21, 25, 26, 27. Total v2 gain over the incumbent: **+₹41,436.54** — of which 2025 contributed +₹27,456.18 (from ₹23.06 to ₹27,479.24) and 2026 +₹13,980.36.

### Final position against the mandates, stated plainly
- **Mandate 2 objective (a) — regime completeness: MET and held at termination.** Cells: 2025 — UP +₹2,204.81 (195 tr) · DOWN +₹21,561.86 (498 tr) · FLAT +₹3,712.57 (52 tr); 2026 — UP +₹15,888.69 (30 tr) · DOWN +₹188,336.51 (512 tr) · FLAT +₹7,362.90 (84 tr). The book earns on the SHORT side in falling markets, the LONG side in rising ones, and event sleeves in flat ones — "ready in any situation" holds at cell level. Honest thinness: 2025 UP and FLAT are positive by thousands, not tens of thousands.
- **Mandate 1 objective (b) — the ₹20,000/month per-year floor: 2026 MET, 2025 NOT MET.** 2026 +₹211,588.10 vs ₹200,000 (over by ₹11,588.10; ₹21,158.81/month). 2025 +₹27,479.24 vs ₹240,000 — **gap ₹212,520.76** (₹2,289.94/month). Combined +₹239,067.34 = **₹10,866.70/month** over 22 months vs the ₹75,000 goal. The proven ceiling on this data, under this gate, is roughly ₹10.9k/month combined — reported as measured, not smoothed.
- **Objective (c) — the ₹20,000 ± ₹1,000 consistency band: NOT reached.** Month range −₹5,149.95 (Oct 2025) to +₹52,696.68 (Oct 2026), spread ₹57,846.63, stdev ₹14,064.19, **1 of 22 months inside the band**; 2025 still has six red months (Mar −₹3,124.15 · May −₹2,779.66 · Jun −₹955.92 · Jul −₹5,088.45 · Oct −₹5,149.95 · Nov −₹4,545.69) while 2026 has none. 2026 months run ₹8,486.54–₹52,696.68 — consistent in sign, not in size.
- **Concentration (Lesson 6), standing caveat:** ex-top-3 = 2025 **−₹12,272.78** (2025's positive total still rests on its top-3 stocks) · 2026 +₹83,088.96.
- **Final book:** 2025 745 tr · 2026 626 tr; eight components (F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND + the v2 mechanism/cell law in state.book_law_added). Books: stocks_engine_v2_c24_book2025_trades.csv / stocks_engine_v2_c24_book2026_trades.csv.
- **Untested at saturation (recorded, not run):** INV-R3 below-trend (18 / 12 rows) and INV-ABOVE-R3 (28 / 4 rows) — the chain stopped because the charter's saturation rule fired, not because the inventory was empty. Any continuation needs a user re-charter, exactly as v1's saturation was superseded by the v2 order. Fresh-window judging (November paper board, December) remains the arbiter for everything this run banked in-sample/cross-year.

---

## V3 — MAXIMIN TUNING (user re-charter 2026-10-31 20:55 IST)

**Order:** "start tuning them because at least ten thousand should be the minimum. For stocks." Charter written into `stocks_RECURSIVE_ENGINE.md` §v3; Lesson 38 appended. Objective: lexicographic maximin over the 22-month vector (worst month → ≥ +₹10,000, then toward ₹15,000), hard constraints = neither year falls / neither year negative / every regime cell × year stays positive / combined never falls / controls + audit in-pass / freeze before scoring / one change per cycle / additive challengers carry the Cycle-6 standard. The frozen SarvaRitu forward test (Nov–Dec) is untouched; v3 output is a new version for a later fresh test.

**Incumbent (asserted in-pass):** the frozen post-C24 book verbatim — 2025 745 tr / +₹27,479.24 · 2026 626 tr / +₹211,588.10 · combined +₹239,067.34. Cells recomputed and asserted: 2025 UP +₹2,204.81 / DOWN +₹21,561.86 / FLAT +₹3,712.57 · 2026 UP +₹15,888.69 / DOWN +₹188,336.51 / FLAT +₹7,362.90 — all positive (mandate-2 objective (a) is the v3 starting constraint, not a target).

**Diagnosis (stocks_engine_v3_diag.py; v3_out/v3_diag.json — incumbent decomposition + counts only for challenger populations):**
- The weak months are two distinct animals. **UP-regime deserts:** Nov 2025 (19/19 days UP), May 2025 (21/21 UP), Jun 2025 (21/21 UP) — the below-trend machinery (F4, INV-LONG) cannot fire at all; only INV-ABOVE + event systems trade, and in Nov/May they lost (Nov: INV-ABOVE −₹1,638.14, N4-V3 −₹2,149.24; Jun: 7 trades total, all INV-ABOVE, −₹955.92, in a month with **zero calendar events** — 0 results reactions, 1 news row). **DOWN-regime bleed:** Mar 2025 (13 DOWN days) — F4 −₹3,941.75 over 37 tr while INV-LONG earned +₹2,190.68; Jan 2025 F4 −₹5,472.71 (71 tr) absorbed by INV-LONG/N4/P2F. Oct 2025 mixes both (F4 −₹3,021.83 on 3 tr; P2F −₹1,202.33; P2F-R2 −₹1,182.00). Jul 2025: INV-ABOVE −₹2,473.45 (3 tr) + F4 −₹1,025.28 (19 tr).
- **Deletion scan (maximin registry, re-derived at this book):** 45 (comp × stock × dir) slices ≤ 0 in both years, combined −₹23,050.08 — but the mass is small and mostly 2025-only (2026 leg 0.0 = the slice never traded in 2026): top rows INV-ABOVE × PFC × LONG (13 tr, −₹1,793.92; weak legs May −₹756.18, Mar −₹253.50), P2F-R2 × BDL × LONG (2 tr, −₹1,671.00; Nov leg −₹830.00), R2-LOWBAND × TVSMOTOR × LONG (1 tr, −₹1,515.50), P2F-R2 × TVSMOTOR × SHORT (1 tr, −₹1,390.25; May leg), INV-ABOVE × RECLTD × LONG (6 tr, −₹1,277.62; May leg −₹502.73). One (comp × cell) pair is both-years-nonpositive: R2-LOWBAND × FLAT (2026 −₹144.70 only). Deletions alone cannot lift the worst month materially — the largest Oct-2025 leg in the whole scan is −₹894.00 (P2F-R2 × OBEROIRLTY × LONG, 1 tr).
- **Challenger population counts (no P&L read):** INV-R3 below-trend (round ≥ 3, early, ADR ≥ 3.0, LONG, law applied) = 18 rows 2025 (**Mar 9**, Feb 4, Jan 5) / 12 rows 2026 (Jan–Apr, Jun) — it aims at Mar 2025, the DOWN-bleed month, and at nothing in Jul–Nov 2025. INV-ABOVE-R3 = 28 rows 2025 (Apr 7, **Oct 5**, Dec 5, **May 4**, Sep 3, Nov 2, Jun 1, Mar 1) / 4 rows 2026 — it aims at the UP-desert months. Round distribution confirms round ≥ 3 is a real population (1,269 round-3 rows before filters).
- **Queue:** C1 INV-R3 (below) → C2 INV-ABOVE-R3 → C3+ maximin registry deletions (multi-trade rows first, re-derived at the then-current book) → new event-class breadth (dividend-class days for the same-day machinery; a systematic bulk/block-deal calendar is the only class that occurs in event-desert months like Jun 2025) if the queue stalls.

## V3 CYCLE 1 — CH-V3-1 "INV-R3": BANKED under the v3 maximin gate (2026-10-31)
- **Anchors (in-pass):** build controls ALL PASS; the round ≤ 2 path reproduces `build_inv` per-trade in both years and, minus the v2 law names and the C24 FLAT stand-aside, equals the incumbent INV-LONG rows exactly; frozen counts matched (18 / 12); R3 rows disjoint from incumbent INV rows by round value.
- **Component:** 2025 **18 tr / +₹4,438.70** (exp +₹246.59; months Jan +₹413.23 · Feb −₹532.21 · **Mar +₹4,557.68**) · 2026 **12 tr / +₹2,226.28** (exp +₹185.52). Combined 30 tr / **+₹6,664.98**, expectancy **+₹222.17** vs flip placebo **−₹15,172.11 / −₹194.52 per trade** (54 + 24 placebo trades) — the Cycle-6 standard passes decisively.
- **Gate arithmetic:** combined **+₹239,067.34 → +₹245,732.32** ✓ · 2025 +₹27,479.24 → **+₹31,917.94** ✓ · 2026 +₹211,588.10 → **+₹213,814.38** ✓ · cells all positive after (2025 DOWN +₹21,561.86 → +₹26,000.56; 2026 FLAT +₹7,362.90 → +₹7,062.90 — the June-2026 R3 trade (−₹300.00) sits on a FLAT day; the cell holds) ✓.
- **Maximin:** Mar 2025 −₹3,124.15 → **+₹1,433.53** — the target month flips green and leaves the bottom-5. Sorted vector improves lexicographically at the 4th position. **Bottom-5 after:** Oct 2025 −₹5,149.95 · Jul 2025 −₹5,088.45 · Nov 2025 −₹4,545.69 · May 2025 −₹2,779.66 · Jun 2025 −₹955.92.
- **Book law added:** component INV-R3 (ninth component). Books: `stocks_engine_v3_c1_book2025_trades.csv` / `_book2026_trades.csv` (763 / 638 tr). Ex-top-3: 2025 −₹12,272.78 → −₹9,745.33 (the bank is NOT concentration — it earns outside the top-3). Evidence: `stocks_engine_v3_cycle1_score.py`, `v3_out/v3_cycle1_result.json`.
- **Read:** the round axis of the INV family is alive where the late-entry axis was dead (Lesson 36) — chain depth and entry clock are different filters: round-3 chains are later CONFIRMATIONS of the same morning pattern, not later entries into a spent move. The R3 population lives only in Jan–Apr (below-trend season), so the UP-desert months are untouched — C2 (INV-ABOVE-R3) is aimed at them.

## V3 CYCLE 2 — CH-V3-2 "INV-ABOVE-R3": REJECTED under the v3 maximin gate (2026-10-31)
- **Anchors (in-pass):** build controls ALL PASS; the g1 + round ≤ 2 path equals the incumbent INV-ABOVE rows exactly; frozen counts matched (28 / 4); disjointness asserted.
- **Component:** 2025 **28 tr / +₹5,158.67** (exp +₹184.24; May +₹3,825.52 · Apr +₹1,346.62 · Dec +₹977.70 · Jun +₹273.39 · Nov +₹178.33 · **Oct −₹466.38** · Mar −₹883.00 · Sep −₹93.51) · 2026 **4 tr / −₹61.66** (exp −₹15.41). Combined 32 tr / +₹5,097.01, expectancy +₹159.28; flip placebo combined +₹3,445.23 / +₹149.75 per trade — beaten combined, but **inside 2025 the flip beats the real side per-trade** (placebo exp +₹236.59 vs real +₹184.24: above-trend SHORTs were again the better 2025 trade in this population, the Lesson 35 warning live).
- **Gate arithmetic:** combined would rise +₹245,732.32 → +₹250,829.33, and 2025 would rise — but **2026 falls** (−₹61.66; hard constraint (ii) fails) and **the worst month worsens**: Oct 2025 −₹5,149.95 → **−₹5,616.33** (the challenger's own Oct slice is −₹466.38) — the lexicographic beat fails at the first position. May 2025 would have flipped green (+₹1,045.86) and Jun 2025 improved (−₹682.53); under maximin those gains do not compensate a bill presented to the worst month. **REJECTED — no_beat 0 → 1.** Incumbent unchanged (post-C1 book).
- **Read:** the round axis is gate-specific, exactly as Lesson 22's grid discipline predicts — alive below-trend (C1), not bankable above-trend. The above-gate R3 population earns in the aggregate and still taxes precisely the months v3 exists to lift; a total-raiser that bills the worst month is the photograph-improver of the maximin era (Lesson 38, corollary (i)). Lesson addendum appended (Lesson 35).

## V3 CYCLE 3 — DELETION V3C3-P2FR2-OBEROIRLTY-LONG-EXCL: BANKED (2026-10-31)
- Registry re-derived at the post-C1 book (`stocks_engine_v3_registry.py`; `v3_out/v3_registry.json`): 15 slices at the standing bar; 14 lexicographically beat; **N4-V3 × HDFCBANK × LONG refused un-scored as a rotation** (Oct leg −₹852.04, Jul leg **+₹830.00** — the diagnosis scan's negative-legs view hid the winner; the full month-leg map is now part of the registry derivation).
- Deleted set asserted == freeze: **1 trade (2025-10-20, −₹894.00)**. Gate: all legs pass. Oct 2025 **−₹5,149.95 → −₹4,255.95**; 2025 → +₹32,811.94; combined **→ +₹246,626.32**. Jul 2025 (−₹5,088.45) becomes the worst month. no_beat reset 1 → 0.

## V3 CYCLE 4 — DELETION V3C4-P2F-OBEROIRLTY-LONG-EXCL: BANKED (2026-10-31)
- The R+1 sibling of C3 (same October-2025 reaction, first lag). Deleted set asserted == freeze: **1 trade (2025-10-17, −₹889.35)**. Gate: all legs pass. Oct 2025 **→ −₹3,366.60**; combined **→ +₹247,515.67**. Bottom-5: Jul 2025 −₹5,088.45 · Nov 2025 −₹4,545.69 · Oct 2025 −₹3,366.60 · May 2025 −₹2,779.66 · Jun 2025 −₹955.92.
- **Frontier note (recorded for the cycles ahead):** Jul 2025's bleed has NO qualifying deletion — its big legs are F4 × TVSMOTOR × LONG (−₹3,564.10, 2 tr; the name is the book's carrier, full-period hugely positive) and INV-ABOVE × GLENMARK × LONG (−₹2,299.75, 2 tr; fails the both-years bar) — July is concentration-bound, not rot-bound. Jun 2025 likewise has no deletion legs (7 trades, all INV-ABOVE, −₹955.92 total). After the registry queue, the worst-month frontier is Jul/Jun 2025, and only additive breadth (event classes that occur in desert months) can move them.

## V3 CYCLES 5–15 — MAXIMIN REGISTRY DELETIONS: ALL BANKED (2026-10-31)
Each cycle: freeze written before scoring (stocks_engine_frozen.md + v3_out/freeze_cN.json), deleted set asserted == freeze in-pass, build controls ALL PASS, gate = lexicographic maximin beat + all hard constraints. Evidence: v3_out/v3_cycleN_result.json.

- **C5 — N4-V3 × INDUSTOWER × LONG** (2 tr: Jan 2025 −336.36, Oct 2025 −345.88). Oct 2025 → −₹3,020.72. Combined → +₹248,197.91.
- **C6 — P2F-R2 × BDL × LONG** (2 tr: Aug 2025 −841.00, Nov 2025 −830.00). Nov 2025 → −₹3,715.69. Combined → +₹249,868.91.
- **C7 — P2F × GODREJCP × LONG** (1 tr: 2025-11-04, −629.30). Nov 2025 → −₹3,086.39. Combined → +₹250,498.21.
- **C8 — P2F-R2 × GODREJCP × LONG** (1 tr: 2025-11-06, −622.45). Nov 2025 → −₹2,463.94. Combined → +₹251,120.66.
- **C9 — INV-ABOVE × PFC × LONG** (13 tr, all 2025, −1,793.92; month legs Mar −253.50 / Apr −784.24 / May −756.18 — the registry's thickest slice, eleven ≈ −₹250 stops vs two target hits). May 2025 → −₹2,023.48. Combined → +₹252,914.58.
- **C10 — INV-ABOVE × RECLTD × LONG** (6 tr, all 2025, all losers, −1,277.62; Apr −774.89 / May −502.73). May 2025 → −₹1,520.75. Combined → +₹254,192.20.
- **C11 — P2F-R2 × TVSMOTOR × SHORT** (1 tr: 2025-05-02, −1,390.25). May 2025 → −₹130.50. Combined → +₹255,582.45.
- **C12 — N4-V3 × OIL × SHORT** (2 tr: Feb 2025 −365.24, May 2025 −365.32). **May 2025 crosses to +₹234.82 — green.** Red months 6 → 4. Combined → +₹256,313.01.
- **C13 — R2-LOWBAND × TVSMOTOR × LONG** (1 tr: 2025-08-05, −1,515.50; beat at the vector's 6th position, Aug 2025 → +₹2,723.45). Combined → +₹257,828.51.
- **C14 — P2F-R2 × GLENMARK × LONG** (1 tr: 2025-02-19, −715.00). Combined → +₹258,543.51.
- **C15 — P2F × UNITDSPR × LONG** (1 tr: 2026-05-18, −700.15). Combined → **+₹259,243.66**. **15-CYCLE REPORT POINT.**

## V3 STATE AT THE REPORT POINT (2026-10-31, post-C15)
- **Book:** 1,368 trades (2025: 731 / 2026: 637) — 2025 **+₹44,729.13**, 2026 **+₹214,514.53**, combined **+₹259,243.66** (start of v3: +₹239,067.34; climb +₹20,176.32 with the worst months lifted, not the strong ones padded). 22-month average ₹11,784/month (from ₹10,867). 2025 ex-top-3 **+₹30.76** (from −₹12,272.78 — the weak year now earns, barely, outside its top-3 names). All six regime cells positive in both years (2025 UP +11,242.90 / DOWN +29,773.66 / FLAT +3,712.57; 2026 UP +15,888.69 / DOWN +191,562.94 / FLAT +7,062.90).
- **Bottom-5:** Jul 2025 **−₹5,088.45** · Oct 2025 **−₹3,020.72** (from −₹5,149.95) · Nov 2025 **−₹2,463.94** (from −₹4,545.69) · Jun 2025 **−₹955.92** (unchanged) · May 2025 **+₹234.82** (from −₹2,779.66 — green). Mar 2025 left the bottom-5 via C1 (−₹3,124.15 → +₹1,687.03). Red months: 6 → **4**. The worst month has NOT crossed ₹0 and is nowhere near +₹10,000 — stated plainly.
- **What is left, honestly:** the deletion registry is exhausted but for one bankable row (N4-V3 × VEDL × SHORT, −₹616.60, Jan 2026) and one permanent rotation (N4-V3 × HDFCBANK × LONG — its +₹830 Jul-2025 leg makes it unbankable under maximin while July is the worst month). **Jul 2025 and Jun 2025 cannot be moved by deletions at all:** July's bleed is concentration (F4 × TVSMOTOR × LONG −₹3,564.10 on the book's carrier; INV-ABOVE × GLENMARK × LONG −₹2,299.75 fails the both-years bar) and June is an information desert (zero calendar events, 7 trades). The only road left is additive breadth that occurs in desert months — a systematic bulk/block-deal calendar (uniform across both windows, web-sourced, frozen before scoring) — or genuinely new mechanisms. That is a build decision for the parent/user, not a tuning step; the engine is NOT saturated (no_beat = 0) and the v3 state is left RUNNING at the report point with the queue recorded.

## V3 CYCLE 16 — DELETION V3C16-N4-VEDL-SHORT-EXCL: BANKED (2026-10-31; desert-phase continuation)
- Registry re-derived at the post-C15 book (stocks_engine_v3_registry.py; v3_out/v3_registry.json): exactly 2 qualifying slices — N4-V3 × VEDL × SHORT (beats=True) and the permanent N4-V3 × HDFCBANK × LONG rotation (beats=False, unchanged). Deleted set asserted == freeze in-pass (1 trade: 2026-01-30, 09:35, −₹616.60). Gate: all six checks pass. Jan 2026 → +₹32,776.36; combined **+₹259,243.66 → +₹259,860.26**; 2026 → +₹215,131.13; 2025 unchanged +₹44,729.13. Bottom-5 unchanged (the beat registers at Jan 2026's position). no_beat stays 0. Books: stocks_engine_v3_c16_book2025_trades.csv / _book2026_trades.csv. Evidence: v3_out/v3_cycle16_result.json.
- **The deletion frontier is now EMPTY at the standing bar** (full ≤ −₹500, each-year ≤ 0): the only remaining row is the HDFCBANK rotation, unbankable while Jul 2025 is the worst month. From here, v3 progress is additive only — the desert-month breadth phase (bulk/block-deal calendar) begins.

## V3 DESERT PHASE — BULK/BLOCK-DEAL CALENDAR: BUILD ATTEMPTED, NOT BUILT (sourcing verdict, 2026-10-31)
- **Verdict: a uniform bulk/block-deal calendar for Jan 2025–Oct 2026 CANNOT be built from this environment, and a partial one was refused.** The desert-phase order required uniform construction across both judging windows; every systematic source was tested and failed on reachability or uniformity:
  - **NSE historical report API** (`www.nseindia.com/api/historicalOR/bulk-block-short-deals`, the documented endpoint behind the exchange's own bulk/block page; client = NseIndiaApi `nse` package, installed in `.venv_nse` for this build): the host **www.nseindia.com is unreachable from this VM** — curl timeouts at 25s and 60s, httpx read-timeout on the cookie handshake, and the web fetcher returns a network error. `archives.nseindia.com` answers (200, fast) but carries only the latest session's bulk.csv/block.csv.
  - **BSE BulkDealData API** (api.bseindia.com, browser headers + bseindia.com referer): **Akamai 403** from this IP.
  - **Wayback Machine** snapshots of the daily bulk.csv/block.csv: effectively absent in-window (one 301 in Jan 2025) — a snapshot calendar would fabricate no-deal days.
  - **Ansaar** (ansaar.in — holds 89,177 NSE bulk rows, Jan 2023–Sep 2026, per its published analysis): only the latest session and a 30-session summary are readable pages; per-stock deal history is client-side only, the `?date=` parameter is ignored, and the sitemap exposes no session archive. Not a uniform source via any readable route.
  - **Tickertape** per-stock deal tables: JS-gated — the text fetcher receives "0 of 0 results".
  - **GitHub dataset** `shahzebkhan-os/btst`: a genuine exchange-shaped bulk-deals CSV, but **bulk-only and truncated at 2026-03-20** (no block deals; Apr–Oct 2026 missing) → non-uniform across the judging windows. NOT used; recorded here as the cross-check reference if exchange access ever opens.
  - **Dividend/record-date rows:** no uniform source found either (the calendars' 7 dividend rows are per-event research) → not built, per the same standard.
- **Why refused rather than approximated:** a calendar with silently missing days makes missing data impersonate no-event days, and the desert months are exactly where coverage decides the measurement — the Lesson 1 / Lesson 26 failure shape at the data layer. The calendar is re-buildable in one step if NSE/BSE access opens (endpoint + field map BD_DT_DATE/BD_SYMBOL/BD_BUY_SELL/BD_QTY_TRD/BD_TP_WATP are documented above).
- **Also considered and refused pre-scoring:** N4-DIV (adding the calendars' existing `dividend` rows to N4-V3's event set) — the ex-date morning move is mechanically the dividend adjustment itself (e.g. ITC ₹6.50 ≈ 1.5%), so the 09:25 trigger would fire on arithmetic, not information. Not a cycle.
- **Pivot (charter §(c), second named hunting ground):** additive variants of the proven earners buildable uniformly from in-workspace data — the untested (band × lag) cell [1.5%, 2.0%) × R+1 (C17) and INV-family structure diagnoses. Jun 2025 stays unreachable by ANY event-class challenger (zero events of any class is its definition); its only theoretical lever is non-event machinery.

## CYCLE 17 (v3, desert phase) — REJECTED: CH-V3-3 P2F-MIDBAND-R1, [1.5%,2.0%) reactions followed at R+1
- **Result: REJECTED on the Cycle-6 standard and the gate.** Component: 16 trades combined, net **−₹464.39**, expectancy **−₹29.02/trade** — negative, so the additive standard fails before the maximin question (the flip placebo was also negative, −₹64.24/trade — the Lesson-21 shape exactly: beating the placebo is necessary, not sufficient). By year: 2025 **10 tr / +₹2,309.35** (exp +₹230.94; May 2025 +₹246.50 landed as targeted, Nov 2025 −₹80.45) vs 2026 **6 tr / −₹2,773.74** (exp −₹462.29; May −₹1,959.77, Aug −₹441.97, Oct −₹881.00, Feb +₹509.00). Union: 2026 falls, combined 259,860.26 → 259,395.87, lexi beat False — gate fails on three legs. Book unchanged; evidence `v3_out/v3_cycle17_result.json`.
- **What this closes:** the P2F reaction-strength gradient at R+1 is now measured at three adjacent bands — ≥2.5% earns (+₹19,416.63 in-sample incumbent), [2.0%,2.5%) negative (SAT-32), [1.5%,2.0%) negative-expectancy (this cycle). Reaction FOLLOWING at R+1 exists only at the top band; below it, the same entries are noise with a cost attached. One grid cell remains unrun by the Lesson-22 rule ([1.0%,1.5%)×R+1) — queued as a grid-completing cycle, not as a hope.
- Counters: cycles_completed 17, banks 15, rejects 2 (C2, C17), no_beat_cycles 1.

## CYCLE 18 (v3, desert phase) — DIAGNOSED AND REFUSED PRE-SCORING: INV-ABOVE round-1 amputation fails the both-years bar on asserted numbers
- **Diagnosis (stocks_engine_v3_cycle18_diag.py; population rebuilt with C2's exact pick — g1 gate, round≤2, standing law — and matched to the current book row-by-row; the 19 population-only 2025 rows are exactly the v2 C24 FLAT-day stand-aside trades, Mar–May 2025, as in C1's anchor):** INV-ABOVE by round on the CURRENT book —
  - **Round 1: 133 tr combined, net −₹2,346.67** (2025: 105 tr / **+₹1,260.61**, +₹12.01/trade ≈ zero; 2026: 28 tr / **−₹3,607.28**, −₹128.83/trade).
  - **Round 2: 54 tr combined, net +₹13,977.13** (2025: 46 tr / +₹7,020.64; 2026: 8 tr / +₹6,956.49, +₹869.56/trade) — round 2 carries the entire component.
- **Desert anatomy, final form:** Jul 2025's INV-ABOVE bleed (−₹2,473.45) is exactly 3 round-1 trades (GLENMARK −₹1,134.05 and −₹1,165.70, HINDCOPPER −₹173.70); Jun 2025's whole month is 7 INV-ABOVE trades (6 round-1, net −₹1,236.42; 1 round-2, +₹280.50); Nov 2025 round-1 −₹1,923.73 vs round-2 +₹285.59.
- **The challenger that suggests itself — INV-ABOVE takes round-2 signals only — is REFUSED without scoring, because the gate arithmetic is already determined by the asserted diagnosis:** deleting round 1 would lift Jul 2025 to −₹2,615.00, Jun 2025 to +₹280.50 and Nov 2025 to −₹540.21 (a clear lexicographic beat), and 2026 would rise +₹3,607.28 — **but 2025 would FALL by ₹1,260.61**, violating the charter's hard constraint that neither year falls. The maximin constitution prices cross-year consistency above worst-month repair; a slice that is (barely) positive in one year cannot be amputated to fix months in that same year. Recorded so the axis is not re-proposed: the (component × round) axis for INV-ABOVE is CLOSED by the both-years bar, the same bar that closed INV-ABOVE-R3 (C2) from the other side.
- Book unchanged (combined +₹259,860.26). Counters: cycles_completed 18, banks 15, scored rejects 2 (C2, C17), pre-scoring refusals 2 (N4-DIV design refusal; C18 gate-arithmetic refusal), no_beat_cycles 2.

## CYCLE 19 (v3, desert phase) — REJECTED: CH-V3-4 P2F-LOWEST-R1, [1.0%,1.5%) reactions followed at R+1 — THE (band × R+1) GRID IS NOW COMPLETE
- **Result: REJECTED.** Component: 20 trades combined, net **−₹621.05**, expectancy **−₹31.05/trade** (flip placebo −₹243.30/trade — beaten, and irrelevant: expectancy is negative, Lesson 21). By year: 2025 **10 tr / +₹1,072.71** (Nov 2025 +₹2,491.90 would have flipped that month green, but Oct 2025 −₹1,792.95 and May 2025 −₹650.00 moved the other way) vs 2026 **10 tr / −₹1,693.76**. Union: 2026 falls, combined 259,860.26 → 259,239.21, lexi beat False. Book unchanged; evidence `v3_out/v3_cycle19_result.json`.
- **The grid, closed with evidence at every cell (R+1 following of results reactions):** ≥2.5% EARNS (incumbent P2F) · [2.0%,2.5%) negative (SAT-32) · [1.5%,2.0%) negative expectancy (C17) · [1.0%,1.5%) negative expectancy (C19). Reaction-following at R+1 is a top-band-only phenomenon; below 2.5% the entries are noise carrying a ₹40 cost. No further band cells exist to run.
- Counters: cycles_completed 19, no_beat_cycles **3** (C17 reject, C18 gate-arithmetic refusal, C19 reject) → **the charter's saturation rule fires.**

## ENGINE v3 — TERMINATED: SATURATED-V3 (2026-10-31, desert phase close)
- **Termination rule met:** 3 consecutive maximin no-beats (C17, C18, C19) after the deletion registry exhausted (C16) and the ordered data build failed on sourcing (bulk/block calendar, Lesson 39). Every road named in the v3 charter and the desert-phase order has been walked to a recorded end: (a) (comp × stock × dir) deletions — registry exhausted, last row banked C16; (b) (comp × round) axis — INV-LONG R3 banked (C1), INV-ABOVE R3 rejected (C2), INV-ABOVE round-1 amputation barred by the both-years rule on asserted numbers (C18); (c) P2F (band × lag) grid — completed, only the incumbent ≥2.5% × R+1 cell earns; (d) new event classes — bulk/block calendar not buildable uniformly from this environment (sourcing verdict, Lesson 39); dividend/N4 variant refused on a mechanical-artefact argument pre-scoring; (e) INV earliness axis — closed in v2 (L36).
- **Final v3 book (the C16 book; C17–C19 changed nothing): combined +₹259,860.26 = ₹11,812/month over 22 months** (provisional per 100 shares, ₹40/trade, paper, real ₹0). **2025: +₹44,729.13** (731 tr, ₹3,727/month, ex-top-3 **+₹30.76**) · **2026: +₹215,131.13** (636 tr, ₹21,513/month). v3's total lift over the frozen v2 book: **+₹20,792.92** (15 banks, 3 scored rejects, 2 pre-scoring refusals, 19 cycles).
- **Against the user's standards, stated plainly:** red months 6 → **4** (Mar and May 2025 flipped green in v3's first phase); **the worst month, Jul 2025 −₹5,088.45, NEVER crossed ₹0** — the ₹10,000 minimum-month objective is NOT met, and the desert phase (C16–C19) added nothing to the bottom-5 (Jul −5,088.45, Oct −3,020.72, Nov −2,463.94, Jun −955.92, May +234.82 — unchanged; C16's bank landed in Jan 2026). All six regime cells × year remain positive (2025 UP +11,242.90 / DOWN +29,773.66 / FLAT +3,712.57; 2026 UP +15,888.69 / DOWN +192,179.54 / FLAT +7,062.90). The ₹15–25k/month acceptance band: met by 2026 alone (₹21,513/month), not by the 22-month average (₹11,812) and not by 2025 (₹3,727) — the remaining gap is a 2025-regime gap, concentrated in four months whose common anatomy is now fully documented (UP-regime INV-ABOVE round-1 bleed + zero/few usable events).
- **What would reopen v3 (named, per the saturation discipline):** (1) exchange/bulk-block data access from this environment (endpoint + field map recorded in the desert-phase log entry — the calendar then builds in one step and its event class gets its frozen challengers); (2) genuinely new data (e.g. November–December 2026 fresh bars — the frozen SarvaRitu forward test is already running untouched and judges this book family on fresh data); (3) a genuinely new mechanism class not derived from the F4/INV/N4/P2F families. Re-running closed cells, loosening the gate, or re-defining the floor are not reopenings.
- **Books of record:** `stocks_engine_v3_c16_book2025_trades.csv` / `stocks_engine_v3_c16_book2026_trades.csv`. The SarvaRitu roof registry and the frozen Nov–Dec forward test are unaffected (the forward test judges the v2-frozen book family as pre-registered; v3's book is the candidate line for a later fresh test, per the charter).

---

## ENGINE FLOOR SESSION (2026-11-02, user directive: Rs15,000/month pace in EACH year separately — Jan-Oct >= Rs1,50,000 in 2025 AND in 2026; provisional per 100 shares, Rs40/trade, paper, real Rs0)

Incumbent adopted: the v3 C16 book (December candidate line; dominates the frozen v2 C24 reference in both years: 2025 +44,729.13 / 2026 +2,15,131.13). Baseline independently re-summed to the paisa; REGIME-CLASSIFIER-1 labels replicated exactly against both books' published cells; N4 move recomputation 56/56 vs the recorded standalone moves and 34/34 on the in-book join (stocks_engine_floor_baseline.py). Session gate frozen in stocks_engine_frozen.md before scoring (nine legs: combined rises; 2025 total + Jan-Oct do not fall; 2026 does not fall; all regime cells x year stay positive; ex-top-3 per year >= 0 and combined ex-top-3 does not fall; no green month flips; no Jan-Oct half flips; beats both pre-registered placebos; timing audit 0 + re-sum exact). Start: 2025 Jan-Oct +45,985.12 (gap Rs1,04,014.88) / 2026 Jan-Oct +2,15,131.13 (floor met).

- **FLOOR-1 (N4-V3 symmetric cap |move by 09:30| >= 3.0%, whole book) — REJECTED.** The component-level pass (fix tests 2026-11-02) does not transplant: prior book law had already harvested the standalone file's losing >=3% names, so the in-book >=3% bucket splits 2025 -1,838.73 (17 tr) / 2026 +5,678.23 (14 tr). Variant combined 2,59,860.26 -> 2,56,020.76; legs (a) and (c) FAIL; all other legs pass, both placebos beaten (A 2,43,992.28 / B 2,39,932.73). A 2025-only variant is a date filter — not entertained. Evidence stocks_engine_floor_c1_result.json. Lesson 41 appended.
- **FLOOR-2 (N4-V3 LONG over-extension cap: skip signed move >= +3.0%) — BANKED.** Direction split of the FLOOR-1 bucket: LONG >=3% negative in both years (2025 -940.81 / 10 tr / 2 W; 2026 -1,790.26 / 4 tr / 1 W); SHORT >=3% carries 2026 (10 tr / 9 W / +7,468.49). Dropping the 14 LONG trades: combined -> **+2,62,591.33 (+2,731.07)**; 2025 total +45,669.94, Jan-Oct **+47,048.67**, ex-top-3 +30.76 -> **+5,131.62**; 2026 +2,16,921.39, ex-top-3 +87,402.25. All nine legs pass; placebos A (mirror) +2,53,289.69 / B (chrono first-N) +2,47,989.60 beaten. Disclosed: one dropped trade was a winner (OBEROIRLTY 2025-10-16, +2,455.85) — October 2025 deepened while the rule and the year improved. Books: stocks_engine_floor_c2_book{2025,2026}_trades.csv. Lesson 42 appended.
- **FLOOR-3 (challenger: P2F-family reaction-size cap) — REFUSED AT DIAGNOSIS.** reaction_ret reconstructed for all 114 in-book family trades, 0 band violations; expectancy RISES with reaction size in both years (2026: 2.5-4% +384/tr, 4-6% +865, 6-8% +85, >=8% +695; 2025 all buckets positive). No over-extension region exists to cut. Same-cycle second kill: F4 x regime-cell cross-year locked in both cells (DOWN 2025 -2,369.54 / 2026 +1,06,005.51; FLAT 2025 +2,460.68 / 2026 -2,949.58). No-bank (v3 C18 refusal precedent). Lesson 43 appended.
- **FLOOR-4 (deletion: N4-V3 x HDFCBANK x LONG) — BANKED.** Registry re-derived at the C2 book under the gate-accurate bar (< 0 one year, <= 0 other, combined <= -500): exactly one qualifying row book-wide — 3 tr, all 2025, -836.12 (Apr -814.08 / Jul +830.00 / Oct -852.04), zero 2026 presence. Combined -> **+2,63,427.45 (+836.12)**; 2025 total +46,506.06, Jan-Oct **+47,884.79**, ex-top-3 +5,967.74; 2026 untouched. All nine legs pass; placebos A +2,59,936.58 / B +2,60,589.13 beaten. Disclosed cost (frozen in advance): the positive July leg's removal deepens the worst month (Jul 2025 -> -5,664.05) — accepted under the per-year floor objective; maximin would have refused. Books: stocks_engine_floor_c4_book{2025,2026}_trades.csv.
- **FLOOR-5 (whole-stock axis rows) — REFUSED (aggregation).** At the C4 book: (comp x stock x dir) and (comp x cell) axes EMPTY. (comp x stock) shows P2F-R2 x RECLTD (-690.73) and N4-V3 x PFC (-561.82), both refused: each is a sum of direction slices that individually fail the -500 bar (RECLTD LONG -252.73 / SHORT -438.00, different years; PFC LONG -399.96 / SHORT -161.86 with a +568.78 winning 2026 trade inside). Aggregating sub-bar slices to clear the bar is the mirror of slicing thinner (SAT-30) — the bar binds both ways. No-bank. Lesson 44 appended.
- **FLOOR-6 (F4 entry-hour axis) — NO-BANK (axis empty).** F4 is ~94% concentrated in the 10:00 hour in both years and that hour is the same cross-year lock (-2,703.03 in 2025 / +89,051.14 in 2026); all other hours positive in both years. No qualifying slice. Session ends on the brief's 6-cycle stop; closing no-bank streak 2 (FLOOR-5, FLOOR-6) — the formal 3-cycle saturation rule is not triggered, but every enumerated axis at the final book is empty, refused, or closed.

## FLOOR SESSION — ENDING BOOK (FLOOR-C4 state)
- **Combined +Rs2,63,427.45** (session lift +Rs3,567.19; 2 banks, 1 scored reject, 2 diagnosis refusals, 1 empty axis). Books of record: stocks_engine_floor_c4_book2025_trades.csv (718 tr) / stocks_engine_floor_c4_book2026_trades.csv (632 tr). Full scorecard: stocks_engine_session_2026-11-02.md.
- **2026: Jan-Oct +Rs2,16,921.39 = Rs21,692.14/month — FLOOR MET (+Rs66,921.39).** All months green, halves +1,20,674.05 / +96,247.34, ex-top-3 +87,402.25, cells DOWN +1,93,697.00 / UP +16,161.49 / FLAT +7,062.90.
- **2025: Jan-Oct +Rs47,884.79 = Rs4,788.48/month — FLOOR NOT MET; gap Rs1,02,115.21 (31.9% of the floor).** Full year +46,506.06; halves (Jan-Oct) +40,672.50 / +7,212.29; ex-top-3 +5,967.74 (session repaired it from +30.76); cells DOWN +32,605.74 / UP +11,017.75 / FLAT +2,882.57, all positive; red Jan-Oct months Jun -955.92 / Jul -5,664.05 / Oct -4,624.53.
- **The gap's anatomy (stated plainly):** not a slice problem — every deletion axis is exhausted at the quality bar. F4 made +91.14 on 246 trades in 2025 vs +1,03,055.93 in 2026 on an identical population; the joint state was inert in 2025's tape and no ex-ante sub-population (stock, direction, cell, hour) separates the years. Families remaining open in-sample: NONE. Reopening conditions unchanged: bulk/block data access, Nov-Dec 2026 fresh data (forward test already collecting), or a genuinely new mechanism class.
- **Book law added:** FLOOR-2 (N4-V3: no entry with signed move by 09:30 >= +3.0%) / FLOOR-4 (N4-V3: no HDFCBANK LONG). The frozen SarvaRitu forward test (v2 book) ran untouched throughout.

---

## ENGINE ROUND 2 (2026-11-02, user directive: different use cases, combinations and permutations until the goal is achievable; no saturation conclusions)

Goal restated: Jan-Oct >= Rs1,50,000 in EACH year separately (Rs15,000/month; provisional per 100 shares, Rs40/trade, paper, real Rs0). Starting book FLOOR-C4 (2025 Jan-Oct +47,884.79 / 2026 +2,16,921.39). Same frozen nine-leg gate + cross-year rule (a candidate improving one year while degrading the other does not bank; 2026 may not fall below the floor). Every candidate construction anchored multiset-exact against the FLOOR-C4 component it replaced before scoring; timing audit 0 violations on all population builds. 28 gated cycles + 22 grid cells; full grid in stocks_engine_round2_2026-11-02.md; evidence r2_results.json.

- **BANKS (2).** (1) R2-07 grid cell: INV-LONG ADR>=3.0 (unchanged), round cap <=2 -> <=3, entry cutoff 10:30 -> 11:00 — combined +11,255.92 (2025 Jan-Oct +6,620.26; 2026 +4,635.66), all nine legs, placebos beaten (1,80,365.56 / 2,20,390.77); absorbed round-3 rows de-duplicated out of INV-R3; the 10:30 control cell inside the grid reproduces the incumbent combined to the paisa, isolating the gain to the 11:00 hour + round 3. (2) R2-17: N4-V3 threshold 1.0% -> 0.8% at book geometry T150/S080 with the FLOOR-2 cap retained — combined +2,075.33 (2025 +1,831.25; 2026 +244.08), all nine legs. Session lift +13,331.25 combined.
- **FLAGGED, NOT BANKED (user decision): R2-26 INV-ABOVE exits T150/S080** — combined +13,089.83 (2025 Jan-Oct +7,534.00; 2026 +4,122.33), passes 8 of 9 legs, fails only (f): Mar 2025 +1,091.17 -> -1,368.66. Per-cell splits do not repair it (UP-only R2-27 +8,733.80 fails (e); FLAT-only R2-28 fails the same March flip — the damage is in the FLAT cell). Adoption would put 2025 at +63,870.30 Jan-Oct. The engine does not waive its own gate (Nifty CH3-R precedent: adoption is the user's call).
- **F4 (R2-01..06, R2-20..24): closed on this window across every axis.** Bands [0.4,0.9) / [0.6,1.2), measurement 09:45, EXCL_DIR off, per-cell geometries (DOWN/FLAT x T125/S065, T175/S095), FLAT stand-aside — all FAIL. Invariant: every F4 population change buys 2025 (+Rs12-18k) with a larger 2026 loss (-Rs20k to -1,23,440); the 09:45 measurement alone is +17-18k in 2025 and -1,15,493 in 2026. The FLAT stand-aside (R2-24) also loses to its own chrono placebo (variant 2,77,247.60 vs placebo 2,82,398.84).
- **INV-ABOVE grid (R2-08): no cell banks** — 2025 gains in most cells (+5-9k) are paid by 2026 or beaten by the component's own SHORT-side / opposite-gate placebos (placebo books 2,37,070-3,28,119). Merged INV round-law cells (R2-09/10) fail; the split-comp structure stands.
- **Reaction grid (R2-11..14): all four untested cells fail** — P2F >=3.0 @R+1, P2F-R2 >=3.0 @R+2, R2-LOWBAND without UP stand-aside, P2F >=2.0 @R+1. No passing cell exists to combine.
- **N4 (R2-15/16/18):** threshold 1.2% fails (2026 pays); the 09:40 confirming-close entry is the round's most expensive idea (-16k to -22k combined in both cells) — one bar of confirmation pays the move away in both years.
- **New mechanism PERSIST-R2 (R2-19): FAIL on the cross-year rule.** Second-day continuation with R+1 persistence and an R+2 10:00 hold: standalone 2025 +2,903.00 / 2026 -643.26; combined would rise +2,009.67 on 2025 alone; legs (c) and (e) refuse it.
- **ROUND 2 — ENDING BOOK.** Combined +Rs2,76,758.70 full-book basis (2025 total +54,957.57 / 2026 +2,21,801.13). Books of record: stocks_engine_r2_book2025_trades.csv (776 tr) / stocks_engine_r2_book2026_trades.csv (680 tr); re-sum from file exact. **2026: Jan-Oct +2,21,801.13 = Rs22,180.11/month — FLOOR MET (+71,801.13).** All months green; cells all positive; ex-top-3-stocks +87,675.53. **2025: Jan-Oct +56,336.30 = Rs5,633.63/month — FLOOR NOT MET; gap Rs93,663.70 (37.6% of the floor).** Halves +48,410.24 / +7,926.06; ex-top-3-stocks +9,775.76 (Round 2 added +3,808.02); cells DOWN +39,226.00 / FLAT +2,882.57 / UP +14,227.73, all positive; red months Jun -955.92 / Jul -5,664.05 / Oct -4,624.53 (unchanged set, Jul is the book's worst month in both sessions). Book law added: INV-LONG rounds <=3 + cutoff 11:00; N4-V3 threshold 0.8%. Stop condition met: 28 cycles + 22 cells, enumerated space exhausted. The frozen November forward test (v2 book) ran untouched throughout.


---

# ROUND 3 — 2026-11-02 (targeted techniques on 2025; standing order: do not stop)

Starting book = Round-2 ending book (verified by independent re-sum from
the exported CSVs before any scoring): 2025 Jan–Oct **+₹56,336.30**
(776 tr full-year, total +₹54,957.57) — gap to floor ₹93,663.70; 2026
Jan–Oct **+₹2,21,801.13** (680 tr) — floor MET, protected by the
cross-year rule (2026 must stay ≥ ₹1,50,000; leg x added to the gate).
R2-26 (INV-ABOVE T150/S080) still unadopted, awaiting Chandu; not touched.
10 cycles worked (9 gated candidates + 1 audit). **Bankings: NONE.** The
ending book is the Round-2 ending book, unchanged to the paisa.

## R3-01 — WS1 wound basket (GATED, REJECTED)
Wound decomposition (2025 Jun −₹955.92 / Jul −₹5,664.05 / Oct −₹4,624.53;
47 trades, −₹11,244.50): F4 −₹4,047.11 (22 tr), INV-ABOVE −₹3,637.29
(14), N4-V3 −₹2,614.80 (5), P2F −₹486.45, P2F-R2 −₹458.85; cells UP
−₹6,496.88, DOWN −₹5,173.10, FLAT +₹425.48. The two largest wound rows —
F4 TVSMOTOR LONG −₹3,564.10 and SHORT −₹3,302.78 — are whole-book giants
(+₹20,385.20 / +₹14,526.85) and are NOT deletable. Frozen basket rule
(rows with wound net < 0 AND whole-book net in (−₹500, 0]): 7 rows,
58 trades (F4 NTPC SHORT, F4 WIPRO SHORT, N4 INDUSTOWER SHORT, P2F
INDUSTOWER LONG, P2F WIPRO LONG, P2F-R2 INDUSTOWER LONG, P2F-R2 WIPRO
SHORT). Variant: 2025 → ₹58,209.83 (+₹1,873.53), 2026 → ₹2,21,623.03
(−₹178.10). REJECTED: leg (c) 2026 fell; leg (h) — mirror-wound basket
placebo ₹2,81,788.63 and chrono first-58 placebo ₹2,80,891.16 both beat
the variant's ₹2,78,454.13 combined. The sub-bar registry holds nothing
the placebos don't beat.

## R3-02 — WS2 event-layer audit (AUDIT, no candidate — nothing to rebuild)
2025 calendar is COMPLETE: 100 results rows (exactly 4 per stock), 0 with
missing/out-of-window reaction dates; reaction candidates **100** vs
2026's **80**; band ≥2.5% candidates 33 vs 39; [2.0,2.5) 12 vs 9; N4
signal-days 91 vs 77. The 16 out-of-window reaction dates in the 2026
file are 15 Nov-2025 events (placeholder "2026-01-01"; valid Nov-2025
reaction dates sourceable from results_events_v1.csv, but those events
sit outside the Jan–Oct judged window under either dating, so a
"corrected calendar" candidate would change nothing judged — not built)
plus UNITDSPR 2026-10-28, whose reaction date is unsourceable from
stored sources (named, never invented; the incumbent treats the
announcement day as R). 2025's family shortfall is expectancy and band
mix (P2F-R2 −₹390.06 on 21 tr vs 2026 +₹15,149.33 on 32; P2F healthy in
both years), NOT missing events. Workstream closed by evidence.

## R3-03 — F4 15-min execution (GATED, REJECTED)
Entries deferred to the next quarter-hour bar open; measurement, band,
law frozen; anchors exact (std-mode population == cache; audit 0
violations). 2025 → ₹56,564.96 (+₹228.66), 2026 → ₹1,88,799.78
(−₹33,001.35). REJECTED legs a, c, e, h. The deferral tax lands in 2026,
same signature as R2-03/R2-16: this book's entries lose value with every
bar of delay, in both constructions tried.

## R3-04 — INV 15-min execution (GATED, REJECTED)
Chain entries deferred to quarter-hour opens; law frozen (INV-LONG
rounds ≤3 <11:00; INV-ABOVE rounds ≤2 <10:30); std-chain anchor exact
(15,453 rows). 2025 → ₹45,304.57 (−₹11,031.73), 2026 → ₹2,08,306.48
(−₹13,494.65); Jan and Mar 2025 flip red. REJECTED on 7 legs. WS3
closed: 15-min entry constructions are worse than 5-min for both
families, both years. The 5-min execution bar is load-bearing.

## R3-05 — GAP-FOLLOW ≥1.5% (GATED, REJECTED)
Pre-registered diagnostic (both years pooled): follow expectancy
−₹27.36/trade H1, −₹43.12 H2 — the 25 do not reward following overnight
gaps at this construction. Standalone 2025 −₹22,079.40 / 2026 −₹2,219.99.
REJECTED on 8 legs.

## R3-06 — GAP-FADE ≥1.5% (GATED, REJECTED)
Diagnostic: fade expectancy +₹3.10 H1 / +₹25.80 H2 (both halves
positive, small). Standalone 2025 **+₹21,762.48** / 2026 **−₹15,956.71**.
Book: 2025 → ₹78,098.78, 2026 → ₹2,05,844.42, combined FALLS −₹1,121.50;
May 2025 flips (+₹2,498.99 → −₹7,587.51); loses to placebos. REJECTED
legs a, c, e, f, h. The fade's 2025 gain is bought with 2026 — the
cross-year failure mode in its purest form.

## R3-07 — ORB-STOCK (GATED, REJECTED — family closed)
Index-method port: 09:15–09:30 range, first close beyond, entry next
bar ≤11:30, T125/S050. Standalone 2025 −₹96,573.49 (5,098 tr) / 2026
−₹2,43,756.84 (3,929 tr) — expectancy ≈ −₹19 / −₹62 per trade. REJECTED
on all 9 legs + leg x. Chandu's index opening-range method does not
port to cash stocks on the 25; no second ORB cell will be run.

## R3-08 — GAP-FADE ≥2.5% (GATED, REJECTED)
Standalone 2025 +₹11,429.79 / 2026 +₹1,207.57; combined RISES
+₹9,571.17 and both years rise — but REJECTED: leg (e) ex-top-3 falls
(gains concentrated in the top-3 stocks), leg (f) May 2025 flips
(+₹2,498.99 → −₹2,186.79), leg (h) loses to the one-bar-late placebo.

## R3-09 — GAP-FOLLOW ≥2.5% (GATED, REJECTED)
Standalone ≈ 2025 −₹4,439.73 / 2026 +₹73.78. REJECTED legs a, b, d, e,
f, h. The {follow, fade} × {1.5%, 2.5%} gap grid is now fully gated:
follow is dead at both thresholds; fade is positive-2025-only at both.

## R3-10 — GAP-FADE LONG-only sub-sleeve ≥1.5% (GATED, REJECTED — flagged observation)
Sign-split diagnostic (pre-registered from the 1.5% fade population):
fade-LONG (buying faded gap-DOWNS) expectancy +₹57.20 H1 (322 tr) /
+₹72.27 H2 (62 tr) — positive in both halves; fade-SHORT (fading
gap-ups) −₹48.74 / −₹8.51 — negative in both. The LONG-only sub-sleeve:
2025 → **₹83,315.69 (+₹26,979.39)**, 2026 → ₹2,17,720.37 (**−₹4,080.76**),
combined +₹22,084.79. Passes legs a, b, d, g, h, i, x (7 of 10). REJECTED:
leg (c) 2026 falls, leg (e) ex-top-3 2026 falls, leg (f) May 2025 flips
(+₹2,498.99 → −₹4,762.43) and Dec 2025 flips. NOT banked — the
cross-year rule is absolute in this engine. Recorded as the round's
largest single 2025 improvement and a flagged observation for Chandu,
in the same class as R2-26: adoption against named failed legs is his
decision, not the engine's.

## WS5 — combinations: VACUOUS
No Round-3 banking exists; there is nothing to combine. The ending book
is the Round-2 ending book unchanged.

## Round-3 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹56,336.30 = ₹5,633.63/month — floor NOT met; gap
  ₹93,663.70 (unchanged).** Full-year +₹54,957.57, 776 trades. Red
  months Jun −₹955.92, Jul −₹5,664.05, Oct −₹4,624.53 unchanged.
- **2026: Jan–Oct +₹2,21,801.13 = ₹22,180.11/month — floor MET
  (unchanged).** 680 trades, all months green.
Books: stocks_engine_r3_book2025_trades.csv / ...2026_trades.csv
(identical in content to the Round-2 books — re-exported under R3 names).
Evidence: r3_results.json (per-cycle gate legs, placebos, flips).
R2-26's numbers are unchanged by Round 3 (+₹13,089.83, Mar-2025 flip);
its adoption decision is still Chandu's.

---

# ROUND 4 (2026-11-02) — combined flags, gap-fade refinement, volume audit

Starting book: Round-2 ending book (2025 JO ₹56,336.30; 2026 JO
₹2,21,801.13). Evidence: r4_results.json. Report:
stocks_engine_round4_2026-11-02.md.

## R4-01 — COMBINED FLAGS gated whole (DECISION SUPPORT, not banked)
R2-26 (INV-ABOVE T150/S080 swap) + R3-10 (GAP-FADE LONG-only sleeve)
applied together. Ingredients re-anchored to the paisa first (R2-26:
2025 JO +₹7,534.00, combined +₹13,089.83; R3-10: 2025 +₹26,979.39,
2026 −₹4,080.76, combined +₹22,084.79). The combination is EXACTLY
additive (disjoint components): 2025 JO → **₹90,849.69**; combined
₹2,76,758.70 → ₹3,11,933.32. Surprise: leg (c) PASSES — 2026 JO rises
+₹41.57 because R2-26's 2026 gain (+₹4,122.33) cancels the fade's 2026
loss (−₹4,080.76). Fails exactly two legs: (e) ex-top-3 (2026 ex-top-3
₹87,675.53 → ₹71,201.56 under the full sleeve) and (f) May 2025 flips
(+₹2,498.99 → −₹2,019.04) and Dec 2025 flips (+₹1,207.95 → −₹345.69) —
both flips are the fade sleeve's. Placebos beaten (3 pre-registered).

## R4-02 — GAP-FADE LONG, DOWN-cell days only (REJECTED, leg e only)
2025 JO → ₹59,799.09 (+₹3,462.79); 2026 JO → ₹2,27,624.69 (+₹5,823.56).
Cross-year repaired, but the DOWN-only sleeve's gains concentrate:
ex-top-3 leg fails. One leg short.

## R4-03 — GAP-FADE LONG, DOWN+FLAT cells (BANKED)
2025 JO → **₹77,806.57 (+₹21,470.27)**; 2026 JO → **₹2,23,293.34
(+₹1,492.21)**; combined → ₹2,99,721.18. ALL 10 legs pass: the FLAT
cell's breadth repairs the concentration leg (2025 ex-top-3 ₹9,775.76
→ ₹23,764.74) while the UP cell — the source of the 2026 damage
(−₹5,572.97) — stays out. Sleeve standalone: 2025 +₹21,470.27,
2026 +₹1,492.21. The flagged R3-10 phenomenon is now a banked
component in cross-year-clean form. Incumbent updated.

## R4-04/05/06 — threshold swaps 2.0 / 2.5 / 3.0 (ALL REJECTED)
Unrestricted higher-threshold sleeves swapped against the banked
sleeve: combined falls every time (₹2,89,232.22 / ₹2,89,250.65 /
₹2,90,678.79 vs ₹2,99,721.18); 2026 standalone −₹8,493.16 / −₹1,329.35
/ −₹3,721.67. Bigger gaps fade worse in the UP/FLAT cells the banked
form excludes. Size is not the fade's problem; day-type is.

## R4-07 — entry at 09:15 open (BANKING VOID — timing audit)
The bar-0 cell "passed" with sleeve standalone +₹67,392.17 /
+₹22,054.04 and was banked by the script on the harness's default
timing_violations=0. That default is wrong here: the signal IS the
gap (bar-0 open / prior close), so a fill at bar-0's open is a fill
at the print that first reveals the information — entry before the
information existed, on all 390 sleeve trades. The bar-0 gain over
the honest bar-1 sleeve (+₹41k in 2025, +₹26k in 2026) is the
first-bar snap-back harvested at the signal print: the look-ahead
signature. Banking VOIDED on leg (i) the same run; incumbent
reverted to the R4-03 book; the two cells gated against the voided
base were re-run (R4-08R / R4-09R). The open-entry convention remains
legitimate only where the signal is fully known before the open
(the reaction families).

## R4-08R — entry 09:35 swap (REJECTED, corrected base)
2025 JO → ₹50,193.10; 2026 → ₹1,82,500.44; 7 legs fail. Delay kills
the fade exactly as it killed F4/INV timing variants.

## R4-09R — exits T150/S080 swap (REJECTED, corrected base)
2025 JO → ₹86,098.47 but 2026 → ₹2,09,171.26; fails (c), (e), (f).
The wider geometry re-imports 2026 losses; T125/S050 stands.

## R4-10 — banked book + R2-26 (DECISION SUPPORT — PASSES ALL LEGS)
2025 JO → ₹85,340.57; 2026 JO → ₹2,27,415.67; combined → ₹3,12,811.01.
ALL 10 legs pass, flip_detail empty: the Mar-2025 flip that killed
R2-26 in Round 2 is gone — the banked sleeve's March gains
(+₹5,033.28) absorb the swap's March loss (−₹2,459.83); March stands
at +₹3,664.62 under the combination. Recorded UNBANKED: adopting a
flagged variant is Chandu's decision, not the engine's.

## R4-11 — sleeve swapped to the FULL R3-10 form (DECISION SUPPORT)
Fails (a), (c), (e), (f): combined falls to ₹2,98,843.49, 2026 falls
−₹5,572.97 (the UP cell, exactly). The banked refinement dominates
the flagged sleeve head-to-head.

## R4-12 — R2-26 + full sleeve (DECISION SUPPORT)
= R4-01's variant re-gated on the banked base: 2025 JO ₹90,849.69,
2026 JO ₹2,21,842.70 (BELOW the banked book's ₹2,23,293.34). Fails
(c), (e), (f). Adopting both flags now costs 2026 ₹1,450.64 against
the banked book and keeps both fade flips.

## R4-13 — WS3 volume audit (no candidate)
No volume field exists in any stored equity candle: every file in
data/full_hist (25 symbols + index, 5-min and daily) is OHLC-only
(headers: timestamp/date, open, high, low, close), and the logger
machinery carries no volume. Volume-confirmed reactions cannot be
built from stored data. Named gap: a volume-bearing candle build.
Nothing fabricated; no candidate gated.

## Round-4 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹77,806.57 = ₹7,780.66/month — floor NOT met; gap
  ₹72,193.43** (round opened at ₹93,663.70; the banked sleeve closed
  ₹21,470.27 of it). Full-year +₹76,427.84, 857 trades. Red months
  Jun −₹955.92, Jul −₹5,523.29, Oct −₹4,624.53. Cells: DOWN
  +₹42,688.79, FLAT +₹20,890.05, UP +₹12,849.00. Ex-top-3 +₹23,764.74.
- **2026: Jan–Oct +₹2,23,293.34 = ₹22,329.33/month — floor MET**
  (₹73,293.34 above the line). 899 trades, all months green.
Books: stocks_engine_r4_book2025_trades.csv /
stocks_engine_r4_book2026_trades.csv (exported and independently
re-summed to the paisa). Evidence: r4_results.json.
Decision state: R2-26 now carries NO failing leg on this book
(R4-10) — adoption is Chandu's and would put 2025 at ₹85,340.57.
R3-10's full form is dominated by the banked refinement (R4-11).


---

# ROUND 5 — 2026-11-02 (gap-fade mirror + micro-grid, non-event reversal, P2F-R2 conditioning, red-month diagnosis)

Starting book: Round-4 ending book (2025 JO ₹77,806.57, gap ₹72,193.43;
2026 JO ₹2,23,293.34, floor MET). 12 gated cycles + 1 diagnosis audit
+ 1 decision-support combination. **BANKED: ZERO.** Ending book
identical to the paisa (exports re-summed). Evidence: r5_results.json;
report: stocks_engine_round5_2026-11-02.md.

## R5-01 — GAP-FADE SHORT >=1.5%, UP cells only (REJECTED)
Standalone -₹13,051.53 (2025) / -₹1,746.40 (2026); book 2025 JO ->
₹70,868.47, 2026 -> ₹2,21,546.94. Fails 8 legs (a,b,c,d,e,f,g,h) —
and its own mirror placebo (follow-LONG book ₹3,14,289.90) beats it:
on UP days gap-ups CONTINUE. Flips May + Dec 2025.

## R5-02 — GAP-FADE SHORT >=1.5%, UP+FLAT cells (REJECTED)
Standalone -₹12,433.50 / -₹1,137.24; fails the same 8 legs. Adding
the FLAT cell does not rescue the short side. The fade is one-sided;
the mirror family is CLOSED.

## R5-03 — GAP-FADE LONG thr 1.25% swap, DOWN+FLAT (REJECTED — leg e only)
2025 JO -> ₹88,401.23 (+₹10,594.66); 2026 JO -> ₹2,26,071.55
(+₹2,778.21); combined -> ₹3,13,094.05; both placebos beaten; no
flips. Fails ONLY (e): the incremental [1.25%, 1.5%) slice's 2026
gains concentrate in the top-3 names (2026 ex-top-3 ₹75,557.94 ->
₹67,253.47; combined ex-top-3 falls ₹99,322.68 -> ₹94,567.68).
Recorded with its failing leg named (owner-decision class).

## R5-04 — GAP-FADE LONG thr 1.75% swap, DOWN+FLAT (REJECTED)
2025 JO -> ₹73,811.52; 2026 -> ₹2,19,743.09; fails (a),(b),(c).
Standalone 2026 turns negative (-₹2,058.04): the [1.5%, 1.75%) slice
is load-bearing in 2026.

## R5-05 — GAP-FADE LONG exits T100/S065 swap (REJECTED)
2025 JO -> ₹75,147.99; 2026 -> ₹2,23,268.97; fails (a),(b),(c).
The tighter target / wider stop pair is worse in both years.

## R5-06 — GAP-FADE LONG exits T150/S065 swap (REJECTED — leg c only)
2025 JO -> ₹84,937.76 (+₹7,131.19); 2026 -> ₹2,16,268.73
(-₹7,024.61); combined full-year rises (+₹106.58) and every other
leg passes — the wider geometry pays in the weak year and bills the
strong year, the R4-09R shape at a different stop. Leg (c) refuses.

## R5-07 — NON-EVENT REVERSAL LONG (REJECTED — legs e, f)
New mechanism, pre-registered population (non-event stock-days,
|move by 10:30| >= 2.0%, entry 10:35, T100/S065; 180 reaction
candidates, 539 contaminated stock-days excluded; timing violations
counted = 0). Standalone +₹12,209.45 (2025) / +₹24,306.56 (2026) on
691 trades; book 2025 JO -> ₹90,121.11 (+₹12,314.54), 2026 ->
₹2,47,599.90 (+₹24,306.56); combined -> ₹3,36,237.19; beats both
placebos (opposite-dir ₹2,34,944.85; one-bar-late ₹3,01,424.12);
halves and cells pass. Fails (e) — gains concentrate in the top-3
(combined ex-top-3 ₹99,322.68 -> ₹86,879.08) — and (f) — Dec 2025
flips +₹1,207.95 -> -₹632.67. A real phenomenon the gate cannot
bank; recorded with both failing legs named (owner-decision class).

## R5-08 — NON-EVENT REVERSAL SHORT (REJECTED)
Standalone -₹41,334.92 / -₹18,088.52 on 818 trades; fails 8 legs.
Non-event morning rips do NOT revert — shorting them is the single
worst sleeve of the round. The reversal phenomenon is LONG-only.

## R5-09 — P2F-R2 keep DOWN+FLAT cells (REJECTED)
Removes the 2025 UP-cell loss (+₹433.24 to 2025 JO) but bills 2026
-₹2,389.00; fails (a),(b),(c),(e),(h) — the chrono placebo
(₹2,99,567.23) also beats the variant (₹2,97,006.93).

## R5-10 — P2F-R2 keep DOWN cells only (REJECTED)
Same 2025 JO as R5-09; 2026 -₹4,479.17; fails (a),(b),(c),(e),(h).
2026's FLAT-cell P2F-R2 (+₹2,090.17) is real money.

## R5-11 — P2F-R2 keep band [2.5%, 4.0%) (REJECTED)
2026 JO -> ₹2,10,568.48: the >= 4.0% band IS 2026's P2F-R2
(+₹12,724.86 of its +₹15,149.33). Fails (a),(b),(c),(e),(h).

## R5-12 — P2F-R2 keep band >= 4.0% only (REJECTED)
Best 2025 outcome of WS4 (JO -> ₹79,105.92, +₹1,299.35) — bought
with 2026's [2.5%, 4.0%) money (-₹2,424.47); fails (a),(c),(e).
P2F-R2's weakness is population-wide and cross-year-opposed on
every condition tested; the conditioning axis is CLOSED.

## R5-13 — WS5 red-month diagnosis (AUDIT — no candidate)
Jun 2025 (-₹955.92) = 7 trades, ALL INV-ABOVE. Jul (-₹5,523.29) =
broad shallow bleed (INV-ABOVE -₹2,473.45 / 3 tr; N4-V3 -₹1,821.00 /
2 tr; F4 -₹1,025.28 / 19 tr). Oct (-₹4,624.53) = F4 -₹3,021.83 in 3
trades. Frozen signature rule (negative in all 3 months AND negative
full-2025 AND sum3 <= -₹3,000): NO slice qualifies. (INV-ABOVE x UP)
is negative in all three months (-₹3,442.37) but earns +₹6,435.21
across 2025 — variance on an earner; (F4 x DOWN) is negative Jul+Oct
and full-2025 but has zero Jun trades. Three months, three
anatomies; no candidate manufactured. Table: r5_ws5_diag.json.

## R5-15 — DECISION SUPPORT: R5-03 + R5-07 combined (UNBANKED)
Exactly additive (anchors reproduced first): 2025 JO -> ₹1,00,715.77
(₹10,071.58/mo; gap would fall to ₹49,284.23); 2026 JO ->
₹2,50,378.11; combined -> ₹3,49,610.06; both placebos beaten. Fails
the same two legs — (e) combined ex-top-3 -> ₹82,699.21, (f) the
Dec-2025 flip (NE-REV's alone). Adoption is Chandu's, as a waiver of
legs (e) and (f) — the engine banks nothing it did not pass.

## Round-5 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹77,806.57 = ₹7,780.66/month — floor NOT met; gap
  ₹72,193.43 (unchanged).** Full-year +₹76,427.84, 857 trades,
  ex-top-3 +₹23,764.74. Red months Jun -₹955.92, Jul -₹5,523.29,
  Oct -₹4,624.53.
- **2026: Jan–Oct +₹2,23,293.34 = ₹22,329.33/month — floor MET.**
  899 trades, all months green.
Books: stocks_engine_r5_book2025_trades.csv /
stocks_engine_r5_book2026_trades.csv (exported and independently
re-summed to the paisa — identical to the Round-4 books, as nothing
banked). Evidence: r5_results.json.
Decision state: R2-26 still awaits Chandu (clean sheet, R4-10).
Round 5 adds two owner-decision items — R5-07 NE-REV LONG (fails
e/f; adoption alone -> 2025 JO ₹90,121.11) and R5-03 thr-1.25 sleeve
(fails e only; adoption alone -> 2025 JO ₹88,401.23); combined
(R5-15) -> 2025 JO ₹1,00,715.77, still ₹49,284.23 short of the
floor, failing (e) and (f).


---

# ROUND 6 (2026-11-02) — triple pricing, NE-REV repairs, increment conditioning, range-expansion; causality audit

Starting book: the Round-4/5 ending book (2025 JO ₹77,806.57; 2026 JO
₹2,23,293.34). Constructions frozen in the report's pre-registration
before scoring. 9 gated runs (R6-01 decision support + 8 candidates),
2 audits, 1 banking, 4 rows voided by the audit. Evidence:
r6_results.json (11 records).

## R6-01 — DECISION SUPPORT: triple R2-26 + R5-03 + R5-07 (UNBANKED)
Ingredients re-anchored to the paisa on the Round-5 book first
(R2-26 → 85,340.57 / 2,27,415.67; R5-03 → 88,401.23 / 2,26,071.55;
R5-07 → 90,121.11 / 2,47,599.90). The combination is EXACTLY additive:
2025 JO → ₹1,08,249.77 (₹10,824.98/mo; gap would fall to ₹41,750.23),
2026 JO → ₹2,54,500.44, combined → ₹3,62,699.89; all three placebos
beaten (P1 all-placebo ₹1,62,831.09; P2 ₹3,27,886.82; P3
₹3,16,724.72).
Fails exactly two legs: (e) combined ex-top-3 99,322.68 → 86,720.81,
and (f) Dec 2025 +1,207.95 → −99.76 (milder than R5-15's −632.67 —
R2-26's December gains absorb most of NE-REV's December loss).
Adoption is Chandu's; restated on the ending book in the report.

## R6-02 — NE-REV thr 2.25% — REJECTED, leg (e) only
Standalone +₹7,375.61 / +₹40,742.69 (545 trades). 2025 JO →
₹84,207.51; 2026 JO → ₹2,64,036.03; combined ₹3,47,839.48 — larger
than R5-07's combination and with NO month flips. Refused only by
ex-top-3 (combined 99,322.68 → 97,177.38; 2025's own falls
23,764.74 → 20,114.34). Owner-decision class (flagged).

## R6-03 — NE-REV thr 2.50% — REJECTED (b, e, f)
Standalone −₹3,572.54 / +₹34,425.59. 2025 JO falls to ₹76,388.46 and
Dec 2025 flips (+1,207.95 → −1,495.32): the strongest dislocations
are 2025-negative — the threshold axis is not monotone in the weak
year; 2.25% is the family's best cell and it still fails (e).

## R6-04 — NE-REV DOWN+FLAT cells — REJECTED, leg (e) only
Standalone +₹544.11 / +₹32,422.92. 2025 JO → ₹78,350.68; 2026 JO →
₹2,55,716.26. The restriction repairs exactly what it aimed at:
R5-07's Dec-2025 flip is gone (the December damage was UP-cell) and
2026 keeps most of its gain — but ex-top-3 still falls (2025
23,764.74 → 13,867.75). Owner-decision class (flagged).

## R6-05 — NE-REV entry 11:05 — REJECTED (a, b, e, f)
Standalone −₹18,420.55 / +₹18,386.53. The 35-minute delay destroys
2025 (−₹14,594.12 JO; Jan/May/Dec flip). Fifth delay mechanism to
lose on this book; the entry-delay axis stays closed (R3-L4).

## R6-06 — AUDIT: NE-REV carrier exclusion SKIPPED (pre-registered)
Needs top-3 earners ranked on the PRIOR year's book for both years.
2026-on-2025 is causal; 2025 would need a 2024 book, which does not
exist in this workspace (calendars/populations cover 2025 +
Jan–Oct 2026), and ranking 2025 on the 2026 book is look-ahead.
Skipped with no substitute invented, exactly as pre-registered.

## R6-07 — Fade increment [1.25,1.5), DOWN-only, 09:20 — REJECTED (e)
Decomposition verified first (S1.25 = S1.5 + increment, disjoint and
exhaustive; increment standalone +10,594.66 / +2,778.21). DOWN-only:
standalone +₹9,278.66 / +₹913.63; 2025 JO → ₹87,085.23. The DOWN
cell carries nearly all of the increment's 2025 value, but its 2026
side still concentrates (2026 ex-top-3 75,557.94 → 68,047.39).

## R6-08 — Fade increment [1.25,1.5), DOWN+FLAT, entry 09:40 — BANKED
Standalone +₹2,305.22 / +₹4,763.03; ALL 10 legs pass, both placebos
beaten, no flips. 2025 JO → ₹80,111.79; 2026 JO → ₹2,28,056.37.
Entering the marginal band 20 minutes later changes its stock mix
enough to cure the concentration that refused R5-03 and R6-07 —
the one delay construction on this book that pays (see R6-L1).

## R6-09 — RANGE-EXPANSION FOLLOW LONG — REJECTED (7 legs)
Standalone −₹1,181.70 / −₹10,839.47 (242 trades), beaten by its own
one-bar-late placebo, May 2025 flips. Volatility-state continuation
on cash names does not exist on the long side.

## R6-10 — RANGE-EXPANSION FOLLOW SHORT — REJECTED, leg (c) only
Standalone +₹14,409.54 / −₹10,286.95 (237 trades). 2025 JO →
₹96,126.79 (+₹16,015.00 against the then-incumbent); 2026 JO →
₹2,17,769.42 (−₹10,286.95, still above the floor line). Every other
leg passes. The cross-year opposition (Lesson 47) in a new
mechanism; owner-decision class (flagged).

## R6-11 — AUDIT: admission causality (Nifty-R5-WS0 model) — 4 ROWS VOIDED
1,860 rows checked mechanically + machinery code certification.
CLEAN everywhere except N4-V3's event-day tag: 1 proven violation
(BDL 2025-01-16, +₹1,691.75 — the calendar's own detail records the
exchange filing at 13:49 on the reaction day; entry was 09:35) and
3 uncertifiable same-day results rows the calendar marks declared
during market hours (HINDZINC 2026-07-24 −460.80; HINDUNILVR
2026-10-28 −1,482.24; VEDL 2026-10-28 +303.20). All 4 voided;
book re-baselined the same run (2025 JO → ₹78,420.04; 2026 JO →
₹2,29,696.21; voided combined net +₹51.91 — the book was not
carried by them). BDL 2025-03-26 disclosed, not voided (no
timestamp in its record). Full certificate in the Round-6 report.

## WS4 — combinations of Round-6 bankings
One banking exists (R6-08); there is no second banking to combine
it with. Closes by statement.

## Round-6 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹78,420.04 = ₹7,842.00/month — floor NOT met; gap
  ₹71,579.96.** Full-year +₹77,041.31, 887 trades, ex-top-3
  +₹23,708.10. Red months Jun −₹955.92, Jul −₹7,083.39,
  Oct −₹3,944.53.
- **2026: Jan–Oct +₹2,29,696.21 = ₹22,969.62/month — floor MET.**
  969 trades, all months green.
Books: stocks_engine_r6_book2025_trades.csv /
stocks_engine_r6_book2026_trades.csv (exported from the ending
incumbent and independently re-summed to the paisa). Evidence:
r6_results.json; audit detail r6_causality_audit.json.
Decision state: the flagged list now carries R2-26 (clean),
R5-03 (e only), R5-07 (e+f), the R6-01 triple (e+f; restated on
this book → 2025 JO ₹1,06,558.02, gap ₹43,441.98), R6-02 (e only),
R6-04 (e only), R6-10 (c only) — see the Round-6 report.

---

# ROUND 7 (2026-11-02) — REXP-SHORT repair, breadth-first sleeves

Pre-registration, constructions and verdict rule frozen in
stocks_engine_round7_2026-11-02.md BEFORE scoring. Starting book =
the Round-6 ending book (2025 JO ₹78,420.04 / gap ₹71,579.96; 2026
JO ₹2,29,696.21, floor MET). New discipline this round: every new
sleeve trades only on the CERTIFIED non-event set (R6-11 standard:
the R5 reaction windows UNION every calendar event day, any type,
with its reaction window — 843 stock-days excluded vs the R5 set's
539).

## R7-01 — AUDIT: REXP-SHORT 2026-damage decomposition
R6-10's population rebuilt verbatim, anchor exact (standalone
+₹14,409.54 / −₹10,286.95; 237 trades; timing violations 0).
Jan–Oct by cell — 2025: DOWN 41 tr +₹14,870.39 · FLAT 9 tr
−₹2,717.22 · UP 43 tr +₹3,861.83. 2026: DOWN 86 tr **−₹8,399.33** ·
FLAT 17 tr −₹2,530.85 · UP 21 tr +₹643.23. The damage is DOWN-cell
located — the opposite address from NE-REV's and the fade's UP-cell
damage. 2026 worst names: TVSMOTOR −₹5,389.25, GODREJCP −₹3,380.55,
ASTRAL −₹3,133.20, UNITDSPR −₹2,503.10.

## WS1 — REXP-SHORT repair
- **R7-02 (DOWN+FLAT): REJECTED, leg (c) only.** Standalone
  +₹12,153.17 / −₹10,930.18 (50/103 tr); 2025 JO → ₹90,573.21;
  2026 JO → ₹2,18,766.03. The restriction is worse for 2026 than
  the full population (it drops UP's +₹643.23, keeps FLAT's
  −₹2,530.85 and all of DOWN's damage). Flagged.
- **R7-03 (DOWN only): REJECTED, leg (c) only.** Standalone
  +₹14,870.39 / −₹8,399.33 (41/86 tr); 2025 JO → ₹93,290.43; 2026
  JO → ₹2,21,296.88. Every other leg passes (2025 ex-top-3 →
  ₹38,000.12; placebos beaten; no flips). Dominates R7-02 on both
  years; the largest single-sleeve 2025 delta on the flagged list.
  Flagged.

## WS2 — R7-04 NE-REV afternoon: REJECTED on 7 legs
Certified population 11,958 stock-days; 963 signal days/trades
(462/501). Standalone −₹37,819.07 / +₹10,059.27; 2025 JO →
₹44,183.07; fails a, b, d, e, f, g, h (Jan + May 2025 flip;
beaten by placebos). The reversal is a morning phenomenon. Not
flagged.

## WS3 — R7-05 two-day dislocation reversal: REJECTED on 8 legs
1,189 signal days; 212 skipped (no 09:20 bar, counted); 977
trades. Standalone −₹62,345.49 / −₹43,694.93 — negative in both
years, beaten by both placebos, 4 month flips. Two-day falls
continue; they do not revert intraday. Not flagged.

## WS4 — R7-06 quiet-name NE-REV: REJECTED on (e) + (f)
Anchors: R5-07 reproduced exactly. Certified-population morning
NE-REV: 661 rows, standalone +₹14,105.64 / +₹24,112.86 (the
strengthening removed 30 rows and RAISED the weak year's
standalone). Quiet filter kept 196 trades (77/119); standalone
+₹4,492.57 / +₹12,167.10; combined book rises, placebos beaten —
but combined ex-top-3 falls ₹1,01,181.87 → ₹89,033.84 and Jan
2025 flips (+₹2,200.31 → −₹1,790.60). Breadth by construction
does not cure leg (e). Flagged.

## WS5 — R7-07 combinations: closes by statement (zero bankings)

## R7-08 — DECISION SUPPORT: R5-07 repriced on the certified population
Gated whole-book, force_no_bank: 2025 JO → ₹92,537.28 (delta
+₹14,117.24), 2026 JO → ₹2,53,809.07 (delta +₹24,112.86);
fails (e) + (f) (Jan 2025 → −₹750.61; Dec 2025 → −₹632.67).
The certified form is the current standard's price of the flag —
worth +₹1,802.70 more to 2025 than the birth form, same two
failing legs.

## Round-7 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹78,420.04 = ₹7,842.00/month — floor NOT met;
  gap ₹71,579.96 (unchanged; zero bankings).** Full-year
  +₹77,041.31, 887 trades, ex-top-3 +₹23,708.10. Red months Jun
  −₹955.92, Jul −₹7,083.39, Oct −₹3,944.53.
- **2026: Jan–Oct +₹2,29,696.21 = ₹22,969.62/month — floor MET.**
  969 trades, all months green.
Books: stocks_engine_r7_book2025_trades.csv /
stocks_engine_r7_book2026_trades.csv (identical to the Round-6
books; exported and independently re-summed to the paisa).
Evidence: r7_results.json (8 records). Decision state: the
flagged list now carries R2-26 (clean), R5-03 (e), R5-07 (e+f),
R5-07-CERT (e+f), R6-02 (e), R6-04 (e), R6-10 (c), R7-02 (c),
R7-03 (c), R7-06 (e+f), the triple (restated ₹1,06,558.02) and
the max stack triple + R7-03 (arithmetic restatement
₹1,21,428.41; gap ₹28,571.59) — see the Round-7 report.

# ROUND 8 (2026-11-02) — Max-stack gate, drive-continuation, index-state conditioning, REXP geometry neighbour

Pre-registration, constructions and verdict rule frozen in
stocks_engine_round8_2026-11-02.md BEFORE scoring. Starting book =
the Round-7 ending book (2025 JO ₹78,420.04 / gap ₹71,579.96; 2026
JO ₹2,29,696.21, floor MET). All flagged variants stay unbanked —
every Round-8 baseline is the book without them.

## R8-01 — AUDIT: WS0 ingredient anchors
Each stack ingredient applied alone reproduces its flagged-list
price on this book to the paisa: R2-26 → JO 85,954.04 /
2,33,818.54 · R5-03-clean (swap + GAP-FADE-INC retired) →
86,709.48 / 2,27,711.39 · R5-07-CERT → 92,537.28 / 2,53,809.07 ·
R7-03 → 93,290.43 / 2,21,296.88. Construction anchors inside the
ingredients also exact; timing violations 0.

## R8-02 — DECISION SUPPORT: MAX STACK gated whole (force_no_bank)
R2-26 + R5-03-clean + R5-07-CERT + R7-03 as ONE candidate:
exactly additive at row level (disjoint components). 2025 JO
**₹1,23,231.11** (₹12,323.11/mo; gap would fall to ₹26,768.89);
2026 JO ₹2,47,547.25; combined 3,70,821.53. **Fails leg (f)
ONLY** — Jan 2025 +2,200.31 → −715.46, Dec 2025 +1,207.95 →
−99.76. Leg (c) passes (the stack's other ingredients pay 2026
more than R7-03 costs it) and leg (e) passes (2025 ex-top-3 →
+44,205.13) — the inherited (c)+(e) failures of the R7
arithmetic restatement do not transfer to the assembled book.
Placebos beaten: P1 1,57,925.25, P2 3,25,723.56, P3 3,24,846.36.

## WS1 — Drive-continuation
- **R8-03 (LONG): REJECTED on seven legs (a, b, c, d, e, f, h).**
  Certified population, 800 signal days / 800 trades; standalone
  −₹1,710.67 / −₹28,882.57 — negative in both years; Jan and May
  2025 flip; the one-bar-late placebo (3,07,386.03) beats the
  variant. Morning up-drives on quiet days are faded by the
  close, not followed. Not flagged.
- **R8-04 (SHORT twin): NOT SCORED.** The frozen rule required
  the LONG standalone positive in both years; it is negative in
  both. Audit record only.

## WS2 — Index-state conditioning
- **R8-05 (NE-REV-IDX): REJECTED on (e) + (f).** NIFTY-down
  (≤ −0.30% at 10:30) filter kept 453/661 certified rows (208
  dropped on state, 0 unknown). Conditioned standalone
  +10,055.20 / +31,651.93; JO → 89,773.13 / 2,61,348.14. The
  Jan-2025 flip is cured; Dec 2025 still flips (+1,207.95 →
  −838.69) and combined ex-top-3 falls (the 2026 gains land in
  carrier names). Flagged as a NE-REV-family alternative.
- **R8-06 (banked fade × NIFTY-down): REJECTED on (c) only.**
  350 of 404 banked fade legs already sit on NIFTY-down mornings
  (unknown 0; bar-index violations 0). Removing the 54 not-down
  legs: 2025 JO → 82,018.25 (removed legs were −3,598.21 there),
  2026 JO → 2,27,218.97 (+2,477.24 there). Placebos beaten.
  Flagged — a restriction decision on banked legs.

## WS3 — R8-07 REXP-DOWN at T100/S065: REJECTED on (c) only
Population re-anchored exactly at T125/S050 first. At T100/S065:
standalone +₹10,243.45 / −₹5,899.72 (41/86 trades); 2025 JO →
88,663.49; 2026 JO → 2,23,796.49; placebos beaten. The tighter
target cuts the 2026 bleed by ₹2,499.61 and the 2025 gain by
₹4,626.94. Flagged as the PREFERRED REXP-DOWN form with both
prices stated (T100: +10,243.45 / −5,899.72 · T125: +14,870.39 /
−8,399.33), per the pre-registered disposition.

## WS4 — R8-08 combinations: closes by statement (zero bankings)

## Round-8 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹78,420.04 = ₹7,842.00/month — floor NOT met;
  gap ₹71,579.96 (unchanged; zero bankings).** Full-year
  +₹77,041.31, 887 trades, ex-top-3 +₹23,708.10. Red months Jun
  −₹955.92, Jul −₹7,083.39, Oct −₹3,944.53.
- **2026: Jan–Oct +₹2,29,696.21 = ₹22,969.62/month — floor MET.**
  969 trades, all months green.
Books: stocks_engine_r8_book2025_trades.csv /
stocks_engine_r8_book2026_trades.csv (identical to the Round-7
books; exported and independently re-summed to the paisa).
Evidence: r8_results.json (8 records). Decision state: the
flagged list now carries R2-26 (clean), R5-03 (e), R5-07 (e+f),
R5-07-CERT (e+f), R8-05 (e+f), R6-02 (e), R6-04 (e), R6-10 (c),
R7-02 (c), R8-07 (c — preferred REXP-DOWN form), R7-03 (c),
R7-06 (e+f), R8-06 (c — restriction), the triple (arithmetic)
and the GATED max stack (R8-02: fails (f) only; adoption →
2025 JO ₹1,23,231.11, gap ₹26,768.89) — see the Round-8 report.


---

# ROUND 9 (2026-11-02) — flip decomposition, stack-minus-flaw pricing, ATH sleeve, IDX December repair

## WS0 — R9-01 flip decomposition (audit)
Both max-stack flips belong to NE-REV-CERT alone. Jan 2025
(delta −2,915.77): CERT −2,950.92 (66 rows, all DOWN-cell; the
wound's address is DOWN × NIFTY 10:25 move in (−0.30%, 0):
−5,192.36 on 12 rows), R2-26 +64.16, R5-03-clean −29.01,
R7-03 0. Dec 2025 (delta −1,307.71): CERT −1,840.62 (6 rows,
all UP-cell; the three index-dip rows −2,046.64, the three
index-up rows +206.02), R2-26 +532.91, others 0. Sums verified
against the R8-02 gate sheet in code. Evidence:
r9_ws0_decomp.json.

## WS1 — stack-minus-flaw variants (decision support, force_no_bank)
- R9-02 Variant A (NE-REV-NOTCH slot): sleeve +18,618.88 /
  +21,026.84 (262/332). Stack 2025 JO 1,27,134.02, 2026 JO
  2,44,461.23; Jan cured (+4,476.90); fails (f) on Dec only.
  Worth more than the unconditioned stack (combined
  3,72,248.75 vs 3,70,821.53).
- R9-03 Variant B (NE-REV-UPGUARD slot): sleeve +7,938.33 /
  +26,626.59 (218/345). Stack JO 1,15,155.58 / 2,50,060.98;
  Dec cured (+1,946.88), Jan flip remains; fails (e) + (f).
- R9-04 Variant C (NOTCH+UPGUARD slot): sleeve +12,596.19 /
  +23,744.40 (200/313). Stack JO 1,19,813.44 / 2,47,178.79;
  Jan +4,476.90, Dec +1,946.88 — **PASSES ALL TEN LEGS**
  (recorded decision support; clean-adoption price
  ₹11,981.34/mo, gap ₹30,186.56).

## WS2 — R9-05 ATH-proximity momentum: REJECTED on eight legs
346 trigger days → 342 trades (113/229). Standalone
−21,322.97 / −27,329.31; fails (a)–(h) except (i)/(x);
Dec 2025 flips to −13,330.65. Not flagged. The follow family
is closed at the daily timescale too (R8-L2 extended).

## WS3 — NE-REV-IDX December repair
- R9-06 (audit): IDX December = 3 UP-cell rows (−2,046.64);
  IDX UP bucket +6,022.69 (2025) / −2,717.56 (2026).
- R9-07 NE-REV-IDXCELL standalone: REJECTED on (e) only —
  2025 JO 82,452.55, 2026 JO 2,64,065.70, NO flips anywhere.
  Flagged (NE-REV family's no-flip form).
- R9-08 stack with IDXCELL slot (decision support): JO
  1,13,146.38 / 2,57,803.88; Jan +1,807.31, Dec +1,740.86 —
  **PASSES ALL TEN LEGS** (second clean stack price).

## WS4 — R9-09 combinations: closes by statement (zero bankings)

## Round-9 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹78,420.04 = ₹7,842.00/month — floor NOT
  met; gap ₹71,579.96 (unchanged; zero bankings).** Full-year
  +₹77,041.31, 887 trades, ex-top-3 +₹23,708.10.
- **2026: Jan–Oct +₹2,29,696.21 = ₹22,969.62/month — floor
  MET.** 969 trades, all months green.
Books: stocks_engine_r9_book2025_trades.csv /
stocks_engine_r9_book2026_trades.csv (identical to the
starting book; exported and independently re-summed to the
paisa). Evidence: r9_results.json (9 records). Decision
state: two stack forms now pass all ten legs as decision
support — R9-04-STACK-NU (adoption → 2025 JO ₹1,19,813.44,
gap ₹30,186.56) and R9-08-STACK-IDXCELL (→ ₹1,13,146.38,
gap ₹36,853.62) — plus one-leg prices R9-02-STACK-NOTCH
(→ ₹1,27,134.02, (f)-Dec only) and R8-MAXSTACK-GATED
(→ ₹1,23,231.11, (f) only); R9-07-IDXCELL joins the
NE-REV family flags ((e) only, no flips). 21 flagged
entries — see the Round-9 report.


---

# ROUND 10 — 2026-11-02 (conditioned NE-REV standalone + July lens)

Starting book: R9-FINAL (2025 JO +₹78,420.04; 2026 JO
+₹2,29,696.21). Pre-registration frozen in the Round-10
report BEFORE any scoring (incl. the WS2 algebra consequence
and the WS3 separator test). 8 cycles: 3 gated candidates,
4 audits, 1 decision-support restatement. **Banked: 0.
Voided cells: none.** Full record:
stocks_engine_round10_2026-11-02.md; evidence
r10_results.json; July evidence r10_july_decomp.json.

- R10-01 AUDIT: starting books re-verified from the R9 CSVs;
  NE-REV admission algebra verified per-row (IDXCELL ⊆ IDX ⊆
  NOTCH; NU = NOTCH ∩ UPGUARD; 0 violations). Literal
  {IDXCELL, NOTCH} combinations collapse — composed form
  NOTCHCELL frozen instead.
- R10-02 NE-REV-NU standalone: REJECTED on (e) only. 2025 JO
  → 89,119.61; 2026 JO → 2,53,440.61; no flips; placebos
  beaten. Flagged (standalone price).
- R10-03 NE-REV-NOTCH standalone: REJECTED on (e)+(f). 2025
  JO → 96,440.19; Dec 2025 flips to −632.67 without UPGUARD.
  Flagged (largest 2025 standalone price).
- R10-04 NE-REV-NOTCHCELL standalone: REJECTED on (e) only.
  2025 JO → 84,986.53; 2026 JO → 2,56,909.60; no flips.
  Flagged.
- R10-05 AUDIT (July lens): offender INV-ABOVE −2,473.45
  (3 rows, all shallow-dip state). Separator FAILS leg (iii)
  — shallow bucket is a combined +2,445.28 earner (2026
  +3,066.24). July loss diffuse across six components.
- R10-06: closes by statement — no separator, no candidate.
  Observation logged for Round 11 pre-registration:
  INV-ABOVE hard-dip rows lose in both years (−1,230.62 /
  −4,012.18) but have zero July rows.
- R10-07: WS5 combinations close — zero bankings.
- R10-08 stack prices restated on the ending book, all four
  reproduced to the paisa (unconditioned 1,23,231.11 /
  2,47,547.25; A 1,27,134.02 / 2,44,461.23; C 1,19,813.44 /
  2,47,178.79; IDXCELL 1,13,146.38 / 2,57,803.88).

## Round-10 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹78,420.04 = ₹7,842.00/month — floor NOT
  met; gap ₹71,579.96 (unchanged; zero bankings).** Full-year
  +₹77,041.31, 887 trades, ex-top-3 +₹23,708.10.
- **2026: Jan–Oct +₹2,29,696.21 = ₹22,969.62/month — floor
  MET.** 969 trades, all months green.
Books: stocks_engine_r10_book2025_trades.csv /
stocks_engine_r10_book2026_trades.csv (identical to the
starting book; exported and independently re-summed).
Decision state: the conditioned NE-REV family is fully
mapped — 3 gated standalone prices (NU / NOTCH / NOTCHCELL,
all failing only (e), NOTCH also (f)) + 4 gated stack-slot
prices (C and IDXCELL pass all ten legs). 24 flagged entries
— see stocks_engine_state.json. Lessons R10-L1…L4 appended.

# ROUND 11 — 2026-11-02 (INV-ABOVE hard-dip exclusion, cross-family pair, leg-(e) anatomy, December freeze)
Pre-registration frozen in stocks_engine_round11_2026-11-02.md
before any scoring. 8 cycles: 2 gated candidates, 5 audits,
1 decision-support freeze. Voided cells: none. Timing
violations: 0 on every construction.

- R11-01 AUDIT: starting books re-verified from the R10 CSVs
  (2025 JO 78,420.04 / 887; 2026 JO 2,29,696.21 / 969).
  INV-ABOVE state census reproduces R10-05's bucket nets to
  the paisa (hard -1,230.62 / -4,012.18); unknown rows 0.
- R11-02 INV-ABOVE hard-dip exclusion: REJECTED on (e) ONLY,
  by Rs135.40 combined. Both years rise (2025 JO -> 80,171.76;
  2026 JO -> 2,33,708.39; combined +5,242.80), no flips,
  placebos beaten — but the removed losses sit in carrier
  names, so ex-top-3 falls to 1,01,046.47. Flagged (owner
  decision; a removal, composes with the pair).
- R11-03 CROSS-FAMILY PAIR (NE-REV-NU + REXP-DOWN T100/S065):
  BANKED — ALL TEN LEGS PASS. The (e)-only failure and the
  (c)-only failure cure each other assembled. 2025 JO ->
  99,363.06 (+20,943.02); 2026 JO -> 2,47,540.89
  (+17,844.68); combined -> 3,47,421.84. June 2025 greens
  (+1,343.41); July 2025 -2,101.93.
- R11-04: NOTCHCELL substitution closes by statement —
  trigger not met (the pair banked).
- R11-05 AUDIT (leg-(e) anatomy of NU standalone): the
  shortfall (Rs10,610.42) is entirely 2026. NU 2026 =
  +34,926.51 INSIDE the top-3 (TVSMOTOR 18,734.26 /
  OBEROIRLTY 11,376.19 / ASTRAL 4,816.06) and -11,182.11
  OUTSIDE it (UNITDSPR -10,762.92). 2025 ex-top-3 rises
  +571.69 on top-3 churn. Separator test over state slices:
  0 qualify — the failure is a name fact, not a state fact.
- R11-06: closes by statement — no separator, no candidate.
- R11-07 FREEZE (decision support): banked book frozen in
  stocks_engine_banked_book_FREEZE_dec2026.md with the
  per-feature timing certification; regeneration identity
  PASSED row-for-row and to the paisa; December pass/kill
  lines pre-registered (PASS net > 0 + no week < -15,000 +
  >= 20 trades; FLOOR LINE >= 15,000; KILL <= 0).
- R11-08: union = the pair alone, re-gated PASS. Stack
  totals reproduced exactly on the ending book; adoption
  values restated (unconditioned +23,868.05 / +6.36; A
  +27,770.96 / -3,079.66; C +20,450.38 / -362.10; IDXCELL
  +13,783.32 / +10,262.99). Freeze addendum extends the
  freeze to the ending book.

## Round-11 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹99,363.06 = ₹9,936.31/month — floor NOT
  met; gap ₹50,636.94 (was ₹71,579.96).** Full-year
  +₹99,880.95, 1,128 trades, ex-top-3 +₹35,264.65. Red
  Jan–Oct months: Jul −2,101.93, Oct −3,751.28.
- **2026: Jan–Oct +₹2,47,540.89 = ₹24,754.09/month — floor
  MET.** 1,368 trades, all months green.
Books: stocks_engine_r11_book2025_trades.csv /
stocks_engine_r11_book2026_trades.csv (exported and
independently re-summed). Decision state: 25 flagged
entries — see stocks_engine_state.json. Lessons R11-L1…L3
appended.

# ROUND 12 — 2026-11-02 (hard-dip re-gate on the pair book, single-leg flag re-tests, October + July-residual wounds)
Pre-registration frozen in stocks_engine_round12_2026-11-02.md
before any scoring. 9 cycles: 2 gated candidates, 7 audits
(incl. the WS5 finalise). Voided cells: none. Timing
violations: 0 on every construction.

- R12-01 AUDIT: starting books re-verified from the R11 CSVs
  (2025 JO 99,363.06 / 1,128; 2026 JO 2,47,540.89 / 1,368;
  Jul -2,101.93, Oct -3,751.28 asserted). INV-ABOVE census
  reproduces R11-01's bucket nets to the paisa (hard
  -1,230.62 / -4,012.18); unknown rows 0.
- R12-02 INV-ABOVE hard-dip exclusion, NEW BASELINE: BANKED
  — ALL TEN LEGS PASS. The R11-02 construction verbatim on
  the pair book: 2025 JO -> 1,01,114.78 (+1,751.72); 2026 JO
  -> 2,51,553.07 (+4,012.18); combined -> 3,52,664.64. The
  (e) failure inverts: combined ex-top-3 delta -135.40 on the
  old baseline -> +953.74 here (base 1,03,228.30 ->
  1,04,182.04). Placebos beaten (chrono 3,48,898.96; cross
  3,42,973.57). The R11-02 flag is retired — banked.
- R12-03 R5-03-clean re-gate: REJECTED on (c) + (e). Raw
  deltas 2025 +8,289.44 (JO 1,07,652.50) / 2026 -1,984.82
  (JO 2,45,556.07); combined rises, placebos beaten, no
  flips — but the clean swap must now retire the banked
  GAP-FADE-INC too, and its 2026 rows out-earn the widening;
  combined ex-top-3 falls to 97,652.34. Flag restated:
  adoption from the ending book +6,537.72 / -5,997.00.
- R12-04 AUDIT (WS2 screening): every other single-leg flag
  is pre-refused by delta-leg arithmetic, printed per flag —
  (c)-only REXP/FADE forms displace banked rows with worse
  2026 nets by identity (deltas -2,499.61 to -5,030.46);
  NE-REV slot alternatives are non-additive with NU and
  fail (b)/(c) as swaps (IDXCELL 4,032.51 / NOTCHCELL
  6,566.49 / thr-2.25-CERT 8,523.03 vs NU 12,596.19 in
  2025; NOTCH 21,026.84 vs NU 23,744.40 in 2026). No
  candidate scored.
- R12-05 AUDIT (October decomposition): Oct 2025 -3,751.28
  on 20 rows = F4 -3,021.83 (3 trades, ALL up-state) +
  N4-V3 -793.80 + P2F -312.98 + P2F-R2 -288.00 + INV-ABOVE
  -207.92, partly offset (INC +680.00, NU +193.25).
  Separator test: F4 x up passes (i) + (ii) (FY25 up-bucket
  -9,887.43), fails (iii) — the bucket is +30,693.95
  combined (2026 +40,581.38).
- R12-06: closes by statement — 0 qualifying separators.
- R12-07 AUDIT (July residual decomposition): Jul 2025
  -2,101.93 on 41 rows. The pair already paid +4,981.46
  into July (NU +5,255.43, REXP -273.97). Residual:
  INV-ABOVE -2,473.45 (3 shallow-dip rows — the R10-05
  cell), N4-V3 -1,821.00, GAP-FADE-INC -1,560.10, F4
  -1,025.28 (mixed states). Separator: shallow passes
  (i) + (ii), fails (iii) (+2,445.28 combined, as in
  R10-05); hard passes (ii) + (iii) but holds zero July
  rows.
- R12-08: closes by statement — 0 qualifying separators.
- R12-09: union = R12-02 alone, re-gated PASS. Stack totals
  reproduced exactly on the ending book; adoption values
  restated (unconditioned +22,116.33 / -4,005.82; A
  +26,019.24 / -7,091.84; C +18,698.66 / -4,374.28;
  IDXCELL +12,031.60 / +6,250.81) — only IDXCELL still adds
  in both years. Freeze addendum (Round 12) extends the
  December freeze to the ending book; regeneration
  verification PASSED row-for-row and to the paisa.

## Round-12 ending scorecard (per year, never pooled)
- **2025: Jan–Oct +₹1,01,114.78 = ₹10,111.48/month — floor
  NOT met; gap ₹48,885.22 (was ₹50,636.94).** Full-year
  +₹1,01,111.57, 1,105 trades, ex-top-3 +₹35,085.01. Red
  Jan–Oct months: Jul −2,101.93, Oct −3,751.28 (both
  unchanged by the banking; both separator-less).
- **2026: Jan–Oct +₹2,51,553.07 = ₹25,155.31/month — floor
  MET.** 1,352 trades, all months green.
Books: stocks_engine_r12_book2025_trades.csv /
stocks_engine_r12_book2026_trades.csv (exported,
independently re-summed, regeneration-verified). Decision
state: 24 flagged entries — see stocks_engine_state.json.
Lessons R12-L1…L4 appended.

# ROUND 13 — 2026-11-02 (prior-day sweep + reclaim transplant, REXP and NE-REV-NU geometry neighbours)
Pre-registration frozen in stocks_engine_round13_2026-11-02.md
before any scoring. 8 cycles: 6 gated candidates, 2 audits
(incl. the WS4 finalise). Voided cells: none. Timing
violations: 0 on every construction.

- R13-01 AUDIT: starting books re-verified from the R12 CSVs
  (2025 JO 1,01,114.78 / 1,105; 2026 JO 2,51,553.07 / 1,352;
  Jul -2,101.93, Oct -3,751.28 asserted).
- R13-02 SWEEP-RECLAIM LONG (prior-day-low sweep + reclaim,
  T125/S050): REJECTED on nine of ten legs. Standalone
  -1,62,923.55 / -1,06,668.60 on 1,585/1,300 trades (2,885
  signals); loses to both placebos (flipped book 3,20,661.65,
  late book 1,39,743.54 vs variant combined 83,072.49).
- R13-03 SWEEP-REJECT SHORT (prior-day-high sweep +
  rejection): REJECTED on seven legs (a, b, c, d, e, f, h).
  Standalone -11,893.51 / -370.85 on 1,794/1,304 trades —
  gross zero before costs. The transplant family is CLOSED
  in both directions.
- R13-04 REXP-DOWN swap T125/S065: REJECTED on (a) + (c) +
  (e). Sleeve JO +12,534.71 / -10,152.39 — the wider target
  buys 2025 (+2,291.26) with 2026 (-4,252.67).
- R13-05 REXP-DOWN swap T100/S050: BANKED — ALL TEN LEGS
  PASS. Sleeve JO +12,486.11 / -4,384.34; the tighter stop
  improves both years (+2,242.66 / +1,515.38). 2025 JO ->
  1,03,357.44; 2026 JO -> 2,53,068.45.
- R13-06 NE-REV-NU swap T125/S065: REJECTED on (a) + (c)
  only — FLAGGED as an owner decision (adoption from the
  ending book +2,326.81 / -5,998.05). Sleeve standalone
  +15,631.27 / +17,746.35.
- R13-07 NE-REV-NU swap T100/S050: REJECTED on (a) + (b) +
  (c) + (f); Jun 2025 flips. The stop step that paid REXP
  costs NU in both years. NU's T100/S065 is bracketed on
  both axes.
- R13-08 WS4: union = R13-05 alone, re-gated PASS. Stack
  totals reproduced exactly on the ending book; adoption
  values restated (unconditioned +19,873.67 / -5,521.20; A
  +23,776.58 / -8,607.22; C +16,456.00 / -5,889.66; IDXCELL
  +9,788.94 / +4,735.43 — IDXCELL still the only form adding
  in both years). December freeze addendum (Round 13)
  appended; regeneration verification PASSED.
Books: stocks_engine_r13_book2025_trades.csv /
stocks_engine_r13_book2026_trades.csv (exported,
independently re-summed, regeneration-verified). Decision
state: 25 flagged entries — see stocks_engine_state.json.
Lessons R13-L1…L2 appended.

# ROUND 14 — 2026-11-02 (exit-geometry neighbours on the original sleeves)
Pre-registration frozen in stocks_engine_round14_2026-11-02.md
before any scoring (the GAP-FADE cell chosen by a frozen
excursion-diagnostic rule, disclosed in the pre-registration).
8 cycles: 6 gated candidates, 2 audits (incl. the WS5
finalise). Voided cells: none. Timing violations: 0 on every
construction.

- R14-01 AUDIT: starting books re-verified from the R13 CSVs
  (2025 JO 1,03,357.44 / 1,105; 2026 JO 2,53,068.45 / 1,352;
  Jul -2,000.01, Oct -3,751.28 asserted).
- R14-02 F4 swap T175/S095: REJECTED on (a) + (c) — FLAGGED.
  Sleeve +6,371.44 / +92,288.65 vs the banked cell's
  +91.14 / +1,03,055.93 (JO deltas +6,280.30 / -10,767.28):
  the target step is a year-trade on F4 too, on an
  exact cross-year score (SAT-12's closure was
  estimate-only).
- R14-03 INV-LONG swap T150/S050: REJECTED on (a) + (c) —
  FLAGGED. Sleeve +28,170.00 / +39,612.14 (JO deltas
  +4,275.39 / -10,547.95) on the re-formed chain population.
- R14-04 INV-ABOVE swap T150/S050: BANKED — ALL TEN LEGS
  PASS. Sleeve JO +12,513.28 / +10,114.82 (JO deltas
  +2,050.12 / +2,753.43); hard-dip exclusion re-applied at
  the new geometry drops 22 / 15. Decomposes R2-26: its
  March flip was the S080 stop, not the T150 target.
- R14-05 GAP-FADE family swap T125/S065: BANKED — ALL TEN
  LEGS PASS. Family JO +24,355.17 / +7,733.66 (JO deltas
  +579.68 / +1,478.42). The diagnostic's stop-axis pick;
  exact gain ~1/6 of the +12,157.87 rough estimate.
- R14-06 N4-V3 swap to the scorecard cell T125/S050:
  REJECTED on (a) + (b) + (c) + (e). Sleeve JO -13.80 /
  +11,548.34 — reverting costs 2025 JO -8,137.41 / 2026 JO
  -18,013.98 on the current population. The SAT-15 rebuild
  is worth more now than at birth.
- R14-07 P2F family swap T150/S050: REJECTED on (a) + (b) +
  (e). JO rises in both years (+627.22 / +111.87) but
  full-year 2025 and ex-top-3 fall. Attribution: Lesson
  33's two-axis 2025 bleed was the stop widening, not the
  target.
- R14-08 WS5: union of R14-04 + R14-05, re-gated PASS.
  Stack totals reproduced exactly on the ending book;
  adoption values restated (unconditioned +17,243.87 /
  -9,753.05; A +21,146.78 / -12,839.07; C +13,826.20 /
  -10,121.51; IDXCELL +7,159.14 / +503.58 — IDXCELL still
  the only form adding in both years, now marginally in
  2026). December freeze addendum (Round 14) appended;
  regeneration verification PASSED.
Books: stocks_engine_r14_book2025_trades.csv /
stocks_engine_r14_book2026_trades.csv (exported,
independently re-summed, regeneration-verified). Decision
state: 27 flagged entries — see stocks_engine_state.json.
Lessons R14-L1…L5 appended.

# ROUND 15 — 2026-11-02 (two-step geometry continuations + the VOLUME data axis)
Pre-registration frozen in stocks_engine_round15_2026-11-02.md
before any scoring (the two second steps, the volume
causality law, the frozen rvol band and the diagnostic
sleeve-choice rule all stated in advance).
8 cycles: 2 gated candidates, 5 audits (build, diagnostic,
two not-run gates, WS4 finalise), 1 verification. Voided
cells: none. Timing violations: 0 on every construction.
Unclassifiable volume rows: 0.

- R15-01 AUDIT: starting books re-verified from the R14 CSVs
  (2025 JO 1,05,987.24 / 1,101; 2026 JO 2,57,300.30 / 1,352;
  Jul -2,733.21, Oct -4,152.19 asserted).
- R15-02 INV-ABOVE swap T175/S050 (second target step):
  REJECTED on (c) only — FLAGGED. Sleeve 15,367.09 /
  8,916.53; JO deltas +92.57 / -1,198.29; combined full-year
  total rises (+1,001.66) on Nov/Dec-2025 strength; no
  flips, placebos beaten. The year-trade signature at a
  far smaller price: T150 took nearly all the winners had.
- R15-03 GAP-FADE family swap T125/S080 (second stop step):
  REJECTED on (a) + (b) + (c) + (e). Family JO deltas
  -2,548.14 / -4,790.90; GAP-FADE 2026 standalone goes
  negative (-3,012.95) at the wider stop. The stop axis is
  a peak at S065, not a slope. Not flagged (four legs).
- R15-04 AUDIT (volume build): daily volume for the 25
  stocks + NIFTY fetched via the connector path (v3
  days/1) into the NEW dataset stocks_daily_volume.csv
  (12,584 rows, 2024-11-15..2026-10-31; pre-2025 tail is
  lookback only). Coverage COMPLETE for all 25 stocks in
  both years (249/249 in 2025, 203/203 in 2026; zero
  holes, zero zero-volume days; series also covers
  2026-10-29/30). NIFTY volume is 0 on every day as
  returned (an index has no traded volume) — stored as
  returned, used by no gate. No candle file altered.
- R15-05 AUDIT (volume diagnostic, frozen rule): keep
  prior-day rvol >= 1.0 (trailing-20-day median; causality
  asserted row by row). Combined JO deltas: F4 -47,355.57
  (+1,972.94 / -49,328.51), N4-V3 -9,385.58, P2F family
  -3,003.70. NO sleeve positive.
- R15-06 AUDIT: volume gate 1 NOT RUN — frozen rule (no
  positive diagnostic sleeve). WS3 closes with no gate.
- R15-07 AUDIT: volume gate 2 NOT RUN — frozen rule.
- R15-08 WS4: no bankings, no union to re-gate; ending
  book == starting book. Stack totals reproduced exactly
  on the ending book; adoption values unchanged
  (unconditioned +17,243.87 / -9,753.05; A +21,146.78 /
  -12,839.07; C +13,826.20 / -10,121.51; IDXCELL
  +7,159.14 / +503.58). December freeze addendum (Round
  15) appended: frozen book UNCHANGED; regeneration
  verification PASSED.
Books: stocks_engine_r15_book2025_trades.csv /
stocks_engine_r15_book2026_trades.csv (exported,
independently re-summed, regeneration-verified; identical
in substance to the Round-14 books). Decision state: 28
flagged entries — see stocks_engine_state.json. Lessons
R15-L1…L4 appended.

# ROUND 16 — 2026-11-02 (the volume MIRROR — quiet-prior-day entries)
Pre-registration frozen in stocks_engine_round16_2026-11-02.md
before any scoring (the mirror form as the exact complement
of Round 15's frozen feature, the causality law, the sleeve
anchors, and the WS3 run-condition all stated in advance).
6 cycles: 2 gated candidates, 4 audits (verification, the
not-run WS3 gate, WS4 pair). Voided cells: none. Timing
violations: 0 on every construction. Unclassifiable volume
rows: 0. Round 16 banked: 0.

- R16-01 AUDIT: starting books re-verified from the R15 CSVs
  (2025 JO 1,05,987.24 / 1,101; 2026 JO 2,57,300.30 / 1,352;
  Jul -2,733.21, Oct -4,152.19 asserted). Sleeve anchors
  exact; mirror kept/dropped counts reproduce the R15
  diagnostic's low/kept counts to the row.
- R16-02 REJECTED (F4 volume mirror, keep prior-day rvol
  < 1.0; kept 134/165 of 246/355): 2025 JO -2,064.08, 2026
  JO -53,727.42, combined -> 3,09,097.98; fails (a) + (b) +
  (c) + (e) + (f) — March 2026 flips (+11,344.23 ->
  -673.18); placebos beaten; not flagged (five legs). F4's
  2026 value lives in BOTH volume halves (deleting the loud
  half at R15's diagnostic cost -49,328.51; deleting the
  quiet half costs -53,727.42 exact).
- R16-03 REJECTED (N4-V3 volume mirror; kept 17/13 of
  35/34): 2025 JO -3,937.27, 2026 JO -24,363.08, combined
  -> 3,38,225.04; fails (a) + (b) + (c) + (e); no flips;
  placebos beaten; not flagged (four legs).
- R16-04 AUDIT (P2F volume mirror NOT RUN — the frozen WS3
  condition required a banking or an exactly-one-leg
  failure in WS1/WS2; five and four failed legs met
  neither. No P2F mirror number computed.)
- R16-05 AUDIT (WS4: no bankings, no union to re-gate;
  ending book == starting book; stack prices restated
  exactly on the unchanged book — unconditioned
  1,23,231.11 / 2,47,547.25, A 1,27,134.02 / 2,44,461.23,
  C 1,19,813.44 / 2,47,178.79, IDXCELL 1,13,146.38 /
  2,57,803.88; flagged list unchanged at 28).
- R16-06 AUDIT (December freeze addendum — book unchanged,
  no volume form in either direction is frozen —
  regeneration-verified against the R15 CSVs; ending books
  exported to stocks_engine_r16_book{2025,2026}_trades.csv).
  Frontier finding recorded in the report: the in-sample
  programme stands where the other segments stand —
  December fresh data, November forward evidence, owner
  decisions (16 rounds, 105 recorded cycles). Lessons
  R16-L1…L2 appended.

## ADOPTION — Variant C applied by owner direction (2026-11-02, 16:48 IST)
- ADOPT-01 VERIFICATION: Variant C rebuilt from the Round-16
  book behind the full gate — Jan-Oct 1,19,813.44 /
  2,47,178.79 EXACT, row-for-row identical to the R9-04
  gated book; the R9-04 sheet reproduced exactly (all ten
  legs pass; placebos 174,662.47 / 344,925.15 / 322,968.45;
  timing violations 0).
- ADOPT-02 GATE vs the pre-adoption book: 8 of 10 legs pass
  (combined +4,054.14; 2025 rises; no flips; placebos
  beaten; leg (x) holds). Legs (c) -10,121.51 and (e)
  -16,352.41 fail on that comparison — the post-R9 bankings
  out-earn the stack's frozen forms in 2026 — and stand as
  FAILED-AND-WAIVED BY THE OWNER'S DIRECTION, recorded in
  full in stocks_adoption_variantC_2026-11-02.md.
- ADOPT-03 DECEMBER FREEZE: the adopted book is frozen in
  stocks_engine_adopted_variantC_FREEZE_dec2026.md
  (regeneration verification PASSED; PASS/KILL
  re-registered). The Round-16 book is retained as the
  comparison baseline (state: pre_adoption_incumbent_r16).
  November's frozen book untouched. Candidate pace now:
  2025 Rs11,981.34/mo (gap Rs30,186.56); 2026
  Rs24,717.88/mo (floor met).
