# Stocks (SarvaRitu) Engine — ROUND 4 · Combined Flags, Gap-Fade Refinement, Volume Audit
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026.**

- **Starting book** (Round-2 ending book, re-verified by independent re-sum): 2025 Jan–Oct **+₹56,336.30** (₹5,633.63/mo; gap ₹93,663.70) · 2026 Jan–Oct **+₹2,21,801.13** (₹22,180.11/mo; floor MET).
- **Gate:** the frozen nine-leg session gate **plus leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** inside every verdict.
- **Ending book:** 2025 Jan–Oct **+₹77,806.57** (₹7,780.66/mo; **gap ₹72,193.43**) · 2026 Jan–Oct **+₹2,23,293.34** (₹22,329.33/mo; floor MET). **One banking (R4-03).**

## The failure, first: R4-07's banking was VOIDED on the timing audit
The entry-axis cell "entry at the 09:15 open" (entry_bar 0) initially passed the gate with a sleeve standalone of +₹67,392.17 (2025) / +₹22,054.04 (2026) and was banked by the script on the harness's default `timing_violations=0`. **That default was wrong for this cell, and the banking does not stand.** The sleeve's signal *is* the gap, and the gap is defined as bar-0's open ÷ prior close — so a fill at bar-0's open is a fill at the very print that first reveals the qualifying information: entry before the information existed, on **all 390 sleeve trades**. The bar-0 "improvement" over the honest 09:20 sleeve (+₹41,226.62 in 2025, +₹26,134.80 in 2026, standalone) is the first-bar snap-back harvested at the signal print — the look-ahead signature this engine exists to refuse. The void was recorded the same run (record `R4-07-VOID` in `r4_results.json`), the incumbent was reverted to the R4-03 book and re-asserted to the paisa, and the two cells that had been gated against the voided base (09:35 entry, T150/S080 exits) were **re-run against the corrected base** as R4-08R / R4-09R — both rejected. The open-entry convention remains legitimate only where the signal is fully known *before* the open (the reaction families enter at 09:15 on prior-day information); a gap-defined signal completes at the open itself, so its earliest honest entry is the next bar. **No number from R4-07 is used anywhere in this report's book.**

---

## WS1 — Combined flags, gated whole (R4-01) — decision support
Both ingredients were re-anchored against the current base to the paisa before the combination was scored (R2-26: 2025 JO +₹7,534.00, combined +₹13,089.83 · R3-10: 2025 JO +₹26,979.39, 2026 JO −₹4,080.76, combined +₹22,084.79 — all reproduced exactly). The two variants touch disjoint components (an INV-ABOVE exit swap; an added sleeve), and the combination is **exactly additive**:

| | 2025 Jan–Oct | 2026 Jan–Oct | Gate combined (2025 full + 2026) |
|---|---|---|---|
| Base | ₹56,336.30 | ₹2,21,801.13 | ₹2,76,758.70 |
| R2-26 + R3-10 together | **₹90,849.69** | **₹2,21,842.70** | **₹3,11,933.32** |

The additive 2025 figure is the brief's expected ₹90,849.69 to the paisa. The non-obvious line is 2026: it **rises +₹41.57**, because R2-26's 2026 gain (+₹4,122.33) cancels the fade sleeve's 2026 loss (−₹4,080.76) almost exactly.

