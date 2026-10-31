# NIFTY — Family (p): morning partial whose trail is NOT breakeven-on-high, and/or partial NOT applied blindly to every morning
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): family (p), UNTRIED, Nifty only, paper only,
full pass bar = Cluster 1 green ≥60% (≥5/8) AND Cluster 1 total positive
AND combined PE total NOT below (lA) +₹80,660, winners not collapsed.
(p) = a morning partial whose trail is NOT breakeven, and/or a partial
that is not applied blindly to every morning — e.g. trail to the partial
level itself, or a continuation filter evaluated AT the partial trigger
that decides trail-vs-hold before the reversal is known. (p) must be
defined WITHOUT hindsight. No (o) variant is re-run alone here.

Base for comparison: (lA) = (lC) = (n3) on Cluster 1 — 5/8 day-green,
total −₹2,720, winners 12/14 green, 2 no-trade, +₹83,380, combined
+₹80,660. Baseline plain combined +₹66,980. (o1) Cluster 1 6/8,
+₹4,832.50, but winners +₹46,075, combined +₹50,907.50 — failed.
(lA) itself is NOT adopted; it is only the previous best kept.

Engine: `morning_partial_p_sweep.py`, raw replay
`morning_partial_p_sweep_raw.json`; Clusters 2/3 direct replay
`morning_partial_p_clusters23.py`, raw
`morning_partial_p_clusters23_raw.json`. Replayed bar by bar from the
Upstox 5-min cache, same (d)/(k) BN-confirmed rescan morning as (h)–(o)
(entry = next bar open, stop = signal high, target = entry − 2×risk,
square-off 15:10, 100 shares equivalent, ₹40/trade, re-entry scan =
(lA) plain full trade, afternoon stop-on-first-fail, to 15:05).
Re-entry rule as in (o): re-entry runs ONLY if the morning final exit
is a stop (plain stop, or stop_after_partial at the original stop).
If the morning exits at target, trail exit, or square-off, the day is
closed — no re-entry.

## Definitions, stated before the results

Morning trade in ALL (p) variants = (k)'s rescan morning. The partial
is applied to that morning trade ONLY; the re-entry, if any, is plain.

- **(p1) closeBE:** partial50 at 1.0×risk; remaining trail = entry,
  but exit ONLY on a 5-min CLOSE ≥ entry (PE). A wick high touch
  alone does not exit. Original stop still exits intra-bar.
- **(p2) closeMid:** partial50 at 1.0×risk; remaining trail =
  entry − 0.5×risk, exit ONLY on close ≥ that mid level. Trail exit
  nets 75×risk − ₹40 instead of 50×risk − ₹40.
- **(p3) highMid:** partial50 at 1.0×risk; remaining trail =
  entry − 0.5×risk, exit on intra-bar HIGH ≥ mid level.
- **(p4) time1000:** (o1) highBE, but partial booked ONLY if the
  partial trigger bar time < 10:00; a later partial is a plain trade.
- **(p5) time0945:** as (p4), cutoff < 09:45.
- **(p6) time1030:** as (p4), cutoff < 10:30.
- **(p7) time1000_closeBE:** (p4) + (p1) combined.
- **(p8) time1000_closeMid:** (p4) + (p2) combined.

Accounting/order: 100 shares split 50/50, ₹40 cost once, original
stop (intra-bar high) BEFORE favourable (partial/target) on each bar;
target on a bar beats a trail-close on the same bar (low ≤ target);
high-touch trails start on the NEXT bar after the partial bar (as in
(o) — the partial bar's high may pre-date the low touch within the
bar; this was caught and fixed during this sweep, see below).
Green = net > ₹0. No-trade counted separately from green throughout.
For CE in Clusters 2/3 the rules are mirrored (partial level
entry + 1.0×risk, trail BE = entry, mid = entry + 0.5×risk, close
exit on close ≤ trail level).

## Headline — (p) PASSES the full pass bar in-sample, with three variants — but read the caveats before calling it a fix

