# Stocks resume — event watchlist refresh + S10 (setup2-PE new room) — 2026-10-30

**STOCKS ONLY — cash intraday, 25 screenshot stocks. Paper only, no
orders. Every rupee figure below is provisional per 100 shares — NOT
an options-lot or futures-lot profit. Stocks are never pooled with
index. Real money: ₹0.**

Stocks work resumed 2026-10-30 on the user's instruction, after the
08:12 pause (index first) was lifted. Starting point: S9 is the
highest-tuned stock version (50 trades Jan–Oct 2026, +₹1,640.00
provisional per 100 shares, NOT adopted).

---

## 1. Event picture first — November 2026 watchlist (refreshed)

Full file: `stock_event_watchlist_nov2026.md`. Rule applied: check
influencing factors (results / CEO changes / major news) BEFORE any
system work. **No CEO/management-change or other single-stock
major-news event for any of the 25 was found for November — the month
is results-driven.**

Verified in this refresh (public sources, 2026-10-30):
ITC **2 Nov**, NATIONALUM **2 Nov** (results + interim dividend),
NHPC **4 Nov**, GLENMARK **5 Nov**, HINDALCO **6 Nov**,
OIL **12 Nov** — ⚠️ **correction: earlier watchlist said OIL 11 Nov;
the current board-meeting list says 12 Nov.**
GODREJCP already reported **29 Oct** (+ ₹5 interim dividend, record
date 4 Nov — its post-reaction window runs into ~10 Nov).
HINDZINC (19 Oct), RECLTD (26 Oct, + ₹3.50 dividend), VEDL (28 Oct)
already reported — November carries only their post-reaction windows.

Carried from Results Intelligence v1, not re-verified this pass:
NTPC 31 Oct (reaction Mon 2 Nov), PFC 5 Nov, TATASTEEL **7 Nov**
(revised from 27 Oct; Saturday board → reaction Mon 9 Nov),
KALYANKJIL 10 Nov, BDL 14 Nov (reaction Mon 16 Nov), IRCTC 17/18 Nov.

No November date found this pass for HDFCBANK, TVSMOTOR, UNITDSPR,
OBEROIRLTY, INDUSTOWER, WIPRO, HINDCOPPER, ASTRAL, HINDUNILVR —
labelled unconfirmed in the watchlist, NOT treated as no-event proof;
recheck in November paper week 1.

---

## 2. S10 — frozen before scoring

Spec: `new_stock_system_s10_frozen.md` (frozen 2026-10-30, before the
run). Engine: `stock_system_s10.py`.

S10 = S9 exactly (S8 price design + Event Gate v1 G-TIERED + gate-ranked
cap 1/day, 1/stock/week), ONE change: for **setup2_or_breakdown PE
candidates only**, the PD-level room test is replaced by a
structural-support room test — room = entry − nearest prior daily low
below entry, lookback 20 trading days (extend to 60 if no low is below
entry; if still none, open-downside, test passed, sentinel ratio
999.0). Threshold unchanged: room ≥ 1.5× risk. The gate reads the new
room_ratio for these candidates. Everything else byte-identical.

Why: S8's diagnosis — a setup2 breakdown fires on a close below PDL,
so by entry there is usually **no PD level below entry** and the old
test discarded the candidate before measuring anything.

### Funnel diagnostic (same window, candidate stage)

| Stage | Count |
|---|---|
| Raw setup2 PE signals (25 stocks, Jan–Oct) | 92 |
| Second-close confirmed + valid risk | 45 |
| Passed OLD PD-level room test | **0 of 45** |
| Passed NEW structural room test | 18 of 45 |
| Of those 18: then blocked by Nifty-bias / prospective < ₹500 | 4 / 13 (some both) |
| Setup2 PE candidates in S10's uncapped pool | 4 |

The structural diagnosis was right — the old test killed 45 of 45.
But it was not the frequency bottleneck: the ₹500 prospective floor
and the second-close chain cut far more than room ever did.

---

## 3. S10 results vs S9 — Jan–Oct 2026, identical window

