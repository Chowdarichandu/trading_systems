# Index OPTIONS — Skill-only tuning, 2026-10-30

Paper only, no orders, no stocks, no other systems. Skill v2 (S1) ONLY.
Window: October 2026, 1–28 Oct, 18 trading days. Nifty and Bank separately,
never pooled. Pass bar (all three together, per index): premium net per
1 lot > 0 AND premium full-target >= 50% AND frequency >= 5/week
(legs / 18 * 5). Nothing adopted on October/in-sample alone; November paper
from Mon 2026-11-02 remains validation.

Frozen definitions (written before scoring; V11 added after V1/V2 scored
identical to base, before V11 was scored — see the 09:30-PE section):
[index_options_skill_tuned_oct30_frozen.md](sandbox://workspace/trading/index_options_skill_tuned_oct30_frozen.md)
Script: [skill_tune_oct30.py](sandbox://workspace/trading/skill_tune_oct30.py)
Fetch script: [skill_tune_fetch_missing.py](sandbox://workspace/trading/skill_tune_fetch_missing.py)
Full 228-leg trade list:
[index_options_skill_tuned_oct30_trades.csv](sandbox://workspace/trading/index_options_skill_tuned_oct30_trades.csv)

## Method — read before the numbers

- Base S1 recomputed from the spot cache and verified EXACT before variants:
  Nifty 8 legs / spot +₹8,420, Bank 9 legs / spot +₹8,675 — identical to the
  v2 CSV on both tracks. Every variant below is one change at a time vs
  that base; nothing is blended and no October-fitted filters are stacked.
- Premium rule (the October premium-completion overlay, applied uniformly):
  strike = ATM nearest 100 to entry spot; expiry monthly 2026-10-27 for
  1–27 Oct, weekly 2026-11-03 for 28 Oct; entry premium = open of the first
  5-min option candle after the spot signal time; stop = entry − 50 option
  points, target = entry + 90 option points, both CE and PE; stop before
  target per bar including the entry bar; square-off 15:10 close; net per
  1 lot = (exit − entry) × lot − ₹220 assumed cost; lot Nifty 65 / Bank 30.
  By construction a premium target is +₹5,630 (Nifty) / +₹2,480 (Bank) and
  a premium stop is −₹3,470 (Nifty) / −₹1,720 (Bank). Premium full-target =
  premium target exit only; a square-off green is NOT a full target.
- Premium completeness: 227 of 228 variant legs are COMPUTED. The single
  NOT_COMPUTED leg is V3 Bank 28 Oct CE (strike 54000, Nov-03 expiry):
  the Bank Nov-03 option chain returns 0 strikes via the API (status 200),
  the same Bank post-October chain gap noted in the premium completion —
  so that leg cannot be premium-scored and is never spot-converted.
  21 missing contract-days were fetched for this run via the Upstox API
  through the existing localhost forwarder (plain API GETs, profile check
  200 first, every fetch 200 with 77 candles); the cached premium files are
  under `~/workspace/trading/v4_options_oct_data/candles_premium_*.json`.
- Spot nets are shown alongside premiums for every variant, but the pass
  bar is judged on PREMIUMS. Spot provisional = points × 100 shares −
  ₹40/leg, NOT an options-lot profit.

## Base (Skill v2, S1) — October premiums, for reference

| Track | Legs | Premium net / 1 lot | Full-target | Frequency |
|---|---|---|---|---|
| Nifty | 8 | +₹3,394.50 | 2/8 = 25.0% | 2.22/week |
| Bank | 9 | −₹2,880.00 | 3/9 = 33.3% | 2.50/week |

Base fails all three legs jointly on both indices; Bank is premium-negative
(the key failure this run was asked to fix) despite a positive spot net
(+₹8,675). Frequency without premium edge is worthless — that is the base.

## October premium table — all variants, per index separately

Frequency = legs / 18 × 5. "Legs passed" counts net > 0, FT ≥ 50%,
frequency ≥ 5/week. NC = NOT_COMPUTED legs (excluded from premium net/FT).

| Variant | Track | Legs (NC) | Premium net / 1 lot | Full-target | /week | Legs passed | Failing legs |
|---|---|---|---|---|---|---|---|
| BASE S1 | Nifty | 8 (0) | +₹3,394.50 | 25.0% | 2.22 | net only | FT, freq |
| BASE S1 | Bank | 9 (0) | −₹2,880.00 | 33.3% | 2.50 | none | net, FT, freq |
| V1 P-LOW | Nifty | 8 (0) | +₹3,394.50 | 25.0% | 2.22 | net only | FT, freq |
| V1 P-LOW | Bank | 9 (0) | −₹2,880.00 | 33.3% | 2.50 | none | net, FT, freq |
| V2 P-2ND | Nifty | 8 (0) | +₹3,394.50 | 25.0% | 2.22 | net only | FT, freq |
| V2 P-2ND | Bank | 9 (0) | −₹2,880.00 | 33.3% | 2.50 | none | net, FT, freq |
| V3 CE-NOBLOCK | Nifty | 14 (0) | +₹9,874.50 | 35.7% | 3.89 | net only | FT, freq |
| V3 CE-NOBLOCK | Bank | 15 (1) | +₹1,120.00 computed | 42.9% (6/14) | 4.17 | net only* | FT, freq |
| V4 BIAS-WIDE | Nifty | 10 (0) | +₹5,554.50 | 30.0% | 2.78 | net only | FT, freq |
| V4 BIAS-WIDE | Bank | 12 (0) | −₹3,840.00 | 33.3% | 3.33 | none | net, FT, freq |
| V5 OR30 | Nifty | 10 (0) | +₹8,239.00 | 30.0% | 2.78 | net only | FT, freq |
| V5 OR30 | Bank | 6 (0) | +₹2,280.00 | 50.0% (3/6) | 1.67 | net, FT | freq |
| V6 OR20 | Nifty | 9 (0) | +₹9,024.50 | 33.3% | 2.50 | net only | FT, freq |
| V6 OR20 | Bank | 10 (0) | −₹4,600.00 | 30.0% | 2.78 | none | net, FT, freq |
| V7 R1-PREM | Nifty | 10 (0) | +₹5,554.50 | 30.0% | 2.78 | net only | FT, freq |
| V7 R1-PREM | Bank | 12 (0) | +₹360.00 | 41.7% | 3.33 | net only | FT, freq |
| V8 R-REV | Nifty | 11 (0) | −₹463.50 | 18.2% | 3.06 | none | net, FT, freq |
| V8 R-REV | Bank | 11 (0) | −₹2,120.00 | 36.4% | 3.06 | none | net, FT, freq |
| V9 C3-PREM | Nifty | 5 (0) | +₹14,695.00 | 60.0% (3/5) | 1.39 | net, FT | freq |
| V9 C3-PREM | Bank | 7 (0) | +₹4,760.00 | 57.1% (4/7) | 1.94 | net, FT | freq |
| V10 PB-FALLBACK | Nifty | 8 (0) | +₹4,285.00 | 37.5% | 2.22 | net only | FT, freq |
| V10 PB-FALLBACK | Bank | 9 (0) | +₹1,320.00 | 44.4% | 2.50 | net only | FT, freq |
| V11 P-RESCAN | Nifty | 9 (0) | +₹2,059.75 | 22.2% | 2.50 | net only | FT, freq |
| V11 P-RESCAN | Bank | 9 (0) | −₹2,880.00 | 33.3% | 2.50 | none | net, FT, freq |

\* V3 Bank "net only" is on computed legs only (14/15); the NC leg is a
spot stop (−₹13,655), so the computed +₹1,120 would fall to −₹600 if that
leg were a premium stop, and FT could reach at most 7/15 = 46.7% even if
it were a target — V3 Bank cannot pass FT on any outcome of the NC leg.

## Before / after per track (spot provisional → premium, base → variant)

Spot FT = spot target exits / legs. Premium FT = premium target exits /
computed legs. Spot and premium FTs differ because the premium overlay
(−50/+90) is not the native spot rule (signal-bar stop, 2× target).

| Variant / track | Spot net (base → variant) | Spot FT | Premium net (base → variant) | Premium FT | Freq (base → variant) |
|---|---|---|---|---|---|
| V1, V2 / both | unchanged on both | unchanged | unchanged on both | unchanged | unchanged |
| V3 Nifty | +₹8,420 → +₹9,495 | 2/8 → 5/14 | +₹3,394.50 → +₹9,874.50 | 25.0% → 35.7% | 2.22 → 3.89 |
| V3 Bank | +₹8,675 → +₹72,065 | 3/9 → 7/15 | −₹2,880 → +₹1,120 computed | 33.3% → 42.9% | 2.50 → 4.17 |
| V4 Nifty | +₹8,420 → +₹5,130 | 2/8 → 3/10 | +₹3,394.50 → +₹5,554.50 | 25.0% → 30.0% | 2.22 → 2.78 |
| V4 Bank | +₹8,675 → +₹28,690 | 3/9 → 5/12 | −₹2,880 → −₹3,840 | 33.3% → 33.3% | 2.50 → 3.33 |
| V5 Nifty | +₹8,420 → −₹510 | 2/8 → 1/10 | +₹3,394.50 → +₹8,239.00 | 25.0% → 30.0% | 2.22 → 2.78 |
| V5 Bank | +₹8,675 → +₹1,185 | 3/9 → 2/6 | −₹2,880 → +₹2,280 | 33.3% → 50.0% | 2.50 → 1.67 |
| V6 Nifty | +₹8,420 → +₹8,060 | 2/8 → 2/9 | +₹3,394.50 → +₹9,024.50 | 25.0% → 33.3% | 2.22 → 2.50 |
| V6 Bank | +₹8,675 → −₹25,515 | 3/9 → 3/10 | −₹2,880 → −₹4,600 | 33.3% → 30.0% | 2.50 → 2.78 |
| V7 Nifty | +₹8,420 → +₹16,000 | 2/8 → 4/10 | +₹3,394.50 → +₹5,554.50 | 25.0% → 30.0% | 2.22 → 2.78 |
| V7 Bank | +₹8,675 → +₹31,320 | 3/9 → 5/12 | −₹2,880 → +₹360 | 33.3% → 41.7% | 2.50 → 3.33 |
| V8 Nifty | +₹8,420 → +₹20,455 | 2/8 → 4/11 | +₹3,394.50 → −₹463.50 | 25.0% → 18.2% | 2.22 → 3.06 |
| V8 Bank | +₹8,675 → +₹13,375 | 3/9 → 4/11 | −₹2,880 → −₹2,120 | 33.3% → 36.4% | 2.50 → 3.06 |
| V9 Nifty | +₹8,420 → +₹4,915 | 2/8 → 3/5 | +₹3,394.50 → +₹14,695 | 25.0% → 60.0% | 2.22 → 1.39 |
| V9 Bank | +₹8,675 → +₹21,460 | 3/9 → 4/7 | −₹2,880 → +₹4,760 | 33.3% → 57.1% | 2.50 → 1.94 |
| V10 Nifty | +₹8,420 → −₹2,820 | 2/8 → 3/8 | +₹3,394.50 → +₹4,285 | 25.0% → 37.5% | 2.22 → 2.22 |
| V10 Bank | +₹8,675 → +₹5,105 | 3/9 → 4/9 | −₹2,880 → +₹1,320 | 33.3% → 44.4% | 2.50 → 2.50 |
| V11 Nifty | +₹8,420 → +₹19,810 | 2/8 → 3/9 | +₹3,394.50 → +₹2,059.75 | 25.0% → 22.2% | 2.22 → 2.50 |
| V11 Bank | +₹8,675 → +₹8,675 | 3/9 → 3/9 | −₹2,880 → −₹2,880 | 33.3% → 33.3% | 2.50 → 2.50 |

## The 09:30-PE rule, re-examined properly (the pilot's 23 Oct case)

The three blocked 09:30 PE days in October are Nifty 16 Oct, Nifty 23 Oct
and Bank 16 Oct. On all three, the 09:30 bar's LOW is also above PDL, so
V1 (low-penetration) changes nothing — the bar never penetrated PDL at
all, intraday or on close. On 23 Oct Nifty the 09:35 close (₹22,686.90) is
also above PDL (₹22,554.85), so V2 (second-close) changes nothing either.
Both "quick fixes" fail for a definitional reason, not a data gap: the
09:30 breakdown was early and shallow, and price only closed below PDL
at the 10:05 bar (signal 10:05, entry spot ₹22,526.25).

V11 (PDL rescan, filter retained, timing relaxed to ≤ 11:30) is the fix
that actually fires: it takes exactly one extra trade — Nifty 23 Oct PE,
signal 10:05 — and correctly takes nothing on 16 Oct either index (price
never approaches PDL there). But on premiums that rescued trade is a
square-off LOSS of −₹1,334.75 (entry premium ₹125.85, exit ₹108.70 at
15:10; premium never reached the +90 target ₹215.85 nor the −50 stop
₹75.85), while on spot it is a target (+₹11,390). So V11 Nifty spot net
rises +₹8,420 → +₹19,810 and spot FT rises 2/8 → 3/9, but premium net
FALLS +₹3,394.50 → +₹2,059.75 and premium FT falls 25.0% → 22.2%. The
pilot's 23 Oct PE "target" was a spot target, not a premium target — the
known 23 Oct spot-target/premium-loss divergence, reproduced a third
time. V11 is therefore NOT a premium fix: it adds a premium loser. It is
kept in the record as the correct diagnosis of the rule (PDL timing, not
close-vs-low), not as a kept variant.

## Variant verdicts, one by one

- **V1 P-LOW — DISCARD (inert).** Identical to base on both tracks, spot
  and premium. The low condition never differs from the close condition
  on a blocked day in October.
- **V2 P-2ND — DISCARD (inert).** Identical to base on both tracks. The
  09:35 close is above PDL on every blocked day, so no second-close trade
  ever fires. Distinct from Family C C4, which required a second close on
  every signal; V2 applied it only to the blocked 09:30 PE case, and it
  still fires nowhere.
- **V3 CE-NOBLOCK — CLOSEST ON FREQUENCY, NOT WORKING.** Highest frequency
  of any variant (Nifty 3.89, Bank 4.17/week) and both premium nets
  positive (Nifty +₹9,874.50, Bank +₹1,120 computed), but FT fails on both
  (35.7%, 42.9%) and frequency still fails on both. The Bank spot net
  (+₹72,065) is a mirage on premiums: the two huge Bank spot targets
  (9 Oct +₹27,270, 22 Oct +₹29,760) compress to +₹2,480 each on premiums,
  while the 13 Oct spot target (+₹10,170) reverses to a premium stop
  (−₹1,720). Removing the CE block adds 6 Nifty and 6 Bank legs; 5 of the
  6 added Nifty legs are premium targets/stops exactly as their spot
  class except 1 Oct (spot stop → premium stop, same class) — the FT
  failure is a count failure (5/14), not a reversal story, on Nifty.
- **V4 BIAS-WIDE — DISCARD as a premium fix (spot keep does NOT survive
  premiums).** Family A's spot result (Bank +₹28,690, 3.33/week) reverses
  on Bank premiums to −₹3,840: the added Bank legs net −₹960 on premiums
  (13 Oct spot target → premium stop −₹1,720; 15 Oct spot target →
  premium target +₹2,480; 21 Oct spot stop → premium stop −₹1,720).
  Widened neutral buys frequency with spot targets that do not become
  premium targets. Nifty improves on premiums (+₹5,554.50) but still fails
  FT (30.0%) and frequency (2.78).
- **V5 OR30 — DISCARD as a system; Bank leg noted.** Nifty spot goes
  negative (−₹510) while its premium net rises (+₹8,239) — a
  spot/premium inversion driven by compression (e.g. 21 Oct PE spot stop
  −₹2,335 → premium target +₹5,630). Bank passes net + FT (50.0%, 3/6)
  but at 1.67/week, and its spot FT is only 2/6 — the premium FT pass is
  a 3-leg count on 6 legs, not a robust edge. OR30 also loses base trades
  (Bank 6 legs vs 9) — it is a different, smaller system, not a fix.
- **V6 OR20 — DISCARD.** Nifty premium net rises (+₹9,024.50) but FT fails
  (33.3%); Bank is a disaster on spot (−₹25,515) and still negative on
  premiums (−₹4,600, FT 30.0%). A 2-bar OR is too noisy for Bank.
- **V7 R1-PREM — BANK PREMIUM-NEGATIVE FIXED, BUT NOT WORKING.** This is
  the only re-entry result that moves Bank from negative to positive on
  premiums: re-entry legs net +₹3,240 on Bank (6 Oct spot stop → premium
  stop −₹1,720, worsening; 8 Oct and 12 Oct spot targets → premium
  targets +₹2,480 each), taking Bank −₹2,880 → +₹360. But +₹360 is barely
  positive, FT is 41.7% (fails), frequency is 3.33/week (fails). Nifty
  re-entries net +₹2,160 on premiums, but one of them reverses (5 Oct
  spot target → premium stop −₹3,470) while 12 Oct converts
  (spot target → premium target +₹5,630). R1 on premiums confirms the
  Family C spot keep for Bank only in the weak sense: it fixes the sign,
  not the system.
- **V8 R-REV — DISCARD (sharpest spot→premium reversal in this run).**
  Spot gains on both tracks (Nifty +₹20,455, Bank +₹13,375) become premium
  losses on both (−₹463.50, −₹2,120). Reversal re-entries after a stop do
  not survive the premium overlay. Do not carry forward.
- **V9 C3-PREM — PASSES NET + FT ON BOTH INDICES, FAILS FREQUENCY ONLY.**
  Nifty 5 legs, +₹14,695, FT 60.0%; Bank 7 legs, +₹4,760, FT 57.1%. This is
  the hit-quality variant: pullback entry converts the base's premium
  profile (e.g. Nifty 8 Oct spot stop −₹1,780 → premium target +₹5,630;
  Bank 8 Oct pullback 12:20 = the same leg as the V7 re-entry). But it
  trades only 1.39 / 1.94 per week — it needs 13 more Nifty legs and 11
  more Bank legs in 18 days at the same quality to reach 5/week. It is
  the closest track by legs passed (2 of 3 on both indices), not the
  closest family on frequency.
- **V10 PB-FALLBACK — DISCARD.** Both premium nets positive (Nifty
  +₹4,285, Bank +₹1,320) but FT fails on both (37.5%, 44.4%) and frequency
  is unchanged from base (2.22 / 2.50). The fallback preserves the base
  trade count and mostly preserves its FT failure; Nifty spot even goes
  negative (−₹2,820) while premiums stay positive — another compression
  artefact, not an edge.
- **V11 P-RESCAN — DISCARD as a premium variant (diagnosis kept).** See
  the 09:30-PE section above. Spot fix, premium loser.

## Verdict — NO variant passes October on premiums

**No Skill variant meets net > 0 AND full-target ≥ 50% AND frequency
≥ 5/week on October premiums, on either index.** Closest overall family:
V3 CE-NOBLOCK (highest frequency, both nets positive, FT failing on
both). Closest tracks by legs passed: V9 on both indices and V5 on Bank
(net + FT pass, frequency fail only). The Bank premium-negative failure
is fixed in sign by V7 (+₹360), V3 (+₹1,120 computed), V5 (+₹2,280),
V9 (+₹4,760) and V10 (+₹1,320) — but none of those fixes also reaches
50% FT and 5/week, so none is "working" under the pass bar. In
particular, the Family A widened-neutral candidate (V4) does NOT fix
Bank on premiums (−₹3,840): its October spot gain does not survive the
premium overlay, and it must not be quoted as a Bank fix anymore.

## Jan–Oct check

**Not run, by the task's own condition.** Jan–Oct scoring (spot first,
premiums where already fetched) was ordered only for a variant that
passes October on premiums. No variant passes October, so no Jan–Oct
score is claimed for any variant in this run, and no variant is carried
to Jan–Oct as a passer. V3, V9 and V5-Bank are October-closest only;
they are not January–October results and must not be presented as such.
If the parent wants a Jan–Oct diagnostic on the closest variants
despite the non-pass, that is a new instruction, not a completion of
this one.

## Trade lists (decision-relevant variants; full list in the CSV)

Premium net per 1 lot; "prem" exit is the −50/+90 overlay exit.

### V3 CE-NOBLOCK — added legs vs base (base legs are the BASE rows)

Nifty added: 1 Oct CE sig 10:00, 22600, spot stop −₹3,230, prem stop
−₹3,470; 9 Oct CE sig 09:30, 22400, spot target +₹6,260, prem target
+₹5,630; 13 Oct CE sig 09:30, 22500, spot target +₹6,190, prem target
+₹5,630; 15 Oct CE sig 09:30, 22800, spot target +₹3,640, prem target
+₹5,630; 21 Oct CE sig 09:30, 23100, spot stop −₹4,855, prem stop
−₹3,470; 22 Oct CE sig 10:20, 22700, spot stop −₹6,930, prem stop
−₹3,470. Added premium net +₹6,480.
Bank added: 9 Oct CE sig 09:30, 55100, spot target +₹27,270, prem target
+₹2,480; 13 Oct CE sig 09:35, 55200, spot target +₹10,170, prem stop
−₹1,720; 15 Oct CE sig 09:50, 55600, spot target +₹17,370, prem target
+₹2,480; 21 Oct CE sig 09:30, 55800, spot stop −₹7,525, prem stop
−₹1,720; 22 Oct CE sig 10:10, 54800, spot target +₹29,760, prem target
+₹2,480; 28 Oct CE sig 09:45, 54000, spot stop −₹13,655, prem
NOT_COMPUTED (Bank Nov-03 chain gap). Added computed premium net +₹4,000.

### V9 C3-PREM — all legs (pullback entries replace direct entries)

Nifty: 6 Oct CE pullback sig 09:50, 22600, spot stop −₹1,945, prem
square-off +₹1,275; 8 Oct PE pullback sig 09:50, 22500, spot stop
−₹1,780, prem target +₹5,630; 12 Oct PE pullback sig 10:00, 22500, spot
target +₹5,090, prem target +₹5,630; 26 Oct CE pullback sig 11:30,
22500, spot target +₹2,730, prem target +₹5,630; 28 Oct PE pullback sig
10:35, 22600, spot target +₹820, prem stop −₹3,470. Net +₹14,695, FT 3/5.
Bank: 1 Oct CE pullback sig 10:20, 54900, spot target +₹7,420, prem
target +₹2,480; 5 Oct PE pullback sig 10:55, 54700, spot target +₹6,040,
prem target +₹2,480; 6 Oct CE pullback sig 09:45, 55000, spot stop
−₹2,930, prem stop −₹1,720; 8 Oct PE pullback sig 12:20, 54800, spot
target +₹12,670, prem target +₹2,480; 12 Oct PE pullback sig 10:25,
55000, spot target +₹13,020, prem target +₹2,480; 14 Oct CE pullback
sig 09:40, 55600, spot stop −₹12,205, prem stop −₹1,720; 27 Oct CE
pullback sig 10:15, 54500, spot stop −₹2,555, prem stop −₹1,720.
Net +₹4,760, FT 4/7.

### V7 R1-PREM — re-entry legs only (morning legs = BASE rows)

Nifty: 5 Oct CE re-entry sig 09:40, 22600, spot target +₹2,490, prem
stop −₹3,470; 12 Oct PE re-entry sig 10:00, 22500, spot target +₹5,090,
prem target +₹5,630. Re-entry premium net +₹2,160.
Bank: 6 Oct CE re-entry sig 10:30, 55000, spot stop −₹3,045, prem stop
−₹1,720; 8 Oct PE re-entry sig 12:20, 54800, spot target +₹12,670, prem
target +₹2,480; 12 Oct PE re-entry sig 10:25, 55000, spot target
+₹13,020, prem target +₹2,480. Re-entry premium net +₹3,240.

### V11 P-RESCAN — the single added leg

Nifty 23 Oct PE rescan sig 10:05, 22500, spot target +₹11,390, prem
square-off −₹1,334.75 (entry premium ₹125.85, exit ₹108.70 at 15:10).
Bank: no added leg (16 Oct never closes below PDL).

## Caveats that travel with every number above

1. Early-October trades are scored on the long-dated monthly 27 Oct
   contract, not a weekly — a weekly trader's premiums would differ.
2. The −50/+90 premium overlay is the V4/V5-v2 options rule, not Skill's
   native spot rule; Skill premium rows are "the overlay outcome of
   Skill's spot signals", and the compression (+₹5,630/−₹3,470 Nifty,
   +₹2,480/−₹1,720 Bank per leg) is why spot nets like V3 Bank +₹72,065
   collapse to +₹1,120 on premiums.
3. October is 18 days; every variant difference above is 1–6 legs wide.
   Nothing here is adopted, and no variant is combined with another —
   stacking V3 + V9, or V7 + V3, on October would be October-fitting, and
   was not scored.
4. One leg remains NOT_COMPUTED (V3 Bank 28 Oct, Bank Nov-03 chain gap);
   it is the only premium gap in this run.
