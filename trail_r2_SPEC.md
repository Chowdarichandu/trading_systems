# TRAIL ROUND 2 — SPEC (frozen 2026-11-16, before any scoring)

Owner follow-up (2026-11-16 20:16 IST, voice-garbled message read
as): run the +30 trail with wider / "normal" trails, and for
book-half run it with a trail on the rest. Three untested arms, all
exit-geometry-only on the same stored entries. Context: TRAIL30
(activate at +30, D = 10/15/20) scored earlier today — Bank stack
WR 73.9% but kept only 16–19% of the control's money, FAIL on all
three streams. These arms test whether WIDER trails (A), a
FROM-ENTRY trail (B), or HALF-AT-+30 + TRAIL-ON-THE-REST (C)
changes that. Paper research only. No frozen book, ledger or live
job is touched.

## Streams (entries identical; controls must reproduce EXACTLY first)

Same assembly, leg sets and anchors as small_target_SPEC.md /
lock30_SPEC.md / trail30_SPEC.md (this build execs the lock30
assembly + geometry chunks and the trail30 walks verbatim; every
control assertion in those builds must pass again BEFORE any
variant is scored):

1. **BANK_STACK** — TUNED STACK v2, Jan–Oct: **+₹127,351.50 / 111**.
2. **BANK_LEGACY** — legacy v21, Jan–Oct: **+₹83,650.50 / 99**.
3. **NIFTY_V1** — TUNED v1 (EVE-07), Jan–Oct: **+₹103,050.25 / 74**.

Lots: Bank 30, Nifty 65. Cost ₹220/leg. If any control misses, the
run STOPS and reports the discrepancy.

## Conventions common to all three arms

- **Fill discipline (variant fills):** a stop/trail exit fills at
  its binding level, or at the exit bar's open if the bar opens
  beyond the level (gap-through); a target-type fill at its level,
  or at the bar's open if the bar opens beyond it. This is the
  small-target / LOCK30 / TRAIL30 variant discipline, disclosed
  there: the frozen books fill at the level even on gap-through
  bars; the variants fill at the open, applied uniformly, in
  advance.
- **Completed-bar checks:** every trail level is set from the peak
  through the PRIOR bar; a bar's own high joins the peak only after
  that bar's stop check has run.
- **Placebo (all arms):** the same legs with entries shifted +30
  minutes (6 bars) on the leg's own series, scored under the SAME
  arm at the SAME D, entry at the shifted bar's open. Legs with no
  valid shifted entry (shifted bar beyond the series or past the
  leg mode's last stop-check bar — 15:05 for g0 legs, 15:20
  otherwise) are dropped from the placebo and counted.
- **Gate (full, same run, per stream per configuration):** timing /
  leak audit on the new fills (exit time ≥ entry time; every exit
  fill is the exit bar's own binding level / open / close; entry
  fill equals the recorded entry premium on every leg; no exit
  after the stream's square-off); win rate (the owner's
  "accuracy" — reported FIRST for every row); ₹/trade-day
  (trade-day = a date with ≥1 leg; identical leg set ⇒ identical
  trade-days across control and variants); halves Jan–May vs
  Jun–Oct; full month table Jan–Oct with red months named;
  ex-top-3; worst drawdown; independent re-sum of the written
  trades file to the paisa.
- **November counterfactual:** Nov 2–16 legs as stored (Bank stack
  log, Bank legacy PRIMARY log, Nifty TUNED v1 legs = DEC-S1 shadow
  log minus component-B PE rows), shown separately, NEVER used to
  select. CF geometry per trail30_SPEC.md (Bank stack: runner lock
  90 / tgt2 180, arm30 iff family = NS1_second; Bank legacy: plain
  stop −50 / target +90; Nifty: TUNED v1 geometry lock 60 / tgt2
  175 / arm 50 / SQ 15:20), terminal 15:20 close on the
  november_shadow_data premium candles (exact-tag files outranking
  globs).

## ARM A — TRAIL30-WIDE (wider trails after the +30 activation)

TRAIL30 exactly as frozen in trail30_SPEC.md — the leg's own frozen
geometry in full until activation (its stop, target, arms, runner
stage, square-off); activation = the first completed bar whose high
reaches entry + 30, registered at that bar's close after that bar's
stop/target checks; from the bar AFTER activation the fixed target
is removed, any runner stage is abandoned, and the only exits are
the trailing stop at (peak through the prior bar) − D and the leg's
own square-off — with **D ∈ {25, 40}** (the only change vs TRAIL30's
10/15/20). Config names: TRAIL30W_D25, TRAIL30W_D40.

## ARM B — TRAIL-ENTRY (the "normal" trail, from the entry bar)

The leg's exit geometry is REPLACED in full — no fixed target, no
runner stage, no arms (the trail does their job):

