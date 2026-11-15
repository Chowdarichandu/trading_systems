# TRIO — DATE-WISE RESULTS · JANUARY 2025 / JANUARY 2026 TO 2026-11-13

Owner's order 2026-11-14 15:40. One strategy, one name: **TRIO** — the three repaired lines that run
from Mon 2026-11-16, reported separately per segment, never pooled. Paper only, real money ₹0.
Full date-wise table: `trio_daily_results_2026-11-14.csv` (463 rows).

## The strategy (what actually runs)
- **Bank line:** TUNED STACK v2 + B-FIX-1 (skip PE legs on down-gap days with entry premium ₹500–800). Per 1 lot (30).
- **Nifty line:** TUNED v1 + N-FIX-1 (skip CE legs on gap-up days). Per 1 lot (65).
- **Stocks line:** the RAW Stock Book (adopted Variant C stack) — its repair candidates S-FIX-1/2 both
  FAILED their gates, so the raw book is the strategy's stocks line. **Equity cash intraday, per
  100 shares PROVISIONAL, ₹40/trade** — provisional wherever shown.

## Coverage
- Bank / Nifty lines: 214 trading days, 2026-01-01 – 2026-11-13 (205 days Jan–Oct + 9 in November).
- Stocks line: 249 trading days in 2025 (Jan–Oct adopted window shown with trades; Nov–Dec 2025
  calendar rows carry 0 trades — see note) and the same 2026 calendar as the index lines.
- In the CSV, a blank cell means that segment was not trading / not in window on that date
  (all of 2025 for the two index lines); 0.00 / 0 means the segment traded that day and took no trade.

## Verification record (every check exact, run before this file was written)
- Bank repaired month sums tie to `bank_three_lines_monthly_2026-11-14.md` REPAIRED column for all
  11 months (Jan–Oct +₹131,510.00; Nov −₹3,440.00; trades 94 + 2).
- Nifty repaired month sums tie to `nifty_three_lines_monthly_2026-11-14.md` REPAIRED column for all
  11 months (Jan–Oct +₹117,170.00; Nov ₹0.00; trades 66 + 0).
- Stocks raw month sums tie to `stocks_three_lines_monthly_2026-11-14.md` RAW column for all
  21 months (2025 Jan–Oct +₹119,813.44 / 1,064 trades; 2026 Jan–Oct +₹247,178.79 / 1,363 trades;
  Nov 2026 +₹7,517.94 / 32 trades).
- The 2025 stocks store's 44 Nov–Dec 2025 legs (+₹1,951.39) sit outside the adopted Jan–Oct window
  and are excluded from the line, exactly as in the three-lines table; those calendar rows show 0 / 0.
- Sources: `november_books_fix_repair_bank_legs.csv`, `november_books_fix_repair_nifty_legs.csv`
  (Jan–Oct legs, per-leg repaired net), `november_repaired_bfix1_bank_log.csv`,
  `november_repaired_nfix1_nifty_log.csv` (November), `stocks_engine_adoptedC_book2025_trades.csv`,
  `stocks_engine_adoptedC_book2026_trades.csv`, `stocks_sarvaritu_paper_log.csv` (November stocks).
  Calendars: `round5_greenday_book_days.csv` (index day universe), NSE daily bars
  (`volrix/nifty_daily_2019_2026.csv`) unioned with the stores' own trade dates (stocks).

## Month subtotals per line

### Bank line — TUNED STACK v2 + B-FIX-1 (repaired)

| Month | Net (Rs) | Trades |
|---|---:|---:|
| 2026-01 | +24,028.00 | 8 |
| 2026-02 | +17,122.00 | 8 |
| 2026-03 | +7,800.00 | 15 |
| 2026-04 | +9,810.00 | 12 |
| 2026-05 | +27,120.00 | 9 |
| 2026-06 | +3,040.00 | 8 |
| 2026-07 | +5,184.00 | 15 |
| 2026-08 | +2,566.50 | 3 |
| 2026-09 | +16,470.00 | 9 |
| 2026-10 | +18,369.50 | 7 |
| 2026-11 | -3,440.00 | 2 |
| **Total** | **+128,070.00** | **96** |

### Nifty line — TUNED v1 + N-FIX-1 (repaired)

| Month | Net (Rs) | Trades |
|---|---:|---:|
| 2026-01 | +15,531.25 | 6 |
| 2026-02 | +12,699.25 | 8 |
| 2026-03 | +5,723.50 | 10 |
| 2026-04 | +27,881.25 | 6 |
| 2026-05 | +6,888.25 | 8 |
| 2026-06 | +4,828.00 | 5 |
| 2026-07 | +12,814.00 | 9 |
| 2026-08 | +1,911.75 | 4 |
| 2026-09 | +13,367.75 | 7 |
| 2026-10 | +15,525.00 | 3 |
| 2026-11 | +0.00 | 0 |
| **Total** | **+117,170.00** | **66** |

### Stocks line — raw Stock Book, 2025 (Jan–Oct adopted window)

| Month | Net (Rs) | Trades |
|---|---:|---:|
| 2025-01 | +4,476.90 | 262 |
| 2025-02 | +25,913.57 | 257 |
| 2025-03 | +8,412.63 | 160 |
| 2025-04 | +53,220.39 | 134 |
| 2025-05 | +6,518.38 | 51 |
| 2025-06 | +1,802.59 | 14 |
| 2025-07 | -660.91 | 41 |
| 2025-08 | +13,486.06 | 72 |
| 2025-09 | +10,686.50 | 52 |
| 2025-10 | -4,042.67 | 21 |
| **Total** | **+119,813.44** | **1064** |

### Stocks line — raw Stock Book, 2026

| Month | Net (Rs) | Trades |
|---|---:|---:|
| 2026-01 | +28,021.10 | 118 |
| 2026-02 | +12,576.14 | 158 |
| 2026-03 | +18,225.72 | 336 |
| 2026-04 | +46,744.31 | 177 |
| 2026-05 | +43,842.74 | 131 |
| 2026-06 | +6,756.75 | 111 |
| 2026-07 | +10,284.46 | 30 |
| 2026-08 | +10,106.06 | 39 |
| 2026-09 | +14,494.14 | 111 |
| 2026-10 | +56,127.37 | 152 |
| 2026-11 | +7,517.94 | 32 |
| **Total** | **+254,696.73** | **1395** |
