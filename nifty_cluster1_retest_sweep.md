# NIFTY — Retest-breakdown + Cluster 3 partial + Stall sweeps
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Source: `nifty_failing_cases_jan_oct_2026.md` Cluster 1 = Immediate
OR-breakdown PE bear-trap, 8 trades, original total −₹24,290, Jan–Aug 2026.
Previous families: timing (best 3/8 = 37.5% green), stop/distance/
re-entry (best genuine 4/8 = 50.0%, OR-high stop, total −₹31,910 —
worse than baseline; Z-degenerate 5/8 REJECTED), partial/trail
(early partial 20% reaches 5/8 and 10% reaches 6/8 on COUNT, but
greens are tiny ₹154–₹701, Cluster 1 total still negative
−₹6,074 / −₹2,422, and winner total collapses from +₹91,270 to
+₹22,348 / +₹17,757 — NOT adopted, per Chandu's rejection of tiny
wins as a way to fill a cap).

Engine: `retest_stall_sweep.py`, replayed bar by bar from the Upstox
5-min cache (`data/progressive/NIFTY/spot_5m.csv`), same exit order
as all prior sweeps: stop checked BEFORE target on each bar,
including the entry bar, square-off 15:10. 100 shares equivalent,
₹40/trade total cost. "Green" = net > ₹0. No-trade is counted
separately from green throughout. Square-off positives are flagged
separately where they occur.

**Pass bar for this task (stricter than count alone, as instructed):
a variant passes ONLY if it reaches 60% green on count AND Cluster
total turns positive AND winners do not collapse.** A positive total
built on 2–3 large later-signal targets while 5–6 trades still lose
is not a pass, and a count pass built on ₹150–₹700 partials is not
a pass. That bar is applied to every variant below.

## Headline — Families 1–3 are now exhausted, and only ONE passes, for Cluster 3 alone

- **Family 1, retest-breakdown entry: FAILS on Cluster 1.**
  Strict (second breakdown ≤ 11:30): 3/8 green (37.5%), 2 no-trade,
  3 still loss, Cluster 1 total +₹7,945 — positive total, but
  count is short of 60% by 2 trades, and the winner total
  COLLAPSES from +₹91,270 to +₹2,100 (3 green, 9 no-trade,
  2 losses on the 14 winning PE days). Combined PE (Cluster 1 +
  winners) is +₹10,045 vs baseline +₹66,980. Extended (second
  breakdown any time): 3/8 green, total +₹5,840, winners +₹5,375,
  combined +₹11,215 — still a failure on count and on winners.
  The retest greens are the SAME later signals the timing sweep
  already found (9 Jan 10:50 +₹6,040, 29 Jun 11:30 +₹6,840,
  19 Aug 10:10 +₹1,020). Retest is, in outcome, a timing gate
  with an extra bounce filter — it does not fix the morning
  trade, and it discards straight-down winners that never bounce.
- **Family 2, Cluster 3 partial/trail at a non-tiny level: PASSES
  for Cluster 3 alone, at 45% and 40% of target distance.**
  Partial 45% of target (0.9× risk) + trail to breakeven:
  3/3 green, total +₹4,589 (vs baseline −₹10,585), greens
  ₹1,630 / ₹1,366 / ₹1,594 — non-tiny, not ₹300 partials.
  Partial 40% (0.8× risk): 3/3 green, total +₹4,066, greens
  ₹1,444 / ₹1,210 / ₹1,412. Partial 50% (1.0× risk): only 2/3
  green, total −₹453 — still negative, because 13 Feb's MFE
  (48.1% of target) misses the 50% level by 1.9 points.
  **Caveat that must travel with this pass:** it is a
  Cluster 3 exit, not a universal entry rule. Applied to ALL
  PE trades, partial 45% cuts the winner total from +₹91,270
  to +₹42,977 (still 14/14 green, but −53%), and the all-PE
  combined (Cluster 1 + Cluster 3 + winners) falls from
  baseline +₹56,395 to +₹33,818. Applied to Cluster 1 alone,
  partial 45% gives only 2/8 green and −₹13,749. A Cluster 3
  partial can only be adopted if there is a live way to tell
  a slow give-back from an immediate bear-trap at entry —
  and there is none in this sweep: the distinction (bars to
  stop, MFE) is only known after the trade is already open.
  The pass is therefore recorded as a Cluster 3 exit
  improvement, NOT as a rule carried into a whole-month run
  on its own.
