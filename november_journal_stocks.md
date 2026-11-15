# Stocks — November 2026 paper trade journal

Every trade gets one full entry per trade_journal_TEMPLATE.md: basis, strategy, outcome, failure cause, fix.
Written nightly by the RSI engine (17:15). Paper only, real money ₹0.

---

# 2026-11-02 — Day 1 (regime DOWN in every logger; the frozen gate input as recorded in the INV1 scorecard log: Nifty prior close 23053.1 vs 50DMA 23254.75). All figures provisional per 100 shares, ₹40/trade, paper only, real money ₹0. MFE/MAE computed by the evening engine from the same sarvaritu_fwd 5-min candles the loggers used (`stocks_eve_2026-11-02.py`).

## 2026-11-02 · NTPC · LONG · PRIMARY (whole book, N4-V3 component)

- **Strategy in play:** N4-V3 reaction-day morning-move, frozen SarvaRitu whole book (book geometry T150/S080)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Sat 2026-10-31 (consol PAT +40.7% YoY; interim dividend ₹3) → reaction day Mon 2026-11-02. By 09:30 NTPC had moved +3.178% (09:25 close 326.30 vs prev close 316.25 on 2026-10-30), qualifying under the frozen N4-V3 reaction-day rule; entry at 09:35 per the frozen convention. A reader can re-derive this from `stocks_n4_november_paper_log.csv` (2026-11-02 row) + the frozen spec.
- **Market context at entry:** Regime DOWN (frozen gate: Nifty prior close below its 50DMA, per the scorecard record). Stock-specific results spike against a down-regime tape.
- **Entry:** 09:35 @ ₹325.30 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹322.71 (−0.80%) · target ₹330.18 (+1.50%) · square-off 15:10
- **What actually happened:** Early high 327.50 at 09:45 (MFE +₹220.00), then no follow-through — price faded through the morning; the wider book stop was reached later than the scorecard stop. MAE −₹335.00 (low 321.95 within the holding window, past the stop level).
- **Exit:** 11:50 @ ₹322.70 — STOP (live-shadow producer record; the whole-book log records exit price 322.70)
- **Result:** −₹300.24 net after ₹40 cost · full-target? no
- **Rules followed exactly?** Yes on the frozen EOD construction. Process note (not a rule deviation): this signal fired at the open and was the trade Chandu caught as not announced live in the morning; the live loop later recorded entry and the 11:50 stop exit, and the EOD log matches it exactly.
- **Same-day comparison:** The N4-V3 primary scorecard took the identical signal on its own geometry (T125/S050) and stopped earlier at 10:05 @ 323.67 for −₹202.65 (entry below). The promoted TUNED SHADOW (one-sided cap, from 2026-11-03) would have SKIPPED this trade — signed move +3.178% ≥ +3.0% on a LONG (would-be only, not shadow money).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race, in the diagnosed over-extension shape: a ≥+3% morning spike on results that the tape did not sustain.
- **Evidence:** +3.178% by 09:30; MFE only +₹220.00 (09:45 high 327.50 vs target 330.18); fade to the stop by late morning on both geometries.
- **Has history seen this before?** Yes — this is the recurring N4-V3 failure bucket. Standalone N4-V3, Jan–Oct 2026 (scorecard basis): the |move| ≥3% bucket is 26 of 56 trades and the only negative-average bucket (book basis −₹962.38 total, avg −₹37.01; scorecard −₹2,442.50, avg −₹93.94); split by direction at book level, LONG ≥+3% is negative in both 2025 (−₹940.81 / 10 tr) and 2026 (−₹1,790.26 / 4 tr). Stops overall: 35 of 56 scorecard trades (21 within ≤15 min).
- **The fix:** ALREADY FIXED by shadow — the one-sided cap (skip N4-V3 LONG entries with signed move by 09:30 ≥ +3.0%; SHORTs uncapped) passed the whole-book gate in today's floor session (cycle FLOOR-2, all nine legs) and is promoted tonight as Stocks TUNED SHADOW v1 from Tue 2026-11-03. Spec: `november_shadow_stocks_onesided_cap_2026-11-02.md`. The symmetric cap draft is superseded (failed at book level, cycle FLOOR-1).
- **Lesson ID:** RSI-STOCKS-001

## 2026-11-02 · NTPC · LONG · PRIMARY SCORECARD (N4-V3 component scorecard)

- **Strategy in play:** N4-V3 primary scorecard (scorecard geometry T125/S050), frozen November component scorecard
- **Basis for the trade:** identical signal to the whole-book entry above — results reaction +3.178% by 09:30, entry 09:35 @ ₹325.30 per the frozen scorecard spec (`stocks_n4_november_paper_log.csv`, 2026-11-02).
- **Market context at entry:** regime DOWN (as above).
- **Entry:** 09:35 @ ₹325.30 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹323.67 (−0.50%) · target ₹329.37 (+1.25%) · square-off 15:10
- **What actually happened:** MFE +₹220.00 (09:45 high 327.50); the 10:05 bar's low 323.35 hit the stop. MAE −₹195.00 within the holding window.
- **Exit:** 10:05 @ ₹323.67 — STOP
- **Result:** −₹202.65 net after ₹40 cost · full-target? no
- **Rules followed exactly?** yes — stop-first scan from the 09:35 bar per the frozen scorecard convention.
- **Same-day comparison:** whole book (above) held the same signal on wider geometry and lost −₹300.24; the TUNED SHADOW would have skipped both (Lesson RSI-STOCKS-001).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race (over-extension bucket, as above).
- **Evidence:** 10:05 bar low 323.35 through stop 323.67, 30 minutes after entry, after a +₹220.00 MFE at 09:45.
- **Has history seen this before?** Yes — same counts as the book entry above (26-trade ≥3% bucket, negative on both bases; 35 of 56 stops in the scorecard history).
- **The fix:** ALREADY FIXED by shadow — one-sided cap, TUNED SHADOW v1 from 2026-11-03 (see book entry).
- **Lesson ID:** RSI-STOCKS-001 (shared with the whole-book entry — same signal, two geometries)

## 2026-11-02 · GODREJCP · SHORT · SHADOW SCORECARD (P2F)

- **Strategy in play:** P2F shadow scorecard (separate November component scorecard; NOT a whole-book trade — the frozen book band is ≥2.5% and this reaction was −2.27%)
- **Basis for the trade:** Q2 FY27 results board 2026-10-29 after-market → reaction Fri 2026-10-30: −2.27% (close 818.00 vs 837.00), which qualifies ≥2.00% SHORT under the shadow scorecard's boundary rule; R+1 entry Mon 2026-11-02 at the 09:15 open per the frozen scorecard spec (`stocks_p2f_november_shadow_log.csv`, 2026-11-02).
- **Market context at entry:** regime DOWN. The stock had already fallen on the reaction day; the R+1 open offered no further downside follow-through.
- **Entry:** 09:15 @ ₹813.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹817.06 (+0.50% against) · target ₹802.84 (−1.25%) · square-off 15:10
- **What actually happened:** Best point was the entry bar's low 812.50 (MFE +₹50.00); the entry bar itself had spiked to 823.00, and the 09:20 bar's high 817.50 hit the stop — stopped on the first scanned bar after entry.
- **Exit:** 09:20 @ ₹817.06 — STOP
- **Result:** −₹446.50 net after ₹40 cost · full-target? no · SHADOW SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — scan from the bar after entry, stop before target, per the frozen scorecard convention.
- **Same-day comparison:** the whole book correctly did NOT take this trade (reaction −2.27% is below the frozen ≥2.5% book band) — blocking was right today; see the no-trade review in the RSI log.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — a one-bar stop-out with essentially no favourable excursion (+₹50.00 MFE).
- **Evidence:** entry 09:15 @ 813.00; 09:20 bar high 817.50 through stop 817.06; exit stamped 09:20.
- **Has history seen this before?** Yes — recurring for the P2F family: in the stored Jan–Oct 2026 family universe (87 trades: P2F 46 + P2F-R2 34 + R2-LOWBAND 7), 25 stops landed within ≤15 minutes of entry (fix-test record, `november_rsi_fix_tests_2026-11-02.md`).
- **The fix:** NO FIX — accepted risk. The one mechanical fix for this shape (skip the opening bar, STOCKS-FIX-01) was tested 2026-11-02 and REJECTED (+₹27,293.58 → +₹9,582.00; the delay cost ₹21,272.50 on kept trades) and must not be retested identically. The book-level protection already exists: the frozen ≥2.5% band kept this trade out of the book.
- **Lesson ID:** RSI-STOCKS-002

## 2026-11-02 · HINDCOPPER · LONG · PRIMARY (whole book, INV-LONG component; identical execution in the INV1 scorecard)

- **Strategy in play:** INV-LONG (inverted-regime long), frozen SarvaRitu whole book (T125/S050); the INV1 scorecard recorded the identical execution, so it is journalled once here and cross-referenced there
- **Basis for the trade:** INV1 condition met — Nifty prior close 23053.1 ≤ 50DMA 23254.75 (DOWN regime gate) — and a skill_or_breakout signal; entry 09:35 per the frozen construction (`stocks_p2inv_november_shadow_log.csv`, 2026-11-02; ADR 3.549; no event).
- **Market context at entry:** regime DOWN — the regime this component is designed to trade against.
- **Entry:** 09:35 @ ₹404.15 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹402.13 · target ₹409.20 · square-off 15:10
- **What actually happened:** Shallow dip first (MAE −₹80.00, low 403.35 at 09:45), then a steady climb; target reached in the 10:40 bar (bar high 409.70). MFE +₹555.00.
- **Exit:** 10:40 @ ₹409.20 — TARGET
- **Result:** +₹465.19 net after ₹40 cost (gross +₹505.19) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** the same stock also traded in the book's F4 component at 10:05 (separate frozen signal, entry below) and hit its target too; the two are distinct component executions under the frozen book, not a double-count of one signal.

### If the trade won
- **Why it worked:** the breakout followed through in a DOWN regime — the component's home conditions — with a shallow MAE (−₹80.00 against a −₹202 stop distance) before a clean run to target.
- **Give-back check:** captured ₹505.19 of +₹555.00 MFE (91%) — the small remainder is the target level itself (exit at the target price while the exit bar printed 409.70). No give-back concern.

## 2026-11-02 · HINDCOPPER · LONG · PRIMARY (whole book, F4 component)

- **Strategy in play:** F4 retest-hold confirmation, frozen SarvaRitu whole book (T150/S095, first-signal-only)
- **Basis for the trade:** F4 morning-move signal measured at 10:00 within the frozen 0.5–1.0% band, with the retest-hold confirmation the frozen spec requires; entry at the open of the next bar, 10:05 @ ₹404.55 (10:05 bar open in the candles the logger used). The whole-book log records entry time, exit price and net; the entry price here is the 10:05 bar open, consistent with the frozen F4 convention in the stored F4 trade files.
- **Market context at entry:** regime DOWN; metals were the day's strong pocket (both F4 trades today were metal longs).
- **Entry:** 10:05 @ ₹404.55 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹400.71 (−0.95%) · target ₹410.62 (+1.50%) · square-off 15:10
- **What actually happened:** No real drawdown (MAE −₹25.00, entry-bar low 404.30), then a persistent climb all day; the 14:00 bar (high 410.80) reached the target. MFE +₹625.00.
- **Exit:** 14:00 @ ₹410.62 — TARGET
- **Result:** +₹566.82 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** INV-LONG on the same stock (above) also hit target earlier at 10:40; distinct frozen component signal.

### If the trade won
- **Why it worked:** confirmation plus follow-through — the retest held and the name trended for four hours with almost no adverse excursion.
- **Give-back check:** captured at the target price; the exit bar's high was only ₹0.18 above it. No give-back.

## 2026-11-02 · HINDZINC · LONG · PRIMARY (whole book, F4 component)

