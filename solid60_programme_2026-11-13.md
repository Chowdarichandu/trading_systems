# SOLID-60 PROGRAMME — 2026-11-13

**Owner directive 2026-11-13 06:33 IST:** entries must be SOLID; book profit at the target, then TRAIL; win rate at least 60–70% — not 50-50. Bank Nifty first, then Nifty. Paper only, real money ₹0. December candidates only; frozen November books untouched. Full frozen spec (features, tier rule, exit geometries, gate, pass bars) is in the header of `solid60_programme_2026-11-13.py`, registered before any scoring. Bars were never moved; no waiver language anywhere in this report.

## VERDICT — NOTHING PASSES

**0 of 27 configurations** (3 streams × 3 tiers × 3 exits) meet the owner's bars (gate pass AND win rate ≥ 60% AND total > 0 AND total ≥ 60% of the stream incumbent).

| Index | Best WR line | Best money line | Any PASS? |
|---|---|---|---|
| Bank A (stack) | ALL·X-1 **59.5%** — gate-clean, fails the 60% bar by one leg | ALL·X-1 **+₹127,351.50** (the incumbent itself) | **No** |
| Bank B (NS1) | ALL·X-3 **68.8%** — passes both owner bars, fails the gate on the delay-1 placebo alone | ALL·X-1 **+₹10,269.50** (incumbent; gate-fails ex-top-3) | **No** |
| Nifty (TUNED v1) | ALL·X-2 54.1% | ALL·X-1 **+₹103,050.25** (incumbent; gate-clean, WR 51.4%) | **No** |

**Closest configuration (both registered selections agree): `bank_A_stack | ALL | X-1`** — the incumbent stack, ungated-filter-free: gate PASS (zero gate fails), +₹127,351.50, the most profitable configuration among WR ≥ 55% and the highest-WR gate-passing profitable configuration. It fails the owner's WR bar by **0.5 points: 66 wins of 111 legs (59.5%); 67 wins would be 60.4%.** One leg short — and the bar stays where the owner put it.

**Runner-up worth naming: `bank_B_ns1 | ALL | X-3`** (NS1 stream + the owner's ladder trail) is the ONLY configuration in the programme that clears both owner bars — WR **68.8%** (11/16) and total **+₹7,040.00** = 68.6% of its incumbent — but it **fails the gate on a single leg**: the delay-1 placebo (same legs, entry one bar later, same ladder) earns **+₹7,280.00**, ₹240 more. Entering later beats entering on time, so the ladder's timing carries no proven edge on this stream. Its ex-top-3 is +₹20.00 — razor thin on 16 legs.

## PART A — WHERE THE WINS ACTUALLY CONCENTRATE (under incumbent exits X-1)

The registered tier rule (SOLID = ≥2 of the four U1 systems agreeing at entry, entry ≤ 13:30) **does not find quality — on both indices, agreement points the wrong way:**

**Bank A — stack (111 legs, ALL WR 59.5%, +₹127,351.50)**

| Cut | Legs | WR | Total ₹ |
|---|---|---|---|
| agree 0 | 25 | **64.0%** | +27,432.50 |
| agree 1 | 56 | 60.7% | +71,375.50 |
| agree 2 (= SOLID core) | 22 | 54.5% | +25,101.50 |
| agree 3 | 8 | 50.0% | +3,442.00 |
| **SOLID tier (agree≥2, ≤13:30)** | 28 | 53.6% | +26,181.50 |
| **SOLIDS+ tier** | 8 | 50.0% | +1,840.00 |
| premium **< 500** | 32 | **75.0%** | **+69,749.50** |
| premium 500–750 | 32 | 43.8% | +7,087.00 |
| premium > 750 | 47 | 59.6% | +50,515.00 |
| family NS1_second | 13 | 61.5% | +16,149.50 |
| family S3-R1 | 9 | 66.7% | +9,720.00 |
| family BASE | 52 | 59.6% | +64,946.00 |
| CE / PE | 21 / 90 | 61.9% / 58.9% | +30,285.00 / +97,066.50 |
| entry late (>12:30) | 23 | 65.2% | +18,860.50 |

**Bank B — NS1 standalone (16 legs, ALL WR 56.2%, +₹10,269.50).** The SOLID tier is **empty — structurally**: every NS1 leg is a PE leg on a day where the sysmap records at most ONE system in that direction (agree: 11 legs = 1, 5 legs = 0; max agree in the stream is 1). NS1 fires precisely on single-system (Skill V3) days, so a ≥2-agreement tier can never contain it. Cuts: premium <500 → WR 80.0%, +₹12,283.00; premium >750 → WR 25.0%, **−₹5,360.00**; mid-day entries (10:31–12:30) WR 62.5%, +₹11,323.00 vs early entries WR 33.3%, −₹3,840.00.

**Nifty — TUNED v1 (74 legs, ALL WR 51.4%, +₹103,050.25)**

| Cut | Legs | WR | Total ₹ |
|---|---|---|---|
| agree 0 | 20 | **60.0%** | +27,125.00 |
| agree 1 | 23 | 47.8% | +31,921.75 |
| agree 2 | 22 | 45.5% | +20,887.00 |
| agree 3 | 9 | 55.6% | +23,116.50 |
| **SOLID tier** | 31 | 48.4% | +44,003.50 |
| **SOLIDS+ tier** | 29 | 48.3% | +40,390.75 |
| component B (CE-only in v1) | 26 | **61.5%** | +45,506.50 |
| component A | 35 | 51.4% | +54,102.00 |
| component C (expiry sleeve) | 13 | 30.8% | +3,441.75 |
| premium 150–300 | 28 | 60.7% | +50,529.75 |
| PE / CE | 33 / 41 | 57.6% / 46.3% | +70,444.25 / +32,606.00 |

**Reading of Part A (descriptive, not a gated result):** multi-system agreement is *anti*-correlated with win rate in these streams — the books earn on the first system's signal, and later agreement arrives after the move is underway. The strongest concentration in the whole programme is **entry premium**: Bank legs bought below 500 win 75% of the time and hold more than half the stack's profit; the 500–750 band is the stack's worst (43.8%). These cuts were NOT registered tiers; promoting any of them would require its own pre-registered programme (this workspace's history with premium bands — the frozen 400–550 drop filter — is exactly why band edges are not improvised here).