- **Family 3, stall exit (N = 10 and 20 bars): FAILS.**
  Cluster 3 stall 10: 1/3 green, total −₹4,445 (improved from
  −₹10,585, still negative). Stall 20: 0/3 green, −₹7,860.
  Cluster 1 stall 10 and 20: 0/8 green, −₹24,290 unchanged —
  exactly as predicted, because Cluster 1 stops in 1–5 bars,
  before any 10- or 20-bar stall can trigger. Stall is not a
  Cluster 1 fix at any N ≥ 10, and it is not a Cluster 3 fix
  at 10 or 20 either.
- **Side finding, not a pass:** stall 10 on Cluster 2 (reclaim
  CE, 2 trades) cuts the total from −₹11,420 to −₹2,100
  (14 Jan −₹30, essentially a scratch; 26 Oct −₹2,070 vs
  −₹8,635), with 0/2 green. That is loss-cutting, not
  conversion, and it is reported here because Cluster 2 was
  not the stall target — do not re-label it as a Cluster 2 fix.

No variant in Families 1–3 reaches 60% with positive economics
on Cluster 1. **Nothing in this report is adopted, and nothing
is carried into a whole-month run on its own.** The long-horizon
task continues in the parent conversation — this is exhaustion
of Families 1–3, not completion of the task.

## Family 1 — Retest-breakdown entry, defined so it can be reproduced

Definition (distinct from the two rules it is often confused with):
- The FIRST qualifying breakdown (V4 setup2 PE: close < OR low,
  close < PDL, room ≥ 200×scale, OR width ≤ 360×scale, signal
  ≤ 11:30; Skill OR for 2026-04-02 and 2026-03-23) is SKIPPED
  entirely. No loss is booked on it.
- Bounce = the first later bar whose CLOSE ≥ OR low (back
  into, or above, the opening range). A bar that merely touches
  the OR low intraday but closes below it does NOT count.
- Second breakdown = the first later bar after the bounce
  whose close < OR low and < PDL (same V4/Skill conditions).
- Entry = next bar open after the second signal, stop =
  second signal high, target = entry − 2 × risk, stop before
  target, square-off 15:10.
- R1 (strict): second signal must be ≤ 11:30, the original
  signal window. R2 (extended): second signal any time up to
  the last bar that still allows an entry bar before 15:10.
  R1 is the primary variant; R2 is reported separately so
  R1 is not cherry-picked by extending the window.
