# NIFTY — Close-based profit-lock trail + pre-signal sizing sweep (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): bounce sizing + new morning-exit sweep is done
(`nifty_cluster1_bounce_sizing_sweep.md`) — bounce-bar sizing fails
(BS-A 0/8, −₹31,550, winners 6/14; bounce range larger than original
risk on 5/8 days, one-bar delay alone destroys winners; BS-S is
post-hoc leverage, do NOT quote as a pass). New morning exits: best
T-RATCHET 4/8 green, −₹8,687.50, combined +₹5,032.50, still short of
60% by 1 trade, still negative on Cluster 1, winners collapsed 85%.
T-D OR-low touch exit is 0/8, −₹8,470, loss-cutter only. Nothing
adopted, nothing carried to a whole-month run.

This task, Nifty only, paper only, same pass bar (60% green AND
total positive AND winners not collapsed), no re-running buffer,
OR-high, close-exit or partial families on the original trade
alone, no re-fitting the discarded box, no re-running M1/M11
thresholds, no re-combining re-entry+partial:

(a) CLOSE-BASED profit-lock trail — trigger and exit only on 5-min
    closes, not intraday low/high touches. Stepped locks
    0.5×→0.25×, 1.0×→0.5×, 1.5×→1.0× on closes only.
(b) Lock that only arms after a CLOSE below a level, combined with
    the original stop (not replacing it), so a wobble that never
    closes favourably cannot arm the lock at all.
