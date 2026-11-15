# NOVEMBER BOOKS FIX — 2026-11-14

**Owner order (2026-11-14 07:51 IST): the current state is NOT
approved — in November the Bank and Nifty books show mostly red
days, and it is to be FIXED under the standing free hands granted
07:20. The brake/regime armour delivered this morning protects
live money but does not change the books losing in this market;
this run addresses the books themselves.**

**Real money: ₹0 throughout. Paper only.** Every figure is option
premiums **per 1 lot** (Bank Nifty lot 30, Nifty lot 65), cost
**₹220/trade** inside every net, UNIQUE-ONCE counting, option
BUYING only. Segments are reported separately and never pooled.
November evidence is reported as counterfactual only — **November
sets no rule**; every repair below is frozen from, and gated on,
Jan–Oct 2026 stored legs.

Standing anchors (re-summed in this run before anything else):
Bank TUNED STACK v2 **111 legs, +₹127,351.50** · Bank legacy
v21 frame **99 legs, +₹83,650.50** · Nifty TUNED v1 **74 legs,
+₹103,050.25** · Nifty DEC-S1 (control) **97 legs, +₹91,168.50**
(DEC-S1 re-scored deterministically in-run: NC 0, total exact).

---

## PHASE 1 — LEG-LEVEL LOSS ANATOMY (Jan–Oct, stored legs only)

Every leg of the four books was split by **side (CE/PE) × day-type
(regime-like / non-regime, the frozen definition of
`november_regime_fix_2026-11-14.md`) × entry-time bucket
(pre-11:00 / 11:00–12:30 / post-12:30) × exit class (entry-bar
stop / later stop / target / runner-stop / square-off)**.
Exit-class mapping, frozen here: `stop`/`be_stop` → entry-bar stop
iff exit_time = entry_time, else later stop; `target`/
`runner_target` → target; `runner_stop`/`lock_stop` →
runner-stop; `square_off`/`runner_square_off` → square-off.
Full leg table: `november_books_fix_anatomy_legs.csv`; full
4-way cross: `november_books_fix_anatomy_cells.csv`.

### The naming the brief asks for — full-cross losing cells (≥10 legs, net < 0)

| Book | Cell (side / day-type / bucket / exit) | Legs | Net ₹ | WR |
|---|---|---:|---:|---:|
| Bank stack | PE / non-regime / pre-11:00 / later stop | 10 | −17,200.00 | 0% |
| Bank legacy | PE / non-regime / pre-11:00 / later stop | 12 | −20,640.00 | 0% |
| Bank legacy | PE / regime / pre-11:00 / later stop | 16 | −27,520.00 | 0% |
| Nifty TUNED v1 | CE / regime / pre-11:00 / later stop | 13 | −35,360.00 | 0% |
| Nifty DEC-S1 | CE / regime / pre-11:00 / later stop | 13 | −35,360.00 | 0% |
| Nifty DEC-S1 | PE / regime / pre-11:00 / later stop | 11 | −34,920.00 | 0% |

**Read this table correctly:** every one of these cells is a
*stop-exit* cell. A full stop is −₹1,720 (Bank) / −₹3,470 (Nifty)
by construction, so a stop cell is negative by definition — it is
the cost side of the same legs whose runner-stop/target cells
carry the books (stack runner-stops +₹80,810 on 37 legs, targets
+₹96,640 on 23). No stand-down can be conditioned on an exit
class, because the exit is not knowable at entry. These cells
diagnose *where the toll is paid*; they are not, by themselves,
repairable. The repairable map is the next table — the same legs
cut by features that ARE knowable at the entry moment (side,
overnight gap, entry premium, entry time), with all exits pooled.

### The repairable map — entry-knowable losing cells (all exits pooled)

