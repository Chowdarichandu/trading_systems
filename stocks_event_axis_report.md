# Stocks EQUITY — Event-Axis Invention (A) + November Dry Run (B) — 2026-10-31

**EQUITY CASH only, LONG/SHORT. Paper only, no orders, real money
₹0. Every rupee figure provisional per 100 shares. Cost ₹40 per
round trip. Window Jan–Oct 2026 (Oct 1–28), 25 stocks. Halves
Jan–May / Jun–Oct. Spec frozen BEFORE scoring:
`stocks_event_axis_frozen.md`. Engine: `stocks_event_axis.py`;
full numbers: `stocks_event_axis_results.json`; per-family trade
CSVs: `eq_eventaxis_*.csv`.**

# SECTION A — EVENT-AXIS INVENTION

## Validation (before any subset was scored)

- All three frozen pools reproduce their published totals
  exactly: ladder+volume V3 = 3,275 trades / −₹16,284.00;
  P2-full @T125 = 918 / +₹10,657.81; INV1 @T125 = 694 /
  +₹22,964.30.
- One vocabulary catch: ladder files tag event membership
  `event`, the round-8/9/10 files tag it `event_window`. After
  normalising, the independently re-derived WIDE window
  (calendar ±7 trading days, per-stock trading-day index)
  matches the frozen CSV tag on **100% of trades in all three
  pools (0 mismatches)** — the definitions agree; the tag was
  safe to subset on.

## EA1 — event-only restriction of the strongest pools

Gate: net > 0 in BOTH halves AND breadth ≥ 10/25 positive
stocks AND top-3 share ≤ 75% of a positive total.

| Family | Trades | Win% | Net Jan–May | Net Jun–Oct | Net total | Gross exp ₹/tr | Breadth | Gate |
|---|---|---|---|---|---|---|---|---|
| V3-ladder · WIDE | 863 | 42.5% | −3,456.86 | −9,513.19 | −12,970.05 | +28.72 | 8/25 | FAIL |
| V3-ladder · NARROW (±2d) | 302 | 42.1% | +6,169.95 | −16,087.57 | −9,917.62 | +7.16 | 10/25 | FAIL |
| P2-full · WIDE | 290 | 30.3% | −5,006.81 | +5,289.93 | +283.12 | +40.98 | 9/25 | FAIL |
| P2-full · NARROW (±2d) | 102 | 24.5% | −12,376.16 | −6,547.80 | −18,923.96 | −145.53 | 4/25 | FAIL |
| INV1 · WIDE | 199 | 30.7% | −2,843.41 | +2,646.36 | −197.05 | +39.01 | 10/25 | FAIL |
| INV1 · NARROW (±2d) | 69 | 21.7% | −9,899.21 | −6,572.60 | −16,471.81 | −198.72 | 3/25 | FAIL |

No-event complements (context, not families): V3-ladder
no-event +₹48,870.46 in Jan–May but −₹52,184.41 in Jun–Oct
(total −₹3,313.95); P2-full no-event +₹10,374.69 total
(Jan–May −₹28.69 / Jun–Oct +₹10,403.38); **INV1 no-event
+₹23,161.35 total, positive in both halves (+₹10,098.42 /
+₹13,062.93), breadth 11/25.**

**Verdict EA1: NO PASS — and the premise is corrected.**
Restricting these pools to event windows does not create a
survivor. For the ladder, event-window trades are the *worst*
part of the pool in Jun–Oct (October alone −₹15,417.20 WIDE);
its Jan–May money was in no-event trades. The Part-3
observation that motivated this workstream (event trades
positive inside the D1/D2/X2 families) does **not** generalise
to the ladder or P2 pools — it belonged to those families'
specific exits, not to event proximity itself. For INV1, the
money sits in the below-trend condition, not in event
proximity: its no-event subset carries both halves, and its
event subset is Jan–May-negative. The NARROW reaction-±2-day
window is uniformly toxic for signal-pool trades (negative
gross expectancy in both halves for P2 and INV1) — trading a
mechanical signal *near* a reaction day is the opposite trade
to N4, which trades *the reaction move itself* at a fixed
trigger. Consequence: INV1 stays exactly as frozen for its
November shadow (it already includes its event days; nothing
here justifies changing it), and no event-restricted variant
of any pool earns a paper spec.