| Set | Cluster 1 green | Cluster 1 total (₹) | Winners (₹) | Combined PE (₹) | Pass full bar? |
|---|---|---|---|---|---|
| Baseline (plain) | 0/8 | −24,290 | +91,270 | +66,980 | — |
| (lA) (reference) | 5/8 day | −2,720 | +83,380 | +80,660 | No — total negative |
| (o1) (prior family) | 6/8 day | +4,832.50 | +46,075 | +50,907.50 | No — combined regresses |
| **(p1) closeBE** | 6/8 day | +4,832.50 | +56,695 | +61,527.50 | **No** — combined below (lA) |
| **(p2) closeMid** | 6/8 day | +6,091.25 | +49,027.50 | +55,118.75 | **No** — combined below (lA) |
| **(p3) highMid** | 6/8 day | +6,091.25 | +42,337.50 | +48,428.75 | **No** — worst combined in (p) |
| **(p4) time1000 highBE** | 6/8 day | +4,832.50 | +78,847.50 | **+83,680** | **YES — +₹3,020 above (lA)** |
| **(p5) time0945 highBE** | 6/8 day | +4,832.50 | +82,422.50 | **+87,255** | **YES — +₹6,595 above (lA), best in (p)** |
| **(p6) time1030 highBE** | 6/8 day | +4,832.50 | +58,147.50 | +62,980 | **No** — combined below (lA) |
| **(p7) time1000 closeBE** | 6/8 day | +4,832.50 | +78,847.50 | **+83,680** | **YES — same as (p4) on this data** |
| **(p8) time1000 closeMid** | 6/8 day | +6,091.25 | +78,847.50 | **+84,938.75** | **YES — +₹4,278.75 above (lA)** |

Winner green count is 12/14, 2 no-trade, 0 losses in ALL (p)
variants — the pass/fail is entirely about winner VALUE, as in (o).

**What "passes" means here, and what it does NOT mean:**
- (p4), (p5), (p7), (p8) meet every leg of the stated full pass bar
  on Cluster 1 + winners, in-sample, Jan–Oct 2026. That is the first
  time any family after (lA) has done so, and the task's reporting
  condition for family (p) is therefore met.
- It does NOT mean (p) is adopted. The cutoffs were chosen from a
  small pre-defined set (09:45 / 10:00 / 10:30) after the partial
  trigger times on this same data were already visible in (o), so
  (p4)/(p5) are in-sample tuned variants, not out-of-sample proof.
  A variant must still prove itself on unseen data (a future month,
  e.g. November paper, or a held-out window) before adoption, under
  the same pass bar. Do NOT carry (p5) into a whole-month run or a
  live rule on this report alone.
- (p5) is, in substance, a near-no-partial rule: on the whole
  Cluster 1 + winners set it partials exactly TWO mornings —
  13 May (Cluster 1) and 29 Sep (winner). Every other morning is a
  plain trade. Its combined gain over (lA) (+₹6,595) is therefore
  13 May's +₹7,552.50 swing minus 29 Sep's −₹957.50 shrinkage, and
  nothing else. That is a one-day saving, not a broad conversion —
  the same narrowness warned about in (o), now on the winner side
  too. (p4) partials four mornings (13 May, 13 Mar, 24 Apr, 29 Sep)
  and gains +₹3,020 over (lA) for the same reason.
- The cutoff is fragile by construction: moving it 5 minutes either
  way changes which mornings are partialled (23 Mar partials at
  10:00, 24 Apr at 09:45, 7 Sep at 10:15, 23 Oct at 10:15), and (p6)
  at 10:30 already fails. A rule whose pass depends on a 15-minute
  window must be treated as a candidate to validate, not a found edge.

## Results — (p), Cluster 1 (identical day nets in all variants except 13 May under mid trails)

Cluster 1 day nets are the (lA) day nets except 13 May in every
variant, because no other Cluster 1 morning reaches its partial
trigger before its stop:

| Date | (lA) day net | (p1)/(p4)/(p5)/(p6)/(p7) | (p2)/(p3)/(p8) |
|---|---|---|---|
| 2026-01-09 | +₹2,295 | +₹2,295 | +₹2,295 |
| 2026-02-06 | +₹1,120 | +₹1,120 | +₹1,120 |
| 2026-03-30 | −₹2,055 | −₹2,055 | −₹2,055 |
| 2026-04-02 | −₹3,730 | −₹3,730 | −₹3,730 |
| **2026-05-13** | **−₹5,075** | **+₹2,477.50** (partial 09:35, BE exit 09:50) | **+₹3,736.25** (partial 09:35, mid exit 09:50) |
| 2026-06-29 | +₹2,100 | +₹2,100 | +₹2,100 |
| 2026-07-08 | +₹955 | +₹955 | +₹955 |
| 2026-08-19 | +₹1,670 | +₹1,670 | +₹1,670 |
| **Cluster 1 total** | **−₹2,720** | **+₹4,832.50** | **+₹6,091.25** |
| **Cluster 1 green** | **5/8** | **6/8** | **6/8** |

