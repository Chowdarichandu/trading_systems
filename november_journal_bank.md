# Bank — November 2026 paper trade journal

Every trade gets one full entry per trade_journal_TEMPLATE.md: basis, strategy, outcome, failure cause, fix.
Written nightly by the RSI engine (17:15). Paper only, real money ₹0.

## 2026-11-02 · BANKNIFTY · PE 54800 · PRIMARY

- **Strategy in play:** B2 opening-range breakdown (Skill V3), BNF-PAPER-V1 primary; NS1 second-leg search also ran (see comparison).
- **Basis for the trade (why this trade, why then):** Skill V3 opening-range break — first 5-min close below the opening-range low at 10:15 (OR = opening range per the frozen Skill V3 construction); entry at the open of the next bar, 10:20, per the frozen convention. B2 key kept: the leg is Skill V3 PE solo, but the frozen B2 drop rule removes Skill-solo legs only with entry ≤09:55 — this entry is 10:20, so it stands; the Skill V3 CE block does not apply to a PE leg. PDH/PDC/PDL and the exact Red band: n/a — not recorded in the EOD log row; not invented here.
- **Market context at entry:** OR-breakdown signal mid-morning; spot recovered back inside the opening range within ~15 minutes of the signal and stayed inside for hours (watcher/homework record for today) — i.e. the breakdown did not follow through. Gap/day-type fields: n/a — not recorded in the EOD log row.
- **Entry:** 10:20 @ ₹681.95 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹631.95 (−50) · target ₹771.95 (+90) · square-off 15:10
- **What actually happened:** premium fell straight to the stop on the next bar — exit 10:25 at the stop. MAE −50 pts (stop hit at 10:25); MFE n/a — no intra-trade premium path beyond entry/exit is recorded in the EOD log, and the trade lived one bar after entry.
- **Exit:** 10:25 @ ₹631.95 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points on the premium) · full-target? no
- **Rules followed exactly?** Yes on the frozen EOD construction. One defect logged (process, not rule): the live producer flagged this entry MISSED at 10:34 (first poll after the entry bar), so the trade was not announced live; the EOD frozen-construction row is the official log per spec.
- **Same-day comparison:** CONTROL U1-B2 took the identical B2 key (see its entry below) — same entry, same stop, −₹1,720 (control money, never added to primary). NS1 second leg: none — the first fresh OR crossing after the base exit had room_ratio 1.49 < 1.5, so the search ended per the frozen NS1 rule; the block was correct under the frozen spec, and Bank Round 8 (2026-11-02) found room 1.25 / 1.75 are exact no-ops on the causal book, so there is no evidence a looser room gate would have helped today.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the OR breakdown reversed immediately; spot was back inside the range within ~15 minutes.
- **Evidence:** entry 10:20 @ 681.95, stop exit 10:25 @ 631.95 (one bar, full −50); spot recovered inside the OR within ~15 minutes and stayed inside for hours.
- **Has history seen this before?** Yes — recurring. In the primary's own B2 pool (Jan–Oct 2026, `historical_proof_bank_B2_trades.csv`): 14 of 70 OR-break legs (20.0%) stopped within ≤10 minutes, every one at the full −₹1,720; 12 of the 14 were PE. All 3 spot-checkable cases (of 14) had closed back inside the OR by 11:00. Counted in `november_rsi_homework_2026-11-02.md`.
- **The fix:** three no-delay skip-at-entry candidates tested tonight (see registry): BANK-EVE-01 (skip OR entries before 10:00) GATE PASS but superseded; BANK-EVE-02 (skip Skill-V3-solo OR legs — the only candidate that would have caught today's leg) GATE FAIL (G5 halves: H2 −₹12,605.50 < 0); BANK-EVE-03 (skip OR PE entries before 10:00) GATE PASS → TUNED SHADOW BOOK from 2026-11-03. Honest note: EVE-03 would NOT have caught today's trade (entry 10:20) — today's shape remains an accepted risk under the promoted shadow; the fix attacks the bucket where this cause concentrates (8 of the 14 historical quick stops were PE entries before 10:00).
- **Lesson ID:** RSI-BANK-001

## 2026-11-02 · BANKNIFTY · PE 54800 · CONTROL

- **Strategy in play:** U1-B2 control (BNF-PAPER-V1's labelled control — B2 exactly, no NS1).
- **Basis for the trade (why this trade, why then):** identical B2 key to the primary today — Skill V3 OR-breakdown, signal 10:15, entry 10:20; the control shares the B2 construction, so the same frozen rule authorised it. Levels: n/a — not recorded in the EOD log row.
- **Market context at entry:** same as primary — breakdown reversed, spot back inside the OR within ~15 minutes.
- **Entry:** 10:20 @ ₹681.95 · 1 lot (30)
- **Planned exits at entry:** stop ₹631.95 (−50) · target ₹771.95 (+90) · square-off 15:10
- **What actually happened:** stopped on the next bar, same path as primary. MAE −50; MFE n/a — not recorded in the EOD log.
- **Exit:** 10:25 @ ₹631.95 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · CONTROL money — never added to primary totals.
- **Rules followed exactly?** yes
- **Same-day comparison:** primary took the same key with the same result (above); the primary's NS1 search additionally ran and correctly produced no second leg (room_ratio 1.49 < 1.5).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race (same event as primary).
- **Evidence:** entry 10:20 @ 681.95 → stop 10:25 @ 631.95.
- **Has history seen this before?** Yes — same count as primary: 14 of 70 OR-break legs in the B2 pool stopped within ≤10 minutes (20.0%).
- **The fix:** same candidates as primary — BANK-EVE-03 GATE PASS → shadow from 2026-11-03 (shadow is scored against the primary; the control is unchanged). Status: TESTED tonight.
- **Lesson ID:** RSI-BANK-001 (shared with the primary entry — same signal, same event)

## 2026-11-03 · BANKNIFTY · CE 55500 · PRIMARY

- **Strategy in play:** NS1 second leg, BNF-PAPER-V1 primary (B2 base produced no leg today — see comparison).
- **Basis for the trade (why this trade, why then):** NS1 second-leg rule — the S1 base leg exited by stop at 10:00 (exit bar ≤13:30), and the first fresh opening-range crossing after that exit came at 10:15 on the CE side. Room ratio was infinite (no prior-day level above the crossing close), the day bias was bullish so the CE was not blocked, and the signal was ≤14:30 — all frozen NS1 conditions met. Entry at the open of the next bar, 10:20, in the 55500 CE (expiry 2026-11-23, key NSE_FO|62165), premium verified from Upstox intraday option candles at EOD per the log row. PDH/PDC/PDL exact values: n/a — not recorded in the EOD log row; not invented here.
- **Market context at entry:** Bullish-bias morning; the base leg had already stopped out at 10:00 and spot then crossed the opening range upward. Other systems today: (lA) v2 confirmer never broke the OR low 09:30–11:30; V5 v2 had no candidates (Skill candle filtered: CE close ≥ PDH); Volrix (b) prev-day change +0.58% > −1.0%, no trigger.
- **Entry:** 10:20 @ ₹867.60 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹817.60 (−50) · target ₹957.60 (+90) · square-off 15:10
- **What actually happened:** premium developed first — 10:20 high 893.40, 10:25 high 896.00, 10:30 high 901.00 (MFE +33.4 pts at 10:30) — then faded: 10:35 low 852.00 (back through entry), on to the stop at 11:10 (low 811.05). MAE −50 pts (full stop).
- **Exit:** 11:10 @ ₹817.60 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points on the premium) · full-target? no
- **Rules followed exactly?** Yes — frozen NS1 construction, EOD log row.
- **Same-day comparison:** CONTROL U1-B2: no trade today — its only key was the same Skill V3 CE solo (signal 09:55, entry 10:00), blocked by the frozen B2 rule (Skill V3 Bank CE blocked), and the control has no NS1. SHADOW-TUNED v1 (BANK-EVE-03): took this NS1 leg identically (EVE-03 touches only B2 base PE OR entries before 10:00; this is an NS1 CE at 10:20 — three non-matches) → shadow −₹1,720 today, labelled shadow money. B2 base (primary): no leg — the only U1 key was the blocked Skill V3 CE solo above.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** slow give-back / developed-then-stopped — the trade developed past +30 (to +33.4 by 10:30) and then faded all the way back through entry to the full −50 stop. Exit-rule shape, not a dead-on-arrival entry: the entry produced a real excursion and the fixed G0 geometry gave all of it back plus the full stop.
- **Evidence:** entry 10:20 @ 867.60 → highs 893.40 / 896.00 / 901.00 (10:20–10:30) → 10:35 low 852.00 (through entry) → stop exit 11:10 @ 817.60. Candle-by-candle counterfactual in `flaw_cycle_2026-11-03.md` §4 (same day, same trade).
- **Has history seen this before?** Yes — recurring and quantified today by the flaw cycle on the causal v21 book (Jan–Oct 2026, 99 legs): 22 of 99 legs (22.2%) developed past +30 and then faded to the full stop (−₹37,840 combined); they are 22 of the book's 47 full stops. In the NS1 family specifically: 16 legs, 7 full stops, of which 3 were this developed→stop shape in the gated replay (2026-02-03, 2026-03-24, 2026-07-02). Today is the 2nd live November instance of the book's full-stop flaw in 2 days (Nov 2 was the never-developed shape).
- **The fix:** BANK-EVE-04 — give-back lock on NS1 second legs only (a completed bar's high ≥ entry+30 raises the stop to entry+0 for subsequent bars; base and all other legs unchanged). Tested tonight behind the full gate: v21 +₹83,650.50 → +₹87,370.50 (+₹3,720; 4 NS1 legs changed: 3 stops saved +₹1,500 each, 1 square-off cut −₹780), halves +₹64,158 / +₹23,212.50, ex-top-3 +₹58,330.50, no month flips, placebo beaten, timing 0 violations — GATE PASS → part of TUNED SHADOW BOOK v2 from 2026-11-04. Counterfactual on today: the lock armed at the 10:30 close and would have exited 10:35 @ ₹867.60 → −₹220 instead of −₹1,720. Honest contrast: the same lock applied book-wide (FC-2, flaw cycle today) FAILED the gate (−₹39,661.50) because base-pool winners share the dip shape; the NS1-only restriction is what separates. Status: GATE PASS → shadow from 2026-11-04.
- **Lesson ID:** RSI-BANK-002

## 2026-11-03 · BANKNIFTY · MISSED-MOVE (no trade — book flat after 11:10)

- **What the book was doing:** flat — both the (blocked) base slot and the single NS1 second leg were consumed; every Bank book is morning-only, so there was no re-entry and no afternoon participation by construction.
- **What was missed:** after the 11:10 stop exit (spot 55,459.50), spot reclaimed the morning range high (55,486.95) and ran to a day high of 55,739.00 (+279.5 pts from the exit print, ≥ the 150-pt missed-move trigger). The same 55500 CE premium crossed back above the original entry at 12:50 (close 883.80), hit a day high of ₹995.00, and stood at ₹907.50 at 14:10 — the exited trade would have been ≈ +₹977 at 14:10 vs −₹1,720 realised.
- **Whipsaw honesty:** the spike fully round-tripped — spot fell back to 55,382 by 15:00 and the premium to ₹737.55, below the original stop; holding the original trade to 15:00 would have lost ≈ −₹4,121, worse than the stop taken. The miss existed only inside the spike; capturing it needed a re-entry with its own fast exit, not a wider stop.
- **The fix:** BANK-EVE-06 pre-registered tonight (re-entry after a stopped leg on a post-12:00 re-cross of the morning range extreme, plus an afternoon day-range-break sleeve after 12:30; G0 exits, max one re-entry/day, segment day-cap governs). NOT SCORED tonight — the Jan–Oct afternoon-reclaim population is not built, so no number is quoted and no gate verdict exists; the Nov 3 counterfactual above is the recorded evidence. Status: PROPOSED (pre-registered in the registry).
- **Lesson ID:** RSI-BANK-003

## 2026-11-04 · BANKNIFTY · CE 55900 · PRIMARY

- **Strategy in play:** NS1 second leg, BNF-PAPER-V1 primary (B2 base produced no leg today — see comparison). TUNED SHADOW BOOK v2 live from today; SHADOW v22 NOT_COMPUTED today (see comparison).
- **Basis for the trade (why this trade, why then):** NS1 second-leg rule — the S1 base leg exited by stop at 09:35 (exit bar ≤13:30), and the first fresh opening-range crossing after that exit came at 13:35 on the CE side. Room ratio was infinite (no prior-day level above the crossing close), the day bias was neutral so the CE was not blocked, and the signal was ≤14:30 — all frozen NS1 conditions met. Entry at the open of the next bar, 13:40, in the 55900 CE (expiry 2026-11-23), premium verified from Upstox intraday option candles at EOD per the log row. PDH/PDC/PDL exact values: n/a — not recorded in the EOD log row; not invented here.
- **Market context at entry:** Neutral-bias day; the base leg had stopped out in the morning (09:35) and spot then crossed the opening range upward in the early afternoon — a late second leg, more than four hours after the base exit. Other systems today: (lA) v2 confirmer never broke the OR low 09:30–11:30; V5 v2 had no candidates (Skill candle filtered: CE close ≥ PDH); Volrix (b) prev-day change +0.98% > −1.0%, no trigger.
- **Entry:** 13:40 @ ₹757.00 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹707.00 (−50) · target ₹847.00 (+90) · square-off 15:10
- **What actually happened:** premium ticked up on the entry bar to a high of 781.60 (MFE +24.6 pts at 13:40) and never developed further — 13:45 high 769.15, 13:50 high 738.40, 13:55 high 744.50 — then the 14:00 bar broke down (low 672.00) through the stop. MAE −50 pts (full stop; the bar's low overshot to −85 but the frozen fill is at the stop level).
- **Exit:** 14:00 @ ₹707.00 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points on the premium) · full-target? no
- **Rules followed exactly?** Yes — frozen NS1 construction, EOD log row.
- **Same-day comparison:** CONTROL U1-B2: no trade today — its only key was a Skill V3 CE solo (signal 09:30, entry 09:35), blocked by the frozen B2 rule (Skill V3 Bank CE blocked), and the control has no NS1. TUNED SHADOW v2 (live from today): took this NS1 leg identically → −₹1,720 (shadow money; full entry below — the EVE-04 lock never armed, MFE +24.6 < +30, and EVE-05 touches only B2 base PE entries before 10:30). SHADOW v22: NOT_COMPUTED today — Bank Nifty spot 5-minute candles for 2026-11-04 were unavailable at scoring time, so the day is excluded from all v22 totals, never estimated (disclosure, not a trade). B2 base (primary): no leg — the only U1 key was the blocked Skill V3 CE solo above.
- **Missed-move check (standing trigger):** after the 14:00 exit the same contract recovered — 14:25 bar high ₹795.05 (+38.05 vs the original entry) — before fading to ~₹730 by 15:20. Whether spot itself moved ≥150 pts after the exit (the trigger) is NOT_COMPUTED: the day's spot 5-minute path is not in the stored record (the same gap that made SHADOW v22 NOT_COMPUTED today). No missed-move entry is journalled on a premium-only reading; the EVE-06(a) re-entry counterfactual for today is likewise NOT_COMPUTED (its trigger is a spot close, not a premium level).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through / never-developed full stop — the OR crossing produced only a +24.6-point flicker on the entry bar and then faded straight to the full −50 stop within 20 minutes. Entry-side shape (the break itself was dead), not an exit-rule give-back: the trade never reached the +30 development mark where any lock could act.
- **Evidence:** entry 13:40 @ 757.00 → entry-bar high 781.60 (+24.6, the day's best for this trade) → highs decay 769.15 / 738.40 / 744.50 → 14:00 bar low 672.00 through the ₹707.00 stop; exit 14:00 @ 707.00. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_55900CE_2026-11-04_2026-11-23.json`), re-derived in tonight's engine script.
- **Has history seen this before?** Yes — this is the book's single largest loss shape. In the causal v21 book (Jan–Oct 2026, 99 legs): 25 of 99 legs (25.3%) were never-developed full stops (best excursion < +30 before the stop), every one −₹1,720, a combined −₹43,000; they are 25 of the book's 47 full stops (flaw cycle, 2026-11-03). In the NS1 family specifically: 16 legs, 7 full stops, of which 4 were this never-developed shape (2026-03-05, 2026-04-09, 2026-04-16, 2026-07-28) and 3 the developed→stop shape. Frame note, stated plainly: all 16 causal-book NS1 legs are PE (the v21 frame drops NS1 CE), so today's exact class — an afternoon NS1 CE — has no population in the causal book; November's live NS1 CE legs now stand at 2 (Nov 3 developed→stop, Nov 4 never-developed), both full stops.
- **The fix:** two candidates gated tonight (see registry): BANK-EVE-07 (no-development cut restricted to NS1 legs) is an exact NO-OP — the cut changed 0 of 16 NS1 legs in the flaw-cycle replay, and it would not have fired today either (today's entry-bar high +24.6 already clears its +15 check level); BANK-EVE-08 (skip NS1 legs entering at/after 13:00) GATE FAIL on net — on the causal book the only two late NS1 legs are both winners (+₹306.50 and +₹2,480.00), so the skip cuts earners (+₹83,650.50 → +₹80,864.00). The class-level fix that already exists sits in the forward frame, not in a new rule: the v21/v22 construction drops NS1 CE legs entirely, and re-admitting them was re-tested today in the aggressive tune (cycle c1c) and lost −₹7,259.50 — today's leg is a member of a population the December frame already excludes; the frozen November primary takes it by design. Status: NO FIX PROMOTED — accepted risk inside the frozen primary; the exclusion is already the December/v22 position.
- **Lesson ID:** RSI-BANK-004

## 2026-11-04 · BANKNIFTY · CE 55900 · SHADOW-TUNED v2

- **Strategy in play:** TUNED SHADOW BOOK v2 = BNF-PAPER-V1 + BANK-EVE-05 base skip (OR-break PE entries before 10:30 skipped) + BANK-EVE-04 breakeven lock on NS1 second legs only. First live day of v2.
- **Basis for the trade (why this trade, why then):** identical NS1 signal to the primary (13:35 fresh OR crossing after the 09:35 base stop exit; room ratio infinite; neutral bias). Neither v2 component touches it: EVE-05 applies only to B2 base PE entries before 10:30 (this is an NS1 CE at 13:40 — no match), and the EVE-04 lock arms only if a completed bar's high reaches entry+30 = ₹787.00.
- **Market context at entry:** same as primary — neutral-bias day, late-afternoon second leg.
- **Entry:** 13:40 @ ₹757.00 · 1 lot (30)
- **Planned exits at entry:** stop ₹707.00 (−50) · target ₹847.00 (+90) · square-off 15:10 · plus the EVE-04 lock: a completed bar's high ≥ ₹787.00 raises the stop to ₹757.00 for later bars.
- **What actually happened:** the lock never armed — the best bar high was 781.60 on the entry bar (MFE +24.6 < +30), verified bar-by-bar from the stored premium candles in tonight's engine script (`bank_segment_engine_evening_2026-11-04.py`). The trade then followed the primary's path exactly to the stop.
- **Exit:** 14:00 @ ₹707.00 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW money — never added to primary totals.
- **Rules followed exactly?** yes
- **Same-day comparison:** PRIMARY took the identical leg for the identical −₹1,720 (above). CONTROL: no trade (blocked CE solo, no NS1). SHADOW v22: NOT_COMPUTED today (spot candles unavailable at scoring time) — excluded, not estimated.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through / never-developed full stop — same event as the primary (Lesson RSI-BANK-004). The shadow's protective component (EVE-04) is built for the developed→stop shape and by construction cannot act on a trade that never develops; today is the clean demonstration of that boundary, one day after the same lock would have saved ₹1,500 on Nov 3's developed leg.
- **Evidence:** entry-bar high 781.60 vs the ₹787.00 lock threshold — the trade missed arming by 5.4 premium points, then stopped at 14:00.
- **Has history seen this before?** Yes — same counts as the primary entry: 25 never-developed stops in the causal book, 4 of them in the NS1 family; EVE-04 changed none of those 4 in its gate (its 4 changed legs were the developed shape plus one square-off).
- **The fix:** none new from the shadow's side — tonight's EVE-07 (NS1-only no-development cut) is a NO-OP and EVE-08 (late-NS1 skip) FAILED the gate; the shadow keeps v2 rules unchanged. Status: NO FIX — accepted risk, boundary of the promoted lock recorded.
- **Lesson ID:** RSI-BANK-004 (shared with the primary entry — same signal, same event)

## 2026-11-02 · BANKNIFTY · PE 54800 · SHADOW v21

- **Strategy in play:** SHADOW v21 — the RAW v21 book, unmodified (owner-directed live shadow from 2026-11-05; this day backfilled CANDLE-SCORED the same morning). Family BASE (Skill V3 component leg), segment ge400_warm, v21 segment geometry.
- **Basis for the trade (why this trade, why then):** the day's only assembled v21 leg — the Skill V3 opening-range breakdown leg (signal 10:15, first close below the OR low; entry at the next bar's open, 10:20). Raw v21 takes every assembled leg: NO EVE-05 skip (that skip exists only in SHADOW v22 and the TUNED SHADOW frames), NO EVE-04 lock. This is the same component leg the primary took today; v21's own frame admitted it independently. Levels (PDH/PDC/PDL, Red band): n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** same as the primary's entry today — OR breakdown that reversed; spot back inside the opening range within ~15 minutes.
- **Entry:** 10:20 @ ₹681.95 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹631.95 (−50) · trigger +90 (₹771.95) → lock +90 · second target +180 · square-off 15:20 (v21 segment geometry per the shadow log note)
- **What actually happened:** stopped on the next bar, identical path to the primary — exit 10:25 at the stop. MAE −50 pts; MFE n/a — no intra-trade premium path beyond entry/exit is recorded for this leg.
- **Exit:** 10:25 @ ₹631.95 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v21 money — never added to primary, TUNED SHADOW, or v22 totals. This day is v21's November forward evidence for its December judging, labelled as such.
- **Rules followed exactly?** yes — raw v21 construction, CANDLE-SCORED from stored candles.
- **Same-day comparison:** PRIMARY took the identical leg → −₹1,720 (its own entry above). CONTROL U1-B2 identical → −₹1,720 (control money). SHADOW v22: this same leg was removed by BANK-EVE-05 (pre-10:30 OR-break PE skip) and logged as a v22 EVE-05-SKIP disclosure — not a trade, no net. TUNED SHADOW BOOK did not exist yet on 2026-11-02 (v1 starts 2026-11-03).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary's leg today.
- **Evidence:** entry 10:20 @ 681.95 → stop 10:25 @ 631.95 (one bar, full −50).
- **Has history seen this before?** Yes — same count as the primary entry: 14 of 70 OR-break legs in the B2 pool stopped within ≤10 minutes (20.0%).
- **The fix:** none inside raw v21 — by the owner's design the book runs unmodified so its December judging rests on the frozen rules; the EVE-05 skip that removes this exact leg shape lives in the v22 and TUNED SHADOW frames, not here. Status: NO FIX — accepted by construction (raw-book forward evidence).
- **Lesson ID:** RSI-BANK-001 (shared with the primary/control entries — same signal, same event)

## 2026-11-04 · BANKNIFTY · PE 55800 · SHADOW v21

- **Strategy in play:** SHADOW v21 — RAW v21 book, unmodified (backfilled CANDLE-SCORED 2026-11-05). Family S3-R1, segment ge400_warm, v21 state geometry.
- **Basis for the trade (why this trade, why then):** S3-R1 state add-on leg assembled by the v21 frame (signal 09:50, entry at the next bar's open 09:55) in the 55800 PE (expiry 2026-11-23), premium from stored/served candles. The primary's frame produced no equivalent leg today (its only key was the blocked Skill V3 CE solo) — the S3 sleeve exists only in the v21/v22 frames. Levels/state detail beyond the log row: n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** morning PE leg on a day whose primary frame later fielded only a late NS1 CE; this leg ran 09:55–10:25 and was done before the primary's 13:40 entry.
- **Entry:** 09:55 @ ₹715.30 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹665.30 (−50) · trigger +90 (₹805.30) → lock at +90 · second target +180 (₹895.30) · square-off 15:20
- **What actually happened:** developed immediately — entry-bar high 775.00, a dip back to the entry area at 10:05–10:10 (lows 715.05 / 715.00; MAE −0.5 pts — it never went underwater beyond a fraction) — then ran: 10:15 high 793.20, 10:20 high 816.95, 10:25 high 828.00 (MFE +112.7 pts). The +90 trigger armed the lock at ₹805.30 and the runner stopped there on the 10:25 bar. Premium path re-derived from the stored candles (`november_shadow_data/candles_BANKNIFTY_55800PE_2026-11-04_2026-11-23.json`) in tonight's engine script.
- **Exit:** 10:25 @ ₹805.30 — RUNNER STOP (locked +90)
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? no — first target/lock captured; second target (+180) not reached · SHADOW v21 money — never added to primary, TUNED SHADOW, or v22 totals. November forward evidence for v21's December judging.
- **Rules followed exactly?** yes — raw v21 construction, CANDLE-SCORED.
- **Same-day comparison:** SHADOW v22 took the identical leg for the identical +₹2,480 (entry below — neither EVE-04 nor EVE-05 touches an S3 leg). PRIMARY: no equivalent signal — its NS1 CE 55900 stopped at 14:00 for −₹1,720. TUNED SHADOW v2 took that same NS1 leg → −₹1,720. CONTROL: no trade.

### If the trade won
- **Why it worked:** follow-through — the leg developed from the entry bar onward and never traded below entry beyond −0.5 pts; the state sleeve's morning PE entry caught the day's early downside drift and the segment geometry's +90 lock converted it before any fade. Not labelled lucky: the excursion was orderly, not a one-bar spike.
- **Give-back check:** MFE +112.7 vs +90 captured — the runner gave back 22.7 points from the 10:25 high (828.00) to the lock (805.30), which is the lock working as designed, not a leak; no exit-tuning signal from a single winner.

## 2026-11-04 · BANKNIFTY · PE 55800 · SHADOW v22

- **Strategy in play:** SHADOW v22 — v21 frame + BANK-EVE-04 (NS1-only give-back lock) + BANK-EVE-05 (pre-10:30 OR-break PE skip). Family S3-R1, segment ge400_warm.
- **Basis for the trade (why this trade, why then):** identical assembled leg to SHADOW v21 today (signal 09:50, entry 09:55, 55800 PE, expiry 2026-11-23). Neither v22 step touches it: EVE-05 removes only Skill V3-representative OR-break PE base legs before 10:30 (this is an S3 state leg), and EVE-04's lock applies only to NS1 second legs.
- **Market context at entry:** same as the v21 entry above.
- **Entry:** 09:55 @ ₹715.30 · 1 lot (30)
- **Planned exits at entry:** stop ₹665.30 (−50) · trigger +90 (₹805.30) → lock at +90 · second target +180 (₹895.30) · square-off 15:20
- **What actually happened:** identical path to v21 — MFE +112.7 (10:25 high 828.00), MAE −0.5, runner stopped at the +90 lock on the 10:25 bar.
- **Exit:** 10:25 @ ₹805.30 — RUNNER STOP (locked +90)
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? no (second target not reached) · SHADOW v22 money — never added to primary, TUNED SHADOW, or v21 totals.
- **Rules followed exactly?** yes — v22 construction, CANDLE-SCORED. Scoring note: this day was initially recorded NOT_COMPUTED on 2026-11-04 (spot candles unavailable at that scoring time) and has since been re-scored from served candles; the +₹2,480 above is the re-scored record of truth in `november_shadow_v22_bank_log.csv`.
- **Same-day comparison:** SHADOW v21 identical +₹2,480 (above). PRIMARY −₹1,720 (NS1 CE, different frame/signal). TUNED SHADOW v2 −₹1,720 (same NS1 leg as primary). CONTROL: no trade.

### If the trade won
- **Why it worked:** same as the v21 entry — orderly development from the entry bar, no real adverse excursion, +90 lock converted the move. Not lucky.
- **Give-back check:** MFE +112.7 vs +90 captured (22.7 points left beyond the lock) — by design of the segment geometry; no action.

## 2026-11-05 · BANKNIFTY · MISSED-MOVE (no trade — book flat all day)

- **What the book was doing:** flat all day — the primary took no leg (only key: Skill V3 CE solo, signal 11:15 / entry 11:20, blocked by the frozen B2 Skill-CE block; the S1 base exited by target at 11:30 and NS1 then found no fresh OR crossing ≤14:30). The TUNED SHADOW v2 frame likewise had nothing to take.
- **What was missed:** a major afternoon trend. Spot before 11:30 ranged 56,718.20–57,235.00; after 12:00 it ran from a 57,300.35 close to a day high of 57,847.65 and closed the day at 57,773.65 — +612.65 pts above the pre-11:30 high and +547.30 pts from the first midday close to the high, far beyond the 150-pt missed-move trigger. Day range 1,129.45 pts (56,718.20–57,847.65). Spot path verified tonight from the day's 75 intraday bars via the EOD construction route.
- **Why no standing candidate could have participated:** BANK-EVE-06(a) re-entry requires a prior STOPPED leg that day — today there was no stopped leg in the primary frame (the book never traded; the base's target exit is an S1-internal event, not a primary leg). BANK-EVE-06(b), the afternoon day-range-break sleeve that was the coverage attempt for exactly this shape, was gated and REJECTED on 2026-11-04 (−₹36,659.50 over 136 legs, both halves negative) — its Jan–Oct population says afternoon break entries lose as a class, however painful today looks in isolation.
- **Whipsaw honesty:** none needed on direction — the move held into the close (last bar 57,773.65 near the high); the honest cost statement is the gate's: the rejected sleeve's 136 historical legs lost −₹36,659.50, so one clean afternoon does not reopen it. A new variant would have to differ mechanically (e.g. condition on a morning target-exit base day), and no such population has been built or gated — nothing is quoted.
- **The fix:** none promoted. Recorded as the second November missed-move day (after 2026-11-03, RSI-BANK-003) and the first where the book was flat from the open rather than stopped out first — the session-coverage gap now has both shapes on record. Status: LOGGED — coverage family remains closed on gate evidence (EVE-06(b) REJECTED); any revival needs a mechanically distinct, newly built population.
- **Lesson ID:** RSI-BANK-005

## 2026-11-05 · BANKNIFTY · CE 57100 · SHADOW Skill

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow from 2026-11-05 (solo legs included; the frozen primaries' B2/C3 blocks are NOT applied). Scored 2026-11-06 morning (the scorer's state lists Skill Bank days through Nov 5); journalled tonight because this is the exact leg the frozen primary blocked that day.
- **Basis for the trade (why this trade, why then):** the day's only U1 key — Skill V3 CE solo, signal 11:15, entry at the open of the next bar, 11:20, in the 57100 CE (expiry 2026-11-23). The Skill standalone book takes every Skill V3 key by its own rules; the PRIMARY blocked this same key under the frozen B2 rule (Skill V3 Bank CE blocked). Levels: n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** late-morning entry on the day spot later ran a major afternoon trend (pre-11:30 range 56,718.20–57,235.00; day high 57,847.65, close 57,773.65 — see the RSI-BANK-005 missed-move entry for the same day).
- **Entry:** 11:20 @ ₹729.40 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹679.40 (−50) · target ₹819.40 (+90) · square-off 15:10 (G0 geometry)
- **What actually happened:** developed immediately — entry bar high 762.00 (MFE building), 11:25 bar high 819.00, and the target filled on the 11:30 bar @ ₹819.40; the 11:30 bar's own high was 869.80 (MFE +140.4 pts). MAE −4.85 pts (entry-bar low 724.55) — the trade was never meaningfully underwater. Premium path re-derived from the stored candles (`november_shadow_data/candles_BANKNIFTY_57100CE_2026-11-05_2026-11-23.json`) in tonight's engine script.
- **Exit:** 11:30 @ ₹819.40 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? yes · SHADOW Skill money — never added to primary, TUNED SHADOW, v21 or v22 totals.
- **Rules followed exactly?** yes — Skill standalone construction, CANDLE-SCORED.
- **Same-day comparison:** PRIMARY: no trade — this key was blocked by the frozen Skill-CE block (the third consecutive blocked day at that point: Nov 3, Nov 4, Nov 5). TUNED SHADOW v2: no trade (same block in its frame). SHADOW v21 / v22: Nov 5 since scored as no-trade days (assembled rows 0).

### If the trade won
- **Why it worked:** follow-through — the late-morning OR-break CE caught the start of the day's real up-move; the premium ran from entry to target in two bars with almost no adverse excursion (−4.85). Not labelled lucky: the excursion was orderly and the spot trend behind it held into the close.
- **Give-back check:** MFE +140.4 vs +90 captured — 50.4 points ran beyond the fixed G0 target. That is the fixed-target geometry working as frozen, recorded as exit-tuning evidence only; a single winner does not reopen the trailing family (gated and rejected in the 2026-11-03 BIG BUILD, adopted nowhere).
- **Blocked-block evidence note:** this win is one leg of forward evidence on the frozen CE block, not a verdict on it. The Skill standalone Bank line for Nov 2–5 stands at −₹2,680.00 over 4 trades (Nov 2 PE −₹1,720, Nov 3 CE −₹1,720, Nov 4 CE −₹1,720, Nov 5 CE +₹2,480) — the block remains net-protective on November forward evidence so far, and the Jan–Oct admission population for blocked CE solos still does not exist (BANK-EVE-10, NOT TESTABLE). Cross-reference: RSI-BANK-005 (same day's missed-move entry).

## 2026-11-06 · BANKNIFTY · MISSED-MOVE (no trade — book flat all day)

- **What the book was doing:** flat all day — the primary took no leg (only key: Skill V3 CE solo, signal 09:45 / entry 09:50, blocked by the frozen B2 Skill-CE block — the fourth consecutive day this block has fired: Nov 3 09:55/10:00, Nov 4 09:30/09:35, Nov 5 11:15/11:20, Nov 6 09:45/09:50; the S1 base exited by stop at 11:00 and NS1's first fresh OR crossing then had room_ratio 0.28 < 1.5, so the search ended per the frozen NS1 rule). The TUNED SHADOW v3 frame (first live day) likewise had nothing to take.
- **What was missed:** the month's biggest trend day so far. Spot opened 57,812.90, dipped to a day low of 57,320.80 in the opening bar, and then rose all day: pre-11:30 high 57,991.75; after 12:00 it ran from a 57,799.50 close to a day high of 59,086.00 and CLOSED at that high (last bar 15:25 close 59,086.00) — an afternoon extension of +1,094.25 pts above the morning high, far beyond the 150-pt missed-move trigger, on a 1,765.20-pt day range. Spot path verified tonight by re-running the day's EOD construction (75 bars; output reproduced the logged NS1 room_ratio 0.28 exactly).
- **Why no standing candidate could have participated:** identical structure to 2026-11-05 (RSI-BANK-005): BANK-EVE-06(a) re-entry requires a prior STOPPED primary leg that day — the book never traded (the base's 11:00 stop exit is an S1-internal event, not a primary leg, and the NS1 search itself was room-blocked); BANK-EVE-06(b), the afternoon day-range-break sleeve built for exactly this shape, was gated and REJECTED on 2026-11-04 (−₹36,659.50 over 136 legs, both halves negative).
- **Whipsaw honesty:** none needed on direction — the move held and accelerated into the close (close = day high). The honest cost statement remains the gate's: the rejected sleeve's 136 historical legs lost −₹36,659.50, so two clean afternoons (Nov 5, Nov 6) do not reopen it. The blocked Skill CE solo at 09:50 sat underneath this entire rise; its SHADOW Skill score for Nov 6 is NOT YET SCORED (scorer state through Nov 5) — excluded, never estimated; Nov 5's identical-shape leg scored +₹2,480 in the Skill book (entry above).
- **The fix:** none promoted. Recorded as the third November missed-move day (after 2026-11-03 RSI-BANK-003 and 2026-11-05 RSI-BANK-005) and the second consecutive flat-all-day one — the session-coverage flaw count is now 3. Any revival needs a mechanically distinct, newly built population (e.g. conditioned on a morning base-exit day); none has been built or gated, so nothing is quoted. Tonight's gated work attacked the NS1 treatment and the bleed overlay instead (BANK-EVE-11 PASS as a union confirmation, BANK-EVE-12 NO-OP — see the RSI log).
- **Lesson ID:** RSI-BANK-006

## 2026-11-06 · BANKNIFTY · CE 57800 · SHADOW Skill

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (solo legs included; the frozen primaries' B2/C3 blocks are NOT applied). Scored since the 2026-11-06 evening run (scorer state now lists Skill Bank days through Nov 6); journalled tonight on catch-up.
- **Basis for the trade (why this trade, why then):** the day's only U1 key — Skill V3 CE solo, signal 09:45, entry at the open of the next bar, 09:50, in the 57800 CE (expiry 2026-11-23). The Skill standalone book takes every Skill V3 key by its own rules; the PRIMARY blocked this same key under the frozen B2 rule (Skill V3 Bank CE blocked). Levels: n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** morning entry on the month's biggest trend day so far — spot opened 57,812.90 and rose all day to close at its high, 59,086.00 (see the RSI-BANK-006 missed-move entry for the same day).
- **Entry:** 09:50 @ ₹768.25 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹718.25 (−50) · target ₹858.25 (+90) · square-off 15:10 (G0 geometry)
- **What actually happened:** developed from the entry bar (high 843.70), dipped at 09:55 (low 756.75; MAE −11.5 pts), then built steadily — 10:05 high 857.00, 10:25 high 875.00 (MFE +106.75 pts) — and the target filled on the 10:25 bar. Premium path re-derived from the stored candles (`november_shadow_data/candles_BANKNIFTY_57800CE_2026-11-06_2026-11-23.json`) in tonight's engine script.
- **Exit:** 10:25 @ ₹858.25 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? yes · SHADOW Skill money — never added to primary, TUNED SHADOW, v21 or v22 totals.
- **Rules followed exactly?** yes — Skill standalone construction, CANDLE-SCORED.
- **Same-day comparison:** PRIMARY: no trade — this key was blocked by the frozen Skill-CE block (the fourth consecutive blocked day: Nov 3, Nov 4, Nov 5, Nov 6). TUNED SHADOW v3: no trade (same block in its frame; first live day of v3). SHADOW v21 / v22: Nov 6 since scored as no-trade days (assembled rows 0).

### If the trade won
- **Why it worked:** follow-through — the morning OR-break CE caught the start of an all-day uptrend that closed at its high; the premium reached target in 35 minutes with only an −11.5-pt dip. Not labelled lucky: the excursion was orderly and the spot trend behind it held all day.
- **Give-back check:** MFE +106.75 vs +90 captured — 16.75 points ran beyond the fixed G0 target; the fixed-target geometry working as frozen, recorded as exit-tuning evidence only.
- **Blocked-block evidence note:** second consecutive winner on the blocked shape. The Skill standalone Bank line for Nov 2–6 now stands at −₹200.00 over 5 trades (Nov 2 PE −₹1,720; Nov 3 CE −₹1,720; Nov 4 CE −₹1,720; Nov 5 CE +₹2,480; Nov 6 CE +₹2,480), and the blocked CE solos alone (Nov 3–6) stand at 2 wins / 2 losses, +₹1,520.00 net as standalone legs. That balances the November forward count — it does not reverse the block: the Jan–Oct admission population for blocked CE solos still does not exist (BANK-EVE-10, NOT TESTABLE) and the pooled-CE re-tests of 2026-11-04 lost (−₹11,600.50 / −₹7,259.50). Cross-reference: RSI-BANK-006 (same day's missed-move entry).

## 2026-11-09 · BANKNIFTY · PE 58900 · PRIMARY

- **Strategy in play:** B2 opening-range breakdown (Skill V3), BNF-PAPER-V1 primary; NS1 second-leg search also ran (see comparison).
- **Basis for the trade (why this trade, why then):** Skill V3 opening-range break — signal 10:40 (first close below the opening-range low per the frozen Skill V3 construction); entry at the open of the next bar, 10:45, per the frozen convention. B2 key kept: the leg is Skill V3 PE solo, but the frozen B2 drop rule removes Skill-solo legs only with entry ≤09:55 — this entry is 10:45, so it stands; the Skill V3 CE block does not apply to a PE leg. Entry premium = open of the 10:45 candle for 58900 PE (expiry 2026-11-23), verified from Upstox intraday option candles at EOD per the log row. PDH/PDC/PDL and the exact Red band: n/a — not recorded in the EOD log row; not invented here.
- **Market context at entry:** spot had gapped up (open 59,219.95 vs the prior close 58,850.65 on the EOD construction's daily record) and faded through the morning — pre-11:30 spot range 58,877.85–59,393.45; the breakdown signal came mid-morning on a day that then reversed upward and closed at its high (see the missed-move entry below). Other systems today: (lA) v2 no rescan bar ≤13:30 closed below the OR low and PDL with room/width gates; V5 v2 no candidates (Skill candle filtered: PE close ≥ PDL); Volrix (b) prev-day change −0.40% > −1.0%, no trigger.
- **Entry:** 10:45 @ ₹815.40 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · target ₹905.40 (+90) · square-off 15:10
- **What actually happened:** the trade died on its own entry bar — the 10:45 bar opened at the entry 815.40, ticked to a high of 818.75 (MFE +3.35 pts), then collapsed to a low of 734.55 (MAE −80.85 pts; the bar's low overshot the stop by 30.85 but the frozen fill is at the stop level) and closed 737.90. The stop was hit inside the entry bar itself — the fastest full stop of November. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_58900PE_2026-11-09_2026-11-23.json`), re-derived in tonight's engine script.
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points on the premium) · full-target? no
- **Rules followed exactly?** Yes — frozen EOD construction; the log row records that the stop is checked before target including on the entry bar, per G0.
- **Same-day comparison:** CONTROL U1-B2 took the identical B2 key (entry below) — same entry, same entry-bar stop, −₹1,720 (control money). TUNED SHADOW BOOK v3 took the identical leg (entry below) — its EVE-05 skip removes only OR-break PE entries before 10:30 and this entry is 10:45, so the leg stands in the shadow frame too → shadow −₹1,720. NS1 second leg: none — the S1 base exited by stop at 10:45 (exit bar ≤13:30), and the first fresh OR crossing after that exit came at 11:30 on the CE side but was blocked on a bearish-bias day, so the search ended per the frozen NS1 rule (verified tonight by re-running the EOD construction, which reproduces the block exactly). SHADOW v21 / v22: 2026-11-09 NOT YET SCORED at this run (scorer state lists scored days through Nov 6) — excluded, never estimated. SHADOW Skill: likewise not yet scored for Nov 9.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the extreme form: the OR breakdown reversed inside the entry bar itself; the premium never developed (MFE +3.35) and the same bar that filled the entry also filled the stop.
- **Evidence:** entry bar 10:45: open 815.40 / high 818.75 / low 734.55 / close 737.90; exit at the stop level 765.40 on that bar. Spot then rose all afternoon to a day high and close of 59,741.25 — the downside break was the day's wrong side within minutes.
- **Has history seen this before?** Yes — recurring, and tonight's run counted the exact sub-shape in the primary's own B2 pool (Jan–Oct 2026, `historical_proof_bank_B2_trades.csv`): of 70 OR-break legs, 14 (20.0%) stopped within ≤10 minutes (all −₹1,720), and 4 of those 14 stopped on the entry bar itself (hold 0 min: 2026-02-02 PE 09:45, 2026-05-27 PE 10:00, 2026-06-29 PE 09:35, 2026-10-07 PE 09:40 — all PE, all before 10:30). Today is November's second instance of the quick-stop class (after Nov 2's one-bar stop, RSI-BANK-001) and its first entry-bar stop; all four historical entry-bar cases entered before 10:30, so today's 10:45 entry sits outside the bucket the promoted skips (EVE-03 <10:00, EVE-05 <10:30) were built on.
- **The fix:** three no-delay skip-at-entry candidates gated tonight on the B2 pool (see registry): BANK-EVE-13 (skip OR-break PE entries before 11:00 — EVE-05's threshold widened 30 min; would have caught today) GATE PASS vs the raw B2 baseline on every leg (+₹18,731.50 → +₹18,735.50, 34 legs; quick stops 14→2; placebo +₹15,131.50 beaten) BUT NOT PROMOTED — it is dominated by the standing EVE-05 rule on the same pool (+₹28,994.50, 47 legs): the 10:30–11:00 PE OR legs it additionally skips are worth +₹10,259.00 of earners, so adopting it would give that back for a +₹4.00 gain over doing nothing. BANK-EVE-14 (skip Skill-solo OR legs before 11:00) GATE FAIL — G5 halves (H2 −₹13,565.50 < 0), net +₹19,331.50. BANK-EVE-15 (skip all OR-break entries before 11:00) GATE FAIL — net (+₹10,735.50 < baseline) and placebo (+₹23,131.50 not beaten). Status: NO FIX PROMOTED — today's shape stays accepted risk under the frozen primary and the standing shadow; the pre-11:00 window axis is now measured at three thresholds (10:00 / 10:30 / 11:00) and 10:30 stands as its peak.
- **Lesson ID:** RSI-BANK-007

## 2026-11-09 · BANKNIFTY · PE 58900 · CONTROL

- **Strategy in play:** U1-B2 control (BNF-PAPER-V1's labelled control — B2 exactly, no NS1).
- **Basis for the trade (why this trade, why then):** identical B2 key to the primary today — Skill V3 OR-breakdown, signal 10:40, entry 10:45; the control shares the B2 construction, so the same frozen rule authorised it. Levels: n/a — not recorded in the EOD log row.
- **Market context at entry:** same as primary — morning breakdown that reversed inside the entry bar; spot closed the day at its high.
- **Entry:** 10:45 @ ₹815.40 · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · target ₹905.40 (+90) · square-off 15:10
- **What actually happened:** stopped on the entry bar, same path as primary (entry-bar high 818.75, low 734.55). MFE +3.35; MAE −80.85.
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · CONTROL money — never added to primary totals.
- **Rules followed exactly?** yes
- **Same-day comparison:** primary and TUNED SHADOW v3 took the same key with the same result (entries above/below); the primary's NS1 search additionally ran and correctly produced no second leg (11:30 CE crossing blocked on a bearish-bias day).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race (same event as primary).
- **Evidence:** entry 10:45 @ 815.40 → stop on the same bar @ 765.40 (bar low 734.55).
- **Has history seen this before?** Yes — same counts as primary: 14 of 70 OR-break legs in the B2 pool stopped within ≤10 minutes (20.0%), 4 of them on the entry bar.
- **The fix:** same candidates as primary — BANK-EVE-13 PASS-but-dominated (not promoted), EVE-14 / EVE-15 GATE FAIL. The control is unchanged by design. Status: TESTED tonight.
- **Lesson ID:** RSI-BANK-007 (shared with the primary entry — same signal, same event)

## 2026-11-09 · BANKNIFTY · PE 58900 · SHADOW-TUNED v3

- **Strategy in play:** TUNED SHADOW BOOK v3 = BNF-PAPER-V1 + BANK-EVE-05 base skip (OR-break PE entries before 10:30 skipped) + BANK-EVE-04 breakeven lock on NS1 second legs only + BANK-EVE-09 (NS1 second legs entering before 10:30 skipped).
- **Basis for the trade (why this trade, why then):** identical B2 signal to the primary (Skill V3 OR-breakdown, signal 10:40, entry 10:45, 58900 PE, expiry 2026-11-23). No v3 component touches it: EVE-05 removes only OR-break PE entries before 10:30 (this entry is 10:45 — kept), EVE-04 and EVE-09 apply only to NS1 second legs (this is a B2 base leg).
- **Market context at entry:** same as primary — breakdown reversed inside the entry bar.
- **Entry:** 10:45 @ ₹815.40 · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · target ₹905.40 (+90) · square-off 15:10
- **What actually happened:** identical path to the primary — stopped on the entry bar (high 818.75, low 734.55).
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW money — never added to primary totals. Tuned-shadow MTD (v1+v2+v3 continuous line) is now −₹5,160.00 over 3 trades — its own circuit-breaker MTD leg (≤ −₹5,000) is now met; see the RSI log.
- **Rules followed exactly?** yes
- **Same-day comparison:** PRIMARY identical −₹1,720; CONTROL identical −₹1,720 (control money). SHADOW v21 / v22 / Skill: Nov 9 not yet scored — excluded.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary (Lesson RSI-BANK-007). The shadow's protective components are built for the early-entry bucket (EVE-05, <10:30) and the NS1 developed shape (EVE-04); a 10:45 base leg that dies on its entry bar is outside both by construction.
- **Evidence:** entry-bar high 818.75 vs entry 815.40 (MFE +3.35) — no lock or skip in the v3 stack could have acted.
- **Has history seen this before?** Yes — same counts as the primary entry: 14 quick OR stops in the B2 pool, 4 on the entry bar, all four entering before 10:30 (inside EVE-05's window on the historical pool; today's entry is the first November instance outside it).
- **The fix:** tonight's EVE-13 would have skipped this leg (10:45 < 11:00) and passed every gate leg vs the raw baseline, but it is dominated by the shadow's own EVE-05 component (+₹28,994.50 vs +₹18,735.50 on the same pool) and was NOT promoted; EVE-14 / EVE-15 failed. The shadow keeps v3 rules unchanged. Status: NO FIX — accepted risk, boundary of the promoted skip recorded.
- **Lesson ID:** RSI-BANK-007 (shared with the primary/control entries — same signal, same event)

## 2026-11-09 · BANKNIFTY · MISSED-MOVE (book flat after the 10:45 entry-bar stop)

- **What the book was doing:** flat from 10:45 — the primary's only leg had stopped on its entry bar, and the one route back in, the NS1 second leg, was closed by the frozen rule: the S1 base exited by stop at 10:45 and the first fresh OR crossing after it (11:30, CE side) was blocked on a bearish-bias day, ending the search. The TUNED SHADOW v3 frame shares that NS1 rule and was likewise flat.
- **What was missed:** a major uptrend on the opposite side. Spot rose from the 10:45 bar's open of 58,906.15 to a day high of 59,741.25 — which was also the close (last bar 15:25 close 59,741.25) — a rise of +835.10 pts after the last exit, and an afternoon extension of +347.80 pts above the pre-11:30 high of 59,393.45, both far beyond the 150-pt missed-move trigger. Day range 863.40 pts (58,877.85–59,741.25). Spot path verified tonight by re-running the day's EOD construction (75 bars; it reproduced the logged NS1 bearish-bias block exactly).
- **Why no standing candidate could have participated:** the NS1 CE crossing at 11:30 was the day's only re-entry-shaped signal and the frozen bearish-bias block removed it — that block is part of the frozen primary/NS1 spec, and no gated candidate tonight re-opens the bias rule (the causal NS1 population is all-PE, so a CE-bias test has no stored population, the same evidence bound as BANK-EVE-10). BANK-EVE-06(a) re-entry needs a spot close back through the morning range extreme on the STOPPED side (PE) — spot never went back down; it ran the other way. BANK-EVE-06(b) remains gate-REJECTED, and the 2026-11-08 BREAK-CAPTURE build (owner-directed) has since failed both capture variants on Bank as well (Re-entry −₹10,018.80; Hold-60 −₹14,136.80, full gate) — the standalone breakout-capture route is dead in both forms.
- **Whipsaw honesty:** none needed on direction — the move held and accelerated into the close (close = day high). The honest cost statement remains the gates': every afternoon/breakout capture population gated so far has lost as a class, so a fourth clean afternoon does not reopen them.
- **The fix:** none promoted. Recorded as the fourth November missed-move day (after 2026-11-03 RSI-BANK-003, 2026-11-05 RSI-BANK-005, 2026-11-06 RSI-BANK-006) and the first in the stopped-out-then-opposite-trend shape — the session-coverage flaw count is now 4. Tonight's gated work attacked the entry-bar-stop shape instead (EVE-13/14/15 — see the RSI log).
- **Lesson ID:** RSI-BANK-008

## 2026-11-09 · BANKNIFTY · PE 58900 · SHADOW v21

- **Strategy in play:** SHADOW v21 — the RAW v21 book, unmodified (owner-directed live shadow from 2026-11-05). Family BASE (Skill V3 component leg), segment ge400_warm, v21 segment geometry. This entry is the catch-up journal for the Nov 9 row scored on 2026-11-10 (the Nov 9 evening run had it as NOT YET SCORED — excluded then, journalled now from the written log, never estimated).
- **Basis for the trade (why this trade, why then):** the day's assembled v21 leg — the Skill V3 opening-range breakdown leg (signal 10:40, first close below the OR low; entry at the next bar's open, 10:45). Raw v21 takes every assembled leg: NO EVE-05 skip, NO EVE-04 lock. Same component leg the primary took today. Levels (PDH/PDC/PDL, Red band): n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** same as the primary's entry today — gap-up day that faded through the morning, then reversed upward and closed at its high.
- **Entry:** 10:45 @ ₹815.40 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · trigger +90 (₹905.40) → lock +90 · second target +180 (₹995.40) · square-off 15:20 (v21 segment geometry per the shadow log note)
- **What actually happened:** stopped on the entry bar itself — identical path to the primary: 10:45 bar high 818.75 (MFE +3.35), low 734.55 (MAE −80.85), exit at the stop level on that bar.
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v21 money — never added to primary, TUNED SHADOW, v22, Skill or TUNED STACK totals. This day is v21's November forward evidence for its December judging, labelled as such. SHADOW v21 November-to-date after this row: −₹960.00 · 3 trades.
- **Rules followed exactly?** yes — raw v21 construction, CANDLE-SCORED from stored candles (`november_shadow_v21_bank_log.csv`).
- **Same-day comparison:** PRIMARY identical −₹1,720; CONTROL identical −₹1,720 (control money); TUNED SHADOW v3 identical −₹1,720 (shadow money); SHADOW v22 identical −₹1,720 (its entry below); SHADOW Skill identical −₹1,720 (its entry below); TUNED STACK (v1 backfill definition) identical −₹1,720 (its entry below).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary (Lesson RSI-BANK-007).
- **Evidence:** entry bar 10:45: open 815.40 / high 818.75 / low 734.55 / close 737.90; stop filled inside the entry bar at 765.40. Spot then rose all afternoon to a day high and close of 59,741.25.
- **Has history seen this before?** Yes — same counts as the primary entry: in the B2 pool (Jan–Oct 2026) 14 of 70 OR-break legs stopped within ≤10 minutes and 4 stopped on the entry bar itself, all four entering before 10:30; today's 10:45 entry is the first November instance outside that window.
- **The fix:** none inside raw v21 — by the owner's design the book runs unmodified so its December judging rests on the frozen rules. Status: NO FIX — accepted by construction (raw-book forward evidence).
- **Lesson ID:** RSI-BANK-007 (shared with the primary/control/shadow entries — same signal, same event)

## 2026-11-09 · BANKNIFTY · PE 58900 · SHADOW v22

- **Strategy in play:** SHADOW v22 — v21 frame + BANK-EVE-04 (NS1-only give-back lock) + BANK-EVE-05 (pre-10:30 OR-break PE skip). Family BASE (Skill V3 component leg), segment ge400_warm. Catch-up journal for the Nov 9 row scored on 2026-11-10 (NOT YET SCORED at the Nov 9 evening run — excluded then, journalled now from the written log).
- **Basis for the trade (why this trade, why then):** identical assembled leg to SHADOW v21 today (signal 10:40, entry 10:45, 58900 PE, expiry 2026-11-23). Neither v22 step touches it: EVE-05 removes only OR-break PE base legs entering before 10:30 (this entry is 10:45 — kept), and EVE-04's lock applies only to NS1 second legs (this is a BASE leg, and it never developed in any case).
- **Market context at entry:** same as the v21 entry above.
- **Entry:** 10:45 @ ₹815.40 · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · trigger +90 (₹905.40) → lock +90 · second target +180 (₹995.40) · square-off 15:20
- **What actually happened:** identical path to v21 — stopped on the entry bar (high 818.75, low 734.55; MFE +3.35, MAE −80.85).
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v22 money — never added to primary, TUNED SHADOW, v21, Skill or TUNED STACK totals. SHADOW v22 November-to-date after this row: +₹760.00 · 2 trades (Nov 4 S3-R1 +₹2,480; Nov 9 −₹1,720; Nov 2 EVE-05-SKIP disclosure, not a trade).
- **Rules followed exactly?** yes — v22 construction, CANDLE-SCORED (`november_shadow_v22_bank_log.csv`).
- **Same-day comparison:** SHADOW v21 identical −₹1,720 (above). PRIMARY −₹1,720; CONTROL −₹1,720; TUNED SHADOW v3 −₹1,720; SHADOW Skill −₹1,720; TUNED STACK −₹1,720 — every Bank book took this leg and every book stopped identically; no frame's protective rule covers a 10:45 entry-bar stop.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary (Lesson RSI-BANK-007).
- **Evidence:** entry-bar high 818.75 vs entry 815.40 (MFE +3.35) — no lock or skip in the v22 stack could have acted; EVE-05's window ends at 10:30 and this entry is 10:45.
- **Has history seen this before?** Yes — same counts as the primary entry (14 quick OR stops in the B2 pool, 4 on the entry bar, all four before 10:30). On the v22 frame specifically, BANK-EVE-17 (2026-11-10) measured the surviving population: exactly ONE OR leg frozen-stopped inside its first 3 bars across Jan–Oct, and it was a genuine close-through, not a wick.
- **The fix:** BANK-EVE-17 (first-3-bars close-stop on OR legs, v22 frame) was gated on 2026-11-10 for exactly this flaw and FAILED — net below incumbent and the flaw cohort not improved (−₹1,720.00 → −₹1,826.50 on the one addressable leg). The time-window widening (EVE-13, before 11:00) passed vs the raw baseline but is dominated by EVE-05 itself and was NOT promoted. Status: NO FIX — accepted risk; close-stop geometry closed as a direction for RSI-BANK-007.
- **Lesson ID:** RSI-BANK-007 (shared — same signal, same event)

## 2026-11-09 · BANKNIFTY · PE 58900 · SHADOW Skill

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05); solo legs included, B2/C3 filters NOT applied. Geometry G0 stop-50 / target+90 / SQ 15:10. Catch-up journal for the Nov 9 row (scored in `november_shadow_skill_bank_log.csv`; the Nov 9 evening run had Skill's Nov 9 as not yet scored).
- **Basis for the trade (why this trade, why then):** the Skill V3 opening-range breakdown itself, taken standalone — signal 10:40, entry at the next bar's open 10:45, 58900 PE (expiry 2026-11-23). No B2 keep/drop rule applies in this book; the leg the primary kept is the same leg here by construction.
- **Market context at entry:** same as the primary's entry today.
- **Entry:** 10:45 @ ₹815.40 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · target ₹905.40 (+90) · square-off 15:10
- **What actually happened:** identical path — stopped on the entry bar (high 818.75, low 734.55; MFE +3.35, MAE −80.85).
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW Skill money — never added to any other book. SHADOW Skill November-to-date after this row: −₹1,920.00 · 6 trades.
- **Rules followed exactly?** yes — standalone Skill V3 construction, CANDLE-SCORED.
- **Same-day comparison:** PRIMARY / CONTROL / TUNED SHADOW v3 / SHADOW v21 / SHADOW v22 / TUNED STACK all identical −₹1,720 on this leg (each in its own entry, own money).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary (Lesson RSI-BANK-007).
- **Evidence:** entry bar 10:45: open 815.40 / high 818.75 / low 734.55 / close 737.90; stop filled on the entry bar.
- **Has history seen this before?** Yes — same B2-pool counts as the primary entry (14 quick OR stops, 4 entry-bar stops, all before 10:30 historically).
- **The fix:** none inside the standalone Skill book — it runs the skill unfiltered by design so the skill's own forward record stays honest; the filtered frames' candidates for this flaw (EVE-13 not promoted, EVE-17 GATE FAIL) are recorded in the v22 entry above. Status: NO FIX — accepted by construction.
- **Lesson ID:** RSI-BANK-007 (shared — same signal, same event)

## 2026-11-09 · BANKNIFTY · PE 58900 · TUNED STACK

- **Strategy in play:** TUNED STACK (v1 definition — RETROSPECTIVE BACKFILL row, scored_live=NO) = SHADOW v22 frame + EVE-06(a) re-entry + c4 runner extension + v1 NS3/S3 band add-ons. Producing component: **v22 frame (BASE / Skill V3 leg)** — no other stack layer fired on this leg. From Wed 2026-11-11 the live stack runs TUNED STACK v2 (v1 + BANK-EVE-19); v2 scores this day identically (the stack holds no NS1 leg today for EVE-19 to skip).
- **Basis for the trade (why this trade, why then):** identical assembled leg to SHADOW v22 today (signal 10:40, entry 10:45, 58900 PE, expiry 2026-11-23), carried by the v22 frame into the stack. c4 had nothing to extend (the leg stopped before +90, in phase 1); the EVE-06(a) re-entry trigger never fired afterwards (PE side needed an afternoon close below the morning low 58,877.85 — the lowest afternoon close was 59,085.35); no band-dropped NS3/S3 candidate existed for v1 today — each verified in the backfill report, not assumed.
- **Market context at entry:** same as the primary's entry today.
- **Entry:** 10:45 @ ₹815.40 · 1 lot (30)
- **Planned exits at entry:** stop ₹765.40 (−50) · trigger +90 (₹905.40) → lock +90 · second target +180 (₹995.40) · square-off 15:20
- **What actually happened:** identical path — stopped on the entry bar (high 818.75, low 734.55; MFE +3.35, MAE −80.85).
- **Exit:** 10:45 @ ₹765.40 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · TUNED STACK money (backfill, retrospective) — never added to primary, TUNED SHADOW, v21, v22 or Skill totals. TUNED STACK November-to-date: +₹760.00 · 2 legs, both RETROSPECTIVE backfill (scored_live=NO); live scoring under v2 starts Wed 2026-11-11.
- **Rules followed exactly?** yes — frozen stack construction, candle-scored 2026-11-10 with the v22-intermediate anchor reproduced exactly (`november_shadow_stack_bank_log.csv`).
- **Same-day comparison:** SHADOW v22 identical −₹1,720 (the frame leg itself); PRIMARY / CONTROL / TUNED SHADOW v3 / SHADOW v21 / SHADOW Skill all identical −₹1,720 on the same signal.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the primary (Lesson RSI-BANK-007).
- **Evidence:** entry-bar high 818.75 vs entry 815.40 (MFE +3.35); the stack's extra layers act only after development (+90) or on a later same-side reclaim — neither existed.
- **Has history seen this before?** Yes — same counts as the primary entry. On the stack frame, BANK-EVE-20's ablations (2026-11-10) confirm no layer addresses an entry-bar stop; the layers earn elsewhere (re-entry +₹6,119, c4 +₹5,400, v1 +₹20,502 in-book).
- **The fix:** no stack-layer fix exists for this shape; the flaw's gated candidates (EVE-13 not promoted, EVE-17 GATE FAIL) are recorded in the v22 entry above. Status: NO FIX — accepted risk, recorded for the December review.
- **Lesson ID:** RSI-BANK-007 (shared — same signal, same event)

## 2026-11-11 · BANKNIFTY · CE 60800 · PRIMARY (LEGACY FROZEN — BNF-PAPER-V1)

- **Strategy in play:** NS1 second leg, BNF-PAPER-V1 primary (frozen). From today this book is reported as LEGACY FROZEN (control line) — TUNED STACK v2 is Bank's PRIMARY-DESIGNATED book by the owner's order of 2026-11-10 ~15:53 IST; the frozen book's logging, scoring and record are unchanged by the designation.
- **Basis for the trade (why this trade, why then):** NS1 second leg — the S1 base exited by TARGET at 10:40 (exit bar ≤13:30, the eligibility condition), and the first fresh opening-range crossing after that exit came at 13:55 on the CE side (spot 13:55 bar: open 60,613.75 / close 60,752.40, crossing the OR high); room_ratio inf (no prior-day level above the crossing close), day bias bullish so the CE side was not blocked, signal 13:55 ≤14:30 — every frozen NS1 condition met, so entry at the open of the next bar, 14:00. Strike 60800 CE (expiry 2026-11-23, key NSE_FO|62323); entry premium = open of the 14:00 premium candle, verified from Upstox intraday option candles at EOD per the log row. PDH/PDC/PDL exact values: n/a — not recorded in the EOD log row; room_ratio inf is the recorded room fact; not invented here.
- **Market context at entry:** strong up day — spot opened 60,524.70, printed a day low of 60,376.10 early, ran to a day high of 61,394.30, and the S1 base had already made its target by 10:40. The NS1 signal came in the afternoon after a midday pullback (13:55 spot bar low 60,612.65), with spot closing the day at 60,792.40. B2 base today: none — the day's only U1 key was a Skill V3 CE solo (signal 09:35, entry 09:40), blocked by the frozen B2 rule (Skill V3 Bank CE blocked). Other systems: (lA) v2 confirmer never broke the OR low 09:30–11:30; V5 v2 no candidates (Skill candle filtered: CE close ≥ PDH); Volrix (b) prev-day change +1.51% > −1.0%, no trigger.
- **Entry:** 14:00 @ ₹823.10 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹773.10 (−50) · target ₹913.10 (+90) · square-off 15:10
- **What actually happened:** immediate follow-through. The entry bar (14:00) opened 823.10, ran to a high of 900.00 (MFE +76.90 on the entry bar) with a low of 805.75 (MAE −17.35 — never close to the stop), and closed 897.80. The next bar (14:05) opened 898.10 and printed a high of 942.35 (MFE +119.25) with a low of 895.10, filling the target at 913.10 on that bar. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_60800CE_2026-11-11_2026-11-23.json`), re-derived in tonight's engine run; it matches the live intraday directive (entry 823.10, target exit 913.10) exactly.
- **Exit:** 14:05 @ ₹913.10 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points on the premium) · full-target? yes
- **Rules followed exactly?** Yes — frozen EOD construction; the log row records every NS1 condition (base target exit ≤13:30, first fresh crossing, room_ratio inf, bullish bias, signal ≤14:30).
- **Same-day comparison:** CONTROL U1-B2: no trade — the control shares only the B2 base, whose only key today was the blocked CE solo, and the control carries no NS1 (per the log row). TUNED SHADOW BOOK v3 took the identical NS1 leg (entry below) → +₹2,480 (shadow money). SHADOW Skill took the day's blocked CE solo standalone → +₹2,480 (its entry below). SHADOW v21 / SHADOW v22 / TUNED STACK v2: 2026-11-11 NOT SCORED tonight — the v21-frame assembly is blocked because the Upstox daily-bar endpoint still ends at 2026-11-09, so the scorer's spot-directory prep cannot include today (intraday spot is complete: 75 bars to 15:25); the day is excluded from those books' totals, never estimated, and the scorer's catch-up re-scores it automatically once the daily bar is served (see the NC note entry below).

### If the trade won
- **Why it worked:** the basis carried it — a genuine second-leg shape: the base had already proven the up-move by exiting on target, the price pulled back midday instead of exhausting, and the 13:55 fresh OR crossing came with unlimited room above (room_ratio inf) on a bullish-bias day. The premium confirmed instantly (entry-bar high +76.90, no meaningful adverse excursion, MAE −17.35) and the target filled on the second bar. Not a lucky win: no wick-save, no stop scare — the signal, the room and the follow-through were all present. This is the legacy primary's first winning trade of November after four full stops, and its first NS1 target (Nov 3 and Nov 4 NS1 legs both stopped).
- **Give-back check:** captured the full frozen +90 target; the exit bar's high ran +29.25 beyond it (942.35 vs the 913.10 fill) and spot's post-exit high was 60,919.50 (14:05 bar) before the day faded to a 60,792.40 close — so the uncaptured overshoot was one bar's wick, not a trend the G0 geometry left behind. Recorded as exit-geometry evidence only; G0's +90 target is frozen and the runner question belongs to the v21-frame books, whose today is NC.

## 2026-11-11 · BANKNIFTY · CE 60800 · SHADOW-TUNED v3

- **Strategy in play:** TUNED SHADOW BOOK v3 = BNF-PAPER-V1 (primary frame) + BANK-EVE-05 base skip (OR-break PE entries before 10:30 skipped) + BANK-EVE-04 breakeven lock on NS1 second legs only + BANK-EVE-09 (NS1 second legs entering before 10:30 skipped).
- **Basis for the trade (why this trade, why then):** identical NS1 signal to the legacy primary (S1 base target exit 10:40; first fresh OR crossing 13:55 CE; room_ratio inf; bullish bias; entry 14:00, 60800 CE, expiry 2026-11-23). No v3 component removes it: EVE-05 and EVE-09 apply to pre-10:30 legs (this entry is 14:00), and EVE-04 modifies only the NS1 exit path (below). Scored tonight by this engine from the same premium candles the 15:20 logging used, per the engine's step 5.
- **Market context at entry:** same as the legacy primary's entry above.
- **Entry:** 14:00 @ ₹823.10 · 1 lot (30)
- **Planned exits at entry:** stop ₹773.10 (−50), rising to entry ₹823.10 for subsequent bars once a completed bar's high reaches entry+30 (EVE-04 FC-2 lock) · target ₹913.10 (+90) · square-off 15:10
- **What actually happened:** the EVE-04 lock armed on the entry bar itself (14:00 bar high 900.00 ≥ entry+30 = 853.10), so the stop for the 14:05 bar stood at breakeven 823.10 — academic, because the 14:05 bar's low was 895.10 (never near either stop) and its high 942.35 filled the +90 target. Identical path and fill to the primary.
- **Exit:** 14:05 @ ₹913.10 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? yes · SHADOW money — never added to primary totals. Tuned-shadow MTD (v1+v2+v3 continuous line) is now −₹2,680.00 over 4 trades — back above the −₹5,000 circuit-breaker MTD leg that Nov 9 had triggered.
- **Rules followed exactly?** yes
- **Same-day comparison:** LEGACY PRIMARY identical +₹2,480 (entry above — the lock changed nothing today because the trade never looked back). CONTROL: no trade. SHADOW Skill: the blocked CE solo standalone +₹2,480 (below). SHADOW v21 / v22 / TUNED STACK v2: NOT SCORED tonight (NC — see the note entry below).

### If the trade won
- **Why it worked:** same basis as the primary's leg — proven base move, fresh afternoon crossing, unlimited room, instant premium follow-through. The shadow's distinguishing component (EVE-04) armed exactly as designed but was never tested by the path; today is therefore evidence for the shared NS1 signal, not for or against the lock.
- **Give-back check:** identical to the primary — full +90 captured; +29.25 of exit-bar overshoot beyond the target, by the frozen geometry's design.

## 2026-11-11 · BANKNIFTY · CE 60700 · SHADOW Skill

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05); solo legs included, B2/C3 filters NOT applied. Geometry G0 stop-50 / target+90 / SQ 15:10. Scored tonight by the shadow scorer's `--skill-only` route (CANDLE-SCORED, `november_shadow_skill_bank_log.csv`).
- **Basis for the trade (why this trade, why then):** the Skill V3 opening-range break itself, taken standalone — signal 09:35, entry at the next bar's open 09:40, 60700 CE (expiry 2026-11-23). This is the exact key the frozen primary blocked today under the B2 rule (Skill V3 Bank CE blocked); the standalone book carries no such block, so the leg counts here by construction.
- **Market context at entry:** early up-move on a strong day (spot opened 60,524.70 and pushed through the morning range; day high 61,394.30, close 60,792.40).
- **Entry:** 09:40 @ ₹738.90 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹688.90 (−50) · target ₹828.90 (+90) · square-off 15:10
- **What actually happened:** fast development, then a choppy hold, then the target. Entry bar (09:40) high 799.25 (MFE +60.35), low 732.40 (MAE −6.50). The premium then chopped for seven bars — 09:45 high 825.75 (+86.85, just short of target), dips to 713.90 at 09:55 (MAE −25.00 overall, never near the 688.90 stop) and 730.80 at 10:05 — before the 10:25 bar (high 856.65) filled the target at 828.90. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_60700CE_2026-11-11_2026-11-23.json`).
- **Exit:** 10:25 @ ₹828.90 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points) · full-target? yes · SHADOW Skill money — never added to any other book. SHADOW Skill November-to-date after this row: +₹560.00 · 7 trades.
- **Rules followed exactly?** yes — standalone Skill V3 construction, CANDLE-SCORED.
- **Same-day comparison:** LEGACY PRIMARY / TUNED SHADOW v3: this key was blocked in both frames (frozen CE block) — no trade on this signal; both instead took the afternoon NS1 leg for +₹2,480 each in their own money. CONTROL: no trade. The blocked-CE-solo forward tally (standalone Skill) is now 3 wins / 2 losses, +₹4,000.00 net (Nov 3 −₹1,720; Nov 4 −₹1,720; Nov 5 +₹2,480; Nov 6 +₹2,480; Nov 11 +₹2,480) — recorded as December evidence; the block itself stays (BANK-EVE-10 remains NOT TESTABLE — no Jan–Oct blocked-key population exists — and the pooled-CE re-admission tests in the 2026-11-04 aggressive tune lost: c1b −₹11,600.50, c1c −₹7,259.50).

### If the trade won
- **Why it worked:** the morning OR break had real follow-through behind it on a trend day — the entry bar itself made +60.35 and, unlike November's PE-side breaks, the dips held well above the stop (worst −25.00) until the target filled. A clean win for the standalone skill, and simultaneously a data point about what the frozen block costs on strong CE mornings — one day's +₹2,480 against a Jan–Oct evidence base that says the pooled CE population loses; the tally is kept, the rule is not reopened on forward anecdotes.
- **Give-back check:** full +90 captured; the exit bar ran to 856.65 (+27.75 beyond the fill) — the standard G0 target overshoot, noted, not chased.

## 2026-11-11 · BANKNIFTY · SHADOW v21 / SHADOW v22 / TUNED STACK v2 — NOT SCORED (NC)

- **What happened:** no journal trade entries are due for these three books today because today is NOT SCORED for the v21 frame. This engine ran the shadow scorer for 2026-11-11: the Bank v22/v21 assembly aborted on its own guard — `bank_r3_setups` store lacks 2026-11-11 — because the scorer's spot-directory prep builds its day list from the Upstox daily-bar endpoint, which at scoring time still ends at 2026-11-09 (the 2026-11-11 daily bar is not yet served). The day's intraday spot is complete (75 bars, 09:15–15:25, fetched live tonight) and the primary's EOD log row exists, so this is a daily-bar publication lag, not missing market data. The TUNED STACK v2 scoring uses the same assembly machinery (its anchor is the v22 intermediate), so the stack's first live day is NC for the same reason.
- **Treatment:** 2026-11-11 is named NC / excluded for SHADOW v21, SHADOW v22 and TUNED STACK v2 — no rows written, no nets estimated, MTDs unchanged (v21 −₹960.00 · 3 trades; v22 +₹760.00 · 2 trades; TUNED STACK v2 +₹760.00 backfill / ₹0 live). No EVE-05-SKIP or EVE-19-skip disclosure can be made for today — the assembly that would produce them did not run. The 15:32 scorer re-scores any missing November day automatically once the full day is served, so these books' Nov 11 rows are expected as a catch-up (the Nov 9 rows landed the same way on Nov 10) and will be journalled then from the written logs, never back-filled from tonight's reasoning. The frozen primary-frame books (legacy, TUNED v3, Skill standalone) do not depend on that assembly and are scored normally above.

## 2026-11-11 · BANKNIFTY · SHADOW v21 / SHADOW v22 / TUNED STACK v2 — NC RESOLVED (catch-up scored)

- The 2026-11-11 NOT SCORED note above is superseded: the scorer's catch-up has landed. All three v21-frame books now hold a written 2026-11-11 row, and each is a **no-trade day** (v22 assembly 0 legs; stack: kept 0 after EVE-05/EVE-19, EVE-19 skipped 0, no re-entry trigger, no v1 events). No money was estimated at any point; the day simply enters those books as a scored flat day. TUNED STACK v2's live record therefore starts: Nov 11 flat (scored_live=YES), Nov 12 −₹1,720 (entry below).

## 2026-11-12 · BANKNIFTY · CE 61200 · PRIMARY (LEGACY FROZEN — BNF-PAPER-V1)

- **Strategy in play:** NS1 second leg, BNF-PAPER-V1 (frozen), reported as LEGACY FROZEN (control line) — TUNED STACK v2 is Bank's PRIMARY-DESIGNATED book; the frozen book's logging, scoring and record are unchanged by the designation.
- **Basis for the trade (why this trade, why then):** NS1 second leg — the S1 base exited by STOP at 12:05 (exit bar ≤13:30, the eligibility condition), and the first fresh opening-range crossing after that exit came at 12:40 on the CE side; room_ratio 2.552 (≥ the frozen 1.5 threshold), day bias neutral so the CE side was not blocked, signal 12:40 ≤14:30 — every frozen NS1 condition met, so entry at the open of the next bar, 12:45. Strike 61200 CE (expiry 2026-11-23, key NSE_FO|62339); entry premium = open of the 12:45 premium candle, verified from Upstox intraday option candles at EOD per the log row. PDH/PDC/PDL exact values: n/a — not recorded in the EOD log row; room_ratio 2.552 is the recorded room fact; not invented here.
- **Market context at entry:** the day's only B2 key was a Skill V3 CE solo (signal 09:30, entry 09:35) — blocked by the frozen B2 rule (Skill V3 Bank CE blocked), so no B2 base leg. Other systems: (lA) v2 confirmer never broke the OR low 09:30–11:30; V5 v2 no candidates (V4: no V4 signal yet; Skill candle filtered: room < 200*scale); Volrix (b) prev-day change +1.76% > −1.0%, no trigger. Full-day EOD construction from Upstox intraday spot candles (74 bars), per the log row.
- **Entry:** 12:45 @ ₹710.00 (open of entry candle, per frozen convention) · 1 lot (30)
- **Planned exits at entry:** stop ₹660.00 (−50) · target ₹800.00 (+90) · square-off 15:10
- **What actually happened:** immediate confirmation, one shallow dip, then the target. Entry bar (12:45) opened 710.00, ran to a high of 774.85 (MFE +64.85) with a low of 708.30 (MAE −1.70), closed 761.45. The 12:55 bar dipped to 700.75 (MAE −9.25 overall — never near the 660.00 stop). The 13:05 bar (high 829.30, MFE +119.30) filled the target at 800.00. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_61200CE_2026-11-12_2026-11-23.json`), re-derived in tonight's engine run; it matches the log row (entry 710.00, target exit 800.00) exactly.
- **Exit:** 13:05 @ ₹800.00 — TARGET
- **Result:** +₹2,480.00 net after ₹220 cost (+90 points on the premium) · full-target? yes · LEGACY FROZEN money. Legacy November-to-date after this row: **−₹1,920.00 · 6 trades** (four full stops, then two consecutive NS1 targets, Nov 11 and Nov 12).
- **Rules followed exactly?** Yes — frozen EOD construction; the log row records every NS1 condition (base stop exit ≤13:30, first fresh crossing, room_ratio 2.552, neutral bias, signal ≤14:30).
- **Same-day comparison:** CONTROL U1-B2: no trade — the control shares only the B2 base, whose only key today was the blocked CE solo, and the control carries no NS1. TUNED SHADOW BOOK v3 took the identical NS1 leg but its EVE-04 breakeven lock exited it at 12:55 for −₹220 (entry below — the day's one frame divergence). SHADOW Skill took the day's blocked CE solo standalone → −₹1,720 (entry below). SHADOW v21 / SHADOW v22 / TUNED STACK v2 each took an unrelated S3-R1 PE leg → −₹1,720 each (entries below).

### If the trade won
- **Why it worked:** the second-leg shape repeated yesterday's textbook form with one difference — today's S1 base exited by stop (12:05), not target, yet the fresh 12:40 crossing still came with real room (2.552) and the premium confirmed instantly (entry-bar MFE +64.85, worst excursion −9.25). Not a lucky win: no stop scare at any point. NS1's November line on this frame is now 2 targets / 2 stops (Nov 3 and Nov 4 stopped; Nov 11 and Nov 12 targeted), +₹1,520.00 for the sleeve.
- **Give-back check:** MFE +119.30 vs +90 captured — ₹29.30 of premium points ran beyond the target on the exit bar. Noted as exit-tuning evidence only; removing or raising the second target was already gate-tested on the stack frame (BANK-EVE-18, 2026-11-10) and FAILED — the cap is load-bearing there.

## 2026-11-12 · BANKNIFTY · CE 61200 · SHADOW-TUNED v3

- **Strategy in play:** TUNED SHADOW BOOK v3 (primary frame) = BNF-PAPER-V1 + BANK-EVE-05 base skip + BANK-EVE-04 NS1-only breakeven lock + BANK-EVE-09 (skip NS1 second legs entering before 10:30). Scored by this engine from the same stored premium candles as the legacy row.
- **Basis for the trade (why this trade, why then):** the identical NS1 second leg to the legacy primary (signal 12:40, entry 12:45, 61200 CE, expiry 2026-11-23). No v3 rule removes it: EVE-09's skip window ends at 10:30 (entry 12:45 — kept); EVE-05 governs B2 base legs (none today). The EVE-04 lock is the only v3 rule that acts on this leg.
- **Market context at entry:** same as the legacy entry above.
- **Entry:** 12:45 @ ₹710.00 · 1 lot (30)
- **Planned exits at entry:** stop ₹660.00 (−50) · target ₹800.00 (+90) · EVE-04 lock: once a completed bar's high reaches entry+30 (₹740.00), the stop for subsequent bars rises to entry+0 (₹710.00) · square-off 15:10
- **What actually happened:** the lock armed on the entry bar itself (12:45 high 774.85 ≥ 740.00), so the stop for the 12:50 bar onward stood at breakeven 710.00. The 12:50 bar held (low 712.25), but the 12:55 bar dipped to 700.75 — through the raised stop — and the leg exited at breakeven before the 13:05 bar ran to the +90 target. Derivation from the stored candles (`november_shadow_data/candles_BANKNIFTY_61200CE_2026-11-12_2026-11-23.json`) through tonight's gated replay, which reproduced the frozen leg, the EVE-04 gate total and the legacy row exactly before scoring this.
- **Exit:** 12:55 @ ₹710.00 — LOCK STOP (breakeven, EVE-04)
- **Result:** −₹220.00 net after ₹220 cost (0 points on the premium) · full-target? no · TUNED SHADOW money — never added to any other book. TUNED SHADOW BOOK November-to-date after this row: **−₹2,900.00 · 5 trades**.
- **Rules followed exactly?** yes — v3 construction as frozen; the divergence from the legacy book is the lock working exactly as specified, on a path it was not built for.
- **Same-day comparison:** LEGACY FROZEN took the identical leg to the full target: +₹2,480.00. The lock cost the tuned book ₹2,700.00 against the legacy frame today — the first forward instance of EVE-04 converting a target (in Jan–Oct it only ever converted stops into saves and one square-off into a cut).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** breakeven-lock whipsaw (lock stop-before-target race) — the entry was right and developed +64.85 on its first bar; the armed lock then bound at entry+0, a shallow −9.25 dip through it stopped the leg, and the target filled two bars later. The exit rule, not the entry, failed.
- **Evidence:** 12:45 bar high 774.85 (arm) / low 708.30; 12:50 low 712.25 (held); 12:55 low 700.75 ≤ 710.00 lock stop → exit 710.00; 13:05 high 829.30 ≥ 800.00 target. Legacy MAE on the same path was only −9.25 against a −50 stop.
- **Has history seen this before?** Not in this exact form. Jan–Oct, EVE-04 changed 4 of the 16 v21 NS1 legs: three developed-then-fell legs saved (+₹1,500 each vs the frozen stop) and one square-off cut (−₹780) — net +₹3,720.00, which is why it passed. On the EVE-09-kept 13-leg frame, tonight's replay finds only 2 lock-changed legs (2026-02-05: frozen +₹560.00 → lock −₹220.00, a cut of the same family as today's; 2026-07-02: frozen −₹1,720.00 → lock −₹220.00, a save). A lock-converted full target is November's first instance — forward evidence against the lock's floor level, counted once, not fitted to.
- **The fix:** BANK-EVE-21 (NS1 lock floor entry−20, arm +30 unchanged) was gated tonight with the full controls in the same run (evidence: `bank_segment_engine_evening_2026-11-12.py` / `.json`). It would have kept today's leg alive (dip −9.25 > the −20 floor) and scored the target — but on Jan–Oct it totals +₹89,710.50 vs the incumbent frame's +₹89,530.50 (Δ only +₹180.00 over 2 changed legs), and the shifted-arm placebo (+60 arm, same −20 floor) reproduces the candidate total EXACTLY — the floor level is not what does the work. **Status: GATE FAIL (placebo leg) → TUNED SHADOW BOOK stays v3, lock unchanged.** Never retest the −20 floor identically; a future variant in this family must change the arm definition, not the floor.
- **Lesson ID:** RSI-BANK-009

## 2026-11-12 · BANKNIFTY · PE 61200 · SHADOW v21

- **Strategy in play:** SHADOW v21 — the RAW v21 book, unmodified (owner-directed live shadow, 2026-11-05); family S3-R1, segment ge400_warm, geometry stop-50 / trig+90 / lock+90 / tgt2+180, square-off 15:20. CANDLE-SCORED (`november_shadow_v21_bank_log.csv`). These November days are v21's forward evidence for its December judging.
- **Basis for the trade (why this trade, why then):** the v21 assembly's S3-R1 leg — signal 11:25, entry at the next bar's open 11:30, 61200 PE (expiry 2026-11-23). No EVE-04/EVE-05 step exists in this book; the leg stands exactly as the frozen v21 construction produced it.
- **Market context at entry:** midday, premium band ge400_warm (entry 841.50). The primary frame's own action today was separate (morning CE solo blocked; NS1 CE leg in the afternoon).
- **Entry:** 11:30 @ ₹841.50 · 1 lot (30)
- **Planned exits at entry:** stop ₹791.50 (−50) · trigger +90 (₹931.50) → lock +90 · second target +180 (₹1,021.50) · square-off 15:20
- **What actually happened:** no follow-through. The entry bar (11:30) reached a high of 851.95 (MFE +10.45) with a low of 811.35; the next bar (11:35) fell to a low of 785.00 and filled the stop. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_61200PE_2026-11-12_2026-11-23.json`).
- **Exit:** 11:35 @ ₹791.50 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v21 money — never added to any other book. SHADOW v21 November-to-date after this row: **−₹2,680.00 · 4 trades** (forward evidence for December judging).
- **Rules followed exactly?** yes — v21 construction, CANDLE-SCORED.
- **Same-day comparison:** SHADOW v22 and TUNED STACK v2 took the identical assembled leg for the identical −₹1,720 (entries below — neither the EVE-04/05 steps nor the stack's extra layers touch an S3-R1 leg that never develops). LEGACY FROZEN +₹2,480 (unrelated NS1 CE leg); TUNED SHADOW v3 −₹220 (same NS1 leg, lock exit); SHADOW Skill −₹1,720 (unrelated CE solo).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race — the premium never developed (MFE +10.45 against a +90 trigger) and the stop filled on the second bar.
- **Evidence:** entry bar high 851.95 vs entry 841.50 (MFE +10.45); 11:35 bar low 785.00 through the 791.50 stop; no lock, runner or add-on layer in any frame could have acted on a leg that never reached +30, let alone +90.
- **Has history seen this before?** Yes — this is the sleeve's base rate, not an anomaly. Jan–Oct S3-R1 on the v21 book (`flaw_cycle_incumbent_trades.csv`): 6 legs — 3 full stops (2026-02-23, 2026-07-06, 2026-09-30; −₹1,720 each) and 3 runner-stop wins (+₹2,480 each), net +₹2,280.00. November adds one of each (Nov 4 runner win, today a stop): the family stands 4 stops / 4 wins across Jan–Nov. The stops' entry times are scattered (09:50, 10:15, 11:30, 11:50, 12:55 is a win) — no time or geometry axis separates them on this count.
- **The fix:** NO FIX — accepted risk. The sleeve's expectancy rests on its runner wins carrying its stops at roughly even frequency, which is what both the backtest and November show; every exit-geometry direction that could be pointed at this shape has a fresh verdict on file (close-stop closed by BANK-EVE-17; tgt2 removal failed as BANK-EVE-18). No candidate is queued from this leg.
- **Lesson ID:** RSI-BANK-010

## 2026-11-12 · BANKNIFTY · PE 61200 · SHADOW v22

- **Strategy in play:** SHADOW v22 — v21 frame + EVE-04 NS1 give-back lock + EVE-05 pre-10:30 OR-PE skip (owner-directed live shadow, 2026-11-04); family S3-R1, segment ge400_warm, geometry stop-50 / trig+90 / lock+90 / tgt2+180, square-off 15:20. CANDLE-SCORED (`november_shadow_v22_bank_log.csv`).
- **Basis for the trade (why this trade, why then):** identical assembled leg to SHADOW v21 today (signal 11:25, entry 11:30, 61200 PE, expiry 2026-11-23). Neither v22 step touches it: EVE-05 removes only OR-break PE base legs entering before 10:30 (this is an S3-R1 leg entering 11:30), and EVE-04's lock applies only to NS1 second legs (this is not one, and it never developed in any case).
- **Market context at entry:** same as the v21 entry above.
- **Entry:** 11:30 @ ₹841.50 · 1 lot (30)
- **Planned exits at entry:** stop ₹791.50 (−50) · trigger +90 (₹931.50) → lock +90 · second target +180 (₹1,021.50) · square-off 15:20
- **What actually happened:** identical path to v21 — MFE +10.45 on the entry bar, stop filled on the 11:35 bar (low 785.00).
- **Exit:** 11:35 @ ₹791.50 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v22 money — never added to any other book. SHADOW v22 November-to-date after this row: **−₹960.00 · 3 trades**.
- **Rules followed exactly?** yes — v22 construction, CANDLE-SCORED.
- **Same-day comparison:** SHADOW v21 identical −₹1,720 (above); TUNED STACK v2 identical −₹1,720 (below); the primary-frame books took the unrelated NS1 CE leg (legacy +₹2,480, tuned v3 −₹220).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race — same event as the v21 entry (Lesson RSI-BANK-010).
- **Evidence:** entry-bar high 851.95 vs entry 841.50 (MFE +10.45) — no v22 step could have acted.
- **Has history seen this before?** Yes — same counts as the v21 entry (Jan–Oct S3-R1: 3 stops / 3 runner wins; November 1 stop / 1 win).
- **The fix:** NO FIX — accepted risk, per the v21 entry (RSI-BANK-010). No v22-specific rule is implicated.
- **Lesson ID:** RSI-BANK-010 (shared — same signal, same event)

## 2026-11-12 · BANKNIFTY · PE 61200 · TUNED STACK v2 (PRIMARY-DESIGNATED)

- **Strategy in play:** TUNED STACK v2 — Bank's PRIMARY-DESIGNATED book (owner order 2026-11-10): v22 frame + EVE-06(a) re-entry + c4 runner extension + v1 NS3/S3 band add-ons + BANK-EVE-19 (pre-10:30 NS1_second drop). Live scoring, scored_live=YES (`november_shadow_stack_bank_log.csv`).
- **Basis for the trade (why this trade, why then):** the v22-frame S3-R1 leg (signal 11:25, entry 11:30, 61200 PE, expiry 2026-11-23), component: v22 frame. No stack layer adds or removes it: EVE-19 governs NS1_second legs only (none in the stack today); the re-entry search needs a stopped v22 leg earlier in the day (this leg is the day's first and only); c4 and the v1 add-ons act only on development that never came.
- **Market context at entry:** same as the v21/v22 entries above.
- **Entry:** 11:30 @ ₹841.50 · 1 lot (30)
- **Planned exits at entry:** stop ₹791.50 (−50) · trigger +90 (₹931.50) → lock +90 · second target +180 (₹1,021.50) · square-off 15:20
- **What actually happened:** identical path — MFE +10.45 on the entry bar, stop filled on the 11:35 bar (low 785.00).
- **Exit:** 11:35 @ ₹791.50 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · TUNED STACK v2 money, reported on its own line only. Stack November-to-date after this row: **−₹960.00 · 3 legs** — split: RETROSPECTIVE backfill (v1 definition, scored_live=NO) +₹760.00 · 2 legs / LIVE (v2 rules, scored_live=YES) −₹1,720.00 · 1 leg (Nov 11 live: no-trade day).
- **Rules followed exactly?** yes — stack v2 live scoring as frozen; the day was scored by the shadow-scoring chain and is present in the stack ledger with scored_live=YES (this engine did not rescore it).
- **Same-day comparison:** SHADOW v21 and SHADOW v22 identical −₹1,720 (above). The stack's extra layers contributed 0 legs again today — its November live record so far is the v22 frame's record, which December judging must read as such.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race — same event as the v21/v22 entries (Lesson RSI-BANK-010).
- **Evidence:** MFE +10.45 only; the stack's layers act on development (+90), on a stopped leg's reclaim (none earlier), or on NS1 timing (not this family) — none existed.
- **Has history seen this before?** Yes — same S3-R1 counts as the v21 entry (Jan–Oct 3 stops / 3 runner wins; the stack's own Jan–Oct record carries the same sleeve).
- **The fix:** NO FIX — accepted risk (RSI-BANK-010). The stack-specific concern is different and recorded plainly: two live days in, the stack has yet to fire a single layer beyond its v22 frame (Nov 11 flat, Nov 12 frame-only leg, stopped) — that is a coverage observation for December judging, not a defect to tune tonight.
- **Lesson ID:** RSI-BANK-010 (shared — same signal, same event)

## 2026-11-12 · BANKNIFTY · CE 61300 · SHADOW Skill

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05); solo legs included, B2/C3 filters NOT applied. Geometry G0 stop-50 / target+90 / SQ 15:10. CANDLE-SCORED (`november_shadow_skill_bank_log.csv`).
- **Basis for the trade (why this trade, why then):** the Skill V3 opening-range break itself, taken standalone — signal 09:30, entry at the next bar's open 09:35, 61300 CE (expiry 2026-11-23). This is the day's only U1 key — the leg the frozen primary blocked under the Skill-CE block, taken here by construction.
- **Market context at entry:** morning OR break on the CE side; the primary frame blocked it (frozen rule), the v21-frame books did not assemble it, and the primary's traded leg came hours later (NS1, 12:45).
- **Entry:** 09:35 @ ₹723.40 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹673.40 (−50) · target ₹813.40 (+90) · square-off 15:10
- **What actually happened:** an early pop, then a long decay. Entry bar (09:35) high 760.00 (MFE +36.60), low 701.30. The premium chopped for six bars (dips to 688.60 at 09:45 and 722.60 at 10:05, a recovery high of 770.00 at 10:15 never threatened the target) and the 10:10 bar's low of 671.05 filled the stop. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_61300CE_2026-11-12_2026-11-23.json`).
- **Exit:** 10:10 @ ₹673.40 — STOP
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW Skill money — never added to any other book. SHADOW Skill November-to-date after this row: **−₹1,160.00 · 8 trades**.
- **Rules followed exactly?** yes — standalone Skill construction, CANDLE-SCORED.
- **Same-day comparison:** the frozen primary, control and TUNED v3 frames all blocked this key (no trade on it); the v21-frame books took the unrelated S3-R1 PE leg (−₹1,720 each). Blocked-CE-solo forward tally after today: **3 wins / 3 losses, +₹2,280.00 net standalone** (Nov 3 −₹1,720; Nov 4 −₹1,720; Nov 5 +₹2,480; Nov 6 +₹2,480; Nov 11 +₹2,480; Nov 12 −₹1,720).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop — the break developed +36.60 on its entry bar, never built on it, and decayed through the stop over 35 minutes.
- **Evidence:** entry-bar high 760.00 (MFE +36.60) vs the +90 target never approached again (best later high 770.00 at 10:15, after the stop had already filled at 10:10); MAE −52.35 excursion on the exit bar (low 671.05 vs the 673.40 stop fill).
- **Has history seen this before?** Yes — the blocked-CE-solo class is now 3W/3L in November forward evidence. In Jan–Oct the class has no stored population at all (the frozen B2 rule kept none of them, so they were never logged as trades) — BANK-EVE-10 remains NOT TESTABLE, and the pooled-CE re-admissions tested on 2026-11-04 lost (c1b −₹11,600.50; c1c −₹7,259.50).
- **The fix:** NO FIX — accepted risk. The frozen CE block stays; a balanced 3W/3L forward tally at +₹2,280.00 over six legs is December evidence, not a rule change, and no gateable population exists to test admission on.
- **Lesson ID:** RSI-BANK-011

## 2026-11-13 · BANKNIFTY · PE 60800 · SHADOW v21

- **Strategy in play:** SHADOW v21 — the RAW v21 book, unmodified (owner-directed live shadow, 2026-11-05); family NS3_gapclass, rep NS3_NS3-GD, segment own, geometry stop-50 / trig+90 / lock+50 / tgt2+150, square-off 15:20. CANDLE-SCORED (`november_shadow_v21_bank_log.csv`). These November days are v21's forward evidence for its December judging.
- **Basis for the trade (why this trade, why then):** the v21 assembly's NS3 gap-class leg — signal 12:15, entry at the next bar's open 12:20, 60800 PE (expiry 2026-11-23). No EVE-04/EVE-05 step exists in this book; the leg stands exactly as the frozen v21 construction produced it. Levels/state detail beyond the log row: n/a — not recorded in the shadow log row; not invented here.
- **Market context at entry:** midday PE leg on a range day for the primary frame (spot day range 60,780.55–61,300.55; the opening bar was the day high). The primary frame itself had no key at all today.
- **Entry:** 12:20 @ ₹705.00 (open of entry candle) · 1 lot (30)
- **Planned exits at entry:** stop ₹655.00 (−50) · trigger +90 (₹795.00) → lock +50 (₹755.00) · second target +150 (₹855.00) · square-off 15:20
- **What actually happened:** the trade died on its own entry bar — the 12:20 bar opened at the entry 705.00, never traded above it (high 705.00; MFE 0.00 pts), and collapsed to a low of 632.05 (MAE −72.95 pts; the bar's low overshot the stop by 22.95 but the frozen fill is at the stop level), closing 653.50. Premium path from the stored candles (`november_shadow_data/candles_BANKNIFTY_60800PE_2026-11-13_2026-11-23.json`).
- **Exit:** 12:20 @ ₹655.00 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v21 money — never added to any other book. SHADOW v21 November-to-date after this row: **−₹4,400.00 · 5 trades** (forward evidence for December judging).
- **Rules followed exactly?** yes — raw v21 construction, CANDLE-SCORED.
- **Same-day comparison:** SHADOW v22 and TUNED STACK v2 took the identical assembled leg for the identical −₹1,720 (entries below). LEGACY FROZEN primary: no trade today (no U1 keys at all, no S1 base, so no NS1). CONTROL: no trade. TUNED SHADOW v3: no trade (primary frame produced no leg). SHADOW Skill: no trade (no OR break 09:30–11:30).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the extreme form: the premium never developed at all (MFE 0.00) and the entry bar itself filled the stop.
- **Evidence:** entry bar 12:20: open 705.00 / high 705.00 / low 632.05 / close 653.50; exit at the stop level 655.00 on that bar. The next bar (12:25) stayed weak (high 663.10, low 611.05) — no immediate reclaim was missed.
- **Has history seen this before?** Yes as a class, first time in this exact sub-form for this family. NS3_gapclass on the causal v21 book (Jan–Oct 2026, `bank_engine_r6_v21_trades.csv`): 15 legs, net +₹13,155.00 — 8 full stops (−₹1,720 each), 6 runner targets (+₹4,280 each) and 1 square-off (+₹1,235.00). None of the 15 stopped on its entry bar (the fastest historical NS3 stops exited on the next bar); today is the family's first entry-bar stop in the stored record. The sleeve's expectancy rests on its runner targets carrying its stops, which is what Jan–Oct shows.
- **The fix:** NO FIX — accepted risk, and tonight no candidate may be opened in any case: the owner's 2026-11-13 settlement ("Keep whatever is running… Let it run") makes the segment engines SCORE-ONLY from tonight — no new variants, exits or filters on these streams. Status: LOGGED, no tuning.
- **Lesson ID:** RSI-BANK-012

## 2026-11-13 · BANKNIFTY · PE 60800 · SHADOW v22

- **Strategy in play:** SHADOW v22 — v21 frame + BANK-EVE-04 (NS1-only give-back lock) + BANK-EVE-05 (pre-10:30 OR-break PE skip); family NS3_gapclass, rep NS3_NS3-GD, segment own, geometry stop-50 / trig+90 / lock+50 / tgt2+150, square-off 15:20. CANDLE-SCORED (`november_shadow_v22_bank_log.csv`).
- **Basis for the trade (why this trade, why then):** identical assembled leg to SHADOW v21 today (signal 12:15, entry 12:20, 60800 PE, expiry 2026-11-23). Neither v22 step touches it: EVE-05 removes only OR-break PE base legs entering before 10:30 (this is an NS3 leg entering 12:20), and EVE-04's lock applies only to NS1 second legs (this is not one, and it never developed in any case).
- **Market context at entry:** same as the v21 entry above.
- **Entry:** 12:20 @ ₹705.00 · 1 lot (30)
- **Planned exits at entry:** stop ₹655.00 (−50) · trigger +90 (₹795.00) → lock +50 (₹755.00) · second target +150 (₹855.00) · square-off 15:20
- **What actually happened:** identical path to v21 — entry bar high 705.00 (MFE 0.00), low 632.05, stop filled on the entry bar.
- **Exit:** 12:20 @ ₹655.00 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · SHADOW v22 money — never added to any other book. SHADOW v22 November-to-date after this row: **−₹2,680.00 · 4 trades**.
- **Rules followed exactly?** yes — v22 construction, CANDLE-SCORED.
- **Same-day comparison:** SHADOW v21 identical −₹1,720 (above); TUNED STACK v2 identical −₹1,720 (below); the primary-frame books took nothing today.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the v21 entry (Lesson RSI-BANK-012).
- **Evidence:** entry bar 12:20: open = high 705.00, low 632.05 — no v22 step could have acted.
- **Has history seen this before?** Yes — same counts as the v21 entry (NS3_gapclass Jan–Oct: 15 legs, 8 stops, net +₹13,155.00; no entry-bar stop before today).
- **The fix:** NO FIX — accepted risk; no v22-specific rule is implicated, and the engines are score-only from tonight under the owner's 2026-11-13 settlement.
- **Lesson ID:** RSI-BANK-012 (shared — same signal, same event)

## 2026-11-13 · BANKNIFTY · PE 60800 · TUNED STACK v2 (PRIMARY-DESIGNATED)

- **Strategy in play:** TUNED STACK v2 — Bank's PRIMARY-DESIGNATED book (owner order 2026-11-10): v22 frame + EVE-06(a) re-entry + c4 runner extension + v1 NS3/S3 band add-ons + BANK-EVE-19 (pre-10:30 NS1_second drop). Live scoring, scored_live=YES (`november_shadow_stack_bank_log.csv`), scored tonight by this engine with `bank_tuned_stack_live_score.py` — anchor OK (the v22 intermediate and the raw assembly both reproduced the written v22/v21 logs exactly for today).
- **Basis for the trade (why this trade, why then):** the v22-frame NS3_gapclass leg (signal 12:15, entry 12:20, 60800 PE, expiry 2026-11-23), component: v22 frame. No stack layer adds or removes it: EVE-19 governs NS1_second legs only (0 skipped today); the re-entry search found no trigger (no earlier stopped v22 leg to reclaim against — this leg is the day's first); c4 changed 0 legs; v1 events: none.
- **Market context at entry:** same as the v21/v22 entries above.
- **Entry:** 12:20 @ ₹705.00 · 1 lot (30)
- **Planned exits at entry:** stop ₹655.00 (−50) · trigger +90 (₹795.00) → lock +50 (₹755.00) · second target +150 (₹855.00) · square-off 15:20
- **What actually happened:** identical path — entry bar high 705.00 (MFE 0.00), low 632.05, stop filled on the entry bar.
- **Exit:** 12:20 @ ₹655.00 — STOP (entry bar)
- **Result:** −₹1,720.00 net after ₹220 cost (−50 points) · full-target? no · TUNED STACK v2 money, reported on its own line only. Stack November-to-date after this row: **−₹2,680.00 · 4 legs** — split: RETROSPECTIVE backfill (v1 definition, scored_live=NO) +₹760.00 · 2 legs / LIVE (v2 rules, scored_live=YES) −₹3,440.00 · 2 legs (Nov 11 live: no-trade day; Nov 12 −₹1,720; Nov 13 −₹1,720).
- **Rules followed exactly?** yes — stack v2 live scoring as frozen, anchor-verified in tonight's run.
- **Same-day comparison:** SHADOW v21 and SHADOW v22 identical −₹1,720 (above). The stack's extra layers contributed 0 legs again today — three live days in, its live record is still entirely its v22 frame's record (Nov 11 flat; Nov 12 and Nov 13 frame-only legs, both stopped), which December judging must read as such.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — same event as the v21/v22 entries (Lesson RSI-BANK-012).
- **Evidence:** MFE 0.00 — the stack's layers act on development (+90), on a stopped leg's later reclaim (none earlier today), or on NS1 timing (not this family); none existed.
- **Has history seen this before?** Yes — same NS3 counts as the v21 entry; on the stack's own wider Jan–Oct assembly (`bank_positive_tuning_2026-11-10_stack_trades.csv`) NS3_gapclass is 21 legs, 9 stops, net +₹26,217.00 — stops are this sleeve's base rate, carried by its runner targets.
- **The fix:** NO FIX — accepted risk (RSI-BANK-012); score-only from tonight under the owner's 2026-11-13 settlement, so no candidate is queued from this leg.
- **Lesson ID:** RSI-BANK-012 (shared — same signal, same event)
