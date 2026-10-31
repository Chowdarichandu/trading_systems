# Four-column long run — Jan 2025 to 29 Oct 2026 inclusive

Paper only. No orders placed, no live trading, no live-trading recommendation.
**NOT adopted on this run alone.** See verdict §6.

## Columns (stated at the top so they can be corrected)

Same four columns as
`~/workspace/trading/october_2026_four_column_nifty_bank_skill.md`:

1. **Nifty (lA)** — original Nifty (lA) rule: BN-confirmed rescan morning +
   band-filtered re-entry, scan-skip to 11:30, afternoon stop-on-first-fail
   to 15:05, PE only. Source definition:
   `~/workspace/trading/nifty_cluster1_extended_window_sweep.md` and
   `~/workspace/trading/merged_skill_la_index_october_2026.md` /
   `merged_skill_la_jan_oct.py`.
2. **Bank Nifty V4** — V4 version, Bank leg only, capped-v2 V4 index
   definition (`~/workspace/trading/jan_oct_2026_v4_and_skill.md`,
   `~/workspace/trading/progressive_capped_v2.py`).
3. **Day Trader skill — Bank Nifty only** — Jake Schincariol's Day Trader
   skill, Indian adaptation (`~/workspace/custom-skills/day-trader-india/SKILL.md`),
   Bank Nifty only, OR-only with V4-style filters (bias-aligned, room
   ≥ 200× scale, PD bound).
4. **Day Trader skill — Nifty only** — same skill definition, Nifty only.

Columns are **separate systems**: a trade can appear in more than one
column (e.g. the same Bank breakdown day in both Bank V4 and Skill Bank).
That is stated, not deduped across columns. Column totals must NOT be
added together as a portfolio total.

## Frozen rules (no re-tuning in this run)

- **Provisional cash rules — NOT Chandu's rules, labelled as such:**
  100 shares equivalent, ₹40/trade cost, signal-candle stop, 2× target,
  square-off 15:10, short paper-only. Index nets are point-scaled
  cash-equivalents (100 × index points), NOT portfolio rupees.
- **Capped series:** prospective target net ≥ ₹500, max 3 index trades/week,
  max 1 trade/symbol/week, cap applied **within each calendar month**
  (capped-v2 precedent). Results gate NEUTRAL.
- Green = net > 0. Expectancy = net ÷ trades. Max drawdown = peak-to-trough
  of the date-ordered cumulative net within that column.

## Why 29 Oct 2026 was missed before

The October four-column run used the progressive cache in
`~/workspace/trading/data/progressive/`, which ends **28 Oct 2026**, and it
was run while 29 Oct was still in progress / not in that cache — the
Upstox completed-days endpoint returns completed days only, so 29 Oct
was excluded explicitly. The market has now closed (15:30 IST, 29 Oct
2026), so 29 Oct is included here using the Upstox intraday route
(`intraday` subcommand of
`~/workspace/custom-connectors/custom.upstox/bin/upstox.py`, calling
`/v3/historical-candle/intraday/{instrument_key}/{unit}/{interval}`).
No 401 occurred; both intraday fetches returned `status: success`.

## Data and coverage — no gaps left, one boundary noted

- **Window: 1 Jan 2025 – 29 Oct 2026 inclusive, 453 trading days**
  (2025: 249 days, 2026: 203 days to 28 Oct, plus 29 Oct 2026).
  NIFTY and BANKNIFTY spot files have exactly the same 452 cache days.
- Jan 2025 – Nov 2025 V4/Skill: existing
  `capped_v2_summary_YYYY-MM.json` files. **Dec 2025 was missing** from
  that set, so it was run fresh in this task with
  `progressive_capped_v2.py 2025 12` (no existing file overwritten):
  22 days, V4 index 10 trades / −₹36,845, Skill index 9 / −₹39,995.
- (lA) month JSONs existed for Jan–Oct 2026 only. **2025 (lA) was run
  fresh** in this task with `~/workspace/trading/four_column_la_2025.py`
  (same frozen definition as `merged_skill_la_jan_oct.py`). Validation
  first: the same script run on 2026-01 reproduces the existing
  January 2026 (lA) capped set **exactly** (5 trades / +₹11,875;
  Nifty 2 / +₹11,575, Bank mirror 3 / +₹300), trade by trade, before
  any 2025 month was trusted.
