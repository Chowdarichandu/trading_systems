# BANK NIFTY FAST-EARNER TUNING — 2026-11-12 (overnight)

**Owner directive (2026-11-12 20:57 IST):** Bank Nifty is the first and sole earner focus — "I need something that's working." The wanted shape: trades that make money **fast**, resolved within minutes (his reference winners: the NS1 legs of Nov 11/12, target in 1–4 five-minute bars). Nifty got no programme tonight. **Paper only, real money ₹0. December candidates only; frozen November primaries untouched.**

## VERDICT — NOTHING PASSED BOTH TESTS

No fast-exit variant passes the Jan–Oct gate on either stream, and no fast-exit variant passes the owner's Nov 2–10 test on either stream. **Every variant FAILS BOTH.** The only configuration that passes the owner's test anywhere is the incumbent stack itself (FE-4 on stream A, window +₹760) — i.e., the fast-earner shape, as specified, does not exist in these two streams. Details and the closest variants are below; bars were never moved and no failed variant will be retested identically.

| Stream | Variant | Jan–Oct total (FE-4 = control) | Gate | Nov 2–10 window | Owner test | Final |
|---|---|---|---|---|---|---|
| A — Stack v2 (111 legs) | FE-1 +50/−50, TS bar 2 | +₹20,217.00 (+₹127,351.50) | FAIL | −₹440.00 | FAIL | **FAILS BOTH** |
| A — Stack v2 | FE-2 +30/−40, TS bar 2 | −₹4,939.50 | FAIL | −₹740.00 | FAIL | **FAILS BOTH** |
| A — Stack v2 | FE-3 BE-arm +30, tgt +90, TS bar 3 | +₹36,844.50 | FAIL | −₹1,940.00 | FAIL | **FAILS BOTH** |
| B — NS1 standalone (16 legs) | FE-1 +50/−50, TS bar 2 | +₹4,772.00 (+₹10,269.50) | FAIL | −₹215.00 | FAIL | **FAILS BOTH** |
| B — NS1 standalone | FE-2 +30/−40, TS bar 2 | +₹2,102.00 | FAIL | −₹740.00 | FAIL | **FAILS BOTH** |
| B — NS1 standalone | FE-3 BE-arm +30, tgt +90, TS bar 3 | +₹8,855.00 | FAIL (1 leg) | −₹1,160.00 | FAIL | **FAILS BOTH** |
| A — Stack v2 | FE-4 control | +₹127,351.50 | — | **+₹760.00** | **PASS** | incumbent |
| B — NS1 standalone | FE-4 control | +₹10,269.50 | — | −₹3,440.00 | FAIL | incumbent |

**Closest variant:** FE-3 on stream B — the only variant that fails the gate on a single leg (total: +₹8,855.00 vs FE-4's +₹10,269.50; it beats both placebos, both halves, ex-top-3, and flips no month). It still fails the owner's test (−₹1,160 in the window). Closest on the owner's test is FE-1 on stream B (−₹215 — ₹216 short of profitable), but it fails the gate twice over, including losing to its own delay-1 placebo.

---

## 1. Data resolution — what "fast" can honestly mean here

Premium data is **5-minute candles**. A "1–3 minute" hold is **not verifiable** on this data — intrabar ordering is unknowable. The verifiable form of the owner's spec, frozen before scoring: exits resolved **on the entry bar or the next 1–2 bars (≤ ~10 minutes from the entry bar's open)**; FE-3 allows the 3rd bar (≤ ~15 minutes). Nothing finer is claimed anywhere in this programme. Intrabar convention = the workspace's frozen one, shared with the incumbent machinery: within a bar the **stop is checked before the target**, level exits fill **at the level**, time-stop exits fill at the bar's **close**. Bars are counted positionally in each contract's recorded candle series (entry bar = bar 0).

## 2. What was run (spec frozen in the script header before any FE number existed)

