# Bank Nifty recursive engine — frozen definitions

Definitions are written here BEFORE any scoring in a cycle. Nothing in this file is edited after its cycle has been scored; a new fix gets a new section.

## Incumbent — V1 (frozen 2026-10-30, carried in as the book to beat)
Verbatim from `november_paper_bank_V1_frozen.md` / `aggressive_oct_bank.md`:
- V1 = B2 + NS1 second legs, UNIQUE-ONCE per (date, index, direction), earliest entry.
- B2 = U1 Bank pool with (1) Skill V3 Bank CE blocked, (2) Skill-solo Bank legs with entry ≤09:55 dropped. U1 components: (lA) v2 (L1) + V5 v2 + Tuned Skill V3 (CE no-block in the raw pool; the B2 block applies after pooling) + Volrix tuned intraday (b) at −1.0%.
- NS1 second legs: at most one second leg per day after the base leg exited by target or stop with exit-bar time ≤13:30; second signal = first fresh crossing of either opening-range level after the base exit bar, signal time ≤14:30, room_ratio ≥1.5, CE blocked on a bearish-bias day.
- No NS2 legs in V1.
- Exits G0: stop = entry − 50 premium points, target = entry + 90, stop before target on every bar including entry bar, square-off 15:10.
- Entry premium = open of the 5-min option candle at the entry bar; strike ATM nearest 100; expiry in force for the trade date; lot 30; cost ₹220/trade.

## Cycle definitions
_(Each cycle appends its one frozen fix here before scoring.)_

## Cycle 1 — TIGHT-STOP-40 on the V1 pool (frozen 2026-10-31, BEFORE scoring)
- **Diagnosis (working book = reproduced V1, reconciliation PASS to the paisa):** October V1 = 12 trades, 9 targets (+₹2,480 each = +₹22,320) and 3 stops (−₹1,720 each = −₹5,160) → +₹17,160. The ONLY October drag is full −50 stops. Jan–Oct: 68 stop exits total −₹116,960 — the largest single drag line in the book. A wider stop (−65) was tried pre-engine and failed (lesson 4); a tighter stop was never tried.
- **The one fix:** exit geometry on the full V1 pool (B2 base + NS1 second legs, UNIQUE-ONCE unchanged) changes from stop −50 / target +90 to **stop −40 / target +90**. Everything else identical: stop checked before target on every bar including the entry bar, square-off 15:10, entry = open of the 5-min option candle at the entry bar, ATM nearest 100, lot 30, cost ₹220/trade. No entry, component, direction or date change.
- **Controls in the same run:** timing audit on every trade; placebo = same legs, same −40/+90 geometry, entry delayed +30 min (6 bars); halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3-trades stress; independent re-sum from the written trades file.
- **Banking rule (protocol):** bank only if October improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs V1 (42.3% Jan–Oct / 75.0% Oct).

## Cycle 2 — NS1-CE-BLOCK on the V1 pool (frozen 2026-10-31, BEFORE scoring)
- **Diagnosis (working book = V1, from `bank_engine_V1_trades.csv`):** NS1 second legs split cleanly by direction — CE second legs: 25 trades, −₹10,925.50, FT 24.0%; PE second legs: 16 trades, +₹15,897.50, FT 62.5%. October's CE second leg (6 Oct, 10:45) is one of October's 3 stops (−₹1,720); both October PE second legs hit target (+₹4,960). This extends lesson 2 (CE breakout legs are the poison family in this channel) to the second-leg mechanism; the frozen NS1 rule only blocks CE second legs on bearish-bias days — the controlled split says CE second legs bleed across all day types.
- **The one fix:** in the V1 pool, **drop every NS1 second leg with direction CE** (all months). Everything else identical: B2 base legs untouched (CE base legs stay), PE second legs stay, G0 exits −50/+90, stop before target, square-off 15:10, entry = open of the entry-bar option candle, ATM nearest 100, lot 30, cost ₹220/trade, UNIQUE-ONCE unchanged (dropping a second leg never creates a new leg).
- **Controls in the same run:** timing audit on every trade; placebo = same kept legs, G0 geometry, entry delayed +30 min (6 bars); halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3-trades stress; independent re-sum from the written trades file.
- **Banking rule (protocol):** bank only if October improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs V1 (42.3% Jan–Oct / 75.0% Oct).

## Cycle 3 — CHALLENGER: G7 runner-lock50 exits on the engine book v2 pool (frozen 2026-10-31, BEFORE scoring)
- **Why a challenger:** protocol challenger rule — every 3rd cycle builds a challenger from the lessons instead of a patch. This is the challenger queued in lesson 12 (G7 was a genuine small improvement on B2 legs pre-engine: +₹4,200 Jan–Oct, FT and frequency exactly held, red January fixed) — never yet tested on the V1 pool, and not on the current book v2 pool (V1 + NS1-CE-BLOCK). S1 pre-engine stacked G7 on the V3 pool's October set only and was dominated there; its Jan–Oct on any NS1-containing pool was never scored.
- **Diagnosis (target month September, book v2):** September = 8 trades, −₹2,327 (4 stops −₹6,880, 2 targets +₹4,960, 2 square-offs −₹407). The Jun–Sep bleed is stop-dominated (Jun 7 stops/2 targets, Jul 10/3, Aug 8/2, Sep 4/2). Stop distance is a dead lever (lessons 4 + 14), so the challenger attacks the WINNER side: raise what a reached target is worth.
- **The challenger (one structural change):** exits on the full book-v2 pool change from G0 plain to **runner-lock50**: stop −50 until the premium touches entry+90; from the next bar the stop locks at entry+50 and the target extends to entry+150; square-off 15:10. Everything else identical to book v2 (pool = B2 base + NS1 second legs with CE second legs blocked, UNIQUE-ONCE, entry = open of entry-bar candle, ATM nearest 100, lot 30, cost ₹220/trade). A trade counts as full-target when it reaches the +90 trigger (same FT definition as the pre-engine G7 scoring).
- **Controls in the same run:** timing audit on every trade; placebo = same pool, same runner-lock50 geometry, entry delayed +30 min (6 bars); halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3-trades stress; independent re-sum from the written trades file.
- **Banking rule (protocol):** the challenger replaces the working book only if September improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v2 (46.7% Jan–Oct; October must not be un-secured — it must stay ≥ its banked +₹18,880 is NOT required, but no previously secured month may be un-secured: October must remain strongly positive and no month-end may go red).

## Cycle 4 — PREMIUM-BAND-BLOCK [400,550) on the book v2 pool (frozen 2026-10-31, BEFORE scoring)
- **Diagnosis (working book v2, from `bank_engine_cycle2_trades.csv`):** legs entered at a premium in the 400–550 band are the book's dead zone — Jan–Oct: 20 trades, −₹8,607.50, FT 5/20 (25.0%), vs 250–400 band +₹18,480 (FT 61.9%) and ≥550 +₹10,991. September specifically: 3 of its 4 stops (premiums 534.60, 479.15→square-off −104.50, 411.45, 403.00 — four of its five losers) sit in [400,550); its winners sit outside it (952.50 target, 301.15 target). The band edges are the round diagnostic bins printed before this fix was chosen, not optimised edges. Entry premium is known at the entry bar's open — the rule is ex-ante.
- **The one fix:** in the book-v2 pool (B2 base + NS1 second legs, CE second legs blocked), **drop every leg whose entry premium (open of the 5-min option candle at its entry bar) is in [400, 550)**. Everything else identical: G0 exits −50/+90, stop before target, square-off 15:10, ATM nearest 100, lot 30, cost ₹220/trade, UNIQUE-ONCE unchanged.
- **Controls in the same run:** timing audit on every trade; placebo = same kept legs, G0, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum.
- **Banking rule (protocol):** bank only if September improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v2 (46.7%). Known cost accepted in advance: October's 13 Oct target (entry premium 547.35) falls in the band and will be dropped — October must remain strongly positive, which the diagnosis supports (+₹18,880 − ₹2,480 = +₹16,400 expected).

