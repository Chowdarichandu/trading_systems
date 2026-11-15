# SARVASETU TOP-3 CONVICTION — whole book × 1,081 stocks × NOVEMBER 2026, top-3 picks only (scored 2026-11-11)

**This is a RETROSPECTIVE scoring of a selection rule designed on 11 Nov 2026 (owner design order 2026-11-11 17:56 IST) — not live forward evidence.**
Paper only, real money ₹0. Basis: **provisional per 100 shares**, ₹40/trade, square-off 15:10.
**Window: the seven November trading days — Mon 2026-11-02, Tue 03, Wed 04, Thu 05, Fri 06, Mon 09, Wed 11** (Tue 10 = Diwali-Balipratipada holiday). October data (from Sep 30) seeds prior-day reactions/levels only.
**Universe: the full Sarvasetu universe — 1,081 liquid NSE names** (`wide_nse_universe_2026-11-11.csv`: Nifty 500 constituents + extension tier passing the ₹6 cr traded-value screen), applied backwards over seven trading days (constituent drift over one week is negligible; the caveat stands as stated). **No fetching was needed**: the Sarvasetu bar store (`screen_work/sarvasetu_bars_octnov`) already held bars for all 1,081 names, Sep 30 → Nov 11 — the run covers the true full universe, not a subset.

## Method — exactly the owner's rule, mechanically applied

**Step 1 — candidate pool.** Every trade the frozen November whole book would take across all **seven** SarvaRitu components (F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND) at full 1,081 width — the book's own machinery (`stocks_sarvaritu_logger.build_book`, v2/C24 law), parameterised only by universe, data root (built from the Sarvasetu bar store; NIFTY copied from the live logger's own root so the regime series is identical) and event calendar (the Sarvasetu merged machinery calendar). Same construction as the whole-book × 200 run.

**Step 2 — conviction ranking (the rule, verbatim in substance).** For each stock-day in the pool:

> conviction score = (number of DISTINCT components flagging that stock that day) × 100 + trigger magnitude %

Trigger magnitude % is the % move that qualified the trade under its owning component, taken from the machinery's own signal fields:
- **N4-V3** = |09:30 move| — the construction's own signal measure: the 09:25-bar close vs prior close, in % (the `move_pct` inside `n4_raw`, re-derived from the same inputs);
- **P2F / P2F-R2 / R2-LOWBAND** = |reaction-day % move| (`reaction_ret_pct` of the candidate);
- **F4** = |first-move %| (`premove_pct`, the move to the 10:00 measure);
- **INV-LONG / INV-ABOVE** = the chain machinery exposes **no % magnitude**, so the prescribed fallback is used and stated here plainly: the trade's **pool rank inverted to a percentile** within that day's chain pool (population: round ≤ 2, entry < 10:30, ADR ≥ 3.0 — the identical filter both INV constructions draw from; pool sizes 575–963/day), pool ordered by the machinery's own preference (setup RANK desc, earlier entry, symbol, round); percentile = 100 × (N − rank + 1) / N, best rank → 100.

Each stock-day is **owned** by its highest-magnitude component (magnitude ties broken by component name, deterministically); the trade scored is that component's **earliest** trade on that stock that day. Stock-days are ranked by score desc, tie-break magnitude desc, then symbol. **Top 3 per day**; fewer than 3 qualifying → take what exists, never pad. (Every November day had 131–505 qualifying stock-days, so all seven days filled their 3 picks — 21 trades.)

