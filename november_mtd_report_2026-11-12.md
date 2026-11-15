# November MTD Performance Report — 2026-11-01 → 2026-11-12

Compiled 2026-11-12 (~15:45 IST) from the CSV logs in ~/workspace/trading. Every figure independently re-summed from the log rows; no day estimated. Trading days: Nov 2, 3, 4, 5, 6, 9, 11, 12 (Nov 10 = Diwali-Balipratipada holiday, markets closed; Nov 1/7/8 weekend). Paper only, real money ₹0. Bases: index lines = option premium per 1 lot, net after ₹220/trade; stock lines = provisional per 100 shares, net after ₹40/trade. **Segments are never pooled into one verdict total** — each line stands alone.

---

## 1. BANK STACK v2 — PRIMARY (ledger: november_shadow_stack_bank_log.csv)

**⚠️ DATA GAP — this ledger contains rows for ONLY TWO days: 2026-11-04 and 2026-11-09.** Both are RETROSPECTIVE BACKFILL (scored_live = NO, candle-scored 2026-11-10 under the v1 definition). **LIVE (v2 rules) record: ₹0 · 0 legs — no live day has been scored yet.**

| Day | Net ₹ | Trades |
|---|---|---|
| Nov 4 | +2,480.00 (S3-R1 PE 55800, runner_stop) | 1 |
| Nov 9 | −1,720.00 (Skill V3 PE 58900, entry-bar stop) | 1 |
| **MTD (file contents)** | **+760.00** | **2 (1W / 1L)** |

Days with NO row in the ledger:
- Nov 2, 3, 5, 6 — no rows (the 2026-11-10 backfill recorded no stack trades on those days; they are not written as no-trade rows in this ledger).
- **Nov 11 — NOT SCORED (NC).** The stack's first live day. Cause: Upstox daily-bar series still ends 2026-11-09, so the scorer's spot-directory prep aborts (intraday candles complete). Excluded, never estimated; catch-up runs automatically once the daily bar is served.
- **Nov 12 — NOT SCORED yet** (same scoring chain pending).

## 2. BANK LEGACY — BNF-PAPER-V1 (november_paper_bank_log.csv, PRIMARY rows)

| Day | Net ₹ | Trades |
|---|---|---|
| Nov 2 | −1,720.00 | 1 |
| Nov 3 | −1,720.00 | 1 |
| Nov 4 | −1,720.00 | 1 |
| Nov 5 | 0 (no trade) | 0 |
| Nov 6 | 0 (no trade) | 0 |
| Nov 9 | −1,720.00 | 1 |
| Nov 11 | +2,480.00 | 1 |
| Nov 12 | +2,480.00 (NS1 CE 61200 target) | 1 |
| **MTD** | **−1,920.00** | **6 (2W / 4L)** |

Control line (U1-B2, same file, never added to primary): **MTD −₹3,440.00 · 2 trades (0W/2L)** — Nov 2 −1,720, Nov 9 −1,720.

## 3. NIFTY PRIMARY — NF-PAPER-C3G7 (november_paper_nifty_log.csv, PRIMARY rows)

