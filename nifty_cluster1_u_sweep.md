# NIFTY — Family (u): 23 Mar vs untouched pair + bounce-persistence guards + 13 May give-back validated OOS + Cluster 2 new axes — NO PASS, nothing adopted

## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (t) is done: no pass, nothing adopted. Previous best kept is
still (lA) on Cluster 1 (−₹2,720, 5/8 day-green) with winners intact,
and (lA) itself is **not** adopted. Cluster 3 survival N=10 (3/3,
+₹4,589.25) remains the best scoped result for Cluster 3 only,
combined below baseline.

Pass bar, same as (p)/(q)/(r)/(s)/(t): **60% green on the failing set
AND total positive AND combined NOT below (lA) on the same window,
winners not collapsed.** Green = net > ₹0. **No-trade is counted
separately from green throughout — a filter/guard can only avoid,
never convert, and a total improved only by avoiding trades is
reported as avoidance, not conversion.** 100 shares equivalent,
₹40/trade, square-off 15:10, stop checked before target on each bar
except where a variant states otherwise.

Engine: `u_sweep.py`, raw replay `u_sweep_raw.json`, replayed bar by
bar from the Upstox 5-min cache. (lA) baseline reproduced by the
engine, not copied: Cluster 1 5/8 green, −₹2,720; winners 12/14 green,
2 no-trade, +₹83,380; combined **+₹80,660**. OOS (lA) baseline also
reproduced: 74 traded / 18 no-trade, 39 green, 52.7%, **+₹35,570** —
identical to (q)'s (lA) OOS baseline, and G4 (p4 reference) reproduces
(q)'s p4 OOS numbers exactly (41 green, +₹47,952.50), so the new OOS
numbers below are on the same engine as (q), not a new engine. G1
reproduces (o1) in-sample exactly (Cluster 1 6/8, +₹4,832.50; winners
+₹46,075). Nothing fabricated. No (p) cutoff was re-run as a new
claim, no second-close hold variant was re-run, no (s)/(t) rule was
re-run on a new window to hunt a pass.

## Part 1 — What distinguishes 23 Mar from 30 Mar / 2 Apr? On the tested axes: nothing ex-ante

(lA) rescan mornings, Cluster 1 (8) + PE winners (14). Bounce = the
bars after entry (entry = open of the bar after the signal).

### The pair, side by side

| Axis | 2026-03-23 (winner, +₹7,260) | 2026-03-30 (untouched, −₹2,055) | 2026-04-02 (untouched, (lA) −₹3,730) |
|---|---|---|---|
| Signal | 09:50, skill mode | 11:25 | 10:45 (rescan; plain 09:55) |
| Gap % | −1.341 | −1.269 | −1.408 |
| Below-PDL (pts) | 438.55 | 336.35 | 412.25 |
| Signal range (pts) | 40.30 | 22.45 | 35.65 |
| Signal close vs prev close (pts below) | 505.6 | 371.3 | 496.8 |
| Prev-close position in prev-day range | 0.242 | 0.092 | 0.262 |
| BN gap % | −1.642 | −1.597 | −1.748 |
| BN day return % | −2.217 | −2.389 | +2.071 |
| BN close at signal vs BN OR low (pts) | −112.45 | −68.20 | −3.85 |
| Entry-bar close − entry (pts) | −31.05 | +35.70 | +21.75 |
| Entry-bar high − entry (pts) | +5.80 | +38.20 | +32.60 |
| Max high in first 3 bars after entry (pts) | +5.80 | +67.70 | +45.35 |
| First close ≥ entry | 14:00 (late, after target) | 11:30 (entry bar) | 10:50 (entry bar) |
| First close ≥ signal high | never | 11:30 (entry bar) | 10:50 (entry bar) |
| First close ≥ OR low | 14:00 (late) | 11:30 (entry bar) | 10:50 (entry bar) |

**Reading, stated plainly:** 23 Mar and 30 Mar share the deep-gap,
far-below-previous-low morning, the deep BN gap, and a down BN day
(−2.22% vs −2.39%). Their prev-close positions (0.242 vs 0.092) and
BN signal depths (−112 vs −68) differ in degree, not in kind, and
both sit inside the winner range on every one of those axes (e.g.
BN signal depth on winners runs from −413.75 to −0.40; prev-close
position from 0.000 to 0.577). 2 Apr is the only day of the three
whose BN day flips up (+2.07%) and whose BN signal depth is shallow
(−3.85) — but that separates 2 Apr alone, not 30 Mar, and BN day
return is known only at the close, so it is a diagnostic, not a
live filter.

