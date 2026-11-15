# NOVEMBER REGIME FIX — 2026-11-14

**Owner order (2026-11-14 06:52 IST): no deferrals. November is a
new scenario — a regime — and the fix work targets the regime.
Run to completion today. This is that run's finished report, pass
or fail.**

**Real money: ₹0. No live trades were placed; nothing was armed,
merged into, or modified in any running book, job or ledger.**
Every figure below is paper/backtest on option premiums **per 1
lot** (Bank Nifty lot 30, Nifty lot 65), cost **₹220/trade** inside
every net, UNIQUE-ONCE counting, option BUYING only. Indices are
reported separately and never pooled. Incumbent for every Bank
merge: **TUNED STACK v2 — 111 legs, +₹127,351.50, 89 trade-days,
₹1,430.92/trade-day (Jan–Oct 2026, 205 trading days)**. November
baseline (Nov 2–13, 9 trading days): stack **−₹2,680,
1 green / 3 red / 5 no-trade**.

---

## PHASE A — DATA: COMPLETE

Both builds ran sequentially in one fresh attempt. **No HTTP 429
recurred.** One infrastructure interruption: the first IOI build
process died at 1,112/1,204 chunks on a dropped connection
(`RemoteDisconnected`, not a rate limit) during a runtime restart;
the resumable build was re-run from its checkpoint and completed.

| Build | Result |
|---|---|
| `round5_ioi_build.py` | **1,204/1,204 chunks.** Dataset: Jan–Oct **187 complete days + 18 NC_BAND** (genuinely band-incomplete in the source; Jan 1, Feb 3, Mar 2, Apr 4, May 4, Jun 2, and 2 more in Jul–Oct); November **7 complete** (Nov 2, 3, 4, 5, 6, 9, 12), Nov 11 **NC_BAND**, Nov 13 **NC_NO_SPOT** (its 10:55 spot bar was never served — never estimated) |
| `round5_data_build.py` | **1,100/1,100 contracts.** `morning_flow.csv`: 214 rows, **195 complete** (187 Jan–Oct + 8 November; November's only incomplete day is Nov 11) |

Phase A's verdict: the full Jan–Oct window exists for every gate
below. Nothing in Phases B–D is a partial-window read.

---

## PHASE B — THE FROZEN GATES

### B0 — A scorer defect, disclosed before any FLOW-VOL/OPT-FLOW number

The frozen `round5_score.py` was run first, exactly as written. It
returned **0 legs for both families** — not a result but an
instrument defect: the freeze's NC rule requires "≥60 bars inside
11:00–15:10", and that window contains **at most 51 five-minute
bars** (11:00→15:10 = 250 minutes). As written, every fired day is
NC by construction (FLOW-VOL's 62 signal days all landed in its NC
list). The operative run is `round5_score_fixed.py` — byte-identical
except the 60-bar completeness floor is applied to the traded
contract's **full day** (75–77 bars when complete; the 11:00 and
15:10 bars remain required), which is the freeze's evident intent.
Signal rules, geometry, gate legs, seeds: untouched. The families'
verdicts below rest on the corrected run; the defect and the
correction are recorded here so the evidence is auditable.

### B1 — IOI-1 (Part 7 primary: morning OI build-up continuation) — **GATE FAIL, decisive**

143 legs · **−₹65,321.00** · −₹456.79/leg · win rate 30.8%.
Months: Jan +₹10,469.00 · Feb −₹1,647.00 · Mar −₹9,000.00 ·
Apr −₹4,800.00 · May −₹15,680.00 · Jun −₹6,520.00 · Jul −₹12,342.00 ·
Aug −₹16,644.00 · Sep −₹2,837.00 · Oct −₹6,320.00 (one positive
month in ten). Halves (median split 2026-06-04): **−₹19,898.00 /
−₹45,423.00**. Ex-top-3 **−₹72,761.00**. Placebos all beat it:
REVERSED −₹23,009.30 · COIN −₹27,468.80 · TIME-SHIFTED (12:00)
−₹26,751.50. Timing audit 0 violations; scoring-NC 0; re-sum EXACT.
**Killing legs: total, both halves, ex-top-3, and all three
placebos.** Day counts: 44 green / 99 red over 143 trade-days.
The Jan–Jun partial read (−₹27,178) was not a window artefact —
the full window is worse. IOI-1 is closed, never to be retested
identically. (Supplementary merge arithmetic, not the registered
merge: its 86 legs on stack-idle days total −₹59,681.00 — it would
drag the stack to ₹67,670.50.)

