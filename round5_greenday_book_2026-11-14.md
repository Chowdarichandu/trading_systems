# BANK NIFTY — GREEN-DAY BOOK (SPEED TRACK C, 2026-11-14)

**Real money ₹0 — no live trades were placed and nothing is armed.** Every
figure below is paper/backtest arithmetic on stored, already-scored leg
files. Basis: Bank Nifty option premiums per 1 lot (30), cost ₹220/trade
inside every stored net, UNIQUE-ONCE counting. A candidate, if one had
passed, would go to the owner for his Monday decision — none did.

---

## 1. VERDICT — NOT A CANDIDATE (neither book)

**Book P (stack + priority increment D1 > V3 > B1) is NOT the candidate.**
It beats the stack on total (+₹140,844.50 vs +₹127,351.50) and it improves
November's day-count (2 green / 3 red / 4 no-trade vs the stack's
1 / 3 / 5; November total −₹200.00 vs −₹2,680.00) — but it **fails two
pre-registered legs**: its green-day share **of trade-days falls** to
58.7% from the stack's 67.4%, and **July is a red month (−₹176.00)**,
breaking the zero-red-months condition.

**Book D (stack + D1 only) is NOT the candidate either.** It beats the
stack on total (+₹136,324.50), keeps zero red months, and clears the
₹900 bar (₹1,175.21/trade-day) — but its green-day share of trade-days
also **falls** (62.9% vs 67.4%) and its **November day-count does not
improve at all**: D1's only November leg (Nov 12, PE 61300, +₹2,480)
fell on a stack-busy day, so the increment is empty and November is
unchanged at −₹2,680.00, 1 / 3 / 5.

Per the pre-registered rule, that ends it: **no green-day book from this
construction goes forward as the candidate.** The stack alone remains
the book.

## 2. FROZEN CONSTRUCTION — written before the formal scoring run

1. **Base book:** TUNED STACK v2's 111 Jan–Oct 2026 legs, exactly as
   stored in `solid60_programme_2026-11-13_bank_A_stack_features.csv`
   (anchor: +₹127,351.50, 89 trade-days, ₹1,430.92/trade-day).
2. **Increment pool:** the three fragments' legs **on stack-idle days
   only**, from the rounds' own scored leg files, each extracted with
   its round driver's own rule (real mode, Bank Nifty,
   trade_date ≤ 2026-10-31, date not a stack trade-day):
   - D1 — `round4_trades.csv`, family D1 (round 4).
   - V3 — `oi_buildup_trades.csv`, variant V3 (round 1).
   - B1 — `round2_trades.csv`, variant B1 (round 2).
3. **Book P (priority):** stack legs + **at most one increment leg per
   stack-idle day**, chosen by frozen priority **D1 > V3 > B1** among
   the increments signalling that day. Unchosen same-day legs are
   excluded and listed (§4).
4. **Book D:** stack legs + the D1 increment only, identical metrics.
5. **No other combinations. No parameter tuning. November sets no
   rule** — counterfactual check only (Nov 2–13, 9 trading days).
6. **Gate (Jan–Oct, both books):** total, legs, trade-days,
   ₹/trade-day vs ₹900, leg win rate, full month table (no red month),
   halves (H1 = Jan–May, H2 = Jun–Oct), ex-top-3 **days**, independent
   re-sum, and green/red/no-trade day counts with green-day share of
   trade-days and of all 205 days — each vs the stack alone.
7. **Pre-registered verdict rule:** THE CANDIDATE only if a book beats
   the stack on **total** AND **green-day share**, keeps **zero red
   months**, and **improves November's day-count**. Otherwise, plainly
   not.

## 3. HEADLINE COMPARISON — Jan–Oct 2026 (205 trading days)

| Book | Legs | Total | Trade-days | ₹/trade-day | Win rate | Green / Red / No-trade days | Green share of trade-days | Green share of all days | Red months |
|---|---|---|---|---|---|---|---|---|---|
| **STACK v2 (base)** | 111 | **+₹127,351.50** | 89 | ₹1,430.92 | 59.5% | 60 / 29 / 116 | **67.4%** | 29.3% | **0** |
| **Book P (priority)** | 172 | **+₹140,844.50** | 150 | ₹938.96 | 54.7% | 88 / 62 / 55 | 58.7% | **42.9%** | **1 (Jul)** |
| **Book D (stack + D1)** | 138 | **+₹136,324.50** | 116 | ₹1,175.21 | 57.2% | 73 / 43 / 89 | 62.9% | 35.6% | **0** |

