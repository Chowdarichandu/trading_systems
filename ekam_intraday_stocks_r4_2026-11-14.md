# EKAM-INTRADAY — STOCKS · ROUND 4 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 4: the 6-vote turn.
Spec: `ekam_intraday_stocks_r4_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_stocks_r4_build.py` · Numbers: `ekam_intraday_stocks_r4_results.json`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (stores carry no volume).

## Control — CAND-T5 reproduced exactly

All windows, month tables, ex-top-3 and November match
`ekam_intraday_stocks_r2_results.json` to the paisa:
2025: 1,035 trades · **+₹62,164.57** · WR 35.56% · expectancy ₹60.06 ·
2026: 1,025 trades · **+₹63,883.60** · WR 35.71% · expectancy ₹62.33 ·
November CF: 45 trades · +₹24,528.65 · WR 48.89%.
Timing audit: entry-after-signal asserted on every CAND-T6 trade (structural in the
context builder); truncated-series vote recompute 616 checked, **0 mismatches**.

## The turn — CAND-T6 (entry requires the full 6 of 6 votes; exit stack unchanged)

Exit stack identical to CAND-T5: vote-decay exit at own votes ≤ 3, hard stop −1.00%,
no cap, square-off 15:15 basis (15:10 bar close). Entry is a genuine re-selection at
T=6, not a filter on the CAND-T5 trades.

**First plain fact: the trade count did not fall.** CAND-T6 takes 1,035 trades in
2025 and 1,025 in 2026 — exactly CAND-T5's counts. The 5/day cap is saturated in both
books: on essentially every trading day at least five names reach a 6-vote bar, so
requiring 6 votes does not thin the book — it **re-selects** it. Entries come later in
the day (the 6th vote arrives after the 5th) and the day-cap slots go to a different
mix of names and times than the first-≥5 race produced.

| Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|
| 2025 | 615 · **+72,825.19** · 36.10% · exp 118.41 | 420 · **−18,772.80** · 30.95% · exp −44.70 | 1,035 · **+54,052.39** · 34.01% · exp 52.22 | +23,067.39 | **100.0** (draws −77,846.18 / −35,702.45 / +4,594.87) |
| 2026 | 600 · **−5,987.35** · 31.67% · exp −9.98 | 425 · **+23,508.71** · 32.00% · exp 55.31 | 1,025 · **+17,521.36** · 31.80% · exp 17.09 | −7,248.64 | **100.0** (draws −72,880.34 / −36,662.10 / +9,800.95) |

Months 2025 (₹): Jan +49,245.05 · Feb +21,334.64 · Mar −7,291.15 · Apr −6,652.50 ·
May +7,788.25 · Jun +8,400.90 · Jul −9,805.20 · Aug −3,648.35 · Sep −1,802.09 ·
Oct −3,517.16.
Months 2026 (₹): Jan −9,347.77 · Feb −1,051.95 · Mar −7,369.11 · Apr +3,910.85 ·
May −8,380.02 · Jun +16,250.65 · Jul −2,775.40 · Aug −931.44 · Sep +4,402.30 ·
Oct +22,813.25.
November CF: 45 trades · **+₹962.75** · WR 33.33% · expectancy ₹21.39.

## Against the control, and against the anatomy that motivated the turn

| Line | CAND-T5 | CAND-T6 |
|---|---|---|
| 2025 full | +62,164.57 | +54,052.39 |
| 2025 Jul–Oct | −787.06 | **−18,772.80** |
| 2026 full | +63,883.60 | +17,521.36 |
| 2026 Jan–Jun | +66,314.25 | **−5,987.35** |
| 2026 Jul–Oct | −2,430.65 | +23,508.71 |
| November CF | +24,528.65 | +962.75 |

The turn made both years worse, and it did not fix the wound it aimed at: 2025's
Jul–Oct went from −787.06 to −18,772.80. The reason is visible in the counts. The
anatomy's 6-vote rows (+12,237.57 / +8,545.80 in Jul–Oct) were a SUBSET of the
CAND-T5 book — trades that had already won the first-≥5-signal race and the day cap
against 5-vote competition, and happened to print 6 at entry. The standalone T6 book
is a different set: it admits every name's later 6-vote signal (including signals
that arrive after the move is extended) and reshuffles the cap, so the subset's
numbers do not transfer. A layer that looks strong inside a book is not the same
book restricted to that layer. 2026 adds a second warning: ex-top-3 is **−7,248.64**
— the year's +17,521.36 is carried by its three largest trades.

## Desired-result bar — checklist verdict (per year)

The bar: positive in both years AND both windows of each year AND expectancy
≥ ₹80/trade AND placebo ≥ 95th percentile in both years.

| Leg | 2025 | 2026 |
|---|---|---|
| Year positive | ✓ +54,052.39 | ✓ +17,521.36 |
| Jan–Jun positive | ✓ +72,825.19 | ✗ −5,987.35 |
| Jul–Oct positive | ✗ −18,772.80 | ✓ +23,508.71 |
| Expectancy ≥ ₹80 | ✗ 52.22 | ✗ 17.09 |
| Placebo ≥ 95 | ✓ 100.0 | ✓ 100.0 |

**Bar NOT reached — in either year.** Each year fails two legs, and the legs it
fails are mirror images (2025 fails Jul–Oct, 2026 fails Jan–Jun): the 6-vote book
has no stable window. CAND-T6 is worse than the CAND-T5 control on the full year in
both years (+54,052.39 vs +62,164.57; +17,521.36 vs +63,883.60), worse in November
(+962.75 vs +24,528.65), and its 2026 ex-top-3 is negative. The 6-vote turn is
rejected; CAND-T5 remains the standing candidate of this family.
