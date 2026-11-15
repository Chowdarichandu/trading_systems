# HOLD PROGRAMME — ROUND 2 RESULTS · 2026-11-15

Spec: `hold_programme_r2_SPEC.md` (frozen before scoring). Build:
`hold_programme_r2_build.py` · Data: `hold_programme_r2_results.json` ·
Best-cell trades: `hold_programme_r2_best_cell_trades.csv`.
Basis: equity cash, LONG only, frozen 25 names, daily candles to 2026-11-13,
**per 100 shares PROVISIONAL**, ₹40 per completed position, paper only,
real money ₹0. Judged per year, never pooled. Engine, windows, WMARK marking
and stats are Round 1's verbatim; only the RSI cross-up level moves.

**CONTROL CHECK — L35-H15 reproduced Round 1's E1-H15 EXACTLY:**
2025: 83 trades · +₹42,163 · 2026: 103 trades · +₹83,963. ✓

## The grid — RSI cross-up level × hold (net ₹ per year)

### Level 30 (shallower dip)

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H10 | 53 | −9,092 | 41.5 | −0.57 | −14,940 | −39,350 | 64 | −7,122 | 39.1 | −0.37 | −10,500 | −44,706 |
| H15 | 50 | −35,752 | 46.0 | −0.27 | −24,230 | −97,232 | 57 | +18,351 | 38.6 | −0.35 | −13,345 | −34,319 |
| H20 | 47 | −2,167 | 46.8 | +0.25 | −20,735 | −47,330 | 53 | +34,323 | 37.7 | −0.12 | −11,040 | −36,019 |

### Level 35 (control level)

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H10 | 96 | +13,864 | 61.5 | +1.06 | −21,740 | −59,224 | 121 | −11,306 | 40.5 | −0.31 | −9,390 | −107,798 |
| **H15 (CONTROL)** | **83** | **+42,163** | **63.9** | **+1.47** | **−24,230** | **−56,175** | **103** | **+83,963** | **41.7** | **−0.16** | **−9,890** | **−88,109** |
| H20 | 73 | +1,020 | 56.2 | +0.98 | −41,750 | −105,455 | 94 | +82,570 | 42.6 | −0.33 | −14,740 | −128,652 |

### Level 40 (deeper dip)

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H10 | 151 | −7,769 | 52.3 | −0.00 | −24,640 | −128,498 | 160 | +22,631 | 41.2 | +0.19 | −23,540 | −129,325 |
| H15 | 132 | +38,372 | 52.3 | +0.32 | −25,440 | −124,166 | 140 | −8,944 | 41.4 | +0.05 | −29,540 | −138,783 |
| H20 | 112 | +101,255 | 62.5 | +0.97 | −31,840 | −125,678 | 124 | −9,567 | 42.7 | −0.31 | −19,540 | −141,932 |

## Best cell by the frozen rule: L35-H15 — the control itself

Only two cells are positive in both years: L35-H15 (+₹42,163 / +₹83,963,
combined +₹126,126) and L35-H20 (+₹1,020 / +₹82,570, combined +₹83,590).
The control is the higher of the two.

**Did any cell beat the control in BOTH years? NO.** Every neighbour loses
to the control in at least one year: L40-H20 makes far more in 2025
(+₹101,255) but is negative in 2026 (−₹9,567); L30 improves nothing in 2025
at any hold; shortening the hold to H10 kills 2026 at both levels 35 and 30.

### Best cell (L35-H15) — the extra checks
- **Placebo:** 97.6th percentile (1,000 random-entry draws, same stocks /
  counts / hold; median draw −₹97,448 vs the real +₹126,126 combined).
- **Ex-top-3:** 2025 **−₹34,527** (the year's +₹42,163 is carried by its
  three biggest trades — without them the year is negative) · 2026
  **+₹5,073** (the +₹83,963 also leans heavily on its top 3).
- **Month table (by entry month):**

| Month | 2025 trades | 2025 net ₹ | Month | 2026 trades | 2026 net ₹ |
|---|---|---|---|---|---|
| Jan | 21 | +7,360 | Jan | 4 | −2,478 |
| Feb | 9 | +1,870 | Feb | 5 | −4,775 |
| Mar | 11 | +26,195 | Mar | 15 | +100,733 |
| Apr | 7 | +10,863 | Apr | 3 | +21,018 |
| May | 0 | 0 | May | 5 | −4,484 |
| Jun | 4 | +18,561 | Jun | 15 | +10,530 |
| Jul | 4 | −32,150 | Jul | 12 | −3,295 |
| Aug | 13 | −22,110 | Aug | 6 | −15,895 |
| Sep | 10 | +22,154 | Sep | 16 | −34,592 |
| Oct | 4 | +9,420 | Oct | 22 | +17,201 |

  One month — March 2026, +₹100,733 — exceeds the whole 2026 year net:
  outside March, 2026 sums to −₹16,770.

- **Its November trades (Nov 2–13): 2 positions, both still OPEN** (the
  15-day hold runs past the data; marked at the 2026-11-13 close):

| Stock | Entry date | Entry ₹ | Marked exit (2026-11-13) ₹ | Net ₹ | Status |
|---|---|---|---|---|---|
| BDL | 2026-11-04 | 1,010.10 | 1,030.00 | +1,950 | OPEN/MARKED |
| HINDCOPPER | 2026-11-05 | 432.00 | 439.40 | +700 | OPEN/MARKED |
| **Total (marked)** | | | | **+2,650** | |

## Reading (numbers only)

- The neighbourhood confirms the control rather than improving it: level 35
  is a local peak — 30 is too shallow (2025 negative at every hold), 40 is
  too deep (2026 negative at H15 and H20 despite the biggest 2025 of the
  grid, +₹101,255 at H20).
- H15 stays the hold: H10 loses 2026 at levels 30 and 35; H20 roughly ties
  H15 in 2026 at level 35 (+₹82,570 vs +₹83,963) but collapses 2025 to
  +₹1,020.
- Concentration is the standing weakness, unchanged by tuning: ex-top-3 is
  negative in 2025 and barely positive in 2026, and one entry month
  (Mar 2026) carries more than the 2026 year. Max drawdown −₹56,175 /
  −₹88,109 against nets of +₹42,163 / +₹83,963.
