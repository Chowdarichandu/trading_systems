# Invention Round — Two Fresh Signal Families, Built and Gated

### Owner order 2026-11-12 17:03 IST: "I need twenty thousand per month — work on it"
### Source brief: `target_20000_gap_programme_2026-11-12.md` Part 4 (Bank #1, Nifty #1)
### Paper only · Real money ₹0 · Nothing armed · Frozen November primaries untouched · Output = December candidates only

**Verdicts, up front:**

| Family | Verdict | Gated Jan–Oct 2026 | ₹/month | November counterfactual |
|---|---|---|---|---|
| **A — Bank afternoon pullback-continuation (BANK-APC v1)** | **FAIL** | **−₹15,385.00** / 100 legs | **−₹1,538.50** | 2 signals; premium not in any existing store → both NOT_COMPUTED, ₹0 evidenced |
| **B — Nifty weekly-expiry-day book** | **NOT TESTABLE** | — | — | — (same data gap; see §3) |

**Effect on the stacked target:** neither family adds anything. Bank stacked stays **₹16,897.25/month** (gap to ₹20,000: **₹3,102.75/month**). Nifty stacked stays **₹12,347.90/month** (gap: **₹7,652.10/month**). Family A's gated pace was negative, so even arithmetic stacking would have *reduced* the Bank stack; Family B cannot be scored until a defined data build lands (§3).

Computation: `invention_round_2026-11-12.py` → `invention_round_2026-11-12_results.json`; Family A trades: `invention_round_2026-11-12_familyA_trades.csv`. The full controls gate ran in the same run as first scoring for both families (coverage verification for B *is* its first gate).

---

## 1. FROZEN SPEC — fixed before scoring (single configuration per family, no sweep)

### Family A — BANK-APC v1 (Bank Nifty afternoon pullback-continuation)

Mechanically distinct from every closed route: not a range-break capture (BREAK-CAPTURE / EVE-06b / EVE-12 closed), not an admission filter on an existing book, not the owner ladder, not causal-chain selection. The trigger is a **retracement-and-hold against a first-half trend leg**, entered in the afternoon in the trend direction — the untested form named in the gap programme for the session-coverage flaw (4 missed afternoon moves in November).

- **Population:** Bank Nifty days Jan–Oct 2026 present in the premium-covered store — **185 days**. Disclosed store facts: the spot store's 7 extra jul-oct days (2026-07-29/30/31, 08-26/27/28/31) have no premium coverage anywhere, and 11 NSE calendar days are absent from the spot store entirely (2026-01-28/29/30, 02-25/26/27, 04-29/30, 05-27, 05-29, 10-28) — the post-expiry fetch gaps every Bank book in this workspace shares.
- **Trend leg (first half):** day_open = open of the 09:15 bar; REF = close of the 12:55 bar. REF − day_open ≥ **+150.0** → up-leg (CE); day_open − REF ≥ **+150.0** → down-leg (PE); otherwise no trade. Leg extreme = max high / min low of bars 09:15–12:55; leg size measured origin (day_open) → extreme.
- **Pullback:** level PL = extreme ∓ **25%** of the leg. Afternoon scan (bars 13:00–14:30, in order): a bar closing beyond day_open kills the day (origin broken — checked first, before trigger/signal on the same bar). The first bar touching PL triggers the pullback; the first bar at/after the trigger that **closes in the trend direction** (CE: close > open; PE: close < open) is the signal bar. One leg per day, first pullback only.
- **Entry/strike:** entry at the next bar (signal + 5 min), premium = that bar's open (house convention). Strike = round100(signal close); expiry = monthly in force; on the expiry day the strike shifts 100 ITM (CE −100 / PE +100) per the incumbent books' convention.
- **Geometry:** the incumbent stack's input geometry (P21) with the brief's square-off — stop **−50**; at **+90** the leg becomes a runner, floor locks **entry+50**, second target **+150**; **SQ 15:10** at that bar's close. Replay semantics mirror `bank_aggressive_tune_score.replay_mod` exactly (stop before target on every bar incl. entry; runner phase from the bar after the trigger bar). Lot 30, cost ₹220/trade.
- **Premium source:** the `option_5m.csv` chain store — cross-validated against the JSON candle store the incumbents score from before use (see §2, audit).

