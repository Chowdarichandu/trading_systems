# Stocks EQUITY — LINE R3 — FROZEN before scoring (2026-10-31)

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0.**
**Every rupee figure: provisional per 100 shares. Gross = before
the frozen ₹40/trade flat cost; net = gross − ₹40/trade.
Window: Jan–Oct 2026 (October = 1–28 Oct).**

## What this is

The transfer test that was never run for the INV family. INV-LONG
is verified REAL on the home 25 (re-summed exact from its trade
dump, timing audit CLEAN — its qualifier, Nifty *previous* close
vs 50DMA, is complete before the trade day opens). Question: does
it live on the 25 new large caps too, and what is the honest
pooled-50 number? **Rules VERBATIM — no re-tuning on the new
universe, no parameter touched.**

## The rules — exact (from `stocks_inv_v2_candidate_spec.md` /
`stocks_tuning_inv_frozen.md`)

1. **Entry pool: P2** — frozen V5 re-entry signal stream
   (`stocks_equity_reentry.py` `pool_pick` over v4 + skill_or
   detectors, chains exactly as `stocks_equity_round8.py:
   run_chain`); chain round ≤ 2 under the exit's own timing;
   entry_time < 10:30; ADR≥3% stock-day (prior-10-day mean
   (high−low)/close×100, min 5 prior rows, trade day excluded).
2. **INV1 condition:** Nifty previous close ≤ its 50DMA (daily
   bars strictly before the trade day; 50DMA = mean of the 50
   closes ending at the previous bar; equality = met). If the
   50DMA cannot be computed, no trades that day.
3. **INV-LONG** = INV1 rows with direction LONG only.
   **INV1** = both directions.
4. **Exits: T125/S050** — target +1.25% / stop −0.5%,
   stop-first on a same-candle tie, 15:10 square-off.

## Machinery

Line 4's transfer pattern, unchanged: the ext run uses
`stocks_equity_round8_ext.py` (the frozen Round 8 file with only
the data path and symbol list substituted — `data/progressive_ext/`),
regime maps built from `data/progressive_ext/` daily files, and
the same `build_cell` / `p2_filter` / `cond_inv1` / `block` code.
The NIFTY `spot_daily.csv` in `progressive_ext/` is **byte-identical**
to the home file (verified before freezing), so the INV1
qualifying-day set is identical across universes — only the traded
stocks differ. Ext symbol list (25): RELIANCE, TCS, ICICIBANK,
INFY, BHARTIARTL, SBIN, LT, AXISBANK, KOTAKBANK, BAJFINANCE,
HCLTECH, MARUTI, SUNPHARMA, TITAN, M&M, ULTRACEMCO, NESTLEIND,
POWERGRID, ONGC, COALINDIA, JSWSTEEL, GRASIM, CIPLA, DRREDDY,
EICHERMOT.

## Validation gate (must pass BEFORE any ext number is trusted)

The R3 engine's home run (original machinery, home universe)
must reproduce, to the paisa:

- **INV1 home:** 694 trades, net **+₹22,964.30**, halves
  Jan–May **+₹7,255.01** / Jun–Oct **+₹15,709.29**.
- **INV-LONG home:** 249 trades, net **+₹24,185.73**, halves
  **+₹14,751.12** / **+₹9,434.61**, October **+₹7,691.08**,
  breadth **12/25**, top-3 share **116.2%**.

If the gate fails, scoring stops and the failure is reported.

## Runs (in order)

1. **EXT INV-LONG** (rule under test): trades, net, halves,
   October, breadth (/25), top-3 share, net expectancy, win%.
2. **EXT INV1** (both directions, context + its own verdict):
   same reporting.
3. **POOLED-50 INV-LONG:** home + ext rows combined; trades,
   net, halves, October, breadth (/50), top-3 share, expectancy;
   concentration read — TVSMOTOR + GLENMARK combined net and
   their share of the pooled net, vs ≈97% at home; top-5
   per-stock table.

## Transfer standard — pre-declared

A configuration **TRANSFERS** if and only if, on the ext 25:
**both halves (Jan–May and Jun–Oct) net > 0 AND breadth ≥ 10/25**
stocks net-positive. Anything else **FAILS**, stated plainly.
October and expectancy are reported, not gating.

## Outputs

- This frozen spec: `stocks_R3_frozen.md`
- Engine: `stocks_R3.py`; results: `stocks_R3_results.json`
- Trade CSVs: `R3_ext_inv1_trades.csv`, `R3_ext_inv_long_trades.csv`,
  `R3_pool50_inv_long_trades.csv`
- Report: `stocks_R3_report.md`
- **If and only if INV-LONG transfers:** `stocks_inv_long_pooled_candidate_spec.md`
  freezing the pooled-50 INV-LONG as the candidate, with a
  pre-declared December 2026 fresh-window judging rule. If it
  fails, no pooled spec is written and INV-LONG's standing stays
  home-universe-only, exactly as the v2 candidate spec records it.

Stage work only. Nothing here is adopted; nothing here is a
live-trading instruction. The November INV1 shadow is untouched.
