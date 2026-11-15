# Stocks (SarvaRitu) Engine — ROUND 3 · Targeted Techniques on 2025
**Date:** 2026-11-02 · **Segment:** Stocks (equity cash intraday, SarvaRitu umbrella)
**Basis (unchanged):** equity cash only · Chandu's 25 watchlist stocks only · provisional per 100 shares · ₹40/trade · paper only, real money ₹0 · same-day re-entry allowed · frozen November book/scorecards/loggers untouched (read-only).

## The floor, per year (never pooled)
₹1,50,000 Jan–Oct per year (₹15,000/month). **2025 is judged separately from 2026; a segment-year below its floor is failing regardless of the other year.**

- **Starting book** (Round-2 ending book, re-verified by independent re-sum from the exported trade CSVs before any scoring): 2025 Jan–Oct **+₹56,336.30** (₹5,633.63/mo; gap ₹93,663.70) · 2026 Jan–Oct **+₹2,21,801.13** (₹22,180.11/mo; floor MET).
- **Gate:** the frozen nine-leg session gate (combined rises · 2025 total + Jan–Oct no fall · 2026 no fall · all 3 regime cells × year positive · ex-top-3-stocks · no green month flips red · no half flips · beats pre-registered placebos · timing audit clean) **plus Round-3 leg (x): 2026 Jan–Oct must stay ≥ ₹1,50,000** — a 2025 gain bought with a 2026 breach does not bank.
- **R2-26** (INV-ABOVE exits T150/S080, +₹13,089.83 combined, fails only the Mar-2025 flip leg) remains **unadopted, awaiting Chandu's decision**. Round 3 worked on the banked book only; R2-26's numbers are unchanged by Round 3.

## Headline
**10 cycles worked (9 gated candidates + 1 audit). Bankings: ZERO.** Every Round-3 candidate was rejected by the gate, most of them on the cross-year rule or the concentration/flip legs rather than on the 2025 total. The ending book is the Round-2 ending book, **unchanged to the paisa**: 2025 ₹5,633.63/month (gap ₹93,663.70), 2026 ₹22,180.11/month (floor met). The one genuine phenomenon found — the 25 reward **buying faded gap-downs** — is worth +₹26,979.39 to 2025 but costs 2026 ₹4,080.76, so the engine cannot bank it; it is flagged below for Chandu in the same class as R2-26.

---

## WS1 — Month-wound diagnosis → targeted registry basket

**Diagnosis (trade-by-trade decomposition of the 2025 red months).** Jun −₹955.92 (12 tr), Jul −₹5,664.05 (20 tr), Oct −₹4,624.53 (15 tr) — 47 trades, −₹11,244.50 in total. By component: F4 −₹4,047.11 (22 tr), INV-ABOVE −₹3,637.29 (14), N4-V3 −₹2,614.80 (5), P2F −₹486.45 (3), P2F-R2 −₹458.85 (3); INV-LONG, INV-R3 and R2-LOWBAND took no wound-month trades. By regime cell: UP −₹6,496.88, DOWN −₹5,173.10, FLAT +₹425.48. The decomposition's central fact: the two largest wound rows are the book's biggest earners — F4 TVSMOTOR LONG lost −₹3,564.10 inside the wound months but earned +₹20,385.20 whole-book, and F4 TVSMOTOR SHORT lost −₹3,302.78 in the wound against +₹14,526.85 whole-book. The wounds are variance on the engines, not rot in dead rows. (Additions side: no row excluded by year-specific law exists to re-add — the same law builds both years; nothing was addable.)

**R3-01 — the gated basket (REJECTED).** Frozen rule, fixed before the gate ran: delete every (component × stock × direction) row whose wound-month net < 0 **and** whose whole-book net lies in (−₹500, 0] — i.e. exactly the individually sub-bar members, tested as ONE candidate. Members (7 rows, 58 trades book-wide): F4 NTPC SHORT (whole −₹134.15), F4 WIPRO SHORT (−₹384.32), N4-V3 INDUSTOWER SHORT (−₹115.92), P2F INDUSTOWER LONG (−₹232.98), P2F WIPRO LONG (−₹496.67), P2F-R2 INDUSTOWER LONG (−₹229.00), P2F-R2 WIPRO SHORT (−₹102.39).

