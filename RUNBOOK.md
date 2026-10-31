# 3-Blue-Line Runbook — failed vs passed, gap scenarios, and what we learn

Owner: Chandu. Engine: v4 (`backtest_3_blue_line_v4.py`), pure Upstox 5-min
bar-open fills, target +90 / stop -50, act+1 cost-trail, assumed costs
Rs 220/trade (Rs 40 flat + 3 pts slippage/leg), 1 lot = 30 units.
No live trading. No result here is proof the system works.

## How this runbook is used

1. Every trading day gets one row: its inputs, its gap scenario, and its
   v4 outcome (trade or no_trade, and why it was filtered if known).
2. When a day fails and a later, similar day passes, compare their input
   rows side by side. The difference is a tuning *candidate*, not a
   tuning decision.
3. A tuning candidate is only adopted after it repeats across similar
   days in the expanded sample, not after a single day. Fitting one day
   (especially October alone, 18 days / 6 trades) is overfitting.
4. Every adopted change gets a dated entry below, with the before/after
   numbers on the full sample at that time.
5. Costs are assumed Rs 220/trade until Chandu shares actual Upstox
   charges. Trading capital was never shared, so no risk % is computed.

## Definitions (provisional — Chandu to correct if his differ)

- PDH / PDC / PDL: previous trading day high / close / low.
- Full gap up: day open > PDH. Full gap down: day open < PDL.
- Partial gap up: PDC < open <= PDH. Partial gap down: PDL <= open < PDC.
- Flat-open flag: |open - PDC| <= 50 points, regardless of the class above.
  (No October pilot day opened exactly at PDC, so "flat" is a flag, not
  a separate class, until Chandu defines it differently.)
- Gap filled: gap up day whose low <= PDC; gap down day whose high >= PDC.
- Broke PDH / broke PDL: day high > PDH / day low < PDL.
  NOTE: for a full gap up, broke PDH is 100% by definition (it opened
  above PDH); for a full gap down, broke PDL is 100% by definition.
  Those two rates are not findings.
- Failed day, in this runbook, means a v4 trade that lost money.
  A no_trade day is NOT a failed trade; it is a filtered day, and its
  filter reason is logged separately.

## October pilot — passed vs the one failed v4 trade

Source: `data/banknifty-2026-10/trade_log_v4_pure_actplus1.csv`
18 days, 6 trades, 5 targets, 1 trail, 0 stops, net +Rs 12,180.

### Passed trades (5 targets, each net +Rs 2,480)

| Date | Setup | Dir | Bias | OR width | Gap vs PDC | Gap class |
|---|---|---|---|---|---|---|
| 2026-10-01 | setup4_reclaim | CE | neutral | 349.95 | -50.00 | partial gap down |
| 2026-10-13 | setup3_bounce_rejection | PE | bearish | 464.25 | -10.45 | partial gap down (near-flat) |
| 2026-10-21 | setup2_or_breakdown | PE | bearish | 181.20 | +219.75 | partial gap up |
| 2026-10-23 | setup2_or_breakdown | PE | neutral | 343.35 | +40.05 | partial gap up (near-flat) |
| 2026-10-26 | setup3_bounce_rejection | PE | bearish | 580.10 | -37.05 | partial gap down (near-flat) |

What the passed rows share: nothing single. Bias spans neutral and
bearish, OR width spans 181 to 580, gap spans down and up, and three of
the five opened within 50 points of PDC (near-flat opens). That is why
no single input from October alone should be tuned on.

### The one failed v4 trade

| Date | Setup | Dir | Bias | OR width | Gap vs PDC | Gap class | Outcome |
|---|---|---|---|---|---|---|---|
| 2026-10-27 | setup1_breakout_retest | CE | bullish | 301.25 | +54.00 | FULL gap up (> PDH) | trail, -Rs 220 |

Inputs that differ from the passed rows: it is the only full gap up in
the pilot, the only bullish-bias trade, and the only Setup 1 trade.
Day behaviour: spot high 54,654.05, then reversal, gap filled
(low 53,951.20 <= PDC 54,366.70), close 53,974.90, i.e. -391.80 vs PDC.
The pure engine entered 09:40 at 279.75 and trailed out 10:15 at cost.
Chandu's separate live fill that day (+Rs 2,715, 220.60 -> 311.10) is a
different, faster booking and is kept as a live benchmark, not as an
engine result. Difference to investigate, not to hard-code: entry was
intra-candle / lower than the next bar open, and exit was a smaller,
faster booking than the +90 target.

### PDH / PDC / PDL in the Rs 12,180 run — nothing left out

PDH = previous day high (ceiling), PDC = previous day close (bias anchor),
PDL = previous day low (floor). These are the Blue Lines, and they are
in every v4 signal test, not an extra layer added later.

How each line is actually used in v4:
- Setup 2 PE: signal 5-min close must be below the opening-range low AND
  below PDL.
- Setup 2 CE: signal close must be above the opening-range high AND
  below PDH (Rule A: a CE at or above PDH is barred unless Setup 1
  retest-hold fires).
- Setup 3 PE: blocking line = PDC if the signal close is above PDC,
  otherwise PDL. Room = signal close - blocking line, must be >= 200.
- Setup 4 CE: day must open below PDC, then reclaim with a close above
  the opening-range high, above PDC, and below PDH.
- Room in general: distance from the signal close to the next Blue
  Line / Red band in the trade direction, must be >= 200 (inf in the
  log means no Blue Line / band lay beyond the signal close in that
  direction).

Per trade in the Rs 12,180 pure run:

