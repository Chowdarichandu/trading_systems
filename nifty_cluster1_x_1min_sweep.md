# Family (x) — 1-min replay of (lA): Nifty only, paper only

**Verdict first: family (x) is EXHAUSTED. It does not pass, and nothing
from it is adopted.** The 1-min replay flips one of the three still-loss
days (13 May) to green, but it fails every other leg of the pass bar:
only 1/3 of the failing set turns green (2/3 needed), the Cluster 1
total stays negative, and the winners collapse. The 5-min entry-bar
stops on 30 Mar and 2 Apr are REAL, not aggregation artefacts — the
stop is still touched inside the same 5-min window at 1-min resolution.
The next family is direction-flip as a separate system, not a PE fix
(see "Next family" at the end).

## Baseline reproduction (required before claiming any 1-min difference)

The 5-min (lA) engine (`extended_window_sweep.day_variant`, variant
`lA`) was re-run in this script and reproduces the given (lA) nets
**exactly, day by day**:

- Cluster 1 (8 days): 5/8 green, total **−₹2,720**
  (9 Jan +2,295; 6 Feb +1,120; 30 Mar −2,055; 2 Apr −3,730;
  13 May −5,075; 29 Jun +2,100; 8 Jul +955; 19 Aug +1,670).
- PE winners (14 days): 12/14 green, 2 no-trade (24 Feb, 12 Aug),
  total **+₹83,380**.
- Combined (lA): **+₹80,660**. All three totals match the task context.

Note: the reproduced (lA) winner day nets differ from the *original*
morning nets on three days because (lA) uses the BN-confirmed rescan
signal, not the original signal (27 Aug ₹2,980 vs ₹3,000 original;
7 Sep ₹2,470 vs ₹2,990; 8 Oct ₹11,690 vs ₹5,440). The comparison table
below uses the reproduced (lA) nets as the baseline, so the comparison
is like-for-like.

## 1-min data

- Source: Upstox only, via
  `~/workspace/custom-connectors/custom.upstox/bin/upstox.py candles`
  (`--unit minutes --interval 1`), one request per instrument-day.
  No second source was sought.
- Coverage: all 22 days × Nifty (`NSE_INDEX|Nifty 50`) and Bank Nifty
  (`NSE_INDEX|Nifty Bank`), **375 bars each (09:15–15:29), no day missing**.
  Files: `~/workspace/trading/data/1min/NIFTY/spot_1m_<date>.csv` and
  `.../BANKNIFTY/...`; fetch script `fetch_1min_x.py`.
- Consistency check: aggregating the 1-min bars into 5-min bars
  reproduces the 5-min cache bars exactly on the checked entry bars
  (30 Mar 11:30: open 22,468.10 / high 22,506.30 / low 22,457.35 /
  close 22,503.80; 2 Apr 10:50: 22,204.85 / 22,237.45 / 22,199.25 /
  22,226.60; 23 Mar 09:55: 22,628.55 / 22,634.35 / 22,592.60 /
  22,597.50 — all identical to `spot_5m.csv`). The 1-min feed is the
  same feed at finer resolution, not a different feed.

## How (lA) was adapted to 1-min bars (explicit)

- Bar label = start minute. A 1-min bar labelled HH:MM covers
  HH:MM–HH:MM+1 (a 5-min bar labelled HH:MM covered HH:MM–HH:MM+5).
- Opening range = 1-min bars labelled < 09:30 (09:15–09:29, 15 bars);
  OR low = min 1-min low, OR high = max 1-min high. On all 8 Cluster 1
  days the 1-min OR low equals the 5-min OR low exactly, so OR
  redefinition does **not** drive the differences below.
- BN break time = first 1-min BN bar labelled ≥ 09:30 and ≤ 11:30 whose
  close < BN 1-min OR low. It can therefore fall inside the 5-min bar
  the 5-min engine labelled as the break (e.g. 9 Jan: 09:32 at 1-min vs
  09:30 at 5-min — here later, not earlier, because the 5-min 09:30 bar
  closed below BN OR low on its 5-min close while its first 1-min
  closes did not; 30 Mar: 10:53 at 1-min vs 10:50 at 5-min).
- Nifty rescan = first 1-min bar labelled ≥ BN break label and ≤ 11:30
  whose close < Nifty 1-min OR low AND < PDL. V4 mode additionally
  requires OR width ≤ 360×scale and room ≥ 200×scale (room = close
  minus highest PD level below close, or infinity if none). Skill mode
  (2 Apr, 23 Mar) skips the room/width filter. Identical conditions to
  5-min `rescan_trade`; only the bar grid changes.
- Entry = next 1-min bar open; stop = signal-bar (1-min) high;
  target = entry − 2×risk; square-off at the 15:10 1-min bar close;
  100 shares; ₹40/trade. Stop checked before target on every bar
  including the entry bar — the same within-bar convention as 5-min
  (within a single 1-min bar, ordering is still unobserved).
