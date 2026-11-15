# Bank Nifty Tuning Programme — 2026-11-12

Owner order 2026-11-12 16:23 IST: "I need tuning all 3." This is the Bank programme.
Paper only, real money ₹0. Basis: Bank Nifty option premiums per 1 lot (30), ₹220/trade, UNIQUE-ONCE.
Frozen November primary logs/specs untouched. Output = December candidates only.

## VERDICT — NOTHING PASSED

Six pre-registered exit-side variants were gated Jan–Oct on the TUNED STACK v2 assembly under the
standing controls gate (timing + admission audits, placebos, halves, month table, ex-top-3,
independent re-sum; bars unmoved; a variant must beat the incumbent total AND fail no gate leg).
**All six FAIL.** The incumbent TUNED STACK v2 (+₹127,351.50) remains the Bank December primary.

| Variant | Gated total (Jan–Oct) | Δ vs incumbent | Placebo | Gate legs failed | November CF (Nov 2–12) |
|---|---|---|---|---|---|
| Incumbent STACK v2 | **₹127,351.50** / 111 legs | — | — | — (anchor) | **−₹960.00** |
| T-B1a LOCK30-TRAIL | ₹132,651.00 / 111 | **+₹5,299.50** | ₹25,169.50 (delay-6) | ex-top-3 legs, ex-top-3 days, August flip | −₹2,760.00 |
| T-B2b PE-STOP60 | ₹126,291.50 / 109 | −₹1,060.00 | ₹23,982.00 (delay-6) | total, ex-top-3 legs | −₹1,560.00 |
| T-B2c PE-BE50 | ₹115,125.00 / 111 | −₹12,226.50 | ₹25,883.50 (delay-6) | total, ex-top-3 legs/days, August flip | −₹960.00 |
| T-B1b LOCK10-AT-58 | ₹106,948.50 / 111 | −₹20,403.00 | ₹34,208.50 (delay-6) | total, ex-top-3 legs/days, June + August flips | −₹3,360.00 |
| T-B2a PE-STOP40 | ₹92,565.50 / 118 | −₹34,786.00 | ₹30,630.50 (delay-6) | total, ex-top-3 legs/days, July flip | **−₹360.00** |
| T-B3 LADDER-STACK | ₹38,305.50 / 111 | −₹89,046.00 | ₹27,903.00 flipped / −₹41,172.00 shifted | total, ex-top-3 legs/days, Feb + Oct flips | −₹3,886.50 |

The one variant that improves November (T-B2a, −₹360 vs −₹960) is the second-worst Jan–Oct book.
The one variant that beats the Jan–Oct total (T-B1a) makes November worse. No variant does both.

## ANCHOR (must reproduce before any variant is scored — it did)

Rebuilt leg-for-leg in `tuning_bank_2026-11-12.py`: v22 intermediate 90 legs +₹91,450.50 →
after-c4 106 legs +₹102,969.50 → stack v1 115 legs +₹123,471.50 → EVE-19 incumbent **111 legs,
+₹127,351.50**, matching `bank_positive_tuning_2026-11-10_eve19_trades.csv` exactly and the frozen
session summary battery (H1 ₹83,082 / H2 ₹44,269.50; ex-top-3 legs = ex-top-3 days ₹100,528.50;
months Jan 24,028 · Feb 15,284 · Mar 8,560 · Apr 9,810 · May 25,400 · Jun 3,040 · Jul 4,224 ·
Aug 2,059.50 · Sep 15,056.50 · Oct 19,889.50 — all positive; worst day 2026-03-05 −₹3,440;
worst DD −₹7,221; 67.4% positive days). The variant builder's identity pass reproduces the same
111 legs; `sim_variant` (the dict-bar generalisation used for re-entry legs) reproduces the frozen
`sim_g0` exactly on 31/31 frozen statics.

Final incumbent param distribution (the geometry the transforms act on):
- stop50/trig90/lock90/tgt2 180 (c4-extended PLAIN legs): 55 legs (47 PE), +₹50,753
- stop50/trig90/lock50/tgt2 150 (NS3 P21): 21 legs, +₹26,217
- stop50/trig105/lock75/tgt2 330: 13 legs, +₹41,982.50
- stop50/trig90/PLAIN at expiry (no c4): 22 legs, +₹8,399

Legs touched per variant: T-B1a/T-B1b 98 (all trig-90 legs) · T-B2a/T-B2b 90 PE legs · T-B2c 37 PLAIN PE legs.

## VARIANT DETAIL