| Date | Setup | PDH | PDC | PDL | Entry spot | How PDL / PDC acted |
|---|---|---|---|---|---|---|
| 2026-10-01 | setup4 CE | 55,135.50 | 54,633.05 | 54,174.30 | 54,925.20 | Reclaim above PDC; room 209.80 to PDH |
| 2026-10-13 | setup3 PE | 55,416.45 | 54,918.00 | 54,708.80 | 55,181.80 | Close > PDC, so blocking = PDC, room 263.80; PDL was not the blocker |
| 2026-10-21 | setup2 PE | 55,883.70 | 55,488.10 | 55,331.10 | 55,248.55 | Close below ORL and below PDL (by 82.55); room inf, no line below |
| 2026-10-23 | setup2 PE | 55,134.45 | 54,925.70 | 54,459.35 | 54,442.05 | Close below ORL and below PDL (by 17.30); room inf, no line below |
| 2026-10-26 | setup3 PE | 54,990.50 | 54,287.35 | 53,942.35 | 54,272.90 | Close < PDC, so blocking = PDL, room 330.55 |
| 2026-10-27 | setup1 CE | 54,392.50 | 54,366.70 | 53,777.50 | 54,523.10 | PDL far below; room 220.90 to the 54,744 ledge; trail -Rs 220 |

So PDL mattered most on the PE side: it is the breakdown line for
Setup 2 and the fallback blocking line for Setup 3 when price is
already below PDC. It was not skipped in the Rs 12,180 run; the
October log carries PDH, PDC and PDL for every day, including the
12 no-trade days.

### No-trade days in October (12) — filtered, not failed trades

2026-09-30, 10-05, 10-06, 10-07, 10-08, 10-09, 10-12, 10-14, 10-15,
10-16, 10-19, 10-22. Their gap classes, from the table below, span
partial up and partial down; none was a full gap down. Filter reasons
per day are to be filled in from the engine logs as the expansion runs,
not guessed here.

## October pilot — gap scenario table (day level, all 18 days)

| Date | Gap | Class | Gap filled? | Broke PDH? | Broke PDL? | Close vs PDC | v4 outcome |
|---|---|---|---|---|---|---|---|
| 2026-09-30 | -84.05 | partial down | yes | yes | no | +373.10 | no_trade |
| 2026-10-01 | -50.00 | partial down | yes | no | yes | -182.30 | target CE |
| 2026-10-05 | +389.90 | partial up | yes | yes | no | +263.35 | no_trade |
| 2026-10-06 | +187.20 | partial up | no | yes | no | +414.30 | no_trade |
| 2026-10-07 | -159.70 | partial down | yes | yes | yes | -72.85 | no_trade |
| 2026-10-08 | -12.65 | partial down | no | no | yes | -540.50 | no_trade |
| 2026-10-09 | +231.20 | partial up | no | yes | no | +741.60 | no_trade |
| 2026-10-12 | +93.50 | partial up | yes | no | no | -338.65 | no_trade |
| 2026-10-13 | -10.45 | partial down | yes | yes | no | +563.05 | target PE |
| 2026-10-14 | -74.35 | partial down | yes | yes | no | -165.05 | no_trade |
| 2026-10-15 | +129.75 | partial up | yes | yes | no | +494.50 | no_trade |
| 2026-10-16 | +116.65 | partial up | yes | no | no | +33.50 | no_trade |
| 2026-10-19 | -16.55 | partial down | yes | no | yes | -355.90 | no_trade |
| 2026-10-21 | +219.75 | partial up | yes | no | yes | -511.20 | target PE |
| 2026-10-22 | -242.45 | partial down | yes | no | yes | -51.20 | no_trade |
| 2026-10-23 | +40.05 | partial up | yes | no | yes | -638.35 | target PE |
| 2026-10-26 | -37.05 | partial down | yes | no | yes | +79.35 | target PE |
| 2026-10-27 | +54.00 | FULL up | yes | yes | no | -391.80 | trail CE |

October alone cannot answer gap probabilities: 1 full gap up, 0 full
gap downs, 9 partial up, 8 partial down.

## Gap analytics — July to October spot, day level (81 days)

Source: `data/banknifty-2026-jul-oct/spot_daily.csv`, 2026-07-02 to
2026-10-27 (2026-07-01 excluded: no previous day). This is day-level
price behaviour, NOT v4 trade outcomes. Sample is still small; treat
rates as observed frequencies, not chances to trade on.

| Gap class | n | Gap filled | Broke PDH | Broke PDL | Closed above PDC | Closed below open |
|---|---|---|---|---|---|---|
| Full gap up | 11 | 45.5% (5/11) | 100%* | 9.1% (1/11) | 63.6% (7/11) | 72.7% (8/11) |
| Full gap down | 14 | 35.7% (5/14) | 7.1% (1/14) | 100%* | 21.4% (3/14) | 64.3% (9/14) |
| Partial gap up | 25 | 68.0% (17/25) | 60.0% (15/25) | 32.0% (8/25) | 68.0% (17/25) | 48.0% (12/25) |
| Partial gap down | 31 | 74.2% (23/31) | 29.0% (9/31) | 64.5% (20/31) | 29.0% (9/31) | 58.1% (18/31) |

\* trivial by definition, see Definitions.

Reading, in plain terms:
- Gap up coming down: full gap up days closed below their open 72.7%
  of the time, but only 36.4% closed below the previous close. So
  "coming down intraday" is common; "giving back the whole gap and
  closing down vs previous close" is less common.
