# NIFTY — Survival-gated exit + Cluster 3 discriminator + Cluster 2 stall+partial
## Paper only, no orders, no live-trading recommendation. Long-horizon task, continued — do NOT stop.

Source: `nifty_cluster1_retest_sweep.md` (retest fails on Cluster 1 at
3/8, winners collapse to +₹2,100; stall fails at 0/8 on Cluster 1;
Cluster 3 partial 45% passes for Cluster 3 alone at 3/3, +₹4,589,
non-tiny ₹1,210–₹1,630, but as a universal rule it loses combined
+₹33,818 vs baseline +₹56,395 and winners fall to +₹42,977).
This sweep tests the next family exactly as specified, with the
same pass bar: **60% green AND cluster total positive AND
winners not collapsed.** A variant that passes on count but
with a negative total, or with a positive total built on
tiny greens, or by collapsing winners, is NOT a pass.

Engine: `survival_gated_sweep.py`, raw replay
`survival_gated_sweep_raw.json`, replayed bar by bar from the
Upstox 5-min cache (`data/progressive/NIFTY/spot_5m.csv`), same
exit order as all prior sweeps: stop checked BEFORE target on
each bar, including the entry bar, square-off 15:10.
100 shares equivalent, ₹40/trade. "Green" = net > ₹0.
No-trade counted separately from green throughout.

## Headline — Families 1–3 here are exhausted, nothing passes Cluster 1

- **Family 1, survival-gated exit: Cluster 1 is NOT fixed by
  any survival gate, by construction and in the replay.**
  Cluster 1 stops in 1–5 bars, so every Cluster 1 trade is
  already out before a 10- or 20-bar gate. Survival N=10
  and N=20, both interpretations: **0/8 green, −₹24,290
  unchanged.** That is not a failure of the gate's tuning;
  it is the gate's definition — it cannot touch a trade
  that is already stopped out. Do not present survival
  as a Cluster 1 fix.
- **Family 1 on Cluster 3: survival N=10 (interpretation B)
  DOES preserve the Cluster 3 pass, with far less winner
  damage than the universal partial.** 3/3 green, total
  **+₹4,589** — identical, trade for trade in net, to the
  ungated partial 45% on Cluster 3 (13 Feb +₹1,630,
  30 Apr +₹1,366, 18 May +₹1,594, all non-tiny).
  Winners under survival N=10 (B) are **14/14 green,
  +₹69,334** (vs baseline +₹91,270, −24%), against
  +₹42,977 (−53%) for the universal partial. All-PE
  combined under survival N=10 (B) is **+₹49,633**
  (Cluster 1 −₹24,290 + Cluster 3 +₹4,589 + winners
  +₹69,334), vs baseline +₹56,395 and universal
  partial +₹33,818. Survival is a genuine improvement
  over the universal partial, but it is still **below
  baseline combined**, because Cluster 1 is untouched
  at −₹24,290 and 8 of 14 winners are still partialled.
  It is therefore recorded as a scoped Cluster 3 exit
  improvement, NOT adopted as a universal rule and NOT
  carried into a whole-month run on its own.
- **Family 1, N=20: fails Cluster 3.** Survival N=20 (B):
  2/3 green, total **−₹674** — 18 May stops at 10:30,
  before its gate (entry 09:40 + 20 bars), so it never
  earns the partial and books its full −₹3,670.
  Winners under N=20 (B) recover to +₹80,614 and
  combined all-PE is +₹55,650, only ₹745 below baseline
  — but that near-baseline total is bought by losing
  Cluster 3, which is the cluster the gate was meant
  to protect. N=20 is not a pass.