- Re-entry (only after a morning stop): scan 1-min bars after the stop
  bar; candidate = close < Nifty 1-min OR low; window labels ≤ 15:05.
  Morning phase (label ≤ 11:30): skip band-failing candidates.
  Afternoon phase (label > 11:30): the FIRST band-failing candidate
  ENDS the scan (lA stop-on-first-fail). Band = risk in
  [10, rescan risk]. Entry next 1-min open, stop candidate-bar high,
  target 2×risk, ₹40 again.
- PD levels (PDH/PDC/PDL) and scale are taken from the existing 5-min
  daily cache, exactly as the 5-min engine uses them, so only the bar
  grid changes, not the levels.

## Task 1 — Diagnostic: do the 5-min entry-bar stops survive at 1-min?

**Yes for the stop itself; no for the "MFE 0" shorthand.** In all three
5-min entry-bar stops, price moved favourably first at 1-min resolution
before the stop was touched — but by only 2.80–10.75 points, nowhere
near the 2×risk targets (32.50–40.50 points), and under (lA) rules
(no partial, no trail on morning or re-entry trades) that small
excursion changes nothing. The stop is still touched inside the same
5-min window in every case.

### 30 Mar, morning trade — 5-min entry bar 11:30, entry 22,468.10, stop 22,488.25 (risk 20.15)

| Minute | Open | High | Low | Close |
|---|---|---|---|---|
| 11:30 | 22,468.10 | 22,469.10 | 22,457.35 | 22,467.50 |
| 11:31 | 22,467.25 | **22,488.40** | 22,466.55 | 22,488.40 |
| 11:32 | 22,487.20 | 22,493.80 | 22,487.20 | 22,490.15 |
| 11:33 | 22,489.40 | 22,491.00 | 22,480.65 | 22,485.25 |
| 11:34 | 22,484.35 | 22,506.30 | 22,484.35 | 22,503.80 |

First stop-touch minute: **11:31**. Max favourable excursion BEFORE
that minute: **10.75 points** (11:30 low 22,457.35). Price moved
favourably first: yes. Target was 22,427.80 — never approached.

### 2 Apr, morning trade (Skill mode) — 5-min entry bar 10:50, entry 22,204.85, stop 22,225.10 (risk 20.25)

| Minute | Open | High | Low | Close |
|---|---|---|---|---|
| 10:50 | 22,204.85 | 22,206.55 | 22,199.25 | 22,203.00 |
| 10:51 | 22,202.50 | 22,205.15 | 22,201.60 | 22,202.40 |
| 10:52 | 22,201.65 | 22,205.65 | 22,200.15 | 22,200.70 |
| 10:53 | 22,200.55 | **22,229.55** | 22,200.55 | 22,229.55 |
| 10:54 | 22,230.10 | 22,237.45 | 22,223.30 | 22,226.60 |

First stop-touch minute: **10:53** — a near-vertical spike minute
(open 22,200.55, close 22,229.55). Max favourable excursion BEFORE
that minute: **5.60 points** (10:50 low 22,199.25). Price moved
favourably first: yes, trivially. Target was 22,164.35.

### 2 Apr, re-entry trade — 5-min entry bar 11:30, entry 22,206.50, stop 22,222.75 (risk 16.25)

| Minute | Open | High | Low | Close |
|---|---|---|---|---|
| 11:30 | 22,206.50 | 22,210.80 | 22,203.70 | 22,209.50 |
| 11:31 | 22,208.80 | 22,216.20 | 22,206.55 | 22,214.45 |
| 11:32 | 22,213.65 | 22,222.70 | 22,209.40 | 22,220.05 |
| 11:33 | 22,219.90 | **22,224.10** | 22,215.30 | 22,215.30 |
| 11:34 | 22,214.75 | 22,219.80 | 22,210.75 | 22,219.80 |

First stop-touch minute: **11:33** (note 11:32 high 22,222.70 missed the
stop by 0.05). Max favourable excursion BEFORE that minute:
**2.80 points** (11:30 low 22,203.70). Price moved favourably first:
yes, trivially. Target was 22,174.00.

### Winner contrast — 23 Mar, morning trade (Skill mode), 5-min entry bar 09:55, entry 22,628.55, stop 22,665.05 (risk 36.50)

| Minute | Open | High | Low | Close |
|---|---|---|---|---|
| 09:55 | 22,628.55 | 22,629.25 | 22,621.60 | 22,625.85 |
| 09:56 | 22,625.55 | 22,634.35 | 22,609.50 | 22,612.85 |
| 09:57 | 22,611.60 | 22,613.45 | 22,599.30 | 22,603.15 |
| 09:58 | 22,603.75 | 22,629.50 | 22,603.75 | 22,620.00 |
| 09:59 | 22,618.50 | 22,619.40 | 22,592.60 | 22,597.50 |

