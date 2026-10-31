# LINE STRESS-1 — HOW FRAGILE IS THE ALL-GREEN BOOK?

**Attack, not defence.** The user rejected the all-green milestone as "very
optimal" (too perfect = overfit). This line attacks the frozen incumbent with
five pre-declared robustness stresses. **Measurement only — no fixes, no new
rules, nothing re-tuned.** Paper only, real ₹0, provisional per 100 shares,
home 25, Jan–Oct 2026.

**Incumbent under attack** (from `stocks_engine_state.json`, rebuilt exactly
per the JN-1 recipe: INV-LONG + N4-V3 + P2F 2.5% + F4-minus-setup3 @ T150/S080,
RF-1 special-session stand-aside book-wide; exclusions: ASTRAL out of N4-V3/P2F,
HINDUNILVR out of P2F, BDL out of INV-LONG).

**Anchor: EXACT.** Rebuild = 906 trades, **+₹138,631.32**, month table identical
to the state file to the paisa (Jan +11,378.22 · Feb +5,125.86 · Mar +19,116.26 ·
Apr +1,464.36 · May +29,377.98 · Jun +172.76 · Jul +3,196.63 · Aug +185.69 ·
Sep +18,041.54 · Oct +50,572.02). Script: `stocks_STRESS1.py`; numbers:
`stocks_STRESS1_results.json`.

---

## STRESS 1 — COST SENSITIVITY (₹40 is an assumption; his real charges are unknown)

Every dump's net is after ₹40/trade (asserted on the F4 dumps: gross − net =
₹40.00 exactly). Higher cost subtracts the delta × trades (906 trades).

| Month | ₹40 (base) | ₹60/trade | ₹80/trade |
|---|---|---|---|
| Jan | +11,378.22 | +9,138.22 | +6,898.22 |
| Feb | +5,125.86 | +3,085.86 | +1,045.86 |
| Mar | +19,116.26 | +15,996.26 | +12,876.26 |
| Apr | +1,464.36 | **−775.64** | **−3,015.64** |
| May | +29,377.98 | +27,457.98 | +25,537.98 |
| Jun | +172.76 | **−1,287.24** | **−2,747.24** |
| Jul | +3,196.63 | +2,936.63 | +2,676.63 |
| Aug | +185.69 | **−454.31** | **−1,094.31** |
| Sep | +18,041.54 | +16,461.54 | +14,881.54 |
| Oct | +50,572.02 | +47,952.02 | +45,332.02 |
| **Total** | **+138,631.32** | **+120,511.32** | **+102,391.32** |
| **Months green** | **10/10** | **7/10** | **7/10** |

**Reading:** the *total* is not cost-fragile — doubling the assumed cost to
₹80/trade still leaves +₹102,391.32. The *all-green table* is: the same three
thin months (Apr, Jun, Aug) flip red already at ₹60. All-green is a ₹40-cost
artefact; a strongly positive book is not.

## STRESS 2 — CONCENTRATION (whose money is it?)

Full-period stock ranking, top of the table: **TVSMOTOR +₹61,717.72 (38 tr) =
44.5% of the entire book's profit**; GLENMARK +₹32,182.31 (57 tr); ASTRAL
+₹25,812.99 (40 tr). Top-3 together = **+₹119,713.02 = 86.4% of the total**,
from 135 of 906 trades.

| Book | Total | Months green | What breaks |
|---|---|---|---|
| Full book | +138,631.32 | 10/10 | — |
| ex-TVSMOTOR | +76,913.60 | **9/10** | June flips (−2,507.24); October halves to +23,803.90 |
| ex-TVSMOTOR + GLENMARK | +44,731.29 | **6/10** | Feb, Mar, Jun, Aug red |
| ex-top-3 (TVS + GLENMARK + ASTRAL) | +18,918.30 | **6/10** | Mar, May, Jun, Aug red |

**Reading:** removing TVSMOTOR alone does **not** kill the book (still
+₹76,913.60, 9/10 green) — but it kills the all-green claim via June and cuts
October below the ₹50,000 line the engine "secured". Remove the top three
stocks and the book is still positive (+₹18,918.30) but only 6/10 months
green. The profit pool is real but narrow: three stocks, one of them
(TVSMOTOR) carrying nearly half.

## STRESS 3 — EXCLUSION FRAGILITY (the three surgical fixes, split by half)

Each exclusion's removed trades, Jan–May vs Jun–Oct. A robust exclusion should
be negative in **both** halves; a one-half exclusion is a period patch.

| Excluded slice | Trades | Full period | Jan–May | Jun–Oct | Verdict |
|---|---|---|---|---|---|
| N4-V3 × ASTRAL | 2 (0 winners) | −₹1,611.45 | −₹777.50 (1 tr) | −₹833.95 (1 tr) | Negative both halves — but **1 trade per half** |
| P2F × ASTRAL | 2 (0 winners) | −₹1,592.10 | −₹756.10 (1 tr) | −₹836.00 (1 tr) | Negative both halves — but **1 trade per half** |
| P2F × HINDUNILVR | 2 (0 winners) | −₹2,294.05 | −₹1,194.05 (1 tr, Feb) | −₹1,100.00 (1 tr, Jul) | Negative both halves — but **1 trade per half** |
| INV-LONG × BDL | 22 (6 winners) | −₹1,486.93 | **+₹1,089.37 (18 tr)** | **−₹2,576.30 (4 tr)** | **CARRIED BY ONE HALF** |

