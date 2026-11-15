# DIAL — STOCKS · SPEC (frozen 2026-11-14, before scoring)

Programme: DIAL (one roof, one name — registry `dial_programme.md`). Segment: **Stocks**.
Member: DIAL standalone indicator system — STANDALONE. It does NOT condition or filter the
Stock Book's trades; it generates its own signals from the frozen 25 names' candles.
Basis: equity cash intraday · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0.
Frozen 25: ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC
INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL
TVSMOTOR UNITDSPR VEDL WIPRO.

## CORE SPEC (owner-frozen — verbatim, unaltered)

- Data: 5-min candles for the 25 names, Jan 2025–Oct 2026, from the persisted stores the
  Stock Book runs used; signal on a COMPLETED bar's close; entry at the NEXT bar's open.
- **DIAL-T (trend):** Supertrend(7,3) flip at a bar close AND price on the same side of
  session VWAP → LONG for up-flips, SHORT for down-flips. First qualifying signal per stock
  per day.
- **DIAL-R (reversion):** RSI(14) ≤ 30 AND Bollinger %B ≤ 0.05 AND EMA50 slope (6 bars)
  > −0.1% → LONG; mirror (≥ 70, ≥ 0.95, slope < +0.1%) → SHORT. First qualifying signal
  per stock per day.
- Exits (both): target +1.0% on price, stop −0.5%, square-off 15:15. Cost ₹40/trade.
  Report components separately AND combined as the DIAL-Stocks book, PER YEAR (stocks are
  judged per year, never pooled).

## GATE (frozen, same run, per year)

Timing audit; random-entry placebo per year (same trade count per year, random name/day/bar,
same geometry — must beat 95th pct in EACH year); halves per year; month table per year;
ex-top-3 per year.
**PASS BAR (per year, both years must pass):** placebos met AND halves positive AND
ex-top-3 positive AND monthly pace ≥ ₹7,500 in 2026 and ≥ ₹5,000 in 2025 AND no more than
4 red months in a year. WR reported (no WR bar — the Stock Book family is payoff-shaped).

## DATA / FILL DETAILS (how the frozen core is realised on the persisted stores)

1. **Store:** `data/sarvaritu_fwd/<SYM>/spot_5m.csv` — the forward store the Stock Book
   runs themselves maintain. Verified identical to `data/full_hist/` on every overlapping
   bar (0 close diffs on sampled names) and extends to 2026-11-13, which the November CF
   needs. One store for everything: gate window + CF.
2. **No volume exists** in any persisted full-history stock store (OHLC only; the sole
   volume-bearing store covers Oct 2026 at 1-min). Session VWAP is therefore computed as
   the **equal-weighted cumulative mean of bar typical price (H+L+C)/3**, reset each
   session — recorded here as "session VWAP (EW proxy)". This is a fill detail forced by
   the stores, flagged wherever DIAL-T numbers are reported.
3. **Indicator construction (all causal, trailing only):**
   - Supertrend(7,3): standard ratchet bands; ATR(7) is Wilder RMA seeded with the SMA of
     the first 7 true ranges. Computed on the **continuous** per-stock 5-min series
     (state carries across sessions, as on a live chart). Direction +1 = uptrend
     (ST line = final lower band), −1 = downtrend. A flip at bar t = direction(t) ≠
     direction(t−1) between consecutive bars of the continuous series.
   - RSI(14): Wilder, on closes, continuous series; seeded with the SMA of the first
     14 close-changes.
   - Bollinger(20,2): on closes, continuous series; SD is the population SD (ddof=0),
     TradingView convention. %B = (close − lower) / (upper − lower); if upper == lower,
     %B is undefined → no DIAL-R signal that bar.
   - EMA50: span-50 EMA on closes, seeded with the SMA of the first 50 closes,
     continuous series. Slope(6) = (EMA50[t] − EMA50[t−6]) / EMA50[t−6].
   - Session VWAP (EW proxy): cumulative mean of typical price from the session's first
     bar through bar t inclusive.
   - Warm-up: no signal until the continuous series has ≥ 60 bars of history (binds only
     on 2025-01-01, the store's first day).
4. **Signal / entry:** signal evaluated at bar t's close using bars ≤ t only. Entry at the
   next PRESENT bar's open within the same session; the entry bar's stamp must be ≤ 15:10
   (an entry at the 15:15 bar would be at/after square-off — not taken). A flip on the
   day's first bar is valid (prior state is known at its close).
5. **Tradable stock-day:** the day contains the bar stamped 15:10 AND ≥ 30 bars. Otherwise
   the stock-day is NC (no trades), counted. Known NC: 2025-10-21 (Muhurat session,
   13:45–14:40, 12 bars, no 15:10 bar) — all 25 names. Partial days that contain 15:10
   (ITC 2025-01-06, 71 bars; VEDL 2026-04-30, 66 bars) are tradable on their present bars.
6. **Exit fills:** entry price E = entry bar's open. LONG: target = 1.01·E, stop = 0.995·E.
   SHORT: target = 0.99·E, stop = 1.005·E. Bars monitored from the entry bar through the
   15:10 bar inclusive. Within a bar, if both levels lie inside the bar's range the STOP
   fills first (conservative). Gap rule: LONG stop — if the bar opens ≤ stop, fill at the
   open; LONG target — if the bar opens ≥ target, fill at the open; otherwise fill at the
   level. SHORT mirrored. If neither level is hit by the 15:10 bar, square-off at the
   15:10 bar's CLOSE (the price at 15:15). Net per trade: LONG (exit − E)·100 − 40;
   SHORT (E − exit)·100 − 40 (per 100 shares provisional).
7. **Components independent:** DIAL-T and DIAL-R each take their own first signal per
   stock-day; both may trade the same stock-day, even in opposite directions. The combined
   DIAL-Stocks book is the plain union of the two trade sets.
8. **Gate window:** trades are dated by ENTRY day and gated per calendar year over
   Jan 1–Oct 31 (the programme's Jan–Oct convention, matching how the Stock Book itself
   is judged). Halves: H1 = Jan–May, H2 = Jun–Oct. Monthly pace = year total / 10.
   Red month = month net < 0 (a month with no trades nets ₹0, not red).
9. **Placebo:** per series (DIAL-T, DIAL-R, combined) per year, 200 draws, fixed seed
   (20261114). Each draw = the series' real trade count for that year; each placebo trade
   = uniform random tradable stock-day of that year × uniform random entry bar (stamps
   09:20–15:10 present that day) × uniform random side; exit geometry and fill rules
   identical (evaluated on that stock-day's real bars). Percentile = % of draws whose
   total is below the real total. Judged on totals net of the same ₹40/trade.
10. **Timing audit:** by construction the entry bar strictly follows the signal bar and
    every indicator at bar t is a trailing function of bars ≤ t; the build asserts
    entry_stamp > signal_stamp on every trade and reports the assertion.
11. **November CF (descriptive only):** the frozen system run over entry dates
    2026-11-02 – 2026-11-13 (the Stock Book's 9 November trading days: Nov 2,3,4,5,6,9,11,
    12,13). The 14 bars stamped 2026-11-08 (Sunday stub in the store) are not a book
    trading day and fail the tradable rule (no 15:10 bar) → NC, excluded, noted.
