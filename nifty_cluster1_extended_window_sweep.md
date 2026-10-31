# NIFTY — Extended-window families (l)–(n) on (k) only (Cluster 1)
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Task (parent, 2026-10-29): families (h)–(k) done
(`nifty_cluster1_triple_sweep.md`): (h) triple 2/8, −₹11,985;
(i) recovery-target 4/8, −₹10,845, same greens as (d), caps payoffs;
(j) RS re-entry 1/8, −₹18,025, RS dead on both trades; (k) (d)-extended
5/8 day-green, −₹4,110, combined +₹79,270 — green bar met, total still
negative, new ceiling not a pass, must not be quoted as a pass with a
negative total. Winners not collapsed by any variant there (12/14,
+₹83,380). Nothing adopted, nothing carried to a whole-month run.

This task, Nifty only, paper only, same pass bar (**60% green AND
Cluster 1 total positive AND winners not collapsed**): (l) (k) combined
with a rule avoiding the 30 Mar afternoon stop without losing the
8 Jul afternoon green; (m) (k) combined with a partial/trail exit on
the re-entry itself; (n) a morning-loss cap. No family (a)–(k) and no
earlier family is re-run alone here.

Engine: `extended_window_sweep.py`, raw replay
`extended_window_sweep_raw.json`. Replayed bar by bar from the Upstox
5-min cache (`data/progressive/NIFTY/spot_5m.csv` and
`data/progressive/BANKNIFTY/spot_5m.csv`), same (d) rescan morning as
(h)–(k) (BN-confirmed rescan morning: first V4/Skill breakdown at/after
the Bank Nifty break time, ≤11:30; entry = next bar open, stop = signal
high, target = entry − 2×risk, stop before target per bar including the
entry bar, square-off 15:10, 100 shares equivalent, ₹40/trade).
Green = net > ₹0. No-trade counted separately from green throughout.
Cluster 1 baseline: 8 trades, 0/8 green, total −₹24,290. Winners baseline:
14 V5 Nifty PE target days, 14/14 green, total +₹91,270. Baseline combined
PE: +₹66,980. (k) reproduction check in this run reproduces (k) exactly
(9 Jan +₹2,295, 6 Feb +₹1,120, 30 Mar −₹3,445, 2 Apr −₹3,730,
13 May −₹5,075, 29 Jun +₹2,100, 8 Jul +₹955, 19 Aug +₹1,670; total −₹4,110).

## Headline — families (l)–(n) all exhausted, nothing passes, nothing adopted

- **No variant passes all three legs.** (lA), (lC) and (n3) all reach
  5/8 green — the same green count as (k) — and improve the Cluster 1
  total to −₹2,720, but **−₹2,720 is still negative**, so none is a pass,
  none is applied to Clusters 2/3, and none is carried into a
  whole-month run on its own.
- **Best Cluster 1 total is now −₹2,720 (lA = lC = n3, identical day
  outcomes), not −₹4,110.** The improvement over (k) is exactly
  +₹1,390: the avoided 30 Mar afternoon stop, and nothing else. No new
  green is created by any (l)–(n) variant. "Least negative" is still
  not "positive", and must not be quoted as a pass.
- **Winners are NOT collapsed by any variant here** (all nine: 12/14
  green, 2 no-trade, 0 losses, +₹83,380 — identical to (d)/(k), because
  no rescan winner stops, so every re-entry leg is inert for winners,
  verified not assumed). The failure here is purely on Cluster 1
  economics, as in (h)–(k).
- **Combined totals must not be quoted as passes:** (lA)/(lC)/(n3)
  combined = −₹2,720 + ₹83,380 = **+₹80,660**, above (k) (+₹79,270) but
  still below RF-BAND-SCAN alone (+₹83,845), and it pairs a negative
  Cluster 1 total with unchanged winners — the same avoidance-total
  error warned about in every prior report.
- **(m) and the general (n) cap both make things worse, for stated
  reasons, not by assertion.** Partial on the re-entry cannot create a
  green because the two stopping re-entries never reach even a 25%
  partial trigger (see (m) below); a general morning-loss cap deletes
  working re-entries (see (n) below).