### T-B1a LOCK30-TRAIL — ₹132,651.00 — FAIL (concentration + August)
Trig-90 legs: at +90 no exit; from the next bar the floor is entry+30, ride to the 15:20 SQ.
Total beats the incumbent by ₹5,299.50 and the delay-6 placebo (₹25,169.50) is beaten; halves pass
(H1 ₹80,722.50 / H2 ₹51,928.50). It fails where it matters: the gain is concentrated — top-3 legs
₹15,884 / ₹12,144.50 / ₹11,583.50 (sum ₹39,612 vs incumbent ₹26,823), so **ex-top-3 legs fall to
₹93,039.00 and ex-top-3 days to ₹94,759.00, both below the incumbent's ₹100,528.50** — and **August
flips green→red (+₹2,059.50 → −₹1,540.50)**. Mechanism (49 legs changed): a few runners explode
(2026-07-08 PE re-entry +₹2,480 → +₹15,884; 2026-03-06 PE +₹2,480 → +₹11,538.50), while NS3 legs that
the incumbent exits at the +150 target (+₹4,280) systematically give back to the +30 floor (+₹680,
−₹3,600 each ×4). Worst DD worsens to −₹10,821. November CF −₹2,760 (below). **Not promotable.**

### T-B1b LOCK10-AT-58 — ₹106,948.50 — FAIL
Trig-90 legs arm at +58 with the floor at entry+10 and ride. 63 legs changed; the thin +10 lock gives
back too much everywhere: total −₹20,403, ex-top-3 legs ₹68,431.50, June (+₹3,040 → −₹261.50) and
August (+₹2,059.50 → −₹3,871.50) flip red. November CF −₹3,360 (the Nov 4 winner exits at +₹80).

### T-B2a PE-STOP40 — ₹92,565.50 — FAIL (the November fix that costs ₹34,786)
PE legs stop at −40 instead of −50. 42 legs changed; tighter PE stops chop Jan–Oct winners, and the
changed stop pattern re-derives 9 extra EVE-06(a) re-entries (2 lost; 118 legs total). July flips
(+₹4,224 → −₹1,057); worst DD −₹12,898; ex-top-3 ₹65,742.50. November CF is the best of all variants
at **−₹360** — both November PE stop-outs (Nov 9, Nov 12) cap at −₹1,420 instead of −₹1,720, saving
₹600 over the window. ₹600 of November relief against ₹34,786 of Jan–Oct damage: decisively FAIL.

### T-B2b PE-STOP60 — ₹126,291.50 — FAIL (nearest miss; November gets worse, not better)
PE legs stop at −60. The nearest miss of the programme: total and ex-top-3 legs both exactly ₹1,060
below the incumbent (₹126,291.50 / ₹99,468.50; top-3 legs unchanged), all 10 months stay positive,
H1 improves to ₹86,822, placebo beaten, 31 legs changed, 2 re-entries lost (109 legs). It still fails
the total and ex-top-3 legs — and its November CF is **−₹1,560, worse than the incumbent**: the wider
stop does not rescue the November PE legs, it enlarges them (Nov 9 exits at −₹2,020 on the entry bar;
Nov 12's leg holds until 12:45 and exits at −₹2,020). The November PE leak is not a stop-width problem.

### T-B2c PE-BE50 — ₹115,125.00 — FAIL
PLAIN PE legs arm a break-even floor at +50 with the +90 target kept. 22 legs changed; total
−₹12,226.50, ex-top-3 ₹88,302, August flips (+₹2,059.50 → −₹2,667). November CF identical to the
incumbent (−₹960): both November PE stop-outs died on their entry/first bars before a +50 arm could
ever engage, and the Nov 4 runner leg's exit premium is unchanged.

### T-B3 LADDER-STACK — ₹38,305.50 — FAIL (route closes on the stack too)
The locked owner ladder (spot stages +30/+58/+82/+100, floors +5/+15/+25, T4 exit at the bar's
premium close, hard stop = premium close ≤ entry−20, SQ at the 15:10 close) on all 111 incumbent
legs, entries frozen — entry premium reconstructed on 111/111 legs, candidate NC = 0. It keeps only
30.1% of the incumbent: total ₹38,305.50, ex-top-3 legs ₹27,933, February (+₹15,284 → −₹2,972.50) and
October (+₹19,889.50 → −₹1,049) flip red. Stage census: 48 legs reached T4 (spot +100) yet the book
still collapses — premium-close exits at stage floors systematically capture less premium than the
stack's level geometry, and 38 legs never staged (hard-stop/SQ drift). Both placebos beaten (flipped
₹27,903 / shifted −₹41,172) and still nowhere near the incumbent. November CF worst at −₹3,886.50.
The ladder verdict from v21 entries (+₹16,777.50, did not displace) repeats on the stack assembly:
**ladder-on-stack is now a closed route alongside ladder-on-v21 — do not retest identically.**

## NOVEMBER COUNTERFACTUAL (Nov 2–12, from the scored stack ledger + candles)

