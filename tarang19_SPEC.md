# TARANG Design 19 — SPEC (pre-registered 2026-11-17, before any Design 19 scoring)

**Programme status:** CONTINUES (owner's standing mandate —
designs iterate from diagnosis until a gate pass or the owner's
stop). Design 18's diagnosis (tarang18_2026-11-17.md S.7) is
this design's seed: the Bollinger-excursion family is measured
exhausted — both directions, both pools (survivors / rejects),
both exit geometries, both allocations (Designs 7–18); the
reject pool grosses −₹12.02/−₹10.94 per trade under frozen
exits and only +₹2.13/+₹3.81 under symmetric exits, an order
of magnitude below the ₹40 levy. What survived every design
was not an excursion trade: the survival/rejection sort and
quiet allocation are worth ₹15–25/trade as PRE-FILTERS on
other streams. Design 19 leaves excursions entirely and
builds on the multi-indicator **vote state** itself — the
EKAM-style state — traded on its own **transitions**.

**Basis:** equity cash, PROVISIONAL per 100 shares, ₹40/trade,
paper only, real money ₹0. No stock options. Research only —
nothing armed, no paper run started, no live book touched.

**Universe / data:** the 127 Round-6-verified F&O names
(`tarang6_verify.json` verified_universe), stores
`data/tarang_vol/<SYM>/spot_5m_vol.csv` (incumbents) and
`data/tarang_wide_vol/<SYM>/spot_5m_vol.csv` (wide names) via
`tarang6_score.load_name6`; missing volume prints count as 0
(the family's standing convention). Data runs 2025-01-01 →
2026-11-13.

## S.1 The vote state

All indicators are computed on each name's **continuous** 5-min
close series, causal (bar g uses bars ≤ g only). One EMA
convention throughout — the family's seeded EMA: seed = SMA of
the first n values at index n−1, then k = 2/(n+1) recursion
(`tarang7_score._ema_seeded` / EKAM `ema_series`, identical).

- **EMA-9, EMA-21, EMA-50:** seeded EMA of close, spans 9/21/50
  (EMA-50 defined from bar 49).
- **MACD:** line = EMA-12 − EMA-26 (defined from bar 25);
  signal = seeded EMA-9 of the line over the subarray starting
  at bar 25 (defined from bar 33, the `tarang7_score.add_bb_macd`
  construction); hist = line − signal.
- **RSI(14):** Wilder (EKAM `rsi_wilder`): SMA seed of the
  first 14 gains/losses at bar 14, then (13·prev + new)/14.
- **Supertrend(7, 3.0):** EKAM `supertrend_dir` — Wilder ATR(7),
  basic bands mid ± 3·ATR, final-band ratchet, direction
  +1/−1 (0 before bar 6).
- **ADX(14):** EKAM `adx_wilder` — Wilder-smoothed TR/±DM,
  DX, ADX seeded at bar 27 as SMA of DX[14..27], then Wilder
  recursion.
- **Bollinger(20, 2):** rolling 20 mean ± 2 × population sd of
  close (the `tarang7_score.add_bb_macd` construction, defined
  from bar 19). %B = (close − lower)/(upper − lower).

**Six votes at bar g**, each in {+1, −1, 0}:

| # | Component | +1 | −1 | 0 |
|---|---|---|---|---|
| 1 | RSI(14) zone | 50 < RSI < 70 | 30 < RSI < 50 | RSI = 50, ≥ 70, ≤ 30 |
| 2 | MACD hist sign | hist > 0 | hist < 0 | hist = 0 |
| 3 | Supertrend | dir = +1 | dir = −1 | dir = 0 (warm-up) |
| 4 | ADX trend sign | ADX ≥ 20 and close > EMA-50 | ADX ≥ 20 and close < EMA-50 | ADX < 20, or close = EMA-50 |
| 5 | EMA alignment | EMA-9 > EMA-21 | EMA-9 < EMA-21 | equal |
| 6 | Bollinger %B side | %B > 0.5 | %B < 0.5 | %B = 0.5, or upper = lower |

**Amendment A1 (2026-11-17, before scoring — numerical tie
band on vote 6):** %B is a ratio of floats; when the close is
exactly at the 20-bar mean the true %B is exactly 0.5 and the
vote must be 0, but independent floating-point paths place
such bars at 0.5 ± ~3e-10 (measured on the engine/validator
smoke test — every cross-path vote disagreement was this
case). Vote 6 therefore reads: **+1 if %B > 0.5 + 1e-9; −1 if
%B < 0.5 − 1e-9; else 0.** The band changes no genuine
reading (a true %B inside the band is a tie to nine decimal
places) and makes the tie resolve identically in every
implementation — the same class of fix as Design 15's
round-at-source ruler.

**Amendment A2 (2026-11-17, after the first scoring pass —
engine Bollinger numerics):** the first pass's engine
Bollinger used the cumsum form E[x²] − E[x]², which on flat
windows (20 identical closes; 123 bars on SUZLON and
COCHINSHIP) invents a ~1e-5-wide band where the true sd is
exactly 0 — flipping vote 6 against the validator's pandas
path, which returns exactly 0. The engine now computes the
bands by a two-pass sliding window (mean, then mean squared
deviation), with exactly-flat windows (max = min) snapped to
sd = 0 — their variance is zero by definition, and a one-ulp
mean error otherwise leaves a ~1e-13 band. The formula
(Bollinger(20,2), population sd) is unchanged; only its
numerics are made safe. The first pass was discarded in
full and the run repeated; every figure in the Design 19
report is from the corrected run, and the fault is disclosed
there (the Design 15 pattern).

**V(g) = the sum, in −6..+6.** V(g) is **defined** only if
g ≥ 59 (the EKAM warm-up guard: 60 bars of series history)
and every component input is defined (RSI, hist, ADX, EMA-50,
EMA-9, EMA-21, bands all non-NaN and supertrend dir ≠ 0);
otherwise V(g) is undefined and can neither signal nor decay
an exit.

## S.2 Entries — transitions, not levels

A **LONG transition** fires at bar g if V(g) and V(g−1) are
both defined, V(g−1) < +4 and V(g) ≥ +4. A **SHORT
transition** fires if V(g−1) > −4 and V(g) ≤ −4. The entry
fills at the **open of bar g+1**, which must be in the same
session and stamped in **[09:30, 14:30]**.

Candidate generation is a per-name chronological simulation,
independent of the day cap: the name starts flat; while flat,
the first actionable transition opens a position; while a
position is open, transitions are ignored; after an exit
whose fill bar is f, scanning resumes at bar f (the position
is closed before bar f's close in every fill type; the
square-off fill is the day's last bar, so no same-day resume
exists there). A fresh transition after a close is a fresh
candidate — re-entry is part of the design. Each candidate
carries: sym, date, side, signal bar g (and its stamp),
entry bar e = g+1, entry price = open(e), **vol_ratio** at
the signal bar = vol[g] / mean(vol[g−19..g]) (the family's
field; 0 if the mean is 0), **strength** = |V(g)| ∈ {4, 5, 6}.

## S.3 Exits — vote-decay, disaster stop, square-off

Evaluated bar by bar from the entry bar e to the day's
square-off bar sq (the last bar stamped ≤ 15:15, the family
`day_maps` construction), in this order at each bar j:

1. **Disaster stop −1.0% (stop-first):** stop level =
   entry × 0.99 (LONG) / × 1.01 (SHORT). If the bar's open is
   beyond the stop, fill at the open; else if the bar's range
   touches the stop (low ≤ stop for LONG, high ≥ stop for
   SHORT), fill at the stop. Reason `stop`.
2. **Square-off:** if j = sq, fill at close(sq). Reason
   `squareoff`.
3. **Vote-decay:** if V(j) is defined and V(j) < +2 (LONG) /
   V(j) > −2 (SHORT), fill at the **open of bar j+1**. Reason
   `decay`. (j < sq here, so j+1 exists and is ≤ sq.)

Net per trade = side × (exit − entry) × 100 − ₹40.

## S.4 Books — one stream, two allocations

Candidates from S.2 are assembled chronologically with the
family's greedy allocator: sort key (date, entry_time,
**ranking key**, signal_time, sym); caps **1 open position
per name** (busy-until the taken trade's exit bar), **2
entries per name-day**, **10 entries per book-day**; a skipped
candidate does not regenerate later candidates (the family's
standing construction).

- **T19-A — A4 volume-priority:** ranking key = vol_ratio
  DESC, then strength DESC.
- **T19-B — quiet-priority (Design 17 construction):**
  ranking key = vol_ratio ASC, then strength DESC.

## S.5 Controls (all pre-registered; any failure aborts or fails the audit leg)

1. **EKAM machinery control (reported FIRST, before any D19
   number):** EKAM's own vote machinery (imported
   `ekam_intraday_stocks_build` + `ekam_intraday_stocks_r2_build.exit_x2p`)
   run on the frozen 25 under EKAM's 09:15 configuration —
   first qualifying signal of the day at threshold 5, entry at
   the next bar's open, CAND exit stack D=3 / S=1.00% / no cap —
   with EARLIEST-5 selection must reproduce the published
   **CAND-T5** Jan–Oct lines **+₹62,164.57 (2025) /
   +₹63,883.60 (2026)**, and with EARLIEST-3 selection the
   published **S2** lines **+₹45,300.64 / +₹72,605.30**.
   Tolerance: exact to ±₹0.05 per line (rounding only). If
   either line misses, no D19 number is quoted.
   Companion parity: this scorer's own RSI(14), MACD hist,
   ADX(14), Supertrend direction and EMA-9/21 implementations,
   computed on the 25 names' tarang_vol OHLC, are compared
   against EKAM's indicator functions on the same arrays —
   max abs differences and direction-agreement reported.
