# Bank Nifty recursive engine — log

## 2026-10-31 13:15 IST — Engine created (Chandu's request, combined-view chat)
- Protocol: `bank_RECURSIVE_ENGINE.md`. Lessons seeded with 13 lessons from the controlled Bank work already on record (`bank_engine_lessons.md`).
- Incumbent: V1 = B2 + NS1 second legs — Jan–Oct premiums +₹23,703.50 (130 trades, 42.3% FT, no red month-ends), October +₹17,160.00 (12 trades, 75.0% FT). Real money ₹0.
- Goal: ₹20,000/month average (₹200,000 Jan–Oct) per 1 lot, with the gate: total rises + no red month-end + frequency ≥2/week + FT does not collapse.
- First target month: October (lift toward ₹20,000 without breaking Jan–Sep), then September backward; the known bleed is Jun–Sep.
- November paper BNF-PAPER-V1 is frozen and untouched by this engine.
- Cycle 1 launched immediately on creation.

## Cycle 1 — 2026-10-31 — Target: October — TIGHT-STOP-40 on the V1 pool — REJECTED
- Reproduction first: V1 working book rebuilt from B2 premium trades + NS1 second legs (aggressive-run construction) and reconciled to the recorded reference TO THE PAISA: Jan–Oct +₹23,703.50, 130 trades, FT 55 (42.3%), October +₹17,160.00 (12 trades), every month net and month-end cumulative matched, independent re-sum matched. Trades: `bank_engine_V1_trades.csv`.
- Diagnosis: October's only drag is its 3 full stops (−₹1,720 each = −₹5,160 against 9 targets +₹22,320). Jan–Oct stop exits: 68 trades, −₹116,960 — the book's largest drag line.
- Fix (frozen in `bank_engine_frozen.md` before scoring): stop −50 → −40, target +90 unchanged, full V1 pool.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct +₹6,318.50 (130 trades, FT 36.2%, 3.20/week); October +₹10,260.00 (12 trades, FT 58.3%). New red month-ends: Aug (−₹5,294.50 cum) and Sep (−₹3,941.50 cum). Halves: Jan–May +₹21,286.50 / Jun–Oct −₹14,968.00.
- Controls (same run): timing audit 0 violations, all 130 entry bars checked (entry premium = open of entry bar; NS1 entries ≥ their signal times; no exit before entry). Placebo (+30 min shifted entry, same geometry): −₹29,004.30 Jan–Oct — candidate beat placebo but that does not save it. Ex-top-3 stress: −₹1,121.50 (book turns negative without its top 3). Independent re-sum from `bank_engine_cycle1_trades.csv`: matched.
- Verdict: REJECTED on every gate leg — October fell (−₹6,900 vs V1), total fell (−₹17,385), FT collapsed, two red month-ends created. Working book stays V1. No-bank on October = 1.

