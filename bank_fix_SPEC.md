# BANK-FIX PROGRAMME — SPEC (FROZEN BEFORE SCORING)

Frozen: 2026-11-16 (IST), before any bank-fix scoring was run.
Owner's order: 2026-11-16 15:38 IST — Bank Nifty is the one line
haunting him; every Bank line is red in November while stocks make
money. Fix it with NEW dials only, through the full controls gate.

**Basis (standing): paper only, real money ₹0. Bank Nifty option
premiums per 1 lot (30), cost ₹220/trade inside every net,
UNIQUE-ONCE counting, option BUYING only. No frozen November book,
ledger, or live job is touched by this programme. Anything that
passes the gate becomes a score-only forward shadow + December
candidate — nothing here changes a running book.**

## Anchors (must reproduce exactly before any variant is scored)

From the gated stores (`november_books_fix_anatomy_legs.csv` ⨝
`solid60_programme_2026-11-13_bank_A_stack_features.csv`, the same
stores the B-FIX-1 and Phase-2 gates ran on):

| Line | Legs | Jan–Oct total |
|---|---:|---:|
| TUNED STACK v2 (control) | 111 | **+₹127,351.50** |
| Stack + B-FIX-1 | 94 kept | **+₹131,510.00** |
| Stack + confidence ≥ 0.5 (full factors) | 88 kept | **+₹122,337.50** (WR 62.5%, ₹1,609.70/trade-day) |
| Legacy BNF-PAPER-V1 frame | 99 | **+₹83,650.50** |

Control detail (Phase-2 reproduction): 89 trade-days ·
₹1,430.92/trade-day · WR 59.5% · H1 +₹83,082.00 / H2 +₹44,269.50 ·
ex-top-3 +₹100,528.50 · zero red months · 60G/29R/116NT of 205 days.
If any anchor fails to reproduce, the run stops and reports — no
scoring.

## STEP 1 — ANATOMY (runs first; it may add ONE dial, D5)

Every November Bank leg, Nov 2–16, across the three lines —
stack (`november_shadow_stack_bank_log.csv`), legacy PRIMARY
(`november_paper_bank_log.csv`), repaired (the stack legs under
B-FIX-1; a filter on the same legs, shown as flags, not new legs).
For each leg, from the stored 5-min premium candles
(`november_shadow_data/`): entry time/premium, side, strike,
premium band (<₹500 / ₹500–800 / >₹800), day gap% (frozen regime
file), max favourable excursion (MFE, points, and its bar time =
the turn), max adverse excursion (MAE, points, and its bar time),
recorded exit. MFE/MAE are measured over the bars from the entry
bar through the exit bar inclusive. The anatomy answers, with
numbers: how many losers were ever in profit and by how much;
when they turned; and, per dial below, how many November winners
it would have killed and how many losers it would have saved.
November is diagnosis and counterfactual only — it selects
nothing; every dial is gated on Jan–Oct.

## STEP 2 — THE DIALS (all on TUNED STACK v2, Jan–Oct gated store)

### D1 — COMBINED REPAIR: B-FIX-1 + confidence ≥ 0.5 together
A leg is KEPT iff it survives BOTH: (a) not the B-FIX-1 cell
(side = PE AND gap% < 0 AND entry premium ∈ [₹500, ₹800]), AND
(b) composite confidence score ≥ 0.5, scored with the Phase-2
build's `score_leg` verbatim (full Jan–Oct factors F1–F6:
agree, premium-vs-median ₹692.50, tod bucket, gap alignment,
second-leg flag, anchor outcome). The two proven improvements
were only ever scored separately; this scores the combination.
**Forward caveat (stated wherever D1's November/forward numbers
appear):** the forward shadow basis can only score F2+F3+F4 —
F1 (`agree`) and F5/F6 (second/anchor) are not carried in the
November shadow log and are set to their neutral 0, exactly as
`bank_confgate_shadow_score.py` does. The Jan–Oct gate uses the
full factors; the forward shadow uses the November basis. They
are different bases and are never mixed in one number.

### D2 — LATE-ENTRY BAR (two cuts, scored as separate rows)
- **D2a:** no stack entries at/after **11:30** — drop legs with
  entry_time ≥ 11:30.
- **D2b:** no stack entries at/after **12:00** — drop legs with
  entry_time ≥ 12:00.
Distinctness: this is a clock cut on the final book's legs, not a
signal-class or admission filter (every signal class keeps
trading before the cut) and not any gated variant on record.

### D3 — TIME-STOP EXIT (two check times, scored as separate rows)
- **D3a:** check bar = first bar at/after **11:30**. **D3b:** 12:00.
- Rule (per leg, entries and leg set unchanged): let B* be the
  first bar of the leg's own premium series with time ≥ the check
  time. The rule applies only if entry_time ≤ check time. If the
  leg's recorded incumbent exit is strictly after B* (i.e. the leg
  was still open at B*'s close under the incumbent geometry — an
  incumbent exit ON B* is an intrabar level exit and the leg was
  not open at the close) AND B*'s close < entry premium, the leg
  exits at B*'s close with reason `time_stop`, net recomputed as
  (close − entry) × 30 − ₹220. Otherwise the recorded exit stands.
- **Difference from the closed FE-1/2/3 tests (checked against
  `tuning_bank_fast_2026-11-12.md` before freezing this dial):**
  FE-1/2/3 REPLACED the entire exit geometry of every leg (new
  targets/stops +50/−50, +30/−40, breakeven-arm +30) and truncated
  ALL legs unconditionally at the close of bar 2–3 after entry
  (~10–15 minutes), whatever their P&L. D3 changes no level (the
  −50 stop / +90 target / runner geometry is untouched), fires at
  a fixed CLOCK time hours after entry (not a bar count), and
  fires only on legs that are still open AND below their entry
  premium at that moment — a leg above entry at the check bar is
  completely untouched. Conditional clock check ≠ unconditional
  bar-count truncation with replaced geometry. D3 is therefore
  NOT a retest of FE-1/2/3.

