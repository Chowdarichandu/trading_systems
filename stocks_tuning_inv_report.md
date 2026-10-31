# Stocks EQUITY — INV family tuning loop — report

**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders. Real money ₹0.**
**All figures provisional per 100 shares, net = gross − ₹40/trade. Window Jan–Oct 2026 (Oct = 1–28).**
Spec: `stocks_tuning_inv_frozen.md` (frozen before scoring). This loop produces v2 CANDIDATES only — the November INV1 shadow (`stocks_p2inv_november_shadow_spec.md`) is untouched.

## Validation gate — PASS

Rebuilt machinery vs published Round 8/9/10 figures: P2@T125 (918, +₹10,657.81), INV1@T125 (694, +₹22,964.30; halves +₹7,255.01 / +₹15,709.29), INV1@T10 (721, +₹19,232.08; halves −₹517.74 / +₹19,749.82), INV2-condition@T125 (563, +₹48,437.14; halves +₹24,913.18 / +₹23,523.96). Gate result: **PASS** (detail in `stocks_tuning_inv_results.json`).

## Family T1 — EXIT LADDER on INV1 (verdict below)

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T100_S050 | 721 | 38.4 | 66.67 | 26.67 | -517.74 (584) | 19749.82 (137) | 19232.08 | 12004.24 | 10/25 | 195.1 | no |
| T100_S065 | 690 | 42.6 | 44.14 | 4.14 | -9350.15 (555) | 12209.35 (135) | 2859.2 | 10282.61 | 9/25 | 1072.7 | no |
| T100_S080 | 667 | 47.8 | 34.56 | -5.44 | -11434.37 (535) | 7804.35 (132) | -3630.02 | 9755.19 | 11/25 | None | no |
| T125_S050 | 694 | 34.6 | 73.09 | 33.09 | 7255.01 (564) | 15709.29 (130) | 22964.3 | 8490.91 | 10/25 | 141.0 | **PASS** |
| T125_S065 | 662 | 38.7 | 53.28 | 13.28 | -1526.17 (534) | 10319.74 (128) | 8793.57 | 7124.82 | 8/25 | 358.4 | no |
| T125_S080 | 638 | 44.0 | 47.36 | 7.36 | -3353.35 (513) | 8047.53 (125) | 4694.18 | 6755.45 | 9/25 | 576.2 | no |
| T150_S050 | 679 | 31.2 | 51.36 | 11.36 | -5025.92 (551) | 12738.3 (128) | 7712.38 | 10114.59 | 8/25 | 317.2 | no |
| T150_S065 | 646 | 35.4 | 32.06 | -7.94 | -12662.89 (520) | 7533.99 (126) | -5128.9 | 8749.76 | 8/25 | None | no |
| T150_S080 | 622 | 40.7 | 32.78 | -7.22 | -8660.22 (499) | 4169.11 (123) | -4491.11 | 7444.07 | 9/25 | None | no |
| T175_S050 | 662 | 29.8 | 51.02 | 11.02 | -8732.5 (539) | 16029.42 (123) | 7296.92 | 14637.85 | 8/25 | 407.6 | no |
| T175_S065 | 625 | 34.2 | 43.01 | 3.01 | -9191.53 (504) | 11075.65 (121) | 1884.12 | 13035.23 | 8/25 | 1759.8 | no |
| T175_S080 | 601 | 39.4 | 48.99 | 8.99 | -2587.07 (483) | 7988.83 (118) | 5401.76 | 11813.75 | 9/25 | 699.5 | no |
| T200_S050 | 652 | 28.4 | 51.18 | 11.18 | -12173.36 (530) | 19460.18 (122) | 7286.82 | 16748.37 | 8/25 | 453.3 | no |
| T200_S065 | 614 | 32.2 | 27.19 | -12.81 | -22933.36 (494) | 15070.8 (120) | -7862.56 | 15145.75 | 8/25 | None | no |
| T200_S080 | 590 | 37.5 | 35.6 | -4.4 | -14640.82 (473) | 12046.57 (117) | -2594.25 | 13924.27 | 8/25 | None | no |

