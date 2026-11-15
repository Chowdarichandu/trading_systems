# Nifty — November 2026 paper trade journal

Every trade gets one full entry per trade_journal_TEMPLATE.md: basis, strategy, outcome, failure cause, fix.
Written nightly by the RSI engine (17:15). Paper only, real money ₹0.

---

## 2026-11-02 · NIFTY · NO TRADE — blocked solo signal (PRIMARY + CONTROL both took nothing)

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:35, would-be entry 09:40). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2 had no qualifying rescan bar, V5 v2 had no candidates, and Volrix (b) did not trigger (prev-day change +0.51% > −1.0% threshold). A reader can re-derive this from the 2026-11-02 row of `november_paper_nifty_log.csv` plus the live producer log for 2026-11-02, which shows the same four system states all day.
- **Market context at entry:** n/a — no entry. Day's only fired system was Skill V3 (CE side).
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55). No shadow book exists for Nifty, so no shadow comparison.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint: 1 of ≥2 required systems fired. This is the frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-02 row; live producer log 2026-11-02 (Skill V3 "fired" at every check; (lA) / V5 / Volrix negative at every check).
- **Has history seen this before?** Yes — confirmation binding is the book's normal state: the standing causal book holds only 35 confirmed trades across Jan–Oct 2026 (0.86/week). The solo-Skill population in the stored Jan–Oct pool is 45 legs and **every one enters after 09:55 (earliest 10:00)** — an early (≤09:55) solo Skill leg like today's has **zero instances** in the stored pool, so its outcome class cannot be backtested from stored data. The testable late solo-Skill sleeves are negative (see fix below).
- **The fix:** Candidate family NIFTY-EVE-01/02b/03b tested tonight under the full controls gate (see candidate registry): adding late solo Skill CE legs, late solo Skill PE legs, or all late solo Skill legs to the standing causal book — **all GATE FAIL** (sleeves −₹40,534.65 / −₹3,689.00 with 1 named NC / −₹44,223.65 with 1 named NC; combined books ₹13,567.35 / ₹50,413.00 / ₹9,878.35 vs incumbent ₹54,102.00). Status: **NO FIX — blocking stands as accepted design**; the early-solo slice is untestable on stored data (empty population) and is not invented around.
- **Lesson ID:** RSI-NIFTY-001, cross-referenced in `november_rsi_nifty_log.md` (2026-11-02) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-03 · NIFTY · NO TRADE — blocked solo signal, day 2 (PRIMARY + CONTROL both took nothing)

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:45, would-be entry 09:50). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: CE close ≥ PDH), and Volrix (b) did not trigger (prev-day change +1.68% > −1.0% threshold). A reader can re-derive this from the 2026-11-03 row of `november_paper_nifty_log.csv` plus the live producer log for 2026-11-03 (Skill V3 "fired" from the 09:51 check onward; (lA) / V5 / Volrix negative at every check).
- **Market context at entry:** n/a — no entry. Spot opened 23582.25, dipped to 23482.80 on the 09:15 bar, then ground steadily up all day (15:10 close 23731.75). The blocked CE direction pointed the right way on the day; direction being right is not the gate — the stored late solo-Skill sleeves are negative (2026-11-02 gate), and today's leg belongs to the early (≤09:55) slice, which has zero instances in the stored Jan–Oct pool and cannot be scored.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55); the control log `november2026_paper_nifty_u1n1_log.csv` remains header-only. No shadow book exists for Nifty, so no shadow comparison.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the second consecutive day: 1 of ≥2 required systems fired. This is the frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-03 row (full-day EOD construction from Upstox intraday spot candles, 74 bars); live producer log 2026-11-03.
- **Has history seen this before?** Yes — this is the second consecutive instance (2026-11-02 was the first, Lesson RSI-NIFTY-001). In the stored Jan–Oct pool, confirmation binding is the book's normal state (35 confirmed trades, 0.86/week), and the early solo-Skill slice remains an empty population (0 legs) — untestable, never estimated.
- **The fix:** No new fix is proposed from this instance — the solo-Skill admission family was gated and failed on 2026-11-02 (NIFTY-EVE-01/02b/03b, all FAIL) and a rejected variant is never retested identically. Tonight's tuning instead ran the standing directive queue: bleed-guard overlay (NIFTY-EVE-04, exact no-op at day granularity), a third mechanically distinct trailing form (NIFTY-EVE-05 delayed lock arm, GATE FAIL on net), and the afternoon-coverage probe (NIFTY-EVE-06, population empty — NOT TESTABLE). Status: **NO FIX — blocking stands as accepted design.**
- **Lesson ID:** RSI-NIFTY-002, cross-referenced in `november_rsi_nifty_log.md` (2026-11-03) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36)
- The book was flat all day (no exit), so the check covers the full session on Upstox 5-minute spot bars fetched tonight. Opening range (09:15–09:30): high 23628.30 / low 23482.80, width 145.50 pts. Morning high to 12:00: 23699.30 (11:55 bar). Tradable afternoon (12:00–15:10) high: 23746.25 (13:40 bar) — an extension of only **+46.95 pts beyond the morning high**, below the ≥60-pt Nifty threshold and well below the morning range. The 15:15–15:25 bars are stale/closing artefacts (flat 23731.85, then a single 23810.85 print) and were excluded.
- **Verdict: NOT a missed-move day for Nifty.** The day was one continuous grind up from the 09:15 low, not an afternoon fresh move after a flat morning. Session-coverage flaw count for Nifty stays 0; the coverage probe (EVE-06) records why no afternoon sleeve can be built from the C3 family: there are no untaken afternoon confirmed keys in the stored pool to add.

---

## 2026-11-02 · NIFTY · PE 23300 · SHADOW DEC-S1 (Component B) — candle-scored, journalled 2026-11-04 under the owner directive of 2026-11-04

- **Strategy in play:** SHADOW DEC-S1 (adopted December candidate, November forward evidence), Component B — gap fade. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Nifty gapped UP +0.73% (open 23222.30 vs prior close 23053.10 on 2026-10-30), meeting Component B's frozen trigger |gap| ≥ 0.50%; the fade takes the opposite side at the 10:05 bar: PE, ATM100 strike 23300, monthly expiry in force 2026-11-23. A reader can re-derive this from the DEC-S1 spec in `november_shadow_runs_2026-11-04.md` plus the day's spot open/prior close.
- **Market context at entry:** Gap-up morning; the fade is short-the-gap by construction.
- **Entry:** 10:05 @ ₹288.00 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹238.00 (−50) · target ₹378.00 (+90) · breakeven arm +50 → stop to entry · runner lock +60 after +90 · second target +175 · square-off 15:20
- **What actually happened:** Premium ran to a high of 347.95 at 13:40 (MFE +59.95 — the +50 breakeven arm triggered, stop rose to entry), worst point 265.00 (MAE −23.00), then decayed back to entry and was stopped at breakeven.
- **Exit:** 14:35 @ ₹288.00 — BE STOP (breakeven-armed stop at entry)
- **Result:** −₹220.00 (0.00 points — cost only) · full-target? no
- **Rules followed exactly?** Yes — frozen DEC-S1 geometry, candle-scored from the same premium candles as the shadow log.
- **Same-day comparison:** Primary NF-PAPER-C3G7 took nothing that day (blocked solo Skill CE, Lesson RSI-NIFTY-001); control U1-N1 also took nothing. SHADOW DEC-S1 is a separate labelled book; its money is never in primary figures.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** Runner/BE-armed then decayed — the leg armed its breakeven protection (+59.95 excursion) and then gave back the entire excursion to the entry stop; nothing was captured from a +59.95 move.
- **Evidence:** Premium candles for 23300 PE 2026-11-02 (`november_shadow_data/candles_NIFTY_23300PE_2026-11-02_2026-11-23.json`): high 347.95 at 13:40, exit at entry 288.00 at 14:35.
- **Has history seen this before?** Yes — DEC-S1's Jan–Oct book holds 7 be_stop legs (−₹1,540.00 total; 3 of them Component B). The wider class matters more: this leg belongs to Component B PE (gap-up fades), whose Jan–Oct population is 23 legs, net −₹11,881.75, with 8 full stops — the negative half of Component B (B CE legs: +₹45,506.50 over 26 legs).
- **The fix:** NIFTY-EVE-07 — drop Component B PE legs from the tuned form of DEC-S1 (rule diff in the candidate registry). Status: **GATE PASS (2026-11-04) → TUNED SHADOW BOOK v1 from 2026-11-05**; this leg's class is skipped there. SHADOW DEC-S1 itself stays frozen as the December candidate.
- **Lesson ID:** RSI-NIFTY-003, cross-referenced in `november_rsi_nifty_log.md` (2026-11-04) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-03 · NIFTY · PE 23600 · SHADOW DEC-S1 (Component B) — candle-scored, journalled 2026-11-04

- **Strategy in play:** SHADOW DEC-S1, Component B — gap fade. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Nifty gapped UP +0.60% (open 23582.25 vs prior close 23440.80), meeting the |gap| ≥ 0.50% trigger; fade = PE at the 10:05 bar, ATM100 strike 23600, monthly expiry in force 2026-11-23.
- **Market context at entry:** Gap-up morning that kept going — spot ground up all day (open 23582.25 → 15:10 close 23731.75), i.e. a gap-continuation day, the fade's worst environment.
- **Entry:** 10:05 @ ₹290.05 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹240.05 (−50) · target ₹380.05 (+90) · breakeven arm +50 · runner lock +60 after +90 · second target +175 · square-off 15:20
- **What actually happened:** Almost no favourable excursion — premium high 295.00 at 10:10 (MFE +4.95) — then a one-way decay as spot rose, through the stop (low 239.70 on the exit bar).
- **Exit:** 13:35 @ ₹240.05 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen DEC-S1 geometry, candle-scored.
- **Same-day comparison:** Primary took nothing (blocked solo Skill CE, Lesson RSI-NIFTY-002); control took nothing. The other DEC-S1 leg that day (Component C CE, below) made +₹3,036.50 — DEC-S1's day net was −₹433.50, labelled shadow money only.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** No follow-through — gap fade fired into a gap-continuation day: the gap-up was the start of an all-day rise, so the PE fade was opposed from entry to stop.
- **Evidence:** Spot 2026-11-03 rose steadily all session (see the 2026-11-03 primary journal entry); the PE premium's best print was +4.95 at 10:10, ten minutes after entry, and it never recovered.
- **Has history seen this before?** Yes, repeatedly — this is the recurring cause for this setup: Component B PE legs in Jan–Oct 2026 went 23 legs / −₹11,881.75 with 8 full stops (34.8% of the population); this is the 9th B-PE full stop including November. Component B CE legs over the same window: +₹45,506.50 — the fade's edge is one-sided in the stored history.
- **The fix:** NIFTY-EVE-07 — drop Component B PE legs (no gap-up fades) in the tuned form. Status: **GATE PASS (2026-11-04) → TUNED SHADOW BOOK v1 from 2026-11-05** (controlled score +₹91,168.50 → +₹103,050.25 on Jan–Oct; full gate in the registry). Under v1 this leg is skipped; SHADOW DEC-S1 (frozen December candidate) still takes it by its own rules and stays separately labelled.
- **Lesson ID:** RSI-NIFTY-004, cross-referenced in `november_rsi_nifty_log.md` (2026-11-04) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-03 · NIFTY · CE 23600 · SHADOW DEC-S1 (Component C) — candle-scored, journalled 2026-11-04

