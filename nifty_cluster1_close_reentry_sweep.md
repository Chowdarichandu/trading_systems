# NIFTY — Close-confirmed re-entry (strict variants) + signal-quality filter + bounce-bar-close entry (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): previous family done
(`nifty_cluster1_close_trail_sweep.md`) — close-based trail 0/8 in
every variant, total −₹22,285; close-favourable ceiling proved
(4 of 8 Cluster 1 days never close favourably at all before the
stop, 2 more close at most 0.16–0.22×, only 2 ever close ≥0.5×
favourably); CT-10 preserves winners best (14/14, +₹80,780) but
converts 0/8; pre-signal sizing best S-ORAVG 2/8, −₹23,140,
combined below baseline. Nothing adopted, nothing carried to a
whole-month run.

This task, Nifty only, paper only, same pass bar (60% green AND
total positive AND winners not collapsed):
(i) CLOSE-CONFIRMED RE-ENTRY, (ii) SIGNAL-QUALITY FILTER on the
signal itself, (iii) entering at the BOUNCE BAR'S CLOSE PRICE
(not its next open). For each variant replay all 8 Cluster 1 days
+ 14 winners bar by bar, report green / no-trade / still loss,
cluster total, winner total, combined total. If a variant passes
on Cluster 1 with positive economics, apply to Clusters 2/3. If
none passes, report best variant and next family — task continues
in parent conversation, do NOT present exhaustion as completion.

Engine: `close_reentry_sweep.py`, raw replay
`close_reentry_sweep_raw.json`. Replayed bar by bar from the Upstox
5-min cache (`data/progressive/NIFTY/spot_5m.csv`), same signal
scan as all prior sweeps (V4 setup2 PE breakdown: close < OR low,
close < PDL, room ≥ 200×scale, OR width ≤ 360×scale, signal
≤ 11:30; 2026-04-02 Skill, 2026-03-23 Skill winner). Entry = next
bar open unless a variant says otherwise, original stop = signal
high (PE), original target = entry − 2×risk, stop checked before
target on each bar including the entry bar, square-off 15:10,
100 shares equivalent, ₹40/trade. Green = net > ₹0. No-trade
counted separately from green throughout. Cluster 1 baseline:
8 trades, 0/8 green, total −₹24,290. Winners baseline: 14 V5
Nifty PE target days, 14/14 green, total +₹91,270. Baseline
combined PE: +₹66,980.

## Headline — families (i)–(iii) all exhausted, nothing passes, nothing adopted

- **Best day-green in the whole sweep is 2/8 (25%), not 5/8.**
  That is RE-BASE and RE-PDL (identical trades, see below) and
  RE-EXT, all at 2/8 day green. Every other variant is 0–1/8.
  No variant reaches the 60% green bar, so **no variant is
  applied to Clusters 2/3 and nothing is carried into a
  whole-month run on its own.**
- **Family (ii) cannot pass by construction, and the run proves
  it:** a filter on the original signal can only turn a losing
  day into a no-trade, never into a green trade (the kept trades
  are replayed unchanged). Every SQ variant is therefore 0/8
  green on Cluster 1, whatever its total. Totals that "improve"
  under SQ are avoidance totals, not conversion totals, and
  they are bought with winner totals collapsing (SQ-D30: Cluster 1
  total ₹0 on 8/8 no-trade, but winners fall to 4/14, +₹36,500).
  Do not quote any SQ total as a pass.
- **Family (iii) is 0/8 in both versions.** Entering at the
  bounce bar's close does not avoid the bounce — the NEXT bar
  still runs through the stop. BC-A total −₹23,885 is barely
  better than baseline, and only because smaller losses elsewhere
  almost offset one ballooned loss (13 May −₹11,155). BC-B
  total −₹11,290 looks better, but it is loss-shrink from
  tiny risks (19 Aug risk 0.50 pts → −₹90), and it destroys
  winners (5/14, −₹185 total). Neither is a fix.
