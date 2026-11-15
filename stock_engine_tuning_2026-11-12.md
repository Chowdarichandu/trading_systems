# Stock Engine — causal-three TUNING PROGRAMME (2026-11-12)

Owner order 2026-11-12 06:52 IST: "Can you tune them to make profitable?" — a chained tuning programme for the causal chain components (F4-C / INV-LONG-C / INV-ABOVE-C) inside Stock Engine, against the diagnosed failure mechanisms of the morning's gate (`stock_engine_causal3_2026-11-12.md`). Paper only, real money ₹0. Basis: provisional per 100 shares, ₹40/trade; ₹25,000 fixed-capital lens on combined engines.

## VERDICT — NO VARIANT PASSES STAGE 1. NOTHING IS WIRED. Stock Engine stays 4-live.

All five mechanically-distinct variants were screened on the same 27-day wide window (Oct 1 – Nov 11 2026, 1,081 names). None clears the pre-registered screen bar (combined ex-top-3 > 0 AND better than the 4-live baseline's −₹3,256.65 AND neither month worse than the baseline's same-month ex-top-3: Oct ≥ −₹6,897.97, Nov ≥ −₹1,352.29). Per the two-stage protocol, Stage 2 (full gate) does not run for any variant, and nothing is armed for Fri 2026-11-13. `stock_engine_live.py` and cron `stocks-wide-nse-shadow` are byte-untouched (mtimes Nov 11 14:42 / 14:38 verified).

**T3 (late lock 13:30 + 97th-percentile chain floor) is the near-miss**: it passes three of the four screen legs — combined ex-top-3 **+₹1,609.13** (the only variant positive, and better than the baseline), October not worse (−₹5,879.89 vs −₹6,897.97) — and fails only the November leg: Nov ex-top-3 **−₹1,673.10** vs the baseline's −₹1,352.29, worse by **₹320.81**. The bar is pre-registered and was not moved. T3 is a rejected variant: it is not retested identically, and no T3-derived tweak was run in this programme.

## Harness validation (before any variant was scored)

Pools rebuilt through the causal3 gate's own builders (identical code path). (a) 4-live baseline via the production `derive_day`: **39 tr · +₹8,724.39 · ex-top-3 −₹3,256.65 — reproduced exactly**. (b) The failed gate configuration (stream percentiles, price cap, floor 90) via the tuned derive: **162 tr · −₹4,267.84 · ex-top-3 −₹18,321.31 — reproduced exactly**. In every variant below, the reaction family's picks are unchanged (39 picks · +₹8,724.39) — the chassis held; only chain slots moved.

## Stage-1 table — all five variants (27 days, 1,081 names)

| Variant | Trades | Net ₹ | WR | Expectancy ₹ | Ex-top-3 ₹ | Oct ex-top-3 ₹ | Nov ex-top-3 ₹ | Lens ₹ | Screen |
|---|---|---|---|---|---|---|---|---|---|
| 4-live baseline | 39 | +8,724.39 | 43.6% | +223.70 | −3,256.65 | −6,897.97 | −1,352.29 | +634.72 | — |
| Failed gate config | 162 | −4,267.84 | 34.6% | −26.34 | −18,321.31 | −21,848.70 | −6,289.60 | −4,811.70 | — |
| **T1** absolute-strength ranking | 162 | **−20,913.42** | 27.8% | −129.10 | **−32,894.46** | −31,783.97 | −10,711.54 | −9,440.92 | FAIL (all legs) |
| **T2** slot reservation (chain ≤2/day, 13:30) | 93 | +3,023.65 | 44.1% | +32.51 | −8,957.39 | −14,228.64 | −1,879.38 | +421.16 | FAIL |
| **T3** late lock 13:30 + floor ≥97 | 159 | **+14,315.27** | 42.8% | +90.03 | **+1,609.13** | −5,879.89 | **−1,673.10** | −1,243.69 | FAIL (Nov leg only, by ₹320.81) |
| **T4** risk-based cap ₹1,500/100sh | 162 | +439.21 | 34.0% | +2.71 | −11,541.83 | −14,790.62 | −4,829.70 | −5,334.14 | FAIL |
| **T5** INV-LONG-C confirmation | 162 | −4,541.53 | 36.4% | −28.03 | −18,595.00 | −25,829.73 | −2,582.26 | −3,284.56 | FAIL |

Month nets (for the record): T1 Oct −₹19,185.50 / Nov −₹1,727.92 · T2 Oct −₹3,873.97 / Nov +₹6,897.62 (25 Nov trades) · T3 Oct +₹6,171.38 (118 tr) / Nov +₹8,143.89 (41 tr) · T4 Oct −₹4,548.08 / Nov +₹4,987.29 · T5 Oct −₹11,776.26 / Nov +₹7,234.73.

Chain pick attribution (picks · net ₹):

| Variant | F4-C | INV-LONG-C | INV-ABOVE-C | Chain total |
|---|---|---|---|---|
| Failed gate | 29 · −10,010.06 | 68 · +116.90 | 26 · −3,099.07 | 123 · −12,992.23 |
| T1 | 33 · −10,177.65 | 64 · −11,096.20 | 26 · −8,363.96 | 123 · −29,637.81 |
| T2 | 32 · −9,973.37 | 10 · +5,774.96 | 12 · −1,502.33 | 54 · −5,700.74 |
| T3 | 67 · **+1,311.97** | 28 · **+5,065.52** | 25 · −786.61 | 120 · +5,590.88 |
| T4 | 29 · −6,582.35 | 68 · −63.66 | 26 · −1,639.17 | 123 · −8,285.18 |
| T5 | 37 · −9,250.84 | 60 · −916.01 | 26 · −3,099.07 | 123 · −13,265.92 |

