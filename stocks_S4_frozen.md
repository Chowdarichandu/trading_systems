# LINE S4 — FROZEN CELLS (frozen BEFORE any scoring, 2026-10-31)

Equity cash intraday, LONG/SHORT language only. No options, no premiums.
Paper only — real money ₹0, no orders. All figures **provisional per 100
shares**, net = gross − **₹40/trade** cost. Window **Jan–Oct 2026** as
cached (home price cache Oct = 1–28, 18 trading days; ext Oct = 1–30,
20 trading days — each universe scored on the days its cache holds).
Universe: home 25 (data/progressive/) + ext 25 (data/progressive_ext/) =
**pooled 50 primary**, home/ext splits reported.

**CONTROLS-FIRST PROTOCOL (binding):** the timing audit runs in the SAME
run as first scoring, BEFORE any score is printed. If the audit fails,
the run aborts and no number is quoted. Every qualifier below is computed
only from bars at or before its stated timestamp; every entry is strictly
after its qualifier completes (asserted over ALL trades, by bar index
and by timestamp).

**Exit conventions** (programme-standard): within a bar that spans both
stop and target, the STOP fills first. Square-off at the **15:10 bar
close** (if a day lacks a 15:10 bar, the day's last bar close).

---

## Coverage check (done before freezing, result recorded here)

- Volume caches exist for **all 50 stocks** (progressive_vol/ 25 home,
  progressive_vol_ext/ 25 ext), 2026 bars: home 15,300/stock, ext
  15,375/stock, 75 bars/day.
- Price-day sets vs volume-day sets are identical on every shared day;
  the home volume cache holds one extra day (2026-10-29) absent from the
  home price cache — unused (trades exist only on price-cache days).
- Zero-volume bars: only the 15:15 and 15:20 bars on ~62 days
  (Aug onward) — after the 15:10 square-off, so they never enter any
  VWAP used by a signal (signals complete by 15:05). Volume OHLC matches
  price-cache OHLC exactly on sampled days.
- **Verdict: volume is USABLE for Axis B on all 50 stocks.** VWAP uses
  price-cache OHLC (typical price) × volume-cache volume, joined on
  timestamp; the loader asserts per-day bar alignment.

---

## AXIS A — LAST-HOUR MOMENTUM

Qualifier (per stock-day): **day move = close of the 14:30 bar ÷ open of
the 09:15 bar − 1**, computed at the 14:30 bar close (information
complete at 14:30 bar label; entry strictly after).

- move ≥ +1.0% → **LONG**; move ≤ −1.0% → **SHORT**. Otherwise no trade.
- **Entry: 14:35 bar open.** One trade per stock-day per cell.
- Days lacking a 14:30 or 14:35 bar are skipped for Axis A.

| Cell | Direction | Exits |
|---|---|---|
| **A-MOM-SQ** (primary) | with the day move | 15:10 square-off close only |
| **A-MOM-T05** | with the day move | target +0.5% / stop −0.5% (stop-first), else 15:10 |
| **A-FADE-SQ** (CONTROL) | AGAINST the day move | 15:10 square-off close only |

Control read: a real momentum effect must beat its own fade —
A-MOM-SQ net vs A-FADE-SQ net, same qualifier days, same exit style.

## AXIS B — VWAP DEVIATION REVERSION

Intraday VWAP: cumulative from 09:15 over 5-min bars, typical price
(H+L+C)/3, VWAP_t = Σ(tp·vol)/Σvol over bars up to and including bar t
(bars at/before t only — no exceptions).

Scan: from the **11:00 bar** onward (signal bar time in [11:00, 15:05];
entry bar must be ≤ 15:10). **First** bar whose close deviates ≥1.5%
from VWAP at that bar triggers:

| Cell | Trigger | Entry | Target | Stop |
|---|---|---|---|---|
| **B-REV-LONG** | close ≤ VWAP×(1−0.015) | next bar open, LONG | nearer of (signal-bar VWAP level, entry×1.0075) | entry×(1−0.005) |
| **B-REV-SHORT** | close ≥ VWAP×(1.015) | next bar open, SHORT | nearer of (signal-bar VWAP level, entry×0.9925) | entry×(1+0.005) |
| **B-PBO-LONG** (PLACEBO) | close ≤ stale×(1−0.015) | next bar open, LONG | nearer of (stale level, entry×1.0075) | entry×(1−0.005) |
| **B-PBO-SHORT** (PLACEBO) | close ≥ stale×(1.015) | next bar open, SHORT | nearer of (stale level, entry×0.9925) | entry×(1+0.005) |

Frozen interpretation choices (made here, before scoring):
- **Target level = VWAP through the signal bar** — the last VWAP value
  knowable at the moment of entry (entry is at the next bar's open;
  a VWAP including the entry bar's own data would be a leak and is
  forbidden by the protocol).
- **Stale level (placebo)** = the FINAL cumulative VWAP of the previous
  trading day in that stock's price series, carried flat all day.
  Information complete at previous day 15:30 — strictly before any
  placebo entry.
- **Skip rule:** if the entry price is already at/past the target level
  (LONG: entry ≥ level; SHORT: entry ≤ level), the reversion has
  already completed before entry — the trade is skipped and counted.
- Max **1 trade per stock-day per direction-cell** (LONG and SHORT cells
  are separate; both may fire on the same day at different times).
- If Σvol through the signal bar is 0, no signal (cannot occur before
  15:15 per the coverage check; rule frozen anyway).

Placebo read: real intraday VWAP must beat the stale level —
B-REV-LONG vs B-PBO-LONG, B-REV-SHORT vs B-PBO-SHORT, and combined.

---

## GATE (per axis, all legs required for a candidate)

1. Pooled Jan–May net > 0 **AND** pooled Jun–Oct net > 0.
2. Pooled breadth ≥ **35/50** stocks net-positive.
3. Pooled October net > 0.
4. Timing audit clean (0 violations over all trades in the axis).
5. Control beaten — Axis A: A-MOM-SQ > A-FADE-SQ. Axis B: each REV cell
   beats its PBO counterpart AND combined REV > combined PBO.

If an axis passes: freeze its passing configuration in
`stocks_S4_candidate_spec.md` with December fresh-window judging
(December 2026 fresh data, rules verbatim: candidate stands if
December pooled net > 0 with both December halves > 0; dies if
December pooled net < 0; otherwise extends to January).
If no axis passes: **no candidate**, stated plainly.

## Reporting (every cell, pass or fail)

Trades, net, win %, expectancy/trade, Jan–May, Jun–Oct, October,
home/ext split, breadth (x/50), best-5 / worst-5 stocks, direction
split (Axis A: up-move LONGs vs down-move SHORTs; Axis B: by cell),
exit-reason mix. Trade dumps: `stocks_S4_<cell>_trades.csv` with
qualifier, info-complete timestamp and entry timestamp on every row.
