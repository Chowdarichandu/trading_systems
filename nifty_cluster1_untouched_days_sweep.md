# NIFTY — Family (r): the two untouched Cluster 1 days + Clusters 2/3 on their own terms — NO PASS, nothing adopted
## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (q) failed out-of-sample for all three (p) variants, so (p) joins
(o) as in-sample only. Previous best kept is still (lA) on Cluster 1
economics (−₹2,720, 5/8 day-green) with winners intact, and (lA) itself
is NOT adopted. November paper is NOT frozen for (p) or for any (r)
variant below.

(r) returns, as instructed, to the two Cluster 1 days untouched in every
(o) and (p) variant — 30 Mar and 2 Apr, no partial, re-entry unchanged —
and to Clusters 2/3 on their own terms, WITHOUT claiming Cluster 1 is
fixed and WITHOUT re-running (p) cutoffs on a new window to hunt a pass.

Pass bar, same as (p)/(q): **60% green AND total positive AND combined
NOT below (lA) on the same window, winners not collapsed.** Green =
net > ₹0. No-trade is counted separately from green throughout — a
no-trade is never a green, and a total improved only by avoiding trades
is reported as avoidance, not conversion. 100 shares equivalent,
₹40/trade, square-off 15:10, stop checked before target on each bar.

Engine: `r_untouched_sweep.py`, raw replay
`r_untouched_sweep_raw.json`, replayed bar by bar from the Upstox 5-min
cache. (lA) baseline below is reproduced by that engine from
`extended_window_sweep.day_variant("lA")`, not copied from (p): Cluster 1
5/8, −₹2,720; winners 12/14 green, 2 no-trade, +₹83,380; combined
+₹80,660 — identical to (p)'s (lA) reference.

## Part A — the two untouched days: what actually happened

### Correction to the brief's premise, stated plainly

The brief asked "why does no bar close below OR low after the stop?"
For 2 Apr that is true after the second stop (see below). For 30 Mar
it is NOT true in the afternoon sense, and the report must not repeat
it: **after 30 Mar's 11:30 stop, 20 bars close below the OR low**
(22470.15), from 11:45 through 15:20. What fails on 30 Mar is not the
absence of closes below the OR low — it is (lA)'s afternoon rule:
the FIRST afternoon candidate, 11:45 (close 22464.55, candidate risk
20.65 vs rescan risk 20.15), fails the band [10, 20.15] by 0.50 points,
and (lA)'s stop-on-first-fail ends the scan there. The day is therefore
left at its morning loss, −₹2,055, not because the afternoon offered
nothing, but because (lA) deliberately refuses the first afternoon
candidate and stops looking.

### 30 Mar 2026 — afternoon price action

- (lA) morning (BN-confirmed rescan): signal 11:25, close 22468.20
  (1.95 points below OR low 22470.15, 336.35 below previous-day low),
  entry 11:30 open 22468.10, stop 22488.25 (signal high), risk 20.15.
  The entry bar itself, 11:30, highs at 22506.30 and stops the trade:
  **1 bar to stop, MFE 0.00, net −₹2,055.** The signal bar is
  immediately reversed in its entry bar, with zero favourable excursion.
- After the stop the day whipsaws: 22420–22594 until about 14:00,
  then breaks down to a new day low of 22283.85 at 15:00 and closes
  22335.60 at 15:10. The late breakdown is real, but every
  band-passing afternoon re-entry candidate stops (see variants):
  13:55 (−₹1,390), 14:15 (−₹1,340), 14:25 (−₹1,825). The 14:20 bar
  that looks like a late-breakdown entry in hindsight is itself the
  stop bar for the 14:15 candidate (high 22431.85 vs stop 22425.35).
