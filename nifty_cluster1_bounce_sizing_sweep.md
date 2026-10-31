# NIFTY — Bounce-bar sizing + new morning-exit sweeps (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): combined sweep is done
(`nifty_cluster1_combined_sweep.md`) — M1 out-of-sample fails
conversion (4/55 losses green, 7.3%; fast stops 3/28, 10.7%; winner
deletion cost −₹19,905), M11 fails catastrophically out-of-sample
(0/55 losses green, 14 winners deleted, total −₹885 vs baseline
+₹25,560) — **M11 is dead, do NOT carry it forward**. Re-entry +
partial/trail as ONE rule: best C-SURV 2/8 green, total −₹18,237 —
partial clips the re-entry targets and converts zero additional
days. November paper spec prepared only, no candidate frozen, no
thresholds frozen for adoption. Nothing adopted.

This task, Nifty only, paper only, same pass bar (60% green AND
total positive AND winners not collapsed), no re-running buffer,
OR-high, close-exit or partial families on the original trade
alone, no re-fitting the discarded box, no re-running M1/M11
thresholds, no re-combining re-entry+partial:

1. Sizing the morning trade by the BOUNCE bar's range rather than
   the signal bar's range.
2. A NEW morning-trade exit not yet tried.
For each variant: green / no-trade / still loss, cluster total,
winner total, combined total, with no-trade counted separately
from green. If a variant passes on Cluster 1 with positive
economics, apply to Clusters 2/3. If none passes, report best
variant and next family — task continues in parent conversation,
do NOT present exhaustion as completion.

