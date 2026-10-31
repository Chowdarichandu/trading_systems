# NIFTY — Out-of-sample morning check + Combined re-entry + partial/trail rule
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): morning-bar / box families are done
(`nifty_cluster1_morning_bar_sweep.md`): gap+belowPDL box DISCARDED
(frozen validation on 92 out-of-sample PE days: 1 hit, 0 Cluster-3-like,
delta ₹0, 0/10 out-of-sample slow give-back trades inside the box);
morning-bar filters: best M1 body ≥ 0.50 is 1/8 green, M11 OR-low maker
≠ 09:15 is 0/8 green with 6 no-trades and winners falling to 8/14.
Nothing adopted, nothing carried to a whole-month run.

This task, Nifty only, paper only, same pass bar (60% green AND total
positive AND winners not collapsed), no re-fitting of the discarded
box, no re-running body/wick/range thresholds alone:

1. Out-of-sample check of M1 and M11 on the 92 out-of-sample PE days
   (universe in `morning_bar_universe.json`).
2. Combined same-day rule for Cluster 1: re-entry PLUS a partial/trail
   on the re-entry trade, tested as ONE rule, not as two separately
   reported rules. Replay all 8 Cluster 1 days + 14 winners,
   no-trade counted separately from green.
3. Prepare (do NOT run yet, November has not happened) a November 2026
   paper spec for any candidate emerging from (1) or (2), with
   thresholds FROZEN before November, exactly as the box was frozen —
   and to be discarded on the same terms if it fails there.

