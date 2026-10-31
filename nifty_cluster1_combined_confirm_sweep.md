# NIFTY — Untried combinations: BN-confirmed rescan + band re-entry, BN-confirmed re-entry, signal-low + band, relative strength (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): re-entry-filter sweep done
(`nifty_cluster1_reentry_filter_sweep.md`) — best RF-BAND-SCAN 3/8
day-green, −₹7,425, combined +₹83,845 — still negative, still
short of 60%, must not be quoted as a pass. Signal-low re-entry
0/8, −₹24,895, worse than baseline — deletes working cases, do
not re-propose. Bank Nifty cross-confirmation 0/8 in every
version — BN already breaks at 09:30 on 5 of 8 losing days, so
binary confirmation keeps losses unchanged; FILTER is avoidance
only, RESCAN only changes 6 Feb / 2 Apr and still loses.
Nothing adopted, nothing carried to a whole-month run.

This task, Nifty only, paper only, same pass bar (**60% green
AND total positive AND winners not collapsed**):
(d) combined rule — Bank Nifty-confirmed rescan for the morning
trade PLUS risk-band-filtered re-entry after its stop (the two
best single ideas, tested only separately before);
(e) Bank Nifty-confirmed RE-ENTRY (re-entry only if Bank Nifty
also closes below its OR low on the re-entry bar — confirmation
on the second trade, not the first);
(f) signal-low re-entry COMBINED with the risk band (deeper close
must also carry an in-band risk);
(g) relative-strength — require Bank Nifty's breakdown to be
DEEPER than Nifty's in scale-adjusted points, rather than any
BN close below OR low counting.
For each variant all 8 Cluster 1 days + 14 winners are replayed
bar by bar, green / no-trade / still loss, cluster total,
winner total, combined total, with no-trade counted separately
from green. If a variant passes on Cluster 1 with positive
economics, apply to Clusters 2/3. If none passes, report best
variant and next family — task continues in parent
conversation, do NOT present exhaustion as completion. No
family from the prior report is re-run alone here, and no
earlier exhausted family is re-run alone.

Engine: `combined_confirm_sweep.py`, raw replay
`combined_confirm_sweep_raw.json`. Replayed bar by bar from the
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
Baseline reproduction in this run: all 8 Cluster 1 originals
replay exactly (−₹3,745, −₹2,275, −₹2,055, −₹2,115, −₹5,075,
−₹4,740, −₹1,985, −₹2,300).

## Headline — families (d)–(g) all exhausted, nothing passes, nothing adopted

- **Best day-green in the whole sweep is 4/8 (50%), not 5/8.**
  That is (d) alone. Every other variant is 0–2/8. No variant
  reaches the 60% green bar, so **no variant is applied to
  Clusters 2/3 and nothing is carried into a whole-month run
  on its own.**
- **Best Cluster 1 total is still negative:** (d) −₹5,660
  (combined +₹77,720, because winners under the BN-rescan
  morning fall to +₹83,380). A combined total above baseline
  with a still-negative Cluster 1 total and only 4/8 day-green
  is NOT a pass — it is loss-shrink plus mostly-unchanged
  winners, not conversion of the failing cluster.
- **(d) is a real improvement, and still a failure by the
  pass bar.** Combining the two best single ideas adds exactly
  one new day-green over RF-BAND-SCAN (6 Feb, +₹1,120, via a
  rescan morning trade that then re-enters in-band), moving
  3/8 → 4/8 and −₹7,425 → −₹5,660. It is one day-green short
  of 60% and ₹5,660 short of a positive cluster total. It
  also gives back ₹6,125 of combined value versus
  RF-BAND-SCAN alone (+₹77,720 vs +₹83,845), because the
  BN-rescan morning costs winners ₹7,890 (₹91,270 → ₹83,380)
  while gaining only ₹1,765 on Cluster 1. Quoting (d)'s
  combined total without the 4/8 and the negative cluster
  total would repeat the avoidance-total error.
- **(e) is 2/8, (f) is 0/8, (g) is 0/8 in both versions.**
  BN confirmation on the re-entry (e) deletes the working
  19 Aug re-entry and adds a fresh stop on 6 Feb. Signal-low
  + band (f) is identical in its DAY and SCAN forms (see
  below) and produces no day-green at all. Relative strength
  (g) is the worst winner-destroyer in the whole long-horizon
  series so far: FILTER keeps only 3/14 winners (+₹21,940),
  RESCAN keeps 8/14 (+₹32,775) and flips two winners to
  losses — the magnitude condition is stricter than the
  binary one, not a finer separator.

