# NIFTY Cluster 1 — Partial / Trail + Bias/Room + Narrow-OR sweeps
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Source: `nifty_failing_cases_jan_oct_2026.md` Cluster 1 = Immediate
OR-breakdown PE bear-trap, 8 trades, original total −₹24,290, Jan–Aug 2026.
Previous families: timing (best 3/8 = 37.5% green), stop/distance/re-entry
(best genuine 4/8 = 50.0%, OR-high stop with original target, total
−₹31,910 — worse than baseline; Z-degenerate 5/8 REJECTED as noise
targets, not reused here).
Engine: `partial_trail_sweep.py`, replayed bar by bar from the Upstox
5-min cache (`data/progressive/NIFTY/spot_5m.csv`), same signal scan
as the timing/stop sweeps (V4 setup2 PE breakdown: close < OR low,
close < PDL, room >= 200×scale, OR width <= 360×scale, signal <= 11:30;
2026-04-02 Skill: close < OR low, close < PDL, no width/room cap).
Entry = next bar open. 100 shares equivalent, ₹40/trade total cost.
Bar order, stated so results are reproducible: on each bar the adverse
level (stop / trailed stop) is checked BEFORE the favourable level
(partial / target), matching the original engine. A bar hitting both
is a stop, not a partial/target.
"Green" = net > ₹0. No-trade is counted separately from green
throughout. Square-off positives are flagged separately. 60% target
= at least 5 of 8 green. Winning set for impact checks: the same 14
V5 Nifty PE target days used in the timing/stop sweeps (original
total +₹91,270).

## Headline — READ THIS FIRST: the count reaches 60%, the economics do not

A very early partial booking DOES reach the 60% green count on
Cluster 1 — partial at 20% of target distance gives 5/8 green, and
partial at 10% gives 6/8 green — and, as instructed, those variants
were applied to Clusters 2 and 3, where they also turn every trade
green (see below). **This is NOT presented as an adopted fix, and
it must not be carried into a whole-month run on count alone,
for the same reason the Z-degenerate variant was rejected in the
stop sweep:**

- The partial greens are tiny: ₹154–₹701 at 20%, ₹112–₹464 at 10%
  (Cluster 1). They are not targets; they are 50 shares booked at
  0.4× / 0.2× risk, with the other 50 scratched at breakeven.
- Cluster 1 total is STILL negative under both: −₹6,074 at 20%,
  −₹2,422 at 10% (vs baseline −₹24,290). The two trades that never
  move at all (30 Mar, 2 Apr, MFE 0) cannot be saved by any partial,
  and at 20% the 29 Jun loss (−₹4,740) still dominates.
- Winner value collapses: the 14 winning PE days stay 14/14 green
  under early partials, but their total falls from +₹91,270 to
  +₹22,348 at 20% and +₹17,757 at 10%. Combined PE total (Cluster 1
  + winners) falls from baseline +₹66,980 to +₹16,274 at 20% and
  +₹15,335 at 10%. A rule that turns losers into ₹200 greens by
  capping winners at ~20% of their original profit is not
  "consistent green" in Chandu's sense — he has already rejected
  tiny wins as a way to fill a cap, and this is the same trap in
  a different form.
- What the early-partial result DOES prove, honestly: 6 of 8
  Cluster 1 trades move at least 10% of target distance (0.2× risk)
  in their favour before stopping out, and 5 of 8 move at least
  20% (0.4× risk). The failure is therefore not "price never goes
  our way" — it is that the full 2× target is too far for a trade
  whose stop sits inside the OR, and the original exit books
  nothing for a 10–40% favourable move. That is a real finding
  for the NEXT family (see "Next family" below), not a reason to
  adopt a 10% partial.

The task instruction was: report back when a variant reaches 60%
or when Families A+B+C are all exhausted. A variant HAS reached
60% on count, so this report is that report — with the
economics stated alongside the count, so the parent/Chandu can
decide whether count alone is enough, or whether the tiny-win
rejection (as with Z-degenerate) applies here too.