Engine: `bounce_sizing_sweep.py` (+ `bounce_sizing_extra.py` for
BS-CAP / T-RATCHET), raw replays `bounce_sizing_sweep_raw.json`
and `bounce_sizing_extra_raw.json`. Replayed bar by bar from the
Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv`,
`spot_daily.csv`), same signal scan as all prior sweeps (V4
setup2 PE breakdown: close < OR low, close < PDL, room ≥
200×scale, OR width ≤ 360×scale, signal ≤ 11:30; 2026-04-02
Skill, 2026-03-23 Skill winner). Stop checked before target on
each bar including the entry bar, square-off 15:10, 100 shares
equivalent, ₹40/trade unless a sizing variant says so. Green =
net > ₹0. No-trade counted separately from green throughout.
Cluster 1 baseline: 8 trades, 0/8 green, total −₹24,290.
Winners baseline: 14 V5 Nifty PE target days, 14/14 green,
total +₹91,270. Baseline combined PE: +₹66,980.

## Headline — both families exhausted, nothing passes, nothing adopted

- **Family 1, bounce-bar sizing: FAILS, and the live version is
  worse than baseline on every leg.** BS-A (delayed entry, stop =
  entry + bounce range, target = entry − 2× range) is **0/8
  green, total −₹31,550** — worse than baseline −₹24,290 —
  and winners collapse to **6/14, +₹9,775** (from +₹91,270).
  BS-A2 (same, only if the bounce bar still closes below OR
  low) is 0/8 green with 3 no-trades, traded total −₹16,705,
  winners still 6/14, +₹9,775. BS-CAP (bounce range capped at
  original risk) is 0/8 green, −₹22,660, winners 7/14,
  +₹20,245. The bounce range is not a better risk unit: on
  5 of 8 Cluster 1 days it is LARGER than the original risk
  (30 Mar 48.95 vs 20.15; 2 Apr 40.65 vs 20.75; 13 May 76.80
  vs 50.35; 29 Jun 57.65 vs 47.00; 6 Feb 25.45 vs 22.35),
  so sizing by it widens the loss, and delaying entry by one
  bar destroys genuine winners that the original entry caught.
- **Family 2, new morning exits: best is 4/8 green, still fails
  the pass bar.** T-A (profit-lock trail: trigger 0.5× risk,
  lock 0.25× risk, full position, no partial, no breakeven
  move) is **4/8 green, but total −₹9,946.25 (still negative)**
  and winners collapse to **14/14 green in count but only
  +₹10,918.75 in total** — the trail locks every winner at
  its first 0.25× retracement, destroying ₹80,351 of winner
  value. T-RATCHET (locks stepping up: 0.5×→0.25×, 1.0×→0.5×,
  1.5×→1.0×) improves Cluster 1 only to **4/8, −₹8,687.50**
  and winners only to **+₹13,720** — because on most winner
  days the price retraces to the first lock before it ever
  reaches the 1.0× threshold that would raise the lock.
  T-B (trigger 1.0×, lock 0.5×) is 1/8, −₹16,737.50, winners
  +₹27,115. T-D (OR-low TOUCH exit) is 0/8, −₹8,470 — the
  best loss-shrink in the family, but zero conversion, and
  winners fall to 9/14, +₹60,795. T-C6/T-C3 (absolute time
  exits, distinct from stall — see below) are 0/8 on Cluster
  1, unchanged, because every Cluster 1 stop hits before
  the clock can fire.
- **Nothing is adopted, nothing is applied to Clusters 2/3**
  (condition not met), and nothing is carried into a
  whole-month run on its own. The best variant in this
  sweep, T-RATCHET (4/8, −₹8,687.50, combined +₹5,032.50),
  is still short of 60% by 1 trade, still negative on
  Cluster 1, and still collapses winners by 85%. It is
  recorded as the best variant, not as a candidate.

## Family 1 — Sizing by the bounce bar's range: definitions first

Bounce bar B = the bar immediately after the signal bar (the
original entry bar). Its range Rb = high − low:

| Date | Signal | Orig risk (pts) | Bounce bar | Rb (pts) | Rb vs orig risk |
|---|---|---|---|---|---|
| 2026-01-09 | 09:30 | 37.05 | 09:35 | 30.25 | smaller |
| 2026-02-06 | 09:35 | 22.35 | 09:40 | 25.45 | larger |
| 2026-03-30 | 11:25 | 20.15 | 11:30 | 48.95 | 2.4× larger |
| 2026-04-02 (Skill) | 09:55 | 20.75 | 10:00 | 40.65 | 2.0× larger |
| 2026-05-13 | 09:30 | 50.35 | 09:35 | 76.80 | larger |
| 2026-06-29 | 09:30 | 47.00 | 09:35 | 57.65 | larger |
| 2026-07-08 | 09:30 | 19.45 | 09:35 | 17.60 | smaller |
| 2026-08-19 | 09:30 | 22.60 | 09:35 | 14.95 | smaller |

Critical implementation point, stated before the results: Rb
is known only AFTER B closes, so a bounce-sized trade CANNOT
be entered at the original entry open. The live version is
therefore a DELAYED entry at the open after B (bar sig+2),
with stop = entry + Rb and target = entry − 2×Rb. Any
sizing that claims to use Rb at the original entry is
post-hoc, not live — see BS-S below, which is labelled
diagnostic for exactly that reason. Note also that a
stop = B's high with entry after B is exactly the
second-close rule already tested in the timing sweep
(0/8 at 09:35+second close) — it is NOT re-run here as a
"new" variant.

### Results — Family 1

| Variant | Cluster 1 green | No-trade | Still loss | Cluster 1 total (₹) | Winners green | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | 14/14 | +91,270 | +66,980 | — |
| BS-A: delayed entry, stop = entry + Rb, target 2×Rb | 0/8 | 0 | 8 | −31,550 | 6/14 | +9,775 | −21,775 | No |
| BS-A2: BS-A only if B closes < OR low | 0/8 | 3 | 5 | −16,705 (traded only) | 6/14 | +9,775 | −6,930 (traded only) | No |
| BS-CAP: BS-A with Rb capped at orig risk | 0/8 | 0 | 8 | −22,660 | 7/14 | +20,245 | −2,415 | No |
| BS-S: orig prices, shares = round(100×orig risk/Rb), diagnostic only | 0/8 | 0 | 8 | −21,439.95 | 14/14 | +118,735.50 | +97,295.55 | No — see below |

BS-A day nets (Cluster 1): 9 Jan −₹3,065; 6 Feb −₹2,585;
30 Mar −₹4,935; 2 Apr −₹4,105; 13 May −₹7,720; 29 Jun
−₹5,805; 8 Jul −₹1,800; 19 Aug −₹1,535. Every day still
stops — delaying entry by one bar and widening the stop
to Rb does not survive the bounce, it just moves the
stop further away and then loses more when it is hit.
BS-A2 no-trades are 30 Mar, 2 Apr, 29 Jun (bounce bar
closed back above OR low); the 5 traded days are the
same stops as BS-A, so the "improved" total is avoidance
on 3 days, not conversion on any day.
BS-CAP day nets: 9 Jan −₹3,065; 6 Feb −₹2,275; 30 Mar
−₹2,055; 2 Apr −₹2,115; 13 May −₹5,075; 29 Jun −₹4,740;
8 Jul −₹1,800; 19 Aug −₹1,535 — capping Rb at original
risk returns 4 days to exactly their original nets and
still converts nothing, because the delayed entry price
itself is worse (e.g. 29 Jun entry 24,060.55 vs original
24,018.70, already 41.85 points against the trade).

BS-S — why its combined total must NOT be quoted as a
pass: shares are scaled by Rb after the fact (41 shares
on 30 Mar, 151 on 19 Aug), so green count is unchanged
by construction (same exit prices, same signs: 0/8
Cluster 1, 14/14 winners) and the winner total
+₹118,735.50 is inflated by leverage on small-Rb winner
days (194 shares on 22 Jul, 170 on 24 Apr, 168 on 12 Aug)
with a flat ₹40 cost that does not scale with size.
It proves only that sizing changes magnitude, not
conversion — and it is not live at the original entry,
because Rb is not known until the entry bar closes.

Winner damage under BS-A/BS-A2/BS-CAP, for the record:
BS-A winners 6/14: targets 21 Jan +₹5,620, 23 Mar
+₹8,310, 24 Apr +₹5,170, 27 Aug +₹3,230, 7 Sep +₹3,490,
23 Oct +₹8,080; flipped to stops include 16 Mar −₹4,190,
13 Mar −₹3,740, 29 Sep −₹5,020. Delaying entry by one
bar is itself a large winner cost, before any sizing
effect — the delayed trade is a different trade, and a
worse one for winners.

## Family 2 — NEW morning exits: definitions first, so they are not re-runs

Prior exits already exhausted: stop buffer (+10/+20),
OR-high stop, close-above-OR-low exit (Z), partials
(book 50% at 0.5×/1.0× risk, trail rest to breakeven),
stall (exit at close after N bars WITHOUT a new
favourable extreme — its counter RESETS on every new
low for a PE trade), survival-gated exits, and
re-entry+partial combined. The variants below are
different from all of those:

- **T-A / T-B — profit-lock trail, full position.**
  No partial booking, no move to breakeven. Once price
  moves favourably by the trigger distance, the whole
  position's exit becomes the lock level, and it exits
  there in full on the first high ≥ lock. T-A: trigger
  0.5× risk, lock 0.25× risk. T-B: trigger 1.0× risk,
  lock 0.5× risk. This differs from the prior partial
  because the locked profit is the FULL position's
  profit, not half a position, and from a breakeven
  trail because the lock is a positive profit level,
  not entry.
- **T-RATCHET — stepped profit-lock trail.** Same full-
  position lock, but the lock steps up as favourable
  move grows: 0.5× favourable → lock 0.25×; 1.0× →
  lock 0.5×; 1.5× → lock 1.0×. Target stays 2× risk.
  This is the only variant in the family that can, in
  principle, let a winner run past its first lock.
- **T-C6 / T-C3 — ABSOLUTE time exit, distinct from
  stall.** Stall resets its counter on every new low;
  this clock does NOT reset. If by the close of the
  6th (T-C6) or 3rd (T-C3) bar after the entry bar the
  trade has not reached 0.5× risk favourable AT ANY
  POINT, exit at that bar's close. Stop/target are
  checked before the time exit on every bar.
- **T-D — OR-low TOUCH exit, distinct from close-exit
  Z.** Z waited for a 5-min CLOSE above OR low; T-D
  exits at OR low on the first bar whose HIGH ≥ OR
  low, before the original stop. Original target kept.

### Results — Family 2

| Variant | Cluster 1 green | No-trade | Still loss | Cluster 1 total (₹) | Winners green | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | 14/14 | +91,270 | +66,980 | — |
| T-A: trail trigger 0.5×, lock 0.25× | 4/8 | 0 | 4 | −9,946.25 | 14/14 | +10,918.75 | +972.50 | No |
| T-RATCHET: stepped locks 0.25×/0.5×/1.0× | 4/8 | 0 | 4 | −8,687.50 | 14/14 | +13,720 | +5,032.50 | No |
| T-B: trail trigger 1.0×, lock 0.5× | 1/8 | 0 | 7 | −16,737.50 | 14/14 | +27,115 | +10,377.50 | No |
| T-C6: absolute time exit, 6 bars, need 0.5× | 0/8 | 0 | 8 | −24,290 | 14/14 | +91,270 | +66,980 | No |
| T-C3: absolute time exit, 3 bars, need 0.5× | 0/8 | 0 | 8 | −24,290 | 14/14 | +85,490 | +61,200 | No |
| T-D: OR-low touch exit | 0/8 | 0 | 8 | −8,470 | 9/14 | +60,795 | +52,325 | No |

T-A day nets (Cluster 1): 9 Jan −₹3,745 (MFE 23.9% of
target = 0.48× risk, just below the 0.5× trigger, so
no lock ever triggers); 6 Feb +₹518.75 (trail lock
09:40); 30 Mar −₹2,055 (MFE 0%, no trigger); 2 Apr
−₹2,115 (MFE 0%, no trigger); 13 May +₹1,218.75
(trail lock 09:35); 29 Jun −₹4,740 (MFE 14.1%, no
trigger); 8 Jul +₹446.25 (trail lock 09:35); 19 Aug
+₹525.00 (trail lock 09:35). Greens are trail-lock
exits, NOT targets — they are counted as green
because net > ₹0, as in all prior sweeps, but they
are ₹446–₹1,219 locked profits, not 2× targets.
Losses are exactly the 4 days whose MFE never
reached 0.5× risk — the trail cannot help a trade
that never moves favourably, which is why it stops
at 4/8.
T-A winners: all 14 exit at their 0.25× lock, none
reaches target — e.g. 21 Jan +₹1,125 (vs +₹9,280),
23 Oct +₹1,388.75 (vs +₹11,390), 16 Mar +₹1,082.50
(vs +₹8,940). Winner total +₹10,918.75 is 12% of
baseline. A rule that converts 4 losses by capping
every winner at a quarter of its risk is not
consistent green, it is a different, smaller trade.

T-RATCHET day nets (Cluster 1): same 4 greens as
T-A, except 13 May improves to +₹2,477.50 (its MFE
74.2% of target = 1.48× risk reaches the 1.0×
threshold, so its lock steps up to 0.5× before
exiting); other greens unchanged (+₹518.75, +₹446.25,
+₹525.00); same 4 losses (−₹3,745, −₹2,055, −₹2,115,
−₹4,740). Winners: 13 of 14 exit at the first lock
unchanged; only 29 Sep improves (T-A +₹438.75 →
ratchet +₹1,875.00, its lock stepped to 1.0× risk).
Why the ratchet mostly does not help: on most
winner days the price retraces to the first lock
BEFORE any bar's low reaches the 1.0× threshold
that would raise the lock — the lock is set by
intraday lows, and the retracement that exits the
trade happens on an earlier bar than the threshold
bar. A ratchet keyed to intraday extremes therefore
behaves almost identically to a single lock.

T-B: only 13 May greens (+₹2,477.50, its MFE reaches
1.0× risk); 6 Feb (MFE 47.4% of target = 0.95× risk,
just below trigger), 8 Jul (36.6%), 19 Aug (25.0%)
all fail the higher trigger and stop out. Winners
+₹27,115 (one target survives, 12 Aug +₹6,250; the
rest exit at 0.5× lock).
T-C6: Cluster 1 identical to baseline on all 8 days
— every Cluster 1 stop hits in 1–5 bars, before the
6th-bar clock (entry bar + 6) can fire; winners
identical to baseline. An absolute clock longer than
the stop time cannot change a fast-stop cluster.
T-C3: Cluster 1 identical to baseline for the same
reason (stops at 1–5 bars include stops on the
3rd-bar clock bar itself, checked before the time
exit); winners lose one target (22 Jul +₹6,320 →
time exit +₹540 at 09:50, because it had not reached
0.5× risk by that bar's close despite later reaching
target) for a −₹5,780 winner cost, total +₹85,490.
T-D: Cluster 1 losses shrink on all 8 days (9 Jan
−₹350, 6 Feb −₹1,050, 30 Mar −₹245, 2 Apr −₹275,
13 May −₹2,555, 29 Jun −₹1,405, 8 Jul −₹885, 19 Aug
−₹1,705; total −₹8,470, 65% smaller than baseline)
but zero convert — exiting at OR low is still a
loss, just a smaller one, on every day. Winners:
5 flip to losses on OR-low touch (5 May −₹840,
22 Jul −₹2,110, 12 Aug −₹1,150, 7 Sep −₹75, 8 Oct
−₹260), total +₹60,795. A loss-cutter, not a
converter — same verdict as stall, by a different
mechanism.

## Clusters 2 and 3 — not applied
Condition in the task: apply a variant to Clusters 2/3
only if it reaches 60% on Cluster 1 with positive
economics. No variant did (best 4/8, Cluster 1 total
still negative in every variant, winners collapsed
in every variant that greens at all), so no variant
is carried into Cluster 2 (reclaim failure, 2 trades,
−₹11,420) or Cluster 3 (slow give-back, 3 trades,
−₹10,585) as a fix. For the record, T-A/T-RATCHET
are PE-breakdown exits and would not in any case
apply to Cluster 2's CE reclaim trades, and T-D's
OR-low touch is the wrong side's level for Cluster 3's
give-back problem (its fix, if any, is on its own
exit, already tested as partial/stall/survival).

## Variant summary — both families in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| BS-A bounce-range delayed entry | 0/8 | −31,550 | +9,775 | −21,775 | No |
| BS-A2 bounce-range, breakdown-intact only | 0/8 (+3 no-trade) | −16,705 traded | +9,775 | −6,930 traded | No |
| BS-CAP bounce-range capped at orig risk | 0/8 | −22,660 | +20,245 | −2,415 | No |
| BS-S bounce-range share scaling, diagnostic only | 0/8 | −21,439.95 | +118,735.50 | +97,295.55 | No — post-hoc, sign unchanged |
| T-A profit-lock trail 0.5×→0.25× | 4/8 | −9,946.25 | +10,918.75 | +972.50 | No — total negative, winners collapsed |
| T-RATCHET stepped locks | 4/8 | −8,687.50 | +13,720 | +5,032.50 | No — best variant, still short |
| T-B profit-lock trail 1.0×→0.5× | 1/8 | −16,737.50 | +27,115 | +10,377.50 | No |
| T-C6 absolute time exit, 6 bars | 0/8 | −24,290 | +91,270 | +66,980 | No — clock never fires |
| T-C3 absolute time exit, 3 bars | 0/8 | −24,290 | +85,490 | +61,200 | No |
| T-D OR-low touch exit | 0/8 | −8,470 | +60,795 | +52,325 | No — loss-cutter only |

## What this sweep proves, and what it does not

- Bounce-range sizing does not fix the morning trade.
  The bounce bar's range is larger than the original
  risk on most Cluster 1 days, so it widens losses;
  and the one-bar delay it forces destroys winners
  (6–7/14 vs 14/14) before sizing even matters. A risk
  unit measured from a bar that already contains the
  bounce is, by construction, a risk unit measured
  after the damage — it cannot be the morning trade's
  stop.
- A profit-lock trail is the closest any single exit
  has come to 60% on Cluster 1 (4/8, vs 2/8 for
  re-entry, 3/8 for timing gates, 4/8 for OR-high
  stop with a worse total), but it fails the pass bar
  on both other legs: Cluster 1 total is still
  negative (−₹8,687.50 best), and it caps winners at
  12–15% of their baseline value. The 4 greens it
  creates are ₹446–₹2,478 locked profits, and the 4
  days it cannot help are exactly the days with no
  favourable move at all (MFE 0–24% of target) —
  no exit rule can convert a trade that never moves
  in its favour without widening the stop or adding
  a second trade, both already tested and failed.
- Absolute time exits and OR-low touch exits are
  loss-cutters, not converters, on this cluster:
  T-C never fires before the fast stops, and T-D
  shrinks every loss by 65% in total while converting
  none and flipping 5 winners. They belong in the
  same category as stall, not in the category of a
  60% fix.
- What remains untested for Cluster 1 after this
  sweep — the next family, NOT a re-run of the above:
  (a) a CLOSE-based profit-lock trail (trigger and
  exit only on 5-min closes, not intraday low/high
  touches) — the intraday trail tested here exits on
  the first wobble back to the lock, before most
  winners ever reach the threshold that would raise
  it; a close-based version may let winners run
  while still locking the Cluster 1 days that close
  favourably before reversing; (b) a lock that only
  arms after a close below a level, combined with the
  original stop (not a replacement for it), so a
  wobble that never closes favourably cannot arm
  the lock at all; (c) on the sizing side, a risk
  unit measured from a PRE-signal bar (e.g. the OR
  bars' range, or the previous day's range) rather
  than from the bounce bar — the only sizing that
  can be known at entry time without delaying the
  trade. Those are the next families, not re-runs
  of bounce-range sizing, intraday trails, absolute
  clocks, or OR-low touch exits, and not another
  re-entry+partial combination.

Files: engine `bounce_sizing_sweep.py`, raw replay
`bounce_sizing_sweep_raw.json`, extra engine
`bounce_sizing_extra.py`, extra raw replay
`bounce_sizing_extra_raw.json`. Paper only throughout;
no orders placed, nothing fabricated. The long-horizon
task continues in the parent conversation: Families
1–2 in this task are exhausted, and the next decision
is which untried family to run — and none of the
variants in this report is adopted.
