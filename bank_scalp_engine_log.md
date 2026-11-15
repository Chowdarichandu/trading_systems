# Bank Scalp Engine — Log

## Phase 0 — Data-integrity gate (2026-10-31 ~21:35–21:55 IST)
- Local audit: `data/1min/BANKNIFTY/` holds genuine 1-min SPOT for only 22 scattered
  days and NO option premiums → insufficient. Local premium store is 5-min only.
- Script token live (refreshed 2026-10-31 16:02 UTC, profile probe 200).
- PROOF (2026-10-27): index 1-min via v3 = 375 bars 09:15–15:29 ✓; expired ATM
  54400/54500 CE+PE 1-min via v2 expired-instruments = 385 bars ✓ (v3 returns 400
  for expired keys — the v2 expired route is the only option route).
- Monthly probes Jan–Sep 2026 (one mid-month day each): index + ATM CE all 375 bars ✓.
- RANGE calls work: one call returned 6 trading days for a contract.
- Bulk fetch launched (range call per contract over its expiry window; strike band =
  each day's 5-min [low, high] ± 100; per-day top-ups for misses; manifest written).
- Spot VWAP family killed at protocol level: index volume = 0 (lesson 3).
- Protocol frozen in bank_scalp_engine_protocol.md BEFORE any scoring.
- CADENCE RULE (user steering 2026-10-31 21:39 IST, standing on all his recursive
  engines): cycles complete in minutes and chain BACK-TO-BACK inside the running
  session — diagnose → freeze → score with full controls → bank/reject → next cycle
  immediately, no turn-end between cycles. The 15-min watchdog is a silent backstop
  only, never the cadence. Any watchdog-restarted cycle honours this same rule.
  Completion report only at protocol termination (SUCCESS / SATURATED / BLOCKED-DATA)
  or a genuine blocker.

## Phase 0 — Coverage verdict (2026-10-31 ~21:58 IST)
- Bulk fetch DONE: spot 192/192 days; 926 contracts; only 10 missing (day, strike,
  type) cells — 2026-02-01 (Sunday Budget session) 7 CE strikes, 2026-02-03 1 PE,
  2026-07-08 2 CE — all handled as NOT_COMPUTED if ever ATM at a signal.
- **Scored window = 2026-01-01 → 2026-10-27, 192 trading days, genuine 1-min.**
  Phase 0 PASSED (target was Jan–Oct; ≥2-month minimum exceeded ~5×).

## Cycle 1 — F1 "OR1": 1-min opening-range micro-burst (FROZEN before scoring)
- Diagnosis it answers: 5-min S1 died with gross ≈ ₹0 over holds up to 15 min.
  At 1-min the entry follows the break within a minute and the hold is ≤5 min —
  less signal slippage, less decay exposure. Empirical question: is there gross?
- OR = spot high/low of 1-min bars 09:15–09:29 (bars 0–14).
- Signal: 1-min bar i, 15 ≤ i ≤ 255 (09:30–13:30), close > ORH with previous bar
  close ≤ ORH → CE; close < ORL with previous close ≥ ORL → PE (fresh crosses only).
- Entry = open of bar i+1. Exits: **target +12, stop −9**, hard 5-min cap (protocol).
- Cap **4/day**; entry bars ≥10 min apart. UNIQUE-ONCE per (date, direction, i).
- Scorer: bank_scalp_engine_cycle1.py on core; full controls in the same run.
- **RESULT: REJECTED.** 541 trades, **−₹119,912.50** (H1 −₹64,654 / H2 −₹55,258.50);
  expectancy −₹221.65 ≈ −1× cost; gross = −₹892.50 ≈ **zero again**. Audit 0
  violations; re-sum matched; NOT_COMPUTED 0; capped-out 430. It beat both
  placebos (lag −₹133,453; random mean −₹127,756) — loses less than random, which
  is not an edge. Every month negative.
- Path diagnosis: 339/541 trades (63%) resolve INSIDE the entry bar; stops 298 vs
  targets 216 — the −9 stop wins the intra-bar race because the premium spikes on
  the break bar and retraces within the entry minute. Time-exits (27) averaged
  +2.23 pts gross. CE/PE gross both ≈ 0. **The 1-min retiming changed nothing:
  an OR break carries no 5-min forward premium drift at any decision speed.**

## Cycle 2 — F4 "PV1": premium-velocity trigger (FROZEN before scoring)
- Why: the one trigger family the 5-min study never had — the signal lives in the
  OPTION PREMIUM's own 1-min path, not in spot. If premium momentum itself persists
  for 1–3 minutes (order-flow/IV micro-bursts), a spot-based study could not see it.
- At each minute t (bar index 15…340): strike S = ATM at spot close of bar t.
  Velocity v = premium close of S at t − close of S at t−2 (that strike's own
  series, both types checked independently). If v ≥ **+10 pts** AND spot close[t]
  > spot close[t−2] → buy CE; mirror (PE premium v ≥ +10 AND spot down) → buy PE.
- Entry = open of bar t+1 of that strike/type. Exits: target +12, stop −9, 5-min cap.
- Cap 4/day (both types combined); entry bars ≥10 min apart; UNIQUE-ONCE (date, type, t).
- Scorer: bank_scalp_engine_cycle2.py; full controls in the same run.
- **RESULT: REJECTED.** 768 trades, **−₹167,215.50** (H1 −₹84,423 / H2 −₹82,792.50);
  expectancy −₹217.73; audit 0; re-sum matched; NC 0. Gross = **+₹1,743** — the
  first non-negative gross of any scalp test, and it beat both placebos clearly
  (lag −₹208,479; random mean −₹180,729, worst draw −₹168,268). But +₹1,743 over
  768 trades = +0.08 pts/trade — statistically a whisper, and the ₹220 cost turns
  it into −₹167k. Path: stops 418 (mean −9.00), targets 312 (+12.00), time 38
  (+2.00). Premium velocity at the ≥10 threshold is ~zero-gross like everything
  else; only a far stricter threshold (rarer events) could differ — parked as a
  possible late challenger, not a lead.

## DESIGN CHARTER v2 — frozen 2026-10-31 ~22:15 IST (confirmation)
- The user mandate of 21:42 IST is frozen into bank_scalp_engine_protocol.md as
  the Design Charter v2 addendum BEFORE any charter scoring: target ladder
  2.5/10/12/15/20 as separate variants, trailing stop (activate +8, trail 5),
  re-entry by design (flat-only, cap 8/day per mechanism, cost reason stated),
  OR + level-rejection setups on 1-min and 3-min, cost arithmetic in the open
  (breakeven 7.33 pts), day-level gate (% green days, median/worst/best day).
- **CONFIRMED: charter frozen before Cycle 3 (the first charter cycle) scoring.**
  Cycles 1–2 were Charter-v1 cycles (frozen before their scoring; both rejected;
  book empty). Saturation counter restarts under v2 per the addendum's reasoning.

## Cycle 3 — OR micro-burst, 1-min, TARGET LADDER (FROZEN before scoring)
- Setup: OR1 signals exactly as Cycle 1 (OR 09:15–09:29; fresh crosses, bars 15–255).
- Charter exits: five separate variants OR1-T2.5 / T10 / T12 / T15 / T20, each with
  fixed stop −9 and the 5-min cap; charter re-entry (flat-only, cap 8/day).
- Each variant gets full controls + day-level stats. Scorer:
  bank_scalp_engine_charter.py (driver: cycle3).
- **RESULT: ALL 5 RUNGS REJECTED.** Net: T2.5 −₹244,703 / T10 −₹191,074.50 /
  T12 −₹179,771 / T15 −₹169,982 / T20 −₹162,992. Both halves negative at every rung.
  Audit 0; re-sums matched. **Cost arithmetic, as mandated, in the open:** the
  +2.5 rung's win rate is literally **0.0%** — its best possible net is
  2.5×30 − 220 = **−₹145/trade**; it cannot win a single trade after cost, and its
  gross is ALSO negative (−₹52,203) because the −9 stop wins the intra-bar race.
  Gross rises monotonically with the rung (−994 → +10,089 → +19,218 → +24,888):
  post-break drift is real but slow — best gross/trade is +0.97 pts vs the 7.33
  breakeven. Days-green peaks at 19.5% (T20).

## Cycle 4 — OR micro-burst, 3-min, ladder (same frozen programme)
- **RESULT: ALL 5 RUNGS REJECTED.** Net −₹123,414.50 (T20) to −₹171,080 (T2.5);
  gross at T20 only +₹9,685.50 — 3-min decisions are strictly worse than 1-min for
  OR bursts at every rung (the confirmation delay eats the drift). Days-green ≤20.6%.

## Cycle 5 — Level-rejection, 1-min, ladder
- **RESULT: ALL 5 RUNGS REJECTED — family DEAD.** Gross NEGATIVE at every rung
  (−₹21,522 to −₹38,984): the 1-min rejection entry is anti-predictive, and the
  random placebo BEATS it at T12/T15/T20. H2 (Red-band months) is far worse than
  H1 at every rung — band/ledge rejections are the worst component.

## Cycle 6 — Level-rejection, 3-min, ladder
- **RESULT: ALL 5 RUNGS REJECTED — family DEAD on both timeframes.** Gross
  negative at every rung (−₹13,110 to −₹37,602); lag placebo beats it at most
  rungs. Level-rejection is closed: 5-min, 1-min, 3-min, fixed and (Cycle 8)
  trailing — anti-predictive everywhere.
- Saturation note: charter programme cycles 3–8 are the user's explicitly ordered
  frozen set (every rung × both setups × both timeframes + trailing entries). The
  3-consecutive-no-beat saturation rule applies to the post-programme challenger
  cycles; the programme itself is scored in full, as ordered. Recorded openly.

## Cycle 7 — Trailing variants: OR1-TRAIL, OR3-TRAIL (act +8, trail 5, stop −9)
- **OR1-TRAIL: REJECTED on net, but a gross breakthrough.** 858 trades, gross
  **+₹75,009.30 (+2.91 pts/trade)** — 3× the best fixed rung — net −₹113,750.70
  after ₹188,760 of cost. Beats both placebos (lag −₹142,305; random mean
  −₹162,015). Days-green 26.5%, best of any variant so far.
- OR3-TRAIL: gross +₹33,948 (+1.87 pts/trade), net −₹99,152. Rejected.
- Anatomy (OR1-TRAIL): 414 stops at −9 (−₹111,780); 402 trail-stop exits
  averaging **+15.05 pts** (+₹181,496); 42 time exits +4.20 pts.

## Cycle 8 — Trailing variants: LR1-TRAIL, LR3-TRAIL
- **BOTH REJECTED.** Trailing flips LR gross positive (+₹14,672.70 / +₹4,348.80)
  but H2 net is −₹105,606 / −₹106,129 and the random placebo beats both. LR closed.

## Diagnosis before Cycle 9 (OR1-TRAIL path splits, 858 trades)
- NO sub-population reaches the 7.33-pt breakeven: break size flat (2.8–3.6 pts
  across buckets), ordinal flat, best slices are tiny (13:00+ +5.28 pts, n=49;
  OR width <150 +4.39, n=51). The edge is diffuse — filtering would be slice
  curve-fitting. The remaining honest lever is the EXIT geometry itself.

## Cycle 9 — OR1-TRAIL-W: trail distance 5 → 7 (FROZEN before scoring)
- One change only: activation +8 and stop −9 unchanged; trail 5 → 7. Rationale:
  trail-stop exits bank +15.05 on average — the peak they fall back from is
  higher; test whether the 5-pt give-back is over-tight within the 5-min cap.
- Scorer: bank_scalp_engine_cycle9.py; full controls + day stats, same run.
- **RESULT: REJECTED.** Gross +₹65,091.30 — WORSE than trail 5 (+₹75,009.30).
  Net −₹123,668.70; days-green 27.0%. Wider trail surrenders more of fast-decaying
  peaks. Challenger no-beat 1.

## Cycle 10 — OR1-TRAIL-T4: trail distance 4 (one step the other way)
- **RESULT: REJECTED on net, gross improves.** Gross **+₹80,796.30** (+3.14
  pts/trade) > trail 5. Net −₹107,963.70 (H1 −₹49,969 / H2 −₹57,994.70); audit 0;
  beats both placebos (lag −₹142,566; random mean −₹158,050). No-beat 2.

## Cycle 11 — OR1-TRAIL-T3: trail distance 3
- **RESULT: REJECTED on net, gross improves again but decelerating.** Gross
  **+₹84,184.80** (+3.27 pts/trade); net −₹104,795.20 (H1 −₹49,309 / H2
  −₹55,486.20); WR 37.4%; days-green 25.4%; beats both placebos (lag −₹138,460;
  random mean −₹153,365); audit 0; re-sum matched. No-beat 3.
- Trail ridge: 7 → ₹65,091 · 5 → ₹75,009 · 4 → ₹80,796 · 3 → ₹84,185. Gains
  decelerate (+10k, +5.8k, +3.4k); the ridge peak is ≈ ₹85–90k gross against a
  ₹188,760 cost load at this frequency. No geometry step can close a 2.2× gap,
  and the Cycle-9 diagnosis proved gross/trade is flat across every selectable
  sub-population (best bucket +5.28 pts, n=49 — still < 7.33). The arithmetic is
  closed, not merely unexplored.

## TERMINATION — SATURATED (2026-10-31)
- 3 consecutive post-programme no-beat cycles (9, 10, 11) after the full mandated
  charter programme (Cycles 3–8: 20 ladder variants + 4 trailing entries) and the
  two v1 cycles — 11 cycles, 31 variants scored, every one with full controls in
  the same run (audit 0 violations throughout; every re-sum matched).
- **Book: EMPTY. Nothing ever met the banking gate.** Success gate NOT met.
- Best variant (by gross, NOT banked): OR1-TRAILT3 — 859 trades, net
  −₹104,795.20, gross +₹84,184.80 (+3.27 pts/trade vs 7.33 breakeven), days-green
  25.4%, window 2026-01-01 → 2026-10-27 (192 trading days, genuine 1-min).
- Bottom line: at ₹220/trade on 1 lot (30), sub-5-minute Bank Nifty premium
  scalping has a hard arithmetic ceiling. The best genuine mechanism found —
  1-min opening-range breaks with a tight trailing exit — captures +3.27
  pts/trade gross, 45% of the cost breakeven. Level-rejection is anti-predictive
  at every horizon tested; premium velocity is ~zero-gross; the +2.5-pt rung
  cannot win a single trade after cost. This terminates SATURATED, not SUCCESS.
