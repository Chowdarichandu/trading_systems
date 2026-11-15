# INDICATOR PARAMETER ATLAS — STOCKS · SPEC (FROZEN 2026-11-14, before scoring)

Programme: DIAL (registry `dial_programme.md`). Segment: **Stocks**. Owner's order
2026-11-14 15:43: tune the top indicators and their value parameters, with entry and exit
defined, even for long term.
Basis: equity cash · frozen 25-name Stock Book watchlist · **per 100 shares PROVISIONAL** ·
₹40/trade · paper only, real money ₹0. Judged PER YEAR (2025, 2026), never pooled.
STANDALONE research — no book, ledger or job is touched. The Round 2 frequency test runs
separately and is NOT duplicated here; this atlas is parameter tuning WITH frequency
discipline built in.

Frozen 25: ASTRAL BDL GLENMARK GODREJCP HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC
INDUSTOWER IRCTC ITC KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL
TVSMOTOR UNITDSPR VEDL WIPRO.

## SHARED CONVENTIONS

- Indicator constructions are Round 1's (`dial_stocks_build.py`), causal/trailing only:
  EMA = SMA-seeded span EMA; RSI = Wilder; Bollinger = window mean ± k·population-SD on
  closes; Supertrend = standard ratchet, Wilder-RMA ATR SMA-seeded; MACD = EMA(fast) −
  EMA(slow) with SMA-seeded span EMA of the MACD line as signal; ADX(14) = Wilder
  (SMA-seeded, then Wilder smoothing); Donchian(p) at bar t = max high / min low of the
  prior p bars EXCLUDING bar t. All computed on the CONTINUOUS per-stock series (state
  carries across sessions, as on a live chart).
- A signal is evaluated at a bar's CLOSE from bars ≤ that bar. Entry is the next present
  bar's open in the same session (Part A) / next session's open (Part B).
- Timing audit: every Part A trade asserts entry bar strictly after signal bar; every
  Part B trade asserts entry date strictly after signal date.
- No cherry-picking: every grid row is reported; only ROBUST rows are SELECTED.

# PART A — INTRADAY (5-min)

## A.1 Data and fills (Round 1 verbatim)
Store `data/sarvaritu_fwd/<SYM>/spot_5m.csv`. Tradable stock-day = contains the 15:10 bar
AND ≥ 30 bars, else NC (counted). Session VWAP = equal-weighted cumulative mean of bar
typical price (stores carry no volume — disclosed EW proxy, as Round 1). Signal bars need
≥ 60 bars of continuous history and every series used defined (non-NaN) at t and t−1.
Entry bar stamp ≤ 15:10. Fixed-% exits: monitored entry bar → 15:10 bar inclusive;
stop-first on same-bar overlap; gap-through fills at the open; otherwise fill at the
level; unfilled → square-off at the 15:10 bar's CLOSE. Net = side·(exit−entry)·100 − 40.

## A.2 Frequency discipline (frozen — the atlas's answer to Round 1's churn)
Per config (family × parameters × ADX level): per stock-day take the FIRST qualifying
signal only (≤ 1 candidate per stock per day). Across the watchlist, per day, rank that
day's candidates by EXTREMITY (defined per family below; ties → earlier signal stamp,
then symbol A–Z) and take AT MOST 5 trades per day. The cap governs entries only (a FLIP
exit may be triggered by a later same-day signal that was not itself entered).

## A.3 Families, parameters, entry rules, extremity
Trend families take the ADX(14) filter at levels {none, 20, 25} (signal bar requires
ADX(t) ≥ level) and all four exits. Reversion families take no ADX and exits X1–X3 only.

1. **EMA-X** — EMA cross (9,21) / (13,34) / (20,50) WITH the VWAP-proxy side condition:
   fast EMA crosses above slow AND close > session VWAP-proxy → LONG; cross below AND
   close < VWAP-proxy → SHORT. Extremity = |EMAfast − EMAslow| / close at signal bar.
2. **ST** — Supertrend flip, period {7, 10, 14} × mult {2, 3, 4}: direction change at bar
   close → LONG on flip to +1, SHORT on flip to −1 (no VWAP condition in the atlas).
   Extremity = |close − Supertrend line| / close.
3. **RSI-M** — RSI momentum, period {7, 14, 21}: RSI crosses up through 50 → LONG;
   crosses down through 50 → SHORT. Extremity = |RSI − 50| at signal bar.
4. **MACD** — (8,21,5) / (12,26,9) / (19,39,9): MACD line crosses above signal → LONG;
   below → SHORT. Extremity = |MACD − signal| / close.
5. **BB-BO** — Bollinger breakout, window {14, 20, 30} × sd {1.5, 2, 2.5}: close crosses
   above upper band → LONG; below lower band → SHORT. Extremity = band penetration
   |close − band| / close.
6. **DC** — Donchian breakout, period {10, 20, 55}: close > prior-period high → LONG;
   close < prior-period low → SHORT. Extremity = |close − channel edge| / close.
7. **RSI-R** — RSI reversion, period {7, 14, 21} × threshold pairs (25,75) / (30,70) /
   (35,65): LONG when RSI crosses back UP through the low threshold after having been at
   or below it; SHORT mirror at the high threshold. Extremity = excursion depth beyond
   the threshold reached during that excursion (low − min RSI, resp. max RSI − high).
8. **BB-R** — Bollinger reversion, window {14, 20, 30} × sd {1.5, 2, 2.5}: LONG when
   close crosses back up to ≥ lower band after a close below it; SHORT mirror at the
   upper band. Extremity = deepest band penetration during the excursion, % of close.

