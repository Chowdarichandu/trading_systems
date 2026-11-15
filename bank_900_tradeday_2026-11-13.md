# BANK NIFTY — ₹900 PER TRADE-DAY VERIFICATION (2026-11-13)

**Owner's bar (2026-11-13 18:31 IST, supersedes the ₹800-per-calendar-day
framing):** the least minimum AVERAGE return is **₹900 per day, counted only
on days a trade happens** (trade-days). No-trade days are excluded from the
average entirely. Bank Nifty only. Pure option BUYING books. **Real money ₹0 —
no live trades were placed; everything below is paper/backtest on stored,
already-verified ledgers.** Basis: Bank Nifty option premiums per 1 lot (30),
cost ₹220/trade inside every net, UNIQUE-ONCE counting, Jan–Oct 2026
(205 trading days). Offline verification only — no running book or job was
touched.

---

## 1. VERDICT — PASS

**Two existing gated books clear ₹900 per trade-day AND pass the full
controls gate recomputed on this basis:**

| Book | Legs | Trade-days | Jan–Oct total | **₹ / trade-day** | ₹ / leg | ₹ / calendar day | Win rate |
|---|---|---|---|---|---|---|---|
| **TUNED STACK v2** (running primary) | 111 | 89 | **+₹127,351.50** | **₹1,430.92** | ₹1,147.31 | ₹621.23 | 59.5% |
| **PB1** (stack legs, entry premium < ₹500) | 32 | 28 | **+₹69,749.50** | **₹2,491.05** | ₹2,179.67 | ₹340.24 | 75.0% |

PB1 is a subset of the stack (its 32 legs are stack legs admitted below
₹500 entry premium) — **the two passes are not two independent books and
their totals must never be added.** The stack is the book that runs; PB1 is
the proven quality layer inside it.

Every other measured book fails, each on a named leg (§5).

## 2. GATE — recomputed on the trade-day basis, same run

