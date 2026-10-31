# NIFTY — Untried combinations (h)–(k) only: triple, recovery-target, RS re-entry, (d)-extended (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): combined-confirmation sweep done
(`nifty_cluster1_combined_confirm_sweep.md`): (d) BN-confirmed
rescan morning + band-filtered re-entry is new ceiling 4/8
day-green, −₹5,660, combined +₹77,720 — still 1 short of 60%
and still negative, and combined is ₹6,125 below RF-BAND-SCAN
alone because BN-rescan costs winners ₹7,890. (e) BN-confirmed
re-entry 2/8, −₹16,245. (f) Signal-low + band 0/8, −₹23,355,
F-DAY ≡ F-SCAN — signal-low dead in three forms, do not
re-propose as hard gate. (g) Relative strength 0/8 both
versions, worst winner-destroyer (G-FILTER winners 3/14,
+₹21,940; G-RESCAN 8/14, +₹32,775, 2 flipped). Nothing adopted,
nothing carried to a whole-month run.

This task, Nifty only, paper only, same pass bar (**60% green
AND total positive AND winners not collapsed**):
(h) triple combination, (i) recovery-target re-entry,
(j) relative-strength re-entry, (k) (d) with re-entry window
extended past 11:30. No family (a)–(g) and no earlier family
is re-run alone here.

Engine: `triple_sweep.py`, raw replay `triple_sweep_raw.json`.
Replayed bar by bar from the Upstox 5-min cache
(`data/progressive/NIFTY/spot_5m.csv` and
`data/progressive/BANKNIFTY/spot_5m.csv`), same signal scan
as all prior sweeps (V4 setup2 PE breakdown: close < OR low,
close < PDL, room ≥ 200×scale, OR width ≤ 360×scale, signal
≤ 11:30; 2026-04-02 Skill, 2026-03-23 Skill winner). Entry =
next bar open, original stop = signal high (PE), original
target = entry − 2×risk unless (i) says otherwise, stop
checked before target on each bar including the entry bar,
square-off 15:10, 100 shares equivalent, ₹40/trade.
Green = net > ₹0. No-trade counted separately from green
throughout. Cluster 1 baseline: 8 trades, 0/8 green,
total −₹24,290. Winners baseline: 14 V5 Nifty PE target
days, 14/14 green, total +₹91,270. Baseline combined PE:
+₹66,980. (d) mornings reproduce exactly in this run
(9 Jan −₹3,745, 6 Feb rescan −₹1,810, 30 Mar −₹2,055,
2 Apr rescan −₹2,065, 13 May −₹5,075, 29 Jun −₹4,740,
8 Jul −₹1,985, 19 Aug −₹2,300).

## Headline — families (h)–(k) all exhausted, nothing passes, nothing adopted

- **No variant passes all three legs.** The pass bar is
  60% green AND Cluster 1 total positive AND winners not
  collapsed. (k) is the first variant in the whole
  long-horizon series to reach the green count alone
  (5/8), but its Cluster 1 total is still **negative
  (−₹4,110)**, so it is NOT a pass, is NOT applied to
  Clusters 2/3, and is NOT carried into a whole-month
  run on its own.
- **Best day-green is now 5/8 (k), best Cluster 1 total
  is still negative in every variant.** (k) −₹4,110 is
  the least-negative Cluster 1 total yet (better than
  (d) −₹5,660 by ₹1,550), but "least negative" is not
  "positive", and it is bought with an afternoon stop
  on 30 Mar that makes that day worse.
- **Winners are NOT collapsed by any variant here**
  (all four: 12/14 green, 2 no-trade, 0 losses,
  +₹83,380 — identical to (d), because no rescan
  winner stops, so every re-entry leg is inert for
  winners, verified not assumed). The failure here is
  purely on Cluster 1 economics, not a winner cost —
  unlike (g), and unlike (d)'s ₹7,890 winner cost
  versus RF-BAND-SCAN, which is already baked into
  the +₹83,380 winner total used for all four
  variants.
- **Combined totals must not be quoted as passes:**
  (k) +₹79,270 is above baseline (+₹66,980) and above
  (d) (+₹77,720), but still below RF-BAND-SCAN alone
  (+₹83,845), and it pairs a negative Cluster 1 total
  with unchanged winners — the same avoidance-total
  error warned about in every prior report.

## Definitions, stated before the results

