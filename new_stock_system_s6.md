# S6 — new stock system for the 1-valuable-stock-trade-per-day bar — IN-SAMPLE ONLY, NOT ADOPTED

**Date:** 2026-10-29 evening. **Paper only, no orders, cash intraday only, NO options.**
**Frozen spec (written before scoring):** `new_stock_system_s6_frozen.md`.
**Engine:** `stock_system_s6.py`. **Trades:** `s6_trades_jan_oct_2026.csv` (53),
uncapped `s6_uncapped_jan_oct_2026.csv` (78), month JSON
`data/progressive/s6_summary_2026-jan-oct.json`.
**Window:** Jan–Oct 2026, October = 1–28 Oct only, 25 stocks, 5,075 stock-days,
203 trading days. **All numbers below are in-sample context only.**
**Nothing in this report is adopted. No S6 November log was created, because S6
does not pass (see §4) — a failing in-sample system does not go on an
adoption-track November log.**

## 1. The user bar S6 was built for

Confirmed 2026-10-29 19:19 IST: **1 valuable STOCK trade per day, index separate.**
Index (Nifty (lA) / Bank V4) paper is separate and is never pooled into any
stock total below. Valuable = a convicted, high-return setup — not a tiny win,
not a partial-breakeven win counted as a win, and not a forced trade on a day
with no setup. A day with no valuable setup = no trade that day, reported honestly.

## 2. S6 design — the one structural change

S1–S5 used an OR-boundary stop (CE: OR low − 0.1%; PE: OR high + 0.1%). A CE
reclaim entering near the OR high therefore carried ≈ the whole OR width as
risk, while a PE bounce entering near the OR high carried almost none, so the
room filter (≥1.5× risk) systematically filtered CE trades out: S2 had 0 CE
trades out of 61; S3–S5 had 1 CE trade each.

**S6 stop (new, direction-symmetric retest-hold stop):**
- CE: stop = min(signal candle low, confirmation candle low).
- PE: stop = max(signal candle high, confirmation candle high).
- Risk = |entry − stop|; target = entry ± 2 × risk; give-back exit unchanged
  (50 shares at 1× risk, rest trailed to breakeven, square-off 15:10).
- Rationale: breach of that level invalidates the signal under the original
  Filter 4 (Retest Hold Confirmation). It is not the S1–S5 OR-boundary stop,
  and not the original cash `run_day` signal-candle-only stop (S6 uses signal
  AND confirmation candles).

Everything else is S2: setups 2/3/4 only, second-close confirmation, entry =
open of the candle after confirmation, room to the next PD level finite AND
≥ 1.5 × (new) risk, Nifty bias-only confirmation, prospective full-target net
≥ ₹500, 100 shares, ₹40/trade, 15:10 square-off, short paper-only.
**Cap changed to fit the new bar:** max 1 stock trade per trading day across
all 25 stocks, max 1/stock/week retained, ranking prospective target net DESC,
then room ratio DESC, then setup rank DESC. The cap is a ceiling, not a quota.

## 3. Results — Jan–Oct 2026 in-sample, capped

| Series | Trades | Win net>0 | Full-target rate | Net ₹ | Expectancy ₹ | Freq/day | Freq/week |
|---|---|---|---|---|---|---|---|
| **S6** | **53** | **45.3% (24)** | **17.0% (9)** | **−₹3,847.50** | **−₹72.59** | **0.26** | **1.20** |
| S2 (best kept) | 61 | 59.0% | 19.7% (12) | −₹785.98 | −₹12.88 | 0.30 | 1.39 |
| S1 | 18 | 50.0% | 22.2% (4) | −₹1,875.94 | −₹104.22 | 0.09 | 0.42 |
| V4 stocks (capped-v2) | 132 | — | 22.7% | −₹17,435 | −₹132 | — | ~3.0 |
| Skill stocks (capped-v2) | 143 | — | 22.4% | −₹21,835 | −₹153 | — | ~3.3 |

S6 is **worse than S2 on every headline metric** — net, expectancy, win rate,
full-target rate and frequency — despite being the first version to produce
CE trades in number. The net>0 rate (45.3%) is not comparable to old target
rates: 15 of the 24 net-positive trades are partial-breakeven wins
(partial 50 at 1× risk, rest stopped at breakeven = small positive after cost).
Full-target rate (17.0%) is the comparable figure.

### Days: the frequency shortfall is candidate scarcity, NOT the cap

- Trading days in window: **203**. Days traded: **53**. Days with at least one
  uncapped candidate: **54**. Days with **no valuable setup: 149**.