## PART B — FULL WR-vs-PROFIT TRADEOFF TABLE (Jan–Oct 2026, gated)

Gate = audits (admission / truncation-causality / fill — **clean on every simulated configuration**) + delay-1 placebo (X-2/X-3) + random-subset placebo p95 (subset tiers) + halves + month-flip + ex-top-3 ≥ 0 + independent re-sum (exact on all 27). Owner bars: WR ≥ 60%, total > 0, total ≥ 60% of incumbent.

| Config | Legs | WR | Total ₹ | % of inc. | Gate | Owner bars | Verdict |
|---|---|---|---|---|---|---|---|
| bank_A ALL·X-1 | 111 | 59.5% | +127,351.50 | 100.0% | **PASS** | WR ✗ | FAIL — WR 0.5pt short |
| bank_A ALL·X-2 | 111 | 54.1% | +76,726.50 | 60.2% | fail (3 month flips) | WR ✗ | FAIL |
| bank_A ALL·X-3 | 111 | 52.3% | +44,352.00 | 34.8% | fail (Aug flip) | WR ✗, total ✗ | FAIL |
| bank_A SOLID·X-1 | 28 | 53.6% | +26,181.50 | 20.6% | fail (placebo, halves, 4 flips) | ✗✗ | FAIL |
| bank_A SOLID·X-2 | 28 | 50.0% | +22,517.00 | 17.7% | fail (placebo, halves, ex3, 6 flips) | ✗✗ | FAIL |
| bank_A SOLID·X-3 | 28 | 32.1% | −2,920.00 | −2.3% | fail | ✗✗ | FAIL |
| bank_A SOLIDS+·X-1 | 8 | 50.0% | +1,840.00 | 1.4% | fail (placebo, halves, ex3, flips) | ✗✗ | FAIL |
| bank_A SOLIDS+·X-2 | 8 | 50.0% | +490.00 | 0.4% | fail | ✗✗ | FAIL |
| bank_A SOLIDS+·X-3 | 8 | 25.0% | −2,900.00 | −2.3% | fail | ✗✗ | FAIL |
| bank_B ALL·X-1 | 16 | 56.2% | +10,269.50 | 100.0% | fail (ex-top-3 −2,153.50) | WR ✗ | FAIL |
| bank_B ALL·X-2 | 16 | 50.0% | +1,028.00 | 10.0% | fail (delay-1, halves, ex3) | ✗✗ | FAIL |
| bank_B ALL·X-3 | 16 | **68.8%** | +7,040.00 | 68.6% | fail (**delay-1 only**: 7,280) | **✓✓** | FAIL — gate only |
| bank_B SOLID / SOLIDS+ (all exits) | 0 | — | 0.00 | — | fail (tier empty) | — | FAIL — no such legs exist |
| nifty ALL·X-1 | 74 | 51.4% | +103,050.25 | 100.0% | **PASS** | WR ✗ | FAIL — WR |
| nifty ALL·X-2 | 74 | 54.1% | +93,774.75 | 91.0% | fail (delay-1 by ₹302.90, Jun flip) | WR ✗ | FAIL |
| nifty ALL·X-3 | 74 | 36.5% | +33,474.25 | 32.5% | fail (delay-1, halves, flips) | ✗✗ | FAIL |
| nifty SOLID·X-1 | 31 | 48.4% | +44,003.50 | 42.7% | fail (placebo, 3 flips) | ✗✗ | FAIL |
| nifty SOLID·X-2 | 31 | 54.8% | +36,112.50 | 35.0% | fail (placebo, 4 flips) | ✗✗ | FAIL |
| nifty SOLID·X-3 | 31 | 29.0% | +19,059.75 | 18.5% | fail (all legs) | ✗✗ | FAIL |
| nifty SOLIDS+·X-1 | 29 | 48.3% | +40,390.75 | 39.2% | fail (placebo, 3 flips) | ✗✗ | FAIL |
| nifty SOLIDS+·X-2 | 29 | 55.2% | +32,015.50 | 31.1% | fail (delay-1, placebo, flips) | ✗✗ | FAIL |
| nifty SOLIDS+·X-3 | 29 | 27.6% | +14,355.00 | 13.9% | fail (all legs) | ✗✗ | FAIL |

