# Stocks EQUITY — Line G1 — State-gate extensions — REPORT

**Status: COMPLETE — 0 of 9 cells pass the frozen gate. No
candidate spec is frozen.**

Equity cash intraday only, LONG/SHORT. Paper only — real money
₹0, no orders. Every figure: provisional per 100 shares,
₹40/trade deducted. **Home 25 only**, Jan–Oct 2026. Cells were
frozen in `stocks_G1_frozen.md` before scoring; timing audit +
per-cell lag-placebo ran in the same run (`stocks_G1.py`,
`stocks_G1_results.json`).

**Mandatory disclosure:** M2's state gate was itself selected on
this same Jan–Oct data. Any G1 pass would have been a provisional
December-judged hypothesis, never a confirmed system. There are
no passes, so the disclosure attaches to the near-miss below.

## Anchors — all exact, asserted before any cell was believed

- SA-ALL (home 11:00 fade ungated): **+₹4,243.18**, 1,073 trades,
  October +₹341.29 — matches the Line O2 home control to the paisa.
- M2 F4 book: **+₹42,418.91**, 717 trades, October +₹36,166.23 ✓.
- F4 lag-placebo rebuilt (Jan–Sep): **−₹906.88** — matches Line
  M2's record to the paisa.
- Internal splits reconcile: SA-B50 + SA-A50 = SA-ALL;
  SD-EV + SD-NE = F4 book; SB October identical in SB-ALL/SB-B50
  (October 2026 was 100% below-50DMA days — M2's finding,
  independently re-confirmed here: SA-A50 and SC-A50 have zero
  October trades).
- **Audits: clean everywhere.** Built-in H1 counters + the
  independent re-derivation audit (pm, band, direction, entry bar,
  state/event restriction) — 0 violations on every real and
  placebo book (5,724 real trades checked).

## Results (Jan–Oct; halves = Jan–May / Jun–Sep; placebo Jan–Sep)

| Cell | Trades | Net ₹ | Jan–May | Jun–Sep | Oct | Breadth | Green | Placebo | Gate |
|---|---|---|---|---|---|---|---|---|---|
| SA-ALL (anchor) | 1,073 | +4,243.18 | +10,096.92 | −6,195.03 | +341.29 | 8/25 | 5/10 | −7,219.63 | FAIL halves, breadth |
| **SA-B50** | 805 | **+29,552.95** | **+19,074.95** | **+10,136.71** | +341.29 | **9/25** | 7/10 | +25,640.14 | **FAIL breadth only** |
| SA-A50 | 268 | −25,309.77 | −8,978.03 | −16,331.74 | 0 (no trades) | 4/25 | 1/10 | −32,859.77 | FAIL |
| SB-ALL | 1,227 | −35,247.26 | −6,471.28 | +2,523.95 | −31,299.93 | 7/25 | 5/10 | −79,365.60 | FAIL |
| SB-B50 | 877 | −34,674.43 | −2,798.78 | −575.72 | −31,299.93 | 6/25 | 6/10 | −49,549.25 | FAIL |
| SC-ALL | 1,227 | −65,651.20 | −39,784.35 | −44,025.16 | +18,158.31 | 5/25 | 4/10 | +14,665.40 | FAIL (placebo beats it) |
| SC-A50 | 350 | −14,030.92 | +7,583.65 | −21,614.57 | 0 (no trades) | 11/25 | 5/10 | +23,202.03 | FAIL (placebo beats it) |
| SD-EV | 171 | +23,213.97 | +7,325.00 | −2,075.20 | +17,964.17 | 13/25 | 4/10 | −10,175.40 | FAIL Jun–Sep, breadth |
| SD-NE | 546 | +19,204.94 | −4,321.64 | +5,324.52 | +18,202.06 | 14/25 | 4/10 | +9,268.52 | FAIL Jan–May, placebo |

No cell reaches 9–10/10 months green; the best is SA-B50 at 7/10.

### Month tables (₹)

