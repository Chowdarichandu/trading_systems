# Stock Engine — THE INVENTION: "SECOND-HALF GATE" (2026-11-12)

Owner order 2026-11-12 07:10 IST: *"at which time interval — first half or second half of the day — entry remains profitable… I don't want to lose this, that's the main motto… invent something which compensates us."* Paper only, real money ₹0. Basis: provisional per 100 shares, ₹40/trade; ₹25,000 fixed-capital lens on combined engines. Code: `stock_engine_secondhalf_2026-11-12.py`; summary: `stock_engine_secondhalf_2026-11-12_summary.json`; picks: `stock_engine_secondhalf_2026-11-12_picks_<S1|S2|PS1|PS2>.csv`. Stage 1 (the time-of-day map): `stock_engine_timeofday_2026-11-12.md`.

## Verdict first

**BOTH VARIANTS FAIL THE STAGE-1 SCREEN. Nothing is wired; Stock Engine stays 4-live; `stock_engine_live.py` and the cron are untouched.** Stage 2 (full controls gate) never ran — it is reserved for a screen passer, and there is none.

| Variant | Trades | Net ₹ | WR | Expectancy ₹ | Ex-top-3 ₹ | Lens ₹ | Screen |
|---|---|---|---|---|---|---|---|
| 4-live baseline (reference) | 39 | +8,724.39 | 43.6% | +223.70 | −3,256.65 | +634.72 | — |
| Failed gate, no windows (reference) | 162 | −4,267.84 | 34.6% | −26.34 | −18,321.31 | −4,811.70 | FAIL (2026-11-12 gate) |
| **S1 session windows** | 131 | **+11,673.55** | 37.4% | +89.11 | **−1,762.49** | −487.46 | **FAIL — 3 of 5 legs** |
| S1 placebo (random windows) | 46 | +3,256.06 | 43.5% | +70.78 | −7,962.61 | +211.40 | — |
| **S2 windows + still-valid** | 136 | +3,255.30 | 34.6% | +23.94 | **−10,828.62** | −3,395.33 | **FAIL — all 5 legs** |
| S2 placebo (random windows) | 136 | +5,411.65 | 32.4% | +39.79 | −8,776.32 | −4,981.24 | — |

## The design

