# Stocks (SarvaRitu) Engine — ROUND 8 · Max-Stack Gate, Drive-Continuation, Index-State Conditioning, REXP Geometry Neighbour
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · no volume features (stored candles are OHLC only) · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting book** (Round-6/7 ending book, causality-audited; to be re-verified by independent re-sum of the exported CSVs before any Round-8 scoring): 2025 Jan–Oct **+₹78,420.04** (₹7,842.00/mo; gap ₹71,579.96) · 2026 Jan–Oct **+₹2,29,696.21** (₹22,969.62/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code (lessons R4-L2, R6-L4, Nifty-46, R6-11) — a cell whose entry uses information not knowable strictly before the entry bar is void on sight.
- **Flagged, NOT adopted** (Chandu's calls; baselines stay on the book without them): R2-26 (clean sheet), R5-03 (fails (e)), R5-07 / R5-07-CERT (fail (e)+(f)), R6-02 (fails (e)), R6-04 (fails (e)), R6-10 (fails (c)), R7-02 (fails (c)), R7-03 (fails (c)), R7-06 (fails (e)+(f)), the triple and the max stack (arithmetic restatements until this round).

---

## PRE-REGISTRATION (written before any Round-8 scoring)

### Certified population and index data (frozen definitions)
- **Certified non-event set:** exactly the Round-7 set — `stocks_engine_r7_builders.certified_exclusions()` (the R6-11 standard: frozen R5 reaction windows ∪ every calendar event day, any event_type, with its reaction window; blanket window when the reaction date is unsourceable). No substitute definition is invented mid-round.
- **Nifty intraday state:** from `data/full_hist/NIFTY/spot_5m.csv` (5-min bars; the bar timestamped T covers [T, T+5min) and completes at T+5min) and the prior trading day's Nifty close from `data/full_hist/NIFTY/spot_daily.csv` (supplemented by `data/sarvaritu_fwd/NIFTY/spot_daily.csv` for dates absent from the full-history file, the FL convention). A state measured on the bar timestamped T is knowable at T+5min and may condition only entries at bars strictly after that instant. Days where the needed Nifty bar or prior close is missing are counted and treated as **state unknown** (the conditioned leg does not trade in the variant; it is never guessed).

### WS0 — Max-stack gate (R8-01 anchors audit; R8-02 gate, decision support, force_no_bank)
The full adoption stack gated as ONE whole-book candidate on the starting book:
1. **R2-26** — swap comp `INV-ABOVE` for the cached T150/S080 population (exact prior construction).
2. **R5-03, clean form** — swap comp `GAP-FADE` for the ≥1.25% DOWN+FLAT fade-LONG sleeve (09:20 entry, exact prior construction) **and retire comp `GAP-FADE-INC`** (the banked 09:40 increment occupies the same [1.25%, 1.5%) band inside the swapped sleeve; keeping both would double-trade those stock-days). This is the form the flagged list already prices on this book.
3. **R5-07-CERT** — add the morning NE-REV LONG rows on the certified population (R7-08 construction, comp renamed `NE-REV-CERT`).
4. **R7-03** — add the REXP-SHORT rows restricted to DOWN regime cells (R7-03 construction verbatim).
- **Anchors (R8-01, audit — no combination is scored in R8-01):** each ingredient applied ALONE to the starting book must reproduce its flagged-list price on this book before the combination is read: R2-26 → 2025 JO ₹85,954.04 / 2026 JO ₹2,33,818.54 · R5-03-clean → ₹86,709.48 / ₹2,27,711.39 · R5-07-CERT → ₹92,537.28 / ₹2,53,809.07 · R7-03 → ₹93,290.43 / ₹2,21,296.88. Any anchor that fails stops the round's WS0 until explained.
- **Placebos (whole books, same structure incl. GAP-FADE-INC retirement):** P1 all-placebo — INV-ABOVE SHORT-side T150/S080 swap + GAP-FOLLOW mirror SHORT sleeve in the GAP-FADE slot + NE-REV-CERT opposite direction (SHORT) + REXP LONG on DOWN cells. P2 — real R2-26 + real R5-03-clean + NE-REV-CERT one bar late (10:40) + REXP DOWN one bar late (10:25). P3 — real R2-26 + gap sleeve one bar late (bar 2) with INC retired + real NE-REV-CERT + real R7-03.
- Timing violations: the sum of the ingredients' own counted violations (gap entries at bar ≥ 1 after the bar-0 print; NE-REV entries 10:35 strictly after the 10:25 signal bar; REXP entries 10:20 strictly after the 10:10 signal bar) — counted in code, asserted 0.
- R8-02 is recorded with force_no_bank regardless of verdict — adoption of any part of the stack is Chandu's.

### WS1 — Drive-continuation sleeve (R8-03; twin R8-04)
- Population: certified non-event stock-days (above), weekend days excluded, at most one trade per stock-day.
- Signal: close of the **10:25** bar vs prior daily close ≥ **+2.00%**. The 10:25 bar completes at 10:30; every input is known at 10:30.
- Entry: **LONG** at the open of the **10:35** bar. Exits **T125/S050** via `replay_plain` (entry bar checked; square-off 15:10 per the frozen machinery). ₹40/trade.
- Placebos (whole books, identical population): opposite direction (SHORT) at the same entry bar; same direction one bar later (10:40 open). Timing audit: violations = rows whose entry bar index is not strictly after the 10:25 signal bar's index — counted, asserted 0.
- **SHORT-twin rule (frozen):** the LONG standalone is computed and printed first, as a diagnostic. IF AND ONLY IF the LONG standalone net is positive in BOTH years, the symmetric follow twin is also gated (R8-04): certified non-event days with the 10:25-bar close ≤ **−2.00%** vs prior close → **SHORT** at the open of the 10:35 bar, T125/S050, same placebos. If the diagnostic does not trigger, R8-04 records the non-trigger as an audit entry and no twin is scored. (The twin's population is NE-REV's signal population traded in the follow direction; as a book addition it is a distinct comp.)

### WS2 — Index-state conditioning (R8-05, R8-06)
- **R8-05 (NE-REV × Nifty-down):** the certified morning NE-REV population (R7-08 construction verbatim — anchor first: unconditioned standalone must reproduce +₹14,105.64 / +₹24,112.86 on 661 rows) admitted **only on days where Nifty's 10:25-bar close is ≤ −0.30% vs Nifty's prior-day close** (state knowable at 10:30; entries at 10:35). State-unknown days do not trade and are counted. Gated whole-book as an addition (comp `NE-REV-IDX`). Placebos: the flipped and one-bar-late rows of the same build under the same day filter.
- **R8-06 (banked fade × Nifty-down state):** the banked sleeve legs are the starting book's rows with comp ∈ {`GAP-FADE`, `GAP-FADE-INC`}. State := close of Nifty's **09:15 bar** (completes 09:20) vs Nifty's prior-day close: **down** iff state < 0. Precedence: every fade entry is at the open of a bar strictly after the 09:15 bar (GAP-FADE 09:20, bar index 1 > 0; GAP-FADE-INC 09:40) — the engine's bar-index audit form (entry bar index strictly greater than the state bar's index), asserted per leg in code; state-unknown legs are counted and treated as not-down. Variant book = starting book with the fade/inc legs on not-down days **removed**. Placebos (whole books): P1 mirror restriction — fade/inc legs kept only on **not-down** days (the opposite subset); P2 chrono restriction — the same number of fade/inc legs removed chronologically earliest-first. Timing violations counted = legs failing the bar-index assertion (asserted 0).

### WS3 — R7-03 geometry neighbour (R8-07)
- Construction: REXP-SHORT restricted to DOWN regime cells, verbatim R7-03 population (anchor first at the frozen geometry: standalone must reproduce +₹14,870.39 / −₹8,399.33, 41/86 trades), rescored at **T100/S065** (target 1.00%, stop 0.65% — the single pre-registered neighbour cell; no other geometry is scored in this workstream).
- Gated whole-book as an addition (comp `REXP-SHORT`). Placebos: opposite direction (LONG, DOWN cells, T100/S065) and same direction one bar later (10:25, T100/S065), identical population. Timing audit as in WS1 of Round 7 (entry 10:20 strictly after the 10:10 signal bar), counted, asserted 0.
- Disposition (frozen): if it passes ALL legs it banks. Either way, the flagged list afterwards carries the T100/S065 form as the preferred REXP-DOWN flag with **both** prices stated (T125/S050 gated delta and T100/S065 gated delta), per the tasking.

### WS4 — Combinations + decision state (R8-08, or R8-08/R8-09 if a banking exists)
- Any two or more Round-8 bankings are combined and re-gated whole-book. If fewer than two bankings exist, WS4's combination part closes by statement.
- Finalise: ending books exported and independently re-summed; every flagged variant's adoption value restated on the ending book (R6-L5 discipline — disjoint-comp deltas applied arithmetically, method stated; nested/alternative flags marked as such, never summed); state updated. Nothing in the finalise cycle is banked.

### Verdict rule (frozen for all Round-8 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks (except WS0, which is force_no_bank by construction). A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R8-01 — WS0 ingredient anchors (audit): all four reproduce their flagged prices exactly
Each stack ingredient, applied alone to the starting book, lands on its flagged-list price to the paisa — R2-26 → 2025 JO ₹85,954.04 / 2026 JO ₹2,33,818.54 · R5-03-clean → ₹86,709.48 / ₹2,27,711.39 · R5-07-CERT → ₹92,537.28 / ₹2,53,809.07 · R7-03 → ₹93,290.43 / ₹2,21,296.88. Construction anchors inside the ingredients are also exact (gap sleeve ≥1.25% standalone +₹32,064.93 / +₹4,270.42; NE-REV-CERT +₹14,105.64 / +₹24,112.86 on 291/370 rows; REXP DOWN +₹14,870.39 / −₹8,399.33 on 41/86 rows). Timing violations counted: 0 everywhere.

## R8-02 — WS0 MAX-STACK GATE (decision support): fails leg (f) ONLY — the stack is better than its arithmetic
The four ingredients act on disjoint components, so the combination is **exactly additive at row level**: 2025 JO **₹1,23,231.11** (₹12,323.11/month; gap would fall to **₹26,768.89**), 2026 JO **₹2,47,547.25**, combined ₹3,70,821.53 vs base ₹3,06,737.52; 1,199 / 1,420 trades. The gate sheet:

| Leg | Verdict | Detail |
|---|---|---|
| (a) combined rises | ✅ | 3,06,737.52 → 3,70,821.53 |
| (b) 2025 no fall | ✅ | JO 78,420.04 → 1,23,231.11 |
| (c) 2026 no fall | ✅ | JO 2,29,696.21 → 2,47,547.25 — R7-03's −₹8,399.33 is absorbed by the other ingredients' 2026 gains |
| (d) cells positive | ✅ | all six cells positive |
| (e) ex-top-3 | ✅ | 2025 ex-top-3 ₹23,708.10 → **₹44,205.13**; combined ₹1,01,181.87 → ₹1,01,750.21 — the leg the triple failed at R6-01 **passes** in the full stack |
| (f) no green-month flips | ❌ | **Jan 2025 +₹2,200.31 → −₹715.46; Dec 2025 +₹1,207.95 → −₹99.76** |
| (g) no half flips | ✅ | |
| (h) beats placebos | ✅ | P1 all-placebo ₹1,57,925.25 · P2 swaps + sleeves late ₹3,25,723.56 · P3 R2-26 + sleeve late + real sleeves ₹3,24,846.36 — all beaten |
| (i) timing clean | ✅ | violations counted 0 |
| (x) 2026 floor holds | ✅ | ₹2,47,547.25 ≥ ₹1,50,000 |

**The gated truth is better than the Round-7 arithmetic restatement (₹1,21,428.41, legs (c)+(e)+(f) inherited):** the restatement used R5-07's birth form and R5-03's as-gated delta, and inherited failing legs that do not transfer to the assembled book. Gated properly — CERT form, clean R5-03, R7-03 included — the stack's **sole** failing leg is (f): two small 2025 months (Jan, Dec) flip green-to-red. Recorded with force_no_bank: adoption is Chandu's, and it is now priced with a one-leg failure instead of three.

## WS1 — Drive-continuation (R8-03): REJECTED on seven legs; (R8-04): twin not triggered
800 signal days, 800 trades (428 in 2025, 372 in 2026) on the certified population. Standalone **−₹1,710.67 (2025)** / **−₹28,882.57 (2026)** — negative in both years; 2025 JO → ₹73,389.15, combined falls to ₹2,76,144.28; fails (a), (b), (c), (d), (e), (f), (h) (Jan and May 2025 flip; the one-bar-late placebo book, ₹3,07,386.03, beats the variant). A ≥2% morning up-drive on a quiet day does not continue into the afternoon on these tapes — it is faded by the close, the mirror image of NE-REV's phenomenon. Not flagged (seven legs is not a near-miss).
**R8-04:** the frozen twin rule required the LONG standalone to be positive in both years; it is negative in both, so **no SHORT twin was scored** — recorded as an audit entry, per the freeze.

## WS2 — Index-state conditioning (R8-05, R8-06): real medicine, partial cure — both flagged
**R8-05 NE-REV-IDX.** The day filter (NIFTY 10:25-bar close ≤ −0.30% vs prior close) kept **453 of 661** certified rows (201/252 by year); 208 signal rows dropped on state, **0 on state-unknown**. Conditioned standalone +₹10,055.20 / +₹31,651.93 (full year); book JO deltas **+₹11,353.09 / +₹31,651.93** → 2025 JO **₹89,773.13**, 2026 JO **₹2,61,348.14**; placebos beaten (₹2,48,211.36 / ₹3,12,878.44). It **cures the Jan-2025 flip** that both NE-REV forms carried — and still fails **(e) + (f)**: combined ex-top-3 falls ₹1,01,181.87 → ₹1,00,005.19 (the sleeve's 2026 gains land in carrier names), and Dec 2025 flips (+₹1,207.95 → −₹838.69). Flagged as a NE-REV-family alternative.
**R8-06 banked fade × NIFTY-down.** Of the 404 banked fade legs, **350 already sit on NIFTY-down mornings** (state-unknown: 0; bar-index violations: 0) — the banked sleeve was implicitly index-conditioned by its own construction. Removing the 54 not-down legs: 2025 JO → **₹82,018.25** (the removed legs were net −₹3,598.21 in 2025), 2026 JO → ₹2,27,218.97 (the same legs were net +₹2,477.24 in 2026). Fails **(c) only**; both placebos beaten (mirror ₹2,75,585.82; chrono ₹2,99,587.78). Flagged — a restriction decision, not an addition.

## WS3 — R7-03 geometry neighbour (R8-07): REJECTED on (c) only — the (c) question now has two prices
Population re-anchored exactly at T125/S050 first (+₹14,870.39 / −₹8,399.33; 41/86). At **T100/S065**: standalone **+₹10,243.45 / −₹5,899.72**, same 41/86 trades; 2025 JO → **₹88,663.49**, 2026 JO → ₹2,23,796.49; every leg passes except **(c)**; placebos beaten. The tighter target cuts the 2026 bleed by ₹2,499.61 and the 2025 gain by ₹4,626.94 — there is no geometry at which this population pays 2025 for free. Per the frozen disposition, the flagged list now carries the **T100/S065 form as the preferred REXP-DOWN flag with both prices stated** (T100: +₹10,243.45 / −₹5,899.72 · T125: +₹14,870.39 / −₹8,399.33).

## WS4 — Combinations (R8-08)
Zero bankings in Round 8; there is no combination to re-gate. Closes by statement.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹78,420.04** = **₹7,842.00/month** · **gap to floor ₹71,579.96 (unchanged — Round 8 banked nothing)** · full-year +₹77,041.31 · 887 trades · ex-top-3 stocks **+₹23,708.10** (top-3: OBEROIRLTY ₹30,748.68, ASTRAL ₹14,260.02, GLENMARK ₹8,324.51).
Months: Jan +₹2,200.31 · Feb +₹20,242.66 · Mar +₹8,953.57 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹7,083.39** · Aug +₹11,173.48 · Sep +₹5,585.44 · **Oct −₹3,944.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹73,644.96 · H2 +₹4,775.08.
Regime cells (full-year): DOWN +₹42,941.63 · FLAT +₹21,250.68 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · GAP-FADE +₹21,470.27 · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹5,851.63 · GAP-FADE-INC +₹2,305.22 · F4 +₹91.14 · R2-LOWBAND −₹116.75 · INV-R3 −₹230.42 · P2F-R2 −₹390.06.

### 2026 — floor MET
Jan–Oct **+₹2,29,696.21** = **₹22,969.62/month** (₹79,696.21 above the floor line) · 969 trades · all ten months green (Jan +₹29,518.32 … Oct +₹63,740.90) · ex-top-3 stocks +₹77,473.77.
Regime cells: DOWN +₹2,10,264.94 · FLAT +₹2,909.78 · UP +₹16,521.49.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹29,562.32 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · GAP-FADE-INC +₹4,763.03 · INV-ABOVE +₹3,349.21 · GAP-FADE +₹1,492.21 · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r8_book2025_trades.csv`, `stocks_engine_r8_book2026_trades.csv` (exported from the ending incumbent — identical to the Round-7 books — and independently re-summed to the paisa). Evidence: `r8_results.json` (8 records: 4 gated candidates, 1 decision-support gate, 3 audits). Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R8-L1…R8-L4). State: `stocks_engine_state.json` (`round8_summary`).

## Decision state after Round 8 (owner's calls, none taken by the engine — all restated on the ending book, per R6-L5)
- **R8-MAXSTACK-GATED** (R2-26 + R5-03-clean + R5-07-CERT + R7-03, gated whole at R8-02): fails **(f) only** (Jan + Dec 2025 flips). Adoption → 2025 JO **₹1,23,231.11 (₹12,323.11/month), gap ₹26,768.89**, 2026 JO **₹2,47,547.25**. The largest decision is now a one-leg decision.
- **R2-26** (INV-ABOVE T150/S080): clean sheet. Adoption → 2025 JO **₹85,954.04**, 2026 JO ₹2,33,818.54.
- **R5-03** (gap-fade thr 1.25% swap): fails (e) only. Clean adoption (retiring GAP-FADE-INC) → 2025 JO **₹86,709.48**, 2026 JO ₹2,27,711.39.
- **R5-07-CERT** (NE-REV LONG, certified population): fails (e) + (f). Adoption → 2025 JO **₹92,537.28**, 2026 JO ₹2,53,809.07.
- **R8-05** (NE-REV-IDX, NIFTY-down conditioning): fails (e) + (f), Dec flip only. Adoption → 2025 JO **₹89,773.13**, 2026 JO **₹2,61,348.14**. NE-REV-family alternative.
- **R8-07** (REXP-SHORT DOWN-only, T100/S065 — preferred REXP-DOWN form): fails (c) only. Adoption → 2025 JO **₹88,663.49**, 2026 JO ₹2,23,796.49. The T125/S050 form (R7-03) prices at 2025 JO **₹93,290.43**, 2026 JO ₹2,21,296.88.
- **R8-06** (fade × NIFTY-down restriction of banked legs): fails (c) only. Adoption → 2025 JO **₹82,018.25**, 2026 JO ₹2,27,218.97.
- **R6-10** (REXP SHORT, full population): fails (c) only. Adoption → 2025 JO **₹94,435.04**, 2026 JO ₹2,19,409.26. (R7-02, R7-03, R8-07 are its nested forms — alternatives, never additive.)
- **R6-02** (NE-REV thr 2.25%): fails (e) only → 2025 JO ₹84,820.98, 2026 JO ₹2,70,438.90. **R6-04** (NE-REV DOWN+FLAT): fails (e) only → 2025 JO ₹78,964.15, 2026 JO ₹2,62,119.13. **R7-06** (quiet-name NE-REV): fails (e) + (f) → 2025 JO ₹82,466.59, 2026 JO ₹2,41,863.31. **R5-07** (birth form): fails (e) + (f) → 2025 JO ₹90,734.58, 2026 JO ₹2,54,002.77.
- NE-REV-family flags (R5-07 / R5-07-CERT / R8-05 / R6-02 / R6-04 / R7-06) are alternatives to each other, never additive; REXP flags (R6-10 / R7-02 / R7-03 / R8-07) are nested forms of one population, never additive; the max stack already contains one form of each family (CERT + R7-03) and is not additive with any single flag.

## Where the 2025 floor can still come from (honest close)
Round 8 banked nothing — and repriced the owner's largest decision from a three-leg refusal to a **one-leg refusal**: the gated max stack (₹1,23,231.11; ₹12,323.11/month) fails only leg (f), on two small months (Jan −₹715.46, Dec −₹99.76 in the variant). Inside the gate, the remaining gap (₹71,579.96) has no Round-8-sized engineering answer left: the follow direction is now dead in its last untested form (drive-continuation), index-state conditioning redistributes NE-REV's failures without removing them, and the REXP family's (c) question exists at two prices, both owner-priced. What remains outside owner decisions is unchanged from Round 7's close: a new data axis (volume / bulk-block / delivery % — none in the workspace), or Nov–Dec forward evidence on the frozen book. The engine's honest statement after eight rounds: every rupee between here and ₹1,21,000+ of 2025 sits behind one or two named gate legs, and the legs are the owner's to waive or Chandu's fresh data to dissolve — the candles have been asked, in gated form, every question this round's workstreams carried.

