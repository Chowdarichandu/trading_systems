# TRAIL30 TEST — SPEC (frozen 2026-11-16, before any scoring)

Owner question (2026-11-16 20:08 IST): "With 30 points and trail how
much accuracy". This tests the one +30-exit form not yet scored on
the index entries: a TRUE trailing stop that activates at +30 and
follows the running peak. It is mechanically distinct from all three
+30 forms already measured and dead:

- **(a) The 2026-11-03 ladder** (v21 Bank legs): SPOT-stage ratchets
  — premium locks +5/+15/+25 keyed to spot stages +30/+58/+82/+100 —
  with the hard stop tightened to **−20 from the start**. Scored
  +₹16,777.50 vs +₹83,650.50 plain, WR 46.5%. There is no
  running-peak trail in it: the stop only ever jumps between three
  fixed levels, and the tight −20 stop applies from entry.
- **(b) LOCK30** (2026-11-16): after the +30 touch, ONE fixed floor
  at entry+5; the +90 target and the runner geometry stay alive.
  Stack WR collapsed to 31.5% (the +5 lock is ₹150 < ₹220 cost).
  The floor never follows the peak.
- **(c) S30** (2026-11-16 small-target test): the WHOLE position is
  sold at +30 — no stop movement, no trail (S20 / S30T are the same
  family). Stack kept 14% of the control's money.

TRAIL30: nothing is sold at +30 and no fixed floor is set. At
activation the fixed target is REMOVED, and the only exits left are
a stop that trails the running peak by D points, and the leg's own
square-off. Paper research only. No frozen book, ledger or live job
is touched.

## Streams (entries identical; controls must reproduce EXACTLY first)

Same assembly, leg sets and anchors as small_target_SPEC.md /
lock30_SPEC.md (this build reuses that machinery verbatim; every
control assertion in it must pass again before any variant is
scored):

1. **BANK-STACK** — TUNED STACK v2, Jan–Oct: **+₹127,351.50 / 111**.
2. **BANK-LEGACY** — legacy v21, Jan–Oct: **+₹83,650.50 / 99**.
3. **NIFTY-V1** — TUNED v1 (EVE-07), Jan–Oct: **+₹103,050.25 / 74**.

Lots: Bank 30, Nifty 65. Cost ₹220/leg. If any control misses, the
run STOPS and reports the discrepancy.

## TRAIL30 (the variant — exit geometry only)

Each leg keeps its OWN frozen exit geometry (its params, its arms,
its runner stages, its square-off) until activation, with ONE
modification from activation onward:

- **Phase 1 (before activation):** the frozen geometry in full —
  the leg's own stop (−50 in these books), its target, its arms
  (Bank NS1_second arm30 → entry+0; Nifty arm50 → entry+0), its
  runner stage, its square-off.
- **Activation (the touch):** the first completed 5-min bar (entry
  bar onward) whose high reaches entry + 30, registered at that
  bar's close — the books' own arm convention, the same
  registration point LOCK30 used. On the activation bar itself the
  frozen geometry still governs in full (its stop and target checks
  run first on that bar, in the books' own order).
- **Peak:** the running maximum of premium highs from the entry bar
  onward. At activation the peak includes the activation bar's high.
- **Phase 2 (from the bar AFTER activation):** the fixed target is
  REMOVED and any runner stage is abandoned (a runner entered on
  the activation bar never governs a bar). The only exits are:
  1. **Trailing stop** at level = (peak through the PRIOR bar) − D.
     Breach = a bar's low at or below the level. Fill at the level,
     or at the bar's open if the bar opens below the level (the
     gap-through fill discipline of the small-target / LOCK30 runs,
     disclosed: the frozen books fill at the level even on
     gap-through bars; the variant fills at the open, applied
     uniformly, in advance). The peak updates only after a
     non-breaching bar's check.
  2. **The leg's own square-off**, unchanged (Bank: 15:20 close,
     last bar ≤ 15:20 otherwise; Bank re-entry g0 legs keep their
     source terminal rule — stop/target on bars ≤ 15:05, terminal
     = 15:10 bar open if present, else the close of the last bar
     ≤ 15:05; Nifty: 15:20 close).
  The frozen stop is subsumed in phase 2: peak ≥ entry+30 at
  activation, so the trail level starts at ≥ entry+30−D ≥ entry+10
  for every D tested.
