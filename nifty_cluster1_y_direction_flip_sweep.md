# Family (y) — Direction-flip AS A SEPARATE SYSTEM, not a PE fix

**Verdict first: family (y) FAILS its own pass bar and is exhausted. Nothing is adopted.**
The flip system, judged alone, converts only 2 of 8 genuine flip trades to green
(25%, bar 60%) and loses ₹15,310 in total (bar: positive). 2 Apr is a genuine
flip winner (+₹3,250) but it is 1 of 17 universe days, not a system. Flip P&L is
NOT netted against PE losses anywhere in this report, and no PE trade is kept
alive by a flip overlay. No out-of-sample validation run is needed for a system
that fails in-sample, and none is claimed.

Paper only, Nifty only, no orders, no live-trading recommendation.

## 1. Frozen definition — stated before scoring, no re-tuning after outcomes

**Universe day:** a day on which the (lA) PE system has BOTH a morning stop AND
a re-entry stop. (lA) = BN-confirmed rescan morning
(`combined_confirm_sweep.rescan_trade`) + `scan_reentry` variant "lA"
(`extended_window_sweep`): morning-phase scan-skip to 11:30, afternoon
stop-on-first-fail to 15:05, band [10, rescan risk].

**Mode scope (stated, so the universe is auditable):** primary scan uses V4
rescan mode for every day; the documented Cluster 1 days are additionally run
with their documented modes (2 Apr = skill) and, if the documented-mode result
differs, the documented mode replaces V4 for that date, deduplicated by date and
counted once. Days that would be two-stop under a skill-mode morning alone, but
not under the (lA) V4/documented rule, are therefore NOT in this universe —
this is the (lA) two-stop universe, not every conceivable PE variant's universe.

**Flip trigger (ONE definition, picked before results):** the FIRST 5-min bar
AFTER the re-entry stop bar whose CLOSE is above the Nifty OR low.
Entry = next bar open. Stop = flip signal bar low (CE, mirrored).
Target = entry + 2 x risk. Square-off at the 15:10 close.
100 shares, ₹40/trade, one flip trade per day max.
Flip-signal scan runs from the bar after the re-entry stop bar through the
15:05 bar (so entry is at most 15:10). Stop-before-target on every bar
including the entry bar (mirroring PE ordering). If there is no next bar after
the flip signal bar, the day is no-trade.

**Knife-edge rule (stated before results):** a flip trade with risk < 5 points
is flagged as an artefact, reported with its net, but EXCLUDED from the genuine
green count and from the pass-bar green rate. The genuine total (artefacts
removed) is reported alongside the all-traded total.

Green = net > ₹0. No-trade counted separately from green throughout.

**Pass bar for the flip system itself (not the PE bar):** flip green ≥ 60% on
flip days AND flip total positive AND no single flip trade > 50% of flip total
AND every universe day reported (no cherry-picking). An in-sample pass would
still need out-of-sample validation (held-out year / forward paper, thresholds
frozen) before any adoption. That condition is moot here because (y) fails
in-sample.

**Baseline reproduction:** the (lA) engine was re-run, not copied. On the 8
Cluster 1 days it reproduces 5/8, −₹2,720, exactly as in (x). Previous best kept
remains (lA) (−₹2,720, 5/8), and (lA) itself is not adopted. No 1-min variant
from (x) is carried forward, and no 5-min PE variant, partial, target multiple,
guard, or cooling delay is re-run here. Flip entries are 5-min only, as defined.

## 2. Universe — 17 days out of 451 scanned

Scanned: 451 trading days present in the Nifty 5-min cache, 2025-01-01 to
2026-10-28 (days with missing Nifty or Bank Nifty day data skipped; none of the
17 universe days is affected). Universe (two PE stops under (lA)): **17 days**
(13 in 2025, 4 in 2026). Flip traded: 11 days (8 genuine, 3 artefact).
No-trade (no bar closes above the OR low after the second stop, through 15:05):
**6 days**. A two-stop day is rare — 17/451 = 3.8% of scanned days — and a flip
signal after it is rarer still.

Afternoon reversal magnitude is reported per day below as diagnostic context
only (minimum low after the second stop bar, maximum close after it, 15:10-bar
close, and 15:10 close minus minimum low). It is NOT the flip trade's outcome:
on most universe days price recovers only a few tens of points, nowhere near
enough to pay a flip target, and on 2 Apr it recovers ~542 points — the outlier
that motivated this family, not the norm.