Stop **never touched** in the entry bar. Favourable excursion inside
the entry bar: **35.95 points** (low 22,592.60) — an order of magnitude
larger than the 2.80–10.75 points on the losing days, and the trade
went on to its 5-min target at 10:15. The contrast is clean: losers
drift a few points favourably then spike through the stop; the winner
falls immediately and keeps falling.

**Diagnostic verdict: 5-min entry-bar stops are REAL, not artefacts.**
What does not survive is the literal "MFE 0" shorthand — at 1-min
resolution there was small favourable movement first on all three
losing entry bars. That correction changes no outcome under (lA)
rules, because (lA) has no partial or trail that could have banked
2.80–10.75 points, and none of the excursions came close to target.

## Task 2 — Full 1-min replay vs 5-min (lA), day by day

### Cluster 1 (8 days)

| Date | 5-min (lA) | 1-min replay | 1-min morning (signal / entry / stop / risk / exit) | 1-min re-entry |
|---|---|---|---|---|
| 2026-01-09 | +₹2,295 | **−₹3,680** | 09:33 / 25,822.40 / 25,847.70 / 25.30 / stop 09:36 | 09:37 / stop / −₹1,110 (risk 10.70) |
| 2026-02-06 | +₹1,120 | **+₹1,850** | 10:10 / 25,524.05 / 25,533.50 / 9.45 / target 10:12 | — |
| 2026-03-30 | −₹2,055 | **−₹3,120** | 11:11 / 22,458.75 / 22,473.95 / 15.20 / stop 11:13 | 11:15 / stop / −₹1,560 (risk 15.20) |
| 2026-04-02 (Skill) | −₹3,730 | **−₹1,730** | 10:47 / 22,197.70 / 22,214.60 / 16.90 / stop 10:53 | none (morning-phase candidates fail band: 11:28 risk 6.50, 11:29 risk 1.35) |
| 2026-05-13 | −₹5,075 | **+₹4,590** | 09:34 / 23,337.30 / 23,360.45 / 23.15 / target 09:37 | — |
| 2026-06-29 | +₹2,100 | **−₹1,815** | 09:34 / 24,018.70 / 24,036.45 / 17.75 / stop 09:38 | none (afternoon first-fail 11:33, risk 19.30 > band cap 17.75, scan ends) |
| 2026-07-08 | +₹955 | **−₹2,570** | 09:30 / 24,226.90 / 24,240.90 / 14.00 / stop 09:46 | 10:24 / stop / −₹1,130 (risk 10.90) |
| 2026-08-19 | +₹1,670 | **+₹1,600** | 09:30 / 24,090.80 / 24,099.00 / 8.20 / target 09:34 | — |
| **Cluster 1 total** | **−₹2,720** | **−₹4,875** | **3/8 green (was 5/8), 0 no-trade** | |

### PE winners (14 days)

| Date | 5-min (lA) | 1-min replay | 1-min morning outcome |
|---|---|---|---|
| 2026-01-21 | +₹9,280 | +₹1,920 | target (risk 9.80, vs 46.60 at 5-min) |
| 2026-02-24 | no-trade | no-trade | no rescan signal at 1-min either |
| 2026-03-16 | +₹8,940 | +₹2,220 | target (risk 11.30, vs 44.90) |
| 2026-03-13 | +₹5,400 | +₹2,590 | target (risk 13.15, vs 27.20) |
| 2026-03-23 (Skill) | +₹7,260 | +₹2,000 | target (risk 10.20, vs 36.50) |
| 2026-04-24 | +₹8,820 | **−₹630** | stop 09:31 (risk 5.90); no re-entry (all later candidates fail the [10, 5.90] band, which is empty above 10 by construction — band cap below the 10 floor) |
| 2026-05-05 | +₹5,040 | +₹990 | morning stop −₹1,710, re-entry target +₹2,700 |
| 2026-07-22 | +₹6,320 | +₹3,740 | target (risk 18.90, vs 31.80) |
| 2026-08-12 | no-trade | no-trade | no rescan signal at 1-min either |
| 2026-08-27 | +₹2,980 | +₹445 | morning stop −₹1,645, re-entry target +₹2,090 |
| 2026-09-29 | +₹3,790 | +₹2,760 | target (risk 14.00, vs 19.15) |
| 2026-09-07 | +₹2,470 | +₹1,150 | target (risk 5.95, vs 12.55) |
| 2026-10-08 | +₹11,690 | **−₹1,595** | stop 11:32 (risk 15.55); afternoon first-fail 11:33 ends scan |
| 2026-10-23 | +₹11,390 | +₹3,180 | target (risk 16.10, vs 57.15) |
| **Winners total** | **+₹83,380** | **+₹18,770** | **10/14 green (was 12/14), 2 no-trade, 2 losses** |