- SA-ALL: Jan +9,778 · Feb −2,075 · Mar +4,682 · Apr −12,241 · May +9,952 · Jun −326 · Jul −5,983 · Aug −11,963 · Sep +12,077 · Oct +341
- SA-B50: Jan +11,953 · Feb −2,891 · Mar +4,682 · Apr −10,455 · May +15,785 · Jun +2,940 · Jul +742 · Aug −5,623 · Sep +12,077 · Oct +341
- SA-A50: Jan −2,174 · Feb +816 · Mar 0 · Apr −1,787 · May −5,833 · Jun −3,267 · Jul −6,725 · Aug −6,340 · Sep 0 · Oct 0
- SB-ALL: Jan +12,641 · Feb −7,387 · Mar −20,537 · Apr +7,715 · May +1,098 · Jun +4,989 · Jul −5,315 · Aug +14,551 · Sep −11,700 · Oct −31,300
- SB-B50: Jan +12,290 · Feb −2,996 · Mar −20,537 · Apr +6,878 · May +1,567 · Jun +2,333 · Jul +53 · Aug +8,738 · Sep −11,700 · Oct −31,300
- SC-ALL: Jan −30,218 · Feb −10,209 · Mar +7,396 · Apr −17,951 · May +11,198 · Jun −24,212 · Jul +548 · Aug −20,215 · Sep −146 · Oct +18,158
- SC-A50: Jan +801 · Feb +262 · Mar 0 · Apr +709 · May +5,812 · Jun −11,969 · Jul +2,716 · Aug −12,361 · Sep 0 · Oct 0
- SD-EV: Jan −96 · Feb +1,965 · Mar −2,135 · Apr −3,756 · May +11,348 · Jun −96 · Jul −1,131 · Aug −3,272 · Sep +2,424 · Oct +17,964
- SD-NE: Jan +9,264 · Feb −6,681 · Mar +4,805 · Apr −7,292 · May −4,417 · Jun −3,306 · Jul 0 · Aug −1,386 · Sep +10,016 · Oct +18,202

## Findings

1. **The one real signal: the below50 state genuinely strengthens
   the 11:00 home fade — and it still fails.** SA-B50 passes five
   of six gate legs (total, both halves, October, placebo, audit)
   and multiplies the ungated fade ~7× (+₹29,552.95 vs +₹4,243.18).
   It fails on breadth, 9/25 — and the reason is decisive:
   **TVSMOTOR alone is +₹34,732.71, more than the cell's entire
   net**; ex-TVSMOTOR the cell is −₹5,179.76. The state gate did
   not broaden the fade; it concentrated it into the same single
   stock that carries INV-LONG and M2's F4. Not a candidate.
2. **The mirror state is toxic, symmetrically.** The fade on
   above50 days loses −₹25,309.77 (SA-A50); fixed-time follow in
   the capped band loses in both states (SC-ALL −₹65,651.20,
   SC-A50 −₹14,030.92, both beaten by their own placebos). The
   state separates — but only M2's exact construction (signal
   entries, follow direction) monetises it.
3. **The fade twin of M2 is dead (S-b).** Fading the same capped
   [0.5%, 1.0%) move at 10:00 loses −₹35,247.26 overall and
   −₹31,299.93 in October alone — in the identical state-month
   where M2's follow made +₹36,166.23. In the M2 state the
   moderate morning move CONTINUES; fading it is the exact wrong
   side. The state gate is not direction-neutral.
4. **F4's edge is not an event phenomenon (S-d).** Restricting
   F4 to event-window days keeps +₹23,213.97 but breaks Jun–Sep
   (−₹2,075.20); restricting to no-event days keeps +₹19,204.94
   but breaks Jan–May (−₹4,321.64) and loses to its own placebo
   on Jan–Sep (+₹1,002.88 vs +₹9,268.52). Neither half of the
   split carries the edge; it is a property of the full gated
   population, and each restriction also cuts breadth below the
   gate (13 and 14 vs 16 for the full book).

## Verdict

**The state gate was an M2-local phenomenon.** Applied to the
fade (any band, either state), to fixed-time follow (either
state), or used to split F4 by event context, it produces no
gate-passing cell. Its one genuine transfer effect — improving
the 11:00 fade under below50 — is a concentration effect in a
single stock (TVSMOTOR), the same dependence already disclosed
on INV-LONG and on F4 itself. Per the frozen plan, no
`stocks_G1_candidate_spec.md` is frozen. The December board is
unchanged: M2's F4 remains the state-gate family's sole frozen
candidate, judged on fresh data.

Files: `stocks_G1_frozen.md` · `stocks_G1.py` ·
`stocks_G1_results.json` · `stocks_G1_run.log` · trade dumps
`stocks_G1_SA_ALL_trades.csv`, `stocks_G1_SA_B50_trades.csv`,
`stocks_G1_SA_A50_trades.csv`, `stocks_G1_SB_ALL_trades.csv`,
`stocks_G1_SB_B50_trades.csv`, `stocks_G1_SC_ALL_trades.csv`,
`stocks_G1_SC_A50_trades.csv`, `stocks_G1_SD_EV_trades.csv`,
`stocks_G1_SD_NE_trades.csv` — all in ~/workspace/trading/.