## Per-variant diagnosis (against M1 flood / M2 price-cap / M3 INV-LONG-C marginal trades)

**T1 — absolute-strength ranking: FAIL, worst of the queue.** Floors derived as specified (90th percentile of each frozen twin's taken trades, same window): F4-C 0.931% (the twin's |premove| distribution is capped by F4's own band_hi = 1.0 — median 0.712, max 0.999, so the "top-decile" floor sits at the construction's band edge); INV-LONG-C 4.257% displacement (median 1.572, max 15.338); INV-ABOVE-C 4.994% (median 2.116, max 17.956). Displacement = |signal-candle close / prior close − 1|×100. Result: win rate collapsed to 27.8% and every leg worsened vs the failed gate. **Diagnosis: M1 was never a percentile artefact.** Ranking by absolute displacement systematically prefers the most extended, already-overrun moves — the biggest signal-candle displacements are the worst entries. Absolute strength is anti-information for these detectors; the percentile form was not the problem.

**T2 — slot reservation: FAIL.** Capping chain slots at 2/day and moving chain selection to 13:30 cut the damage (chain total −₹5,700.74 on exactly 54 picks — the cap bound every day; combined net positive +₹3,023.65; November net +₹6,897.62) and INV-LONG-C's reserved picks flipped positive (10 picks · +₹5,774.96 — rationing works for that comp). But **F4-C took 32 of the 54 reserved slots and lost −₹9,973.37** — inside the reserved pool, F4-C's 13:30 so-far percentiles still flood (M1 survives inside the reservation), and October ex-top-3 (−₹14,228.64) stayed far worse than the baseline's. Reservation alone cannot fix a comp whose picks are negative at every rationing level tried so far.

**T3 — late lock + 97th-percentile floor: FAIL on one leg, by ₹320.81.** The one treatment that changes the picture: ranking chain candidates at 13:30 against the complete morning pool with a ≥97 floor turned F4-C's picks positive for the first time (67 picks · +₹1,311.97, vs −₹10,010.06 in the failed gate) and kept INV-LONG-C's positive (28 · +₹5,065.52); combined net +₹14,315.27 is the best of any 7-live configuration tested, and combined ex-top-3 +₹1,609.13 is the only positive. It fails the screen solely on November ex-top-3 (−₹1,673.10 vs −₹1,352.29 allowed). Read honestly: the sleeves' intraday edge, where it exists, lives in the extreme tail of the day's completed pool ranked late — i.e. it needs most of the day's information to separate — which is precisely the end-of-day ranking property the causal conversion gave up, partially recovered by a 13:30 lock. Partially is not enough under the pre-registered bar, and November (the forward-evidence month) is the leg it fails.

**T4 — risk-based cap: FAIL.** Stated arithmetic held: for %-stop constructions the ₹1,500/100-shares risk cap is a tighter effective price cap (INV comps: stop = entry×0.5%/share → risk = entry×0.5 → entry ≤ ₹3,000; F4-C: SP 0.95% → entry ≤ ₹1,578.95). It cannot admit the >₹5,000 strength zone at all — no %-stop trade on a ₹10,000 name can carry ≤₹1,500 risk per 100 shares. It did cut the worst damage (combined net −₹4,267.84 → +₹439.21; F4-C picks −₹6,582.35 vs −₹10,010.06) but the pick count stayed 162 — **M2 was never the binding constraint; M1 (the flood) is untouched by any cap on price/risk.** Ex-top-3 −₹11,541.83.

**T5 — INV-LONG-C confirmation: FAIL.** Confirmation set: of 5,618 INV-LONG-C book rows, 792 (14.1%) are confirmed — 316 by another component's same-direction rep, 500 by the second detector head at the same round (fidelity-asserted against the causal chain). But at pick level the requirement barely binds: INV-LONG-C picks fell only 68 → 60 and their net moved +₹116.90 → −₹916.01 (noise), while F4-C's picks (untouched by T5, per spec) worsened to 37 · −₹9,250.84 through slot refills. **Diagnosis: M3's marginal early-signal trades are not, in the main, unconfirmed** — the second head / another component usually agrees, because the detectors fire on the same level events. Confirmation is not the separating variable.

## Bottom line

Five mechanically distinct treatments — ranking by absolute strength, slot rationing, late lock with a near-maximal floor, risk-based capping, and cross-confirmation — and none makes the combined engine clear a screen whose hardest leg is merely "positive ex-top-3 with neither month worse than a 39-trade baseline." The pattern across T1–T5 is consistent with the gate's original reading: **under streaming selection economics (6 slots/day, per-100 basis, these caps), the causal sleeves' edge is inseparable from the end-of-day rank information the frozen constructions use** — T3 shows a 13:30 lock recovers much of the headline, but the recovery is top-3-dependent and fails exactly on the forward month. The causal variants remain scored, named, unarmed components. Any future attempt must differ mechanically from all six configurations now on record (failed gate + T1–T5) and pass the same two-stage protocol.

**Arming: NONE.** Stock Engine trades the 4-live construction today (2026-11-12, untouched) and tomorrow (2026-11-13). No dry-run replays were performed — there is no winner to replay.

Files: `stock_engine_tuning_2026-11-12.py` (Stage-1 screen: pool rebuild, harness validation, T1–T5) · `stock_engine_tuning_2026-11-12_summary.json` · `stock_engine_tuning_2026-11-12_picks_<T1..T5>.csv` (per-variant combined picks).
