# NIFTY engine — ROUND 9 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most); the primary's live producer already enters at confirmation, so November paper is causal by construction and was not re-scored.
Baseline at round open: **the ROUND-6/7/8 STANDING BOOK** = +₹54,102.00 — causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20), FT 34.3%, 0.86/wk, pace ₹5,410.20/month, floor gap ₹95,898.00. Freeze: `nifty_engine_frozen.md` ROUND 9 (written before any Round-9 candidate scoring; the Cycle-154 candidate freeze was appended after the Cycle-153 diagnosis and before any Cycle-154 scoring, per the Bank WS1 pattern).

**Gate calibration (pre-registered, applied uniformly):** the banking test is the **RELATIVE GATE** — net above the standing baseline, FT% not below the baseline's, frequency not below the baseline's, no baseline-green month flips red, no red month-ends, both halves ≥ 0, placebo (+30 min) beaten, ex-top-3 ≥ 0, timing audit clean, NOT_COMPUTED = 0, independent re-sum exact. The **OLD ABSOLUTE LINES** (FT ≥ 42.0%, frequency ≥ 1.00/wk — calibrated on the adopted book's inadmissible-inclusive figures, lesson 56) remain **referred to the owner**: printed as STATUS for every verdict below, never the banking test, never silently relaxed.

**Causality certification (lessons 46/52), as frozen for this round:** gap g(D) and the prior-day trend pdret_prior(D) are both fully known at D's 09:15 open (the lesson-46 own-day artefact `pdret` is used nowhere); WS1's entry at 10:05 is strictly after. WS3 diagnosis features are restricted to facts knowable at the leg's own entry bar (direction, sources, entry time, gap, pdret_prior, DTE, entry premium, spot move open→entry); premium-path quantities (MFE, exit reason) are diagnosis only, never candidate inputs. WS4 (lA) entry times come from the merge's own input files (the system's own signal bars — the source certified for the Round-6 WS2 solo books); entry is at the system's own bar, never at a later confirmation bar. Fetches this round: none required — every Round-9 population's contracts were already on disk (WS1 25 legs, WS2 fade 49 + expiry 13, WS4 17 legs all scored with NC = 0 and no fetch). **Named NOT_COMPUTED (carried):** the 2026-10-28 22500 PE leg on the weekly expiry 2026-11-03 — in no Round-9 population; stays NOT_COMPUTED, named, never estimated.

## Cycle 150 — Validation

The Round-9 harness re-scores the standing book leg-for-leg: **+₹54,102.00, 35 trades, FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact — VALID.** ABS status: FT FAIL / freq FAIL.

## WS1 — The fade's last cell (Cycle 151): with-trend × entry 10:05

The one combination Round 8 deliberately left unfrozen (lesson 66): the Round-7 FADE population at threshold 0.50%, admission restricted to with-trend days (sign of gap == sign of pdret_prior, the exact Round-8 WS1(b) definition), entry delayed to 10:05 (the Cycle-145 form). Sleeve: 25 legs (29 exclusions: 24 trend-filter, 2 standing keys — 03-02 CE, 06-08 CE — 1 EXP0, and the balance trend-filtered March/April days).

| Sleeve standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | March (combined) | April (combined) | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| +15,937.00 (25 legs) | +70,039.00 | 60 | **35.0** | 1.48 | +30,515.50/+39,523.50 | +39,979.75 | +36,574.00 | **+12,443.50** | **−3,050.00** | **FAIL: April flip only** | FT FAIL · freq PASS |

Reading: the combination is worth more than either parent form's sleeve (with-trend at 09:35 was +₹7,064.50; this is +₹15,937.00) and it cures BOTH of the family's recorded wounds — March stays green (+12,443.50 combined; sleeve March +4,548.50, vs −16,271.50 for the unrestricted 10:05 form) and FT passes as an addition (35.0% ≥ 34.3%, the restriction no longer dilutes at the late entry). It fails on exactly one leg: **April flips** — the book's thinnest green month (+₹210.00) goes to −3,050.00 (sleeve April −3,260.00; sleeve February is also −7,101.50 against a thick baseline month). Every other gate leg passes: net +₹15,937.00 over baseline, frequency 1.48/wk, halves strongly positive, placebo beaten by ₹30,060.25, ex-top-3 +36,574.00, no red month-ends, audit clean, NC 0. Per the freeze, the fade family now **CLOSES**: six gated forms (follow, fade 09:35, thresholds 0.75/1.00, with-trend 09:35, fade 10:05, with-trend × 10:05), each refused on a single named leg. The Cycle-145 form remains the family's flagged item; this combined form is recorded as a noted observation with its failing leg named (lesson 69).

## WS2 — Flagged-pair gate (Cycle 152) — DECISION SUPPORT, force-no-bank

Book = round-open standing book + Cycle-145 fade legs (49) + Cycle-138 expiry-sleeve legs, all at standing geometry, gated in full against the round-open baseline. **This cycle never banks and never updates the standing book.** The expiry sleeve enters with 13 legs here, not 15: two of its keys (of the five excluded) collide with fade keys and UNIQUE-ONCE assigns them to the fade — the pair is worth ₹210.00 less than the sum of the two flagged adoption values, which is precisely what this gate exists to price.

| Pair total | Adoption value | n | FT% | /wk | Halves | Placebo | Ex-top-3 | March | May | Relative gate (DS only) | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **+91,168.50** | **+37,066.50** | 97 | 34.0 | 2.39 | +45,393.50/+45,775.00 | +52,867.25 | +57,703.50 | −11,846.50 | +4,574.00 | FAIL: FT, March flip | FT FAIL · freq PASS |

Gate sheet (every leg): net_above_baseline ✓ (+37,066.50) · **ft_not_degraded ✗ (34.0% < 34.3%)** · frequency_not_degraded ✓ (2.39/wk) · **no_green_month_flips_red ✗ — flips: 2026-03 only** (March +7,895.00 → −11,846.50; the fade's March wound, −16,271.50 sleeve March, is only partly offset by the expiry sleeve's March) · no_red_month_ends ✓ · halves_both≥0 ✓ · placebo_beaten ✓ (by ₹38,301.25) · ex_top3≥0 ✓ (+57,703.50) · timing_audit_clean ✓ (97/0) · not_computed_zero ✓ · resum_exact ✓. Component standalones inside the pair: fade +₹33,624.75 (reproduces Cycle 145 to the paisa), expiry +₹3,441.75 over its 13 non-colliding legs. If the owner adopted both flagged items as they stand, the book would be **+₹91,168.50 Jan–Oct = ₹9,116.85/month (gap ₹58,831.50)**, carrying a red March and a 0.3-point FT dilution as the priced costs. The decision is the owner's; the engine has not adopted anything.

## WS3 — Causal-May diagnosis (Cycle 153) + conditional candidate (Cycle 154)

**May path-by-path** (the causal book's May is 3 legs, all confirmed PE, all full stops — a different population from the adopted book's May scanned in Round 4):

| Leg | Entry facts | Premium path | Spot context |
|---|---|---|---|
| 2026-05-11 PE | (lA)+Skill, 09:40, K 23900, exp 05-26, DTE 15, prem ₹353.00 | MFE **+16.90** @ 10:20 → stop 11:40 @ 303.00, **−₹3,470.00** | gap −0.867%, pdret_prior −0.643%, spot 23,970.10 → 23,881.35 (with the trade) |
| 2026-05-13 PE | (lA)+Skill+V5, 09:35, K 23300, exp 05-26, DTE 13, prem ₹304.25 | MFE **+37.85** @ 09:35 (the entry bar itself) → stop 10:20 @ 254.25, **−₹3,470.00** | gap −0.291%, pdret_prior −1.636%, spot 23,362.45 → 23,337.30 (with) |
| 2026-05-18 PE | (lA)+Skill+V5, 09:40, K 23400, exp 05-26, DTE 8, prem ₹294.65 | MFE **+16.50** @ 09:55 → stop 10:55 @ 244.65, **−₹3,470.00** | gap −0.749%, pdret_prior −0.229%, spot 23,482.20 → 23,358.50 (with) |

Anatomy: three down-gap, prior-day-down PE entries whose premiums never reached even the +50 BE arm (best MFE +37.85, on the entry bar) and all stopped within two hours. June adds one more full stop (06-19 PE solo (lA), 13:00) and two BE stops (−₹220 ×2): the wound (negative legs in May+Jun) is 6 legs, −₹14,320.00 in total.

**Separator scan** (Bank WS1 frozen test; wound = 6 legs; book = 35; FT legs = 12). Exactly one feature separates — **F8 |g(D)| ≥ 0.50%**: wound share 4/6 (66.7%) vs book share 11/35 (31.4%), ratio **2.12** ≥ 2× ✓; holds 4 of 6 wound legs ≥ half ✓; FT-leg share 4/12 (33.3%) < 60% ✓. All other features fail: F1 PE (ratio 1.17, FT share 83%), F5 entry ≤ 09:40 (1.33), F11 premium ≥ ₹300 (1.59, holds exactly half), F7 gap < 0 (1.22), F3 confirmed (1.04), F6 pdret_prior < 0 (0.97), F4 solo (lA) (0.83), F2 CE (0.58), F9 DTE ≤ 7 (0.53), F10 DTE ≥ 21 (0.73), F12 spot-against (0/6 — no book leg enters against its morning spot move). The candidate was frozen in writing (appended to `nifty_engine_frozen.md`) before scoring: **exclude the 11 standing legs with |g(D)| ≥ 0.50%**.

**Cycle 154 — the F8 exclusion, gated:** the excluded population is named in full in the cycle record (01-30 CE, 02-13 PE, 03-02 CE, 03-13 PE, 03-23 PE, 05-11 PE, 05-18 PE, 06-08 CE, 06-19 PE, 09-24 PE, 10-21 PE). Its scored nets sum to **+₹11,776.00** — the signature population is a net EARNER for the book: it holds four wound legs (−₹10,630.00) but also the book's largest leg (03-13 PE, +₹11,155.00) and three +₹3,680.00 runner legs. Candidate: **+₹42,326.00** (24 legs, FT 33.3%, 0.59/wk, halves +19,475.00/+22,851.00, placebo +32,442.75 beaten, ex-top-3 +11,851.00) — **REJECTED on four legs: net (below baseline), FT, frequency, and a March flip** (+7,895.00 → −3,470.00, from dropping March's two big winners). The exclusion does repair the wound months (May −10,410.00 → −3,470.00; Jun −3,910.00 → −220.00) — it buys them with March and ₹11,776.00 of net. Per the freeze there is no second candidate and no exit variant: **the causal-May question is CLOSED** — May is three confirmed down-gap PE stops whose shared feature (|gap| ≥ 0.50%) names a population the book profits from overall (lesson 70).

## WS4 — Causal union (Cycle 155)

Population (never measured before): EXP0 pool keys with (lA) v2 among sources AND ≥ 2 sources AND key not in the standing book — the multi-source (lA) keys the CH3-R confirmation window missed — entered at (lA)'s OWN sysmap bar, strike re-struck ATM100 there. 17 legs (17 further keys excluded as already in the standing book; no (lA)-time-missing keys). **All 17 are PE.**

| Union standalone | Combined book | n | FT% | /wk | Halves | Placebo | Ex-top-3 | August (combined) | Relative gate | Old lines (status) |
|---|---|---|---|---|---|---|---|---|---|---|
| **−7,653.00** (17 legs) | +46,449.00 | 52 | 28.8 | 1.28 | +27,869.50/+18,579.50 | +2,414.75 | +12,984.00 | −7,812.50 | FAIL: net, FT, April flip | FT FAIL · freq PASS |

Reading: the missed-confirmation population is the pool's adverse-selection tail, not discarded value — 8 of its 17 legs are full stops (−₹3,470.00), its August slice is −₹6,111.50 (combined August −1,701.00 → −7,812.50), and it flips April (−₹6,940.00 sleeve April). This is the WS0 finding read from the other side: the value in the (lA) family sits in the keys the causal rule admits early, and the keys that only confirm late lose when traded at (lA)'s own bar. **REJECTED; the causal-union family is closed** (lesson 71).

## WS5 — Combinations, closure, restatement (Cycles 156–158)

No workstream banked, so there are no combinations to re-gate (freeze rule). **Cycle 156 (closure):** the standing book re-gated vs the round-open baseline — every quality leg intact (FT 34.3%, 0.86/wk, halves +27,581.00/+26,521.00, placebo +22,876.00 beaten, ex-top-3 +20,637.00, audit 35/0, NC 0, re-sum exact); only net-above-baseline non-passing, trivially, because the book IS the baseline. **Cycle 157 (candidate freeze verification):** identical figures — OK. **Cycle 158 (flagged restatement on the ending book):** the ending book is the round-open book, so the restatements reproduce the recorded values exactly — fade-10:05 combined +₹87,726.75 (fails the March flip only), expiry combined +₹57,753.75 (fails FT only), pair +₹91,168.50 (fails FT + March flip; adoption value +₹37,066.50).

## Flagged list — restated on the ending book (unchanged)

| Flagged item | Form | Adoption value | Combined if adopted | Gate status |
|---|---|---|---|---|
| Expiry-day Skill sleeve (R7 C138) | Standing geometry | **+₹3,651.75** | +₹57,753.75 | FLAGGED — fails the FT leg only (34.3 → 32.0); owner decision pending; NOT adopted |
| Gap-fade entry-10:05 (R8 C145) | R7 fade construction, entry 10:05 | **+₹33,624.75** | +₹87,726.75 | NOTED OBSERVATION — fails the March flip leg only; NOT adopted |
| **Both flagged items together (R9 C152/C158)** | Standing geometry, UNIQUE-ONCE | **+₹37,066.50** | **+₹91,168.50** | DECISION SUPPORT — fails FT (34.0%) + March flip; priced for the owner's combined decision; NOT adopted |
| Gap-fade with-trend × 10:05 (R9 C151) | Restriction × delay combined | +₹15,937.00 | +₹70,039.00 | NOTED OBSERVATION — fails the April flip leg only; fade family CLOSED; NOT adopted |

## Ending scorecard

| | |
|---|---|
| Standing book (December causal candidate, unchanged) | Causal 35 legs × (stop −50, BE arm +50, tgt1 +90 → lock +60, TGT2 +175, square-off 15:20) |
| Jan–Oct 2026 total | **+₹54,102.00** |
| Monthly pace | **₹5,410.20** vs ₹15,000 floor |
| **Remaining gap** | **₹95,898.00** |
| Round delta | **₹0.00** — 0 bankings |
| Trades / FT / frequency | 35 / 34.3% / 0.86 per week |
| Months | Jan +17,096.75 · Feb +12,789.25 · Mar +7,895.00 · Apr +210.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,998.75 · Aug −1,701.00 · Sep +4,652.75 · Oct +16,480.50 |
| Halves | +27,581.00 / +26,521.00 |
| Placebo (+30 min) | +22,876.00 — beaten |
| Ex-top-3 | +20,637.00 |
| Timing audit / NC / re-sum | 35/0 · 0 · exact |
| Old absolute lines (status only, referred to owner) | FT ≥ 42.0% **FAIL** (34.3%) · frequency ≥ 1.00/wk **FAIL** (0.86) |
| December candidate of record | Chandu's adopted book (+₹114,921.75 as recorded, waivers unchanged) — causal lineage unchanged by this round: **+₹54,102.00** after Round-6 geometry bankings |
| Named NOT_COMPUTED | 2026-10-28 22500 PE (weekly expiry 2026-11-03) — not in any Round-9 population; never estimated |

**Round-9 totals:** 9 cycles (150–158): validation 1, WS1 1, WS2 1 (decision support), WS3 2 (diagnosis + conditional candidate), WS4 1, WS5 3 (closure, freeze verification, flagged restatement). Banked: **0**. The fade family is closed after six gated forms — its last cell cures March and FT and is refused on an April flip alone. The flagged pair is priced for the owner at +₹37,066.50 (combined +₹91,168.50). The causal-May wound has a true separator (|gap| ≥ 0.50%) whose population the book profits from, so May closes unrepaired. The causal union is negative — the confirmation window's discards are an adverse-selection tail. Records: `nifty_engine_frozen.md` (Round-9 freeze + Cycle-154 candidate freeze + results), `nifty_engine_log.md`, `nifty_engine_lessons.md` (69–72), `nifty_engine_state.json` (cycle 158, run9 block, flagged list restated), diagnosis evidence `nifty_engine_r9_ws3_diag.json`, per-cycle summaries `nifty_engine_run3r9_*_summary.json`, harnesses `nifty_engine_r9_harness.py`, `nifty_engine_r9_stage1.py`, `nifty_engine_r9_stage2.py`, `nifty_engine_r9_ws3_diag.py`. November primary untouched throughout.
