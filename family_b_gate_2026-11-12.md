# Family B Gate Run — Nifty Weekly-Expiry-Day Book (NIFTY-WEXP v1)

### Follow-through on `invention_round_2026-11-12.md` §3: the 760-file chain build landed, so the family is testable
### Paper only · Real money ₹0 · December candidate only · Nothing armed · Frozen November primaries untouched

## VERDICT: **FAIL** — 4 of 7 gate legs fail

| Measure | Value |
|---|---|
| **Total Jan–Oct 2026** | **+₹10,237.25** (positive — but the gate is not a total-only test) |
| Legs | **29** (of 33 expiry days; 4 days had no system signal) · NC = **0** |
| ₹/month pace | **+₹1,023.73** |
| Win rate / FT90 | 12W / 17L · FT 24.1% (7 of 29 reached +90) |
| H1 (Jan–May) | **−₹14,959.75** ✗ |
| H2 (Jun–Oct) | +₹25,197.00 ✓ |
| Ex-top-3 legs (= ex-top-3 days, one leg/day) | **−₹18,352.75** ✗ |
| Placebos | delay-6 **+₹11,420.25 — BEATS the candidate** ✗ · flipped −₹16,152.75 (beaten ✓) |
| Red months | **5 of 10** ✗ · worst month **−₹10,410.00** ✗ |

**Gate legs:** ① total > 0 **PASS** · ② halves both > 0 **FAIL** (H1 −₹14,959.75) · ③ bleed (≤3 red months, worst ≥ −₹5,000) **FAIL** (5 red; worst −₹10,410) · ④ ex-top-3 > 0 **FAIL** (−₹18,352.75) · ⑤ both placebos beaten **FAIL** (delay-6 +₹11,420.25 > candidate +₹10,237.25) · ⑥ NC = 0 **PASS** · ⑦ audits clean + re-sum exact **PASS**.

**Effect on the target:** Family B adds **₹0**. Nifty stacked stays **₹12,347.90/month** (gap to ₹20,000: **₹7,652.10/month**). Even had it passed, its +₹1,023.73/month pace would only have lifted the stack to ₹13,371.63/month — ₹6,628.37 short. The expiry-day population (≤33 days/year, one leg/day) is structurally too thin to close a ₹7,652/month gap at any expectancy this data supports.

Computation: `family_b_gate_2026-11-12.py` → `family_b_gate_2026-11-12_results.json`; trades: `family_b_gate_2026-11-12_trades.csv`. The full controls gate ran in the same run as first scoring; the spec below was frozen in the script header before any premium was read.

---

## 1. FROZEN SPEC — NIFTY-WEXP v1 (fixed before scoring, single configuration, no sweep)

- **Population:** the **33 Nifty weekly expiry days** Jan–Oct 2026 (expiry registry minus the 10 monthly expiries — `R8.weekly_expiry_days()`). One leg per day maximum.
- **Entry — the day's FIRST U1 system signal.** The sysmap (`nifty_engine_r5_ws0.build_sysmap`, the same causal per-system signal store every incumbent Nifty book reads) holds each system's earliest signal time per (date, direction) for the four U1 systems: **(lA) v2 · V5 v2 · Skill V3 · Volrix (b)**. On an expiry day, take the earliest signal time across **all systems and both directions**; if that time belongs to exactly one direction, enter that direction at that time. A cross-direction tie at the earliest time → no leg (frozen tie-break; never occurred). A first signal after 15:10 is inadmissible (the book cannot enter after its own square-off) → no leg (never occurred). **No confirmation keying (no C3), no time window, no exclusion against any other book's keys — standalone.**
- **Strike/contract:** strike = **atm100(spot open at entry time)** (the incumbent convention); the contract expiring **that day**, premium from `nifty_weekly_expiry_chain/` only (760/760 files, cross-validated 15/15 identical). Entry fill = open of the first chain bar at/after the signal time (the house `nifty_engine_score.replay` semantics).
- **Geometry — G7, frozen** (`nifty_engine_score.G7` + replay defaults): stop **−50**; at **+90** the leg becomes a runner, stop moves to **entry+50**, second target **+150**; square-off **15:10** (runners also 15:10); no break-even arm. **Lot 65, cost ₹220/trade.**

