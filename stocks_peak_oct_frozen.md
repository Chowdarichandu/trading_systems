# OCTOBER PEAK LAB — frozen fixes (written BEFORE scoring each cycle)

## Cycle 1 — frozen 2026-10-31, before any lever was scored

Diagnosis first (stocks_peak_oct_cycle1_diag.py; incumbent verified to
the paisa: 934 tr, total +131,646.79, Oct +50,029.72, audit 0 viol).
October by component: F4 +43,184.33 (103 tr) / INV-LONG +7,691.08 /
N4-V3 -530.69 / P2F -315.00. F4 October exits @ T150/S080:
37 target / 26 stop / 40 square-off; losers 41 tr, -16,209.70.

Candidate (c) P2F 3.0%-band HOME leg — BARRED, not scored: all 33 HOME
rows of stocks_T2_T2-A_3.0_trades.csv are already inside the incumbent
P2F 2.5% book (nested subset, same reaction days) = double-counting an
existing trade, forbidden by lab rules. Its home October (-315.00) is
also already in the book.

Candidate (a) F4 target 1.50% -> 1.75% — NOT chosen: only 5 of 103
October trades reached +1.75% WITHIN their holding window (3 reached
+2.00%); the other 27 reaches happened only after exit (post-exit
flattery, discounted per OC-4's method). OC-4 already measured this
exact step at S065: October estimate +1,188.18, full-period -15,744.13,
verdict "not supported". 32 banked target exits would be put at risk
for at most ~5 marginal conversions.

FROZEN LEVER (b): F4 stop -0.80% -> -0.95%, target +1.50% unchanged,
everything else identical (band [0.5,1.0) + below50 gate, setup3
removed, RF-1 book-wide, INV-LONG / N4-V3 / P2F 2.5% unchanged).
Diagnostic basis: of 26 October stop-outs at S080, 7 never fell
through -0.95% on the day and 2 of those later reached +1.50% the
same day (named recoverable pool); 19 fell through -0.95% anyway
(bounded extra cost 0.15%/trade). This is the OC-4 stop logic
(stops firing on mean-reverting dips) extended one step, scored
honestly by full rebuild — the rebuild, not the estimate, decides.

Progress rule (lab): banked as the new peak basis only if October
rises >= +250 vs 50,029.72; otherwise flat cycle, book unchanged.
Full Jan-Oct month table is reported either way; other months may
fall in this lab and the cost is recorded, not hidden.

## Cycle 2 — frozen 2026-10-31, before any lever was scored

Diagnosis first (stocks_peak_oct_cycle2_diag.py; anchors verified:
Anchor A T150/S095 rebuild == cycle1 dump, 640 tr, audit 0 viol;
Anchor B union == cycle1 peak table, 916 tr, total +135,319.67,
October +51,413.61). October losers by component: F4 34 losers
-16,020.61 (net +44,568.22, 101 tr) — F4 is the October engine and
its loser pool; INV-LONG 11 losers -4,633.92 (net +7,691.08);
N4-V3 4 losers -1,036.42 (net -530.69); P2F 2 losers -315.00.

F4 October excursions @ T150/S095 (exits 38 target / 19 stop /
44 square-off):
- (a) T175 re-diagnosed at S095: only 5/101 reached +1.75% WITHIN
  holding (3 reached +2.00%); 27 reached +1.75% only after exit.
  Unchanged from S080 — still unsupported; 33 banked target exits
  would be put at risk for at most ~5 marginal conversions.
- (b) S110 pool: of 19 stop-outs, 6 never fell through -1.10% on the
  full day (would survive a -1.10% stop); 13 fell through -1.10%
  anyway (bounded extra cost 0.15%/trade). None of the 6 reached
  +1.50% after their S095 exit, so the expected gain is avoided
  -0.95% stop losses converting to square-offs, not target hits —
  the same mean-reverting-dip logic as Lesson 4 / Cycle 1, scored
  honestly by full rebuild.
- (c) Surgery scan: NO setup / direction / round / setup x dir group
  is negative in both October AND the full period (round2 is full
  -4,606.75 but October +1,781.75 — removing it would hurt October;
  every setup and both directions are strongly positive in both).
  Lesson 5's standard is not met, so no (c) lever exists this cycle.
  (A lone sig_time 10:10 bucket is both-negative, full 16 tr
  -2,265.76 / Oct 3 tr -1,821.74, but a single 5-minute bucket with
  strongly positive neighbours 10:05 +7,055.03 and 10:15 +8,148.32
  is a noise slice, not a structural restriction — rejected.)
  Symbol-only both-negatives (IRCTC Oct -658.53, NHPC -11.72,
  OIL -105.84) are tiny and barred in spirit by Lesson 11.

FROZEN LEVER (b): F4 stop -0.95% -> -1.10%, target +1.50% unchanged,
everything else identical (band [0.5,1.0) + below50 gate, setup3
removed, RF-1 book-wide, INV-LONG / N4-V3 / P2F 2.5% unchanged).

Progress rule (lab): banked as the new peak basis only if October
rises >= +250 vs 51,413.61; otherwise flat cycle, book unchanged.
Full Jan-Oct month table is reported either way; other months may
fall in this lab and the cost is recorded, not hidden.

## Cycle 3 — frozen 2026-10-31, before any lever was scored

Diagnosis first (stocks_peak_oct_cycle3_diag.py; anchors verified:
Anchor A T150/S110 rebuild == cycle2 dump, 630 tr, audit 0 viol;
Anchor B union == cycle2 peak table, 909 tr, total +131,768.01,
October +52,428.50). October losers by component: F4 33 losers
-15,005.72 (net +45,583.11, 100 tr) — F4 remains the October engine
and its loser pool; INV-LONG 11 losers -4,633.92 (net +7,691.08);
N4-V3 4 losers -1,036.42 (net -530.69); P2F 2 losers -315.00.

F4 October excursions @ T150/S110 (exits 38 target / 13 stop /
49 square-off):
- (a) T175 re-measured at S110, as instructed (wider stop keeps
  trades alive longer, so the reach count might have grown): it did
  NOT grow — still only 5/100 reached +1.75% WITHIN holding
  (3 reached +2.00%), unchanged from 5/101 @ S095 and 5/103 @ S080,
  and all 5 reaches are inside trades that already exited at the
  +1.50% target; 27 reached +1.75% only after exit. Candidate (a)
  is dismissed on this evidence, not assumed away.
- Square-off pool (new this cycle): 49 trades, net +7,777.00
  (29 winners +14,155.00 / 20 losers -6,378.00). 17 reached
  MFE >= +1.00% within holding (6 in [1.25,1.50), 11 in [1.00,1.25)),
  their net only +2,968.00 against Rs13,987.00 of MFE-to-close
  give-back. Recorded as a real pool, BUT no exit-progress lever is
  frozen from it this cycle: the M2 machinery (U.replay_plain)
  replays only plain target/stop/square-off — a trailing/lock rule
  is NOT replayable by the existing machinery without inventing a
  new intra-candle ordering convention mid-lab, and the only plain
  proxy (lowering the target toward +1.00/+1.25%) runs against
  Lesson 4's proven direction (widening 1.25->1.50 added ~+Rs24k).
- (c) Surgery scan: NO setup / direction / round / setup x dir group
  is negative in both October AND the full period (round2: full
  -10,900.18 but Oct +1,818.75). sig_time 10:10 is both-negative
  again (full 16 tr -2,488.24 / Oct 3 tr -1,499.03) but remains a
  lone 5-minute noise slice between strongly positive neighbours
  (10:05 full +6,068.38 / Oct +3,704.55; 10:15 full +8,043.92 /
  Oct +2,357.19) — rejected as in Cycle 2; sig_time 10:45 is
  1 Oct trade / full -77.70, trivial. Symbol both-negatives
  (IRCTC Oct -726.99, OIL Oct -173.07) are tiny and barred in
  spirit by Lesson 11. No Lesson-5 (c) lever exists this cycle.

FROZEN LEVER (b): F4 stop -1.10% -> -1.25%, target +1.50% unchanged,
everything else identical (band [0.5,1.0) + below50 gate, setup3
removed, RF-1 book-wide, INV-LONG / N4-V3 / P2F 2.5% unchanged).
Diagnostic basis: the stop-widening vein is diminishing (Cycle 1
+1,383.89, Cycle 2 +1,014.89 at rising total cost) and S125 is NOT
assumed to work — it is scored only because the diagnosis proves a
surviving recoverable pool still exists at S110: of 13 October
stop-outs, 4 never fell through -1.25% on the full day
(INDUSTOWER 10-15 MAE 1.157% net -463.12; KALYANKJIL 10-27 MAE
1.185% net -587.80; PFC 10-22 MAE 1.120% net -398.60; BDL 10-07
MAE 1.147% net -1,229.32; pool total -2,678.84), none of the 4
later reached +1.50% (expected gain is avoided -1.10% stops
converting to square-offs, as in Cycles 1-2); the other 9 fell
through -1.25% anyway (bounded extra cost ~Rs860 in October at
0.15% x their entries). The full rebuild, not the estimate, decides.

Progress rule (lab): banked as the new peak basis only if October
rises >= +250 vs 52,428.50; otherwise flat cycle (flat_cycles += 1),
book unchanged. Full Jan-Oct month table is reported either way;
other months may fall in this lab and the cost is recorded, not hidden.

## Cycle 4 — frozen 2026-10-31, before any lever was scored

Diagnosis first (stocks_peak_oct_cycle4_diag.py; anchors verified:
Anchor A T150/S125 rebuild == cycle3 dump, 620 tr, audit 0 viol;
Anchor B union == cycle3 peak table, 901 tr, total +131,331.19,
October +53,290.52). October losers by component: F4 33 losers
-14,143.70 (net +46,445.13, 100 tr; exits now 38 target / 8 stop /
54 square-off — the loser pool has migrated to square-offs);
INV-LONG 11 losers -4,633.92, ALL 11 stop exits (net +7,691.08,
21 tr); N4-V3 4 losers -1,036.42; P2F 2 losers -315.00.

Candidate (a) F4 stop -1.25% -> -1.40% — REJECTED on pool-proof:
of the 8 October F4 stop-outs at S125, ZERO never fell through
-1.40% (full-day MAEs 1.414%..2.713%; the two shallowest, VEDL
10-29 1.415% and HINDCOPPER 10-22 1.414%, still breach it).
Recoverable pool = 0 trades / Rs0 — S140 would only add 0.15%
cost to all 8 stop-outs. The F4 stop vein is exhausted at S125;
the pre-approval condition ("only if the diagnosis proves a
fresh recoverable pool") is NOT met, so (a) is not frozen.

Candidate (c) F4 rounds 2->3 — REJECTED on structural pool: a
third qualifying pick (same gate/direction, setup3 excluded,
after the round-2 exit) exists on only 5 stock-days in the full
Jan-Oct period and ZERO in October. No October lever exists.

Candidate (b) INV-LONG exit change — SUPPORTED by the diagnosis:
INV-LONG's October losers are 11/11 stop exits at its T125/S050
structure (verified from stocks_M1.py: default dump
tuning_inv_T1_T125_S050_trades.csv). Of those 11 stops, 3 never
fell through -0.65% on the full day (pool net -2,328.87):
TVSMOTOR 10-15 r2 (net -2,062.00, full-day MAE 0.593%),
WIPRO 10-26 (-134.30, MAE 0.557%), WIPRO 10-28 (-132.57,
MAE 0.540%) — each dipped just past -0.50% and never reached
-0.65%, so a -0.65% stop keeps them alive to target/square-off
(same mean-reverting-dip logic as Lesson 4 / F4 Cycles 1-3).
A 4th stop (KALYANKJIL 10-16, MAE 0.731%) survives -0.80% but
not -0.65%. The other 7 fell through -0.65% anyway (bounded
extra cost 0.15%/trade). INV-LONG target widening is dead by
contrast: 0 non-target October trades reached +1.50% within
holding. F4 loser scan at S125: no setup/dir/round group is
negative in October (round2 Oct +1,818.75, 0 losers; both setups
and both directions strongly positive) — no Lesson-5 lever.

FROZEN LEVER (b): INV-LONG stop -0.50% -> -0.65%, target +1.25%
unchanged, ONE exit parameter only. INV-LONG is rebuilt with its
own audited machinery (stocks_tuning_inv.build_cell("T125_S065")
cached chains -> p2_filter cap=2, entry <10:30, ADR>=3 ->
cond_inv1 -> LONG only -> weekend/RF-1 filter), exactly the pool
definition that produced the incumbent T125/S050 dump; the score
script must first anchor inv_rows("T125_S050") LONG == the M1
dump to the paisa. Everything else identical (F4-minus-setup3
@ T150/S125, N4-V3, P2F 2.5%, RF-1 book-wide). Timing invariants
asserted on the new leg: cond_inv1 holds on every row, round<=2,
entry_time <10:30 (entries are next-candle opens after signals
by the round-8 run_chain construction, validated in the INV
tuning loop's validation gate).

Progress rule (lab): banked as the new peak basis only if October
rises >= +250 vs 53,290.52; otherwise flat cycle (flat_cycles += 1),
book unchanged. Full Jan-Oct month table is reported either way;
other months may fall in this lab and the cost is recorded, not hidden.

## Cycle 5 — frozen 2026-10-31: NO LEVER FROZEN (diagnosis-only flat)

Diagnosis first (stocks_peak_oct_cycle5_diag.py + _diag2.py; anchors
verified: Anchor A T150/S125 rebuild == cycle3 dump, 620 tr, audit
0 viol; Anchor B union == cycle3 peak table, 901 tr, total
+131,331.19, October +53,290.52).

(i) F4 square-off MTM profile — NO decay into the close:
October square-offs (54 tr, orig net +6,122.00, 25 losers -8,033.00),
static same-entry exit at the close of: 13:00 +3,056.00 (delta
-3,066.00), 14:00 +4,984.00 (-1,138.00), 14:30 +5,426.00 (-696.00),
15:00 +6,372.00 (+250.00). Full period (288 tr, orig +21,099.00):
13:00 -6,018.00, 14:00 -9,271.00, 14:30 -12,752.00, 15:00 -6,521.00
— every earlier time is worse full-period. And the one marginal
figure (15:00, +250.00) does NOT survive the all-trades same-entry
accounting: 3 October F4 trades exit at target on the 15:05/15:10
bars and would be forfeited to a 15:00 square-off; including every
trade still open after the candidate bar, 15:00 = October -134.20 /
full -8,007.41 (13:00 -16,023.23 / -18,633.37; 14:00 -12,042.29 /
-20,897.36; 14:30 -10,476.17 / -22,169.32). Square-offs on average
GAIN into the close, not decay. Candidate (a) is NOT supported at
any earlier time.

(ii) F4 qualifier sub-band split — NO rotten band:
[0.5,0.75): full 362 tr +35,271.23, October 57 tr +22,071.99
(21 losers). [0.75,1.0): full 210 tr +43,960.88, October 43 tr
+24,373.14 (12 losers). Neither sub-band is October-negative, let
alone October-negative AND full-negative (Lesson 5 standard unmet).
A floor raise to 0.75 would delete +22,071.99 of October; a cap at
0.75 would delete +24,373.14. Candidate (b) is NOT supported in
either direction.

DECISION: neither lever is supported, and neither was given
unconditional pre-approval — (a) was conditional on diagnosed decay
into the close (absent) and (b) on the Lesson-5 both-negative
standard (unmet). Per the lab instruction for exactly this case,
NO lever is frozen and nothing is scored. Cycle 5 is a
diagnosis-only FLAT cycle: flat_cycles 1 -> 2, book and peak
unchanged (October +53,290.52, total +131,331.19, 901 tr).
One more consecutive flat cycle (Cycle 6) = PEAK FOUND (3/3).

## Cycle 6 — frozen 2026-10-31, before any lever was scored (LAST cycle before lab termination rule)

Diagnosis first (stocks_peak_oct_cycle6_diag.py; anchors verified at
T=10:00: Anchor A T150/S125 rebuild == cycle3 dump, 620 tr, audit
0 viol; Anchor B union == peak table, 901 tr, total +131,331.19,
October +53,290.52).

Diagnosis re-check — F4 direction split at the current S125 basis
(filtered book: non-weekend, setup3 removed):
- LONG:  full 229 tr +41,294.67 (105 losers -66,951.83) |
  October 52 tr +24,563.00 (19 losers -8,122.20).
- SHORT: full 343 tr +37,937.44 (164 losers -133,629.08) |
  October 48 tr +21,882.13 (14 losers -6,021.50).
Both directions are strongly positive in BOTH windows — no
direction is rotten, no Lesson-5 direction surgery exists. This
split is reported for the record only; it does not change the
frozen lever below.

RATIONALE for the one structural dimension never varied at this
basis: F4's MEASUREMENT TIME. H1's October scan showed October's
money concentrated early (09:45-10:00). F4 measures the morning
move at 10:00 — measuring at 09:45 admits the same gated
population (band [0.5,1.0) + below50, same setups, same
T150/S125 exits) one bar-set earlier. Every other dimension at
this basis is already exhausted on evidence: stop > -1.25% (pool
zero), target 1.75% (x3), rounds 3 (October pool zero), INV-LONG
exit changes (scored/dead), earlier square-off times (Cycle 5:
negative at every time on all-trades accounting), band floor/cap
tweaks (Cycle 5: both sub-bands strongly positive in both
windows), trailing/lock rules (not replayable).

FROZEN LEVER: F4 measurement time 10:00 -> 09:45, everything else
identical (M2F.T = "09:45"; CFG band_hi=1.0 + below50 regime;
band [0.5,1.0); setup3_bounce_rejection removed; non-weekend
filter; exits T150/S125 unchanged; INV-LONG @ T125/S050, N4-V3,
P2F 2.5% and RF-1 book-wide unchanged). The qualifier is the move
from open through the bar ending 09:45 (premove over candles with
time < 09:45, per the machinery); signals only at/after 09:45.
The build's timing audit must assert entry >= measurement on the
new basis: M2F._AUDIT violations == 0 AND every new F4 trade has
sig_time >= "09:45", entry_time >= "09:45", meas_time == "09:45"
(asserted explicitly in the score script).

Progress rule (lab): banked as the new peak basis only if October
rises >= +250 vs 53,290.52; otherwise flat cycle (flat_cycles
2 -> 3) = PEAK FOUND, lab terminates. Full Jan-Oct month table is
reported either way; other months may fall in this lab and the
cost is recorded, not hidden.
