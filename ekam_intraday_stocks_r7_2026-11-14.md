# EKAM-INTRADAY — STOCKS · ROUND 7 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 7: six votes under the
cap-3 selection. Spec: `ekam_intraday_stocks_r7_SPEC.md` (frozen before
scoring). Build: `ekam_intraday_stocks_r7_build.py` · Numbers:
`ekam_intraday_stocks_r7_results.json`. Basis: **equity cash intraday ·
frozen 25-name watchlist · per 100 shares PROVISIONAL · ₹40/trade · paper
only, real money ₹0.** Judged PER YEAR, never pooled. VWAP is the
equal-weighted typical-price proxy (stores carry no volume).

## Control — S2 EARLIEST-3 reproduced exactly

All windows, month tables, ex-top-3 and November match
`ekam_intraday_stocks_r5_results.json` (row S2) to the paisa: 2025: 621
trades · **+₹45,300.64** · WR 34.94% · expectancy ₹72.95 · 2026: 615 trades ·
**+₹72,605.30** · WR 36.75% · expectancy ₹118.06 · November CF: 27 trades ·
+₹20,662.60 · WR 55.56%. Timing audit: entry-after-signal asserted on every
trade (structural in the context builder); truncated-series vote recompute
616 checked, **0 mismatches**. Sanity: S2-T6 is a genuinely different book —
1,109 of its 1,386 (date, stock) entries differ from S2's (later signal,
different side mix), every trade carries exactly 6 votes; trade counts match
S2's only because the EARLIEST-3 cap binds on nearly every day in both books
(pre-cap candidates: 11,224 at T=6 vs 11,549 at T=5).

## The row — S2-T6 (6-of-6 votes, EARLIEST-3, CAND-T5 exits)

| Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|
| 2025 | 369 · **+63,865.42** · 36.31% · exp 173.08 | 252 · **−4,907.73** · 31.75% · exp −19.48 | 621 · **+58,957.69** · 34.46% · exp 94.94 | +27,972.69 | **100.0** |
| 2026 | 360 · **−918.74** · 29.44% · exp −2.55 | 255 · **+16,710.95** · 34.12% · exp 65.53 | 615 · **+15,792.21** · 31.38% · exp 25.68 | −6,327.79 | **100.0** |

November CF: 27 trades · **−₹4,153.65** · WR 29.63% (control: +₹20,662.60).

Months 2025 (₹): Jan +36,058.35 · Feb +4,185.87 · Mar −4,477.90 ·
Apr +1,986.70 · May +14,256.50 · Jun +11,855.90 · Jul −4,742.70 ·
Aug −3,550.43 · Sep −562.09 · Oct +3,947.49.
Months 2026 (₹): Jan −3,656.37 · Feb +4,068.30 · Mar −465.30 · Apr −93.80 ·
May −7,134.02 · Jun +6,362.45 · Jul −1,046.15 · Aug +1,360.45 ·
Sep +6,734.00 · Oct +9,662.65.

Placebo draws (min / median / max): 2025 −52,566.95 / −22,325.44 /
+13,394.77 · 2026 −50,129.44 / −23,052.23 / +11,167.36.

## What the combination actually did — two plain facts

**1. It improves the year it was diagnosed on.** Against the control, 2025
rises to +₹58,957.69 (from +₹45,300.64), expectancy clears the ₹80 line for
the first time in the thinned family (₹94.94), and the Jul–Oct wound shrinks
from −₹7,310.17 to −₹4,907.73 — but does not close: Jul (−₹4,742.70) and Aug
(−₹3,550.43) stay red. The 6-vote entries inside the cell did earn in R6's
anatomy (+₹5,924.30); re-selecting the whole book at 6 votes keeps only part
of that, because EARLIEST-3 now refills the freed slots with other days'
6-vote candidates.

**2. It breaks the other year.** 2026 falls from +₹72,605.30 to +₹15,792.21:
Jan–Jun flips negative (−₹918.74 against the control's +₹71,329.45),
expectancy drops to ₹25.68, ex-top-3 goes negative (−₹6,327.79), and
November flips from +₹20,662.60 to −₹4,153.65. The 6-vote gate is
window-unstable in the same way the side drop was: it helps where it was
measured and hurts where it wasn't. Round 4's cap-5 version of this gate
showed the same signature from the other side.

## Desired-result bar — checklist verdict (S2-T6)

The bar: positive in both years AND both windows of each year AND expectancy
≥ ₹80/trade AND placebo ≥ 95th percentile in both years.

| Year | Year + | Jan–Jun + | Jul–Oct + | Expectancy ≥ 80 | Placebo ≥ 95 | Bar |
|---|---|---|---|---|---|---|
| 2025 | ✓ +58,957.69 | ✓ +63,865.42 | ✗ −4,907.73 | ✓ 94.94 | ✓ 100.0 | **fail** |
| 2026 | ✓ +15,792.21 | ✗ −918.74 | ✓ +16,710.95 | ✗ 25.68 | ✓ 100.0 | **fail** |

**Bar NOT reached.** S2-T6 is rejected as the channel: it is better than the
control in 2025 and far worse in 2026, and it turns November negative. S2
EARLIEST-3 (the control) remains the strongest thinned form — 2026 fully
clear, 2025 failing on Jul–Oct −₹7,310.17 and expectancy ₹72.95 — and
CAND-T5 remains the standing candidate on two-year totals. The 2025 Jul–Oct
cell has now resisted selection (R5), the side drop (R6) and the 6-vote gate
under both caps (R4, R7): every carrier identified inside it — LONG side,
5-vote entries, Sep–Oct, ASTRAL — earns in another window of the same book.