2. **Engine/validator parity:** the vote series and the
   transition sets are computed twice — the engine
   (loop-based indicators) and an independent validator
   (pandas ewm/rolling-based indicators, separately written
   transition scan) — and must agree on every name: identical
   transition sets, V equal at every signal bar and its
   predecessor. Any mismatch is an audit violation.
3. **Timing/leak audit** over every taken trade: entry after
   signal; entry exactly at signal + 1; entry inside
   [09:30, 14:30]; signal present in the validator's
   transition set with matching V values; exit re-simulated
   on the trade's own day by an independent bar-loop exit and
   matched on bar, price and reason; square-off price =
   close(sq); net recompute; caps (≤2/name/day, ≤10/day, no
   same-name overlap); a full independent allocator rebuild
   (validator transitions + the book's ranking + bar-loop
   exits) matched trade-for-trade.
4. **Truncation spot-check:** 30 sampled taken trades;
   indicators and V recomputed from the series truncated at
   the signal bar must reproduce V(g) and V(g−1) exactly.
5. **Placebos:** (a) 200-draw random-entry placebo per book
   with the book's OWN exits — same names/days, the book's
   own entries-per-day counts, random eligible bars in
   [09:45, 14:45] (the family's standing placebo window),
   random side, identical caps; a random entry's vote-decay
   reads that name-day's actual V series. Percentile of the
   real net within the draws, per year. (b) Direction-flip
   placebo (information): the taken trades with sides flipped
   and exits re-simulated.
6. **Independent re-sum** of the written trades CSV against
   the engine nets, to the paisa.

## S.6 Gate (unmoved, per book — `tarang2_score.gate_for`)

Net positive BOTH years · beats the random-entry placebo p90
BOTH years · ex-top-3 positive BOTH years · no month worse
than −₹15,000 · November 2026 slice (Nov 1–13) ≥ −₹3,000 ·
audits clean (S.5.2–S.5.4 all zero). Nine legs.

## S.7 Stream anatomy (the seed's question)

Report, per year: the RAW candidate stream (every candidate
from S.2 scored standalone, before allocation) — trades,
gross ₹, gross/trade, net — against the ₹40 levy; the taken
books' gross/cost/net per trade (`tarang9_score.cost_anatomy`);
side splits, halves, win rate, max drawdown, month table,
top-10 contributors, resolution mix (stop / decay /
square-off counts and nets). The question Design 20 inherits:
**does this family start near the levy, where the measured
pre-filters (survival sort, quiet allocation) could finish
the job?**
