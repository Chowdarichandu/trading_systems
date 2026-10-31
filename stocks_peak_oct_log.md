# OCTOBER PEAK LAB — cycle log

## Cycle 1 — 2026-10-31 — PROGRESS (October +1,383.89)

**Basis verified:** incumbent rebuilt exactly (Anchor A: T150/S080 rebuild
== OC-4 dump, 661 tr; Anchor B: union == peak state table, 934 tr,
total +131,646.79, October +50,029.72; audit 0 violations).

**Diagnosis (October at current basis):** F4 carries October
(+43,184.33, 103 tr); INV-LONG +7,691.08 (21 tr), N4-V3 −530.69,
P2F −315.00. F4 October exits: 37 target / 26 stop / 40 square-off;
losers 41 tr / −16,209.70. Excursions: only 5/103 trades reached
+1.75% within holding (T175 unsupported — same step measured
Oct +1,188 / full −15,744 at S065 by OC-4); of 26 stop-outs, 7 never
fell through −0.95% and 2 of those later hit +1.50% the same day.

**Candidates:** (c) P2F 3.0% HOME leg BARRED — all 33 HOME rows already
inside the P2F 2.5% book (double-count). (a) T175 not chosen (above).
**Frozen lever (b): F4 stop −0.80% → −0.95%, target +1.50% unchanged**
(frozen in stocks_peak_oct_frozen.md before scoring).

**Scored (full rebuild, audit 640 tr / 0 violations):**
October 50,029.72 → **51,413.61 (+1,383.89 ≥ +250 = progress)**;
total 131,646.79 → **135,319.67 (+3,672.88)**; trades 934 → 916.
Month deltas: Jun −1,233.49 → +764.77 (flips green), Feb +2,067.91,
Mar +1,373.64, Jan +489.65; costs recorded: Sep −1,690.61 (still
+15,723.18), May −1,589.18, Apr +50.73 → −194.06 (flips slightly red),
Aug −11.64, Jul −104.25. Greens: 8/10 (Apr swapped for Jun).

**State:** iteration 1, october_peak 51,413.61, flat_cycles 0.
Files: stocks_peak_oct_cycle1_diag.py/.json, stocks_peak_oct_cycle1_score.py,
stocks_peak_oct_cycle1_result.json, stocks_peak_oct_cycle1_f4s095_trades.csv.

## Cycle 2 — 2026-10-31 — PROGRESS (October +1,014.89)

**Basis verified:** anchors pass (Anchor A: T150/S095 rebuild == cycle1
dump, 640 tr, audit 0 viol; Anchor B: union == cycle1 peak table,
916 tr, total +135,319.67, October +51,413.61).

**Diagnosis (October at S095 basis):** F4 carries October
(+44,568.22, 101 tr; 34 losers / −16,020.61); INV-LONG +7,691.08
(11 losers / −4,633.92), N4-V3 −530.69, P2F −315.00. F4 October exits:
38 target / 19 stop / 44 square-off. Excursions: (a) T175 still weak —
only 5/101 reached +1.75% within holding (3 reached +2.00%), 27 only
after exit. (c) surgery scan: NO setup / direction / round /
setup×dir group is negative in both October AND full period (round2:
full −4,606.75 but Oct +1,781.75; all setups and both directions
positive in both) — Lesson 5 standard unmet, no (c) lever; a lone
sig_time 10:10 bucket (full −2,265.76 / Oct −1,821.74, n=16/3) was
rejected as a noise slice between positive neighbours.
**Frozen lever (b): F4 stop −0.95% → −1.10%, target +1.50% unchanged**
(6 of 19 stop-outs never fell through −1.10% on the day; 13 did —
bounded +0.15%/trade cost; frozen in stocks_peak_oct_frozen.md
before scoring).

**Scored (full rebuild, audit 630 tr / 0 violations):**
October 51,413.61 → **52,428.50 (+1,014.89 ≥ +250 = progress)**;
total 135,319.67 → **131,768.01 (−3,551.66 — total fell; October-only
objective, cost recorded, not hidden)**; trades 916 → 909.
F4 October 44,568.22 → 45,583.11. Month deltas: Mar +3,166.52,
Sep +1,351.40, Feb +200.10, Jul +9.84; costs: Apr −3,382.98
(−194.06 → −3,577.04, deeper red), Jan −2,317.56, Jun +764.77 →
−1,070.86 (flips red), Aug −1,453.63, May −304.61.
Greens: 7/10 (Jun lost; Apr/Aug already red, deeper).

