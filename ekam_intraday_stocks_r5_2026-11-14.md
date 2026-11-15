# EKAM-INTRADAY — STOCKS · ROUND 5 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 5: the selection turn.
Spec: `ekam_intraday_stocks_r5_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_stocks_r5_build.py` · Numbers: `ekam_intraday_stocks_r5_results.json`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (stores carry no volume).
Every row uses CAND-T5's entries (first ≥5-vote signal per stock-day) and CAND-T5's
exit stack (decay ≤3, stop −1.00%, no cap, 15:10 square-off). **Only the rule that
picks the day's trades out of the candidate list changes.**

## Control — S0 = CAND-T5 reproduced exactly

All windows, month tables, ex-top-3 and November match
`ekam_intraday_stocks_r2_results.json` to the paisa:
2025: 1,035 trades · **+₹62,164.57** · WR 35.56% · expectancy ₹60.06 ·
2026: 1,025 trades · **+₹63,883.60** · WR 35.71% · expectancy ₹62.33 ·
November CF: 45 trades · +₹24,528.65 · WR 48.89%.
Timing audit: entry-after-signal asserted on every trade of every row (structural in
the context builder); truncated-series vote recompute 313 checked, **0 mismatches**.

## The rows

| Row | Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|---|
| S0 earliest-5 | 2025 | 615 · **+62,951.63** · 35.61% · exp 102.36 | 420 · **−787.06** · 35.48% · exp −1.87 | 1,035 · **+62,164.57** · 35.56% · exp 60.06 | +29,064.57 | **100.0** |
| S0 earliest-5 | 2026 | 600 · **+66,314.25** · 36.17% · exp 110.52 | 425 · **−2,430.65** · 35.06% · exp −5.72 | 1,025 · **+63,883.60** · 35.71% · exp 62.33 | +39,713.60 | **100.0** |
| S1 priority-5 | 2025 | 370 · **+53,415.81** · 34.59% · exp 144.37 | 261 · **−11,211.77** · 34.87% · exp −42.96 | 631 · **+42,204.04** · 34.71% · exp 66.88 | +9,104.04 | **100.0** |
| S1 priority-5 | 2026 | 364 · **+71,657.45** · 36.81% · exp 196.86 | 257 · **+910.85** · 36.58% · exp 3.54 | 621 · **+72,568.30** · 36.71% · exp 116.86 | +49,378.30 | **100.0** |
| S2 earliest-3 | 2025 | 369 · **+52,610.81** · 34.69% · exp 142.58 | 252 · **−7,310.17** · 35.32% · exp −29.01 | 621 · **+45,300.64** · 34.94% · exp 72.95 | +12,200.64 | **100.0** |
| S2 earliest-3 | 2026 | 360 · **+71,329.45** · 36.67% · exp 198.14 | 255 · **+1,275.85** · 36.86% · exp 5.00 | 615 · **+72,605.30** · 36.75% · exp 118.06 | +49,415.30 | **100.0** |
| S3 first-hour-only | 2025 | 610 · **+63,471.63** · 35.57% · exp 104.05 | 420 · **−787.06** · 35.48% · exp −1.87 | 1,030 · **+62,684.57** · 35.53% · exp 60.86 | +29,584.57 | **100.0** |
| S3 first-hour-only | 2026 | 600 · **+66,314.25** · 36.17% · exp 110.52 | 425 · **−2,430.65** · 35.06% · exp −5.72 | 1,025 · **+63,883.60** · 35.71% · exp 62.33 | +39,713.60 | **100.0** |

November CF: S0 45 trades · +₹24,528.65 · S1 27 trades · +₹20,662.60 ·
S2 27 trades · +₹20,662.60 (identical to S1 — November's days never separated the
two rules) · S3 45 trades · +₹24,528.65 (identical to S0).

Placebo draws (min / median / max): S0 −77,846.18 / −35,702.45 / +4,594.87 (2025),
−72,880.34 / −36,662.10 / +9,800.95 (2026) · S1 −56,461.40 / −22,317.34 / +11,949.00,
−60,062.40 / −22,800.16 / +10,176.81 · S2 −52,566.95 / −22,325.44 / +13,394.77,
−50,129.44 / −23,052.23 / +11,167.36 · S3 −68,151.40 / −37,363.56 / +2,740.33,
−72,880.34 / −36,662.10 / +9,800.95.