- **Strategy in play:** F4 retest-hold confirmation, frozen SarvaRitu whole book (T150/S095, first-signal-only)
- **Basis for the trade:** F4 morning-move signal measured at 10:00 within the frozen 0.5–1.0% band with retest-hold confirmation; entry at the open of the next bar, 10:05 @ ₹509.00 (10:05 bar open in the logger's candles).
- **Market context at entry:** regime DOWN; metals strong (as above).
- **Entry:** 10:05 @ ₹509.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹504.16 (−0.95%) · target ₹516.63 (+1.50%) · square-off 15:10
- **What actually happened:** MAE only −₹15.00 (entry-bar low 508.85); a slow, steady grind up; the 13:35 bar (high 517.45) reached the target. MFE +₹845.00.
- **Exit:** 13:35 @ ₹516.63 — TARGET
- **Result:** +₹723.50 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent — F4 trades in the whole book only.

### If the trade won
- **Why it worked:** the confirmed morning move in the day's leading sector simply kept going; the trade was never threatened.
- **Give-back check:** exit at the target price inside the bar that printed the day's best high to that point — nothing material left behind at exit.

## 2026-11-02 · WIPRO · SHORT · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (raw INV population scored separately; NOT a whole-book trade — the book's INV-LONG is long-only and pool-picked)
- **Basis for the trade:** INV1 condition met (Nifty prior close 23053.1 ≤ 50DMA 23254.75); skill_or_breakdown signal, entry 09:35 @ ₹195.84 per the scorecard construction (`stocks_p2inv_november_shadow_log.csv`; ADR 3.373; no event).
- **Market context at entry:** regime DOWN.
- **Entry:** 09:35 @ ₹195.84 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹196.82 · target ₹193.39 · square-off 15:10
- **What actually happened:** MFE only +₹32.00 (low 195.52); price reversed and hit the stop two bars later. MAE −₹102.00 (stop level).
- **Exit:** 09:45 @ ₹196.82 — STOP
- **Result:** −₹137.92 net after ₹40 cost · full-target? no · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes
- **Same-day comparison:** a round-2 re-entry on the same stock at 09:55 also stopped (entry below).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — breakdown did not follow through; stopped within 10 minutes.
- **Evidence:** entry 09:35, stop exit 09:45; MFE +₹32.00 against a −₹98.00 stop distance.
- **Has history seen this before?** Yes — the INV1 scorecard's dominant failure mode: Jan–Oct 2026 stored population (694 trades) has 446 stops (64.3%), of which 215 landed within ≤15 minutes of entry (31.0% of all trades). Today's INV1 card repeated the pattern (5 stops in 8 trades, 4 of them within ≤10 minutes).
- **The fix:** two candidates tested tonight from this diagnosis — STOCKS-EVE-02 (skip event_window trades) GATE FAIL (placebo + May flip) and STOCKS-EVE-03 (LONG-only) GATE FAIL (June/August flips + cross-year unverifiable). Status: NO FIX promoted — accepted risk under the frozen scorecard; a rejected variant is never retested identically.
- **Lesson ID:** RSI-STOCKS-003

## 2026-11-02 · NATIONALUM · SHORT · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (as above)
- **Basis for the trade:** INV1 condition met; setup3_bounce_rejection signal, entry 09:40 @ ₹322.00 (ADR 3.091; no event recorded in the scorecard; note the live calendar flags NATIONALUM results dated 2026-11-02 with reaction day 2026-11-03 — the scorecard row itself records event_status no_event).
- **Market context at entry:** regime DOWN; metals were the day's strong pocket — a short in a metal name was against the day's sector flow.
- **Entry:** 09:40 @ ₹322.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹323.61 · target ₹317.98 · square-off 15:10
- **What actually happened:** MFE +₹20.00 (low 321.80); reversed straight to the stop. MAE −₹175.00 (bar high 323.75, past the stop).
- **Exit:** 09:50 @ ₹323.61 — STOP
- **Result:** −₹201.00 net after ₹40 cost · SCORECARD money
- **Rules followed exactly?** yes
- **Same-day comparison:** the book took no NATIONALUM trade; its metal exposure today was long (F4), which worked.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race, against the day's sector trend.
- **Evidence:** stop in 10 minutes; MFE +₹20.00 vs stop distance −₹161.00.
- **Has history seen this before?** Yes — same INV1 quick-stop count as above (215 of 694 trades stopped within ≤15 minutes). Setup-level: setup3_bounce_rejection in the stored INV1 population is 79 trades, net −₹2,587.18 — a historically weak setup inside the scorecard, noted, not acted on tonight (the scorecard is frozen).
- **The fix:** NO FIX — feeds Lesson RSI-STOCKS-003's accepted-risk record; tonight's two INV1 candidates (EVE-02/EVE-03) both failed the gate.
- **Lesson ID:** RSI-STOCKS-003

## 2026-11-02 · TVSMOTOR · SHORT · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (as above)
- **Basis for the trade:** INV1 condition met; skill_or_breakdown signal, entry 09:40 @ ₹4,180.80 (ADR 3.08; event_window flagged in the scorecard).
- **Market context at entry:** regime DOWN; an event-window name — the class the goal description says is checked first.
- **Entry:** 09:40 @ ₹4,180.80 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹4,201.70 · target ₹4,128.54 · square-off 15:10
- **What actually happened:** Price first dipped to 4171.30 (MFE +₹950.00 — about 18% of the way to target), then reversed violently: bar highs reached 4217.00 (MAE −₹3,620.00) before the stop fill at the stop level. The day's largest scorecard loss, driven by the stock's high absolute price (₹20.90/share adverse = ₹2,090 gross per 100 shares).
- **Exit:** 09:50 @ ₹4,201.70 — STOP
- **Result:** −₹2,130.40 net after ₹40 cost · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes
- **Same-day comparison:** no book trade in this name today.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race in an event-window name — breakdown reversed within 10 minutes after a partial favourable move.
- **Evidence:** MFE +₹950.00 then stop at 09:50, two bars after entry; event_window flag on the row.
- **Has history seen this before?** Yes, in both parts: INV1 quick stops 215/694 (≤15 min); and the event_window slice of the stored INV1 population is 199 trades netting −₹197.05 (vs no_event 495 trades, +₹23,161.35) — the event slice is historically flat-to-negative, which is exactly what tonight's candidate tested.
- **The fix:** TESTED tonight — STOCKS-EVE-02 (skip INV1 event_window trades): GATE FAIL. Net improves only +₹197.05 (+₹22,964.30 → +₹23,161.35) while dropping 199 trades; the chronological placebo (skip the first 199 trades) scores +₹40,498.53 and beats it clearly; May flips green→red (+₹2,926.59 → −₹3,092.92); H2 falls ₹15,709.29 → ₹13,062.93; and the cross-year leg is unverifiable (no 2025 standalone INV1 file with event flags exists in the stored data). Never retest identically.
- **Lesson ID:** RSI-STOCKS-003

## 2026-11-02 · UNITDSPR · LONG · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (as above)
- **Basis for the trade:** INV1 condition met; skill_or_breakout signal, entry 09:40 @ ₹1,346.30 (ADR 3.478; event_window flagged).
- **Market context at entry:** regime DOWN.
- **Entry:** 09:40 @ ₹1,346.30 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹1,339.57 · target ₹1,363.13 · square-off 15:10
- **What actually happened:** Small favourable probe (MFE +₹180.00, high 1348.10), then a slide through the stop; MAE −₹770.00 (low 1338.60, past the stop level).
- **Exit:** 10:00 @ ₹1,339.57 — STOP
- **Result:** −₹713.15 net after ₹40 cost · SCORECARD money
- **Rules followed exactly?** yes (scorecard construction; note the whole book's v2 law deletes INV-LONG × UNITDSPR — that law binds the book, not this raw scorecard population, and the distinction is recorded here rather than silently merged).
- **Same-day comparison:** no book trade in this name (the book law above is why).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / stop-before-target race — breakout faded within 20 minutes, in an event-window name.
- **Evidence:** MFE +₹180.00 vs target distance +₹1,683.00; stop at 10:00.
- **Has history seen this before?** Yes — INV1 quick-stop pattern (215/694 ≤15 min; this one took 20) and the flat event_window slice (−₹197.05 over 199 trades).
- **The fix:** TESTED tonight as part of the same diagnosis — STOCKS-EVE-02 GATE FAIL (see TVSMOTOR entry). NO FIX promoted.
- **Lesson ID:** RSI-STOCKS-003

## 2026-11-02 · KALYANKJIL · LONG · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (as above)
- **Basis for the trade:** INV1 condition met; skill_or_breakout signal, entry 09:45 @ ₹503.70 (ADR 3.678; no event).
- **Market context at entry:** regime DOWN.
- **Entry:** 09:45 @ ₹503.70 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹501.18 · target ₹510.00 · square-off 15:10
- **What actually happened:** Ran to 508.85 (MFE +₹515.00 — 82% of the way to the 510.00 target) but never touched the target, then slowly gave almost everything back; MAE −₹235.00 intraday; squared off at 504.60.
- **Exit:** 15:10 @ ₹504.60 — SQUARE-OFF
- **Result:** +₹50.00 net after ₹40 cost (gross +₹90.00) · SCORECARD money
- **Rules followed exactly?** yes
- **Same-day comparison:** no book trade in this name (KALYANKJIL sits in the book's INV base exclusion set; the scorecard scores the raw population).

### If the trade won
- **Why it worked:** the breakout direction was right and the stop was never threatened after the early dip — but only just: this is a near-miss, not a clean win.
- **Give-back check:** FAILED the spirit of the check — captured ₹90.00 of +₹515.00 MFE (17%). Cause class: slow give-back (exit-rule shape, entry was right) — the frozen T125 target sat ₹1.15 above the day's high. Logged as exit-tuning evidence under Lesson RSI-STOCKS-004; no candidate was built on a single day tonight, and the frozen scorecard is unchanged.

## 2026-11-02 · WIPRO · SHORT · SCORECARD (INV1, round 2)

- **Strategy in play:** INV1 scorecard, round-2 re-entry (the frozen scorecard allows re-entry; the one-and-done rule belongs to index options, not equity cash)
- **Basis for the trade:** INV1 condition met; skill_or_breakdown signal again after the round-1 stop, entry 09:55 @ ₹196.02 (ADR 3.373; no event).
- **Market context at entry:** regime DOWN; the name had already refused to break down once this morning.
- **Entry:** 09:55 @ ₹196.02 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹197.00 · target ₹193.57 · square-off 15:10
- **What actually happened:** MFE +₹6.00 only (low 195.96); reversed to the stop by 10:15. MAE −₹188.00 (bar high 197.90).
- **Exit:** 10:15 @ ₹197.00 — STOP
- **Result:** −₹138.01 net after ₹40 cost · SCORECARD money
- **Rules followed exactly?** yes
- **Same-day comparison:** round 1 on the same stock lost −₹137.92 (above); the pair cost the scorecard −₹275.93.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — a repeat breakdown attempt in a name that had already shown no downside follow-through.
- **Evidence:** MFE +₹6.00 in 20 minutes; second stop of the morning on the same stock/direction.
- **Has history seen this before?** Yes — the quick-stop pattern (215/694 ≤15 min). On the re-entry axis specifically, history does NOT support a ban: round-2 trades in the stored INV1 population are 160 trades netting +₹2,757.20 (positive), so a round-2 skip was diagnosed and refused before scoring tonight — recorded so it is not re-proposed as new.
- **The fix:** NO FIX — accepted risk (diagnosis-refused family, evidence above).
- **Lesson ID:** RSI-STOCKS-003

## 2026-11-02 · VEDL · LONG · SCORECARD (INV1, round 1)

- **Strategy in play:** INV1 scorecard (as above)
- **Basis for the trade:** INV1 condition met; skill_or_breakout signal, entry 10:15 @ ₹242.54 (ADR 3.06; event_window flagged — an event-window trade that worked, recorded against any one-sided reading of today's event losses).
- **Market context at entry:** regime DOWN; metals strong.
- **Entry:** 10:15 @ ₹242.54 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹241.33 · target ₹245.57 · square-off 15:10
- **What actually happened:** Shallow MAE −₹59.00, then a steady climb; target reached in the 13:45 bar (bar high 245.66). MFE +₹312.00.
- **Exit:** 13:45 @ ₹245.57 — TARGET
- **Result:** +₹263.17 net after ₹40 cost (gross +₹303.17) · full-target? yes · SCORECARD money
- **Rules followed exactly?** yes (scorecard construction; the book's INV base exclusion set contains VEDL, so the book took no equivalent trade — distinction recorded).
- **Same-day comparison:** book metal longs (F4 HINDCOPPER/HINDZINC) also hit target — the sector read was consistent across components.

### If the trade won
- **Why it worked:** breakout follow-through in the day's leading sector, in the component's DOWN-regime home conditions.
- **Give-back check:** captured ₹303.17 of +₹312.00 MFE (97%) at the target. Clean.

---

# 2026-11-03 — Day 2 (regime FLAT in the live-shadow producer; Nifty prior close vs 50DMA no longer DOWN, so the INV1 condition did not fire and there are no INV1 rows today). All figures provisional per 100 shares, ₹40/trade, paper only, real money ₹0. MFE/MAE from the same sarvaritu_fwd 5-min candles the loggers used, scanned from the bar after entry per the frozen P2F-family convention.

## 2026-11-03 · GODREJCP · SHORT · PRIMARY (whole book, R2-LOWBAND component)

- **Strategy in play:** R2-LOWBAND (P2F family, low band at R+2), frozen SarvaRitu whole book (T125/S050)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results board 2026-10-29 after-market → reaction Fri 2026-10-30: −2.27% (close 818.00 vs 837.00), inside the frozen R2-LOWBAND band [2.0%, 2.5%); entry at R+2, Tue 2026-11-03, at the 09:15 open per the frozen spec (live-shadow producer record; whole-book log matches). A reader can re-derive this from `stocks_sarvaritu_live_shadow_log.csv` (2026-11-03 row) + the frozen spec.
- **Market context at entry:** Regime FLAT. Same name, same direction as yesterday's P2F shadow-scorecard trade, which had already stopped in one bar — the family took the second leg of the same event anyway, per the frozen rules.
- **Entry:** 09:15 @ ₹823.70 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹827.82 (+0.50% against) · target ₹813.41 (−1.25%) · square-off 15:10
- **What actually happened:** In the scanned window (from the 09:20 bar) price never went favourable: the 09:20 bar's low was 824.95 (MFE −₹125.00 — still above the entry for a short) and its high 829.70 hit through the stop (MAE −₹600.00). The unscanned entry bar itself had dipped to 820.05, which the frozen convention does not count.
- **Exit:** 09:20 @ ₹827.82 — STOP (one bar after entry)
- **Result:** −₹451.85 net after ₹40 cost · full-target? no
- **Rules followed exactly?** Yes — frozen R+2 low-band entry and stop-first scan from the bar after entry.
- **Same-day comparison:** The TUNED SHADOW v1 (N4-V3 one-sided cap) had no N4-V3 signal to act on today (ITC +0.113% and NATIONALUM −0.869% both below the frozen 1.0% trigger), so the shadow neither took nor skipped this trade — it is an N4-V3-component shadow only.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the P2F family's recurring one-bar stop-out, repeated on the same stock and event as yesterday's scorecard loss.
- **Evidence:** entry 09:15 @ 823.70; 09:20 bar high 829.70 through stop 827.82; zero favourable excursion in the scanned window.
- **Has history seen this before?** Yes — this is Lesson RSI-STOCKS-002's cause, second consecutive day. Stored Jan–Oct 2026 family universe (87 trades: P2F 46 + P2F-R2 34 + R2-LOWBAND 7): 25 stops within ≤15 minutes of entry. R2-LOWBAND standalone is thin (7 trades, +₹1,260.78 in 2026; in the c24 book dumps its 2025 family rows sit inside a family subtotal of +₹7,050.76 over 57 rows) — the component's evidence base is small and December forward data is its arbiter.
- **The fix:** TESTED tonight, twice, both GATE FAIL — STOCKS-EVE-04 (skip a family entry if the same stock's last family trade within 10 days was a loser): +₹27,293.58 → +₹20,751.65, the cooldown drops 17 trades worth +₹6,541.93 net because the family's next trade on a name usually recovers; cross-year also fails (2026 family subtotal degrades on the c24 basis). STOCKS-EVE-05 (same cooldown, triggered only by a prior QUICK stop ≤15 min): +₹27,293.58 → +₹23,231.94, ex-top-3 falls, cross-year unverifiable (book dumps carry no exit times). Status: NO FIX promoted — accepted risk under the frozen book; neither variant may be retested identically. The skip-the-opening-bar fix for this same shape was already rejected on 2026-11-02 (STOCKS-FIX-01).
- **Lesson ID:** RSI-STOCKS-002 (recurrence — same lesson, second day)

## 2026-11-03 · NTPC · LONG · SHADOW SCORECARD (P2F)

- **Strategy in play:** P2F shadow scorecard (separate November component scorecard; NOT a whole-book trade — the whole book's P2F cell for this event is not the R+1 ≥2.00% scorecard form scored here)
- **Basis for the trade:** Q2 FY27 results filed Sat 2026-10-31 → reaction Mon 2026-11-02: +2.13% (close 323.00 vs 316.25 on 2026-10-30), qualifying ≥2.00% LONG under the shadow scorecard rule; R+1 entry Tue 2026-11-03 at the 09:15 open per the frozen scorecard spec (`stocks_p2f_november_shadow_log.csv`, 2026-11-03).
- **Market context at entry:** Regime FLAT. The stock had already faded from its results spike on the reaction day itself (the book's N4-V3 trade on this name stopped yesterday).
- **Entry:** 09:15 @ ₹323.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹321.38 (−0.50%) · target ₹327.04 (+1.25%) · square-off 15:10
- **What actually happened:** In the scanned window (from the 09:20 bar) price never traded above entry: 09:20 bar high 322.15 (MFE −₹85.00), low 319.90 through the stop (MAE −₹310.00). The unscanned entry bar's low was 317.85.
- **Exit:** 09:20 @ ₹321.38 — STOP
- **Result:** −₹201.50 net after ₹40 cost · full-target? no · SHADOW SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — scan from the bar after entry, stop before target, per the frozen scorecard convention.
- **Same-day comparison:** the whole book took no NTPC trade today; its only trade was the R2-LOWBAND GODREJCP short above, which stopped the same way.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — third P2F-family one-bar stop-out in two days (GODREJCP scorecard Mon, GODREJCP book + NTPC scorecard Tue).
- **Evidence:** entry 09:15 @ 323.00; 09:20 bar low 319.90 through stop 321.38; no favourable excursion in the scanned window.
- **Has history seen this before?** Yes — same family count as above (25 of 87 stored trades stop within ≤15 minutes).
- **The fix:** Same tonight's tests — STOCKS-EVE-04 and STOCKS-EVE-05 both GATE FAIL (see the GODREJCP book entry). NO FIX promoted — accepted risk; the frozen scorecard is unchanged.
- **Lesson ID:** RSI-STOCKS-002 (recurrence)

---

## 2026-11-04 · ITC · LONG · P2F (SarvaRitu whole book; same signal scored in the P2F shadow scorecard)

- **Strategy in play:** P2F (results-reaction follow, R+1 entry), frozen SarvaRitu book, T125/S050 geometry on this cell (scorecard basis identical today)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Mon 2026-11-02 after-market → reaction Tue 2026-11-03 +2.82% (close 273.90 vs 266.40 on 2026-11-02), inside the frozen book band (≥2.5%) → R+1 entry Wed 2026-11-04 at the 09:15 open, per the frozen P2F rule (`stocks_p2f_november_shadow_log.csv`, 2026-11-04 row).
- **Market context at entry:** Book regime FLAT (REGIME-CLASSIFIER-1). Nifty prior close (2026-11-03) 23810.85, above its 50DMA 23233.58 (computed from the forward data root) — the frozen gate uses the prior close.
- **Entry:** 09:15 @ ₹272.90 (09:15 bar open) · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹271.54 (−0.50%) · target ₹276.31 (+1.25%) · square-off 15:10
- **What actually happened:** One-bar resolution: the 09:20 bar ran to a high of 283.15 (MFE +₹1,025.00 in the scanned window) and hit the target; in the scanned window price never traded below entry (MAE +₹685.00, i.e. no adverse excursion after the entry bar).
- **Exit:** 09:20 @ ₹276.31 — TARGET
- **Result:** +₹301.12 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes — scan from the bar after entry, stop before target, per the frozen convention; recomputed from candles tonight to within ₹0.12 of the logged net.
- **Same-day comparison:** the P2F shadow scorecard took the identical trade (+₹301.12); its T10 shadow target (275.63) also hit on the same bar for +₹232.90. TUNED SHADOW v1 (N4-V3 cap) had no signal today.

### If the trade won
- **Why it worked:** the reaction-day follow-through was immediate and one-directional — the frozen R+1 entry caught a genuine second-day continuation, not a fade.
- **Give-back check:** captured ₹341.00 gross of a +₹1,025.00 excursion — the T125 target caps the upside on spike bars. Logged as exit-tuning evidence only: tonight's STOCKS-EVE-08 shows shrinking the target to T100 loses money across the family, and no larger-target variant was tested tonight, so no change is inferred from one bar.

## 2026-11-04 · NATIONALUM · SHORT · P2F (SarvaRitu whole book; same signal scored in the P2F shadow scorecard)

- **Strategy in play:** P2F (results-reaction follow, R+1 entry), frozen SarvaRitu book, T125/S050
- **Basis for the trade (why this trade, why then):** Q2 FY27 results + interim dividend ₹4.50 filed Mon 2026-11-02 after-market → reaction Tue 2026-11-03 −3.19% (close 317.55 vs 328.00), inside the frozen book band (≥2.5%) → R+1 SHORT entry Wed 2026-11-04 at the 09:15 open.
- **Market context at entry:** Book regime FLAT; Nifty prior close above 50DMA (see ITC entry).
- **Entry:** 09:15 @ ₹317.55 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹319.14 (+0.50% adverse) · target ₹313.58 (−1.25%) · square-off 15:10
- **What actually happened:** The 09:20 bar dropped to a low of 313.75 — MFE +₹380.00, missing the T125 target (313.58) by ₹0.17 — then price reversed; the 09:40 bar's high of 320.30 hit the stop (MAE −₹275.00).
- **Exit:** 09:40 @ ₹319.14 — STOP
- **Result:** −₹198.77 net after ₹40 cost · full-target? no
- **Rules followed exactly?** yes — recomputed from candles tonight to within ₹0.23 of the logged net.
- **Same-day comparison:** the P2F shadow scorecard took the identical trade (−₹198.77); its T10 shadow target (314.37) WAS hit on the 09:20 bar → +₹277.55 shadow. That single-day contrast fed tonight's STOCKS-EVE-08 test — which FAILED the gate (below), so the T10 form is not promoted.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** stop-before-target race, near-miss form — the move reached 96% of the target distance in one bar, stalled ₹0.17 short, and reversed through the stop.
- **Evidence:** entry 09:15 @ 317.55; 09:20 bar low 313.75 vs target 313.58; 09:40 bar high 320.30 through stop 319.14.
- **Has history seen this before?** Yes, but rarely: in the stored 87-trade P2F family, 40 trades exited on stop, and only 3 of the 87 first ran ≥75% of the way to target before stopping (counted tonight by rescanning the stored family from candles). This is a known tail shape of the family, not its dominant failure mode.
- **The fix:** STOCKS-EVE-08 — P2F family target T125 → T100, stops unchanged — tested tonight under the full gate: **GATE FAIL** (net leg: +₹27,284.00 rescan basis → +₹19,750.00; both halves and ex-top-3 fall; the smaller target caps the 41 stored target-winners by more than it saves on stops). NO FIX promoted — accepted risk.
- **Lesson ID:** RSI-STOCKS-006

## 2026-11-04 · NTPC · LONG · R2-LOWBAND (SarvaRitu whole book)

- **Strategy in play:** R2-LOWBAND (low-band reaction, R+2 entry), frozen SarvaRitu book, T125/S050
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Sat 2026-10-31 → reaction Mon 2026-11-02 +2.13% (close 323.00 vs 316.25 on 2026-10-30), inside the frozen low band (2.0–2.5%, below the P2F book band) → R+2 entry Wed 2026-11-04 at the 09:15 open, per the frozen R2-LOWBAND rule. The C23 stand-aside (regime UP) did not apply — regime FLAT.
- **Market context at entry:** Book regime FLAT; this name has now been traded by three different frozen cells in three days (N4-V3 Mon, P2F scorecard Tue, R2-LOWBAND today) — each fired exactly as specified.
- **Entry:** 09:15 @ ₹320.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹318.40 (−0.50%) · target ₹324.00 (+1.25%) · square-off 15:10
- **What actually happened:** No follow-through at all: best excursion +₹30.00, drift down through the morning, stop touched on the 10:20 bar (MAE −₹215.00).
- **Exit:** 10:20 @ ₹318.40 — STOP
- **Result:** −₹200.00 net after ₹40 cost · full-target? no
- **Rules followed exactly?** yes — matches the live-shadow producer exactly (entry 320.00, stop exit 10:20).
- **Same-day comparison:** no scorecard equivalent (R2-LOWBAND is a book cell; the P2F scorecard's NTPC trade was yesterday's, −₹201.50).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop — a two-day-old reaction with no remaining momentum; price never threatened the target.
- **Evidence:** MFE only +₹30.00 across 65 minutes; steady drift to the stop by 10:20.
- **Has history seen this before?** The R2-LOWBAND stored population is tiny (7 trades, 3 stops; in-book c24 rows: 2 in 2025, 3 in 2026), so no reliable frequency exists for this cell alone; at family level the P2F family's dominant loss shape is the stop exit (40 of 87 stored trades).
- **The fix:** none new tonight — the family-level fixes for repeat stop-outs (STOCKS-EVE-04 loser cooldown, STOCKS-EVE-05 quick-stop cooldown) already FAILED the gate on 2026-11-03, and a 7-trade cell cannot support its own candidate. NO FIX — accepted risk.
- **Lesson ID:** RSI-STOCKS-007

## 2026-11-04 · HINDCOPPER · LONG · INV-ABOVE (SarvaRitu whole book)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction: p2 population + g1 gate pick), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade (why this trade, why then):** The frozen C22 construction — the name qualified in the p2 population (chain round ≤2, entry before 10:30, ADR ≥ 3.0) and was the g1 gate's pick for the day; LONG only, with the v2 law exclusions applied (HINDCOPPER is not excluded). Entry at the 09:35 bar open per the chain convention.
- **Market context at entry:** Book regime FLAT. Note the book's INV-LONG cell stands aside on FLAT days (C24), but INV-ABOVE carries no FLAT stand-aside in the frozen law — the distinction is the spec's, applied as written. Nifty prior close above 50DMA.
- **Entry:** 09:35 @ ₹400.10 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹398.10 (−0.50%) · target ₹405.10 (+1.25%) · square-off 15:10
- **What actually happened:** Clean follow-through: MFE +₹525.00, and in the scanned window price never materially traded below entry (MAE +₹105.00); target hit on the 10:15 bar.
- **Exit:** 10:15 @ ₹405.10 — TARGET
- **Result:** +₹460.12 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes — recomputed from candles tonight to within ₹0.12 of the logged net.
- **Same-day comparison:** HINDCOPPER is the book's repeat winner this week (INV-LONG + F4 on Mon, both target). The INV1 scorecard took no trades today (its DOWN-regime condition was not met — Nifty prior close above the 50DMA).

### If the trade won
- **Why it worked:** the g1 gate pick again selected the day's strongest metal name and the move followed through without an adverse excursion — the same shape as Monday's HINDCOPPER wins.
- **Give-back check:** captured ₹500.12 gross vs MFE +₹525.00 — essentially full capture; no give-back.

## 2026-11-04 · GLENMARK · LONG · INV-ABOVE (SarvaRitu whole book)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade (why this trade, why then):** Same frozen C22 construction as the HINDCOPPER entries — p2 population qualification (round ≤2, entry before 10:30, ADR ≥ 3.0) with the g1 gate active; LONG. The (F4/N4-V3, GLENMARK, SHORT) v2 exclusion does not apply to an INV-ABOVE LONG.
- **Market context at entry:** Book regime FLAT; entry at 10:10, the latest of today's three INV-ABOVE entries.
- **Entry:** 10:10 @ ₹2,418.20 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹2,406.11 (−0.50% = −₹1,209.00 per 100 shares — the widest rupee stop in the book today, purely because of the share price) · target ₹2,448.43 (+1.25%) · square-off 15:10
- **What actually happened:** The 10:15 bar ran to a high of 2426.30 (MFE +₹810.00, only a third of the target distance), then the name reversed; the stop was hit on the 10:25 bar (MAE −₹1,210.00).
- **Exit:** 10:25 @ ₹2,406.11 — STOP
- **Result:** −₹1,249.10 net after ₹40 cost · full-target? no — the day's largest loss, and larger than the day's three winners combined.
- **Rules followed exactly?** yes — recomputed from candles tonight to within ₹0.10 of the logged net; the size of the loss is the frozen geometry applied to a ₹2,418 share, not a deviation.
- **Same-day comparison:** the other two INV-ABOVE trades today both hit target (+₹460.12, +₹465.69) — the component was 2-of-3 today and still net negative because of this trade's rupee size.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop (reversal through the stop after a modest excursion), with rupee-size amplification — at a ₹2,418 entry, the standard 0.5% stop is a ₹1,209 gross loss per 100 shares.
- **Evidence:** MFE +₹810.00 at 10:15 (high 2426.30 vs target 2448.43); stop 2406.11 hit by 10:25.
- **Has history seen this before?** Yes — the size shape is structural: across the c24 book dumps, INV-ABOVE lost 133 of 206 trades, and all 12 losses of ₹1,000 or more belong to the two high-priced names, GLENMARK and TVSMOTOR. GLENMARK's own INV-ABOVE history is split by year: 2025 −₹6,182.42 over 23 trades, 2026 +₹331.87 over 3 trades (including a +₹2,442.62 winner — its winners are as outsized as its losers).
- **The fix:** two mechanically distinct candidates tested tonight, both **GATE FAIL**: STOCKS-EVE-06 (skip INV-ABOVE entries priced ≥ ₹1,500 — the dropped high-price sets are net POSITIVE in both years, +₹2,035.85 in 2025 and +₹2,931.22 in 2026; the chronological placebo beats the variant in both years; month flips) and STOCKS-EVE-07 (skip INV-ABOVE entries at/after 10:00 — the late bucket earns +₹1,597.28 in 2025 and +₹3,220.95 in 2026; net falls in both years). NO FIX promoted — accepted risk: the frozen geometry's rupee variance on high-priced names is the price of their equally large winners.
- **Lesson ID:** RSI-STOCKS-005

## 2026-11-04 · HINDCOPPER · LONG · INV-ABOVE round 2 (SarvaRitu whole book)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050 — second chain round on the same name, permitted by the frozen construction (round ≤2)
- **Basis for the trade (why this trade, why then):** The name re-qualified in the p2 population on its second chain round after the first round's target exit, with the g1 gate still active; entry at the 10:20 bar open.
- **Market context at entry:** Book regime FLAT; the name was the day's clear momentum leader (already +1 target on the day).
- **Entry:** 10:20 @ ₹404.55 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹402.53 (−0.50%) · target ₹409.61 (+1.25%) · square-off 15:10
- **What actually happened:** Follow-through continued: MFE +₹775.00, worst excursion only −₹110.00; target hit on the 11:55 bar.
- **Exit:** 11:55 @ ₹409.61 — TARGET
- **Result:** +₹465.69 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes — recomputed from candles tonight to within ₹0.31 of the logged net.
- **Same-day comparison:** with the 09:35 round, HINDCOPPER INV-ABOVE contributed +₹925.81 of today's book; the component's day was still dragged negative by GLENMARK's rupee size (see above).

### If the trade won
- **Why it worked:** same-name momentum continuation — the second-round re-entry, which the frozen construction explicitly permits, caught the next leg of the same move.
- **Give-back check:** captured ₹505.69 gross vs MFE +₹775.00 — the target was hit on a bar that ran further; standard T125 capture, no defect.

# 2026-11-05 — Day 4 (regime FLAT; Nifty prior close 23960.6 vs 50DMA 23227.75 — prior close above, so the INV1 condition did not fire and there are no INV1 rows today). All figures provisional per 100 shares, ₹40/trade. Candle verification: `stocks_eve_2026-11-05.py` Part A (fwd candles) — every book net below recomputed to within ₹0.45 (level rounding only).

## 2026-11-05 · ITC · LONG · P2F-R2 (SarvaRitu whole book)

- **Strategy in play:** P2F-R2 (R+2 follow-through leg of the P2F family), frozen SarvaRitu book, T125/S050
- **Basis for the trade:** ITC's results reaction on Tue 2026-11-03 was +2.82% (close 273.90 vs 266.40), qualifying ≥2.00% LONG; the R+1 P2F leg traded Wed (+₹301.12 target) and the frozen R+2 leg takes the same direction again today at the 09:15 open. A reader can re-derive the entry from the family spec + the reaction-day close alone.
- **Market context at entry:** Book regime FLAT (Nifty prior close above its 50DMA).
- **Entry:** 09:15 @ ₹283.10 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹281.68 (−0.50%) · target ₹286.64 (+1.25%) · square-off 15:10
- **What actually happened:** No follow-through at all after the entry bar: in the scanned window the best excursion was −₹140.00 (never favourable) and the worst −₹275.00; the 09:20 bar hit the stop.
- **Exit:** 09:20 @ ₹281.68 — STOP
- **Result:** −₹181.55 net after ₹40 cost (recomputed −₹182.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent — the P2F shadow scorecard is the R+1 leg only; this R+2 leg trades in the whole book only.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the R+2 leg fired into a reaction that had already paid out on R+1; zero favourable excursion after entry.
- **Evidence:** entry 09:15, stop exit 09:20 (one bar later); MFE in the scanned window −₹140.00 against a −₹141.55 stop distance.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-002's shape, now on its third consecutive day (GODREJCP scorecard Nov 2, NTPC scorecard + GODREJCP book Nov 3, both R+2 legs today). Stored family universe: 25 of 87 trades stop within ≤15 minutes. BUT the R+2 legs as a bucket are historical earners: +₹14,173.26 over 41 stored trades (EVE-09 tonight) — the shape is frequent, the bucket is not bad.
- **The fix:** two candidates tested tonight from this diagnosis — STOCKS-EVE-09 (drop all R+2 legs) GATE FAIL (net + cross-year + month flip: the dropped legs earn +₹16,432.69 in 2026) and STOCKS-EVE-10 (widen family stop to 0.80%) GATE FAIL (net +₹27,284.00 → +₹21,753.00 rescan; the tighter-stop mirror control scored higher, +₹30,744.00 — noted as an observation only, not a candidate). Status: NO FIX promoted — accepted risk under the frozen book.
- **Lesson ID:** RSI-STOCKS-002 (recurrence — third day)

## 2026-11-05 · NATIONALUM · SHORT · P2F-R2 (SarvaRitu whole book)

- **Strategy in play:** P2F-R2, frozen SarvaRitu book, T125/S050
- **Basis for the trade:** NATIONALUM's results reaction on Tue 2026-11-03 was −3.19% (close 317.55 vs 328.00), qualifying ≥2.00% SHORT; R+1 leg traded Wed (stopped, −₹198.77); the frozen R+2 leg repeats the direction today at the 09:15 open.
- **Market context at entry:** Book regime FLAT.
- **Entry:** 09:15 @ ₹328.80 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹330.44 (+0.50%) · target ₹324.69 (−1.25%) · square-off 15:10
- **What actually happened:** A brief favourable dip (MFE +₹180.00 in the scanned window) reversed immediately; the 09:20 bar ran to a −₹440.00 adverse excursion and hit the stop.
- **Exit:** 09:20 @ ₹330.44 — STOP
- **Result:** −₹204.40 net after ₹40 cost (recomputed −₹204.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent (R+2 leg, book only). The same name's R+1 leg stopped yesterday — two family stops on one reaction, exactly as the frozen construction specifies.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — one-bar reversal through the stop after a +₹180.00 favourable print.
- **Evidence:** entry 09:15, stop exit 09:20; MFE +₹180.00 vs MAE −₹440.00 in the scanned window.
- **Has history seen this before?** Yes — same Lesson RSI-STOCKS-002 recurrence as ITC above (25 of 87 stored family trades stop within ≤15 minutes); the R+2 bucket itself is +₹14,173.26 over 41 trades, so the day is the bucket's known variance, not a bucket defect.
- **The fix:** STOCKS-EVE-09 and STOCKS-EVE-10 (above) — both GATE FAIL, neither retestable identically. NO FIX promoted.
- **Lesson ID:** RSI-STOCKS-002 (recurrence — third day)

## 2026-11-05 · NHPC · LONG · N4-V3 (SarvaRitu whole book; same signal in the N4-V3 primary scorecard)

- **Strategy in play:** N4-V3 event-reaction, frozen SarvaRitu book geometry T150/S080 (scorecard geometry T125/S050 scored alongside)
- **Basis for the trade:** NHPC Q2 FY27 results filed after-market Wed 2026-11-04 (consol PAT +35.95% YoY to ₹1,657.57 cr) → reaction day today; move by 09:30 = +3.937% (09:25 close 81.58 vs prior close 78.49) ≥ the frozen 1.0% trigger, direction LONG; entry at the close of the 09:30 bar, recorded 09:35.
- **Market context at entry:** Book regime FLAT.
- **Entry:** 09:35 @ ₹81.29 · per 100 shares (provisional basis)
- **Planned exits at entry:** book — stop ₹80.64 (−0.80%) · target ₹82.51 (+1.50%); scorecard — stop ₹80.88 (−0.50%) · target ₹82.31 (+1.25%); square-off 15:10
- **What actually happened:** Never favourable after entry (MFE −₹19.00 in the scanned window): the scorecard stop went at 09:40 and the wider book stop at 09:45 as the morning spike unwound.
- **Exit:** book 09:45 @ ₹80.64 — STOP; scorecard 09:40 @ ₹80.88 — STOP
- **Result:** book −₹105.03 net after ₹40 cost (recomputed −₹105.00); scorecard −₹80.65 (recomputed −₹81.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** the TUNED SHADOW v1 (one-sided cap) SKIPPED this trade — a LONG with signed move +3.937% ≥ +3.0% is exactly its one rule. Shadow saved the full loss on both bases (see the shadow ledger in the registry).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop after an outsized morning spike — the ≥+3% LONG bucket's known failure shape: the reaction was already fully priced by 09:30 and faded from the entry.
- **Evidence:** trigger +3.937%; MFE −₹19.00 (price never traded favourably after the entry bar); both geometries stopped within 10 minutes.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-001, the same cause as NTPC on Nov 2 (+3.178%): the ≥3% morning-move bucket is the component's only negative-average bucket (26 of 56 standalone trades; LONG ≥+3% negative in both 2025 and 2026 at book level).
- **The fix:** ALREADY FIXED by TUNED SHADOW v1 (one-sided cap, live since 2026-11-03) — today is its first live save: it skipped NHPC and avoided −₹105.03 (book basis) / −₹80.65 (scorecard basis). The frozen book itself is unchanged by design; December adoption is judged on the shadow's forward line.
- **Lesson ID:** RSI-STOCKS-001 (recurrence — and the shadow fix's first forward proof)

## 2026-11-05 · PFC · LONG · N4-V3 (SarvaRitu whole book; same signal in the N4-V3 primary scorecard)

- **Strategy in play:** N4-V3 event-reaction, frozen book geometry T150/S080 (scorecard T125/S050 alongside)
- **Basis for the trade:** PFC Q2 FY27 results filed intraday Wed 2026-11-04 (standalone PAT +11.8% YoY to ₹4,986.71 cr; 2nd interim dividend ₹4.10) → intraday announcement, so reaction day = today per spec; move by 09:30 = +1.039% (09:25 close 325.85 vs prior close 322.50) ≥ 1.0% trigger, LONG; entry at the 09:30 bar close, recorded 09:35.
- **Market context at entry:** Book regime FLAT.
- **Entry:** 09:35 @ ₹325.85 · per 100 shares (provisional basis)
- **Planned exits at entry:** book — stop ₹323.24 (−0.80%) · target ₹330.74 (+1.50%); scorecard — stop ₹324.22 (−0.50%) · target ₹329.92 (+1.25%); square-off 15:10
- **What actually happened:** A mid-morning dip took price through the scorecard's tighter stop (scorecard exit 10:35 @ ₹324.22) and to a book-basis MAE of −₹245.00 — ₹0.16 per share above the book stop — before the move resumed; MFE +₹515.00 and the book target was hit at 12:15.
- **Exit:** book 12:15 @ ₹330.74 — TARGET; scorecard 10:35 @ ₹324.22 — STOP
- **Result:** book +₹448.77 net after ₹40 cost (recomputed +₹449.00) · full-target? yes (book basis); scorecard −₹202.93 (recomputed −₹203.00)
- **Rules followed exactly?** yes — the divergence is the two frozen geometries working exactly as specified, not a deviation.
- **Same-day comparison:** TUNED SHADOW v1 TOOK this trade identically (LONG move +1.039% < +3.0%, cap not triggered): shadow +₹448.77 on the book basis, −₹202.93 on the scorecard basis.

### If the trade won
- **Why it worked:** a modest, un-extended reaction (+1.039%, inside the healthy trigger band) with real follow-through after one shake-out dip — the opposite shape to NHPC's extended spike.
- **Give-back check:** captured ₹489.00 gross of +₹515.00 MFE on the book basis — near-full capture, no defect. The day's real information is the geometry split: the same signal is a winner on T150/S080 and a loser on T125/S050, which fed STOCKS-EVE-11 tonight — GATE FAIL on the reproduction leg (the rescan could not reproduce the stored T125/S050 incumbent: +₹7,260.00 rescan vs +₹7,990.43 stored), so the apparent wide-stop gain is NOT quoted as a result and nothing was promoted.

## 2026-11-05 · HINDCOPPER · LONG · INV-ABOVE (SarvaRitu whole book)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade:** The name qualified in the p2 population with the g1 gate active; entry at the 10:25 bar open (₹434.15 — verified tonight as that bar's open in the fwd candles, and the logged stop is exactly −0.50% from it).
- **Market context at entry:** Book regime FLAT; the name was yesterday's momentum leader (two INV-ABOVE targets, +₹925.81) trading near its highs.
- **Entry:** 10:25 @ ₹434.15 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹431.98 (−0.50%) · target ₹439.58 (+1.25%) · square-off 15:10
- **What actually happened:** Immediate reversal: MFE −₹150.00 in the scanned window (never favourable after entry), MAE −₹220.00; the very next bar hit the stop.
- **Exit:** 10:30 @ ₹431.98 — STOP
- **Result:** −₹257.07 net after ₹40 cost (recomputed −₹257.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent — INV-ABOVE trades in the whole book only; the INV1 scorecard had no rows today (regime condition not met).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race on a follow-through-exhaustion entry — the name was bought the morning after its two-target momentum day, at the highs, and reversed within one bar.
- **Evidence:** entry 10:25, stop exit 10:30 (next bar); MFE −₹150.00 — the trade was never in profit after entry.
- **Has history seen this before?** Partially — INV-ABOVE's November record is now 4 trades with 2 fast stops (GLENMARK Nov 4, 15 minutes; this one, 5 minutes), but the c24 book dumps carry no exit times for the component, so a historical fast-stop frequency cannot be counted honestly; it is recorded as unverifiable rather than estimated. The component's two natural fixes (price cap, late-entry cut) were both gate-failed on 2026-11-04 (EVE-06/EVE-07).
- **The fix:** NO FIX — accepted risk: no mechanically distinct candidate remains for this component tonight that has not already failed the gate; the exhaustion-after-a-big-day shape is logged as a watch item for December forward evidence, not tuned on one day.
- **Lesson ID:** RSI-STOCKS-008

---

## 2026-11-06 — Day 5 (regime FLAT; Nifty prior close 24536.6 vs 50DMA 23234.10 — prior close above, so the INV1 condition did not fire and there are no INV1 rows today). All figures provisional per 100 shares, ₹40/trade. Candle verification: `stocks_eve_2026-11-06.py` Part A (fwd candles) — every net below recomputed to within ₹0.37 (level rounding only). The book's best day of November: 4 trades, 4 winners, day net +₹6,577.68. Two logger-scope divergences recorded, not adjusted: the N4-V3 scorecard traded ASTRAL (below) and the P2F shadow scorecard traded PFC (below), neither of which appears in today's whole-book log; the book log governs book MTD.

## 2026-11-06 · NHPC · LONG · P2F (SarvaRitu whole book; same trade in the P2F shadow scorecard)

- **Strategy in play:** P2F (R+1 follow-through leg of the P2F family), frozen SarvaRitu book, T125/S050
- **Basis for the trade:** NHPC's results reaction on Thu 2026-11-05 was +2.69% (close 80.60 vs 78.49), qualifying ≥2.00% LONG; the frozen R+1 leg takes that direction today at the 09:15 open. A reader can re-derive the entry from the family spec + the reaction-day close alone.
- **Market context at entry:** Book regime FLAT (Nifty prior close above its 50DMA).
- **Entry:** 09:15 @ ₹80.60 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹80.20 (−0.50%) · target ₹81.61 (+1.25%) · square-off 15:10
- **What actually happened:** Immediate follow-through: the 09:20 bar ran to a +₹225.00 scanned-window MFE and hit the target; the adverse excursion in the window was +₹183.00 (never adverse after the entry bar).
- **Exit:** 09:20 @ ₹81.61 — TARGET
- **Result:** +₹60.75 net after ₹40 cost (recomputed +₹61.00) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** the P2F shadow scorecard took the identical trade (+₹60.75; its T10 shadow column +₹40.60). The same name's second R+1 candidate today, PFC, traded only in the shadow scorecard (next-but-one entry below) — it does not appear in the whole-book log; divergence recorded, not adjusted.

### If the trade won
- **Why it worked:** a clean reaction-day follow-through — the R+1 leg's textbook shape: yesterday's +2.69% reaction extended straight into the target on the second bar.
- **Give-back check:** captured ₹101.00 gross of the +₹225.00 scanned-window MFE; the day high was ₹83.10 (+₹250.00 beyond entry), so a wider target would have captured more — one day's continuation, noted as exit-tuning colour only; the family's tighter-target variant was gate-failed on 2026-11-04 (EVE-08) and no wider-target family variant was registered tonight.

## 2026-11-06 · GLENMARK · LONG · INV-ABOVE (SarvaRitu whole book) — first entry

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade:** The name qualified in the p2 population with the g1 gate active; entry at the 09:35 bar open (₹2,486.60 — verified tonight as that bar's open in the fwd candles, and the logged exit is exactly the +1.25% target from it). Context: GLENMARK filed Q2 FY27 results post-market Thu 2026-11-05 (consol PAT −56.78% YoY) and gapped down at the open (09:15 open ₹2,365.50 vs prior close ₹2,481.80) before ripping upward through the morning — the INV-ABOVE entry rode the recovery, it was not a results-reaction trade.
- **Market context at entry:** Book regime FLAT; the name was the morning's strongest recovery on the watchlist.
- **Entry:** 09:35 @ ₹2,486.60 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹2,474.17 (−0.50%) · target ₹2,517.68 (+1.25%) · square-off 15:10
- **What actually happened:** One shallow dip (MAE −₹210.00 in the scanned window) then a straight run: MFE +₹4,240.00 by the exit bar; the 09:50 bar hit the target.
- **Exit:** 09:50 @ ₹2,517.68 — TARGET
- **Result:** +₹3,068.25 net after ₹40 cost (recomputed +₹3,068.00) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent — INV-ABOVE trades in the whole book only; the INV1 scorecard had no rows today (regime condition not met). The same name was blocked by the N4-V3 scorecard today (reaction −0.935%, below the 1.0% trigger) — a different frozen construction; the day's GLENMARK move was captured here instead.

### If the trade won
- **Why it worked:** genuine momentum with follow-through — the recovery from the results gap-down never paused at the entry level; the +1.25% target was reached in three bars with only a −₹210.00 dip against it.
- **Give-back check:** the stock's day high was ₹2,682.50 — it ran far beyond the target after exit. That is exit-tuning evidence, not an entry defect: the component's wider-target form (R2-26, T150/S080) is already flagged and awaiting Chandu's decision; it is not re-proposed on one day.

## 2026-11-06 · RECLTD · LONG · INV-ABOVE (SarvaRitu whole book)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade:** The name qualified in the p2 population with the g1 gate active; entry at the 09:35 bar open (₹296.25 — verified tonight as that bar's open, and the logged exit is exactly the +1.25% target from it).
- **Market context at entry:** Book regime FLAT.
- **Entry:** 09:35 @ ₹296.25 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹294.77 (−0.50%) · target ₹299.95 (+1.25%) · square-off 15:10
- **What actually happened:** A slow, steady climb with almost no adverse excursion (MAE −₹50.00 in the scanned window; MFE +₹465.00 by the exit bar); the target was hit at 10:25.
- **Exit:** 10:25 @ ₹299.95 — TARGET
- **Result:** +₹330.31 net after ₹40 cost (recomputed +₹330.00) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** no scorecard equivalent (INV-ABOVE is book-only; INV1 had no rows today).

### If the trade won
- **Why it worked:** the component's cleanest shape — qualification, then uninterrupted follow-through with the stop never threatened (−₹50.00 worst excursion against a −₹148.00 stop distance).
- **Give-back check:** near-full capture — the day high was ₹300.90, only ₹95.00 beyond the target exit. No defect.

## 2026-11-06 · GLENMARK · LONG · INV-ABOVE (SarvaRitu whole book) — second entry, same stock, same day

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen SarvaRitu book, PLAIN T125/S050
- **Basis for the trade:** The name qualified again after the first entry's target exit; the frozen construction permits same-day re-entry on a fresh qualification (no one-and-done rule in equity cash — that restriction belongs to options only). Entry at the 09:55 bar open (₹2,526.70 — verified as that bar's open; the logged exit is exactly its +1.25% target).
- **Market context at entry:** Book regime FLAT; the name was mid-trend after the first target.
- **Entry:** 09:55 @ ₹2,526.70 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹2,514.07 (−0.50%) · target ₹2,558.28 (+1.25%) · square-off 15:10
- **What actually happened:** Continuation, not exhaustion: MAE only −₹150.00 in the scanned window, MFE +₹3,460.00 by the exit bar; target hit at 10:20.
- **Exit:** 10:20 @ ₹2,558.28 — TARGET
- **Result:** +₹3,118.37 net after ₹40 cost (recomputed +₹3,118.00) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** the first GLENMARK entry above (+₹3,068.25) — the pair took +₹6,186.62 from one name in one morning, both full targets.

### If the trade won
- **Why it worked:** intraday momentum continuation — the second qualification came with the trend intact and the stop was never threatened. Tonight's STOCKS-EVE-13 tested the opposite hypothesis (cap the component at one entry per stock per day) on the full history: the repeat bucket earns +₹10,396.16 over 50 trades and the cap GATE FAILED in both years. Today is that bucket working as history says it does.
- **Give-back check:** the day high (₹2,682.50) ran beyond this exit too — same exit-tuning note as the first entry; no new candidate raised on it.
- **Lesson ID:** RSI-STOCKS-009 (new — same-day INV-ABOVE repeats are continuation, not exhaustion)

## 2026-11-06 · ASTRAL · SHORT · N4-V3 (primary scorecard only — not in today's whole-book log)

- **Strategy in play:** N4-V3 event-reaction, primary scorecard geometry T125/S050 (book geometry T150/S080 computed alongside for the shadow line)
- **Basis for the trade:** ASTRAL Q2 FY27 results filed Thu 2026-11-05 afternoon (consol PAT −5.9% YoY to ₹127 cr; interim dividend ₹1.50) → intraday announcement, so reaction day = today per spec; move by 09:30 = −10.000% (09:25 close ₹1,249.20 vs prior close ₹1,388.00) ≥ the frozen 1.0% trigger, direction SHORT; entry at the 09:30 bar close, recorded 09:35. ASTRAL entered the calendar only through the daily filing check per spec (it was one of the nine no-date stocks at freeze time).
- **Market context at entry:** Book regime FLAT; the name had already crashed at the open (09:15 bar low ₹1,260.00) — the short entered into an extended move, the mirror image of the ≥+3% LONG spike the one-sided cap exists for, on the uncapped side.
- **Entry:** 09:35 @ ₹1,249.20 · per 100 shares (provisional basis)
- **Planned exits at entry:** scorecard — stop ₹1,255.45 (+0.50%) · target ₹1,233.59 (−1.25%); book geometry — stop ₹1,259.19 (+0.80%) · target ₹1,230.46 (−1.50%); square-off 15:10
- **What actually happened:** Instant follow-through: the 09:35 bar itself ran to ₹1,215.50 (MFE +₹3,370.00 in the scanned window, MAE ₹0.00 — price never traded above the entry) and hit both geometries' targets on that bar.
- **Exit:** 09:35 @ ₹1,233.59 — TARGET (scorecard); book-geometry target ₹1,230.46 also hit on the same bar
- **Result:** scorecard +₹1,521.50 net after ₹40 cost (recomputed +₹1,521.00) · full-target? yes; book geometry +₹1,834.00 (recomputed, shadow line only)
- **Rules followed exactly?** yes
- **Same-day comparison:** TUNED SHADOW v1 TOOK this trade identically — its cap is one-sided (LONG ≥ +3.0% only; SHORTs are uncapped precisely because the ≥3% SHORT bucket carried 2026 earners, 9/10 winners in the banked analysis). The whole-book log does not contain an ASTRAL row today — a logger-scope divergence, recorded here and in the RSI log, not adjusted; book MTD is computed from the book log alone.

### If the trade won
- **Why it worked:** a genuine results-day collapse with immediate continuation — the −10% reaction extended straight through the target on the entry bar; the uncapped-SHORT design choice (FLOOR-2) earned its keep in forward evidence for the first time.
- **Give-back check:** the 09:35 bar low (₹1,215.50) ran ₹1,809.00 beyond the scorecard target — full target captured as specified; the overshoot is one bar's violence, not an exit defect.

## 2026-11-06 · PFC · LONG · P2F (shadow scorecard only — not in today's whole-book log)

- **Strategy in play:** P2F (R+1 follow-through leg), P2F shadow scorecard, T125/S050
- **Basis for the trade:** PFC's results reaction on Thu 2026-11-05 was +2.14% (close ₹329.40 vs ₹322.50), qualifying ≥2.00% LONG; the R+1 leg takes that direction today at the 09:15 open.
- **Market context at entry:** Book regime FLAT.
- **Entry:** 09:15 @ ₹328.50 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹326.86 (−0.50%) · target ₹332.61 (+1.25%) · square-off 15:10
- **What actually happened:** No follow-through at all: the entry bar itself fell to ₹323.70 and the scanned-window best excursion was −₹100.00 (never favourable); the 09:20 bar hit the stop.
- **Exit:** 09:20 @ ₹326.86 — STOP
- **Result:** −₹204.25 net after ₹40 cost (recomputed −₹204.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** the whole-book log does not contain this trade (the book took only NHPC of today's two R+1 names) — logger-scope divergence recorded, not adjusted. The name's N4-V3 signal was yesterday's book winner (+₹448.77) — a different component on a different day; no contradiction.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the R+1 leg fired into a reaction that did not extend; zero favourable excursion after entry.
- **Evidence:** entry 09:15, stop exit 09:20 (one bar later); scanned-window MFE −₹100.00 against a −₹164.00 stop distance; the entry bar's own low was ₹323.70.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-002's family shape: 25 of the 87 stored family trades stop within ≤15 minutes. The family bucket itself remains the earner (stored +₹27,293.58); today's split — NHPC target, PFC stop — is the family's normal variance on one reaction pair.
- **The fix:** the family candidate tested tonight from the standing queue was STOCKS-EVE-12 (tighten the family stop to 0.35%, the registered follow-up to EVE-10's mirror observation) — it improves every verifiable leg (rescan +₹27,284.00 → +₹30,744.00) but its cross-year leg is UNVERIFIABLE (the stored family population is 2026-only and the c24 dumps carry no exit geometry), so the gate outcome is FAIL and nothing was promoted. For this specific trade a 0.35% stop would have lost less (−₹155.00 recomputed scale), but one trade does not promote a rule.
- **Lesson ID:** RSI-STOCKS-002 (recurrence — fourth day, scorecard leg)

## 2026-11-09 — Day 6 (regime UP; Nifty prior regular close Fri 2026-11-06 ₹25,030.35 vs 50DMA ≈ ₹23,264 — prior close above, 50DMA rising, so the book's regime label is UP and the INV1 above-50DMA condition is the operative one). All figures provisional per 100 shares, ₹40/trade. Candle verification: `stocks_eve_2026-11-09.py` Part A (fwd candles, 75 bars per symbol — complete set, day SCORED) — every net below recomputed to within ₹0.50 (level rounding only). Book day: 4 trades, 2 winners / 2 losers, day net **+₹704.30**. One logger-scope divergence recorded, not adjusted: the whole book took N4-V3 TATASTEEL SHORT (below) while the standalone N4-V3 scorecard recorded TATASTEEL as no-trigger — the two constructions measure the trigger against different prior closes (book: the Sun 2026-11-08 Muhurat session close ₹190.20 carried in the fwd daily series → −1.225%; scorecard: Fri regular close ₹186.30, Muhurat excluded → +0.843%). The book log governs book MTD.

## 2026-11-09 · GLENMARK · LONG · PRIMARY (whole book, P2F-R2 component; identical execution scored as the P2F leg in the P2F shadow scorecard)

- **Strategy in play:** P2F-R2 (SarvaRitu whole book) — post-results follow-through, second leg of the P2F family; the same 09:15 execution is the P2F shadow scorecard's R+1 trade today.
- **Basis for the trade (why this trade, why then):** GLENMARK Q2 FY27 results filed Thu 2026-11-05 17:05 IST after-market (consol PAT −56.78% YoY) → reaction day Fri 2026-11-06 closed +4.36% (₹2,590.00 vs ₹2,481.80), qualifying ≥2.00% LONG despite the weak headline — the market's verdict was the reaction, not the headline. R+1 Mon 2026-11-09: entry at the 09:15 open per the frozen P2F spec.
- **Market context at entry:** regime UP; GLENMARK opened exactly at Friday's close (₹2,590.00) and held above its reaction-day range from the first bar.
- **Entry:** 09:15 @ ₹2,590.00 (09:15 bar open) · provisional per 100 shares
- **Planned exits at entry:** stop ₹2,577.05 (−0.50%) · target ₹2,622.38 (+1.25%) · square-off 15:10
- **What actually happened:** dipped to ₹2,572.20 on the entry bar (inside the entry bar, not scanned per spec), then climbed steadily; MFE +₹4,960.00 on the scanned window (09:25 bar high ₹2,639.60), MAE +₹200.00 favourable-side minimum — the stop was never threatened after the entry bar.
- **Exit:** 09:25 @ ₹2,622.38 — TARGET
- **Result:** +₹3,197.50 net after ₹40 cost · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** the P2F shadow scorecard scored the identical execution +₹3,197.50 (T10 shadow variant +₹2,550.00); the live-shadow producer matched entry, target and exit time exactly.

### If the trade won
- **Why it worked:** the reaction-day close (+4.36% on a bad headline) was genuine institutional follow-through, and the R+1 open offered the frozen entry with the trend already established — the family's best November trade so far, on the same name that paid the book +₹6,186.62 on Friday.
- **Give-back check:** captured the full frozen target; the stock ran on to a day high of ₹2,714.00 (+₹12,400.00 per 100 shares beyond entry) — noted as exit-geometry evidence only; the frozen T125 exit is not re-tuned on one day, and the same name's later INV-ABOVE entries (below) show what chasing the continuation cost today.

## 2026-11-09 · GLENMARK · LONG · PRIMARY (whole book, INV-ABOVE component) — first entry

- **Strategy in play:** INV-ABOVE (SarvaRitu whole book, Cycle-22 construction: intraday-reversal chain, round ≤2, entry before 10:30, ADR ≥3.0 gate, T125/S050)
- **Basis for the trade (why this trade, why then):** the frozen chain fired a LONG at the 09:35 bar after GLENMARK's morning reversal structure qualified under the C22 population + g1 gate; entry is the entry bar's open per the chain convention. A reader can re-derive it from the frozen chain + today's candles: 09:35 bar open ₹2,658.00, stop ₹2,644.71 and target ₹2,691.22 follow mechanically.
- **Market context at entry:** regime UP; the stock was already +2.6% on the day (₹2,658 vs ₹2,590 open) after the P2F target had paid at 09:25 — this was a continuation entry into an extended morning move, on the day's strongest name.
- **Entry:** 09:35 @ ₹2,658.00 (09:35 bar open) · provisional per 100 shares
- **Planned exits at entry:** stop ₹2,644.71 (−0.50%) · target ₹2,691.22 (+1.25%) · square-off 15:10
- **What actually happened:** the entry bar itself ranged ₹2,643.10–₹2,664.40 (its low already touched the stop); on the scanned post-entry window MFE was −₹460.00 (never favourable) and MAE −₹2,070.00; the 09:40 bar (low ₹2,637.30) closed the stop question.
- **Exit:** 09:40 @ ₹2,644.71 — STOP (stop level also touched on the entry bar's low)
- **Result:** −₹1,369.00 net after ₹40 cost · full-target? no
- **Rules followed exactly?** yes — the loss is the frozen geometry working as specified, not a deviation
- **Same-day comparison:** TUNED SHADOW v1 does not cover INV-ABOVE (it filters N4-V3 only) — no shadow equivalent; the book's own P2F-R2 leg on the same stock was already out with +₹3,197.50.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — a 0.50% stop (₹13.29) placed inside the entry bar's own range (₹21.30 wide) on a stock that then pulled back ~1% (to ₹2,632.70 at 09:30/09:40) before resuming to a day high of ₹2,714.00. The direction was right; the stop distance was smaller than the name's normal 5-minute noise after a +4% reaction day.
- **Evidence:** 09:35 bar low ₹2,643.10 ≤ stop ₹2,644.71; 09:40 bar low ₹2,637.30; day high ₹2,714.00 reached later — the trade was shaken out of a move that ultimately ran +₹5,600.00 per 100 shares beyond its entry.
- **Has history seen this before?** This is INV-ABOVE's modal loss: in the stored c24 populations (206 trades, both years) the S050 rescan counts 128 stop exits (62%); GLENMARK's own INV-ABOVE history is the component's worst name — 26 stored trades net −₹5,850.55 (2025: 23 tr, −₹6,182.42; 2026: 3 tr, +₹331.87). Recurring cause, therefore a fix candidate — tonight's EVE-15/16/17 all start here.
- **The fix:** three candidates tested tonight (see RSI log 2026-11-09): STOCKS-EVE-15 (widen stop to S080, T125 kept) GATE FAIL on the reproduction/construction leg; STOCKS-EVE-16 (drop INV-ABOVE when the stock already traded a P2F-family leg that day) GATE FAIL — the historical overlap is a single trade; STOCKS-EVE-17 (delete GLENMARK from INV-ABOVE) GATE FAIL on cross-year (2026 degrades). Status: NO GATE-PASSING FIX — the tight-stop shakeout stays as the component's accepted, measured cost for now; the frozen book is unchanged.
- **Lesson ID:** RSI-STOCKS-010

## 2026-11-09 · GLENMARK · LONG · PRIMARY (whole book, INV-ABOVE component) — second entry, same stock, same day

- **Strategy in play:** INV-ABOVE (SarvaRitu whole book) — the chain's second round on the same stock-day, which the frozen law permits (round ≤2) and Friday's evidence supported (Lesson RSI-STOCKS-009: repeats are continuation).
- **Basis for the trade (why this trade, why then):** after the first round stopped out, the chain re-qualified GLENMARK LONG at 09:40 (bar open ₹2,650.80); stop ₹2,637.55, target ₹2,683.93 follow mechanically from the frozen T125/S050 geometry.
- **Market context at entry:** regime UP; the stock was mid-pullback (₹2,661.10 high at 09:30 → ₹2,637.30 low at 09:40) inside a day that was still strongly positive.
- **Entry:** 09:40 @ ₹2,650.80 (09:40 bar open) · provisional per 100 shares
- **Planned exits at entry:** stop ₹2,637.55 (−0.50%) · target ₹2,683.93 (+1.25%) · square-off 15:10
- **What actually happened:** MFE −₹180.00 on the scanned window (never favourable), MAE −₹1,820.00; the 09:45 bar (low ₹2,632.60) hit the stop. The pullback bottomed at ₹2,632.60 and the stock then ran to ₹2,714.00.
- **Exit:** 09:45 @ ₹2,637.55 — STOP
- **Result:** −₹1,365.40 net after ₹40 cost (recomputed −₹1,365.00, level rounding) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** no shadow equivalent (TUNED SHADOW v1 is N4-V3 only). Pair total for the day's INV-ABOVE GLENMARK rounds: −₹2,734.40, against +₹3,197.50 on the same stock's P2F-R2 leg.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the same cause as the first round, five minutes later: the re-entry bought the pullback's middle, not its end, and the same 0.50% stop sat inside the next bar's range. Distinct from Friday's lesson: repeats earn at population level (EVE-13), but a repeat fired *while the first round's shakeout is still unfolding* inherits the same noise band.
- **Evidence:** 09:45 bar low ₹2,632.60 vs stop ₹2,637.55; day high ₹2,714.00 afterwards; the two rounds' combined excursion beyond entry was +₹11,000+ per 100 shares, of which the component captured none.
- **Has history seen this before?** Same count as the first entry — Lesson RSI-STOCKS-010's population (128/206 scanned stops). Same-day repeat pairs specifically: EVE-13 (2026-11-06) showed the 50 stored repeat entries earn +₹10,396.16 combined, so this pair is the bucket's variance, not its average.
- **The fix:** same three candidates as the first entry (EVE-15/16/17, all GATE FAIL tonight — see RSI log). A mechanically distinct follow-up is queued, not tested tonight: a same-stock re-entry delay (no second round until at least 3 bars after a first-round stop) — it differs from EVE-13's drop-the-repeat rule and from EVE-16's cross-component filter, and needs a chain-faithful replay before it can be scored.
- **Lesson ID:** RSI-STOCKS-010 (same lesson, second instance today)

## 2026-11-09 · TATASTEEL · SHORT · PRIMARY (whole book, N4-V3 component)

- **Strategy in play:** N4-V3 (SarvaRitu whole book; book geometry T150/S080, entry = 09:30 bar close, entry_time labelled 09:35 per `n4_raw`)
- **Basis for the trade (why this trade, why then):** TATASTEEL Q2 FY27 results approved Sat 2026-11-07 → reaction day Mon 2026-11-09 in the live calendar. In the book's own construction the trigger is the 09:25 close (₹187.87) against the prior daily close in the fwd series — the Sun 2026-11-08 Muhurat session close ₹190.20 — a −1.225% move, beyond the frozen 1.0% threshold, SHORT. Entry ₹187.47 is the 09:30 bar close exactly, per the frozen builder.
- **Market context at entry:** regime UP for the index, but TATASTEEL itself had gapped to ₹192.50 at the open and was already fading hard (09:25 close ₹187.87) — a stock-specific rejection of the results, against the index tape.
- **Entry:** 09:35 (labelled; price = 09:30 close) @ ₹187.47 · provisional per 100 shares
- **Planned exits at entry:** stop ₹188.97 (+0.80%) · target ₹184.66 (−1.50%) · square-off 15:10
- **What actually happened:** orderly fade all morning; MFE +₹289.00, MAE −₹123.00 (worst adverse was the 09:45 bar's ₹188.70 high, inside the stop); the 11:00 bar's low ₹184.58 reached the target.
- **Exit:** 11:00 @ ₹184.66 — TARGET
- **Result:** +₹241.20 net after ₹40 cost (recomputed +₹241.00) · full-target? yes
- **Rules followed exactly?** yes under the book's frozen construction — with the divergence defect noted in the day header: the standalone scorecard, measuring against Friday's regular close (₹186.30, Muhurat excluded), recorded +0.843% and no trade. Logged as a construction divergence between two frozen loggers, not adjusted in either.
- **Same-day comparison:** scorecard: no trade on TATASTEEL; its HINDALCO SHORT (below) is book-excluded by the frozen C10 law, so the two N4 ledgers legitimately differ today. TUNED SHADOW v1: SHORTs are uncapped, so the shadow takes this book trade identically (+₹241.20 book basis) and also takes the scorecard's HINDALCO SHORT identically (−₹508.20 scorecard basis).

### If the trade won
- **Why it worked:** the fade was real — an opening spike to ₹194.00 (day high, first bar) rejected after a qualified-audit-opinion results headline, then a clean one-way slide to target with no stop threat. Labelled honestly: the *entry's existence* owes to the Muhurat prior-close artefact described above; the *path after entry* was a genuine, chart-verifiable fade. A lucky provenance, a clean execution.
- **Give-back check:** captured the full target; the day low was ₹184.34, only ₹0.32 beyond the target — nothing material left behind.

## 2026-11-09 · HINDALCO · SHORT · PRIMARY SCORECARD (N4-V3 component scorecard only — excluded from the whole book by frozen C10 law)

- **Strategy in play:** N4-V3 primary scorecard (T125/S050 geometry), standalone construction (Muhurat session excluded from the daily series)
- **Basis for the trade (why this trade, why then):** HINDALCO Q2 FY27 results filed Fri 2026-11-06 intraday (consol PAT +59% YoY) → reaction day Mon 2026-11-09; trigger −1.774% (09:25 close ₹941.40 vs Fri regular close ₹958.40), beyond the 1.0% threshold, SHORT; entry is the 09:30 close ₹936.40 recorded at 09:35 per the scorecard's frozen convention.
- **Market context at entry:** regime UP; HINDALCO had crashed to ₹919.30 on the 09:15 bar and bounced to ₹941.40 by 09:25 — the short was fired into a violent two-way opening, not a calm fade.
- **Entry:** 09:35 @ ₹936.40 · provisional per 100 shares
- **Planned exits at entry:** stop ₹941.08 (+0.50%) · target ₹924.70 (−1.25%) · square-off 15:10
- **What actually happened:** MFE +₹175.00, MAE −₹800.00 on the scanned window; price ground upward through the morning and the 10:05 bar (high ₹944.40) hit the stop. The stock closed the day at ₹960.00 — above Friday's close; the results reaction the scorecard faded was, by the close, a non-event.
- **Exit:** 10:05 @ ₹941.08 — STOP
- **Result:** −₹508.20 net after ₹40 cost (recomputed −₹508.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** whole book: not taken — (N4-V3, HINDALCO, SHORT) is a frozen C10 exclusion in the book law, so the book avoided this loss by construction. TUNED SHADOW v1 (scorecard basis): SHORT uncapped → taken identically, −₹508.20.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop — the opening crash was the whole move; from the 09:30 entry the stock only recovered, and a +59% PAT headline gave sellers no second leg. The 0.50% scorecard stop was reached on ordinary recovery drift, not a spike.
- **Evidence:** entry-bar sequence 919.30 low (09:15) → 941.40 (09:25 close) before entry; post-entry highs rising bar by bar to the 10:05 stop; day close ₹960.00 > prior close ₹958.40.
- **Has history seen this before?** N4-V3 scorecard November so far: 3 taken trades before today (NTPC stop, NHPC stop, PFC stop) plus ASTRAL's target — stop-before-target is the scorecard's dominant November outcome (4 of 5 taken trades). In the stored scorecard history the incumbent re-sums at +₹7,990.43 (Jan–Oct 2026, T125 file) — positive across the year, so one month of stops is variance until the month closes; counted, not extrapolated.
- **The fix:** NO NEW FIX proposed from this trade — the whole book already carries the structural answer (the C10 exclusion of this exact name/direction, banked in-sample), and TUNED SHADOW v1's one-sided cap deliberately does not cap SHORTs. Status: NO FIX — accepted risk at scorecard level; the scorecard exists to measure the uncapped construction honestly.
- **Lesson ID:** RSI-STOCKS-011

## 2026-11-09 · GLENMARK · LONG · SHADOW SCORECARD (P2F)

- **Strategy in play:** P2F shadow scorecard (R+1 leg, T125/S050) — the identical 09:15 execution journalled above as the book's P2F-R2 row, scored here in the scorecard's own ledger.
- **Basis / entry / exits:** as the book entry above: 09:15 @ ₹2,590.00, stop ₹2,577.05, target ₹2,622.38, exit 09:25 TARGET, **+₹3,197.50** net after ₹40 cost (T10 shadow variant +₹2,550.00). Rules followed exactly? yes.
- **Why it worked:** reaction-day follow-through, as above. Give-back check: as above — the continuation belonged to the afternoon, and the INV-ABOVE rounds show the cost of chasing it with a 0.50% stop.

## 2026-11-09 · ASTRAL · SHORT · SHADOW SCORECARD (P2F)

- **Strategy in play:** P2F shadow scorecard (R+1 leg, T125/S050)
- **Basis for the trade (why this trade, why then):** ASTRAL Q2 FY27 results Thu 2026-11-05 after-market → reaction Fri 2026-11-06 closed −9.68% (₹1,253.60 vs ₹1,388.00), qualifying ≥2.00% SHORT; R+1 Mon 2026-11-09 entry at the 09:15 open ₹1,261.60 per the frozen spec.
- **Market context at entry:** regime UP; ASTRAL's reaction day had already been a capitulation (−9.68% after Friday's −10% intraday trigger day for the N4 scorecard) — the R+1 short was selling into a name two days removed from its news low.
- **Entry:** 09:15 @ ₹1,261.60 · provisional per 100 shares
- **Planned exits at entry:** stop ₹1,267.91 (+0.50%) · target ₹1,245.83 (−1.25%) · square-off 15:10
- **What actually happened:** the entry bar itself ranged ₹1,252.30–₹1,284.50 (a ₹32 range on a ₹6.31 stop); on the scanned post-entry window MFE was −₹700.00 (never favourable) and the 09:20 bar hit the stop. The stock rose all day to a ₹1,293.00 high — a relief bounce, not a continuation.
- **Exit:** 09:20 @ ₹1,267.91 — STOP
- **Result:** −₹670.80 net after ₹40 cost (recomputed −₹671.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** whole book: not taken (the book's P2F population uses the ≥2.5% reaction band on its own construction and this leg sits in the scorecard ledger only — the same ledger split as GODREJCP on Nov 2). No TUNED SHADOW coverage (P2F is outside v1).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race, extreme-reaction form: after a −9.68% reaction day the name's 5-minute noise (₹32 on the entry bar) was five times the frozen 0.50% stop; the R+1 continuation premise failed outright — the day was a bounce from the open.
- **Evidence:** entry bar high ₹1,284.50 vs stop ₹1,267.91; day high ₹1,293.00, no bar after entry traded below the entry price on the scanned window (MFE −₹700.00).
- **Has history seen this before?** In the stored 87-trade P2F family files, reactions of |move| ≥5% are a small tail; the family's November scorecard record is now 4 taken (ITC target, NATIONALUM stop, NHPC target, PFC stop) before today — today's pair (GLENMARK target / ASTRAL stop) keeps the family at its historical shape: targets pay for stops when the reaction is follow-through, not capitulation. Counted as the family's extreme-reaction instance #1 in November; a one-off so far, logged as accepted risk unless it recurs.
- **The fix:** NO FIX tested tonight — a |reaction| cap on P2F would be a new filter on a 1-instance November cause, and the stored family population is 2026-only, so its cross-year leg is unverifiable by the same ground that failed EVE-12. Queued as a watch item: if a second extreme-reaction (≥5%) R+1 leg stops in November, it becomes a registered candidate family. Status: PROPOSED (watch), not tested.
- **Lesson ID:** RSI-STOCKS-012

## 2026-11-09 · NHPC · LONG · LIVE-SHADOW ONLY (P2F-R2 live-shadow producer — not in the EOD book or scorecard logs)

- **Strategy in play:** P2F-R2 as produced by the live-shadow runner (09:15 entry @ ₹81.30, stop ₹80.89, target ₹82.32)
- **What actually happened:** the 09:15 bar itself fell to ₹79.38; on the frozen scan the 09:20 bar hit the stop @ ₹80.89. **Result: −₹80.65** (live-shadow log; recomputed −₹81.00). Rules followed exactly? yes, within the live-shadow ledger.
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race (Lesson RSI-STOCKS-002's R+2 shape). The EOD whole book did not log an NHPC row today, so this stays a live-shadow-ledger result only, never in book MTD. No new fix — the R+2 family was gated on 2026-11-05 (EVE-09, GATE FAIL).

## 2026-11-09 · PFC · LONG · LIVE-SHADOW ONLY (R2-LOWBAND live-shadow producer — not in the EOD book or scorecard logs)

- **Strategy in play:** R2-LOWBAND as produced by the live-shadow runner (09:15 entry @ ₹332.05, stop ₹330.39, target ₹336.20)
- **What actually happened:** slipped from the open; the 09:20 bar hit the stop @ ₹330.39. **Result: −₹206.03** (live-shadow log; recomputed −₹206.00). Rules followed exactly? yes, within the live-shadow ledger. The EOD whole book logged no PFC row (and R2-LOWBAND stands aside on UP-regime days under the frozen C23 law — today was UP), so this is a live-shadow-ledger result only.
- **Why it failed — failure cause:** no follow-through chop — a low-band second-day leg with no bid from the open. Logged under Lesson RSI-STOCKS-002's family; no new fix proposed.

# 2026-11-11 — Day 7 (regime UP; Nifty prior close above its 50DMA, so the INV1 condition did not fire and there are no INV1 rows today; Tue 2026-11-10 was the Diwali-Balipratipada market holiday). All figures provisional per 100 shares, ₹40/trade, paper only, real money ₹0. Candle verification: `stocks_eve_2026-11-11.py` Part A (fwd candles, 75 bars/symbol — day SCORED); every net below recomputed to within ₹0.30 of the logged net.

## 2026-11-11 · TATASTEEL · SHORT · PRIMARY (whole book, P2F component; same signal in the P2F shadow scorecard)

- **Strategy in play:** P2F (results-reaction follow, R+1 entry), frozen SarvaRitu whole book, T125/S050
- **Basis for the trade (why this trade, why then):** TATASTEEL's reaction day was Mon 2026-11-09 at −2.81%, inside the frozen book band (≥2.5%) → R+1 SHORT entry at the 09:15 open on the next trading day, Wed 2026-11-11 (Tue 2026-11-10 was a market holiday, so R+1 falls today). A reader can re-derive this from `stocks_sarvaritu_paper_log.csv` (2026-11-11 row) + the live-shadow producer record + the frozen spec.
- **Market context at entry:** Regime UP. The short was against the day's regime, exactly as the frozen reaction-follow law prescribes (the component follows the stock's own reaction, not the index regime).
- **Entry:** 09:15 @ ₹186.40 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹187.33 (+0.50% against) · target ₹184.07 (−1.25%) · square-off 15:10
- **What actually happened:** No favourable excursion at all in the scanned window (MFE ₹0.00); the 09:20 bar ran up through the stop (MAE −₹109.00 in the scanned window). The stock kept rising all day — high ₹189.77, 15:10 close ₹188.56 — so the stop did its job against a genuinely wrong-way day.
- **Exit:** 09:20 @ ₹187.33 — STOP (one bar after entry)
- **Result:** −₹133.20 net after ₹40 cost (recomputed −₹133.00) · full-target? no
- **Rules followed exactly?** yes — scan from the bar after entry, stop before target, per the frozen convention.
- **Same-day comparison:** the P2F shadow scorecard took the identical trade (−₹133.20, T10 column also −₹133.20; live scorecard log). Divergence recorded: the EOD P2F shadow log file (`stocks_p2f_november_shadow_log.csv`) carries no 2026-11-11 row at this run — the live scorecard log and the whole-book log both carry the trade with identical nets; the book log governs book MTD and nothing was adjusted. TUNED SHADOW v1/v2 do not act on P2F signals.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the P2F family's recurring one-bar stop-out, here on a reaction that reversed outright (the stock closed +1.2% above entry).
- **Evidence:** entry 09:15 @ 186.40; 09:20 bar high through stop 187.33; MFE ₹0.00 in the scanned window; day high 189.77 / close 188.56.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-002's shape again: in the stored Jan–Oct 2026 family universe (87 trades), 25 stops landed within ≤15 minutes of entry. This is the family's dominant loss shape and every mechanical fix for it has failed the gate (below).
- **The fix:** NO FIX — accepted risk. The fixes already gate-failed for this exact shape: skip-the-opening-bar (STOCKS-FIX-01, 2026-11-02), 10-day loser cooldown (EVE-04), quick-stop cooldown (EVE-05), drop R+2 legs (EVE-09), widen stop to 0.80% (EVE-10), target T100 (EVE-08), tighten stop to 0.35% (EVE-12, failed only on the unverifiable cross-year leg). None may be retested identically, and one more −₹133 stop does not create a new mechanical axis.
- **Lesson ID:** RSI-STOCKS-002 (recurrence)

## 2026-11-11 · KALYANKJIL · LONG · PRIMARY (whole book, N4-V3 component)

- **Strategy in play:** N4-V3 reaction-day morning-move, frozen SarvaRitu whole book (book geometry T150/S080)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Tue 2026-11-10 (board meeting 16:00–17:00 on the Diwali-Balipratipada trading holiday; consol PAT +63.9% YoY to ₹427.10 cr; revenue +31.4% YoY) → announcement on a non-trading day, so the reaction day is the next trading day, Wed 2026-11-11, per the frozen spec. By 09:30 KALYANKJIL had moved +8.658% (09:25 close 663.90 vs prev close 611.00 on Mon 2026-11-09 regular session; the Sun 2026-11-08 Muhurat session is excluded from the prev-close series), qualifying under the frozen N4-V3 rule; entry at 09:35 per the frozen convention. A reader can re-derive this from `stocks_n4_november_paper_log.csv` (2026-11-11 row) + the frozen spec.
- **Market context at entry:** Regime UP — a very strong results reaction in a rising tape; the day's open was ₹630.00 and the morning spike carried through the entry.
- **Entry:** 09:35 @ ₹666.20 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹660.87 (−0.80%) · target ₹676.19 (+1.50%) · square-off 15:10
- **What actually happened:** Almost no adverse excursion (MAE −₹45.00); price ran straight to the target in two bars (MFE in the holding window +₹1,280.00). The stock went on to a day high of ₹689.00 (+₹2,280.00 beyond entry) and then faded to a 15:10 close of ₹662.00 — below entry — so the frozen target exit captured the move's reliable part and none of the fade.
- **Exit:** 09:45 @ ₹676.19 — TARGET
- **Result:** +₹959.30 net after ₹40 cost (recomputed +₹959.00) · full-target? yes
- **Rules followed exactly?** yes
- **Same-day comparison:** the N4-V3 primary scorecard took the identical signal on its own geometry and also hit target (+₹792.75, entry below). **TUNED SHADOW v1 (one-sided cap) SKIPPED this trade** — signed move +8.658% ≥ +3.0% on a LONG — so today is the cap's first forward COST day: the shadow took ₹0 where the incumbent made +₹959.30 (book) / +₹792.75 (scorecard). TUNED SHADOW v2 (EVE-20) does not act on N4 signals.

### If the trade won
- **Why it worked:** a genuine, large results beat (+63.9% PAT) with immediate follow-through — the reaction was real demand, not a spike-and-fade; the trade was never threatened (MAE −₹45 against a −₹533 stop distance).
- **Give-back check:** captured ₹999.00 gross of the +₹1,280.00 holding-window MFE at the frozen target; the later run to ₹689 and full fade to ₹662 are recorded as context, not as give-back — the target exit is the frozen law and today it beat the square-off by ₹1,419.00.
- **Shadow-cost note (not a defect of this trade):** this winner feeds Lesson **RSI-STOCKS-015** — the one-sided cap's skipped set, +₹80.65 in the shadow's favour through Nov 9, flips to −₹712.10 (scorecard basis) after today. Tonight's STOCKS-EVE-21 tested the mechanical remedy (a ≥+6% extreme-move exemption) and it FAILED the gate: the historical ≥+6% LONG bucket is net negative on both bases, so the cap stands and today's cost is logged as the rule's known variance, not a reason to edit it mid-window.

## 2026-11-11 · KALYANKJIL · LONG · PRIMARY SCORECARD (N4-V3 component scorecard)

- **Strategy in play:** N4-V3 primary scorecard (scorecard geometry T125/S050), frozen November component scorecard
- **Basis for the trade:** identical signal to the whole-book entry above — results reaction +8.658% by 09:30, entry 09:35 @ ₹666.20 per the frozen scorecard spec (`stocks_n4_november_paper_log.csv`, 2026-11-11).
- **Market context at entry:** regime UP (as above).
- **Entry:** 09:35 @ ₹666.20 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹662.87 (−0.50%) · target ₹674.53 (+1.25%) · square-off 15:10
- **What actually happened:** MAE −₹45.00; the 09:45 bar's high 679.00 hit the target; no earlier bar touched the stop (scorecard note). MFE in the holding window +₹1,280.00. The T10 shadow column exited earlier at 09:40 @ 672.86 for +₹626.20.
- **Exit:** 09:45 @ ₹674.53 — TARGET
- **Result:** +₹792.75 net after ₹40 cost (recomputed +₹793.00) · full-target? yes · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — stop-first scan from the bar after the entry bar per the frozen scorecard convention.
- **Same-day comparison:** whole book (above) held the same signal on wider geometry and made +₹959.30; TUNED SHADOW v1 skipped both bases (Lesson RSI-STOCKS-015).

### If the trade won
- **Why it worked:** as the book entry — a real results beat with clean follow-through on both geometries.
- **Give-back check:** captured at the target price inside the bar that printed 679.00; standard T125 capture, no defect.

# 2026-11-12 — Day 8 (regime UP; Nifty prior close above its 50DMA, so the INV1 condition did not fire and there are no INV1 rows today). All figures provisional per 100 shares, ₹40/trade, paper only, real money ₹0. Candle verification: `stocks_eve_2026-11-12.py` Part A (fwd candles, 75 bars/symbol — day SCORED); every net below recomputed to within ₹0.40 of the logged net (level rounding only). Book day: 4 trades, 1 winner, day net −₹425.54. The Stock Engine live layer (separate labelled shadow, never in book totals) took 3 of these same signals today (KALYANKJIL P2F, HINDCOPPER N4-V3, TATASTEEL P2F-R2) for +₹265.06 — its first live day.

## 2026-11-12 · KALYANKJIL · LONG · PRIMARY (whole book, P2F component; same signal in the P2F shadow scorecard)

- **Strategy in play:** P2F reaction-follow, frozen Stock Book (geometry T125/S050); the P2F shadow scorecard took the identical trade
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Tue 2026-11-10 (board 16:00–17:00 on the Diwali-Balipratipada holiday; consol PAT +63.9% YoY to ₹427.10 cr; revenue +31.4% YoY) → reaction day Wed 2026-11-11 closed +8.63% (₹663.75 vs ₹611.00 on Mon 2026-11-09), qualifying ≥2.00% LONG in the scorecard and inside the frozen book band → R+1 entry at the Thu 2026-11-12 09:15 open per the frozen spec. A reader can re-derive this from `stocks_p2f_november_shadow_log.csv` (2026-11-12 row) + the frozen spec.
- **Market context at entry:** Regime UP; second consecutive strong day for the name after yesterday's +8.658% N4-V3 reaction and target.
- **Entry:** 09:15 @ ₹675.00 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹671.62 (−0.50%) · target ₹683.44 (+1.25%) · square-off 15:10
- **What actually happened:** The entry bar itself was violent (range ₹669.00–₹702.00; its low touched below the stop, but the frozen spec scans from the bar after entry, so the stop was not in play on that bar). In the scanned window the 09:20 bar's high ₹698.25 hit the target; MFE in the scanned window +₹2,325.00, and the day ran on to a ₹717.00 high and a ₹714.00 close at 15:10 — the frozen target captured the reliable part only.
- **Exit:** 09:20 @ ₹683.44 — TARGET
- **Result:** +₹803.75 net after ₹40 cost (recomputed +₹804.00) · full-target? yes
- **Rules followed exactly?** yes — entry-bar low not scanned, per the frozen spec (recorded explicitly because the entry bar's low ₹669.00 was below the stop level)
- **Same-day comparison:** the P2F shadow scorecard took the identical trade (+₹803.75; its T10 column +₹635.00). TUNED SHADOW v1/v2 do not act on P2F signals. Tonight's STOCKS-EVE-22 tested dropping extreme-reaction (≥5%) P2F legs — this trade's +8.63% reaction is exactly that bucket — and it GATE FAILED: the historical extreme bucket earns +₹12,635.05, so this winner is the bucket working as history says it does.

### If the trade won
- **Why it worked:** a genuine large results beat with two days of follow-through — the R+1 leg rode real demand, not a one-bar spike; the target filled on the second bar.
- **Give-back check:** captured ₹843.75 gross of a much larger day (high ₹717.00, 15:10 close ₹714.00 — ₹3,056.00 beyond the target exit). That overshoot is exit-tuning context, not an entry defect: the frozen T125 target is the family law and no exit variant is proposed on one day.

## 2026-11-12 · TATASTEEL · SHORT · PRIMARY (whole book, P2F-R2 component)

- **Strategy in play:** P2F-R2 (second-round reaction-follow), frozen Stock Book (geometry T125/S050)
- **Basis for the trade (why this trade, why then):** the same TATASTEEL results event (board Sat 2026-11-07; reaction Mon 2026-11-09 −2.81% on the engine's daily-series basis, disclosed in the P2F log) produced its R2 leg today: R+1-style SHORT entry at the 09:15 open per the frozen R2 construction, one day after the book's P2F leg on the same name stopped out. Re-derivable from `stocks_sarvaritu_live_shadow_log.csv` (2026-11-12 P2F-R2 row, entry ₹188.75) + the frozen spec.
- **Market context at entry:** Regime UP — a short into a rising tape, on a name that had already reversed upward yesterday (day high ₹189.77 vs the ₹186.40 P2F entry).
- **Entry:** 09:15 @ ₹188.75 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹189.69 (+0.50%) · target ₹186.39 (−1.25%) · square-off 15:10
- **What actually happened:** Almost no favourable excursion — MFE only +₹41.00 in the scanned window (best low ₹188.34); price ground upward through the morning and the 09:50 bar (high ₹189.79) hit the stop. Day high ₹190.65, 15:10 close ₹188.20 — holding would have squared off slightly better than the stop, by ₹149.00, but the short was wrong all morning.
- **Exit:** 09:50 @ ₹189.69 — STOP
- **Result:** −₹134.37 net after ₹40 cost (recomputed −₹134.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** the Stock Engine live layer took the identical leg (−₹134.37). TUNED SHADOW v1/v2 do not act on P2F-family signals.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race family shape, in its slower form — no follow-through chop: the reaction had already reversed on R-day+1 (yesterday's P2F leg stopped on the same reversal), and the R2 leg shorted the same reversed name again into strength.
- **Evidence:** entry 09:15 @ ₹188.75; scanned-window MFE +₹41.00 only; 09:50 bar high ₹189.79 through stop ₹189.69; day high ₹190.65.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-002's family shape again (the P2F family's dominant loss form: in the stored 87-trade family universe, 25 stops landed within ≤15 minutes of entry; today's stop at 35 minutes is the same no-follow-through pattern at a slower tempo). The R2-after-a-stopped-R1 configuration is the family's repeat-leg shape, and the cooldown fixes for it (EVE-04, EVE-05) already gate-failed.
- **The fix:** NO NEW FIX — accepted risk. Every mechanical fix for this shape has failed the gate (skip-the-opening-bar FIX-01; EVE-04/05 cooldowns; EVE-09 drop R+2 legs — the R+2 bucket earns +₹14,173.26 stored; EVE-10 widen stop; EVE-08 target T100; EVE-12 tighten stop, failed only on cross-year). Tonight's EVE-22 tested a different family axis (extreme-reaction stand-down) and also GATE FAILED. None may be retested identically.
- **Lesson ID:** RSI-STOCKS-002 (recurrence)

## 2026-11-12 · HINDCOPPER · LONG · PRIMARY (whole book, N4-V3 component)

- **Strategy in play:** N4-V3 reaction-day morning-move, frozen Stock Book (book geometry T150/S080)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed after-market Wed 2026-11-11 (exchange filing 21:06–21:36 IST; consol PAT ₹518.13 cr, +181.9% YoY / +47% QoQ; revenue ₹1,175 cr, +63.7% YoY) → reaction day Thu 2026-11-12. By 09:30 HINDCOPPER had moved +4.033% (09:25 close ₹453.95 vs prev close ₹436.35; the book machinery's own reading is +3.88% — both clear the frozen 1.0% trigger, and T-S2 today settled that the trigger stays 1.0%), qualifying LONG; entry at 09:35 per the frozen convention. HINDCOPPER entered the calendar only through the daily filing check (one of the nine no-date stocks at freeze time). Re-derivable from `stocks_n4_november_paper_log.csv` (2026-11-12 row) + the frozen spec.
- **Market context at entry:** Regime UP, but the name itself was already fading: it had gapped open at ₹464.00 (+6.3% vs prev close) and by the 09:25 bar had cooled to ₹453.95 — the entry bought a reaction that had peaked in the first bar.
- **Entry:** 09:35 @ ₹455.40 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹451.76 (−0.80%) · target ₹462.23 (+1.50%) · square-off 15:10
- **What actually happened:** Never favourable — MFE −₹70.00 in the scanned window (the price never traded above ₹456.45 after entry); the 09:40 bar's low ₹451.55 hit the stop on tonight's fwd-candle scan. The fade continued all day: day low ₹441.00, 15:10 close ₹447.75 — the stop beat holding by ₹764.00.
- **Exit:** 09:40 @ ₹451.76 — STOP (fwd-scan timing; the scorecard's own feed recorded its tighter stop on the 09:35 bar — see the scorecard entry below; nets match the logs exactly on both bases)
- **Result:** −₹404.32 net after ₹40 cost (recomputed −₹404.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** the scorecard basis (below) stopped for −₹267.70. **TUNED SHADOW v1 (one-sided cap) SKIPPED this trade on both bases** — signed move ≥ +3.0% on a LONG — so today the cap SAVED ₹404.32 (book) / ₹267.70 (scorecard): the mirror image of yesterday's KALYANKJIL cost day. TUNED SHADOW v2 does not act on N4 signals. The Stock Engine live layer took the trade identically (−₹404.32).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / spike-and-fade — a +181.9% PAT headline whose intraday demand peaked in the opening bar (gap +6.3%, cooled to +4.0% by 09:25) and then faded for the rest of the session; the 09:35 entry bought the fade, not the reaction.
- **Evidence:** 09:15 bar open ₹464.00 / high ₹464.90; 09:25 close ₹453.95; post-entry high only ₹456.45; day low ₹441.00; 15:10 close ₹447.75 (below entry by ₹765.00 gross).
- **Has history seen this before?** Yes — this is precisely the bucket TUNED SHADOW v1 exists for: in the stored 56-trade standalone N4-V3 population, LONG entries with a ≥+3.0% move by 09:30 net −₹5,526.08 on the scorecard basis / −₹7,811.90 on the book basis (10 trades: the +3–6% band −₹5,174.94 / −₹7,088.95 over 8 trades, plus the ≥+6% pair −₹351.14 / −₹722.95). The frozen incumbent keeps taking them; the shadow keeps skipping them.
- **The fix:** ALREADY FIXED in shadow — TUNED SHADOW v1's one-sided cap skipped this trade today and saved the full loss on both bases. No new candidate: yesterday's EVE-21 (band-cap refinement) already GATE FAILED, and the cap itself is the standing answer, judged at December adoption on the full forward record.
- **Lesson ID:** RSI-STOCKS-015 (the cap's forward record — today a save day, against yesterday's cost day)

## 2026-11-12 · HINDCOPPER · LONG · PRIMARY SCORECARD (N4-V3 component scorecard)

- **Strategy in play:** N4-V3 primary scorecard (scorecard geometry T125/S050), frozen November component scorecard
- **Basis for the trade:** identical signal to the whole-book entry above — results reaction +4.033% by 09:30, entry 09:35 @ ₹455.40 per the frozen scorecard spec (`stocks_n4_november_paper_log.csv`, 2026-11-12).
- **Market context at entry:** regime UP (as above).
- **Entry:** 09:35 @ ₹455.40 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹453.12 (−0.50%) · target ₹461.09 (+1.25%) · square-off 15:10
- **What actually happened:** the scorecard log records the stop hit on the 09:35 bar itself on its own candle feed; tonight's fwd-candle scan puts the first post-entry bar through the stop at 09:40 (low ₹451.55) — a one-bar feed-timing difference, recorded not adjusted; the net is identical either way. MFE −₹70.00, MAE −₹385.00 in the scanned window. The T10 shadow column also stopped at ₹453.12 (−₹267.70).
- **Exit:** 09:35 per the scorecard log @ ₹453.12 — STOP (fwd scan: 09:40, same price)
- **Result:** −₹267.70 net after ₹40 cost (recomputed −₹268.00) · full-target? no · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — stop-first scan from the bar after the entry bar per the frozen scorecard convention, on the scorecard's own feed
- **Same-day comparison:** whole book (above) on wider geometry lost −₹404.32; TUNED SHADOW v1 skipped both bases.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop / spike-and-fade — same cause as the book entry above.
- **Evidence:** as the book entry; the scorecard's November record is now 5 stops in 7 taken trades (NTPC, NHPC, PFC, HINDALCO, HINDCOPPER) against 2 targets (ASTRAL, KALYANKJIL).
- **Has history seen this before?** Yes — the ≥+3% LONG bucket above (−₹5,526.08 scorecard over 10 stored trades); the scorecard's stop-before-target dominance in November is the incumbent's known shape, counted not extrapolated.
- **The fix:** ALREADY FIXED in shadow — TUNED SHADOW v1 skipped it (see the book entry).
- **Lesson ID:** RSI-STOCKS-015 (recurrence, scorecard basis)

## 2026-11-12 · ASTRAL · LONG · PRIMARY (whole book, INV-ABOVE component)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen Stock Book, PLAIN T125/S050
- **Basis for the trade (why this trade, why then):** the name qualified in the frozen chain population with the g1 gate active; entry at the 09:55 bar open (₹1,301.20 — verified tonight as that bar's open in the fwd candles, and the logged exit is exactly the −0.50% stop from it). ASTRAL was mid-recovery: it had opened at ₹1,280.50 and run to a ₹1,303.00 day high on the 09:50 bar — the entry came one bar after that high. Re-derivable from `stocks_sarvaritu_paper_log.csv` (2026-11-12 row) + the frozen chain.
- **Market context at entry:** Regime UP; the name was +1.6% above its open at entry, at the top of its morning range.
- **Entry:** 09:55 @ ₹1,301.20 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹1,294.69 (−0.50%) · target ₹1,317.46 (+1.25%) · square-off 15:10
- **What actually happened:** Never favourable — MFE −₹110.00 in the scanned window; the stock faded steadily and the 10:10 bar hit the stop (adverse excursion by the exit bar −₹1,090.00 per 100 shares). The fade ran all day: 15:10 close ₹1,274.50 — the stop beat holding by ₹2,670.00 gross.
- **Exit:** 10:10 @ ₹1,294.69 — STOP
- **Result:** −₹690.60 net after ₹40 cost (recomputed −₹691.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** **TUNED SHADOW v2 (EVE-20) TOOK this trade identically** — ASTRAL's prior trading day (Wed 2026-11-11) moved only +0.25% close-to-close, far below v2's ≥+4.0% drop condition, so v2 had nothing to drop; today is v2's first live taken trade and it is this loss (−₹690.60, shadow money). TUNED SHADOW v1 does not act on INV-ABOVE.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race in its slow form, on a no-follow-through fade — the chain bought the top of the morning range (entry ₹1,301.20 vs the ₹1,303.00 high printed one bar earlier) and the 0.50% stop (₹6.51) sat inside the name's normal 5-minute noise as the recovery failed.
- **Evidence:** 09:50 bar high ₹1,303.00 (the day high); entry 09:55 @ ₹1,301.20; scanned-window MFE −₹110.00 (never favourable); 10:10 bar through stop ₹1,294.69; day close ₹1,274.50.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-010's modal INV-ABOVE loss: in the stored c24 populations (206 trades, both years) the S050 rescan counts 128 stop exits (62%). The post-spike-day configuration that v2 filters did not occur (prior day +0.25%), so this is the component's ordinary tight-stop cost, not the EVE-20 configuration.
- **The fix:** NO GATE-PASSING FIX — the fixes for this cause have all been gated: EVE-15 (widen stop S080) failed on reproduction/construction, EVE-18 (opening-range-width stop, chain-faithful) failed on the 2026-07 month flip + book ex-top-3 legs, EVE-06/07/13/14/16/17 all failed their gates. Status: accepted, measured cost of the frozen component; the frozen book is unchanged.
- **Lesson ID:** RSI-STOCKS-010 (recurrence)

# 2026-11-13 — Day 9 (regime UP; Nifty prior close above its 50DMA, so the INV1 condition did not fire and there are no INV1 rows today). All figures provisional per 100 shares, ₹40/trade, paper only, real money ₹0. Candle verification: `stocks_eve_2026-11-13.py` Part A only (fwd candles, 75 bars/symbol — day SCORED); every net below recomputed to within ₹0.20 of the logged net. Book day: 2 trades, 1 winner, day net −₹447.80. SCORE-ONLY run per the owner's settlement today ("Keep whatever is running… Let it run") — no tuning candidates were gated tonight. The Stock Engine live layer (separate labelled shadow, never in book totals) lost −₹3,182.52 on 5 wide-universe N4-V3 picks (4 stops, 1 target) — its final day; it takes no new picks.

## 2026-11-13 · IRCTC · SHORT · PRIMARY (whole book, N4-V3 component)

- **Strategy in play:** N4-V3 reaction-day morning-move, frozen Stock Book (book geometry T150/S080)
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed after-market Thu 2026-11-12 (board 15:00–16:45 IST; filed 17:45 IST; consol PAT ₹263.56 cr, −22.9% YoY; revenue ₹1,333.07 cr, +16.3%; exceptional Rail Neer GST provision ₹116.30 cr) → reaction day Fri 2026-11-13. By 09:30 IRCTC had moved −2.304% (09:25 close ₹460.10 vs prev close ₹470.95), clearing the frozen 1.0% trigger, qualifying SHORT; entry at 09:35 per the frozen convention. The watchlist had carried 2026-11-17/18 for this name; the actual announcement was Thu 2026-11-12, so the reaction day is today per spec. Re-derivable from `stocks_n4_november_paper_log.csv` (2026-11-13 IRCTC row) + the frozen spec.
- **Market context at entry:** Regime UP; the name itself was falling on a weak print (PAT down, exceptional provision) — a stock-specific fade inside a rising tape.
- **Entry:** 09:35 @ ₹460.40 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹464.08 (+0.80%) · target ₹453.49 (−1.50%) · square-off 15:10
- **What actually happened:** The short worked but never reached target: best favourable excursion +₹420.00 (day low ₹456.20); worst adverse excursion −₹235.00 (post-entry high ₹462.75 — through the scorecard's tighter stop by ₹0.05, but ₹1.33/share inside the book's wider stop). Price drifted sideways-down and the trade squared off at 15:10.
- **Exit:** 15:10 @ ₹457.70 — SQUARE-OFF
- **Result:** +₹230.00 net after ₹40 cost (recomputed +₹230.00, exact) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** the scorecard basis (below) stopped on the identical signal for −₹270.20 — a pure geometry divergence. **TUNED SHADOW v1 took this trade identically on both bases** (SHORTs are uncapped): +₹230.00 book basis / −₹270.20 scorecard basis. The Stock Engine did not pick IRCTC.

### If the trade won
- **Why it worked:** the direction was right (a genuine weak print faded all day, close ₹457.70 below entry) and the book's S080 stop was wide enough to survive the 10:10 adverse probe that killed the tighter scorecard stop — the mirror image of PFC on 2026-11-05, where the scorecard stopped and the book went on to target.
- **Give-back check:** captured ₹270.00 gross of the +₹420.00 excursion (64%); the ₹453.49 target was never reached (day low ₹456.20). No defect — square-off capture on a slow fade is the frozen geometry's normal outcome.

## 2026-11-13 · IRCTC · SHORT · PRIMARY SCORECARD (N4-V3 component scorecard)

- **Strategy in play:** N4-V3 primary scorecard (scorecard geometry T125/S050), frozen November component scorecard
- **Basis for the trade:** identical signal to the whole-book entry above — results reaction −2.304% by 09:30, entry 09:35 @ ₹460.40 per the frozen scorecard spec (`stocks_n4_november_paper_log.csv`, 2026-11-13).
- **Market context at entry:** regime UP (as above).
- **Entry:** 09:35 @ ₹460.40 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹462.70 (+0.50%) · target ₹454.64 (−1.25%) · square-off 15:10
- **What actually happened:** MFE +₹115.00 before the stop in the scanned window (full-day MFE +₹420.00 came after the exit); the 10:10 bar's high ₹462.75 clipped the ₹462.70 stop by ₹0.05/share. The fade then continued to the ₹456.20 day low without the scorecard.
- **Exit:** 10:10 @ ₹462.70 — STOP
- **Result:** −₹270.20 net after ₹40 cost (recomputed −₹270.00) · full-target? no · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — stop-first scan from the bar after the entry bar per the frozen scorecard convention
- **Same-day comparison:** whole book (above) on wider geometry held the same signal to a +₹230.00 square-off; TUNED SHADOW v1 took the scorecard basis identically (−₹270.20).

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** stop-before-target race caused by geometry, not by the signal — the S050 stop sat ₹0.05 inside the morning's adverse probe; the underlying short was correct all day.
- **Evidence:** entry 09:35 @ ₹460.40; 10:10 bar high ₹462.75 vs stop ₹462.70; day low ₹456.20 and 15:10 close ₹457.70, both below entry — holding on book geometry paid +₹230.00.
- **Has history seen this before?** Yes — the second November geometry-divergence instance: PFC on 2026-11-05 (scorecard S050 stopped −₹202.93 while the book's S080/T150 held to a +₹448.77 target) is the same shape in the opposite P&L order. The scorecard's November record is now 7 stops in 9 taken trades against 2 targets — its stop dominance is the frozen geometry's known cost, counted not extrapolated.
- **The fix:** NO FIX — score-only per the owner's settlement 2026-11-13; both geometries are frozen and each is judged on its own full record at December adoption. No candidate was gated tonight.
- **Lesson ID:** RSI-STOCKS-017 (new — geometry divergence: identical signal, opposite outcomes decided by stop width alone; first instance PFC 2026-11-05, second today)

## 2026-11-13 · BDL · SHORT · PRIMARY SCORECARD (N4-V3 component scorecard; no whole-book row — see comparison)

- **Strategy in play:** N4-V3 primary scorecard (scorecard geometry T125/S050), frozen November component scorecard
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed Thu 2026-11-12 intraday (board 11:30–13:30 IST; standalone PAT ₹183.48 cr, −15.3% YoY; revenue ₹1,664.14 cr, +45.1%) → intraday announcement, so reaction day is Fri 2026-11-13 per spec. By 09:30 BDL had moved −1.346% (09:25 close ₹1,040.90 vs prev close ₹1,055.10), clearing the frozen 1.0% trigger, qualifying SHORT; entry 09:35. The watchlist had carried Sat 2026-11-14; the actual announcement was Thu 2026-11-12. Re-derivable from `stocks_n4_november_paper_log.csv` (2026-11-13 BDL row) + the frozen spec.
- **Market context at entry:** Regime UP; a defence name falling on a PAT decline despite strong revenue growth — a mixed print.
- **Entry:** 09:35 @ ₹1,044.80 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹1,050.02 (+0.50%) · target ₹1,031.74 (−1.25%) · square-off 15:10
- **What actually happened:** A real two-sided fight: MFE +₹470.00 early (price reached ₹1,040.10 in the scanned window), then a sharp reversal — MAE −₹1,020.00 — and the 09:50 bar hit the stop. The day then faded anyway (15:10 close ₹1,030.00, below the target price) — after the stop, not before it.
- **Exit:** 09:50 @ ₹1,050.02 — STOP
- **Result:** −₹562.40 net after ₹40 cost (recomputed −₹562.00) · full-target? no · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes
- **Same-day comparison:** no whole-book row for BDL today — the book log carries only IRCTC (N4-V3) and ASTRAL (INV-ABOVE); the scorecard log governs the scorecard line and the divergence is recorded, not adjusted (the same treatment as ASTRAL on 2026-11-06). **TUNED SHADOW v1 took this trade identically** (SHORT, uncapped): −₹562.40, shadow money.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** stop-before-target race / no follow-through after an initial move — the short developed +₹470.00 (36% of the target distance) and then reversed through the stop within 15 minutes; the eventual fade to ₹1,030.00 came hours later and does not rescue the entry timing.
- **Evidence:** entry 09:35 @ ₹1,044.80; scanned-window MFE +₹470.00, MAE −₹1,020.00; 09:50 bar through stop ₹1,050.02; day high ₹1,059.35, 15:10 close ₹1,030.00.
- **Has history seen this before?** Yes — the scorecard's modal November shape: 7 of its 9 taken trades have now stopped (NTPC, NHPC, PFC, HINDALCO, HINDCOPPER, BDL, IRCTC) against 2 targets (ASTRAL, KALYANKJIL), while its Jan–Oct 2026 incumbent re-sums positive (+₹7,990.43) — November stop dominance is counted, not extrapolated (Lesson RSI-STOCKS-011's standing note).
- **The fix:** NO FIX — score-only per the owner's settlement 2026-11-13. No candidate was gated tonight; the frozen scorecard is unchanged.
- **Lesson ID:** RSI-STOCKS-011 (recurrence — scorecard stop-before-target on a headline fade)

## 2026-11-13 · HINDCOPPER · LONG · P2F SHADOW SCORECARD (P2F component; correctly NOT in the whole book)

- **Strategy in play:** P2F reaction-follow shadow scorecard (geometry T125/S050), frozen November component scorecard
- **Basis for the trade (why this trade, why then):** Q2 FY27 results filed after-market Wed 2026-11-11 (consol PAT ₹518.13 cr, +181.9% YoY) → reaction day Thu 2026-11-12 closed +2.25% (₹446.15 vs ₹436.35), qualifying ≥2.00% LONG for the scorecard → R+1 entry at the Fri 2026-11-13 09:15 open per the frozen spec. Re-derivable from `stocks_p2f_november_shadow_log.csv` (2026-11-13 row) + the frozen spec.
- **Market context at entry:** Regime UP; the name was on day two of fading its own results spike — yesterday's N4-V3 book and scorecard trades on the same name both stopped.
- **Entry:** 09:15 @ ₹443.90 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹441.68 (−0.50%) · target ₹449.45 (+1.25%) · square-off 15:10
- **What actually happened:** Never favourable in the scanned window — MFE −₹210.00; the 09:20 bar's low ₹439.10 hit the stop one bar after entry. The fade continued: day low ₹437.00, 15:10 close ₹439.70 — the stop beat holding by ₹420.00 gross.
- **Exit:** 09:20 @ ₹441.68 — STOP
- **Result:** −₹262.00 net after ₹40 cost (recomputed −₹262.00, exact) · full-target? no · SCORECARD money — never added to book totals
- **Rules followed exactly?** yes — scan from the bar after entry per the frozen spec
- **Same-day comparison:** the whole book took nothing on HINDCOPPER today — its +2.25% reaction sits below the frozen book band (≥2.5%), so the book correctly excluded a leg the scorecard (≥2.00%) took and lost on. TUNED SHADOW v1/v2 do not act on P2F signals.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** entry-bar whipsaw / stop-before-target race — the family's dominant shape: a one-bar stop with zero favourable excursion, on a reaction that had already failed yesterday.
- **Evidence:** entry 09:15 @ ₹443.90; scanned-window MFE −₹210.00; 09:20 bar low ₹439.10 through stop ₹441.68; day close ₹439.70 below entry.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-002 again: 25 of the stored family's 87 trades stop within ≤15 minutes. This is the third consecutive trading day the shape has appeared (TATASTEEL P2F 2026-11-11, TATASTEEL P2F-R2 2026-11-12, HINDCOPPER P2F today).
- **The fix:** NO NEW FIX — score-only per the owner's settlement 2026-11-13, and every mechanical fix for this shape has already failed the gate (FIX-01 skip-the-opening-bar; EVE-04/05 cooldowns; EVE-08 T100; EVE-09 drop R+2; EVE-10 widen stop; EVE-12 tighten stop failed only on cross-year; EVE-22 extreme-reaction stand-down). None may be retested identically.
- **Lesson ID:** RSI-STOCKS-002 (recurrence)

## 2026-11-13 · ASTRAL · LONG · PRIMARY (whole book, INV-ABOVE component)

- **Strategy in play:** INV-ABOVE (Cycle-22 construction), frozen Stock Book, PLAIN T125/S050
- **Basis for the trade (why this trade, why then):** the name qualified in the frozen chain population with the g1 gate active; entry at the 09:40 bar open (₹1,275.60 — verified tonight as that bar's open in the fwd candles, and the logged exit is exactly the −0.50% stop from it). ASTRAL opened at ₹1,275.00 and was range-bound in the morning (day high ₹1,280.00) — unlike yesterday, the entry was not at a spike high; the recovery simply never came. Re-derivable from `stocks_sarvaritu_paper_log.csv` (2026-11-13 row) + the frozen chain.
- **Market context at entry:** Regime UP; second consecutive day the chain bought ASTRAL (yesterday's identical component trade stopped at −₹690.60).
- **Entry:** 09:40 @ ₹1,275.60 · per 100 shares (provisional basis)
- **Planned exits at entry:** stop ₹1,269.22 (−0.50%) · target ₹1,291.54 (+1.25%) · square-off 15:10
- **What actually happened:** Some favourable excursion first — MFE +₹440.00 (price reached ₹1,280.00, the day high) — then a steady fade; MAE −₹700.00 and the 12:00 bar hit the stop on tonight's scan. The fade ran to a ₹1,254.00 day low and a ₹1,262.10 close at 15:10 — the stop beat holding by ₹1,350.00 gross.
- **Exit:** 12:00 @ ₹1,269.22 — STOP (fwd-scan timing)
- **Result:** −₹677.80 net after ₹40 cost (recomputed −₹678.00) · full-target? no
- **Rules followed exactly?** yes
- **Same-day comparison:** **TUNED SHADOW v2 (EVE-20) TOOK this trade identically** — ASTRAL's prior trading day (Thu 2026-11-12) moved −0.08% close-to-close (₹1,275.00 vs ₹1,276.00, verified tonight from the fwd daily closes), far from v2's ≥+4.0% drop condition, so v2 had nothing to drop; v2's second live taken trade is this loss (−₹677.80, shadow money). TUNED SHADOW v1 does not act on INV-ABOVE.

### If the trade lost (or gave back most of its MFE)
- **Why it failed — failure cause:** no follow-through chop with the tight-stop cost — the entry developed only +₹440.00 (28% of the target distance) before fading, and the 0.50% stop (₹6.38) again sat inside the name's normal 5-minute noise.
- **Evidence:** entry 09:40 @ ₹1,275.60; MFE +₹440.00 at the ₹1,280.00 day high; 12:00 bar through stop ₹1,269.22; day low ₹1,254.00, close ₹1,262.10.
- **Has history seen this before?** Yes — Lesson RSI-STOCKS-010's modal INV-ABOVE loss (128 of 206 stored trades exit by stop on the S050 rescan, 62%), and the second consecutive day on this same name (2026-11-12 ASTRAL −₹690.60). The repeat itself is not the flaw at population level — EVE-13 proved same-day/prior-day repeats earn in aggregate; this is the component's ordinary variance arriving twice on one name.
- **The fix:** NO GATE-PASSING FIX and NO NEW FIX — score-only per the owner's settlement 2026-11-13. The gated fixes for this cause all stand failed (EVE-06/07/13/14/15/16/17/18). The frozen book is unchanged.
- **Lesson ID:** RSI-STOCKS-010 (recurrence)

## 2026-11-13 · Stock Engine live layer · 5 trades · SHADOW (wide universe, never in book totals)

- **Strategy in play:** Stock Engine LIVE (4-live construction: N4-V3 decision point 09:35 over the 1,081-name wide universe, Variant D selection economics) — all 5 of today's picks were N4-V3. Source for every figure below: `stock_engine_live_log.csv` (2026-11-13 rows). MFE/MAE: n/a — the wide-universe names are not in the 25-stock fwd candle store, so no excursion is invented; entry/exit times and prices are the live log's own record.
- **MSTCLTD LONG** 09:35 @ ₹783.35 → 09:35 @ ₹777.08 STOP (on the entry bar) — **−₹666.68**. Failure cause: entry-bar stop, zero holding time. Lesson RSI-STOCKS-002's shape transplanted to the wide universe.
- **PICCADIL SHORT** 09:35 @ ₹534.60 → 09:35 @ ₹538.88 STOP (on the entry bar) — **−₹467.68**. Failure cause: entry-bar stop, zero holding time.
- **SHARDAMOTR LONG** 09:35 @ ₹1,005.80 → 09:35 @ ₹997.75 STOP (on the entry bar) — **−₹844.64**. Failure cause: entry-bar stop, zero holding time.
- **FIEMIND LONG** 09:35 @ ₹2,093.00 → 09:45 @ ₹2,076.26 STOP — **−₹1,714.40** (the day's largest per-100 loss, a high-price name at the frozen 0.80% book-geometry stop distance). Failure cause: early stop, no follow-through.
- **POCL SHORT** 09:35 @ ₹367.25 → 10:10 @ ₹361.74 TARGET — **+₹510.88**. Why it worked: the only pick whose reaction followed through to its frozen target; a clean win on the log's record, not labelled lucky (no excursion data to audit beyond the target fill itself).
- **Day total: −₹3,182.52 on 5 trades (4 stops, 1 target)** — shadow money, provisional per 100 shares, never added to the Stock Book's floor figures. Rules followed exactly? yes, per the live log (all exits at frozen levels). **Status: this was the Stock Engine's final live day — per the owner's settlement today it finished 2026-11-13 and takes no new picks; its November live record closes at −₹2,917.46 over 8 trades (2026-11-12 +₹265.06, today −₹3,182.52).** The frozen Stock Book itself is untouched and keeps running as-is.
