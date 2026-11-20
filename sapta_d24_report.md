# SAPTA Design 24 — Report · 2026-11-18

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40 on every entry AND every exit (₹80 per completed trade, SPEC §2) · no stock options.
**Spec:** `sapta_d24_SPEC.md` (pre-registered 2026-11-18). Design 23 closed the entry-timing surface (0/5 streams pass; CLR-FADE the near-miss); Design 22 had already closed the allocation surface. Design 24 changes the SELECTION surface — the one surface never yet changed: **RS63**, a monthly rank-and-hold cross-sectional relative-strength book inside the rotating universe (trailing 63-trading-day return, hold the rank 1–7 entry band, exits only by rank decay past the 1–14 hold band, universe exit or window end — no intraday timing signal at all). The standing 4-leg book gate, the owner's EKAM bar as fifth line, and a clearly-labelled diagnostic of the identical rule on EKAM's frozen 25 (SPEC §5, not gated).

## D24 universe

Rotating construction (Designs 12–23, unchanged): 69 distinct names across the 8 quarters; the pool on a rebalance date is the names active that date. Daily closes from the `universe_daily` parquet dump; 23 monthly rebalances, 2025-01-01 → 2026-11-02. Names without a parquet series: none.

## Controls (mandatory, before scoring)

- C-1 clone parity, CAND-T5 on the frozen 25: reproduced = True (2025 {'trades': 1035, 'total': 62164.57, 'wr': 35.56, 'expectancy': 60.06}, 2026 {'trades': 1025, 'total': 63883.6, 'wr': 35.71, 'expectancy': 62.33}).
- C-1 clone parity, S2 on the frozen 25: reproduced = True (2025 {'trades': 621, 'total': 45300.64, 'wr': 34.94, 'expectancy': 72.95}, 2026 {'trades': 615, 'total': 72605.3, 'wr': 36.75, 'expectancy': 118.06}).
- C-2 exit prices vs EKAM `exit_x2p`: 53820 cells, 0 mismatches.
- C-3 vote truncated recompute: frozen-25 314 checked, 0 mismatches; SAPTA union 204 checked, 0 mismatches.
- C-4 daily clone parity: BB+RSI lists match = True; stats match = True; MACD-only lists match = True.
- **C-1..C-4 ALL PASS: True**
- C-24a Design 16 anchor: got 424 trades / ₹+136,826.29 / ₹+24,893.52 vs published 424 / ₹+136,826.29 / ₹+24,893.52; taken set identical to sapta_d16_trades.csv = True; re-TRAIL parity {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0} → reproduced = True.
- C-24b Design 21 RXUNION anchor: got 423 trades / ₹+86,256.44 / ₹+28,448.67 vs published 423 / ₹+86,256.44 / ₹+28,448.67; taken set identical to sapta_d21_trades.csv = True; re-TRAIL parity {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0} → reproduced = True.
- **ALL CONTROLS PASS: True**

## BOOK RS63 — relative strength, rotating universe

Rebalances 23 · entries 42 · exits: rank-decay 17, universe-exit 18, unrankable 0, window-end 7 · entry skips (no close) 0 · exit close fallbacks 0 · holdings after each rebalance [7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7].
- 2025: trades 26 · gross -55,160.00 · net -57,240.00 · WR 57.7% · avg hold 80.3 trading days
- 2026: trades 16 · gross +110,751.00 · net +109,471.00 · WR 50.0% · avg hold 72.0 trading days
- November 2026 slice: 0 trades · net ₹+0.00 · October 2025: 4 trades · net ₹+10,788.00 · October 2026: 3 trades · net ₹+16,397.00
- Placebo (SPEC §4, 200 draws, matched schedule; skipped placements 0): draw means ₹+5,036 (2025) / ₹+69,269 (2026); real net percentile 27.5 / 76.5; p90 ₹+122,675 / ₹+149,251.
- Month table (entry month): 2025-01 -123,070 · 2025-03 +66,820 · 2025-04 +11,319 · 2025-06 +8,100 · 2025-07 -35,228 · 2025-08 +1,370 · 2025-09 +2,661 · 2025-10 +10,788 · 2026-01 -36,980 · 2026-03 -9,400 · 2026-04 +34,009 · 2026-05 +44,640 · 2026-07 +60,805 · 2026-10 +16,397
- Top contributors: LAURUSLABS +122,550 (25 +29,560 / 26 +92,990) · GODFRYPHLP +66,820 (25 +66,820 / 26 +0) · AUROPHARMA +44,640 (25 +0 / 26 +44,640) · BHARATFORG +43,960 (25 +0 / 26 +43,960) · FORTIS +19,125 (25 +19,125 / 26 +0) · NATIONALUM +11,960 (25 +11,960 / 26 +0) · ICICIBANK +11,275 (25 +11,275 / 26 +0) · BSE +8,100 (25 +8,100 / 26 +0)
- **Gate: net25 -57,240 net26 +109,471 nov +0 | pct 27.5/76.5 | extop -159,785/-72,119 | trades 42 WR 54.8% DD -121,535 | legs 0/4 FAIL**
- **EKAM bar (fifth line):** vs Cand-1 -119,405 (2025) / +45,587 (2026); vs Cand-2 -102,541 / +36,866 → **FALLS SHORT**.

