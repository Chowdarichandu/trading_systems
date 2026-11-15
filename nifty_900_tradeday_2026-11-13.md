# NIFTY ₹900-PER-TRADE-DAY VERIFICATION — 2026-11-13

**Real money: ₹0. Paper only, no live orders, nothing armed or modified —
offline verification of stored, previously gated books.**

**THE BAR (owner, 2026-11-13 18:31 IST):** the least minimum AVERAGE return
must be **₹900 per day, counted only on days a trade happens (trade-days)**.
No-trade days are excluded from the average entirely.

**Basis for every figure:** Nifty index options, option premiums per 1 lot
(65), cost ₹220/trade inside every net, UNIQUE-ONCE, expiries per each
book's frozen spec (weekly sleeve = Component C). Option BUYING only — all
three books are long-premium constructions. Leg sets were rebuilt
deterministically from the stored harnesses + the frozen r11 component
dump and the gated anchors reproduced **to the paisa** before any new
statistic was computed (DEC-S1 +₹91,168.50/97 · TUNED v1 +₹103,050.25/74 ·
TUNED v2 +₹115,950.75/59). Computation:
`nifty_900_tradeday_2026-11-13.py` → `nifty_900_tradeday_2026-11-13_results.json`.
Calendar: 205 trading days Jan–Oct 2026 (programme-standard volrix daily
file). Controls, all recomputed for the trade-day statistic in this run:
timing audit, NC count, independent CSV re-sum, month table on BOTH bases,
halves on the trade-day basis, trade-day distribution, shifted-entry
placebo family (delay 2–12 bars incl. canonical shift30) expressed as a
percentile of the trade-day average, ex-top-3 on the trade-day basis
(3 best trade-DAYS removed).

---

## VERDICT — TUNED v2 PASSES

**Nifty TUNED v2 (EVE-11: DEC-S1 − B PE − A CE − C CE) clears the owner's
₹900/trade-day bar and passes the full controls gate on this basis.**

| Measure (Jan–Oct 2026) | TUNED v2 |
|---|---|
| Total | **+₹115,950.75** |
| Legs | 59 |
| Distinct trade-days | 51 |
| **Average per trade-day** | **₹2,273.54** (bar: ≥ ₹900) |
| Average per leg | ₹1,965.27 |
| Average per calendar trading day (205) | ₹565.61 |
| Win rate (legs) | 59.3% |
| Target-hit rate (FT) | 44.1% |
| Trade-day frequency | 51 of 205 days (**24.9%**) |
| Trade-days ≥ ₹900 | 54.9% |
| Median trade-day | +₹2,753.75 |
| Worst / best trade-day | −₹5,295.50 / +₹11,155.00 |
| Losing trade-days | 17 of 51 |
| H1 (Jan–May), trade-day basis | +₹67,064.25 / 28 days = **₹2,395.15/day** |
| H2 (Jun–Oct), trade-day basis | +₹48,886.50 / 23 days = **₹2,125.50/day** |
| Red months (monthly net) | **none** |
| Red month-ends (cumulative) | **none** |
| Placebo (shift30, trade-day avg) | ₹1,559.25 — beaten |
| Placebo percentile (delay family 2–12 bars) | **100.0** (real average above all 10 placebos; family range ₹1,107.50–₹1,810.83) |
| Ex-top-3 trade-days | +₹82,485.75 → **₹1,718.45/trade-day** (still ≥ ₹900) |
| Ex-top-3 legs | +₹82,485.75 |
| Timing audit | 0 violations |
| Not-computed legs | 0 |
| Independent re-sum | exact |