| Book | Entry-knowable cell | Legs | Net ₹ | WR | Note |
|---|---|---:|---:|---:|---|
| **Bank stack** | PE × gap down (gap% < 0) × entry premium ₹500–800 | 17 | **−4,158.50** | 35.3% | Neighbours thrive: PE down-gap <₹500 = +₹33,677.00/16 (WR 75.0%); PE down-gap >₹800 = +₹30,840.00/18 (WR 72.2%). The hole is the mid-premium band on down-gaps only |
| Bank legacy | PE × entry premium ₹500–800 (any gap) | 25 | −9,967.00 | 36.0% | Same band weakness in the control frame; the stack's version of the band is +₹7,627.00/35 only because its down-gap half is offset by gap-up legs (+₹11,785.50/18) |
| **Nifty TUNED v1** | CE × gap up (gap% > 0) | 8 | **−14,119.75** | 12.5% | Spans two components: A/Volrix CE 5 legs −₹5,994.50; C expiry-sleeve CE 3 legs −₹8,125.25. Mirror cell CE × gap down = +₹46,725.75/33 (WR 54.5%) — the book's second-best cell. Sign-specific, not side-specific |
| Nifty TUNED v1 | CE × component A | 10 | −2,560.75 | 30.0% | Subsumed by the gap cell above (its gap-down half earns; its gap-up half is −₹5,994.50) |
| Nifty TUNED v1 | CE × component C | 5 | −10,339.75 | 0.0% | Its gap-up half (−₹8,125.25/3) is inside the repair cell; its gap-down half is 2 legs −₹2,214.50 |
| Nifty DEC-S1 | PE × component B | 23 | −11,881.75 | 34.8% | The already-proven B-PE leak — already removed in TUNED v1; listed for completeness, not a repair target |
| Bank stack | CE × reversal-only days | 6 | −1,920.00 | 33.3% | Diagnostic only — the post-11:00 reversal is not knowable at a morning entry, so no rule may condition on it |

Everything else at entry-knowable granularity is positive in both
lead books: the stack earns on regime days (+₹68,669.50) and
non-regime days (+₹58,682.00), on both sides, in every entry
bucket; TUNED v1 likewise (regime +₹42,526.25, non-regime
+₹60,524.00). There is no broad stand-down available that does
not destroy profit — the repairs below are therefore narrow,
cell-shaped stand-downs, one per index.

### Parallel books — Bank stack + REGIME-REV (descriptive, day-level)

REGIME-REV (Bank standalone GATE PASS 2026-11-14 morning;
+₹15,872.00 / 31 legs Jan–Oct) run as a parallel book beside the
stack — day nets added per calendar day. **This is a descriptive
combination of two standalone books, not a merge test** (the
registered merge test already FAILED this morning: REGIME-REV's
stack-idle-day increment is −₹2,808.00, because 16 of its 31 legs
sit on stack-busy days where a single-capital book could not take
both). Counted over the 203 classified Jan–Oct days:

| Line | Total ₹ | Green | Red | No-trade |
|---|---:|---:|---:|---:|
| Stack alone | +127,351.50 | 60 | 29 | 114 |
| REGIME-REV alone | +15,872.00 | 16 | 15 | 172 |
| **Parallel combined** | **+143,223.50** | **71** | **33** | **99** |

November (9 trading days), day by day:

| Day | Stack ₹ | REGIME-REV ₹ | Combined ₹ |
|---|---:|---:|---:|
| Nov 2 | 0.00 | +2,480.00 | +2,480.00 |
| Nov 3 | 0.00 | −1,099.00 | −1,099.00 |
| Nov 4 | +2,480.00 | 0.00 | +2,480.00 |
| Nov 5 | 0.00 | +2,480.00 | +2,480.00 |
| Nov 6 | 0.00 | 0.00 | 0.00 |
| Nov 9 | −1,720.00 | 0.00 | −1,720.00 |
| Nov 11 | 0.00 | −1,720.00 | −1,720.00 |
| Nov 12 | −1,720.00 | 0.00 | −1,720.00 |
| Nov 13 | −1,720.00 | 0.00 | −1,720.00 |
| **Total / days** | **−2,680.00 · 1G/3R/5NT** | **+2,141.00 · 2G/2R/5NT** | **−539.00 · 3G/5R/1NT** |

The parallel shape fixes November's *day-count* problem (3 green
of 9, only 1 no-trade) but not its sign: −₹539.00. And it is not
deployable as stated — on stack-busy days it double-books the
same capital. It is recorded here as the brief requires: a
descriptive table, not a candidate.

---

## PHASE 2 — THE FREEZE (written before any repair is scored)

### BANK — repair B-FIX-1 (stand-down on TUNED STACK v2)

- **Rule:** a stack leg is NOT taken iff **side = PE** AND the
  day's **overnight gap < 0** (gap% vs prior close, audit
  convention, from the frozen regime-classification file) AND
  **entry premium ∈ [₹500, ₹800]** (inclusive). Everything else
  about the book is unchanged — same signals, same entries, same
  G0/runner exits.
- **Knowable at entry:** the gap is fixed at the 09:15 open; the
  entry premium is the entry bar's own open, known at the entry
  moment; the side is the leg's own. No post-entry information,
  no post-11:00 information, no November information.
- **Target cell (Jan–Oct):** PE × gap-down × premium 500–800 =
  17 legs, −₹4,158.50, WR 35.3% (Phase 1 table).
