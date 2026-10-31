# NIFTY failing cases — January to October 2026 (Step 1 only: identify, do NOT tune yet)

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday, provisional rules (NOT Chandu's live options rules): 100 shares
equivalent (index points × 100), ₹40/trade assumed cost, stop = signal-candle
low/high, target = 2× stop distance, square-off 15:10, Setup 1 skipped, short
signals paper-only, one trade/instrument/day for the raw candidates, capped
as described in the sources below.

**Scope, and what this report is NOT:**
- NIFTY index only first, as instructed. Bank Nifty is second and is NOT
  mixed into any cluster below.
- Window: January 2026 to 28 October 2026 only. 29 October 2026 is excluded
  (it was still in progress on the day of the source runs).
- Primary universe: V5 index Nifty leg — 32 trades, 16 targets, 16 stops,
  0 square-offs, 41.7% win on the combined V5 index, Nifty net +₹47,965.
  That net is +₹102,750 gross on the 16 winners minus ₹54,785 on the
  16 losers below. Every loser in this report is a stop; there is no
  square-off loser in the V5 Nifty leg.
- Supplementary check: V4 index Nifty leg (capped-v2 series) is 27 trades,
  14 targets, 13 stops, net +₹42,410. Its 13 losses are EXACTLY the 13 V4
  losses in the V5 list below (same dates, same setups, same nets).
  V5 adds only 3 Skill losses (2026-01-30, 2026-04-02, 2026-06-08).
  So the V4 leg adds NO new failing scenario beyond the V5 list.
  Skill index Nifty leg on its own (capped-v2) is 29 trades, net +₹49,890
  in the capped-v2 JSONs; it is not re-listed day by day here because
  the task's source legs are V5 Nifty and V4 index Nifty, and V5 already
  contains the deduped Skill picks.
- Sources: `v5_index_banknifty_nifty_jan_oct_2026.md`,
  `jan_oct_2026_v4_and_skill.md`, month JSONs
  `data/progressive/v5_index_summary_2026-01.json` through
  `v5_index_summary_2026-10.json` and
  `data/progressive/capped_v2_summary_2026-01.json` through
  `capped_v2_summary_2026-10.json`. Day-level entry/stop/target,
  opening-range and previous-day levels, bars-to-stop, maximum
  favourable excursion (MFE, in points before the stop bar, as % of
  the full target distance) and "later target" (did price reach the
  target level, / close beyond it, later the same day AFTER the stop
  was hit — a diagnostic only, never used to re-score the trade)
  were recomputed from the Upstox 5-min cache for NIFTY
  (`data/progressive/NIFTY/spot_5m.csv`, `spot_daily.csv`) with the
  same `find_signal` / `run_day` / `skill_or_outcome` logic as the
  source engines. Nothing was fabricated.
- **No fix has been applied and no tuned re-run has been done in this
  step.** The "parameters that could be tweaked" section at the end
  covers the FIRST failing case only, and is preparation for Step 2,
  not Step 2 itself.

## Headline: why Nifty is green one day and failing the next

It is not one random bad day. The same failing shape repeats, month
after month, from January to August:

- 11 of the 16 losses are PE (short) trades, 5 are CE (long).
- 10 of the 16 losses are the same setup family: V4 setup2 OR
  breakdown (PE).
- 14 of the 16 stops sit INSIDE the 09:15–09:30 opening range
  (OR). That is the mechanism, not a coincidence: the stop is the
  signal candle's high (PE) or low (CE), and for a 09:30–09:35
  signal that extreme is usually still inside, or only just
  outside, the OR. A modest bounce back into the OR therefore
  hits the stop, even when the day later goes the trade's way.
- 10 of the 16 losses later reach the target level after the stop
  (8 of them later CLOSE beyond it). The direction was often
  right; the entry/stop timing was what failed. That is why
  "tune the parameters" must mean "fix the entry/stop
  confirmation", not "flip the direction".
- 15 of the 16 losing days opened below the previous close
  (gap_pct negative; the exception, 2026-06-29, opened +0.04%,
  essentially flat, and 2026-08-19 opened −0.01%, essentially
  flat). Losing days are therefore almost all gap-down /
  down-open days, not gap-up days.
- Stop distance (risk) is tight for Nifty: median 29.85 points,
  range 16.20–85.95 points. Target distance is 2× that.
  The single largest loss, 2026-10-26 (−₹8,635), is the outlier
  risk of 85.95 points — 2.9× the median — not a typical trade.
- September 2026 has ZERO Nifty losses in V5 (2 trades, both
  targets). October has only the one reclaim loss below.
  The failing scenarios below are therefore a January–August
  phenomenon, with October's loss belonging to a different,
  rarer scenario.

## Day list — every V5 Nifty losing trade, Jan–Oct 2026

Net = direction × (exit − entry) × 100 − ₹40. Risk = |entry − stop|
in points. Target net = 2 × risk × 100 − ₹40. MFE% = maximum
favourable move before the stop bar, as % of the full target
distance. "Later target" = price reached the target level after
the stop (H = high/low touched, C = closed beyond it).

| Date | Method / setup | Dir | Prev-day bias (close score) | OR low–high (width) | Signal | Entry | Stop | Target | Risk (pts) | Net (₹) | Target net (₹) | Exit | Bars to stop | MFE (pts / %) | Later target |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-01-09 | V4 setup2_or_breakdown | PE | bearish (3.8) | 25,839.15–25,940.60 (101.4) | 09:30 | 25,836.05 | 25,873.10 | 25,761.95 | 37.05 | −3,745 | 7,370 | stop 09:40 | 2 | 17.70 / 23.9% | H + C |
| 2026-01-14 | V4 setup4_reclaim | CE | neutral (37.4) | 25,638.35–25,744.80 (106.5) | 11:15 | 25,747.75 | 25,720.30 | 25,802.65 | 27.45 | −2,785 | 5,450 | stop 13:20 | 25 | 44.00 / 80.1% | No |
| 2026-01-30 | Skill or_breakout | CE | bullish (87.9) | 25,224.35–25,285.95 (61.6) | 09:35 | 25,291.05 | 25,261.20 | 25,350.75 | 29.85 | −3,025 | 5,930 | stop 11:10 | 19 | 32.10 / 53.8% | H + C |
| 2026-02-06 | V4 setup2_or_breakdown | PE | bearish (34.9) | 25,553.55–25,630.80 (77.2) | 09:35 | 25,543.45 | 25,565.80 | 25,498.75 | 22.35 | −2,275 | 4,430 | stop 09:45 | 2 | 21.20 / 47.4% | H + C |
| 2026-02-13 | V4 setup2_or_breakdown | PE | bearish (28.4) | 25,558.30–25,630.35 (72.0) | 09:30 | 25,549.00 | 25,586.10 | 25,474.80 | 37.10 | −3,750 | 7,380 | stop 12:25 | 35 | 35.70 / 48.1% | H + C |
| 2026-03-30 | V4 setup2_or_breakdown | PE | bearish (9.2) | 22,470.15–22,618.05 (147.9) | 11:25 | 22,468.10 | 22,488.25 | 22,427.80 | 20.15 | −2,055 | 3,990 | stop 11:30 | 1 | 0.00 / 0.0% | H + C |
| 2026-04-02 | Skill or_breakdown | PE | bearish (26.2) | 22,209.15–22,394.65 (185.5) | 09:55 | 22,206.80 | 22,227.55 | 22,165.30 | 20.75 | −2,115 | 4,110 | stop 10:00 | 1 | 0.00 / 0.0% | No |
| 2026-04-30 | V4 setup2_or_breakdown | PE | neutral (37.7) | 23,872.75–24,019.15 (146.4) | 10:00 | 23,848.75 | 23,880.00 | 23,786.25 | 31.25 | −3,165 | 6,210 | stop 12:10 | 26 | 51.90 / 83.0% | No |
| 2026-05-13 | V4 setup2_or_breakdown | PE | bearish (20.1) | 23,362.45–23,503.80 (141.3) | 09:30 | 23,337.30 | 23,387.65 | 23,236.60 | 50.35 | −5,075 | 10,030 | stop 09:55 | 5 | 74.75 / 74.2% | No |
| 2026-05-18 | V4 setup2_or_breakdown | PE | bearish (21.4) | 23,363.05–23,494.60 (131.5) | 09:35 | 23,358.50 | 23,394.80 | 23,285.90 | 36.30 | −3,670 | 7,220 | stop 10:30 | 11 | 41.40 / 57.0% | No |
| 2026-06-08 | Skill or_breakout | CE | neutral (36.9) | 23,070.15–23,157.05 (86.9) | 09:30 | 23,184.95 | 23,147.30 | 23,260.25 | 37.65 | −3,805 | 7,490 | stop 09:35 | 1 | 0.00 / 0.0% | H only |
| 2026-06-29 | V4 setup2_or_breakdown | PE | bearish (6.3) | 24,032.35–24,110.75 (78.4) | 09:30 | 24,018.70 | 24,065.70 | 23,924.70 | 47.00 | −4,740 | 9,360 | stop 09:40 | 2 | 13.25 / 14.1% | H only |
| 2026-07-08 | V4 setup2_or_breakdown | PE | bearish (3.4) | 24,229.90–24,295.25 (65.3) | 09:30 | 24,221.45 | 24,240.90 | 24,182.55 | 19.45 | −1,985 | 3,850 | stop 09:45 | 3 | 14.25 / 36.6% | H + C |
| 2026-07-13 | V4 setup2_or_breakout | CE | bullish (84.5) | 24,000.20–24,044.45 (44.2) | 09:55 | 24,121.05 | 24,104.85 | 24,153.45 | 16.20 | −1,660 | 3,200 | stop 10:05 | 2 | 7.75 / 23.9% | H + C |
| 2026-08-19 | V4 setup2_or_breakdown | PE | bearish (0.0) | 24,093.05–24,172.85 (79.8) | 09:30 | 24,076.40 | 24,099.00 | 24,031.20 | 22.60 | −2,300 | 4,480 | stop 09:50 | 4 | 11.30 / 25.0% | H + C |
| 2026-10-26 | V4 setup4_reclaim | CE | neutral (54.9) | 22,387.35–22,524.40 (137.1) | 09:55 | 22,635.70 | 22,549.75 | 22,807.60 | 85.95 | −8,635 | 17,150 | stop 11:30 | 19 | 70.45 / 41.0% | No |

Totals for the list: 16 stops, ₹54,785 loss. Winners in the same
V5 Nifty leg (for context, not part of the failing list):
16 targets, ₹102,750 gross, net +₹47,965.

Notes on the two "H only" rows: on 2026-06-08 and 2026-06-29
price later touched the target level intraday but never closed
beyond it. They are counted as "later reached" (10/16) but not
as "later closed beyond" (8/16).

## Scenario clusters — distinct failing scenarios, not one "stops" bucket

Classification rule, applied before ranking and stated so Step 2
can re-test it on one day: a trade belongs to a cluster by
(setup + direction + bars-to-stop + MFE), not by outcome alone.
A trade that later reached its target is flagged, but that flag
does NOT move it to a different cluster — it is a property of
the cluster, and it is what makes the cluster fixable without
flipping direction.

### Cluster 1 — FIRST failing case: immediate OR-breakdown PE bear-trap
- **Count: 8 trades. Loss: −₹24,290 (44.3% of the total ₹54,785 loss).**
- Days: 2026-01-09 (−₹3,745), 2026-02-06 (−₹2,275),
  2026-03-30 (−₹2,055), 2026-04-02 Skill (−₹2,115),
  2026-05-13 (−₹5,075), 2026-06-29 (−₹4,740),
  2026-07-08 (−₹1,985), 2026-08-19 (−₹2,300).
- Shape: V4 setup2_or_breakdown PE, plus the one Skill
  or_breakdown PE on 2026-04-02, all 8 on bearish-bias days.
  Signal at 09:30–09:35 for 6 of the 8
  (exceptions: 2026-03-30 signal 11:25, stop in the
  very next bar; 2026-04-02 signal 09:55, stop in the
  very next bar). Stop hit within 5 bars (1–5 bars; median 2).
  MFE before the stop is 0–74% of target distance, median
  about 25% — in most of these the trade never got going.
  Stop sits inside the OR in all 8 cases, so the loss is
  literally "price bounced back into the opening range and
  took out the signal candle's high".
- Later-target property: 6 of the 8 later reach the target
  level, 5 later close beyond it (2026-01-09, 2026-02-06,
  2026-03-30, 2026-07-08, 2026-08-19; 2026-06-29 touches
  only). The exceptions that never reach target are
  2026-04-02 and 2026-05-13. So for most of this cluster
  the direction was right and the entry was early / the
  stop was inside the noise.
- **Month-by-month occurrence: YES, it repeats across the
  whole window.** January, February, March, April, May,
  June, July, August — eight consecutive months, one
  (or, in May, one counted here plus the slow case below)
  immediate bear-trap per month. It does NOT occur in
  September (no Nifty losses at all) or October (only the
  reclaim loss). This is not a one-off month effect and
  not a single bad week: it is the standing failure mode
  of the PE breakdown entry as coded.
- Why it failed, in price-action terms: the first
  09:30–09:35 close below the OR low and below the
  previous-day low is treated as a breakdown, but on
  these days that close was the morning extreme, not
  the start of a trend leg. The next 1–5 bars retraced
  into the OR. Because the stop is the signal candle's
  high — itself inside the OR — that retracement is
  enough to stop the trade out before any continuation
  can develop. The 2× target (40–100 points away) is
  then reached later on 6 of the 8 days, after the
  trader is already out.

### Cluster 2 — SECOND failing case (by loss): reclaim failure (setup4 CE)
- **Count: 2 trades. Loss: −₹11,420 (20.8% of total loss).**
- Days: 2026-01-14 (−₹2,785), 2026-10-26 (−₹8,635).
- Shape: setup4_reclaim CE, neutral bias both days.
  Signal 11:15 (January) and 09:55 (October). Stop hit
  slowly, 25 and 19 bars later. MFE 80.1% (January) and
  41.0% (October) of target distance — January's trade
  got four-fifths of the way to target and then gave it
  all back; October's got two-fifths of the way. Neither
  later reaches target. January's day closes below entry
  (25,669.10 vs entry 25,747.75); October's day closes
  above entry (22,753.20 vs 22,635.70) but well below
  target (22,807.60).
- Month-by-month occurrence: January and October only.
  It does NOT repeat across the window — it is a rare
  but expensive scenario, and its loss is dominated by
  a single trade: October's risk (85.95 points) is
  2.9× the median Nifty risk (29.85 points), so one
  reclaim failure costs more than four average
  immediate bear-traps.
- Why it failed, in price-action terms: the reclaim
  close held for hours but was never confirmed by a
  second leg up. Price drifted back through the
  reclaimed level / signal-candle low and stopped the
  trade out. This is a "reclaim that did not hold",
  not a "breakdown that reversed in minutes" — the
  time scale (19–25 bars vs 1–5 bars) and the MFE
  (41–80% vs mostly <50%) are what separate it from
  Cluster 1.

### Cluster 3 — THIRD failing case: slow PE breakdown give-back
- **Count: 3 trades. Loss: −₹10,585 (19.3% of total loss).**
- Days: 2026-02-13 (−₹3,750), 2026-04-30 (−₹3,165),
  2026-05-18 (−₹3,670).
- Shape: V4 setup2_or_breakdown PE, like Cluster 1,
  but the stop is hit late: 35, 26 and 11 bars later.
  MFE 48.1%, 83.0% and 57.0% — the trade moved
  roughly half to four-fifths of the way to target,
  then reversed all the way back through the signal
  high and stopped out. February's trade later closes
  beyond target (day close 25,460.55 vs target
  25,474.80 — note: for a PE trade, "beyond" means
  below target, and the close is below it); April's
  and May's never reach target.
- Month-by-month occurrence: February, April, May
  only. It does not occur in January, March, June,
  July, August, September or October in the V5 Nifty
  leg. It is a mid-window, three-month phenomenon,
  distinct from Cluster 1 by time-to-stop and by MFE.
- Why it failed, in price-action terms: these are not
  morning whipsaws. The breakdown initially worked,
  then the day reversed (April's day closes at
  24,043.70, well above entry 23,848.75; May's closes
  at 23,644.45, above entry 23,358.50). With no
  partial booking and no trail in the provisional
  exit (stop = signal high, target = 2× risk, nothing
  in between), a trade that has banked 50–80% of its
  target distance in price terms still books a full
  stop loss when it reverses. That is an exit-rule
  failure, not an entry-direction failure.

### Cluster 4 — OR-breakout CE bull-trap
- **Count: 3 trades. Loss: −₹8,490 (15.5% of total loss).**
- Days: 2026-01-30 Skill or_breakout (−₹3,025),
  2026-06-08 Skill or_breakout (−₹3,805),
  2026-07-13 V4 setup2_or_breakout (−₹1,660).
- Shape: CE breakout above the OR high, then a fall
  back through the signal candle's low (the stop).
  January's is slow (19 bars, MFE 53.8%, later
  reaches and closes beyond target); June's is
  immediate (1 bar, MFE 0%, later touches target
  but never closes beyond it); July's is immediate
  (2 bars, MFE 23.9%, later reaches and closes
  beyond target, on a very narrow OR of 44.2 points).
  Bias is bullish twice, neutral once — so, unlike
  Cluster 1, this is not a bearish-bias-only failure.