- Gap down covering the gap: full gap down days filled the gap only
  35.7% of the time, and only 1 of 14 (7.1%) went on to break PDH.
  Covering the gap and then breaking the previous day high is rare
  in this 81-day window, not a base case.
- Gap down going down: full gap down days closed below their open
  64.3% of the time and closed above PDC only 21.4% of the time.
- Partial gaps fill far more often (68-74%) than full gaps (36-46%),
  which is expected: a partial gap is a smaller distance to cover.

These rates do NOT say what a v4 trade will do on a gap day. That
needs the v4 outcome by gap class, which the July-September expansion
is now computing (in progress at 2026-10-28 15:19 IST).

## Tuning log (adopted changes only — none adopted from October alone)

- 2026-10-28: v4 act+1 trail rule adopted (trail exit only after
  activation bar + 1). October pure result moved +Rs 9,480 -> +Rs 12,180
  on the same 6 trades. This was a rule Chandu specified, verified
  against his expected pure total, not a fit to a single day.
- (open) Full-gap-up Setup 1 behaviour, e.g. 2026-10-27: candidate to
  watch in expansion, not adopted. Question: does a full gap up +
  bullish bias + Setup 1 behave differently from partial-gap Setup 1?
  October has only one such day, so no answer yet.

## Open questions for Chandu (definitions data cannot answer)

1. Flat: is |open - PDC| <= 50 the right flat threshold, or do you
   define flat as open inside the previous day range, or something else?
2. For a failed vs passed pair, which inputs matter most to you for
   the comparison: bias, OR width, gap size, room to next level,
   entry spot vs PDH, or something else? The runbook currently logs
   all of them.
3. Red band exact definition (order-block anchor/buffer): still open
   from earlier work; v2 bands sit ~10-44 points below your levels.

## July-September expansion — completed 2026-10-28, verdict changed

Primary result, no bands (PD/OR only, Setup 1 skipped), same v4 rules,
pure bar-open fills, Rs 220/trade. Each expiry run separately. Logs
verified from the per-expiry files, not just reported:

| Expiry | Days | Trades | Wins | Net | Exits |
|---|---|---|---|---|---|
| 2026-07-28 | 20 | 6 | 0 | -Rs 7,320 | 4 stop, 2 trail |
| 2026-08-25 | 17 | 6 | 0 | -Rs 10,320 | 6 stop |
| 2026-09-29 | 20 | 3 | 0 | -Rs 5,160 | 3 stop |
| 2026-10-27 (pilot) | 18 | 6 | 5 | +Rs 12,180 | 5 target, 1 trail |
| **July-October combined** | **75** | **21** | **5** | **-Rs 10,620** | **13 stop, 5 target, 3 trail** |

Combined: win rate 23.8%, expectancy -Rs 506/trade, profit factor
0.54, peak-to-trough drawdown Rs 22,800. All 5 wins are October.
By setup combined: setup2 breakdown 11 trades, -Rs 10,520;
setup2 breakout 2, -Rs 3,440; setup3 4, +Rs 3,020; setup4 3, +Rs 540;
setup1 1, -Rs 220. By direction: CE 6, -Rs 3,120; PE 15, -Rs 7,500.

Failed-vs-passed lesson, in runbook terms: the failed pattern is not
one bad day. July, August and September each produced zero wins, and
most losses were full -Rs 1,720 stops, not trails. October's 5 targets
are the exception to explain, not the baseline. Tuning October alone
would have fitted the outlier.

V2-band second pass (NOT user bands, labelled as such):
July 7 trades / -Rs 7,540, August 1 / -Rs 1,720, September 1 / -Rs 1,720,
total 9 trades / 0 wins / -Rs 10,980. It improved July-September net
by Rs 11,820 only by blocking 7 losing stops (7 x Rs 1,720 = Rs 12,040)
minus 1 added July Setup 1 trail (-Rs 220). No v2-band trade won in
those months. Likely mechanism, not proven: many v2 bands per day
(July 33, August 170, September 424 over the windows) make the
room-to-next-level test block most signals. That is filtering, not
evidence v2 bands pick winners.

Gap class, v4 outcome, 75 window days (not all calendar days between
July and October; windows are expiry-month days up to each expiry,
and September has no 2026-09-14 candles in the Upstox pull):
full gap down 13 days, 5 trades, 0 wins, -Rs 8,600; full gap up 10 days,
1 trade, 0 wins, -Rs 220; partial gap down 30 days, 10 trades,
3 wins, -Rs 3,100; partial gap up 22 days, 5 trades, 2 wins, +Rs 1,300.
All 5 wins sit in partial-gap days, all in October. Full-gap broke
rates are trivial by definition and are not findings.
Per-day gap rows and logs: `data/banknifty-2026-07/`,
`data/banknifty-2026-08/`, `data/banknifty-2026-09/`,
combined `data/banknifty-2026-jul-oct/trade_log_v4_pure_actplus1_combined.csv`
and `gap_table_v4_combined.csv`.

Note on a flagged August trade: 2026-08-25 setup4 CE strike 57,500 at
entry spot 57,620.55 is the correct expiry-day ITM strike (ATM rounded
57,600 minus 100), not an ATM error.

## Audit claim tested 2026-10-28 — strict Setup 2 bias filter does NOT fix it

A pasted CSV + audit claimed the -Rs 22,800 came from (1) unfiltered
Setup 2 breakdowns, (2) weekly vs monthly expiry gamma traps, and
(3) a CSV column-shift that misread October wins as zeroes, and
proposed allowing Setup 2 PE only when closing strength < 35% and
Setup 2 CE only when >= 80%. Each claim was checked against real
Upstox option candles, and the filter was actually re-run
(`backtest_v4_strict_setup2.py`, same data, same costs):