**Step 3 — scoring.** Each pick is scored exactly as the book runs it (that component's entry/exit/cost).

## Verification (run in the same session)
- **Fidelity:** an independent detailed rebuild (retaining entry/exit prices, reasons and magnitudes) reproduces the production `build_book` output **exactly** — same trade multiset, same nets (2,827 = 2,827 rows) on all seven days.
- **Anchor:** restricting this run to the frozen 25 watchlist names reproduces the frozen paper log **trade-for-trade: 26 trades · +₹8,391.28, zero differences in either direction** — at full 1,081 width, the machinery, calendar, bars and regime labels behave identically to the live book on its own names.
- The machinery also builds 25 lag-window rows dated Oct 26–30 (epoch seeding, reaction lags from the Oct 26 epoch) — excluded from every November figure here, exactly as in the 200-wide run.

## The picks — all seven days, all three picks

| Date (regime) | # | Stock | Owner | Conf. | Components flagging | Trigger % | Entry → Exit | Result ₹ |
|---|---|---|---|---|---|---|---|---|---|
| Nov 2 (DOWN) | 1 | PTCIL | INV-LONG | 2 | F4 + INV-LONG | 99.85 (pctile) | 09:35 24,255.00 → 15:10 24,415.00 (square-off) | **+15,960.00** |
| Nov 2 | 2 | INDOMIM | INV-LONG | 2 | F4 + INV-LONG | 99.41 (pctile) | 09:40 1,172.20 → 10:15 1,186.85 (target) | **+1,425.25** |
| Nov 2 | 3 | RATEGAIN | INV-LONG | 2 | F4 + INV-LONG | 98.96 (pctile) | 09:40 801.40 → 11:35 797.39 (stop) | −440.70 |
| Nov 3 (FLAT) | 1 | GOODLUCK | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:35 515.45 → 10:00 521.89 (target) | +604.31 |
| Nov 3 | 2 | MENONBE | INV-ABOVE | 1 | INV-ABOVE | 99.84 (pctile) | 09:40 317.50 → 09:40 315.91 (stop) | −198.75 |
| Nov 3 | 3 | QPOWER | INV-ABOVE | 1 | INV-ABOVE | 99.69 (pctile) | 09:40 1,457.80 → 12:55 1,450.51 (stop) | −768.90 |
| Nov 4 (FLAT) | 1 | AAVAS | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:35 1,129.70 → 11:00 1,124.05 (stop) | −604.85 |
| Nov 4 | 2 | ACMESOLAR | INV-ABOVE | 1 | INV-ABOVE | 99.90 (pctile) | 09:35 419.25 → 09:40 417.15 (stop) | −249.62 |
| Nov 4 | 3 | AEGISVOPAK | INV-ABOVE | 1 | INV-ABOVE | 99.79 (pctile) | 09:35 235.00 → 09:50 237.94 (target) | +253.75 |
| Nov 5 (FLAT) | 1 | MATRIMONY | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:40 559.00 → 10:15 565.99 (target) | +658.75 |
| Nov 5 | 2 | GSPCROP | INV-ABOVE | 1 | INV-ABOVE | 99.84 (pctile) | 10:10 445.05 → 10:25 442.82 (stop) | −262.53 |
| Nov 5 | 3 | ABFRL | INV-ABOVE | 1 | INV-ABOVE | 94.41 (pctile) | 09:35 42.07 → 10:45 41.86 (stop) | −61.03 |
| Nov 6 (FLAT) | 1 | ALEMBICLTD | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:35 98.46 → 09:45 99.69 (target) | +83.08 |
| Nov 6 | 2 | CANTABIL | INV-ABOVE | 1 | INV-ABOVE | 99.83 (pctile) | 09:35 261.70 → 09:40 260.39 (stop) | −170.85 |
| Nov 6 | 3 | EMAMILTD | INV-ABOVE | 1 | INV-ABOVE | 99.67 (pctile) | 09:35 387.60 → 10:00 392.44 (target) | +444.50 |
| Nov 9 (UP) | 1 | GLENMARK | INV-ABOVE | 2 | INV-ABOVE + P2F-R2 | 85.57 (pctile) | 09:35 2,658.00 → 09:35 2,644.71 (stop) | −1,369.00 |
| Nov 9 | 2 | RADICO | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:35 4,557.70 → 09:55 4,534.91 (stop) | −2,318.85 |
| Nov 9 | 3 | UNOMINDA | INV-ABOVE | 1 | INV-ABOVE | 99.83 (pctile) | 09:35 1,327.70 → 10:15 1,344.30 (target) | +1,619.63 |
| Nov 11 (UP) | 1 | AAVAS | INV-ABOVE | 1 | INV-ABOVE | 100.00 (pctile) | 09:35 1,140.50 → 09:40 1,134.80 (stop) | −610.25 |
| Nov 11 | 2 | ACI | INV-ABOVE | 1 | INV-ABOVE | 99.86 (pctile) | 09:35 427.80 → 14:10 425.66 (stop) | −253.90 |
| Nov 11 | 3 | HOMEFIRST | INV-ABOVE | 1 | INV-ABOVE | 99.72 (pctile) | 09:55 1,092.90 → 10:05 1,087.44 (stop) | −586.45 |

**Per-day pick subtotals:** Nov 2 **+16,944.55** · Nov 3 −363.34 · Nov 4 −600.72 · Nov 5 +335.19 · Nov 6 +356.73 · Nov 9 −2,068.22 · Nov 11 −1,450.60.

## Headline — TOP-3 book: 21 trades · net +₹13,153.59 · win rate 38.1%
**Read the two structural notes before the headline:**
1. **One day and one stock carry it.** Nov 2 alone is +₹16,944.55 — the other six days net −₹3,790.96 combined — and the single PTCIL pick (+₹15,960.00, a ₹24,255/share name held to square-off) is 121% of the total. Ex-PTCIL, the top-3 book is −₹2,806.41 over 20 trades. Same per-100-shares price-scaling concentration as every wide run today, now compressed into 21 trades.
2. **All 21 picks are INV-owned — a mechanical consequence of the prescribed magnitude scales, not a discovery.** The INV fallback magnitude runs 0–100 (percentile), while genuine % magnitudes run small (F4 first moves ≈ 0.5–1.0 in these picks, reactions 2.5–~10, N4 ≥ 1.0). Whenever confluence ties — and 17 of the 21 picks are confluence-1 — the INV percentile term wins ownership and the top of the ranking. Confluence did bind where it existed: Nov 2's three picks are the day's F4 + INV-LONG double-flags (scores ≈ 299), and Nov 9's #1 is the INV-ABOVE + P2F-R2 double-flag (285.57). Within INV, the percentile ordering follows the machinery's own preference (setup rank, then earliest entry), so on confluence-1 days the rule effectively selects the day's earliest, highest-setup-rank chain trades. Their outcomes were ordinary (8 winners of 21) — the percentile ranks *pool preference*, and pool preference did not predict outcome in this window.

## What the top-3 filter adds or removes — the unfiltered full-width book (Step-1 pool)
**All 7 components × 1,081 names, no filter: 2,827 trades · net +₹662,055.18 · win rate 39.8% · ex-top-3 +₹404,938.43** (top-3 pool stocks: POWERINDIA +₹105,992.50, FORCEMOT +₹99,088.00, PTCIL +₹52,036.25 — 38.8% of the pool total; the pool is far less concentrated than the 200-wide run because the same price-scaling now spreads over 2,827 trades).

| Component | Trades | Net ₹ | Win % |
|---|---|---|---|
| F4 | 115 | +16,630.95 | 59.1 |
| INV-LONG | 406 | +148,614.66 | 49.3 |
| INV-ABOVE | 2,289 | +484,876.65 | 37.1 |
| N4-V3 | 7 | +5,783.45 | 57.1 |
| P2F | 5 | +3,989.77 | 60.0 |
| P2F-R2 | 3 | +2,811.55 | 33.3 |
| R2-LOWBAND | 2 | −651.85 | 0.0 |
| **Pool total** | **2,827** | **+662,055.18** | **39.8** |

Pool per-day: Nov 2 +164,945.37 (522 tr) · Nov 3 −39,010.12 (359) · Nov 4 +389,056.62 (753) · Nov 5 +13,797.68 (354) · Nov 6 +26,046.13 (210) · Nov 9 +17,788.57 (195) · Nov 11 +89,430.93 (434).

**The filter's arithmetic:** the top-3 rule keeps 21 of 2,827 trades (0.7%) and +₹13,153.59 of the pool's +₹662,055.18 (2.0%). In this window the pool's money was in breadth — thousands of small INV-ABOVE/INV-LONG trades — and a 3-per-day cap structurally cannot hold breadth. What the filter *does* produce is a positive 21-trade book with the month's single best conviction day (Nov 2) fully captured; what it removes is everything else, including the pool's two biggest days (Nov 4 +₹389k across 753 trades → the filter's Nov 4 picks net −₹600.72).

