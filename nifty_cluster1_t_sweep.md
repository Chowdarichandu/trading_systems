# NIFTY — Family (t): bounce-bar-aware stops + morning-bar structure + new Cluster 2 ideas — NO PASS, nothing adopted

## Paper only, no orders, no live-trading recommendation. Long-horizon task continues — this is NOT completion.

## Task and frozen definitions

Family (s) is done: no pass, nothing adopted. c2-A was **discarded** on
held-out 2025 reclaim trades (0/3 green, kills the 6 Jun winner), and the
pure thin-signal no-trade converted **0** failing days. Previous best kept
is still (lA) on Cluster 1 (−₹2,720, 5/8 day-green) with winners intact,
and (lA) itself is **not** adopted. Cluster 3 survival N=10 (3/3,
+₹4,589.25) remains the best scoped result for Cluster 3 only, combined
below baseline.

Pass bar, same as (p)/(q)/(r)/(s): **60% green on the failing set AND
total positive AND combined NOT below (lA) on the same window, winners
not collapsed.** Green = net > ₹0. **No-trade is counted separately from
green throughout — a filter can only avoid, never convert, and a total
improved only by avoiding trades is reported as avoidance, not
conversion.** 100 shares equivalent, ₹40/trade, square-off 15:10, stop
checked before target on each bar except where a variant states
otherwise.

Engine: `t_sweep.py`, raw replay `t_sweep_raw.json`, replayed bar by bar
from the Upstox 5-min cache. (lA) baseline reproduced by the engine, not
copied: Cluster 1 5/8 green, −₹2,720; winners 12/14 green, 2 no-trade,
+₹83,380; combined **+₹80,660**. Nothing fabricated. No (p) cutoff was
re-run, no second-close hold variant was re-run, no (s) rule was re-run
on a new window.

## Part 1 — A stop that survives the bounce bar itself

Base: (lA) BN-confirmed rescan morning. Entry = open of the bar after
the signal, stop = signal high (PE), target = entry − 2×risk. The
**bounce bar is the entry bar** (the bar after the signal). On the two
untouched days the morning stops in that entry bar with 0 MFE, so a stop
that survives it is the precise thing to test — but "survives" must be
defined, with its widened risk and recomputed target stated up front,
and judged on conversions. If a variant morning stops, the (lA)
re-entry scan runs with its band cap set to the **variant** risk
(stated, not hidden); if the variant morning does not stop, the day
closes, as in (lA).

Variants, defined before results:

- **t1 arm1:** stop ignored on the entry bar only; same stop/target
  after.
- **t2 bounce-high:** stop = entry-bar high, target recomputed at
  entry − 2×new risk, stop arms from the bar **after** the entry bar
  (otherwise it would stop on the entry bar itself by construction).
  New risk is bar-specific, stated per day below.
- **t3 arm2:** stop ignored on the entry bar AND the next bar; same
  stop/target after.
- **t4 arm2-bounce-high:** stop = entry-bar high, target recomputed,
  stop arms from 2 bars after the entry bar.
- **t5 close-stop:** stop checked ONLY on a 5-min CLOSE ≥ stop, whole
  trade (exit at the close, so the loss can exceed the original risk);
  target checked intra-bar first on each bar, as in the close-trail
  families; square-off 15:10.
- **t6 bounce-high-target-kept (diagnostic):** stop = entry-bar high,
  target **kept** at the original target. This isolates widening from
  farther target — and shows why widening alone destroys reward/risk.

t2/t4/t6 are **not** the +10/+20 buffers and **not** the OR-high stop:
the new stop is exactly the bounce (entry) bar's high, a bar-specific
extreme. That distinction matters, because on winner days the entry-bar
high sits almost on top of the entry (see below) — a bounce-high stop
is a tiny stop on winners and a large stop on losers, the worst
possible asymmetry.

### Part 1 results — Cluster 1 (8) + PE winners (14)