Cells positive in BOTH halves (before breadth): ['T125_S050'].
Best 3 by weaker-half net: T125_S050 (JM ₹7255.01, JO ₹15709.29, total ₹22964.3, breadth 10/25), T100_S050 (JM ₹-517.74, JO ₹19749.82, total ₹19232.08, breadth 10/25), T125_S065 (JM ₹-1526.17, JO ₹10319.74, total ₹8793.57, breadth 8/25).
**Verdict: the frozen T125/S050 is itself the ladder's best cell** — no exit change improves the weaker half. Ladder closed as a tuning direction (cells that pass the full gate, if any, are marked in the table).

## Family T2 — TRAIL EXIT on INV1

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| TRA (activate +0.75% / trail 0.4%) | 732 | 43.7 | 53.51 | 13.51 | -3624.33 (592) | 13514.02 (140) | 9889.69 | 8318.69 | 8/25 | 297.1 | no |
| TRB (activate +1.0% / trail 0.5%) | 692 | 39.0 | 62.82 | 22.82 | -2245.75 (561) | 18034.82 (131) | 15789.07 | 9367.49 | 9/25 | 196.7 | no |
TRA exit mix: {'square_off': [7, 1.0], 'stop': [407, 55.6], 'trail_stop': [318, 43.4]}. Weaker half ₹-3624.33 vs plain T125/S050 ₹7255.01; full-gate pass: False.
TRB exit mix: {'square_off': [31, 4.5], 'stop': [417, 60.3], 'trail_stop': [244, 35.3]}. Weaker half ₹-2245.75 vs plain T125/S050 ₹7255.01; full-gate pass: False.
**Verdict:** neither trail variant passes the full gate; trailing does not fix INV1's weaker half. Trail direction closed.

## Family T3 — DIRECTION split of INV1 (LONG-only / SHORT-only)

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T125_S050 LONG-only | 249 | 36.1 | 137.13 | 97.13 | 14751.12 (200) | 9434.61 (49) | 24185.73 | 7691.08 | 12/25 | 116.2 | **PASS** |
| T125_S050 SHORT-only | 445 | 33.7 | 37.26 | -2.74 | -7496.11 (364) | 6274.68 (81) | -1221.43 | 799.83 | 11/25 | None | no |
| T100_S050 LONG-only | 256 | 38.3 | 104.78 | 64.78 | 3120.3 (204) | 13464.18 (52) | 16584.48 | 11921.5 | 12/25 | 143.1 | **PASS** |
| T100_S050 SHORT-only | 465 | 38.5 | 45.69 | 5.69 | -3638.04 (380) | 6285.64 (85) | 2647.6 | 82.74 | 9/25 | 778.1 | no |
| T125_S065 LONG-only | 237 | 40.1 | 120.59 | 80.59 | 12331.8 (189) | 6768.8 (48) | 19100.6 | 7604.46 | 13/25 | 149.4 | **PASS** |
| T125_S065 SHORT-only | 425 | 37.9 | 15.75 | -24.25 | -13857.97 (345) | 3550.94 (80) | -10307.03 | -479.64 | 9/25 | None | no |
**The T10 question:** INV1 at T10/S050 combined has Jan–May −₹517.74 (the known flip). LONG-only at T10: Jan–May ₹3120.3 (n=204), Jun–Oct ₹13464.18 — the flip is CURED on the LONG side. SHORT-only at T10: Jan–May ₹-3638.04, Jun–Oct ₹6285.64.
Direction configurations passing the full gate: ['T125_S050-LONG', 'T100_S050-LONG', 'T125_S065-LONG'].
**Verdict:** LONG-only is a genuine v2 candidate where marked PASS above.