- **Strategy in play:** SHADOW DEC-S1, Component C — weekly-expiry sleeve. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** 2026-11-03 was a weekly expiry day. The U1 pool's Skill V3 key (signal 09:45, the same key the primary blocked as a solo) is re-struck under Component C on the contract expiring that day: CE, ATM100 strike 23600, expiry 2026-11-03, entered at Skill V3's own entry bar 09:50. Rule: DEC-S1 spec, Component C (admitted 09:15–11:00, unless A or B owns the key — B owned the PE key, this is the CE key).
- **Market context at entry:** Spot in an all-day up-grind (open 23582.25, rising through the morning) — the CE direction was with the day's trend.
- **Entry:** 09:50 @ ₹75.90 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹25.90 (−50) · target ₹165.90 (+90) · breakeven arm +50 · runner lock +60 after +90 · second target +175 · square-off 15:20
- **What actually happened:** The premium rose with spot and the leg was closed at 13:20 @ ₹126.00, recorded in the shadow log as square_off, capturing +50.10 points. The intraday premium path beyond entry/exit was not retained in `november_shadow_data/` for this contract, so MFE/MAE beyond the captured +50.10 are not re-derivable tonight and are not invented.
- **Exit:** 13:20 @ ₹126.00 — SQUARE-OFF (as recorded in `november_shadow_decs1_nifty_log.csv`)
- **Result:** +₹3,036.50 (+50.10 points, after ₹220 cost) · full-target? no (+90 not reached)
- **Rules followed exactly?** Yes, per the shadow log's frozen-geometry scoring; the 13:20 square_off label is the scorer's record and is reported as recorded.
- **Same-day comparison:** Primary and control took nothing (the underlying Skill key was solo for C3). DEC-S1's other leg that day (Component B PE) lost −₹3,470.00; DEC-S1 day net −₹433.50, shadow money only.

### If the trade won
- **Why it worked:** The expiry-day Skill momentum key pointed the same way as the session's one-way trend; follow-through carried the premium +50.10 points without needing the +90 target.
- **Give-back check:** Not assessable beyond the exit — the contract's intraday candle path was not retained (see above); captured +50.10 of at least +50.10. Not labelled lucky: direction, basis and trend all agreed.

---

## 2026-11-04 · NIFTY · NO TRADE — zero-key day (PRIMARY + CONTROL both took nothing); SHADOW DEC-S1 day NOT_COMPUTED

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised, and today is stronger than the two prior days: there were **no U1 legs at all**. Skill V3: no OR break 09:30–11:30; (lA) v2: confirmer never broke the OR low 09:30–11:30; V5 v2: no candidates (V4: no signal; Skill: no OR break ≤ 11:30); Volrix (b): prev-day change +1.58% > −1.0%, no trigger. Re-derivable from the 2026-11-04 row of `november_paper_nifty_log.csv` (full-day EOD construction, 74 bars).
- **Market context at entry:** n/a — no entry. Spot opened 23742.25 and made its whole morning move inside the opening-range bars themselves (09:25 close 23941.30, morning high 23946.35), then ranged inside that range for the rest of the day (15:10 close 23912.70).
- **Entry:** n/a — no entry (no key existed to confirm or block)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — no deviation; there was nothing to take.
- **Same-day comparison:** Control U1-N1 also took nothing (no keys). SHADOW DEC-S1 for 2026-11-04 is **NOT_COMPUTED** — the shadow scorer's v3 historical endpoint returned 0 spot bars at scoring time, so the day is excluded from all DEC-S1 totals and will be re-scored automatically when served; it is never estimated. (The primary's EOD construction used the intraday endpoint, which did serve the day — a different route; the discrepancy is recorded, not smoothed over.)

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why nothing fired — cause:** Zero-key day: 0 of the source systems produced a leg, so confirmation was never even the binding constraint (contrast Days 1–2, Lessons RSI-NIFTY-001/002). This is the frozen design's sparsity, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-04 row; spot bars fetched tonight via the EOD route (75 bars incl. closing artefacts).
- **Has history seen this before?** Yes — sparsity is the book's normal state (35 confirmed trades in Jan–Oct 2026, 0.86/week, so most days are no-key or no-confirmation days). Solo-system books for all four systems were gated and lost to the confirmed book in the in-sample rounds (Cycles 119–122), so "take something anyway" has already been tested and refused.
- **The fix:** **NO FIX — accepted design.** No new candidate is proposed from a zero-key day; tonight's tuning came from the DEC-S1 failure causes (Lessons RSI-NIFTY-003/004 → NIFTY-EVE-07, GATE PASS).
- **Lesson ID:** RSI-NIFTY-005, cross-referenced in `november_rsi_nifty_log.md` (2026-11-04) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36)
- The book was flat all day, so the check covers the full session on the spot bars fetched tonight. Opening range (09:15–09:30): high 23942.50 / low 23696.15, width 246.35 pts. Morning extremes to 12:00: high 23946.35 / low 23696.15. Tradable afternoon (12:00–15:10): high 23929.85 / low 23737.45 — **entirely inside the morning range, extension 0 pts on either side**, below the ≥60-pt Nifty threshold and below the morning range.
- **Verdict: NOT a missed-move day for Nifty.** The day's move happened inside the opening-range formation itself, before any frozen system's window opens; the afternoon offered no fresh move. Session-coverage flaw count for Nifty stays 0.

---

## 2026-11-05 · NIFTY · NO TRADE — blocked solo signal, day 3 of the class (PRIMARY + CONTROL both took nothing) + FIRST MISSED-MOVE DAY

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:45, would-be entry 09:50) — the third instance of this exact class (2026-11-02, 2026-11-03, today). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: CE close ≥ PDH), and Volrix (b) did not trigger (prev-day change +0.63% > −1.0% threshold). Re-derivable from the 2026-11-05 row of `november_paper_nifty_log.csv` (full-day EOD construction from Upstox intraday spot candles, 74 bars) plus the live producer log for 2026-11-05 (Skill V3 "fired" at every check; the other three systems negative at every check).
- **Market context at entry:** n/a — no entry. Spot gapped UP +1.74% (open 24378.05 vs 2026-11-04 daily close 23960.60), dipped to the 09:15 low 24296.30, then rose all day: morning high 24442.20, afternoon high 24579.90 (13:45), 15:10 close 24542.45. The blocked CE direction was right again — and today, unlike Nov 2–3, the standalone form of the leg actually paid (see the SHADOW Skill entry below): direction being right on the day is still not the gate.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a for the primary. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55); the control log `november2026_paper_nifty_u1n1_log.csv` remains header-only. TUNED SHADOW BOOK v1 (live from today, = DEC-S1 minus Component B PE legs) took nothing: the day's only DEC-S1 construction was a Component B PE leg — exactly the class v1 skips (see the DEC-S1 entry below). SHADOW Skill (separate owner-directed standalone book) DID take this key — CE 24400 @ 09:50 — and made +₹5,194.50 under G7 (journalled separately below; its money is never in primary or DEC-S1 figures).

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the third time in four days: 1 of ≥2 required systems fired. Frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-05 row; live producer log 2026-11-05.
- **Has history seen this before?** Yes — third consecutive instance of the class (Lessons RSI-NIFTY-001, RSI-NIFTY-002, today). The stored Jan–Oct pool still holds zero early (≤09:55) solo Skill legs, so the class remains untestable in-sample. November forward evidence for the standalone form now exists and is mixed-positive: the three blocked keys taken standalone (SHADOW Skill, G7) went −₹3,470.00 (Nov 2, stop), +₹2,688.75 (Nov 3, square-off) and +₹5,194.50 (today, runner square-off) = +₹4,413.25 over 3 legs. Three forward legs do not overturn the Jan–Oct gate (the testable late solo-Skill sleeves lost −₹40,534.65 / −₹44,223.65), and the frozen rule is not changed on three days — but the count is now on record and growing; if the class keeps paying standalone through November, that is December evidence, labelled as such.
- **The fix:** No new fix from the admission family — NIFTY-EVE-01/02b/03b already GATE FAIL and are never retested identically. Tonight's tuning ran on the DEC-S1/tuned frame instead (NIFTY-EVE-09/10/11, all GATE PASS — see the RSI log), and the afternoon-coverage gap is registered as NIFTY-EVE-12 (PROPOSED, population build first). Status for the blocking itself: **NO FIX — blocking stands as accepted design**, with the November standalone count tracked above.
- **Lesson ID:** RSI-NIFTY-006, cross-referenced in `november_rsi_nifty_log.md` (2026-11-05) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — TRIGGER FIRED, first time for Nifty
- The book was flat all day (no trade, no exit), so the check covers the full session on Upstox 5-minute spot bars fetched tonight (75 bars incl. closing artefacts). Opening range (09:15–09:30): high 24391.95 / low 24296.30, width 95.65 pts. Morning high to 12:00: 24442.20. Tradable afternoon (12:00–15:10) high: **24579.90 (13:45 bar) — an extension of +137.70 pts beyond the morning high**, above the ≥60-pt Nifty threshold AND above the morning range (95.65 pts). The 15:15–15:25 flat closing prints (24542.20) were excluded.
- **Verdict: MISSED-MOVE DAY for Nifty — session-coverage flaw count 0 → 1.** What the book was doing: flat — its only key (the morning Skill CE) had been blocked at 09:50 and no system fired again. Why it could not participate: the frozen C3 book has no afternoon mechanism at all — confirmation never arrived in the morning window, and the standing afternoon-addition population is empty (NIFTY-EVE-06: zero untaken confirmed afternoon keys in the stored pool). Counterfactuals on record: the blocked morning CE itself, taken standalone, captured the day (+₹5,194.50, SHADOW Skill); DEC-S1's only response to the day was the opposite trade (a gap-fade PE, NOT_COMPUTED tonight — see below). Fix path: NIFTY-EVE-12 (afternoon spot-range-break sleeve) registered PROPOSED tonight — its Jan–Oct population is not built, so no number is quoted; the population build is the next step before any scoring (Bank's version of this sleeve was gate-REJECTED, −₹36,659.50 over 136 legs, so the prior is poor and the gate, not hope, will decide).

