# EKAM-INTRADAY STOCKS — TRAILING-STOP VARIANT — RESULTS (2026-11-16)

Spec: `ekam_intraday_trailing_SPEC.md` (frozen before scoring). Build:
`ekam_intraday_trailing_build.py`. Entries verbatim from the frozen R1/R2/R5
machinery; the ONLY change is a trailing stop added on top of the frozen exits
(activation A over entry, trail distance TD below the running peak; hard stop
−1.00% until the trail arms; vote-decay ≤3 and 15:10 square-off unchanged).
Basis: equity cash intraday, per 100 shares provisional, ₹40/trade, paper only.

**Control reproduced exactly, to the paisa, before any variant was scored** —
Cand-1: 2025 +₹62,164.57 · 2026 +₹63,883.60 · Nov +₹24,528.65. Cand-2: 2025
+₹45,300.64 · 2026 +₹72,605.30 · Nov +₹20,662.60. The reason-annotated exit
replica also matched the frozen `net_of` on all 3,696 candidate trades.

## Verdict in plain numbers

- **Grid points beating the control in BOTH years: NONE (0 of 9, either candidate).**
  No point beats the control in even one single year.
- **Grid points beating the control in November: NONE.**
- **Grid points beating the control on expectancy in both years: NONE** — expectancy
  is below the control at every point in both years; 2025 expectancy is negative at
  all 18 candidate-points.
- The trail raises the win rate (35% → 39–56%) and shrinks the wins: these books are
  payoff-shaped — the profit sits in a few big runners that ride to the vote-decay
  exit, and the trail cuts exactly those. Least-bad point on both candidates is
  A +1.00% / TD 0.75% (latest activation, widest trail) — still far below control
  everywhere (Cand-1 2026 +₹21,790 vs control +₹63,884; Cand-2 2026 +₹56,507 vs
  control +₹72,605; both negative in 2025).

Caveat: this is a 9-point grid scored on the same data the candidates were tuned on
(selection bias) — stated for the record; it changes nothing here since no point won.

## Cand-1 (CAND-T5, earliest 5/day) — 1,035 trades 2025 · 1,025 trades 2026 · 45 Nov

| Variant | 2025 total | exp | WR | Jan–Jun | Jul–Oct | ex-top-3 | worst | 2026 total | exp | WR | Jan–Jun | Jul–Oct | ex-top-3 | worst | Nov 2–13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTROL | +62,164.57 | 60.06 | 35.56 | +62,951.63 | −787.06 | +29,064.57 | −2,289.80 | +63,883.60 | 62.33 | 35.71 | +66,314.25 | −2,430.65 | +39,713.60 | −2,511.60 | +24,528.65 |
| A0.50/TD0.40 | −33,848.01 | −32.70 | 50.53 | −16,844.09 | −17,003.93 | −44,492.69 | −2,283.20 | +12,386.09 | 12.08 | 52.59 | +12,196.17 | +189.91 | −3,329.79 | −2,511.60 | +6,964.92 |
| A0.50/TD0.50 | −32,659.24 | −31.55 | 46.76 | −18,975.64 | −13,683.59 | −44,603.29 | −2,283.20 | +9,519.62 | 9.29 | 50.15 | +4,169.24 | +5,350.38 | −5,757.28 | −2,511.60 | +8,065.58 |
| A0.50/TD0.75 | −30,508.03 | −29.48 | 38.94 | −20,365.26 | −10,142.77 | −49,022.66 | −2,283.20 | −3,276.54 | −3.20 | 38.73 | +3,307.64 | −6,584.18 | −21,507.79 | −2,511.60 | +12,568.93 |
| A0.75/TD0.40 | −33,462.43 | −32.33 | 44.35 | −18,710.43 | −14,752.01 | −44,952.31 | −2,289.80 | −592.90 | −0.58 | 43.71 | +10,763.67 | −11,356.57 | −16,308.78 | −2,511.60 | +10,493.82 |
| A0.75/TD0.50 | −33,143.89 | −32.02 | 44.35 | −21,547.12 | −11,596.77 | −45,087.94 | −2,289.80 | −558.87 | −0.55 | 43.71 | +3,822.73 | −4,381.60 | −15,835.77 | −2,511.60 | +12,982.83 |
| A0.75/TD0.75 | −22,542.38 | −21.78 | 42.03 | −16,863.73 | −5,678.65 | −41,057.00 | −2,289.80 | +8,501.73 | 8.29 | 42.15 | +14,166.47 | −5,664.74 | −9,729.52 | −2,511.60 | +14,880.06 |
| A1.00/TD0.40 | −21,864.05 | −21.12 | 40.19 | −13,414.62 | −8,449.43 | −33,512.81 | −2,289.80 | +10,086.93 | 9.84 | 39.22 | +16,079.10 | −5,992.17 | −5,628.95 | −2,511.60 | +13,076.18 |
| A1.00/TD0.50 | −20,330.03 | −19.64 | 40.19 | −10,895.83 | −9,434.20 | −36,795.08 | −2,289.80 | +5,459.63 | 5.33 | 39.22 | +8,198.33 | −2,738.70 | −9,817.27 | −2,511.60 | +13,350.38 |
| A1.00/TD0.75 | −3,705.47 | −3.58 | 40.19 | +3,465.56 | −7,171.03 | −23,627.22 | −2,289.80 | +21,790.48 | 21.26 | 39.22 | +24,277.65 | −2,487.16 | +3,559.23 | −2,511.60 | +14,539.21 |