- **Family 1, interpretation A (strict-arm) is reported
  because the gate definition matters, and it FAILS.**
  If the partial trigger is simply not checked until
  the gate bar (no retroactive booking of a partial
  level already passed), survival N=10 on Cluster 3
  is only 1/3 green, −₹6,054, and N=20 is 0/3,
  −₹10,585 (baseline). The reason is plain: Cluster 3
  partials were earned early (13 Feb partial at
  10:15, 8 bars after entry; 30 Apr at 10:15, 2 bars
  after entry; 18 May at 09:50, 2 bars after entry)
  and price never returned below the partial level
  after the gate before hitting the stop. A gate that
  arms late destroys the very partial it was meant
  to gate. Interpretation B (eligibility: if still
  open at the gate, book what was already earned)
  is therefore the only survival definition that
  preserves Cluster 3 — and even B does not fix
  Cluster 1.
- **Family 2, live Cluster 3 discriminator: NO single
  signal-time feature separates Cluster 3 from
  Cluster 1 and the winners.** Every feature overlaps
  (table below). One post-hoc two-feature box does
  separate all 25 PE trades in-sample — gap between
  −0.90% and −0.65% AND signal close more than 200
  points below the previous-day low — but it is fitted
  to 3 Cluster 3 days, its floor clears Cluster 3's
  minimum (204.7) by only 4.7 points, and it has no
  out-of-sample validation. It is reported honestly
  as a candidate to validate, NOT as a live
  discriminator and NOT as a basis to adopt the
  Cluster 3 partial. Without a validated discriminator,
  the Cluster 3 partial must still be judged on its
  all-PE combined total, where survival N=10 (B)
  at +₹49,633 still loses to baseline +₹56,395.
- **Family 3, Cluster 2 on its own terms (stall 10 +
  partial 45%): best Cluster 2 total yet, still NOT
  a pass.** 1/2 green, total **−₹875** (14 Jan
  +₹1,195 via partial then breakeven stop; 26 Oct
  −₹2,070 via stall 10, partial never triggered).
  That beats baseline −₹11,420, stall 10 alone
  −₹2,100, and partial 45% alone −₹7,440, but 1/2
  is 50%, below the 60% bar, and the total is still
  negative. 26 Oct is the blocker in every Cluster 2
  variant: its MFE is 41.0% of target (0.82× risk),
  below the 45% partial level (0.90× risk), so no
  45% partial can ever book on it. (Prior sweep's
  partial 40% turned both Cluster 2 days green at
  +₹4,456, but only because 26 Oct's MFE clears
  40% by 1.0 point — a knife-edge, not re-tested
  here and not claimed as a fix.)

**Nothing in this report is adopted, and nothing is
carried into a whole-month run on its own.** The
long-horizon task continues in the parent conversation
— this is exhaustion of Families 1–3 in this task,
not completion of the task.

## Family 1 — Survival-gated exit, defined so it can be reproduced

Baseline: entry = next bar open after signal, stop =
signal high (PE) / signal low (CE), target = entry
−/+ 2× risk, stop before target each bar, square-off
15:10, 100 shares, ₹40/trade. Partial 45% level =
entry −/+ 0.9× risk (45% of the 2× risk target
distance); book 50 shares there, trail remaining 50
to breakeven (entry).

Gate: the trade must still be open at the open of
bar sig+1+N (N = 10 or 20 full bars after the entry
bar). Trades stopped before the gate keep their full
stop loss; trades reaching target before the gate
keep their full target. Those two properties are
verified in the replay, not assumed.

- **Interpretation B (primary, "eligibility"):** at the
  gate open, if the best favourable extreme so far
  already reached the partial level, book 50 shares
  at the partial level immediately and trail the rest
  to breakeven, then replay the gate bar onward with
  the breakeven stop (adverse first, then partial,
  then target each bar). If the partial level has not
  yet been reached, arm it from the gate bar onward.
- **Interpretation A (strict-arm, for honesty):** the
  partial trigger is not checked at all until the
  gate bar; a partial level passed before the gate
  does NOT book retroactively. Only bars from the
  gate onward can trigger it.

