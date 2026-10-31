# October 2026 — Four-column table: Nifty and Bank Nifty systems separately, date by date

Paper only. No orders placed, no live trading, no live-trading recommendation.
**NOT adopted on October alone.** October is 18 trading days, small-N, and
cap artefacts are visible in it (see notes). This table separates systems;
it does not pool them into a new system.

## Interpretation (stated so it can be corrected)

The user wording was short ("nifty stuff separately and the version which
we found edge for bank nifty separately and the skill creator skill trader
skill for separate bank nifty and nifty — four columns, all the dates from
October"). The four main columns below are read as:

1. **Nifty (lA)** — the original Nifty (lA) rule: BN-confirmed rescan
   morning + band-filtered re-entry, morning scan-skip to 11:30,
   afternoon stop-on-first-fail to 15:05, PE only. This was the Nifty edge
   leg in Jan–Oct ((lA)-only Nifty: 24 trades, 79.2% green, +₹71,780).
2. **Bank Nifty V4** — V4 as the previous best-kept index version,
   Bank Nifty leg only, capped-v2 definition.
3. **Day Trader skill — Bank Nifty only** — creator Jake Schincariol's
   Day Trader skill, Indian adaptation, OR-only with V4-style filters.
4. **Day Trader skill — Nifty only** — same skill, Nifty only.

If column 2 was meant to be a different Bank system, the appendix still
contains the other Bank legs (V4 Nifty, (lA) Bank mirror, V5 Bank) so the
table can be re-cut without a new run. The four main columns were NOT
changed after seeing results.

## Scope, rules, and reconciliation

- **Window: 1–28 October 2026 only, 18 trading days.** 29 Oct excluded
  (still in progress that day, not in the cache). Trading days, verified
  from the 5-min cache: 1, 5, 6, 7, 8, 9, 12, 13, 14, 15, 16, 19, 21, 22,
  23, 26, 27, 28 Oct. (2 Oct, 20 Oct and weekends are not trading days
  in this cache.)
- **Every date gets a row**, including no-trade days (shown as no-trade /
  ₹0, not omitted).
- **Provisional cash rules, NOT Chandu's live options rules:** 100 shares
  equivalent, ₹40/trade cost, signal-candle stop, 2× target, square-off
  15:10, short paper-only. Index nets are point-scaled cash-equivalents
  (100 × index points), NOT portfolio rupees.
- **Capped series, as in the October standalone / dual / triple reports:**
  prospective net target ≥ ₹500, max 3 index trades/week, max 1
  trade/symbol/week. Columns are **separate systems**, so a trade can
  appear in more than one column if two systems fire on the same
  symbol+date — that is stated, not deduped across columns. In particular:
  Bank 1 Oct (+₹16,640) appears in both Bank V4 and Skill Bank, and
  Nifty 8 Oct appears in both Nifty (lA) (+₹11,690, later rescan signal)
  and Skill Nifty (+₹5,440, earlier OR signal) — same day, different
  signals, different nets.
- **Reconciliation — all known October totals match exactly:**
  - Skill index October: 3 trades / +₹16,610 = Skill Bank +₹16,640
    + Skill Nifty −₹30. ✓
  - V4 index October: 7 trades / +₹51,825 = Bank V4 +₹43,630
    + V4 Nifty +₹8,195 (appendix). ✓
  - (lA)-only October, capped: 4 trades / +₹35,805 = Nifty (lA) +₹23,080
    + (lA) Bank mirror capped +₹12,725 (appendix). ✓
  - (lA) uncapped October: 5 trades / +₹59,865. The 5th candidate,
    Bank 23 Oct +₹24,060, is capped out (W43 already has Bank 21 Oct;
    bias-strong breaks the tie, 21 Oct = 1, 23 Oct = 0) — footnoted,
    not hidden.

## Date-wise table — October 2026

| Date | Nifty (lA) net | Bank V4 net | Skill Bank net | Skill Nifty net |
|---|---|---|---|---|
| 2026-10-01 Thu | no-trade | setup4 CE target **+₹16,640** | OR CE target **+₹16,640** | no-trade |
| 2026-10-05 Mon | no-trade | no-trade | no-trade | no-trade |
| 2026-10-06 Tue | no-trade | no-trade | no-trade | no-trade |
| 2026-10-07 Wed | no-trade | no-trade | no-trade | no-trade |
| 2026-10-08 Thu | PE rescan target **+₹11,690** | no-trade | no-trade | OR PE target **+₹5,440** |
| 2026-10-09 Fri | no-trade | no-trade | no-trade | no-trade |
| 2026-10-12 Mon | no-trade | no-trade | no-trade | no-trade |
| 2026-10-13 Tue | no-trade | setup3 PE stop **−₹3,730** | no-trade | no-trade |
| 2026-10-14 Wed | no-trade | no-trade | no-trade | no-trade |
| 2026-10-15 Thu | no-trade | no-trade | no-trade | no-trade |
| 2026-10-16 Fri | no-trade | no-trade | no-trade | no-trade |
| 2026-10-19 Mon | no-trade | no-trade | no-trade | no-trade |
| 2026-10-21 Wed | no-trade | setup2 PE target **+₹20,200** | no-trade | no-trade |
| 2026-10-22 Thu | no-trade | no-trade | no-trade | no-trade |
| 2026-10-23 Fri | PE rescan target **+₹11,390** | no-trade | no-trade | no-trade |
| 2026-10-26 Mon | no-trade | setup3 PE target **+₹10,520** | no-trade | no-trade |
| 2026-10-27 Tue | no-trade | no-trade | no-trade | no-trade |
| 2026-10-28 Wed | no-trade | no-trade | no-trade | OR PE stop **−₹5,470** |

Notes on the table:
- Nifty (lA) signals: 8 Oct rescan 11:25, 23 Oct rescan 10:05; both
  morning targets, no re-entry leg fired in October (as in the dual
  report — October tests the (lA) rescan morning, not its re-entry rule).
- Bank V4 signals: 1 Oct setup4 CE, 13 Oct setup3 PE, 21 Oct setup2 PE,
  26 Oct setup3 PE. The V4 Bank candidate on 23 Oct (+₹24,060, same
  trade as the (lA) mirror candidate) is capped out in W43 by the
  21 Oct Bank trade — it is in the appendix/uncapped pool, not in the
  capped Bank V4 column.
- Skill Bank has exactly one October trade (1 Oct); Skill Nifty has
  exactly two (8 Oct target, 28 Oct stop). All other October dates are
  no-trade for Skill index — the 393 raw OR signals in October are
  filtered out before any net is computed, and their unfiltered net is
  NOT claimed.

## Totals per column (separate — do not read as one system)

| Column | Trades | Green (net > 0) | Net ₹ | Expectancy ₹ |
|---|---|---|---|---|
| **1. Nifty (lA)** | **2** | **2 / 100%** | **+₹23,080** | **+₹11,540** |
| **2. Bank V4** | **4** | **3 / 75.0%** | **+₹43,630** | **+₹10,907.50** |
| **3. Skill Bank** | **1** | **1 / 100%** | **+₹16,640** | **+₹16,640** |
| **4. Skill Nifty** | **2** | **1 / 50.0%** | **−₹30** | **−₹15** |

Frequency in October: Nifty (lA) 0.4/week, Bank V4 0.8/week,
Skill Bank 0.2/week, Skill Nifty 0.4/week — all well below any
2–3/week quality-frequency bar, because October is 18 days and each
column is deliberately narrow (one system, one index).

## Verdict — which column actually had an edge in October alone?

- **Bank V4 is the strongest October column on substance:** 4 trades,
  75% green, +₹43,630, expectancy +₹10,908, and the only column with
  more than two trades that is also strongly positive. Its edge in
  October is real in the sense that it is not one trade: three
  separate targets (1, 21, 26 Oct) against one stop (13 Oct).
- **Nifty (lA) is clean but tiny:** 2/2 green, +₹23,080, expectancy
  +₹11,540 — the highest expectancy, but on 2 trades. That is
  consistent with its Jan–Oct Nifty edge (79.2% green), not proof of
  it on its own.
- **Skill Bank is a single trade:** 1/1, +₹16,640. A 100% win rate on
  one trade is not an edge claim — and the trade is the same 1 Oct
  trade already counted in Bank V4, so it adds no independent evidence.
- **Skill Nifty is flat:** 2 trades, +₹5,440 − ₹5,470 = −₹30. No edge
  in October; the target and the stop cancel exactly.

**October alone cannot be adoption for any column.** Reasons, all
visible in this table: (a) 18 days / 1–4 trades per column is small-N;
(b) cap artefacts remove large trades (Bank 23 Oct +₹24,060 capped out
  of both Bank V4 and (lA) Bank; V4 Nifty 28 Oct −₹5,470 capped out by
  the 26 Oct Nifty trade in W44); (c) the (lA) re-entry leg fired zero
  times in October, so column 1 says nothing about re-entry;
(d) columns overlap on the same days (1 Oct, 8 Oct), so their nets
  are not independent observations.

## Footnote only — pooled total (labelled, NOT the headline)

Adding the four columns together gives 9 trade-cells and
+₹23,080 + ₹43,630 + ₹16,640 − ₹30 = **+₹83,320**. This number is
**double-counted by design** (Bank 1 Oct counted twice, Nifty 8 Oct
counted as two different signals) and mixes four separate systems.
It must NOT be quoted as a system total, a portfolio result, or an
adoption metric. The honest headline is the four separate column
totals above.

## Appendix — other Bank / Nifty legs, so the table can be re-cut

These are NOT main columns; they are here only so a different column-2
(or column-1) choice does not need a new run.

| Leg (October 2026, capped unless stated) | Trades | Green | Net ₹ | Trades in detail |
|---|---|---|---|---|
| V4 Nifty (capped-v2 index leg) | 3 | 2 / 66.7% | +₹8,195 | 8 Oct setup2 PE target +₹5,440; 23 Oct setup2 PE target +₹11,390; 26 Oct setup4 CE stop −₹8,635 |
| (lA) Bank mirror, capped | 2 | 1 / 50.0% | +₹12,725 | 7 Oct rescan morning stop, no re-entry −₹7,475; 21 Oct rescan target +₹20,200 |
| (lA) Bank mirror, uncapped | 3 | 2 / 66.7% | +₹36,785 | Above + 23 Oct rescan target +₹24,060 (capped out in W43) |
| V5 Bank (pooled V4+Skill, October) | 4 | 3 / 75.0% | +₹43,630 | Identical to Bank V4 capped in October (V5 dedup pool = V4 pool for Bank) |
| V5 Nifty (October) | 3 | 2 / 66.7% | +₹8,195 | Identical to V4 Nifty capped in October |
| V4 Bank, uncapped candidates | 5 | 4 | +₹67,690 | Capped 4 (+₹43,630) + 23 Oct setup2 PE target +₹24,060 (capped out in W43) |
| (lA) Nifty, uncapped | 2 | 2 / 100% | +₹23,080 | Same as capped — no Nifty (lA) candidate was capped out in October |

Cross-checks: V4 index October = Bank V4 +₹43,630 + V4 Nifty +₹8,195
= +₹51,825 (7 trades). (lA)-only October capped = Nifty (lA) +₹23,080
+ (lA) Bank capped +₹12,725 = +₹35,805 (4 trades). Skill index October
= Skill Bank +₹16,640 + Skill Nifty −₹30 = +₹16,610 (3 trades).

## Sources and files

- This report: `~/workspace/trading/october_2026_four_column_nifty_bank_skill.md`
- CSV (same date-wise table):
  `~/workspace/trading/october_2026_four_column.csv`
- Sources reconciled to: `~/workspace/trading/october_2026_v4_and_skill.md`
  (V4 + Skill October), `~/workspace/trading/merged_skill_la_index_october_2026.md`
  ((lA) October), `~/workspace/trading/triple_v4_skill_la_index_jan_oct_2026.md`
  (triple October slice), and month JSONs
  `~/workspace/trading/data/progressive/capped_v2_summary_2026-10.json`,
  `merged_skill_la_summary_2026-10.json`,
  `triple_v4_skill_la_summary_2026-10.json`,
  `v5_index_summary_2026-10.json`.
- Provisional cash rules throughout (100 shares, ₹40/trade, signal-candle
  stop, 2× target, square-off 15:10). Bank (lA) mirror is provisional,
  not the original Nifty-only (lA); it is appendix-only here, not a main
  column.