- **Why this is not a closed route:** the failed **gap-guard**
  stood down *all* legs — both sides, all premiums — on
  *top-quartile |gap|* days only, and failed because extreme-gap
  days are profitable for this book. B-FIX-1 is the opposite
  shape: it fires on *ordinary* down-gap days of any size, for
  one side and one premium band only; on top-quartile days it
  removes only that same narrow cell. It is not a signal-class /
  admission filter (every U1 signal is still admitted; the
  stand-down applies to one side × gap-sign × premium cell at
  book level), not an exit change (the T-B2 wider-stop family
  stays rejected; geometry untouched), and not a premium-band
  book (PB1/PB3/PB4 were standalone subsets traded *instead of*
  the stack; B-FIX-1 keeps the full stack minus one cell).

### NIFTY — repair N-FIX-1 (stand-down on TUNED v1)

- **Rule:** a TUNED v1 leg is NOT taken iff **side = CE** AND
  the day's **overnight gap > 0**. Everything else unchanged —
  components A, B, C all keep trading; PE legs are never touched;
  CE legs on gap-down and flat-gap (gap% = 0) days are untouched.
- **Knowable at entry:** the gap is fixed at the 09:15 open and
  every TUNED v1 leg enters at or after 09:35; the side is the
  leg's own. No other information is used.
- **Target cell (Jan–Oct):** CE × gap-up = 8 legs, −₹14,119.75,
  WR 12.5% (A/Volrix CE 5 legs −₹5,994.50; C CE 3 legs
  −₹8,125.25). The mirror cell CE × gap-down is +₹46,725.75 on
  33 legs — the stand-down is sign-specific, not a CE cut.
- **Why this is not a closed route:** it is not the B-PE removal
  (already inside v1), not a component deletion (A and C keep
  trading on gap ≤ 0 days; B is untouched), and not any gated
  Nifty variant on record — T-N1a/T-N1b were exit-geometry
  changes, T-N3 restored C CE *unconditionally* on the v2 frame.
  No gap-sign × side stand-down has been gated on TUNED v1.

### GATE (both indices, all legs frozen here, before scoring)

(i) **Total:** repaired book total ≥ 90% of the standing total
    (Bank ≥ ₹114,616.35; Nifty ≥ ₹92,745.23).
(ii) **Cell:** the target cell's post-repair contribution is
    ₹0 (its legs are stood down) — its loss is cut 100%, which
    must satisfy "≥ 0, or loss cut ≥ 50%"; the cost test is (i).
(iii) **Placebo:** 200 seeded random stand-downs of the same
    leg-count k from the same book (seeds 1000–1199, uniform
    sample without replacement per draw). The repaired total
    must exceed the **95th percentile** (linear interpolation)
    of the 200 placebo totals. A repair that merely skips
    trades fails here.
(iv) **Halves:** the repaired book's H1 (Jan–May) total > 0 AND
    H2 (Jun–Oct) total > 0.
(v) **November counterfactual (reported, not a pass/fail leg):**
    the same stand-down applied to the book's November forward
    legs, day by day over Nov 2–13 (9 trading days), against the
    actual (Bank stack −₹2,680.00, 1G/3R/5NT; Nifty TUNED v1
    +₹3,036.50 on 1 leg, 1G/0R/8NT). November gap values: Bank
    from the frozen regime file; Nifty computed from the stored
    November spot bars (`oi_history/spot_nov_bars.json`, audit
    convention — Nov 3 gap = **+0.6034%**, cross-checked against
    the failure audit's recoverable gaps: Nov 4 −0.2881%, Nov 5
    +1.7422%, Nov 6 +0.0065%, all matching).

**One repair per index. If it fails, it is reported and the run
stops there for that index — no second variant.**

---

## PHASE 2 — GATE RESULTS (run after the freeze above; programme `november_books_fix_phase2.py`)

### B-FIX-1 (Bank TUNED STACK v2) — **GATE PASS**

| Gate leg | Requirement | Result |
|---|---|---|
| (i) Total | repaired ≥ ₹114,616.35 (90% of +₹127,351.50) | **+₹131,510.00 — PASS** (the repair ADDS ₹4,158.50 on Jan–Oct) |
| (ii) Target cell | cell net after repair ≥ 0 / loss cut ≥ 50% | cell 17 legs −₹4,158.50 → **₹0, loss cut 100% — PASS** |
| (iii) Placebo | repaired total > 95th pct of 200 seeded random stand-downs of 17 legs | placebo p95 **+₹124,715.98**; repaired beats **200/200** draws — **PASS** |
| (iv) Halves | repaired H1 > 0 and H2 > 0 | H1 (Jan–May) **+₹85,880.00** · H2 (Jun–Oct) **+₹45,630.00 — PASS** |
| (v) November counterfactual | reported, not pass/fail | see below |