| Variant | Cluster 1 green / no-trade / total | Winners green / no-trade / total | Combined | vs (lA) +₹80,660 | Pass? |
|---|---|---|---|---|---|
| (lA) reference | 5/8 / 0 / −₹2,720 | 12/14 / 2 / +₹83,380 | +₹80,660 | — | Reference, total negative |
| **t1 arm1** | 4/8 / 0 / −₹6,740 | 12/14 / 2 / +₹83,380 | +₹76,640 | −₹4,020 | **No** |
| **t2 bounce-high, target recomputed** | 4/8 / 0 / −₹15,335 | 10/14 / 3 / +₹10,000 | −₹5,335 | −₹85,995 | **No — catastrophic on winners** |
| **t3 arm2** | 4/8 / 0 / −₹6,740 | 12/14 / 2 / +₹83,380 | +₹76,640 | −₹4,020 | **No — identical totals to t1** |
| **t4 arm2-bounce-high** | 4/8 / 0 / −₹16,195 | 10/14 / 3 / +₹10,000 | −₹6,195 | −₹86,855 | **No** |
| **t5 close-stop** | 3/8 / 0 / −₹10,105 | 12/14 / 2 / +₹83,380 | +₹73,275 | −₹7,385 | **No** |
| **t6 bounce-high, target kept (diagnostic)** | 1/8 / 0 / −₹18,050 | 6/14 / 3 / +₹1,330 | −₹16,720 | −₹97,380 | **No — worst in (t)** |

### Part 1 day detail — Cluster 1

(lA) day nets for reference: 9 Jan +₹2,295, 6 Feb +₹1,120, 30 Mar
−₹2,055, 2 Apr −₹3,730, 13 May −₹5,075, 29 Jun +₹2,100, 8 Jul +₹955,
19 Aug +₹1,670.

**t1 arm1 — the untouched days still stop, one bar later, and 6 Feb
flips green → loss.** 30 Mar morning stops 11:35 (was 11:30) for the
same −₹2,055, no re-entry; 2 Apr morning stops 10:55 for the same
−₹2,065, re-entry −₹1,665, day −₹3,730 unchanged. The bounce is not a
one-bar event that ends at the entry bar's close: the next bar still
highs above the signal high on both untouched days. Worse, delaying
the morning stop by one bar shifts the (lA) re-entry scan start past
the working re-entry bar on 6 Feb: (lA) re-entry +₹2,930 becomes
−₹1,090, day +₹1,120 → −₹2,900, a −₹4,020 swing that is the whole
combined shortfall. Winners are untouched (no winner morning stops),
so t1's failure is purely this one mechanism. **Conversions on the
(lA) failing set (30 Mar, 2 Apr, 13 May): 0/3.**

**t3 arm2 — identical totals to t1.** Same day nets on all 8 days
(stop times move to 09:45/10:25/11:40/11:00 on the stopping mornings,
nets unchanged). A two-bar arm does not outlast the bounce either,
and it does not change any re-entry outcome versus t1. Arming longer
is not the answer; the bounce runs 1–5 bars and the stop level itself
is the problem, not the arming window.

**t2 bounce-high — the asymmetry, in numbers.** New risks on
Cluster 1: 9 Jan 12.55 (was 37.05), 6 Feb 37.40 (was 17.70), 30 Mar
38.20 (was 20.15), 2 Apr 32.60 (was 20.25), 13 May 2.05 (was 50.35),
29 Jun 44.40 (was 47.00), 8 Jul 3.35 (was 19.45), 19 Aug 3.65 (was
22.60). On the untouched days the bounce-high stop is **larger**
than the original stop, so both mornings stop for more (−₹3,860 and
−₹3,300) and their re-entries also stop (days −₹5,965 and −₹4,965).
On three other Cluster 1 days the bounce-high stop is **tiny**, so
the morning "targets" are degenerate: 13 May +₹370 (risk 2.05,
target 4.10 points), 8 Jul +₹630 (risk 3.35), 19 Aug +₹690 (risk
3.65) — tiny-risk artefacts, not conversions, and they must not be
counted as meaningful greens the way the Z-degenerate targets were
rejected in the stop sweep. The (lA) failing set conversion is
therefore 1/3 at most (13 May, tiny), and Cluster 1 total is far
worse. On winners the damage is the mirror image: entry-bar highs
sit 0.50–13.00 points above entry on most winner days, so targets
collapse to 1–26 points and winner total falls from +₹83,380 to
+₹10,000; 13 Mar becomes an invalid-risk no-trade (entry-bar high
exactly equals entry, risk 0.00) and 8 Oct flips target → stop
(−₹3,350). **A bounce-high stop is untradeable as a general rule:
it widens exactly where the trade is already losing and shrinks
exactly where it is winning.**

