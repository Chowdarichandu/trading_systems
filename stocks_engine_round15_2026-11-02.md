# Stocks (SarvaRitu) Engine — ROUND 15 · two-step geometry continuations + the VOLUME data axis
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-14 ending book): 2025 Jan–Oct **+₹1,05,987.24** (₹10,598.72/mo; gap ₹44,012.76; red Jan–Oct months Jul −₹2,733.21 / Oct −₹4,152.19) · 2026 Jan–Oct **+₹2,57,300.30** (₹25,730.03/mo; floor MET). To be re-verified by independent re-sum of `stocks_engine_r14_book{2025,2026}_trades.csv` in R15-01 before any Round-15 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): the 27 flagged entries through Round 14, incl. the max stack and its forms. Closed for good and not re-run: adjacent geometry at the first step (Round 14 exhausted it — this round tests only the two pre-registered SECOND steps in the directions that banked), the sweep family, standalone NE-REV, single-leg flag re-tests, July/October wound separators.
- **Round 15's premise:** Round 14 banked exactly two geometry steps, one per axis-family: INV-ABOVE's target step (T125→T150 at S050) and the GAP-FADE family's stop step (S050→S065 at T125). R13/R14's lesson is that a step's value is a per-sleeve measurement, never a prior — so the continuation question is empirical and is asked exactly once per banked direction, at the next single-axis rung, frozen below. The round's second half opens the one data axis the book has never had: **volume** (absent from every stored candle — the named data gap since Round 4), built under a strict causality law and gated at most twice.

---

## PRE-REGISTRATION (written before any Round-15 candidate is scored)

