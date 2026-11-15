# NIFTY ENGINE — ROUND 11 (2026-11-02) — December preparation, narrow scope

**Segment:** Nifty only. Premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE. Paper only, real money ₹0.
**Floor:** ₹1,50,000 Jan–Oct 2026 (₹15,000/month). **Standing book (unchanged): +₹54,102.00 = ₹5,410.20/month; gap ₹95,898.00.**
**Result: nothing banked, nothing adopted. Two deliverables: (1) DEC-S1 frozen as a labelled December SHADOW candidate and its specification VERIFIED by regeneration; (2) the gate re-basing decision note (both columns, no recommendation).**
**Cycles run: 2 (168–169)** — Cycle 168 verification · Cycle 169 decision note (analysis of recorded verdicts, no scoring). No new in-sample signal cycles were run: Round 10's gated conclusion (the in-sample signal space is exhausted) stands and this round's brief forbids them.

Freeze: `nifty_engine_frozen.md`, ROUND 11 section (written before any Round-11 scoring), containing the complete DEC-S1 specification (S0–S9) with per-condition causality certifications (lessons 46/52) and the pre-registered verification protocol (S10). The standing December candidate's freeze (Round-10 WS4, rules 1–9) is not altered by this round.

---

## 1. DEC-S1 — the flagged pair, frozen as a December SHADOW candidate

**Status.** DEC-S1 is a labelled December **shadow** candidate. It is NOT adopted, it does NOT replace the standing December candidate, and it changes no standing book. December 2026 judges the standing candidate and DEC-S1 **in parallel**, each under its own pre-registered pass/kill, each labelled; neither verdict alters the other.

**Specification summary** (full tradeable text: frozen file, S0–S9):

- **Assembly (S1):** A → B → C under UNIQUE-ONCE per (date, direction); a key owned by an earlier component excludes the later component's leg on that key (exclusions named in the run record).
- **Component A — standing causal book (S2):** the of-record candidate's rules 1–7 (U1 systems speaking only at their own bars; ≥2-system keys admitted iff the 2nd-earliest entry ≤ 09:55, entered AT that bar; solo (lA) v2 at its own bar; solo non-(lA) not admitted; EXP0; ATM100 at the entry bar's spot open; monthly expiry in force).
- **Component B — gap-fade, 10:05 entry (S3; the Round-8 Cycle-145 form):** days D with prior trading day P in `spot_daily`; g(D) = open(D)/close(P) − 1; admitted iff |g(D)| ≥ 0.50%; direction opposite the gap; entry at the 10:05 bar; strike ATM100 at the 10:05 spot bar open; monthly expiry in force; EXP0 skip (D == expiry excluded); keys already in A excluded.
- **Component C — expiry-day sleeve (S4; the Round-7 Cycle-138 form):** weekly expiry days = expiries-route dates NOT in the monthly list; U1 pool keys on those days with Skill V3 among their sources; entry at Skill V3's own sysmap entry time, admitted only within 09:15–11:00 (missing Skill time → excluded and named); strike re-struck ATM100 at that bar; contract = the weekly expiry expiring that day; keys already in A ∪ B excluded.
- **Geometry (S5, all legs):** standing geometry — stop −50 (stop before target, entry bar included); BE arm +50 → stop to entry; tgt1 +90 → runner lock +60, TGT2 +175; square-off 15:20 close; entry price = the entry bar's open in the contract's own candles.
- **Causality (S6):** every admission condition and feature is certified knowable at its decision bar in writing in the freeze — the gap uses prints that exist at 09:15 for a 10:05 entry; Component C enters at Skill's own bar and never before it; strikes are struck at the entry bar's spot open; the leg day's own close-to-close return (the lesson-46 artefact) is used nowhere.
- **December expiry handling (S7):** A and B — 2026-12-01…12-29 trade monthly expiry 2026-12-29 (12-29 itself EXP0-excluded); 2026-12-30/31 trade the 2027-01-26 monthly. C — December weekly expiry days are 2026-12-01, 2026-12-08, 2026-12-15, 2026-12-22 (2026-12-29 is the monthly date, excluded by the minus-monthly construction); the expiries route governs if it lists any additional December weekly date.
- **NC policy (S8):** identical to the standing candidate's — a leg whose candles cannot be obtained is NOT_COMPUTED, named, never estimated, excluded from the total and disclosed beside it; NC > 0 makes the December verdict PROVISIONAL, never a pass. The carried 2026-10-28 22500 PE leg (weekly expiry 2026-11-03) is in no DEC-S1 population and remains NOT_COMPUTED.
- **DEC-S1 December pass/kill (S9 — judged on December 2026 data alone, window 2026-12-01…12-31):** **PASS** iff December net > ₹0 AND timing audit clean (0 violations) AND NC = 0. **KILL** iff December net ≤ −₹3,470.00 (one full-stop equivalent) OR any timing violation. **INCONCLUSIVE** (no verdict claimed) iff net ∈ (−₹3,470.00, ₹0] with a clean audit, or net > ₹0 with NC > 0 (provisional). Printed beside, never as the test: floor pace would need December ≥ +₹15,000; DEC-S1's Jan–Oct pace is ₹9,116.85/month.