30 Mar and 2 Apr are untouched by every (p) variant, as in (o):
no partial, re-entry unchanged. (p) converts exactly one Cluster 1
morning (13 May) and keeps the five (lA) greens — it does not
convert 30 Mar or 2 Apr, and it does not create a second new green.

## Winners — why close trails alone fail, and why time-gating passes

Winners under (lA): 12/14 green, 2 no-trade (24 Feb, 12 Aug), 0 losses,
+₹83,380. Winner day nets by variant (only days that change vs (lA)
are listed; all other traded winners keep their (lA) net):

- **(p1) closeBE, winners +₹56,695 (−₹26,685 vs (lA)).** Close-BE
  saves three of the five (o1) BE winners to target_after_partial:
  23 Mar +₹5,435 (was BE +₹1,785), 7 Sep +₹1,842.50 (was +₹587.50),
  23 Oct +₹8,532.50 (was +₹2,817.50) — their BE bars were wick
  touches with closes back below entry (23 Mar 10:05 close
  22,605.65 < entry 22,628.55; 7 Sep 10:20 close 23,801.60 <
  23,808.10; 23 Oct 10:20 close 22,516.30 < 22,526.25). But 5 May
  and 22 Jul still exit at BE on a close (5 May 11:00 close
  23,951.90 > entry 23,941.40; 22 Jul closes above entry by 11:20),
  and the other seven traded winners still shrink by 50×risk each
  to target_after_partial. Close-BE is a real improvement over
  high-BE (+₹10,620 vs (o1)) but not enough: it still truncates
  two runners and shrinks seven targets.
- **(p2) closeMid, winners +₹49,027.50 (−₹34,352.50).** Mid-close
  pays more than BE on trail exits (13 May +₹3,736.25, 23 Mar
  would be +₹2,697.50 instead of +₹5,435) but it fires EARLIER
  than BE on bounces that reach mid without reaching entry —
  23 Mar exits mid at 10:00 itself, 7 Sep at 10:40, 23 Oct at
  10:20 — so it truncates runners (o1)'s BE rule would have
  kept to target_after_partial under (p1). Mid trails are worse
  than BE trails for winners, in both close and high form.
- **(p3) highMid, winners +₹42,337.50 (−₹41,042.50).** Worst in
  (p): every bounce that reaches mid on the next bar exits at
  75×risk, including 16 Mar (+₹3,327.50 vs (p1) +₹6,695) and
  24 Apr (+₹3,282.50 vs +₹6,605). Trail-to-mid is NOT a solution
  to the winner-shrinkage problem — it is a faster truncation.
- **(p4) time1000, winners +₹78,847.50 (−₹4,532.50).** Only three
  winners are partialled: 13 Mar target_after_partial +₹4,040
  (was +₹5,400), 24 Apr +₹6,605 (was +₹8,820), 29 Sep
  +₹2,832.50 (was +₹3,790). All later winners (23 Mar, 5 May,
  22 Jul, 7 Sep, 23 Oct, and the 10:20/10:40/11:25 winners) are
  plain targets, untouched. Winner loss ₹4,532.50 < Cluster 1
  gain ₹7,552.50, so combined passes by ₹3,020.
- **(p5) time0945, winners +₹82,422.50 (−₹957.50).** Only ONE
  winner is partialled: 29 Sep +₹2,832.50 (was +₹3,790). 24 Apr's
  partial at 09:45 is NOT < 09:45, so it is plain +₹8,820.
  Winner loss ₹957.50 < Cluster 1 gain ₹7,552.50, so combined
  passes by ₹6,595 — the best in (p), and the narrowest rule.
- **(p6) time1030, winners +₹58,147.50 (−₹25,232.50).** Adds
  23 Mar BE +₹1,785, 22 Jul BE +₹1,550, 7 Sep BE +₹587.50,
  23 Oct BE +₹2,817.50 to the (p4) set — the five BE winners
  return, and combined fails again. This is the fragility
  warning in numbers: 10:00 passes, 10:30 fails.