## Definitions, stated before the results

### (d) BN-confirmed rescan morning + band-filtered re-entry

- Morning trade = XC-RESCAN-ORL from the prior sweep: first
  V4/Skill breakdown bar at or after the Bank Nifty break
  time (first BN bar ≥ 09:30, ≤ 11:30, close < BN OR low),
  ≤ 11:30; entry, stop, target as baseline. If BN never
  breaks by 11:30, no-trade (0 such days in Cluster 1).
- If that morning trade stops, re-entry = RF-BAND-SCAN from
  the prior sweep, with the band measured against the
  RESCAN trade's own risk (not the baseline trade's risk):
  first bar after the stop (scanning to 11:30) whose close
  < OR low and whose re-entry risk lies in [10, rescan
  risk]; entry next open, stop that bar high, target
  2× risk, ₹40 again. Day net = morning + re-entry.
- Winners are replayed under the same rule generally: a
  rescan morning that stopped would also get a band
  re-entry. In fact no rescan winner stops (12/14 green,
  2 no-trade, 0 losses), so the re-entry leg is inert
  for winners here — verified, not assumed.

### (e) BN-confirmed re-entry

- Morning trade = baseline original trade, unchanged.
- If it stops, re-entry candidate = first bar after the
  stop (scanning to 11:30) whose Nifty close < OR low
  AND whose Bank Nifty close on the SAME time label
  < BN OR low. Entry next open, stop that bar high,
  target 2× risk, ₹40 again. No risk-band filter is
  applied here — that would be (d)+(e) combined, which
  is a next family, not this variant. Day net =
  morning + re-entry.
- Winners under (e): unchanged (14/14, +₹91,270) — a
  winner never stops, so no re-entry triggers. Verified
  explicitly in the run: zero winner days stop under
  the baseline.

### (f) Signal-low re-entry + risk band

- Morning trade = baseline original trade, unchanged.
- If it stops, a re-entry candidate must satisfy BOTH:
  close < ORIGINAL signal bar's low (signal lows from
  the prior sweep: 9 Jan 25,820.80, 6 Feb 25,534.20,
  30 Mar 22,465.80, 2 Apr 22,205.55, 13 May 23,335.70,
  29 Jun 24,016.80, 8 Jul 24,215.30, 19 Aug 24,071.75)
  AND re-entry risk in [10, original risk].
- F-DAY: the FIRST siglow candidate is tested against
  the band; if it fails, no re-entry that day.
- F-SCAN: a failing siglow candidate is skipped and
  scanning continues for the next siglow candidate
  that passes the band (to 11:30).
- Winners under (f): unchanged (14/14, +₹91,270),
  same reason as (e).

### (g) Relative strength — scale-adjusted depth