Gate legs (pre-registered in `bank_900_tradeday_build.py` before scoring):
G1 trade-day average ≥ ₹900 · G2 total > 0 · G3 both halves > 0 on the
calendar AND trade-day bases · G4 no red month on the calendar basis ·
G5 ex-top-3 > 0 (trade-day basis) · G6 random-density placebo on the
trade-day-average statistic (2,000 same-count subsets of the parent pool,
seed 42) ≥ 95th percentile · G7 independent re-sum to the paisa.
Timing/leak audit: on record for both books (stack EVE lineage; PB1 legs
verified verbatim against the stack ledger in the bank_2000 run; the band
is the entry candle's open — knowable at entry).

| Leg | STACK v2 | PB1 |
|---|---|---|
| G1 ₹/trade-day ≥ 900 | ✅ ₹1,430.92 | ✅ ₹2,491.05 |
| G2 total > 0 | ✅ +₹127,351.50 | ✅ +₹69,749.50 |
| G3 halves (cal / trade-day) | ✅ +₹83,082.00 / +₹44,269.50 · ₹1,888.23 / ₹983.77 per TD | ✅ +₹44,725.00 / +₹25,024.50 · ₹3,194.64 / ₹1,787.46 per TD |
| G4 red months (calendar) | ✅ **0 of 10** | ✅ **0 of 10** |
| G5 ex-top-3 (trade-day basis) | ✅ +₹100,528.50 over 86 TD = **₹1,168.94/TD** | ✅ +₹42,926.50 over 25 TD = **₹1,717.06/TD** |
| G6 placebo (trade-day statistic) | standing gate on record; supplementary vs union pool: **99.9th pct** (draws' p95 ₹1,293.35) | ✅ **99.9th pct** (draws' p95 ₹1,913.60) |
| G7 re-sum | ✅ exact | ✅ exact |

Both books clear the ₹900 line **even after their three best legs are
removed** (stack ₹1,168.94/TD, PB1 ₹1,717.06/TD ex-top-3).

## 3. MONTH TABLES — both bases

### TUNED STACK v2

| Month | Total | ₹/calendar day | Trade-days | ₹/trade-day |
|---|---|---|---|---|
| Jan | +₹24,028.00 | ₹1,201.40 | 7 | ₹3,432.57 |
| Feb | +₹15,284.00 | ₹727.81 | 9 | ₹1,698.22 |
| Mar | +₹8,560.00 | ₹450.53 | 10 | ₹856.00 |
| Apr | +₹9,810.00 | ₹490.50 | 9 | ₹1,090.00 |
| May | +₹25,400.00 | ₹1,336.84 | 9 | ₹2,822.22 |
| Jun | +₹3,040.00 | ₹144.76 | 7 | ₹434.29 |
| Jul | +₹4,224.00 | ₹183.65 | 13 | ₹324.92 |
| Aug | +₹2,059.50 | ₹98.07 | 5 | ₹411.90 |
| Sep | +₹15,056.50 | ₹716.98 | 10 | ₹1,505.65 |
| Oct | +₹19,889.50 | ₹994.48 | 10 | ₹1,988.95 |
| **Jan–Oct** | **+₹127,351.50** | **₹621.23** | **89** | **₹1,430.92** |

### PB1 (stack legs < ₹500 entry premium)

| Month | Total | ₹/calendar day | Trade-days | ₹/trade-day |
|---|---|---|---|---|
| Jan | +₹21,513.00 | ₹1,075.65 | 5 | ₹4,302.60 |
| Feb | +₹14,102.00 | ₹671.52 | 4 | ₹3,525.50 |
| Mar | +₹760.00 | ₹40.00 | 1 | ₹760.00 |
| Apr | +₹4,070.00 | ₹203.50 | 3 | ₹1,356.67 |
| May | +₹4,280.00 | ₹225.26 | 1 | ₹4,280.00 |
| Jun | +₹2,480.00 | ₹118.10 | 1 | ₹2,480.00 |
| Jul | +₹1,985.00 | ₹86.30 | 3 | ₹661.67 |
| Aug | +₹760.00 | ₹36.19 | 2 | ₹380.00 |
| Sep | +₹8,870.00 | ₹422.38 | 4 | ₹2,217.50 |
| Oct | +₹10,929.50 | ₹546.48 | 4 | ₹2,732.38 |
| **Jan–Oct** | **+₹69,749.50** | **₹340.24** | **28** | **₹2,491.05** |

The bar is the ten-month average: individual months sit below ₹900 per
trade-day in the weak stretch (stack: Mar, Jun, Jul, Aug; PB1: Mar, Jul,
Aug) — no month is red on the calendar basis for either book.

## 4. TRADE-DAY DISTRIBUTION

| | STACK v2 | PB1 |
|---|---|---|
| Trade-days / 205 days | 89 (43.4%) | 28 (13.7%) |
| Trade-days ≥ ₹900 | 58.4% | 71.4% |
| Positive trade-days | 67.4% | 78.6% |
| Median trade-day | +₹2,030.00 | +₹2,255.00 |
| Worst trade-day | −₹3,440.00 | −₹1,720.00 |
| Best trade-day | +₹9,680.00 | +₹9,680.00 |

## 5. FAILURES — measured, with the killing leg named

| Book | ₹/trade-day | Killing leg |
|---|---|---|
| LEGACY BNF-PAPER-V1 (99 legs, +₹83,650.50) | ₹909.24 (92 TD) | **G4** — 3 red months (Apr −₹90.00, Jul −₹3,680.00, Aug −₹873.50). It clears the ₹900 average by ₹9.24 and still fails the gate. Supplementary placebo 5.5th pct. |
| PB3 union <500 (35 legs, +₹75,989.50) | ₹2,451.27 (31 TD) | **G4** — Aug −₹960.00. (Placebo 100th pct, all other legs pass.) |
| PB4 union <650 (52 legs, +₹82,611.50) | ₹1,877.53 (44 TD) | **G4** — Jul −₹4,059.00. (Placebo 99.7th pct.) |
| PB0 legacy <500 (annex; 27 legs) | ₹2,396.10 (25 TD) | **G4** — 3 red months (Mar, Jul, Aug) + 2 zero months (May, Jun). |
| PB2 stack <650 (annex; 49 legs) | ₹1,862.72 (41 TD) | **G4** — Jul red; also carries the bank_2000 standing placebo FAIL on the total statistic. |
| U1 union, no filter (annex; 123 legs) | ₹1,169.42 (101 TD) | **Not a book** — bank_2000 binding leg: a union must beat its best parent; ₹118,111.50 < stack ₹127,351.50. Packaging, not an edge. |

## 6. NOVEMBER FORWARD EVIDENCE — same basis, stated plainly

Verified in this run from `november_shadow_stack_bank_log.csv` (not taken
on trust): the stack has **4 November trade-days** — Nov 4 **+₹2,480.00** ·
Nov 9 **−₹1,720.00** · Nov 12 **−₹1,720.00** · Nov 13 **−₹1,720.00** →
**November total −₹2,680.00 = −₹670.00 per trade-day.** The Jan–Oct pass
does **not** extend to November so far: on the same basis the running
primary is negative this month (1 win in 4 trade-days, against a 59.5%
Jan–Oct win rate).

**PB1's November is ABSENT, not negative:** all 9 distinct November parent
entry premiums (stack log + legacy PRIMARY log) fall between ₹681.95 and
₹867.60 — above the < ₹500 band — so PB1 has placed **0 legs, 0 trade-days**
in November. Its forward record on this basis does not exist yet.

## 7. HONEST CAVEATS

1. **The trade-day average coexists with many no-trade days.** The stack
   trades on 89 of 205 days (43.4%) — 116 days it does nothing. PB1 trades
   on 28 of 205 days (13.7%) — 177 no-trade days. ₹1,430.92/trade-day and
   ₹621.23/calendar-day are the same book stated two ways.
2. **₹900/trade-day is an average, not a daily minimum.** 41.6% of the
   stack's trade-days finish below ₹900 and its worst trade-day is
   −₹3,440.00. The owner's earlier "minimum" language is met only in the
   average sense he defined at 18:31 (no-trade days excluded).
3. **This is a Jan–Oct backtest stage pass.** Per the standing trust rule,
   forward paper evidence is the deciding currency — and the stack's
   November forward line on this basis is −₹670.00/trade-day (§6). The
   pass certifies the ten-month gated record, not November.
4. PB1's higher average is bought with rarity: it is a filter fact about
   the stack's cheap-premium legs, already wired as a prepared-not-started
   paper spec in the bank_2000 programme (§7 there). Nothing was armed by
   this verification.

## FILES

- This report: `bank_900_tradeday_2026-11-13.md`
- Build (pre-registration in header): `bank_900_tradeday_build.py`
- Results: `bank_900_tradeday_results.json` (every figure above, re-summed)
- Parents: `solid60_programme_2026-11-13_bank_A_stack_features.csv` ·
  `bank_engine_r6_v21_trades.csv` · `bank_2000_PB{0,1,2,3,4}_*_trades.csv` ·
  `bank_2000_U1_union_all_trades.csv` · `november_shadow_stack_bank_log.csv`
