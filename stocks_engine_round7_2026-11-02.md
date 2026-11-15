# Stocks (SarvaRitu) Engine — ROUND 7 · REXP-SHORT Repair, Breadth-First Sleeves (Afternoon Reversal, Two-Day Dislocation, Quiet-Name Reversal)
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting book** (Round-6 ending book, causality-audited; re-verified by independent re-sum of the exported CSVs before any Round-7 scoring): 2025 Jan–Oct **+₹78,420.04** (₹7,842.00/mo; gap ₹71,579.96) · 2026 Jan–Oct **+₹2,29,696.21** (₹22,969.62/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict. Timing/admission violations are derived from each construction and asserted in code (lessons R4-L2, R6-L4, Nifty-46) — a cell whose entry uses information not knowable before the entry bar is void on sight.
- **Flagged, NOT adopted** (Chandu's calls; baselines stay on the book without them): R2-26 (clean sheet), R5-03 (fails (e)), R5-07 (fails (e)+(f)), R6-02 (fails (e)), R6-04 (fails (e)), R6-10 (fails (c)), the triple (fails (e)+(f) on its birth book).

## Diagnosis carried in (from Rounds 5–6)
Additions keep failing leg (e) — they concentrate in the book's top-3 carrier names (2025 top-3: OBEROIRLTY ₹30,748.68, ASTRAL ₹14,260.02, GLENMARK ₹8,324.51) — while the genuinely broad addition (R4-03) banked. R6-10 (REXP SHORT) is the book's only (c)-only failure: +₹16,015.00 to 2025 Jan–Oct, −₹10,286.95 to 2026. Round 7 (i) repairs R6-10 by locating its 2026 damage, and (ii) hunts breadth-first constructions whose populations are wide by design.

---

## PRE-REGISTRATION (written before any Round-7 scoring)

### The certified non-event set (R6-11 standard, applied to every Round-7 sleeve)
A stock-day is **certified non-event** only if it is outside ALL of:
1. the frozen R5 contamination set (results reaction windows {R, R+1, R+2} from `reaction_candidates` on both calendars, pooled — the exact R5/R6 set), **and**
2. every calendar row for that stock (any event_type — results, large_order, block_deal, dividend, corporate_action, management_change, fda_approval, sector_policy, pricing): the row's `event_date`; and, when `reaction_date` is present, the `reaction_date` plus the next two trading days of that stock after it; when `reaction_date` is absent (unsourceable), the three trading days after `event_date` (blanket — the reaction day cannot be certified, so the window is excluded whole).
Set sizes and the number of R5-07 population stock-days the strengthening removes are reported in WS2/WS4 before their candidates are read. No substitute definition is invented mid-round.

### WS1 — REXP-SHORT repair (R7-01 audit; R7-02, R7-03 candidates)
Population is R6-10's frozen construction, rebuilt verbatim and re-anchored before scoring (first hour = bars 09:15–10:10, all 12 required; ratio = today's first-hour range ÷ median first-hour range of the previous 20 data-bearing days of the same stock, ≥ 2.0; close position ≤ 0.25 → SHORT; entry at the open of the 10:20 bar; T125/S050 via `replay_plain`, entry bar checked; square-off 15:10; one trade per stock-day; weekend days excluded; **no price levels anywhere**). Anchor: standalone must reproduce R6-10 exactly (2025 +₹14,409.54 / 2026 −₹10,286.95, 237 trades).
- **R7-01 (audit):** decompose R6-10's rows by frozen regime label (REGIME-CLASSIFIER-1, prior-day data only — the gate's own `FL.LABELS`) × year, and by stock for 2026. No candidate is scored in R7-01.
- **R7-02:** the SHORT population restricted to stock-days labelled **DOWN or FLAT**, gated whole-book as an addition (comp `REXP-SHORT`).
- **R7-03:** the SHORT population restricted to **DOWN** days only, gated whole-book — as a swap of the `REXP-SHORT` comp if R7-02 banked, else as an addition.
- Placebos per cell (whole books, identical restricted population): opposite direction (LONG replay on the same stock-days, same entry bar) and same direction one bar later (10:25 open). Timing audit: violations = rows whose entry bar index is not strictly after the 10:10 signal bar's index — counted in code, asserted 0.

