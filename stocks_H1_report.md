# Stocks EQUITY — Line H1 — October-first discovery on Chandu's own 25 stocks

Equity cash intraday only, LONG/SHORT. **Paper only — real money ₹0,
no orders.** Every figure: **provisional per 100 shares, ₹40/trade**
flat cost deducted. Universe: **the home 25 only** (user scope
directive 2026-10-31: "Run only on my stocks"). No ext, no pooled
numbers anywhere in this report. Protocol: Line O1's, exactly —
grid frozen in `stocks_H1_frozen.md` BEFORE scanning.

## Verdict rules (from the frozen plan)

- **OCTOBER HIT** = home October 2026 net ≥ **+₹50,000**.
- A hit is **REAL** only if Jan–Sep 2026 is positive in **BOTH**
  halves (Jan–May AND Jun–Sep) **AND** breadth ≥ 15/25 **AND** it
  beats its lag-placebo. Only then is a candidate spec frozen
  (December fresh-window judging).
- October-only success is a hypothesis, never a result
  (V5×T10: October +₹6,502.57 → Jan–Sep −₹178,594.99).

## Data / coverage

- Home 5-min cache: October = Oct 1–28 (18 trading days). Oct 29–30
  added from the 1-min cache aggregation (O1's validated method,
  re-run here): **1,875 bars checked against the cached Oct 28
  5-min bars, 0 mismatches; 25/25 stocks added for both days.**
  Final October coverage: **20 trading days (Oct 1–30)**.
- Nifty regime map extended to Oct 30 (live closes verified against
  the cached Oct 28 close). Oct 28/29/30 all classify below-50DMA —
  in fact every qualifying October trade in the top cells fell on a
  below-50DMA day, which is why their `below50` twins are identical.
- **Phase-1 timing audit: 37,767 trades generated, 0 violations.**

## Phase 1 — October discovery scan

Full grid: **1,536 cells** (384 base × 4 contexts), saved in
`stocks_H1_results.json`. 593 cells positive; median cell −₹166.95.

### OCTOBER HITS (≥ +₹50,000): **NONE.**

**October's honest ceiling on his 25 stocks in this grid is
+₹34,124.43** — the ₹50k month was not reachable on the home
universe in these families. Near zone (≥ +₹20,000), distinct cells
(context twins with identical trade sets collapsed):

| Cell (T · thr · dir · mode · exit · ctx) | Trades | Oct net ₹ | Breadth /25 |
|---|---|---|---|
| 10:00 · 0.5% · follow · sig · T125/S065 · all | 182 | **+34,124.43** | 19 |
| 09:45 · 0.5% · follow · fixed · T125/S065 · noevent | 92 | **+24,380.09** | 14 |
| 10:00 · 0.5% · follow · fixed · T125/S065 · all | 181 | +22,001.79 | 18 |
| 14:00 · 1.0% · fade · fixed · T125/S065 · all | 204 | +20,906.37 | 12 |
| 14:00 · 1.0% · fade · fixed · T125/S050 · all | 204 | +20,147.69 | 13 |
| 10:00 · 0.5% · follow · sig · T125/S050 · all | 202 | +20,088.94 | 17 |
| 09:45 · 0.5% · follow · fixed · T125/S065 · all | 123 | +20,034.53 | 12 |

Best cell per (mode × direction) family: sig·follow +₹34,124.43
(above); fixed·follow +₹24,380.09 (above); fixed·fade +₹20,906.37
(above); sig·fade only **+₹5,702.07** (10:00 · 0.5% · T125/S065 ·
all, its family best).

Shape of the month: everything that made money on his stocks in
October was **early (09:45–10:00), low-threshold (0.5%), FOLLOW**
— riding the morning move, not fading it — with the widest
stop (−0.65%). The known-flat home 11:00 fade reproduces exactly
in this grid (+₹341.29 in October, the same home slice Line O1
reported), confirming the scan machinery is faithful. The best
cell's October splits event +₹14,360.75 (54 trades) / no-event
+₹19,763.68 (128 trades) — it is not an event-window artefact.