## A.4 Exits (frozen)
- **X1** +0.8% / −0.4% · **X2** +1.0% / −0.5% · **X3** +1.5% / −0.75% (target/stop on
  entry price, direction-mirrored), square-off 15:15 (= 15:10 bar close).
- **FLIP** (trend families only): hold until the first later same-day bar at whose close
  the SAME config's opposite-direction signal condition fires (any such bar on that
  stock-day, entered or not) → exit at that bar's CLOSE; hard stop −0.75% monitored
  bar-by-bar from the entry bar (gap-through at open, else at the level; stop beats a
  same-bar-close flip); neither → square-off at the 15:10 close.

## A.5 Windows and robustness (frozen)
Trades dated by entry day. Per year: **Discovery = Jan 1–Jun 30; Validation = Jul 1–
Oct 31.** A config is **ROBUST in a year** iff ALL hold:
- discovery total > 0 AND validation total > 0;
- ≥ 2 one-step neighbours with validation total > 0 — neighbours = same-family configs
  differing by exactly one grid step in exactly one coordinate (each indicator parameter,
  the ADX level, the exit in the order X1<X2<X3<FLIP), same year;
- validation ex-top-3 > 0 (validation total minus its 3 largest trade nets);
- validation random-entry placebo ≥ 95th percentile at the same frequency: 200 draws
  (seed 20261115), each draw = the config's validation trade count, each placebo trade =
  uniform random tradable stock-day in the validation window × uniform random entry bar
  (stamps 09:20–15:10 present that day) × uniform random side, exited with the config's
  exit geometry (FLIP configs: −0.75% hard stop + ride to the 15:10 close), net of ₹40;
- validation pace = validation total / 4 ≥ ₹7,500/mo (2026) / ₹5,000/mo (2025);
- ≤ 1 red month inside validation (Jul/Aug/Sep/Oct month nets; a no-trade month = ₹0,
  not red).
**Family PASS = ONE single config (parameters + ADX + exit) ROBUST in BOTH years.**
Configs robust in one year only are reported as ONE-YEAR evidence, NOT SELECTED.
November CF: only for a PASS config — that exact config over entry dates 2026-11-02–13,
descriptive, no gate. If no family passes, no CF is produced and that is stated.

# PART B — LONG TERM (daily candles, swing)

## B.1 Data
`data/sarvaritu_fwd/<SYM>/spot_daily.csv` (2024-10-01 → 2026-11-13; verified to match the
5-min store's aggregation bar-for-bar on a sampled day). The Oct–Dec 2024 bars are
warm-up only. Scored windows: trades whose ENTRY date falls in Jan 1–Oct 31 of 2025 resp.
2026, attributed to that year. Exits are followed past Oct 31 until the exit rule fires
or the data ends (2026-11-13); a position still open at data end is closed at the last
close and flagged FORCED. LONG ONLY throughout (equity cash). One open position per name
at a time; names independent (each trade = 100 shares of one name); no re-entry while a
position in that name is open. ₹40 per completed trade.

## B.2 Fills
Signal at day t close → entry at day t+1 open. Native close-signal exits at day t close
→ exit at day t+1 open. Price-level exits (the RSI-R +10% cap, trailing stops) are
evaluated intraday on the day's OHLC: gap-through at the open, else at the level.
Per-day priority when overlays are active: (1) time-stop at the day's open (if the day
is ≥ 60 trading days after the entry day and the position is still open at that open);
(2) trailing stop during the day; (3) native exit signal at the day's close.

## B.3 Systems (native exits)
1. **EMA50-X / EMA100-X / EMA200-X** — entry: close crosses above EMA(n); exit: close
   crosses below EMA(n).
2. **GCROSS** — EMA(50,200): entry on golden cross (EMA50 crosses above EMA200); exit
   on death cross. (EMA200 is SMA-seeded on the daily series and first defined ~Jul 2025;
   the 2025 window is correspondingly short — measured, not patched.)
3. **RSI50** — RSI(14): entry on cross up through 50; exit on cross down through 50.
4. **RSI-REV** — RSI(14): entry on cross back up through 30 after RSI ≤ 30; exit at the
   first close with RSI ≥ 70 (→ next open) or price +10% from entry (intraday level),
   whichever first.
5. **MACD-D** — MACD(12,26,9): entry on signal cross up; exit on signal cross down.
6. **ST-D** — Supertrend(10,3) daily: entry on flip to +1; exit on flip to −1.
7. **BB-REV-D** — Bollinger(20,2) daily: entry when close is back ≥ lower band after a
   close below it; exit at the first close ≥ middle band (→ next open).

## B.4 Exit overlays (each scored separately, per system)
BASE (native only) · TRAIL2 (native + trailing stop = highest close since entry −
2×ATR(14)) · TRAIL3 (same, 3×ATR(14)) · TIME60 (native + 60-trading-day time stop).
Trailing stop, frozen mechanics: state = highest close and ATR(14) (Wilder, daily) as of
the PRIOR day's close; today's stop = highest close − k·ATR; if today's open ≤ stop →
exit at open; elif today's low ≤ stop → exit at stop. State updates after each day.

## B.5 Reporting and verdict (frozen)
Per system × overlay, per year: trades, total (after ₹40/trade), WR, avg hold in trading
days (entry day → exit day in that name's series), worst trade; plus the max drawdown
(₹, peak-to-trough) of the combined 2025+2026 equity curve of closed trades ordered by
exit date. **COUNTED (a pass) = total positive in BOTH years AND ≥ 10 trades in EACH
year.** Anything else is reported as measured — NOT SELECTED.
