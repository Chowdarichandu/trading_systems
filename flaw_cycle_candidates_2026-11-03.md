# FLAW-CYCLE — candidate pre-registration (written BEFORE any scoring)

Date: 2026-11-03 (~11:50 IST), before the flaw-cycle scorer is run.
Ordered by Chandu 2026-11-03 ~11:43 IST: identify the flaw behind two
consecutive negative live days (Nov 2 and Nov 3, Bank primary −₹1,720
each, both full −50 stops on OR-family legs), apply the fix, and check
counterfactually whether those days would still be negative.

Incumbent: Bank book v21 (causal, +₹83,650.50, 99 legs, Jan–Oct 2026),
reproduced through the audited pipeline (bank_r7_core / assemble6) and
verified leg-for-leg against bank_engine_r8_v21_regen_trades.csv before
any variant is scored. Basis: premiums per 1 lot (30), cost ₹220/trade,
UNIQUE-ONCE (inherited — admissions do not change in any candidate).

ALL candidates are EXIT OVERLAYS ONLY. Admissions, legs, segments and
each leg's frozen exit parameters (stop/trig/lock/tgt2 from its v21
`_params`) are unchanged. Each leg's phase 1 is the race between the
−50 stop and the +90 trigger, square-off 15:20, stop checked before
target on every bar including the entry bar (replay_x semantics).
Overlays act only inside phase 1. If a leg reaches its +90 trigger,
its frozen phase 2 runs untouched.

## FC-1 — NODEV-CUT (attacks the never-developed full stop)
While in phase 1, track the running maximum bar HIGH from the entry
bar. At the CLOSE of the 2nd bar after the entry bar (bar index
entry+2), if that running maximum is still < entry + 15, exit at that
bar's close (exit_reason "nodev_cut"). Within every bar the order is:
(1) frozen stop touch, (2) frozen trigger touch, (3) the nodev check
(only on the entry+2 bar, at its close), (4) square-off. A leg whose
stop or trigger is touched on or before the check bar is unaffected.

## FC-2 — GIVEBACK-LOCK (attacks the developed-then-faded full stop)
While in phase 1, once a bar COMPLETES with its high ≥ entry + 30,
the phase-1 stop for all SUBSEQUENT bars rises from entry − 50 to
entry + 0 (breakeven premium). The arming bar itself is still governed
by the old stop (the lock is armed only after the bar completes —
no intrabar use of the arming bar's range). If the raised stop is
touched, exit at entry + 0 (exit_reason "lock_stop"). If the +90
trigger is touched first, frozen phase 2 runs untouched.

## FC-3 — FC-1 + FC-2 combined (both overlays active, same parameters)

## Controls (same run, per backtest_controls_gate)
- Causality audit in writing: entries are the frozen v21 entries
  (pipeline-verified, entry = open of entry bar, checked for all rows);
  overlay decisions use only bars at or before the decision bar, and
  the FC-2 lock only bars already completed. Violations counted, not
  sampled.
- Placebo: delay-6 twin — identical legs, parameters and overlay, with
  entries delayed +30 min (6 bars), the pipeline's standing placebo
  construction. Variant must beat its own placebo twin.
- Halves (Jan–May / Jun–Oct), full month table + month-end cumulative,
  no green month of the incumbent may flip red, no red month-end.
- Ex-top-3 stress: variant total minus its own top-3 legs must be ≥ 0.
- FT90 must not fall below the incumbent's 49.5%.
- Independent re-sum of every written trades file to the paisa.
- NOT_COMPUTED: any leg whose candles cannot be loaded is counted and
  named; NC must be 0 for a PASS (incumbent NC = 0).

## Gate (the standing Round-2 banking gate vs v21, plus ex-top-3 ≥ 0)
PASS requires ALL of: net > incumbent net; no red month-ends; no green
month flips red; FT90 ≥ 49.5%; frequency unchanged (legs identical,
2.44/wk ≥ 2.0); both halves ≥ 0; placebo beaten; timing violations 0;
NC 0; re-sum exact; ex-top-3 ≥ 0. The deciding leg(s) will be named
for every FAIL. A PASS is promoted only as a labelled TUNED SHADOW /
December candidate per standing rules — the frozen November primary
(BNF-PAPER-V1, G0 exits, square-off 15:10) is never mutated.

## Counterfactual protocol (Nov 2 + Nov 3, November-primary geometry)
The two live days are re-scored candle-by-candle under the NOVEMBER
primary's frozen geometry (PLAIN stop −50 / target +90, square-off
15:10, entry = open of entry bar) — first the incumbent (must reproduce
−₹1,720 on both days exactly), then FC-1, FC-2, FC-3 on the identical
premium paths. Candles: real 5-min premium candles for BANKNIFTY
54800 PE (2026-11-02) and 55500 CE (2026-11-03), expiry 2026-11-23.
