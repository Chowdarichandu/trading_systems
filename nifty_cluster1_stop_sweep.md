# NIFTY Cluster 1 — Stop-placement, Signal-distance and Re-entry sweeps
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued after timing.

Source: `nifty_failing_cases_jan_oct_2026.md` Cluster 1 = Immediate
OR-breakdown PE bear-trap, 8 trades, original total −₹24,290, Jan–Aug 2026.
Previous family: timing (`nifty_timing_sweep_cluster1.md`) — best 3/8 =
37.5% green, no timing gate reaches 60%, timing damages winners.
Engine: `stop_sweep.py`, replayed bar by bar from the Upstox 5-min cache
(`data/progressive/NIFTY/spot_5m.csv`), same signal scan as the timing
sweep (V4 setup2 PE breakdown: close < OR low, close < PDL, room >=
200×scale, OR width <= 360×scale, signal <= 11:30; 2026-04-02 Skill:
close < OR low, close < PDL, no width/room cap). Entry = next bar open.
Stop checked before target on each bar including the entry bar,
square-off 15:10. 100 shares equivalent, ₹40/trade.
"Green" in the summary = net > ₹0; square-off positives are flagged
separately and are NOT counted as targets. No-trade is counted
separately from green throughout. 60% target = at least 5 of 8 green.
Winning set for impact checks: the same 14 V5 Nifty PE target days
used in the timing sweep (original total +₹91,270).

## Headline: NO genuine variant reaches 60%

Stop + distance + re-entry families are all exhausted in this run.
Best genuine green rate is 4/8 = 50.0% (stop = OR high, original
target kept) — and that variant is WORSE in total (−₹31,910 vs
baseline −₹24,290) because its four losses are enormous
(−₹18,825, −₹16,690, −₹9,245, −₹7,420). It is not a fix.
Every other variant is 0–3/8 green. No variant is carried into a
whole-month run, and no variant is applied to Clusters 2/3, because
the 60% condition was not met by any genuine variant.

## Variant summary — Cluster 1, 8 trades, original total −₹24,290

| Family / variant | Green (net>0) | Targets | No-trade | Still loss | Traded total (₹) | Reaches 60%? |
|---|---|---|---|---|---|---|
| Baseline (signal high, 2× target) | 0 / 8 | 0 | 0 | 8 | −24,290 | No |
| X1 — stop = signal high +10 pts, target recomputed | 1 / 8 | 0 | 0 | 7 | −26,245 | No |
| X2 — stop = signal high +20 pts, target recomputed | 1 / 8 | 0 | 0 | 7 | −33,245 | No |
| Y1 — stop = OR high, target recomputed (2× new risk) | 3 / 8 | 1 | 0 | 5 | −24,130 | No |
| Y2 — stop = OR high, ORIGINAL target kept | 4 / 8 | 4 | 0 | 4 | −31,910 | No |
| Z — exit only on 5-min CLOSE above OR low, original target kept | 0 / 8 | 0 | 0 | 8 | −23,130 | No |
| Z-degenerate — close above OR low, target recomputed from OR-low distance | 5 / 8 | 5 | 0 | 3 | (see below) | REJECTED, not counted |
| Distance 10 pts below OR low | 1 / 8 | 1 | 1 | 6 | −15,370 | No |
| Distance 20 pts below OR low | 1 / 8 | 1 | 3 | 4 | −7,290 | No |
| Distance 30 pts below OR low | 2 / 8 | 2 | 4 | 2 | −1,975 | No |
| Re-entry (one, after stop, on close back below OR low) — re-entry trade alone | 3 / 8 | 3 | 2 (no re-entry) | 3 | re-entry trades total +₹6,935 | No |
| Re-entry — day combined (original loss + re-entry) | 2 / 8 | — | 2 | 4 | combined total −₹17,355 | No |

## Family 1 — STOP PLACEMENT

### X — signal high + buffer (target recomputed at 2× new risk)
A buffer does NOT survive the bounce — it makes every loss bigger,
because the bounce runs through signal high +10 and +20 as well.
The only "green" in either buffer variant is 19 Aug, and it is a
square-off positive (+₹2,745 at 15:10), not a target.
- +10 pts: 1/8 net-positive, 0 targets, total −₹26,245 (worse than
  baseline). Day nets: 9 Jan −₹4,745 (stop 09:45), 6 Feb −₹3,275,
  30 Mar −₹3,055, 2 Apr −₹3,115, 13 May −₹6,075, 29 Jun −₹5,740,
  8 Jul −₹2,985, 19 Aug +₹2,745 square-off.
  Winners: 11/14 green, +₹75,585 (baseline +₹91,270) — 3 winners
  flip to loss (16 Mar −₹5,530, 5 May −₹3,580, 29 Sep −₹2,955);
  combined PE total +₹49,340, well below baseline +₹66,980.
