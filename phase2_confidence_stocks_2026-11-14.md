# PHASE-2 CONFIDENCE — STOCK BOOK · CONFIDENCE GATING · 2026-11-14

Spec: `phase2_confidence_stocks_SPEC.md` (frozen before scoring). Numbers:
`phase2_confidence_stocks_results.json`. Script:
`phase2_confidence_stocks_build.py`. Research only — no book, ledger, or
job changed.
**Basis (every figure): equity cash intraday, per 100 shares PROVISIONAL,
₹40/trade, paper only, real ₹0.**
Owner's principle: idle beats a marginal trade. Years scored SEPARATELY —
stocks are judged per year, never pooled.

## Control (reproduced before any scoring, exact)
Gated store: `stocks_engine_adoptedC_book{2025,2026}_trades.csv`, Jan–Oct
only, cross-checked against `stocks_adoption_variantC_results.json`
(adopted jan_oct, row_for_row_vs_r9_04 = true):
- **2025: 1,064 legs · +₹119,813.44 · WR 45.39% · 160 trade-days ·
  ₹748.83/trade-day · red months Jul (−₹660.91) and Oct (−₹4,042.67) ·
  halves +₹98,541.87 / +₹21,271.57 · ex-top-3 +₹107,481.57**
- **2026: 1,363 legs · +₹247,178.79 · WR 44.75% · 181 trade-days ·
  ₹1,365.63/trade-day · ZERO red months · halves +₹149,410.01 /
  +₹97,768.78 · ex-top-3 +₹228,933.24**
(₹/trade-day denominator = the book's own distinct trade-days in the
window, fixed for all subsets.) The store's population is the adopted
stack — the seven roof components plus the r9 sleeves NE-REV-NU, GAP-FADE,
REXP, INV-R3; the store governs, not the seven-name summary.

## Factor audit — what survived, what was dropped
Composite = equal-weight mean of five entry-knowable factors, each in
[0,1], percentiles = mid-rank empirical CDF within the year pool.
**Coverage measured 100.0% for all five factors in BOTH years** — nothing
was partially applied.
- **S1 Entry time** (carried): earlier entry scores higher (room before
  the 15:20 square-off).
- **S2 Trend alignment** (causally joined): the book's own
  REGIME-CLASSIFIER-1 (prev_close vs 50DMA + 5-day MA slope), replicated
  exactly from `regime_maps_from` / `regime_labels` on full-history NIFTY
  closes. LONG-on-UP / SHORT-on-DOWN → 1.0, FLAT → 0.5, against → 0.0.
- **S3 Trend strength**: |prev_close/ma50 − 1|, percentile.
- **S4 Prior-day relative volume** (causally joined): prior trading day's
  volume ÷ its trailing-20-day mean, percentile.
- **S5 Same-stock confluence** (carried): count of book legs in the same
  stock that day entered at or before this leg, percentile.
DROPPED, per the frozen uniformity rule: entry/exit prices, exit_reason,
setup, INV round (carried only for F4/INV components — joins 952 of 2,427
legs, 39%); prior-day stock move % (not carried; per-stock daily bars on
disk cannot uniformly reconstruct it across both years); component/stock
identity and standalone side (no non-circular numeric confidence form).
**Regime-join validation:** the replicated labels reproduce the November
paper log's own regime values exactly on both dates the close series
covers (2026-11-02 DOWN, 2026-11-03 FLAT). Cross-check against labels from
the logger's own candle store: 200/203 Jan–Oct 2026 dates agree (98.52%,
just under the spec's 99% cross-check line — 3 boundary flips between two
NIFTY close series; disclosed, not hidden; the primary check against the
book's own logged labels was exact).

## Gate results (frozen bar, per year; a level passes only if it passes in EACH year)

**2025** (full book: +₹119,813.44, WR 45.39%):
| Cut | Kept | Total | WR | ₹/trade-day | Placebo | Verdict |
|---|---|---|---|---|---|---|
| T70 | 745 | +₹81,309.57 | 44.30% | ₹508.18 | 39.0th pct | **FAIL** — WR below full book · new red month (Jan) · placebo |
| T60 | 638 | +₹74,898.84 | 43.57% | ₹468.12 | 57.5th pct | **FAIL** — WR · new red month (Jan) · placebo |
| T50 | 532 | +₹55,188.39 | 43.80% | ₹344.93 | 30.5th pct | **FAIL** — WR · total < 60% · new red months (Jan, Mar) · placebo |