**Gate (pre-registered, PASS requires all):** ① total > 0 · ② H1 and H2 both > 0 · ③ red months ≤ 3 of 10 and worst month ≥ −₹5,000 · ④ ex-top-3 legs > 0 · ⑤ total beats delay-6 placebo **and** flipped-direction placebo (unfillable placebo legs at candidate net, the disclosed house convention — in the event, fills were 0 for both) · ⑥ NC = 0 · ⑦ timing/admission audit clean and independent re-sum exact.

### Family B — Nifty weekly-expiry-day book

Population would be the **33 Nifty weekly expiry days** Jan–Oct 2026 (`nifty_engine_run3_expiries.json` minus monthly expiries). Per the brief, premium-chain completeness is verified **first**; no entry rule is defined or scored unless the chain can support causal scoring (§3).

---

## 2. FAMILY A — RESULT: FAIL

| Measure | Value |
|---|---|
| Legs generated / scored | 100 / 100 (NC = 0) |
| **Total Jan–Oct** | **−₹15,385.00** |
| ₹/month | **−₹1,538.50** |
| Expectancy | −₹153.85/leg |
| Win rate | 35.0% (47 CE / 53 PE) |
| H1 (Jan–May) | +₹6,909.00 |
| H2 (Jun–Oct) | −₹22,294.00 |
| Ex-top-3 legs | −₹28,225.00 (top-3 are three identical +₹4,280 runner targets) |
| Placebos | delay-6: −₹25,192.00 · flipped: −₹34,360.00 — both beaten, and it does not matter: the book itself loses |
| Gross of costs | +₹6,615.00 (+₹66.15/leg) — the raw direction is nearly flat; ₹22,000 of costs plus the exit geometry turn it negative |

**Month table:** Jan +₹1,009.00 (14) · Feb +₹6,290.00 (7) · Mar −₹3,080.00 (14) · Apr +₹7,890.00 (12) · May −₹5,200.00 (10) · Jun −₹5,200.00 (10) · Jul **−₹12,040.00** (7) · Aug −₹8,600.00 (5) · Sep −₹2,814.00 (9) · Oct +₹6,360.00 (12). **Six red months.**

**Gate legs:** ① FAIL (−₹15,385) · ② FAIL (H2 −₹22,294) · ③ FAIL (6 red months; worst −₹12,040) · ④ FAIL (ex-top-3 −₹28,225) · ⑤ PASS · ⑥ PASS · ⑦ PASS. **Verdict: FAIL — 4 of 7 legs.**

**Failure mode, mechanically:** 59 of 100 legs stop out at the full −₹1,720 (−₹1,01,480 in stops). Only 31 legs ever reach the +90 trigger; 15 of those reach the +150 runner target (+₹4,280 each). After a first-half trend leg and a 25% pullback-hold bar, the afternoon move more often continues *against* the entry than resumes — the pullback-hold candle as frozen carries no tradable edge after costs. This closes the afternoon-pullback form as specified; per standing rules the failed configuration is not retested identically and no parameter of it was re-fitted in this run.

**Audits (all in-run):** timing/admission — the leg set was re-derived by a second, independent implementation (pandas, explicit cutoffs); leg-for-leg identical, 0 violations; every entry is exactly signal+5 and inside the ≤14:30 window. Data integrity — the chain store was compared bar-for-bar against the JSON store the incumbent books score from: **558 contract files, 42,149 bars, 0 mismatches** (the stores are the same underlying data). Independent re-sum from the emitted trades CSV: exact (−₹15,385.00). One leg (2026-01-05 PE 60200) was additionally hand-verified against raw spot bars end-to-end.

