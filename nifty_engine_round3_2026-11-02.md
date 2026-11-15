# NIFTY ENGINE — ROUND 3 (2026-11-02)

**Standing order:** the engines do not stop until the segment floor is met — Nifty ≥ **₹1,50,000 Jan–Oct 2026** (₹15,000/month). Basis: index-option premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0. Starting book: the **ADOPTED** December candidate (CH3-R × lock50/TGT2-175, adopted by Chandu 2026-11-02 with the August and frequency clauses recorded as FAILED-and-waived) = **+₹114,921.75**, 44 trades, FT 45.5%, 1.08/wk; gap ₹35,078.25. Every candidate was scored in the same run as its full controls (timing/leak audit, +30-min placebo, split halves, month table, ex-top-3, independent re-sum) and gated against the adopted book under the round-3 gate pre-registered in `nifty_engine_frozen.md` before any scoring. The frozen November primary (NF-PAPER-C3G7) was never touched.

**Result: floor NOT reached. One banking. Ending December candidate +₹116,348.50 → ₹11,634.85/month; remaining gap ₹33,651.50.** 34 gated cycles (40–45, 47–73) + 1 data workstream (WS3); all five workstreams worked through.

---

## WS1 — The August wound (Cycle 40) — BANKED

**Diagnosis** (`nifty_engine_r3_diag_august*.py`, all 44 adopted legs feature-scanned): the adopted book's August is exactly 3 legs — 11 Aug PE 24500 (entry premium 200.50, premium MFE **+12.5**, square-off −₹1,152.75), 19 Aug PE 24100 (115.80, MFE **+17.2**, square-off −₹564.50), 31 Aug PE 24000 (199.75, MFE **+5.2**, full stop −₹3,470.00). On all three the premium never progressed and spot's maximum favourable excursion after entry was ≤ 0.224% — no-trend days; decay and one adverse drift did the damage. Entry-known features checked book-wide — premium band, DTE (14/6/29), entry time, confirmation strength, weekday, pre-entry spot move, morning spot range, prior-day range, 3-day realised vol — none separate the three from the book's winners except one tight shared state: **the prior trading day's spot return was shallowly negative** (−0.456%, −0.317%, −0.394%), in a book whose PE engine is built on real down days (prior-day ≤ −0.5% legs net +₹95,125.75 on 21 legs). Frozen signature (recorded before scoring, not re-tuned after): **PE leg + prior-day spot return ∈ (−0.50%, −0.25%)** — 6 adopted legs (29 Jun, 11/19/31 Aug, 07 Sep, 21 Oct), monthly-geometry sum −₹1,661.25. Honesty note recorded in the freeze: the signature is a discovery on scanned data; its face value is an upper bound and December fresh data is its real judge. Stand-aside on the signature was diagnosis arithmetic only (+₹1,661.25 but frequency 0.94/wk and it spends the +₹3,030.00 October winner) — not promoted to a candidate.

**Cycle 40 — signature legs carried on the weekly expiry in force** (the lesson-31 theta-truncation mechanism, scoped to the signature instead of the whole book): **+₹116,348.50** — **BANKED**, full gate passed (FT 45.5% held, halves +65,655.50/+50,693.00, placebo +64,842.50 beaten, ex-top-3 +82,883.50, audit 44/0, NC 0, re-sum exact, frequency 1.08/wk, no adopted-green month flipped, no red month-end). Delta **+₹1,426.75** over the adopted book; August −5,187.25 → **−3,058.50** (the 31 Aug full stop becomes a −₹1,214.50 square-off on the 1-day weekly; 07 Sep gives back ₹702.00). **This book supersedes the adopted book as the December candidate.**

## WS2 — Frequency recovery (Cycles 41–45) — all rejected

The adopted 44 legs are a strict subset of the banked incumbent's 59; the 15 dropped ("difference") legs are all confirmed legs that entered after 09:55.

| Cycle | Candidate | Total | FT | Verdict |
|---|---|---|---|---|
| 41 | Union (adopted ∪ incumbent = EXP0 59, adopted geometry) | +₹98,209.00 | 39.0% | FAIL — net, FT |
| 42 | Difference legs standalone (15) | **−₹16,712.75** | 20.0% | FAIL — the dropped population is a losing book on its own (halves both negative) |
| 43 | Admission: entry premium ≤ 200 (8 legs) | +₹110,753.50 | 42.3% | FAIL — net only; every other gate leg passes |
| 44 | Admission: entry time ≤ 10:30 (12 legs) | +₹105,414.50 | 41.1% | FAIL — net, FT |
| 45 | Admission: DTE ≥ 7 (11 legs) | +₹94,672.25 | 38.2% | FAIL — net, FT; August worsens to −₹8,326.00 |

