# LADDER-BANK BUILD — 2026-11-03

## VERDICT: STOPPED BEFORE SCORING — pre-registered stop rule triggered

**No ladder number exists and none is quoted.** The build brief required the
premium reconstruction to reproduce each v21 leg's recorded entry premium
before any scoring, with a hard stop if reconstruction failed on >10% of
legs. **Reconstruction failed on 31 of 99 legs (31.3%).** The build was
halted at the audit stage, exactly as pre-registered. Nothing was armed,
no cron was created, no November book or log was touched.

## The locked design (approved by Chandu 2026-11-03, Bank first — NOT scored)

- Entries: the 99 causal Bank v21 legs (Jan–Oct 2026) from
  `bank_engine_r6_v21_trades.csv`, unchanged; only the exits change.
- Exits (primary): spot-stage ladder on 5-min closes — hard stop premium
  close ≤ entry − 20; T1 at spot +30 → lock entry +5; T2 at +58 → lock
  entry +15; T3 at +82 → lock entry +25; T4 at +100 → exit at that bar's
  close premium; floors ratchet only; square-off 15:10. Sensitivities
  (stop −15/−25; locks shifted ∓5) and the B2-only subset were also
  pre-registered. None of this was run.

## Benchmark verification — PASS

- `bank_engine_r6_v21_trades.csv` independent re-sum: **+₹83,650.50**
  (99 legs) — matches the frozen v21 total exactly.
- January 2026 re-sum: **+₹22,748.00** — matches exactly.
- The benchmark leg set is intact; the failure is in the premium store,
  not in the entries.

## Reconstruction audit — method

Two independent routes to each leg's contract, cross-checked:

- **Route A (blind):** monthly expiry = smallest store monthly expiry ≥
  leg date; strike searched across the whole chain for the entry-bar OPEN
  equal to the recorded entry premium.
- **Route B (pipeline leg book):** strike + expiry from
  `bank_r6_core.assemble6`'s leg book — the same reproduction
  `flaw_cycle_run.py` verified leg-for-leg against the frozen regen CSV —
  then the entry bar read from `daily2leg/prem_bank.json`.