**November counterfactual (Nov 2–12, separately labelled, not in the gate):** the frozen generator produced **2 signals** on November spot — 2026-11-06 CE 58300, entry 13:15; 2026-11-11 CE 61000, entry 13:05 (both expiry 2026-11-23). Neither contract's premium candles exist in any existing store (`november_shadow_data` holds only prior books' legs; the chain store ends at October), so both are **NOT_COMPUTED** — the counterfactual evidences ₹0, which means *no evidence*, not a zero result. (2026-11-08's 14-bar muhurat session has no first half and cannot signal; Nov 10 was a holiday.)

---

## 3. FAMILY B — RESULT: NOT TESTABLE (premium chain does not exist)

The completeness verification ran before any entry rule was defined, and it fails outright:

- **33** weekly expiry days form the population. Expiring-contract 5-min premium candles exist for **15 of 33 days — exactly ONE contract per day** (one strike, one direction), every one of them in `aggressive_data`, every one fetched because a *prior programme's leg* needed it (the run-3 weekly fetch targeted pool legs; 13 of the 15 are the very contracts DEC-S1's Component C sleeve trades). A standalone book cannot be built on this: any mechanical rule that ever wants the other direction, or ATM at a different signal time, has no data — and a "rule" that trades whichever single contract happens to exist is not a new family, it is a re-score of the Component C sleeve, a closed route.
- **18 of 33 days have zero expiring-contract candles:** 2026-01-13, 01-20, 02-03, 02-10, 03-02, 03-10, 03-24, 04-21, **all four June days** (06-02, 06-09, 06-16, 06-23), 08-11, 09-01, 09-15, and **all three October days** (10-06, 10-13, 10-19). June and October are entirely dark.
- There is **no Nifty chain store** in the workspace (no `option_5m.csv` analogue); the JSON store is leg-indexed, not chain-indexed — which is exactly the gap the gap programme flagged ("chain completion is part of the brief").
- November is no better: the expiries registry ends 2026-10-27 and November shadow data holds only prior books' legs, so no November counterfactual is computable either.

**Exact data build required (nothing else blocks this family):** a historical 5-min candle backfill of the expiring weekly contract for each of the 33 weekly expiry days — for each day, every strike on the 50-pt grid inside [day's spot low − 100, day's spot high + 100], both CE and PE, expiring that day. That union covers any ATM-at-signal-close (round100) entry rule and its same-strike flip placebo. **Size: 760 contract-day candle files** (8–20 per day across the 33 days), via the expired-contract + historical-candle route already proven in `nifty_engine_run3_fetch_weekly.py` (Upstox expired option contracts, browser User-Agent header per the standing fix), saved as `candles_NIFTY_<strike><CE|PE>_<day>_<day>.json` in `aggressive_data`. Once that build lands, the family can be frozen, gated, and November-counterfactualed on the same terms as Family A. Until then: **NOT TESTABLE — no figure exists and none is approximated.**

---

## 4. What this means for the ₹20,000 target

| Segment | Stacked before | Family A / B contribution | Stacked after | Remaining gap |
|---|---|---|---|---|
| Bank Nifty | ₹16,897.25/mo | A: FAIL (−₹1,538.50/mo gated — adds ₹0; stacking it would subtract) | **₹16,897.25/mo** | **₹3,102.75/mo** |
| Nifty | ₹12,347.90/mo | B: NOT TESTABLE (adds ₹0 until the 760-file build lands) | **₹12,347.90/mo** | **₹7,652.10/mo** |

The afternoon session-coverage flaw is now rejected in **four** mechanically distinct forms (range-break ×3, pullback-continuation ×1): the afternoon moves November showed are not capturable by spot-shape entries under the incumbent exit geometry and cost load, on ten months of evidence. Bank's remaining ₹3,103/month and Nifty's ₹7,652/month still require either the option-chain-native axis (forward collector — a data build, per the gap programme) or the one approval-gated book already inventoried (SHORT-FOLLOW R7-M1 is *inside* the stacked figures above — it is not counted twice here). Family B becomes testable the day its 760-file historical build is run; that build is a fetch job, not a research question.

*Method note: both families were scored exactly once, under the spec frozen in §1, with the standing controls gate (timing + admission/feature audits, both placebos, halves, full month table, ex-top-3, independent re-sum) executed in the same run. No parameter was adjusted after any result was seen.*
