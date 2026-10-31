# NIFTY — Family (o): (lA) + partial/trail exit on the MORNING trade only
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): family (o), UNTRIED, Nifty only, paper only,
same pass bar (60% green AND total positive AND winners not collapsed).
(o) = (lA)/(lC) combined with a partial/trail exit on the MORNING trade
only — distinct from (m), which was re-entry only. No family (l)–(n) or
earlier family is re-run alone here.

Base for comparison: (lA) = (lC) = (n3) on Cluster 1 — 5/8 day-green,
total −₹2,720, winners 12/14 green, 2 no-trade, +₹83,380, combined
+₹80,660. (lA) remaining problem, fully enumerated: three losses
−₹10,860 (30 Mar −₹2,055, 2 Apr −₹3,730, 13 May −₹5,075) against five
greens +₹8,140.

Engine: `morning_partial_sweep.py`, raw replay
`morning_partial_sweep_raw.json`; Clusters 2/3 direct replay
`morning_partial_clusters23.py`, raw
`morning_partial_clusters23_raw.json`. Replayed bar by bar from the
Upstox 5-min cache, same (d)/(k) BN-confirmed rescan morning as (h)–(n)
(entry = next bar open, stop = signal high, target = entry − 2×risk,
stop before target per bar including the entry bar, square-off 15:10,
100 shares equivalent, ₹40/trade, re-entry scan = (lA) plain full
trade, afternoon stop-on-first-fail, to 15:05).

## Definitions, stated before the results

Morning trade in ALL (o) variants = (k)'s rescan morning. The partial
is applied to that morning trade ONLY; the re-entry, if any, is a plain
full trade (200×risk target, original stop), NOT partialled.

- **(o1) partial50_trailBE:** trigger entry − 1.0×risk, book 50 shares
  there, remaining stop moves to breakeven (entry).
- **(o2) partial50_noTrail:** trigger entry − 1.0×risk, book 50 shares
  there, remaining keeps the ORIGINAL stop.
- **(o3) partial25_trailBE:** trigger entry − 0.5×risk, book 50 shares
  there, remaining stop moves to breakeven (entry).
Accounting/order, as in `partial_trail_sweep.py` and
`extended_window_sweep.py`: 100 shares split 50/50, ₹40 cost charged
once, adverse level (stop / trailed stop) checked BEFORE favourable
level (partial / target) on each bar; partial+target on the same bar
nets 150×risk − ₹40 for (o1)/(o2) and 125×risk − ₹40 for (o3), instead
of 200×risk − ₹40. Green = net > ₹0. No-trade counted separately
from green throughout.

Re-entry rule, the one judgement in (o), stated before the results:
the (lA) re-entry scan runs ONLY if the morning trade's final exit is
a stop — a plain stop (no partial booked) or a stop_after_partial under
(o2) (remaining leg hits the original stop, morning net = −₹40 scratch).
If the morning exits at target, at breakeven after a partial (o1/o3,
morning net positive), or at square-off, the day is closed — no
re-entry. Morning net and re-entry net are reported separately per day
below, so the decomposition is auditable. In fact this judgement changes
no Cluster 1 day: under (o2) the only partial-booked morning is 13 May,
which exits stop_after_partial at 09:55, and (lA) finds no re-entry
candidate on 13 May at any time to 15:05 (no bar closes below OR low
after the stop), so the re-entry-after-scratch question is moot on
Cluster 1. It is flagged here so a later family cannot silently assume
it either way.

## Headline — (o) passes Cluster 1, fails combined economics, nothing adopted

- **All three (o) variants pass the Cluster 1 legs of the pass bar:**
  (o1) 6/8 green, +₹4,832.50; (o2) 5/8 green, +₹2,315; (o3) 6/8 green,
  +₹1,920. Green bar (≥5/8) met in all three, Cluster 1 total positive
  in all three. That is the first time in families (h)–(o) that Cluster 1
  itself is positive — the 13 May hypothesis in the parent task is
  confirmed exactly (see below).
