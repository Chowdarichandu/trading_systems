# NIFTY — Re-entry filtered by its own risk + signal-low re-entry + Bank Nifty cross-confirmation (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): previous family done
(`nifty_cluster1_close_reentry_sweep.md`) — best day-green 2/8
(25%), not 5/8. Honesty correction carried forward: family (i)
there was NOT new — prior `stop_sweep` re-entry was already
close-confirmed, so RE-BASE reproduces it (2/8, −₹16,345; prior
report total −₹17,355 appears ₹1,010 out, day nets agree, verdict
unchanged). RE-2C worse (1/8), RE-PDL identical to RE-BASE,
RE-EXT worse (2/8, −₹18,450). Signal-quality filter 0/8 by
construction. Bounce-bar-close entry 0/8, BC-B destroys winners
(5/14, −₹185). Nothing adopted, nothing carried to a whole-month
run.

This task, Nifty only, paper only, same pass bar (**60% green
AND total positive AND winners not collapsed**):
(a) re-entry filtered by its OWN risk, (b) re-entry requiring a
close below the SIGNAL BAR'S LOW, (c) cross-instrument
confirmation for the morning trade itself (Bank Nifty). For each
variant replay all 8 Cluster 1 days + 14 winners bar by bar,
report green / no-trade / still loss, cluster total, winner
total, combined total, with no-trade counted separately from
green. If a variant passes on Cluster 1 with positive
economics, apply to Clusters 2/3. If none passes, report best
variant and next family — task continues in parent
conversation, do NOT present exhaustion as completion.

