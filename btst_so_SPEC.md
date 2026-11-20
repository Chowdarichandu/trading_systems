# BTST-STOCK-OPTIONS (LIQUID-ONLY) — SPEC (FROZEN 2026-11-17, before any scoring)

Owner-raised 2026-11-17 06:40 IST: "options are the one where we get the
profits where we desire — think about it." Context: stock options were closed
after failing vs cash in the near-expiry intraday-hold and far-expiry runs
(2026-11-15) — BUT those runs held the option for the FULL cash hold (up to
60 days; 179/320 near-run positions died at expiry first) and the far run hit
an NC wall (116/130 NCs were contracts not yet trading). Neither isolated the
genuinely liquid underlyings, and neither tested the OVERNIGHT (BTST) hold.
This test is that one fair cell. Research only; paper, real money Rs0;
option BUYING only; mutates nothing running.

## 1. Signals (frozen)

EKAM-DAILY (EKAM-2c) entries exactly as published: rows of
`ekam2c_trades.csv` with book = EKAM2c and entry_date inside Jan 1 – Oct 31
of the year (2025: 74 trades · cash +Rs42,954.60 · 2026: 102 trades · cash
+Rs1,41,328.40 — re-asserted from the CSV before scoring; a mismatch stops
the run). Signal day **t = signal_date**; the BTST exit session is the
trade's entry_date (the next session, by sim2c construction). All EKAM-2c
signals are long -> the options arm buys CALLS only.

## 2. Liquidity qualification (mechanical, applied before any trade scoring)

Candidate universe = the frozen 25 names. Scope fact, recorded not judged:
names outside the 25 (RELIANCE, SBIN, TCS, INFY, ...) carry no EKAM-2c
store-basis signals and cannot enter this test; the rule below decides
among the 25.

For each name x each monthly expiry Jan 2025 – Oct 2026 (22 months):
- Expiry date from the programme's discovery (`stock_options_data/
  expiries.json`, gaps filled by the same probing route as
  `stock_options_fetch.py`). Contract list = the expired-contract list for
  that expiry (programme cache; probed if missing).
- ATM CE = listed CE strike nearest the name's spot daily close (store
  basis) on the last session of the previous month.
- Span = the name's own store-calendar sessions from the first session of
  the expiry month through the expiry date.
- A session counts as TRADED if Upstox serves a daily candle for the ATM CE
  on it (established programme fact: a candle is returned only for days the
  contract traded — the daily-resolution equivalent of "traded bars on the
  session").
- coverage(name) = traded sessions / span sessions, pooled over 22 months.
  A month with no discovered expiry or no contract list counts every span
  session as untraded, with the reason recorded per name.
- volume(name) = median of the daily volume field over all traded days,
  pooled (Upstox volume units, as served; ranking is unit-invariant).

**QUALIFY iff coverage >= 0.90 AND volume rank <= 8 of the 25** (top
tercile). The full 25-row screen table (coverage, volume, rank, verdict,
reject reason) is published in the report. If zero names qualify, nothing
is scored and the screen table IS the result.

## 3. Options arm (per signal on qualifying names)

- Expiry: nearest discovered monthly expiry >= 7 calendar days after t
  (search t's month, then the next two). None -> NC `NO_EXPIRY`.
- Strike: listed CE strike nearest day-t spot daily close (store basis) —
  the programme's established strike-reference convention
  (stock_options_SPEC s.2). This fixes the strike only; the fill is a real
  traded price (s. below). Contract list = the expired list for that
  expiry (the strikes listed for that expiry; no later information is
  used for price, entry or exit).
- Entry: the contract's 5-minute bars on day t (expired-instruments route).
  Entry price = close of the LAST bar starting in 15:00–15:25 (the close
  window). No bar in the window -> NC `NO_TRADE_CLOSE_WINDOW`.
- Exit: the contract's 5-minute bars on the exit session. Exit price =
  close of the FIRST bar starting in 09:15–09:45. No bar in the window but
  bars exist that day -> close of the first bar of the day, flagged
  `LATE_EXIT`. No bar all day -> NC `NO_TRADE_EXIT_DAY`.
- Size: lots = max(1, round(100 / lot_size)); share-equivalent =
  lots x lot_size, printed per trade. All comparisons use the
  per-100-equivalent: net / share-equivalent x 100.
- Cost: **Rs220 per completed options position** — the figure both prior
  stock-options programmes (near + far, 2026-11-15) applied to stock
  options, covering the brokerage+tax round trip; held constant so this
  test is comparable with them.

## 4. Cash control (identical signals — the bar the options arm must beat)

BTST in cash on the same signals: buy 100 shares at the spot 5-minute
close at the option entry bar's timestamp on day t; sell at the spot
5-minute close at the option exit bar's timestamp on the exit session.
Fallbacks (flagged per trade): entry -> store daily close of t; exit ->
store daily open of the exit session. Cost Rs40/trade.
Two lines are reported: FULL (every signal on qualifying names) and
MATCHED (only signals where the options arm filled). **The gate uses
MATCHED** — identical signals, both arms filled; the NC rate (s.6) is the
separate tradability condition.

## 5. Placebo

Each signal shifted +5 sessions: t' = the 5th store session after t for
that name; entry at t' close window, exit the next session, identical
contract machinery (expiry >= 7 days from t', strike nearest t' daily
close, same windows, same cost, per-100 basis). t' or its exit session
beyond the data -> NC `PLACEBO_NO_DATA`. Reported per year with NC count.

## 6. Gate (frozen)

PASS iff, in EACH year separately: options-arm per-100 net (matched set)
> cash-control per-100 net (matched set), AND the options NC rate
(NC / attempted) <= 20%. Any other outcome is reported as measured —
FAIL, with no relabelling. Years are never pooled.

## 7. Reporting (per year, never pooled)

Attempted · NC by reason · trades · net (actual Rs for the lots traded AND
per-100-equivalent) · WR · ex-top-3 (per-100) · best/worst month (per-100,
by signal month) · cash FULL and MATCHED lines · placebo line · spread
reality per trade: underlying % move (spot entry bar -> spot exit bar)
vs option premium % return; aggregates: median underlying move, median
option return, gross option P&L before cost, total cost, matched cash
gross — where the money went, in numbers.

## 8. Data & integrity

Upstox expired-instruments routes only (the programme's route), browser
User-Agent on every call, pacing >= 0.45s, token from the programme's own
store, never printed. **HTTP 429 = hard stop for the attempt**: caches and
checkpoints are kept, unfetched items score as NC `FETCH_MISSING` for this
attempt and are named in the report. All fetches cache under
`btst_so_data/` (programme contract/expiry caches are read, and newly
discovered expiries/contract lists are written back to the shared
programme cache as in prior runs). If historical stock-option bars are
unserved wholesale, the run stops, reports exactly what was served, and
scores nothing — an honest NC beats a fitted number.