## EA2 — event-proximity drift (scheduled RESULTS only)

Rule (frozen): direction = sign of the PREVIOUS results event's
reaction-day close-vs-open; enter at the open of day R−2, exit
at the close of day R−1, where R = this event's reaction day.
**This is a 2-trading-day hold with overnight exposure — NOT
intraday** — and is judged separately for that reason.

- Results events with reaction day in window: 85. Scored: 74.
  Skips: 11 (10 = first in-file event for the stock, no
  previous quarter in the calendar; 1 = previous reaction day
  missing from daily data; 0 zero-sign).
- 74 trades, win 55.4%, total **+₹8,811.00**: Jan–May
  **+₹14,880.00** (39 trades, gross expectancy +₹421.54/trade),
  Jun–Oct **−₹6,069.00** (35 trades, gross expectancy
  −₹133.40/trade). October alone +₹15,353.00 — i.e. Jun–Sep is
  deeply negative and the second half is one month carrying a
  losing quarter-window.
- Concentration fails in spirit even where the letter is
  checked: BDL alone +₹15,010.00 (more than the whole total);
  the top-3 stocks sum to +₹27,080 against a +₹8,811 total —
  the other 71 trades net −₹18,269 in aggregate outside the
  top names. Breadth 11/25.

**Verdict EA2: FAIL** (Jun–Oct negative; top-heavy). The
previous-reaction-sign drift is real in Jan–May and in October
and absent-to-negative in between — the same half-year regime
signature that has killed every family in this search. No
paper spec.

## EA3 — reaction-day volume confirmation on N4-V3

Pace = (09:15+09:20+09:25 volume on the reaction day) ÷
(20-day mean of the same), from `data/progressive_vol/`.
KEPT = pace ≥ 1.0. Unclassifiable: **0 of 56** (every N4-V3
trade had ≥ 10 prior volume days and all three bars).

| Set (T125 primary) | Trades | Win% | Net Jan–May | Net Jun–Oct | Gross exp JM | Gross exp JO |
|---|---|---|---|---|---|---|
| Full N4-V3 | 56 | 37.5% | +5,155.13 | +2,835.30 | +191.62 | +168.88 |
| KEPT (pace ≥ 1.0) | 50 | 36.0% | +4,941.56 | **−508.66** | +199.41 | +13.23 |
| DROPPED (pace < 1.0) | 6 | 50.0% | +213.57 | +3,343.96 | +111.19 | +1,154.65 |

At T10 (secondary) the same shape: kept +₹5,889.11 total with
Jun–Oct **−₹1,882.19**; dropped Jun–Oct +₹2,628.29.

**Verdict EA3: FAIL on the frozen pass bar.** Volume
confirmation slightly raises Jan–May expectancy (+199.41 vs
+191.62 gross) but destroys Jun–Oct: N4-V3's second-half edge
partly lives in LOW-pace reaction days (the 6 dropped trades
carried +₹3,343.96 of Jun–Oct profit). Filtering N4 by
reaction-day volume would have flipped its only both-halves
system to a one-half system. **N4-V3 enters November exactly
as frozen — unchanged.**

## Section A overall

**No EA family passes. No paper spec is earned by Workstream
A.** The event axis, tested three direct ways on top of the
pools that inspired it, does not produce a new both-halves
survivor: event-proximity restriction (EA1) subtracts value,
pre-event drift (EA2) flips sign between halves like
everything else in 2026, and volume confirmation (EA3) removes
the wrong trades. The event-axis exposure that remains live
is the pair already frozen for November — N4-V3 (primary) and
INV1 (shadow) — both unchanged by anything found here.

---

# SECTION B — MONDAY-READINESS DRY RUN, FRIDAY 2026-10-30

Engine: `stocks_nov_dryrun.py`. Raw fetched data:
`data/dryrun_2026-10-30/` (25 stock 5-min files + NIFTY daily).
Would-be log rows: `stocks_nov_dryrun_n4_2026-10-30.csv`,
`stocks_nov_dryrun_inv1_2026-10-30.csv`. **The real November
logs were not touched — verified header-only (1 line each)
after the run.** No November claims: this is a rehearsal on
30-Oct data.

