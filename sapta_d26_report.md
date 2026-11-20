# SAPTA Design 26 — Report · 2026-11-18

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40 per completed trade (EKAM convention) · no stock options.
**Spec:** `sapta_d26_SPEC.md` (pre-registered 2026-11-18). Design 25's survey passed all three daily-scale mean-reversion streams on the frozen survey bar (which carried no placebo leg) while the placebo diagnostic failed everywhere (percentiles 0.0–21.5 — the Design 14 regime-occupancy signature). This design builds each stream into a book in its frozen D25 form — same rotating universe, same entry-day gate, no caps added — and judges it under the full five-line gate: the standing four legs (net · placebo >90th · ex-top-3 · month floor) plus the owner's EKAM bar as the fifth line. The placebo recipe is D25 §2 verbatim, unsoftened, now binding.

## D26 universe

Rotating construction (Designs 12–25, unchanged): 69 distinct names across the 8 quarters; books enter only when the ENTRY day is in the name's active set.

## Controls (mandatory, before scoring)

- C-1 clone parity, CAND-T5 on the frozen 25: reproduced = True (2025 {'trades': 1035, 'total': 62164.57, 'wr': 35.56, 'expectancy': 60.06}, 2026 {'trades': 1025, 'total': 63883.6, 'wr': 35.71, 'expectancy': 62.33}).
- C-1 clone parity, S2 on the frozen 25: reproduced = True (2025 {'trades': 621, 'total': 45300.64, 'wr': 34.94, 'expectancy': 72.95}, 2026 {'trades': 615, 'total': 72605.3, 'wr': 36.75, 'expectancy': 118.06}).
- C-2 exit prices vs EKAM `exit_x2p`: 53820 cells, 0 mismatches.
- C-3 vote truncated recompute: frozen-25 314 checked, 0 mismatches; SAPTA union 204 checked, 0 mismatches.
- C-4 daily clone parity: BB+RSI lists match = True; stats match = True; MACD-only lists match = True.
- **C-1..C-4 ALL PASS: True**
- C-26a EKAM HOME ANCHOR: sim2c full-stats dicts equal published EKAM-2c = True (2025: 74 trades · +₹42,954.60 · WR 71.62; 2026: 102 · +₹1,41,328.40 · 62.75); BB-REV-D standalone anchor match = True (91/+₹28,946.00 · 119/+₹1,00,067.00); RSI-REV standalone anchor match = True (33/+₹63,575.50 · 43/+₹1,08,108.90) → reproduced = True.
- C-26b gated-clone parity (active=None, all 25): sim2c_gated == sim2c = True; sim1c_gated == EKAM.sim BB = True, RSI = True → reproduced = True.
- C-26c Design 16 anchor: got 424 trades / ₹+136,826.29 / ₹+24,893.52 vs published 424 / ₹+136,826.29 / ₹+24,893.52; set identical = True; re-TRAIL parity {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0} → reproduced = True.
Daily preps ready for 69/69 rotating names (universe_daily parquet, 2019-01-01 → 2026-11-13).

- C-26d Design 25 reproduction anchor: per-stream trade sets identical to `sapta_d25_trades.csv` and year fields (trades/gross/net/ex-top-3) + full-window totals equal to `sapta_d25_results.json` — EKAM-2c True, BB-REV-D True, RSI-REV True → reproduced = True.
- Placebo consistency vs D25 diagnostic (EKAM-2c): percentiles/draw means identical = True (run 1.0/4.5 vs D25 1.0/4.5).
- Placebo consistency vs D25 diagnostic (BB-REV-D): percentiles/draw means identical = True (run 16.0/1.0 vs D25 16.0/1.0).
- Placebo consistency vs D25 diagnostic (RSI-REV): percentiles/draw means identical = True (run 0.0/21.5 vs D25 0.0/21.5).

## Book gate table

| Book | Net 25/26 | Placebo pct 25/26 | Ex-top-3 25/26 | Worst month (exit/entry) | EKAM bar | Legs |
|---|---:|---:|---:|---:|---|---:|
| EKAM-2c | +36,682 / +27,583 | 1.0 / 4.5 | -4,963 / -17 | -88,182 / -62,320 | ✗ | 1/4  |
| BB-REV-D | +52,780 / +29,562 | 16.0 / 1.0 | +2,425 / +6,762 | -30,396 / -32,750 | ✗ | 2/4  |
| RSI-REV | +57,683 / +48,524 | 0.0 / 21.5 | +6,998 / +16,354 | -34,024 / -42,401 | ✗ | 2/4  |

EKAM bar (leg 5): net ≥ Cand-1 AND Cand-2 in both years — 2025 ≥ +₹62,165 and ≥ +₹45,301; 2026 ≥ +₹63,884 and ≥ +₹72,605. EKAM-Daily home line (reported alongside): +₹42,954.60 / +₹1,41,328.40.