**2026** (full book: +₹247,178.79, WR 44.75%):
| Cut | Kept | Total | WR | ₹/trade-day | Placebo | Verdict |
|---|---|---|---|---|---|---|
| T70 | 954 | +₹190,757.68 | 43.82% | ₹1,053.91 | 82.0th pct | **FAIL** — WR · placebo |
| T60 | 818 | +₹169,248.37 | 44.01% | ₹935.07 | 86.0th pct | **FAIL** — WR · placebo |
| T50 | 682 | +₹163,697.00 | 44.72% | ₹904.40 | 99.0th pct | **FAIL** — WR only (44.72% vs 44.75% full book) |

**No grid level passes.** The pattern differs by year and both halves of it
are damning in different ways: in 2025 the score *anti-selects* — kept
subsets land at the 31st–58th percentile of random same-size subsets and
win rate falls at every cut. In 2026 the deep cut genuinely preserves
money (T50 keeps 66% of the total on 50% of trades, 99th placebo
percentile, no red month, both halves and ex-top-3 positive) — but win
rate never rises at any cut in either year: the kept trades win at the
same ~44–45% rate as the book as a whole. A confidence filter that cannot
raise the win rate has not found confidence.

## November application (descriptive only — November sets no rule)
The frozen score meets a data wall in November: the volume store ends
2026-10-30, so S4 exists only for legs whose prior trading day is
2026-10-30 — **only Nov 2's 4 legs are scorable; the other 28 are
UNSCORED** (missing factor: S4 prior-day relative volume; never estimated).
On the one day the filter could judge, it judged badly: at T70 it idles
HINDZINC F4 (+₹723.50, the day's biggest winner, score 0.3877 vs cut
0.3983); at T60/T50 it also idles HINDCOPPER INV-LONG (+₹465.19).

| Day | Actual | T70 kept / idled / unscored | T60–T50 kept / idled / unscored |
|---|---|---|---|
| Nov 2 | +₹1,455.27 | +₹731.77 / +₹723.50 / — | +₹266.58 / +₹1,188.69 / — |
| Nov 3 | −₹451.85 | — / — / −₹451.85 | — / — / −₹451.85 |
| Nov 4 | −₹420.94 | — / — / −₹420.94 | — / — / −₹420.94 |
| Nov 5 | −₹299.28 | — / — / −₹299.28 | — / — / −₹299.28 |
| Nov 6 | +₹6,577.68 | — / — / +₹6,577.68 | — / — / +₹6,577.68 |
| Nov 9 | +₹704.30 | — / — / +₹704.30 | — / — / +₹704.30 |
| Nov 11 | +₹826.10 | — / — / +₹826.10 | — / — / +₹826.10 |
| Nov 12 | −₹425.54 | — / — / −₹425.54 | — / — / −₹425.54 |
| Nov 13 | −₹447.80 | — / — / −₹447.80 | — / — / −₹447.80 |
| **Month** | **+₹7,517.94** | see below | see below |

Filtered month totals (actual +₹7,517.94): **T70 ₹6,794.44** (UNSCORED
kept) / ₹731.77 (UNSCORED excluded) · **T60 ₹6,329.25** / ₹266.58 ·
**T50 ₹6,329.25** / ₹266.58. On the only like-for-like reading (UNSCORED
kept), the filter makes November *worse* at every level — it can only
touch Nov 2, and there it removes winners. The excluded variant is shown
because the spec requires both ways; it is not a tradable figure (it
discards 28 unjudged trades).

## Audit note (disclosed, not buried)
The first scoring pass contained a defect in the November leg of the run:
the prior-day-volume lookup initially fell back to the volume store's last
row (2026-10-30) for November legs whose true prior trading day was not in
the store — a silent fill of exactly the kind the spec forbids. It was
caught in audit, fixed to strict prior-trading-day presence (master
calendar = the NIFTY daily series), and re-run. The fix changed NO Jan–Oct
figure (volume coverage there is genuinely complete — every kept/idled
number above is identical across both passes); it changed only the
November application, from a false "32 scored" to the honest 4 scored /
28 UNSCORED.

## Honest bottom line
Confidence, as entry-knowable state, knows nothing usable about stock
trades. In 2025 it picks slightly *worse* than chance; in 2026 its deep
cut can smell where the money sits but still cannot tell a winner from a
loser — win rate is flat at every cut in both years. That is the opposite
of the Bank stack, where the same method lifted WR 59.5% → 62.5% and
passed. The Stock Book's edge is shaped differently: it is a payoff book,
not a selection book — it wins ~45% of trades by construction and makes
its money on exit asymmetry (targets 2–3× stops across its components).
There is nothing at the entry bar, in any factor the stores honestly
carry, that separates its winners in advance. **The Stock Book stands
unchanged; no confidence filter is adopted for stocks.**