**Reading:** plainly — three of the four exclusions rest on exactly **2 trades
each** (one per half). They point the same way in both halves, which is better
than a coin flip, but two trades cannot carry statistical weight; they are
judgement calls recorded as such. The fourth, BDL, is the weakest of all: over
the full 22 trades the slice *made* money in Jan–May (+₹1,089.37 — excluding it
**cost** the book in Jan, Feb and Mar) and only lost in Jun–Oct, where June's
green rests on 2 of those 4 H2 trades (−₹1,406.25). The BDL exclusion is a
second-half patch wearing a full-period label (−₹1,486.93 nets a +₹1,089 /
−₹2,576 split).

## STRESS 4 — THIN-MONTH REALITY (June, August, April)

| Month | Book | Trades | Best single trade | Best-trade share | Month without its best trade |
|---|---|---|---|---|---|
| June | +₹172.76 | 73 | GLENMARK, P2F, 2 Jun: +₹2,733.37 | 1,582% of the month | **−₹2,560.61** |
| August | +₹185.69 | 32 | GLENMARK, N4-V3, 20 Aug: +₹2,807.11 | 1,512% of the month | **−₹2,621.42** |
| April | +₹1,464.36 | 112 | GLENMARK, INV-LONG, 7 Apr: +₹2,590.50 | 177% of the month | **−₹1,126.14** |

**Reading:** all three "green" thin months are **one trade deep** — remove the
single best trade and each is red. All three best trades are the same stock
(GLENMARK, the book's #2 earner). June and August are not months the system
won; they are months where one GLENMARK trade outran ~30–70 other trades'
small net losses. April is broader (112 trades, 46 winners) but still flips
without its top trade.

## STRESS 5 — EXIT-PARAMETER NEIGHBOURHOOD (how much is OC-3 + OC-4?)

F4 restored to its **pre-tuning exits T125/S065** inside the otherwise-final
book (setup3 exclusion kept, everything else identical; 926 trades):

| | Final book (F4 @ T150/S080) | F4 @ original T125/S065 |
|---|---|---|
| Total | +₹138,631.32 | **+₹114,212.29** |
| Months green | 10/10 | **7/10** (Feb −860.84, Apr −5,628.81, Jun −863.79 red) |
| October | +₹50,572.02 | **+₹46,124.28 — below the ₹50k line** |
| F4 component | +₹79,547.71 | +₹55,128.68 |

**Reading:** the two exit steps chosen by the engine on this very window
(target 1.25→1.50%, stop −0.65→−0.80%) are worth **+₹24,419.03 — 17.6% of the
total — and 3 of the 10 green months**, including October's "secured" status
itself (at the original exits October is +₹46,124.28, under the goal). The
exit *direction* was diagnosis-led (stops were firing on dips that
mean-reverted), and the book at old exits is still strongly positive — but the
specific all-green configuration is partly a parameter choice made on the data
that judges it. (One honest counter-note: August was *better* at the old exits,
+₹2,534.93 vs +₹185.69 — the wider stop cost August; the tuning was not a
uniform improvement.)

---

## VERDICT — what survives, what breaks, and the honest split

**Survives every stress:** the book's *profitability*. At double the assumed
cost it still makes +₹102,391.32; with its three best stocks deleted it still
makes +₹18,918.30; with F4 back on its original exits it still makes
+₹114,212.29; with TVSMOTOR — 44.5% of the profit — removed entirely, it still
makes +₹76,913.60. No single stress turns the total negative or close to it.
The underlying streams (a state-gated morning-follow stream, a below-trend
long pool, two event-reaction streams) earn money on this window in a way that
does not depend on any one knob.

**Breaks under almost every stress:** the *all-green table itself* — the very
result presented as the milestone. At ₹60/trade it is 7/10. Without TVSMOTOR it
is 9/10 and October loses its ₹50k. Without the top-3 stocks, 6/10. At F4's
original exits, 7/10 and October is under goal. Three of its green months
(June, August, April) are each exactly one GLENMARK trade deep. And of the
four surgical exclusions that manufactured the last three green months, three
rest on 2 trades apiece and the fourth (BDL) was a money-maker in the first
half of the year — its exclusion is a Jun–Oct patch.

**The honest assessment:** the *total* is mostly structure — roughly ₹1.0–1.15
lakh of the +₹1.39 lakh survives cost doubling, exit reversion and
single-stock removal, because four genuinely different mechanisms contribute.
The *10/10* is mostly fit: the engine repaired the book month-by-month on the
same Jan–Oct window that now judges it, and the last mile of "every month
green" was paved with two exit steps worth 3 green months, four exclusions
resting on 2–22 trades (one of them single-half), and three months whose green
is one trade thick. Treat the book as a real, profitable-in-sample system with
a fragile perfect record — the correct next judge is fresh data (November
paper, then the frozen December test), not another in-sample repair.
