# FROZEN ENGINE BOOK — JAN 2025 → OCT 2026 VALIDATION

**Run ordered by Chandu, 2026-10-31: "Now run for jan 2025 to till date."**
The six-component book frozen in `stocks_engine_candidate_spec.md` was run
**verbatim** — every gate, exit and mechanism-scoped exclusion exactly as
frozen. No re-tuning, no new exclusions fitted on 2025, no parameter
changes. 2025 is the out-of-sample year (the engine was built entirely on
Jan–Oct 2026); Jan–Oct 2026 is the in-sample control.

Basis (unchanged): equity cash intraday, home 25 only, LONG/SHORT,
provisional per 100 shares, ₹40/trade cost, paper only, real money ₹0,
square-off 15:10, RF-1 weekend/special-session stand-aside.

---

## HEADLINE

| Window | Book | Trades | Net (₹, per 100 sh, after ₹40/tr) | ₹/month |
|---|---|---:|---:|---:|
| **2025 (out-of-sample)** | **F4 + INV-LONG only** — 4 of 6 components NOT RUNNABLE (see §5) | 506 | **+2,548.77** | **+212.40** |
| 2026 Jan–Oct (in-sample control) | Full six-component book | 663 | **+197,607.74** — reproduces the plateau **exactly** | +19,760.77 |
| Combined (asymmetric — see §4) | 2025 partial + 2026 full | 1,169 | +200,156.51 | +9,098.02 avg over 22 months |

Against the ₹75,000/month goal: the runnable part of the book earned
essentially **zero out-of-sample** (+₹212/month). F4 — the book's biggest
in-sample earner (+₹101,757.06 in 2026) — **lost money in 2025**
(−₹5,093.75). INV-LONG stayed mildly positive (+₹7,642.52). The small
positive 2025 total is concentrated: ex-top-3 the partial book is
**−₹20,101.77**; one stock (OBEROIRLTY, +₹14,367.48) carries it.

---

## 1. DATA INVENTORY (Step 1)

**(a) 5-min candles, home 25, Jan–Dec 2025 — FOUND, with one gap, filled.**
The progressive cache (`data/progressive/<SYM>/spot_5m.csv` +
`spot_daily.csv`) already spans 2025-01-01 → 2026-10-28 for all 25 stocks +
NIFTY. One gap: **ASTRAL, BDL, HINDUNILVR, OIL were missing all of
September 2025** (22 trading days, 2025-09-01 → 2025-09-30, in both files).
Filled from Upstox with the existing pipeline
(`fetch_upstox_via_connector.call`, `keys.json` instrument keys): 1,650
5-min bars / 22 days per symbol, dates matching NIFTY's cached September
dates exactly. **Pipeline consistency proof:** the same fetch+aggregate
path applied to NIFTY for Sep 2025 reproduces the cache's daily bars to
the paisa (22 days × 4 OHLC fields, 0 mismatches) — so all fills are in
the cache's own convention (daily = 5-min aggregation, close = last bar).

**(b) Daily closes for the 50DMA state — lookback fetched.**
The cache starts 2025-01-01, leaving no 50DMA for Jan–mid-Mar 2025.
Fetched Oct–Dec 2024 5-min candles for NIFTY + all 25 via the same
pipeline and aggregated to daily (62 trading days, 2024-10-01 →
2024-12-31, every symbol). With this prepend, the 50DMA is computable
from **2025-01-01 itself**; the state gates run on real state all year
(no missing-state artefacts). Regime math spot-checked by independent
recomputation on 2025-01-02, 2025-03-17, 2025-06-02, 2026-10-30 — exact.