## Variant summary — Cluster 1, 8 trades, original total −₹24,290

| Family / variant | Green | No-trade | Still loss | Traded total (₹) | Winners total (₹) | Combined PE (₹) | Reaches 60%? |
|---|---|---|---|---|---|---|---|
| Baseline (signal high, 2× target) | 0 / 8 | 0 | 8 | −24,290 | +91,270 | +66,980 | No |
| A1 — partial 50% of target + trail to BE | 1 / 8 | 0 | 7 | −16,738 | +46,793 | +30,055 | No |
| A2 — partial 25% of target + trail to BE | 4 / 8 | 0 | 4 | −9,946 | +24,644 | +14,698 | No |
| A3 — trail activation at 100 index pts, to BE | 0 / 8 | 0 | 8 | −24,290 | +91,270 | +66,980 | No |
| A4 — trail to BE at 50% of target, NO partial | 0 / 8 | 0 | 8* | −19,255 | +48,230 | +28,975 | No |
| A5 — partial 50% of target, NO trail | 0 / 8 | 0 | 8* | −19,255 | +68,313 | +49,057 | No |
| **A-partial 20% of target + trail to BE** | **5 / 8** | **0** | **3** | **−6,074** | **+22,348** | **+16,274** | **YES, on count** |
| **A-partial 10% of target + trail to BE** | **6 / 8** | **0** | **2** | **−2,422** | **+17,757** | **+15,335** | **YES, on count** |
| A-partial 30% of target + trail to BE | 3 / 8 | 0 | 5 | −12,311 | +28,455 | +16,144 | No |
| A-partial 40% of target + trail to BE | 2 / 8 | 0 | 6 | −14,112 | +40,681 | +26,569 | No |
| B1 — room >= 200 pts absolute (as-coded) | 0 / 8 | 0 | 8 | −24,290 | +91,270 | +66,980 | No |
| B2 — bias-strong only (score < 20) | 0 / 8 | 3 | 5 | −14,825 | +36,820 | +21,995 | No |
| B3 — room >= 300×scale (as-coded) | 0 / 8 | 0 | 8 | −24,290 | +91,270 | +66,980 | No |
| B-depth >= 30 pts below PDL (scan-continue) | 1 / 8 | 1 | 6 | −14,615 | +91,250 | +76,635 | No |
| B-depth >= 50 pts below PDL (scan-continue) | 1 / 8 | 1 | 6 | −12,180 | +83,610 | +71,430 | No |
| B-depth >= 100 pts below PDL (scan-continue) | 0 / 8 | 4 | 4 | −7,115 | +8,510 | +1,395 | No |
| C1 — no trade if OR width <= 80 pts | 0 / 8 | 4 | 4 | −12,990 | +82,880 | +69,890 | No |
| C2 — no trade if OR width <= 100 pts | 0 / 8 | 4 | 4 | −12,990 | +54,890 | +41,900 | No |
| C3 — no trade if OR width <= 150 pts | 0 / 8 | 7 | 1 | −2,115 | +16,200 | +14,085 | No |

\* A4/A5 "still loss" includes one scratch: 13 May becomes −₹40
(trailed stop / partial-then-original-stop), which is a loss of
₹40, not green. It is counted in "still loss" because net <= ₹0.

## Family A — Partial / trail, one variant at a time

Partial split is 50/50 throughout: 50 shares booked at the partial
level, 50 shares remaining with the trailed stop (breakeven) or,
in A5, the original stop. Cost ₹40 is charged once per trade.

