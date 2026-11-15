# EKAM-INTRADAY — STOCKS · ROUND 6 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 6: the 2025 Jul–Oct cell.
Round 5 (`ekam_intraday_stocks_r5_2026-11-14.md`) thinned the book by selection.
S2 EARLIEST-3 cleared every bar leg in 2026 (both windows positive, expectancy
₹118.06, placebo 100.0) but 2025 still fails on one cell: **Jul–Oct −₹7,310.17**
and full-year expectancy ₹72.95 (< ₹80). S1 fails the same cell (−₹11,211.77,
expectancy ₹66.88). Every variant's last wound is 2025 Jul–Oct. This round opens
that cell: anatomy first, then exactly one dial chosen by the frozen mapping
below — or no dial at all.

Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0. Judged PER YEAR, never
pooled. VWAP is the equal-weighted typical-price proxy (stores carry no volume).
Everything except the Step-2 dial is R1/R2/R5 verbatim, reused from
`ekam_intraday_stocks_build.py` (R1), `ekam_intraday_stocks_r2_build.py` (R2) and
`ekam_intraday_stocks_r5_build.py` (R5): CAND-T5 entries (first ≥5-vote signal
per stock-day), CAND-T5 exit stack (vote-decay exit at own votes ≤ 3, hard stop
−1.00%, no cap, square-off at the 15:10 bar's close), ≤ 1 trade per stock per day.

## CONTROL (must reproduce before anything else)

**S2 = EARLIEST-3** exactly as published in `ekam_intraday_stocks_r5_results.json`:
R5 `collect_day_candidates` + `sel_s2` (candidates sorted by (signal_stamp, sym),
first 3), exit D=3, S=1.00%, C=none — every window block (trades, total, WR,
expectancy) for 2025 and 2026, ex-top-3, and the November CF line
(2025 **+₹45,300.64** · 2026 **+₹72,605.30** · November 27 trades
**+₹20,662.60**). Any mismatch stops the run.

## STEP 1 — ANATOMY of S2's 2025 Jul–Oct trades

The 252 trades with date in 2025-07-01..2025-10-31, nets by the control stack.
Splits, each with trades / net / WR:
- **by month** — Jul / Aug / Sep / Oct (date month).
- **by side** — LONG (side +1) vs SHORT (side −1).
- **by stock** — the 5 most negative names by total net, with their totals
  (trades and WR shown).
- **by entry votes** — 5 vs 6 (the candidate's own-direction votes at entry).
State which cells carry the −₹7,310.17. For the Step-2 mapping only, the same
by-side split is also computed for S2's **2026 Jul–Oct** trades.

## STEP 2 — THE DIAL (exactly one, by this frozen mapping — checked in this order)

1. **SIDE DROP.** If one side's 2025 Jul–Oct net is negative AND that same side
   is negative-or-weakest in 2026 Jul–Oct — where *weakest* means its 2026
   Jul–Oct net is ≤ the other side's — then that side is dropped everywhere
   (see "how a dial is applied" below).
2. **NO DIAL — month concentration.** Else, if the 2025 Jul–Oct bleed
   concentrates in ONE month — frozen definition: a single month's net is
   ≤ −₹7,310.17 (the whole window loss), i.e. the other three months together
   are non-negative — then NO dial is scored (a month cut is curve-fitting).
   The report ends at the anatomy plus this statement.
3. **BREADTH GATE.** Else, entries are gated on breadth: for each candidate,
   breadth at its own signal bar = the share of the frozen 25 names that have a
   bar at that signal timestamp on that date whose close at that bar is above
   their own session VWAP-proxy at that bar (cumulative mean of typical price
   through that bar). Denominator = names with a bar at that timestamp. Skip a
   LONG candidate if breadth < 40%; skip a SHORT candidate if breadth > 60%.
   The gate uses only bars at the signal timestamp itself — causal; entry is
   still the next bar.

**How a dial is applied (frozen):** the dial filters the day's pre-cap candidate
list (the same list R5's selection rules operate on), then EARLIEST-3 selection
runs on what remains — a filtered-out candidate frees its slot for the next
candidate, exactly as the R5 selection rows work. A candidate's admission
depends only on its own properties and data at its own signal bar; no
end-of-day information is used.

## STEP 3 — RE-SCORE (only if a dial was chosen)

Per year (2025, 2026 separately, never pooled): windows Jan–Jun / Jul–Oct /
full Jan–Oct (trades, net, WR, expectancy per trade), month table Jan–Oct,
ex-top-3 (full-year total minus the 3 largest trade nets), November CF (the R1
nine November dates), and the random-entry placebo by the R2 design verbatim
(200 draws, fresh `random.Random(20261114)` per year; each draw = the row's
real trade count for that year; each placebo trade = uniform random tradable
stock-day of that year × uniform random entry bar 09:20–15:10 × uniform random
side; exit by the CAND exit stack D=3 / S=1.00% / C=none; percentile = % of
draws below the real total).

**Timing audit:** entry stamp > signal stamp asserted on every trade
(structural in the R5 context builder); plus the R2/R5 truncated-series vote
recompute (every 37th pre-cap T=5 candidate) must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, re-checked line by line for the dialled row)

The row is the channel only if: positive in both years AND in both windows of
each year AND full-year expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND
placebo ≥ 95th percentile in both years. The report states the checklist
verdict plainly, per year.
