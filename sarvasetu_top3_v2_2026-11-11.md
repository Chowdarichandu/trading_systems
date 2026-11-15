# SARVASETU TOP-3 v2 — FIXED RANKING + WIDER PROOF WINDOW (Oct 1 – Nov 11, 27 trading days) + pick-count variants A–F (scored 2026-11-11)

**This is a RETROSPECTIVE scoring of selection rules assembled on 11 Nov 2026 — not live forward evidence.**
Paper only, real money ₹0. Basis: **provisional per 100 shares**, ₹40/trade, square-off 15:10.
Owner delegation 2026-11-11 18:59 IST ("make it more profitable, it's up to you") + addendum 19:00 IST (variants D/E/F).
**Window: Thu 2026-10-01 → Wed 2026-11-11 — 27 trading days** (October's 20 scored days + November's 7; Oct 2, Oct 20, Nov 10 excluded by the candle data itself — market holidays). Seed day Wed 2026-09-30 seeds prior-day reactions/levels only.
**Universe: the full Sarvasetu universe — 1,081 liquid NSE names** (`wide_nse_universe_2026-11-11.csv`), applied backwards over the window (constituent drift over six weeks is possible in principle; index reviews are semi-annual and none fell inside the window — the caveat stands as stated). Bars: the Sarvasetu bar store (`screen_work/sarvasetu_bars_octnov`, Sep 30 → Nov 11); no fetching was needed and no 429 was encountered.

## What v2 fixes

v1's ranking mixed scales: INV components expose no trigger %, so v1 used their **pool percentile (0–100)** as magnitude, while the other components carried genuine % moves (F4 ≈ 0.5–1.0, reactions 2.5–10, N4 ≥ 1.0). The percentile term swamped everything — all 21 v1 picks came out INV-owned, and the total was one stock deep (ex-PTCIL −₹2,806.41).

