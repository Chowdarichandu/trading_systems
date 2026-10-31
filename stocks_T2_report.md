# Stocks EQUITY — LINE T2: EVENT-AXIS DEEPENING (P2F extensions) — REPORT

**Spec frozen before scoring: `stocks_T2_frozen.md`. Engine:
`stocks_T2.py`; results: `stocks_T2_results.json`; trades:
`stocks_T2_<cell>_trades.csv`.**
Equity cash, LONG/SHORT, paper only, real ₹0. All figures
provisional per 100 shares, ₹40/trade, Jan–Oct 2026
(October = 1–28 Oct). HOME 25 and POOLED 50 reported
separately throughout. T2-C is NON-INTRADAY (holds overnight)
and is labelled as such wherever it appears.

## Anchors + timing audit (controls first, same run as scoring)

**Anchors reproduce EXACTLY** (in-engine regeneration, HOME):
- P2F 2.0% R+1 T125: 48 trades, **+₹12,835.88**, H1 +₹3,498.10 /
  H2 +₹9,337.78, breadth 14/25 ✅
- P2F 2.5% R+1 T125: 39 trades, **+₹15,489.08**, expectancy
  **+₹397.16**, H1 +₹6,702.84 / H2 +₹8,786.24 ✅
- Cross-check vs Line 3 V2 published HOME bands: T2-A 3.0%
  home = 33 trades / +₹14,231.75 and 4.0% home = 22 trades /
  +₹8,399.06 — **identical to Line 3** ✅ (T2-A's new content
  is the pooled scoring + October slices.)

**Timing audit: CLEAN — 0 violations across all 420 trades in
all five cells.** Asserted programmatically over every trade:
entry date > reaction day R (qualifier = R's close, complete
15:30 on R), entry time = 09:15 on the stated entry day (R+1
for T2-A/T2-C, R+2 for T2-B), direction = sign of the rounded
reaction return, |reaction return| ≥ the cell threshold.

**Gate (frozen):** both halves > 0 AND October > 0 AND audit
clean, plus HOME cells only: expectancy ≥ +₹397.16.

## T2-A — Magnitude curve at R+1 (thresholds 3.0% / 4.0%)

| Cell | Universe | Trades | Win% | Net ₹ | Exp ₹ | H1 ₹ (n) | H2 ₹ (n) | Oct ₹ (n) | Breadth | Top-3 | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 3.0% | HOME | 33 | 48.5 | +14,231.75 | +431.27 | +6,720.88 (21) | +7,510.87 (12) | **−315.00 (2)** | 11/25 | 97.5% | ❌ FAIL — October |
| 3.0% | POOLED | 66 | 45.5 | **+31,719.61** | +480.60 | +17,391.09 (41) | +14,328.52 (25) | +2,547.21 (8) | 24/50 | 50.1% | ✅ **PASS** |
| 4.0% | HOME | 22 | 54.5 | +8,399.06 | +381.78 | +7,383.06 (15) | +1,016.00 (7) | **−132.00 (1)** | 10/25 | 112.8% | ❌ FAIL — October + expectancy |
| 4.0% | POOLED | 45 | 48.9 | **+17,374.45** | +386.10 | +13,779.22 (31) | +3,595.23 (14) | +4,356.38 (5) | 19/50 | 75.0% | ✅ **PASS** |

Direction split: the SHORT tilt persists but softens pooled.
3.0% pooled: LONG 27 trades +₹16,032.35 (exp +₹593.79) /
SHORT 39 +₹15,687.26 (+₹402.24) — both sides pay pooled,
unlike the base P2F. 4.0% pooled: LONG 19 +₹4,939.75 /
SHORT 26 +₹12,434.70. Home remains SHORT-carried (3.0% home
SHORT +₹13,181.45 of +₹14,231.75).

**Reading:** the magnitude curve is real but not monotone in
value — 3.0% pooled is the strongest cell in this line
(+₹31,719.61, expectancy +₹480.60, the highest expectancy
scored anywhere on the event axis, breadth 24/50, top-3 share
down to 50.1%). 4.0% pooled passes the frozen gate but is
strictly weaker (fewer trades, H2 thins to +₹3,595.23).
**Both HOME cells fail on October alone** — on samples of 2
and 1 trades (−₹315.00 / −₹132.00). The gate is the gate:
recorded as FAIL on home, PASS on pooled, no re-judging.

## T2-B — Second-day drift (entry R+2; thresholds 2.0% / 2.5%)

Drops: 1 HOME candidate at each band (no R+2 in data), 0 EXT.