- **But NO (o) variant passes the full pass bar, because winners are
  shrunk far more than Cluster 1 gains.** Winner green count is
  unchanged (12/14 green, 2 no-trade, 0 losses in all three variants),
  but winner VALUE falls in all three: (o1) +₹46,075 (−₹37,305 vs (lA)),
  (o2) +₹62,415 (−₹20,965), (o3) +₹31,102.50 (−₹52,277.50). Combined
  PE totals therefore FALL below (lA) in all three: (o1) +₹50,907.50,
  (o2) +₹64,730, (o3) +₹33,022.50, against (lA) +₹80,660 and even against
  the plain baseline combined +₹66,980 for (o1) and (o3). A Cluster 1
  gain of +₹4,640 to +₹7,552.50 bought with a winner loss of
  ₹20,965–₹52,277.50 is not positive economics — it is the same
  avoidance-total error warned about in every prior report, in reverse:
  do not quote the Cluster 1 total alone as a pass when the combined
  total regresses.
- **Therefore: nothing in (o) is adopted, nothing is carried into a
  whole-month run on its own, and (o) is NOT presented as a pass.**
  The (o) variants are exhausted as a family. What (o) proves, and
  what it does not, is in the last section — the next family must
  solve the winner-shrinkage problem, not re-run (o).

## Results — (o), Cluster 1 (baseline 0/8, −₹24,290; (lA) 5/8, −₹2,720)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| (o1) Cluster 1 | 6/8 day | 0 | 2 | +4,832.50 | Cluster 1 legs only — see combined |
| (o1) Winners | 12/14 | 2 | 0 | +46,075 | Green count kept, value −₹37,305 |
| (o1) Combined PE | — | — | — | +50,907.50 | No — below (lA) +₹80,660 and baseline +₹66,980 |
| (o2) Cluster 1 | 5/8 day | 0 | 3 | +2,315 | Cluster 1 legs only — see combined |
| (o2) Winners | 12/14 | 2 | 0 | +62,415 | Green count kept, value −₹20,965 |
| (o2) Combined PE | — | — | — | +64,730 | No — below (lA) +₹80,660 and baseline +₹66,980 |
| (o3) Cluster 1 | 6/8 day | 0 | 2 | +1,920 | Cluster 1 legs only — see combined |
| (o3) Winners | 12/14 | 2 | 0 | +31,102.50 | Green count kept, value −₹52,277.50 |
| (o3) Combined PE | — | — | — | +33,022.50 | No — worst combined in (o) |

Day-by-day, (o1) — the ONLY day that changes vs (lA) is 13 May:

| Date | Rescan morning (plain → partial) | Re-entry (lA, plain) | Day net: (lA) → (o1) |
|---|---|---|---|
| 2026-01-09 | stop 09:40 −₹3,745, partial never triggers | 10:50 target +₹6,040 | +₹2,295 → +₹2,295 (unchanged) |
| 2026-02-06 | stop 10:15 −₹1,810, partial never triggers | 10:20 target +₹2,930 | +₹1,120 → +₹1,120 (unchanged) |
| 2026-03-30 | stop 11:30 −₹2,055, partial never triggers | none (11:45 afternoon first-fail ends scan) | −₹2,055 → −₹2,055 (unchanged) |
| 2026-04-02 | stop 10:50 −₹2,065, partial never triggers | 11:25 stop −₹1,665 | −₹3,730 → −₹3,730 (unchanged) |
| 2026-05-13 | **partial 09:35 at 23,286.95, breakeven exit 09:50 → +₹2,477.50** | none | **−₹5,075 → +₹2,477.50 (swing +₹7,552.50)** |
| 2026-06-29 | stop 09:40 −₹4,740, partial never triggers | 11:30 target +₹6,840 | +₹2,100 → +₹2,100 (unchanged) |
| 2026-07-08 | stop 09:45 −₹1,985, partial never triggers | 12:05 target +₹2,940 | +₹955 → +₹955 (unchanged) |
| 2026-08-19 | stop 09:50 −₹2,300, partial never triggers | 10:15 target +₹3,970 | +₹1,670 → +₹1,670 (unchanged) |

