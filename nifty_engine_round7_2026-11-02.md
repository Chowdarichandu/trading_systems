# NIFTY engine — ROUND 7 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most); the primary's live producer already enters at confirmation, so November paper is causal by construction and was not re-scored.
Baseline at round open: **the ROUND-6 STANDING BOOK** = +₹54,102.00 — causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20), FT 34.3%, 0.86/wk, pace ₹5,410.20/month, floor gap ₹95,898.00. Freeze: `nifty_engine_frozen.md` ROUND 7 (written before any Round-7 scoring).

**Gate calibration (pre-registered, applied uniformly):** the banking test is the **RELATIVE GATE** — net above the standing baseline, FT% not below the baseline's, frequency not below the baseline's, no baseline-green month flips red, no red month-ends, both halves ≥ 0, placebo (+30 min) beaten, ex-top-3 ≥ 0, timing audit clean, NOT_COMPUTED = 0, independent re-sum exact. The **OLD ABSOLUTE LINES** (FT ≥ 42.0%, frequency ≥ 1.00/wk — calibrated on the adopted book's inadmissible-inclusive figures, lesson 56) remain **referred to the owner**: printed as STATUS for every verdict below, never the banking test, never silently relaxed. This round tested NEW SIGNAL FAMILIES only; Rounds 1–6 spaces (confirmation definition, solo books, geometry, admissions) were not re-run.

**Causality certification (lessons 46/52), restated for this round:** every family's decision bar and entry bar are named in the Round-7 freeze, and in every family the entry bar is strictly after the bar that completes the signal (gap: 09:15 prints → 09:35 entry; (lA) mirror: signal-bar close → next bar; WS2: Bank admission t2_B → state read strictly before the Nifty bar, sleeve entry at t2_B + 5 min; WS4: Skill's own entry bar, whose signal bar precedes it per the Round-5 WS0 certificate). Strike = ATM100 at the entry bar's spot open. Cross-index times come from the same frozen merge input files as the Nifty sysmap, filtered to BANKNIFTY. (lA) machinery validation: the unmodified PE construction reproduced the recorded Jan–Sep (lA) signal times **42/42 exactly** (run pre-freeze as a machinery check and re-asserted inside the WS3 generator). Fetches this round via the expired-instruments route (browser UA; discovery built 3 contracts files): WS1 69/69 OK, WS3 10 jobs fetched and all verified present at scoring (NC 0), WS4 15/15 OK. **Named NOT_COMPUTED (carried):** the 2026-10-28 22500 PE leg on the weekly expiry 2026-11-03 — not in any Round-7 population; stays NOT_COMPUTED, named, never estimated.

## Cycle 131 — Validation

The Round-7 harness re-scores the standing book leg-for-leg: **+₹54,102.00, 35 trades, FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact — VALID.** ABS status: FT FAIL / freq FAIL.

## WS1 — Index gap sleeve (Cycles 132–133)

Population: 54 days with |overnight gap| ≥ 0.50% (spot open vs prior close, both known at 09:15); entry 09:35, ATM100 at that bar, monthly expiry in force, EXP0 skip (2026-03-30); sleeve legs whose key is already in the standing book excluded (FOLLOW 7, FADE 4).

| Cycle | Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 132 FOLLOW | −63,495.40 (46 legs) | −9,393.40 | 81 | 17.3 | 2.00 | +1,493.25/−10,886.65 | −1,209.90 | −42,858.40 | FAIL: net, FT, flips (Apr, Sep), red month-ends (Jun–Oct), halves, placebo, ex-top-3 | FT FAIL · freq PASS |
| 133 FADE | +32,127.15 (49 legs) | +86,229.15 | 84 | 31.0 | 2.07 | +27,597.00/+58,632.15 | +50,286.75 | +52,764.15 | FAIL: FT (34.3 → 31.0), green-month flip (Mar +7,895.00 → −8,233.50) | FT FAIL · freq PASS |