- +20 pts: 1/8 net-positive, 0 targets, total −₹33,245 (much worse).
  Day nets: 9 Jan −₹5,745, 6 Feb −₹4,275, 30 Mar −₹4,055,
  2 Apr −₹4,115, 13 May −₹7,075, 29 Jun −₹6,740, 8 Jul −₹3,985,
  19 Aug +₹2,745 square-off.
  Winners: 11/14 green, +₹78,080; combined +₹44,835.
Verdict: buffer is a larger loss on the same days, not a fix. The
bounce is not a 10–20 point overshoot of the signal high.

### Y — stop = OR high
OR high is 73–188 points above entry (vs original risk 19–50 pts),
so this is a fundamentally different trade, not a tweak.
- Y1, target recomputed (2× new risk, targets 122–376 pts away):
  3/8 net-positive but only 1 target (9 Jan +₹20,870, target 14:40);
  the other two positives are square-off positives (30 Mar +₹13,210,
  19 Aug +₹2,745). Losses: 6 Feb −₹8,775, 2 Apr −₹18,825,
  13 May −₹16,690, 29 Jun −₹9,245, 8 Jul −₹7,420. Total −₹24,130,
  barely better than baseline, built on one huge target and two
  square-offs. Winners collapse: 10/14 green, +₹28,050 (4 winners
  flip to large stops, e.g. 16 Mar −₹19,275, 21 Jan −₹17,065);
  combined +₹3,920. Rejected.
