# Bank Nifty upgrade tuning over U1-B2 — Bank channel ONLY

Index OPTIONS only, paper only, no orders, no stocks. Bank Nifty only —
no Nifty figures, no combined total or verdict anywhere in this file.
**Real money = ₹0. Nothing adopted.** Any passer would still need frozen
November paper from Mon 2026-11-02; in the event, **no variant passed, so
U1-B2 is kept unchanged** and its November spec is unchanged.

Units: October = option premiums per 1 lot (Bank lot 30, stop −50 /
target +90 premium points, ₹220 cost). Jan–Sep = **spot provisional per
leg** (spot points × 100 shares − ₹40 — NOT an options-lot profit, NOT a
futures profit), labelled per leg. Jan–Oct totals are **MIXED**
(spot Jan–Sep + premium Oct), never a pure premium total.

Pass bar (from task, all together): a variant replaces B2 only if it
progresses on net AND full-target % AND frequency (≥2/week) AND
month-end cumulative green at every month-end Jan–Oct. Judged on the
October-premium window and the Jan–Oct mixed window separately.

## 0. Baseline reproduced exactly — U1-B2

Recomputed from `index_options_U1_B2_bank_trades.csv` (89 legs) and
replayed bar-by-bar for October from cached premium candles
(`data/banknifty-2026-10/option_5m.csv`): all 9 October legs reproduce
exactly (7 targets +₹2,480, 2 stops −₹1,720).

| Window | Trades | /week | Full-target | Net |
|---|---|---|---|---|
| Oct premiums | 9 | 2.50 | 7/9 = 77.8% | **+₹13,920** |
| Jan–Oct mixed | 89 | 2.19 | 32/89 = 36.0% | **+₹124,415 mixed** |

Month-end cumulative (mixed): Jan +₹13,830 · Feb +₹22,925 · Mar
+₹120,715 · Apr +₹106,340 · May +₹175,260 · Jun +₹124,750 · Jul
+₹114,385 · Aug +₹88,225 · Sep +₹110,495 · Oct **+₹124,415** — green at
every month-end. Baseline confirmed; all variants below are scored
against exactly this.

## 1. VIOLENT-DAY definition — frozen from data before scoring outcomes

**VIOLENT day = Bank Nifty spot first-hour range (bars starting
09:15–10:10) ≥ 500 spot points**, computed from cached spot 5-min data
only, with no reference to any trade outcome. Distribution it was frozen
from: Jan–Oct first-hour range median ≈396 pts, ~70th percentile ≈499
pts — so ≥500 is roughly the most violent 30% of days, a round threshold
at that percentile.

Counts: **25 of 89 B2 legs fall on violent days (22 distinct dates)
Jan–Oct; 5 of 9 B2 legs in October** — 13 Oct PE, 21 Oct PE, 23 Oct PE,
26 Oct CE, 26 Oct PE, all of them baseline targets. October first-hour
ranges for B2 dates: 1 Oct 430 · 5 Oct 473 · 7 Oct 348 · 8 Oct 275 ·
13 Oct 630 · 21 Oct 567 · 23 Oct 815 · 26 Oct 615.

Note: 37 of 80 Jan–Sep B2 legs are (lA) day-scored legs with no intraday
entry/stop in the file; 13 of them sit on violent days. Where a variant
needs an intraday path those legs are **NOT_COMPUTED** and held at
baseline — counted, never silently assumed. Only 7 violent Jan–Sep legs
are fully replayable (entry, stop/target prices and times present).

## 2. RUNNER family — B2plus-RUNNER (one rule, violent days only)

Rule frozen before scoring: on violent days only, when premium first
hits +90, do **not** exit — move stop to entry (breakeven) and run to a
second target of **+150 premium points**; exit at breakeven stop, +150,
or 15:10 square-off, whichever first. Jan–Sep spot translation
(labelled): after the leg's recorded spot target, stop at entry spot,
second target 60 further spot points in the trade direction (mirrors
+90 → +150 premium), scored per 100 shares provisional.

- **October premiums: 9 trades, 2.50/week, net +₹18,420 (+₹4,500 vs
  B2), full-target 6/9 = 66.7% (DOWN from 77.8%).** Four violent legs
  reached +150 (+₹4,280 each: 21, 23, 26 Oct PE, 26 Oct CE); one gave
  the whole target back — 13 Oct PE hit +90, then stopped at breakeven
  for **−₹220 instead of +₹2,480**.
- **Jan–Oct mixed: 89 trades, 2.19/week, net +₹134,915 mixed
  (+₹10,500 vs B2), full-target 31/89 = 34.8% (DOWN from 36.0%).**
  Jan–Sep spot delta +₹6,000 from a single replayable violent target
  leg (24 Jun CE +₹8,960 → +₹14,960 provisional); the other violent
  Jan–Sep target legs are (lA) day legs = NOT_COMPUTED, held at
  baseline. Month-end cumulative green at every month-end (Jun
  +₹130,750, Oct +₹134,915; full curve in the working notes).