### WS2 — NE-REV afternoon variant (R7-04) — NEW TIME POPULATION
- Population: certified non-event stock-days (above), weekend days excluded, at most one trade per stock-day.
- Signal: close of the **13:25** bar vs prior daily close ≤ **−2.00%**. The 13:25 bar completes at 13:30; every input is known at 13:30.
- Entry: **LONG** at the open of the **13:35** bar (the 13:30 bar is skipped, mirroring the morning construction's skip). Exits **T100/S065** via `replay_plain` (entry bar checked), square-off 15:10. ₹40/trade.
- Placebos (whole books, identical population): opposite direction (SHORT) at the same entry bar; same direction one bar later (13:40 open). Timing audit: violations = rows whose entry bar index is not strictly after the 13:25 signal bar's index — counted, asserted 0.

### WS3 — Two-day dislocation reversal (R7-05) — NEW HORIZON
- Signal (known in full before the trade day's open): cumulative two-session move = close[D−1] ÷ close[D−3] − 1 ≤ **−3.00%**, where D is the trade day and D−1, D−2 are the two prior trading sessions of the same stock.
- Certification: D, D−1 and D−2 must all be certified non-event (the set above) — the fall being faded must not be a recorded event reaction on any of its sessions.
- Entry: **LONG** at the open of the **09:20** bar of D (selected by time lookup; stock-days lacking a 09:20 bar are skipped and counted). Exits **T125/S050** via `replay_plain` (entry bar checked), square-off 15:10. At most one trade per stock-day. Weekend days excluded. No hold-to-next-day variant (intraday only, per the book's charter).
- Placebos (whole books, identical population): opposite direction (SHORT) at the same entry bar; same direction one bar later (09:25 open). Timing audit: the signal uses only closes of sessions strictly before D; violations = rows whose entry bar is not the 09:20 bar or later — counted, asserted 0.

### WS4 — Quiet-name NE-REV (R7-06)
- Base construction: the morning NE-REV exactly as frozen in R5-07 (signal: close of the 10:25 bar vs prior close ≤ −2.00%; entry LONG at the open of the 10:35 bar; T100/S065 via `replay_plain`; square-off 15:10; one trade per stock-day) on the **certified** population (the R6-11 strengthening above supersedes the R5 population for this new sleeve; the population delta vs R5-07 is reported before the verdict is read). Anchor: the unreconstructed R5-07 builder must first reproduce its recorded standalone (+₹12,209.45 / +₹24,306.56; 303/388 rows).
- Quiet filter (the only addition): for trade day D, each name's characteristic = the median of its daily range% over the **trailing 20 sessions strictly before D**, range% = (high − low) ÷ close × 100 from daily bars. The watchlist median for D = the median of the 25 names' characteristics (names with fewer than 20 trailing sessions are excluded from that day's cross-section and cannot trade). A name trades only if its characteristic is **strictly below** D's watchlist median. Every input is trailing daily data — no return-based ranking anywhere (the R6-06 causality ruling stands).
- Placebos (whole books, identical restricted population): opposite direction (SHORT) at 10:35; same direction one bar later (10:40). Timing audit as in WS1/WS2 (entry strictly after the 10:25 signal bar), counted, asserted 0.
- The question this cell answers: does breadth-by-construction cure leg (e)?

### WS5 — Combinations + decision state (R7-07, R7-08)
- Any two or more Round-7 bankings are combined and re-gated whole-book (R7-07). If fewer than two bankings exist, WS5 closes by statement.
- R7-08 (finalise, decision support): ending books exported and independently re-summed; every flagged variant's adoption value restated on the ending book (R6-L5 discipline — overlaps with any Round-7 banking netted by (date, stock, entry_time) keys, method stated); state updated. Nothing in R7-08 is banked.

### Verdict rule (frozen for all Round-7 candidates)
Each candidate is gated whole-book per year under the nine-leg gate + leg (x). A candidate passing ALL legs banks. A candidate failing any leg is recorded with its failing legs named; near-misses join the flagged list as owner decisions — the engine adopts nothing on Chandu's behalf.

*(End of pre-registration. All sections below are written after scoring.)*

---

## R7-01 — REXP-SHORT decomposition (audit): the 2026 damage lives in the DOWN cell
R6-10's population rebuilt verbatim and re-anchored exactly (standalone +₹14,409.54 / −₹10,286.95; 237 trades; timing violations 0). Jan–Oct decomposition by frozen regime cell:

| Cell | 2025 trades | 2025 net | 2026 trades | 2026 net |
|---|---|---|---|---|
| DOWN | 41 | **+₹14,870.39** | 86 | **−₹8,399.33** |
| FLAT | 9 | −₹2,717.22 | 17 | −₹2,530.85 |
| UP | 43 | +₹3,861.83 | 21 | +₹643.23 |

2026 by stock (worst first): TVSMOTOR −₹5,389.25 (3 tr) · GODREJCP −₹3,380.55 (6) · ASTRAL −₹3,133.20 (4) · UNITDSPR −₹2,503.10 (7) · KALYANKJIL −₹1,735.87 (10) · PFC −₹1,103.73 (8) · HINDALCO −₹1,046.90 (2) · RECLTD −₹977.51 (8).

**The damage is not where the book's other repairs found theirs.** NE-REV's flip lived in UP cells and the fade's 2026 damage lived in UP cells; REXP-SHORT's 2026 damage lives in the **DOWN cell itself** — the identical construction earns +₹14,870.39 on 2025's DOWN days and loses −₹8,399.33 on 2026's. This is Lesson 47's signature inside a single cell: the two tapes disagree about what a range-expansion bottom-quartile close means on a down-regime day, and no cell restriction can separate them, because every restriction keeps DOWN.

## WS1 — REXP-SHORT repair (R7-02, R7-03): both restricted forms fail leg (c) alone
| Cycle | Form | Trades 25/26 | Standalone 2025 / 2026 | 2025 JO → | 2026 JO → | Failed legs |
|---|---|---|---|---|---|---|
| R7-02 | DOWN+FLAT cells | 50 / 103 | +₹12,153.17 / −₹10,930.18 | **₹90,573.21** | ₹2,18,766.03 | **(c) only** |
| R7-03 | DOWN cells only | 41 / 86 | +₹14,870.39 / −₹8,399.33 | **₹93,290.43** | ₹2,21,296.88 | **(c) only** |

Both forms pass every other leg — halves, cells, ex-top-3 (2025 ex-top-3 rises to ₹35,282.90 / ₹38,000.12), placebos beaten, no flips, timing clean. The restriction cannot repair the (c) failure because it removes the UP cell's +₹643.23 (R7-02 is *worse* for 2026 than the full population) while keeping the damaged DOWN cell whole. **R7-03 dominates R7-02 on both years** and is the largest single-sleeve 2025 delta on the flagged list (+₹14,870.39) at the REXP family's smallest 2026 cost (−₹8,399.33; 2026 JO stays at ₹2,21,296.88, far above its floor). Both join the flagged list as owner decisions — the (c)-leg question is unchanged from R6-10: whether 2026 may pay a bounded amount for a 2025 phenomenon while staying above its own floor.

## WS2 — NE-REV afternoon (R7-04): REJECTED on seven legs — the reversal is a morning phenomenon
Certified population: 11,958 stock-days, 963 signal days, 963 trades (462 in 2025, 501 in 2026). Standalone **−₹37,819.07 (2025)** / +₹10,059.27 (2026); 2025 JO → ₹44,183.07; combined book falls; beaten by its placebos; Jan and May 2025 flip. The identical dislocation measured at 13:25 does not revert in the weak year — afternoon dumps continue into the close. Not flagged (seven legs is not a near-miss). The NE-REV phenomenon is specific to the morning measurement: a dump priced against the open's information state, not against midday's.

## WS3 — Two-day dislocation reversal (R7-05): REJECTED on eight legs — two-day falls continue
1,189 signal days; 212 skipped for a missing 09:20 bar (late-starting days, counted per the pre-registration); 977 trades. Standalone **−₹62,345.49 (2025)** / **−₹43,694.93 (2026)** — negative in both years, beaten by both placebos, four month flips across the two years. A ≥3% two-session fall is a trend state on these tapes, not a reversal setup: stretching NE-REV's horizon from one morning to two sessions destroys the phenomenon entirely. Not flagged. The reversal family is now bounded on both sides: same-day morning only (R5-07 class), not afternoon (R7-04), not multi-day (R7-05).

## WS4 — Quiet-name NE-REV (R7-06): REJECTED on (e) + (f) — breadth by construction does not cure leg (e)
Anchors first, as pre-registered: R5-07 reproduced exactly (+₹12,209.45 / +₹24,306.56; 303/388 rows). The certified population (843 stock-days excluded vs the R5 set's 539; +304 event-day exclusions) removes 30 of R5-07's 691 population rows — and the certified morning NE-REV standalone is **higher in 2025 (+₹14,105.64)** and nearly unchanged in 2026 (+₹24,112.86) on 661 rows: the uncertifiable rows were net losers in the weak year.

The quiet filter kept 196 of 661 signal days (77 trades in 2025, 119 in 2026). Standalone +₹4,492.57 / +₹12,167.10 — positive in both years, combined book rises to ₹3,23,397.19, placebos beaten. **It still fails leg (e)**: the variant book's combined ex-top-3 *falls* ₹1,01,181.87 → ₹89,033.84 (2025's own ex-top-3 also falls, ₹23,708.10 → ₹22,640.60, despite the positive standalone) — the sleeve's gains land in the book's carrier names (names quiet by trailing range are not disjoint from the carriers), and once a name is in the variant's top-3 its sleeve gains are exactly what leg (e) removes. It also flips Jan 2025 (+₹2,200.31 → −₹1,790.60). **Answer to the pre-registered question: no** — breadth-by-construction does not cure (e), because (e) is a whole-book interaction, not a property of the sleeve's own population (lesson R7-L4). Flagged as an owner decision.

## WS5 — Combinations (R7-07)
Zero bankings in Round 7; there is no combination to re-gate. Closes by statement.

## R7-08 — Decision support: R5-07 repriced on the certified population
The R5-07 flag rebuilt on the certified non-event set and gated whole-book as decision support (force_no_bank): 2025 JO → **₹92,537.28** (delta +₹14,117.24), 2026 JO → **₹2,53,809.07** (delta +₹24,112.86), combined ₹3,44,956.02, placebos beaten — fails **(e) + (f)** (Jan 2025 +₹2,200.31 → −₹750.61; Dec 2025 +₹1,207.95 → −₹632.67). The certified form is worth **more** to 2025 than the flag's birth form (+₹14,117.24 vs +₹12,314.54 of Jan–Oct delta) with the same two failing legs. If Chandu adopts NE-REV at all, the certified form is the one the current causality standard prices.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹78,420.04** = **₹7,842.00/month** · **gap to floor ₹71,579.96 (unchanged — Round 7 banked nothing)** · full-year +₹77,041.31 · 887 trades · ex-top-3 stocks **+₹23,708.10** (top-3: OBEROIRLTY ₹30,748.68, ASTRAL ₹14,260.02, GLENMARK ₹8,324.51).
Months: Jan +₹2,200.31 · Feb +₹20,242.66 · Mar +₹8,953.57 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹7,083.39** · Aug +₹11,173.48 · Sep +₹5,585.44 · **Oct −₹3,944.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹73,644.96 · H2 +₹4,775.08.
Regime cells (full-year): DOWN +₹42,941.63 · FLAT +₹21,250.68 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · GAP-FADE +₹21,470.27 · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹5,851.63 · GAP-FADE-INC +₹2,305.22 · F4 +₹91.14 · R2-LOWBAND −₹116.75 · INV-R3 −₹230.42 · P2F-R2 −₹390.06.

### 2026 — floor MET
Jan–Oct **+₹2,29,696.21** = **₹22,969.62/month** (₹79,696.21 above the floor line) · 969 trades · all ten months green (Jan +₹29,518.32 … Oct +₹63,740.90) · ex-top-3 stocks +₹77,473.77.
Regime cells: DOWN +₹2,10,264.94 · FLAT +₹2,909.78 · UP +₹16,521.49.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹29,562.32 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · GAP-FADE-INC +₹4,763.03 · INV-ABOVE +₹3,349.21 · GAP-FADE +₹1,492.21 · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r7_book2025_trades.csv`, `stocks_engine_r7_book2026_trades.csv` (exported from the ending incumbent — identical to the Round-6 books — and independently re-summed to the paisa). Evidence: `r7_results.json` (8 records: 5 gated candidates, 2 audits, 1 decision-support gate). Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R7-L1…R7-L5). State: `stocks_engine_state.json` (`round7_summary`).

## Decision state after Round 7 (owner's calls, none taken by the engine — all restated on the ending book, per R6-L5)
- **R2-26** (INV-ABOVE T150/S080): clean sheet. Adoption → 2025 JO **₹85,954.04**, 2026 JO ₹2,33,818.54.
- **R5-03** (gap-fade thr 1.25% swap): fails (e) only. Clean adoption (retiring GAP-FADE-INC) → 2025 JO **₹86,709.48**, 2026 JO ₹2,27,711.39.
- **R5-07** (NE-REV LONG, R5 population): fails (e) + (f). Adoption → 2025 JO **₹90,734.58**, 2026 JO ₹2,54,002.77.
- **R5-07-CERT** (NE-REV LONG, certified population — R7-08): fails (e) + (f). Adoption → 2025 JO **₹92,537.28**, 2026 JO ₹2,53,809.07. The current standard's form of the same flag; worth +₹1,802.70 more to 2025 than the birth form.
- **R6-02** (NE-REV thr 2.25%): fails (e) only. Adoption → 2025 JO **₹84,820.98**, 2026 JO ₹2,70,438.90.
- **R6-04** (NE-REV DOWN+FLAT): fails (e) only. Adoption → 2025 JO **₹78,964.15**, 2026 JO ₹2,62,119.13.
- **R6-10** (REXP SHORT, full): fails (c) only. Adoption → 2025 JO **₹94,435.04**, 2026 JO ₹2,19,409.26.
- **R7-02** (REXP SHORT, DOWN+FLAT): fails (c) only. Adoption → 2025 JO **₹90,573.21**, 2026 JO ₹2,18,766.03. Dominated by R7-03.
- **R7-03** (REXP SHORT, DOWN only): fails (c) only. Adoption → 2025 JO **₹93,290.43** (₹9,329.04/mo), 2026 JO ₹2,21,296.88.
- **R7-06** (quiet-name NE-REV): fails (e) + (f). Adoption → 2025 JO **₹82,466.59**, 2026 JO ₹2,41,863.31.
- **The triple (R2-26 + R5-03 + R5-07)**: restated arithmetically (unchanged) → 2025 JO **₹1,06,558.02 (₹10,655.80/month), gap ₹43,441.98**, 2026 JO ₹2,56,140.28. (With R5-07 in its CERT form instead of the birth form, the same arithmetic gives 2025 JO ₹1,08,360.76 — restatement of a restatement; quoted here once, not carried as a separate flag.)
- **Max stack (triple + R7-03)**: arithmetic restatement (NOT a gated combination) → 2025 JO **₹1,21,428.41 (₹12,142.84/month), gap ₹28,571.59**, 2026 JO ₹2,47,740.95 — the closest 2025 has come to the floor. Its components carry their own failing legs: (e) + (f) from the triple's birth book, (c) from R7-03. NE-REV-family flags (R5-07 / R5-07-CERT / R6-02 / R6-04 / R7-06) are alternatives to each other, never additive; REXP flags (R6-10 / R7-02 / R7-03) are nested subsets, never additive.

## Where the 2025 floor can still come from (honest close)
Round 7 banked nothing and moved the book not one paisa — and it was not an idle round: it located R6-10's damage exactly (inside the DOWN cell, where no restriction can reach it), bounded the reversal phenomenon on both sides (morning only; one session only), answered the breadth question in the negative with a clean construction, and repriced the largest flag under the current causality standard at a *higher* value than its birth price. The 2025 gap (₹71,579.96) now sits almost entirely in owner decisions: the flagged list carries the triple (₹1,06,558.02), R7-03 (+₹14,870.39, disjoint), and the max stack at ₹1,21,428.41 — every rupee of it refused by one or two named legs, none of them the floor leg itself. Outside owner decisions, the remaining routes are unchanged and were not advanced this round: a new data axis (volume / bulk-block / delivery % — none in the workspace; the carrier-exclusion repair still waits on a causal 2024 book), or Nov–Dec forward evidence on the frozen book. Seven rounds in, the in-sample candle set has now been asked the reversal question at three horizons, the expansion question in three cell forms, and the breadth question by construction — the marginal in-sample question is getting thinner, and the report says so rather than manufacturing one.