| Day | Net ₹ | Trades |
|---|---|---|
| Nov 2–6, 11, 12 | 0 (no trade — solo Skill CE keys blocked by C3 each day) | 0 |
| Nov 9 | −3,470.00 (PE 24800 stop — the primary's only November trade) | 1 |
| **MTD** | **−3,470.00** | **1 (0W / 1L)** |

Control line (U1-N1, same file): **MTD −₹3,470.00 · 1 trade** (Nov 9, same confirmed key).

## 4. STOCK BOOK (stocks_sarvaritu_paper_log.csv — full book, EOD construction)

| Day | Net ₹ | Trades (W/L) |
|---|---|---|
| Nov 2 | +1,455.27 | 4 (3/1) |
| Nov 3 | −451.85 | 1 (0/1) |
| Nov 4 | −420.94 | 6 (3/3) |
| Nov 5 | −299.28 | 5 (1/4) |
| Nov 6 | +6,577.68 | 4 (4/0) |
| Nov 9 | +704.30 | 4 (2/2) |
| Nov 11 | +826.10 | 2 (1/1) |
| **MTD through Nov 11** | **+8,391.28** | **26 (14W / 12L)** |

**⚠️ GAP — Nov 12 has NO row in the book log yet:** the book's EOD sleeves finalise ~16:35 today. What is known for Nov 12 is the **live layer only** (producer CSV stocks_sarvaritu_live_shadow_log.csv): KALYANKJIL +803.75, HINDCOPPER −404.32, TATASTEEL −134.37 = **+₹265.06 · 3 trades (1W/2L)**. The EOD sleeves (F4 / INV-LONG / INV-ABOVE) may still add trades tonight — Nov 12's book figure is NOT final until the 16:35 logging lands.

## 5. STOCK ENGINE (stock_engine_live_log.csv + retrospective sim summary)

**LIVE forward record (starts Nov 12):**

| Day | Net ₹ | Trades |
|---|---|---|
| Nov 12 | +265.06 (KALYANKJIL P2F target +803.75 · HINDCOPPER N4-V3 stop −404.32 · TATASTEEL P2F-R2 stop −134.37) | 3 (1W/2L) |

**Retrospective simulation, Nov 2–11** (scored_live=NO / backfill — from stock_engine_live_2026-11-11_summary.json; the live ledger CSV itself contains only the Nov 12 rows): Nov 2 −300.24 · Nov 3 −451.85 · Nov 4 −398.77 · Nov 5 −309.43 · Nov 6 +3,959.87 · Nov 9 +3,438.70 · Nov 11 +826.10 → **+₹6,764.38 · 11 trades (4W/7L)**, ex-top-3 −₹1,352.29 (top-3-carried, as flagged at build).

**November total (sim + live): +₹7,029.44 · 14 trades** — of which the genuine live forward evidence is only Nov 12: **+₹265.06**.

## 6. SHADOWS (one line each)

| Shadow | Per-day nets (scored days) | MTD ₹ | Trades (W/L) | Gaps |
|---|---|---|---|---|
| **DEC-S1** (Nifty) | Nov 2 −220.00 · Nov 3 −433.50 (2 tr) · Nov 5 −3,470.00 · Nov 11 +3,680.00 | **−443.50** | 5 (2/3) | **Nov 12 UNSCORED** — daily-candle lag (scorer aborted on spot-dir prep) |
| **Nifty TUNED SHADOW BOOK v2** | No leg on any scored day (Nov 6, Nov 9 scored: no leg; Nov 11 scored via DEC-S1 construction — its only leg was a Component B PE, which v2 excludes by construction → no leg) | **0.00** | 0 | **No standalone CSV log exists** — derived from the DEC-S1 construction, tracked in segment_floor_tracker.md. **Nov 12 UNSCORED** with DEC-S1 (same candle lag) |
| **SHADOW v21** (Bank) | Nov 2 −1,720 · Nov 4 +2,480 · Nov 9 −1,720 · Nov 3/5/6/11 scored no-trade | **−960.00** | 3 (1/2) | **Nov 12 UNSCORED** — no row (candle lag) |
| **SHADOW v22** (Bank) | Nov 4 +2,480 · Nov 9 −1,720 · Nov 2 leg removed by EVE-05 before scoring (not a trade) · Nov 3/5/6/11 scored no-trade | **+760.00** | 2 (1/1) | **Nov 12 UNSCORED** — no row (candle lag) |
| **SHADOW Skill Bank** | Nov 2 −1,720 · Nov 3 −1,720 · Nov 4 −1,720 · Nov 5 +2,480 · Nov 6 +2,480 · Nov 9 −1,720 · Nov 11 +2,480 · Nov 12 −1,720 | **−1,160.00** | 8 (3/5) | Fully scored incl. Nov 12 |
| **SHADOW Skill Nifty** | Nov 2 −3,470 · Nov 3 +2,688.75 · Nov 5 +5,194.50 · Nov 6 +3,030.00 · Nov 9 −3,470 · Nov 11 −3,470 · Nov 12 −3,470 | **−2,966.75** | 7 (3/4) | Fully scored incl. Nov 12 |

(Also standing, from segment_floor_tracker.md — Bank TUNED SHADOW BOOK v3: MTD −₹2,680 · 4 trades through Nov 11; its Nov 12 row is scored by the evening Bank engine, not yet final at compile time.)

---

## Reference-point verification (all independently re-summed)

| Standing figure | Recomputed | Verdict |
|---|---|---|
| Bank legacy MTD through Nov 11 = −₹4,400 (5 trades) | −₹4,400.00 · 5 trades | ✅ MATCH |
| Bank legacy + Nov 12 +₹2,480 → −₹1,920 expected | −₹1,920.00 · 6 trades | ✅ MATCH |
| Nifty primary MTD = −₹3,470 (1 trade) | −₹3,470.00 · 1 trade | ✅ MATCH |
| Stock Book MTD through Nov 11 = +₹8,391.28 | +₹8,391.28 · 26 trades | ✅ MATCH |
| DEC-S1 MTD through Nov 11 = −₹443.50 | −₹443.50 · 5 trades | ✅ MATCH |
| Skill Bank MTD through Nov 11 = +₹560 (7 trades) | +₹560.00 · 7 trades | ✅ MATCH |
| Skill Nifty MTD through Nov 11 = +₹503.25 (6 trades) | +₹503.25 · 6 trades | ✅ MATCH |
| Stack MTD = +₹760 backfill | +₹760.00 · 2 legs, both scored_live=NO | ✅ MATCH |

**No mismatches found.**

## Open data gaps (nothing estimated)

1. **Stack v2 primary: Nov 11 NC + Nov 12 unscored** — its live record is still ₹0/0 legs; the +₹760 is backfill only. Cause: Upstox daily-candle lag breaking the scorer's spot-dir prep; catch-up is automatic once the daily bar publishes (Nov 11→12 precedent for the shadow logs).
2. **Nov 12 unscored** for DEC-S1, Nifty TUNED v2, SHADOW v21, SHADOW v22 — same candle lag. Skill Bank/Nifty Nov 12 DID score (different route).
3. **Stock Book Nov 12 not final** — EOD sleeves land ~16:35; only the live layer (+₹265.06) is known.
4. **Nifty TUNED v2 has no CSV ledger of its own** — it exists only as a DEC-S1-construction derivation in the floor tracker.