## Family T4 — CONDITION VARIANTS (P2 pool, row filters)

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| T125_S050 cond=INV1 | 694 | 34.6 | 73.09 | 33.09 | 7255.01 (564) | 15709.29 (130) | 22964.3 | 8490.91 | 10/25 | 141.0 | **PASS** |
| T125_S050 cond=N20 | 563 | 35.7 | 126.03 | 86.03 | 24913.18 (426) | 23523.96 (137) | 48437.14 | 5937.85 | 11/25 | 86.4 | **PASS** |
| T125_S050 cond=DBL | 390 | 34.4 | 82.43 | 42.43 | 7861.57 (297) | 8687.21 (93) | 16548.78 | 8916.58 | 9/25 | 181.3 | no |
| T125_S050 cond=BAND | 399 | 31.8 | 3.55 | -36.45 | -24189.15 (303) | 9646.74 (96) | -14542.41 | 2553.06 | 6/25 | None | no |
New condition variants passing the full gate: ['T125_S050-N20'] (INV1 itself is the reference, not a new variant).
**Verdict:** a condition variant passes — frozen as candidate material below in the summary.

## Family T5 — FEBRUARY DIAGNOSIS (report only — NO filter built)

INV1 February 2026 at T125/S050: n=124, net ₹-21123.92, grossExp ₹-130.35, win 27.4%. Comparators: Jan–May ex-Feb n=440, net ₹28378.93, grossExp ₹104.5; Jun–Oct n=130, net ₹15709.29, grossExp ₹160.84.
- February by direction:
  - LONG: n=39, net ₹-9951.91, grossExp ₹-215.18, win 25.6%
  - SHORT: n=85, net ₹-11172.01, grossExp ₹-91.44, win 28.2%
- Jan–May ex-Feb by direction:
  - LONG: n=161, net ₹24703.03, grossExp ₹193.43, win 38.5%
  - SHORT: n=279, net ₹3675.9, grossExp ₹53.18, win 32.6%
- February by chain round:
  - round1: n=94, net ₹-18205.03, grossExp ₹-153.67, win 26.6%
  - round2: n=30, net ₹-2918.89, grossExp ₹-57.3, win 30.0%
- Jan–May ex-Feb by chain round:
  - round1: n=330, net ₹19336.9, grossExp ₹98.6, win 35.2%
  - round2: n=110, net ₹9042.03, grossExp ₹122.2, win 33.6%
- February by day-gap bucket:
  - +0.3..+1%: n=26, net ₹-1652.05, grossExp ₹-23.54, win 34.6%
  - -0.3..+0.3%: n=41, net ₹-12688.57, grossExp ₹-269.48, win 26.8%
  - -1..-0.3%: n=7, net ₹-656.88, grossExp ₹-53.84, win 28.6%
  - <-1%: n=13, net ₹-2509.61, grossExp ₹-153.05, win 15.4%
  - >+1%: n=37, net ₹-3616.81, grossExp ₹-57.75, win 27.0%
- Jan–May ex-Feb by day-gap bucket:
  - +0.3..+1%: n=102, net ₹9765.09, grossExp ₹135.74, win 38.2%
  - -0.3..+0.3%: n=128, net ₹4469.95, grossExp ₹74.92, win 36.7%
  - -1..-0.3%: n=61, net ₹3037.77, grossExp ₹89.8, win 37.7%
  - <-1%: n=52, net ₹6188.11, grossExp ₹159.0, win 32.7%
  - >+1%: n=97, net ₹4918.01, grossExp ₹90.7, win 27.8%
- February by ADR bucket:
  - ADR 3-4: n=73, net ₹-19002.33, grossExp ₹-220.31, win 24.7%
  - ADR 4-5: n=34, net ₹-137.68, grossExp ₹35.95, win 35.3%
  - ADR 5+: n=17, net ₹-1983.91, grossExp ₹-76.7, win 23.5%
- Jan–May ex-Feb by ADR bucket:
  - ADR 3-4: n=339, net ₹22719.95, grossExp ₹107.02, win 34.8%
  - ADR 4-5: n=79, net ₹7750.41, grossExp ₹138.11, win 39.2%
  - ADR 5+: n=22, net ₹-2091.43, grossExp ₹-55.07, win 18.2%
