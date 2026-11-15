# Bank Nifty Engine — ROUND 5 (2026-11-02)

Basis: premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE, Jan–Oct 2026,
paper only, real money ₹0. Starting book: v19 = +₹133,898.00 recorded
(106 legs, FT90 53.8%), gap ₹16,102 to the ₹1,50,000 floor pace.
17 gated cycles (115–116, 118–129, 133–135). **The floor is NOT met.**
Ending book: **v20 = +₹78,250.50 → ₹7,825.05/month; remaining gap ₹71,749.50.**

## WS0 — ADMISSION-CAUSALITY AUDIT OF v19 (Cycle 115) — VIOLATIONS FOUND

Every leg of `bank_engine_r4_v19_trades.csv` was certified against its own
source system's signal time (evidence: `bank_r5_ws0_audit.json`). Bank has no
≥2-system confirmation rule, but the audit found two other violation classes
affecting **39 legs carrying +₹68,469 of the recorded +₹133,898**:

| Class | Legs | Recorded net | Finding |
|---|---|---|---|
| V-SK — EOD-solo Skill rule | 9 BASE legs | +₹25,320 | Kept Skill-V3 representatives entering ≤09:55 survived the B2 solo drop only because a second system confirmed the key LATER the same day (confirmations 09:55–13:25, after entry). Causally solo-at-entry; dropped in the rebuild, keys fall back to the next system leg or vanish. Legs: 02-27 PE +2,480 · 03-11 PE +5,180 · 04-16 PE −1,720 · 05-14 PE +5,180 · 06-16 PE −1,720 · 06-30 PE −1,720 · 07-14 PE −1,720 · 08-24 PE +9,680 · 10-23 PE +9,680 |
| V-NS — NS-family entry-time fields | 30 legs (13 NS1 + 17 NS3) | +₹43,149 | The source CSVs' `entry_time` is the spot trade's EXIT-bar time on stop/target exits (`newsetups_score.replay` returns it as such), not the entry. True entries are signal+5 min. NS1: only 2026-01-20 (+₹7,463) and 2026-07-28 (−₹1,720) of 15 legs are causal as recorded. NS3: all 17 legs affected. Strikes verified unchanged under re-timing (CSV entry_spot = spot open at signal+5 on every leg) |
| Certified CAUSAL | 58 BASE legs (+₹54,926) + 2 NS1 legs + all 7 S3 legs | — | (lA)/V5/Volrix representatives enter strictly after their own signal bars; S3 legs are signal+5 by construction; NS1 preconditions (S1 target/stop exit ≤13:30, exit before the crossing bar) verified leg by leg; bias is prior-day; DTE from the calendar |
| Machinery certificates | — | — | The B1→B2 drop rule was re-derived and verified EXACTLY (110 pooled → 89; 21 drops itemised: 8 Skill-CE block, 4 later-confirmed early Skill, 9 true-solo early Skill); the state pipeline (score_all stream → trailing states → cold-(lA) taken set) reproduces the frozen 82/82 |
| Calibration note (not a violation) | 1 Volrix leg (2026-06-01, −₹1,720) | — | Its trigger-day return on stored daily data is −0.924% vs the frozen −1.0% threshold (2026-05-28 is absent from both spot sources). Admission input (prior-day close) is causal; recorded as a generator-vintage calibration discrepancy, the same class Nifty Round 4 disclosed for its Volrix cell |

