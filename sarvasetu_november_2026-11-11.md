# SARVASETU — Wide-NSE Shadow: November 2026 retrospective (scored 2026-11-11)

**This is a RETROSPECTIVE scoring of a shadow built on 11 Nov 2026 — not live forward evidence. The live record starts Thu 2026-11-12.**
Paper only, real money ₹0. Basis: **provisional per 100 shares**, ₹40/trade, frozen SarvaRitu geometries (N4-V3 T150/S080; P2F / P2F-R2 / R2-LOWBAND T125/S050), square-off 15:10.
Universe: 1081 liquid NSE names as fetched 2026-11-11 (`wide_nse_universe_2026-11-11.csv`), applied backwards over Nov 2–11 (constituent drift over 7 trading days is negligible; the caveat stands).
Event-calendar coverage for Nov 2–11 is the curated 25-name SarvaRitu calendar — the only event source retrievable for those dates (NSE event calendar is forward-only; BSE API / Moneycontrol blocked from this network). Names without calendar events produce no trades by construction; every universe name's bars were still fetched and evaluated each day (coverage below).

## Totals — 14 trades · net +3,433.60 · win rate 42.9%

## Per-day
| Date | Trades | Net ₹ | Win % | Usable bars coverage |
|---|---|---|---|---|
| 2026-11-02 | 1 | -300.24 | 0.0 | 1075/1081 (99.4%) |
| 2026-11-03 | 1 | -451.85 | 0.0 | 1077/1081 (99.6%) |
| 2026-11-04 | 3 | -97.65 | 33.3 | 1079/1081 (99.8%) |
| 2026-11-05 | 4 | -42.21 | 25.0 | 1080/1081 (99.9%) |
| 2026-11-06 | 1 | +60.75 | 100.0 | 1080/1081 (99.9%) |
| 2026-11-09 | 2 | +3,438.70 | 100.0 | 1080/1081 (99.9%) |
| 2026-11-11 | 2 | +826.10 | 50.0 | 0/1081 (0.0%) |

## Per-component
| Component | Trades | Net ₹ | Win % |
|---|---|---|---|
| N4-V3 | 5 | +1,244.00 | 60.0 |
| P2F | 4 | +29.90 | 50.0 |
| P2F-R2 | 3 | +2,811.55 | 33.3 |
| R2-LOWBAND | 2 | -651.85 | 0.0 |

Best trade: 2026-11-09 P2F-R2 GLENMARK LONG 09:15 @ 2590.0 → 2622.38 (target) **+3,197.50**
Worst trade: 2026-11-03 R2-LOWBAND GODREJCP SHORT 09:15 @ 823.7 → 827.82 (stop) **-451.85**

## Coverage / NOT_COMPUTED notes
A symbol-day is NOT_COMPUTED when it returned < 50 usable 5-min bars (no trade can be scored for it that day). Non-event names in that state miss nothing by construction; event-active names in that state are listed here individually:
- 2026-11-11: NOT_COMPUTED (event-active, unusable bars): KALYANKJIL, TATASTEEL
- Nov 11 leg taken from the dry-run log (evaluated on the intraday endpoint's completed bars). A retrospective re-score of Nov 11 was NOT POSSIBLE at scoring time: the v3 historical endpoint had not yet published 2026-11-11 candles (the same publication lag that blocked the index shadow scorer today), so Nov 11 coverage above reads 0 by that route — the dry-run leg stands as the day's record.
- Nov 10: market holiday (Diwali-Balipratipada) — no run. Nov 1: Sunday — no run.

## Scale reference (never added to the figures above)
The frozen 25-stock SarvaRitu book's own November book net over the same days (Nov 2–11) is **+₹8,391.28** over its trades (provisional per 100 shares, EOD construction incl. the EOD-only sleeves F4 / INV-LONG / INV-ABOVE, which this shadow does not run). Shown for scale only — the two books are never added together.
