# SMALL TUNES — VWAP × EMA CROSSOVER · STOCKS intraday · SPEC (frozen 2026-11-14, before scoring)

Owner's correction (2026-11-14 15:50): start from the rules traders actually use — buy above
VWAP, EMA crossovers — small turns, one dial at a time. This run tunes ONLY those dials.
Research only — changes no running book, ledger or job. Separate from the Stocks Parameter
Atlas (parallel run); no shared files.
Basis: equity cash intraday · frozen 25-name Stock Book watchlist · **per 100 shares
PROVISIONAL** · ₹40/trade · paper only, real money ₹0.
Frozen 25: ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC
INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL
TVSMOTOR UNITDSPR VEDL WIPRO.

## DATA / FILL DETAILS (mirrors the DIAL-Stocks conventions exactly)

1. **Store:** `data/sarvaritu_fwd/<SYM>/spot_5m.csv` (timestamp, open, high, low, close) —
   the forward store the Stock Book runs maintain; extends to 2026-11-13.
2. **⚠ VWAP DISCLOSURE:** the persisted stock stores carry **no volume**, so session VWAP is
   the **equal-weighted cumulative mean of bar typical price (H+L+C)/3**, reset each session
   — "session VWAP (EW proxy)", the same forced basis as DIAL-Stocks. Every VWAP number in
   this run is on that basis.
3. **EMA construction:** span EMA on closes, seeded with the SMA of the first `span` closes,
   computed on the **continuous** per-stock 5-min series (state carries across sessions, as
   on a live chart) — identical to DIAL-Stocks' `ema_series`.
4. **Warm-up:** no signal until the continuous series has ≥ 60 bars of history including the
   signal bar (binds only at the very start of 2025).
5. **Tradable stock-day:** contains the bar stamped 15:10 AND ≥ 30 bars; otherwise NC,
   counted, never traded. (Known NC: 2025-10-21 Muhurat, all 25 names; the 2026-11-08
   Sunday stub in November.)
6. **Signal / entry:** signal evaluated at a completed bar's close using bars ≤ t only.
   Entry at the NEXT present bar's open within the same session; entry bar stamp ≤ 15:10.
   Timing audit asserts entry stamp > signal stamp on every trade.
7. **Exit monitoring:** entry bar through the 15:10 bar inclusive; if no exit triggers,
   square-off at the 15:10 bar's CLOSE (the 15:15 price). Within a bar, a stop fills before
   a target; a gap through a level fills at the bar's open (DIAL conventions).
8. **Net per trade:** LONG (exit − entry)·100 − 40; SHORT (entry − exit)·100 − 40.
   WR = share of trades with net > 0.

## THE RULES (per stock; first fully-qualifying signal per stock per day)

Bands: VWAP_up(t) = VWAP(t)·(1+b), VWAP_dn(t) = VWAP(t)·(1−b), b = the buffer dial.

- **Rule A — VWAP cross.** LONG at bar t (t ≥ 2nd bar of the session) when
  close(t−1) ≤ VWAP_up(t−1) and close(t) > VWAP_up(t); SHORT mirrored on VWAP_dn.
- **Rule B — EMA cross.** LONG at bar t when EMA_fast crosses up through EMA_slow at t
  (fast(t−1) ≤ slow(t−1), fast(t) > slow(t), continuous series — the previous bar may be
  the prior session's last bar); SHORT mirrored.
- **Rule C — EMA cross + VWAP side.** Rule B's cross at bar t AND the cross bar closes on
  the matching VWAP side beyond the buffer: LONG needs close(t) > VWAP_up(t);
  SHORT needs close(t) < VWAP_dn(t).
- **Rule C2 — VWAP reclaim with EMA alignment.** Rule A's cross at bar t AND the EMA pair
  is already aligned at t: LONG needs EMA_fast(t) > EMA_slow(t); SHORT mirrored.

## THE SMALL TUNES (dials — each row of the grid is one dial setting; neighbours differ by one dial)

1. **EMA pair** (Rules B, C, C2): (5,20), (9,21), (13,34), (20,50).
2. **VWAP hold** (Rules A, C2 only): 0 vs 1 confirming bar — with hold = 1, the bar after
   the cross must also close on the crossed side of the buffered band, else the cross is
   void and scanning continues to the next cross that day. Entry = open of the bar after
   the last confirmation bar. (Rule C takes no hold: its condition is on the cross bar.)
3. **VWAP buffer** (Rules A, C, C2): 0 / 0.05% / 0.10%.
4. **Exit** (all rules): X1 target +0.8% / stop −0.4% · X2 target +1.0% / stop −0.5% ·
   X3 exit at the close of the first bar whose close is back across VWAP (LONG: close <
   VWAP; SHORT: close > VWAP), hard stop −0.75% · X4 exit at the close of the first bar
   where the EMA pair crosses opposite, hard stop −0.75%. X3/X4 monitor from the entry bar;
   the hard stop is intrabar and precedes the same bar's close exit. X4 uses the row's own
   EMA pair; for Rule A (no pair) X4 uses (9,21).

Grid: A = hold(2) × buffer(3) × exit(4) = 24 rows · B = pair(4) × exit(4) = 16 rows ·
C = pair(4) × buffer(3) × exit(4) = 48 rows · C2 = pair(4) × hold(2) × buffer(3) × exit(4)
= 96 rows. 184 rows total.

## FREQUENCY (frozen)

At most **1 trade per stock per day** (the first fully-qualifying signal) AND at most
**5 trades per day across the list**, per row independently: the day's candidates are
ordered by (signal bar stamp, entry bar stamp, symbol A→Z) — earliest signals first — and
the first 5 are taken. Selection uses times only, never outcomes.

## REPORTING (frozen)

- Per year — **2025 and 2026 separately, never pooled**: for every row, Jan–Jun,
  Jul–Oct and full Jan–Oct (entry-date basis): trades, net, WR.
- **Best row** per rule per year = highest full Jan–Oct net (ties: higher WR, then earlier
  dial order).
- **Placebo:** random-entry ONLY on the best full-year row per rule per year — 200 draws,
  seed 20261114; each draw = the row's real Jan–Oct trade count for that year, each placebo
  trade = uniform random tradable stock-day of that year × uniform random entry bar
  (stamps 09:20–15:10 present that day) × uniform random side, exited with the row's own
  exit rule on that stock-day's real bars. Percentile = % of draws whose total is below
  the real total, reported plainly.
- **November CF (descriptive only):** each rule's best row (selected on 2026 Jan–Oct) run
  over entry dates 2026-11-02 – 2026-11-13 (the 9 book trading days: Nov 2,3,4,5,6,9,11,
  12,13). Never used to select anything.