## 2. Cycle 168 — regeneration verification: **VERIFIED**

Rebuilt from the S1–S5 specification alone (certified builders; script `nifty_engine_r11_verify.py`), scored under standing geometry with the **full controls gate in the same run**:

| Field | DEC-S1 rebuild | Frozen record (C152/C167) | Check |
|---|---|---|---|
| Legs | 97 (A 35 · B 49 · C 13) | 97 | MATCH |
| Total | **+₹91,168.50** | +₹91,168.50 | MATCH — to the paisa |
| FT | 34.0% | 34.0% | MATCH |
| Frequency | 2.39/wk | 2.39/wk | MATCH |
| Halves | +₹45,393.50 / +₹45,775.00 | same | MATCH |
| Placebo (+30 min) | +₹52,867.25 (beaten) | same | MATCH |
| Ex-top-3 | +₹57,703.50 | same | MATCH |
| Month table | Jan +19,211.25 · Feb +5,038.75 · Mar −11,846.50 · Apr +28,416.00 · May +4,574.00 · Jun −1,331.00 · Jul +5,839.00 · Aug +841.25 · Sep +20,265.25 · Oct +20,160.50 | identical | MATCH ×10 |
| Timing/admission audit | 97 checked / 0 violations | 97/0 | MATCH |
| NOT_COMPUTED | 0 | 0 | MATCH |
| Independent re-sum | exact | exact | MATCH |

Component identities: A reproduces +₹54,102.00 (audit 35/0); B standalone +₹33,624.75 (exclusions named: 4 standing-key collisions, 1 EXP0); C in-pair standalone +₹3,441.75 over 13 legs (5 key-collision exclusions vs A ∪ B named; 15-leg standalone population, 2 keys collide with B). Pair identity holds exactly: 54,102.00 + 33,624.75 + 3,441.75 = **91,168.50** — the adoption value +₹37,066.50, i.e. ₹210.00 less than the sum of the two flags, from the two UNIQUE-ONCE collisions (lesson 72). **26/26 pre-registered field checks MATCH. No mismatch was found; nothing was patched.** Summary: `nifty_engine_run3r11_r11_c168_decs1_regen_verify_summary.json`; leg list: `nifty_engine_r11_decs1_legs.json`.

DEC-S1 is therefore a specification, not a leg list — December can be traded and judged from the frozen rules alone, exactly as the standing candidate can (Cycle 166 precedent).

## 3. Cycle 169 — gate re-basing decision note (decision support only)

**The question referred to the owner.** The old absolute lines — **FT ≥ 42.0%** and **frequency ≥ 1.00/wk** — were calibrated (Rounds 3–5) on the adopted book (+₹114,921.75), which Round 5's WS0 audit later proved admission-inadmissible: its causal reading is +₹50,618.00 at FT 34.3%, 0.86/wk. Since Round 6 the banking test has been the **relative gate** (net above baseline; FT and frequency not below the baseline's; no green-month flips; no red month-ends; halves ≥ 0; placebo beaten; ex-top-3 ≥ 0; audit clean; NC = 0; re-sum exact), with the absolute lines printed as STATUS only. "Re-basing" means setting the absolute lines at the causal book's own measured levels — **FT ≥ 34.3%, frequency ≥ 0.86/wk** — which makes them numerically identical to the relative gate's FT/frequency legs. This note states, from already-controlled verdicts only, what each choice would have done to the candidates already tested. No new scoring was run for this note; no recommendation is made — the last row of each column is the arithmetic consequence, and the decision is the owner's.

**The evidence base (causal era, Rounds 6–10; all figures controlled, per 1 lot):**

| Candidate (as addition to / change of the causal book) | Controlled result | FT | Freq/wk | Failing gate legs (relative gate) |
|---|---|---|---|---|
| Standing causal book itself | +₹54,102.00 | 34.3% | 0.86 | — (baseline) |
| R6 lock +60 (geometry change) | +₹500.50 → book +₹51,118.50 | 34.3% | 0.86 | none — **BANKED** |
| R6 square-off 15:20 (geometry change) | +₹2,983.50 → book +₹54,102.00 | 34.3% | 0.86 | none — **BANKED** |
| Expiry sleeve (C138) | combined +₹57,753.75 (+₹3,651.75) | 32.0% | 1.23 | FT only |
| Fade thr 0.75% (C142) | combined +₹64,984.00 | 29.0% | 1.53 | FT only |
| Fade thr 1.00% (C143) | combined +₹57,560.00 | 33.3% | 1.18 | FT only |
| Fade with-trend (C144) | combined +₹61,166.50 | 30.0% | 1.48 | FT only |
| Fade-10:05 (C145) | combined +₹87,726.75 (+₹33,624.75) | 35.7% | 2.07 | March flip only |
| Fade-combo, with-trend × 10:05 (C151) | combined +₹70,039.00 (+₹15,937.00) | 35.0% | 1.48 | April flip only |
| Flagged pair = DEC-S1 book (C152) | +₹91,168.50 (+₹37,066.50) | 34.0% | 2.39 | FT (34.0 < 34.3) + March flip |
| R10 agreement conditioning (C160) | +₹46,882.00 | 33.3% | 0.74 | net, FT, frequency, April flip |
| R10 OR-width subsets (C162/C163) | +₹21,298.25 / +₹42,467.75 | 35.7% / 38.5% | 0.34 / 0.64 | net, frequency (+ex-top-3 / March flip) |
| R10 post-expiry addition (C164) | +₹35,523.75 | 30.0% | 1.23 | net, FT, April flip, audit, NC |

