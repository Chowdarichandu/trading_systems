# RECURSIVE ENGINE — FROZEN FAMILY DEFINITIONS

Definitions are frozen BEFORE scoring. One structural change per family.
All scoring: full-book rebuild Jan–Oct 2026 from the audited component dumps
(stocks_M1.py loaders), timing audit asserted, paper only, real ₹0,
provisional per 100 shares, ₹40/trade, home 25, equity cash LONG/SHORT.

Working book (iteration 0): INV-LONG + N4-V3 + P2F 2.5%, 344 trades,
+₹47,665.24. Only red month: February (57 trades, −₹5,533.46).
Diagnosis (Line M1): Feb 1–2 — Budget Sunday session (Feb 1, Nifty −2.16%)
+ Feb 2 whipsaw; INV-LONG 12 trades, 0 wins, −₹9,770.34; rest of Feb −₹181.57.

## Cycle 1 families (frozen 2026-10-31, before scoring)

- **RF-1 — SPECIAL-SESSION STAND-ASIDE.** No trades from any component on
  non-standard sessions: any date present in the trading calendar
  (NIFTY spot_daily dates) that falls on a Saturday or Sunday. Identified
  from the calendar itself, applies to any month. Generalised form of the
  Budget-day fix M1 barred as a single-date filter.
- **RF-2 — POST-SHOCK STAND-ASIDE.** No entries on any trading day whose
  PRIOR trading day's Nifty close-to-close move was ≥ 2% in absolute value
  (prior day = previous date in the NIFTY calendar; closes from
  data/progressive/NIFTY/spot_daily.csv).
- **RF-3 — RF-1 + RF-2** (union of excluded dates).

## Acceptance (per family, all four legs required)
1. February net > 0.
2. No month that is green in the base book flips to ≤ 0.
3. February trades ≥ 60% of base February trades (57) — i.e. ≥ 34.2, so ≥ 35 trades.
4. Timing audit clean (component audits as in stocks_M1.py anchor mode,
   re-asserted in the cycle run).

On accept: the family becomes part of the working book (iteration 1) and the
state month table/total are replaced. On reject: family + reason recorded in
stocks_engine_state.json tried_families; if all three reject,
consecutive_no_fix becomes 1.

## October Cycle 1 (OC) — frozen 2026-10-31, BEFORE computing (fast cycle: sums of audited dumps, no engine rebuild)

Target: OCTOBER (goal >= +₹50,000). Working book (state, iteration 1):
combined real book + banked RF-1 — 329 trades, +₹52,099.08,
October +₹6,845.39, month table as in stocks_engine_state.json.

- **OC-1 — ADD-COMPONENT: M2 F4 state-gated cell as 4th independent
  component.** Source dump: stocks_M2_F4_trades.csv (anchors to verify
  before summing: Jan–Oct +₹42,418.91; October +₹36,166.23; 717 trades).
  RF-1 applies book-wide: drop any F4 trades dated 2026-02-01 (Sunday
  special session) and restate F4's months before union.
- **OC-2 — ADD-COMPONENT: home 11:00 fade as 4th independent component.**
  Source: stocks_O1_P2_1100_1_fade_fixed_T125S065_all_trades.csv filtered
  to HOME25 (stocks_M1.py list) — the exact slice Line M1 reproduced
  (anchors: Jan–Oct +₹4,243.18; October +₹341.29; September +₹12,077.25).

## Acceptance — October phase banking rule (per amended protocol)
Bank a union if ALL hold: (1) October improves by >= +₹15,000 over
+₹6,845.39; (2) union total >= +₹52,099.08 (total does not fall);
(3) no month in the union table < −₹12,000. If both pass, bank the one
with the higher October and record the other as rejected-with-reason
(revisitable). If one passes, bank it. On bank: state working_book,
month_table, total, trades, iteration updated; October remains the
target until it reaches +₹50,000 (secured at goal) — recursion
continues on the residual gap.

---

## OCTOBER CYCLE 2 (frozen 2026-10-31, BEFORE union scoring)

**Diagnosis (from audited dumps; union anchor reproduced exactly —
1,043 trades, +₹97,574.23, October +₹43,011.62):** October by
component: F4 +₹36,166.23 (117 tr), INV-LONG +₹7,691.08, N4-V3
−₹530.69, P2F −₹315.00. Only 3 negative October days (sum −₹2,808.26).
F4's October losers (51 tr, −₹23,638.67) are diffuse across qualifier
bands and directions (both bands, both dirs net-positive in October),
with ONE structural exception: **setup3_bounce_rejection is the only
F4 setup negative in October (5 tr, −₹2,570.36, 0 winners) AND the
only F4 setup negative across the full Jan–Oct period (57 tr,
−₹9,653.53)**. The gap (₹6,988.38) is not closable from October's
negative days alone; an unused stream (DBL-LONG) was evaluated and
rejected at diagnosis (see log: February-deepening leg + overlap).

**THE FIX (one structural change):** the F4 component no longer takes
**setup3_bounce_rejection** signals. Setup type is known at signal
time (ex-ante); the exclusion applies to ALL months Jan–Oct; all other
components and rules (RF-1 book-wide, F4 state gate, T125/S065 exits)
are unchanged.

**Acceptance (October-phase banking legs, from the cycle brief):**
bank if (1) October rises vs +₹43,011.62; (2) union total does not
fall vs +₹97,574.23; (3) no month < −₹12,000; (4) no previously-
positive month loses more than ₹5,000 vs the current state table;
(5) the already-red months (Feb −₹2,759.77, Apr −₹7,708.27,
Jun −₹2,096.96) are not deepened by more than ₹2,000. If October
reaches ≥ +₹50,000, October is SECURED and the target moves to
September; otherwise the recursion continues on the residual gap.

---

## OCTOBER CYCLE 3 (frozen 2026-10-31, BEFORE scoring the fix)

**Diagnosis (Step 1, stocks_engine_oc3_diag.py; current-book anchor
reproduced EXACTLY first: 986 trades, +₹107,227.76, October
+₹45,581.98, month table == state).** October by component:
F4-minus-setup3 +₹38,736.59 (112 tr — verified), INV-LONG +₹7,691.08
(21 tr), N4-V3 −₹530.69 (6 tr), P2F −₹315.00 (2 tr). Gap to goal:
₹4,418.02.

- **N4-V3 / P2F October drags are accidents, not patterns.** N4: 6
  trades, 2 target wins vs 4 stops; full-period N4 is +₹6,150.35.
  P2F: 2 trades, both stopped (−₹132.00, −₹183.00); full-period P2F
  is +₹14,957.98 and October simply had 2 qualifying reactions.
  Dropping/gating either component for October's sake is barred
  (candidate iii test fails: neither drag is structural full-period).
- **INV-LONG October losers (11 tr, −₹4,633.92, all stop exits) are
  diffuse** — 7 stocks, 6 dates, both entry buckets. The only
  concentrated slice, skill_or_breakout (9 of 11 losers), is
  +₹7,626.59 in October and +₹33,119.20 full-period; setup4_reclaim
  is −₹2,465.33 full-period but only −₹396.95 of October losers on
  3 October trades. No ex-ante INV-LONG gate is supported
  (candidate ii fails its own diagnosis).
- **F4-minus-setup3 October losers (47 tr, −₹20,713.31):** 36 stop
  exits = −₹19,795.31 (95% of the loss); 11 losing square-offs =
  −₹918.00. No gate structure: both premove sub-bands net-positive
  ([0.5,0.75) +₹18,232.23; [0.75,1.0) +₹20,504.36), both directions
  net-positive (LONG +₹17,421.05; SHORT +₹21,315.54), round-2 leg
  net-positive in October (+₹886.56) and ≈0 full-period (+₹51.44),
  entries ≥12:00 are 1 October trade (−₹37.00) and NET-POSITIVE
  full-period (9 tr, +₹2,628.27) — the entry-time-cutoff seed is
  dead. Exit-progress: stop exits all terminate at −0.52 of target
  distance (the −0.65% stop, by construction); square-offs close at
  median 0.32 of the way to target (only 4/31 October square-offs in
  [0.6,1.0)). **F4's economics are target-driven: 45 October target
  exits = +₹48,587.90; 200 full-period target exits = +₹219,475.66
  against 316 stops = −₹200,990.98.** The one untested structural
  lever on the winning side is the target size itself.

**THE FIX (one structural change; pre-approved candidate i):**
**OC-3-F4T150 — the F4 component's exit target changes from +1.25%
to +1.50%; the stop stays −0.65%.** Everything else identical:
state gate (band [0.5%,1.0%) AND Nifty prior close ≤ 50DMA), 10:00
measurement, first V5 signal at/after 10:00 in the move direction,
max 2 rounds/stock-day, setup3_bounce_rejection post-filtered
exactly as in the banked book's construction, RF-1 book-wide.
Scored by full engine rebuild (stocks_M2_fix.py machinery) at
T150/S065; the T125/S065 rebuild must first reproduce
stocks_M2_F4_trades.csv exactly (anchor). The other three
components are unchanged (audited dumps, RF-1 filtered).

**Acceptance (October-phase banking legs, from the cycle brief):**
bank if (1) October rises vs +₹45,581.98; (2) union total does not
fall vs +₹107,227.76; (3) no month < −₹12,000; (4) no positive month
loses more than ₹5,000 vs the state table; (5) red repair targets
(Feb −₹1,813.21, Apr −₹7,042.44, Jun −₹2,270.04) deepen by no more
than ₹2,000 each. If October ≥ +₹50,000, October is SECURED and
the target moves to September. (No placebo: the fix is an exit
parameter, not a gate.)

---

## OC CYCLE 4 — FROZEN BEFORE SCORING (2026-10-31)

**Diagnosis (OC-4 Step 1, from stocks_engine_oc4_diag.py; anchor:
F4@T150 rebuild == stocks_engine_oc3_f4t150_trades.csv exactly,
audit 696 tr / 0 violations; banked F4 = 637 tr, +₹60,002.45,
October 109 tr / +₹41,292.83).**

Excursion profile of F4@T150/S065 (MFE measured on the bars held;
post-exit first passage uses the SAME day's later bars and is a
diagnostic only, not a score):
- Full period: 151 target exits (+₹201,851.50), 314 stop exits
  (−₹194,058.05), 172 square-offs (+₹52,209.00). Non-target exits
  with MFE ≥ +1.50%: **zero** — no gap-throughs; every trade that
  travelled to target exited there.
- Exit bars of 17 trades travelled to ≥ +1.75% (4 to ≥ +2.00%)
  inside the bar that exited at +1.50%.
- TARGET side (T150→T175): post-exit, 109 of 151 target exits
  reach +1.75% before −0.65%, only 10 reverse to the stop, 32 do
  neither. Passage counts flatter the wider target; the rupee
  estimate does not — the 10 reversals cost −2.15% each against
  +0.25% gains, and the 32 neithers give back most of the banked
  +1.50% by the close. Rough estimates: **full period −₹15,744.13
  (negative); October +₹1,188.18 — below the ₹1,861.78 residual
  gap anyway.** The marginal T150→T175 step is NOT supported.
- STOP side (−0.65%→−0.80%): the "stops leak future targets"
  story is FALSE — only 7 of 314 stop-outs later reach +1.50%
  before −0.80%; 249 fall through to −0.80% (stopped trades are
  genuinely dead). The recoverable value is elsewhere: 58
  stop-outs (18%) trigger NEITHER level after the stop bar and
  close the day back near flat — the −0.65% stop fires on
  intraday dips that mean-revert by the close. Rough estimates
  (caveat: same-bar deepening past −0.80% inside the stop bar is
  invisible to this diagnostic; only the rebuild resolves it):
  **full period +₹30,428.54; October +₹2,409.51 — the only
  candidate positive in BOTH windows, and October's estimate
  exceeds the ₹1,861.78 gap.** October alone: target passage
  28:1 (est +₹1,188.18); stop passage 1 to-target / 28 deeper /
  7 neither (est +₹2,409.51).

**THE FIX (one structural change): OC-4-F4S080 — the F4
component's stop changes from −0.65% to −0.80%; the target stays
+1.50%.** Everything else identical: state gate (band [0.5%,1.0%)
AND Nifty prior close ≤ 50DMA), 10:00 measurement, first V5
signal at/after 10:00 in the move direction, max 2
rounds/stock-day, setup3_bounce_rejection post-filtered exactly
as in the banked book's construction, RF-1 book-wide. Scored by
full engine rebuild (stocks_M2_fix.py machinery) at T150/S080;
the T150/S065 rebuild must first reproduce
stocks_engine_oc3_f4t150_trades.csv exactly AND the filtered
T150/S065 union must equal the state month table (+₹112,101.53 /
Oct +₹48,138.22) before the fix is judged. The other three
components are unchanged (audited dumps, RF-1 filtered).

**Acceptance (October-phase banking legs, from the cycle
brief):** bank if (1) October rises vs +₹48,138.22; (2) union
total does not fall vs +₹112,101.53; (3) no month < −₹12,000;
(4) no positive month loses more than ₹5,000 vs the state table;
(5) red months (Feb −₹1,660.11, Apr −₹3,324.69, Jun −₹473.22)
deepen by no more than ₹2,000 each; (6) timing audit clean on
the new build. If October ≥ +₹50,000, October is SECURED and
the target moves to September. (No placebo: the fix is an exit
parameter, not a gate.)

---

## SE CYCLE 1 — September turn (frozen 2026-10-31, BEFORE scoring)

**Diagnosis (from stocks_engine_se1_diag.py; anchor: rebuilt union
== state exactly — 934 tr, +₹131,646.79, Sep 80 tr / +₹17,413.79,
Oct +₹50,029.72).** September by component: F4 +₹13,593.59 (71 tr),
INV-LONG +₹3,820.20 (9 tr); N4-V3 and P2F took no September trades.
9 negative days sum −₹7,376.85, all F4-driven except Sep 24
(INV −₹968.80). Structural-drag test (slice negative in September
AND negative full-period): NHPC stock (Sep −₹465.28 / 5 tr; full
−₹1,171.48 / 31 tr — thin, single-stock, not chosen) and **the F4
round2 leg (Sep −₹2,471.53 / 6 tr; full −₹852.58 / 74 tr)** — the
only mechanism-level slice failing both windows. (Exit-reason
"stop" is the loss mechanism, not a rule input — excluded.)

**THE FIX (one structural change): SE-1-F4R1 — the F4 component
takes only the FIRST qualifying signal per stock-day (max 1
round); round-2 second entries are not taken.** Everything else
identical: state gate (band [0.5%,1.0%) AND Nifty prior close
≤ 50DMA), 10:00 measurement, T150/S080 exits,
setup3_bounce_rejection excluded, RF-1 book-wide, other three
components unchanged. Ex-ante: the round-1 trade is built first
and identically whether or not a round-2 exists, so dropping
leg == "round2" from the audited S080 dump
(stocks_engine_oc4_f4s080_trades.csv) is exactly the gated book;
scored as the full Jan–Oct union from the component dumps.

**Acceptance (September-phase legs, from the cycle brief):**
bank ONLY if (1) September rises vs +₹17,413.79; (2) **October
stays ≥ +₹50,000 — HARD FLOOR, any breach rejects outright**;
(3) union total does not fall vs +₹131,646.79; (4) no positive
month loses more than ₹5,000 vs the state table; (5) June
(−₹1,233.49) and August (−₹1,484.26) deepen by no more than
₹2,000 each. If the fix is rejected, September is secured as-is
(+₹17,413.79) and the target moves to August either way.

---

## AU CYCLE 1 — August turn (frozen 2026-10-31, BEFORE scoring)

**Diagnosis (stocks_engine_au1_diag.py / au1_diag2.py; anchor: rebuilt
union == state exactly — 934 tr, +₹131,646.79, Aug −₹1,484.26).**
August = N4-V3 +₹5,698.96 and P2F +₹408.12 carrying an F4 month of
−₹7,286.99 (18 tr). OC-4's wider stop is only the top layer: matched
S065→S080, 11 August stop-outs were already dead at −0.65% and simply
lost ₹1,866.36 more at −0.80% (zero August rescues); at S065 F4's
August was still −₹5,420.63. No mechanism-level F4 slice is negative
in both August and full-period (breakdown, direct leg, lower band all
deeply positive full-period) — reverting or conditioning the stop
fails the total/October legs by construction. The one slice that IS
rotten in August AND full-period, in TWO independent systems, is
**ASTRAL in the event-follow components**: N4-V3 ASTRAL 2 trades,
full −₹1,611.45 (Aug −₹833.95); P2F ASTRAL 2 trades, full −₹1,592.10
(Aug −₹836.00) — 4 of 4 trades losers across both systems, and the
frozen reaction profiles (stock_reaction_profiles.md) independently
classify ASTRAL as fade-type (its big reactions faded 3/3), i.e.
following its reactions is mechanistically wrong. ASTRAL is NOT a
bad stock for the book — INV-LONG +₹5,350.84 and F4 +₹20,462.15 on
it — the poison is stock × mechanism specific. Thin-sample caveat
recorded: 4 trades is the smallest surgical exclusion the engine has
made; it stands or falls on fresh data like everything else.

**THE FIX (one structural change): AU-1-EVENT-ASTRAL — the two
event-follow components (N4-V3 and P2F 2.5%) no longer trade
ASTRAL.** INV-LONG and F4 keep trading ASTRAL unchanged. Everything
else identical (RF-1 book-wide; F4 = state gate, T150/S080,
setup3 excluded). Ex-ante: symbol and component are known at entry.
Scored as the full Jan–Oct union from the audited component dumps
(anchor must reproduce the state table first).

**Acceptance (August-phase legs, from the cycle brief):** bank if
(1) August rises vs −₹1,484.26; (2) October ≥ +₹50,000 (hard floor);
(3) September stays positive (secured); (4) union total does not
fall vs +₹131,646.79; (5) no positive month loses more than ₹5,000
vs the state table; (6) June (−₹1,233.49) deepens by no more than
₹2,000. If August turns positive, August is SECURED and the target
moves to July.

---

## JU-1 (frozen 2026-10-31, BEFORE scoring)

**Diagnosis (July verification turn).** Anchor verified: rebuild ==
state (930 trades, +₹134,850.34; July +₹2,096.63 / 14 trades). July
is thin and concentrated: top-1 trade (P2F TVSMOTOR +₹4,844.50) =
231% of the month; ex-top-3 = −₹6,041.00; winners 4/14; two target
exits (+₹7,397.63) carry nine stops (−₹5,531.00). INV-LONG inactive
in July. Slice scan (negative in July AND full-period) found four
comp×stock slices; three have NO supporting evidence and are
rejected at diagnosis — WIPRO and HDFCBANK are continuation-profile
stocks (frozen profiles: 3/4 and 3/4 CONTINUED) with cost-level
per-trade noise, and F4×NHPC is −₹43/trade over 28 trades (noise,
wrong mechanism). The fourth matches the Lesson 11 pattern with an
independent evidence stack:

- **P2F × HINDUNILVR:** July 1 trade −₹1,100.00; full-period 2
  trades, both losers, −₹2,294.05. The frozen reaction profiles
  (stock_reaction_profiles.md) name HINDUNILVR in the fade-tendency
  group (0 CONTINUED / 2 FADED / 1 FLAT, weakest pre-window on the
  board) and the earlier P2 study recorded it as the worst ungated
  P2 payer (−₹3,484.80) — following its reactions is mechanistically
  wrong in the follow-through mechanism specifically. N4-V3's
  HINDUNILVR trades are NOT poison (its July trade was the month's
  +₹2,553.13 target win) — poison is stock × mechanism, so the
  exclusion is scoped to P2F only (Lesson 11). Thin-sample caveat:
  2 in-band trades; the profile + ungated-band evidence carries the
  case, and it stands or falls on fresh data.

**THE FIX (one structural change): JU-1-P2F-HINDUNILVR — the P2F
2.5% component no longer trades HINDUNILVR.** N4-V3, INV-LONG and
F4 keep trading it unchanged. Everything else identical (RF-1
book-wide; event components already exclude ASTRAL per AU-1; F4 =
state gate, T150/S080, setup3 excluded). Ex-ante: symbol and
component are known at entry. Scored as the full Jan–Oct union from
the audited component dumps (anchor must reproduce the state table
first).

**Acceptance (July-phase legs, from the cycle brief):** bank if
(1) July rises vs +₹2,096.63; (2) October ≥ +₹50,000 (hard floor);
(3) September and August stay positive (secured); (4) union total
does not fall vs +₹134,850.34; (5) no positive month loses more
than ₹5,000 vs the state table; (6) June (−₹1,233.49) deepens by no
more than ₹2,000. On completion July is SECURED and the target
moves to June.

## JN-1 (frozen 2026-10-31, BEFORE scoring)

**Target: June −₹1,233.49 — the ONLY red month.** Secured: October
+₹50,029.72 (HARD FLOOR ₹50,000; headroom only ₹29.72), September
+₹17,413.79, August +₹185.69, July +₹3,196.63. Book +₹137,144.39 /
928 trades. Anchor verified in the JN-1 diagnosis (rebuild from
audited dumps == state table to the paisa).

**Diagnosis (stocks_engine_jn1_diag.py):** June = 75 trades. F4
−₹2,538.69, INV-LONG −₹1,772.32, N4-V3 −₹1,131.10 (1 trade), P2F
+₹4,208.62 (2 trades). Loss concentrated on Jun 24 (−₹5,154.72) and
Jun 10 (−₹2,728.71); stops dominate (−₹23,537.79 across 37 exits vs
18 targets +₹20,073.30). Slice scan (negative in June AND
full-period) found several candidates; two were eliminated before
freezing:
- **F4 × GODREJCP** (Jun −₹2,460.96 / 3 tr; full −₹3,814.67 / 16 tr)
  — the largest June drag, but its October slice is +₹1,060.25:
  removing it cuts October to ₹48,969.47 and breaks the hard floor.
  NOT bankable while the floor binds.
- **F4 round2 legs** (Jun −₹1,393.79; full −₹852.58) — that is the
  already-rejected SE-1-F4R1 family. Not re-proposed.

**The chosen slice: INV-LONG × BDL** — June −₹1,406.25 (2 trades,
both stops), full-period −₹1,486.93 over 22 trades with only 6
winners (27%). Negative in the target month AND negative across the
full period — the Lesson 5 surgical pattern. Lesson 11 scoping:
BDL is a strong earner in the OTHER components (+₹10,168.59 across
N4-V3/P2F/F4 — it is a core event name); the poison is in the
INV-LONG pool mechanism specifically, so the exclusion is scoped
to INV-LONG only. Side benefits visible in the slice table: its
April slice is −₹1,413.63 (removal directly relieves the
razor-thin April, +₹50.73) and its October slice is −₹542.30
(removal ADDS October headroom). Thin-sample caveat: June's gain
rests on 2 June trades; the 22-trade full-period record (27% win
rate) carries the case, and it stands or falls on fresh data.

**THE FIX (one structural change): JN-1-INV-BDL — the INV-LONG
component no longer trades BDL.** N4-V3, P2F and F4 keep trading
BDL unchanged. Everything else identical (RF-1 book-wide; event
components exclude ASTRAL per AU-1; P2F excludes HINDUNILVR per
JU-1; F4 = state gate, T150/S080, setup3 excluded). Ex-ante:
symbol and component are known at entry. Scored as the full
Jan–Oct union from the audited component dumps (anchor must
reproduce the state table first).

**Acceptance (June-phase legs, from the cycle brief):** bank if
(1) June rises vs −₹1,233.49; (2) October ≥ +₹50,000 (hard floor);
(3) September, August and July stay positive (secured);
(4) union total does not fall vs +₹137,144.39; (5) no positive
month loses more than ₹5,000 vs the state table. If June turns
positive, all ten months are green and current_target moves to
TOTAL-RAISING challenger cycles.

---

## CH-1 — CHALLENGER: P2F-PROFILE (frozen 2026-10-31, BEFORE scoring)

**Charter basis:** self-improvement challenger cycle (Lessons 3 + 11).
Lesson 11 proved poison is stock × mechanism: ASTRAL's reactions fade
3/3 (frozen profiles) yet P2F follows them and loses; HINDUNILVR the
same. The incumbent patches this with name exclusions. The challenger
replaces the patch with a RULE: let each stock's own reaction history
choose the direction.

**P2F-PROFILE (standalone system, home 25, Jan–Oct 2026):**
- Event set: the audited P2F candidate construction verbatim
  (stocks_T2.py build_candidates, HOME universe): results-calendar
  reaction days R (reaction_date within 7 days of announce, else the
  event date), R and R+1 trade date within 2026-01-01..2026-10-28,
  |reaction_ret| >= 2.0% (reaction_ret = close-to-close % on R).
  Construction anchor: follow-direction at T125/S050 must reproduce
  the T2 anchor exactly (48 trades, +Rs12,835.88) before any
  challenger number is believed.
- Direction rule (causal): for a trade on stock S with reaction day R
  and entry at R+1 09:15 open — look at S's PRIOR reaction events in
  the same >=2.0% event set with R_prior < R whose outcome is known
  before entry (outcome day = next trading day after R_prior; require
  outcome date < trade date). Outcome of a prior reaction: CONTINUED
  if the R_prior+1 close-to-close % has the same sign as the reaction
  ret, FADED if opposite sign; a zero R+1 move is unclassified and
  excluded from the counts. If >=2 classified prior reactions and
  CONTINUED share >= 2/3 -> trade WITH the reaction (follow); if
  FADED share >= 2/3 -> trade AGAINST it (fade); otherwise follow.
- Entry R+1 first 5-min bar open (09:15); exit T125/S065
  (target +1.25%, stop -0.65%), square-off 15:10 (T2 replay engine).
- NO stock-name exclusions inside P2F-PROFILE (the profile rule is
  the replacement for the AU-1/JU-1 patches). RF-1 applies: trades
  whose TRADE DATE is a Sat/Sun are dropped (history is information
  and is NOT filtered).
- Placebo: identical candidates/entries/exits, but the direction
  decision uses a DONOR stock's prior-reaction history — donor map =
  one random permutation of the 25 symbols, seed 20261031 (stated
  here, before scoring). Same >=2 / >=2/3 rule on the donor's causal
  history as of the same dates; default follow when donor history is
  thin. The real assignment must beat the placebo standalone.

**Assembly (the challenger book):** incumbent components verbatim
(INV-LONG minus BDL; N4-V3 minus ASTRAL; F4 minus setup3 @ T150/S080;
RF-1 book-wide) with the P2F-2.5% component REPLACED by P2F-PROFILE
as defined above (which therefore also drops the P2F-specific
ASTRAL/HINDUNILVR name exclusions — they are subsumed by the rule).
Anchor: the incumbent rebuild must reproduce the state exactly
(+Rs138,631.32, 906 trades, state month table) before the swap.

**Frozen gate (challenger replaces incumbent ONLY if ALL hold):**
(a) assembled book: all ten months > 0; (b) assembled total >
+Rs138,631.32; (c) October >= +Rs50,000; (d) assembled ex-top-3
(per-stock across the whole book, top-3 positive stocks removed)
is BETTER than the incumbent's ex-top-3; (e) timing audit clean
(every challenger trade: entry date = R+1 trading day, entry 09:15,
direction == profile rule recomputed independently, every profile
input strictly prior with outcome date < trade date) AND
P2F-PROFILE standalone beats its placebo.
If the gate fails: incumbent unchanged, rejection + lesson recorded;
the rejected challenger counts as a no-bank cycle.

---

## CH-2 — challenger: N4-V3 exit rebuild T125/S050 -> T150/S080 (frozen 2026-10-31, before scoring)

**Diagnosis (stocks_engine_ch2_diag.py, run before this freeze):**
- (B) N4-V3 excursions on the incumbent N4 set (50 trades, +Rs7,761.80):
  exit split stop 31 / -15,985.68, target 17 / +22,612.48, square-off 2 /
  +1,135.00; MFE>=1.50 only 6 of 50. Post-exit first passage (OC-4
  method): target exits reach +1.50 before -0.80 in 15 of 17 cases but
  the 2 reversals cost -2.30% each -> rough T150 swing -Rs1,995.57;
  stop exits reach +1.25 later in 7 of 31, fall to -0.80 in 22 ->
  rough S080 swing +Rs11,472.97; combined rough swing +Rs9,477.40.
- (A) F4-MIRROR population: 69 above50 days, October above50 = 0
  (October structurally untouched, as predicted); 350 qualifying
  capped-band stock-days; fade-drift 10:00->close mean +0.059%,
  positive 176/350 (coin flip), rough total +Rs40,671 carried by
  three months (Jul +21,003, Jun +11,313, Aug +9,340) with May
  negative — a regime-concentrated close-hold drift statistic, not
  a signal-entry score; the Lesson 2 / Lesson 8 mirage profile.
- CHOICE: (B). Direct excursion evidence on the incumbent's own
  trades (the method behind banked OC-3/OC-4), Lesson 3 information
  family + Lesson 4 exit economics. (A) is not scored this cycle.

**Challenger definition (verbatim):** the incumbent book with ONLY
the N4-V3 component's exits changed: target +1.25% -> +1.50%, stop
-0.50% -> -0.80%. Entries identical (reaction day, 09:35 bar open,
same direction); ASTRAL exclusion and RF-1 weekend drop still apply
to N4; every other component, gate, exclusion and exit is verbatim
incumbent. Anchors required before the swap: (i) incumbent rebuild
== state (+Rs138,631.32, 906 trades, state month table); (ii) N4
replay at T125/S050 reproduces the source dump nets per trade.
Timing audit: every rebuilt trade has entry_time 09:35 and
(date, stock, direction, entry) identical to its anchor trade.

**Adoption gate (evaluated FOR THE RECORD):** (a) all ten months
> 0; (b) total > +Rs138,631.32; (c) October >= +Rs50,000;
(d) ex-top-3 not worse than the incumbent's.

**USER OVERRIDE (2026-10-31 12:08 IST):** the user distrusts the
in-sample fit ("results are very optimal"). This challenger is
scored FOR THE RECORD ONLY and is NOT ADOPTED even if every gate
leg passes. The incumbent is frozen verbatim as the December
candidate (stocks_engine_candidate_spec.md) and the engine state
is set terminated = "FROZEN_FOR_FRESH_DATA" at the end of this
cycle, with consecutive_no_bank unchanged.

**SUPERSESSION (2026-10-31 12:10 IST, before scoring ran):** the
user reversed the freeze order and directed the engine to run
non-stop until SATURATION (3 consecutive cycles failing to beat
the best book on the gate). The override paragraph above is
superseded: the ORIGINAL adoption gate applies — adopt iff total
higher AND all ten months green AND October >= Rs50,000 AND
ex-top-3 not worse. No FROZEN/BREAK_EVEN termination this cycle;
no candidate spec is written. The challenger definition itself
(N4-V3 exits T150/S080, everything else verbatim) is unchanged.

## SAT-1 — THICKEN JUNE (frozen 2026-10-31, BEFORE scoring)

**Diagnosis (stocks_engine_sat1_diag.py, anchor exact: 906 tr,
+Rs138,631.32, June +Rs172.76 / 73 tr):** June = F4 -2,538.69 (54),
INV-LONG -366.07 (16), N4-V3 -1,131.10 (1), P2F +4,208.62 (2);
35 stops -22,131.54 vs 18 targets +20,073.30. Slice scan (negative
in June AND full-period) headline: the known F4 x GODREJCP slice
(Jun -2,460.96, full -3,814.67) is still October-blocked (its
October slice +1,060.25 vs headroom 572.02 — Lesson 12). But its
SHORT half is the rot: **F4 x GODREJCP x SHORT = Jun -1,680.96
(2 tr), full -4,754.92 (10 tr, expectancy -475.49/tr), October
slice exactly 0.00, August 0.00, April +180.00** — while the LONG
half of the same stock x mechanism is full-period POSITIVE
(+940.25). Poison is stock x mechanism x DIRECTION (Lesson 11,
refined). Runner-up F4 x OIL (Jun -990.16, full -2,661.85) is
dominated by the chosen slice on June gain, total gain and
October neutrality.

**Fix SAT-1-F4-GODREJCP-SHORT:** the F4 component no longer takes
SHORT signals on GODREJCP. F4 keeps GODREJCP LONG signals; every
other component trades GODREJCP unchanged; all gates, exits,
exclusions and RF-1 verbatim incumbent. Ex-ante: direction is
known at signal time. The fix only DELETES trades from the
pre-audited F4 dump, so timing validity is inherited; the anchor
assertion (ungated rebuild == state) is the gate.

**Saturation gate:** bank iff (a) total > +Rs138,631.32;
(b) all ten months > 0; (c) October >= +Rs50,000. June's rise is
documented against the CH-2 revisit need (+Rs654.66): if banked
with June delta >= +654.66, June's revisit condition is covered
in full and the counter resets (no_beat_cycles -> 0,
best_total updated).

---

## SAT-2 — thicken August (frozen BEFORE scoring, 2026-10-31)

**Diagnosis (stocks_engine_sat2_diag.py + diag2 + diag3, anchor
exact: 896 tr, +Rs143,386.24, August +Rs185.69 / 32 tr, October
+Rs50,572.02, headroom Rs572.02):** August is carried by the event
systems (N4-V3 +6,532.91, P2F +1,244.12) against **F4 -7,286.99**
(18 tr: 11 stops -10,393.92, 3 targets +2,231.93, 4 square-offs
+875.00). Every F4 August trade is a skill_or setup; the stops are
breakdown SHORTs and breakout LONGs concentrated Aug 20/27/28/31.
But NO comp x setup, comp x setup x dir, or F4 x stock slice is
negative in both August and full-period with real mass: F4 x SHORT
full = +42,078.56, F4 x LONG full = +42,224.07 — August's killers
are full-period earners having a bad month (Lesson 8 shape).

**Families killed on evidence before freezing:**
- F4 stop widening (S095 / S110): excursion diagnostic
  (diag3, OC-4 method) — of August's 11 F4 stop exits, **0 reached
  the +1.50% target post-exit, 7 continued deeper, 4 went flat**;
  rough August swing S095 +Rs262.61, S110 -Rs1,191.02. August's
  stops were genuine continuations, not mean-reverting dips —
  the OC-4 rescue does not transfer. NOT frozen.
- F4 x UNITDSPR (Aug -1,947.84, full -3,042.59): October slice
  +2,617.85, and even its SHORT half carries October +780.00 >
  headroom 572.02 — floor-blocked both ways (Lesson 12/15 checked).
