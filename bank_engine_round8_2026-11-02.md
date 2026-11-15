# Bank Nifty Engine — ROUND 8 (2026-11-02)

Basis: index-options premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE,
paper only, real money ₹0. Gating reference: **book v21 = +₹83,650.50**
(99 legs, FT90 49.5%, 2.44/week), the causal book frozen at Round 6.
Every candidate was scored with the full controls gate in the same run
(timing audit + admission/feature-timing certification via the causal
pipeline + delay-6 placebo + halves + month table + ex-top-3 +
independent re-sum), on causal times only. The November primary
BNF-PAPER-V1 and its logs/specs were not touched.

**Result: 6 cycles (162–167), ZERO banked. Book v21 stands unchanged.
Ending pace ₹8,365.05/month vs the ₹15,000 floor — gap ₹66,349.50,
floor NOT met.** The round's main deliverable is forward-looking: v21 is
now frozen as a fully specified, timing-certified, regeneration-verified
December candidate with pre-registered pass/kill (WS2/WS3).

## WS1 — NS1 causal neighbours (Cycles 162–165)

Pre-registered cells (stated in the brief before scoring), each a whole-book
re-gate vs v21 with NS1 second legs regenerated (`ns1_gen_legs`, causal
crossing+1 entries). Disclosure: Round-5 WS2 gated room 1.4/1.6 and windows
14:00/15:00 against REF_AUD (Lesson 68); rooms 1.25/1.75 were never scored
anywhere, and no cell had ever been gated against v21.

- **Cycle 162 — sanity: PASS.** The regenerated frozen-cell set
  (room 1.5, window 14:30; 65 candidate legs) equals v21's NS1 set exactly,
  and the frozen cell through the judge reproduces v21 to the paisa
  (+₹83,650.50, n=99, FT90 49.5, placebo −₹4,313.50, NC 0).
- **Cycle 163 — room 1.25: EXACT NO-OP.** 67 candidates (2 more pass the
  room test), but the taken book is byte-identical to v21 (+₹83,650.50,
  n=99, every control identical — trades file diff empty). The marginal
  candidates are absorbed by key/band competition downstream. Nothing to
  bank.
- **Cycle 164 — room 1.75: EXACT NO-OP.** 64 candidates (1 fewer); the
  taken book is again byte-identical to v21. The removed candidate was
  not a taken leg. Nothing to bank.
- **Cycle 165 — window end 15:00: REJECTED.** 67 candidates; exactly one
  added taken leg — 2026-09-03 PE second leg, entry 15:05 @ 588.0,
  square-off 15:20 @ 579.8, net −₹466.00 → book **+₹83,184.50** (n=100,
  FT90 49.0%, placebo −₹4,313.50 beaten, ex-top-3 +₹54,144.50). Fails net
  (−₹466.00) and FT90 (49.0 < 49.5); no month flip (September +10,776.50 →
  +10,310.50). The placebo twin records NC 1 (the added leg's +30-minute
  entry has no candle path — after-hours bar), noted, not estimated.

**WS1 verdict:** the NS1 axis is closed on the causal book — the frozen
cell (room ≥ 1.5, window to 14:30) stands, confirming Lesson 68's plateau
against the current book (Lesson 84). The second-leg family's value is
fully extracted by the pool + band + state machinery around it.

## WS2 — December freeze of v21 (Cycle 166)

Frozen in `bank_engine_frozen.md` (ROUND 8 block, §§1–12), written BEFORE
the Cycle-167 verification run:

- **Full tradeable specification**: basis (§1); the B2 pool in causal
  order — component legs at their own entry bars, Volrix (b) as the
  regenerated rule (trigger ≤ −1.0%, cooldown 15, 09:20 entry, entry-spot
  ATM), the causal-solo ≤09:55 drop judged as-of the entry bar,
  UNIQUE-ONCE earliest entry, Skill-CE representative block (§2); NS1
  second legs in regenerated form at the frozen cell (§3); pool filters —
  NS1-CE block and the [400, 550) premium band (§4); the signal stream,
  anchored trailing-10 state, cold-(lA) skip and segment assignment (§5);
  the exit assembly per segment (lt400 −50/+105/lock +75/tgt2 +330;
  ge400_warm −50/+90/lock +90/tgt2 +180; ge400_cold plain −50/+90;
  expiry-day legs plain) at square-off 15:20 (§6); the add-on stack in
  sequential admission order NS3 (GD+GU only, signal+5 entries, own
  geometry −50/+90/lock +50/tgt2 +150) → S3-A → S3-E → S3-D under the
  Round-3 admission rules (§7).
