# BANK ₹2,000/DAY PROGRAMME — 2026-11-13

**Owner order 2026-11-13 15:21 IST:** Bank Nifty INDIVIDUALLY ≥ ₹2,000/day —
"minimum profit would be 2000, that's a minimum movement it will give."
Bank only. Pure option BUYING. Paper only, real money ₹0. 1 lot (30),
₹220/trade inside every net. Nothing in this programme touches a running
book, job, FREEZE or settlement file.

**Where Bank stands (anchors, asserted in-run before scoring):**
- TUNED STACK v2 (primary): 111 legs, **+₹127,351.50** Jan–Oct = ₹621/day,
  gate PASS (standing).
- Legacy B2/NS1 frame (BNF-PAPER-V1): 99 legs, **+₹83,650.50** = ₹408.05/day,
  20.5% of days ≥ ₹2,000, gate PASS (daily-earner build).
- Gap to the owner's bar ≈ **₹1,379/day** on the stack, ₹1,592/day on legacy.
  One NS1 target win = +₹2,480 — winners are big enough; winning-DAY
  frequency is the gap. This programme attacks exactly that.

---

## §0 PRE-REGISTRATION (written before any configuration was scored)

**Parents (frozen ledgers, read-only):**
- STACK stream = `solid60_programme_2026-11-13_bank_A_stack_features.csv`
  (111 legs, X-1 incumbent exits; anchor +₹127,351.50 asserted exact).
- LEGACY stream = `bank_engine_r6_v21_trades.csv`
  (99 legs; anchor +₹83,650.50 asserted exact).

**Denominator:** 205 trading days, Jan–Oct 2026 (the workspace convention —
both standing ₹/day figures use it). Day metrics are computed over all 205
days, zero-trade days included.

**Dedupe rule (union configurations):** two legs are the same leg iff
(date, direction, entry_time, entry_premium) are all equal. On collision the
STACK copy is kept (the stack is the primary book). Inventory found 87
identical-key collisions between the parents, of which 4 carry different
nets under the two books' exit geometries (disclosed in §3) — the rule above
decides them, registered here before the union was totalled.

**Configurations (the complete list — nothing else is scored):**
- **PB1** — STACK legs with entry_premium < 500.
- **PB2** — STACK legs with entry_premium < 650.
- **PB0** — LEGACY legs with entry_premium < 500.
- **PB3** — UNION (deduped) legs with entry_premium < 500.
- **PB4** — UNION (deduped) legs with entry_premium < 650.
- **U1** — UNION (deduped), no band filter.

**Band edges:** 500 is the SOLID-60 split's core edge (measured descriptively
there, never registered as a book: stack legs < 500 ran WR 75.0%,
+₹69,749.50 / 32 legs; 500–750 was the worst band, 43.8%). 650 is registered
as the extension edge because the SOLID-60 mid band splits at it: 500–650 =
17 legs, WR 52.9%, +₹6,622.00 vs 650–750 = 15 legs, WR 33.3%, +₹465.00.
No other edge is tested.

**Feature-timing audit (registered):** entry_premium is the open of the
entry 5-minute candle (the frozen convention) — the band is knowable at the
moment of entry, from the quote the order is placed at. Union identity
fields are all entry-time facts. No leg may be invented, dropped silently,
or have its net altered: every configuration leg is verified verbatim
against its parent ledger in-run.

**Gate (every configuration, same run — bars fixed here):**
- A. Parent anchors re-summed exact.
- B. Leg-integrity audit: 0 invented / 0 altered legs.
- C. Total > 0.
- D. Both calendar halves > 0 (H1 = Jan–May, H2 = Jun–Oct).
- E. Ex-top-3 > 0.
- F. Consistency: red months ≤ 4 of 10; worst month named either way.
- G. Random-density placebo (subset configurations PB0–PB4): 2,000 draws,
  seed 42, same-count random subsets of the configuration's own parent pool
  (STACK for PB1/PB2, LEGACY for PB0, the deduped UNION pool for PB3/PB4);
  the configuration's total must exceed the draws' 95th percentile.
  For U1 (density 100% — a random subset of the pool is the pool) the
  placebo is degenerate by construction; U1's binding extra leg instead:
  its total must exceed BOTH parents' totals — packaging that does not
  beat its best parent fails.