The 13 May hypothesis is confirmed exactly, bar by bar: entry
23,337.30, risk 50.35, partial level 23,286.95, books its 50% partial on
the entry bar itself (09:35 low 23,262.55 ≤ 23,286.95, high 23,339.35 <
stop 23,387.65), remaining leg exits at breakeven on the 09:50 bar
(high 23,372.45 ≥ entry 23,337.30), morning net 50 × 50.35 − ₹40 =
+₹2,477.50 instead of −₹5,075. (o1) Cluster 1 total is therefore
exactly (lA) −₹2,720 + ₹7,552.50 = +₹4,832.50, and the only new green
in (o1) is 13 May. Every other (o1) morning stops before its partial
trigger is reached — the partial does nothing on 7 of 8 Cluster 1
mornings, which is why (o1) cannot convert 30 Mar or 2 Apr, and why
its Cluster 1 gain is a single-day gain, not a broad conversion.

Day-by-day, (o2) — only 13 May changes vs (lA):

| Date | Morning (o2) | Re-entry | Day net: (lA) → (o2) |
|---|---|---|---|
| 2026-01-09, 02-06, 03-30, 04-02, 06-29, 07-08, 08-19 | as (o1): plain stop, partial never triggers | as (lA) | unchanged |
| 2026-05-13 | partial 09:35, then remaining hits original stop 09:55 → **−₹40 scratch** | none (no candidate to 15:05) | −₹5,075 → −₹40 (swing +₹5,035; NOT green) |

(o2) therefore reaches 5/8 green only because the five (lA) greens are
kept and 13 May becomes a −₹40 scratch rather than a −₹5,075 loss —
its Cluster 1 total +₹2,315 is positive, but its green count is the
(lA) count, not a new conversion. Do not quote (o2) as "converting
13 May to green": it converts it to a scratch.

Day-by-day, (o3) — three days change vs (lA):

| Date | Morning (o3) | Re-entry | Day net: (lA) → (o3) |
|---|---|---|---|
| 2026-01-09, 02-06, 03-30, 04-02, 06-29 | as (o1): plain stop, partial trigger (0.5×risk) not reached before stop | as (lA) | unchanged |
| 2026-05-13 | partial 09:35 at 23,312.12, breakeven exit 09:50 → +₹1,218.75 | none | −₹5,075 → +₹1,218.75 (swing +₹6,293.75) |
| 2026-07-08 | partial 09:35 at 24,211.72, breakeven exit 09:40 → +₹446.25 | **none — morning already closed green, so the (lA) 12:05 re-entry target is not taken** | +₹955 → +₹446.25 (swing −₹508.75) |
| 2026-08-19 | partial 09:35 at 24,065.10, breakeven exit 09:40 → +₹525 | **none — same reason** | +₹1,670 → +₹525 (swing −₹1,145) |

(o3) Cluster 1 total is (lA) −₹2,720 + ₹6,293.75 − ₹508.75 − ₹1,145 =
+₹1,920. Its 6/8 green count is 13 May plus the five (lA) greens
minus nothing, plus 8 Jul and 19 Aug counted as morning-BE greens
instead of re-entry greens — so (o3) creates one genuinely new green
(13 May) and shrinks two existing greens. The lower 25% trigger is
therefore not a better version of (o1) on Cluster 1: it buys 13 May
for ₹1,218.75 instead of ₹2,477.50 and pays ₹1,653.75 back on
8 Jul + 19 Aug.

## Winners — why (o) fails the combined bar (must not be hidden)

Winners under (lA): 12/14 green, 2 no-trade (24 Feb, 12 Aug, rescan
no-trade), 0 losses, +₹83,380. Under (o) the green count and the
no-trade count are identical in all three variants — no winner flips
to a loss — but the value falls because every winning morning that
reaches its partial trigger either banks only 150×risk / 125×risk
instead of 200×risk, or, worse under a trail, exits at breakeven after
the partial instead of running to target.

(o1) winner detail (12 traded days; 24 Feb and 12 Aug no-trade as in (lA)):
- Target after partial (150×risk − ₹40, shrunk): 21 Jan +₹6,950
  (was +₹9,280), 16 Mar +₹6,695 (was +₹8,940), 13 Mar +₹4,040 (was
  +₹5,400), 24 Apr +₹6,605 (was +₹8,820), 27 Aug +₹2,225 (was +₹2,980
  under the (lA) rescan morning),
  8 Oct +₹8,757.50 (was +₹11,690).