## 3. Results — every universe day

| Date | PE morning (signal / net) | PE re-entry (signal / net) | PE day net | Flip signal | Flip entry / stop / risk | Flip exit (time) | Flip net | Artefact? | After 2nd stop: min low / max close / 15:10 close / reversal |
|---|---|---|---|---|---|---|---|---|---|
| 2025-01-10 | 09:30 / −₹6,355 | 11:40 / −₹5,630 | −₹11,985 | 12:20 | 23,516.90 / 23,513.90 / 3.00 | stop 12:25 | −₹340 | **Yes (<5)** | 23,396.85 / 23,541.80 / 23,412.20 / +15.35 |
| 2025-02-07 | 10:15 / −₹7,310 | 12:50 / −₹2,850 | −₹10,160 | 13:25 | 23,567.40 / 23,546.10 / 21.30 | stop 13:50 | −₹2,170 | No | 23,443.20 / 23,580.15 / 23,573.70 / +130.50 |
| 2025-02-10 | 09:40 / −₹2,525 | 09:55 / −₹1,385 | −₹3,910 | — | — | no-trade | — | — | 23,316.30 / 23,401.30 / 23,380.35 / +64.05 |
| 2025-02-28 | 09:35 / −₹1,925 | 10:00 / −₹1,055 | −₹2,980 | — | — | no-trade | — | — | 22,104.85 / 22,291.05 / 22,124.65 / +19.80 |
| 2025-03-03 | 09:45 / −₹4,500 | 12:50 / −₹2,775 | −₹7,275 | — | — | no-trade | — | — | 22,071.90 / 22,150.40 / 22,117.25 / +45.35 |
| 2025-05-06 | 09:55 / −₹2,145 | 10:10 / −₹1,855 | −₹4,000 | — | — | no-trade | — | — | 24,331.80 / 24,399.85 / 24,387.65 / +55.85 |
| 2025-05-15 | 10:05 / −₹2,655 | 10:25 / −₹1,140 | −₹3,795 | 10:35 | 24,742.80 / 24,611.25 / 131.55 | stop 11:10 | −₹13,195 | No | 24,600.60 / 25,105.45 / 25,056.40 / +455.80 |
| 2025-08-26 | 09:35 / −₹2,860 | 10:30 / −₹1,630 | −₹4,490 | 11:05 | 24,796.75 / 24,793.30 / 3.45 | target 11:10 | +₹650 | **Yes (<5)** | 24,689.60 / 24,824.50 / 24,695.00 / +5.40 |
| 2025-09-24 | 11:00 / −₹2,800 | 14:55 / −₹2,580 | −₹5,380 | 15:05 | 25,063.40 / 25,057.95 / 5.45 | stop 15:10 | −₹585 | No | 25,050.75 / 25,066.35 / 25,059.75 / +9.00 |
| 2025-09-30 | 10:35 / −₹2,995 | 11:35 / −₹2,040 | −₹5,035 | 12:25 | 24,674.00 / 24,665.95 / 8.05 | stop 12:30 | −₹845 | No | 24,587.70 / 24,677.20 / 24,614.85 / +27.15 |
| 2025-10-30 | 09:50 / −₹4,135 | 10:15 / −₹3,820 | −₹7,955 | — | — | no-trade | — | — | 25,845.25 / 25,954.65 / 25,873.75 / +28.50 |
| 2025-11-11 | 09:45 / −₹3,125 | 10:20 / −₹2,155 | −₹5,280 | 11:55 | 25,527.95 / 25,523.60 / 4.35 | target 12:00 | +₹830 | **Yes (<5)** | 25,523.60 / 25,705.55 / 25,694.90 / +171.30 |
| 2025-12-17 | 10:20 / −₹2,455 | 11:20 / −₹1,185 | −₹3,640 | — | — | no-trade | — | — | 25,770.35 / 25,829.70 / 25,816.25 / +45.90 |
| 2026-01-19 | 10:00 / −₹2,705 | 10:30 / −₹1,910 | −₹4,615 | 11:00 | 25,556.60 / 25,540.40 / 16.20 | stop 11:10 | −₹1,660 | No | 25,508.70 / 25,628.95 / 25,591.15 / +82.45 |
| 2026-02-13 | 10:10 / −₹1,585 | 11:05 / −₹1,060 | −₹2,645 | 11:55 | 25,559.00 / 25,548.20 / 10.80 | target 12:20 | +₹2,120 | No | 25,444.30 / 25,602.45 / 25,477.20 / +32.90 |
| **2026-04-02** | 10:45 / −₹2,065 | 11:25 / −₹1,665 | −₹3,730 | 11:35 | 22,234.75 / 22,218.30 / 16.45 | target 11:55 | **+₹3,250** | No | 22,218.30 / 22,760.40 / 22,760.40 / +542.10 |
| 2026-08-31 | 10:30 / −₹2,050 | 14:00 / −₹1,465 | −₹3,515 | 14:45 | 24,077.25 / 24,055.40 / 21.85 | stop 15:00 | −₹2,225 | No | 24,044.65 / 24,094.45 / 24,051.95 / +7.30 |