Routes agree on all 99 legs. **Where the store contains the entry bar, the
reproduction is exact: 68/68 legs match to the paisa (|Δ| ≤ 0.005, entry
bar open — the harness's `mode='open'` fill convention), zero value
mismatches.** Contract identification is not the problem.

## The finding — a systematic store gap, not noise

- `daily2leg/prem_bank.json` contains **no premium bars before 10:00 for
  any 2026 contract-day**: all 10,226 contract-days in the store start at
  10:00 or later (earliest first bar 10:00; the affected contract-days hold
  exactly 64 bars, 10:00–15:15).
- All 31 failed legs entered between **09:20 and 09:55**. Every leg entered
  at/after 10:00 reconstructed exactly; every leg entered before 10:00
  failed. The split is perfectly clean.
- Failed legs by family: **BASE 22 · NS3_gapclass 7 · S3-R1 2** (NS1_second:
  0 — second legs enter after 10:50).
- The 31 failed legs carry **+₹17,630.00 of the book's +₹83,650.50
  (21.1%)** under their original exits.
- `daily2leg/spot.json` is complete (75 bars from 09:15) — the gap is
  premium-only.

### Why the remaining 68 legs were NOT scored anyway

Scoring only the reconstructable legs would silently delete every
morning entry — precisely the population where the ladder's −20 hard stop
and T1 stage bind earliest — and would drop 21.1% of the book's net. The
B2 robustness subset is drawn mostly from the same morning BASE pool, so
it is hit even harder. Any number from that truncated set would be a
selection artefact, and quoting it would repeat the exact failure mode
this programme has already retracted twice. The stop rule exists for
this case; it was followed.

### Failed legs (31) — date · direction · family · entry · expiry · strike

2026-01-22 CE BASE 09:20 · 2026-01-27 · 59300
2026-02-02 PE BASE 09:45 · 2026-02-24 · 58300
2026-02-20 CE BASE 09:20 · 2026-02-24 · 60900
2026-02-27 PE BASE 09:55 · 2026-03-30 · 60800
2026-03-13 PE BASE 09:50 · 2026-03-30 · 54300
2026-03-16 CE BASE 09:20 · 2026-03-30 · 53800
2026-03-20 CE NS3_gapclass 09:35 · 2026-03-30 · 54400
2026-03-20 PE S3-R1 09:45 · 2026-03-30 · 54200
2026-03-23 PE BASE 09:50 · 2026-03-30 · 52100
2026-03-27 PE NS3_gapclass 09:35 · 2026-03-30 · 52700
2026-04-01 PE BASE 09:35 · 2026-04-28 · 51600
2026-04-10 CE BASE 09:20 · 2026-04-28 · 55600
2026-04-10 PE BASE 09:35 · 2026-04-28 · 55600
2026-05-11 CE BASE 09:20 · 2026-05-26 · 54700
2026-05-11 PE BASE 09:40 · 2026-05-26 · 54500
2026-05-18 PE BASE 09:50 · 2026-05-26 · 52800
2026-06-02 CE BASE 09:20 · 2026-06-30 · 53300
2026-06-09 PE BASE 09:45 · 2026-06-30 · 54700
2026-07-08 PE NS3_gapclass 09:35 · 2026-07-28 · 57700
2026-07-13 CE NS3_gapclass 09:40 · 2026-07-28 · 57700
2026-07-15 PE BASE 09:45 · 2026-07-28 · 58100
2026-07-24 PE BASE 09:50 · 2026-07-28 · 56100
2026-07-30 PE BASE 09:40 · 2026-08-25 · 56900
2026-08-25 CE BASE 09:35 · 2026-08-25 · 57600
2026-09-02 CE BASE 09:20 · 2026-09-29 · 57000
2026-09-17 CE NS3_gapclass 09:35 · 2026-09-29 · 56500
2026-09-24 PE NS3_gapclass 09:40 · 2026-09-29 · 55600
2026-09-28 PE NS3_gapclass 09:35 · 2026-09-29 · 54800
2026-09-29 PE BASE 09:35 · 2026-09-29 · 53900
2026-09-30 PE S3-R1 09:50 · 2026-10-27 · 54600
2026-10-07 PE BASE 09:40 · 2026-10-27 · 54700

(Full per-leg audit: `ladder_bank_reconstruction_audit.csv`.)

## What unblocks the build (owner/parent decision — not done here)

The missing bars are a store-assembly gap, not missing market data in the
workspace: `daily2leg/build_store.py` already merges
`data/banknifty-2026-MM/option_5m.csv` among its sources, and the audited
v21 pipeline's own candle route holds full-day paths for these contracts
(that is how the original exits were scored). Either:

1. backfill the pre-10:00 bars into `prem_bank.json` from the consolidated
   monthly `option_5m.csv` sources, rebuild the store, and re-run this
   audit — the build proceeds only if reconstruction then passes ≥90%
   (target: 99/99 exact); or
2. formally re-specify the build's premium source to the audited candle
   route, with the same entry-premium verification kept as the gate.

Until one of those is decided, the ladder build stays stopped and no
ladder figure of any kind should be quoted to Chandu.

## Files produced

- `ladder_bank_build_2026-11-03.md` — this report
- `ladder_bank_reconstruction_audit.py` — reproducible audit (benchmark
  re-sum assertions + two-route contract verification)
- `ladder_bank_reconstruction_audit.csv` — per-leg reconstruction status
  for all 99 legs
- `ladder_bank_reconstruction_audit.json` — audit summary

No scorer was written and no results CSV/JSON of ladder trades exists —
deliberately: the stop rule fired before scoring.

---

# CONTINUATION — 2026-11-03 (same day): backfill, re-audit, scoring, full gate

The stop above stands as the record of the first run. The parent then
authorised unblock option 1 from the section above: backfill the pre-10:00
bars from the sources `build_store.py` already declares, re-audit, and —
only if the gate passed — score the locked design unchanged. That is what
was done. Nothing was armed, no cron was created, no November book or log
was touched.

## 1. Backfill log (declared sources only, add-only)

Sources, in `build_store.py` merge order: (1) `data/banknifty-2026-MM/
option_5m.csv`; (2) the candle caches (`aggressive_data/`,
`historical_proof_data/`, `v4_options_oct_data/`,
`fix_tests_2026-11-02_cache/`, `oct2026_fresh/ext29_30/premium/`). No web
fetch, no other source. (Root cause of the gap: `build_store.py`'s KEEP
filter retains only 10:00–15:15 bars; the sources themselves hold the
full day.)

- Scope: the 31 failed contract-days plus their flipped-direction
  counterparts (needed by the gate's flipped placebo) = 60 contract-days.
- Before merging, every one of the 31 legs' entry bars was verified in
  the sources: **31/31 entry-bar opens match the recorded entry premiums
  exactly** (the two legs the CSVs lack entirely — 2026-02-27 PE 60800
  and 2026-07-30 PE 56900 — are covered exactly by the caches).
- CSV-vs-cache disagreements on candidate bars: **0** (where both hold a
  bar, values are identical; per build_store order the cache copy is the
  recorded one — 369 bars labelled cache, 162 csv).
- **531 bars added** (09:15–09:55, 9 bars × 59 contract-days), per month
  of leg date: Jan 18 · Feb 54 · Mar 108 · Apr 36 · May 54 · Jun 36 ·
  Jul 81 · Aug 18 · Sep 108 · Oct 18.
- Add-only proof: all **658,177 pre-existing bars** in `prem_bank.json`
  were diffed against the pre-merge backup — **0 altered**. Backup kept
  at `daily2leg/prem_bank.json.pre_ladder_backfill_2026-11-03.bak`.
- One contract-day could not be filled from any declared source:
  **56900 CE, expiry 2026-08-25, on 2026-07-30** has no pre-10:00 bars
  anywhere (its PE leg is fully covered). Consequence is confined to the
  flipped placebo: that single leg's placebo is NOT_COMPUTED (see §5).
  No scored leg is affected.
- Scripts: `ladder_bank_backfill_check.py`, `ladder_bank_backfill_merge.py`.

## 2. Re-audit — PASS 99/99

`ladder_bank_reconstruction_audit.py` re-run unchanged in method (the
stopped run's hard-coded 68/31 assertions replaced by the continuation
gate; original outputs preserved as
`ladder_bank_reconstruction_audit_pre_backfill.{csv,json}`):

- **Reconstruction exact on 99/99 legs** (|Δ| ≤ 0.005, entry-bar open),
  both contract routes in agreement on all 99, 0 value mismatches.
- Benchmark re-sums intact: CSV total **+₹83,650.50**, January
  **+₹22,748.00**. Scoring unblocked under the brief's primary gate.

## 3. Primary scoring — the locked design, unchanged

Entries: the 99 v21 legs. Exits: hard stop −20 premium (close-based);
spot-stage floors on 5-min closes from the entry spot (spot bar open at
entry): T1 +30 → lock +5, T2 +58 → +15, T3 +82 → +25, T4 +100 → exit at
that bar's close premium; floors ratchet only; square-off at the 15:10
bar's close. Money: (exit − entry) × 30 − ₹220 per leg.

| | Ladder (primary) | Original v21 exits, same entries |
|---|---|---|
| Total (99 legs, 92 days) | **+₹16,777.50** | **+₹83,650.50** |
| Mean / leg | +₹169.47 | +₹845.00 |
| Win rate | 46.5% | — |
| Positive days | 46.7% | — |

**The ladder keeps 20.1% of the benchmark on identical entries
(Δ −₹66,873.00).** Month table (ladder): Jan +7,389.50 · Feb +908.00 ·
Mar +4,744.00 · Apr −904.50 · May +3,529.00 · Jun +708.50 · Jul −2,588.00 ·
Aug −810.50 · Sep +2,931.50 · Oct +870.00. Halves: H1 (Jan–May)
+₹15,666.00 · H2 (Jun–Oct) +₹1,111.50 — both positive. Ex-top-3 legs
+₹8,830.50; ex-top-3 days +₹5,483.00 — the total is not carried by its
top 3. Worst day 2026-04-30 −₹2,095.00; worst 3 leg-days −₹4,129.50;
worst drawdown −₹8,955.50.

### Stage-reach anatomy (why the number is what it is)

Reached: T1 63/99 · T2 53 · T3 44 · T4 40. Exit reasons: T4_EXIT 40 ·
HARD_STOP 36 · LOCK_FLOOR_T1 10 · LOCK_FLOOR_T2 9 · LOCK_FLOOR_T3 4 ·
SQUARE_OFF 0.

| Highest stage | Legs | Total | Mean net | Mean realised premium pts |
|---|---|---|---|---|
| none | 36 | −₹42,934.50 | −₹1,192.62 | ≈ −32.4 |
| T1 | 10 | −₹6,044.50 | −₹604.45 | ≈ −12.8 |
| T2 | 9 | −₹3,363.00 | −₹373.67 | ≈ −5.1 |
| T3 | 4 | +₹932.00 | +₹233.00 | ≈ +15.1 |
| T4 | 40 | +₹68,187.50 | +₹1,704.69 | ≈ +64.2 |

Two facts decide the result:

1. **All of the profit is the T4 legs** (+₹68,187.50 from 40 legs). Every
   other bucket is negative in aggregate.
2. **Close-based overshoot is severe.** The "−20 hard stop" realises
   ≈ −32.4 premium points on average (a 5-min bar's close lands well
   past the floor on fast moves), and the locks leak the same way: legs
   whose highest stage was T1 carry a +5 floor yet realise ≈ −12.8
   points on average; T2 legs (+15 floor) realise ≈ −5.1. The ladder's
   stated geometry is not the realised geometry on 5-min closes.

## 4. Sensitivities (labelled non-primary — the primary above stands)

| Variant | Total |
|---|---|
| Stop −15 (locks 5/15/25) | +₹16,180.50 |
| Stop −25 (locks 5/15/25) | +₹22,510.50 |
| Locks −5 (0/10/20, stop −20) | +₹14,184.00 |
| Locks +5 (10/20/30, stop −20) | +₹15,118.50 |

No sensitivity approaches the +₹83,650.50 benchmark either.

## 5. B2-subset robustness and placebos (primary params)

- **B2 subset** (family == BASE, 61 legs — the B2 pool as carried into
  v21): ladder **−₹481.00** vs original exits **+₹55,466.00** on the same
  legs. On the core pool the ladder is negative; the primary's positive
  total comes from the add-on families (NS1/NS3/S3 legs).
- **Flipped-direction placebo:** **−₹60,426.50** over 98 legs (1
  NOT_COMPUTED: 2026-07-30 PE leg — its flipped 56900 CE contract has no
  pre-10:00 bars in any declared source, §1). On the same 98 legs the
  primary totals +₹18,226.00 — it beats the placebo by ₹78,652.50.
- **Shifted-entry +60 min placebo:** **−₹44,409.50** over 98 legs (1
  NOT_COMPUTED: 2026-05-04 S3-PDC leg, entry 14:25 → shifted 15:25 is
  after the 15:10 square-off). On the same 98 legs the primary totals
  +₹15,238.00 — it beats the placebo by ₹59,647.50.

## 6. Gate checklist (all in the same run)

- Timing audit: entry premiums == recorded (99/99 via §2); every exit
  premium == the store close at the recorded exit bar; every exit within
  [entry, 15:10]; decisions on closes of completed bars only — **PASS**.
- Independent second implementation of the exit logic (stage-timeline
  first, then exit walk) reproduces exit time, exit premium, reason,
  highest stage and net on **99/99 legs** — **PASS**.
- Independent re-sum of every headline from `ladder_bank_trades.csv`
  (total, months, halves, ex-top-3 legs/days, worst day, drawdown) —
  **PASS, exact**; the file's original-exit column re-sums to
  +₹83,650.50.
- Hand spot-checks of one T4, one hard-stop and one lock-floor leg
  against the raw store bars — all reproduce (incl. the 2026-03-05 T1
  leg: +5 floor, realised exit −15 pts on a gap-through close).
- Store integrity: 658,177 pre-existing bars, 0 altered (§1) — **PASS**.

## 7. Verdict

Procedurally the build is complete and the gate passes: the ladder is a
real, causal effect on these entries — it beats both placebos by wide
margins and stays positive ex-top-3 with both halves positive.
Economically it is **not** an improvement: on identical entries it earns
**+₹16,777.50 against the incumbent exits' +₹83,650.50**, its core B2
pool is negative under it (−₹481.00 vs +₹55,466.00), and its realised
stop/lock geometry on 5-min closes is far looser than its stated levels
(−20 stop → ≈ −32 realised; +5 lock → ≈ −13 realised on T1 exits). The
ladder as locked does not displace the v21 exits. Nothing is armed; any
adoption decision is the owner's.

## Files produced (continuation)

- `ladder_bank_backfill_check.py` / `ladder_bank_backfill_merge.py` —
  source check and add-only merge (backup:
  `daily2leg/prem_bank.json.pre_ladder_backfill_2026-11-03.bak`)
- `ladder_bank_reconstruction_audit.{py,csv,json}` — re-audit (99/99);
  stopped-run originals preserved as `*_pre_backfill.{csv,json}`
- `ladder_bank_score.py` — scorer + gate
- `ladder_bank_trades.csv` — per-leg primary trades (99 rows)
- `ladder_bank_results.json` — full results (variants, anatomy, B2,
  placebos incl. per-leg placebo nets, audits)
