# NIFTY — Family (w): pure target multiple + re-entry cooling delay + target-first ordering diagnostic — NO PASS, nothing adopted

## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (v) is done: no pass, nothing adopted. Previous best kept is
still (lA) on Cluster 1 (−₹2,720, 5/8 day-green), not adopted.
Cluster 3 survival N=10 (k=0.9, prior sweep) remains scoped to
Cluster 3 only, not re-run in (w). Cluster 2 remains recorded
unfixable on the available 6-trade sample — forward logging only,
no new rule.

Pass bar, same as (p)/(q)/(r)/(s)/(t)/(u)/(v): **60% green on the
failing set AND total positive AND combined NOT below (lA) on the
same window, winners not collapsed.** Green = net > ₹0.
**No-trade is counted separately from green throughout.**
100 shares equivalent, ₹40/trade, square-off 15:10, stop checked
before target on each bar except in the diagnostic §4, where the
ordering itself is the test. The failing set under (lA) is the
3 Cluster 1 days with day net ≤ ₹0: **30 Mar, 2 Apr, 13 May**.
60% of 3 therefore means **at least 2 of those 3 days green** —
a variant that preserves the 5 baseline greens and converts only
1 failing day is 6/8 overall but only 1/3 on the failing set, and
it fails the green leg. That distinction is applied throughout
this report and is the reason the headline table quotes both
counts.

Engine: `w_sweep.py`, raw replay `w_sweep_raw.json`, replayed bar
by bar from the Upstox 5-min cache, reusing `u_sweep.day_lA_plain`
for the (lA) baseline and `extended_window_sweep.scan_reentry`
for (lA) re-entry. (lA) is reproduced by the engine, not copied:
Cluster 1 5/8, −₹2,720; winners 12/14 green, 2 no-trade, +₹83,380;
combined **+₹80,660**. The 2 winner no-trades (24 Feb, 12 Aug)
are rescan no-signals, identical under every (w) variant — no
variant creates or deletes a winner trade.

## Part 1 — A genuinely new morning-bar axis: the target multiple

### Why this axis is new, and what it is not

No prior sweep changed the morning target multiple alone. Every
prior morning trade used target = entry − 2×risk, and every
target change in prior sweeps was bundled with something else:
a different stop (bounce-high stops, t2/t4/t6, recomputed at
2×new risk), a different entry (bounce-bar-close entry, delayed
entry), or a partial booking (50 shares at k×risk, the rest
trailed — families (o)/(p)/(q)/(u)/(v) in all their shapes).
A pure target multiple is none of those: **signal, entry bar,
entry price, stop price and risk are all unchanged; only the
full-size exit level moves**, from entry − 2×risk to
entry − m×risk, with the whole 100 shares exiting there.
It is executable as a limit order known at entry, unlike a
signal-close entry (look-ahead) or a target-first ordering
(§4, diagnostic only). It is also the last simple morning-exit
axis that had not been isolated: timing gates, second-close,
stop buffers, OR-high stop, close-above-OR-low exit, signal
distance, bias/room, narrow-OR no-trade, retest entry,
morning-bar body/wick/range filters M1–M10/M11, thin/gap/
below-PDL/OR-width filters, bounce-bar stops/arming,
bounce-persistence guards U1/U2 and every partial shape are
all already exhausted and are **not** re-run here.

Variants, defined before results:

- **W-T0.5:** target = entry − 0.5×risk, full size.
- **W-T1.0:** target = entry − 1.0×risk, full size.
- **W-T1.5:** target = entry − 1.5×risk, full size.
- In all three, stop-before-target per bar, square-off 15:10,
  and (lA) re-entry scan unchanged (band cap = original
  rescan risk, which is unchanged because entry/stop are
  unchanged) running only if the morning final exit is a
  plain stop. A morning that targets at the m-level does not
  re-enter, exactly as a 2× target morning does not.

### Results — Cluster 1 (8) + winners (14)

