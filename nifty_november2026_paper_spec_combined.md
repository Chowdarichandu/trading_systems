# November 2026 paper spec — Nifty Cluster-1-like validation (PREPARATION ONLY, NOT RUN)
## Paper only, no orders, no live trading. November 2026 has not happened; no November day is claimed here.

Status at freezing (2026-10-29): NO candidate emerged from the
combined sweep (`nifty_cluster1_combined_sweep.md`). M1 and M11 both
failed out-of-sample (M1: 4/55 losses green; M11: 0/55, total −₹885,
winner deletion −₹72,350). Combined re-entry + partial variants all
failed (best C-SURV: 2/8 green, −₹18,237). **Therefore no thresholds
are frozen for November adoption in this spec.** Freezing a failed
variant for November would be presenting exhaustion as a candidate.

## What November is for

November 2026 is a fresh, unseen validation set for the NEXT family's
candidate — the candidate that emerges after this sweep, from a family
not yet exhausted (e.g. sizing by the bounce bar's range, or a new
morning-trade exit not yet tried). That candidate's thresholds must
be written into this spec BEFORE its first November trade is scored,
exactly as the gap+belowPDL box was frozen before its forward test —
and discarded on the same terms if it fails there, not re-fitted on
November data.

## Frozen November protocol (applies to whatever candidate is added)

- Universe: Nifty PE breakdown days in November 2026, scanned exactly
  as in all prior sweeps (V4 setup2: close < OR low, close < PDL,
  room ≥ 200 × scale, OR width ≤ 360 × scale, signal ≤ 11:30; Skill
  OR-breakdown if no V4 signal). One trade per day, paper only.
- Exit (provisional cash, NOT Chandu's live options rules): entry =
  next bar open after signal, stop = signal high (PE) unless the
  candidate's frozen rule changes it, target = entry − 2 × risk
  unless the candidate's frozen rule changes it, stop checked
  before target on each bar including the entry bar, square-off
  15:10, 100 shares equivalent, ₹40/trade.
- Data source: Upstox 5-min cache extended into November; for days
  in progress use the intraday endpoint (the historical endpoint
  returns completed days only — fixed 2026-10-29). Missing days stay
  missing in the manifest, not patched.
- Daily log (one row per November PE day): date, baseline net,
  candidate net, green / no-trade / loss under the candidate,
  whether the day is Cluster-1-like (fast stop, baseline bars ≤ 4)
  or a winner day, and the candidate's signal/entry/stop/target.

## Pre-registered pass rule (all legs must hold)

A candidate is discussed for adoption ONLY if, on November 2026:

1. Cluster-1-like green ≥ 60% — at least 60% of November's
   Cluster-1-like (fast-stop baseline loss) days turn green under
   the candidate (no-trade counted separately, NOT as green).
2. November PE total positive under the candidate.
3. Winners not collapsed — candidate winner total on November
   winner days is at least 80% of the baseline winner total on
   those same days (guardrail against M11-style deletion).
4. No single November trade contributes more than 50% of the
   candidate's November net (guardrail against one-target luck).

## Pre-registered discard rule

A candidate failing ANY leg above is discarded on the same terms as
the gap+belowPDL box: not re-fitted on November data, not carried
into December as an adoption candidate, and its November failure
logged with the reason. A new candidate must come from a new family
or a new, pre-registered rule — not from moving the failed
candidate's threshold until November turns green.

## Shadow log only (NOT an adoption candidate)

C-SURV (combined re-entry + survival B N=10 partial on the re-entry
leg; in-sample Cluster 1: 2/8 green, −₹18,237) may be shadow-logged
in November alongside the baseline — its daily nets recorded, nothing
more. A November shadow total above baseline does NOT adopt C-SURV,
because C-SURV already failed its in-sample pass bar and was not
frozen as a candidate. The same applies to M1 (shadow only if
logged, with its winner-deletion cost reported alongside any total
improvement) and M11 (not shadow-logged as a candidate at all —
it is dead in-sample and out-of-sample).

## To be completed before November scoring starts

- [ ] Next family's candidate name and exact frozen rule (signal,
  entry, stop, target, partial/trail if any, re-entry if any).
- [ ] That rule pasted verbatim into this spec, with its in-sample
  and out-of-sample numbers from the sweep that produced it.
- [ ] November daily log file path, once November data exists.

Until those boxes are filled, this spec freezes nothing for adoption
and no November run is claimed. Paper only throughout.