---

## 2026-11-05 · NIFTY · CE 24400 · SHADOW Skill (standalone) — candle-scored by the shadow scorer tonight

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen primaries' B2/C3 blocks are NOT applied.
- **Basis for the trade (why this trade, why then):** The day's Skill V3 key — the same key the primary blocked as a solo: OR-break CE, signal 09:45, entry at the 09:50 bar, ATM100 strike 24400, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** Gap-up day (+1.74% open) that kept trending up all session (see the primary entry above) — the CE was with the day's trend from entry to close.
- **Entry:** 09:50 @ ₹313.20 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹263.20 (−50) · target +90 → runner lock entry+50 · second target +150 · square-off 15:10 (G7 geometry per the Skill shadow spec)
- **What actually happened:** Premium dipped first — low 271.75 on the 10:45 bar (MAE −41.45, inside the −50 stop) — then rose with spot to a high of 442.60 at 13:45 (MFE +129.40; the +90 arm fired, runner lock rose to entry+50), and held above the lock into the close.
- **Exit:** 15:10 @ ₹396.50 — RUNNER SQUARE-OFF (15:10 close of the square-off bar, as recorded in `november_shadow_skill_nifty_log.csv`)
- **Result:** +₹5,194.50 (+83.30 points, after ₹220 cost) · full-target? no (+150 not reached; +90 arm reached)
- **Rules followed exactly?** Yes — frozen Skill-shadow geometry, candle-scored from `november_shadow_data/candles_NIFTY_24400CE_2026-11-05_2026-11-23.json` (77 bars).
- **Same-day comparison:** Primary and control took nothing (the key was solo for C3 — Lesson RSI-NIFTY-006). SHADOW DEC-S1's only leg today was the opposite side (Component B PE fade, NOT_COMPUTED — below). TUNED SHADOW v1 took nothing.

### If the trade won
- **Why it worked:** The OR-break key pointed the same way as a gap-up trend day and follow-through carried spot +137.70 pts beyond the morning high in the afternoon; the premium survived an early −41.45 dip (inside the stop) and rode the trend to +129.40. Not labelled lucky: basis, direction and session trend all agreed — but it is ONE leg of a standalone book whose Jan–Oct solo-Skill sleeves failed the full gate; the win is November forward evidence for that book, nothing more.
- **Give-back check:** Captured +83.30 of +129.40 MFE — 46.10 points given back from the 13:45 peak into the 15:10 square-off; the +50 runner lock was never threatened after arming. Recorded as exit-tuning colour only; no geometry change is proposed from one leg (trailing/lock variants for Nifty have failed the gate in three distinct forms).

---

## 2026-11-05 · NIFTY · PE 24400 · SHADOW DEC-S1 (Component B) — NOT_COMPUTED tonight, excluded from all totals

- **Strategy in play:** SHADOW DEC-S1 (adopted December candidate, November forward evidence), Component B — gap fade. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Nifty gapped UP +1.74% (open 24378.05 vs prior daily close 23960.60), meeting Component B's frozen |gap| ≥ 0.50% trigger; the fade constructs the opposite side at the 10:05 bar: PE, ATM100 strike 24400, monthly expiry in force 2026-11-23. The shadow scorer constructed exactly this one leg for today (legs_constructed 1, Components A and C: none — A had no confirmed key, C is not a weekly-expiry day).
- **Scoring status:** **NOT_COMPUTED** — at tonight's scoring attempts the scorer reported premium candles unavailable for 24400 PE exp 2026-11-23, so entry/exit/result are **not recorded and never estimated**. The day is excluded from every DEC-S1 total; the scorer re-runs the day automatically once it can score it (the full scorer run is currently blocked earlier, on a Bank-side spot-store preparation assertion for 2026-11-05 — unrelated to this leg; the Skill logs for today were scored through the scorer's --skill-only route). No journal fields are fabricated for an unscored leg.
- **Same-day comparison:** TUNED SHADOW BOOK v1 skips this leg's class by its defining rule (no Component B PE legs), so v1's today is a clean no-trade regardless of how this leg eventually scores. Under TUNED SHADOW BOOK v2 (from 2026-11-06, NIFTY-EVE-11) the leg is likewise skipped.
- **Correction to the 2026-11-04 record:** the 2026-11-04 DEC-S1 day previously journalled as NOT_COMPUTED has since been **scored by the shadow scorer as a no-trade day** (Component B: no fade — gap −0.29%; Component C: not a weekly expiry day; A legs 0) and stands in `november_shadow_decs1_nifty_log.csv` as such. DEC-S1 therefore has **zero** outstanding NOT_COMPUTED days before today; 2026-11-05 is the only NC day, excluded as above.

---

## 2026-11-05 · NIFTY · PE 24400 · SHADOW DEC-S1 (Component B) — NOW SCORED (corrects the NOT_COMPUTED entry above; journalled 2026-11-06)

