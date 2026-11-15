# SARVASETU — Wide-NSE Shadow: FULL October + November-to-date retrospective (scored 2026-11-11)

**This is a RETROSPECTIVE scoring of a shadow built on 11 Nov 2026 — not live forward evidence. The live record starts Thu 2026-11-12.**
Paper only, real money ₹0. Basis: **provisional per 100 shares**, ₹40/trade, frozen SarvaRitu geometries (N4-V3 T150/S080; P2F / P2F-R2 / R2-LOWBAND T125/S050), square-off 15:10.
**Window: Thu 2026-10-01 → Wed 2026-11-11** (the owner's corrected window — the whole of October plus November to date). Seed day Wed 2026-09-30 was fetched for prior-day reactions and is not scored. **Trading days actually scored: 27** of 30 weekdays; no-candle weekdays (market holidays) excluded by the candle data itself: 2026-10-02, 2026-10-20, 2026-11-10.
Universe: 1081 liquid NSE names as fetched 2026-11-11 (`wide_nse_universe_2026-11-11.csv`), applied backwards over the whole window (constituent drift over six weeks is possible in principle — index reviews are semi-annual and none fell inside this window — but the caveat stands).
Event input: the union of the stocks machinery's three contemporaneous event calendars (230 rows after dedupe): the live producer's curated calendar (events from 2026-10-29) + `stock_event_calendar_ext_jan_oct_2026.csv` (built 2026-10-31) + `stock_event_calendar_jan_oct_2026.csv` (built 2026-10-30) — same schema, same reaction convention. The live calendar alone starts Oct 29; Oct 1–28 scored on it alone would show a construction artefact (no event input), not a result. Names without calendar events produce no trades by construction; every universe name's bars were still fetched and evaluated each day (coverage below).

## Window totals — 67 trades · net +30.18 · win rate 44.8%
- October portion (Oct 1–30, 20 scored days): 42 trades · net -4,573.83 · win rate 45.2%
- **November portion (Nov 2–11, 7 scored days): 25 trades · net +4,604.01 · win rate 44.0%**

## Per-day
| Date | Trades | Net ₹ | Win % | Usable bars coverage |
|---|---|---|---|---|
| 2026-10-01 | 0 | +0.00 | 0.0 | 1063/1081 (98.3%) |
| 2026-10-02 | — | — | — | 0/1081 (0.0%) — NO DATA / holiday, not scored |
| 2026-10-05 | 0 | +0.00 | 0.0 | 1064/1081 (98.4%) |
| 2026-10-06 | 0 | +0.00 | 0.0 | 1063/1081 (98.3%) |
| 2026-10-07 | 0 | +0.00 | 0.0 | 1064/1081 (98.4%) |
| 2026-10-08 | 0 | +0.00 | 0.0 | 1063/1081 (98.3%) |
| 2026-10-09 | 1 | +3,192.50 | 100.0 | 1063/1081 (98.3%) |
| 2026-10-12 | 1 | -1,132.45 | 0.0 | 1062/1081 (98.2%) |
| 2026-10-13 | 2 | +1,601.48 | 50.0 | 1063/1081 (98.3%) |
| 2026-10-14 | 1 | +1,610.00 | 100.0 | 1064/1081 (98.4%) |
| 2026-10-15 | 1 | -712.50 | 0.0 | 1064/1081 (98.4%) |
| 2026-10-16 | 1 | +230.21 | 100.0 | 1064/1081 (98.4%) |
| 2026-10-19 | 3 | -750.56 | 33.3 | 1065/1081 (98.5%) |
| 2026-10-20 | — | — | — | 0/1081 (0.0%) — NO DATA / holiday, not scored |
| 2026-10-21 | 4 | -5,702.21 | 75.0 | 1066/1081 (98.6%) |
| 2026-10-22 | 3 | -300.51 | 33.3 | 1067/1081 (98.7%) |
| 2026-10-23 | 2 | +1,726.25 | 100.0 | 1071/1081 (99.1%) |
| 2026-10-26 | 4 | +2,721.79 | 75.0 | 1071/1081 (99.1%) |
| 2026-10-27 | 3 | +1,759.81 | 66.7 | 1071/1081 (99.1%) |
| 2026-10-28 | 5 | -2,314.45 | 40.0 | 1073/1081 (99.3%) |
| 2026-10-29 | 5 | -4,695.50 | 0.0 | 1074/1081 (99.4%) |
| 2026-10-30 | 6 | -1,807.69 | 16.7 | 1074/1081 (99.4%) |
| 2026-11-02 | 5 | +1,433.40 | 40.0 | 1075/1081 (99.4%) |
| 2026-11-03 | 2 | +1,118.02 | 50.0 | 1077/1081 (99.6%) |
| 2026-11-04 | 4 | +1,489.72 | 50.0 | 1079/1081 (99.8%) |
| 2026-11-05 | 4 | -42.21 | 25.0 | 1080/1081 (99.9%) |
| 2026-11-06 | 4 | +559.63 | 50.0 | 1080/1081 (99.9%) |
| 2026-11-09 | 4 | -780.65 | 50.0 | 1080/1081 (99.9%) |
| 2026-11-10 | — | — | — | 0/1081 (0.0%) — NO DATA / holiday, not scored |
| 2026-11-11 | 2 | +826.10 | 50.0 | 1081/1081 (100.0%) |

## Per-component (window)
| Component | Trades | Net ₹ | Win % | November trades | November net ₹ |
|---|---|---|---|---|---|
| N4-V3 | 26 | -4,837.73 | 50.0 | 11 | +1,854.02 |
| P2F | 18 | +1,210.35 | 38.9 | 5 | +1,599.77 |
| P2F-R2 | 18 | +2,816.35 | 38.9 | 7 | +1,802.07 |
| R2-LOWBAND | 5 | +841.21 | 60.0 | 2 | -651.85 |

Best trade: 2026-11-06 N4-V3 TITAN LONG 09:35 @ 4945.1 → 4994.0 (square_off) **+4,850.00**
Worst trade: 2026-10-21 N4-V3 ULTRACEMCO LONG 09:35 @ 10920.0 → 10832.64 (stop) **-8,776.00**

## November delta vs the earlier November-only deliverable
The earlier run (`sarvasetu_november_2026-11-11.md`, live-producer calendar only) reported November as 14 trades · +₹3,433.60. This report's November subtotal uses the merged machinery calendars; the difference is entirely added event coverage, itemised here:
- ADDED 2026-11-02 P2F-R2 UNITDSPR LONG 09:15 @ 1330.0 → 1346.62 (target) +1,622.50 — event carried only by the machinery calendars
- ADDED 2026-11-02 N4-V3 POWERGRID LONG 09:35 @ 269.15 → 267.0 (stop) -255.32 — event carried only by the machinery calendars
- ADDED 2026-11-02 N4-V3 RELIANCE LONG 09:35 @ 1234.6 → 1253.12 (target) +1,811.90 — event carried only by the machinery calendars
- ADDED 2026-11-02 N4-V3 SUNPHARMA SHORT 09:35 @ 1756.8 → 1770.85 (stop) -1,445.44 — event carried only by the machinery calendars
- ADDED 2026-11-03 P2F RELIANCE LONG 09:15 @ 1287.9 → 1304.0 (target) +1,569.87 — event carried only by the machinery calendars
- ADDED 2026-11-04 P2F-R2 RELIANCE LONG 09:15 @ 1301.9 → 1318.17 (target) +1,587.37 — event carried only by the machinery calendars
- ADDED 2026-11-06 N4-V3 BHARTIARTL LONG 09:35 @ 2097.0 → 2080.22 (stop) -1,717.60 — event carried only by the machinery calendars
- ADDED 2026-11-06 N4-V3 M&M LONG 09:35 @ 3241.9 → 3215.96 (stop) -2,633.52 — event carried only by the machinery calendars
- ADDED 2026-11-06 N4-V3 TITAN LONG 09:35 @ 4945.1 → 4994.0 (square_off) +4,850.00 — event carried only by the machinery calendars
- ADDED 2026-11-09 P2F-R2 M&M LONG 09:15 @ 3278.0 → 3261.61 (stop) -1,679.00 — event carried only by the machinery calendars
- ADDED 2026-11-09 P2F-R2 TITAN LONG 09:15 @ 5000.7 → 4975.7 (stop) -2,540.35 — event carried only by the machinery calendars
- Every trade from the earlier run is reproduced unchanged.
- Nov 11 cross-check: the two dry-run legs (KALYANKJIL, TATASTEEL) are reproduced inside this run's Nov 11 scoring.

## Coverage / NOT_COMPUTED notes
A symbol-day is NOT_COMPUTED when it returned < 50 usable 5-min bars. Event-active names in that state (a trade could have been missed) are listed individually:
- None — every event-active name had usable bars on its active days.
- Nov 11 bars come from the Upstox intraday endpoint (the historical endpoint had not published 2026-11-11 candles at scoring time); all other days use the historical minutes/5 endpoint.
- Seed day 2026-09-30 fetched, not scored. Nov 1 was a Sunday.

## Scale reference (never added to the figures above)
The frozen 25-stock SarvaRitu book's own paper log (`stocks_sarvaritu_paper_log.csv`) covers only 2026-11-02 → 2026-11-11 (26 trades) — it holds NO October rows, so no same-source October comparison exists. Its November rows: 26 trades · net +8,391.28 (provisional per 100 shares, EOD whole-book construction incl. the EOD-only sleeves F4 / INV-LONG / INV-ABOVE, which this shadow does not run). The only October book figure on record is the adoption/EOD whole-book October total of +₹56,127.37 (full month, incl. EOD sleeves — a different basis, reference only). Shown for scale only — the two books are never added together.
