# Stocks EQUITY — Line M2 — FROZEN fix plan (written BEFORE any fix is scored)

**Frozen: 2026-10-31, after the Step-1 diagnosis, before the fix
loop runs.** Equity cash intraday only, LONG/SHORT. Paper only —
real money ₹0, no orders. Every figure: provisional per 100 shares,
₹40/trade flat cost deducted. **Home 25 only.** Jan–Oct 2026;
October = full month (Oct 1–30, Oct 29/30 from the validated 1-min
aggregation, as in Line H1).

## The cell under repair (HIT-1, exact)

Measurement 10:00 · qualifier |pre-move from open through the bar
ending 10:00| ≥ 0.5% · direction FOLLOW · entry = first V5 pooled
signal at/after 10:00 whose direction matches the pre-move's sign
(honest build, H1 machinery) · chain cap 2 · exits T125/S065
(target +1.25% / stop −0.65%, stop-first, 15:10 square-off).

Anchors (reproduced by `stocks_M2_diag.py` from the H1 engine,
asserted to the paisa, timing audit 2,374 trades / 0 violations):
October 182 trades **+₹34,124.43** (breadth 19/25; event +₹14,360.75
/ no-event +₹19,763.68) · Jan–Sep 1,431 trades **−₹63,538.43**
(Jan–May −₹38,658.84 / Jun–Sep −₹24,879.59) · lag-placebo Jan–Sep
**−₹18,135.89**.

## Root cause (from Step-1 diagnosis, `stocks_M2_diag.json`)

The cell's edge lives in exactly one ex-ante state — **a moderate
morning move (0.5%–1.0%) on a below-trend day** (Nifty prior close
≤ 50DMA) — and the frozen cell trades far outside it:

- Qualifier band ≥1.0%: −₹40,532.42 of the −₹63,538.43 Jan–Sep hole
  (64% of the loss on 37% of trades), negative in **both** halves
  (Jan–May −₹26,918.81, Jun–Sep −₹13,613.61) **and in October
  itself** (−₹2,041.80). October's entire win came from the
  sub-1% population (+₹36,166.23).
- Band × regime (Jan–Sep): 0.5–1.0% × below50 = **+₹6,830.03**
  (598 trades); 0.5–1.0% × above50 = −₹29,836.04; ≥1.0% × below50 =
  −₹47,523.81. October was 100% below50 days — the one month the
  unfiltered cell happened to sit in its profitable state.
- No one-dimensional projection separates: direction flips by half
  (SHORT is the Jan–May hole, LONG the Jun–Sep hole); each regime
  alone is negative; setup mix, event context and entry time do
  not separate. The volatility explanation is **rejected**: corr
  (monthly mean stock ADR%, monthly expectancy) = −0.018; March
  had higher volatility than October on both measures and lost.

## Fix families (the complete list — nothing else will be scored)

- **F1 — Qualifier-band cap.** Qualify only if 0.5% ≤ |pre-move| <
  1.0%. Everything else verbatim. (Single mechanism: remove the
  violent-move population.)
- **F2 — Trend-regime gate.** Trade only on days whose prior close
  has Nifty ≤ its 50DMA (the H1/INV regime map verbatim).
  Everything else verbatim.
- **F3 — Prior-day volatility gate.** Trade only when the prior
  trading day's Nifty intraday range (high−low)/close ≥ 1.00%
  (spot_daily.csv, known before the trade day). Everything else
  verbatim. (Tests the diagnosis's rejected-but-plausible rival:
  that the cell needs a high-range tape.)
- **F4 — State gate (the root-cause repair).** Qualification
  restricted to the diagnosed state: 0.5% ≤ |pre-move| < 1.0% AND
  Nifty prior close ≤ 50DMA. Everything else verbatim. Frozen as
  ONE qualification rule (the diagnosis's separator is the joint
  state; F1/F2 are scored first so the report shows each
  component's standalone result alongside it).

Screened out by the diagnosis without a family slot: chain-cap 1
(round-2 is the Jan–May hole but direct trades are the Jun–Sep
hole — halves conflict); direction restriction (flips by half);
setup exclusion (skill_or_breakdown is October's payer and
Jan–Sep's loser in the same proportion — no separation); event
context (both sides negative Jan–Sep); per-stock exclusion (would
be hindsight fitting; GLENMARK is disclosed, not removed).

## Scoring and acceptance (fixed here)

Every family is scored on the **full Jan–Oct 2026** with the H1
engine machinery (rebuild, not trade-filtering, wherever the rule
changes qualification; gates that are pure day/trade properties
are additionally cross-checked against the base trade file).
Reported per family: trades, net, Jan–May, Jun–Sep, October, full
month table, breadth (per-stock net > 0, of 25, full period and
Jan–Sep), timing-audit count, and the family's **own lag-placebo**
(same rule, qualifier lagged one trading day, Jan–Sep).

**Acceptance for a fix (all legs required):**
1. October ≥ **+₹25,000**;
2. Jan–Sep positive in **BOTH** halves (Jan–May > 0 AND Jun–Sep > 0);
3. Full month table published;
4. Timing audit clean (0 violations);
5. Fixed book beats the lag-placebo (its own placebo, Jan–Sep);
6. Breadth ≥ **15/25**.

Combinations beyond F4 are not permitted. If F4 is the only family
that passes, the report must state that its two components fail
standalone (if they do) and carry that disclosure into the
candidate spec — the December fresh window is then the real judge.
If no family passes, no candidate spec is frozen and the cell
stays an October artefact with the root cause named above.
