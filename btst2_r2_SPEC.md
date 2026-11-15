# BTST-2 ROUND 2 — SPEC (FROZEN 2026-11-15, before scoring)

Anatomy of BTST-2's largest cell, E0-H2, plus ONE frozen risk filter.
Research only; arms nothing, touches no book/ledger/job. Basis identical
to BTST-2 Round 1: equity cash, LONG only, frozen 25 names, **per 100
shares PROVISIONAL**, ₹40 per completed position, paper only, real
money ₹0. Machinery imported verbatim from `hold_programme_build.py`
(`prep`, `sim`, `score_year`, `stats`) — nothing re-implemented.

## Control (must reproduce before anything else; abort if it fails)

E0-H2 scored exactly as in BTST-2 R1, per year (entries Jan 1–Oct 31;
exits past window end re-marked WMARK):
- 2025: 1,075 trades · net **+₹98,386** · max DD **−₹232,796**
- 2026: 1,075 trades · net **+₹303,058** · max DD **−₹276,472**

## Definitions (frozen)

- **Entry week** = the ISO week (ISO year, ISO week number) of a scored
  trade's entry date. E0 enters all 25 names at each week's first bar,
  so one entry week = one group of (normally 25) trades sharing an ISO
  week. Week net = sum of its trades' nets. Week capital deployed =
  sum over its trades of entry price × 100.
- **Month table** = by ENTRY month (entry date's year-month): trades, net.
- **Halves** = by entry date: H1 = entries Jan 1–May 31, H2 = entries
  Jun 1–Oct 31. Trades and net per half.
- **Return on deployed capital (year)** = year net ÷ SUM of the year's
  weekly deployments × 100 (capital-turnover basis). Average and maximum
  weekly deployment also reported.
- **Best-4-weeks share** = sum of the 4 largest week nets ÷ year net × 100.

## Part A — anatomy (control, per year)

Month table · halves · the 10 worst entry-weeks (ISO week, first entry
date, trades, net) · capital deployed per entry week (average, max) ·
return on deployed capital · best-4-weeks share of the year's net.

## Part B — ONE frozen filter (nothing else changes)

Skip an entry week entirely (all 25 names) if **NIFTY's prior-week
return was worse than −2%**:
- NIFTY daily closes from `results_data/NIFTY50.csv` (2024-01-01 →
  2026-10-28; verified identical to `volrix/nifty_daily_2019_2026.csv`
  on all 514 common days in Oct 2024–Oct 2026).
- Group NIFTY trading days by ISO week; a week's close = its last
  trading day's close. Prior-week return for entry week W =
  close(prior ISO week) ÷ close(the ISO week before it) − 1, where
  "prior ISO week" = the ISO week immediately before W in the NIFTY
  series. Skip W iff that return < −0.02 (strictly).
- If the return cannot be computed (series start), the week is KEPT
  and counted as such.
- The filter decision is keyed on the entry week's ISO week and uses
  only NIFTY closes from weeks strictly before it — no future data.

Report per year, beside the control: weeks skipped (with their ISO
weeks and prior-week returns), trades kept, net, max DD (same
exit-date-ordered equity line as `stats`), total + average deployed
capital of kept weeks, return on deployed capital.

## Deliverables

`btst2_r2_2026-11-15.md` + `btst2_r2_results.json`, built by
`btst2_r2_build.py`.