- Month-by-month occurrence: January, June, July
  only. It does not repeat across the whole window.
- Why it failed, in price-action terms: the mirror
  image of Cluster 1 on the long side — a breakout
  close above the OR high that was the morning
  extreme, followed by a pullback through the
  signal low. June's case is the purest version:
  signal 09:30, stop in the next bar, no favourable
  move at all.

### Ranking

| Rank | Scenario | Trades | Loss (₹) | Share of ₹54,785 loss | Months |
|---|---|---|---|---|---|
| 1 | Immediate OR-breakdown PE bear-trap (Cluster 1) | 8 | −24,290 | 44.3% | Jan, Feb, Mar, Apr, May, Jun, Jul, Aug |
| 2 | Reclaim failure, setup4 CE (Cluster 2) | 2 | −11,420 | 20.8% | Jan, Oct |
| 3 | Slow PE breakdown give-back (Cluster 3) | 3 | −10,585 | 19.3% | Feb, Apr, May |
| 4 | OR-breakout CE bull-trap (Cluster 4) | 3 | −8,490 | 15.5% | Jan, Jun, Jul |

Ranking is by total loss, and the first place is
unambiguous: Cluster 1 is also first by frequency
(8 trades, twice any other cluster). The remaining
order by frequency alone would put Clusters 3 and 4
tied second (3 each) ahead of Cluster 2 (2); by loss,
Cluster 2 is second because October's single
₹8,635 loss outweighs a whole cluster of small
losses. Step 2 should therefore start with
Cluster 1, and should NOT re-rank Cluster 2 ahead
of it on the strength of one outlier trade.