**What the trails did:** X-2 (book +90 → lock +50, +25 steps) keeps 91% of Nifty's money and lifts its WR 51.4→54.1, but keeps only 60.2% of Bank A's and flips three of its months red. X-3 (the owner's ladder: +30 BE, +58→+30, +82→+58, +100 tight trail) **strangles runner-based streams** — Bank A falls to 34.8% of incumbent with WR 52.3%, Nifty to 32.5% with WR 36.5% — because rung stops at entry/+30 are hit by ordinary pullbacks before the runner phase that pays these books. The same ladder is the *only* geometry that lifts NS1 above 60% WR (68.8%; all 16 exits are stop/lock_stop, median hold 3 bars): the ladder suits already-confirmed continuation legs, and its failure there is the placebo's, not the owner's bars.

## NOVEMBER LENS (Nov 2–12, recorded incumbent = X-1; cannot promote)

November's sysmaps are Skill-V3-only on every leg day, so **no November leg in any stream reaches agree ≥ 2 — the SOLID and SOLIDS+ tiers are empty in November too.**

| Stream | Config | Legs | WR | Net ₹ |
|---|---|---|---|---|
| Bank A | ALL·X-1 | 3 | 33.3% | −960.00 |
| Bank A | ALL·X-2 | 3 | 33.3% | −2,160.00 |
| Bank A | ALL·X-3 | 3 | 33.3% | −2,760.00 |
| Bank B (NS1) | ALL·X-1 | 4 | 50.0% | **+1,520.00** |
| Bank B (NS1) | ALL·X-2 | 4 | 50.0% | −130.00 |
| Bank B (NS1) | ALL·X-3 | 4 | 50.0% | +1,280.00 |
| Nifty v1 | ALL·X-1 | 1 | 100% | +3,036.50 |
| Nifty v1 | ALL·X-2 | 1 | 100% | +3,036.50 |
| Nifty v1 | ALL·X-3 | 1 | 0% | −220.00 |

Both trail geometries make Bank's November worse than the recorded exits; on the NS1 legs the ladder (X-3) preserves most of the win (+1,280 of +1,520) while X-2 gives it back (−130).

## ANCHORS & AUDITS

- Bank A rebuilt leg-for-leg vs the frozen EVE-19 record (111 legs, +₹127,351.50, all months positive) before scoring; Bank B's recorded pipeline exits reproduced (16 legs, +₹10,269.50); Nifty v1 anchor +₹103,050.25 asserted three ways (harness score_r6, recorded CSV leg-keys identical, premium-loader cross-validation 74/74).
- Admission / truncation-causality / fill audits: **zero violations** on all simulated configurations; every trades CSV independently re-summed exact.
- November anchors asserted: Bank A −₹960.00, Bank B +₹1,520.00, Nifty v1 +₹3,036.50 (the Nov 3 component-C CE leg).
- Honest absences: `room_ratio` is not a stored field on the Jan–Oct streams (November-legacy-only) — it was not reconstructed or estimated. The X-1 delay-1 placebo is not applicable (recorded geometry cannot be re-based); the random-subset placebo binds for X-1 subset tiers, per the registered spec.

## FILES

- Computation: `solid60_programme_2026-11-13.py` → `solid60_programme_2026-11-13_results.json`, run log `solid60_programme_2026-11-13_run.log`
- Trades: `solid60_programme_2026-11-13_<stream>_<tier>_<exit>_trades.csv` (27 files)
- Part A leg-level features: `solid60_programme_2026-11-13_<stream>_features.csv` (3 files)
