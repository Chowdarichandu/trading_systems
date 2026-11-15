# Stocks (SarvaRitu) Engine — ROUND 16 · the volume MIRROR (quiet-prior-day entries)
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting (banked) book** (Round-15 ending book, unchanged from Round 14): 2025 Jan–Oct **+₹1,05,987.24** (₹10,598.72/mo; gap ₹44,012.76; red Jan–Oct months Jul −₹2,733.21 / Oct −₹4,152.19) · 2026 Jan–Oct **+₹2,57,300.30** (₹25,730.03/mo; floor MET). To be re-verified by independent re-sum of `stocks_engine_r15_book{2025,2026}_trades.csv` in R16-01 before any Round-16 scoring.
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code — a cell whose entry uses information not knowable strictly before the entry bar is void on sight. **No month-named or year-named rules anywhere in this round.**
- **Flagged, NOT adopted** (Chandu's calls; the book stays without them): the 28 flagged entries through Round 15, incl. the max stack and its forms. Closed for good and not re-run: adjacent geometry at one and two steps, the sweep family, standalone NE-REV, single-leg flag re-tests, July/October wound separators, and the rvol ≥ 1.0 volume restrictions (diagnostic-negative in Round 15).
- **Round 16's premise:** Round 15 built the volume axis (daily volume, complete coverage, strict causality law) and its first frozen form — keep entries whose prior day traded at or above its trailing-20-day median volume — was **diagnostic-negative on all three placebo-equipped sleeves**: F4 combined −₹47,355.57 (2026 alone −₹49,328.51 — F4's 2026 winners were built on quiet-prior-day entries), N4-V3 −₹9,385.58, P2F family −₹3,003.70. Lesson R15-L3 is explicit: the diagnostic's mirror image is a new candidate, not a result. This round pre-registers and gates exactly that mirror — nothing else. No second band, no second threshold, no cross-sleeve volume combination is licensed by anything measured.

---

## PRE-REGISTRATION (written before any Round-16 candidate is scored)

### The frozen feature and the mirror condition (identical definitions to Round 15)
For a book row (stock S, entry date D), from `stocks_daily_volume.csv`: let P = the last trading day strictly before D in S's volume series; **rvol = volume(P) ÷ median(volume over the 20 trading days ending on P, inclusive)**. A row with fewer than 20 prior volume days before P, or with P missing from the series, or with a non-positive median, is **unclassifiable**: it is excluded from every conditioned set (real and placebos alike) and counted by name — never estimated. (Round 15 measured 0 unclassifiable rows in every sleeve; the count is re-asserted here.)

**Mirror condition (the only volume form this round): keep the sleeve's rows with rvol < 1.0** — entries preceded by a quieter-than-median prior day. The boundary belongs to the other side exactly as Round 15 defined it (rvol == 1.0 was in the ≥ 1.0 kept set), so the mirror and the Round-15 form partition the classifiable rows.

**The causality law (part of the timing audit, asserted in code, unchanged from Round 15):** a day's volume is knowable only AFTER that day closes. It may condition NEXT-day (or later) decisions only; **no same-day intraday decision may use same-day daily volume.** Every volume input is dated strictly before the entry date (P < D, and the 20-day window ends on P), asserted row by row; violations void the cell on sight. The feature is therefore knowable before the entry session opens.

### R16-01 — Starting-book verification (audit)
The starting books are re-summed from `stocks_engine_r15_book{2025,2026}_trades.csv` and asserted against the recorded totals (2025 JO ₹1,05,987.24 / full ₹1,07,589.18 / 1,101 rows; 2026 JO ₹2,57,300.30 / full ₹2,57,300.30 / 1,352 rows; Jul 2025 −₹2,733.21; Oct 2025 −₹4,152.19). No candidate is scored if the audit fails.

### Sleeve anchors (asserted in code before either gate; a failed anchor stops the workstream, it is never patched silently)
The sleeve populations are the banked ones, rebuilt by the Round-14 builders exactly as in Round 15 WS3, and each builder's real set must reproduce the banked comp rows exactly (multiset identity on date/stock/dir/entry_time/net) before any conditioning is applied:
- **F4:** `rescore` of the banked F4 rows at the book geometry T150/S095, flavour "plain".
- **N4-V3:** the `n4_geo` builder at the book geometry T150/S080 (0.8% threshold, full law + FLOOR-2 cap, R6-11 voided signals excluded in every set).
- **P2F family:** `rescore` of the banked P2F and P2F-R2 rows at T125/S050, open-entry convention, flavour "plain" or "v2" — whichever anchors, as in Round 15.