Reading the lens honestly: both books add green **days** (60 → 88 and
60 → 73) and lift the green share of **all** days — but they add red
days faster than green on the days they trade (29 → 62 and 29 → 43),
so the green share **of trade-days falls** under both. Book P's
₹938.96/trade-day clears the ₹900 bar by only ₹38.96, and after its
three best days are removed it falls to ₹775.66/trade-day (§5).

## 4. EXTRACTION AND PRIORITY CHOICE — validation

Increment pools after the stack-idle filter (each re-summed
independently from its source file; all anchors exact):

| Increment | Legs (all on distinct stack-idle days) | Total |
|---|---|---|
| D1 | 27 | +₹8,973.00 |
| V3 | 42 | +₹3,360.00 |
| B1 | 12 | +₹4,560.00 |

Extraction was validated against the rounds' own merged figures before
any new book was scored: stack + D1 alone reproduces round 4's
₹136,324.50 / 116 TD; stack + V3 alone reproduces round 1's
₹130,711.50 / 131 TD; stack + B1 alone reproduces round 2's
₹131,911.50 / 101 TD.

The three pools signal on **61 distinct stack-idle days**. The frozen
priority chose: **D1 27 of 27 legs (+₹8,973.00) · V3 29 of 42 legs
(+₹4,720.00) · B1 5 of 12 legs (−₹200.00)** → chosen increment
**61 legs, +₹13,493.00**. The **20 skipped legs total +₹3,400.00** —
the frozen strength priority sometimes takes the weaker leg on the day
(e.g. 2026-02-16: D1 chosen while B1's skipped leg was +₹2,480.00).
That is the cost of a priority frozen in advance; it is reported, not
re-tuned. Full skipped-leg list is in the results JSON.

## 5. GATE DETAIL — halves and ex-top-3 days

| Book | H1 total (₹/TD) | H2 total (₹/TD) | Ex-top-3-days total | Ex-top-3-days ₹/TD |
|---|---|---|---|---|
| STACK | +₹83,082.00 (₹1,888.23) | +₹44,269.50 (₹983.77) | +₹100,528.50 | ₹1,168.94 |
| Book P | +₹89,989.50 (₹1,267.46) | +₹50,855.00 (₹643.73) | +₹114,021.50 | **₹775.66** |
| Book D | +₹86,389.50 (₹1,542.67) | +₹49,935.00 (₹832.25) | +₹109,501.50 | ₹969.04 |

(Top-3 days removed are the same for all three books — the stack's own
2026-01-21 +₹9,680.00, 2026-02-20 +₹9,680.00, 2026-01-20 +₹7,463.00;
increments never land on stack-busy days.) Both candidate books keep
both halves positive and stay positive ex-top-3 days; Book P's
ex-top-3-days average drops **below the ₹900 bar**, one more sign its
edge is thin. Independent re-sum: source files re-read in a second
pass — stack (111, ₹127,351.50), D1 (27, ₹8,973.00), V3 (42,
₹3,360.00), B1 (12, ₹4,560.00) — and the written day-level CSV re-sums
to all three book totals exactly.

## 6. MONTH TABLES — total ₹ (trade-days · green/red/no-trade · ₹/trade-day)

| Month | STACK total | Book P total (TD · G/R/NT · ₹/TD) | Book D total (TD · G/R/NT · ₹/TD) |
|---|---|---|---|
| Jan | +₹24,028.00 | +₹31,735.50 (14 · 11/3/6 · ₹2,266.82) | +₹26,015.50 (10 · 8/2/10 · ₹2,601.55) |
| Feb | +₹15,284.00 | +₹7,444.00 (16 · 6/10/5 · ₹465.25) | +₹12,604.00 (13 · 6/7/8 · ₹969.54) |
| Mar | +₹8,560.00 | +₹7,400.00 (18 · 11/7/1 · ₹411.11) | +₹10,080.00 (14 · 10/4/5 · ₹720.00) |
| Apr | +₹9,810.00 | +₹13,050.00 (12 · 9/3/8 · ₹1,087.50) | +₹12,290.00 (10 · 8/2/10 · ₹1,229.00) |
| May | +₹25,400.00 | +₹30,360.00 (11 · 9/2/8 · ₹2,760.00) | +₹25,400.00 (9 · 7/2/10 · ₹2,822.22) |
| Jun | +₹3,040.00 | +₹7,800.00 (14 · 8/6/7 · ₹557.14) | +₹8,760.00 (11 · 7/4/10 · ₹796.36) |
| Jul | +₹4,224.00 | **−₹176.00 (18 · 6/12/5 · −₹9.78)** | +₹784.00 (15 · 5/10/8 · ₹52.27) |
| Aug | +₹2,059.50 | +₹6,819.50 (12 · 7/5/9 · ₹568.29) | +₹5,299.50 (8 · 5/3/13 · ₹662.44) |
| Sep | +₹15,056.50 | +₹10,042.00 (19 · 8/11/2 · ₹528.53) | +₹13,682.00 (12 · 6/6/9 · ₹1,140.17) |
| Oct | +₹19,889.50 | +₹26,369.50 (16 · 13/3/4 · ₹1,648.09) | +₹21,409.50 (14 · 11/3/6 · ₹1,529.25) |

Book P's single red month is July (−₹176.00): the stack's +₹4,224.00
could not absorb the chosen increments' −₹4,400.00 that month. Book D
has no red month, but July thins to +₹784.00 on 15 trade-days.

## 7. NOVEMBER COUNTERFACTUAL — day by day (Nov 2–13, 9 trading days)

| Date | STACK | Book P increment | Book P day | Book D day |
|---|---|---|---|---|
| Nov 2 | no trade | **V3 +₹2,480.00** | **+₹2,480.00 GREEN** | no trade |
| Nov 3 | no trade | — | no trade | no trade |
| Nov 4 | +₹2,480.00 | — | +₹2,480.00 GREEN | +₹2,480.00 GREEN |
| Nov 5 | no trade | — | no trade | no trade |
| Nov 6 | no trade | — | no trade | no trade |
| Nov 9 | −₹1,720.00 | — | −₹1,720.00 RED | −₹1,720.00 RED |
| Nov 11 | no trade | — | no trade | no trade |
| Nov 12 | −₹1,720.00 | — (D1 leg +₹2,480 on a stack-busy day — excluded) | −₹1,720.00 RED | −₹1,720.00 RED |
| Nov 13 | −₹1,720.00 | — (no increment: V3 no direction, B1 no signal, D1 NC) | −₹1,720.00 RED | −₹1,720.00 RED |
| **Total / count** | **−₹2,680.00 · 1G / 3R / 5NT** |  | **−₹200.00 · 2G / 3R / 4NT** | **−₹2,680.00 · 1G / 3R / 5NT** |

Book P genuinely improves November's day-count and nearly flattens
the month — one added green day (Nov 2) from V3. It still leaves
November with more red days than green, and November was never the
gate: the Jan–Oct red month and the falling trade-day green share
had already decided the verdict.

## 8. CANDIDATE-RULE SCORECARD

| Pre-registered leg | Book P | Book D |
|---|---|---|
| Total beats stack | ✅ +₹140,844.50 | ✅ +₹136,324.50 |
| ₹/trade-day ≥ ₹900 | ✅ ₹938.96 | ✅ ₹1,175.21 |
| Green share of trade-days beats stack (67.4%) | ❌ 58.7% | ❌ 62.9% |
| Green share of all days beats stack (29.3%) | ✅ 42.9% | ✅ 35.6% |
| Zero red months | ❌ Jul −₹176.00 | ✅ |
| November day-count improves | ✅ 2/3/4 vs 1/3/5 | ❌ unchanged |
| **THE CANDIDATE** | **NO** | **NO** |

## FILES

- This report: `round5_greenday_book_2026-11-14.md`
- Results (all metrics, chosen/skipped legs, November rows):
  `round5_greenday_book_results.json`
- Day-level CSV (205 Jan–Oct days + 9 November days, both books):
  `round5_greenday_book_days.csv`
- Formal run: `round5_greenday_book_build.py`
- Sources (read-only): `solid60_programme_2026-11-13_bank_A_stack_features.csv` ·
  `oi_buildup_trades.csv` · `round2_trades.csv` · `round4_trades.csv` ·
  `november_shadow_stack_bank_log.csv`