- **Effective stop on every bar from the entry bar onward:**
  level = max(entry − 50, peak_prior − D), **D ∈ {15, 25, 40}**.
  The −50 hard stop is the floor until the trail rises above it.
- **peak_prior:** on the entry bar, the entry premium itself (the
  price at the entry instant — the only peak knowable when the
  position opens; so the entry bar's effective stop is
  max(entry − 50, entry − D)). On each later bar, the running
  maximum of premium highs over all completed bars from the entry
  bar through the prior bar.
- **Check order per bar:** stop check against the bar's low first
  (fill per the common discipline); if no breach, the bar completes
  and its high joins the peak.
- **Square-off unchanged per leg mode:** sq1520 legs exit at the
  15:20 bar's close (if the series ends earlier, the close of the
  last bar ≤ 15:20); g0 (Bank re-entry) legs keep their source
  terminal rule — stop checks on bars ≤ 15:05 only, terminal = the
  15:10 bar open if present, else the close of the last bar
  ≤ 15:05.
- No mirror audit exists for this arm, by design: with the trail
  removed it would NOT reproduce the control (the control has a
  target and runner geometry; this arm removes them). Its
  integrity checks are the timing/fill audit, the placebo and the
  re-sum. Config names: TRAILENT_D15, TRAILENT_D25, TRAILENT_D40.

## ARM C — HALF30-TRAIL (book half at +30, trail the rest)

**LABEL (in every output): requires 2 lots to execute literally;
on this 1-lot record it is a points blend, one ₹220 cost per leg.**

- **Phase 1 (whole position, before activation):** the leg's own
  frozen geometry in full, exactly as TRAIL30 phase 1 — its stop
  (−50 in these books), target, arms, runner stage, square-off.
  (The task's "−50 stop on the remainder before activation" is this
  frozen geometry: the −50 stop is these books' phase-1 stop.)
- **Activation:** identical registration to the trail30 walks — the
  first bar whose high reaches entry + 30 while the leg is open,
  registered after that bar's stop/target checks (a leg the frozen
  geometry exits on a bar never activates on that bar). At
  activation, **half the position exits at the activation fill** =
  the entry + 30 level, or the activation bar's open if the bar
  opened above the level (target-fill discipline).
- **Phase 2 (the remaining half):** from the bar AFTER activation,
  exactly TRAIL30 phase 2 with **D ∈ {15, 25}** — fixed target
  removed, runner stage abandoned (a runner entered on the
  activation bar never governs a bar), the only exits the trailing
  stop at (peak through the prior bar) − D — the peak includes the
  activation bar's high — and the leg's own square-off. If
  activation registers on the square-off bar itself, the remainder
  exits at that bar's close (g0 legs: at their terminal fill).
- **Never activated:** the whole position takes the variant walk's
  frozen-geometry exit (identical to the control exit except the
  common gap-through fill discipline).
- **Net** = [0.5 × (activation fill − entry) + 0.5 × (remainder
  exit − entry)] × lot − ₹220 when activated; the walk's net
  otherwise. In the trades file, an activated leg's exit_premium is
  the blended effective exit premium (0.5 × activation fill +
  0.5 × remainder exit), its exit_time / exit_reason are the
  remainder's, and the activation bar/fill are recorded in their
  own columns. Config names: HALF30T_D15, HALF30T_D25.

## VERDICT RULE (frozen)

A configuration (one arm at one D on one stream) is a **PASS** only
if ALL of:
1. its Jan–Oct total beats the control total, AND
2. it keeps **zero red months**, AND
3. it beats its placebo (shifted-entry twin, same arm, same D).

If a configuration wins on accuracy (win rate) but loses on total,
the report states exactly that trade-off in plain numbers — no PASS
label. (Stated in advance: the Bank legacy control itself has 3 red
months — Apr, Jul, Aug — and the Nifty v1 control has 1 — Mar — so
rule 2 is an absolute bar, as in every run of this family.) Halves,
ex-top-3, activation share and the November counterfactual are
reported in full for every configuration regardless of the label.

## If a configuration PASSes on a stream

Build its score-only forward-shadow scorer + seeded ledger for that
stream (Nov 2–16 counterfactual rows labelled
BACKFILL_COUNTERFACTUAL) and report the cron line for the parent to
add (21:50 IST slot). The build does NOT create the cron.

## Deliverables

trail_r2_SPEC.md (this file) · trail_r2_build.py ·
trail_r2_2026-11-16.md · trail_r2_results.json ·
trail_r2_trades.csv (284 Jan–Oct legs × control + 7 configurations,
plus the 12 November CF legs). Data: local stores only; no fetch is
expected to be needed — any Upstox fetch would use the browser
User-Agent and hard-stop the run on a 429.