- **Verdict: REJECTED — fails the full-target leg on both windows.**
  The runner makes more money by making fewer full targets: it converts
  a banked +90 into a breakeven scratch on 13 Oct. Net alone does not
  pass under the all-together rule.

## 3. VOLATILE-STOP family — violent days only, target +90 unchanged

Extra risk per trade, stated up front (lot 30): stop −65 = **+₹450/lot**
extra risk vs B2; stop −75 = **+₹750/lot** extra. Jan–Sep spot
translation (labelled): stop widened by the same 15 / 25 points beyond
the leg's recorded stop price, per 100 shares provisional (= ₹1,500 /
₹2,500 extra per affected leg in that unit).

October first, honestly: **B2 has no violent-day stop leg in October**
(all 5 violent legs are targets, both October stops are on calm days),
so both variants are **identical to B2 in October — +₹13,920, 77.8% FT,
no progress on that window at all.**

Jan–Sep replayable violent stop legs: 6 (20 Feb CE, 9 Mar CE, 2 Apr PE,
10 Apr CE, 1 Jun CE, 9 Jul CE). Widening converts exactly one — 10 Apr
CE −₹5,040 → +₹9,960 target — and simply deepens the other five losses
by ₹1,500 (−65) / ₹2,500 (−75) each.

| Variant | Oct premiums | Jan–Oct mixed | Jan–Oct FT | /week | Cum. green? |
|---|---|---|---|---|---|
| B2plus-VSTOP65 | +₹13,920 (unchanged) | **+₹131,915 mixed (+₹7,500)** | 36.0% file-flag / 37.1% by exit-reason | 2.19 | Yes, every month-end |
| B2plus-VSTOP75 | +₹13,920 (unchanged) | **+₹126,915 mixed (+₹2,500)** | 36.0% file-flag / 37.1% by exit-reason | 2.19 | Yes, every month-end |

Full-target caveat, stated plainly: the one converted leg (10 Apr) is a
Volrix spot leg, and in the B2 trades file Volrix Jan–Sep target legs
carry full_target = 0 by that file's convention. So under the file's
own flag the FT rate does **not** move (36.0%); it rises to 37.1% only
if target exits are recounted by exit reason. Either way October shows
zero progress.

- **Verdict: BOTH REJECTED.** VSTOP65 is the closest variant in this
  run (Jan–Oct net +₹7,500, cumulative green throughout), but it fails
  the all-together bar: no net or FT progress on the October-premium
  window, and its Jan–Oct FT progress depends on changing the counting
  convention. One converted leg out of six, bought with deeper losses
  on the other five, is not a robust fix.

## 4. PREMIUM-CONVERSION family — Bank October diagnosis + one gate

Diagnosis (October component legs, spot outcome vs premium outcome):
of 17 Bank component legs, spot and premium agree on every leg except
one — **13 Oct V5 PE: spot scored a stop (−₹3,730 provisional) while
the premium hit target (+₹2,480)**. That leg is in B2 and the premium
scoring already captures the favourable side; there is **no B2 October
leg where spot hit target but premium failed** — the harmful divergence
direction is absent in October. Jan–Sep premium candles were not
fetched for B2 contracts, so Jan–Sep conversion is **NOT_COMPUTED** —
no premium data invented.

One gate tested (October premiums only, frozen as stated): **entry-bar
premium momentum — drop the leg if the premium's entry-bar close is
below the entry premium.** It drops 5 of 9 B2 legs: both stops
(7, 8 Oct) but also three +₹2,480 winners (5 Oct, 13 Oct, 26 Oct CE).
Result: **4 trades, 1.11/week, net +₹9,920, FT 4/4** — net DOWN ₹4,000
and frequency below the 2/week floor.

- **Verdict: REJECTED — fails net and frequency.** Premium weakness on
  the entry bar does not separate Bank winners from losers in October;
  three of the month's targets started with a red entry bar.

## Summary — Bank only

| Variant | Oct net Δ | Oct FT | Jan–Oct net Δ (mixed) | Jan–Oct FT | Failed leg |
|---|---|---|---|---|---|
| B2plus-RUNNER | +₹4,500 | 66.7% ↓ | +₹10,500 | 34.8% ↓ | Full-target (both windows) |
| B2plus-VSTOP65 | ₹0 | 77.8% = | +₹7,500 | 36.0% = (flag) | No Oct progress; FT convention |
| B2plus-VSTOP75 | ₹0 | 77.8% = | +₹2,500 | 36.0% = (flag) | No Oct progress; FT convention |
| B2plus-GATE (entry-bar momentum) | −₹4,000 | 4/4 on 4 trades | NOT_COMPUTED (Oct-only family) | — | Net + frequency |

**No upgrade beat B2 on all legs together, so no passing-variant trades
CSV is produced and U1-B2 is kept exactly as frozen.** The frozen
November paper Bank spec remains B2 unchanged, from Mon 2026-11-02, in
the separate Bank log, no re-tuning during November. The two ideas
worth remembering from this run are narrow ones: violent-day runners
add money but cost hit quality (13 Oct), and a −65 violent-day stop
converted exactly one of six replayable stops — both are November-paper
observations, not rule changes.