| Variant | Cluster 1 green / no-trade / total | Failing-set conversion (30 Mar / 2 Apr / 13 May) | Winners green / no-trade / total | Combined | vs (lA) +₹80,660 | Pass? |
|---|---|---|---|---|---|---|
| (lA) reference | 5/8 / 0 / −₹2,720 | 0/3 | 12/14 / 2 / +₹83,380 | +₹80,660 | — | Reference, total negative |
| **W-T0.5** | 6/8 / 0 / **+₹4,230** | **1/3** (13 May only) | 12/14 / 2 / +₹20,485 | +₹24,715 | **−₹55,945** | **No — failing-set 1/3, combined fails** |
| **W-T1.0** | 6/8 / 0 / **+₹7,350** | **1/3** (13 May only) | 12/14 / 2 / +₹41,450 | +₹48,800 | **−₹31,860** | **No — failing-set 1/3, combined fails** |
| **W-T1.5** | 5/8 / 0 / −₹2,720 | 0/3 | 12/14 / 2 / +₹62,415 | +₹59,695 | **−₹20,965** | **No — Cluster 1 identical, winners only taxed** |

Read the W-T0.5 / W-T1.0 rows correctly, because they are the
trap in this family: both pass the Cluster 1 total leg
(+₹4,230 / +₹7,350, positive) and reach 6/8 overall green, and
neither passes the full bar. The 6th green in both is 13 May
alone; the two untouched days never convert, so the failing-set
leg is 1/3 (33.3%), not 60%. And both fail the combined leg by
₹31,860–₹55,945, because every winner target is cut to
one-quarter (m=0.5) or one-half (m=1.0) of its (lA) value while
only one Cluster 1 day is converted. Winner green *count* never
collapses (12/12 traded winners stay green in every variant),
but winner *value* collapses — ₹62,895 at m=0.5, ₹41,930 at
m=1.0, ₹20,965 at m=1.5 — and the pass bar requires the total
too, not just the count. W-T1.5 is the cleanest proof that the
multiple alone cannot help Cluster 1: its Cluster 1 days are
byte-identical to (lA) (13 May's 1.5× level, entry − 75.53 =
23,261.77, is missed by 0.78 points — its entry-bar low is
23,262.55 — and it then stops as before), while winners lose
₹20,965 for nothing.

### Day-by-day — Cluster 1, all three multiples

(lA) day nets for reference: 9 Jan +₹2,295, 6 Feb +₹1,120,
30 Mar −₹2,055, 2 Apr −₹3,730, 13 May −₹5,075, 29 Jun +₹2,100,
8 Jul +₹955, 19 Aug +₹1,670.

| Date | (lA) morning → day | W-T0.5 morning → day | W-T1.0 morning → day | W-T1.5 morning → day |
|---|---|---|---|---|
| 2026-01-09 | stop −₹3,745, re 10:50 +₹6,040 → +₹2,295 | stop, re identical → +₹2,295 | stop, re identical → +₹2,295 | stop, re identical → +₹2,295 |
| 2026-02-06 | stop −₹1,810, re 10:20 +₹2,930 → +₹1,120 | stop, re identical → +₹1,120 | stop, re identical → +₹1,120 | stop, re identical → +₹1,120 |
| **2026-03-30** | stop −₹2,055, no re → −₹2,055 | **stop −₹2,055, no re → −₹2,055** | **stop −₹2,055, no re → −₹2,055** | **stop −₹2,055, no re → −₹2,055** |
| **2026-04-02** | stop −₹2,065, re 11:25 −₹1,665 → −₹3,730 | **stop, re identical → −₹3,730** | **stop, re identical → −₹3,730** | **stop, re identical → −₹3,730** |
| **2026-05-13** | stop −₹5,075, no re → −₹5,075 | **target 09:35 +₹2,477.50 → +₹2,477.50** | **target 09:35 +₹4,995 → +₹4,995** | stop −₹5,075, no re → −₹5,075 |
| 2026-06-29 | stop −₹4,740, re 11:30 +₹6,840 → +₹2,100 | stop, re identical → +₹2,100 | stop, re identical → +₹2,100 | stop, re identical → +₹2,100 |
| 2026-07-08 | stop −₹1,985, re 12:05 +₹2,940 → +₹955 | **target 09:35 +₹932.50 → +₹932.50** (no re-entry) | stop, re identical → +₹955 | stop, re identical → +₹955 |
| 2026-08-19 | stop −₹2,300, re 10:15 +₹3,970 → +₹1,670 | **target 09:35 +₹1,090 → +₹1,090** (no re-entry) | stop, re identical → +₹1,670 | stop, re identical → +₹1,670 |