## Step-by-step outcome

1. **Fetch 5-min candles, 25 stocks, 29+30 Oct (Upstox path as
   in `fetch_vol_janoct.py`): WORKED, with one real failure
   found — see F1.** After the wide-refetch guard (below),
   every stock had exactly 75 bars on both days.
2. **NIFTY daily via `/v3/historical-candle/{key}/days/1/{to}/{from}`:
   WORKED.** 53 bars (2026-08-14 → 2026-10-30); 51 dates overlap
   the cache and every overlapping close matches the cache
   exactly (max diff 0.0).
3. **Daily aggregation from 5-min (needed for 29-Oct stock
   dailies / previous closes): VALIDATED.** Aggregating
   2026-10-28 from the volume cache reproduces the daily cache
   OHLC for all 25 stocks with max abs diff 0.0.
4. **N4-V3 simulation: WORKED.** Reaction-day candidates for
   30 Oct per the November watchlist (verified 2026-10-30
   refresh): **GODREJCP only** (Q2 FY27 results, board
   2026-10-29 → reaction 2026-10-30). Trigger: 09:25 close
   805.0 vs 29-Oct close 837.0 = **−3.823%** → fires. Row that
   would have been logged:
   - GODREJCP, results, event 2026-10-29, reaction 2026-10-30,
     SHORT, entry 09:35 @ 807.95 (09:30-bar close), stop
     811.99, target 797.85, exit **stop @ 811.99, 11:35**,
     **net −₹443.97** provisional per 100 shares; T10 shadow
     also −₹443.97 (same stop, hit before either target).
5. **INV1 condition: WORKED — condition MET for 30 Oct.**
   NIFTY close 2026-10-29 = **22,936.75** ≤ 50DMA **23,276.78**
   (50 closes ending 29 Oct).
6. **P2 generation for 30 Oct (frozen round-8 machinery,
   contexts injected in-memory only): WORKED.** 28 raw chain
   trades @T125 → **4 after the P2 filters** (chain ≤ 2,
   entry < 10:30, ADR ≥ 3% — ADR filter passed for 7/25 stocks
   that day). Because the condition was MET, these 4 rows
   **would have been logged** (all round 1, all no_event):
   - KALYANKJIL SHORT 09:35 @ 506.00 → target 14:00 @ 499.68,
     net **+₹592.50** (T10 shadow +₹466.00)
   - WIPRO LONG 09:35 @ 193.91 → target 12:15 @ 196.33,
     net **+₹202.39** (T10 shadow +₹153.91)
   - HINDCOPPER SHORT 09:45 @ 401.90 → stop 12:05 @ 403.91,
     net **−₹240.95** (T10 shadow −₹240.95)
   - NATIONALUM SHORT 09:45 @ 316.70 → stop 11:35 @ 318.28,
     net **−₹198.35** (T10 shadow −₹198.35)
   - Day total at T125: **+₹355.59** provisional per 100 shares.

## Failure points found (all reproduced live, not hypothetical)

- **F1 — CRITICAL, both crons: the newest trading day can be
  silently missing from a short-range Upstox response.** Run 1:
  HDFCBANK returned **0 bars for 2026-10-30** in the 2-day
  (29–30 Oct) response while returning 75 for 29 Oct. Run 2:
  HDFCBANK *and* HINDUNILVR both came back short. In every
  case a wider request (last 5 trading days) returned the full
  75 bars. It is intermittent — different stocks on different
  runs. A cron that trusts a single-day/short-range response
  will, some Mondays, silently skip a stock: for N4 a missed
  candidate, for INV1 silently missing trades, with no error
  anywhere.
- **F2 — N4 cron: the Jan–Oct calendar file is a trap.**
  `stock_event_calendar_jan_oct_2026.csv` contains **no
  GODREJCP 2026-10-29 row and no rows at all after 2026-10-28**.
  Anything reading only that file finds zero candidates for
  30 Oct — including the one real candidate. The cron body as
  written uses the November watchlist + same-day filing check
  (correct — the GODREJCP event exists only there), but the
  body never says the calendar must NOT be used for November.
  Also observed: HINDALCO filed a Reg-30 intimation ON 30 Oct
  (earnings-call notice for 6 Nov, not results) — a filing
  check must classify the event, not merely detect a filing.
