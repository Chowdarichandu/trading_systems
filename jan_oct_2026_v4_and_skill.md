# January to October 2026 — V4 along with Day Trader Skill (consolidated, same report format)

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday only. Provisional rules, NOT Chandu's live options rules:
100 shares/trade, ₹40/trade assumed cost, stop = signal-candle low/high,
target = 2× stop distance, square-off 15:10, Setup 1 skipped, short signals
paper-only, one trade/instrument/day for raw runs.

## Scope and data

- Window: **January 2026 to October 2026 only. October = 1–28 Oct only — 29 Oct 2026 is NOT included**,
  it was still in progress on the day of the October run. This is NOT Jan–Oct 2025.
- Trading days in window: **203 days** (Jan 20, Feb 21, Mar 19, Apr 20, May 19, Jun 21, Jul 23, Aug 21, Sep 21, Oct 18).
- Instruments: **27 — Nifty, Bank Nifty, and 25 stocks** (GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR,
  UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM,
  VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR).
- Data: Upstox 5-min cache to 2026-10-28, already in the workspace. **Nothing was fabricated.**
  May 2026 and October 2026 are reused from their standalone reports
  (`may_2026_v4_and_skill.md`, `october_2026_v4_and_skill.md`) — not redone.
  Missing months Jan, Feb, Mar, Apr, Jun, Jul, Aug, Sep 2026 were run under the same engines
  (`progressive_capped_v2.py`) and written to `data/progressive/capped_v2_summary_2026-MM.json`.
- **INDEX AND STOCKS ARE PRESENTED SEPARATELY IN EVERY TABLE.** Index nets are 100 shares ×
  index points — point-scaled cash-equivalents, NOT portfolio rupees and NOT comparable
  rupee-for-rupee with stock nets. A combined total is shown only for reconciliation,
  at the end of each month section and in the cumulative table. Judge stocks progression
  on the stocks-only column, and index progression on the index column.
- "Win rate" = targets ÷ trades (square-offs are not counted as wins).
- Capped-v2 = separate caps, NOT combined: max 3 index trades/week AND max 3 stock trades/week,
  max 1/symbol/week, per series. Ranking (signal-time only): conviction
  (setup4 > setup3 > setup2 > skill OR), then bias-strong, then room ratio, then prospective
  net target. Filter: prospective net target ≥ ₹500 (net of ₹40 cost).
  Note: with only NIFTY and BANKNIFTY, the index leg can reach at most 2/week under
  1/symbol/week — the intended 3/week is not attainable without a second trade in the
  same index in a week. Observed index leg: V4 0.8–1.8/week, Skill 0.6–1.75/week.

## January 2026 — 20 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 100 | 31.0% | 10 / 20.0% / −₹4,915 | 90 / 32.2% / +₹3,907 |
| Skill filtered raw* | 106 | 20.8% | 11 / 27.3% / +₹2,340 | 95 / 20.0% / −₹5,335 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 452. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 452-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 18 | 27.8% | 6 / 33.3% / +₹9,650 | 12 / 25.0% / +₹645 | ₹4,460 |
| Skill capped-v2 | 22 | 36.4% | 7 / 42.9% / +₹12,890 | 15 / 33.3% / +₹1,010 | ₹4,685 |
| Unified capped-v2 | 22 | 27.3% | 7 / 28.6% / +₹6,625 | 15 / 26.7% / −₹355 | ₹4,113 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹1,008, raw Skill −₹2,995, capped-v2 V4 +₹10,295, Skill +₹13,900, Unified +₹6,270.

## February 2026 — 21 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 93 | 34.4% | 10 / 30.0% / −₹38,545 | 83 / 34.9% / −₹7,400 |
| Skill filtered raw* | 103 | 29.1% | 7 / 42.9% / −₹5,655 | 96 / 28.1% / −₹6,102 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 447. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 447-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 18 | 16.7% | 6 / 16.7% / −₹23,290 | 12 / 16.7% / −₹2,085 | ₹4,409 |
| Skill capped-v2 | 19 | 21.1% | 4 / 25.0% / −₹5,755 | 15 / 20.0% / −₹875 | ₹2,945 |
| Unified capped-v2 | 21 | 14.3% | 6 / 16.7% / −₹23,290 | 15 / 13.3% / −₹5,365 | ₹4,074 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹45,945, raw Skill −₹11,757, capped-v2 V4 −₹25,375, Skill −₹6,630, Unified −₹28,655.

## March 2026 — 19 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 81 | 38.3% | 6 / 83.3% / +₹77,625 | 75 / 34.7% / −₹1,920 |
| Skill filtered raw* | 118 | 41.5% | 9 / 88.9% / +₹107,730 | 109 / 37.6% / −₹6,780 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 418. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 418-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 16 | 56.2% | 6 / 83.3% / +₹77,625 | 10 / 40.0% / +₹530 | ₹5,717 |
| Skill capped-v2 | 22 | 45.5% | 7 / 85.7% / +₹77,640 | 15 / 26.7% / −₹6,995 | ₹6,013 |
| Unified capped-v2 | 24 | 45.8% | 9 / 77.8% / +₹99,805 | 15 / 26.7% / −₹4,535 | ₹6,442 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 +₹75,705, raw Skill +₹100,950, capped-v2 V4 +₹78,155, Skill +₹70,645, Unified +₹95,270.