### Placebos (per gate — the standing conditioned-population convention from Round 15)
For each gated sleeve: the **mirror-conditioned flip book** (opposite direction on the identical entry bars, same rvol < 1.0 condition) and the **mirror-conditioned late book** (same direction, one bar later, same condition), each swapped in whole-book. rvol depends only on (stock, entry date), so a row and its flip/late counterparts always share one classification. The gate's placebo leg compares the variant's combined full-year total against both placebo books' combined full-year totals.

### WS1 — R16-02: F4 MIRROR
Restrict the banked F4 sleeve to its rows with prior-day rvol < 1.0 (population, admission, entries and exits otherwise unchanged — the restriction only removes rows). Gate whole-book against the starting book.

### WS2 — R16-03: N4-V3 MIRROR
The same restriction form on the banked N4-V3 sleeve. Gate whole-book against the starting book.

### WS3 — R16-04: P2F MIRROR (CONDITIONAL — the condition is frozen here, before any scoring)
The P2F-family mirror gate runs **if and only if** at least one of R16-02 / R16-03 either (i) **banks** (all ten legs pass), or (ii) is rejected failing **exactly one** of the ten bool legs (a)–(i) + (x) — a near-miss on a single leg. If neither WS1 nor WS2 banks or single-leg-near-misses, R16-04 **closes by statement** as an audit record and no P2F mirror number is computed. Rationale, frozen in advance: the P2F family's Round-15 diagnostic was the smallest of the three (−₹3,003.70 combined, on only 4 / 9 dropped rows per year — the thinnest population of the three), so its mirror earns a gate only on evidence that the mirror form itself carries signal on this book.

### WS4 — Combinations + stack maintenance + December freeze addendum (R16-05, R16-06)
Candidates are each gated against the **starting** book. Resolution (the standing rule): restrictions on disjoint components compose; if more than one banking passes, the union (all banked sleeves' mirror-conditioned rows swapped in together) is re-gated whole-book against the starting book, with union placebos built the same way (all banked sleeves' conditioned flip sets swapped in together; likewise the conditioned late sets) — if the union passes it is the ending book; if the union fails while a single candidate passed, the single passing candidate with the highest combined total is the ending book and the union's failure is recorded. If exactly one candidate banks, it is the ending book; if none banks, the ending book is the starting book and WS4 closes by statement. The four stack prices are restated on the ending book by the R12-09 generalised method (on an unchanged book the totals must reproduce the recorded prices exactly). **December freeze addendum:** the freeze document is extended to the ending book, and the extension is **regeneration-verified** — the ending book rebuilt from the Round-15 CSVs plus the banked Round-16 constructions re-derived by fresh code (builders + volume conditioning recomputed from `stocks_daily_volume.csv`) must match the exported ending CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years. If a mirror banks, the addendum records that the frozen book gains a prior-day-volume admission feature for that sleeve (rvol < 1.0; P and its window end strictly before the entry date — knowable before the session opens), superseding the freeze's "no volume features" basis line for that sleeve only; the December pass/kill lines apply to the book as a whole, unchanged. Ending books exported to `stocks_engine_r16_book{2025,2026}_trades.csv` and independently re-summed. Rejected candidates failing at most two legs join the flagged list as owner decisions, with adoption values measured from the ending book.

### Verdict rule (frozen for all Round-16 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (subject to the WS4 resolution). A candidate failing any leg is recorded with its failing legs named; the engine adopts nothing on Chandu's behalf.