**The one clean difference is post-trade information, not an entry
signal:** on the untouched days the entry bar itself closes above
the signal high and above the OR low, and the next bars keep closing
there (2 Apr: five consecutive closes above the signal high; 30 Mar:
entry bar and second bar both above it). On 23 Mar the entry bar
closes 31.05 points *below* entry, the first close above entry does
not arrive until 14:00, and the price never closes above the signal
high at all. The same pattern holds across the winner set: on 11 of
the 12 traded winners the entry-bar close is below entry (exceptions:
8 Oct, +20.15, still below its 58.65-point signal high; 19 Aug,
+3.15, below its signal high), and the first close above the signal
high is late (12:00–15:25) or never. But an entry-bar close above
the signal high **is** the stop — the trade has already stopped
intra-bar before that close is known. Post-entry bounce persistence
therefore cannot be an entry filter: at entry time, the only thing
known is that the signal bar closed below the OR low, which is true
of winners and untouched days alike.

**Part 1 verdict on axes: the untouched shape is unfilterable at
entry on every axis tested in (t) and (u)** — gap, below-PDL, OR
width, thinness, signal range, prev-close position, BN gap, BN
signal depth, BN day return. A future discriminator must first
explain what distinguishes 23 Mar from 30 Mar on some axis not in
this table, or it will repeat the (t)/(s) failure. The live use of
bounce persistence is not as an entry filter but as a re-entry
guard — and that is tested next, where it fails in the opposite
direction from the one the brief expected.

### Bounce-persistence re-entry guards — FAIL, catastrophically

Base: (lA) morning; if it stops, the (lA) re-entry scan runs with
one added guard. Band [10, rescan risk] and the afternoon first-fail
rule are kept; a guard-skip never ends the scan (only a guard-passing
afternoon candidate that fails the band ends it, as in (lA)).

- **U1:** skip a re-entry candidate if ANY of the 3 bars before it
  closed ≥ OR low.
- **U2:** skip a re-entry candidate unless the bar immediately
  before it also closed < OR low (two consecutive closes below OR
  low ending at the candidate).

| Variant | Cluster 1 green / total | Winners green / total | Combined | vs (lA) +₹80,660 | Pass? |
|---|---|---|---|---|---|
| (lA) reference | 5/8 / −₹2,720 | 12/14 / +₹83,380 | +₹80,660 | — | Reference, total negative |
| **U1** | 2/8 / **−₹17,445** | 12/14 / +₹83,380 | +₹66,935 | −₹13,725 | **No — catastrophic** |
| **U2** | 1/8 / **−₹18,355** | 12/14 / +₹83,380 | +₹65,025 | −₹15,635 | **No — catastrophic** |

Winners are untouched in both variants (no winner morning stops, so
the guard never runs there) — the entire damage is on Cluster 1,
and its mechanism is the opposite of the hypothesis:

- U1 deletes all three working (lA) re-entries: 29 Jun (+₹2,100 →
  −₹4,740, guard skips 11:30/11:40/11:45/11:50, then an afternoon
  first-fail ends the scan), 8 Jul (+₹955 → −₹1,985, guard skips
  10:20 and every afternoon candidate until a first-fail ends the
  scan), 19 Aug (+₹1,670 → −₹2,300, guard skips 10:10 and the scan
  then dies on band fails). 9 Jan keeps a green but a smaller one
  (+₹2,295 → +₹1,045, guard skips 10:50/10:55/11:00 and a later
  re-entry pays +₹4,790 instead of +₹2,930 on top of a −₹3,745
  morning). 6 Feb is unchanged (+₹1,120). 30 Mar worsens (−₹2,055
  → −₹3,445, a 13:55 stop the (lA) afternoon first-fail had blocked)
  and 2 Apr improves only by avoidance (−₹3,730 → −₹2,065, its
  11:25 re-entry skipped, no replacement).
- U2 is worse still: 6 Feb flips green → loss (+₹1,120 → −₹2,900,
  its working 10:20 re-entry is preceded by a bar that did not close
  below the OR low), 9 Jan flips green → loss (+₹2,295 → −₹1,205),
  29 Jun and 8 Jul lose their re-entries entirely. Only 19 Aug
  keeps its green (+₹1,670), and 2 Apr again improves only by
  avoidance (−₹2,065).