Engine: `reentry_filter_sweep.py`, raw replay
`reentry_filter_sweep_raw.json`. Replayed bar by bar from the
Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv` and
`data/progressive/BANKNIFTY/spot_5m.csv`), same signal scan as
all prior sweeps (V4 setup2 PE breakdown: close < OR low,
close < PDL, room ≥ 200×scale, OR width ≤ 360×scale, signal
≤ 11:30; 2026-04-02 Skill, 2026-03-23 Skill winner). Entry =
next bar open unless a variant says otherwise, original stop =
signal high (PE), original target = entry − 2×risk, stop checked
before target on each bar including the entry bar, square-off
15:10, 100 shares equivalent, ₹40/trade. Green = net > ₹0.
Cluster 1 baseline: 8 trades, 0/8 green, total −₹24,290.
Winners baseline: 14 V5 Nifty PE target days, 14/14 green,
total +₹91,270. Baseline combined PE: +₹66,980.
Re-entry baseline (RE-BASE, reference only, prior rule): first
bar after the stop whose close < OR low, to 11:30; day-green
2/8, day total −₹16,345, combined +₹74,925.

## Headline — families (a)–(c) all exhausted, nothing passes, nothing adopted

- **Best day-green in the whole sweep is 3/8 (37.5%), not 5/8.**
  That is RF-MIN10-SCAN and RF-BAND-SCAN (see below). Every
  other variant is 0–2/8. No variant reaches the 60% green
  bar, so **no variant is applied to Clusters 2/3 and nothing
  is carried into a whole-month run on its own.**
- **Best Cluster 1 total is still negative:** RF-BAND-SCAN
  −₹7,425 (combined +₹83,845, because winners are untouched
  by a re-entry-only rule). A combined total above baseline
  with a still-negative Cluster 1 total and only 3/8 day-green
  is NOT a pass — it is loss-shrink plus unchanged winners,
  not conversion of the failing cluster.
- **Family (b) is 0/8 day-green and slightly worse than
  baseline in total** (−₹24,895 vs −₹24,290). A close below
  the signal bar's low is a deeper confirmation, but on these
  days it mostly removes the re-entries that worked (29 Jun
  gets none) and keeps two small re-entry targets that still
  do not cover the original loss.
- **Family (c) is 0/8 green in every version, filter and
  rescan alike.** Bank Nifty already breaks down at 09:30 on
  5 of the 8 Cluster 1 days — confirmation from outside the
  Nifty candle is already present on the losing days, so it
  cannot separate them. FILTER versions are 0/8 by
  construction (a filter on the original trade can only
  no-trade, never green); RESCAN versions, which could in
  principle green via a later signal, green 0/8 in practice
  and RESCAN-PDL is worse than baseline in total (−₹25,935).
  Cross-confirmation also costs winners: FILTER keeps only
  9/14 winners (+₹66,240), RESCAN-ORL keeps 12/14 (+₹83,380),
  RESCAN-PDL keeps 10/14 (+₹68,710) — every XC combined
  total is BELOW baseline (+₹66,980) except none: FILTER
  combined +₹46,340, RESCAN-ORL +₹59,605, RESCAN-PDL
  +₹42,775.

## Definitions, stated before the results

### (a) Re-entry filtered by its own risk — Trade 1 is always the baseline trade

Re-entry candidate = first bar after the stop bar whose close
< OR low, window to 11:30, entry = next bar open, stop = that
bar's high, target = entry − 2×risk, ₹40 cost again. Day net =
Trade 1 net + re-entry net. No re-entry ⇒ day = Trade 1 net.
The filter is applied to the re-entry's OWN risk (stop − entry
of the re-entry bar), not to the original trade's risk.
Original risks for reference: 9 Jan 37.05, 6 Feb 22.35,
30 Mar 20.15, 2 Apr 20.75, 13 May 50.35, 29 Jun 47.00,
8 Jul 19.45, 19 Aug 22.60 points. RE-BASE re-entry risks for
reference: 9 Jan 30.40, 6 Feb 2.25, 2 Apr 29.10, 29 Jun 34.40,
8 Jul 27.00, 19 Aug 5.30 points — the two tiny risks the task
names are 6 Feb (2.25) and 19 Aug (5.30).

Two readings of "skip" are tested separately, because they are
different rules and only one of them can find a later re-entry:

- **-DAY:** the FIRST re-entry candidate is tested against the
  filter; if it fails, there is NO re-entry that day (no
  scanning for a later candidate).
- **-SCAN:** a failing candidate is skipped and scanning
  CONTINUES for the next close < OR low that passes the
  filter (to 11:30).

Filter variants:

- **RF-MIN10:** re-entry risk ≥ 10 points.
- **RF-BAND:** 10 points ≤ re-entry risk ≤ original risk
  (both the tiny-risk skip AND the exceeds-original skip).
- **RF-MAXORIG:** re-entry risk ≤ original risk only
  (tiny risks kept, oversized risks skipped).

Winners under every (a) variant: unchanged (14/14, +₹91,270)
— a winner never stops, so no re-entry triggers. Combined PE
total for (a) variants is therefore Cluster 1 day total +
₹91,270, stated not hidden.

### (b) Re-entry requiring a close below the signal bar's low — RB-SIGLOW

- First bar after the stop bar whose close < the ORIGINAL
  signal bar's LOW (not just < OR low), window to 11:30;
  entry = next bar open, stop = that bar's high, target =
  entry − 2×risk, ₹40 cost again. Day net = Trade 1 + re-entry.
- This is distinct from RE-PDL in the prior sweep, which
  turned out identical to RE-BASE because PDL was already
  below OR low on these days. Signal low is a different,
  tighter level: signal low < signal close < OR low, so a
  close below signal low is strictly deeper than a close
  below OR low. Signal lows: 9 Jan 25,820.80, 6 Feb
  25,534.20, 30 Mar 22,465.80, 2 Apr 22,205.55, 13 May
  23,335.70, 29 Jun 24,016.80, 8 Jul 24,215.30,
  19 Aug 24,071.75.
- Winners under RB-SIGLOW: unchanged (14/14, +₹91,270), same
  reason as (a).

### (c) Cross-instrument confirmation — Bank Nifty

Bank Nifty OR = 09:15–09:30 high/low from the BANKNIFTY 5-min
cache; Bank Nifty previous-day levels from its daily cache.
Bank Nifty breakdown = first bar ≥ 09:30, ≤ 11:30, whose close
< Bank Nifty OR low (mode ORL), or < OR low AND < Bank Nifty
PDL (mode PDL, the V4-like stricter version).

- **XC-FILTER:** original Nifty trade is kept ONLY if Bank
  Nifty broke down at or before the Nifty signal bar time;
  otherwise the day is a no-trade and NO later signal is
  sought. Like SQ, this can only avoid, never green — its
  0/8 is by construction, and its totals are avoidance
  totals, always read with the winner column.
- **XC-RESCAN:** the Nifty trade is the FIRST V4/Skill
  breakdown bar at or after the Bank Nifty breakdown bar
  time (≤ 11:30); entry, stop, target as baseline. This is
  the only XC version that could green via a later signal,
  and it is the honest test of "Bank Nifty confirmation"
  as an entry rule rather than as a filter.
- Winners are replayed under the same XC rule on their own
  days (same Bank Nifty data, same mode), so winner damage
  is measured, not assumed away.

## Results — (a) Re-entry risk filter, Cluster 1 (8 days, baseline 0/8, −₹24,290)

| Variant | Re-entry alone green | Day green | No re-entry | Day total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| Baseline (no re-entry) | — | 0/8 | — | −24,290 | +66,980 | — |
| RE-BASE (reference, prior rule) | 3/6 traded | 2/8 | 2 | −16,345 | +74,925 | No |
| RF-MIN10-SCAN | 3/6 traded | 3/8 | 2 | −15,730 | +75,540 | No |
| RF-MIN10-DAY | 2/4 traded | 2/8 | 4 | −17,100 | +74,170 | No |
| RF-BAND-SCAN | 4/5 traded | 3/8 | 3 | −7,425 | +83,845 | No — best total, still 3/8 and still negative |
| RF-BAND-DAY | 2/2 traded | 2/8 | 6 | −11,410 | +79,860 | No |
| RF-MAXORIG-SCAN | 3/5 traded | 2/8 | 3 | −12,720 | +78,550 | No |
| RF-MAXORIG-DAY | 3/4 traded | 2/8 | 4 | −10,655 | +80,615 | No |

Day-by-day, RF-BAND-SCAN (best total) and RF-MIN10-SCAN (joint-best day-green):

| Date | Trade 1 | RF-BAND-SCAN re-entry → result | RF-BAND-SCAN day net | RF-MIN10-SCAN re-entry → result | RF-MIN10-SCAN day net |
|---|---|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50, risk 30.40 → target | +2,295 GREEN | 10:50, risk 30.40 → target | +2,295 GREEN |
| 2026-02-06 | −2,275 | 10:05, risk 10.60 → target +2,080 | −195 (re-entry green, day still loss) | 10:00, risk 25.60 → stop −2,600 | −4,875 |
| 2026-03-30 | −2,055 | none | −2,055 | none | −2,055 |
| 2026-04-02 | −2,115 | 10:45, risk 20.25 → stop −2,065 | −4,180 | 10:05, risk 29.10 → stop −2,950 | −5,065 |
| 2026-05-13 | −5,075 | none | −5,075 | none | −5,075 |
| 2026-06-29 | −4,740 | 11:30, risk 34.40 → target | +2,100 GREEN | 11:30, risk 34.40 → target | +2,100 GREEN |
| 2026-07-08 | −1,985 | none (first candidate risk 27.00 > orig 19.45, no later in-band candidate by 11:30) | −1,985 | 10:20, risk 27.00 → stop −2,740 | −4,725 |
| 2026-08-19 | −2,300 | 10:15, risk 20.05 → target | +1,670 GREEN | 10:15, risk 20.05 → target | +1,670 GREEN |

Why scanning beats first-only, and why it still stops at 3/8:
scanning past the tiny 19 Aug candidate (10:10, risk 5.30) finds
the 10:15 candidate (risk 20.05, target +₹3,970) and turns 19 Aug
from a −₹1,280 day (RE-BASE) into a +₹1,670 day — that is the
one genuine conversion the risk filter adds over RE-BASE, and it
is the reason both -SCAN variants reach 3/8 while every -DAY
variant stays at 2/8. But scanning also hurts: on 6 Feb,
MIN10-SCAN skips the tiny 09:55 candidate and takes a 10:00
candidate that stops (−₹2,600, day −₹4,875, worse than RE-BASE
day −₹2,540 and worse than BAND-SCAN day −₹195). And no risk
filter can touch 30 Mar or 13 May (no re-entry at all), or turn
2 Apr / 8 Jul green (their in-band re-entries still stop).
Filtering re-entry risk is therefore a loss-shrink and a
single-day conversion, not a cluster fix: the ceiling moves
from 2/8 to 3/8, still 2 short of 5/8, and the best total is
still negative.

Why RF-BAND-SCAN's total (−₹7,425) must not be read as a pass
on its own: it is the best Cluster 1 total in this sweep only
because it avoids the two worst re-entry stops (8 Jul's
oversized 27.00-point re-entry and, via the band, the
second-worst outcomes) while keeping the three targets — but
the cluster still loses money in total, 5 of 8 days still
lose, and the combined +₹83,845 is Cluster 1 (−₹7,425) plus
winners that this rule never touches (+₹91,270). Quoting the
combined total without the 3/8 and the negative cluster total
would repeat the avoidance-total error flagged in the prior
sweep.

## Results — (b) Signal-low re-entry, Cluster 1 (baseline 0/8, −₹24,290)

| Variant | Re-entry alone green | Day green | No re-entry | Day total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| RB-SIGLOW | 2/3 traded | 0/8 | 5 | −24,895 | +66,375 | No — worse total than baseline |

Day-by-day, RB-SIGLOW:

| Date | Signal low | Re-entry signal → result | Day net |
|---|---|---|---|
| 2026-01-09 | 25,820.80 | 11:00, risk 11.05 → stop −1,145 | −4,890 (worse than baseline −3,745) |
| 2026-02-06 | 25,534.20 | 10:05, risk 10.60 → target +2,080 | −195 (re-entry green, day still loss) |
| 2026-03-30 | 22,465.80 | none (never closes below signal low by 11:30) | −2,055 |
| 2026-04-02 | 22,205.55 | 10:05, risk 29.10 → stop −2,950 (same as RE-BASE) | −5,065 |
| 2026-05-13 | 23,335.70 | none | −5,075 |
| 2026-06-29 | 24,016.80 | none — the 11:30 RE-BASE re-entry (target +6,840) does NOT qualify, because its close is below OR low but not below signal low | −4,740 (the working re-entry is lost) |
| 2026-07-08 | 24,215.30 | none | −1,985 |
| 2026-08-19 | 24,071.75 | 10:20, risk 7.25 → target +1,410 | −890 (re-entry green, day still loss) |

Why RB-SIGLOW fails: the deeper confirmation mostly does not
arrive (5 of 8 days get no re-entry at all), and where it does
arrive it is either too late/small to cover the original loss
(6 Feb, 19 Aug: re-entry targets that leave the day at −₹195
and −₹890) or a fresh stop (9 Jan). Worst, it removes the one
re-entry that did work at scale: 29 Jun's 11:30 re-entry
closes below OR low (24,032.35) but above signal low
(24,016.80), so the stricter rule deletes a +₹6,840 target
and hands the day back to −₹4,740. Deeper confirmation on the
re-entry is not a stricter version of a working rule — on
this data it is a rule that deletes the working cases.
Combined +₹66,375 is below baseline +₹66,980, so even the
combined leg goes backwards.

## Results — (c) Bank Nifty cross-confirmation, Cluster 1 + winners

### Cluster 1 (8 days, baseline 0/8, −₹24,290)

| Variant | Green | No-trade | Still loss | Cluster 1 total (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | — |
| XC-FILTER-ORL | 0/8 | 2 | 6 | −19,900 | No — avoidance only, by construction |
| XC-FILTER-PDL | 0/8 | 2 | 6 | −19,900 | No — avoidance only, by construction |
| XC-RESCAN-ORL | 0/8 | 0 | 8 | −23,775 | No |
| XC-RESCAN-PDL | 0/8 | 0 | 8 | −25,935 | No — worse than baseline |

Day-by-day, XC Cluster 1 (Bank Nifty break time = first BN bar
close < BN OR low, resp. < BN OR low and < BN PDL):

| Date | Nifty orig signal / net | BN break ORL | BN break PDL | FILTER kept? | RESCAN-ORL signal / net | RESCAN-PDL signal / net |
|---|---|---|---|---|---|---|
| 2026-01-09 | 09:30 / −3,745 | 09:30 | 09:30 | yes | 09:30 / −3,745 | 09:30 / −3,745 |
| 2026-02-06 | 09:35 / −2,275 | 10:10 | 10:25 | no (break after signal) | 10:10 / −1,810 | 10:25 / −3,970 |
| 2026-03-30 | 11:25 / −2,055 | 10:50 | 10:50 | yes | 11:25 / −2,055 | 11:25 / −2,055 |
| 2026-04-02 | 09:55 / −2,115 | 10:45 | 10:45 | no (break after signal) | 10:45 / −2,065 | 10:45 / −2,065 |
| 2026-05-13 | 09:30 / −5,075 | 09:30 | 09:30 | yes | 09:30 / −5,075 | 09:30 / −5,075 |
| 2026-06-29 | 09:30 / −4,740 | 09:30 | 09:30 | yes | 09:30 / −4,740 | 09:30 / −4,740 |
| 2026-07-08 | 09:30 / −1,985 | 09:30 | 09:30 | yes | 09:30 / −1,985 | 09:30 / −1,985 |
| 2026-08-19 | 09:30 / −2,300 | 09:30 | 09:30 | yes | 09:30 / −2,300 | 09:30 / −2,300 |

Why (c) cannot work on this cluster: Bank Nifty breaks down at
09:30 on 5 of the 8 losing days (9 Jan, 13 May, 29 Jun, 8 Jul,
19 Aug) — the cross-confirmation the task hypothesised is
already present on the majority of losers, so requiring it
keeps those losses unchanged. The only days it removes are
6 Feb and 2 Apr, where Bank Nifty breaks later than Nifty
(10:10 / 10:45) — and removing two losses by no-trade is
avoidance, not conversion, which is why FILTER totals
(−₹19,900) must not be quoted as greens. RESCAN does not
rescue the other six: on 6 Feb it finds a later Nifty signal
(10:10 ORL, −₹1,810; 10:25 PDL, −₹3,970, worse than the
original −₹2,275) and on 2 Apr a 10:45 signal (−₹2,065, a
₹50 improvement, still a loss); the other six days replay
identically. Making the Bank Nifty condition stricter (PDL)
only delays the 6 Feb signal into a larger loss. A
confirmation that is present at 09:30 on 5/8 losers, yet
Bank Nifty never breaks down at all by 11:30 on 2 winners
(24 Feb, 12 Aug) and breaks only after the Nifty signal on
3 more, is not a separator in either direction — it is a
correlated market-open fact, not a quality signal.

### Winners under XC (14 days, baseline 14/14, +₹91,270)

| Variant | Green | No-trade | Still loss | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| Baseline | 14/14 | 0 | 0 | +91,270 | +66,980 | — |
| XC-FILTER-ORL | 9/14 | 5 | 0 | +66,240 | +46,340 | No |
| XC-FILTER-PDL | 9/14 | 5 | 0 | +66,240 | +46,340 | No |
| XC-RESCAN-ORL | 12/14 | 2 | 0 | +83,380 | +59,605 | No |
| XC-RESCAN-PDL | 10/14 | 4 | 0 | +68,710 | +42,775 | No |

Winner detail that matters: FILTER no-trades 5 winners in
both modes (24 Feb and 12 Aug: Bank Nifty never breaks down
by 11:30 at all; 27 Aug, 7 Sep, 8 Oct ORL: Bank Nifty breaks
after the Nifty signal; PDL: 27 Aug and 8 Oct never break
below PDL, 7 Sep breaks after the signal). RESCAN-ORL recovers
3 of those (27 Aug +₹2,980, 7 Sep +₹2,470, 8 Oct +₹11,690 —
the last larger than its original +₹5,440, because the later
signal has a larger risk and a larger 2× target) but still
loses 24 Feb and 12 Aug entirely, for a net winner loss of
₹7,890 vs baseline. RESCAN-PDL loses 4 winners entirely
(24 Feb, 12 Aug, 27 Aug, 8 Oct). Every XC combined total is
below baseline — cross-confirmation costs more winner value
than it saves in loser avoidance on every version, and
converts 0 Cluster 1 days in the process.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to Clusters 2/3 only if
it reaches 60% on Cluster 1 with positive economics. No variant
did (best day-green 3/8; best Cluster 1 total still negative;
every XC variant 0/8), so no variant is carried into Cluster 2
(reclaim failure, 2 trades, −₹11,420) or Cluster 3 (slow
give-back, 3 trades, −₹10,585) as a fix. For the record: (a)
and (b) are PE-breakdown re-entry rules and would not in any
case apply to Cluster 2's CE reclaim trades without a mirrored
(long-side) definition, which was not tested here; (c) as a
breakdown confirmation would apply to Cluster 3's PE trades
only as a filter/rescan of the same kind that converted 0/8
here, so there is no basis to claim it for Cluster 3 either.

## Variant summary — families (a)–(c) in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| RE-BASE (reference, prior rule) | 2/8 day | −16,345 | +91,270 | +74,925 | No |
| RF-MIN10-SCAN | 3/8 day | −15,730 | +91,270 | +75,540 | No |
| RF-MIN10-DAY | 2/8 day | −17,100 | +91,270 | +74,170 | No |
| RF-BAND-SCAN | 3/8 day | −7,425 | +91,270 | +83,845 | No — best total, still 3/8, still negative |
| RF-BAND-DAY | 2/8 day | −11,410 | +91,270 | +79,860 | No |
| RF-MAXORIG-SCAN | 2/8 day | −12,720 | +91,270 | +78,550 | No |
| RF-MAXORIG-DAY | 2/8 day | −10,655 | +91,270 | +80,615 | No |
| RB-SIGLOW | 0/8 day | −24,895 | +91,270 | +66,375 | No — worse than baseline |
| XC-FILTER-ORL | 0/8 | −19,900 | +66,240 | +46,340 | No — avoidance only |
| XC-FILTER-PDL | 0/8 | −19,900 | +66,240 | +46,340 | No — avoidance only |
| XC-RESCAN-ORL | 0/8 | −23,775 | +83,380 | +59,605 | No |
| XC-RESCAN-PDL | 0/8 | −25,935 | +68,710 | +42,775 | No — worse than baseline |

## What this sweep proves, and what it does not

- Risk-filtering the re-entry moves the ceiling from 2/8 to
  3/8, and only via scanning: the single new conversion is
  19 Aug, where skipping the tiny 10:10 candidate (risk 5.30)
  finds a 10:15 candidate (risk 20.05, target +₹3,970) that
  covers the original loss. That is a real, replayed
  conversion — but it is one day, and the same scanning
  makes 6 Feb worse under MIN10. A risk band is a
  loss-shrink device with one conversion in it, not a
  cluster fix, and its best total (−₹7,425) still loses.
- Signal-low confirmation on the re-entry is worse than
  useless on this cluster: it deletes the 29 Jun working
  re-entry, produces no day-green at all, and ends below
  baseline in total. Do not re-propose signal-low as a
  re-entry condition.
- Bank Nifty confirmation does not separate Cluster 1 losers
  from winners, because the confirmation is already present
  at 09:30 on most losers. The failure is not "Nifty broke
  down alone" — on 5 of 8 days both indices broke down
  together in the first bar, and the Nifty trade still
  stopped out on the bounce back into its own OR. The
  bounce is a Nifty-OR phenomenon, not a
  cross-instrument disagreement phenomenon.
- What remains untested for Cluster 1 after this sweep —
  the next family, NOT a re-run of the above: (d) a
  COMBINED rule — Bank Nifty-confirmed rescan for the
  morning trade PLUS a risk-band-filtered re-entry after
  its stop (the two best single ideas here, combined, which
  this sweep tested only separately); (e) a Bank Nifty-
  confirmed RE-ENTRY (re-entry only if Bank Nifty also
  closes below its OR low on the re-entry bar — a
  confirmation on the second trade, not the first, which
  is a different rule from (c) here); (f) signal-low
  re-entry combined with the risk band (RB-SIGLOW + RF-BAND
  together, so the deeper close must also carry an
  in-band risk — tested separately here, not together);
  (g) a relative-strength version of (c): require Bank
  Nifty's breakdown to be DEEPER than Nifty's (e.g. BN
  close further below its OR low, in scale-adjusted points,
  than Nifty's signal close below its OR low), rather than
  any BN close below OR low counting — the binary BN
  condition tested here is too weak to separate, a
  magnitude condition might not be. Those are the next
  families, not re-runs of close trails, signal-low arming,
  OR-bar/previous-day sizing, intraday trails, bounce
  sizing, timing gates, stop buffers, OR-high stops,
  distance scan-forward, single-close re-entry,
  original-signal quality filters, bounce-bar-close entries,
  re-entry+partial combinations, or the three families in
  this report.

Files: engine `reentry_filter_sweep.py`, raw replay
`reentry_filter_sweep_raw.json`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: families (a)–(c) in
this report are exhausted, and the next decision is which
untried family to run — and none of the variants in this
report is adopted.