- Breakeven after partial (50×risk − ₹40, still green but a fraction
  of the target): 23 Mar +₹1,785 (was +₹7,260), 5 May +₹1,230 (was
  +₹5,040), 22 Jul +₹1,550 (was +₹6,320), 7 Sep +₹587.50 (was +₹2,470
  under the (lA) rescan morning), 23 Oct +₹2,817.50 (was +₹11,390).
- Target same bar as partial: 29 Sep +₹2,832.50 (was +₹3,790).
Five winning mornings that would have run to target are cut to a
breakeven exit by the (o1) trail — that is ₹37,305 of winner value
given up for one Cluster 1 day (+₹7,552.50). (o2) avoids the trail, so
its winners keep target_after_partial on all 12 traded days and fall
only ₹20,965 (the 50×risk partial shrinkage on each target). (o3)
trails earliest, so five-plus winning mornings exit at breakeven and
its winners fall ₹52,277.50 — the worst combined total in (o), despite
its 6/8 Cluster 1 green count.

The lesson is structural, not a tuning miss: a partial/trail exit
applied to EVERY morning, winners included, cannot distinguish a
morning that will give back (13 May) from a morning that will run to
target (23 Mar, 23 Oct) at the moment the partial triggers — both have
moved 1.0×risk favourably. The trail therefore saves the give-back
morning and truncates the runner in the same stroke. Any next family
that keeps a morning partial must first answer: at partial time, what
— other than hindsight — separates the give-back morning from the
runner? That question is NOT answered by (o), and (o) must not be
carried forward as if it were.

## Clusters 2 and 3 — (o) applied, as instructed (original trades, direct replay)

Condition in the task: apply a variant to Clusters 2/3 if it passes
on Cluster 1 with positive economics. (o1)–(o3) pass the Cluster 1
legs, so all three were applied — to the ORIGINAL Cluster 2/3 trades
(direct bar-by-bar replay from the reported entry/stop/target, CE
mirrored: partial level entry + trigger×risk, adverse = low ≤ stop,
favourable = high ≥ partial/target; Cluster 2 is setup4 reclaim, not
a setup2 breakdown scan, so no signal rescan is used). Original
Clusters 2+3 total: −₹22,005 (Cluster 2 −₹11,420, Cluster 3 −₹10,585).

| Variant | Cluster 2 (2 trades) | Cluster 3 (3 trades) | Clusters 2+3 combined |
|---|---|---|---|
| (o1) partial50_trailBE | 1/2 green, −₹7,302.50 | 2/3 green, −₹452.50 | 3/5 green, −₹7,755 |
| (o2) partial50_noTrail | 0/2 green, −₹8,675 | 0/3 green, −₹3,830 | 0/5 green, −₹12,505 |
| (o3) partial25_trailBE | 2/2 green, +₹2,755 | 3/3 green, +₹2,496.25 | 5/5 green, +₹5,251.25 |

Day detail:
- (o1): 14 Jan CE partial 11:30, breakeven 12:10 → +₹1,332.50 (was
  −₹2,785); 26 Oct CE partial never triggers (MFE 70.45 < trigger
  85.95) → −₹8,635 unchanged; 13 Feb PE partial never triggers
  (MFE 35.70 < trigger 37.10) → −₹3,750 unchanged; 30 Apr PE partial
  10:15, breakeven 10:35 → +₹1,522.50 (was −₹3,165); 18 May PE partial
  09:55, breakeven 10:00 → +₹1,775 (was −₹3,670).
- (o2): the same three partial-booked trades become −₹40 scratches
  instead of greens (14 Jan stop_after_partial 13:20, 30 Apr
  12:10, 18 May 10:30); the two no-partial trades are unchanged.
  (o2) improves Clusters 2+3 by ₹9,500 (to −₹12,505) with zero greens
  — improvement by scratch, not by conversion.
- (o3): all five convert to small greens — 14 Jan +₹646.25
  (partial 11:25, breakeven 12:10), 26 Oct +₹2,108.75 (partial
  10:05, breakeven 10:25), 13 Feb +₹887.50 (partial 09:40,
  breakeven 09:45), 30 Apr +₹741.25 (partial 10:05, breakeven
  10:35), 18 May +₹867.50 (partial 09:50, breakeven 10:00) —
  combined +₹5,251.25, a ₹27,256.25 swing from −₹22,005.