Why the untouched days cannot convert at any multiple, in
numbers (stop-before-target, entry bar = the stop bar on both):

- **30 Mar:** risk 20.15. The 0.5× level (entry − 10.08 =
  22,458.03) *is* reached by the entry bar's low (22,457.35),
  but the same bar's high (22,506.30) reaches the stop first
  under stop-before-target, so the trade stops at −₹2,055
  before any target can fire — at m=0.5, 1.0 and 1.5 alike.
  Shortening the target cannot help a trade whose stop bar
  is also its entry bar and whose favourable excursion on
  that bar (10.75 points) is smaller than the stop distance
  on the same bar (38.20 points above entry). This is the
  same 1-bar / 0-MFE shape (r) proved, now shown to be
  target-multiple-proof as well.
- **2 Apr:** risk 20.25. The entry bar's low is only 5.60
  points below entry, so even the 0.5× level (10.13 points)
  is never reached before the entry-bar stop, and the
  (lA) re-entry (11:25, −₹1,665) is unchanged at every m
  because the morning stop itself is unchanged. No multiple
  touches this day at all: morning, re-entry and day net
  are identical to (lA) at m=0.5, 1.0 and 1.5.
- **13 May:** risk 50.35. The entry bar's low (23,262.55,
  74.75 below entry = 1.48× risk) reaches the 0.5× level
  (23,312.13) and the 1.0× level (23,286.95) on a bar whose
  high (23,339.35) does *not* reach the stop, so it targets
  at both m values — +₹2,477.50 at m=0.5, +₹4,995 at m=1.0.
  It misses the 1.5× level by 0.78 points, as above, and
  then stops. 13 May is therefore a target-multiple
  conversion, but it is the *only* failing-set conversion
  in the family, and it is a give-back conversion, not an
  untouched-day conversion — consistent with (u)/(v):
  13 May is an exit problem, 30 Mar / 2 Apr are not.

Two sensitivity notes, neither of which changes any verdict:

- **19 Aug at m=0.5 is an exact-equality hit:** the 0.5×
  level is 24,065.10 and the entry bar's low is exactly
  24,065.10, so the engine books the target (+₹1,090).
  If that equality were missed, 19 Aug would instead stop
  and re-enter for its (lA) day net (+₹1,670), Cluster 1
  total at m=0.5 would be +₹4,810 (not +₹4,230) and
  combined +₹25,295 (not +₹24,715) — still 1/3 on the
  failing set and still ₹55,365 below (lA). The verdict
  does not hinge on the equality.
- **8 Jul at m=0.5** is the mirror image: the morning
  targets early (+₹932.50) instead of stopping and
  re-entering (+₹955), a ₹22.50 difference on a day that
  stays green either way. A shorter target does not
  create value here; it merely replaces a working
  re-entry with an early exit of the same size.

### Winners under the multiples — value, not count

| Variant | Winners traded green | Winner total | vs (lA) +₹83,380 | Largest single winner tax |
|---|---|---|---|---|
| (lA) | 12/12 | +₹83,380 | — | — |
| W-T0.5 | 12/12 | +₹20,485 | −₹62,895 (−75.4%) | 8 Oct: +₹11,690 → +₹2,892.50 |
| W-T1.0 | 12/12 | +₹41,450 | −₹41,930 (−50.3%) | 8 Oct: +₹11,690 → +₹5,825 |
| W-T1.5 | 12/12 | +₹62,415 | −₹20,965 (−25.1%) | 8 Oct: +₹11,690 → +₹8,757.50 |

No winner flips to a loss and no winner becomes a no-trade,
because every (lA) winner morning targets and a nearer target
is reached no later. The damage is purely in value, and it is
proportional to the multiple by construction (a target at
m×risk pays m/2 of the 2× target profit, minus the same
₹40 cost) — which is why no multiple can escape it: the
multiple that converts 13 May (m ≤ 1.0) is exactly the
multiple that quarters or halves every winner, and the
multiple that preserves most winner value (m=1.5) converts
nothing. This is the same structural trade-off as the
partials, in full-size form, and it fails for the same
reason: one conversion cannot pay for twelve taxed winners.

### Secondary check — W-T0.5 on the OOS window (not a pass claim)

