# SMALL-TARGET EXIT TEST — SPEC (frozen 2026-11-16, before any scoring)

Owner's direct order (2026-11-16 18:06 IST). His standing philosophy
(2026-10-28): identify levels, enter, book a SMALL profit, stop. Question:
on the SAME entries the running books already take, what happens if the
exit books a small fixed target (+20 / +30 premium points) instead of
riding to +90? Paper research only. No frozen book, ledger or live job
is touched.

## Streams (entries identical; controls must reproduce EXACTLY first)

1. **BANK-STACK** — TUNED STACK v2 entries, Jan–Oct 2026.
   Control: **+₹127,351.50 / 111 legs** (frozen exit geometry as stored:
   −50 stop / +90 target / runner stages / arm30 on NS1_second legs).
   Source: the frozen pipeline assembly (bank_fix_d3.py machinery,
   copied verbatim) — the build asserts the incumbent leg-for-leg
   against bank_positive_tuning_2026-11-10_eve19_trades.csv before any
   variant is scored. Lot 30, cost ₹220/leg.
2. **BANK-LEGACY** — legacy v21 entries (BNF-PAPER-V1 frame), Jan–Oct.
   Control: **+₹83,650.50 / 99 legs**. Source: the same assembly's
   rows21; the build asserts replay of every leg against its recorded
   exit and cross-checks the leg set + total against
   november_books_fix_anatomy_legs.csv (BANK_LEGACY). Lot 30, ₹220.
3. **NIFTY-V1** — TUNED v1 (EVE-07) entries, Jan–Oct.
   Control: **+₹103,050.25 / 74 legs**. Source: nifty_next_phase_trades.csv
   set=BASE minus component-B PE rows (the frozen v1 definition); the
   build additionally replays every leg under the standing geometry
   (lock 60 / tgt2 175 / arm 50 / SQ 15:20, replay_r5) from
   candles_exact and compares exit time / premium / net leg-for-leg.
   Lot 65, cost ₹220/leg.

If any control misses its total or its leg-for-leg check, the run STOPS
and reports the discrepancy. Nothing is scored on a missed control.

## The one change — exit geometry only

Entries, strikes, expiries and fills are the books' own. For legs whose
frozen exit is a runner/staged geometry, the small target replaces the
WHOLE exit: the entire position exits at the target. All staged elements
(runner lock, second target, breakeven arms — Bank arm30, Nifty arm50)
are removed. The position is governed solely by target / stop /
square-off.

- **S20**: target +20 premium points, stop −50.
- **S30**: target +30 premium points, stop −50.
- **S30T**: target +30 premium points, stop tightened to −30.

### Fill discipline (the variant's own, stated in advance)

- Entry fill: the entry bar's open — identical to the recorded entry
  premium (asserted per leg; a leg whose candle entry open differs from
  the recorded entry premium is a control failure, not a variant input).
- Walk: 5-min bars of the leg's own contract, starting at the entry bar.
  On every bar, the STOP is checked before the TARGET (the frozen books'
  own convention, entry bar included).
- Target fill: the first bar whose high reaches entry + target fills at
  the target price — unless that bar opens beyond the target, then at
  the bar's open. Stop fill: same discipline (level, or the open on a
  gap-through). Disclosed difference: the frozen books fill at the level
  even on gap-through bars; the variant fills at the open. The rule is
  applied uniformly to target and stop, in advance, for all streams.
- Square-off unchanged per stream: Bank stack/legacy 15:20 bar close
  (last bar at or before 15:20 if no 15:20 bar exists); Nifty 15:20 bar
  close (same fallback). Bank stack re-entry legs keep their source
  terminal rule (their premium series is the daily2leg store: stop/target
  checked on bars up to 15:05, terminal = 15:10 bar open if present,
  else the close of the last bar at or before 15:05) — that IS their
  frozen square-off, so "square-off unchanged" holds per source.

## What this is NOT (stated in advance)

- NOT the 2026-11-03 target ladder: that was staged partial lock +
  trailing on v21 entries only. Here the whole position exits at one
  fixed small target — no staging, no trail — on all three streams.
- NOT FE-1/2/3: those truncated positions by the CLOCK regardless of
  price. Here every exit is a price level (target / stop / square-off);
  no time-based exit exists in any variant.

## MFE context (reported per stream)

From each leg's own premium path, entry bar through the CONTROL exit
bar inclusive: did the path reach +20 (and +30) before it reached −50?
First-hit race, stop-first within a bar (the books' convention).
Reported: share of legs reaching +20 before −50, share reaching +30
before −50, and the MFE distribution (median / quartiles) — so the
owner sees why the totals come out as they do.

## Gate (full, same run, per stream per variant)

- Timing/leak audit on the new exit fills: exit time ≥ entry time;
  every exit fill is the exit bar's own level/open/close (no future
  bar is ever read); entry fill equals the recorded entry premium on
  every leg; no exit after the stream's square-off.
- Placebo: the same legs with entries shifted +30 minutes (6 bars) on
  the leg's own series, scored under the SAME variant geometry (entry
  at the shifted bar's open; legs with no valid shifted entry are
  dropped from the placebo and counted). The variant must beat its
  shifted twin's total.
- Halves: Jan–May vs Jun–Oct nets.
- Full month table (Jan–Oct), red months named.
- Ex-top-3 (total minus the three largest leg nets).
- Win rate and ₹/trade-day (trade-day = a date with ≥1 leg; identical
  leg set ⇒ identical trade-days across control and variants).
- Independent re-sum of the written trades file, to the paisa.
- November counterfactual: Nov 2–16 legs as stored (Bank stack log,
  Bank legacy PRIMARY log, Nifty TUNED v1 legs = DEC-S1 shadow log
  minus component-B PE rows), variant exits walked on the
  november_shadow_data premium candles, terminal = 15:20 close (last
  bar at or before 15:20). Shown separately, NEVER used to select.

## VERDICT RULE (frozen)

A variant is a **PASS** for its stream only if ALL of:
1. its Jan–Oct total beats the control total, AND
2. it keeps **zero red months**, AND
3. it beats its placebo (shifted-entry twin).

If a variant wins on win rate but loses on total, the report states
exactly that trade-off in plain numbers — no PASS label. Halves,
ex-top-3 and the November counterfactual are reported in full for
every variant regardless of the label.

## If a variant PASSes

Build its score-only forward-shadow scorer + seeded ledger (Nov 2–16
counterfactual rows labelled BACKFILL_COUNTERFACTUAL) and report the
cron line for the parent to add (21:05 IST slot). The build does NOT
create the cron.

## Deliverables

small_target_SPEC.md (this file) · small_target_build.py ·
small_target_2026-11-16.md · small_target_results.json ·
small_target_trades.csv. Data: local stores only; no fetch is expected
to be needed — any Upstox fetch would use the browser User-Agent and
hard-stop the run on a 429.