**State:** iteration 2, october_peak 52,428.50, flat_cycles 0,
basis now F4 @ T150/S110. Files: stocks_peak_oct_cycle2_diag.py/.json,
stocks_peak_oct_cycle2_score.py, stocks_peak_oct_cycle2_result.json,
stocks_peak_oct_cycle2_f4s110_trades.csv.

## Cycle 3 — 2026-10-31 — PROGRESS (October +862.02)

**Basis verified:** anchors pass (Anchor A: T150/S110 rebuild == cycle2
dump, 630 tr, audit 0 viol; Anchor B: union == cycle2 peak table,
909 tr, total +131,768.01, October +52,428.50).

**Diagnosis (October at S110 basis):** F4 carries October
(+45,583.11, 100 tr; 33 losers / −15,005.72); INV-LONG +7,691.08
(11 losers / −4,633.92), N4-V3 −530.69, P2F −315.00. F4 October exits:
38 target / 13 stop / 49 square-off. Excursions:
- (a) T175 re-measured at S110 (wider stop = longer holding, so the
  reach count might have grown): it did NOT grow — still only 5/100
  reached +1.75% within holding (3 reached +2.00%), unchanged from
  S095/S080, and all 5 reaches are inside trades that already exited
  at the +1.50% target; 27 reached +1.75% only after exit. (a)
  dismissed on evidence.
- Square-off pool (new): 49 tr, net +7,777.00 (29 win / +14,155.00;
  20 lose / −6,378.00); 17 reached MFE ≥ +1.00% within holding
  (6 in [1.25,1.50), 11 in [1.00,1.25)), net only +2,968.00 against
  ₹13,987.00 of MFE-to-close give-back. No exit-progress lever frozen:
  replay_plain replays only plain target/stop/square-off (a trailing/
  lock rule would need a new intra-candle ordering convention invented
  mid-lab), and the plain proxy (lower target) contradicts Lesson 4.
- (c) surgery scan: NO setup / direction / round / setup×dir group
  negative in both October AND full (round2 full −10,900.18 but
  Oct +1,818.75). sig_time 10:10 both-neg again (full −2,488.24 /
  Oct −1,499.03) but still a lone noise slice between strongly
  positive neighbours (10:05 +6,068.38/+3,704.55; 10:15 +8,043.92/
  +2,357.19) — rejected as in Cycle 2; 10:45 trivial (full −77.70).
**Frozen lever (b): F4 stop −1.10% → −1.25%, target +1.50% unchanged**
(pool proven, not assumed: 4 of 13 stop-outs never fell through
−1.25% on the full day — INDUSTOWER 10-15, KALYANKJIL 10-27,
PFC 10-22, BDL 10-07; pool −2,678.84, 0 later hit +1.50%; 9 fell
through anyway, bounded extra cost ~₹860 in October; frozen in
stocks_peak_oct_frozen.md before scoring).

**Scored (full rebuild, audit 620 tr / 0 violations):**
October 52,428.50 → **53,290.52 (+862.02 ≥ +250 = progress)**;
total 131,768.01 → **131,331.19 (−436.82 — total fell slightly;
October-only objective, cost recorded, not hidden)**; trades 909 → 901.
F4 October 45,583.11 → 46,445.13. Month deltas: Aug +3,688.88
(−2,949.53 → +739.35, flips green), Apr +2,944.64 (still red −632.40),
Jun +252.87, May +81.44, Jul −40.15; costs: Mar −3,188.75,
Sep −2,104.15, Feb −1,501.63, Jan −1,431.99.
Greens: 8/10 (Aug gained; Apr/Jun still red, both shallower).
Stop-widening vein, October gains by cycle: +1,383.89 / +1,014.89 /
+862.02 — still paying, still diminishing.

**State:** iteration 3, october_peak 53,290.52, flat_cycles 0,
basis now F4 @ T150/S125. Files: stocks_peak_oct_cycle3_diag.py/.json,
stocks_peak_oct_cycle3_score.py, stocks_peak_oct_cycle3_result.json,
stocks_peak_oct_cycle3_f4s125_trades.csv.

## Cycle 4 — 2026-10-31 — FLAT (October −86.62; flat_cycles 1/3)

