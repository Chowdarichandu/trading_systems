# Stocks (SarvaRitu) Engine — ROUND 9 · Flip Decomposition + Stack-Minus-Flaw Pricing, ATH-Proximity Sleeve, NE-REV December Repair
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-6/7/8 ending book, causality-audited; re-verified by independent re-sum of the exported CSVs before any Round-9 scoring): 2025 Jan–Oct **+₹78,420.04** (₹7,842.00/mo; gap ₹71,579.96) · 2026 Jan–Oct **+₹2,29,696.21** (₹22,969.62/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code (lessons R4-L2, R6-L4, Nifty-46, R6-11) — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round: a condition may reference state (index level/move, regime cell, price bands), never the calendar.**
- **Flagged, NOT adopted** (Chandu's calls; baselines stay on the book without them): R2-26 (clean sheet), R5-03 (fails (e)), R5-07 / R5-07-CERT (fail (e)+(f)), R8-05 IDX (fails (e)+(f)), R6-02 (fails (e)), R6-04 (fails (e)), R6-10 (fails (c)), R7-02 (fails (c)), R7-03 (fails (c)), R8-07 (fails (c)), R7-06 (fails (e)+(f)), R8-06 (fails (c)), and the gated max stack (fails (f) only, R8-02).

---

## PRE-REGISTRATION (written before any Round-9 variant is scored; the WS0/R9-01 decomposition and the state diagnoses it rests on are audits, completed before this freeze)

### WS0 — Flip decomposition (R9-01, audit)
Each max-stack ingredient applied ALONE to the starting book (constructions re-anchored at their R8-01 prices); per-month deltas are exact because the ingredients act on disjoint components. The two flips are attributed before any variant is designed.

### WS1 — Stack-minus-flaw variants (R9-02, R9-03, R9-04 — ALL decision support, force_no_bank)
The stack is the R8-02 construction (R2-26 swap + R5-03-clean swap with GAP-FADE-INC retired + NE-REV slot + R7-03 add) with the NE-REV slot's population conditioned by ONE frozen state rule per variant. The state feature is NIFTY's intraday move at the signal bar: `nifty_move(day, "10:25")` = close of NIFTY's 10:25 bar vs NIFTY's prior-day close (the R8-05/R8-06 feature; the bar completes at 10:30, every NE-REV entry is at 10:35 — the state is knowable strictly before entry). A row whose state is unknown (missing NIFTY bar or prior close) is counted and NOT admitted — never guessed.

- **Variant A (R9-02) — NE-REV-NOTCH in the stack.** Admit a CERT row only when its NIFTY 10:25 move is **not** in the open band **(−0.30%, 0)** — the index is either down ≥ 0.30% (a systemic dip) or flat/up (an idiosyncratic stock fall). *Separator, stated from the diagnosis before scoring:* the (−0.30, 0) bucket is the only NIFTY-state bucket negative in 2025 (−₹4,513.24) and the only one negative combined (−₹1,427.22 over 67 rows); it holds the January wound's address (2025 DOWN-cell × middle bucket −₹5,991.46; January's own middle-bucket rows −₹5,192.36 of NE-REV's −₹2,950.92 January).
- **Variant B (R9-03) — NE-REV-UPGUARD in the stack.** Admit a CERT row on an **UP-regime day only when its NIFTY 10:25 move ≥ 0**; DOWN/FLAT-day rows admitted unconditionally. *Separator:* all six December-2025 CERT rows sit on UP-regime days; the UP × (NIFTY < 0) bucket holds all three December losers that the index-dip state admits (−₹2,046.64) and is negative in 2026 (−₹2,513.73) — on an up-regime day, a ≥2% stock fall while the index is also falling intraday is a regime crack, not a dip.
- **Variant C (R9-04) — NE-REV-NOTCH+UPGUARD in the stack.** Both conditions applied together (a row must satisfy each that applies to it).
- **Placebos (whole books, same stack structure incl. GAP-FADE-INC retirement), per variant:** P1 all-placebo — R2-26 SHORT-side swap + GAP-FOLLOW mirror SHORT sleeve + the variant's conditioned FLIPPED (SHORT) NE-REV rows + REXP LONG on DOWN cells. P2 — the real stack with the variant's conditioned NE-REV rows one bar late. P3 — the real stack (with the variant's real conditioned NE-REV) with the gap sleeve one bar late. Timing violations: the sum of the ingredients' own counted violations (asserted 0) — the state conditions add none (state bar completes 10:30 < 10:35 entries).
- Each variant is recorded with force_no_bank regardless of verdict — adoption of any stack form is Chandu's.

### WS2 — ATH-proximity momentum sleeve (R9-05, bankable candidate)
- **Trigger (daily data, causal):** for stock S and session T (a weekday in S's daily series, with at least 252 prior sessions available), let H(T) = max daily high over the 252 sessions ending at T inclusive. T is a trigger day iff close[T] ≥ 0.98 × H(T). Every input is known at T's close.
- **Entry:** the next session T+1 in S's daily series, LONG at the open of the **09:35** bar (weekend entry days excluded per engine convention; if T+1 has no 09:35 bar, no trade — counted). At most one trade per (stock, entry day) — each entry day has exactly one trigger day (its prior session) by construction.
- **Event rule (frozen):** NO event exclusion. The sleeve trades on price state alone; results/news days are admissible. (The certified-set standard binds sleeves whose premise is a non-event day; this sleeve's premise is a daily price state, stated here so the population is unambiguous.)
- **Exits:** T125/S050 via `replay_plain` (entry bar checked), square-off 15:10 — the frozen machinery defaults. ₹40/trade.
- **Placebos (whole books, identical population):** opposite direction (SHORT) at the same entry bar; same direction one bar later (09:40 open). Timing audit: violations = rows whose entry session is not strictly after the trigger session — counted in code from the series indices (structurally impossible; asserted 0).

### WS3 — NE-REV-IDX December repair (R9-06 decomposition audit; R9-07 standalone gate; R9-08 stack price, decision support)
- R9-06 decomposes the R8-05 IDX form's December-2025 rows by name / regime cell / state (audit; the rows are already known from the WS0 diagnosis: 3 rows, all UP-cell).
- **Repaired ingredient (frozen): NE-REV-IDXCELL** — the R8-05 IDX rows (certified population, NIFTY 10:25 move ≤ −0.30%) restricted to **DOWN+FLAT regime cells** (the trade day's frozen regime label). *Separator:* every December-2025 IDX row is an UP-cell row; the IDX UP-cell bucket is the form's only negative cell in 2026 (−₹2,717.56) — an index-dip bounce bought on an up-regime day is the sleeve trading against its own regime premise. The 2025 cost is stated before scoring: the IDX UP bucket carries +₹6,022.69 of 2025 standalone, so this repair is expected to be expensive in the weak year — the gate, not the hope, decides.
- R9-07 gates IDXCELL as a whole-book addition on the starting book (comp `NE-REV-IDX`), placebos = the same cell restriction applied to the IDX flipped and one-bar-late rows. A full pass banks (it is an ingredient, not a stack).
- R9-08 prices the max stack with the NE-REV slot = NE-REV-IDXCELL (decision support, force_no_bank; placebos shaped as in WS1 with the IDXCELL rows).

### WS4 — Combinations + decision state (R9-09 / R9-10)
- Any two or more Round-9 bankings are combined and re-gated whole-book. If fewer than two bankings exist, the combination part closes by statement.
- Finalise: ending books exported and independently re-summed; every flagged variant's adoption value and every stack price restated on the ending book (R6-L5 discipline — disjoint-comp deltas applied arithmetically, method stated; nested/alternative flags marked as such, never summed); state updated. Nothing in the finalise cycle is banked.

### Verdict rule (frozen for all Round-9 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks — except WS1 and R9-08, which are force_no_bank by construction (stack adoptions are Chandu's). A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R9-01 — WS0 FLIP DECOMPOSITION (audit): both flips belong to NE-REV-CERT alone
Each ingredient applied alone to the starting book; the month deltas sum exactly to the R8-02 gate sheet (Jan −₹2,915.77, Dec −₹1,307.71 — verified in code):

| Ingredient | Jan 2025 delta | Dec 2025 delta |
|---|---|---|
| R2-26 (INV-ABOVE swap) | +64.16 | +532.91 |
| R5-03-clean (fade swap, INC retired) | −29.01 | 0.00 |
| **R5-07-CERT (NE-REV add)** | **−2,950.92** | **−1,840.62** |
| R7-03 (REXP-SHORT DOWN add) | 0.00 | 0.00 |

- **January offender: NE-REV-CERT, entirely.** Its 66 January rows (all on DOWN-regime days) net −₹2,950.92. Inside them, the wound has an exact state address: rows on days when NIFTY's 10:25 move sat in the shallow-dip band (−0.30%, 0) lose **−₹5,192.36 on 12 trades** (the DOWN × middle-bucket cell is −₹5,991.46 across 2025); the same rows on index-down-hard days (≤ −0.30%) net −₹428.15 and on index-up days +₹2,669.59. By name the bleed is broad (GLENMARK −₹2,956.54 on 3, UNITDSPR −₹2,038.00, TVSMOTOR −₹1,493.82 — against OBEROIRLTY +₹3,712.76, BDL +₹1,347.71): no name slice is the story; the index state is.
- **December offender: NE-REV-CERT, entirely.** Its 6 December rows (all on UP-regime days) net −₹1,840.62: BDL −991.79 (12-08) and −929.85 (12-16), HINDUNILVR −1,586.48 (12-05) and +450.00 (12-12), HINDCOPPER −125.00 (12-16), UNITDSPR +1,342.50 (12-18). The three rows admitted on index-dip days (NIFTY ≤ −0.30%) sum −₹2,046.64; the three on index-up days sum +₹206.02.

Full per-ingredient month tables and row detail: `r9_ws0_decomp.json`.

## WS1 — Stack-minus-flaw variants (all decision support, force_no_bank)

### R9-02 — Variant A (NE-REV-NOTCH slot): fails (f) only — and is worth more than the unconditioned stack
The notch sleeve (262/332 rows kept; state-unknown dropped 0) standalone: **+₹18,618.88 (2025) / +₹21,026.84 (2026)** — the restriction *raises* the weak year (it removes a −₹4,513.24 bucket) and costs 2026 ₹3,086.02. In the stack: 2025 JO **₹1,27,134.02** (₹12,713.40/mo — the highest 2025 stack price), 2026 JO ₹2,44,461.23, combined ₹3,72,248.75 (above the unconditioned stack's ₹3,70,821.53). Stack January: **+₹4,476.90 — cured.** Stack December: −₹99.76 — the (f) failure that remains is December alone. Placebos beaten (P1/P2/P3 as frozen). Failing legs: **(f) only**.

### R9-03 — Variant B (NE-REV-UPGUARD slot): fails (e) + (f)
The upguard sleeve (218/345 rows) standalone: +₹7,938.33 / +₹26,626.59 — December is cured at sleeve level, but the kept 2025 population is thin and carrier-heavy. In the stack: 2025 JO ₹1,15,155.58, 2026 JO ₹2,50,060.98; stack December +₹1,946.88 (cured), stack January −₹715.46 (flip remains), and leg **(e) fails** (2025 ex-top-3 ₹40,244.34 but the combined ex-top-3 test fails — the cure's kept value concentrates). Failing legs: **(e), (f)**. Dominated by Variant C as a stack form.

### R9-04 — Variant C (NE-REV-NOTCH+UPGUARD slot): **PASSES ALL TEN LEGS — the clean-adoption price**
The doubly-conditioned sleeve (200/313 rows) standalone: +₹12,596.19 / +₹23,744.40. In the stack: 2025 JO **₹1,19,813.44 (₹11,981.34/month; gap would fall to ₹30,186.56)**, 2026 JO **₹2,47,178.79**, combined ₹3,68,943.62. Stack January **+₹4,476.90**, stack December **+₹1,946.88** — both flips cured; halves, cells, ex-top-3 (2025 → ₹46,266.80), placebos and leg (x) all pass; timing violations 0. Recorded with force_no_bank per the freeze: **this is the price at which the stack needs no waiver — ₹3,417.67 of 2025 JO below the unconditioned stack (R8-02) and ₹7,320.58 below Variant A.** Adoption is Chandu's.

## WS2 — ATH-proximity sleeve (R9-05): REJECTED on eight legs — strength-following loses at the daily timescale too
Population: 346 trigger days → 342 trades (113 in 2025, 229 in 2026; skips: 1 weekend entry, 3 missing 09:35 bars). Standalone **−₹21,322.97 (2025) / −₹27,329.31 (2026)**; book JO falls to ₹73,381.33 / ₹2,02,366.90; December 2025 flips hard (+₹1,207.95 → −₹13,330.65); beaten by its own placebos. Fails (a), (b), (c), (d), (e), (f), (g), (h). Not flagged — eight legs is not a near-miss. Buying closes near a 52-week high on the home 25 is a fade target, not a follow signal — the same verdict the tapes gave intraday (R8-L2), now at the daily-state timescale.

## WS3 — NE-REV-IDX December repair (R9-06 audit; R9-07 gate; R9-08 stack price)
- **R9-06:** the IDX form's December is exactly 3 rows, all UP-cell (BDL −991.79, HINDCOPPER −125.00, BDL −929.85; −₹2,046.64). The IDX UP bucket overall: 2025 62 tr **+₹6,022.69** (the form's best 2025 cell), 2026 19 tr **−₹2,717.56** (its only negative 2026 cell) — the repair's stated cost was known before scoring.
- **R9-07 — NE-REV-IDXCELL standalone: REJECTED on (e) only.** The repaired ingredient (139/233 rows) standalone +₹4,032.51 / +₹34,369.49; book 2025 JO → **₹82,452.55**, 2026 JO → **₹2,64,065.70**; **no month flips anywhere** (December exposure removed by construction) and every other leg passes, placebos beaten. It fails only the concentration leg — the December repair is real, and its price is the 2025 UP bucket. Flagged as the NE-REV family's no-flip form.
- **R9-08 — Stack with the IDXCELL slot: PASSES ALL TEN LEGS (decision support).** 2025 JO **₹1,13,146.38 (₹11,314.64/month; gap ₹36,853.62)**, 2026 JO **₹2,57,803.88** (the highest 2026 stack price), combined ₹3,71,005.03; stack January +₹1,807.31, stack December +₹1,740.86 — both green. A second fully-gated stack price, ₹6,667.06 of 2025 JO below Variant C and ₹10,625.09 of 2026 JO above it.

## WS4 — Combinations (R9-09)
Zero Round-9 bankings (R9-05 rejected on eight legs; R9-07 on (e) alone; R9-02/03/04 and R9-08 are decision support by construction) — no combination exists to re-gate. Closes by statement. Ending books exported to `stocks_engine_r9_book{2025,2026}_trades.csv` and independently re-summed to the paisa — identical to the starting book.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met (banked book unchanged)
Jan–Oct **+₹78,420.04** = **₹7,842.00/month** · **gap to floor ₹71,579.96 (unchanged — Round 9 banked nothing)** · full-year +₹77,041.31 · 887 trades · ex-top-3 stocks **+₹23,708.10** (top-3: OBEROIRLTY ₹30,748.68, ASTRAL ₹14,260.02, GLENMARK ₹8,324.51).
Months: Jan +₹2,200.31 · Feb +₹20,242.66 · Mar +₹8,953.57 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹7,083.39** · Aug +₹11,173.48 · Sep +₹5,585.44 · **Oct −₹3,944.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹73,644.96 · H2 +₹4,775.08.
Regime cells (full-year): DOWN +₹42,941.63 · FLAT +₹21,250.68 · UP +₹12,849.00.

### 2026 — floor MET (unchanged)
Jan–Oct **+₹2,29,696.21** = **₹22,969.62/month** (₹79,696.21 above the floor line) · 969 trades · all ten months green · ex-top-3 stocks +₹77,473.77.
Regime cells (full-year): DOWN +₹2,10,264.94 · FLAT +₹2,909.78 · UP +₹16,521.49.

Books: `stocks_engine_r9_book2025_trades.csv`, `stocks_engine_r9_book2026_trades.csv` (the starting book, re-summed). Evidence: `r9_results.json` (9 records: 2 gated candidates, 4 decision-support gates, 3 audits), `r9_ws0_decomp.json`. Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R9-L1…R9-L5). State: `stocks_engine_state.json` (`round9_summary`, 21 flagged entries).

## Decision state after Round 9 (owner's calls, none taken by the engine — all restated on the ending book)
- **R9-04-STACK-NU — the clean stack: PASSES ALL TEN LEGS.** Adoption → 2025 JO **₹1,19,813.44 (₹11,981.34/month), gap ₹30,186.56**, 2026 JO ₹2,47,178.79. No waiver needed on any leg. This is now the headline Stocks decision.
- **R9-08-STACK-IDXCELL — the second clean stack: PASSES ALL TEN LEGS.** Adoption → 2025 JO **₹1,13,146.38 (₹11,314.64/month), gap ₹36,853.62**, 2026 JO ₹2,57,803.88.
- **R9-02-STACK-NOTCH** — fails (f) on December only; the highest 2025 price: adoption → 2025 JO **₹1,27,134.02 (₹12,713.40/month), gap ₹22,865.98**, 2026 JO ₹2,44,461.23.
- **R8-MAXSTACK-GATED** (unconditioned) — fails (f) only: 2025 JO ₹1,23,231.11, gap ₹26,768.89. **R9-03-STACK-UPGUARD** — fails (e)+(f): ₹1,15,155.58. (Stack forms are alternatives to each other, never additive.)
- **R9-07-IDXCELL** (ingredient) — fails (e) only, no flips: adoption → 2025 JO ₹82,452.55, 2026 JO ₹2,64,065.70. NE-REV-family alternative.
- All Round-8 flags stand at their restated prices (R2-26 clean → ₹85,954.04; R5-03 (e) → ₹86,709.48; R5-07-CERT (e)+(f) → ₹92,537.28; R8-05 (e)+(f) → ₹89,773.13; R6-02 (e) → ₹84,820.98; R6-04 (e) → ₹78,964.15; R7-06 (e)+(f) → ₹82,466.59; R6-10 (c) → ₹94,435.04; R7-03 (c) → ₹93,290.43; R8-07 (c) → ₹88,663.49; R7-02 (c) → ₹90,573.21; R8-06 (c) → ₹82,018.25; the triple (e)+(f) → ₹1,06,558.02). NE-REV-family flags are alternatives to each other; REXP flags are nested forms of one population; no stack form is additive with any single flag.

## Where the 2025 floor can still come from (honest close)
Round 9 banked nothing on the traded book — and finished the pricing job Round 8 started. The (f) failure that stood between the book and ₹1,23,231.11 is now fully attributed (one ingredient, two state addresses) and **two stack forms pass all ten legs**: the owner's decision is no longer "waive a leg or not" but "which clean price" — ₹1,19,813.44 (NOTCH+UPGUARD) or ₹1,13,146.38 (IDXCELL) — against the one-leg prices ₹1,27,134.02 (NOTCH, December flip only) and ₹1,23,231.11 (unconditioned, both flips). Inside the gate, on the banked book, the remaining ₹71,579.96 has no Round-9 engineering answer: the last untested follow form (ATH-proximity) lost in both years, closing the follow family at every timescale, and the December/January repairs all live in the flagged stack forms. Beyond owner decisions, the routes are unchanged: a new data axis (volume / bulk-block / delivery % — none in the workspace), or Nov–Dec forward evidence on the frozen book.
