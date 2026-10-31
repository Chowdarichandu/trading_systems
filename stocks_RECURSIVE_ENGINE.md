# THE RECURSIVE ENGINE — stocks, Chandu's 25 (built 2026-10-31; amended same day on his correction)

His words: "you need to loop identify — it's a recursive engine you need to build. Identify, fix, apply, fix, apply… recursing until we met something break even." And: a cycle should complete in minutes and recurse IMMEDIATELY — no slow schedule. And: **first fix October.**

## Month order (his method)
**October first** (goal: October ≥ +₹50,000), then **September**, then August, July … January — each month in turn becomes the target: diagnose why it is weak/red, fix, apply, and move on only when it is secured (positive; for October, at the ₹50k goal). Every later fix is re-checked against ALL previously secured months — a fix that un-secures a secured month is rejected.

## The loop (one cycle — minutes, back-to-back, no waiting)
1. **IDENTIFY** — read `stocks_engine_state.json`. Target = the current month in the order. Diagnose its weakness from the working book's trades, with numbers.
2. **FIX** — ONE rule-fix from the diagnosis: ex-ante, applies to all months, never a date filter or per-month parameter, not in the tried-families registry. Freeze in `stocks_engine_frozen.md` BEFORE scoring.
3. **APPLY** — rebuild the full book Jan–Oct 2026 (audited engines, timing audit asserted in the same pass).
4. **DECIDE (banking rule)** — ACCEPT and bank the fix if it improves the target month AND breaks nothing (no secured month un-secured, no month pushed below −₹12,000, total does not fall, audit clean, activity sane) — **even if the improvement is partial.** A red month improved is progress banked; the recursion continues on the residual. REJECT only if it breaks something or doesn't improve the target. Record every family + outcome in the registry; append the cycle to `stocks_engine_log.md`; update the state.
5. **RECURSE immediately** — the next cycle starts from the new state at once. A 15-minute watchdog schedule exists only to restart the chain if it ever stalls; it must check `cycle_lock` in the state and skip if a fresh cycle is already running.

## Saturation run (user order, 2026-10-31 12:10 IST — supersedes the freeze and the 2-cycle break-even)
Run the engine AGAIN, non-stop, until it **saturates**: a cycle "beats" the best book only if the total rises AND all ten months stay green AND October ≥ ₹50,000. The run ends when **3 consecutive cycles fail to beat the best** — that plateau is the system's ceiling on this data, and it is reported with the full climb (every banked step and its gain) and the plateau evidence. The October peak lab runs the same logic on October alone.
**Goal (user, 2026-10-31 12:13 IST): ₹75,000/month average = ₹750,000 over Jan–Oct.** The saturation plateau is reported against this line: if the run saturates below it, the report states the plateau, the gap, and which mechanism families remain untried — it does not stop early because the goal looks far.

## Termination
- **SUCCESS:** October ≥ ₹50,000 AND all 10 months positive → freeze `stocks_engine_candidate_spec.md` (December judging), terminated = "SUCCESS", final report.
- **BREAK-EVEN:** all 10 months ≥ 0 (October secured short of ₹50k) and 2 consecutive cycles bank nothing → terminated = "BREAK_EVEN", final report.
- **EXHAUSTED:** 3 consecutive cycles bank nothing while the current target month is still red → terminated = "EXHAUSTED", final report naming the resisting month and every diagnosis.
- The user saying stop ends it at any time.