| | 2025 Jan–Oct | 2026 Jan–Oct | Combined |
|---|---|---|---|
| Base | ₹56,336.30 | ₹2,21,801.13 | ₹2,76,758.70 |
| Basket variant | ₹58,209.83 (+₹1,873.53) | ₹2,21,623.03 (−₹178.10) | ₹2,78,454.13 |

Failed legs: **(c)** 2026 fell; **(h)** placebos — the mirror-wound basket (identical rule on the green months Feb+Mar+Aug) reached ₹2,81,788.63 combined and plain chronological first-58 removal reached ₹2,80,891.16; both beat the variant. The sub-bar registry holds nothing the placebos don't beat. **The wound-basket route is closed.**

## WS2 — Complete the 2025 event population (AUDIT — no hole exists)

**R3-02 — audit, no candidate gated (by evidence, not by omission).** The premise — that 2025's thinner reaction-family output meant missing 2025 events — is **false**:

| Event layer | 2025 | 2026 |
|---|---|---|
| Calendar rows | 114 | 115 |
| Results rows (per stock) | 100 (exactly 4) | 100 (exactly 4) |
| Results rows with missing/out-of-window reaction date | **0** | 16 |
| Reaction candidates produced | **100** | 80 |
| Candidates with \|reaction\| ≥ 2.5% | 33 | 39 |
| Candidates in [2.0, 2.5) | 12 | 9 |
| N4 signal-days (\|move\| ≥ 0.5 superset) | **91** | 77 |
| In-book P2F / P2F-R2 / R2-LOWBAND / N4 trades (full-year rows) | 26 / 21 / 1 / 36 | 31 / 32 / 3 / 37 |

2025's population is complete — it produces **more** candidates and more N4 signal-days than 2026's. The 16 defective reaction dates are all in the **2026** file: 15 are Nov-2025 events carrying a placeholder reaction date of 2026-01-01 (valid Nov-2025 reaction dates for all 15 are sourceable from the stored `results_events_v1.csv`, but those events fall outside the Jan–Oct judged window under either dating, so a corrected-calendar candidate would change nothing that is judged — building one would be theatre, and it was not built). The 16th is **UNITDSPR, Q2 FY27 results on 2026-10-28, reaction date blank in every stored source — named here as unsourceable, never invented**; the incumbent construction treats the announcement day itself as the reaction day.

What actually ails the 2025 families is expectancy and band mix, not coverage: fewer ≥2.5% reactions (33 vs 39) and P2F-R2 earning −₹390.06 on 21 trades in 2025 against +₹15,149.33 on 32 in 2026, while P2F is healthy in both years (+₹15,884.42 / +₹20,116.78). Those are properties of the 2025 tape; no calendar repair changes them. **Workstream closed by evidence.**

## WS3 — Entry-timing optimisation (both variants gated, both rejected)

Constructions anchored exactly before scoring: with deferral off, the rebuilt F4 population reproduces the cached population trade-for-trade and the rebuilt chain reproduces all 15,453 cached chain rows; current-law builders on the cached populations reproduce the book's F4 / INV-LONG / INV-ABOVE exactly; timing audit 0 violations.

**R3-03 — F4, 15-min execution (REJECTED).** Measurement frozen (premove @10:00, band [0.5, 1.0)%, follow, T150/S095); entry deferred to the open of the next quarter-hour bar. 2025 → ₹56,564.96 (**+₹228.66**); 2026 → ₹1,88,799.78 (**−₹33,001.35**); combined falls. Failed legs (a), (c), (e), (h). Placebos: quarter-hour fade book; one-bar-late entry book.

**R3-04 — INV, 15-min execution (REJECTED).** Chain entries deferred to quarter-hour opens; law frozen (INV-LONG rounds ≤3, entries <11:00, FLAT stand-aside; INV-ABOVE rounds ≤2, <10:30). 2025 → ₹45,304.57 (**−₹11,031.73**); 2026 → ₹2,08,306.48 (**−₹13,494.65**); Jan 2025 (₹5,997.81 → −₹1,957.45) and Mar 2025 (₹1,091.17 → −₹894.78) flip red. Failed legs (a), (b), (c), (d), (e), (f), (h). Placebos: quarter-hour SHORT-mirror components; one-bar-late chain.