**Why the guard is backwards:** a working (lA) re-entry is, by
construction, the *first* close back below the OR low after a
bounce — so its preceding bars very often closed above the OR low.
A persistence guard therefore deletes exactly the working trades
and keeps only the trades whose bounce had already faded, which
are the ones that stop again (30 Mar's afternoon candidates, 2 Apr's
11:25 candidate is the exception that proves the avoidance point:
skipping it saves ₹1,665 and creates nothing). **Do not re-propose
a bounce-persistence / bounce-faded re-entry guard in either form
without explaining why it would not delete the 29 Jun, 8 Jul and
19 Aug re-entries again.** The (lA) re-entry rule — first band-passing
close below the OR low — remains the best re-entry rule tested, and
it is still not adopted.

## Part 2 — 13 May on its own terms: green rate passes OOS, economics fail on both windows

13 May, (lA) morning, verified: entry 23,337.30, stop 23,387.65, risk
50.35, target 23,236.60. Entry bar 09:35: high 23,339.35 (only 2.05
above entry — the stop is *not* threatened on the entry bar), low
23,262.55 (74.75 below entry = 1.48× risk), close 23,276.50. The trade
then gives back: 09:50 high 23,372.45, close above the OR low, and
the original stop is hit 09:55 for −₹5,075. This is a give-back
shape, not an entry-bar stop: the favourable excursion is large
(1.48× risk on the entry bar) and the reversal is slow (4 bars).
Every partial variant below therefore converts 13 May in-sample —
the question, as instructed, is whether it survives the OOS window,
not whether it converts 13 May.

Variants, defined before results (generic partial: partial at k×risk,
50 shares booked = 50×k×risk, remaining 50 trailed to BE or MID;
high-touch trails start next bar after the partial bar; close trails
may use the partial bar close; re-entry (lA scan) only if the morning
final exit is a stop):

| Variant | 13 May day net | Cluster 1 (in-sample) | Winners (in-sample) | Combined in-sample |
|---|---|---|---|---|
| (lA) reference | −₹5,075 | 5/8, −₹2,720 | 12/14, +₹83,380 | +₹80,660 |
| **G1 k=1.0, BE high, no cutoff** (= ungated o1 shape) | **+₹2,477.50** (partial 09:35, BE exit 09:50) | 6/8, +₹4,832.50 | 12/14, +₹46,075 | +₹50,907.50 |
| **G2 k=0.9, BE high, no cutoff** | **+₹2,225.75** | 6/8, +₹4,580.75 | 12/14, +₹43,978.50 | +₹48,559.25 |
| **G3 k=0.5, BE high, no cutoff** | **+₹1,218.75** | 6/8, +₹1,920 | 12/14, +₹31,102.50 | +₹33,022.50 |
| **G4 k=1.0, BE high, <10:00** (= p4, reference) | **+₹2,477.50** | 6/8, +₹4,832.50 | 12/14, +₹78,847.50 | +₹83,680 |
| **G5 k=1.0, MID close, no cutoff** | **+₹3,736.25** (mid-close exit 09:50) | 6/8, +₹6,091.25 | 12/14, +₹49,027.50 | +₹55,118.75 |

In-sample, every ungated variant fails the combined leg (G1/G2/G3/G5
all below (lA) +₹80,660, by ₹25,541–₹47,637) — the (o) lesson again:
a partial applied to every morning truncates runners by more than
it saves on give-backs. G4 is the only in-sample passer, and it
already failed OOS in (q).

### OOS window (92 days, 74 traded) — the decisive table

| Variant | Green / traded | Green rate | Total | vs (lA) OOS +₹35,570 | (lA)-losers converted | (lA)-winners total |
|---|---|---|---|---|---|---|
| (lA) baseline | 39 / 74 | 52.7% | +₹35,570 | — | — | +₹184,820 |
| **G1 k=1.0 BE** | 46 / 74 | **62.2%** | +₹14,690 | **−₹20,880** | 7 / 35 (20.0%) | +₹108,770 (−₹76,050) |
| **G2 k=0.9 BE** | 50 / 74 | **67.6%** | +₹24,230 | **−₹11,340** | 11 / 35 (31.4%) | +₹100,483 (−₹84,337) |
| **G3 k=0.5 BE** | 58 / 74 | **78.4%** | +₹23,990 | **−₹11,580** | 19 / 35 (54.3%) | +₹62,983.75 (−₹121,836.25) |
| **G4 p4 reference** | 41 / 74 | 55.4% | +₹47,952.50 | +₹12,382.50 | 2 / 35 (5.7%) | +₹178,422.50 (−₹6,397.50) |
| **G5 k=1.0 MID close** | 46 / 74 | **62.2%** | +₹23,547.50 | **−₹12,022.50** | 7 / 35 (20.0%) | +₹110,167.50 (−₹74,652.50) |