- February's worst stocks: TVSMOTOR (n=4, ₹-7511.75), GLENMARK (n=6, ₹-5348.45), OBEROIRLTY (n=4, ₹-3178.05), ASTRAL (n=2, ₹-1545.75), BDL (n=12, ₹-1516.08).
- Exit mix Feb: {'square_off': [11, 8.9], 'stop': [86, 69.4], 'target': [27, 21.8]} vs Jan–May ex-Feb: {'square_off': [16, 3.6], 'stop': [284, 64.5], 'target': [140, 31.8]}.
- Medians — day gap %: Feb 0.359 vs JM-ex 0.183 vs JO 0.021; |gap|: Feb 0.609 vs JM-ex 0.674 vs JO 0.577; ADR: Feb 3.713 vs JM-ex 3.588 vs JO 3.274.
**What distinguishes February (in numbers):** both directions lose in February (LONG ₹-9951.91 on 39 trades, SHORT ₹-11172.01 on 85 trades) whereas Jan–May ex-Feb pays on LONGs (₹24703.03); February's gross expectancy is ₹-130.35/trade against ₹104.5 for the rest of Jan–May — the entries themselves were worse, not just the exits (exit mix and round mix in the cuts above). No February filter is built from this — that would be hindsight. Any feature named here (direction mix, gap, ADR, round) is ex-ante knowable, but using it requires its own frozen family on a fresh window, not a patch on this data.

## Family T6 — CHAIN / ENTRY STRUCTURE on INV1 @ T125/S050

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| cap1_cut1030 | 534 | 35.6 | 77.84 | 37.84 | 1131.87 (424) | 19075.23 (110) | 20207.1 | 7970.41 | 8/25 | 151.7 | no |
| cap1_cut1130 | 651 | 34.7 | 55.34 | 15.34 | -3715.74 (518) | 13703.25 (133) | 9987.51 | 5958.63 | 7/25 | 272.1 | no |
| cap2_cut1030 | 694 | 34.6 | 73.09 | 33.09 | 7255.01 (564) | 15709.29 (130) | 22964.3 | 8490.91 | 10/25 | 141.0 | **PASS** |
| cap2_cut1130 | 975 | 33.6 | 46.47 | 6.47 | 3527.4 (799) | 2783.46 (176) | 6310.86 | 6267.53 | 9/25 | 463.2 | no |
| cap3_cut1030 | 742 | 34.4 | 59.78 | 19.78 | -86.74 (604) | 14764.39 (138) | 14677.65 | 9073.41 | 9/25 | 209.4 | no |
| cap3_cut1130 | 1113 | 32.6 | 28.25 | -11.75 | -15996.19 (921) | 2922.84 (192) | -13073.35 | 7951.14 | 6/25 | None | no |
Structure cells passing the full gate: ['cap2_cut1030']. Baseline (cap2, 10:30) is the frozen P2 shape; cap/cutoff changes are v2-candidate material only where marked PASS.
**Verdict:** chain/entry structure yields a passing configuration — see table.

## Loop summary — INV line (all six families scored)

**Pass-gate configurations** (both halves net-positive at ₹40 + breadth ≥10/25 + positive net expectancy):
- **T125/S050 combined INV1** — the frozen baseline itself; it is the ONLY both-halves-positive cell of the 15-cell exit ladder (T1) and the only passing cell of the chain/entry structure grid (T6). The exit ladder and the pool structure are both exhausted at their frozen point: every wider target, wider stop, trail exit, chain-cap change and cutoff change breaks the Jan–May half.
- **INV-LONG (direction restriction) at T125/S050** — 249 trades, +₹24,185.73, halves +₹14,751.12 / +₹9,434.61, expectancy +₹97.13, breadth 12/25 → **frozen as the v2 candidate** in `stocks_inv_v2_candidate_spec.md` (with alternates and a concentration disclosure: TVSMOTOR + GLENMARK ≈ 97% of its net).
- LONG-only also passes at T100/S050 (cures the known T10 Jan–May flip — the flip was entirely SHORT-side) and at T125/S065 (breadth 13/25) — recorded as alternates in the candidate spec.
- N20 condition (= INV2) at T125 passes with the highest totals but is Round 10's pre-existing alternate carrying a 63.6%-from-March concentration warning — not carried, reasons recorded in the candidate spec.