- Boundary, not a missing day: **1 Jan 2025 has no prior day in the
  cache**, so no column can form a PD-based candidate that day (the v2
  engine skips the first cache row; the (lA) engine finds no previous
  day). Its CSV row exists with ₹0 in all columns. No other day is
  missing, and no day was invented.
- 29 Oct 2026: intraday 5-min data for both indices (see §4), with
  prior-day (28 Oct) PD levels from the cache daily files.

## 1. Grand totals — Jan 2025 to 29 Oct 2026

96 ISO weeks spanned. A single-symbol column can trade at most
1/week under the 1/symbol/week cap, so 2–3/week is unattainable for
any one column here; frequency is judged against that ceiling as well
as against the portfolio-level 2–3/week bar (see verdict).

| Column | Trades | Green | Green % | Net ₹ | Expectancy ₹ | Max DD ₹ | Trades/week |
|---|---|---|---|---|---|---|---|
| **1. Nifty (lA)** | **61** | **37** | **60.7%** | **+₹99,125** | **+₹1,625.00** | **₹23,345** | **0.64** |
| **2. Bank V4** | **76** | **24** | **31.6%** | **−₹25,060** | **−₹329.74** | **₹88,245** | **0.79** |
| **3. Skill Bank** | **58** | **15** | **25.9%** | **−₹96,400** | **−₹1,662.07** | **₹115,950** | **0.60** |
| **4. Skill Nifty** | **54** | **29** | **53.7%** | **+₹94,005** | **+₹1,740.83** | **₹19,750** | **0.56** |

Subtotals:

| Period | Nifty (lA) | Bank V4 | Skill Bank | Skill Nifty |
|---|---|---|---|---|
| 2025 (12 months) | 37 trades, 18 green, +₹27,345 | 41, 11, −₹51,420 | 29, 6, −₹86,750 | 25, 13, +₹44,115 |
| Jan–Oct 2026 (incl. 29 Oct no-trade) | 24, 19, +₹71,780 | 35, 13, +₹26,360 | 29, 9, −₹9,650 | 29, 16, +₹49,890 |

Both Nifty columns are net-positive in **both** calendar years; both
Bank columns are net-negative over the full window despite a positive
Jan–Oct 2026 Bank V4 leg, because 2025 drags them under.

## 2. Month-by-month tables (trades, green, net, cumulative net)

### Column 1 — Nifty (lA)

| Month | Trades | Green | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| 2025-01 | 3 | 1 | −₹8,430 | −₹8,430 |
| 2025-02 | 4 | 3 | +₹9,395 | +₹965 |
| 2025-03 | 1 | 0 | −₹7,275 | −₹6,310 |
| 2025-04 | 2 | 2 | +₹20,410 | +₹14,100 |
| 2025-05 | 4 | 1 | −₹8,740 | +₹5,360 |
| 2025-06 | 1 | 1 | +₹11,060 | +₹16,420 |
| 2025-07 | 4 | 2 | +₹3,650 | +₹20,070 |
| 2025-08 | 3 | 2 | +₹6,560 | +₹26,630 |
| 2025-09 | 4 | 0 | −₹18,855 | +₹7,775 |
| 2025-10 | 4 | 4 | +₹24,670 | +₹32,445 |
| 2025-11 | 2 | 1 | +₹1,740 | +₹34,185 |
| 2025-12 | 5 | 1 | −₹6,840 | +₹27,345 |
| 2026-01 | 2 | 2 | +₹11,575 | +₹38,920 |
| 2026-02 | 3 | 2 | +₹1,815 | +₹40,735 |
| 2026-03 | 3 | 2 | +₹9,305 | +₹50,040 |
| 2026-04 | 2 | 2 | +₹9,260 | +₹59,300 |
| 2026-05 | 3 | 1 | −₹3,035 | +₹56,265 |
| 2026-06 | 1 | 1 | +₹2,100 | +₹58,365 |
| 2026-07 | 2 | 2 | +₹7,275 | +₹65,640 |
| 2026-08 | 4 | 3 | +₹4,145 | +₹69,785 |
| 2026-09 | 2 | 2 | +₹6,260 | +₹76,045 |
| 2026-10 (incl. 29 Oct) | 2 | 2 | +₹23,080 | **+₹99,125** |