Cell legs stood down (Jan–Oct): 2026-02-27 ×2 (BASE (lA) −₹1,720; EVE06a −₹118), 2026-03-27 ×2 (NS3-GD −₹1,720; EVE06a +₹2,480), 2026-05-18 (V5 −₹1,720), 2026-07-08 ×2 (NS3-GD −₹1,720; EVE06a +₹2,480), 2026-07-30 (V5 −₹1,720), 2026-08-04 (Skill +₹2,480), 2026-08-07 ×2 (Skill −₹1,720; EVE06a −₹1,267), 2026-09-01 (NS1 +₹306.50), 2026-09-30 (S3-R1 −₹1,720), 2026-10-07 ((lA) −₹1,720), 2026-10-08 ×2 (Skill −₹1,720; EVE06a +₹2,480), 2026-10-13 (S3-R1 +₹2,480). The cell contains winners too (5 of 17) — the stand-down removes them as the price of the rule; the placebo leg is what proves the removal is not random luck.

**November counterfactual (v):** actual stack Nov 2–13 = **−₹2,680 (1G/3R/5NT)**. Under B-FIX-1: Nov 4 PE 715.30 (gap −0.0989%) stood down — removes the **+₹2,480 win**; Nov 13 PE 705.00 (gap −0.3543%) stood down — removes the **−₹1,720 loss**; Nov 9 (gap +0.2267%) and Nov 12 (gap +0.0155%) legs kept at −₹1,720 each. **Repaired November = −₹3,440 (0G/2R/7NT) — ₹760 WORSE than actual on these 9 days.** Stated plainly: on the days November actually dealt, this repair would not have helped. It is a Jan–Oct repair (205 days, placebo-controlled); November's remaining 10 days are its forward test.

### N-FIX-1 (Nifty TUNED v1) — **GATE PASS**

| Gate leg | Requirement | Result |
|---|---|---|
| (i) Total | repaired ≥ ₹92,745.23 (90% of +₹103,050.25) | **+₹117,170.00 — PASS** (the repair ADDS ₹14,119.75 on Jan–Oct) |
| (ii) Target cell | cell net after repair ≥ 0 / loss cut ≥ 50% | cell 8 legs −₹14,119.75 → **₹0, loss cut 100% — PASS** |
| (iii) Placebo | repaired total > 95th pct of 200 seeded random stand-downs of 8 legs | placebo p95 **+₹108,558.31**; repaired beats **199/200** draws — **PASS** |
| (iv) Halves | repaired H1 > 0 and H2 > 0 | H1 **+₹68,723.50** · H2 **+₹48,446.50 — PASS** |
| (v) November counterfactual | reported, not pass/fail | see below |

Cell legs stood down (Jan–Oct): A/Volrix CE — 2026-02-02 −₹3,470 (gap +0.115%), 2026-03-20 −₹3,470 (+0.097%), 2026-04-27 −₹3,470 (+0.174%), 2026-07-09 −₹220 (+0.139%), 2026-10-09 +₹4,635.50 (+0.374%); C sleeve CE — 2026-03-17 −₹3,470 (+0.589%), 2026-05-19 −₹2,524.25 (+0.130%), 2026-07-07 −₹2,131 (+0.166%). Note every gap in the cell is a SMALL up-gap (+0.10% to +0.59%) — this is not the extreme-gap guard in disguise; it is the ordinary up-gap morning where v1's CE legs systematically pay the toll (7 of 8 legs lost; the mirror CE × gap-down cell won +₹46,725.75).

**November counterfactual (v):** TUNED v1's actual November forward = **+₹3,036.50 (1G/0R/8NT)** on one leg — Nov 3 component-C CE 23600 (gap **+0.6034%**, computed from the stored spot bars and cross-checked against the failure audit's neighbouring days). That leg is a CE leg on a gap-up day → **stood down under N-FIX-1. Repaired November = ₹0 (0G/0R/9NT).** Stated plainly: the repair removes November's only Nifty win so far. Same discipline as Bank: the rule is earned on 205 Jan–Oct days, not on 9 November days; Nov 16–30 is the forward test.

---

## PHASE 3 — APPLICATION (done 2026-11-14, for Mon 2026-11-16)

