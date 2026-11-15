# Loss-Reduction Programme — Bank Nifty · Nifty · Stocks
### What we did · What we are doing · How December gets decided

Created 2026-11-10 on Chandu's direction ("start working on it — make a document on what we did and what we are doing").
Paper only, real money ₹0. Index figures = option premiums per 1 lot (Bank lot 30, Nifty lot 65, cost ₹220/trade). Stocks = equity cash, provisional per 100 shares, ₹40/trade. Segments are judged separately, never pooled.

**Standing rules this programme works under**
- November primaries (Bank BNF-PAPER-V1, Nifty NF-PAPER-C3G7, frozen SarvaRitu book) are NEVER mutated mid-month. Every fix proves itself as a labelled shadow first.
- No number is quoted before the full controls gate passes in the same run (timing/leak audit, placebos, halves, month table, ex-top-3, independent re-sum).
- A backtest number earns no trust without forward, live, chart-verifiable evidence.
- Floor: ₹15,000/month per segment, separately. Tracker: `segment_floor_tracker.md`.

---

## PART 1 — WHAT WE DID (every loss-reduction attempt, with its verdict)

### Bank Nifty
| Attempt | What it was | Verdict |
|---|---|---|
| Break-hold confirmation (2026-11-02) | Delay OR-break entries until the break holds | **REJECTED** — +₹18,731.50 → +₹4,462.00; avoided ₹6,741 of losers but the delay cost ₹21,010.50 |
| Target ladder T1–T4 (2026-11-03) | Owner's ladder (+30/+58/+82/+100 spot) on v21's 99 entries | **Does not displace v21 exits** — +₹16,777.50 vs +₹83,650.50 incumbent; all profit in 40 T4 legs; close-based exits leak |
| S/R rejection layer (2026-11-04) | Support/resistance rejection patterns added to v21 | **REJECTED** — combined book −₹36,588.00 vs v21's +₹83,650.50; turns v21 negative |
| v22 Phase 1 (EVE-04 + EVE-05) | NS1 give-back lock + skip pre-10:30 OR-break PE | **PASSED** — +₹91,450.50 Jan–Oct; runs as SHADOW v22 |
| v22 Phase 2 re-entry (EVE-06a) | Re-enter on signal recurrence after a leg stop | **PASSED as increment** — +₹6,119.00 / 16 legs (flag: 5 of 16 double-stopped) |
| Afternoon sleeve (EVE-06b) | New afternoon entries | **REJECTED** — −₹36,659.50 / 136 legs, 8 of 10 months negative |
| Aggressive tune (2026-11-04) | Entry expansion, BE-arm, scoped lock, runner extension, NS3/S3 add-ons | Saturated at **+₹123,471.50 Jan–Oct (₹12,347.15/mo)**; entry-expansion and lock families all rejected; runner extension +₹5,400 and v1 add-ons +₹20,502 banked. In-sample ceiling, zero forward days at build time |
| BREAK-CAPTURE v1 (2026-11-08) | Standalone breakout capture, re-entry (R) and hold-60 (H) forms | **ALL FOUR BOOKS FAIL** — Bank R −₹10,018.80, Bank H −₹14,136.80 (2026). Standalone breakout entry on options is dead in both forms |
| EVE-13 (2026-11-09) | Skip OR-break PE before 11:00 | Gate **PASS but NOT PROMOTED** — dominated by the standing 10:30 skip (EVE-05: +₹28,994.50 vs +₹18,735.50); the 10:30–11:00 legs are earners (+₹10,259.00). 10:30 is the measured peak |
| EVE-14 / EVE-15 (2026-11-09) | Skip solo-Skill / all OR breaks before 11:00 | **FAIL** both |
| EVE-16 (2026-11-10) | v22 + re-entry gated as one full book | **FAIL by one leg** — net +₹97,569.50 beats v22 (+₹6,119) and every other leg passes, but August flips green→red on one re-entry (−₹1,267). Leading December candidate on net (₹9,756.95/mo); adoption needs Chandu's explicit waiver (DEC-S1 precedent) |
| EVE-17 (2026-11-10) | Close-based stop for the first 3 bars (whipsaw attack) | **FAIL** — only 1 addressable leg Jan–Oct (EVE-05 already removed the cluster) and it closed through its stop. Finding: quick OR stops are genuine closes, not wicks — softening the stop makes fills variable and usually worse. Route closed |
| Bleed controls | Day-loss cap −₹3,000; circuit breaker (3 straight losing days or MTD ≤ −₹5,000 → pause + flaw cycle) | In force on the shadow/December layer. Bank primary hit the trigger 2026-11-05 (3 losses, MTD −₹5,160) — recorded against December adoption of the primary frame |