Why both are reported: the task's wording ("book
the partial ONLY if still open after N bars") is
ambiguous between eligibility and arming, and the
two readings give opposite Cluster 3 results (see
below). Reporting only B would hide that the gate
only works under the eligibility reading.

### Family 1 — Cluster 3, day by day (original nets in brackets)

| Date (orig) | Survival B N=10 | Survival B N=20 | Survival A N=10 | Survival A N=20 |
|---|---|---|---|---|
| 2026-02-13 (−3,750) | +1,630: gate 10:25, partial earned earlier, BE stop 10:25 | +1,630: gate later, same partial profit, BE stop | −3,750: partial earned 10:15, never re-triggered after gate | −3,750 |
| 2026-04-30 (−3,165) | +1,366: gate 10:55, partial earned earlier, BE stop 11:35 | +1,366: same | +1,366: partial re-triggered after gate | −3,165 |
| 2026-05-18 (−3,670) | +1,594: gate 10:30, partial earned earlier, BE stop 10:30 | −3,670: stop 10:30 before gate | −3,670: partial earned 09:50, never re-triggered after gate | −3,670 |
| **Summary** | **3/3 green, +4,589** | **2/3 green, −674** | **1/3 green, −6,054** | **0/3 green, −10,585** |

Reading: B N=10 reproduces the ungated partial 45%
Cluster 3 result exactly in net (₹1,630 / ₹1,366 /
₹1,594), because a breakeven scratch on the remaining
50 shares is ₹0 regardless of when the breakeven stop
is hit. The gate changes WHEN the partial is booked,
not how much it books, for Cluster 3 — under B.
Under A, the gate changes whether it is booked at
all, and for 13 Feb and 18 May the answer is no.

### Family 1 — Cluster 1, all variants (original total −₹24,290)

| Variant | Green | No-trade | Still loss | Total (₹) |
|---|---|---|---|---|
| Baseline | 0/8 | 0 | 8 | −24,290 |
| Survival B N=10 | 0/8 | 0 | 8 | −24,290 |
| Survival B N=20 | 0/8 | 0 | 8 | −24,290 |
| Survival A N=10 | 0/8 | 0 | 8 | −24,290 |
| Survival A N=20 | 0/8 | 0 | 8 | −24,290 |

Day by day, every Cluster 1 trade is identical to
baseline under every survival variant: 9 Jan stop
09:40 −₹3,745; 6 Feb stop 09:45 −₹2,275; 30 Mar stop
11:30 −₹2,055; 2 Apr stop 10:00 −₹2,115; 13 May stop
09:55 −₹5,075; 29 Jun stop 09:40 −₹4,740; 8 Jul stop
09:45 −₹1,985; 19 Aug stop 09:50 −₹2,300. No Cluster 1
trade survives to any gate (stops in 1–5 bars), so
no partial can ever apply to it. This is the
definition working as specified, not a tuning miss.

### Family 1 — Cluster 2 (CE) under survival, for completeness

Survival B N=10 and N=20, and A N=10, are identical
on Cluster 2: 1/2 green, total −₹7,440 (14 Jan
+₹1,195 via partial then breakeven stop; 26 Oct
−₹8,635 full stop, partial never reached because
MFE 0.82× risk < 0.90× risk). Survival A N=20 is
0/2, −₹11,420 (14 Jan's partial was earned before
its gate and never re-triggered). Survival does not
fix Cluster 2 either; the combined stall+partial
test in Family 3 is the Cluster 2 result to use.

### Family 1 — Winning PE days (14 days, baseline +₹91,270)

| Variant | Green | Total (₹) | What changed vs baseline |
|---|---|---|---|
| Baseline | 14/14 | +91,270 | — |
| Universal partial 45% (prior sweep) | 14/14 | +42,977 | 14/14 partialled, value roughly halved |
| **Survival B N=10** | **14/14** | **+69,334** | 6 full targets untouched, 8 partialled |
| Survival B N=20 | 14/14 | +80,614 | 12 full targets, 2 partialled |
| Survival A N=10 | 14/14 | +71,874 | 7 full targets, 7 partialled |
| Survival A N=20 | 14/14 | +87,489 | 12 full targets, 2 partialled |