- F4 x GLENMARK x SHORT (Aug -4,008.24): the slice is a top
  full-period earner; removal craters the total. Gate-dead.
- A bundle of the remaining micro-slices (several on 1 trade):
  rejected as a method — one structural change per cycle, and
  1-trade slices are the overfit pattern STRESS-1 flagged.

**Fix SAT-2-F4-INDUSTOWER-LONG:** the F4 component no longer takes
LONG signals on INDUSTOWER. The slice: **Aug -693.00 (2 tr, 0
winners), full -361.12 (18 tr, 7 winners), October -792.72** —
negative in the target month AND full-period (Lesson 5 criterion),
mechanism x direction scoped (Lesson 11/15 shape), and its removal
IMPROVES secured October by +792.72 and April by +758.76. F4 keeps
INDUSTOWER SHORT; every other component trades INDUSTOWER
unchanged; all gates, exits, exclusions and RF-1 verbatim
incumbent. Ex-ante: direction and stock known at signal time. The
fix only DELETES trades from the pre-audited F4 dump, so timing
validity is inherited; the anchor assertion (ungated rebuild ==
state) is the gate.

**Saturation gate:** bank iff (a) total > +Rs143,386.24;
(b) all ten months > 0; (c) October >= +Rs50,000. August's rise is
documented against the CH-2 N4-rebuild revisit need
(+Rs3,834.85): partial coverage is reported as a shortfall, not
spun (Lesson 10 — bank partial progress that passes the gate).

## SAT Cycle 3 — RE-MEASUREMENT of SE-1-F4R1 at the current book (frozen BEFORE scoring, 2026-10-31)

**This is a re-test of an already-frozen family at a new book state,
not a new family.** SE-1-F4R1 (F4 takes only the FIRST qualifying
signal per stock-day; round-2 legs dropped, all months) was scored
at the SE-1 book (+Rs131,646.79 / 934 tr) and rejected ONLY on the
October hard floor: its recorded deltas were total +852.58,
September +2,471.53, June +1,393.79 (flips GREEN), August -429.57,
October -1,551.75 against a headroom of Rs29.72.

**Why re-measure:** SAT-1 and SAT-2 changed the F4 population
(GODREJCP SHORT and INDUSTOWER LONG trades deleted), so F4's
round-2 legs at the CURRENT book are a different set from the ones
SE-1 measured; October headroom is now Rs1,364.74. The old
measurement is stale and cannot be carried forward.

**Re-measurement definition (verbatim mechanics):** rebuild the
current book exactly as the state describes (anchor: 878 trades /
+Rs143,747.36 / October +Rs51,364.74 / state month table) from the
pre-audited dumps (INV-LONG minus BDL, N4-V3 minus ASTRAL, P2F 2.5%
minus ASTRAL and HINDUNILVR, F4 from
stocks_engine_oc4_f4s080_trades.csv minus weekend sessions, minus
setup3_bounce_rejection, minus GODREJCP SHORT, minus INDUSTOWER
LONG). The re-test book = current book with every F4 trade whose
leg == "round2" deleted. F4 round-1 trades are built identically
with or without round-2 (SE-1 convention), so the deletion IS the
gated F4 book; timing validity is inherited from the pre-audited
dump, no new trades are created.

**Saturation gate:** bank iff (a) total > +Rs143,747.36;
(b) all ten months > 0; (c) October >= +Rs50,000 after the change.
Special floor rule: if October lands within Rs250 BELOW the floor
(Rs49,750–Rs49,999.99), do NOT bank — record the exact shortfall
for a later October-positive unlock. The full month table and
each month's delta are published against BOTH the current book
and the SE-1 measurement.

## SAT-3 — thicken June / unlock SE-1-F4R1 (frozen BEFORE scoring, 2026-10-31)

**Diagnosis (stocks_engine_sat3_diag.py, anchor exact: 878 tr,
+Rs143,747.36, August +Rs878.69, October +Rs51,364.74, headroom
Rs1,364.74):** August's residual has no protocol-clean slice left
(SAT-2's verdict stands — the remaining August-negative slices are
1-3-trade micro-slices or flat: F4 x UNITDSPR x SHORT is full
-Rs147.01 over 9 tr, expectancy -Rs16/tr = cost noise, NOT rot).
The June scan (June is the second-thinnest month, +Rs1,853.72)
found the slice negative in June AND full-period AND October:
**F4 x HINDUNILVR x SHORT = Jun -Rs1,040.00 (1 tr), full
-Rs2,664.00 (9 tr, 5 winners, expectancy -Rs296.00/tr), October
-Rs1,316.80** — while F4 x HINDUNILVR LONG is full-period positive
(the whole-stock F4 slice is -Rs1,184.02 only because of the SHORT
half). Poison is stock x mechanism x DIRECTION again (Lesson 15).
Its only positive month of size is April (+Rs526.88; April
+Rs2,043.12 absorbs it and stays green). Removal also lifts
October headroom to Rs2,681.54, which UNLOCKS the SE-1-F4R1
revisit (needs >= Rs1,551.75) for a later cycle. Runner-up
F4 x OIL x SHORT (full -Rs3,078.24 / 15 tr, Jun -Rs835.16,
Oct -Rs398.60) is recorded as the SAT-4 seed — not bundled
(one structural change per cycle).

**Fix SAT-3-F4-HINDUNILVR-SHORT:** the F4 component no longer
takes SHORT signals on HINDUNILVR. F4 keeps HINDUNILVR LONG;
every other component trades HINDUNILVR unchanged (JU-1's
P2F-scoped exclusion is a different mechanism and stays as-is);
all gates, exits, exclusions and RF-1 verbatim incumbent.
Ex-ante: direction and stock known at signal time. The fix only
DELETES trades from the pre-audited F4 dump, so timing validity
is inherited; the anchor assertion (ungated rebuild == state)
is the gate.

**Saturation gate:** bank iff (a) total > +Rs143,747.36;
(b) all ten months > 0; (c) October >= +Rs50,000;
(d) ex-top-3 not worse than the incumbent's. June's and
October's deltas are documented; if banked, SE-1-F4R1's
October-headroom condition is re-checked and recorded.

## SAT-4 — NEW COMPONENT: N4-LOWBAND (frozen BEFORE scoring, 2026-10-31)

**Charter:** saturation run; August (+Rs878.69) is the frontier and
its own slices are exhausted (SAT-2) — only new August-earning flow
can thicken it toward the CH-2 N4-rebuild revisit need
(August +Rs3,141.85 more, i.e. August >= Rs4,020.54). One structural
change: ADD one component built from Lesson 3 materials (the event
axis), defined on the band N4-V3 does not trade.

**Component definition (verbatim mechanics, audited N4 machinery):**
- Event set: COMBINED results + single-news reaction days from
  stock_event_calendar_jan_oct_2026.csv, effective reaction date =
  reaction_date if event_date <= reaction_date <= event_date + 7d,
  else event_date (identical to stocks_equity_n4deep.py).
- Universe/window: home 25, trading days 2026-01-01..2026-10-28
  (the N4 machinery's window — NIFTY daily ends 2026-10-28).
- Qualifier: move by 09:30 = (close of the 09:25 bar / prior daily
  close - 1) x 100. LOWBAND trades only 0.75% <= |move| < 1.0%
  (N4-V3's frozen trigger is |move| >= 1.0% — the bands are disjoint
  by construction; zero overlap with the N4-V3 dump is verified
  mechanically on (date, stock)).
- Direction: sign of the move (LONG if positive, SHORT if negative).
- Entry: close of the 09:30 bar, entry_time labelled 09:35
  (identical to N4-V3).
- Exits: T125/S050 — target +1.25%, stop -0.50% (N4-V3's CURRENT
  exits; the CH-2 T150/S080 rebuild is NOT used here), stop checked
  before target within a bar, exit scan from the 09:35 bar itself
  (the CH-2-verified replay convention, start_offset 0), square-off
  at the 15:10 bar close.
- RF-1 applied as book-wide convention (weekend-session dates
  dropped; count reported).
- NO name exclusions are added in this cycle (the AU-1 ASTRAL
  exclusion is scoped to N4-V3/P2F as built; adding it here would be
  a second change). ASTRAL's slice inside the component is reported
  for the record.
- Basis: equity cash, paper only, real Rs0, provisional per
  100 shares, Rs40/trade.

**Construction anchor (must pass before any LOWBAND number is
believed):** the identical pipeline at |move| >= 1.0% must reproduce
eq_n4deep_v3_trades_T125_janoct.csv exactly (56 trades, per-trade net
and exit_reason). Timing audit on the LOWBAND build: entry_time ==
09:35, entry == 09:30-bar close, exit_time >= entry-bar time,
qualifier uses only prior close + bars up to the 09:25 close.

**Saturation gate:** bank the component iff (a) union total >
+Rs143,747.36; (b) all ten months > 0; (c) October >= +Rs50,000.
August's union value and the remaining N4-revisit shortfall
(Rs4,020.54 - union August) are reported either way. If banked:
no_beat_cycles resets to 0 and best_total updates; if not:
no_beat_cycles increments (currently 1; run ends at 3).

## WATCHDOG CORRECTION NOTE (2026-10-31, appended after SAT-4 freeze)
The section above headed "SAT-3 — thicken June / unlock SE-1-F4R1"
(F4-HINDUNILVR-SHORT) was frozen by the 12:17 IST watchdog run,
which read a null cycle_lock at 12:18 in a race window: the Stocks
chat chain concurrently ran its own SAT-3 (the F4R1 re-measurement,
NOT banked) and then froze SAT-4 (N4-LOWBAND) with a fresh lock at
12:20 IST. The HINDUNILVR-SHORT fix was NEVER SCORED by the
watchdog and is NOT part of the book. It is renumbered as a
PENDING SAT-5 candidate, to be re-diagnosed and re-frozen only
after SAT-4 completes and the state is re-read (Lesson 16:
recorded deltas expire). Watchdog diagnosis (anchor exact vs the
pre-SAT-3 state): stocks_engine_wd5_diag.py / _wd5_diag.json —
slice F4 x HINDUNILVR x SHORT: full -Rs2,664.00 (9 tr), June
-Rs1,040.00, October -Rs1,316.80, April +Rs526.88.

## SAT-5 — F4 excludes HINDUNILVR SHORT (frozen 2026-10-31, BEFORE scoring)
- **Family:** mechanism-scoped direction exclusion (Lessons 11/15 pattern):
  the F4 component no longer takes SHORT signals on HINDUNILVR. F4 keeps
  HINDUNILVR LONG (its October slice is +Rs5,369.90 by subtraction: name
  total Oct +4,053.10 minus SHORT Oct -1,316.80). All other components
  unchanged (P2F already excludes HINDUNILVR entirely per JU-1; N4-V3
  and INV-LONG trade it unchanged).
- **Provenance:** this is the watchdog's pending candidate (its pre-SAT-3
  freeze, renumbered per the WATCHDOG CORRECTION NOTE above), NEVER
  scored. Re-diagnosed at the post-SAT-4 book in
  stocks_engine_sat5_diag.py (anchor exact: 878 tr / +Rs143,747.36 /
  October +51,364.74): the slice re-measures IDENTICALLY to the
  watchdog's record — 9 tr, net -Rs2,664.00, 5 winners; months
  Jan -1,904.08, Apr +526.88, Jun -1,040.00, Sep +1,070.00,
  Oct -1,316.80; no trades in Feb/Mar/May/Jul/Aug.
- **Diagnosis of the rival directions (same diag run):** (2) INV-LONG
  exit rebuild — DEAD: all 17 alternate exit dumps (T100..T200 x
  S050..S080 + TRA/TRB) score BELOW the incumbent T125/S050 at
  component level (-Rs2,466.26 to -Rs18,094.15); T125/S050 is the
  grid peak. (3) P2F exit rebuild — not built: Lesson 4 (removing
  P2F's small target destroyed its edge) and CH-1 (S065 hurt P2F)
  stand against it; P2F expectancy at current exits is +Rs571.03/tr,
  the book's highest — the "overwhelming" condition is not met.
- **Scoring:** rebuild the incumbent from the audited dumps (anchor
  must match the state to the paisa), delete exactly the frozen
  slice's 9 trades, recompute the month table. Timing validity is
  inherited (deletion-only from the pre-audited F4 dump — JN-1
  precedent); the score run asserts the deleted set == the frozen
  slice on (date, stock, dir).
- **Saturation gate:** bank iff (a) union total > +Rs143,747.36;
  (b) all ten months > 0; (c) October >= +Rs50,000. If banked:
  no_beat_cycles resets to 0 and best_total updates. If rejected:
  no_beat_cycles 2 -> 3 and the run is SATURATED (close per protocol:
  candidate spec + final saturation summary).
- Basis: equity cash, paper only, real Rs0, provisional per
  100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-6 — RE-MEASUREMENT + BANKING TEST of SE-1-F4R1 at the post-SAT-5 book (frozen 2026-10-31, BEFORE scoring)
- **Family:** SE-1-F4R1 re-measured (third scoring of this frozen family:
  SE-1 rejected on the October floor; SAT-3 re-measurement NOT banked,
  October Rs187.01 short). The F4 component takes only the FIRST
  qualifying signal per stock-day — all F4 leg == "round2" trades are
  dropped from the CURRENT book. No other component changes.
- **Why now (Lesson 16 discipline):** October headroom is Rs2,681.54,
  which exceeds F4R1's twice-measured invariant October cost
  (Rs1,551.75, the 8 October round2 legs). BUT SAT-5 (F4 x HINDUNILVR x
  SHORT removal, 9 trades) intervened on the same component — its slice
  may contain round2 legs, so EVERY leg of the old measurement is void
  until re-derived at the current book. The score run must report: the
  leg composition of the SAT-5 frozen slice (direct vs round2), the
  round2 set at the current book (trades, net, month nets, the October
  legs listed), and the deltas vs the SAT-3 measurement.
- **Scoring:** rebuild the incumbent from the audited dumps with ALL
  current filters (anchor must match the state to the paisa:
  869 tr / +Rs146,411.36 / October +Rs52,681.54), delete exactly the
  current F4 round2 set, recompute the month table. Timing validity is
  inherited (deletion-only from the pre-audited F4 dump — SAT-3
  precedent).
- **Saturation gate:** bank iff (a) union total > +Rs146,411.36;
  (b) all ten months > 0; (c) October >= +Rs50,000 after the drop.
  If banked: F4R1 becomes part of the book, no_beat_cycles resets
  to 0, best_total updates. If any leg fails: do NOT bank,
  no_beat_cycles 0 -> 1, and the summary states the next frontier.
  Report either way: the new October headroom if banked, August's
  value, and the updated N4-revisit August shortfall (required
  August >= Rs4,020.54; shortfall = 4,020.54 - August_after).
- Basis: equity cash, paper only, real Rs0, provisional per
  100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-7 — F4 component excludes UNITDSPR SHORT signals (frozen 2026-10-31, BEFORE scoring)
- **Family:** stock x mechanism x DIRECTION exclusion (Lessons 11/15):
  the F4 component takes NO SHORT signals on UNITDSPR. F4 keeps
  UNITDSPR LONG; N4-V3, P2F and INV-LONG trade UNITDSPR unchanged.
  No other change.
- **Diagnosis (current book, anchor exact 799 tr / +Rs146,423.19):**
  August +103.44 = event systems +7,777.03 against F4 -7,369.24
  (15 tr, 9 stops -9,700.92, all on Aug 20/27/28/31). F4 x UNITDSPR
  is the ONLY F4 stock slice negative in BOTH August (-1,947.84 /
  3 tr) and full period (-1,294.84 / 13 tr); its direction split is
  the Lesson 15 pattern — LONG half +552.17 (5 tr), SHORT half
  -1,847.01 (8 tr, 3 winners). The whole-stock removal stays
  floor-blocked (October +2,617.85 > headroom 1,129.79), but the
  SHORT half's October slice (+780.00, 1 tr) FITS the headroom —
  the SAT-2 block (headroom then 572.02) has lifted at the current
  book (Lesson 16 re-check). Slice month nets: Feb -1,123.04,
  Mar -331.81, Apr -500.00, Aug -672.16, Oct +780.00 — every other
  affected month improves on removal; no thin month is hurt.
  Winners-side state search was NEGATIVE (reported, not forced):
  August's F4 winners share no ex-ante state the losers lack
  (all 15 F4 August trades enter 10:xx; premove sub-bands positive
  full-period in every band; event-system wins are GLENMARK
  reaction-following in both directions) — no gate exists; the
  direction-scoped deletion is the fix.
- **Scoring:** rebuild the incumbent from the audited dumps with
  ALL current filters (anchor must match the state to the paisa:
  799 tr / +Rs146,423.19 / October +Rs51,129.79), delete exactly
  the F4 x UNITDSPR x SHORT set (8 tr / -Rs1,847.01 asserted),
  recompute the month table. Timing validity is inherited
  (deletion-only from the pre-audited F4 dump).
- **Saturation gate:** bank iff (a) union total > +Rs146,423.19;
  (b) all ten months > 0; (c) October >= +Rs50,000 after the drop
  (expected 50,349.79). If banked: the exclusion becomes part of
  the book, no_beat_cycles stays 0, best_total updates. If any leg
  fails: do NOT bank, no_beat_cycles 0 -> 1. Report either way:
  August's new value and the updated N4-revisit August shortfall
  (required August >= Rs4,020.54; shortfall = 4,020.54 - Aug_after).
- Basis: equity cash, paper only, real Rs0, provisional per
  100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-8 — F4 component excludes HINDCOPPER SHORT signals (frozen 2026-10-31, BEFORE scoring)
- **Family:** stock x mechanism x DIRECTION exclusion (Lessons 11/15):
  the F4 component takes NO SHORT signals on HINDCOPPER. F4 keeps
  HINDCOPPER LONG; N4-V3, P2F and INV-LONG trade HINDCOPPER unchanged.
  No other change.
- **Diagnosis (SAT-8 diag, stocks_engine_sat8_diag.py — re-derived at
  the CURRENT post-SAT-7 book per Lesson 16; anchor exact 791 tr /
  +Rs148,270.20 / month table to the paisa):** the slice re-measures
  IDENTICAL to the SAT-7 diag record — the intervening SAT-7 change
  (UNITDSPR SHORT) acts on a disjoint stock, so the deltas did not
  expire (Lesson 16 invariance clause): **12 tr, net -Rs1,094.95,
  4 winners, all skill_or_breakdown direct legs.** Month nets:
  Jan -476.24, Mar +302.13, Apr +65.00, May -479.08, Jun +346.00,
  Aug -959.56 (2 tr: Aug 20 -486.60, Aug 27 -472.96 — the same late-
  August F4 stop cluster SAT-2/SAT-7 diagnosed), Sep +106.80,
  Oct 0.00 (1 tr, 2026-10-30, scratch -0.00). The direction split is
  the Lesson 15 pattern: the name as a whole is +697.56 only because
  the LONG half earns (+1,792.51, 4 tr, 3 w) — the SHORT half is the
  rot, and its October slice is exactly Rs0.00, so it fits the
  Rs349.79 October headroom at zero cost. This is the only remaining
  Aug-negative/full-negative F4 direction slice that fits the
  headroom (SAT-7 diagnosis); F4 x GLENMARK x SHORT stays
  floor-blocked (October +1,404.72 > 349.79) and is a Lesson 6
  concentration name.
- **Scoring:** rebuild the incumbent from the audited dumps with
  ALL current filters (incl. SAT-7's UNITDSPR-SHORT; anchor must
  match the state to the paisa: 791 tr / +Rs148,270.20 /
  October +Rs50,349.79), delete exactly the F4 x HINDCOPPER x SHORT
  set (12 tr / -Rs1,094.95 asserted), recompute the month table.
  Timing validity is inherited (deletion-only from the pre-audited
  F4 dump).
- **Saturation gate:** bank iff (a) union total > +Rs148,270.20
  (expected +Rs149,365.15); (b) all ten months > 0 (expected min
  August +Rs1,735.16); (c) October >= +Rs50,000 after the drop
  (expected unchanged +Rs50,349.79); (d) ex-top-3 not worse.
  If banked: the exclusion becomes part of the book, no_beat_cycles
  stays 0, best_total updates. If any leg fails: do NOT bank,
  no_beat_cycles 0 -> 1. Report either way: August's new value and
  the updated N4-revisit August shortfall (required August >=
  Rs4,020.54; shortfall = 4,020.54 - Aug_after).
- Basis: equity cash, paper only, real Rs0, provisional per
  100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-9 — CHALLENGER F4-MIRROR: capped-band signal-fade on ABOVE-50DMA days (frozen 2026-10-31, BEFORE scoring)
- **Family:** NEW COMPONENT (challenger, self-improvement charter): the
  mirror image of the F4 state gate across the regime axis. Diagnosed
  in CH-2 (population counted, drift a coin-flip) but NEVER built or
  scored. This is the SAT-9 frontier named in the state after the
  August direction-slice space was exhausted (SAT-8).
- **Definition (verbatim, no free parameters left):** a stock-day
  qualifies iff (i) it is an ABOVE-50DMA day — Nifty prior close >
  50DMA, i.e. NOT H1.below50(day), the exact complement of F4's
  regime gate, same NIFTY_REG map; (ii) the capped morning move by
  10:00 (M.premove, close of last bar before 10:00 vs day open) has
  0.5% <= |pm| < 1.0% — the same band as F4; (iii) not a
  weekend/special session (RF-1, book-wide).
- **Entry:** signal mode (H1.build_cell, dirmode="fade") — the first
  V5 signal at/after 10:00 whose direction is AGAINST the morning
  move (up-move -> SHORT entry, down-move -> LONG entry), entered at
  the next bar's open. FIRST-SIGNAL-ONLY per stock-day (the book's
  F4R1 rule): at most one mirror trade per stock-day.
- **Exits:** T150/S080 (target +1.50%, stop -0.80%, square-off 15:10)
  — F4's book exits, U.replay_plain, unchanged.
