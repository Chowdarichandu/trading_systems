# EKAM-INTRADAY — STOCKS · ROUND 6 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 6: the 2025 Jul–Oct cell.
Spec: `ekam_intraday_stocks_r6_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_stocks_r6_build.py` · Numbers: `ekam_intraday_stocks_r6_results.json`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (stores carry no volume).

## Control — S2 EARLIEST-3 reproduced exactly

All windows, ex-top-3 and November match `ekam_intraday_stocks_r5_results.json`
to the paisa: 2025: 621 trades · **+₹45,300.64** · WR 34.94% · expectancy ₹72.95 ·
2026: 615 trades · **+₹72,605.30** · WR 36.75% · expectancy ₹118.06 ·
November CF: 27 trades · +₹20,662.60 · WR 55.56%.
Timing audit: entry-after-signal asserted on every trade (structural in the
context builder); truncated-series vote recompute 313 checked, **0 mismatches**.

## Step 1 — Anatomy of S2's 2025 Jul–Oct: 252 trades · −₹7,310.17 · WR 35.32%

**By side — the carrier is LONG.**
LONG: 128 trades · **−₹20,082.90** · WR 30.47% · expectancy −₹156.90.
SHORT: 124 trades · **+₹12,772.73** · WR 40.32% · expectancy +₹103.01.
The window's −₹7,310.17 is the LONG side's −₹20,082.90 partly offset by SHORTs.
Mapping check (2026 Jul–Oct by side): LONG 122 trades · **−₹5,012.55** ·
SHORT 133 trades · +₹6,288.40 — LONG is negative there too.

**By month — back-loaded, two red months.**
Jul: 69 · **+₹12,028.60** · WR 49.28% · Aug: 57 · **+₹3,073.60** · WR 38.60% ·
Sep: 66 · **−₹10,186.77** · WR 24.24% · Oct: 60 · **−₹12,225.60** · WR 28.33%.
Sep + Oct = −₹22,412.37 against Jul + Aug = +₹15,102.20.

**By stock — one name exceeds the whole window loss.**
ASTRAL: 43 trades · **−₹11,048.00** · WR 30.23% · GODREJCP: 38 · −₹2,173.40 ·
HDFCBANK: 33 · −₹2,030.00 · HINDCOPPER: 13 · −₹1,614.97 · HINDALCO: 14 · −₹1,104.40.
Top-5 losers sum −₹17,970.77. Only 11 of the 25 names appear in this window's
book at all; the offsets are GLENMARK 52 · +₹7,144.00 and BDL 51 · +₹2,671.10.

**By entry votes — the 5-vote entries bleed, the 6-vote entries earn.**
5 votes: 199 trades · **−₹13,234.47** · WR 32.66% · 6 votes: 53 trades ·
**+₹5,924.30** · WR 45.28%.

## Step 2 — The dial: SIDE DROP (drop LONG everywhere)

The frozen mapping checks the side rule first: LONG is negative in 2025 Jul–Oct
(−₹20,082.90) AND negative in 2026 Jul–Oct (−₹5,012.55, also the weakest side
there). **Dial = drop LONG; the book becomes SHORT-only**, applied at the
candidate list with EARLIEST-3 refilling from SHORT candidates (spec order: the
side rule fired, so the month-concentration branch was not reached — for the
record, Oct's −₹12,225.60 would have met its arithmetic).

## Step 3 — The dialled row (SHORT-only EARLIEST-3)

| Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|
| 2025 | 354 · **−20,387.99** · 34.18% · exp −57.59 | 252 · **+19,705.25** · 38.49% · exp 78.20 | 606 · **−682.74** · 35.97% · exp −1.13 | −19,207.74 | **96.5** |
| 2026 | 339 · **+35,519.84** · 37.17% · exp 104.78 | 253 · **+13,766.15** · 38.34% · exp 54.41 | 592 · **+49,285.99** · 37.67% · exp 83.25 | +27,445.99 | **100.0** |

November CF: 27 trades · **−₹4,210.85** · WR 29.63% (control: +₹20,662.60).

Months 2025 (₹): Jan +8,161.16 · Feb −3,629.27 · Mar −5,938.52 · Apr +1,584.92 ·
May −22,141.49 · Jun +1,575.21 · Jul +14,801.30 · Aug +10,494.75 · Sep −1,186.95 ·
Oct −4,403.85.
Months 2026 (₹): Jan +14,768.80 · Feb +7,311.44 · Mar +21,790.65 · Apr −8,141.40 ·
May −5,809.30 · Jun +5,599.65 · Jul −6,652.20 · Aug +7,318.50 · Sep +14,446.95 ·
Oct −1,347.10.

Placebo draws (min / median / max): 2025 −55,133.94 / −20,356.77 / +4,735.19 ·
2026 −49,248.50 / −21,168.95 / +16,754.90.

## What the dial actually did — two plain facts

**1. The cell is fixed — and the wound moves.** SHORT-only turns 2025 Jul–Oct
from −₹7,310.17 to **+₹19,705.25**. But the same drop turns 2025 Jan–Jun from
the control's +₹52,610.81 to **−₹20,387.99** (May 2025 alone −₹22,141.49):
in early 2025 the LONG side was carrying the book, and refilling its slots with
SHORT candidates manufactures losers. Full-year 2025 lands at **−₹682.74** —
the dial makes the year it was aimed at *worse* than the control's +₹45,300.64.

**2. The LONG bleed is a window property, not a side property.** LONG loses in
Jul–Oct of both years (−₹20,082.90 / −₹5,012.55) and earns in Jan–Jun of both
years (it is most of the control's +₹52,610.81 / +₹71,329.45 there). A side
cannot be dropped for a window. 2026 stays clean under the dial (all five bar
legs pass) but smaller than the control (+₹49,285.99 vs +₹72,605.30), and
November flips from +₹20,662.60 to −₹4,210.85.

## Desired-result bar — checklist verdict (dialled row)

The bar: positive in both years AND both windows of each year AND expectancy
≥ ₹80/trade AND placebo ≥ 95th percentile in both years.

| Year | Year + | Jan–Jun + | Jul–Oct + | Expectancy ≥ 80 | Placebo ≥ 95 | Bar |
|---|---|---|---|---|---|---|
| 2025 | ✗ −682.74 | ✗ −20,387.99 | ✓ +19,705.25 | ✗ −1.13 | ✓ 96.5 | **fail** |
| 2026 | ✓ +49,285.99 | ✓ +35,519.84 | ✓ +13,766.15 | ✓ 83.25 | ✓ 100.0 | pass |

**Bar NOT reached.** The side drop is rejected: it fixes the named cell and
breaks the year that contains it. S2 EARLIEST-3 (the control) remains the
strongest thinned form — 2026 fully clear, 2025 failing on Jul–Oct −₹7,310.17
and expectancy ₹72.95 — and CAND-T5 remains the standing candidate on two-year
totals. The 2025 Jul–Oct cell has now resisted selection (R5), the side drop
(R6), and the 6-vote re-selection (R4): its losses sit in LONG entries, in
Sep–Oct, in 5-vote signals and in one name (ASTRAL) — but every one of those
carriers earns in another window of the same book.