### Column 2 — Bank Nifty V4

| Month | Trades | Green | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| 2025-01 | 3 | 0 | −₹45,905 | −₹45,905 |
| 2025-02 | 4 | 2 | +₹42,435 | −₹3,470 |
| 2025-03 | 2 | 0 | −₹14,430 | −₹17,900 |
| 2025-04 | 3 | 0 | −₹32,275 | −₹50,175 |
| 2025-05 | 4 | 2 | +₹24,150 | −₹26,025 |
| 2025-06 | 2 | 0 | −₹10,595 | −₹36,620 |
| 2025-07 | 5 | 3 | +₹7,945 | −₹28,675 |
| 2025-08 | 4 | 1 | −₹9,205 | −₹37,880 |
| 2025-09 | 3 | 0 | −₹18,390 | −₹56,270 |
| 2025-10 | 3 | 3 | +₹47,420 | −₹8,850 |
| 2025-11 | 3 | 0 | −₹11,155 | −₹20,005 |
| 2025-12 | 5 | 0 | −₹31,415 | −₹51,420 |
| 2026-01 | 3 | 1 | +₹6,900 | −₹44,520 |
| 2026-02 | 3 | 0 | −₹24,615 | −₹69,135 |
| 2026-03 | 3 | 3 | +₹65,340 | −₹3,795 |
| 2026-04 | 4 | 2 | +₹4,300 | +₹505 |
| 2026-05 | 3 | 2 | +₹9,165 | +₹9,670 |
| 2026-06 | 4 | 0 | −₹34,260 | −₹24,590 |
| 2026-07 | 5 | 1 | −₹14,055 | −₹38,645 |
| 2026-08 | 4 | 0 | −₹33,655 | −₹72,300 |
| 2026-09 | 2 | 1 | +₹3,610 | −₹68,690 |
| 2026-10 (incl. 29 Oct) | 4 | 3 | +₹43,630 | **−₹25,060** |

### Column 3 — Day Trader skill, Bank Nifty only

| Month | Trades | Green | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| 2025-01 | 3 | 0 | −₹45,905 | −₹45,905 |
| 2025-02 | 4 | 2 | +₹28,095 | −₹17,810 |
| 2025-03 | 1 | 0 | −₹9,430 | −₹27,240 |
| 2025-04 | 2 | 1 | +₹22,440 | −₹4,800 |
| 2025-05 | 3 | 0 | −₹30,960 | −₹35,760 |
| 2025-06 | 1 | 0 | −₹4,685 | −₹40,445 |
| 2025-07 | 3 | 2 | +₹9,585 | −₹30,860 |
| 2025-08 | 3 | 1 | −₹3,515 | −₹34,375 |
| 2025-09 | 1 | 0 | −₹3,590 | −₹37,965 |
| 2025-10 | 0 | 0 | ₹0 | −₹37,965 |
| 2025-11 | 3 | 0 | −₹17,370 | −₹55,335 |
| 2025-12 | 5 | 0 | −₹31,415 | −₹86,750 |
| 2026-01 | 3 | 1 | +₹6,900 | −₹79,850 |
| 2026-02 | 1 | 0 | −₹7,080 | −₹86,930 |
| 2026-03 | 4 | 3 | +₹56,040 | −₹30,890 |
| 2026-04 | 4 | 1 | −₹2,975 | −₹33,865 |
| 2026-05 | 4 | 1 | −₹23,310 | −₹57,175 |
| 2026-06 | 1 | 0 | −₹15,645 | −₹72,820 |
| 2026-07 | 4 | 1 | −₹565 | −₹73,385 |
| 2026-08 | 4 | 0 | −₹33,655 | −₹107,040 |
| 2026-09 | 3 | 1 | −₹6,000 | −₹113,040 |
| 2026-10 (incl. 29 Oct) | 1 | 1 | +₹16,640 | **−₹96,400** |

### Column 4 — Day Trader skill, Nifty only