- This is NOT the second-close rule (which required two
  CONSECUTIVE closes below the OR low, with no bounce in
  between) and NOT the re-entry rule (which booked the
  first trade's stop loss first, then re-entered). Here the
  first breakdown is never traded at all.

### Family 1 — Cluster 1, day by day (original nets in brackets)

| Date | First | Bounce | Second (R1) | R1 result | R1 net (₹) | Second (R2) | R2 net (₹) |
|---|---|---|---|---|---|---|---|
| 2026-01-09 (−3,745) | 09:30 | 09:40 | 10:50 | target 11:35 | +6,040 | 10:50 | +6,040 |
| 2026-02-06 (−2,275) | 09:35 | 09:45 | 09:55 | stop 10:00, risk only 2.25 pts | −265 | 09:55 | −265 |
| 2026-03-30 (−2,055) | 11:25 | 11:30 | — (11:45 is after 11:30) | no-trade | — | 11:45, stop 11:55 | −2,105 |
| 2026-04-02 (−2,115, Skill) | 09:55 | 10:00 | 10:05 | stop 10:10 | −2,950 | 10:05 | −2,950 |
| 2026-05-13 (−5,075) | 09:30 | 09:50 | — (no second breakdown) | no-trade | — | — | — |
| 2026-06-29 (−4,740) | 09:30 | 09:35 | 11:30 | target 12:30 | +6,840 | 11:30 | +6,840 |
| 2026-07-08 (−1,985) | 09:30 | 09:45 | 10:20 | stop 10:30 | −2,740 | 10:20 | −2,740 |
| 2026-08-19 (−2,300) | 09:30 | 09:45 | 10:10 | target 10:15, risk only 5.30 pts | +1,020 | 10:10 | +1,020 |

Summary — R1 strict: **3/8 green (37.5%), 2 no-trade, 3 still
loss, traded total +₹7,945** (vs baseline −₹24,290).
R2 extended: **3/8 green, 1 no-trade, 4 still loss, traded
total +₹5,840** (30 Mar trades and loses −₹2,105; 13 May
still has no second breakdown at any time).

Why the total is positive while the count fails: the two
large later-signal targets (+₹6,040 and +₹6,840) outweigh
three small losses. That is the same total-vs-count trap
the timing sweep warned about — a positive total on 3/8
green is not "consistent green", and it is not counted
as a pass here.

Why retest adds nothing new: its three greens are
identical, trade for trade, to the timing sweep's later-
signal greens (9 Jan 10:50, 29 Jun 11:30, 19 Aug 10:10).
The bounce filter does not create a new trade; it
selects the same later breakdowns a time gate selects,
and it additionally requires a bounce, which is why
it loses winners (below). Two Cluster 1 days retest
can never fix as a morning trade: 30 Mar (first signal
already 11:25, second 11:45) and 13 May (bounce at
09:50, then no second breakdown at all — price never
closes below the OR low again that day).

### Family 1 — Winning PE days (14 days, original total +₹91,270)

| Date (original) | First | Bounce | Second (R1) | R1 result | R1 net (₹) | Second (R2) | R2 net (₹) |
|---|---|---|---|---|---|---|---|
| 2026-01-21 (+9,280) | 10:20 | 12:10 | — | no-trade | — | 14:25, stop 14:30 | −3,355 |
| 2026-02-24 (+7,350) | 09:30 | — (never closes ≥ OR low) | — | no-trade | — | — | — |
| 2026-03-16 (+8,940) | 10:20 | 11:15 | — | no-trade | — | — | — |
| 2026-03-13 (+5,400) | 09:45 | — | — | no-trade | — | — | — |
| 2026-03-23 (+7,260, Skill) | 09:50 | 14:00 | — | no-trade | — | 14:05, target 14:30 | +6,630 |
| 2026-04-24 (+8,820) | 09:30 | — | — | no-trade | — | — | — |
| 2026-05-05 (+5,040) | 10:30 | 11:00 | 11:05 | stop 11:15 | −2,380 | 11:05 | −2,380 |
| 2026-07-22 (+6,320) | 09:30 | 10:05 | 10:10 | target 10:25 | +3,620 | 10:10 | +3,620 |
| 2026-08-12 (+6,250) | 09:55 | 10:30 | 10:35 | target 10:45 | +1,740 | 10:35 | +1,740 |
| 2026-08-27 (+3,000) | 09:55 | — | — | no-trade | — | — | — |
| 2026-09-29 (+3,790) | 09:30 | 11:10 | — | no-trade | — | — | — |
| 2026-09-07 (+2,990) | 09:50 | 10:00 | 10:05 | target 10:10, risk 4.10 pts | +780 | 10:05 | +780 |
| 2026-10-08 (+5,440) | 09:40 | 10:00 | 10:05 | stop 10:10 | −1,660 | 10:05 | −1,660 |
| 2026-10-23 (+11,390) | 10:05 | — | — | no-trade | — | — | — |

Summary — R1 strict winners: **3 green, 9 no-trade, 2 losses,
total +₹2,100** (vs baseline +₹91,270, 14/14 green).
R2 extended winners: **4 green, 7 no-trade, 3 losses, total
+₹5,375**. Combined PE, R1: Cluster 1 +₹7,945 + winners
+₹2,100 = **+₹10,045** (baseline +₹66,980). Combined PE, R2:
+₹5,840 + ₹5,375 = **+₹11,215**.

The mechanism is plain: most genuine winners never bounce —
price goes straight down from the first breakdown and never
closes back at or above the OR low (24 Feb, 13 Mar, 24 Apr,
27 Aug, 23 Oct). A rule that requires a bounce therefore
discards the straight-down winners entirely, while keeping
only the choppy winners that happen to re-break down later.
Retest is not a Cluster 1 fix; it is a winner-destroying
filter with the same later signals timing already found.

### Family 1 — Cluster 3 extension check (not a pass, not carried)

Retest on Cluster 3's 3 PE days (same definition):
13 Feb: first 09:30, bounce 09:40, second 09:45, stop 09:50,
−₹2,165 (was −₹3,750). 30 Apr: first 10:00, bounce 12:10,
no second breakdown, no-trade. 18 May: first 09:35, bounce
09:40, second 09:45, stop 10:15, −₹3,000 (was −₹3,670).
**0/3 green, 1 no-trade, total −₹5,165** (R1 and R2 identical
here). Retest does not fix Cluster 3 either — its second
breakdowns are just smaller, faster versions of the same
give-back.

## Family 2 — Cluster 3 on its own terms: partial/trail at a non-tiny level

Cluster 3 = slow PE breakdown give-back, 3 trades, baseline
total −₹10,585: 13 Feb −₹3,750 (MFE 48.1% of target distance,
stop 35 bars), 30 Apr −₹3,165 (83.0%, 26 bars), 18 May
−₹3,670 (57.0%, 11 bars). The failure was an exit failure:
the trade moved half to four-fifths of the way to target,
then reversed through the signal high with no partial and
no trail in the provisional exit.

Rule tested (one level at a time): original entry/stop/
target; book 50 shares at the partial level, move the
remaining 50 shares' stop to breakeven (entry); adverse
(current stop) checked before favourable (partial/target)
each bar, as in the prior partial sweep. Partial level is
stated as a fraction of the FULL target distance (2× risk),
so 50% = 1.0× risk, 45% = 0.9× risk, 40% = 0.8× risk.

| Variant | 13 Feb | 30 Apr | 18 May | Green | Total (₹) | Pass? |
|---|---|---|---|---|---|---|
| Baseline (no partial) | −3,750 | −3,165 | −3,670 | 0/3 | −10,585 | No |
| Partial 50% + trail BE | −3,750 (MFE 48.1% misses 50% by 1.9 pts) | +1,523 (partial 10:15, BE stop 10:35) | +1,775 (partial 09:55, BE stop 10:00) | 2/3 (66.7%) | −453 | **No — count passes, total still negative** |
| **Partial 45% + trail BE** | **+1,630 (partial 10:15, BE stop 10:25)** | **+1,366 (partial 10:15, BE stop 10:35)** | **+1,594 (partial 09:50, BE stop 10:00)** | **3/3 (100%)** | **+4,589** | **Yes, for Cluster 3 alone** |
| Partial 40% + trail BE | +1,444 (partial 10:15, BE stop 10:25) | +1,210 (partial 10:15, BE stop 10:35) | +1,412 (partial 09:50, BE stop 10:00) | 3/3 (100%) | +4,066 | Yes, for Cluster 3 alone |

These greens are non-tiny by the task's own test: every
green at 45% and 40% is ₹1,210–₹1,630, booked as
50 × (0.9× or 0.8× risk) − ₹40, not ₹150–₹700. The 45%
level is the highest level that captures all three
Cluster 3 days — 50% fails on 13 Feb by a 1.9-point MFE
miss, which is a knife-edge in the other direction, and
40% works but books less per trade. 45% is therefore
the Cluster 3 level to carry forward as a candidate,
not 50% and not 40%.

Application check (as instructed — apply a passing variant
to the other clusters, and check winners):
- Cluster 1, partial 45% + trail BE: 2/8 green
  (6 Feb +₹966, 13 May +₹2,226), 6 still loss, total
  **−₹13,749** (vs baseline −₹24,290). Improves Cluster 1,
  does not pass it. Partial 50% on Cluster 1: 1/8 green,
  −₹16,738. Partial 40% on Cluster 1: 2/8 green, −₹14,112.
  No Cluster 3 partial level passes Cluster 1.
- Cluster 2 (CE reclaim, mirrored partial: book 50 at
  entry + frac × 2 × risk, trail to breakeven):
  partial 50%: 1/2 green (14 Jan +₹1,333; 26 Oct still
  −₹8,635, MFE 41.0% misses 50%), total −₹7,303.
  Partial 45%: 1/2 green (14 Jan +₹1,195; 26 Oct still
  −₹8,635), total −₹7,440.
  Partial 40%: 2/2 green (14 Jan +₹1,058; 26 Oct +₹3,398,
  partial 10:05, BE stop 10:25), total +₹4,456 — but
  26 Oct's MFE is 41.0% of target, so the 40% trigger
  clears it by only 1.0 point. That is a knife-edge
  pass, not a robust one, and it must not be presented
  as a Cluster 2 fix without that warning.
- Winners (14 PE days), partial 45% + trail BE:
  14/14 green, total **+₹42,977** (vs baseline +₹91,270).
  Partial 50%: 14/14, +₹46,793. Partial 40%: 14/14,
  +₹40,681. Winners stay green under a partial, but
  their value is roughly halved, because most winners
  book half at 0.9× risk and scratch the rest at
  breakeven on the mid-trade retracement to entry.
  All-PE combined under partial 45%: Cluster 1 −₹13,749
  + Cluster 3 +₹4,589 + winners +₹42,977 = **+₹33,818**
  (baseline all-PE: −₹24,290 − ₹10,585 + ₹91,270 =
  **+₹56,395**). A universal partial 45% is therefore
  WORSE in combined economics than the baseline, even
  though it fixes Cluster 3 alone. That is why the
  Cluster 3 pass cannot be carried into a whole-month
  run as a blanket rule: it needs a live discriminator
  between a slow give-back and an immediate bear-trap
  or a straight winner, and no such discriminator has
  been tested yet.

## Family 3 — Stall exit (N = 10 and 20 bars)

Rule tested (one N at a time): original entry/stop/target;
track the best favourable extreme from the entry bar
onward (lowest low for PE, highest high for CE). A bar
that does not make a new favourable extreme increments
the stall counter; a new extreme resets it to 0.
Counting starts on the bar AFTER the entry bar. When
the counter reaches N, exit at that bar's close
(stop/target checked first on that bar). Square-off
15:10 still applies.

| Variant | Cluster 3 (3) | Cluster 1 (8) | Cluster 2 (2) | Winners (14) |
|---|---|---|---|---|
| Baseline | 0 green, −10,585 | 0 green, −24,290 | 0 green, −11,420 | 14 green, +91,270 |
| Stall 10 | 1 green, −4,445: 13 Feb +1,220 (stall 11:05, exit 25,536.40 vs entry 25,549.00); 30 Apr −1,995 (stall 12:05, vs −3,165); 18 May −3,670 unchanged (stop 10:30 before 10 stall bars elapse without a new low) | 0 green, −24,290 unchanged (every Cluster 1 stop hits in 1–5 bars, before any stall can trigger) | 0 green, −2,100: 14 Jan −30 (stall 12:50, essentially a scratch, vs −2,785); 26 Oct −2,070 (stall 10:55, vs −8,635) | 14 green, +78,775: 12 targets unchanged; 24 Feb target becomes stall +1,085 (vs +7,350); 22 Jul target becomes stall +90 (vs +6,320) |
| Stall 20 | 0 green, −7,860: 13 Feb −1,025 (stall 11:55, vs −3,750); 30 Apr −3,165 unchanged (stop 12:10); 18 May −3,670 unchanged | 0 green, −24,290 unchanged | 0 green, −11,420 unchanged (both stops hit before 20 stall bars) | 14 green, +87,590: 13 targets unchanged; 22 Jul target becomes stall +2,640 (vs +6,320) |

Verdict: stall 10 improves Cluster 3 and Cluster 2 losses
without converting them (except 13 Feb, a genuine stall
green at +₹1,220), and stall 20 is weaker still. Stall
does not reach 60% on any cluster, and stall 10 damages
two winners badly (24 Feb and 22 Jul, both still green
only because their stall exits happen to close above
entry). Stall is a loss-cutter, not a converter, and it
is not carried forward as a fix.

## Variant summary — all three families, pass bar applied

| Family / variant | Cluster 1 green | Cluster 1 total (₹) | Winners total (₹) | Combined PE Cluster 1 + winners (₹) | Passes 60% + positive + no winner collapse? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| 1. Retest strict (≤11:30) | 3/8 (37.5%) | +7,945 | +2,100 | +10,045 | **No** (count fails, winners collapse) |
| 1. Retest extended (any time) | 3/8 (37.5%) | +5,840 | +5,375 | +11,215 | **No** (count fails, winners collapse) |
| 2. Cluster 3 partial 50% + trail BE | (Cluster 3: 2/3) | (Cluster 1 context: 1/8, −16,738) | +46,793 | — | **No for Cluster 3** (total −453) |
| 2. Cluster 3 partial 45% + trail BE | (Cluster 3: 3/3, +4,589) | (Cluster 1 context: 2/8, −13,749) | +42,977 | +33,818 all-PE | **Yes for Cluster 3 alone; No as a universal rule** (combined falls) |
| 2. Cluster 3 partial 40% + trail BE | (Cluster 3: 3/3, +4,066) | (Cluster 1 context: 2/8, −14,112) | +40,681 | — | **Yes for Cluster 3 alone; No as a universal rule** |
| 3. Stall 10 | 0/8 | −24,290 | +78,775 | +54,485 | **No** (0% on Cluster 1 and Cluster 3 count 1/3) |
| 3. Stall 20 | 0/8 | −24,290 | +87,590 | +63,300 | **No** |

## What this sweep proves, and what it does not

- Cluster 1's morning breakdown is not fixed by waiting
  for a bounce and re-breaking down. The retest trade
  IS the later trade timing already found, and the
  bounce requirement throws away the straight-down
  winners that never bounce. If the morning trade is
  to be fixed, it will not be by re-entering the same
  breakdown later in the day.
- Cluster 3's failure IS an exit failure, and a
  non-tiny partial (45% of target, 0.9× risk, trail
  to breakeven) fixes it on its own 3 days with
  ₹1,366–₹1,630 greens. That is the first genuine,
  non-tiny, positive-total pass in this long-horizon
  work — but it is scoped to Cluster 3, and scoping
  it to Cluster 3 at entry time is the unsolved part.
- Stall is a loss-cutter, not a converter. Its best
  use in this sweep is not Cluster 1 or Cluster 3 at
  all, but Cluster 2's reclaim (stall 10: −₹11,420 to
  −₹2,100, 0 green) — and even there it converts
  nothing to green.
