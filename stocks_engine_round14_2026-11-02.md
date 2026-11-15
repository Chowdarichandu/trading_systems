# Stocks (SarvaRitu) Engine — ROUND 14 · exit-geometry neighbours on the original sleeves
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-13 ending book): 2025 Jan–Oct **+₹1,03,357.44** (₹10,335.74/mo; gap ₹46,642.56; red Jan–Oct months Jul −₹2,000.01 / Oct −₹3,751.28) · 2026 Jan–Oct **+₹2,53,068.45** (₹25,306.85/mo; floor MET). To be re-verified by independent re-sum of `stocks_engine_r13_book{2025,2026}_trades.csv` in R14-01 before any Round-14 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): the 25 flagged entries through Round 13, incl. the max stack and its forms. Round 14 adopts nothing on Chandu's behalf; its bankable candidates are gated on the banked book. Closed for good and not re-run: sweep-reclaim/reject family, standalone NE-REV, single-leg flag re-tests, July/October wound separators.
- **Round 14's premise:** Rounds 11–13 proved that single-axis geometry swaps on recently-banked sleeves can pass on this book (REXP-DOWN's stop step banked at R13-05; R8-L4/R13-L2: a geometry neighbour prices a leg, and only the single-axis step attributes it). The ORIGINAL sleeves' exit geometry has never been re-gridded as whole-sleeve swaps on this book — F4's neighbours were measured on the v1/v2 books or per regime cell (R2-20…23), the INV grid predates the R2-07 law, the fade's Round-5 neighbours moved two axes at once, N4's scorecard cell was never re-gated after the FLOOR-2 cap and the 0.8% threshold changed its population, and the P2F family's two tests both moved target and stop together (Lesson 33). At most **ONE adjacent neighbour per sleeve**, frozen below before any candidate is scored.

---

## PRE-REGISTRATION (written before any Round-14 candidate is scored)