### B2 — IOI-2 (Part 7 variant: writer-squeeze) — **GATE FAIL**

21 legs · **−₹10,006.50** · −₹476.50/leg · win rate 33.3%.
Months: Jan −₹5,160.00 · Feb +₹4,700.00 · Jun +₹2,480.00 ·
Jul −₹3,440.00 · Aug −₹3,226.50 · Sep −₹3,440.00 · Oct −₹1,920.00
(no legs Mar–May). Halves: **−₹460.00 / −₹9,546.50**. Ex-top-3
**−₹17,446.50**. Placebos: REVERSED −₹9,949.50 (beats the real book
by ₹57.00), COIN −₹4,836.00 (beats it), TIME-SHIFTED **+₹9,727.50**
(beats it by ₹19,734.00 — delaying this family's entry an hour
turns it positive, which kills its late-morning-window claim
outright). Timing 0; NC 0; re-sum EXACT. **Killing legs: total,
both halves, ex-top-3, all three placebos.** Day counts:
7 green / 14 red over 21 trade-days. The Jan–Jun partial-window
+₹2,020 (8 legs) did not survive contact with Jul–Oct. IOI-2 is
closed.
**Registered merge (strongest failing family, merge-only
evidence): FAIL** — increment 12 legs on stack-idle days
**−₹6,106.50** → merged ₹121,245.00 on 101 trade-days
(₹1,200.45/trade-day) vs the stack's ₹127,351.50; merged day
counts 64 G / 37 R / 104 NT vs the stack's 60 / 29 / 116.

### B3 — FLOW-VOL (futures volume thrust ≥1.25× + basis direction) — **GATE FAIL, decisive**

62 legs · **−₹44,294.00** · **−₹714.42/trade-day** · win rate 25.8%.
Months: Jan −₹7,281.00 · Feb −₹7,547.00 · Mar −₹1,920.00 ·
Apr −₹960.00 · May −₹6,880.00 · Jun −₹6,633.00 · Jul −₹2,880.00 ·
Aug +₹560.00 · Sep −₹2,153.00 · Oct −₹8,600.00 (one positive month
in ten). Halves: **−₹24,588.00 / −₹19,706.00**. Ex-top-3
**−₹51,734.00**. Placebos: COIN percentile **5.5** (the real book
beats only 5.5% of coin draws — the placebo beats the book),
REVERSED −₹2,219.30, TIME-SHIFTED −₹43,308.50 (both beat it).
NC 0/205. Re-sum exact. **Killing legs: total and the ₹900/
trade-day leg, both halves, the month floor, ex-top-3, and all
three placebos.** Day counts: 16 green / 46 red / 143 no-trade.
**Merge: FAIL** — increment 40 legs on stack-idle days
**−₹21,230.50** → merged ₹106,121.00 on 129 trade-days
(₹822.64/trade-day); merged months gain a red June (−₹153.00);
merged day counts 72 G / 57 R / 76 NT.
**November counterfactual:** 3 legs, all on stack-idle days —
Nov 3 CE 55500 stop −₹1,720.00 · Nov 5 CE 57100 target +₹2,480.00 ·
Nov 11 CE 61100 target +₹2,480.00 → increment **+₹3,240.00**,
merged November **+₹560.00 (3 G / 4 R / 2 NT)** vs the stack's
−₹2,680 (1/3/5). The Phase-1 forensic observation was real —
thrust fired on three idle days and on no loss day, and those
three legs netted positive — but it is three legs against a
−₹44,294 ten-month record. It does not rescue the family.