- The pasted CSV is NOT the verified pure log. Same entries, impossible
  exits: Jul 6 58300 PE claimed target 773.50 at 11:15, actual bar
  685.50-695.75, target never reached after entry, stop hit 12:10 at
  615.25; Jul 8 57700 PE claimed 789.90 at 10:35, actual bar
  535.40-585.00, stop hit 09:45 at 642.00; Aug 10 57600 PE claimed
  652.75 at 10:35, actual bar 492.55-505.45, stop hit 10:15 at 501.00;
  Aug 11 claimed 627.00 at 10:35, actual bar 500.05-522.45, stop hit
  10:55 at 483.30. October rows in that CSV also use the earlier
  placeholder live fills (380->470, 410->500, 220.60->311.10), not
  pure bar-open fills.
- Weekly vs monthly is invalid for 2026: Bank Nifty weekly options
  were discontinued November 2024, monthly expiry only on the last
  Tuesday. All July-September windows here are monthly expiries.
- Column-shift does not explain -Rs 22,800: our logs are read by
  column name in pandas, and the engine printed its totals during
  the run, independent of any CSV re-read. October wins are present
  in our logs, not zeroes.
- Strict filter re-run, true engine re-run (not post-hoc dropping):
  July 5 trades / 0 wins / -Rs 5,600; August 5 / 0 / -Rs 8,600;
  September 2 / 0 / -Rs 3,440; July-September total 12 / 0 /
  -Rs 17,640 (vs -Rs 22,800 unfiltered). October with the same filter:
  5 trades / 4 wins / +Rs 9,700, because the neutral Oct 23 PE win
  is blocked. Combined July-October strict: 17 trades / 4 wins /
  -Rs 7,940 (vs -Rs 10,620). So the filter saves Rs 5,160 in
  July-September, costs Rs 2,480 in October, and still leaves every
  month except October winless. It is not a fix.

## Why October worked and July-September did not — walkthrough 2026-10-28

This is a diagnostic on 21 trades, not a new rule. Every point below
is a hypothesis to test, not an adopted change.

### Points to highlight

1. Setup 2 is the main drag. Setup 2 breakdown: 11 trades, 2 wins,
   net -Rs 10,520. Setup 2 breakout: 2 trades, 0 wins, -Rs 3,440.
   Setup 3: 4 trades, 2 wins, +Rs 3,020 (the only positive setup).
   Setup 4: 3 trades, 1 win, +Rs 540. Setup 1: 1 trade, 0 wins, -Rs 220.
   October's wins were spread (setup4 1, setup3 2, setup2 2), so
   October was not a single-setup story.
2. Wins are fast, losses grind. Median time to exit: wins 15 minutes,
   losses 37.5 minutes. October wins: 30, 65, 15, 5 and 15 minutes to
   target. Slow losses to stop: Aug 14 in 205 minutes, Sep 7 in
   215 minutes, Jul 6 in 115 minutes, Jul 15 trail in 145 minutes.
   The exception is Oct 13, a win that took 65 minutes.
3. Losses reverse immediately, wins continue immediately. At the
   exit bar, spot had moved against most PE losses by +42 to +176
   points, and against CE losses by -71 to -126 points. Wins moved
   +115 (CE) or -115 to -245 (PE) in favour. Two losses were whipsaws
   in day terms (Jul 8 day close -915 vs entry, but stop hit in
   10 minutes at +124 spot; Jul 15 day close -341 vs entry, but
   trail at cost), the rest were true reversals by day close.
4. Room is vacuous for PE breakdowns. Every setup2 breakdown trade
   (11/11) has room = inf, because all PD lines sit above the signal
   close once price is below PDL. The >= 200 room filter therefore
   does not filter breakdowns at all. For CE breakouts room is finite
   to the next level above, so the filter is asymmetric.
5. Bias, OR width, gap and signal time do NOT separate wins from
   losses in this sample. Bias: bearish 3 wins / 9 losses, neutral
   2 / 6, bullish 0 / 1. OR width median: wins 350, losses 299;
   the worst bucket is OR 201-350 (2 wins / 11 losses). Signal
   before 10:00: 3 wins / 7 losses; after 10:00: 2 / 9. Signal candle
   body and entry vs PDL also overlap heavily between wins and
   losses. Any rule built on one of these alone is fitting noise.
6. Near-misses cluster just under +90. All 3 trail trades reached
   +84 to +87 in premium before reversing to cost (Jul 1, Jul 15,
   Oct 27). Two stops also reached +55 to +63 before reversing
   (Jul 28, Aug 14). A smaller target would convert some of these,
   but see step 3 below: it does not turn the sample positive on
   its own.
7. October also had a data advantage: it used your supplied bands,
   July-September no-band runs skipped Setup 1 entirely. That does
   not explain October's setup2/setup3/setup4 wins, which do not
   depend on bands except for room, but it does mean the comparison
   is not perfectly like-for-like.

### Steps to increase win ratio and accuracy — test in this order

Each step must be tested on July-October AND validated on a fresh
period (Oct 28 onward) before adoption. In-sample improvement alone
is not adoption.

1. Fix the PE room test. Replace inf room for breakdowns with a real
   downside test, e.g. distance to the next structural support below
   entry (intraday low, OR low, or a supplied band), or require a
   minimum distance below PDL. Test whether this blocks the
   immediate-reversal breakdowns without blocking Oct 21 / Oct 23.
