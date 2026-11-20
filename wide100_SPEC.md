# WIDE-100 INTRADAY — SPEC (frozen 2026-11-17, before scoring)

Owner order 2026-11-17 06:14 IST: run EKAM and TRIO stocks on a large
universe. This arm: the two INTRADAY stocks books — EKAM-INTRADAY
candidates CAND-T5 and S2, and the TRIO Stock Book — widened from the
frozen 25 to 100 names. Paper research only; nothing running is
mutated. Basis throughout: equity cash, per 100 shares PROVISIONAL,
₹40/trade, paper only, real ₹0.

## STAGE 1 — UNIVERSE (frozen)

Rule: the frozen 25 PLUS the next 75 most-liquid NSE names = 100.
Liquidity = median daily traded value (close × volume) over the
Oct-2026 sessions in the local daily dump
(`universe_daily/*.parquet`, 2,646 names).

Eligibility disclosure (deviation from the raw metric, stated here so
it is auditable): the raw top-75 by the metric contains 12 names that
cannot be scored in the test windows at all — they listed in
Sep–Oct 2026 (or, ATHERENERG/GROWW/MEESHO, after Jan 2025) and have
no 2025 / Jan–Oct-2026 history in the dump: JPL, TONBO, MONEYVIEW,
ATHERENERG, KANOHAR, GROWW, BONFIG, MEESHO, ZETWERK, PARASHLTH,
HEROMOTORS, SMT. A widening test whose extra names cannot trade in
the scored windows tests nothing, so eligibility additionally
requires: ≥15 Oct-2026 sessions in the dump, dump history starting
≤ 2025-01-15, last dump bar 2026-11-13. The top 75 eligible names
replace the excluded ones in rank order. Full ranking evidence:
`wide100_universe_stage1.json` (incl. the excluded names and the
names just below the cut: OFSS is #76).

THE 100 (frozen 25 first, then the 75 in liquidity rank order):

Frozen 25: ASTRAL, BDL, GLENMARK, GODREJCP, HDFCBANK, HINDALCO,
HINDCOPPER, HINDUNILVR, HINDZINC, INDUSTOWER, IRCTC, ITC,
KALYANKJIL, NATIONALUM, NHPC, NTPC, OBEROIRLTY, OIL, PFC, RECLTD,
TATASTEEL, TVSMOTOR, UNITDSPR, VEDL, WIPRO.

New 75: RELIANCE, INFY, ICICIBANK, BHARTIARTL, BSE, TCS,
PCJEWELLER, KOTAKBANK, AXISBANK, ETERNAL, SBIN, BAJFINANCE, LT,
M&M, NETWEB, CUPID, TECHM, DIVISLAB, BHEL, SHRIRAMFIN, HCLTECH,
MCX, MARUTI, COFORGE, APOLLOHOSP, PERSISTENT, PAYTM, IDEA,
ADANIPORTS, ADANIENT, ADANIPOWER, BEL, WELCORP, HAL, DIXON,
INDHOTEL, LAURUSLABS, ULTRACEMCO, POWERINDIA, POLICYBZR,
MAXHEALTH, APOLLO, SUZLON, TITAN, POWERGRID, JIOFIN, POLYCAB,
GVT&D, INDIGO, EICHERMOT, CHOLAFIN, SUNPHARMA, CHENNPETRO,
BAJAJ-AUTO, COALINDIA, UNIONBANK, HEROMOTOCO, SWIGGY, SOLARINDS,
FEDERALBNK, APARINDS, TRENT, TDPOWERSYS, DRREDDY, JSWSTEEL, LICI,
SAIL, TMPV, CUMMINSIND, SBILIFE, NESTLEIND, ADANIGREEN, CANBK,
ADANIENSOL, TFCILTD.
(Cut at #75 TFCILTD, median ₹210.63 cr/day; #76 OFSS ₹209.48 cr.)

## STAGE 2 — DATA BUILD

New root `data/wide100/<SYM>/` in the frozen stores' exact layout:
`spot_5m.csv` (timestamp,open,high,low,close; timestamps
`YYYY-MM-DD HH:MM:SS+05:30`) and `spot_daily.csv`
(date,open,high,low,close).

- The frozen 25 + NIFTY: copied verbatim from `data/sarvaritu_fwd`.
- The 75 new names: fetched via the programme's established Upstox
  route (connector surrogate auth as in
  `fetch_upstox_via_connector.py`; browser User-Agent on every
  request; instrument keys `NSE_EQ|<ISIN>` from
  `universe_daily/universe.csv`).
  - Daily: one v3 `days/1` range call 2024-10-01 → 2026-11-13
    (mirrors the 25-name layout, whose spot_daily starts 2024-10-01;
    v2 `day` fallback as in the established fetchers).
  - 5-minute: v3 `minutes/5` range calls in monthly chunks,
    2025-01-01 → 2026-11-13 (the established deep-history pattern of
    `stocks_engine_v2_rebuild_data.py`).
  - spot_daily for new names is written from the daily endpoint
    (NOT aggregated from 5m), matching how the 25-name stores were
    built by the fetch layer.
- Checkpointing: per-symbol, per-chunk; a JSON manifest
  (`wide100_fetch_manifest.json`) records chunks completed, bars,
  first/last bar per file. The fetcher is resumable and skips
  completed chunks.
- HTTP 429 = hard stop for the attempt: the fetcher stops at once,
  the manifest records RATE_LIMITED, coverage is reported honestly,
  and scoring proceeds on the covered set with coverage stated.
  No retries, no thrash.
- Coverage per name = distinct 5m session dates fetched /
  the name's own trading dates in `universe_daily` within
  2025-01-01 → 2026-11-13 (the dump is the session denominator).

## STAGE 3 — CONTROLS (all must reproduce EXACTLY before wide scoring)

On the frozen 25 from the existing stores (`data/sarvaritu_fwd` for
EKAM; the adopted-book construction for the Stock Book):

- CAND-T5 (T=5 votes, exit D=3 / S=1.00% / no cap, earliest-5/day):
  2025 Jan–Oct +₹62,164.57 · 2026 Jan–Oct +₹63,883.60 ·
  Nov 2–13 +₹24,528.65.
- S2 (identical, earliest-3/day):
  2025 Jan–Oct +₹45,300.64 · 2026 Jan–Oct +₹72,605.30 ·
  Nov 2–13 +₹20,662.60 (published in the R5 run record).
- Stock Book (adopted-C incumbent): Jan–Oct 2025 +₹1,19,813.44 ·
  Jan–Oct 2026 +₹2,47,178.79, verified by rebuilding the adopted
  book from the R16 book + frozen ingredients (the
  `stocks_engine_adoptC_verify.py` construction, part B) and
  asserting row-for-row multiset equality with the on-disk dumps
  `stocks_engine_adoptedC_book{2025,2026}_trades.csv` — without
  writing anything.
- PLUS the wide-run machinery's own control: the Stock Book
  raw-bar engine used for the wide run (below) must pass its
  native control on the 25 (`stocks_sarvaritu_logger.run_control`:
  per-trade equality with the post-C24 dumps from
  `data/full_hist`, incl. the October-2026 subset).

## STAGE 4 — WIDE SCORING (frozen rules verbatim)

Windows (identical for the 25-control and the 100-wide runs):
2025 Jan–Oct, 2026 Jan–Oct, and the November slice
2026-11-02 → 2026-11-13, each reported separately.

### EKAM candidates (CAND-T5, S2)
Machinery: `ekam_intraday_stocks_build` (data/votes/candidates) +
`ekam_intraday_stocks_r2_build.net_of` + the R5 selectors, imported
and applied verbatim; only the share root and the symbol list
change (all 100 names' stores under `data/wide100`). Rules
verbatim: first ≥5-vote signal per stock-day, entry next bar open,
≤1 trade/stock/day; the day lists sorted by (signal stamp, symbol);
CAND-T5 takes earliest 5/day, S2 earliest 3/day — the caps now bind
across 100 names; that IS the test. Exit: vote-decay ≤3, hard stop
−1.00%, no cap, square-off 15:10 bar close. Placebo: the frozen
`r2.placebo_pct` on the wide universe (200 draws, seed 20261114).

### Stock Book
The adopted-C incumbent is a stack assembled from precomputed
25-name trade-row sleeves whose builders carry hard-asserted
25-name anchors (`stocks_engine_r9_ingredients` and the round
libraries); no parameterisable raw-bar engine exists for that
stack, so it cannot be widened verbatim. The frozen raw-bar Stock
Book engine that CAN be widened verbatim is the logger's
`build_book` (the v2 book: F4 + INV-LONG + INV-ABOVE + N4-V3 +
P2F + P2F-R2 + R2-LOWBAND + v2 law) — the machinery that runs the
live November paper book, and the same machinery the
wholebook-200 build widened to 200 names in November. The wide
Stock Book run uses it, parameterised exactly as
`sarvaritu_wholebook_200_build.load_machinery200` does (data root
+ SYMBOLS in both the globals and the reentry head; window
2025-01-01 → 2026-11-13), on `data/wide100`. The comparison is
within-machinery: wide-100 vs the same engine on the 25. The
adopted-C headline totals remain the Stage-3 control and are
reported as context, never mixed into the wide comparison.

Calendar limitation (stated, not hidden): the event components
(N4-V3, P2F, P2F-R2, R2-LOWBAND) fire only on curated calendar
events. The frozen calendars (`stock_event_calendar_2025.csv`,
`stock_event_calendar_jan_oct_2026.csv`) cover the frozen 25 only;
no curated calendar exists for the new 75, and fabricating one
would break "frozen rules verbatim" (the calendar is a frozen
input). So in the wide run the event components fire only for the
25 (and, in the November slice, for any of the 100 covered by the
live/merged calendars), while the price-driven components (F4,
INV-LONG, INV-ABOVE) run on all 100. Component-level splits are
reported for both runs so the comparison stays honest.
November slice calendar = live calendar + Sarvasetu merged
calendar rows (the wholebook-200 precedent), window
2026-10-26 → 2026-11-13.

### Reported per book per window
Trades, net, WR, ex-top-3 (by trade), month table (Jan–Oct),
max drawdown (cumulative net in date/entry order), top-5 names'
share of net, placebo percentile where the frozen machinery
supports it (EKAM yes; Stock Book: the gate placebos are 25-name
sleeve constructions — not applicable wide, reported as such),
and the per-component split for the Stock Book. November slice
reported the same way minus months/placebo.

## DELIVERABLES
`wide100_SPEC.md` (this file) · `wide100_2026-11-17.md` ·
`wide100_results.json` · `wide100_trades.csv` ·
`wide100_fetch_manifest.json` (the data manifest).
If Stage-2 coverage ends partial, the report leads with coverage
and scores only covered names.
