# EKAM-INTRADAY — STOCKS · ROUND 3 SPEC (frozen 2026-11-14, before scoring)

Programme: EKAM-INTRADAY v1, Stocks segment — ROUND 3: fix the Jul–Oct wound.
Round 2 (`ekam_intraday_stocks_r2_SPEC.md`, `ekam_intraday_stocks_r2_2026-11-14.md`)
tuned the X2 exit dials; its candidate CAND-T5 improved both years
(2025 +₹62,164.57 / 2026 +₹63,883.60, placebo 100.0 both years, November +₹24,528.65)
but did NOT reach the desired-result bar: Jul–Oct is negative in all four
candidate-years and full-year expectancy is ₹60.06 / ₹62.33 against the ₹80 line.
Round 3 finds WHERE the Jul–Oct bleed sits in CAND-T5, then turns the ONE structural
dial the anatomy names. Everything else — entries, votes, exits, data, fills, caps —
is R1/R2 verbatim, reused from `ekam_intraday_stocks_build.py` (R1) and
`ekam_intraday_stocks_r2_build.py` (R2).
Basis: equity cash intraday · frozen 25-name watchlist · **per 100 shares PROVISIONAL** ·
₹40/trade · paper only, real money ₹0. Judged PER YEAR, never pooled.
VWAP remains the equal-weighted typical-price proxy (stores carry no volume).

## CONTROL (must reproduce before anything else)

CAND-T5 exactly as published in `ekam_intraday_stocks_r2_results.json`
(T=5; exit D=3, S=1.00%, C=none): every window block (trades, total, WR) for 2025 and
2026, the month tables, ex-top-3, and the November CF line. Any mismatch stops the run.

## STEP 1 — ANATOMY of CAND-T5 (reported before any dial)

The CAND-T5 trade set (R2 post-cap contexts at T=5, nets at the CAND exit params)
is split three ways. Definitions, frozen:

- **(a) Side:** LONG (side = +1) vs SHORT (side = −1).
- **(b) Entry hour bucket** by `entry_stamp` (the entry bar's stamp):
  09–11 = stamp < "11:00" · 11–13 = "11:00" ≤ stamp < "13:00" · 13–15 = stamp ≥ "13:00".
- **(c) Votes at entry:** the trade record's `votes` field = own-direction votes at the
  signal bar that produced the entry; for the T5 base this is 5 or 6 (any other value
  stops the run as a data error).

Every cell is reported PER YEAR (2025, 2026 separately), for Jan–Jun and Jul–Oct
separately AND for the full Jan–Oct window: trades, net, WR.

**WOUND RULE (frozen):** within one split, a cell is A WOUND if in BOTH years:
(i) its Jul–Oct net < 0, AND
(ii) its full Jan–Oct net is negative OR the lowest among that split's cells that year.
Collect all wound cells across the three splits. If wounds exist in exactly one split,
that split names the dial. If wounds exist in several splits, the split whose wound
cell has the most negative combined Jul–Oct net (2025 Jul–Oct net + 2026 Jul–Oct net)
names the dial; tie → split order (a) side, (c) votes, (b) hour. If one split holds
two wound cells, the one with the more negative combined Jul–Oct net is the wound.

## STEP 2 — THE DIAL (exactly one, chosen by this frozen mapping)

All dials operate on the frozen post-cap CAND-T5 trade set; no re-selection is done
and the ≤ 5/day cap can only shrink.

- **Wound = one side** → drop that side entirely (full year, both years). Candidate =
  the CAND-T5 trades of the other side, nets unchanged.
- **Wound = votes == 5** → confirmation bar: for every votes == 5 CAND-T5 trade,
  require own-direction votes at the ORIGINAL entry bar (the bar right after the
  signal bar) to still be ≥ 5. If confirmed, the entry shifts to the open of the
  following bar (`entry_li + 1`) and the CAND exit stack (D=3, S=1.00%, C=none) is
  re-run from there. Unconfirmed, own-votes undefined (None) at that bar, or
  `entry_li + 1` beyond the 15:10 square-off bar → the trade is dropped.
  Votes == 6 trades are unchanged.
- **Wound = bucket 13–15** → entry cutoff 13:00. Candidate = CAND-T5 trades with
  `entry_stamp` < "13:00", nets unchanged.
- **Wound = any other cell** (hour 09–11 or 11–13, or votes == 6), **or no wound
  anywhere** → NO dial is scored; the report ends at the anatomy.

## STEP 3 — THE DIALED CANDIDATE (full re-score, per year, never pooled)

Windows Jan–Jun / Jul–Oct / full Jan–Oct: trades, net, WR, expectancy per trade
(full-year net ÷ trades). Plus, per year: month table (Jan–Oct), ex-top-3 (full-year
total minus the 3 largest trade nets), November CF (the R1 nine November dates),
and a random-entry placebo by the R2 design verbatim (200 draws, fresh
`random.Random(20261114)` per candidate-year; each draw = the candidate's real trade
count for that year; each placebo trade = uniform random tradable stock-day of that
year × uniform random entry bar 09:20–15:10 × uniform random side; exit by the CAND
exit stack D=3 / S=1.00% / C=none on that stock-day's real bars and real vote series —
the exits are unchanged by every dial in this round; percentile = % of draws below
the real total).
**Timing audit:** entry stamp > signal stamp asserted on every candidate trade
(including shifted confirmation entries); plus the R2 truncated-series vote recompute
(every 37th pre-cap candidate, T4+T5 combined) must show 0 mismatches.

## DESIRED-RESULT BAR (the owner's, re-checked line by line)

A candidate is the channel only if: positive in both years AND in both windows of
each year AND full-year expectancy per trade ≥ ₹80 (2× the ₹40 cost) AND placebo
≥ 95th percentile in both years. The report states the checklist verdict plainly.