- H. Delay-1 placebo: registered NOT APPLICABLE to recorded-geometry legs
  (SOLID-60 registered precedent: recorded exits cannot be re-based one
  bar later; the random-density placebo binds). Stated, not skipped
  silently.
- I. Independent re-sum: every written trade CSV is re-read and re-summed
  by a separate pass; totals must match to the paisa.

**Metrics reported per configuration:** legs, WR, total, ₹/day (÷205),
% of days ≥ ₹2,000, % of days > 0, % of zero-trade days, median day,
worst-decile mean day, worst day, month table, halves, ex-top-3, placebo
result, gate verdict with the killing leg named where it fails.

**Owner's-target verdict (separate from the gate):** a configuration can
pass the controls gate and still fall short of ₹2,000/day. Both are stated:
gate PASS/FAIL, and the remaining gap to ₹2,000/day in ₹/day.

**November counterfactual:** Nov 2–12 frozen logs (stack:
`november_shadow_stack_bank_log.csv` incl. retrospective backfill rows;
legacy: `november_paper_bank_log.csv`, PRIMARY channel only — CONTROL rows
are the same trades under a control label and are never counted). Nov 13
excluded: its EOD logs were not final at build time. Day-by-day cumulative
per configuration; progressive / degradative / absent stated plainly.

**Route 3 (OI):** the OI build-up programme's history dataset exists
(`oi_history/banknifty_daily_oi.csv`) but its gated Bank result does NOT —
`oi_buildup_programme_2026-11-13.md` Part 2 was registered this morning and
its results sections are still empty; no `oi_buildup_trades.csv` /
`oi_buildup_results.json` exists. **OI line: PENDING** — no OI stream is
included in any union in this programme, and none was built here.

---

## §1 VERDICT — BANK INDIVIDUALLY vs ₹2,000/DAY

**No configuration in this programme reaches ₹2,000/day — and no new
configuration beats the book that already runs.** The best PASSING new
configuration is **PB4 (union of both books, legs admitted only below
₹650 entry premium): +₹82,611.50 Jan–Oct = ₹402.98/day**, 11.7% of days
≥ ₹2,000 — a remaining gap of **₹1,597/day**. The running stack remains
Bank's best line at **₹621/day** (48 days ≥ ₹2,000, 23.4%), a gap of
₹1,379/day. The full stack + legacy pool, deduped, is 123 legs in 205
days — **0.6 legs/day is the entire signal flow both books produce.**
Averaging ₹2,000/day needs +₹410,000 across Jan–Oct; the whole pool is
worth +₹118,111.50. The gap is signal FREQUENCY, not winner size and not
admission quality — the band results below prove admission quality is
real (75% win rate, placebo rank 99.7th percentile) and still lands at
₹340/day, because a < 500 book trades 32 times in 205 days.

## §2 ROUTE 1 — PREMIUM-BAND BOOKS

| Config | Legs | WR | Total ₹ | ₹/day | Days ≥2k | Zero-trade days | Red months (worst) | Placebo rank | GATE |
|---|---|---|---|---|---|---|---|---|---|---|
| **PB1** stack <500 | 32 | **75.0%** | +69,749.50 | 340.24 | 19 (9.3%) | 86.3% | **0** (worst Mar +760) | 99.7th pct | **PASS** |
| PB2 stack <650 | 49 | 67.3% | +76,371.50 | 372.54 | 23 (11.2%) | 80.0% | 1 (Jul −2,339) | 93.0th pct | **FAIL — placebo** |
| PB0 legacy <500 | 27 | 66.7% | +59,902.50 | 292.21 | 16 (7.8%) | 87.8% | 3 (Aug −3,440) | 99.7th pct | **PASS** |
| PB3 union <500 | 35 | 71.4% | +75,989.50 | 370.68 | 20 (9.8%) | 84.9% | 1 (Aug −960) | 99.7th pct | **PASS** |
| **PB4** union <650 | 52 | 65.4% | +82,611.50 | **402.98** | 24 (11.7%) | 78.5% | 1 (Jul −4,059) | 98.5th pct | **PASS** |

