# NIFTY ENGINE — ROUND 10 (2026-11-02)

**Segment:** Nifty only. Premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE. Paper only, real money ₹0.
**Floor:** ₹1,50,000 Jan–Oct 2026 (₹15,000/month). **Starting book:** standing causal book **+₹54,102.00** (gap ₹95,898.00).
**Result: nothing banked. Ending book UNCHANGED: +₹54,102.00 = ₹5,410.20/month. Remaining gap ₹95,898.00.**
**Cycles run: 9 (159–167)** — validation 1 · WS1 2 (1 gated + 1 closure record) · WS2 2 · WS3 1 · WS4 1 (verification) · WS5 2.

Gate for every verdict below: the **relative gate** is the banking test (net above baseline, FT and frequency not degraded, no baseline-green month flips red, no red month-ends, halves ≥ 0, placebo beaten, ex-top-3 ≥ 0, timing audit clean, NC = 0, re-sum exact). The **old absolute lines** (FT ≥ 42.0%, frequency ≥ 1.00/wk) are printed as **status only** — they are the owner's referred re-basing decision, not the banking test. Every candidate below also fails those absolute lines unless noted, except where the addition raises frequency above 1.00/wk (noted).

Freeze: `nifty_engine_frozen.md`, ROUND 10 section, written before any Round-10 candidate scoring, with per-feature timing certifications (a)–(f), the frozen WS1 mirror rule, the WS3 addition rule, and the WS4 December specification including its pre-registered pass/kill. One piece of freeze prose was wrong and is corrected in the results section (see WS3).

Data preparation (pre-freeze, recorded): the Bank spot monthly files lacked 2026-01-30, 2026-02-26, 2026-02-27; 75 real 5-minute candles per day were fetched (browser User-Agent) into `nifty_engine_r10_bank_spot_patch.csv`, making the WS1 feature computable for all 35 legs.

---

## Cycle 159 — Validation
Standing book reproduces exactly: **+₹54,102.00**, 35 legs, FT 34.3%, 0.86/wk, halves +₹27,581.00/+₹26,521.00, placebo +₹22,876.00, ex-top-3 +₹20,637.00, audit 35/0, NC 0, re-sum exact. Round-open baseline set. Absolute lines (status): FT 34.3% FAIL · frequency 0.86 FAIL.

## WS1 — Bank-spot early state (Cycles 160–161): family closed
Certified feature: Bank Nifty spot's move from its own open, using bars strictly before each leg's entry bar; threshold ±0.20% (frozen).

Bucket diagnostic on the standing legs (scored nets): **AGREE 30 legs +₹46,882.00 · NEUTRAL 5 legs +₹7,220.00 · DISAGREE 0 legs**. The two indices never move ≥ 0.20% in opposite directions by these entry bars.