- depth_adj = (OR low − close) / scale, where scale =
  previous close / 55,000 for each index separately
  (the engine's scale, as in `timing_sweep.day_data`).
  For Nifty scale ≈ 0.41–0.47, for Bank Nifty
  scale ≈ 0.91–1.11, so a BN depth_adj above a Nifty
  depth_adj means the BN raw depth is roughly 2× the
  Nifty raw depth. Note: depth_adj ordering is identical
  to percentage-depth ordering (depth_adj = 55,000 ×
  depth / prev close), so re-proposing "percentage
  depth" as a different rule would not change any
  result here.
- G-FILTER: original Nifty trade is kept ONLY if, by
  the Nifty signal time, some BN bar (≥ 09:30) closed
  < BN OR low with depth_adj greater than the Nifty
  signal's depth_adj; otherwise no-trade. Like every
  filter, this can only avoid, never green — its 0/8
  is by construction, and its totals are avoidance
  totals, always read with the winner column.
- G-RESCAN: Nifty breakdown candidates are scanned in
  order; the first candidate for which BN (bars up to
  that candidate's time) has a close < BN OR low with
  depth_adj greater than that candidate's depth_adj
  is the trade; entry, stop, target as baseline. If
  no candidate qualifies by 11:30, no-trade. This is
  the only (g) version that could green via a later
  signal.

## Results — (d) Combined rescan + band re-entry (best in this sweep, still NOT a pass)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| Cluster 1 (8 days) | 4/8 day | 0 | 4 | −5,660 | No — 1 short of 5/8, total still negative |
| Winners (14 days) | 12/14 | 2 | 0 | +83,380 | — (same as XC-RESCAN-ORL alone) |
| Combined PE | — | — | — | +77,720 | No — below RF-BAND-SCAN's +₹83,845 |

Day-by-day, (d) Cluster 1 (morning = rescan trade; re-entry = band-filtered):

| Date | Rescan morning (signal / net) | Band re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | 09:30 / −3,745 (unchanged) | 10:50, risk 30.40 → target +6,040 | +2,295 GREEN |
| 2026-02-06 | 10:10 / −1,810 (rescan, BN break 10:10) | 10:20, risk 14.85 → target +2,930 | +1,120 GREEN — the one new conversion over RF-BAND-SCAN |
| 2026-03-30 | 11:25 / −2,055 (unchanged) | none (stop at 11:30, window ends) | −2,055 |
| 2026-04-02 | 10:45 / −2,065 (rescan, BN break 10:45) | 11:25, risk 16.25 → stop −1,665 | −3,730 (worse than baseline −2,115) |
| 2026-05-13 | 09:30 / −5,075 (unchanged) | none (no close < OR low after stop by 11:30) | −5,075 |
| 2026-06-29 | 09:30 / −4,740 (unchanged) | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN |
| 2026-07-08 | 09:30 / −1,985 (unchanged) | none (first candidate risk 27.00 > rescan risk 19.45, no later in-band candidate by 11:30) | −1,985 |
| 2026-08-19 | 09:30 / −2,300 (unchanged) | 10:15, risk 20.05 → target +3,970 | +1,670 GREEN |

Why (d) gains exactly one day: on 6 Feb the rescan morning
is a smaller trade (risk 17.70, loss −₹1,810) than the
baseline morning (risk 22.35, loss −₹2,275), and its
10:20 re-entry (risk 14.85, inside [10, 17.70]) targets
for +₹2,930, which covers the smaller morning loss.
Under RF-BAND-SCAN alone, 6 Feb's day was −₹195
(re-entry +₹2,080 against the larger morning loss) —
so the combination turns a near-miss into a green day,
not by finding a new re-entry, but by shrinking the
morning loss the re-entry has to cover. Every other
day replays exactly as RF-BAND-SCAN (9 Jan, 29 Jun,
19 Aug green; 30 Mar, 13 May, 8 Jul no re-entry) except
2 Apr, where the rescan morning plus a band re-entry
stop makes the day worse (−₹3,730 vs baseline
−₹2,115 and vs RF-BAND-SCAN −₹4,180 — better than
RF-BAND-SCAN alone on that day, worse than doing
nothing after the rescan morning).

Winners under (d): 12/14 green, 2 no-trade (24 Feb,
12 Aug — BN never breaks by 11:30), 0 losses, +₹83,380.
Detail that matters: 27 Aug +₹2,980 (vs +₹3,000
original), 7 Sep +₹2,470 (vs +₹2,990), 8 Oct +₹11,690
(vs +₹5,440, larger because the later rescan signal
carries a larger risk and a larger 2× target); all
other kept winners replay at their original nets.
So (d)'s combined +₹77,720 = Cluster 1 (−₹5,660) +
winners (+₹83,380), which is ₹6,125 BELOW RF-BAND-SCAN's
combined (+₹83,845 = −₹7,425 + ₹91,270): the BN-rescan
morning buys ₹1,765 of Cluster 1 improvement at a
₹7,890 winner cost. A combination that improves the
failing cluster while making the combined leg worse
than the best single rule is not a step forward to
adopt — it is the new ceiling (4/8) to beat, with its
cost stated.

## Results — (e) BN-confirmed re-entry, Cluster 1 (baseline 0/8, −₹24,290)

| Variant | Re-entry alone green | Day green | No re-entry | Day total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| (e) BN-confirmed re-entry | 2/4 traded | 2/8 | 4 | −16,245 | +75,025 | No |

Day-by-day, (e):

| Date | Re-entry signal → result | Day net |
|---|---|---|
| 2026-01-09 | 10:50, risk 30.40 → target +6,040 | +2,295 GREEN (same as RE-BASE) |
| 2026-02-06 | 10:10, risk 17.70 → stop −1,810 | −4,085 (worse than baseline −2,275; earlier Nifty candidates failed the BN condition, scanning reached 10:10) |
| 2026-03-30 | none | −2,055 |
| 2026-04-02 | 10:45, risk 20.25 → stop −2,065 | −4,180 (same trade as the XC rescan trade) |
| 2026-05-13 | none | −5,075 |
| 2026-06-29 | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN (same as RE-BASE) |
| 2026-07-08 | none | −1,985 |
| 2026-08-19 | 10:35, risk 9.20 → stop −960 | −3,260 (the working 10:15 re-entry, target +3,970 under RE-BASE, is deleted: BN was not below its OR low at 10:15, so scanning reaches a later, smaller trade that stops) |

Why (e) fails: BN confirmation on the re-entry bar does
not separate working re-entries from failing ones — it
keeps the two large working re-entries (9 Jan, 29 Jun),
deletes the working 19 Aug re-entry, and adds a fresh
stop on 6 Feb. It ends at the same 2/8 day-green as
RE-BASE, with a day total (−₹16,245) barely better
than RE-BASE (−₹16,345) and well below RF-BAND-SCAN
(−₹7,425). Confirmation on the second trade is not a
better rule than confirmation on the first trade —
both are 0–2/8 ideas on this cluster, and (e) must not
be quoted as "BN confirmation works on re-entries"
on the strength of its two greens, which are the same
two greens RE-BASE already had.

## Results — (f) Signal-low + risk band, Cluster 1 (baseline 0/8, −₹24,290)

| Variant | Re-entry alone green | Day green | No re-entry | Day total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| F-DAY | 1/2 traded | 0/8 | 6 | −23,355 | +67,915 | No |
| F-SCAN | 1/2 traded | 0/8 | 6 | −23,355 | +67,915 | No — identical to F-DAY (see below) |

Day-by-day, (f) (both forms identical):

| Date | First siglow candidate → band test → result | Day net |
|---|---|---|
| 2026-01-09 | 11:00, risk 11.05, in [10, 37.05] → stop −1,145 | −4,890 (worse than baseline) |
| 2026-02-06 | 10:05, risk 10.60, in [10, 22.35] → target +2,080 | −195 (re-entry green, day still loss) |
| 2026-03-30 | none (never closes below signal low by 11:30) | −2,055 |
| 2026-04-02 | 10:05, risk 29.10, NOT in [10, 20.75] → no re-entry | −2,115 (better than RB-SIGLOW's −5,065, still a loss) |
| 2026-05-13 | none | −5,075 |
| 2026-06-29 | none — the 11:30 RE-BASE re-entry closes below OR low but above signal low, so it never qualifies | −4,740 (the working re-entry is lost, as under RB-SIGLOW alone) |
| 2026-07-08 | none | −1,985 |
| 2026-08-19 | 10:20, risk 7.25, NOT in [10, 22.60] → no re-entry | −2,300 (better than RB-SIGLOW's −890? No — worse in day terms: RB-SIGLOW's small target at least cut the day to −890; the band blocks it and hands the day back to −2,300) |

Why F-DAY and F-SCAN are identical: on the two days
where the first siglow candidate fails the band
(2 Apr, 19 Aug), no LATER siglow candidate passes
the band by 11:30 either, so scanning finds nothing
new. The band's only effect over RB-SIGLOW alone is
to delete two re-entries (2 Apr's stop, 19 Aug's small
target), moving the total from −₹24,895 to −₹23,355
— a ₹1,540 improvement that is still below baseline
in green count (0/8) and still a negative cluster
total. Combining two failing filters does not make
a passing rule: signal-low deletes the 29 Jun working
re-entry in every form, and the band cannot restore
it. Do not re-propose signal-low in any combination
that keeps the signal-low condition as a hard gate.

## Results — (g) Relative strength, Cluster 1 + winners

### Cluster 1 (8 days, baseline 0/8, −₹24,290)

| Variant | Green | No-trade | Still loss | Cluster 1 total (₹) | Pass? |
|---|---|---|---|---|---|
| G-FILTER | 0/8 | 2 | 6 | −19,900 | No — avoidance only, by construction |
| G-RESCAN | 0/8 | 0 | 8 | −22,535 | No |

Day-by-day, (g) Cluster 1 (depth_adj = (OR low − close) / scale;
BN max = largest BN depth_adj at or before the Nifty signal):

| Date | Nifty signal depth_adj | BN max depth_adj by signal | FILTER kept? | RESCAN signal / net |
|---|---|---|---|---|
| 2026-01-09 | 4.25 | 14.79 | yes | 09:30 / −3,745 (unchanged) |
| 2026-02-06 | 19.84 | none (BN never below OR low by 09:35) | no | 10:30 / −970 (later signal, smaller risk 9.30; still a loss) |
| 2026-03-30 | 4.70 | 93.16 | yes | 11:25 / −2,055 (unchanged) |
| 2026-04-02 | 6.42 | none (BN never below OR low by 09:55) | no | 11:25 / −1,665 (later signal, risk 16.25; still a loss, BN depth_adj 4.11 barely above Nifty's 3.75) |
| 2026-05-13 | 57.51 | 123.87 | yes | 09:30 / −5,075 (unchanged) |
| 2026-06-29 | 34.87 | 91.68 | yes | 09:30 / −4,740 (unchanged) |
| 2026-07-08 | 22.24 | 53.03 | yes | 09:30 / −1,985 (unchanged) |
| 2026-08-19 | 43.72 | 55.90 | yes | 09:30 / −2,300 (unchanged) |

Why (g) cannot work as a filter: FILTER's two no-trades
are exactly the same two days XC-FILTER removed (6 Feb,
2 Apr — BN breaks later than Nifty), so its Cluster 1
total (−₹19,900) is identical to XC-FILTER's, and its
0/8 is by construction. Why (g) cannot work as a
rescan: on the six days where BN depth already exceeds
Nifty depth at the original signal, the rescan trade
IS the original trade; on the other two days it finds
a later signal that still loses (−₹970, −₹1,665),
improving the total by only ₹1,755 over baseline.
A magnitude condition that is already satisfied on
6/8 losers at their original signals cannot separate
losers from winners — it is the binary condition with
a stricter threshold, and the strictness falls
almost entirely on winners (see below).

### Winners under (g) (14 days, baseline 14/14, +₹91,270)

| Variant | Green | No-trade | Still loss | Winners total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| G-FILTER | 3/14 | 11 | 0 | +21,940 | +2,040 | No — winners collapsed |
| G-RESCAN | 8/14 | 4 | 2 | +32,775 | +10,240 | No — winners collapsed and 2 flipped |

Winner detail that matters: FILTER keeps only 21 Jan
(+₹9,280), 13 Mar (+₹5,400) and 23 Mar (+₹7,260) — every
other winner fails the depth condition at its signal
time, including near-misses that show the threshold
is not a separator but a cliff: 24 Apr BN 88.00 vs
Nifty 88.68 (fails by 0.68), 23 Oct BN 414.31 vs Nifty
428.24 (fails by 13.93 on a very deep signal).
RESCAN recovers some (24 Apr +₹4,990 on a 09:35 signal,
22 Jul +₹3,620, 29 Sep +₹2,710, 7 Sep +₹940,
23 Oct +₹2,140) but still loses 4 winners entirely
(24 Feb, 12 Aug, 27 Aug, 8 Oct) and FLIPS two winners
to losses (16 Mar −₹2,960 on a 10:30 signal, 5 May
−₹605 on a 10:55 signal). Every (g) combined total is
far below baseline (+₹66,980): FILTER +₹2,040,
RESCAN +₹10,240. Relative strength, in this
scale-adjusted form, is the most winner-destructive
family tested in the long-horizon series. Do not
re-propose a BN-depth threshold — binary or
magnitude — without first explaining why it would
not repeat this winner collapse.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to Clusters 2/3 only if
it reaches 60% on Cluster 1 with positive economics. No variant
did (best day-green 4/8; best Cluster 1 total still negative;
every (g) variant 0/8 with collapsed winners), so no variant is
carried into Cluster 2 (reclaim failure, 2 trades, −₹11,420)
or Cluster 3 (slow give-back, 3 trades, −₹10,585) as a fix.
For the record: (d), (e) and (f) are PE-breakdown re-entry
rules and would not in any case apply to Cluster 2's CE
reclaim trades without a mirrored (long-side) definition,
which was not tested here; (g) as a breakdown condition
would apply to Cluster 3's PE trades only as a filter/rescan
of the kind that converted 0/8 here, so there is no basis
to claim it for Cluster 3 either.

## Variant summary — families (d)–(g) in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| RE-BASE (reference, prior rule) | 2/8 day | −16,345 | +91,270 | +74,925 | No |
| RF-BAND-SCAN (reference, prior best) | 3/8 day | −7,425 | +91,270 | +83,845 | No — prior ceiling |
| (d) Rescan morning + band re-entry | 4/8 day | −5,660 | +83,380 | +77,720 | No — new ceiling, still 1 short and still negative |
| (e) BN-confirmed re-entry | 2/8 day | −16,245 | +91,270 | +75,025 | No |
| (f) F-DAY signal-low + band | 0/8 day | −23,355 | +91,270 | +67,915 | No |
| (f) F-SCAN signal-low + band | 0/8 day | −23,355 | +91,270 | +67,915 | No — identical to F-DAY |
| (g) G-FILTER relative strength | 0/8 | −19,900 | +21,940 | +2,040 | No — avoidance only, winners collapsed |
| (g) G-RESCAN relative strength | 0/8 | −22,535 | +32,775 | +10,240 | No — winners collapsed, 2 flipped |

## What this sweep proves, and what it does not

- Combining the two best single ideas DOES move the ceiling,
  from 3/8 to 4/8, and the mechanism is identified: it
  shrinks the morning loss on 6 Feb so the existing band
  re-entry can cover it. That is a real, replayed
  conversion — but it is one day, it still leaves the
  cluster negative, and it costs more winner value than
  it gains on Cluster 1. The combination is the new
  ceiling to beat, not a pass.
- BN confirmation, wherever it is placed — on the morning
  trade (c, 0/8), on the re-entry (e, 2/8, same greens as
  RE-BASE), or as a magnitude threshold (g, 0/8 with
  collapsed winners) — does not separate Cluster 1 losers
  from winners on this data. The failure is not "Nifty
  broke down alone" and it is not "Nifty broke down
  shallowly while BN broke deeply" — on most losing days
  both indices broke together, deeply, in the first bar.
- Signal-low is now dead in three forms: alone (0/8,
  −₹24,895), and combined with the band in both DAY and
  SCAN forms (0/8, −₹23,355). It deletes the 29 Jun
  working re-entry every time. Do not re-propose it.
- What remains untested for Cluster 1 after this sweep —
  the next family, NOT a re-run of the above: (h) a TRIPLE
  combination — (d)'s BN-confirmed rescan morning PLUS a
  BN-confirmed, band-filtered re-entry after its stop
  ((d)+(e) together, which this sweep tested only
  separately); (i) a RECOVERY-TARGET re-entry — the
  re-entry's target is sized to cover the morning loss
  (target distance = morning loss + cost, plus a profit
  margin) instead of the fixed 2× re-entry risk, which
  directly addresses days where a re-entry target exists
  but is too small to turn the day green (6 Feb under
  (f): +₹2,080 against −₹2,275; 19 Aug under RB-SIGLOW:
  +₹1,410 against −₹2,300); (j) a RELATIVE-STRENGTH
  RE-ENTRY — the re-entry bar must satisfy BN depth_adj
  > Nifty re-entry depth_adj, i.e. the (g) magnitude
  condition moved to the second trade, where it has not
  been tested at all; and (k) (d) with the re-entry
  window extended past 11:30, which directly addresses
  (d)'s three no-re-entry days (30 Mar: stop at 11:30
  itself; 13 May: no close < OR low after the stop by
  11:30; 8 Jul: no in-band candidate by 11:30) — but
  only as a combination with (d), not as a re-run of
  RE-EXT alone. Those are the next families, not
  re-runs of close trails, signal-low arming, OR-bar/
  previous-day sizing, intraday trails, bounce sizing,
  timing gates, stop buffers, OR-high stops, distance
  scan-forward, single-close re-entry, original-signal
  quality filters, bounce-bar-close entries,
  re-entry+partial combinations, or the families
  (a)–(g) in this and the prior report.

Files: engine `combined_confirm_sweep.py`, raw replay
`combined_confirm_sweep_raw.json`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: families (d)–(g) in
this report are exhausted, and the next decision is which
untried family to run — and none of the variants in this
report is adopted.