- **Timing certification (§10)**: every admission condition and feature
  certified knowable at its decision bar, in writing — per family
  (own-signal entries, prior-close Volrix trigger and bias, as-of solo
  judgement, NS1 next-bar entry after a completed crossing bar, band and
  segment read at the fill, state counting only exits known at entry,
  NS3 gap known at the open, S3 entries at signal+5, DTE by calendar).
- **December expiry handling (§8)**: monthly expiry in force under the
  calendar rule behind the frozen EXPIRIES series (last Tuesday, moved to
  the preceding trading day on a holiday — the rule behind 2026-03-30 and
  the November monthly expiry 2026-11-23); December's date under that rule
  is 2026-12-29, to be confirmed against the exchange contract master and
  named in the December log before the first December trade (contract
  master governs if it differs). Weekly contracts never used.
- **NC policy (§9)**: an unobtainable contract is NOT_COMPUTED — excluded,
  counted, named, never estimated or substituted; **NC > 0 in December →
  the verdict is PROVISIONAL, never a pass**.
- **Pre-registered December pass/kill (§11)**, judged on December 2026
  data alone:
  - **PASS: December net > ₹0 AND timing audit 0 violations AND NC = 0.**
  - **KILL: December net ≤ −₹5,000, OR any timing violation** (a killed
    candidate is retired, not re-tuned on December data).
  - PROVISIONAL: NC > 0, or −₹5,000 < net ≤ ₹0 (month stands at face
    value, not re-tested on the same data).
  - Floor-pace context printed beside, never as the test: December
    ≥ +₹15,000 would be a floor-pace month.

## WS3 — Regeneration verification (Cycle 167)

The frozen specification was regenerated through the audited causal
pipeline and compared against the trades of record
(`bank_engine_r6_v21_trades.csv`):

- **Leg-for-leg: 99 legs compared, 0 mismatches** (date, direction,
  family, representative, entry/exit times and premiums, exit reason,
  full-target flag, net — all equal).
- **Net +₹83,650.50 to the paisa**; FT90 49.5%, 2.44/week, no red
  month-ends; halves +₹61,938.00 / +₹21,712.50; placebo (delay-6)
  −₹4,313.50 beaten; ex-top-3 +₹54,610.50; NOT_COMPUTED 0; timing audit
  0 violations; independent re-sum of the regenerated file
  (`bank_engine_r8_v21_regen_trades.csv`) 99 / +₹83,650.50 exact.
- **VERIFICATION: PASS.** Evidence: `bank_r8_regen.json`.

## Ending scorecard — book v21 (unchanged)

| Measure | Value |
|---|---|
| Jan–Oct 2026 net (premiums, 1 lot) | **+₹83,650.50** |
| Trades | 99 (2.44/week) |
| FT90 | 49.5% |
| Months | Jan +22,748 · Feb +20,480 · Mar +1,120 · Apr −90 · May +17,680 · Jun +560 · Jul −3,680 · Aug −873.50 · Sep +10,776.50 · Oct +14,929.50 (no red month-ends) |
| Halves | +₹61,938.00 / +₹21,712.50 |
| Placebo (delay-6) | −₹4,313.50 — beaten |
| Ex-top-3 | +₹54,610.50 |
| NOT_COMPUTED / timing violations | 0 / 0 |
| Monthly pace vs ₹15,000 floor | **₹8,365.05 — gap ₹66,349.50, NOT met** |

Round 8 closes the last neighbour axis of the existing families on causal
data (NS1) and converts v21 from a change-note lineage into a frozen,
certified, regeneration-verified December candidate. The remaining gap
is, as at Round 7's close, outside every axis measured on causal data —
it needs a genuinely new causal signal family or forward (November+)
evidence. The standing order applies: the engine does not stop; the next
round is the parent agent's to launch.