- Uncapped candidates: 78, capped trades: 53, capped-out trades: 25 — but
  those 25 were on days that already traded, so the 1/day cap cost only
  **1 extra trading day**. S6 does not fail frequency because the cap binds;
  it fails because only 54 of 203 days produce a candidate passing every
  filter, and no trade was forced on the other 149 days (correctly, per the bar).
- Exits (capped): 27 stops, 15 stops-after-partial-BE, 9 targets-after-partial,
  2 square-offs. No full target was reached without a partial first, as in S1–S5.

### Setup / direction split — CE appears, setup2 does not

| Split | Capped | Uncapped |
|---|---|---|
| setup3 bounce rejection PE | 46 | 70 |
| setup4 reclaim CE | 7 | 8 |
| setup2 breakout/breakdown (either direction) | 0 | 0 |
| setup4 pullback CE | 0 | 0 |

- CE leg (capped): 7 trades, **net −₹2,980.00, 0 full targets**, 1 partial-BE,
  5 stops, 1 square-off loss. Uncapped CE: 8 trades, 0 full targets, 5 stops.
  The new stop rescued CE *presence* but not CE *profitability*: the
  signal/confirmation-low stop is so tight that CE trades are noise-stopped
  before they can reach 2× risk. Example CE candidates: GODREJCP 30 Jan
  (risk ₹7.90, stop −₹830), KALYANKJIL 26 Oct (risk ₹7.00, stop −₹740),
  HINDALCO 6 Mar (risk ₹8.00, the only CE partial-BE win, +₹360).
- PE leg (capped): 46 trades, net −₹867.50, 9 full targets, 14 partial-BE.
  PE alone is near breakeven; CE is what drags S6 below S2.
- Setup2 produces signals in the raw funnel (see below) but **zero** uncapped
  candidates under S6 — second-close, room and Nifty filters kill every one,
  as in S2–S5. S6 therefore does not solve setup2 at all.

### Filter funnel (5,075 stock-days)

| Stage | S6 | S2 (comparison) |
|---|---|---|
| Stock-days scanned | 5,075 | 5,075 |
| OR filter passed | 4,859 | 4,859 |
| Old V4 signal found | 910 | 910 |
| Second-close passed | 443 | 443 |
| Finite room ≥1.5× risk passed | 237 | 179 (≥1.5× on OR-boundary risk) |
| Nifty bias-only passed | 203 | 167 |
| Prospective target ≥ ₹500 | 78 | 74 |
| After cap (S6: 1/day; S2: 3/week) | 53 | 61 |

The new stop did widen the funnel (room 179 → 237, Nifty 167 → 203), but the
extra candidates were mostly losing CE trades and extra PE stops, not edge.
Funnel widening, again, is not edge.

### Month-by-month net ₹ (capped) — cumulative does NOT rise

| Month | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|
| Jan | 6 | +₹2,130.00 | +₹2,130.00 |
| Feb | 8 | −₹1,870.00 | +₹260.00 |
| Mar | 7 | −₹710.00 | −₹450.00 |
| Apr | 6 | −₹735.00 | −₹1,185.00 |
| May | 2 | −₹165.00 | −₹1,350.00 |
| Jun | 6 | −₹1,260.00 | −₹2,610.00 |
| Jul | 4 | +₹885.00 | −₹1,725.00 |
| Aug | 8 | −₹635.00 | −₹2,360.00 |
| Sep | 3 | −₹445.00 | −₹2,805.00 |
| Oct (1–28) | 3 | −₹1,042.50 | −₹3,847.50 |

Ex-March net: −₹3,137.50. Ex-October net: −₹2,805.00. S6 is not carried by
March or October alone — it is negative with either month removed, and its
cumulative falls from January onward with only July interrupting the decline.

### Per-stock (capped, trades > 0 only)

| Stock | Trades | Net>0 | Full targets | Net ₹ |
|---|---|---|---|---|
| GLENMARK | 5 | 4 | 2 | +₹1,370.00 |
| OBEROIRLTY | 3 | 2 | 1 | +₹1,220.00 |
| ASTRAL | 8 | 5 | 2 | +₹600.00 |
| HINDALCO | 5 | 3 | 2 | +₹440.00 |
| HINDUNILVR | 1 | 1 | 0 | +₹185.00 |
| HINDZINC | 2 | 1 | 0 | −₹245.00 |
| HDFCBANK | 1 | 0 | 0 | −₹315.00 |
| BDL | 8 | 3 | 1 | −₹465.00 |
| HINDCOPPER | 2 | 0 | 0 | −₹685.00 |
| KALYANKJIL | 1 | 0 | 0 | −₹740.00 |
| GODREJCP | 5 | 2 | 0 | −₹1,222.50 |
| UNITDSPR | 5 | 1 | 0 | −₹1,595.00 |
| TVSMOTOR | 7 | 2 | 1 | −₹2,395.00 |