**t4 arm2-bounce-high — same story, slightly worse.** Cluster 1
−₹16,195 (2 Feb re-entry worsens to −₹3,095, day −₹6,875); winners
identical to t2 (+₹10,000). Arming a second bar changes nothing
once the stop itself is the bounce high.

**t5 close-stop — losses grow, greens fall.** Close-only stop
exits at the close, which has already overshot the stop: 29 Jun
morning −₹7,570 (was −₹4,740), 13 May −₹5,555 (was −₹5,075),
30 Mar −₹3,610 (was −₹2,055), 2 Apr morning −₹2,215 (was
−₹2,065). Cluster 1 greens fall 5 → 3 (29 Jun flips to −₹730
despite a +₹6,840 re-entry; 6 Feb becomes −₹15, a near-scratch
day). Winners are unchanged (their targets hit before any
close-stop matters), so t5's failure is again purely on the losing
side: a close stop is a later, larger stop, not a surviving stop.
**Conversions on the (lA) failing set: 0/3.**

**t6 diagnostic — the cleanest proof in (t).** Keeping the original
(far) target while widening the stop to the bounce high gives
Cluster 1 1/8, −₹18,050 and winners 6/14, +₹1,330. Winners that
would have run to a 2× target on a 12–58 point risk now stop at a
0.50–13 point bounce-high stop long before the far target. This is
not a candidate; it is the control that shows t2's recomputed
target is the only reason t2 keeps any winner value at all, and
even with it, t2 collapses.

### Part 1 verdict

**No bounce-bar stop passes, and none converts an untouched day to
a genuine green.** Arming (t1/t3) delays the stop by one or two
bars and costs a working re-entry; bounce-high stops (t2/t4) are
asymmetric in the wrong direction; close stops (t5) pay more for
the same losses. The bounce-bar stop family is exhausted as a
Cluster 1 fix — do not re-propose "ignore the entry bar", "stop
beyond the entry bar high", or "stop on close" without explaining
why they would not repeat t1's re-entry shift, t2's winner
collapse, or t5's overshoot.

## Part 2 — Morning-bar structure beyond thinness

Features computed on the **(lA) signal bars** (rescan signals, not
plain signals — thin status is scope-sensitive, as (s) showed), for
Cluster 1 (8) + PE winners (14). Gap = day open vs previous close.
Below-PDL = previous-day low minus signal close. OR width/scale =
(OR high − OR low) / (prev close / 55,000).

| Date | Signal | Gap % | Below-PDL | OR width / scale | Sig range | (lA) day net |
|---|---|---|---|---|---|---|
| 2026-01-09 (C1) | 09:30 | −0.110 | 21.30 | 215.7 | 52.30 | +₹2,295 |
| 2026-02-06 (C1) | 10:10 | −0.140 | 63.70 | 165.7 | 28.90 | +₹1,120 |
| **2026-03-30 (untouched)** | 11:25 | **−1.269** | **336.35** | **356.2** | 22.45 | −₹2,055 |
| **2026-04-02 (untouched)** | 10:45 | **−1.408** | **412.25** | **449.4** | 35.65 | −₹3,730 |
| 2026-05-13 (C1) | 09:30 | −0.291 | 10.45 | 331.8 | 51.95 | −₹5,075 |
| 2026-06-29 (C1) | 09:30 | +0.037 | 21.90 | 179.3 | 48.90 | +₹2,100 |
| 2026-07-08 (C1) | 09:30 | −0.392 | 128.90 | 147.6 | 25.60 | +₹955 |
| 2026-08-19 (C1) | 09:30 | −0.012 | 81.05 | 181.7 | 27.25 | +₹1,670 |
| 2026-01-21 (W) | 10:20 | −0.334 | 65.50 | 321.8 | 48.85 | +₹9,280 |
| 2026-03-16 (W) | 10:20 | −0.237 | 55.30 | 356.2 | 45.50 | +₹8,940 |
| 2026-03-13 (W) | 09:45 | −0.748 | 158.90 | 169.0 | 38.40 | +₹5,400 |
| **2026-03-23 (W)** | 09:50 | **−1.341** | **438.55** | **516.2** | 40.30 | **+₹7,260** |
| 2026-04-24 (W) | 09:30 | −0.230 | 117.15 | 340.2 | 49.70 | +₹8,820 |
| 2026-05-05 (W) | 10:30 | −0.295 | 63.40 | 279.7 | 28.70 | +₹5,040 |
| 2026-07-22 (W) | 09:30 | −0.176 | 111.40 | 271.3 | 36.15 | +₹6,320 |
| 2026-08-27 (W) | 10:40 | +0.289 | 38.65 | 225.2 | 18.40 | +₹2,980 |
| 2026-09-29 (W) | 09:30 | −0.210 | 142.45 | 311.5 | 27.35 | +₹3,790 |
| 2026-09-07 (W) | 10:10 | −0.061 | 89.40 | 164.6 | 14.55 | +₹2,470 |
| 2026-10-08 (W) | 11:25 | −0.018 | 208.15 | 300.0 | 70.80 | +₹11,690 |
| 2026-10-23 (W) | 10:05 | +0.240 | 31.80 | 212.2 | 62.80 | +₹11,390 |