## Cycle 5 — TARGET-75 on the book v3 pool (frozen 2026-10-31, BEFORE scoring)
- **Diagnosis (working book v3):** the Jun–Sep bleed is a full-target collapse, not a stop-size problem (lessons 4, 14 closed stop distance): book v3 FT Jan–May = 27/42 (64.3%) vs Jun–Sep = 8/36 (22.2%); August = 2/10. In weak months Bank premiums travel toward +90 and fall short or reverse — bigger targets were rejected pre-engine (lesson 3), but a SMALLER target was never tried in this channel.
- **The one fix:** exit geometry on the full book-v3 pool changes from stop −50 / target +90 to **stop −50 / target +75**. Everything else identical: pool (B2 base + NS1 second legs, CE second legs blocked, premium band [400,550) blocked), stop checked before target on every bar including the entry bar, square-off 15:10, entry = open of the entry-bar option candle, ATM nearest 100, lot 30, cost ₹220/trade, UNIQUE-ONCE. Full-target % is scored against the +75 target for this candidate.
- **Controls in the same run:** timing audit on every trade; placebo = same pool, same −50/+75 geometry, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum.
- **Banking rule (protocol):** bank only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v3 (50.0% at the +90 definition; the candidate's FT is read at its own +75 definition and must also not be bought purely by the lower bar — the NET legs of the gate decide: total and August must both rise in rupees).

## Cycle 6 — CHALLENGER: book v3 + NS4 opening-range-rebreak add-on legs (frozen 2026-10-31, BEFORE scoring)
- **Why a challenger:** protocol challenger rule — every 3rd cycle. Leg-dropping is nearly exhausted (frequency 2.17/week, lesson 17) and exit geometry is closed in both directions (lessons 3, 4, 14, 16, 18), so the challenger adds a NEW component mechanism, consistent with every lesson and contradicted by none.
- **Diagnosis (target month August, book v3):** August = 10 trades, −₹5,581, all base legs — no add-on leg survives in August, and the book's frequency margin is thin. NS4 (opening-range rebreak: after the opening range is set, price leaves and re-breaks it later in the session) is a frozen Bank family that was only ever scored spot-provisional — never on premiums (lesson 1 forbids judging it on spot). Bank NS4 legs Jan–Oct: 60; on (date,direction) keys unused by book v3: 28 add-on candidates (August +2: 11 Aug PE 11:15, 20 Aug CE 13:35); exact-tag premium candles exist for 24 of the 28 — the other 4 are NOT_COMPUTED, excluded and counted, never substituted.
- **The challenger (one structural change — an added component):** book v3 pool **plus NS4 or_rebreak legs as add-ons**, where an NS4 leg is admitted only if (a) its (date, direction) key is unused by the book-v3 pool (add-on semantics — it never replaces a book leg), (b) its entry premium is outside the book's admission band [400,550) (same admission rule as every book-v3 leg), and (c) its exact-tag premium candles exist. Everything else identical: G0 exits −50/+90, stop before target, square-off 15:10, entry = open of the entry-bar option candle, strike ATM nearest 100 to the leg's entry spot, expiry in force, lot 30, cost ₹220/trade, UNIQUE-ONCE.
- **Controls in the same run:** timing audit on every trade (NS4 entries checked against their signal times in the NS4 file; book legs as before); placebo = same combined pool, G0, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated.
- **Banking rule (same frozen standard as Cycle 3):** the challenger replaces the working book only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v3 (50.0%).

## Cycle 7 — CHALLENGER: PREMIUM-GATED RUNNER on the book v3 pool (frozen 2026-10-31, BEFORE scoring)
- **Why a challenger:** protocol — 2 consecutive no-bank cycles on August (Cycles 5, 6) and a challenger is mandated. Built from lessons 12 + 16: the runner is real but regime-dependent; Cycle 3's per-leg data (already scored, used here as diagnosis) shows WHERE it works.
- **Diagnosis:** runner-lock50's delta vs G0 on the v2 pool, by entry-premium band: **<400: +₹8,400 (28 legs)**; 400–550: −₹3,000 (band now excluded from the book anyway); ≥550: +₹4,800 but containing the weak-month taxes. August's only cheap-premium target (24 Aug, entry premium 173.60) ran the full way to +150 under the runner (+₹4,280 vs +₹2,480), while August's expensive target (4 Aug, 629.95) was lock-taxed — a premium gate keeps the first and spares the second. Cheap premiums have expansion headroom when a move runs; that is the state this challenger conditions on. Entry premium is known at the entry bar's open — ex-ante.
- **The challenger (one structural change — a state-gated exit assembly):** on the book-v3 pool, legs with **entry premium < 400** exit by runner-lock50 (stop −50 until entry+90 is touched; from the next bar stop locks at entry+50, target extends to entry+150; square-off 15:10); legs with **entry premium ≥ 400** keep plain G0 (−50/+90). Pool, entries, strikes, lot 30, cost ₹220/trade and UNIQUE-ONCE unchanged. Full-target counts a leg that touches +90 (same definition as the pre-engine G7 scoring).
- **Controls in the same run:** timing audit on every trade; placebo = same gated assembly, same pool, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum.
- **Banking rule (same frozen standard as Cycles 3 and 6):** the challenger replaces the working book only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v3 (50.0%), with no secured month un-secured (September and October must stay green/strongly positive).

## Cycle 8 — NS3 gap-class add-on legs on book v4 (frozen 2026-10-31, BEFORE scoring)
- **Screened out before this cycle (diagnosis only, not scored as fixes):** (i) stale/time-stop exit — of book v4's 42 stop legs only 7 were still open 60 min after entry (avg premium change ≈ 0 at +60 min) while 4 of 12 still-open target legs were underwater at +60 min and would have been killed; (ii) spot-drift state gate — August's PE stops were entered WITH direction-aligned drift (+0.23% to +0.52%) and still died, and every drift band of book v4 is net positive (no losing pocket exists to gate); spot coverage also incomplete (185 of 203 days). (iii) Runner-gate refinement to [250,400) — worth +₹1,200 total on Cycle 3/7 data but deterministically costs August its +₹1,800 runner gain, so it is PARKED until August is secured by other means (same status as Cycle 3's observation).
- **Diagnosis (target month August, book v4):** August = 10 trades, −₹3,781; its entries go straight down (stop-leg MFE: six of seven < +25) and no exit mechanism can rescue them (lessons 4, 14, 16, 18 + the screens above). The only remaining direction is new entries. NS3 (gap-class: GU/GD/FLAT legs classified by the day's gap) is the last Bank add-on family never premium-scored. Census: 58 Bank NS3 legs → 26 on keys unused by book v4 → only 6 admissible after the premium-band admission rule (6 dropped) and exact-candle availability (14 NOT_COMPUTED, excluded and counted). August gains 1 candidate leg (6 Aug CE FLAT 09:55). This cycle is scored honestly on all gate legs; its thinness is stated in advance — it completes the add-on census either way.
- **The one fix:** book v4 pool **plus admitted NS3 legs as add-ons** (admission: (date,direction) key unused by book v4; entry premium outside [400,550); exact-tag premium candles exist). Add-on legs take the book's current exit assembly (premium-gated runner: entry premium <400 → runner-lock50, ≥400 → plain G0). Everything else identical: entries = open of entry-bar candle, strike ATM nearest 100 to entry spot, expiry in force, lot 30, cost ₹220/trade, UNIQUE-ONCE.
- **Controls in the same run:** timing audit on every trade (NS3 entries checked against their signal times); placebo = same combined pool and exit assembly, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated.
- **Banking rule (protocol):** bank only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v4 (50.0%).

## Cycle 9 — CHALLENGER: NS5a skill-rescan add-on legs on book v4 (frozen 2026-10-31, BEFORE scoring)
- **Why a challenger:** protocol — every 3rd cycle (3, 6, 9). NS5a (Skill-system afternoon rescan legs) is the largest Bank family never premium-scored: 90 legs → 44 on keys unused by book v4 → 12 admissible under the book's admission rules (13 band-dropped, 19 NOT_COMPUTED excluded and counted), with up to 3 August candidates. Lessons 19/21 (NS4/NS3 add-ons lost) set a sceptical prior, but each family is judged on its own controlled run — the census is not complete until NS5a is measured on premiums, and August needs new entries, not new exits (its stop legs go straight down; every exit family is closed).
- **The challenger (one structural change — an added component):** book v4 pool **plus admitted NS5a skill_rescan legs as add-ons** (admission: (date,direction) key unused by book v4; entry premium outside [400,550); exact-tag premium candles exist). Add-on legs take the book's current exit assembly (premium-gated runner: entry premium <400 → runner-lock50, ≥400 → plain G0). Everything else identical: entry = open of entry-bar candle, strike ATM nearest 100 to entry spot, expiry in force, lot 30, cost ₹220/trade, UNIQUE-ONCE.
- **Controls in the same run:** timing audit on every trade (NS5a entries checked against their signal times); placebo = same combined pool and exit assembly, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated.
- **Banking rule (same frozen standard as Cycles 3 and 6):** the challenger replaces the working book only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v4 (50.0%), with no secured month un-secured.

## Cycle 10 — CHALLENGER: NS5b ce_mirror_rescan add-on legs on book v4 (frozen 2026-10-31, BEFORE scoring)
- **Why a challenger:** protocol — 2 consecutive no-bank cycles on August (Cycles 8, 9) mandates a challenger. August (book v4) = 10 trades, −₹3,781: 7 stops, 1 plain target, 1 runner target150, 1 square-off; 9 PE / 1 CE, all base legs. Every exit family is closed (lessons 3, 4, 14, 16, 18) and August needs new entries, not new exits. The runner-gate refinement to [250,400) stays PARKED — it deterministically costs August its runner gain and is legitimate only once August is secured otherwise.
- **Diagnosis / census:** NS5b (CE mirror rescan: a CE leg mirrored from a confirmed PE-side rescan break) is a Bank family never premium-scored in this engine. Census stated in advance from the parked list: 28 Bank NS5b legs in the source file; admission under the book's rules (below) is expected to be thin (~8 admissible, remainder key-dropped / band-dropped / NOT_COMPUTED). Prior is sceptical: NS5b is all-CE, and CE add-on legs have repeatedly lost (lessons 2, 15, 22 — NS5a's losses were CE-concentrated). Each family is still judged on its own controlled premium run; this cycle completes the NS5 census either way.
- **The challenger (one structural change — an added component):** book v4 pool **plus admitted NS5b ce_mirror_rescan legs as add-ons** (admission: (date,direction) key unused by book v4; entry premium outside [400,550); exact-tag premium candles exist — NOT_COMPUTED legs excluded and counted, never substituted). Add-on legs take the book's current exit assembly (premium-gated runner: entry premium <400 → runner-lock50, ≥400 → plain G0). Everything else identical: entry = open of entry-bar candle, strike ATM nearest 100 to entry spot, expiry in force, lot 30, cost ₹220/trade, UNIQUE-ONCE.
- **Controls in the same run:** timing audit on every trade (NS5b entries checked against their signal times); placebo = same combined pool and exit assembly, entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated.
- **Banking rule (same frozen standard as Cycles 3, 6 and 9):** the challenger replaces the working book only if August improves AND total rises AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v4 (50.0%), with no secured month un-secured.

## RUN 2 — Cycle 1 (engine Cycle 11) — COLD-STATE (lA) STAND-ASIDE (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a NEW mechanism — a book-state-conditioned component stand-aside. It is not a re-try of any closed family: not an exit geometry (lessons 3, 4, 14, 16, 18), not an entry-premium gate/band (5, 17), not an add-on family (8, 19, 21, 22, 23), not a component subset (7 — a blanket (lA) drop was screened out in Run 1 precisely because (lA) earns overall; this rule KEEPS (lA) in warm state). State-gating an exit by entry premium banked in Cycle 7 (lesson 20) — this gates a component by the book's own trailing state, a different state variable and a different mechanism.
- **Diagnosis (book v4, from `bank_engine_cycle7_trades.csv`, scored outcomes only):** define the book's trailing-10 state at each leg = net of the last 10 book-v4 legs signalled before it (signal-stream window). (lA) v2 legs split perfectly by that state: **cold state (trailing-10 < 0): 6 legs, −₹10,320 — every one a full −50 stop (−₹1,720 × 6)**; warm state: 7 legs, +₹13,760. (lA) is a continuation/rescan rep: when the book's recent stream is losing, its continuation legs walk straight into the stop. August holds 4 of the cold (lA) stops (10, 17, 19, 31 Aug). Other reps do NOT show this pattern in cold state (Skill +₹499 over 11 cold legs, Volrix +₹760), so the rule is (lA)-specific, matching the diagnosis, not a blanket cold halt (a blanket halt would also break the frequency gate: 26 cold legs exist).
- **The one fix (book-level state rule on book v4):** for each leg in chronological order, compute the trailing-10 signal-stream net using only legs whose outcome is already known at this leg's entry (prior-day legs always; same-day legs only if their exit_time ≤ this leg's entry_time). **If at least 10 such legs exist and their net is < 0, and the leg's rep is (lA) v2, the leg is skipped.** Skipped legs still enter the signal-stream window for later legs (the state tracks the signal stream, not only taken trades — stated in advance). Everything else identical to book v4: pool (B2 base + NS1 second legs, CE second legs blocked, premium band [400,550) blocked), exits = premium-gated runner (entry premium <400 → runner-lock50, ≥400 → G0 −50/+90), entry = open of entry-bar candle, ATM nearest 100, lot 30, cost ₹220/trade, UNIQUE-ONCE.
- **Controls in the same run:** timing audit on every taken trade PLUS a state audit (assert every state-input leg exited at or before the decision leg's entry); placebo = the identical rule and assembly with every entry delayed +30 min (state computed on the delayed stream); halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum from the written trades file; NOT_COMPUTED count stated.
- **Banking rule (Run-2 standard):** bank only if total rises AND August improves AND no red month-end AND frequency ≥2/week AND FT does not collapse vs book v4 (50.0%), with no secured month un-secured. (Target-month rule: August is the current target and this mechanism is aimed at it.)

## RUN 2 — Cycle 2 (engine Cycle 12) — RATCHET-LOCK on the gated runner, book v5 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a NEW exit mechanism — a *progressive* (ratcheting) lock. Stop −50, first target +90 and second target +150 are all unchanged; what changes is that the runner's lock is not fixed at +50 but ratchets up after further progress. Not a re-try of any closed family: fixed lock50 full-runner (lesson 16, regime-taxed), the premium-gated fixed lock (banked Cycle 7, lesson 20 — this cycle builds on that banked assembly, it does not re-test it), stop/target sizes (3, 4, 14, 18), or the parked [250,400) premium-band refinement (a band variant, not used here). Consistent with lesson 20: cheap-premium legs (the only runner-eligible ones) have expansion headroom.
- **Diagnosis (book v5's runner legs, premium paths from the candle cache):** 8 legs exited at the +50 runner lock (+₹1,280 each). **6 of those 8 first reached ≥ entry+120 after the +90 trigger** and then fell back through +50 — the fixed lock leaves ₹1,200/leg (=(90−50)×30) on the table on exactly the legs that proved they could travel. The other 2 never reached +120 (59.2, 102.4) and are untouched by this rule. Risk stated in advance: a runner_target150 leg that touches +120, then dips to +90 before reaching +150, would exit at +90 (+₹2,480) instead of +150 (+₹4,280) — the controlled run decides the net.
- **The one fix (exit assembly on book v5; pool and the banked Cycle-11 state rule unchanged):** for runner-eligible legs only (entry premium <400), after the +90 trigger the lock starts at entry+50 as now; **once a subsequent bar's high reaches entry+120, the lock ratchets to entry+90 for all later bars** (the ratchet arms on the bar AFTER the +120 touch, the same next-bar convention as the original lock). Second target stays entry+150; square-off 15:10; stop checked before target on every bar. Legs with entry premium ≥400 keep plain G0, untouched. Full-target still counts a leg that touches +90.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly (book v5 stream + ratchet) with every entry delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated. Sanity gate inside the run: ratchet OFF must reproduce book v5 exactly (+₹56,796.50, 82 trades) before the ratchet result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v5 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured — in particular August (secured green in Cycle 11 at +₹3,099) and September (+₹1,737.50) must stay green and October must stay strongly positive. This is a book-level challenger win rule, not the target-month rule; July is not required to improve (its only runner leg never reached +120, so the mechanism does not act there — stated in advance).

## RUN 2 — Cycle 3 (engine Cycle 13) — RUNNER SECOND TARGET +180 on book v5 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** the runner's SECOND target is a distinct parameter of the banked Cycle-7 assembly and has never been varied in this channel. What lessons 3 and 18 closed is the PLAIN G0 target on the whole pool (+120/+150 fail; +75 fails — paths are bimodal for legs with no lock protection). A runner leg is a different animal: it is already locked at +50, so extending its second target risks only the lock value, not the −50 stop. This is also the exact extension the Nifty engine banked under full controls in its own channel (Cycle 8 there) — noted as a mechanism precedent only; Bank is judged on Bank's own controlled run.
- **Diagnosis (book v5 runner legs, candle paths):** 10 legs exited at runner_target150 (+₹4,280 each). Their post-trigger day maxima (entry-relative) were 157.5, 193.6, 220.9, 323.3, 347.9, 353.5, 375.4, 393.2, 439.4, 650.4 — 9 of 10 travelled at least +180 at some point in the session. If a leg reaches +180 before falling back to the +50 lock it gains +₹900 (=(180−150)×30); if it falls to the lock first it loses ₹3,000 vs the +150 exit. The path ORDER decides — that is what the controlled replay measures. (Cycle 12's lesson is respected: this diagnosis does not assume post-exit excursions are capturable; the replay keeps the leg in the market past +150, so the path after the +150 touch is genuinely the leg's own path.)
- **The one fix (exit assembly on book v5; pool, Cycle-11 state rule and the fixed +50 lock unchanged — the rejected ratchet is NOT stacked):** for runner-eligible legs only (entry premium <400), the runner's second target moves from entry+150 to **entry+180**. Initial stop −50, first target +90, lock +50 after the trigger, square-off 15:10, stop before target — all unchanged. Legs ≥400 keep plain G0. Full-target still counts a leg that touches +90.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly with entries delayed +30 min; halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: second target at +150 must reproduce book v5 exactly (+₹56,796.50, 82 trades) before the +180 result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v5 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,099 and September +₹1,737.50 stay green, October stays strongly positive).

## RUN 2 — Cycle 4 (engine Cycle 14) — BE-ARM on the ≥400 G0 segment, book v6 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a NEW protection mechanism for the only segment of the book that has none. Legs with entry premium ≥400 exit plain G0 — no lock, no trail. The mechanism: once the premium has progressed +50, the stop arms to entry (break-even) for the rest of the leg, target unchanged at +90. It is NOT the closed G6 break-even runner (lesson 4): G6 armed only AFTER the full +90 target was touched and extended the target to +150 — a winner-extension that gave back. This arm fires at HALF progress (+50), never extends anything, and applies only to the segment that has no runner. It is also distinct from stop-size changes (3, 4, 14): the initial stop stays −50 until progress is proven. The same mechanism banked in the Nifty channel (BE50, its Cycle 5) — precedent only; Bank is judged on Bank's run.
- **Diagnosis (book v5/v6 ≥400 legs, path-ordered):** 57 legs; **31 reached +50 progress before any stop breach.** Their G0 outcomes: 26 targets, 3 stops, 2 square-offs. The arm's arithmetic: a leg that reached +50, later dips to entry, and would have stopped converts −₹1,720 → −₹220 (+₹1,500); a leg that reached +50, dips to entry, and would have reached +90 converts +₹2,480 → −₹220 (−₹2,700). Which side dominates is a path question — the controlled replay decides. Stated in advance: the at-risk side (26 targets) is larger than the save side (3 stops), so this cycle is expected to be decided by how many of those 26 actually dip to entry after +50.
- **The one fix (exit assembly on book v6; pool, Cycle-11 state rule, gated runner with second target +180 all unchanged):** for legs with entry premium ≥400 only — **BE-arm: from the bar after the first bar whose high ≥ entry+50, the stop moves from entry−50 to entry** (next-bar convention, as with the locks). Stop checked before target on every bar; target +90 and square-off 15:10 unchanged. Exit reason recorded as `be_arm_stop` when the armed stop fires. Runner-eligible legs (<400) are untouched.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly (book v6 stream + BE-arm) with entries delayed +30 min; halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: arm disabled must reproduce book v6 exactly (+₹61,896.50, 82 trades) before the armed result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v6 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September +₹1,737.50 stay green; October stays strongly positive).

## RUN 2 — Cycle 5 (engine Cycle 15) — CHALLENGER: BLUE-LINE v4 add-on legs on book v6 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a genuinely NEW component family — the user's own 3-Blue-Line system (PDH/PDC/PDL levels, opening range, Red bands, four setups; `3-blue-line-bank-nifty-backtest-spec.md`), never tested as part of this book. It is not an NS rescan variant (lessons 8, 19, 21, 22, 23 close those): its signals come from prior-day levels and band structure, a different information source from every U1/NS component. Its own trade logs score it under ITS conventions (cost-trail, book-20) — those numbers are NOT used here; every admitted leg is re-scored under this book's conventions and exit assembly, the one-convention rule.
- **Census (stated in advance):** Blue-Line v4 traded legs Jan–Oct = 42 (month logs `trade_log_v4_t90.csv` Jan–Jun, `trade_log_v4_t50.csv` Jul–Oct — entries are target-independent because the system is one-and-done per day, so the entry set is the same across target variants). On (date,direction) keys unused by book v6: 21. None of the 21 is in the aggressive candle cache (NOT_COMPUTED there) — they are scored instead from the Blue-Line dataset's own `option_5m.csv` premium candles (same underlying Upstox premium data, monthly files, expiry carried per row). A leg whose series or entry bar is missing in `option_5m.csv` is NOT_COMPUTED, excluded and counted, never substituted.
- **Admission (book rules, same as Run-1 add-on cycles):** (a) (date, direction) key unused by the book-v6 taken book; (b) entry premium (open of the entry bar in `option_5m.csv`) outside the book's admission band [400,550); (c) exact premium series exists. At most one add-on per key (the source system trades at most one leg per day anyway). Add-on legs take the book's current exit assembly: entry premium <400 → runner-lock50 with second target +180 (book v6 assembly); ≥400 → plain G0 −50/+90.
- **The base book is unchanged:** book v6 (incl. the Cycle-11 state rule, applied to the base stream exactly as banked) is NOT re-decided; add-ons are admitted on top and do not enter the state rule's window retroactively.
- **Controls in the same run:** timing audit on every trade — base legs as before; add-on legs checked entry_time ≥ signal_time (both from the Blue-Line log) and entry premium = open of the entry bar in `option_5m.csv`, cross-checked against the log's own entry_premium (mismatches reported); placebo = combined stream with every entry delayed +30 min (base legs via the standard delayed scoring, add-ons via delayed replay in `option_5m.csv`); halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED count stated. Sanity gate inside the run: the base stream alone must reproduce book v6 exactly (+₹61,896.50, 82 trades).
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v6 (53.7%) AND no secured month is un-secured (August +₹3,999, September +₹1,737.50 stay green, October stays strongly positive). Frequency can only rise (legs are added).

## RUN 2 — Cycle 6 (engine Cycle 16) — RUNNER LOCK +75 on book v6 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** the runner's LOCK LEVEL has never been varied in this channel — Cycles 3 and 7 both used the +50 lock (full runner rejected in 3 for weak-month taxes; premium-gated +50 lock banked in 7). A lock level is not the initial stop (lessons 4, 14 close that) and not a target size (3, 18): it is the profit-protection level of the banked runner assembly, and the same variation banked in the Nifty channel (its Cycle 3, lock50 → lock75, FT held). One parameter of the banked assembly, tested on Bank's own controlled run.
- **Diagnosis (book v6):** 9 legs exited at the +50 runner lock (+₹1,280 each). Every one of them, by construction, fell through +75 on its way to +50 — under a +75 lock each exits at +₹2,030 instead (+₹750 × 9 = +₹6,750 if nothing else changes). The stated risk: any of the 9 runner_target180 legs (+₹5,180 each) whose path dipped to ≤ +75 after the +90 trigger before reaching +180 would be cut to +₹2,030 (−₹3,150 each); two such legs erase the gain. Path order decides — the replay measures it.
- **The one fix (exit assembly on book v6; pool, Cycle-11 state rule, second target +180 unchanged; the rejected ratchet and BE-arm are NOT stacked):** for runner-eligible legs only (entry premium <400), the post-trigger lock moves from entry+50 to **entry+75**. Initial stop −50, first target +90 (lock arms from the bar after the trigger, as before), second target +180, square-off 15:10, stop before target. Legs ≥400 keep plain G0. Full-target still counts a leg that touches +90.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly with entries delayed +30 min; halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: lock at +50 must reproduce book v6 exactly (+₹61,896.50, 82 trades) before the +75 result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v6 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September +₹1,737.50 stay green, October stays strongly positive).

## RUN 2 — Cycle 7 (engine Cycle 17) — RUNNER LOCK +90 on book v7 (frozen 2026-10-31, BEFORE scoring)
- **Why this cycle:** Cycle 16 banked the lock at +75 and left the lock curve's peak unmeasured in this channel: +50 → +75 gained. This cycle completes the curve (+75 → +90) under the same controls. It is the same new mechanism family as Cycle 16 (the runner lock level, never varied before Run 2), iterated once on the banked value — and it carries the peak rule stated in advance: **if +90 does not beat +75, the lock stays at +75 and the lock family is closed** (the Nifty channel's lock curve peaked at 75; Bank's is measured on Bank's own paths).
- **Diagnosis (book v7):** 9 legs exited at the +75 lock (+₹2,030 each); every one fell through +90 on its way down, so a +90 lock pays +₹2,480 on each (+₹450 × 9 = +₹4,050 if nothing else changes). The stated risk is the mirror of Cycle 16's: any runner_target180 leg (9 legs, +₹5,180) whose path dips to ≤ +90 after the trigger before reaching +180 is cut to +₹2,480 (−₹2,700 each); two such legs erase the gain, and Cycle 16 already showed one target leg (20 Jan) dips into the (50,75] band.
- **The one fix (exit assembly on book v7; everything else unchanged):** runner-eligible legs (entry premium <400) — post-trigger lock moves from entry+75 to **entry+90**. Initial stop −50, first target +90 (the lock arms from the bar after the trigger; note the lock level now equals the trigger level — a leg that triggers and then trades back to its trigger price exits there), second target +180, square-off 15:10, stop before target. Legs ≥400 keep plain G0.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: lock at +75 must reproduce book v7 exactly (+₹65,496.50, 82 trades) before the +90 result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v7 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September +₹2,487.50 stay green, October stays strongly positive).