Morning trade in ALL four variants = (d)'s BN-confirmed
rescan morning (XC-RESCAN-ORL): first V4/Skill breakdown
bar at or after the Bank Nifty break time (first BN bar
≥ 09:30, ≤ 11:30, close < BN OR low), ≤ 11:30; entry,
stop, target as baseline. If BN never breaks by 11:30,
no-trade (0 such days in Cluster 1; 2 winner days,
24 Feb and 12 Aug, are no-trade under the rescan
morning in every variant here).

Re-entry scanning is SCAN-SKIP throughout: a candidate
bar (close < Nifty OR low) failing any condition is
skipped and scanning continues to the window end; the
first candidate passing ALL conditions is the trade.
This matches RF-BAND-SCAN's scan logic, so differences
between variants are the conditions, not the scan.

### (h) Triple: (d) + (e) together

Morning = rescan morning. If it stops, re-entry must
satisfy BOTH: risk in [10, rescan risk] (band, as in
(d)) AND Bank Nifty close on the SAME time label
< BN OR low (BN confirmation, as in (e)). Window
11:30. Day net = morning + re-entry. This is the
combination the prior sweep explicitly left untried
((d) and (e) tested only separately).

### (i) Recovery-target re-entry

Morning = rescan morning. If it stops, re-entry
candidate selection is exactly (d)'s band-filtered
scan (risk in [10, rescan risk], to 11:30), but the
re-entry TARGET is re-sized, not 2× risk:
target distance = (morning loss magnitude + ₹40) / 100
+ 5 points margin, where morning loss magnitude =
|morning net| (which already includes its ₹40 cost).
A target hit therefore gives re-entry net =
morning magnitude + ₹500, and day net = +₹500
exactly, by construction. Stop = re-entry bar high,
unchanged. Square-off net is unchanged in form.

Correction found and fixed during this run, stated
plainly: the shared `replay_pe` helper computes a
target net as 2×risk×100 − ₹40 regardless of the
target distance passed in. Using it for (i) would
have overstated every recovery-target payoff
(9 Jan ₹6,040 instead of ₹4,245, 6 Feb ₹2,930
instead of ₹2,310, 29 Jun ₹6,840 instead of ₹5,240,
19 Aug ₹3,970 instead of ₹2,800) and would have
falsely reproduced (d)'s −₹5,660 total. This run
uses a corrected `replay_pe_actual` for (i) only,
net from the actual exit price. All (i) numbers
below are the corrected ones; the uncorrected
first pass was discarded, not reported as a result.

### (j) Relative-strength re-entry

Morning = rescan morning. If it stops, re-entry
candidate must satisfy BOTH: risk in [10, rescan
risk] AND BN depth_adj > Nifty re-entry depth_adj
on the re-entry bar, where depth_adj =
(OR low − close) / scale, scale = previous close /
55,000 per index separately (same definition as
(g)). BN close is the same time label. Window
11:30. This moves the (g) magnitude condition to
the second trade, where it had not been tested.

### (k) (d) with re-entry window extended past 11:30

Morning = rescan morning. Re-entry = (d)'s
band-filtered scan, but scanning to **15:05**
instead of 11:30. This is ONLY a combination with
(d); RE-EXT alone is not re-run. A re-entry signal
at 15:05 would have no next bar and yields no
trade (no such signal occurs in Cluster 1 here).
Re-entry target stays 2× risk. This directly
addresses (d)'s three no-re-entry days: 30 Mar
(stop at 11:30 itself), 13 May (no close < OR low
after the stop by 11:30), 8 Jul (no in-band
candidate by 11:30).

## Results — (h) Triple, Cluster 1 (baseline 0/8, −₹24,290; (d) 4/8, −₹5,660)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| Cluster 1 (8 days) | 2/8 day | 0 | 6 | −11,985 | No |
| Winners (14 days) | 12/14 | 2 | 0 | +83,380 | — (inert, no rescan winner stops) |
| Combined PE | — | — | — | +71,395 | No — below (d) +₹77,720 |

Day-by-day, (h):

| Date | Rescan morning | Triple re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50, risk 30.40 → target +6,040 | +2,295 GREEN |
| 2026-02-06 | −1,810 | 10:45, risk 10.50 → stop −1,090 | −2,900 |
| 2026-03-30 | −2,055 | none (stop at 11:30, window ends) | −2,055 |
| 2026-04-02 | −2,065 | none (11:25 candidate BN 50,081.15 > BN ORL 50,004.30) | −2,065 |
| 2026-05-13 | −5,075 | none | −5,075 |
| 2026-06-29 | −4,740 | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN |
| 2026-07-08 | −1,985 | none (10:20 candidate risk 27.00 > rescan risk 19.45) | −1,985 |
| 2026-08-19 | −2,300 | none (see below) | −2,300 |