| Cell | Universe | Trades | Win% | Net ₹ | Exp ₹ | H1 ₹ (n) | H2 ₹ (n) | Oct ₹ (n) | Breadth | Top-3 | Gate |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2.0% | HOME | 47 | 51.1 | +14,429.46 | +307.01 | +15,498.38 (28) | **−1,068.92 (19)** | +1,618.05 (3) | 14/25 | 72.0% | ❌ FAIL — H2 |
| 2.0% | POOLED | 98 | 48.0 | +37,932.01 | +387.06 | +39,821.76 (60) | **−1,889.75 (38)** | +5,039.22 (10) | 30/50 | 51.6% | ❌ FAIL — H2 |
| 2.5% | HOME | 38 | 50.0 | +9,813.68 | +258.25 | +12,288.08 (25) | **−2,474.40 (13)** | +189.99 (1) | 12/25 | 95.8% | ❌ FAIL — H2 |
| 2.5% | POOLED | 82 | 47.6 | +31,153.15 | +379.92 | +34,380.75 (53) | **−3,227.60 (29)** | +3,546.16 (7) | 28/50 | 62.9% | ❌ FAIL — H2 |

**Reading:** skipping R+1 does NOT find a second drift day.
The R+2 book is an H1 phenomenon: pooled H1 is enormous
(+₹39,821.76 at 2.0%) and H2 is negative at both bands on
both universes. Whatever post-reaction drift exists beyond
day 1 was a Jan–May regime property, not a stable behaviour.
**T2-B is dead at both bands — no candidate, no rescue
variant** (an H1-only reading would be hindsight regime
fitting). Direction note, diagnostic only: home R+2 money is
again SHORT-side (2.0% home SHORT +₹16,872.18 vs LONG
−₹2,442.72), while pooled LONGs pay via the EXT names
(MARUTI +₹9,543.75) — the halves verdict overrides all of it.

## T2-C — Two-day hold, stop-only (band 2.5%) — ⚠ NON-INTRADAY

Drops: 1 HOME candidate (no R+2 in data), 0 EXT.

| Universe | Trades | Win% | Net ₹ | Exp ₹ | H1 ₹ (n) | H2 ₹ (n) | Oct ₹ (n) | Breadth | Top-3 | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| HOME | 38 | 31.6 | +2,890.17 | +76.06 | **−2,106.83 (26)** | +4,997.00 (12) | **−132.00 (1)** | 9/25 | 346.5% | ❌ FAIL |
| POOLED | 82 | 26.8 | +17,663.42 | +215.41 | +18,124.53 (55) | **−461.11 (27)** | +3,862.98 (7) | 16/50 | 249.3% | ❌ FAIL — H2 |

**Reading:** removing the target destroys the P2F edge. Win
rate collapses to 26.8% pooled — the −0.5% stop amputates
most trades before the drift can pay, and the book survives
only on rare unstopped two-day runners (EICHERMOT alone
+₹24,962.50 pooled, i.e. the top-3 share of 249.3%: the
positive total is a tail artefact, offset by steady stop-outs,
and H2 is negative anyway). Post-earnings drift at this band
pays **because** of the small target, not despite it. **T2-C
is dead** — and as a NON-INTRADAY cell it was never adoptable
as an intraday system regardless.

## Verdicts

- **T2-A 3.0% POOLED: ✅ PASS** → frozen as the primary
  variant in `stocks_T2_candidate_spec.md` (December
  fresh-window judging). HOME: ❌ FAIL (October, 2 trades).
- **T2-A 4.0% POOLED: ✅ PASS** → co-frozen in the same
  candidate spec as the nested variant (4.0% population ⊂
  3.0% population — not an independent discovery). HOME:
  ❌ FAIL (October + expectancy).
- **T2-B (both bands, both universes): ❌ FAIL** — H2
  negative everywhere. Dead.
- **T2-C: ❌ FAIL** — both universes. Dead; NON-INTRADAY
  besides.

**Honesty notes.** (1) The pooled passes inherit a selection
history: the 3.0%/4.0% bands were already known to pass on
HOME in Line 3 (V2, pre-declared thresholds) — pooled scoring
is genuinely new evidence (EXT events were never in Line 3),
but the threshold choice was not made blind. (2) Both pooled
passes are ~2× the base P2F pooled scale yet remain small
money in absolute terms and rest on 66/45 trades over ten
months. (3) Nothing here touches November: the frozen P2F
shadow (2.0%, R+1, home) runs as frozen.
