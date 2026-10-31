# U1 — Unified-1 — Jan–Oct 2026 run

**Paper only. No orders. No stocks. Index OPTIONS only.**
**Real money made = ₹0 — no live trades were placed.**
**Nothing is adopted on this run alone.** Adoption still needs frozen
November 2026 paper from Monday 2026-11-02, separate Nifty/Bank logs,
no re-tuning during November.

Frozen definition: [index_options_U1_frozen.md](sandbox://workspace/trading/index_options_U1_frozen.md)
Trades (362 unique keys): [index_options_U1_janoct_trades.csv](sandbox://workspace/trading/index_options_U1_janoct_trades.csv)
Merge script: `u1_janoct_merge.py`
Component sources: [index_options_U1_skillV3_jansep_spot.csv](sandbox://workspace/trading/index_options_U1_skillV3_jansep_spot.csv),
[index_options_U1_volrixB_jansep_spot.csv](sandbox://workspace/trading/index_options_U1_volrixB_jansep_spot.csv),
`index_options_o1_janoct_trades.csv` ((lA) v2, V5 v2),
`index_options_premium_october_trades.csv` + `index_options_skill_tuned_oct30_trades.csv`
(V3) + Volrix (b) October premiums.

## 1. Method and the unit warning — read first

- **Counting: UNIQUE-ONCE.** Key = (date, index, direction). Each key once,
  earliest entry. Legs fed in: 510. Unique U1 trades: 362. Duplicate legs
  removed: 148. No double-counting, no exclusive-deletion.
- **Window:** 1 Jan – 28 Oct 2026, 203 trading days (Jan 20, Feb 21,
  Mar 19, Apr 20, May 19, Jun 21, Jul 23, Aug 21, Sep 21, Oct 18).
  October = 1–28 Oct only; 29–30 Oct are NOT in any number here.
- **October = premium, per 1 lot** (−50/+90 overlay, ₹220 cost,
  Nifty lot 65, Bank lot 30). **Jan–Sep = spot provisional per leg**
  (points × 100 shares − ₹40), because option premiums for ~300
  Jan–Sep contract-days were NOT fetched in this run (volume).
  Jan–Sep nets are therefore NOT options-lot profits and NOT futures
  profits, and they are NOT on the same scale as October premiums:
  Bank spot uses 100 shares vs a 30 lot (≈3.33× point scale),
  Nifty spot uses 100 shares vs a 65 lot (≈1.54×). **Do NOT compare a
  Jan–Sep spot net rupee-for-rupee with an October premium net, and do
  NOT present the mixed Jan–Oct total as a pure premium total.**
  Subtotals are kept separate below for exactly that reason.
- **Full-target %** = target exits only; square-off greens are not
  full targets. Frequency = trades ÷ trading days × 5, per index.
- **Validation of the two new Jan–Sep pieces:**
  - Skill V3 generator, run on October, matches V3 in
    `index_options_skill_tuned_oct30_trades.csv` on 29/29 rows
    (index, date, direction, signal/entry time, entry spot, spot net,
    spot reason). O1 Skill S1 Jan–Sep legs: all 238 keys are in the
    V3 file with identical nets, so V3 is used as the authoritative
    Skill source and O1 Skill legs are not double-fed.
  - Volrix (b) Jan–Sep: 23 legs, all triggers verified except one
    flagged conflict — Bank entry 1 Jun (trigger 29 May) passes on the
    Volrix daily file (−1.12%) but fails on progressive spot_daily
    (−0.92%, ~125-point close difference). It is KEPT in the run
    (−₹5,040 spot) and flagged; on a strict spot_daily-only basis
    Bank Jan–Sep would be −₹164,955 instead of −₹169,995, which does
    not change any verdict below.

## 2. October reproduction check — EXACT

| Index | Trades | Trades/week (÷3.6) | Full-target | Net premium / 1 lot |
|---|---|---|---|---|
| Nifty | 16 | 4.44 | 6/16 = 37.5% | **+₹14,169.75** |
| Bank Nifty | 18 | 5.00 | 10/18 = 55.6% | **+₹11,040.00** |
| Combined premium | 34 | — | 16/34 = 47.1% | **+₹25,209.75** |

Reproduces the frozen October U1 check exactly. No October leg was
re-scored or altered.

## 3. Jan–Sep — spot provisional only, per index separately

| Index | Trades | Trades/week (÷37 wks) | Full-target | Net spot provisional |
|---|---|---|---|---|
| Nifty | 163 | 4.41 | 59/163 = 36.2% | **+₹95,150.00** |
| Bank Nifty | 165 | 4.46 | 38/165 = 23.0% | **−₹169,995.00** |
| Combined spot | 328 | — | 97/328 = 29.6% | −₹74,845.00 |

Representative-system split, Jan–Sep (representative = earliest entry
on each key; other systems on the same key are overlaps, not extra
trades):
- Nifty: Skill V3 110 reps −₹19,475; (lA) v2 27 reps +₹72,325;
  Volrix (b) 11 reps +₹28,560; V5 v2 15 reps +₹13,740.
  Multi-system keys: 52 of 163.
- Bank: Skill V3 116 reps −₹171,110; (lA) v2 19 reps +₹4,715;
  V5 v2 18 reps −₹27,120; Volrix (b) 12 reps +₹23,520.
  Multi-system keys: 50 of 165.
- Standalone component totals for context (not U1 totals): Skill V3
  Jan–Sep alone Nifty +₹4,700 (151 trades, 37.1% FT), Bank −₹158,870
  (150 trades, 25.3% FT); Volrix (b) alone Nifty +₹28,560 (11, 54.5%),
  Bank +₹23,520 (12, 50.0%). The Bank problem is therefore driven
  mainly by Skill V3, not by Volrix or (lA).

## 4. Jan–Oct combined — MIXED units, labelled, never a pure premium total

| Index | Trades | Trades/week (÷40.6 wks) | Full-target | Mixed net (spot Jan–Sep + premium Oct) |
|---|---|---|---|---|
| Nifty | 179 | 4.41 | 65/179 = 36.3% | **+₹109,319.75 mixed** |
| Bank Nifty | 183 | 4.51 | 48/183 = 26.2% | **−₹158,955.00 mixed** |
| Combined mixed | 362 | — | 113/362 = 31.2% | **−₹49,635.25 mixed** |

This mixed total is an arithmetic sum across two different units.
It is reported only because the task asked for a combined figure
with its label; it must not be quoted as "U1 made −₹49,635" in
options-lot terms.

## 5. Month-by-month cumulative progression (mixed units, per index)

### Nifty — ends positive, but not steadily rising

| Month | Trades | Month net | Cumulative mixed | Full-target |
|---|---|---|---|---|
| Jan | 19 | −₹11,050.00 | −₹11,050.00 | 5 |
| Feb | 19 | +₹6,695.00 | −₹4,355.00 | 6 |
| Mar | 16 | +₹34,890.00 | +₹30,535.00 | 8 |
| Apr | 20 | +₹26,335.00 | +₹56,870.00 | 7 |
| May | 16 | −₹25,560.00 | +₹31,310.00 | 3 |
| Jun | 21 | +₹24,195.00 | +₹55,505.00 | 7 |
| Jul | 17 | +₹29,060.00 | +₹84,565.00 | 8 |
| Aug | 16 | +₹2,730.00 | +₹87,295.00 | 5 |
| Sep | 19 | +₹7,855.00 | +₹95,150.00 | 10 |
| Oct (premium) | 16 | +₹14,169.75 | +₹109,319.75 | 6 |

Nifty cumulative falls in Jan→Feb→May (May −₹25,560 is the worst
month), so it does NOT rise month by month, even though the final
total is positive and Mar/Apr/Jul carry it.

### Bank Nifty — never positive at any month-end

| Month | Trades | Month net | Cumulative mixed | Full-target |
|---|---|---|---|---|
| Jan | 19 | −₹65,870.00 | −₹65,870.00 | 2 |
| Feb | 19 | −₹37,685.00 | −₹103,555.00 | 4 |
| Mar | 17 | +₹52,490.00 | −₹51,065.00 | 6 |
| Apr | 20 | −₹41,930.00 | −₹92,995.00 | 4 |
| May | 14 | +₹47,150.00 | −₹45,845.00 | 6 |
| Jun | 20 | −₹66,725.00 | −₹112,570.00 | 2 |
| Jul | 22 | −₹46,995.00 | −₹159,565.00 | 4 |
| Aug | 17 | −₹46,815.00 | −₹206,380.00 | 3 |
| Sep | 17 | +₹36,385.00 | −₹169,995.00 | 7 |
| Oct (premium) | 18 | +₹11,040.00 | −₹158,955.00 | 10 |

Bank cumulative is negative at every month-end, worst −₹206,380
in August. Only Mar, May, Sep and Oct are green months. October's
premium +₹11,040 does not rescue the Jan–Sep spot deficit, even
allowing for the spot-vs-lot scale difference: Bank hits are 23.0%
Jan–Sep and 26.2% Jan–Oct, far below 50% in any framing.

## 6. Plain verdict — U1 does NOT hold up Jan–Oct

- **Frequency: passes as a minimum, exceeds the 2–3/week band.**
  Nifty 4.41/week, Bank 4.51/week Jan–Oct — the same pattern as
  October. Frequency was never the blocker.
- **Nifty: holds in total, fails the quality/progression bars.**
  Jan–Sep spot +₹95,150 and Jan–Oct mixed +₹109,319.75, but
  full-target only 36.3% (vs 50% bar) and cumulative dips in May,
  so it is not "profit rising month by month".
- **Bank Nifty: breaks badly outside October.** Jan–Sep spot
  −₹169,995, full-target 23.0%, cumulative negative every month.
  October (premium +₹11,040, 55.6% FT) is the outlier, not the norm.
  The driver is Skill V3 on Bank (−₹171,110 as representative,
  −₹158,870 standalone); (lA) and Volrix (b) are positive on Bank
  Jan–Sep but far too small to offset it.
- **Combined: mixed −₹49,635.25, full-target 31.2% — fails.**
  The October premium total (+₹25,209.75) must not be extrapolated
  to Jan–Oct: on the longer window U1 is a Nifty-positive,
  Bank-negative system with poor hit quality on both indices.
- **What would have to change:** Bank Skill V3 is the failing leg
  to fix or exclude in a future frozen variant — but that is a NEW
  variant, not a re-score of U1, and it must be validated on
  November paper, not on this in-sample window.
- **Nothing adopted.** U1 stays a named, frozen, in-sample
  description only. Next step remains frozen November 2026 paper
  (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning
  during November) for whatever variant is carried forward.
