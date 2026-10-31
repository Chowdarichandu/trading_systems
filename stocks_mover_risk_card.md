# Morning-Mover — Flagship Risk Card + Regime Diagnostic (Tuning Loop Line 6)

*Analysis only, computed from the existing trade dumps (`mover_A_old_trades.csv`, `mover_A_ext_trades.csv`, `mover_M1_poolB_trades.csv`). No new rules, no pass claims, nothing adopted or changed. Equity cash intraday, paper only, real money ₹0. All figures provisional per 100 shares, ₹40/trade cost already deducted. Window Jan–Oct 2026 (October = 1–28 Oct, 18 trading days).*

*Definitions: a **chain** = one stock-day's trades (direct leg + optional round-2 leg). Daily stats aggregate every trade closing that day, over days the book actually traded ("active days"). Max drawdown is peak-to-trough on the daily cumulative net curve, starting from 0.*

---

## Risk Card 1 — MOVER-A pooled 50 (10:00 measurement, 25 home + 25 ext stocks)

- Trades 998 · Chains 623 · Active days 174 · **Final net +₹249,155.03**
- **Max drawdown: −₹33,440.10 (−13.4% of final net)**
- Worst single day: **2026-05-15, −₹16,073.80** · Best single day: 2026-03-13, +₹33,220.59
- Longest losing-day streak: **5 days** · Longest losing-chain streak: **7 chains**
- Days positive: **61.5%** of active days
- Worst calendar month: **2026-01, −₹9,886.28** (only three negative months: Jan −₹9,886.28, Feb −₹190.30, May −₹2,312.51)
- Worst single chain: 2026-07-01 MARUTI, −₹14,436.00
- Full double-stop chains (both legs stopped): **118 of 623 chains = 18.9%** (31.5% of the 375 two-leg chains); those chains together lost −₹169,420.99

**Top-5 worst days**

| Date | Daily net (₹) |
|---|---|
| 2026-05-15 | −16,073.80 |
| 2026-05-14 | −12,274.26 |
| 2026-07-01 | −8,917.30 |
| 2026-01-22 | −8,543.90 |
| 2026-02-27 | −7,110.85 |

Monthly net (₹): Jan −9,886.28 · Feb −190.30 · Mar +67,883.49 · Apr +70,532.34 · May −2,312.51 · Jun +38,821.76 · Jul +3,442.52 · Aug +1,071.97 · Sep +22,982.07 · Oct +56,809.97

---

## Risk Card 2 — MOVER-B pooled 50 (10:15 measurement, 25 home + 25 ext stocks)

- Trades 1,422 · Chains 917 · Active days 192 · **Final net +₹464,617.03**
- **Max drawdown: −₹17,471.45 (−3.8% of final net)**
- Worst single day: **2026-07-01, −₹11,674.75** · Best single day: 2026-10-21, +₹66,768.34
- Longest losing-day streak: **5 days** · Longest losing-chain streak: **10 chains**
- Days positive: **66.1%** of active days
- Worst calendar month: **2026-07, +₹9,747.90 — B had no negative month at all** in Jan–Oct pooled
- Worst single chain: 2026-07-01 MARUTI, −₹14,436.00 (same chain as in the A books)
- Full double-stop chains: **120 of 917 chains = 13.1%** (23.8% of the 505 two-leg chains); those chains together lost −₹182,332.70

**Top-5 worst days**

| Date | Daily net (₹) |
|---|---|
| 2026-07-01 | −11,674.75 |
| 2026-05-14 | −9,843.46 |
| 2026-02-27 | −7,110.85 |
| 2026-03-17 | −4,617.16 |
| 2026-06-25 | −4,557.29 |

Monthly net (₹): Jan +20,654.74 · Feb +18,593.73 · Mar +113,901.46 · Apr +56,999.06 · May +33,657.98 · Jun +49,709.85 · Jul +9,747.90 · Aug +12,887.79 · Sep +29,715.98 · Oct +118,748.54

---

## Risk Card 3 — MOVER-A ext 25 (10:00 measurement, new large-cap universe only)

- Trades 300 · Chains 199 · Active days 116 · **Final net +₹164,483.29**
- **Max drawdown: −₹30,370.73 (−18.5% of final net)**
- Worst single day: **2026-05-15, −₹13,835.30** · Best single day: 2026-04-08, +₹22,179.62
- Longest losing-day streak: **6 days** · Longest losing-chain streak: **4 chains**
- Days positive: **59.5%** of active days
- Worst calendar month: **2026-01, −₹9,669.81** (five negative months: Jan, Feb, May, Jul, Aug — all small vs the Mar/Apr/Jun/Sep/Oct gains)
- Worst single chain: 2026-07-01 MARUTI, −₹14,436.00
- Full double-stop chains: **25 of 199 chains = 12.6%** (24.8% of the 101 two-leg chains); those chains together lost −₹90,886.02

**Top-5 worst days**

| Date | Daily net (₹) |
|---|---|
| 2026-05-15 | −13,835.30 |
| 2026-05-14 | −9,160.80 |
| 2026-07-01 | −8,196.00 |
| 2026-01-22 | −7,357.25 |
| 2026-02-27 | −6,382.50 |

Monthly net (₹): Jan −9,669.81 · Feb −3,976.94 · Mar +47,228.62 · Apr +44,814.28 · May −5,253.60 · Jun +31,111.12 · Jul −3,956.71 · Aug −1,052.37 · Sep +25,254.15 · Oct +39,984.55

---

## Regime Split — MOVER-A pooled chains by Nifty trend (diagnostic only)

Split by the INV-work definition: **MET** = Nifty previous close ≤ its 50DMA on the chain's date; **NOT-MET** = previous close above the 50DMA. Nifty daily series: `volrix/nifty_daily_2019_2026.csv`. All 623 chains classified.

| Bucket | Chains | Net (₹) | Expectancy / chain (₹) |
|---|---|---|---|
| MET (Nifty ≤ 50DMA) | 475 | +225,534.92 | +474.81 |
| NOT-MET (Nifty > 50DMA) | 148 | +23,620.11 | +159.60 |

*Interpretation (one line, no gate proposed): the mover's edge is present in both regimes but is roughly three times stronger per chain on below-trend Nifty days, which also supplied about three-quarters of all chains.*

---

## Size Translation Table — ACCOUNTING ONLY

*The Jan–Oct nets of the pooled books restated at larger share counts. Arithmetic only: gross P&L scales linearly with shares while the ₹40/trade cost is held flat at every size, exactly as briefed. Real broker charges may not stay flat as size grows, so treat this as a translation of the paper numbers — **not a recommendation to trade any size**. Paper only, real money ₹0.*

| Book | 100 sh (as scored) | 200 sh | 500 sh | 1,000 sh |
|---|---|---|---|---|
| MOVER-A pooled 50 (998 trades) | +₹249,155.03 | +₹538,230.06 | +₹1,405,455.15 | +₹2,850,830.30 |
| MOVER-B pooled 50 (1,422 trades) | +₹464,617.03 | +₹986,114.06 | +₹2,550,605.15 | +₹5,158,090.30 |

(At 100 shares: A pooled gross +₹289,075.03 − ₹39,920 costs; B pooled gross +₹521,497.03 − ₹56,880 costs.)

---

*Engine: `stocks_mover_risk_card.py`; machine-readable results: `stocks_mover_risk_card.json`. Reminder: November judges frozen variants A (10:00) vs B (10:15) on fresh data on both universes — this card changes no rule and makes no fresh-window claim.*