**Basis verified:** anchors pass (Anchor A: T150/S125 rebuild ==
cycle3 dump, 620 tr, audit 0 viol; union == cycle3 peak table,
901 tr, total +131,331.19, October +53,290.52; Anchor B: INV
audited machinery inv_rows("T125_S050") LONG == M1 dump exactly,
240 tr).

**Diagnosis (October at S125 basis):** F4 net +46,445.13 (100 tr)
but its loser pool has migrated: exits 38 target / 8 stop /
54 square-off; 33 losers −14,143.70, of which 25 are square-off
losers and only 8 stops. INV-LONG 11 losers −4,633.92, ALL stop
exits; N4-V3 −530.69; P2F −315.00.
- (a) F4 S140 REJECTED on pool-proof: of 8 October stop-outs,
  ZERO never fell through −1.40% (full-day MAEs 1.414%–2.713%;
  shallowest VEDL 10-29 1.415%, HINDCOPPER 10-22 1.414%). Pool
  = 0 — the F4 stop vein is EXHAUSTED at S125 (gains were
  +1,383.89 / +1,014.89 / +862.02, now no pool at all).
- (c) F4 rounds 2→3 REJECTED: a third qualifying pick after the
  round-2 exit exists on 5 stock-days full-period, ZERO in
  October. No October lever.
- F4 surgery scan at S125: no setup/dir/round group negative in
  October (round2 +1,818.75 with 0 losers). INV-LONG target
  widening dead: 0 non-target October trades reached +1.50%
  within holding.
**Frozen lever (b): INV-LONG stop −0.50% → −0.65%, target +1.25%
unchanged** (pool proven: 3 of 11 October stops never fell
through −0.65% — TVSMOTOR 10-15 r2 −2,062.00 MAE 0.593%,
WIPRO 10-26 −134.30 MAE 0.557%, WIPRO 10-28 −132.57 MAE 0.540%;
pool −2,328.87; frozen in stocks_peak_oct_frozen.md before
scoring; INV-LONG rebuilt via stocks_tuning_inv build_cell
T125_S065 → p2_filter → cond_inv1 → LONG, invariants asserted:
cond 0 viol, pool 0 viol, weekend 0).

**Scored (full rebuild):** October 53,290.52 → **53,203.90
(−86.62 < +250 = FLAT, not banked)**; the pool did not convert —
wider stops hold trades longer and shift later chain entries
(INV-LONG trades 240 → 229; INV October 7,691.08 → 7,604.46).
Would-be total 131,331.19 → 125,746.79 (−5,584.40 — cost
recorded, not hidden): Mar −2,410.79, Apr −2,226.92,
Jun −2,200.90, May −529.26, Sep −298.98, Aug −79.31; gains
Jan +1,212.72, Feb +1,035.66, Jul 0.00.

**State:** iteration 4, october_peak 53,290.52 (unchanged),
flat_cycles 1, basis unchanged (F4 @ T150/S125, INV-LONG
@ T125/S050). Files: stocks_peak_oct_cycle4_diag.py/.json,
stocks_peak_oct_cycle4_score.py, stocks_peak_oct_cycle4_result.json,
stocks_peak_oct_cycle4_inv_s065_trades.csv.

## Cycle 5 — 2026-10-31 — FLAT, diagnosis-only (October unchanged; flat_cycles 2/3)

**Basis verified:** anchors pass (Anchor A: T150/S125 rebuild ==
cycle3 dump, 620 tr, audit 0 viol; Anchor B: union == cycle3 peak
table, 901 tr, total +131,331.19, October +53,290.52).

**Diagnosis (i) — F4 square-off MTM: no decay into the close.**
October square-offs: 54 tr, net +6,122.00 (25 losers −8,033.00 —
the −14,143.70 quoted for Cycle 4 is F4's total October loser pool,
stops included). Static same-entry exit at earlier closes:
13:00 −3,066.00 vs 15:10, 14:00 −1,138.00, 14:30 −696.00,
15:00 +250.00. Full period (288 sq-offs, +21,099.00): all four
earlier times negative (−6,018.00 / −9,271.00 / −12,752.00 /
−6,521.00). The 15:00 +250.00 is overturned by all-trades
same-entry accounting (diag2): 3 October trades take target exits
on the 15:05/15:10 bars that a 15:00 square-off forfeits —
15:00 all-trades delta = October −134.20, full −8,007.41
(13:00 −16,023.23/−18,633.37; 14:00 −12,042.29/−20,897.36;
14:30 −10,476.17/−22,169.32). Square-offs gain into the close
on average; lever (a) unsupported at every earlier time.