Why (h) is worse than (d) alone, not better: adding
BN confirmation to the band re-entry deletes the
working 19 Aug re-entry (10:15 candidate: BN close
57,145.45 > BN ORL 57,094.50, so it fails BN
confirmation, and every later candidate fails the
band — risks 7.25, 4.85, 7.55, 9.20, 0.95, 5.20,
9.35, 9.20, 6.15, 7.65, 1.10, 2.40, plus three
risk≤0 bars), deletes the 2 Apr re-entry candidate
the same way, and on 6 Feb it skips the working
10:20 re-entry (BN 59,974.55 > BN ORL 59,924.15)
and reaches a later 10:45 trade that stops
(−₹1,090) instead of the 10:20 target (+₹2,930).
Triple filtering is stricter, not smarter: it
keeps only the two largest working re-entries
(9 Jan, 29 Jun) and adds a fresh stop. (h) must
not be quoted as "confirmation improves re-entry"
— (e) already showed BN confirmation on the
second trade does not separate working from
failing re-entries, and (h) confirms it again
under the band.

## Results — (i) Recovery-target re-entry, Cluster 1 (corrected nets)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| Cluster 1 (8 days) | 4/8 day | 0 | 4 | −10,845 | No — same greens as (d), total worse |
| Winners (14 days) | 12/14 | 2 | 0 | +83,380 | — (inert) |
| Combined PE | — | — | — | +72,535 | No — below (d) +₹77,720 |

Day-by-day, (i) (re-entry target distance = recovery
distance; a target hit gives day net +₹500 by
construction):

| Date | Rescan morning | Recovery re-entry (signal / risk / target dist) → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50 / 30.40 / 42.85 → target +4,245 | +500 GREEN |
| 2026-02-06 | −1,810 | 10:20 / 14.85 / 23.50 → target +2,310 | +500 GREEN |
| 2026-03-30 | −2,055 | none | −2,055 |
| 2026-04-02 | −2,065 | 11:25 / 16.25 / 26.05 → stop −1,665 | −3,730 |
| 2026-05-13 | −5,075 | none | −5,075 |
| 2026-06-29 | −4,740 | 11:30 / 34.40 / 52.80 → target +5,240 | +500 GREEN |
| 2026-07-08 | −1,985 | none (10:20 risk 27.00 > 19.45) | −1,985 |
| 2026-08-19 | −2,300 | 10:15 / 20.05 / 28.40 → target +2,800 | +500 GREEN |

Why (i) does not help, despite turning the same
four days green: it converts no NEW day. Candidate
selection is identical to (d), so the days with no
re-entry (30 Mar, 13 May, 8 Jul) stay no-re-entry
and 2 Apr's re-entry still stops (its recovery
target 22,180.45 is not reached before its stop
at 11:30). On the four days it does green, it
CAPS the payoff at exactly +₹500 instead of
(d)'s +₹2,295 / +₹1,120 / +₹2,100 / +₹1,670,
because the recovery distance (42.85, 23.50,
52.80, 28.40) is in every case SMALLER than
(d)'s 2× risk distance (60.80, 29.70, 68.80,
40.10). Total therefore worsens from (d)'s
−₹5,660 to −₹10,845, a ₹5,185 give-back, for
the same 4/8 green count. The task's motivating
examples are answered directly: a re-entry target
that is "too small to turn the day green" is not
the binding problem on (d)'s days — (d)'s
re-entries already cover their mornings, and
sizing the target down to exactly cover the
morning only shrinks the win. Recovery sizing
would only create a new green on a day where a
re-entry reaches the recovery distance but NOT
the 2× distance and then reverses — no such day
occurs in Cluster 1 under (d)'s candidates.
Do not re-propose recovery sizing as a standalone
fix; if it returns, it must be paired with a
candidate rule that finds a NEW re-entry, not
with (d)'s existing candidates.

## Results — (j) Relative-strength re-entry, Cluster 1

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| Cluster 1 (8 days) | 1/8 day | 0 | 7 | −18,025 | No |
| Winners (14 days) | 12/14 | 2 | 0 | +83,380 | — (inert) |
| Combined PE | — | — | — | +65,355 | No — below baseline combined +₹66,980 |

Day-by-day, (j):

