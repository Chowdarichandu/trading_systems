# Bank Nifty Scalping — OCTOBER-ONLY Scoring of the Frozen Charter

**A measurement, not a re-opening.** Scored 2026-11-01 at Chandu's request ("Do for
October") after the scalping RSI engine terminated SATURATED on the full window.
Nothing here re-tunes, re-opens or changes the engine's verdict. Bank Nifty ONLY.
Paper only, real money ₹0. Premiums per 1 lot (30), cost ₹220/trade.

- **Window:** October 2026 within the genuine 1-min dataset — **17 trading days,
  2026-10-01 → 2026-10-27** (the fetched window ends Oct 27).
- **Definitions:** Charter v2 verbatim (`bank_scalp_engine_protocol.md`), scored with
  the engine's own machinery (`bank_scalp_engine_charter.py` / `_core.py`); prior-day
  levels resolve against the full calendar exactly as in the full-window runs.
- **Controls, same run:** timing audit **0 violations on all 25 variants**; October
  lag placebo (+1 bar) and October count-matched random placebo (20 draws, seed 42)
  per variant; ex-top-3 stress; independent re-sum from the written CSVs **matched**.
  **NOT_COMPUTED in October: 0** for every variant.
- **Cross-verification:** the October trade lists below are row-for-row identical to
  the October subsets of the original full-window trade CSVs (checked for
  TRAILT3/TRAILT4/TRAILW/TRAIL, OR1-T20, OR3-T15, LR1-T20, LR3-T12, PV1 — all matched).
- Scorer: `bank_scalp_october_run.py`; machine summary: `bank_scalp_october_summary.json`;
  trades: `bank_scalp_oct_OR_ladder.csv`, `bank_scalp_oct_trail.csv`, `bank_scalp_oct_PV1.csv`.

## 1. Fixed-target ladder — October (stop −9, cap 8/day, flat-only re-entry)