2. Test a time / stall exit. Tested 2026-10-28 on premium closes
   (only for trades still open at that time; post-exit closes do
   not count). Rule: at +60 minutes, exit at that bar's close if
   premium close < entry premium, otherwise keep the original
   target/stop/trail. Long trades affected: Jul 6 close 690.00 vs
   entry 683.50 (up, would NOT exit under a strict down-only rule;
   see note), Jul 15 657.20 vs 666.00 (down, exit net -Rs 484 vs
   trail -Rs 220, worse by Rs 264), Aug 11 507.65 vs 537.00 (exit
   net -Rs 1,100 vs -Rs 1,720, saves Rs 620), Aug 14 412.35 vs
   381.05 (up, exit net +Rs 719 vs -Rs 1,720, saves Rs 2,439),
   Aug 17 313.80 vs 344.65 (exit net -Rs 1,145 vs -Rs 1,720, saves
   Rs 575), Sep 7 542.85 vs 534.60 (up, exit net +Rs 27 vs -Rs 1,720,
   saves Rs 1,747), Oct 13 562.00 vs 547.35 (up, survives, still
   goes on to target). Note: the +60 rule as stated (exit only if
   down) does NOT exit Jul 6, Aug 14 or Sep 7, because they were
   up at +60; the saving above for Aug 14 and Sep 7 comes from
   exiting at +60 regardless of up/down, at a profit, instead of
   waiting for a later stop. A cleaner version to test in the
   engine is therefore: exit at +60 at that bar's close, whatever
   the premium, unless target already hit. On that version the
   six long losses above become: Jul 6 net -Rs 25 (vs -Rs 1,720),
   Jul 15 -Rs 484 (vs -Rs 220), Aug 11 -Rs 1,100 (vs -Rs 1,720),
   Aug 14 +Rs 719 (vs -Rs 1,720), Aug 17 -Rs 1,145 (vs -Rs 1,720),
   Sep 7 +Rs 27 (vs -Rs 1,720), total improvement about
   Rs 6,812, taking combined July-October from -Rs 10,620 to
   about -Rs 3,808, still negative, and Oct 13 would exit at
   +60 for +Rs 219 instead of +Rs 2,480 if the rule fires before
   its 65-minute target, costing Rs 2,261. Net of that Oct 13
   cost, the +60 exit-all version is about -Rs 6,069 combined.
   This is an in-sample diagnostic, not an adopted rule; it must
   be run in the engine and validated on Oct 28 onward.
3. Test smaller targets, honestly. In-sample first-touch math:
   +50 target converts 5 losing trades (3 trails + Jul 28 + Aug 14)
   to wins, giving 10 wins / 11 losses, net about -Rs 6,120 (win
   Rs 1,280, loss -Rs 1,720). +30 converts 8, giving 13 / 8, net
   about -Rs 4,920. Neither turns July-October positive, because
   7 losing trades never reached even +20 before stopping. Smaller
   targets help only if combined with a filter for those 7.
4. Filter the straight-against trades. 7 losing trades never reached
   +20 in premium before stopping (Jul 8, Jul 24, Aug 10, Aug 17,
   Aug 19, Aug 25, Sep 11). Test pre-entry confirmation that could
   have blocked them: a second close in favour, a minimum signal
   candle body, or spot continuation in the next bar, and check
   that it does not also block Oct 23 (target in 5 minutes) or
   Oct 21 (target in 15 minutes).
5. Keep Setup 3 and Setup 4, question Setup 2 breakout. Setup 3 is
   the only positive setup so far; Setup 2 breakout is 0/2 and
   Setup 2 breakdown is 2/11. Do not delete Setup 2 on 21 trades,
   but give it the strictest test in steps 1, 2 and 4, and report
   it separately by setup in every future run.
6. Do not adopt the strict bias filter as a fix. Already tested:
   July-September 12 trades / 0 wins / -Rs 17,640, October
   +Rs 9,700 after losing the Oct 23 win, combined -Rs 7,940.
   It helps, it does not fix.

Breakeven reminder: at +90 / -50 with Rs 220 costs, a win nets
Rs 2,480 and a loss nets -Rs 1,720, so breakeven win rate is
1720 / (2480 + 1720) = 41.0%. Current combined win rate is 23.8%.
Any step that raises win rate must be judged against that bar, not
against October alone.

## 50-point target test — engine re-run 2026-10-28

User direction: focus on +50 points only, increase lots if needed.
Test: v4 engine, stop still -50, target changed to +50 only, same
data, same costs Rs 220/trade for 1 lot, same act+1 trail.

| Month | Trades | Wins | Net (1 lot) |
|---|---|---|---|
| July | 6 | 3 | -Rs 1,320 |
| August | 6 | 1 | -Rs 7,320 |
| September | 3 | 0 | -Rs 5,160 |
| October | 6 | 6 | +Rs 7,680 |
| **Combined** | **21** | **10 (47.6%)** | **-Rs 6,120, expectancy -Rs 291/trade** |

Versus +90 target combined: -Rs 10,620, 5 wins. So +50 improves
combined by Rs 4,500 and doubles the win count, but does NOT turn
it positive. October alone is worse at +50 (+Rs 7,680 vs +Rs 12,180
at +90), because 5 wins shrink from Rs 2,480 to Rs 1,280 each
(-Rs 6,000) and only Oct 27 flips from trail -Rs 220 to target
+Rs 1,280 (+Rs 1,500).