## EKAM-2c — FAIL

- 2025: trades 58 · gross +39,002.10 · gross/trade +672.45 · net +36,682.10 · WR 77.6% · avg hold 23.8d · ex-top-3 -4,962.90 · exits: cap 8 @ +8,397 · signal 42 @ +2,062 · time 8 @ -14,349
- 2026: trades 53 · gross +29,703.00 · gross/trade +560.43 · net +27,583.00 · WR 60.4% · avg hold 20.6d · ex-top-3 -17.00 · exits: cap 6 @ +4,675 · signal 38 @ +1,379 · time 6 @ -6,695 · window_end 3 @ -3,533
- Max DD (full book, exit-date order): ₹-93,560.50.
- Leg 1 net positive both years: True (+36,682.10 / +27,583.00).
- Leg 2 placebo >90th both years: False (pct 1.0 / 4.5; draw means ₹+118,011 / ₹+60,198 vs real nets above).
- Leg 3 ex-top-3 positive both years: False (-4,962.90 / -17.00).
- Leg 4 month floor (worst month ≥ −₹15,000 on both bases): False (exit basis worst 2025-04 ₹-88,181.50; entry basis worst 2025-01 ₹-62,320.00).
- Leg 5 EKAM bar (meet/beat Cand-1 AND Cand-2, both years): False (2025 distance: Cand-1 -25,482.47 · Cand-2 -8,618.54 · EKAM-Daily home -6,272.50; 2026 distance: Cand-1 -36,300.60 · Cand-2 -45,022.30 · EKAM-Daily home -113,745.40).
- November 2026 slice: 0 entries · closed 0 net ₹+0.00 · open/marked 0 net ₹+0.00 · entered earlier, still open 3 marked ₹-10,720.00.
- Top contributors (scored years): LODHA +23,950 (25 +17,060 / 26 +6,890) · HAVELLS +21,915 (25 +21,915 / 26 +0) · GLENMARK +21,120 (25 +21,120 / 26 +0) · LAURUSLABS +17,890 (25 +7,630 / 26 +10,260) · PHOENIXLTD +14,815 (25 +5,135 / 26 +9,680) · SUNPHARMA +14,085 (25 +14,725 / 26 -640) · FORTIS +13,900 (25 +6,240 / 26 +7,660) · JSWSTEEL +13,382 (25 +9,412 / 26 +3,970)

## BB-REV-D — FAIL

- 2025: trades 63 · gross +55,300.00 · gross/trade +877.78 · net +52,780.00 · WR 73.0% · avg hold 13.1d · ex-top-3 +2,425.00 · exits: signal 63 @ +878
- 2026: trades 57 · gross +31,842.00 · gross/trade +558.63 · net +29,562.00 · WR 56.1% · avg hold 14.0d · ex-top-3 +6,762.00 · exits: signal 57 @ +559
- Max DD (full book, exit-date order): ₹-46,015.00.
- Leg 1 net positive both years: True (+52,780.00 / +29,562.00).
- Leg 2 placebo >90th both years: False (pct 16.0 / 1.0; draw means ₹+81,368 / ₹+69,155 vs real nets above).
- Leg 3 ex-top-3 positive both years: True (+2,425.00 / +6,762.00).
- Leg 4 month floor (worst month ≥ −₹15,000 on both bases): False (exit basis worst 2025-02 ₹-30,396.00; entry basis worst 2025-02 ₹-32,750.00).
- Leg 5 EKAM bar (meet/beat Cand-1 AND Cand-2, both years): False (2025 distance: Cand-1 -9,384.57 · Cand-2 +7,479.36 · EKAM-Daily home +9,825.40; 2026 distance: Cand-1 -34,321.60 · Cand-2 -43,043.30 · EKAM-Daily home -111,766.40).
- November 2026 slice: 0 entries · closed 0 net ₹+0.00 · open/marked 0 net ₹+0.00 · entered earlier, still open 0 marked ₹+0.00.
- Top contributors (scored years): COFORGE +25,670 (25 +25,670 / 26 +0) · HAVELLS +21,915 (25 +21,915 / 26 +0) · LODHA +20,934 (25 +14,044 / 26 +6,890) · HCLTECH +18,695 (25 +18,695 / 26 +0) · PHOENIXLTD +14,815 (25 +5,135 / 26 +9,680) · JSWSTEEL +12,685 (25 +8,715 / 26 +3,970) · LAURUSLABS +10,655 (25 +7,630 / 26 +3,025) · AUROPHARMA +10,620 (25 +0 / 26 +10,620)

## RSI-REV — FAIL

