# Stocks (SarvaRitu) — VARIANT C ADOPTION + VERIFICATION RE-RUN
**Date:** 2026-11-02 · **Direction:** Chandu, 16:48 IST — "You apply the fix and run again."
**Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features · **frozen November book/scorecards/loggers/specs/logs untouched (read-only throughout).**
**Run:** `stocks_engine_adoptC_verify.py` · evidence `stocks_adoption_variantC_results.json` · gate = the frozen nine-leg session gate + leg (x), full controls in the same run (timing audit, placebos, halves, month table, ex-top-3, independent re-sum).

---

## 1. VERIFICATION RESULT — totals EXACT, no mismatch

**Check B (the headline):** Variant C rebuilt from the current ending book (Round-16 book: 2025 Jan–Oct ₹105,987.24 / 2026 Jan–Oct ₹257,300.30) by the frozen R9-04 stack construction reproduces the expected totals **to the paisa**:

| Year | Expected Jan–Oct | Rebuilt Jan–Oct | Full-year | Rows |
|---|---|---|---|---|
| 2025 | ₹119,813.44 | **₹119,813.44** | ₹121,764.83 | 1,108 |
| 2026 | ₹247,178.79 | **₹247,178.79** | ₹247,178.79 | 1,363 |

The adopted book is **row-for-row identical** (multiset on comp/date/stock/dir/entry_time/net) to the R9-04 gated build — the construction is baseline-invariant because every post-R9 banking touched only sleeves the stack replaces wholesale or leaves untouched (both directions verified in code). Exported CSVs (`stocks_engine_adoptedC_book{2025,2026}_trades.csv`) independently re-summed: exact.