Breakeven at +50 / -50, 1 lot: win Rs 1,280, loss -Rs 1,720,
breakeven win rate = 1720 / (1280 + 1720) = 57.3%. Actual 47.6%
is about 2 wins short of breakeven (12 wins would give about
-Rs 120, 13 wins would be positive).

Lots do not change the breakeven ratio, they scale it. At 2 lots
(approx costs Rs 400/trade: Rs 40 flat + slippage on 60 units),
win about +Rs 2,600, loss about -Rs 3,400, total about -Rs 11,400,
drawdown roughly double. At 3 lots, total about -Rs 16,680.
Increasing lots on a negative-expectancy system increases the
loss, it does not fix the win rate. Lots only help once expectancy
is positive and capital / risk limits allow it, neither of which
is established here (capital still not shared).

## Fix grid for July-September losses — engine re-runs 2026-10-28

All variants are true engine re-runs, same data, same Rs 220/trade
for 1 lot, unless stated. No variant turns July-September or
July-October positive in-sample.

| Variant | July | August | September | July-Sept | October | Combined |
|---|---|---|---|---|---|---|
| Base v4, target 90 | -7,320 | -10,320 | -5,160 | -22,800 | +12,180 | -10,620 |
| Target 50 only | -1,320 | -7,320 | -5,160 | -13,800 | +7,680 | -6,120 |
| Stall 60, target 90 | -5,889 | -6,687 | -3,412 | -15,988 | +9,920 | -6,068 |
| Strict bias, target 50 | -2,600 | -5,600 | -3,440 | -11,640 | +6,400 | -5,240 |
| Stall 60, target 50 | -1,389 | -6,126 | -3,412 | -10,927 | +6,620 | -4,307 |
| Strict + stall 60, target 50 | -2,669 | -4,980 | -1,692 | -9,341 | +5,340 | -4,001 |
| No Setup 2 at 09:30, target 50 | -1,320 | -7,320 | -5,160 | -13,800 | +7,680 | -6,120 |

Best in-sample is strict + stall 60 + target 50: combined -Rs 4,001,
July-September still -Rs 9,341. That is a 62% smaller combined loss
than base, not a reversal.

No-09:30 test, corrected: blocking the 09:30 Setup 2 signal did NOT
save Jul 8, Aug 10, Aug 11 or Aug 19. The next candle (09:35 signal,
09:40 entry) fired the same breakdown and still stopped, same net.
Delaying entry by 5 minutes is not a fix for those days.

Conclusion from the grid: target, stall and bias filters each help,
stacking them helps more, but none of them, alone or stacked,
reverses July-September to positive on this sample. A reversal
needs a different signal filter (e.g. a confirmation that the
breakdown actually continues, tested properly), or accepting that
Setup 2 breakdown as coded does not work in these months. Stacking
three filters on 21 trades is also high overfit risk: the best
combo must be validated on Oct 28 onward before any adoption.

## Different-approach lead tested — drop Setup 2, true re-run 2026-10-28

Lead identified from the setup breakdown: Setup 2 was the whole
loss, non-Setup 2 was positive post-hoc. True engine re-run with
Setup 2 disabled (not post-hoc deletion, so later signals on
Setup 2 days can fire):

Target 90, no Setup 2:
July 3 trades / 0 wins / -Rs 2,160; August 1 / 0 / -Rs 1,720;
September 1 / 0 / -Rs 1,720 (a replacement Setup 4 pullback on
Sep 11, the day of the original Setup 2 breakout, also stops);
October 4 / 3 wins / +Rs 7,220. Combined 9 trades / 3 wins /
+Rs 1,620. July-September alone: 5 trades / 0 wins / -Rs 5,600.

Target 50, no Setup 2:
July 3 / 2 wins / +Rs 840; August 1 / 0 / -Rs 1,720;
September 1 / 0 / -Rs 1,720; October 4 / 4 wins / +Rs 5,120.
Combined 9 trades / 6 wins / +Rs 2,520. July-September alone:
5 trades / 2 wins / -Rs 2,600.

Correction to the post-hoc lead: post-hoc non-Setup 2 was
+Rs 3,340 at target 90 and +Rs 4,240 at target 50 on 8 trades.
True re-run is smaller (+Rs 1,620 / +Rs 2,520 on 9 trades)
because September gains a replacement losing trade. The lead
survives, but it is NOT a July-September fix: July-September
alone is still negative without Setup 2, and October still
carries the combined result. Sample is only 9 trades. Plan:
validate Setup 3/4/1 only, target 50, stall 60, 1 lot, on Oct 28
onward paper only, before any adoption or lot increase.

## V5 test — three fixes from the doc, engine re-runs 2026-10-28

V5 as coded (`backtest_v5.py`): Fix 1 Setup 2 signal only after
09:30, strict bias for Setup 2 (PE bearish only, CE bullish only),
Fix 2 bounded room for Setup 2 PE (Red band edge below close if
any, else PDL minus lowest prior daily low, finite not inf),
Fix 3 doc stall at exactly entry + 60 minutes if premium close
minus entry is under 20 points, exit at that close.

| V5 version | July | August | September | July-Sept | October | Combined |
|---|---|---|---|---|---|---|
| V5 main, target 90 | -2,449 | -6,880 | -1,692 | -11,021 | +7,440 | -3,581 |
| V5 main, target 50 | -949 | -3,880 | -1,692 | -6,521 | +5,340 | -1,181 |
| V5 literal room, target 90 | -2,449 | -3,440 | -1,720 | -7,609 | +4,960 | -2,649 |
| V5 literal room, target 50 | -949 | -3,440 | -1,720 | -6,109 | +4,060 | -2,049 |