Because W-T0.5 is the most aggressive multiple (its
conversion set bounds the m=1.0/m=1.5 conversion sets from
above: any morning that reaches a 1.0× level before its stop
also reaches the 0.5× level first, under the same
stop-before-target order), it was run on the 92-day OOS
window as a secondary check. The result is disclosed in
full precisely because it must not be quoted in half:

| Window | (lA) | W-T0.5 | Difference |
|---|---|---|---|
| OOS traded / no-trade | 74 / 18 | 74 / 18 (identical days) | — |
| OOS green / traded | 39 / 74 (52.7%) | 60 / 74 (81.1%) | +21 greens |
| OOS total | +₹35,570 | +₹38,865 | **+₹3,295** |
| (lA)-loser total (35 days) | −₹149,250 | −₹15,222.50 | +₹134,027.50 saved |
| (lA)-loser conversion | — | 21 / 35 = **60.0% exactly** | — |
| (lA)-winner total (39 days) | +₹184,820 | +₹54,087.50 | **−₹130,732.50 (−70.7%)** |
| (lA)-winner green count | 39 / 39 | 39 / 39 | count preserved, value collapsed |

**W-T0.5 is NOT reported as an OOS pass, for three stated
reasons, any one of which blocks adoption:**

1. **In-sample contradiction.** The same variant fails the
   combined leg in-sample by ₹55,945 and converts only 1/3
   of the in-sample failing set. A variant that passes one
   window and fails the other by that margin, with the
   failing set still negative in-sample (30 Mar + 2 Apr =
   −₹5,785), is not a coherent rule — it is a window
   artefact, and prior discipline (p)/(q) forbids adopting
   an in-sample failure on an OOS total alone.
2. **The OOS margin is a wash.** +₹3,295 on 74 traded days
   is less than one typical winner trade (largest OOS
   winner tax alone is −₹11,797.50, on 2025-02-14) and is
   the net of a ₹134,027.50 loser saving and a
   ₹130,732.50 winner tax. A gain bought by shrinking
   winning trades by 70.7% in value is not positive
   economics under the task's discipline, even when the
   winner *count* (39/39) is preserved.
3. **The conversion leg is exactly at the bar, not above
   it.** 21/35 = 60.0% meets a ≥60% reading by zero margin;
   one fewer conversion (20/35 = 57.1%) would fail it.
   Combined with (1) and (2), an exactly-at-bar leg on a
   wash total is not a scoped pass.

OOS W-T1.0 / W-T1.5 were not run: both already fail the
failing-set leg (1/3 and 0/3) and the combined leg
in-sample, and their conversion sets are bounded above by
W-T0.5's, so an OOS run would be hunting for a window in
which a failed in-sample variant looks better, not a
validation of a passing one. The 21 OOS conversions under
W-T0.5 are listed in `w_sweep_raw.json` (OOS section);
the 14 (lA)-loser days that still lose under W-T0.5, and
the 37 changed winner days, are the complement in the same
file. No OOS number in this section is carried into a
whole-month run or into November paper.

**Part 1 verdict: the target-multiple family is exhausted.**
m=0.5 and m=1.0 convert only 13 May, m=1.5 converts nothing,
and every multiple taxes winners in proportion to its
conversion power. The untouched days (30 Mar, 2 Apr) are
target-multiple-proof for the reasons in the day table:
stop-first on the entry bar, and (for 2 Apr) no favourable
excursion at all before the stop.

## Part 2 — Re-entry timing variant: cooling delay after the morning stop

### Definition, and the table that must come first

**W-RK:** morning = (lA) exactly. After a morning stop,
re-entry candidates whose signal-bar index is ≤
stop_idx + K are skipped; thereafter the (lA) scan runs
unchanged (morning-phase scan-skip, afternoon first
band-fail ends the scan, band [10, rescan risk], window
to 15:05). K = 2 and K = 7 are tested. This is a *timing*
variant in the task's sense: it changes *when* the
re-entry scan may first trade, not the trigger (close <
OR low), not the band, and not the morning. It is not a
bounce-persistence guard (U1/U2 are not re-run, and no
guard conditions on preceding closes are added), not a
band widening (rB, already failed), and not a second
re-entry (rF, already failed — and, under (lA) logic, a
second re-entry is in any case inert on Cluster 1: the
only (lA) re-entry that stops is 2 Apr's, after which
(r) proved no bar ever closes below the OR low again).