### Month-by-month occurrence matrix (V5 Nifty losses)

| Month | Losses | Clusters present | Month net, V5 Nifty leg |
|---|---|---|---|
| Jan 2026 | 3 | 1 (Jan 09), 2 (Jan 14), 4 (Jan 30) | −275 (4 trades: 1 target, 3 stops) |
| Feb 2026 | 2 | 1 (Feb 06), 3 (Feb 13) | +1,325 (3 trades: 1 target, 2 stops) |
| Mar 2026 | 1 | 1 (Mar 30) | +19,545 (4 trades: 3 targets, 1 stop) |
| Apr 2026 | 2 | 1 (Apr 02), 3 (Apr 30) | +10,780 (4 trades: 2 targets, 2 stops) |
| May 2026 | 2 | 1 (May 13), 3 (May 18) | −3,705 (3 trades: 1 target, 2 stops) |
| Jun 2026 | 2 | 4 (Jun 08), 1 (Jun 29) | −8,545 (2 trades: 0 targets, 2 stops) |
| Jul 2026 | 2 | 1 (Jul 08), 4 (Jul 13) | +6,915 (4 trades: 2 targets, 2 stops) |
| Aug 2026 | 1 | 1 (Aug 19) | +6,950 (3 trades: 2 targets, 1 stop) |
| Sep 2026 | 0 | — | +6,780 (2 trades: 2 targets, 0 stops) |
| Oct 2026 (to 28 Oct) | 1 | 2 (Oct 26) | +8,195 (3 trades: 2 targets, 1 stop) |
| **Total** | **16** | | **+47,965 (32 trades)** |