### B4 — OPT-FLOW (band volume imbalance + premium confirmation) — **GATE FAIL**

37 legs · **−₹7,867.00** · **−₹212.62/trade-day** · win rate 37.8%.
Months: Jan +₹1,520.00 · Feb +₹2,693.00 · Mar +₹3,040.00 ·
Apr −₹6,880.00 · May −₹3,440.00 · Jun +₹760.00 · Jul −₹3,440.00 ·
Aug −₹4,400.00 · Sep +₹4,960.00 · Oct −₹2,680.00. Halves:
**−₹3,067.00 / −₹4,800.00**. Ex-top-3 **−₹15,307.00**. Placebos:
beats REVERSED (−₹18,052.30) only; COIN percentile 68.0 (< 95),
TIME-SHIFTED −₹3,851.50 beats it. **NC 18 days = 8.8% of 205 —
the NC leg also fails**, and 37 legs < the 40-trade minimum.
**Killing legs: total/₹900, minimum sample, NC, both halves,
month floor (Apr −₹6,880 < −₹5,000), ex-top-3, COIN,
TIME-SHIFTED.** Day counts: 14 green / 23 red / 168 no-trade.
**Merge: FAIL** — increment 20 legs **−₹11,207.00** → merged
₹116,144.50 on 109 trade-days (₹1,065.55/trade-day); merged
months gain a red August (−₹620.50); merged day counts
66 G / 43 R / 96 NT.
**November counterfactual:** family legs Nov 3 CE stop −₹1,720.00 ·
Nov 5 CE target +₹2,480.00 · Nov 12 CE stop −₹1,720.00 (family
total −₹960.00; Nov 11 NC — band incomplete); the Nov 12 leg falls
on a stack-busy day, so the increment is **+₹760.00** → merged
November **−₹1,920.00 (2 G / 4 R / 3 NT)**.

**Phase B summary: all four frozen families FAIL their gates —
IOI-1, FLOW-VOL decisively; IOI-2 and OPT-FLOW on nearly every
leg. No merge passes. The intraday-OI and flow surfaces, traded
as continuations at 11:00, are now closed on full-window
evidence.**

---

## PHASE C — THE REGIME SLICE: what makes money on November-shaped days?

**Definition (frozen from the failure audit's own measurements,
computed with its exact formulas, before slicing):** a Jan–Oct day
is **REGIME-LIKE** iff **(a)** its overnight |gap| sits in the top
quartile of the year's gaps (Bank: |gap| ≥ 0.586%; Nifty: ≥ 0.574%),
**or (b)** after 11:00 the spot moves ≥0.7% of the 11:00 close
**against** the morning (09:15–11:00) direction. Classification
reproduces the audit's published baselines exactly (Bank: 203
sessions, median |gap| 0.303%, reversal share 21.7%; Nifty: 203
sessions, 0.262%, 18.2%).

**Day counts:** Bank **79 regime-like of 203** (35 gap-only,
28 reversal-only, 16 both) vs 124 non-regime. Nifty **78 of 203**
(41 / 27 / 10) vs 125. **November density check: 6 of November's
9 Bank days are regime-like (Nov 2, 3, 5, 6, 9, 11) — a 67%
regime density against a 38.9% base rate.** The owner's framing
is measurable and correct: November is a regime-dense month.
(Nifty November days cannot be classified — Nifty intraday spot
bars were not persisted, the audit's H2 gap; stated, not
estimated. Two Jan–Oct programme days per index have <70 stored
spot bars and are unclassified; legs on them are counted
separately — Bank: one V3-increment leg, one IOI-1 leg.)

### Bank Nifty — slice of every book (legs on regime-like vs non-regime days)