### Frontier clause (frozen)
If nothing banks and every mirror run is refused on named legs, this report will state plainly — as a finding, with the cycle count — that the in-sample programme has reached the same frontier as the other segments: what remains is December fresh data against the frozen book, November forward evidence, and the owner's adoption decisions. That statement, if it comes, is a measurement about the in-sample window, not a recommendation to stop the standing order.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R16-01 — STARTING-BOOK VERIFICATION (audit, passed)
Books re-summed from the Round-15 CSVs: 2025 JO ₹1,05,987.24 / full ₹1,07,589.18 / 1,101 rows; 2026 JO ₹2,57,300.30 / full ₹2,57,300.30 / 1,352 rows — exact vs the Round-15 record; Jul 2025 −₹2,733.21 and Oct 2025 −₹4,152.19 asserted. No scoring preceded this audit. Sleeve anchors all exact (F4 rescore at T150/S095 "plain", N4 builder at T150/S080, P2F and P2F-R2 rescores at T125/S050 each reproduce the banked comp rows before any conditioning). Unclassifiable volume rows: **0 in every sleeve** — coverage is complete for every gated population, exactly as in Round 15, and the mirror's kept / dropped counts reproduce Round 15's diagnostic low / kept counts to the row (asserted in R16-05): the two forms partition the classifiable rows.