## April 2026 — 20 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 105 | 30.5% | 6 / 50.0% / +₹9,955 | 99 / 29.3% / −₹11,651 |
| Skill filtered raw* | 96 | 29.2% | 9 / 33.3% / +₹625 | 87 / 28.7% / −₹10,965 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 393. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 393-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 21 | 23.8% | 6 / 50.0% / +₹9,955 | 15 / 13.3% / −₹6,435 | ₹6,432 |
| Skill capped-v2 | 23 | 21.7% | 8 / 37.5% / +₹7,805 | 15 / 13.3% / +₹4,355 | ₹5,503 |
| Unified capped-v2 | 24 | 25.0% | 9 / 44.4% / +₹8,690 | 15 / 13.3% / −₹6,435 | ₹6,628 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹1,696, raw Skill −₹10,340, capped-v2 V4 +₹3,520, Skill +₹12,160, Unified +₹2,255.

## May 2026 — 19 days, 4 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 91 | 25.3% | 10 / 30.0% / −₹23,650 | 81 / 24.7% / −₹5,335 |
| Skill filtered raw* | 97 | 29.9% | 11 / 27.3% / −₹31,270 | 86 / 30.2% / +₹3,939 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 398. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 398-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 18 | 27.8% | 6 / 50.0% / +₹5,460 | 12 / 16.7% / +₹1,980 | ₹5,371 |
| Skill capped-v2 | 17 | 29.4% | 7 / 28.6% / −₹27,015 | 10 / 30.0% / +₹2,330 | ₹7,161 |
| Unified capped-v2 | 19 | 26.3% | 7 / 42.9% / −₹7,415 | 12 / 16.7% / +₹1,980 | ₹6,437 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹28,985, raw Skill −₹27,331, capped-v2 V4 +₹7,440, Skill −₹24,685, Unified −₹5,435.

## June 2026 — 21 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 104 | 30.8% | 6 / 0.0% / −₹41,720 | 98 / 32.7% / −₹6,676 |
| Skill filtered raw* | 111 | 28.8% | 4 / 0.0% / −₹26,910 | 107 / 29.9% / −₹14,916 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 448. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 448-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 20 | 10.0% | 5 / 0.0% / −₹39,000 | 15 / 13.3% / −₹4,435 | ₹4,546 |
| Skill capped-v2 | 18 | 11.1% | 3 / 0.0% / −₹24,190 | 15 / 13.3% / −₹7,715 | ₹4,160 |
| Unified capped-v2 | 21 | 9.5% | 6 / 0.0% / −₹42,805 | 15 / 13.3% / −₹4,435 | ₹4,686 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹48,396, raw Skill −₹41,826, capped-v2 V4 −₹43,435, Skill −₹31,905, Unified −₹47,240.

## July 2026 — 23 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 120 | 31.7% | 11 / 36.4% / −₹8,590 | 109 / 31.2% / +₹859 |
| Skill filtered raw* | 112 | 24.1% | 10 / 40.0% / +₹1,050 | 102 / 22.5% / −₹7,400 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 481. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 481-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 23 | 26.1% | 9 / 33.3% / −₹7,140 | 14 / 21.4% / −₹3,230 | ₹4,696 |
| Skill capped-v2 | 20 | 30.0% | 7 / 42.9% / +₹8,010 | 13 / 23.1% / −₹210 | ₹5,360 |
| Unified capped-v2 | 23 | 26.1% | 9 / 33.3% / −₹7,140 | 14 / 21.4% / −₹3,230 | ₹4,696 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹7,731, raw Skill −₹6,350, capped-v2 V4 −₹10,370, Skill +₹7,800, Unified −₹10,370.

## August 2026 — 21 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 110 | 34.5% | 16 / 37.5% / −₹35,920 | 94 / 34.0% / −₹6,239 |
| Skill filtered raw* | 128 | 26.6% | 13 / 38.5% / −₹33,095 | 115 / 25.2% / −₹5,974 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 454. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 454-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 20 | 25.0% | 7 / 28.6% / −₹26,705 | 13 / 23.1% / −₹1,440 | ₹4,818 |
| Skill capped-v2 | 22 | 18.2% | 7 / 28.6% / −₹26,705 | 15 / 13.3% / −₹4,435 | ₹4,837 |
| Unified capped-v2 | 22 | 22.7% | 7 / 28.6% / −₹26,705 | 15 / 20.0% / −₹1,590 | ₹4,483 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹42,159, raw Skill −₹39,069, capped-v2 V4 −₹28,145, Skill −₹31,140, Unified −₹28,295.