- **Exclusions (the book's mechanism-scoped F4 exclusions, applied
  symmetrically to the mirror's own trades by (stock x traded
  direction)):** setup3_bounce_rejection signals not taken;
  GODREJCP x SHORT, INDUSTOWER x LONG, HINDUNILVR x SHORT,
  UNITDSPR x SHORT, HINDCOPPER x SHORT trades dropped. An excluded
  first signal leaves NO trade that stock-day (deletion semantics,
  identical to the book's loaders).
- **Controls (same pass, mandatory):** timing audit counted in-build
  (H1._AUDIT: entry >= 10:00, signal >= 10:00, entry after signal);
  Placebo A = SIGN-FLIP (identical build, dirmode="follow" on the
  same above50 days, same exclusions) — the mirror must beat it;
  Placebo B = LAG (identical fade build, premove taken from the
  previous trading day for that stock, regime gate on the actual
  day) — the mirror must beat it. Breadth (stocks > 0) and
  ex-top-3 reported for the component. Overlap vs incumbent F4
  verified mechanically: F4 trades only on below50 days, the mirror
  only on above50 days, so the (date) sets — and a fortiori the
  (date, symbol) sets — must be disjoint; asserted in the run.
- **Scoring:** incumbent rebuilt from the audited dumps with ALL
  current filters (incl. SAT-8's HINDCOPPER-SHORT; anchor must match
  the state to the paisa: 779 tr / +Rs149,365.15 / October
  +Rs50,349.79). Union = incumbent + mirror (components trade
  independently, as everywhere in this book). October note: October
  2026 was 100% below50 days, so the mirror's October slice is
  expected to be zero trades / Rs0.00 — reported, not assumed.
- **Saturation gate:** bank the component iff (a) union total >
  +Rs149,365.15; (b) all ten months > 0; (c) October >= +Rs50,000;
  (d) union ex-top-3 not worse than Rs30,773.31; AND (e) controls:
  audit clean AND mirror standalone net beats BOTH placebos.
  If banked: the mirror becomes the book's 5th component,
  no_beat_cycles stays 0, best_total updates. If any leg fails:
  do NOT bank, no_beat_cycles 0 -> 1. Report either way: the
  component standalone (total, halves, months, breadth, expectancy,
  both placebo margins), the union month table, August's union
  value and the updated N4-revisit August shortfall (required
  August >= Rs4,020.54; shortfall = 4,020.54 - Aug_union).
- Basis: equity cash LONG/SHORT, paper only, real Rs0, provisional
  per 100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-10 — F4 component exit change: stop -0.80% -> -0.95%, target +1.50% unchanged (frozen 2026-10-31, AFTER diagnosis, BEFORE scoring)
- **Family:** ONE stop step on the incumbent F4 component (the
  programme's historically most productive lever: OC-4 banked
  S065 -> S080 and secured October). Re-test at the CURRENT book per
  Lesson 16 — the peak lab's further steps (to S125) were measured at
  a book whose April (+Rs3,671.26 now) and June (+Rs3,941.51 now) were
  far thinner. Lesson 4 addendum governs: exit medicine is
  population-specific, so THIS book's stop population was diagnosed
  first (stocks_engine_sat10_diag.py / sat10_diag.json).
- **Diagnosis (current book, anchor exact 779 tr / +Rs149,365.15):**
  the F4 component holds 478 trades (net +Rs90,281.54) with 182 stop
  exits (net -Rs127,492.99). Post-exit first passage at -0.95%
  (OC-4 / SAT-2 diag3 method): FULL — 4/182 reach the +1.50% target
  (rescue), 153/182 pass -0.95% first (deeper), 25 neither (10 of
  those close >= flat); rough swing est **+Rs6,951.25**. OCTOBER —
  22 stops: 1 rescue / 15 deeper / 6 neither, est **+Rs2,953.74**
  (predicted October Rs53,303.53). AUGUST — 6 stops: 0 rescue /
  5 deeper / 1 neither, est **-Rs652.72** (predicted August
  Rs1,082.44, still green — consistent with SAT-2: August's stops are
  genuine continuations; the step costs August a little and the
  union gate decides). Predicted month table all-green, predicted
  total Rs156,316.40 — the pre-registered support test (est total up
  AND predicted all-green AND predicted October >= 50,000) PASSES,
  so the step is frozen and scored exactly. The low rescue count
  (4/182) is disclosed: the estimate leans on neither-close value;
  the exact rebuild, not the estimate, is the score.
- **Definition (verbatim, no free parameters left):** the F4
  component rebuilt with M2F machinery (CFG band_hi 1.0, regime
  below50, 10:00 measure, first V5 signal at/after 10:00, follow)
  at TP = 1.50, SP = 0.95 — stop -0.95%, target +1.50% unchanged.
  SINGLE STEP ONLY (no S110/S125 in this cycle). Everything else in
  the book is frozen verbatim: setup3_bounce_rejection not taken;
  first qualifying signal per stock-day only (SAT-6 F4R1 — round2
  legs dropped); the five stock x direction exclusions (GODREJCP
  SHORT, INDUSTOWER LONG, HINDUNILVR SHORT, UNITDSPR SHORT,
  HINDCOPPER SHORT); RF-1 weekend stand-aside; INV-LONG / N4-V3 /
  P2F components untouched (incl. AU-1 / JU-1 / JN-1 exclusions).
  Entries are exit-independent under the first-signal rule, so the
  S095 build must carry the identical entry set to the S080 build.
- **Anchors (all must hold before the fix is judged):** (A) fresh
  rebuild at TP 1.50 / SP 0.80 == stocks_engine_oc4_f4s080_trades.csv
  per-trade (date, symbol, round, net, entry_time); (B) filtered
  S080 rebuild union == state (779 tr / +Rs149,365.15 / month table
  to the paisa); (C) timing audit 0 violations on BOTH builds;
  (D) S095 build entry set (date, symbol, entry_time) == S080 entry
  set after identical filtering.
- **Saturation gate:** bank iff (a) union total > +Rs149,365.15;
  (b) all ten months > 0; (c) October >= +Rs50,000; (d) union
  ex-top-3 not worse than Rs30,773.31; (e) anchors + audit pass.
  If banked: F4's book exits become T150/S095, the new dump is
  written to stocks_engine_sat10_f4s095_trades.csv, no_beat_cycles
  stays 0, best_total updates; the N4-revisit August shortfall is
  recomputed at the new book (required August >= Rs4,020.54) and
  reported. If any leg fails: do NOT bank, no_beat_cycles 1 -> 2,
  and the F4 stop-step frontier at this book is recorded closed in
  the direction measured.
- Basis: equity cash LONG/SHORT, paper only, real Rs0, provisional
  per 100 shares, Rs40/trade, home 25, Jan-Oct 2026.

## SAT-11 — F4 stop step 2 (S095 → S110): NOT FROZEN FOR SCORING — pre-registered support test FAILED on the August leg; F4 stop family CLOSED at S095 (recorded 2026-10-31)
- **Pre-registered support test (set in the cycle brief BEFORE the diagnosis ran):** freeze and score the single step S095 → S110 (T150 unchanged, everything else verbatim) ONLY IF the excursion diagnosis of the CURRENT S095 stop population (first passage at −1.10%: rescue to +1.50% / deeper to −1.10% / neither → day close clamped; OC-4 / SAT-2 diag3 / SAT-10 method) estimates (i) total up, (ii) predicted all ten months green with August ≥ ~₹1,000, (iii) predicted October ≥ ₹50,000. If predicted August < ₹500: do NOT score; close the stop family at S095.
- **Diagnosis (stocks_engine_sat11_diag.py / sat11_diag.json; anchor exact — union == state 779 tr / +₹153,263.52, month table to the paisa):** current F4 (T150/S095) = 478 tr / +₹94,179.91; stop exits 155 / −₹130,188.29. First passage at −1.10%: FULL **1 rescue / 126 deeper / 28 neither** (8 closed ≥ flat), rough swing est **+₹6,686.35** (predicted total ₹159,949.87); OCTOBER (17 stops) 0 rescue / 11 deeper / 6 neither, est +₹2,610.24 (predicted ₹53,527.27); AUGUST (5 stops) **0 rescue / 5 deeper / 0 neither**, est **−₹1,168.73** (predicted August **+₹13.70**).
- **Verdict:** legs (i) and (iii) pass on the estimate; leg (ii) FAILS — predicted August ₹13.70 is below both the ~₹1,000 support line and the ₹500 family-close line. Per the pre-registered rule the step was **NOT frozen and NOT scored**; the incumbent is unchanged (F4 exits stay T150/S095). The **F4 stop family is CLOSED at S095 on this window**; reopening requires August thickened by other means first (Lesson 14 sequencing), then a fresh excursion diagnosis of whatever stop population exists then.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-12 — F4 target step (T150 → T165): NOT FROZEN FOR SCORING — pre-registered support test FAILED on the total leg; F4 TARGET FAMILY CLOSED at T150 (recorded 2026-10-31)
- **Pre-registered support test (set in the cycle brief BEFORE the diagnosis ran):** freeze and score the single step T150 → T165 (S095 unchanged, everything else verbatim) ONLY IF the excursion diagnosis of the CURRENT F4 winner population (target exits only; post-exit first passage to +1.65% vs −0.95% up to the 15:10 square-off, neither → square-off close clamped; SAT-10 diag method mirrored to the winner side, both sides counted honestly) estimates (i) total up, (ii) predicted all ten months green, (iii) predicted October ≥ ₹50,000. If the test fails: do NOT score; record the target family as closed at T150.
- **Diagnosis (stocks_engine_sat12_diag.py / sat12_diag.json; anchor exact — union == state 779 tr / +₹153,263.52, month table to the paisa):** current F4 (T150/S095) = 478 tr / +₹94,179.91; target exits 133 / +₹183,123.20. Post-exit first passage at +1.65%: FULL **103 reach / 3 stop-first / 27 neither** (6 no later bars), rough swing est **−₹8,293.33** (predicted total ₹144,970.19). The asymmetry is the finding: reach pays +0.15 × entry (103 tr, +₹14,303.80, avg +₹138.87) but each neither gives back most of the banked target (27 tr, −₹19,286.20, avg −₹714.30) and each stop-first loses target + stop (3 tr, −₹3,310.93, avg −₹1,103.64). A 77% reach rate cannot pay for a ~5:1 per-trade give-back ratio. OCTOBER (36 targets): 27 reach / 0 stop-first / 9 neither, est **+₹1,560.27** → predicted ₹52,477.30 (headroom ₹2,477.30 — the step WOULD have unlocked the GLENMARK-SHORT block, but only by spending ₹8,293.33 of total to buy it). AUGUST (2 targets): 2 reach / 0 / 0, est +₹153.67 → predicted ₹1,336.10. Worst month swings: January −₹5,815.82 (18 targets), April −₹2,830.49, May −₹1,880.93.
- **Verdict:** leg (i) FAILS — estimated total DOWN ₹8,293.33; legs (ii) and (iii) pass on the estimate. Per the pre-registered rule the step was **NOT frozen and NOT scored**; the incumbent is unchanged (F4 exits stay T150/S095). The **F4 TARGET FAMILY is CLOSED at T150 on this window** (the T125 → T150 step banked at OC-3 was the ladder's last paying rung at this population; reopening requires a fresh winner-population diagnosis at a materially different book state).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-13 — NEW COMPONENT P2F-R2 (P2F's information axis extended to R+2, with the book's event-follow name exclusions): FROZEN FOR SCORING (2026-10-31)
- **Diagnosis first (stocks_engine_sat13_diag.py / sat13_diag.json; anchor exact — union == state 779 tr / +₹153,263.52 / month table to the paisa / ex-top-3 ₹38,278.28):** two directions weighed. (1) Book-wide (comp × stock × dir) slice scan at the CURRENT book: 31 qualifying rows but all small — the largest full-period loss is F4 × OIL × SHORT (−₹2,712.77 / 13 tr; June −₹486.88; Oct slice −₹465.84) and most rows are single-trade thin-month slices; weighed and NOT chosen (the R2 union effect is ~5× the best slice, and slices stay available — adding a disjoint component does not consume them). (2) P2F-R2 built with the audited stocks_tuning_event.py machinery verbatim: construction anchor 39 candidates == the M1 raw P2F@2.5 population; 38 trades built (RECLTD R=2026-10-27 dropped — no R+2 in the daily series); timing audit 0 violations (every date == the stock's 2nd trading day after R by construction, entry = R+2 first-bar open 09:15); (date,stock) overlap vs incumbent P2F = 0; RF-1 weekend trades = 0. Standalone RAW: 38 tr / +₹9,813.68, expectancy +₹258.25, win 19/38, breadth 12, halves H1 +₹12,288.08 / **H2 −₹2,474.40 (disclosed weakness)**; placebo (opposite direction, identical entries) 38 tr / −₹477.83, expectancy −₹12.57 — R2 beats the placebo overall and per-trade, but NOT in H2 (placebo H2 +₹1,455.72). With the book's event-follow name exclusions applied (below): 34 tr / +₹12,912.48, expectancy +₹379.78, H1 +₹13,472.08 / H2 −₹559.60; the 4 excluded trades net −₹3,098.80 — the fade-profile names lose at R+2 too (Lesson 11, consistent).
- **Definition (verbatim, no free parameters left):** a FIFTH component, traded independently alongside the incumbent four. Event set, reaction definition and candidate generation EXACTLY as the incumbent P2F (stocks_tuning_event.py: results events from stock_event_calendar_jan_oct_2026.csv, effective reaction date R within [announce, announce+7d], reaction_ret = R close / prior close − 1, incumbent candidate window ALL_HI 2026-10-28 on R and R+1). Band |reaction_ret| ≥ 2.5% (the incumbent P2F band). Entry: the OPEN of the first 5-minute bar on **R+2** — the stock's second trading day after R (daily[ri+2]) — in the reaction direction (LONG if reaction_ret > 0 else SHORT), entry_time stamped 09:15. Exits: T125/S050 (target +1.25%, stop −0.50%) via the verbatim replay engine, square-off at the 15:10 bar close. ₹40/trade, per 100 shares. **Book law applied as part of the definition (SAT-9 precedent — the mirror carried the book's F4 exclusions in its definition): RF-1 weekend stand-aside (0 trades affected), and the event-follow mechanism-scoped name exclusions AU-1 (no ASTRAL) and JU-1 (no HINDUNILVR) — both frozen for this mechanism family BEFORE this component existed, on frozen reaction-profile evidence (Lesson 11), not fitted to R2.** Everything else in the book is frozen verbatim (INV-LONG / N4-V3 / P2F / F4 T150/S095 first-signal-only with all SAT-1..SAT-8 exclusions).
- **Disclosed variant:** the RAW component (no name exclusions) was also diagnosed: union +₹163,077.20, min month July +₹922.99, August +₹2,756.43, ex-top-3 ₹50,344.06 — it passes the same gate but weaker on every leg. The frozen definition above is the book-consistent one; both are recorded so the choice is auditable.
- **Anchors (all must hold before the fix is judged):** (A) incumbent union rebuild == state (779 tr / +₹153,263.52 / month table / ex-top-3 ₹38,278.28); (B) R2 candidate population == 39 (== M1 raw P2F@2.5) and the frozen 34-trade set == the diagnosis set (date, symbol, dir, net); (C) timing audit 0 violations and (date,stock) overlap vs incumbent P2F == 0; (D) placebo re-scored on the frozen 34-candidate subset and reported (not a gate leg — disclosed).
- **Saturation gate:** bank iff (a) union total > +₹153,263.52; (b) all ten months > 0; (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹38,278.28; (e) anchors + audit pass. If banked: P2F-R2 becomes the book's 5th component (dump stocks_engine_sat13_p2fr2_trades.csv), no_beat_cycles → 0, best_total updates; the N4-revisit August shortfall is recomputed (required August ≥ ₹4,020.54) and reported; the component's negative H2 (−₹559.60) is carried as a disclosed December-judging risk (Lesson 7). If any leg fails: do NOT bank, no_beat_cycles 2 → 3, and the run closes SATURATED (candidate spec + final summary per protocol).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-14 — P2F component excludes HINDALCO LONG signals (stock × mechanism × DIRECTION exclusion, from the SAT-13 slice registry, re-derived at the current book): FROZEN FOR SCORING (2026-10-31)
- **Diagnosis first (stocks_engine_sat14_diag.py / sat14_diag.json; anchor exact — current book == state: 813 tr / +₹166,176.00 / month table to the paisa / ex-top-3 ₹51,853.86; components INV-LONG 218 / N4-V3 50 / P2F 33 / F4 478 / P2F-R2 34):** the SAT-13 slice registry was re-derived from scratch at the CURRENT five-component book (Lesson 16 — registry numbers were hypotheses about a four-component book). Scan for (comp × stock × dir) slices negative in AUGUST and negative FULL-PERIOD: 8 slices. Feasible under the cycle's constraints (August gain ≥ ₹449.11 — the exact CH-2 N4-rebuild revisit shortfall; October slice ≤ ₹1,107.02 headroom; every month green after removal): exactly 2 — F4 × GLENMARK × SHORT (20 tr; Aug −₹4,744.78 but full only −₹136.98, win 10/20, October slice +₹1,062.55 which would leave October at ₹50,044.47, and a Lesson 6 top-3 name the state already marks not-a-real-candidate — NOT chosen) and the slice below. Pre-registered selection rule: least surgery = fewest trades removed, tie-break smallest |full net|.
- **The slice (re-verified trade-by-trade at the current book before freezing):** P2F × HINDALCO × LONG = **1 trade** — 2026-08-10, entry 09:15, exit stop, net **−₹572.50** (reaction R = 2026-08-07, reaction_ret +3.17%). It is P2F's ONLY HINDALCO trade in the book, so the slice is the component's entire position in that name × direction: August slice −₹572.50, full-period −₹572.50, October slice exactly ₹0.00.
- **THIN-SAMPLE CAVEAT (disclosed, first-class):** this is a ONE-TRADE slice — the thinnest evidence class the engine has ever banked on (JU-1 banked on 2). The claim is NOT that HINDALCO-LONG reactions are a discovered loser population; it is the mechanical Lesson 5/15 shape (negative in the target month AND full-period, October-neutral) at minimum surgery, taken to discharge the CH-2 revisit arithmetic (Lesson 14 sequencing). December fresh data judges the assembled book, not this trade.
- **Definition (verbatim):** the P2F 2.5% component does NOT take LONG signals on HINDALCO (P2F keeps HINDALCO SHORT if any arise; N4-V3 / INV-LONG / F4 / P2F-R2 trade HINDALCO unchanged — mechanism × direction scoped per Lessons 11/15). Everything else in the book is frozen verbatim (five components; F4 T150/S095 first-signal-only with all SAT-1..SAT-8 exclusions; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** August ₹3,571.43 → ₹4,143.93 (≥ ₹4,020.54 — the N4-rebuild revisit condition on the August leg); total ₹166,176.00 → ₹166,748.50; October unchanged ₹51,107.02; trades 813 → 812; all other months unchanged.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (813 tr / +₹166,176.00 / month table / ex-top-3 ₹51,853.86); (B) the deleted set extracted at scoring == the frozen 1-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹166,176.00; (b) all ten months > 0; (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹51,853.86; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates, and the N4-rebuild revisit status is reported (August leg only — the rebuild itself is re-measured and re-applied in SAT-15, not here; its CH-2 August delta of −₹3,834.85 and June condition must be re-measured at the then-current book per Lesson 16). If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-15 — RE-MEASUREMENT + RE-APPLY of the CH-2 N4-V3 exit rebuild (T125/S050 → T150/S080) at the current five-component book: FROZEN FOR SCORING (2026-10-31)
- **Charter:** Lesson 16 — CH-2's deltas (component +₹9,483.45; August −₹3,834.85; June −₹654.66 flip) were measured on a FOUR-component book 14 cycles ago and are STALE: they are hypotheses, not numbers. This cycle re-measures everything at the current book before any re-apply. Lesson 14 — the revisit sequencing obligation is discharged on both legs (June covered since SAT-1; August leg met since SAT-14: August +₹4,143.93 ≥ ₹4,020.54, margin ₹123.39); discharge of the sequencing obligation is NOT a verdict on the rebuild — the rebuild banks or fails on THIS measurement alone.
- **Definition (verbatim, no free parameters):** the N4-V3 component's ENTRIES are unchanged — the frozen T125/S050 entry set from eq_n4deep_v3_trades_T125_janoct.csv (56 raw trades; entry 09:35, reaction direction), replayed on the audited 5-minute candle store with the CH-2 convention (start_offset determined empirically by the T125/S050 replay anchor; stop checked before target within a bar; square-off at the 15:10 bar close). ONLY the exits change: target +1.25% → **+1.50%**, stop −0.50% → **−0.80%**. ₹40/trade, per 100 shares. Book law applied identically to the incumbent N4: RF-1 weekend stand-aside and the AU-1 mechanism-scoped exclusion (no ASTRAL). Everything else in the book is frozen verbatim (INV-LONG excl. BDL; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 T150/S095 first-signal-only with all SAT-1..SAT-8 exclusions from stocks_engine_sat10_f4s095_trades.csv; P2F-R2 with AU-1/JU-1 exclusions).
- **Anchors (all must hold before the rebuild is judged):** (A) current-book rebuild == state (812 tr / +₹166,748.50 / month table to the paisa / ex-top-3 ₹52,426.36; components INV-LONG 218 / N4-V3 50 / P2F 32 / F4 478 / P2F-R2 34 — P2F is 32 after SAT-14's HINDALCO-LONG removal); (B) N4 replay at T125/S050 reproduces the book's N4 component PER-TRADE (date, stock, dir, net) after identical filtering — the replay machinery must regenerate the incumbent before it may measure the challenger; (C) timing/entry audit on the T150/S080 build: entries identical to the anchor trades (date, stock, direction, 09:35 entry_time, entry price), exit_time ≥ entry_time (entry-bar convention, as in CH-2), 0 violations.
- **Saturation gate:** bank the rebuild iff (a) union total > +₹166,748.50; (b) all ten months > 0; (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹52,426.36; (e) anchors + audit pass. If banked: N4-V3's book exits become T150/S080, the new dump is written to stocks_engine_sat15_n4_t150s080_trades.csv, no_beat_cycles stays 0, best_total updates; the book's N4 source for future cycles is the SAT-15 dump (state must record this). If any month flips red (August named in the brief; June watched): do NOT bank, no_beat_cycles 0 → 1, and record the EXACT new revisit arithmetic at THIS book — the pre-rebuild August (and June) balance the rebuild would need in order to pass leg (b) — in the state and log.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-16 — NEW COMPONENT P2F-R3 (P2F's information axis extended to R+3): FROZEN FOR SCORING (2026-10-31)
- **Diagnosis first (stocks_engine_sat16_diag.py / sat16_diag.json; anchor exact — incumbent anchored from the CURRENT component dumps per SAT-15 book law: INV-LONG 218 / N4-V3 50 from stocks_engine_sat15_n4_t150s080_trades.csv (M1.load_n4() NOT used) / P2F 32 / F4 478 / P2F-R2 34 = 812 tr / +₹176,231.95 / month table to the paisa / ex-top-3 ₹56,308.12, top-3 TVSMOTOR / ASTRAL / OBEROIRLTY):** P2F-R3 built with the SAT-13 machinery verbatim at lag ri+3: construction anchor 39 candidates == the M1 raw P2F@2.5 population (the same reaction set as P2F/R2); 38 trades built (RECLTD R=2026-10-27 dropped — no R+3 in the daily series); timing audit 0 violations (every date == the stock's 3rd trading day after R by construction, entry = R+3 first-bar open 09:15); (date,stock) overlap vs incumbent P2F = 0 and vs P2F-R2 = 0 (mechanical); within-R3 duplicate (symbol,date) = 0; RF-1 weekend trades = 0. Frozen variant (RF-1 + AU-1/JU-1 name exclusions): **34 tr / +₹952.10, expectancy +₹28.00, win 12/34, breadth 21, H1 +₹2,641.97 / H2 −₹1,689.87**. The 4 excluded-name trades net −₹1,536.40 (ASTRAL −₹780.90 / −₹809.20; HINDUNILVR −₹1,196.30 / +₹1,250.00 — mostly the Lesson 11 fade profile again, one winner). **Controls verdict in the same pass: the opposite-direction placebo on identical entries beats the real rule — 34 tr / +₹4,064.36, expectancy +₹119.54, H1 +₹534.80 / H2 +₹3,529.56.** Per Lesson 18's discipline (a placebo must be beaten per-trade), R3 carries no follow signal: at R+3 the reaction direction is noise, and in H2 it is worse than its own flip. August slice +₹130.25 (positive but negligible); July slice −₹1,727.50 flips July red in the union; ex-top-3 falls. The freeze below is recorded so the scoring is auditable; the diagnosis already says the gate cannot pass.
- **Definition (verbatim, no free parameters left):** a SIXTH component, traded independently alongside the incumbent five. Event set, reaction definition and candidate generation EXACTLY as the incumbent P2F (stocks_tuning_event.py: results events from stock_event_calendar_jan_oct_2026.csv, effective reaction date R within [announce, announce+7d], reaction_ret = R close / prior close − 1, incumbent candidate window ALL_HI 2026-10-28 on R and R+1). Band |reaction_ret| ≥ 2.5% (the incumbent P2F band). Entry: the OPEN of the first 5-minute bar on **R+3** — the stock's third trading day after R (daily[ri+3]) — in the reaction direction (LONG if reaction_ret > 0 else SHORT), entry_time stamped 09:15. Exits: T125/S050 (target +1.25%, stop −0.50%) via the verbatim replay engine, square-off at the 15:10 bar close. ₹40/trade, per 100 shares. **Book law applied as part of the definition (SAT-9/SAT-13 precedent): RF-1 weekend stand-aside (0 trades affected), and the event-follow mechanism-scoped name exclusions AU-1 (no ASTRAL) and JU-1 (no HINDUNILVR) — frozen for this mechanism family before this component existed (Lesson 11), not fitted to R3.** Everything else in the book is frozen verbatim (INV-LONG excl. BDL; N4-V3 at T150/S080 from the SAT-15 dump, excl. ASTRAL; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 T150/S095 first-signal-only with all SAT-1..SAT-8 exclusions; P2F-R2 with AU-1/JU-1 exclusions).
- **Anchors (all must hold before the fix is judged):** (A) incumbent union rebuild == state (812 tr / +₹176,231.95 / month table / ex-top-3 ₹56,308.12) with N4 anchored on the SAT-15 dump; (B) R3 candidate population == 39 (== M1 raw P2F@2.5) and the frozen 34-trade set == the diagnosis set (date, symbol, dir, net); (C) timing audit 0 violations and (date,stock) overlap vs incumbent P2F == 0 and vs P2F-R2 == 0; (D) placebo re-scored on the frozen 34-candidate subset and reported (disclosed; per Lesson 18 a placebo beaten per-trade is itself disqualifying evidence, recorded in the verdict).
- **Saturation gate:** bank iff (a) union total > +₹176,231.95; (b) all ten months > 0 (August reported explicitly — R3's August slice must not un-secure the +₹309.08 razor); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹56,308.12; (e) anchors + audit pass. If banked: P2F-R3 becomes the book's 6th component (dump stocks_engine_sat16_p2fr3_trades.csv), no_beat_cycles stays 0, best_total updates. If any leg fails: do NOT bank, no_beat_cycles 0 → 1, and the R-ladder is recorded CLOSED at R+2 (Lesson 19's persistence is an R+2 fact, not a ladder).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-17 — N4-V3 component excludes TVSMOTOR LONG signals (stock × mechanism × DIRECTION exclusion, top of the re-derived slice registry): FROZEN FOR SCORING (2026-10-31)
- **Diagnosis first (stocks_engine_sat17_diag.py / sat17_diag.json; anchor exact — current book == state: 812 tr / +₹176,231.95 / month table to the paisa / ex-top-3 ₹56,308.12; components INV-LONG 218 / N4-V3 50 from stocks_engine_sat15_n4_t150s080_trades.csv (SAT-15 book law — M1.load_n4() NOT used) / P2F 32 / F4 478 / P2F-R2 34):** the (comp × stock × dir) slice registry was re-derived FROM SCRATCH at the current five-component book (Lesson 16 — SAT-13's registry described a four-component book and SAT-15 changed every N4 slice). 148 slices total; **28 qualify** (full-period negative AND negative in ≥ 1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,247.76 headroom). Ranked by full-period value (most negative first), the quality bar applied (genuinely negative full period — the GLENMARK-SHORT pattern, Aug −₹4,744.78 vs full only −₹136.98 / 10 of 20 winners, sits at the BOTTOM of this registry at −₹136.98 and is below the bar as recorded), and feasibility applied (removal leaves every month > 0, the razors Aug/Jul/Jun with ≥ ₹100 margin, October ≥ ₹50,000, ex-top-3 not worse): the TOP row is the slice below. Next rows for the record: F4 × OIL × SHORT (−₹2,712.77 / 13 tr / 4 w; Jun −₹486.88; Oct slice −₹465.84), INV-LONG × VEDL × LONG (−₹2,424.75 / 18 tr / 4 w; Apr-negative), INV-LONG × HINDZINC × LONG (−₹2,131.83 / 9 tr / 1 w) — the registry queue persists for later cycles.
- **The slice (re-verified trade-by-trade at the current book before freezing):** N4-V3 × TVSMOTOR × LONG = **1 trade** — **2026-07-22, entry 09:35 at ₹3,932.20, exit stop at ₹3,900.74 at 14:00, net −₹3,185.76** at the book's T150/S080 exits (combined (results) reaction, move by 09:30 +3.58%; at the old T125/S050 exits the same entry was −₹2,006.10, stop 10:25). It is N4-V3's ONLY TVSMOTOR LONG trade in the book (the component's two other TVSMOTOR trades are SHORTs and earn +₹5,476.55 / +₹5,129.45 — the direction split is the Lesson 15 shape): July slice −₹3,185.76, full-period −₹3,185.76, October slice exactly ₹0.00, August/June slices exactly ₹0.00.
- **THIN-SAMPLE CAVEAT (disclosed, first-class):** this is a ONE-TRADE slice — the thinnest evidence class (SAT-14 banked one such, disclosed the same way). The claim is NOT that TVSMOTOR-LONG reactions are a discovered loser population — one trade cannot show that, and TVSMOTOR remains the book's largest earner overall (its SHORT reactions inside this same component are two of the component's best trades). The claim is the mechanical Lesson 5/15 registry shape at the top of the re-derived queue: the slice is the most-negative full-period row in the book, it sits entirely inside a razor month (July +₹1,262.53), and its removal is October-neutral and August-neutral. December fresh data judges the assembled book, not this trade.
- **Definition (verbatim):** the N4-V3 component (T150/S080 exits, SAT-15 dump as its trade source) does NOT take LONG signals on TVSMOTOR (N4-V3 keeps TVSMOTOR SHORT; INV-LONG / P2F / F4 / P2F-R2 trade TVSMOTOR unchanged — mechanism × direction scoped per Lessons 11/15). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 T150/S095 first-signal-only with all SAT-1..SAT-8 exclusions; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** July ₹1,262.53 → ₹4,448.29; total ₹176,231.95 → ₹179,417.71; October unchanged ₹52,247.76 (headroom ₹2,247.76); August unchanged ₹309.08 (still the razor); trades 812 → 811; ex-top-3 unchanged ₹56,308.12 (the removed trade is on a top-3 name, so total and top-3 rise together — leg (d) passes as equality).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (812 tr / +₹176,231.95 / month table / ex-top-3 ₹56,308.12); (B) the deleted set extracted at scoring == the frozen 1-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹176,231.95; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹56,308.12; (e) anchors pass. If banked: no_beat_cycles 1 → 0, best_total updates; N4-V3's TVSMOTOR-LONG exclusion is recorded as book law (future cycles anchoring N4 on the SAT-15 dump must apply it). If any leg fails: do NOT bank, no_beat_cycles 1 → 2.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-18 — F4 component excludes OIL SHORT signals (stock × mechanism × DIRECTION exclusion, next row of the re-derived slice registry): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat18_diag.py):** registry re-derived from scratch at the post-SAT-17 book (147 slices, 27 qualifying). The brief's target slice re-measured trade-by-trade and is **IDENTICAL to the SAT-17 registry record to the paisa** (13 tr / −₹2,712.77; Jun −₹486.88; Oct −₹465.84) — SAT-17 intervened only on an N4 leg, disjoint from F4, so the deltas did not expire (Lesson 16 invariance, fourth positive instance).
- **The frozen slice — F4 × OIL × SHORT, the exact 13 trades to be deleted (date, net):** 2026-01-20 +505.00 · 2026-02-03 −495.53 · 2026-02-05 +305.00 · 2026-02-20 −140.00 · 2026-02-24 +135.00 · 2026-02-25 −65.00 · 2026-03-25 −483.89 · 2026-04-15 +40.00 · 2026-05-14 −529.63 · 2026-05-15 −530.20 · 2026-06-09 −486.88 · 2026-09-02 −500.80 · 2026-10-21 −465.84. **Sum −₹2,712.77, 4 winners of 13.**
- **Month profile of the slice:** Jan +505.00 · Feb −260.53 · Mar −483.89 · Apr +40.00 · May −1,059.83 · Jun −486.88 · Jul 0.00 · **Aug exactly 0.00 (no August trades — the razor is untouched)** · Sep −500.80 · **Oct −465.84 (negative — removal RAISES October, no headroom spent)**. Negative in a thin month (June) AND full-period — the Lesson 5 shape; full −₹2,712.77 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × OIL × LONG earns +₹491.75 (6 tr, 4 w) and stays; the name as a whole (−₹2,221.02) is negative only because the SHORT half is the rot.
- **Definition (verbatim):** the F4 component (T150/S095 exits, first-signal-only, SAT-10 dump as its trade source) does NOT take SHORT signals on OIL (F4 keeps OIL LONG; INV-LONG / N4-V3 / P2F / P2F-R2 trade OIL unchanged — mechanism × direction scoped per Lessons 11/15). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹179,417.71 → ₹182,130.48; October ₹52,247.76 → ₹52,713.60 (headroom ₹2,713.60); June ₹1,382.01 → ₹1,868.89; May ₹33,304.29 → ₹34,364.12; August UNCHANGED ₹309.08 (still the razor); trades 811 → 798; ex-top-3 ₹56,308.12 → ₹59,020.89 (improves — OIL is not a top-3 name, so leg (d) passes by improvement, not equality). Small costs on removal: January −505.00 and April −40.00 (both stay strongly green).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (811 tr / +₹179,417.71 / month table / ex-top-3 ₹56,308.12), N4 from the SAT-15 dump minus the SAT-17 TVSMOTOR-LONG exclusion; (B) the deleted set extracted at scoring == the frozen 13-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹179,417.71; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹56,308.12; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's OIL-SHORT exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-19 — INV-LONG component excludes VEDL (stock × mechanism exclusion; INV-LONG is LONG-only, so the slice is the component's whole VEDL population): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat19_diag.py):** registry re-derived from scratch at the post-SAT-18 book (146 slices, 26 qualifying: full-period negative AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,713.60 headroom). Anchor A exact (798 tr / +₹182,130.48 / month table to the paisa / ex-top-3 ₹59,020.89; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-18 registry record to the paisa** (18 tr / −₹2,424.75 / 4 w; Apr-negative; Oct −₹318.05) — SAT-18 intervened only on an F4 leg, disjoint from INV-LONG, so the deltas did not expire (Lesson 16 invariance, fifth positive instance).
- **The frozen slice — INV-LONG × VEDL × LONG, the exact 18 trades to be deleted (date, net):** 2026-01-23 −388.28 · 2026-01-23 −386.95 · 2026-01-29 −417.45 · 2026-02-04 −386.20 · 2026-03-06 +858.87 · 2026-03-11 −411.02 · 2026-03-11 −409.43 · 2026-03-17 −387.73 · 2026-04-15 −423.30 · 2026-05-04 −185.95 · 2026-05-04 −185.80 · 2026-05-12 +341.56 · 2026-05-13 +352.50 · 2026-05-14 −207.60 · 2026-05-14 −206.80 · 2026-06-11 +336.88 · 2026-10-16 −164.25 · 2026-10-26 −153.80. **Sum −₹2,424.75, 4 winners of 18.**
- **Month profile of the slice:** Jan −1,192.68 · Feb −386.20 · Mar −349.31 · **Apr −423.30 (the thin-month leg)** · May −92.09 · Jun +336.88 · Jul 0.00 · **Aug exactly 0.00 (no August trades — the razor is untouched)** · Sep 0.00 · **Oct −318.05 (negative — removal RAISES October, no headroom spent)**. Negative in a thin month (April) AND full-period — the Lesson 5 shape; full −₹2,424.75 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Mechanism scope (Lesson 11): VEDL earns in F4's gated flow (raw dump +₹3,062.75 / 28 tr) and in P2F (+₹575.25) — the rot is inside INV-LONG's below-trend pool only, so the exclusion is INV-LONG-scoped; every other component trades VEDL unchanged. INV-LONG takes LONG signals only, so there is no opposite-direction half inside the component to split (Lesson 15's split does not apply within a one-direction mechanism).
- **Definition (verbatim):** the INV-LONG component (below-trend pool, T125/S050) does NOT take signals on VEDL (INV-LONG keeps all other names; N4-V3 / P2F / F4 / P2F-R2 trade VEDL unchanged — mechanism-scoped per Lesson 11). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹182,130.48 → ₹184,555.23; October ₹52,713.60 → ₹53,031.65 (headroom ₹3,031.65); April ₹7,494.13 → ₹7,917.43; January ₹25,418.78 → ₹26,611.46; August UNCHANGED ₹309.08 (still the razor); trades 798 → 780; ex-top-3 ₹59,020.89 → ₹61,445.64 (improves — VEDL is not a top-3 name). Only cost on removal: June −336.88 → ₹1,532.01 (stays green, keeps ≥ ₹100 razor margin).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (798 tr / +₹182,130.48 / month table / ex-top-3 ₹59,020.89), N4 from the SAT-15 dump minus the SAT-17 TVSMOTOR-LONG exclusion, F4 minus the SAT-18 OIL-SHORT exclusion; (B) the deleted set extracted at scoring == the frozen 18-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹182,130.48; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹59,020.89; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; INV-LONG's VEDL exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.

## SAT-20 — INV-LONG component excludes HINDZINC (stock × mechanism exclusion; INV-LONG is LONG-only, so the slice is the component's whole HINDZINC population): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat20_diag.py):** registry re-derived from scratch at the post-SAT-19 book (145 slices, 11 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65 headroom). Anchor A exact (780 tr / +₹184,555.23 / month table to the paisa / ex-top-3 ₹61,445.64; components INV-LONG 200 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 34; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus the SAT-19 VEDL exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-19 registry record to the paisa** (9 tr / −₹2,131.83 / 1 w; Jun-negative; Oct exactly 0.00) — SAT-19 intervened only on VEDL within INV-LONG, disjoint from HINDZINC, so the deltas did not expire (Lesson 16 invariance, sixth positive instance).
- **The frozen slice — INV-LONG × HINDZINC × LONG, the exact 9 trades to be deleted (date, net):** 2026-01-13 −358.30 · 2026-01-21 −388.20 · 2026-01-21 −388.45 · 2026-02-02 −335.57 · 2026-03-20 −302.75 · 2026-04-07 +620.44 · 2026-04-09 −320.75 · 2026-05-04 −343.48 · 2026-06-11 −314.77. **Sum −₹2,131.83, 1 winner of 9.**
- **Month profile of the slice:** Jan −1,134.95 · Feb −335.57 · Mar −302.75 · Apr +299.69 · May −343.48 · **Jun −314.77 (the thin-month leg)** · Jul 0.00 · **Aug exactly 0.00 (no August trades — the razor is untouched)** · Sep 0.00 · **Oct exactly 0.00 (October-neutral — no headroom spent, none minted)**. Negative in a thin month (June) AND full-period — the Lesson 5 shape; full −₹2,131.83 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Mechanism scope (Lesson 11): HINDZINC also loses inside F4 (−₹631.12), N4-V3 (−₹1,043.24) and P2F (−₹374.40) and earns in P2F-R2 (+₹812.50), but none of those (comp × stock × dir) rows independently qualifies at the bar in this registry — the exclusion is INV-LONG-scoped and every other component trades HINDZINC unchanged. INV-LONG takes LONG signals only, so there is no opposite-direction half inside the component to split (Lesson 15's split does not apply within a one-direction mechanism).
- **Definition (verbatim):** the INV-LONG component (below-trend pool, T125/S050) does NOT take signals on HINDZINC (INV-LONG keeps all other names; N4-V3 / P2F / F4 / P2F-R2 trade HINDZINC unchanged — mechanism-scoped per Lesson 11). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹184,555.23 → ₹186,687.06; October UNCHANGED ₹53,031.65 (headroom ₹3,031.65); June ₹1,532.01 → ₹1,846.78 (the razor month improves); January ₹26,611.46 → ₹27,746.41; August UNCHANGED ₹309.08 (still the razor); trades 780 → 771; ex-top-3 ₹61,445.64 → ₹63,577.47 (improves — HINDZINC is not a top-3 name). Only cost on removal: April −299.69 → ₹7,617.74 (stays strongly green).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (780 tr / +₹184,555.23 / month table / ex-top-3 ₹61,445.64), N4 from the SAT-15 dump minus the SAT-17 TVSMOTOR-LONG exclusion, F4 minus the SAT-18 OIL-SHORT exclusion, INV-LONG minus BDL + the SAT-19 VEDL exclusion; (B) the deleted set extracted at scoring == the frozen 9-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹184,555.23; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹61,445.64; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; INV-LONG's HINDZINC exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat20_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹2,131.83):** 771 tr / **+₹186,687.06**. Month table: Jan 26,611.46 → 27,746.41 (+1,134.95) · Feb 18,112.44 → 18,448.01 (+335.57) · Mar 20,093.11 → 20,395.86 (+302.75) · Apr 7,917.43 → 7,617.74 (−299.69, the slice's only positive month — stays strongly green) · May 34,456.21 → 34,799.69 (+343.48) · Jun 1,532.01 → 1,846.78 (+314.77 — the razor month IMPROVES) · Jul 4,448.29 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 53,031.65 (unchanged — the slice is October-neutral; headroom stays ₹3,031.65)**. Ex-top-3 **₹61,445.64 → ₹63,577.47** (improvement — HINDZINC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹2,131.83; all ten green with razors Aug 309.08 / Jun 1,846.78 / Jul 4,448.29 all ≥ ₹100; October ≥ 50,000; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no HINDZINC signals.** **Saturation: no_beat_cycles stays 0, best_total → ₹186,687.06 — the run is NOT saturated.**
- **Next:** saturation continues from +₹186,687.06 (₹18,669/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (10 qualifying remain at this derivation — re-derive before use; next rows: P2F-R2 × TVSMOTOR × LONG −₹1,979.90, F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20, whose removal would thicken the razor); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-21 — P2F-R2 component excludes TVSMOTOR LONG signals (stock × mechanism × DIRECTION exclusion; P2F-R2 keeps any TVSMOTOR SHORT — none exist in-window — and every other component trades TVSMOTOR unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat21_diag.py):** registry re-derived from scratch at the post-SAT-20 book (144 slices, 10 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65 headroom). Anchor A exact (771 tr / +₹186,687.06 / month table to the paisa / ex-top-3 ₹63,577.47; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 34; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-20 registry record to the paisa** (1 tr / −₹1,979.90 / 0 w; Jul-negative; Oct exactly 0.00; Aug exactly 0.00) — SAT-20 intervened only on an INV-LONG HINDZINC leg, disjoint from P2F-R2, so the deltas did not expire (Lesson 16 invariance, seventh positive instance).
- **The frozen slice — P2F-R2 × TVSMOTOR × LONG, the exact 1 trade to be deleted:** 2026-07-24, TVSMOTOR LONG, entry 09:15 ₹3,879.80, stop exit ₹3,860.40 at 10:05, net **−₹1,979.90** (reaction R = 2026-07-22, +3.24%). **Sum −₹1,979.90, 0 winners of 1.** Thin-sample caveat recorded first-class (1 trade — the SAT-14/SAT-17 precedent class; no population claim is made; TVSMOTOR remains the book's #1 earner and this says nothing about the name, only about this mechanism × direction leg).
- **Month profile of the slice:** Jul **−₹1,979.90 (the thin-month leg — the slice's only trade)** · every other month exactly 0.00, including **Aug exactly 0.00 (the razor is untouched)** and **Oct exactly 0.00 (October-neutral — no headroom spent, none minted)**. Negative in a thin month (July) AND full-period — the Lesson 5 shape; full −₹1,979.90 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Mechanism × direction scope (Lessons 11/15): TVSMOTOR earns massively in every other component (F4 +₹39,505.22, INV-LONG +₹19,049.74, N4-V3 +₹10,606.00 — its LONGs there already minus the SAT-17 exclusion — P2F +₹4,844.50); the rot is this one R+2-follow LONG leg only, so the exclusion is P2F-R2 × LONG-scoped. P2F-R2 has no TVSMOTOR SHORT trades in-window, so no opposite-direction half exists to split inside the component.
- **Definition (verbatim):** the P2F-R2 component (R+2 follow of ≥2.5% reactions, T125/S050, SAT-13 dump as its trade source) does NOT take LONG signals on TVSMOTOR (all other components trade TVSMOTOR unchanged, including N4-V3's SHORTs and its SAT-17 LONG exclusion staying exactly as-is — mechanism × direction scoped per Lessons 11/15). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT; P2F-R2 with AU-1/JU-1 name exclusions; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹186,687.06 → ₹188,666.96; July ₹4,448.29 → ₹6,428.19; October UNCHANGED ₹53,031.65 (headroom ₹3,031.65); August UNCHANGED ₹309.08 (still the razor); trades 771 → 770; ex-top-3 UNCHANGED ₹63,577.47 (the removed trade sits on the #1 earner, so total and top-3 rise together — leg (d) passes as EQUALITY, the SAT-17 pattern; per the Lesson 6 addendum the top-3 share is reported with it: TVSMOTOR ₹72,025.56 → ₹74,005.46, share 38.58% → 39.23% — concentration deepens and is disclosed, not hidden).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (771 tr / +₹186,687.06 / month table / ex-top-3 ₹63,577.47), N4 from the SAT-15 dump minus the SAT-17 TVSMOTOR-LONG exclusion, F4 minus the SAT-18 OIL-SHORT exclusion, INV-LONG minus BDL + VEDL + HINDZINC; (B) the deleted set extracted at scoring == the frozen 1-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹186,687.06; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹63,577.47; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; P2F-R2's TVSMOTOR-LONG exclusion is recorded as book law (future cycles anchoring P2F-R2 on the SAT-13 dump must apply it). If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat21_score.py; Anchor B: deleted set == the frozen 1 trade exactly, net −₹1,979.90):** 770 tr / **+₹188,666.96**. Month table: Jul 4,448.29 → 6,428.19 (+1,979.90 — the slice's only month); every other month identical to the paisa, incl. **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** and **Oct 53,031.65 (unchanged — October-neutral; headroom stays ₹3,031.65)**. Ex-top-3 **₹63,577.47 → ₹63,577.47 (EQUALITY pass** — the removed trade sits on the #1 earner; TVSMOTOR ₹72,025.56 → ₹74,005.46, share 38.58% → 39.23%, concentration deepening disclosed per the Lesson 6 addendum; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,979.90; all ten green with razors Aug 309.08 / Jun 1,846.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000; ex-top-3 not worse — equality on a concentration name, reported as such; anchors clean). **Book law added: P2F-R2 takes no TVSMOTOR LONG signals** (future cycles anchoring P2F-R2 on the SAT-13 dump must apply it). **Saturation: no_beat_cycles stays 0, best_total → ₹188,666.96 — the run is NOT saturated.**
- **Next:** saturation continues from +₹188,666.96 (₹18,867/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (9 qualifying remain at this derivation — re-derive before use; next rows: F4 × IRCTC × SHORT −₹1,297.01, INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20, whose removal would thicken the razor to ~₹714.28); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-22 — F4 component excludes IRCTC SHORT signals (stock × mechanism × DIRECTION exclusion; F4 keeps IRCTC LONG; all other components trade IRCTC unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat22_diag.py):** registry re-derived from scratch at the post-SAT-21 book (143 slices, 9 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,031.65 headroom). Anchor A exact (770 tr / +₹188,666.96 / month table to the paisa / ex-top-3 ₹63,577.47; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 465 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus the SAT-18 OIL-SHORT exclusion; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-21 registry record to the paisa** (13 tr / −₹1,297.01 / 5 w; Apr −₹143.25, Jun −₹105.00 thin-month legs; Oct +₹275.00) — SAT-21 intervened only on a P2F-R2 TVSMOTOR-LONG leg, disjoint from F4, so the deltas did not expire (Lesson 16 invariance, eighth positive instance).
- **The frozen slice — F4 × IRCTC × SHORT, the exact 13 trades to be deleted:** 2026-01-21 −₹619.07 · 2026-01-27 +₹878.45 · 2026-01-28 −₹620.69 · 2026-01-29 +₹260.00 · 2026-03-20 −₹538.09 · 2026-03-24 −₹524.36 · 2026-03-27 +₹185.00 · 2026-04-20 −₹568.25 · 2026-04-24 +₹425.00 · 2026-05-06 −₹345.00 · 2026-06-24 −₹105.00 · 2026-10-16 −₹20.00 · 2026-10-30 +₹295.00. **Sum −₹1,297.01, 5 winners of 13.** A 13-trade slice — a materially thicker evidence class than the 1-trade banks (SAT-14/17/21); the negative is spread across six months, not one accident.
- **Month profile of the slice:** Jan −₹101.31 · Mar −₹877.45 · **Apr −₹143.25 (thin-month leg)** · May −₹345.00 · **Jun −₹105.00 (thin-month leg)** · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct +₹275.00 (POSITIVE — the removal spends ₹275.00 of the ₹3,031.65 headroom, leaving headroom ₹2,756.65 and October ₹52,756.65, still ≥ ₹50,000)** · Feb/Jul/Sep exactly 0.00. Negative in two thin months AND full-period — the Lesson 5 shape; full −₹1,297.01 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × IRCTC × LONG earns +₹497.45 (9 tr) and stays; the SHORT half is the rot. Mechanism scope (Lesson 11): IRCTC earns in INV-LONG (+₹411.40), N4-V3 (+₹235.00) and P2F (+₹616.81) and loses only small in P2F-R2 (−₹296.05, below the bar and a different mechanism — untouched; one slice per cycle); the exclusion is F4 × SHORT-scoped.
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take SHORT signals on IRCTC (F4 keeps IRCTC LONG; all other components trade IRCTC unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹188,666.96 → ₹189,963.97; trades 770 → 757; October ₹53,031.65 → ₹52,756.65 (headroom ₹2,756.65 — this bank SPENDS ₹275.00 of headroom, unlike SAT-18/19 which minted it); August UNCHANGED ₹309.08 (still the razor); June ₹1,846.78 → ₹1,951.78; April ₹7,617.74 → ₹7,760.99; ex-top-3 ₹63,577.47 → ₹64,874.48 (improvement — IRCTC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (770 tr / +₹188,666.96 / month table / ex-top-3 ₹63,577.47), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 13-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹188,666.96; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹63,577.47; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's IRCTC-SHORT exclusion is recorded as book law (future cycles anchoring F4 on the SAT-10 dump must apply it). If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat22_score.py; Anchor B: deleted set == the frozen 13 trades exactly, net −₹1,297.01):** 757 tr / **+₹189,963.97**. Month table: Jan 27,746.41 → 27,847.72 (+101.31) · Feb 18,448.01 (unchanged) · Mar 20,395.86 → 21,273.31 (+877.45) · Apr 7,617.74 → 7,760.99 (+143.25) · May 34,799.69 → 35,144.69 (+345.00) · Jun 1,846.78 → **1,951.78** (+105.00 — the razor month improves) · Jul 6,428.19 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 53,031.65 → 52,756.65 (−275.00 — the bank SPENDS ₹275.00 of headroom, leaving ₹2,756.65)**. Ex-top-3 **₹63,577.47 → ₹64,874.48 (improvement** — IRCTC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,297.01; all ten green with razors Aug 309.08 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000 at ₹52,756.65; ex-top-3 improves; anchors clean). **Book law added: F4 takes no IRCTC SHORT signals** (future cycles anchoring F4 on the SAT-10 dump must apply it). **Saturation: no_beat_cycles stays 0, best_total → ₹189,963.97 — the run is NOT saturated.**
- **Next:** saturation continues from +₹189,963.97 (₹18,996/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (8 qualifying remain at this derivation — re-derive before use; next rows: INV-LONG × INDUSTOWER −₹1,189.01, N4-V3 × OIL × LONG −₹862.04 — the only August-negative row in the top set, Aug −₹405.20, whose removal would thicken the razor to ~₹714.28 — F4 × HINDALCO × LONG −₹851.10); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-23 — INV-LONG component excludes INDUSTOWER (stock × mechanism exclusion; INV-LONG is LONG-only, so the slice is the component's whole INDUSTOWER population; all other components trade INDUSTOWER unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat23_diag.py):** registry re-derived from scratch at the post-SAT-22 book (142 slices, 8 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,756.65 headroom). Anchor A exact (757 tr / +₹189,963.97 / month table to the paisa / ex-top-3 ₹64,874.48; components INV-LONG 191 / N4-V3 49 / P2F 32 / F4 452 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-22 registry record to the paisa** (12 tr / −₹1,189.01 / 3 w; Apr −₹512.09; Oct −₹228.45) — SAT-22 intervened only on an F4 IRCTC-SHORT leg, disjoint from INV-LONG, so the deltas did not expire (Lesson 16 invariance, ninth positive instance).
- **The frozen slice — INV-LONG × INDUSTOWER × LONG, the exact 12 trades to be deleted:** 2026-01-14 +₹504.69 · 2026-01-23 −₹250.87 · 2026-02-09 −₹266.20 · 2026-02-09 −₹266.00 · 2026-03-17 −₹257.35 · 2026-04-06 −₹254.72 · 2026-04-08 −₹257.37 · 2026-05-13 +₹469.13 · 2026-05-14 +₹130.00 · 2026-05-18 −₹257.10 · 2026-05-20 −₹254.77 · 2026-10-13 −₹228.45. **Sum −₹1,189.01, 3 winners of 12.**
- **Month profile of the slice:** Jan +₹253.82 · Feb −₹532.20 · Mar −₹257.35 · **Apr −₹512.09 (thin-month leg)** · May +₹87.26 · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct −₹228.45 (negative — removal MINTS ₹228.45 of headroom, per the SAT-18 corollary)** · Jun/Jul/Sep exactly 0.00. Negative in a thin month AND full-period — the Lesson 5 shape; full −₹1,189.01 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Mechanism scope (Lesson 11): INDUSTOWER earns in F4 (+₹2,287.14 — its kept SHORT flow; F4's own LONG half was already excluded in SAT-2) and N4-V3 (+₹564.20), and loses only small in P2F (−₹240.20) and P2F-R2 (−₹243.07) — both below the bar, different mechanisms, untouched (SAT-20 sharpening: each mechanism's slice qualifies on its own numbers). The exclusion is INV-LONG-scoped. Note the cross-mechanism pattern: INDUSTOWER LONG flow has now failed inside two mechanisms (F4 SAT-2, INV-LONG here) while its F4 SHORT flow earns — recorded as context, not as a book-wide rule.
- **Definition (verbatim):** the INV-LONG component (below-trend pool, T125/S050) does NOT take INDUSTOWER signals (all other components trade INDUSTOWER unchanged — mechanism-scoped per Lesson 11). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 excl. SAT-1..SAT-8 direction slices + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹189,963.97 → ₹191,152.98; trades 757 → 745; October ₹52,756.65 → ₹52,985.10 (headroom ₹2,985.10 — minted ₹228.45); April ₹7,760.99 → ₹8,273.08; August UNCHANGED ₹309.08 (still the razor); June UNCHANGED ₹1,951.78; ex-top-3 ₹64,874.48 → ₹66,063.49 (improvement — INDUSTOWER is not a top-3 name). Small costs on removal: January −₹253.82 and May −₹87.26 (both stay strongly green).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (757 tr / +₹189,963.97 / month table / ex-top-3 ₹64,874.48), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 12-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹189,963.97; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹64,874.48; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; INV-LONG's INDUSTOWER exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat23_score.py; Anchor B: deleted set == the frozen 12 trades exactly, net −₹1,189.01):** 745 tr / **+₹191,152.98**. Month table: Jan 27,847.72 → 27,593.90 (−253.82) · Feb 18,448.01 → 18,980.21 (+532.20) · Mar 21,273.31 → 21,530.66 (+257.35) · Apr 7,760.99 → **8,273.08** (+512.09) · May 35,144.69 → 35,057.43 (−87.26) · Jun 1,951.78 (unchanged) · Jul 6,428.19 (unchanged) · **Aug 309.08 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 (unchanged) · **Oct 52,756.65 → 52,985.10 (+228.45 — the bank MINTS ₹228.45 of headroom, leaving ₹2,985.10)**. Ex-top-3 **₹64,874.48 → ₹66,063.49 (improvement** — INDUSTOWER is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹1,189.01; all ten green with razors Aug 309.08 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000 at ₹52,985.10; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no INDUSTOWER signals** (future cycles anchoring INV-LONG must apply BDL + VEDL + HINDZINC + INDUSTOWER). **Saturation: no_beat_cycles stays 0, best_total → ₹191,152.98 — the run is NOT saturated.**
- **Next:** saturation continues from +₹191,152.98 (₹19,115/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (7 qualifying remain at this derivation — re-derive before use; next rows: N4-V3 × OIL × LONG −₹862.04 — the only August-negative row, Aug −₹405.20, whose removal would thicken the razor to ₹714.28; F4 × HINDALCO × LONG −₹851.10; F4 × TATASTEEL × LONG −₹775.38); (ii) August remains the razor at +₹309.08; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-24 — N4-V3 component excludes OIL LONG signals (stock × mechanism × DIRECTION exclusion; N4-V3's OIL population is LONG-only in-window — no OIL SHORT trades exist in the component — and all other components trade OIL unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat24_diag.py):** registry re-derived from scratch at the post-SAT-23 book (141 slices, 7 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10 headroom). Anchor A exact (745 tr / +₹191,152.98 / month table to the paisa / ex-top-3 ₹66,063.49; components INV-LONG 179 / N4-V3 49 / P2F 32 / F4 452 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG exclusion; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-23 registry record to the paisa** (2 tr / −₹862.04 / 0 w; May −₹456.84; Aug −₹405.20; Oct exactly ₹0.00) — SAT-23 intervened only on an INV-LONG INDUSTOWER leg, disjoint from N4-V3, so the deltas did not expire (Lesson 16 invariance, tenth positive instance). This is the registry's only August-negative row in the top set.
- **The frozen slice — N4-V3 × OIL × LONG, the exact 2 trades to be deleted:** 2026-05-14 −₹456.84 · 2026-08-10 −₹405.20. **Sum −₹862.04, 0 winners of 2.**
- **Month profile of the slice:** May −₹456.84 · **Aug −₹405.20 (thin-month leg — the ONLY August-negative row; removal THICKENS the razor 309.08 → 714.28)** · **Oct exactly ₹0.00 (no October trades — headroom untouched at ₹2,985.10)** · all other months exactly 0.00. Negative in a thin month AND full-period — the Lesson 5 shape; full −₹862.04 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). **Thin-sample caveat, disclosed first-class: 2 trades (the SAT-14/SAT-17/SAT-21 precedent class)** — no population claim; the case rests on the Lesson 5/15 shape at minimum surgery plus the August-thickening arithmetic. Mechanism × direction scope (Lessons 11/15): OIL earns in F4 (+₹491.75 — its kept LONG flow; F4's OIL SHORT half was already excluded in SAT-18) and INV-LONG (+₹1,208.06); its P2F (−₹302.00) and P2F-R2 (−₹299.90) slices are below the bar, different mechanisms, untouched (SAT-20 sharpening). N4-V3 has no OIL SHORT trades in-window, so the direction split inside N4 is vacuous — the exclusion is recorded as N4 × OIL × LONG per the unit of exclusion. OIL has now failed as LONG inside N4-V3 and as SHORT inside F4 while earning as LONG inside F4/INV-LONG — recorded as context, never a book-wide rule.
- **Definition (verbatim):** the N4-V3 component (results/news reaction day, trigger ≥1% by 09:30, entry 09:35, exits T150/S080) does NOT take OIL LONG signals (all other components trade OIL unchanged — mechanism × direction-scoped per Lessons 11/15). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 excl. SAT-1..SAT-8 direction slices + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹191,152.98 → ₹192,015.02; trades 745 → 743; **August ₹309.08 → ₹714.28 (the razor thickened 2.3×)**; May ₹35,057.43 → ₹35,514.27; October UNCHANGED ₹52,985.10 (headroom ₹2,985.10); June UNCHANGED ₹1,951.78; ex-top-3 ₹66,063.49 → ₹66,925.53 (improvement — OIL is not a top-3 name). No month pays any cost on removal (the slice is zero outside May/August).
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (745 tr / +₹191,152.98 / month table / ex-top-3 ₹66,063.49), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 2-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹191,152.98; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹66,063.49; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; N4-V3's OIL-LONG exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat24_score.py; Anchor B: deleted set == the frozen 2 trades exactly, net −₹862.04):** 743 tr / **+₹192,015.02**. Month table: Jan 27,593.90 (unchanged) · Feb 18,980.21 (unchanged) · Mar 21,530.66 (unchanged) · Apr 8,273.08 (unchanged) · May 35,057.43 → **35,514.27** (+456.84) · Jun 1,951.78 (unchanged) · Jul 6,428.19 (unchanged) · **Aug 309.08 → 714.28 (+405.20 — THE RAZOR THICKENED 2.3×; August remains the minimum month but is no longer a whisker)** · Sep 18,043.55 (unchanged) · **Oct 52,985.10 (unchanged — headroom ₹2,985.10 untouched; the slice had no October trades)**. Ex-top-3 **₹66,063.49 → ₹66,925.53 (improvement** — OIL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹862.04; all ten green with razors Aug 714.28 / Jun 1,951.78 / Jul 6,428.19 all ≥ ₹100 and the minimum month now August +714.28; October ≥ 50,000 at ₹52,985.10; ex-top-3 improves; anchors clean). **Book law added: N4-V3 takes no OIL LONG signals** (future cycles anchoring N4 must apply ASTRAL + TVSMOTOR-LONG + OIL-LONG exclusions to the SAT-15 dump). **Saturation: no_beat_cycles stays 0, best_total → ₹192,015.02 — the run is NOT saturated.**
- **Next:** saturation continues from +₹192,015.02 (₹19,202/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (6 qualifying remain at this derivation — re-derive before use; next rows: F4 × HINDALCO × LONG −₹851.10; F4 × TATASTEEL × LONG −₹775.38; F4 × NHPC × SHORT −₹769.23; INV-LONG × KALYANKJIL −₹764.57; August-negative slices remain lower in the queue: F4 × PFC × SHORT Aug −₹55.00, F4 × RECLTD × SHORT Aug −₹342.58); (ii) August is thickened to +₹714.28 but remains the thinnest month; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-25 — F4 component excludes HINDALCO LONG signals (stock × mechanism × DIRECTION exclusion; all other components trade HINDALCO unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat25_diag.py):** registry re-derived from scratch at the post-SAT-24 book (140 slices, 6 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10 headroom). Anchor A exact (743 tr / +₹192,015.02 / month table to the paisa / ex-top-3 ₹66,925.53; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 452 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-24 registry record to the paisa** (9 tr / −₹851.10 / 3 w; Apr −₹215.00, Jun −₹1,137.25 thin-month legs; Oct exactly ₹0.00) — SAT-24 intervened only on an N4-V3 OIL-LONG leg, disjoint from F4, so the deltas did not expire (Lesson 16 invariance, eleventh positive instance).
- **The frozen slice — F4 × HINDALCO × LONG, the exact 9 trades to be deleted:** 2026-01-13 +₹680.00 · 2026-01-23 −₹951.81 · 2026-02-20 +₹1,331.97 · 2026-02-25 −₹200.00 · 2026-03-06 −₹385.00 · 2026-04-27 −₹215.00 · 2026-05-14 +₹1,010.00 · 2026-06-02 −₹1,137.25 · 2026-09-18 −₹984.01. **Sum −₹851.10, 3 winners of 9.**
- **Month profile of the slice:** Jan −₹271.81 · Feb +₹1,131.97 · Mar −₹385.00 · **Apr −₹215.00 (thin-month leg)** · May +₹1,010.00 · **Jun −₹1,137.25 (thin-month leg)** · Sep −₹984.01 · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct exactly ₹0.00 (no October trades — headroom untouched at ₹2,985.10)** · Jul exactly 0.00. Negative in two thin months AND full-period — the Lesson 5 shape; full −₹851.10 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × HINDALCO × SHORT earns +₹2,345.84 (8 tr) and stays; the LONG half is the rot. Mechanism scope (Lesson 11): HINDALCO also loses inside INV-LONG (−₹895.40) and N4-V3 (−₹907.36) and earns in P2F-R2 (+₹1,276.75), and P2F's HINDALCO-LONG population was already excluded in SAT-14 — but only the F4 slice independently clears this cycle's bar (full ≤ −₹500 AND thin-month-negative AND October-feasible), so the exclusion is F4 × LONG-scoped and every other mechanism keeps its HINDALCO trades (SAT-20 sharpening, applied again).
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take LONG signals on HINDALCO (F4 keeps HINDALCO SHORT; all other components trade HINDALCO unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹192,015.02 → ₹192,866.12; trades 743 → 734; October UNCHANGED ₹52,985.10 (headroom ₹2,985.10); August UNCHANGED ₹714.28 (still the thinnest month, untouched); June ₹1,951.78 → ₹3,089.03 (+1,137.25 — a razor month thickens); April ₹8,273.08 → ₹8,488.08; September ₹18,043.55 → ₹19,027.56; ex-top-3 ₹66,925.53 → ₹67,776.63 (improvement — HINDALCO is not a top-3 name). Costs on removal: February −₹1,131.97 (→ ₹17,848.24) and May −₹1,010.00 (→ ₹34,504.27) — both stay strongly green.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (743 tr / +₹192,015.02 / month table / ex-top-3 ₹66,925.53), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 9-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹192,015.02; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹66,925.53; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's HINDALCO-LONG exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat25_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹851.10):** 734 tr / **+₹192,866.12**. Month table: Jan 27,593.90 → 27,865.71 (+271.81) · Feb 18,980.21 → 17,848.24 (−1,131.97) · Mar 21,530.66 → 21,915.66 (+385.00) · Apr 8,273.08 → **8,488.08** (+215.00) · May 35,514.27 → 34,504.27 (−1,010.00) · Jun 1,951.78 → **3,089.03** (+1,137.25 — a razor month thickens 1.6×) · Jul 6,428.19 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 18,043.55 → 19,027.56 (+984.01) · **Oct 52,985.10 (unchanged — the slice had no October trades; headroom ₹2,985.10 untouched)**. Ex-top-3 **₹66,925.53 → ₹67,776.63 (improvement** — HINDALCO is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹851.10; all ten green with razors Aug 714.28 / Jun 3,089.03 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000 at ₹52,985.10; ex-top-3 improves; anchors clean). **Book law added: F4 takes no HINDALCO LONG signals** (future cycles anchoring F4 on the SAT-10 dump must apply it; F4 keeps HINDALCO SHORT). **Saturation: no_beat_cycles stays 0, best_total → ₹192,866.12 — the run is NOT saturated.**
- **Next:** saturation continues from +₹192,866.12 (₹19,287/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (5 qualifying remain at this derivation — re-derive before use; next rows: F4 × TATASTEEL × LONG −₹775.38, F4 × NHPC × SHORT −₹769.23, INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — its removal would thicken the August razor to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-26 — F4 component excludes TATASTEEL LONG signals (stock × mechanism × DIRECTION exclusion; all other components trade TATASTEEL unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat26_diag.py):** registry re-derived from scratch at the post-SAT-25 book (139 slices, 5 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹2,985.10 headroom). Anchor A exact (734 tr / +₹192,866.12 / month table to the paisa / ex-top-3 ₹67,776.63; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 443 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-25 registry record to the paisa** (9 tr / −₹775.38 / 2 w; Apr −₹245.92, Jun −₹263.64 thin-month legs; Oct −₹57.00) — SAT-25 intervened only on an F4 HINDALCO-LONG leg, disjoint from TATASTEEL, so the deltas did not expire (Lesson 16 invariance, twelfth positive instance). The full queue re-measured identical to the SAT-25 record (NHPC-SHORT −₹769.23, KALYANKJIL −₹764.57, PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97).
- **The frozen slice — F4 × TATASTEEL × LONG, the exact 9 trades to be deleted:** 2026-01-14 +₹239.49 · 2026-01-23 −₹221.16 · 2026-02-20 +₹164.00 · 2026-04-28 −₹245.92 · 2026-06-02 −₹29.00 · 2026-06-08 −₹234.64 · 2026-09-18 −₹171.00 · 2026-09-25 −₹220.15 · 2026-10-09 −₹57.00. **Sum −₹775.38, 2 winners of 9.**
- **Month profile of the slice:** Jan +₹18.33 · Feb +₹164.00 · **Apr −₹245.92 (thin-month leg)** · **Jun −₹263.64 (thin-month leg)** · Sep −₹391.15 · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct −₹57.00 (negative — removal MINTS ₹57.00 of headroom, per the SAT-18 corollary)** · Mar/May/Jul exactly 0.00. Negative in two thin months AND full-period — the Lesson 5 shape; full −₹775.38 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × TATASTEEL × SHORT earns +₹646.21 (9 tr) and stays; the LONG half is the rot. Mechanism scope (Lesson 11): TATASTEEL's slices in the other components are all below the bar (INV-LONG −₹217.04, N4-V3 +₹73.08, P2F −₹145.29, P2F-R2 +₹219.38) and stay untouched (SAT-20 sharpening — each mechanism's slice qualifies on its own numbers); the exclusion is F4 × LONG-scoped.
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take LONG signals on TATASTEEL (F4 keeps TATASTEEL SHORT; all other components trade TATASTEEL unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹192,866.12 → ₹193,641.50; trades 734 → 725; October ₹52,985.10 → ₹53,042.10 (headroom ₹3,042.10 — minted ₹57.00); August UNCHANGED ₹714.28 (still the thinnest month, untouched); June ₹3,089.03 → ₹3,352.67 (+263.64); April ₹8,488.08 → ₹8,734.00; September ₹19,027.56 → ₹19,418.71; ex-top-3 ₹67,776.63 → ₹68,552.01 (improvement — TATASTEEL is not a top-3 name). Costs on removal: January −₹18.33 (→ ₹27,847.38) and February −₹164.00 (→ ₹17,684.24) — both stay strongly green.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (734 tr / +₹192,866.12 / month table / ex-top-3 ₹67,776.63), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 9-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹192,866.12; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹67,776.63; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's TATASTEEL-LONG exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat26_score.py; Anchor B: deleted set == the frozen 9 trades exactly, net −₹775.38):** 725 tr / **+₹193,641.50**. Month table: Jan 27,865.71 → 27,847.38 (−18.33) · Feb 17,848.24 → 17,684.24 (−164.00) · Mar 21,915.66 (unchanged) · Apr 8,488.08 → **8,734.00** (+245.92) · May 34,504.27 (unchanged) · Jun 3,089.03 → **3,352.67** (+263.64) · Jul 6,428.19 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,027.56 → 19,418.71 (+391.15) · **Oct 52,985.10 → 53,042.10 (+57.00 — the bank MINTS ₹57.00 of headroom, leaving ₹3,042.10)**. Ex-top-3 **₹67,776.63 → ₹68,552.01 (improvement** — TATASTEEL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹775.38; all ten green with razors Aug 714.28 / Jun 3,352.67 / Jul 6,428.19 all ≥ ₹100; October ≥ 50,000 at ₹53,042.10; ex-top-3 improves; anchors clean). **Book law added: F4 takes no TATASTEEL LONG signals** (future cycles anchoring F4 on the SAT-10 dump must apply it; F4 keeps TATASTEEL SHORT). **Saturation: no_beat_cycles stays 0, best_total → ₹193,641.50 — the run is NOT saturated.**
- **Next:** saturation continues from +₹193,641.50 (₹19,364/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (4 qualifying remain at this derivation — re-derive before use; next rows: F4 × NHPC × SHORT −₹769.23, INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — its removal would thicken the August razor to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-27 — F4 component excludes NHPC SHORT signals (stock × mechanism × DIRECTION exclusion; all other components trade NHPC unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat27_diag.py):** registry re-derived from scratch at the post-SAT-26 book (138 slices, 4 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,042.10 headroom). Anchor A exact (725 tr / +₹193,641.50 / month table to the paisa / ex-top-3 ₹68,552.01; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 434 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-26 registry record to the paisa** (13 tr / −₹769.23 / 2 w) — and the full remaining queue re-measured identical with it (KALYANKJIL −₹764.57, PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97). SAT-26 intervened only on an F4 TATASTEEL-LONG leg, disjoint from NHPC — the deltas did not expire (Lesson 16 invariance, thirteenth positive instance).
- **The frozen slice — F4 × NHPC × SHORT, the exact 13 trades to be deleted:** 2026-01-21 −₹112.38 · 2026-02-03 −₹114.02 · 2026-02-09 −₹33.00 · 2026-02-18 −₹46.00 · 2026-02-27 −₹25.00 · 2026-03-27 −₹15.00 · 2026-04-09 −₹46.00 · 2026-04-24 +₹8.00 · 2026-04-30 −₹118.36 · 2026-07-27 −₹115.24 · 2026-09-01 −₹111.85 · 2026-10-07 −₹108.80 · 2026-10-08 +₹68.42. **Sum −₹769.23, 2 winners of 13.**
- **Month profile of the slice:** Jan −₹112.38 · Feb −₹218.02 · Mar −₹15.00 · **Apr −₹156.36 (thin-month leg)** · **Jul −₹115.24 (thin-month leg)** · Sep −₹111.85 · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct −₹40.38 (negative — removal MINTS ₹40.38 of headroom, per the SAT-18 corollary)** · May/Jun exactly 0.00. Negative in two thin months AND full-period — the Lesson 5 shape; full −₹769.23 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × NHPC × LONG is mildly negative but below the bar (12 tr / −₹102.46) and stays untouched (SAT-20 sharpening — each mechanism × direction slice qualifies on its own numbers). Mechanism scope (Lesson 11): NHPC's slices in the other components stay untouched (INV-LONG +₹124.24, N4-V3 −₹104.80 — both below the bar); the exclusion is F4 × SHORT-scoped.
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take SHORT signals on NHPC (F4 keeps NHPC LONG; all other components trade NHPC unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹193,641.50 → ₹194,410.73; trades 725 → 712; October ₹53,042.10 → ₹53,082.48 (headroom ₹3,082.48 — minted ₹40.38); August UNCHANGED ₹714.28 (still the thinnest month, untouched); April ₹8,734.00 → ₹8,890.36; July ₹6,428.19 → ₹6,543.43; September ₹19,418.71 → ₹19,530.56; June UNCHANGED ₹3,352.67; ex-top-3 ₹68,552.01 → ₹69,321.24 (improvement — NHPC is not a top-3 name). No month pays a cost on removal — every affected month improves.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (725 tr / +₹193,641.50 / month table / ex-top-3 ₹68,552.01), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 13-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹193,641.50; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹68,552.01; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's NHPC-SHORT exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat27_score.py; Anchor B: deleted set == the frozen 13 trades exactly, net −₹769.23):** 712 tr / **+₹194,410.73**. Month table: Jan 27,847.38 → 27,959.76 (+112.38) · Feb 17,684.24 → 17,902.26 (+218.02) · Mar 21,915.66 → 21,930.66 (+15.00) · Apr 8,734.00 → **8,890.36** (+156.36) · May 34,504.27 (unchanged) · Jun 3,352.67 (unchanged) · Jul 6,428.19 → **6,543.43** (+115.24) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,418.71 → 19,530.56 (+111.85) · **Oct 53,042.10 → 53,082.48 (+40.38 — the bank MINTS ₹40.38 of headroom, leaving ₹3,082.48)**. No month pays a cost on removal — every affected month improves. Ex-top-3 **₹68,552.01 → ₹69,321.24 (improvement** — NHPC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹769.23; all ten green with razors Aug 714.28 / Jun 3,352.67 / Jul 6,543.43 all ≥ ₹100; October ≥ 50,000 at ₹53,082.48; ex-top-3 improves; anchors clean). **Book law added: F4 takes no NHPC SHORT signals** (future cycles anchoring F4 on the SAT-10 dump must apply it; F4 keeps NHPC LONG). **Saturation: no_beat_cycles stays 0, best_total → ₹194,410.73 — the run is NOT saturated.**
- **Next:** saturation continues from +₹194,410.73 (₹19,441/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (3 qualifying remain at this derivation — re-derive before use; next rows: INV-LONG × KALYANKJIL −₹764.57, F4 × PFC × SHORT −₹667.69 (Aug −₹55.00), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — its removal would thicken the August razor to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-28 — INV-LONG component excludes KALYANKJIL signals (stock × mechanism exclusion; INV-LONG is LONG-only, so no direction split exists inside it; all other components trade KALYANKJIL unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat28_diag.py):** registry re-derived from scratch at the post-SAT-27 book (137 slices, 3 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,082.48 headroom). Anchor A exact (712 tr / +₹194,410.73 / month table to the paisa / ex-top-3 ₹69,321.24; components INV-LONG 179 / N4-V3 47 / P2F 32 / F4 421 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-27 registry record to the paisa** (24 tr / −₹764.57 / 7 w) — and the full remaining queue re-measured identical with it (PFC-SHORT −₹667.69, RECLTD-SHORT −₹503.97). SAT-27 intervened only on an F4 NHPC-SHORT leg, disjoint from all three queue rows — the deltas did not expire (Lesson 16 invariance, fourteenth positive instance).
- **The frozen slice — INV-LONG × KALYANKJIL × LONG, the exact 24 trades to be deleted:** 2026-01-20 −₹271.00 · 2026-01-28 −₹228.02 · 2026-01-30 −₹222.65 · 2026-01-30 −₹222.70 · 2026-02-09 −₹251.12 · 2026-02-09 −₹250.05 · 2026-02-17 −₹253.05 · 2026-03-25 +₹439.50 · 2026-03-25 +₹445.75 · 2026-03-30 −₹232.60 · 2026-04-06 +₹476.44 · 2026-04-13 −₹262.70 · 2026-06-05 −₹223.65 · 2026-06-15 +₹411.56 · 2026-06-15 −₹222.93 · 2026-09-03 −₹338.32 · 2026-09-03 −₹337.60 · 2026-09-08 +₹707.44 · 2026-09-10 +₹724.75 · 2026-09-15 −₹347.02 · 2026-10-06 −₹329.65 · 2026-10-07 +₹666.50 · 2026-10-13 −₹323.15 · 2026-10-16 −₹320.30. **Sum −₹764.57, 7 winners of 24.**
- **Month profile of the slice:** Jan −₹944.37 · Feb −₹754.22 · Mar +₹652.65 · Apr +₹213.74 · **Jun −₹35.02 (thin-month leg)** · Sep +₹409.25 · **Aug exactly ₹0.00 (no August trades — the razor is untouched)** · **Oct −₹306.60 (negative — removal MINTS ₹306.60 of headroom, per the SAT-18 corollary)** · May/Jul exactly 0.00. Negative in a thin month AND full-period — the Lesson 5 shape; full −₹764.57 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Mechanism scope (Lesson 11): KALYANKJIL earns in N4-V3 (+₹1,972.87) and F4 (+₹497.38) and stays there; its P2F (−₹152.75) and P2F-R2 (−₹201.70) slices are below the bar and stay untouched (SAT-20 sharpening — each mechanism's slice qualifies on its own numbers); the exclusion is INV-LONG-scoped. INV-LONG is LONG-only, so there is no direction split to take inside it (SAT-19 precedent).
- **Definition (verbatim):** the INV-LONG component (below-trend pool, LONG-only, T125/S050) does NOT take signals on KALYANKJIL (all other components trade KALYANKJIL unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹194,410.73 → ₹195,175.30; trades 712 → 688; October ₹53,082.48 → ₹53,389.08 (headroom ₹3,389.08 — minted ₹306.60); August UNCHANGED ₹714.28 (still the thinnest month, untouched); June ₹3,352.67 → ₹3,387.69; January ₹27,959.76 → ₹28,904.13; February ₹17,902.26 → ₹18,656.48; ex-top-3 ₹69,321.24 → ₹70,085.81 (improvement — KALYANKJIL is not a top-3 name). Costs on removal: March −₹652.65 (→ ₹21,278.01), April −₹213.74 (→ ₹8,676.62) and September −₹409.25 (→ ₹19,121.31) — all stay strongly green.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (712 tr / +₹194,410.73 / month table / ex-top-3 ₹69,321.24), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 24-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹194,410.73; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹69,321.24; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; INV-LONG's KALYANKJIL exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat28_score.py; Anchor B: deleted set == the frozen 24 trades exactly, net −₹764.57):** 688 tr / **+₹195,175.30**. Month table: Jan 27,959.76 → 28,904.13 (+944.37) · Feb 17,902.26 → 18,656.48 (+754.22) · Mar 21,930.66 → 21,278.01 (−652.65) · Apr 8,890.36 → 8,676.62 (−213.74) · May 34,504.27 (unchanged) · Jun 3,352.67 → **3,387.69** (+35.02) · Jul 6,543.43 (unchanged) · **Aug 714.28 (unchanged — the razor intact; the slice had no August trades)** · Sep 19,530.56 → 19,121.31 (−409.25) · **Oct 53,082.48 → 53,389.08 (+306.60 — the bank MINTS ₹306.60 of headroom, leaving ₹3,389.08)**. Ex-top-3 **₹69,321.24 → ₹70,085.81 (improvement** — KALYANKJIL is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹764.57; all ten green with razors Aug 714.28 / Jun 3,387.69 / Jul 6,543.43 all ≥ ₹100; October ≥ 50,000 at ₹53,389.08; ex-top-3 improves; anchors clean). **Book law added: INV-LONG takes no KALYANKJIL signals** (future cycles anchoring INV-LONG must apply it; all other components trade KALYANKJIL unchanged). **Saturation: no_beat_cycles stays 0, best_total → ₹195,175.30 — the run is NOT saturated.**
- **Next:** saturation continues from +₹195,175.30 (₹19,518/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (2 qualifying remain at this derivation — re-derive before use; next rows: F4 × PFC × SHORT −₹667.69 (Aug −₹55.00 — its removal would thicken the August razor to ~₹769.28), F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — removal would thicken August to ~₹1,057.25)); (ii) August remains the thinnest month at +₹714.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-29 — F4 component excludes PFC SHORT signals (stock × mechanism × DIRECTION exclusion; F4 keeps PFC LONG; all other components trade PFC unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat29_diag.py):** registry re-derived from scratch at the post-SAT-28 book (136 slices, 2 qualifying at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,389.08 headroom). Anchor A exact (688 tr / +₹195,175.30 / month table to the paisa / ex-top-3 ₹70,085.81; components INV-LONG 155 / N4-V3 47 / P2F 32 / F4 421 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER + SAT-28 KALYANKJIL; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The top qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-28 registry record to the paisa** (18 tr / −₹667.69 / 8 w) — and the other qualifying row re-measured identical with it (RECLTD-SHORT −₹503.97). SAT-28 intervened only on an INV-LONG KALYANKJIL leg, disjoint from both F4 rows — the deltas did not expire (Lesson 16 invariance, fifteenth positive instance).
- **The frozen slice — F4 × PFC × SHORT, the exact 18 trades to be deleted:** 2026-01-20 +₹510.27 · 2026-02-03 −₹408.08 · 2026-02-26 +₹180.00 · 2026-02-27 +₹265.00 · 2026-03-04 −₹185.00 · 2026-03-19 +₹590.53 · 2026-03-24 −₹419.10 · 2026-03-27 −₹416.01 · 2026-03-30 +₹542.22 · 2026-04-08 −₹434.92 · 2026-04-10 −₹447.60 · 2026-06-11 −₹435.53 · 2026-08-27 −₹55.00 · 2026-09-15 +₹325.00 · 2026-09-29 −₹347.18 · 2026-10-05 −₹342.29 · 2026-10-23 +₹175.00 · 2026-10-30 +₹235.00. **Sum −₹667.69, 8 winners of 18.**
- **Month profile of the slice:** Jan +₹510.27 · Feb +₹36.92 · Mar +₹112.64 · **Apr −₹882.52 (thin-month leg)** · **Jun −₹435.53 (thin-month leg)** · **Aug −₹55.00 (thin-month leg — removal thickens the August razor to ₹769.28)** · Sep −₹22.18 · **Oct +₹67.71 (positive — removal SPENDS ₹67.71 of headroom, per the SAT-22 mirror note; inside headroom ₹3,389.08)** · May/Jul exactly 0.00. Negative in three thin months AND full-period — the Lesson 5 shape; full −₹667.69 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × PFC × LONG earns +₹1,652.90 (12 tr) and stays untouched. Mechanism scope (Lesson 11): PFC's slices in the other components stay untouched (INV-LONG +₹2,117.27, P2F +₹442.50, P2F-R2 +₹436.25 earn; N4-V3 −₹197.58 below the bar); the exclusion is F4 × SHORT-scoped.
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take SHORT signals on PFC (F4 keeps PFC LONG; all other components trade PFC unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER + KALYANKJIL; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹195,175.30 → ₹195,842.99; trades 688 → 670; October ₹53,389.08 → ₹53,321.37 (headroom ₹3,321.37 — spends ₹67.71); August ₹714.28 → ₹769.28 (razor thickened); April ₹8,676.62 → ₹9,559.14; June ₹3,387.69 → ₹3,823.22; September ₹19,121.31 → ₹19,143.49; ex-top-3 ₹70,085.81 → ₹70,753.50 (improvement — PFC is not a top-3 name). Costs on removal: January −₹510.27 (→ ₹28,393.86), February −₹36.92 (→ ₹18,619.56), March −₹112.64 (→ ₹21,165.37) — all stay strongly green.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (688 tr / +₹195,175.30 / month table / ex-top-3 ₹70,085.81), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 18-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹195,175.30; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹70,085.81; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's PFC-SHORT exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat29_score.py; Anchor B: deleted set == the frozen 18 trades exactly, net −₹667.69):** 670 tr / **+₹195,842.99**. Month table: Jan 28,904.13 → 28,393.86 (−510.27) · Feb 18,656.48 → 18,619.56 (−36.92) · Mar 21,278.01 → 21,165.37 (−112.64) · Apr 8,676.62 → **9,559.14** (+882.52) · May 34,504.27 (unchanged) · Jun 3,387.69 → **3,823.22** (+435.53) · Jul 6,543.43 (unchanged) · **Aug 714.28 → 769.28 (+55.00 — the razor THICKENED; the slice's August leg was negative)** · Sep 19,121.31 → 19,143.49 (+22.18) · **Oct 53,389.08 → 53,321.37 (−67.71 — the bank SPENDS ₹67.71 of headroom, leaving ₹3,321.37)**. Costs on removal (Jan −510.27, Feb −36.92, Mar −112.64) all stay strongly green. Ex-top-3 **₹70,085.81 → ₹70,753.50 (improvement** — PFC is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹667.69; all ten green with razors Aug 769.28 / Jun 3,823.22 / Jul 6,543.43 all ≥ ₹100; October ≥ 50,000 at ₹53,321.37; ex-top-3 improves; anchors clean). **Book law added: F4 takes no PFC SHORT signals** (future cycles anchoring F4 on the SAT-10 dump must apply it; F4 keeps PFC LONG). **Saturation: no_beat_cycles stays 0, best_total → ₹195,842.99 — the run is NOT saturated.**
- **Next:** saturation continues from +₹195,842.99 (₹19,584/month vs the ₹75,000/month goal — the gap is stated plainly). Frontiers: (i) the registry queue (1 qualifying remains at this derivation — re-derive before use: F4 × RECLTD × SHORT −₹503.97 (Aug −₹342.58 — its removal would thicken the August razor to ~₹1,111.86; Oct +₹477.00)); (ii) August remains the thinnest month at +₹769.28; (iii) the GLENMARK-SHORT argument (explicit argument required); (iv) genuinely new Lesson-3 material beyond the reaction-lag axis (fully mapped).

## SAT-30 — F4 component excludes RECLTD SHORT signals (stock × mechanism × DIRECTION exclusion; F4 keeps RECLTD LONG; all other components trade RECLTD unchanged): FROZEN FOR SCORING (2026-10-31)

- **Diagnosis (stocks_engine_sat30_diag.py):** registry re-derived from scratch at the post-SAT-29 book (135 slices, **1 qualifying** at this cycle's bar: full-period ≤ −₹500 AND negative in ≥1 thin month Apr/Jun/Jul/Aug AND October slice ≤ ₹3,321.37 headroom). Anchor A exact (670 tr / +₹195,842.99 / month table to the paisa / ex-top-3 ₹70,753.50; components INV-LONG 155 / N4-V3 47 / P2F 32 / F4 403 / P2F-R2 33; N4 from the SAT-15 T150/S080 dump minus the SAT-17 TVSMOTOR-LONG + SAT-24 OIL-LONG exclusions; F4 minus SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT + SAT-29 PFC-SHORT; INV-LONG minus BDL + SAT-19 VEDL + SAT-20 HINDZINC + SAT-23 INDUSTOWER + SAT-28 KALYANKJIL; P2F-R2 minus the SAT-21 TVSMOTOR-LONG exclusion). The sole qualifying row, re-measured trade-by-trade, is **IDENTICAL to the SAT-29 registry record to the paisa** (14 tr / −₹503.97 / 6 w; Aug −₹342.58; Oct +₹477.00) — SAT-29 intervened only on an F4 PFC-SHORT leg, disjoint from RECLTD-SHORT — the deltas did not expire (Lesson 16 invariance, sixteenth positive instance). The diag also re-derived the registry on the POST-removal book: **0 qualifying rows remain** (headroom re-based to ₹2,844.37) — this is the registry's LAST row; banking it empties the deletion frontier at this bar.
- **The frozen slice — F4 × RECLTD × SHORT, the exact 14 trades to be deleted:** 2026-01-13 +₹235.00 · 2026-01-21 −₹377.39 · 2026-02-27 +₹55.00 · 2026-03-10 −₹351.32 · 2026-03-19 +₹470.00 · 2026-03-20 +₹462.28 · 2026-04-02 −₹336.35 · 2026-05-06 −₹376.59 · 2026-08-27 −₹342.58 · 2026-09-01 −₹100.00 · 2026-09-29 −₹319.02 · 2026-10-21 −₹60.00 · 2026-10-23 +₹145.00 · 2026-10-30 +₹392.00. **Sum −₹503.97, 6 winners of 14.**
- **Month profile of the slice:** Jan −₹142.39 · Feb +₹55.00 · Mar +₹580.96 · **Apr −₹336.35 (thin-month leg)** · May −₹376.59 · **Aug −₹342.58 (thin-month leg — removal thickens the August razor to ₹1,111.86)** · Sep −₹419.02 · **Oct +₹477.00 (positive — removal SPENDS ₹477.00 of headroom, per the SAT-22 mirror note; inside headroom ₹3,321.37)** · Jun/Jul exactly 0.00. Negative in two thin months AND full-period — the Lesson 5 shape; full −₹503.97 clears the quality bar (≤ −₹500; not the GLENMARK near-zero pattern). Direction split (Lesson 15): F4 × RECLTD × LONG earns +₹949.99 (5 tr) and stays untouched. Mechanism scope (Lesson 11): RECLTD's slices in the other components stay untouched (INV-LONG +₹0.24, N4-V3 +₹242.04, P2F +₹228.37 earn small; P2F-R2 −₹438.00 is below the bar); the exclusion is F4 × SHORT-scoped.
- **Definition (verbatim):** the F4 component (state-gated cell, T150/S095, first-signal-only per SAT-6, SAT-10 dump as its trade source) does NOT take SHORT signals on RECLTD (F4 keeps RECLTD LONG; all other components trade RECLTD unchanged). Everything else in the book is frozen verbatim (five components; INV-LONG excl. BDL + VEDL + HINDZINC + INDUSTOWER + KALYANKJIL; N4-V3 at T150/S080 excl. ASTRAL + TVSMOTOR-LONG + OIL-LONG; P2F 2.5% excl. ASTRAL / HINDUNILVR / HINDALCO-LONG; F4 with all SAT-1..SAT-8 exclusions + SAT-18 OIL-SHORT + SAT-22 IRCTC-SHORT + SAT-25 HINDALCO-LONG + SAT-26 TATASTEEL-LONG + SAT-27 NHPC-SHORT + SAT-29 PFC-SHORT; P2F-R2 excl. ASTRAL / HINDUNILVR names + TVSMOTOR-LONG; RF-1 book-wide).
- **Expected arithmetic (to be confirmed by the audited rebuild, not believed before it):** total ₹195,842.99 → ₹196,346.96; trades 670 → 656; October ₹53,321.37 → ₹52,844.37 (headroom ₹2,844.37 — spends ₹477.00); August ₹769.28 → ₹1,111.86 (razor thickened 1.4×); April ₹9,559.14 → ₹9,895.49; May ₹34,504.27 → ₹34,880.86; September ₹19,143.49 → ₹19,562.51; ex-top-3 ₹70,753.50 → ₹71,257.47 (improvement — RECLTD is not a top-3 name). Costs on removal: January −₹142.39 gain is negative — removal ADDS ₹142.39 to January (→ ₹28,536.25); February −₹55.00 (→ ₹18,564.56), March −₹580.96 (→ ₹20,584.41) — both stay strongly green. Post-removal registry: **EMPTY of qualifying rows** — the deletion frontier is exhausted at this bar; future cycles must bring new material or close toward saturation.
- **Anchors (all must hold before the fix is judged):** (A) current-book rebuild == state (670 tr / +₹195,842.99 / month table / ex-top-3 ₹70,753.50), per the book-law construction above; (B) the deleted set extracted at scoring == the frozen 14-trade set above exactly (date, stock, dir, net); (C) the removal is deletion-only on audited component dumps — timing validity is inherited from the components' own audits (no new entries are created).
- **Saturation gate:** bank iff (a) union total > +₹195,842.99; (b) all ten months > 0 AND the razors keep ≥ ₹100 (Aug ≥ 100, Jul ≥ 100, Jun ≥ 100); (c) October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹70,753.50; (e) anchors pass. If banked: no_beat_cycles stays 0, best_total updates; F4's RECLTD-SHORT exclusion is recorded as book law. If any leg fails: do NOT bank, no_beat_cycles 0 → 1.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat30_score.py; Anchor B: deleted set == the frozen 14 trades exactly, net −₹503.97):** 656 tr / **+₹196,346.96**. Month table: Jan 28,393.86 → 28,536.25 (+142.39) · Feb 18,619.56 → 18,564.56 (−55.00) · Mar 21,165.37 → 20,584.41 (−580.96) · Apr 9,559.14 → **9,895.49** (+336.35) · May 34,504.27 → **34,880.86** (+376.59) · Jun 3,823.22 (unchanged) · Jul 6,543.43 (unchanged) · **Aug 769.28 → 1,111.86 (+342.58 — the razor THICKENED 1.4×; the slice's August leg was negative)** · Sep 19,143.49 → 19,562.51 (+419.02) · **Oct 53,321.37 → 52,844.37 (−477.00 — the bank SPENDS ₹477.00 of headroom, leaving ₹2,844.37)**. Costs on removal (Feb −55.00, Mar −580.96) stay strongly green. Ex-top-3 **₹70,753.50 → ₹71,257.47 (improvement** — RECLTD is not a top-3 name; top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: BANKED — all five saturation-gate legs pass** (total rises +₹503.97; all ten green with razors Aug 1,111.86 / Jun 3,823.22 / Jul 6,543.43 all ≥ ₹100; October ≥ 50,000 at ₹52,844.37; ex-top-3 improves; anchors clean). **Book law added: F4 takes no RECLTD SHORT signals** (future cycles anchoring F4 on the SAT-10 dump must apply it; F4 keeps RECLTD LONG). **Saturation: no_beat_cycles stays 0, best_total → ₹196,346.96 — the run is NOT saturated.**
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — the gap is stated plainly). **The deletion registry is EMPTY** (post-removal re-derivation: 134 slices, 0 qualifying at the standing bar) — the deletion frontier is exhausted; remaining frontiers: (i) genuinely new Lesson-3 material (new earning components — the reaction-lag axis is fully mapped: R+1/R+2 real, R+3 noise, below-band dead at every lag); (ii) August remains the thinnest month at +₹1,111.86; (iii) the GLENMARK-SHORT argument (full ≈ −₹137, BELOW the registry bar — explicit argument required, not a routine slice; lowering the bar toward it is the overfit direction and is refused by the standing discipline).

## SAT-31 — NEW COMPONENT F4-UPBAND: F4's joint state on the band's upper complement slice [1.0%, 1.25%) (6th component candidate; new earning material — the deletion registry is EMPTY): FROZEN FOR SCORING (2026-10-31)

- **Charter basis:** the registry is exhausted (SAT-30: 0 qualifying rows), so progress can only come from new Lesson-3 material. Lesson 17's corollary licenses testing a boundary's complement exactly once. F4's band [0.5%, 1.0%) has had its lower complement tested on the reaction axis (SAT-4: below-band carries no follow-through at any lag, Lessons 17/19/20), but the band's UPPER complement under F4's OWN joint state has never been scored. This cycle tests it — once, frozen, placebo-controlled.
- **DISCLOSED PRIOR (stated before scoring, not after):** M2 found the ≥1% region was the UNGATED follow cell's loss driver (64% of the Jan–Sep loss). This test is narrower: whether the JOINT STATE (below-50DMA gate + this slice ONLY, [1.0%, 1.25%) — not the whole ≥1% region, not the ungated cell) rescues it. The prior says probably not; the test is run because the gated slice is a different population from the ungated region, and the answer either buys a new component or validates the band's upper boundary the way Lessons 17/20 validated the others.
- **Definition (verbatim):** F4-UPBAND = on below-50DMA days (Nifty prev close ≤ 50DMA, per H1.below50), for each home-25 stock whose morning move by 10:00 (H1/M premove at T="10:00") satisfies 1.0% ≤ |premove| < 1.25% (disjoint from F4's [0.5%, 1.0%) band by construction), take the FIRST accepted V5 signal at/after 10:00 in the FOLLOW direction (H1.build_cell sig mode, dirmode="follow", first-signal-only per SAT-6 — round2 legs dropped), enter next bar open, exits T150/S095 (the book's current F4 exits), square-off per the audited replay. RF-1 stand-aside (no weekend-session days). The book's F4 mechanism-scoped exclusions apply symmetrically: drop setup3_bounce_rejection trades and any trade whose (symbol, direction) is in {(GODREJCP, SHORT), (INDUSTOWER, LONG), (HINDUNILVR, SHORT), (UNITDSPR, SHORT), (HINDCOPPER, SHORT), (OIL, SHORT), (IRCTC, SHORT), (HINDALCO, LONG), (TATASTEEL, LONG), (NHPC, SHORT), (PFC, SHORT), (RECLTD, SHORT)}. Everything else in the book is frozen verbatim (five components and all book law through SAT-30).
- **Controls in the same pass (mandatory, before any number is believed):** (i) timing audit via H1._AUDIT deltas on both builds — 0 violations required; (ii) sign-flip placebo on IDENTICAL entries (same days, same band slice, same machinery, dirmode="fade", same exclusions) — the real rule must beat the placebo in total AND per-trade expectancy (Lesson 18 discipline: expectancy first); (iii) halves (Jan–May / Jun–Oct) disclosed for the component; (iv) breadth and ex-top-3 reported; (v) overlap vs incumbent F4 verified mechanically == 0 shared (date, symbol) pairs (disjoint premove bands make this structural); (vi) incumbent anchor == state (656 tr / +₹196,346.96 / month table / ex-top-3 ₹71,257.47) asserted BEFORE the component is scored.
- **Saturation gate:** bank the component iff (a) union total > +₹196,346.96; (b) all ten months > 0 in the union; (c) union October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹71,257.47; (e) anchors + timing audit pass AND the component beats its sign-flip placebo on total and expectancy. If banked: no_beat_cycles stays 0, best_total updates; F4-UPBAND becomes the book's 6th component under this frozen definition (December judging applies, Lesson 7). If any leg fails: do NOT bank, no_beat_cycles 0 → 1, and the band's upper boundary verdict is recorded (validated like its lower boundaries, or not) in the lessons.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat31_score.py):** anchor exact first (656 tr / +₹196,346.96 / month table to the paisa / ex-top-3 ₹71,257.47; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33). Builds over 135 below50 non-weekend days (October: 20, all below50). **Component standalone: 124 raw → 87 trades after the symmetric exclusions, net −₹24,036.07, expectancy −₹276.28/trade, 28 winners, breadth 9/25. Halves BOTH negative: Jan–May −₹16,589.40 / Jun–Oct −₹7,446.67.** Months: Jan −6,874.12 · Feb −1,394.66 · Mar −308.98 · Apr +488.46 · May −8,500.10 · Jun −1,336.12 · Jul 0.00 · Aug +440.14 · Sep −4,043.72 · Oct −2,506.97 — negative in 7 of 10 months. **Controls: timing audit 0 violations on both builds (153 follow / 21 fade audited signal-trades); sign-flip placebo on identical entries: 20 raw → 6 trades, −₹1,039.27, expectancy −₹173.21 — the placebo loses LESS per trade than the real rule (Lesson 18 discipline: expectancy first); overlap vs incumbent F4 = 0 shared (date, symbol) pairs, as constructed.** The disclosed M2 prior HOLDS inside the joint state: the below-trend gate does not rescue the [1.0%, 1.25%) slice.
- **Union (743 tr): +₹172,310.89** — Jan 21,662.13 · Feb 17,169.90 · Mar 20,275.43 · Apr 10,383.95 · May 26,380.76 · Jun 2,487.10 · Jul 6,543.43 · Aug 1,552.00 · Sep 15,518.79 · Oct 50,337.40. Ex-top-3 ₹71,257.47 → ₹53,306.76.
- **Decide: REJECTED — gate legs (a) total rises FAIL (172,310.89 < 196,346.96), (d) ex-top-3 FAIL, (e) controls FAIL (placebo beats the real rule per-trade); legs (b) all-green and (c) October ≥ 50,000 pass but cannot purchase the failed legs.** Incumbent unchanged (+₹196,346.96). **Saturation: no_beat_cycles 0 → 1, best_total unchanged ₹196,346.96.** The band's upper boundary is now VALIDATED like its lower ones: F4's [0.5%, 1.0%) cap is load-bearing on BOTH sides. F4-UPBAND family CLOSED (Lesson 17 addendum, SAT-31). No book law added.
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — the gap is stated plainly); counter at 1 — two more consecutive no-beats end the run as saturated. Frontiers: (i) genuinely new Lesson-3 material (the reaction-lag axis is fully mapped; the F4 band is now bounded by failing complements on both sides and by the mirror failure — the state axis inside F4 offers no further slices); (ii) August remains the thinnest month at +₹1,111.86; (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required, bar NOT to be lowered).

## SAT-32 — NEW COMPONENT P2F-LOWBAND: the reaction band's lower complement [2.0%, 2.5%) at R+1 (6th component candidate; new earning material — the deletion registry is EMPTY): FROZEN FOR SCORING (2026-10-31)

- **Charter basis:** the registry is exhausted (SAT-30) and F4-UPBAND is closed (SAT-31). Lesson 17's corollary licenses testing a boundary's complement exactly once. P2F's ≥2.5% band floor has never had its complement scored at the book's OWN exits: CH-1's 2.0%-band run was an ungated profile challenger at S065 (the wider stop Lesson 4/CH-1 showed hurts P2F) with a direction rule that never fired — it did not isolate this slice. This cycle tests the incremental slice alone, at S050, frozen and placebo-controlled.
- **DISCLOSED PRIOR (stated before scoring, not after):** CH-1's 2.0%-band ungated follow underperformed the 2.5% component (+₹12,835.88 at 2.0 vs +₹15,489.08 at 2.5 on the T1/T2 runs, and the CH-1 challenger lost to the incumbent) — the prior says this slice is at best a dilutant. The test is run because the slice has never been isolated at the book's exits, and the answer either buys a new component or validates the 2.5% floor by its complement (the Lessons 17/20 pattern).
- **Definition (verbatim):** P2F-LOWBAND = for each results/news reaction day (stock_event_calendar_jan_oct_2026, effective reaction date R per the audited event logic) on a home-25 stock whose reaction-day close-to-close move satisfies **2.0% ≤ |reaction| < 2.5%** (disjoint from P2F's ≥2.5% band by construction), enter at the **R+1 open** (first 5-min bar open of the next trading session) in the reaction direction (up-reaction → LONG, down-reaction → SHORT), exits **T125/S050** (the book's P2F exits), square-off 15:10, replay convention = the audited tuning machinery (exits evaluated from the bar after the entry bar). RF-1 stand-aside (no weekend-session entry days). P2F's mechanism-scoped exclusions apply: **ASTRAL and HINDUNILVR excluded whole-name; HINDALCO LONG excluded** (HINDALCO SHORT, if any, kept). Everything else in the book is frozen verbatim (five components and all book law through SAT-31).
- **Construction anchor (VERIFIED in diagnosis, stocks_engine_sat32_diag.py):** the identical machinery at the incumbent band (≥2.5%, lag +1) reproduces the tuning dump's P2F leg **39/39 per-trade** (net + exit reason), AND the lowband build reproduces the dump's own [2.0%, 2.5%) rows **9/9 per-trade** — the slice population exists verbatim inside the audited tuning dump (48 P2F rows = 39 + 9). Replay start-offset = 1 (entry bar skipped), determined empirically (offset 0 matches only 32/39 + 8/9).
- **Diagnosis (stocks_engine_sat32_diag.py / sat32_diag.json):** 9 lowband candidates; raw 9 trades → **frozen 8** after RF-1 + exclusions (1 dropped: HINDUNILVR LONG, 2026-05-05, −₹1,190.75 — the JU-1 exclusion; no RF-1 weekend drops). **Frozen 8 trades:** 2026-01-30 TVSMOTOR SHORT −₹1,872.50 (stop) · 2026-02-10 TATASTEEL LONG −₹141.49 (stop) · 2026-07-28 RECLTD LONG −₹224.00 (stop) · 2026-08-04 ITC LONG −₹6.00 (square-off) · 2026-08-06 NHPC SHORT +₹29.00 (square-off) · 2026-08-11 OIL LONG +₹540.37 (target) · 2026-10-21 HDFCBANK SHORT −₹394.77 (stop) · 2026-10-22 HINDZINC SHORT +₹606.94 (target). **Sum −₹1,462.45, 3 winners.** Standalone: expectancy **−₹182.81/trade**, breadth 3/8, halves **H1 −₹2,013.99 / H2 +₹551.54** (the split flips — H1 carries the TVSMOTOR stop). Month slices: Jan −1,872.50 · Feb −141.49 · Jul −224.00 · **Aug +563.37** · **Oct +212.17** · Mar/Apr/May/Jun/Sep 0.00. **Placebo (opposite direction, identical entries, same filters): 8 trades, −₹3,465.83, expectancy −₹433.23, 0 winners — the real rule beats its placebo in total AND per-trade, but is itself negative.** Timing audit 0 violations (every entry date verified == R+1 in the daily series).
- **Controls in the same pass at scoring (mandatory):** (i) incumbent anchor == state (656 tr / +₹196,346.96 / month table / ex-top-3 ₹71,257.47) asserted BEFORE judging, per book law (N4 = SAT-15 dump minus SAT-17/SAT-24; F4 = SAT-10 dump minus all F4 exclusions through SAT-30; INV-LONG minus BDL+VEDL+HINDZINC+INDUSTOWER+KALYANKJIL; P2F-R2 minus SAT-21); (ii) frozen set at scoring == the diagnosis set above exactly; (iii) timing audit asserted; (iv) overlap vs incumbent P2F and P2F-R2 == 0 shared (date, stock) pairs, verified mechanically (disjoint bands make P2F overlap structural; R2 shares reaction days at a different lag — entry dates differ); (v) placebo on the frozen subset reported.
- **Saturation gate:** bank the component iff (a) union total > +₹196,346.96; (b) all ten months > 0 in the union; (c) union October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹71,257.47; (e) anchors + timing audit pass AND the component beats its placebo on total and expectancy. If banked: no_beat_cycles stays 0, best_total updates; P2F-LOWBAND becomes the book's 6th component under this frozen definition (December judging applies, Lesson 7). If any leg fails: do NOT bank, no_beat_cycles 1 → 2, and the 2.5%-floor verdict is recorded in the lessons.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat32_score.py; Anchors A/B/C all pass):** incumbent anchor exact (656 tr / +₹196,346.96 / month table to the paisa / ex-top-3 ₹71,257.47; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33). Frozen set at scoring == the diagnosis set exactly (8 tr); timing audit 0 violations; overlap vs P2F = 0 and vs P2F-R2 = 0 shared (date, stock) pairs, verified mechanically. **Component standalone (frozen): 8 tr / −₹1,462.45, expectancy −₹182.81, 3 winners, breadth 3; halves H1 −₹2,013.99 / H2 +₹551.54; August slice +₹563.37, October slice +₹212.17. Placebo (opposite direction, identical entries, same filters): 8 tr / −₹3,465.83, expectancy −₹433.23, 0 winners (all 8 placebo trades are stop exits — the slice's R+1 days whipsaw through ±0.5% adversely for both directions; the follow direction survives better, holding the slice's only two target exits) — the component BEATS its placebo in total and per-trade.** **Union (664 tr): +₹194,884.51** — Jan 26,663.75 · Feb 18,423.07 · Mar 20,584.41 · Apr 9,895.49 · May 34,880.86 · Jun 3,823.22 · Jul 6,319.43 · Aug 1,675.23 · Sep 19,562.51 · Oct 53,056.54. Ex-top-3 ₹71,257.47 → ₹71,667.52 (top-3 unchanged TVSMOTOR / ASTRAL / OBEROIRLTY).
- **Decide: REJECTED — gate leg (a) total rises FAILS (₹194,884.51 < ₹196,346.96); legs (b) all-green, (c) October ≥ 50,000 (₹53,056.54), (d) ex-top-3 (₹71,667.52) and (e) anchors/audit/placebo all pass but cannot purchase leg (a) (the SAT-12 discipline: a gate leg is not purchasable with another leg's currency — the August thickening to ₹1,675.23 is kindness, not money).** Incumbent unchanged (+₹196,346.96). **Saturation: no_beat_cycles 1 → 2, best_total unchanged ₹196,346.96.** The disclosed CH-1 prior holds at the slice level with the book's own exits: the [2.0%, 2.5%) slice is a net drag (its −₹182.81 expectancy is the arithmetic reason CH-1's 2.0% band underperformed). **P2F's 2.5% floor is now VALIDATED by its complement at R+1 — P2F-LOWBAND family CLOSED (Lesson 21).** No book law added.
- **Next:** saturation continues from +₹196,346.96 (₹19,635/month vs the ₹75,000/month goal — stated plainly); counter at 2 of 3 — one more consecutive no-beat ends the run as saturated. Frontiers: (i) genuinely new Lesson-3 material outside the reaction-band/lag complex (both P2F band boundaries, the F4 band's both complements + mirror, and the R-ladder are all closed; the reaction axis is now bounded on every side it has been tested) and outside the F4 state slices; (ii) August thickening by new material (August +₹1,111.86, still the minimum month); (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required, bar NOT to be lowered).

## SAT-33 — R2-LOWBAND (the last cell of the (band × lag) grid) — FROZEN BEFORE SCORING (2026-10-31)
- **Definition (verbatim):** a NEW component candidate: results/news reaction days whose reaction-day move is in **[2.0%, 2.5%)** (the incremental slice below P2F's ≥2.5% floor), entered at the **R+2 open** (second trading session after the reaction day) in the reaction direction, exits **T125/S050**, square-off 15:10, RF-1 weekend stand-aside, and P2F's mechanism-scoped exclusions applied (**ASTRAL** and **HINDUNILVR** whole-name; **HINDALCO LONG**). Everything else in the book is frozen verbatim.
- **Disclosed priors (negative on both axes, recorded before scoring):** SAT-32 showed this band slice loses at R+1 (frozen 8 tr / −₹1,462.45, expectancy −₹182.81); Lesson 20 showed the ≥2.5% signal decays by lag (R+3 expectancy ≈ ₹0, placebo beats it). This cell is tested exactly once, as the grid's closing cell, on the record — no retest, no blending, no lag-averaging if it fails.
- **Controls (same pass, before any number is believed):** construction anchor — the identical machinery at lag +2 on the ≥2.5% band must reproduce the SAT-13 P2F-R2 frozen dump (34 trades) per-trade; timing audit (every entry date == R+2 in the daily series) asserted 0 violations; opposite-direction placebo on identical entries; halves; breadth; (date, stock) overlap vs incumbent P2F, P2F-R2 and the SAT-32 P2F-LOWBAND frozen set must be 0, verified mechanically.
- **Gate (saturation beat):** bank only if the union total rises AND all ten months stay green AND October ≥ ₹50,000 AND ex-top-3 not worse AND controls pass. Incumbent: +₹196,346.96 / 656 tr; saturation no_beat_cycles = 2 — a no-beat closes the run as SATURATED.

## SAT-34 — NEW COMPONENT R2-MIDBAND: the reaction band's next cell down, [1.5%, 2.0%), at R+2 (7th component candidate; new earning material — the deletion registry is EMPTY): FROZEN FOR SCORING (2026-10-31)

- **Charter basis:** Lesson 22 — a grid cell is closed by its own controlled run, never by extrapolation from its neighbours. The (band × lag) grid's two living low cells both sit at R+2 (P2F-R2 at ≥2.5%, R2-LOWBAND at [2.0%, 2.5%) banked in SAT-33); the next cell down the band axis at that same lag — [1.5%, 2.0%) at R+2 — has never been run. This cycle tests it exactly once, frozen and placebo-controlled, like every other cell.
- **DISCLOSED PRIORS (stated before scoring, not after):** negative on the band axis — Lesson 17 (N4's [0.75%, 1.0%) complement is dead at its lag; sub-1% follow-through does not exist) and Lesson 21 (the [2.0%, 2.5%) slice at R+1 held only faint content and lost after costs). Positive on the method — Lesson 22 (band and lag interact; SAT-32's dead cell at R+1 did not predict SAT-33's live cell at R+2). The priors conflict; the cell's own run decides.
- **Definition (verbatim):** R2-MIDBAND = for each results/news reaction day (stock_event_calendar_jan_oct_2026, effective reaction date R per the audited event logic) on a home-25 stock whose reaction-day close-to-close move satisfies **1.5% ≤ |reaction| < 2.0%** (disjoint from R2-LOWBAND's [2.0%, 2.5%) and P2F-R2's ≥2.5% bands by construction), enter at the **R+2 open** (first 5-min bar open of the second trading session after R) in the reaction direction (up-reaction → LONG, down-reaction → SHORT), exits **T125/S050** (the reaction complex's exits), square-off 15:10, replay convention = the audited SAT-13/33 machinery (exits evaluated from the bar after the entry bar). RF-1 stand-aside (no weekend-session entry days). P2F's mechanism-scoped exclusions apply: **ASTRAL and HINDUNILVR excluded whole-name; HINDALCO LONG excluded** (HINDALCO SHORT, if any, kept). Everything else in the book is frozen verbatim (six components and all book law through SAT-33).
- **Diagnosis (stocks_engine_sat34_diag.py / sat34_diag.json — to be confirmed by the audited score pass, not believed before it):** construction anchor — the identical machinery at lag +2 on the ≥2.5% band reproduces the SAT-13 P2F-R2 frozen dump **34/34 per-trade**; incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7). Candidates **7** → raw 7 → **frozen 6** (1 dropped: ASTRAL SHORT, 2026-02-10, −₹789.75 — the AU-1 exclusion; no RF-1 weekend drops). **Frozen 6 trades:** 2026-02-05 INDUSTOWER LONG −₹262.55 (stop) · 2026-05-18 TVSMOTOR SHORT +₹4,247.50 (target) · 2026-05-26 ITC SHORT +₹220.00 (square-off) · 2026-08-04 TATASTEEL LONG −₹135.35 (stop) · 2026-08-12 HINDCOPPER SHORT −₹305.42 (stop) · 2026-10-22 OBEROIRLTY SHORT −₹855.00 (stop). **Sum +₹2,909.18, 2 winners.** Standalone: expectancy **+₹484.86/trade**, breadth 2/6, halves **H1 +₹4,204.95 / H2 −₹1,295.77**. Month slices: Feb −262.55 · May +4,467.50 · **Aug −440.77** · **Oct −855.00** · six months flat. **Placebo (opposite direction, identical entries, same filters): 6 trades, +₹1,054.91, expectancy +₹175.82, 3 winners** — beaten by the real rule in total and per-trade, and the component clears zero, BUT the placebo is itself POSITIVE (see disclosures). Timing audit 0 violations (every entry date verified == R+2 in the daily series); (date, stock) overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / N4-V3 all 0, verified mechanically.
- **THIN-SAMPLE / CONCENTRATION DISCLOSURES (first-class, recorded in the freeze, not after the verdict):** (i) the entire component net is ONE trade — TVSMOTOR SHORT +₹4,247.50 exceeds the component's whole +₹2,909.18; ex-that-trade the component is **−₹1,338.32**; (ii) the placebo is positive (+₹175.82/trade), so on 6 trades the directional content is not cleanly separable from R+2-day volatility — the Lesson 21 clauses (beat placebo per-trade AND clear zero) are met mechanically, but the margin is one trade deep; (iii) win rate 2/6 and H2 is negative (−₹1,295.77); (iv) the August slice (−₹440.77) would spend the August razor from ₹666.78 to **₹226.01** — inside the ≥ ₹100 margin guard, with ₹126.01 to spare; (v) pre-registered expectation for leg (d): because the carrying trade sits on TVSMOTOR (a top-3 name, +₹4,247.50) while OBEROIRLTY (also top-3) contributes −₹855.00, the union ex-top-3 is expected to FALL by ≈ ₹483 (to ≈ ₹72,035) if top-3 membership is unchanged — leg (d) is therefore expected to be the binding leg, and the score pass will compute it exactly rather than argue about it here.
- **Controls in the same pass at scoring (mandatory):** (i) incumbent anchor == state (663 tr / +₹197,607.74 / month table / ex-top-3 ₹72,518.25) asserted BEFORE judging, per book law (N4 = SAT-15 dump minus SAT-17/SAT-24; F4 = SAT-10 dump minus all F4 exclusions through SAT-30; INV-LONG minus BDL+VEDL+HINDZINC+INDUSTOWER+KALYANKJIL; P2F-R2 minus SAT-21; R2-LOWBAND from the SAT-33 dump); (ii) construction anchor re-verified (lag+2 ≥2.5% == SAT-13 dump 34/34); (iii) frozen set at scoring == the diagnosis set above exactly; (iv) timing audit asserted 0; (v) overlap vs ALL incumbent reaction components == 0 shared (date, stock) pairs, verified mechanically; (vi) placebo on the frozen subset reported.
- **Saturation gate:** bank the component iff (a) union total > +₹197,607.74; (b) all ten months > 0 in the union AND August ≥ ₹100 (the razor margin); (c) union October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹72,518.25; (e) anchors + timing audit pass AND the component beats its placebo on total and per-trade expectancy AND the component's expectancy clears zero (the full Lesson 21 test). If banked: no_beat_cycles stays 0, best_total updates; R2-MIDBAND becomes the book's 7th component under this frozen definition (December judging applies, Lesson 7) with the thin-sample disclosure carried verbatim. If any leg fails: do NOT bank, no_beat_cycles 0 → 1, and the cell is recorded CLOSED in the lessons — no retest, no blending, no lag-averaging (Lessons 20/22 discipline).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat34_score.py; Anchors A/B/C + construction anchor all pass):** incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7); construction anchor 34/34 in the score pass; frozen set == diagnosis set exactly (6 tr); timing audit 0 violations; overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / N4-V3 all 0, verified mechanically. **Component standalone (frozen): 6 tr / +₹2,909.18, expectancy +₹484.86, 2 winners, breadth 2; halves H1 +₹4,204.95 / H2 −₹1,295.77; August slice −₹440.77, October slice −₹855.00. Placebo (flip, identical entries): 6 tr / +₹1,054.91, expectancy +₹175.82, 3 winners — POSITIVE outright, beaten by the real rule in total and per-trade; the component clears zero (the full Lesson 21 test passes standalone).** The carrying trade is TVSMOTOR SHORT 2026-05-18, +₹4,247.50 (target); ex-it the component is −₹1,338.32. **Union (669 tr): +₹200,516.92** — Jan 28,536.25 · Feb 18,157.31 · Mar 20,584.41 · Apr 9,895.49 · May 39,348.36 · Jun 3,823.22 · Jul 6,965.93 · **Aug 226.01** · Sep 19,562.51 · **Oct 53,417.43** (headroom ₹3,417.43). Ex-top-3 **₹72,518.25 → ₹72,034.93 (−₹483.32** — exactly the freeze's pre-registered expectation: top-3 membership unchanged, TVSMOTOR 74,005.46 → 78,252.96, OBEROIRLTY 23,236.24 → 22,381.24).
- **Decide: REJECTED — gate leg (d) FAILS (ex-top-3 worsens by ₹483.32); legs (a) total rises (+₹200,516.92), (b) all-green with August ₹226.01 ≥ ₹100, (c) October ₹53,417.43 ≥ ₹50,000 and (e) anchors/audit/placebo all pass and cannot purchase leg (d) (the SAT-12 discipline).** The component is positive standalone and is still a concentration purchase, not an earning stream: its whole net sits on the book's #1 earner. Incumbent unchanged (+₹197,607.74). **Saturation: no_beat_cycles 0 → 1, best_total unchanged ₹197,607.74.** **R2-MIDBAND family CLOSED (Lesson 23).** No book law added; no component dump written.
- **Next:** saturation continues from +₹197,607.74 (₹19,761/month vs the ₹75,000/month goal — stated plainly); counter at 1 of 3. Frontiers: (i) genuinely new Lesson-3 material outside the reaction grid (now mapped on both lags: ≥2.5% real R+1/R+2, dead R+3; [2.0,2.5) dead R+1, thin-banked R+2; [1.5,2.0) rejected-at-R+2 on concentration) and outside the bounded F4 band; (ii) August thickening by new material (August +₹666.78, still the minimum month); (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required, bar NOT to be lowered).

## SAT-35 — NEW COMPONENT P2F-MIDBAND: the reaction band's [1.5%, 2.0%) cell at R+1 (7th component candidate; new earning material — the deletion registry is EMPTY): FROZEN FOR SCORING (2026-10-31)

- **Charter basis:** Lesson 22 — a grid cell is closed by its own controlled run, never by extrapolation from its neighbours. SAT-34 tested this band ([1.5%, 2.0%)) at R+2 and it was rejected on gate leg (d) (Lesson 23) — that closes the R+2 cell, not this one. The R+1 row's cells so far: ≥2.5% is the incumbent P2F; [2.0%, 2.5%) at R+1 is dead (SAT-32, Lesson 21). The [1.5%, 2.0%) cell at R+1 has never been run. This cycle tests it exactly once, frozen and placebo-controlled, like every other cell.
- **DISCLOSED PRIORS (stated before scoring, not after):** negative on both axes — Lesson 21 (the [2.0%, 2.5%) slice at this same lag held only faint content and lost after costs; a descent one band lower at the same lag starts weaker) and Lesson 23 (this band at R+2 was one-trade-carried with a positive placebo). Positive only on the method — Lesson 22 (band and lag interact; neither axis's verdict transfers). The priors lean negative; the cell's own run decides.
- **Definition (verbatim):** P2F-MIDBAND = for each results/news reaction day (stock_event_calendar_jan_oct_2026, effective reaction date R per the audited event logic) on a home-25 stock whose reaction-day close-to-close move satisfies **1.5% ≤ |reaction| < 2.0%** (disjoint from P2F-LOWBAND's [2.0%, 2.5%) and P2F's ≥2.5% bands by construction), enter at the **R+1 open** (first 5-min bar open of the first trading session after R) in the reaction direction (up-reaction → LONG, down-reaction → SHORT), exits **T125/S050** (the reaction complex's exits), square-off 15:10, replay convention = the audited SAT-32 lag+1 machinery (start-offset determined empirically against the tuning dump). RF-1 stand-aside (no weekend-session entry days). P2F's mechanism-scoped exclusions apply: **ASTRAL and HINDUNILVR excluded whole-name; HINDALCO LONG excluded** (HINDALCO SHORT, if any, kept). Everything else in the book is frozen verbatim (six components and all book law through SAT-33).
- **Diagnosis (stocks_engine_sat35_diag.py / sat35_diag.json — to be confirmed by the audited score pass, not believed before it):** construction anchor — the identical lag+1 machinery reproduces the tuning dump's P2F leg on BOTH verified slices (**≥2.5%: 39/39; [2.0%, 2.5%): 9/9**; replay start-offset 1; offset 0 matches only 32/39 + 8/9), so the [1.5%, 2.0%) slice is built by machinery verified per-trade at this lag; incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7). Candidates **7** → raw 7 → **frozen 6** (1 dropped: ASTRAL SHORT, 2026-02-09, −₹778.40 — the AU-1 exclusion; no RF-1 weekend drops). **Frozen 6 trades:** 2026-02-04 INDUSTOWER LONG +₹509.00 (target) · 2026-05-15 TVSMOTOR SHORT −₹1,767.80 (stop) · 2026-05-25 ITC SHORT −₹191.97 (stop) · 2026-08-03 TATASTEEL LONG −₹136.47 (stop) · 2026-08-11 HINDCOPPER SHORT −₹305.50 (stop) · 2026-10-21 OBEROIRLTY SHORT −₹881.00 (stop). **Sum −₹2,773.74, 1 winner.** Standalone: expectancy **−₹462.29/trade**, breadth 1/6, halves **H1 −₹1,450.77 / H2 −₹1,322.97** (both negative). Month slices: Feb +509.00 · May −1,959.77 · **Aug −441.97** · **Oct −881.00** · six months flat. **Placebo (opposite direction, identical entries, same filters): 6 trades, −₹2,275.45, expectancy −₹379.24, 2 winners — the placebo LOSES LESS than the real rule in total and per-trade.** Three of the six entry days (TVSMOTOR, ITC, OBEROIRLTY) stop out at the identical net in BOTH directions — the R+1 day blasts through the ±0.5% stop adversely regardless of direction (the SAT-32 whipsaw signature). Timing audit 0 violations (every entry date verified == R+1 in the daily series); (date, stock) overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / R2-MIDBAND / N4-V3 all 0, verified mechanically.
- **THIN-SAMPLE / CONCENTRATION DISCLOSURES (first-class, recorded in the freeze, not after the verdict):** (i) the component fails the Lesson 21 standalone test on every clause at diagnosis — expectancy is negative (−₹462.29), and the placebo beats the real rule in total (−₹2,275.45 vs −₹2,773.74) and per-trade (−₹379.24 vs −₹462.29); (ii) the ex-carrier number (net excluding the single best trade) is **−₹3,282.74** — the only winner (+₹509.00) is not carrying a positive net, it is cushioning a negative one; (iii) win rate 1/6, breadth 1/6, both halves negative; (iv) the August slice (−₹441.97) would spend the August razor from ₹666.78 to **₹224.81** — inside the ≥ ₹100 margin guard; (v) pre-registered expectation for leg (d): the component's top-3-name contribution is TVSMOTOR −₹1,767.80 + OBEROIRLTY −₹881.00 = −₹2,648.80 against a component net of −₹2,773.74, so if top-3 membership is unchanged the union ex-top-3 is expected to FALL by ≈ ₹124.94 (to ≈ ₹72,393.31) — leg (d) is expected to fail alongside legs (a) and (e); the score pass computes it exactly; (vi) same reaction events as SAT-34's R+2 cell (7 candidates both times) with opposite fortunes by entry day — e.g. TVSMOTOR (R 2026-05-14, −1.69%): +₹4,247.50 target at R+2, −₹1,767.80 stop at R+1 — recorded as population evidence, not as an argument either way.
- **Controls in the same pass at scoring (mandatory):** (i) incumbent anchor == state (663 tr / +₹197,607.74 / month table / ex-top-3 ₹72,518.25) asserted BEFORE judging, per book law (N4 = SAT-15 dump minus SAT-17/SAT-24; F4 = SAT-10 dump minus all F4 exclusions through SAT-30; INV-LONG minus BDL+VEDL+HINDZINC+INDUSTOWER+KALYANKJIL; P2F-R2 minus SAT-21; R2-LOWBAND from the SAT-33 dump); (ii) construction anchor re-verified (lag+1 machinery == tuning dump P2F leg on both verified slices: ≥2.5% 39/39 AND [2.0%, 2.5%) 9/9); (iii) frozen set at scoring == the diagnosis set above exactly; (iv) timing audit asserted 0; (v) overlap vs ALL incumbent reaction components == 0 shared (date, stock) pairs, verified mechanically; (vi) placebo on the frozen subset reported; (vii) ex-carrier number (net excluding the single best trade) reported.
- **Saturation gate:** bank the component iff (a) union total > +₹197,607.74; (b) all ten months > 0 in the union AND August ≥ ₹100 (the razor margin); (c) union October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹72,518.25; (e) anchors + timing audit pass AND the component beats its placebo on total and per-trade expectancy AND the component's expectancy clears zero (the full Lesson 21 test). If banked: no_beat_cycles stays 0, best_total updates; P2F-MIDBAND becomes the book's 7th component under this frozen definition (December judging applies, Lesson 7) with the thin-sample disclosure carried verbatim. If any leg fails: do NOT bank, no_beat_cycles 1 → 2, and the cell is recorded CLOSED in the lessons — no retest, no blending, no lag-averaging (Lessons 20/22 discipline).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat35_score.py; Anchors A/B/C + construction anchor all pass):** incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; components INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7); construction anchor re-verified in the score pass (lag+1 machinery == tuning dump P2F leg: ≥2.5% 39/39 AND [2.0%, 2.5%) 9/9); frozen set == diagnosis set exactly (6 tr); timing audit 0 violations; overlap vs P2F / P2F-R2 / P2F-LOWBAND / R2-LOWBAND / R2-MIDBAND / N4-V3 all 0, verified mechanically. **Component standalone (frozen): 6 tr / −₹2,773.74, expectancy −₹462.29, 1 winner, breadth 1; halves H1 −₹1,450.77 / H2 −₹1,322.97; August slice −₹441.97, October slice −₹881.00. Placebo (flip, identical entries): 6 tr / −₹2,275.45, expectancy −₹379.24, 2 winners — the placebo loses LESS than the real rule in total and per-trade; the component clears neither zero nor its flipped self (the full Lesson 21 test fails on every clause).** Best trade INDUSTOWER LONG 2026-02-04 +₹509.00 (the only winner); **ex-carrier −₹3,282.74**. Three entry days (TVSMOTOR −₹1,767.80, ITC −₹191.97, OBEROIRLTY −₹881.00) stop out at the identical net in both directions. **Union (669 tr): +₹194,834.00** — Jan 28,536.25 · Feb 18,928.86 · Mar 20,584.41 · Apr 9,895.49 · May 32,921.09 · Jun 3,823.22 · Jul 6,965.93 · **Aug 224.81** · Sep 19,562.51 · **Oct 53,391.43** (headroom ₹3,391.43). Ex-top-3 **₹72,518.25 → ₹72,393.31 (−₹124.94** — exactly the freeze's pre-registered expectation; top-3 membership unchanged).
- **Decide: REJECTED — gate legs (a), (d) and (e) FAIL; legs (b) (all-green, August ₹224.81 ≥ ₹100) and (c) (October ₹53,391.43) pass and cannot purchase them (the SAT-12 discipline).** The cell carries no directional content at this lag at all: the follow rule is the worse of the two directions on its own entries. Incumbent unchanged (+₹197,607.74). **Saturation: no_beat_cycles 1 → 2, best_total unchanged ₹197,607.74.** **P2F-MIDBAND family CLOSED (Lesson 24).** No book law added; no component dump written.
- **Next:** saturation continues from +₹197,607.74 (₹19,761/month vs the ₹75,000/month goal — stated plainly); counter at 2 of 3 — one more consecutive no-beat cycle saturates the run. The (band × lag) reaction grid is now fully mapped (R+1: ≥2.5% real, [2.0,2.5) dead, [1.5,2.0) direction-free; R+2: ≥2.5% real, [2.0,2.5) thin-banked, [1.5,2.0) concentration-rejected; R+3 dead). Frontiers: (i) genuinely new Lesson-3 material outside the reaction grid and outside the bounded F4 band; (ii) August thickening by new material (August +₹666.78, still the minimum month); (iii) the GLENMARK-SHORT argument (below-bar — explicit argument required, bar NOT to be lowered).

## SAT-36 — FORMAL JUDGEMENT: F4 × GLENMARK × SHORT exclusion (the standing item, judged on its merits at last; the deletion registry is EMPTY and this slice sits BELOW its bar): FROZEN FOR SCORING (2026-10-31)
- **Charter:** refused procedurally three times (SAT-8: floor-blocked + concentration name; SAT-14: "an August story, not rot"; SAT-17 registry: the queue's bottom row, below the bar). October headroom (₹4,272.43) now covers its October slice, so the floor objection is dead; what remains is the merits question, and this cycle answers it formally rather than leaving it as a permanent procedural deferral. The recorded facts were stale (Lesson 16) and are re-derived at the current book in the diagnosis (stocks_engine_sat36_diag.py / sat36_diag.json) BEFORE this freeze.
- **Diagnosis (anchor A exact: 663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7):** the slice re-measures IDENTICAL to the SAT-14 record (its legs were never touched by SAT-15..SAT-35 — Lesson 16 invariance): **20 trades, 10 winners, net −₹136.98, expectancy −₹6.85/trade (≈ ₹0)**. Months: Jan −390.00 · Feb −859.68 · Mar −142.71 · **Apr −1,926.32** · **May +3,519.65** · Jun −1,020.00 · **Aug −4,744.78** · **Sep +4,364.31** · **Oct +1,062.55** (6 of 9 traded months negative, 5 ex-August). Halves: **H1 +₹200.94 / H2 −₹337.92** (the halves nearly cancel — no persistent sign). **Net excluding August: +₹4,607.80 — outside one month the slice EARNS.** Worst trade 2026-08-31 −₹2,386.69 (skill_or_breakdown); **ex-carrier (net ex-worst) +₹2,249.71** — the entire negative case rests on the August trades, and materially on one of them. Best trade 2026-09-09 +₹3,622.85. Context: F4 × GLENMARK × LONG earns +₹3,188.19 (13 tr, kept either way); GLENMARK whole-book +₹20,615.44 (10.43% of the book; #4 earner — top-3 are TVSMOTOR / ASTRAL / OBEROIRLTY, so this is no longer a top-3 name, though it remains a carrier name; its August event wins carried August in both directions per SAT-7).
- **Fix (frozen BEFORE scoring):** SAT-36-F4-GLENMARK-SHORT — F4 takes no SHORT signals on GLENMARK (stock × mechanism × DIRECTION exclusion; F4 keeps GLENMARK LONG; all other components trade GLENMARK unchanged). The deleted set is the 20 trades in the diagnosis, asserted trade-by-trade at scoring (Anchor B). Deletion-only on the audited SAT-10 dump; timing inherited.
- **TWO standards, both pre-registered, BOTH must pass to bank:** (1) **the arithmetic saturation gate** — (a) union total > +₹197,607.74; (b) all ten months > 0 AND August ≥ ₹100; (c) union October ≥ +₹50,000; (d) union ex-top-3 not worse than ₹72,518.25; (e) anchors A/B pass. (2) **the standing quality bar** — the registry's Lesson 5 rot-everywhere standard: the slice's full-period net ≤ −₹500 at the CURRENT book. **The bar is not lowered at the finish line:** a gate pass bought by the bar's failure is month-shape, not money (Lesson 5; SAT-6 addendum; SAT-14 precedent). Pre-registered arithmetic, stated before scoring: the gate is EXPECTED to pass on all five legs (total +₹136.98 nominal; August → ≈ ₹5,411.56; October → ₹53,209.88; ex-top-3 unchanged at equality if top-3 membership holds, since the deletion raises GLENMARK's per-stock total and the total by the identical −(−₹136.98)) — and the quality bar is EXPECTED to fail (−₹136.98 > −₹500). If both expectations hold, the refusal is recorded as a PRINCIPLED no-beat: the engine declines a nominal total rise manufactured out of one month's shape on a near-zero-expectancy, half-winning population.
- **If banked (both standards pass):** no_beat_cycles stays 0; book law added (F4 takes no GLENMARK SHORT signals). **If not banked:** no_beat_cycles 2 → 3 — **the run is SATURATED** and closes in this cycle: the incumbent (+₹197,607.74, 663 tr, six components) is frozen verbatim in stocks_engine_candidate_spec.md for December judging, and the final saturation summary is written to stocks_engine_log.md.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Oct 2026.
- **Exact score (stocks_engine_sat36_score.py; Anchors A/B pass):** incumbent anchor exact (663 tr / +₹197,607.74 / month table to the paisa / ex-top-3 ₹72,518.25; INV 155 / N4 47 / P2F 32 / F4 389 / R2 33 / R2LOW 7); deleted set == the frozen diagnosis set exactly (20 tr / −₹136.98). **Union (643 tr): +₹197,744.72** — Jan 28,926.25 · Feb 19,279.54 · Mar 20,727.12 · Apr 11,821.81 · May 31,361.21 · Jun 4,843.22 · Jul 6,965.93 · **Aug 5,411.56** · Sep 15,198.20 · **Oct 53,209.88** (headroom ₹3,209.88). Ex-top-3 **₹72,518.25 → ₹72,655.23 (+₹136.98; top-3 membership unchanged — GLENMARK is #4, so the deletion raises the total and the ex-top-3 sum by the identical amount)**.
- **Decide: GATE (standard 1) PASSES on all five legs — (a) total +₹136.98, (b) all-green with August ₹5,411.56, (c) October ₹53,209.88, (d) ex-top-3 +₹136.98, (e) anchors — and the QUALITY BAR (standard 2) FAILS: slice full-period −₹136.98 > −₹500. NOT BANKED.** Every leg's pass is the same ₹136.98 — a near-zero-expectancy (₹−6.85/trade), 10/20-winning population whose net ex-August is +₹4,607.80 and whose ex-carrier is +₹2,249.71 does not meet the Lesson 5 rot-everywhere standard, and the bar is not lowered at the finish line. **Recorded as a PRINCIPLED NO-BEAT (the SAT-14 precedent, now judged formally and closed): no_beat_cycles 2 → 3 — THE RUN IS SATURATED.** The incumbent (+₹197,607.74, 663 tr, six components) is frozen verbatim in stocks_engine_candidate_spec.md for December judging; the final saturation summary is in stocks_engine_log.md. Lesson 25 appended. The GLENMARK-SHORT question is CLOSED on this window — revisitable only on fresh (December+) data, never re-argued in-sample. The disclosed price of the standards: the ₹136.98 nominal total rise and the August thickening to ₹5,411.56 were declined. (Read: ₹136.98.)

## V2-CYCLE-1 — (GLENMARK × SHORT) exclusion from the SAME-DAY FOLLOW components (F4 + N4-V3): FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Charter:** first cycle under the v2 charter (stocks_RECURSIVE_ENGINE.md): windows Jan–Dec 2025 + Jan–Oct 2026, both scored in the same run; bank only if combined total rises AND neither year's total falls AND neither year is negative at book level. Incumbent = the frozen v1 book run verbatim on both years (stocks_engine_v2_build.py; ALL controls pass: SAT-36 dump assembly == plateau, F4/INV rebuilds per-trade, all nine event-builder anchors per-trade, 2025 F4/INV anchors exact, timing audits 0). Incumbent: 2025 full book 636 tr / **+₹23.06** (F4 261/−5,093.75 · INV-LONG 245/+7,642.52 · N4-V3 63/−5,779.08 · P2F 28/+14,365.77 · P2F-R2 28/−5,973.98 · R2-LOWBAND 11/−5,138.42; five red months; ex-top-3 −₹27,814.95); 2026 = +₹197,607.74 exact; combined **+₹197,630.80 (₹8,983.22/month over 22 months vs the ₹75,000 goal)**.
- **Diagnosis (component × year, from the machinery-built incumbent books):** the four component-level 2025 failures (P2F-R2 −5,973.98 · N4-V3 −5,779.08 · R2-LOWBAND −5,138.42 · F4 −5,093.75) are all 2026-positive, so deleting any whole component fails gate leg (b) mechanically; the two largest single 2025 leaks are regime flips, not rot (F4×HINDUNILVR×LONG −10,218.40 in 2025 but +765.62 in 2026; F4×TVSMOTOR×SHORT −5,728.79 in 2025 but +20,255.64 in 2026). The weakest CROSS-YEAR point — negative in both years, in two independent components that share one mechanism — is **GLENMARK × SHORT inside the same-day follow mechanisms**: F4 (follow the morning move by 10:00): 2025 **7 tr / −₹3,010.96** (exp −₹430.14), 2026 20 tr / −₹136.98 (exp −₹6.85); N4-V3 (follow the reaction-day move by 09:30): 2025 **2 tr / −₹2,731.28** (exp −₹1,365.64), 2026 3 tr / −₹494.21 (exp −₹164.74). Combined removal set: **32 tr / −₹6,373.43** (2025 −₹5,742.24 · 2026 −₹631.19).
- **SAT-36 DISCLOSURE (stated before scoring, not after):** SAT-36 judged F4 × GLENMARK × SHORT on the 2026 window alone (−₹136.98), refused it under the v1 −₹500 quality bar, and closed the question "on this window — revisitable only on fresh (December+) data, never re-argued in-sample." This cycle does NOT re-argue the 2026 slice (unchanged, still ≈ ₹0 expectancy, still not the basis). It re-opens the question on the condition SAT-36 itself named — fresh evidence: a full out-of-sample year (2025, never fitted, run verbatim) in which the identical (name × direction) loses −₹5,742.24 across BOTH follow components, under a user-ordered new method (2026-10-31 14:58 IST) whose charter replaces the single-window bar with the cross-year gate. If the parent or the user judges this re-opening out of bounds, the freeze record shows exactly what was done and why, and the bank can be unwound from the trade CSVs.
- **Scope discipline (why the exclusion stops at the follow mechanisms):** GLENMARK × SHORT inside the NEXT-DAY event-follow family earns in 2026 (P2F +₹5,112.24 / 2 tr; P2F-R2 +₹1,316.80 / 2 tr) — a name-wide SHORT ban would cut 2026 by ₹6,429.04 and fail the gate; the leak is specific to same-day follow entries (chasing an intraday move in a news-driven pharma name that squeezes), not to the name. GLENMARK LONG is untouched everywhere; INV-LONG / P2F / P2F-R2 / R2-LOWBAND are untouched entirely.
- **Fix (frozen BEFORE scoring):** V2C1-FOLLOW-GLENMARK-SHORT-EXCL — F4 and N4-V3 take no SHORT signals on GLENMARK; everything else in the book is frozen verbatim. Deletion-only on the machinery-built incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slices above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹5,765.30** (= 23.06 + 5,742.24), 2026 **+₹198,238.93** (= 197,607.74 + 631.19), combined **+₹204,004.23** (₹9,272.92/month). Legs: (a) combined rises +₹6,373.43; (b) neither year falls (2025 +5,742.24, 2026 +631.19); (c) neither year negative (2025 +₹5,765.30 > 0 — thin, stated plainly: the 2025 book stays within ₹5,765.30 of red even after this fix). Ex-top-3 per year and month tables reported at scoring (reporting duty, not a gate leg). Controls in the same pass: incumbent totals asserted from stocks_engine_v2_build.py's all-controls-passed output; deleted set == diagnosis set exactly; no other trade changes.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-2 — (BDL × SHORT) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (anchor exact vs the post-C1 books: 2025 627 tr / +₹5,765.30 · 2026 640 tr / +₹198,238.93 · combined +₹204,004.23; stocks_engine_v2_cycle2_diag.py):** component × year at the incumbent — P2F-R2 −5,973.98 / +14,892.38 · R2-LOWBAND −5,138.42 / +1,260.78 · N4-V3 −3,047.80 / +21,787.26 · F4 −2,082.79 / +101,894.04 · INV-LONG +7,642.52 / +38,987.84 · P2F +14,365.77 / +19,416.63. Two charter questions answered on the record: (i) **the R+2 lag is the 2025 poison, not the low band** — at the SAME ≥2.5% band, moving R+1 → R+2 flips 2025 from +₹14,365.77 (P2F) to −₹5,973.98 (P2F-R2) while 2026 stays positive; the low band at R+2 is also 2025-negative (−₹5,138.42) with a near-zero 2026. P2F-R2's 2025 loss is DIFFUSE — single trades in names that are 2026-absent (BDL LONG −1,671.00, TVSMOTOR SHORT −1,390.25, OBEROIRLTY LONG −894.00) or 2026-earners (GLENMARK SHORT −1,014.50 vs +1,316.80; OBEROIRLTY SHORT −925.00 vs +3,861.38; GODREJCP SHORT −640.00 vs +3,940.62): only ONE P2F-R2 slice is negative in both years (KALYANKJIL LONG, −₹548.17 combined), so no honest slice fix exists inside P2F-R2, and deleting the whole component fails gate leg (b) mechanically (2026 −₹14,892.38). The lag question is therefore DIAGNOSED, not fixable by deletion — it stands as the component's year-specialisation risk under December judging. (ii) **N4-V3's 2025 loss is slice-level, not whole-component:** its both-years-negative slices sum to −₹9,501.67 combined (2025 portion −₹5,713.26) against real 2025 winners (OBEROIRLTY SHORT +3,744.57, OBEROIRLTY LONG +2,455.85, UNITDSPR SHORT +2,199.35, GODREJCP LONG +1,704.20, BDL LONG +1,498.67).
- **The weakest actionable cross-year point:** N4-V3 × BDL × SHORT — the largest both-years-negative slice in the book: 2025 **2 tr / −₹2,545.00 (0 winners)** · 2026 **1 tr / −₹640.00 (0 winners)** · combined **−₹3,185.00**. Scope discipline (Lessons 11/15): BDL LONG inside N4-V3 EARNS in 2025 (+₹1,498.67) and BDL is a core earner in the other event systems (JN-1) — the exclusion is (mechanism × stock × direction)-scoped to N4-V3 × SHORT only; every other component trades BDL unchanged, and N4-V3 keeps BDL LONG.
- **Fix (frozen BEFORE scoring):** V2C2-N4-BDL-SHORT-EXCL — N4-V3 takes no SHORT signals on BDL; everything else in the book is frozen verbatim. Deletion-only on the post-C1 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹8,310.30** (= 5,765.30 + 2,545.00), 2026 **+₹198,878.93** (= 198,238.93 + 640.00), combined **+₹207,189.23** (₹9,417.69/month). Legs: (a) combined rises +₹3,185.00; (b) neither year falls; (c) neither year negative (2025 +₹8,310.30 — thicker, still the thin year, stated plainly). Ex-top-3 per year and month tables reported at scoring (reporting duty, not a gate leg). Controls in the same pass: incumbent totals asserted against the state v2 best; deleted set == diagnosis set exactly; no other trade changes.
- **Standing v2 registry bar (pre-registered for this and later deletion cycles):** a (component × stock × direction) slice qualifies only if it is negative in BOTH years AND its combined net ≤ −₹500 (the cross-year form of the Lesson 5 rot standard, per Lesson 27 — the bar is not lowered later in the run).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-3 — CHALLENGER CH-V2-1 "P2F-3.0": P2F rebuilt at a ≥3.0% reaction band: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle per the every-3rd-cycle rule)
- **Why this challenger (priors stated, no slice pre-measured):** P2F is the book's strongest cross-year survivor (2025 +₹14,365.77 · 2026 +₹19,416.63 — the only event component positive in both years). Its 2.5% floor is validated from BELOW (Lesson 21: the [2.0%, 2.5%) complement loses at R+1) but has never been tested from ABOVE on the home 25: whether 2.5% is a floor or a peak is an open question. The one external prior is T2's pooled-50 measurement, where the 3.0% band was the best P2F variant (+₹31,719.61, expectancy +₹480.60) — a different universe (pooled home+ext), recorded as a December candidate there; this challenger asks the band question inside THIS book on the home 25 across both years. It is consistent with every lesson (Lesson 3 material, Lesson 17/21 complement logic applied from the other side) and contradicted by none. The freeze is BLIND: the [2.5%, 3.0%) slice's cross-year numbers are not measured before scoring.
- **Challenger definition (frozen):** the post-Cycle-2 incumbent book with ONLY the P2F component rebuilt by the build machinery's own `p2f_book(cands, lo_band=3.0)` on each year's calendar — identical machinery, identical R+1 lag, identical T125/S050 exits, identical RF-1 + AU-1/JU-1/SAT-14 exclusions (ASTRAL, HINDUNILVR, HINDALCO×LONG); every other component (F4, INV-LONG, N4-V3 as post-C1/C2 book law, P2F-R2, R2-LOWBAND) carried verbatim from the post-C2 books. If banked, the challenger book REPLACES the incumbent (book law: P2F band ≥3.0%) and the dropped [2.5%, 3.0%) slice is out of the book permanently under this law.
- **Controls (same pass, before any challenger number is read):** the full v2 build is re-executed in-process and ALL its controls must pass (Control A plateau assembly, F4/INV rebuilds, all nine event anchors, 2025 anchors, timing audits 0); the build's incumbent P2F sets must equal the post-C2 books' P2F rows per-trade in both years (C1/C2 touched no P2F leg); the challenger P2F sets must be exact subsets of the incumbent P2F sets (a band raise can only drop trades — any added or altered trade fails the run).
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. Standalone component comparison (P2F-3.0 vs P2F-2.5 per year), month tables and ex-top-3 per year are reported either way. A rejection is recorded as a challenger no-beat (no_beat_cycles +1) with its lesson; the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-4 — (HINDALCO × LONG) exclusion from INV-LONG: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry re-derived in Cycle 2's diagnosis at the post-C1 book and invariant since — Cycles 2/3 touched no INV-LONG leg, Lesson 16; asserted exactly at scoring):** INV-LONG × HINDALCO × LONG is the largest remaining both-years-negative slice under the standing v2 registry bar (negative in BOTH years AND combined ≤ −₹500): 2025 **4 tr / −₹1,451.18 (0 winners)** · 2026 **5 tr / −₹895.40 (1 winner)** · combined **−₹2,346.58**, expectancy −₹260.73/trade. Cross-mechanism corroboration (context only, never the basis — SAT-25 discipline): the same (name × direction) already failed inside P2F (SAT-14 exclusion) and F4 (SAT-25 exclusion); this is the third mechanism in which HINDALCO LONG independently qualifies on its own numbers.
- **Scope discipline (Lessons 11/15):** INV-LONG is LONG-only, so (mechanism × stock) is its finest unit (SAT-19 precedent). The exclusion is INV-LONG-scoped only: HINDALCO keeps earning at the R+2 lag (P2F-R2 +₹1,276.75 in 2026) and its SHORT slices elsewhere are untouched — including N4-V3 × HINDALCO × SHORT, a separate registry row judged on its own cycle.
- **Fix (frozen BEFORE scoring):** V2C4-INV-HINDALCO-EXCL — INV-LONG takes no HINDALCO signals; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-2 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹9,761.48** (= 8,310.30 + 1,451.18), 2026 **+₹199,774.33** (= 198,878.93 + 895.40), combined **+₹209,535.81** (₹9,524.36/month). Legs: (a) combined rises +₹2,346.58; (b) neither year falls; (c) neither year negative. Floor check (mandate 2026-10-31 15:17 IST, reporting): 2026 would stand ₹225.67 below its ₹200,000 floor; 2025 ₹230,238.52 below its ₹240,000 floor. Ex-top-3 per year and month tables reported at scoring.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-5 — (UNITDSPR × LONG) exclusion from INV-LONG: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–4 touched no INV-LONG × UNITDSPR leg, Lesson 16; asserted exactly at scoring):** INV-LONG × UNITDSPR × LONG — 2025 **4 tr / −₹470.49 (1 winner)** · 2026 **2 tr / −₹1,361.10 (0 winners)** · combined **−₹1,831.59**, expectancy −₹305.27/trade — negative in BOTH years, clears the standing v2 registry bar (combined ≤ −₹500). Note the year's weight is inverted vs most rows: the 2026 slice is the larger loss.
- **Scope discipline (Lessons 11/15):** INV-LONG is LONG-only, so (mechanism × stock) is its finest unit. UNITDSPR is NOT name-poisoned: its SHORT flow earns inside F4's kept population and N4-V3 (2025 UNITDSPR SHORT +₹2,199.35 in N4-V3) — all untouched. The exclusion is INV-LONG-scoped only.
- **Fix (frozen BEFORE scoring):** V2C5-INV-UNITDSPR-EXCL — INV-LONG takes no UNITDSPR signals; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-4 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹10,231.97** (= 9,761.48 + 470.49), 2026 **+₹201,135.43** (= 199,774.33 + 1,361.10), combined **+₹211,367.40** (₹9,607.61/month). Legs: (a) combined rises +₹1,831.59; (b) neither year falls; (c) neither year negative. Floor check (reporting): a bank puts **2026 over its ₹200,000 floor (+₹1,135.43)** while 2025 remains ₹229,768.03 below its floor — the per-year headline keeps both facts separate, per the mandate.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-6 — CHALLENGER CH-V2-2 "P2F-NEWS": R+1 follow of NEWS-event reactions at the ≥2.5% band: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle, aimed at 2025 per the floor mandate)
- **Why this challenger (mandate-directed seed):** the floor amendment directs challengers at the weak year, seeded from what worked in 2025 — P2F (+₹14,365.77, the strongest cross-year survivor) is the seed. P2F follows RESULTS reactions at R+1; the calendars also carry NEWS events (large orders, FDA approvals, block deals, management changes, sector policy, corporate actions) whose reaction days N4-V3 trades intraday but NO component follows at R+1. CH-V2-2 tests whether the R+1 follow — the one lag that works in both years (Cycle 2 diagnosis: R+2 is the 2025 poison) — also carries on news reactions, at P2F's living band (≥2.5%, closed cross-year by Lessons 21/28 — no new band is invented) and P2F's exits (T125/S050). Lesson 3 material (information axis); consistent with every lesson, contradicted by none. Dividend rows are ex-dates (inert) and are not candidates.
- **Challenger definition (frozen):** a NEW component, P2F-NEWS, added to the post-Cycle-5 incumbent book. Candidates: calendar rows with event_type in N4's SINGLE_NEWS classes {management_change, large_order, fda_approval, block_deal, sector_policy, pricing, corporate_action}; effective reaction date R by the calendars' own rule (reaction_date if event ≤ reaction ≤ event+7d, else event_date); reaction return = close-to-close on R from the daily series; direction = its sign; band |reaction| ≥ 2.5%; entry = R+1 first-bar open; exits by the build machinery's verbatim score_lag at lag 1 (T125/S050, 15:10 square-off); RF-1 weekend stand-aside on the entry date. NO name exclusions (the mechanism is tested clean; any slice surgery is a later cycle's question). Any candidate whose (entry date, stock, direction) exactly duplicates an incumbent P2F trade is dropped and counted (one information event is never counted twice in the union).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass; the news-candidate construction mirrors the anchored results path (same effective-date rule, same daily series) and every candidate's R is cross-checked against N4's combined event-day set for that stock (which consumes the same calendar rows); score_lag is the anchored verbatim function (P2F 48-trade anchor in-pass); timing asserted per trade (entry date is the trading day strictly after R; direction from R's close, known before entry). The flip placebo (identical entries, opposite direction) is scored and reported.
- **Banking standard (pre-registered for an ADDITIVE challenger):** the v2 cross-year gate (combined rises AND neither year falls AND neither year negative) AND the Lesson 21 full test on the component itself (standalone combined expectancy > 0 AND the component beats its flip placebo per-trade). Month tables and ex-top-3 per year reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) with its lesson; thin trade counts are disclosed, not hidden.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-7 — (HDFCBANK × SHORT) exclusion from F4: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–6 touched no F4 × HDFCBANK × SHORT leg, Lesson 16; asserted exactly at scoring):** F4 × HDFCBANK × SHORT — 2025 **5 tr / −₹1,460.11 (2 winners)** · 2026 **7 tr / −₹250.50 (3 winners)** · combined **−₹1,710.61**, expectancy −₹142.55/trade — negative in BOTH years, clears the standing v2 registry bar (combined ≤ −₹500).
- **Scope discipline (Lessons 11/15):** the exclusion is (F4 × HDFCBANK × SHORT)-scoped only. HDFCBANK SHORT inside R2-LOWBAND EARNS in 2026 (+₹836.81) and HDFCBANK LONG inside R2-LOWBAND earned in 2025 (+₹650.00) — different mechanisms, untouched; F4 keeps HDFCBANK LONG.
- **Fix (frozen BEFORE scoring):** V2C7-F4-HDFCBANK-SHORT-EXCL — F4 takes no SHORT signals on HDFCBANK; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-5 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹11,692.08** (= 10,231.97 + 1,460.11), 2026 **+₹201,385.93** (= 201,135.43 + 250.50), combined **+₹213,078.01** (₹9,685.36/month). Legs: (a) combined rises +₹1,710.61; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2026 stays over its floor; 2025 gap narrows to ₹228,307.92.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-8 — (KALYANKJIL × LONG) exclusion from F4: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–7 touched no F4 × KALYANKJIL × LONG leg, Lesson 16; asserted exactly at scoring):** F4 × KALYANKJIL × LONG — 2025 **3 tr / −₹713.82 (1 winner)** · 2026 **7 tr / −₹911.39 (2 winners)** · combined **−₹1,625.21**, expectancy −₹162.52/trade — negative in BOTH years, clears the standing v2 registry bar (combined ≤ −₹500).
- **Scope discipline (Lessons 11/15):** the exclusion is (F4 × KALYANKJIL × LONG)-scoped only. KALYANKJIL earns inside N4-V3 in both directions (2026 LONG +₹587.37, SHORT +₹1,385.50) — untouched; F4 keeps KALYANKJIL SHORT (not a both-years-negative slice); the v1 INV-LONG × KALYANKJIL exclusion (SAT-28) is a different mechanism and stands separately.
- **Fix (frozen BEFORE scoring):** V2C8-F4-KALYANKJIL-LONG-EXCL — F4 takes no LONG signals on KALYANKJIL; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-7 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹12,405.90** (= 11,692.08 + 713.82), 2026 **+₹202,297.32** (= 201,385.93 + 911.39), combined **+₹214,703.22** (₹9,759.24/month). Legs: (a) combined rises +₹1,625.21; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹227,594.10; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-9 — CHALLENGER CH-V2-3 "N4-HIFLOOR": N4-V3 rebuilt with the 09:30 trigger floor raised ≥1.0% → ≥1.5%: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** N4-V3 carries the book's largest remaining both-years-negative slice cluster (HINDALCO-SHORT −₹1,475.56 · HINDZINC-LONG −₹1,444.04 · UNITDSPR-LONG −₹1,312.80 · RECLTD-LONG −₹1,062.88 · WIPRO-SHORT −₹574.20) and its post-C1/C2 component line is still ≈ ₹0 in 2025 (−₹502.80). The registry treats those slices one at a time; this challenger asks the population question at once: **are N4's cross-year losses concentrated in its weakest triggers — the [1.0%, 1.5%) move slice?** Lesson 17 validated the ≥1.0% floor from BELOW (the [0.75%, 1.0%) complement failed in 2026); the territory above has never been isolated cross-year (the SAT-31 complement-from-above pattern, applied to N4's floor). The freeze is blind: the [1.0%, 1.5%) slice's cross-year numbers are not measured before scoring.
- **Challenger definition (frozen):** the post-Cycle-8 incumbent book with ONLY the N4-V3 component rebuilt at trigger floor ≥1.5% — identical machinery (the build's n4_raw with the floor parameterised; results + SINGLE_NEWS combined days, 09:25-close move vs prev close, entry 09:30 close at 09:35), identical SAT-15 exits (T150/S080 replay), and the FULL current N4 book law applied identically (RF-1; no ASTRAL; no TVSMOTOR LONG; no OIL LONG; no GLENMARK SHORT per V2C1; no BDL SHORT per V2C2). Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: N4-V3 trigger floor ≥1.5%) and the [1.0%, 1.5%) population is out permanently under that law.
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass; the parameterised n4 copy at floor 1.0 must reproduce the SAT-15 dump per-trade (the build's own anchor, re-asserted on the copy) and, after book filters + v2 law, must equal the post-C8 books' N4-V3 rows per-trade in BOTH years; the challenger set must be an exact subset of the incumbent N4 set (a floor raise only drops trades — any added or altered trade fails the run).
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. Standalone component comparison (N4-1.5 vs N4-1.0 per year), the dropped slice per year, month tables and ex-top-3 per year are reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) with its lesson; the incumbent and the registry continue unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-10 — (HINDALCO × SHORT) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–9 touched no N4-V3 × HINDALCO × SHORT leg, Lesson 16; asserted exactly at scoring):** N4-V3 × HINDALCO × SHORT — 2025 **1 tr / −₹568.20 (0 winners)** · 2026 **1 tr / −₹907.36 (0 winners)** · combined **−₹1,475.56**, expectancy −₹737.78/trade — negative in BOTH years at 0 winners in both, clears the standing v2 registry bar (combined ≤ −₹500). Thin-sample caveat disclosed (2 trades; the SAT-14/17/21 precedent class — the cross-year 0-winner pattern in two independent years is the evidence, and it is stated as such).
- **Scope discipline (Lessons 11/15):** the exclusion is (N4-V3 × HINDALCO × SHORT)-scoped only. HINDALCO LONG is already excluded inside P2F (SAT-14), F4 (SAT-25) and INV-LONG (V2C4) on those mechanisms' own numbers; its P2F-R2 LONG keeps earning (+₹1,276.75) — untouched. Each mechanism's slice stands on its own record.
- **Fix (frozen BEFORE scoring):** V2C10-N4-HINDALCO-SHORT-EXCL — N4-V3 takes no SHORT signals on HINDALCO; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-8 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹12,974.10** (= 12,405.90 + 568.20), 2026 **+₹203,204.68** (= 202,297.32 + 907.36), combined **+₹216,178.78** (₹9,826.31/month). Legs: (a) combined rises +₹1,475.56; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹227,025.90; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-11 — (HINDZINC × LONG) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–10 touched no N4-V3 × HINDZINC × LONG leg, Lesson 16; asserted exactly at scoring):** N4-V3 × HINDZINC × LONG — 2025 **1 tr / −₹400.80 (0 winners)** · 2026 **2 tr / −₹1,043.24 (0 winners)** · combined **−₹1,444.04**, expectancy −₹481.35/trade — negative in BOTH years at 0 winners in both, clears the standing v2 registry bar (combined ≤ −₹500). Thin-sample caveat disclosed (3 trades; evidence class as in V2-CYCLE-10). Context (SAT-20 record): HINDZINC loses inside four mechanisms and earns in the fifth (P2F-R2 +₹812.50) — each slice qualifies on its own numbers or stays; the INV-LONG slice was banked in v1 (SAT-20), this is N4-V3's own slice.
- **Scope discipline (Lessons 11/15):** the exclusion is (N4-V3 × HINDZINC × LONG)-scoped only; P2F-R2's earning HINDZINC LONG and every other mechanism's HINDZINC trades are untouched.
- **Fix (frozen BEFORE scoring):** V2C11-N4-HINDZINC-LONG-EXCL — N4-V3 takes no LONG signals on HINDZINC; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-10 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹13,374.90** (= 12,974.10 + 400.80), 2026 **+₹204,247.92** (= 203,204.68 + 1,043.24), combined **+₹217,622.82** (₹9,891.95/month). Legs: (a) combined rises +₹1,444.04; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹226,625.10; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-12 — CHALLENGER CH-V2-4 "F4-S110": F4 rebuilt with stop −0.95% → −1.10% (target +1.50% unchanged): FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** F4's stop ladder was climbed one step in v1 (S080 → S095, SAT-10, banked) and the next step was refused in SAT-11 on a DIAGNOSIS ONLY — the excursion support test failed on the August leg under v1's all-months-green gate (2026 window alone: 155 stop exits, first passage at −1.10% = 1 rescue / 126 deeper / 28 neither, rough swing +₹6,686.35 with August −₹1,168.73). The family was closed "on this window" — and under the v2 method a single-window closure is a hypothesis, not a verdict (Lesson 27's pattern): 2025 is a full unfitted year whose F4 stop population has never been diagnosed, and the v2 gate judges year totals, not one month's shape. This challenger scores the step exactly, on both years, with the audited rebuild — the estimate is not the score (Lesson 4, SAT-10 addendum).
- **Challenger definition (frozen):** the post-Cycle-11 incumbent book with ONLY the F4 component rebuilt by the validation machinery's collect2 at (target 1.50%, stop 1.10%), filtered by f4_keep verbatim, with the FULL current F4 book law applied identically (RF-1; setup3 out; first-signal-only; EXCL_DIR; no GLENMARK SHORT per V2C1; no HDFCBANK SHORT per V2C7; no KALYANKJIL LONG per V2C8). Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: F4 exits T150/S110).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass (including Control B2: the S095 rebuild == the frozen F4 set); the incumbent books' F4 rows must equal the build's F4 sets minus the three v2-law slices, per-trade, in both years; the S110 builds' timing-audit deltas must show 0 violations; the challenger F4 ENTRY set (date, stock, dir, entry_time) must equal the incumbent F4 entry set in both years (an exit change cannot create or destroy entries in the kept population — any mismatch fails the run and is diagnosed, not scored past).
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. Component comparison (F4-S110 vs F4-S095 per year), month tables and ex-top-3 per year reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) and closes the F4 stop family CROSS-YEAR at S095; the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-13 — (UNITDSPR × LONG) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–12 touched no N4-V3 × UNITDSPR × LONG leg, Lesson 16; asserted exactly at scoring):** N4-V3 × UNITDSPR × LONG — 2025 **1 tr / −₹1,212.80 (0 winners)** · 2026 **1 tr / −₹100.00 (0 winners)** · combined **−₹1,312.80**, expectancy −₹656.40/trade — negative in BOTH years at 0 winners in both, clears the standing v2 registry bar (combined ≤ −₹500). Thin-sample caveat disclosed (2 trades; evidence class as in V2-CYCLE-10/11).
- **Scope discipline (Lessons 11/15):** the exclusion is (N4-V3 × UNITDSPR × LONG)-scoped only. UNITDSPR's SHORT flow is one of N4-V3's own 2025 winners (+₹2,199.35) and keeps earning there and in F4 — untouched; the v2 INV-LONG × UNITDSPR exclusion (V2C5) is a different mechanism and stands separately.
- **Fix (frozen BEFORE scoring):** V2C13-N4-UNITDSPR-LONG-EXCL — N4-V3 takes no LONG signals on UNITDSPR; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-11 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹14,587.70** (= 13,374.90 + 1,212.80), 2026 **+₹204,347.92** (= 204,247.92 + 100.00), combined **+₹218,935.62** (₹9,951.62/month). Legs: (a) combined rises +₹1,312.80; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹225,412.30; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-14 — (RECLTD × LONG) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–13 touched no N4-V3 × RECLTD × LONG leg, Lesson 16; asserted exactly at scoring):** N4-V3 × RECLTD × LONG — 2025 **2 tr / −₹730.60 (0 winners)** · 2026 **1 tr / −₹332.28 (0 winners)** · combined **−₹1,062.88**, expectancy −₹354.29/trade — negative in BOTH years at 0 winners in both, clears the standing v2 registry bar (combined ≤ −₹500). Thin-sample caveat disclosed (3 trades; evidence class as in V2-CYCLE-10/11/13).
- **Scope discipline (Lessons 11/15):** the exclusion is (N4-V3 × RECLTD × LONG)-scoped only. RECLTD SHORT inside N4-V3 earns in 2026 (+₹574.32) — untouched; RECLTD's small earners in INV-LONG (+₹0.24), P2F (+₹228.37) and F4 LONG (+₹949.99) all stand (the SAT-30 pattern).
- **Fix (frozen BEFORE scoring):** V2C14-N4-RECLTD-LONG-EXCL — N4-V3 takes no LONG signals on RECLTD; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-13 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹15,318.30** (= 14,587.70 + 730.60), 2026 **+₹204,680.20** (= 204,347.92 + 332.28), combined **+₹219,998.50** (₹9,999.93/month). Legs: (a) combined rises +₹1,062.88; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹224,681.70; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-15 — CHALLENGER CH-V2-5 "N4-RESULTS-ONLY": N4-V3 rebuilt without its news-only-day trades: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** N4-V3's trigger set is a UNION of two information classes — results reaction days and news reaction days (management changes, large orders, FDA approvals, block deals, sector policy, corporate actions). Lesson 29 proved the classes behave differently at R+1 (results persist, news does not); whether they behave differently at N4's own same-day lag has never been measured on either window. If N4's news-only-day trades drag in both years, the component is carrying a dead class; if they earn, the union is certified. The freeze is blind: the news-only slice's numbers are not measured before scoring.
- **Challenger definition (frozen):** the post-Cycle-14 incumbent book with ONLY the N4-V3 component rebuilt from the same machinery (parameterised copy, floor ≥1.0%, SAT-15 exits T150/S080) with each trade tagged by its event-day class — RESULTS if the day is a results reaction day for that stock (a day in both classes counts as results), NEWS-ONLY if it is in the SINGLE_NEWS set only — and with all NEWS-ONLY trades dropped; the FULL current N4 book law then applied identically (RF-1; no ASTRAL; no TVSMOTOR LONG; no OIL LONG; no GLENMARK SHORT; no BDL SHORT; no HINDALCO SHORT; no HINDZINC LONG; no UNITDSPR LONG; no RECLTD LONG). Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: N4-V3 trades results reaction days only).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass; the parameterised copy at the full combined set must reproduce the SAT-15 dump per-trade (2026) and, after book filters + full v2 law, must equal the post-C14 books' N4-V3 rows per-trade in BOTH years (the Cycle 9 anchor pattern, extended with the law added since); the challenger set must be an exact subset of the incumbent N4 set in both years.
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. The news-only slice per year (the diagnosis this score reveals), component comparison, month tables and ex-top-3 per year are reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) with its lesson; the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-16 — (WIPRO × SHORT) exclusion from N4-V3: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–15 touched no N4-V3 × WIPRO × SHORT leg, Lesson 16; asserted exactly at scoring):** N4-V3 × WIPRO × SHORT — 2025 **2 tr / −₹112.80 (1 winner)** · 2026 **3 tr / −₹461.40 (0 winners)** · combined **−₹574.20**, expectancy −₹114.84/trade — negative in BOTH years, clears the standing v2 registry bar (combined ≤ −₹500). This is the smallest slice banked under the bar so far; the bar is the standard and it is not moved in either direction.
- **Scope discipline (Lessons 11/15):** the exclusion is (N4-V3 × WIPRO × SHORT)-scoped only. WIPRO LONG inside N4-V3 does NOT qualify and stays (2025 −₹536.24, but 2026 +₹36.18 — not negative in both years), and WIPRO earns inside the P2F family in 2025 (P2F-R2 LONG +₹163.34, SHORT +₹199.06) — all untouched.
- **Fix (frozen BEFORE scoring):** V2C16-N4-WIPRO-SHORT-EXCL — N4-V3 takes no SHORT signals on WIPRO; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-14 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹15,431.10** (= 15,318.30 + 112.80), 2026 **+₹205,141.60** (= 204,680.20 + 461.40), combined **+₹220,572.70** (₹10,026.03/month). Legs: (a) combined rises +₹574.20; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹224,568.90; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-17 — (KALYANKJIL × LONG) exclusion from P2F-R2: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–16 touched no P2F-R2 × KALYANKJIL × LONG leg, Lesson 16; asserted exactly at scoring):** P2F-R2 × KALYANKJIL × LONG — 2025 **1 tr / −₹291.22 (0 winners)** · 2026 **1 tr / −₹256.95 (0 winners)** · combined **−₹548.17**, expectancy −₹274.09/trade — negative in BOTH years at 0 winners in both, clears the standing v2 registry bar (combined ≤ −₹500). Thin-sample caveat disclosed (2 trades; evidence class as in V2-CYCLE-10/11/13). This is also the ONLY both-years-negative slice inside P2F-R2 (Cycle 2 diagnosis) — the component's 2025 loss is otherwise diffuse/regime (the R+2 lag finding), and this exclusion does not pretend to fix that.
- **Scope discipline (Lessons 11/15):** the exclusion is (P2F-R2 × KALYANKJIL × LONG)-scoped only. KALYANKJIL SHORT inside P2F-R2 earns in both years (2025 +₹628.75, 2026 +₹55.25) and KALYANKJIL earns inside N4-V3 in both directions — all untouched; the same (name × direction) already stands excluded inside F4 (V2C8) and INV-LONG (SAT-28) on those mechanisms' own numbers, each standing separately.
- **Fix (frozen BEFORE scoring):** V2C17-R2-KALYANKJIL-LONG-EXCL — P2F-R2 takes no LONG signals on KALYANKJIL; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-16 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹15,722.32** (= 15,431.10 + 291.22), 2026 **+₹205,398.55** (= 205,141.60 + 256.95), combined **+₹221,120.87** (₹10,050.95/month). Legs: (a) combined rises +₹548.17; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹224,277.68; 2026 stays over its floor.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-18 — CHALLENGER CH-V2-6 "P2F-EXITS": P2F rebuilt at T150/S080 (from T125/S050): FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** T150/S080 is the one exit pair with a positive controlled prior on a reaction population — the SAT-15 N4 rebuild gained +₹9,483.45 (2026) moving reaction-day entries from T125/S050 to T150/S080. Whether that medicine transfers to the OTHER reaction population (P2F's R+1 entries) has never been isolated on either window: v1's SAT-5 closure of "P2F exit rebuild" rested on CH-1, which changed the band AND the stop (S065) inside a different, profile-gated system — the clean pair-swap on P2F itself was never run (the Lesson 31 labelling discipline: a closure by association is a hypothesis). Lesson 4's standing warning applies in full: exit medicine is population-specific, so the prior is a question, not an expectation. The freeze is blind.
- **Challenger definition (frozen):** the post-Cycle-17 incumbent book with ONLY the P2F component rebuilt by a parameterised copy of the build's score_lag at (target 1.50%, stop 0.80%) — identical candidates (results reactions, both calendars), identical ≥2.5% band, identical R+1 lag and 09:15-open entries, identical RF-1 + exclusions (ASTRAL, HINDUNILVR, HINDALCO×LONG). Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: P2F exits T150/S080).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass; the parameterised copy at (1.25, 0.50) must reproduce the build's incumbent P2F sets per-trade in BOTH years, and those sets must equal the post-C17 books' P2F rows (no v2 cycle has touched a P2F leg); the challenger's ENTRY set (date, stock, dir, entry_time) must equal the incumbent P2F entry set in both years (an exit change cannot create or destroy entries).
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. Component comparison per year, month tables and ex-top-3 per year reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) and closes the P2F exit question on exact cross-year evidence; the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-19 — (TATASTEEL × LONG) exclusion from INV-LONG: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter)
- **Diagnosis (registry from Cycle 2's diagnosis; invariant since — Cycles 2–18 touched no INV-LONG × TATASTEEL leg, Lesson 16; asserted exactly at scoring):** INV-LONG × TATASTEEL × LONG — 2025 **8 tr / −₹301.79 (3 winners)** · 2026 **4 tr / −₹217.04 (1 winner)** · combined **−₹518.83**, expectancy −₹43.24/trade — negative in BOTH years, clears the standing v2 registry bar (combined ≤ −₹500) by ₹18.83, the thinnest margin of the run. The bar is the standard: it clears, it is judged; the margin is disclosed, not rounded away.
- **Scope discipline (Lessons 11/15):** the exclusion is INV-LONG-scoped only (INV-LONG is LONG-only; (mechanism × stock) is its finest unit). TATASTEEL's other slices do not qualify and stay: F4 LONG excluded in v1 on its own record (SAT-26) is a different mechanism; TATASTEEL SHORT earns inside P2F-R2 (+₹219.38, 2026); its N4-V3 slices are sub-bar in both directions.
- **Fix (frozen BEFORE scoring):** V2C19-INV-TATASTEEL-EXCL — INV-LONG takes no TATASTEEL signals; everything else in the book is frozen verbatim. Deletion-only on the post-Cycle-17 incumbent books; the deleted set is asserted trade-by-trade at scoring against the diagnosis slice above.
- **Gate (v2 charter, pre-registered arithmetic):** post-fix expected 2025 **+₹16,024.11** (= 15,722.32 + 301.79), 2026 **+₹205,615.59** (= 205,398.55 + 217.04), combined **+₹221,639.70** (₹10,074.53/month). Legs: (a) combined rises +₹518.83; (b) neither year falls; (c) neither year negative. Floor check (reporting): 2025 gap narrows to ₹223,975.89; 2026 stays over its floor. **Registry note (pre-registered):** this is the LAST slice at the standing bar — after this cycle the both-years-negative registry is empty (the largest remaining rows, P2F × WIPRO × LONG −₹496.67 and below, sit under the bar and stay, per Lesson 25's discipline: the bar is not lowered at the finish line).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2-CYCLE-20 — CHALLENGER CH-V2-7 "F4-ROUND2": F4's second-signal (round-2) legs restored: FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** SAT-6 banked first-signal-only for F4 on the 2026 window (the round-2 population then measured 70 tr / −₹11.83 — a nominal, distributional bank). That verdict is single-window: the round-2 population's 2025 value has never been measured, and under the v2 method it is a hypothesis, not a verdict (Lesson 27 pattern). This is also the last untested F4 population question — the band is closed on both sides and in mirror (Lessons 18/21 line), the exits are closed cross-year (Lessons 31/33 line via SAT-12), the slice registry for F4 is empty at the bar. Disclosed prior: at the current law the 2026 round-2 delta is expected to be ≈ ₹0 (SAT-6's −₹11.83 was measured under an earlier, thinner law; the v2 law removes three more slice families from the population) — the challenger is run because the cadence requires a challenger and this question is genuinely open on 2025, not because a bank is expected.
- **Challenger definition (frozen):** the post-Cycle-19 incumbent book with F4's round-2 legs RESTORED: from the audited S095 raw populations (the build's own collect2 runs for both years), the legs that f4_keep rejects SOLELY for their round — isolated black-box: a raw leg belongs to the restoration set iff f4_keep(leg) is false and f4_keep(leg with its round field set to 1) is true — normalised and passed through the FULL current F4 book law (RF-1 and the v1 law are inside f4_keep's equivalence to the plateau set; the v2 additions — no GLENMARK SHORT, no HDFCBANK SHORT, no KALYANKJIL LONG — applied on top), then added to the incumbent book as F4 trades. Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: F4 takes first AND second signals per stock-day).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass (incl. B1/B2 F4 anchors and the 2025 F4 anchor); the restoration set must be non-empty in both years, disjoint from the kept set, and every member must carry round ≠ 1 in the raw population (any failure stops the run for diagnosis, not scoring); the incumbent books' F4 rows must equal the build's kept sets minus the v2-law slices (the Cycle 12 anchor); the raw populations' timing audits in-pass must show 0 violations (the build's own audit deltas for these exact collect2 runs).
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. The restoration set's standalone per year, month tables and ex-top-3 per year are reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) and closes the round-2 question CROSS-YEAR (first-signal-only stands on both windows); the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.
- **Construction note (same cycle, before scoring):** the freeze's parenthetical named the round field; probing the audited machinery shows the round-2 encoding field is `leg` (values direct/round2; `round` is its numeric mirror and is not read by f4_keep). The isolation is therefore the leg-flip: a raw leg is in the restoration set iff f4_keep(leg) is false and f4_keep(leg with leg set to "direct") is true. The DEFINITION is unchanged — legs rejected solely for being round-2 legs (probe: 66 round2 legs in the 2026 raw population; 46 pass every other frozen condition; the other 20 are also blocked by other rules, e.g. setup3, and stay out). All anchors and the gate are as frozen.

## V2-CYCLE-21 — CHALLENGER CH-V2-8 "R2-EXITS": P2F-R2 rebuilt at T150/S080 (from T125/S050): FROZEN BEFORE SCORING (2026-10-31, v2 cross-year charter; challenger cycle)
- **Why this challenger:** P2F-R2 is the book's sickest component (2025 −₹5,682.76 at component level after Cycle 17; 2026 +₹14,635.43) and its disease was diagnosed as the R+2 lag in a trending year (Cycle 2) — but its EXIT pair has never been tested on its own population. Lesson 33 forbids assuming the pair verdict transfers between populations (it failed on R+1 after paying on same-day); by the same discipline, T125/S050's correctness on the R+2 population is an untested hypothesis, and the wider pair is the one candidate medicine with a positive prior on a sibling population. If the R+2 population's winners need more room and its losers are stop-driven in 2025's chop, the swap is the component's repair; if not, the component's exits close and its 2025 loss stands as pure lag/regime. The freeze is blind.
- **Challenger definition (frozen):** the post-Cycle-19 incumbent book with ONLY the P2F-R2 component rebuilt by the parameterised score_lag copy at lag 2 and (target 1.50%, stop 0.80%) — identical candidates (results reactions ≥2.5%, both calendars), identical RF-1 + frozen exclusions (ASTRAL, HINDUNILVR out at the frozen stage; TVSMOTOR LONG out at the book stage) and the v2 addition (no KALYANKJIL LONG, per V2C17). Every other component carried verbatim. If banked, the challenger book replaces the incumbent (book law: P2F-R2 exits T150/S080).
- **Controls (same pass, before any challenger number is read):** the full v2 build re-executes in-process and ALL controls must pass (incl. the P2F-R2 candidate/frozen/book anchors); the parameterised copy at (1.25, 0.50) must reproduce the build's frozen R2 sets per-trade in BOTH years, and the build's R2 book sets minus the KALYANKJIL-LONG law must equal the post-C19 books' P2F-R2 rows; the challenger's ENTRY set (date, stock, dir, entry_time) must equal the incumbent R2 entry set in both years.
- **Gate (v2 charter — the only banking rule):** bank iff (a) combined total rises AND (b) neither year's total falls AND (c) neither year is negative at book level, scored on both windows in the same run. Component comparison per year, month tables and ex-top-3 per year reported either way. A rejection is a challenger no-beat (no_beat_cycles +1) and closes the P2F-R2 exit question on exact cross-year evidence; the incumbent continues unchanged.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## REGIME-CLASSIFIER-1 — FROZEN BEFORE ANY REGIME SCORING (2026-10-31, mandate 2: regime completeness + consistency band)
- **Definition (frozen, causal — every input known at the prior close):** for each trading day d, let PC = NIFTY close on the prior trading day, M(d) = the 50-day mean of NIFTY closes strictly before d (the audited machinery's own ma50 convention, spot-checked in the validation), and S(d) = M(d) − M(d−5) (the 50DMA's 5-day slope, also strictly prior). Labels:
  - **UP**: PC > M(d) AND S(d) ≥ 0 (price above a non-falling trend line)
  - **DOWN**: PC ≤ M(d) AND S(d) ≤ 0 (price at/below a non-rising trend line)
  - **FLAT**: everything else (price and slope disagree — transition/chop days)
  A day whose M(d) or M(d−5) is not computable is UNCLASSIFIED and excluded from cell reporting (none is expected: the data root carries Q4-2024 lookback).
- **Causality discipline:** the label for day d uses closes up to d−1 only — no same-day open/high/low/close enters it. Cross-check asserted at first use: for every day in both windows, (PC ≤ M(d)) must equal the audited machinery's below50(d) exactly.
- **Use (mandate 2):** every cycle from Cycle 22 reports book P&L by (cell × year) with trade counts; a cell negative in either year is a named weakness ranked like a red month; the challenger cadence targets the weakest cell (DOWN → SHORT mechanisms, UP → LONG, FLAT → event-driven/fade). The classifier is never re-tuned to improve a cell — changing the classifier after seeing cell P&L would be regime-fitting, the exact failure Lesson 26 names. If the labels prove uninformative, that is reported as evidence, not repaired by relabelling.
- Basis: NIFTY daily closes from data/full_hist (the same series the machinery trades on); labels apply to the book's trade dates in Jan–Dec 2025 + Jan–Oct 2026.

## V2 CYCLE 22 — CHALLENGER CH-V2-9 "INV-ABOVE" — FROZEN BEFORE SCORING (2026-10-31; regime-targeted per mandate 2)
- **Named weakness (mandate 2, objective (a)):** the UP cell — 2025 **−₹4,665.03** (63 tr) vs 2026 +₹12,282.57 (22 tr): the book has no uptrend earner in the year that had 128 UP days. (FLAT × 2025 −₹872.72 is the second gap.) The mandate's sleeve rule (UP → LONG mechanisms) and the floor mandate's seed rule (build from what worked in 2025 — INV-LONG +₹7,642.52 was a 2025 survivor) both point at the same test: **does the INV chain pool earn on ABOVE-trend days?**
- **Challenger (additive component, swap-nothing):** a new component "INV-ABOVE" = the audited build_inv machinery VERBATIM (PLAIN chains, T125/S050, p2 filters round ≤ 2 + entry < 10:30 + ADR ≥ 3.0, LONG only, RF-1 weekend stand-aside, base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER, KALYANKJIL}) with ONE change: the regime gate is g1 (prior close > 50DMA — above-trend days) instead of cond_inv1 (at/below). The v2 INV mechanism law {no HINDALCO, no UNITDSPR, no TATASTEEL} applies to the mirror as to the original (mechanism-scoped law, Lesson 11). Its trades fall only on g1 days = UP or FLAT cells under REGIME-CLASSIFIER-1 — an UP/FLAT sleeve by construction.
- **Anchors (asserted in-pass):** build controls ALL PASS; the identical code path with gate = cond_inv1 reproduces build_inv's sets per-trade in BOTH years, and minus the v2-law names equals the incumbent book's INV-LONG rows exactly; mirror rows are day-disjoint from incumbent INV rows (g1 vs not-g1); timing = the audited run_chain construction (signal at candle close, entry next candle's open — the same machinery the INV anchor rebuilds prove).
- **Decision (pre-registered, the additive-challenger standard set at Cycle 6):** bank iff (i) the cross-year gate passes (combined rises AND neither year falls AND neither year negative) AND (ii) the component's combined expectancy > 0 AND (iii) it beats its flip placebo per-trade — the placebo being the SHORT side of the identical gated population (same days, filters, exclusions and law).
- **Prior, disclosed as weak (Lesson 18):** joint states do not mirror — the v1 F4-MIRROR died and the v1 above-trend INV variants were never the earners. This test exists because mandate 2 makes the UP cell a named objective and INV is the only 2025-proven LONG machinery; a rejection closes the mirror idea for the INV family as well, and at no_beat = 3 terminates v2 as SATURATED-V2 with the regime gaps (UP × 2025, FLAT × 2025) reported as the proven ceiling's shape.
- Regime reporting in the score: challenger standalone by cell × year; if banked, the new book's cells × year and month spread.

## V2 CYCLE 23 — FREEZE (2026-10-31)
- **Diagnosis (regime cells, C22 book; labels REGIME-CLASSIFIER-1):** (R2-LOWBAND × UP) = 2025 9 tr **−₹3,506.17** / 2026 4 tr **−₹22.58** — negative in BOTH years, combined **−₹3,528.75**. It is the residual that keeps the UP × 2025 cell negative (−₹1,301.36): the R+2 family's second UP bleed (P2F-R2 × UP cannot be cut — its 2026 UP cell earns +₹2,389.00, so the gate forbids it).
- **Cell-exclusion bar (pre-registered here, the slice bar's shape at the cell unit mandate 2 created):** a (component × regime cell) exclusion qualifies iff the pair is negative in BOTH years AND combined ≤ −₹500. This pair qualifies (−₹3,506.17 / −₹22.58 / −₹3,528.75). Thinness disclosed: 13 trades total, and 2026's cell is nearly zero (−₹22.58 / 4 tr) — the change is nearly free in 2026; all its value is 2025. A regime stand-aside keyed to the frozen causal classifier is mechanism law of the same kind this book already runs on (F4 and INV-LONG trade only on below50 days) — it is not a date filter and carries no month parameter.
- **The one change:** R2-LOWBAND stands aside on UP-labelled days, both windows (deletes exactly its UP rows: 9 in 2025, 4 in 2026 — asserted in-pass against this freeze). Nothing else changes.
- **Anchors:** build controls ALL PASS in-pass (labels and audit come from the same machinery); incumbent == state (C22 books); deleted set == the frozen set exactly (count + net per year); classifier price leg asserted == below50 on all window days.
- **Decision:** the cross-year gate on totals (combined rises AND neither year falls AND neither year negative). Expected if the diagnosis holds: 2025 +₹3,506.17, 2026 +₹22.58 — and the UP × 2025 cell turns positive (+₹2,204.81), completing mandate objective (a): every regime cell positive in both years.

## V2 CYCLE 24 — FREEZE (2026-10-31)
- **Diagnosis (regime cells, C23 book; labels REGIME-CLASSIFIER-1; evidence v2_out/v2_cycle24_diag.json):** (INV-LONG × FLAT) = 2025 9 tr **−₹2,739.25** / 2026 11 tr **−₹2,600.72** — negative in BOTH years, combined **−₹5,339.97**, qualifying under the cell-exclusion bar pre-registered at Cycle 23 (both years negative AND combined ≤ −₹500). A full (component × cell) scan of the C23 book shows it is the **only remaining both-years-negative pair**. Queued at Cycle 23 as this cycle's fix.
- **The one change:** INV-LONG stands aside on FLAT-labelled days, both windows (deletes exactly its FLAT rows: 9 in 2025, 11 in 2026 — asserted in-pass against this freeze). Nothing else changes. A regime stand-aside keyed to the frozen causal classifier — mechanism law of the same kind the book already runs (F4 and INV-LONG trade only on below50 days); not a date filter, no month parameter.
- **Cell guard (mandate 2 objective (a), pre-registered for every v2 cycle from here):** a bank that flips any regime cell negative in either year is a REJECT even if the totals gate passes. Here the FLAT cells are positive in both years (2025 +₹973.32 / 2026 +₹4,762.18) and removing a negative slice can only strengthen them (expected → +₹3,712.57 / +₹7,362.90); all other cells are untouched by construction. The guard is asserted in-pass regardless.
- **Anchors:** build controls ALL PASS in-pass; incumbent == state (C23 books); deleted set == the frozen set exactly (count + net per year); classifier price leg asserted == below50 on all window days.
- **Decision:** the cross-year gate on totals (combined rises AND neither year falls AND neither year negative) AND the cell guard. Expected if the diagnosis holds: 2025 +₹2,739.25 → +₹27,479.24, 2026 +₹2,600.72 → +₹211,588.10, combined +₹239,067.34.

## V2 CYCLE 25 — CHALLENGER CH-V2-10 "INV-LATE" — FROZEN BEFORE SCORING (2026-10-31; growth challenger, seeded from 2025's proven INV family)
- **Why this challenger:** deletions are exhausted at every unit (name × direction registry empty at C19; (component × cell) pairs empty at C24) — the 2025 floor gap (₹212,520.76) can now only be closed by ADDING earning material. The floor mandate's seed rule points at what worked in 2025, and the INV family is its proven LONG machinery (INV-LONG +₹7,642.52 in 2025 at build; INV-ABOVE banked at C22). The cycle diagnosis (v2_out/v2_cycle24_diag.json, counts only — no P&L read) measured the machinery's own discarded populations: the p2 earliness filter (entry < 10:30) discards a large, never-scored population — below-trend, round ≤ 2, entry ≥ 10:30: **86 rows (2025) / 93 rows (2026)** after ADR ≥ 3.0, RF-1, base exclusions and the v2 INV law. This challenger asks whether the earliness leg is load-bearing or merely inherited: its complement is the test.
- **Challenger (additive component "INV-LATE", swap-nothing):** the audited INV chain machinery VERBATIM (PLAIN chains, T125/S050, ADR ≥ 3.0, LONG only, RF-1 weekend stand-aside, base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER, KALYANKJIL}, v2 INV law {no HINDALCO, no UNITDSPR, no TATASTEEL}, below-trend gate cond_inv1 — INV-LONG's own gate) with ONE change: the entry-time leg of the p2 filters reads **entry_time ≥ 10:30** instead of < 10:30. Round ≤ 2 is kept. The population is the exact complement of INV-LONG's entry-time leg — disjoint from INV-LONG's rows by construction (asserted in-pass).
- **Anchors (asserted in-pass):** build controls ALL PASS; the identical code path with the incumbent entry leg (round ≤ 2, entry < 10:30, law = ∅) reproduces build_inv per-trade in BOTH years, and minus the v2-law names equals the incumbent book's INV-LONG rows exactly (the C22 anchor pattern); timing = the audited run_chain construction.
- **Decision (pre-registered, the additive-challenger standard set at Cycle 6, plus the C24 cell guard):** bank iff (i) the cross-year gate passes (combined rises AND neither year falls AND neither year negative) AND (ii) the component's combined expectancy > 0 AND (iii) it beats its flip placebo per-trade — the placebo being the SHORT side of the identical gated late population (same days, filters, exclusions and law) AND (iv) no regime cell flips negative in either year in the resulting book. Challenger trades fall on below50 days (DOWN/FLAT cells) by construction.
- **Prior, disclosed honestly:** the earliness filter came out of the original INV tuning — its kept side is a proven earner in both years, which is weak evidence the filter is load-bearing and the complement is the spent part of the day. This test exists because the complement was never scored cross-year and the population is large (179 rows); a rejection closes the late-entry axis for the below-trend gate on exact evidence, the same way Cycle 20 closed F4's second-signal legs.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2 CYCLE 26 — CHALLENGER CH-V2-11 "INV-ABOVE-LATE" — FROZEN BEFORE SCORING (2026-10-31; growth challenger, INV family)
- **Why this challenger:** Cycle 25 closed the late-entry axis on the below-trend gate (the complement earns in 2026, bills 2025 — Lesson 36). The above-trend gate is a different population with a different composition (the C22 sleeve's days are UP/FLAT-cell days, and its kept side earns in both years at +₹30.65 / +₹93.03 per trade); whether its late complement behaves the same way is a separate empirical question, and the diagnosis counted the population: above-trend, round ≤ 2, entry ≥ 10:30 = **72 rows (2025) / 27 rows (2026)** after ADR ≥ 3.0, RF-1, base exclusions and the v2 INV law. One axis remains untested on this gate; this cycle tests it.
- **Challenger (additive component "INV-ABOVE-LATE", swap-nothing):** the audited INV chain machinery VERBATIM (PLAIN chains, T125/S050, ADR ≥ 3.0, LONG only, RF-1 weekend stand-aside, base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER, KALYANKJIL}, v2 INV law {no HINDALCO, no UNITDSPR, no TATASTEEL}, above-trend gate g1 — INV-ABOVE's own gate) with ONE change relative to INV-ABOVE: the entry-time leg reads **entry_time ≥ 10:30** instead of < 10:30. Round ≤ 2 kept. Disjoint from INV-ABOVE's rows by construction (asserted in-pass).
- **Anchors (asserted in-pass):** build controls ALL PASS; the identical code path with the incumbent entry leg (round ≤ 2, entry < 10:30, gate g1, v2 law applied) equals the incumbent book's INV-ABOVE rows exactly in both years (the C22 construction); late population counts == the frozen counts above.
- **Decision (Cycle-6 additive standard + C24 cell guard):** bank iff (i) the cross-year gate passes AND (ii) combined expectancy > 0 AND (iii) beats the flip placebo (SHORT side of the identical late above-trend population) per-trade AND (iv) no regime cell flips negative in either year. Challenger trades fall on g1 days (UP/FLAT cells) by construction.
- **Prior, disclosed honestly:** Lesson 36 is the prior — on the sibling gate the late complement was year-flipping regime rent. A rejection here closes the late-entry axis for the whole INV family; a bank would show the two gates' late populations genuinely differ.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V2 CYCLE 27 — CHALLENGER CH-V2-12 "P2F-NEWS" — FROZEN BEFORE SCORING (2026-10-31; growth challenger, P2F family, new event class)
- **Why this challenger:** the P2F family is the book's strongest cross-year seed (2025 +₹14,365.77 at build — the largest single 2025 component — and positive in every band bucket in both years, per the cycle diagnosis). P2F today follows RESULTS reactions only. Both calendars carry a second event class the book already trusts elsewhere: the news classes N4-V3 trades (SINGLE_NEWS = management_change, large_order, fda_approval, block_deal, sector_policy, pricing, corporate_action — dividend excluded, exactly as in N4's construction): 10 events in the 2025 window / 12 in 2026, of which reaction candidates (measurable reaction day + an R+1 session) number 10 / 11 and those clearing P2F's ≥2.5% band number **3 (2025) / 4 (2026)** (cycle diagnosis, counts only). The question is whether the follow-through mechanism is about results specifically or about large information shocks generally.
- **Challenger (additive component "P2F-NEWS", swap-nothing):** the audited P2F machinery VERBATIM — reaction measured close-to-close on the reaction day (the calendars' effective-reaction-date rule), direction = the reaction's sign, band |reaction| ≥ 2.5%, entry at the R+1 session's 09:15 open, exits T125/S050 (score_lag lag 1), RF-1 weekend stand-aside, and P2F's own frozen exclusions (no ASTRAL, no HINDUNILVR, no HINDALCO LONG) — with ONE change: the event universe is the SINGLE_NEWS classes instead of results. Disjoint from P2F's population by event class (asserted in-pass: no (stock, R) overlap with the results candidates).
- **Anchors (asserted in-pass):** build controls ALL PASS; the generalised candidate builder with the class set restricted to {results} reproduces the build's reaction_candidates per-candidate in both years (the machinery is identical; only the class filter differs); candidate counts == the frozen counts (10 / 11 candidates, 3 / 4 at band).
- **Decision (Cycle-6 additive standard + C24 cell guard):** bank iff (i) the cross-year gate passes AND (ii) combined expectancy > 0 AND (iii) beats the flip placebo per-trade (identical candidates, direction flipped, same exits) AND (iv) no regime cell flips negative in either year.
- **Thinness, pre-registered:** the whole population is 7 band candidates across two years. If banked, the bank is recorded as THIN (the SAT-14/17 precedent class) and the component is flagged for fresh-window judging like every thin bank in this book's history; the standard itself is not altered for its size. A rejection closes the news-class axis for the follow family (results-only stands as the mechanism's universe).
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

- **Construction note (appended 2026-10-31, BEFORE any scoring — the first score run stopped on its own disjointness assertion before a single trade was priced):** the freeze's disjointness assumption is false at the reaction-day level — one news event in 2025 (BDL, R = 2025-11-14, reaction +6.27%) shares its (stock, reaction day) with a results event, so the day's move cannot be attributed to two mechanisms. **Dedup rule (N4's own precedent — its combined set dedupes reaction dates per symbol): news candidates whose (symbol, R) is already a results candidate are dropped; the results machinery owns that reaction day.** Post-dedup frozen counts (counts-only probe, no P&L): 2025 **9 candidates / 2 at band** · 2026 **11 candidates / 4 at band** (2026's calendar-level overlap, TVSMOTOR R = 2026-10-28, never becomes a candidate — its R+1 falls outside the window). The challenger population is therefore 6 band candidates; every other term of the freeze is unchanged.

---

## V3 CYCLE 1 — CHALLENGER CH-V3-1 "INV-R3" — FROZEN BEFORE SCORING (2026-10-31; v3 maximin charter; recorded v2 queue head)
- **Why this challenger:** the head of the recorded untested queue at v2 saturation (log: "INV-R3 (below) → INV-ABOVE-R3", counts re-verified in the v3 diagnosis: **18 rows 2025 / 12 rows 2026** after all filters and law). Target months: **Mar 2025** (9 of the 18 rows fall there — the 4th-worst month, −₹3,124.15, a DOWN-regime month where the sibling INV-LONG population earned +₹2,190.68 while F4 bled) and Jan/Feb of both years. It cannot touch Jul–Nov 2025 (no below-trend round-≥3 rows exist there — disclosed in the diagnosis); under the lexicographic criterion a bank here lifts the vector at the Mar-2025 position and below.
- **Challenger (additive component "INV-R3", swap-nothing):** the audited INV machinery VERBATIM (`run_chain` PLAIN chains, T125/S050, ADR from the machinery's own map) with the p2 filter's round leg changed from `round ≤ 2` to **`round ≥ 3`** — every other leg identical: entry_time < 10:30, ADR ≥ 3.0, gate = cond_inv1 (below-trend days), LONG only, RF-1 weekend stand-aside, base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER, KALYANKJIL}, and the v2 INV law {no HINDALCO, no UNITDSPR, no TATASTEEL}. Disjoint from the incumbent INV-LONG/INV-ABOVE populations by the round value (asserted in-pass: no (date, stock, entry_time, round) overlap).
- **Anchors (asserted in-pass):** build controls ALL PASS; the identical code path with the round leg at `round ≤ 2` reproduces `build_inv` per-trade in both years and, minus the v2-law names, equals the incumbent book's INV-LONG rows exactly (the C22 anchor pattern); frozen population counts == the diagnosis counts (18 / 12).
- **Decision (v3 maximin + Cycle-6 additive standard):** bank iff (i) the sorted 22-month vector lexicographically improves, AND (ii) neither year's total falls and neither year is negative, AND (iii) every regime cell × year stays positive, AND (iv) combined total does not fall, AND (v) component combined expectancy > 0, AND (vi) it beats the flip placebo (SHORT side of the identical gated round-≥3 population) per-trade. Timing audit in the same pass (the machinery's audited chain construction; every row's entry is generated from its own day's bars at or before its entry time — asserted by the build's audit counters plus a determinism re-run).
- **Prior, disclosed honestly:** Lesson 36 closed the LATE-entry complements of this family on both gates (regime rent, year-flipping). The round leg is a different filter axis (chain depth, not entry clock), and the v2 log queued it explicitly as untested; this freeze is that one test. A rejection closes the round axis for the INV family; a bank is recorded with its month concentration stated.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 2 — CHALLENGER CH-V3-2 "INV-ABOVE-R3" — FROZEN BEFORE SCORING (2026-10-31; v3 maximin charter; recorded v2 queue, second item)
- **Why this challenger:** the mirror of C1 on the above-trend gate — the population the v3 diagnosis showed actually lives in the worst months: **28 rows 2025** (Apr 7 · **Oct 5** · Dec 5 · **May 4** · Sep 3 · **Nov 2** · **Jun 1** · Mar 1) / **4 rows 2026** (Apr, May, Jul, Aug — 1 each). Target months: the UP-desert bottom — Oct 2025 (−₹5,149.95, the worst month), Nov 2025 (−₹4,545.69), May 2025 (−₹2,779.66), Jun 2025 (−₹955.92) — where the incumbent's only above-trend earner (INV-ABOVE) is thin or losing (Nov −₹1,638.14, Jun −₹955.92 on its own 7 trades). C1 proved the round axis is alive on the below gate; this is its own test on the above gate (Lesson 22 discipline: a sibling cell's verdict does not transfer).
- **Challenger (additive component "INV-ABOVE-R3", swap-nothing):** the audited INV machinery VERBATIM (`run_chain` PLAIN chains, T125/S050, machinery ADR) with the p2 round leg at **`round ≥ 3`** and the regime gate at **g1 (above-trend days)** — every other leg identical to C1: entry_time < 10:30, ADR ≥ 3.0, LONG only, RF-1 weekend stand-aside, base exclusions {BDL, VEDL, HINDZINC, INDUSTOWER, KALYANKJIL}, v2 INV law {no HINDALCO, no UNITDSPR, no TATASTEEL}. Disjoint from INV-ABOVE (round ≤ 2) and from INV-R3 (gate) by construction, asserted in-pass.
- **Anchors (asserted in-pass):** build controls ALL PASS; the g1 + round ≤ 2 path reproduces the C22 mirror construction and, minus law, equals the incumbent book's INV-ABOVE rows exactly; frozen population counts == the diagnosis counts (28 / 4).
- **Decision (v3 maximin + Cycle-6 additive standard):** bank iff (i) the sorted 22-month vector lexicographically improves, AND (ii) neither year's total falls and neither year is negative, AND (iii) every regime cell × year stays positive, AND (iv) combined total does not fall, AND (v) component combined expectancy > 0, AND (vi) it beats the flip placebo (SHORT side of the identical gated round-≥3 population) per-trade. Timing audit in the same pass.
- **Prior, disclosed honestly:** the above-trend SHORT placebo was the better 2025 trade inside the round ≤ 2 mirror (Lesson 35: exp +₹74.22 in 2025, −₹155.14 in 2026) — the placebo leg is a real hurdle here, not a formality. The incumbent INV-ABOVE lost money in Nov/Jun 2025, so the sleeve this challenger extends is itself regime-thin in exactly the target months; the counts are small (32 rows over two years) and any bank is recorded with that thinness stated.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 3 — DELETION V3C3-P2FR2-OBEROIRLTY-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry, re-derived at the post-C1 book)
- **Registry (stocks_engine_v3_registry.py; v3_out/v3_registry.json):** 15 slices qualify at the standing bar (full-period ≤ −₹500 AND each-year ≤ 0); 14 lexicographically beat; 1 is a rotation and is refused un-scored (N4-V3 × HDFCBANK × LONG: Oct leg −₹852.04 but Jul leg **+₹830.00** — deleting it makes Jul 2025 the new worst month; Lesson 38 corollary (iii)). Queue order: worst-month lifters first.
- **This cycle:** P2F-R2 takes no OBEROIRLTY LONG signals. Frozen set (re-derived at the post-C1 book; Lesson 16 invariance — C1 touched no P2F-R2 leg): **1 trade — 2025-10-20, 09:15, −₹894.00** (2026: none). Full-period −₹894.00, each-year ≤ 0, and its only month leg is the current worst month itself (Oct 2025 −₹5,149.95 → −₹4,255.95 on a bank).
- **Evidence standard, disclosed:** 1 trade — the SAT-14 thin class. The mechanism-scoped pattern is Lesson 11's (OBEROIRLTY is 2025's INV-LONG carrier, +₹14,367.48 there — untouched; its P2F-family follows of the same October reaction lost at both lags, −₹889.35 at R+1 and −₹894.00 here). The sibling R+1 slice is a separate cycle (one change per cycle).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 4 — DELETION V3C4-P2F-OBEROIRLTY-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F takes no OBEROIRLTY LONG signals — the R+1 sibling of C3's slice (the same October-2025 reaction followed at the first lag). Frozen set (extracted from the post-C3 book; C3 touched no P2F leg — Lesson 16 invariance): **1 trade — 2025-10-17, 09:15, −₹889.35** (2026: none). Full-period −₹889.35, each-year ≤ 0, only month leg = Oct 2025 (currently −₹4,255.95 → −₹3,366.60 on a bank).
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class, same Lesson 11 pattern as C3 (the name's P2F-family LONG follows lose at both lags while its INV-LONG flow carries 2025 — untouched).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 5 — DELETION V3C5-N4-INDUSTOWER-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** N4-V3 takes no INDUSTOWER LONG signals. Frozen set (extracted from the post-C4 book; C3/C4 touched no N4 leg): **2 trades — 2025-01-24 (−₹336.36), 2025-10-28 (−₹345.88)** (2026: none). Full-period −₹682.24, each-year ≤ 0; month legs Jan 2025 and Oct 2025 (currently −₹3,366.60 → −₹3,020.72 on a bank).
- **Evidence standard, disclosed:** 2 trades. INDUSTOWER is already excluded from the F4/INV machinery by base law — the name's N4 follows are the remaining surface, and both lost; the slice is mechanism-scoped (Lesson 11), nothing else about the name changes.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 6 — DELETION V3C6-P2FR2-BDL-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F-R2 takes no BDL LONG signals. Frozen set (extracted from the post-C5 book; C5 touched no P2F-R2 leg): **2 trades — 2025-08-18 (−₹841.00), 2025-11-18 (−₹830.00)** (2026: none). Full-period −₹1,671.00, each-year ≤ 0; month legs Aug 2025 and Nov 2025 (currently −₹4,545.69 → −₹3,715.69 on a bank).
- **Evidence standard, disclosed:** 2 trades. BDL is already excluded from the F4/INV machinery by base law; both of its R+2 LONG follows stopped out at the band edge. Mechanism-scoped (Lesson 11).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 7 — DELETION V3C7-P2F-GODREJCP-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F takes no GODREJCP LONG signals. Frozen set (extracted from the post-C6 book; C6 touched no P2F leg): **1 trade — 2025-11-04, 09:15, −₹629.30** (2026: none). Full-period −₹629.30, each-year ≤ 0; only month leg Nov 2025 (currently −₹3,715.69 → −₹3,086.39 on a bank).
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class. Mechanism-scoped (Lesson 11): GODREJCP's other mechanisms are untouched — the name is in fact already queued as a P2F SHORT for the live November forward test (reaction 30 Oct 2026 −2.27%), a different direction in a different component window.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 8 — DELETION V3C8-P2FR2-GODREJCP-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F-R2 takes no GODREJCP LONG signals — the R+2 sibling of C7's slice (the same early-November-2025 reaction followed at the second lag). Frozen set (extracted from the post-C7 book; C7 touched no P2F-R2 leg): **1 trade — 2025-11-06, 09:15, −₹622.45** (2026: none). Full-period −₹622.45, each-year ≤ 0; only month leg Nov 2025 (currently −₹3,086.39 → −₹2,463.94 on a bank).
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class; with C7 this closes the name's LONG follows of that reaction at both lags — the reaction-follow family keeps the name in every other mechanism and direction (Lesson 11).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 9 — DELETION V3C9-INVABOVE-PFC-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** INV-ABOVE takes no PFC LONG signals — the registry's thickest slice. Frozen set (extracted from the post-C8 book): **13 trades, all 2025** — 2025-03-28 (−₹253.50); Apr 2025 ×6 (−₹259.35, −₹258.73, −₹257.50, −₹257.95, −₹247.27, +₹496.56); May 2025 ×6 (−₹235.05, −₹243.37, +₹468.44, −₹247.72, −₹248.00, −₹250.48). Full-period **−₹1,793.92**; month legs Mar −₹253.50 · Apr −₹784.24 · May −₹756.18 — every month leg negative (the two winners sit inside negative months), so no rotation; May 2025 lifts −₹2,779.66 → −₹2,023.48 on a bank. 2026: none.
- **Evidence standard:** 13 trades — the registry's strongest population. The pattern is repeat-stop bleed (eleven ≈ −₹250 stops against two target hits): the name's above-trend chains repeatedly fail to follow through in 2025. Mechanism-scoped (Lesson 11) — PFC's below-trend and event flow untouched.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 10 — DELETION V3C10-INVABOVE-RECLTD-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** INV-ABOVE takes no RECLTD LONG signals. Frozen set (extracted from the post-C9 book): **6 trades, all 2025, all losers** — 2025-04-21 (−₹256.98), 2025-04-22 (−₹262.58), 2025-04-30 (−₹255.33), 2025-05-09 (−₹236.65), 2025-05-16 (−₹25.00), 2025-05-22 (−₹241.08). Full-period **−₹1,277.62**; month legs Apr −₹774.89 · May −₹502.73 — May 2025 lifts −₹2,023.48 → −₹1,520.75 on a bank. 2026: none.
- **Evidence standard:** 6 trades, zero winners — the same repeat-stop shape as C9's PFC slice, in the PSU-financial pair, in the same Apr–May 2025 above-trend window. Mechanism-scoped (Lesson 11).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 11 — DELETION V3C11-P2FR2-TVSMOTOR-SHORT-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F-R2 takes no TVSMOTOR SHORT signals. Frozen set (extracted from the post-C10 book): **1 trade — 2025-05-02, 09:15, −₹1,390.25** (2026: none). Full-period −₹1,390.25, each-year ≤ 0; only month leg May 2025 (currently −₹1,520.75 → −₹130.50 on a bank).
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class — a single band-edge stop on the book's carrier name. The scoped unit is (P2F-R2 × SHORT) only: TVSMOTOR's LONG flow (the book's largest earner across mechanisms) is untouched, and the same name's R2-LOWBAND LONG slice is a separate registry row for a later cycle. Lesson 11's standing warning applies in reverse here: one stopped SHORT follow does not indict the name.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 12 — DELETION V3C12-N4-OIL-SHORT-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** N4-V3 takes no OIL SHORT signals. Frozen set (extracted from the post-C11 book): **2 trades — 2025-02-10 (−₹365.24), 2025-05-22 (−₹365.32)** (2026: none). Full-period −₹730.56, each-year ≤ 0; month legs Feb 2025 and May 2025 — the May leg takes May 2025 from −₹130.50 to **+₹234.82** on a bank (the month leaves the red entirely).
- **Evidence standard, disclosed:** 2 trades, both reaction-day SHORT follows that failed; mechanism-scoped (Lesson 11) — OIL's LONG flow and other mechanisms untouched.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 13 — DELETION V3C13-R2LOWBAND-TVSMOTOR-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** R2-LOWBAND takes no TVSMOTOR LONG signals. Frozen set (extracted from the post-C12 book): **1 trade — 2025-08-05, 09:15, −₹1,515.50** (2026: none). Full-period −₹1,515.50, each-year ≤ 0; only month leg Aug 2025 (currently +₹1,207.95 → +₹2,723.45 on a bank — the beat registers at the vector's 6th position).
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class — the low band's single oversized stop on the carrier name (the component's stop on a 2.0–2.5% reaction is the widest in the family). Scoped to (R2-LOWBAND × LONG) only; with C11, the name's two registry rows are both closed while its main LONG flow is untouched (Lesson 11).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 14 — DELETION V3C14-P2FR2-GLENMARK-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F-R2 takes no GLENMARK LONG signals. Frozen set (extracted from the post-C13 book; the helper prints the exact row above the scorer run and the scorer asserts against it): full-period −₹715.00, 2025 only, single Feb-2025 leg (exact date/net as printed by v3_next_freeze.py and held in v3_out/freeze_c14.json). Feb 2025 lifts on a bank; the beat registers above the bottom-5.
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class. Mechanism-scoped (Lesson 11): GLENMARK is a major earner elsewhere (2026 INV-ABOVE carrier) — untouched.
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 15 — DELETION V3C15-P2F-UNITDSPR-LONG-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry)
- **This cycle:** P2F takes no UNITDSPR LONG signals. Frozen set (extracted from the post-C14 book): **1 trade — 2026-05-18, 09:15, −₹700.15** (2025: none). Full-period −₹700.15, each-year ≤ 0; only month leg May 2026. This is the registry's last row whose deletion lifts a 2026 month — after it, one row remains (N4-V3 × VEDL × SHORT, Jan 2026 −₹616.60), held for the post-report continuation.
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class. UNITDSPR is already excluded from the INV machinery by the v2 law; this closes its P2F LONG surface only (Lesson 11).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.

## V3 CYCLE 16 — DELETION V3C16-N4-VEDL-SHORT-EXCL — FROZEN BEFORE SCORING (2026-10-31; v3 maximin registry, desert-phase continuation)
- **This cycle:** N4-V3 takes no VEDL SHORT signals. Frozen set (extracted from the post-C15 book; registry re-derived this run, v3_out/v3_registry.json): **1 trade — 2026-01-30, 09:35, −₹616.60** (2025: none). Full-period −₹616.60, each-year ≤ 0; only month leg Jan 2026.
- **Evidence standard, disclosed:** 1 trade, SAT-14 thin class. Mechanism-scoped (Lesson 11): VEDL's N4 LONG flow (incl. +₹303.20, Oct 2026) and all other mechanisms untouched; INV-LONG's own VEDL exclusion (v1 law) is a separate scope. This is the registry's LAST qualifying row — after it, the deletion frontier is empty at the standing bar (the only other row, N4-V3 × HDFCBANK × LONG, is a permanent rotation while Jul 2025 is the worst month).
- **Decision:** bank iff the sorted 22-month vector lexicographically improves AND neither year falls / neither negative AND every regime cell × year stays positive AND combined does not fall. Deleted set asserted == this freeze exactly.
- Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per 100 shares, ₹40/trade, home 25, Jan–Dec 2025 + Jan–Oct 2026.
