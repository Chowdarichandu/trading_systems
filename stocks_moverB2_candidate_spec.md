# MOVER-B2 — CANDIDATE SPEC (frozen 2026-10-31)

**Status: CANDIDATE for a fresh window. NOT adopted. In-sample
tuned (Jan–Oct 2026) under the frozen family list in
`stocks_moverB2_frozen.md`; full results in
`stocks_moverB2_report.md`.**

Equity cash intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders, real money ₹0. Every rupee
figure provisional per 100 shares; net = gross − ₹40/trade flat.

## The rule (complete — this spec is self-contained)

Universe: the pooled 50 stocks (25 home watchlist + 25 ext
large caps), each scored on its own 5-min candles.

For each stock, each trading day:

1. **Pre-move measurement at 10:30.** Pre-move = (close of the
   last 5-min bar before 10:30) ÷ (open of the day's first bar)
   − 1. If |pre-move| < 1.0%, the stock-day does not qualify —
   no trades.
2. On a qualifying stock-day, take the frozen V5 re-entry signal
   stream for that stock-day (home: `stocks_equity_reentry.py`
   heads; ext: `stocks_equity_reentry_ext.py` heads). **Discard
   the first signal of the day entirely** — no trade, no cost.
3. Trade the **next** signal, in **whatever direction** the
   stream gives (LONG or SHORT). Entry = the open of the bar
   after the signal bar.
4. Exits (T125): target **+1.25%**, stop **−0.5%**, stop checked
   before target within a bar, otherwise square-off at the
   15:10 bar's close.
5. After an exit, the signal search restarts at the exit bar,
   and **one further re-entry** is allowed if another signal
   occurs (chain cap **2 trades** per stock-day). After a
   discard or a blocked signal, the search restarts at the
   signal bar + 1.
6. No ADR, event, direction, timing or per-stock filters. Net
   per trade = gross − ₹40, per 100 shares. The tradable unit
   is the stock-day **chain**.

The ONLY difference from MOVER-B is step 1's measurement time:
**10:30 instead of 10:15.** (MOVER-B itself differed from
MOVER-A only by 10:15 instead of 10:00.)

## In-sample record (Jan–Oct 2026, Oct = 1–28) — tuned, NOT fresh

- Pooled 50: **1,212 chains, 1,835 trades, net +₹812,204.86**,
  expectancy **+₹670.14/chain**, chain win 62.2%.
- Halves: Jan–May **+₹448,461.50** / Jun–Oct **+₹363,743.36**.
- Splits: home 743 chains / 1,160 trades / **+₹270,069.11**
  (breadth 24/25); ext 469 chains / 675 trades /
  **+₹542,135.75** (breadth 24/25).
- October (1–28): **+₹144,167.85**.
- Breadth **48/50** — only SBIN (−₹48.95) and NHPC (−₹908.48)
  negative. Top-3 share 34.0%; largest contributor MARUTI
  +₹130,810.75 (16.1%).
- Max drawdown (daily-aggregated, risk-card method):
  **−₹18,493.11**.
- Improver gate vs base MOVER-B (+₹464,617.03): net greater ✓,
  both halves positive ✓, breadth ≥45/50 ✓, max DD no worse
  than −₹25,000 ✓, no losing month ✓ — **PASS** (highest pooled
  net among the six passing families of the B2 line).

### Full pooled month table (Jan–Oct 2026)

| Month | Chains | Trades | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| Jan | 143 | 231 | +74,526.64 | +74,526.64 |
| Feb | 117 | 178 | +50,328.52 | +124,855.16 |
| Mar | 196 | 291 | +174,633.57 | +299,488.73 |
| Apr | 143 | 219 | +99,112.98 | +398,601.71 |
| May | 109 | 157 | +49,859.79 | +448,461.50 |
| Jun | 102 | 155 | +104,933.64 | +553,395.14 |
| Jul | 108 | 164 | +50,068.85 | +603,463.99 |
| Aug | 57 | 87 | +22,901.63 | +626,365.62 |
| Sep | 59 | 82 | +41,671.39 | +668,037.01 |
| Oct (1–28) | 178 | 271 | +144,167.85 | +812,204.86 |
| **Total** | **1,212** | **1,835** | **+812,204.86** | — |

No losing month; weakest month Aug +₹22,901.63. Top-2 months
(Mar + Oct) = 39.3% of the total.

## Disclosures (read before judging any fresh result)

1. **In-sample.** This configuration was *selected* on the same
   Jan–Oct 2026 window that produced MOVER-A and MOVER-B. The
   measurement-time slope was scored at exactly three
   pre-frozen points (10:15 base, 10:20, 10:30) and rose at
   each — treat the +74.8% improvement over B as an upper-bound
   estimate until fresh data judges it.
2. **Slope untested beyond 10:30.** The B2 frozen list stopped
   at 10:30 by design. Nothing here says 10:30 is the peak.
3. **Untested stacks.** Direct-only and same-direction (both
   gate-passing at 10:15) were not re-tested on top of 10:30
   in this line; the candidate is the plain 10:30 rule.
4. **Exit alternates recorded:** on this configuration, target
   1.5% FAILS the gate (drawdown −₹28,603.98, net +₹743,491.24)
   and stop 0.65% passes but earns less (+₹775,596.27). The
   candidate keeps T125 (+1.25% / −0.5%).
5. November's frozen A/B shadows (home + ext, 10:00 vs 10:15)
   are **untouched** by this spec and proceed as scheduled.

## Fresh-window judging rule (pre-registered)

Window: **December 2026** (the next full fresh month after the
November exams), pooled 50, rules exactly as above, ₹40/trade,
paper only.

- December net positive at T125 accounting with **≥ 80 chains**
  → B2 is confirmed as a candidate alongside the November
  survivors, for an adoption decision on the combined evidence.
- December net negative with ≥ 80 chains → **B2 is killed**;
  MOVER-B (10:15) remains the line's reference configuration.
- Fewer than 80 chains, or net exactly ₹0 → inconclusive;
  extend one month under identical rules.

No parameter of this spec may be changed during the fresh
window.