**(a) NIFTY LEAD SWITCH — DONE.** How TUNED v1's forward legs are produced (established from the machinery): there is no TUNED v1 scorer of its own. The 15:32 shadow-scoring job scores DEC-S1 into `november_shadow_decs1_nifty_log.csv`; TUNED v1's forward line has been a **drop-only derivation** from that log — v1 = every DEC-S1 row except component-B PE rows (the derivation used in `nifty_900_tradeday_2026-11-13_results.json`'s `november_forward` block, which keeps exactly the Nov 3 C CE leg). That derivation is now a standing machine (`nifty_nfix1_score.py`, below), so v1's forward legs are produced every evening, not reconstructed after the fact. **From Mon 2026-11-16 TUNED v1 (+ N-FIX-1) is Nifty's LEAD November book; NF-PAPER-C3G7 continues as a scored control line.** Recorded with dated entries in `november_paper_MAP.md` and `segment_floor_tracker.md`. The daily-stats job (`november-paper-daily-stats`) is where the lead line is presented: its body was read first, amended with a books-fix section (Bank repaired-lead line added; Nifty section head switched, C3G7 demoted to the labelled control line "NF-PAPER-C3G7 (frozen primary to 13 Nov, now control line)"), and read back to verify — no existing scoring line removed or altered.

**(b) REPAIRED LINES STOOD UP — BOTH (both gates passed).**
- Bank: `bank_bfix1_score.py` reads the day's stack legs from the stack's own ledger (never modifies it), applies B-FIX-1, writes `november_repaired_bfix1_bank_log.csv`; job **`bank-bfix1-scorer-daily` 18:50 IST Mon–Fri** from Mon 2026-11-16. Label: **REPAIRED LEAD — TUNED STACK v2 + B-FIX-1**. The original stack keeps scoring untouched as the primary/control line — the Nov 20 checkpoint and Nov 30 verdict stay producible on it.
- Nifty: `nifty_nfix1_score.py` derives the day's TUNED v1 legs from the DEC-S1 ledger, applies N-FIX-1, writes `november_repaired_nfix1_nifty_log.csv` (carries both the v1-original and repaired day nets); job **`nifty-nfix1-scorer-daily` 19:05 IST Mon–Fri** from Mon 2026-11-16. Label: **LEAD — TUNED v1 + N-FIX-1 (repaired lead)**; TUNED v1 original + C3G7 + DEC-S1 keep scoring as control lines.
- **Dry-runs (required before scheduling — both reproduce the Phase-2 counterfactuals EXACTLY):** Bank backfill Nov 2–13: stack −₹2,680.00 → repaired **−₹3,440.00**, stood down Nov 4 (+₹2,480) and Nov 13 (−₹1,720), in-scorer assertion passed. Nifty backfill Nov 2–13: TUNED v1 +₹3,036.50 → repaired **₹0.00**, Nov 3 leg stood down, in-scorer assertion passed; the scorer's computed November gaps reproduce the audit-verified values day by day (Nov 3 +0.6034%, Nov 4 −0.2881%, Nov 5 +1.7422%, Nov 6 +0.0065%). Backfill rows in both ledgers are marked `BACKFILL_COUNTERFACTUAL` and never enter the live MTDs, which start at zero on 2026-11-16.
- Gap handling going forward: each scorer establishes the day's gap from stored spot (frozen regime file for November Bank days → November spot-bars store → persisted progressive spot file). If a gap cannot be established on a day with legs at risk, the day is marked **NC_GAP** and no repaired figure is produced — never estimated.

**(c) FAILED-REPAIR BRANCH — not triggered** (both gates passed). The December consequence of the passes: each repaired configuration is its index's December adoption candidate, decided at the Nov 30 verdicts on the Nov 16–30 forward record; if that record does not support a repaired line, the standing book (stack v2 / TUNED v1) remains the candidate. The three-leg circuit breaker (incl. HWM-DD) binds the December layer either way. Paper only throughout; real money ₹0.

## Deliverables of this run
`november_books_fix_2026-11-14.md` (this file) · `november_books_fix_results.json` · `november_books_fix_anatomy_legs.csv` · `november_books_fix_anatomy_cells.csv` · `november_books_fix_repair_bank_legs.csv` · `november_books_fix_repair_nifty_legs.csv` · programmes `november_books_fix_phase1.py`, `november_books_fix_phase2.py` · scorers `bank_bfix1_score.py`, `nifty_nfix1_score.py` · ledgers `november_repaired_bfix1_bank_log.csv`, `november_repaired_nfix1_nifty_log.csv`.