### A1 — partial at 50% of target distance (1.0× risk) + trail to BE: 1/8 green
Only 13 May reaches 1.0× risk favourably (MFE 74.75 vs risk 50.35).
It books +₹2,478 (50 × 50.35 − ₹40) and the remaining 50 scratch at
breakeven. Every other Cluster 1 day stops before reaching 1.0×
risk, so A1 is identical to baseline on 7 of 8 days.
Day nets: 9 Jan −₹3,745; 6 Feb −₹2,275; 30 Mar −₹2,055;
2 Apr −₹2,115; 13 May +₹2,478; 29 Jun −₹4,740; 8 Jul −₹1,985;
19 Aug −₹2,300. Total −₹16,738.
Winners: 14/14 green, +₹46,793 — partial booking halves winner
value even when the remaining leg reaches target, because half
the position is already booked at 1.0× risk instead of 2.0×.

### A2 — partial at 25% of target distance (0.5× risk) + trail to BE: 4/8 green
Closest genuine partial variant before the tiny-partial sweep
below. Greens are all partial greens (no full targets):
6 Feb +₹519 (partial 50 × 11.18 − ₹40), 13 May +₹1,219,
8 Jul +₹446, 19 Aug +₹525. Still losing: 9 Jan −₹3,745
(MFE 17.70 vs partial level 18.53 — misses by 0.83 points, the
narrowest miss in the whole sweep), 30 Mar −₹2,055 (MFE 0),
2 Apr −₹2,115 (MFE 0), 29 Jun −₹4,740 (MFE 13.25 vs 23.50).
Total −₹9,946. Winners: 14/14 green, +₹24,644 — again, winner
value is more than halved, because most winners book half at
0.5× risk and scratch the rest at breakeven on the mid-trade
retracement to entry.