Reading: a month can be net positive while still
containing a Cluster 1 loss (February, March, April,
July, August all do). "Green month" therefore does
NOT mean "Cluster 1 is fixed". Conversely, June is
the only month with zero Nifty targets, and both
its losses belong to Clusters 1 and 4 — June is
not a separate scenario, it is Clusters 1 + 4
occurring together with no winner to offset them.

### Cross-cutting checks (not separate clusters)

- Bias: bearish-bias days account for 10 losses and
  ₹31,710 of loss; neutral days 4 losses / ₹18,390;
  bullish days 2 losses / ₹4,685. Filtering to
  bearish-only would NOT remove Cluster 1 (10 of
  its 11 PE trades are bearish-bias already, and
  the 11th PE trade in Cluster 3, 2026-04-30, is
  neutral).
- Signal time: 7 of the 16 signals are at 09:30
  (the first post-OR bar), 3 more at 09:35, 3 at
  09:55, and one each at 10:00, 11:15 and 11:25.
  Cluster 1 is concentrated at 09:30–09:35 (6 of
  its 8 signals), which is why a time/confirmation
  tweak is a candidate for that cluster specifically
  (see below), not a blanket rule for all clusters.
- Risk size: only Cluster 2's October trade
  (85.95 points) is an outlier. All other losses
  have risk 16.20–50.35 points. A risk cap would
  therefore mainly change Cluster 2, not Cluster 1.