**THE FIX (Step 2 of the brief, applied exactly):** every component's trigger magnitude is normalised to a **within-day, within-component percentile (0–100)** across that day's stock-day representatives of that component (one representative per stock-day per component = its earliest trade; position percentile, best = 100 — the same convention v1's INV pool percentile used). Conviction = **confluence** (distinct components flagging the stock-day) as the PRIMARY key, the owning component's normalised magnitude as SECONDARY (score = confluence × 100 + owner percentile). A stock-day is **owned** by its highest-normalised-magnitude component (ties: earliest entry, then component name); the trade scored is that component's own construction. Native magnitudes are the machinery's own signal fields, unchanged from v1 (N4-V3 = |09:30 move|; P2F/P2F-R2/R2-LOWBAND = |reaction-day %|; F4 = |first-move %|; INV-LONG/INV-ABOVE = the chain pool percentile — which is then itself re-percentiled within the component, like every other component).

## Pools (Step 1) — built, anchored, verified in this run

Same machinery as v1 (`stocks_sarvaritu_logger.build_book`, v2/C24 law, Sarvasetu merged event calendar), one code path over all 27 days (window lo = 2026-09-30):

- **Fidelity:** the independent detailed rebuild reproduces the production `build_book` output **exactly** — same trade multiset, same nets (**9,703 = 9,703 rows**) across all 27 days.
- **Anchor 1 (the brief's anchor):** the November subset of this combined pool reproduces v1's `sarvasetu_top3_november_2026-11-11_pool.csv` **exactly — 2,827 trades, identical keys including magnitudes**. Extending the window backwards did not move a single November trade.
- **Anchor 2:** restricting the pool to the frozen 25 watchlist names reproduces the frozen paper log **trade-for-trade: 26 trades · +₹8,391.28, zero differences**.
- **Combined pool: 9,703 trades · +₹1,495,964.66 · WR 40.0%** — October: 6,876 trades · +₹833,909.48 (WR 40.0%); November: 2,827 trades · +₹662,055.18 (WR 39.8%, identical to v1's pool). Pool ex-top-3: +₹1,112,948.76.

| Component | Window trades | Window net ₹ | Win % | October trades | October net ₹ | November trades | November net ₹ |
|---|---|---|---|---|---|---|---|
| F4 | 3,236 | +646,384.83 | 52.2 | 3,121 | +629,753.88 | 115 | +16,630.95 |
| INV-LONG | 4,116 | +361,328.17 | 31.9 | 3,710 | +212,713.51 | 406 | +148,614.66 |
| INV-ABOVE | 2,289 | +484,876.65 | 37.1 | 0 | 0.00 | 2,289 | +484,876.65 |
| N4-V3 | 24 | −1,978.86 | 54.2 | 17 | −7,762.31 | 7 | +5,783.45 |
| P2F | 18 | +1,372.38 | 33.3 | 13 | −2,617.39 | 5 | +3,989.77 |
| P2F-R2 | 15 | +3,140.28 | 33.3 | 12 | +328.73 | 3 | +2,811.55 |
| R2-LOWBAND | 5 | +841.21 | 60.0 | 3 | +1,493.06 | 2 | −651.85 |

**Three pool facts that shape everything downstream (all are the frozen construction's own behaviour, verified by the anchors — not gaps in this run):**
1. **The whole October window is DOWN-regime** under the book's label (Nifty prior close vs 50DMA); November runs DOWN (Nov 2) → FLAT (Nov 3–6) → UP (Nov 9, 11). October is a one-regime stress test, not a balanced month.
2. **INV-ABOVE never fires on a DOWN-regime day** under the frozen C22 law — zero trades on every October day *and* on Nov 2; all 2,289 of its trades fall on the six FLAT/UP November days. In October the "seven strategies" were effectively six.
3. **Chain warmup:** the bar store starts Sep 30, so the chain family's ADR inputs need sessions to accumulate — the chain pool is empty on Oct 1, 5, 6, 7 (Oct 1's pool is F4 only, 111 trades; INV-LONG first appears Oct 8). F4 and INV-LONG also fire far more per day in the DOWN tape (≈156 and ≈185 trades/day in October vs ≈16 and ≈58 in November).

## Variants (Step 3 + addendum) — same pools, same fixed ranking, 27 days

- **A** — top 3/day, no floor. **B** — top 3/day + conviction floor (owner percentile ≥ 90; never pad). **C** — B + price-risk cap (pick entry ≤ ₹5,000).
- **D** — top **6/day**, floor + cap. **E** — **split basket**: MORNING basket = top 3 among {N4-V3, P2F, P2F-R2, R2-LOWBAND, F4}; POOL basket = top 3 among {INV-LONG, INV-ABOVE}; confluence counted *within* each basket's component set; each basket floored (≥90) and capped (≤ ₹5,000) independently; a stock in both baskets counts once (morning owns it, pool basket walks to its next-ranked name); up to 6 trades/day. **F** — top **9/day**, floor + cap.

| Variant | Trades | Net ₹ | Win % | Expectancy ₹/tr | **Ex-top-3 ₹** | November (tr / net ₹ / WR%) | October (tr / net ₹ / WR%) | Best day | Worst day |
|---|---|---|---|---|---|---|---|---|---|
| A — top-3, no floor | 81 | +15,843.75 | 43.2 | +195.60 | **−7,273.62** | 21 / +21,451.76 / 42.9 | 60 / −5,608.01 / 43.3 | Nov 2 +16,944.55 | Oct 30 −5,420.78 |
| B — top-3 + floor | 81 | +22,514.40 | 45.7 | +277.96 | **−3,254.09** | 21 / +21,451.76 / 42.9 | 60 / +1,062.64 / 46.7 | Nov 2 +16,944.55 | Oct 30 −5,420.78 |
| C — top-3 + floor + cap | 81 | +10,407.31 | 45.7 | +128.49 | **−2,598.68** | 21 / +5,301.42 / 38.1 | 60 / +5,105.89 / 48.3 | Oct 13 +5,111.64 | Oct 30 −5,420.78 |
| **D — top-6 + floor + cap** | **162** | **+24,032.62** | **42.6** | **+148.35** | **+8,916.25** | 42 / +7,930.50 / 38.1 | 120 / +16,102.12 / 44.2 | Oct 16 +10,703.11 | Oct 30 −8,329.92 |
| E — split basket 3+3 | 139 | +7,149.24 | 39.6 | +51.43 | **−6,286.80** | 34 / +6,856.01 / 44.1 | 105 / +293.23 / 38.1 | Oct 26 +8,286.89 | Oct 29 −4,934.20 |
| F — top-9 + floor + cap | 243 | +15,198.03 | 40.7 | +62.54 | **−1,070.22** | 63 / +6,937.15 / 34.9 | 180 / +8,260.88 / 42.8 | Oct 16 +9,877.15 | Oct 30 −9,165.10 |

**Component mix of picks (picks · net ₹) — no variant is a one-component book; the v1 pathology is gone:**

| Variant | F4 | INV-LONG | INV-ABOVE | N4-V3 | P2F | P2F-R2 | R2-LOWBAND |
|---|---|---|---|---|---|---|---|
| A | 40 · −8,852.57 | 19 · +17,604.21 | 8 · −2,557.41 | 3 · +1,095.47 | 4 · +3,134.18 | 5 · +6,071.72 | 2 · −651.85 |
| B | 39 · −5,877.17 | 17 · +16,842.03 | 8 · −2,557.41 | 5 · +4,041.65 | 5 · +4,645.43 | 5 · +6,071.72 | 2 · −651.85 |
| C | 40 · −6,067.51 | 15 · +4,334.03 | 8 · −2,557.41 | 5 · +4,041.65 | 5 · +4,645.43 | 5 · +6,071.72 | 3 · −60.60 |
| **D** | **78 · +7,812.28** | **35 · +7,397.15** | **26 · −1,259.08** | **7 · +2,326.73** | **6 · +3,512.98** | **7 · +4,303.16** | **3 · −60.60** |
| E | 35 · +1,072.06 | 48 · −590.89 | 18 · −2,239.32 | 13 · +334.64 | 10 · +2,669.48 | 10 · +5,062.06 | 5 · +841.21 |
| F | 117 · +4,132.19 | 57 · +2,291.84 | 44 · −991.27 | 7 · +2,326.73 | 7 · +3,380.98 | 8 · +4,118.16 | 3 · −60.60 |

Residual F4 tilt, diagnosed honestly: (i) **genuine** — F4 was October's strongest pool component (+₹629,753.88 at 52.0% WR) and the F4+INV-LONG double-flag was the common confluence-2 pattern of the DOWN tape, usually F4-owned; (ii) **granularity** — percentile steps are 100/N, so small-population components (F4 ≈ 100–160 reps/day, the reaction family often < 10) resolve conviction coarsely and their top reps cluster at 96–100, while INV-ABOVE's ~600 reps/day resolve finely. The scales are now the same *kind* (percentile vs percentile); population size still sets the resolution. Also structural: every component's daily #1 representative scores exactly 100, so among confluence-1 stock-days the top of the list is effectively "each strategy's best idea of the day" (final order by symbol — deterministic and outcome-blind). At 6/day (D), that is close to literally the design: every strategy's best, floored and capped.

## Reading the variants

- **The fix works on its own terms.** With ranking alone repaired (A/B), November improves from v1's +₹13,153.59 to **+₹21,451.76 (+63%)** on the same 21 picks budget — because reaction/N4 components now own their stock-days: Nov 6's M&M via P2F (+₹3,959.87, replacing an INV pick worth +₹444.50), Nov 9's GLENMARK via P2F-R2 (+₹3,197.50 — the very trade the frozen live book won that day — instead of v1's INV-owned −₹1,369.00), Nov 11's KALYANKJIL via N4-V3 (+₹959.30) and TATASTEEL via P2F. Nov 2's three double-flagged picks are unchanged (PTCIL +₹15,960.00, INDOMIM +₹1,425.25, RATEGAIN −₹440.70). But over the full 27 days A still fails ex-top-3: it remains PTCIL-dependent.
- **The floor strictly helps (B vs A):** identical November, October swings −₹5,608.01 → +₹1,062.64; B beats A on all three judging metrics. The sub-90th-percentile tail was pure drag.
- **The cap is regime-dependent (C vs B):** it repairs October further (+₹1,062.64 → +₹5,105.89 — e.g. it removes Oct 23's GRWRHITECH, entry ₹6,824, −₹3,452.00, the single list's #3 that day) but amputates November (+₹21,451.76 → +₹5,301.42) because November's biggest winner, PTCIL at ₹24,255/share, is exactly what the cap exists to exclude. At 3/day the cap costs more than it saves; the wound it prevents is real but rarer than the winner it blocks.
- **D is the only variant that survives ex-top-3.** Six floored, capped picks a day diversify the single-name risk that sinks A–C: D's top-3 stocks (SHRIPISTON +₹6,579.20, GLAND +₹4,577.30, M&M +₹3,959.87) are 62.9% of its headline, yet removing them still leaves **+₹8,916.25**. D is positive in *both* sub-windows (October +₹16,102.12, November +₹7,930.50) — the only variant besides C and F positive in October, and the only one positive ex-top-3 anywhere.
- **F dilutes D back under water ex-top-3 (−₹1,070.22):** ranks 7–9 each day add expectancy of only ~₹63/trade overall and re-import the tail the floor was meant to cut. In this window, 6/day is the sweet spot; 9/day is too many.
- **E's split fails as mechanised** — and the failure is located precisely: its MORNING basket made **+₹9,979.45 over 73 picks** while its POOL basket **lost −₹2,830.21 over 66 picks**. Forcing three INV picks every day imports INV exposure on DOWN-tape days the single ranked list would never have chosen (INV-owned picks are E's two losing components: INV-LONG −₹590.89, INV-ABOVE −₹2,239.32). The pool basket also came up empty on five days (Oct 1/5/6/7 — chain warmup, no INV trades exist; Oct 23 — its only ≥90th-percentile INV-LONG name, GRWRHITECH, was price-capped and the next rep sat at 87.5), so E traded 139, not 162. The owner's session-split intuition is not refuted in principle — the morning basket was the profitable half — but as a *forced* 3+3 it underperforms the single list's freedom to allocate the day's six slots.
- **Every variant's worst day is Oct 30** (month-end DOWN tape): the selection layer cannot fix a day the whole pool bled; position-count (D/F) deepens that day's loss (−₹8,329.92 / −₹9,165.10) even as it wins the window.

## Fixed-capital lens (Step 4) — winner D restated at ₹25,000 per trade

Shares = floor(25,000 / entry), minimum 1 (no D pick entered above ₹25,000 — the ₹5,000 cap makes the 1-share case moot: **0 one-share trades**; 18,883 shares in total). Per-share gains are taken from the machinery's own unrounded exit levels — (net + ₹40) / 100 — so the lens preserves each trade's exact % outcome; ₹40/trade cost applied once per trade, as on the primary basis.

| Lens | Trades | Net ₹ | Win % | Expectancy ₹/tr | November net ₹ |
|---|---|---|---|---|---|
| D on per-100-shares basis (primary) | 162 | +24,032.62 | 42.6 | +148.35 | +7,930.50 |
| **D on ₹25,000/trade fixed-capital basis** | 162 | **+1,215.08** | 42.6 | **+7.50** | +188.13 |

**Read this before the headline:** at realistic ₹25k sizing, gross gains are ₹7,695.08 and the ₹40/trade cost consumes **84%** of them (on the per-100 basis the same trades deploy far more notional on mid-priced names, so cost is 21% of gross). The fixed-capital expectancy is **+₹7.50 per trade** — positive, but inside the noise of any cost/slippage assumption. The per-100-shares headline overstates real-money profitability on this design by roughly 20×. D is worth forward paper; on this evidence it is **not yet proven profitable in real-money terms**, and the live shadow spec below therefore tracks the lens basis alongside the primary basis from day one.

## VERDICT (pre-registered judging: ex-top-3 first, then expectancy, then win rate)

Judging order across all six: **D (+8,916.25) > F (−1,070.22) > C (−2,598.68) > B (−3,254.09) > E (−6,286.80) > A (−7,273.62)**.

**WINNER: Variant D — top 6/day, fixed ranking + conviction floor (≥90) + price-risk cap (entry ≤ ₹5,000).** It is the only variant with a positive ex-top-3 net across the 27 days, positive in both sub-windows, with all seven components owning picks. The top-3 idea is therefore **not** declared unproven — but the honest summary of the whole exercise is narrower than any headline: (1) repairing the ranking scale was worth +63% on November at 3/day; (2) at 3/day every variant is still one-stock deep over 27 days; (3) profitability, such as it is, appears at **6/day with the floor and the cap** — breadth *with* quality gates, not concentration; (4) in fixed-capital money the surviving edge is thin (+₹7.50/trade expectancy) and cost-dominated. D is armed below as a **shadow** — forward paper decides whether it is real.

## LIVE SHADOW SPEC — Sarvasetu Top-3 (variant D) — for arming from Thu 2026-11-12

*(Written by this run; NOT armed here. The parent wires it after the owner sees this verdict.)*

- **Name:** Sarvasetu Top-3 — LIVE SHADOW (variant D). Paper only, real money ₹0. Separate log, never merged into the frozen SarvaRitu book's numbers.
- **Universe:** the Sarvasetu 1,081-name liquid NSE list (`wide_nse_universe_2026-11-11.csv`), refreshed on the Sarvasetu shadow's own cadence; 5-minute bars from Upstox (browser User-Agent header mandatory; on HTTP 429 hard-stop the day and mark the day NOT_COMPUTED — never estimate).
- **Candidate pool (daily, EOD-scored):** every trade the November whole book would take that day across all seven components — F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND — via the book's own machinery (`stocks_sarvaritu_logger.build_book`, v2/C24 law, C22-form INV-ABOVE, merged machinery event calendar), with each trade's native trigger magnitude recorded (N4 = |09:30 move %|; P2F family = |reaction-day %|; F4 = |first-move %|; INV family = chain pool percentile).
- **Ranking (the fixed rule):** one representative per (stock, component) = that component's earliest trade on the stock that day. Normalise each component's representative magnitudes to a within-day, within-component percentile (position percentile, best = 100). Confluence = distinct components flagging the stock-day (primary key); owner = the component with the highest normalised percentile (ties: earliest entry, then component name); score = confluence × 100 + owner percentile. Rank stock-days by score desc, then stock symbol.
- **Selection (variant D):** from the ranked list take the first **6** stock-days satisfying BOTH: owner percentile **≥ 90** (conviction floor) and owner-trade entry price **≤ ₹5,000** (price-risk cap). Fewer than 6 qualifying → take what exists; **never pad**. One trade per stock-day, under the owning component's own entry/exit construction.
- **Scoring:** each pick scored exactly as its component runs it (frozen geometries; square-off 15:10), ₹40/trade. Report BOTH bases daily: (primary) provisional per 100 shares; (secondary) fixed-capital lens at ₹25,000/trade notional — shares = floor(25,000/entry), min 1 (entry > ₹25,000 → 1 share, flagged). Log every pick with date, rank, stock, owner component, confluence, flagging components, native magnitude + kind, normalised percentile, score, entry/exit times and prices, exit reason, net on both bases, regime.
- **Known behaviours to expect (not defects):** INV-ABOVE will produce no candidates on DOWN-regime days (frozen C22 law); the chain family needs its rolling bar history maintained (warmup); on confluence-thin days the six slots approximate "each strategy's floored, capped best idea".
- **Judging:** the shadow's forward record is judged on the lens basis and the per-100 basis separately, ex-top-3 first — the same standard as this proof. No promotion to any live book without the owner's explicit go after forward evidence.

## Coverage / NOT_COMPUTED

Usable bars (≥50 5-min bars) per scored day: October 98.2–99.4% of 1,081 (Oct 12 lowest: 1,062; Oct 29/30: 1,074); November 99.4–100% (Nov 11: 1,081/1,081). **Event-active (symbol, day) pairs in the window: 120 — NOT_COMPUTED: none.** Every name with a calendar event or reaction window had usable bars on its active days. All seven components were computed at full width on every day they can fire (INV-ABOVE's October absence and the Oct 1–7 chain warmup are construction properties documented above, not unscored items).

## Caveats

- Retrospective scoring of selection rules assembled 2026-11-11; the window is the proof, not forward evidence. The live record starts only when the shadow is armed (from Thu 2026-11-12 at the earliest).
- October is a single-regime (DOWN) month and its first four scored days have warmup-truncated chain pools (bar store begins Sep 30, 2026); regime diversity in this proof is limited (20 DOWN days, 5 FLAT, 2 UP). Variant D's win is established on *this* tape; a rising-market month is a different test the forward shadow will supply.
- Construction inheritances from the November book, unchanged: N4 admission is the machinery's |09:30 move| ≥ 1.0% (the adopted 0.8% figure belongs to the December-candidate axis); the adopted book's extra stack sleeves (GAP-FADE, NE-REV-NU, REXP, INV-R3) are outside the owner's seven and excluded.
- The per-100-shares basis is a provisional cash-translation unit, never a lot; rupee outcomes scale with share price by construction — the price cap and the fixed-capital lens exist precisely to keep that visible.
- No frozen book, log, producer, or index file was modified. This run wrote only its own pools, summary, trades CSV, build script/log and this report.

## Deliverables

- This report: `sarvasetu_top3_v2_2026-11-11.md`
- Winner (variant D) picks, all fields incl. both bases: `sarvasetu_top3_v2_2026-11-11_trades.csv` (162 rows)
- October pool: `sarvasetu_top3_october_2026-11-11_pool.csv` (6,876 rows) — alongside November's `sarvasetu_top3_november_2026-11-11_pool.csv` (2,827 rows, reproduced exactly)
- Combined 27-day pool: `sarvasetu_top3_v2_2026-11-11_pool.csv` (9,703 rows); full detail incl. every variant's picks: `sarvasetu_top3_v2_2026-11-11_summary.json`; runner: `sarvasetu_top3_v2_build.py`