- **Distances (pre-registered, the only dials): D ∈ {10, 15, 20}
  points.** No other settings are scored.

## Gate (full, same run, per stream per D)

- Timing/leak audit on the new fills: exit time ≥ entry time; every
  exit fill is the exit bar's own binding level / open / close (no
  future bar is ever read); entry fill equals the recorded entry
  premium on every leg; no exit after the stream's square-off.
  Internal mirror audit: the variant walk with the trail DISABLED
  and level fills must reproduce every leg's recorded control exit
  (time / premium / reason) — a divergence stops the run for that
  stream.
- Placebo: the same legs with entries shifted +30 minutes (6 bars)
  on the leg's own series, scored under the SAME variant at the
  SAME D. Legs with no valid shifted entry are dropped from the
  placebo and counted. The variant must beat its shifted twin's
  total.
- Win rate (the owner's "accuracy" — reported FIRST for every row),
  ₹/trade-day (trade-day = a date with ≥1 leg; identical leg set ⇒
  identical trade-days across control and variants).
- Halves: Jan–May vs Jun–Oct nets.
- Full month table (Jan–Oct), red months named.
- Ex-top-3 (total minus the three largest leg nets).
- Activation share: legs whose trail ever activated (touch
  registered while the leg was open), legs with ≥1 trail-governed
  bar, and trail-stop exits — per stream per D.
- Independent re-sum of the written trades file, to the paisa.
- November counterfactual: Nov 2–16 legs as stored (Bank stack log,
  Bank legacy PRIMARY log, Nifty TUNED v1 legs = DEC-S1 shadow log
  minus component-B PE rows), shown separately, NEVER used to
  select. CF geometry per lock30_SPEC.md (Bank stack: runner lock
  90 / tgt2 180, arm30 iff family = NS1_second; Bank legacy: the
  log's own plain stop −50 / target +90; Nifty: TUNED v1 geometry
  lock 60 / tgt2 175 / arm 50 / SQ 15:20), terminal 15:20 close on
  the november_shadow_data premium candles (exact-tag files
  outranking globs).

## VERDICT RULE (frozen)

A variant (one D on one stream) is a **PASS** only if ALL of:
1. its Jan–Oct total beats the control total, AND
2. it keeps **zero red months**, AND
3. it beats its placebo (shifted-entry twin at the same D).

If a D wins on accuracy (win rate) but loses on total, the report
states exactly that trade-off in plain numbers — no PASS label.
(Note, stated in advance: the Bank legacy control itself has 3 red
months — Apr, Jul, Aug — and the Nifty v1 control has 1 — Mar — so
rule 2 is an absolute bar, as in the small-target and LOCK30 runs.)
Halves, ex-top-3, activation share and the November counterfactual
are reported in full for every D regardless of the label.

## If a D PASSes on a stream

Build its score-only forward-shadow scorer + seeded ledger for that
stream (Nov 2–16 counterfactual rows labelled
BACKFILL_COUNTERFACTUAL) and report the cron line for the parent to
add (21:35 IST slot). The build does NOT create the cron.

## Deliverables

trail30_SPEC.md (this file) · trail30_build.py ·
trail30_2026-11-16.md · trail30_results.json · trail30_trades.csv
(284 Jan–Oct legs × control + 3 D-variants, plus the 12 November CF
legs). Data: local stores only; no fetch is expected to be needed —
any Upstox fetch would use the browser User-Agent and hard-stop
the run on a 429.
