# Stocks (SarvaRitu) Engine — ROUND 5 · Gap-Fade Mirror, Sleeve Micro-Grid, Non-Event Reversal, P2F-R2 Conditioning, Red-Month Diagnosis
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting book** (Round-4 ending book, re-verified by independent re-sum of the exported CSVs): 2025 Jan–Oct **+₹77,806.57** (₹7,780.66/mo; gap ₹72,193.43) · 2026 Jan–Oct **+₹2,23,293.34** (₹22,329.33/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing violations are derived from each construction and passed explicitly (lesson R4-L2) — a cell whose entry uses its own signal print is void on sight.
- **R2-26 is NOT adopted** (Chandu's call, still pending): every Round-5 baseline is the book without it.
- **Ending book: UNCHANGED to the paisa.** 12 gated cycles, 1 diagnosis audit, 1 decision-support combination — **zero bankings, zero voided cells**. 2025 Jan–Oct **+₹77,806.57** (₹7,780.66/mo; **gap ₹72,193.43**) · 2026 Jan–Oct **+₹2,23,293.34** (₹22,329.33/mo; floor MET).

---

## WS3 — PRE-REGISTRATION (written before any WS3 scoring)

**Population rule (frozen).** Universe: the 25 watchlist symbols, every trading day present in `data/full_hist`. A stock-day is **event-contaminated** — and excluded — if it falls in the reaction window {R, R+1, R+2} (the stock's own trading days) of **any** results event for that stock, where R is the machinery's effective reaction date (`reaction_candidates` over `stock_event_calendar_2025.csv` and `stock_event_calendar_jan_oct_2026.csv`, both years pooled into one contamination set). Weekend bars excluded, as in every sleeve of this engine.

**Signal (frozen).** For a non-contaminated stock-day: move = (close of the 10:25 bar ÷ prior daily close − 1) × 100. The 10:25 bar completes at 10:30, so the move is fully known at 10:30. move ≤ −2.00% → LONG candidate; move ≥ +2.00% → SHORT candidate. At most one trade per stock-day (the signal is evaluated once, at 10:30).

**Entry / exits (frozen).** Entry at the **open of the 10:35 bar** — strictly after the signal bar (10:25); the 10:30 bar is skipped entirely, so no fill can touch the signal print or the bar that follows it. Exits **T100/S065** via `replay_plain` (entry bar checked), square-off 15:10. Cost ₹40/trade, per 100 shares.

**Controls (frozen).** Placebos, computed as whole books on the identical population: (i) the opposite direction on the same stock-days and entry bar; (ii) the same direction entered one bar later (10:40 open). Timing audit: violations = rows whose entry bar is not strictly after the signal bar; by construction this must be 0 and is asserted in code, not defaulted.

**Verdict rule (frozen).** Each direction is a separate candidate, gated whole-book per year under the nine-leg gate + leg (x). Neither direction inherits anything from the other or from the gap-fade family.

*(End of pre-registration. All sections below are written after scoring.)*

---

## WS1 — Gap-fade SHORT, UP-cell mirror (R5-01, R5-02) — REJECTED, family closed
The banked phenomenon (R4-03) is fade-LONG in DOWN+FLAT cells. Its mirror — SHORT gap-ups ≥1.5%, 09:20 entry, T125/S050, added as a separate component so the banked sleeve is untouched — was never gated; R3's diagnostic had scored only the *unrestricted* short side (−₹49/−₹9 per trade). Placebos per cell: follow-LONG on the same gap-up days (the mirror population) and the same sleeve one bar late. Timing: entries at bar 1, signal complete at bar 0's open print → 0 violations by construction.

| Cycle | Cell | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|
| R5-01 | SHORT, UP cells only (111 tr) | −₹13,051.53 / −₹1,746.40 | ₹70,868.47 | ₹2,21,546.94 | a, b, c, d, e, f, g, h |
| R5-02 | SHORT, UP+FLAT cells (170 tr) | −₹12,433.50 / −₹1,137.24 | ₹71,486.50 | ₹2,22,156.10 | a, b, c, d, e, f, g, h |

Both cells lose in both years, flip May and Dec 2025, and — the decisive read — **the mirror placebo beats the variant**: the follow-LONG book (₹3,14,289.90 for R5-01's cell) exceeds the fade book (₹2,84,923.25). On up-trend days gap-ups *continue*; the fade's reversion exists only on the gap-down side in DOWN/FLAT states. **The gap-fade is one-sided, and the mirror family is closed on both cell sets.**

## WS2 — Banked-sleeve micro-grid (R5-03…R5-06) — all REJECTED; the banked cell is the neighbourhood peak
Swaps of the GAP-FADE component around the banked cell (≥1.5%, DOWN+FLAT, 09:20, T125/S050). Round 4's threshold swaps were scored on the *unrestricted* sleeve; these are the restricted form's own neighbours. Placebos per cell: mirror follow-SHORT at the cell's parameters; the same cell one bar late.

| Cycle | Swap | 2025 JO → | 2026 JO → | Combined → | Failed legs |
|---|---|---|---|---|---|
| R5-03 | Threshold **1.25%** | **₹88,401.23** (+₹10,594.66) | **₹2,26,071.55** (+₹2,778.21) | ₹3,13,094.05 | **(e) only** |
| R5-04 | Threshold **1.75%** | ₹73,811.52 | ₹2,19,743.09 | ₹2,92,175.88 | a, b, c |
| R5-05 | Exits **T100/S065** | ₹75,147.99 | ₹2,23,268.97 | ₹2,97,038.23 | a, b, c |
| R5-06 | Exits **T150/S065** | ₹84,937.76 (+₹7,131.19) | ₹2,16,268.73 (−₹7,024.61) | ₹2,99,827.76 | **(c) only** |

- **R5-03** passes 9 of 10 legs — both years rise, both placebos beaten (₹2,43,147.39 / ₹2,67,118.88 vs variant ₹3,13,094.05), no flips. It fails only leg (e): the incremental [1.25%, 1.5%) slice's gains concentrate in the top-3 stocks — 2026 ex-top-3 falls ₹75,557.94 → ₹67,253.47 and combined ex-top-3 falls ₹99,322.68 → ₹94,567.68 (2025's own ex-top-3 *rises*, ₹23,764.74 → ₹27,314.21). Recorded with its failing leg named, in the owner-decision class of R2-26 (see Decision state).
- **R5-06** fails only leg (c): the wider target pays in the weak year and bills the strong year — the R4-09R shape at a different stop. Combined full-year actually rises (+₹106.58); the cross-year leg refuses it anyway.
- **R5-04 / R5-05** lose outright. The [1.5%, 1.75%) slice is load-bearing in 2026 (the 1.75% sleeve's 2026 standalone is −₹2,058.04), and the tighter-target pair is worse in both years.

Four neighbours, four rejections, each on a different leg or leg-set: **the R4-03 cell is the peak of its neighbourhood on the gate's terms, not merely the first cell that passed.**

## WS3 — Non-event intraday reversal (R5-07, R5-08) — a real LONG-only phenomenon the gate cannot bank
Scored exactly as pre-registered above. Population built from 180 pooled reaction candidates; 539 contaminated stock-days excluded. Timing violations **counted = 0** on every row (asserted in code).

| Cycle | Direction | Trades | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|---|
| R5-07 | **LONG** (fade the ≥2% morning dump) | 691 | **+₹12,209.45 / +₹24,306.56** | **₹90,121.11** | **₹2,47,599.90** | **(e), (f)** |
| R5-08 | SHORT (fade the ≥2% morning rip) | 818 | −₹41,334.92 / −₹18,088.52 | ₹41,903.46 | ₹2,05,204.82 | a, b, c, d, e, f, g, h |

**R5-07 is the round's largest finding.** A ≥2% fall by 10:30 on a day with no results event reverts, in both years, at real size: combined book → ₹3,36,237.19 (+₹36,516.01), both placebos beaten clearly (opposite-direction ₹2,34,944.85; one-bar-late ₹3,01,424.12), halves and regime cells green, leg (x) satisfied with ₹97,599.90 to spare. It fails exactly two legs:
- **(e) ex-top-3:** the sleeve's gains sit in the book's top-3 names — combined ex-top-3 *falls* ₹99,322.68 → ₹86,879.08 (2025: ₹23,764.74 → ₹21,800.93; 2026: ₹75,557.94 → ₹65,078.15) even as the totals rise by ₹36,516.01.
- **(f) month flip:** Dec 2025 +₹1,207.95 → −₹632.67 (the sleeve's Dec-2025 rows net −₹1,840.62; December sits outside the judged Jan–Oct window but leg (f) reads the full year).

**R5-08 is the round's worst sleeve.** Morning rips on non-event days do *not* revert — shorting them loses −₹59,423.44 standalone across the two years and fails 8 legs. The reversal phenomenon is **LONG-only**, the same one-sidedness WS1 found in the gap family.

## WS4 — P2F-R2 regime / band conditioning (R5-09…R5-12) — all REJECTED; the weakness is population-wide
P2F-R2 on the current book: 2025 Jan–Oct **−₹1,148.55** (21 trades; full-year −₹390.06) vs 2026 **+₹15,149.33** (32 trades). Every book row's reaction band was recovered by exact join to the machinery's scored lag-2 rows (**53/53 joined, 0 recomputed**). The brief's 2.0–2.5% band at R+2 is the separate R2-LOWBAND component (1 trade in 2025 — it cannot carry a conditioning verdict), so the band axis is applied inside P2F-R2's own ≥2.5% population, split at 4.0%. Placebos per condition: chrono-removal of the same count, and complement-removal (keep only the dropped subset).

Anatomy first: 2025 cells DOWN −₹715.31 / UP −₹433.24 / FLAT — (no trades); bands [2.5, 4.0) −₹1,299.35 / ≥4.0 **+₹150.80**. 2026 cells DOWN +₹10,670.16 / FLAT +₹2,090.17 / UP +₹2,389.00; bands [2.5, 4.0) +₹2,424.47 / ≥4.0 **+₹12,724.86**.

| Cycle | Condition | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|
| R5-09 | Keep DOWN+FLAT entry cells | ₹78,239.81 (+₹433.24) | ₹2,20,904.34 (−₹2,389.00) | a, b, c, e, h |
| R5-10 | Keep DOWN entry cells only | ₹78,239.81 (+₹433.24) | ₹2,18,814.17 (−₹4,479.17) | a, b, c, e, h |
| R5-11 | Keep band [2.5%, 4.0%) | ₹77,655.77 | ₹2,10,568.48 (−₹12,724.86) | a, b, c, e, h |
| R5-12 | Keep band ≥4.0% only | ₹79,105.92 (+₹1,299.35) | ₹2,20,868.87 (−₹2,424.47) | a, c, e |

Every restriction that removes a 2025 loss removes more 2026 money. The ≥4.0% band is simultaneously 2025's only positive slice and 84% of 2026's component; the cell split is the same shape inverted. Even the chrono placebo beats R5-09/R5-10 (₹2,99,567.23 / ₹3,00,785.48 vs variants ₹2,97,006.93 / ₹2,94,916.76) — the UP/FLAT trades being removed are not even the component's worst by a null standard. **P2F-R2's 2025 weakness is a property of the whole population on the 2025 tape (R3-L3), not of any conditionable subset. The conditioning axis is closed.**

## WS5 — Red-month diagnosis, Jun/Jul/Oct 2025 (R5-13, audit) — no signature, no candidate
Frozen signature rule (written before the scan was read): a (component × regime-cell) slice qualifies only if negative in **each** of Jun, Jul and Oct 2025, negative across full-year 2025, and its three-month sum ≤ −₹3,000.

| Month | Total | Anatomy |
|---|---|---|
| Jun 2025 | −₹955.92 (7 trades) | **One component only: INV-ABOVE −₹955.92.** An information desert, not a bleed |
| Jul 2025 | −₹5,523.29 (30 trades) | Broad shallow bleed: INV-ABOVE −₹2,473.45 (3 tr) · N4-V3 −₹1,821.00 (2 tr) · F4 −₹1,025.28 (19 tr) · P2F −₹173.47 · P2F-R2 −₹170.85 · GAP-FADE +₹140.76 |
| Oct 2025 | −₹4,624.53 (14 trades) | **F4 −₹3,021.83 in 3 trades** · N4-V3 −₹793.80 · P2F −₹312.98 · P2F-R2 −₹288.00 · INV-ABOVE −₹207.92 |

The two near-misses, and why the rule refuses both:
- **INV-ABOVE × UP** is the only slice negative in all three months (−₹955.92 / −₹2,473.45 / −₹13.00; sum −₹3,442.37) — but it **earns +₹6,435.21 across full-year 2025**. Its wound-month losses are variance on an earning slice (the R3-L2 shape); the full-year leg of the rule exists precisely to refuse it.
- **F4 × DOWN** is negative in Jul (−₹1,819.15) and Oct (−₹3,021.83) and across 2025 (−₹2,369.54), sum −₹4,840.98 — but it has **zero June trades**, so it is not a three-month signature.

**Qualifying slices: none.** The three red months have three different anatomies; no conditional candidate was manufactured. Full table: `r5_ws5_diag.json`.

## WS6 — Combinations (R5-15, decision support)
No Round-5 bankings exist, so there is no combination to bank. As decision support only (the Round-4 WS4 disposition), the round's two near-misses were gated in combination — both row sets rebuilt and **anchored to their recorded single-variant totals to the paisa before scoring** (R5-03: ₹88,401.23 / ₹2,26,071.55; R5-07: ₹90,121.11 / ₹2,47,599.90):

**R5-15 — thr-1.25 sleeve swap + NE-REV LONG:** exactly additive. 2025 JO → **₹1,00,715.77**, 2026 JO → **₹2,50,378.11**, combined → ₹3,49,610.06; both combination placebos beaten (both sleeves one bar late ₹2,68,821.82; both mirrors ₹1,78,371.06 — vs variant ₹3,49,610.06). It fails the **same two legs**: (e) combined ex-top-3 → ₹82,699.21, and (f) the Dec-2025 flip (NE-REV's alone; the 1.25% swap adds no flip). Recorded **unbanked regardless of verdict** — adoption is Chandu's.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹77,806.57** = **₹7,780.66/month** · **gap to floor ₹72,193.43 (unchanged — nothing banked)** · full-year +₹76,427.84 · 857 trades · ex-top-3 stocks **+₹23,764.74** (top-3: OBEROIRLTY ₹30,432.17, ASTRAL ₹14,260.02, GODREJCP ₹7,970.91).
Months: Jan +₹5,327.82 · Feb +₹18,656.16 · Mar +₹6,124.45 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹5,523.29** · Aug +₹11,173.48 · Sep +₹5,379.98 · **Oct −₹4,624.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹72,356.85 · H2 +₹5,449.72.
Regime cells (full-year): DOWN +₹42,688.79 · FLAT +₹20,890.05 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · GAP-FADE +₹21,470.27 · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹7,543.38 · F4 +₹91.14 · INV-R3 −₹230.42 · P2F-R2 −₹390.06 · R2-LOWBAND −₹116.75.

### 2026 — floor MET
Jan–Oct **+₹2,23,293.34** = **₹22,329.33/month** (₹73,293.34 above the floor line) · 899 trades · all ten months green (Jan +₹29,738.12 … Oct +₹54,379.99) · ex-top-3 stocks +₹75,557.94.
Regime cells: DOWN +₹2,02,017.65 · FLAT +₹5,215.00 · UP +₹16,060.69.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹27,922.48 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · INV-ABOVE +₹3,349.21 · GAP-FADE +₹1,492.21 · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r5_book2025_trades.csv`, `stocks_engine_r5_book2026_trades.csv` (exported from the ending incumbent and independently re-summed to the paisa — identical to the Round-4 books, as nothing banked). Evidence: `r5_results.json` (14 records: 12 gated cycles, the R5-13 diagnosis audit, the R5-15 decision-support combination, plus per-cycle placebos/flips/standalones; R5-14 was reserved for the WS5 conditional candidate, which the diagnosis did not produce). Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R5-L1…R5-L5). State: `stocks_engine_state.json` (`round5_summary`).

## Decision state after Round 5 (owner's calls, none taken by the engine)
- **R2-26** (INV-ABOVE T150/S080): still pending from Round 2; passes all 10 legs on the current book (R4-10). Adoption → 2025 ₹85,340.57.
- **R5-07** (NE-REV LONG): fails legs (e) and (f). Adoption alone → 2025 Jan–Oct **₹90,121.11** (₹9,012.11/mo), gap ₹59,878.89.
- **R5-03** (gap-fade thr 1.25%): fails leg (e) only. Adoption alone → 2025 Jan–Oct **₹88,401.23**, gap ₹61,598.77.
- **R5-15** (R5-03 + R5-07 together): exactly additive → 2025 Jan–Oct **₹1,00,715.77** (₹10,071.58/mo), gap **₹49,284.23** — the closest 2025 has come to the floor — failing (e) and (f).

## Where the 2025 floor can still come from (honest close)
Round 5 closed four more axes with controlled runs: the gap-fade mirror (one-sided phenomenon), the banked sleeve's neighbourhood (the R4-03 cell is its peak), P2F-R2 conditioning (population-wide weakness), and the red-month signature search (three anatomies, no shared signature). It also found the strongest new phenomenon since the gap-fade itself — non-event morning-dump reversion — which the gate refuses on concentration and one out-of-window month flip; that refusal, and the two other one/two-leg near-misses, are now the owner's decisions, itemised above with their adoption values. What remains outside owner decisions is unchanged from Round 4's close: a new data axis (volume / bulk-block deals / delivery % — none in the workspace), or Nov–Dec forward evidence on the frozen book.