| Variant | Trades | Gross ₹ | Gross pts/tr | Net ₹ | Win % | Days | Days green % | Median day ₹ | Worst day ₹ | Best day ₹ | Ex-top3 ₹ | Lag placebo ₹ | Random placebo mean ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OR1-T2.5 | 74 | −7,215.00 | −3.250 | −23,495.00 | 0.0 | 17 | 0.0 | −1,560.00 | −2,940.00 | −145.00 | −23,060.00 | −22,805.00 | −21,149.00 |
| OR1-T10 | 74 | −2,880.00 | −1.297 | −19,160.00 | 40.5 | 17 | 11.8 | −1,070.00 | −2,940.00 | 80.00 | −19,400.00 | −17,450.00 | −18,472.03 |
| OR1-T12 | 74 | −1,710.00 | −0.770 | −17,990.00 | 39.2 | 17 | 11.8 | −770.00 | −2,940.00 | 140.00 | −18,410.00 | −16,100.00 | −18,067.55 |
| OR1-T15 | 74 | −2,700.00 | −1.216 | −18,980.00 | 32.4 | 17 | 17.6 | −1,010.00 | −3,920.00 | 230.00 | −19,670.00 | −16,820.00 | −17,451.50 |
| OR1-T20 | 73 | −570.00 | −0.260 | −16,630.00 | 30.1 | 17 | 17.6 | −710.00 | −3,920.00 | 650.00 | −17,770.00 | −18,194.50 | −17,018.80 |
| OR3-T2.5 | 44 | −4,635.00 | −3.511 | −14,315.00 | 0.0 | 16 | 0.0 | −635.00 | −3,230.00 | −145.00 | −13,880.00 | −13,280.00 | −12,331.25 |
| OR3-T10 | 44 | −1,050.00 | −0.795 | −10,730.00 | 43.2 | 16 | 31.3 | −410.00 | −3,350.00 | 240.00 | −10,970.00 | −10,730.00 | −10,370.08 |
| OR3-T12 | 44 | −393.00 | −0.298 | −10,073.00 | 40.9 | 16 | 37.5 | −350.00 | −3,773.00 | 420.00 | −10,493.00 | −9,590.00 | −10,205.83 |
| OR3-T15 | 44 | +249.00 | +0.189 | −9,431.00 | 36.4 | 16 | 31.3 | −375.00 | −3,773.00 | 690.00 | −10,121.00 | −9,917.00 | −9,717.58 |
| OR3-T20 | 44 | +1,954.50 | +1.481 | −7,725.50 | 34.1 | 16 | 37.5 | −300.00 | −3,773.00 | 1,030.00 | −8,865.50 | −9,257.00 | −9,535.02 |
| LR1-T2.5 | 95 | −7,020.00 | −2.463 | −27,920.00 | 0.0 | 17 | 0.0 | −1,850.00 | −2,885.00 | −490.00 | −27,485.00 | −31,025.00 | −27,074.75 |
| LR1-T10 | 95 | −3,420.00 | −1.200 | −24,320.00 | 41.0 | 17 | 0.0 | −1,640.00 | −2,290.00 | −490.00 | −24,560.00 | −24,890.00 | −22,978.32 |
| LR1-T12 | 95 | −2,794.50 | −0.981 | −23,694.50 | 37.9 | 17 | 0.0 | −1,400.00 | −2,660.00 | −490.00 | −24,114.50 | −23,994.50 | −22,454.08 |
| LR1-T15 | 95 | −2,230.50 | −0.783 | −23,130.50 | 33.7 | 17 | 0.0 | −1,334.00 | −3,200.00 | −320.00 | −23,820.50 | −24,428.00 | −21,701.60 |
| LR1-T20 | 95 | −384.00 | −0.135 | −21,284.00 | 30.5 | 17 | 5.9 | −1,310.00 | −3,050.00 | 430.00 | −22,424.00 | −23,097.50 | −21,246.80 |
| LR3-T2.5 | 91 | −5,940.00 | −2.176 | −25,960.00 | 0.0 | 17 | 0.0 | −1,505.00 | −3,430.00 | −145.00 | −25,525.00 | −26,650.00 | −25,960.00 |
| LR3-T10 | 91 | −966.00 | −0.354 | −20,986.00 | 45.1 | 17 | 5.9 | −1,070.00 | −3,430.00 | 80.00 | −21,226.00 | −17,800.00 | −22,188.02 |
| LR3-T12 | 91 | +864.00 | +0.316 | −19,156.00 | 44.0 | 17 | 5.9 | −1,050.00 | −3,430.00 | 140.00 | −19,576.00 | −16,994.50 | −21,692.05 |
| LR3-T15 | 91 | +2,304.00 | +0.844 | −17,716.00 | 40.7 | 17 | 11.8 | −780.00 | −3,430.00 | 230.00 | −18,406.00 | −17,507.50 | −20,852.20 |
| LR3-T20 | 91 | −600.00 | −0.220 | −20,620.00 | 29.7 | 17 | 5.9 | −1,230.00 | −3,430.00 | 380.00 | −21,760.00 | −17,348.50 | −20,475.40 |

## 2. Trailing variants — OR 1-min, activate +8, initial stop −9 (October)

