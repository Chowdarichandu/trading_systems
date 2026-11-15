# Causal variants F4-C / INV-LONG-C / INV-ABOVE-C — FULL GATE (2026-11-12)

Owner order 2026-11-12 06:16 IST: convert the three EOD-only sleeves so they "fall under the same bridge as the four" — same live causality discipline as N4-V3 / P2F / P2F-R2 / R2-LOWBAND — so Stock Engine can run 7 live strategies. Paper only, real money ₹0. Basis: provisional per 100 shares, ₹40/trade; ₹25,000 fixed-capital lens on combined engines.

## VERDICT — NO VARIANT ARMS. Stock Engine remains 4-live.

| Variant | Leg 1 causality | Leg 2 combined | Leg 3 history | Overall |
|---|---|---|---|---|
| F4-C | **PASS** | FAIL (its picks −₹10,010.06) | PASS | **OUT** |
| INV-LONG-C | **PASS** | FAIL (standalone wide ex-top-3 −₹148,421.43) | PASS | **OUT** |
| INV-ABOVE-C | **PASS** | FAIL (its picks −₹3,099.07) | **FAIL** (collapses vs twin in BOTH years) | **OUT** |

Leg 2 is a hard gate on the combined engine (pre-registered: combined ex-top-3 must IMPROVE on the 4-live baseline's −₹3,256.65). It did not — the combined 7-live engine scored ex-top-3 **−₹18,321.31**. Per the gate rules, no variant is wired into `stock_engine_live.py` or the cron job; nothing was tuned-and-retested. The engine that opened Thu 2026-11-12 is the unchanged 4-live construction.

## The conversion (what was built)

Identical detectors, signals, regime gates, chain rounds, entry/exit geometry as the frozen constructions. The ONLY change is round selection: where the frozen `pool_pick` compares both detector heads' first signals by rank across the whole day (a later higher-rank signal displaces an earlier one — BERGEPAINT 2026-10-16: the 10:15 skor LONG is displaced by a setup3 completing 10:35; the frozen trade is SHORT 10:40), `pool_pick_causal` **locks the round at the moment the first signal for that round completes**; the frozen priority key applies only among signals completed by that moment (same-candle ties); no later signal can displace a locked round; rounds chain from the exit exactly as frozen. Spot-verified on BERGEPAINT 2026-10-16: the causal machinery takes the 10:15 skor LONG (F4-C book row: LONG, entry 10:20 @ ₹473.10, +₹55.00) — the trade the frozen construction never took. Code: `stock_engine_causal3_gate.py` (`pool_pick_causal`, `run_chain_causal`, `build2_causal`).

## Leg 1 — Causality proof: PASS, zero mismatches

Truncation test, 11 sample days (2026-10-01, 10-06, 10-09, 10-13, **10-16**, 10-19, 10-22, 10-27, 10-30, 11-06, **11-11**) × cuts 10:30 / 12:00 / 13:30 / 15:00 = 44 day-slices, full 1,081-name width: **78,163 causal chain trades checked, 6,165 causal F4 first trades checked — 0 identity mismatches** (setup, direction, entry time, entry price identical at every cut). The causal variants' trades are fully determined at their entry times. The conversion is causally sound — what fails below is economics, not causality.

## Leg 2 — Wide width, Oct 1 – Nov 11 2026 (27 trading days, 1,081 names)

Baseline reproduction asserted first: the selection harness (`stock_engine_live_sim.derive_day`, unchanged) on the 4 live comps reproduces the recorded baseline **exactly** — 39 picks · +₹8,724.39 · ex-top-3 −₹3,256.65, key-for-key vs `stock_engine_live_2026-11-11_trades.csv`.

### Per-variant books (all trades, post v2-law, per-100 basis; wide-book totals are price-basis-inflated by high-priced names — same caveat as every wide run — so ex-top-3 is the readable column)

| Book | Trades | Net ₹ | WR | Ex-top-3 ₹ | Frozen twin (trades · net · ex-top-3) |
|---|---|---|---|---|---|
| F4-C | 3,745 | +423,169.17 | 47.5% | **+269,540.42** | 3,236 · +646,384.83 · +528,085.33 |
| INV-LONG-C | 5,618 | +3,291.82 | 28.4% | **−148,421.43** | 4,116 · +361,328.17 · +198,131.42 |
| INV-ABOVE-C | 2,760 | +350,274.29 | 33.5% | **+115,196.29** | 2,289 · +484,876.65 · +249,679.90 |

INV-LONG-C is the standalone red flag the brief asked to surface: the causal chain takes ~1,500 more trades than its frozen twin at width (the early signals the frozen rank-pick would have displaced become real trades), and the marginal trades are losers — headline ≈ ₹0, ex-top-3 deeply negative. F4-C and INV-ABOVE-C retain ~65–72% of their twins' headline nets with positive ex-top-3 as standalone books.

### Combined 7-live Stock Engine (the leg-2 test): FAIL

| | Trades | Net ₹ | WR | Expectancy | Ex-top-3 ₹ | Lens ₹ |
|---|---|---|---|---|---|---|
| **Combined 7-live** | 162 | **−4,267.84** | 34.6% | −26.34 | **−18,321.31** | −4,811.70 |
| October | 120 | −7,795.23 | 35.8% | −64.96 | −21,848.70 | −3,494.25 |
| November | 42 | +3,527.39 | 31.0% | +83.99 | −6,289.60 | −1,317.45 |
| 4-live baseline | 39 | +8,724.39 | 43.6% | +223.70 | −3,256.65 | +634.72 |

Pick attribution (the four live comps' picks are unchanged from the baseline — their 09:10/09:35 batches precede the chain batches): N4-V3 13 · +₹334.64 | P2F 11 · +₹2,486.48 | P2F-R2 10 · +₹5,062.06 | R2-LOWBAND 5 · +₹841.21 | **F4-C 29 · −₹10,010.06** | **INV-LONG-C 68 · +₹116.90** | **INV-ABOVE-C 26 · −₹3,099.07**. The causal three took 123 of 162 slots and netted **−₹12,992.23**. Why: under live streaming, the chain comps' so-far percentiles cross the ≥90 floor constantly, so the 6/day cap fills with ordinary chain trades all day; the sleeves' standalone book strength at width lives in high-priced names the ₹5,000 selection cap excludes, and in the full-day rank information the causal conversion deliberately gives up.

Simulation evidence only (NOT armed) — combined picks on the two most recent days: Nov 9: GLENMARK P2F-R2 +₹3,197.50, TATASTEEL N4-V3 +₹241.20, RADICO INV-ABOVE-C −₹2,318.85, UNOMINDA INV-ABOVE-C +₹1,619.63, AARTIDRUGS INV-ABOVE-C −₹280.65, AARTIPHARM INV-ABOVE-C −₹519.25 (day +₹1,939.58). Nov 11: TATASTEEL P2F −₹133.20, KALYANKJIL N4-V3 +₹959.30, AAVAS INV-ABOVE-C −₹610.25, ACI INV-ABOVE-C −₹253.90, 360ONE INV-ABOVE-C −₹625.57, ADROITIND INV-ABOVE-C +₹175.71 (day −₹487.91).

## Leg 3 — Full history, 25-watchlist (Jan–Oct 2025 + Jan–Oct 2026, per-100)

Pre-registered collapse rule: a variant fails a year if twin net > 0 AND (causal net < 0 OR causal net < 25% of twin net); leg fails if it collapses in BOTH years. Placebo = same signals, entry shifted one candle, own TP/SP. Independent re-sum of every written CSV asserted equal. Frozen INV builds cross-checked against `build_inv` / `build_inv_above` (exact).

| Year | Book | Trades | Net ₹ | WR | Ex-top-3 ₹ | Placebo ₹ | Halves H1/H2 ₹ |
|---|---|---|---|---|---|---|---|
| 2025 | F4 | 246 | +91.14 | 47.6% | −9,790.86 | −859.02 | −5,008 / +5,099 |
| 2025 | F4-C | 275 | **−18,652.98** | 44.7% | −23,751.34 | −14,513.40 | −19,532 / +879 |
| 2026 | F4 | 347 | +98,735.31 | 55.6% | +25,315.62 | +82,339.98 | +47,586 / +51,150 |
| 2026 | F4-C | 404 | +55,755.51 | 49.5% | +362.81 | +41,731.74 | +17,444 / +38,311 |
| 2025 | INV-LONG | 220 | +12,605.23 | 36.4% | −2,495.54 | +17,100.13 | +12,371 / +234 |
| 2025 | INV-LONG-C | 257 | **−1,415.04** | 33.1% | −12,022.81 | +4,242.09 | −1,303 / −112 |
| 2026 | INV-LONG | 133 | +44,062.10 | 48.9% | +9,830.00 | +44,335.50 | +28,818 / +15,244 |
| 2026 | INV-LONG-C | 165 | +41,981.25 | 43.6% | +3,179.46 | +37,746.41 | +23,234 / +18,747 |
| 2025 | INV-ABOVE | 140 | +5,639.90 | 34.3% | −5,805.42 | +7,911.62 | — |
| 2025 | INV-ABOVE-C | 201 | **−8,287.73** | 27.9% | −18,510.12 | −5,061.82 | — |
| 2026 | INV-ABOVE | 36 | +3,349.21 | 38.9% | −746.48 | +6,573.90 | — |
| 2026 | INV-ABOVE-C | 47 | **−149.17** | 36.2% | −2,638.93 | +3,652.65 | — |

Month tables, full halves and breadth per set: `stock_engine_causal3_hist_summary.json` + per-set CSVs `stock_engine_causal3_hist_<comp>_<year>.csv`.

Readings: F4-C keeps 56% of its twin's strong 2026 (but its ex-top-3 collapses to +₹362.81 — the retained edge is top-3-concentrated) and is outright negative in 2025, a year its twin was flat (+₹91.14) — collapse in one year only → leg-3 PASS by the pre-registered rule, with the 2025 warning on record. INV-LONG-C nearly matches its twin in 2026 on the 25 (+₹41,981.25 vs +₹44,062.10) — its wide-width failure is a tail-universe phenomenon, not a watchlist one — but it still turns its twin's positive 2025 negative → one-year collapse → leg-3 PASS by rule. INV-ABOVE-C turns its twin negative in BOTH years → leg-3 FAIL outright.

## Bottom line

The causal conversion itself is proven sound (leg 1, zero mismatches in 84,328 checked trades) — the three sleeves CAN be made to fall under the same causality bridge as the four. What the gate kills is their current economics inside the live engine: under streaming selection they flood the daily cap with ordinary trades and net −₹12,992.23 across the window, dragging the combined engine's ex-top-3 from −₹3,256.65 to −₹18,321.31. A future attempt would need a mechanically different selection treatment for streaming chain candidates (e.g. decision points only at fixed times with populations frozen then) — that is a NEW candidate requiring its own gate, not a retest of this one.

**Arming: NONE — not today (2026-11-12), not Fri 2026-11-13.** `stock_engine_live.py` and cron `stocks-wide-nse-shadow` are untouched; Stock Engine trades the 4-live construction. The causal variants exist as scored, named components (F4-C / INV-LONG-C / INV-ABOVE-C) in the files below; December judging must not confuse them with the frozen sleeves, which remain EOD-book components of SarvaRitu.

Files: `stock_engine_causal3_gate.py` (conversion + legs 1–2) · `stock_engine_causal3_hist.py` (leg 3) · `stock_engine_causal3_gate_summary.json` · `stock_engine_causal3_hist_summary.json` · `stock_engine_causal3_2026-11-12_trades.csv` (combined sim picks) · `stock_engine_causal3_variant_rows.csv` (causal book rows, wide) · `stock_engine_causal3_hist_<comp>_<year>.csv` (leg-3 sets).