## Cycle 2 — 2026-10-31 — Target: October — NS1-CE-BLOCK on the V1 pool — BANKED ✅
- Diagnosis: NS1 second legs split by direction — CE second legs 25 trades −₹10,925.50 (FT 24.0%) vs PE second legs 16 trades +₹15,897.50 (FT 62.5%). October's CE second leg (6 Oct) was one of its 3 stops. Extends lesson 2 to the second-leg mechanism.
- Fix (frozen before scoring): drop every NS1 second leg with direction CE, all months; base legs and PE second legs untouched; G0 exits unchanged.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹34,629.00** (105 trades, FT 46.7%, 2.59/week); October **+₹18,880.00** (11 trades, FT 81.8%). No red month-ends (lowest cumulative close: Jan +₹5,520). Month table: Jan +5,520 / Feb +11,937 / Mar +10,480 / Apr +7,040 / May +7,240 / Jun −7,080 / Jul −9,760 / Aug −7,301 / Sep −2,327 / Oct +18,880. Halves: Jan–May +₹42,217.00 / Jun–Oct −₹7,588.00 (second half still negative in absolute terms — improved from the incumbent's −₹11,398, not cured; the Jun–Sep bleed is the next territory).
- Controls (same run): timing audit 0 violations, all 105 entry bars checked. Placebo (+30 min shifted entry, same kept legs, G0): −₹4,027.80 Jan–Oct / +₹6,280 Oct — real rule beats it clearly. Ex-top-3 stress: +₹27,189.00 (stays strongly positive). Independent re-sum from `bank_engine_cycle2_trades.csv`: matched to the paisa.
- Verdict: BANKED — October improves (+₹1,720), total rises (+₹10,925.50), no red month-end, frequency 2.59/week ≥ 2, FT rises on both windows (42.3→46.7% Jan–Oct; 75.0→81.8% Oct). **New working book: V1 + NS1-CE-BLOCK ("engine book v2"), +₹34,629.00 Jan–Oct.** October is secured at +₹18,880 (its best controlled figure so far); target moves to September.

## Cycle 3 — 2026-10-31 — CHALLENGER — Target: September — G7 runner-lock50 on book v2 pool — REJECTED (frozen banking rule)
- Diagnosis: Jun–Sep bleed is stop-dominated; stop distance is a dead lever (lessons 4, 14), so the challenger attacked the winner side (lesson 12's queued G7 retest, first time on an NS1-containing pool).
- Challenger (frozen before scoring): exits = runner-lock50 (stop −50 until +90 touched, then stop locks at entry+50, target extends to +150, square-off 15:10) on the full book-v2 pool.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct +₹44,829.00 (105 trades, FT 46.7%, 2.59/week) — total +₹10,200 above book v2, no red month-ends, FT and frequency identical. BUT target month September: −₹2,327.00 → **−₹4,727.00** (its 2 targets touched +90 then reversed to the +50 lock: +₹1,280 each instead of +₹2,480). October also gave back +₹18,880 → +₹17,080. Month table: Jan +11,520 / Feb +12,537 / Mar +14,080 / Apr +4,640 / May +10,240 / Jun −6,480 / Jul −7,360 / Aug −6,701 / Sep −4,727 / Oct +17,080. Halves: Jan–May +₹53,017 / Jun–Oct −₹8,188.
- Controls (same run): timing audit 0 violations, 105 entry bars checked. Placebo (+30 min, same runner geometry): +₹4,187.70 — beaten clearly. Ex-top-3: +₹31,989.00. Independent re-sum matched.
- Verdict: REJECTED under this cycle's frozen banking rule — the target month (September) worsened, and a secured month (October) gave back ₹1,800. Recorded honestly: the challenger PASSED the four-leg success gate (total / no-red / FT / frequency) and is the highest Jan–Oct total seen (+₹44,829) — it is kept as a noted observation, not the working book. If a later cycle secures September by another mechanism, re-testing runner-lock50 on top becomes a legitimate new cycle. Working book stays v2 (+₹34,629). No-bank on September = 1.

## Cycle 4 — 2026-10-31 — Target: September — PREMIUM-BAND-BLOCK [400,550) on book v2 — BANKED ✅
- Diagnosis: legs entered at premium [400,550) are the book's dead zone (FT 25% in the band vs 61.9% at 250–400); 4 of September's 5 losers sat in the band, both its winners outside it. CORRECTION to the frozen diagnosis: the "20 trades, −₹8,607.50" figure was measured on the V1 pool; in the book-v2 pool the band held 17 legs netting −₹3,447.50 (the rest was CE second legs already blocked in Cycle 2). The rule was frozen before scoring and the scored numbers below are the v2-pool truth; the diagnosis overstatement is recorded, not hidden.
- Fix (frozen before scoring): drop every book-v2 leg whose entry premium (open of entry-bar candle) is in [400,550); G0 exits unchanged.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹38,076.50** (88 trades, FT 50.0%, 2.17/week); September **−₹2,327.00 → +₹2,937.50 — September is GREEN for the first time**; October +₹16,400.00 (10 trades, FT 80.0% — the pre-accepted cost of dropping its 13 Oct in-band target). No red month-ends. Month table: Jan +10,680 / Feb +9,720 / Mar +10,480 / Apr +4,560 / May +7,240 / Jun −7,840 / Jul −10,520 / Aug −5,581 / Sep +2,937.50 / Oct +16,400. Halves: Jan–May +₹42,680 / Jun–Oct −₹4,603.50 (improved from −₹7,588).
- Controls (same run): timing audit 0 violations, 88 entry bars checked. Placebo (+30 min, same kept legs): −₹1,394.80 — beaten clearly. Ex-top-3: +₹30,636.50. Independent re-sum matched.
- Verdict: BANKED — September improves and turns green, total rises (+₹3,447.50), no red month-end, FT rises (46.7→50.0%), frequency 2.17/week ≥ 2 (thin margin — flagged: leg-dropping fixes are nearly exhausted; prefer additive or exit-side fixes from here). **New working book: engine book v3 = v2 + premium-band-block, +₹38,076.50 Jan–Oct.** September secured; target moves to August.

## Cycle 5 — 2026-10-31 — Target: August — TARGET-75 on book v3 pool — REJECTED
- Diagnosis (corrected counts): book v3 FT Jan–May = 29/46 (63.0%) vs Jun–Sep = 7/32 (21.9%); August 2/10. (The frozen text's 27/42 and 8/36 were mis-counted from month totals; the qualitative FT-collapse diagnosis stands and the corrected counts are recorded here.) Side finding: (lA) v2 is NOT a drop candidate — in book v3 it is 13 trades, +₹2,840, FT 6/13; its August 0-for-4 is month noise inside a positive rep.
- Fix (frozen before scoring): target +90 → +75, stop −50 unchanged, full book-v3 pool. (Process note: the first invocation of this cycle's scorer was mis-parameterised with the pool filter omitted; it was immediately re-run with the frozen pool and both output files were overwritten by the correct run — the numbers below are the correct-pool run.)
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct +₹26,307.50 (88 trades, FT 53.4% at the +75 definition, 2.17/week); August −₹5,581.00 → **−₹5,950.00 (worse)**; October +₹12,800. June (−7,840 → −4,540) and July (−10,520 → −7,670) improved, but capping every winner at +₹2,030 instead of +₹2,480 taxed the strong months far more than the few conversions bought. No red month-ends. Halves: Jan–May +₹29,630 / Jun–Oct −₹3,322.50.
- Controls (same run): timing audit 0 violations, 88 entry bars checked. Placebo (+30 min, same geometry): +₹106.70 — beaten, but irrelevant against the incumbent. Ex-top-3: +₹20,217.50. Independent re-sum matched.
- Verdict: REJECTED — target month worsened and total fell ₹11,769. Working book stays v3 (+₹38,076.50). No-bank on August = 1.

## Cycle 6 — 2026-10-31 — CHALLENGER — Target: August — book v3 + NS4 OR-rebreak add-ons — REJECTED
- Diagnosis: exit geometry is closed both directions and leg-dropping is nearly exhausted, so the challenger added a new component: NS4 opening-range-rebreak legs, never before premium-scored (spot-provisional only). 60 Bank NS4 legs → 28 on keys unused by book v3 → 14 admitted after the book's premium-band admission rule (10 dropped) and exact-candle availability (4 NOT_COMPUTED, excluded and counted, never substituted).
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): the NS4 add-ons themselves: 14 trades, **−₹15,680.00, FT 2/14 (14.3%)**. Combined book: Jan–Oct +₹22,396.50 (102 trades, FT 45.1%, 2.51/week); August −₹5,581.00 → **−₹7,301.00 (worse)**; October +₹14,680. No red month-ends (cushion absorbed it). Halves: Jan–May +₹34,840 / Jun–Oct −₹12,443.50.
- Controls (same run): timing audit 0 violations, 102 entry bars checked (NS4 entries verified ≥ their signal times). Placebo (+30 min, same pool): −₹15,045.30 — beaten, irrelevantly. Ex-top-3: +₹14,956.50. Independent re-sum matched.
- Verdict: REJECTED — target month worsened, total fell ₹15,680, FT collapsed (50.0% → 45.1%); only frequency improved. Working book stays v3 (+₹38,076.50). No-bank on August = 2 → Cycle 7 must be a challenger (protocol).

## Cycle 7 — 2026-10-31 — CHALLENGER — Target: August — PREMIUM-GATED RUNNER on book v3 — BANKED ✅
- Challenger (frozen before scoring): legs with entry premium <400 exit by runner-lock50; legs ≥400 keep plain G0. Built from lessons 12+16 and Cycle 3's per-leg deltas (runner delta by entry-premium band: <400 +₹8,400 / 400–550 −₹3,000 / ≥550 +₹4,800 with the weak-month taxes inside it).
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹46,476.50** (88 trades, FT 50.0%, 2.17/week) — the diagnosed +₹8,400 reproduced exactly. October **+₹19,400.00** (best controlled October in this channel's history; its cheap-premium targets ran). August −₹5,581.00 → **−₹3,781.00** (24 Aug cheap target ran to +150: +₹4,280). September +₹1,737.50 (still green; paid one −₹1,200 lock on its cheap target). July −₹11,720 (one lock). No red month-ends. Month table: Jan +16,680 / Feb +12,120 / Mar +10,480 / Apr +2,160 / May +7,240 / Jun −7,840 / Jul −11,720 / Aug −3,781 / Sep +1,737.50 / Oct +19,400. Halves: Jan–May +₹48,680 / Jun–Oct −₹2,203.50 (best second half yet).
- Controls (same run): timing audit 0 violations, 88 entry bars checked. Placebo (same gated assembly, +30 min): +₹3,220.70 — beaten by ₹43,255.80. Ex-top-3: +₹33,636.50. Independent re-sum matched. NOT_COMPUTED 0.
- Verdict: BANKED — August improves, total rises ₹8,400, no red month-end, frequency and FT held exactly, secured months stay secured (Sep green, Oct improved). **New working book: engine book v4 = v3 + premium-gated runner, +₹46,476.50 Jan–Oct.** August remains the target (still a negative individual month at −₹3,781).

## Cycle 8 — 2026-10-31 — Target: August — NS3 gap-class add-ons on book v4 — REJECTED
- Fix (frozen before scoring): book v4 + admitted NS3 gap-class legs as add-ons (key-unused, outside the [400,550) admission band, exact premium candles only). 58 Bank NS3 legs → 26 key-survivors → 6 admitted (6 band-dropped, 14 NOT_COMPUTED excluded and counted). August's one candidate leg (6 Aug CE FLAT) was not among the admitted six, so August was unchanged by construction.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): NS3 add-ons: 6 trades, −₹2,127.00, FT 1/6. Combined: Jan–Oct +₹44,349.50 (94 trades, FT 47.9%, 2.32/week); August −₹3,781.00 (unchanged); October +₹19,400 (unchanged). No red month-ends.
- Controls (same run): timing audit 0 violations, 94 entry bars checked (NS3 entries ≥ signal times). Placebo (same pool/assembly, +30 min): +₹8,311.70 — beaten, irrelevantly. Ex-top-3: +₹31,509.50. Independent re-sum matched.
- Verdict: REJECTED — total fell ₹2,127, August did not improve, FT diluted (50.0% → 47.9%). Working book stays v4 (+₹46,476.50). No-bank on August = 1.

## Cycle 9 — 2026-10-31 — CHALLENGER — Target: August — NS5a skill-rescan add-ons on book v4 — REJECTED
- Challenger (frozen before scoring): book v4 + admitted NS5a skill_rescan legs as add-ons (key-unused, outside [400,550), exact candles only). 90 Bank NS5a legs → 44 key-survivors → 12 admitted (13 band-dropped, 19 NOT_COMPUTED excluded and counted). (Cosmetic note: the summary JSON's internal cycle label reads "cycle8_NS5A…" due to a string substitution slip when cloning the Cycle 8 script; the files `bank_engine_cycle9_trades.csv` / `bank_engine_cycle9_summary.json` and all numbers are Cycle 9's.)
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): NS5a add-ons: 12 trades, −₹4,047.00, FT 3/12 — 8 of the 12 are CE legs and the CE add-on pattern from lessons 2/15 repeats. Combined: Jan–Oct +₹42,429.50 (100 trades, FT 47.0%, 2.46/week); August −₹3,781.00 → **−₹5,501.00 (worse — an add-on stop)**; October +₹19,400 → +₹15,960 (two add-on CE stops — a secured month taxed). No red month-ends.
- Controls (same run): timing audit 0 violations, 100 entry bars checked (NS5a entries ≥ signal times). Placebo (same pool/assembly, +30 min): −₹5,662.30 — beaten, irrelevantly. Ex-top-3: +₹29,589.50. Independent re-sum matched.
- Verdict: REJECTED on August, total and FT legs. Working book stays v4 (+₹46,476.50). No-bank on August = 2, consecutive no-beat cycles = 2.

## Session summary — 2026-10-31 (Cycles 1–9, subagent run)
- Reproduction gate passed first: V1 rebuilt and reconciled to the recorded reference to the paisa (+₹23,703.50, 130 trades) before any new scoring.
- BANKED: Cycle 2 NS1-CE-BLOCK (→ +₹34,629.00), Cycle 4 premium-band-block [400,550) (→ +₹38,076.50; September green for the first time), Cycle 7 premium-gated runner challenger (→ **+₹46,476.50**; October +₹19,400, the channel's best controlled October).
- REJECTED under full controls: Cycle 1 tight stop −40, Cycle 3 full runner-lock50 (passed the 4-leg gate, failed its frozen target-month leg — kept as an observation), Cycle 5 target +75, Cycle 6 NS4 add-ons, Cycle 8 NS3 add-ons, Cycle 9 NS5a add-ons.
- **Current best Bank book (engine book v4): Jan–Oct premiums +₹46,476.50 per 1 lot (lot 30, cost ₹220/trade, UNIQUE-ONCE), 88 trades, FT 50.0%, 2.17/week, no red month-ends, October +₹19,400. Bank contribution ≈ ₹4,648/month against the combined ₹50,000/month aspiration — honestly far below the line; the gap is not hidden.**
- Engine NOT terminated: saturation requires 3 consecutive no-beat cycles (currently 2). August is the resisting month (individual month −₹3,781; every exit family closed, entry splits screened out, add-on census complete). Parked, in order: (1) runner-gate refinement to [250,400) — +₹1,200 total but −₹1,800 August, legitimate only once August is secured otherwise; (2) NS5b (8 admissible legs) / NS6 (1) — thin; (3) the NOT_COMPUTED add-on legs (NS3 14, NS5a 19, NS5b 17) would need the browser premium-fetch route before they can be judged.
- November paper BNF-PAPER-V1 files were never touched by this run.

## Cycle 10 — 2026-10-31 — CHALLENGER — Target: August — NS5b ce_mirror_rescan add-ons on book v4 — REJECTED
- Why a challenger: 2 consecutive no-bank cycles on August (Cycles 8, 9). Diagnosis: August (book v4) = 10 trades, −₹3,781 (7 stops, 1 target, 1 runner target, 1 square-off; 9 PE / 1 CE, all base). Every exit family is closed; the parked runner-gate refinement stays parked (it costs August its runner gain). NS5b is the last add-on family with meaningful coverage never premium-scored.
- Challenger (frozen before scoring): book v4 + admitted NS5b legs (key-unused, outside [400,550), exact candles only). Census: 28 Bank NS5b legs → 8 admitted (1 key-dropped, 2 band-dropped, 17 NOT_COMPUTED excluded and counted). No August leg was among the admitted eight, so August was unchanged by construction.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): NS5b add-ons: 8 trades, **−₹1,160.00, FT 3/8** — all CE, repeating the CE pattern of lessons 2/15/22. Combined: Jan–Oct +₹45,316.50 (96 trades, FT 49.0%, 2.36/week); August −₹3,781.00 (unchanged); October +₹20,160.00 (add-ons netted +₹760 there, taxed elsewhere). No red month-ends. Month table: Jan +16,680 / Feb +12,120 / Mar +12,960 / Apr +440 / May +5,520 / Jun −11,280 / Jul −9,240 / Aug −3,781 / Sep +1,737.50 / Oct +20,160. Halves: Jan–May +₹47,720 / Jun–Oct −₹2,403.50.
- Controls (same run): timing audit 0 violations, 96 entry bars checked (NS5b entries verified ≥ their signal times). Placebo (same pool/assembly, +30 min): −₹10,539.30 — beaten, irrelevantly. Ex-top-3: +₹32,476.50. Independent re-sum from `bank_engine_cycle10_trades.csv`: matched to the paisa.
- Verdict: REJECTED — August did not improve, total fell ₹1,160, FT diluted (50.0% → 49.0%). Working book stays v4 (+₹46,476.50). No-bank on August = 3, consecutive no-beat cycles = 3.

## TERMINATION — 2026-10-31 — SATURATED / EXHAUSTED (3 consecutive no-beat cycles: 8, 9, 10)
- Protocol termination condition met: Cycles 8 (NS3), 9 (NS5a challenger) and 10 (NS5b challenger) all failed to beat the running best; the peak is Cycle 7's banked book. August is the resisting month (individual month −₹3,781 in book v4; its 7 stop legs go straight down and every exit family — stop distance both ways, target size both ways, full runner, premium-gated runner refinements screened — and every add-on family — NS1-CE blocked/banked, NS2, NS3, NS4, NS5a, NS5b — has now been controlled-tested).
- **Final Bank book (engine book v4, frozen as the plateau): Jan–Oct premiums +₹46,476.50 per 1 lot (lot 30, cost ₹220/trade, UNIQUE-ONCE), 88 trades, FT 50.0%, 2.17/week, no red month-ends, October +₹19,400.** Climb: V1 +₹23,703.50 → Cycle 2 NS1-CE-BLOCK +₹34,629.00 → Cycle 4 premium-band-block +₹38,076.50 (September green first time) → Cycle 7 premium-gated runner +₹46,476.50.
- Plateau vs the combined line, reported honestly and per-index only (no pooled verdict): Bank contributes ≈ ₹4,648/month against the ₹50,000/month combined Bank+Nifty aspiration — far below the line; the gap is not hidden. This is an in-sample plateau, not an adoption verdict; any Bank candidate is judged on fresh data (December) in the Bank channel.
- Remaining unscored material is thin only: NS6 (1 leg) and the NOT_COMPUTED add-on legs (NS3 14, NS5a 19, NS5b 17), which would need the browser premium-fetch route — noted, not chased, because every admitted sample of those families lost on premiums.
- November paper BNF-PAPER-V1 files were never touched by this engine.

---

# RUN 2 — challenger / new-mechanism cycles (started 2026-10-31, after the combined target was lowered to ₹20,000/month)

Starting book: Run-1 book v4 (+₹46,476.50). Rules unchanged (gate, controls, premiums per 1 lot 30, ₹220/trade, UNIQUE-ONCE); no re-trying lessons-closed families. Full per-cycle detail in `bank_engine_cycleN_summary.json` / `bank_engine_cycleN_trades.csv`; definitions frozen in `bank_engine_frozen.md` before each scoring.

- **R2 Cycle 1 (engine Cycle 11) — COLD-STATE (lA) STAND-ASIDE: BANKED → book v5 +₹56,796.50.** Skip (lA) v2 legs signalled while the trailing-10 signal-stream net (causal, exits known at entry) is < 0. Diagnosis: cold (lA) legs 6/6 full stops (−₹10,320); warm (lA) +₹13,760/7 legs. Result: 82 trades, FT 53.7%, 2.02/week, no red month-ends, **August −₹3,781 → +₹3,099 (the Run-1 resisting month secured)**, Jun–Oct half −₹2,203.50 → +₹8,116.50, October +₹19,400 held. Controls: timing 0/82, placebo +₹4,980.70 beaten, ex-top-3 +₹43,956.50, re-sum matched. (Book-level note: frequency margin is thin at 2.02/week — drop mechanisms are effectively closed from here.)
- **R2 Cycle 2 (Cycle 12) — RATCHET-LOCK +50→+90 after +120: REJECTED (exact no-op).** 0 of 82 legs changed; the +120 excursions happen after the +50-lock exit. No-beat 1. Lesson 25 (path-ordered diagnosis).
- **R2 Cycle 3 (Cycle 13) — RUNNER SECOND TARGET +180 (<400 legs): BANKED → book v6 +₹61,896.50.** 9 of 10 runner-target legs reached +180 (+₹900 each), 1 fell back (−₹3,000). August +₹3,999, October +₹22,100, FT 53.7% held, no red month-ends, placebo +₹8,580.70 beaten, timing 0/82, re-sum matched. No-beat reset.
- **R2 Cycle 4 (Cycle 14) — BE-ARM on ≥400 G0 segment: REJECTED.** Total → +₹43,160.00, FT 43.9%; 13 arms saved 3 stops but killed 8 targets; May flipped −₹860. No-beat 1. Lesson 27.
- **R2 Cycle 5 (Cycle 15) — BLUE-LINE v4 ADD-ONS: REJECTED.** 42 legs censused; 10 admitted net −₹13,000 (9 stops); August un-secured (+₹3,999 → −₹2,881) — the August PE bleed reproduces from the user's own independent level system. Controls clean (0 NOT_COMPUTED after a timestamp-format fix in the harness, entry premiums cross-checked to the logs). No-beat 2. Lesson 28.
- **R2 Cycle 6 (Cycle 16) — RUNNER LOCK +75: BANKED → book v7 +₹65,496.50.** 9 lock exits +₹750 each (+₹6,750), 1 target180 leg cut (−₹3,150). August +₹3,999 unchanged, September +₹2,487.50, October +₹23,600, FT 53.7% held, placebo +₹6,780.70 beaten, ex-top-3 +₹49,956.50, timing 0/82. No-beat reset.
- **R2 Cycle 7 (Cycle 17) — RUNNER LOCK +90: REJECTED.** Total back to +₹61,896.50 (10 lock exits +₹450, 3 target legs cut −₹2,700 each). Lock curve peaks at +75; family closed per the frozen peak rule. No-beat 1. Lesson 29.
- **R2 Cycle 8 (Cycle 18) — WARM-STATE RUNNER for ≥400 segment: BANKED → book v8 +₹77,196.50.** ≥400 legs get runner-lock75/+180 only when the anchored trailing-10 state is warm; cold keeps plain G0. +₹11,700 (23 legs changed; March +₹6,300, May +₹7,200; August +₹3,999 and September +₹2,487.50 untouched, October +₹22,250). FT 53.7%, 2.02/week, no red month-ends, halves +₹64,280 / +₹12,916.50, placebo +₹10,260.70 beaten, ex-top-3 +₹61,656.50, timing 0/82, re-sum matched. No-beat reset. Lesson 30.
- **R2 Cycle 9 (Cycle 19) — RUNNER SECOND TARGET +210 book-wide: REJECTED.** 11 legs reach +210 (+₹900 each), 4 fall back (−₹3,150 each) → +₹74,496.50. Target curve peaks at +180; family closed. No-beat 1. Lesson 31.
- **R2 Cycle 10 (Cycle 20) — SPEED-CONDITIONED SECOND TARGET (trigger ≤2 bars → +210): REJECTED.** Only 3 legs changed: 2 reach +210, 1 fast leg falls back → +₹75,846.50. No-beat 2. Lesson 32.
- **Diagnosis-closed after Cycle 20 (exact deltas on book v8, not scored as cycles):** cold-state <400 → G0 −₹1,800; ≥400 TGT2-150 −₹1,800; trailing-5 warm gate −₹3,150; ≥400 lock60 −₹3,600; same-bar lock arming ≈ −₹37,800 (and not honestly scorable at 5-min granularity); expiry-day defensive exit −₹2,250 by construction. Expiry-day stand-aside diagnosed (−₹2,510 / 8 legs) but unbankable under the frequency gate. Solo-leg add-ons stay closed by the pre-engine B1-vs-B2 comparison. Lesson 33.

## RUN 2 TERMINATION — SATURATED/EXHAUSTED (2026-10-31)

- **Final Run-2 book (engine book v8): Jan–Oct premiums +₹77,196.50 per 1 lot (30), 82 trades, FT 53.7%, 2.02/week, no red month-ends.** Months: Jan +14,730 / Feb +13,320 / Mar +16,780 / Apr +5,010 / May +14,440 / Jun −6,570 / Jul −9,250 / Aug +3,999 / Sep +2,487.50 / Oct +22,250 (June/July negative as individual months; every month-end cumulative close is positive). Book v8 = book v4 + cold-state (lA) stand-aside + runner second target +180 + runner lock +75 + warm-state runner for the ≥400 segment. Frozen verbatim in `bank_engine_frozen.md` as the December candidate; trades in `bank_engine_cycle18_trades.csv`.
- Run-2 climb: v4 +₹46,476.50 → v5 +₹56,796.50 → v6 +₹61,896.50 → v7 +₹65,496.50 → v8 +₹77,196.50 (4 banks in 10 cycles; ≈ ₹7,720/month Bank pace).
- Combined arithmetic, per-index reporting only (no pooled verdict): Bank +₹77,196.50 + Nifty best +₹98,001.00 (read from `nifty_engine_state.json`, EXP0 banked in its own Run 2) = ₹175,197.50 vs the ₹200,000 combined line — **SUCCESS-combined NOT met; gap ₹24,802.50.** The combined target counts for nothing as a verdict here; each index stands on its own line above.
- Termination basis: 2 consecutive scored no-beat cycles (19, 20) after the last bank, with every remaining candidate mechanism closed by exact path-level diagnosis (lesson 33) — the diagnosed space is exhausted, the same exhaustion standard that closed Run 1. In-sample plateau only; December fresh data in the Bank channel decides adoption. November paper BNF-PAPER-V1 files were never touched by this engine.

---

# SESSION 2026-11-02 — floor-target session (target: Bank alone ≥ ₹1,50,000 Jan–Oct = ₹15,000/month pace)

Starting book: engine book v8 (+₹77,196.50, 82 trades, FT 53.7%, 2.02/week, no red month-ends). Gap to the floor pace: ₹72,803.50. Frequency sits exactly at the ≥2/week gate floor (82 legs / 40.6 weeks), so no leg may be dropped net — the session works exit-side and state-side only. November paper BNF-PAPER-V1 untouched.

- **Diagnosis (exact per-leg replays on book v8, before any cycle):** (i) the parked Run-1 runner-gate refinement (<250 → G0) is DEAD on v8: −₹3,600 (the two <250 runner_target180 legs, 24 Aug and 26 Oct, cost ₹2,700 each; runner value in the <250 band is +₹3,600, and +₹13,500 in [250,400)). (ii) Second target +210 splits by segment: ≥400-warm −₹5,850, <400 +₹3,150 → Cycle 21. (iii) Lock +90 on the ≥400-warm segment (its lock curve was never measured — Cycle 17 measured <400 only): +₹4,500 → Cycle 22. (iv) ≥400-warm runner value by state-strength band is positive in EVERY band (warmup ₹0, [0,3k) +₹1,800, [3k,8k) +₹6,300, ≥8k +₹3,600) — a state-strength threshold gate is diagnosis-dead. (v) Runner value by premium sub-band: only negative pocket is ≥400-warm [550,750): −₹1,800 over 8 legs → Cycle 23. (vi) No-progress time-stop family (exit at 15 min if MFE < +40, and the whole grid 2–4 bars × +25/+40): DEAD at every grid point (best −₹1,359; headline −₹33,045) — Bank's eventual +180 runners routinely show MFE < +40 in their first 15 minutes, so winners and quick-stop losers are indistinguishable at 15 min; there is no exit-side rescue for the homework's quick-stop signature. (vii) Jun/Jul (−₹15,820 in v8, 13 of 16 legs full stops, PE-dominated) carries no usable causal state signature — June's legs were signalled in warm state, July's bleed is the regime PE property of lesson 28, and every covering mechanism (blanket cold halt, cold <400 → G0) is already diagnosis-closed or frequency-blocked. Diagnosis-closed, recorded, not cycled.

## Cycle 21 — 2026-11-02 — SEGMENT-SPLIT SECOND TARGET +210 (<400 only) on book v8 — BANKED
- Fix (frozen before scoring): runner second target +180 → +210 for entry-premium <400 legs only; ≥400 legs byte-identical to v8.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹77,196.50 → +₹80,346.50** (+₹3,150: 7 legs reach +210 at +₹900 each, 1 leg — 26 Oct CE — falls back to the lock −₹3,150). 82 trades, FT 53.7% held (invariant by construction), 2.02/week, no red month-ends, no green month flipped (Aug 3,999 → 4,899; Oct 22,250 → 20,900, still strongly positive). Halves +₹67,880 / +₹12,466.50, both ≥ 0.
- Controls (same run): sanity base reproduced v8 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹8,010.70 — beaten by ₹72,335.80; ex-top-3 +₹62,106.50; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED — every gate leg passes. **New working book: engine book v9 = v8 + <400 runner second target +210, +₹80,346.50 Jan–Oct (~₹8,035/month; gap to the ₹15,000/month floor pace: ₹69,653.50).**

## Cycle 22 — 2026-11-02 — SEGMENT-SPLIT LOCK +90 (≥400-warm segment only) on book v9 — BANKED
- Fix (frozen before scoring): post-trigger lock +75 → +90 for ≥400-warm runner legs only; <400 assembly and ≥400-cold G0 unchanged.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹80,346.50 → +₹84,846.50** (+₹4,500: 16 lock exits +₹450 each, 1 target leg — 16 Mar — cut −₹2,700). 82 trades, FT 53.7% held, 2.02/week, no red month-ends, no green month flipped (Mar 16,780 → 15,880 stays strongly positive; Jun −6,570 → −6,120 improves). Halves +₹70,580 / +₹14,266.50 — both improved.
- Controls (same run): sanity base reproduced book v9 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹7,230.70 — beaten by ₹77,615.80; ex-top-3 +₹66,606.50; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED — every gate leg passes. **New working book: engine book v10 = v9 + ≥400-warm runner lock +90, +₹84,846.50 Jan–Oct (~₹8,485/month; gap to the ₹15,000/month floor pace: ₹65,153.50).**

## Cycle 23 — 2026-11-02 — RUNNER-OFF GATE for ≥400-warm legs in [550,750) on book v10 — REJECTED (exact no-op)
- Fix (frozen before scoring): ≥400-warm legs entered at a premium in [550,750) exit plain G0 instead of the runner.
- Result: **0 legs changed; total identical at +₹84,846.50.** The diagnosed −₹1,800 pocket was measured against the lock-+75 assembly; Cycle 22's banked lock +90 already recovered it — under the +90 lock, every fall-back leg in the band exits at +₹2,480, exactly the plain-target value, so runner ≡ G0 on all 8 band legs. Controls all clean (sanity/placebo/timing/re-sum as in Cycle 22 — the variant IS the base).
- Verdict: REJECTED as a no-op (same species as Cycle 12's ratchet). The [550,750) pocket is closed — by Cycle 22, not by a gate. Working book stays v10 (+₹84,846.50). No-bank streak: 1.

## Cycle 24 — 2026-11-02 — SECOND-TARGET CURVE COMPLETION: +240 (<400 segment) on book v10 — BANKED
- Fix (frozen before scoring): <400 runner second target +210 → +240; all else identical to v10.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹84,846.50 → +₹91,146.50** (+₹6,300: all 7 affected legs reach +240 at +₹900 each, zero fall back). 82 trades, FT 53.7% held, 2.02/week, no red month-ends, no green month flipped (Jan 16,530 → 18,330; Feb 16,470 → 18,270; Aug 4,899 → 5,799; Oct 22,250 → 24,050). Halves +₹74,180 / +₹16,966.50 — both improved.
- Controls (same run): sanity base reproduced book v10 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹8,130.70 — beaten by ₹83,015.80; ex-top-3 +₹70,206.50; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED — every gate leg passes. **New working book: engine book v11 = v10 + <400 runner second target +240, +₹91,146.50 Jan–Oct (~₹9,115/month; gap to the ₹15,000/month floor pace: ₹58,853.50).**
- Diagnosis-closed alongside (exact replays on book v10, not scored as cycles): <400 lock +90 at target2 +210 = −₹2,250 (the <400 lock family stays closed at +75, confirming Cycle 17 on the new assembly); ≥400-cold legs given the runner = +₹2,700 on exactly ONE leg (15 Jul) of 12 — single-leg noise, closed per Cycle 18's own reasoning; (lA) deep-cold un-skip variant = dead (the only marginally-cold skipped (lA) leg, 29 Jun at state −400, was itself a full stop).

## Cycle 25 — 2026-11-02 — SECOND TARGET +270 (<400 segment) on book v11 — BANKED
- Fix (frozen before scoring): <400 runner second target +240 → +270. Pre-scoring leak check (controls-gate discipline — a parameter paying at every step is a warning, not a headline): the 7 affected legs were verified independently of the replay — correct weekly strikes/expiries, entry premiums exact, post-trigger paths walked bar by bar; maximum reached before any dip to the +75 lock: +650.4 / +393.2 / +439.4 / +353.5 / +375.4 / +323.3 / +347.9. No leak; genuine trend-day paths.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹91,146.50 → +₹97,446.50** (+₹6,300: 7 of 7 reach +270, zero fall back). 82 trades, FT 53.7% held, 2.02/week, no red month-ends, no green month flipped (Jan 18,330 → 20,130; Feb 18,270 → 20,070; Aug 5,799 → 6,699; Oct 24,050 → 25,850). Halves +₹77,780 / +₹19,666.50 — both improved.
- Controls (same run): sanity base reproduced book v11 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹9,030.70 — beaten by ₹88,415.80; ex-top-3 +₹73,806.50; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED — every gate leg passes. **New working book: engine book v12 = v11 + <400 runner second target +270, +₹97,446.50 Jan–Oct (~₹9,745/month; gap to the ₹15,000/month floor pace: ₹52,553.50).**

## Cycle 26 — 2026-11-02 — SECOND TARGET +300 (<400 segment) on book v12 — BANKED
- Fix (frozen before scoring): <400 runner second target +270 → +300 — the last step the Cycle-25 path verification proved all 7 legs reach (weakest clean maximum +323.3).
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹97,446.50 → +₹103,746.50** (+₹6,300: 7 of 7 reach +300, zero fall back). 82 trades, FT 53.7% held, 2.02/week, no red month-ends, no green month flipped (Jan 20,130 → 21,930; Feb 20,070 → 21,870; Aug 6,699 → 7,599; Oct 25,850 → 27,650). Halves +₹81,380 / +₹22,366.50 — both improved.
- Controls (same run): sanity base reproduced book v12 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹9,930.70 — beaten by ₹93,815.80; ex-top-3 +₹77,406.50; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED — every gate leg passes. **New working book: engine book v13 = v12 + <400 runner second target +300, +₹103,746.50 Jan–Oct (~₹10,375/month; gap to the ₹15,000/month floor pace: ₹46,253.50).**

## Cycle 27 — 2026-11-02 — SECOND TARGET +330 (<400 segment, the turning step) on book v13 — BANKED (thin)
- Fix (frozen before scoring): <400 runner second target +300 → +330 — the peak-rule measurement of the step that turns the curve.
- Result (premiums per 1 lot, lot 30, cost ₹220/trade, UNIQUE-ONCE): Jan–Oct **+₹103,746.50 → +₹104,567.00** (+₹820.50: 6 legs reach +330 at +₹900 each; the weakest verified leg, 21 Oct, misses +330 (clean maximum +323.3) and exits at its 15:10 close +₹4,200.50, −₹4,579.50 vs its +300 exit). 82 trades, FT 53.7% held, 2.02/week, no red month-ends, no green month flipped (Oct 27,650 → 23,970.50, still the book's second-strongest month). Halves +₹84,980 / +₹19,587.00, both ≥ 0.
- Controls (same run): sanity base reproduced book v13 exactly; timing audit 0 violations / 82 entry bars; placebo (+30 min) +₹10,830.70 — beaten by ₹93,736.30; ex-top-3 +₹75,527.00; NOT_COMPUTED 0; independent re-sum matched to the paisa.
- Verdict: BANKED on the frozen gate — with the thinness on record: this step's entire margin is six legs' continuation minus one leg's closing print. **New working book: engine book v14 = v13 + <400 runner second target +330, +₹104,567.00 Jan–Oct (~₹10,457/month; gap to the ₹15,000/month floor pace: ₹45,433.00).** The <400 target2 family is now CLOSED at its measured peak (+330): the +360 step is diagnosis-closed at −₹10,879.50 (two rocket legs fall back to the lock at −₹6,750 each).

## SESSION TERMINATION — 2026-11-02 — plateau at book v14 (floor pace NOT reached)
- 7 cycles run (21–27), 6 banked, 1 exact no-op rejected. Climb: v8 +₹77,196.50 → v9 +₹80,346.50 (C21 segment-split TGT2 +210) → v10 +₹84,846.50 (C22 ≥400-warm lock +90) → v11 +₹91,146.50 (C24 <400 TGT2 +240) → v12 +₹97,446.50 (C25 +270) → v13 +₹103,746.50 (C26 +300) → v14 +₹104,567.00 (C27 +330). Session gain +₹27,370.50 (+35.5%), closing 37.6% of the ₹72,803.50 gap.
- **Final book v14: +₹104,567.00 Jan–Oct 2026, premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE — ≈ ₹10,457/month against the ₹15,000/month floor. The floor is NOT met; the remaining gap is ₹45,433.00 (₹4,543/month).** This is an in-sample plateau, not an adoption verdict; December fresh data in the Bank channel judges it.
- Saturation basis (the Run-2 exhaustion standard): every remaining plausible family is closed by a scored verdict or an exact path-level diagnosis — segment target curves peaked (+330 <400 / +180 ≥400), lock curves complete (+75 <400 / +90 ≥400 = the trigger level), runner gates and bands dead or no-op ([250,400) −₹3,600; [550,750) pocket closed by C22; state-strength gating loses in every band split), state-window variants single-leg noise (W15 +₹450 on one leg), time-stop family dead at every grid point, confirmation/hold family rejected in its scored form and frequency-blocked in all sibling forms (any net leg drop breaks 82 legs = 2.02/week ≥ 2/week), Jun/Jul and expiry pockets real but unreachable under the frequency gate, add-on census exhaustive (NS3/NS5a/NS5b premium legs remain NOT_COMPUTED-blocked; every admitted sample of those families lost), scalping dead (lesson 34). The one structural wall left is frequency itself: the book sits exactly at the ≥2/week floor, so no losing leg can be dropped and no new premium-scored entry family exists to add.
- November paper BNF-PAPER-V1 files were never touched by this session.

---

# ROUND 2 — 2026-11-02 — floor-target continuation on Chandu's order (no saturation conclusions; permutations, combinations, use-case pockets)

Working machinery (new, sanity before scoring): `bank_r2_core.py` generalised exit replay reproduces book v14 (+₹104,567.00 incl. placebo +₹10,830.70, ex-top-3 +₹75,527.00, halves, months — exact) and book v8 (+₹77,196.50) through the new code path. Definitions frozen in bank_engine_frozen.md (Round-2 appendix) before any cell was scored; one pre-scoring correction recorded there (the FT gate leg is read as FT90 vs the working book's FT — the literal own-trigger clause is unsatisfiable for trigger-105 cells by monotonicity). Data completion: 22 expired contracts fetched from the Upstox expired-instruments API (browser UA) into historical_proof_data/ so no Round-2 cell rests on a NOT_COMPUTED exclusion (16 NS1 + 6 expiry-ITM).

## Cycles 28–30 — 2026-11-02 — EXIT-GEOMETRY GRID on book v14 (stop {40,50,60} × trigger {75,90,105} × lock {none,50,75,90}; modes A <400-only / B ≥400 / AB all) — 1 of 108 cells BANKED
- Result: exactly one cell passes the full gate (incl. independent re-sum): **mode A, stop −50, trigger +105, lock +75 → +₹105,167.00 (+₹600.00)**. Two legs change: 2026-01-20 PE runner_stop +₹2,030 → square-off +₹6,380 (the +105 arm lets the leg run un-locked past +90); 2026-07-27 PE runner_stop +₹2,030 → stop −₹1,720. FT90 53.7 held, 82 trades, 2.02/week, no red month-ends, halves +₹89,330/+₹15,837, placebo +₹18,480.70 beaten, ex-top-3 +₹76,127.00, timing 0 violations, NOT_COMPUTED 0. All 107 other cells score at or below v14's net (45 fail on the net leg alone). The (50, 90) stop/trigger pair is a joint peak in both segments; stop −40 and trigger +75 damage FT90 wherever they appear. Full 108-cell table: bank_engine_round2_2026-11-02.md / bank_r2_grid_results.json.
- Verdict: BANKED. **New working book: engine book v15 = v14 + <400 runner trigger +105 (stop −50, lock +75, TGT2 +330 unchanged), +₹105,167.00 Jan–Oct.**

## Cycle 31 — 2026-11-02 — NS1 ROOM-RATIO sweep {1.3, 1.4, 1.6} (window 14:30, ATM) on book v15 — REJECTED (no cell changes the book)
- Regeneration sanity (before scoring): the parameterised generator reproduces all 41 pooled NS1 second legs exactly at frozen parameters; the 24 non-pooled regenerated legs are each explained by an earlier base leg on the key; signal times match the frozen map (0 mismatches).
- Result: room 1.3, 1.4 and 1.6 each return the identical book (+₹105,167.00, 82 trades). The room axis cannot bite: its only newly admitted leg (room 1.3/1.4: 2026-01-07 PE, entry premium ₹445.85) falls inside the blocked premium band [400,550); no taken second leg carries room in [1.5, 1.6). NOT_COMPUTED 0 after the data completion fetch. Verdict: REJECTED — the frozen 1.5 threshold is a plateau point, not a tuned edge.

## Cycle 32 — 2026-11-02 — NS1 SIGNAL-WINDOW sweep {14:00, 15:00} (room 1.5, ATM) on book v15 — REJECTED
- Result: window 14:00 → identical book (no taken second leg signals in (14:00, 14:30]). Window 15:00 → 83 taken, +₹104,842.00 (−₹325.00): the single added leg (2026-09-03 PE, entry premium 588.0) exits square-off −₹325.00; FT90 falls 53.7 → 53.0. Verdict: REJECTED on net + FT90.

## Cycle 33 — 2026-11-02 — NS1 SECOND-LEG STRIKE 100 ITM (room 1.5, window 14:30) on book v15 — REJECTED
- Result: 80 taken, +₹96,809.50 (−₹8,357.50), FT90 52.5, frequency 1.97/week. All 14 ITM second legs were premium-scored after fetching their contracts (NOT_COMPUTED 0). Verdict: REJECTED on net + FT90 + frequency — the October-only ITM result (lesson 6) extends to the full book and to second legs specifically.

## Cycle 34 — 2026-11-02 — (lA) RESCAN CUTOFF 11:30 on book v15 — REJECTED
- Re-pool sanity: the frozen-parameter re-pool reproduces the 89-leg B2 base exactly. Result: 80 taken, +₹104,857.00 (−₹310.00), frequency 1.97/week. Legs lost: the pooled (lA) winners on 2026-02-24 (signal 12:40) and 2026-09-08 (signal 12:00), plus — pipeline interaction, measured — the 09:45 Skill legs on 2026-04-16 and 2026-06-30, whose source sets collapse to Skill-solo when their (lA) rescan co-source is cut and which then fall under the B2 Skill-solo ≤09:55 drop (one replacement leg enters 2026-04-16 at 10:00). Verdict: REJECTED on net + frequency.

## Cycle 35 — 2026-11-02 — (lA) RESCAN CUTOFF 12:30 on book v15 — REJECTED
- Result: 80 taken, +₹104,857.00 (−₹310.00), frequency 1.97/week (the 2026-02-24 leg and the 2026-06-30 Skill-solo interaction drive the loss; the delay-0 books of Cycles 34/35 coincide, their placebo twins differ ₹16,000.70 vs ₹20,200.70, proving the pools genuinely differ). Verdict: REJECTED on net + frequency. The frozen 13:30 cutoff is worth +₹310.00 to the book and keeps the frequency floor.

## Cycle 36 — 2026-11-02 — BIAS-GATE THRESHOLDS ±5 POINTS {(40,85), (30,75)} — EXACT NO-OP (proven, not assumed)
- Result: across all 40 stored V5-v2 winners, none sits on a flip band (CE winners with prev-day closing strength in [35,40): zero; PE winners with strength in [75,80): zero). Both variant books are identical to v15 by construction. The admission side (legs a looser gate would have generated) does not exist in stored candidates and was not invented. The ±5-point bias axis is inert on this book.

## Cycle 37 — 2026-11-02 — EXPIRY-DAY STRIKE RULE 100 ITM on book v15 — REJECTED
- Result: 82 taken, +₹101,417.00 (−₹3,750.00), FT90 52.4. Only 1 of the 8 expiry-day legs changes outcome at its ITM strike (2026-02-24 PE +₹2,030 → −₹1,720); the other 7 are identical because the exits are level-relative (stop −50 / target +90 read the same at any strike). All 6 missing ITM contracts fetched first (NOT_COMPUTED 0). Verdict: REJECTED on net + FT90.

## Cycle 38 — 2026-11-02 — JUN/JUL PE BLEED POCKET (cold-state signature, 3 conditional geometries) on book v16 — REJECTED
- Diagnosis printed before the signature was frozen: Jun/Jul PE legs 14 / −₹15,680.00 / 12 losers; signature = PE leg with anchored state cold covers 10 of 14 (−₹13,000.00); prev-day-return and gap signatures do not isolate the bleed. 17 signature legs Jan–Oct.
- Result (signature legs only, rest of book untouched): plain (−50/+90) +₹103,967.00; plain (−60/+90) +₹101,925.50; plain (−40/+90) +₹103,067.00 — all below book v16 (+₹106,517.00). Verdict: REJECTED ×3. The bleed is real and mechanically locatable, but no tested conditional geometry monetises it: the cold-PE legs that run earn more under the standard assembly than any variant recovers from the losers. (Stand-aside remains frequency-barred: 17 legs.)

## Cycle 39 — 2026-11-02 — EXPIRY-DAY POCKET (3 geometries on the 8 expiry-day legs) on book v15 — 1 BANKED
- Result: **plain G0 (−50/+90) regardless of segment/state → +₹106,517.00 (+₹1,350.00)** — full gate PASS incl. re-sum: FT90 53.7 held, 82 trades, 2.02/week, no red month-ends, no green month flips, halves ≥ 0, placebo +₹18,365.20 beaten, timing 0 violations, NOT_COMPUTED 0. Variants rejected: (−40/+90) +₹104,117.00; (−50/+75) +₹105,167.00 with FT90 52.4.
- Verdict: BANKED. **New working book: engine book v16 = v15 + expiry-day legs take plain G0 (−50/+90), +₹106,517.00 Jan–Oct.** Expiry-day paths do better without the runner — no lock give-back on expiry-day theta paths.

## Cycle 40 — 2026-11-02 — WIDE-CANDLE REJECTION (Blue-Line setup3) STANDALONE add-ons on book v16 — REJECTED
- Result: exactly 1 admissible leg in Jan–Oct under the frozen admission rules (unused key, premium outside [400,550), series present): 2026-07-06 PE, entry premium 683.5, scoring −₹1,720.00 under the v16 assembly → combined +₹104,797.00, FT90 53.0. Verdict: REJECTED on net + FT90. The book's pool already covers nearly every setup3 day (Cycle 15's pooled-mix admission found its legs mostly on keys the book now holds or in the blocked band).

## Cycle 41 — 2026-11-02 — COMBINATIONS + NS1 CROSS-GRID completion — stack BANKED (already the working book); 17 cross cells REJECTED
- NS1 cross-grid (gated vs v16, v16 assembly): room {1.3,1.4,1.6} × window {14:00,15:00} × strike {ATM, ITM} + ITM at 14:30 + window × ITM at room 1.5 — 17 cells. ATM cells return the identical book or the window-15:00 book (+₹106,192.00, −₹325.00); every ITM cell returns +₹98,159.50 (80 taken, FT90 52.5; a few carry named stream-level NOT_COMPUTED legs, 1–2, counted). No pass. Family 2 closes 24/24 cells with zero passes.
- Combinations: the only passing ingredients in Round 2 are the Cycle-28 grid cell and the Cycle-39 expiry pocket (Families 2 and 3 and the other pockets produced none), so the combination space is exactly their stack. Formal re-gate of the stack against the Round-2 starting book: **book v16 vs v14 — PASS** (net +₹106,517.00 vs +₹104,567.00; FT90 53.7 both; no red month-ends; no green month flips; halves +₹90,230.00/+₹16,287.00 ≥ 0 — see scorecard in the Round-2 report; placebo +₹18,365.20 beaten; timing audit 0 violations; independent re-sum 82 trades / +₹106,517.00 matched, bank_engine_r2c41_stack_trades.csv).

## ROUND 2 CLOSING — 2026-11-02 — enumerated space exhausted at book v16 (floor pace NOT reached)
- 14 cycles (28–41), 2 banked (Cycles 28 and 39), Round-2 gain +₹1,950.00 over v14. **Final book v16: +₹106,517.00 Jan–Oct 2026, premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE — ₹10,651.70/month against the ₹15,000/month floor. Remaining gap ₹43,483.00 (₹4,348.30/month).**
- Space accounting (every cell scored under the full controls gate, verdicts in bank_engine_round2_2026-11-02.md): exit grid 108/108; NS1 permutations 24/24 (3 axes + full cross); (lA) cutoffs 2/2 + frozen; bias thresholds 2/2 (zero-effect proven on stored winners); expiry-day strike 1/1; bleed pocket 3/3 geometries under a mechanically frozen signature; expiry pocket 3/3; setup3 standalone 1 family (1 admissible leg); combinations — only two passing ingredients existed, their stack is book v16 and is formally re-gated. Nothing in the enumerated space is unscored.
- What the space's shape says, in measurements: the frozen points (room 1.5, window 14:30, cutoff 13:30, bias 35/80, stop −50, trigger +90 in the ≥400 segments) are plateau points — moving any of them in either direction is inert or negative; the only two positive directions in the whole space were a later runner arm on cheap legs (+105 trigger, +₹600) and removing the runner entirely on expiry-day legs (+₹1,350). The remaining ₹43,483 is not inside this space: the book's 82 legs at 2.02/week are the frequency floor, every leg-dropping variant fails that gate, and no cell in any family added a profitable leg.
- November paper BNF-PAPER-V1 files were never touched by this session. Book v16 is frozen in bank_engine_frozen.md as the December candidate (supersedes v14); December fresh data judges it in the Bank channel.

## ROUND 3 — targeted techniques (2026-11-02, Cycles 42–63; starting book v16 +₹106,517.00)
Definitions frozen in bank_engine_frozen.md (ROUND 3 appendix) before scoring. Full record: bank_engine_round3_2026-11-02.md.

### Workstream 1 — the unscored legs, unblocked (Cycles 42–44)
- Census reproduced the parked counts exactly (NS3 14 / NS5a 19 / NS5b 17 NOT_COMPUTED); 31 missing contracts fetched via the expired-instruments route (browser UA), 0 failures. NOT_COMPUTED is now 0 for all three families — first complete premium scoring in the engine's history. Completed v4 censuses (original Cycles 8/9/10 re-run post-fetch): NS3 18 admitted +₹13,821.00 (the 6-leg partial sample said −₹2,127 — REVERSED); NS5a 30 admitted −₹9,792.00; NS5b 23 admitted −₹18,012.50.
- Cycle 42 NS3 on v16: 19 admitted, family +₹11,051.00, book +₹117,568.00 — NOT banked: fails only FT90 (51.5% < 53.7%). NS3 earns via runner locks/partials (8/19 FT90); the dilution is structural.
- Cycle 43 NS5a on v16: 35 admitted, −₹17,642.00 — rejected (net, FT90).
- Cycle 44 NS5b on v16: 23 admitted, −₹18,012.50 — rejected (net, Sep flip, FT90). Family net identical under the v4 and v16 assemblies — scorer cross-validated.

### Workstream 2 — mechanised setups (Cycles 45–52; signals regenerated from stored 5-min spot, 21 contracts fetched, NC 0 everywhere)
- Cycle 45 S3-A (OR ≥400, v4 reading): 6 admitted +₹2,280.00 — FT90 only (53.4%).
- Cycle 46 S3-B (350–580): 9 admitted −₹7,080.00 — rejected. Cycle 47 S3-C (400–650): 5 admitted −₹200.00 — rejected.
- Cycle 48 S3-D (wick rejection): 3 admitted +₹445.50 — FT90 only. Cycle 49 S3-E (close below PDC): 4 admitted +₹1,520.00 — FT90 only (53.5%).
- Cycle 50 S4 spec reading: 1 leg −₹1,720.00 — rejected. Cycle 51 S4B v4-as-coded: 9 admitted −₹7,080.00, flips Sep — rejected. The bear-trap reclaim has no premium edge under either documented reading.
- Cycle 52 S1 retest-hold on DERIVED Red bands (swing-high rejection clusters from prior-10-day 5-min spot, frozen derivation): 7 admitted −₹3,176.50 — rejected on net. The mechanical bands do not reproduce the hand-drawn bands' edge.

### Workstream 3 — execution optimisation (Cycles 53–57; frozen convention asserted to reproduce v16 exactly, main + placebo, before any variant was read)
- Cycle 53 EC-A (enter at entry bar's close): +₹42,752.00 — rejected (net −₹63,765, May flips red, FT90 43.9). Cycle 54 EC-B (next bar's open): +₹41,339.00 — rejected likewise. The first 5–10 minutes after the frozen entry carry the book's edge; any entry delay is ruinous (same direction as the Day-1 hold-confirmation rejection, larger).
- Cycle 55 SQ-1445: +₹107,871.50 — BANKED vs v16 (+₹1,354.50). Cycle 56 SQ-1500: +₹104,795.00 — rejected (net). Cycle 57 SQ-1520: +₹107,930.00 — BANKED vs v16 (+₹1,413.00), dominates 14:45 → **book v17** (frozen above; trades bank_engine_r3_v17_trades.csv).

### Workstream 4 — combinations on v17 (Cycles 58–63; gate vs v17)
- Cycle 58 v17+NS3: +₹122,609.50 (NS3 worth +₹14,679.50 under 15:20) — FT90 only (52.5%).
- Cycle 59 v17+S3-A: +₹110,210.00 — FT90 only (53.4%, one leg short). Cycle 60 v17+S3-E: +₹109,450.00 — FT90 only (53.5%, one leg short).
- Cycle 61 v17+NS5a: +₹93,648.00 — rejected (net). Cycle 62 v17+NS5b: +₹91,072.50 — rejected (net, Sep flip).
- Cycle 63 v17+NS3+S3-A+S3-E (+S3-D admitted 0 after key consumption): **+₹127,369.50**, 108 trades — passes every gate leg except FT90 52.8% (57/108; 58 needed). FLAGGED for Chandu's waiver decision (frozen file, above); not banked.

### Round-3 closing census
- 22 cycles (42–63), 2 banked (Cycles 55, 57 — same knob; v17 takes the better), Round-3 gain +₹1,413.00 over v16. **Final book v17: +₹107,930.00 Jan–Oct 2026 — ₹10,793.00/month vs the ₹15,000 floor; gap ₹42,070.00.**
- Every Round-3 candidate was premium-scored with NOT_COMPUTED 0 (52 contracts fetched this round; the multi-year data wall is gone). The remaining gap does not live in the unscored legs (they are now scored: one genuinely positive family, NS3, blocked only by the FT90 quality leg), nor in the unbuilt setups (built and gated: small positives in the Setup-3 close-rejection readings, negatives elsewhere), nor in execution timing (entry delays ruinous; square-off worth +₹1,413). November primary files untouched.

## ROUND 4 — 2026-11-02 (Cycles 64–114; brief: find a version of the flagged Cycle-63 stack that passes FT90 on its own merits, plus keep widening the search)
Starting book v17 +₹107,930.00 (gap ₹42,070). All definitions frozen in bank_engine_frozen.md ROUND 4 appendix BEFORE scoring; diagnosis in bank_r4_diag.json. Core bank_r4_core.py reproduces v17 and the flagged stack (+₹127,369.50 / 108 / FT90 52.8%, placebo +₹15,367.50) exactly.

### Workstream 1 — NS3's own exit geometry (Cycles 64–81; 18 cells × assemblies (a) v17+NS3@cell, (b) full stack)
Every cell fails the banking gate vs v17 on FT90 alone. Trig-75 cells CUT stack FT90 to 49.1–50.9% (arming the runner at +75 exits legs before their paths touch +90 — up to 4 converted legs lost); trig-90 cells leave FT90 at exactly 57/108 in all 9 cells — FT90 is path-determined under this grid; geometry moves NET only. Assembly (b) nets: T75 row +118,621.50 → +127,171.50; T90 row +124,819.50 → +133,219.50 (Cycle 81, T90L65G175 — best cell; passes the gate vs the FLAGGED STACK, fails vs v17 on FT90 only). Assembly (a) best also Cycle 81: +₹128,459.50, FT90 52.5%.

### Workstream 2 — NS3 admission refinement (Cycles 82–88; stack variants vs v17)
- Cycle 82 premium <400: **+₹119,818.00, 95 trades, FT90 54.7% — BANKED.**
- Cycle 83 premium ≥550: +₹120,241.50, FT90 52.0% — rejected (FT90).
- Cycle 84 DTE ≥1: +₹129,089.50, FT90 53.3% (57/107) — FT90-only failure vs v17; passes vs the flagged stack.
- Cycle 85 DTE ≤7: **+₹117,820.00, 95 trades, FT90 54.7% — BANKED.**
- Cycle 86 DTE >7: +₹122,239.50, FT90 52.0% — rejected (FT90).
- Cycle 87 source GD only: **+₹127,288.00, 104 trades, FT90 53.8% — BANKED.**
- Cycle 88 source GD+GU: **+₹128,048.00, 106 trades, FT90 53.8% — BANKED → book v18** (max net of the passers; also passes vs the flagged stack). The dilutive slice was the NS3-FLAT sublegs (2 admitted, −₹678.50, FT90 0/2): excluding them lifts the stack over the FT90 guard at full net. v18 frozen above (trades bank_engine_r4_v18_trades.csv).

### Workstream 3 — Setup-3 completion (Cycles 89–96)
Standalone (v17 + cell only): S3-F +₹699 family net, S3-G +₹699 (identical admitted set), S3-H −₹200, S3-I −₹960, S3-J +₹1,520 — all fail FT90 standalone. In the flagged stack (Cycles 94–96), S3-F/G/J admit ZERO additional legs — every candidate key is already owned by the base/NS3/S3-A/E/D; stack totals identical to Cycle 63. The Setup-3 definition space is exhausted: new readings only re-find existing legs.

### Workstream 4 — near-miss conversion audit + the one permitted candidate (Cycle 97)
Audit: exactly 3 near-miss legs (MFE ∈ [75,90), ft90=0), all base PE legs. 2026-06-09 full-day path max +89.9 (never reached +90 — unconvertible); 2026-08-27 alive to square-off at +80.55 (unconvertible); 2026-07-14 stopped 11:10, full-day path max +104.0 (the only convertible path). Separator under the frozen criterion: DTE ≥ 14 (near-miss rate 10.3% vs 0%, holds 3/3, converted share 46% < 60%); premium ≥550 and entry <11:00 fail the converted-share leg. Candidate (DTE≥14 legs keep own assembly, stop −50 → −65; own-assembly reconstruction verified exact on all 61 main + 59 placebo legs): **+₹118,069.50, 108 trades, FT90 53.7% (58/108 — the 2026-07-14 leg converted) — BANKED vs v17**; the wider stop costs ₹9,300 of net vs the flagged stack, so it does not displace v18.

### Workstream 5 — entry-state features on the stack (Cycles 98–101; tercile cuts verified −0.208%/+0.138% vs frozen −0.210/+0.139)
All four fail: range30 ≤ trailMed only +₹88,329.50 (FT90 47.1, freq 1.72); range30 > trailMed only +₹60,930.00 (April flips red, freq 1.63); drop gap-T3 +₹105,713.50 (freq 1.82); drop gap-T1 +₹79,870.50 (April flips, FT90 50.8, freq 1.55). The stack earns in both range states and all gap terciles; day-state admission is closed for the stack.

### Workstream 6 — combinations (Cycles 102–114; gated vs v17, reported vs flagged stack, displacement-tested vs the current best)
- **Cycle 102 v18 × NS3 geometry T90L65G175: +₹133,898.00, 106 trades, FT90 53.8% — BANKED vs v17, passes vs flagged stack, DISPLACES v18 → book v19** (frozen above; trades bank_engine_r4_v19_trades.csv). The geometry's full +₹5,850 gain survives the GD+GU restriction — every geometry-gaining NS3 leg is a GD/GU leg.
- Cycle 103 v18 × WS4 transform: +₹118,748.00, FT90 54.7% — banked vs v17, no displacement (stop-widening cost again ≈ ₹9,300).
- Cycle 104 GD+GU ∧ premium<400: +₹121,538.00, FT90 55.3% — banked, no displacement. Cycle 106 GD ∧ premium<400 is the identical book (same 94 trades; every GU leg is ≥400 or key-dropped under the band rule).
- Cycle 105 GD+GU ∧ DTE≤7: +₹119,540.00, FT90 55.3% — banked, no displacement.
- Cycles 107–109 S3-F/G/J on v18: zero legs admitted; totals identical to v18.
- Cycle 110 premium<400 ∧ DTE≤7: +₹115,340.00, FT90 54.3% — banked, no displacement. Cycle 111 GD+GU ∧ premium<400 ∧ DTE≤7: +₹117,060.00, FT90 54.8% — banked, no displacement.
- Cycle 112 GD+GU ∧ premium<400 @ T90L65G175: +₹127,238.00, FT90 55.3% — banked, no displacement. Cycle 113 GD+GU ∧ DTE≤7 @ geometry: +₹124,490.00, FT90 55.3% — banked, no displacement.
- Cycle 114 v19 × WS4 transform: +₹124,598.00, FT90 54.7% (58/106) — banked vs v17, no displacement.

### Round-4 closing census
- 51 cycles (64–114), all six workstreams gated through. Bankings vs v17: Cycles 82, 85, 87, 88, 97, 102–106, 110–114. Two displacements: v18 (Cycle 88, +₹128,048.00) then v19 (Cycle 102, +₹133,898.00). Round gain over v17: **+₹25,968.00**.
- **Final book v19: +₹133,898.00 Jan–Oct 2026 — ₹13,389.80/month vs the ₹15,000 floor; gap ₹16,102.00.** FT90 53.8% (57/106) — the stack now passes the full gate on its own merits; the Cycle-63 waiver question is moot and the flagged stack is superseded. November primary untouched.

## ROUND 5 (2026-11-02) — WS0 causality audit + targeted workstreams on v19 (Cycles 115–135)

Definitions frozen in bank_engine_frozen.md (ROUND 5 appendix) before scoring. 17 gated cycles. Full record: bank_engine_round5_2026-11-02.md.

- **Cycle 115 WS0 AUDIT — VIOLATIONS FOUND in v19.** 39 legs carrying +₹68,469 of the recorded +₹133,898 violate admission causality: (V-SK) 9 Skill-V3 representative legs ≤09:55 kept only via later same-day confirmation under the end-of-day solo reading (+₹25,320); (V-NS) 30 NS1/NS3 legs whose source `entry_time` is the spot trade's EXIT-bar time, not the entry (13 of 15 NS1, +₹21,941; all 17 NS3, +₹21,208). Certificates: B1→B2 rule re-derived exactly (110→89, 21 drops itemised); state pipeline reproduces the frozen taken set 82/82; 58 BASE legs + 2 NS1 legs + all 7 S3 legs CAUSAL; one Volrix calibration note (2026-06-01 leg, trigger −0.924% on stored data — disclosed, not a violation). **Causal rebuild REF_AUD: 102 legs, +₹69,940.50, FT90 48.0%, 2.51/wk, no red month-ends, halves +58,268/+11,672.50, placebo −7,223.50 beaten, ex-top-3 +40,900.50, NC 0, re-sum exact.** (−₹63,957.50 = 47.8% of the recorded headline was non-causal.) Rebuild correction disclosed: first build pooled NS1 at recorded times (+₹73,390.50); the WS2 sanity caught it, pooling at causal times throughout gives REF_AUD above. All Round-5 gating is vs REF_AUD.
- Cycle 116 WS1 wound diagnosis on REF_AUD: all 49 losers are full −₹1,720 stops; wound = Jun+Jul (16 legs, −₹27,520). No feature passes the frozen separator test (closest: bearish-bias days, 1.6× concentration vs 2× required; that group nets +₹21,890). No candidate run; WS1 closed.
- Cycles 118–121 WS2 NS1 permutations: room 1.4, room 1.6 and window 14:00 each reproduce REF_AUD IDENTICALLY; window 15:00 adds one losing leg (+₹69,474.50, FT90 47.6) — rejected. Frozen NS1 cell is a plateau; axis closed.
- Cycles 122–124 WS3 Skill-solo re-admission (population 72 legs: 51 CE, 21 PE): PE-only +₹35,413.50; CE-only +₹22,885.00 (March flips); room≥1.5 +₹8,687.00 (March flips) — all rejected by ₹34.5k–₹61.3k. The v1-era exclusion is load-bearing.
- Cycles 125–129 WS4 Volrix grid (regenerated sets; two named construction exceptions — 2026-06-01 calibration, October strike basis): −0.75% +₹60,400.50 rejected; −1.25% +₹62,440.50 rejected; **−1.0%/cd10 regenerated +₹72,110.50 BANKED (+₹2,170); −1.0%/cd5 +₹78,050.50 BANKED (+₹8,110); −1.0%/cd15 +₹78,250.50 BANKED (+₹8,310)**.
- Cycles 133–134 WS5 bias-conditioned exits: bearish-day lock 40 → +₹69,490.50 (−₹450); bullish-day tgt2 130 → +₹62,590.50 (−₹7,350) — both rejected on net only.
- Cycle 135 WS6 final re-gate: **book v20 = causal rebuild + Volrix (−1.0%, cd15) regenerated = +₹78,250.50, 99 legs, FT90 49.5%, 2.44/wk, no red month-ends, halves +62,688/+15,562.50, placebo −4,313.50 beaten, ex-top-3 +49,210.50, NC 0, re-sum exact; PASS vs REF_AUD and chained vs C127.** Trades bank_engine_r5_v20_trades.csv.

### Round-5 closing census
- 17 cycles (115–116, 118–129, 133–135), all six workstreams gated through. Bankings: Cycles 127, 128, 129 (one Volrix axis; best = cd15).
- **Final book v20: +₹78,250.50 Jan–Oct 2026 — ₹7,825.05/month vs the ₹15,000 floor; gap ₹71,749.50. Floor NOT met.** v20 (audited lineage) supersedes v19 as the December candidate of record; v19's recorded +₹133,898 stands in the Round-4 freeze with the WS0 annotation — 47.8% of it was non-causal entry-timing value. November primary untouched.

## ROUND 6 (2026-11-02) — rebuild on the causal foundation (Cycles 136–149)

Gating reference: v20 (+₹78,250.50), reproduced exactly before scoring. Rounds 1–4 magnitudes are not evidence (mis-timed legs); only constructions re-tested, on causal times. Full record: bank_engine_round6_2026-11-02.md.

- Cycle 136 WS1 decomposition of v20 (causal): BASE 61 legs +₹55,466 (Volrix regen 7 in-book legs +₹19,910; V5 +₹15,330; (lA) +₹11,939.50; Skill +₹8,286.50) · NS1 16 +₹10,269.50 · NS3 (GD+GU @ L65/G175) 15 +₹7,755 (GD 14 +₹9,475; GU 1 −₹1,720) · S3-A 6 +₹2,280 · S3-E 1 +₹2,480. NS3 causal census: 58 legs (GD 37 / GU 14 / FLAT 7).
- Cycle 137 WS1 admission retest — NS3 ALL sublegs @ L65/G175: +₹77,558.50, FT90 48.5 — REJECTED (net, FT90). The FLAT exclusion holds causally (admitting FLAT costs ₹692).
- **Cycle 138 WS1 NS3 GD+GU @ lock50/tgt2 175: +₹80,650.50 — BANKED vs v20 (Δ +₹2,400).**
- **Cycle 139 WS1 NS3 GD+GU @ lock65/tgt2 150: +₹81,100.50 — BANKED vs v20 (Δ +₹2,850).**
- **Cycle 140 WS1 NS3 GD+GU @ lock50/tgt2 150: +₹83,650.50 — BANKED vs v20 (Δ +₹5,400).** NS3 family net ₹7,755 → ₹13,155 on the same 15 legs. On causal times the geometry peak is the TIGHTER cell — the opposite corner from the mis-timed grid.
- Cycle 141 WS2 causal stack re-test (decomposition verdict): S3-A +₹2,280 and S3-E +₹2,480 are both net-positive causally — no removal candidate exists; the S3 stack stands. Closed.
- Cycle 142 WS3 gap FOLLOW (pre-registered; 60 gap days ≥0.50%, entry 09:35): admitted 40 legs, sleeve −₹16,150 → book +₹62,100.50 — REJECTED (net, June flip, FT90 44.6).
- Cycle 143 WS3 gap FADE: admitted 33 legs, sleeve −₹27,360 → book +₹50,890.50 — REJECTED (net, March flip, FT90 42.4). Bank gap family closed in both directions.
- Cycle 144 WS4 expiry-day sleeve (pre-registered; population 9 B1 representatives on the 10 monthly expiry dates, entry 09:15–11:00): admitted 4, sleeve −₹6,880 → book +₹71,370.50 — REJECTED (net, June flip, FT90 47.6). Family closed.
- Cycles 145–148 WS5 Volrix completion from (−1.0%, cd15): cd12 +₹73,080.50 rejected; cd20 +₹70,600.50 rejected; trigger −0.9% EXACT no-op (same 11 legs, +₹78,250.50); trigger −1.1% +₹68,580.50 rejected. Banked cell is the plateau peak; both axes closed.
- Cycle 149 WS6 final re-gate: **book v21 = v20 × NS3(GD+GU) @ stop50/trig90/lock50/tgt2 150 = +₹83,650.50, 99 legs, FT90 49.5%, 2.44/wk, no red month-ends, halves +61,938/+21,712.50, placebo −4,313.50 beaten, ex-top-3 +54,610.50, NC 0, timing clean, re-sum exact; PASS vs v20 and chained vs C139 and C138.** Trades bank_engine_r6_v21_trades.csv; controls bank_r6_v21_freeze.json.

### Round-6 closing census
- 14 cycles (136–149), all six workstreams gated through. Bankings: Cycles 138, 139, 140 (one NS3-geometry axis; best = C140, frozen as v21 at Cycle 149).
- **Final book v21: +₹83,650.50 Jan–Oct 2026 — ₹8,365.05/month vs the ₹15,000 floor; gap ₹66,349.50. Floor NOT met.** v21 supersedes v20 as the December candidate of record. November primary untouched.

## ROUND 7 (2026-11-02) — the untouched axes on the causal book (Cycles 150–161)

Gating reference: v21 (+₹83,650.50), reproduced exactly before scoring (with v20). All gating on causal times only. Full record: bank_engine_round7_2026-11-02.md.

- Cycle 150 WS1 V5 regeneration validation: frozen-parameter regen (min_target ₹500, cap_index 3) reproduces the frozen Bank V5 leg set EXACTLY (40 legs, 0 unresolved, 0 skipped) — PASS, variants trusted.
- Cycle 151 WS1 V5 min_target ₹250: book identical to v21 (+₹83,650.50, n=99, all controls identical) — EXACT NO-OP, nothing to bank.
- Cycle 152 WS1 V5 min_target ₹1,000: EXACT NO-OP (identical book).
- Cycle 153 WS1 V5 cap_index 5: EXACT NO-OP (identical book).
- Cycle 154 WS1 V5 cap_index 2: EXACT NO-OP (identical book). The Bank V5 selection is invariant across the whole knob grid — the filter/cap bind on the shared pool, never on Bank's picks. WS1 closed.
- Cycle 155 WS2 (lA) CE MIRROR (exact mirror of the frozen L1 engine; Bank's own population, Nifty verdict not imported): 25 legs, 21 admitted, sleeve −₹8,622.00 → book +₹75,028.50 (n=120, FT90 45.0) — REJECTED (net, June flip +560 → −5,893.50, FT90 dilution). Bank's (lA) edge is PE-only. Family closed.
- Cycle 156 WS3 Skill regeneration validation: frozen-window regen reproduces the frozen Skill sets EXACTLY (Jan–Sep 150/150, Oct 14/14; the 2026-10-28 CE 54000 / exp 2026-11-03 Nov-03-chain leg excluded symmetrically, named) — PASS.
- Cycle 157 WS3 Skill OR 09:15–09:45: 138 legs (vs 164 frozen-window) → book +₹77,994.50 (n=100, FT90 50.0, NC 0) — REJECTED (net −₹5,656; June flip +560 → −₹1,160). Frozen 09:15–09:30 OR stands. Closed.
- Cycle 158 WS4 strike ITM-100 BLANKET (whole construction shifted; real ITM candles, fetch still-missing 0, NC 0): +₹74,170.00 (n=101, FT90 49.5) — REJECTED on net (−₹9,480.50).
- Cycle 159 WS4 strike ITM-100 EXPIRY-DAY ONLY (NC 0): +₹79,450.50 (n=99, FT90 48.5) — REJECTED (net −₹4,200.00, FT90 dilution). The expiry-day ITM rule does not survive premium scoring on Bank. Strike axis closed; ATM stands.
- Cycle 160 WS5 square-off 15:10 re-gate: +₹80,329.50 — REJECTED on net (−₹3,321.00).
- Cycle 161 WS5 square-off 15:25 re-gate: +₹83,388.00 — REJECTED on net (−₹262.50). Incumbent 15:20 is the causal peak of {15:10, 15:20, 15:25} — the pre-audit banking is confirmed on causal data. WS5 closed.
- WS6 combinations: the round's banking set is empty, so no combination exists to gate — closed by statement.

### Round-7 closing census
- 12 cycles (150–161), all six workstreams gated through. **Bankings: none. Book v21 stands at +₹83,650.50 — ₹8,365.05/month vs the ₹15,000 floor; gap ₹66,349.50. Floor NOT met.**
- Process note: WS1's first run re-ran the candidate universe per variant (un-cached); killed at ~25 min before any score existed, fixed with per-month caching, re-run clean. No number from the killed run is used anywhere.
- Every axis Round 7 opened is now closed on causal data: V5 knobs (invariant), (lA) mirror (PE-only), Skill OR window (frozen stands), strike (ATM stands), square-off (15:20 confirmed). The gap needs a genuinely new causal signal family or forward data.

## ROUND 8 (2026-11-02) — NS1 causal neighbours + the December freeze of v21 (Cycles 162–167)

Gating reference: v21 (+₹83,650.50), causal book. All gating on causal times, full controls gate in the same run for every scored cell. Full record: bank_engine_round8_2026-11-02.md.

- Cycle 162 SANITY: frozen NS1 cell (room 1.5, window 14:30) regenerated set == v21's NS1 set (65 candidate legs); judge7 at the frozen cell reproduces v21 exactly (+₹83,650.50, n=99, FT90 49.5, placebo −₹4,313.50, NC 0).
- Cycle 163 WS1 NS1 room 1.25 (window 14:30): 67 candidates (+2 pass the room test) — taken book BYTE-IDENTICAL to v21 (+₹83,650.50, n=99). EXACT NO-OP; the marginal candidates are absorbed by key/band competition downstream. Nothing to bank.
- Cycle 164 WS1 NS1 room 1.75 (window 14:30): 64 candidates (−1) — taken book BYTE-IDENTICAL to v21. EXACT NO-OP; the removed candidate was not a taken leg. Nothing to bank.
- Cycle 165 WS1 NS1 window 15:00 (room 1.50): 67 candidates; exactly one added taken leg — 2026-09-03 PE second leg, entry 15:05 @ 588.0, square-off −₹466.00 → book +₹83,184.50 (n=100, FT90 49.0). REJECTED on net (−₹466.00) and FT90 dilution; no month flip (Sep +10,776.50 → +10,310.50). Placebo-twin NC 1 recorded (the added leg's +30-min entry has no candle path). NS1 axis closed on the causal book in both room directions and on window extension — the frozen cell stands, confirming Lesson 68's plateau vs the current book.
- Cycle 166 WS2 DECEMBER FREEZE: book v21 frozen as the December candidate in bank_engine_frozen.md (ROUND 8 block, §§1–12) — full tradeable specification with the admission/feature timing certification written in (§10), December expiry handling (§8: monthly rule, December date 2026-12-29 to be confirmed against the contract master), NC policy (§9: NC > 0 → PROVISIONAL, never a pass), and pre-registered December pass/kill (§11: PASS Dec net > 0 + audit clean + NC = 0; KILL Dec net ≤ −₹5,000 or any timing violation; floor-pace context Dec ≥ +₹15,000 printed beside, never as the test). Freeze written BEFORE the verification run.
- Cycle 167 WS3 REGENERATION VERIFICATION: the frozen specification regenerated through the causal pipeline reproduces v21 LEG-FOR-LEG (99 legs, 0 mismatches) and to the paisa (+₹83,650.50), full controls in the same run (timing 0, NC 0, placebo beaten, halves ≥ 0, ex-top-3 +₹54,610.50, re-sum exact). PASS. Evidence: bank_r8_regen.json; regenerated file bank_engine_r8_v21_regen_trades.csv.

### Round-8 closing census
- 6 cycles (162–167), all three workstreams completed. **Bankings: none. Book v21 stands at +₹83,650.50 — ₹8,365.05/month vs the ₹15,000 floor; gap ₹66,349.50. Floor NOT met.**
- The round's deliverable is forward-looking: v21 is now frozen as a fully specified, timing-certified, regeneration-verified December candidate with pre-registered pass/kill. The NS1 axis joins the closed axes (Rounds 5–7) — on causal data the existing families have no ungated neighbour left in this round's scope.