**This is the most important negative result in (u), and it must
not be quoted in half:** G1, G2, G3 and G5 all *pass* the green-rate
leg OOS (62–78%, above the 60% bar) and all *fail* the total leg
(₹11,340–₹20,880 below (lA)). G3 is the extreme case: it converts
19 of 35 (lA)-losers to green (54.3%, the highest conversion in
this family) and still loses ₹11,580 to (lA), because it taxes every
winner it touches — winner total falls ₹121,836, from +₹184,820 to
+₹62,983.75, while (lA)-loser total improves only from −₹149,250
to −₹38,993.75. A partial that fires on every morning converts
losers to *small* greens (G3 BE exits pay 25×risk − ₹40) and
truncates winners to *half* targets, and the winner tax is 1.1–1.5×
the loser saving in every ungated variant. G4 (time-gated) is the
mirror image: it preserves winners (−₹6,397.50) and its total beats
(lA), but it converts only 2/35 losers and its green rate is 55.4%
— it already failed (q) on that leg, and nothing here revives it.

**Part 2 verdict: no 13 May give-back variant passes.** 13 May is
convertible in-sample by any partial that triggers on its entry
bar, and no ungated partial survives OOS economics; no time-gated
partial survives OOS green rate. The trade-off is structural, not
a parameter choice: ungated partials buy green *count* with winner
*value*, and the pass bar requires both. 13 May therefore stays an
in-sample give-back example, not a validated exit rule. The one
shape not yet tested OOS is a *survival-gated* partial (partial
only if the trade is still open at gate N) — that is the next
family's lead, not a claim here, because survival gating was only
ever tested in-sample (Cluster 3 + winners) and its winner tax at
N=10 (−₹21,936 on the in-sample winner set) may or may not survive
the OOS window.

## Part 3 — Cluster 2 new axes: none separates, on both years together

Six reclaim trades (2026 fitted 3 + 2025 held-out 3, same scan as
(t)). Axes tested here for the first time: the reclaim's own
intraday path after the signal (first close below L, first low below
L, MFE before exit) and Bank Nifty's day trend (BN close vs open)
and BN's first close above its OR high after the signal. L = max(OR
high, previous close). Original nets: 2026 — 14 Jan −₹2,785, 1 Jul
+₹4,240, 26 Oct −₹8,635; 2025 — 20 Feb −₹1,215, 6 Jun +₹22,260,
1 Aug −₹2,310.

| Date | Outcome | First close < L | First low < L | MFE (pts) | BN day ret % | BN first close > BN ORH after signal |
|---|---|---|---|---|---|---|
| 2026-01-14 | −₹2,785 | 11:20 (entry bar) | 11:20 | 44.0 | +0.395 | 11:25 |
| 2026-07-01 | **+₹4,240** | never (before target) | 09:40 (entry bar) | 111.1 | +0.805 | 09:40 |
| 2026-10-26 | −₹8,635 | 10:35 (8 bars later) | 10:35 | 117.5 | +0.118 | 15:25 |
| 2025-02-20 | −₹1,215 | 13:55 (entry bar) | 13:55 | 6.55 | +0.058 | never |
| 2025-06-06 | **+₹22,260** | 10:10 (entry bar) | 10:10 | 235.8 | +1.565 | 10:20 |
| 2025-08-01 | −₹2,310 | 10:45 (3rd bar) | 10:40 | 5.2 | −0.547 | 10:35 |

**Every axis fails in both directions:**

- *First close below L:* the 6 Jun winner fails on its entry bar
  (10:10) and still runs to target; the 26 Oct loser holds above L
  for 8 bars and still stops. Immediate failure and immediate
  survival both occur in both outcomes.
- *First low below L:* the 1 Jul winner's low dips below L on its
  entry bar (09:40) and still targets; the 26 Oct loser holds its
  low above L until 10:35 and still stops. A low-touch rule (RETESTL
  in (t)) is therefore not rescued by this axis either.
- *MFE:* the 26 Oct loser reaches 117.5 points favourably — more
  than the 1 Jul winner's 111.1 — before stopping. Favourable
  excursion does not mark the winner.
- *BN day trend:* five of six days end BN-positive (both winners,
  three of four losers); only the 1 Aug loser ends negative. No
  separation.
- *BN first close above its OR high after the signal:* occurs
  early for a loser (14 Jan, 11:25) and a winner (1 Jul, 09:40),
  late for a loser (26 Oct, 15:25), early for a winner (6 Jun,
  10:20) and a loser (1 Aug, 10:35), and never for a loser (20 Feb).
  Every timing outcome occurs in both outcomes.