Survival B N=10, winner by winner (baseline in
brackets): 21 Jan target +₹9,280 (unchanged);
24 Feb partialled then BE stop +₹1,623 (was
+₹7,350); 16 Mar target +₹8,940 (unchanged);
13 Mar target +₹5,400 (unchanged); 23 Mar target
+₹7,260 (unchanged); 24 Apr target after partial
+₹6,384 (was +₹8,820); 5 May partialled then BE
stop +₹1,103 (was +₹5,040); 22 Jul partialled then
BE stop +₹1,391 (was +₹6,320); 12 Aug target after
partial +₹4,520 (was +₹6,250); 27 Aug target after
partial +₹2,164 (was +₹3,000); 29 Sep target
+₹3,790 (unchanged); 7 Sep target after partial
+₹2,157 (was +₹2,990); 8 Oct target after partial
+₹3,933 (was +₹5,440); 23 Oct target +₹11,390
(unchanged). Winners stay green under survival —
the count does not collapse — but 8 of 14 are
still partialled, costing ₹21,936 vs baseline.
That is why survival N=10 (B) combined all-PE
(+₹49,633) beats the universal partial (+₹33,818)
yet still loses to baseline (+₹56,395): the gate
saves the fast winners, but the slow winners that
survive 10 bars are exactly the ones the partial
then clips, and Cluster 1 contributes nothing to
offset it.

### Family 1 — Combined totals (the pass-bar test, not a single cluster)

| Variant | Cluster 1 | Cluster 3 | Winners | All-PE combined | Pass? |
|---|---|---|---|---|---|
| Baseline | −24,290 | −10,585 | +91,270 | **+56,395** | — |
| Universal partial 45% | −13,749 | +4,589 | +42,977 | +33,818 | No (combined falls) |
| **Survival B N=10** | **−24,290** | **+4,589** | **+69,334** | **+49,633** | **No — Cluster 1 0/8, combined below baseline** |
| Survival B N=20 | −24,290 | −674 | +80,614 | +55,650 | No — Cluster 3 fails, combined still below baseline |
| Survival A N=10 | −24,290 | −6,054 | +71,874 | +41,530 | No |
| Survival A N=20 | −24,290 | −10,585 | +87,489 | +52,614 | No |

No survival variant passes the stated bar on
Cluster 1 (0/8 in every case), and no survival
variant beats baseline on combined all-PE economics.
Survival B N=10 is the best survival variant on
the scoped question — it keeps Cluster 3 green
while cutting winner damage from −53% to −24% —
but "best survival variant" is not "adopted", and
it is not carried into a whole-month run.

## Family 2 — Live Cluster 3 discriminator, tested honestly

Question: at entry (signal time, no look-ahead), is
there any feature that separates the 3 Cluster 3
days from the 8 Cluster 1 days and the 14 winning
PE days? Features computed from the previous day's
OHLC, the 09:15–09:30 opening range, and the signal
candle only. Note: "room below" is None for every
PE breakdown here, because the signal close is below
the previous-day low, so no previous-day level sits
below it — room is infinite by the original engine's
definition, not a usable feature.

### Feature table, day by day (PE only)

Signal = signal bar label; bars = bars since 09:30;
gap = day open vs previous close (%); bias = previous
close position in previous range (%); ORw = opening
range width (pts); prevR = previous-day range (pts);
firstR = 09:15 bar range (pts); sigR = signal candle
range (pts); belowORL = OR low − signal close (pts);
belowPDL = previous-day low − signal close (pts);
risk = stop − entry (pts).