## Diagnostic — RS63-F25, identical rule on EKAM's frozen 25 (SPEC §5 — NOT a book, NOT gated)

- 2025: trades 24 · gross -27,829.00 · net -29,749.00 · WR 45.8% · avg hold 101.1 trading days
- 2026: trades 17 · gross -42,835.00 · net -44,195.00 · WR 23.5% · avg hold 47.9 trading days
- November 2026 slice: 2 trades · net ₹-635.00 · October 2025: 1 trades · net ₹+4,230.00 · October 2026: 2 trades · net ₹-430.00
- Placebo percentiles (diagnostic only): 29.0 (2025) / 13.5 (2026) · max DD ₹-141,084 · WR 36.6%
- Month table (entry month): 2025-01 -95,648 · 2025-02 -12,190 · 2025-03 +1,444 · 2025-04 +380 · 2025-06 +35,260 · 2025-07 +39,630 · 2025-08 +7,955 · 2025-09 +10,820 · 2025-10 +4,230 · 2025-11 -21,915 · 2025-12 +285 · 2026-04 -5,440 · 2026-05 -31,070 · 2026-06 +14,740 · 2026-07 -19,430 · 2026-08 -18,275 · 2026-09 +16,345 · 2026-10 -430 · 2026-11 -635
- Top contributors: TVSMOTOR +68,540 (25 +58,020 / 26 +10,520) · HINDALCO +28,775 (25 +28,775 / 26 +0) · HINDCOPPER +25,665 (25 +25,300 / 26 +365) · BDL +20,940 (25 +32,420 / 26 -11,480) · GLENMARK +14,760 (25 +14,330 / 26 +430) · NATIONALUM +13,572 (25 +13,572 / 26 +0) · HDFCBANK +7,305 (25 +7,305 / 26 +0) · HINDZINC +4,130 (25 +4,230 / 26 -100)

## Head-to-head — gated SAPTA books vs Design 24

| Book | Net 2025 / 2026 | Ex-top-3 2025 / 2026 | Placebo pct | DD | WR | Trades | Legs |
|---|---:|---:|---:|---:|---:|---:|---|
| D13 GAPFADE-TRAIL (gated) | +0 / +0 | +0 / +0 | 0.0 / 0.0 | +0 | 0.0% | 0 | 0/4 FAIL |
| D16 GAPFADE-UNION (gated) | +0 / +0 | +0 / +0 | 0.0 / 0.0 | +0 | 0.0% | 0 | 0/4 FAIL |
| D17 GAPFADE-FOCUS (gated) | +0 / +0 | +0 / +0 | 0.0 / 0.0 | +0 | 0.0% | 0 | 0/4 FAIL |
| D19 FILL3 (gated) | +0 / +0 | +0 / +0 | 0.0 / 0.0 | +0 | 0.0% | 0 | 0/4 FAIL |
| D21 RXUNION (gated) | +86,256 / +28,449 | +55,721 / +6,834 | 100.0 / 99.0 | -13,455 | 44.9% | 423 | 4/4 PASS |
| **D24 RS63** | -57,240 / +109,471 | -159,785 / -72,119 | 27.5 / 76.5 | -121,535 | 54.8% | 42 | 0/4 FAIL |
| D24 RS63-F25 (diagnostic, not gated) | -29,749 / -44,195 | — | 29.0 / 13.5 | -141,084 | 36.6% | 41 | — |

## Verdict