(c) Sizing: risk unit measured from a PRE-SIGNAL bar (OR bars'
    range, or previous day's range) rather than the bounce bar —
    the only sizing knowable at entry time without delaying
    the trade.

For each variant: green / no-trade / still loss, cluster total,
winner total, combined total, with no-trade counted separately
from green. If a variant passes on Cluster 1 with positive
economics, apply to Clusters 2/3. If none passes, report best
variant and next family — task continues in parent conversation,
do NOT present exhaustion as completion.

Engine: `close_trail_sweep.py`, raw replay
`close_trail_sweep_raw.json`. Replayed bar by bar from the Upstox
5-min cache (`data/progressive/NIFTY/spot_5m.csv`,
`spot_daily.csv`), same signal scan as all prior sweeps (V4
setup2 PE breakdown: close < OR low, close < PDL, room ≥
200×scale, OR width ≤ 360×scale, signal ≤ 11:30; 2026-04-02
Skill, 2026-03-23 Skill winner). Entry = next bar open after
signal, original stop = signal high (PE), original target =
entry − 2×risk, stop checked before target on each bar
including the entry bar, square-off 15:10, 100 shares
equivalent, ₹40/trade unless a sizing variant says so.
Green = net > ₹0. No-trade counted separately from green
throughout. Cluster 1 baseline: 8 trades, 0/8 green, total
−₹24,290. Winners baseline: 14 V5 Nifty PE target days,
14/14 green, total +₹91,270. Baseline combined PE: +₹66,980.

## Headline — families (a)–(c) all exhausted, nothing passes, nothing adopted

- **Family (a), close-based trail: 0/8 green in EVERY variant.**
  All five close-trail variants give the identical Cluster 1
  total, **−₹22,285** (only +₹2,005 vs baseline): 7 stops
  unchanged, and 13 May improved from −₹5,075 to −₹3,070
  on a close-lock exit that is still a loss. No variant
  converts a single Cluster 1 day. This is not a coding
  coincidence — it is proved by the close-favourable
  ceiling below: only 2 of 8 days ever close ≥0.5× risk
  favourably before the stop bar, and the one day that
  does arm a lock (13 May) exits at a close that has
  already retraced above entry, so the "locked" exit
  is still a loss (see the close-execution warning
  below).
- **Family (b), signal-low arming: also 0/8, identical
  Cluster 1 total −₹22,285.** Arming on a close below
  the signal bar's low changes nothing on Cluster 1,
  because the days that arm are the same days that
  already armed on distance, and the days that never
  close favourably never arm either. On winners it is
  WORSE than the plain close trail (see below): arming
  on the first close below the signal low arms too
  early, on the entry bar itself on many winner days.
- **Family (c), pre-signal sizing: best is 2/8 green,
  still fails everything else.** S-ORAVG (mean OR-bar
  range) is 2/8, −₹23,140 — the 2 greens are one huge
  widened target (9 Jan +₹14,033) and one square-off
  (19 Aug +₹2,745), while 6 days still stop and their
  losses are much larger (up to −₹9,230). S-PD10
  (10% of previous-day range) is 0/8, −₹21,176, and
  collapses winners to 9/14. S-ORAVG-CAP is 0/8,
  −₹24,242 — essentially baseline, because the mean
  OR-bar range exceeds the original risk on almost
  every day, so the cap binds back to the original
  risk (see below).
- **Nothing is adopted, nothing is applied to Clusters
  2/3** (condition not met), and nothing is carried
  into a whole-month run on its own. The best variant
  by the pass bar is none — there is no variant that
  is even close on conversion. The least-damaging
  variant for winners is CT-10 (see below), but it
  converts 0/8, so it is recorded as a winner-preservation
  observation, not as a candidate.

## The proof before the results: the close-favourable ceiling

For each Cluster 1 day, the maximum (entry − close) on
bars BEFORE the stop bar, in × original risk. No
close-based trigger above this ceiling can ever arm
on that day, and no close-based exit can ever fire
before the stop on that day:

| Date | Risk (pts) | Max close fav before stop | × risk | At |
|---|---|---|---|---|
| 2026-01-09 | 37.05 | 5.95 pts | 0.161× | 09:35 |
| 2026-02-06 | 22.35 | 17.15 pts | 0.767× | 09:40 |
| 2026-03-30 | 20.15 | 0.00 pts | 0.000× | — |
| 2026-04-02 (Skill) | 20.75 | 0.00 pts | 0.000× | — |
| 2026-05-13 | 50.35 | 60.80 pts | 1.208× | 09:35 |
| 2026-06-29 | 47.00 | 0.00 pts | 0.000× | — |
| 2026-07-08 | 19.45 | 4.30 pts | 0.221× | 09:35 |
| 2026-08-19 | 22.60 | 0.00 pts | 0.000× | — |

Reading: 4 of 8 days never close favourably at all
before the stop (0.00×). 2 more close at most
0.16–0.22× risk favourably. Only 2 days (6 Feb,
13 May) ever close ≥0.5× risk favourably before
the stop — and 6 Feb's next bar hits the stop
intraday before any close-lock can exit, while
13 May's close-lock exit is a loss (below). So
the maximum conversion any close-based exit can
achieve on Cluster 1, before even running it, is
bounded well below 60%: at most 1 day (13 May)
can even reach a lock exit, and that exit is not
green. Any future exit-only rule — close-based or
intraday — faces the same ceiling in a different
form: 6 of 8 Cluster 1 days simply do not move
favourably on a close before they stop. The next
family must therefore change the entry or the
stop, not the exit (see "Next family" below).

## Close-execution warning — a close "lock" is not a locked price

This matters for reading every close-trail number
below, and it is why the intraday trail's 4/8
conversion does NOT carry over to closes. An
intraday trail exits AT the lock price the moment
the high touches it. A close-only trail cannot:
it learns the retracement only at the bar close,
and it must exit at that close price, which has
already overshot the lock. On 13 May the lock
(0.25× risk = entry − 12.59) is armed on the
09:35 close (fav 1.208× risk), but the exit close
at 09:50 is 23,367.60 — ABOVE entry (23,337.30) —
so the "locked" exit books −₹3,070, not a
+0.25× profit. A close-based lock is a
retracement trigger, not a guaranteed profit
floor. Any future close-trail claim that quotes
the lock distance as the booked profit is wrong
on this data.

## Definitions, so these are not re-runs of the intraday trail

Ordering per bar (conservative, stated before the
results): (1) intraday high ≥ original stop →
stop (stop wins over a close-lock); (2) intraday
low ≤ target → target; (3) at bar close, update
arm/lock from the CLOSE only, then — old-lock
check FIRST — if a lock armed on an earlier bar
is breached by this close, exit at this close;
a lock armed on bar k cannot exit on bar k
itself; (4) square-off at 15:10 close. For the
ratchet, the old-lock check before the lock
update is essential: a close that falls from
1.5× fav to 0.6× fav breaches the 1.0× lock and
must exit at that close, not silently keep the
trade because the new close still qualifies for
a smaller step.

- **CT-05:** close fav ≥ 0.5× risk → lock 0.25× risk.
- **CT-10:** close fav ≥ 1.0× risk → lock 0.50× risk.
- **CT-RATCHET-CLOSE:** stepped on closes: fav ≥0.5
  → lock 0.25; fav ≥1.0 → lock 0.50; fav ≥1.5 →
  lock 1.00 (lock only ever moves in the trade's
  favour; old-lock check as above).
- **CT-ARM-SIG:** lock arms ONLY when a bar closes
  below the SIGNAL bar's low; then lock 0.25×
  risk, exit on a later close ≥ lock. Original
  stop and target stay active throughout — the
  lock is an additional exit, not a stop
  replacement. A wobble that never closes below
  the signal low cannot arm the lock at all.
- **CT-ARM-SIG-RATCHET:** same arm (close below
  signal low), stepped locks 0.25/0.50/1.00 by
  close fav after arming (floor 0.25 on arming).
- **S-ORAVG:** risk unit = mean range (high−low)
  of the 3 OR bars (09:15, 09:20, 09:25), known
  at entry; stop = entry + risk unit, target =
  entry − 2× risk unit, 100 shares, no trail.
- **S-PD10:** risk unit = 0.10 × previous-day
  range (high−low), known at entry; same
  stop/target formula.
- **S-ORAVG-CAP:** risk unit = min(mean OR-bar
  range, original risk).

## Results — Families (a) and (b): close-based trails

| Variant | Cluster 1 green | No-trade | Still loss | Cluster 1 total (₹) | Winners green | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | 14/14 | +91,270 | +66,980 | — |
| CT-05: close 0.5×→0.25× | 0/8 | 0 | 8 | −22,285 | 12/14 | +48,255 | +25,970 | No |
| CT-10: close 1.0×→0.50× | 0/8 | 0 | 8 | −22,285 | 14/14 | +80,780 | +58,495 | No |
| CT-RATCHET-CLOSE: stepped closes | 0/8 | 0 | 8 | −22,285 | 13/14 | +45,885 | +23,600 | No |
| CT-ARM-SIG: arm on close < signal low, lock 0.25× | 0/8 | 0 | 8 | −22,285 | 12/14 | +39,000 | +16,715 | No |
| CT-ARM-SIG-RATCHET: same arm, stepped | 0/8 | 0 | 8 | −22,285 | 12/14 | +35,125 | +12,840 | No |

All five variants have the identical Cluster 1 day
nets — this is the ceiling, not a copy error:

| Date | Original | Every CT variant |
|---|---|---|
| 2026-01-09 | −₹3,745 | −₹3,745 (stop 09:40; max close fav 0.161×, never arms) |
| 2026-02-06 | −₹2,275 | −₹2,275 (stop 09:45; arms on 09:40 close fav 0.767×, next bar's high hits stop before any close-lock can exit) |
| 2026-03-30 | −₹2,055 | −₹2,055 (stop 11:30; max close fav 0.00×, never arms) |
| 2026-04-02 (Skill) | −₹2,115 | −₹2,115 (stop 10:00; max close fav 0.00×, never arms) |
| 2026-05-13 | −₹5,075 | −₹3,070 (close_lock 09:50 at 23,367.60 — above entry, still a loss; see close-execution warning) |
| 2026-06-29 | −₹4,740 | −₹4,740 (stop 09:40; max close fav 0.00×, never arms) |
| 2026-07-08 | −₹1,985 | −₹1,985 (stop 09:45; max close fav 0.221×, never arms) |
| 2026-08-19 | −₹2,300 | −₹2,300 (stop 09:50; max close fav 0.00×, never arms) |

Why the variants coincide on Cluster 1: the only
day that arms under ANY trigger (13 May, close
fav 1.208× at 09:35) arms under every trigger
(0.5×, 1.0×, ratchet, signal-low — its 09:35
close, 23,276.50, is below its signal low
23,335.70), and its exit close (09:50, 23,367.60)
is the same regardless of lock distance, because
the exit price is the close, not the lock. The
only other arming day (6 Feb) is stopped on the
next bar under every variant. Trigger choice is
therefore irrelevant on Cluster 1 — the binding
constraint is the close-favourable ceiling, not
the trigger level.

Winner damage — this is where the variants DO
differ, and it is the one respect in which the
close hypothesis was partly right:

- **CT-10 preserves winners best: 14/14, +₹80,780
  (88.5% of baseline).** Only 2 close-lock exits
  (24 Feb +₹1,685 vs +₹7,350; 22 Jul +₹1,495 vs
  +₹6,320); the other 12 reach target. Waiting
  for a 1.0× close before arming lets most
  winners reach target before any retracement
  close can exit them — unlike the intraday
  trail, where the first intraday wobble to the
  lock exits every winner (T-A: +₹10,919).
  But CT-10 converts 0/8 on Cluster 1, so this
  is a winner-preservation observation, NOT a
  candidate: a rule that preserves winners while
  converting nothing does not meet the pass bar.
- **CT-05: 12/14, +₹48,255 (52.9% of baseline).**
  6 close-lock exits; 2 winners flip to losses
  on close-lock overshoot (5 May −₹1,090 vs
  +₹5,040; 22 Jul −₹10 vs +₹6,320 — the close
  that breaches the lock is above entry, so the
  "locked" exit books a loss). The 0.5× close
  trigger arms too early, on the first
  favourable close, before the winner has run.
- **CT-RATCHET-CLOSE: 13/14, +₹45,885 (50.3%).**
  The ratchet is WORSE than CT-10 and worse
  than CT-05 on total, for the same reason the
  intraday ratchet failed: its first step
  (0.5×→0.25×) arms early, and the close that
  breaches that first lock exits the trade
  before it can ever reach the 1.0×/1.5× steps
  that would raise the lock. 7 close-lock exits
  (only 7 targets survive); 5 May flips to
  −₹1,090. Stepping on closes does not fix
  stepping on intraday lows — the first step
  is still the step that exits the trade.
- **CT-ARM-SIG: 12/14, +₹39,000 (42.7%).** 7
  close-lock exits; 2 flips to losses (24 Feb
  −₹1,295 vs +₹7,350; 5 May −₹600 vs +₹5,040).
  Arming on a close below the signal low arms
  on the entry bar itself on many winner days
  (the entry bar's close is frequently below
  the signal low), so the "stricter" arm is in
  practice an EARLIER arm than CT-10's 1.0×
  close trigger. Family (b)'s premise — that
  a level arm is stricter than a distance arm —
  is false on this data: the signal low is so
  close to entry that closing below it is easy.
- **CT-ARM-SIG-RATCHET: 12/14, +₹35,125
  (38.5%).** 8 close-lock exits, 6 targets; same
  2 flips as CT-ARM-SIG, plus 8 Oct cut to
  +₹1,565 (vs +₹5,440) on a ratchet close-lock.
  The worst winner total in family (a)/(b).

## Results — Family (c): pre-signal sizing

| Variant | Cluster 1 green | No-trade | Still loss | Cluster 1 total (₹) | Winners green | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | 14/14 | +91,270 | +66,980 | — |
| S-ORAVG: mean OR-bar range | 2/8 | 0 | 6 | −23,140 | 11/14 | +85,070 | +61,930 | No |
| S-PD10: 10% of prev-day range | 0/8 | 0 | 8 | −21,176 | 9/14 | +36,588 | +15,412 | No |
| S-ORAVG-CAP: min(OR-avg, orig risk) | 0/8 | 0 | 8 | −24,242 | 14/14 | +91,210 | +66,968 | No |

### S-ORAVG — risk units and day nets (Cluster 1)

Mean OR-bar range is 35.57–91.87 points, vs
original risk 19.45–50.35 points — on 7 of 8 days
it is LARGER than the original risk, so the sized
stop is wider and the sized target (2×) is much
further away:

| Date | Orig risk | OR-avg risk unit | Sized stop / target | Net (orig → sized) | Exit |
|---|---|---|---|---|---|
| 2026-01-09 | 37.05 | 70.37 | stop 25,906.42 / target 25,695.31 | −₹3,745 → **+₹14,033** | target 12:35 |
| 2026-02-06 | 22.35 | 42.37 | stop 25,585.82 / target 25,458.71 | −₹2,275 → −₹4,277 | stop 11:20 |
| 2026-03-30 | 20.15 | 90.90 | stop 22,559.00 / target 22,286.30 | −₹2,055 → −₹9,130 | stop 12:00 |
| 2026-04-02 (Skill) | 20.75 | 83.70 | stop 22,290.50 / target 22,039.40 | −₹2,115 → −₹8,410 | stop 11:55 |
| 2026-05-13 | 50.35 | 91.87 | stop 23,429.17 / target 23,153.56 | −₹5,075 → −₹9,227 | stop 10:15 |
| 2026-06-29 | 47.00 | 46.52 | stop 24,065.22 / target 23,925.66 | −₹4,740 → −₹4,692 | stop 09:40 |
| 2026-07-08 | 19.45 | 41.43 | stop 24,262.88 / target 24,138.59 | −₹1,985 → −₹4,183 | stop 09:50 |
| 2026-08-19 | 22.60 | 35.57 | stop 24,111.97 / target 24,005.26 | −₹2,300 → **+₹2,745** | square-off 15:10 |

The 2 greens do not make a pass. 9 Jan's
+₹14,033 is a genuine target, but at a 140.74-
point target distance — a different trade scale
from the original 74.10-point target — and it is
bought with 5 much larger stops (−₹4,277 to
−₹9,227). 19 Aug's +₹2,745 is a square-off at
15:10, not a target. Winners under S-ORAVG:
11/14, +₹85,070 (93.2% of baseline) — 3 flips
to stops (16 Mar −₹8,785 vs +₹8,940; 5 May
−₹7,383 vs +₹5,040; 29 Sep −₹4,922 vs +₹3,790),
because the wider target (2× a 36–102 point
risk unit) is out of reach on days the original
target caught. Combined +₹61,930 is BELOW
baseline +₹66,980 despite the 2 greens. Sizing
by OR-bar range widens both legs of the trade
and, on balance, loses.

### S-PD10 — risk units and day nets (Cluster 1)

10% of previous-day range is 11.48–40.91 points
— smaller than original risk on 6 of 8 days,
larger only on 30 Mar (38.15 vs 20.15) and
2 Apr (32.27 vs 20.75):

| Date | Orig risk | PD10 risk unit | Net (orig → sized) | Exit |
|---|---|---|---|---|
| 2026-01-09 | 37.05 | 27.48 | −₹3,745 → −₹2,788 | stop 09:40 |
| 2026-02-06 | 22.35 | 17.82 | −₹2,275 → −₹1,822 | stop 09:45 |
| 2026-03-30 | 20.15 | 38.15 | −₹2,055 → −₹3,856 | stop 11:30 |
| 2026-04-02 (Skill) | 20.75 | 32.27 | −₹2,115 → −₹3,267 | stop 10:55 |
| 2026-05-13 | 50.35 | 40.91 | −₹5,075 → −₹4,132 | stop 09:55 |
| 2026-06-29 | 47.00 | 22.26 | −₹4,740 → −₹2,266 | stop 09:35 |
| 2026-07-08 | 19.45 | 18.20 | −₹1,985 → −₹1,860 | stop 09:45 |
| 2026-08-19 | 22.60 | 11.48 | −₹2,300 → −₹1,188 | stop 09:40 |

0/8 green, total −₹21,176 (+₹3,114 vs baseline
by shrinking losses, not by converting any).
Winners collapse to 9/14, +₹36,588 (40.1% of
baseline): 5 flips to stops (24 Feb −₹1,661;
22 Jul −₹1,306; 12 Aug −₹1,516; 29 Sep −₹3,221;
8 Oct −₹1,754), because the smaller risk unit
tightens the stop on most winner days below the
original signal-high stop that those winners
survived. Combined +₹15,412 is far below
baseline. A pre-signal risk unit that is
usually SMALLER than the signal risk is a stop
tightener, not a fix.

### S-ORAVG-CAP — why it is baseline in disguise

Risk unit = min(mean OR-bar range, original
risk). Mean OR-bar range exceeds original risk
on 7 of 8 Cluster 1 days (exception: 29 Jun,
46.52 vs 47.00, net −₹4,692 vs −₹4,740) and on
13 of 14 winner days (exception: 23 Oct, 56.85
vs 57.15, net +₹11,330 vs +₹11,390), so the cap
binds back to the original risk almost
everywhere: Cluster 1 0/8, −₹24,242 (baseline
−₹24,290, difference +₹48 from those 2 days
only); winners 14/14, +₹91,210 (baseline
+₹91,270, difference −₹60). Combined +₹66,968
vs baseline +₹66,980. This variant proves the
negative: OR-bar range is not a useful risk
unit at all — uncapped it widens the trade and
loses on balance, capped it disappears. It is
not a candidate, it is a control that confirms
the original signal-high risk is, on these
days, already tighter than the OR's own bars.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to
Clusters 2/3 only if it reaches 60% on Cluster 1
with positive economics. No variant did (best
conversion 2/8, every variant's Cluster 1 total
still negative, and every variant that greens
at all either widens losses elsewhere or
collapses winners), so no variant is carried
into Cluster 2 (reclaim failure, 2 trades,
−₹11,420) or Cluster 3 (slow give-back, 3
trades, −₹10,585) as a fix. For the record,
the close-trail variants are PE-breakdown exits
and would not in any case apply to Cluster 2's
CE reclaim trades without a mirrored (long-side)
definition, which was not tested here; and
Cluster 3's give-back problem is an exit
problem on trades that DO move favourably for
hours, the opposite of Cluster 1's never-move
problem — a rule that fails on Cluster 1's
never-move days cannot be assumed to fix
Cluster 3's give-back days.

## Variant summary — families (a)–(c) in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| CT-05 close 0.5×→0.25× | 0/8 | −22,285 | +48,255 | +25,970 | No |
| CT-10 close 1.0×→0.50× | 0/8 | −22,285 | +80,780 | +58,495 | No — best winner preservation, 0 conversion |
| CT-RATCHET-CLOSE stepped closes | 0/8 | −22,285 | +45,885 | +23,600 | No |
| CT-ARM-SIG arm on close < signal low | 0/8 | −22,285 | +39,000 | +16,715 | No |
| CT-ARM-SIG-RATCHET same arm, stepped | 0/8 | −22,285 | +35,125 | +12,840 | No |
| S-ORAVG mean OR-bar range | 2/8 | −23,140 | +85,070 | +61,930 | No — greens are 1 widened target + 1 square-off, combined below baseline |
| S-PD10 10% of prev-day range | 0/8 | −21,176 | +36,588 | +15,412 | No — loss-shrink only, winners collapsed |
| S-ORAVG-CAP min(OR-avg, orig risk) | 0/8 | −24,242 | +91,210 | +66,968 | No — baseline in disguise |

## What this sweep proves, and what it does not

- A close-based trail does NOT rescue the
  intraday trail's conversion. The intraday
  trail's 4/8 came from intraday lows that
  reached 0.5× risk favourably and then
  retraced to a lock price intraday. On closes,
  those same days mostly never close ≥0.5×
  favourably before the stop (ceiling table
  above), and the one day that does (13 May)
  exits at a loss because a close exit
  overshoots its lock. Moving the trigger from
  lows to closes removes the conversion
  entirely (4/8 → 0/8) while improving winner
  preservation at the high trigger (CT-10:
  88.5% of baseline winners, vs 12% for
  intraday T-A). That trade-off is now
  measured, not guessed: close triggers
  preserve winners, intraday triggers convert
  (some) losses — neither does both.
- A level arm (close below signal low) is not
  stricter than a distance arm on this data.
  It arms on the entry bar on many winner days
  and therefore damages winners more than
  CT-10 (42.7% vs 88.5% of baseline), while
  changing nothing on Cluster 1. Do not
  re-propose signal-low arming as a "stricter"
  variant without a level that is actually
  further from entry than the signal low.
- Pre-signal sizing does not fix the morning
  trade. OR-bar range is too wide (wider stops,
  unreachable targets, combined below baseline
  despite 2 greens); 10% of previous-day range
  is usually too tight (smaller stops, 5 winner
  flips, combined +₹15,412); capped OR-bar
  range is baseline. The signal candle's own
  high — the original risk — is not obviously
  the wrong risk unit; the failure is that the
  bounce retraces through it in 1–5 bars, and
  no risk unit measured before the signal can
  know how far that bounce will run.
- What remains untested for Cluster 1 after
  this sweep — the next family, NOT a re-run
  of the above: (i) a CLOSE-confirmed
  re-entry, distinct from the intraday re-entry
  already tested: after a stop, enter again
  ONLY if a later bar CLOSES below the OR low
  (counted as a separate trade, first loss
  kept, not netted silently); (ii) a signal-
  quality filter on the signal itself — signal
  close distance below the OR low, and/or OR
  width band — tested honestly as a no-trade
  filter, with no-trade counted separately
  from green, so it cannot falsely pass the
  60% green bar by avoidance alone; (iii) on
  the entry side, a trade that waits for the
  bounce bar to CLOSE before entering at its
  close price (not its next open) — a
  different entry price from the delayed-open
  entries already tested. Those are the next
  families, not re-runs of close trails,
  signal-low arming, OR-bar or previous-day
  sizing, intraday trails, or bounce sizing,
  and not another re-entry+partial combination.

Files: engine `close_trail_sweep.py`, raw replay
`close_trail_sweep_raw.json`. Paper only throughout;
no orders placed, nothing fabricated. The long-horizon
task continues in the parent conversation: Families
(a)–(c) in this task are exhausted, and the next
decision is which untried family to run — and none
of the variants in this report is adopted.