| Group / date | Signal | Bars | Gap % | Bias | ORw | PrevR | FirstR | SigR | BelowORL | BelowPDL | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| C1 2026-01-09 | 09:30 | 0 | −0.110 | 3.8 | 101.45 | 274.75 | 100.40 | 52.30 | 2.00 | 21.30 | 37.05 |
| C1 2026-02-06 | 09:35 | 1 | −0.140 | 34.9 | 77.25 | 178.15 | 77.25 | 31.60 | 9.25 | 35.20 | 22.35 |
| C1 2026-03-30 | 11:25 | 23 | −1.269 | 9.2 | 147.90 | 381.55 | 147.90 | 22.45 | 1.95 | 336.35 | 20.15 |
| C1 2026-04-02 | 09:55 | 5 | −1.408 | 26.2 | 185.50 | 322.70 | 185.50 | 22.00 | 2.65 | 412.10 | 20.75 |
| C1 2026-05-13 | 09:30 | 0 | −0.291 | 20.1 | 141.35 | 409.15 | 141.35 | 51.95 | 24.50 | 10.45 | 50.35 |
| C1 2026-06-29 | 09:30 | 0 | +0.037 | 6.3 | 78.40 | 222.60 | 78.40 | 48.90 | 15.25 | 21.90 | 47.00 |
| C1 2026-07-08 | 09:30 | 0 | −0.392 | 3.4 | 65.35 | 181.95 | 58.85 | 25.60 | 9.85 | 128.90 | 19.45 |
| C1 2026-08-19 | 09:30 | 0 | −0.012 | 0.0 | 79.80 | 114.75 | 70.35 | 27.25 | 19.20 | 81.05 | 22.60 |
| **C3 2026-02-13** | **09:30** | **0** | **−0.872** | **28.4** | **72.05** | **154.30** | **72.05** | **41.25** | **10.60** | **204.70** | **37.10** |
| **C3 2026-04-30** | **10:00** | **6** | **−0.690** | **37.7** | **146.40** | **274.75** | **78.20** | **32.40** | **23.15** | **210.35** | **31.25** |
| **C3 2026-05-18** | **09:35** | **1** | **−0.749** | **21.4** | **131.55** | **229.00** | **122.80** | **47.45** | **4.65** | **251.90** | **36.30** |
| W 2026-01-21 | 10:20 | 10 | −0.334 | 13.1 | 147.60 | 413.65 | 147.60 | 48.85 | 24.30 | 65.50 | 46.60 |
| W 2026-02-24 | 09:30 | 0 | −0.242 | 58.4 | 94.65 | 162.10 | 71.25 | 42.00 | 33.25 | 95.45 | 36.95 |
| W 2026-03-16 | 10:20 | 10 | −0.237 | 15.5 | 150.05 | 380.40 | 150.05 | 45.50 | 41.30 | 55.30 | 44.90 |
| W 2026-03-13 | 09:45 | 3 | −0.748 | 30.0 | 72.65 | 276.85 | 68.80 | 38.40 | 17.85 | 158.90 | 27.20 |
| W 2026-03-23 | 09:50 | 4 | −1.341 | 24.2 | 217.15 | 277.55 | 217.15 | 40.30 | 5.50 | 438.55 | 36.50 |
| W 2026-04-24 | 09:30 | 0 | −0.230 | 12.1 | 149.40 | 175.40 | 105.75 | 49.70 | 38.95 | 117.15 | 44.30 |
| W 2026-05-05 | 10:30 | 12 | −0.295 | 41.7 | 122.70 | 285.45 | 122.70 | 28.70 | 8.05 | 63.40 | 25.40 |
| W 2026-07-22 | 09:30 | 0 | −0.176 | 45.4 | 119.35 | 126.55 | 90.15 | 36.15 | 22.70 | 111.40 | 31.80 |
| W 2026-08-12 | 09:55 | 5 | +0.003 | 28.8 | 82.70 | 147.60 | 82.70 | 34.40 | 12.05 | 50.70 | 31.45 |
| W 2026-08-27 | 09:55 | 5 | +0.289 | 0.0 | 99.10 | 170.85 | 59.10 | 22.00 | 1.60 | 11.00 | 15.20 |
| W 2026-09-29 | 09:30 | 0 | −0.210 | 5.7 | 129.00 | 318.05 | 73.30 | 27.35 | 4.45 | 142.45 | 19.15 |
| W 2026-09-07 | 09:50 | 4 | −0.061 | 1.7 | 71.50 | 109.90 | 71.50 | 18.30 | 1.35 | 78.70 | 15.15 |
| W 2026-10-08 | 09:40 | 2 | −0.018 | 33.1 | 123.30 | 171.35 | 77.95 | 41.25 | 3.30 | 73.85 | 27.40 |
| W 2026-10-23 | 10:05 | 7 | +0.240 | 57.7 | 87.55 | 230.15 | 69.10 | 62.80 | 176.65 | 31.80 | 57.15 |