With R2-03 (09:45 measurement) and R2-16 (09:40 confirmation), four separate delay mechanisms have now all lost money. **The entry-timing axis is closed: the 5-minute next-bar entry is load-bearing for both families.**

## WS4 — Two new mechanism classes (all cells gated)

Disclosure: two older closed lines sit near this territory — the S3 screen's verdict that price-derived events are information-free on the 25, and the pre-SarvaRitu "R2 follow-through & gaps" skeleton. The constructions below are different (overnight gap at the open with next-bar entry; index-style range break on cash names) and were run once each under this round's orders, judged by the gate alone.

**Gap diagnostic (pre-registered, both years pooled, per-trade expectancy after ₹40 cost):**

| Sleeve | H1 (Jan–Jun) | H2 (Jul–Oct) |
|---|---|---|
| GAP-FOLLOW (804 tr) | −₹27.36 | −₹43.12 |
| GAP-FADE (804 tr) | +₹3.10 | +₹25.80 |
| — of which fade-LONG (buy the gap-down, 384 tr) | **+₹57.20** | **+₹72.27** |
| — of which fade-SHORT (fade the gap-up, 420 tr) | −₹48.74 | −₹8.51 |

The 25 do not reward following overnight gaps at all; they mildly reward fading them, and the entire fade effect lives in one side: **buying gap-downs**.

| Cycle | Candidate | 2025 Δ (Jan–Oct) | 2026 Δ (Jan–Oct) | Gate combined Δ | Failed legs | Verdict |
|---|---|---|---|---|---|---|
| R3-05 | GAP-FOLLOW ≥1.5% | −₹22,079.40 | −₹2,219.99 | −₹26,861.32 | a,b,c,d,e,f,g,h | REJECTED |
| R3-06 | GAP-FADE ≥1.5% | +₹21,762.48 | −₹15,956.71 | −₹1,121.50 | a,c,e,f,h | REJECTED |
| R3-08 | GAP-FADE ≥2.5% | +₹11,429.79 | +₹1,207.57 | **+₹9,571.17** | e,f,h | REJECTED |
| R3-09 | GAP-FOLLOW ≥2.5% | −₹4,439.73 | +₹73.78 | −₹3,740.95 | a,b,d,e,f,h | REJECTED |
| R3-10 | GAP-FADE LONG-only ≥1.5% | **+₹26,979.39** | −₹4,080.76 | **+₹22,084.79** | c,e,f | REJECTED — flagged |
| R3-07 | ORB-STOCK | −₹96,573.49 | −₹2,43,756.84 | −₹3,46,100.99 | all + x | REJECTED |

(Year deltas are Jan–Oct book deltas. "Gate combined" is the gate's own sum — 2025 full-year total + 2026 Jan–Oct — so it differs from the sum of the two Jan–Oct deltas by the sleeve's Nov/Dec 2025 trades; e.g. R3-06's fade loses a further ₹6,927.27 in Nov/Dec 2025, which is why its gate combined falls even though its Jan–Oct deltas net positive. Placebos for every gap cell: the opposite direction's book and the same direction entered one bar late; for ORB: the flipped book and the one-bar-later book.)

