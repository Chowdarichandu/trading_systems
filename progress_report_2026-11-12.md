# PROGRESS REPORT — October · November-to-date · Whole Year (Jan–Oct 2026)

Compiled 2026-11-12 (evening) from the CSV logs and gated records in `~/workspace/trading`.
Every figure re-summed or cross-checked against its log/record; where a tracker line and a log
disagree, **the log wins** (footnotes §5). Paper only throughout — real money ₹0.
Bases: index figures = option premiums per 1 lot (Bank 30 / Nifty 65), net after ₹220/trade;
stocks figures = **provisional per 100 shares**, net after ₹40/trade.
Segments are reported separately and **never pooled into one verdict total**.
Floor = ₹15,000/month per segment. November window = 8 trading days (Nov 2, 3, 4, 5, 6, 9, 11, 12;
Nov 10 = market holiday).

---

## 1. BANK NIFTY — primary: TUNED STACK v2 (primary since 2026-11-11)

| Window | Net ₹ | Trades (W/L) | Floor standing |
|---|---|---|---|
| **October 2026** (gated record) | **+19,889.50** | 11 legs (9W/2L) | **ABOVE floor** by ₹4,889.50 |
| **November TD — LIVE only** (Nov 11–12) | **−1,720.00** | 1 leg (0W/1L); Nov 11 = no-trade day | Below floor — gap ₹16,720 |
| **November TD — incl. retrospective backfill** (Nov 4 +2,480 · Nov 9 −1,720, scored_live=NO) | **−960.00** | 3 legs (1W/2L) | Below floor — gap ₹15,960 |
| **Whole year Jan–Oct 2026** (gated, causal) | **+127,351.50** | 111 legs | Avg **₹12,735.15/month — below floor by ₹2,264.85/month** (all 10 months positive) |

November live detail: Nov 12 — PE 61200, entry 11:30 @ ₹841.50 → stop 11:35 @ ₹791.50, **−₹1,720**.
(Stack ledger repaired and scored same-day on 2026-11-12; Nov 11–12 rows are now live-scored.)

**Legacy control line — BNF-PAPER-V1** (frozen, judged separately, never added to the primary):

| Window | Net ₹ | Trades (W/L) | Floor standing |
|---|---|---|---|
| October 2026 (v21 frame, gated record) | +14,929.50 | — | Below floor by ₹70.50 |
| November TD | **−1,920.00** | 6 (2W/4L) | Below floor — gap ₹16,920 |
| Whole year Jan–Oct 2026 (gated, causal) | +83,650.50 | 99 legs | Avg ₹8,365.05/month — below floor |

November legacy composition (log-verified, corrected — see footnote 3): **2 PE base legs −₹3,440**
(Nov 2, Nov 9) + **4 NS1 second legs net +₹1,520** (stops Nov 3, Nov 4; targets Nov 11, Nov 12 at
+₹2,480 each) = −₹1,920.

---

## 2. NIFTY — primary: NF-PAPER-C3G7

| Window | Net ₹ | Trades (W/L) | Floor standing |
|---|---|---|---|
| October 2026 | NOT AVAILABLE¹ | — | — |
| **November TD** | **−3,470.00** | 1 (0W/1L) | Below floor — gap ₹18,470 |
| Whole year Jan–Oct 2026 | NOT AVAILABLE¹ | — | — |

November detail: the primary's only trade in 8 days — Nov 9 PE 24800, entry 10:45 @ ₹293.85 →
stop 11:25, −₹3,470. Solo keys were C3-blocked on Nov 5, 11, 12.

**Candidate lines (December evidence):**

| Line | October 2026 | November TD (forward) | Jan–Oct 2026 gated | Monthly avg vs floor |
|---|---|---|---|---|
| **DEC-S1** (adopted candidate) | **+20,160.50** · 4 legs (4W/0L) — above floor | **−443.50** · 5 trades (2W/3L) | **+91,168.50** · 97 legs | ₹9,116.85/mo — below by ₹5,883.15 |
| **TUNED v1** (DEC-S1 − B PE) | **+20,160.50** · 4 legs (no B PE legs fell in Oct) — above floor | **+3,036.50** · 1 leg — **the only positive Nifty forward record** | **+103,050.25** · 74 legs | ₹10,305.03/mo — below by ₹4,694.97 |
| **TUNED v2** (DEC-S1 − B PE − A CE − C CE) | **+15,525.00** · 3 legs — above floor by ₹525 | ₹0 · 0 legs | **+115,950.75** · 59 legs | ₹11,595.08/mo — below by ₹3,404.92 |