- **Best variant by the pass bar is none.** By day-green it is
  RE-BASE / RE-PDL (2/8, −₹16,345); by Cluster 1 total among
  variants that trade every day it is also RE-BASE / RE-PDL;
  by loss-shrink alone it is BC-B (−₹11,290), which fails on
  winners. None satisfies all three legs of the pass bar.

## Honesty correction — family (i) as assigned is NOT new

The task describes (i) as "distinct from the intraday re-entry
already tested". On checking the prior engine, that description
is wrong about the prior rule: `stop_sweep.py::replay_reentry`
already defines re-entry as **the first bar after the stop bar
whose CLOSE is back below OR low** — i.e. it is already a
close-confirmed re-entry, not an intraday-touch re-entry.
Re-running that exact rule here as "new" would have been a
duplicate claim, so this sweep does the honest thing instead:

- RE-BASE reproduces the prior rule **only as a reference**,
  and its new variants are genuinely distinct from it:
  RE-2C (two consecutive closes below OR low), RE-PDL (close
  below OR low AND below PDL AND full V4 room, not just OR low),
  RE-EXT (same single close, window extended from 11:30 to
  15:05).
- **Reproduction discrepancy, flagged not hidden:** RE-BASE here
  gives day combined total **−₹16,345**, while the prior
  stop-sweep report quoted −₹17,355 — a ₹1,010 difference.
  Day-green count (2/8), re-entry-alone green count (3/6) and
  every individual day net in this replay agree with the prior
  report's day nets (9 Jan +₹2,295, 29 Jun +₹2,100, 19 Aug
  −₹1,280, 6 Feb −₹2,540, 2 Apr −₹5,065, 8 Jul −₹4,725,
  30 Mar −₹2,055, 13 May −₹5,075 — these sum to −₹16,345, not
  −₹17,355). The prior report's total, not its day nets, appears
  to be ₹1,010 out. Either way the verdict is unchanged: 2/8,
  not a pass. The prior total should be corrected in the
  record, not quoted further.

## Definitions, stated before the results

### (i) Re-entry variants — Trade 1 is always the baseline trade

- **RE-BASE (reference only, NOT new):** if Trade 1 stops, ONE
  re-entry: first bar after the stop bar whose close < OR low,
  signal ≤ 11:30; entry = next bar open, stop = that bar's high,
  target = entry − 2×risk, ₹40 cost again. Day net = Trade 1 net
  + re-entry net. No re-entry ⇒ day = Trade 1 net.
- **RE-2C:** same, but the re-entry signal must be the SECOND
  of two CONSECUTIVE closes below OR low after the stop
  (a single close below OR low, followed by a close back above
  it, does not qualify; the pair must complete by 11:30).
- **RE-PDL:** same single close as RE-BASE, but the re-entry
  bar must ALSO close below PDL and satisfy full V4 room
  (close to next PD level below ≥ 200×scale); Skill day 2 Apr
  uses Skill conditions (close < OR low, < PDL, no room cap),
  as in the original trade.
- **RE-EXT:** same single close as RE-BASE, but the window is
  extended to a 15:05 signal bar (entry on the next bar, which
  must exist before square-off).
- Winners under every RE variant: unchanged (14/14, +₹91,270) —
  a winner never stops, so no re-entry triggers. Combined PE
  total for RE variants is therefore Cluster 1 day total +
  ₹91,270, stated not hidden.

### (ii) Signal-quality filter — ORIGINAL signal only, no rescan

This is the point that makes (ii) different from the distance
family in the stop sweep. There, the scan CONTINUED to the first
later bar meeting the distance (so later signals appeared and
were counted as greens). Here, the original signal is taken as
given: if it fails the filter, the day is a **no-trade** and no
later signal is sought. Kept trades are replayed exactly as
baseline. Filter variants (trade only if…):

- **SQ-D5 / D10 / D20 / D30:** signal close at least 5 / 10 /
  20 / 30 points below OR low.
