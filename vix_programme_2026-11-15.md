# VIX PROGRAMME (2026-11-15)

**Owner order 2026-11-15: work on VIX-related strategies.** Spec
frozen in `vix_programme_SPEC.md` before scoring. Research only —
nothing armed. **Option buying only. Paper only, real money ₹0.**
Index figures are option premiums per 1 lot (Bank 30 / Nifty 65),
cost ₹220/trade.

**India VIX source:** the Round-2 dataset
`round2_history/india_vix_daily.csv` (Yahoo Finance `^INDIAVIX`
published daily closes, as documented in
`new_data_round2_2026-11-13.md`). Coverage 2025-12-22 → 2026-11-11;
203 of 205 Jan–Oct trading days carry a close — missing 2026-01-01
and 2026-02-01, never filled.

Machinery note: the Upstox token in the store had expired at
2026-11-14 22:00; the programme's own `auto_token_refresh.py`
restored it before scoring (expires 2026-11-15 22:00). No 429 was hit.

---

## PART A — ANATOMY: the running books by prior-day VIX band

Stored Jan–Oct legs split by the **prior trading day's** India VIX
close. Anchors re-verified at load: Bank TUNED STACK v2 = 111 legs,
**+₹127,351.50**; Nifty TUNED v1 = 74 legs, **+₹103,050.25**. One leg
per book (2026-02-02, whose prior day 2026-02-01 has no VIX close) is
NC and excluded from the bands — Bank −₹1,720, Nifty −₹3,470; band
sums + NC leg = book totals exactly.

### Bank TUNED STACK v2

| Prior-day VIX | Legs | Net (₹) | WR | ₹/trade-day |
|---|---|---|---|---|
| <12 | 19 | +25,544.00 | 68.4% | +1,596.50 |
| 12–14 | 35 | +37,588.00 | 48.6% | +1,342.43 |
| 14–17 | 19 | +35,829.50 | 78.9% | **+2,107.62** |
| 17–20 | 18 | +20,790.00 | 61.1% | +1,386.00 |
| >20 | 19 | +9,320.00 | 52.6% | +776.67 |

**No band bleeds.** Best band: **14–17** (₹2,107.62/trade-day, WR
78.9%). Weakest band: **>20** (+₹776.67/trade-day — still positive;
this is the same +₹9,320 high-VIX residue Round 2 measured
independently). The stack earns in every VIX state; it earns least
when VIX is already extreme.

### Nifty TUNED v1

| Prior-day VIX | Legs | Net (₹) | WR | ₹/trade-day |
|---|---|---|---|---|
| <12 | 18 | +38,478.50 | 61.1% | **+2,404.91** |
| 12–14 | 22 | +17,728.00 | 50.0% | +886.40 |
| 14–17 | 8 | +15,595.00 | 50.0% | +2,227.86 |
| 17–20 | 15 | +20,714.25 | 53.3% | +1,479.59 |
| >20 | 10 | +14,004.50 | 40.0% | +1,750.56 |

**No band bleeds.** Best band: **<12** (₹2,404.91/trade-day).
Weakest band: **12–14** (+₹886.40/trade-day — positive, roughly a
third of the best band's rate). TUNED v1 earns in every VIX state,
most in calm sub-12 conditions.

**Plain statement:** for both running books, every prior-day VIX
band earns and none bleeds. VIX level does not separate the books'
good days from bad days — the weakest bands (Bank >20, Nifty 12–14)
are still worth +₹777 to +₹886 per trade-day.

---

## PART B — TWO STANDALONE VIX-TRIGGERED BUYING RULES

Construction (frozen): signal at day D's close; entry next trading
day at the open of the 09:20 bar; ATM strike to that bar's spot open
(Bank step 100 / Nifty step 50); in-force expiry (Bank monthly /
Nifty weekly-front); exits stop −50 before target +90 on every bar,
square-off 15:20; 1 lot; ₹220/trade. NC = 0 in all four cells —
every signal was constructible.

### V1 — LOW-VIX TREND BUY (VIX close < 12 AND spot close above its 20-day average → buy CE next day)

**Bank: 27 trades, −₹32,391.00, WR 11.1% — FAIL.**
Halves: Jan–May −₹15,951.00 / Jun–Oct −₹16,440.00. Ex-top-3
−₹39,831.00. Placebo **0.0th percentile** (random-entry median
−₹8,640.00 — the rule lost more than every one of the 200 random
draws). Months: Jan 11t −₹10,520 · Feb 4t −₹5,431 · Jul 3t −₹5,160 ·
Aug 8t −₹9,560 · Sep 1t −₹1,720. Failing legs: total ≤ 0, Jan–May
half ≤ 0, Jun–Oct half ≤ 0, ex-top-3 ≤ 0, placebo < 95th.

**Nifty: 18 trades, −₹28,179.00, WR 27.8% — FAIL.**
Halves: Jan–May −₹21,398.75 / Jun–Oct −₹6,780.25. Ex-top-3
−₹33,180.50. Placebo 12.5th percentile (median −₹11,834.75).
Months: Jan 5t −₹11,847.75 · Feb 4t −₹9,551.00 · Jul 3t −₹5,093.00 ·
Aug 6t −₹1,687.25. Failing legs: all five.

The calm-VIX uptrend state is real (Part A shows the incumbents earn
their best Nifty rate there) — but a blind next-morning ATM CE buy
in that state is not the way to harvest it: the bought premium
decays/stops out (Bank WR 11.1%) while the incumbents' edge comes
from their own intraday entries.

### V2 — VIX-SPIKE FADE (VIX +≥15% in a day AND spot −≥1% that day → buy CE next day; first day of a spike run only)

**Bank: 6 trades, −₹6,120.00, WR 16.7% — FAIL.**
Halves: Jan–May −₹2,680.00 / Jun–Oct −₹3,440.00. Ex-top-3
−₹5,160.00. Placebo 30.0th percentile (median −₹1,920.00). Months:
Mar 4t −₹2,680 · Jul 1t −₹1,720 · Sep 1t −₹1,720. Failing legs:
all five.

**Nifty: 6 trades, −₹1,271.25, WR 50.0% — FAIL.**
Halves: Jan–May −₹473.75 / Jun–Oct −₹797.50. Ex-top-3 −₹9,188.00
(the small total leans on its top trades). Placebo 63.5th
percentile (median −₹3,760.75). Months: Mar 4t −₹473.75 · Jul 1t
−₹2,248.00 · Sep 1t +₹1,450.50. Failing legs: all five.

Only 6 spike events per index fired in Jan–Oct — the sample is
thin — and even so both are negative in both halves. The next-day
reversal after a fear spike did not pay for the bought CE premium.

---

## VERDICT

- **Part A:** neither running book has a VIX band that bleeds.
  Bank's best band is 14–17, weakest >20 (still +₹777/trade-day).
  Nifty's best band is <12, weakest 12–14 (still +₹886/trade-day).
  A VIX-level filter on the incumbents has nothing to cut.
- **Part B: V1 FAIL on both indices. V2 FAIL on both indices.**
  Every gate leg fails in all four cells. Per the frozen spec,
  neither rule is retested in this programme.

Files: `vix_programme_SPEC.md` · `vix_programme_score.py` ·
`vix_programme_results.json` · `vix_programme_trades.csv`
(57 scored trades).