- Y2, original target kept (target distance unchanged, so reward
  is now far below 2× risk — this is the honest version of "wider
  stop, same target"):
  4/8 green, all 4 targets: 9 Jan +₹7,370 (target 11:35),
  6 Feb +₹4,430 (10:30), 30 Mar +₹3,990 (13:50), 19 Aug +₹4,480
  (11:05). Losses: 2 Apr −₹18,825, 13 May −₹16,690, 29 Jun −₹9,245,
  8 Jul −₹7,420. Total −₹31,910 — WORSE than baseline despite
  4/8 green, because the four surviving losses carry OR-high risk
  (87–188 pts). Winners are untouched (14/14, +₹91,270, because
  the wider stop never triggers and the target is unchanged);
  combined +₹59,360 is therefore flattering — it is baseline
  winners plus a Cluster 1 variant that still loses more in total.
  Closest to 60% on green count (4/8), still short by 1 trade, and
  fails on total and on risk size. NOT adopted.

### Z — exit only on a 5-min CLOSE above OR low (not an intra-bar high touch)
Clean version, original target kept: 0/8 green, total −₹23,130
(only ₹1,160 better than baseline). Every day still loses, just at
the close price instead of the signal high: 9 Jan −₹4,105 (close
above OR low 09:40), 6 Feb −₹2,595, 30 Mar −₹3,610, 2 Apr −₹970
(smallest loss in the family), 13 May −₹3,070, 29 Jun −₹4,180,
8 Jul −₹2,785, 19 Aug −₹1,815. Winners fall to 9/14, +₹58,720
(5 winners exit early on a close above OR low, e.g. 5 May −₹1,090,
22 Jul −₹2,505, 12 Aug −₹1,650); combined +₹35,590.
Verdict: a close-based exit shrinks some losses but converts none.

#### Z-degenerate — why the recomputed-target version is REJECTED
If the target is recomputed from the OR-low distance (risk =
OR low − entry, only 2.05–25.15 pts), targets collapse to 4.1–50.3
points and the count becomes 5/8 "green": 9 Jan +₹580 (target on
the entry bar itself, 09:35), 6 Feb +₹1,980, 30 Mar +₹370,
2 Apr +₹430, 13 May +₹4,990 (entry bar), with 29 Jun −₹4,180,
8 Jul −₹2,785, 19 Aug −₹1,815 still losing. Three of the five
"greens" are entry-bar noise targets of ₹370–₹580, and the
largest (+₹4,990) is a 50-point target on a trade whose original
target was 100 points. Counting this as "60% reached" would be
changing the target to fit the noise, not fixing the trade.
It is recorded here so it cannot be claimed later, and it is
NOT counted in the headline, NOT carried forward, and NOT
applied to Clusters 2/3.

## Family 2 — SIGNAL DISTANCE (signal close must be at least X below OR low)
Scanning continues to the first bar meeting the distance, so later
signals appear — flagged below. Distance mostly converts trades to
no-trades, not to greens, and damages winners.
- 10 pts: 1/8 green, 1 no-trade, total −₹15,370. Green: 9 Jan
  +₹2,540 (later signal 10:55, target 11:15). No-trade: 30 Mar.
  Losses: 6 Feb −₹2,090, 2 Apr −₹2,950, 13 May −₹5,075,
  29 Jun −₹4,740, 8 Jul −₹755, 19 Aug −₹2,300.
  Winners: 11/14, +₹68,935; combined +₹53,565.
- 20 pts: 1/8 green, 3 no-trade, total −₹7,290. Green: 19 Aug
  +₹3,970 (later signal 10:15, target 11:05). No-trade: 30 Mar,
  29 Jun, 8 Jul. Losses: 9 Jan −₹1,145, 6 Feb −₹2,090,
  2 Apr −₹2,950, 13 May −₹5,075.
  Winners: 10/14, +₹56,450; combined +₹49,160.
- 30 pts: 2/8 green, 4 no-trade, total −₹1,975 (best total in the
  family, still only 2/8 green). Greens: 9 Jan +₹4,790 (later
  signal 11:10, target 11:45), 19 Aug +₹1,470 (later signal 10:30,
  target 10:40). No-trade: 30 Mar, 2 Apr, 29 Jun, 8 Jul. Losses:
  6 Feb −₹1,810, 13 May −₹6,425 (worse than original — later
  signal 09:35 with 63.85-pt risk).
  Winners: 9/14 green, 1 no-trade, +₹43,110; combined +₹41,135.
Verdict: distance is avoidance (no-trade), not conversion. At
30 pts half the cluster does not trade at all, and the two
"greens" are later signals, as in the timing sweep.

## Family 3 — RE-ENTRY (one only, after a stop, on a close back below OR low)
Counted separately, as instructed: re-entry trade alone, and day
combined (original loss + re-entry).
- Re-entry trade alone: 3/8 green (targets), 2 no re-entry,
  3 re-entry losses. Greens: 9 Jan +₹6,040 (re-entry signal
  10:50, target 11:35), 29 Jun +₹6,840 (11:30, target 12:30),
  19 Aug +₹1,020 (10:10, target 10:15). Losses: 6 Feb −₹265
  (09:55), 2 Apr −₹2,950 (10:05), 8 Jul −₹2,740 (10:20).
  No re-entry (price never closes back below OR low after the
  stop, up to 11:30): 30 Mar, 13 May. Re-entry trades total
  +₹6,935 on 6 trades.
- Day combined: 2/8 green — 9 Jan +₹2,295 (−₹3,745 + ₹6,040)
  and 29 Jun +₹2,100 (−₹4,740 + ₹6,840). The other re-entry
  green (19 Aug) does not turn the day green: −₹2,300 + ₹1,020
  = −₹1,280. Combined total −₹17,355 (vs baseline −₹24,290),
  still 4 days losing, 2 days with no second chance.
Verdict: re-entry recovers two days, but it is the same later
signals the timing gates already found (9 Jan 10:50, 29 Jun
11:30, 19 Aug 10:10) — it does not fix the morning trade, it
adds a second, later trade. 2/8 combined green is not 60%.

## Clusters 2 and 3 — not applied
Condition in the task: apply a variant to Clusters 2/3 only if it
reaches 60% on Cluster 1. No genuine variant did, so no variant
is carried into Clusters 2 (reclaim failure, 2 trades, −₹11,420)
or 3 (slow give-back, 3 trades, −₹10,585) as a fix. This is
consistent with the timing sweep, which also found timing does
not fix those clusters (Cluster 2 signals are 11:15 and 09:55,
already late; Cluster 3 is an exit-rule failure, not an
entry/stop failure).

## Verdict — stop, distance and re-entry families, exhausted

- 60% target (5/8 green): NOT reached by any genuine variant.
  Best genuine: Y2 (OR-high stop, original target) 4/8 green,
  but total −₹31,910 and risks 87–188 pts — worse than baseline.
- Best Cluster 1 total among genuine variants: distance 30 pts,
  −₹1,975, but only 2/8 green and 4/8 no-trade — avoidance, not
  consistent green.
- Best combined PE total among genuine variants: Y2, +₹59,360
  (Cluster 1 −₹31,910 + winners +₹91,270), below baseline
  +₹66,980 — because Cluster 1 itself is worse in total.
- What the three families together prove: the bounce that stops
  Cluster 1 out is not a 10–20 point overshoot (buffer fails),
  not a close-vs-touch distinction (close exit converts 0/8),
  and not a shallow-breakdown filter (distance converts to
  no-trade, not green). The only variants that "green" the
  cluster do so by replacing the morning trade with a later
  signal (timing gates, distance later signals, re-entries) or
  by shrinking the target to noise (Z-degenerate, rejected) or
  by widening risk so far that losses dwarf the greens (OR-high).
- **No variant from these families is adopted, and none is
  carried into a whole-month run.** The next family to test,
  if the long-horizon task continues, must change something
  these families did not: e.g. a partial booking / trail for
  trades that move toward target before reversing (relevant
  to Cluster 3, and to Cluster 1 days that later reach target),
  a bias/room filter that selects only breakdowns with room
  beyond the next level, or a no-trade rule for the specific
  morning shape (first-bar breakdown with a narrow OR) —
  tested with the same 60% green target, and with no-trade
  counted separately from green, so avoidance cannot be
  presented as conversion.
- Files: engine `stop_sweep.py`, raw replay `stop_sweep_raw.json`.
  Paper only throughout; no orders placed, nothing fabricated.