The helper (`tuning_bank_2026-11-12_nov.py`) asserted its identity book leg-for-leg against
`november_shadow_stack_bank_log.csv` before applying any variant: Nov 4 +₹2,480 · Nov 9 −₹1,720 ·
Nov 12 −₹1,720 · all other days 0 · **total −₹960.00** ✓. November had no EVE-19 skips, no re-entry
legs and no v1 add-on legs under any variant (Nov 9 and Nov 12 re-entry derivations end in
no_trigger under every variant, including T-B2b's later Nov 12 stop at 12:45 and T-B3's relabelled
hard stops).

| Day / leg | Incumbent | T-B1a | T-B1b | T-B2a | T-B2b | T-B2c | T-B3 |
|---|---|---|---|---|---|---|---|
| Nov 4 · S3-R1 PE 55800, in 09:55 @715.30 | +2,480 (runner_stop 10:25 @805.30) | +680 (floor +30, 10:50) | +80 (floor +10, 10:05) | +2,480 | +2,480 | +2,480 | −227.50 (T2 floor, 10:05) |
| Nov 9 · BASE PE 58900, in 10:45 @815.40 | −1,720 (stop, entry bar) | −1,720 | −1,720 | −1,420 (stop −40) | −2,020 (stop −60) | −1,720 | −2,545 (hard stop at close 737.90) |
| Nov 12 · S3-R1 PE 61200, in 11:30 @841.50 | −1,720 (stop 11:35) | −1,720 | −1,720 | −1,420 (stop −40) | −2,020 (stop 12:45) | −1,720 | −1,114 (hard stop 11:30) |
| **Window total** | **−960** | **−2,760** | **−3,360** | **−360** | **−1,560** | **−960** | **−3,886.50** |

## DECEMBER RANKING — BANK

1. **TUNED STACK v2 (incumbent) — December primary, unchanged.** The only gate-clean book
   (+₹127,351.50 gated, all months positive). Its November live ledger (−₹1,720 live since the
   Nov 11 switch; −₹960 incl. backfill) is the evidence base; the Nov 20 stack-vs-legacy checkpoint
   stands as pre-registered. Segment floor check unchanged: ₹12,735.15/mo vs the ₹15,000/mo floor —
   no gated variant closes that gap.
2. **T-B1a LOCK30-TRAIL — watch-only, do NOT promote.** Highest gated total (₹132,651) but fails the
   gate on concentration (ex-top-3 legs/days), flips August red, and its November counterfactual is
   worse (−₹2,760). If forward evidence is wanted, it can run in December as a labelled shadow judged
   on December data alone — it is not a primary candidate on this record.
3. **T-B2b PE-STOP60 — closed as a fix.** Nearest numeric miss (−₹1,060 on total and ex-top-3) but
   its November counterfactual disproves the premise: wider PE stops enlarge the live PE losses.
4. **T-B2c PE-BE50 — FAIL**, August flip; November-neutral.
5. **T-B1b LOCK10-AT-58 — FAIL**, two month flips.
6. **T-B2a PE-STOP40 — FAIL** on Jan–Oct by ₹34,786 despite the best November CF (−₹360).
7. **T-B3 LADDER-STACK — FAIL decisively; route closed** (with ladder-on-v21).

## METHOD NOTES

- Transforms were pre-registered before scoring (this file's programme spec): T-B1a/T-B1b act on legs
  whose assembly trig == 90 (final params after c4 where applicable); T-B2c acts on PLAIN PE legs
  only; admission is frozen — pipe/add-on leg keys and entry premiums are identical to the incumbent
  in every variant (audited); the EVE-06(a) re-entry set is re-derived by the frozen phase-2 rule
  from each variant's own exits and scored under the variant geometry (T-B2a: +9/−2 legs; T-B2b: −2;
  others unchanged), exactly as EVE-19 re-derived it from the skipped book.
- Placebos: T-B1/T-B2 use the leg-identical delay-6 twin under the same geometry (a leg with no
  delay-6 entry counts at its candidate net) with re-entries replaced by the +60-min shifted
  derivation; T-B3 uses flipped-direction and +60-min shifted-entry with candidate-net fill for NC
  legs (the EVE-18 P1 convention, disclosed). All candidates beat their placebos; every failure is
  against the incumbent's own gate legs.
- Fill audit: every candidate exit premium is one of the variant's own level fills or the frozen
  machinery's close/open exit for that leg type — 0 violations in all six books after the audit was
  corrected for the frozen gap-through level-fill convention (a stop level fills AT the level on a
  gap-through bar, byte-identical in the incumbent's own rows, e.g. 2026-04-10) and the re-entry
  15:10-open square-off.
- Independent re-sum: every candidate book was written to CSV and re-summed from disk; all match
  their batteries. Files: `tuning_bank_2026-11-12.py`, `tuning_bank_2026-11-12_nov.py`,
  `tuning_bank_2026-11-12_results.json`, `tuning_bank_2026-11-12_{tb1a,tb1b,tb2a,tb2b,tb2c,tb3}_trades.csv`.