(Pre-audit caveat: CH3-R × lock50/TGT2-175, FT 45.5%, 1.08/wk, passes both absolute lines — but it sits on the book WS0 proved inadmissible and was adopted by the owner over other clauses; it is not evidence about the causal book under either column. Cycle-40 was banked under the old lines and voided for look-ahead feature timing, not for any gate line.)

### Column A — KEEP the absolute lines (FT ≥ 42.0%, frequency ≥ 1.00/wk as hard banking requirements, alongside the other gate legs)

- The standing book itself fails both lines (34.3% < 42.0%; 0.86 < 1.00). Any candidate that does not lift FT by ≥ 7.7 points AND frequency by ≥ 0.14/wk while passing every other leg cannot bank.
- The two Round-6 bankings would **not** have banked: lock +60 and square-off 15:20 (FT 34.3%, 0.86/wk throughout) fail both lines. Causal-era banked total under this column: **₹0** (the book would stand at the WS0 causal +₹50,618.00, its geometry improvements un-bankable).
- Every flagged item still fails, on FT: expiry sleeve 32.0%, pair 34.0%, fade-combo 35.0%, fade-10:05 35.7% — the best FT any tested addition reaches. All sleeve additions pass the frequency line (1.18–2.39/wk); frequency binds only the subset candidates (C160/C162/C163), which also fail the net leg.
- **Bottom line of Column A: nothing already tested banks; the gate is closed by construction on the causal book, and the December candidates remain exactly as frozen regardless.**

### Column B — RE-BASE the lines to the causal book (FT ≥ 34.3%, frequency ≥ 0.86/wk)

- The lines become identical to the relative gate's FT/frequency legs, so the banking record is exactly the record the engine has already produced: the two Round-6 geometry bankings stand — **+₹3,484.00 combined banked** (book ₹50,618.00 → ₹54,102.00) — and nothing else in Rounds 6–10 banks.
- **No flagged item is unlocked.** Each fails a leg that re-basing does not touch, or fails FT against the baseline itself: expiry sleeve FT 32.0% < 34.3% (its ONLY failing leg — it fails under both columns); pair FT 34.0% < 34.3% AND the March flip (+₹7,895.00 → −₹11,846.50); fade-10:05 passes both re-based lines and fails the March flip only; fade-combo passes both and fails the April flip only; the FT-only fade forms (C142 29.0%, C143 33.3%, C144 30.0%) fail even the re-based FT line. Month-flip legs are separate gate legs — re-basing the FT/frequency lines does not amend them.
- Sensitivity, stated so the owner can read off any intermediate choice: an FT line at ≤ 32.0% (with frequency anywhere ≤ 1.23/wk) is the first setting at which any additional tested candidate's FT leg passes — the expiry sleeve — and it would then bank on its remaining legs, all of which pass. No FT setting above 35.7% admits any sleeve; no frequency setting at or below 1.00/wk changes any sleeve verdict.
- **Bottom line of Column B: +₹3,484.00 of already-banked geometry improvements are the only difference from Column A; the flagged items' outcomes are identical under both columns, because none of them is refused on a line alone.**

The two decisions are independent: DEC-S1 now lets December's fresh data judge the pair without any adoption; the re-basing decision governs only what the engine may bank in future rounds. Both remain the owner's.

## Ending position

| Measure | Value |
|---|---|
| Standing book (December causal candidate) | **+₹54,102.00** Jan–Oct 2026 — unchanged |
| Monthly pace / floor / gap | ₹5,410.20 / ₹15,000 / **₹95,898.00** — unchanged |
| DEC-S1 (December shadow, NOT adopted) | **+₹91,168.50** Jan–Oct = ₹9,116.85/month; specification VERIFIED (Cycle 168) |
| December forward tests frozen | Standing candidate (rules 1–9, pass/kill of record) + DEC-S1 (S9 pass/kill), in parallel, labelled |
| Banked this round | None (freeze + verification only, as briefed) |
| Real money | ₹0 — paper only. November primary NF-PAPER-C3G7 untouched. |