**Near-miss:** DBL condition — both halves positive and balanced (+₹7,861.57 / +₹8,687.21) but breadth 9/25, one stock short of the gate.

**Dead:** both trail exits (Jan–May flips negative); BAND condition (gross expectancy +₹3.55 — the edge lives in the deep-below-50DMA days the band excludes); every non-baseline ladder cell; cap 1 / cap 3 / 11:30 cutoff structures.

**February (T5):** the hole is an ENTRY-quality hole, not an exit or structure hole — February gross expectancy −₹130.35/trade across 124 trades, both directions negative, no gap/ADR/round signature that separates it from the rest of Jan–May (medians near-identical). No filter built.

**November is untouched:** the INV1 shadow runs as frozen. The v2 candidate awaits its own pre-declared fresh window after November's judgement.
## Line 1b — INV-LONG concentration stress + DBL follow-up (spec: frozen file, Line 1b section)

Anchors reproduced to the paisa before scoring: INV-LONG 249 trades, +₹24,185.73 (halves +₹14,751.12 / +₹9,434.61, breadth 12/25); DBL @ T125/S050 390 trades, +₹16,548.78 (halves +₹7,861.57 / +₹8,687.21, breadth 9/25).

INV-LONG per-stock nets behind the concentration warning: TVSMOTOR ₹15287.54, GLENMARK ₹8252.87 — together ₹23540.41 of the ₹24,185.73 total (97.3%).

### Family S1 — INV-LONG concentration stress

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| INV-LONG (reference) | 249 | 36.1 | 137.13 | 97.13 | 14751.12 (200) | 9434.61 (49) | 24185.73 | 7691.08 | 12/25 | 116.2 | **PASS** |
| S1a ex-TVSMOTOR | 237 | 35.0 | 77.55 | 37.55 | 7569.2 (192) | 1328.99 (45) | 8898.19 | 2315.46 | 11/25 | 180.5 | **PASS** |
| S1b ex-GLENMARK | 236 | 35.6 | 107.51 | 67.51 | 11195.27 (193) | 4737.59 (43) | 15932.86 | 4921.58 | 11/25 | 144.9 | **PASS** |
| S1c ex-both | 224 | 34.4 | 42.88 | 2.88 | 4013.35 (185) | -3368.03 (39) | 645.32 | -454.04 | 10/25 | 1546.0 | no |
| S1d winsorised (per-stock cap +₹2,000) | 249 | 36.1 | — | 2.21 | 3053.92 | 631.97 | 551.48 | — | 12/25 | 1088.0 | accounting |