### Nifty
| Attempt | What it was | Verdict |
|---|---|---|
| Re-entry port (EVE-08, tested twice) | v22-style re-entry on DEC-S1 | **GATE FAIL both times** — 24 stop days → 4 reclaim triggers, all blocked by the −₹3,000 day cap; cap-removed sensitivity still negative |
| Afternoon sleeve (EVE-06 / EVE-12) | Afternoon entries / break sleeve | **Cannot be built** — no stored Jan–Oct 5-min Nifty spot population; no number quoted |
| EVE-07 (2026-11-05) | DEC-S1 minus component B PE | **PASSED** — became TUNED SHADOW v1 (+₹103,050.25 Jan–Oct) |
| EVE-09/10/11 (2026-11-05) | Further component trims on the tuned frame | **EVE-11 PASSED** — DEC-S1 minus B PE, A-CE, C-CE = +₹115,950.75 (₹11,595/mo pace) → TUNED SHADOW BOOK v2, live from 2026-11-06 |
| EVE-13 (2026-11-06) | Day-loss cap on tuned v2 | Exact **NO-OP** — cap axis closed on both Nifty frames |
| EVE-14/15/16 (2026-11-09) | Entry-time cutoffs ≥10:30 / ≥11:00 | **FAIL** all three |
| EVE-17 (scored 2026-11-10) | No-development cut: exit a leg if premium hasn't reached +15 by the 3rd bar | **GATE FAIL, premise inverted** — +₹23,048.25 vs +₹54,102.00 incumbent (Δ −₹31,053.75). The cut legs are worth +₹19,163.50 as traded: slow developers are this book's earners. RSI-NIFTY-009 reclassified as normal stop-rate variance (Nov 9 = 6th stop in 25 confirmed-PE legs); no fix carried forward |
| EVE-18 (2026-11-10) | Loosen C3 via day-level second-source agreement | **NOT TESTABLE** — the stored pool merges sources into one key per (date, direction), so the admission set is 0 by construction. Every C3-loosening reachable from stored data is now closed; further attack needs sub-key signal data that doesn't exist in stored form |
| EVE-12 (population built, scored 2026-11-10) | First fresh day-range break after 12:30 while flat, DEC-S1 geometry | **GATE FAIL, decisively** — standalone −₹100,604.40 / 156 legs (FT 7.7%: afternoon entries decay, only 12 reach +90); layered on TUNED v2 the increment is −₹109,591.65 and drags the book to +₹6,359.10; Feb/May/Jun/Aug flip red; both placebos beat it (flipped/fade side +₹21,410 — observation only, not a candidate). **Third independent rejection of the standalone afternoon-break entry** (Bank EVE-06(b), BREAK-CAPTURE v1, EVE-12). The population build itself stands as completed infrastructure (205/205 spot days, premium store completed add-only, hash-verified). November counterfactual: NOT_COMPUTED (no November afternoon population exists) |
| DEC-S1 tuning overall | Full next-phase tune-up (2026-11-04) | **DEC-S1 stands untuned** — inventory empty; everything that ever passed is already inside it. Phase 2 needs a genuinely new Nifty signal source or December fresh data |