## WS1 — R16-02: F4 MIRROR — REJECTED on (a) + (b) + (c) + (e) + (f)
Keep F4 rows with prior-day rvol < 1.0 (kept **134 / 165** of the sleeve's 246 / 355 rows; dropped rvol ≥ 1.0: 112 / 190). **2025 JO → ₹1,03,923.16 (−₹2,064.08); 2026 JO → ₹2,03,572.88 (−₹53,727.42)**; combined full-year ₹3,64,889.48 → **₹3,09,097.98**. Placebos beaten on the same conditioned population (flip book ₹2,15,958.51; late book ₹2,95,094.67 — leg (h) passes), cells stay positive, halves hold, timing violations 0, leg (x) holds (2026 JO ₹2,03,572.88 ≥ ₹1,50,000). What kills it: both years fall, combined ex-top-3 falls (₹1,18,176.37 → ₹96,900.58), and **March 2026 flips** (+₹11,344.23 → −₹673.18). Five failing legs: **not flagged**.

The mirror's exact price completes Round 15's diagnostic picture. Deleting F4's quiet-prior-day rows (the ≥ 1.0 form) cost 2026 −₹49,328.51 at diagnostic strength; deleting its loud-prior-day rows (this mirror) costs 2026 **−₹53,727.42** at the exact gate. **F4's 2026 value lives in both volume halves** — the unrestricted population is the system, and prior-day relative volume at this band does not separate its winners from its losers in either direction.

## WS2 — R16-03: N4-V3 MIRROR — REJECTED on (a) + (b) + (c) + (e)
Keep N4-V3 rows with prior-day rvol < 1.0 (kept **17 / 13** of 35 / 34 rows; dropped rvol ≥ 1.0: 18 / 21). **2025 JO → ₹1,02,049.97 (−₹3,937.27); 2026 JO → ₹2,32,937.22 (−₹24,363.08)**; combined → **₹3,38,225.04**. Placebos beaten (flip ₹3,17,077.28; late ₹3,35,825.08), no month flips, no half flips, cells positive, timing 0, leg (x) holds. Both years fall and combined ex-top-3 falls (→ ₹1,02,918.83 from ₹1,18,176.37), so the same four legs refuse it. Four failing legs: **not flagged**. N4-V3's small population, like F4's large one, earns across both volume halves; the restriction only amputates.

## WS3 — R16-04: P2F MIRROR — NOT RUN (frozen condition unmet, closed by statement)
The condition frozen in the pre-registration required a banking or an exactly-one-leg failure in WS1 or WS2. The F4 mirror failed five legs and the N4-V3 mirror four — neither banked, neither near-missed. Per the frozen rule the P2F-family mirror gate **does not run and no P2F mirror number is computed**. The condition did the work it was designed for: after both larger sleeves refused the form outright, the thinnest population (the P2F family's mirror would keep only 4 / 9 of its 47 / 63 rows — its Round-15 diagnostic was −₹3,003.70) was not shopped for a friendlier verdict.

## WS4 — R16-05 / R16-06: COMBINATIONS + STACK PRICES + FREEZE ADDENDUM
Nothing banked in Round 16, so there is no union to re-gate: **the ending book is the starting (Round-15) book, unchanged.** Ending books exported to `stocks_engine_r16_book{2025,2026}_trades.csv`, independently re-summed, and **regeneration verification PASSED** — a fresh load of the Round-15 CSVs matches the exported Round-16 CSVs row-for-row (multiset identity on comp/date/stock/dir/entry_time/net) and to the paisa in both years (no Round-16 construction is banked, so the rebuild is the audited starting book itself).

Stack prices restated on the ending book (generalised rebuild — totals reproduce the recorded prices **exactly**; adoption values are unchanged from Round 15 because the book is unchanged):

| Stack form | 2025 JO | 2026 JO | Adoption value from ending book (2025 / 2026) | Gate state |
|---|---|---|---|---|
| Unconditioned (R8-02) | ₹1,23,231.11 | ₹2,47,547.25 | +₹17,243.87 / **−₹9,753.05** | fails (f) |
| Variant A — NOTCH slot (R9-02) | ₹1,27,134.02 | ₹2,44,461.23 | +₹21,146.78 / **−₹12,839.07** | fails (f), Dec only |
| Variant C — NU slot (R9-04) | ₹1,19,813.44 | ₹2,47,178.79 | +₹13,826.20 / **−₹10,121.51** | **passes all ten legs** |
| IDXCELL slot (R9-08) | ₹1,13,146.38 | ₹2,57,803.88 | +₹7,159.14 / **+₹503.58** | **passes all ten legs** |

**December freeze:** the R16-06 addendum to `stocks_engine_banked_book_FREEZE_dec2026.md` records that the frozen book is **unchanged** by Round 16 — no volume-conditioned form in either direction enters it — and that regeneration verification passed. The December pass/kill lines apply to the book as a whole, unchanged.

## ENDING PER-YEAR SCORECARD (banked book — unchanged by Round 16)

**2025:** JO **+₹1,05,987.24** on 1,054 Jan–Oct trades (full year +₹1,07,589.18, 1,101 rows) — **₹10,598.72/month vs the ₹15,000 floor; gap ₹44,012.76** (unchanged). Months: Jan +3,179.19 · Feb +22,851.02 · Mar +8,836.43 · Apr +49,418.32 · May +4,409.25 · Jun +1,301.64 · Jul −2,733.21 · Aug +12,204.81 · Sep +10,671.98 · Oct −4,152.19. Ex-top-3 (full) +₹42,038.91. Red Jan–Oct months: Jul and Oct.

**2026:** JO **+₹2,57,300.30** on 1,352 trades — **₹25,730.03/month, floor MET**, every month green, ex-top-3 (full) +₹76,137.46.

## DECISION STATE after Round 16

- Banked book: **unchanged** — INV-ABOVE at T150/S050, the GAP-FADE family at T125/S065, no volume feature anywhere. 2025 gap to floor: **₹44,012.76**.
- Round 16 banked: **0**. Cycles: 6 (2 gated candidates, 4 audits incl. the not-run WS3 gate and the WS4 finalise pair). Voided cells: **none**; timing violations 0 on every construction; unclassifiable volume rows 0.
- Flagged list: **28 entries, unchanged** — both mirror rejections fail more than two legs and are not flagged under the standing rule.
- **The volume axis is now closed in both directions at the frozen band.** Round 15's form (rvol ≥ 1.0) died at the diagnostic on all three sleeves; Round 16's mirror (rvol < 1.0) was gated exactly on the two largest sleeves and refused on five legs (F4) and four legs (N4-V3) — and on F4 the mirror costs 2026 *more* (−₹53,727.42) than the diagnostic said the loud half was worth (−₹49,328.51). Prior-day relative volume, at the trailing-20-median band, does not separate this book's winners from its losers. No second band or threshold is licensed by anything measured, and none will be fitted.
- **Frontier finding (per the frozen clause):** with the mirror refused, the in-sample programme has reached the same frontier as the other segments. Sixteen rounds and 105 recorded engine cycles have now measured, on this window: every sleeve's exit geometry at one and two steps, the deletion registry to exhaustion, the stack ingredients and their conditioned forms, the sweep transplant in both directions, wound separators under the combined-years test, and the volume axis in both directions. What remains is what remains for Bank and Nifty: **December fresh data against the frozen book (pass/kill pre-registered), November forward evidence, and Chandu's adoption decisions** (the stacks, repriced above; R2-26; R13-06; R14-02; R14-03; R15-02). This is a finding about the Jan–Oct in-sample window, recorded as tasked — not a recommendation; the standing order is Chandu's to change.
