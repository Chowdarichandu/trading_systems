# Index OPTIONS — O1 cross-confirmation persistence, Jan–Oct 2026
Paper only, no orders, no stocks. Frozen definition (written before scoring):
[index_options_o1_janoct_frozen.md](sandbox://workspace/trading/index_options_o1_janoct_frozen.md).
Full trade-level file (503 base trades): [index_options_o1_janoct_trades.csv](sandbox://workspace/trading/index_options_o1_janoct_trades.csv).
Script: [o1_janoct.py](sandbox://workspace/trading/o1_janoct.py) + (lA) L1 engine [o1_la_l1.py](sandbox://workspace/trading/o1_la_l1.py).

Window: Jan–Oct 2026, 203 trading days. Nifty and Bank separately, never pooled.
O1 = PE breakdown taken ONLY if the confirming index (the other index) closes below its
own OR low on BOTH the signal bar AND the entry bar (next bar, whose open is the entry).
CE trades are never filtered by O1 and are kept unchanged on every track.
Unit: spot provisional = points × 100 shares − ₹40 per leg. This is NOT an options-lot
profit and NOT a futures profit. Premiums NOT recomputed for Jan–Oct (see October-only
overlay at the end). No cap is re-applied after filtering; filtered trades are not replaced.
Full-target = exit_reason target AND day net > 0. Frequency = trades ÷ 203 × 5 per week.
Nothing here is adopted: Jan–Oct is in-sample for O1 (October was its birth month);
November 2026 paper from 2026-11-02 remains validation.

## Headline — do the October keeps survive Jan–Oct?
- October keeps were Skill Bank and (lA) Bank. On the full Jan–Oct window NEITHER survives
  as a viable track: Skill Bank O1 is still deeply negative (−₹67,330), and (lA) Bank O1,
  while positive on Jan–Oct (+₹29,055), is negative once October itself is stripped out
  (−₹6,695 ex-October). O1 helps both tracks versus their bases, but it does not make
  either one a positive system outside October.
- The only tracks where O1 flips the sign on Jan–Oct are the two Bank tracks (V4 Bank and
  (lA) Bank) — and both flips are October-driven (see ex-October check below).
- O1's damage is concentrated on the best track: (lA) Nifty, the strongest base in this
  run (+₹114,060, 75.6% win), loses ₹28,790 under O1 and every single filtered trade is
  a winner (7 winners, 0 losers removed). O1 fights (lA) Nifty's edge; it does not refine it.
- No O1 track reaches 5 trades/week (best: Skill Bank 2.19/week, down from 3.20 base).
  O1 can only delete trades, so it can never fix the frequency leg.

## Per-track table (paste-ready)

| Track | Base trades | Base net prov. | Base win | Base full-target | Base /wk | O1 trades | O1 net prov. | O1 win | O1 full-target | O1 /wk | Filtered out (winners / losers, filtered net) | Verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| V4 Nifty | 46 | +₹33,130 | 21/46 (45.7%) | 21/46 (45.7%) | 1.13 | 24 | +₹29,005 | 12/24 (50.0%) | 12/24 (50.0%) | 0.59 | 22 (9 / 13, +₹4,125) | DISCARD — net falls ₹4,125, frequency halved |
| V4 Bank | 46 | −₹28,635 | 14/46 (30.4%) | 14/46 (30.4%) | 1.13 | 26 | +₹15,755 | 9/26 (34.6%) | 9/26 (34.6%) | 0.64 | 20 (5 / 15, −₹44,390) | KEEP as candidate (Jan–Oct only, weak) — sign flip, but see caveats |
| Skill v2 Nifty | 125 | +₹47,265 | 49/125 (39.2%) | 48/125 (38.4%) | 3.08 | 77 | +₹30,155 | 29/77 (37.7%) | 28/77 (36.4%) | 1.90 | 48 (20 / 28, +₹17,110) | DISCARD — net, win and FT all fall |
| Skill v2 Bank | 130 | −₹157,750 | 39/130 (30.0%) | 36/130 (27.7%) | 3.20 | 89 | −₹67,330 | 28/89 (31.5%) | 25/89 (28.1%) | 2.19 | 41 (11 / 30, −₹90,420) | DISCARD — improves ₹90,420 but still deeply negative; October keep does NOT survive |
| (lA) v2 Nifty | 45 | +₹114,060 | 34/45 (75.6%) | 25/45 (55.6%) | 1.11 | 38 | +₹85,270 | 27/38 (71.1%) | 20/38 (52.6%) | 0.94 | 7 (7 / 0, +₹28,790) | DISCARD — removes winners only; confirms October discard |
| (lA) v2 Bank | 39 | −₹21,320 | 15/39 (38.5%) | 11/39 (28.2%) | 0.96 | 34 | +₹29,055 | 15/34 (44.1%) | 11/34 (32.4%) | 0.84 | 5 (0 / 5, −₹50,375) | KEEP as candidate (Jan–Oct only) — cleanest filter: losers only; still needs Nov paper |
| V5-v2 Nifty | 32 | +₹47,965 | 16/32 (50.0%) | 16/32 (50.0%) | 0.79 | 20 | +₹37,610 | 10/20 (50.0%) | 10/20 (50.0%) | 0.49 | 12 (6 / 6, +₹10,355) | DISCARD — net falls, win/FT flat, frequency halved |
| V5-v2 Bank | 40 | +₹16,415 | 14/40 (35.0%) | 14/40 (35.0%) | 0.99 | 22 | +₹26,145 | 8/22 (36.4%) | 8/22 (36.4%) | 0.54 | 18 (6 / 12, −₹9,730) | DISCARD — marginal gain (+₹9,730, +1.4pp) for halved frequency; October slice also discards |

Base definitions (asymmetric by design, stated so the table is not misread): V4, Skill v2 (S1)
and (lA) v2 (L1) are UNCAPPED candidate sets; V5-v2 is the CAPPED pool (3 index/week,
1/symbol/week, per calendar month), because its definition includes the cap. V4 uncapped
(92 trades) is not the capped V4 series (62 trades); Skill v2 (S1, 255 trades) is not the
bias-aligned/room-filtered Skill series inside the V5 pool; (lA) v2 L1 (84 trades) is not
the capped (lA) series (47 trades). Volrix v2: no O1 effect by construction (no OR signal bar).

## October cross-check — all 8 slices reproduce Family C exactly
Recomputing O1 on the October slice of each Jan–Oct base gives the Family C C1 deltas
to the rupee (no mismatches): V4 Nifty 4→2, +₹2,725→+₹2,755; V4 Bank 5→3,
+₹67,690→+₹60,900; Skill Nifty 8→4, +₹8,420→+₹15,780; Skill Bank 9→7,
+₹8,675→+₹20,790; (lA) Nifty 3→2, +₹28,020→+₹16,330; (lA) Bank 4→3,
+₹28,275→+₹35,750; V5 Nifty 3→2, +₹8,195→+₹2,755; V5 Bank 4→2, +₹43,630→+₹36,840.
This cross-check is what caught the (lA) base error below — it passed only after the fix.

## Base correction found during this run — (lA) source (read before quoting (lA) numbers)
The merged Jan–Oct JSONs (merged_skill_la_summary_2026-MM.json, la_candidates) use the
BASE 11:30 rescan without the L1 extension and drop 2 October v2 days (Bank 8 Oct 13:15,
Nifty 21 Oct 11:35). They were rejected as the (lA) base. The (lA) numbers above come
from a fresh L1 implementation (o1_la_l1.py) that reproduces October Family C exactly.
Any (lA) Jan–Oct total quoted from the merged JSONs (66 candidates) understates the L1
base (84 trades) and must not be mixed with the numbers here. Sensitivity: reading
"broke before 11:30" as ≤ 11:30 instead of strictly < 11:30 adds exactly one trade —
Nifty 2026-08-04, signal 12:05, day net −₹1,655 — excluded under the strict reading used here.

## Ex-October robustness check (not a second adoption test — a warning label)
O1 net with October stripped out (base ex-Oct → O1 ex-Oct, trades in brackets):
- V4 Nifty: +₹30,405 (42) → +₹26,250 (22) — stays positive, O1 still costs money.
- V4 Bank: −₹96,325 (41) → −₹45,145 (23) — O1 helps a lot but the sign flip on Jan–Oct
  is entirely October (+₹60,900 of the O1 net sits in October alone).
- Skill Nifty: +₹38,845 (117) → +₹14,375 (73) — stays positive, O1 costs ₹24,470.
- Skill Bank: −₹166,425 (121) → −₹88,120 (82) — still deeply negative without October.
- (lA) Nifty: +₹86,040 (42) → +₹68,940 (36) — stays strongly positive; O1 costs ₹17,100.
- (lA) Bank: −₹49,595 (35) → −₹6,695 (31) — the Jan–Oct sign flip (+₹29,055) is entirely
  October (+₹35,750); ex-October O1 is still negative.
- V5 Nifty: +₹39,770 (29) → +₹34,855 (18) — stays positive, O1 costs ₹4,915.
- V5 Bank: −₹27,215 (36) → −₹10,695 (20) — same pattern: Jan–Oct gain is October-driven.
Reading: O1's two sign flips do not hold outside October. The October keeps survive the
full-window arithmetic but not the ex-October check — that is why neither is adopted and
both need November paper, where October cannot rescue them.

## Where O1 actually works — the PE leg vs the CE drag
O1 only touches PE trades, so on tracks with a bad CE leg it cannot rescue the track:
- Skill Bank PE leg alone: base +₹8,885 (81 PE trades) → O1 +₹99,305 (40 PE trades kept).
  The track stays negative because its CE leg, untouched by O1, is −₹166,635 (49 trades).
  O1 is a good PE filter on Bank; Skill Bank's problem is its CE side, not its PE side.
- V4 Bank PE leg: base −₹39,985 (41 PE) → O1 +₹4,405 (21 PE kept); CE leg +₹11,350.
- Skill Nifty PE leg: base +₹43,930 (79 PE) → O1 +₹26,820 (31 PE kept) — O1 hurts Nifty PE.
- (lA) tracks are PE-only, so their O1 deltas are pure PE-filter effects: Nifty −₹28,790
  (all winners removed), Bank +₹50,375 (all losers removed). The same filter is a winner-killer
  on Nifty (lA) and a loser-killer on Bank (lA) — that index split, not a universal edge,
  is the Jan–Oct story of O1.

## October-only premium overlay (NOT a Jan–Oct premium result)
Premiums NOT recomputed for Jan–Oct. For the O1-kept October subset only, premiums known
in index_options_v2_october_trades.csv (lot Nifty 65 / Bank 30, stop −50 / target +90
option points, ₹220 assumed cost, as in v2):
- Skill Nifty O1-kept October (4 CE trades): 0 premiums computed — all NOT_COMPUTED.
- Skill Bank O1-kept October (7 trades): 0 premiums computed — all NOT_COMPUTED.
- (lA) Nifty O1-kept October (21 Oct +₹4,940 spot, 23 Oct +₹11,390 spot): 1 computed —
  23 Oct premium −₹1,334.75 (spot winner, premium loser — the known v2 reversal); 21 Oct NOT_COMPUTED.
- (lA) Bank O1-kept October (8 Oct −₹8,510 spot, 21 Oct +₹20,200 spot, 23 Oct +₹24,060 spot):
  2 computed, both +₹2,480 (21 + 23 Oct) = +₹4,960 premium on the computed subset; 8 Oct NOT_COMPUTED.
- V5 Nifty O1-kept October (23 Oct +₹11,390 spot, 26 Oct −₹8,635 spot): both computed —
  −₹1,334.75 + (−₹3,470) = −₹4,804.75 premium vs +₹2,755 spot.
- V5 Bank O1-kept October (1 Oct +₹16,640 spot, 21 Oct +₹20,200 spot): 1 computed —
  21 Oct +₹2,480; 1 Oct NOT_COMPUTED.
- V4 October premium rows do not exist separately; V4's O1-kept October trades coincide
  with V5 rows (same dates/directions), so the V5 premium figures above are the overlapping
  values, labelled as overlap-derived, not V4-specific: V4 Nifty kept-October premium
  overlap −₹4,804.75 (2 trades), V4 Bank kept-October premium overlap +₹4,960 on 2 computed
  trades (21 + 23 Oct) with 1 Oct NOT_COMPUTED. Do not quote these as V4 premium P&L.
Net premium message: the October O1 premium subset is too thin (at most 2 computed trades
per track, and Skill tracks have zero) to confirm or overturn any spot verdict above.

## Verdicts in one paragraph each
- V4 Nifty — DISCARD. Win/FT tick up (45.7% → 50.0%) only because 22 trades are deleted;
  net falls and frequency halves (1.13 → 0.59/week). October was already neutral (+₹30).
- V4 Bank — KEEP as candidate (Jan–Oct only, weak). Net flips −₹28,635 → +₹15,755 and
  win/FT rise, with 15 losers removed against 5 winners. Caveats, all material: the October
  slice of this same track was a Family C DISCARD (net fell ₹6,790 in October); ex-October
  O1 is still −₹45,145; full-target rate is only 34.6% and frequency 0.64/week. November
  paper must show it positive without an October-sized month before it is anything more
  than a candidate.
- Skill Nifty — DISCARD. The highest-frequency base (3.08/week) is also the one O1 hurts
  most in rupees after Skill Bank: net −₹17,110, win and FT both fall, 20 winners removed.
- Skill Bank — DISCARD (October keep does NOT survive). O1 removes 30 losers against 11
  winners and improves net by ₹90,420 — the largest rupee improvement in this run — yet
  the track ends at −₹67,330 because its CE leg (−₹166,635) is untouched by a PE-only filter.
  A filter that leaves the track deeply negative is not a keep, however large its delta.
- (lA) Nifty — DISCARD. The strongest base in the run is damaged by O1 on every leg
  (net −₹28,790, win 75.6% → 71.1%, FT 55.6% → 52.6%) and the filter removes 7 winners and
  0 losers. This confirms the October discard, now on 45 trades instead of 3.
- (lA) Bank — KEEP as candidate (Jan–Oct only). The cleanest O1 track in both windows:
  5 losers removed, 0 winners removed, net flips −₹21,320 → +₹29,055, win 38.5% → 44.1%,
  FT 28.2% → 32.4%. Caveats: frequency only 0.84/week, FT still far below 50%, and the
  flip is October-driven (ex-October O1 −₹6,695). November paper decides; nothing adopted.
- V5 Nifty — DISCARD. Net falls ₹10,355, win/FT flat at 50.0%, frequency 0.79 → 0.49/week.
  The capped pool's Nifty leg does not want this filter.
- V5 Bank — DISCARD. The Jan–Oct net gain (+₹9,730) and win/FT gain (+1.4pp) are marginal
  against a halved frequency (0.99 → 0.54/week), the October slice discards it too
  (net fell ₹6,790 in October), and ex-October O1 is negative (−₹10,695).

## Caveats that travel with these numbers
1. All nets are spot provisional (points × 100 shares − ₹40), NOT options-lot profits and
   NOT futures profits. The October premium subset (above) already shows spot winners
   turning premium-negative (23 Oct Nifty), so no spot verdict here is a premium verdict.
2. O1 was born in October; Jan–Oct contains its birth month, so this is in-sample
   persistence, not validation. November paper from 2026-11-02, with the frozen definition,
   is the validation step for the two keeps ((lA) Bank, V4 Bank).
3. No missing-bar cases occurred: all 173 filtered trades failed on the confirmer-close
   test itself (reason confirmer_NOT_below_ORlow_both_bars in the CSV), none on missing data.
4. The (lA) base correction above means earlier (lA) Jan–Oct figures derived from the
   merged JSONs (66 candidates) are superseded for (lA) v2 by the L1 figures here (84 trades).
5. Frequency everywhere is below the 5/week target after O1; O1 is a selectivity filter,
   and selectivity cannot create the missing trading days.

## Filtered-out trades (all 173, with outcome)
Every PE trade removed by O1, per track. CE trades are never in this list (kept unchanged).
Full rows including confirmer closes are in the CSV.
### V4 NIFTY — 22 filtered out
- 2026-01-08 PE setup2_or_breakdown sig 09:30 stop -965 (loser)
- 2026-02-06 PE setup2_or_breakdown sig 09:35 stop -2275 (loser)
- 2026-02-12 PE setup2_or_breakdown sig 11:25 target +800 (winner)
- 2026-02-13 PE setup2_or_breakdown sig 09:30 stop -3750 (loser)
- 2026-02-24 PE setup2_or_breakdown sig 09:30 target +7350 (winner)
- 2026-04-30 PE setup2_or_breakdown sig 10:00 stop -3165 (loser)
- 2026-05-05 PE setup2_or_breakdown sig 10:30 target +5040 (winner)
- 2026-05-12 PE setup2_or_breakdown sig 09:35 stop -2320 (loser)
- 2026-05-18 PE setup2_or_breakdown sig 09:35 stop -3670 (loser)
- 2026-06-29 PE setup2_or_breakdown sig 09:30 stop -4740 (loser)
- 2026-06-30 PE setup2_or_breakdown sig 09:30 stop -2720 (loser)
- 2026-07-24 PE setup2_or_breakdown sig 09:55 target +3500 (winner)
- 2026-08-12 PE setup2_or_breakdown sig 09:55 target +6250 (winner)
- 2026-08-17 PE setup2_or_breakdown sig 10:10 target +2240 (winner)
- 2026-08-25 PE setup2_or_breakdown sig 10:20 stop -1475 (loser)
- 2026-08-27 PE setup2_or_breakdown sig 09:55 target +3000 (winner)
- 2026-09-07 PE setup2_or_breakdown sig 09:50 target +2990 (winner)
- 2026-09-08 PE setup2_or_breakdown sig 09:55 stop -1305 (loser)
- 2026-09-09 PE setup2_or_breakdown sig 10:05 stop -405 (loser)
- 2026-09-10 PE setup2_or_breakdown sig 10:10 stop -225 (loser)
- 2026-10-08 PE setup2_or_breakdown sig 09:40 target +5440 (winner)
- 2026-10-28 PE setup2_or_breakdown sig 10:15 stop -5470 (loser)

### V4 BANKNIFTY — 20 filtered out
- 2026-01-21 PE setup2_or_breakdown sig 09:55 target +20150 (winner)
- 2026-02-02 PE setup3_bounce_rejection sig 09:40 stop -10655 (loser)
- 2026-03-06 PE setup2_or_breakdown sig 10:00 target +13930 (winner)
- 2026-04-01 PE setup3_bounce_rejection sig 09:30 stop -23515 (loser)
- 2026-04-10 PE setup3_bounce_rejection sig 09:30 stop -9405 (loser)
- 2026-04-28 PE setup2_or_breakdown sig 11:20 target +15400 (winner)
- 2026-05-27 PE setup2_or_breakdown sig 09:55 stop -4395 (loser)
- 2026-05-29 PE setup3_bounce_rejection sig 10:25 target +15660 (winner)
- 2026-06-09 PE setup3_bounce_rejection sig 09:40 stop -3915 (loser)
- 2026-06-16 PE setup2_or_breakdown sig 10:05 stop -6075 (loser)
- 2026-06-24 PE setup3_bounce_rejection sig 09:30 stop -8625 (loser)
- 2026-06-29 PE setup2_or_breakdown sig 09:30 stop -15645 (loser)
- 2026-07-15 PE setup3_bounce_rejection sig 09:40 stop -4560 (loser)
- 2026-07-24 PE setup2_or_breakdown sig 09:45 stop -6360 (loser)
- 2026-07-28 PE setup2_or_breakdown sig 09:40 stop -4950 (loser)
- 2026-07-30 PE setup2_or_breakdown sig 09:35 stop -7825 (loser)
- 2026-08-11 PE setup2_or_breakdown sig 09:30 stop -5010 (loser)
- 2026-08-14 PE setup2_or_breakdown sig 10:30 stop -5385 (loser)
- 2026-10-13 PE setup3_bounce_rejection sig 10:35 stop -3730 (loser)
- 2026-10-26 PE setup3_bounce_rejection sig 10:15 target +10520 (winner)

### Skill v2 NIFTY — 48 filtered out
- 2026-01-01 PE or_breakdown sig 10:15 stop -2085 (loser)
- 2026-01-08 PE or_breakdown sig 09:30 stop -965 (loser)
- 2026-01-29 PE or_breakdown sig 09:35 stop -5360 (loser)
- 2026-02-06 PE or_breakdown sig 09:35 stop -2275 (loser)
- 2026-02-09 PE or_breakdown sig 09:35 stop -2560 (loser)
- 2026-02-12 PE or_breakdown sig 11:25 target +800 (winner)
- 2026-02-13 PE or_breakdown sig 09:30 stop -3750 (loser)
- 2026-02-18 PE or_breakdown sig 09:55 stop -3580 (loser)
- 2026-02-24 PE or_breakdown sig 09:30 target +7350 (winner)
- 2026-03-05 PE or_breakdown sig 09:35 stop -3695 (loser)
- 2026-03-11 PE or_breakdown sig 09:35 target +7160 (winner)
- 2026-03-24 PE or_breakdown sig 09:40 target +7120 (winner)
- 2026-04-02 PE or_breakdown sig 09:55 stop -2115 (loser)
- 2026-04-06 PE or_breakdown sig 09:45 stop -4565 (loser)
- 2026-04-15 PE or_breakdown sig 09:35 stop -2920 (loser)
- 2026-04-16 PE or_breakdown sig 09:35 target +7520 (winner)
- 2026-04-22 PE or_breakdown sig 09:40 target +3170 (winner)
- 2026-04-30 PE or_breakdown sig 10:00 stop -3165 (loser)
- 2026-05-05 PE or_breakdown sig 10:30 target +5040 (winner)
- 2026-05-06 PE or_breakdown sig 09:35 target +2470 (winner)
- 2026-05-12 PE or_breakdown sig 09:35 stop -2320 (loser)
- 2026-05-14 PE or_breakdown sig 09:40 stop -2770 (loser)
- 2026-05-18 PE or_breakdown sig 09:35 stop -3670 (loser)
- 2026-05-29 PE or_breakdown sig 09:40 stop -5760 (loser)
- 2026-06-01 PE or_breakdown sig 09:40 target +9650 (winner)
- 2026-06-05 PE or_breakdown sig 10:30 target +8410 (winner)
- 2026-06-09 PE or_breakdown sig 09:45 target +6640 (winner)
- 2026-06-12 PE or_breakdown sig 09:35 target +2710 (winner)
- 2026-06-29 PE or_breakdown sig 09:30 stop -4740 (loser)
- 2026-06-30 PE or_breakdown sig 09:30 stop -2720 (loser)
- 2026-07-21 PE or_breakdown sig 10:20 target +2840 (winner)
- 2026-07-24 PE or_breakdown sig 09:55 target +3500 (winner)
- 2026-08-04 PE or_breakdown sig 10:30 stop -1040 (loser)
- 2026-08-12 PE or_breakdown sig 09:55 target +6250 (winner)
- 2026-08-17 PE or_breakdown sig 10:10 target +2240 (winner)
- 2026-08-25 PE or_breakdown sig 10:20 stop -1475 (loser)
- 2026-08-27 PE or_breakdown sig 09:55 target +3000 (winner)
- 2026-08-31 PE or_breakdown sig 09:40 stop -2425 (loser)
- 2026-09-01 PE or_breakdown sig 09:45 stop -920 (loser)
- 2026-09-03 PE or_breakdown sig 11:00 target +2420 (winner)
- 2026-09-07 PE or_breakdown sig 09:50 target +2990 (winner)
- 2026-09-08 PE or_breakdown sig 09:55 stop -1305 (loser)
- 2026-09-09 PE or_breakdown sig 10:05 stop -405 (loser)
- 2026-09-10 PE or_breakdown sig 10:10 stop -225 (loser)
- 2026-10-07 PE or_breakdown sig 09:35 stop -2725 (loser)
- 2026-10-08 PE or_breakdown sig 09:40 target +5440 (winner)
- 2026-10-12 PE or_breakdown sig 09:50 stop -4605 (loser)
- 2026-10-28 PE or_breakdown sig 10:15 stop -5470 (loser)

### Skill v2 BANKNIFTY — 41 filtered out
- 2026-01-07 PE or_breakdown sig 09:50 stop -5080 (loser)
- 2026-01-19 PE or_breakdown sig 09:40 stop -4715 (loser)
- 2026-01-21 PE or_breakdown sig 09:55 target +20150 (winner)
- 2026-01-23 PE or_breakdown sig 09:40 stop -10485 (loser)
- 2026-01-28 PE or_breakdown sig 10:05 stop -12150 (loser)
- 2026-02-02 PE or_breakdown sig 11:05 stop -7915 (loser)
- 2026-02-03 PE or_breakdown sig 09:40 stop -16805 (loser)
- 2026-02-05 PE or_breakdown sig 09:35 stop -5680 (loser)
- 2026-02-25 PE or_breakdown sig 10:45 target +16660 (winner)
- 2026-02-26 PE or_breakdown sig 10:35 stop -3620 (loser)
- 2026-02-27 PE or_breakdown sig 09:40 target +14830 (winner)
- 2026-03-06 PE or_breakdown sig 10:00 target +13930 (winner)
- 2026-03-18 PE or_breakdown sig 10:00 stop -9550 (loser)
- 2026-03-23 PE or_breakdown sig 09:45 target +25440 (winner)
- 2026-03-30 PE or_breakdown sig 10:50 stop -10520 (loser)
- 2026-04-01 PE or_breakdown sig 10:20 stop -18035 (loser)
- 2026-04-02 PE or_breakdown sig 10:45 stop -10115 (loser)
- 2026-04-09 PE or_breakdown sig 09:45 stop -17400 (loser)
- 2026-04-15 PE or_breakdown sig 09:35 stop -9320 (loser)
- 2026-04-27 PE or_breakdown sig 10:25 target +9990 (winner)
- 2026-05-27 PE or_breakdown sig 09:55 stop -4395 (loser)
- 2026-06-16 PE or_breakdown sig 09:40 stop -5480 (loser)
- 2026-06-22 PE or_breakdown sig 09:35 stop -5955 (loser)
- 2026-06-29 PE or_breakdown sig 09:30 stop -15645 (loser)
- 2026-07-03 PE or_breakdown sig 11:10 stop -3945 (loser)
- 2026-07-14 PE or_breakdown sig 09:35 target +23410 (winner)
- 2026-07-16 PE or_breakdown sig 10:25 stop -3830 (loser)
- 2026-07-20 PE or_breakdown sig 09:35 stop -10455 (loser)
- 2026-07-24 PE or_breakdown sig 09:45 stop -6360 (loser)
- 2026-07-27 PE or_breakdown sig 09:55 target +3820 (winner)
- 2026-07-28 PE or_breakdown sig 09:40 stop -4950 (loser)
- 2026-07-30 PE or_breakdown sig 09:35 stop -7825 (loser)
- 2026-07-31 PE or_breakdown sig 09:35 stop -7295 (loser)
- 2026-08-07 PE or_breakdown sig 11:00 stop -6680 (loser)
- 2026-08-11 PE or_breakdown sig 09:30 stop -5010 (loser)
- 2026-08-18 PE or_breakdown sig 10:00 stop -2210 (loser)
- 2026-08-24 PE or_breakdown sig 09:35 target +3470 (winner)
- 2026-09-18 PE or_breakdown sig 10:35 target +5060 (winner)
- 2026-09-24 PE or_breakdown sig 09:35 target +16360 (winner)
- 2026-10-07 PE or_breakdown sig 09:35 stop -7475 (loser)
- 2026-10-12 PE or_breakdown sig 09:50 stop -4640 (loser)

### (lA) v2 NIFTY — 7 filtered out
- 2026-01-07 PE la_pe_rescan_reentry sig 12:15 target +2360 (winner)
- 2026-02-06 PE la_pe_rescan_reentry sig 10:10 day_green +1120 (winner)
- 2026-05-05 PE la_pe_rescan_reentry sig 10:30 target +5040 (winner)
- 2026-06-29 PE la_pe_rescan_reentry sig 09:30 day_green +2100 (winner)
- 2026-07-24 PE la_pe_rescan_reentry sig 09:55 target +3500 (winner)
- 2026-08-27 PE la_pe_rescan_reentry sig 10:40 target +2980 (winner)
- 2026-10-08 PE la_pe_rescan_reentry sig 11:25 target +11690 (winner)

### (lA) v2 BANKNIFTY — 5 filtered out
- 2026-03-06 PE la_pe_rescan_reentry sig 10:45 day_loss -1375 (loser)
- 2026-06-29 PE la_pe_rescan_reentry sig 09:30 day_loss -24935 (loser)
- 2026-06-30 PE la_pe_rescan_reentry sig 13:20 day_loss -560 (loser)
- 2026-07-14 PE la_pe_rescan_reentry sig 10:15 day_loss -16030 (loser)
- 2026-10-07 PE la_pe_rescan_reentry sig 09:35 day_loss -7475 (loser)

### V5-v2 NIFTY — 12 filtered out
- 2026-02-06 PE setup2_or_breakdown sig 09:35 stop -2275 (loser)
- 2026-02-13 PE setup2_or_breakdown sig 09:30 stop -3750 (loser)
- 2026-02-24 PE setup2_or_breakdown sig 09:30 target +7350 (winner)
- 2026-04-02 PE or_breakdown sig 09:55 stop -2115 (loser)
- 2026-04-30 PE setup2_or_breakdown sig 10:00 stop -3165 (loser)
- 2026-05-05 PE setup2_or_breakdown sig 10:30 target +5040 (winner)
- 2026-05-18 PE setup2_or_breakdown sig 09:35 stop -3670 (loser)
- 2026-06-29 PE setup2_or_breakdown sig 09:30 stop -4740 (loser)
- 2026-08-12 PE setup2_or_breakdown sig 09:55 target +6250 (winner)
- 2026-08-27 PE setup2_or_breakdown sig 09:55 target +3000 (winner)
- 2026-09-07 PE setup2_or_breakdown sig 09:50 target +2990 (winner)
- 2026-10-08 PE setup2_or_breakdown sig 09:40 target +5440 (winner)

### V5-v2 BANKNIFTY — 18 filtered out
- 2026-01-21 PE setup2_or_breakdown sig 09:55 target +20150 (winner)
- 2026-02-02 PE setup3_bounce_rejection sig 09:40 stop -10655 (loser)
- 2026-03-06 PE setup2_or_breakdown sig 10:00 target +13930 (winner)
- 2026-03-23 PE or_breakdown sig 09:45 target +25440 (winner)
- 2026-03-30 PE or_breakdown sig 10:50 stop -10520 (loser)
- 2026-04-01 PE setup3_bounce_rejection sig 09:30 stop -23515 (loser)
- 2026-04-10 PE setup3_bounce_rejection sig 09:30 stop -9405 (loser)
- 2026-04-28 PE setup2_or_breakdown sig 11:20 target +15400 (winner)
- 2026-05-29 PE setup3_bounce_rejection sig 10:25 target +15660 (winner)
- 2026-06-09 PE setup3_bounce_rejection sig 09:40 stop -3915 (loser)
- 2026-06-16 PE setup2_or_breakdown sig 10:05 stop -6075 (loser)
- 2026-06-24 PE setup3_bounce_rejection sig 09:30 stop -8625 (loser)
- 2026-06-29 PE setup2_or_breakdown sig 09:30 stop -15645 (loser)
- 2026-07-15 PE setup3_bounce_rejection sig 09:40 stop -4560 (loser)
- 2026-07-24 PE setup2_or_breakdown sig 09:45 stop -6360 (loser)
- 2026-07-30 PE setup2_or_breakdown sig 09:35 stop -7825 (loser)
- 2026-10-13 PE setup3_bounce_rejection sig 10:35 stop -3730 (loser)
- 2026-10-26 PE setup3_bounce_rejection sig 10:15 target +10520 (winner)

