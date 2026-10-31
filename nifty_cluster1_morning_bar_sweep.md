# NIFTY — Forward validation of the gap+belowPDL box + Cluster 1 morning-bar sweep
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): (1) forward-validate the gap+belowPDL box with
thresholds FROZEN before the test, on trades it was not fitted on, and
DISCARD it if it fails there, do NOT re-fit; (2) attack Cluster 1's
morning bar itself, since waiting families are exhausted for Cluster 1
(timing, retest, survival all 0–37.5%, because trades stop in 1–5 bars).
Pass bar, same as all prior sweeps: **60% green AND cluster total
positive AND winners not collapsed.** No-trade is counted separately
from green throughout. A variant that only avoids losses, or only
turns total positive on later signals, is NOT a pass.

Engine: `morning_bar_sweep.py`, raw replay `morning_bar_sweep_raw.json`,
universe replay `morning_bar_universe.json`, replayed bar by bar from the
Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv`,
`spot_daily.csv`), same exit logic as all prior sweeps: entry = next
bar open after signal, stop = signal high (PE), target = entry −
2 × risk, stop checked before target on each bar including the entry
bar, square-off 15:10, 100 shares equivalent, ₹40/trade.
Survival-partial logic (interpretation B, N=10) was re-verified before
use: it reproduces Cluster 3 exactly (+₹4,589: +₹1,630 / +₹1,366 /
+₹1,594) and the 14 winners exactly (+₹69,334, once the Skill winner
2026-03-23, +₹7,260, is included alongside the 13 V4 winners).

## Headline — both families are exhausted, nothing passes, box is DISCARDED

- **Family 1, frozen box: FAILS out-of-sample, DISCARD it.**
  Box, frozen exactly as specified: **gap in [−0.90%, −0.65%] AND
  signal close >200 points below the previous-day low.** No threshold
  was moved, widened, or re-fitted in this test.
  On 92 out-of-sample Nifty PE breakdown days (see below) the box
  fires exactly **once** (1.1%), and that one hit is NOT a
  Cluster-3-like trade: 2026-05-11 loses −₹5,035, and its partial
  never triggers, so partial-only-inside-the-box changes the
  out-of-sample total by **₹0**. In 2025 alone (65 PE days) the box
  fires **zero** times. It also catches **zero** of the 10
  out-of-sample slow give-back-like trades. A discriminator that
  fires once in 92 days, on a trade it cannot help, is not a live
  rule. It is discarded here, not re-fitted, not carried forward,
  and not used to adopt the Cluster 3 partial.
- **Family 2, morning bar: NO variant passes Cluster 1.**
  Best green rate is **1/8 = 12.5%** (M1, M2, M3, M4, M5), far short
  of 60% (5/8). Every morning-bar variant leaves Cluster 1's total
  **negative** (best −₹6,045, M11, on 0 greens and 6 no-trades).
  Best combined PE total (Cluster 1 + 14 winners) is M1 at +₹64,460,
  still **below baseline +₹66,980**. Morning-bar shape does not
  separate Cluster 1 from winners: Cluster 1 signal bars are
  mostly already strong red bars (see feature table), so a
  "strong bar only" filter mostly keeps the same losing trades
  and, on the one day it changes, it replaces the morning trade
  with the later signal the timing gates already found.
- **Nothing in this report is adopted, and nothing is carried into
  a whole-month run on its own.** The long-horizon task continues
  in the parent conversation — this is exhaustion of Families 1–2
  in this task, not completion of the task.

## Family 1 — Forward validation of the gap+belowPDL box (frozen)

### Universe (trades the box was NOT fitted on)

One PE breakdown trade per day, scanned exactly as in the prior
sweeps: V4 setup2 conditions first (close < OR low, close < PDL,
room ≥ 200 × scale, OR width ≤ 360 × scale, signal ≤ 11:30); if no
V4 signal, the Skill OR-breakdown signal (close < OR low, close
< PDL, no width/room cap). Dates in the Jan–Oct 2026 V5 PE set
(25 trades: 8 Cluster 1, 3 Cluster 3, 14 winners) are excluded from
the out-of-sample universe. Cache covers 2025-01-01 to 2026-10-28,
452 daily rows, so the out-of-sample universe is a different year
(2025) plus the non-V5 days of 2026. November 2026 paper days do
not exist yet in the cache and are therefore not claimed here;
when they arrive they are a further, still-unrun validation set,
not a substitute for this one.

| Universe | PE days | Green | Loss | Square-off | Baseline total (₹) |
|---|---|---|---|---|---|
| In-sample V5 PE (fitted, for reference) | 25 | 14 | 11 | 0 | +56,395 |
| Out-of-sample, all | 92 | 37 | 55 | 5 | +25,560 |
| Out-of-sample, 2025 only | 65 | 27 | 38 | 5 | +35,930 |
| Out-of-sample, 2026 non-V5 only | 27 | 10 | 17 | 0 | −10,370 |
| Out-of-sample, Skill-mode only, 2026 | 5 | 3 | 2 | 0 | (see universe file) |

Baseline out-of-sample total (+₹25,560) is not a claim about the
system as a whole — it is the denominator against which the
box's incremental value is measured, on the same provisional
cash exit (100 shares, ₹40/trade) as every prior sweep.

### Box result, frozen thresholds, no re-fitting

| Group | Box hits | Box green | Box loss | Box total (₹) | Partial-only-in-box total (₹) | Delta vs baseline (₹) |
|---|---|---|---|---|---|---|
| In-sample V5 (fitted) | 3/25 | 0 | 3 | −10,585 | +71,569 | +15,174 |
| Out-of-sample, all | **1/92** | 0 | 1 | −5,035 | **+25,560** | **0** |
| Out-of-sample, 2025 | 0/65 | 0 | 0 | 0 | +35,930 | 0 |
| Out-of-sample, 2026 non-V5 | 1/27 | 0 | 1 | −5,035 | −10,370 | 0 |

The in-sample row is shown only to prove the box was applied
correctly (it recovers exactly the 3 Cluster 3 days, and
partial-only-in-box recovers the survival Cluster 3 gain).
The out-of-sample row is the verdict, and it fails on every
leg:

1. **Hit rate 1.1% (1/92), 0% in 2025.** A rule that almost never
   fires cannot carry a Cluster 3 exit into live use, whatever
   its in-sample precision.
2. **The sole hit is not Cluster-3-like.** 2026-05-11: V4 signal
   09:35, gap −0.867%, belowPDL 244.85 pts (inside the frozen
   box), entry 23,881.35, stop 23,931.30, risk 49.95 pts, stop
   11:20, net **−₹5,035**, bars-to-stop 20 in this engine's
   counting (slow, like Cluster 3), but MFE only **36.1% of
   target distance** — below the 45% partial level (0.9 × risk),
   so the survival partial never triggers and its survival net
   is identical: −₹5,035. The box flagged a slow loser, not a
   partial-able give-back.
3. **Sensitivity for slow give-back is 0/10.** Out-of-sample
   slow give-back-like trades, defined as baseline stop with
   bars-to-stop ≥ 10 in this engine's counting (≡ ≥ 11 in the
   prior sweeps' counting) and MFE ≥ 48% of target distance:
   10 trades (2025-01-10, 2025-01-17, 2025-03-03, 2025-05-20,
   2025-09-23, 2025-12-02, 2025-12-03, 2025-12-17, 2026-06-03,
   2026-08-31), all with survival nets positive (+₹1,033 to
   +₹2,802, i.e. the partial WOULD have helped each of them) —
   and **none** is inside the box. Their gaps range from −0.456%
   to +0.303% and their belowPDL values from 0.9 to 124.85 pts;
   the box's gap band and its 200-point floor both miss every
   one. The box does not identify the phenomenon it was fitted
   to describe; it identifies 3 specific days in 2026.
4. **Near-miss check (why not just widen it):** widening is
   re-fitting, which the task forbids, and the near misses show
   it would not rescue the box anyway. Gap-band-only
   out-of-sample hits (6): 2025-01-27 (square-off +₹6,520),
   2025-02-03 (stop −₹3,230), 2025-02-24 (square-off +₹3,200),
   2025-04-01 (target +₹14,770), 2026-05-11 (the box hit),
   2026-07-24 (target +₹3,500) — a mix of winners, square-offs
   and one loser, not a Cluster 3 population. BelowPDL->200-only
   out-of-sample hits (2): 2025-02-28 (target +₹12,050) and
   2026-05-11. Neither leg alone, and no widening of either leg
   that stays honest, turns the box into a slow-give-back
   detector, because the out-of-sample slow trades sit at
   belowPDL < 125 pts — the 200-point floor is on the wrong
   side of them entirely.

**Verdict on Family 1: DISCARD the gap+belowPDL box.**
Do not re-fit its gap band, its 200-point floor, or its
conjunction. Do not use it to adopt the Cluster 3 partial.
The Cluster 3 partial (survival B N=10) remains what the
prior sweep left it: solved on its own 3 days, but with no
validated live discriminator, so it must still be judged on
its all-PE combined total, where it loses to baseline.

## Family 2 — Cluster 1's morning bar itself

### Why this family, and what "morning bar" means here

Waiting families cannot fix Cluster 1 by construction: timing
waits for a later bar, retest waits for a pullback, survival
waits 10–20 bars — and Cluster 1 stops in 1–5 bars. The stop
family already tested buffer stops (+10/+20 pts, worse totals)
and the OR-high stop (4/8 green but total −₹31,910, risks
87–188 pts). What had NOT been tested as a scan filter was the
shape of the breakdown bar itself: its body, its upper wick,
its range, and its range relative to the opening range, plus
the day-level shape of the opening range (which bar makes the
OR low). Each variant below is a **scan-continuation filter**:
the scan takes the FIRST bar ≤ 11:30 that is both a breakdown
(close < OR low, close < PDL, V4 room/width conditions, or
Skill conditions for 2026-04-02) AND meets the morning-bar
condition; if no bar meets it by 11:30, the day is a no-trade.
That is the same scan semantics as the timing and distance
sweeps, so a "green" under a filter can be a later signal —
flagged as such where it occurs, exactly as in those sweeps.
A pure day-level filter (M11) is stated separately.

### Feature table — Cluster 1 signal bars (why body/wick filters struggle)

Body ratio = |close − open| / range; upper-wick ratio =
(high − max(open, close)) / range. All 8 Cluster 1 signal bars
are red (close < open).

| Date | Signal | Range | Body | Body ratio | Upper wick | Upper-wick ratio | OR width | Range / OR width |
|---|---|---|---|---|---|---|---|---|
| 2026-01-09 | 09:30 | 52.30 | 3.95 | 0.076 | 32.00 | 0.612 | 101.45 | 0.52 |
| 2026-02-06 | 09:35 | 31.60 | 19.35 | 0.612 | 2.15 | 0.068 | 77.25 | 0.41 |
| 2026-03-30 | 11:25 | 22.45 | 13.05 | 0.581 | 7.00 | 0.312 | 147.90 | 0.15 |
| 2026-04-02 (Skill) | 09:55 | 22.00 | 14.30 | 0.650 | 6.75 | 0.307 | 185.50 | 0.12 |
| 2026-05-13 | 09:30 | 51.95 | 29.75 | 0.573 | 19.95 | 0.384 | 141.35 | 0.37 |
| 2026-06-29 | 09:30 | 48.90 | 48.60 | 0.994 | 0.00 | 0.000 | 78.40 | 0.62 |
| 2026-07-08 | 09:30 | 25.60 | 19.55 | 0.764 | 1.30 | 0.051 | 65.35 | 0.39 |
| 2026-08-19 | 09:30 | 27.25 | 24.40 | 0.895 | 0.75 | 0.028 | 79.80 | 0.34 |

For comparison, the 14 winners' signal bars have body ratios
0.168–0.965 and upper-wick ratios 0.000–0.509 (weakest winner
bars: 2026-09-29 body 0.168 / wick 0.503; 2026-05-05 body 0.378 /
wick 0.509). Cluster 1 bars are mostly already strong red bars
(6 of 8 body ≥ 0.57, 5 of 8 wick ≤ 0.31) — there is no "weak
bar" signature to filter on. Only 2026-01-09 is a genuinely
weak bar (body 0.076, wick 0.612), and it is the one day every
filter changes.

### Variant summary — Cluster 1 (8 trades, baseline 0/8, −₹24,290) + winners (14, baseline 14/14, +₹91,270)

Baseline combined PE (Cluster 1 + winners) = **+₹66,980**.
Pass requires Cluster 1 ≥ 5/8 green AND Cluster 1 total > ₹0
AND winners not collapsed.

| Variant | Cluster 1 green | Cluster 1 no-trade | Cluster 1 still loss | Cluster 1 total (₹) | Winners green / total (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 | 14/14 / +91,270 | +66,980 | — |
| M1 body ≥ 0.50 | 1/8 | 0 | 7 | −14,505 | 13/14 / +78,965 | +64,460 | No |
| M2 body ≥ 0.70 | 1/8 | 1 | 6 | −16,330 | 12/14 / +74,345 | +58,015 | No |
| M3 upper-wick ≤ 0.30 | 1/8 | 1 | 6 | −14,635 | 12/14 / +70,740 | +56,105 | No |
| M4 upper-wick ≤ 0.15 | 1/8 | 1 | 6 | −18,135 | 9/14 / +39,835 | +21,700 | No |
| M5 body ≥ 0.50 AND wick ≤ 0.30 | 1/8 | 1 | 6 | −14,635 | 13/14 / +72,225 | +57,590 | No |
| M6 signal range ≥ 30 pts | 0/8 | 3 | 5 | −18,785 | 10/14 / +72,155 | +53,370 | No |
| M7 signal range ≥ 40 pts | 0/8 | 3 | 5 | −18,970 | 7/14 / +49,785 | +30,815 | No |
| M8 body ≥ 0.70 AND wick ≤ 0.15 | 0/8 | 2 | 6 | −22,370 | 10/14 / +45,245 | +22,875 | No |
| M9 range ≥ 40% of OR width | 0/8 | 3 | 5 | −19,925 | 6/14 / +40,530 | +20,605 | No |
| M10 range ≥ 60% of OR width | 0/8 | 7 | 1 | −4,740 | 1/14 / +6,990 | +2,250 | No |
| M11 OR-low maker ≠ 09:15 (day filter) | 0/8 | 6 | 2 | −6,045 | 8/14 / +51,510 | +45,465 | No |

No variant reaches 60% green, no variant has a positive
Cluster 1 total, and every variant's combined total is below
baseline. The morning-bar family is exhausted on these
thresholds; the thresholds are round numbers (0.50, 0.70,
0.30, 0.15, 30, 40 pts, 40%, 60%), not knife-edge fits, so
there is no "just move the threshold by 0.01" rescue that
would not itself be re-fitting.

### Day-by-day notes (the pattern behind the table)

- **M1 (body ≥ 0.50) — the best morning variant, still 1/8.**
  Only 2026-01-09 changes: its 09:30 bar (body 0.076) fails,
  the scan continues to the 10:50 later signal, target +₹6,040
  — the same later signal the timing gates already found, not
  the morning trade fixed. The other 7 Cluster 1 days are
  unchanged (their bars already pass). Winners: 13/14, but the
  one flip is expensive — 2026-09-29's 09:30 bar (body 0.168)
  fails, its 09:35 replacement stops at −₹4,295 (was +₹3,790),
  a −₹8,085 swing that wipes out Cluster 1's +₹9,785
  improvement and leaves combined below baseline.
- **M2/M3/M5 — the same single green, different damage.**
  All three green only 2026-01-09 (10:50, +₹6,040) and
  no-trade 2026-03-30, while 2026-05-13 worsens to −₹6,425
  (later 09:35 signal, 63.85-pt risk, the same worsening the
  timing sweep found) and 2026-04-02 worsens to −₹2,950
  (10:05 later signal). Winners fall to 12–13/14.
- **M4/M8 — tighter wick filters collapse winners.**
  M4 winners 9/14, +₹39,835; M8 winners 10/14, +₹45,245.
  A wick ≤ 0.15 rule rejects genuine winner bars whose
  breakdown bars carry a normal upper wick.
- **M6/M7 (range floors) — avoidance, not conversion.**
  0 greens, 3 no-trades each; the no-trades are 2026-03-30,
  2026-07-08 and 2026-08-19 (M6) — small-range signal bars
  that simply do not trade, while the large-range losers
  (2026-01-09, 2026-05-13, 2026-06-29) are unchanged.
- **M9/M10 (range share of OR) — near-total avoidance.**
  M10 trades only 2026-06-29 in Cluster 1 (still a loss,
  −₹4,740) and only 1 winner in 14 (combined +₹2,250).
  A filter that trades 1 day in 8 and 1 winner in 14 is not a
  trading rule, it is a refusal to trade.
- **M11 (OR-low maker ≠ 09:15, day-level) — best Cluster 1
  total, worst logic.** If the 09:15 bar makes the OR low, the
  whole day is a no-trade. Cluster 1: 6 no-trades, 2 losses
  (2026-01-09 −₹3,745 and 2026-08-19 −₹2,300, the two days
  whose OR low is made at 09:25), total −₹6,045, **0 greens**.
  Winners: 8/14 green, 6 no-trades, total +₹51,510 (from
  +₹91,270) — the filter deletes 6 genuine winners
  (2026-01-21, 2026-03-16, 2026-03-23, 2026-05-05, 2026-08-12,
  2026-09-07) to avoid 6 Cluster 1 losses. Avoidance at a
  1-for-1 winner cost, with zero conversion, is not a pass.

### Clusters 2 and 3 — not applied, as specified

Condition in the task: apply a passing variant to Clusters 2/3
only if it passes on Cluster 1. No morning variant passes, so
none is applied to Cluster 2 (reclaim failure CE, 2 trades,
−₹11,420 — a CE cluster, so a PE morning-bar filter does not
apply to it in any case) or Cluster 3 (slow PE give-back, 3
trades, −₹10,585) as a fix. For the record only: Cluster 3's
signal bars (body 0.931 / 0.938 / 0.622, wick 0.000 / 0.000 /
0.145) all pass M1, M3 and M5, so those filters would leave
Cluster 3 unchanged — they neither help nor hurt it, which
is consistent with Cluster 3 being an exit-rule problem, not
a morning-bar-shape problem.

## Variant summary — both families in this task, pass bar applied

| Family / variant | Cluster 1 green | Cluster 1 total (₹) | Winners total (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| Box (frozen) → partial only in box, out-of-sample | — (1 hit, 0 Cluster-3-like) | — | — | delta ₹0 on 92 days | **No — DISCARD** |
| M1 body ≥ 0.50 | 1/8 | −14,505 | +78,965 | +64,460 | No |
| M11 OR-low maker ≠ 09:15 | 0/8 | −6,045 | +51,510 | +45,465 | No |
| All other morning variants M2–M10 | 0–1/8 | −22,370 to −14,635 | +6,990 to +74,345 | +2,250 to +58,015 | No |

## What this sweep proves, and what it does not

- The gap+belowPDL box is dead as a live rule: 1 hit in 92
  out-of-sample days, 0 hits in 2025, 0 of 10 slow give-back
  trades caught, and the one hit cannot use the partial it
  was meant to gate. Discarding it is not a setback for the
  long-horizon task — it is the task working as specified:
  a post-hoc box either validates frozen or it is gone.
  The Cluster 3 partial's problem is now stated cleanly:
  the partial helps slow give-back trades wherever they
  occur (10/10 out-of-sample slow trades would have been
  helped by it), but there is no entry-time feature that
  identifies those trades in advance, and applying the
  partial universally still loses combined (prior sweep:
  survival B N=10 combined +₹49,633 vs baseline +₹56,395
  on the in-sample PE set, because Cluster 1 is untouched
  and winners are clipped).
- Cluster 1's morning bar is not the discriminator either.
  Its signal bars are, with one exception (2026-01-09),
  strong red bars indistinguishable in body, wick and range
  from winner bars. Every morning-bar filter therefore does
  one of three things: keeps the same losing trades (M1 on
  7 of 8 days), replaces the morning trade with a later
  signal already found by timing (2026-01-09 10:50,
  2026-06-29 11:30), or avoids trading at a 1-for-1 winner
  cost (M11). None converts a morning trade to green.
- What remains untested for Cluster 1 after this sweep:
  the stop bar itself — i.e. what the bar AFTER the signal
  does before the stop is hit — is already covered by the
  close-exit test (0/8) and the buffer test (worse totals);
  the remaining untried shape is a rule that does not
  filter the morning trade at all, but changes what happens
  after the first stop within the same day in combination
  with an exit change (re-entry + partial, tested
  separately, not together), or a rule that sizes the
  morning trade by the bounce bar's range rather than the
  signal bar's range. Those are the next families, not
  re-runs of body/wick/range thresholds.

## Next family to test (the task continues — this is NOT completion)

Families 1–2 in this task are exhausted. The next family must
not re-run body/wick/range thresholds, and must not re-fit
the discarded box:

1. **Out-of-sample check of the best morning variants
   (M1, M11) on the 92 out-of-sample PE days** — they are
   in-sample morning filters until they are checked there,
   and M11 in particular must be checked for the same
   winner-deletion cost it shows in-sample (6 winners
   deleted for 6 losses avoided).
2. **Combined same-day rules for Cluster 1:** re-entry
   (prior sweep: 2/8 days green combined) PLUS a partial/
   trail on the re-entry trade, tested as one rule, not as
   two separately reported rules — because the re-entry
   greens are later signals, and a partial on them may
   change their economics without changing the morning
   trade's loss.
3. **November 2026 paper as a fresh validation set** for
   any candidate that emerges from (1) or (2), with its
   thresholds frozen before November, exactly as the box
   was frozen here — and discarded on the same terms if
   it fails there.

Files: engine `morning_bar_sweep.py`, raw replay
`morning_bar_sweep_raw.json` (all morning-variant day nets
for Cluster 1 and winners, M11 day filter), universe replay
`morning_bar_universe.json` (all 117 PE days: 25 in-sample,
92 out-of-sample, with gap, belowPDL, box flag, baseline
net, survival-partial net, body/wick/range features).
Paper only throughout; no orders placed, nothing fabricated.
The long-horizon task continues in the parent conversation:
the next decision is which of the three next families above
to run — and none of the variants in this report is adopted.
