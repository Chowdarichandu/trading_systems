# Stocks (SarvaRitu) Engine — ROUND 6 · Triple-Combination Pricing, NE-REV Repairs, Increment Conditioning, Range-Expansion Follow
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting book** (Round-4/5 ending book, re-verified by independent re-sum of the exported CSVs): 2025 Jan–Oct **+₹77,806.57** (₹7,780.66/mo; gap ₹72,193.43) · 2026 Jan–Oct **+₹2,23,293.34** (₹22,329.33/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing violations are derived from each construction and asserted in code (lessons R4-L2, Nifty-46) — a cell whose entry uses its own signal print is void on sight.
- **Flagged, NOT adopted** (Chandu's calls, baselines stay on the book without them): R2-26 (clean sheet on the current book), R5-03 (fails leg (e) only), R5-07 (fails legs (e) and (f)).

---

## PRE-REGISTRATION (written before any Round-6 scoring)

### WS0 — Triple combination, DECISION SUPPORT ONLY (R6-01)
Ingredients, each re-anchored on the starting book to its recorded delta before combining:
- **R2-26:** swap the book's INV-ABOVE rows for the cached T150/S080 INV-ABOVE population (`inv_above_rows` on `r2_cache.pkl`, the exact Round-2 construction). Recorded on this base (R4-10): 2025 JO → ₹85,340.57, 2026 JO → ₹2,27,415.67.
- **R5-03:** swap the book's GAP-FADE rows for the ≥1.25% DOWN+FLAT sleeve (09:20, T125/S050, the exact R5-03 construction). Recorded: 2025 JO → ₹88,401.23, 2026 JO → ₹2,26,071.55.
- **R5-07:** add the NE-REV LONG rows (the exact R5-07 construction). Recorded: 2025 JO → ₹90,121.11, 2026 JO → ₹2,47,599.90.
Placebos (combined full-year totals, frozen): **P1** all-placebo — SHORT-side T150 INV-ABOVE swap + gap mirror (follow-SHORT ≥1.25%, DOWN+FLAT) in the GAP-FADE slot + NE-REV opposite direction (SHORT); **P2** real R2-26 + real R5-03 sleeve + NE-REV one bar late (10:40); **P3** real R2-26 + gap sleeve one bar late (09:25) + real NE-REV. Recorded with `force_no_bank` regardless of verdict — adoption is Chandu's.

### WS1 — NE-REV repairs (R6-02…R6-05; R6-06 = the (d) audit)
Population is R5-07's frozen non-event population (stock-days outside every {R, R+1, R+2} results-reaction window, both calendars pooled; weekend bars excluded; at most one trade per stock-day). Signal: close of the 10:25 bar vs prior daily close; the 10:25 bar completes at 10:30. Exits T100/S065 via `replay_plain` (entry bar checked), square-off 15:10, ₹40/trade.
- **(a) R6-02 / R6-03:** LONG on move ≤ −2.25% / ≤ −2.50%, entry at the open of the 10:35 bar (the 10:30 bar skipped, as frozen in R5).
- **(b) R6-04:** LONG on move ≤ −2.00%, entry 10:35, restricted to stock-days whose frozen regime label (REGIME-CLASSIFIER-1, prior-day data only) is DOWN or FLAT.
- **(c) R6-05:** LONG on move ≤ −2.00%, entry at the open of the **11:05** bar; signal unchanged (10:25 close).
- **(d) R6-06 (audit, not a candidate):** carrier exclusion (drop the sleeve's rows in the book's top-3 earner names as ranked on the **prior year's** book) is applied **only if** a causal prior-year book ranking exists for both judging years. Ranking 2026 rows on the completed 2025 book is causal; ranking 2025 rows would require a 2024 SarvaRitu book, which does not exist in this workspace (the machinery's calendars and populations cover 2025 and Jan–Oct 2026 only; ranking 2025 on the 2026 book would be look-ahead and is refused). If the both-years condition fails, (d) is skipped and the skip is recorded — no substitute ranking is invented.
Placebos per cell (whole books, identical population/cells): opposite direction on the same stock-days and entry bar; same direction one bar later (10:40 for the 10:35 cells; 11:10 for R6-05). Timing audit: violations = rows whose entry bar is not strictly after the 10:25 signal bar — counted in code, asserted 0. A repair passing ALL legs (nine + (x)) banks as the NE-REV-LONG component.

### WS2 — R5-03 increment conditioning (R6-07, R6-08)
The ≥1.25% sleeve (DOWN+FLAT, 09:20, T125/S050) decomposes exactly into the banked ≥1.5% sleeve plus the **[1.25%, 1.5%) increment** (identical construction; the row-set difference, verified by (date, stock) keys and standalone sums before scoring). Only the increment is conditioned; the banked sleeve is never touched. The increment is added as its own component (GAP-FADE-INC).
- **R6-07:** increment restricted to DOWN-cell days only, entry bar 1 (09:20 open).
- **R6-08:** increment on DOWN+FLAT days, entry at the open of the first bar strictly after 09:35 — the **09:40** bar, selected by time lookup (not position); rows whose 09:40 bar is absent are dropped and counted.
Placebos per cell (whole books): the mirror increment (follow-SHORT on the identical band/cell population at the same entry bar) and the same increment one bar later. Timing: the gap signal is complete at bar 0's open print; every entry is at bar ≥ 1 — violations counted in code, asserted 0.

### WS3 — Range-expansion follow (R6-09 LONG, R6-10 SHORT) — NEW MECHANISM
- **First hour:** the bars starting 09:15 through 10:10 (the 10:10 bar covers 10:10–10:15). First-hour range = max(high) − min(low) over those bars; first-hour close = close of the 10:10 bar. A stock-day qualifies for measurement only if all 12 first-hour bars are present.
- **Volatility state:** ratio = today's first-hour range ÷ the median first-hour range of the **previous 20 data-bearing trading days** of the same stock (strictly prior days; ≥20 required). Signal requires ratio ≥ 2.0.
- **Direction:** close position pos = (first-hour close − hour low) ÷ (hour high − hour low). pos ≥ 0.75 → LONG candidate; pos ≤ 0.25 → SHORT candidate. The hour completes at 10:15; every input is known at 10:15.
- **Entry / exits:** entry at the **open of the 10:20 bar** (the 10:15 bar is skipped entirely). Exits **T125/S050** via `replay_plain` (entry bar checked), square-off 15:10. ₹40/trade, per 100 shares. At most one trade per stock-day. Weekend bars excluded. **No price levels of any kind (no PDH/PDL, no opening-range levels) are used anywhere in this construction** — it is a volatility-state entry, not a level break; the closed ORB family is not reopened.
- **Controls (frozen):** placebos per direction as whole books on the identical population: (i) the opposite direction at the same entry bar; (ii) the same direction one bar later (10:25 open). Timing audit: violations = rows whose entry bar index is not strictly after the 10:10 signal bar's index — counted in code, asserted 0.
- **Verdict rule (frozen):** each direction is a separate candidate, gated whole-book per year under the nine-leg gate + leg (x).

*(End of pre-registration. All sections below are written after scoring.)*

---

## ⚠️ ADMISSION-CAUSALITY AUDIT (R6-11) — 4 N4-V3 rows VOIDED, book re-baselined; every other component certified clean

Run on the Nifty Round-5 WS0 model: every admission condition of every component must be fully knowable at its recorded entry bar. **1,860 rows checked mechanically** (every input recomputed from stored data) plus code-level certification of the chain machinery. Full record: `r6_results.json` (R6-11) and `r6_causality_audit.json`.

**The violation — N4-V3's event-day tag on same-day intraday announcements.** N4's morning-move signal is causal; what fails is the day's *membership in the reaction set* when the admitting event was announced intraday on the reaction day itself, after the 09:35 entry:

| Row | Net | Evidence |
|---|---|---|
| BDL 2025-01-16 LONG | +₹1,691.75 | **PROVEN.** The calendar's own detail records the exchange filing at **13:49** on the reaction day; the trade entered 09:35 |
| HINDZINC 2026-07-24 | −₹460.80 | Uncertifiable: same-day results the calendar marks declared **during market hours** (`after_market = no`), no pre-09:35 evidence |
| HINDUNILVR 2026-10-28 SHORT | −₹1,482.24 | Uncertifiable: same construction |
| VEDL 2026-10-28 LONG | +₹303.20 | Uncertifiable: same construction |

All 4 **voided and the book re-baselined in the same run**: 2025 Jan–Oct ₹80,111.79 → **₹78,420.04**; 2026 Jan–Oct ₹2,28,056.37 → **₹2,29,696.21**. Voided combined net **+₹51.91** — the book was not carried by them. Every Round-6 candidate delta sits on components disjoint from N4-V3, so **all Round-6 verdicts stand**; only the baseline moved.

**Certified clean (per component):**
- **Regime gates** — `below50` / `cond_inv1` / `g1` and the FL regime labels are functions of prior closes only; every F4 / INV-LONG / INV-ABOVE / INV-R3 row's date gate was recomputed from NIFTY daily data and matches.
- **F4** — premove uses bars strictly before 10:00 against the 09:30 bar's open; band [0.5%, 1.0%) and follow-direction recomputed for all 601 rows (Oct 29/30 rows recomputed from the forward data root, the machinery's own second root); every entry ≥ 10:05, strictly after the measurement completes. The build machinery's own `_AUDIT` counter asserts the same condition at construction.
- **INV family** — chain heads (`find_v4_from`, `find_skor_from`) build state bar-by-bar in order and return at bar *i* using bars ≤ *i*; entries at *idx+1*; the ADR filter uses the prior 10 daily bars only; rounds are sequential counts of completed same-day signals; cutoffs verified per row (INV-LONG ≤ 11:00, INV-ABOVE ≤ 10:30). **`pool_pick`'s price tie-break is unreachable across heads**: RANK gives the v4 setups 1–3 and the skor setups 0, so the static rank always decides a cross-head pick and no later bar's entry price can choose an earlier entry (the Nifty caveat class, checked and closed here).
- **N4-V3 (surviving 69 rows)** — entry 09:35 after the 09:25 signal bar; move, direction and the one-sided +3% LONG cap recomputed for every row; 64 of 73 rows have reaction day after the announcement day; the other same-day rows carry pre-open-public evidence on their own records (prior-day-announced block deal, a bonus ex-date, an opening block-window sale, an overnight USFDA approval).
- **P2F / P2F-R2 / R2-LOWBAND (105 rows)** — entries at the R+1 / R+2 open; the reaction return (R close ÷ R−1 close) is complete at R's close, before any entry; bands and directions recomputed for every row. `results_events` takes R as the calendar reaction_date verbatim — no return-based selection anywhere in the dating.
- **GAP-FADE / GAP-FADE-INC (404 rows)** — gap recomputed from the bar-0 open print vs prior close for every row; regime labels prior-day-only; every entry strictly after the print bar (09:20 = second bar; 09:40 by time lookup, index ≥ 1). Two GAP-FADE rows enter at 09:40 / 10:05 because their stock-days' bars start late — in both, the entry is the second recorded bar, strictly after the print that defines the gap. Certified with that note.

**Disclosed, not voided:** BDL 2025-03-26 (−₹1,100.68), a same-day large-order row whose record carries no timestamp and no intraday mark (its 2025-01-16 sibling was filed at 13:49 — but a sibling's pattern is inference, not evidence). One calendar row (UNITDSPR 2026-10-28) has an unsourceable reaction date (named in Round 3); it admits no book row.

## WS0 — Triple combination (R6-01, decision support): exactly additive; fails (e) and (f) only
Ingredients re-anchored to the paisa on the Round-5 book before combining (R2-26 → ₹85,340.57 / ₹2,27,415.67; R5-03 → ₹88,401.23 / ₹2,26,071.55; R5-07 → ₹90,121.11 / ₹2,47,599.90 — all reproduced). The combination is **exactly additive**, to the paisa, in both years:

- **2025 Jan–Oct → ₹1,08,249.77 (₹10,824.98/month); 2026 Jan–Oct → ₹2,54,500.44; combined → ₹3,62,699.89.**
- Placebos beaten: P1 all-placebo ₹1,62,831.09 · P2 ₹3,27,886.82 · P3 ₹3,16,724.72 (variant ₹3,62,699.89). Legs a, b, c, d, g, h, i, x pass.
- **Failing legs: (e)** combined ex-top-3 ₹99,322.68 → ₹86,720.81 (2026's ex-top-3 absorbs the damage: ₹75,557.94 → ₹56,375.37), **and (f)** Dec 2025 +₹1,207.95 → −₹99.76 — a much smaller flip than R5-15's (−₹632.67), because R2-26's December gains absorb most of NE-REV's December loss.
- Recorded **unbanked** — adoption is Chandu's. Restated on the ending book in the Decision state below.

## WS1 — NE-REV repairs (R6-02…R6-05; R6-06 audit): two repairs reduce the failure to leg (e) alone; none banks
| Cycle | Repair | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|
| R6-02 | Threshold **2.25%** | +₹7,375.61 / +₹40,742.69 | **₹84,207.51** | **₹2,64,036.03** | **(e) only** |
| R6-03 | Threshold 2.50% | −₹3,572.54 / +₹34,425.59 | ₹76,388.46 | ₹2,57,718.93 | b, e, f |
| R6-04 | **DOWN+FLAT cells** (thr 2.0%) | +₹544.11 / +₹32,422.92 | ₹78,350.68 | ₹2,55,716.26 | **(e) only** |
| R6-05 | Entry **11:05** (thr 2.0%) | −₹18,420.55 / +₹18,386.53 | ₹63,212.45 | ₹2,41,679.87 | a, b, e, f |

- **R6-02** is the family's best construction: combined ₹3,47,839.48 (above R5-07's ₹3,36,237.19), **no month flips** — and leg (e) still refuses it (combined ex-top-3 ₹99,322.68 → ₹97,177.38; 2025's own ex-top-3 falls ₹23,764.74 → ₹20,114.34). The Dec-2025 flip that killed R5-07 does not occur at 2.25%.
- **R6-04** confirms the diagnosis behind it: R5-07's December damage was UP-cell-located — restricting to DOWN+FLAT removes the flip entirely and keeps ₹32,422.92 of 2026 — but its 2025 standalone is only +₹544.11 and ex-top-3 falls harder (₹23,764.74 → ₹13,867.75).
- **R6-03** is worse in the weak year (2025 standalone negative; Dec flips again): the threshold axis is not monotone in 2025. **R6-05** is the fifth delay mechanism to lose on this book — the 11:05 entry destroys 2025 (−₹18,420.55 standalone; three month flips).
- **R6-06 (audit):** repair (d), carrier exclusion, **skipped as pre-registered** — no causal prior-year book ranking exists for 2025 (no 2024 SarvaRitu book in the workspace; ranking 2025 on the 2026 book would be look-ahead). No substitute was invented and no candidate was gated.

## WS2 — Increment conditioning (R6-07, R6-08): the delayed increment BANKS
Decomposition verified before scoring: the ≥1.25% sleeve = banked ≥1.5% sleeve + [1.25%, 1.5%) increment, row sets disjoint and exhaustive, increment standalone +₹10,594.66 / +₹2,778.21 (the recorded R5-03 deltas).

| Cycle | Conditioning | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|
| R6-07 | Increment, **DOWN cells only**, 09:20 | +₹9,278.66 / +₹913.63 | ₹87,085.23 | ₹2,24,206.97 | **(e) only** |
| R6-08 | Increment, DOWN+FLAT, **entry 09:40** | +₹2,305.22 / +₹4,763.03 | **₹80,111.79** | **₹2,28,056.37** | **none — BANKED** |

**R6-08 passes all ten legs** (placebos beaten — mirror-increment book ₹2,93,692.75 and one-bar-late book ₹3,05,644.25 vs the variant's ₹3,06,789.43 combined, the late margin a thin ₹1,145.18 and recorded as such; no flips; timing violations 0, the signal being complete at the 09:15 print). Entering the marginal band 20 minutes later changes its stock mix enough to cure the concentration that refused the same population at 09:20 in both its swap form (R5-03) and its DOWN-only form (R6-07, whose 2026 side still concentrates: ex-top-3 ₹75,557.94 → ₹68,047.39). The banked sleeve (≥1.5%) was never touched. This is the round's only banking — and the book's first construction in six rounds to win *because* of a later entry (lesson R6-L1).

## WS3 — Range-expansion follow (R6-09, R6-10): LONG dead; SHORT fails leg (c) only
Scored exactly as pre-registered; timing violations counted = 0 on every row (entry bar 10:20 strictly after the 10:10 signal bar, asserted in code).

| Cycle | Direction | Trades | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|---|
| R6-09 | LONG (top-quartile close) | 242 | −₹1,181.70 / −₹10,839.47 | ₹79,840.19 | ₹2,17,216.90 | a, b, c, d, e, f, h |
| R6-10 | SHORT (bottom-quartile close) | 237 | +₹14,409.54 / −₹10,286.95 | **₹96,126.79** | ₹2,17,769.42 | **(c) only** |

**R6-09** loses in both years and is beaten by its own one-bar-late placebo — volatility-state continuation does not exist on the long side. **R6-10** is a real 2025 phenomenon (+₹16,015.00 to Jan–Oct against the then-incumbent, every other leg green, no flips) billed to 2026 (−₹10,286.95; 2026 remains above its floor line regardless) — the book's cross-year opposition (Lesson 47) appearing in a brand-new mechanism. Owner-decision class.

## WS4 — Combinations of Round-6 bankings
One banking exists (R6-08); there is no second banking to combine it with. Closes by statement.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹78,420.04** = **₹7,842.00/month** · **gap to floor ₹71,579.96** (round opened at ₹72,193.43; R6-08 banked +₹2,305.22, the audit void cost −₹1,691.75) · full-year +₹77,041.31 · 887 trades · ex-top-3 stocks **+₹23,708.10** (top-3: OBEROIRLTY ₹30,748.68, ASTRAL ₹14,260.02, GLENMARK ₹8,324.51).
Months: Jan +₹2,200.31 · Feb +₹20,242.66 · Mar +₹8,953.57 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹7,083.39** · Aug +₹11,173.48 · Sep +₹5,585.44 · **Oct −₹3,944.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹73,644.96 · H2 +₹4,775.08.
Regime cells (full-year): DOWN +₹42,941.63 · FLAT +₹21,250.68 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · GAP-FADE +₹21,470.27 · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹5,851.63 · GAP-FADE-INC +₹2,305.22 · F4 +₹91.14 · R2-LOWBAND −₹116.75 · INV-R3 −₹230.42 · P2F-R2 −₹390.06.

### 2026 — floor MET
Jan–Oct **+₹2,29,696.21** = **₹22,969.62/month** (₹79,696.21 above the floor line) · 969 trades · all ten months green (Jan +₹29,518.32 … Oct +₹63,740.90) · ex-top-3 stocks +₹77,473.77.
Regime cells: DOWN +₹2,10,264.94 · FLAT +₹2,909.78 · UP +₹16,521.49.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹29,562.32 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · GAP-FADE-INC +₹4,763.03 · INV-ABOVE +₹3,349.21 · GAP-FADE +₹1,492.21 · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r6_book2025_trades.csv`, `stocks_engine_r6_book2026_trades.csv` (exported from the ending incumbent and independently re-summed to the paisa). Evidence: `r6_results.json` (11 records: the R6-01 decision-support gate, 8 gated candidates, the R6-06 skip audit, the R6-11 causality audit). Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R6-L1…R6-L5). State: `stocks_engine_state.json` (`round6_summary`).

## Decision state after Round 6 (owner's calls, none taken by the engine — all restated on the ending book, per R6-L5)
- **R2-26** (INV-ABOVE T150/S080): clean sheet. Adoption → 2025 JO **₹85,954.04**, 2026 JO ₹2,33,818.54.
- **R5-03** (gap-fade thr 1.25% swap): fails (e) only. Clean adoption (retiring the banked GAP-FADE-INC) → 2025 JO **₹86,709.48**, 2026 JO ₹2,27,711.39.
- **R5-07** (NE-REV LONG): fails (e) + (f). Adoption → 2025 JO **₹90,734.58**, 2026 JO ₹2,54,002.77.
- **R6-02** (NE-REV thr 2.25%): fails (e) only; the largest NE-REV construction. Adoption → 2025 JO **₹84,820.98**, 2026 JO ₹2,70,438.90.
- **R6-04** (NE-REV DOWN+FLAT): fails (e) only. Adoption → 2025 JO **₹78,964.15**, 2026 JO ₹2,62,119.13.
- **R6-10** (REXP SHORT): fails (c) only. Adoption → 2025 JO **₹94,435.04** (₹9,443.50/mo), 2026 JO ₹2,19,409.26 (still above floor).
- **The triple (R2-26 + R5-03 + R5-07)**: priced at R6-01 on the Round-5 book (₹1,08,249.77); restated on this book (void applied, R5-03 at clean-adoption net) → 2025 JO **₹1,06,558.02 (₹10,655.80/month), gap ₹43,441.98** — the closest 2025 has come to the floor. Its R6-01 gate sheet (fails (e) + (f)) was run on the Round-5 book and is not re-run; the totals above are the arithmetic restatement.

## Where the 2025 floor can still come from (honest close)
Round 6 banked the increment's delayed form, priced the owner's largest decision exactly, reduced NE-REV's failure to a single leg twice over, and found one more (c)-only phenomenon — while its audit removed 4 rows and certified the rest of the book causal. The 2025 gap (₹71,579.96) is now concentrated in owner decisions: the flagged list carries ₹28,137.98 of additive 2025 deltas (triple form) plus R6-10's +₹16,015.00, each refused by exactly one or two named legs. Outside owner decisions, the remaining routes are unchanged: a new data axis (volume / bulk-block / delivery % — none in the workspace; the carrier-exclusion repair also waits on a causal 2024 book), or Nov–Dec forward evidence on the frozen book.