### A3 — trail activation at 100 index points (the v4 activation rule): 0/8 green
No Cluster 1 trade ever moves 100 points favourably before its
stop (maximum MFE is 13 May's 74.75 points). A3 is therefore
exactly the baseline on all 8 days, and exactly the baseline on
all 14 winners (+₹91,270). The v4 100-point activation, which was
designed for Bank Nifty options spot moves, is simply out of
scale for Nifty cash trades with 19–50 point risks. It is not a
fix for this cluster at any scale that matters here.

### A4 — trail to breakeven at 50% of target, NO partial: 0/8 green
Only 13 May activates the trail (MFE > 1.0× risk) and it exits at
breakeven: −₹40 instead of −₹5,075. Every other day stops at the
original stop before activation. Total −₹19,255.
Winners: only 8/14 green, +₹48,230 — 6 winners that originally
reached target now scratch at −₹40, because a mid-trade
retracement to entry (which the original trade survived, because
its stop was above entry) now takes them out at breakeven before
the target is reached. A breakeven trail is actively harmful to
winners: it converts full targets into scratches. (An earlier
draft of this replay reported A4 winners at +₹26,710 because a
trailed stop was wrongly priced at the original stop; that bug
was found, fixed in `partial_trail_sweep.py`, and the replay was
re-run — the corrected A4 winner total is +₹48,230, and the
corrected Cluster 1 total is −₹19,255, not −₹24,290.)

### A5 — partial at 50% of target, NO trail: 0/8 green
13 May books a partial (+₹2,518 on 50 shares) but the remaining
50 still hit the original stop (−₹2,518), netting −₹40 — a
scratch, not green. All other days are baseline. Total −₹19,255.
Winners: 14/14 green, +₹68,313 (partial + full target on the
remaining half, no breakeven scratch). A5 proves the trail, not
the partial, is what creates the A1 green: without the trail,
a partial merely cancels itself against the remaining stop.

### Partial-level sweep — the 60% result, and why it is not a clean fix
Same 50/50 split and breakeven trail as A1/A2, only the partial
level varies. This is one family, tested level by level, not a
cherry-picked single day:

| Partial level (% of target distance) | Partial level (× risk) | Cluster 1 green | Cluster 1 total (₹) | Winners total (₹) | Combined PE (₹) |
|---|---|---|---|---|---|
| 10% | 0.2× | 6 / 8 | −2,422 | +17,757 | +15,335 |
| 20% | 0.4× | 5 / 8 | −6,074 | +22,348 | +16,274 |
| 25% (A2) | 0.5× | 4 / 8 | −9,946 | +24,644 | +14,698 |
| 30% | 0.6× | 3 / 8 | −12,311 | +28,455 | +16,144 |
| 40% | 0.8× | 2 / 8 | −14,112 | +40,681 | +26,569 |
| 50% (A1) | 1.0× | 1 / 8 | −16,738 | +46,793 | +30,055 |

Day nets at 20%: 9 Jan +₹701, 6 Feb +₹407, 30 Mar −₹2,055,
2 Apr −₹2,115, 13 May +₹967, 29 Jun −₹4,740, 8 Jul +₹349,
19 Aug +₹412.
Day nets at 10%: 9 Jan +₹331, 6 Feb +₹184, 30 Mar −₹2,055,
2 Apr −₹2,115, 13 May +₹464, 29 Jun +₹430, 8 Jul +₹155,
19 Aug +₹186.
The pattern is mechanical: a partial at X% + breakeven trail
turns green exactly those trades whose MFE exceeds X% of target
distance, and turns them green by exactly 50 × (X% × target
distance) − ₹40 — a few hundred rupees at 10–20%. The two
MFE-0 days (30 Mar, 2 Apr) can never turn green under any
partial, which is why 6/8 is the ceiling for this family on
Cluster 1 (at 10%, every trade with any favourable move at all
turns green, and the ceiling is reached). Winner totals fall
monotonically as the partial level falls, because winners also
book half their position at the early level and scratch the
rest on the first retracement to entry. At 10%, the average
winner nets ₹1,268 vs ₹6,519 originally.

## Family B — Bias / room filter

### B1 / B3 — room as coded in the original engine: NO effect (important finding)
The original scan defines room as (signal close − the highest PD
level BELOW the signal close), or infinity if no PD level is below
the close. For a PE breakdown, the signal close is below PDL —
the lowest PD level — so there is NO PD level below it, and room
is infinity for all 8 Cluster 1 days and all 14 winners. Raising
the room threshold to 200 points absolute (B1) or 300×scale (B3)
therefore changes nothing: 0/8 green, 0 no-trade, baseline totals
on both sides. The "room >= 200" condition in the original V4
scan is vacuous for breakdowns below PDL — it cannot filter
Cluster 1, and it never did. Any future room filter for
breakdowns must be defined differently (see depth below), not by
raising this threshold.

### B2 — bias-strong only (previous-day bias score < 20): 0/8 green, 3 no-trade
Bias scores (close position in previous-day range, %): 9 Jan 3.8,
6 Feb 34.9, 30 Mar 9.2, 2 Apr 26.2, 13 May 20.1, 29 Jun 6.3,
8 Jul 3.4, 19 Aug 0.0. Score < 20 keeps 9 Jan, 30 Mar, 29 Jun,
8 Jul, 19 Aug (5 trades, all still lose, total −₹14,825) and
filters 6 Feb, 2 Apr, 13 May to no-trade. Note 13 May (score
20.1) is filtered out by 0.1 points — a knife-edge, not a robust
separation. Winners: only 6/14 survive the filter (+₹36,820),
8 winners are no-trade. Combined +₹21,995, far below baseline.
Bias-strong is avoidance of 3 losses at the cost of 8 winners —
not a fix, and not a separator: the kept Cluster 1 trades are
still 0/5 green.

### B-depth — depth of the signal close below PDL (the meaningful room substitute)
Signal-close depth below PDL, Cluster 1: 9 Jan 21.30, 6 Feb 35.20,
30 Mar 336.35, 2 Apr 412.10, 13 May 10.45, 29 Jun 21.90,
8 Jul 128.90, 19 Aug 81.05. Winners: 11.00–438.55, overlapping
completely. Depth does not separate losers from winners either:
- Depth >= 30 (scan-continue to 11:30): 1/8 green (9 Jan +₹2,540
  on a later 10:55 signal, the same later signal the timing and
  distance sweeps already found), 1 no-trade (29 Jun), total
  −₹14,615; winners 14/14, +₹91,250; combined +₹76,635 — the
  highest combined total in this report, but still only 1/8
  Cluster 1 green, and the one green is a later signal, not a
  fixed morning trade.
- Depth >= 50: 1/8 green (9 Jan +₹4,790, later 11:10 signal),
  1 no-trade, total −₹12,180; winners 14/14, +₹83,610.
- Depth >= 100: 0/8 green, 4 no-trade, total −₹7,115; winners
  collapse to 6/14, +₹8,510; combined +₹1,395. Depth >= 100
  destroys winners while converting nothing.

## Family C — No-trade rule for a narrow OR

OR widths, Cluster 1: 9 Jan 101.45, 6 Feb 77.25, 30 Mar 147.90,
2 Apr 185.50, 13 May 141.35, 29 Jun 78.40, 8 Jul 65.35,
19 Aug 79.80. Thresholds were taken from these widths, as
instructed, and a filtered day is no-trade, NOT green:
- C1 (width <= 80): 4 no-trade (6 Feb, 29 Jun, 8 Jul, 19 Aug),
  4 still losing (9 Jan, 30 Mar, 2 Apr, 13 May), total −₹12,990;
  winners 12/14, +₹82,880; combined +₹69,890 — slightly above
  baseline combined, but only because it drops ₹11,300 of
  Cluster 1 losses while dropping ₹8,390 of winners. Green
  count 0/8.
- C2 (width <= 100): same 4 Cluster 1 no-trades as C1 (no
  Cluster 1 OR width falls between 80 and 100 except 9 Jan's
  101.45, which is just above), total −₹12,990; winners fall
  to 8/14, +₹54,890; combined +₹41,900.
- C3 (width <= 150): 7 no-trade, only 2 Apr (185.50) trades and
  loses −₹2,115; winners collapse to 2/14, +₹16,200;
  combined +₹14,085. At this threshold the rule is "almost
  never trade", not a filter.

Family C is pure avoidance in every variant: it converts
nothing to green, and wider thresholds destroy winners faster
than they avoid losses.

## Clusters 2 and 3 — application of the 60% variants (as instructed)

Because a variant reached 60% on Cluster 1 on count (partial
20% and 10%, trail to breakeven), those variants were applied
to Clusters 2 and 3, replayed bar by bar from the given
entry/stop/target (CE logic mirrored for Cluster 2: favourable
= high, adverse = low):

| Cluster / day | Original | Partial 20% + trail BE | Partial 10% + trail BE |
|---|---|---|---|
| Cluster 2, 2026-01-14 CE reclaim | −₹2,785 | +₹509 (partial, then BE stop 12:10) | +₹235 (partial, then BE stop 11:25) |
| Cluster 2, 2026-10-26 CE reclaim | −₹8,635 | +₹1,679 (partial, then BE stop 10:25) | +₹820 (partial, then BE stop 10:05) |
| Cluster 2 total | −₹11,420 | +₹2,188 | +₹1,055 |
| Cluster 3, 2026-02-13 PE give-back | −₹3,750 | +₹702 (partial, then BE stop 09:40) | +₹331 (partial, then BE stop 09:40) |
| Cluster 3, 2026-04-30 PE give-back | −₹3,165 | +₹585 (partial, then BE stop 10:35) | +₹273 (partial, then BE stop 10:35) |
| Cluster 3, 2026-05-18 PE give-back | −₹3,670 | +₹686 (partial, then BE stop 10:00) | +₹323 (partial, then BE stop 10:00) |
| Cluster 3 total | −₹10,585 | +₹1,973 | +₹927 |

So on count, partial 20% / 10% turns 2/2 of Cluster 2 and 3/3 of
Cluster 3 green as well — which is exactly what the Cluster 3
diagnosis predicted (those trades moved 48–83% toward target
before reversing, so any early partial + breakeven trail saves
them). But the same caveat applies, more strongly for
Cluster 2: October's ₹8,635 loss becomes a ₹1,679 / ₹820
partial green only because its MFE (70.45 points) exceeds the
early partial level — the trade still never reaches its target,
and the "fix" books less than a fifth of the original target
net (₹17,150). Cluster 3 is the one place where a partial/trail
is a genuine exit-rule improvement (its failure WAS an exit
failure), but at 10–20% the improvement is still a few hundred
rupees, not the target.

## Verdict — Families A+B+C

- 60% green on Cluster 1, on count: REACHED, by early partial
  booking only (20%: 5/8, 10%: 6/8). No bias/room filter and no
  narrow-OR rule reaches 60% on count; both are avoidance only.
- Best genuine (non-tiny) variant in these families: A2, partial
  25% + trail BE, 4/8 green, total −₹9,946 — still short of 60%
  by 1 trade, and still negative in total, with winner value
  cut to ₹24,644.
- Best Cluster 1 total in these families: partial 10%, −₹2,422
  — still negative, built on six tiny partial greens.
- Best combined PE total in these families: depth >= 30,
  +₹76,635 — but only 1/8 Cluster 1 green, and that green is a
  later signal already found by earlier sweeps.
- **No variant in Families A+B+C is adopted here, and none is
  carried into a whole-month run on count alone.** The early-
  partial result is recorded as a count-pass with failed
  economics, in the same category as the rejected Z-degenerate
  variant: counting it as "fixed" would mean redefining green
  down to ₹150–₹700 partials while destroying winner value.
  If Chandu decides the count is what matters and tiny partial
  greens count, then partial 20% (5/8, Cluster 1 −₹6,074,
  Clusters 2/3 also green) is the variant to carry forward —
  but that decision must be his, explicitly, because it
  contradicts his earlier "not tiny wins" correction.

## Next family to test (the task continues — this is NOT completion)

The sweeps so far prove what does NOT fix Cluster 1: the clock
(timing), the stop distance (buffer / OR-high / close-exit),
the signal distance, a re-entry after the stop, a bias/room
filter, a narrow-OR no-trade, and a full-size target with any
of those. What has NOT been tested yet, and is the logical next
family, is a change to the ENTRY itself on the morning bar:

1. **Retest-breakdown entry:** skip the FIRST breakdown close
   entirely; enter only on a SECOND breakdown after price has
   first bounced back into (or above) the OR low — i.e. the
   breakdown must survive a retest, not merely close below the
   OR low once. This is distinct from the second-close rule
   (which required consecutive closes below) and from the
   re-entry rule (which booked a loss first). It directly
   attacks the Cluster 1 mechanism (first close = morning
   extreme) without widening risk or shrinking the target.
2. **Cluster 3 on its own terms:** partial/trail at a non-tiny
   level (e.g. 50% of target, where Cluster 3's 48–83% MFE
   actually matters) tested as a Cluster 3 exit rule alone,
   not as a Cluster 1 fix — because Cluster 3's failure was
   an exit failure, and a 50% partial there books ₹1,500+
   per trade, not ₹300.
3. **Stall exit:** exit a trade that makes no favourable
   progress for N bars (e.g. 6 bars / 30 minutes) at the
   prevailing close, instead of waiting for the full stop —
   tested for Cluster 1's 1–5-bar stops it cannot help (they
   stop too fast), but it may matter for Cluster 3's 11–35-bar
   give-backs.

Files: engine `partial_trail_sweep.py`, raw replay
`partial_trail_sweep_raw.json` (A1–A5, B1–B3, C1–C3, baseline
props, winning-PE impact; partial-level sweep and depth sweep
were run as documented replays of the same engine logic and
their day nets are in the tables above). Paper only throughout;
no orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: the next decision is
whether early-partial count counts as a pass, or whether the
retest-breakdown entry family is tested next.