| Month | Trades | Green | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| 2025-01 | 2 | 0 | −₹12,440 | −₹12,440 |
| 2025-02 | 3 | 2 | +₹14,700 | +₹2,260 |
| 2025-03 | 1 | 1 | +₹2,340 | +₹4,600 |
| 2025-04 | 2 | 2 | +₹22,415 | +₹27,015 |
| 2025-05 | 2 | 0 | −₹8,475 | +₹18,540 |
| 2025-06 | 0 | 0 | ₹0 | +₹18,540 |
| 2025-07 | 4 | 2 | +₹5,290 | +₹23,830 |
| 2025-08 | 3 | 2 | +₹9,180 | +₹33,010 |
| 2025-09 | 1 | 0 | −₹1,380 | +₹31,630 |
| 2025-10 | 2 | 2 | +₹14,045 | +₹45,675 |
| 2025-11 | 1 | 1 | +₹7,020 | +₹52,695 |
| 2025-12 | 4 | 1 | −₹8,580 | +₹44,115 |
| 2026-01 | 4 | 2 | +₹5,990 | +₹50,105 |
| 2026-02 | 3 | 1 | +₹1,325 | +₹51,430 |
| 2026-03 | 3 | 3 | +₹21,600 | +₹73,030 |
| 2026-04 | 4 | 2 | +₹10,780 | +₹83,810 |
| 2026-05 | 3 | 1 | −₹3,705 | +₹80,105 |
| 2026-06 | 2 | 0 | −₹8,545 | +₹71,560 |
| 2026-07 | 3 | 2 | +₹8,575 | +₹80,135 |
| 2026-08 | 3 | 2 | +₹6,950 | +₹87,085 |
| 2026-09 | 2 | 2 | +₹6,950 | +₹94,035 |
| 2026-10 (incl. 29 Oct) | 2 | 1 | −₹30 | **+₹94,005** |

## 3. Reconciliation (explicit — mismatches would be flagged here; none found)

### October 2026 — matches the October four-column run exactly

| Column | Oct 1–28 (prior run) | Oct 1–29 (this run) | 29 Oct addition |
|---|---|---|---|
| Nifty (lA) | 2 trades / +₹23,080 | 2 / +₹23,080 | ₹0 — no trade |
| Bank V4 | 4 / +₹43,630 | 4 / +₹43,630 | ₹0 — no trade |
| Skill Bank | 1 / +₹16,640 | 1 / +₹16,640 | ₹0 — no trade |
| Skill Nifty | 2 / −₹30 | 2 / −₹30 | ₹0 — no trade |

October was also re-derived from the full candidate pools plus the
29 Oct candidates and re-capped within October (ISO week W44):
the re-cap reproduces the 1–28 sets trade by trade, and 29 Oct adds
no candidate to any column, so there is **no displacement** of a
26–28 Oct trade and no second, different October total. The
"October-with-29-Oct" line is therefore identical to the 1–28 line.

### Jan–Oct 2026 subtotals — all known benchmarks reproduce exactly

- **V4 index** 62 trades / +₹68,770 = Bank V4 35 / +₹26,360 +
  V4 Nifty 27 / +₹42,410. ✓ Column 2 (Bank only) is therefore
  deliberately **not** equal to the V4 index total; the Bank leg alone
  is +₹26,360, and Bank + Nifty = +₹68,770.
- **Skill index** 58 / +₹40,240 = Skill Bank 29 / −₹9,650 +
  Skill Nifty 29 / +₹49,890. ✓
- **(lA)-only** 47 / +₹23,435 = Nifty (lA) 24 / +₹71,780 +
  (lA) Bank mirror 23 / −₹48,345. ✓ The Bank mirror is appendix-only
  here, not a main column.
- **Dual Skill + (lA)** 66 / −₹1,600 and **triple** 74 / +₹23,355
  (from `triple_v4_skill_la_summary_2026-jan-oct.json`) both
  reproduce. ✓
- Full-window cross-check: V4 index Jan 2025–Oct 2026 =
  Bank V4 76 / −₹25,060 + V4 Nifty 83 / +₹55,070 = 159 / +₹30,010
  (2025 V4 index alone: 83 / +₹3,650). (lA) Bank mirror full window:
  2025: 34 trades / −₹8,685; Jan–Oct 2026: 23 / −₹48,345;
  total 57 / −₹57,030. So (lA)-only full window =
  Nifty (lA) 61 / +₹99,125 + Bank mirror 57 / −₹57,030 =
  118 trades / +₹42,095. These appendix legs are shown so the
  column-2 / column-1 choices can be re-cut without a new run;
  they are not CSV columns.

