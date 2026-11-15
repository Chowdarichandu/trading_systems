# Stock Engine — LIVE construction (2026-11-11)

Owner order 2026-11-11 19:48 IST: *"it should not run aftermarket, it should run during market and it should work like Bank Nifty."* The EOD-finalised Variant D design (selection after the close by `sarvasetu_top3_eod_scorer.py`) is **superseded before its first live day**. From Thu 2026-11-12, Stock Engine runs during market hours: signals are evaluated on 5-minute candle closes, picks **lock** at fixed intraday decision points and are announced as they lock, exits are announced on the exit candle, and the after-close step is accounting only. Paper only, real money ₹0.

Bases: provisional per 100 shares, ₹40/trade (primary); ₹25,000/trade fixed-capital lens (secondary). Stock Engine is a shadow beside the frozen 25-stock SarvaRitu book — its numbers are never added to the book's floor figures, and never pooled with Bank Nifty / Nifty.

## 1. Construction spec

Universe: 1,081 names (`wide_nse_universe_2026-11-11.csv`). Selection economics are Variant D's, unchanged: representative = the component's trade for the stock-day; magnitude = the component's native trigger size; within-component percentile ranking; owner = strongest component; score = confluence × 100 + owner percentile; lock while slots remain with owner percentile ≥ 90, entry ≤ ₹5,000, max 6 picks/day, each stock once/day, never pad; a locked pick is final and is traded under its owning component's own frozen entry/exit construction.

**Decision points: 09:10 and 09:35** — derived from when each component's signal actually becomes determinable (below), not chosen arbitrarily. At each decision point only candidates fully determined by then are ranked; confluence counts only components determined by then; a candidate not locked at its own batch's decision point is dead (its entry bar has passed).

### Per-component determinable times

| Component | Signal determined | Entry | Decision point | Live? |
|---|---|---|---|---|
| P2F | Pre-open: reaction-day close vs prior close (lag 1) + event calendar | Trade-day 09:15 open | 09:10 | ✅ |
| P2F-R2 | Pre-open: same reaction, lag 2 | 09:15 open | 09:10 | ✅ |
| R2-LOWBAND | Pre-open: same reaction, lag 2, 2.0–2.5% band | 09:15 open | 09:10 | ✅ |
| N4-V3 | 09:35: 09:25-bar close vs prior close, \|move\| ≥ 1.0% (event-day names only) | 09:30-bar close | 09:35 | ✅ |
| F4 | **Not determinable intraday** (see below) | — | — | ❌ NOT_LIVE |
| INV-LONG | **Not determinable intraday** | — | — | ❌ NOT_LIVE |
| INV-ABOVE | **Not determinable intraday** | — | — | ❌ NOT_LIVE |

For the four live components the percentile population is **complete before entry** (the day's full reaction set is known pre-open; the day's full N4 qualifier set is known at 09:35), so their live percentiles are exactly the retrospective ones — there is no so-far approximation anywhere in the live construction.

### NOT_LIVE — F4, INV-LONG, INV-ABOVE (excluded, never approximated)

Their trades are produced by the frozen chain machinery (`run_chain` / `build2`), whose signal choice is `pool_pick`: it compares **both** detector heads' first signals and takes the higher RANK (setup4 > setup3 > setup2 > skill), with the v4 head's windows running to **14:30**. A trade's identity is therefore not fixed at its entry time.

Worked example, BERGEPAINT 2026-10-16: the skor head signals LONG at 10:15 (would-be entry 10:20), but the construction does **not** take it — a setup3 v4 signal completing at 10:35 outranks it, and the chain's actual round-1 trade is SHORT at 10:40. Whether an early signal becomes a trade depends on candles up to 14:30; later rounds chain off that outcome. The detectors themselves are prefix-streaming; the non-causality sits in `pool_pick`'s cross-time rank comparison, which is the frozen construction's own logic and may not be rewritten. (A v4-headed round-1 trade happens to be determinable at its signal close, but skor-headed rounds and the round sequence are not — a component cannot be faithfully halved, so all three are excluded whole.)

Empirical proof — Timing Audit A2 (machinery rebuilt on candle-truncated days; candidate identities compared with the full build):

| Day | Slice | Chain rows checked | Chain mismatches | F4 first trades checked | F4 mismatches |
|---|---|---|---|---|---|
| 2026-10-16 | 10:30 | 949 | 125 | 112 | 21 |
| 2026-10-16 | 13:30 | 1,694 | 27 | 138 | 9 |
| 2026-10-30 | 10:30 | 1,313 | 30 | 234 | 8 |
| 2026-10-30 | 13:30 | 2,063 | 6 | 242 | 2 |
| 2026-11-11 | 10:30 | 1,169 | 63 | 0 (not a below-50 day) | — |
| 2026-11-11 | 13:30 | 2,134 | 19 | 0 | — |