## September 2026 — 21 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 119 | 26.9% | 8 / 37.5% / −₹160 | 111 / 26.1% / −₹2,985 |
| Skill filtered raw* | 133 | 32.3% | 11 / 45.5% / +₹15,405 | 122 / 31.1% / −₹5,779 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 455. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 455-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 18 | 44.4% | 4 / 75.0% / +₹10,390 | 14 / 35.7% / +₹2,290 | ₹2,323 |
| Skill capped-v2 | 20 | 35.0% | 5 / 60.0% / +₹950 | 15 / 26.7% / −₹6,930 | ₹3,756 |
| Unified capped-v2 | 20 | 40.0% | 5 / 60.0% / +₹4,790 | 15 / 33.3% / −₹540 | ₹2,922 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 −₹3,145, raw Skill +₹9,626, capped-v2 V4 +₹12,680, Skill −₹5,980, Unified +₹4,250.

## October 2026 — 18 days, 5 ISO weeks

### Raw — uncapped, one trade/instrument/day

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 103 | 36.9% | 9 / 66.7% / +₹70,415 | 94 / 34.0% / −₹7,984 |
| Skill filtered raw* | 106 | 36.8% | 3 / 66.7% / +₹16,610 | 103 / 35.9% / −₹244 |

* Skill raw net is the V4-style filtered pool (bias alignment, room ≥ 200×scale, PD bound).
  Skill OR signals before those filters: 393. Their unfiltered net is NOT claimed —
  the engine filters before computing an outcome, so inventing a 393-trade net would be fabrication.

### Capped-v2 — 3 index/week + 3 stock/week, convicted + high-return only

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net | Avg prospective target net |
|---|---|---|---|---|---|
| V4 capped-v2 | 22 | 40.9% | 7 / 71.4% / +₹51,825 | 15 / 26.7% / −₹5,255 | ₹4,872 |
| Skill capped-v2 | 18 | 33.3% | 3 / 66.7% / +₹16,610 | 15 / 26.7% / −₹2,370 | ₹3,692 |
| Unified capped-v2 | 22 | 40.9% | 7 / 71.4% / +₹51,825 | 15 / 26.7% / −₹5,255 | ₹4,872 |

Combined totals for reconciliation only (NOT a portfolio result): raw V4 +₹62,431, raw Skill +₹16,366, capped-v2 V4 +₹46,570, Skill +₹14,240, Unified +₹46,570.

## Cumulative — January to October 2026 (203 days)

### Capped-v2 cumulative

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 capped-v2 | 194 | 29.4% | 62 / 43.5% / +₹68,770 | 132 / 22.7% / −₹17,435 |
| Skill capped-v2 | 201 | 28.4% | 58 / 43.1% / +₹40,240 | 143 / 22.4% / −₹21,835 |
| Unified capped-v2 | 218 | 28.0% | 72 / 41.7% / +₹64,380 | 146 / 21.2% / −₹29,760 |

Combined capped-v2 totals for reconciliation only: V4 +₹51,335, Skill +₹18,405, Unified +₹34,620.
Those positives are entirely index-driven — see the split above.

### Raw cumulative

| Series | Trades | Win | Index trades / win / net | Stocks trades / win / net |
|---|---|---|---|---|
| V4 raw | 1026 | 31.9% | 92 / 38.0% / +₹4,495 | 934 / 31.3% / −₹45,424 |
| Skill filtered raw | 1110 | 30.0% | 88 / 40.9% / +₹46,830 | 1022 / 29.1% / −₹59,556 |

Combined raw totals for reconciliation only: V4 −₹40,929, Skill filtered −₹12,726.

## Verdict — January to October 2026

- **Stocks-only: NO progression.** Capped-v2 stocks are negative for every series over Jan–Oct 2026:
  V4 −₹17,435 (132 trades, 22.7% win), Skill −₹21,835 (143 trades, 22.4% win),
  Unified −₹29,760 (146 trades, 21.2% win). Raw stocks are worse: V4 −₹45,424, Skill filtered −₹59,556.
  Stocks were positive in only scattered capped months (V4: Jan, Mar, May, Sep; Skill: Jan, Apr, May).
  The only consecutive positive pair is Skill in Apr–May, and it does not continue into June —
  no sustained month-by-month profit progression on stocks.
- **Index separately: NO stable progression either.** Capped-v2 index is positive in total
  (V4 +₹68,770, Skill +₹40,240, Unified +₹64,380) but it is one month, March 2026, that does it:
  March index alone is +₹77,625 (V4) / +₹77,640 (Skill) / +₹99,805 (Unified). Without March,
  capped-v2 index is negative for V4 and Skill. Other months swing from +₹51,825 (Oct V4) to
  −₹39,000 (Jun V4) on single Bank Nifty/Nifty stops and targets. That is volatility, not progression.
- **Frequency:** capped-v2 passes on count (17–24 trades/month, 3.2–4.6/week per series,
  never 500+). Raw does not (81–133 trades/month per series).
- **No V5 / new version adopted on Jan–Oct 2026.** One partial month (October, 18 days) and one
  outlier month (March, index) do not validate a version. Previous best kept, paper only.
  A candidate must progress on stocks-only net AND on index net separately, on unseen months,
  before adoption — not on a combined total that hides a negative stocks leg.

Sources: `data/progressive/capped_v2_summary_2026-01.json` through `capped_v2_summary_2026-10.json`;
standalone reports `may_2026_v4_and_skill.md` and `october_2026_v4_and_skill.md` (reused for May and October).