## Definitions, stated before the results

Morning trade in ALL variants = (k)'s morning: (d)'s BN-confirmed
rescan morning. If it stops, the re-entry scan is (k)'s band-filtered
scan (risk in [10, rescan risk]) unless the variant says otherwise.
Morning-phase candidates are ≤11:30, afternoon-phase candidates are
>11:30. This phase split matters for (lA): a whole-scan
stop-on-first-fail would kill 8 Jul at its 10:20 morning-phase band
fail (risk 27.00 > 19.45), so (lA) applies stop-on-first-fail ONLY to
the afternoon phase, not to the whole scan.

### (l) Avoid the 30 Mar afternoon stop, keep the 8 Jul afternoon green

- **(lA) Afternoon stop-on-first-fail.** Morning phase (≤11:30)
  scan-skip as in (k). Afternoon phase (>11:30): the FIRST candidate
  (close < Nifty OR low) failing the band ENDS afternoon scanning —
  no re-entry that day. A first afternoon candidate passing the band
  is traded. 30 Mar: first afternoon candidate 11:45, risk 20.65 >
  rescan risk 20.15, fails → scan ends, no 13:55 stop. 8 Jul: first
  afternoon candidate 12:05, risk 14.90 in band → traded, green kept.
- **(lB) Afternoon risk-ratio.** Morning scan-skip to 11:30;
  afternoon scan-skip to 15:05 with the EXTRA condition risk ≥
  0.70 × rescan risk, in addition to the band. Scan-skip continues
  past failing afternoon candidates (prior-sweep convention), so a
  ratio fail does not end the scan — it moves to the next candidate.
  30 Mar ratio: 13:55 risk 13.50 / 20.15 = 0.670, fails; 8 Jul ratio:
  14.90 / 19.45 = 0.766, passes. The 0.70 threshold is stated as a
  separator fitted on these two afternoons, not as a general rule.
- **(lC) Afternoon window to 12:30 only.** Morning scan-skip to
  11:30; afternoon scan-skip to 12:30 (not 15:05). 30 Mar: no passing
  afternoon candidate by 12:30 (11:45 fails the band, next passing
  candidate is 13:55) → no re-entry. 8 Jul: 12:05 passes within the
  window → green kept.

### (m) Partial/trail on the re-entry itself (morning unchanged)

Accounting and bar order exactly as in `partial_trail_sweep.py`:
100 shares split 50/50, ₹40 cost charged once, adverse level (stop /
trailed stop) checked BEFORE favourable level (partial / target) on
each bar, partial+target on the same bar handled as in that sweep.

- **(m1) partial50_trailBE:** trigger entry − 1.0×risk, book 50 shares
  there, remaining stop moves to breakeven (entry).
- **(m2) partial50_noTrail:** trigger entry − 1.0×risk, book 50 shares
  there, remaining keeps the ORIGINAL stop.
- **(m3) partial25_trailBE:** trigger entry − 0.5×risk, book 50 shares
  there, remaining stop moves to breakeven.
A winning re-entry under (m1)/(m2) nets 150×risk − ₹40 instead of
200×risk − ₹40; under (m3) it nets 125×risk − ₹40 instead of
200×risk − ₹40. Those are arithmetic consequences, not assumptions,
and they are what shrinks the existing greens below.

### (n) Morning-loss cap on (k)

- **(n1) Skip ANY re-entry if |morning net| > ₹4,000.**
- **(n2) Skip ANY re-entry if |morning net| > ₹3,000.**
- **(n3) Skip AFTERNOON re-entry only if |morning net| > ₹2,000**
  (morning-phase re-entries unaffected). 30 Mar morning −₹2,055 vs
  8 Jul morning −₹1,985: the ₹2,000 threshold separates them by
  ₹70. Any threshold in (₹1,985, ₹2,055] gives the same (n3) outcome
  and any threshold ≤₹1,985 would also skip 8 Jul, so (n3) is a
  knife-edge fitted separator, not a robust rule — flagged wherever
  it appears, even though its day outcome equals (lA)/(lC).

