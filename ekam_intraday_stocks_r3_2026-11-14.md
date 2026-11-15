# EKAM-INTRADAY — STOCKS · ROUND 3 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 3: fix the Jul–Oct wound.
Spec: `ekam_intraday_stocks_r3_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_stocks_r3_build.py` · Numbers: `ekam_intraday_stocks_r3_results.json`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (stores carry no volume).

## Control — CAND-T5 reproduced exactly

All windows, month tables, ex-top-3 and November match
`ekam_intraday_stocks_r2_results.json` to the paisa:
2025: 1,035 trades · **+₹62,164.57** · WR 35.56% · expectancy ₹60.06 ·
2026: 1,025 trades · **+₹63,883.60** · WR 35.71% · expectancy ₹62.33 ·
November CF: 45 trades · +₹24,528.65 · WR 48.89%.
Timing audit: entry-after-signal is structural in the reused contexts; truncated-series
vote recompute 625 checked, **0 mismatches**.

## Step 1 — Anatomy of CAND-T5 (trades · net ₹ · WR)

### (a) Side

| Cell | Year | Jan–Jun | Jul–Oct | Full Jan–Oct |
|---|---|---|---|---|
| LONG | 2025 | 327 · +77,716.68 · 39.45% | 217 · **−19,535.44** · 29.95% | 544 · +58,181.24 · 35.66% |
| LONG | 2026 | 308 · +23,142.50 · 34.09% | 199 · **−16,683.40** · 27.14% | 507 · +6,459.10 · 31.36% |
| SHORT | 2025 | 288 · −14,765.05 · 31.25% | 203 · +18,748.38 · 41.38% | 491 · +3,983.33 · 35.44% |
| SHORT | 2026 | 292 · +43,171.75 · 38.36% | 226 · +14,252.75 · 42.04% | 518 · +57,424.50 · 39.96% |

### (b) Entry hour (by entry stamp)

| Cell | Year | Jan–Jun | Jul–Oct | Full Jan–Oct |
|---|---|---|---|---|
| 09–11 | 2025 | 610 · +63,471.63 · 35.57% | 420 · −787.06 · 35.48% | 1,030 · +62,684.57 · 35.53% |
| 09–11 | 2026 | 600 · +66,314.25 · 36.17% | 425 · −2,430.65 · 35.06% | 1,025 · +63,883.60 · 35.71% |
| 11–13 | 2025 | 0 · 0.00 · — | 0 · 0.00 · — | 0 · 0.00 · — |
| 11–13 | 2026 | 0 · 0.00 · — | 0 · 0.00 · — | 0 · 0.00 · — |
| 13–15 | 2025 | 5 · −520.00 · 40.00% | 0 · 0.00 · — | 5 · −520.00 · 40.00% |
| 13–15 | 2026 | 0 · 0.00 · — | 0 · 0.00 · — | 0 · 0.00 · — |

Essentially every entry is before 11:00 (1,030 of 1,035 in 2025; all 1,025 in 2026) —
the first-signal-per-stock rule plus the 5/day earliest-first cap puts the whole book
in the first bucket. The hour split carries no separable cell.

### (c) Votes at entry (own-direction votes at the signal bar)

| Cell | Year | Jan–Jun | Jul–Oct | Full Jan–Oct |
|---|---|---|---|---|
| 5 | 2025 | 488 · +12,624.12 · 34.22% | 328 · **−13,024.63** · 33.23% | 816 · −400.51 · 33.82% |
| 5 | 2026 | 496 · +44,180.38 · 36.90% | 341 · **−10,976.45** · 33.14% | 837 · +33,203.93 · 35.36% |
| 6 | 2025 | 127 · +50,327.51 · 40.94% | 92 · +12,237.57 · 43.48% | 219 · +62,565.08 · 42.01% |
| 6 | 2026 | 104 · +22,133.87 · 32.69% | 84 · +8,545.80 · 42.86% | 188 · +30,679.67 · 37.23% |

Cross-checks: every split sums to the CAND-T5 totals (full year +62,164.57 / +63,883.60;
Jul–Oct −787.06 / −2,430.65) in both years.

## Wound test (frozen rule: Jul–Oct negative in BOTH years AND full-year negative or
## lowest-in-split in BOTH years)

- **LONG:** Jul–Oct leg passes (−19,535.44 / −16,683.40). Full-year leg FAILS in 2025 —
  LONG's +58,181.24 is the split's BEST full year in 2025 (SHORT is +3,983.33); LONG is
  lowest only in 2026. Not a wound.
- **SHORT:** Jul–Oct is positive in both years (+18,748.38 / +14,252.75). Not a wound.
- **09–11:** Jul–Oct leg passes (it is the whole book's window: −787.06 / −2,430.65).
  Full-year leg FAILS both years — +62,684.57 / +63,883.60, positive and not the split's
  lowest. Not a wound.
- **11–13 / 13–15:** no Jul–Oct trades in either year (Jul–Oct net 0.00, not < 0).
  Not wounds.
- **Votes 5:** Jul–Oct leg passes (−13,024.63 / −10,976.45). Full-year leg passes in
  2025 (−400.51, negative) but FAILS in 2026 — votes-5's +33,203.93 is not negative and
  not the split's lowest (votes-6 is +30,679.67). Not a wound.
- **Votes 6:** Jul–Oct is positive in both years (+12,237.57 / +8,545.80). Not a wound.

**Wounds found: NONE.**

What the anatomy shows, in plain numbers: the book's small Jul–Oct deficit
(−787.06 / −2,430.65) is the NET of two offsetting bleeds — LONG in Jul–Oct
(−19,535.44 / −16,683.40) and votes-5 in Jul–Oct (−13,024.63 / −10,976.45) — largely
paid back inside the same window by SHORT (+18,748.38 / +14,252.75) and votes-6
(+12,237.57 / +8,545.80). Each bleeding cell fails the wound rule on exactly one
full-year leg: LONG is the carrying side of 2025 (Jan–Jun +77,716.68), and votes-5 is
the better full-year cell of 2026. Neither bleed is separable — cutting either cell
removes its carrying window with it.

## Step 2 — The dial

**NO DIAL SCORED.** Per the frozen spec, with no cell meeting the wound rule the
report ends at the anatomy. No candidate was built, so no placebo / month table /
November line exists for a dialed candidate this round.

## Desired-result bar — checklist verdict

No dialed candidate exists this round, so the bar cannot be re-checked on a new row.
On the standing candidate (CAND-T5, from Round 2) the bar remains **NOT reached**:
both years positive ✓ · placebo 100.0 both years ✓ · Jul–Oct negative in both years ✗
(−787.06 / −2,430.65) · expectancy ₹60.06 / ₹62.33 against the ₹80 line ✗.