### Single-feature check — none separates Cluster 3

| Feature | Cluster 3 range | Cluster 1 range | Winners range | Separates? |
|---|---|---|---|---|
| Bars since 09:30 | 0–6 | 0–23 | 0–12 | No — 0, 1 and 6 all occur elsewhere |
| Gap % | −0.872 to −0.690 | −1.408 to +0.037 | −1.341 to +0.289 | No — Cluster 3 band sits inside both ranges; 13 Mar winner gap −0.748 is inside it |
| Bias score | 21.4–37.7 | 0.0–34.9 | 0.0–58.4 | No — fully overlapped |
| OR width | 72.05–146.40 | 65.35–185.50 | 71.50–217.15 | No |
| Previous-day range | 154.30–274.75 | 114.75–409.15 | 109.90–413.65 | No |
| First-bar range | 72.05–122.80 | 58.85–185.50 | 59.10–217.15 | No |
| Signal candle range | 32.40–47.45 | 22.00–52.30 | 18.30–62.80 | No |
| Close below OR low | 4.65–23.15 | 1.95–24.50 | 1.35–176.65 | No |
| Close below prev-day low | 204.70–251.90 | 10.45–412.10 | 11.00–438.55 | No — Cluster 1 has 336 and 412, a winner has 439 |
| Risk | 31.25–37.10 | 19.45–50.35 | 15.15–57.15 | No |

The closest single feature is gap: Cluster 3 is
tightly clustered at −0.69% to −0.87%, but a gap
band of −0.90% to −0.65% also catches Cluster 1's
30 Mar (−1.269% is outside, 2 Apr −1.408% is
outside — so gap alone, strictly, catches 0 Cluster 1
days in that exact band) and one winner, 13 Mar
(−0.748%). Gap alone therefore fails on the winner
side, not the Cluster 1 side. Below-prev-day-low
alone fails on both sides (Cluster 1: 30 Mar 336,
2 Apr 412; winner: 23 Mar 439).

### Two-feature box — separates in-sample, reported with its warning

Conjunction: **gap between −0.90% and −0.65% AND
signal close more than 200 points below the
previous-day low.** On these 25 trades it captures
Cluster 3 3/3 and nothing else: Cluster 1 days in
the gap band number zero (30 Mar and 2 Apr are
below −1.26%), and the one winner in the gap band
(13 Mar, −0.748%) has below-prev-day-low of only
158.90, below the 200 floor. The other candidate
conjunction, gap band AND bias 21–38, fails: it
also catches the 13 Mar winner (bias 30.0).