The task requires the working-re-entry table *before* any
claim about 30 Mar / 2 Apr. Here it is, for both K values:

| Working (lA) re-entry day | (lA) re-entry → day net | W-RK2 → day net | W-RK7 → day net |
|---|---|---|---|
| 2026-06-29 | 11:30, risk 34.40 → target +₹6,840 → **+₹2,100** | **Identical: 11:30 +₹6,840 → +₹2,100** | **Identical: 11:30 +₹6,840 → +₹2,100** |
| 2026-07-08 | 12:05, risk 14.90 → target +₹2,940 → **+₹955** | **Identical: 12:05 +₹2,940 → +₹955** | **Identical: 12:05 +₹2,940 → +₹955** |
| 2026-08-19 | 10:15, risk 20.05 → target +₹3,970 → **+₹1,670** | **Identical: 10:15 +₹3,970 → +₹1,670** | **DELETED: no re-entry → −₹2,300** |

Note the correction to the brief's shorthand: under the
(lA) engine, 8 Jul's working re-entry is an *afternoon*
12:05 trade (its 10:20 morning candidate fails the band
at risk 27.00 > rescan risk 19.45 and is scan-skipped),
not a 10:20 trade — the 10:20 figure in (u) is the
guard-skipped candidate, not the traded re-entry. Any
afternoon-only re-entry change must therefore preserve
12:05 on 8 Jul, and both RK variants do (RK2 and RK7
leave 8 Jul untouched because its signal is far after
the morning stop). RK7's failure is on 19 Aug, not 8 Jul:
its 10:15 signal is only 5 bars after the 09:50 stop
bar, so a 7-bar cooling delay skips it, and no later
band-passing candidate replaces it — the day falls from
+₹1,670 to −₹2,300, a −₹3,970 swing that is the whole
reason RK7 is disqualified as a fix, before 30 Mar /
2 Apr are even considered.

### Results — Cluster 1 (8), winners unchanged in both variants

| Variant | Cluster 1 green / no-trade / total | 30 Mar day | 2 Apr day | Winners | Combined | vs (lA) +₹80,660 |
|---|---|---|---|---|---|---|
| (lA) reference | 5/8 / 0 / −₹2,720 | −₹2,055 (no re) | −₹3,730 (re 11:25 −₹1,665) | 12/14 / +₹83,380 | +₹80,660 | — |
| **W-RK2** | 4/8 / 0 / −₹6,740 | −₹2,055 (unchanged) | −₹3,730 (unchanged) | 12/14 / +₹83,380 | +₹76,640 | −₹4,020 |
| **W-RK7** | 3/8 / 0 / −₹7,955 | −₹2,055 (unchanged) | −₹2,065 (avoidance only) | 12/14 / +₹83,380 | +₹75,425 | −₹5,235 |

Winners are structurally unchanged in both variants (no
(lA) winner morning stops, so no re-entry scan ever runs
for them) — winner invariance here is a property of (lA),
not a result of the variants, and is stated as such.

- **W-RK2 passes the working-three table and still fails
  as a fix.** All three required re-entries are identical
  to (lA), 30 Mar is unchanged (its 11:45 afternoon
  candidate is 3 bars after the stop, so K=2 does not
  skip it, and (lA)'s afternoon first-fail still ends the
  scan there) and 2 Apr is unchanged (its 11:25 signal is
  7 bars after the stop, so K=2 does not skip it).
  Failing-set conversion: **0/3**. The only Cluster 1
  change is a *different* green day, 6 Feb: its working
  10:20 re-entry is 1 bar after its 10:15 stop, so K=2
  skips it, and the next candidate (10:45) stops for
  −₹1,090, flipping the day from +₹1,120 to −₹2,900.
  A cooling delay that preserves the three named trades
  but deletes the next-earliest working trade (6 Feb,
  1 bar after its stop) is not a fix — it is a reminder
  that working re-entries occur at every delay from 1
  bar (6 Feb) to 28 bars (8 Jul), so no cooling delay
  can separate failing re-entries from working ones by
  delay alone.