November worst single trade: −₹1,970.00 at the control and at every grid point
(the month's worst trade never arms the trail).

## Cand-2 (S2, earliest 3/day) — 621 trades 2025 · 615 trades 2026 · 27 Nov

| Variant | 2025 total | exp | WR | Jan–Jun | Jul–Oct | ex-top-3 | worst | 2026 total | exp | WR | Jan–Jun | Jul–Oct | ex-top-3 | worst | Nov 2–13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| CONTROL | +45,300.64 | 72.95 | 34.94 | +52,610.81 | −7,310.17 | +12,200.64 | −2,289.80 | +72,605.30 | 118.06 | 36.75 | +71,329.45 | +1,275.85 | +49,415.30 | −2,511.60 | +20,662.60 |
| A0.50/TD0.40 | −40,552.60 | −65.30 | 50.72 | −21,080.97 | −19,471.63 | −49,834.20 | −2,209.00 | +38,239.85 | 62.18 | 55.28 | +28,396.47 | +9,843.37 | +22,523.97 | −2,511.60 | +3,685.10 |
| A0.50/TD0.50 | −40,396.43 | −65.05 | 47.67 | −23,168.32 | −17,228.11 | −50,958.93 | −2,209.00 | +30,562.34 | 49.69 | 53.17 | +18,854.26 | +11,708.08 | +15,285.44 | −2,511.60 | +3,803.30 |
| A0.50/TD0.75 | −37,503.18 | −60.39 | 38.49 | −24,013.09 | −13,490.09 | −56,017.80 | −2,209.00 | +21,384.77 | 34.77 | 40.49 | +19,987.51 | +1,397.26 | +3,153.52 | −2,511.60 | +9,511.13 |
| A0.75/TD0.40 | −43,026.67 | −69.29 | 43.80 | −25,612.90 | −17,413.77 | −52,308.27 | −2,289.80 | +37,208.44 | 60.50 | 45.85 | +33,417.43 | +3,791.01 | +21,492.56 | −2,511.60 | +7,214.00 |
| A0.75/TD0.50 | −40,076.41 | −64.54 | 43.80 | −25,657.68 | −14,418.73 | −50,638.91 | −2,289.80 | +30,883.91 | 50.22 | 45.85 | +25,018.91 | +5,865.00 | +15,607.01 | −2,511.60 | +8,720.55 |
| A0.75/TD0.75 | −29,606.72 | −47.68 | 41.71 | −21,049.18 | −8,557.54 | −48,121.34 | −2,289.80 | +38,945.01 | 63.33 | 45.04 | +34,808.72 | +4,136.29 | +20,713.76 | −2,511.60 | +11,822.26 |
| A1.00/TD0.40 | −28,097.90 | −45.25 | 39.45 | −18,211.89 | −9,886.01 | −37,876.62 | −2,289.80 | +48,721.82 | 79.22 | 41.63 | +36,505.43 | +12,216.39 | +33,005.94 | −2,511.60 | +8,346.16 |
| A1.00/TD0.50 | −28,012.52 | −45.11 | 39.45 | −18,483.07 | −9,529.44 | −39,917.82 | −2,289.80 | +38,739.28 | 62.99 | 41.63 | +27,565.88 | +11,173.40 | +23,462.38 | −2,511.60 | +9,071.30 |
| A1.00/TD0.75 | −15,344.38 | −24.71 | 39.45 | −6,037.53 | −9,306.85 | −33,859.01 | −2,289.80 | +56,507.17 | 91.88 | 41.63 | +47,020.42 | +9,486.75 | +38,275.92 | −2,511.60 | +11,046.96 |

November worst single trade: −₹1,970.00 at the control and at every grid point.

## Files

- `ekam_intraday_trailing_results.json` — full machine-readable results.
- `ekam_intraday_trailing_trades.csv` — all 36,960 trades (control + 9 grid points ×
  2 candidates) with exit prices, exit stamps and exit reasons
  (`trail` / `trail_gap` / `stop` / `gap_stop` / `decay` / `squareoff`).
- Nothing live was touched: no job, ledger, or frozen candidate file changed.
