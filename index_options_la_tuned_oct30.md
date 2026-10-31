# (lA) tuning — 2026-10-30 (October first, index OPTIONS only, paper only)

Scope: (lA) ONLY. No orders, no stocks, no other systems, no stacked variants, no pooled
Nifty+Bank numbers. October 2026 (1–28 Oct, 18 trading days) scored first on premiums.
Frozen definitions (written before scoring):
[index_options_la_tuned_oct30_frozen.md](sandbox://workspace/trading/index_options_la_tuned_oct30_frozen.md).
Script: [la_tune_oct30.py](sandbox://workspace/trading/la_tune_oct30.py);
leg-level output: [index_options_la_tuned_oct30_legs.csv](sandbox://workspace/trading/index_options_la_tuned_oct30_legs.csv);
diagnostics: [index_options_la_tuned_oct30_diag.json](sandbox://workspace/trading/index_options_la_tuned_oct30_diag.json).

## Base and premium rule (recap, so this report stands alone)
Base = (lA) v2 L1: PE only; confirmer (other index) break = first bar 09:30–11:30 closing below
its own OR low; rescan cutoff 13:30 where the confirmer broke strictly before 11:30, else 11:30;
rescan signal = first bar at/after the break, at/before cutoff, close < own OR low AND < own PDL,
OR width ≤ 360×scale, room ≥ 200×scale; entry next-bar open, stop = signal high, target =
entry − 2×risk, stop-before-target, square-off 15:10. Re-entry ("lA" scan): only after a morning
STOP; scan to 15:05; candidate close < OR low; band 10 ≤ risk ≤ morning risk; a morning band-fail
is skipped, an afternoon (> 11:30) band-fail ENDS the scan (stop-on-first-fail).
Premium overlay (same as the v2 premium completion): strike = ATM nearest 100 to entry spot;
expiry 2026-10-27 for 1–27 Oct, 2026-11-03 for 28 Oct; entry premium = open of the first cached
5-min option candle after signal time; stop = entry − 50, target = entry + 90 option points;
square-off 15:10; net per 1 lot = (exit − entry) × lot − ₹220 assumed cost; lot Nifty 65 / Bank 30.
Spot provisional = points × 100 shares − ₹40/leg — NOT an options-lot profit.
New legs created by a variant also had to pass room/risk ≥ 1.5 (task floor); in October that
gate rejected ZERO candidates anywhere, so it is non-binding here, not a driver of any result.
Full-target (premium) = premium exit = target; a square-off green is never a full target.
Frequency = legs ÷ 18 days × 5. "Working" = premium net > 0 AND premium full-target ≥ 50% AND
frequency ≥ 5/week, per index separately, with every leg premium-computed.

## Base reproduction — exact (must pass before variant numbers are trusted)
Base premium legs reproduce the October premium file to the rupee on both indices:
Nifty 3 legs / +₹6,678.50 (8 Oct square-off +₹2,383.25; 21 Oct target +₹5,630; 23 Oct square-off
−₹1,334.75); Bank 4 legs / +₹1,520.00 (7 Oct stop −₹1,720; 8 Oct stop −₹1,720; 21 Oct target
+₹2,480; 23 Oct target +₹2,480). Base re-entry fires on no October day under the base scan.

## Variants scored (one knob each — see frozen file for exact definitions)
- W1: rescan cutoff 14:30 where confirmer broke < 11:30, else 11:30.
- W2: rescan cutoff 15:05 where confirmer broke < 11:30, else 11:30.
- W3: tiered cutoff — break < 10:30 → 14:30; 10:30–11:30 → 13:30; ≥ 11:30 → 11:30.
- RB1: re-entry band [10, 1.5 × morning risk]; RB2: re-entry band [5, 2 × morning risk].
- BF1: OR-width ("band-filter") cap 360 → 480×scale; BF2 (control): cap 360 → 240×scale.
- S1: afternoon stop-on-first-fail REMOVED (afternoon band-fail skips, scan continues to 15:05).
- S2: afternoon stop-on-first-fail applies only after 13:30 (fails at ≤ 13:30 skip).
- X1: keep morning only if confirmer close at signal-bar time < confirmer OR low.
- X2: day eligible only if the confirmer bar after its break bar also closes < confirmer OR low.
- X3: confirmer break-bar close must also be < confirmer PDL.
- X4: keep morning only if confirmer close at entry-bar time (signal + 5 min) < confirmer OR low.
- O1 itself was NOT re-scored (already scored Jan–Oct); X1/X4 are its two component conditions
  scored separately, which is new information, not a repeat of O1.

## Before / after per track — October premiums first, spot alongside
All variant legs were premium-computed from cached candle files (0 NOT_COMPUTED in any variant),
so every premium figure below is complete, not a subset. FT = premium full-target rate.

| Variant / index | Legs (base → after) | Premium net / 1 lot (base → after) | Premium FT (base → after) | Freq/week (base → after) | Spot prov. net (base → after) | Verdict |
|---|---|---|---|---|---|---|
| W1 = W2 = W3, Nifty | 3 → 4 | +₹6,678.50 → +₹3,208.50 | 33.3% → 25.0% | 0.83 → 1.11 | +₹28,020 → +₹27,100 | DISCARD — adds a loser, net halved, FT down |
| W1 = W2 = W3, Bank | 4 → 4 | +₹1,520 → +₹1,520 (no change) | 50.0% → 50.0% | 1.11 → 1.11 | +₹28,275 → +₹28,275 | DISCARD — no effect |
| RB1 = RB2, Nifty | 3 → 3 | +₹6,678.50 (no change) | 33.3% (no change) | 0.83 (no change) | +₹28,020 (no change) | DISCARD — no effect (no Nifty morning stops in Oct) |
| RB1 = RB2, Bank | 4 → 5 | +₹1,520 → +₹4,000.00 | 50.0% → 60.0% | 1.11 → 1.39 | +₹28,275 → +₹40,160 | CLOSEST (Bank) — net + FT pass, frequency fails |
| BF1, Nifty | 3 → 3 | +₹6,678.50 (no change) | 33.3% (no change) | 0.83 (no change) | +₹28,020 (no change) | DISCARD — no effect |
| BF1, Bank | 4 → 4 | +₹1,520 (no change) | 50.0% (no change) | 1.11 (no change) | +₹28,275 (no change) | DISCARD — no effect (see why below) |
| BF2, Nifty | 3 → 1 | +₹6,678.50 → −₹1,334.75 | 33.3% → 0% | 0.83 → 0.28 | +₹28,020 → +₹11,390 | DISCARD — destroys frequency; kept leg is premium-negative despite a spot target |
| BF2, Bank | 4 → 1 | +₹1,520 → +₹2,480 | 50.0% → 100% | 1.11 → 0.28 | +₹28,275 → +₹20,200 | DISCARD — single trade, not a system |
| S1, Nifty | 3 → 3 | +₹6,678.50 (no change) | 33.3% (no change) | 0.83 (no change) | +₹28,020 (no change) | DISCARD — no effect |
| S1, Bank | 4 → 5 | +₹1,520 → +₹4,000.00 | 50.0% → 60.0% | 1.11 → 1.39 | +₹28,275 → +₹36,435 | CLOSEST (Bank) — net + FT pass, frequency fails; same premium as RB, different spot leg |
| S2, Nifty / Bank | 3 → 3 / 4 → 4 | no change both | no change both | no change both | no change both | DISCARD — no effect |
| X1, Nifty / Bank | 3 → 3 / 4 → 4 | no change both | no change both | no change both | no change both | DISCARD — no effect; signal-bar persistence holds on all 7 base legs |
| X2, Nifty | 3 → 2 | +₹6,678.50 → +₹4,295.25 | 33.3% → 50.0% | 0.83 → 0.56 | +₹28,020 → +₹16,330 | DISCARD — FT up only by deleting the 8 Oct winner; net and frequency down |
| X2, Bank | 4 → 3 | +₹1,520 → +₹3,240.00 | 50.0% → 66.7% | 1.11 → 0.83 | +₹28,275 → +₹35,750 | DISCARD — net + FT up by deleting the 7 Oct loser, but frequency down; still fails frequency |
| X3, Nifty | 3 → 0 | +₹6,678.50 → ₹0 | — (no trades) | 0.83 → 0 | +₹28,020 → ₹0 | DISCARD emphatically — kills the whole track |
| X3, Bank | 4 → 1 | +₹1,520 → −₹1,720 | 50.0% → 0% | 1.11 → 0.28 | +₹28,275 → −₹8,510 | DISCARD emphatically — keeps only the 8 Oct loser |
| X4, Nifty / Bank | 3 → 2 / 4 → 3 | +₹6,678.50 → +₹4,295.25 / +₹1,520 → +₹3,240.00 | 33.3% → 50.0% / 50.0% → 66.7% | 0.83 → 0.56 / 1.11 → 0.83 | +₹28,020 → +₹16,330 / +₹28,275 → +₹35,750 | DISCARD — October numbers identical to X2 (same 2 days dropped); see decomposition note below |

## October premium table — base legs + every NEW leg (unchanged variants = base legs)
Base legs (all variants except those listed as changed repeat these exactly):

| Index | Date | Leg | Signal | Strike / expiry | Entry prem. | Exit prem. / time / reason | Premium net / 1 lot | Spot net prov. |
|---|---|---|---|---|---|---|---|---|
| NIFTY | 2026-10-08 | morning | 11:25 | 22300PE / 2026-10-27 | 247.05 @ 11:30 | 287.10 @ 15:10 square-off | +₹2,383.25 | +₹11,690 target |
| NIFTY | 2026-10-21 | morning | 11:35 | 22800PE / 2026-10-27 | 151.30 @ 11:40 | 241.30 @ 14:45 target | +₹5,630.00 | +₹4,940 target |
| NIFTY | 2026-10-23 | morning | 10:05 | 22500PE / 2026-10-27 | 125.85 @ 10:10 | 108.70 @ 15:10 square-off | −₹1,334.75 | +₹11,390 target |
| BANKNIFTY | 2026-10-07 | morning | 09:35 | 54700PE / 2026-10-27 | 736.90 @ 09:40 | 686.90 @ 09:40 stop | −₹1,720.00 | −₹7,475 stop |
| BANKNIFTY | 2026-10-08 | morning | 13:15 | 54600PE / 2026-10-27 | 676.10 @ 13:20 | 626.10 @ 13:35 stop | −₹1,720.00 | −₹8,510 stop |
| BANKNIFTY | 2026-10-21 | morning | 11:15 | 55200PE / 2026-10-27 | 379.95 @ 11:20 | 469.95 @ 11:35 target | +₹2,480.00 | +₹20,200 target |
| BANKNIFTY | 2026-10-23 | morning | 09:55 | 54400PE / 2026-10-27 | 321.55 @ 10:00 | 411.55 @ 10:05 target | +₹2,480.00 | +₹24,060 target |

New legs (the only legs any variant adds; everything else above is unchanged):

| Variant / index | Date | Leg | Signal | Strike / expiry | Entry prem. | Exit prem. / time / reason | Premium net / 1 lot | Spot net prov. |
|---|---|---|---|---|---|---|---|---|
| W1/W2/W3, NIFTY | 2026-10-07 | morning | 14:10 | 22600PE / 2026-10-27 | 272.15 @ 14:15 | 222.15 @ 14:25 stop | −₹3,470.00 | −₹920 stop (spot risk only 8.8 pts; premium stop is the fixed −50, so premium risk is NOT small — see caveat) |
| RB1/RB2, BANKNIFTY | 2026-10-08 | re-entry | 13:40 | 54600PE / 2026-10-27 | 689.40 @ 13:45 | 779.40 @ 14:00 target | +₹2,480.00 | +₹11,885 square-off green (NOT a spot target) |
| S1, BANKNIFTY | 2026-10-08 | re-entry | 13:45 | 54600PE / 2026-10-27 | 702.00 @ 13:50 | 792.00 @ 14:05 target | +₹2,480.00 | +₹8,160 target |

Removed legs (filters only): X2 and X4 both remove NIFTY 2026-10-08 (morning winner) and
BANKNIFTY 2026-10-07 (morning loser); X3 removes all NIFTY legs and all BANKNIFTY legs except
2026-10-08; BF2 keeps only NIFTY 2026-10-23 and BANKNIFTY 2026-10-21. X1 removes nothing.

## Why each knob did or did not move — diagnostics (not just the totals)
- Rescan window (W1/W2/W3 collapse to ONE effective change in October): the only added signal
  is NIFTY 7 Oct 14:10 (confirmer Bank broke 09:35; no qualifying NIFTY close by 13:30; first
  qualifying close at 14:10). No signal appears 14:30–15:05 on any day, so W2 adds nothing over
  W1; W3 adds the same leg because the 7 Oct confirmer break (09:35) is before 10:30 too. On
  BANK, no window extension adds anything: 28 Oct (confirmer break 10:15) has no qualifying
  close even to 15:05, and the width-fail days (below) stay width-failed under W. The window
  extensions are therefore not three independent results — quoting W1, W2 and W3 as three
  confirmations would triple-count one trade.
- Re-entry band (RB1 = RB2 in October): BANK 8 Oct morning risk is 84.70. The base scan's first
  afternoon candidate is 13:40, risk 115.00 — outside [10, 84.70], so the base scan ends there.
  Widening the band to [10, 127.05] (RB1) or [5, 169.40] (RB2) takes that same 13:40 candidate;
  the two bands are indistinguishable in October. On BANK 7 Oct, no variant adds a re-entry:
  after the morning stop there is NO later close below OR low at all (empty scan), so no band
  or skip rule can manufacture one. On NIFTY there is no morning stop day in October, so no
  re-entry variant can fire there at all.
- Stop-on-first-fail (S1 vs S2): S1 skips the 13:40 band-fail (risk 115.00) and takes the next
  candidate, 13:45, risk 41.00, which reaches a spot target (+₹8,160) and a premium target
  (+₹2,480). S2 does nothing because the 13:40 fail is AFTER 13:30, so it still ends the scan.
  S1's gain therefore comes specifically from skipping a post-13:30 first-fail. RB and S1 end
  with the SAME October premium total on BANK (+₹4,000) via DIFFERENT spot legs (RB: square-off
  green; S1: target) — on premiums they are indistinguishable here, and they must NOT be
  stacked: under a widened band the scan takes 13:40 first, so S1's 13:45 leg would never be
  reached; stacking is not additive.
- Band-filter / OR width (BF1 no effect, BF2 destructive): BANK width-fail days under the base
  cap are 5 Oct (width 473.30 vs cap 356.40), 12 Oct (389.75 vs 361.68), 16 Oct (373.90 vs 365.31).
  Under BF1's 480×scale cap all three pass the width gate — yet still no signal, because on
  those days there is NO bar closing below OR low AND below PDL at all (first qualifying close:
  none). Width was not the binding constraint; the missing close was. BF2 (240×scale) keeps
  only NIFTY 23 Oct (width 87.55) and BANK 21 Oct (width 181.20) — the width cap is a frequency
  killer, not a quality filter, at that level.
- Cross-confirmation decomposition (X1/X4 vs O1): X1 drops nothing — the confirmer is still
  below its OR low at the signal-bar time on all 7 base legs. X4 drops exactly the same 2 days
  O1 dropped in October Family C (NIFTY 8 Oct winner; BANK 7 Oct loser): at the entry-bar time
  the confirmer has already closed back above its OR low (NIFTY 8 Oct: Bank close 54,791.05 at
  11:30 vs Bank OR low 54,767.55; BANK 7 Oct: Nifty close 22,617.10 at 09:40 vs Nifty OR low
  22,600.45). So O1's October (lA) effect is entirely its entry-bar condition; the signal-bar
  condition adds nothing in October. X2 drops the same 2 days for a different reason (the
  confirmer's break bar is not followed by a second close below OR low on those days) — same
  October outcome, different rule, so X2 and X4 are not two independent confirmations either.
- X3 (confirmer PDL depth) fails structurally: confirmer break-bar closes sit ABOVE confirmer
  PDL on 6 of 7 base days (misses by 26–228 points; e.g. NIFTY 21 Oct break close 55,559.35 vs
  Bank PDL 55,331.10). Only BANK 8 Oct passes (break close 22,472.45 < Nifty PDL 22,546.30) —
  and that day is a loser. A PDL-depth confirmer filter keeps the loser and drops every winner
  in October; it is not a usable (lA) filter.

## Verdict — NO variant is working; nothing adopted
No variant meets net > 0 AND full-target ≥ 50% AND frequency ≥ 5/week on October premiums, on
either index. Closest, with the failing leg named:
- BANK closest: RB1 / RB2 / S1 — net +₹4,000.00 (pass), full-target 60.0% (pass), frequency
  1.39/week (FAIL, 3.61/week short). Base BANK also passes net + full-target (50.0%) at 1.11/week.
- NIFTY closest: X2 / X4 — net +₹4,295.25 (pass), full-target 50.0% (pass), frequency 0.56/week
  (FAIL, 4.44/week short). Base NIFTY fails full-target too on premiums (33.3%): its three spot
  targets become only one premium target, because two premium rises (+40.05 on 8 Oct, and the
  23 Oct premium never reaching +90) fall short of the fixed +90 overlay.
- Everything else either hurts (W1 NIFTY, X3, BF2) or does nothing (W on BANK, BF1, S2, X1,
  RB/S1 on NIFTY). No variant is kept as best beyond the "closest" label above, and no variant
  is combined with any other.

## Why frequency cannot be fixed by these knobs — the October ceiling
Confirmer-break days in October: NIFTY 7 of 18 (5, 7, 8, 12, 16, 21, 23 Oct), BANK 8 of 18
(5, 7, 8, 12, 16, 21, 23, 28 Oct). A morning (lA) leg can only exist on a confirmer-break day, and
window/band/width knobs do not create confirmer breaks — so the morning-leg ceiling under this
knob set is 7 legs (1.94/week) for NIFTY and 8 legs (2.22/week) for BANK, before any signal
quality filter. Actual October conversion: NIFTY 4 of 7 break days (after W), BANK 4 of 8.
Re-entries add at most one leg per morning-stop day, and in October only BANK 8 Oct yields one
(BANK 7 Oct yields none under any variant). The absolute October ceiling for (lA) under these
knobs is therefore roughly 8–9 legs per index (~2.2–2.5/week) — less than half the 5/week bar.
Reaching 1/day for (lA) alone would require changing the confirmer definition itself (a wider
confirmer-break window, a different confirmer, or a non-confirmed leg) — that is a NEW family,
not a knob in this task, and it was deliberately not attempted here because the task restricted
extensions to days where the confirmer already broke early. 10–11 days per index have no
confirmer break at all and can never trade under (lA) as defined.

## Jan–Oct check — NOT run, by the task's own condition
The task orders a Jan–Oct check only for a variant that passes October. No variant passes
October, so no Jan–Oct scoring (spot or premium) was run for W/RB/BF/S/X variants in this run.
Jan–Oct (lA) base and O1 numbers already in the progressive log are NOT these variants' Jan–Oct
numbers and must not be quoted as such. No new Jan–Oct premium fetch was attempted (and none was
needed: every October variant leg was already premium-computed from cached candles).

## Caveats and open items for the parent
1. Premium scoring uses the fixed −50/+90 overlay, not (lA)'s native spot stop/target. That is
   why spot targets become premium square-offs (NIFTY 8 Oct, 23 Oct) and why a tiny spot-risk
   trade (W1 NIFTY 7 Oct, risk 8.8 pts, spot stop −₹920) still loses the full premium stop
   (−₹3,470): premium risk under the overlay is fixed, regardless of spot risk.
2. RB vs S1 on BANK are premium-identical in October (+₹2,480 added leg each) but spot-different
   (square-off green vs target). Do not present either as "better" on premiums alone, and do not
   stack them.
3. October is 18 days; every gain or loss above is 1 leg wide except the filter deletions.
   Nothing here is adoption-grade; November paper from Mon 2026-11-02 remains the validation
   step, with the BASE (lA) v2 definition (not any variant here) unless the parent freezes one
   of the "closest" variants above as a separate November watch candidate.
4. No browser fetch was run in this subagent run (a subagent cannot run the live-browser fetch);
   it was also not needed, because all 7 base legs and all 3 new legs hit already-cached October
   option candles. Any future (lA) variant whose legs fall outside the cached contract set would
   need a browser-capable parent run for premium completion, and must be reported NOT_COMPUTED
   until then.