Reading of the table, straight:
- **Follow is dead at both thresholds.** No further follow cells.
- **Fade is a 2025-only phenomenon at book level.** At ≥1.5% it hands 2026 −₹15,956.71; at ≥2.5% both years rise but the gains concentrate in the top-3 stocks (leg e), May 2025 flips red (leg f), and the one-bar-late placebo beats it (leg h).
- **R3-10 is the round's strongest 2025 result and it still cannot bank.** The LONG-only fade passes 7 of 10 legs (combined, 2025, cells, halves, placebos, timing, 2026-floor) and fails exactly three: 2026 falls −₹4,080.76 (leg c), ex-top-3 2026 falls (leg e), and May 2025 (+₹2,498.99 → −₹4,762.43) and Dec 2025 flip (leg f). The engine's cross-year rule is absolute — **not banked**. It is recorded as a **flagged observation for Chandu**, in the same class as R2-26: if he chooses to adopt a candidate against named failed legs, that is his decision; the engine will not make it.
- **R3-07 ORB-STOCK is the worst construction this engine has ever gated:** standalone −₹96,573.49 (2025, 5,098 trades) and −₹2,43,756.84 (2026, 3,929 trades) — expectancy ≈ −₹19 and −₹62 per trade. Chandu's index opening-range method does not port to individual cash stocks at T125/S050. The ORB family is closed; no range-width or exit variants will be run.

## WS5 — Combinations
**Vacuous.** No Round-3 candidate banked, so there is nothing to combine. The ending book is the Round-2 ending book unchanged.

---

## Ending scorecard (per year — never pooled)

### 2025 — floor NOT met
Jan–Oct **+₹56,336.30** = **₹5,633.63/month** · **gap to floor ₹93,663.70** (unchanged by Round 3) · full-year +₹54,957.57 · 776 trades (full-year rows).
Months: Jan +₹5,997.81 · Feb +₹16,971.36 · Mar +₹1,091.17 · Apr +₹21,850.91 · May +₹2,498.99 · **Jun −₹955.92 · Jul −₹5,664.05** · Aug +₹13,766.58 · Sep +₹5,403.98 · **Oct −₹4,624.53** · (Nov −₹2,586.68 · Dec +₹1,207.95, outside the judged window).
Regime cells (full-year): DOWN +₹39,226.00 · FLAT +₹2,882.57 · UP +₹12,849.00.
Components (full-year): INV-LONG +₹23,894.61 · P2F +₹15,884.42 · INV-ABOVE +₹8,281.25 · N4-V3 +₹7,543.38 · F4 +₹91.14 · INV-R3 −₹230.42 · P2F-R2 −₹390.06 · R2-LOWBAND −₹116.75.

### 2026 — floor MET
Jan–Oct **+₹2,21,801.13** = **₹22,180.11/month** (₹71,801.13 above the floor line) · 680 trades · all ten months green (Jan +₹33,684.05 … Oct +₹49,591.93).
Regime cells: DOWN +₹1,96,194.09 · FLAT +₹9,546.35 · UP +₹16,060.69.
Components: F4 +₹1,03,055.93 · INV-LONG +₹50,160.09 · N4-V3 +₹27,922.48 · P2F +₹20,116.78 · P2F-R2 +₹15,149.33 · INV-ABOVE +₹3,349.21 · R2-LOWBAND +₹1,283.36 · INV-R3 +₹763.95.

Books: `stocks_engine_r3_book2025_trades.csv`, `stocks_engine_r3_book2026_trades.csv` (content identical to the Round-2 books — nothing banked; re-exported under Round-3 names). Evidence: `r3_results.json` (every cycle's gate legs, placebo totals, flip details). Logs/lessons appended: `stocks_engine_log.md`, `stocks_engine_lessons.md` (R3-L1…R3-L8). State: `stocks_engine_state.json`.

## Where the 2025 floor can still come from (honest close)
Three rounds have now gated the full law grids of all seven components, regime cells, wound baskets, data completion, entry timing at both bars, and two new mechanism classes. Every 2025-positive idea found since Round 2's bankings is either 2026-negative (gap-fade family) or top-3-concentrated or placebo-beaten. The remaining routes are outside the current information set: (1) **Chandu's adoption decisions** on the two flagged gate-failures — R2-26 (+₹7,534.00 to 2025 Jan–Oct) and R3-10 (+₹26,979.39 to 2025, −₹4,080.76 to 2026) — which together would put 2025 at ₹90,849.69, still ₹59,150.31 short; (2) a **new data axis** not in the workspace (bulk/block deals, delivery percentages); (3) **Nov–Dec forward evidence** from the frozen test. Grinding further cells on the same candles would be curve-fitting pressure, not research — the engine says so plainly rather than manufacturing a pass.
