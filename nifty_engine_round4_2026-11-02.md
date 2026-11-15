# NIFTY engine — ROUND 4 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most).

## ⚠️ Headline: Round 3's only banking was look-ahead — RETRACTED before any Round-4 scoring

Round 4 opened by re-verifying the starting book's signature feature against `spot_daily.csv`. The Round-3 Cycle-40 signature — frozen as "PE leg whose **prior trading day's** spot return ∈ (−0.50%, −0.25%)" — was computed by a helper (`pdret`) that returns the leg day's **own** close-to-close return. Verification, all six legs:

| Leg | Recorded "prior-day" value | Own-day return (actual) | TRUE prior-day return |
|---|---|---|---|
| 2026-06-29 PE | −0.310% | −0.310% | +0.166% |
| 2026-08-11 PE | −0.456% | −0.456% | +0.054% |
| 2026-08-19 PE | −0.317% | −0.317% | −0.547% |
| 2026-08-31 PE | −0.394% | −0.394% | +0.352% |
| 2026-09-07 PE | −0.496% | −0.496% | +0.102% |
| 2026-10-21 PE | −0.339% | −0.339% | −1.111% |

The recorded values match the own-day column exactly; the true prior-day returns show no band. The rule selected legs by how their own day ended — information available ~6 hours after entry. **Untradeable; the +₹1,426.75 Cycle-40 banking is void.** The engine's timing audit verified entry bars but never feature timing; that hole is named (lesson 46) and every Round-4 feature was certified causal in its freeze.

**Corrected baseline:** December candidate = the ADOPTED book (CH3-R × lock50/TGT2-175, monthly legs only) = **+₹114,921.75** — re-verified in the Round-4 harness (44 trades, FT 45.5%, 1.08/wk, halves +65,655.50/+49,266.25, placebo +63,269.50 beaten, ex-top-3 +81,456.75, timing audit 44/0, NC 0, re-sum exact). **Pace ₹11,492.18/month; floor gap ₹35,078.25** (not ₹33,651.50 as reported after Round 3). All Round-4 gating ran against this clean book under the supersession rule.

## Workstream verdicts (26 gated cycles, Cycles 74–99)

### WS1 — May-wound signature: diagnosis complete, NO signature, NO cycle
May = 4 PE legs: 11 May −₹3,470 (stop; premium MFE +16.9/MAE −75.1), 12 May **+₹8,087** (runner), 13 May −₹3,470 (stop; MFE +37.9/MAE −101.2), 18 May −₹3,470 (stop; MFE +16.5/MAE −145.4). Causal scan (gap, pre-entry move/range, TRUE prior-day return, prior-day range, bias position, prior vol, entry premium, DTE — single bands + PE conjunctions, book-wide): no band separates the losers into a negative, winner-free set. The only negative boxes are May-fitted premium boxes, contradicted by the book (PE legs with premium ≥ ₹290 net +₹28,361 — the March high-premium PEs are +₹11,155 winners). **May's −₹2,323 is variance in a 4-leg month, not an entry-identifiable state.**

### WS2 — Volrix parameter grid (Cycles 74–91): nothing banked; frozen parameters are the peak
Construction: confirmation-toggle on recorded pool legs; vintage calibration at −1.0% disclosed in frozen.md (two marginal trigger days, −1.010%/−1.026%, excluded so the centre reproduces the frozen book). Centre cell (Cycle 82) reproduced +₹114,921.75 exactly ✓. Book-exit totals by (trigger, cooldown): −0.75% → 102,575.25 / 103,986.75 / 94,841.50; −1.0% → 114,921.75 / 114,921.75 / 110,658.00; −1.25% → 107,580.25 / 96,645.25 / 100,115.25. Plain-exit (G0 on Volrix legs) is uniformly worse — on the frozen set it costs ₹17,361.50 (→ ₹97,560.25). Every cell failed net vs the candidate (two −1.25% cells also failed frequency). **Volrix axis closed.**

