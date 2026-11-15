# NIFTY engine — ROUND 5 report (2026-11-02)

Segment: NIFTY index options, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.
Floor: ₹1,50,000 Jan–Oct 2026 (₹15,000/month). November primary/spec/logs untouched (read-only at most).
Starting book: the ADOPTED book (CH3-R × lock50/TGT2-175) = +₹114,921.75. Round 3's Cycle-40 banking stays VOID (retracted Round 4); nothing this round resurrects it.

## ⚠️ WS0 HEADLINE — the adopted book's confirmation was partly look-ahead; the round re-baselined before scoring anything

**16 of the adopted book's 44 legs were admitted at a bar where their admission condition ("confirmed by ≥ 2 systems") did not yet exist.** The pool records a key's entry as the EARLIEST system's entry bar, but `source_systems` counts every system that fired on the key that day — including systems whose own entry bar came later. Per-system entry times recovered from the merge's own input files (`u1_janoct_merge.py` inputs) give each confirmed leg's confirmation-completion bar t2 (second-earliest system entry):

- **9 legs: t2 falls after CH3-R's 09:55 window** — causally, CH3-R never takes them. Their adopted-book nets sum **+₹45,499.25** (eight winners, one loser): 08 Jan +5,847.75 (t2 11:20) · 11 Mar **+11,155.00** (t2 10:45) · 16 Apr +3,030.00 (t2 12:35) · 12 May +8,087.00 (t2 10:50 — this is Round 4's "May winner"; May's one runner was a confirmation-lag leg) · 01 Jun +5,344.00 (t2 13:10) · 24 Jun +6,150.00 (t2 10:05) · 13 Jul +6,325.50 (t2 10:00) · 31 Aug −3,470.00 (t2 10:35) · 26 Oct +3,030.00 (t2 10:00).
- **7 legs: t2 ≤ 09:55 but after the recorded 09:20 entry** — all Volrix-rep legs (Volrix fires 09:20 on a prior-day trigger; Skill confirms at 09:35–09:50). Re-timed to the confirmation bar (strike = ATM100 at that bar, per the frozen convention; 4 contracts fetched via the expired-instruments route, 75–77 bars each, entry bars verified): adopted **+₹16,390.25 → causal −₹2,414.25** (Δ **−₹18,804.50**). The 15–30 minutes WAS the value: 02 Feb −220 → −3,470 · 02 Mar −220 → −3,470 · 27 Apr +1,411.50 → −3,470 · 09 Oct +11,155 → +4,655 · 16 Feb +7,953.75 → +7,030.75 · 20 Mar −3,470 → −3,470 · 09 Jul −220 → −220.
- The other 28 legs are causal as recorded (7 solo (lA); 21 confirmation ties — both systems' entries at the same bar).

**Causal book (the adopted rule read causally, full controls in the same run): +₹50,618.00** — 35 trades, FT 34.3%, 0.86/wk, halves +25,231.25/+25,386.75, placebo +23,542.25 beaten, ex-top-3 +17,312.25, timing audit 35/0, NC 0, re-sum exact, no red month-ends. Months: Jan +18,127.00 · Feb +10,709.25 · Mar +7,245.00 · Apr −440.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,729.00 · Aug −1,717.25 · Sep +5,020.00 · Oct +15,265.00.

**Quantified effect: −₹64,303.75 — 56.0% of the adopted headline depends on the confirmation-lag convention** (+45,499.25 in legs the causal rule drops, +18,804.50 in entry-timing value on the re-timed legs). Pace falls to **₹5,061.80/month; floor gap ₹99,382.00**.

Fair context, recorded with the finding: this is a **documented convention**, not a hidden bug — the frozen live producer (`live_signal_producer.py`, NIFTY C3 note) already states that the EOD construction enters a confirmed key at its earliest leg while the live entry is at the confirming leg ("the documented confirmation-lag class"). It nevertheless fails WS0's certification standard — the same standard that voided Cycle 40 (lesson 46): a selection input must be known at the decision bar. The affected bankings are the C3/C3L/CH3-R family scores built on earliest-entry confirmation (the incumbent C3+G7 line included); per the WS0 freeze, the causal book replaced the adopted book as this engine's working baseline for all Round-5 gating, and the adoption record in `nifty_engine_frozen.md` / `nifty_engine_state.json` is annotated, not rewritten. **December consequence, stated plainly: traded live under the producer's confirmation-entry semantics, the adopted book's live expectation is the causal figure (+₹50,618 pace), not +₹114,921.75 — unless December intends to enter at the first system's bar and treat later confirmation as a post-entry fact, which is a different rule from the one frozen for the live primary.**

## WS0 audit certificate — every other feature in the adopted book's construction

| Feature / condition | Inputs | Known at | Verdict |
|---|---|---|---|
| (lA) v2 signal | confirmer-index OR break (bars ≤ signal bar), own rescan close < ORL & < PDL, OR width (09:15–09:25 bars), room vs prior-day PDH/PDC/PDL | signal bar close; entry = next bar open | CAUSAL |
| Skill V3 signal | OR from 09:15/09:20/09:25 bars; first close beyond OR in 09:30–11:30; 09:30-PE rule: that bar's close vs PDL (prior-day low) | signal bar close; entry = next bar open | CAUSAL |
| V5 v2 membership | V4 (prior-day levels + bias) and Skill-filtered candidates (room from prior-day levels at the signal close); dedup by static setup rank; prospective = room × provisional unit at signal close; entry = first option candle after the signal | signal bar close | CAUSAL, with caveat ↓ |
| V5 weekly portfolio cap | rank by signal-time-only features (`cap_select` docstring), then date; 3/week + 1/symbol/week | the week's candidates' signal times | CERTIFIED WITH CAVEAT: a V5 leg's pool existence can depend on another same-week candidate's signal-time features (including a later one). Cross-leg portfolio rule inside V5's frozen definition; uses no leg's own post-entry data and moves no entry. Disclosed, not voided |
| Volrix (b) | prior trading day's close-to-close ≤ −1.0%; 10-session cooldown over prior firings; entry 09:20 | day's open (R4 vintage calibration of record) | CAUSAL |
| Bias (V4/V5 internals) | prior trading day's close position in its range | day's open | CAUSAL |
| CH3-R selection — confirmation count | `source_systems` on the pool record | **the last source's entry bar — NOT the leg's entry bar** | **VIOLATION (headline above)** |
| CH3-R 09:55 window, EXP0, DTE | recorded entry time; calendar | entry / always | CAUSAL as rules (the window's input was the violation) |
| Strike | ATM nearest 100 at the entry bar (validation: pool `entry_spot` reproduces 40/40 recorded strikes; full_hist spot open 43/44) | entry bar | CAUSAL |
| Exit geometry | bars ≥ entry bar only; entry = open of the entry bar; every system's signal bar strictly precedes its entry bar | — | CAUSAL (entry-bar audit 44/0 in R4; 35/0 on the causal book) |
| Retracted Cycle-40 signature | — | — | stays VOID; not used anywhere this round |

## Workstream verdicts (all gated vs the causal book, full controls in the same run)

**WS1 — August causal rescan (Cycle 101, diagnosis): NO separator; August closed permanently.** On the causal book the August wound is 2 legs (11 Aug −1,152.75, 19 Aug −564.50; the 31 Aug leg was dropped by WS0). Full causal scan (TRUE prior-day return, gap, pre-entry morning range/move, entry premium, DTE, bias; bands + PE conjunctions, book-wide): prior-day return / gap / premium / DTE / bias yield no negative winner-free set containing both legs. Morning range yields only wound-fitted notches — [0.400, 0.419] is the two August legs alone (−1,717.25); [0.377, 0.419] adds two losers (−5,407.25, 0 winners) but its edges are set by winners 0.012–0.021 away on both sides (0.365 → +4,304.00; 0.440 → +11,155.00) and the August values are mid-distribution — the May standard (Round 4 WS1) rejects fitted boxes, and Round 4's WS4 found every morning-range tercile positive. No signature frozen, no Cycle 102 scored.

**WS2 — strike axis: both cells rejected; family closed on this book too.**
- Cycle 103 ITM-100 blanket: **+₹37,104.50** (FT 37.1%; placebo +37,029.75 essentially tied) — fails net (−13,513.50), FT, a June green→red flip, frequency.
- Cycle 104 ITM-100 expiry-scoped (DTE ≤ 4): **+₹48,508.75** — fails net (−2,109.25), FT, frequency.

**WS3 — DTE-0 re-admission under expiry-day geometry: rejected in all five cells; EXP0 confirmed causally.** Population (frozen, causally admissible): 24 Feb PE 09:35, 30 Jun PE 09:45 (causal re-time), 29 Sep PE 09:35 — the 30 Mar leg is excluded by the same rule that dropped 9 adopted legs (confirmation completes 11:30 > 09:55). The population loses under every geometry: control (book geometry) **+₹46,899.75** (population −3,718.25) · sq 14:30 **+₹47,484.75** (−3,133.25, the best cell) · sq 15:00 **+₹47,293.00** · arm +40 **+₹46,899.75** (inert — identical) · lock +40 **+₹46,249.75**. All fail net, FT and frequency.

**WS4 — entry-time exit split: both cells rejected.**
- Cycle 110 Cell A (entry > 11:00 → lock +40): **+₹49,968.00** — fails net (−650.00), FT, frequency.
- Cycle 111 Cell B (entry ≤ 11:00 → lock +40): **+₹50,767.50** — net ABOVE the causal book by +₹149.50 (one-leg plateau noise, lesson 36), but fails the FT line (34.3% < 42.0%) and frequency. Not banked.

**WS3 contingency — Cycle 112 (population at sq 15:00 + arm +40): +₹47,293.00** — identical to Cycle 107 (the arm never binds on these legs); rejected. (Fired per its freeze: WS1 yielded no technique and WS5 has no combination.)

**WS5 — combinations: none** (no Round-5 banking exists). Closes by statement per its freeze.

## Structural note on the gate (recorded, NOT acted on)

Two gate lines were calibrated on the adopted book's figures — FT ≥ 42.0% (vs its 45.5%) and frequency ≥ 1.00/wk (vs its 1.08) — which were themselves computed including the inadmissible legs. On the causal book (FT 34.3%, 0.86/wk), **every same-population candidate fails the FT line by construction**, whatever its net (Cycle 111 beat the net and still failed). The clauses were NOT relaxed mid-round (lesson 39 discipline: a gate the engine re-bases when it becomes inconvenient is not a gate). Re-basing them is a pre-registered decision for a future round or the owner, stated before scoring — flagged here as the round's open item alongside the floor gap itself.

## Ending scorecard

| | |
|---|---|
| Working book (post-WS0 baseline) | Adopted rule read causally: CH3-R with confirmation-completion admission + EXP0 + BE50 arm + lock +50 + TGT2 +175 |
| Jan–Oct 2026 total | **+₹50,618.00** |
| Monthly pace | **₹5,061.80** vs ₹15,000 floor |
| **Remaining gap** | **₹99,382.00** |
| Trades / FT / frequency | 35 / 34.3% / 0.86 per week |
| Months | Jan +18,127.00 · Feb +10,709.25 · Mar +7,245.00 · Apr −440.00 · May −10,410.00 · Jun −3,910.00 · Jul +10,729.00 · Aug −1,717.25 · Sep +5,020.00 · Oct +15,265.00 |
| Halves | +25,231.25 / +25,386.75 |
| Placebo (+30 min) | +23,542.25 — beaten |
| Ex-top-3 | +17,312.25 |
| Timing audit / NC / re-sum | 35/0 · 0 · exact |
| December candidate of record | Chandu's adopted book (+₹114,921.75 as recorded, waivers unchanged) — **annotated with the WS0 finding: its live-semantics figure is the causal +₹50,618.00** |

**Round-5 totals:** WS0 audit (Cycle 100) + WS1 diagnosis (Cycle 101) + 10 gated candidate cycles (103–112). Banked: **none**. Net effect: ₹0 by banking; the round's material event is the WS0 re-baseline (−₹64,303.75 of convention value identified and removed from the working book). Every directed family — August signature, strike axis, expiry-day geometry, entry-time exit split — was measured on the causal book with full controls and rejected. Records: `nifty_engine_frozen.md` (Round-5 freezes + results), `nifty_engine_log.md`, `nifty_engine_lessons.md` (52–56), `nifty_engine_state.json` (cycle 112, run5 complete), WS0 detail `nifty_engine_r5_ws0_detail.json`, WS1 scan `nifty_engine_r5_ws1_diag.json`, per-cycle summaries `nifty_engine_run3r5_*_summary.json`, harnesses `nifty_engine_r5_*.py`. November primary untouched throughout.
