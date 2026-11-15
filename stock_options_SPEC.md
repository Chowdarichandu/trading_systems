# STOCK OPTIONS — SPEC (FROZEN 2026-11-15, before any premium fetch or scoring)

Owner's order 2026-11-15: work on stock options. Question: do the proven
stock signals make more or less money as BOUGHT stock options than as cash?

OWNER CORRECTION 2026-11-15 11:03 (supersedes the 10:45 follow-up):
source (c) TRIO Stock Book is REMOVED from this programme entirely.
The owner's rule: TRIO and EKAM are separate entities and stock options
is its own separate entity — do not mix TRIO into it. The programme is
sources (a) and (b) only. (No (c) fetch or scoring was ever run; the
(c) text below is struck through by this correction and is void.)

Research only. Arms nothing. OPTION BUYING ONLY — no selling, ever.
Paper only, real money Rs0. Judged per source, per year, never pooled.

## 1. Signal sources (frozen builds reused — not redesigned)

(a) EKAM-DAILY 2c — trades from `ekam2c_trades.csv`, book = EKAM2c
    (BB band-return + RSI oversold turn-up incl. the 2c RSI-upgrade rule).
    All entries LONG. Window counts: 2025 = 74 trades, 2026 = 102 trades.
    Published cash lines: 2025 +Rs42,954.60 / 2026 +Rs1,41,328.40
    (per 100 shares, Rs40/trade).

(b) HOLD L35-H15 — trades from `hold_programme_r2_best_cell_trades.csv`,
    window rows only (NOV rows excluded). All entries LONG.
    Window counts: 2025 = 83 trades, 2026 = 103 trades.
    Published cash lines: 2025 +Rs42,163 / 2026 +Rs83,963
    (per 100 shares, Rs40/trade).