**Combined-flags gate sheet** (placebos pre-registered: P1 both changes in placebo form ₹2,24,482.60 · P2 R2-26 + fade one bar late ₹2,72,712.83 · P3 placebo swap + fade one bar late ₹2,44,083.03 — the variant's ₹3,11,933.32 beats all three):

| Leg | Result |
|---|---|
| (a) combined rises | ✅ ₹2,76,758.70 → ₹3,11,933.32 |
| (b) 2025 no fall (total + Jan–Oct) | ✅ |
| (c) 2026 no fall | ✅ **+₹41.57** — the cross-year objection to R3-10 disappears inside the combination |
| (d) all 3 regime cells × year positive | ✅ (2025: DOWN ₹42,688.79 / FLAT ₹24,325.79 / UP ₹23,076.04 · 2026: DOWN ₹2,02,017.65 / FLAT ₹6,135.29 / UP ₹13,689.76) |
| (e) ex-top-3 | ❌ combined ex-top-3 ₹97,451.29 → ₹96,119.41 — the full sleeve's 2026 gains concentrate (2026 ex-top-3 ₹87,675.53 → ₹71,201.56) |
| (f) no green month flips red | ❌ May 2025 +₹2,498.99 → **−₹2,019.04**; Dec 2025 +₹1,207.95 → **−₹345.69** (both flips are the fade sleeve's; R2-26's own Mar-2025 flip does **not** occur in the combination — March stands at +₹3,664.62, see R4-10) |
| (g) no half flips | ✅ |
| (h) beats placebos | ✅ (all three pre-registered placebos beaten) |
| (i) timing audit clean | ✅ |
| (x) 2026 ≥ ₹1,50,000 | ✅ ₹2,21,842.70 |

**Verdict: fails exactly legs (e) and (f).** Recorded as decision support only — neither flag was adopted by the engine. Note what the sheet does to the owner's decision: the combination's surviving objections are the full sleeve's concentration and its two month flips — and WS2 below banked a *refined* form of that same sleeve which has neither problem.

## WS2 — Gap-fade LONG refinement (the round's prize, banked)
Base form = R3-10 (fade LONG-only, ≥1.5%, entry 09:20, T125/S050). One axis at a time; placebos per cell = the mirror population (follow-SHORT on the same gap-down days, identical parameters) and the same cell one bar late. Cells that swap the sleeve were gated against the then-incumbent.

| Cycle | Cell | 2025 JO Δ | 2026 JO Δ | Failed legs | Verdict |
|---|---|---|---|---|---|
| R4-02 | Regime: DOWN days only | +₹3,462.79 | +₹5,823.56 | (e) only | REJECTED — one leg short |
| **R4-03** | **Regime: DOWN+FLAT days** | **+₹21,470.27** | **+₹1,492.21** | **none — all 10 pass** | **BANKED** |
| R4-04 | Threshold 2.0% (swap) | −₹2,304.84 | −₹9,985.37 | a, b, c, e, f | REJECTED |
| R4-05 | Threshold 2.5% (swap) | −₹7,215.85 | −₹2,821.56 | a, b, c, f | REJECTED |
| R4-06 | Threshold 3.0% (swap) | −₹3,395.39 | −₹5,213.88 | a, b, c | REJECTED |
| R4-07 | Entry 09:15 open | — | — | **(i) timing — 390 violations** | **VOID (see above)** |
| R4-08R | Entry 09:35 (swap, corrected base) | −₹27,613.47 | −₹40,792.90 | a, b, c, d, e, f, h | REJECTED |
| R4-09R | Exits T150/S080 (swap, corrected base) | +₹8,291.90 | −₹14,122.08 | c, e, f | REJECTED |

Why R4-03 banks where R3-10 could not: the fade's 2026 damage was located by cell — UP **−₹5,572.97**, FLAT −₹4,331.35, DOWN +₹5,823.56 (book deltas of the full sleeve). Excluding the UP cell removes the cross-year loss entirely (2026 Δ turns +₹1,492.21) and keeps May/Dec 2025 intact (no flips). DOWN-only (R4-02) repaired the cross-year leg too but concentrated the gains until ex-top-3 failed; adding the FLAT cell restored breadth (2025 ex-top-3 ₹9,775.76 → **₹23,764.74**) — the FLAT cell is part of the cure, not collateral. The threshold axis then proved the point from the other side: unrestricted sleeves at 2.0/2.5/3.0% are all 2026-negative standalone (−₹8,493.16 / −₹1,329.35 / −₹3,721.67) because bigger gaps fade worst in exactly the excluded cells. **Day-type was the fade's problem; size never was.** The banked sleeve: **GAP-FADE LONG, |gap| ≥ 1.5%, DOWN+FLAT regime cells only, entry 09:20 open, T125/S050** — standalone +₹21,470.27 (2025) / +₹1,492.21 (2026), now a book component.

## WS3 — Volume-confirmed reactions (R4-13, audit — the axis does not exist in stored data)
**No volume field exists in any stored equity candle.** Every file in `data/full_hist` — all 25 watchlist symbols plus the index, 5-minute and daily — carries only `timestamp/date, open, high, low, close`; the logger machinery likewise has no volume field. The volume-confirmed construction therefore **cannot be built from stored data, and no candidate was gated**. Nothing was fabricated. Named gap: a volume-bearing candle build for the 25 (5-min and daily, 2025–2026) — a new data build, in the same class as the bulk/block-deal and delivery-percentage axes named in Round 3. If that build ever lands, the construction is ready to define: reaction-family entries (N4-V3 / P2F population) filtered on the reaction day's volume ≥ 1.5× its trailing 20-day median, plus the symmetric low-volume mirror, gated whole-book per year.

## WS4 — Combinations with the flagged variants (decision support, nothing banked)
Gated against the corrected incumbent (the R4-03 banked book):

| Cycle | Combination | 2025 JO | 2026 JO | Failed legs | Reading |
|---|---|---|---|---|---|
| R4-10 | Banked book **+ R2-26** | ₹85,340.57 | ₹2,27,415.67 | **none — all 10 pass** | R2-26's Round-2 failing leg is **gone**: the banked sleeve's March-2025 gains (+₹5,033.28) absorb the swap's March loss (−₹2,459.83); March stands at +₹3,664.62. Recorded unbanked — adoption of a flagged variant is Chandu's decision, and after this gate sheet it is a decision with **no failing leg attached** |
| R4-11 | Sleeve swapped to the **full R3-10 form** | ₹83,315.69 | ₹2,17,720.37 | a, c, e, f | The refinement **dominates** the flagged sleeve head-to-head: swapping back to the full form loses ₹5,509.12 of 2025 and ₹5,572.97 of 2026 against the banked book |
| R4-12 | **R2-26 + full sleeve** (= R4-01's variant on the new base) | ₹90,849.69 | ₹2,21,842.70 | c, e, f | Against the banked book, adopting both flags now **costs** 2026 ₹1,450.64 and keeps both fade flips — strictly worse than R4-10's path |

**Decision state after Round 4, plainly:** adopt R2-26 alone → 2025 ₹85,340.57 with a clean gate sheet (R4-10). Adopt the full fade sleeve in any combination → the (e)/(f) failures return (R4-11/R4-12). The engine has banked everything it may bank; R2-26's adoption is the owner's call, and it is now the largest single step left toward the 2025 floor (₹7,534.00 of the ₹72,193.43 gap).

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹77,806.57** = **₹7,780.66/month** · **gap to floor ₹72,193.43** (Round 4 closed ₹21,470.27 of it) · full-year +₹76,427.84 · 857 trades · ex-top-3 stocks **+₹23,764.74** (top-3: OBEROIRLTY ₹30,432.17, ASTRAL ₹14,260.02, GODREJCP ₹7,970.91).
Months: Jan +₹5,327.82 · Feb +₹18,656.16 · Mar +₹6,124.45 · Apr +₹39,749.43 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹5,523.29** · Aug +₹11,173.48 · Sep +₹5,379.98 · **Oct −₹4,624.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window). Halves (Jan–Oct): H1 +₹72,356.85 · H2 +₹5,449.72.
Regime cells (full-year): DOWN +₹42,688.79 · FLAT +₹20,890.05 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · **GAP-FADE +₹21,470.27 (new, banked R4-03)** · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹7,543.38 · F4 +₹91.14 · INV-R3 −₹230.42 · P2F-R2 −₹390.06 · R2-LOWBAND −₹116.75.

### 2026 — floor MET
Jan–Oct **+₹2,23,293.34** = **₹22,329.33/month** (₹73,293.34 above the floor line) · 899 trades · all ten months green (Jan +₹29,738.12 … Oct +₹54,379.99) · ex-top-3 stocks +₹75,557.94.
Regime cells: DOWN +₹2,02,017.65 · FLAT +₹5,215.00 · UP +₹16,060.69.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹27,922.48 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · INV-ABOVE +₹3,349.21 · **GAP-FADE +₹1,492.21 (new)** · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r4_book2025_trades.csv`, `stocks_engine_r4_book2026_trades.csv` (exported from the corrected incumbent and independently re-summed to the paisa). Evidence: `r4_results.json` (every cycle's gate legs, placebos, flips, the R4-07 void record). Logs/lessons: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R4-L1…R4-L6). State: `stocks_engine_state.json` (`round4_summary`).

## Where the 2025 floor can still come from (honest close)
Round 4 banked the one thing Rounds 1–3 had left on the table: the gap-fade phenomenon, in the only form that survives the cross-year and concentration legs. The remaining ₹72,193.43 of 2025 gap has three named routes, none of them more cells on these candles: **(1) Chandu's adoption of R2-26** — now carrying a clean gate sheet on the current book (R4-10), worth ₹7,534.00, leaving ₹64,659.43; **(2) a new data axis** — volume (named gap, WS3), bulk/block deals, delivery percentages — none present in the workspace; **(3) Nov–Dec forward evidence** from the frozen test. The engine also leaves one discipline note behind: R4-07's voided banking is recorded in full, because a gate that cannot catch its own harness's defaults is not a gate.