**Diagnosis (ii) — F4 sub-band split: no rotten band.**
[0.5,0.75): full 362 tr +35,271.23 / Oct 57 tr +22,071.99.
[0.75,1.0): full 210 tr +43,960.88 / Oct 43 tr +24,373.14.
Neither band is October-negative or full-negative — Lesson 5
standard unmet; a floor raise deletes +22,071.99 of October, a
cap deletes +24,373.14. Lever (b) unsupported either direction.

**Frozen/scored:** NOTHING frozen, NOTHING scored — neither
candidate was unconditionally pre-approved, and both of their
stated support conditions failed (see frozen.md Cycle 5). This
is the instructed diagnosis-only flat outcome, not a skipped
scoring.

**State:** iteration 5, october_peak 53,290.52 (unchanged),
flat_cycles 2, basis unchanged (F4 @ T150/S125, INV-LONG
@ T125/S050). Files: stocks_peak_oct_cycle5_diag.py/.json,
stocks_peak_oct_cycle5_diag2.py, stocks_peak_oct_cycle5_result.json.

## Cycle 6 — 2026-10-31 — FLAT (October −14,826.76; flat_cycles 3/3) — **PEAK FOUND, LAB TERMINATED**

**Basis verified:** anchors pass at T=10:00 (Anchor A: T150/S125
rebuild == cycle3 dump, 620 tr, audit 0 viol; Anchor B: union ==
peak table, 901 tr, total +131,331.19, October +53,290.52).

**Diagnosis re-check — F4 direction split at the S125 basis:**
LONG full 229 tr +41,294.67 / October 52 tr +24,563.00;
SHORT full 343 tr +37,937.44 / October 48 tr +21,882.13.
Both directions strongly positive in both windows — no rotten
direction, no Lesson-5 surgery; reported for the record only.

**Frozen lever: F4 measurement time 10:00 → 09:45** (M2F.T =
"09:45"; qualifier = move from open through the bar ending 09:45;
signals only at/after 09:45; band [0.5,1.0) + below50, setup3
removed, T150/S125 exits, everything else identical; frozen in
stocks_peak_oct_frozen.md before scoring). Rationale: H1's
October scan showed October's money concentrated early
(09:45–10:00); this was the one structural dimension never
varied at this basis.

**Scored (full rebuild; new-basis timing audit clean — 548 raw
trades, 0 violations; explicit assert: every trade sig_time ≥
09:45, entry_time ≥ 09:45, meas_time == 09:45):**
October 53,290.52 → **38,463.76 (−14,826.76 < +250 = FLAT, not
banked)**. Measuring 15 minutes earlier does NOT admit the same
population earlier — it admits a different, worse one: F4
October 46,445.13 → 31,618.37 (572 → 498 filtered trades) and
F4 full-period collapses +79,232.11 → **−17,211.62**. The 10:00
measurement is load-bearing, not incidental. Would-be total
131,331.19 → 34,887.46 (−96,443.73), trades 901 → 827.
Would-be month deltas: Apr +13,967.12, Jan +5,751.41,
Aug +4,841.76, Jul +810.56; costs: Sep −29,200.22,
May −29,609.21, Jun −24,576.48, Mar −17,213.44, Oct −14,826.76,
Feb −6,388.47 (flips red).

**State:** iteration 6, october_peak 53,290.52 (unchanged),
flat_cycles 3, **terminated = "PEAK FOUND"**, basis unchanged
(F4-minus-setup3 @ T150/S125, measured 10:00; INV-LONG
@ T125/S050). Files: stocks_peak_oct_cycle6_diag.py/.json,
stocks_peak_oct_cycle6_score.py, stocks_peak_oct_cycle6_result.json,
stocks_peak_oct_cycle6_f4t0945_trades.csv.

---

## FINAL LAB REPORT — OCTOBER PEAK FOUND: +₹53,290.52

**Peak (in-sample, at the Cycle-3 banked basis):** October
**+₹53,290.52**; full Jan–Oct total +₹131,331.19; 901 trades;
8/10 months green. Book at peak: INV-LONG (T125/S050) + N4-V3 +
P2F 2.5% + F4-minus-setup3 @ T150/S125 (band [0.5,1.0) +
below-50DMA gate, measured 10:00), RF-1 book-wide.
Month table at peak: Jan +9,173.84 · Feb +4,939.87 ·
Mar +21,673.47 · Apr −632.40 · May +26,032.03 · Jun −817.99 ·
Jul +1,962.07 · Aug +739.35 · Sep +14,970.43 · Oct +53,290.52.