**Check A (construction identity):** rebuilt on its birth baseline with the exact R9-WS1 recipe, Variant C reproduces its recorded R9-04 gate sheet **exactly** — all ten legs pass, sums ₹306,737.52 → ₹368,943.62, scorecards identical, placebos P1 ₹174,662.47 / P2 ₹344,925.15 / P3 ₹322,968.45, timing violations 0 (ingredients' counted violations: NE-REV 0 + REXP 0, asserted at build; the NOTCH/UPGUARD state reads the 10:25 NIFTY bar, complete at 10:30, strictly before every 10:35 entry).

**Check C (re-gate vs the pre-adoption book — reported in full):** gated against the Round-16 book, the adopted book passes **8 of 10 legs**:

| Leg | Verdict | Numbers |
|---|---|---|
| (a) combined rises | PASS | ₹364,889.48 → ₹368,943.62 (+₹4,054.14) |
| (b) 2025 no fall | PASS | full ₹107,589.18 → ₹121,764.83; JO ₹105,987.24 → ₹119,813.44 |
| (c) 2026 no fall | **FAIL** | ₹257,300.30 → ₹247,178.79 (**−₹10,121.51**) |
| (d) cells positive | PASS | all six regime cells > 0 |
| (e) ex-top-3 | **FAIL** | combined ₹118,176.37 → ₹101,823.96 (**−₹16,352.41**; 2026 leg: ₹76,137.46 → ₹55,557.16; both years stay ≥ 0 individually) |
| (f) no green-month flips | PASS | flip list empty (stack Jun 2025 +₹1,802.59, Jan +₹4,476.90, Dec +₹1,946.88) |
| (g) no half flips | PASS | — |
| (h) beats placebos | PASS | ₹368,943.62 > P2 ₹344,925.15 > P3 ₹322,968.45 > P1 ₹174,662.47 |
| (i) timing clean | PASS | 0 violations |
| (x) 2026 Jan–Oct ≥ ₹1,50,000 | PASS | ₹247,178.79 |

**Why (c) and (e) fail on this comparison — stated plainly:** the pre-adoption book's post-R9 bankings (the R11 pair with REXP at its R13-05 T100/S050 geometry, the R14-04 INV-ABOVE target step, the R14-05 fade stop step) out-earn the stack's frozen forms in 2026 and outside the top-3 names. Adopting Variant C trades ₹10,121.51 of 2026 for ₹13,826.20 of 2025 — the exact adoption values on record since Round 13. The construction's own frozen gate sheet (R9-04) passes all ten legs; on the current-baseline comparison, legs (c) and (e) stand as **failed-and-waived by the owner's direction** — the direction was given with those adoption values in front of him. No leg is edited, averaged away, or hidden.

---

## 2. ADOPTION RECORD
- **Adopted:** Variant C — the max stack with NE-REV-NOTCH+UPGUARD in the NE-REV slot (R2-26 INV-ABOVE exits T150/S080 + R5-03-clean GAP-FADE ≥1.25% DOWN+FLAT 09:20 with GAP-FADE-INC retired + NE-REV-NU + R7-03 REXP-SHORT DOWN-only T125/S050), gated whole at R9-04.
- **Effective:** 2026-11-02, on the owner's direction quoted above. It supersedes the Round-16 banked book as the Stocks **candidate book**. The pre-adoption book is preserved verbatim in state (`pre_adoption_incumbent_r16`) and stays the comparison baseline.
- **Recorded in:** `stocks_engine_state.json` (adoption block `adoption_variantC_2026_11_02`; incumbent → adopted CSVs; flagged list annotated entry-by-entry) and by dated addendum in the freeze documentation (banked-book freeze addendum + the adopted book's own freeze, below).
- **Not touched:** the frozen November SarvaRitu book, its scorecards, loggers, specs and logs; no new signal research was run.

## 3. DECEMBER FREEZE — extended to the adopted book, regeneration-verified
`stocks_engine_adopted_variantC_FREEZE_dec2026.md` now holds the adopted book's full tradeable specification: every component (seven sleeves row-identical to the pre-adoption book; INV-ABOVE in its R2-26 anchored form; GAP-FADE in the R5-03-clean form with GAP-FADE-INC retired; the NE-REV-NU slot; the R7-03 REXP add), timing certification per admission condition, and the regeneration chain (Round-16 CSVs → strip → swaps → slot → add) whose verification is Check B above: **PASSED, row-for-row and to the paisa**.
December pass/kill re-registered for the adopted book, same structure as the existing freeze:
- **PASS:** December net > ₹0 AND no ISO week of December worse than −₹15,000 AND ≥ 20 trades.
- **FLOOR LINE (separate):** December net ≥ ₹15,000.
- **KILL:** December net ≤ ₹0.
- **EXTEND:** < 20 trades → judging extends to January 2027, cumulatively. No parameter changes in December.

## 4. DECISION LIST — restated from the adopted baseline
### Alternative stack forms (same NE-REV slot; alternatives, NEVER additive; totals rebuilt and asserted in this run unless marked recorded)
| Form | 2025 JO | 2026 JO | Δ vs adopted (2025 / 2026) | Own gate sheet |
|---|---|---|---|---|
| **Variant C (ADOPTED)** | **₹119,813.44** | **₹247,178.79** | — | all ten pass (R9-04) |
| Unconditioned (CERT slot) | ₹123,231.11 | ₹247,547.25 | +₹3,417.67 / +₹368.46 | fails (f) — Jan + Dec flips |
| A (NOTCH slot) | ₹127,134.02 | ₹244,461.23 | +₹7,320.58 / −₹2,717.56 | fails (f) — Dec flip only; highest 2025 price |
| IDXCELL slot | ₹113,146.38 | ₹257,803.88 | −₹6,667.06 / +₹10,625.09 | all ten pass; only form that raises 2026 vs the adopted book |
| B (UPGUARD slot) | ₹115,155.58 | ₹250,060.98 | −₹4,657.86 / +₹2,882.19 | fails (e)+(f); dominated (recorded totals, delta arithmetic) |

### Surviving live flags (sleeve row-identity verified in this run — JO deltas carry exactly)
| Flag | Δ vs adopted (2025 / 2026) | Totals if adopted | Shape |
|---|---|---|---|
| R13-06 — NE-REV-NU geometry T125/S065 | +₹2,326.81 / −₹5,998.05 | ₹122,140.25 / ₹241,180.74 | buys 2025 with 2026 |
| R14-02 — F4 geometry T175/S095 | +₹6,280.30 / −₹10,767.28 | ₹126,093.74 / ₹236,411.51 | buys 2025 with 2026 |
| R14-03 — INV-LONG geometry T150/S050 | +₹4,275.39 / −₹10,547.95 | ₹124,088.83 / ₹236,630.84 | buys 2025 with 2026 |

(Each was gated at birth failing (a)+(c) vs its birth baseline; 2026 stays above the ₹1,50,000 floor line under each. They remain the owner's calls; the engine adopts nothing further on his behalf.)

### Superseded / contained by the adoption (no longer separate decisions)
- **Contained:** R2-26 (is the adopted INV-ABOVE form), R5-03 (R5-03-clean is the adopted fade sleeve), R7-03 (is the adopted REXP add), R9-04-STACK-NU itself (adopted — closed).
- **NE-REV standalone family** (R5-07, R5-07-CERT, R8-05 IDX, R6-02, R6-04, R7-06 quiet-name, R9-07-IDXCELL ingredient, R10-02 NU standalone, R10-03 NOTCH standalone, R10-04 NOTCHCELL): alternative slot forms — priced only through the stack-form table above; not additive to a book that already carries the NU slot.
- **REXP family** (R6-10 full, R7-02 DOWN+FLAT, R8-07 T100/S065): alternative/nested forms of the adopted REXP sleeve; not additive.
- **R8-06 FADE-IDX restriction:** priced on the pre-adoption fade population the adoption replaced — not applicable without a new gate (new research, not run).
- **R15-02 (INV-ABOVE T175/S050):** alternative form of the pre-adoption INV-ABOVE sleeve — superseded.
- **R3-10 (GAP-FADE LONG-only sub-sleeve):** superseded (already superseded in practice).
- **Stack records** (R8-MAXSTACK-GATED, R9-02, R9-03, R9-08, R6-01-TRIPLE): restated in the stack-form table above.

## 5. ENDING SCORECARD — the adopted book (per year, never pooled)
### 2025 — floor NOT met
Jan–Oct **+₹119,813.44 = ₹11,981.34/month · gap to floor ₹30,186.56** · full-year +₹121,764.83 · 1,108 trades (1,064 in Jan–Oct) · ex-top-3 (full) +₹46,266.80 (top-3: OBEROIRLTY ₹39,542.99, ASTRAL ₹22,268.52, GODREJCP ₹13,686.52).
Months (Jan–Oct): Jan +₹4,476.90 · Feb +₹25,913.57 · Mar +₹8,412.63 · Apr +₹53,220.39 · May +₹6,518.38 · Jun +₹1,802.59 · **Jul −₹660.91** · Aug +₹13,486.06 · Sep +₹10,686.50 · **Oct −₹4,042.67** · (Nov +₹4.51 · Dec +₹1,946.88, outside the judged window). Halves: H1 +₹98,541.87 · H2 +₹21,271.57.
Regime cells (full): DOWN +₹66,566.97 · FLAT +₹30,787.40 · UP +₹24,410.46.
Components (full, rows/net): F4 246 / +₹91.14 · GAP-FADE 112 / +₹32,064.93 · INV-ABOVE 131 / +₹17,248.75 · INV-LONG 291 / +₹23,894.61 · INV-R3 4 / −₹230.42 · N4-V3 35 / +₹5,851.63 · NE-REV-NU 200 / +₹12,596.19 · P2F 26 / +₹15,884.42 · P2F-R2 21 / −₹390.06 · R2-LOWBAND 1 / −₹116.75 · REXP 41 / +₹14,870.39.

### 2026 — floor MET
Jan–Oct **+₹247,178.79 = ₹24,717.88/month** (₹97,178.79 above the floor line) · 1,363 trades · all ten months green (thinnest: Jun +₹6,756.75) · ex-top-3 (full) +₹55,557.16 (top-3: TVSMOTOR ₹101,522.89, OBEROIRLTY ₹47,976.08, ASTRAL ₹42,122.66).
Halves: H1 +₹149,410.01 · H2 +₹97,768.78. Regime cells (full): DOWN +₹219,008.90 · FLAT +₹11,915.35 · UP +₹16,254.54.
Components (full, rows/net): F4 355 / +₹103,055.93 · GAP-FADE 292 / +₹4,270.42 · INV-ABOVE 31 / +₹7,471.54 · INV-LONG 182 / +₹50,160.09 · INV-R3 4 / +₹763.95 · N4-V3 34 / +₹29,562.32 · NE-REV-NU 313 / +₹23,744.40 · P2F 31 / +₹20,116.78 · P2F-R2 32 / +₹15,149.33 · R2-LOWBAND 3 / +₹1,283.36 · REXP 86 / −₹8,399.33.

### Comparison baseline (pre-adoption book, retained)
2025 Jan–Oct ₹105,987.24 (₹10,598.72/mo; gap ₹44,012.76) · 2026 Jan–Oct ₹257,300.30 (₹25,730.03/mo; floor met). Adoption deltas: **2025 +₹13,826.20 · 2026 −₹10,121.51 · combined full +₹4,054.14.**

## Deliverables of this run
- `stocks_engine_adoptC_verify.py` (the run) · `stocks_adoption_variantC_results.json` (evidence: both gate sheets, placebo totals, alternative-stack rebuilds, sleeve-identity checks, scorecards)
- `stocks_engine_adoptedC_book2025_trades.csv` / `stocks_engine_adoptedC_book2026_trades.csv` (the adopted book, independently re-summed)
- `stocks_engine_adopted_variantC_FREEZE_dec2026.md` (December freeze of the adopted book) · adoption addendum in `stocks_engine_banked_book_FREEZE_dec2026.md`
- `stocks_engine_state.json` updated (adoption block; incumbent → adopted book; pre-adoption incumbent preserved; all 28 flagged entries annotated) · cycles ADOPT-01…03 appended · log entry appended