### Stocks (SarvaRitu, equity cash)
| Attempt | What it was | Verdict |
|---|---|---|
| P2F skip-opening-bar (2026-11-02) | Delay P2F entries one bar | **REJECTED** — +₹27,293.58 → +₹9,582.00 |
| N4-V3 one-sided cap (2026-11-02) | Skip N4-V3 LONG entries with ≥ +3.0% move by 09:30 (SHORTs uncapped) | **PASSED at book level** — runs as TUNED SHADOW v1 from 2026-11-03 |
| ORB-TREND v1 (2026-11-05) | Opening-range breakout sleeve, 4 variants, both years | **ALL FAIL BOTH YEARS** (best variant −₹73,221 in 2026); the entry fails, not the exit; 2026 flipped placebo beats the real book |
| EVE-09/10/11 (2026-11-05) | Component filters | **FAIL** all |
| EVE-12/13/14 (2026-11-06) | INV-ABOVE repeat filters | **FAIL** — INV-ABOVE repeats are earners; the filters would cut the money-making legs |
| EVE-15 (2026-11-09) | Widen INV-ABOVE stop 0.50% → 0.80% | **FAIL** — rescan not faithful to the live chain |
| EVE-16 (2026-11-09) | Drop same-day P2F leg overlap | **FAIL** — no material gain |
| EVE-17 (2026-11-09) | Delete GLENMARK from INV-ABOVE | **FAIL** — 2026 degrades and the placebo beats it |
| EVE-18 (2026-11-10) | INV-ABOVE stop scaled to opening-range width | **FAIL (2 legs), flagged for December judging** — largest single-component effect ever gated here (2025 component +₹5,209.71 → +₹23,711.10; Nov-9 counterfactual: both GLENMARK rounds reach target instead of −₹2,734.40), but 2026-07 flips green→red and whole-book 2026 ex-top-3 degrades. Gate stands; not promoted |
| EVE-19 (2026-11-10) | Re-entry delay ≥3 bars after a stop exit | **FAIL** — 2025 improves (+₹4,767.05) but 2026 degrades (−₹2,436.23); cross-year leg fails |
| EVE-20 (2026-11-10) | Drop INV-ABOVE entries when the stock's prior day moved ≥ +4.0% | **GATE PASS (all legs, both years)** → **PROMOTED as Stocks TUNED SHADOW v2 from Wed 2026-11-11**. Small but uniform (+₹2,193.52 over two years; mirror filter worsens both years, so the post-spike stand-down is the real effect). Nov-9 counterfactual: would have saved the full −₹2,734.40 |

### Cross-segment (dead ends, closed)
- **Morning-Mover line: DEAD** — look-ahead artefact, retracted 2026-10-31; its books fell with it.
- **₹1,000/day-per-entity hunt: STOPPED** by Chandu 2026-11-03; target not met; reopens only on his word.
- **SHORT-FOLLOW (DAILY-2LEG R7-M1): gate-passed and frozen, DISARMED** on Chandu's order 2026-11-03; runs only on his approval.
- **Final rulebook (ceilings Bank ₹7,500 / Nifty ₹9,530 / Stocks none): built, NOT running** — its forward 20-day run awaits Chandu's approval.
- **Trailing stops:** tested in all three engines; adopted in none of the final-rulebook books.

---

## PART 2 — WHERE THE LOSSES ACTUALLY ARE (November forward evidence, 6 trading days)

