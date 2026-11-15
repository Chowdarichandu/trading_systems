# Bank Nifty Engine — ROUND 4 (2026-11-02, Cycles 64–114)

Brief: starting from book v17 (+₹107,930.00 Jan–Oct 2026, gap ₹42,070 to the ₹1,50,000 floor pace), find a version of the flagged Cycle-63 stack (v17 + NS3 + S3-A + S3-E = +₹127,369.50, 108 trades, failing only FT90 — 57 of 108 full targets vs 58 needed) that passes FT90 on its own merits, and keep widening the search across six workstreams. All definitions were frozen in `bank_engine_frozen.md` (ROUND 4 appendix) before scoring; diagnosis in `bank_r4_diag.json`; every candidate premium-scored under the full controls gate in the same run (timing/leak audit, +30-min placebo, halves, month table, ex-top-3, independent re-sum). NOT_COMPUTED = 0 throughout. Paper only, real money ₹0. November primary untouched.

## Headline result

**The stack now passes FT90 on its own merits — no waiver needed.** Two displacements:

- **Cycle 88 → book v18 = +₹128,048.00** (106 trades, FT90 53.8% = 57/106): v17 + NS3 restricted to the **GD+GU sublegs** + S3-A + S3-E. NS3's FT90-dilutive slice was its FLAT sublegs (2 admitted legs, −₹678.50, FT90 0/2); excluding them lifts the stack over the guard at full net.
- **Cycle 102 → book v19 = +₹133,898.00** (106 trades, FT90 53.8%): v18 with the NS3(GD+GU) legs on NS3's own best geometry (stop −50 / target +90 / lock +65 / second target +175). The geometry's full +₹5,850 gain survives the GD+GU restriction.

**Ending scorecard — book v19** (premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE): **+₹133,898.00 Jan–Oct 2026 = ₹13,389.80/month vs the ₹15,000 floor; gap ₹16,102.00.** 106 trades, 2.61/week, FT90 53.8% (57/106), no red month-ends, halves +₹106,561.00 / +₹27,337.00, placebo +₹11,211.50 beaten, ex-top-3 +₹104,858.00, timing audit clean, re-sum exact. Months: Jan +30,893.00 · Feb +26,878.00 · Mar +20,850.00 · Apr +5,090.00 · May +22,850.00 · Jun −5,360.00 · Jul −11,400.00 · Aug +8,806.50 · Sep +10,681.00 · Oct +24,609.50. Composition: base 82; NS3(GD+GU)@own-geometry 17 legs +₹21,208.00 (FT90 9); S3-A 6 legs +₹2,280.00; S3-E 1 leg +₹2,480.00; S3-D 0 (keys consumed). Trades: `bank_engine_r4_v19_trades.csv`.

**FT90 status of the best stack variant:** v19 reaches the full +90 target on 57 of 106 legs = 53.8%, which meets the gate's requirement (≥ the incumbent v17's 53.7%, 57 legs needed at n=106) — it passes every gate leg including FT90. The Round-3 flagged stack (+₹127,369.50, 52.8%) is superseded and its waiver question is moot.

## Workstream verdicts

**WS1 — NS3's own exit geometry (Cycles 64–81, 18 cells × 2 assemblies).** No banking. FT90 is path-determined under this grid: all nine trig-90 cells hold the stack at exactly 57/108; trig-75 cells CUT it to 49.1–50.9% (arming at +75 exits legs before their paths touch +90). Geometry moves net only — best cell T90L65G175: full stack +₹133,219.50 (passes vs the flagged stack, FT90-only failure vs v17); v17+NS3-only assembly +₹128,459.50.

**WS2 — NS3 admission refinement (Cycles 82–88).** Four bankings vs v17: premium <400 (+₹119,818.00, FT90 54.7%), DTE ≤7 (+₹117,820.00, FT90 54.7%), GD only (+₹127,288.00, FT90 53.8%), GD+GU (+₹128,048.00, FT90 53.8% → v18). Rejected on FT90: premium ≥550 (52.0%), DTE >7 (52.0%). DTE ≥1 (+₹129,089.50) fails FT90 vs v17 by one leg (57/107 = 53.3%) while passing vs the flagged stack.

