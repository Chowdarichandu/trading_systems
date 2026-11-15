# STOCKS ENGINE — ROUND 2 (2026-11-02)

Mandate (Chandu, 2026-11-02 ~12:35 IST): no saturation conclusions; work different use cases, combinations and permutations until the goal is achievable. Goal: **Jan–Oct ≥ ₹1,50,000 in EACH year separately** (₹15,000/month). Basis: equity cash only, provisional per 100 shares, cost ₹40/trade, paper only, real money ₹0. Universe: Chandu's 25 watchlist stocks. Starting book: FLOOR-C4 (Round 1 ending book). Gate: the frozen Round-1 session gate (nine legs — combined rises; 2025 total + Jan–Oct do not fall; 2026 does not fall; every regime cell × year stays positive; ex-top-3-stocks ≥ 0 per year and combined does not fall; no green month flips red; no Jan–Oct half flips sign; beats pre-registered placebos; timing audit clean) **plus** the cross-year rule — a candidate that improves one year while degrading the other does not bank, and nothing may push 2026 below ₹1,50,000. Every candidate construction was anchored multiset-exact against the FLOOR-C4 component it replaces before scoring (F4, INV-LONG, INV-ABOVE, P2F, P2F-R2, R2-LOWBAND, N4-V3 all reproduced exactly); timing/leak audit 0 violations across all population builds; ending book CSVs independently re-summed to the paisa.

## Result

| Year | FLOOR-C4 Jan–Oct | Round-2 end Jan–Oct | Pace/month | Floor ₹1,50,000 | Gap |
|---|---|---|---|---|---|
| 2025 | +₹47,884.79 | **+₹56,336.30** | ₹5,633.63 | NOT MET | −₹93,663.70 |
| 2026 | +₹2,16,921.39 | **+₹2,21,801.13** | ₹22,180.11 | MET | +₹71,801.13 above |

Session lift: **+₹13,331.25 combined** (2025 +₹8,451.51, 2026 +₹4,879.74), from 2 banked changes across 28 gated cycles + 22 grid cells. Stop condition met: ≥12 cycles run (28 + 22 cells) AND the enumerated space exhausted (every cell below has a gated verdict).

## Banked changes (2)

