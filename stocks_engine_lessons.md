# ENGINE LESSONS — what the mistakes taught (read at the start of every cycle; appended at the end of any cycle that learns something)

The engine's charter (user, 2026-10-31): recursive self-improvement — *improve from your own mistakes, correct them, and build a new system.* A lesson is only written when a controlled run proved it, with its evidence named.

1. **Timing is truth.** A leak (entries before their qualifying information existed) manufactured lakhs of fake profit (Morning-Mover line, B4/B5 audit). Every system is rebuilt honest and audited trade-by-trade; a leaky total is never "adjusted down" — it is discarded. *(Evidence: stocks_moverB4/B5_report.md)*
2. **Price-derived events are information-free on his 25.** PDH/PDL breaks, retest holds, level rejections, 20-day breaks, RSI crosses (all forms), VWAP deviation: in family after family the stale-placebo loses LESS than the real rule — gross expectancy ≈ ₹0 to −₹19/trade before costs. New systems must not be built on price events alone. *(Evidence: stocks_L1_report.md, stocks_RSI1_report.md, stocks_S4_report.md)*
3. **Money lives in information and in state.** Results/news reactions (N4-V3, P2F) and joint market states (below-50DMA × moderate move — F4; below-trend pools — INV-LONG) are the only verified-real threads. Build new systems from these two materials.
4. **The exit is half the system.** Removing the small target destroyed P2F's edge; widening F4's target (+1.25→+1.50%) and stop (−0.65→−0.80%, because 18% of stop-outs were dips that mean-reverted to flat) added ≈ +₹24k. Diagnose exit progress (excursions) before touching entries. *(Evidence: stocks_T2_report.md, engine cycles OC-3/OC-4)*
5. **Surgical removal works when a part is rotten everywhere.** setup3_bounce_rejection was the only F4 setup negative in both the target month and the full period; deleting it banked +₹9,653.53 and improved two other months. A part negative in only one month is a mirage — leave it.
6. **Concentration is the standing risk.** TVSMOTOR/GLENMARK have carried whole books. No system is believed until it survives ex-top-3 stress; breadth is reported beside every total.
7. **Joint states can pass when their parts fail — and that is exactly why they are suspect.** F4's gate components each fail standalone. Anything discovered this way is frozen verbatim and judged on fresh data (December), never re-tuned in-sample.
8. **One month is a regime, not a verdict.** October 2026 was 100% below-trend days; its outliers are regime artefacts until other months agree. Halves + full month tables or it didn't happen.
9. **Rules generalise; dates don't.** "No trades on special sessions" (any month, any year) is a rule and banked +₹4,433.84; "skip Feb 1–2" is a patch and is forbidden.
10. **Bank partial progress.** All-or-nothing acceptance stalled the loop (RF-1 nearly discarded despite improving everything it touched). A fix that improves the target and breaks nothing is banked; the recursion continues on the residual.
11. **Poison is stock × mechanism, not stock.** ASTRAL is one of the book's best names in the state/pool systems (INV-LONG +₹5,350.84, F4 +₹20,462.15) and a 4-of-4 loser in BOTH event-follow systems (N4-V3 −₹1,611.45, P2F −₹1,592.10) — its reactions fade (3/3 in the frozen reaction profiles), so following them loses while gated intraday flow on the same stock wins. Exclusions must be scoped to the mechanism that fails, never applied book-wide on a stock's name. *(Evidence: engine cycle AU-1; stocks_engine_au1_diag.py, stock_reaction_profiles.md)*

*Addendum to Lesson 11 (JU-1, 2026-10-31):* second confirming instance — HINDUNILVR is the other fade-profile name the frozen profiles flag (0 CONTINUED / 2 FADED; worst ungated P2 payer −₹3,484.80), and its P2F trades were 2/2 losers (−₹2,294.05); the P2F-scoped exclusion banked cleanly (+₹1,100.00 July, +₹1,194.05 February, nothing else touched) while N4-V3's trade in the same stock was the month's biggest win (+₹2,553.13) and stays. Stock × mechanism, confirmed twice.

12. **A fix is judged net of the secured floors.** The largest June slice (F4 × GODREJCP, June −₹2,460.96, full −₹3,814.67) was unbankable because the same slice is +₹1,060.25 in secured October, whose headroom was ₹29.72 — removing a target-month loser that is a secured-month winner breaks the floor. When a target month resists, scan for slices whose secured-month slices are zero or negative; the smaller clean slice (INV-LONG × BDL, June −₹1,406.25, October −₹542.30) banked and greened the last red month. *(Evidence: engine cycle JN-1; stocks_engine_jn1_diag.py, stocks_engine_jn1_score.py)*

*Addendum to Lesson 11 (JN-1, 2026-10-31):* third confirming instance — BDL is a core earner in the event systems (+₹10,168.59 across N4-V3/P2F/F4) and a 22-trade, 6-winner loser inside INV-LONG's pool (−₹1,486.93); the INV-LONG-scoped exclusion greened June (the last red month) and relieved April, while the event components keep trading BDL untouched.