Note on overlap: Bank V4 and Skill Bank coincide on several
breakdown days (e.g. all five Dec 2025 Bank trades: 3, 11, 17, 26,
29 Dec, setup2 OR breakdown PE, identical nets in both columns).
That is expected — V4 setup2 and the Skill OR breakdown are the
same day's breakdown — and is why columns are not added together.

## 4. 29 Oct 2026 — computed from intraday data, not copied from the morning paper map

Intraday fetches (Upstox intraday route, after close): both indices
returned 75 five-min bars, 09:15–15:25 IST, `status: success`.

- **Bank Nifty:** open 54,175.60, high 54,980.15, low 54,047.90,
  close 54,909.65 — matching the reference context, but the column
  verdicts below were recomputed from the bars, not copied.
  Prior day (28 Oct): PDH 54,440.25, PDC 54,267.40, PDL 53,626.15,
  bias neutral (close-position 78.8%), scale 0.9867.
  Opening range: high 54,379.95, low 54,047.90, width 332.05.
- **Nifty:** open 22,690.65, high 22,961.95, low 22,656.75,
  close 22,936.75. Prior day (28 Oct): PDH 22,778.05, PDC 22,698.85,
  PDL 22,497.70, bias neutral (71.7%), scale 0.4127.
  Opening range: high 22,745.75, low 22,656.75, width 89.00.

| Column | 29 Oct signal | Outcome |
|---|---|---|
| Nifty (lA) | No morning rescan: no BN-confirmed PE breakdown rescan fired | **No-trade, ₹0** (no entry/stop/target) |
| Bank V4 | `find_signal` = none, `run_day` = no_trade | **No-trade, ₹0** |
| Skill Bank | OR breakout CE at 09:35 (close 54,409.75) — **fails the room filter**: room to PDH only 30.50 points vs required 200 × 0.9867 = 197.34 (room ratio 0.155 < 1). PD bound itself passed (close < PDH). | **Filtered out, ₹0** — not a trade |
| Skill Nifty | OR breakout CE at 09:35 (close 22,758.25) — **fails the room filter**: room to PDH only 19.80 points vs required 200 × 0.4127 = 82.54 (room ratio 0.240 < 1). PD bound passed (close < PDH). | **Filtered out, ₹0** — not a trade |

This agrees in outcome with the morning paper map's no-trade, but
it is an independent four-column computation: on a strong up day
there was no PE rescan for (lA) and no V4 setup, and the only Skill
OR signals were CE breakouts with almost no room to the prior-day
high, so the frozen room filter removed them. No 29 Oct entry, stop,
or target exists to report for any column.

## 5. What the long run shows, column by column

- **Nifty (lA) — the strongest long-run column on total net, but not
  clean progression.** +₹99,125 over 61 trades, 60.7% green, max DD
  only ₹23,345. Positive in both years (2025 +₹27,345; Jan–Oct 2026
  +₹71,780). But cumulative net does **not** rise month by month:
  it falls in Sep 2025 (−₹18,855 month), Dec 2025, and May 2026,
  and 2025 as a whole is far weaker (37 trades, 48.6% green in 2025
  vs 79.2% in Jan–Oct 2026). Frequency 0.64/week.
- **Skill Nifty — closest on risk-adjusted shape, same frequency
  problem.** +₹94,005 over 54 trades, 53.7% green, highest expectancy
  (+₹1,741) and lowest max DD (₹19,750). Positive in both years
  (2025 +₹44,115; Jan–Oct 2026 +₹49,890). But cumulative also dips
  in several months (May 2025, Sep 2025, Dec 2025, May–Jun 2026),
  so it is not month-by-month rising either. Frequency 0.56/week.
- **Bank V4 — October strength does not survive the long window.**
  −₹25,060 over 76 trades, only 31.6% green, max DD ₹88,245.
  Jan–Oct 2026 alone is +₹26,360, but 2025 is −₹51,420, and the
  cumulative path ends 2025 at −₹51,420, briefly turns positive in
  Apr–May 2026 (+₹505 / +₹9,670), then falls to −₹72,300 by Aug 2026.
  The October 2026 Bank leg (+₹43,630) is the best Bank month in
  the window and still does not rescue the column.