V5 main target 50 is the closest to breakeven yet: 15 trades,
combined -Rs 1,181, versus base -Rs 10,620. It is still negative,
and July-September alone is still -Rs 6,521.

What V5 actually does, trade by trade:
- October Setup 2 win Oct 23 is blocked in V5 main by strict
  bias (neutral 69.08, not bearish), even though it was a win.
  October V5 trades are Oct 1, Oct 13 (stall +Rs 219, not target),
  Oct 21, Oct 26, Oct 27.
- Literal room version blocks BOTH October Setup 2 wins, Oct 21
  and Oct 23, as warned: Oct 21 PDL 55,331.10 minus nearest prior
  low below it 55,279.00 = 52 < 200; Oct 23 PDL 54,459.35 minus
  54,383.15 = 76 < 200. Literal room is therefore harmful if
  support means every prior daily low.
- V5 main bounded room, as coded, blocks many new-low breakdowns
  because the fallback (PDL minus lowest prior low) often equals
  0 when PDL itself is the lowest prior low. That is why July
  trades fall from 6 to 4 and August from 6 to 4. It improves the
  net by trading less, not by proving those breakdowns were
  bad on a structural test. The room definition still needs
  Chandu's clarification: Red bands only, or a different support
  set, not every daily low.
- Doc stall (gain < 20 at +60) differs from exit-all at +60:
  Aug 14 at +60 was up 31 points, so doc stall does NOT exit it,
  while exit-all would have booked +Rs 719. V5 August still
  stops Aug 14 at target 90 and targets it at target 50.

V5 is not adopted as a fix. It is the best in-sample variant so
far at target 50, but it is still negative combined, still
negative in July-September alone, and it is three more filters
on a small sample.

## V6 test — strict support, neutral PE accommodation, 90-min time-stop, 2026-10-28

V6 as coded (`backtest_v6.py`): Fix 1 (no Setup 2 at 09:30)
kept; Setup 2 PE bearish always, neutral only if signal candle
closes in bottom 25% of its range; CE bullish only; room only
from Red bands or 3+ day daily-low shelves (prior 20 days,
50-point tolerance), otherwise room = inf and velocity required
(signal candle range > mean range of previous post-OR bars that
day, up to 10); time-stop 90 close-based (at entry + 90 minutes,
if premium close minus entry is under 40, exit at that close).

| V6, close-based time-stop | July | August | September | July-Sept | October | Combined |
|---|---|---|---|---|---|---|
| Target 90 | -3,742 | -7,761 | -2,450 | -13,953 | +12,180 | -1,773 |
| Target 50 | -2,242 | -7,320 | -2,450 | -12,012 | +7,680 | -4,332 |

Max-high time-stop variant: August target 90 returns to
-10,320 (no Aug 14 saving), all other months identical.
V6 does NOT flip July-September positive, and at target 50 it
is worse than V5 main (-Rs 4,332 vs -Rs 1,181). At target 90 it
is better than V5 main (-Rs 1,773 vs -Rs 3,581) only because
October returns to the full base +Rs 12,180.

Trade-level findings:
- Oct 23 DOES survive V6, contrary to the interim velocity
  warning, because velocity in the engine uses previous
  post-OR bars only (09:30-09:50), not the OR bars, so its
  122.50 range passes that average. October V6 is identical
  to base v4: 6 trades, +Rs 12,180 at target 90, +Rs 7,680
  at target 50.
- Aug 14 IS saved only on the close reading: time-stop at
  12:05 close 416.35, gain +35, net +Rs 839, versus stop
  -Rs 1,720, a saving of about Rs 2,559. On the max-high
  reading it touched +63 by 11:30, so it survives the
  time-stop and still stops at -Rs 1,720.
- Time-stop also hurts one trade: Jul 15 timestop net -Rs 589
  versus trail -Rs 220, because its 90-minute close is below
  cost.
- Jul 8 is blocked in V6 (velocity or shelf), but Jul 24 and
  Jul 28 return as stops, and Sep 2 CE stays blocked
  (neutral, CE bullish only). September V6 has only Sep 7
  timestop (-Rs 730, saving Rs 990 vs stop) and Sep 11
  pullback stop.

Conclusion: V6's support definition is cleaner than V5 literal
room, and it protects October fully, but it removes the
trading-less filters that made V5 target 50 the best variant.
It is not adopted as a fix.

## V5.5 hybrid, bull switch, and ATR tests, 2026-10-28

All tests are true engine re-runs, target 90 and 50, July-Sept
bull months defined by month (not by 50-day MA, which does
not support bull in this data: September closes are 0/16
above the 50-day MA, July has no 50-day MA from data starting
Jul 1, and price fell from about 57,918 on Jul 1 to 54,259 on
Sep 29).

| Variant | July-Sept T90 | Oct T90 | Combined T90 | July-Sept T50 | Oct T50 | Combined T50 |
|---|---|---|---|---|---|---|
| Hybrid (V5 room + V6 velocity + time-stop90 + neutral PE) | -10,513 | +12,180 | +1,667 | -8,572 | +7,680 | -892 |
| Bull all-CE (PE disabled Jul-Sep, all CE allowed) | -5,380 | +12,180 | +6,800 | -3,880 | +7,680 | +3,800 |
| Bull literal (Jul-Sep only Setup1 + Setup4 reclaim CE) | -1,940 | +12,180 | +10,240 | -440 | +7,680 | +7,240 |
| ATR (V6 + Setup2 PE range >= 1.5 x mean post-OR 5m range, prior 14 days) | -6,343 | +12,180 | +5,837 | -4,402 | +7,680 | +3,278 |