- **(p7) time1000_closeBE, winners +₹78,847.50.** Identical to
  (p4) on this data: the only partialled winners are the three
  target_after_partial mornings, none of which touches BE, so
  close-vs-high makes no difference here.
- **(p8) time1000_closeMid, winners +₹78,847.50, Cluster 1
  +₹6,091.25, combined +₹84,938.75.** Same winner set as (p4),
  plus 13 May's mid-close gain (+₹1,258.75 over BE). Second-best
  combined in (p), and the only passing variant that improves
  BOTH legs over (p4).

## A replay bug caught and fixed during this sweep (must travel with the numbers)

The first (p) run let a high-touch trail fire on the SAME bar as
the partial. That is wrong: the partial bar's high may pre-date
the low touch within the bar, and (o) never fired a trail on the
partial bar itself. It understated (p4) winners by ₹2,720 (13 Mar
showed a same-bar BE exit +₹1,320 instead of target_after_partial
+₹4,040). The fixed engine (`morning_partial_p_sweep.py`) starts
high-touch trails on the NEXT bar after the partial bar; close
trails may use the partial bar's own close, which is after the
touch. All numbers in this report are from the FIXED run, verified
against the raw JSON. (o) numbers are unaffected — (o) already
used next-bar trails.

## Clusters 2 and 3 — passing variants applied, as instructed

Condition: apply a variant to Clusters 2/3 if it passes on Cluster 1
with positive economics. (p4), (p5), (p7), (p8) pass, so they were
applied to the ORIGINAL Cluster 2/3 trades (direct replay, CE
mirrored). Original Clusters 2+3 total: −₹22,005 (Cluster 2
−₹11,420, Cluster 3 −₹10,585). For reference, non-passing (p1)/(p2)
were also run on Clusters 2/3 to show the contrast:

| Variant | Cluster 2 (2 trades) | Cluster 3 (3 trades) | Clusters 2+3 combined |
|---|---|---|---|
| (p4) time1000 highBE | 0/2 green, −₹11,420 | 1/3 green, −₹5,140 | 1/5 green, −₹16,560 |
| (p5) time0945 highBE | 0/2 green, −₹11,420 | 0/3 green, −₹10,585 | 0/5 green, −₹22,005 (unchanged) |
| (p8) time1000 closeMid | 0/2 green, −₹11,420 | 1/3 green, −₹4,232.50 | 1/5 green, −₹15,652.50 |
| (p1) closeBE (not passing) | 1/2 green, −₹7,302.50 | 2/3 green, −₹452.50 | 3/5 green, −₹7,755 |
| (p2) closeMid (not passing) | 1/2 green, −₹6,616.25 | 2/3 green, +₹1,236.25 | 3/5 green, −₹5,380 |

Day detail for the passing variants:
- (p4): only 18 May converts — partial 09:55, BE exit 10:00 →
  +₹1,775 (was −₹3,670). 14 Jan partial is gated out (11:30 ≥
  10:00) → plain stop −₹2,785; 26 Oct partial never triggers
  → −₹8,635; 13 Feb partial never triggers → −₹3,750;
  30 Apr partial gated out (10:15 ≥ 10:00) → −₹3,165.
- (p5): NOTHING converts — 18 May's partial at 09:55 is also
  ≥ 09:45, so every Cluster 2/3 trade is plain and the total is
  exactly the original −₹22,005. (p5) passes Cluster 1 + winners
  and does literally nothing for Clusters 2/3.
- (p8): only 18 May converts — partial 09:55, mid-close exit
  09:55 → +₹2,682.50 (was −₹3,670); all other days as (p4).

Caveat, same as (o3): the Clusters 2/3 gains under (p1)/(p2)
are exit banking on give-back trades, not entry fixes, and they
come with the winner collapse that fails the combined bar — so
they do NOT rescue a non-passing variant, and the passing
variants' Clusters 2/3 numbers must not be quoted as a pass on
their own. On the full picture (Cluster 1 + winners + Clusters
2/3, for scale only, not a new pass bar): (p5) is +₹87,255 −
₹22,005 = +₹65,250; (p4) is +₹83,680 − ₹16,560 = +₹67,120;
(p8) is +₹84,938.75 − ₹15,652.50 = +₹69,286.25. All three are
still below (lA)'s Cluster 1 + winners alone on a like-for-like
basis only if Clusters 2/3 are added to (lA) too — (lA) on the
same full picture is +₹80,660 − ₹22,005 = +₹58,655, so (p)
passing variants DO improve the full picture by ₹6,595–
₹10,631.25 in-sample. That improvement is entirely 13 May
(and, for (p4)/(p8), 18 May) — it is not a Clusters 2/3 fix.