- **Cycle 160 — agreement conditioning** (admit only the 30 AGREE legs): **+₹46,882.00**, FT 33.3%, 0.74/wk, halves +₹20,141.00/+₹26,741.00, placebo +₹13,829.50 beaten, ex-top-3 +₹13,417.00, audit 30/0, NC 0, re-sum exact. **REJECTED under the relative gate** on net-above-baseline, FT-not-degraded, frequency-not-degraded, and no-green-month-flips (April +₹210.00 → −₹3,470.00 — the dropped neutral set holds April's +₹3,680.00 anchor leg). Absolute lines (status): FT FAIL · frequency FAIL.
- **Cycle 161 — mirror:** closure record under the freeze's frozen mirror rule (run only if net(disagree) > 0 AND > net(agree)). Net(disagree) = ₹0 on an empty population — the rule does not fire and there is nothing to score. **NOT RUN.** Cross-index conditioning is now closed in both forms: Bank option confirmations (Round 7, complete too late) and Bank spot state (this round — agreement describes the book rather than filtering it, and disagreement never occurs). Lesson 73.

## WS2 — OR-width admission (Cycles 162–163): closed
Certified feature: tercile of the 09:15–09:30 opening-range width vs its trailing 20-trading-day distribution (OR completes 09:30; every leg enters ≥ 09:35).

Tercile nets on the standing legs: **lower 9 legs +₹11,634.25 · middle 14 legs +₹21,298.25 · upper 12 legs +₹21,169.50** — every tercile earns.

- **Cycle 162 — middle-tercile only:** **+₹21,298.25**, FT 35.7%, 0.34/wk, halves +₹3,951.50/+₹17,346.75, placebo +₹17,437.25 beaten, **ex-top-3 −₹749.50**, audit 14/0, NC 0. **REJECTED** on net, frequency, ex-top-3. Absolute lines (status): FT FAIL · frequency FAIL.
- **Cycle 163 — middle+upper:** **+₹42,467.75**, FT 38.5%, 0.64/wk, halves +₹12,256.75/+₹30,211.00, placebo +₹28,177.50 beaten, ex-top-3 +₹11,992.75, audit 26/0, NC 0. **REJECTED** on net, frequency, and the March flip (+₹7,895.00 → −₹3,260.00). Absolute lines (status): FT FAIL · frequency FAIL.

Lesson 74: day-state admission is now closed across six axes on the causal book (gap %, first-30-min range, prior-day expansion, premium bands, Bank spot state, OR width) — every state earns, so every admission filter only subtracts.

## WS3 — Post-expiry-day population (Cycle 164): adverse tail, closed
48 post-expiry sessions in Jan–Oct 2026 (all Wednesdays). Pool keys on those sessions not in the standing book: **16** (≥ the frozen 8-leg minimum; 0 named exclusions at build). Entered at causal bars per the freeze (confirmed keys at the 2nd-earliest system bar with no 09:55 window; solo keys at their own system's bar; strike re-struck ATM100 when the entry time moved). Disclosed prior: Round 9 WS4's late-confirming (lA) tail was adverse — the overlap is real and the verdict below was not imported from it.

- Sleeve standalone: **−₹18,578.25** over 15 scored legs, plus 1 NOT_COMPUTED.
- **Cycle 164 — standing + sleeve:** **+₹35,523.75**, 50 scored legs, FT 30.0%, 1.23/wk, halves +₹12,003.00/+₹23,520.75, placebo +₹586.25 beaten, ex-top-3 +₹2,058.75, re-sum exact. **REJECTED** on net-above-baseline, FT-not-degraded, the April flip (+₹210.00 → −₹3,260.00), timing audit, and NC = 0. Absolute lines (status): FT FAIL · frequency PASS.
- The single NC leg and the single audit entry are the same leg, and it is the book's carried leg: **2026-10-28 22500 PE, monthly expiry 2026-11-03** (registry holds 0 contracts; one re-fetch attempted in-round, discovery EMPTY). Its trade date is the first session after the October monthly expiry (2026-10-27), so it belongs to this population. **Correction:** the Round-10 freeze's prose said this leg is "in NO Round-10 population" — that was wrong for WS3 and is corrected in writing in `nifty_engine_frozen.md`. The leg was named, never estimated, never scored, and it blocked banking under the frozen NC clause exactly as designed. Lesson 75.

What the causal rule leaves behind — late-confirming, unconfirmed, or post-expiry — loses in this pool. The post-expiry family is closed.

## WS5 — Combinations (Cycle 165): closure by statement
Round 10 banked nothing through Cycle 164, and the freeze's combination rule covers bankings only. **No combination exists to re-gate. Closed by statement.**

## WS4 — December freeze preparation (Cycle 166): VERIFIED
The December candidate is frozen in `nifty_engine_frozen.md` as a complete specification (rules 1–9): U1 systems at their own bars; ≥2-system admission with the 2nd-earliest entry ≤ 09:55 entered at that bar; solo (lA) admitted; EXP0; ATM100 at the entry bar; monthly expiry in force (December 2026: dates 12-01…12-29 trade expiry 2026-12-29, with 12-29 itself EXP0-excluded; 12-30/31 trade the 2027-01-26 monthly; weekly contracts not traded); geometry stop −50 / BE arm +50 / tgt1 +90 → lock +60 / TGT2 +175 / square-off 15:20; ₹220/trade, 1 lot of 65, UNIQUE-ONCE; NOT_COMPUTED named, never estimated, NC > 0 → verdict PROVISIONAL; and a **pre-registered December pass/kill** — PASS iff December net > ₹0 with a clean timing audit and NC = 0; KILL iff net ≤ −₹3,470.00 or any timing violation; otherwise INCONCLUSIVE. (Context, never the test: floor pace needs December ≥ +₹15,000; the candidate's Jan–Oct pace is ₹5,410.20/month.)

**Regeneration verification (Cycle 166): VERIFIED.** A fresh rebuild from rules 1–4 over the certified sysmap reproduces the standing book **leg-for-leg** (date, direction, entry time, strike, expiry) and reproduces **+₹54,102.00 to the paisa** (35 legs, audit 35/0, NC 0, re-sum exact); the standing book re-scored identically. The candidate is a specification, not a leg list — December can be traded from the rules alone.

## WS5 — Closure re-gate + flagged restatement (Cycle 167)
Closure re-gate of the ending book vs the round-open baseline: identity — all quality legs intact; only net-above-baseline non-passing, trivially (the book against itself).

**Flagged list, restated on the ending book** (decision support, force-no-bank — the standing book was never touched; all values reproduce Round 9 exactly because the book is unchanged):

| Flagged item | Adoption value | Combined total | Fails (relative gate) | Absolute lines (status) |
|---|---|---|---|---|
| Expiry-day sleeve | +₹3,651.75 | +₹57,753.75 | FT only (32.0% vs 34.3%) | FT FAIL · freq PASS |
| Gap-fade 10:05 | +₹33,624.75 | +₹87,726.75 | March flip only (+7,895.00 → −8,376.50) | FT FAIL · freq PASS |
| Flagged pair (joint) | +₹37,066.50 | +₹91,168.50 | FT (34.0%) + March flip (→ −₹11,846.50) | FT FAIL · freq PASS |
| Fade-combo (restricted × 10:05) | +₹15,937.00 | +₹70,039.00 | April flip only (+210.00 → −3,050.00) | FT FAIL · freq PASS |

The pair is worth ₹210.00 less than the sum of its flags (UNIQUE-ONCE collisions — lesson 72). Even adopting the pair, the best flagged outcome, pace would be ₹9,116.85/month — still ₹58,831.50 short of the floor, with a red March as the priced cost. **All four remain NOT adopted; the decisions are the owner's.** The fade family stays closed (six gated forms, each refused on one named leg — no seventh form was proposed).

---

## Ending scorecard

| Measure | Value |
|---|---|
| Standing book (December causal candidate) | **+₹54,102.00** Jan–Oct 2026 |
| Monthly pace | **₹5,410.20/month** |
| Floor | ₹15,000/month (₹1,50,000 Jan–Oct) |
| **Remaining gap** | **₹95,898.00** |
| Legs / FT / frequency | 35 / 34.3% / 0.86 per week |
| Halves | +₹27,581.00 / +₹26,521.00 |
| Placebo (+30 min) | +₹22,876.00 (beaten) |
| Ex-top-3 | +₹20,637.00 |
| Months | Jan +17,096.75 · Feb +12,789.25 · Mar +7,895.00 · Apr +210.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,998.75 · Aug −1,701.00 · Sep +4,652.75 · Oct +16,480.50 |
| Controls | Audit 35/0 · NC 0 · re-sum exact |
| Banked this round | **None** (9 cycles) |
| Real money | ₹0 — paper only. November primary NF-PAPER-C3G7 untouched. |

## Honest closing assessment — what remains for this segment

The in-sample signal space for Nifty is essentially exhausted, and Round 10 closed its last two untested conditioning axes. After ten rounds and 167 cycles, every axis this window offers has been gated: the confirmation pool is at its peak (+₹54,102 is the causal centre, re-earned twice); solo books lose to the confirmed book; the window's discards are an adverse tail at causal entries; the post-expiry population is the same tail; strikes, geometry and expiry axes are at their grid peaks or closed; day-state admission is closed across six axes because every state earns; cross-index conditioning is empty in both constructions (Bank confirms too late; Bank spot never disagrees); gap-follow is ruinous and the gap-fade family is closed after six single-leg refusals; second legs do not transplant; afternoons are noise. There is no seventh fade form, no third conditioning axis, and no honest in-sample cycle left that this freeze discipline would allow — further rounds on Jan–Oct 2026 would be fitting noise, and the gate exists precisely to refuse that.

What remains is real, but none of it is another in-sample cycle:

1. **The owner's flagged decisions.** Four flagged items stand priced on the ending book (above). The largest, the jointly-priced pair (+₹37,066.50), would lift the book to +₹91,168.50 (₹9,116.85/month) at the cost of a red March and FT 34.0% — still short of the floor. Adopting any of them is a waiver of a named gate leg, recorded as FAILED-and-waived; the engine will not self-adopt.
2. **The owner's gate re-basing decision.** The old absolute lines (FT ≥ 42.0%, frequency ≥ 1.00/wk) were calibrated on the inadmissible book and remain referred, printed as status only. Re-basing is a pre-registered owner decision; it changes what "passes" means, not what the numbers are.
3. **December fresh data.** The segment's forward test is now frozen as a verified specification with a pre-registered pass/kill (Cycle 166). December will judge the causal candidate on data no cycle has seen — the only evidence that can still move this segment's standing. November's frozen primary runs separately and untouched.

The floor is not met: **₹5,410.20/month against ₹15,000, gap ₹95,898.00.** That is stated plainly, with controls, as the segment's ending position for Round 10.