## RUN 2 — Cycle 8 (engine Cycle 18) — WARM-STATE RUNNER for the ≥400 segment, book v7 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a new state-gated assembly — the runner is extended to the ≥400 segment ONLY in the book's warm state. Lesson 20 banked gating an exit by a state known at entry (entry premium); Cycle 11 banked gating a component by the book's trailing state. This cycle combines the two proven gating principles on a segment that has never had the runner in isolation: the full-pool runner (Cycle 3) was rejected because it taxed the target month on the old book — the ≥400-only, warm-only slice was never isolated, and the current book gives September (the month Cycle 3 taxed) a +₹2,487.50 cushion. The state variable is the SAME anchored state as the frozen Cycle-11 rule: trailing-10 net of book-v4 outcomes, known at entry (prior-day legs always; same-day only if exited by entry).
- **Diagnosis (book v7 ≥400 target legs, path replay with lock75/+180):** applying the runner to ≥400 legs in warm state only changes 24 legs for a diagnosed delta of ≈ +₹11,250 (7 legs travel to +180: +₹2,700 each; the rest fall to the +75 lock: −₹450 each). In cold state the same change is +₹2,250 on only 2 changed legs — noise, and lesson 16's regime warning (runners tax weak regimes) says not to run it there. September's one affected leg is taxed −₹450, leaving September green at ≈ +₹2,037.50.
- **The one fix (exit assembly on book v7; pool, Cycle-11 state rule, <400 assembly unchanged):** for legs with entry premium ≥400, **if the anchored trailing-10 state at entry is warm (net ≥ 0 over the last 10 known book-v4 legs; fewer than 10 known legs = warmup = warm), the leg exits by runner-lock75 with second target +180** (stop −50, trigger +90, lock +75 from the next bar, target2 +180, square-off 15:10); if the state is cold, the leg keeps plain G0 exactly as now. Legs <400 are untouched (their banked assembly: runner-lock75 + second target +180).
- **Controls in the same run:** timing audit on every trade (including the state audit — every state input exited at or before the decision leg's entry, as in Cycle 11); placebo = identical assembly with entries delayed +30 min (state computed on the delayed book-v4 stream, the Cycle-11 placebo convention); halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: warm gate disabled must reproduce book v7 exactly (+₹65,496.50, 82 trades).
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v7 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September must stay green, October stays strongly positive).

## RUN 2 — Cycle 9 (engine Cycle 19) — RUNNER SECOND TARGET +210, book-wide, on book v8 (frozen 2026-10-31, BEFORE scoring)
- **Why this cycle:** the runner's second target was banked at +180 in Cycle 13 (from +150) and Cycle 18 extended the runner to the ≥400 warm segment at that same +180. The target curve's peak is unmeasured beyond +180 — this cycle completes it, exactly as Cycle 17 completed the lock curve, with the same peak rule stated in advance: **if +210 does not beat +180, +180 stays and the runner-target family is closed.** One parameter, book-wide (both runner segments: <400 legs and warm-state ≥400 legs), everything else identical to book v8.
- **Diagnosis:** Cycle 13's <400 runner_target legs showed post-trigger session maxima of 193–650 (9 of 10 ≥ +180 at the time); Cycle 18's new ≥400 runner legs added 7 more +180 exits. Legs that reach +210 before falling to the +75 lock gain +₹900 each (=(210−180)×30); legs that fall to the lock first lose ₹3,150 vs the +180 exit. Path order decides.
- **The one fix:** runner second target entry+180 → **entry+210** for every runner leg in book v8's assembly. Initial stop −50, trigger +90, lock +75, square-off 15:10, stop before target, cold-state ≥400 legs keep plain G0, Cycle-11 state rule untouched.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: second target at +180 must reproduce book v8 exactly (+₹77,196.50, 82 trades) before the +210 result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v8 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September +₹2,487.50 stay green, October stays strongly positive).

## RUN 2 — Cycle 10 (engine Cycle 20) — SPEED-CONDITIONED SECOND TARGET on book v8 (frozen 2026-10-31, BEFORE scoring)
- **Why this is a valid Run-2 cycle:** a new conditioning variable for the runner assembly — **time-to-trigger** (bars from entry until the premium first touches +90), known causally at the moment the runner arms. Cycle 19 closed the unconditional target curve (+210 book-wide lost: 4 legs fell back). Diagnosis on book v8's 41 runner legs: fast triggers (≤2 bars, 13 legs) show post-entry maxima mostly far beyond +210 (9 of 13 ≥ 211, median ≈ 271) — momentum continuation; slow triggers (28 legs) include the shallow paths that fell back in Cycle 19. Conditioning the extension on trigger speed is a mechanism the closed families never used (entry gates conditioned on spot/premium state at entry; this conditions the exit on the leg's own realised path speed).
- **Diagnosis note (recorded, not cycled):** expiry-day legs in book v8 net **−₹2,510 over 8 legs** (5 full stops, 3 lock exits) — the Nifty EXP0 pocket exists in Bank too, but dropping 8 legs breaks the ≥2/week frequency gate (74 trades = 1.82/week) and no live add-on family exists to offset it. Parked as unbankable under the current gate, same status as the Run-1 [250,400) refinement.
- **The one fix (exit assembly on book v8; everything else unchanged):** for every runner leg (both segments — <400 legs and warm-state ≥400 legs), **if the +90 trigger is touched within the first 3 bars of the leg (entry bar = bar 0, i.e. trigger bar index ≤ 2), the second target is +210; otherwise it stays +180.** Lock +75, initial stop −50, trigger +90, square-off 15:10, stop before target, cold-state ≥400 legs keep plain G0, Cycle-11 state rule and Cycle-18 warm gate untouched.
- **Controls in the same run:** timing audit on every trade; placebo = identical assembly with entries delayed +30 min (trigger speed measured on the delayed path); halves; month table with month-end closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated. Sanity gate inside the run: fast-target set equal to slow-target (+180) must reproduce book v8 exactly (+₹77,196.50, 82 trades) before the conditioned result is read.
- **Banking rule (Run-2 standard, book-level challenger leg):** bank only if total rises AND no red month-end AND FT does not collapse vs book v8 (53.7%) AND frequency unchanged (2.02/week) AND no secured month is un-secured (August +₹3,999, September +₹2,487.50 stay green, October stays strongly positive).

## DECEMBER CANDIDATE — engine book v8 (frozen verbatim at Run-2 termination, 2026-10-31)
Judged on fresh December data in the Bank channel; November paper BNF-PAPER-V1 is a different, separately frozen spec and is untouched.
- **Pool:** V1 = B2 base legs + NS1 second legs, UNIQUE-ONCE (date, direction), earliest entry; then block NS1 CE second legs; then block legs whose entry premium (entry-bar open) is in [400, 550).
- **Entry-side state rule:** anchored state = trailing-10 net of book-v4 outcomes over the signal stream (legs signalled before this leg whose exits were known at its entry; prior-day legs always known, same-day only if exited by entry time). Skip a leg if it is an (lA) v2 leg AND the state is cold (≥10 known legs and net < 0).
- **Exits (stop −50, first target +90, stop checked before target, square-off 15:10):**
  - Entry premium < 400 → runner: after the +90 trigger, lock at entry+75 (arms from the bar after the trigger bar), second target entry+180, else square-off.
  - Entry premium ≥ 400 → if the anchored state is warm (net ≥ 0, or fewer than 10 known legs) the same runner applies; if cold, plain G0 (no runner).
- **In-sample record (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade):** +₹77,196.50, 82 trades, FT 53.7%, 2.02/week, no red month-ends; months Jan +14,730 / Feb +13,320 / Mar +16,780 / Apr +5,010 / May +14,440 / Jun −6,570 / Jul −9,250 / Aug +3,999 / Sep +2,487.50 / Oct +22,250. Trades: `bank_engine_cycle18_trades.csv`. Real money: ₹0 (paper/backtest only).