## Results — (l), Cluster 1 (baseline 0/8, −₹24,290; (k) 5/8, −₹4,110)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| (lA) Cluster 1 | 5/8 day | 0 | 3 | −2,720 | No — green bar met, total still negative |
| (lA) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (lA) Combined PE | — | — | — | +80,660 | No — below RF-BAND-SCAN +₹83,845 |
| (lB) Cluster 1 | 5/8 day | 0 | 3 | −4,545 | No — worse than (k) |
| (lB) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (lB) Combined PE | — | — | — | +78,835 | No |
| (lC) Cluster 1 | 5/8 day | 0 | 3 | −2,720 | No — green bar met, total still negative |
| (lC) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (lC) Combined PE | — | — | — | +80,660 | No — below RF-BAND-SCAN +₹83,845 |

Day-by-day, (lA) and (lC) — identical on all 8 days (differences from
(k) in bold):

| Date | Rescan morning | Re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50, risk 30.40 → target +6,040 | +2,295 GREEN |
| 2026-02-06 | −1,810 | 10:20, risk 14.85 → target +2,930 | +1,120 GREEN |
| 2026-03-30 | −2,055 | **none — (lA) 11:45 fails band, scan ends; (lC) no passing candidate by 12:30** | **−2,055 (was −3,445 under (k))** |
| 2026-04-02 | −2,065 | 11:25, risk 16.25 → stop −1,665 | −3,730 |
| 2026-05-13 | −5,075 | none — no bar closes < OR low after the 09:55 stop at any time to 15:05 | −5,075 |
| 2026-06-29 | −4,740 | 11:30, risk 34.40 → target +6,840 | +2,100 GREEN |
| 2026-07-08 | −1,985 | 12:05, risk 14.90 → target +2,940 | +955 GREEN |
| 2026-08-19 | −2,300 | 10:15, risk 20.05 → target +3,970 | +1,670 GREEN |

Day-by-day, (lB) — only 30 Mar differs from (k):

| Date | Rescan morning | Re-entry → result | Day net |
|---|---|---|---|
| 2026-03-30 | −2,055 | **14:25, risk 17.85 (ratio 0.886) → stop −1,825** (13:55 ratio 0.670 and 14:15 ratio 0.645 skipped under scan-skip; 14:00/14:05/14:10/14:20 fail the band) | **−3,880 (worse than (k) −3,445 by ₹435)** |
| all other 7 days | as (k) | as (k) | as (k) |

Why (l) does and does not help: (lA) and (lC) do exactly what the
task asked — they avoid the 30 Mar afternoon stop without losing the
8 Jul afternoon green — but avoiding one −₹1,390 stop only moves the
cluster from −₹4,110 to −₹2,720. The three remaining losses under
(lA)/(lC) still total −₹10,860 (30 Mar −₹2,055, 2 Apr −₹3,730,
13 May −₹5,075) against five greens totalling +₹8,140. No (l) variant
creates a new green, because the only afternoon re-entries in (k) are
30 Mar (a stop) and 8 Jul (already green). (lB) is the cautionary
version: a ratio condition under scan-skip does not delete the
afternoon trade, it moves it to a later, larger stop (14:25, −₹1,825),
so (lB) is worse than (k). A ratio condition would only equal (lA)
if it were also stop-on-first-fail — in which case it is (lA) with a
different label, not a separate rule.

## Results — (m), Cluster 1 (partial/trail on the re-entry)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| (m1) partial50_trailBE, Cluster 1 | 4/8 day | 0 | 4 | −11,330 | No — worse than (k) on both legs |
| (m1) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (m1) Combined PE | — | — | — | +72,050 | No |
| (m2) partial50_noTrail, Cluster 1 | 5/8 day | 0 | 3 | −9,840 | No — same greens as (k), total worse |
| (m2) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (m2) Combined PE | — | — | — | +73,540 | No |
| (m3) partial25_trailBE, Cluster 1 | 3/8 day | 0 | 5 | −14,195 | No — worst in this sweep |
| (m3) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (m3) Combined PE | — | — | — | +69,185 | No |