1. **R2-07 grid cell — INV-LONG: ADR ≥ 3.0 (unchanged), round cap ≤2 → ≤3, entry cutoff 10:30 → 11:00.** Combined +₹11,255.92 (2,63,427.45 → 2,74,683.37); 2025 Jan–Oct +₹6,620.26 (47,884.79 → 54,505.05); 2026 Jan–Oct +₹4,635.66 (2,16,921.39 → 2,21,557.05). All nine legs pass; placebos beaten (SHORT-side book 1,80,365.56; opposite-gate book 2,20,390.77). The round-3 rows the variant absorbs were de-duplicated out of INV-R3 (which keeps its FLAT-day and round ≥4 rows). Control inside the grid: the same cell at the old 10:30 cutoff reproduces the incumbent combined to the paisa (2,63,427.45) — the entire gain is the 11:00 entry hour plus round 3 at that hour, in both years.
2. **R2-17 — N4-V3 move threshold 1.0% → 0.8% (std 09:35 entry, T150/S080, banked FLOOR-2 one-sided ≥+3% LONG cap retained).** Combined +₹2,075.33 (2,74,683.37 → 2,76,758.70); 2025 Jan–Oct +₹1,831.25 (54,505.05 → 56,336.30); 2026 Jan–Oct +₹244.08 (2,21,557.05 → 2,21,801.13). All nine legs pass; flipped-direction placebo beaten. (The [0.75,1.0) lowband slice was scored dead in the v3 saturation at T125/S050 exits — SAT-4; at the book's T150/S080 geometry the 0.8 threshold is a different cell and it passes.)

## Flagged for Chandu's decision — NOT banked (gate not waived by the engine)

**R2-26 — INV-ABOVE exits T125/S050 → T150/S080.** Combined **+₹13,089.83** (2,76,758.70 → 2,89,848.53); 2025 Jan–Oct **+₹7,534.00** (56,336.30 → 63,870.30); 2026 Jan–Oct **+₹4,122.33** (2,21,801.13 → 2,25,923.46). Passes 8 of 9 legs (combined, both years, cells, ex-top-3, halves, placebos, timing). **Fails leg (f) only:** Mar 2025 flips green → red (+₹1,091.17 → −₹1,368.66). Per-cell splits do not repair it: UP-days-only geometry (R2-27, +₹8,733.80 combined, no flip) fails leg (e) ex-top-3-stocks; FLAT-days-only (R2-28, +₹4,356.03) fails the same March flip (the damage sits in the FLAT cell). Adopting R2-26 would take 2025 to +₹63,870.30 Jan–Oct (pace ₹6,387.03/month, gap −₹86,129.70) and 2026 to +₹2,25,923.46 — at the price of one red month in 2025. Decision is Chandu's (precedent: Nifty CH3-R adoption, 2026-11-02).

## Full grid — every cell's gated verdict

Failed-leg key: a combined rises · b 2025 no fall · c 2026 no fall · d cells positive · e ex-top-3 · f no green-month flip · g no half flip · h beats placebos.

### 1. F4 permutations (base: FLOOR-C4, combined 2,63,427.45)

| Cycle | Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|---|
| R2-01 | band [0.4,0.9) @10:00 | FAIL | 2,55,471.71 | 60,371.79 | 1,96,478.65 | a, c |
| R2-02 | band [0.6,1.2) @10:00 | FAIL | 2,12,033.06 | 41,006.61 | 1,72,405.18 | a, b, c, e, f |
| R2-03 | band [0.5,1.0) @09:45 | FAIL | 1,65,067.66 | 65,018.29 | 1,01,428.10 | a, c, d, e, f, h |
| R2-04 | band [0.4,0.9) @09:45 | FAIL | 1,58,052.68 | 65,950.24 | 93,481.17 | a, c, d, e, f, h |
| R2-05 | band [0.6,1.2) @09:45 | FAIL | 1,55,648.09 | 59,854.60 | 97,172.22 | a, c, d, e, f, h |
| R2-06 | EXCL_DIR off, frozen band @10:00 | FAIL | 2,52,917.12 | 51,819.10 | 2,02,991.67 | a, c, e, f |

Pattern, stated once: every F4 population change buys 2025 (up to +₹18,065) with a larger 2026 loss (up to −₹1,23,440). The 09:45 measurement alone is +₹17–18k in 2025 and −₹1,15,493 in 2026. Placebos per cell: mirror-direction book + decoy band [1.5,2.0) book.

### 2. INV pool permutations (11 cells per component; incumbent cell ADR 3.0 / rounds ≤2 / <10:30 excluded)

**INV-LONG** (base combined 2,63,427.45; placebos per cell: SHORT-side book, opposite-gate book):

| Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|
| ADR2.5 r≤2 <10:30 | FAIL | 2,53,181.48 | 52,744.20 | 2,01,816.01 | a, c, e, f |
| ADR2.5 r≤2 <11:00 | FAIL | 2,53,887.09 | 55,799.33 | 1,99,466.49 | a, c, e, f |
| ADR2.5 r≤3 <10:30 | FAIL | 2,53,932.91 | 52,113.40 | 2,03,198.24 | a, c, e, f |
| ADR2.5 r≤3 <11:00 | FAIL | 2,56,467.72 | 56,268.01 | 2,01,578.44 | a, c, e, f |
| ADR3.0 r≤2 <11:00 | **PASS** | 2,70,864.83 | 50,965.20 | 2,21,278.36 | — |
| ADR3.0 r≤3 <10:30 | FAIL | 2,63,427.45 | 47,884.79 | 2,16,921.39 | a (identical to incumbent — control cell) |
| ADR3.0 r≤3 <11:00 | **PASS — BANKED** | 2,74,683.37 | 54,505.05 | 2,21,557.05 | — |
| ADR3.5 r≤2 <10:30 | FAIL | 2,33,824.71 | 43,289.80 | 1,91,913.64 | a, b, c, e, f |
| ADR3.5 r≤2 <11:00 | FAIL | 2,36,387.13 | 44,093.74 | 1,93,672.12 | a, b, c, e, f |
| ADR3.5 r≤3 <10:30 | FAIL | 2,33,824.71 | 43,289.80 | 1,91,913.64 | a, b, c, e, f |
| ADR3.5 r≤3 <11:00 | FAIL | 2,35,422.06 | 42,797.60 | 1,94,003.19 | a, b, c, e, f |

**INV-ABOVE** (run against the post-R2-07 book, base combined 2,74,683.37):

| Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|
| ADR2.5 r≤2 <10:30 | FAIL | 2,72,437.17 | 55,577.56 | 2,20,491.27 | a, b, c, d, e, h |
| ADR2.5 r≤2 <11:00 | FAIL | 2,61,828.81 | 56,824.19 | 2,08,214.25 | a, c, d, e, f, h |
| ADR2.5 r≤3 <10:30 | FAIL | 2,75,817.05 | 59,350.87 | 2,20,429.61 | c, d, e, h |
| ADR2.5 r≤3 <11:00 | FAIL | 2,67,534.76 | 60,525.60 | 2,07,847.26 | a, c, d, e, f, h |
| ADR3.0 r≤2 <11:00 | FAIL | 2,68,845.18 | 58,220.46 | 2,13,283.71 | a, c, e, f, h |
| ADR3.0 r≤3 <10:30 | FAIL | 2,79,577.14 | 59,792.25 | 2,21,495.39 | c, h |
| ADR3.0 r≤3 <11:00 | FAIL | 2,76,757.24 | 63,650.41 | 2,13,741.29 | c, e, f, h |
| ADR3.5 r≤2 <10:30 | FAIL | 2,69,017.42 | 51,964.23 | 2,17,201.34 | a, b, c, e, h |
| ADR3.5 r≤2 <11:00 | FAIL | 2,69,238.56 | 52,455.87 | 2,17,201.34 | a, b, c, e, f, h |
| ADR3.5 r≤3 <10:30 | FAIL | 2,70,819.89 | 53,228.05 | 2,17,859.03 | a, b, c, e, h |
| ADR3.5 r≤3 <11:00 | FAIL | 2,74,249.27 | 55,231.87 | 2,18,592.34 | a, b, c, e, h |

No INV-ABOVE cell banks. Several cells gain in 2025 (+₹5–9k) but every one either costs 2026 or loses to its own placebos (the SHORT-side and opposite-gate INV populations are themselves strong: placebo books run 2,37,070–3,28,119 combined).

**Merged round-law cells** (INV-LONG + INV-R3 unified, rounds ≥1, ADR 3.0, <10:30):

| Cycle | Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|---|
| R2-09 | merged, FLAT stand-aside ON | FAIL | 2,63,727.45 | 47,884.79 | 2,17,221.39 | a, b, c, e |
| R2-10 | merged, FLAT stand-aside OFF | FAIL | 2,58,087.48 | 45,145.54 | 2,14,320.67 | a, b, c, e |

### 3. Reaction grid — untested cells (P2F family law held constant)

| Cycle | Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|---|
| R2-11 | P2F band ≥3.0 @ R+1 | FAIL | 2,70,379.72 | 51,826.38 | 2,20,077.07 | a, b, c, e |
| R2-12 | P2F-R2 band ≥3.0 @ R+2 | FAIL | 2,74,158.49 | 54,408.90 | 2,21,507.57 | a, b, c, e, h |
| R2-13 | R2-LOWBAND, UP stand-aside removed | FAIL | 2,71,154.62 | 51,766.38 | 2,21,534.47 | a, b, c, e, f, h |
| R2-14 | P2F band ≥2.0 @ R+1 | FAIL | 2,74,113.45 | 55,397.58 | 2,20,094.60 | a, c, f |

No reaction cell passed, so there are no passing-cell combinations to stack (the combination step of this family is empty by its own precondition). Placebos: flipped-direction books, decoy band [1.5,2.0) books, chrono first-N removal for the two restrictions.

### 4. N4 permutations (all with the banked FLOOR-2 one-sided cap)

| Cycle | Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|---|
| R2-15 | threshold 1.2%, std entry | FAIL | 2,72,881.73 | 55,229.86 | 2,18,580.48 | a, c, e |
| R2-16 | 09:40 confirming-close entry (thr 1.0) | FAIL | 2,58,335.15 | 46,315.77 | 2,12,957.79 | a, b, c, e, h |
| R2-17 | threshold 0.8%, std entry | **PASS — BANKED** | 2,76,758.70 | 56,336.30 | 2,21,801.13 | — |
| R2-18 | threshold 1.2% × 09:40 confirm | FAIL | 2,54,761.54 | 46,679.81 | 2,09,020.14 | a, b, c, e, h |

The confirming-close entry is the single most expensive idea in the round (−₹16–22k combined in both its cells): waiting one bar for confirmation pays the move away in both years.

### 5. Regime-cell combinations

Incumbent cell anatomy (Jan–Oct, at session start): F4 DOWN 2025 227 tr / −₹2,370 vs 2026 312 tr / +₹1,06,006 — the same labelled cell carries both years' opposite signs; F4 FLAT 2025 +₹2,461 / 2026 −₹2,950.

| Cycle | Cell | Verdict | Combined | 2025 Jan–Oct | 2026 Jan–Oct | Failed legs |
|---|---|---|---|---|---|---|
| R2-20 | F4 DOWN-cell exits T125/S065 | FAIL | 2,44,886.68 | 52,355.63 | 1,93,909.78 | a, b, c, e, h |
| R2-21 | F4 DOWN-cell exits T175/S095 | FAIL | 2,72,509.58 | 62,804.86 | 2,11,083.45 | a, c, h |
| R2-22 | F4 FLAT-cell exits T125/S065 | FAIL | 2,76,142.47 | 52,313.15 | 2,25,208.05 | a, b, d |
| R2-23 | F4 FLAT-cell exits T175/S095 | FAIL | 2,76,520.84 | 56,148.04 | 2,21,751.53 | a, b, c, e |
| R2-24 | F4 × FLAT stand-aside | FAIL | 2,77,247.60 | 53,875.62 | 2,24,750.71 | b, h (chrono placebo 2,82,398.84 beats the variant) |
| R2-25 | INV-LONG exits T150/S080 | FAIL | 2,76,537.16 | 60,719.09 | 2,17,196.80 | a, c, f |
| R2-26 | INV-ABOVE exits T150/S080 | FAIL — FLAGGED | 2,89,848.53 | 63,870.30 | 2,25,923.46 | f only (see above) |
| R2-27 | INV-ABOVE T150/S080, UP days only | FAIL | 2,85,492.50 | 60,434.56 | 2,25,003.17 | e only |
| R2-28 | INV-ABOVE T150/S080, FLAT days only | FAIL | 2,81,114.73 | 59,772.04 | 2,22,721.42 | f only (same Mar 2025 flip) |

Placebos for geometry cells: the same geometry applied to the wrong cell; for R2-25/26/27/28: SHORT-side books at the same geometry.

### 6. New-mechanism trial

**R2-19 — PERSIST-R2** (definition frozen before scoring): results reaction |ret| ≥ 2.5%; R+1 daily close persists beyond the R close in the reaction direction; enter R+2 at the 09:55-bar close (price at 10:00) only if R+2's open→10:00 drift is strictly in the reaction direction; exits T125/S050; P2F-R2 family law. Standalone sleeve: 2025 Jan–Oct **+₹2,903.00**, 2026 Jan–Oct **−₹643.26**. Book verdict: **FAIL** — legs (c) 2026 no-fall and (e) ex-top-3. Combined would have risen (+₹2,009.67) on 2025's contribution alone; the cross-year rule refuses it. Placebos: flipped entries on identical qualifying days; the unconditioned sibling (no persistence leg).

## Ending book — controlled scorecard

Books of record: `stocks_engine_r2_book2025_trades.csv` (776 tr) / `stocks_engine_r2_book2026_trades.csv` (680 tr). Independent re-sum from the written files: exact, both years.

**2025** — total +₹54,957.57 · Jan–Oct **+₹56,336.30** (731 tr, 334 wins) · halves (Jan–Oct) +₹48,410.24 / +₹7,926.06 · ex-top-3-stocks +₹9,775.76 (top stocks: OBEROIRLTY +23,146.80, ASTRAL +13,414.72, GLENMARK +8,620.29) · cells DOWN +39,226.00 / FLAT +2,882.57 / UP +14,227.73 — all positive.
Months Jan–Oct: Jan +5,997.81 · Feb +16,971.36 · Mar +1,091.17 · Apr +21,850.91 · May +2,498.99 · Jun −955.92 · Jul −5,664.05 · Aug +13,766.58 · Sep +5,403.98 · Oct −4,624.53.
Components Jan–Oct: INV-LONG 291 tr / +23,894.61 · P2F 21 / +15,319.47 · N4-V3 30 / +9,815.36 · INV-ABOVE 121 / +8,711.44 · F4 246 / +91.14 · INV-R3 4 / −230.42 · P2F-R2 17 / −1,148.55 · R2-LOWBAND 1 / −116.75.
Deltas vs FLOOR-C4: Jan–Oct +₹8,451.51; ex-top-3-stocks +₹3,808.02 (5,967.74 → 9,775.76); red months unchanged (Jun, Jul, Oct).

**2026** — total = Jan–Oct **+₹2,21,801.13** (680 tr, 365 wins) · halves +₹1,31,143.71 / +₹90,657.42 · ex-top-3-stocks +₹87,675.53 (top stocks: TVSMOTOR +76,670.26, ASTRAL +30,793.84, OBEROIRLTY +26,661.50) · cells DOWN +1,96,194.09 / FLAT +9,546.35 / UP +16,060.69 — all positive, all ten months green.
Months Jan–Oct: Jan +33,684.05 · Feb +20,734.89 · Mar +22,557.75 · Apr +13,095.59 · May +41,071.43 · Jun +7,934.71 · Jul +8,025.74 · Aug +10,310.86 · Sep +14,794.18 · Oct +49,591.93.
Components Jan–Oct: F4 355 tr / +1,03,055.93 · INV-LONG 182 / +50,160.09 · N4-V3 37 / +27,922.48 · P2F 31 / +20,116.78 · P2F-R2 32 / +15,149.33 · INV-ABOVE 36 / +3,349.21 · R2-LOWBAND 3 / +1,283.36 · INV-R3 4 / +763.95.
Deltas vs FLOOR-C4: Jan–Oct +₹4,879.74; the floor line holds with ₹71,801.13 of headroom.

**Book law added in Round 2:** (i) INV-LONG: ADR ≥ 3.0, rounds ≤ 3, entry cutoff 11:00 (INV-R3 retains FLAT-day round ≥ 3 and round ≥ 4 rows); (ii) N4-V3: move threshold 0.8% (FLOOR-2 cap and all prior law unchanged). The frozen November SarvaRitu book/scorecards/loggers were not touched (read-only throughout).

## Space coverage / stop

Enumerated space: F4 6/6 cells · INV crosses 22/22 cells + 2 merged · reaction 4/4 untested cells · N4 4/4 cells · regime cells 9/9 · new mechanism 1/1. Combinations: banked changes were chained into the running book and every later cycle was gated against the combined state; the reaction family produced no passing cell to combine. **Stop condition met: 28 cycles + 22 grid cells run, enumerated space exhausted.** Remaining gap is 2025's: ₹93,663.70 of Jan–Oct money that no cell in the enumerated space produces without taking more than that out of 2026 or breaking a gate leg. Open items that are not in-sample cells: the flagged R2-26 decision (Chandu's), and fresh data (Nov–Dec 2026 forward evidence).

Evidence: `r2_results.json` (28 gated records incl. all grid cells, legs, placebos, cell tables) · scripts `stocks_engine_r2_{anchor,populations,lib,f4,inv,events,cells,cells2,final}.py` · populations `r2_cache.pkl` · running book `r2_books.pkl`.