| Book | Regime legs | Regime total | Regime days G/R | Non-regime legs | Non-regime total | Non-reg days G/R |
|---|---|---|---|---|---|---|
| **TUNED STACK v2** | 56 | **+₹68,669.50** | 30/12 (42 TD) | 55 | +₹58,682.00 | 30/17 (47 TD) |
| Legacy v21 frame | 55 | +₹41,226.50 | 26/22 (48 TD) | 44 | +₹42,424.00 | 23/21 (44 TD) |
| R4-D1 increment | 8 | **+₹7,240.00** | 5/3 | 19 | +₹1,733.00 | 8/11 |
| VIX-B1 increment | 5 | −₹200.00 | 2/3 | 7 | +₹4,760.00 | 4/3 |
| OI-V3 increment | 8 | −₹5,360.00 | 2/6 | 33 | +₹6,240.00 | 15/18 |
| OPT-FLOW | 15 | −₹600.00 | 6/9 | 22 | −₹7,267.00 | 8/14 |
| IOI-2 | 1 | −₹1,720.00 | 0/1 | 20 | −₹8,286.50 | 7/13 |
| FLOW-VOL | 28 | −₹16,747.00 | 8/20 | 34 | −₹27,547.00 | 8/26 |
| IOI-1 | 59 | −₹32,462.00 | 17/42 | 83 | −₹31,139.00 | 27/56 |

### Nifty — slice (stored legs only)

| Book | Regime legs | Regime total | Regime days G/R | Non-regime legs | Non-regime total | Non-reg days G/R |
|---|---|---|---|---|---|---|
| **TUNED v1** | 39 | **+₹42,526.25** | 19/12 (31 TD) | 35 | +₹60,524.00 | 18/17 (35 TD) |
| DEC-S1 (control) | 62 | +₹30,644.50 | 27/26 (53 TD) | 35 | +₹60,524.00 | 18/17 (35 TD) |

A cross-check falls out of the Nifty slice: DEC-S1 minus TUNED v1
on regime days = **−₹11,881.75, exactly the proven Jan–Oct B-PE
leak**, and ₹0.00 on non-regime days. The entire B-PE leak lives
on regime-like days — the slice independently re-derives it.

### The Phase C answer

**On Jan–Oct evidence, nothing in the tested set beats the
incumbents on November-shaped days — because the incumbents do
not fail on those days in general.** The stack earns
+₹68,669.50 on regime-like days (₹1,634.99/trade-day, 30 G / 12 R)
— *better* per trade-day than its own non-regime rate
(₹1,248.55). TUNED v1 likewise earns on both day types. What
November did was concentrate: two-thirds of its days drew the
regime class, and the specific legs the stack drew inside it
(PE into up-reversals, H4 of the audit) lost. That is a hostile
draw inside a class the books normally profit from — not a class
they are blind to. Of the fragments, only the **R4-D1 increment
is positive on regime days** (+₹7,240.00 on 8 legs, 5 G / 3 R);
V3's and B1's merge value lives on non-regime days. Every new
family from Phases B and D's surface work loses on regime days,
several catastrophically (IOI-1 −₹32,462; FLOW-VOL −₹16,747).

---

## PHASE D — ONE REGIME-NATIVE FAMILY: REGIME-REV v1

### The mechanical-difference judgement (written first, as required)

The closed afternoon family is: BREAK-CAPTURE v1 (opening-range
break capture, re-entry and hold-60 forms — Bank −₹10,018.80 /
−₹14,136.80), BANK-APC v1 (afternoon pullback-continuation —
−₹15,385.00), Nifty EVE-12 (first fresh day-range break after
12:30 — −₹100,604.40), and Bank EVE-06(b) (standalone afternoon
break entry, gate-rejected). **Every one of them buys the side
the market is already moving toward in the afternoon** — a break
in the break direction, or a pullback inside an established trend
in the trend direction. EVE-06(a), the other adjacent
construction, re-enters a *stopped* leg on its *own* side after a
reclaim of the morning extreme — same-side, post-stop,
book-attached.