**WS3 — Setup-3 completion (Cycles 89–96).** Standalone family nets: S3-F +₹699, S3-G +₹699 (identical admitted set), S3-H −₹200, S3-I −₹960, S3-J +₹1,520 — all FT90-fail standalone. Inside the stack, every positive cell admits **zero** legs (all candidate keys already owned). The Setup-3 definition space is exhausted.

**WS4 — Near-miss conversion audit + one candidate (Cycle 97).** Exactly 3 near-miss legs (MFE ∈ [75, 90)); two are unconvertible in principle (2026-06-09's full-day path max is +89.9; 2026-08-27 was alive at the square-off). Only 2026-07-14 (stopped 11:10, day path max +104.0) could ever convert. Under the frozen separator criterion, DTE ≥ 14 separates (near-miss rate 10.3% vs 0%, 3/3 held, 46% of converted legs); premium ≥550 (61%) and entry <11:00 (72%) fail the converted-share leg. The single candidate — DTE≥14 legs keep their own assembly with stop widened to −65 (own-assembly reconstruction verified exact on all 61 main + 59 placebo legs) — **banked: +₹118,069.50, FT90 53.7% (58/108, the 2026-07-14 leg converted)**. It pays ₹9,300 of extra stop distance for that one conversion, so it never displaces the tighter books.

**WS5 — Entry-state features (Cycles 98–101).** All four fail: range30 ≤ trailing median (+₹88,329.50, FT90 47.1, 1.72/wk), range30 > median (+₹60,930.00, April flips red, 1.63/wk), drop gap-T3 (+₹105,713.50, 1.82/wk), drop gap-T1 (+₹79,870.50, April flips, 1.55/wk). Tercile cuts verified against the frozen diagnosis (−0.208%/+0.138% computed vs −0.210/+0.139 frozen). The stack earns in both range states and all gap terciles; the axis is closed.

**WS6 — Combinations (Cycles 102–114).** Cycle 102 banked and displaced (→ v19, above). Also banked vs v17 without displacing: C103 v18 × WS4 transform (+₹118,748.00, FT90 54.7%); C104 GD+GU ∧ premium<400 (+₹121,538.00, FT90 55.3%; C106 GD ∧ premium<400 is the identical book); C105 GD+GU ∧ DTE≤7 (+₹119,540.00, FT90 55.3%); C110 premium<400 ∧ DTE≤7 (+₹115,340.00, FT90 54.3%); C111 triple intersection (+₹117,060.00, FT90 54.8%); C112 premium<400 @ geometry (+₹127,238.00, FT90 55.3%); C113 DTE≤7 @ geometry (+₹124,490.00, FT90 55.3%); C114 v19 × WS4 transform (+₹124,598.00, FT90 54.7%). C107–109: S3-F/G/J on v18 admit zero legs (totals identical to v18).

## Round census

51 cycles (64–114); 15 bankings vs v17; 2 displacements (v18, v19); round gain **+₹25,968.00** over v17. The floor is not reached — Bank ends Round 4 at ₹13,389.80/month, ₹16,102 short over Jan–Oct — but the round's central question is closed: the stack family is fully bankable under the unmodified gate. Every mandated workstream is measured and closed (geometry grid, admission subsets, Setup-3 space, the single audit-permitted candidate, day-state features, combinations). What remains outside this mandate: a genuinely new leg family, or December's fresh data.

Records: `bank_engine_log.md` (Round-4 section), `bank_engine_lessons.md` (lessons 56–63), `bank_engine_frozen.md` (v18 + v19 freezes), `bank_engine_state.json` (round4 block), results JSONs `bank_r4_ws1/ws2/ws3/ws4/ws5/ws6/ws6b/ws6c_results.json`, `bank_r4_diag.json`, freeze files `bank_r4_v18_freeze.json` / `bank_r4_v19_freeze.json`.