Reading: Nifty gaps ≥ 0.5% revert intraday far more often than they continue — following them is one of the worst constructions this engine has scored, and fading them is a real, placebo-beaten effect (+₹32,127.15 standalone; the combined book's May improves −10,410.00 → −5,855.00 and June flips to +6,085.50). The gate still refuses FADE as an addition: its full-target rate dilutes the book's FT line and its March legs flip a green month red. Per the freeze (one construction, no variants) FADE is **rejected, not tuned**; it is recorded as a noted observation (lesson 61) — any future use must be as its own frozen system judged on fresh data, not as a descendant tuned on this window.

## WS2 — Cross-index conditioning (Cycles 134–136)

Bank confirmed admissions were built from the Bank pool (B2 keys with ≥ 2 sources, admission at the second-earliest Bank system entry, Bank sysmap from the same frozen merge inputs — **54 admissions, 0 keys excluded for missing times**; a spot-check key reproduces exactly). Bank state at a Nifty entry bar = direction of the latest Bank admission strictly before it.

| Cycle | Book | Total | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 134 (a) agreement | standing legs with agreeing prior Bank state | +7,360.00 | 2 | 100.0 | 0.05 | +3,680.00/+3,680.00 | +804.75 | 0.00 | FAIL: net, frequency (diagnostic gate, as frozen) | FT PASS · freq FAIL |
| 135 (a) disagreement | standing legs with disagreeing prior Bank state | 0.00 | 0 | 0.0 | 0.00 | 0.00/0.00 | 0.00 | 0.00 | FAIL: net, FT, frequency, placebo | FT FAIL · freq FAIL |
| 136 (b) Bank-state sleeve | — | NOT RUN | — | — | — | — | — | — | Frozen criterion not met (see below) | — |

The finding is structural, not statistical: **only 2 of the 35 standing legs (2026-03-23 PE, 2026-10-21 PE) had ANY Bank state knowable at their entry bar** — on 17 of the 19 standing-leg dates that have a Bank admission at all, the Bank confirmation completed at or after the Nifty leg's entry (the Nifty book enters ≤ 09:55 on 28 of 35 legs; Bank t2 admissions spread 09:xx–13:xx). The disagreement population is empty. The agreement subset's expectancy is ₹3,680.00/leg vs the book's ₹1,545.77/leg, but with 2 legs retained the frozen (b) criterion (expectancy greater AND ≥ 12 legs retained) fails on retention, so **Cycle 136 is NOT RUN and WS2 closes** (lesson 62). Cross-index conditioning of THIS book is empty by construction; a Bank→Nifty sleeve would have to be judged as a standalone system on its own population, which the frozen criterion deliberately did not license on 2 legs of evidence.

## WS3 — (lA) CE mirror (Cycle 137)

The (lA) v2 (L1) law mirrored exactly (confirmer Bank break-UP = first Bank bar 09:30–11:30 closing > Bank OR high; identical cutoff rule; rescan close > own OR high AND > PDH; OR width ≤ 360×scale; room above ≥ 200×scale; entry next bar). Machinery validation re-asserted in the generator (PE original 42/42). Mirror population: 35 signals → 31 legs after EXP0 skips (2026-04-28, 2026-05-26, 2026-10-27) and one standing-book key exclusion (2026-07-01 CE).

| Cycle | Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 137 (lA) CE mirror | −32,862.90 (31 legs) | +21,239.10 | 66 | 19.7 | 1.63 | +15,923.25/+5,315.85 | +12,042.25 | −12,225.90 | FAIL: net, FT, red month-ends (Aug, Sep), ex-top-3 | FT FAIL · freq PASS |

Reading: the mirror is decisively negative — (lA)'s PE rescan edge is one-sided by evidence, not by omission (lesson 63). The CE side of the (lA) family is closed with a full gated run.

## WS4 — Expiry-day sleeve (Cycle 138)

Weekly expiry days from the expiries route: 43 expiries in window, 10 monthly → **33 weekly expiry days** (incl. holiday-shifted 2026-03-02, 2026-04-13, 2026-10-19; weekly-flag cross-check on existing contracts files: no disagreements). Population: pool keys with Skill V3 among sources on a weekly expiry day, Skill's own entry within 09:15–11:00, key not in the standing book (3 excluded on that rule) → **15 legs**, weekly contract expiring the same day, strike re-struck ATM100 at the Skill entry bar.

| Cycle | Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| 138 expiry-day Skill | +3,651.75 (15 legs) | +57,753.75 | 50 | 32.0 | 1.23 | +28,343.00/+29,410.75 | +32,400.50 | +24,288.75 | FAIL: FT only (34.3 → 32.0) | FT FAIL · freq PASS |

Reading: the round's cleanest near-miss. Every other relative-gate leg passes — net +₹3,651.75, frequency up, halves up, placebo beaten by ₹25,353.25, ex-top-3 up, no flips, and August repairs (−1,701.00 → +1,911.75) while May improves (−10,410.00 → −4,173.50). It fails on the FT leg alone: the sleeve's own full-target rate is 4/15 (26.7%), diluting the book's 34.3% to 32.0%. Under the pre-registered gate it is **not banked** (lesson 64). The sleeve is recorded as a noted observation with its failing leg named; December fresh data is the only route by which it may be re-proposed, as its own frozen system.

## WS5 — Combinations (Cycles 139–140)

No workstream banked, so there are no combinations to re-gate (freeze rule). **Cycle 139 (WS5 closure):** the standing book re-gated whole-book vs the round-open baseline — +₹54,102.00, every quality leg intact (FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00 beaten, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact); the only non-passing leg is net-above-baseline, trivially, because the book IS the baseline. **Cycle 140 (candidate freeze verification):** the same full controls pass re-run as the round's closing record — identical figures, audit 35/0, NC 0, re-sum exact. ABS status for the standing book: FT FAIL (34.3%) · freq FAIL (0.86) — status only.

## Ending scorecard

| | |
|---|---|
| Standing book (December causal candidate, unchanged) | Causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20) |
| Jan–Oct 2026 total | **+₹54,102.00** |
| Monthly pace | **₹5,410.20** vs ₹15,000 floor |
| **Remaining gap** | **₹95,898.00** |
| Round delta | **₹0.00** — 0 bankings (2 near-misses refused by single gate legs, recorded with their failing legs named) |
| Trades / FT / frequency | 35 / 34.3% / 0.86 per week |
| Months | Jan +17,096.75 · Feb +12,789.25 · Mar +7,895.00 · Apr +210.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,998.75 · Aug −1,701.00 · Sep +4,652.75 · Oct +16,480.50 |
| Halves | +27,581.00 / +26,521.00 |
| Placebo (+30 min) | +22,876.00 — beaten |
| Ex-top-3 | +20,637.00 |
| Timing audit / NC / re-sum | 35/0 · 0 · exact |
| Old absolute lines (status only, referred to owner) | FT ≥ 42.0% **FAIL** (34.3%) · frequency ≥ 1.00/wk **FAIL** (0.86) |
| December candidate of record | Chandu's adopted book (+₹114,921.75 as recorded, waivers unchanged) — causal lineage unchanged by this round: +₹50,618.00 at book geometry → **+₹54,102.00** after Round-6 geometry bankings |
| Named NOT_COMPUTED | 2026-10-28 22500 PE (weekly expiry 2026-11-03) — not in any Round-7 population; never estimated |

**Round-7 totals:** 10 cycles (131–140): validation 1, WS1 2, WS2 3 (one not-run by its frozen criterion), WS3 1, WS4 1, WS5 2 (closure + freeze verification). Banked: **0**. The four new families are now measured: gap-follow is a strong loser; gap-fade and the expiry-day sleeve are real but FT-dilutive additions the relative gate refuses on single legs; cross-index conditioning is empty by timing construction; the (lA) CE mirror proves the (lA) edge one-sided. The standing book's gap (₹95,898.00) remains a signal-population problem: the causal population is 35 legs in 10 months, and none of this round's new families adds gate-clean legs to it. Records: `nifty_engine_frozen.md` (Round-7 freeze + results), `nifty_engine_log.md`, `nifty_engine_lessons.md` (61–64), `nifty_engine_state.json` (cycle 140, run7 block), per-cycle summaries `nifty_engine_run3r7_*_summary.json`, harnesses `nifty_engine_r7_harness.py`, `nifty_engine_r7_fetch.py`, `nifty_engine_r7_ws3.py`. November primary untouched throughout.