Caveat that must travel with the (o3) Clusters 2+3 number: a 25%
partial + breakeven trail converts ANY give-back trade that moves
0.5×risk favourably and then reverses to entry into a small green,
by construction — it is exit banking, not an entry fix, and it is
the same mechanism that collapses winner value on Cluster 1
((o3) winners −₹52,277.50). The 5/5 (o3) green rate on Clusters 2/3
therefore does NOT rescue (o3) as a whole: on the full PE + CE
picture (Cluster 1 + winners + Clusters 2/3, for scale only, not a
new pass bar) (o3) is still far below (lA), because the winner
shrinkage dwarfs the Clusters 2/3 gain. No (o) variant is carried
into Clusters 2/3 as an adopted fix either — the application was
a test, and the test shows the same trade-off in all three clusters.

## Variant summary — family (o), pass bar applied

| Family / variant | Cluster 1 green | Cluster 1 total (₹) | Winners (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline (plain) | 0/8 | −24,290 | +91,270 | +66,980 | — |
| (lA) (reference, prior least-negative) | 5/8 day | −2,720 | +83,380 | +80,660 | No — green bar met, total negative |
| (o1) (lA) + partial50_trailBE morning | 6/8 day | +4,832.50 | +46,075 | +50,907.50 | No — Cluster 1 legs pass, combined regresses ₹29,752.50 vs (lA) |
| (o2) (lA) + partial50_noTrail morning | 5/8 day | +2,315 | +62,415 | +64,730 | No — Cluster 1 legs pass, combined regresses ₹15,930 vs (lA); 13 May is scratch, not green |
| (o3) (lA) + partial25_trailBE morning | 6/8 day | +1,920 | +31,102.50 | +33,022.50 | No — Cluster 1 legs pass, combined regresses ₹47,637.50 vs (lA); worst combined in (o) |

## What (o) proves, and what remains untested — task continues, not completed

- The 13 May hypothesis is confirmed exactly: a 50% morning partial
  with a breakeven trail turns 13 May from −₹5,075 into +₹2,477.50,
  and that single day is what takes Cluster 1 positive under (o1).
  No other Cluster 1 morning reaches even the 50% partial trigger
  before its stop, so (o1) is a one-day fix on Cluster 1, not a
  broad conversion — 30 Mar and 2 Apr are untouched by any (o)
  variant (30 Mar: no partial, no re-entry under (lA); 2 Apr:
  no partial, re-entry stop unchanged).
- A morning partial applied to every morning is a bad trade overall:
  it saves give-back mornings and truncates runners by the same
  mechanism, and on this data the truncation costs 3–7× the saving.
  (o2) is the least-bad combined variant (+₹64,730) precisely because
  it does NOT trail — it only shrinks targets by 50×risk each — and
  even (o2) is below baseline combined.
- What remains untested for Cluster 1 after (o) — the next family,
  NOT a re-run of (o): **(p) a morning partial whose trail is NOT
  breakeven, and/or a partial that is not applied blindly to every
  morning** — e.g. trail to the partial level itself (locking half
  the partial profit instead of all-or-nothing at breakeven), or a
  continuation filter evaluated AT the partial trigger (time of day,
  distance from the OR, Bank Nifty confirmation at that bar) that
  decides trail-vs-hold before the reversal is known. (p) must be
  defined without hindsight — a filter that uses the eventual outcome
  (target vs reversal) to choose the exit is not a rule — and it must
  be tested on Cluster 1 mornings AND winners together, with the same
  pass bar (Cluster 1 green ≥60%, Cluster 1 total positive, combined
  not below (lA)), before any claim. Until (p) or a later family
  passes that full bar, the previous best kept is still (lA) on
  Cluster 1 economics (−₹2,720, 5/8) with winners intact — and (lA)
  itself is not adopted either.

Files: engine `morning_partial_sweep.py`, raw replay
`morning_partial_sweep_raw.json`, Clusters 2/3 engine
`morning_partial_clusters23.py`, raw
`morning_partial_clusters23_raw.json`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task continues in
the parent conversation: family (o) variants are exhausted, none is
adopted, and the next decision is family (p) — not a whole-month run
of (o).