- **BOOK RS63: gate FAIL (0/4)** — net ₹-57,240.00 / ₹+109,471.00, placebo pct 27.5 / 76.5, ex-top-3 ₹-159,785 / ₹-72,119, worst month 2025-04 ₹-54,715, DD ₹-121,535, WR 54.8%, 42 trades, November ₹+0. **EKAM bar: FALLS SHORT** (2025 vs Cand-1 -119,405 / vs Cand-2 -102,541; 2026 vs Cand-1 +45,587 / vs Cand-2 +36,866).
- **Diagnostic RS63-F25 (not gated):** net ₹-29,749.00 / ₹-44,195.00, placebo pct 29.0 / 13.5, 41 trades — the identical selection rule on EKAM's curated pool does NOT earn by the same informal standard (positive nets + placebo ≥ 90 both years).
- The diagnosis is selection-bound: monthly cross-sectional momentum earns on neither universe — with timing (D23), allocation (D22) and now selection measured out, the rotating universe has yielded exactly one edge family in 24 designs: the first-bar gap fade. The frozen 25's edge, by contrast, lives in EKAM's intraday votes and its daily swing — mechanisms, not selection.
**Design-25 seed (per SPEC §9, selection-bound failure):** the selection surface is CLOSED — the identical rule fails on both universes, so the constraint is the rule, not the pool. Design 25 leaves selection too and goes to the one surface this programme has never traded: the DAILY timeframe on the rotating universe with EKAM-Daily's own mechanism class (mean-reversion at daily scale, the closed Daily line's machinery pointed at the rotating pool instead of the frozen 25) — pre-registered fresh as a survey in the Design 18 method before any book.


## Audit (independent path — sapta_d24_audit.py)

Counters: {'csv_rows': 83, 'audit_trades': 83, 'key_missing_in_audit': 0, 'key_extra_in_audit': 0, 'entry_price_mismatch': 0, 'exit_price_mismatch': 0, 'exit_date_mismatch': 0, 'exit_reason_mismatch': 0, 'gross_mismatch': 0, 'net_mismatch': 0, 'resum_mismatch_books': 0}. **AUDIT CLEAN — 0 issues.** Every RS63 and RS63-F25 trade re-derived from the parquet dump via a pyarrow reader (the scorer used pandas), the active map rebuilt from the stored selections, ranks and rebalances re-simulated from scratch; the written trades CSV re-summed per book per year against the results file. parquet-vs-5m close cross-check (data note, SPEC s.7): 972 sampled name-days, 786 mismatches at Rs 0.05 tolerance.

## Designer's note (post-audit, read before quoting the verdict)

**The 2026 headline is real but it is not selection skill.** RS63's +₹1,09,471 in 2026 clears both EKAM candidates that year — and it is carried by LAURUSLABS alone (+₹92,990 of it); ex-top-3, 2026 is −₹72,119. The matched-schedule placebo's draw MEAN in 2026 is +₹69,269: on this rotating pool, holding almost anything for ~72 trading days paid in 2026, and the ranked book sits at only the 76.5th percentile of random selection. In 2025 the same placebo mean is +₹5,036 while the ranked book lost −₹57,240 (27.5th percentile) — the rank actively hurt: the book's first rebalance (Jan 2025, entry month −₹1,23,070) bought late-2024's trailing winners straight into the Jan–Mar 2025 correction, the classic momentum-crash entry, and rank-decay exits (17 of 42 trades) realised the falls slowly at monthly checks. WR 54.8% with DD −₹1,21,535 is a coin-flip book with fat left tail, not an edge.

**The diagnostic settles the attribution.** The identical rule on EKAM's frozen 25 loses in BOTH years (−₹29,749/−₹44,195, placebo 29.0/13.5) — worse than on the rotating pool. Selection is therefore not a surface where the curated 25 rescues the rule (the reverse of the intraday transplant finding): monthly cross-sectional momentum, as frozen, is the constraint. Per SPEC §9 the selection surface is CLOSED and the Design-25 seed in the verdict stands: a Design-18-method survey of EKAM-Daily's mechanism class (daily-scale mean reversion) on the rotating universe — the one timeframe/mechanism pairing this programme has never run on this pool.

**Data note, interpreted.** The audit's cross-check found 786 of 972 sampled parquet daily closes differ from the 5-min stores' last-bar closes beyond ₹0.05. The parquet dump carries corporate-action-adjusted closes; the 5-min stores are unadjusted. For a multi-week holding book the adjusted series is the correct basis (unadjusted closes would fabricate split-day losses), and ranks/returns inside one consistent series are unaffected by the basis difference; the intraday books never hold across an adjustment, which is why this never surfaced in Designs 1–23. The audit re-derived every trade on the same parquet basis and is CLEAN; the book's verdict is internally sound, but its rupee figures are not price-comparable tick-for-tick with the intraday books' unadjusted basis.