**Causal rebuild (REF_AUD, the reference for all Round-5 gating):**
102 legs, **+₹69,940.50**, FT90 48.0% (49/102), 2.51/week, no red month-ends,
halves +₹58,268.00 / +₹11,672.50, placebo −₹7,223.50 (beaten), ex-top-3
+₹40,900.50, NOT_COMPUTED 0, timing audit clean, independent re-sum exact.
Months: Jan +22,748 · Feb +20,480 · Mar +3,600 · Apr −1,810 · May +13,250 ·
Jun −3,640 · Jul −10,500 · Aug −873.50 · Sep +9,726.50 · Oct +16,959.50.
Families: BASE 64 +₹47,156 · NS1 16 +₹10,269.50 · NS3 15 +₹7,755 ·
S3-A 6 +₹2,280 · S3-E 1 +₹2,480.
**−₹63,957.50 of v19's recorded headline (47.8%) was non-causal value.**
A rebuild-mechanics correction was caught by the WS2 sanity and disclosed:
the first causal build pooled NS1 survivors at their recorded (exit-bar)
times; pooling at causal times throughout changes one key (2026-04-16 PE)
and REF_AUD moved +₹73,390.50 → +₹69,940.50 before any WS2 cell was scored.
v19 remains the December candidate of record in the Round-4 freeze,
annotated; **the audited lineage (v20, below) supersedes it** — v19's
recorded figures must not be quoted without this annotation.

## WS1 — WOUND DIAGNOSIS (Cycle 116; no Cycle 117 — no separator)

On the audited book: every one of the 49 losing legs is a full −₹1,720 stop
(the wound is stop COUNT, not size). Worst months Jul (−₹10,500) and Jun
(−₹3,640); the 16 wound legs total −₹27,520. Losses by family: BASE 32,
NS3 8, NS1 6, S3-A 3; by direction: PE 39 of 49 (PE is 78% of the book and
nets +₹57,276 — proportional). Closest feature, bearish-bias days: 56% of
the wound vs 35% of book legs (1.6× concentration; the frozen criterion
requires 2×) and bearish-day legs net +₹21,890 overall. **No feature passes
the frozen separator test — no conditional candidate was run.** The ≥₹400
premium band holds 81% of the wound on 73% of legs and nets only +₹12,508
on 74 legs (vs +₹58,602 on 22 legs in the ₹200–400 band) — noted as colour;
it does not meet the criterion and was not tested as a candidate.

## WS2 — NS1 PERMUTATIONS (Cycles 118–121) — nothing banked

Sanity: regenerated NS1 at (room 1.5, window 14:30) reproduces the audited
baseline's NS1 set exactly (16 legs in-book).
- C118 room 1.4 @ 14:30: book IDENTICAL to REF_AUD (+₹69,940.50) — no
  marginal leg survives pooling/filters.
- C119 room 1.6 @ 14:30: book IDENTICAL — no baseline leg sits in [1.5, 1.6).
- C120 window 14:00 @ 1.5: book IDENTICAL — no baseline signal in (14:00, 14:30].
- C121 window 15:00 @ 1.5: +₹69,474.50 (103 legs, FT90 47.6) — one extra late
  leg, net −₹466 vs ref, FT90 diluted. Rejected.
The frozen NS1 cell is a plateau on the causal book; the axis is closed.

## WS3 — SKILL-SOLO EARLY-LEG RE-ADMISSION (Cycles 122–124) — all rejected

Population (enumerated from data): 72 B1 legs with source systems exactly
{Skill V3}, entry ≤ 09:55, absent from B2 — 51 CE + 21 PE.
- C122 PE only: +₹35,413.50 (Δ −₹34,527), FT90 42.9, Jun–Oct half −₹247.50.
- C123 CE only: +₹22,885.00 (Δ −₹47,055.50), FT90 38.5, March flips red.
- C124 room ≥ 1.5 at the signal bar (52 legs pass): +₹8,687.00
  (Δ −₹61,253.50), FT90 36.1, March flips red — the room condition does NOT
  rescue the population; it is the worst cell.
The v1-era solo/early exclusion is load-bearing: this population is the
pool's worst segment on the modern book, in both directions.

## WS4 — VOLRIX-BANK GRID (Cycles 125–129) — THREE BANKINGS

