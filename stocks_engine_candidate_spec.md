# DECEMBER CANDIDATE — THE SATURATED ENGINE BOOK, FROZEN VERBATIM (2026-10-31)

The saturation run (SAT-1..SAT-36) terminated **SATURATED** at its plateau: three consecutive no-beat cycles (SAT-34, SAT-35, SAT-36) under the frozen standards. This spec freezes the incumbent book exactly as it stood at the plateau. **No parameter changes are permitted under this spec; any change voids the December judging.**

## Basis (all components)
- Equity cash intraday, LONG/SHORT, Chandu's home 25 stocks only. No options, no futures.
- Provisional per 100 shares; ₹40/trade cost deducted; paper only, real ₹0.
- Square-off 15:10 on every component.
- **RF-1 (book-wide):** no entries on special/weekend sessions (calendar-derived), all components.
- Fresh-data construction uses the same audited machinery and data pipeline as the in-sample build (5-min spot, event calendar with effective reaction dates); timing audit asserted in the judging pass (no entry before its qualifying information existed).

## The six components (663 trades in-sample)

### 1. F4 — state-gated morning follow (389 trades in-sample)
- Day state: Nifty previous close **below** its 50DMA.
- Signal: V5/skill_or morning move in the band **[0.5%, 1.0%)** measured by 10:00, traded in the follow direction. `setup3_bounce_rejection` signals excluded (OC-2).
- **First qualifying signal per stock-day only** (round-2 legs dropped; SE-1-F4R1, banked SAT-6).
- Exits: **T150 / S095** (target +1.50%, stop −0.95%).
- In-sample anchor dump: `stocks_engine_sat10_f4s095_trades.csv` (before the exclusion filters below).
- Mechanism × stock × direction exclusions (F4 takes no such signals):
  GODREJCP SHORT · HINDUNILVR SHORT · UNITDSPR SHORT · HINDCOPPER SHORT · OIL SHORT · IRCTC SHORT · NHPC SHORT · PFC SHORT · RECLTD SHORT · INDUSTOWER LONG · HINDALCO LONG · TATASTEEL LONG.
  (F4 keeps the opposite direction on every one of these names; all other components trade them unchanged.)

### 2. INV-LONG — below-trend pool, LONG only (155 trades in-sample)
- Joint state: Nifty previous close ≤ 50DMA + P2 pool membership (audited M1 machinery), LONG only.
- Exits: **T125 / S050** (target +1.25%, stop −0.50%) — the measured grid peak (SAT-5); do not re-grid.
- Whole-name exclusions inside INV-LONG only: **BDL · VEDL · HINDZINC · INDUSTOWER · KALYANKJIL** (the names trade freely in every other component).

### 3. N4-V3 — reaction-day follow (47 trades in-sample)
- Results/news reaction day; qualifying move **|move| ≥ 1.0% by 09:30** (the ≥1.0% floor is load-bearing — Lesson 17); entry **09:35** in the reaction direction.
- Exits: **T150 / S080** (the CH-2 rebuild, banked SAT-15).
- In-sample anchor dump: `stocks_engine_sat15_n4_t150s080_trades.csv`.
- Exclusions: **ASTRAL** whole-name; **TVSMOTOR LONG**; **OIL LONG** (opposite directions and other components unchanged).