## Month table — best row S3 (frozen rule: highest combined two-year total, ₹126,568.17)

Months 2025 (₹): Jan +26,544.36 · Feb +57.41 · Mar −574.12 · Apr +23,345.86 ·
May +19,136.75 · Jun −5,038.63 · Jul +11,891.30 · Aug +7,592.82 · Sep −7,347.97 ·
Oct −12,923.21.
Months 2026 (₹): Jan +31,421.02 · Feb −10,400.00 · Mar +44,589.25 · Apr −20,326.40 ·
May +6,735.30 · Jun +14,295.08 · Jul −17,194.60 · Aug +7,901.85 · Sep +4,887.25 ·
Oct +1,974.85.
(S3's months differ from the control's only in Jan 2025: +₹520.00 — see below.)

## What the selection turn actually did — three plain facts

**1. The cap race is a first-hour race.** Restricting eligibility to signals stamped
≤ 10:30 (S3) changes almost nothing: 2026 is trade-for-trade identical to the control,
and 2025 differs by exactly 5 trades (+₹520.00). The earliest-5 winners were already
first-hour signals; signals after 10:30 almost never take a cap slot. "First-hour-only"
is not a different book — it is the control with its tail shown to be weightless.

**2. Thinning to the earliest 3 raises expectancy hard — in 2026.** S2 takes ~40% fewer
trades (621 / 615) and its 2026 expectancy nearly doubles (₹62.33 → ₹118.06), its 2026
Jul–Oct turns **positive** (+₹1,275.85, the first positive Jul–Oct in any tuned row of
this family), and its 2026 full total rises to +₹72,605.30 on ~400 fewer trades. S1's
bucket split adds nothing over plain earliest-3: S2 ≥ S1 in both years (+45,300.64 vs
+42,204.04; +72,605.30 vs +72,568.30) — the reserved after-11:00 slots earn ~zero.

**3. The same thinning breaks 2025.** S1/S2 cut 2025's full total by ₹16,864–19,961 and
deepen 2025's Jul–Oct (−₹7,310.17 / −₹11,211.77 vs the control's −₹787.06). In 2025 the
control's near-zero Jul–Oct was produced by the FULL 5-a-day book: the 4th and 5th
daily trades were carrying that window, and removing them removes its winners. The
wound is specific — 2025 Jul–Oct — and selection cannot reach it from either direction:
the full book holds it at −₹787, every thinner book makes it worse, and the 6-vote
re-selection of Round 4 made it −₹18,772.80.

## Desired-result bar — checklist verdict (per row, per year)

The bar: positive in both years AND both windows of each year AND expectancy
≥ ₹80/trade AND placebo ≥ 95th percentile in both years.

| Row | 2025 legs failed | 2026 legs failed | Bar |
|---|---|---|---|
| S0 earliest-5 (control) | Jul–Oct −787.06 · expectancy 60.06 | Jul–Oct −2,430.65 · expectancy 62.33 | **NOT reached** |
| S1 priority-5 | Jul–Oct −11,211.77 · expectancy 66.88 | **none — all five legs pass** | **NOT reached** (2025) |
| S2 earliest-3 | Jul–Oct −7,310.17 · expectancy 72.95 | **none — all five legs pass** | **NOT reached** (2025) |
| S3 first-hour-only | Jul–Oct −787.06 · expectancy 60.86 | Jul–Oct −2,430.65 · expectancy 62.33 | **NOT reached** |

**Bar NOT reached by any row** — but the shape of the failure changed. S1 and S2 are
the first rows in this family to pass a complete year (2026: both windows positive,
expectancy ₹116.86 / ₹118.06, placebo 100.0, ex-top-3 +₹49,378.30 / +₹49,415.30).
What remains is one cell: **2025 Jul–Oct**, negative under every selection rule tried
(control −₹787.06, S3 −₹787.06, S2 −₹7,310.17, S1 −₹11,211.77, R4's 6-vote book
−₹18,772.80) and 2025 expectancy, which thinning lifts only to ₹72.95. CAND-T5 (S0)
remains the standing candidate on two-year totals; S2 is the strongest thinned form
and the first to clear a full year, but it is worse than the control in 2025 and does
not displace it.