| Variant | Trail | Trades | Gross ₹ | Gross pts/tr | Net ₹ | Win % | Days | Days green % | Median day ₹ | Worst day ₹ | Best day ₹ | Ex-top3 ₹ | Lag placebo ₹ | Random placebo mean ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| OR1-TRAIL | 5 | 73 | +6,022.50 | +2.750 | −10,037.50 | 32.9 | 17 | 29.4 | −490.00 | −2,940.00 | 1,478.00 | −14,326.00 | −9,160.00 | −13,985.58 |
| OR1-TRAILW | 7 | 73 | +6,516.00 | +2.975 | −9,544.00 | 28.8 | 17 | 35.3 | −490.00 | −2,940.00 | 1,418.00 | −14,279.50 | −10,106.50 | −14,378.65 |
| OR1-TRAILT4 | 4 | 73 | +6,622.50 | +3.024 | −9,437.50 | 35.6 | 17 | 29.4 | −490.00 | −2,940.00 | 1,508.00 | −13,816.00 | −8,470.00 | −13,608.78 |
| OR1-TRAILT3 | 3 | 74 | +6,940.50 | +3.126 | −9,339.50 | 35.1 | 17 | 29.4 | −490.00 | −2,940.00 | 1,538.00 | −13,808.00 | −8,622.50 | −13,187.98 |

## 3. Premium-velocity PV1 — October (v1 mechanics: +12/−9, cap 4/day, spacing 10)

| Variant | Trades | Gross ₹ | Gross pts/tr | Net ₹ | Win % | Days | Days green % | Median day ₹ | Worst day ₹ | Best day ₹ | Ex-top3 ₹ | Lag placebo ₹ | Random placebo mean ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| PV1 | 68 | +1,626.00 | +0.797 | −13,334.00 | 45.6 | 17 | 5.9 | −700.00 | −1,330.00 | 560.00 | −13,754.00 | −12,530.00 | −16,704.20 |

## October read

**(a) Least-bad / best variant in October:** **OR1-TRAILT3** — the full-window best is
also October's best, by both net and gross efficiency: 74 trades, gross **+₹6,940.50
(+3.13 pts/trade)**, net **−₹9,339.50**, win 35.1%, 5 of 17 days net-green (29.4%),
median day −₹490, worst −₹2,940, best +₹1,538. It beats its October random placebo
(mean −₹13,187.98) — and **no variant of the 25 was net-positive in October**; the
least-bad fixed-target variant was OR3-T20 at −₹7,725.50, which is only "least-bad"
because it traded least (44 trades = least cost load).

**(b) Trailing family vs the 7.33-pt cost breakeven:** October gross was +2.75 (trail 5),
+2.98 (trail 7), +3.02 (trail 4), **+3.13 pts/trade (trail 3)** — the same ordering as the
full window, and slightly *below* the full-window TRAILT3 figure of +3.27. October's
best captures **~43% of the 7.33-pt breakeven** (full window: ~45%). October was not a
better month for the trailing mechanism; it was marginally worse.

**(c) Days-green, TRAILT3:** October **29.4%** (5/17 days) vs full window **25.4%** —
a +4-point difference on a 17-day sample, with the median October day still −₹490.
Not a material difference; both say roughly 3 days in 4 end red.

**(d) Does October change any conclusion?** No — it is the same arithmetic in a smaller
window, with two honest wrinkles. First, the wrinkles: two LR3 rungs (T12 +0.32, T15
+0.84 pts/trade) and OR3-T20 (+1.48) show small *positive gross* in October where the
full window showed LR negative at every rung — but their nets are −₹19,156 / −₹17,716 /
−₹7,725.50, LR3-T12's own lag placebo (−₹16,994.50) beats the variant itself, and
LR1's random placebo beats the LR1 variants outright at several rungs, so the wrinkles
are slice noise around a negative centre, not a contradiction with evidence behind
them. Second, the confirmations: the +2.5 rung's win rate is **0.0% in October too**,
on all four setups (even OR1-T2.5's *best day* was −₹145 — the cost arithmetic made
visible); the trailing ridge keeps its full-window ordering with TRAILT3 on top; and
every variant's ex-top-3 is worse than its headline, so nothing is a few lucky trades
from green. October, the strongest month for the level-based books, does not rescue
sub-5-minute scalping: at ₹220/trade the cost load (74 trades ≈ ₹16,280 for TRAILT3)
still runs at more than twice the genuine gross the best mechanism manufactures
(₹6,940.50). The terminated engine's verdict stands unmodified.