**Bank Nifty primary: −₹6,880 · 4 trades · 0 full targets · FT 0%**
- All 4 trades stopped at the full −₹1,720: Nov 2 PE 54800 (base leg), Nov 3 NS1 CE 55500 (developed +33.4, gave it all back), Nov 4 NS1 CE 55900 (never developed, MFE +24.6), Nov 9 PE 58900 (stopped on its own entry bar).
- Loss concentration: early OR-break PEs and NS1 second legs. Historical frequency of the Nov 9 failure mode: 14 of 70 OR-break legs stop within 10 minutes (20%), 4 on the entry bar itself (RSI-BANK-007).
- Session-coverage flaw: 4 missed afternoon moves (Nov 3, 5, 6, 9) — spot ran +612 to +1,094 points after the book went flat. Every capture form tested for this has failed the gate; no honest fix exists yet. The money in this pattern sits on the exit side of entries already trusted (Nov 5: the same 57100 CE made +₹2,480 under a +90 target and +₹13,364 ridden to square-off).

**Nifty primary: −₹3,470 · 1 trade in 6 days**
- The primary's problem is scarcity, not bleed: C3 confirmation blocked solo Skill legs on 4 of 5 days in week 1 (RSI-NIFTY-008). Its one trade (Nov 9, PE 24800) stopped with no follow-through — the breakdown printed the day low and chopped (RSI-NIFTY-009).
- DEC-S1 shadow: −₹4,123.50 · 4 trades. Its bleed is one component: **B PE is 0-for-3 in November, −₹7,160** (Nov 2 −₹220 BE-stop, Nov 3 −₹3,470, Nov 5 −₹3,470). Component C's one leg made +₹3,036.50.
- SHADOW Skill (Nifty): **+₹3,973.25 · 5 trades** (Nov 9 scored 2026-11-10: the primary's PE 24800 leg, −₹3,470) — still the strongest Nifty line in November, halved by Monday's stop.

**Stocks book: +₹7,565.18 · 24 trades (provisional per 100 shares)**
- The book works. Its leak is specific: INV-ABOVE's 0.50% stop sits inside one-bar noise on strong reaction names — Nov 9 GLENMARK ×2 = −₹2,734.40 while P2F-R2 on the same name made +₹3,197.50. GLENMARK is INV-ABOVE's worst name historically (26 trades, −₹5,850.55); 128 of 206 stored INV-ABOVE trades exit by stop. All three fixes tried on 2026-11-09 failed the gate.

**Shadows vs primaries (November, the loss-reduction evidence race — updated 2026-11-10 with Nov 9 shadow scoring completed)**
- Bank: SHADOW v22 **+₹760** (2 trades) · SHADOW v21 **−₹960** (3 trades) · TUNED v3 −₹5,160 (3 trades, took the primary's losing legs; its −₹5,000 breaker level is tripped) · Primary −₹6,880. (Nov 9: v21 and v22 both took the primary's PE 58900 leg and stopped at −₹1,720 — the preliminary engine read of "no trade" was wrong; the candle-scored log governs.)
- Nifty: SHADOW Skill **+₹3,973.25** (5 trades; Nov 9 it took the primary's PE 24800 leg, −₹3,470) · TUNED v2 ₹0 (0 trades — unproven forward) · DEC-S1 −₹4,123.50 (no trade Nov 9) · Primary −₹3,470.
- Bank SHADOW Skill: **−₹1,920** (6 trades; Nov 9 −₹1,720 on the same PE 58900 leg).
- Stocks: TUNED SHADOW v1 +₹2,523.97 book basis (runs behind the frozen book by design — it is a filter test, 1-skip sample so far).

---

## PART 3 — WHAT WE ARE DOING NOW (running, from 2026-11-10)

1. **November finishes exactly as frozen** (to Mon 2026-11-30). Primaries untouched; the month's verdict stays honest. Tue 2026-11-10 is a market holiday (Diwali-Balipratipada) — no trades, flat lines are the holiday, not a failure.
2. **The shadow race continues daily** — v21, v22, TUNED v3 (Bank); DEC-S1, TUNED v2, Skill (Nifty); TUNED v1 (Stocks) — scored from the same real candles, logged separately, never merged. Nov 9 shadow rows were caught up and candle-scored on 2026-11-10 (all five logs complete through Nov 9); nothing is estimated.
3. **Evening engines keep the flaw cycle running** (Bank 17:15 / Nifty 17:32 / Stocks 17:47, Mon–Fri): every losing day gets a named failure cause, a historical frequency, and up to 3 fully-gated fix candidates. A candidate that passes becomes the next tuned shadow from the next trading day — never a mid-window primary edit.
4. **Bleed controls stay armed** on the shadow/December layer: day-loss caps (−₹3,000 index / −₹1,500 stocks) and the circuit breaker (3 straight losing days or MTD ≤ −₹5,000 index / −₹3,000 stocks → pause + flaw cycle).
5. **FIX AGENDA — owner escalation 2026-11-10 ~15:30 IST ("Banknifty is falling and Nifty are failing — fix that one, that's the main agenda"):** (a) **Bank TUNED STACK goes LIVE as a labelled shadow from Wed 2026-11-11** — wired into the Bank engine (additive section, 2026-11-10) with its own log `november_shadow_stack_bank_log.csv` seeded with the Nov 2–9 backfill rows (scored_live=NO — RETROSPECTIVE; +₹760, identical to v22 — the November evidence supports the v22 frame; the stack's extra layers still need their live days). The frozen primary is NOT switched — the freeze is the owner's own integrity rule and stands until he rescinds it. (b) Nifty: TUNED SHADOW v2 (DEC-S1 minus the bleeding B-PE leg) is already the live fix on the primary frame, ₹0/0 trades so far — scarcity, not absence of the fix, is its November story; the EVE-12 population build (below) is the remaining preparatory fix work. (c) December adoption remains the point where the fixed books become THE books, judged on this forward evidence.
6. **Tuning round of 2026-11-10 (owner-directed, run midday):** Bank EVE-16 FAIL-by-one-leg (waiver question open), EVE-17 FAIL (route closed); Nifty EVE-17 FAIL (family refuted), EVE-18 NOT TESTABLE (C3-loosening space closed); Stocks EVE-18 FAIL-but-flagged for December judging, EVE-19 FAIL, **EVE-20 PASS → TUNED SHADOW v2 live from Wed 2026-11-11** beside TUNED v1. Remaining queue: Nifty EVE-12 population build (5-min spot + premium Jan–Oct) before any afternoon-break scoring; Bank EVE-10 remains NOT TESTABLE and is not forced.
7. **Bank positive-tuning session (owner order 2026-11-10 ~15:36 IST, "tune Bank till it turns positive"):** **BANK-EVE-19 PASS → TUNED STACK v2** (stack + pre-10:30 NS1 skip, re-entry derived against the skipped book): **+₹127,351.50 Jan–Oct, ₹12,735.15/month, Δ +₹3,880.00 vs the stack**, all gate legs pass, all 10 months positive (delta rests on 4 legs — noted honestly in the registry; remaining floor gap ₹2,264.85/month). v2 is the stack shadow's live rule set from its first live day, Wed 2026-11-11 (Bank engine addendum wired 2026-11-10). BANK-EVE-18 (ride runners past the second target to square-off) FAIL — Δ −₹11,578.50; the placebo arming at +120 scored exactly the candidate, proving the cap removal itself loses: **the second target is load-bearing**, and the Nov 5 +₹13,364 ride is unrepresentative. BANK-EVE-20 ablations: all three layers earn their place (minus re-entry −₹6,119 in-book value; minus c4 −₹5,400; minus v1 −₹20,502 with August flipping red). November counterfactual unchanged at +₹760 under every variant (November's stack had no NS1/re-entry/v1 legs).
6. **December adoption pack is being assembled from this document** — the criteria in Part 4 are pre-registered now, before December data exists, so the decision can't be fitted afterwards.

---

## PART 4 — DECEMBER ADOPTION CRITERIA (pre-registered 2026-11-10)

Judged per segment, on December data alone under each candidate's pre-registered pass/kill, with November forward evidence and the Jan–Oct gate as the supporting record. Month-end November verdicts land 2026-11-30; the December book choice is Chandu's call on that evidence.

**Bank Nifty — candidates:** v21 (frozen December candidate; PASS = December net > 0 + clean audit; KILL ≤ −₹5,000) · v22 (v21 + EVE-04 + EVE-05) · TUNED v3 (primary frame + EVE-09 stack) · saturated tuned stack (+₹123,471.50 in-sample — admitted only with its in-sample label attached).
- The primary frame (BNF-PAPER-V1 construction) carries a recorded circuit-breaker trigger from November (3 straight losses, MTD past −₹5,000) — that stands against adopting the primary frame unchanged.
- Before the first December trade: confirm the December expiry (2026-12-29 per the calendar rule) against the contract master.

**Nifty — candidates:** DEC-S1 (adopted candidate; pass/kill pre-registered, KILL ≤ −₹3,470) · TUNED v2 (DEC-S1 minus B PE / A-CE / C-CE).
- DEC-S1's two failed-and-waived legs stay on its record permanently (FT 34.0% vs 34.3%; March flips red) — never quoted without the qualification.
- The B-PE question is decided on evidence: B-PE is 0-for-3 (−₹7,160) in November forward data; TUNED v2 has 0 November trades, so if v2 is chosen it is chosen on gate evidence, not forward proof — and that distinction goes in the decision note.

**Stocks — candidate:** Variant C (adopted; legs (c)/(e) FAILED-AND-WAIVED vs the pre-adoption baseline — the qualification is never dropped).
- Judged per year (2025 and 2026 separately ≥ floor pace), never pooled.
- Before December: reconcile the N4 threshold (adopted 0.8% vs live producer 1%) and extend the live-shadow cron's November body-guard.

---

## PART 4b — BANK PRIMARY SWITCH (owner order, 2026-11-10 ~15:53 IST)

After the choice was put to him twice, Chandu ordered the outcome three times ("make it profitable" / "fix that one, that's the main agenda" / "I need banknifty turn green"). Executed as a **primary-designation switch, effective Wed 2026-11-11**: TUNED STACK v2 is Bank Nifty's primary-designated book; its November ledger starts at the +₹760 backfill. BNF-PAPER-V1 becomes the labelled **LEGACY FROZEN** control line — its logging, scoring and −₹6,880 record are untouched; nothing is rewritten or erased, and the freeze on the V1 *spec* still holds (it simply no longer carries the primary designation). Wired into the Bank engine (stack scoring = the engine's primary task; reports lead with the stack) and the daily-stats job (Bank section leads with TUNED STACK v2 from 11 Nov; the Nov-30 verdict reports the two segments separately and labelled, never merged). Stated limit: a green *combined* November for Bank still requires v2 to earn +₹6,880 across Nov 11–30 — not guaranteed; the switch guarantees the headline book is the profitable gate-passed frame from tomorrow.

## PART 5 — OPEN DECISIONS (Chandu's calls, not the engine's)

1. **December book selection, per index** — on the Nov 30 evidence. Current forward evidence favours Bank v22's frame and (on gate evidence only) Nifty TUNED v2; DEC-S1 and v21 remain the frozen candidates until he rules.
2. **Ladder next step** — test with intrabar triggers, or accept the verdict and keep v21 exits (open since 2026-11-03).
3. **SHORT-FOLLOW paper run** — gate-passed, frozen, disarmed; runs only on his approval.
4. **Final-rulebook forward 20-day run** — pre-registered, awaiting his approval.
5. **ORB-TREND v2 direction** (stocks breakout) — regime gate / retest entry / drop (open since 2026-11-05).

*Files: registry `november_rsi_candidates.md` · journals `november_journal_{bank,nifty,stocks}.md` · engine logs `november_rsi_{bank,nifty,stocks}_log.md` · tracker `segment_floor_tracker.md` · gate evidence per candidate in the dated eve files. This document is the summary; the files are the record.*