- **Strategy in play:** SHADOW DEC-S1 (adopted December candidate, November forward evidence), Component B — gap fade. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Nifty gapped UP +1.74% (open 24378.05 vs prior daily close 23960.60), meeting Component B's frozen |gap| ≥ 0.50% trigger; the fade takes the opposite side at the 10:05 bar: PE, ATM100 strike 24400, monthly expiry in force 2026-11-23. Re-derivable from the DEC-S1 spec in `november_shadow_runs_2026-11-04.md` plus the day's spot open/prior close. This entry replaces the NOT_COMPUTED placeholder journalled on 2026-11-05 — the scorer has since served the premium candles and scored the leg (`november_shadow_decs1_nifty_log.csv`, 2026-11-05 row, CANDLE-SCORED).
- **Market context at entry:** Gap-up morning that kept trending up all session (morning high 24442.20, afternoon high 24579.90, 15:10 close 24542.45) — a gap-continuation day, the fade's worst environment, for the second time in three days.
- **Entry:** 10:05 @ ₹273.55 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹223.55 (−50) · target ₹363.55 (+90) · breakeven arm +50 → stop to entry · runner lock +60 after +90 · second target +175 · square-off 15:20
- **What actually happened:** Small favourable excursion only — premium high 291.00 at 10:45 (MFE +17.45, never near the +50 breakeven arm) — then a one-way decay as spot rose, through the stop.
- **Exit:** 13:30 @ ₹223.55 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen DEC-S1 geometry, candle-scored from `november_shadow_data/candles_NIFTY_24400PE_2026-11-05_2026-11-23.json`.
- **Same-day comparison:** Primary and control took nothing (blocked solo Skill CE, Lesson RSI-NIFTY-006). TUNED SHADOW BOOK v1, live that day, skipped this leg's class by its defining rule (no Component B PE legs) — a clean no-trade; TUNED SHADOW BOOK v2 (from 2026-11-06) likewise skips it. SHADOW Skill took the opposite side (CE 24400, +₹5,194.50).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** No follow-through — gap fade fired into a gap-continuation day: the gap-up was the start of an all-day rise, so the PE fade was opposed from entry to stop. Identical cause to Lesson RSI-NIFTY-004 (2026-11-03).
- **Evidence:** Spot 2026-11-05 rose all session (open 24378.05 → 15:10 close 24542.45); the PE premium's best print was +17.45 at 10:45 and it never recovered.
- **Has history seen this before?** Yes, repeatedly — Component B PE legs in Jan–Oct 2026: 23 legs, −₹11,881.75, 8 full stops. November has now added a 9th (Nov 3) and a 10th (this leg) full stop, plus the Nov 2 breakeven give-back: B PE is 0-for-3 in November (−₹220.00 / −₹3,470.00 / −₹3,470.00 = −₹7,160.00). Component B CE over Jan–Oct: +₹45,506.50 — the fade's edge remains one-sided.
- **The fix:** NIFTY-EVE-07 — drop Component B PE legs in the tuned form. Status: **ALREADY FIXED in the tuned line** — GATE PASS 2026-11-04, live as TUNED SHADOW BOOK v1 from 2026-11-05 and carried into v2 from 2026-11-06; both skipped this leg. SHADOW DEC-S1 itself stays frozen as the December candidate and still takes this class by its own rules, separately labelled — its November line is the forward evidence against that class.
- **Lesson ID:** RSI-NIFTY-007, cross-referenced in `november_rsi_nifty_log.md` (2026-11-06) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-06 · NIFTY · NO TRADE — blocked solo signal, day 4 of the class (PRIMARY + CONTROL both took nothing) + MISSED-MOVE DAY #2

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:30, would-be entry 09:35) — the fourth instance of this class (2026-11-02, 2026-11-03, 2026-11-05, today). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: room < 200*scale), and Volrix (b) did not trigger (prev-day change +2.40% > −1.0% threshold). Re-derivable from the 2026-11-06 row of `november_paper_nifty_log.csv` (full-day EOD construction from Upstox intraday spot candles, 74 bars; tonight's re-run of `nov_paper_eod_2026-11-06.py` reproduced the same key and notes exactly).
- **Market context at entry:** n/a — no entry. Spot opened essentially flat (24538.20 vs prior close 24536.60, gap +0.01%), dipped to 24388.05 on the 09:15 bar, then rose all day: morning high 24702.60, afternoon high 24949.85 (15:05), 15:10 close 24938.90. The blocked CE direction was right again.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a for the primary. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55). SHADOW DEC-S1 and SHADOW Skill for 2026-11-06 are **NOT YET SCORED** at this evening run (the shadow scorer's state lists scored days through 2026-11-05) — excluded from all totals, never estimated; on the day's construction the DEC-S1 fade had no trigger (gap +0.01%) and it was not a weekly-expiry day, but the scored row is the scorer's, not this journal's. TUNED SHADOW BOOK v2 (live from today, EVE-11) therefore has no scored day yet: MTD ₹0 · 0 trades.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the fourth time in five days: 1 of ≥2 required systems fired. Frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-06 row; EOD re-run tonight reproduced the key (CE, Skill V3 only, signal 09:30, entry 09:35).
- **Has history seen this before?** Yes — fourth consecutive instance of the class (Lessons RSI-NIFTY-001, 002, 006, today). The stored Jan–Oct pool still holds zero early (≤09:55) solo Skill legs, so the class remains untestable in-sample. The November standalone count (SHADOW Skill, G7) stands at 3 scored legs, +₹4,413.25; today's standalone leg is not yet scored and is not counted.
- **The fix:** No new fix from the admission family — NIFTY-EVE-01/02b/03b already GATE FAIL and are never retested identically. Status: **NO FIX — blocking stands as accepted design**, with the November standalone count tracked as December evidence.
- **Lesson ID:** RSI-NIFTY-008, cross-referenced in `november_rsi_nifty_log.md` (2026-11-06) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — TRIGGER FIRED, second time for Nifty
- The book was flat all day, so the check covers the full session on the Upstox 5-minute spot bars from tonight's EOD re-run (75 bars incl. closing artefacts). Opening range (09:15–09:30): high 24539.20 / low 24388.05, width 151.15 pts. Morning high to 12:00: 24702.60. Tradable afternoon (12:00–15:10) high: **24949.85 (15:05 bar) — an extension of +247.25 pts beyond the morning high**, above the ≥60-pt Nifty threshold AND above the morning range (151.15 pts). The 15:15–15:25 closing prints (flat 24938.90, then a single 25030.35 print) were excluded.
- **Verdict: MISSED-MOVE DAY for Nifty — session-coverage flaw count 1 → 2.** What the book was doing: flat — its only key (the morning Skill CE) had been blocked at 09:35 and no system fired again. Why it could not participate: the frozen C3 book has no afternoon mechanism; NIFTY-EVE-12 (afternoon spot-range-break sleeve) remains PROPOSED — tonight's population check confirms no stored Jan–Oct 5-minute Nifty spot population exists in the workspace from which to build its break population (only sleeve-specific spot patches), so no gate ran and no number is quoted. The build remains the next step; Bank's version of this sleeve was gate-REJECTED (−₹36,659.50 over 136 legs), so the prior is poor.

---

## 2026-11-09 · NIFTY · PE 24800 · PRIMARY (NF-PAPER-C3G7) — FIRST primary trade of November

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner-lock50), frozen November primary. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Opening-range breakdown, confirmed. Spot sold off from the open and the 10:40 bar broke both the opening-range low (24897.85) and the previous day's low (24985.30), printing the day low 24838.75 and closing at 24845.75. Two distinct source systems fired on the same (date, PE) key — Skill V3 (OR-breakdown) and V5 v2 (fired via the Skill or_breakdown) — both signal 10:40, so the frozen C3 rule (≥2 source systems on a key) authorised the entry; representative leg V5 v2 per merge order. Entry at the earliest leg bar, 10:45; strike ATM100 24800 (spot ~24846 at entry); monthly expiry in force 2026-11-23. (lA) v2 had no qualifying rescan bar; Volrix (b) prev-day change −0.18% > −1.0%, no trigger. A reader can re-derive this entry from the frozen spec + the day's spot and premium candles alone.
- **Market context at entry:** Gap-up open (+90.05 pts vs the previous close 24986.40; open 25076.40, near the previous high 25131.85) that reversed immediately — the 09:15 bar alone ranged 25084.05–24912.45. Opening range (09:15–09:30): 25084.05 / 24897.85, width 186.20 pts. By the 10:45 entry the morning was a steady down-drift that had just printed its low on the signal bar.
- **Entry:** 10:45 @ ₹293.85 (open of the 10:45 premium candle) · 1 lot
- **Planned exits at entry:** stop ₹243.85 (−50) · first target ₹383.85 (+90) → runner lock entry+50, second target +150 · square-off 15:10
- **What actually happened:** The premium never developed. Best point (MFE) +0.25 pts — the entry bar's own high, 294.10. Spot never traded below its entry level after entry (the 10:45 bar's low was 24845.35, essentially the entry print) and chopped 24845–24960 all morning; the premium decayed bar by bar (10:50 close 268.00; last flicker 288.45 at 11:05, still below entry). Worst point (MAE) −51.35 pts on the exit bar (low 242.50). The G7 runner never armed — the premium never reached +90.
- **Exit:** 11:25 @ ₹243.85 — STOP (the 11:25 bar's low 242.50 cut the stop; spot closed that bar at 24939.60, ~93 pts above the entry spot — spot rose into the stop)
- **Result:** −₹3,470.00 (−50.00 pts on the premium, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen spec followed exactly; entry and exit verified from Upstox intraday option candles at EOD and matching the live intraday exit directive for this leg. No deviation.
- **Same-day comparison:** CONTROL U1-N1 took the identical key (see its entry below) → also −₹3,470.00 under G0 geometry; counted separately, never in primary totals. SHADOW DEC-S1 and TUNED SHADOW BOOK v2 for 2026-11-09: NOT YET SCORED (shadow scorer state through 2026-11-06) — excluded from all totals, never estimated. SHADOW Skill's Nov 9 row is likewise not yet scored: the standalone book takes Skill V3 keys, and Skill V3 fired today as part of this confirmed key, so whether and how its row lands is the scorer's to make, not this journal's.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — the confirming breakdown bar itself printed the day's low; after entry there was zero downside follow-through, spot reclaimed and chopped above the entry level, and the bought premium bled to its stop on time decay plus spot drift against the position.
- **Evidence:** Signal bar (10:40) low 24838.75 = the day's low; no later bar traded lower. Entry-bar spot low 24845.35; exit bar (11:25) spot close 24939.60. Premium path: entry 293.85, entry-bar high 294.10 (MFE +0.25), no subsequent bar high above entry (best later high 288.45 at 11:05), stop-bar low 242.50.
- **Has history seen this before?** Yes, as a class. The primary's own history is the standing causal book (Component A of the frozen DEC-S1 leg set, Jan–Oct 2026): 35 legs, 9 full stops (−₹31,230.00). The confirmed-PE subset: 25 legs, +₹56,662.75 net, with **5 full stops (20% of its legs, −₹17,350.00)** — today is the 6th forward instance of the shape. Only 1 of the 5 historical A PE stops exited within 45 minutes; today's 40-minute stop is at the fast end. Worst historical month for the book's stops: May 2026 (3 of 9). Limit, stated honestly: the frozen leg file stores no MFE, so the narrower "never developed at all" sub-shape cannot be counted in-sample — the count above is for full stops on confirmed PE legs.
- **The fix:** The time-of-day family diagnosed from today's 10:45 entry was tested tonight and **refuted** — NIFTY-EVE-14 / EVE-15 / EVE-16 (drop confirmed PE legs entering ≥10:30, resp. ≥11:00, on the standing book and on the TUNED v2 frame) all **GATE FAIL on net**: the historical late A PE legs are earners (+₹11,317.00 over 7 legs, 1 stop), so the cut removes profit, not bleed. The shape's live fix candidate is **NIFTY-EVE-17 — no-development cut** (exit at the close of the 3rd bar after entry if the running maximum premium high is still < entry+15; on today's path it would have exited 11:00 @ 280.00 for −₹1,120.25 instead of −₹3,470.00 — a counterfactual, not a score). Status: **PROPOSED, not scored** — per-leg premium paths are stored for 32 of 35 A legs; 3 named legs have no stored candle file (2026-01-23 25100 PE, 2026-10-09 22400 CE, 2026-10-21 22800 PE) and the replay must first reproduce all 35 stored exits before any number may be quoted. Tonight's loss therefore stands as **the book's known stop cost — no gate-passing fix yet**, with EVE-17 queued as the next build.
- **Lesson ID:** RSI-NIFTY-009, cross-referenced in `november_rsi_nifty_log.md` (2026-11-09) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — NOT fired today
- The book's last exit was 11:25, so the check covers 11:25–15:10 on the day's Upstox 5-minute spot bars (fetched tonight by re-running the EOD construction; 75 bars). Morning range (to 12:00): high 25084.05 / low 24838.75. Post-exit extremes: high 25060.00, low 24847.60 — **entirely inside the morning range**; the tradable afternoon (12:00–15:10) high 25038.30 (14:15) / low 24847.60 (13:15) likewise. Extension beyond the morning extremes: 0 pts either side — below the ≥60-pt threshold and below the morning range (186.20 pts).
- **Verdict: NOT a missed-move day.** Session-coverage flaw count stays **2**. The day chopped sideways after the stop; there was no afternoon trend for any sleeve to miss.

---

## 2026-11-09 · NIFTY · PE 24800 · CONTROL (U1-N1)

- **Strategy in play:** CONTROL U1-N1 (U1 pool with solo + early ≤09:55 keys dropped; G0 baseline geometry), frozen control in the same log. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** The same confirmed key as the primary (V5 v2 + Skill V3, PE, signal 10:40, entry 10:45). The control does not drop it: the key is not solo, and its entry (10:45) is after the control's 09:55 early cutoff.
- **Market context at entry:** As the primary entry above.
- **Entry:** 10:45 @ ₹293.85 · 1 lot
- **Planned exits at entry:** stop ₹243.85 (−50) · target ₹383.85 (+90) · square-off 15:10 (G0 — no runner)
- **What actually happened:** Identical premium path to the primary: MFE +0.25 (entry bar), decay all morning, stop-bar low 242.50.
- **Exit:** 11:25 @ ₹243.85 — STOP
- **Result:** −₹3,470.00 (−50.00 pts, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes.
- **Same-day comparison:** Identical to the primary to the paisa — the G7 runner never armed (the premium never reached +90), so the two geometries coincide on this path; there is no geometry lesson in today's pair, only the shared entry lesson (RSI-NIFTY-009). Control results are never added to primary totals.

---

## 2026-11-06 · NIFTY · CE 24500 · SHADOW Skill (standalone) — NOW SCORED (was NOT YET SCORED on 2026-11-06; journalled 2026-11-09)

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen C3 block is NOT applied.
- **Basis for the trade (why this trade, why then):** The day's Skill V3 key — the same key the primary blocked as a solo (Lesson RSI-NIFTY-008): OR-break CE, signal 09:30, entry at the 09:35 bar, ATM100 strike 24500, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** The month's biggest trend day so far — spot ran all session to an afternoon high of 24949.85 and the CE was with the trend.
- **Entry:** 09:35 @ ₹341.55 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹291.55 (−50) · target +90 → runner lock entry+50 · second target +150 · square-off 15:10
- **What actually happened:** The premium reached +90, arming the runner; the lock then exited at entry+50. Exact peak is not in the scored row and is not estimated.
- **Exit:** 10:50 @ ₹391.55 — RUNNER-LOCK (runner_stop)
- **Result:** +₹3,030.00 (+50.00 pts, after ₹220 cost) · full-target? yes (premium reached +90)
- **Rules followed exactly?** Yes — candle-scored by the shadow scorer under the book's frozen G7 geometry.
- **Same-day comparison:** The primary blocked this key as a solo and took nothing (₹0); the standalone book's capture is December evidence on the solo question, tracked nightly — the Jan–Oct solo-Skill sleeves all failed the full gate, and four November legs do not overturn that.

### If the trade won
- **Why it worked:** Level quality plus follow-through — a clean OR break on a genuine trend day; the runner armed quickly and the +50 lock banked the move before any give-back mattered.
- **Give-back check:** At least 40 pts were given back from the +90 arm point to the +50 lock exit by the lock's design; the exact MFE is not in the scored row, so no larger give-back is claimed. SHADOW Skill November-to-date: **4 trades, +₹7,443.25** (Nov 2 −₹3,470.00; Nov 3 +₹2,688.75; Nov 5 +₹5,194.50; Nov 6 +₹3,030.00). Nov 9: not yet scored.

---

## 2026-11-09 · NIFTY · SHADOW DEC-S1 / TUNED SHADOW BOOK v2 — day NOT YET SCORED (excluded, never estimated)

- **SHADOW DEC-S1:** No scored row exists for 2026-11-09 at this evening run (the shadow scorer's state lists scored days through 2026-11-06). The day is **excluded from all DEC-S1 totals** — not a no-trade day, not a zero. DEC-S1 November-to-date stands at **4 trades, −₹4,123.50** over scored days Nov 2–6. **Correction to the 2026-11-06 entries:** 2026-11-06 DEC-S1 has since been scored as a **no-trade day** (A legs 0; no fade — gap +0.01%; not a weekly-expiry day).
- **TUNED SHADOW BOOK v2** (DEC-S1 minus B PE / A CE / C CE): on the now-scored Nov 6 construction it had **no leg** (DEC-S1 itself held no leg that day — A legs 0, because the day's only pool key was a solo Skill CE, which does not confirm; no B fade; not a weekly-expiry day) → v2 MTD ₹0 · 0 trades over scored days through Nov 6. Its Nov 9 day is unscored with DEC-S1's and is excluded, never estimated. Whether DEC-S1's construction holds a leg on today's confirmed PE key is the scorer's row to make, not this journal's.

---

## 2026-11-09 · NIFTY · SHADOW DEC-S1 / TUNED SHADOW BOOK v2 — CORRECTION: day now scored as NO-TRADE (journalled 2026-11-10 evening)

- **SHADOW DEC-S1:** The 2026-11-09 row now exists in `november_shadow_decs1_nifty_log.csv` and is a **no-trade day**: A legs 0 (sysmap PE: Skill V3 + V5 v2 fired, but DEC-S1's own Component A construction took no leg); Component B: no fade — gap +0.36%; Component C: not a weekly-expiry day. This replaces the "NOT YET SCORED" status in the entry above — the day is a scored ₹0, not an exclusion. DEC-S1 November-to-date stands unchanged at **4 trades, −₹4,123.50** over scored days Nov 2–9.
- **TUNED SHADOW BOOK v2** (DEC-S1 minus B PE / A CE / C CE): on the scored Nov 9 construction DEC-S1 held no leg, so v2 had none either → v2 MTD **₹0 · 0 trades** over scored days through Nov 9.
- **Note on the divergence:** the frozen primary took the confirmed PE key on Nov 9 while DEC-S1's Component A construction took no leg the same day. Both rows stand as scored by their own constructions; neither is adjusted to match the other.

---

## 2026-11-09 · NIFTY · PE 24800 · SHADOW Skill (standalone) — NOW SCORED (journalled 2026-11-10 evening)

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen C3 block is NOT applied — but today Skill V3 fired as part of a confirmed key, so the standalone book and the primary hold the identical leg.
- **Basis for the trade (why this trade, why then):** The same Skill V3 OR-breakdown key as the primary entry above: signal 10:40 (spot bar broke the OR low 24897.85 and the previous day's low 24985.30, printing the day low 24838.75), entry at the 10:45 bar, ATM100 strike 24800 PE, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** As the primary entry above — gap-up open (+90.05 pts) that reversed immediately; by entry a steady down-drift that had just printed its low on the signal bar.
- **Entry:** 10:45 @ ₹293.85 (open of the 10:45 premium candle) · 1 lot
- **Planned exits at entry:** stop ₹243.85 (−50) · target ₹383.85 (+90) → runner lock entry+50, second target +150 · square-off 15:10 (G7)
- **What actually happened:** Identical contract and path to the primary: premium never developed — MFE +0.25 pts (entry bar's own high 294.10), decayed bar by bar, stop-bar low 242.50. The G7 runner never armed.
- **Exit:** 11:25 @ ₹243.85 — STOP
- **Result:** −₹3,470.00 (−50.00 pts on the premium, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — candle-scored by the shadow scorer under the book's frozen G7 geometry.
- **Same-day comparison:** PRIMARY and CONTROL took the identical leg for the identical −₹3,470.00 (entries above); SHADOW DEC-S1 and TUNED v2 held no leg that day (entry above). All four lines are counted separately, never pooled.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — the same cause as the primary's leg (shared contract, shared path): the confirming breakdown bar printed the day's low and spot never traded below its entry level again.
- **Evidence:** As the primary entry above (signal-bar low 24838.75 = day low; premium MFE +0.25; exit-bar spot close 24939.60, ~93 pts above the entry spot).
- **Has history seen this before?** This is the standalone book's first November stop on a confirmed (not solo) key; its November record is now 5 trades: Nov 2 −₹3,470.00 (stop), Nov 3 +₹2,688.75, Nov 5 +₹5,194.50, Nov 6 +₹3,030.00, Nov 9 −₹3,470.00 → **MTD +₹3,973.25**. The underlying failure shape's history is counted in the primary entry above (RSI-NIFTY-009: 5 full stops in the 25 historical confirmed-PE legs; this leg is the 6th forward instance across books, same leg counted once per book).
- **The fix:** Same as the primary's — the no-development cut diagnosed from this shape (NIFTY-EVE-17) was scored on 2026-11-10 exactly as registered and **GATE FAIL** (standing book +₹54,102.00 → +₹23,048.25; the cut fires on 21 of 35 legs and that population is net positive as traded). Status: **NO FIX — accepted risk**; EVE-17 is never retested identically.
- **Lesson ID:** RSI-NIFTY-009 (shared with the primary/control entries for this leg), cross-referenced in `november_rsi_nifty_log.md` (2026-11-09 and 2026-11-10) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-10 · NIFTY · NO TRADE — market holiday (Diwali-Balipratipada)

- **Strategy in play:** NF-PAPER-C3G7, frozen November primary; control U1-N1; SHADOW DEC-S1; TUNED SHADOW BOOK v2; SHADOW Skill.
- **Basis for the trade:** n/a — no trade was possible; the market was closed for Diwali-Balipratipada. No rows exist for 2026-11-10 in `november_paper_nifty_log.csv`, `november_shadow_decs1_nifty_log.csv` or `november_shadow_skill_nifty_log.csv`, and none are invented. This is a holiday, not a no-trade trading day: trading days elapsed stays **6**.
- **Market context at entry:** n/a — market closed.
- **Entry / Planned exits / Exit:** n/a — no position in any book.
- **Result:** ₹0 in every book · full-target? n/a
- **Rules followed exactly?** Yes — nothing taken, nothing estimated.
- **Same-day comparison:** All books flat by closure. Standings carried from the scored record: PRIMARY MTD **−₹3,470.00 · 1 trade**; SHADOW DEC-S1 MTD **−₹4,123.50 · 4 trades** (Nov 9 now scored no-trade); TUNED SHADOW BOOK v2 MTD **₹0 · 0 trades**; SHADOW Skill MTD **+₹3,973.25 · 5 trades** (Nov 9 leg journalled above).

---

## 2026-11-11 · NIFTY · NO TRADE — blocked solo signal, day 5 of the class (PRIMARY + CONTROL both took nothing) + MISSED-MOVE DAY #3 (downside)

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:40, would-be entry 09:45) — the fifth instance of this class (2026-11-02, 2026-11-03, 2026-11-05, 2026-11-06, today). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: CE close ≥ PDH), and Volrix (b) did not trigger (prev-day change +0.23% > −1.0% threshold). Re-derivable from the 2026-11-11 row of `november_paper_nifty_log.csv` (full-day EOD construction from Upstox intraday spot candles, 74 bars; tonight's re-run of the EOD construction reproduced the same key and notes exactly). Note: 2026-11-10 was a market holiday (Diwali-Balipratipada), not a trading day.
- **Market context at entry:** n/a — no entry. Spot gapped up (open 25337.80 vs the 2026-11-09 close 25044.65), made the day high 25424.35 on the 09:45 bar, then ranged 25263.80–25424.35 through the morning before breaking down in the afternoon to a 15:05/15:10 low of 25095.35. The blocked CE pointed up; the day's real move was down, in the afternoon.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a for the primary. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55). SHADOW Skill (separate standalone book) DID take this key — CE 25400 @ 09:45 — and stopped for −₹3,470.00 (journalled separately below; its money is never in primary figures). SHADOW DEC-S1 and TUNED SHADOW BOOK v2 for 2026-11-11 are **NOT YET SCORED** (the shadow scorer's state lists DEC-S1 scored days through 2026-11-09) — excluded from all totals, never estimated.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the fifth time in seven trading days: 1 of ≥2 required systems fired. Frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-11 row; tonight's EOD re-run reproduced the key (CE, Skill V3 only, signal 09:40, entry 09:45).
- **Has history seen this before?** Yes — fifth instance of the class (Lessons RSI-NIFTY-001, 002, 006, 008, today). The stored Jan–Oct pool still holds zero early (≤09:55) solo Skill legs, so the class remains untestable in-sample. The November standalone count for the blocked keys (SHADOW Skill, G7) is now 5 legs: −₹3,470.00 (Nov 2) / +₹2,688.75 (Nov 3) / +₹5,194.50 (Nov 5) / +₹3,030.00 (Nov 6) / −₹3,470.00 (today) = **+₹3,973.25 net** — still positive, but today halves the cushion; five forward legs do not overturn the Jan–Oct gate, and the frozen rule stands.
- **The fix:** No new fix from the admission family — NIFTY-EVE-01/02b/03b already GATE FAIL, NIFTY-EVE-18 is empty by construction, and a rejected variant is never retested identically. Status: **NO FIX — blocking stands as accepted design**, with the November standalone count tracked as December evidence.
- **Lesson ID:** RSI-NIFTY-010, cross-referenced in `november_rsi_nifty_log.md` (2026-11-11) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — TRIGGER FIRED, third time for Nifty, first to the downside
- The book was flat all day, so the check covers the full session on Upstox 5-minute spot bars fetched tonight (75 bars incl. closing artefacts). Opening range (09:15–09:30): high 25399.10 / low 25263.80, width 135.30 pts. Morning extremes to 12:00: high 25424.35 / low 25263.80. Tradable afternoon (12:00–15:10): high 25393.45 (no upside extension) / low **25095.35 (15:05 and 15:10 bars) — an extension of 168.45 pts beyond the morning low**, above the ≥60-pt Nifty threshold AND above the morning range (135.30 pts). The 15:15–15:25 closing prints were excluded.
- **Verdict: MISSED-MOVE DAY for Nifty — session-coverage flaw count 2 → 3.** What the book was doing: flat — its only key (the morning Skill CE) had been blocked at 09:45 and no system fired again, in either direction. Why it could not participate: the frozen C3 book has no afternoon mechanism. Fix path status: NIFTY-EVE-12 (afternoon spot-range-break sleeve, both directions) was scored under the full gate on 2026-11-10 and **GATE FAIL** decisively (standalone −₹100,604.40 / 156 legs; increment on TUNED v2 −₹109,591.65; the flipped-direction placebo beat it) — the third independent construction to reject a standalone afternoon-break entry. No new afternoon candidate is proposed from today; the flaw is recorded, the tested fix stands refuted in this form.

---

## 2026-11-11 · NIFTY · CE 25400 · SHADOW Skill (standalone) — candle-scored

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen C3 block is NOT applied.
- **Basis for the trade (why this trade, why then):** The day's Skill V3 key — the same key the primary blocked as a solo (Lesson RSI-NIFTY-010): OR-break CE, signal 09:40, entry at the 09:45 bar, ATM100 strike 25400, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** Gap-up morning that made its high on the entry bar itself (spot 25424.35 at 09:45) and then ranged all morning before breaking down in the afternoon — the CE was against the day's eventual direction.
- **Entry:** 09:45 @ ₹328.55 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹278.55 (−50) · target +90 → runner lock entry+50 · second target +150 · square-off 15:10 (G7 geometry per the Skill shadow spec)
- **What actually happened:** The premium never developed. Best point (MFE) +6.45 pts — the entry bar's own high, 335.00. It then chopped between roughly ₹285 and ₹321 all morning (never near the +90 arm, so the runner never armed), and when spot broke down after 12:10 the premium fell through the stop. Worst point (MAE) −51.80 pts on the exit bar (low 276.75).
- **Exit:** 12:15 @ ₹278.55 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen Skill-shadow geometry, candle-scored from `november_shadow_data/candles_NIFTY_25400CE_2026-11-11_2026-11-23.json`.
- **Same-day comparison:** Primary and control took nothing (the key was solo for C3 — Lesson RSI-NIFTY-010). SHADOW DEC-S1 / TUNED v2 for today: NOT YET SCORED, excluded.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — the OR-break bar printed the day high; after entry there was zero upside follow-through, spot ranged above the entry for hours (premium bleeding on decay), then broke down through the stop in the afternoon.
- **Evidence:** Signal/entry bar (09:45) spot high 25424.35 = the day's high; no later bar traded higher. Premium path: entry 328.55, entry-bar high 335.00 (MFE +6.45), no subsequent bar high above the entry bar's, stop-bar (12:15) low 276.75 below the 278.55 stop.
- **Has history seen this before?** Yes — the standalone book's November record is now 6 trades: Nov 2 −₹3,470.00 (stop), Nov 3 +₹2,688.75, Nov 5 +₹5,194.50, Nov 6 +₹3,030.00, Nov 9 −₹3,470.00 (stop, confirmed key), today −₹3,470.00 (stop) → **MTD +₹503.25**. All three of its stops share the never-developed shape (the frozen leg files store no MFE, so the narrower sub-shape stays uncountable in-sample, as recorded for RSI-NIFTY-009). In Jan–Oct the testable late solo-Skill sleeves lost standalone (CE sleeve −₹40,534.65 / 26 legs; all-solo −₹44,223.65) — today's leg is consistent with that history, and the early (≤09:55) slice this leg belongs to still has zero stored instances.
- **The fix:** None new — the admission family is gate-closed (NIFTY-EVE-01/02b/03b GATE FAIL; EVE-18 empty by construction) and the no-development cut diagnosed from this shape (NIFTY-EVE-17) was GATE FAIL on 2026-11-10. Status: **NO FIX — accepted risk** of the standalone shadow book; it continues as labelled December evidence only.
- **Lesson ID:** RSI-NIFTY-010 (shared with the primary blocked-signal entry for this key), cross-referenced in `november_rsi_nifty_log.md` (2026-11-11) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-11 · NIFTY · SHADOW DEC-S1 / TUNED SHADOW BOOK v2 — day NOT YET SCORED (excluded, never estimated)

- **SHADOW DEC-S1:** No scored row exists for 2026-11-11 at this evening run (the shadow scorer's state lists DEC-S1 scored days through 2026-11-09; the Skill books for today ARE scored). The day is **excluded from all DEC-S1 totals** — not a no-trade day, not a zero. DEC-S1 November-to-date stands at **4 trades, −₹4,123.50** over scored days Nov 2–9, and will be re-scored automatically when served.
- **TUNED SHADOW BOOK v2** (DEC-S1 minus B PE / A CE / C CE): scores off the DEC-S1 construction, so its Nov 11 day is unscored with it and excluded, never estimated. v2 MTD **₹0 · 0 trades** over scored days through Nov 9.

---

## 2026-11-11 · NIFTY · PE 25400 · SHADOW DEC-S1 (Component B) — NOW SCORED (was NOT YET SCORED on 2026-11-11; journalled 2026-11-12)

- **Strategy in play:** SHADOW DEC-S1 (adopted December candidate, November forward evidence), Component B — gap fade. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** Nifty gapped UP on the open (open 25337.80 vs the prior trading day's close 25044.65 on 2026-11-09; 2026-11-10 was a market holiday), meeting Component B's frozen |gap| ≥ 0.50% trigger; the fade takes the opposite side at the 10:05 bar: PE, ATM100 strike 25400, monthly expiry in force 2026-11-23. Re-derivable from the DEC-S1 spec in `november_shadow_runs_2026-11-04.md` plus the day's spot open/prior close. This entry replaces the NOT YET SCORED status in the 2026-11-11 entry above — the scorer has since served the day (`november_shadow_decs1_nifty_log.csv`, 2026-11-11 row, CANDLE-SCORED).
- **Market context at entry:** Gap-up morning that faded through the day — spot made its high 25424.35 on the 09:45 bar and fell to an afternoon low of 25095.35, i.e. a gap-fade day, the opposite of the gap-continuation days that stopped this sleeve on Nov 3 and Nov 5.
- **Entry:** 10:05 @ ₹296.80 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹246.80 (−50) · target ₹386.80 (+90) · breakeven arm +50 → stop to entry · runner lock +60 after +90 · second target +175 · square-off 15:20
- **What actually happened:** The premium dipped only slightly first (low 285.35 at 11:35, MAE −11.45), then rose with the spot fade to a high of 419.85 at 13:50 (MFE +123.05; the +90 target zone was reached, the runner armed and the lock rose to entry+60), then gave back to the lock.
- **Exit:** 14:00 @ ₹356.80 — RUNNER STOP (runner lock at entry+60; the 14:00 bar's low 354.40 cut the lock)
- **Result:** +₹3,680.00 (+60.00 points, after ₹220 cost) · full-target? yes (+90 arm reached; +175 second target not reached)
- **Rules followed exactly?** Yes — frozen DEC-S1 geometry, candle-scored from `november_shadow_data/candles_NIFTY_25400PE_2026-11-11_2026-11-23.json`.
- **Same-day comparison:** Primary and control took nothing that day (blocked solo Skill CE, Lesson RSI-NIFTY-010). TUNED SHADOW BOOK v2 skips this leg's class by its defining rule (no Component B PE legs), so v2 had no Nov 11 leg — this win is therefore also the tuned line's November opportunity cost on this class, recorded as such: B PE November now stands at 4 legs, −₹3,480.00 (−220.00 / −3,470.00 / −3,470.00 / +3,680.00), still negative, and the Jan–Oct case for the skip (−₹11,881.75 / 23 legs) is unchanged. SHADOW Skill took the opposite side that day (CE 25400) and stopped for −₹3,470.00.

### If the trade won
- **Why it worked:** The gap-up actually faded — spot never traded above its 09:45 high and fell all afternoon, so the fade's premise held for once; follow-through carried the premium to +123.05 and the runner machinery banked +60. Not labelled lucky: basis, direction and session path all agreed, and the lock exit is the frozen geometry working as designed.
- **Give-back check:** Captured +60.00 of +123.05 MFE — 63.05 points given back from the 13:50 peak to the 14:00 lock exit, by the lock's design (entry+60 after +90). Recorded as exit-tuning colour only; no geometry change is proposed from one leg.

---

## 2026-11-12 · NIFTY · NO TRADE — blocked solo signal, day 6 of the class (PRIMARY + CONTROL both took nothing)

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised. The only U1 key of the day was a Skill V3 CE solo key (signal 09:35, would-be entry 09:40) — the sixth instance of this class (2026-11-02, 2026-11-03, 2026-11-05, 2026-11-06, 2026-11-11, today). The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: room < 200*scale), and Volrix (b) did not trigger (prev-day change +0.84% > −1.0% threshold). Re-derivable from the 2026-11-12 row of `november_paper_nifty_log.csv` (full-day EOD construction from Upstox intraday spot candles, 75 bars).
- **Market context at entry:** n/a — no entry. Spot opened 25213.50 (gap −0.16% vs the 2026-11-11 close 25255.05), rose to a morning high of 25384.80 at 10:00, then drifted down all day to an afternoon low of 25210.00 (12:15) and a 15:10 close of 25275.40. The blocked CE pointed up into a day that went nowhere and then down.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a for the primary. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary and live producer both withheld the solo key, exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 also took nothing — it drops this key independently (solo + early, entry ≤09:55). SHADOW Skill (separate standalone book) DID take this key — CE 25400 @ 09:40 — and stopped for −₹3,470.00 (journalled separately below; its money is never in primary figures). SHADOW DEC-S1 for 2026-11-12 is scored as a no-trade day (entry below); TUNED SHADOW BOOK v2 therefore had no leg either.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the sixth time in eight trading days: 1 of ≥2 required systems fired. Frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-12 row.
- **Has history seen this before?** Yes — sixth instance of the class (Lessons RSI-NIFTY-001, 002, 006, 008, 010, today). The stored Jan–Oct pool still holds zero early (≤09:55) solo Skill legs, so the class remains untestable in-sample. The November standalone count for the blocked keys (SHADOW Skill, G7) is now 6 legs: −₹3,470.00 (Nov 2) / +₹2,688.75 (Nov 3) / +₹5,194.50 (Nov 5) / +₹3,030.00 (Nov 6) / −₹3,470.00 (Nov 11) / −₹3,470.00 (today) = **+₹503.25 net** — the cushion built in the first four legs is now almost entirely given back by two consecutive stops; the forward evidence no longer leans against the block.
- **The fix:** No new fix from the admission family — NIFTY-EVE-01/02b/03b already GATE FAIL, NIFTY-EVE-18 is empty by construction, and a rejected variant is never retested identically. Status: **NO FIX — blocking stands as accepted design**, with the November standalone count tracked as December evidence.
- **Lesson ID:** RSI-NIFTY-011, cross-referenced in `november_rsi_nifty_log.md` (2026-11-12) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — NOT fired today
- The book was flat all day, so the check covers the full session on Upstox 5-minute spot bars fetched tonight (75 bars). Opening range (09:15–09:30): high 25342.00 / low 25142.95, width 199.05 pts. Morning extremes to 12:00: high 25384.80 / low 25142.95. Tradable afternoon (12:00–15:10): high 25283.50 / low 25210.00 — **entirely inside the morning range, extension 0 pts on either side**, below the ≥60-pt Nifty threshold and below the morning range.
- **Verdict: NOT a missed-move day for Nifty.** The afternoon offered no fresh move beyond the morning range. Session-coverage flaw count stays **3**.

---

## 2026-11-12 · NIFTY · CE 25400 · SHADOW Skill (standalone) — candle-scored

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen C3 block is NOT applied.
- **Basis for the trade (why this trade, why then):** The day's Skill V3 key — the same key the primary blocked as a solo (Lesson RSI-NIFTY-011): OR-break CE, signal 09:35, entry at the 09:40 bar, ATM100 strike 25400, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** Spot rose into a 10:00 morning high (25384.80) and then drifted down all day — the CE was against the day's eventual direction after the first half hour.
- **Entry:** 09:40 @ ₹279.10 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹229.10 (−50) · target +90 → runner lock entry+50 · second target +150 · square-off 15:10 (G7 geometry per the Skill shadow spec)
- **What actually happened:** Small favourable excursion only — premium high 295.65 at 10:00 (MFE +16.55, never near the +90 arm, so the runner never armed) — then a steady decay as spot fell, through the stop. Worst point (MAE) −51.60 pts on the exit bar (low 227.50).
- **Exit:** 11:40 @ ₹229.10 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen Skill-shadow geometry, candle-scored from `november_shadow_data/candles_NIFTY_25400CE_2026-11-12_2026-11-23.json`.
- **Same-day comparison:** Primary and control took nothing (the key was solo for C3 — Lesson RSI-NIFTY-011). SHADOW DEC-S1 held no leg today (entry below); TUNED v2 likewise none.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — the OR-break's follow-through ended at the 10:00 spot high; after that spot drifted down all session and the bought premium bled to its stop.
- **Evidence:** Spot high 25384.80 at 10:00, then a one-way drift to 25210.00 by 12:15. Premium path: entry 279.10, best high 295.65 at 10:00 (MFE +16.55), stop-bar (11:40) low 227.50 below the 229.10 stop.
- **Has history seen this before?** Yes — the standalone book's November record is now 7 trades: Nov 2 −₹3,470.00 (stop), Nov 3 +₹2,688.75, Nov 5 +₹5,194.50, Nov 6 +₹3,030.00, Nov 9 −₹3,470.00 (stop, confirmed key), Nov 11 −₹3,470.00 (stop), today −₹3,470.00 (stop) → **MTD −₹2,966.75**. Four of its seven legs are full stops, all sharing the never-developed shape (the frozen leg files store no MFE, so the narrower sub-shape stays uncountable in-sample, as recorded for RSI-NIFTY-009). In Jan–Oct the testable late solo-Skill sleeves lost standalone (CE sleeve −₹40,534.65 / 26 legs; all-solo −₹44,223.65) — the last two days are consistent with that history.
- **The fix:** None new — the admission family is gate-closed (NIFTY-EVE-01/02b/03b GATE FAIL; EVE-18 empty by construction) and the no-development cut diagnosed from this shape (NIFTY-EVE-17) was GATE FAIL on 2026-11-10. Status: **NO FIX — accepted risk** of the standalone shadow book; it continues as labelled December evidence only.
- **Lesson ID:** RSI-NIFTY-011 (shared with the primary blocked-signal entry for this key), cross-referenced in `november_rsi_nifty_log.md` (2026-11-12) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-12 · NIFTY · SHADOW DEC-S1 / TUNED SHADOW BOOK v2 — scored NO-TRADE day

- **SHADOW DEC-S1:** The 2026-11-12 row in `november_shadow_decs1_nifty_log.csv` is a **no-trade day**: A legs 0 (sysmap CE: Skill V3 only — a solo key, no confirmed leg); Component B: no fade — gap −0.16%; Component C: not a weekly-expiry day. DEC-S1 November-to-date is now **5 trades, −₹443.50** (Nov 2 −₹220.00; Nov 3 −₹433.50 on 2 legs; Nov 4 no-trade; Nov 5 −₹3,470.00; Nov 6 no-trade; Nov 9 no-trade; Nov 11 +₹3,680.00; today no-trade). No excluded days outstanding.
- **TUNED SHADOW BOOK v2** (DEC-S1 minus B PE / A CE / C CE): on the scored Nov 11 construction DEC-S1's only leg was a Component B PE leg, which v2 skips by rule, and on Nov 12 DEC-S1 held no leg at all → v2 MTD **₹0 · 0 trades** over scored days through Nov 12.

---

## 2026-11-13 · NIFTY · NO TRADE — blocked solo signal, day 7 of the class, but a LATE solo this time (PRIMARY took nothing; CONTROL took the key)

- **Strategy in play:** NF-PAPER-C3G7 (C3 confirmed-only + G7 runner geometry), frozen November primary; control U1-N1.
- **Basis for the trade (why this trade, why then):** n/a — no trade was authorised for the primary. The only U1 key of the day was a Skill V3 CE solo key (signal 10:05, would-be entry 10:10) — the seventh instance of the blocked-solo class (2026-11-02, 2026-11-03, 2026-11-05, 2026-11-06, 2026-11-11, 2026-11-12, today), but the first LATE one: every prior instance entered ≤09:55; today's enters 10:10. The frozen C3 rule requires ≥2 distinct source systems on a key; a solo leg is not taken at any hour. No second system confirmed at any point: (lA) v2's confirmer never broke the OR low in 09:30–11:30, V5 v2 had no candidates (V4: no signal; Skill candidate filtered: room < 200*scale), and Volrix (b) did not trigger (prev-day change +0.18% > −1.0% threshold). Re-derivable from the 2026-11-13 rows of `november_paper_nifty_log.csv` (full-day EOD construction from Upstox intraday spot candles, 75 bars; tonight's re-run of `nov_paper_eod_2026-11-13.py` reproduced the same key and notes exactly).
- **Market context at entry:** n/a — no entry. Spot opened 25209.85 (gap −0.35% vs the 2026-11-12 close 25299.35), dipped to the OR low 25077.55, recovered to a morning high of 25246.35, then faded: afternoon low 25054.40 (14:20), 15:10 close 25139.95. The blocked CE pointed up into a day that ended lower.
- **Entry:** n/a — no entry (blocked before entry by the C3 ≥2-system rule)
- **Planned exits at entry:** n/a — no position; had C3 authorised a trade, the frozen exits would have been stop −50 · target +90, runner lock +50 after +90, second target +150, square-off 15:10
- **What actually happened:** No position was opened, so MFE/MAE are n/a for the primary. The blocked key never gained a confirming second system during the day.
- **Exit:** n/a — no position
- **Result:** ₹0 (0 points) · full-target? n/a
- **Rules followed exactly?** Yes — primary withheld the solo key exactly as frozen. No deviation.
- **Same-day comparison:** Control U1-N1 DID take this key (see its entry below) — it is solo but entry 10:10 > 09:55, so the control's solo+early drop does not apply (the N1 Jan–Oct pool keeps solo legs after 09:55) → stopped for −₹3,470.00, counted separately, never in primary totals. SHADOW Skill (separate standalone book) took the identical leg and stopped for the identical −₹3,470.00 (journalled separately below). SHADOW DEC-S1 scored a no-trade day (entry below); TUNED SHADOW BOOK v2 therefore had no leg either.

### Blocked-signal review (no-trade day analysis, in place of the loss section)
- **Why it was blocked — cause:** Confirmation was the binding constraint for the seventh time in nine trading days: 1 of ≥2 required systems fired. Frozen C3 design working as specified, not a defect.
- **Evidence:** `november_paper_nifty_log.csv` 2026-11-13 rows; EOD re-run tonight reproduced the key (CE, Skill V3 only, signal 10:05, entry 10:10).
- **Has history seen this before?** Yes — seventh instance of the class (Lessons RSI-NIFTY-001, 002, 006, 008, 010, 011, today). Today is the first instance in the TESTABLE slice: the stored Jan–Oct pool holds zero early (≤09:55) solo Skill legs, but the late (>09:55) solo Skill CE slice was gated on 2026-11-02 (NIFTY-EVE-01: 26 legs, sleeve standalone −₹40,534.65, FT 7.7% — GATE FAIL), so this exact class has a negative in-sample record and today's forward leg agrees with it. The November standalone count for the blocked keys (SHADOW Skill, G7) is now 7 legs: −₹3,470.00 (Nov 2) / +₹2,688.75 (Nov 3) / +₹5,194.50 (Nov 5) / +₹3,030.00 (Nov 6) / −₹3,470.00 (Nov 11) / −₹3,470.00 (Nov 12) / −₹3,470.00 (today) = **−₹2,966.75 net** — three consecutive stops have turned the standalone line negative; the forward evidence now supports the block.
- **The fix:** NO FIX — and none may be built: the admission family is gate-closed (NIFTY-EVE-01/02b/03b GATE FAIL; EVE-18 empty by construction), and under the owner's settlement of 2026-11-13 the segment engines are SCORE-ONLY — no new variants, exits or filters. Status: **blocking stands as accepted design**, with the November standalone count tracked as December evidence.
- **Lesson ID:** RSI-NIFTY-012, cross-referenced in `november_rsi_nifty_log.md` (2026-11-13) and the Nifty section of `november_rsi_candidates.md`.

### Missed-move check (standing process fix, 2026-11-03 ~14:36) — NOT fired today
- The book was flat all day, so the check covers the full session on Upstox 5-minute spot bars fetched tonight (75 bars). Opening range (09:15–09:30): high 25209.85 / low 25077.55, width 132.30 pts. Morning extremes to 12:00: high 25246.35 / low 25077.55. Tradable afternoon (12:00–15:10): high 25159.00 / low 25054.40 (14:20) — the low extends only **23.15 pts beyond the morning low**, below the ≥60-pt Nifty threshold and below the morning range; no upside extension.
- **Verdict: NOT a missed-move day for Nifty.** Session-coverage flaw count stays **3**. The tested fix for this shape (NIFTY-EVE-12) was GATE FAIL on 2026-11-10 and, under the score-only settlement, no new afternoon candidate arises.

---

## 2026-11-13 · NIFTY · CE 25200 · CONTROL (U1-N1) — the late solo key, kept by the control and stopped

- **Strategy in play:** CONTROL U1-N1 (U1 pool with solo + early ≤09:55 keys dropped; G0 baseline geometry), frozen control in the same log. Paper only, real money ₹0, 1 lot (65).
- **Basis for the trade (why this trade, why then):** The day's Skill V3 CE key — OR-break CE, signal 10:05, entry at the 10:10 bar, ATM100 strike 25200, monthly expiry in force 2026-11-23. The control does not drop it: the key is solo, but its entry (10:10) is after the control's 09:55 early cutoff, and the N1 Jan–Oct pool keeps solo legs with entry > 09:55. The primary's C3 rule (≥2 systems) still blocks it — the two books diverge on exactly this rule today, for the first time in November.
- **Market context at entry:** Gap-down open (−0.35%) that had recovered off the OR low; spot was mid-recovery at entry and made its morning high (25246.35) later in the morning before fading all afternoon.
- **Entry:** 10:10 @ ₹274.50 (open of the 10:10 premium candle) · 1 lot
- **Planned exits at entry:** stop ₹224.50 (−50) · target ₹364.50 (+90) · square-off 15:10 (G0 — no runner)
- **What actually happened:** A modest favourable excursion first — premium high 297.95 at 10:45 (MFE +23.45, never near the +90 target) — then a steady decay as spot faded, through the stop. Worst point (MAE) −54.40 pts on the exit bar (low 220.10).
- **Exit:** 12:00 @ ₹224.50 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen control geometry, candle-scored from `november_shadow_data/candles_NIFTY_25200CE_2026-11-13_2026-11-23.json`; entry premium verified from Upstox intraday option candles at EOD.
- **Same-day comparison:** Primary took nothing (the key was solo for C3 — see the entry above). SHADOW Skill took the identical leg under G7 and stopped for the identical −₹3,470.00 (the runner never armed, so G0 and G7 coincide). Control results are never added to primary totals; control November-to-date: 2 trades, −₹6,940.00 (Nov 9 confirmed PE −₹3,470.00; today −₹3,470.00).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — the OR-break's follow-through topped at +23.45 premium points at 10:45; after that spot faded all session and the bought premium bled to its stop.
- **Evidence:** Premium path: entry 274.50, best high 297.95 at 10:45 (MFE +23.45), stop-bar (12:00) low 220.10 below the 224.50 stop. Spot: morning high 25246.35, then a fade to an afternoon low of 25054.40.
- **Has history seen this before?** Yes, repeatedly — this is the recurring cause for this setup. Today's class (late solo Skill CE, entry >09:55) is exactly the NIFTY-EVE-01 sleeve gated on 2026-11-02: 26 legs in Jan–Oct, standalone −₹40,534.65, FT 7.7%. The control's own November record is 2 trades, both full stops. The standalone shadow's November record (below) is now 5 full stops in 8 legs.
- **The fix:** NO FIX — the admission family is gate-closed (NIFTY-EVE-01 GATE FAIL on this exact slice) and the engines are SCORE-ONLY under the owner's 2026-11-13 settlement. Status: **accepted risk of the frozen control construction**; the leg is December evidence for keeping the C3 confirmation rule.
- **Lesson ID:** RSI-NIFTY-012 (shared with the primary blocked-signal entry for this key), cross-referenced in `november_rsi_nifty_log.md` (2026-11-13) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-13 · NIFTY · CE 25200 · SHADOW Skill (standalone) — candle-scored

- **Strategy in play:** SHADOW Skill — Day Trader Skill (Skill V3) standalone book, owner-directed live shadow (2026-11-05). Paper only, real money ₹0, 1 lot (65). Solo legs included; the frozen C3 block is NOT applied.
- **Basis for the trade (why this trade, why then):** The day's Skill V3 key — the same key the primary blocked as a solo and the control kept as a late solo (Lesson RSI-NIFTY-012): OR-break CE, signal 10:05, entry at the 10:10 bar, ATM100 strike 25200, monthly expiry in force 2026-11-23. The standalone book takes every Skill V3 key by its own frozen rule.
- **Market context at entry:** As the control entry above — gap-down open recovering at entry, morning high later, then an all-afternoon fade.
- **Entry:** 10:10 @ ₹274.50 (open of entry candle) · 1 lot
- **Planned exits at entry:** stop ₹224.50 (−50) · target +90 → runner lock entry+50 · second target +150 · square-off 15:10 (G7 geometry per the Skill shadow spec)
- **What actually happened:** Identical premium path to the control leg: high 297.95 at 10:45 (MFE +23.45, never near the +90 arm, so the runner never armed), then decay through the stop; worst point −54.40 on the exit bar (low 220.10).
- **Exit:** 12:00 @ ₹224.50 — STOP (−50)
- **Result:** −₹3,470.00 (−50.00 points, after ₹220 cost) · full-target? no
- **Rules followed exactly?** Yes — frozen Skill-shadow geometry, candle-scored from `november_shadow_data/candles_NIFTY_25200CE_2026-11-13_2026-11-23.json`.
- **Same-day comparison:** Primary took nothing (solo for C3). Control U1-N1 took the identical leg under G0 for the identical −₹3,470.00. SHADOW DEC-S1 held no leg today (entry below); TUNED v2 likewise none.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** **No follow-through chop** — identical shape to the control leg above: follow-through topped at +23.45 at 10:45, then spot faded all session and the premium bled to its stop.
- **Evidence:** Premium path and spot path as the control entry above (same contract, same candles).
- **Has history seen this before?** Yes — the standalone book's November record is now 8 trades: Nov 2 −₹3,470.00 (stop), Nov 3 +₹2,688.75, Nov 5 +₹5,194.50, Nov 6 +₹3,030.00, Nov 9 −₹3,470.00 (stop, confirmed key), Nov 11 −₹3,470.00 (stop), Nov 12 −₹3,470.00 (stop), today −₹3,470.00 (stop) → **MTD −₹6,436.75**. Five of its eight legs are full stops, all sharing the never-developed shape; in Jan–Oct the testable late solo-Skill CE sleeve lost standalone (−₹40,534.65 / 26 legs) — November is now consistent with that history on both the blocked-key subset (−₹2,966.75 over 7 legs) and the whole book.
- **The fix:** None — the admission family is gate-closed (NIFTY-EVE-01/02b/03b GATE FAIL; EVE-18 empty by construction), the no-development cut (NIFTY-EVE-17) was GATE FAIL on 2026-11-10, and the engines are SCORE-ONLY under the owner's 2026-11-13 settlement. Status: **NO FIX — accepted risk** of the standalone shadow book; it continues as labelled December evidence only.
- **Lesson ID:** RSI-NIFTY-012 (shared), cross-referenced in `november_rsi_nifty_log.md` (2026-11-13) and the Nifty section of `november_rsi_candidates.md`.

---

## 2026-11-13 · NIFTY · SHADOW DEC-S1 / TUNED SHADOW BOOK v2 — scored NO-TRADE day

- **SHADOW DEC-S1 (control line — retired as a standalone December candidate on 2026-11-13, scored through Nov 30 for data continuity):** The 2026-11-13 row in `november_shadow_decs1_nifty_log.csv` is a **no-trade day**: A legs 0 (sysmap CE: Skill V3 only — a solo key, no confirmed leg); Component B: no fade — gap −0.35%; Component C: not a weekly-expiry day. DEC-S1 November-to-date unchanged: **5 trades, −₹443.50** (Nov 2 −₹220.00; Nov 3 −₹433.50 on 2 legs; Nov 4 no-trade; Nov 5 −₹3,470.00; Nov 6 no-trade; Nov 9 no-trade; Nov 11 +₹3,680.00; Nov 12 no-trade; today no-trade). No excluded days outstanding.
- **TUNED SHADOW BOOK v2** (DEC-S1 minus B PE / A CE / C CE): DEC-S1 held no leg today → v2 MTD **₹0 · 0 trades** over scored days through Nov 13. TUNED v1 (the lead December candidate per the 2026-11-13 audit) likewise had no leg today; its November forward line stands at +₹3,036.50 · 1 leg.