## Phase 2 — Jan–Sep validation of the top-2 October cells

Definitions were frozen in the `stocks_H1_frozen.md` Phase-2
addendum before Jan–Sep was scored. **Phase-2 timing audit: 4,542
trades generated (cells + placebos), 0 violations.** October
re-checks reproduce Phase 1 **exactly** for both cells
(182 trades / +₹34,124.43 and 92 trades / +₹24,380.09).

### HIT-1 — 10:00 · 0.5% · follow · sig · T125/S065 · all

- Jan–Sep: 1,431 trades, **−₹63,538.43** — Jan–May **−₹38,658.84**,
  Jun–Sep **−₹24,879.59**. **Both halves negative.**
- Months: Jan +3,310.91 · Feb −15,668.23 · Mar −4,413.11 ·
  Apr −6,504.15 · May −15,384.26 · Jun −19,096.94 · Jul −3,895.38 ·
  Aug −11,381.74 · Sep +9,494.47. Positive in only 2 of 9 months.
- Breadth 13/25; expectancy −₹44.40/trade. Worst stock GLENMARK
  −₹28,182.08.
- Lag-placebo: −₹18,135.89 — **the placebo loses less than the
  cell itself**; the cell does not beat it.
- Jan–Oct total incl. its October: −₹29,414.00 (≈ −₹2,941/month).
- **Verdict: FAILS all three REAL legs. October-only artefact.**

### HIT-2 — 09:45 · 0.5% · follow · fixed · T125/S065 · noevent

- Jan–Sep: 746 trades, **−₹75,871.49** — Jan–May **−₹24,395.25**,
  Jun–Sep **−₹51,476.24**. **Both halves negative.**
- Months: Jan +3,444.71 · Feb +2,554.33 · Mar −13,359.84 ·
  Apr −16,267.28 · May −767.17 · Jun −16,652.67 · Jul −4,586.16 ·
  Aug −3,338.23 · Sep −26,899.18. Positive in only 2 of 9 months.
- Breadth 8/25; expectancy −₹101.70/trade. Worst stock GLENMARK
  −₹23,306.15.
- Lag-placebo: −₹7,464.58 — again **loses less than the cell**;
  not beaten.
- Jan–Oct total incl. its October: −₹51,491.40 (≈ −₹5,149/month).
- **Verdict: FAILS all three REAL legs. October-only artefact.**

## Verdict

**No October hit, no candidate. Nothing in this line is real.**

1. **The ₹50,000 October did not happen on his 25 stocks.** Across
   1,536 honestly-built cells, October's ceiling on the home
   universe is **+₹34,124.43** (10:00, 0.5% threshold, follow the
   morning move on the first V5 signal, +1.25%/−0.65% exits) —
   roughly two-thirds of the bar, before validation.
2. **Even that ceiling is an October-only artefact.** Both top
   cells lose heavily on Jan–Sep in *both* halves (−₹63,538.43 and
   −₹75,871.49), fail breadth (13/25 and 8/25 vs the ≥15 leg), and
   are *worse than their own lag-placebos*. October 2026 was a
   below-trend month in which early-morning follow-through on his
   stocks happened to pay; the same rules bleed the rest of the
   year. This is the V5×T10 pattern again, caught by the same
   protocol.
3. **Best validated run-rate in this line: none — no cell
   validated.** The best honest October configuration is a
   *negative* system over Jan–Oct (−₹29,414.00). For context only
   (not H1 results): the previously verified home systems remain
   the home universe's honest frontier — INV-LONG +₹24,185.73 over
   Jan–Oct (≈ ₹2,419/month), N4-V3 and P2F smaller — all far below
   the ₹50k/month bar, and October was a hard month for them too.
4. **No `stocks_H1_candidate_spec.md` is frozen.** December has
   nothing new from this line to judge. The hunt on his stocks
   needs a different mechanism family, not more cells of this one:
   on the home 25, morning-move follow/fade at fixed times and on
   the V5 stream is now measured — October-flavoured in both
   directions — and closed.