Day-by-day, (m2) (the least-bad (m) variant; (m1)/(m3) differences noted
below):

| Date | Rescan morning | Partial re-entry → result | Day net |
|---|---|---|---|
| 2026-01-09 | −3,745 | 10:50, partial 11:10, target after partial +4,520 (was +6,040) | +775 GREEN |
| 2026-02-06 | −1,810 | 10:20, partial+target same bar 10:25 +2,187.50 (was +2,930) | +377.50 GREEN |
| 2026-03-30 | −2,055 | 13:55 → stop −1,390, partial NEVER triggers | −3,445 |
| 2026-04-02 | −2,065 | 11:25 → stop −1,665, partial NEVER triggers | −3,730 |
| 2026-05-13 | −5,075 | none | −5,075 |
| 2026-06-29 | −4,740 | 11:30, partial 12:10, target after partial +5,120 (was +6,840) | +380 GREEN |
| 2026-07-08 | −1,985 | 12:05, partial 12:15, target after partial +2,195 (was +2,940) | +210 GREEN |
| 2026-08-19 | −2,300 | 10:15, partial 10:35, target after partial +2,967.50 (was +3,970) | +667.50 GREEN |

Why (m) cannot help, and why it hurts: the premise was "an afternoon
re-entry that moves most of the way to target banks something instead
of reversing to a full stop". The two stopping re-entries do not move
most of the way anywhere — their maximum favourable excursion (MFE)
is 30 Mar 4.35 points (16.1% of its 27.00-point target distance) and
2 Apr 2.80 points (8.6% of its 32.50-point target distance), and both
stop on the entry bar itself (30 Mar 14:00 high 22,487.20 ≥ stop
22,441.60; 2 Apr 11:30 high 22,224.10 ≥ stop 22,222.75). A 50% partial
trigger (1.0×risk: 13.50 / 16.25 points) and even a 25% partial trigger
(0.5×risk: 6.75 / 8.125 points) are never reached on either day, so
(m) changes nothing on the days it was meant to fix. On the five
winning re-entries it only shrinks the payoff (150×risk or 125×risk
instead of 200×risk), and (m1)/(m3) additionally flip 8 Jul: under
(m1) the 12:05 re-entry books its 50% partial at 12:15 (+₹745) but the
12:20 bar high (24,234.25) hits the trailed breakeven stop (entry
24,229.00) before the 12:30 target, so the re-entry nets only +₹705
and the day falls to −₹1,280 (green lost); under (m3) the same trail
gives a +₹332.50 re-entry and a −₹1,652.50 day. (m2) keeps all five
(k) greens but at −₹9,840, ₹5,730 worse than (k) — the exact sum of
the five partial shrinkages. Partial/trail on the re-entry is therefore
exhausted as a family on Cluster 1: it creates zero new greens and, in
its trailed forms, destroys one.

## Results — (n), Cluster 1 (morning-loss cap)

| Set | Green | No-trade | Still loss | Total (₹) | Pass? |
|---|---|---|---|---|---|
| (n1) cap >₹4,000, Cluster 1 | 4/8 day | 0 | 4 | −10,950 | No — deletes a working green |
| (n1) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (n1) Combined PE | — | — | — | +72,430 | No |
| (n2) cap >₹3,000, Cluster 1 | 3/8 day | 0 | 5 | −16,990 | No — deletes two working greens |
| (n2) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (n2) Combined PE | — | — | — | +66,390 | No — below baseline combined +₹66,980 |
| (n3) afternoon cap >₹2,000, Cluster 1 | 5/8 day | 0 | 3 | −2,720 | No — green bar met, total still negative |
| (n3) Winners | 12/14 | 2 | 0 | +83,380 | — (inert) |
| (n3) Combined PE | — | — | — | +80,660 | No — below RF-BAND-SCAN +₹83,845 |