**S1 verdict (pre-declared rule): INV-LONG STANDS WEAKENED.** Ex-both: total ₹645.32, halves ₹4013.35 / ₹-3368.03, expectancy ₹2.88, breadth 10 positive stocks of the remaining 23. Winsorised: total ₹551.48, halves ₹3053.92 / ₹631.97, expectancy ₹2.21 (breadth unchanged by construction — a positive cap cannot flip a stock's sign).

### Family S2 — DBL LONG-only

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DBL LONG-only @ T125_S050 (primary) | 133 | 37.6 | 222.91 | 182.91 | 15426.61 (92) | 8900.76 (41) | 24327.37 | 7957.95 | 10/25 | 129.0 | **PASS** |
| DBL LONG-only @ T100_S050 (shadow) | 139 | 40.3 | 189.99 | 149.99 | 8669.52 (96) | 12178.88 (43) | 20848.4 | 12188.37 | 10/25 | 131.2 | **PASS** |

**S2 verdict:** DBL LONG-only at the primary exit PASSES the full gate — frozen as an additional v2 candidate in stocks_dbl_candidate_spec.md (n=133, halves ₹15426.61 / ₹8900.76, breadth 10/25, expectancy ₹182.91). Shadow exit T100/S050: passes (breadth 10/25).

### Family S3 — DBL both-directions at friendlier exits

| Config | n | Win% | GrossExp ₹ | NetExp ₹ | Jan–May ₹ (n) | Jun–Oct ₹ (n) | Jan–Oct ₹ | Oct ₹ | Breadth | Top-3 % | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| DBL both-dir @ T100_S050 | 407 | 39.1 | 84.68 | 44.68 | 6501.77 (310) | 11684.6 (97) | 18186.37 | 12478.18 | 10/25 | 161.0 | **PASS** |
| DBL both-dir @ T125_S065 | 376 | 38.0 | 57.69 | 17.69 | 2176.91 (284) | 4473.52 (92) | 6650.43 | 7447.67 | 8/25 | 462.0 | no |

**S3 verdict:** passing cell(s): T100_S050 — frozen in stocks_dbl_candidate_spec.md. T100/S050 breadth 10/25 (halves ₹6501.77 / ₹11684.6); T125/S065 breadth 8/25 (halves ₹2176.91 / ₹4473.52).

### Family S4 — INV-LONG month table

| Month | Trades | Net ₹ | Cumulative ₹ | Flag |
|---|---|---|---|---|
| 2026-01 | 41 | 3181.71 | 3181.71 |  |
| 2026-02 | 39 | -9951.91 | -6770.2 | **< −₹3,000** |
| 2026-03 | 61 | 4719.85 | -2050.35 |  |
| 2026-04 | 37 | 3296.63 | 1246.28 |  |
| 2026-05 | 22 | 13504.84 | 14751.12 |  |
| 2026-06 | 18 | -1772.32 | 12978.8 |  |
| 2026-07 | 0 | 0.0 | 12978.8 |  |
| 2026-08 | 1 | -304.35 | 12674.45 |  |
| 2026-09 | 9 | 3820.2 | 16494.65 |  |
| 2026-10 | 21 | 7691.08 | 24185.73 |  |

Months below −₹3,000: ['2026-02']. Top-2 months' share of the Jan–Oct total: 87.6% (the two largest monthly nets sum to ₹21195.92 of ₹24,185.73).

**Line 1b verdict.** INV-LONG **stands weakened**: remove either payer and it still passes the gate on its own (ex-TVSMOTOR +₹8,898.19, breadth 11/25; ex-GLENMARK +₹15,932.86, breadth 11/25), but remove both and the Jun–Oct half flips (−₹3,368.03; total +₹645.32, expectancy +₹2.88), and the winsorised book is a coin-flip (+₹551.48, expectancy +₹2.21, halves +₹3,053.92 / +₹631.97). The candidate's shape survives; its margin does not — outside the two payers there is essentially no edge left in the second half. Its month table (S4) says the same thing in time rather than names: February is the only month below −₹3,000 (−₹9,951.91 — the whole of the T5 February hole is the LONG side's February), July has zero qualifying trades, and two months (May +₹13,504.84, October +₹7,691.08) carry 87.6% of the total. **DBL, by contrast, is promoted**: the LONG-only step lifts the Line 1 near-miss through the full gate at both exits (T125 primary: 133 trades, +₹24,327.37, expectancy +₹182.91 — the highest of any passing configuration in the INV line — breadth exactly 10/25), and DBL both-directions also passes at T100/S050. DBL-LONG is frozen as an additional v2 candidate in `stocks_dbl_candidate_spec.md`, carrying a concentration disclosure as severe as INV-LONG's (TVSMOTOR + GLENMARK = 110.8% of its net). Both candidates now stand or fall on fresh windows, not on more Jan–Oct surgery. November's INV1 shadow is untouched.

