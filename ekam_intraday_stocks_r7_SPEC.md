# EKAM-INTRADAY — STOCKS · ROUND 7 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 7: six votes under the
cap-3 selection. Round 6 (`ekam_intraday_stocks_r6_2026-11-14.md`) opened S2's
2025 Jul–Oct cell (−₹7,310.17). The side-drop dial fixed that cell but broke
the year (2025 full −₹682.74 vs control +₹45,300.64; November flipped to
−₹4,210.85): LONG earns Jan–Jun and bleeds Jul–Oct in both years — the side
is seasonal, not defective. The same anatomy's other repeated signal: inside
the cell, **5-vote entries lost −₹13,234.47 (199 trades) while 6-vote entries
made +₹5,924.30 (53 trades)**. Round 4 had already tested 6 votes, but under
the OLD cap-5 selection, where the 6-vote book re-selected badly. Under Round
5's winning cap-3 (EARLIEST-3) selection the combination is untested. This
round tests exactly that combination — one row, nothing else moves.

Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR, never
pooled. VWAP is the equal-weighted typical-price proxy (stores carry no
volume). Everything except the entry-vote threshold is R1/R2/R5 verbatim,
reused from `ekam_intraday_stocks_build.py` (R1),
`ekam_intraday_stocks_r2_build.py` (R2) and
`ekam_intraday_stocks_r5_build.py` (R5).

## CONTROL (must reproduce before anything else)

**S2 = EARLIEST-3** exactly as published in `ekam_intraday_stocks_r5_results.json`
(row S2) and re-verified in R6: R5 `collect_day_candidates` (T=5) +
`sel_s2` (candidates sorted by (signal_stamp, sym), first 3), CAND-T5 exit
stack (vote-decay exit at own votes ≤ 3, hard stop −1.00%, no cap, square-off
at the 15:10 bar's close) — every window block (trades, total, WR,
expectancy) for 2025 and 2026, month tables, ex-top-3, and the November CF
line (2025 **+₹45,300.64** · 2026 **+₹72,605.30** · November 27 trades
**+₹20,662.60**). Any mismatch stops the run.

## THE ROW — S2-T6

Identical to S2 in every respect — EARLIEST-3 day cap (candidates sorted by
(signal_stamp, sym), first 3), CAND-T5 exit stack (decay ≤ 3, stop −1.00%,
no cap, square-off 15:10), ≤ 1 trade per stock per day — **EXCEPT** the
per-stock-day candidate is the first signal at the full **6 of 6 votes**
(R1 `day_candidates(S, date, 6)`), not the first ≥5-vote signal. A stock-day
whose signals never reach 6 votes contributes no candidate; a day with fewer
than 3 six-vote candidates takes fewer than 3 trades. Every S2-T6 trade must
carry votes = 6 (asserted).

## SCORING

Per year (2025, 2026 separately, never pooled): windows Jan–Jun / Jul–Oct /
full Jan–Oct (trades, net, WR, expectancy per trade), month table Jan–Oct,
ex-top-3 (full-year total minus the 3 largest trade nets), November CF (the
R1 nine November dates), and the random-entry placebo by the R2 design
verbatim (200 draws, fresh `random.Random(20261114)` per year; each draw =
the row's real trade count for that year; each placebo trade = uniform random
tradable stock-day of that year × uniform random entry bar 09:20–15:10 ×
uniform random side; exit by the CAND exit stack D=3 / S=1.00% / C=none;
percentile = % of draws below the real total).

**Timing audit:** entry stamp > signal stamp asserted on every trade
(structural in the R5 context builder); plus the R2/R4 truncated-series vote
recompute over the combined pre-cap candidate list (T=5 + T=6, every 37th)
must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, re-checked line by line for S2-T6)

The row is the channel only if: positive in both years AND in both windows
of each year AND full-year expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND
placebo ≥ 95th percentile in both years. The report states the checklist
verdict plainly, per year.