Day-by-day differences from (k) only (all other days as (k)):

- **(n1):** 29 Jun re-entry skipped (|morning| ₹4,740 > ₹4,000) →
  day −₹4,740 instead of +₹2,100 (green lost, −₹6,840 swing);
  13 May cap also fires (|morning| ₹5,075) but 13 May has no re-entry
  under (k) anyway, so no change there. Total −₹10,950.
- **(n2):** 9 Jan re-entry skipped (|morning| ₹3,745 > ₹3,000) →
  day −₹3,745 instead of +₹2,295 (green lost, −₹6,040 swing), plus
  the (n1) 29 Jun loss. Total −₹16,990.
- **(n3):** 30 Mar afternoon re-entry skipped (|morning| ₹2,055 >
  ₹2,000) → day −₹2,055 instead of −₹3,445; 8 Jul afternoon re-entry
  kept (|morning| ₹1,985 ≤ ₹2,000) → +₹955 unchanged. Total −₹2,720,
  identical to (lA)/(lC) on every day.

Why (n) fails as a general rule, and what (n3) really is: a
morning-loss cap punishes exactly the days whose re-entries work —
the largest morning losses (9 Jan, 29 Jun) are the days with the
largest re-entry targets, because the band ties re-entry risk to
rescan risk. Capping re-entries by morning loss therefore deletes
greens faster than it avoids stops. The task's motivating cases do
not support the cap either: 13 May's −₹5,075 morning loss is a case
where the cap fires but changes nothing, because (k) finds no
re-entry candidate on 13 May at all (no bar closes below OR low after
the 09:55 stop, to 15:05); and 30 Mar's afternoon −₹1,390 is not a
morning loss at all, so a morning-loss cap only touches it in the
(n3) afternoon-only, ₹2,000-threshold form — which is (lA)/(lC) by
another name, fitted on a ₹70 gap (₹2,055 vs ₹1,985). (n3) must not
be presented as an independent confirmation of (lA)/(lC): three rules
converging on the same two afternoon days is one observation, not
three.

## Clusters 2 and 3 — not applied

Condition in the task: apply a variant to Clusters 2/3 only if it
reaches 60% on Cluster 1 WITH positive economics. (lA)/(lC)/(n3)
reach 60% green but their Cluster 1 total is negative (−₹2,720), so
the condition is not met; (lB), (m1)–(m3), (n1), (n2) fail both legs.
No variant is carried into Cluster 2 (reclaim failure, 2 trades,
−₹11,420) or Cluster 3 (slow give-back, 3 trades, −₹10,585) as a fix.
For the record: (l)–(n) are PE-breakdown re-entry rules and would not
in any case apply to Cluster 2's CE reclaim trades without a mirrored
(long-side) definition, which was not tested here.

## Variant summary — families (l)–(n) in this task, pass bar applied

| Family / variant | Green | Cluster 1 total (₹) | Winners (₹) | Combined (₹) | Pass? |
|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | +91,270 | +66,980 | — |
| RF-BAND-SCAN (reference, prior best combined) | 3/8 day | −7,425 | +91,270 | +83,845 | No — prior ceiling on combined |
| (d) Rescan morning + band re-entry (reference) | 4/8 day | −5,660 | +83,380 | +77,720 | No |
| (k) (d) + re-entry window to 15:05 (prior ceiling) | 5/8 day | −4,110 | +83,380 | +79,270 | No — green bar met, total negative |
| (lA) (k) + afternoon stop-on-first-fail | 5/8 day | −2,720 | +83,380 | +80,660 | No — green bar met, total still negative; NEW least-negative ceiling |
| (lB) (k) + afternoon risk-ratio ≥0.70 (scan-skip) | 5/8 day | −4,545 | +83,380 | +78,835 | No — worse than (k) |
| (lC) (k) + afternoon window to 12:30 only | 5/8 day | −2,720 | +83,380 | +80,660 | No — same outcome as (lA) |
| (m1) (k) + partial50_trailBE on re-entry | 4/8 day | −11,330 | +83,380 | +72,050 | No — flips 8 Jul green to loss |
| (m2) (k) + partial50_noTrail on re-entry | 5/8 day | −9,840 | +83,380 | +73,540 | No — same greens, shrunk payoffs |
| (m3) (k) + partial25_trailBE on re-entry | 3/8 day | −14,195 | +83,380 | +69,185 | No — flips 29 Jun and 8 Jul greens |
| (n1) (k) + skip any re-entry, \|morning\| >₹4,000 | 4/8 day | −10,950 | +83,380 | +72,430 | No — deletes 29 Jun green |
| (n2) (k) + skip any re-entry, \|morning\| >₹3,000 | 3/8 day | −16,990 | +83,380 | +66,390 | No — deletes 9 Jan and 29 Jun greens |
| (n3) (k) + skip afternoon re-entry, \|morning\| >₹2,000 | 5/8 day | −2,720 | +83,380 | +80,660 | No — same outcome as (lA)/(lC), knife-edge threshold |