## 2. Timing audits on the live construction

- **A1 (in-code assertions, pass):** every locked pick's lock_time ≤ its entry_time; every ranking input used at a decision point has determination time ≤ that point.
- **A2:** above — the NOT_LIVE evidence.
- **A3 (pass):** all 24 N4 pool rows in the window re-derived from bars ≤ 09:30 only (09:25 move for signal/direction/magnitude, 09:30 close for entry) — 24/24 exact. The reaction family uses no intraday data at all, determinable pre-open by construction.
- **Fidelity anchor:** the simulation's candidate pool comes from the same `build_book_detailed` code path whose 25-stock restriction reproduces the frozen paper log trade-for-trade (asserted in the run).

## 3. Simulation — LIVE construction, 27 trading days (Thu 2026-10-01 → Wed 2026-11-11)

Decision-point-by-decision-point replay on stored bars (`stock_engine_live_sim.py`; picks in `stock_engine_live_2026-11-11_trades.csv`). This is a retrospective simulation of the live rules, not live evidence.

| Window | Trades | Net (per 100) | Win rate | Expectancy | Ex-top-3 | Lens net (₹25k) | Lens expectancy |
|---|---|---|---|---|---|---|---|
| **27 days** | **39** | **+₹8,724.39** | 43.6% | +₹223.70 | **−₹3,256.65** | +₹634.72 | +₹16.27 |
| October | 28 | +₹1,960.01 | 46.4% | +₹70.00 | −₹6,897.97 | +₹779.06 | +₹27.82 |
| November (7 days) | 11 | +₹6,764.38 | 36.4% | +₹614.94 | −₹1,352.29 | −₹144.34 | −₹13.12 |

Top-3 trades (all window): TCS +₹4,716.17, M&M +₹3,959.87, DRREDDY +₹3,305.00.

Per-component pick mix: P2F-R2 10 picks · +₹5,062.06 | P2F 11 · +₹2,486.48 | R2-LOWBAND 5 · +₹841.21 | N4-V3 13 · +₹334.64.

**Honest read:** the headline is positive on the per-100 basis and (just) on the lens for the full window, but it is **concentration-driven** — ex-top-3 is negative in both months, and November's lens is slightly negative (−₹144.34). At November's pace (+₹6,764 over 7 trading days) it does not meet the ₹15,000/month stocks-segment floor either. This construction earns a forward paper run — which the owner has ordered — not a "profitable" label.

### November per-day picks (live construction)

| Date | Lock | Pick | Net |
|---|---|---|---|
| Nov 2 | 09:35 | NTPC · N4-V3 LONG @325.30 | −₹300.24 |
| Nov 3 | 09:10 | GODREJCP · R2-LOWBAND SHORT @823.70 | −₹451.85 |
| Nov 4 | 09:10 | NATIONALUM · P2F SHORT @317.55 | −₹198.77 |
| Nov 4 | 09:10 | NTPC · R2-LOWBAND LONG @320.00 | −₹200.00 |
| Nov 5 | 09:10 | NATIONALUM · P2F-R2 SHORT @328.80 | −₹204.40 |
| Nov 5 | 09:35 | NHPC · N4-V3 | −₹105.03 |
| Nov 6 | 09:10 | M&M · P2F | **+₹3,959.87** |
| Nov 9 | 09:10 | GLENMARK · P2F-R2 | **+₹3,197.50** |
| Nov 9 | 09:35 | TATASTEEL · N4-V3 | +₹241.20 |
| Nov 11 | 09:10 | TATASTEEL · P2F SHORT @186.40 | −₹133.20 |
| Nov 11 | 09:35 | KALYANKJIL · N4-V3 LONG @666.20 | **+₹959.30** |

## 4. Honest comparison vs Variant D (EOD selection)

| | Variant D (EOD, retired) | Stock Engine LIVE |
|---|---|---|
| Trades (27d) | 162 | 39 |
| Net (per 100) | +₹24,032.62 | +₹8,724.39 |
| Ex-top-3 | **+₹8,916.25** | −₹3,256.65 |
| Win rate / expectancy | 42.6% / +₹148.35 | 43.6% / +₹223.70 |
| November | 42 tr · +₹7,930.50 | 11 tr · +₹6,764.38 |
| Lens (27d) | +₹1,215.08 | +₹634.72 |