**Warning that must travel with this box:** it is
a post-hoc box fitted to 3 positive days. Its
200-point floor clears Cluster 3's minimum (204.70)
by only 4.7 points — a knife-edge, the same kind
of knife-edge that already disqualified the
Cluster 2 partial 40% pass. Its gap band is 0.25
percentage points wide, chosen after seeing the
three gaps. With 3 positives, a box that separates
in-sample is expected by chance, not evidence of
a live rule. It must NOT be adopted as a live
discriminator, and it must NOT be used to carry
the Cluster 3 partial into a whole-month run,
until it is validated on trades it was not fitted
on (forward paper, or a different year). Until
then, the honest verdict stands: **no validated
live discriminator exists**, and the Cluster 3
partial must be judged on its all-PE combined
total, where survival N=10 (B) at +₹49,633 still
loses to baseline +₹56,395.

What the discriminator table does prove, negatively:
Cluster 3 is not a "big gap" or "wide OR" or
"late signal" phenomenon at entry. Its defining
properties — slow stop (11–35 bars) and 48–83%
MFE — are only known after the trade is open,
which is exactly why a survival gate (which waits
for the trade to stay open) is the right shape of
rule for it, and why an entry-time filter is the
wrong shape.

## Family 3 — Cluster 2 on its own terms: stall 10 + partial 45%

Rule (one variant, as specified): original CE
entry/stop/target (14 Jan signal 11:15, entry
25,747.75, stop 25,720.30, risk 27.45; 26 Oct
signal 09:55, entry 22,635.70, stop 22,549.75, risk
85.95). Partial 45% level = entry + 0.9× risk,
book 50 shares there, trail remaining 50 to
breakeven. Stall counter as in the prior sweep:
a bar that does not make a new favourable high
increments it, a new high resets it to 0, exit at
that bar's close when it reaches 10. Per-bar
order: adverse (current stop) first, then partial,
then target, then stall exit at close for the
still-open quantity.

| Date (orig) | Partial 45% alone (prior) | Stall 10 alone (prior) | Stall 10 + partial 45% (this sweep) |
|---|---|---|---|
| 2026-01-14 (−2,785) | +1,195: partial 11:25, BE stop 12:10 | −30: stall 12:50, essentially a scratch | **+1,195: partial 11:25, BE stop 12:10** (stall never fires — the breakeven stop hits first; combined = partial alone on this day) |
| 2026-10-26 (−8,635) | −8,635: MFE 41.0% of target = 0.82× risk, below the 0.90× risk partial level, so no partial ever triggers | −2,070: stall 10:55, exit 22,615.40 | **−2,070: stall 10:55, exit 22,615.40** (partial never triggers, so combined = stall alone on this day) |
| **Summary** | 1/2 green, −7,440 | 0/2 green, −2,100 | **1/2 green (50%), total −875** |

Verdict: stall 10 + partial 45% is the best
Cluster 2 total yet — it takes the better leg
from each parent rule on each day (partial on
14 Jan, stall on 26 Oct) — but it is still **NOT
a pass**: 1/2 green is below the 60% bar, and
the total is still negative. The combination does
not create a new green on 26 Oct, because the
two rules fail on that day for different reasons
(partial: MFE too small; stall: only cuts the
loss, it cannot turn a −₹2,070 stall exit into
a profit). No Cluster 2 variant in this sweep
converts 26 Oct to green without the 40% partial
knife-edge from the prior sweep, and that variant
is not re-claimed here.

## Variant summary — all families in this task, pass bar applied

| Variant | Cluster 1 green | Cluster 1 total (₹) | Cluster 3 green / total (₹) | Winners total (₹) | Combined all-PE (₹) | Pass? |
|---|---|---|---|---|---|---|
| Baseline | 0/8 | −24,290 | 0/3 / −10,585 | +91,270 | +56,395 | — |
| Survival B N=10 | 0/8 | −24,290 | 3/3 / +4,589 | +69,334 | +49,633 | **No** (Cluster 1 0/8, combined below baseline) |
| Survival B N=20 | 0/8 | −24,290 | 2/3 / −674 | +80,614 | +55,650 | **No** (Cluster 3 fails) |
| Survival A N=10 | 0/8 | −24,290 | 1/3 / −6,054 | +71,874 | +41,530 | **No** |
| Survival A N=20 | 0/8 | −24,290 | 0/3 / −10,585 | +87,489 | +52,614 | **No** |
| Cluster 2 stall10+partial45 | (Cluster 2: 1/2, −875) | — | — | — | — | **No** (50% < 60%, total negative) |
| Discriminator (single feature) | — | — | — | — | — | **No** — none separates |
| Discriminator (gap+belowPDL box) | — | — | — | — | — | **Not adopted** — post-hoc, 3-day fit, knife-edge floor |