- **Skill Bank — the weakest column, no edge on this window.**
  −₹96,400 over 58 trades, 25.9% green, expectancy −₹1,662,
  max DD ₹115,950. Cumulative net is negative at **every** month-end
  in the window (best: −₹4,800 in Apr 2025). Only two months in
  2025–2026 exceed 50% green (Feb 2025, Mar 2026). Frequency
  0.60/week.

## 6. Verdict — no column progresses on net + win rate + frequency together

**No column passes all three legs together over Jan 2025–Oct 2026
with cumulative profit rising month by month:**

- Net: only the two Nifty columns are positive (+₹99,125 (lA),
  +₹94,005 Skill Nifty); both Bank columns are negative.
- Win rate: only the two Nifty columns exceed 50% green
  (60.7% (lA), 53.7% Skill Nifty); Bank V4 31.6%, Skill Bank 25.9%.
- Frequency: **no** column reaches 2–3 quality trades/week —
  0.56–0.79/week for all four. That bar cannot be met by a
  single-symbol column under the frozen 1/symbol/week cap (ceiling
  1/week); it would need a multi-symbol portfolio, which these
  columns are not. Even against the 1/week ceiling, the columns
  use only about 60–80% of it.
- Cumulative progression: **no** column rises month by month.
  Both Nifty columns have multiple down months and, for (lA),
  a materially weaker 2025 than 2026.

The honest ranking on this window is: Nifty (lA) ≈ Skill Nifty
(both positive, both >50% green, low drawdowns) > Bank V4
(negative, low win rate) > Skill Bank (deeply negative, lowest
win rate, largest drawdown). The two Nifty columns are the only
candidates worth carrying into unseen-month paper, and neither
is adopted here.

**Validation status — this long run is still NOT clean validation
for any column.** Every column was already scored on part of this
window (Jan–Oct 2026 for all four; 2025 for V4/Skill in the
progressive runs), and the 2025 (lA) leg computed here was derived
with the (lA) definition frozen from the 2026 work, not with a
definition frozen before 2025 was ever seen. A frozen candidate
would still need **unseen-month (November 2026) validation before
any adoption claim**, with its definition frozen and no re-tuning
on November. Nothing in this report is a live-trading
recommendation, and no lot increase follows from it. Previous best
kept for index remains V4 index on the Jan–Oct 2026 comparison
(62 / +₹68,770), paper only — but on the full Jan 2025–Oct 2026
window even V4 index is only 159 / +₹30,010, which is why the
November check matters more than re-quoting the 2026 slice.

## Files

- This report: `~/workspace/trading/four_column_jan2025_oct2026.md`
- Date-wise CSV (453 rows, every trading day, no-trade days as ₹0):
  `~/workspace/trading/four_column_jan2025_oct2026.csv`
  Columns: `date, nifty_la_net, nifty_la_trade, bank_v4_net, bank_v4_trade,
  skill_bank_net, skill_bank_trade, skill_nifty_net, skill_nifty_trade`.
  The 460+ row figure in the task assumed a longer day count; the
  verified trading-day count is 453 (249 + 203 + 29 Oct). The CSV
  carries all daily rows; they are not dumped into this report text.
- Supporting scripts (frozen definitions, not new systems):
  `~/workspace/trading/four_column_build.py` (CSV + aggregates),
  `~/workspace/trading/four_column_la_2025.py` (2025 (lA) fill, validated
  on 2026-01), `~/workspace/trading/four_column_29oct.py` (29 Oct
  computation + October re-cap),
  `~/workspace/trading/four_column_29oct_candidates.json` (29 Oct
  candidate dump).
- New month JSONs written by this run (existing files untouched):
  `~/workspace/trading/data/progressive/capped_v2_summary_2025-12.json`,
  `~/workspace/trading/data/progressive/merged_skill_la_summary_2025-01.json`
  through `...-2025-12.json`.
- Sources reconciled to: October four-column report and CSV,
  `capped_v2_summary_*.json`, `merged_skill_la_summary_*.json`,
  `triple_v4_skill_la_summary_2026-jan-oct.json`.
- Provisional cash rules throughout (100 shares, ₹40/trade,
  signal-candle stop, 2× target, square-off 15:10). These are NOT
  Chandu's live options rules.