| | **S9** | **S10** |
|---|---|---|
| Trades | 50 | 53 |
| Trades/day (203 days) | 0.246 | 0.261 |
| Win rate | 50.0% | 50.9% |
| Full targets | 13 (26.0%) | 13 (24.5%) |
| **Net, provisional per 100 shares** | **+₹1,640.00** | **+₹1,677.50** |
| Expectancy / trade | +₹32.80 | +₹31.65 |
| Setup mix | setup3 41, setup4 9, setup2 **0** | setup3 40, setup4 9, setup2 **4** |

The 4 rescued setup2 PE trades (all no_event tier): HINDUNILVR
2026-03-17 −₹700 (swing20), NTPC 2026-02-26 −₹325 (swing20),
HDFCBANK 2026-09-09 +₹307.50 (open-downside), HINDUNILVR 2026-09-29
+₹445 (open-downside) → **setup2 leg net −₹272.50, 0 full targets**.
One side effect: the 2026-03-17 HINDUNILVR setup2 trade took that
day's single cap slot from S9's OBEROIRLTY trade.

### Month-by-month cumulative (provisional per 100 shares)

| Month | S9 month | S9 cum | S10 month | S10 cum |
|---|---|---|---|---|
| Jan | +2,375.00 | +2,375.00 | +2,375.00 | +2,375.00 |
| Feb | −520.00 | +1,855.00 | −845.00 | +1,530.00 |
| Mar | −645.00 | +1,210.00 | −1,035.00 | +495.00 |
| Apr | −785.00 | +425.00 | −785.00 | −290.00 |
| May | −535.00 | −110.00 | −535.00 | −825.00 |
| Jun | −940.00 | −1,050.00 | −940.00 | **−1,765.00** |
| Jul | +1,815.00 | +765.00 | +1,815.00 | +50.00 |
| Aug | +1,035.00 | +1,800.00 | +1,035.00 | +1,085.00 |
| Sep | +360.00 | +2,160.00 | +1,112.50 | +2,197.50 |
| Oct (1–28) | −520.00 | +1,640.00 | −520.00 | +1,677.50 |

S10 oscillates exactly like S9 — same Jan-high, same Feb–Jun bleed —
and digs a **deeper** mid-year hole (−₹1,765 vs −₹1,050 at June)
before recovering to a near-identical finish.

---

## 4. Verdict — S10 NOT adopted, NOT a November watch candidate

Against the pre-registered rule (progress on net + win + frequency
together, cumulative not worse):

- **Net:** +₹37.50 better over 10 months — noise, not progress.
- **Win rate:** 50.9% vs 50.0% — held, not a real gain; full-target
  rate fell (24.5% vs 26.0%).
- **Frequency:** 0.261/day vs 0.246 — nowhere near the user's
  1 valuable trade/day standard. **Failed leg.**
- **Cumulative path:** ends ₹37.50 higher but with a worse drawdown
  path (June trough −₹1,765). **Failed leg.**

**S9 remains the highest-tuned stock version.** S10 goes to the
rejected list. The durable finding: setup2 PE exists (92 raw signals)
but is rare after confirmation (45) and its rescued trades do not pay
(−₹272.50, 0 full targets) — closing the setup2-PE family. The binding
constraints on stock frequency are the prospective ≥₹500 floor and
the confirmation chain, not room.

## 5. Next family — S11 frozen (diagnosed, NOT scored)

S9's no-event leg diagnosed from its capped trades (30 trades,
−₹885): the loss is setup3 PE (26 trades, −₹2,870), and it enters
through the gate's OR rule — room-only passes 18 trades / −₹1,855,
prospective-only passes 3 / −₹1,050, while candidates passing BOTH
bars were 9 trades / **+₹2,020**.
**S11 frozen** (`new_stock_system_s11_frozen.md`): S9 base, one
change — no-event tier requires room ≥ 2.0× **AND** prospective
≥ ₹1,000. Frozen 2026-10-30, deliberately **not scored** in this
session; scoring is the next stocks step, and its frequency leg will
be reported honestly (this fix removes trades by design).
