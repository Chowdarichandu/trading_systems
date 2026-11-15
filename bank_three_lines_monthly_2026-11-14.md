# BANK NIFTY — THREE LINES, MONTH-ON-MONTH · JAN–NOV 2026 (Nov to the 13th)

Owner's order 2026-11-14 11:54. Bank Nifty, TUNED STACK v2 family, 1 lot, paper only, real money ₹0.
Read-only computation — no book, ledger, or job changed.

**The three lines**
1. **RAW** — TUNED STACK v2 as it stands.
2. **REPAIRED** — stack + B-FIX-1 (skip PE legs on down-gap days with entry premium ₹500–800) — the repaired lead from Mon 2026-11-16.
3. **CONFIDENCE** — stack legs kept by the Phase-2 confidence gate (score ≥ 0.5) — forward shadow from Mon 2026-11-16.

| Month | RAW — stack v2 | REPAIRED — + B-FIX-1 | CONFIDENCE — gate ≥ 0.5 | Winner |
|---|---|---|---|---|
| Jan | **+24,028.00** | **+24,028.00** | +21,513.00 | Raw / Repaired (tie) |
| Feb | +15,284.00 | **+17,122.00** | +15,284.00 | Repaired |
| Mar | +8,560.00 | +7,800.00 | **+8,760.00** | Confidence |
| Apr | **+9,810.00** | **+9,810.00** | +9,050.00 | Raw / Repaired (tie) |
| May | +25,400.00 | **+27,120.00** | +20,440.00 | Repaired |
| Jun | **+3,040.00** | **+3,040.00** | +1,520.00 | Raw / Repaired (tie) |
| Jul | +4,224.00 | +5,184.00 | **+9,525.00** | Confidence |
| Aug | +2,059.50 | **+2,566.50** | +2,059.50 | Repaired |
| Sep | +15,056.50 | +16,470.00 | **+16,776.50** | Confidence |
| Oct | **+19,889.50** | +18,369.50 | +17,409.50 | Raw |
| **Subtotal Jan–Oct** | **+127,351.50** | **+131,510.00** | **+122,337.50** | Repaired |
| Nov (to 13th) | −2,680.00 | −3,440.00 | **+760.00** | Confidence |
| **TOTAL Jan–Nov** | **+124,671.50** | **+128,070.00** | **+123,097.50** | Repaired |
| Legs taken, Jan–Nov | 115 (111 + 4) | 96 (94 + 2) | 90 (88 + 2) | — |

**Anchor verification (all six exact, checked before this table was built)**
- Jan–Oct: RAW +₹127,351.50 ✓ · REPAIRED +₹131,510.00 ✓ · CONFIDENCE +₹122,337.50 ✓
- November (Nov 2–13): RAW −₹2,680.00 ✓ · REPAIRED −₹3,440.00 ✓ · CONFIDENCE +₹760.00 ✓
- The RAW month column was computed from two independent stores (the books-fix repair-legs file and the Phase-2 anatomy/features join) — identical month by month.

**Sources**
- Jan–Oct RAW + REPAIRED: `november_books_fix_repair_bank_legs.csv` (111 legs, per-leg raw net and repaired net; 17 legs stood down by B-FIX-1).
- Jan–Oct CONFIDENCE: `phase2_tuning_bank_results.json`, threshold T70 (= T60 kept set, cut score 0.5, 88 legs) month table — matches the published table in `phase2_tuning_bank_2026-11-14.md`.
- November RAW: `november_shadow_stack_bank_log.csv` (4 legs). REPAIRED: `november_repaired_bfix1_bank_log.csv` (Nov 4 win and Nov 13 loss stood down → 2 legs kept). CONFIDENCE: `november_shadow_confgate_bank_log.csv` (Nov 4 + Nov 13 kept → +₹760.00).

**Reading notes (facts, not verdicts)**
- No line wins every month: Raw/Repaired tie in Jan, Apr and Jun (B-FIX-1 stood nothing down in those months); Raw alone takes Oct; Repaired alone takes Feb, May, Aug; Confidence takes Mar, Jul, Sep — and November.
- The Repaired line leads the Jan–Nov total (+₹128,070.00) on the strength of Jan–Oct; in November itself it is the worst of the three (−₹3,440.00), because B-FIX-1 also stands down November's only win (Nov 4).
- The Confidence line is the only one positive in November (+₹760.00) and the lowest on the Jan–Oct subtotal — it gives up ₹5,014.00 of the raw book's year to buy its cleaner profile (WR 62.5% vs 59.5% on Jan–Oct).
- November is 9 trading days; the remaining 10 days (Nov 16–30) are the forward test for the Repaired lead and the Confidence shadow. December adoption is decided at the Nov 30 verdicts.