Regenerated sets (trigger = prior-session close-to-close ≤ thr; entry next
session 09:20; strike ATM at entry spot; monthly expiry in force). Two
construction exceptions vs the frozen file set are named in the freeze
addendum: the 2026-06-01 calibration leg (regeneration fires 2026-06-02)
and the October leg's strike basis (frozen 54300 trigger-close ATM vs
regenerated 53900 entry-spot ATM).
- C125 −0.75% / cd10: +₹60,400.50, FT90 47.5 — rejected (net, FT90).
- C126 −1.25% / cd10: +₹62,440.50, FT90 46.1 — rejected (net, FT90).
- C127 −1.0% / cd10 (frozen cell, regenerated): **+₹72,110.50, FT90 48.5 —
  BANKED vs REF_AUD (Δ +₹2,170)**. The frozen file set was worse than its
  own rule on stored data; both exception legs are causal as regenerated.
- C128 −1.0% / cd5 (18 legs): **+₹78,050.50, FT90 49.0 — BANKED (Δ +₹8,110)**.
- C129 −1.0% / cd15 (11 legs): **+₹78,250.50, FT90 49.5 — BANKED (Δ +₹8,310)**.
Bank's trigger axis peaks at the frozen −1.0% (as Nifty's did), but Bank's
cooldown axis — never run before — is live: cd15 ≈ cd5 ≫ cd10.

## WS5 — BIAS-CONDITIONED EXIT SPLIT (Cycles 133–134) — both rejected

- C133 bearish-day (prior-day cs <35) runner legs lock := +40:
  +₹69,490.50 (Δ −₹450) — fails net only; every other gate leg clean.
- C134 bullish-day (cs ≥80) second-target legs tgt2 := +130:
  +₹62,590.50 (Δ −₹7,350) — fails net only.
The frozen exit geometry is not improved by bias conditioning.

## WS6 — COMBINATION / FINAL RE-GATE (Cycle 135)

The three WS4 bankings are one axis (mutually exclusive Volrix sets) and
WS5 banked nothing, so the combination is the best banked variant:
**book v20 = causal rebuild with the Volrix set regenerated at
(−1.0%, cooldown 15)** — re-gated whole-book: PASS vs REF_AUD and PASS
chained vs C127. Trades: `bank_engine_r5_v20_trades.csv`;
freeze: `bank_r5_v20_freeze.json`.

## ENDING SCORECARD

| Book | Net Jan–Oct | Legs | FT90 | /week | Pace/month | Gap to ₹1,50,000 |
|---|---|---|---|---|---|---|
| v19 (recorded, WS0-annotated) | +₹133,898.00 | 106 | 53.8% | 2.61 | ₹13,389.80 | ₹16,102.00 |
| REF_AUD (causal rebuild) | +₹69,940.50 | 102 | 48.0% | 2.51 | ₹6,994.05 | ₹80,059.50 |
| **v20 (Round-5 best)** | **+₹78,250.50** | **99** | **49.5%** | **2.44** | **₹7,825.05** | **₹71,749.50** |

v20 controls: no red month-ends; months Jan +22,748 · Feb +20,480 ·
Mar +1,120 · Apr −90 · May +18,430 · Jun +560 · Jul −8,780 · Aug −873.50 ·
Sep +9,726.50 · Oct +14,929.50; halves +₹62,688.00 / +₹15,562.50; placebo
−₹4,313.50 (beaten by ₹82,564); ex-top-3 +₹49,210.50; NOT_COMPUTED 0;
timing audit clean (99/99 entry bars); independent re-sum exact.
Families: BASE + NS1 + NS3(GD+GU)@T90/L65/G175 + S3-A + S3-E as in the
causal rebuild, with the 11-leg regenerated Volrix (b) set (−1.0%, cd15)
inside the pool.

**Verdict: Round 5 complete — all six workstreams gated through (17
cycles). The floor pace is NOT reached: the honest, causal Bank book
stands at ₹7,825.05/month against the ₹15,000 floor.** The round's main
event is the WS0 correction: nearly half of v19's recorded headline was
entry-timing value that does not exist at causal entries. What Round 5
added on the causal book (+₹8,310) came from re-parameterising a frozen
pool member (Volrix cooldown), not from new legs. November primary
(BNF-PAPER-V1) untouched throughout, per protocol.