Frequency cannot be bought back from the difference legs under any single mechanical condition — every admission is net-negative because the difference set itself is.

## WS3 — The remaining blocked population (Cycle 46, data workstream)

Live retry of the expired-instruments route (browser User-Agent, 3 attempts): the registry still returns **0 contracts for expiry 2026-11-03**. The one remaining leg — **2026-10-28, 22500 PE, weekly expiry 2026-11-03, entry 10:20, solo Skill V3** — stays **NOT_COMPUTED, named, never estimated**. P3's Round-2 record (+₹59,663.75 on 101 scored legs + this 1 NC) stands unrevised. No other U1-family leg is uncomputed.

## WS4 — Adopted-book geometry micro-grid (Cycles 47–73) — no cell banked

Lock {+40, +50, +60} × TGT2 {+160, +175, +190} × BE arm {+40, +50, +60} on the 44 adopted legs, full gate per cell vs the adopted book:

| Lock \ TGT2 | 160 (arm 40/50/60) | 175 (arm 40/50/60) | 190 (arm 40/50/60) |
|---|---|---|---|
| 40 | 99,279.50 / 112,435.50 / 111,944.75 | 98,990.25 / 113,121.25 / 112,630.50 | 98,441.00 / 109,721.75 / 109,231.00 |
| 50 | 101,080.00 / 114,236.00 / 113,745.25 | 100,790.75 / **114,921.75** / 114,431.00 | 100,241.50 / 111,522.25 / 111,031.50 |
| 60 | 100,712.75 / 113,868.75 / 113,378.00 | 100,423.50 / 114,554.50 / 114,063.75 | 99,874.25 / 111,155.00 / 110,664.25 |

The bold centre cell (Cycle 60) is the adopted book itself, reproduced exactly (validation). Best off-centre cell: Cycle 69 (lock 60 / TGT2 175 / arm 50) +₹114,554.50. Arm +40 costs ~₹13–14k uniformly (FT drops to 43.2%); arm 50 ≥ arm 60 in every row. **The adopted point is the peak of its own micro-grid** — the geometry plateau holds jointly in all three axes on the adopted leg set.

## WS5 — Combinations

Per the pre-registered freeze, combinations exist only for WS4 cells that banked. None did → no WS5 candidates. The Cycle-40 book stands.

---

## Ending scorecard — December candidate (Cycle-40 book)

CH3-R leg rule + EXP0; geometry stop −50 / BE arm +50 / tgt1 +90 → lock +50 / TGT2 +175 / square-off 15:10; **plus** PE legs whose prior-day spot return ∈ (−0.50%, −0.25%) carried on the weekly expiry in force.

- **Total +₹116,348.50 Jan–Oct 2026** — 44 trades, FT 45.5%, 1.08/week, **₹11,634.85/month vs the ₹15,000 floor → gap ₹33,651.50**
- Months: Jan +23,974.75 · Feb +14,882.25 · Mar +21,650.00 · Apr +7,471.50 · May −2,323.00 · Jun +7,584.00 · Jul +17,054.50 · Aug −3,058.50 · Sep +4,318.00 · Oct +24,795.00 — no red month-ends
- Halves +65,655.50 / +50,693.00 · Placebo (+30 min) +64,842.50, beaten · Ex-top-3 +82,883.50 · Timing audit 44/44 clean · NOT_COMPUTED 0 · Independent re-sum exact

**What Round 3 established:** the remaining floor gap is not hiding in the adopted book's geometry (27 cells, peak confirmed), its dropped legs (negative population, all admissions fail), its August legs (one scoped carriage banked, +₹1,426.75), or its blocked population (one leg, registry still empty). Further progress needs a genuinely new signal/mechanism or December fresh data judging this candidate. Records: `nifty_engine_log.md` (Round 3 block), `nifty_engine_frozen.md` (Run 3 Round 3 section), `nifty_engine_lessons.md` (lessons 41–45), `nifty_engine_state.json` (cycle 73, december_candidate updated), per-cycle summaries `nifty_engine_run3r3_cycle*_summary.json`.
