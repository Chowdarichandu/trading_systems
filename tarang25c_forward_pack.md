# TARANG-T25-C — FORWARD-PAPER PACK (frozen rules, prepared 2026-11-17)

**Status: PREPARED, NOT STARTED.** This pack exists so
that, on the owner's explicit word, T25-C can begin
forward paper scoring with zero further design work.
Nothing here is scheduled, no cron exists, and the
scorer is run only by hand (or by a future instruction
from the owner). A gate pass earns forward paper only on
the owner's explicit word — Design 25 SPEC S.0.

Basis: equity cash, PROVISIONAL per 100 shares,
₹40/trade, paper only, real money ₹0. No stock options.

## The gate record (Design 25, tarang25_2026-11-17.md)

TARANG-T25-C (GAP-FADE-UP-15) — **PASS, 9 of 9 legs:**

| Leg | 2025 | 2026 |
|---|---|---|
| Net | +₹1,51,307.50 | +₹50,274.68 |
| Trades / win rate | 563 / 38.0% | 548 / 34.9% |
| Gross/trade (levy ₹40) | +₹308.75 | +₹131.74 |
| Placebo percentile | 100.0 | 100.0 |
| Ex-top-3 net | +₹1,21,012.50 | +₹21,004.68 |
| Max drawdown (year) | −₹2,65,368.50 | −₹2,34,740.62 |

Worst month Jan 2026 −₹13,047.30 (bar −₹15,000);
November 2026 slice +₹13,443.47 (42 trades); audits
clean. Direction-flip placebo −₹1,07,542.14 /
−₹98,647.22. Stated plainly in the Design 25 report and
repeated here: the 2026 monthly pace (₹4,570/month) is
below the ₹15,000/month segment floor, and the per-year
drawdowns are large against the nets. The pass is a gate
pass, not a sizing claim.

## Frozen rules — exactly as gated (tarang25_SPEC.md S.2–S.4)

**Universe:** the 127 verified F&O names of Designs
7–25, in the verified-universe list order
(`tarang23_score.NAMES23`). Data: 5-min bars from the
same stores the backtest used (`data/tarang_vol/<SYM>/
spot_5m_vol.csv` via the family loaders). A forward day
must be present in those stores (bars through 15:15) to
be scored.

**Signal (per name-day, after the name's first store
day):**

    gap% = (today's first-bar open / previous trading
            day's last bar close) − 1

The previous trading day is that name's previous day in
the store. A name's first store day produces no
candidate.

**Book rule (T25-C only):** gap% ≥ **+0.015** → one
candidate, **SHORT**. (Up-gaps only; down-gaps and
smaller gaps are not traded by this book.)

**Entry:** the day's first-bar open (bar local 0, the
09:15 bar). The gap is known at the open; no bar beyond
the first is consulted for the signal.

**Exit (the family's one standard exit, unchanged):**

- Disaster stop at **entry × 1.01** (SHORT), stop-first:
  scanning from the entry bar, a bar that opens at or
  above the stop fills at the bar's open; otherwise a
  bar whose high reaches the stop fills at the stop.
- Otherwise exit at the **close of the square-off bar**
  — the day's last bar with timestamp ≤ 15:15.
- Exit reasons: "stop" / "squareoff". There are no other
  exits. No target, no trailing stop (Design 26 WS3
  tests those as research lines only; they are NOT part
  of this frozen book).

**Caps:** at most **10 taken trades per day**; at most
**1 per name-day** (structural — one candidate exists
per name-day). A candidate not taken is simply not
taken; it does not defer.

**Allocation (only binds when a day has > 10
candidates):** rank by

1. **|gap%| DESC** (exact float);
2. **vol_ratio DESC** — vol[first bar] / mean(vol over
   the 20 bars ending at the first bar), 0 if the mean
   is 0 (Design 25's audit found this key decided zero
   cap-boundary slots in the backtest; it is kept for
   definition completeness);
3. **universe order ASC**.

Take the top 10.

**Money:** gross = (exit − entry) × side × 100 shares;
net = gross − ₹40. Win = net > 0.

## The scorer

`tarang25c_scorer.py` (this directory). Usage:

    python3 tarang25c_scorer.py --date YYYY-MM-DD
    python3 tarang25c_scorer.py --date YYYY-MM-DD --json out.json
    python3 tarang25c_scorer.py --selftest

It loads the stored bars through the same family
machinery as the backtest (tarang23 prep/day_ctx,
tarang24 sig_gapw2, tarang23 take_trade, tarang25
allocate25/vol_ratio_at), prints the day's candidates
and taken trades, and — with `--json` — writes them in
the Design 25 trade-row format. `--selftest` runs the
two pre-registered historical days (2025-08-18 and
2026-03-24, both cap-bound 10-trade days) and verifies
the output reproduces the published Design 25 trades
for those dates exactly; the Design 26 report states
the self-test result.

**Forward use (only on the owner's word):** after a
trading day's bars are in the stores, run the scorer for
that date and append the taken trades to the forward
ledger. Until that word is given, the scorer is run for
nothing except its self-test.

## What is NOT in this pack

No scheduler, no cron, no live feed hookup, no order
placement of any kind, no position tracking beyond the
same-day score (every T25-C trade opens and closes the
same day by construction). Design 26's WS3 exit variants
(gap-half target, trailing-after-half) are research
lines reported separately in tarang26_2026-11-17.md;
they do not modify this frozen book.