Notes on the table, so no row is misread:
- 2025-05-15 is the dominant loss: flip risk 131.55 points because the flip
  signal bar's low (24,611.25) sits far below the next bar's open (24,742.80) —
  a gap-up entry into a wide signal bar. Its stop costs ₹13,195. This is a
  genuine (non-artefact) trade under the frozen definition, and it alone is
  86% of the magnitude of the genuine flip total. It is not removed: the
  definition was frozen before results, and removing the worst trade after
  seeing it would be cherry-picking in reverse.
- 2025-09-24's flip is a 15:05 signal with a 15:10 entry bar: it stops at
  15:10 for −₹585 (entry-bar low touches the stop; square-off at the same
  price would give the same net). It is counted as traded and as a loss.
- Artefact trades: 2025-01-10 stop −₹340 (risk 3.00), 2025-08-26 target +₹650
  (risk 3.45), 2025-11-11 target +₹830 (risk 4.35). Two of the three artefact
  trades are "green" — which is exactly why they are excluded from the genuine
  green rate. All-traded flip total is −₹14,170 (genuine −₹15,310 + artefacts
  +₹1,140); quoting the all-traded total instead of the genuine total would
  still fail every leg, by less.
- No-trade days are not greens and not losses: on 6 of 17 universe days price
  never closes above the OR low after the second stop through 15:05. Their
  afternoon reversals to the 15:10 close are small (+19.80 to +64.05 points),
  except none — no no-trade day hides a large missed rally.

## 4. Pass-bar verdict

| Leg | Required | Flip result | Pass? |
|---|---|---|---|
| Flip green ≥ 60% (genuine, traded) | ≥ 60% | 2/8 = 25.0% (2026-02-13, 2026-04-02) | **No** |
| Flip total positive (genuine) | > ₹0 | −₹15,310 | **No** |
| No single flip trade > 50% of flip total | — | Largest loss −₹13,195 is 86% of the genuine total's magnitude; largest win +₹3,250 cannot rescue a negative total | **No (moot — total already negative)** |
| Every universe day reported | 17/17 | 17/17 in §3, including 6 no-trades and 3 artefacts | Yes |
| Green on all traded days (no-trade as not green) | — | 2/11 = 18.2% all-traded; 2/17 = 11.8% of universe days | No under either reading |

Year split, reported only so it is not quoted out of context: 2025 genuine
0/4 green (Feb 7, May 15, Sep 24, Sep 30 — all losses); 2026 genuine 2/4 green
(Feb 13, Apr 2 wins; Jan 19, Aug 31 losses), total +₹1,485. The 2026 subset is
still below 60% (50%), rests on 4 trades, and selecting it after seeing the
full result would be exactly the in-sample selection error this family was
designed to prevent. It is not a pass, and it is not a basis for a
2026-only flip rule.

## 5. Diagnostic context only — 2 Apr afternoon

2 Apr is the day that motivated this family, so its flip is stated in full,
without inflating it into a system claim:
- (lA) PE morning (skill rescan): signal 10:45, entry 10:50, stop 22,225.10,
  risk 20.25, stop in the entry bar, −₹2,065.
- (lA) PE re-entry: signal 11:25, entry 11:30, stop 22,222.75 (5-min exit bar
  11:30), risk 16.25, −₹1,665. PE day net −₹3,730.
- Frozen flip: signal 11:35 (first 5-min close above OR low 22,209.15 after the
  second stop bar), entry 11:40 open 22,234.75, stop = signal-bar low 22,218.30,
  risk 16.45, target = 22,234.75 + 2 x 16.45 = 22,267.65, exit target at 11:55,
  net **+₹3,250** (100 shares, ₹40 cost).