- 2025: trades 28 · gross +58,803.00 · gross/trade +2,100.11 · net +57,683.00 · WR 75.0% · avg hold 39.9d · ex-top-3 +6,998.00 · exits: cap 17 @ +7,980 · signal 4 @ +6,050 · time 7 @ -14,436
- 2026: trades 13 · gross +49,044.50 · gross/trade +3,772.65 · net +48,524.50 · WR 76.9% · avg hold 30.6d · ex-top-3 +16,354.50 · exits: cap 8 @ +6,826 · time 3 @ -4,125 · window_end 2 @ +3,405
- Max DD (full book, exit-date order): ₹-68,434.00.
- Leg 1 net positive both years: True (+57,683.00 / +48,524.50).
- Leg 2 placebo >90th both years: False (pct 0.0 / 21.5; draw means ₹+130,916 / ₹+57,810 vs real nets above).
- Leg 3 ex-top-3 positive both years: True (+6,998.00 / +16,354.50).
- Leg 4 month floor (worst month ≥ −₹15,000 on both bases): False (exit basis worst 2025-05 ₹-34,024.00; entry basis worst 2025-01 ₹-42,401.00).
- Leg 5 EKAM bar (meet/beat Cand-1 AND Cand-2, both years): False (2025 distance: Cand-1 -4,481.57 · Cand-2 +12,382.36 · EKAM-Daily home +14,728.40; 2026 distance: Cand-1 -15,359.10 · Cand-2 -24,080.80 · EKAM-Daily home -92,803.90).
- November 2026 slice: 0 entries · closed 0 net ₹+0.00 · open/marked 0 net ₹+0.00 · entered earlier, still open 2 marked ₹+6,730.00.
- Top contributors (scored years): LODHA +21,524 (25 +11,764 / 26 +9,760) · GLENMARK +18,485 (25 +18,485 / 26 +0) · SUNPHARMA +16,670 (25 +16,670 / 26 +0) · APLAPOLLO +15,530 (25 +15,530 / 26 +0) · HAVELLS +15,360 (25 +15,360 / 26 +0) · FORTIS +14,444 (25 +6,240 / 26 +8,204) · ADANIGREEN +12,400 (25 +0 / 26 +12,400) · NESTLEIND +11,198 (25 +11,198 / 26 +0)

## Verdict

**No book passes the full gate.** Failing lines per book: EKAM-2c: leg 2 placebo, leg 3 ex-top-3, leg 4 month floor, leg 5 EKAM bar; BB-REV-D: leg 2 placebo, leg 4 month floor, leg 5 EKAM bar; RSI-REV: leg 2 placebo, leg 4 month floor, leg 5 EKAM bar. The books are closed in this form; the gated intraday books (D13/D16/D17/D19-FILL3/D21/D22) stand as the programme's SAPTA books.

**Design-27 seed (per SPEC s.7, all fail; the placebo leg binds on every book):** stated plainly — for SAPTA **Daily-class** books on the rotating universe, the surfaces now measured are: the verbatim EKAM-Daily mechanism and both its components (this design, full gate), the +MACD daily machine and its exit subtractions (Designs 2–14, closed as regime occupancy), entry-side gates and caps at every level (Designs 4–6), and the selection/timing/allocation surfaces (Designs 22–24). The placebo failure is a property of the universe plus this exit stack — random signal-adjacent occupancy of these names earns what the real sequence earns — so **no untried surface remains inside the SAPTA Daily-class construction as the owner specified it** (rotating sector universe, single names, daily scale). What remains untried lies OUTSIDE that construction and is named, not pre-built: (i) the frozen-25 curation itself as the universe — EKAM's home ground, where this mechanism already runs as EKAM-Daily; (ii) index-level (sector-proxy) instruments instead of single names; (iii) horizons beyond TIME60 on the daily mechanism. Design 27 is written from this inventory only if the owner opens one of those surfaces; no closed surface is re-run under a new label.


## Independent audit

Separate code path (pyarrow parquet read, own Bollinger/Wilder-RSI, own signal construction, own single-component and 2c state machines, active map rebuilt from the selections file + RELIANCE calendar): **CLEAN** — 293 reported trades re-derived across 69 names; C-26a independently re-verified on EKAM's home data = True (audit 2025 74 trades / ₹+42,954.60, 2026 102 / ₹+141,328.40 vs published +₹42,954.60 / +₹1,41,328.40); per-book sets, nets, year sums and November slices re-derived; gate legs 1, 3, 4, 5 re-derived from the audit's own trade sets and leg 2 (placebo) rebuilt with the audit's own machines and draw loop under the frozen D25 recipe — percentiles match the run's on all three books; causality and entry-gate compliance asserted on every trade.
