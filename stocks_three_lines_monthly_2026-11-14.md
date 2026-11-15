# STOCK BOOK — THREE LINES, MONTH-ON-MONTH (Jan 2025 – Nov 2026)

**Owner order (2026-11-14 12:08 IST): the three lines, per segment.**
Paper only, real money ₹0. **Every figure: equity cash intraday, per
100 shares PROVISIONAL, ₹40/trade.** Years judged separately — the
subtotals are the verdict rows; the grand total is arithmetic only.

- **RAW** — the Stock Book as it stands (adopted Variant C stack).
- **+ REPAIR** — RAW + S-FIX-1 (skip INV-ABOVE legs entered ≤09:35),
  the repair candidate built in `stocks_repair_2026-11-14.md` —
  **FAILED its gate** (placebo leg: beats 91.0% of random skip-sets,
  bar 95%). Shown because the owner wants the comparison visible;
  NOT adopted. It is the better of the two frozen candidates by
  pooled improvement (+₹1,527.37 vs S-FIX-2's +₹1,345.89, also FAILED).
- **+ CONFIDENCE** — RAW kept by the Phase-2 confidence filter at
  T70, from `phase2_confidence_stocks_2026-11-14.md`'s frozen spec —
  **FAILED its gate** (win rate never rises at any cut, either year).
  NOT adopted.

Anchors tied exactly: RAW Jan–Oct 2025 +₹119,813.44 · 2026
+₹247,178.79 · November +₹7,517.94 · CONFIDENCE T70 kept +₹81,309.57
(2025) / +₹190,757.68 (2026).

| Month | RAW — Stock Book | + REPAIR (S-FIX-1, FAILED) | + CONFIDENCE T70 (FAILED) | Winner |
|---|---:|---:|---:|---|
| Jan 2025 | +4,476.90 | +4,718.64 | -2,238.24 | Repair |
| Feb 2025 | +25,913.57 | +25,913.57 | +16,567.95 | Raw / Repair |
| Mar 2025 | +8,412.63 | +9,812.63 | +5,509.78 | Repair |
| Apr 2025 | +53,220.39 | +48,525.55 | +47,866.40 | Raw |
| May 2025 | +6,518.38 | +10,971.19 | +6,518.38 | Repair |
| Jun 2025 | +1,802.59 | +2,043.10 | +1,802.59 | Repair |
| Jul 2025 | -660.91 | +1,180.21 | -8,109.00 | Repair |
| Aug 2025 | +13,486.06 | +13,486.06 | +13,809.57 | Confidence |
| Sep 2025 | +10,686.50 | +10,975.23 | +5,297.46 | Repair |
| Oct 2025 | -4,042.67 | -3,712.71 | -5,715.32 | Repair |
| **Subtotal 2025 (Jan–Oct)** | **+119,813.44** | **+123,913.47** | **+81,309.57** | Repair |
| Jan 2026 | +28,021.10 | +27,428.44 | +17,942.67 | Raw |
| Feb 2026 | +12,576.14 | +12,576.14 | +16,989.21 | Confidence |
| Mar 2026 | +18,225.72 | +18,225.72 | +17,332.68 | Raw / Repair |
| Apr 2026 | +46,744.31 | +46,744.31 | +34,654.49 | Raw / Repair |
| May 2026 | +43,842.74 | +41,862.74 | +26,296.82 | Raw |
| Jun 2026 | +6,756.75 | +6,756.75 | +7,929.76 | Confidence |
| Jul 2026 | +10,284.46 | +10,284.46 | +13,936.53 | Confidence |
| Aug 2026 | +10,106.06 | +10,106.06 | +10,983.35 | Confidence |
| Sep 2026 | +14,494.14 | +14,494.14 | +4,581.97 | Raw / Repair |
| Oct 2026 | +56,127.37 | +56,127.37 | +40,110.20 | Raw / Repair |
| **Subtotal 2026 (Jan–Oct)** | **+247,178.79** | **+244,606.13** | **+190,757.68** | Raw |
| Nov 2026 (to 13th) | +7,517.94 | +5,028.26 | +6,794.44 | Raw |
| **TOTAL Jan 2025 – Nov 2026** | **+374,510.17** | **+373,547.86** | **+278,861.69** | Raw |
| Legs taken | 2,459 | 2,421 | 1,730 | — |

Notes:
- Oct 2025 was red on all three lines; "Winner" there is the
  least-red line. Jul 2025 the repair line is the only green one —
  the skip happens to clear that month's small loss, which is part
  of why it wins 2025's subtotal yet still fails the placebo.
- November CONFIDENCE figure is on the UNSCORED-kept basis from the
  frozen confidence run: only Nov 2's 4 trades were scorable (the
  volume store ends 2026-10-30); T70 idled +₹723.50 that day and the
  other 28 trades are carried unjudged. The UNSCORED-excluded
  variant is ₹731.77 — not a tradable figure, recorded in the
  confidence report. November legs for the confidence line (1,730
  total) count those 28 as kept, on the same basis.
- November REPAIR figure: S-FIX-1 skips 4 November trades netting
  +₹2,489.68 (three winners incl. GLENMARK +₹3,068.25, one loser
  −₹1,369.00) → +₹5,028.26. Descriptive only; November sets no rule.
- The 2025 store carries 44 Nov–Dec 2025 legs (+₹1,951.39) outside
  the adopted Jan–Oct window; they are excluded from all three
  lines, exactly as in the control and the confidence run.
- The story in the table: the repair line wins 2025 and loses 2026
  and November — a one-year, sub-placebo effect. The confidence
  line wins a few mid-2026 months and loses both years outright.
  RAW wins 2026, November, and the grand total. **No line but RAW
  is adopted; the Stock Book stands unchanged.**