Two features come **closest** to separating the untouched days, and
both are blocked by exactly one winner:

- **Gap < −1.25%:** untouched −1.269% and −1.408%; every winner
  except 23 Mar (−1.341%) is ≥ −0.748%. The gap feature separates
  21 of 22 days and fails on one.
- **Below-PDL > 300 points:** untouched 336.35 and 412.25; every
  winner except 23 Mar (438.55) is ≤ 208.15. Same single blocker.
- **OR width/scale > 350:** untouched 356.2 and 449.4, but winners
  16 Mar (356.2, exactly 30 Mar's value) and 23 Mar (516.2) also
  pass — two blockers, worse.
- Previous-day range (untouched 381.55 / 322.70) and signal range
  (22.45 / 35.65) overlap winners widely and separate nothing.

Filters applied as **pure (lA) no-trades** (day removed entirely,
no rescan, no later signal — so by construction they convert 0
days):

| Filter | Cluster 1 kept green / total | Winners kept green / total | Combined | vs (lA) +₹80,660 | Removed |
|---|---|---|---|---|---|
| Gap < −1.25% | 5/8, +₹3,065 | 11/14, +₹76,120 | +₹79,185 | −₹1,475 | 30 Mar, 2 Apr, **23 Mar winner (+₹7,260)** |
| Below-PDL > 300 | 5/8, +₹3,065 | 11/14, +₹76,120 | +₹79,185 | −₹1,475 | Same three days |
| Gap AND below-PDL | 5/8, +₹3,065 | 11/14, +₹76,120 | +₹79,185 | −₹1,475 | Same three days |
| OR width/scale > 350 | 5/8, +₹3,065 | 10/14, +₹67,180 | +₹70,245 | −₹10,415 | 30 Mar, 2 Apr, 16 Mar (+₹8,940), 23 Mar (+₹7,260) |
| Gap AND OR width/scale | 5/8, +₹3,065 | 11/14, +₹76,120 | +₹79,185 | −₹1,475 | Same as gap alone |

**Conversion reading (required):** the (lA) failing set is 30 Mar,
2 Apr, 13 May. Every filter above converts **0/3** — 30 Mar and
2 Apr become no-trades, 13 May (−₹5,075) still loses, and the 5/8
green figure is the baseline greens preserved, not new greens.
Unlike (s)'s thin+narrow (lA) filter, which at least rose ₹1,995
above (lA) by killing only the cheaper 29 Sep winner (+₹3,790),
the gap/below-PDL filters **fall** ₹1,475 below (lA) because the
single blocking winner (23 Mar, +₹7,260) costs more than the two
avoided losses save on the (lA) day-net basis (−₹2,055 − ₹3,730
= −₹5,785 avoided, but the day nets already include re-entry
greens elsewhere, so the honest comparison is the combined total).
**Morning-bar structure beyond thinness therefore fails like
thinness did: the untouched shape is a deep-gap-down,
far-below-previous-low morning, and the only winner that shares
that shape (23 Mar, a skill-mode winner) is exactly the trade a
filter must not kill.** No feature in this table separates the
untouched days from 23 Mar; a future discriminator must first
explain what distinguishes 23 Mar from 30 Mar / 2 Apr on some
other axis, or it will repeat this failure.

## Part 3 — Cluster 2 needs a new idea, not a stronger hold

No second-close hold variant is re-run (c2-A discarded, c2-E
collapses on 0.15 points). Six new ideas, each tested on the 2026
fitted set **and** the 2025 held-out set in the same report.
Reclaim level L = max(OR high, previous close). Original Cluster 2
trades: 2026 — 14 Jan −₹2,785 (risk 27.45), 26 Oct −₹8,635 (risk
85.95, the outlier), 1 Jul winner +₹4,240 (risk 21.40), total
−₹7,180. 2025 held-out — 20 Feb −₹1,215 (risk 11.75), 6 Jun winner
+₹22,260 (risk 111.50), 1 Aug −₹2,310 (risk 22.70), total +₹18,735.

### New ideas, defined before results

- **BN-ORH:** trade only if Bank Nifty's close on the signal bar
  is above Bank Nifty's OR high, else no-trade.
- **BN-prev:** trade only if Bank Nifty's close on the signal bar
  is above Bank Nifty's previous close, else no-trade.
- **TIME1030:** trade only if the signal bar is ≤ 10:30, else
  no-trade.
- **RISKCAP30 / RISKCAP50:** no-trade if original risk > 30 / 50
  points, else original trade.
- **RISKSIZE30:** shares scaled to a 30-point risk cap — 100 shares
  if risk ≤ 30, else floor(100×30/risk) shares, ₹40 cost flat;
  exit type unchanged, net recomputed on the scaled shares.
- **STOPL:** stop = reclaimed level L (instead of signal low),
  target recomputed at entry + 2×(entry − L), entry unchanged.
  Flagged knife-edge where entry − L < 10 points.
- **RETESTL:** after the signal, first bar whose low touches L
  (low ≤ L) becomes the confirmation bar; entry = next bar open,
  stop = touch-bar low, target recomputed at 2× new risk; no touch
  → no-trade. This is **not** a second-close hold: it requires a
  pullback touch of L, not a second close above it.

### Part 3 results — 2026

| Variant | 14 Jan | 26 Oct | 1 Jul winner | Failing green | Total | Pass? |
|---|---|---|---|---|---|---|
| Original | −₹2,785 | −₹8,635 | +₹4,240 | 0/2 | −₹7,180 | — |
| BN-ORH | no-trade | no-trade | **no-trade (winner killed)** | 0/2 | ₹0 | No — avoidance only, kills winner |
| BN-prev | −₹2,785 | no-trade | **no-trade (winner killed)** | 0/2 | −₹2,785 | No |
| TIME1030 | no-trade | −₹8,635 | +₹4,240 | 0/2 | −₹4,395 | No — avoidance only |
| RISKCAP30 / RISKCAP50 (identical here) | −₹2,785 | no-trade | +₹4,240 | 0/2 | **+₹1,455** | No — positive total, **0 conversions**, best 2026 total in (t) but not a pass |
| RISKSIZE30 | −₹2,785 | −₹2,962 (34 sh) | +₹4,240 | 0/2 | −₹1,507 | No — shrinks the loss, does not green it |
| STOPL | −₹335 (risk 2.95, knife) | −₹3,610 (risk 35.70) | **−₹430 (winner flipped to loss, risk 3.90, knife)** | 0/2 | −₹4,375 | No — worst idea: kills the winner |
| RETESTL | −₹80 (risk 0.40, knife) | **+₹570 (risk 3.05, knife)** | +₹3,890 | 1/2 | +₹4,380 | No — 50% < 60%, and the one "conversion" is a 3.05-point-risk artefact |

BN detail (2026): BN above OR high is −46.15 (14 Jan), −87.70
(26 Oct), −64.65 (1 Jul) — **all three below**, so BN-ORH removes
the whole 2026 reclaim set. BN above previous close is +68.60
(14 Jan, loser passes), −17.45 (26 Oct, loser avoided), −90.50
(1 Jul, winner killed) — it separates nothing in the right
direction.

**RETESTL warning, stated plainly:** its 26 Oct "conversion" is
entry 22,591.20, stop 22,588.15, risk **3.05 points**, target 6.10
points, net +₹570 — the same class of knife-edge artefact as
c2-A's 1 Aug 2025 trade (risk 1.80). A 3-point stop is not a
tradeable retest confirmation, and 14 Jan's retest is even thinner
(risk 0.40, net −₹80). Counting RETESTL as a Cluster 2 fix would
repeat the exact error (s) warned against. It is recorded as
1/2 green with a knife-edge caveat, not as a scoped pass.

### Part 3 results — 2025 held-out (same variants, same definitions)

| Variant | 20 Feb | 6 Jun winner | 1 Aug | Failing green | Total | vs original +₹18,735 |
|---|---|---|---|---|---|---|
| Original | −₹1,215 | +₹22,260 | −₹2,310 | 0/2 | +₹18,735 | — |
| BN-ORH | no-trade | +₹22,260 | −₹2,310 | 0/2 | +₹19,950 | +₹1,215 — avoidance only, winner preserved |
| BN-prev | no-trade | +₹22,260 | −₹2,310 | 0/2 | +₹19,950 | +₹1,215 — same pattern |
| TIME1030 | no-trade (13:50) | +₹22,260 | −₹2,310 | 0/2 | +₹19,950 | +₹1,215 — avoidance only |
| RISKCAP30 / RISKCAP50 | −₹1,215 | **no-trade (winner killed, risk 111.50)** | −₹2,310 | 0/2 | −₹3,525 | −₹22,260 — risk cap kills the biggest winner |
| RISKSIZE30 | −₹1,215 | +₹5,758 (26 sh) | −₹2,310 | 0/2 | +₹2,233 | −₹16,502 — winner preserved in count, gutted in value |
| STOPL | −₹330 (knife 2.90) | **−₹3,075 (winner flipped to loss)** | −₹1,375 | 0/2 | −₹4,780 | −₹23,515 — worst |
| RETESTL | −₹830 | +₹5,230 | −₹1,375 | 0/2 | +₹3,025 | −₹15,710 — winner shrunk, losers still lose |

BN detail (2025): BN above OR high is −62.80 (20 Feb, loser
avoided), +63.45 (6 Jun, winner kept), +98.25 (1 Aug, loser kept)
— BN confirmation looks good in 2025 and fails in 2026, which is
exactly why a cross-year test is required: a rule that preserves
the winner in one year and kills it in the other is not a
discriminator. TIME1030 has the same shape (late-signal loser
avoided in both years, winner kept in both years, other loser
kept in both years) — it is the cheapest avoidance in (t), not a
conversion.

**Risk-size verdict, both years together:** a risk cap is the
mirror image of a distance filter — in 2026 it removes the 85.95
outlier and turns the total positive (+₹1,455), in 2025 it removes
the 111.50 winner and turns the total deeply negative (−₹3,525).
Risk-size scaling preserves green counts in both years but guts
the 2025 winner (+₹22,260 → +₹5,758) while leaving both 2025
losers as full losses. Neither form converts a failing reclaim
trade: **across both years, every Part 3 variant converts 0/4
failing reclaim trades to a genuine (non-knife-edge) green,
except RETESTL's single 3.05-point artefact.** The 85.95-point
October outlier is a risk problem, not a confirmation problem —
but capping or scaling that risk also caps or kills the
111.50-point winner, because on this data large risk is not
itself the loser marker.

### Part 3 verdict

**No new Cluster 2 idea passes.** BN confirmation, time box,
risk cap, risk sizing, stop-at-L, and retest-of-L all fail the
60%-on-failing-set bar as genuine conversions. The best honest
results are scoped avoidances (TIME1030 / BN-ORH in 2025,
RISKCAP in 2026), each contradicted by the other year. STOPL is
actively harmful (flips both years' winners to losses). RETESTL
is not adopted: its only conversion rests on a 3.05-point risk.

## Verdict — family (t) exhausted, nothing adopted

| Part | Best variant | Best result | Pass? |
|---|---|---|---|
| 1 — Bounce-bar stops | t1 / t3 arm1 / arm2 | Cluster 1 4/8, −₹6,740; combined +₹76,640 (below (lA) by ₹4,020); 0/3 conversions on the (lA) failing set | No |
| 1 — Bounce-high stops | t2 | Cluster 1 4/8, −₹15,335; winners +₹10,000; combined −₹5,335 | No — catastrophic |
| 2 — Morning-bar structure | Gap < −1.25% / below-PDL > 300 | Cluster 1 5/8 preserved, +₹3,065; winners 11/14, +₹76,120; combined +₹79,185 (below (lA)); 0/3 conversions; single blocker 23 Mar (+₹7,260) | No — avoidance, not a fix |
| 3 — Cluster 2 new ideas | RISKCAP (2026) / TIME1030 (2025) | 2026 +₹1,455 with 0 conversions; 2025 +₹19,950 with 0 conversions; RETESTL 1/2 in 2026 on a 3.05-pt risk | No |

- **No (t) variant passes** the full bar (60% green on the failing
  set AND total positive AND combined NOT below (lA), winners not
  collapsed) as a genuine conversion fix.
- **Nothing is adopted.** Previous best kept is still (lA)
  (−₹2,720, 5/8) with winners intact, and (lA) itself is not
  adopted. Cluster 3 survival N=10 (3/3, +₹4,589.25) remains the
  best scoped result for Cluster 3 only, combined below baseline.
  November paper is NOT frozen for any (t) variant. No (t)
  in-sample result is carried into a whole-month run on the same
  Jan–Oct data.
- **Dead, do not re-propose without new evidence:** entry-bar
  arming (t1/t3 — costs a working re-entry), bounce-high stops
  (t2/t4/t6 — asymmetric: widen losers, shrink winners), close
  stops (t5 — larger losses for the same exits), gap / below-PDL /
  OR-width filters as no-trades (blocked by 23 Mar), BN reclaim
  confirmation (kills the 2026 winner), stop-at-L (flips both
  winners to losses), retest-of-L on knife-edge risks (3.05 /
  0.40 points are not tradeable confirmations).

## Next family (u) — the task continues, not completed

Family (t) closes the bounce-stop, morning-structure, and
reclaim-confirmation leads and leaves the same core intact: the
(lA) failing set is 30 Mar, 2 Apr, 13 May; the untouched shape is a
deep-gap-down, far-below-previous-low morning that shares its
features with exactly one winner (23 Mar). The next family must
not re-run (t)'s rules on a new window to hunt a pass. Concrete
leads, in the order the evidence points to them:

1. **What distinguishes 23 Mar from 30 Mar / 2 Apr?** That single
   winner is now the key comparison: same deep gap, same
   far-below-PDL distance, but a green day. Test axes not yet
   compared on that pair — intraday path after the signal
   (bounce depth and duration, close-vs-high behaviour in the
   first 3 bars after entry), Bank Nifty path on those days, and
   previous-day close position — before any new filter is
   proposed. If no axis separates them, the untouched shape may
   be unfilterable at entry and the honest next step is a
   re-entry/exit answer, not another entry filter.
2. **13 May on its own terms.** 13 May is the only (lA) failing
   day that is not an untouched entry-bar stop (it was converted
   in-sample by (o)/(p) partials and lost out-of-sample in (q));
   it should be treated as a give-back/exit problem, not grouped
   with the entry-bar stops, and any variant for it must be
   validated on the out-of-sample PE window, not on Jan–Oct
   alone.
3. **Cluster 2: accept the small-N verdict or find a new axis.**
   With 6 reclaim trades across two years, no confirmation,
   cap, size, or stop rule converts a loser without killing a
   winner. The next Cluster 2 family should either test a
   genuinely different axis (e.g. Bank Nifty trend on the day,
   not at the signal bar; or the reclaim's own intraday path
   after the signal) on both years together, or record Cluster 2
   as unfixable on the available reclaim sample and stop
   spending families on it.

Files: engine `t_sweep.py`, raw replay `t_sweep_raw.json`, this
report `nifty_cluster1_t_sweep.md`. Paper only throughout; no
orders placed, nothing fabricated. The long-horizon task continues
in the parent conversation: family (t) is exhausted, none is
adopted, and the next decision is family (u) — not a whole-month
run of any (t) variant on the same Jan–Oct data.