- **W-RK7 fails the working-three table and is therefore
  disqualified before its failing-day numbers are read.**
  It deletes 19 Aug (above) and 6 Feb (its 10:20 signal
  is within 7 bars of its stop; no replacement trades),
  and it improves 2 Apr only by avoidance (−₹3,730 →
  −₹2,065, the losing re-entry skipped, no replacement,
  day still a loss). Failing-set conversion: **0/3**
  (30 Mar unchanged, 2 Apr still a loss, 13 May has no
  re-entry under any variant). Cluster 1 falls to 3/8,
  −₹7,955.
- **Cooling-delay conclusion:** the delay axis is
  exhausted at both ends. A short delay (K=2) changes
  nothing on the failing days and costs a working trade
  elsewhere; a long delay (K=7) deletes a required
  working trade. There is no K in between that helps:
  2 Apr's signal is 7 bars after its stop and 19 Aug's
  is 5 bars after its stop, so any K ≥ 7 that skips
  2 Apr necessarily skips 19 Aug first, and any K ≤ 5
  that preserves 19 Aug also preserves 2 Apr. The
  ordering is the proof, not a threshold to tune.

**Part 2 verdict: no re-entry timing variant in (w) converts
30 Mar or 2 Apr.** RK2 is the only variant that survives
the working-three table, and it converts 0/3 while costing
6 Feb. RK7 does not survive the table. The (lA) re-entry
rule remains the best re-entry rule tested, and it is
still not adopted.

## Part 3 — Ordering diagnostic: target-before-stop (NOT a candidate)

**W-ORD:** identical to (lA) except that, on any bar whose
low reaches the target *and* whose high reaches the stop,
the exit is the target instead of the stop — applied to
both the morning and the re-entry replay. This is
**diagnostic only**: on 5-min bars the intra-bar order is
unobserved, so a target-first rule cannot be executed
from this data and is not proposed as a live rule, at
any multiple.

| Set | (lA) | W-ORD diagnostic | Differing days |
|---|---|---|---|
| Cluster 1 (8) | 5/8, −₹2,720 | 5/8, −₹2,720 | **0** |
| Winners (14) | 12/14, 2 no-trade, +₹83,380 | 12/14, 2 no-trade, +₹83,380 | **0** |
| Combined | +₹80,660 | +₹80,660 | **0** |

W-ORD is byte-identical to (lA) on every Cluster 1 and
winner day, morning and re-entry alike. That closes the
ordering question on this data: **no bar in any Cluster 1
or winner trade ever hits both its stop and its target
before its exit bar** — the entry-bar stops on 30 Mar /
2 Apr, for example, have lows 10.75 / 5.60 points below
entry against 2× targets 40.30 / 40.50 points below
entry, so target-first ordering cannot rescue them
either. The failures are price-path failures, not
ordering-assumption failures. Do not re-propose an
ordering flip as a fix without 1-min (or finer) data
showing a bar that actually hits both levels — and even
then, the flip would need to survive the same pass bar,
not merely change one day's exit label.

## Part 4 — Cluster 2: forward logging format only, no rule, no result

Per the task and per (u)/(v), no new Cluster 2 entry/exit
rule is proposed, tested, or claimed in (w). Cluster 2
remains recorded as unfixable on the available 6-trade
sample. The only (w) output for Cluster 2 is this logging
format, for forward paper trades as they accumulate
(paper only, no re-fitting on the paper month):

| Field | What to record |
|---|---|
| date | Trade date |
| signal | Reclaim signal time, and the (s)-format scan that produced it |
| L | max(OR high, previous close), frozen at signal time |
| entry / stop / risk / target | Frozen entry, stop, risk and target from the original trade |
| exit / net | Actual paper exit (time, reason, net at 100 shares, ₹40/trade) |
| original_would_have_done | What the original (unmodified) trade would have done on the same day, for comparison |
| notes | Post-signal path only as observation (first close/low below L, MFE) — not a fitted rule |

No forward reclaim trade is claimed in this report: no new
reclaim trade was accumulated or evaluated as part of (w),
and no date is listed here, because listing one would
invent it.