- **SQ-WLE80 / WLE100 / WLE120:** OR width ≤ 80 / 100 / 120
  points. **SQ-WGT100:** OR width > 100 points (the opposite
  side, as a sensitivity).
- **SQ-BODY33:** signal close in the bottom third of the signal
  bar ((close − low) / (high − low) ≤ 0.33).
- **SQ-COMB:** distance ≥ 10 points AND OR width ≤ 120 points
  (one combined variant, run regardless of the singles' results).

### (iii) Bounce-bar-close entry

Bounce bar B = the bar immediately after the signal bar (the
original entry bar). Its intraday high is NOT counted as a stop,
because the trade is not entered until B closes — that is the
whole point of the variant, and it is different from the
delayed-open entries already tested (entry at the open AFTER B,
stop = B's high or the signal high).

- **BC-A:** entry = close of B, **only if that close < OR low**
  (otherwise the breakdown is already invalidated and the day
  is a no-trade); stop = original signal high; target =
  entry − 2×(stop − entry); replay from the bar after B.
- **BC-B:** same entry and same no-trade condition, but stop =
  high of B; target recomputed from that (much smaller) risk;
  replay from the bar after B.
- If entry ≥ stop, the trade is invalid / no-trade (counted
  separately, net None). Winners are replayed under the same
  BC rule on their own original signals.

## Original-signal diagnostics — why (ii) had no chance

| Date | Signal | Dist below OR low (pts) | OR width (pts) | Signal range (pts) | Close position* |
|---|---|---|---|---|---|
| 2026-01-09 | 09:30 | 2.00 | 101.45 | 52.30 | 0.313 |
| 2026-02-06 | 09:35 | 9.25 | 77.25 | 31.60 | 0.320 |
| 2026-03-30 | 11:25 | 1.95 | 147.90 | 22.45 | 0.107 |
| 2026-04-02 (Skill) | 09:55 | 2.65 | 185.50 | 22.00 | 0.043 |
| 2026-05-13 | 09:30 | 24.50 | 141.35 | 51.95 | 0.043 |
| 2026-06-29 | 09:30 | 15.25 | 78.40 | 48.90 | 0.006 |
| 2026-07-08 | 09:30 | 9.85 | 65.35 | 25.60 | 0.186 |
| 2026-08-19 | 09:30 | 19.20 | 79.80 | 27.25 | 0.077 |

\* Close position = (close − low) / (high − low); 0 = close at the
low, 1 = close at the high.

Reading: Cluster 1 signals are NOT uniformly shallow, narrow or
weak-bodied. Distance spans 1.95–24.50 points, width 65–186
points, close position 0.006–0.320 (every loser closes in the
bottom third of its bar). Winners overlap the same ranges
(e.g. winner distances 1.35–176.65 points, widths 71.50–217.15
points, one winner at close position 0.339). No threshold on
any one of these three quantities separates losers from winners
— which is exactly what the SQ results below show: every
threshold that removes losers removes more winners.

## Results — (i) Re-entry, Cluster 1 (8 days, baseline 0/8, −₹24,290)

| Variant | Re-entry alone green | Day green | No re-entry | Day total (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| Baseline | — | 0/8 | — | −24,290 | +66,980 | — |
| RE-BASE (reference, prior rule) | 3/6 traded | 2/8 | 2 | −16,345 | +74,925 | No |
| RE-2C (two consecutive closes) | 2/4 traded | 1/8 | 4 | −24,095 | +67,175 | No |
| RE-PDL (close < ORL + < PDL + room) | 3/6 traded | 2/8 | 2 | −16,345 | +74,925 | No — identical to RE-BASE |
| RE-EXT (window to 15:05) | 3/7 traded | 2/8 | 1 | −18,450 | +72,820 | No |

Day-by-day, RE-BASE / RE-PDL (identical on every day):

| Date | Trade 1 | Re-entry signal → result | Re-entry net (₹) | Day net (₹) |
|---|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50 → target 11:35 | +6,040 | +2,295 GREEN |
| 2026-02-06 | −2,275 | 09:55 → stop 10:00 (risk only 2.25 pts) | −265 | −2,540 |
| 2026-03-30 | −2,055 | none (never closes back below OR low by 11:30) | — | −2,055 |
| 2026-04-02 | −2,115 | 10:05 → stop 10:10 | −2,950 | −5,065 |
| 2026-05-13 | −5,075 | none | — | −5,075 |
| 2026-06-29 | −4,740 | 11:30 → target 12:30 | +6,840 | +2,100 GREEN |
| 2026-07-08 | −1,985 | 10:20 → stop 10:30 | −2,740 | −4,725 |
| 2026-08-19 | −2,300 | 10:10 → target 10:15 (risk only 5.30 pts) | +1,020 | −1,280 (re-entry green, day still loss) |

Why RE-PDL is identical to RE-BASE: on all 6 days that get a
re-entry, the first close below OR low after the stop is ALSO
below PDL and also satisfies V4 room — the extra conditions
bind nowhere. Adding PDL/room to the re-entry rule is therefore
not a stricter rule on this data, it is the same rule restated.
Do not re-propose it as a new variant.

Why RE-2C is worse: requiring a second consecutive close
below OR low loses the 29 Jun re-entry entirely (no qualifying
pair by 11:30 — the day falls back to −₹4,740), turns the
9 Jan re-entry into a smaller target (+₹2,540 on an 10:55
signal instead of +₹6,040, so the day stays a loss at −₹1,205),
and makes the 2 Apr and 6 Feb re-entries worse (−₹3,715 and
−₹2,600). Only 19 Aug improves (+₹3,970, day +₹1,670, the
sole RE-2C day green). Stricter confirmation on the re-entry
does not convert more days — it mostly delays or removes the
re-entries that did work.

Why RE-EXT is worse than RE-BASE despite one more trade:
extending the window adds exactly one re-entry, on 30 Mar
(11:45 signal → stop 11:55, −₹2,105), which turns that day
from −₹2,055 into −₹4,160. 13 May still gets no re-entry
even with the extended window. A later window adds a losing
second trade, not a converting one.

## Results — (ii) Signal-quality filter, original signal only

Cluster 1: **0/8 green in every SQ variant** — as constructed
above, a filter cannot green a kept trade. Read the totals as
avoidance totals only, and always with the winner column.

| Variant | Cluster 1 green | Cluster 1 no-trade | Cluster 1 total (₹) | Winners green | Winners no-trade | Winners total (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | −24,290 | 14/14 | 0 | +91,270 | +66,980 | — |
| SQ-D5 (dist ≥ 5) | 0/8 | 3 | −16,375 | 10/14 | 4 | +76,050 | +59,675 | No |
| SQ-D10 (dist ≥ 10) | 0/8 | 5 | −12,115 | 8/14 | 6 | +63,750 | +51,635 | No |
| SQ-D20 (dist ≥ 20) | 0/8 | 7 | −5,075 | 6/14 | 8 | +52,100 | +47,025 | No |
| SQ-D30 (dist ≥ 30) | 0/8 | 8 | 0 | 4/14 | 10 | +36,500 | +36,500 | No — 8/8 avoidance, winners collapsed |
| SQ-WLE80 (width ≤ 80) | 0/8 | 4 | −11,300 | 2/14 | 12 | +8,390 | −2,910 | No — worst winner damage |
| SQ-WLE100 (width ≤ 100) | 0/8 | 4 | −11,300 | 6/14 | 8 | +36,380 | +25,080 | No |
| SQ-WLE120 (width ≤ 120) | 0/8 | 3 | −15,045 | 7/14 | 7 | +42,700 | +27,655 | No |
| SQ-WGT100 (width > 100) | 0/8 | 4 | −12,990 | 8/14 | 6 | +54,890 | +41,900 | No |
| SQ-BODY33 (close in bottom third) | 0/8 | 0 | −24,290 | 13/14 | 1 | +88,270 | +63,980 | No — filter binds nowhere on losers |
| SQ-COMB (dist ≥ 10 AND width ≤ 120) | 0/8 | 6 | −7,040 | 5/14 | 9 | +36,710 | +29,670 | No |

What each filter actually does on Cluster 1:

- **Distance:** SQ-D5 removes the three shallowest losers
  (9 Jan dist 2.00, 30 Mar 1.95, 2 Apr 2.65) and keeps the other
  five losses (−₹16,375). SQ-D20 keeps only 13 May (−₹5,075,
  dist 24.50) and removes everything else. SQ-D30 removes all
  eight — the "₹0 total" is eight days of not trading, not
  eight days of winning, and it costs 10 of 14 winners.
  Every combined total under a distance filter is BELOW
  baseline (+₹66,980), and the gap widens as the threshold
  rises. Distance is a volume knob on participation, not a
  quality separator.
- **OR width:** SQ-WLE80 keeps only the four narrow-OR losers
  (6 Feb, 29 Jun, 8 Jul, 19 Aug — all still losses, −₹11,300)
  and keeps only 2 of 14 winners (+₹8,390); combined
  −₹2,910 is the only negative combined total in the SQ
  family. SQ-WGT100 (the opposite side) keeps the four
  wide-OR losers (−₹12,990) and 8 winners (+₹54,890) — still
  below baseline combined. Neither side of the width band
  holds the winners while shedding the losers, because
  winners span widths 71.50–217.15 points.
- **Body:** SQ-BODY33 keeps all 8 losers (every Cluster 1 signal
  already closes in the bottom third of its bar, close
  positions 0.006–0.320) and 13 of 14 winners (only 27 Aug,
  close position 0.339, is filtered out, costing +₹3,000).
  A filter that binds on nothing on the losing side is not a
  quality filter at all — signal-bar body position does not
  distinguish these losers from these winners, and should not
  be re-proposed.
- **Combined:** SQ-COMB keeps only 29 Jun (−₹4,740) and
  19 Aug (−₹2,300) on Cluster 1 (−₹7,040) and only 5 winners
  (+₹36,710). Combining two non-separating filters does not
  create a separating one; it just compounds the winner loss.

## Results — (iii) Bounce-bar-close entry

| Variant | Cluster 1 green | Cluster 1 no-trade | Cluster 1 total (₹) | Winners green | Winners total (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | −24,290 | 14/14 | +91,270 | +66,980 | — |
| BC-A (entry = bounce close, stop = signal high) | 0/8 | 3 | −23,885 | 11/14 | +50,510 | +26,625 | No |
| BC-B (entry = bounce close, stop = bounce high) | 0/8 | 3 | −11,290 | 5/14 | −185 | −11,475 | No — winners destroyed |

### BC-A day-by-day, Cluster 1

Bounce bar = bar after the signal bar. No-trade = bounce bar's
close is already back above OR low (breakdown invalidated on
the very next bar) — 30 Mar, 2 Apr, 29 Jun.

| Date | Bounce bar | Entry (bounce close) | Stop (signal high) | Risk (pts) | Net (₹) | Exit |
|---|---|---|---|---|---|---|
| 2026-01-09 | 09:35 | 25,830.10 | 25,873.10 | 43.00 | −4,340 | stop 09:40 |
| 2026-02-06 | 09:40 | 25,526.30 | 25,565.80 | 39.50 | −3,990 | stop 09:45 |
| 2026-03-30 | — | — | — | — | no-trade | bounce close above OR low |
| 2026-04-02 | — | — | — | — | no-trade | bounce close above OR low |
| 2026-05-13 | 09:35 | 23,276.50 | 23,387.65 | 111.15 | −11,155 | stop 09:55 |
| 2026-06-29 | — | — | — | — | no-trade | bounce close above OR low |
| 2026-07-08 | 09:35 | 24,217.15 | 24,240.90 | 23.75 | −2,415 | stop 09:45 |
| 2026-08-19 | 09:35 | 24,079.55 | 24,099.00 | 19.45 | −1,985 | stop 09:50 |

Why BC-A fails: entering at the bounce close moves entry
further from the signal high on the days the bounce bar falls
(13 May: entry 23,276.50 vs original 23,337.30, so risk balloons
from 50.35 to 111.15 points and the loss more than doubles to
−₹11,155). Waiting for the bounce bar to close does not mean
the bounce is over — the next bar still runs through the
original signal high on all 5 traded days. Winners under BC-A:
11/14, +₹50,510 (55.3% of baseline) — 3 flips to loss
(16 Mar −₹7,605, 29 Sep −₹6,120, 23 Oct −₹7,920), because the
wider risk (entry further from the signal high) also widens
the target to 2× that risk, out of reach on those days.

### BC-B day-by-day, Cluster 1

Same entries and no-trades as BC-A; only the stop changes
(stop = bounce bar's high, target recomputed).

| Date | Entry | Stop (bounce high) | Risk (pts) | Net (₹) | Exit |
|---|---|---|---|---|---|
| 2026-01-09 | 25,830.10 | 25,848.60 | 18.50 | −1,890 | stop 09:40 |
| 2026-02-06 | 25,526.30 | 25,547.70 | 21.40 | −2,180 | stop 09:45 |
| 2026-05-13 | 23,276.50 | 23,339.35 | 62.85 | −6,325 | stop 09:50 |
| 2026-07-08 | 24,217.15 | 24,224.80 | 7.65 | −805 | stop 09:40 |
| 2026-08-19 | 24,079.55 | 24,080.05 | 0.50 | −90 | stop 09:40 |

Why BC-B's total (−₹11,290) must not be read as progress:
it is loss-shrink from tiny risks, not conversion — 0/8 green,
and the smallest risks are degenerate (19 Aug: a 0.50-point
stop, −₹90, is not a trade, it is a rounding-level stop that
any next-bar wobble hits). And it destroys winners: 5/14,
**−₹185 total** (9 flips to loss, including 23 Oct −₹2,840,
13 Mar −₹3,695, 16 Mar −₹4,140, 29 Sep −₹4,255). A bounce-bar
high as a stop is far too tight for genuine breakdown days,
which routinely retrace above the bounce bar's high before
continuing down. Combined −₹11,475 is far below baseline.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to Clusters 2/3 only if
it reaches 60% on Cluster 1 with positive economics. No variant
did (best day-green 2/8, every SQ variant 0/8 by construction,
every BC variant 0/8), so no variant is carried into Cluster 2
(reclaim failure, 2 trades, −₹11,420) or Cluster 3 (slow
give-back, 3 trades, −₹10,585) as a fix. For the record, the
RE variants are PE-breakdown rules and would not in any case
apply to Cluster 2's CE reclaim trades without a mirrored
(long-side) definition, which was not tested here; and the SQ
filters, being original-signal filters, would apply to
Clusters 2/3 only as no-trade filters, not as conversions —
they cannot green a kept Cluster 2/3 trade either.

## Variant summary — families (i)–(iii) in this task, pass bar applied

| Family / variant | Green (conversion test) | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| RE-BASE (reference, prior rule) | 2/8 day | −16,345 | +91,270 | +74,925 | No |
| RE-2C two consecutive closes | 1/8 day | −24,095 | +91,270 | +67,175 | No |
| RE-PDL close < ORL + < PDL + room | 2/8 day | −16,345 | +91,270 | +74,925 | No — identical to RE-BASE |
| RE-EXT window to 15:05 | 2/8 day | −18,450 | +91,270 | +72,820 | No |
| SQ-D5 / D10 / D20 / D30 | 0/8 each | −16,375 / −12,115 / −5,075 / 0 | +76,050 / +63,750 / +52,100 / +36,500 | +59,675 / +51,635 / +47,025 / +36,500 | No — avoidance only |
| SQ-WLE80 / WLE100 / WLE120 | 0/8 each | −11,300 / −11,300 / −15,045 | +8,390 / +36,380 / +42,700 | −2,910 / +25,080 / +27,655 | No |
| SQ-WGT100 | 0/8 | −12,990 | +54,890 | +41,900 | No |
| SQ-BODY33 | 0/8 | −24,290 | +88,270 | +63,980 | No — binds nowhere on losers |
| SQ-COMB | 0/8 | −7,040 | +36,710 | +29,670 | No |
| BC-A bounce close, stop = signal high | 0/8 | −23,885 | +50,510 | +26,625 | No |
| BC-B bounce close, stop = bounce high | 0/8 | −11,290 | −185 | −11,475 | No — winners destroyed |

## What this sweep proves, and what it does not

- The prior re-entry rule was already close-confirmed. The
  only new re-entry information here is negative: making it
  stricter (two closes, PDL+room, longer window) does not
  improve it — RE-2C is worse, RE-PDL is identical, RE-EXT
  adds a losing trade. The re-entry ceiling on Cluster 1
  remains 2/8 day green, from the same two later signals
  (9 Jan 10:50, 29 Jun 11:30) that the timing gates already
  found. Re-entry does not fix the morning trade; it adds a
  second, later trade that works on 2 of 8 days.
- Signal quality on the signal bar itself does not separate
  losers from winners on any of the three quantities tested
  (distance below OR low, OR width, signal-bar body position).
  A filter can only avoid, and every threshold that avoids a
  meaningful number of losers avoids more winner value than
  it saves. Any future "quality filter" claim must show a
  quantity that separates the two sets — none of these three
  does — and must count no-trades separately from greens,
  or it will falsely pass by avoidance alone (SQ-D30's ₹0
  Cluster 1 total is the warning example: 8/8 no-trade, 0/8
  green, winners 4/14).
- Bounce-bar-close entry does not solve the bounce problem.
  It changes the entry price and, in BC-B, shrinks the risk
  to degenerate levels, but the bar after the bounce bar
  still stops all 5 traded Cluster 1 days, and BC-B's tight
  stop flips 9 of 14 winners to losses. The bounce is not a
  one-bar event that ends at the bounce bar's close; it runs
  for 1–5 bars, and no entry price inside that window, with
  a stop at either the signal high or the bounce high,
  survives it on these days.
- What remains untested for Cluster 1 after this sweep — the
  next family, NOT a re-run of the above: (a) a re-entry
  filtered by its OWN risk (e.g. skip re-entries whose risk
  is tiny — 6 Feb 2.25 pts, 19 Aug 5.30 pts — or whose risk
  exceeds the original, rather than taking every close below
  OR low); (b) a re-entry that requires a close below the
  SIGNAL bar's low, not just below OR low (a deeper
  confirmation than ORL, distinct from RE-PDL, which turned
  out identical because PDL was already below ORL on these
  days — signal-low is a different, tighter level); (c) a
  cross-instrument confirmation for the morning trade itself
  (e.g. require Bank Nifty to also break down the same
  morning before taking the Nifty PE breakdown) — a
  confirmation from outside the Nifty candle, not another
  threshold on the same candle. Those are the next families,
  not re-runs of close trails, signal-low arming, OR-bar or
  previous-day sizing, intraday trails, bounce sizing, timing
  gates, stop buffers, OR-high stops, distance scan-forward,
  single-close re-entry, original-signal quality filters, or
  bounce-bar-close entries, and not another re-entry+partial
  combination.

Files: engine `close_reentry_sweep.py`, raw replay
`close_reentry_sweep_raw.json`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: families (i)–(iii) in
this task are exhausted, and the next decision is which
untried family to run — and none of the variants in this
report is adopted.