Zero-trade stocks in S6 (12): INDUSTOWER, IRCTC, ITC, NATIONALUM, NHPC, NTPC,
OIL, PFC, RECLTD, TATASTEEL, VEDL, WIPRO. S1-zero-stock trades in S6: 5 trades,
same 4 symbols as S2–S5 (HDFCBANK, HINDCOPPER, HINDUNILVR, KALYANKJIL) — the
other 10 S1-zero stocks still never trade.

## 4. Judgement against the new bar — S6 FAILS, all legs together

| Leg | Result |
|---|---|
| (a) Net positive in-sample | ✗ −₹3,847.50 (worse than S2's −₹785.98) |
| (b) Close to 1 valuable trade per trading day, no forced trades | ✗ 0.26/day; 53 traded days vs 149 no-valuable-setup days. No trades were forced — that part of the bar was honoured, and it is exactly why frequency is low. |
| (c) CE trades AND setup2/4 trades present | ✗ Partial only: setup4 CE present (7), but setup2 absent (0) and setup4 pullback absent (0). |
| (d) Full-target rate above S2's 19.7%, ideally above S1's 22.2% | ✗ 17.0%, below both. Partial-BE wins (15) shown separately, not counted as targets. |
| (e) Cumulative rising month by month, not March/October-carried | ✗ Falls Jan–Jun, never recovers; ex-March and ex-October both still negative. |

**Verdict: S6 FAILS. It is NOT adopted, and it does NOT go to November
adoption-track paper.** S2 remains the best kept stock version (least negative,
−₹785.98), itself not adopted. No November stock log is created from S6;
the existing `s2_forward_paper_log.csv` remains the diagnostic-only S2 template
from the previous round, and S6 must not be logged in its place without a
separate, explicit decision.

## 5. What S6 proved, and the S7 design to try next (NOT implemented here)

S6 proved the CE problem has two layers, not one:

1. **Stop asymmetry (fixed in presence, not in profit):** the OR-boundary stop
   did filter CE out; the retest-hold stop lets CE in (7 capped vs 0 in S2).
2. **Reclaim-chasing (not fixed):** entering at the open after a reclaim
   confirmation, with a stop just below the reclaim candles, means the trade
   starts at the top of the reclaim move with almost no pullback room — any
   normal pullback stops it out (5 of 8 CE candidates stopped, 0 full targets).
   The PE bounce trade does not have this problem, because its entry *is* the
   rejection — the move starts from the entry. The CE trade needs its own
   entry, not just its own stop.

**S7 design sketch (to be frozen in its own file before any scoring, not
implemented or scored in this report):** setup4 CE **only via a pullback entry**.
Trigger sequence, stated exactly so it can be frozen verbatim: (i) a setup4
reclaim close (as in `find_signal`) marks the day as reclaim-armed; (ii) the
entry triggers only on a later candle that dips toward the reclaimed level
(OR high, within the existing 40×scale tolerance used for setup4 pullback)
and then closes back above it, with the second-close rule applied to that
pullback candle; (iii) entry = open of the next candle; stop = pullback
candle low; room = distance from entry to the next PD level above, ≥1.5×
pullback risk; target = entry + 2× risk; give-back exit unchanged. PE trades
in S7 keep the S6 retest-hold stop (which did not damage PE: PE leg −₹867.50
on 46 trades, near breakeven). Setup2 remains a separate open problem: if
setup2 still yields zero candidates under S7, it should be reported as absent
rather than rescued by loosening room again, which has now failed in S2–S6
in every direction tried.

## 6. Comparison and guardrails kept

- S6 (−₹3,847.50) vs S1 (−₹1,875.94) vs S2 (−₹785.98, best kept) vs V4 stocks
  (−₹17,435) vs Skill stocks (−₹21,835), same Jan–Oct 2026 window. S6 beats
  only the old V4/Skill stock series on net; it loses to both S1 and S2.
- S6 was NOT re-tuned on this window after seeing its result, and no S6
  variant is claimed here. The S7 sketch in §5 is a proposal for a future
  frozen design, not a result.
- No orders, no live trading, no lot increase. Cash intraday only, no options:
  every net above is 100 shares × stock points minus ₹40/trade, NOT an option
  premium profit. Index and stock totals were never pooled; Nifty was a
  filter only, never traded in S6.