- Afternoon candidates (close < OR low, candidate = next open,
  stop = candidate-bar high, band = [10, rescan risk 20.15]):
  11:45 risk 20.65 band-FAIL (by 0.50); 13:40 risk 39.35 fail;
  13:45 risk 22.60 fail; 13:50 risk 31.95 fail; **13:55 risk 13.50
  pass, stops −₹1,390** (this is the (k) scan-skip result);
  14:00 risk 26.00 fail; 14:05 risk 26.80 fail; 14:10 risk 31.70
  fail; **14:15 risk 13.00 pass, stops −₹1,340**; 14:20 risk 45.85
  fail; **14:25 risk 17.85 pass, stops −₹1,825**; 14:35 risk 15.05
  pass; 14:40 risk 18.30 pass (both untested in isolation because
  the scan stops at the first traded re-entry in every variant
  except rF, and rF's second re-entry already stops at 14:15).

### 2 Apr 2026 — a different shape, not a second 30 Mar

- Original Skill morning: signal 09:55, close 22206.50 (2.65 below
  OR low 22209.15), entry 10:00 open 22206.80, stop 22227.55, risk
  20.75, stop in the entry bar 10:00: **1 bar, MFE 0.00, −₹2,115.**
  The stop-sweep re-entry at 10:05 (close below OR low) also stopped
  (−₹2,950 in that sweep's original-trade framing).
- (lA) morning is different and later: BN confirmation gates the
  signal to 10:45 (close 22206.35, 2.80 below OR low), entry 10:50
  open 22204.85, stop 22225.10, risk 20.25, stop in the entry bar
  10:50: **again 1 bar, MFE 0.00, −₹2,065.** (lA) re-entry at 11:25
  (close 22207.60 < OR low, risk 16.25, in band) also stops in its
  entry bar 11:30: −₹1,665. Day under (lA): **−₹3,730.**
- After that second stop at 11:30, **no bar ever closes below the
  OR low again, and no bar's low even touches it**: minimum close
  after 11:30 is 22223.15, minimum low 22218.30 (both above OR low
  22209.15), and the day rises all afternoon to close 22760.40 at
  15:10 — about 550 points above the morning low. This is a
  trend-reversal day, not a whipsaw day: any PE re-entry trigger
  based on a close (or even a wick) below the OR low can never
  fire after 11:30. A direction flip after two PE stops would be a
  different system, not a PE fix, and is NOT tested here as one.

### Shape recurrence — the 1-bar / 0-MFE shape is exactly these two days

Under both the original trades and the (lA) mornings, the shape
"signal bar reversed in its entry bar, zero favourable excursion"
occurs on exactly 2 of the 8 Cluster 1 days: 30 Mar and 2 Apr.
No other Cluster 1 day has MFE 0 or a 1-bar stop (next smallest
MFE in Cluster 1 is 9 Jan at 23.9% of target, 2 bars). The same
shape appears in a different cluster — Cluster 4's 8 Jun CE trade
(1 bar, MFE 0) — which is noted, not mixed into Cluster 1.
So the untouched days are not a random pair: they are the only
two Cluster 1 days whose morning trade never gets going at all.

## Part A — re-entry trigger variants, one at a time, on (lA) mornings

All variants replace ONLY the re-entry scan after an (lA) morning
stop; the morning itself is unchanged. Winners are structurally
unchanged in every Part A variant (12/14 green, 2 no-trade,
+₹83,380): no (lA) winner morning stops, so no re-entry ever runs
for them — winner invariance here is a property of (lA), not a
result of the variants. The test is therefore on Cluster 1
(8 days) against the (lA) combined +₹80,660.

| Variant (re-entry trigger, scan-skip over band fails unless stated) | Cluster 1 green / no-trade / total | 30 Mar day | 2 Apr day | Combined (C1 + winners) | Pass? |
|---|---|---|---|---|---|
| (lA) reference: close < OR low, band [10, rescan risk], stop-on-first-fail (afternoon) | 5/8 / 0 / −₹2,720 | −₹2,055 (no re-entry) | −₹3,730 (re 11:25, −₹1,665) | +₹80,660 | — (reference, total negative) |
| **rB — band widened to [10, 1.5× rescan risk]** | 4/8 / 0 / −₹10,505 | −₹4,160 (re 11:45, −₹2,105) | −₹3,730 (unchanged) | +₹72,875 | No — worse than (lA) on every leg |
| **rC — close < morning signal low, band [10, rescan risk]** | 0/8 / 0 / −₹26,590 | −₹3,445 (re 13:55, −₹1,390) | −₹2,065 (no re-entry) | +₹56,790 | No — destroys all five (lA) day-greens |
| **rD — close < morning entry, band [10, rescan risk]** | 2/8 / 0 / −₹12,900 | −₹3,445 (re 13:55, −₹1,390) | −₹2,065 (no re-entry) | +₹70,480 | No |
| **rE — close < running intraday low, band [10, rescan risk]** | 1/8 / 0 / −₹16,980 | −₹3,395 (re 14:15, −₹1,340) | −₹2,065 (no re-entry) | +₹66,400 | No |
| **rF — two re-entries allowed, close < OR low, band [10, rescan risk]** | 4/8 / 0 / −₹4,760 | −₹4,785 (re 13:55 −₹1,390, re 14:15 −₹1,340) | −₹3,730 (unchanged) | +₹78,620 | No — closest in Part A, still below (lA) by ₹2,040, Cluster 1 total negative |
| **rH — afternoon-only (≥13:00), close < OR low, band** | 1/8 / 0 / −₹27,100 | −₹3,445 (re 13:55, −₹1,390) | −₹2,065 (no re-entry) | +₹56,280 | No |
| **rI banded — two consecutive closes < OR low, band** | 2/8 / 0 / −₹12,380 | −₹3,445 (re 13:55, −₹1,390) | −₹2,065 (no re-entry) | +₹71,000 | No |
| **rI unbanded — two consecutive closes < OR low, first pair traded** | 2/8 / 0 / −₹15,855 | −₹4,355 (re 13:45, −₹2,300) | −₹2,065 (no re-entry) | +₹67,525 | No |

Reading, variant by variant:

- **rB** is the direct answer to 30 Mar's 0.50-point band fail:
  widening the band lets the 11:45 candidate trade — and it stops
  for −₹2,105, making 30 Mar worse (−₹4,160) and 8 Jul flip from
  +₹955 to −₹4,725. The band was not the problem; the candidate
  was a loser at any band width that admits it.
- **rC** is the worst variant in (r): replacing (lA)'s OR-low
  trigger with the signal-low trigger fires at different, worse
  bars and turns every (lA) day-green into a loss (9 Jan
  +₹2,295 → −₹4,890; 29 Jun +₹2,100 → −₹130; 8 Jul +₹955 →
  −₹3,250; 19 Aug +₹1,670 → −₹4,355). It improves 2 Apr only by
  removing (lA)'s bad re-entry (−₹3,730 → −₹2,065), which every
  non-OR-low variant does — avoidance of one bad re-entry, bought
  by destroying five good ones. (lA)'s OR-low trigger is better
  than the signal-low trigger, and that is now a measured result,
  not an assumption.
- **rD, rE, rH, rI** all share the same pattern: they improve
  2 Apr to −₹2,065 (no re-entry fires) and worsen 30 Mar to about
  −₹3,400 (one stopping re-entry), while losing (lA) greens
  elsewhere. None converts either untouched day to green.
- **rF (two re-entries)** is the closest Part A variant and the
  only one worth naming as "best in Part A": it improves 9 Jan
  (+₹2,295 → +₹4,615) and 8 Jul (+₹955 → +₹4,085), but it
  worsens 30 Mar to −₹4,785, flips 19 Aug to −₹385, and
  shrinks 6 Feb (+₹1,120 → +₹30) and 29 Jun (+₹2,100 →
  +₹485), leaving Cluster 1 at 4/8 green and −₹4,760. A third re-entry was also
  checked for 30 Mar (not a headline variant): 13:55 −₹1,390,
  14:15 −₹1,340, 14:25 −₹1,825, day −₹6,610 — worse again.
  More re-entries do not fix 30 Mar; each additional re-entry
  is another stop on that day.
- **Already-tried check, closed not re-claimed:** an OR-high
  morning stop (stop family Y2) was already tested on plain
  mornings (4/8 green, total −₹31,910, risks 87–188 points) and
  is NOT an (r) variant. On the two untouched days it would
  green 30 Mar only by taking 149.95 points of risk (square-off
  +₹13,210 on a 7.4× risk) and lose −₹19,020 on 2 Apr (stop hit
  at 13:00 as price rises through the OR high) — combined
  negative, and a risk explosion, not a fix. It stays rejected.

**Part A verdict: no re-entry trigger converts 30 Mar or 2 Apr.**
30 Mar's afternoon offers only stopping re-entries at every
band-passing candidate; 2 Apr's afternoon offers no re-entry
trigger at all after 11:30. The untouched days are unfixable by
re-entry, in either trigger definition tested here.

## Part B — Cluster 2 on its own terms: reclaim confirmation

Reclaim definition, from the engine (`daytrader_cash_backtest.
find_signal`, setup4_reclaim): day open below previous close,
signal close above BOTH the OR high and the previous close, and
below the previous-day high, with room ≥ 200×scale to the next
level above. The reclaimed level L used here is therefore
max(OR high, previous close) — a data-visible level, not an
outcome-fitted one. No volume series exists in the 5-min cache,
so "volume confirmation" cannot be tested from this data and is
not claimed; confirmation here is close-based only, as defined
below. Original Cluster 2 trades are replayed directly (not
through (lA) rescan, which is a PE construct).

| Date | Signal close / L / above L | Original (entry, stop, risk, net) |
|---|---|---|
| 2026-01-14 | 25747.00 / 25744.80 / +2.20 | 25747.75, 25720.30, 27.45, −₹2,785 |
| 2026-10-26 | 22636.45 / 22600.00 / +36.45 | 22635.70, 22549.75, 85.95, −₹8,635 |
| 2026-07-01 (only other setup4_reclaim CE trade, a winner — the winner check) | 23940.05 / 23934.90 / +5.15 | 23938.80, 23917.40, 21.40, +₹4,240 |

**Thin-reclaim warning that must travel with any confirmation
rule:** signal close above L is 2.20 (a loser), 5.15 (a winner)
and 36.45 (a loser). Distance above the reclaimed level does
NOT separate losers from the winner — the winner is thinner
than the biggest loser. Any distance filter will therefore
kill the winner before it kills the big loser, as c2-B shows.

| Variant (entry = open after confirmation bar, stop = confirmation-bar low, target recomputed at 2× new risk) | Cluster 2 green / no-trade / total | 14 Jan | 26 Oct | 1 Jul winner (check) | Pass? |
|---|---|---|---|---|---|
| Original | 0/2 / 0 / −₹11,420 | −₹2,785 | −₹8,635 | +₹4,240 | — |
| **c2-A — second close above L (hold confirmation)** | 1/2 / 1 / **+₹3,510** | no-trade (2nd close 25737.50 < L) | **+₹3,510** (2nd close 22636.30 > L; entry 22636.55, stop 22618.80, risk 17.75, target 10:05) | +₹3,890 (preserved, −₹350 vs original) | **No — 50% green < 60%, despite positive total** |
| **c2-E — stronger hold: 2nd close above L AND above signal close** | 0/2 / 2 / ₹0 | no-trade | no-trade (2nd close 22636.30 < signal close 22636.45 by 0.15) | +₹3,890 (preserved) | No — avoidance only, 0 green |
| **c2-B10 / c2-B20 — signal close ≥ L + 10 / 20 points, else no-trade** | 0/2 / 1 / −₹8,635 | no-trade | original trade, −₹8,635 (unchanged) | no-trade (winner killed, +₹4,240 lost) | No — worst on the winner side |

Reading:

- **c2-A is the best variant in all of family (r), and it is
  still not a pass.** It converts the single largest Cluster 2
  loss (26 Oct −₹8,635 → +₹3,510, a +₹12,145 swing) with a
  much smaller, honestly recomputed risk (17.75 vs 85.95), turns
  14 Jan into a no-trade instead of a loss, and preserves the
  only reclaim winner (+₹3,890 vs +₹4,240). On the setup4 set
  as a whole (2 losers + 1 winner) it goes from −₹7,180 to
  +₹7,400, a +₹14,580 improvement. But the pass bar is 60%
  green on the failing set, and 1/2 is 50%: with only two
  failing trades, one conversion plus one avoidance cannot
  pass, and it must not be rounded up to a pass. It is a
  **scoped improvement, not a scoped pass** — and, like (p),
  it is in-sample (3 reclaim trades) and needs held-out
  reclaim trades before it is believed.
- **c2-E** shows how knife-edge the strong-hold version is:
  26 Oct's second close misses the signal close by 0.15 points
  and the whole variant collapses to avoidance (₹0, 0 green).
  It is reported so that a future "stronger confirmation"
  proposal is not mistaken for an improvement over c2-A.
- **c2-B** confirms the thin-reclaim warning in numbers: a
  distance filter keeps the big loser (36.45 above L) and
  removes both the small loser and the winner. Distance
  above the reclaim level is not a confirmation rule.

## Part C — Cluster 3 on its own terms: survival N, re-tested with winners

Cluster 3 is the slow PE give-back (13 Feb −₹3,750, 30 Apr
−₹3,165, 18 May −₹3,670; original total −₹10,585; MFE 48–83% of
target, stops at 35, 26 and 11 bars). The rule re-tested here is
the one already proven on its 3 days: partial 45% (0.9× risk,
50 shares) with the remaining 50 trailed to breakeven, booked
only if the trade is still open at gate N (interpretation B,
eligibility — if the partial level was already reached before
the gate, it books at the gate; this is the only survival
reading that preserved Cluster 3 in the survival sweep).
Baseline for this scope is the plain trades: Cluster 3
−₹10,585 + PE winners +₹91,270 = **+₹80,685**, winners 14/14
green. The survival reimplementation in this sweep reproduces
the survival sweep's known numbers exactly (N=10: Cluster 3
+₹4,589, winners +₹69,334; N=20: Cluster 3 −₹674, winners
+₹80,614, up to rounding), so the new N values below are on
the same engine. Partial greens are non-tiny throughout
(₹1,366–₹1,630 at 45%).

| Variant (partial 45% unless stated) | Cluster 3 green / total | Winners green / total | Cluster 3 + winners combined | vs baseline +₹80,685 | Pass? |
|---|---|---|---|---|---|
| Plain baseline | 0/3 / −₹10,585 | 14/14 / +₹91,270 | +₹80,685 | — | — |
| **Survival N=5** | 3/3 / +₹4,589.25 | 14/14 / +₹60,981.50 | +₹65,570.75 | −₹15,114.25 | No — combined below baseline |
| **Survival N=10** | 3/3 / +₹4,589.25 | 14/14 / +₹69,334.25 | +₹73,923.50 | −₹6,761.50 | No — combined below baseline (known result, reproduced) |
| **Survival N=15** | 2/3 / −₹674.25 | 14/14 / +₹77,709.75 | +₹77,035.50 | −₹3,649.50 | No — Cluster 3 total negative (18 May stops at 10:30, before its gate) |
| **Survival N=20** | 2/3 / −₹674.25 | 14/14 / +₹80,613.75 | +₹79,939.50 | −₹745.50 | No — Cluster 3 total negative, combined still below |
| **Survival N=25** | 2/3 / −₹674.25 | 14/14 / +₹80,613.75 | +₹79,939.50 | −₹745.50 | No — identical to N=20 on this data |
| **Survival N=30** | 1/3 / −₹5,205.50 | 14/14 / +₹87,488.75 | +₹82,283.25 | +₹1,598.25 | **No — combined passes only because winners are barely clipped, while Cluster 3 itself fails (1/3, negative). A combined pass bought by failing the cluster it was meant to fix is not a pass.** |
| **Survival N=10, partial 50% (1.0× risk)** | 2/3 / −₹452.50 | 14/14 / +₹70,472.50 | +₹70,020.00 | −₹10,665.00 | No — 13 Feb's MFE is 0.962× risk, below the 1.0× partial level, so it never books and stops −₹3,750 |

Reading:

- Survival N is a one-way trade-off, not a sweet spot:
  smaller N keeps Cluster 3 green (N=5 and N=10 both 3/3) but
  clips more winners; larger N restores winners but loses
  Cluster 3 (18 May stops before any gate ≥15; 30 Apr stops
  before gate 30). There is no N where Cluster 3 stays green
  AND the combined total reaches baseline — N=10 is the best
  compromise and it still falls ₹6,761.50 short.
- N=30 is the trap to name explicitly: it is the only
  survival variant whose combined total beats baseline, and
  it does so while Cluster 3 is 1/3 green and −₹5,205.50.
  Quoting its combined total without its Cluster 3 legs
  would be exactly the "combined total quoted while the
  failing set itself is still negative" error the task's
  discipline forbids.
- Partial 50% at N=10 fails for a knife-edge reason of its
  own: 13 Feb's favourable excursion is 0.962× risk, 3.8%
  short of the 1.0× partial level. 45% (0.9× risk) is the
  level already proven on Cluster 3, and 50% is worse here,
  not better.

**Part C verdict: survival gating remains the right shape
for Cluster 3 (wait for the trade to stay open, then protect
what it earned), and N=10 remains its best scoped result
(3/3, +₹4,589.25, non-tiny) — but it is not adoptable as a
scoped rule without a validated live discriminator, and no
survival N passes the full bar on Cluster 3 + winners
together.** The gap+below-prev-day-low box from the survival
sweep is still unvalidated and is not re-claimed here.

## Verdict — family (r) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| A — untouched days (re-entry triggers) | rF, two re-entries | Cluster 1 4/8, −₹4,760; combined +₹78,620 (below (lA) by ₹2,040); 30 Mar worsened to −₹4,785 | No |
| B — Cluster 2 (reclaim confirmation) | c2-A, second-close hold | Cluster 2 1/2 green, 1 no-trade, +₹3,510; reclaim winner preserved +₹3,890 | **No — 50% < 60%, despite positive total. Best scoped result in (r), not a pass.** |
| C — Cluster 3 (survival N) | Survival N=10 (45%) | Cluster 3 3/3, +₹4,589.25; winners 14/14, +₹69,334.25; combined +₹73,923.50, below baseline | No |

- **No (r) variant passes** the full bar (60% green AND total
  positive AND combined NOT below (lA), winners not collapsed).
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is not
  adopted. November paper is NOT frozen for any (r) variant.
- **No (p) cutoff was re-run** on a new window in this family,
  and no in-sample pass from (r) is carried into a
  whole-month run.

## Next family (s) — the task continues, not completed

(r) leaves two concrete leads, and the next family must test
them rather than re-running (r)'s triggers:

1. **Freeze c2-A and validate it on held-out reclaim trades.**
   Second-close hold is the only (r) variant that converts a
   failing trade to green without killing its cluster's winner,
   but it rests on 3 reclaim trades (2 losers + 1 winner) and
   a 1/2 green count. Its definition (entry = open after the
   second close above L, stop = second-bar low, target
   recomputed at 2× new risk) must be frozen and tested on
   reclaim trades it was not fitted on — a different year, or
   forward paper — before it is believed. If it fails there,
   it is discarded, not re-fitted to a stronger hold (c2-E
   already shows the stronger hold collapses on 0.15 points).
2. **Test a pure thin-signal no-trade rule for the untouched
   shape, as a no-trade — not as a scan to a later signal.**
   Both untouched days share one ex-ante feature no family
   has tested as a pure no-trade: the (lA) signal close sits
   within 3 points below the OR low (30 Mar: 1.95; 2 Apr
   (lA): 2.80; original 2 Apr: 2.65), with a narrow signal
   range (22.45 / 35.65 / 22.00 points). The distance family
   tested 10/20/30 points with scanning to later signals, not
   a <5-point pure no-trade, and its "greens" were later
   signals. (s) must apply the <5-point rule to Cluster 1 +
   winners together, count no-trades separately from greens,
   and report honestly whether it removes the two untouched
   losses at the cost of winners whose signals are equally
   thin — if it kills winners, it fails like c2-B did.
3. **Do not pursue for the untouched days:** a third or fourth
   re-entry (30 Mar worsens with each one: −₹4,785 at two,
   −₹6,610 at three), a wider band (rB worsens 30 Mar and
   8 Jul), a signal-low trigger (rC destroys all (lA)
   greens), or a direction flip on 2 Apr's reversal afternoon
   (a different system, not a PE fix).

Files: engine `r_untouched_sweep.py`, raw replay
`r_untouched_sweep_raw.json`, this report
`nifty_cluster1_untouched_days_sweep.md`. Paper only throughout;
no orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: family (r) is exhausted,
none is adopted, and the next decision is family (s) — frozen
validation of c2-A, and a pure thin-signal no-trade test —
not a whole-month run of any (r) variant on the same Jan–Oct
data.