**Qualification (never dropped):** DEC-S1's Jan–Oct figure is **FAILED-AND-WAIVED** — the engine
did not bank it (full-target rate 34.0% vs the standing book's 34.3%; March −₹11,846.50 red month);
it stands as the adopted candidate by the owner's direction over that flag. Its B-PE sleeve is the
proven leak: Jan–Oct 23 legs −₹11,881.75 (vs B CE +₹45,506.50); November B legs 4, net −₹3,480 (1 win).
TUNED v1/v2 remove that leak by construction and passed their gates outright.

¹ The C3G7 primary's own gated Jan–Oct/October table does not exist in the compiled sources — it
was never re-scored historically (read-only by rule). Its comparison baseline, the standing causal
book, stands at +₹54,102.00 Jan–Oct (Oct +₹16,480.50) — a baseline, **not** the primary's own score.

---

## 3. STOCKS — primary: STOCK BOOK (frozen 25-stock book, Variant C) · provisional per 100 shares

| Window | Net ₹ | Trades (W/L) | Floor standing |
|---|---|---|---|
| **October 2026** (adoption/freeze record²) | **+56,127.37** | 152 (83W/69L) | **ABOVE floor** by ₹41,127.37 |
| **November TD — FINAL** (EOD logging landed) | **+7,965.74** | 30 (15W/15L) | Below floor — gap ₹7,034.26 |
| **Whole year Jan–Oct 2026** (gated, causal) | **+2,47,178.79** | 1,363 (610W/752L) | Avg **₹24,717.88/month — FLOOR MET** (₹9,717.88/month above) |
| Whole year Jan–Oct **2025** (same book, judged separately) | +1,19,813.44 | 1,064 (483W/581L) | Avg ₹11,981.34/month — below floor; gap ₹30,186.56. (Oct 2025 alone: −₹4,042.67 · 21 trades) |

November final detail: through Nov 11 **+₹8,391.28** (26 trades, 14W/12L); **Nov 12 final day
−₹425.54** (4 trades, 1W/3L: KALYANKJIL P2F +₹803.75 · TATASTEEL P2F-R2 −₹134.37 · HINDCOPPER
N4-V3 −₹404.32 · ASTRAL INV-ABOVE EOD sleeve −₹690.60). The book remains November's green segment.

**Qualification (never dropped):** Variant C's adoption legs (c) and (e) are **FAILED-AND-WAIVED**
against the pre-adoption R16 baseline (2026 −₹10,121.51; combined ex-top-3 −₹16,352.41); "all ten
legs pass" holds only on the construction's frozen R9-04 sheet. Recorded at adoption, 2026-11-02.

² The November paper log holds no October rows; the October figure is the adoption/freeze record
(EOD whole-book basis, incl. EOD sleeves) — a reference basis, stated as such, never blended with
the November log basis.

---

## 4. STOCK ENGINE — its own block (wide 1,081-name live system; never merged with the Stock Book)

| Record | Window | Net ₹ (per 100 sh) | Trades | Standing |
|---|---|---|---|---|
| **Retrospective simulation** (NOT live) | October 2026 | +1,960.01 | 28 (WR 46.4%) | Below floor pace |
| **Retrospective simulation** (NOT live) | Nov 2–11 | +6,764.38 | 11 (4W/7L) | Ex-top-3 −₹1,352.29 — top-3-carried |
| **LIVE record** | Nov 12 (first live day) | **+265.06** | 3 (1W/2L) | ₹25k lens on the day: −₹129.11 |

Simulation 27-day total +₹8,724.39 (ex-top-3 −₹3,256.65) is background evidence only; the engine's
judged record is its live forward record from Nov 12.

---

## 5. Discrepancy footnotes (log wins)

1. **`segment_floor_tracker.md` is stale vs tonight's logs.** It still shows: stack live ₹0/0 legs
   (now **−₹1,720 live**, scored after the 2026-11-12 repair), legacy MTD −₹4,400/5 trades (now
   **−₹1,920/6** after Nov 12), DEC-S1 −₹4,123.50/4 trades (now **−₹443.50/5** after the Nov 11
   catch-up). All figures in this report follow the logs.
2. **The 15:45 MTD report's open gaps have since closed:** stack Nov 11/12 scored (Nov 11 no-trade,
   Nov 12 −₹1,720); DEC-S1 Nov 12 scored as a no-trade day; Stock Book Nov 12 EOD sleeves landed —
   the book's final November figure is **+₹7,965.74**, not the +₹8,656.34 live-layer estimate
   (the ASTRAL INV-ABOVE sleeve, −₹690.60, is the difference).
3. **Bank November composition corrected** by the repair programme (2026-11-12): the earlier
   "4 PE stop-outs / NS1 2-of-2" framing was wrong; the log shows 2 PE base legs (−₹3,440) and
   4 NS1 legs at 2W/2L (net +₹1,520).
4. All tuning variants gated on 2026-11-12 (Bank T-B1a…T-B3, Nifty T-N1a/T-N1b/T-N3, Stocks T-S1)
   **failed**; no figure in this report comes from a failed variant. December rankings stand:
   Bank — STACK v2 · Nifty — TUNED v1, then v2 · Stocks — frozen Stock Book.

*Sources: november_shadow_stack_bank_log.csv · november_paper_bank_log.csv ·
november_paper_nifty_log.csv · november_shadow_decs1_nifty_log.csv ·
stocks_sarvaritu_paper_log.csv · stock_engine_live_log.csv · bank_positive_tuning eve19 trades ·
nifty_next_phase_trades.csv (DEC-S1 leg set, re-summed exact) · stocks_engine_adoptedC book
trades · segment_floor_tracker.md · november_mtd_report_2026-11-12.md ·
repair_programme_2026-11-12.md · tuning_{bank,nifty,stocks}_2026-11-12.md ·
stock_engine_live_2026-11-11.md.*