### R14-01 — Starting-book verification (audit)
The starting books are re-summed from `stocks_engine_r13_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹1,03,357.44 / full ₹1,03,354.23 / 1,105 rows; 2026 JO ₹2,53,068.45 / full ₹2,53,068.45 / 1,352 rows; Jul 2025 −₹2,000.01; Oct 2025 −₹3,751.28). No candidate is scored if the audit fails.

### The GAP-FADE neighbour was chosen by a frozen diagnostic rule (disclosed)
The fade family had no record-dictated pick, so its neighbour was chosen by the SAT-10/11/12 discipline: a first-passage excursion diagnostic on the sleeve's own banked population (404 rows, regenerated at the book cell and asserted row-for-row against the book before diagnosis — `stocks_engine_r14_diag.py`), with the pick rule stated before it ran: *the axis with the larger combined rough swing is frozen; a tie goes to the stop axis.* Result: stop axis **+₹12,157.87** (2025 +₹1,269.48 — 51 stop-outs, rescue +₹5,583.67 / deeper −₹4,457.98 / neither +₹143.78; 2026 +₹10,888.39 — 191 stop-outs, rescue +₹27,295.75 / deeper −₹19,689.70 / neither +₹3,282.34); target axis **−₹1,556.33** (2025 +₹2,189.95; 2026 −₹3,746.28). **Frozen pick: T125/S065.** The estimate only chooses which cell earns an exact score — Lesson 31 stands: it can be sign-wrong, and the gate decides. Prior disclosed: R5-L2's two-axis cells around this sleeve (T100/S065 loses both years; T150/S065 fails (c) alone) — neither is the single-axis stop step frozen here.

### The six frozen swaps (each replaces its sleeve's rows whole-book at the candidate geometry; population, admission and entries unchanged)
1. **R14-02 — F4: T150/S095 → T175/S095** (target step only, the adjacent grid rung; the T175 pop already exists in the Round-2 cache). Priors disclosed: SAT-12's T165 excursion estimate was negative (−₹8,293 rough, 2026 window, v1 book) and closed the target family *on an estimate* — Lesson 31 licenses exactly one exact re-test; the whole-sleeve T175 form was never gated (R2-21/23 tested it per regime cell only, on the Round-2 book). S110 is exactly closed cross-year (v2 C12) and S080 is the retired cell; T175/S095 is the only F4 neighbour never exactly scored as a whole-sleeve swap.
2. **R14-03 — INV-LONG: T125/S050 → T150/S050** (target step only), population re-formed by `run_chain` at the candidate geometry under the current law (ADR ≥ 3.0, rounds ≤ 3, entry < 11:00, FLAT stand-aside). Prior disclosed: the SAT-5 grid peaked at T125/S050 — on the pre-R2-07 population (rounds ≤ 2, 10:30 cutoff); the current population has never had a neighbour gated. The target axis is chosen because the family's only positive geometry evidence sits on it (R2-26, the sibling pool at the wider target).
3. **R14-04 — INV-ABOVE: T125/S050 → T150/S050** (target step only), population re-formed by `run_chain` at the candidate geometry under the current law (ADR ≥ 3.0, rounds ≤ 2, entry < 10:30) **with the R12-02 hard-dip exclusion re-applied to the new rows** (bucket from the NIFTY move at the bar completing at each row's own entry instant; hard ≤ −0.30% dropped). This cell decomposes the flagged R2-26 swap (T150/S080, fails (f) only): if the March flip survives at the incumbent stop, it is a target effect; if it vanishes, it was the stop.
4. **R14-05 — GAP-FADE + GAP-FADE-INC: T125/S050 → T125/S065** (stop step only, both comps; chosen by the diagnostic above).
5. **R14-06 — N4-V3: T150/S080 → T125/S050** (the November-scorecard cell, gated as a whole-sleeve swap on this book, as tasked). The population is the current one — thr 0.8% standard entry, full law, FLOOR-2 one-sided cap, **minus the four R6-11 voided rows** (BDL 2025-01-16; HINDZINC 2026-07-24; HINDUNILVR 2026-10-28; VEDL 2026-10-28), which stay void at every geometry. Disclosure: this re-prices the SAT-15 rebuild on the population that exists now (Lesson 46: the cell is population × geometry; the cap, the threshold change and the voids all postdate SAT-15).
6. **R14-07 — P2F + P2F-R2: T125/S050 → T150/S050** (target step only, one family swap). **Stated reason (required by the round's charter):** both prior geometry tests on this family moved target and stop together (T150/S080 — P2F: 2025 −₹4,132.23 / 2026 +₹301.50; P2F-R2: 2025 +₹703.28 / 2026 −₹3,921.20), so the family's 2025 bleed cannot be attributed to either axis; R13 proved the single-axis step is the informative unit on this book. The target-only step at the incumbent stop is the one cell that attributes it: if 2025 still bleeds, the target is the cost; if it recovers, the stop was.

### Anchors (asserted in code before any candidate is gated; a failed anchor stops the workstream, it is never patched silently)
- **F4:** re-scoring the banked rows from their entry bars at (1.50, 0.95) reproduces the banked nets exactly; re-scoring at (1.75, 0.95) reproduces `f4_rows` on the cached T175 pop exactly (the replay variant is identified by the anchor, not assumed).
- **INV-LONG / INV-ABOVE:** the cached T125/S050 chain pop under the current law (plus the hard-dip exclusion for INV-ABOVE) reproduces the banked rows of each comp exactly.
- **GAP-FADE family:** `gap_rows` at (1.25, 0.50) reproduces both comps' banked rows exactly (sums already asserted in the diagnostic; the workstream asserts multiset identity).
- **N4-V3:** the parameterised builder at (1.50, 0.80) — thr 0.8%, standard entry, law + cap, minus the four voids — reproduces the banked rows exactly.
- **P2F family:** re-scoring the banked rows from their entry bars at (1.25, 0.50) reproduces the banked nets exactly for both comps (replay variant identified by the anchor).

### Placebos (per sleeve, at the candidate geometry — the R13 swap convention)
- **F4 / N4-V3 / P2F family:** the flipped book (opposite direction on identical entries) and the one-bar-late book (same direction, entry one bar later), each swapped in at the candidate geometry; leg (h) reads their combined totals. (N4's late form: entry at the 09:35 bar's close with no confirmation condition — the signal bar's close is the standard entry, so one bar later is the next bar's close.)
- **INV-LONG / INV-ABOVE:** the chain's SHORT-side population at the candidate geometry under the same law filters (the R2-25/26 precedent — a chain has no one-bar-late form; its opposite side is the control the machinery itself generates).
- **GAP-FADE family:** the mirror book (follow direction on the identical gap population) and the one-bar-late book (09:20→09:25 bar for GAP-FADE; 09:40→09:45 for GAP-FADE-INC), per the R4/R6 convention.

### Timing (asserted per construction)
Exit geometry carries no admission information: every swap keeps its sleeve's banked entries (F4, GAP-FADE, N4, P2F) or re-forms them causally (INV: `run_chain` picks never read exit outcomes — round-1 entry identity across geometries is asserted, per the R2 capture note). Entry bars, signal bars and the certified event set are untouched; the four R6-11 voids stay void. Violations are counted and must be 0.

### R14-08 — Combinations + stack maintenance + December freeze addendum
Candidates are each gated against the **starting** book. Resolution (the standing WS4 rule): the six swaps act on disjoint components and compose; if more than one banking passes, the union is re-gated whole-book against the starting book — if the union passes it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded. The four stack prices are restated on the ending book by the R12-09 generalised method (totals must reproduce the recorded prices exactly). **December freeze addendum:** the freeze document is extended to the new ending book, and the extension is **regeneration-verified** — the ending book rebuilt from the Round-13 CSVs plus the banked Round-14 constructions by fresh code must match the exported ending CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. Ending books exported to `stocks_engine_r14_book{2025,2026}_trades.csv` and independently re-summed. If nothing passes, R14-08 closes by statement (stack prices and the freeze addendum are still restated/extended on the unchanged book). Rejected candidates failing at most two legs join the flagged list as owner decisions, with adoption values measured from the ending book.

### Verdict rule (frozen for all Round-14 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the R14-08 resolution). A candidate failing any leg is recorded with its failing legs named; the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R14-01 — STARTING-BOOK VERIFICATION (audit, passed)
Books re-summed from the Round-13 CSVs: 2025 JO ₹1,03,357.44 / full ₹1,03,354.23 / 1,105 rows; 2026 JO ₹2,53,068.45 / full ₹2,53,068.45 / 1,352 rows — exact vs the Round-13 record; Jul 2025 −₹2,000.01 and Oct 2025 −₹3,751.28 asserted. No scoring preceded this audit.

## WS1 — F4 (R14-02)
Anchors: three-way, all exact — `f4_rows` on the cached T150/S095 pop == the banked rows; entry-bar re-scoring at the book cell reproduces the banked nets (flavour identified: `replay_plain`; the 8 Oct-29/30 rows score from the forward root, per R6-L4); re-scoring at T175/S095 reproduces the cached T175 pop exactly.

**R14-02 — F4 T175/S095: REJECTED on (a) + (c).** Sleeve ₹6,371.44 / ₹92,288.65 vs the banked cell's ₹91.14 / ₹1,03,055.93 — JO deltas **+₹6,280.30 / −₹10,767.28**: the wider target buys 2025 and charges 2026, the R13-L2 year-trade on a third sleeve family. Combined falls to ₹3,51,935.70; placebos beaten (flipped ₹1,52,811.29; late ₹3,42,422.71); no flips; timing 0. SAT-12's estimate-based closure of the F4 target family is now confirmed in substance by an exact cross-year score (Lesson 31's re-test, discharged). **Flagged as an owner decision** (two failing legs): adoption from the ending book → 2025 JO +₹6,280.30 / 2026 JO −₹10,767.28.

## WS2 — INV-LONG AND INV-ABOVE (R14-03, R14-04)
Anchors: the cached T125/S050 chain pop under each comp's current law reproduces the banked rows exactly (INV-ABOVE with the hard-dip exclusion dropping 23 / 16, the R12 census counts); round-1 entry identity holds across geometries.

**R14-03 — INV-LONG T150/S050: REJECTED on (a) + (c).** Sleeve +₹28,170.00 / +₹39,612.14 on the re-formed population (277/174 rows) vs the banked cell's +₹23,894.61 / +₹50,160.09 — JO deltas **+₹4,275.39 / −₹10,547.95**, the same year-trade. Side placebo beaten (₹2,49,087.14); no flips; timing 0. The SAT-5 grid peak is confirmed for the current population on the target axis: T125/S050 stands. **Flagged as an owner decision** (two failing legs): adoption from the ending book → 2025 JO +₹4,275.39 / 2026 JO −₹10,547.95.

**R14-04 — INV-ABOVE T150/S050: BANKED — ALL TEN LEGS PASS.** Sleeve JO +₹12,513.28 / +₹10,114.82 (124/20 rows; the hard-dip exclusion re-applied at the new geometry drops 22 / 15) vs the banked cell's JO +₹10,463.16 / +₹7,361.39 — **both years improve: 2025 JO → ₹1,05,407.56 (+₹2,050.12); 2026 JO → ₹2,55,821.88 (+₹2,753.43)**; combined ₹3,56,422.68 → ₹3,62,831.38 against the starting book. Side placebo beaten; no flips; leg (x) holds. The decomposition the cell was bought for: **the flagged R2-26 swap's March flip was its stop widening, not its target** — at the incumbent stop, the wider target flips nothing. R2-26 (T150/S080) stays flagged as a whole; its target half now lives in the banked book at S050.

## WS3 — GAP-FADE FAMILY AND N4-V3 (R14-05, R14-06)
Anchors: `gap_rows` at the book cell reproduces both fade comps exactly; the parameterised N4 builder at (1.50, 0.80) — thr 0.8%, law + cap, voids removed — reproduces the banked N4 rows exactly (35/34).

**R14-05 — GAP-FADE family T125/S065: BANKED — ALL TEN LEGS PASS.** Family JO +₹24,355.17 / +₹7,733.66 vs the banked cell's +₹23,775.49 / +₹6,255.24 — **2025 JO → ₹1,03,937.12 (+₹579.68); 2026 JO → ₹2,54,546.87 (+₹1,478.42)** against the starting book; combined → ₹3,58,480.78. Placebos beaten (mirror ₹2,89,375.45; late ₹3,15,521.88); no flips; timing 0. Inside the family the comps trade years at full-year (GAP-FADE 2026 −₹2,786.62 vs GAP-FADE-INC 2026 +₹4,265.04) — the family was the pre-registered unit and it banks whole. The diagnostic's direction was right and its size was not: exact combined gain +₹2,058.10 against a +₹12,157.87 rough swing (Lesson 31, recorded).

**R14-06 — N4-V3 T125/S050 (the scorecard cell): REJECTED on (a) + (b) + (c) + (e).** Sleeve JO −₹13.80 / +₹11,548.34 vs the banked cell's JO +₹8,123.61 / +₹29,562.32 — reverting costs **2025 JO −₹8,137.41 / 2026 JO −₹18,013.98** on the current population. The SAT-15 rebuild is worth more on the population that exists now (0.8% threshold, one-sided cap, voids removed — all postdating it) than it was at birth: a geometry verdict expires with its population, in both directions (Lesson 46, extended). The book keeps T150/S080; the November scorecard's T125/S050 remains its own frozen instrument — the two are now measured as different systems on this population, and the scorecard is untouched. Four failing legs: not flagged.

## WS4 — P2F FAMILY (R14-07)
Anchors: entry-bar re-scoring at the book cell reproduces both comps exactly (flavour identified per comp: `replay`, both). One P2F-R2 row (WIPRO 2025-10-21, the Muhurat special session) carries the nominal 09:15 label on a day whose first bar is 13:45; it is scored from the session's opening bar — the convention its own lineage used — and the anchor reproduces its banked net (−₹59.0) exactly.

**R14-07 — P2F + P2F-R2 T150/S050: REJECTED on (a) + (b) + (e).** Jan–Oct rises in both years (2025 JO +₹627.22; 2026 JO +₹111.87) but full-year 2025 falls (P2F −₹1,033.36 / P2F-R2 +₹253.04 at full-year) and combined ex-top-3 falls. The attribution the cell was bought for is complete: **Lesson 33's two-axis 2025 bleed was the stop widening (S050→S080), not the target** — at the incumbent stop the wider target is mildly JO-positive. Attribution is not adoption: three failing legs, not flagged, and the family's exits stay closed at T125/S050 with both axes now individually measured.

## R14-08 — COMBINATIONS + STACK PRICES + FREEZE ADDENDUM
The union of Round-14 bankings (R14-04 + R14-05 — disjoint components), re-gated whole-book against the starting book: **PASS** (placebos: fade-flip + INV-side book ₹2,71,808.37; fade-late + INV-side book ₹2,97,954.80). Ending books exported to `stocks_engine_r14_book{2025,2026}_trades.csv` and independently re-summed to the paisa.

Stack prices restated on the ending book (generalised rebuild: swaps applied, banked NE-REV/REXP rows stripped by component, stack slot applied — totals reproduce the recorded prices **exactly**; adoption values now measured from the ending book):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹17,243.87 / **−₹9,753.05** | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹21,146.78 / **−₹12,839.07** | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹13,826.20 / **−₹10,121.51** | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹7,159.14 / **+₹503.58** | **passes all ten legs** |

**IDXCELL remains the only stack form that adds in both years** — and its 2026 margin is now thin (+₹503.58): the ending book keeps absorbing the stacks' value as banked geometry accrues to it (this round's INV-ABOVE target gain is inside the book, while every stack form re-prices INV-ABOVE at its own frozen T150/S080 or T125/S050 lineage).

**December freeze:** the R14-08 addendum to `stocks_engine_banked_book_FREEZE_dec2026.md` extends the freeze to the ending book (the R13-08 book with INV-ABOVE at T150/S050 and the GAP-FADE family at T125/S065 — populations, admissions and entries unchanged; exit geometry carries no admission information), and **regeneration verification PASSED** — rebuilt from the Round-13 CSVs by fresh code (INV-ABOVE re-formed by `run_chain` + law + exclusion; the fade family rebuilt by `gap_rows`), the book matches the exported Round-14 CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. The December pass/kill lines apply to the ending book as a whole.

## ENDING PER-YEAR SCORECARD (banked book — after the R14-04 + R14-05 bankings)

**2025:** JO **+₹1,05,987.24** on 1,054 Jan–Oct trades (full year +₹1,07,589.18, 1,101 rows) — **₹10,598.72/month vs the ₹15,000 floor; gap ₹44,012.76** (was ₹46,642.56). Months: Jan +3,179.19 · Feb +22,851.02 · Mar +8,836.43 · Apr +49,418.32 · May +4,409.25 · Jun +1,301.64 · Jul −2,733.21 · Aug +12,204.81 · Sep +10,671.98 · Oct −4,152.19. Ex-top-3 (full) +₹42,038.91. Red Jan–Oct months: Jul and Oct — both were already red and both deepened under the union (Jul −₹2,000.01 → −₹2,733.21; Oct −₹3,751.28 → −₹4,152.19): the geometry gains are paid from other months, and the gate's flip leg (green→red) was never engaged. The shape cost is disclosed, not hidden: the two bankings buy annual money, not month repair.

**2026:** JO **+₹2,57,300.30** on 1,352 trades — **₹25,730.03/month, floor MET**, every month green, ex-top-3 (full) +₹76,137.46.

## DECISION STATE after Round 14

- Banked book: **INV-ABOVE now wears T150/S050; the GAP-FADE family now wears T125/S065.** 2025 gap to floor: **₹44,012.76** (was ₹46,642.56).
- Round 14 banked: **2** (R14-04, R14-05). Cycles: 8 (6 gated candidates, 2 audits incl. the WS5 finalise). Voided cells: **none**; timing violations 0 on every construction.
- Flagged list: 27 entries (R14-02 F4 T175/S095 and R14-03 INV-LONG T150/S050 added — each fails (a) + (c) only, each the same year-trade at a stated price: +₹6,280.30 / −₹10,767.28 and +₹4,275.39 / −₹10,547.95 from the ending book). R14-06 fails four legs and R14-07 three; neither is flagged under the frozen rule.
- **The original sleeves' exit geometry is now measured on this book, one single-axis neighbour each:** F4's target step (year-trade, flagged), INV-LONG's target step (year-trade, flagged), INV-ABOVE's target step (banked — and it decomposes the R2-26 flag: the flip was the stop), the fade family's stop step (banked), N4's scorecard cell (refused at four legs — the rebuild's value grew), the P2F family's target step (refused; attribution completed — the bleed was the stop). With Rounds 11–13's cells, every sleeve in the book has now had its adjacent geometry scored on the current population; the geometry axis is exhausted at the adjacent cells in the same sense Round 13 recorded for the banked pair.
- The banked book (ending form) remains **frozen for December** with the pre-registered pass/kill lines (R11-07 freeze + R11-08, R12-09, R13-08 and R14-08 addenda).
- Next-round leads: none inside the tested classes. The remaining honest routes to the 2025 floor are the ones already on record — December fresh data judged against the frozen book, a genuinely new data axis (bulk/block deals, delivery percentages — not in this workspace), or Chandu-level adoption decisions (the stacks, repriced above; R2-26; R13-06; and now R14-02 and R14-03 — noting the two new flags and R13-06 are all the same trade in different sleeves: 2025 bought with 2026, at prices +₹6,280.30/−₹10,767.28, +₹4,275.39/−₹10,547.95 and +₹2,326.81/−₹5,998.05 respectively).