- 1-min context from (x), separate grid, not the flip grid: after the re-entry
  stop minute 11:33 (close 22,215.30), Nifty rallied to a 15:10 1-min-bar close
  of 22,746.25 (max 1-min close 22,770.00 at 15:16), a ~531-point reversal. The
  5-min cache's 15:10-bar close is 22,760.40; the two closes differ because the
  5-min bar labelled 15:10 covers 15:10–15:15 while the 1-min bar labelled 15:10
  covers 15:10–15:11. Either way the afternoon rally is real and large — and
  it is 1 day in 17. The flip captured only its first 32.90 points of target
  distance (to 22,267.65 at 11:55) and then closed; the remaining ~480 points
  of rally are not flip profit under this definition, and must not be added to
  the flip total.
- **What 2 Apr does NOT prove:** that two PE stops predict a reversal. On the
  other 16 universe days, the same trigger gives 6 no-trades, 5 genuine losses
  (plus 1 artefact loss), and only 1 other genuine win (2026-02-13, +₹2,120).
  A system that wins on the motivating day and loses on the universe is a
  story, not an edge.

## 6. Why the flip fails — mechanism, not just totals

1. **The trigger fires into chop, not into trend.** On 5 of 8 genuine flip
   trades the flip signal bar is itself a bounce bar: price closes back above
   the OR low, the flip buys the next open, and price falls back through the
   signal low within 1–4 bars (Feb 7, Sep 30, Jan 19, Aug 31) or gaps into a
   wide bar and stops for a large loss (May 15). The OR-low reclaim that
   defines the flip is, on this sample, more often a retest of a broken level
   than the start of an afternoon trend.
2. **Reversal magnitude does not pay the flip.** Afternoon reversal to the
   15:10 close exceeds 100 points on only 4 of 17 universe days (Feb 7 +130.50,
   Nov 11 +171.30, May 15 +455.80, Apr 2 +542.10). On May 15 the large reversal
   still loses because the flip entry gaps far above the signal low and the
   stop is hit at 11:10 before the rally. On Feb 7 and Nov 11 the reversals are
   modest and the flips still stop (Feb 7) or win only as an artefact (Nov 11).
3. **Frequency is too low to learn from, and too low to trade on.** 17 universe
   days in 22 months, 8 genuine flip trades — roughly one genuine flip trade
   every 11 weeks. Even a passing rate on 8 trades would need out-of-sample
   confirmation on a sample that accumulates at that rate; a failing rate on
   8 trades with a −₹15,310 total needs no further confirmation to discard.

## 7. Verdict and next honest step

- **Direction-flip as a separate system: FAILS and is discarded.** It is not
  adopted, it is not carried into November paper, and its thresholds must not
  be re-tuned on this universe to hunt a pass (a second-close flip trigger, a
  wider/narrower stop, or a 1-min flip entry would each be a new definition
  requiring its own frozen validation — and the 1-min grid already shrank
  winner payoffs in (x), so a 1-min flip entry has no prior reason to help).
- **PE system status unchanged:** previous best kept remains (lA) (−₹2,720,
  5/8) with winners intact, and (lA) itself is not adopted. Flip P&L has not
  been added to, or subtracted from, any PE total in this report.
- **Next honest step, as foreshadowed in (u): Cluster 2/3 forward logging
  only.** Cluster 2 was recorded in (u) as unfixable on the available reclaim
  sample; Cluster 3's best scoped result remains survival N=10 (3/3,
  +₹4,589.25, combined below baseline, no validated live discriminator). The
  only work that can add evidence for either cluster now is forward paper
  logging (date, signal, level, frozen entry/stop/risk/target, exit, net, and
  what the original trade would have done — paper only, no re-fitting on the
  paper month). No further family should be spent on direction-flip entry/exit
  rules on this universe, and no further 5-min PE parameter family is proposed
  in this report: those families were exhausted in (u)–(w) and (x).

## Files

- Engine: `y_direction_flip_sweep.py`
- Raw replay: `y_direction_flip_sweep_raw.json` (451 scanned days; 17 universe days with full PE + flip + reversal context)
- This report: `nifty_cluster1_y_direction_flip_sweep.md`

Paper only throughout; no orders placed, nothing fabricated. The long-horizon
task continues in the parent conversation only in the sense of forward logging
for Clusters 2/3 — family (y) itself is complete and failed, and no variant
from it is adopted.