| Date | Rescan morning | RS re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | none — every in-band candidate fails RS (10:50 BN 3.04 vs Nifty 15.95; 10:55 10.83 vs 37.21; 11:00 35.81 vs 60.59; 11:10 39.95 vs 85.36; 11:15 68.34 vs 91.64; 11:30 52.63 vs 100.78) | −3,745 |
| 2026-02-06 | −1,810 | 10:45, risk 10.50 → stop −1,090 (10:20 fails RS: BN −46.16 vs Nifty 18.98) | −2,900 |
| 2026-03-30 | −2,055 | none | −2,055 |
| 2026-04-02 | −2,065 | none (11:25 fails RS: BN −82.03 vs Nifty 3.75) | −2,065 |
| 2026-05-13 | −5,075 | none | −5,075 |
| 2026-06-29 | −4,740 | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN |
| 2026-07-08 | −1,985 | none (10:20 risk 27.00 > 19.45) | −1,985 |
| 2026-08-19 | −2,300 | none (10:15 fails RS: BN −48.94 vs Nifty 46.34; all later candidates fail band) | −2,300 |

Why (j) fails hardest on the second trade: on
9 Jan, Bank Nifty's scale-adjusted depth is BELOW
Nifty's on every candidate bar, even though the
10:50 re-entry itself targets successfully under
(d) — the RS condition deletes a working trade
because Nifty's breakdown is DEEPER than BN's in
adjusted points, which is the normal shape of a
Nifty-led move, not a sign of weakness. On
19 Aug BN is above its own OR low at the working
re-entry bar (depth_adj −48.94), so RS fails by
construction whenever BN has not broken that bar.
Moving the (g) magnitude condition to the second
trade does not rescue it: it is 1/8, its only
green is the same 29 Jun trade (d) already had,
and its combined total (+₹65,355) is below the
baseline combined total. RS, in this
scale-adjusted form, is now dead on both trades:
morning (g) 0/8 with collapsed winners, and
re-entry (j) 1/8 with unchanged winners but a
worse Cluster 1 total than (d), (h) and (i).
Do not re-propose a BN-depth threshold — binary
or magnitude, first trade or second — without
first explaining why it would not repeat this.

## Results — (k) (d) with re-entry window extended to 15:05 (best in this sweep, still NOT a pass)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| Cluster 1 (8 days) | 5/8 day | 0 | 3 | −4,110 | No — green bar met, total still negative |
| Winners (14 days) | 12/14 | 2 | 0 | +83,380 | — (inert, no rescan winner stops) |
| Combined PE | — | — | — | +79,270 | No — below RF-BAND-SCAN +₹83,845 |

Day-by-day, (k) (differences from (d) in bold):

| Date | Rescan morning | Extended re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50, risk 30.40 → target +6,040 | +2,295 GREEN |
| 2026-02-06 | −1,810 | 10:20, risk 14.85 → target +2,930 | +1,120 GREEN |
| 2026-03-30 | −2,055 | **13:55, risk 13.50 → stop −1,390** (11:45 candidate risk 20.65 > 20.15, 13:40 39.35, 13:45 22.60, 13:50 31.95 all fail band) | **−3,445 (worse than (d) −2,055)** |
| 2026-04-02 | −2,065 | 11:25, risk 16.25 → stop −1,665 | −3,730 |
| 2026-05-13 | −5,075 | **none — no bar closes < OR low after the 09:55 stop at any time to 15:05** | −5,075 |
| 2026-06-29 | −4,740 | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN |
| 2026-07-08 | −1,985 | **12:05, risk 14.90 → target +2,940** (10:20 risk 27.00 > 19.45 skipped) | **+955 GREEN — the one new conversion over (d)** |
| 2026-08-19 | −2,300 | 10:15, risk 20.05 → target +3,970 | +1,670 GREEN |

