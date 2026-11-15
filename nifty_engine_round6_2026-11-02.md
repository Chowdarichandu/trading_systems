# NIFTY engine — ROUND 6 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most); the primary's live producer already enters at confirmation, so November paper is causal by construction and was not re-scored.
Baseline at round open: **the CAUSAL BOOK** (Round-5 WS0) = +₹50,618.00 — 35 trades, FT 34.3%, 0.86/wk, pace ₹5,061.80/month, floor gap ₹99,382.00. Freeze: `nifty_engine_frozen.md` ROUND 6 (written before any Round-6 scoring).

**Gate calibration (pre-registered, applied uniformly):** the banking test is the **RELATIVE GATE** — net above the standing baseline, FT% not below the baseline's, frequency not below the baseline's, no baseline-green month flips red, no red month-ends, both halves ≥ 0, placebo (+30 min) beaten, ex-top-3 ≥ 0, timing audit clean, NOT_COMPUTED = 0, independent re-sum exact. The **OLD ABSOLUTE LINES** (FT ≥ 42.0%, frequency ≥ 1.00/wk — calibrated on the adopted book's inadmissible-inclusive figures, lesson 56) are **referred to the owner**: they are printed as STATUS for every verdict below and were never the banking test and never silently relaxed. Banking updates the standing baseline (supersession, Rounds 3–5 rule).

**Causality certification (lessons 46/52), restated for this round:** per-system entry times come from the merge's own frozen input files (WS0 sysmap); each system's signal bar strictly precedes its entry bar (Round-5 certificate); a confirmed key's admission bar t_k is the k-th earliest system entry — fully determined at t_k; strike = ATM100 at the spot 5-minute open of the admission bar; EXP0/calendar known always; geometry reads only bars ≥ the entry bar; entry price = the entry bar's open in the contract's own candles, with the timing audit requiring that bar to exist. 7 missing monthly contracts were fetched via the expired-instruments route (browser UA; all OK, 75–77 bars, entry bars verified). **Named NOT_COMPUTED:** the 2026-10-28 22500 PE leg on the weekly expiry 2026-11-03 — attempted once more through the route this round: **NO_KEY** (the registry holds no contract for that expiry; Rounds 3–5 found 0 contracts). It stays NOT_COMPUTED, named, never estimated; it appears only in the WS2 solo-Skill population.

## WS1 — Confirmation-native rebuild (Cycles 113–118)

Population: EXP0 keys; confirmed keys enter AT t_k with the ATM strike struck at t_k; book geometry. Cycle 113 (centre: systems = 2, window t2 ≤ 09:55, solo (lA) admitted) **reproduces the causal book leg-for-leg and to the paisa** (+₹50,618.00, 35 tr, audit 35/0, NC 0) — the native construction and the WS0 remedy are the same book; the grid below is measured against it.

| Cycle | Cell | Total | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 114 | systems = 3 | +31,352.50 | 16 | 43.8 | 0.39 | +17,104.00/+14,248.50 | +12,483.00 | +3,097.25 | FAIL: net, frequency | FT PASS · freq FAIL |
| 115 | window ≤ 10:30 | +43,186.25 | 49 | 32.7 | 1.21 | +18,090.50/+25,095.75 | −201.25 | +9,880.50 | FAIL: net (−7,431.75), FT | FT FAIL · freq PASS |
| 116 | window ≤ 11:30 | +46,593.75 | 57 | 31.6 | 1.40 | +24,998.50/+21,595.25 | −758.75 | +13,288.00 | FAIL: net (−4,024.25), FT | FT FAIL · freq PASS |
| 117 | no window | +44,645.75 | 59 | 30.5 | 1.45 | +21,528.50/+23,117.25 | −461.00 | +11,340.00 | FAIL: net (−5,972.25), FT | FT FAIL · freq PASS |
| 118 | solo = never | +41,400.50 | 28 | 32.1 | 0.69 | +19,877.75/+21,522.75 | +22,810.50 | +8,094.75 | FAIL: net, FT, frequency | FT FAIL · freq FAIL |

Reading: entered at their own confirmation bars, later confirmations are worth less, not more — every window widening buys frequency with negative-net legs. The 09:55 window on t2 is the peak of the admission axis. Cycle 118 prices the solo (lA) legs' in-book contribution at +₹9,217.50 (centre minus solo-never).

## WS2 — Solo-system causal books (Cycles 119–122)

Each system traded solo on the EXP0-filtered pool keys where it fired, entered at its OWN bar (ATM strike there), book geometry, gated whole-book vs the causal baseline.

| Cycle | Book | Total | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 119 | solo (lA) v2 | +34,533.25 | 41 | 26.8 | 1.01 | +27,563.50/+6,969.75 | +4,019.00 | +1,227.50 | FAIL: net (−16,084.75), FT | FT FAIL · freq PASS |
| 120 | solo V5 v2 | +25,145.00 | 29 | 31.0 | 0.71 | +4,501.00/+20,644.00 | −4,228.50 | −4,745.00 | FAIL: net, FT, frequency, flip (Feb), ex-top-3 | FT FAIL · freq FAIL |
| 121 | solo Skill V3 | +28,280.25 *computable subtotal* | 93 of 94 | 25.8 | 2.29 | +9,817.50/+18,462.75 | −3,205.10 | −5,184.75 | FAIL: net, FT, flip (Jul), ex-top-3, audit, **NC = 1** | FT FAIL · freq PASS |
| 122 | solo Volrix (b) | +22,540.25 | 8 | 37.5 | 0.20 | +5,455.25/+17,085.00 | +5,552.50 | −2,718.50 | FAIL: net, frequency, flips (Mar, Jul), ex-top-3 | FT FAIL · freq FAIL |

*Cycle 121's total is the computable subtotal over 93 legs; the 94th leg is the named NOT_COMPUTED leg (2026-10-28 22500 PE, weekly expiry 2026-11-03, NO_KEY). It is not a book figure and was never estimated.* No solo system beats the confirmed book: the confirmation requirement itself carries the causal book's value (lesson 58).

## WS3 — G7 geometry re-grid on the causal population (Cycles 123–127)

Standing book entering WS3: the causal legs (WS1/WS2 banked nothing, so the causal population stands). Grid: lock ∈ {40, 50, 60} × TGT2 ∈ {150, 175}; centre (50, 175) = standing geometry (validation by construction). C123–C124 gated vs the causal book; after C124 banked, C125–C127 gated vs the lock60 book (+₹51,118.50).

| Cycle | Cell | Total | Δ vs its baseline | Relative gate | Old lines (status) |
|---|---|---|---|---|---|
| 123 | lock 40 / TGT2 175 | +50,117.50 | −500.50 | FAIL: net | FT FAIL · freq FAIL |
| 124 | **lock 60 / TGT2 175** | **+51,118.50** | **+500.50** | **BANKED — all legs pass** (FT 34.3%, 0.86/wk, halves +25,705.75/+25,412.75, placebo +20,094.00, ex-top-3 +17,812.75, no flips, audit 35/0, NC 0, re-sum exact) | FT FAIL · freq FAIL |
| 125 | lock 40 / TGT2 150 | +45,401.75 | −5,716.75 | FAIL: net | FT FAIL · freq FAIL |
| 126 | lock 50 / TGT2 150 | +45,902.25 | −5,216.25 | FAIL: net, flip | FT FAIL · freq FAIL |
| 127 | lock 60 / TGT2 150 | +46,402.75 | −4,716.25 | FAIL: net | FT FAIL · freq FAIL |

The adopted era's lock (+50) does not survive re-gridding on the causal population — the peak moves to +60 — and TGT2 +175 dominates +150 on every row (lesson 59).

## WS4 — Square-off axis (Cycles 128–129)

On the standing book after WS3 (causal legs × lock60/TGT2-175):

| Cycle | Cell | Total | Δ | Relative gate | Old lines (status) |
|---|---|---|---|---|---|
| 128 | square-off 14:45 | +43,614.25 | −7,504.25 | FAIL: net, FT (28.6%) | FT FAIL · freq FAIL |
| 129 | **square-off 15:20** | **+54,102.00** | **+2,983.50** | **BANKED — all legs pass** (FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00, ex-top-3 +20,637.00, no flips, audit 35/0, NC 0, re-sum exact) | FT FAIL · freq FAIL |

## WS5 — Combination (Cycle 130)

The round's two bankings (C124 lock +60; C129 square-off 15:20) combined and re-gated whole-book against the **round-opening** baseline (causal book at book geometry): **+₹54,102.00 — all relative-gate legs pass** (net +3,484.00 over round-open; FT and frequency unchanged; no green month flips red; halves both ≥ 0; placebo beaten; ex-top-3 +20,637.00; audit 35/0; NC 0; re-sum exact). Old absolute lines' status: FT FAIL (34.3% < 42.0%) · frequency FAIL (0.86 < 1.00/wk) — status only. No other combinations exist (the two bankings are both geometry on the same legs and were applied sequentially under supersession; WS1/WS2 banked nothing).

## Ending scorecard

| | |
|---|---|
| Standing book (December causal candidate, frozen) | Causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock **+60**, TGT2 +175, square-off **15:20**) |
| Jan–Oct 2026 total | **+₹54,102.00** |
| Monthly pace | **₹5,410.20** vs ₹15,000 floor |
| **Remaining gap** | **₹95,898.00** |
| Round delta vs causal baseline | **+₹3,484.00** (C124 +₹500.50; C129 +₹2,983.50) — both banked under the relative gate |
| Trades / FT / frequency | 35 / 34.3% / 0.86 per week |
| Months | Jan +17,096.75 · Feb +12,789.25 · Mar +7,895.00 · Apr +210.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,998.75 · Aug −1,701.00 · Sep +4,652.75 · Oct +16,480.50 |
| Halves | +27,581.00 / +26,521.00 |
| Placebo (+30 min) | +22,876.00 — beaten |
| Ex-top-3 | +20,637.00 |
| Timing audit / NC / re-sum | 35/0 · 0 · exact |
| Old absolute lines (status only, referred to owner) | FT ≥ 42.0% **FAIL** (34.3%) · frequency ≥ 1.00/wk **FAIL** (0.86) |
| December candidate of record | Chandu's adopted book (+₹114,921.75 as recorded, waivers unchanged) — annotated lineage: causal +₹50,618.00 at book geometry → **+₹54,102.00** after Round-6 geometry bankings |
| Named NOT_COMPUTED | 2026-10-28 22500 PE (weekly expiry 2026-11-03) — NO_KEY on this round's route attempt; never estimated |

**Round-6 totals:** 18 cycles (113–130): 1 validation + WS1 5 + WS2 4 + WS3 5 + WS4 2 + WS5 1. Banked: **2** (C124, C129). The confirmation concept, rebuilt honestly at its own bars, peaks exactly at its frozen centre on every admission axis and in every solo decomposition; the round's only gains were exit-geometry corrections on the causal population. The floor is not reached: the honest book's gap (₹95,898.00) is a signal-population problem, not a geometry or admission problem — the causal population is 35 legs in 10 months. Records: `nifty_engine_frozen.md` (Round-6 freeze + results/candidate freeze), `nifty_engine_log.md`, `nifty_engine_lessons.md` (57–60), `nifty_engine_state.json` (cycle 130, run6 block), per-cycle summaries `nifty_engine_run3r6_*_summary.json`, final book `nifty_engine_r6_final_book.json`, harnesses `nifty_engine_r6_*.py`. November primary untouched throughout.