### R15-01 — Starting-book verification (audit)
The starting books are re-summed from `stocks_engine_r14_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹1,05,987.24 / full ₹1,07,589.18 / 1,101 rows; 2026 JO ₹2,57,300.30 / full ₹2,57,300.30 / 1,352 rows; Jul 2025 −₹2,733.21; Oct 2025 −₹4,152.19). No candidate is scored if the audit fails.

### WS1 — the two frozen second steps (each replaces its sleeve's rows whole-book; population, admission and entries unchanged)
1. **R15-02 — INV-ABOVE: T150/S050 → T175/S050** (target step only, the next grid rung in the direction R14-04 banked), population re-formed by `run_chain` at the candidate geometry under the current law (ADR ≥ 3.0, rounds ≤ 2, entry < 10:30) **with the R12-02 hard-dip exclusion re-applied to the new rows**. Rationale for the rung: INV-ABOVE's winners were genuinely truncated at T125 and the T150 step paid both years; whether they run to T175 is the one unasked question on this sleeve. No other INV-ABOVE cell this round.
2. **R15-03 — GAP-FADE + GAP-FADE-INC: T125/S065 → T125/S080** (stop step only, both comps; the next rung in the direction R14-05 banked). Rationale: the family's stop axis is where its geometry money was (R14-L5), and the increment comp used the wider stop better than the 09:20 comp — one more rung prices whether the axis still pays. No other fade cell this round.

### Anchors (asserted in code before either candidate is gated; a failed anchor stops the workstream, it is never patched silently)
- **INV-ABOVE:** the chain pop at the BOOK geometry (1.50, 0.50) under the current law plus the hard-dip exclusion reproduces the banked INV-ABOVE rows of the Round-14 book exactly (exclusion drops 22 / 15, the R14 counts); round-1 entry identity holds between the (1.50, 0.50) and (1.75, 0.50) pops.
- **GAP-FADE family:** `gap_rows` at the book cell (1.25, 0.65) reproduces both comps' banked rows exactly (multiset identity).

### Placebos (per sleeve, at the candidate geometry — the standing swap convention)
- **INV-ABOVE:** the chain's SHORT-side population at the candidate geometry under the same law (the R2-25/26 precedent).
- **GAP-FADE family:** the mirror book (follow direction on the identical gap population) and the one-bar-late book (09:20→next bar for GAP-FADE; 09:40→09:45 for GAP-FADE-INC), per the R4/R6 convention as encoded in `fade_geo`.

### Timing (asserted per construction)
Exit geometry carries no admission information: the fade swap keeps its sleeve's banked entries; the INV population re-forms causally (`run_chain` picks never read exit outcomes — round-1 entry identity across geometries is asserted). Violations are counted and must be 0.

### WS2 — VOLUME DATA AXIS, BUILD (R15-04, audit-type cycle)
Fetch daily volume for the 25 watchlist stocks + NIFTY from the Upstox v3 historical-candle daily endpoint (`days/1`), through the registered connector path (browser User-Agent header; credential only via the connector surrogate — never printed, never stored). Stored as a NEW dataset — `stocks_daily_volume.csv` (stock, date, volume) with a coverage record `stocks_daily_volume_coverage.json` — **no existing candle file is altered**. The stored span is 2024-11-15 → 2026-10-31: the pre-2025 tail exists **only** as lookback for the trailing-20-day median WS3's definition requires (a January-2025 entry's median is otherwise undefined); coverage is validated and reported per stock-**year** for 2025 and 2026 as tasked. Validation per stock-year: expected trading days = the days in the engine machinery's own daily series for that stock-year; every expected day missing a volume row is named as a hole; zero-volume days are counted and named separately (a returned zero is data, never replaced); **no missing value is ever estimated**. NIFTY is an index (no traded volume of its own) — its returned series is stored and reported as returned.

### WS3 — FIRST VOLUME GATES (R15-05 diagnostic; R15-06 / R15-07 gates — at most two)
**The causality law (part of the timing audit, asserted in code):** a day's volume is knowable only AFTER that day closes. It may condition NEXT-day (or later) decisions only; **no same-day intraday decision may use same-day daily volume.** Every volume input to every Round-15 volume candidate is dated strictly before the entry date, asserted row by row; violations void the cell on sight.

**Frozen feature:** for a book row (stock S, entry date D): let P = the last trading day strictly before D in S's volume series; **rvol = volume(P) ÷ median(volume over the 20 trading days ending on P, inclusive)**. A row with fewer than 20 prior volume days before P, or with P missing from the series, is **unclassifiable**: it is excluded from every conditioned set (real and placebos alike) and counted by name — never estimated.

**Frozen condition form:** keep the sleeve's rows with **rvol ≥ 1.0** (prior-day volume at or above its trailing median); drop the rest. The band is frozen here, before any volume number is looked at.

**Sleeve choice by frozen diagnostic (R15-05, subset arithmetic on banked nets only — it chooses which cells earn an exact gate, it scores nothing):** the candidate sleeves are the three with flip + late placebo machinery at book geometry — **F4, N4-V3, P2F family**. For each, compute the combined (2025 + 2026) Jan–Oct delta of swapping in only its rvol ≥ 1.0 rows. **Gate 1** = the sleeve with the largest strictly-positive combined delta, gated whole-book with its conditioned flip and late books as placebos. **Gate 2** = the sleeve with the second-largest strictly-positive combined delta, same form — run only if Gate 1 was run and a second positive exists. If no sleeve shows a positive combined delta, WS3 closes with no gate, recorded. At most two gates; no other volume form this round (no second band, no second threshold, no cross-sleeve combination).

### WS4 — Combinations + stack maintenance + December freeze addendum (R15-08)
Candidates are each gated against the **starting** book. Resolution (the standing rule): swaps/filters on disjoint components compose; if more than one banking passes, the union is re-gated whole-book against the starting book — if the union passes it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded. The four stack prices are restated on the ending book by the R12-09 generalised method (totals must reproduce the recorded prices exactly). **December freeze addendum:** the freeze document is extended to the new ending book, and the extension is **regeneration-verified** — the ending book rebuilt from the Round-14 CSVs plus the banked Round-15 constructions by fresh code must match the exported ending CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. Ending books exported to `stocks_engine_r15_book{2025,2026}_trades.csv` and independently re-summed. If nothing passes, R15-08 closes by statement (stack prices and the freeze addendum are still restated/extended on the unchanged book). Rejected candidates failing at most two legs join the flagged list as owner decisions, with adoption values measured from the ending book.

### Verdict rule (frozen for all Round-15 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS4 resolution). A candidate failing any leg is recorded with its failing legs named; the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R15-01 — STARTING-BOOK VERIFICATION (audit, passed)
Books re-summed from the Round-14 CSVs: 2025 JO ₹1,05,987.24 / full ₹1,07,589.18 / 1,101 rows; 2026 JO ₹2,57,300.30 / full ₹2,57,300.30 / 1,352 rows — exact vs the Round-14 record; Jul 2025 −₹2,733.21 and Oct 2025 −₹4,152.19 asserted. No scoring preceded this audit.

## WS1 — THE TWO SECOND STEPS (R15-02, R15-03)
Anchors: three-way, all exact — the chain pop at the book geometry (1.50, 0.50) under the law + hard-dip exclusion reproduces the banked INV-ABOVE rows (exclusion drops 22 / 15, the R14 counts); round-1 entry identity holds between the T150 and T175 pops; `gap_rows` at the book cell (1.25, 0.65) reproduces both fade comps exactly.

**R15-02 — INV-ABOVE T175/S050: REJECTED on (c) only.** Sleeve standalone ₹15,367.09 / ₹8,916.53 at the candidate cell — **2025 JO → ₹1,06,079.81 (+₹92.57); 2026 JO → ₹2,56,102.01 (−₹1,198.29)**. Combined full-year total RISES (₹3,64,889.48 → ₹3,65,891.14) on Nov/Dec-2025 strength, placebos beaten (SHORT-side swap book below the variant), no flips, ex-top-3 rises in both years, timing 0. The second target step is the year-trade signature again, at a far smaller price than the first step's mirror images: T150 captured nearly all of what this population's winners had to give, and T175 mostly re-prices the two years against each other. **Flagged as an owner decision** (one failing leg): adoption from the ending book → 2025 JO +₹92.57 / 2026 JO −₹1,198.29.

**R15-03 — GAP-FADE family T125/S080: REJECTED on (a) + (b) + (c) + (e).** Family standalone at the candidate cell: GAP-FADE ₹22,154.57 / **−₹3,012.95**; GAP-FADE-INC **−₹347.54** / ₹5,955.71 — **2025 JO → ₹1,03,439.10 (−₹2,548.14); 2026 JO → ₹2,52,509.40 (−₹4,790.90)**; combined falls to ₹3,57,550.44; placebos beaten; no flips; timing 0. The stop axis that paid at S065 (+₹2,058.10 exact in Round 14) reverses at S080: at the wider stop the 09:20 comp's 2026 book goes negative outright and the increment's 2025 book follows it. The family's geometry is a peak at S065, not a slope. Four failing legs: not flagged.

## WS2 — VOLUME DATA AXIS, BUILD (R15-04, audit)
Fetched via the registered connector path (v3 `days/1`, browser User-Agent header; credential only through the connector surrogate). Stored as the NEW dataset [stocks_daily_volume.csv](sandbox://workspace/trading/stocks_daily_volume.csv) — **12,584 rows** (26 series × 484 days, 2024-11-15 → 2026-10-31; the pre-2025 tail is lookback only, for the trailing-20-day median). **No existing candle file was altered.** Coverage record: [stocks_daily_volume_coverage.json](sandbox://workspace/trading/stocks_daily_volume_coverage.json). Fetch errors: none.

### Volume coverage table (expected = the machinery's own daily days for that stock-year)
| Series | 2025 expected | 2025 holes | 2025 zero-vol | 2026 expected | 2026 holes | 2026 zero-vol |
|---|---|---|---|---|---|---|
| Each of the 25 watchlist stocks (ASTRAL, BDL, GLENMARK, GODREJCP, HDFCBANK, HINDALCO, HINDCOPPER, HINDUNILVR, HINDZINC, INDUSTOWER, IRCTC, ITC, KALYANKJIL, NATIONALUM, NHPC, NTPC, OBEROIRLTY, OIL, PFC, RECLTD, TATASTEEL, TVSMOTOR, UNITDSPR, VEDL, WIPRO) | 249 | **0** | 0 | 203 | **0** | 0 |
| NIFTY (index) | 249 | 0 | **249 — volume 0 on every day, as returned** | 203 | 0 | **203 — as returned** |

Every stock-year is complete: **no hole exists to name** — the per-day hole lists in the coverage JSON are empty for all 52 stock-years, and no value anywhere was estimated. Two further facts, named: (1) the 2026 volume series carries 2026-10-29 and 2026-10-30, two days beyond the machinery's stored daily span (present in the API series — the book's forward-root rows on those days are covered); (2) NIFTY's volume is 0 on every returned day — an index has no traded volume of its own; the series is stored exactly as returned and is used by no gate.

## WS3 — FIRST VOLUME GATES (R15-05 diagnostic; R15-06 / R15-07 not run)
The causality law was asserted row by row in code (prior trading day P < entry date; the 20-day window ends on P). **Unclassifiable rows: 0 in every sleeve** — coverage is complete for every gated population. The frozen diagnostic (subset arithmetic on banked nets; keep rvol ≥ 1.0):

| Sleeve | Kept rows (25/26) | Dropped rvol<1 (25/26) | 2025 JO delta | 2026 JO delta | Combined |
|---|---|---|---|---|---|
| F4 | 112 / 190 | 134 / 165 | +₹1,972.94 | **−₹49,328.51** | **−₹47,355.57** |
| N4-V3 | 18 / 21 | 17 / 13 | −₹4,186.34 | −₹5,199.24 | −₹9,385.58 |
| P2F family | 43 / 54 | 4 / 9 | −₹106.05 | −₹2,897.65 | −₹3,003.70 |

**No sleeve shows a strictly-positive combined delta, so under the frozen rule NO volume gate was run** (R15-06 and R15-07 close as audits, recorded in `r15_results.json`). The frozen form's verdict at diagnostic strength: on this book, entries preceded by an above-median-volume day are the *worse* half in 2026 for all three sleeves — catastrophically so for F4, whose 2026 winners sit disproportionately behind quiet prior days. The complementary form (keep rvol < 1.0) was **not** pre-registered and was **not** run; it is recorded here as an untested observation for a future round's pre-registration, nothing more (Lesson: a diagnostic's mirror image is a new candidate, not a result).

## R15-08 — COMBINATIONS + STACK PRICES + FREEZE ADDENDUM
Nothing banked in Round 15, so there is no union to re-gate: **the ending book is the starting (Round-14) book, unchanged.** Ending books exported to `stocks_engine_r15_book{2025,2026}_trades.csv`, independently re-summed, and **regeneration verification PASSED** — a fresh load of the Round-14 CSVs matches the exported Round-15 CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years (no Round-15 construction is banked, so the rebuild is the audited starting book itself).

Stack prices restated on the ending book (generalised rebuild — totals reproduce the recorded prices **exactly**; adoption values are unchanged from Round 14 because the book is unchanged):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹17,243.87 / **−₹9,753.05** | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹21,146.78 / **−₹12,839.07** | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹13,826.20 / **−₹10,121.51** | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹7,159.14 / **+₹503.58** | **passes all ten legs** |

**December freeze:** the R15-08 addendum to `stocks_engine_banked_book_FREEZE_dec2026.md` records that the frozen book is **unchanged** by Round 15 — neither second-step geometry cell and no volume form enters it — and that regeneration verification passed. The December pass/kill lines apply to the book as a whole, unchanged.

## ENDING PER-YEAR SCORECARD (banked book — unchanged by Round 15)

**2025:** JO **+₹1,05,987.24** on 1,054 Jan–Oct trades (full year +₹1,07,589.18, 1,101 rows) — **₹10,598.72/month vs the ₹15,000 floor; gap ₹44,012.76** (unchanged). Months: Jan +3,179.19 · Feb +22,851.02 · Mar +8,836.43 · Apr +49,418.32 · May +4,409.25 · Jun +1,301.64 · Jul −2,733.21 · Aug +12,204.81 · Sep +10,671.98 · Oct −4,152.19. Ex-top-3 (full) +₹42,038.91. Red Jan–Oct months: Jul and Oct.

**2026:** JO **+₹2,57,300.30** on 1,352 trades — **₹25,730.03/month, floor MET**, every month green, ex-top-3 (full) +₹76,137.46.

## DECISION STATE after Round 15

- Banked book: **unchanged** — INV-ABOVE at T150/S050, the GAP-FADE family at T125/S065. 2025 gap to floor: **₹44,012.76**.
- Round 15 banked: **0**. Cycles: 8 (2 gated candidates, 5 audits incl. the build, the diagnostic, the two not-run gates and the WS4 finalise, plus the R15-01 verification). Voided cells: **none**; timing violations 0 on every construction; unclassifiable volume rows 0.
- Flagged list: 28 entries (R15-02 added — INV-ABOVE T175/S050, fails (c) only: +₹92.57 / −₹1,198.29 from the ending book). R15-03 fails four legs and is not flagged under the frozen rule.
- **Geometry is now closed at two steps as it was at one:** both directions that banked in Round 14 were continued exactly one rung — the target axis re-prices the years against each other (INV-ABOVE T175), the stop axis reverses outright past its peak (fade S080). No third step is licensed by anything measured.
- **The volume axis exists and its first frozen form is dead at diagnostic strength** on all three sleeves with placebo machinery; the axis itself is now a stored, complete, causality-lawed dataset (`stocks_daily_volume.csv`) available to future pre-registrations — the mirror form (quiet prior day) is the one untested observation this round leaves behind, alongside the standing routes on record: December fresh data against the frozen book, other new data axes not in this workspace (bulk/block deals, delivery percentages), and Chandu-level adoption decisions (the stacks, repriced above; R2-26; R13-06; R14-02; R14-03; R15-02).