**Why this is not a re-score of DEC-S1 Component C.** Component C is a *residual sleeve inside* DEC-S1: it admits **only Skill V3** signals, **only inside 09:15–11:00**, and **only on (date, direction) keys that neither the standing book (A) nor the fade book (B) already holds** — 13 legs, scored at DEC-S1's standing geometry (lock +60 / tgt2 +175 / SQ 15:20). Family B differs on every axis: signal set (all four U1 systems), timing rule (the day's first signal at any time of day), population treatment (all 33 weekly expiry days, standalone, no in-pair exclusions), strike rule (its own atm100 at its own entry time — any strike in the fetched band), and geometry (G7). Overlap is disclosed, not hidden: **12 of B's 29 legs share a (date, direction) key with a C leg** (on those days Skill V3 was the day's first signal and inside C's window too — the same underlying system signal, held in a different book construction under different geometry); **17 legs are keys C never held**, and 3 legs share keys with Component A (which trades those keys in the *monthly* contract — a different instrument).

## 2. RESULT DETAIL

**Month table (all 10 months):** Jan **+₹7,967.75** (2) · Feb −₹4,067.00 (2) · Mar **−₹10,410.00** (3) · Apr −₹62.00 (3) · May −₹8,388.50 (3) · Jun +₹4,034.00 (4) · Jul −₹6,942.25 (3) · Aug +₹2,307.25 (3) · Sep **+₹13,579.25** (4) · Oct **+₹12,218.75** (2). Four days generated no leg — no U1 system signalled at all: 2026-01-13, 02-03, 03-10, 10-19.

**Exit mix:** square-off 15 (most never reached +90 — expiry-day premium decay grinds them out at the close) · full stops 7 (every one the full −₹3,470) · runner targets 4 (Jan 20, Jun 2, Sep 15, Oct 13 — each exactly +₹9,530) · runner stops 2 (+₹3,030 each) · runner square-off 1.

**Failure mode, mechanically:** this is a regime-split, top-heavy book. The entire positive total is four runner targets (+₹38,120); remove just the top 3 and the book is −₹18,352.75. H1 bleeds steadily (Mar −₹10,410, May −₹8,388.50) before H2 recovers — the same first-half/second-half asymmetry Family A showed, in the opposite segment. And the timing itself carries no edge: **entering the same legs 30 minutes later (the delay-6 placebo) makes MORE money (+₹11,420.25) than the first-signal rule** — on expiry days the day's first U1 signal is systematically premature; whatever the population earns, it is not earned by being first. The flipped-direction placebo (−₹16,152.75) confirms the direction vocabulary is not noise — it is the timing and the H1 regime that fail.

**Audits (all in-run):** timing/admission — every leg's entry bar exists in its chain file and the scored entry equals that bar's open (29/29, 0 violations). Independent re-derivation — the leg set was rebuilt by a second implementation (pandas over the four raw sysmap source CSVs, replicating `build_sysmap`'s own filters, plus the spot CSV): **leg-for-leg identical** (date, direction, entry time, strike). Independent re-sum from the emitted trades CSV: exact (+₹10,237.25). One leg hand-verified end-to-end against the raw chain file: 2026-01-20 PE 25500 — entry 09:40 @ 79.30 (bar open ✓), no stop touch, +90 trigger 14:50, runner target +150 on the 15:10 bar @ 229.30 → +₹9,530.00 ✓. NC = 0: every generated leg scored from the chain store; no leg was estimated or substituted.

**November counterfactual: NOT_COMPUTED.** The chain store covers Jan–Oct 2026 only (0 November files), and `november_shadow_data` (27 files) holds only prior books' legs — expiring-weekly premium candles for November's weekly expiry days exist in no store. Per standing rules the counterfactual is marked, not estimated.

## 3. What this closes

The weekly-expiry-day axis is now tested and closed in this form: a standalone first-signal book on the expiring contract, under the incumbent G7 geometry, fails on halves, bleed, concentration, and its own delay placebo. Per standing rules the failed configuration is not retested identically and no parameter was adjusted after any result was seen. Nifty's remaining ₹7,652.10/month gap to the ₹20,000 target is untouched by this family; the gap programme's other Nifty axes (the option-chain-native family — a forward data build, not a backtest) remain the open route.

*Method note: scored exactly once under the frozen spec above, with the standing controls gate (timing + admission/feature audits, both placebos, halves, full month table, ex-top-3 legs and days, independent re-sum) executed in the same run.*