**(c) 2025 event/reaction calendar — CANNOT be built with the same rules.**
The 2026 reaction set lives in `stock_event_calendar_jan_oct_2026.csv`,
built from per-event web research (source: Moneycontrol Board Meetings),
including judgement fields (`reaction_date`, `known_before_open`,
`after_market`) that decide same-day vs next-day reaction. No builder
script or raw research dataset for the home calendar exists in the
workspace (`results_intelligence.py` is a standalone event-study tool
that takes a hand-supplied dates CSV; it does not build this calendar).
The calendar's only 2025 rows are 15 Q2-FY26 results rows (Oct–Nov 2025)
whose `reaction_date` is a placeholder (2026-01-01) — unusable. Rebuilding
~115 events for 2025 with fresh per-event timing research would be a
different construction, not the same rules. **Consequence: N4-V3, P2F,
P2F-R2 and R2-LOWBAND are NOT RUNNABLE on 2025** (§5). They are not
approximated from price data.

**(d) INV-LONG P2 pool for 2025 — built.** Round-8 chains rebuilt from
2025 candles with the identical machinery (pool_pick over V5/skill_or
heads, T125/S050), ADR from the merged daily series (same formula: mean
of prior-10-days' range% ). Stage counts in §3.

**(e) F4 signal machinery on 2025 — identical.** The V5/skill_or
detectors, premove measurement (10:00), band [0.5%, 1.0%), below-50DMA
gate and chain logic are the audited code paths, re-pointed at a shadow
dataset (cache + fills) with the day window extended to
2025-01-01 → 2026-10-28. The workspace cache files were not modified.

Oct 29–30 2026 are handled exactly as in-sample: DAYCTX built from the
1-min cache aggregation (H1's `build_extra_ctx` verbatim; aggregation
re-validated in this run: 1,875 bars checked, 0 mismatches), NIFTY daily
extended via H1's fetch-and-validate-overlap logic.

---

## 2. CONTROLS — 2026 REPRODUCTION (Step 3 ii)

All controls ran **before** any 2025 number was produced, in the same run:

| Control | Result |
|---|---|
| A. SAT-36 dump assembly == plateau | **PASS** — 663 tr / +₹197,607.74 / frozen month table / ex-top-3 ₹72,518.25, exact |
| B1. F4 machinery rebuild at T150/S080 == `stocks_engine_oc4_f4s080_trades.csv` | **PASS** — 661/661 trades, per-trade identical (date, symbol, round, net, entry_time); timing audit 0 violations |
| B2. F4 machinery rebuild at T150/S095, frozen filters == frozen F4 set | **PASS** — 389 tr, +₹101,757.06; audit 0 violations |
| C. INV-LONG machinery rebuild == frozen INV set | **PASS** — 155 tr, +₹38,987.84; stage anchors reproduce exactly (chain 6,687 → P2 918 → INV1 694 → LONG 249 → book 155) |

Because B and C rebuild F4 and INV-LONG from raw candles and match the
frozen book trade-for-trade on 2026, the identical code paths scoring
2025 inherit that audit. **The plateau is reproduced exactly; nothing in
the frozen book's definition was altered.**

2026 component table (in-sample, for contrast with §3):

| Component | Trades | Net ₹ |
|---|---:|---:|
| F4 | 389 | +101,757.06 |
| INV-LONG | 155 | +38,987.84 |
| N4-V3 | 47 | +21,293.05 |
| P2F | 32 | +19,416.63 |
| P2F-R2 | 33 | +14,892.38 |
| R2-LOWBAND | 7 | +1,260.78 |
| **Total** | **663** | **+197,607.74** |

---

## 3. 2025 STANDALONE (Step 3 i + iv) — PARTIAL BOOK: F4 + INV-LONG ONLY

506 trades · **total +₹2,548.77** · expectancy **+₹5.04/trade** ·
win rate 41.3% · breadth **12/25** stocks net-positive ·
ex-top-3 **−₹20,101.77** · max drawdown **−₹17,338.53** (chronological
trade curve) · top stock OBEROIRLTY +₹14,367.48 (564% of the total).

### Month table

"Below50 days" = days NIFTY's previous close was at/below its 50DMA —
the joint state both runnable components require. The zero months are
**gate-closed months** (the state never occurred), not flat trading.

| Month | Below50 days | Trades | F4 ₹ | INV-LONG ₹ | Book ₹ |
|---|---:|---:|---:|---:|---:|
| 2025-01 | 22/23 | 156 | −6,421.88 | +3,218.76 | **−3,203.12** |
| 2025-02 | 20/20 | 130 | +608.15 | +7,168.21 | **+7,776.36** |
| 2025-03 | 13/19 | 101 | −6,221.81 | +1,073.17 | **−5,148.64** |
| 2025-04 | 5/19 | 35 | +1,811.16 | −3,169.30 | **−1,358.14** |
| 2025-05 | 0/21 | 0 | — | — | 0.00 (gate closed) |
| 2025-06 | 0/21 | 0 | — | — | 0.00 (gate closed) |
| 2025-07 | 6/23 | 21 | −1,025.28 | −882.78 | **−1,908.06** |
| 2025-08 | 17/19 | 32 | +4,967.55 | +812.80 | **+5,780.35** |
| 2025-09 | 10/22 | 28 | +4,210.19 | −578.34 | **+3,631.85** |
| 2025-10 | 1/21 | 3 | −3,021.83 | 0.00 (no qualifying trade) | **−3,021.83** |
| 2025-11 | 0/19 | 0 | — | — | 0.00 (gate closed) |
| 2025-12 | 1/22 | 0 | 0.00 (no qualifying signal) | 0.00 | 0.00 |
| **Year** | **95/249** | **506** | **−5,093.75** | **+7,642.52** | **+2,548.77** |

- **Red months (with trades): 5** — Jan, Mar, Apr, Jul, Oct.
  Worst month: **Mar 2025, −₹5,148.64**. Best: Feb 2025, +₹7,776.36.
- The every-month-positive property of the in-sample book does **not**
  survive out-of-sample: of the 8 months that traded, 5 lost money.

### Per-component, 2025

| Component | Trades | Net ₹ | Expectancy ₹/tr | Win % | Breadth | Ex-top-3 ₹ | Max DD ₹ |
|---|---:|---:|---:|---:|---:|---:|---:|
| F4 | 261 | **−5,093.75** | −19.52 | 47.1 | 12/25 | −14,975.75 | −18,552.84 |
| INV-LONG | 245 | **+7,642.52** | +31.19 | 35.1 | 7/25 | −5,606.51 | −11,359.38 |
| Event comps (N4-V3, P2F, P2F-R2, R2-LOWBAND) | — | **NOT RUNNABLE 2025** | — | — | — | — | — |

- **F4 bled out-of-sample.** In-sample it was +₹101,757.06 (389 tr,
  +₹261.59/trade expectancy); on 2025 the same frozen rule is
  −₹19.52/trade. Its 2025 lag-placebo (yesterday's premove qualifying
  today's entries, same filters) lost even more: 153 tr, −₹11,085.16 —
  the real rule beats its placebo, but both are negative: the timing
  ordering held, the population didn't pay.
- **INV-LONG carried the year** (+₹7,642.52) but thinly: breadth 7/25,
  ex-top-3 negative, and 237 of its 245 trades fell in Jan–Apr (the
  below-trend stretch). Stage counts 2025: chain rows 8,767 → P2 pool
  1,620 → INV1 955 → LONG 383 → book 245 after frozen exclusions + RF-1.
- **Timing audit (Lesson 1): 0 violations on all 506 trades** — every
  F4 entry follows a ≥10:00 measurement and a later signal bar; every
  INV entry is a next-bar open inside 09:35–15:10; regime inputs use
  prior-day closes only. RF-1 dropped 1 F4 trade on the one weekend
  session in the 2025 calendar (Sat 2025-02-01, Budget session).

---

## 4. COMBINED JAN 2025 – OCT 2026 (Step 3 iii) — READ THE CAVEAT

The combined figure is **asymmetric by construction**: 2025 contributes
only 2 of the 6 components (506 of the trades), 2026 contributes all 6
(663 trades). It is reported because it was asked for, not as a
like-for-like book total.

- Combined total: **+₹200,156.51** over 22 months = **₹9,098.02/month**
  vs the **₹75,000/month** goal (12.1% of goal).
- 2025 partial-book average: **+₹212.40/month** (12 months).
- 2026 full-book average (in-sample): **+₹19,760.77/month** (10 months).
- Had the four event components been runnable on 2025, the 2025 line
  would differ by their (unknown) 2025 result; in-sample they were
  worth +₹57,862.84 over 10 months, which is **not** evidence about 2025.

---

## 5. DATA GAPS AND NOT RUNNABLE COMPONENTS (Step 3 vi)

| Item | Status |
|---|---|
| **N4-V3 — NOT RUNNABLE 2025** | Needs the reaction-day set (results + single-news events with reaction dates). No same-rules 2025 calendar exists (§1c). |
| **P2F — NOT RUNNABLE 2025** | Needs reaction-day close-to-close moves ≥2.5% from the same calendar. Same reason. |
| **P2F-R2 — NOT RUNNABLE 2025** | Same reaction set, R+2 entry. Same reason. |
| **R2-LOWBAND — NOT RUNNABLE 2025** | Same reaction set, [2.0%, 2.5%) band. Same reason. |
| Sep 2025 candles, ASTRAL/BDL/HINDUNILVR/OIL | **Gap filled** from Upstox via the existing pipeline; verified consistent with the cache convention (§1a). Without the fill these 4 names would have had a broken prev-day chain on 2025-10-01 and no September trading. |
| Oct–Dec 2024 daily lookback | **Filled** (62 trading days × 26 symbols) so the 50DMA/ADR state is real from 2025-01-01 (§1b). |
| 50DMA state, Jan–Dec 2025 | Fully computable — no missing-state caveat remains for F4/INV-LONG. |
| Watchlist size | Data holds 25 stocks; the other 5 names (of the "30" mentioned) were never provided — out of scope here as in-sample. |
| Broker charges | Still the frozen ₹40/trade assumption; Chandu's actual charges are unknown. |

---

## 6. NOTED, NOT APPLIED (Step 3 v)

Observations from the 2025 run. **None of these were applied** — the
book ran verbatim, and acting on any of them would be fitting on 2025.

1. **F4 × HINDUNILVR × LONG: 8 trades, −₹10,218.40** — the worst slice
   of 2025, larger than F4's whole year loss. The frozen exclusions
   cover HINDUNILVR SHORT (in F4) only. Noted only.
2. **F4 × TVSMOTOR × SHORT: 7 tr, −₹5,728.79** and **F4 × GLENMARK ×
   SHORT: 7 tr, −₹3,010.96** — GLENMARK SHORT is the slice SAT-36
   refused to delete in-sample (full-period −₹136.98, quality bar not
   met). It bled on 2025; the refusal standard is unchanged. Noted only.
3. **INV-LONG × RECLTD: 28 tr, −₹2,070.42** — INV-LONG's worst name
   slice of 2025. Noted only.
4. **The book is regime-bound.** Both runnable components require a
   below-50DMA market state; in 2025 that state existed on only 95 of
   249 trading days and was absent for entire months (May, Jun, Nov).
   In above-trend years the frozen book structurally cannot approach
   ₹75,000/month — its frequency goes to zero. Any all-weather coverage
   would be a new system under the controls gate, not a change to this
   book.
5. **A 2025 event calendar is researchable in principle** (exchange
   announcement archives, event by event) in a future session; only
   then could N4-V3/P2F/P2F-R2/R2-LOWBAND be validated on 2025. It was
   not approximated here.
6. **Concentration persisted out-of-sample** (Lesson 6): the partial
   book's positive total rests on OBEROIRLTY alone; ex-top-3 is
   −₹20,101.77. The December fresh-data judging of the frozen book
   (pre-registered in the candidate spec) remains the next verdict that
   counts.

---

## 7. FILES

- Trades (2025, F4 + INV-LONG, 506 rows):
  `stocks_engine_2025_validation_trades.csv`
- This run's script (rerunnable, controls first, exits before scoring
  2025 if any control fails): `stocks_engine_2025_validation.py`
- Frozen book definition: `stocks_engine_candidate_spec.md`

*Paper only. Real money ₹0. No orders placed. Provisional per-100-shares
basis throughout — not an options-lot or futures-lot figure.*