None of these makes July-September itself profitable. Every
combined positive comes from October outweighing a smaller
July-September loss, not from July-September turning positive.
Bull literal July-September is closest to breakeven at
target 50 (-Rs 440) only because it trades twice in 57 days
(Jul 1, Aug 25) and zero times in September — Setup 1 needs
bands, which July-September does not have, and no Setup 4
reclaim fired in September under the literal rule. That is
not a profitable July-September system, it is almost no
trading in July-September.

Other findings:
- Hybrid target 50 combined -Rs 892 is now the closest to
  breakeven at target 50, slightly better than V5 main
  -Rs 1,181, and hybrid target 90 is the first positive
  combined at target 90 besides the no-Setup 2 lead.
  October is untouched in hybrid (6 trades, +Rs 12,180).
- ATR blocks all July Setup 2 PE trades (July becomes
  Setup 3/4 only: -Rs 302 at target 90, +Rs 1,198 at
  target 50), but August still has 3 Setup 2 PE trades
  passing ATR and stopping, so August remains -Rs 4,321
  at target 90.
- The blueprint filter "skip OR width > 450" was NOT used
  as a blanket filter, because it would kill Setup 3 wins
  at Oct 13 (width 464) and Oct 26 (width 580).
- A per-month trade cap of 4 is not a tradable rule in
  advance; it is an outcome of V5's filters, not a filter
  itself, unless conviction ranking is defined first.

No V5.5 variant is adopted. The open question remains:
what actually wins in July-September, not what merely
trades less there while October carries the total.

## Empirical audit, 2026-10-28 — summer cannot be salvaged by current engine

Audit agreed with the test results: July-September was a
distribution/downtrend phase, Bank Nifty falling about
3,600 points from 57,918 on Jul 1 to 54,259 on Sep 29, not a
bull expansion. Setup 2 PE breakdowns acted as bear traps in
that phase, and long Setup 1/4 failed in part because
historical Red Bands are missing for those months. All
V5.5 variants are tested and not adopted. The closest
variant, bull literal -Rs 440 at target 50, is capital
starvation (2 trades in 57 days, 0 in September), not edge.

Two paths posed by the audit, choice not yet made:
Path A — generate historical Red Bands for Q3 (60-session
rolling centroid clustering backward through June-September)
to give Setup 1/4 anchors for summer.
Path B — build a dedicated distribution rejection model
(VWAP / upper-band rejection, fading rallies at resistance
in downtrends) instead of chasing breakdowns at lows.
Separate question posed: pause summer backtesting and
expand the October engine forward into November/December
2026, or build Q3 bands first.

Correction to the audit wording: v4 is the production
baseline for forward paper testing only, NOT live-ready.
It is an 18-day, 6-trade pilot, not validated on a fresh
period, and no live trading is recommended on it.

## January-October run, completed 2026-10-28 — most efficient version

Jan-Jun fetched via Upstox, per expiry, previous day included.
March expiry correction: Upstox returns 0 spot/contracts
for 2026-03-31, 426 contracts for 2026-03-30, so March
window used was Feb 27 to Mar 30. Jan 17 days, Feb 18,
Mar 19, Apr 18, May 17, Jun 21 spot days. Logs in each
month dir, summary at data/banknifty-2026-jan-oct/summary.csv.
Verified from the logs, not just the subagent report.

Jan-Jun:
v4 T90 21 trades / 6 wins / -Rs 420; v4 T50 21 / 13 / +Rs 4,380
Hybrid T90 15 / 3 / -Rs 4,200; Hybrid T50 15 / 8 / -Rs 300
No-Setup2 T90 4 / 1 / -Rs 1,180; No-Setup2 T50 4 / 2 / -Rs 880

Jan-Oct combined (Jan-Jun + Jul-Oct, Jul-Oct not re-run):
No-Setup2 T50 +Rs 1,640, 13 trades / 8 wins, +Rs 126/trade
No-Setup2 T90 +Rs 440, 13 / 4, +Rs 34/trade
v4 T50 -Rs 1,740, 42 / 23, -Rs 41/trade
Hybrid T50 -Rs 1,192, 32 / 17, -Rs 37/trade
Hybrid T90 -Rs 2,533, 32 / 10, -Rs 79/trade
v4 T90 -Rs 11,040, 42 / 11, -Rs 263/trade

Most efficient by net and net per trade: no-Setup2 at
target 50, +Rs 1,640. Caveat, recorded with it: only 13
trades in 185 window days, Jan-Jun half alone negative
(-Rs 880 on 4 trades), Jan-Oct positive comes entirely
from Jul-Oct (+Rs 2,520). It trades about 0.5 times per
week, well below the 2-3 quality trades per week agenda,
so it is not a frequency solution either. v4 T50 is the
most-sampled near-breakeven candidate (-Rs 1,740 on 42
trades). No version is adopted as proven; forward paper
validation remains the next step, no live trading, no
lot increase.

## Next updates to this file

- 2026-10-28 backtest after the 15:30 close: add its row and compare
  it against your shared conditional triggers (54,200 CE above 54,185;
  54,000 CE pullback above 54,050 after dip to 54,019-54,050;
  54,400 PE below 54,415 after rally into 54,415-54,449).
- 2026-10-28 backtest after the 15:30 close: add its row and compare
  it against your shared conditional triggers (54,200 CE above 54,185;
  54,000 CE pullback above 54,050 after dip to 54,019-54,050;
  54,400 PE below 54,415 after rally into 54,415-54,449).
