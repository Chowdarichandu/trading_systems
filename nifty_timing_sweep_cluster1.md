# NIFTY Timing Sweep — Cluster 1 (and Clusters 2/3 check)
## Paper only, no orders, no live-trading recommendation

Task: Chandu, 2026-10-29 11:48 IST — timing is the hypothesis, so test
timings X, then Y, then Z, and keep iterating until at least 60% of
failing trades turn green. Do NOT stop at the first variant's failure.
This supersedes the previous stop-at-day-1 rule for this timing work.

Source: `nifty_failing_cases_jan_oct_2026.md`, Cluster 1 = Immediate
OR-breakdown PE bear-trap, 8 trades, −₹24,290, Jan–Aug 2026.
Engine: `timing_sweep.py`, replayed bar by bar from the Upstox 5-min
cache (`data/progressive/NIFTY/spot_5m.csv`), same exit logic as
`daytrader_cash_backtest.run_day`: entry = next bar open after the
signal, stop = signal high (PE), target = entry − 2 × risk, stop
checked before target on each bar including the entry bar,
square-off 15:10. 100 shares equivalent, ₹40/trade.
Baseline gate 09:30 reproduces all 8 Cluster 1 originals exactly
(7 by V4 setup2 conditions, 1 by Skill OR conditions — see below).

## Gate definition — read this before the tables

5-min bars are labelled by their start time. A bar labelled 09:30
covers 09:30–09:35 in real time and closes at 09:35.

- Baseline: signal bar label >= 09:30 (the original rule).
- X: signal bar label >= 09:35 (first breakdown close at/after 09:40
  real time; entry at the 09:40 open).
- Y: signal bar label >= 09:40 (entry at the 09:45 open).
- Z: signal bar label >= 09:45 (entry at the 09:50 open).
- Further gates tested to exhaustion: 09:50, 10:00, 10:30.
- Intermediate timings: a gate of 09:34 is IDENTICAL to gate 09:35
  and a gate of 09:39 is IDENTICAL to gate 09:40, because there is
  no 09:34 or 09:39 5-min bar. There is no finer timing granularity
  in this data than the 5-min bar.
- Second-close variant: after the first qualifying bar >= gate,
  require the NEXT bar to also close below the OR low; entry is the
  open after that second bar, stop = second bar high, target
  recomputed. Tested separately for gates 09:35, 09:40, 09:45.
- A gate does NOT "delay the same trade by 5 minutes" in general.
  The scan takes the FIRST qualifying breakdown bar at/after the
  gate. On several days that is a different, later breakdown, not
  the morning trade with a later entry. Those cases are flagged
  "later signal" in the day tables below.
- "Turn green" means net > ₹0 (a target). "No-trade" means no
  qualifying signal at/after the gate, or an invalid risk
  (entry <= stop, which the original engine returns as no-trade).
  No-trade is counted separately from green throughout — it avoids
  a loss, it does not book a profit.
- 60% target for Cluster 1 = at least 5 of 8 trades turning green.

## Cluster 1 — variant summary (8 trades, original total −₹24,290)

| Variant | Green | No-trade | Still loss | Traded total (₹) | Reaches 60% green? |
|---|---|---|---|---|---|
| Baseline (no gate, 09:30) | 0 / 8 (0%) | 0 | 8 | −24,290 | No |
| X — gate 09:35 | 1 / 8 (12.5%) | 1 | 6 | −8,595 | No |
| Y — gate 09:40 | 2 / 8 (25.0%) | 0 | 6 | +4,610 | No |
| Z — gate 09:45 | 3 / 8 (37.5%) | 0 | 5 | +3,890 | No |
| Gate 09:50 | 3 / 8 (37.5%) | 1 | 4 | +6,725 | No |
| Gate 10:00 | 3 / 8 (37.5%) | 1 | 4 | +3,555 | No |
| Gate 10:30 | 3 / 8 (37.5%) | 2 | 3 | +9,260 | No |
| 09:35 + second close | 0 / 8 (0%) | 4 | 4 | −4,100 | No |
| 09:40 + second close | 1 / 8 (12.5%) | 6 | 1 | −295 | No |
| 09:45 + second close | 2 / 8 (25.0%) | 5 | 1 | +3,910 | No |

**Headline: NO timing variant reaches 60% green.**
Best green rate is 3/8 = 37.5% (gates 09:45, 09:50, 10:00, 10:30),
short of the 5/8 target by 2 trades. All timing variants were
exhausted for this cluster — X, Y, Z, plus 09:50, 10:00, 10:30,
plus second-close at 09:35/09:40/09:45. Timing alone does not fix
Cluster 1 to the target Chandu set.

Note on totals vs conversion: traded total turns positive from
gate 09:40 onward, but that is NOT the same as 60% conversion.
Two large later-signal targets (9 Jan +₹6,040, 29 Jun +₹6,840)
outweigh the remaining small losses. A positive total built on
2 green trades out of 8, with 5–6 trades still losing, is not
"consistent green" and is not counted as reaching the target.

## Cluster 1 — day by day, per variant