- **PB1 is exactly the SOLID-60 concentration, now registered and gated:**
  it passes every leg — halves +₹44,725.00 / +₹25,024.50, ex-top-3
  +₹42,926.50, **zero red months**, random subsets of the stack beat it
  only 0.3% of the time. The < 500 premium band is a real quality filter.
  It is also a part-time book: median day ₹0, 86.3% of days it does not
  trade at all, worst-decile day mean −₹458.75, worst day −₹1,720.
- **PB2 FAILS** on the random-density placebo alone (total +₹76,371.50 ≤
  p95 +₹78,612.50): on the stack parent, the 500–650 extension legs add
  money that random stack legs of the same count usually add too. The
  same < 650 cut on the union parent (PB4) passes — its placebo pool is
  the union, whose random draws are diluted by the weak legacy-only legs.
  Both results are reported as registered; the difference is the parent
  pool, not a moved bar.
- Adjacent-band check (reported, not gated): the 500–750 band on the
  stack = +₹7,087.00 / 32 legs; on legacy = −₹7,287.00 / 21 legs. The
  < 500 core beats its neighbouring band decisively on both parents.
- **The floor, honestly (the owner's word is "minimum"):** every band
  book's median day is ₹0. These books do not produce a daily minimum —
  they produce occasional large days (best day +₹9,680) separated by
  long flat stretches. No configuration in this programme — band, union,
  or the incumbents — has a positive daily floor: the stack's own
  worst-decile day mean is −₹2,171.10 and its worst day −₹3,440.

## §3 ROUTE 2 — UNION LINE (stack + legacy, UNIQUE-ONCE)

**U1: 123 legs, +₹118,111.50 = ₹576.15/day, 49 days ≥ ₹2,000 (23.9% —
the best day-frequency of anything scored), GATE FAIL.** It fails its
registered binding leg: the union does not beat its best parent. The 12
legacy-only legs (the ones the stack does not take) are worth
**−₹9,240.00** combined — bolting the legacy book onto the stack
subtracts money. The 87 shared legs were deduped once, stack copy kept;
4 shared legs carry different nets under the two exit geometries
(2026-04-13 CE: stack +₹5,180 vs legacy +₹2,480 · 2026-07-15 PE: stack
+₹5,180 vs legacy +₹2,480 · 2026-02-05 PE: stack −₹220 vs legacy +₹560 ·
2026-07-02 PE: stack −₹220 vs legacy −₹1,720 — disclosed per §0).
Verdict as registered: **this is two books' union, not a new edge — and
as a union it is worse than the stack alone.** The stack already contains
everything in the legacy book that pays.

## §4 ROUTE 3 — OI LINE

**OI PENDING.** The gated OI Bank result does not exist yet (registered
this morning; results sections empty; no trades/results files). No OI
stream was built or included here, per the programme's limits. When the
OI programme lands a gate-passing Bank stream, a union test against PB4
is the registered next step — it is the only identified source of NEW
signal frequency, which is what the ₹2,000/day gap is actually made of.

## §5 NOVEMBER 2–12 COUNTERFACTUAL (day-by-day, frozen logs)

| Line | Legs | Total ₹ | Shape |
|---|---|---|---|
| PB1 / PB2 / PB0 / PB3 / PB4 (all band books) | **0** | **0.00** | **ABSENT** |
| U1 union | 8 | −1,160.00 | degradative to Nov 9 (−4,400), partial recovery, ends negative |
| Ref: stack alone | 3 | −960.00 | +2,480 Nov 4 → −1,720 Nov 9 → −1,720 Nov 12 |
| Ref: legacy alone | 6 | −1,920.00 | four stops, then the two NS1 wins (+2,480 × 2) |

Cumulative U1 by day: Nov 2 −1,720 · Nov 3 −3,440 · Nov 4 −2,680 ·
Nov 5 −2,680 · Nov 6 −2,680 · Nov 9 −4,400 · Nov 11 −1,920 · Nov 12 −1,160.

**The band books' November is the sharpest fact in this programme:**
every one of the 9 November parent legs entered at a premium between
₹681.95 and ₹867.60 — not one leg, on either book, was admitted by any
band below ₹650. In November the premium-band book places **no trade at
all**. Its ₹0 is arithmetically better than the incumbents' −₹960 /
−₹1,920, but it is absence, not progress: a book that sits out the month
cannot be the owner's daily earner, and November's premiums (a high-spot,
high-premium regime — Bank at 59–61k) are exactly when the band binds
hardest. The two NS1 wins the owner watched (+₹2,480 each) were entered
at ₹823.10 and ₹710.00 — outside every band tested.

## §6 WHAT THIS MEANS FOR THE ₹2,000/DAY ASK

1. Admission quality is SOLVED and proven: below ₹500 premium, Bank legs
   win 75% and pass the full gate with zero red months. If a Bank leg is
   cheap, it is usually good.
2. Frequency is the whole gap: 0.6 legs/day exist across both books.
   ₹2,000/day at the pool's average leg value (~+₹960) needs ~2
   legs/day. No filter on the existing streams creates legs.
3. The only routes to frequency are new signal sources (OI — pending)
   or accepting the stack as-is at ₹621/day with 23.4% of days ≥ ₹2,000
   and judging it on its average, not on a daily minimum it has never
   had in any month of its gated record.

## §7 PAPER-WIRING SPEC — PREPARED, NOT STARTED (PB4, best passing)

For the parent, if the owner approves a PB4 forward paper run:
- **Rule (frozen):** each trading day, take the TUNED STACK v2 live
  assembly's legs and the legacy BNF-PAPER-V1 legs; dedupe on
  (date, direction, entry_time, entry_premium), stack copy kept; ADMIT
  only legs whose entry premium (open of the entry 5-min candle) < ₹650;
  exits = the admitting book's own frozen geometry per leg (stack legs
  keep stack exits, legacy-only legs keep G0); 1 lot; ₹220/trade.