- Stop-inside-OR: 14 of 16 stops are inside the
  OR. The two exceptions are Cluster 4's
  2026-07-13 (stop 24,104.85, above OR high
  24,044.45) and Cluster 2's 2026-10-26 (stop
  22,549.75, above OR high 22,524.40 — i.e. the
  reclaim stop is just above the OR high, not
  inside it). Every Cluster 1 and Cluster 3 stop
  is inside the OR.

## FIRST failing case only — parameters that could be tweaked (candidates, NOT adopted, NOT tested yet)

This section is preparation for Step 2. Nothing here
has been tested, backtested or adopted. Step 2, as
instructed, is: apply ONE tweak to the FIRST failing
day (2026-01-09) first; if that day turns green /
at least positive, apply it to the second day with
the same scenario (2026-02-06); only when confident,
apply it to the whole month, then run and report.
Do NOT apply any of these to a whole month or to
the whole Jan–Oct window in this step.

Cluster 1 = immediate OR-breakdown PE bear-trap
(8 days listed above). The failure is: first
09:30–09:35 close below OR low + below previous-day
low is taken as a breakdown, price bounces back
into the OR within 1–5 bars and hits the signal
candle's high (the stop), and on 6 of 8 days price
later reaches the original target anyway.

Candidate parameters to tweak, in the order Step 2
should test them (one at a time, not all at once):

