# EKAM-INTRADAY — STOCKS · ROUND 2 RESULTS · 2026-11-14

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 2: tune the vote-decay exit.
Spec: `ekam_intraday_stocks_r2_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_stocks_r2_build.py` · Numbers: `ekam_intraday_stocks_r2_results.json`.
Basis: **equity cash intraday · frozen 25-name watchlist · per 100 shares PROVISIONAL ·
₹40/trade · paper only, real money ₹0.** Judged PER YEAR, never pooled.
VWAP is the equal-weighted typical-price proxy (stores carry no volume).
Entries are Round 1 verbatim — only the X2 exit dials moved, one at a time.

## Control — reproduced exactly

T4-X2 and T5-X2 match the published Round 1 lines on every window and on November
(trades, total, WR all equal): T4-X2 2025 +₹20,559.40 / 2026 +₹51,453.37 ·
T5-X2 2025 +₹36,834.57 / 2026 +₹34,966.66 · November +₹13,261.40 / +₹18,563.30.
Timing audit: entry-after-signal asserted on all 2,060 trades; truncated-series vote
recompute 625 checked, **0 mismatches**. Trade counts never change in this round
(exits only): 1,035 per row in 2025, 1,025 in 2026.

## Dial 1 — decay level (stop 0.75%, no cap). Full-year: trades · net ₹ · WR · expectancy ₹

| Base | Setting | 2025 | 2026 |
|---|---|---|---|
| T4 | decay ≤1 (later) | 1,035 · **+51,095.01** · 34.98% · 49.37 | 1,025 · **+40,648.71** · 34.24% · 39.66 |
| T4 | decay ≤2 (base) | 1,035 · +20,559.40 · 32.66% · 19.86 | 1,025 · +51,453.37 · 33.37% · 50.20 |
| T4 | decay ≤3 (earlier) | 1,035 · +27,434.02 · 33.14% · 26.51 | 1,025 · +49,909.09 · 33.37% · 48.69 |
| T5 | decay ≤1 (later) | 1,035 · **+62,667.47** · 34.98% · 60.55 | 1,025 · +18,960.70 · 34.15% · 18.50 |
| T5 | decay ≤2 (base) | 1,035 · +36,834.57 · 33.14% · 35.59 | 1,025 · +34,966.66 · 33.66% · 34.11 |
| T5 | decay ≤3 (earlier) | 1,035 · +45,059.20 · 33.82% · 43.54 | 1,025 · **+36,749.41** · 33.85% · 35.85 |

Windows (net ₹): T4-D1: 2025 Jan–Jun +59,134.91 / Jul–Oct −8,039.90; 2026 +40,287.21 /
+361.50. T5-D1: 2025 +59,511.16 / **+3,156.31** (the only decay row with a positive 2025
Jul–Oct); 2026 +41,295.41 / −22,334.71. T5-D3: 2025 +46,107.04 / −1,047.84; 2026
+45,216.54 / −8,467.13.
**Frozen-rule winners: T4 → decay ≤1 · T5 → decay ≤3** (T5 by ₹181 of combined total
over ≤1 — ≤1 owns 2025, ≤3 owns 2026).

## Dial 2 — hard stop (decay ≤2, no cap). Full-year: trades · net ₹ · WR · expectancy ₹

| Base | Setting | 2025 | 2026 |
|---|---|---|---|
| T4 | stop −0.50% | 1,035 · −9,549.84 · 28.99% · −9.23 | 1,025 · +8,299.00 · 29.56% · 8.10 |
| T4 | stop −0.75% (base) | 1,035 · +20,559.40 · 32.66% · 19.86 | 1,025 · +51,453.37 · 33.37% · 50.20 |
| T4 | stop −1.00% | 1,035 · **+42,431.32** · 34.30% · 41.00 | 1,025 · **+64,493.15** · 34.93% · 62.92 |
| T5 | stop −0.50% | 1,035 · +22,491.99 · 29.28% · 21.73 | 1,025 · +4,663.79 · 29.56% · 4.55 |
| T5 | stop −0.75% (base) | 1,035 · +36,834.57 · 33.14% · 35.59 | 1,025 · +34,966.66 · 33.66% · 34.11 |
| T5 | stop −1.00% | 1,035 · **+52,091.63** · 34.98% · 50.33 | 1,025 · **+69,123.45** · 35.71% · 67.44 |

Windows (net ₹): T4-S1.00: 2025 +59,733.97 / −17,302.65; 2026 +47,430.90 / +17,062.25.
T5-S1.00: 2025 +57,440.24 / −5,348.61; 2026 +76,101.45 / −6,978.00.
**Frozen-rule winners: T4 → −1.00% · T5 → −1.00%.** The −0.50% stop is too tight at both
bases (win rate drops to ~29% — it cuts trades the decay exit would have recovered).

## Dial 3 — profit cap +1.5% (decay ≤2, stop 0.75%). Full-year net ₹