## What this sweep proves, and what it does not

- Survival gating is the right SHAPE for Cluster 3
  (wait for the trade to stay open, then protect
  what it earned), and it is a real improvement
  over the universal partial: winner damage falls
  from −53% to −24% at N=10, while Cluster 3 stays
  3/3 green at +₹4,589. But shape is not a pass:
  combined all-PE still loses to baseline, because
  Cluster 1 — 44.3% of the original loss — is
  untouched by any gate, and 8 of 14 winners are
  still clipped by the partial.
- Cluster 1 remains unfixed as a morning entry
  across every family so far: timing 37.5%,
  stop genuine 50%, retest 37.5%, partial
  (non-tiny) 25%, stall 0%, survival 0%. A rule
  that waits (timing, retest, survival) cannot fix
  a trade that is already stopped out in 1–5 bars;
  only a rule that changes the morning bar itself
  (stop placement that survives the bounce bar,
  or a different morning entry) can, and the stop
  family already showed its best genuine variant
  at 50% with a worse total.
- Cluster 3's exit is solved on its own 3 days
  (partial 45%, survival-gated at N=10 under
  interpretation B), but it is NOT adoptable as a
  scoped rule without a validated live
  discriminator, and no single signal-time feature
  provides one. The two-feature box is a lead for
  forward validation, not a rule.
- Cluster 2's best honest total is now −₹875
  (stall 10 + partial 45%), still negative, still
  1/2 green, with 26 Oct unconverted in every
  non-knife-edge variant. Cluster 2 is loss-cut,
  not fixed.

## Next family to test (the task continues — this is NOT completion)

Families 1–3 in this task are exhausted. The next
family must attack the gap this sweep leaves open,
not re-run survival, stall, or partial in a new
costume:

1. **Forward validation of the gap+belowPDL box,
   or a different discriminator search on fresh
   trades:** if the box (gap −0.90% to −0.65% AND
   close >200 pts below previous-day low) is to be
   believed, it must be tested on PE trades it was
   not fitted on — November 2026 paper, or a
   different year — with its thresholds frozen
   before the test. If it fails there, it is
   discarded, not re-fitted. Alternatively, search
   for a discriminator in live, post-entry features
   that a survival gate already uses (e.g. "still
   open after 10 bars AND MFE ≥ 0.9× risk" — which
   is exactly what survival B N=10 already is,
   so that search must be framed as validating
   survival B, not as a new entry filter).
2. **Cluster 1's morning bar itself:** the waiting
   families are exhausted for Cluster 1. The next
   Cluster 1 family must change the morning entry
   or its stop in a way not already tested to
   exhaustion (timing, second-close, retest,
   survival, stall all wait; stop buffer / OR-low
   stop were tested in the stop family). Any new
   variant must still meet 60% green AND positive
   cluster total AND no winner collapse, on
   Cluster 1 first, before any whole-month run.

Files: engine `survival_gated_sweep.py`, raw replay
`survival_gated_sweep_raw.json` (all day nets above,
survival B/A × N=10/20 for Clusters 1/2/3 and
winners, discriminator features, Cluster 2 combined
run). Paper only throughout; no orders placed,
nothing fabricated. The long-horizon task continues
in the parent conversation: the next decision is
whether to forward-validate the gap+belowPDL box
or to attack Cluster 1's morning bar itself — and
neither is adopted here.