Engine: `combined_sweep.py`, raw replays `combined_sweep_oos.json`
(92 out-of-sample days, M1/M11/baseline per day) and
`combined_sweep_cluster1.json` (combined-rule day nets). Replayed bar
by bar from the Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv`,
`spot_daily.csv`), same exit logic as all prior sweeps: entry = next
bar open after signal, stop = signal high (PE), target = entry −
2 × risk, stop checked before target on each bar including the entry
bar, square-off 15:10, 100 shares equivalent, ₹40/trade. Green =
net > ₹0 (this includes square-off positives, as in prior sweeps;
they are flagged separately in the counts below).

## Headline — both families exhausted, nothing passes, nothing adopted

- **Family 1, M1 out-of-sample: FAILS the conversion bar.**
  On the 55 out-of-sample baseline losses, M1 turns only **4 green
  (7.3%)**, with 4 no-trades and 47 still losses. On the fast-stop
  subset most like Cluster 1 (stop, universe bars ≤ 4, n = 28) it is
  **3/28 green (10.7%)**. Its out-of-sample total is higher than
  baseline (+₹39,590 vs +₹25,560), but that is later-signal
  replacement, not conversion — and it costs 5 genuine winners
  flipped to losses (−₹19,905 winner deletion cost). It is NOT a pass.
- **Family 1, M11 out-of-sample: FAILS catastrophically, confirming
  the in-sample warning.** 0 greens on the 55 baseline losses,
  16 no-trades, 39 still losses; total collapses to **−₹885** (from
  baseline +₹25,560) because it deletes **14 of 37 winners**
  (−₹72,350 deletion cost, including a +₹14,770 winner on
  2025-04-01) while converting nothing. M11 is dead out-of-sample
  as well as in-sample. Do not carry it forward.
- **Family 2, combined re-entry + partial: FAILS, and the partial
  makes the re-entry worse, not better.** Best combined variant is
  C-SURV at **2/8 green, total −₹18,237** — worse than re-entry
  alone (2/8 green, −₹17,355), because the partial clips the two
  re-entry targets that made the day green. C-A2 is 1/8 green,
  −₹21,602.50; C-A1 is 2/8 green, −₹19,850. No combined variant
  reaches 60% (5/8), none has a positive Cluster 1 total, and
  winners are unchanged only because the partial applies to the
  re-entry trade alone (winners never stop, so no re-entry
  triggers) — that does not rescue a negative cluster total.
- **Nothing in this report is adopted, and nothing is carried into
  a whole-month run on its own.** Family 3 is therefore preparation
  only: no candidate emerged, so **no thresholds are frozen for
  November adoption** — see `nifty_november2026_paper_spec_combined.md`,
  which pre-registers the November pass rules and reserves November
  as validation for the NEXT family's candidate, with the best
  variant here (C-SURV) shadow-logged only, not as an adoption
  candidate. The long-horizon task continues in the parent
  conversation — this is exhaustion of Families 1–2 in this task,
  not completion of the task.

## Family 1 — Out-of-sample check of M1 and M11

### Universe and definitions, stated before the results

Universe: the 92 out-of-sample Nifty PE breakdown days from
`morning_bar_universe.json` (in_sample == False): 65 in 2025, 27 in
2026 non-V5 days. One PE breakdown trade per day, scanned exactly as
in the prior sweeps (V4 setup2 conditions, or Skill OR-breakdown if
no V4 signal; mode per day taken from the universe file). Baseline
recomputed here reproduces the universe baseline exactly: **92 days,
37 green (32 targets + 5 square-off positives), 55 stops, total
+₹25,560** (2025: +₹35,930; 2026 non-V5: −₹10,370).

- **M1:** scan-continuation filter — the scan takes the first bar
  ≤ 11:30 that is both a breakdown (close < OR low, close < PDL,
  V4 room/width or Skill conditions) AND has body ratio
  |close − open| / range ≥ 0.50; if no bar meets it by 11:30, no-trade.
- **M11:** day filter — if the 09:15 bar makes the OR low (the
  minimum low among the 09:15/09:20/09:25 OR bars), the whole day is
  a no-trade; otherwise the baseline trade is taken unchanged.
- **Cluster-1-like analogue out-of-sample:** there are no cluster
  labels out-of-sample, so two subsets are reported, neither fitted
  after the fact: (a) all 55 baseline losses, and (b) the fast-stop
  subset — baseline exit = stop with universe bars ≤ 4 (n = 28),
  the speed most like Cluster 1's 1–5-bar stops. Conversion is
  measured on those subsets; the overall total is reported
  separately so a total improvement built on later signals cannot
  be presented as conversion.
- **Winner deletion cost:** for the 37 baseline-green days, sum of
  (variant net − baseline net) for traded days, plus −baseline net
  for no-trade days (deleted winners). Flipped-to-loss and deleted
  counts are reported separately.

### Results — out-of-sample, all 92 days

| Variant | Green | No-trade | Still loss | Traded total (₹) | vs baseline (₹) |
|---|---|---|---|---|---|
| Baseline | 37/92 | 0 | 55 | +25,560 | — |
| M1 body ≥ 0.50 | 36/92 | 4 | 52 | +39,590 | +14,030 |
| M11 OR-low maker ≠ 09:15 | 23/92 | 30 | 39 | −885 | −26,445 |

### Results — on the 55 baseline losses (the conversion test)

| Variant | Green | No-trade | Still loss | Traded total (₹) | Baseline losses total (₹) |
|---|---|---|---|---|---|
| Baseline (by construction) | 0/55 | 0 | 55 | −183,050 | −183,050 |
| M1 | **4/55 (7.3%)** | 4 | 47 | −149,115 | −183,050 |
| M11 | **0/55 (0%)** | 16 | 39 | −137,145 | −183,050 |

M1 greens on baseline losses (all later signals, not the original
morning trade fixed): 2025-12-02 (−₹2,290 → +₹1,830),
2026-01-08 (−₹965 → +₹3,260), 2026-03-11 (−₹2,780 → +₹2,690),
2026-05-12 (−₹2,320 → +₹8,640). M1 no-trades on losses:
2025-05-15, 2025-07-21, 2026-08-10, 2026-09-09.
M11 no-trades on losses (16): 2025-01-17, 2025-02-10, 2025-02-21,
2025-06-12, 2025-06-18, 2025-08-06, 2025-11-18, 2025-12-02,
2025-12-11, 2025-12-17, 2025-12-18, 2026-01-19, 2026-01-29,
2026-04-09, 2026-08-25, 2026-09-09 — avoidance, zero conversion.

### Results — fast-stop subset (n = 28, Cluster-1-like speed)

| Variant | Green | No-trade | Still loss | Traded total (₹) |
|---|---|---|---|---|
| Baseline | 0/28 | 0 | 28 | −65,190 |
| M1 | **3/28 (10.7%)** | 4 | 21 | −38,730 |
| M11 | **0/28 (0%)** | 7 | 21 | −52,920 |

### Winner deletion cost — the reason M1's higher total is not a pass

Baseline winners: 37 days, total **+₹208,610** (32 targets +
5 square-off positives totalling +₹30,040).

- **M1 on winners: 32/37 green, 0 no-trade, 5 flipped to loss,
  total +₹188,705, deletion cost −₹19,905.**
  Flipped winners: 2025-07-25 (+₹4,340 → −₹3,875),
  2025-08-26 (+₹1,990 → −₹2,860), 2026-02-12 (+₹800 → −₹1,205),
  2026-07-24 (+₹3,500 → −₹2,330), 2026-08-11 (+₹3,010 → −₹155).
  M1's overall +₹14,030 improvement is therefore +₹33,935 on
  losses minus ₹19,905 on winners — a net gain built on 4 later
  signals, at a 5-winner cost, with a 7.3% loss-conversion rate.
  That is not 60% green, and it is not consistent green.
- **M11 on winners: 23/37 green, 14 deleted (no-trade), 0 flipped,
  total +₹136,260, deletion cost −₹72,350.**
  Deleted winners include 2025-04-01 (+₹14,770), 2025-11-06
  (+₹7,020), 2025-08-07 (+₹6,720), 2025-10-14 (+₹6,470),
  2025-04-25 (+₹5,640), 2025-10-31 (+₹5,360), 2025-10-08
  (+₹4,710), plus 2025-02-24, 2025-07-11, 2025-12-26, 2026-07-24,
  2026-08-17, 2026-08-18, 2026-08-24. M11 deletes a winner for
  every loss it avoids (16 loss no-trades vs 14 winner deletions),
  converts zero losses, and turns the out-of-sample total
  negative. The in-sample pattern (6 winners deleted for 6 losses
  avoided, 0 greens) is confirmed out-of-sample, worse.

Split by year (for the record, not a separate pass claim):
2025 (65 days): baseline +₹35,930, M1 +₹40,265, M11 +₹8,315.
2026 non-V5 (27 days): baseline −₹10,370, M1 −₹675, M11 −₹9,200.
Neither variant turns the 2026 out-of-sample leg positive.

**Verdict on Family 1: M1 and M11 both fail out-of-sample.**
M1 fails on conversion (7.3% on losses, 10.7% on fast stops, vs
60% required) despite a higher total; M11 fails on every leg
(0% conversion, total negative, winner deletion −₹72,350).
Neither is adopted, neither is carried into a whole-month run,
and neither changes the in-sample verdicts (M1 1/8, M11 0/8).

## Family 2 — Combined same-day rule: re-entry + partial/trail

### Rule, defined as ONE rule before the replay

- **Trade 1:** the baseline Cluster 1 trade (V4 setup2 PE breakdown,
  2026-04-02 Skill; entry next bar open, stop = signal high,
  target = entry − 2 × risk, ₹40 cost).
- **If Trade 1 stops:** ONE re-entry only — the first bar after the
  stop bar whose close is back below the OR low, up to 11:30,
  becomes the re-entry signal (definition exactly as in the stop
  sweep's `replay_reentry`); entry = next bar open, stop = that
  bar's high, target = entry − 2 × risk, ₹40 cost charged again
  (two trades = two costs).
- **Partial/trail on the re-entry trade ONLY** (not on Trade 1):
  - **C-A2 (main combined rule):** book 50 shares at entry −
    0.5 × risk (25% of target distance), remaining stop moves to
    breakeven (entry). This is the A2 partial from the partial/
    trail sweep, which was the best partial on original trades
    (4/8 green there) — applied here only to the re-entry leg.
  - **C-A1 (sensitivity):** book 50 shares at entry − 1.0 × risk
    (50% of target distance), remaining stop to breakeven.
  - **C-SURV (sensitivity):** survival B N=10 — book 50 shares at
    entry − 0.9 × risk, but only if that level is reached by the
    gate bar (signal + 1 + 10 bars), remaining stop to breakeven;
    if the target is reached before the gate, the full target is
    booked (this is why 2026-01-09's C-SURV re-entry equals its
    raw target, see below).
- **Day outcome = Trade 1 net + re-entry net (with partial).**
  No re-entry (price never closes back below OR low after the stop,
  up to 11:30) ⇒ day = Trade 1 net only. No-trade is counted
  separately from green; there are no no-trades in this family
  (every Cluster 1 day trades at least Trade 1).
- **Winners under this rule:** unchanged — a winner never stops,
  so no re-entry triggers, and the partial applies only to the
  re-entry trade. Winner total stays at baseline **14/14,
  +₹91,270** for every combined variant. That is stated, not
  hidden: it means the winner leg cannot rescue a negative
  Cluster 1 total here, and the combined PE total is simply
  Cluster 1 total + ₹91,270.

Reference point, re-entry alone (stop sweep, for comparison only —
this task's verdict is on the combined rule, not on re-entry alone):
re-entry trade alone 3/8 green, +₹6,935 on 6 trades; day combined
(original + re-entry) **2/8 green, total −₹17,355**.

### Results — Cluster 1, 8 days, baseline 0/8, −₹24,290

| Combined variant | Day green | No-trade | Still loss | Cluster 1 total (₹) | Combined PE (Cluster 1 + winners ₹91,270) |
|---|---|---|---|---|---|
| Re-entry alone (reference) | 2/8 | 0 | 6 | −17,355 | +73,915 |
| **C-A2: re-entry + partial 0.5× risk, trail BE** | **1/8** | 0 | 7 | **−21,602.50** | **+69,667.50** |
| C-A1: re-entry + partial 1.0× risk, trail BE | 2/8 | 0 | 6 | −19,850 | +71,420 |
| C-SURV: re-entry + survival B N=10 | 2/8 | 0 | 6 | −18,237 | +73,033 |

Day-by-day combined nets (original → re-entry raw → re-entry with
partial → day combined):

| Date | Original | Re-entry raw | C-A2 day | C-A1 day | C-SURV day |
|---|---|---|---|---|---|
| 2026-01-09 | −3,745 | +6,040 | +15.00 | +775.00 | +2,295.00 |
| 2026-02-06 | −2,275 | −265 | −2,540.00 | −2,540.00 | −2,540.00 |
| 2026-03-30 | −2,055 | no re-entry | −2,055.00 | −2,055.00 | −2,055.00 |
| 2026-04-02 (Skill) | −2,115 | −2,950 | −5,065.00 | −5,065.00 | −5,065.00 |
| 2026-05-13 | −5,075 | no re-entry | −5,075.00 | −5,075.00 | −5,075.00 |
| 2026-06-29 | −4,740 | +6,840 | −480.00 | +380.00 | +208.00 |
| 2026-07-08 | −1,985 | −2,740 | −4,725.00 | −4,725.00 | −4,725.00 |
| 2026-08-19 | −2,300 | +1,020 | −1,677.50 | −1,545.00 | −1,280.00 |

### Why the partial hurts the re-entry

The re-entry greens are exactly the later signals already found by
timing, distance and re-entry sweeps (2026-01-09 10:50, 2026-06-29
11:30, 2026-08-19 10:10). A partial on those trades books half the
position early and trails the rest to breakeven, so a trade that
would have reached its full 2× target now books roughly half that
target on the second half:

- 2026-01-09: raw re-entry +₹6,040 → C-A2 +₹3,760 (day +₹15, barely
  green), C-A1 +₹4,520 (day +₹775), C-SURV +₹6,040 unchanged (target
  reached before the survival gate, so no partial was booked).
- 2026-06-29: raw +₹6,840 → C-A2 +₹4,260 (day −₹480, **flips the
  day from green to loss**), C-A1 +₹5,120 (day +₹380, still green
  but ₹1,720 smaller than re-entry alone's +₹2,100 day), C-SURV
  +₹4,948 (day +₹208).
- 2026-08-19: raw +₹1,020 never turns the day green under any
  variant (−₹2,300 + ₹1,020 = −₹1,280 raw; partials make it
  −₹1,677.50 / −₹1,545.00 / −₹1,280.00).

In other words, the partial does not convert a single additional
day to green, and it shrinks or destroys the two re-entry greens
that existed. C-A2, the main combined rule, is the worst of the
three (1/8 green) precisely because its early 0.5×-risk partial
clips the most. Combining two separately non-passing ideas
(re-entry 2/8, partial on originals 4/8 but on a different leg)
does not add up to a pass — on the re-entry leg, the partial is
a cost, not a fix.

**Verdict on Family 2: all combined variants fail.**
Best is C-SURV at 2/8 green (25%), total −₹18,237 — still short
of 60% by 3 trades, still negative in total, and still worse than
re-entry alone. No combined variant is adopted, and none is
applied to Clusters 2/3 (condition not met). For the record:
Cluster 2 is a CE reclaim cluster, so a PE re-entry rule does not
apply to it in any case; Cluster 3 is an exit-rule problem on its
own trades, and a partial on a Cluster 1 re-entry leg is not its
fix — Cluster 3's own partial remains unvalidated as a live rule
because its discriminator (the gap+belowPDL box) was discarded.

## Family 3 — November 2026 paper spec (preparation only, NOT run)

No candidate emerged from Families 1–2, so **no thresholds are
frozen for November adoption**. The spec file
`nifty_november2026_paper_spec_combined.md` pre-registers:

- The November paper universe (Nifty PE breakdown days in November
  2026, same V4/Skill scan, same provisional cash exit, paper only,
  1 trade/day, no orders).
- The pass rule a future candidate must meet in November before
  any adoption is discussed: November Cluster-1-like green ≥ 60%
  AND November PE total positive AND winners not collapsed
  (winner total at least 80% of the baseline winner total on the
  same November days — a guardrail, not a fitted threshold).
- The discard rule: a candidate failing any leg in November is
  discarded on the same terms as the gap+belowPDL box, not re-fitted
  on November data.
- C-SURV (best combined variant here, 2/8, −₹18,237) is
  shadow-logged in November only — its daily nets are recorded
  alongside the baseline, but it is NOT the adoption candidate,
  and a November shadow total above baseline does not adopt it
  without a fresh candidate from the next family passing the
  pre-registered rule.

November has not happened; no November day is claimed in this
report, and no November run was made.

## Variant summary — both families in this task, pass bar applied

| Family / variant | Green (conversion test) | Total (₹) | Winners (₹) | Pass? |
|---|---|---|---|---|
| Baseline, in-sample PE (Cluster 1 + winners) | 0/8 (Cluster 1) | Cluster 1 −24,290; combined +66,980 | +91,270 | — |
| M1, in-sample Cluster 1 | 1/8 | −14,505 | +78,965 | No |
| M1, out-of-sample losses | 4/55 (7.3%) | OOS total +39,590 | deletion −19,905 | **No** |
| M11, in-sample Cluster 1 | 0/8 | −6,045 | +51,510 | No |
| M11, out-of-sample losses | 0/55 (0%) | OOS total −885 | deletion −72,350 | **No — dead** |
| Re-entry alone (reference) | 2/8 | −17,355 | +91,270 (unchanged) | No |
| C-A2 combined (main) | 1/8 | −21,602.50 | +91,270 (unchanged) | **No** |
| C-A1 combined | 2/8 | −19,850 | +91,270 (unchanged) | No |
| C-SURV combined (best) | 2/8 | −18,237 | +91,270 (unchanged) | **No** |

## What this sweep proves, and what it does not

- M1 does not generalise as a loss converter. In-sample it was
  1/8 green on Cluster 1; out-of-sample it is 4/55 on losses and
  3/28 on fast stops. Its higher out-of-sample total is a
  later-signal effect, bought with 5 flipped winners. A filter
  whose conversion rate is 7–11% out-of-sample is not a 60% rule.
- M11 is confirmed dead twice over. It converts nothing in-sample
  (0/8) and nothing out-of-sample (0/55, 0/28 fast), and its
  winner-deletion cost grows out-of-sample (−₹72,350, 14 winners)
  versus in-sample (−₹39,760, 6 winners). Any future proposal
  that is a day-level no-trade filter must answer this cost
  first, before its avoided losses are quoted.
- Combining re-entry with a partial does not rescue either idea.
  The partial's value in prior sweeps was on trades that moved
  toward target and then reversed (Cluster 3, and A2 on original
  Cluster 1 trades where it clipped winners to +₹24,644) — on the
  re-entry leg, the trades that matter are full-target later
  signals, and clipping them destroys the day's green. The
  lesson is specific: partial/trail helps a give-back trade, it
  hurts a clean later-signal target.
- What remains untested for Cluster 1 after this sweep: the
  families already named in the morning-bar report — a rule that
  sizes the morning trade by the bounce bar's range rather than
  the signal bar's range, or a rule that does not filter the
  morning trade at all but changes the morning trade's own exit
  in a way not yet tried (the close-exit, buffer, OR-high and
  partial families are all exhausted on the original trade).
  Those are the next families, not re-runs of M1/M11 thresholds,
  not a re-fit of the discarded box, and not another
  re-entry+partial combination with a different partial level
  presented as a new idea — C-A1, C-A2 and C-SURV already span
  early, mid and gated partials on the re-entry leg, and all
  three fail.

Files: engine `combined_sweep.py`, raw replays
`combined_sweep_oos.json` and `combined_sweep_cluster1.json`,
November spec `nifty_november2026_paper_spec_combined.md`.
Paper only throughout; no orders placed, nothing fabricated.
The long-horizon task continues in the parent conversation:
Families 1–2 in this task are exhausted, and the next decision
is which untried family to run — and none of the variants in
this report is adopted.