13. **A causal profile needs history the window doesn't have.** P2F-PROFILE (CH-1) was built to replace the AU-1/JU-1 name exclusions with a rule — direction from each stock's own prior reactions (≥2 classified priors, ≥2/3 share). On a ≥2.0% event set there are only ~2 reactions per stock in the whole 10 months, so the rule classified 3 of 48 trades and flipped ZERO: ASTRAL's −1.86% February reaction sits below the band, leaving its August trade with just 1 classified prior — default follow, straight back into the loss the exclusion had removed. The challenger degenerated into ungated follow at a wider band (2.0 vs 2.5) and wider stop (S065 vs S050 — the wider stop that helped F4 hurt P2F; exit economics are mechanism-specific), lost ₹5,723.81 vs the incumbent component, flipped August red, and was rejected on 3 of 5 gate legs despite beating its placebo standalone (+₹13,120.32 vs +₹12,411.62 — a margin carried by 3 trades). Corollary: within a single 10-month window, mechanism-scoped name exclusions ARE the honest implementation of Lesson 11; a profile rule needs multi-year history or a denser event set before it can even fire, and a rule that never fires has tested nothing. *(Evidence: engine cycle CH-1; stocks_engine_ch1_score.py, stocks_engine_ch1_result.json)*
14. **Thin months are hostages to every component's exits.** The N4-V3 exit rebuild (CH-2) was real money — +₹9,483.45 at component level, almost exactly the +₹9,477.40 the excursion diagnostic estimated, with the assembled total, October and ex-top-3 all passing — and it was still unbankable, because June (+₹172.76) and August (+₹185.69) free-rode on N4's old T125/S050 exits and flipped red (−₹481.90 / −₹3,649.16) under the new ones. A whisker-thin green month is not a secured month; it is an exposure to the next change anywhere in the book. Sequence matters: thicken the thin months first, then the blocked improvements unlock (the N4 rebuild's revisit condition is written in the state). *(Evidence: engine cycle CH-2; stocks_engine_ch2_diag.py, stocks_engine_ch2_score.py, stocks_engine_ch2_result.json)*
15. **When a rotten slice is floor-blocked, split it by direction before abandoning it.** F4 × GODREJCP was negative in June (−₹2,460.96) and full-period (−₹3,814.67) but unbankable for two cycles because its October slice (+₹1,060.25) exceeded October's headroom — Lesson 12 said leave it. The direction split showed the blockage and the rot were different trades: the SHORT half (10 tr, −₹4,754.92, 2/10 winners, all skill_or_breakdown) had an October slice of exactly ₹0.00, while the LONG half is full-period positive (+₹940.25). Removing only the SHORT half banked +₹4,754.92, thickened June 2.57× past the CH-2 revisit need, and left October untouched to the paisa. Poison can be stock × mechanism × direction; a secured-month winner inside a slice does not sanctify the slice's other direction. *(Evidence: engine cycle SAT-1; stocks_engine_sat1_diag.py, stocks_engine_sat1_score.py, stocks_engine_sat1_result.json)*

*Addendum to Lesson 4 (SAT-2, 2026-10-31):* exit medicine is population-specific. The stop-widening that rescued October (OC-4: that month's stop-outs were dips that mean-reverted to flat) does NOT transfer to August: of August's 11 F4 stop exits, **0 reached the +1.50% target post-exit, 7 continued deeper, 4 went flat** (rough swings: S095 +₹262.61, S110 −₹1,191.02 for August). Same component, same exits, different month-population, opposite prescription. Diagnose the target month's own stop population (post-exit first passage) before prescribing an exit change — never import another month's exit verdict. *(Evidence: engine cycle SAT-2; stocks_engine_sat2_diag3.py, stocks_engine_sat2_diag3.json)*
16. **A blocked fix's recorded deltas expire — but unevenly: re-measure before relying on ANY of them.** SE-1-F4R1 sat blocked for three cycles on its recorded October cost (₹1,551.75) and total benefit (+₹852.58). SAT-3 re-measured it at the post-SAT-1/SAT-2 book: the October cost was **invariant to the paisa** (₹1,551.75 — the 8 October round2 legs were never touched by the intervening surgeries), while the total benefit had **decayed to +₹11.83** (the SAT-1/SAT-2 deletions had already harvested round2 losers in other months), September's delta had grown (+₹2,471.53 → +₹2,982.10), August's had worsened (−₹429.57 → −₹775.25, leaving August at +₹103.44), and May's had flipped sign. The state's estimate of the binding leg (₹187.01 short) proved exactly right; the assumption that F4R1 was still a total-raising improvement did not survive contact with the current book. Corollary: a revisit condition is a hypothesis about a book that no longer exists — every banked change to the same component voids the blocked fix's other-months measurements, and only a fresh scoring at the current state may be banked on. *(Evidence: engine cycle SAT-3; stocks_engine_sat3_score.py, stocks_engine_sat3_result.json)*
17. **A trigger threshold is validated when its complement fails.** N4-LOWBAND (SAT-4) traded the exact slice N4-V3 excludes — combined reaction days with the 09:30 move in [0.75%, 1.0%), same machinery (construction anchor 56/56 against the V3 dump), same entries, same T125/S050 exits. The slice loses: 14 trades, −₹1,984.09, win rate 14.3% (2/14), expectancy −₹141.72, halves flip (+₹2,730.29 / −₹4,714.38), breadth 2/12, and it loses in August itself (−₹1,026.45) — the month it was built to thicken. Below 1%, a reaction-day move by 09:30 carries no follow-through worth following; the ≥1.0% floor is load-bearing, not a tuned artefact. Corollary: when a band/threshold looks arbitrary, score its complement before widening it — a failing complement is evidence FOR the boundary. *(Evidence: engine cycle SAT-4; stocks_engine_sat4_score.py, stocks_engine_sat4_result.json)*

*Addendum to Lesson 15 (SAT-5, 2026-10-31):* second confirming instance — F4 × HINDUNILVR looked nearly harmless as a whole (−₹1,184.02) only because its LONG half earns (+₹1,479.98; October +₹5,369.90); the SHORT half was the rot (9 tr, −₹2,664.00). Direction-scoped removal banked +₹2,664.00, thickened June (+₹1,040.00) and pushed October headroom (₹2,681.54) past SE-1-F4R1's invariant October cost. This was also the watchdog's never-scored candidate: its recorded numbers survived three intervening cycles **to the paisa** because none of SAT-1..SAT-4 touched a HINDUNILVR SHORT leg — the positive instance of Lesson 16's invariance clause (deltas on untouched legs do not expire; deltas on touched legs do).

*Addendum to Lesson 4 (SAT-5, 2026-10-31):* exit medicine is population-specific, confirmed from the mirror side. The full INV-LONG exit grid (17 dumps: T100–T200 × S050–S080 + two trails, same entries) was re-scored at the current book: **every alternate scores below the incumbent T125/S050 at component level** (−₹2,466.26 to −₹18,094.15). F4's population wanted target AND stop widened; INV-LONG's population peaks at the tightest tested pair and loses on every widening. There is no book-level exit prescription — only per-population excursion evidence, and a grid peak already in place is a closed family.

*Addendum to Lesson 16 (SAT-6, 2026-10-31):* second positive instance, and the invariance is checkable BEFORE scoring. SAT-5 intervened on F4 between SAT-3's measurement and SAT-6's banking test, which by the lesson's letter voided every SAT-3 delta — but the intervention's leg composition was verifiable in-run: the 9 deleted HINDUNILVR-SHORT trades were **all direct legs, 0 round2**, so the round2 set re-measured **identical to the paisa** (70 tr / −₹11.83; October cost ₹1,551.75 invariant across THREE book states: SE-1, SAT-3, SAT-6). A blocked fix's deltas expire only on the legs the intervening changes actually touched; when a pending deletion and an intervening deletion act on disjoint leg populations of the same component, the measurement carries. Corollary for banking: F4R1's banked value was nominal (+₹11.83 total) — its real content was distributional (September +₹2,982.10, June +₹1,393.79, April +₹1,720.02, ex-top-3 +₹1,133.01) bought with August thinning to +₹103.44 and the N4-revisit shortfall growing to ₹3,917.10. A gate can pass on all legs while the trade it makes is month-shape, not money; report both, every time. *(Evidence: engine cycle SAT-6; stocks_engine_sat6_score.py, stocks_engine_sat6_result.json)*

*Addendum to Lesson 12 (SAT-7, 2026-10-31):* a floor block is a property of the HEADROOM, not of the slice — re-scan blocked direction-slices whenever headroom changes. F4 × UNITDSPR × SHORT was recorded floor-blocked in SAT-2 (its October slice +₹780.00 vs headroom then ₹572.02). Two later banks (SAT-5, SAT-6) moved headroom to ₹1,129.79 without touching a single UNITDSPR leg, and the identical slice — August −₹672.16, full −₹1,847.01 (8 tr, 3 w), every other affected month negative — banked cleanly in SAT-7: August +₹103.44 → +₹775.60, total +₹148,270.20, October ₹50,349.79 (headroom ₹349.79 left). A "blocked" verdict expires with the arithmetic that produced it; the blocked-slice registry is a queue to re-test on every headroom change, not a graveyard. The same cycle's winners-side search was negative and is recorded as such: August's winners share no ex-ante state its losers lack (all 15 F4 August trades enter 10:xx; every premove sub-band is full-period positive; the event wins are one name, GLENMARK, in both directions) — when the state search finds nothing, say so and take the deletion route rather than inventing a gate. *(Evidence: engine cycle SAT-7; stocks_engine_sat7_diag.py, stocks_engine_sat7_score.py, stocks_engine_sat7_result.json)*

*Addendum to Lesson 15 (SAT-8, 2026-10-31):* third, fourth and fifth confirming instances now on record — UNITDSPR SHORT (SAT-7: −₹1,847.01, banked when headroom grew past its October slice) and HINDCOPPER SHORT (SAT-8: 12 tr, −₹1,094.95, 4 w, October slice exactly ₹0.00; the name as a whole is +₹697.56 only because its LONG half earns +₹1,792.51). The same cycle establishes the queue's limit: with HINDCOPPER banked, the August-negative × full-period-negative × direction-slice registry is **empty at this book** — the only other such slice (F4 × GLENMARK × SHORT) is floor-blocked (October +₹1,404.72 vs headroom ₹349.79) AND a Lesson 6 concentration name (top-3 earner), so it is not a real candidate. The direction-slice space is finite and enumerable; once it is exhausted, further thickening of the target month cannot come from deletions — it needs new Lesson-3 material (a genuinely new earning component) or headroom growth. Report the exhaustion plainly rather than slicing thinner. *(Evidence: engine cycles SAT-7/SAT-8; stocks_engine_sat7_diag.py, stocks_engine_sat8_diag.py, stocks_engine_sat8_score.py, stocks_engine_sat8_result.json)*
18. **A joint state does not mirror — and a placebo must be beaten per-trade, not just in total.** F4-MIRROR (SAT-9) was F4's exact mirror image: same capped band [0.5%, 1.0%), same V5 signal machinery (H1.build_cell), same T150/S080 exits, first-signal-only, same exclusions — but fade instead of follow, on above-50DMA days instead of below. It loses: 26 trades, **−₹10,013.80**, expectancy **−₹385.15/trade**, breadth 2/25, both halves negative, August slice −₹4,220.36 (the month it was built to thicken), union August −₹2,485.20. Its raw-net margins over both controls (sign-flip follow −₹17,977.51 / 222 tr; lag fade −₹14,225.61 / 113 tr) are **abstention artefacts** — per trade the mirror is the worst of the three (−385.15 vs −80.98 / −125.89); it "beats" the placebos only by trading less. The substantive finding: on above50 days the capped-band signal population loses in BOTH directions and under a stale qualifier — the money in F4 lives in the specific joint state (below-trend × moderate move × follow), not in the band, the machinery, or a symmetric regime logic. Corollaries: (i) the mirror image of a passing joint state is a brand-new system with no inherited credibility (extends Lesson 7); (ii) a placebo comparison read on raw net alone can crown a selective loser — compare expectancy first, totals second. The F4-MIRROR family is CLOSED in every direction/regime combination of the F4 band. *(Evidence: engine cycle SAT-9; stocks_engine_sat9_score.py, stocks_engine_sat9_result.json, stocks_engine_sat9_mirror_trades.csv)*

*Addendum to Lesson 4 (SAT-10, 2026-10-31):* a stop step is a property of the BOOK STATE, not of the component — and the excursion estimate is a compass, not a score. The October peak lab's march to S125 broke April/June at that book; at the post-SAT-8 book (August thickened to +₹1,735.16, April +₹3,671.26, June +₹3,941.51), ONE step S080 → S095 — excursion-diagnosed first (182 stop exits: 4 rescue / 153 deeper-first / 25 neither; rough est +₹6,951.25) — banked **+₹3,898.37 exact** (total → +₹153,263.52; October +₹567.24; ex-top-3 +₹7,504.97, more than the total gain). Two disciplines made it bankable: (i) **Lesson 14 sequencing** — August paid −₹552.73 for the step and stayed green only because SAT-7/SAT-8 had thickened it first; at the post-SAT-6 book (August +₹103.44) the identical step flips August red and fails the gate; (ii) **the estimate's direction was right and its magnitudes were not** — exact gain was 56% of the estimate, and the month allocation was wrong in both directions (October est +₹2,953.74 vs exact +₹567.24; February est +₹3,389.65 vs exact +₹4,204.65; March est −₹2,324.38 vs exact −₹3,582.31). Freeze on the estimate's direction; judge only on the audited rebuild. Corollary: with a rescue rate of 4/182, the step earns from the neither-close population, not from rescues — one re-diagnosed step at a time is the unit of travel on this lever, and each new stop level creates a new population to diagnose before the next step. *(Evidence: engine cycle SAT-10; stocks_engine_sat10_diag.py, stocks_engine_sat10_diag.json, stocks_engine_sat10_score.py, stocks_engine_sat10_result.json)*

*Addendum to Lesson 4 (SAT-11, 2026-10-31):* the stop ladder's length is set by the worst month's excursion mix, not by the total. One cycle after S095 banked, the NEW S095 stop population was re-diagnosed before any further step (155 stop exits, −₹130,188.29): first passage at −1.10% is 1 rescue / 126 deeper / 28 neither full-period (rough est +₹6,686.35 — the total still points up, October est +₹2,610.24), but August's 5 stops are **5/5 deeper-first, 0 rescue, 0 neither** (est −₹1,168.73 against a +₹1,182.43 balance → predicted August +₹13.70). The pre-registered support test failed on the August leg (predicted August ≥ ~₹1,000 required; < ₹500 closes the family), so the S110 step was never frozen or scored — **the F4 stop family is CLOSED at T150/S095 on this window**. Three independent diagnoses now agree (SAT-2 excursions: 0/11 August stops rescued; SAT-10 exact: the S095 step cost August −₹552.73; SAT-11: the S110 estimate wipes August out): August's stops are continuations in every population measured, so each widening transfers roughly ₹550–₹1,170 out of the thinnest month into the thick ones. "The estimate still says up" is not a reason to climb past the constraint month — the lever is exhausted when the binding month's population holds nothing recoverable, even while the aggregate still rises. *(Evidence: engine cycle SAT-11; stocks_engine_sat11_diag.py, stocks_engine_sat11_diag.json)*

*Addendum to Lesson 4 (SAT-12, 2026-10-31):* the target ladder is asymmetric — a target step is paid in small coins and charged in large ones, so its support test can fail on the total even when the stepped month loves it. The T150 → T165 step was excursion-diagnosed on the current winner population BEFORE freezing (133 target exits): 103 reach +1.65% (77%) for +0.15 × entry each (+₹14,303.80 total, avg +₹138.87), but the 27 "neither" winners — those that touched +1.50%, never reached +1.65%, never hit the −0.95% stop — surrender most of the banked target at the square-off close (−₹19,286.20, avg −₹714.30, a ~5:1 per-trade give-back against the reach gain), and the 3 stop-first cost −₹3,310.93. Rough swing **−₹8,293.33** → the step was never frozen or scored, and the **F4 target family is CLOSED at T150** (OC-3's T125 → T150 remains its last paying rung). Two disciplines generalise: (i) on the winner side, count the neither population's give-back as a first-class cost — a reach rate alone (even 77%) says nothing without the per-trade ratio; (ii) October's slice was POSITIVE (+₹1,560.27, predicted headroom ₹2,477.30 — enough to unlock the floor-blocked GLENMARK-SHORT slice) and the step was still correctly refused: headroom is not money, and a gate leg (total up) is not purchasable with another leg's currency. Mirror image of SAT-11, where the total pointed up and the constraint month forbade the climb — in both directions, the binding leg decides. *(Evidence: engine cycle SAT-12; stocks_engine_sat12_diag.py, stocks_engine_sat12_diag.json)*
19. **Reaction information persists past the first follow day — the information axis has a time dimension.** P2F-R2 (SAT-13) enters on R+2 — the second trading day after the reaction — with the incumbent P2F's exact machinery, band (≥2.5%) and exits (T125/S050): 34 trades, **+₹12,912.48**, expectancy **+₹379.78/trade**, win 19/34, breadth 12, against a placebo on identical entries (opposite direction) of −₹6,542.33 / expectancy −₹192.42. It banked on all five saturation-gate legs and earned MORE outside the top-3 (+₹13,575.58 ex-top-3 delta) than the incumbent's previous best step. Two honest caveats are part of the lesson, not footnotes: (i) the component is H1-carried (H1 +₹13,472.08 / **H2 −₹559.60**, the cost concentrated in June/July) — inside a thick book the union gate passes, but December fresh data is the arbiter (Lesson 7); (ii) it does not contradict Lesson 17 — below-band reactions carry no follow-through at ANY lag tested, while at/above the band the signal is still alive a day later; a threshold's complement failing and a signal's persistence are separate facts about the same boundary. Corollary: when an information-axis system works, test its time-shifted self (R+2, and by extension R+3) before inventing new machinery — but each lag is a new system with no inherited credibility, frozen and placebo-controlled on its own (Lesson 18's discipline). *(Evidence: engine cycle SAT-13; stocks_engine_sat13_diag.py, stocks_engine_sat13_score.py, stocks_engine_sat13_result.json)*

*Addendum to Lesson 11 (SAT-13, 2026-10-31):* fourth confirming instance, on a component that did not exist when the exclusions were frozen — ASTRAL and HINDUNILVR's P2F-R2 trades (the R+2 follow of their reactions) net **−₹3,098.80** (4 trades), the same fade-profile behaviour AU-1/JU-1 recorded at R+1. The mechanism-scoped exclusions transferred to the new lag without being re-fitted: the poison is in how these names' reactions behave, not in the entry day.

*Addendum to Lesson 14 (SAT-14, 2026-10-31):* the revisit condition was discharged — by composition, not by a single thickening fix. Of the ₹3,834.85 of August thickening the CH-2 N4 rebuild required, the bulk came from a NEW component (SAT-13's P2F-R2: August +₹2,389.00) and the last ₹449.11 from the smallest slice in the registry (SAT-14: P2F × HINDALCO × LONG, 1 trade, −₹572.50, October-neutral) — August +₹4,143.93 vs ≥ ₹4,020.54 required. Two disciplines carried it: (i) the registry is a queue, not a graveyard (Lesson 12 addendum) — the slice was re-derived from scratch at the five-component book before use (Lesson 16), and the scan's other feasible row (F4 × GLENMARK × SHORT: Aug −₹4,744.78 but full only −₹136.98, 10/20 winners) was refused as an August story rather than rot-everywhere, despite being the larger August number; (ii) "condition met" is a statement about THIS book's arithmetic, not a verdict on the blocked fix — the rebuild's own deltas are stale and SAT-15 must re-measure them before re-applying. A revisit line discharges the *sequencing* obligation; it never inherits the blocked fix's old score. *(Evidence: engine cycle SAT-14; stocks_engine_sat14_diag.py, stocks_engine_sat14_score.py, stocks_engine_sat14_result.json)*

*Addendum to Lesson 16 (SAT-15, 2026-10-31):* third instance, and it refines the lesson's scope — a blocked fix's COMPONENT deltas expire only when intervening changes touch that component's own trades; what expires otherwise is the gate context around them. The CH-2 N4 exit rebuild was re-measured in SAT-15 after 14 intervening cycles and re-measured **identical to the paisa** (component +₹9,483.45; August −₹3,834.85; June −₹654.66) — necessarily so: the union is additive (no shared capital or interaction between components), none of SAT-1..SAT-14 touched an N4 trade, and an exit rebuild's delta is a function of its own component's entries and candles alone. At CH-2 the identical deltas failed the gate because June (+₹172.76) and August (+₹185.69) flipped red; at SAT-15 they banked because the surrounding balances had been thickened (June +₹2,036.67 → +₹1,382.01 after; August +₹4,143.93 → +₹309.08 after). Corollary: a revisit condition should be written as a requirement on the SURROUNDING BOOK's balances (which is what Lesson 14's sequencing actually was), not as doubt about the blocked fix's numbers — when the blocked fix is component-local and its component is untouched, its old score is exact and the only honest question is whether the book can now absorb it. *(Evidence: engine cycle SAT-15; stocks_engine_sat15_score.py, stocks_engine_sat15_result.json)*
20. **Reaction information has a two-day reach — the R-ladder ends at R+2.** P2F-R3 (SAT-16) is P2F-R2's exact machinery one day later — same 39-candidate reaction set, same ≥2.5% band, same T125/S050 exits, same RF-1 + AU-1/JU-1 exclusions: 34 trades, +₹952.10, expectancy **+₹28.00/trade (≈ ₹0 after costs)**, win 12/34, breadth 21 — and its opposite-direction placebo on identical entries earns MORE, overall and per-trade (**+₹4,064.36, expectancy +₹119.54**), decisively in H2 (placebo +₹3,529.56 vs real −₹1,689.87). Whatever a ≥2.5% reaction still knows on R+2 (Lesson 19: expectancy +₹379.78 against a −₹192.42 placebo) it no longer knows on R+3: at that lag the follow direction is noise, and following it also flips July red (−₹1,727.50 slice) and dilutes ex-top-3 in the union. The H2 pattern is consistent across the ladder — R2's raw H2 (−₹2,474.40) also lost to its placebo's H2 (+₹1,455.72); only R2's H1 carries the lagged-follow axis into the book, under December judging (Lesson 7). Corollary: a persistence finding licenses testing the NEXT lag exactly once, as its own frozen, placebo-controlled system (Lesson 19's corollary) — and a placebo that beats the real rule per-trade closes the ladder on the spot. Do not average lags or blend R+2/R+3 into a "smoothed" component to manufacture a pass. **The R-ladder is CLOSED at R+2.** *(Evidence: engine cycle SAT-16; stocks_engine_sat16_diag.py, stocks_engine_sat16_score.py, stocks_engine_sat16_result.json)*

*Addendum to Lesson 6 (SAT-17, 2026-10-31):* leg (d) can pass as exact EQUALITY, and that certifies less than it appears to. SAT-17 removed N4-V3 × TVSMOTOR × LONG (1 tr, −₹3,185.76, July) — TVSMOTOR is the book's #1 earner, so the deletion raised the total and the top-3 sum by the identical amount and ex-top-3 did not move (₹56,308.12 → ₹56,308.12). "Ex-top-3 not worse" was satisfied without any de-concentration occurring: the book's dependence on TVSMOTOR actually deepened (its per-stock total rose to ₹72,025.56). When a banked slice sits on a top-3 name, report the top-3 share alongside leg (d) — a pass by equality on a concentration name is a different animal from a pass by improvement. Same cycle, registry discipline note: the registry was re-derived from scratch at the five-component book (148 slices, 28 qualifying) and its top row was a slice no earlier registry had ever shown — N4's slices exist only since SAT-15 rebuilt that component's exits (the same TVSMOTOR LONG entry was −₹2,006.10 at T125/S050, −₹3,185.76 at T150/S080). A registry is a function of the book state, not a fixed list: re-derive it after every component rebuild, not just on a schedule (extends Lesson 16). *(Evidence: engine cycle SAT-17; stocks_engine_sat17_diag.py, stocks_engine_sat17_score.py, stocks_engine_sat17_result.json)*

*Addendum to Lesson 15 (SAT-18, 2026-10-31):* sixth confirming instance, and the cleanest bank class in the registry: F4 × OIL × SHORT (13 tr, −₹2,712.77, 4 w; LONG half +₹491.75 and kept) was negative in a thin month (June −₹486.88), negative full-period, **and negative in the secured month itself (October −₹465.84)** — so its removal spent no headroom at all, it *minted* ₹465.84 of it (October → ₹52,713.60, headroom ₹2,713.60), while leaving the August razor exactly untouched (the slice has no August trades). Corollary for queue order: among qualifying rows, prefer slices whose secured-month leg is ≤ 0 — they are the only banks that relax the binding floor constraint while they pay. The slice also re-measured identical to the paisa across the SAT-17 intervention (disjoint N4 leg) — Lesson 16 invariance, fourth positive instance. *(Evidence: engine cycle SAT-18; stocks_engine_sat18_diag.py, stocks_engine_sat18_score.py, stocks_engine_sat18_result.json)*

*Addendum to Lesson 11 (SAT-19, 2026-10-31):* fifth confirming instance — VEDL earns in F4's gated flow (raw dump +₹3,062.75 / 28 tr) and in P2F (+₹575.25), yet inside INV-LONG's below-trend pool it is an 18-trade, 4-winner loser (−₹2,424.75; negative in January, February, March, April — a thin month — May and October). The INV-LONG-scoped exclusion banked cleanly (total → ₹184,555.23; the slice's negative October leg minted headroom, per the SAT-18 corollary) while every other component keeps trading the name. Same cycle, Lesson 16's fifth positive invariance instance: the slice re-measured identical to the paisa across the SAT-18 intervention (disjoint F4 leg). *(Evidence: engine cycle SAT-19; stocks_engine_sat19_diag.py, stocks_engine_sat19_score.py, stocks_engine_sat19_result.json)*

*Addendum to Lesson 11 (SAT-20, 2026-10-31):* sixth confirming instance, with a sharpening — HINDZINC loses inside FOUR mechanisms at once (INV-LONG −₹2,131.83 / 9 tr / 1 w; N4-V3 −₹1,043.24; F4 −₹631.12; P2F −₹374.40) and earns in the fifth (P2F-R2 +₹812.50), yet only the INV-LONG slice independently clears the registry's bar (full ≤ −₹500 AND thin-month-negative AND October-feasible). The exclusion banked INV-LONG-scoped (total → ₹186,687.06; June +₹314.77; October and August exactly untouched) while the other components keep their HINDZINC trades: a name being broadly weak does NOT license a book-wide exclusion — each mechanism's slice must qualify on its own numbers, and the ones that don't qualify stay. Same cycle, Lesson 16's sixth positive invariance instance: the slice re-measured identical to the paisa across the SAT-19 intervention (disjoint VEDL leg inside the same component). *(Evidence: engine cycle SAT-20; stocks_engine_sat20_diag.py, stocks_engine_sat20_score.py, stocks_engine_sat20_result.json)*

*Addendum to Lesson 6 (SAT-21, 2026-10-31):* second equality pass, same signature — SAT-21 removed P2F-R2 × TVSMOTOR × LONG (1 tr, −₹1,979.90, July) and leg (d) again passed as exact equality (₹63,577.47 → ₹63,577.47) while TVSMOTOR's share of the book ROSE (38.58% → 39.23%, ₹74,005.46 of ₹188,666.96). Two of the last five banks (SAT-17, SAT-21) are single TVSMOTOR trades in different mechanisms (N4-V3 reaction-day, P2F-R2 R+2-follow) whose LONG legs lost while the name's other legs earn — the registry keeps finding the #1 earner's bad legs precisely because it trades the most. Standing disclosure rule stands: every equality pass on a concentration name is reported with the top-3 share beside it, and December's fresh-data judging — not the in-sample ex-top-3 leg — is the arbiter of whether the concentration is earned. Same cycle: Lesson 16's seventh positive invariance instance (the slice re-measured identical to the paisa across the disjoint SAT-20 INV-LONG intervention).

*Addendum to Lesson 15 (SAT-22, 2026-10-31):* seventh confirming instance — F4 × IRCTC × SHORT (13 tr, −₹1,297.01, 5 w; negative in January, March, April, May, June) banked while its LONG half (+₹497.45 / 9 tr) stays, and IRCTC keeps earning in INV-LONG (+₹411.40), N4-V3 (+₹235.00) and P2F (+₹616.81): the exclusion is F4 × SHORT-scoped only (Lessons 11/15 jointly). Two bookkeeping notes ride with it: (i) at 13 trades this is a materially thicker evidence class than the 1-trade banks (SAT-14/17/21) — the direction-split queue still contains population-sized rows, not only singletons; (ii) the slice's October leg was POSITIVE (+₹275.00), so the bank SPENT ₹275.00 of headroom (₹3,031.65 → ₹2,756.65) — the mirror of the SAT-18 corollary: rows whose secured-month leg is ≤ 0 remain preferable in queue order, but a positive secured-month leg inside headroom is a price, not a block (Lesson 12). Same cycle: Lesson 16's eighth positive invariance instance (the slice re-measured identical to the paisa across the disjoint SAT-21 P2F-R2 intervention). *(Evidence: engine cycle SAT-22; stocks_engine_sat22_diag.py, stocks_engine_sat22_score.py, stocks_engine_sat22_result.json)*

*Addendum to Lesson 11 (SAT-23, 2026-10-31):* seventh confirming instance, with the direction pattern inverted across mechanisms — INDUSTOWER's LONG flow has now failed inside TWO mechanisms independently (F4's LONG half excluded in SAT-2: full −₹361.12; INV-LONG's whole INDUSTOWER population banked here: 12 tr / −₹1,189.01 / 3 w, Apr −₹512.09, Oct −₹228.45) while the same name EARNS on F4's SHORT side (+₹2,287.14 kept flow) and in N4-V3 (+₹564.20). Its P2F (−₹240.20) and P2F-R2 (−₹243.07) slices stay below the bar and stay in the book (SAT-20 sharpening, applied again). A name can be direction-poisoned in several mechanisms at once without being book-poisoned: the unit of exclusion remains (mechanism × stock × direction), and the cross-mechanism LONG pattern is context for the registry queue, never a licence to widen an exclusion past the slice that qualified. Same cycle: Lesson 16's ninth positive invariance instance (the slice re-measured identical to the paisa across the disjoint SAT-22 F4 intervention). *(Evidence: engine cycle SAT-23; stocks_engine_sat23_diag.py, stocks_engine_sat23_score.py, stocks_engine_sat23_result.json)*

*Addendum to Lesson 11 (SAT-24, 2026-10-31):* eighth confirming instance, with the direction pattern split across mechanisms on the same name — OIL's LONG flow fails inside N4-V3 (2 tr / −₹862.04 / 0 w; May −₹456.84, Aug −₹405.20) and its SHORT flow already failed inside F4 (SAT-18: 13 tr / −₹2,712.77), yet the same name's LONG flow EARNS inside F4 (+₹491.75 kept) and INV-LONG (+₹1,208.06), while its P2F (−₹302.00) and P2F-R2 (−₹299.90) slices sit below the bar and stay in the book (SAT-20 sharpening, applied again). A name can be poisoned in opposite directions inside different mechanisms without being book-poisoned in either: the unit of exclusion remains (mechanism × stock × direction), and OIL is now excluded in exactly two such units (F4 × SHORT, N4-V3 × LONG) while trading freely elsewhere. Same cycle: Lesson 16's tenth positive invariance instance (the slice re-measured identical to the paisa across the disjoint SAT-23 INV-LONG intervention). *(Evidence: engine cycle SAT-24; stocks_engine_sat24_diag.py, stocks_engine_sat24_score.py, stocks_engine_sat24_result.json)*

*Addendum to Lesson 11 (SAT-25, 2026-10-31):* ninth confirming instance, with the same name failing on the same direction in a second mechanism — HINDALCO's LONG flow was already excluded inside P2F (SAT-14, its single R+1 trade −₹572.50, the component's only HINDALCO trade) and now fails inside F4's gated flow (9 tr / −₹851.10 / 3 w; Apr −₹215.00, Jun −₹1,137.25; banked F4-scoped, total → ₹192,866.12, June thickened to ₹3,089.03, October and August exactly untouched), while the same name EARNS at the R+2 lag (P2F-R2 +₹1,276.75) and on F4's SHORT side (+₹2,345.84 kept). Its INV-LONG (−₹895.40) and N4-V3 (−₹907.36) slices did not independently clear this cycle's qualifying bar and stay in the book (SAT-20 sharpening, applied again). A name can be direction-poisoned in two mechanisms at once and still be an earner at another lag of the same information axis: the unit of exclusion remains (mechanism × stock × direction), and a second mechanism's matching failure is corroboration for the queue, never a licence to widen. Same cycle: Lesson 16's eleventh positive invariance instance (the slice re-measured identical to the paisa across the disjoint SAT-24 N4-V3 intervention). *(Evidence: engine cycle SAT-25; stocks_engine_sat25_diag.py, stocks_engine_sat25_score.py, stocks_engine_sat25_result.json)*

*Addendum to Lesson 11 (SAT-26, 2026-10-31):* tenth confirming instance — TATASTEEL's LONG flow fails inside F4's gated flow (9 tr / −₹775.38 / 2 w; Apr −₹245.92, Jun −₹263.64, Oct −₹57.00; banked F4-scoped, total → ₹193,641.50, October headroom minted to ₹3,042.10, August exactly untouched) while the same name's SHORT flow inside the SAME mechanism earns (+₹646.21 / 9 tr, kept — Lesson 15's direction split, ninth confirming instance) and its slices in INV-LONG (−₹217.04), N4-V3 (+₹73.08), P2F (−₹145.29) and P2F-R2 (+₹219.38) all sit below the bar and stay in the book (SAT-20 sharpening, applied again). Same cycle: Lesson 16's twelfth positive invariance instance — the entire five-row registry queue (TATASTEEL-LONG, NHPC-SHORT, KALYANKJIL, PFC-SHORT, RECLTD-SHORT) re-measured identical to the paisa across the disjoint SAT-25 F4 intervention. *(Evidence: engine cycle SAT-26; stocks_engine_sat26_diag.py, stocks_engine_sat26_score.py, stocks_engine_sat26_result.json)*

*Addendum to Lesson 11 (SAT-27, 2026-10-31):* eleventh confirming instance, with the below-the-bar discipline applied inside a direction pair — NHPC's SHORT flow fails inside F4's gated flow (13 tr / −₹769.23 / 2 w; Apr −₹156.36, Jul −₹115.24 thin-month legs, Oct −₹40.38; banked F4-scoped, total → ₹194,410.73, no month paying a cost, October headroom minted to ₹3,082.48, August exactly untouched), while the same name's LONG flow inside the SAME mechanism is also negative but far below the bar (12 tr / −₹102.46) and stays in the book, as do its N4-V3 slice (−₹104.80, below the bar) and its earning INV-LONG slice (+₹124.24). Both directions of one name being weakly negative inside one mechanism does NOT license a whole-stock or whole-mechanism exit: the unit of exclusion remains (mechanism × stock × direction), and a slice that does not clear the bar on its own numbers stays, however suggestive its sibling's failure is (SAT-20 sharpening, applied to a direction pair). Same cycle: Lesson 16's thirteenth positive invariance instance — the entire four-row registry queue (NHPC-SHORT, KALYANKJIL, PFC-SHORT, RECLTD-SHORT) re-measured identical to the paisa across the disjoint SAT-26 F4 intervention. *(Evidence: engine cycle SAT-27; stocks_engine_sat27_diag.py, stocks_engine_sat27_score.py, stocks_engine_sat27_result.json)*

*Addendum to Lesson 11 (SAT-28, 2026-10-31):* twelfth confirming instance, on the registry phase's thickest population — KALYANKJIL inside INV-LONG's below-trend pool is a 24-trade, 7-winner loser (−₹764.57; Jan −₹944.37, Feb −₹754.22, Jun −₹35.02 thin-month leg, Oct −₹306.60) and the INV-LONG-scoped exclusion banked cleanly (total → ₹195,175.30; October headroom minted to ₹3,389.08; August exactly untouched), while the same name EARNS in N4-V3 (+₹1,972.87) and F4's gated flow (+₹497.38) and keeps trading there, and its P2F (−₹152.75) and P2F-R2 (−₹201.70) slices sit below the bar and stay in the book (SAT-20 sharpening, applied again). Two bookkeeping notes: (i) INV-LONG is LONG-only, so a stock exclusion inside it has no direction split to take — the (mechanism × stock) unit IS the finest unit that mechanism offers (SAT-19 precedent); (ii) the removal is not costless in shape — it spends March (−₹652.65), April (−₹213.74) and September (−₹409.25) balances that stay strongly green: a slice negative full-period can still hold positive months, and the gate, not the slice's cleanest months, is the judge (Lesson 12). Same cycle: Lesson 16's fourteenth positive invariance instance — the entire three-row registry queue (KALYANKJIL, PFC-SHORT, RECLTD-SHORT) re-measured identical to the paisa across the disjoint SAT-27 F4 intervention. *(Evidence: engine cycle SAT-28; stocks_engine_sat28_diag.py, stocks_engine_sat28_score.py, stocks_engine_sat28_result.json)*

*Addendum to Lesson 11 (SAT-29, 2026-10-31):* thirteenth confirming instance, with the direction split at its widest spread yet — PFC's SHORT flow fails inside F4's gated flow (18 tr / −₹667.69 / 8 w; Apr −₹882.52, Jun −₹435.53, Aug −₹55.00 thin-month legs, Oct +₹67.71) while the same name's LONG flow inside the SAME mechanism earns +₹1,652.90 (12 tr) and stays, and PFC EARNS in three other mechanisms (INV-LONG +₹2,117.27, P2F +₹442.50, P2F-R2 +₹436.25) with its N4-V3 slice (−₹197.58) below the bar and untouched (SAT-20 sharpening, applied again). The banked F4-scoped exclusion also thickened the August razor (₹714.28 → ₹769.28) because the slice carried a small negative August leg, and spent ₹67.71 of October headroom (SAT-22 mirror note: a positive secured-month leg inside headroom is a price, not a block). Same cycle: Lesson 16's fifteenth positive invariance instance — both qualifying registry rows (PFC-SHORT, RECLTD-SHORT) re-measured identical to the paisa across the disjoint SAT-28 INV-LONG intervention. *(Evidence: engine cycle SAT-29; stocks_engine_sat29_diag.py, stocks_engine_sat29_score.py, stocks_engine_sat29_result.json)*

*Addendum to Lesson 15 (SAT-30, 2026-10-31):* the direction-slice queue is finite BOOK-WIDE, and it is now EMPTY. SAT-8 established the queue's limit for one month (August); SAT-30 closes it for the whole registry: after fourteen consecutive registry banks (SAT-17..SAT-30, each re-derived from scratch, each identical-to-the-paisa under Lesson 16 invariance — sixteenth positive instance here: F4 × RECLTD × SHORT, 14 tr / −₹503.97 / 6 w, re-measured unchanged across the disjoint SAT-29 PFC intervention), the post-removal re-derivation at the post-SAT-30 book (134 slices) found **0 qualifying rows** at the standing bar (full-period ≤ −₹500 AND thin-month-negative AND October slice ≤ headroom). The deletion frontier is exhausted — and the correct response is to STOP deleting, not to lower the bar: the largest sub-bar rows (the GLENMARK-SHORT class, full ≈ −₹137 over 20 trades at 10/20 winners) are one-month stories wearing a full-period costume, and slicing thinner from here manufactures fit, not edge (Lesson 5's shape is the bar, and the bar is the lesson). RECLTD itself was a clean final instance of the joint Lessons 11/15 pattern (fourteenth Lesson 11 instance): its SHORT flow rots inside F4 (−₹503.97; Apr −₹336.35, Aug −₹342.58 thin legs) while its LONG flow inside the same mechanism earns +₹949.99 and stays, and its small slices elsewhere (INV-LONG +₹0.24, N4-V3 +₹242.04, P2F +₹228.37) stay untouched. From SAT-31 on, progress can only come from new EARNING material (new Lesson-3 components) — or the run saturates honestly on three consecutive no-beats. *(Evidence: engine cycle SAT-30; stocks_engine_sat30_diag.py, stocks_engine_sat30_diag.json, stocks_engine_sat30_score.py, stocks_engine_sat30_result.json)*

*Addendum to Lesson 17 (SAT-31, 2026-10-31):* the complement test now closes F4's band from ABOVE as well. F4-UPBAND (SAT-31) ran F4's exact joint state — below-50DMA gate, V5 sig machinery, first-signal-only, the book's own T150/S095 exits and symmetric exclusions — on the next band slice, [1.0%, 1.25%) by 10:00: **87 trades, −₹24,036.07, expectancy −₹276.28/trade, 28 winners, breadth 9/25, BOTH halves negative (Jan–May −₹16,589.40 / Jun–Oct −₹7,446.67), negative in 7 of 10 months** — and its sign-flip placebo on identical entries loses LESS per trade (−₹173.21), so the slice fails on expectancy first, not on volume (Lesson 18 discipline). The disclosed M2 prior (the ≥1% region drove the ungated cell's losses) therefore holds INSIDE the joint state too: the below-trend gate rescues the [0.5%, 1.0%) slice specifically, not the territory above it. With SAT-4/Lessons 17/19/20 (lower complement dead at every lag) and SAT-9 (the mirror dead), F4's band is now bounded by failing complements on both sides and in the mirror direction — **[0.5%, 1.0%) is a measured boundary, not a tuned artefact, on every side it has been tested. The F4-UPBAND family is CLOSED; do not widen the band upward.** One honest footnote: the slice's only kindness was August (+₹440.14) — recorded, and correctly worthless against −₹24,036.07 elsewhere: a thin-month gain does not purchase a total loss (Lesson 14's mirror). *(Evidence: engine cycle SAT-31; stocks_engine_sat31_score.py, stocks_engine_sat31_result.json, stocks_engine_sat31_upband_trades.csv)*
21. **P2F's 2.5% floor is validated by its complement — and beating the placebo is necessary, not sufficient.** P2F-LOWBAND (SAT-32) isolated the incremental slice P2F excludes — reaction days with 2.0% ≤ |move| < 2.5%, entered at the R+1 open in the reaction direction at the BOOK's own T125/S050 exits (CH-1 never isolated it: ungated, S065, profile rule inert). The construction was verified against the audited tuning dump on both slices (39/39 at ≥2.5%, 9/9 on the slice itself). Frozen (RF-1 + AU-1/JU-1/SAT-14 exclusions): **8 trades, −₹1,462.45, expectancy −₹182.81/trade, 3 winners, breadth 3, halves split (H1 −₹2,013.99 / H2 +₹551.54)**. Its opposite-direction placebo on identical entries is far worse (−₹3,465.83, expectancy −₹433.23, 0 winners — all 8 placebo trades stop out: these sub-band R+1 days whipsaw through the ±0.5% stop adversely for both directions), so the follow direction DOES carry faint content below the band — and still loses after the ₹40 cost and the stop geometry. Two corollaries: (i) a component must clear ZERO expectancy, not merely its flipped self — a placebo pass with negative expectancy is a rejected system that happens to be the less-bad direction (sharpens Lesson 18: expectancy first, and expectancy is judged against zero as well as against the placebo); (ii) the reaction complex is now bounded on every tested side — N4's ≥1.0% floor (Lesson 17), P2F's ≥2.5% floor (here), the R-ladder's two-day reach (Lesson 20), F4's [0.5%, 1.0%) band on both sides and in mirror (SAT-31, SAT-9) — every boundary of the verified-real material has a failing complement, so further widening in ANY of these directions is re-testing a closed question, not exploring. The slice also closes CH-1's open arithmetic: its −₹182.81/trade expectancy is exactly why the 2.0% band underperformed the 2.5% component in T1/T2. The slice's August kindness (+₹563.37) was correctly worthless against the total (Lesson 14's mirror, applied again). **The P2F-LOWBAND family is CLOSED; do not lower P2F's band.** *(Evidence: engine cycle SAT-32; stocks_engine_sat32_diag.py, stocks_engine_sat32_diag.json, stocks_engine_sat32_score.py, stocks_engine_sat32_result.json)*
22. **The (band × lag) grid is not symmetric — its last cell passes, on thin evidence that December must judge.** R2-LOWBAND (SAT-33) — reaction band [2.0%, 2.5%) entered at R+2, the one cell neither SAT-32 (same band, R+1: −₹182.81/trade) nor Lesson 20 (≥2.5% band, R+3: expectancy ≈ ₹0, placebo ahead) had tested — banked: **7 trades, +₹1,260.78, expectancy +₹180.11**, against a placebo of −₹951.17 / −₹135.88 per trade on identical entries (beaten in total, per-trade, and the component clears zero — the full Lesson 21 test), construction anchor 34/34 against the SAT-13 R2 dump, timing audit 0, overlaps 0. The disclosed priors were negative on BOTH axes and both were wrong for this cell: sub-band content is absent at R+1 yet present at R+2 on this population, while the ≥2.5% signal is present at R+2 and gone at R+3 — band and lag interact; neither axis's verdict transfers across the other. The caveats are part of the lesson, not footnotes: the bank rests on **7 trades**, is **H1-negative (H1 −₹144.70 / H2 +₹1,405.48)** and **October-carried** (October slice +₹1,428.06 exceeds the component's whole net), and it thins August to +₹666.78. It is frozen verbatim exactly as scored — no retest, no R+3 extension, no blending — and December's fresh data is its arbiter (Lesson 7). Corollary: a grid cell is closed by its own controlled run, never by extrapolation from its neighbours; "the priors are negative" is a reason to disclose, not a reason to skip the one frozen test. *(Evidence: engine cycle SAT-33; stocks_engine_sat33_diag.py, stocks_engine_sat33_score.py, stocks_engine_sat33_result.json)*
23. **A positive standalone can still be a concentration purchase — leg (d) is the separation test, and a positive placebo is a disclosure, not a footnote.** R2-MIDBAND (SAT-34) — the [1.5%, 2.0%) reaction slice at R+2 — passed the FULL Lesson 21 standalone test: 6 trades, +₹2,909.18, expectancy **+₹484.86/trade**, against a placebo of +₹1,054.91 / +₹175.82 per trade on identical entries (beaten in total and per-trade, and the component clears zero). It was still correctly REJECTED, on gate leg (d) alone: the union's ex-top-3 FELL ₹72,518.25 → ₹72,034.93, because the component's entire net is one TVSMOTOR SHORT target exit (+₹4,247.50, 2026-05-18) on a top-3 name while OBEROIRLTY (also top-3) contributed −₹855.00 — ex-the-carrier-trade, the component is **−₹1,338.32**. Corollaries: (i) expectancy and the placebo test judge the component; the ex-top-3 leg judges what the component DOES to the book — a one-trade gain on the #1 earner is a concentration purchase wearing a component's clothes (sharpens Lesson 6); (ii) a POSITIVE placebo (+₹175.82/trade) means the entry days themselves are volatile in both directions — the follow direction's margin over the flip was real on these 6 trades and one trade deep, which is exactly the evidence class leg (d) exists to refuse; (iii) the grid's R+2 row is now bounded below by its own controlled run, as the R+1 row was (Lesson 21): the living band at R+2 starts at [2.0%, 2.5%); a descent to [1.0%, 1.5%) at R+2 is not licensed by this cell's failure (Lesson 22 forbids closing by extrapolation) — but any future proposal carries this cell's disclosed evidence (one-trade carriage, positive placebo, H2-negative) as its prior. **The R2-MIDBAND family is CLOSED.** *(Evidence: engine cycle SAT-34; stocks_engine_sat34_diag.py, stocks_engine_sat34_diag.json, stocks_engine_sat34_score.py, stocks_engine_sat34_result.json)*
24. **At [1.5%, 2.0%) the R+1 follow direction is worse than its own flip — the band carries no directional content at the first lag, and the (band × lag) grid is now fully mapped.** P2F-MIDBAND (SAT-35) is SAT-34's exact band one lag earlier — same 7-candidate reaction set, same T125/S050 exits, same RF-1 + P2F exclusions, machinery verified per-trade against the tuning dump on both adjacent slices at this lag (≥2.5% 39/39, [2.0%, 2.5%) 9/9): frozen 6 trades, **−₹2,773.74, expectancy −₹462.29/trade, 1 winner, breadth 1, both halves negative** — and its opposite-direction placebo on identical entries loses LESS (**−₹2,275.45, expectancy −₹379.24**), so the component fails every clause of the Lesson 21 test (does not clear zero, does not beat the placebo in total or per-trade). The mechanism is visible in the trades: 3 of the 6 entry days (TVSMOTOR, ITC, OBEROIRLTY) stop out at the *identical* net in both directions — the R+1 day after a sub-2% reaction blasts through the ±0.5% stop adversely whichever way it is entered; the population is stop-geometry whipsaw, not information (the SAT-32 signature, one band lower and direction-free rather than merely faint). Ex-carrier −₹3,282.74: the single winner cushions the loss, it does not carry a gain — the mirror image of Lesson 23's carriage. Corollaries: (i) the [1.5%, 2.0%) band is now closed at BOTH lags — at R+2 as a concentration purchase (Lesson 23), at R+1 as content-free — and the two rejections are different facts: R+2's positive standalone rested on one trade's entry-day fortune (the same TVSMOTOR event: +₹4,247.50 target at R+2, −₹1,767.80 stop at R+1), which is precisely why a cell's verdict never transfers across lags in either direction (Lesson 22, confirmed from the negative side); (ii) the R+1 row is complete — ≥2.5% real, [2.0%, 2.5%) faint and negative, [1.5%, 2.0%) direction-free — and with the R+2 row and the dead R+3 (Lesson 20), every cell of the reaction grid has now had its own controlled run; no cell remains that a descent or a lag-shift could honestly propose. **The P2F-MIDBAND family is CLOSED; the reaction (band × lag) grid is CLOSED outside its living cells.** *(Evidence: engine cycle SAT-35; stocks_engine_sat35_diag.py, stocks_engine_sat35_diag.json, stocks_engine_sat35_score.py, stocks_engine_sat35_result.json)*
25. **The quality bar is not lowered at the finish line — a gate pass manufactured from one month's shape is a no-beat, and refusing it is what saturation means.** F4 × GLENMARK × SHORT was judged formally in SAT-36 after three procedural refusals (floor-blocked SAT-8, "August story" SAT-14, registry bottom SAT-17): re-derived at the final book — **20 trades, 10 winners, net −₹136.98, expectancy −₹6.85/trade** — its removal PASSES the arithmetic saturation gate on all five legs (union +₹197,744.72; August ₹666.78 → ₹5,411.56; October ₹53,209.88; ex-top-3 +₹136.98), and every leg's pass is the same ₹136.98. The month table exposes the manufacture: August +₹4,744.78 and April +₹1,926.32 bought with May −₹3,519.65 and September −₹4,364.31. The slice's net excluding August is **+₹4,607.80** (outside one month it earns), its ex-carrier is **+₹2,249.71** (remove its single worst trade, 2026-08-31 −₹2,386.69, and the "rot" is a profit), and its halves nearly cancel (H1 +₹200.94 / H2 −₹337.92) — negative in 6 of 9 traded months, yet none of it is rot-everywhere: it is a zero-expectancy, half-winning population with one bad month. That is the exact profile Lesson 5's bar (full-period ≤ −₹500) exists to refuse, and the refusal is recorded as the run's third consecutive no-beat: **the plateau +₹197,607.74 is the ceiling of what the frozen standards certify, and the declined ₹136.98 + August thickening is the disclosed price of the standards.** Corollaries: (i) breadth of small negatives is not rot when expectancy ≈ ₹0 and two months carry large positives — the bar reads the full-period net, not the count of red months; (ii) a standing item deserves one formal judgement on its merits rather than permanent procedural deferral — but the judgement, once made under both standards, CLOSES the question on this window: GLENMARK-SHORT may be revisited only on fresh (December+) data, never re-argued in-sample. *(Evidence: engine cycle SAT-36; stocks_engine_sat36_diag.py, stocks_engine_sat36_diag.json, stocks_engine_sat36_score.py, stocks_engine_sat36_result.json)*

26. **A book fitted and judged on the same window is a photograph of that window's regime, not a system.** The v1 book was built and certified entirely inside Jan–Oct 2026, a year in which its core gate (below-50DMA) was nearly always open; scored on 2025 — a trending year where below-50DMA days were only 95 of 249, with May, June and November having zero — its flagship collapsed: F4 went from **+₹101,757.43 in-sample (389 trades) to −₹5,093.75 out-of-sample (261 trades)**, and the two runnable components together made only +₹2,548.77 over twelve months (+₹212/month) versus +₹152,929.90 over the ten 2026 months. The arithmetic and audits were exact and leak-free this time — the failure is at book level, not in the accounting: the book is a curve-fit to a single regime, and the user's verdict on it ("then system is wrong", 2026-10-31 14:58 IST) is accepted in substance. INV-LONG is the exception that proves the rule — the only component positive out-of-sample (+₹7,642.52, 245 trades), so it is the one thread that already behaves like a system. **From v2 onward, no fix, component, or exclusion is banked unless it is scored on BOTH windows in the same run and passes the cross-year gate (combined total rises AND neither year's total falls AND neither year is negative at book level), with the arithmetic stated in the log each cycle.** A component may be year-specialised only if the other components keep that year positive. Any result quoted from a single window is a photograph, not a system, and must be labelled as such. *(Evidence: stocks_engine_2025_validation.md — 2025 full-window score, control-A exact reproduction of the 2026 book, user verdict 2026-10-31 14:58 IST)*

27. **A (name × direction) leak can be mechanism-specific, not name-wide — and a slice refused as noise on one window can be rot on two.** GLENMARK × SHORT lost in BOTH years inside the same-day follow mechanisms — F4 (follow by 10:00): −₹3,010.96 in 2025 (7 tr) and −₹136.98 in 2026 (20 tr); N4-V3 (follow by 09:30): −₹2,731.28 in 2025 (2 tr) and −₹494.21 in 2026 (3 tr) — while the identical name and direction EARNED inside the next-day event-follow family in 2026 (P2F +₹5,112.24, P2F-R2 +₹1,316.80). SAT-36's refusal of the F4 slice was correct on the evidence that existed (2026 alone: −₹136.98, ≈ ₹0 expectancy, below the quality bar); the cross-year record did not lower the bar, it changed the evidence — the same direction bleeding −₹5,742.24 across two independent follow components in an unfitted year is a different fact from one window's −₹136.98. Banked under the v2 gate as V2C1 (combined +₹197,630.80 → +₹204,004.23; 2025 +₹23.06 → +₹5,765.30; 2026 +₹197,607.74 → +₹198,238.93). Corollaries: (i) scope a direction exclusion to the mechanism that bleeds — a name-wide GLENMARK SHORT ban would have destroyed +₹6,429.04 of real 2026 money and failed the gate; (ii) a slice containing a large winner (the N4 March-2026 +₹3,084.50 trade) can still be rot in aggregate across two years — the gate reads year totals, and the heterogeneity is disclosed, not hidden; (iii) closures written under one method ("revisitable only on fresh data") are honoured by producing the fresh evidence, not by re-arguing the old window. *(Evidence: stocks_engine_v2_build.py — all controls pass; stocks_engine_v2_cycle1_score.py / v2_out/v2_cycle1_result.json; freeze in stocks_engine_frozen.md, V2-CYCLE-1, with the SAT-36 disclosure stated before scoring)*
28. **A floor validated from below can have living material above it — and a band preference does not transfer across universes.** P2F's 2.5% floor was validated by its complement (Lesson 21: [2.0%, 2.5%) loses at R+1 in 2026). The Cycle 3 challenger tested the band from ABOVE, blind: P2F rebuilt at ≥3.0% on the build machinery, both years, full controls in-pass. The dropped [2.5%, 3.0%) slice **earns in both years** (2025: 5 tr / +₹2,823.67, expectancy +₹564.73; 2026: 5 tr / +₹1,479.98, expectancy +₹296.00), so the challenger book falls in both years (combined +₹207,189.23 → +₹202,885.58) and is rejected on gate legs (a) and (b). Two corollaries: (i) a complement test closes only the side it tests — Lesson 21 bounded P2F's band from below, Lesson 17 bounded N4's floor the same way, and neither said anything about the territory above; a threshold earns the title "peak" only when the slice above it fails its own controlled run (the SAT-31 F4-UPBAND pattern, where the above-slice DID fail — the two outcomes are different facts, not a contradiction); (ii) T2's pooled-50 preference for the 3.0% band (+₹31,719.61, expectancy +₹480.60) does not transfer to the home 25, where the incumbent 2.5% component's expectancy is higher and its [2.5, 3.0) slice is alive in both years — a band's verdict is a property of (band × universe), and pooled evidence is a prior, never a verdict, for the home book. **The P2F band question is CLOSED cross-year at ≥2.5%: do not raise it, do not lower it (Lesson 21).** *(Evidence: engine v2 cycle 3; stocks_engine_v2_cycle3_score.py, v2_out/v2_cycle3_result.json)*
29. **The information axis is (event-class × lag)-specific: news reactions do not persist to R+1 the way results reactions do.** CH-V2-2 (v2 Cycle 6) followed NEWS-event reactions (large orders, FDA approvals, block deals, management changes, sector policy, corporate actions) at R+1 with P2F's exact machinery — living band ≥2.5%, T125/S050 exits, RF-1, no exclusions, full build controls re-run in-pass, reaction returns independently recomputed. The two years DISAGREE on the direction of the effect: 2025's two in-band follows both won (+₹1,949.25, placebo −₹891.70), while 2026's four lost (−₹2,089.31, expectancy −₹522.33) with the flip placebo earning +₹5,475.58 (expectancy +₹1,368.89) — GLENMARK lost in both directions (−₹1,061.10 SHORT, −₹1,207.30 LONG). Component expectancy −₹23.34 vs placebo +₹763.98 fails every clause of the Lesson 21 test, and the gate fails with it. The substantive reading: a results reaction is a repricing that continues into the next session (P2F, and at R+2 in 2026's regime, P2F-R2); a single-item news reaction is impounded on its own day — the mechanism that monetises news is the SAME-DAY one (N4-V3's 09:30 trigger), and by R+1 the residual direction is regime noise (follow-tilted in 2025, fade-tilted in 2026, 6 trades — thin, disclosed; the placebo margin is the decisive fact, not the count). Corollaries: (i) P2F's success licenses results-follows only — an event class is part of a mechanism's identity, exactly as stock and direction are (extends Lesson 11's scoping to the information axis); (ii) a challenger aimed at the weak year can pass in the weak year and still be correctly rejected — the gate's neither-year-falls leg is what stops a 2025-shaped patch from being bought with 2026 money (the cross-year form of Lesson 26). **The P2F-NEWS family is CLOSED; do not follow news reactions at R+1, and do not fade them either — the fade is the same 6 trades read backwards.** *(Evidence: engine v2 cycle 6; stocks_engine_v2_cycle6_score.py, v2_out/v2_cycle6_result.json)*
30. **A threshold slice can be regime-flipped across years — a floor is only closed when both its complements have failed on the judging windows.** CH-V2-3 (v2 Cycle 9) raised N4-V3's trigger floor from ≥1.0% to ≥1.5%, blind, with the parameterised machinery anchored per-trade at 1.0 in the same pass. The dropped [1.0%, 1.5%) slice **loses in 2025 (13 tr / −₹1,860.69) and earns in 2026 (4 tr / +₹3,135.29)** — the identical population is the weak year's rot and the strong year's income. The challenger therefore fails the cross-year gate on legs (a) and (b), and would fail a combined-only gate too (net −₹1,274.60). Corollaries: (i) Lesson 17's validation of the ≥1.0% floor was a 2026-window fact about the slice BELOW; the slice ABOVE the incumbent population's lower edge is a different population with its own verdict — a threshold earns "closed" only when both complements have had their own controlled run on the judging windows, as F4's band did (SAT-4/SAT-31) and P2F's did (Lesson 21 / Lesson 28); N4's floor is now closed at both ends, cross-year. (ii) A component whose worse year is ≈ ₹0 (N4-V3 2025: −₹502.80) invites a one-shot population fix, and the population fix is exactly where regime flips hide — the registry's (mechanism × stock × direction) slices, each negative in both years on its own numbers, remain the honest repair route for such a component, because a slice that loses in both regimes is rot, while a band that flips with the regime is a photograph waiting to happen (Lesson 26, applied at slice level). **The N4 trigger-floor family is CLOSED cross-year at ≥1.0%; do not raise or lower it.** *(Evidence: engine v2 cycle 9; stocks_engine_v2_cycle9_score.py, v2_out/v2_cycle9_result.json)*
31. **An excursion estimate can point the wrong way entirely — the rebuild is the only score, and a family closed on an estimate must be re-closable on an exact score.** SAT-11 refused F4's S095 → S110 stop step on a diagnosis-only support test (rough swing +₹6,686.35 on 2026, refused because its August leg failed v1's gate). CH-V2-4 (v2 Cycle 12) scored the step exactly, on both years, with every anchor in-pass (entry sets identical, audits 0): the step **loses in both years** — 2026 −₹1,259.09 (the estimate's sign was wrong, not just its magnitude) and 2025 −₹287.11, flipping F4's 2025 component negative (+₹91.14 → −₹195.97). Corollaries: (i) Lesson 4's "estimates are compasses" understates the risk — a first-passage estimate can be sign-wrong on the very window it was computed from, because it prices stop-outs at the passage level and ignores what the widened stop does to trades that would have exited at the target or the square-off; only the full replay nets those. (ii) SAT-11's refusal was correct in outcome and is now correct in substance: **the F4 stop family is CLOSED CROSS-YEAR at T150/S095**, and with the target family closed in v1 (SAT-12), F4's exits are settled on both windows — no further exit challenger on F4 is licensed. (iii) A closure recorded as "diagnosis only" should be labelled as such wherever it is cited (the v2 freeze did), so a later method can re-test it exactly without pretending the question was already scored. *(Evidence: engine v2 cycle 12; stocks_engine_v2_cycle12_score.py, v2_out/v2_cycle12_result.json; SAT-11 diagnosis stocks_engine_sat11_diag.json)*
32. **An information-class distinction can be a lag fact without being a quality fact: at its own lag, N4's news-day population is regime-flipped and nets to zero.** CH-V2-5 (v2 Cycle 15) split N4-V3's trades by event-day class — results reaction days vs news-only days (tagged by the machinery, anchored per-trade in both years) — and tested dropping the news class. The news-only slice **loses in 2025 (6 tr / −₹2,625.17) and earns in 2026 (3 tr / +₹2,936.18)**, net −₹311.01 over 9 trades: the challenger fails the gate on legs (a) and (b). Lesson 29 showed news reactions do not persist to R+1 while results reactions do — a fact about PERSISTENCE. It does not follow that news days are bad trades at the same-day lag: at 09:35 entry both classes are traded on the morning's own move, and there the class carries no cross-year sign. Corollaries: (i) every axis of a mechanism — event class included — has its verdict per (axis × lag × window-set), and a distinction proven on one lag licenses nothing on another (the Lesson 22 grid discipline, generalised); (ii) the recurring cross-year shape of this whole run is regime flip at population level (trigger bands, event classes, exit steps) versus stability at (mechanism × stock × direction) slice level — populations average over regimes, slices name specific recurring behaviour; that is why the registry, not the population challenger, has done all of v2's banking outside Cycle 1. **The N4 event-class family is CLOSED at the same-day lag; the results+news union stands.** *(Evidence: engine v2 cycle 15; stocks_engine_v2_cycle15_score.py, v2_out/v2_cycle15_result.json)*
33. **Exit medicine is population-specific — now proven on exact cross-year rebuilds, not estimates: the pair that pays on same-day reaction entries fails on next-day entries.** CH-V2-6 (v2 Cycle 18) rebuilt P2F at T150/S080 — the pair the SAT-15 rebuild proved on N4-V3's same-day reaction population (+₹9,483.45, 2026) — with every anchor in-pass (copy at the incumbent pair reproduces the component per-trade in both years; entry sets identical). On P2F's R+1 population the swap **loses in 2025 (−₹4,132.23: +₹14,365.77 → +₹10,233.54) and gains only +₹301.50 in 2026** — combined −₹3,830.73, rejected on gate legs (a) and (b). The two reaction populations hold different excursion shapes: same-day entries (09:35, off a live morning move) keep running often enough to pay for a wider stop and target; next-day entries (09:15 open, off a completed repricing) pay fast or not at all, so the wider stop is a pure bleed in the trending year. This is Lesson 4's third exact confirmation, each on a different population (INV-LONG's grid peaks at its tightest pair T125/S050; F4's gated flow paid for exactly one widening step and no more, Lesson 31; N4 vs P2F here) — there is no book-level exit prescription and there is no cross-population transfer: an exit pair is part of a mechanism's identity, like its band and its lag. **P2F's exits are CLOSED cross-year at T125/S050; do not re-propose exit swaps between the reaction components.** *(Evidence: engine v2 cycle 18; stocks_engine_v2_cycle18_score.py, v2_out/v2_cycle18_result.json)*
34. **Second signals are the spent remainder of the move — first-signal-only is a cross-year fact, and a discarded population's measurement does not transfer between code lineages.** CH-V2-7 (v2 Cycle 20) restored F4's round-2 legs, isolated black-box as the legs the frozen filter rejects solely for their leg field (46 of 66 raw round-2 legs in 2026; the rest are blocked by other rules too and stay out). Under the current law the restored population **loses in both years** (2025 −₹3,306.97; 2026 40 tr / −₹8,919.19, 17 winners) and the challenger fails the gate on legs (a) and (b) by ₹12,226.16 combined. SAT-6's bank of first-signal-only is therefore confirmed in direction on both windows — but its recorded magnitude (−₹11.83 for the dropped set) was lineage-local: the peak-lab dump lineage and the validation collect2 lineage agree on the kept population to the paisa (Controls B1/B2) yet generate DIFFERENT round-2 populations, so the discarded set's old net was never a property of this book. Corollaries: (i) a signal population is defined by its generation order — the second signal on a stock-day trades a move the first signal already harvested, and it is worse in a trending year and a below-trend year alike; re-entry generosity is not free activity, it is adverse selection (the user's no-trade-cap rule for stocks stands unharmed — this is a finding about THIS mechanism's second signals, not a trade-count restriction); (ii) when two audited lineages agree on what a book KEEPS, their agreement certifies nothing about what each DISCARDS — measure a discarded population in the lineage that would trade it, or do not quote its number. **The F4 round-2 family is CLOSED cross-year; F4 stays first-signal-only.** *(Evidence: engine v2 cycle 20; stocks_engine_v2_cycle20_score.py, v2_out/v2_cycle20_result.json)*
*Addendum to Lesson 33 (v2 Cycle 21, 2026-10-31):* the third population has now been scored, and it returns the third distinct shape. P2F-R2 (R+2 entries) at T150/S080 **improves 2025 by +₹703.28 (−₹5,682.76 → −₹4,979.48) and costs 2026 ₹3,921.20 (+₹15,149.33 → +₹11,228.13)** — rejected on gate legs (a) and (b), combined −₹3,217.92. The exit-pair map is now complete on exact cross-year rebuilds: same-day entries want the wider pair (SAT-15, banked), R+1 entries want the incumbent pair in both years (Cycle 18), R+2 entries want the wider pair in the trending year and the incumbent pair in the below-trend year — a regime split, so no single law serves both windows and the gate keeps the incumbent. **P2F-R2's exits are CLOSED cross-year at T125/S050.** With this, every component's exits have been tested on their own population under the cross-year gate; the exit axis of the whole book is settled, and no further exit challenger is licensed on any component. *(Evidence: engine v2 cycle 21; stocks_engine_v2_cycle21_score.py, v2_out/v2_cycle21_result.json)*

35. **Mirroring is mechanism-specific, not a law — the INV pool mirrors, the F4 structure did not (Cycle 22, CH-V2-9).** Lesson 18's "joint states do not mirror" came from F4, a directional price-structure system: its below-trend edge was the structure itself, so the above-trend twin had nothing to stand on. INV's machinery is a stock-selection pool (chain candidates filtered by round, earliness and ADR) whose below50 gate was inherited, not earned — flipped to above-trend days it earns in BOTH years (exp +₹30.65 / +₹93.03 per trade, gate passed, placebo beaten on the combined per-trade standard). Refinement of Lesson 18, not a repeal: before assuming a regime gate is load-bearing, test the mirror — but read the placebo per year as well as combined: above-trend SHORTs were the better 2025 trade (exp +₹74.22) and a 2026 disaster (exp −₹155.14); the bankable side is the one positive in both years, not the one with the biggest single-year number. The cross-year gate, not the mirror metaphor, remains the arbiter.

*Addendum to Lesson 35 (v3 Cycle 2, 2026-10-31):* the mirror discipline extends to filter axes inside the mechanism — a sibling population's verdict does not transfer across gates. INV-R3 (round ≥ 3, below gate) banked in v3 C1 (combined exp +₹222.17, placebo −₹194.52/trade, worst-quarter month Mar 2025 lifted +₹4,557.68); its exact mirror INV-ABOVE-R3 (round ≥ 3, above gate) earned in the aggregate too (32 tr / +₹5,097.01, exp +₹159.28) and was still correctly REJECTED: its 2026 leg is negative (−₹61.66), its flip placebo beats it per-trade inside 2025 (+₹236.59 vs +₹184.24 — the above-trend SHORT population is again the better 2025 trade), and under the maximin criterion it bills the worst month (Oct 2025 slice −₹466.38). The round axis is therefore alive on the below gate and unproven-to-negative on the above gate — each (axis × gate) cell is its own system with its own verdict, the Lesson 22 grid discipline inside a single mechanism. *(Evidence: engine v3 cycle 2; stocks_engine_v3_cycle2_score.py, v3_out/v3_cycle2_result.json)*

36. **A filter's complement can pass every combined standard and still be regime rent — the gate's per-year leg is the operative discipline (Cycle 25, CH-V2-10).** INV-LATE (the INV machinery with the p2 earliness leg flipped to entry ≥ 10:30, below-trend gate) scored combined +₹4,729.16 with expectancy +₹26.42/trade and its flip placebo beaten per-trade (−₹91.02) — every combined test green — yet it was correctly REJECTED: 2026 contributed +₹66.27/trade while 2025 paid −₹16.68/trade, so leg (b) (neither year falls) refused it. The earliness filter is load-bearing, and asymmetrically so: late chain entries are the spent part of the day in the choppy year and harmless-to-good in the trending year. Generalises Lesson 26 from books to components: judge a population per year before judging it combined; a combined pass with a weak-year bill is a photograph-improver at component scale. *(Evidence: engine v2 cycle 25; stocks_engine_v2_cycle25_score.py, v2_out/v2_cycle25_result.json)*

*Addendum to Lesson 36 (Cycle 26, CH-V2-11):* the above-trend gate's late complement fails with the **opposite** year sign to the below-trend gate's (2025 +₹12.23/trade, 2026 −₹69.58/trade; combined expectancy −₹10.08) — so "late entries" are not a population with a stable sign on either gate, and the difference between the gates is which year does the paying. The earliness leg is therefore load-bearing for the INV family as a whole, and the late-entry axis is **CLOSED cross-year on both gates**. A filter whose complement flips sign by gate and by year is not hiding a sleeve; it is marking the boundary of the machinery's information, which lives in the first part of the day. *(Evidence: engine v2 cycle 26; stocks_engine_v2_cycle26_score.py, v2_out/v2_cycle26_result.json)*

37. **Follow-through belongs to scheduled information, not to information shocks in general (Cycle 27, CH-V2-12).** P2F's machinery transplanted verbatim onto the calendars' news classes (same ≥2.5% band, same R+1 entry, same exits) produced 6 trades for −₹140.06 combined, and in 2026 the flip placebo earned +₹1,368.89/trade against the follower's −₹522.33: unscheduled news reactions faded where results reactions continued. The mechanism's edge is therefore not "a big move happened" but "a big move happened on scheduled, interpretable news whose repricing takes days" — the event class is part of the mechanism, and a class transplant is a new hypothesis, not a scale-up of a proven one. Thin evidence disclosed (6 band candidates across two years, one reaction day lost to the results dedup): the rejection leans on the placebo inversion in the strong year, and fresh-window data could reopen the question — but on this data the follow family's universe is results-only, closed. *(Evidence: engine v2 cycle 27; stocks_engine_v2_cycle27_score.py, v2_out/v2_cycle27_result.json)*

38. **The average hid the weak months; the user's standard is a floor under every month (v3 charter, user order 2026-10-31 20:55 IST).** Two engines optimised totals and averages and both times the headline concealed the distribution: v1's ₹19,761/month was one regime's photograph (Lesson 26), and v2's combined ₹10,867/month average coexisted with six red months in 2025 (worst −₹5,149.95) and a 2025 ex-top-3 of −₹12,272.78. The user's correction — "at least ten thousand should be the minimum" — is adopted as the v3 objective in his own form: **lexicographic maximin over the 22-month vector** (raise the worst month first, then the next), under the v2 hard constraints (neither year falls, no year negative, every regime cell positive, combined never falls). Corollaries: (i) a fix that fattens a strong month while the worst month stands still is NOT progress under this objective, however much it raises the total — it will be reported as a no-beat; (ii) the weak months are quiet months (Jun 2025: 7 trades), so maximin progress is mostly an ACTIVITY problem in low-opportunity regimes, not an exit or slice problem — the deletion registry is exhausted (v2 C19) and the exit axes are settled (Lessons 31/33/34), so the material must be new information breadth or proven-earner variants that would actually have traded in those months; (iii) the floor is judged per month on the same two windows that judge everything else — a worst month lifted by a change that costs another month below it is a rotation, not a lift, and the lexicographic test refuses it by construction. *(Evidence: user orders 2026-10-31 15:17 / 15:30 / 20:50 / 20:55 IST; v2 termination entry in stocks_engine_log.md — month vector, red months, band metrics; v3 charter in stocks_RECURSIVE_ENGINE.md)*
39. **A calendar that cannot be built uniformly must not be built partially — missing days impersonate no-event days, and the impersonation is worst exactly where the measurement matters.** The v3 desert phase ordered a systematic bulk/block-deal calendar (uniform across both judging windows, frozen before scoring). Every systematic source failed on reachability or uniformity from this environment: the NSE historical-report API's host is unreachable, the BSE API is bot-walled, Wayback's daily-file snapshots are near-absent in-window, the one full-history republisher (Ansaar, 89k rows) exposes only its latest session readably, and the one public dataset file is bulk-only and truncated mid-window (Mar 2026). A truncated calendar was available and was REFUSED: scored on it, a challenger would be a different system than its definition (its missing months are unknown, not zero), and the desert months the calendar existed to serve are precisely the months where coverage gaps would decide verdicts. This is Lesson 26 at the data layer — a measurement artefact (coverage) impersonating a system property (no events) — and Lesson 1's timing discipline generalised: an input is either the thing it claims to be, on every day of both windows, or it is not an input. Corollary: when a data build fails on sourcing, the failure is recorded with the same completeness as a scoring (sources tested, failure mode of each, the exact endpoint/field map that would complete the build) so the build is resumable in one step when access changes — a sourcing verdict is a result, not an omission. *(Evidence: v3 desert phase, 2026-10-31; stocks_engine_log.md desert-phase entry; NseIndiaApi docs + installed `.venv_nse` client; GitHub shahzebkhan-os/btst file listing)*
35-addendum-2 (v3 C18, desert phase). **The INV-ABOVE round split is measured: round 2 is the component (54 tr, +₹13,977.13 combined, positive both years); round 1 is expectancy-dead (133 tr, −₹2,346.67 combined — +₹12/trade in 2025, −₹129/trade in 2026) and is the entire desert-month bleed (Jul 2025's −₹2,473.45 = 3 round-1 trades; Jun 2025's month = 6 round-1 + 1 round-2). The amputation is nevertheless UNBANKABLE: round 1 is positive in 2025 (+₹1,260.61), so deleting it violates the neither-year-falls hard constraint even though it would lexicographically beat the month vector. Recorded as a closed axis so it is not re-proposed: a maximin engine with a cross-year floor will sometimes be unable to remove a leg it can prove is dead in one year and zero in the other — that is the constitution working as designed, not an oversight; the repair, if one exists, must come from additive material that lifts the desert months without touching the leg.** *(Evidence: v3_out/v3_cycle18_diag.json — population rebuilt with C2's exact pick, matched row-by-row to the post-C16 book; the 19 population-only rows are the C24 FLAT stand-aside set.)*
40. **Engine v3 saturated with its objective honestly unmet — and the saturation itself is the measurement.** v3 (maximin) lifted the cross-year book +₹20,792.92 over 19 cycles and flipped two red months green, then hit three consecutive no-beats with every named road closed by evidence: the deletion registry exhausted, the (band × lag) grid completed (reaction-following earns ONLY at ≥2.5% × R+1; three lower cells are each negative on their own controlled runs), the round axis adjudicated on both gates, and the one genuinely new data class (bulk/block deals) unbuildable uniformly from this environment. The four surviving red months are all 2025 UP-regime months whose anatomy is identical — INV-ABOVE round-1 bleed plus an information desert — and the one surgical fix for that anatomy (amputate round 1) is barred by the cross-year floor because the leg is barely positive in 2025. The lesson for any successor engine: when the binding constraint becomes the constitution itself (neither-year-falls vs worst-month repair), more cycles on the same families cannot help — the frontier moves only with new DATA (an event class that actually occurs in quiet UP-regime months) or a new mechanism, and the correct terminal act is to say exactly that, with the unmet objective (worst month ≥ ₹0, then ₹10,000) stated as unmet rather than quietly re-scoped. *(Evidence: v3 cycles 16–19 + termination entry in stocks_engine_log.md; v3_out/v3_cycle1{6,7,9}_result.json; v3_out/v3_cycle18_diag.json; Lesson 39 sourcing record.)*
41. **A component-level gate pass does not transplant into the book — the population a filter acts on is a function of book state.** The N4-V3 ≥3% move cap passed the full gate on the standalone 2026 file (book basis +₹19,977.90 → +₹20,940.28), yet at whole-book level (FLOOR-1) it was rejected: the book's own prior deletions (v2/v3 law) had already harvested the standalone file's losing ≥3% names, so the surviving in-book ≥3% bucket had flipped sign in the fitted year (2026 +₹5,678.23) while carrying the diagnosed sign in the untested year (2025 −₹1,838.73). Any fix scored on a component file must be re-gated inside the assembled book, in every year, before it is believed — the standalone universe and the in-book universe are different populations wearing the same name (extends Lesson 16 from deltas to filter populations). *(Evidence: FLOOR session cycle 1; stocks_engine_floor_c1.py, stocks_engine_floor_c1_result.json)*
42. **An entry-quality filter can need the direction split as much as a deletion does.** The symmetric ≥3% cap failed (Lesson 41), but its LONG half was negative in both years (2025 −₹940.81 / 10 tr; 2026 −₹1,790.26 / 4 tr) while its SHORT half carried 2026 (+₹7,468.49, 9/10 winners): over-extension after a reaction is a chasing phenomenon on the LONG side of this book, and shorting an over-extended fall kept paying in 2026. The one-sided cap (skip signed move ≥ +3.0%) banked on all nine gate legs and repaired 2025's ex-top-3 from +₹30.76 to +₹5,131.62 (FLOOR-2). When a filter fails symmetric, split it by direction before abandoning it — the same discipline as Lesson 15, applied to a gate instead of a deletion. *(Evidence: FLOOR session cycle 2; stocks_engine_floor_c2.py, stocks_engine_floor_c2_result.json)*
43. **"Over-extension" is not one phenomenon — the measurement window is the mechanism.** N4's intraday over-extension (move by 09:30 ≥ 3%) hurts, on the LONG side (Lessons 41–42). The P2F family's full-day reaction size pays MORE as it grows: expectancy by |reaction_ret| bucket rises in both years (2026: 2.5–4% +₹384/tr, 4–6% +₹865, ≥8% +₹695; 2025 positive in every bucket), so the FLOOR-3 challenger (a P2F size cap, transplanted from the N4 result) was refused at diagnosis. A morning's froth and a day's information are different axes; a cap that is medicine on one is poison on the other, and a cross-component transplant must re-derive its gradient on the target component before it is even frozen. *(Evidence: FLOOR session cycle 3; stocks_engine_floor_c3_diag.py)*
44. **Aggregation is the mirror sin of thin slicing: the quality bar binds in both directions.** At the FLOOR-C4 book the (comp × stock) axis showed two rows over the −₹500 bar (P2F-R2 × RECLTD −₹690.73; N4-V3 × PFC −₹561.82) and both were refused: each was a sum of direction slices that individually fail the bar, in different directions and mostly different years — and the PFC row concealed a +₹568.78 winning trade (2026) that the coarser cut would have deleted. SAT-30 closed the deletion frontier against slicing THINNER to find qualifying rows; FLOOR-5 closes it against aggregating WIDER to manufacture them. A slice qualifies on its own numbers at its own unit — (mechanism × stock × direction) — or it does not qualify at all. *(Evidence: FLOOR session cycle 5; stocks_engine_floor_c5_diag.py)*
45. **The frozen law had mis-priced the chain's tail, not killed it: INV-LONG rounds <=3 with an 11:00 cutoff banked +Rs11,255.92 combined through the full gate (Round 2, R2-07).** v2's earliness work (Lesson 36) bounded WHEN entries may occur by day-gate; inside the gated population, the round cap and the entry cutoff were separate frozen choices, and both were leaving money in both years: the grid's own control cell (rounds <=3 at the old 10:30 cutoff) reproduces the incumbent combined to the paisa, so the entire gain is the 11:00 entry hour plus round 3 at that hour — +Rs6,620.26 in the weak year, +Rs4,635.66 in the strong year. A parameter frozen by an earlier engine is a hypothesis with a date on it; the permutation cross (ADR x rounds x cutoff) is the instrument that re-tests it, and the control cell inside the grid is what makes the attribution exact rather than rhetorical. Corollary: the merged-law variants (rounds >=1 unified, R2-09/10) both failed — the INV-R3 split (FLAT-day and round>=4 rows under separate law) is load-bearing structure, not bookkeeping. *(Evidence: Round 2 R2-07 grid + R2-09/10; r2_results.json)*
46. **A slice scored dead at one exit geometry is not scored: the cell is (population x geometry), not population alone.** The N4 [0.75,1.0) lowband was negative at T125/S050 (SAT-4) and that verdict closed the axis in v3. At the book's T150/S080 geometry the 0.8% threshold banks +Rs2,075.33 through all nine legs (Round 2, R2-17) — small, and positive in both years (2025 +1,831.25 / 2026 +244.08). Exit geometry changes which trades in a population reach target before stop, so a geometry-specific rejection cannot be promoted to a population rejection. The reverse also binds: geometry wins do not transfer across populations (F4 per-cell geometries, R2-20..23, all failed). *(Evidence: Round 2 R2-17 vs SAT-4; r2_results.json)*
47. **Cross-year opposition is a property of the F4 population itself, not of any one axis.** Across two sessions and eleven gated F4 variants (band edges x2, measurement time, exclusions off, per-cell exit geometries x4, FLAT stand-aside), every population change moves the years in opposite directions: 2025 gains Rs12-18k while 2026 loses Rs20k-1,23,440. The DOWN cell is the same wall in label form (2025 227 tr / -2,370 vs 2026 312 tr / +1,06,006 at identical construction). The second-day continuation mechanism (PERSIST-R2, R2-19) shows the same signature in miniature (2025 +2,903.00 / 2026 -643.26). When every axis of a family flips sign across the same year boundary, the family's information is regime-conditional in a way its own features cannot express — further in-sample permutations of that family are re-rolls of the same dice, and the honest continuation is new data or a new information axis, stated as such with the numbers attached. *(Evidence: Round 2 R2-01..06, R2-19..24; stocks_engine_round2_2026-11-02.md full grid)*
48. **Passing eight of nine legs is a terminal state with its own name — flagged — not a banking with an apology.** R2-26 (INV-ABOVE T150/S080) adds +Rs13,089.83 combined, positive in both years, cells/halves/ex-top-3/placebos all green, and fails exactly one leg: Mar 2025 flips +1,091.17 -> -1,368.66 under the wider target. The per-cell splits prove the flip is not separable from the gain (UP-only fails ex-top-3 instead; FLAT-only keeps the flip). The engine's constitution does not contain a waiver power: the variant is reported with its failing leg named and its adoption value computed (+Rs7,534.00 to the weak year), and the decision moves to the user — the same disposition as the Nifty CH3-R adoption (2026-11-02). A gate that the engine can waive when the number is pretty is not a gate. *(Evidence: Round 2 R2-26/27/28; r2_results.json)*
49. **Confirmation is a cost, not a filter: the 09:40 confirming-close entry was the most expensive idea in Round 2.** Requiring the 09:35 bar to close beyond threshold before entering (N4, R2-16 and R2-18) costs Rs16-22k combined against the standard entry in both years — the five minutes of "confirmation" systematically pay away the move the signal identified, on the LONG and SHORT sides alike (the flipped placebo also degrades). Entry-delay variants of an event system must be presumed guilty: their burden of proof is a full gate pass, and a delay that merely reduces variance while surrendering the first bar's edge will show exactly this signature — fewer disasters, much less money. *(Evidence: Round 2 R2-16, R2-18; r2_results.json)*


---

# ROUND 3 LESSONS (2026-11-02) — targeted techniques on 2025

R3-L1. **A gated basket of sub-bar deletions is worth less than its
placebos.** The wound basket (7 rows, 58 trades, every member negative
in the wound months AND negative whole-book) gained +₹1,873.53 in 2025
but lost −₹178.10 in 2026 and was beaten by BOTH the mirror-months
basket (+₹5,029.93 over base) and plain chrono removal (+₹4,132.46).
Deleting "rows that lost in the red months" is not information; the
wound months are mostly small-sample noise on rows whose whole-book
sign is already known. The registry stays empty; do not re-run wound
baskets at other month sets.

R3-L2. **The biggest wound rows are the book's engines.** F4 TVSMOTOR
LONG/SHORT lost −₹6,866.88 combined inside Jun/Jul/Oct 2025 and earned
+₹34,912.05 whole-book. Any wound treatment that touches them destroys
the book. Wound size and row value are positively correlated here —
variance, not rot.

R3-L3. **The 2025 event layer was never incomplete.** 100/100 results
events with valid reaction dates, 100 candidates vs 2026's 80, MORE N4
signal-days (91 vs 77). Before rebuilding any data layer, audit it:
the suspected hole was in the OTHER year (16 placeholder reaction
dates, all outside the judged window). 2025's reaction-family weakness
is expectancy (P2F-R2 −₹390 vs +₹15,149) and band mix (33 vs 39 events
≥2.5%) — properties of the 2025 tape that no calendar repair changes.

R3-L4. **Entry delay is taxed in every construction.** Quarter-hour
deferral: F4 −₹33,001 in 2026 (2025 +₹229), INV −₹11,032 / −₹13,495.
Together with R2-03 (09:45 measurement) and R2-16 (09:40 confirmation),
four separate delay mechanisms all lose. The 5-min next-bar entry is
load-bearing for F4 and INV; the entry-timing axis is CLOSED for both
families at both the measurement and execution bars.

R3-L5. **The 25 fade gap-downs and follow nothing.** Gap diagnostic,
both halves, both years pooled: follow −₹27/−₹43 per trade; fade
+₹3/+₹26; fade-LONG-only (buy the gap-down) +₹57/+₹72; fade-SHORT
−₹49/−₹9. A real, sign-consistent phenomenon — and it STILL does not
bank: at book level it costs 2026 (−₹4,081 for the LONG-only sleeve;
−₹15,957 for the full fade) and concentrates in the top-3 stocks.
Standalone sleeve expectancy, even when positive in both diagnostic
halves, is not book value. The cross-year and concentration legs are
what separate a phenomenon from a component.

R3-L6. **May 2025 is the gate's tripwire.** Every gap-sleeve variant
flips May 2025 (+₹2,498.99) red — the sleeve's trades land heavily in
that month and lose there in both years' constructions. A candidate
that cannot survive May 2025 cannot bank, whatever it does to the
annual total; this is leg (f) doing exactly its job.

R3-L7. **Chandu's index ORB method does not port to the 25 cash
stocks.** −₹96,573 (2025) / −₹2,43,757 (2026) standalone at ~9,000
trades — the single worst construction ever gated by this engine.
Level breaks on individual names at T125/S050 are information-free
(lesson 2) at industrial scale. ORB on stocks is closed; do not run
range-width or exit variants of it.

R3-L8. **Three rounds, one shape of answer.** Rounds 1–3 have now
gated: the full F4/INV/reaction/N4 law grids, regime cells, wound
baskets, data completion, entry timing at both bars, and two new
mechanism classes (4 gap cells + a sign-split sub-sleeve + ORB). 2025
has not moved (₹56,336.30) since Round 2's two bankings, and every
2025-positive idea found since (gap-fade family) is 2026-negative or
top-3-concentrated. The remaining honest routes to the 2025 floor are
outside the current information set: Nov–Dec 2025 forward evidence
(already in the frozen test window), a genuinely new data axis (bulk/
block deals, delivery percentages — not in the workspace), or
Chandu-level adoption decisions on the two flagged gate-failures
(R2-26, R3-10). Grinding the same candles further is curve-fitting
pressure, not research.


---

# ROUND 4 LESSONS (2026-11-02) — combined flags, refinement, volume

R4-L1. **Regime restriction is the correct first refinement axis for
a cross-year failure — before thresholds, entries, or exits.** The
fade's 2026 damage was located, not diffuse: UP cell −₹5,572.97,
FLAT cell −₹4,331.35, DOWN cell +₹5,823.56. Excluding the UP cell
banked the phenomenon (R4-03). But restriction can overshoot:
DOWN-only failed the concentration leg — the FLAT cell's breadth
(ex-top-3 2025 ₹9,775.76 → ₹23,764.74) is part of the cure, not
collateral. Restrict by where the other year bleeds, then check
what the restriction did to breadth.

R4-L2. **A fill at the signal print is not an entry.** When the
signal is defined by the opening print itself (gap = bar-0 open /
prior close), entry at that print enters before the information
exists — on every trade (390 violations, R4-07, banking voided
the same run). The phantom improvement (+₹41k / +₹26k over the
honest bar-1 sleeve) is the first-bar snap-back measured at the
price that reveals it. Corollary for the harness: timing_violations
must be derived from the construction (entry bar vs the bar that
completes the signal), never defaulted to 0; any cell whose entry
bar is not strictly after its signal bar needs an explicit audit
argument, in writing, before it is scored.

R4-L3. **Raising the fade's threshold re-imports what regime
restriction removed.** Thresholds 2.0/2.5/3.0 on the unrestricted
population are all 2026-negative standalone (−₹8,493 / −₹1,329 /
−₹3,722): the biggest gaps fade worst precisely in the UP/FLAT
cells. Once a failure is located in a day-type, size filters are
the wrong tool — they re-weight the same cells instead of
excluding the bleeding one.

R4-L4. **Re-gate flagged variants after every banking; gate
interactions are book-level, not variant-level.** R2-26's sole
failing leg (Mar 2025 flip) vanished without the variant changing
at all: the banked sleeve's March gains (+₹5,033.28) absorbed the
swap's March loss (−₹2,459.83). On the Round-4 book, R2-26 passes
all 10 legs (R4-10). A flagged variant's status is a property of
the book it would join — reporting it frozen at its original
gate sheet misstates the owner's decision.

R4-L5. **Disjoint components combine exactly additively — verify
it, don't assume it.** R2-26 + R3-10 reproduced the summed deltas
to the paisa (2025 JO ₹90,849.69), and the additivity exposed the
real story: the combination's cross-year leg passes (+₹41.57)
because one flag's 2026 gain cancels the other's 2026 loss. The
combination's remaining failures (ex-top-3, May/Dec flips) belong
entirely to the full sleeve — which the banked refinement has
since superseded (R4-11/R4-12). Combined-flag arithmetic is a
decision tool, not a banking route.

R4-L6. **Volume is not in this workspace.** Every stored equity
candle (25 symbols + index, 5-min and daily) is OHLC-only; the
machinery carries no volume field. A volume-confirmed sleeve is
unbuildable from stored data — the gap is named, not filled.
Volume joins bulk/block deals and delivery percentages on the
list of axes that require a new data build before any cell may
be scored.


---

# ROUND 5 LESSONS (2026-11-02) — mirror, micro-grid, new population, conditioning, diagnosis

R5-L1. **The gap-fade does not mirror — its one-sidedness is now
measured, not assumed.** Fade-SHORT restricted to UP cells loses
-₹13,051.53 standalone in 2025 (101 trades UP+FLAT: -₹12,433.50)
and is beaten by its own mirror placebo (the follow-LONG book,
₹3,14,289.90, exceeds the variant by ~₹29k): on up-trend days,
gap-ups continue. The banked phenomenon is specifically
gap-DOWN reversion in DOWN/FLAT states. Lesson 18's discipline
(a mirror is a new system with no inherited credibility) applied
to the engine's newest component returns a negative verdict, and
the mirror family is closed on both cell sets.

R5-L2. **The banked sleeve is the peak of its own neighbourhood on
the gate's terms.** Around R4-03 (thr 1.5%, T125/S050, DOWN+FLAT):
thr 1.25% adds money in both years (+₹10,594.66 / +₹2,778.21) but
the incremental slice's 2026 gains sit in the top-3 names (leg e);
thr 1.75% loses both years; T100/S065 loses both years; T150/S065
gains 2025 (+₹7,131.19) and bills 2026 (-₹7,024.61) — leg (c)
alone, the R4-09R shape. Four neighbours, four rejections, each on
a different leg: the cell was not merely the first that passed.

R5-L3. **Non-event intraday extremes revert on the long side only —
a real phenomenon that concentration still refuses.** On stock-days
outside every results-reaction window, a >= 2.0% fall by 10:30
reverts (NE-REV LONG: +₹12,209.45 / +₹24,306.56 standalone, 691
trades, beats the opposite-direction and one-bar-late placebos,
positive in both years, halves and cells green) while a >= 2.0%
rise does not (SHORT: -₹41,334.92 / -₹18,088.52, 8 legs). The LONG
sleeve still cannot bank: its gains concentrate in the top-3
(combined ex-top-3 ₹99,322.68 -> ₹86,879.08) and it flips Dec
2025. Third confirmation of the R3-L5 pattern — standalone
expectancy, even placebo-beaten and cross-year positive, is not
book value until the concentration and month legs agree.

R5-L4. **P2F-R2's 2025 weakness is population-wide; no cell or band
condition separates it.** All four restrictions fail the same way:
whatever removes 2025's loss removes more of 2026's money. The
>= 4.0% reaction band is 2025's only positive P2F-R2 slice
(+₹150.80) AND 2026's engine (+₹12,724.86 of +₹15,149.33); the
[2.5%, 4.0%) band is the reverse. The family's sign flips across
the year boundary on every axis tested (cells x2, bands x2) —
Lesson 47's cross-year opposition, now on the reaction axis. The
conditioning axis for P2F-R2 is closed; its 2025 expectancy gap is
a property of the 2025 tape (R3-L3), not of a subset.

R5-L5. **The three red months have three anatomies; a frozen
signature rule that finds nothing is a result.** Jun 2025 is 7
INV-ABOVE trades and nothing else (an information desert, not a
bleed). Jul is a broad shallow bleed across four components. Oct
is 3 F4 trades. The only (comp x cell) slice negative in all
three months — INV-ABOVE x UP, -₹3,442.37 — earns +₹6,435.21
across full-year 2025: variance on an earner, refused by the
rule's full-year leg. No conditional candidate was manufactured.
Wound decomposition remains a diagnostic, not a deletion licence
(R3-L1/L2, confirmed at cell granularity).


---

# ROUND 6 LESSONS (2026-11-02) — pricing, repairs, conditioning, audit

R6-L1. **Delay is a tax on signal-following entries and a cure on
crowded marginal ones — the population decides, not the axis.**
Four delay mechanisms lost across Rounds 3–6 (R3-L4; R6-05's 11:05
entry destroyed NE-REV's 2025, −₹18,420.55 standalone). But the
gap-fade's marginal [1.25%, 1.5%) increment banked ONLY when delayed:
at 09:20 it failed leg (e) twice (R5-03's swap, R6-07's DOWN-only
form), at 09:40 it passed all ten legs (+₹2,305.22 / +₹4,763.03).
The early fills of a fade are the crowded ones; waiting 20 minutes
changed the increment's stock mix, not just its prices. The
entry-timing axis is therefore not "closed" as a blanket — it is
closed for follow constructions (the first bar IS the edge) and
was the winning axis for this fade population. Judge delay per
population, never per slogan. (No tension with R4-L2: the 09:40
entry is honest — the gap signal completes at the 09:15 print.)

R6-L2. **NE-REV's refuser is now singular and named: concentration.**
Two independent repairs (thr 2.25%; DOWN+FLAT restriction) each
fixed everything else — 2.25% posts the family's largest combined
book (₹3,47,839.48) with no flips; the restriction removes the
Dec-2025 flip exactly where the diagnosis said it lived (UP cells)
— and both fail leg (e) alone. When different constructions of one
phenomenon keep dying on the same leg, the leg is describing the
phenomenon: non-event morning-dump reversion pays in the book's
biggest names. That is an owner-decision fact (waive (e) or not),
not an engineering defect another cell will cure.

R6-L3. **A new mechanism inherits the book's cross-year opposition
until proven otherwise.** Range-expansion follow — a genuinely new
population (volatility state, no levels, pre-registered) — split
exactly like everything before it: LONG dead on 7 legs, SHORT
paying 2025 (+₹16,015.00) and billing 2026 (−₹10,286.95), failing
leg (c) alone. Lesson 47's signature is not a property of the old
families; on this workspace it is a property of the two tapes.
New-mechanism rounds should budget for the (c)-leg fight from the
start — and a (c)-only failure is the strongest owner-decision
class there is, since 2026 stays above its floor regardless.

R6-L4. **Admission causality is recomputed per component, never
inherited from the engine's reputation — and the audit harness is
itself an admission input.** The incumbent certified clean on every
price-derived input (prior-close regime gates recomputed row by
row; F4's premove and its ≥10:05 entries; both sleeves' prints;
the reaction families' after-close entries) and failed on exactly
one input class: N4-V3's event-day tag for same-day intraday
announcements (4 rows voided, combined +₹51.91 — immaterial to
the book, material to the standard). The same audit first
"flagged" 14 rows that were innocent: 8 F4 rows whose bars live
in the forward root, and 6 N4 rows admitted by news-class events
a results-only harness cannot see. An auditor run on a narrower
population definition than the machinery's would have voided
real trades and still missed nothing — the harness's universe
must be proven equal to the machinery's before its verdicts are
read (the R5-L3/R3-L3 discipline applied to the audit itself).

R6-L5. **Every banking and every void reprices every outstanding
flag (R4-L4, third confirmation).** Round 6 banked ₹2,305.22 and
voided ₹51.91 of base, and every flagged adoption total moved —
the triple by −₹1,691.75 of void and a −₹2,305.22 clean-adoption
net inside R5-03 — without any flagged variant changing at all.
Decision state quoted to the owner must be restated after ANY
book change, banking or void, in the same report that makes the
change; a flag quoted at its birth book is a stale price.


---

# ROUND 7 LESSONS (2026-11-02) — REXP repair, breadth-first sleeves

R7-L1. **Cell location is a diagnosis, not a presumption — and a
repair aimed at the wrong cell is worse than no repair.** The
book's two successful repairs both removed UP-cell damage (the
fade's cross-year fix, R4-L1; NE-REV's flip fix, R6-04), which
made "restrict the cells" the default tool. R6-10's damage,
decomposed before any repair was aimed (R7-01), sits in the DOWN
cell itself: +₹14,870.39 (2025) vs −₹8,399.33 (2026) on the
identical construction. Both pre-registered restrictions keep
DOWN whole: DOWN+FLAT is worse for 2026 than the unrestricted
population (−₹10,930.18 vs −₹10,286.95 — it deletes UP's +₹643.23
and keeps FLAT's −₹2,530.85), and DOWN-only still fails leg (c)
alone at −₹8,399.33. When the two years disagree INSIDE one cell,
the disagreement is about the mechanism's meaning on that tape,
not about admission — Lesson 47's wall, found inside a single
cell of a brand-new mechanism. Decompose first; a restriction is
only a repair when the damage has an address the restriction can
remove.

R7-L2. **The reversal phenomenon is a morning phenomenon — clock
time is part of a mechanism's identity.** The identical non-event
dislocation (≥2% fall, certified population, same exits) measured
at 13:25 instead of 10:25 posts −₹37,819.07 in 2025 (963 trades,
seven legs failed, beaten by its placebos) against the morning
form's positive weak-year standalone. Nothing about the
construction changed except the hour: a dump measured against
the open's information state reverts; a dump measured against
midday's continues into the close. Extends Lesson 33 (exit pairs
are population-specific) to measurement time: a signal's clock
is not a parameter to be optimised later, it is part of what the
signal IS.

R7-L3. **Stretching the dislocation's horizon destroys it: a
two-day fall is a trend state, not a reversal setup.** The
two-session ≥3% fall, faded intraday on certified non-event
sessions (977 trades), loses −₹62,345.49 / −₹43,694.93 — both
years, both placebos ahead, eight legs failed, the worst
standalone ever gated by this engine after ORB-on-stocks. The
reversal family is now bounded on every side: one session, one
morning measurement (R5-07 class) is the whole phenomenon;
afternoon (R7-L2) and multi-day (here) forms are different
animals and both are short-the-fade traps. Do not re-propose
longer-horizon or later-clock variants of NE-REV on this data.

R7-L4. **Leg (e) is a whole-book interaction, not a sleeve
property — breadth by construction does not cure it.** The
quiet-name sleeve was built to be (e)-clean: names selected by a
causal trailing-range characteristic, 196 trades, standalone
positive in both years (+₹4,492.57 / +₹12,167.10), placebos
beaten. It still fails (e): the variant book's combined ex-top-3
falls ₹12,148.03 because the sleeve's gains land in the book's
carrier names (a name quiet by trailing range is not disjoint
from the carriers), and every rupee a sleeve adds to a top-3
name is a rupee leg (e) subtracts. No sleeve can be certified
(e)-clean from its own population — the leg reads the assembled
book, including which names the sleeve pushes into the top-3.
This is R6-L2's conclusion from the other side: NE-REV fails (e)
because its phenomenon pays in big names; NE-REV-Q fails (e)
even after breadth engineering, because "big names" and "quiet
names" are overlapping sets on different days. The (e) question
is an owner decision (waive it for a named sleeve, or not), not
an engineering target with a construction left to find.

R7-L5. **Causality hygiene paid the weak year: the certified
population is worth more than the population it replaced.** The
R6-11 strengthening, applied to NE-REV's population for Round
7's sleeves, excluded 304 further stock-days and removed 30 of
R5-07's 691 rows — and the certified morning NE-REV standalone
ROSE in 2025 (+₹12,209.45 → +₹14,105.64) while holding 2026
(+₹24,306.56 → +₹24,112.86). The uncertifiable rows were
carrying noise, not edge: event-adjacent days are where a
"non-event" sleeve's premise is false, and their trades were
net losers in the year the floor is judged on. Repriced as a
flag (R7-08), the certified form is worth +₹1,802.70 more to
2025 than the flag's birth form with the same two failing legs.
Corollary: when a standard tightens, reprice the flags under it
before quoting them — a flag's birth population may no longer
be the population the desk would actually trade (extends
R6-L5 from book changes to standard changes).

---

# ROUND 8 LESSONS (2026-11-02) — the stack gated, follow buried, conditioning priced

R8-L1. **Failing legs do not inherit into an assembly — a stack
must be gated, never summed, in both directions.** The R7
arithmetic max stack carried (c) + (e) + (f) by inheritance from
its components. Gated whole at R8-02, the same four ingredients
fail **(f) alone**: leg (c) passes because the stack's other
ingredients pay 2026 ₹26,250.37 while R7-03 charges it ₹8,399.33,
and leg (e) passes because ex-top-3 is recomputed on the
assembled book (2025 ₹23,708.10 → ₹44,205.13 — the CERT sleeve's
breadth outweighs its own concentration at book level). The
assembly was also worth MORE than the restatement quoted
(₹1,23,231.11 vs ₹1,21,428.41: CERT form + clean R5-03). A
flagged list's arithmetic is a lower bound on information, not a
verdict; the owner's largest decisions deserve their own gate
sheet before they are quoted as refused. *(Evidence: R8-01
anchors; R8-02 gate sheet in r8_results.json)*

R8-L2. **Follow is dead on the home 25 in every form now tested —
the tapes fade strength and buy weakness; they do not chase.**
Drive-continuation (≥2% morning up-drive on certified quiet
days, LONG at 10:35, 800 trades) loses in both years
(−₹1,710.67 / −₹28,882.57, seven legs, beaten by its own
one-bar-late placebo). It joins gap-follow (R3), ORB-on-stocks
(R3) and the P2F-news transplant (Lesson 29/37 class) in the
closed set: every profitable direction this book owns is a fade,
a reversal, or a scheduled-information follow (results at R+1 /
R+2) — raw intraday price momentum is not among them, at any
clock or horizon tried (09:20, 10:35, 13:35, two-day). Do not
re-propose continuation sleeves on this data; the follow
question is closed with the same completeness as the reaction
(band × lag) grid. *(Evidence: R8-03; R8-04 non-trigger)*

R8-L3. **Index-state conditioning redistributes a sleeve's
failures; it does not remove them — and the banked book was
already wearing most of the condition.** Conditioning NE-REV on
NIFTY-down mornings kept 453/661 rows, cured its Jan-2025 flip,
and kept ₹11,353.09 of 2025 value — while Dec 2025 still flipped
and leg (e) still failed (conditioning selects days, not names;
the gains still land in carriers, R7-L4). And the fade's own
legs turned out to be 87% NIFTY-down mornings already (350/404):
a sleeve built on stock-level gap-downs in DOWN+FLAT regime
cells had implicitly selected index-down mornings, so the
explicit restriction bought only +₹3,598.21 in 2025 at
−₹2,477.24 in 2026 (leg (c)). Before proposing a conditioning
axis, measure how much of it the construction already contains
— the uncontained remainder is the whole candidate. *(Evidence:
R8-05, R8-06)*

R8-L4. **A geometry neighbour prices a leg; it does not dissolve
it.** REXP-DOWN at T100/S065 vs the frozen T125/S050: the 2026
bleed falls ₹8,399.33 → ₹5,899.72 and the 2025 gain falls
₹14,870.39 → ₹10,243.45 — the tighter target truncates 2025's
runners on the same trades whose stops it softens in 2026,
because both years' populations share the excursion shape that
made the family (Lesson 33's map, one cell finer). The (c)
question for this family now exists at two honest prices, and
choosing between them (or waiving (c) for either) is an owner
act, not an optimisation: any further geometry cell would just
draw another point on the same trade-off line. *(Evidence:
R8-07, population re-anchored at the frozen geometry first)*


---

# ROUND 9 LESSONS (2026-11-02) — one ingredient owned both flips; the cures interact; follow closes at the daily scale

R9-L1. **Decompose a stack's failing leg to ingredient × state
before designing anything — the failure may have a single
owner with two addresses.** The max stack's leg (f) read as a
property of the assembly; attributed exactly (the ingredients
are disjoint, so the attribution is arithmetic, not inference),
both flips belong to NE-REV-CERT alone — January through
DOWN-cell days when the index sat in a shallow dip, December
through UP-cell days. Three of the four ingredients contributed
+₹64.16 / −₹29.01 / ₹0.00 to the January delta: designing
repairs against "the stack" would have spent four ingredients'
worth of search on one sleeve's two states. Corollary: a
flagged stack's price is not a diagnosis; the gate sheet says
WHICH leg, the decomposition says WHOSE rows, and only the
row-level state table says WHY — in that order. *(Evidence:
R9-01; r9_ws0_decomp.json)*

R9-L2. **The mushy middle is a state, and a restriction that
removes a negative bucket is a repair, not a tax.**
NE-REV pays when a ≥2% fall is either systemic-deep (NIFTY
≤ −0.30% by 10:25 — the index capitulates and the bounce is
broad) or idiosyncratic against a non-falling index (≥ 0 — the
tape lifts the name back). Between them, the shallow-dip band
(−0.30%, 0) is the only NIFTY-state bucket negative combined
(−₹1,427.22, 67 rows) and held January's wound
(−₹5,192.36 of it). Excluding it (NOTCH) RAISED the sleeve's
2025 (+₹14,105.64 → +₹18,618.88) while costing 2026
₹3,086.02 — the sign of a restriction's price is a per-year
fact, exactly as a band's verdict is (Lessons 28/30), and
"conditioning always costs expectancy" is as false as
"conditioning is free". Price the bucket being removed, in
each year, before arguing about the rule. *(Evidence: R9
diagnosis cross-tabs; R9-02)*

R9-L3. **Cures interact inside an assembly: two single-cure
variants failed where their combination passed all ten legs.**
NOTCH alone left leg (f) (December); UPGUARD alone cured
December but broke leg (e) inside the stack (its kept 2025
population is thin and carrier-heavy, so the assembled book's
ex-top-3 fell) and left January flipped. Only NOTCH+UPGUARD
passed everything. A variant that fixes the named leg can
break a leg that was passing — leg (e) is a whole-book
interaction (R7-L4), and a sleeve-level cure says nothing
about it. Every conditioned stack must be gated whole and
never inferred from its ingredient's sheet (extends R8-L1
and R4-L4 from repricing to repair design). *(Evidence:
R9-02 / R9-03 / R9-04 gate sheets in r9_results.json)*

R9-L4. **Judge a repair where it will live: a fix too expensive
at sleeve level can be right at stack level.** IDXCELL
removes ₹6,022.69 of 2025 standalone (the IDX form's best
2025 cell) to cure −₹2,046.64 of December rows — as a
standalone ingredient it still fails (e) and pays ₹4,032.51
for its December cleanliness. Inside the stack the same rows
pass all ten legs, because the stack's other ingredients
re-supply the breadth leg (e) reads (2025 JO ₹1,13,146.38,
no flips, the highest 2026 stack price). The reverse also
held this round (UPGUARD: clean at sleeve level for
December, (e)-breaking in the stack). A repair's verdict is
a property of the book it joins — the R4-L4 discipline,
applied to fixes rather than flags. *(Evidence: R9-07,
R9-08; contrast R9-03)*

R9-L5. **The follow family is closed at every timescale now —
strength is a fade target on the home 25, full stop.**
ATH-proximity momentum (close within 2% of the trailing
252-session high → next-session LONG, 342 trades, no event
filter) loses in BOTH years (−₹21,322.97 / −₹27,329.31,
eight gate legs, beaten by its own placebos). It joins
gap-follow, ORB, drive-continuation and the news transplant
in the closed set (R8-L2): every profitable direction this
book owns is a fade, a reversal, or a scheduled-information
follow (results at R+1 / R+2) — raw price strength is not
among them intraday (09:20–13:35), multi-day, or as a daily
state. Do not re-propose strength-following sleeves on this
data in any timescale dress; a future follow proposal needs
a new information axis, not a new clock. *(Evidence: R9-05;
population and skips counted in r9_results.json)*
R10-L1 The conditioned NE-REV forms fail STANDALONE on leg (e) alone —
       NU and NOTCHCELL both, with zero flips and every other leg
       passing. Inside the stack the identical rows passed (e) because
       the stack's other ingredients re-supply the breadth the sleeve
       lacks. Leg (e) is a property of the whole book, not of the
       sleeve: a concentrated sleeve can borrow breadth from a stack
       but cannot manufacture it. Do not re-gate further conditioned
       variants of this population standalone expecting (e) to move.
R10-L2 UPGUARD is the December cure in every context: NOTCH standalone
       flips Dec 2025 to -632.67 (R10-03), the same wound the unguarded
       stack slot showed in R9-02; adding UPGUARD (NU) removes the
       flip standalone too. A wound that reproduces across contexts is
       a property of the population — when a condition cures it in two
       contexts, the condition, not the context, is the mechanism.
R10-L3 A state bucket can be a month wound and a cross-year asset at
       once: INV-ABOVE's shallow-dip rows are its ENTIRE July-2025
       loss (-2,473.45) yet a combined +2,445.28 earner across the
       two years (2026 +3,066.24). A month-shaped removal test without
       a combined-years leg will buy the patch with the other year's
       money — the separator test's leg (iii) is the discipline, and
       it fired correctly here (R10-05/06: July closes with no
       candidate).
R10-L4 An audit may find a real two-year loser the frozen test cannot
       name: INV-ABOVE's hard-dip rows lose in BOTH years (-1,230.62 /
       -4,012.18) but have zero July rows, so the July separator test
       stayed silent — correctly. Such findings go into the NEXT
       round's pre-registration; gating them in the same round would
       convert an observation into a fitted rule.
R11-L1 Two single-leg failures from DIFFERENT families can cure each
       other assembled — and the minimal cure is a pair, not the
       stack. NE-REV-NU (fails (e) only standalone, R10-02) +
       REXP-DOWN T100/S065 (fails (c) only, R8-07) pass ALL TEN
       legs together (R11-03): NU's 2026 volume absorbs REXP's
       2026 cost, curing (c); REXP's profit lands outside NU's
       carrier names, curing (e). Extends R10-L1 (breadth is a
       book property): when two flags fail DIFFERENT single legs,
       gate the cross-family pair before pricing either one as a
       standalone adoption.
R11-L2 Leg (e) can refuse a removal that makes money in both years.
       INV-ABOVE's hard-dip rows lose in both years (-1,230.62 /
       -4,012.18), yet deleting them LOWERS combined ex-top-3 by
       135.40 (R11-02): the losses sit partly inside the carrier
       names, and deleting a loss from a top-3 name raises the
       top-3 sum one-for-one. A rotten slice inside a carrier is
       invisible to deletion — report both numbers and let the
       owner decide; do not call the slice clean or the gate
       wrong.
R11-L3 A concentration failure may have NO state address. NU's
       leg-(e) failure decomposes exactly (R11-05) into a 2026
       name fact: +34,926.51 inside three carriers (TVSMOTOR /
       OBEROIRLTY / ASTRAL) against -11,182.11 OUTSIDE them —
       the sleeve's breadth is negative, not thin. No regime
       cell and no index-state bucket is negative in both years
       (separator test: 0 qualify), so no conditioned variant
       exists to gate. When the anatomy says the money is
       names, not states, stop searching for a state condition:
       the cures are assembly (R11-L1) or owner adoption.

---

# ROUND 12 LESSONS (2026-11-02) — the new baseline re-judges the flags

R12-L1. **A single-leg failure can be a property of the
baseline, not of the candidate — re-gate interaction-leg
flags after any breadth-moving banking.** The INV-ABOVE
hard-dip exclusion failed leg (e) by Rs135.40 on the pre-pair
book (R11-02) and passes ALL TEN LEGS on the pair book
(R12-02) without one row of the construction changing: the
pair raised combined ex-top-3 (Rs1,01,181.87 ->
Rs1,03,228.30) and moved the carrier sets, so the identical
removal's ex-top-3 delta swung from -135.40 to +953.74. A
flag's birth gate sheet is a price on a book that no longer
exists; after a banking that moves breadth, the (e)/(f)-only
flags must be re-GATED, not merely repriced — extends
R4-L4 / R6-L5 from adoption values to verdicts.
*(Evidence: R11-02 vs R12-02 gate sheets; r12_results.json)*

R12-L2. **A swap flag silently absorbs later bankings into
its cost — its "clean" form is defined against a book that
keeps moving.** R5-03's recorded 2026 delta (+Rs2,778.21)
was measured when the swap only had to beat the thr-1.5%
sleeve. By Round 12 the same "clean" swap must also retire
GAP-FADE-INC (banked at R6-08, after the flag was born), and
on the pair book it fails (c) AND (e): 2026 -Rs1,984.82,
combined ex-top-3 -Rs5,575.96 (R12-03). The mirror of
R12-L1: baselines acquit some flags and convict others.
Any flag whose construction references other components
("retire X", "replace Y") must be re-derived against the
current component inventory before it is quoted — Lesson 16
applied to swaps, whose deltas expire on the components
they displace, not only on the legs they touch.
*(Evidence: R12-03 gate sheet vs the R5-03 birth sheet)*

R12-L3. **Delta legs and interaction legs are different
kinds of failure, and only one kind can be cured by a new
baseline.** Legs (b)/(c) compare a variant's year total
against the base's: for a replacement or restriction, the
sign of that difference is fixed by the ingredient's own
rows versus the rows it displaces — negative on every
baseline, provable by arithmetic without scoring (R12-04:
every (c)-only flag's 2026 delta vs the banked form it
displaces is negative by row identity; every NE-REV slot
alternative fails (b) or (c) as a swap against NU's
standalone sums). Legs (e)/(f) are recomputed on the
assembled book — its top-3 sets, its month balances — and
those a new baseline genuinely moves, in both directions
(R12-L1, R12-L2). Before re-gating any single-leg flag,
name which kind its leg is: a delta-leg failure is closed
on every baseline and re-scoring it is theatre; an
interaction-leg failure is open exactly once per materially
different baseline. *(Evidence: R12-04 screening record;
R12-02 / R12-03 verdicts)*

R12-L4. **The weak year's worst month can be the strong
year's engine room — the separator test's combined leg is
the only thing standing between the book and self-amputation,
and it fired correctly twice in one round.** October 2025
(-Rs3,751.28) is three F4 trades, all in the up index-state
bucket; that bucket is -Rs9,887.43 in 2025 and +Rs40,581.38
in 2026 (+Rs30,693.95 combined), so test (iii) refuses the
removal (R12-05). July's residual is the same shape one
component over: INV-ABOVE shallow-dip is July's whole wound
and +Rs2,445.28 combined (R12-07, the R10-05 cell refusing
for the second time). Lesson 47's cross-year opposition,
found at (component x state-bucket) granularity inside
single months: a month-shaped separator test without the
combined-years leg would have bought both patches with the
other year's income. *(Evidence: r12_oct_decomp.json;
r12_july_decomp.json)*

R13-L1. **An index method's level geometry does not transplant
to single names — the sweep + reclaim is information-free on
his 25 in both directions, at population scale.** Chandu's
index method #4 (bear-trap / Blue-Line reclaim) was gated on
cash stocks verbatim in spirit: prior-day-low sweep in the
morning window, first close back above the low, next-bar
entry, T125/S050. It produced 2,885 signals and lost
-Rs1,62,923.55 / -Rs1,06,668.60 standalone (expectancy
~-Rs93/trade), failing nine of ten legs and losing to both
placebos — on identical entries the opposite direction is
the less-bad side. The mirror (prior-day-high sweep +
rejection SHORT, 3,098 signals) is gross-zero before costs
(-Rs4/trade after them), Lesson 2's signature exactly. This
is Lesson 2's family at its largest measured scale: a
single-name prior-day level is crossed and reclaimed
thousands of times a year and none of it is information.
Whatever the index version earns lives in index-level
structure (the multi-day Red bands / ledges of the frozen
method are not a single stock's prior-day low), and the
transplant direction for level events is now closed, not
merely doubted. *(Evidence: R13-02 / R13-03;
r13_results.json)*

R13-L2. **The same geometry step is medicine for one sleeve
and poison for another — in the same round, on the same
book.** The S065 -> S050 stop step banked for REXP-DOWN
(+Rs2,242.66 / +Rs1,515.38, both years up: its
range-expansion entries that work do so without the extra
room) and cost NE-REV-NU in both years (-Rs3,028.80 /
-Rs740.22, June 2025 flipped): NU's dip-buying population
needs the room REXP's does not. Lesson 4's population
specificity, confirmed as a mirror pair inside one round —
there is no book-level stop prescription even between two
sleeves banked together. The same round brackets both
sleeves' TARGET axis identically: T100 -> T125 buys 2025
and charges 2026 on REXP (+2,291.26 / -4,252.67) and on NU
(+2,326.81 / -5,998.05) alike — on this book the target step
is a year-trade, not an improvement, whichever sleeve wears
it; only the stop axis discriminates, and it discriminates
in opposite directions. *(Evidence: R13-04…R13-07;
r13_results.json)*

---

# ROUND 14 LESSONS (2026-11-02) — geometry neighbours on the original sleeves

R14-L1. **The target step is a year-trade on the original
sleeves too — with one measured exception that marks its
boundary.** F4 at T175/S095: +₹6,280.30 (2025 JO) /
−₹10,767.28 (2026 JO), fails (a) + (c). INV-LONG at
T150/S050: +₹4,275.39 / −₹10,547.95, fails (a) + (c). The
R13-L2 signature (REXP and NU priced the identical trade)
is now five sleeves wide: on this book a wider target buys
the weak year with the strong year's money wherever it is
worn. The exception is INV-ABOVE at T150/S050, which paid
BOTH years (+₹2,050.12 / +₹2,753.43, all ten legs) — the
thinnest population in the family (124/20 rows), whose
winners were genuinely being truncated at T125. A target
step is not a book-level prescription in either direction:
it pays exactly where the population's winners run past
the old target in both regimes, and that is a per-sleeve
measurement, never a prior.

R14-L2. **A two-axis flag's failing leg can be decomposed
by single-axis cells — and the clean half may bank
outright.** The flagged R2-26 swap (INV-ABOVE T150/S080)
failed (f) alone: a March-2025 flip. Gated separately, the
target half at the incumbent stop (T150/S050) banks with
no flip at all, while the flip is therefore attributable
to the S080 stop widening. R2-26 as a whole stays flagged
(its stop half is what fails), but its target half now
lives in the banked book. Before pricing a two-axis flag
for the owner, decompose it: the adoption question may be
smaller than the flag.

R14-L3. **Attribution and adoption are separate verdicts
— a cell can be right about its axis and still not bank.**
The P2F family at T150/S050 (target only, incumbent stop)
settles Lesson 33's open attribution: Jan–Oct rises in
both years (+₹627.22 / +₹111.87), so the two-axis swap's
2025 bleed was the STOP widening, not the target. The
cell still fails the gate — (a) + (b) + (e): full-year
2025 falls (the family's Nov/Dec rows pay for the wider
target) and combined ex-top-3 falls. The diagnosis the
cell was bought for is complete and is recorded as such;
it does not convert into a banking, and the family's
exits stay closed at T125/S050, now with both axes
individually measured.

R14-L4. **A geometry verdict expires with its population —
in both directions.** N4-V3 at the scorecard cell
(T125/S050) was the incumbent before SAT-15; reverting to
it on the CURRENT population (0.8% threshold, FLOOR-2
one-sided cap, R6-11 voids — all postdating SAT-15) costs
2025 JO −₹8,137.41 / 2026 JO −₹18,013.98, failing four
legs. The SAT-15 rebuild's measured value at birth
(+₹9,483.45 on its population) has GROWN on the
population that replaced it. Lesson 46 said a cell is
(population × geometry); Round 14 adds that a banking's
worth is not a constant either — when a population is
re-lawed, the geometry verdicts riding on it must be
re-measured, not inherited in either direction. The book
cell (T150/S080) and the November scorecard cell
(T125/S050) are different systems on this population;
the scorecard stays as frozen, and the book keeps its
pair — the two are no longer the same trade wearing two
labels.

R14-L5. **A family swap is judged as a family — its comps
may trade years against each other inside it.** The
GAP-FADE family at T125/S065 banks whole (all ten legs;
family JO +₹579.68 / +₹1,478.42) while its comps move in
opposite directions at full-year: GAP-FADE 2026
−₹2,786.62 against GAP-FADE-INC 2026 +₹4,265.04 (the
increment's later, calmer entries use the wider stop
better than the 09:20 entries do). The gate's unit was
the family as pre-registered; decomposing the banking
after the fact into "the good comp" would be a new
candidate requiring its own gate, not a reading of this
one. Same round, the estimate discipline: the frozen
diagnostic's stop-axis rough swing was +₹12,157.87 and
the exact banked gain is +₹2,058.10 combined full-year —
Lesson 31's magnitude warning (right direction, ~1/6 the
size), recorded beside R13-L2's stop-axis result: on this
book the stop axis is where geometry money is, and it is
always smaller than the excursion arithmetic promises.

---

# ROUND 15 LESSONS (2026-11-02) — second geometry steps + the volume axis

R15-L1. **A banked step does not license its continuation —
the second rung is a new measurement, and on both banked
directions it failed.** INV-ABOVE's target axis: T150 paid
both years (+2,050.12 / +2,753.43); T175 re-prices the
years against each other (+92.57 / −1,198.29, leg (c)
only). The fade family's stop axis: S065 paid both years
(+579.68 / +1,478.42); S080 charges both (−2,548.14 /
−4,790.90, four legs) and takes GAP-FADE's 2026 standalone
negative. Geometry on this book is a landscape of peaks,
not slopes: every axis measured so far has its paying cell
at or before the first step from the incumbent.
*(Evidence: R15-02 / R15-03; r15_results.json)*

R15-L2. **The volume axis's first frozen form is dead at
diagnostic strength, and the diagnostic did its job.**
Keeping only entries whose prior day traded at or above
its trailing-20-day median volume costs all three
placebo-equipped sleeves combined money — F4 −₹47,355.57
(the restriction deletes the days F4's 2026 winners were
built on), N4-V3 −₹9,385.58, P2F family −₹3,003.70 — so
no gate was spent on any of them. A diagnostic that can
return "no cell earns a gate" is the cheapest control the
engine owns; the round's volume spend was one fetch and
one subset computation. *(Evidence: R15-04 / R15-05;
r15_results.json)*

R15-L3. **A diagnostic's mirror image is a new candidate,
not a result.** The rvol ≥ 1.0 restriction losing on all
three sleeves implies the rvol < 1.0 restriction gains on
the same arithmetic — and that implication is NOT a
finding. The mirror form was not pre-registered, was not
run, and enters the record only as an untested observation
for a future round's pre-registration, where it will face
the full gate (placebos on the conditioned population,
concentration, flips) like any other cell. Subset
arithmetic chooses cells; it never banks them.
*(Evidence: R15-05; the pre-registration's frozen rule)*

R15-L4. **A data axis is built once, completely, or not at
all.** The volume fetch returned all 484 series days for
all 26 series with zero holes against the machinery's own
calendar in both judged years, zero zero-volume days in
the 25 stocks, and coverage of the two forward days
(2026-10-29/30) the book trades on — so every downstream
population was classifiable (0 unclassifiable rows) and
no verdict this round carries a data caveat. The two
named oddities are facts of the source, recorded as
returned: an index's volume is 0 on every day (NIFTY is
stored, and used by no gate), and the API series extends
two days past the machinery's stored daily span. Where a
future axis cannot be built complete, its holes must be
named per stock-year before any gate touches it — the
standard this build sets. *(Evidence: R15-04;
stocks_daily_volume_coverage.json)*

---

# ROUND 16 LESSONS (2026-11-02) — the volume mirror

R16-L1. **A restriction family is closed only when both
directions have faced the exact gate — and the mirror can
be the worse of the two.** Round 15's form (keep prior-day
rvol >= 1.0) died at the diagnostic on all three sleeves,
and the subset arithmetic pointed at the mirror: F4's 2026
losers under that form (-Rs49,328.51) implied its winners
sat behind quiet prior days. The exact gate refuses the
implication. Keeping only the quiet half costs F4 MORE in
2026 (-Rs53,727.42) than deleting it did, flips March 2026,
and fails five legs; on N4-V3 the mirror fails the same
four delta/concentration legs. Both halves of both
populations carry the sleeves' value — the unrestricted
population is the system, and prior-day relative volume at
the trailing-20-median band separates nothing in either
direction. R15-L3's discipline is the reason this is a
measurement and not an embarrassment: the mirror was
pre-registered as a candidate, gated with placebos on its
own conditioned population, and refused on named legs.
*(Evidence: R15-05 diagnostic; R16-02 / R16-03;
r16_results.json)*

R16-L2. **A pre-registered run-condition is a control, not
paperwork.** WS3 froze its trigger before any scoring —
the P2F mirror would run only if a larger sleeve banked
the form or failed it on exactly one leg. Both refused it
on four and five legs, so the thinnest population (the
P2F mirror keeps 4 / 9 rows) was never scored, and the
round spent zero gates shopping for a friendlier cell
after unfriendly verdicts. The symmetric discipline to
the diagnostic that assigns gates (R15-L2): a condition
that can return "do not run" protects the round from its
own sequence — verdicts already seen must not be allowed
to re-choose which cells get measured.
*(Evidence: R16-04; the Round-16 pre-registration)*