1. **Confirmation close (highest priority candidate).**
   Require a SECOND 5-min close below the OR low
   (or below the signal candle's low) before entry,
   instead of entering on the first 09:30–09:35
   close. On 2026-01-09 the signal is the 09:30 bar
   itself and the stop is hit at 09:40 — a second
   close would have kept the trade out entirely on
   that day, or moved entry lower. Test on
   2026-01-09 first: does the second-close rule
   avoid the stop, and does it still leave enough
   room to the target?
2. **Signal distance below the OR low.**
   Require the signal close to be at least X points
   below the OR low (X to be chosen on the first
   day only — e.g. 10 points, or 0.25× the signal
   candle's range), instead of any close below the
   OR low counting. Most Cluster 1 entries are
   only just below the OR low (entry 25,836.05 vs
   OR low 25,839.15 on 2026-01-09 is only 3.10
   points below; 2026-08-19 entry is 16.65 points
   below its OR low, so this tweak alone would not
   save every day — that is why it must be tested
   day by day, not assumed).
3. **Stop placement.**
   (a) Stop = signal candle's high + a buffer
   (e.g. +10 points, or +0.25× risk), instead of
   the signal high exactly. The bounce that stops
   Cluster 1 out typically retraces only to the
   signal high; a buffer may or may not survive
   it — test on 2026-01-09, where the stop bar's
   high needs to be checked against the buffered
   level, not assumed.
   (b) Stop = OR low (the re-entry level) instead
   of the signal high: the trade is only wrong if
   price closes back inside the OR, not if it
   merely touches the signal high. This widens
   risk, so the target (2× risk) must be
   recomputed with the new risk, not kept at the
   old target — otherwise the 2:1 reward/risk
   claim breaks.
4. **Time gate for PE breakdowns.**
   No PE breakdown entry before 09:45 (or 10:00).
   6 of the 8 Cluster 1 signals are at 09:30–09:35.
   This is a blunt tweak: it would have avoided
   most of Cluster 1, but it would also have
   avoided any genuine early breakdown on a
   winning day, so Step 2 must check it against
   the winning PE breakdown days in the same
   months (e.g. 2026-01-21, 2026-03-16), not just
   against the losing days.
5. **Re-entry rule (separate from fixing the first entry).**
   If the stop is hit and price later closes back
   below the OR low, allow ONE re-entry in the
   same direction that day. This directly uses
   the "later target" diagnostic (6 of 8 Cluster 1
   days later reach target), but it is a new
   trade, not a fix to the first trade, and it
   must be counted separately in Step 2's day test
   (first entry loss + re-entry result), not
   netted silently into a single "fixed" number.
6. **What NOT to tweak first for Cluster 1.**
   Bias filter (already bearish on 10 of 11 PE
   trades), target distance alone (the target was
   reached later on 6 of 8 days, so the target
   was not the problem), and risk cap (Cluster 1
   risks are 19.45–50.35 points, all in the normal
   range; a cap would mainly hit Cluster 2's
   October outlier). Changing any of these first
   would be random parameter tuning, which is
   exactly what this task is not.

## What Step 2 must NOT do (from the instruction)

- Do not jump from one fixed day to a whole-month
  tuned run. Sequence: first failing day
  (2026-01-09) → second day with the same
  scenario (2026-02-06) → only when confident,
  whole month → run and report back.
- Do not tune Clusters 2, 3 or 4 until Cluster 1
  is fixed and verified in that sequence. In
  particular, do not let Cluster 2's single
  ₹8,635 October loss re-rank the work: Cluster 1
  is first by both frequency (8) and loss
  (₹24,290).
- Do not claim a fix from the "later target"
  diagnostic alone. Later reaching target after
  a stop is evidence the entry/stop was early,
  not evidence that a tweaked trade would have
  banked the target — the tweaked entry, stop
  and target must actually be replayed bar by
  bar on that day.