## What this sweep proves, and what it does not

- The 30 Mar afternoon stop is avoidable three ways with the same
  outcome, but avoiding it is worth exactly ₹1,390 and creates no new
  green. Under the best (l) outcome the remaining Cluster 1 problem is
  fully enumerated: three losses, −₹10,860 (30 Mar −₹2,055, 2 Apr
  −₹3,730, 13 May −₹5,075) against five greens, +₹8,140. Any future
  variant must either convert one of those three losses or avoid one
  of them without losing a green — avoiding the 30 Mar afternoon stop
  was the last avoidance available inside the re-entry family, because
  13 May has no re-entry candidate at all and 2 Apr's re-entry stop is
  a morning-phase trade, not an afternoon one.
- Partial/trail on the re-entry is dead on Cluster 1 for a structural
  reason (stopping re-entries stop on the entry bar with 8–16% MFE,
  below any partial trigger), not because the trigger was mis-tuned:
  even a 25% trigger misses both stopping re-entries, while trailed
  partials flip the 8 Jul green. Do not re-propose re-entry partials
  without first explaining how they would survive an entry-bar stop.
- A general morning-loss cap is dead as a re-entry rule: it deletes
  the working re-entries on the largest-loss days. (n3) survives only
  as a relabelling of (lA)/(lC) on a ₹70 threshold gap.
- What remains untested for Cluster 1 after this sweep — the next
  family, NOT a re-run of the above: **(o) (lA)/(lC) combined with a
  partial/trail exit on the MORNING trade only** (distinct from (m),
  which was re-entry only). The motivating case is checked bar by bar
  here as a hypothesis, not as a result: on 13 May the rescan morning
  (entry 23,337.30, risk 50.35, partial level 23,286.95) books its 50%
  partial on the entry bar itself (09:35 low 23,262.55 ≤ 23,286.95,
  high 23,339.35 < stop 23,387.65), the remaining leg then exits at
  breakeven on the 09:50 bar (high 23,372.45 ≥ entry 23,337.30), for a
  morning net of 50 × 50.35 − ₹40 = **+₹2,477.50** instead of −₹5,075
  — a +₹7,552.50 swing on that day alone, which, if the other mornings
  did not shrink by more than that, would take the (lA) total from
  −₹2,720 to positive. That "if" is exactly what (o) must test day by
  day: partials shrink every winning morning (150×risk or 125×risk
  instead of 200×risk), and a trailed morning partial can flip a
  morning target the way (m1) flipped the 8 Jul re-entry. (o) must
  therefore be run on the rescan mornings under (lA), one day at a
  time, with the same pass bar — it is the next family, not a claimed
  pass, and no (l)–(n) variant in this report is adopted.

Files: engine `extended_window_sweep.py`, raw replay
`extended_window_sweep_raw.json`. Paper only throughout; no orders
placed, nothing fabricated. The long-horizon task continues in the
parent conversation: families (l)–(n) in this report are exhausted,
and the next decision is the (o) morning-partial combination — and
none of the variants in this report is adopted.
