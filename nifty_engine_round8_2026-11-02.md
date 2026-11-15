# NIFTY engine — ROUND 8 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most); the primary's live producer already enters at confirmation, so November paper is causal by construction and was not re-scored.
Baseline at round open: **the ROUND-6/7 STANDING BOOK** = +₹54,102.00 — causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20), FT 34.3%, 0.86/wk, pace ₹5,410.20/month, floor gap ₹95,898.00. Freeze: `nifty_engine_frozen.md` ROUND 8 (written before any Round-8 candidate scoring; the March diagnosis below is a pre-freeze re-score of the already-gated Round-7 Cycle-133 construction, a named ingredient).

**Gate calibration (pre-registered, applied uniformly):** the banking test is the **RELATIVE GATE** — net above the standing baseline, FT% not below the baseline's, frequency not below the baseline's, no baseline-green month flips red, no red month-ends, both halves ≥ 0, placebo (+30 min) beaten, ex-top-3 ≥ 0, timing audit clean, NOT_COMPUTED = 0, independent re-sum exact. The **OLD ABSOLUTE LINES** (FT ≥ 42.0%, frequency ≥ 1.00/wk — calibrated on the adopted book's inadmissible-inclusive figures, lesson 56) remain **referred to the owner**: printed as STATUS for every verdict below, never the banking test, never silently relaxed. WS2 Cycle 146 is additionally reported under two FT readings, frozen in advance: (i) FT90 (the banking basis) and (ii) own-target FT (decision support only, never banked on).

**Causality certification (lessons 46/52), restated for this round:** gap g(D) and the prior-day trend pdret_prior(D) are both fully known at D's 09:15 open (the lesson-46 own-day artefact `pdret` is used nowhere); entries at 09:35 or 10:05 are strictly after; the WS3 afternoon range is complete at 13:00 and its entry bar is strictly after the break bar whose close completes the signal; strikes are ATM100 at the entry bar's spot open; exit geometry reads only bars at/after entry. Fetches this round via the expired-instruments route (browser UA): Cycle 145 13/13 OK, Cycle 147 101/101 OK; NC = 0 at every scoring. **Named NOT_COMPUTED (carried):** the 2026-10-28 22500 PE leg on the weekly expiry 2026-11-03 — in no Round-8 population; stays NOT_COMPUTED, named, never estimated.

**March diagnosis (pre-freeze, diagnosis only).** The Round-7 fade regeneration reproduces the record to the paisa (49 legs, +₹32,127.15 standalone). The March flip is the sleeve's March sum, **−₹16,128.50 over 11 legs**: seven full stops at −₹3,470 (03-05, 03-10, 03-13, 03-17, 03-19, 03-23, 03-27), two BE stops, two runner wins — March's gaps largely CONTINUED intraday. By the causal prior-day trend: the against-trend half (24 legs, +₹25,062.65) holds −₹13,670.00 of the March damage; the with-trend half (25 legs, +₹7,064.50) holds −₹2,458.50, which alone would not flip March (+7,895.00 − 2,458.50 = +5,436.50). WS1(b)'s exact form was frozen from this diagnosis: **with-trend only, trend = sign of pdret_prior** (the brief's named axis in the engine's certified definition); the prior-day-intraday definition variant was deliberately not run — no definition-shopping.

## Cycle 141 — Validation

The Round-8 harness re-scores the standing book leg-for-leg: **+₹54,102.00, 35 trades, FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact — VALID.** Machinery check: the parameterised `replay_r8` equals `replay_r5` leg-for-leg on the standing book. ABS status: FT FAIL / freq FAIL.

## WS1 — Gap-fade refined (Cycles 142–145)

One axis at a time on the Round-7 FADE construction (54 gap days at 0.50%; each cell's exclusions applied identically), gated as an addition to the standing book.

| Cycle | Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | March (combined) | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 142 thr 0.75% | +10,882.00 (27 legs) | +64,984.00 | 62 | 29.0 | 1.53 | +19,602.00/+45,382.00 | +26,790.00 | +31,519.00 | +5,866.50 | FAIL: FT only | FT FAIL · freq PASS |
| 143 thr 1.00% | +3,458.00 (13 legs) | +57,560.00 | 48 | 33.3 | 1.18 | +30,732.50/+26,827.50 | +22,141.50 | +24,095.00 | +5,866.50 | FAIL: FT only | FT FAIL · freq PASS |
| 144 with-trend | +7,064.50 (25 legs) | +61,166.50 | 60 | 30.0 | 1.48 | +22,007.00/+39,159.50 | +38,835.75 | +27,701.50 | +5,436.50 | FAIL: FT only | FT FAIL · freq PASS |
| **145 entry 10:05** | **+33,624.75 (49 legs)** | **+87,726.75** | 84 | **35.7** | 2.07 | +44,841.50/+42,885.25 | +50,702.75 | +54,261.75 | **−8,376.50** | **FAIL: March flip only** | FT FAIL · freq PASS |

Reading: **the fade refinement's best cell is Cycle 145 (entry 10:05)** — and its failing leg is exactly one: the March green-to-red flip. The delayed entry is worth more than the 09:35 original standalone (+₹33,624.75 vs +₹32,127.15) and it is the first fade form whose full-target rate does NOT dilute the book (combined FT 35.7% ≥ 34.3% — the later entry skips the opening noise that capped the early entries below +90). Everything else passes with room: net +₹33,624.75 over baseline, frequency 2.07/wk, halves strongly positive, placebo beaten by ₹37,024.00, ex-top-3 +54,261.75, no red month-ends, audit clean, NC 0. It fails because March at 10:05 is still −₹16,271.50 for the sleeve: March's gaps continued all session, so no entry delay inside the morning escapes them. The three restricted forms (142–144) all cure March exactly as diagnosed and all fail on FT dilution alone — restricting the population removes too many of the legs that reach +90. Restriction and delay each fix one wound and leave the other; the combination (restriction × late entry) was not frozen this round and is recorded as the family's one remaining untested cell for a future round's freeze — combining them in-round, after seeing both answers, would be tuning on the gate's output (lessons 65–66).

## WS2 — Expiry sleeve, own geometry (Cycle 146)

Rebuild validation (freeze-required, before scoring): the rebuilt 15-leg sleeve under standing geometry reproduces Cycle 138 exactly — combined +₹57,753.75, sleeve +₹3,651.75, FT 32.0%, NC 0. The sleeve legs were then traded under **expiry geometry (stop −40, BE arm +50, tgt1 +60 → lock +30, TGT2 +110, square-off 15:20)**; standing legs unchanged.

| Reading | Sleeve (15 legs) | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| (i) FT90 — banking basis | −2,406.25 (FT90 count 3/15) | +51,695.75 | 50 | 30.0 | 1.23 | +23,468.00/+28,227.75 | +17,434.25 | +18,230.75 | FAIL: net (below baseline), FT, Apr flip (+210.00 → −880.00) |
| (ii) Own-target FT — decision support only | −2,406.25 (own-target count 5/15) | +51,695.75 | 50 | 34.0 | 1.23 | (same) | (same) | (same) | would-bank FALSE: net, FT (34.0 < 34.3) and the April flip all fail under this reading too |

Reading: the own-geometry hypothesis is dead, not merely unbankable. Truncating the sleeve to a +60/+110 runner with a −40 stop turns it negative (−₹2,406.25 from +₹3,651.75): the sleeve's few trending legs pay for the rest precisely through the standing +90/+175 runner, and the tighter stop kills two of them first (the Cycle-35 EW-G7 shape on a second population, lesson 67). Under the own-target FT reading the cycle still fails on three legs — so this form is **not** added to the flagged list: it is worse than the flagged standing-geometry form on every axis. ABS status (FT90 reading): FT FAIL / freq PASS.

## WS3 — Afternoon-range sleeve (Cycle 147)

Population (pre-registered): afternoon range = spot bars 12:00–12:55; first bar ≥ 13:00 closing outside the range is followed in the break direction, entry the next bar, monthly expiry, EXP0 skip, standing-key exclusions → **150 legs** (13 exclusions named in the cycle record).

| Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|
| −8,056.25 (150 legs) | +46,045.75 | 185 | 11.9 | 4.56 | +26,416.75/+19,629.00 | +4,364.75 | +12,580.75 | FAIL: net, FT | FT FAIL · freq PASS |

Reading: midday range breaks on Nifty are noise continuations — a near-daily population that loses standalone and dilutes FT to 11.9%. The family is closed with a full gated run; with lesson 49, the afternoon-session opening-range space for Nifty is closed in both constructions (lesson 68).

## WS4 — Combinations and closure (Cycles 148–149)

No workstream banked, so there are no combinations to re-gate (freeze rule). **Cycle 148 (closure):** the standing book re-gated whole-book vs the round-open baseline — +₹54,102.00, every quality leg intact (FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00 beaten, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact); the only non-passing leg is net-above-baseline, trivially, because the book IS the baseline. **Cycle 149 (candidate freeze verification):** the same full controls pass re-run as the round's closing record — identical figures. ABS status for the standing book: FT FAIL (34.3%) · freq FAIL (0.86) — status only.

## Flagged list — restated on the ending book (unchanged from round open)

| Flagged item | Form | Adoption value | Combined if adopted | Gate status |
|---|---|---|---|---|
| Expiry-day Skill sleeve (R7 C138) | Standing geometry | **+₹3,651.75** | +₹57,753.75 | FLAGGED — fails the FT leg only (34.3 → 32.0); owner decision pending; NOT adopted |
| Expiry-day sleeve, own geometry (R8 C146) | tgt1 +60/lock +30/TGT2 +110/stop −40 | −₹2,406.25 | +₹51,695.75 | REJECTED under both FT readings — not flagged |
| Gap-fade entry-10:05 (R8 C145) | R7 fade construction, entry 10:05 | **+₹33,624.75** | +₹87,726.75 | NOTED OBSERVATION — fails the March flip leg only; every other leg passes incl. FT; recorded for owner visibility; NOT adopted |

## Ending scorecard

| | |
|---|---|
| Standing book (December causal candidate, unchanged) | Causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20) |
| Jan–Oct 2026 total | **+₹54,102.00** |
| Monthly pace | **₹5,410.20** vs ₹15,000 floor |
| **Remaining gap** | **₹95,898.00** |
| Round delta | **₹0.00** — 0 bankings (WS1's best cell and the flagged expiry form both refused on single gate legs, recorded with their failing legs named) |
| Trades / FT / frequency | 35 / 34.3% / 0.86 per week |
| Months | Jan +17,096.75 · Feb +12,789.25 · Mar +7,895.00 · Apr +210.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,998.75 · Aug −1,701.00 · Sep +4,652.75 · Oct +16,480.50 |
| Halves | +27,581.00 / +26,521.00 |
| Placebo (+30 min) | +22,876.00 — beaten |
| Ex-top-3 | +20,637.00 |
| Timing audit / NC / re-sum | 35/0 · 0 · exact |
| Old absolute lines (status only, referred to owner) | FT ≥ 42.0% **FAIL** (34.3%) · frequency ≥ 1.00/wk **FAIL** (0.86) |
| December candidate of record | Chandu's adopted book (+₹114,921.75 as recorded, waivers unchanged) — causal lineage unchanged by this round: **+₹54,102.00** after Round-6 geometry bankings |
| Named NOT_COMPUTED | 2026-10-28 22500 PE (weekly expiry 2026-11-03) — not in any Round-8 population; never estimated |

**Round-8 totals:** 9 cycles (141–149): validation 1, WS1 4, WS2 1, WS3 1, WS4 2 (closure + freeze verification). Banked: **0**. The fade is now measured in five gated forms — real in all five, bankable in none: the restricted forms fail FT alone, the late-entry form fails the March flip alone, and the one combination that addresses both was deliberately not run unfrozen. The expiry sleeve's own-geometry form is dead under both FT readings, leaving the standing-geometry form as the owner's flagged decision (+₹3,651.75). The afternoon-range family is closed. Records: `nifty_engine_frozen.md` (Round-8 freeze + results), `nifty_engine_log.md`, `nifty_engine_lessons.md` (65–68), `nifty_engine_state.json` (cycle 149, run8 block, flagged list restated), per-cycle summaries `nifty_engine_run3r7_r8_c14*` / `nifty_engine_run3r8_r8_c146*`, harnesses `nifty_engine_r8_harness.py`, `nifty_engine_r8_diag_march.py`, `nifty_engine_r8_stage{1,2,3}.py`. November primary untouched throughout.
