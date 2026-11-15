# NIFTY — THREE LINES, MONTH-ON-MONTH · JAN–NOV 2026 (Nov to the 13th)

Owner's order 2026-11-14 12:08 (mirrors the Bank three-lines table). Nifty, TUNED v1 family, 1 lot (65), paper only, real money ₹0.
Read-only computation — no book, ledger, or job changed.

**The three lines**
1. **RAW** — TUNED v1 (EVE-07) as it stands.
2. **REPAIRED** — v1 + N-FIX-1 (skip CE legs on gap-up days) — the repaired lead from Mon 2026-11-16.
3. **CONFIDENCE** — v1 legs kept by the Phase-2 composite confidence score at its lightest tested cut (T70, keep top 70%). **This filter FAILED its gate on Nifty (verdict FAIL in `phase2_tuning_nifty_2026-11-14.md`) — it is shown for comparison only and is NOT adopted or running.**

| Month | RAW — TUNED v1 | REPAIRED — + N-FIX-1 | CONFIDENCE — T70 (FAILED filter) | Winner |
|---|---|---|---|---|
| Jan | **+15,531.25** | **+15,531.25** | +14,153.50 | Raw / Repaired (tie) |
| Feb | +9,229.25 | **+12,699.25** | +4,582.00 | Repaired |
| Mar | −1,216.50 | **+5,723.50** | +955.00 | Repaired |
| Apr | +24,411.25 | **+27,881.25** | −3,260.00 | Repaired |
| May | +4,364.00 | **+6,888.25** | +4,364.00 | Repaired |
| Jun | **+4,828.00** | **+4,828.00** | −2,681.50 | Raw / Repaired (tie) |
| Jul | +10,463.00 | +12,814.00 | **+15,670.75** | Confidence |
| Aug | **+1,911.75** | **+1,911.75** | **+1,911.75** | All three (tie) |
| Sep | **+13,367.75** | **+13,367.75** | +9,687.75 | Raw / Repaired (tie) |
| Oct | **+20,160.50** | +15,525.00 | +16,480.50 | Raw |
| **Subtotal Jan–Oct** | **+103,050.25** | **+117,170.00** | **+61,863.75** | Repaired |
| Nov (to 13th) | **+3,036.50** | 0.00 | **+3,036.50** | Raw / Confidence (tie) |
| **TOTAL Jan–Nov** | **+106,086.75** | **+117,170.00** | **+64,900.25** | Repaired |
| Legs taken, Jan–Nov | 75 (74 + 1) | 66 (66 + 0) | 53 (52 + 1) | — |

**Anchor verification (all six exact, checked before this table was built)**
- Jan–Oct: RAW +₹103,050.25 ✓ · REPAIRED +₹117,170.00 ✓ · CONFIDENCE T70 +₹61,863.75 ✓
- November (Nov 2–13): RAW +₹3,036.50 ✓ · REPAIRED ₹0.00 ✓ · CONFIDENCE +₹3,036.50 ✓
- The RAW month column was computed from two independent stores (the books-fix repair-legs file and the Phase-2 control month table) — identical month by month.

**Sources**
- Jan–Oct RAW + REPAIRED: `november_books_fix_repair_nifty_legs.csv` (74 legs, per-leg raw net and repaired net; 8 legs stood down by N-FIX-1).
- Jan–Oct CONFIDENCE: `phase2_tuning_nifty_results.json`, threshold T70 month table (52 legs kept, cut score 0.725) — matches the published table in `phase2_tuning_nifty_2026-11-14.md`.
- November: v1's actual November record — 1 leg, Nov 3 CE 23600 weekly +₹3,036.50. N-FIX-1 stands that leg down (CE on a +0.6034% gap-up day) → REPAIRED ₹0. The confidence score rates that leg 0.8697, above every cut → CONFIDENCE keeps it at T70 (and at T60/T50).

**Confidence footnotes (the filter FAILED its gate on Nifty — comparison only)**
- T70 Jan–Oct: +₹61,863.75 (52 legs, WR 50.0%, placebo 24th percentile) — FAIL.
- T60 Jan–Oct: +₹56,594.00 (44 legs, WR 52.3%) — FAIL. T50 Jan–Oct: +₹44,523.00 (37 legs, WR 48.6%) — FAIL.
- The score anti-selects on this book: on the year it idles v1's real earners (the gap-fade family profits trading against the gap at expensive premiums, which the score marks down). November's single leg happening to be kept does not change the verdict — one leg sets no rule.

**Reading notes (facts, not verdicts)**
- Repaired wins or ties 9 of the 11 rows and leads the Jan–Nov total (+₹117,170.00): N-FIX-1's 8 stood-down legs were worth −₹14,119.75 on the year, including turning v1's only red month (Mar −₹1,216.50) into +₹5,723.50.
- The repair is not free: it costs Oct (stands down a +₹4,635.50 winner; Raw takes the month) and it stands down November's only leg — v1's sole November win — so the Repaired November line is ₹0 against Raw's +₹3,036.50.
- Confidence (failed filter) takes only Jul outright; it turns Apr and Jun red and keeps just 60.0% of Raw's Jan–Oct money. Unlike Bank — where the same idea passed its gate — on Nifty the filter destroys value on the year.
- November is 9 trading days; the remaining 10 days (Nov 16–30) are the forward test for the Repaired lead. December adoption is decided at the Nov 30 verdicts.