Month table — TUNED v2 (₹; per-cal-day over that month's trading days,
per-trade-day over that month's trade-days):

| Month | Net | Cum | Legs | Cal days | Trade-days | ₹/cal-day | ₹/trade-day |
|---|---|---|---|---|---|---|---|
| Jan | +16,965.75 | +16,965.75 | 4 | 20 | 4 | 848.29 | 4,241.44 |
| Feb | +6,135.50 | +23,101.25 | 6 | 21 | 5 | 292.17 | 1,227.10 |
| Mar | +9,193.50 | +32,294.75 | 9 | 19 | 7 | 483.87 | 1,313.36 |
| Apr | +27,881.25 | +60,176.00 | 6 | 20 | 6 | 1,394.06 | 4,646.88 |
| May | +6,888.25 | +67,064.25 | 8 | 19 | 6 | 362.54 | 1,148.04 |
| Jun | +5,048.00 | +72,112.25 | 4 | 21 | 3 | 240.38 | 1,682.67 |
| Jul | +13,034.00 | +85,146.25 | 8 | 23 | 7 | 566.70 | 1,862.00 |
| Aug | +1,911.75 | +87,058.00 | 4 | 21 | 4 | 91.04 | 477.94 |
| Sep | +13,367.75 | +100,425.75 | 7 | 21 | 6 | 636.56 | 2,227.96 |
| Oct | +15,525.00 | +115,950.75 | 3 | 20 | 3 | 776.25 | 5,175.00 |

**The honest caveats, beside the pass (not under it):**
1. **v2 has NO November forward evidence.** Its November record is 0 legs
   on 0 trade-days (derivation below) — this pass is Jan–Oct gate evidence,
   an in-sample ceiling, not forward proof.
2. **The trade-day average coexists with silence:** v2 trades on only
   24.9% of days. On the calendar basis the same book is ₹565.61/day. The
   ₹900 figure is true exactly as the owner defined the basis — and only
   on that basis.

---

## TUNED v1 — clears the average, one gate leg fails (stated exactly)

TUNED v1 (EVE-07, the standing book) averages **₹1,561.37 per trade-day**
(74 legs, 66 trade-days, +₹103,050.25, win rate 51.4%) — comfortably above
₹900 — and passes every control recomputed on the trade-day basis:
placebo percentile 100.0 (shift30 ₹1,008.52, beaten), halves
₹1,376.82 (H1, 38 days) / ₹1,811.82 (H2, 28 days), ex-top-3 trade-days
₹1,104.53/day, timing audit clean, NC 0, re-sum exact, trade-day frequency
32.2%, median trade-day +₹246.88, worst −₹5,295.50.

**The one failing leg:** on the calendar basis, **March 2026 is a red
month for v1 (−₹1,216.50 monthly net)** — the same red month recorded in
its original gate. The Step-2 gate as specified requires no red month on
the calendar basis, so v1 does **not** pass as specified. (On the
cumulative month-END reading v1 has no red month-end — its cumulative
never goes negative; both readings are stated here, neither is hidden.)
v1's other months on the trade-day basis: Jan ₹2,588.54 · Feb ₹1,153.66 ·
Mar −₹121.65 · Apr ₹3,487.32 · May ₹623.43 · Jun ₹1,207.00 · Jul ₹1,046.30 ·
Aug ₹477.94 · Sep ₹2,227.96 · Oct ₹5,040.12.

**November forward evidence belongs to v1** (below) — it is the only
positive Nifty forward line of November.

## DEC-S1 — measured for completeness; cannot be the answer

97 legs, 88 trade-days, +₹91,168.50 → **₹1,036.01/trade-day** (clears the
average numerically), win rate 47.4%, placebo percentile 100.0, halves
₹907.87 / ₹1,204.61. But: **RETIRED** (proven B-PE leak: 23 legs
−₹11,881.75 Jan–Oct), **two red months** (Mar −₹11,846.50, Jun −₹1,331.00),
and its ex-top-3 trade-day average falls to **₹678.86 — below the bar**.
Excluded from the answer by the task's own terms.

---

## NOVEMBER FORWARD EVIDENCE (same basis, verified from the logs)

Source: `november_shadow_decs1_nifty_log.csv`, read row by row in this run.
November DEC-S1 legs: Nov 2 B PE −₹220.00 · Nov 3 B PE −₹3,470.00 ·
Nov 3 C CE **+₹3,036.50** · Nov 5 B PE −₹3,470.00 · Nov 11 B PE +₹3,680.00
(total −₹443.50, matches the tracker). The tuned books' November records
are drop-only derivations from these candle-scored legs:

| Book | Nov legs | Nov trade-days | Nov net | Nov ₹/trade-day |
|---|---|---|---|---|
| TUNED v1 | 1 (Nov 3 C CE) | 1 | **+₹3,036.50** | **+₹3,036.50** |
| TUNED v2 | 0 | 0 | ₹0 | — **no forward evidence** |

November held only B PE ×4 and C CE ×1 in the DEC-S1 population; v2's
defining rules drop both classes, so v2 took nothing. v1 keeps the C CE
leg — November's only Nifty winner.

## Bottom line

- **On the owner's ₹900-per-trade-day basis, Nifty PASSES — through
  TUNED v2: ₹2,273.54 per trade-day, every control leg green, no red
  month.** Its weakness is named, not buried: it has never traded in
  November (0 legs), and it trades on only ~1 day in 4.
- **TUNED v1 also beats the ₹900 average (₹1,561.37/trade-day)** and owns
  the only November forward evidence (+₹3,036.50 on 1 trade-day), but
  carries one red calendar month (March −₹1,216.50) and so does not pass
  the gate exactly as specified.
- Jan–Oct figures remain in-sample gate evidence (ceilings, not proof);
  the forward currency is November paper, where the score is: v1
  +₹3,036.50 · v2 ₹0/no trades. No book was armed, changed or added to by
  this verification.