### 4. P2F — reaction follow at R+1 (32 trades in-sample)
- Reaction-day close-to-close move **|move| ≥ 2.5%**; enter at the **R+1 open** (first 5-min bar open of the next session) in the reaction direction.
- Exits: **T125 / S050** (P2F's small target IS the edge — Lesson 4; do not widen).
- Exclusions: **ASTRAL** and **HINDUNILVR** whole-name; **HINDALCO LONG**.

### 5. P2F-R2 — reaction follow at R+2 (33 trades in-sample)
- Same reaction set and ≥2.5% band as P2F; enter at the **R+2 open** in the reaction direction.
- Exits: **T125 / S050**.
- In-sample anchor dump: `stocks_engine_sat13_p2fr2_trades.csv`.
- Exclusions: **ASTRAL** and **HINDUNILVR** whole-name (baked into the anchor construction); **TVSMOTOR LONG**.
- Disclosed: H1-carried in-sample (H1 +₹13,472.08 / H2 −₹559.60) — December is its arbiter (Lesson 19).

### 6. R2-LOWBAND — reaction band [2.0%, 2.5%) at R+2 (7 trades in-sample)
- Reaction-day move in **[2.0%, 2.5%)**; enter at the **R+2 open** in the reaction direction.
- Exits: **T125 / S050**.
- In-sample anchor dump: `stocks_engine_sat33_r2lowband_trades.csv`.
- Exclusions: **ASTRAL** and **HINDUNILVR** whole-name; **HINDALCO LONG**.
- Disclosed: 7 trades, H1-negative (H1 −₹144.70 / H2 +₹1,405.48), October-carried (October slice +₹1,428.06 > the component's whole net) — frozen verbatim exactly as banked (Lesson 22).

## In-sample record at the plateau (Jan–Oct 2026, the window that built it — NOT a verdict)
- **663 trades, +₹197,607.74** (₹19,760.77/month average).
- Months: Jan +28,536.25 · Feb +18,419.86 · Mar +20,584.41 · Apr +9,895.49 · May +34,880.86 · Jun +3,823.22 · Jul +6,965.93 · Aug +666.78 · Sep +19,562.51 · Oct +54,272.43. All ten green; October ≥ ₹50,000.
- Ex-top-3: **+₹72,518.25**. Top-3: TVSMOTOR +₹74,005.46 (**37.45% of the total**) · ASTRAL +₹27,847.79 · OBEROIRLTY +₹23,236.24. GLENMARK +₹20,615.44 (10.43%).
- August (+₹666.78) is 0.34% of the total — the plateau's thinnest month by far.

## December judging rules (pre-registered; frozen with this spec)
Run the book **verbatim** on December 2026 fresh data (all six components, RF-1, every exclusion above; same ₹40/trade, per 100 shares):
- **CONFIRMED** iff the December total is **positive** AND **no December week is worse than −₹15,000** (weeks = ISO calendar weeks, Mon–Sun, over December trade dates).
- **KILLED** iff the December total is **negative** — the book is then recorded as an in-sample fit and is not re-tuned.
- **INCONCLUSIVE / EXTENDS** iff December produces fewer than 20 book trades in total: judging extends to January 2027 under identical rules.
- No parameter changes, no exclusion changes, no re-freezing during the judging window. A December pass confirms the book as a candidate system; it does not by itself authorise live trading (standing rule: paper-only, one-lot discipline, fresh-data positivity first).

## Disclosed caveats carried into judging (from STRESS-1 and the run's own record)
- **Cost sensitivity (STRESS-1, measured at the earlier +₹138,631.32 book; the plateau book was not re-stressed):** the all-green property existed only at the assumed ₹40/trade — at ₹60 the total was +₹120,511.32 with 7/10 months green; at ₹80, +₹102,391.32 with 7/10. The ₹40 cost assumption is unproven against Chandu's actual broker charges.
- **Concentration:** TVSMOTOR alone is 37.45% of the plateau total (STRESS-1 at the earlier book: ex-TVSMOTOR +₹76,913.60, 9/10 green; ex-top-3 +₹18,918.30, 6/10). At the plateau, ex-top-3 is +₹72,518.25 — December's fresh data, not the in-sample ex-top-3 leg, is the arbiter of whether the concentration is earned.
- **Thin evidence inside the book:** P2F-R2 is H1-carried; R2-LOWBAND rests on 7 trades; several registry banks rest on 1–2 trades (SAT-14, SAT-17, SAT-21, SAT-24); June/August greens at earlier book states were one-trade deep (STRESS-1) and August remains thin at the plateau.
- **The declined slice:** F4 × GLENMARK × SHORT was refused at SAT-36 on the quality bar (full-period −₹136.98 vs the −₹500 standard) although its removal passed the arithmetic gate — the book above is the plateau WITHOUT that deletion, by principle (Lesson 25).

*Frozen 2026-10-31 at saturation. Evidence: stocks_engine_state.json (plateau state), stocks_engine_log.md (final saturation summary), stocks_engine_frozen.md + stocks_engine_lessons.md (every step's freeze and lesson), SAT-36 result stocks_engine_sat36_result.json.*
