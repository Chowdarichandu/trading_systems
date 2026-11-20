# FORTY PROGRAMME — SPEC (frozen 2026-11-16, before any scoring)

Owner's order (2026-11-16 20:44 IST): a WORKING index system with a
**40-point target for Bank Nifty and 20–30 points for Nifty** — "I don't
want hundreds of points to capture." Delivery due when he messages at
06:30 IST 2026-11-17. Paper research only; nothing running is mutated.

Every test earlier today changed exits on the SAME three entry streams
(stack / legacy / TUNED v1) and failed. This programme's centre of
gravity is DIFFERENT ENTRIES built for small moves, paired with the
small target. Two of the eight streams (raw stack, TUNED v1) are kept
as reference rows because the +40 flat exit itself is untested there.

## Target exits (the only change vs each stream's control)

Premium points. Completed-bar fills, same discipline as
small_target / lock30 / trail30 (the `sim_small` walk): stop checked
before target on every bar including the entry bar; fill at the level,
or at the bar's open on a gap-through; square-off at the 15:20 close
(last close ≤ 15:20 otherwise). Cost ₹220/trade. Lots: Bank 30,
Nifty 65.

- Bank: **F40** = exit all at +40, stop −50 · **F40S** = exit all at
  +40, stop −40.
- Nifty: **F25** = +25/−50 · **F30** = +30/−50 · **F25S** = +25/−40.

One stream has a different fill convention, inherited from its frozen
source and applied identically to its control and its variants:
REGIME-REV fills the entry at the confirmation bar's premium CLOSE, so
its walks (control and variant) start on the bar AFTER the entry bar,
and its square-off is the 15:10 close (the source's own). No other
stream is adjusted.

## Entry streams (control = the stream's own frozen exit)

Each control must be reproduced EXACTLY (leg-for-leg against its
frozen source, totals to the paisa) before any variant is scored on
that stream. A stream whose control misses is stopped and reported,
never estimated.

BANK (lot 30):
1. **D1_STACK** — TUNED STACK v2 legs kept by D1 (stack + B-FIX-1 +
   confidence ≥ 0.5), from `bank_fix_d1_trades.csv`, matched leg-for-leg
   to the verified stack legs. Control: **+₹126,496.00 / 71 legs**
   (the legs' own frozen stack exits).
2. **RAW_STACK** — TUNED STACK v2, all legs (small_target STREAM_A,
   itself leg-for-leg vs the EVE-19 file). Control:
   **+₹127,351.50 / 111 legs**.
3. **PREMTAPE** — PREMIUM-TAPE P-RET-120 entries (Step A of
   `premium_tape_bank_r3_trades.csv`), X1 exits. Control:
   **+₹16,692.50 / 58 legs**. Control re-walk via the source's own
   `score_exit` must reproduce every recorded exit.
4. **REGIMEREV** — REGIME-REV entries (`november_regime_family_trades.csv`,
   book BANK_real), frozen −50/+90 after-close-entry exits. Control:
   **+₹15,872.00 / 31 legs**. Control re-walk via the source's
   `replay_after` must reproduce every recorded exit.
5. **VWAP_A_BANK** — VWAP-cross rule-A entries
   (`vwap_ema_smalltunes_bank_results.json` final_trades['A']), E2
   exits. Control: **+₹24,507.50 / 106 legs**. Entries regenerated
   with the source's own `run_row` and matched leg-for-leg to the
   recorded trades before scoring.

NIFTY (lot 65):
6. **TUNED_V1** — TUNED v1 legs (small_target STREAM_NIFTY).
   Control: **+₹103,050.25 / 74 legs**.
7. **TUNED_V2** — TUNED v2 legs = DEC-S1 base rows
   (`nifty_next_phase_trades.csv`) minus B-PE, A-CE, C-CE (keeps A-PE,
   B-CE, C-PE). Control: **+₹115,950.75 / 59 legs** (recorded nets;
   standing-geometry replay audit reported alongside).
8. **VWAP_C_NIFTY** — VWAP-C entries, final configuration rule C /
   EMA (9,21) / hold 0 / buffer 0.10% / exit E4
   (`vwap_ema_smalltunes_nifty_results.json` best_trades['C']).
   Control: **+₹46,579.50 / 72 legs**. Entries regenerated with the
   source's own `find_candidate`/`score_candidate` and matched
   leg-for-leg to the recorded E4 trades before scoring.

## Gate (per stream × exit, full, same run)

Timing/leak audit on every variant fill (exit ≥ entry; fill is the
exit bar's own level/open/close; the walk reads no bar after the exit
bar) · placebo = the same variant geometry on the same leg entered
+30 min (6 bars) later on the leg's own series (legs whose shifted
entry is not scoreable are dropped from the placebo and counted) ·
halves (Jan–May / Jun–Oct) · full month table · ex-top-3 legs · win
rate (reported FIRST — the owner's ask is trades ending positive) ·
₹/trade-day · November CF (Nov 2–16 legs as stored, shown separately,
never selecting).

**PASS** = total > stream control AND zero red months AND placebo
beaten AND WR ≥ 60% (the owner's standing accuracy preference).
**NEAR-MISS** = total > stream control AND WR ≥ 60% but ≥ 1 red month.
**POSITIVE-BUT-UNPROVEN** = positive total AND both halves positive
AND WR ≥ 60%, but not PASS / NEAR-MISS (total ≤ control, or placebo
not beaten).
Anything else = FAIL for the gate; its numbers are still reported.

## Shortlist (the report's ending)

Every configuration that is (a) positive in total, (b) positive in
BOTH halves, and (c) WR ≥ 60% — ranked by total — with its November CF
beside it, labelled PASS / NEAR-MISS / POSITIVE-BUT-UNPROVEN. If a
full PASS exists, its score-only forward-shadow scorer + seeded
ledger are built and the cron line named for the parent (22:05 IST
slot) — the cron itself is NOT created here. If no configuration is
even positive in both halves, the report says exactly that and shows
the best three rows.

## Data

Local stores first (the streams' own frozen loaders). Any Upstox
fetch uses the browser User-Agent and hard-stops on an HTTP 429; a
429 or a missing series marks that stream's affected legs NC —
counted, never estimated — and the programme continues with the
other streams.

## Outputs

`forty_2026-11-17.md` (ranked report) · `forty_results.json` ·
`forty_trades.csv` (every leg × control + variant, Jan–Oct and
November CF, with an independent re-sum check). Results are
checkpointed to disk per stream as the run proceeds.