**Part 3 verdict: Cluster 2 is recorded as unfixable on the
available reclaim sample.** Across (r), (s) and (t) it has now
failed on: second-close hold (discarded OOS), stronger hold
(collapses on 0.15 points), distance filters, BN signal-bar
confirmation, time box, risk cap, risk sizing, stop-at-L, retest-of-L
(knife-edge only), and now post-signal path, MFE, BN day trend and
BN OR-high timing. With 6 trades across two years, no confirmation,
cap, size, stop or path rule converts a loser without killing a
winner or collapsing on a knife-edge. No further family should be
spent on Cluster 2 entry/exit rules until forward paper accumulates
new reclaim trades; forward logging (date, signal, L, frozen
entry/stop/risk/target, exit, net, and what the original trade
would have done — paper only, no re-fitting on the paper month)
is the only honest next step for this cluster, and it is a logging
instruction, not a candidate.

## Verdict — family (u) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| 1 — 23 Mar vs untouched axes | None (post-entry persistence only, post-trade) | 23 Mar and 30 Mar share gap, below-PDL, BN gap, BN day return; only post-entry bounce persistence differs | No — unfilterable at entry on tested axes |
| 1 — Bounce-persistence guards | U1 | Cluster 1 2/8, −₹17,445; combined +₹66,935 | No — catastrophic, deletes working re-entries |
| 2 — 13 May give-back, OOS | G3 (green rate) / G4 (total) | G3: 78.4% green, 19/35 converted, but total ₹11,580 below (lA); G4: total above (lA), but 55.4% green, 2/35 converted | No — no variant passes green AND total together |
| 3 — Cluster 2 new axes | None | No axis separates 6 trades; every axis fails in both directions | No — recorded unfixable on available sample |

- **No (u) variant passes** the full bar (60% green on the failing
  set AND total positive AND combined NOT below (lA), winners not
  collapsed) as a genuine conversion fix.
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is not
  adopted. Cluster 3 survival N=10 (3/3, +₹4,589.25) remains the
  best scoped result for Cluster 3 only, combined below baseline.
  November paper is NOT frozen for any (u) variant. No (u)
  in-sample result is carried into a whole-month run on the same
  Jan–Oct data.
- **Dead, do not re-propose without new evidence:** bounce-
  persistence re-entry guards U1/U2 (delete the 29 Jun, 8 Jul and
  19 Aug working re-entries); ungated morning partials as a
  13 May fix (buy green count with winner value on both windows);
  time-gated partials as a green-rate fix (already failed (q));
  any Cluster 2 entry/exit rule on the 6-trade sample (see Part 3
  list); any entry filter for the untouched shape that does not
  first explain 23 Mar vs 30 Mar.

## Next family (v) — the task continues, not completed

Family (u) closes the entry-filter question for the untouched shape
(on tested axes), the re-entry-guard question (backwards), and the
Cluster 2 question (on the available sample). What remains open,
in the order the evidence points to it:

1. **Survival-gated partial on the OOS window.** The one give-back
   shape never tested OOS: partial (k=1.0, trail BE) booked only if
   the trade is still open at gate N (interpretation B, eligibility
   as in the survival sweep), for N = 5, 10, 20, on the 92-day OOS
   window with (lA) baseline on the same window. In-sample, survival
   N=10 kept Cluster 3 green (3/3, +₹4,589.25) at a winner tax of
   −₹21,936 on the in-sample winner set; the OOS test decides
   whether that tax is smaller than the ungated partials' tax
   (−₹74,000 to −₹122,000) and whether its loser conversion clears
   60% of traded days *with* a total above (lA). If it fails any
   leg, the give-back family is exhausted on this data and 13 May
   stays an in-sample example.
2. **(lA) re-entry, accepted as-is, or a re-entry-timing variant
   that does not delete working trades.** U1/U2 prove the guard
   direction is wrong; any new re-entry idea must be checked
   against the 29 Jun, 8 Jul and 19 Aug working re-entries in the
   same table, before it is proposed as a fix for 30 Mar / 2 Apr.
3. **Cluster 2: forward logging only.** No new entry/exit family
   until new reclaim trades accumulate in forward paper; log them
   in the (s) format, paper only, with no re-fitting on the paper
   month.

Files: engine `u_sweep.py`, raw replay `u_sweep_raw.json`, this
report `nifty_cluster1_u_sweep.md`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task continues
in the parent conversation: family (u) is exhausted, none is
adopted, and the next decision is family (v) — not a whole-month
run of any (u) variant on the same Jan–Oct data.
