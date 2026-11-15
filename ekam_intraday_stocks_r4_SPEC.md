# EKAM-INTRADAY — STOCKS · ROUND 4 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 4: the 6-vote turn.
Round 3 (`ekam_intraday_stocks_r3_SPEC.md`, `ekam_intraday_stocks_r3_2026-11-14.md`)
ran the anatomy of CAND-T5. No single cell met the frozen wound rule, so no dial was
scored — but the anatomy named the weak layer precisely:

- **Votes == 5 at entry:** Jul–Oct **−₹13,024.63 (2025) / −₹10,976.45 (2026)** —
  negative in the wound window of BOTH years; full-year 2025 **−₹400.51** on 816
  trades (the layer is dead weight in 2025 and the Jul–Oct bleeder in both years).
- **Votes == 6 at entry:** Jul–Oct **+₹12,237.57 (2025) / +₹8,545.80 (2026)** —
  positive in the wound window of BOTH years; full-year +₹62,565.08 / +₹30,679.67.

Round 4 turns the one dial the anatomy points at: **require the full 6 of 6 votes at
entry.** Everything else — votes definition, data, fills, caps, exits — is R1/R2
verbatim, reused from `ekam_intraday_stocks_build.py` (R1) and
`ekam_intraday_stocks_r2_build.py` (R2).
Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares PROVISIONAL** ·
₹40/trade · paper only, real money ₹0. Judged PER YEAR, never pooled.
VWAP remains the equal-weighted typical-price proxy (stores carry no volume).

## CONTROL (must reproduce before anything else)

CAND-T5 exactly as published in `ekam_intraday_stocks_r2_results.json`
(T=5 post-cap contexts; exit D=3, S=1.00%, C=none): every window block (trades,
total, WR) for 2025 and 2026, the month tables, ex-top-3, and the November CF line
(2025 +₹62,164.57 · 2026 +₹63,883.60 · November +₹24,528.65). Any mismatch stops
the run.

## THE TURN — CAND-T6

Identical to CAND-T5 in every respect EXCEPT the entry threshold:

- Entry contexts = R2 `build_contexts` at **T=6**: a stock-day's first qualifying
  signal is the first bar where the leading side holds the full **6 of 6** votes
  (exact tie still no signal, scan continues). Entry at the next bar's open;
  last-entry stamp rule unchanged; ≤ 1 trade per stock per day; ≤ 5 trades per day
  across the list, earliest signals first. This is a genuine re-selection, not a
  filter on the CAND-T5 trade set: a stock whose first ≥5 signal came at 5 votes
  may enter later at 6, not at all, or lose its day-cap slot to another stock.
- The signal bar's recorded `votes` for every CAND-T6 trade must be exactly 6
  (any other value stops the run as a data error).
- Exit stack unchanged from CAND-T5: vote-decay exit at own-direction votes ≤ 3,
  hard stop −1.00%, no profit cap, square-off at the 15:10 bar's close
  (R2 parameterised X2 with D=3, S=0.0100, C=None).

## REPORTING (per year — 2025, 2026 separately, never pooled)

Windows Jan–Jun / Jul–Oct / full Jan–Oct: trades, net, WR, expectancy per trade
(window net ÷ trades). Plus, per year: month table (Jan–Oct), ex-top-3 (full-year
total minus the 3 largest trade nets), November CF (the R1 nine November dates),
and a random-entry placebo by the R2 design verbatim (200 draws, fresh
`random.Random(20261114)` per candidate-year; each draw = CAND-T6's real trade
count for that year; each placebo trade = uniform random tradable stock-day of
that year × uniform random entry bar 09:20–15:10 × uniform random side; exit by
the CAND exit stack D=3 / S=1.00% / C=none on that stock-day's real bars and real
vote series; percentile = % of draws below the real total).

**Timing audit:** entry stamp > signal stamp asserted on every CAND-T6 trade
(structural in `build_contexts`); plus the R2 truncated-series vote recompute
(every 37th pre-cap candidate, T5+T6 combined) must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, re-checked line by line)

CAND-T6 is the channel only if: positive in both years AND in both windows of
each year AND full-year expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND placebo
≥ 95th percentile in both years. The report states the checklist verdict plainly,
line by line, per year.