## Variant summary — family (p), pass bar applied

| Family / variant | Cluster 1 green | Cluster 1 total (₹) | Winners (₹) | Combined PE (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline (plain) | 0/8 | −24,290 | +91,270 | +66,980 | — |
| (lA) (reference) | 5/8 day | −2,720 | +83,380 | +80,660 | No — total negative |
| (o1) (lA) + partial50_trailBE morning | 6/8 day | +4,832.50 | +46,075 | +50,907.50 | No — combined regresses |
| (p1) closeBE | 6/8 day | +4,832.50 | +56,695 | +61,527.50 | No — combined below (lA) |
| (p2) closeMid | 6/8 day | +6,091.25 | +49,027.50 | +55,118.75 | No — combined below (lA) |
| (p3) highMid | 6/8 day | +6,091.25 | +42,337.50 | +48,428.75 | No — worst in (p) |
| **(p4) time1000 highBE** | **6/8 day** | **+4,832.50** | **+78,847.50** | **+83,680** | **YES in-sample — +₹3,020 vs (lA)** |
| **(p5) time0945 highBE** | **6/8 day** | **+4,832.50** | **+82,422.50** | **+87,255** | **YES in-sample — +₹6,595 vs (lA), best in (p)** |
| (p6) time1030 highBE | 6/8 day | +4,832.50 | +58,147.50 | +62,980 | No — combined below (lA) |
| **(p7) time1000 closeBE** | **6/8 day** | **+4,832.50** | **+78,847.50** | **+83,680** | **YES in-sample — same as (p4) here** |
| **(p8) time1000 closeMid** | **6/8 day** | **+6,091.25** | **+78,847.50** | **+84,938.75** | **YES in-sample — +₹4,278.75 vs (lA)** |

## What (p) proves, and what remains — task continues, not completed

- A morning partial CAN pass the full Cluster 1 + winners bar —
  but only when it is NOT applied to every morning. Time-gating
  the partial to the earliest trigger bars (<09:45, or <10:00)
  is what passes; close trails alone do not, and mid trails
  make winners worse. The (o) lesson is refined, not overturned:
  the partial's cost is per winner partialled, so the passing
  variants minimise how many winners are partialled at all.
- What (p) does NOT prove: that 09:45 / 10:00 is a real edge.
  The cutoff was selected in-sample, the passing variants each
  hinge on one or two mornings (13 May, and 29 Sep / 13 Mar /
  24 Apr on the winner side), and Clusters 2/3 are essentially
  untouched by the best variant (p5: 0/5, unchanged). 30 Mar
  and 2 Apr remain unconverted in every variant in (o) and (p).
- Next family, NOT a re-run of (p) and NOT adoption of (p5):
  **(q) out-of-sample validation of the (p) passing variants
  before any adoption** — run (p5), (p4), (p8) exactly as defined
  here on unseen data (November 2026 paper, and/or a held-out
  month window) under the same full pass bar, with the cutoff
  frozen at 09:45 / 10:00 and no re-tuning on that window; if
  it fails there, (p) joins (o) as in-sample only and the next
  family returns to the two untouched Cluster 1 days (30 Mar,
  2 Apr) and to Clusters 2/3 on their own terms. Until (q)
  passes, the previous best kept is still (lA) on Cluster 1
  economics (−₹2,720, 5/8) with winners intact — and (lA)
  itself is not adopted either.

Files: engine `morning_partial_p_sweep.py`, raw replay
`morning_partial_p_sweep_raw.json`, Clusters 2/3 engine
`morning_partial_p_clusters23.py`, raw
`morning_partial_p_clusters23_raw.json`. Paper only throughout;
no orders placed, nothing fabricated. The long-horizon task
continues in the parent conversation: family (p) variants are
exhausted, four pass in-sample, none is adopted, and the next
decision is family (q) out-of-sample validation — not a
whole-month run of (p5) on the same Jan–Oct data.