D's headline advantage came substantially from the three sleeves (F4/INV) whose picks are only knowable after the close — on Nov 11, four of D's six picks were INV trades. The live construction keeps a comparable November headline with a quarter of the trades and much higher per-trade expectancy, but loses D's ex-top-3 robustness: with only 39 trades, three big winners carry the window. That is the real price of causality, stated plainly.

*Discarded exploratory pass (for the record):* an earlier same-evening run locked all seven components using so-far-determined percentiles (162 trades · +₹6,907.85 · ex-top-3 −₹7,145.62). It was discarded when Audit A2 showed the INV/F4 trades themselves are not intraday-determinable at any percentile convention — the picks would have announced positions the construction had not yet decided to take.

## 5. Dry-run — 2026-11-11 through the live engine path

Replayed via `stock_engine_live.py --replay 2026-11-11` (the production script, simulation derivation over the stored pool):

**Live locks:** 09:10 — TATASTEEL · P2F · SHORT @186.40 → stop 09:20 @187.33, **−₹133.20** · 09:35 — KALYANKJIL · N4-V3 · LONG @666.20 → target 09:45 @676.19, **+₹959.30**. Day **+₹826.10** per-100 (lens +₹164.85).

**Variant D's EOD six for the same day:** AAVAS INV-ABOVE −₹610.25 · KALYANKJIL N4-V3 +₹959.30 · TATASTEEL P2F −₹133.20 · ACI INV-ABOVE −₹253.90 · HOMEFIRST INV-ABOVE −₹586.45 · CMSINFO INV-ABOVE −₹150.26 — day −₹774.76 (lens −₹483.77).

Same day, opposite sign: the two picks both constructions share net +₹826.10; D's four additional INV picks (unknowable intraday) cost it −₹1,600.86. Differences are structural, not a mismatch to be forced away.

## 6. Wiring for Thu 2026-11-12

- **Engine:** `stock_engine_live.py`. Each tick it refreshes the universe daily store + runtime calendar (via the wide producer's library functions), restores the frozen book Evaluator's state, fetches (actives every tick; one full-universe scan at the first tick ≥ 09:32), steps the Evaluator on completed bars, records representatives from its ENTRY actions, evaluates the 09:10 decision point once every reaction candidate has been stepped (fallback 09:45) and the 09:35 point once the scan has delivered the 09:30 bar (fallback 10:15), announces locks as `STOCK_ENGINE_LIVE_PICK` and locked picks' exits as `STOCK_ENGINE_EXIT`, and ledgers exits to `stock_engine_live_log.csv`. State: `stock_engine_live_state.json`. Detection is the frozen Evaluator's own — the selection layer only designates which of its positions are official picks.
- **Cron `stocks-wide-nse-shadow`** — updated in place (same id, 5-minute interval, delivery, owner `goal:stocks-intraday-systems`, timeout 1200s); title now "Stock Engine — live picks during market hours (Nov 2026)". Phase 1 (09:15–15:35) runs the live tick and posts picks/exits; Phase 2 (15:40–17:30) runs `stock_engine_live.py --summary` and posts ONE "STOCK ENGINE — DAY SUMMARY" — accounting only, it selects nothing. The job no longer calls `sarvasetu_top3_eod_scorer.py` or the producer script.
- **Retired:** `sarvasetu_top3_eod_scorer.py` from selection duty (file left in place; its official ledger `sarvasetu_top3_shadow_log.csv` was never created). The earlier 7-component greedy sim and the machinery-root draft engine were superseded by the final construction above.
- **Live-path nuances (on record):** (i) a lock is announced on the first cron tick after its decision point's data completes — the decision instants (09:10/09:35) are what is recorded as lock_time; (ii) if a reaction candidate's bars never arrive on a live day, no representative exists for it and the percentile population is the candidates that did enter (the retrospective population could differ in that rare case); (iii) owner ties on exact percentile equality break by the Evaluator's candidate order (reaction books before N4), matching the retrospective pool order; (iv) in the 27-day simulation no pick was owned by an earlier batch than its lock batch (checked: 0 cases).
- **Guard:** November 2026, Mon–Fri, in both the job body and the script. December continuation needs a guard amendment — it will not roll over silently.

Files: `stock_engine_live.py` (engine) · `stock_engine_live_sim.py` (simulation + audits) · `stock_engine_live_2026-11-11_trades.csv` (39 simulated picks) · `stock_engine_live_2026-11-11_summary.json` (aggregates + audit detail) · `stock_engine_live_log.csv` / `stock_engine_live_state.json` (live ledger/state, created on the first live tick).