Original nets: 9 Jan −₹3,745; 6 Feb −₹2,275; 30 Mar −₹2,055;
2 Apr (Skill) −₹2,115; 13 May −₹5,075; 29 Jun −₹4,740;
8 Jul −₹1,985; 19 Aug −₹2,300. "—" = no-trade.

### X — gate 09:35
| Date | Signal (new) | Result | Net (₹) |
|---|---|---|---|
| 2026-01-09 | 09:35 | stop 09:40 | −1,810 (loss halved, still loss — this is the same trade as the Step 2 second-close replay on this day, because the 09:30 bar was already a breakdown close) |
| 2026-02-06 | 09:35 (unchanged) | stop 09:45 | −2,275 |
| 2026-03-30 | 11:25 (unchanged, already late) | stop 11:30 | −2,055 |
| 2026-04-02 | 09:55 (unchanged, Skill) | stop 10:00 | −2,115 |
| 2026-05-13 | 09:35 | stop 09:50 | −6,425 (WORSE than original — later signal, larger risk 63.85 pts) |
| 2026-06-29 | 11:30 (later signal) | target 12:30 | +6,840 GREEN (later signal, not the morning trade fixed) |
| 2026-07-08 | 09:35 | stop 09:40 | −755 |
| 2026-08-19 | 09:35 | invalid risk (entry 24,080.50 > stop 24,080.05) | — no-trade |

### Y — gate 09:40
| Date | Signal (new) | Result | Net (₹) |
|---|---|---|---|
| 2026-01-09 | 10:50 (later signal) | target 11:35 | +6,040 GREEN (later signal) |
| 2026-02-06 | 09:40 | stop 09:45 | −2,090 |
| 2026-03-30 | 11:25 (unchanged) | stop 11:30 | −2,055 |
| 2026-04-02 | 09:55 (unchanged) | stop 10:00 | −2,115 |
| 2026-05-13 | 09:40 | stop 09:45 | −570 |
| 2026-06-29 | 11:30 (later signal) | target 12:30 | +6,840 GREEN (later signal) |
| 2026-07-08 | 09:40 | stop 09:45 | −840 |
| 2026-08-19 | 09:40 | stop 09:45 | −600 |

### Z — gate 09:45
| Date | Signal (new) | Result | Net (₹) |
|---|---|---|---|
| 2026-01-09 | 10:50 (later signal) | target 11:35 | +6,040 GREEN (later signal) |
| 2026-02-06 | 09:55 | stop 10:00 | −265 |
| 2026-03-30 | 11:25 (unchanged) | stop 11:30 | −2,055 |
| 2026-04-02 | 09:55 (unchanged) | stop 10:00 | −2,115 |
| 2026-05-13 | 09:45 | stop 09:50 | −2,835 |
| 2026-06-29 | 11:30 (later signal) | target 12:30 | +6,840 GREEN (later signal) |
| 2026-07-08 | 10:20 (later signal) | stop 10:30 | −2,740 (worse than original) |
| 2026-08-19 | 10:10 (later signal) | target 10:15 | +1,020 GREEN (later signal, risk only 5.30 pts) |

### Gates 09:50, 10:00, 10:30 — what changes vs Z
- 09:50: same 3 greens as Z (9 Jan, 29 Jun, 19 Aug); 13 May becomes
  no-trade; 6 Feb −₹265, 30 Mar −₹2,055, 2 Apr −₹2,115,
  8 Jul −₹2,740 still lose. Total +₹6,725.
- 10:00: same 3 greens; 13 May no-trade; 2 Apr becomes a new later
  signal 10:05 and still loses (−₹2,950); 6 Feb −₹2,600,
  30 Mar −₹2,055, 8 Jul −₹2,740 still lose. Total +₹3,555.
- 10:30: same 3 greens (19 Aug now +₹1,470 on a 10:30 signal);
  13 May and 8 Jul no-trade; 6 Feb −₹970, 30 Mar −₹2,055,
  2 Apr −₹2,065 still lose. Total +₹9,260 — the highest Cluster 1
  total, still only 3/8 green.

### Second-close combined variants
- 09:35 + second close: 0 green, 4 no-trade (9 Jan, 30 Mar, 2 Apr,
  29 Jun), 4 losses (6 Feb −₹2,090, 13 May −₹570, 8 Jul −₹840,
  19 Aug −₹600). Total −₹4,100.
- 09:40 + second close: 1 green (9 Jan +₹2,540 on a 10:55 later
  signal), 6 no-trade, 1 loss (13 May −₹2,835). Total −₹295.
  This is the best no-trade rate, but it is mostly avoidance,
  not conversion — and it collapses the winning days below.
- 09:45 + second close: 2 green (9 Jan +₹2,540, 19 Aug +₹3,970),
  5 no-trade, 1 loss (6 Feb −₹2,600). Total +₹3,910.
  Non-loss rate 7/8, green rate only 2/8 — do not read this as
  reaching the 60% green target.

### Two days timing can never fix as a morning trade
- 30 Mar: original signal is already 11:25, so every gate up to
  10:30 leaves it unchanged (−₹2,055). Timing is not its problem.