### D4 — NS1-SECOND-LEG SURGERY (two rows)
- **D4a:** the stack without its NS1 second legs — drop all
  family = `NS1_second` legs (13 in the gated store).
- **D4b:** NS1 second legs only before 12:00 — drop `NS1_second`
  legs with entry_time ≥ 12:00; all other legs untouched.
Motivation (diagnosis, not evidence): November's legacy bleed is
concentrated in NS1 legs (Nov 3, 4, 16 stopped −₹1,720 each; the
two NS1 wins were afternoon entries Nov 11/12). Jan–Oct decides.

### D5 — (only if the Step-1 anatomy shows a sharper dial)
At most ONE extra dial, entry-knowable only, justified by named
anatomy numbers, frozen in an appended section of this spec
BEFORE any scoring runs. If the anatomy shows nothing sharper,
there is no D5 and that is stated.

## D5 DECISION (recorded 2026-11-16, after the Step-1 anatomy,
## before the dial scoring was read)

**No D5. The anatomy shows no sharper entry-knowable dial than
D1–D4, and inventing one from 11 November legs would be fitting
November — which this spec forbids.** The numbers behind the
decision: 7 of November's 8 losing legs (both lines) were
technically "ever in profit", but their max favourable excursions
were 0.0 / 3.35 / 10.45 / 13.25 / 24.6 / 39.2 / 44.4 points — the
turn came on the entry bar or within 15 minutes on every loser.
The losers were dead on arrival; no exit-side or protection dial
can rescue a leg that never travels (and the breakeven-arm family
is FE-3, already closed). On the entry side, November's losers
span every premium band, both gap signs, and entry times from
10:20 to 13:40 — no entry-knowable cell separates them that D1/D2
do not already cover. The dials stand as frozen: D1, D2a, D2b,
D3a, D3b, D4a, D4b.

## CLOSED SURFACES — not retested in any framing
Entry conditioning on buildup/OI/volume/speculation (Phase 3/3B) ·
vote-agreement (TRIO-IND) · VIX filters · signal-class/admission
filters already gated · gap-regime guard · ROLL10. If a dial
collapses into one of these, it is named and dropped.

## THE GATE (frozen; bars do not move)

**Stand-down dials (D1, D2a, D2b, D4a, D4b)** — PASS iff ALL hold:
1. **Total** ≥ 90% of the control total (≥ ₹114,616.35).
2. **Placebo:** candidate total > 95th percentile (linear
   interpolation, the books-fix convention) of 200 seeded random
   stand-downs of the same dropped-leg count k from the 111 legs
   (seeds 1000–1199, uniform sample without replacement per draw).
3. **Halves:** H1 (Jan–May) > 0 AND H2 (Jun–Oct) > 0.
4. **Month table:** no red month (the control has none).
5. **Ex-top-3:** total minus the 3 largest legs > 0.
6. **₹900 trade-day basis:** candidate total / its own trade-days
   ≥ ₹900.
7. **Audits:** timing (every kept leg's recorded exit ≥ entry —
   inherited from the gated store and re-verified); independent
   re-sum of the candidate's written trades CSV reproduces its
   total exactly.
D1 candidacy note (frozen): a D1 gate PASS makes it a December
candidate only if it is NOT dominated by the already-running
B-FIX-1 repair on both total and ₹/trade-day — the comparison
against both parents (B-FIX-1 alone; confidence alone) is
reported either way.

**Exit dial (D3a, D3b)** — PASS iff ALL hold:
1. **Total** must BEAT the control total (+₹127,351.50). An exit
   change that loses money is not a fix.
2. **Placebo (timing):** candidate total > 95th percentile
   (linear interpolation) of 200 seeded draws (seeds 2000–2199)
   of the random-check-bar twin: per draw, each leg with ≥1 bar
   strictly between its entry bar and its incumbent exit bar gets
   one such bar drawn uniformly; if that bar's close < entry
   premium the leg exits there at that close, else its incumbent
   net stands; legs with no such bar keep their incumbent net in
   every draw. This tests whether the 11:30/12:00 clock reading
   itself carries the value, vs exiting underwater legs at
   arbitrary times.
3. **Halves** both > 0. 4. **No red month.** 5. **Ex-top-3 > 0.**
6. **₹/trade-day ≥ ₹900** (trade-days unchanged — same leg set).
7. **Audits:** timing (no exit before entry; every `time_stop`
   exit is on a bar after the entry bar or the entry bar itself
   when entry_time = check time); fill (every `time_stop` exit
   premium equals that bar's close in the leg's own series);
   causality (each leg's D3 outcome depends only on bars ≤ B*);
   independent re-sum from the written trades CSV.

**November counterfactual** is computed and reported for every
dial (stack legs Nov 2–13 from the shadow log; D3 from the stored
November premium candles). It is never a gate leg.

## If a dial passes
Build its score-only forward-shadow scorer + seeded ledger
(Nov 2–16 counterfactual rows labelled BACKFILL_COUNTERFACTUAL)
and report the exact cron line the parent should add (a 19:xx IST
slot after the existing evening chain). This programme does NOT
create the cron and does NOT touch any running job or ledger.

## Deliverables
`bank_fix_SPEC.md` (this file) · `bank_fix_2026-11-16.md`
(anatomy + every dial's gate table + plain verdict per dial) ·
`bank_fix_results.json` · `bank_fix_anatomy_november.csv` ·
per-dial trades CSVs (for the re-sum audit).