The frozen `pool_pick` discarded early signals that the rest of the day invalidated — with hindsight. The causal substitute is **TIME + VALIDITY**: a causal chain component may only trade inside the session window(s) where its entries actually earn (Stage 1's map, pre-registered verdict rule), and (S2) a signal armed before its window must still be valid when the window opens.

**Windows** (the causal variant's OWN 2026 25-universe map; a component with no PROFITABLE bucket sits out): **F4-C → [10:30–12:00]** (its only profitable bucket; its B1 is top-3-carried, ex-top-3 −₹2,826.74) · **INV-LONG-C → [09:15–10:30]** (its only bucket, profitable) · **INV-ABOVE-C → none** (no profitable bucket anywhere — sits out S1/S2 entirely).

- **S1 SESSION WINDOWS:** a chain comp locks picks only if its representative's entry time falls inside one of its windows. Everything else is the failed-gate chassis verbatim (stream percentiles, floor ≥90, price cap ₹5,000, max 6/day, reaction family unchanged).
- **S2 = S1 + STILL-VALID CONFIRMATION:** if a chain rep's entry precedes its window's open W0, then at W0 validity is checked and, if valid, the trade is re-entered at the open of the first candle ≥ W0 with the comp's own TP/SP geometry replayed (F4-C 1.50/0.95, INV 1.25/0.5; net = gross − ₹40). If invalid: discarded, never re-armed. **Validity (uniform, from the construction's own levels):** the signal candle is the candle immediately preceding the candidate's original entry candle (both chain constructions enter at signal+1 open); invalidation level = signal candle LOW for a LONG, HIGH for a SHORT; price at window open = close of the last candle before W0; LONG valid iff price ≥ signal low, SHORT valid iff price ≤ signal high. INV-LONG-C's window opens 09:15 — nothing can be armed before it, so its S2 ≡ S1 by construction. Diagnostics over the 27 days: 2,191 deferred-valid (re-priced) reps, 918 deferred-invalid, 1,923 dead (no later window), 4,672 in-window.

## Harness validation (before any variant was scored)

(a) 4-live baseline via the production derive reproduced **exactly**: 39 tr · +₹8,724.39 · ex-top-3 −₹3,256.65. (b) The new S-derive with windows=None reproduced the failed-gate combined **exactly**: 162 tr · −₹4,267.84 · ex-top-3 −₹18,321.31. Both aborts armed; neither fired. The screen numbers below are therefore measured on a validated harness, same as the tuning programme's.

## Stage-1 screen (pre-registered; 27 days Oct 1 – Nov 11 2026, 1,081 names)

Bar: combined ex-top-3 > 0 **AND** > −₹3,256.65 (baseline) **AND** October ex-top-3 ≥ −₹6,897.97 **AND** November ex-top-3 ≥ −₹1,352.29 **AND** real windows beat same-width random windows (placebo) on combined ex-top-3.

### S1 — fails 3 legs, but the windows carry genuine signal

| Leg | S1 | Bar | Result |
|---|---|---|---|
| Combined ex-top-3 > 0 | −₹1,762.49 | > 0 | **FAIL** |
| Combined ex-top-3 beats baseline | −₹1,762.49 | > −₹3,256.65 | PASS |
| October ex-top-3 not worse | −₹7,734.08 (115 tr · +₹5,047.09) | ≥ −₹6,897.97 | **FAIL** (worse by ₹836.11) |
| November ex-top-3 not worse | −₹1,490.21 (16 tr · +₹6,626.46) | ≥ −₹1,352.29 | **FAIL** (worse by ₹137.92) |
| Beats placebo ex-top-3 | −₹1,762.49 vs PS1 −₹7,962.61 | > placebo | PASS (by ₹6,200.12) |

**Attribution:** the windows recovered most of the chain damage the failed gate diagnosed. Chain picks went from 123 · **−₹12,992.23** (failed gate) to 92 · **+₹2,949.16** (S1): F4-C inside its [10:30–12:00] window = 22 picks · **+₹3,853.40** (vs −₹10,010.06 ungated); INV-LONG-C inside [09:15–10:30] = 70 picks · −₹904.24 (vs +₹116.90 ungated — roughly flat, still a small drag); INV-ABOVE-C sat out (0 picks, vs −₹3,099.07 ungated). S1 is the **first 7-live configuration with a positive headline AND an ex-top-3 above the 4-live baseline**, and the placebo leg proves the windows are not curve-fit noise — random same-width windows lose ₹6,200 more. What still kills it: the book remains top-3-carried (CENTUM ₹4,760.00 + TCS ₹4,716.17 + M&M ₹3,959.87 = ₹13,436.04 > the ₹11,673.55 headline, hence the negative ex-top-3), and on the stricter per-month stock-level ex-top-3 both months stay worse than the 39-trade baseline. November's chain contribution was 5 picks netting −₹137.92 — the exact size of the November leg's failure. **Real signal, insufficient recovery. S1 is rejected as specified and is not to be retested identically.**

### S2 — the still-valid deferral is decisively rejected

S2 fails **every** leg, including the placebo leg — its own random-window placebo (ex-top-3 −₹8,776.32) **beat** S2 (−₹10,828.62). The deferral channel actively destroyed the value S1 had recovered: F4-C picks went from 22 · +₹3,853.40 (S1) to 27 · **−₹4,564.85** (S2), and October collapsed to 120 tr · −₹3,371.16 · ex-top-3 −₹17,455.08 (S1 October: +₹5,047.09). Re-entering armed signals at the window open, after a validity check against the signal candle's extreme, systematically selects worse entries than the in-window originals it displaces: by 10:30 the still-valid set is adversely selected (signals whose levels have not been tested are disproportionately the ones the market is about to run through, and the re-priced entries surrender the original entry's timing edge). November picks are identical to S1's (the deferral never bound there). **The TIME half of the invention carries signal; the VALIDITY half, in this form, is anti-information. S2 is rejected and is not to be retested identically.**

## Causality

Truncation spot-proof on 2026-10-16 and 2026-11-11 at slices 10:30 / 12:00 / 13:30 / 15:00, both variants: **16/16 checks PASS** — every pick with lock time before a slice is identical (identity, direction, entry) between the full-day run and the candle-truncated rebuild, and `lock_time ≤ entry_time` is asserted for every pick in code. Eligibility uses entry time only; validity uses candles strictly before the window open; deferred entries are the first candle ≥ the window open. The mechanisms are genuinely causal — what failed is their economics, not their timing.

## What this closes, and what it leaves open

Eight configurations for the causal three are now on record as failed: the raw gate, T1–T5, S1, S2. The through-line across all eight: the sleeves' standalone books are strong, but every streaming selection treatment either floods the 6/day cap with ordinary chain trades (gate, T1, T4, T5), rations without separating (T2), recovers only via near-end-of-day information (T3's 13:30 lock — still the closest miss, failing November by ₹320.81), or recovers partially via session timing (S1 — real, placebo-beating signal, but top-3-carried and worse than baseline in both months on the strict measure). S1's window effect is the second genuine partial recovery on record (after T3's late lock), and the two are related: both work by letting more of the day's information accumulate before chain trades are chosen. Any future attempt must differ mechanically from all eight — e.g. it would have to change what a chain *candidate* is intraday, not merely when or how it is ranked — and would need its own fresh gate. The frozen sleeves continue to earn where they are computable truthfully: the EOD-scored 25-book.

**Stage 2 (full controls gate + cross-check + wiring for Fri 2026-11-13) did not run — no variant passed the screen. Today's live wiring was never touched. Stock Engine opens and continues with the 4-live construction.**