## SESSION 2026-11-02 (floor-target session) — Cycle 21 — SEGMENT-SPLIT SECOND TARGET: +210 for the <400 segment only, on book v8 (frozen 2026-11-02, BEFORE scoring)
- **Context:** new session objective (Chandu, 2026-11-02): Bank Nifty alone must reach a ₹15,000/month pace = ≥ ₹1,50,000 Jan–Oct 2026 gated. Incumbent book v8 = +₹77,196.50 (gap ₹72,803.50). Frequency is at the gate floor (82 trades, 2.02/week — dropping even one leg breaks ≥2/week), so this session works exit-side and state-side only.
- **Why this is a valid cycle:** Cycle 19 tested second target +210 BOOK-WIDE and was rejected (−₹2,700): 11 legs reached +210, 4 fell back to the lock. Session diagnosis (2026-11-02, exact per-leg replay on book v8) splits that result by the book's own frozen segment boundary: on ≥400-warm legs +210 loses −₹5,850 (4 reach, 3 fall back), but on **<400 legs +210 gains +₹3,150 (7 reach +₹900 each, 1 fall back −₹3,150 — the 26 Oct CE leg)**. The book-wide rejection mixed a losing segment into a winning one; the segment-split was never scored. Consistent with lesson 20 (cheap premiums have expansion headroom) and contradicted by no lesson — lessons 31/32 close the BOOK-WIDE and speed-conditioned forms, not the segment-split form.
- **The one fix (exit assembly on book v8; pool, Cycle-11 state rule, anchored states, all other parameters unchanged):** runner legs with **entry premium < 400** get second target **entry+210** (was +180). Lock stays entry+75, trigger +90, initial stop −50, square-off 15:10, stop before target. ≥400 legs (warm runner / cold G0) are byte-identical to book v8.
- **Controls in the same run:** sanity gate (base parameters must reproduce book v8 exactly: 82 trades, +₹77,196.50); timing audit on every trade; placebo = identical assembly with entries delayed +30 min; halves Jan–May / Jun–Oct; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no month-end close goes red AND no green month flips red AND FT does not fall (FT is invariant here by construction — the +90 trigger touch is unchanged) AND frequency unchanged (2.02/week) AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 22 — SEGMENT-SPLIT LOCK +90 for the ≥400-warm segment only, on book v9 (frozen 2026-11-02, BEFORE scoring)
- **Why this is a valid cycle:** the runner lock curve was measured only on the <400 segment (Cycles 16–17: +50 → +75 banked, +75 → +90 rejected, family closed THERE). The ≥400-warm segment got its runner in Cycle 18 at the +75 lock without its own lock curve ever being measured. Session diagnosis (exact replay on book v8, unchanged by Cycle 21 which touches only <400 legs): lock +90 on ≥400-warm legs = **+₹4,500** (16 lock exits +₹450 each, 1 target leg — 16 Mar — cut −₹2,700). Expensive-premium legs that trigger +90 and retrace tend to fall straight through the (75,90] band to the lock or beyond — different path geometry from the <400 segment, so the <400 peak does not bind here (lesson 35's segment principle).
- **The one fix (exit assembly on book v9; everything else unchanged):** for legs with entry premium ≥400 in warm anchored state (the legs that take the runner under Cycle 18's rule), the post-trigger lock moves from entry+75 to **entry+90** (arms from the bar after the trigger bar, as before — a leg that triggers and then trades back to its trigger price exits there at +₹2,480, the plain-target value). Second target stays entry+180. <400 legs keep their book-v9 assembly (lock +75, second target +210); ≥400 cold legs keep plain G0.
- **Controls in the same run:** sanity gate (base parameters must reproduce book v9 exactly: 82 trades, +₹80,346.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall (invariant by construction — trigger touch unchanged) AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 23 — RUNNER-OFF GATE for ≥400-warm legs entered in [550,750), on book v10 (frozen 2026-11-02, BEFORE scoring)
- **Why this is a valid cycle:** session diagnosis (exact G0-vs-runner replay per leg on book v8) split the ≥400-warm runner's value by premium sub-band: [750,1000) +₹9,900, ≥1000 +₹3,600, but **[550,750) −₹1,800 over 8 legs — the only negative runner pocket in the book**. The [400,550) entry block (Cycle 4, banked) makes [550,750) the cheapest admitted expensive band; its legs behave like the dead zone's neighbours — dear enough to decay, not directional enough to run. Gating an exit assembly by an entry-known state is this book's proven mechanism class (lessons 20, 30); the sub-band split of the ≥400 runner was never measured. (The diagnosis was taken against the lock-75 assembly; Cycle 22 has since banked lock +90 for this segment, so this cycle measures the pocket on the current book — the controlled run decides.)
- **The one fix (exit assembly on book v10; everything else unchanged):** ≥400-warm legs with **entry premium in [550,750)** exit by **plain G0** (stop −50 / target +90, square-off 15:10) instead of the runner. All other legs byte-identical to book v10 (<400: lock +75 / second target +210; ≥400-warm outside the band: lock +90 / second target +180; ≥400-cold: G0).
- **Controls in the same run:** sanity gate (base parameters must reproduce book v10 exactly: 82 trades, +₹84,846.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 24 — SECOND-TARGET CURVE COMPLETION: +240 for the <400 segment, on book v10 (frozen 2026-11-02, BEFORE scoring)
- **Why this cycle:** Cycle 21 banked +210 for the <400 segment, leaving that segment's target curve unpeaked (the frozen peak rule, lessons 29/31: measure the curve until it turns, then close the family). Session diagnosis (exact replay on book v10): +240 changes 7 legs — **all 7 reach it (+₹900 each, +₹6,300 total), zero fall back to the lock.** The 7 legs are the same ones that reached +210 in Cycle 21; their paths run far beyond +240. ≥400 segments are untouched (their +210 split was diagnosed −₹5,850 in Cycle 21's diagnosis and stays closed).
- **The one fix (exit assembly on book v10; everything else unchanged):** runner legs with entry premium < 400 get second target **entry+240** (was +210). Lock stays entry+75, trigger +90, initial stop −50, square-off 15:10, stop before target. ≥400 legs byte-identical to book v10 (warm: lock +90 / target +180; cold: plain G0).
- **Controls in the same run:** sanity gate (base must reproduce book v10 exactly: 82 trades, +₹84,846.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall (invariant by construction) AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 25 — SECOND TARGET +270 for the <400 segment, on book v11 (frozen 2026-11-02, BEFORE scoring)
- **Why this cycle:** the <400 target2 curve paid at +210 (Cycle 21) and +240 (Cycle 24) with zero fall-backs; the peak rule requires measuring until it turns. Because a parameter that pays at every step is a leak warning under the controls-gate skill, the 7 affected legs were first verified independently of the replay: strikes/expiries are the correct weekly contracts, entry premiums match the stored legs to the paisa, and each leg's post-trigger path was walked bar by bar — maximum premium reached before any dip to the +75 lock: +650.4 / +393.2 / +439.4 / +353.5 / +375.4 / +323.3 / +347.9. No leak: these are genuine trend-day paths, and the verified clean maximum of the weakest leg (+323.3, 21 Oct) bounds the curve. Diagnosis of this step on book v11: +₹6,300 (7 reach, 0 fall back).
- **The one fix (exit assembly on book v11; everything else unchanged):** <400 runner second target +240 → **+270**. Lock +75, trigger +90, stop −50, square-off 15:10 unchanged; ≥400 legs byte-identical (warm lock +90 / target +180; cold G0).
- **Controls in the same run:** sanity gate (base must reproduce book v11 exactly: 82 trades, +₹91,146.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall (invariant by construction) AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 26 — SECOND TARGET +300 for the <400 segment, on book v12 (frozen 2026-11-02, BEFORE scoring)
- **Why this cycle:** the curve's last provably-clean step. The Cycle-25 leak-check verification walked all 7 affected legs' paths: the weakest (21 Oct) reaches +323.3 before any dip to the lock, so every leg reaches +300 with the same certainty the +270 step had; beyond +300 the outcome depends on one leg's square-off path and the peak must be measured, not assumed. Diagnosis of this step on book v12 (from the v11 walk): +₹6,300 (7 reach, 0 fall back).
- **The one fix (exit assembly on book v12; everything else unchanged):** <400 runner second target +270 → **+300**. Lock +75, trigger +90, stop −50, square-off 15:10 unchanged; ≥400 legs byte-identical (warm lock +90 / target +180; cold G0).
- **Controls in the same run:** sanity gate (base must reproduce book v12 exactly: 82 trades, +₹97,446.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall (invariant by construction) AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## Session 2026-11-02 — Cycle 27 — SECOND TARGET +330 for the <400 segment (the curve's turning step), on book v13 (frozen 2026-11-02, BEFORE scoring)
- **Why this cycle:** the peak rule — a curve is closed by measuring the step that turns, not by assuming it. Exact diagnosis on book v13: +330 = **+₹820.50 net** (6 legs reach +330 at +₹900 each; the weakest verified leg, 21 Oct — clean maximum +323.3 — instead exits at its 15:10 close for +₹4,200.50, −₹4,579.50 vs its +300 exit). The next step is already diagnosis-closed: +360 = −₹10,879.50 (two rocket legs fall back to the lock, −₹6,750 each). So +330 is the last grid step that can bank, and its margin is thin and single-leg-dependent — stated in advance; the scored gate decides, and if it banks, the family closes at +330 with that thinness on record.
- **The one fix (exit assembly on book v13; everything else unchanged):** <400 runner second target +300 → **+330**. Lock +75, trigger +90, stop −50, square-off 15:10 unchanged; ≥400 legs byte-identical (warm lock +90 / target +180; cold G0).
- **Controls in the same run:** sanity gate (base must reproduce book v13 exactly: 82 trades, +₹103,746.50); timing audit on every trade; placebo = identical assembly, entries delayed +30 min; halves; full month table with month-end cumulative closes; ex-top-3 stress; independent re-sum; NOT_COMPUTED stated.
- **Banking rule (session standard):** bank only if total rises AND no red month-end AND no green month flips red AND FT does not fall (invariant by construction) AND frequency unchanged AND both halves ≥ 0 AND placebo beaten AND audit clean.

## DECEMBER CANDIDATE — engine book v14 (frozen verbatim at the 2026-11-02 session's termination; supersedes the book-v8 candidate above)
Judged on fresh December data in the Bank channel; November paper BNF-PAPER-V1 is a different, separately frozen spec and is untouched.
- **Pool:** V1 = B2 base legs + NS1 second legs, UNIQUE-ONCE (date, direction), earliest entry; then block NS1 CE second legs; then block legs whose entry premium (entry-bar open) is in [400, 550).
- **Entry-side state rule:** anchored state = trailing-10 net of book-v4 outcomes over the signal stream (legs signalled before this leg whose exits were known at its entry; prior-day legs always known, same-day only if exited by entry time). Skip a leg if it is an (lA) v2 leg AND the state is cold (≥10 known legs and net < 0).
- **Exits (stop −50, first target +90, stop checked before target, square-off 15:10):**
  - Entry premium < 400 → runner: after the +90 trigger, lock at entry+75 (arms from the bar after the trigger bar), second target entry+330, else square-off.
  - Entry premium ≥ 400 → if the anchored state is warm (net ≥ 0, or fewer than 10 known legs) runner with lock at entry+90 and second target entry+180; if cold, plain G0 (no runner).
- **In-sample record (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade):** +₹104,567.00, 82 trades, FT 53.7%, 2.02/week, no red month-ends; months Jan +23,730 / Feb +23,670 / Mar +15,880 / Apr +6,360 / May +15,340 / Jun −6,120 / Jul −9,250 / Aug +8,499 / Sep +2,487.50 / Oct +23,970.50 (Jun/Jul negative as individual months; every month-end cumulative close positive). Halves +₹84,980 / +₹19,587. Placebo (+30 min) +₹10,830.70. Ex-top-3 +₹75,527. Trades: `bank_engine_cycle27_trades.csv`. Real money: ₹0 (paper/backtest only).

---

# ROUND 2 — floor-target continuation (frozen 2026-11-02, BEFORE any Round-2 scoring)

**Order (Chandu, 2026-11-02):** no saturation conclusions; work different use cases, combinations and permutations until the goal (≥ ₹1,50,000 Jan–Oct 2026 gated pace, premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE) is achievable. Starting point: **book v14 = +₹104,567.00** (82 trades, FT 53.7%, 2.02/week). Round-1 scored families are not re-run except as ingredients in combinations. November primary/spec/logs untouched (read-only).

**Working-book representation.** Exits are parameterised per segment: `lt400` (entry premium <400), `ge400_warm` (≥400, anchored state warm), `ge400_cold` (≥400, cold → plain). A segment's geometry = (stop S, trigger/first-target T, lock L or none, second target T2). Book v14: lt400 = (50, 90, 75, 330); ge400_warm = (50, 90, 90, 180); ge400_cold = (50, 90, plain). Generalised runner replay: phase 1 stop entry−S checked before trigger entry+T on every bar incl. entry bar (FT = trigger touched); from the bar AFTER the trigger bar, stop = entry+L (or stays entry−S when L = none) and target = entry+T2; stop before target in phase 2; square-off 15:10 close. Plain: stop entry−S, target entry+T, square-off 15:10. The replay records also whether +90 was touched (FT90). Anchored state and cold-(lA) stand-aside exactly as frozen for book v14 (state from the book-v4 scored stream of the pool in force; for pool variants the stream is rebuilt from that pool under the v4 assembly: runner-lock50 <400 / G0 ≥400).

**Banking rule (Round-2 standard, every candidate):** bank only if ALL hold vs the working book: net rises; no red month-end; no month that is net-positive in the working book turns net-negative; FT90 does not fall below the working book's FT (53.7% at v14) and FT at the variant's own trigger ≥ FT90; frequency ≥ 2/week on taken trades; both halves (Jan–May / Jun–Oct) ≥ 0; placebo (identical construction, entries +30 min) beaten; timing audit 0 violations; independent re-sum matches to the paisa; NOT_COMPUTED = 0 on the taken book. Cells that fail are recorded with the leg they failed — a gated verdict, not a narrative.

**Family R2-1 — EXIT-GEOMETRY GRID (fixed v14 leg set).** S ∈ {40, 50, 60} × T ∈ {75, 90, 105} × L ∈ {none, 50, 75, 90}; T2 stays at the segment's working value (330 lt400 / 180 ge400). Modes: A = cell applied to lt400 only; B = cell applied to ge400_warm (runner params) and ge400_cold (S/T as plain stop/target); AB = cell applied to all segments (cold takes S/T plain). 36 cells per mode, 108 total, all scored against book v14 as the fixed reference with full controls per cell. The single best gate-passing cell (highest net) is family 1's banked outcome if any passes; cross-mode stacking is Family R2-5.

**Family R2-2 — NS1 PERMUTATIONS (pool rebuilt).** Second legs regenerated from spot with the frozen generator's logic (`newsetups_score.py`: base S1 spot exit by target/stop with exit bar ≤13:30; first fresh OR-level crossing after the exit bar; CE crossing on a bearish-bias day blocks the second leg; first-candidate discipline — a first crossing that fails the room test ends the search), changing ONLY: room_ratio minimum ∈ {1.3, 1.4, 1.5 (frozen), 1.6}, signal window end ∈ {14:00, 14:30 (frozen), 15:00}, second-leg strike ∈ {ATM (frozen), 100 ITM}. Sanity: at frozen parameters the regenerated second-leg keys+strikes must reproduce the book's current NS1 second legs exactly before any variant is read. Pool per variant: B2 base legs + variant second legs → UNIQUE-ONCE → drop NS1 CE → drop entry-premium band [400,550) → anchored states rebuilt → cold-(lA) skip → working-book exits. Cells: room sweep at (14:30, ATM); window sweep at (1.5, ATM); strike at (1.5, 14:30); then the best combination of the three axes. Premium candles missing for a leg → that leg is NOT_COMPUTED, excluded and counted (a variant whose taken book has NC > 0 cannot bank).

**Family R2-3 — ENTRY-SIDE PERMUTATIONS (pool rebuilt, re-pooled from stored component candidates).**
(a) (lA) rescan cutoff ∈ {11:30, 12:30} (13:30 frozen): (lA) v2 candidates with signal_time > cutoff are removed before pooling.
(b) Bias thresholds (bearish cut, bullish cut) ∈ {(40, 85), (30, 75)} vs frozen (35, 80), bias = prev-day closing strength (close−low)/(high−low)×100: V5-v2 candidates (the pool's only bias-aligned component, per `index_options_v2_frozen.md`) are removed when their direction is not allowed under the variant day's bias (bearish → PE only; bullish → CE only; neutral → both). Admission-side effects (legs a looser gate would have generated) do not exist in stored candidates and are recorded as such, not invented.
(c) Expiry-day strike rule: legs whose date equals their expiry are re-scored at 100 ITM (CE strike −100, PE strike +100) under working-book exits; all other legs unchanged; missing candles → NOT_COMPUTED named.
Re-pooling: candidates per (date, direction) from the stored component files (o1 (lA)+V5 tracks, Skill V3 jansep, Volrix jansep, October per-system files); UNIQUE-ONCE earliest entry; then B2 filters (Skill V3 CE blocked; Skill-solo legs with entry ≤09:55 dropped), band block, states, exits — identical downstream to Family R2-2.

**Family R2-4 — USE-CASE POCKETS.**
(a) Jun/Jul PE bleed: a conditional geometry for PE legs under a mechanical bleed signature (features known at entry: prev-day spot return, day gap, anchored state, entry hour — the signature is frozen in the cycle entry AFTER the feature diagnosis is printed and BEFORE the pocket is scored; a month-named rule is forbidden). Variants frozen with the signature.
(b) Expiry-day pocket: legs with date == expiry get, in turn: plain G0 (−50/+90) regardless of segment/state; (−40/+90); (−50/+75). Stand-aside is not a cell (frequency-blocked by construction).
(c) Wide-candle rejection standalone: Blue-Line v4 legs with setup_type containing "setup3" from the monthly v4 logs (t90 Jan–Jun / t50 Jul–Oct), admitted on (date, direction) keys unused by the working book, entry premium outside [400,550), premium series present in the Blue-Line dataset's option_5m.csv; exits = working-book assembly (segment by entry premium; ≥400 uses the anchored state at that leg's entry on the working stream); re-scored from option_5m.csv under book conventions (Cycle 15 scored setup3 only inside the pooled Blue-Line mix on book v6 — standalone on the current book is unscored).

**Family R2-5 — COMBINATIONS.** Stack the best passing ingredient from each family (singly-scored first), pairwise then jointly, each stack re-gated in full against the then-working book. One change at a time within a family; combinations only from individually gated ingredients.

**Round-2 freeze correction (2026-11-02, before any Round-2 cell was scored):** the banking rule's FT clause is read as: FT90 (the share of legs touching +90, the reference level) does not fall below the working book's FT, AND the variant's own-trigger FT is reported alongside. The literal clause "FT at the variant's own trigger ≥ FT90" is unsatisfiable for trigger +105 cells by monotonicity (FT@105 ≤ FT90 always) and would auto-fail a whole grid row without evidence; the FT90 comparison is the level-consistent control that prevents buying net with a lowered trigger (a +75 trigger inflates its own FT mechanically, FT90 does not move).

**Family R2-4(a) bleed signature — frozen 2026-11-02 AFTER the feature diagnosis was printed and BEFORE the pocket was scored.** Diagnosis (v16 book, 69 PE legs): Jun/Jul PE legs = 14 legs / −₹15,680.00 / 12 losers; 10 of the 14 are anchored-state COLD legs netting −₹13,000.00; prev-day-return and gap signatures do not isolate the bleed (prevret ≤ −0.5% catches 5 Jun/Jul legs, net −₹200). **Signature: a PE leg whose anchored state at entry is cold (≥10 known stream outcomes, trailing-10 net < 0)** — mechanical, known at entry, no month names. 17 signature legs Jan–Oct, net −₹1,053.50 under v16. Conditional geometries for signature legs only (all other legs keep the working assembly): (a) plain G0 (−50/+90); (b) plain (−60/+90); (c) plain (−40/+90). Gated vs book v16 (+₹106,517.00) under the Round-2 banking rule.

---

# ROUND 2 ENDING BOOK — engine book v16 (frozen 2026-11-02; December candidate, supersedes book v14)

**Book v16 = book v15 + expiry-day legs take plain G0 (Cycle 39, BANKED). Book v15 = book v14 + <400 runner trigger +105 (Cycle 28 grid cell, BANKED).** Trades: `bank_engine_r2c41_stack_trades.csv` (independent re-sum matched: 82 trades / +₹106,517.00).

Definition: pool V1 (B2 + NS1 second legs) → UNIQUE-ONCE → NS1 CE second legs blocked → entry premium in [400,550) blocked → anchored trailing-10 state on the book-v4 scored stream → cold-state (lA) v2 stand-aside. Exits (entry = open of the entry bar's 5-min option candle; stop checked before target on every bar; square-off 15:10):
- entry premium <400 → runner: stop −50, trigger **+105**, lock +75 from the bar after the trigger bar, second target +330;
- entry premium ≥400, state warm → runner: stop −50, trigger +90, lock +90, second target +180;
- entry premium ≥400, state cold → plain: stop −50, target +90;
- **expiry-day legs (trade date == the leg's expiry) → plain: stop −50, target +90, regardless of segment/state.**

Controlled scorecard (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade): **+₹106,517.00**, 82 trades, 2.02/week, FT90 53.7% (own-trigger FT 52.4% — the <400 arm sits at +105), no red month-ends, months: Jan +28,080.00 · Feb +24,120.00 · Mar +15,880.00 · Apr +6,810.00 · May +15,340.00 · Jun −6,120.00 · Jul −13,000.00 · Aug +8,499.00 · Sep +2,487.50 · Oct +24,420.50; halves Jan–May +₹90,230.00 / Jun–Oct +₹16,287.00; placebo (+30 min) +₹18,365.20 beaten; ex-top-3 +₹77,477.00; timing audit 0 violations; NOT_COMPUTED 0. Pace ₹10,651.70/month vs the ₹15,000/month floor — **gap ₹43,483.00**. Round-2 record: `bank_engine_round2_2026-11-02.md`; the enumerated Round-2 space is exhausted at this book. The November primary (BNF-PAPER-V1) is a different, frozen construction and is NOT changed by this freeze.

# ROUND 3 — targeted techniques (frozen 2026-11-02, BEFORE any Round-3 scoring)
Mandate (Chandu, 2026-11-02 ~12:59 IST): the engine does not stop until the floor is met — Bank Nifty ≥ ₹1,50,000 Jan–Oct 2026 gated pace (₹15,000/month). Starting book: **v16 = +₹106,517.00** (gap ₹43,483.00). Rounds 1–2 spaces (exit grids, NS1 permutations, entry permutations) are NOT re-run. Basis unchanged: premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0. The November primary/spec/logs are untouched.

**Banking gate (every Round-3 cycle, vs the current best book; start ref = v16):** the `bank_r2_core.gate` standard — net strictly greater; no red month-ends; no month that is green in the ref flips red; FT90 not below ref; frequency ≥ 2.0/week; both halves (Jan–May / Jun–Oct) ≥ 0; placebo (identical construction, entries +30 min) beaten; timing audit 0 violations; taken-book NOT_COMPUTED = 0; independent re-sum from the written trades file matches to the paisa.

**Add-on admission (all Round-3 add-on families, the Cycles 8–10/15 convention):** a leg is admitted only if (a) its (date, direction) key is unused by the current best book's taken legs, (b) its entry premium (open of the entry-bar 5-min option candle) is outside the admission band [400, 550), and (c) its exact-tag premium candles exist in the cache. Legs failing (c) are NOT_COMPUTED: excluded, counted and named — never scored from spot or from any proxy. Legs failing (b) are band-dropped and counted. At most one add-on leg per (date, direction) key per family (the family's earliest signal).

**Add-on exit assembly:** admitted add-ons take the CURRENT best book's exit assembly (at Round-3 start, v16): segment by entry premium with the anchored trailing-10 state computed from the BASE book's stream only (Cycle-11 definition: base-stream legs signalled before the add-on whose exits were known at the add-on's entry; add-ons do not enter the state window — Cycle-15 precedent; the base book is not re-decided); entry premium <400 → runner (stop −50, trigger +105, lock +75, second target +330); ≥400 warm → runner (stop −50, trigger +90, lock +90, second target +180); ≥400 cold → plain (−50/+90); a leg whose trade date equals its expiry → plain (−50/+90) regardless of segment/state. The base book's own legs keep their frozen v16 outcomes exactly (sanity: any Round-3 book containing the base must reproduce +₹106,517.00 / 82 legs for the base subset).

## Workstream 1 — the unscored add-on legs (Cycles 42–44)
The Cycles 8/9/10 censuses left legs NOT_COMPUTED for missing premium candles: NS3 14, NS5a 19, NS5b 17 (census reproduced exactly by `bank_r3_census.py`, 2026-11-02). Those candles are fetched via the Upstox expired-instruments route (browser User-Agent) into `historical_proof_data/`. Each family is then judged TWICE, both under full controls in the same run:
- (i) **Completed census:** the family's full admissible set (post-fetch) added to book v4 under the Cycles 8–10 frozen definitions — the verdict the partial samples (NS3 6 legs −₹2,127; NS5a 12 legs −₹4,047; NS5b 8 legs −₹1,160) could not give.
- (ii) **Banking test:** the family's admissible set (admission vs the v16 taken keys) added to book v16 under the add-on assembly above; banked only on the banking gate vs v16.

## Workstream 2 — mechanised unbuilt setups (Cycles 45+)
Signals are regenerated mechanically from stored 5-min spot (`data/banknifty-2026-*/spot_5m.csv`) + prior-day lines from `spot_daily.csv`; definitions below are frozen before any of them is scored. Common rules (Chandu's root method / v4): bias from prior-day closing strength (<35 bearish PE-only; 35–79 neutral both; ≥80 bullish CE-only); entry window ≤14:30; room ≥200 pts measured on the v4 level set (PDH/PDC/PDL + band edges where bands exist); entry = open of the first 5-min option candle strictly after the signal candle; strike = ATM nearest 100 to the signal close, except on the monthly expiry day (trade date == expiry in force) where it is 100 pts ITM (CE −100, PE +100); one signal per family per day (the family's first).

- **Setup 3 — wide-candle bounce rejection (PE).** Common: bias bearish; bounce flag = some 5-min candle's high enters [ORH, max(ORH, band_high_max)+100]; with no user-supplied bands in the regeneration, band_high_max = ORH, so the bounce zone is [ORH, ORH+100]. Room (R1/R2 readings) = signal close − blocking, blocking = PDC if close > PDC else PDL, ≥200 required.
  - **S3-A (frozen v4 code reading):** OR width ≥ 400 (no upper edge, as coded in v4 final); rejection R1 = first red candle (close < open) closing below ORH after the bounce flag.
  - **S3-B:** OR width ∈ [350, 580]; rejection R1.
  - **S3-C:** OR width ∈ [400, 650]; rejection R1.
  - **S3-D (wick rejection):** OR width ∈ [400, 580]; the signal candle IS the first bounce candle: its high enters the bounce zone, upper wick (high − max(open, close)) ≥ 1.5 × body (|close − open| > 0), close < ORH and close < open.
  - **S3-E (close-back-inside PDC):** OR width ∈ [400, 580]; rejection = first red candle closing below PDC after the bounce flag; room = close − PDL if close > PDL, else close − (day's lowest low up to and including the signal bar); ≥200 required.
- **Setup 4 — gap-down bear-trap / Blue-Line reclaim (CE).** Blue Lines = PDH/PDC/PDL (the spec's definition). Day opens below PDC AND below PDL. Reclaim leg: first 5-min close > ORH and > PDC and > PDL and < PDH, room ≥200 to the next level above → CE (setup4_reclaim). Pullback leg (only if no reclaim leg was taken that day by this family): after a reclaim close has occurred, a later candle whose low is within 40 pts of PDC or PDL and which closes above that level on a green candle, room ≥200 → CE (setup4_pullback). This is the v4 construction isolated as its own family (Cycle 15 tested all Blue-Line setups pooled; setup 4 alone was never gated).
- **Red bands from intraday spot + Setup 1 retest-hold (CE).** Band derivation (mechanical, causal, frozen): from the prior 10 trading days' 5-min spot bars — a swing high is a bar whose high strictly exceeds the highs of the 3 bars before and after it; a swing high is a REJECTED resistance print if, within the next 12 bars, price falls ≥150 pts from it with no 5-min close above it in between; rejected prints within 50 pts of each other (single-linkage) cluster into a band [cluster min, cluster max] widened by ±15 pts; a band is LIVE for day D if no 5-min close after its newest member's formation and before D's open exceeded the band high, and its high is above D's open; at most the 3 nearest live bands (by band low) are used. Setup 1 on these bands (v4 rules verbatim): an opening-range candle (09:15/09:20/09:25) closes ≥ band_lo − 10 → band broken; a post-09:30 candle with low in [band_lo − 50, band_hi] and close > band_hi → retest held; the next green candle closing above ORH with room ≥200 to the next level above (levels = PDH/PDC/PDL + live band edges) → CE signal. Bias must allow CE.

## Workstream 3 — execution optimisation on the v16 legs (Cycles 51+)
Premium-honest variants of the v16 book only (pool, filters, state rule, segments, geometry levels, expiry-day override all frozen; only the named execution convention changes):
- **EC-A (close entry):** entry price = CLOSE of the frozen entry bar; the exit scan starts on the NEXT bar; stop/trigger/lock/second-target measured from the new entry price; square-off 15:10 at that bar's close. Placebo: identical, entry at the close of the bar 6 bars after the frozen entry bar, scan from the next bar.
- **EC-B (next-bar open):** entry = OPEN of the bar after the frozen entry bar; exit scan from that bar (inclusive); geometry from the new entry price; square-off 15:10. Placebo: +30 min in the same convention.
- **SQ-1445 / SQ-1500 / SQ-1520:** square-off time moves from 15:10 to 14:45 / 15:00 / 15:20: bars after the square-off bar are ignored; a leg still open at the square-off bar exits at that bar's close; all else frozen. Placebo: +30-min entries under the same square-off.
Sanity inside every WS3 run: the frozen convention (entry-bar open, square-off 15:10) must reproduce v16 to the paisa before the variant is read.

## Workstream 4 — combinations
Any Round-3 banking stacks onto the then-current best book; the stack is re-gated as a whole book against the previous best before it becomes the new best (the Round-2 Cycle-41 form). New best books are frozen verbatim in this file with their controlled scorecard.

**Round-3 amendment (2026-11-02, noted BEFORE any Workstream-2 scoring):** the Setup-4 day-open condition has two documented readings — the spec text ("opens below PDC/PDL", frozen above as S4) and the v4 code as written (`day_open < pdc` only). Both are tested as separate families: **S4** = spec reading (below both lines); **S4B** = v4 as-coded reading (below PDC only, PDL condition dropped); all other Setup-4 rules identical. Reason recorded: a definition ambiguity in the source material, flagged on signal counts only — no WS2 candidate had been scored when this was noted.

# ROUND 3 RESULT — book v17 FROZEN (2026-11-02, supersedes v16 as December candidate)
**Book v17 = book v16 with the end-of-day square-off moved from 15:10 to 15:20** (Round-3 Cycle 57, BANKED under the full gate vs v16: net strictly greater, FT90 unchanged, no month flips, halves ≥ 0, placebo beaten, timing audit clean, NOT_COMPUTED 0, independent re-sum matched). Everything else is v16 verbatim: pool, filters, anchored trailing-10 state, segment runner curves (<400: −50/+105/lock +75/tgt2 +330; ≥400 warm: −50/+90/lock +90/tgt2 +180; ≥400 cold: plain −50/+90), expiry-day legs plain G0. Trades file: `bank_engine_r3_v17_trades.csv`. The square-off point is non-monotonic: 14:45 also passed (+₹107,871.50) and 15:00 failed (+₹104,795.00) — 15:20 is the best of the frozen set {14:45, 15:00, 15:10, 15:20}.

Controlled scorecard (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade): **+₹107,930.00**, 82 trades, 2.02/week, FT90 53.7%, no red month-ends, months: Jan +29,163.00 · Feb +24,120.00 · Mar +15,880.00 · Apr +6,810.00 · May +15,340.00 · Jun −6,120.00 · Jul −13,000.00 · Aug +8,806.50 · Sep +2,321.00 · Oct +24,609.50; halves Jan–May +₹91,313.00 / Jun–Oct +₹16,617.00; placebo (+30 min, same convention) +₹18,380.50 beaten; ex-top-3 +₹78,890.00; timing audit 0 violations (82 entry bars checked); NOT_COMPUTED 0; independent re-sum 82 trades / +₹107,930.00 ✓. Pace **₹10,793.00/month** vs the ₹15,000/month floor — **gap ₹42,070.00**. Round-3 record: `bank_engine_round3_2026-11-02.md`. The November primary (BNF-PAPER-V1) is NOT changed by this freeze.

**FLAGGED — awaiting Chandu's decision (NOT banked; the FT90 gate leg is not mine to waive):** the Round-3 combination stack **v17 + NS3 + S3-A + S3-E** (Cycle 63) scores **+₹127,369.50** (108 trades, ₹12,736.95/month, gap to floor ₹22,630.50) and passes every gate leg except FT90: 52.8% vs the 53.7% reference — one full-target leg short (57 of 108; 58 needed). Halves +₹105,741.00 / +₹21,628.50; placebo +₹15,367.50 beaten; ex-top-3 +₹98,329.50; no red month-ends; no month flips; timing clean; NOT_COMPUTED 0. Subset v17 + NS3 alone (Cycle 58): +₹122,609.50, FT90 52.5%, all other legs pass. If Chandu waives the FT90 leg (the Nifty CH3-R precedent), the Cycle-63 stack becomes the December candidate verbatim from `bank_r3_ws4_results.json` + the family definitions frozen in the Round-3 appendix above.

# ROUND 4 APPENDIX — definitions frozen 2026-11-02 BEFORE any Round-4 scoring (Cycles 64+)

Base = book v17 (frozen above). Stack composition = the flagged Cycle-63 form: sequential admission NS3 → S3-A → S3-E → S3-D under the Round-3 add-on admission rules, add-ons under the v17 assembly, square-off 15:20. Reproduced exactly by `bank_r4_core.py` before any Round-4 candidate was read: +₹127,369.50 / 108 trades / FT90 57 (52.8%), placebo +₹15,367.50 — identical to Round 3's Cycle 63. Gate = the Round-2 banking gate vs v17 unless a cycle states a different reference; stack variants are additionally reported against the flagged stack's controls. Diagnosis (`bank_r4_diag.py`, `bank_r4_diag.json`) preceded this freeze; every threshold below is taken from that diagnosis and is not revised after scoring begins.

## WS1 — NS3's own exit geometry (Cycles 64–81)
Every admitted NS3 leg (admission unchanged) is scored with ONE uniform parameter set — the family's own geometry replacing the v17 segment assembly wholesale, including the expiry-day plain rule: stop −50 (fixed; the stop axis is closed, lessons 4/14), first target trig ∈ {+75, +90}, runner lock ∈ {+40, +50, +65}, second target ∈ {+130, +150, +175}, square-off 15:20. 18 cells. Each cell is gated in two assemblies: (a) v17 + NS3@cell alone; (b) the full stack with NS3@cell (S3 families keep the book assembly). FT90 remains the path measure (premium touching +90 while the leg is alive, either phase).

## WS2 — NS3 admission refinement (Cycles 82–88)
Subsets of the NS3 candidate pool, one axis at a time, applied BEFORE admission; each gated as a full stack variant vs v17. Frozen cells, from the admitted-19 distribution in the diagnosis (admitted legs are all outside the [400,550) band by construction; DTE = calendar days, trade date → expiry; source = the NS3 subleg label):
- premium: (i) entry premium < 400 only; (ii) entry premium ≥ 550 only.
- DTE: (iii) DTE ≥ 1 (expiry-day legs dropped); (iv) DTE ≤ 7; (v) DTE > 7.
- source: (vi) NS3-GD only; (vii) NS3-GD + NS3-GU (NS3-FLAT dropped).

## WS3 — Setup-3 completion (Cycles 89+)
Generator `bank_r4_setups.py`: a parameterised clone of the Round-3 Setup-3 generator, asserted to reproduce the S3-A / S3-D / S3-E leg sets exactly at (wick 1.5, depth 0). New cells, all at the frozen (400, 580) OR band with every other Round-3 rule unchanged:
- S3-F: WICK, wick ≥ 2.0 × body. S3-G: WICK, wick ≥ 1.25 × body.
- S3-H: R1 with close-back-inside depth ≥ 25 (close < open, close < ORH, ORH − close ≥ 25).
- S3-I: R1 with depth ≥ 50.
- S3-J: PDC with depth ≥ 25 (close < open, close < PDC, PDC − close ≥ 25).
Each cell is gated standalone first (v17 + the cell as the only add-on family, Round-3 admission, book assembly); any cell whose family net is positive is then also gated inside the flagged stack (admitted after S3-D).

## WS4 — near-miss conversion audit (diagnosis recorded; at most one candidate)
Audit of the flagged stack (premium MFE measured entry bar → exit bar): converted legs (premium touched +90 while alive) = 57; near-miss legs (ft90 = 0, MFE ∈ [75, 90)) = exactly 3, all BASE PE legs: 2026-06-09 (MFE 89.9, stopped; full-day path max also 89.9 — the path never reached +90), 2026-07-14 (MFE 81.2, stopped 11:10; full-day path max +104.0 — the only path that reached +90 after its exit), 2026-08-27 (MFE 80.55, alive to the 15:20 square-off — no later path exists). Separator criterion, frozen before its application: a binary feature separates iff (a) its in-group near-miss rate is ≥ 2× the out-group rate, (b) it holds ≥ 2 of the 3 near-misses, (c) its in-group share of converted legs is < 60%. Application to the brief's three axes: entry premium ≥ 550 — rates 7.9% vs 0%, holds 3/3, converted share 61% → FAILS (c). Entry before 11:00 — 6.8% vs 0%, 3/3, 72% → FAILS (c). DTE ≥ 14 — 10.3% vs 0%, 3/3, 46% → SEPARATES. The single permitted candidate is therefore: stack legs with DTE ≥ 14 keep their own exit assembly with the stop widened −50 → −65 (the lesson-4 wider-stop value; trig/lock/second target/square-off unchanged), gated as a full stack variant vs v17. No second WS4 candidate exists under any outcome.

## WS5 — entry-state features on the stack (admission filters, whole stack)
Features from stored 5-min spot (`bank_r3_setups` data), frozen: range30(D) = spot high−low over bars with time < 09:45 on D; trailMed(D) = median of range30 over the prior 20 trading days (defined when ≥ 10 prior days exist); gap%(D) = (D's first-bar open − prior trading day's close) / prior close; tercile cuts from the Jan–Oct gap distribution (191 days): T1 ≤ −0.210%, T2 (−0.210%, +0.139%], T3 > +0.139%. Variants (legs on dates where a feature is undefined are admitted unconditionally; for the range condition, legs entering before 09:45 are admitted unconditionally — the feature completes at 09:45): (a) admit only range30 ≤ trailMed; (a′) admit only range30 > trailMed; (b) drop legs on gap-T3 dates; (b′) drop legs on gap-T1 dates. Each gated as a full stack variant vs v17; the same filter applies to the placebo twin's rows by (date, entry_time).

## WS6 — combinations
Every variant that passes the full gate vs v17 banks and becomes the reference for later cycles (the Round-2 Cycle-41 / Round-3 WS4 form); combinations of passing variants are re-gated as whole books vs v17 AND reported vs the flagged stack's numbers. The flagged stack itself remains NOT banked unless a Round-4 variant passes all gate legs including FT90 on its own merits or Chandu waives FT90.

# ROUND 4 RESULT (interim) — book v18 FROZEN (2026-11-02, supersedes v17 as December candidate)
**Book v18 = book v17 + NS3 restricted to the NS3-GD + NS3-GU sublegs (the NS3-FLAT legs are not admitted) + S3-A + S3-E**, sequential admission under the Round-3 rules, v17 exit assembly, square-off 15:20 (Round-4 Cycle 88, BANKED under the full gate vs v17 — every leg passes including FT90). Composition: base 82 legs; NS3(GD+GU) 17 admitted (+₹15,358.00, FT90 9); S3-A 6 (+₹2,280.00); S3-E 1 (+₹2,480.00); S3-D 0 admitted after key consumption. The NS3-FLAT exclusion removes the family's only FT90-dilutive, net-negative source slice (diagnosis: FLAT 2 admitted legs, −₹678.50, FT90 0/2).
Controlled scorecard (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade): **+₹128,048.00**, 106 trades, 2.61/week, FT90 53.8% (57/106), no red month-ends, months: Jan +30,893.00 · Feb +26,878.00 · Mar +21,600.00 · Apr +5,090.00 · May +23,000.00 · Jun −5,360.00 · Jul −13,650.00 · Aug +8,806.50 · Sep +6,181.00 · Oct +24,609.50; halves Jan–May +₹107,461.00 / Jun–Oct +₹20,587.00; placebo +₹9,960.50 beaten; ex-top-3 +₹99,008.00; timing audit 0 violations; NOT_COMPUTED 0; independent re-sum 106 / +₹128,048.00 ✓. Trades file: `bank_engine_r4_v18_trades.csv`. Pace **₹12,804.80/month** vs the ₹15,000/month floor — **gap ₹21,952.00**. Also passing all gate legs vs v17 in the same workstream (recorded, not displacing v18 — lower net): Cycle 82 NS3 premium <400 stack (+₹119,818.00, 95 trades, FT90 54.7%); Cycle 85 NS3 DTE ≤7 stack (+₹117,820.00, 95 trades, FT90 54.7%); Cycle 87 NS3-GD-only stack (+₹127,288.00, 104 trades, FT90 53.8%). The November primary (BNF-PAPER-V1) is NOT changed by this freeze.

# ROUND 4 RESULT — book v19 FROZEN (2026-11-02, supersedes v18 as December candidate)
**Book v19 = book v18 with the NS3(GD+GU) legs scored on NS3's own exit geometry T90/L65/G175** (Round-4 Cycle 102, BANKED under the full gate vs v17 AND passing the displacement gate vs v18): v17 base (v17 assembly, square-off 15:20) + NS3 restricted to the NS3-GD + NS3-GU sublegs, those legs scored with stop −50 / first target +90 / runner lock +65 / second target +175 / square-off 15:20 + S3-A + S3-E under the book assembly, sequential admission under the Round-3 rules. Composition: base 82 legs; NS3(GD+GU)@own-geometry 17 admitted (+₹21,208.00, FT90 9); S3-A 6 (+₹2,280.00); S3-E 1 (+₹2,480.00); S3-D 0 admitted after key consumption.
Controlled scorecard (Jan–Oct 2026, premiums per 1 lot of 30, cost ₹220/trade): **+₹133,898.00**, 106 trades, 2.61/week, FT90 53.8% (57/106 — passes the FT90 leg on its own merits), no red month-ends, months: Jan +30,893.00 · Feb +26,878.00 · Mar +20,850.00 · Apr +5,090.00 · May +22,850.00 · Jun −5,360.00 · Jul −11,400.00 · Aug +8,806.50 · Sep +10,681.00 · Oct +24,609.50; halves Jan–May +₹106,561.00 / Jun–Oct +₹27,337.00; placebo +₹11,211.50 beaten; ex-top-3 +₹104,858.00; timing audit 0 violations; NOT_COMPUTED 0; independent re-sum 106 / +₹133,898.00 ✓. Trades file: `bank_engine_r4_v19_trades.csv`. Pace **₹13,389.80/month** vs the ₹15,000/month floor — **gap ₹16,102.00**. The Round-3 Cycle-63 FLAGGED stack (+₹127,369.50, FT90-only failure) is superseded and its waiver question is moot: v19 passes every gate leg including FT90 at a higher net, with no waiver. The November primary (BNF-PAPER-V1) is NOT changed by this freeze.

# ROUND 5 APPENDIX — definitions frozen 2026-11-02 BEFORE any Round-5 scoring or audit measurement (Cycles 115+)

Starting book = v19 (frozen above; +₹133,898.00, gap to the ₹1,50,000 floor pace ₹16,102.00). Gate = the Round-2 banking gate (net > ref AND no red month-ends AND no green→red month flip AND FT90 ≥ ref AND frequency ≥ 2.0/week AND both halves ≥ 0 AND placebo beaten AND timing audit clean AND NOT_COMPUTED = 0 AND independent re-sum exact), reference = the AUDITED baseline produced by WS0 (v19 itself if the audit is clean; the causal rebuild if it is not). Premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE, square-off 15:20 everywhere. November primary untouched.

## WS0 — admission-causality audit of v19 (Cycle 115; precedes all other Round-5 work)

Certificate standard (the Nifty Round-5 WS0 model; Nifty lesson 46): for every leg in `bank_engine_r4_v19_trades.csv`, every admission condition the leg relied on must have been fully knowable at its recorded entry bar, using each source system's own signal time — not a later same-day event. Conditions in scope: the leg's own system signal; pool membership; UNIQUE-ONCE representative selection; the B2 filters (Skill-CE block, Skill-solo ≤09:55 drop); the premium-band [400,550) block; the trailing-state machinery (cold-(lA) skip; warm/cold segment state); NS1 preconditions (S1 exit by target/stop with exit ≤ 13:30, first fresh OR crossing after the exit, room_ratio ≥ 1.5, CE bearish-bias block); the NS3 gap-class definitions; the S3 definitions; bias state; DTE.

Violation classes, frozen before measurement:
- **V-NS (entry-time quirk, NS1/NS3 source legs):** the source CSVs' `entry_time` field is the generating spot replay's exit-bar field (`newsetups_score.replay` returns the exit bar's time on stop/target exits). A leg whose recorded premium entry_time is LATER than its source system's own entry bar (signal bar + 1, i.e. signal_time + 5 min) had its entry bar selected by the spot trade's exit — an event completing inside that later bar, not knowable at that bar's open. Causal re-reading: entry at the system's own entry bar (signal_time + 5 min). Strikes are unchanged (they derive from the true entry spot, the signal+1 bar's open). Legs whose spot trade exited on its own entry bar have recorded entry = own entry and are clean.
- **V-SK (Skill early-confirmation):** a kept base leg whose representative system is Skill V3 with entry_time ≤ 09:55 and whose non-solo status (the B2 keep condition) was established only by another system whose own entry bar on that key is LATER than the leg's entry bar (second-earliest system entry t2 > entry_time, t2 recovered from the U1 merge's own input files). At the entry bar the leg was solo; its survival used a later same-day event. Causal re-reading: the leg is dropped. (t2 == entry_time — confirmation complete at the entry bar — is clean.)
- Any further condition found to rely on a later same-day event is named as found, with the same treatment.

Causal rebuild (only the violated classes are corrected; everything else is the identical frozen pipeline): pool rebuilt with NS1/NS3 source legs carrying causal entry times and V-SK legs removed before UNIQUE-ONCE; then UNIQUE-ONCE → NS1-CE block → premium-band block → book-v4 scored stream → anchored trailing states → cold-(lA) skip → v17 exit assembly at square-off 15:20 → sequential admission NS3(GD+GU) @ T90/L65/G175 → S3-A → S3-E under the Round-3 rules. Full controls in the same run (timing + feature-timing audit, placebo, halves, month table, ex-top-3, independent re-sum). The causal book is the Round-5 reference for ALL gating; v19 remains the December candidate of record, annotated with the audit's quantified effect (the Nifty Round-5 disposition). If the audit finds no violation, the certificate is stated explicitly and the reference is v19 verbatim.

Certificates to verify per leg (expected clean): (lA)/V5/Skill representatives enter strictly after their own signal bar; Volrix trigger = the prior trading day's close (return ≤ −1.0% at the frozen cell) with entry 09:20; bias everywhere = the prior trading day's closing strength; `state_at` counts only legs whose exit_time ≤ the decision leg's entry_time on the same day (earlier dates in full); the premium band and segment assignment read the leg's own entry-bar open — the fill price, known at the fill (the book's frozen convention; the same standard as strike-at-entry); an admitted add-on's (date, direction) key has no base leg at any time of day, so the kept add-on set is identical under causal admission; S3 entries are the signal bar + 5 min by construction (`bank_r3_setups.mkleg`); DTE is calendar.

## WS1 — v19 wound diagnosis (Cycle 116; at most one candidate, Cycle 117)

On the AUDITED baseline's trades: month table; the 10 worst legs; loss decomposition by family (BASE pool member by representative system, NS1, NS3, S3) × direction × bias-day state (bearish cs < 35 / neutral / bullish cs ≥ 80, prior-day closing strength). A conditional candidate is permitted ONLY if a binary causal feature separates under the Round-4 WS4 criterion, adapted: (a) its in-group share of the wound (the baseline's negative legs in its two worst months) is ≥ 2× its in-group share of the book's legs, (b) it holds ≥ half the wound legs, (c) its in-group share of the book's full-target legs is < 60%. The single candidate is an admission exclusion of the signature population OR a state-conditioned exit on it, stated when frozen in the round log before scoring, gated vs the audited baseline. No separator → record and close; no second candidate.

## WS2 — NS1 permutations on the audited baseline (Cycles 118–121)

Second legs regenerated from stored spot with the frozen generator's logic (`bank_r2_ns1.gen_ns1`), with the WS0 causal entry convention (entry = crossing bar + 1) that the audited baseline itself carries. One axis at a time at the other axis's frozen value: room_ratio minimum 1.4 (window 14:30); room 1.6 (window 14:30); window end 14:00 (room 1.5); window end 15:00 (room 1.5). Strike = ATM at the spot entry (frozen convention, no ITM cells this round). Each cell: full pool rebuild (base + regenerated seconds → UNIQUE-ONCE → NS1-CE block → premium band → stream → states → cold-(lA) skip → v17 assembly @ 15:20) with the audited baseline's add-on stack re-admitted on top (NS3(GD+GU) @ own geometry, S3-A, S3-E), gated vs the audited baseline. Sanity asserted before scoring: at (1.5, 14:30) the regenerated second-leg set (date, direction, strike, expiry) equals the audited baseline's NS1 set, with entry times equal wherever the baseline is uncorrected.

## WS3 — Skill-solo early-leg re-admission (Cycles 122–124)

Population (enumerated from data at audit time, recorded in the round report): legs in the U1 Bank pool file (`index_options_U1_B1_bank_trades.csv`) with source_systems exactly "Skill V3", entry_time ≤ 09:55, absent from the B2 pool — the population the B2 Skill-solo ≤09:55 rule dropped. Strike/expiry per the frozen Jan–Sep convention (ATM at entry spot, monthly expiry) or as recorded (October premium rows). Cells, one at a time: (a) PE legs only; (b) CE legs only; (c) legs of either direction whose room_ratio at their own signal bar ≥ 1.5 — room_ratio per `newsetups_score.room_ratio` (levels = prior-day PDH/PDC/PDL; close = the signal bar's close; risk = |entry_spot − stop_spot| from the leg's source record; October legs: the source record's stop if present, else the signal bar's extreme from stored spot). Re-admitted legs join the pool BEFORE UNIQUE-ONCE (a solo leg is alone on its key among base systems, so dedup keeps it; collision with an NS1 second on the same key resolves by earliest entry as usual); the B2 Skill rules under test are NOT re-applied to them; every other book rule applies (premium-band block, stream, states, cold-(lA) skip for (lA) reps only, base exit assembly, stack admission on top). Gated vs the audited baseline.

## WS4 — Volrix-Bank grid (Cycles 125–132)

Volrix (b) Bank legs regenerated from stored daily spot: trigger day = a trading day whose close-to-close return ≤ thr; entry = the next trading session at 09:20; strike = ATM nearest 100 to the TRIGGER day's close; expiry = the monthly expiry in force for the entry date (the EXPIRIES convention); direction CE only; cooldown = consecutive Volrix entries at least cd trading sessions apart (session-index difference ≥ cd) over the Volrix stream, applied before pooling. Cells = the full cross thr ∈ {−0.75%, −1.0%, −1.25%} × cd ∈ {5, 10, 15}; the (−1.0%, 10) cell is the frozen point and MUST reproduce the frozen Volrix Bank leg set exactly (asserted as sanity before any variant is scored; failure of the sanity stops the workstream and is reported, not worked around). Each variant cell: the U1 pool rebuilt from the merge's component inputs with the variant Volrix set in place of the frozen one (all other components verbatim), B2 construction applied (the rule set verified exactly against B1→B2 at audit time), then the identical downstream pipeline as WS2 (NS1 seconds frozen, stream, states, cold skip, assembly, stack), gated vs the audited baseline.

## WS5 — bias-conditioned exit split (Cycles 133–134; two cells maximum)

Bias state of a leg's date = the prior trading day's closing strength cs (bearish cs < 35; neutral 35 ≤ cs < 80; bullish cs ≥ 80) — known at the day's open. Applied book-wide (base + add-ons) on the audited baseline via re-scoring of matching legs, square-off 15:20 unchanged:
- Cell A: legs on bearish-bias days whose exit assembly has a runner (lock not None) get lock := +40 (trig and second target unchanged; plain legs unchanged).
- Cell B: legs on bullish-bias days whose exit assembly has a second target (tgt2 not None) get tgt2 := +130 (trig and lock unchanged; plain legs unchanged).
Each gated vs the audited baseline.

## WS6 — combinations (Cycles 135+)

Any Round-5 variant that passes the full gate vs the audited baseline banks and becomes the reference for later cycles in this round; combinations of banked variants are re-gated as whole books vs the audited baseline and reported against the then-current best. If WS0 re-baselined, displacements are additionally reported against v19's recorded numbers with the WS0 annotation attached.

ROUND 5 SANITY ADDENDUM (recorded during WS0/WS4 machinery validation, before
any Round-5 scoring): (1) Volrix (b) premium strikes as built by the proof are
ATM at the ENTRY spot (09:20 bar open), not the trigger-day close stated in
the U1 October doc — verified against all 12 Jan–Sep B2-file strikes (e.g.
2026-01-22: 59300 = ATM(59,316.30 entry spot); trigger-close ATM would be
58700). The WS4 grid therefore uses entry-spot ATM, matching the book's
construction. (2) The frozen Volrix set's 2026-06-01 leg is NOT reproducible
from stored daily data (trigger-day return −0.924% vs the −1.0% threshold;
regeneration fires 2026-06-02 instead) — the WS0 calibration note. WS4 cells
are regenerated sets; the frozen-cell cell is reported with this exception
named, per the Nifty Round-4 calibration precedent.
(3) The frozen October Volrix leg (2026-10-26, strike 54300) uses trigger-day
close ATM (Oct 23 close 54,3xx), unlike the Jan–Sep legs' entry-spot ATM
(Oct 26 entry-spot ATM would be 53900) — a mixed construction basis in the
frozen book, both strikes causal at entry. WS4 regeneration is uniform
entry-spot ATM; the frozen-cell comparison names both exceptions
(2026-06-01 calibration, 2026-10-26 strike basis).

=====================================================================
BOOK v20 FREEZE (Round 5, Cycle 135, 2026-11-02) — AUDITED LINEAGE.
SUPERSEDES v19 AS THE DECEMBER CANDIDATE OF RECORD.
v19's freeze above STANDS AS RECORDED (+₹133,898.00) but is WS0-ANNOTATED:
the Round-5 admission-causality audit (Cycle 115, evidence
bank_r5_ws0_audit.json) found 39 of its 106 legs violating admission
causality (9 V-SK later-confirmed early Skill legs, +₹25,320 recorded;
30 V-NS NS1/NS3 legs timed by exit-bar entry_time fields, +₹43,149
recorded). ₹63,957.50 (47.8%) of v19's recorded net was non-causal
entry-timing value. Do not quote v19's figures without this annotation.
=====================================================================
Book v20 = the WS0 causal rebuild of v19 (causal-solo B2 pool; NS1 and
NS3 legs entered at signal+5; NS3 restricted to GD+GU on its own geometry
T90/L65/G175; S3-A + S3-E sequential admission; square-off 15:20; book
assembly unchanged) with ONE change: the Volrix (b) pool member is the
REGENERATED set at trigger −1.0% / cooldown 15 sessions (11 legs; trigger
= prior-session close-to-close ≤ −1.0%, entry next session 09:20, strike
ATM at entry spot, monthly expiry in force) instead of the frozen file
set. Banked Cycle 129 vs the audited baseline; final whole-book re-gate
Cycle 135 PASS vs REF_AUD and chained vs Cycle 127.
Result: 99 legs, +₹78,250.50 Jan–Oct 2026. FT90 49.5%, 2.44/week, no red
month-ends, halves +₹62,688.00/+₹15,562.50, placebo −₹4,313.50 beaten,
ex-top-3 +₹49,210.50, NOT_COMPUTED 0, timing audit clean, independent
re-sum exact. Months: Jan +22,748 · Feb +20,480 · Mar +1,120 · Apr −90 ·
May +18,430 · Jun +560 · Jul −8,780 · Aug −873.50 · Sep +9,726.50 ·
Oct +14,929.50. Trades: bank_engine_r5_v20_trades.csv; controls:
bank_r5_v20_freeze.json. Pace ₹7,825.05/month vs the ₹15,000 floor —
gap ₹71,749.50, floor NOT met.
Audited baseline (REF_AUD) for the record: 102 legs, +₹69,940.50,
FT90 48.0%, trades bank_engine_r5_causal_trades.csv, controls
bank_r5_ref_aud.json.
=====================================================================
BOOK v21 FREEZE (Round 6, Cycle 149, 2026-11-02) — AUDITED LINEAGE.
Book v21 = book v20 with ONE change: the NS3 add-on family's exit
geometry is stop −50 / trig +90 / lock +50 / tgt2 +150 (was lock +65 /
tgt2 +175 in v20). The NS3 admission is unchanged (GD+GU sublegs only,
causal signal+5 entries; the FLAT exclusion was re-tested causally at
Cycle 137 and holds). Everything else is v20 verbatim: causal-solo B2
pool, NS1 regenerated second legs, Volrix (b) regenerated at trigger
−1.0% / cooldown 15, S3-A + S3-E sequential admission, square-off
15:20. Banked Cycles 138/139/140 vs v20 (one axis; C140 the peak);
final whole-book re-gate Cycle 149 PASS vs v20 and chained vs C139
and C138.
Result: 99 legs, +₹83,650.50 Jan–Oct 2026. FT90 49.5%, 2.44/week,
no red month-ends, halves +₹61,938.00/+₹21,712.50, placebo
−₹4,313.50 beaten, ex-top-3 +₹54,610.50, NOT_COMPUTED 0, timing
audit clean, independent re-sum exact. Months: Jan +22,748 ·
Feb +20,480 · Mar +1,120 · Apr −90 · May +17,680 · Jun +560 ·
Jul −3,680 · Aug −873.50 · Sep +10,776.50 · Oct +14,929.50.
Trades: bank_engine_r6_v21_trades.csv; controls:
bank_r6_v21_freeze.json. Pace ₹8,365.05/month vs the ₹15,000
floor — gap ₹66,349.50, floor NOT met. v21 supersedes v20 as the
December candidate of record.


## ROUND 7 ADDENDUM (2026-11-02) — NO BANKING; BOOK v21 STANDS

Round 7 (Cycles 150–161) gated the five axes never touched on causal
data against v21 and banked nothing: V5 knobs (min_target ₹250/₹1,000,
cap_index 5/2) are exact no-ops after an exact regeneration validation;
the (lA) CE mirror sleeve nets −₹8,622 on Bank's own population
(rejected, June flip, FT90 dilution); Skill OR 09:15–09:45 loses
₹5,656 and flips June (frozen-window regeneration validated exact
first); strike ITM-100 loses blanket (−₹9,480.50) and expiry-day-scoped
(−₹4,200.00, FT90 dilution) at NC 0; square-off 15:20 is confirmed as
the causal peak of {15:10, 15:20, 15:25}. No combination arose (empty
banking set). **Book v21 above is unchanged and remains the December
candidate of record: +₹83,650.50, pace ₹8,365.05/month, gap ₹66,349.50
to the ₹15,000 floor — NOT met.** Causality certificate for the round:
every candidate was scored on the frozen causal entries with the full
controls gate in the same run (timing violations 0, NC 0 throughout);
the two regeneration validations (V5 Cycle 150, Skill Cycle 156)
reproduced their frozen leg sets exactly before any variant was
trusted. Full record: bank_engine_round7_2026-11-02.md.

=====================================================================
# ROUND 8 — DECEMBER CANDIDATE: engine book v21, FULL TRADEABLE SPECIFICATION
(Frozen 2026-11-02, Round-8 Cycle 166, BEFORE the Cycle-167 regeneration
verification and BEFORE any December data exists. This block is the
December candidate of record: it supersedes the v8/v14/v19/v20 change-note
blocks as the operative December specification. Judged on fresh December
2026 data in the Bank channel. The November primary BNF-PAPER-V1 is a
different, separately frozen spec and is NOT touched by this block.)
=====================================================================

## 1. Basis
Index-options premiums per 1 lot (Bank lot 30); cost ₹220/trade;
UNIQUE-ONCE per (date, direction), earliest entry; entry price = open of
the 5-min premium candle at the entry bar; entry strike = ATM nearest 100
to the entry spot (each family's convention in §2–§3/§7 where it differs);
square-off 15:20 (a leg still open exits at the 15:20 bar's close);
paper only, real money ₹0.

## 2. Base pool — B2 in its causal form
Components, each per its frozen U1 construction, each leg entering at its
own system's entry bar:
- (lA) v2, V5 v2, Tuned Skill V3 legs from the systems' own records.
- Volrix (b) — the REGENERATED rule (the v20/v21 pool member, not the
  frozen leg file): trigger = a trading session whose close-to-close
  return ≤ −1.0%; entry = the NEXT session at 09:20; strike = ATM nearest
  100 to the entry session's 09:20 bar open; expiry = the monthly expiry
  in force; direction CE only; cooldown — consecutive Volrix entries at
  least 15 sessions apart over the Volrix stream, applied before pooling.
Pool construction (causal-solo B2, in this order):
(i) drop any Skill V3 leg with entry_time ≤ 09:55 that has NO other-system
    leg on its (date, direction) key entering at or before it — solo
    status judged AS OF the leg's entry bar, never end-of-day;
(ii) UNIQUE-ONCE per (date, direction): the earliest-entry leg is the
    representative;
(iii) drop a pooled leg whose representative is Skill V3 with direction CE.

## 3. NS1 second legs (regenerated form; at most one per day)
Base S1 spot trade exits by target or stop with exit-bar time ≤ 13:30.
Second signal = the first fresh crossing of either opening-range level
after the base exit bar (a bar closes above ORH with the previous bar not
above ORH → CE; below ORL likewise → PE), signal time ≤ 14:30,
room_ratio ≥ 1.5 at the crossing (the frozen cell — Round 8 gated the
neighbours: room 1.25 and 1.75 are exact no-ops, window 15:00 is rejected;
neither neighbour is part of this candidate). A CE crossing on a
bearish-bias day (prior-day closing strength < 35) ends the search
unfilled; a first crossing that fails the room test also ends the search
(first-candidate discipline). Entry = the bar AFTER the crossing bar;
entry premium = that bar's open; strike = ATM nearest 100 to the entry
spot; expiry = monthly in force.

## 4. Pool filters (after §2 + §3 are pooled and UNIQUE-ONCE applied)
- Drop every NS1 second leg with direction CE.
- Drop every leg whose entry premium (its entry-bar open) is in [400, 550).

## 5. Signal stream, anchored state, stand-aside, segments
The pooled legs form the signal stream, each scored under the §6 assembly.
A leg's anchored state = the last ≤10 stream legs known at its entry:
prior-day legs always known; same-day legs only if their exit_time ≤ this
leg's entry_time. State = (count known, net of those legs).
- Cold-(lA) skip: a leg whose representative is (lA) v2 is SKIPPED when
  ≥10 known legs exist and their net < 0. Skipped legs still enter the
  stream window for later legs (the state tracks the signal stream).
- Segment of a taken leg: entry premium < 400 → lt400; otherwise warm
  (net ≥ 0, or fewer than 10 known legs) → ge400_warm; else ge400_cold.

## 6. Exit assembly (base + NS1 legs)
Stop checked before target on every bar including the entry bar;
square-off 15:20.
- lt400: stop −50; trigger +105; from the bar AFTER the trigger bar the
  stop locks at entry+75; second target entry+330.
- ge400_warm: stop −50; trigger +90; lock entry+90 from the bar after the
  trigger bar; second target entry+180.
- ge400_cold: plain — stop −50, target +90.
- Expiry-day override: a leg whose trade date equals its expiry takes
  plain −50/+90 regardless of segment.
FT90 counts a leg whose premium touches +90 while it is alive.

## 7. Add-on stack (sequential admission: NS3 → S3-A → S3-E → S3-D)
A candidate is admitted only if (a) its (date, direction) key is unused by
every leg already taken (base or earlier add-on), (b) its entry premium
is outside [400, 550), (c) its exact-tag premium candles exist — otherwise
it is NOT_COMPUTED (§9). At most one add-on per key per family (the
family's earliest signal). Add-ons do NOT enter the §5 state window; a
§7 leg that takes the book assembly reads the anchored state from the
BASE stream only.
- NS3 (gap-class): GD and GU sublegs ONLY (FLAT sublegs are never
  admitted), per the frozen Round-3 NS3 definitions; entry = the leg's
  own signal bar + 5 min; exits = the family's own geometry: stop −50 /
  first target +90 / runner lock +50 (arms from the bar after the trigger
  bar) / second target +150 / square-off 15:20.
- S3-A / S3-E / S3-D: Setup-3 variants per the frozen Round-3 appendix
  definitions (S3-A: OR width ≥ 400 with R1 rejection; S3-E: R1 with
  close-back-inside PDC; S3-D: wick rejection); entry = signal bar + 5 min
  by construction; exits = the §6 book assembly for the leg's segment.

## 8. December expiry handling
Every leg's expiry = the monthly expiry in force for its trade date under
the exchange calendar rule that produced this book's frozen EXPIRIES
series: the monthly expiry is the last Tuesday of the month, moved to the
preceding trading day when that Tuesday is an exchange holiday (the rule
behind 2026-03-30 and behind the November monthly expiry 2026-11-23).
Under that rule the December 2026 monthly expiry is 2026-12-29 — to be
confirmed against the exchange contract master and named in the December
log BEFORE the first December trade; if the contract master shows a
different December monthly expiry, the contract master governs and the
difference is recorded in the log. Weekly contracts are never used. A
trade date equal to the expiry triggers the §6 override.

## 9. NC policy
A leg whose exact premium candles cannot be obtained is NOT_COMPUTED:
excluded, counted, and named (date, direction, strike, expiry). NC legs
are never scored from spot, never estimated, never substituted. If
December's taken book has NC > 0, the December verdict is PROVISIONAL —
it cannot be a PASS regardless of net.

## 10. Timing certification (admission timing AND feature timing)
Every admission condition and every feature below is knowable at the
leg's decision bar; this certification is part of the freeze.
- (lA)/V5/Skill legs: the entry bar is the system's own recorded entry
  bar, strictly after the information its signal depends on (certified
  per family in the Round-5 WS0 audit).
- Volrix trigger: the prior session's close-to-close return — complete at
  the prior close, before the 09:20 entry.
- Bias / closing strength: the prior trading day's completed daily bar —
  known at the day's open.
- §2(i) solo drop: judged only from legs entering at or before the
  candidate's entry bar (as-of rule; end-of-day membership is never used).
- NS1 preconditions: base exit, crossing close, room (prior-day levels +
  crossing close) and bias are all complete at the crossing bar's close;
  the entry is the NEXT bar's open.
- Premium band (§4) and segment (§5): read the leg's own entry-bar open —
  the fill price, known at the fill (the book's frozen convention, the
  same standard as strike-at-entry).
- Anchored state / cold-(lA) skip: counts only stream legs whose exits
  were known at the decision leg's entry (§5 rule), asserted in code.
- NS3 gap class: the day's opening gap vs prior-day levels — known at the
  day's open; entry = own signal + 5 min.
- S3 families: the opening range completes at 09:30 and every
  bounce/rejection candle is complete at its close; entry = signal + 5.
- DTE / expiry-day override: calendar facts, known in advance.

## 11. December pass/kill (pre-registered; judged on December 2026 data alone)
- PASS: December net > ₹0 AND timing audit 0 violations AND NC = 0.
- KILL: December net ≤ −₹5,000, OR any timing violation. A killed
  candidate is retired — it is not re-tuned on December data.
- PROVISIONAL: NC > 0 (never a pass, §9); or −₹5,000 < net ≤ ₹0 —
  neither passed nor killed; the month stands at face value and is not
  re-tested on the same data.
- Floor-pace context (printed beside the verdict, NEVER the test):
  December ≥ +₹15,000 would be a floor-pace month.

## 12. In-sample record (Jan–Oct 2026, this specification)
+₹83,650.50, 99 trades, FT90 49.5%, 2.44/week, no red month-ends;
months Jan +22,748 · Feb +20,480 · Mar +1,120 · Apr −90 · May +17,680 ·
Jun +560 · Jul −3,680 · Aug −873.50 · Sep +10,776.50 · Oct +14,929.50;
halves +₹61,938.00 / +₹21,712.50; placebo (delay-6) −₹4,313.50 beaten;
ex-top-3 +₹54,610.50; NOT_COMPUTED 0; timing audit clean; independent
re-sum exact. Trades: bank_engine_r6_v21_trades.csv. Pace ₹8,365.05/month
vs the ₹15,000 floor — gap ₹66,349.50, floor NOT met in-sample; December
judges the candidate on fresh data under §11, not on this record.

## ROUND 8 — verification result (recorded AFTER the freeze above, Cycle 167)
The §1–§10 specification was regenerated through the audited causal
pipeline and compared leg-for-leg against the trades of record
(bank_engine_r6_v21_trades.csv): **99 legs, 0 mismatches, net
+₹83,650.50 to the paisa**; full controls in the same run — timing audit
0 violations, NOT_COMPUTED 0, placebo (delay-6) −₹4,313.50 beaten,
halves +₹61,938.00 / +₹21,712.50, ex-top-3 +₹54,610.50, independent
re-sum of the regenerated file (bank_engine_r8_v21_regen_trades.csv)
99 / +₹83,650.50 exact. **VERIFICATION PASS.** Evidence:
bank_r8_regen.json. The December candidate of record is book v21 under
the Round-8 specification above, judged in December under §11.