REGIME-REV differs on four mechanical axes, not on settings:
**(1) Side** — it buys *against* the morning direction, the side
no closed construction ever bought as its real rule (fading
appeared only as EVE-12's Nifty *placebo*, +₹21,410.00, recorded
as an observation and explicitly not a candidate; a placebo is a
control, not a construction — it carried no regime conditioning,
no confirmation event, and afternoon-break timing). **(2)
Trigger** — not a break and not a pullback: a spot **close back
through the morning range midpoint**, i.e. a retracement of at
least half the morning range, an event none of the closed family
used. **(3) Conditioning** — it fires only on regime mornings
(top-quartile gap or ≥0.7% morning thrust, both knowable by
11:00); the closed family had no morning conditioning at all.
**(4) Attachment** — standalone; it does not need a stopped leg
or any book state. **Judgement: mechanically distinct. Scored.**

### The freeze (written in the scorer before the run)

Morning = spot bars 09:15–10:55; O = 09:15 open, C11 = 10:55
close, H/L = morning high/low, M = (H+L)/2, direction =
sign(C11−O) (zero → no trade). Gap% vs the prior session's close
(audit convention). **Regime morning:** |gap%| ≥ the index's own
Q3 (Bank 0.586, Nifty 0.574 — the Phase C constants) **or**
|morning move| ≥ 0.7%. **Confirmation:** the first spot bar in
[11:00, 15:05] whose close crosses M against the morning
direction. **Entry at that bar's close**; side = reversal side
(up-morning → PE, down-morning → CE); strike = ATM (Bank step
100, Nifty step 50) to the confirmation bar's spot close;
contract = in-force monthly expiry. **Exits** from the bar
*after* the confirmation bar (the fill is at its close; its own
high/low precede the fill and are never used): stop −50 checked
before target +90 per bar, fills at the level; else the 15:10
bar close. 1 lot; ₹220/trade; buying only; ≤1 leg/day. Premium
series must start ≤09:20 and contain the 15:10 bar, else NC.
**Placebos:** P1 = the identical logic on NON-regime mornings;
P2 = regime days, same confirmation event, the *morning* side
bought; P3 = regime days, entry at the close 30 minutes after
confirmation, same contract. **Gate:** total > 0; both halves
(Jan–May / Jun–Oct) > 0; ex-top-3 > 0; beats all three placebos
on total and P1 on per-leg average; timing audit 0; scoring-NC
≤ 5% of fired days; independent re-sum exact. Then the merge
test vs the stack and the November counterfactual. The owner's
₹900/trade-day figure is stated beside the verdict as a lens,
not a gate leg (per this run's brief).

### Bank Nifty — STANDALONE GATE: PASS (stage pass). MERGE: FAIL.

31 legs on 31 trade-days · **+₹15,872.00** · **₹512.00/trade-day** ·
win rate 51.6% · 16 green / 15 red days · NC **0 of 31 fired**.

| Gate leg | Result |
|---|---|
| Total > 0 | ✅ +₹15,872.00 |
| Halves | ✅ Jan–May **+₹15,240.00** (18 legs) · Jun–Oct **+₹632.00** (13 legs) — positive, but H2 is thin: 4.0% of the total |
| Ex-top-3 | ✅ +₹8,432.00 |
| P1 non-regime placebo | ✅ −₹9,767.50 on 88 legs (−₹110.99/leg vs the real book's +₹512.00/leg) — the same confirmation logic *loses* on non-regime days; the conditioning carries the edge |
| P2 flip (morning side) | ✅ −₹17,636.50 |
| P3 delay +30 min | ✅ beaten on total (+₹8,345.00) — but P3 is itself positive, and its H2 is −₹2,695.00: the edge decays with delay rather than vanishing, stated plainly |
| Timing audit | ✅ 0 violations by construction (condition inputs ≤ 10:55; the fill is the confirmation bar's close; exits strictly after it) |
| NC | ✅ 0% |
| Re-sum | ✅ EXACT from `november_regime_family_trades.csv` |

Months: Jan +₹760.00 · Mar −₹3,640.00 · Apr +₹8,200.00 ·
May +₹9,920.00 · Jun −₹4,400.00 · Jul +₹1,792.00 · Sep +₹3,240.00 ·
(no fired-and-confirmed days in Feb, Aug, Oct).
**The ₹900 lens, stated beside the pass as required: ₹512.00 per
trade-day is BELOW the owner's ₹900/trade-day bar.** This is a
gate pass on this run's frozen legs, at a per-day rate the owner
has previously set as his minimum average — both facts stand.
**Merge test: FAIL.** Only 15 of its 31 legs fall on stack-idle
days, and those total **−₹2,808.00** → merged ₹124,543.50
(65 G / 39 R / 101 NT) vs the stack's ₹127,351.50 (60/29/116).
REGIME-REV's profit concentrates on days the stack already
trades (+₹18,680.00 of its total sits on stack-busy days). It is
**not** a stack add-on. As a standalone it is a candidate for the
owner's decision — nothing is armed by this report.

### Nifty — NOT GATEABLE on stored data (NC, not estimated)

The identical frozen spec was run. Of 38 fired regime mornings,
**only 3 legs could be scored** (Jun +₹8,890.75 · Jul −₹2,410.50 →
+₹6,480.25, 2 G / 1 R); the other 35 fired days are NC —
the stored Nifty premium series (monthly-expiry stores) either
lack the confirmation-strike contract or start after 09:20
(114 NC attempts across the real book and placebos; P1 likewise
scored only 10 of 89). Three legs are not a gate. **Verdict:
INSUFFICIENT DATA — the family is neither passed nor failed on
Nifty.** Bank's data supported the attempt (C5 store, 0 NC);
Nifty's stores do not. No figure is estimated.

### REGIME-REV November counterfactual (Bank, day by day)

| Day | Leg | Result |
|---|---|---|
| Nov 2 | PE 54900, confirmed 11:00, entry 688.35 | target 778.35 → **+₹2,480.00** |
| Nov 3 | PE 55300, confirmed 14:50, entry 677.20 | square-off 647.90 → **−₹1,099.00** |
| Nov 5 | CE 57100, confirmed 11:00, entry 709.50 | target 799.50 → **+₹2,480.00** |
| Nov 11 | PE 60700, confirmed 13:30, entry 822.00 | stop 772.00 → **−₹1,720.00** |
| Nov 4, 6, 9, 12, 13 | no leg (no regime morning and/or no confirmation) | — |

Family November total **+₹2,141.00** (4 legs, 2 G / 2 R days).
All four legs fall on stack-idle days, so the increment is the
full +₹2,141.00 → **merged November −₹539.00 (3 G / 5 R / 1 NT)**
vs the stack's −₹2,680 (1/3/5). An improvement, not a rescue:
the merged November is still negative.

---

## NOVEMBER COUNTERFACTUALS — ALL FAMILIES (Bank; stack baseline −₹2,680 · 1 G / 3 R / 5 NT)

| Line | Family Nov legs | Increment on stack-idle days | Merged November | Merged days G/R/NT |
|---|---|---|---|---|
| Stack alone | — | — | **−₹2,680.00** | 1/3/5 |
| + IOI-1 (gate-dead; arithmetic only) | 6 legs, +₹2,280.00 (Nov 2 +2,480 · Nov 3 −1,720 · Nov 4 −1,720 · Nov 5 +2,480 · Nov 6 +2,480 · Nov 12 −1,720; Nov 9 no fire; Nov 11 NC_BAND; Nov 13 NC_NO_SPOT) | +₹5,720.00 (its two stack-busy-day legs, Nov 4/12, were both stops) | **+₹3,040.00** | 4/4/1 |
| + IOI-2 | 0 legs | ₹0.00 | −₹2,680.00 | 1/3/5 |
| + FLOW-VOL (gate-dead) | 3 legs, +₹3,240.00 | +₹3,240.00 | **+₹560.00** | 3/4/2 |
| + OPT-FLOW (gate-dead) | 3 legs, −₹960.00 (Nov 11 NC) | +₹760.00 | −₹1,920.00 | 2/4/3 |
| + REGIME-REV (standalone pass, merge fail) | 4 legs, +₹2,141.00 | +₹2,141.00 | −₹539.00 | 3/5/1 |

Read this table with its labels on: the two lines that turn
November positive (IOI-1, FLOW-VOL increments) belong to families
whose ten-month gates failed decisively — November arithmetic on
gate-dead families is a counterfactual, not a promotion path.
November sets no rule; that discipline is what the gates are for.

---

## VERDICT SUMMARY

1. **Data: complete.** Both builds finished (no 429 on the fresh
   attempt); every gate below ran on the full Jan–Oct window.
2. **IOI-1 FAIL** (−₹65,321.00; killed by total, halves,
   ex-top-3, all placebos). **IOI-2 FAIL** (−₹10,006.50; same
   legs, plus the time-shifted placebo turning positive).
   **FLOW-VOL FAIL** (−₹44,294.00; coin placebo at the 5.5th
   percentile). **OPT-FLOW FAIL** (−₹7,867.00; near every leg,
   NC 8.8%). No merge passes. The intraday-OI and flow
   continuation surfaces are closed on full-window evidence.
3. **The regime slice's answer:** regime-like days are 79/203
   Bank days (November: 6/9). The stack *profits* on them
   (+₹68,669.50, ₹1,634.99/trade-day); TUNED v1 profits on them
   (+₹42,526.25). November is a regime-dense hostile draw, not a
   blind spot. The only positive regime-day fragment is the
   already-known R4-D1 increment (+₹7,240.00, 8 legs). The slice
   also re-derives the Nifty B-PE leak exactly (−₹11,881.75, all
   of it on regime days).
4. **REGIME-REV (the one new family): Bank standalone GATE PASS
   — +₹15,872.00, both halves positive, ex-top-3 +₹8,432.00,
   beats all three placebos, 0 NC** — with three plain
   qualifications: H2 is only +₹632.00; ₹512.00/trade-day sits
   below the owner's ₹900 lens; and its **merge test FAILS**
   (increment −₹2,808.00). **Nifty: not gateable** (35 of 38
   fired days NC in the stored premium data). It goes to the
   owner as a standalone candidate for his decision; nothing is
   armed.
5. **November counterfactuals:** every merged line improves on
   −₹2,680; only the gate-dead IOI-1 (+₹3,040.00) and FLOW-VOL
   (+₹560.00) increments turn the month positive, as arithmetic
   on closed families. REGIME-REV's live-shaped increment leaves
   November at −₹539.00.

## FILES

- This report: `november_regime_fix_2026-11-14.md`
- Combined results: `november_regime_fix_results.json`
- Regime classification: `november_regime_days_bank.csv`,
  `november_regime_days_nifty.csv` · slice: `november_regime_slice.py`,
  `november_regime_slice_books.csv`, `november_regime_slice_results.json`
- Phase B: `round5_ioi_trades.csv`, `round5_ioi_gate_results.json`,
  `round5_trades_flow_vol.csv`, `round5_trades_opt_flow.csv`,
  `new_data_round5_results.json` (frozen-scorer defect and the
  corrected copy: `round5_score_fixed.py`, §B0)
- Phase D: `november_regime_family.py`,
  `november_regime_family_trades.csv`,
  `november_regime_family_results.json`, `november_regime_assembly.py`,
  `november_regime_assembly.json`
- IOI November legs: `november_regime_ioi_nov.py`,
  `november_regime_ioi_nov_legs.csv`