### WS3 — Nifty second-leg family (Cycles 92–97): REJECTED — 3 legs, 3 full stops
NS1 transplant onto the candidate book (10 qualifying base-leg days). All six room {1.4/1.5/1.6} × window {14:00/14:30} cells produce the identical 3 legs (permutations non-binding; found crossings have room_ratio ≥ 4.86; one 14:05 crossing was deduped against the book). Two contracts were fetched via the expired-instruments route (75 bars each, entry bars verified) — no NOT_COMPUTED anywhere. The legs:

| Second leg | Entry | Premium | Exit | Net |
|---|---|---|---|---|
| 2026-02-02 PE 24700 | 11:10 | 321.15 | stop 11:30 | −₹3,470.00 |
| 2026-03-02 PE 24600 | 14:00 | 373.60 | stop 14:00 (entry bar) | −₹3,470.00 |
| 2026-05-11 CE 24000 | 13:55 | 360.85 | stop 14:45 | −₹3,470.00 |

Book with second legs: **+₹104,511.75** (47 trades, FT 42.6%, 1.16/wk; May −2,323.00 → −5,793.00) — fails net only, at every cell. **Afternoon OR re-crossings after a resolved morning leg are counter-trend traps in Nifty; the family does not transplant from Bank.**

### WS4 — Day-state admission features: NO cycles (pre-registered method outcome)
Tercile nets on the 44 legs — every tercile of every feature is positive: gap % → +36,567.75 / +34,832.25 / +43,521.75; first-30 range ratio → +19,641.75 / +60,695.75 / +34,584.25; prior-day range expansion → +23,983.75 / +60,104.25 / +30,833.75. Boundaries frozen in the WS4 addendum. The frozen rule (skip a tercile only if its net < 0) yields no candidate. **No admission axis exists in this book.**

### WS5 — Premium-band filter (Cycles 98–99): both rejected
- Top-decile skip (premium > 407.80): **+₹104,426.75** (40 tr, FT 47.5%, 0.99/wk) — fails net + frequency. The top decile holds three −₹220 BE legs and the +₹11,155 March winner.
- Bottom-decile skip (premium < 128.45): **+₹108,265.00** (40 tr, FT 47.5%, 0.99/wk) — fails net + frequency. The cheapest legs include +₹3,137.25 and +₹4,304.00 winners.
Premium level is not a bleed marker at either tail.

### WS6 — Combinations: none (no Round-4 bankings exist to combine). Closes by statement per its freeze.

## Ending scorecard — December candidate (unchanged by banking, corrected by retraction)

| | |
|---|---|
| Book | CH3-R × lock50/TGT2-175 (adopted by Chandu 2026-11-02; waivers of record unchanged) |
| Jan–Oct 2026 total | **+₹114,921.75** |
| Monthly pace | **₹11,492.18** vs ₹15,000 floor |
| **Remaining gap** | **₹35,078.25** |
| Trades / FT / frequency | 44 / 45.5% / 1.08 per week |
| Months | Jan +23,974.75 · Feb +14,882.25 · Mar +21,650.00 · Apr +7,471.50 · May −2,323.00 · Jun +6,157.25 · Jul +17,054.50 · Aug −5,187.25 · Sep +4,926.00 · Oct +26,315.75 |
| Halves | +65,655.50 / +49,266.25 |
| Placebo (+30 min) | +63,269.50 — beaten |
| Ex-top-3 | +81,456.75 |
| Timing audit / NC / re-sum | 44/0 · 0 · exact |

**Round-4 totals:** 26 gated cycles + 2 diagnoses; banked: **none**. Net effect on the candidate: ₹0 by banking, −₹1,426.75 by correction of Round 3's look-ahead banking. Every family the brief directed at the gap — May signature, Volrix grid, second legs, day-state admission, premium bands — was measured on the clean book with full controls and rejected (or, for WS1/WS4, closed at diagnosis under rules frozen before scoring). Records: `nifty_engine_frozen.md` (Round-4 section incl. retraction + all freezes/verdicts), `nifty_engine_log.md`, `nifty_engine_lessons.md` (46–51), `nifty_engine_state.json` (cycle 99, run4 complete), per-cycle summaries `nifty_engine_run3r4_c*_summary.json`, harnesses `nifty_engine_r4_*.py`.