**The path — 50,029.72 → 53,290.52 (+₹3,260.80 over 6 cycles):**
- Cycle 1 — BANKED: F4 stop −0.80% → −0.95% (Oct +1,383.89;
  total +3,672.88).
- Cycle 2 — BANKED: F4 stop −0.95% → −1.10% (Oct +1,014.89;
  total −3,551.66 — cost recorded: Apr/Jun/Aug fell).
- Cycle 3 — BANKED: F4 stop −1.10% → −1.25% (Oct +862.02;
  total −436.82; Aug flipped green). Stop-widening vein,
  diminishing each cycle: +1,383.89 / +1,014.89 / +862.02.
- Cycle 4 — FLAT: INV-LONG stop −0.50% → −0.65% scored
  Oct −86.62 (pool did not convert; chain entries shifted).
- Cycle 5 — FLAT, diagnosis-only: nothing frozen — square-offs
  gain into the close at every earlier time on all-trades
  accounting; both qualifier sub-bands strongly positive.
- Cycle 6 — FLAT: F4 measurement 10:00 → 09:45 scored
  Oct −14,826.76; F4 full-period collapses to −17,211.62.
Three consecutive flats (Cycles 4–6) = PEAK FOUND per lab rules.

**Killed on evidence (never re-freeze):** F4 stop beyond
−1.25% (Cycle 4: S140 recoverable pool = ZERO, all 8 stop-outs
fell through −1.40%); F4 target 1.75% (measured ×3 cycles: only
5/100–103 October trades ever reached +1.75% within holding);
F4 round 3 (October pool = ZERO); INV-LONG stop widening
(Cycle 4, scored −86.62) and INV-LONG target widening (0 reaches);
earlier F4 square-off times 13:00/14:00/14:30/15:00 (Cycle 5:
negative at every time, full and October, all-trades accounting);
F4 band floor/cap tweaks (Cycle 5: [0.5,0.75) Oct +22,071.99 and
[0.75,1.0) Oct +24,373.14 — neither band rotten); F4 direction
surgery (Cycle 6: LONG and SHORT both strongly positive in both
windows); F4 measurement at 09:45 (Cycle 6, scored −14,826.76);
trailing/lock rules (not replayable by the machinery); P2F 3.0%
HOME leg and DBL-LONG (double-counting an existing trade, barred).

**Caveat (unchanged, and it matters):** the peak is an IN-SAMPLE
October ceiling discovered under honest ex-ante rules with clean
timing audits — a discovery number, NOT a validated system.
October 2026 was 100% below-trend days (Lesson 8); the stop
steps were selected on the same window that judges them.
December fresh data judges the secured book, not this peak,
unless the user rules otherwise. Basis throughout: equity cash,
paper only, real ₹0, provisional per 100 shares, ₹40/trade,
home 25. The MAIN engine state (stocks_engine_state.json) was
never touched by this lab.

## RULE CLARIFICATION APPLIED — SATURATED (2026-10-31, coordinator)

User rule (supersedes the 3-flat-cycles stop): no fixed cycle count,
no 3-strike rule. The run continues while cycles beat the best
October so far; the FIRST failed attempt marks SATURATION; the
peak = the best cycle's October value (his example: cycle 19 =
19,000, cycle 20 = 18,000 → cycle 19 is the peak).

Applied to this lab's record (cycle_history now in the state file):
Cycle 0: 50,029.72 (fork) · 1: 51,413.61 · 2: 52,428.50 ·
3: 53,290.52 (BEST) · 4: attempt 53,203.90 — FAILED TO BEAT, first
saturation mark · 5: no lever qualified — failed to beat ·
6: attempt 38,463.76 — failed decisively (F4 measurement 09:45
collapses the gated population; the 10:00 measurement is
load-bearing).

**FINAL: October peak = +₹53,290.52 (Cycle 3 basis: F4 @ T150/S125),
lab SATURATED.** Total at peak +₹131,331.19, 901 trades, 8/10
months green. In-sample October ceiling under honest ex-ante
rules — a discovery number, NOT a validated system.