| Base | No cap (base) | Cap +1.5% |
|---|---|---|
| T4 | 2025 +20,559.40 · 2026 +51,453.37 | 2025 **−37,988.38** · 2026 +29,387.31 |
| T5 | 2025 +36,834.57 · 2026 +34,966.66 | 2025 **−17,317.28** · 2026 **−1,326.15** |

**Frozen-rule winner at both bases: no cap.** The cap amputates exactly the runners the
decay exit exists to ride — it turns 2025 negative at both bases.

## Candidates (combined-after-steps — the step winners combined, NOT a fresh discovery)

### CAND-T4 — decay ≤1, stop −1.00%, no cap

| Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|
| 2025 | 615 · +74,012.36 · 38.86% | 420 · −11,119.55 · 33.57% | 1,035 · **+62,892.81** · 36.71% · exp 60.77 | +27,662.81 | **100.0** (draws −81,620.86 / −35,582.55 / +12,403.45) |
| 2026 | 600 · +52,552.30 · 35.83% | 425 · −3,097.95 · 36.24% | 1,025 · **+49,454.35** · 36.00% · exp 48.25 | +22,454.35 | **100.0** (draws −83,298.85 / −34,636.95 / +7,001.37) |

Months 2025 (₹): Jan +45,648.98 · Feb +17,023.35 · Mar +7,774.35 · Apr +13,783.47 ·
May +7,962.21 · Jun −18,180.00 · Jul −8,796.90 · Aug −2,673.00 · Sep +12,951.30 ·
Oct −12,600.95.
Months 2026 (₹): Jan +5,124.25 · Feb −1,086.60 · Mar +48,077.80 · Apr −20,478.70 ·
May +23,268.25 · Jun −2,352.70 · Jul −12,931.75 · Aug +8,873.20 · Sep +7,959.65 ·
Oct −6,999.05.
November CF: 45 trades · **+12,939.45** · WR 40.00%.

### CAND-T5 — decay ≤3, stop −1.00%, no cap

| Year | Jan–Jun | Jul–Oct | Full Jan–Oct | Ex-top-3 | Placebo |
|---|---|---|---|---|---|
| 2025 | 615 · +62,951.63 · 35.61% | 420 · −787.06 · 35.48% | 1,035 · **+62,164.57** · 35.56% · exp 60.06 | +29,064.57 | **100.0** (draws −77,846.18 / −35,702.45 / +4,594.87) |
| 2026 | 600 · +66,314.25 · 36.17% | 425 · −2,430.65 · 35.06% | 1,025 · **+63,883.60** · 35.71% · exp 62.33 | +39,713.60 | **100.0** (draws −72,880.34 / −36,662.10 / +9,800.95) |

Months 2025 (₹): Jan +26,024.36 · Feb +57.41 · Mar −574.12 · Apr +23,345.86 ·
May +19,136.75 · Jun −5,038.63 · Jul +11,891.30 · Aug +7,592.82 · Sep −7,347.97 ·
Oct −12,923.21.
Months 2026 (₹): Jan +31,421.02 · Feb −10,400.00 · Mar +44,589.25 · Apr −20,326.40 ·
May +6,735.30 · Jun +14,295.08 · Jul −17,194.60 · Aug +7,901.85 · Sep +4,887.25 ·
Oct +1,974.85.
November CF: 45 trades · **+24,528.65** · WR 48.89%.

## Desired-result bar — NOT reached

The bar: positive in both years AND both windows of each year AND expectancy ≥ ₹80/trade
AND placebo ≥ 95th pct in both years.

| Leg | CAND-T4 | CAND-T5 |
|---|---|---|
| Both years positive | ✓ (+62,892.81 / +49,454.35) | ✓ (+62,164.57 / +63,883.60) |
| Both windows, each year | ✗ Jul–Oct negative all four years (−11,119.55 / −3,097.95) | ✗ Jul–Oct negative all four years (−787.06 / −2,430.65) |
| Expectancy ≥ ₹80 | ✗ 60.77 / 48.25 | ✗ 60.06 / 62.33 |
| Placebo ≥ 95th pct | ✓ 100.0 / 100.0 | ✓ 100.0 / 100.0 |

**No row reaches the bar.** What the round did, in plain numbers: combining the step
winners lifted T4's 2025 from +20,559.40 to +62,892.81 and T5's two years from
+36,834.57 / +34,966.66 to +62,164.57 / +63,883.60, with ex-top-3 positive in all four
candidate-years and placebos at 100.0 throughout. What still fails is one shape, in
every row of the round: **Jan–Jun carries the year and Jul–Oct gives a slice back** —
the candidates' Jul–Oct lines (−787.06 to −11,119.55) are far better than the bases'
(−3,634.81 to −19,365.34) but still negative, and expectancy tops out at ₹62.33 against
the ₹80 line. The dials left in this family, if tuning continues: the decay/stop
interaction was only combined once (steps were one-at-a-time), and no dial in this round
touched the Jul–Oct window specifically.
