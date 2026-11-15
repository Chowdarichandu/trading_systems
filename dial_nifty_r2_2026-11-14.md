# DIAL — NIFTY · ROUND 2: THE R-PE SEED · gate run 2026-11-14

Spec: `dial_nifty_r2_SPEC.md` (frozen before scoring). Numbers:
`dial_nifty_r2_results.json` · seed trades: `dial_nifty_r2_trades.csv` ·
build: `dial_nifty_r2_build.py` (Round 1's own code path, copied verbatim —
that is what makes the control below a control).
Standalone seed test — the put-buying side of DIAL-R alone, frozen fresh.
Buying only (puts), 1 lot (65), paper only, real money ₹0. Nifty segment only.
Nothing that runs was changed.

## The seed
Round 1's DIAL-R split by side: LONG-reversion (buy CE at RSI ≤ 30) lost
−₹70,179.00 while SHORT-reversion (buy PE at RSI ≥ 70 AND %B ≥ 0.95 AND EMA50
slope < +0.1%) made +₹32,513.50. Round 1 recorded that as a hypothesis seed,
not a finding. This run takes ONLY the SHORT-reversion signals from Round 1's
computed set — identical signal definition, contract selection, fill
convention, exits (stop −50 / target +90 / square-off 15:20) and cost (₹220).
First-R-signal-of-the-day logic unchanged: a day whose first R signal was LONG
contributes no seed trade.

## Control — Round 1 reproduced exactly (before any gating)
| Line | Published (R1) | Regenerated (R2) | Match |
|---|---|---|---|
| Combined | 205 · −₹89,487.20 | 205 · −₹89,487.20 | ✓ |
| DIAL-T | 112 · −₹51,821.70 | 112 · −₹51,821.70 | ✓ |
| DIAL-R | 93 · −₹37,665.50 | 93 · −₹37,665.50 | ✓ |
| R-CE (long side) | 47 · −₹70,179.00 | 47 · −₹70,179.00 | ✓ |
| **R-PE (the seed)** | **46 · +₹32,513.50 · 22 wins · WR 47.8%** | **46 · +₹32,513.50 · 22 wins · WR 47.8%** | ✓ |

The seed's Jan–Oct signal census: 84 SHORT-reversion signals generated,
**46 scored, 38 NC** — every NC is `nc_no_file` (the exact nearest-strike
weekly contract-day was never stored; no substitution, per spec). The scored
book is what the gate judges; the NC count stands next to every total, as in
Round 1.

## Seed results (Jan–Oct 2026)
| Line | Trades | Total | WR | ₹/trade-day | Pace/mo | Red months |
|---|---|---|---|---|---|---|
| **R-PE seed** | **46** | **+₹32,513.50** | **47.8%** | **706.82** | **3,251.35** | **3** |

Month table (₹ · trades): Jan +3,203.25 (2) · Feb +3,296.25 (4) ·
Mar −1,310.00 (3) · Apr +5,188.75 (5) · May +16,963.50 (5) · Jun −7,300.00 (6) ·
Jul −8,519.00 (9) · Aug +6,182.00 (7) · Sep +7,018.75 (2) · Oct +7,790.00 (3).
Halves: H1 (Jan–May) **+₹27,341.75** · H2 (Jun–Oct) **+₹5,171.75** — both
positive, but May alone is ₹16,963.50 = 52% of the year's total on 5 trades,
and Jun+Jul together are −₹15,819.00.
Ex-top-3: **+₹15,623.50** (the top 3 are all clean +₹5,630 target fills).
Exit mix: 14 targets, 9 stops, 23 square-offs at 15:20 — the book rarely hits
either level; half its trades ride to the close, which is how a sub-50% WR
still nets positive: the +90 targets and favourable square-offs outweigh the
few full −₹3,470 stops.

## Gate (frozen bar) — FAIL on 6 of 8 legs
1. Random-entry placebo ≥ 95th pct → **93.9th pct** (1,000 iterations over the
   PE-only scorable universe, 1,065 contract-day files; placebo mean −₹82.61,
   p95 +₹35,876.96). The seed beats ~94% of random put-buying books — and the
   frozen bar is 95. It misses, narrowly, on the bar as written.
2. Beat +30-min shift placebo → **NO**: shifted entries total **+₹34,264.90**
   (45 trades, 1 dropped) vs the seed's +₹32,513.50. Entering the same puts 30
   minutes later earns ₹1,751.40 MORE. The RSI/%B-extreme moment itself carries
   no timing value — this is the leg that kills the seed as a *signal*.
3. Halves positive → **YES** (both, above).
4. Ex-top-3 positive → **YES** (+₹15,623.50).
5. ₹/trade-day ≥ 900 → **NO** (706.82).
6. WR ≥ 60% → **NO** (47.8%).
7. Monthly pace ≥ ₹7,500 → **NO** (3,251.35).
8. Red months ≤ 2 → **NO** (3 — Mar, Jun, Jul).
Timing audit: PASSED — every scored seed trade's entry bar is exactly signal
bar + 5 min with entry premium equal to the stored bar open.

## November counterfactual (Nov 2–13, descriptive)
The full seed set is 3 signals; 2 are NC (no stored contract), 1 scored:
| Date | Signal | Contract | Status | Net |
|---|---|---|---|---|
| Nov 3 | 13:15 | PE 23700 (exp 11-03) | NC — no file | — |
| Nov 4 | 09:15 | PE 23850 (exp 11-09), in 09:20 @193.05 | scored — stop @143.05 | **−₹3,470.00** |
| Nov 6 | 09:45 | PE 24650 (exp 11-09) | NC — no file | — |
November seed net (scored): **−₹3,470.00** — the one trade the store lets us
see is a full stop, the same loss Round 1 reported for this leg.

## Verdict
**FAIL — 6 of 8 legs. The seed is dead, and per the terms frozen before this
run, DIAL-Nifty closes.** The honest texture, so the record is not flattened:
the +₹32,513.50 is not pure noise — it sits at the 94th percentile of random
put-buying, keeps both halves positive and survives ex-top-3, which the usual
mirage does not. But it is not a tradeable asymmetry either: it cannot clear
the owner's bars on win rate (47.8%), earnings per trade-day (₹707), pace
(₹3,251/mo) or red months (3), it misses the placebo bar as written, and the
shift test shows the money — whatever of it is real — lives in *which days and
strikes* the store happened to hold, not in the overbought-extreme moment:
the same puts bought 30 minutes later earn more. A side carved out of a book
that failed every leg in Round 1 needed to be decisively better than its
parent to be believed; it is only mildly better than random and worse than
its own echo. DIAL-Nifty is not adopted, not armed, and nothing that runs
was changed.