## Comparisons — same November days, separate books, NEVER added together
| Book | Trades | Net ₹ (provisional per 100 shares) |
|---|---|---|
| **Top-3 conviction (this run) — 1,081 names × 7 comps, 3/day** | **21** | **+13,153.59** (ex-PTCIL pick: −2,806.41) |
| Unfiltered whole book — 1,081 × 7 (this run's pool) | 2,827 | +662,055.18 (ex-top-3: +404,938.43) |
| Whole book — 200 × 7 (earlier run) | 329 | +180,269.75 (ex-top-3: +10,900.13) |
| Sarvasetu — 1,081 × 4 intraday comps | 25 | +4,604.01 |
| Frozen SarvaRitu — 25 × 7 (its own paper log, re-verified by this run's anchor) | 26 | +8,391.28 |

On a per-trade basis the top-3 book (+₹626/trade) sits between the 25-book (+₹323/trade) and the 200-wide book (+₹548/trade), and far above the unfiltered pool (+₹234/trade) — the filter does select above-average trades on average; it simply holds too few of them, and its total is one stock deep.

## Coverage / NOT_COMPUTED
Usable bars (≥50 5-min bars) per scored day: Nov 2: 1075/1081 (99.4%) · Nov 3: 1077 (99.6%) · Nov 4: 1079 (99.8%) · Nov 5: 1080 (99.9%) · Nov 6: 1080 (99.9%) · Nov 9: 1080 (99.9%) · Nov 11: 1081 (100%). **Event-active names in a NOT_COMPUTED state: none** — every name with a November calendar event or reaction window had usable bars on its active days. All seven components were computed at full width; none is NOT_COMPUTED.

## Caveats
- Retrospective scoring of a selection rule assembled 2026-11-11; not live forward evidence. No frozen book, log, producer, or index file was modified; this run wrote only its own root (`data/wide1081_nov/`), pool/picks CSVs, summary JSON and this report.
- Construction inheritances from the November book, named in the 200-wide report and unchanged here: N4 admission is the machinery's |09:30 move| ≥ 1.0% (the adopted 0.8% figure belongs to the December-candidate axis); INV-ABOVE runs the Cycle-22 form; the adopted book's extra stack sleeves (GAP-FADE, NE-REV-NU, REXP, INV-R3) are outside the owner's seven and excluded.
- The INV percentile fallback is the task-prescribed treatment for a component with no % magnitude; its scale consequence (note 2 above) is a property of the rule as specified, reported — not silently normalised away.
- The per-100-shares basis is a provisional cash-translation unit, never a lot; rupee outcomes scale with share price by construction — see the concentration notes.