- **F3 — INV1 cron: lookback depth is unspecified.** The
  50DMA needs the 50 closes ending the previous day; the cache
  daily files end 2026-10-28, so from Monday the cron is
  entirely dependent on fresh fetches. The body says "fetch
  Nifty daily candles" with no lookback — a short fetch (e.g.
  30 days) cannot compute a 50DMA and the run would fail or,
  worse, compute a wrong one. Same issue for the stock ADR
  filter (prior-10-day daily ranges; cache ends 28 Oct).
- **F4 — both crons: no market-holiday / outage guard.** On a
  holiday every stock returns 0 bars; neither body says what
  to do. Without a guard, a holiday (or an API outage) is
  indistinguishable in the logs from a genuine no-trade day.
- **F5 — INV1 cron, minor: the spec's `unclassifiable` row**
  (50DMA not computable → log one note row, no trades) is in
  the frozen shadow spec but not mentioned in the cron body.
- **Checked and CLEAN:** the N4 cron's trigger/entry/exit
  wording matches the frozen spec exactly (09:25-bar close vs
  previous close ≥ 1.0%; entry at 09:30-bar close recorded
  09:35; target +1.25% / stop −0.5%, stop-first; 15:10
  square-off; T10 in the shadow column). The INV1 cron's
  condition wording (previous close ≤ 50DMA, equality counts)
  and P2 filter wording match its spec.

## Precise changes the parent should make to the cron bodies
(none were made by this run — bodies untouched)

1. **Both crons, fetch step — add:** "Fetch at least the last
   5 trading days of 5-min candles per stock, not just today.
   Assert exactly 75 bars for today's date per stock; if a
   stock is short, refetch the wider range once; if it is
   still short, name the stock as FAILED in the chat report
   and do not score it — never skip a stock silently."
2. **Both crons — add a guard line:** "If ALL stocks return 0
   bars for today, report 'market holiday or data outage —
   nothing logged' and stop."
3. **N4 cron, step 1 — add:** "Do NOT use
   stock_event_calendar_jan_oct_2026.csv for November — it
   ends 2026-10-28 and contains no November events. The
   watchlist plus the same-day filing check are the only event
   sources. Classify each filing (results vs single-news vs
   other intimation); an intimation that is neither (e.g. an
   earnings-call notice) is not a candidate."
4. **INV1 cron, step 1 — replace "fetch Nifty daily candles"
   with:** "Fetch NIFTY daily candles (days/1) for at least
   the last 80 calendar days, or read
   data/progressive/NIFTY/spot_daily.csv and append the new
   days; the 50DMA is the mean of the 50 closes ending at the
   previous trading day. If fewer than 50 prior closes are
   available, log one `unclassifiable` row and stop."
5. **INV1 cron, step 2 — add:** "Daily ranges for the ADR
   filter come from the same extended daily series (cache
   extended with the newly fetched days, or daily bars
   aggregated from the fetched 5-min candles — aggregation
   verified exact against the cache on 2026-10-28)."

## Monday-readiness verdict

**Both workflows run end-to-end on real data.** With fix 1
(the fetch assertion) applied, both crons are safe to fire on
Monday 2026-11-02; fixes 2–5 are robustness/completeness edits
that should ride along. Without fix 1, the expected failure
mode is a silently incomplete day — observed twice in two
dry runs.

---

*Files: `stocks_event_axis_frozen.md` (spec, frozen pre-scoring),
`stocks_event_axis.py` + `stocks_event_axis_results.json` +
`eq_eventaxis_*.csv` (Workstream A), `stocks_nov_dryrun.py` +
`stocks_nov_dryrun_n4_2026-10-30.csv` +
`stocks_nov_dryrun_inv1_2026-10-30.csv` +
`data/dryrun_2026-10-30/` (Workstream B). Paper only; real
money ₹0 throughout.*