- **Scoring:** reuse `november_shadow_score.py` patterns; new log
  `november_shadow_pb4_bank_log.csv`, journal section in
  `november_journal_bank.md`; scored_live flag per row as with the stack.
- **Reporting:** Bank section line under the stack primary in the 15:45
  daily stats: legs, day net, MTD, % of days ≥ ₹2,000 — labelled SHADOW.
- **Kill/keep (pre-registered):** judge after 20 trading days — keep
  only if its forward ₹/day exceeds the stack's forward ₹/day over the
  same days AND it traded on ≥ 15% of days (the November absence risk);
  otherwise close it and the band finding stays a filter fact, not a book.
- PB1 (stack < 500) is the alternate passing core if the owner prefers
  purity over PB4's extra ₹62.74/day: same wiring, band < 500, stack
  legs only.

## FILES

- This report: `bank_2000_programme_2026-11-13.md`
- Build: `bank_2000_build.py` → `bank_2000_results.json`
- Trade lists: `bank_2000_PB1_stack_lt500_trades.csv` ·
  `bank_2000_PB2_stack_lt650_trades.csv` ·
  `bank_2000_PB0_legacy_lt500_trades.csv` ·
  `bank_2000_PB3_union_lt500_trades.csv` ·
  `bank_2000_PB4_union_lt650_trades.csv` ·
  `bank_2000_U1_union_all_trades.csv`
  (every CSV independently re-summed exact against its scored total)