- **Stream A:** TUNED STACK v2's 111 legs, entries frozen exactly as recorded — including the incumbent EVE-06(a) re-entry set (the ladder build's own rule: entries unchanged, only exits change).
- **Stream B:** the NS1 second-leg stream standalone — the `NS1_second` legs of the frozen causal pipeline (`assemble6` rows21, the same generator the November legacy book draws from), including the 3 early legs EVE-19 skips inside the stack. That stream has **16 legs Jan–Oct** — inside the books, NS1 is a small, concentrated stream (its FE-4 ex-top-3 is already negative, −₹2,153.50; January alone is +₹11,523 of its +₹10,269.50). Its November fame rests on 2 trades.
- **Variants** (identical on both streams; FE-1..FE-3 replace every leg's exit geometry — incumbent params play no role):
  - **FE-1:** target +50 / stop −50 premium points; time-stop at the close of bar 2.
  - **FE-2:** target +30 / stop −40; time-stop at the close of bar 2.
  - **FE-3:** stop −50 until a bar's high reaches +30, arming a breakeven stop at entry from the next bar (frozen `replay_mod` arm semantics); target +90; hard time-stop at the close of bar 3.
  - **FE-4:** control — each stream's recorded incumbent exits (no re-simulation).
- **Gate (standing controls gate, same run, per variant per stream, vs that stream's FE-4):** total must beat FE-4; total must beat the **delay-1-bar placebo** twin (delay-6 also computed); halves rule; ex-top-3 legs and days > 0 and ≥ FE-4; no green month flips red; no exit-before-entry; NC = 0. Audits in-run: admission (entry keys + premiums identical to FE-4), **feature-timing/causality** (every leg re-simulated on its series truncated at its own exit bar reproduces the identical exit), fill audit (every exit is a variant level or the exit-bar close), independent re-sum from the written CSVs. **All audits clean on all six variant books; NC = 0 everywhere; both placebos computed with 0 candidate-net fallback legs.**
- **Owner's acceptance test (in addition, applied exactly):** November counterfactual over **Nov 2–10** (trading days Nov 2, 3, 4, 5, 6, 9; Nov 10 = Diwali, closed) from the frozen November records on real November premium candles — stream A legs from `november_shadow_stack_bank_log.csv`, stream B legs from the NS1 rows of `november_paper_bank_log.csv`. Identity asserted before scoring: A window FE-4 = **+₹760.00**, A full Nov 2–12 = −₹960.00; B window FE-4 = **−₹3,440.00**, B full = +₹1,520.00. A variant "works" only if its window net is **> 0**.

**Anchors (asserted before scoring):** frozen pipeline reproduced 99/99; phase-2 re-entry statics 16/16; v22 leg-for-leg (90 legs, +₹91,450.50); after-c4 (106, +₹102,969.50); stack v1 (115, +₹123,471.50); **stream A incumbent leg-for-leg vs the frozen eve19 record (111 legs, +₹127,351.50, all 10 months positive)**; stream B legs' recorded exits reproduced leg-by-leg from the pipeline.

## 3. Stream A — TUNED STACK v2 (111 legs)

FE-4 control: **+₹127,351.50** (₹12,735.15/mo), win 59.5%, H1 +₹83,082.00 / H2 +₹44,269.50, ex-top-3 +₹100,528.50.

| Variant | Total | ₹/mo | Win % | Placebo d1 / d6 | Gate fails |
|---|---|---|---|---|---|
| FE-1 | +₹20,217.00 | 2,021.70 | 57.7 | −10,240.50 / −15,811.50 | total; ex-top3 legs; ex-top3 days; Jul, Aug flip red |
| FE-2 | −₹4,939.50 | −493.95 | 59.5 | −13,635.00 / −21,732.00 | total; halves; ex-top3 legs+days; Feb, Mar, Apr, Jun, Jul, Aug, Oct flip red |
| FE-3 | +₹36,844.50 | 3,684.45 | 49.5 | +10,995.00 / −13,221.00 | total; ex-top3 legs; ex-top3 days; Feb, Jul, Aug flip red |

**Hold-time proof (the "fast" property, demonstrated):**

| Book | Median bars | Mean | % entry bar | % ≤1 bar | % ≤2 bars | % ≤3 bars | Max |
|---|---|---|---|---|---|---|---|
| FE-4 | 7 | 12.37 | 3.6 | 12.6 | 20.7 | 28.8 | 62 |
| FE-1 | 2 | 1.38 | 21.6 | 40.5 | **100** | 100 | 2 |
| FE-2 | 1 | 0.89 | 45.0 | 65.8 | **100** | 100 | 2 |
| FE-3 | 3 | 2.27 | 3.6 | 26.1 | 43.2 | **100** | 3 |

The variants are genuinely fast — 100% resolved inside the spec window. The problem is what the speed costs: **the stack's money lives in bars 3 and beyond.** Under FE-4, 49 of 111 legs exit in the runner phase (35 runner_stop, 14 runner_target, 3 runner_square_off) and only 20.7% of legs resolve within 2 bars. Truncating at bar 2–3 keeps the stops (13–24 of them) and amputates the runner tails: FE-1 retains just **16%** of the incumbent's total, FE-3 (the best fast variant here) **29%**. FE-2 is outright negative despite hitting its +30 target 60 times — at lot 30, a +30 win nets +₹680 and a −40 stop nets −₹1,420 after the ₹220 cost, so target/stop legs alone need a >67% win rate to break even; it got 59.5%.

Month tables (₹): FE-4 all positive. FE-1 flips Jul (−3,916.50) and Aug (−1,816.50) red and cuts Oct from +19,889.50 to +367.00. FE-3 flips Feb (−3,928.00), Jul (−583.50), Aug (−2,668.50). Full tables in the results JSON.

## 4. Stream B — NS1 standalone (16 legs)

FE-4 control: **+₹10,269.50** (₹1,026.95/mo), win 56.2%, H1 +₹5,963.00 / H2 +₹4,306.50, ex-top-3 **−₹2,153.50** (concentrated — see §2).

| Variant | Total | ₹/mo | Win % | Placebo d1 / d6 | Gate fails |
|---|---|---|---|---|---|
| FE-1 | +₹4,772.00 | 477.20 | 68.8 | **+5,142.50** / −8,941.00 | total; **placebo not beaten** |
| FE-2 | +₹2,102.00 | 210.20 | 75.0 | **+5,606.00** / −10,373.50 | total; **placebo not beaten** |
| FE-3 | +₹8,855.00 | 885.50 | 62.5 | +6,309.50 / −9,874.00 | **total only** |

**Hold-time proof:** FE-4 median 6 bars (only 31.2% within 2 bars). FE-1 median 2, FE-2 median 1, FE-3 median 3 — all 100% within their spec windows.

The decisive fact on this stream: **the delay-1 placebos beat FE-1 and FE-2 outright.** Entering one bar *later* with the same fast exits earns more (+₹5,142.50 and +₹5,606.00) than entering at the signal bar — so the 2-bar in-and-out timing itself carries no edge on NS1 entries; what little the variants earn is drift capture, not the signal's first minutes. FE-3 is the near-miss: it keeps 86% of FE-4's total with a median hold of 3 bars vs 6, beats both placebos, improves ex-top-3 from −₹2,153.50 to +₹1,415.00, and fails the gate on the total leg alone. It is still not promotable — it fails the owner's test (§5) — and the gate bar is not moved.

## 5. Owner's acceptance test — November 2–10 counterfactual

**Stream A window legs (2):**

| Leg | FE-4 (recorded) | FE-1 | FE-2 | FE-3 |
|---|---|---|---|---|
| Nov 4 · PE 55800 · 09:55 @ 715.30 | runner_stop 10:25, **+2,480.00** (6 bars) | target, entry bar, +1,280.00 | target, entry bar, +680.00 | **be_stop, bar 2, −220.00** |
| Nov 9 · PE 58900 · 10:45 @ 815.40 | stop, entry bar, −1,720.00 | stop, entry bar, −1,720.00 | stop, entry bar, −1,420.00 | stop, entry bar, −1,720.00 |
| **Window net** | **+760.00 PASS** | **−440.00 FAIL** | **−740.00 FAIL** | **−1,940.00 FAIL** |

The Nov 4 leg is the whole story in one trade: the incumbent let it run 6 bars to +₹2,480; FE-1/FE-2 cashed it on the entry bar for half/quarter of that; FE-3's breakeven arm — the variant designed to protect exactly this kind of trade — stopped it at entry on bar 2 for −₹220, before the run. The Nov 9 leg stopped on its entry bar under every geometry; no exit rule saves it.

**Stream B window legs (2):**

| Leg | FE-4 (recorded) | FE-1 | FE-2 | FE-3 |
|---|---|---|---|---|
| Nov 3 · CE 55500 · 10:20 @ 867.60 | stop 11:10, −1,720.00 (10 bars) | time_stop bar 2 @ 896.50, **+647.00** | target bar 2, +680.00 | be_stop bar 3, −220.00 |
| Nov 4 · CE 55900 · 13:40 @ 757.00 | stop 14:00, −1,720.00 (4 bars) | time_stop bar 2 @ 735.60, −862.00 | stop bar 2, −1,420.00 | time_stop bar 3 @ 733.00, −940.00 |
| **Window net** | **−3,440.00 FAIL** | **−215.00 FAIL** | **−740.00 FAIL** | **−1,160.00 FAIL** |

FE-1 genuinely improves the NS1 window (it rescues Nov 3 from −₹1,720 to +₹647 by cutting at bar 2) — but Nov 4 still bleeds −₹862 and the window stays ₹215 under water. **Context, outside the test window:** over the full Nov 2–12, stream B FE-1 nets +₹2,345.00 vs FE-4's +₹1,520.00 (the Nov 11/12 winners hit +50 quickly) — but the owner's test is the Nov 2–10 window he named, and there it fails. Stream A full-period: FE-4 −₹960.00; FE-1 −₹2,160.00; FE-2 −₹2,160.00; FE-3 −₹3,660.00.

## 6. Why the fast shape fails here — stated plainly

1. **These streams are not fast books.** Their recorded winners resolve at a median of 6–7 bars and earn in the runner phase. Forcing 2–3 bar resolution doesn't speed up the same edge — it removes it (stream A keeps 16–29% of its total).
2. **On NS1, the first minutes carry no timing edge at all:** a one-bar-later placebo with identical fast exits beats FE-1 and FE-2. The owner's observed Nov 11/12 winners were real, but they were the two best draws of a stream whose Jan–Oct record is 16 legs, ₹1,027/month, ex-top-3 negative — and whose Nov 2–10 legs (the test window) lost under every geometry.
3. **The arithmetic of small fast targets is hostile at lot 30 with ₹220 cost:** +30/−40 geometry needs >67% win rate on target/stop legs to break even; neither stream delivers it.

**Nothing is promoted.** No December candidate arises from this programme. The incumbent stack remains the Bank book; NS1 remains a component of the books it already belongs to, not a standalone fast earner. If a fast Bank earner is to exist, this run says it will not come from re-exiting the stack or NS1 faster — it would need an entry stream whose edge is *in* the first bars, which neither of these is.

## 7. Files

- Script: `tuning_bank_fast_2026-11-12.py` (spec frozen in its header) · November helper: `tuning_bank_fast_2026-11-12_nov.py`
- Results: `tuning_bank_fast_2026-11-12_results.json` (batteries, month tables, hold distributions, placebos, gate fails, November rows)
- Trades: `tuning_bank_fast_2026-11-12_{a_stack,b_ns1}_{fe1,fe2,fe3,fe4}_trades.csv` (8 files, independently re-summed in-run)