- 2 Apr (Skill): original signal is 09:55, so gates 09:35/09:40/
  09:45 leave it unchanged (−₹2,115). Only a 10:00+ gate changes
  it, to a later signal that still loses (−₹2,950 at 10:00,
  −₹2,065 at 10:30).

## Winning PE days — timing damage (must not be hidden)

Winning set: all 14 V5 Nifty PE target days, Jan–Oct 2026
(original total +₹91,270): 21 Jan +₹9,280; 24 Feb +₹7,350;
16 Mar +₹8,940; 13 Mar +₹5,400; 23 Mar (Skill) +₹7,260;
24 Apr +₹8,820; 5 May +₹5,040; 22 Jul +₹6,320; 12 Aug +₹6,250;
27 Aug +₹3,000; 29 Sep +₹3,790; 7 Sep +₹2,990; 8 Oct +₹5,440;
23 Oct +₹11,390.

| Gate (plain, no second close) | Winners still green | Winners flipped to loss | Winners total (₹) | Combined PE total: Cluster 1 + winners (₹) |
|---|---|---|---|---|
| Baseline 09:30 | 14 / 14 | 0 | +91,270 | +66,980 |
| X 09:35 | 12 / 14 | 2 (24 Feb −₹2,120, 29 Sep −₹4,295) | +64,865 | +56,270 (WORSE than baseline) |
| Y 09:40 | 12 / 14 | 2 (24 Feb −₹1,465, 22 Jul −₹320) | +70,075 | +74,685 (best combined, still only 2/8 Cluster 1 green) |
| Z 09:45 | 10 / 14 | 4 (24 Apr, 22 Jul, 29 Sep, 8 Oct) | +56,900 | +60,790 (worse than baseline) |
| 09:50 | 8 / 14 | 6 | +43,300 | +50,025 |
| 10:00 | 7 / 14 | 7 | +30,690 | +34,245 |
| 10:30 | 8 / 14 | 6 | +11,765 | +21,025 |

Second-close is worse for winners: 09:35 + second close gives
7/14 green, +₹14,870; 09:40 + second close gives 6/14,
+₹7,510; 09:45 + second close gives 5/14, +₹2,870.
So the variant with the best Cluster 1 avoidance
(09:40 + second close, 6 no-trades) destroys most winner
value. It must not be carried forward on Cluster 1 alone.

Best combined-net gate is Y (09:40, plain): Cluster 1
+₹4,610 + winners +₹70,075 = +₹74,685, +₹7,705 above baseline.
That is a net improvement, but it is NOT a 60% conversion
(Cluster 1 green 2/8, winners green 12/14) and it depends on
two later-signal targets. It is a candidate to note, not a
fix to adopt on this sweep alone.

## Clusters 2 and 3 — does the same timing fix them?

Condition in the task was: only apply timing to Clusters 2/3
if a variant reaches 60% on Cluster 1. That condition was NOT
met, so no timing variant is carried into Clusters 2/3 as a fix.
For completeness, the check under the best combined gate Y
(09:40) is:

- Cluster 2 (reclaim failure CE, 2 trades, −₹11,420): timing does
  nothing. Signals are 11:15 (14 Jan) and 09:55 (26 Oct), both
  already at/after 09:40, so both losses are unchanged
  (−₹2,785 and −₹8,635). Timing cannot fix a reclaim failure
  whose signal is not a morning breakdown.
- Cluster 3 (slow PE give-back, 3 trades, −₹10,585): timing does
  not turn any green. At gate 09:40: 13 Feb −₹2,165 (was
  −₹3,750), 30 Apr −₹3,165 (unchanged, signal 10:00),
  18 May −₹3,000 (was −₹3,670). At gate 09:45 the same three
  losses. 0/3 green. This cluster is an exit-rule failure
  (trade moved 48–83% to target, then reversed through the
  signal high), not a morning-timing failure.

## Verdict — timing alone, exhausted

- 60% target: NOT reached by any timing variant. Best green
  rate 3/8 = 37.5%, short by 2 trades.
- Best Cluster 1 total: gate 10:30, +₹9,260, still 3/8 green.
- Best combined PE total: gate Y (09:40, plain), +₹74,685,
  still 2/8 Cluster 1 green and 2 winners flipped to loss.
- Best avoidance: 09:40 + second close, 6/8 no-trade, but
  winners fall to 6/14 and +₹7,510 — rejected as a fix.
- **No timing rule is carried into a whole-month run as a fix
  on this sweep alone.** The next iteration must change
  something other than entry time — e.g. stop placement that
  survives the bounce bar, a re-entry after a stop, or a
  trail/partial exit for Cluster 3 — tested day by day in the
  same way (one day, then the second day, then the month),
  with the 60% green target kept for the month's failing set.
- What timing DID prove: the morning extreme is real for the
  6 morning Cluster 1 signals, but simply waiting until
  09:40/09:45 does not convert them — it mostly replaces
  them with different later signals, and it damages genuine
  early winners (24 Feb, 29 Sep, 22 Jul). The failure is
  entry/stop placement on the morning bar, not the clock
  alone.