(c) [VOID — removed by owner correction 2026-11-15 11:03] STOCK BOOK
    (TRIO's stocks line; adopted Variant C book) — full-detail
    trades reconstructed from the frozen engine (stocks_engine_r9_ingredients
    + the adoptC construction), VERIFIED row-for-row against
    `stocks_engine_adoptedC_book{2025,2026}_trades.csv` on
    (comp, date, stock, dir, entry_time, net) and on the Jan-Oct totals.
    Window counts: 2025 = 1,064 trades, 2026 = 1,363 trades.
    Published cash lines: 2025 +Rs1,19,813.44 / 2026 +Rs2,47,178.79
    (per 100 shares, Rs40/trade).
    Direction: LONG entries buy a CE, SHORT entries buy a PE.
    Components WITH short entries: F4, N4-V3, P2F, P2F-R2, R2-LOWBAND, REXP.
    Long-only components: GAP-FADE, INV-ABOVE, INV-LONG, INV-R3, NE-REV-NU.

Universe for all sources: the frozen 25 names (ASTRAL BDL GLENMARK GODREJCP
HDFCBANK HINDALCO HINDCOPPER HINDUNILVR HINDZINC INDUSTOWER IRCTC ITC
KALYANKJIL NATIONALUM NHPC NTPC OBEROIRLTY OIL PFC RECLTD TATASTEEL
TVSMOTOR UNITDSPR VEDL WIPRO).
Windows: entries dated 1 Jan – 31 Oct of 2025 and of 2026, per year.

## 2. Contract selection

Expiry (all sources): the stock's nearest monthly/weekly expiry, from the
Upstox expired-instruments contract listing, with
expiry_date − entry_date >= 5 calendar days. (Stock options are monthly in
practice; the listing decides.)

Strike:
- (a)/(b): the listed strike nearest the entry-day CLOSE of the underlying
  (local daily store `data/sarvaritu_fwd/{sym}/spot_daily.csv`). Tie ->
  lower strike.
- (c): the listed strike nearest the cash ENTRY PRICE. Tie -> lower strike.

Type: CE for LONG entries, PE for SHORT entries (source (c) only).

Lot size: taken from the expired-contract record for the chosen contract;
stated per trade in the output. If the record carries no lot size, the trade
is NC NO_LOTSIZE.

## 3. Entry / exit premium (mirrors the cash trade exactly)

Premium data: Upstox expired-instruments route only
(/v2/expired-instruments/option/contract +
/v2/expired-instruments/historical-candle), browser User-Agent header on
every call, token read from `upstox_refresh/.env` and never printed/logged.
Disk cache under `stock_options_data/`; every response cached before use.

(a)/(b) — daily candles of the chosen contract:
- Entry: premium OPEN on the cash entry_date.
- Exit, by the cash trade's own exit kind, on the cash exit_date:
  - SIGNAL-BB / SIGNAL-RSI / TIME (cash exits at the open) -> premium OPEN.
  - FORCED (cash marks at the close) -> premium CLOSE.
  - HOLD (b) (cash exits at the day-15 close) -> premium CLOSE.
  - WMARK (b) (cash marks at the window-end close) -> premium CLOSE on the
    mark date (= exit_date in the trade list).
  - CAP (cash exits intraday when the underlying touches entry x 1.10) ->
    the first 5-minute bar on exit_date whose underlying spot high
    (local store `data/sarvaritu_fwd/{sym}/spot_5m.csv`) reaches the level;
    exit = that bar's premium CLOSE from 5-minute premium candles.
    If 5-minute premium candles are unavailable for that contract-day,
    exit = premium daily CLOSE on exit_date, labelled CAP_CLOSE.
- Expiry truncation: if the contract expiry is BEFORE the effective exit
  date, the position exits at the premium CLOSE on the expiry date,
  exit_kind = EXPIRY. (An expired contract cannot be held.)

(c) — 5-minute premium candles of the chosen contract on the trade day:
- Entry: premium OPEN of the 5-minute bar at the cash entry_time.
- Exit: premium CLOSE of the 5-minute bar at the cash exit_time.
- The Stock Book is intraday: entry and exit are the same day, so no
  expiry-truncation case arises (expiry is >= 5 days out by construction).

## 4. NC rules (counted and listed, never substituted, never estimated)

- NO_OPTIONS: the name has no expired option contracts listed for the
  needed expiry (no F&O / not listed in that period).
- NO_CONTRACT: listing exists but no strike/expiry satisfies s.2.
- NO_ENTRY_CANDLE (a)/(b) / NO_ENTRY_BAR (c): no premium candle/bar on the
  entry date/bar. No shifting to a later day/bar — the timing is the trade.
- NO_EXIT_CANDLE: no premium candle on or before the required exit date
  after entry (see stale rule) / none at all in the holding span.
- EXIT_STALE (scored, labelled — not NC): exit candle missing on the exact
  exit date; the last available candle on/before that date (and on/after
  entry) is used and its actual date recorded. For (c): the last premium
  bar before the exit bar on the same day, labelled EXIT_STALE_BAR; if no
  bar exists at/after entry that day -> NC NO_EXIT_BAR.
- RATE_LIMITED: HTTP 429 stops the fetch attempt immediately (s.5); every
  trade whose data was not yet fetched is NC RATE_LIMITED.
- NO_LOTSIZE: contract record carries no lot size (s.2).

## 5. Rate-limit law

Pacing >= 0.4 s between API calls. On HTTP 429: hard-stop that fetch
attempt — no retry, no route switch inside the attempt. What is already
cached stays valid; the rest is NC RATE_LIMITED for that attempt. A later
gentle run is a new attempt and may fill cache misses only.

## 6. Money

Cost Rs220 per completed option position, all sources, labelled.
Per-trade option net (per 1 lot) = (exit_premium − entry_premium) x lot_size
− 220 for CE; for PE (source (c) shorts): (exit_premium − entry_premium)
x lot_size − 220 (a bought put gains when the premium rises — same formula;
direction lives in the contract choice, not the arithmetic).
Per-100-shares equivalent = net_per_lot / lot_size x 100.
WR = share of scored trades with net > 0. Halves: Jan–Jun / Jul–Oct by
entry date, nets of scored trades, required per source per year.

## 7. Reporting (deliverables)

`stock_options_2026-11-15.md` + `stock_options_results.json` +
`stock_options_trades.csv`. Per source per year: option trades scored, NC
count by reason, net per lot, per-100-shares equivalent, WR, best/worst
trade, halves; beside it the published cash line. One closing line per
source: options vs cash, which made more (on the per-100 equivalent).

## 7b. [VOID — removed by owner correction 2026-11-15 11:03] Addendum
(2026-11-15, recorded at freeze time — before any premium
fetch or scoring): source (c) exit-detail recovery

The frozen Stock Book dumps carry only (comp, date, stock, dir,
entry_time, net) — no exit_time or prices; the engine's book layer holds
nothing richer (verified 2026-11-15). Source (c)'s exit moment is
therefore recovered as follows, or not at all:
- For each component-year sleeve, candidate component-generator trade
  files are matched on (date, stock, dir, entry_time, net). A sleeve is
  usable only if the match is UNIQUE and COMPLETE: every book row of
  that sleeve matched exactly once, sleeve totals exact.
- A sleeve that fails full verification is NC NO_EXIT_DETAIL in full —
  never partially mixed, never a guessed variant. Individual rows
  unmatched inside an otherwise verified sleeve are NC NO_EXIT_DETAIL.
- The NC share per component is reported plainly (owner's follow-up
  order, 2026-11-15 10:45: score what is feasible, report the NC share,
  do not silently narrow the universe).

## 8. Data-status note at freeze time

At freeze time (2026-11-15) the stored Upstox access token is expired
(JWT exp 2026-11-14 22:00 IST; profile check returns 401). The premium
fetch in s.3–s.5 runs unchanged as soon as a valid token is present in
`upstox_refresh/.env` (the workspace chain refreshes it at 03:45 IST on
weekdays). No rule above depends on when the fetch runs.