## Verdict — family (w) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| 1 — Target multiple, in-sample | W-T1.0 | Cluster 1 6/8, +₹7,350, but failing set 1/3; combined +₹48,800, ₹31,860 below (lA) | No — failing-set and combined both fail |
| 1 — Target multiple, in-sample | W-T0.5 | Cluster 1 6/8, +₹4,230, failing set 1/3; combined +₹24,715, ₹55,945 below (lA) | No |
| 1 — Target multiple, OOS (secondary, W-T0.5 only) | W-T0.5 OOS | 60/74 green, loser conversion exactly 60.0% (21/35), total +₹38,865 (+₹3,295 vs (lA)), but winner value −70.7% and in-sample fails by ₹55,945 | No — wash, not a pass (see §1 reasons 1–3) |
| 1 — Target multiple | W-T1.5 | Cluster 1 identical to (lA); winners −₹20,965 | No — pure winner tax |
| 2 — Re-entry cooling | W-RK2 | Working three identical; failing set 0/3; Cluster 1 4/8, −₹6,740 (6 Feb flipped) | No — survives the table, fixes nothing |
| 2 — Re-entry cooling | W-RK7 | Deletes 19 Aug; Cluster 1 3/8, −₹7,955; failing set 0/3 | No — fails the working-three table |
| 3 — Ordering diagnostic | W-ORD | Byte-identical to (lA) on all 22 days | Not a candidate — ordering is not the issue |
| 4 — Cluster 2 | Logging format only | No rule, no result claimed | — |

- **No (w) variant passes** the full bar (60% green on the
  failing set AND total positive AND combined NOT below
  (lA), winners not collapsed) as a genuine conversion fix,
  on either window. The closest variant, W-T0.5, passes
  the Cluster 1 total leg in-sample and reaches exactly
  60.0% loser conversion OOS, but it fails the failing-set
  leg in-sample (1/3), fails the combined leg in-sample
  by ₹55,945, collapses winner value by 70–75% on both
  windows, and wins OOS by only ₹3,295 — a wash, disclosed
  in full above, not hidden and not adopted.
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is
  not adopted. Cluster 3 survival N=10 (k=0.9, prior
  sweep) remains the best scoped result for Cluster 3
  only, combined below baseline. November paper is NOT
  frozen for any (w) variant. No (w) in-sample result is
  carried into a whole-month run on the same Jan–Oct data.
- **Dead, do not re-propose without new evidence:** pure
  target multiples as a Cluster 1 fix (m=0.5/1.0 convert
  only 13 May, m=1.5 converts nothing, every multiple
  taxes winners in proportion); re-entry cooling delays
  (short delays cost 6 Feb and fix nothing, long delays
  delete 19 Aug — the 5-bar vs 7-bar ordering proves no
  delay separates 2 Apr from 19 Aug); target-first
  intra-bar ordering on 5-min data (byte-identical to
  (lA), no bar hits both levels); any further partial
  shape (v); bounce-persistence guards U1/U2 (u); any
  Cluster 2 entry/exit rule on the 6-trade sample.

## Next family — the task continues, not completed

Family (w) closes the last simple morning-exit axis (the
target multiple) and the cooling-delay re-entry axis on
this data. What remains open is not another 5-min exit,
stop, filter or timing parameter — those families are now
exhausted in every shape tested — but a change of scope
or of data, which needs a parent decision before it is
run, not a silent re-run here:

1. **Finer resolution for the entry-bar stop.** The
   untouched days stop inside their entry bar on 5-min
   data, so every 5-min rule that acts *after* that bar
   is too late by construction. A 1-min replay would test
   whether the entry-bar stop is truly immediate or an
   artefact of 5-min aggregation — but it is a new data
   build, not a new parameter, and its result must pass
   the same bar before any claim is made from it.
2. **A direction-flip system after two PE stops, as a
   different system.** (r) proved 2 Apr rises all
   afternoon after its second stop (no close below the
   OR low again, close 22760.40 at 15:10). A CE flip
   after two PE stops would be a new system, not a PE
   fix, and must not be presented as a Cluster 1
   conversion without that scope change being approved.
3. **Cluster 2 / Cluster 3: forward paper only** (§4 and
   the prior scoped Cluster 3 result), until new trades
   accumulate. No entry/exit family until then.

Files: engine `w_sweep.py`, raw replay `w_sweep_raw.json`,
this report `nifty_cluster1_w_sweep.md`. Paper only
throughout; no orders placed, nothing fabricated. The
long-horizon task continues in the parent conversation:
family (w) is exhausted, none is adopted, and the next
decision is a scope/data decision in (1)–(3) above — not
a whole-month run of any (w) variant on the same Jan–Oct
data.