## Self-improvement charter (user, 2026-10-31 — "RSI" = Recursive Self Improvement)
The engine does not only patch the incumbent book. It **learns from its mistakes and builds new systems**:
- Every cycle starts by reading `stocks_engine_lessons.md` and ends by appending any lesson a controlled run just proved.
- When a target month stalls (2 consecutive cycles bank nothing on it) — or every 3rd cycle, whichever comes first — the cycle must **BUILD A CHALLENGER SYSTEM** from the lessons: a new assembly or mechanism consistent with every lesson and contradicted by none, frozen in `stocks_engine_frozen.md`, scored under the full controls (timing audit, placebo, halves, month table, ex-top-3 stress).
- A challenger replaces the incumbent only on the frozen gate: more green months first, then higher total, with secured months (and October's ₹50k floor) intact. Otherwise it is recorded as a rejected version with its lesson.

## Hard guards (from the 2026-10-31 fake-data failure)
Controls + leak audit in the same pass as any scoring; no number reported before they pass; one structural change per cycle; definitions frozen before scoring; paper only, real ₹0, provisional per 100 shares, ₹40/trade; equity cash LONG/SHORT only, no options; home 25 only.

---

## v2 CHARTER — cross-year method (amended 2026-10-31 on the user's order, after the 2025 validation)

The user's verdict on the v1 book (2026-10-31 14:58 IST): **"then system is wrong"** — accepted in substance (Lesson 26): the v1 book is a single-regime fit. His order: **"Start then self improvement"** — the engine restarts as v2 on the cross-year method. Everything below supersedes the v1 sections wherever they conflict (in particular the v1 month order and the v1 termination states no longer apply).

### (a) Windows — two years, both scored every cycle
- **Window 2025:** Jan–Dec 2025 (full year, 12 months).
- **Window 2026:** Jan–Oct 2026 (the v1 window, kept verbatim as the in-sample anchor).
- **Both windows are scored in every cycle, in the same run.** No cycle may report, diagnose, or bank from one window alone.
- Data: 2025 runs use the validation-corrected dataset (Sep-2025 fills for ASTRAL/BDL/HINDUNILVR/OIL and Q4-2024 daily lookback for real 50DMA gates from 2025-01-01), persisted at `~/workspace/trading/data/full_hist/`; the 2025 event/reaction calendar is `stock_event_calendar_2025.csv`, built with the identical construction as the 2026 file (same schema, same judgement fields, same effective-reaction-date rule: after-market announcement → next trading day).

### (b) The cross-year gate — the only banking rule in v2
A fix is **banked only if**, on the combined book scored over both windows in the same run:
1. the **combined total rises** (2025 + 2026 together), **AND**
2. **neither year's total falls**, **AND**
3. **neither year is negative at book level** in the resulting book.
A component may be year-specialised — live in one year only, or pulling opposite weight across years — **only if the other components keep that year positive**. The gate arithmetic (before/after per year and combined) is **stated in the log every cycle**, pass or fail. A change that lifts only one year while the other falls is a photograph-improver, not a system improvement, and is rejected on the record.

### (c) v1 disciplines carry over, unchanged
- Controls + timing/leak audit **in the same pass** as any scoring; no number is quoted before they pass.
- The fix is **frozen in `stocks_engine_frozen.md` BEFORE scoring**.
- **One structural change per cycle.** Definitions are never re-tuned on the window that judges them.
- Lessons are **read first** (start of cycle) and **appended after** (end of any cycle that learns something).
- Exclusions stay **mechanism-scoped** (name × direction slices with a stated reason — never date filters, never per-month parameters).
- **Ex-top-3 stress is reported per year** (Lesson 6), beside every total; per-year month tables are reported for both years.
- Paper only, real ₹0, provisional per 100 shares, ₹40/trade; equity cash LONG/SHORT only, no options; his 25 stocks only.
- Diagnosis in v2 is **per component × year** on the combined book: the target is the weakest cross-year point (the component whose worse year is weakest), not a single month.

### (d) Saturation (v2)
Saturation = **3 consecutive cycles that cannot beat the combined best under the cross-year gate**. Until then, cycles run back-to-back in minutes (the user's standing cadence order). The ₹75,000/month goal is measured on the combined book's monthly average across the 22 book months (12 of 2025 + 10 of 2026).

### v2 incumbent
The frozen v1 book, verbatim, over both windows: 2026 exact **+₹197,607.74** (663 trades) plus the 2025 full-book score with all six components runnable (2025 calendar built 2026-10-31, `stock_event_calendar_2025.csv`): **2025 = 636 trades / +₹23.06** (five red months; ex-top-3 −₹27,814.95) → **v2 incumbent combined = +₹197,630.80 over 22 months = ₹8,983.22/month** against the ₹75,000/month goal. After **v2 Cycle 1 (BANKED** — GLENMARK × SHORT excluded from the same-day follow components F4 + N4-V3): **combined best = +₹204,004.23** (2025 +₹5,765.30 · 2026 +₹198,238.93; ₹9,272.92/month). That combined book is the number every v2 cycle must beat under the gate. Per-cycle state lives in `stocks_engine_state.json` (v2 block) and the v2 section of `stocks_engine_log.md`.

### (e) AMENDMENT — the per-year floor (user mandate, 2026-10-31 15:17 IST)
His words: **"Whenever I increase the time, you are reducing the profit. Profit should not be reduced. 20,000 per month should be default."** Operational form, on the record:
- **The engine's success bar is now per-year: 2025 ≥ ₹240,000 (₹20,000 × 12) AND 2026 ≥ ₹200,000 (₹20,000 × 10).** Every window must stand on its own; a strong year may no longer subsidise a weak one in the headline. The combined figure and the 22-month average are still reported, but they are no longer the bar.
- Position at the mandate (post-Cycle-1): 2025 +₹5,765.30 (gap ₹234,235) · 2026 +₹198,238.93 (gap ₹1,761). Position when folded into the log (post-Cycle-2 bank, Cycle-3 challenger rejected): 2025 +₹8,310.30 (gap ₹231,690) · 2026 +₹198,878.93 (gap ₹1,121).
- The engine keeps cycling under the cross-year gate toward the floor. Challenger cadence applies with the aim corrected: **challengers are aimed at the weak year** (2025 is the gap; its seed material is what worked there — P2F +₹14,365.77 and INV-LONG +₹7,642.52, the two cross-year survivors).
- **Saturation (3 consecutive no-beat cycles) remains the honesty backstop:** if the engine saturates below the floor, the proven ceiling is reported plainly, per year, against the floor — the gate is NEVER loosened, the floor NEVER re-defined, and no number is inflated to reach it.
- The ₹75,000/month goal stays the horizon above the floor.

### (f) AMENDMENT 2 — regime completeness + consistency band (user mandate, 2026-10-31 15:30 IST)
His words: build a system that generates a consistent amount **±₹1,000** regardless of market movement — deep falling (profit via the SHORT side — equity cash shorting is this book's falling-market instrument), steep rising (LONG side), flat (event-driven / fade sleeves) — **"any situation we need to be ready."** Operational form, on the record:
1. **Frozen causal regime classifier** — defined once, frozen in `stocks_engine_frozen.md` (REGIME-CLASSIFIER-1) BEFORE any regime scoring: every trading day is classified by NIFTY trend state from price vs 50DMA and the 50DMA slope, all inputs known at the PRIOR close. No same-day information in any label, ever.
2. **Regime cells are a unit of diagnosis alongside months** — every cycle from Cycle 22 onward reports the book's P&L by regime cell × year (UP / DOWN / FLAT × 2025 / 2026). A cell negative in either year is a named weakness, ranked like a red month.
3. **Objectives, in order:** (a) every regime cell positive in BOTH years; (b) the ₹20,000/month per-year floor (Amendment (e)); (c) **variance compression toward ₹20,000 ± ₹1,000 per month** — the month-to-month spread is an explicit reported metric every cycle. Fixes that lift the weakest cell/month are preferred over fixes that fatten the strongest.
4. **Sleeve building:** when a regime cell lacks an earner, the challenger cadence targets THAT cell — downtrend sleeve = SHORT-side mechanisms, uptrend = LONG, flat = event-driven (the P2F family is the proven flat-capable seed) and fade-type mechanisms.
5. **All existing gates unchanged** — the cross-year gate, controls + timing audit in the same pass, freeze before scoring, one structural change per cycle. **Honesty backstop unchanged:** the ±₹1,000 band is an optimisation target reported against openly at every milestone; if a cell or the band proves unreachable on this data, that is stated with the cell evidence — never smoothed, cherry-picked, or gate-loosened into existence.

---

## v3 CHARTER — MAXIMIN TUNING (user order 2026-10-31 20:55 IST)

His words: **"start tuning them because at least ten thousand should be the minimum. For stocks."** The v2 run optimised totals and averages; the user rejected the average as the standard (it hid the weak months — 2025 averaged ₹2,290/month while six of its months were red). v3 tunes the book **SarvaRitu** (the frozen post-C24 v2 book) under a **maximin** objective. Everything in the v2 charter not explicitly superseded below carries over (cross-year windows, controls + timing audit in the same pass, freeze before scoring, one structural change per cycle, lessons read first / appended after, mechanism-scoped exclusions, challenger cadence, paper only / real ₹0 / per 100 shares / ₹40 per trade / equity cash LONG-SHORT / home 25).

### (a) The objective — lexicographic maximin over the 22-month vector
- The book's **month vector** = the 22 monthly nets (Jan–Dec 2025 + Jan–Oct 2026), sorted ascending.
- **Primary target: raise the WORST month toward ≥ +₹10,000** (the user's minimum). Incumbent bottom: Oct 2025 −₹5,149.95 · Jul 2025 −₹5,088.45 · Nov 2025 −₹4,545.69 · Mar 2025 −₹3,124.15 · May 2025 −₹2,779.66 · Jun 2025 −₹955.92 · Jul 2026 +₹8,486.54 · Jun 2026 +₹9,641.38 · Aug 2026 +₹9,678.06.
- **Beat criterion:** a cycle beats the incumbent iff the sorted month vector **lexicographically improves** (worst month up; on a tie, the second-worst up; and so on), subject to the hard constraints in (b). The bottom-5 months are reported every cycle.
- **Beyond the minimum:** once the worst month clears +₹10,000, keep lifting the bottom toward **₹15,000** (the floor of the user's ₹15,000–₹20,000/month acceptance band, set 2026-10-31 20:50 IST).

### (b) Hard constraints — any violation is a reject, whatever the maximin gain
1. **Neither year's total falls; neither year is negative** (the cross-year gate's year legs, kept verbatim).
2. **Every regime cell (REGIME-CLASSIFIER-1 × year) stays positive** (mandate 2 objective (a), held as a constraint).
3. **Combined total does not fall.**
4. Controls + timing audit **in the same pass** as every score; the fix is **frozen before scoring**; **one structural change per cycle**; challenger cadence per the v2 charter. Additive challengers additionally carry the standing Cycle-6 standard: combined expectancy > 0 AND beats the flip placebo per-trade.
5. **The frozen SarvaRitu forward test is untouched:** v3 tunes on history only; the frozen book, `stocks_sarvaritu_forward_spec.md` and its logger are never modified by a v3 cycle. Anything v3 banks is a NEW version, for a later fresh test — it is never retro-fitted into the running test.

### (c) Material
The weak months are **quiet / low-activity months** (Jun 2025 carried 7 trades). The lessons bind the search: price-derived level events are information-free on his 25 (Lesson 2 — L1 closed); the home-25 fade was flat; the reaction (band × lag) grid is closed outside its living cells (Lessons 20–24); exit axes are settled per population (Lessons 31/33/34). The honest hunting ground is **information-based breadth**: additional event classes in the two calendars' spirit (dividends/record dates, buybacks, bulk/block deals, index events), variants of the proven earners (P2F / INV family structures), and the recorded untested queue (**INV-R3** below-trend, **INV-ABOVE-R3**). Every challenger must state which weak month(s) it targets and why it would have traded there.

### (d) Saturation (v3)
Saturation = **3 consecutive cycles that fail the maximin beat under the hard constraints** → terminated = "SATURATED-V3", reported with the final bottom-5 and the full climb. Milestones reported as they occur: worst month crossing ₹0, worst month crossing +₹10,000. The ₹75,000/month goal and the ₹20,000/month per-year floor remain the horizons above this objective; neither is redefined by it.

### (e) THE ONE-ROOF RULE (user order 2026-10-31 20:59 IST — "All stocks strategies under one roof")
**SarvaRitu is the single umbrella for ALL stocks work on his 25.** The registry is `stocks_sarvaritu_roof.md`. A new stocks strategy joins the roof **only as a SarvaRitu component, through this engine's gate** — controls + timing/leak audit in the same run as its first scoring, the cross-year gate, and the maximin constraints of (b); there is no other door. A standalone stocks experiment must be **registered as a CANDIDATE in `stocks_sarvaritu_roof.md` before any scoring**; an unregistered experiment's numbers do not exist as far as the roof is concerned. Killed lines are recorded CLOSED in the registry with their one-line cause and are re-opened only on the fresh-evidence condition the lessons record. Pooled-universe and ext-universe work (e.g. T2 P2F 3.0%, the O2 fade) stays OUTSIDE the roof under his scope rule and is registered as outside, with the reason.