### Combined

| | 5-min (lA) | 1-min replay |
|---|---|---|
| Cluster 1 | −₹2,720 | −₹4,875 |
| Winners | +₹83,380 | +₹18,770 |
| **Combined** | **+₹80,660** | **+₹13,895** |

### Why the 1-min totals collapse (mechanism, not mystery)

At 1-min resolution the signal-bar high is a 1-min high, not a 5-min
high, so risks roughly halve (e.g. 23 Mar 36.50 → 10.20; 21 Jan
46.60 → 9.80; 23 Oct 57.15 → 16.10). Targets are 2×risk, so winning
trades pay roughly half to a quarter of their 5-min payoff, while
losing trades still cost a full risk plus ₹40 and occur at similar
frequency. The grid change therefore shrinks rewards more than it
shrinks losses. No 1-min trade carried a risk under ~5 points, so no
result above rests on a knife-edge risk (the two smallest morning
risks, 5.90 on 24 Apr and 5.95 on 7 Sep, sit just above the ~5
threshold and are noted, not relied on).

## Task 3 — Verdict against the pass bar

Pass bar for (lA) scope: 60% green on the failing set (30 Mar, 2 Apr,
13 May — needs 2/3) AND total positive AND combined NOT below (lA) on
the same window, winners not collapsed, no-trade counted separately
from green.

| Leg | Required | 1-min result | Pass? |
|---|---|---|---|
| Failing set green | 2/3 | 1/3 — only 13 May flips (+₹4,590); 30 Mar still loses (−₹3,120), 2 Apr still loses (−₹1,730) | **No** |
| Cluster 1 total positive | > 0 | −₹4,875 (worse than 5-min −₹2,720) | **No** |
| Combined not below (lA) | ≥ +₹80,660 | +₹13,895 | **No** |
| Winners not collapsed | ~12/14 green, ~₹83,380 | 10/14 green, ₹18,770 (two winners flip to losses: 24 Apr, 8 Oct) | **No** |
| No-trade counted separately | — | Cluster 0 no-trade; winners 2 no-trade (same two days as 5-min) | — |

**Family (x) FAILS its pass bar and is exhausted. No scoped 1-min
variant is carried forward.** The single flip (13 May) is reported, not
adopted: its 1-min trade is a different, smaller trade than the 5-min
one (same entry 23,337.30, but signal-bar stop 23,360.45 vs 23,387.65,
risk 23.15 vs 50.35, target hit 09:37) — the flip is produced by the
finer grid shrinking the target, the same mechanism that collapses
the winners. Carrying 13 May alone forward would be cherry-picking
one leg of a failed family. Per the task instruction, no whole-month
run is done on these days, and no out-of-sample claim is made for the
1-min variant.

One honest qualification on the diagnostic: the 1-min replay's 2 Apr
morning trade stops at 10:53 — the exact spike minute identified in
the diagnostic — so that day's failure is doubly confirmed across
both grids. The 1-min replay does **not** rescue 30 Mar or 2 Apr in
any form: both still lose, on different (earlier, smaller) trades.

## Diagnostic note only (NOT a candidate tested here)

2 Apr afternoon reversal, at 1-min resolution: after the re-entry
stop minute 11:33 (close 22,215.30), Nifty rallied all afternoon to a
15:10 close of 22,746.25 (max 1-min close 22,770.00 at 15:16), a
~531-point reversal against the PE direction. This is recorded only
as the factual backdrop for the next family; no direction-flip trade
was simulated, sized, or costed here.

## Next family

**Direction-flip as a separate system, not a PE fix.** The PE
breakdown leg is now closed on this evidence: its entry-bar stops are
real at 1-min resolution, finer resolution does not convert the
failing set, and it shrinks winner payoffs. Any flip work must be
specified and validated as its own system (own entry, stop, target,
and paper validation), not as a patch that keeps PE trades alive.

## Files

- Engine: [nifty_cluster1_x_1min_sweep.py](sandbox://workspace/trading/nifty_cluster1_x_1min_sweep.py)
- Raw JSON: [nifty_cluster1_x_1min_sweep_raw.json](sandbox://workspace/trading/nifty_cluster1_x_1min_sweep_raw.json)
- Fetch script: [fetch_1min_x.py](sandbox://workspace/trading/fetch_1min_x.py)
- 1-min cache: `~/workspace/trading/data/1min/NIFTY/` and `~/workspace/trading/data/1min/BANKNIFTY/` (44 files, 375 bars each) plus `data/1min/manifest_1min_x.json`
- This report: [nifty_cluster1_x_1min_sweep.md](sandbox://workspace/trading/nifty_cluster1_x_1min_sweep.md)

Paper only. No orders were placed, no live-trading recommendation is
made, and no variant from this family is adopted.