Why (k) reaches 5/8 but still fails: extending
the window converts exactly one of (d)'s three
no-re-entry days — 8 Jul, via a 12:05 in-band
candidate that (d)'s 11:30 cutoff missed — taking
the green count from 4/8 to 5/8, the 60% bar.
It does NOT convert 13 May (no afternoon close
below OR low exists at all, so no window length
helps that day) and it makes 30 Mar worse
(−₹2,055 → −₹3,445) by finding an afternoon
candidate that stops. Net effect on the cluster
total is only +₹1,550 versus (d) (−₹5,660 →
−₹4,110): the new +₹955 green plus the
unchanged other greens, minus the extra
−₹1,390 afternoon stop on 30 Mar. A variant
that meets the green count while remaining
₹4,110 negative, with its three remaining
losses totalling −₹12,250 (30 Mar −₹3,445,
2 Apr −₹3,730, 13 May −₹5,075), is not
"consistent green" under the task's definition
— it is five small-to-mid greens outweighed by
three large losses, the same shape as (d) with
one more green. (k) is therefore the new
ceiling to beat (5/8, −₹4,110), not a pass, and
it is NOT applied to Clusters 2/3 and NOT
carried into a whole-month run on its own.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to Clusters
2/3 only if it reaches 60% on Cluster 1 WITH
positive economics. (k) reaches 60% green but its
Cluster 1 total is negative, so the condition is
not met; (h), (i) and (j) fail both legs. No
variant is carried into Cluster 2 (reclaim
failure, 2 trades, −₹11,420) or Cluster 3 (slow
give-back, 3 trades, −₹10,585) as a fix. For the
record: (h)–(k) are PE-breakdown re-entry rules
and would not in any case apply to Cluster 2's
CE reclaim trades without a mirrored (long-side)
definition, which was not tested here.

## Variant summary — families (h)–(k) in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| RF-BAND-SCAN (reference, prior best combined) | 3/8 day | −7,425 | +91,270 | +83,845 | No — prior ceiling on combined |
| (d) Rescan morning + band re-entry (reference, prior ceiling on green) | 4/8 day | −5,660 | +83,380 | +77,720 | No — prior ceiling on green |
| (h) Triple: (d) + BN-confirmed re-entry | 2/8 day | −11,985 | +83,380 | +71,395 | No — worse than (d) on both legs |
| (i) Recovery-target re-entry on (d) candidates (corrected nets) | 4/8 day | −10,845 | +83,380 | +72,535 | No — same greens as (d), caps payoffs to +₹500/day |
| (j) RS re-entry on (d) candidates | 1/8 day | −18,025 | +83,380 | +65,355 | No — below baseline combined |
| (k) (d) + re-entry window to 15:05 | 5/8 day | −4,110 | +83,380 | +79,270 | No — green bar met, total still negative; new ceiling, not a pass |

## What this sweep proves, and what it does not

- The green count can be moved to 5/8, but only by
  an afternoon re-entry (8 Jul 12:05) that the
  11:30 cutoff missed — and that same extension
  adds an afternoon stop (30 Mar 13:55) that
  eats most of the gain. Window extension is a
  real conversion mechanism, not a free one.
- Adding any Bank Nifty condition to the re-entry
  — binary confirmation (h) or magnitude (j) —
  makes the re-entry WORSE than the band alone,
  in both cases deleting working re-entries
  (19 Aug in both, 9 Jan in (j), 6 Feb's working
  10:20 trade in both). BN conditions have now
  failed on the morning trade, on the re-entry
  trade, as a filter, as a rescan, as binary, and
  as magnitude. They are exhausted as a family
  on Cluster 1, not merely untried in one form.
- Recovery sizing (i) proves the arithmetic and
  refutes the premise: sizing a target to exactly
  cover the morning loss guarantees +₹500 if hit,
  but on (d)'s candidates it only shrinks four
  existing wins and creates zero new ones.
- What remains untested for Cluster 1 after this
  sweep — the next family, NOT a re-run of the
  above: (l) (k)'s extended window COMBINED with
  a rule that avoids the 30 Mar afternoon stop
  without losing the 8 Jul afternoon green — e.g.
  an afternoon re-entry that must also satisfy a
  morning-loss or risk condition distinct from the
  band, or an extended window that stops scanning
  after the first afternoon candidate fails the
  band (rather than scanning to 15:05); (m) (k)
  combined with a partial/trail exit on the
  re-entry itself, so an afternoon re-entry that
  moves most of the way to target banks something
  instead of reversing to a full stop; and (n)
  a morning-loss cap: skip the re-entry entirely
  when the morning loss already exceeds a
  threshold (13 May's −₹5,075 and 30 Mar's
  afternoon −₹1,390 are the cases to test, not
  a rule invented from one day). Those are the
  next families, not re-runs of close trails,
  signal-low arming, OR-bar / previous-day sizing,
  intraday trails, bounce sizing, timing gates,
  stop buffers, OR-high stops, distance
  scan-forward, single-close re-entry,
  original-signal quality filters, bounce-bar-close
  entries, re-entry+partial combinations, or the
  families (a)–(k) in this and the prior reports.

Files: engine `triple_sweep.py`, raw replay
`triple_sweep_raw.json`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon
task continues in the parent conversation: families
(h)–(k) in this report are exhausted, and the next
decision is which untried family to run — and none
of the variants in this report is adopted.