- No family here changes the Cluster 1 verdict from
  the earlier sweeps: timing 37.5%, stop genuine 50%,
  retest 37.5%, partial (non-tiny) 25%, stall 0%.
  Cluster 1 remains unfixed as a morning entry.

## Next family to test (the task continues — this is NOT completion)

Families 1–3 in this task are exhausted. The next family
must attack the two gaps this sweep leaves open, not
re-run timing, stop, or retest in a new costume:

1. **Survival-gated exit (the Cluster 3 partial, without
   the universal winner damage):** book the 45% partial
   and trail to breakeven ONLY if the trade is still
   open after N bars (e.g. 10 bars) — i.e. the partial
   applies to trades that have survived long enough
   to be Cluster 3-like, not to every trade from the
   entry bar. Cluster 1 trades (stopped in 1–5 bars)
   are already out before the gate, fast winners that
   reach target before N bars are untouched, and only
   slow trades (Cluster 3, and slow winners) get the
   partial. Test N = 10 and 20, on Cluster 3, Cluster 1,
   Cluster 2, and the 14 winners, with the same
   60% + positive-economics bar.
2. **A live Cluster 3 discriminator, tested honestly:**
   at entry, is there any signal-time feature (bars
   since OR, gap size, OR width, bias score, first-bar
   range) that separates the 3 Cluster 3 days from the
   8 Cluster 1 days and the 14 winners? If no feature
   separates them, say so — a Cluster 3-only exit
   cannot be adopted without one, and the honest
   conclusion is that the partial must be judged on
   its all-PE combined total, where it currently loses
   to baseline.
3. **Cluster 2 on its own terms (stall + partial, not
   retest):** stall 10 already cuts Cluster 2 to
   −₹2,100, and partial 40% turns both Cluster 2 days
   green (+₹4,456) but on a 1.0-point MFE knife-edge
   for 26 Oct. Test stall 10 combined with a partial
   at 45% on Cluster 2 alone, day by day, before
   claiming anything for the reclaim scenario.

Files: engine `retest_stall_sweep.py`, raw replay
`retest_stall_sweep_raw.json` (retest strict/extended,
Cluster 3 partials, stall 10/20, all day nets above;
Cluster 2 partial and winner partial runs were computed
with the same `partial_trail` function and their day
nets are in the tables above). Paper only throughout;
no orders placed, nothing fabricated. The long-horizon
task continues in the parent conversation: the next
decision is whether the Cluster 3 45% partial counts
as a scoped pass, or whether the survival-gated exit
family is tested next.
