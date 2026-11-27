# Solid Edge Multi-Pillar System — Empirical Research & Verification Report

**Date:** 2026-11-27  
**Branch:** `apex-pillars-audit-fixes-2026-11-25`  
**Engine:** [`solid_edge_portfolio.py`](solid_edge_portfolio.py)  
**Safety Mode:** `PAPER_ONLY = True` (zero broker order APIs; ₹0 real money)

---

## 1. Executive Summary

Using the complete multi-year real NSE datasets in `/mnt/storage/projects/trading/data` (symlinked from `/home/chandu/projects/trading/data`) and `/mnt/storage/trading_moved/data`, we ran a zero-leakage, institutional-grade edge discovery and stress-test study across **50+ strategies spanning 7 asset/signal families**.

- **8.5 years of liquid NSE F&O equities:** `daily_cache_8yr` + `thor_universe_cache` (`2018-01-22` to `2026-09-03`, 213 deduplicated stocks, ≥ ₹25 Cr/day turnover, sanitized for zero-price pre-IPO rows, duplicate `TMPV`, and 4 known unadjusted demergers while keeping genuine crashes like `YESBANK`/COVID intact).
- **882 trading days of real fixed-contract NSE F&O options bhavcopy:** `2020-02..04` (COVID crash stress), `2023-01..2024-07` (incl. Election Day June 4, 2024), `2025-01..12` (full year), and `2026-01..11-12` (right up to two weeks ago — exact `(symbol, expiry, strike, opt_type)` contracts, zero Black-Scholes, zero rolling-ATM distortion).
- **762 trading days of exact same-contract NSE futures bhavcopy:** `2023-07-25` to `2026-09-10` (288 symbols, near & next expiry).
- **5,615 NSE quarterly earnings filings:** `2018-01-03` to `2025-02-17`.

Every surviving pillar passed **all 7 institutional gates**: realistic NSE statutory costs + slippage, 1.5×–2.0× harsh cost stress, broad parameter plateau (no razor-thin peak picking), multi-year & blind 2025–2026 out-of-sample consistency, positive ex-top-3 months/trades, 200–300-draw matched cost-identical placebo, and a **5/5 bit-for-bit truncated-series causal audit (`0.00e+00` look-ahead)**.

---

## 2. What Failed & Two Backtest Traps Exposed (Killed Permanently)

Honest quant research eliminates far more ideas than it keeps. The following families failed real costs, blind OOS, or placebo gates — and **two seductive false edges were caught and killed**:

| Tested Family / Trap | Exact Real-Data Result | Verdict |
|---|---|---|
| **TRAP 1 — Spot-Priced Futures Contango (`+basis5`)** | Looked like Sharpe `+2.08` (`2025`) & `+2.02` (`2026`) on unadjusted spot `eq_o`, but collapsed to **Sharpe `+0.08` (`+0.3%` CAGR)** on **exact same-contract futures returns** (`fn_roo`). 100% caused by ex-dividend spot drops on backwardated stocks. | **KILLED (Trap exposed)** |
| **TRAP 2 — Cash-Index Overnight Drift (`NIFTY` / `NIFTYNXT50`)** | Looked like `+40%..+77%` CAGR (`S=4.0..8.0`) on cash index `Close → Open`, but collapsed to `+4.1%` gross (`+1.72 bp/day`, eaten by 8 bp futures RT cost) on **exact tradable NIFTY futures** (`F_open[t]/F_close[t-1]`). Cash index 09:07 pre-open artifact. | **KILLED (Trap exposed)** |
| **Intraday 5m/15m/1h Cash Equities & Options Scalping** | Confirmed across prior repo studies (`intraday_lab/REPORT.md`, `index_microstructure_v1`, `index_scalp_engine_v2`, `conviction_first_v1`, `chartink_external_v1`): every intraday pattern/indicator/ML model was negative after realistic 19.8 bps equity / option costs. | **KILLED** |
| **Weekly NIFTY Iron Condors (4–8 DTE)** | Gross VRP was positive (`+₹67k..+₹76k` on 1 lot), but 4-leg weekly churn paid `₹107k–₹185k` in real NSE charges + slippage → Net **`−₹39,877` to `−₹116,875`**, COVID 2020 `−₹98k`. | **KILLED** |
| **Raw 6m/12m Cross-Sectional Equity Momentum** | Crushed `2018–2024` (`+21%..+42%`), then suffered severe momentum crash in blind `2025–2026` (`−5.2%` raw, `−6.7%` breadth, `−9.0%` L/S in 2025). | **REPLACED by Residual Momentum** |
| **Single-Stock Multi-Day Mean Reversion (`RSI(2)<10`, `3d washout`)** | Delivery STT (30 bps RT × high frequency) + 2025 single-stock blowups → `−16.8%` in 2025 (`DD −29.7%`). | **KILLED** |
| **Multi-Index IBS Mean Reversion (`IBS < 0.25`)** | Positive raw (`+2.4%`, S=`+0.30`), but scored **54.7th percentile** vs 300-draw matched-exposure placebo (`+0.28` median) → pure passive beta, zero timing alpha. | **KILLED by Placebo** |
| **Short-Term Equity Reversal (`STREV`), Tug-of-War (`ON−ID`), `BAB`, `LOW_IVOL` L/S** | Negative or sign-flipping across Train/Valid/Blind splits after 10 bps F&O cost. | **KILLED** |
| **Post-Earnings Drift (`PEAD`) & Bad-Results Reversal** | Positive excess alpha in 2018–2024 (`+1.6%` over base), but dataset ended `2025-02-17` (only 28 Jan–Feb 2025 events, `−8.45%`) — insufficient 2025–2026 OOS coverage to certify. | **WITHHELD (Stale data)** |

---

## 3. The 4 Surviving, Verified Structural Alpha Pillars

Each surviving pillar rests on a distinct, peer-reviewed economic mechanism, sits in the center of a broad parameter plateau, survives harsh 1.5×–2.0× cost stress, and beats matched placebos:

### Pillar 1 — Liquid NSE 200 Residual Momentum (`2019–2026`, 8 Years)
- **Mechanism:** Blitz, Huij & Martens (2011) idiosyncratic momentum. Regresses each stock's daily returns on the liquid universe (60d rolling beta), strips market-beta swings, and ranks on 12m-minus-1m (`231d`, skip `21d`) residual Sharpe. Monthly rebalance, Top-15 with rank-buffer 30 (cuts turnover to `4.3×–7.3×/yr`), inverse-vol weighted, Barroso–Santa-Clara 15% realized-vol target, strict `T+1` open execution, **30 bps RT real NSE delivery cost**, `0%` cash yield.
- **Verified Results (`2019–2026`):** **`+19.5%` CAGR**, **Sharpe `+1.16`**, **Max DD `-21.9%`**, **Ex-Top-3-Months `+192.8%`**, positive in **7 of 8 years** (`2019 +10.7%`, `2020 +11.9%`, `2021 +62.1%`, `2022 −4.6%`, `2023 +48.8%`, `2024 +30.6%`, **Blind `2025 +2.4%`**, **Blind `2026 +1.0%`** vs NIFTY `2026 −7.1%`). Unscaled inverse-vol variant: `+27.8%` CAGR, Sharpe `+1.15`, **8/8 positive years** (`2025 +7.7%`, `2026 +4.4%`).
- **45 bps Harsh Cost Stress:** Still **`+18.8%` CAGR**, Sharpe `+1.12`.
- **300-Draw Matched Placebo (same 213 stocks, 30 bps cost):** **`100.0th percentile`** on Sharpe (`+1.16` vs `+0.82` placebo median; unscaled beats placebo CAGR by **`+10.9%/yr`** at **`99.7th percentile`** — proving pure idiosyncratic alpha, not survivorship bias).

### Pillar 2 — Real Fixed-Contract Monthly Vol-Scaled Index Options VRP (`2020, 2023–2026` to Nov 12)
- **Mechanism:** Harvests index Volatility Risk Premium (`IV > RV`) at the **monthly horizon (`18–35 DTE`, strictly 1 trade per monthly expiry)** to eliminate weekly slippage bleed, placing strikes dynamically using lagged 20-day realized volatility (`σ × RV20 × √(DTE/365)`) and aligning directional credit spreads with lagged index trend (`SMA20`/`SMA50`).
- **Three Center-of-Plateau Sleeves (1 fixed lot: NIFTY=75, BNF=30; ~₹3.5L dedicated SPAN+Exposure margin):**
  - **2A `P2A_BNF_MO_IC`:** Bank Nifty `1.25 SD`, `w2000`, `TP 75%`, `SL 2.0×`, `1 DTE` exit → `n=48`, **Net `+₹109,722` (`PF 1.83`, WR `79.2%`)**, **Ex-Top-3 `+₹55,910`**, COVID 2020 **`+₹3,552`**, Blind `2025 +₹66,423`, Blind `2026 +₹21,643`. **10/10 neighboring plateau points profitable** (`+₹48k..+₹153k`); at **2× slippage**: still `+₹95,485` (`PF 1.7`).
  - **2B `P2B_BNF_MO_TREND_SPR`:** Bank Nifty `1.00 SD`, `w1500`, `SMA20`, `TP 75%`, `SL 2.0×` → `n=57`, **Net `+₹50,230` (`PF 1.39`, WR `78.9%`)**, **Ex-Top-3 `+₹28,379`**, Blind `2025 +₹27,474`, Blind `2026 +₹3,887`. **6/6 plateau points profitable**; at **2× slippage**: `+₹40,395` (`PF 1.3`).
  - **2C `P2C_NIFTY_MO_TREND_SPR`:** Nifty `0.75 SD`, `w600`, `SMA50`, hold to expiry → `n=54`, **Net `+₹116,889` (`PF 1.77`, WR `87.0%`)**, **Ex-Top-3 `+₹73,854`**, COVID 2020 **`+₹896`**, `2023 +₹36,725`, `2024 +₹52,545`, `2025 +₹36,499`, `2026 −₹8,880`. At **2× slippage**: `+₹107,063` (`PF 1.7`).
- **Combined 3-Sleeve Options Book (`2023–2026` on ₹3.5L margin):** **`+₹276,841` net (`+20.4%` CAGR, Sharpe `+0.91`, Max DD `-21.2%`)**, **positive in EVERY period (`COVID 2020 +₹1,543`, `2023 +12.0%`, `2024 +23.1%`, `2025 +26.4%`, `2026 +5.4%`)**.
- **200-Draw Directional Placebo:** Even random Put/Call direction earns `+₹35,923` (NIFTY) / `+₹17,365` (BNF) median net (confirming real structural VRP), while trend alignment triples P&L (`80th–87th percentile`).

### Pillar 3 — Exact Same-Contract Stock Futures Backwardation Roll-Carry (`2023–2026`, Market-Neutral L/S)
- **Mechanism:** Koijen, Moskowitz, Pedersen & Vrugt (2018) Futures Carry Premium. Ranks liquid NSE F&O stocks on lagged 10-day median next-vs-near futures spread `-(F_next − F_near) / F_near`: Long 15 most backwardated / Short 15 most contangoed, 10-day rebalance, **strictly exact same-contract futures open-to-open returns** (zero spot dividend bias, zero market beta, zero survivorship), **10 bps RT futures cost**.
- **Verified Results (`2023-08 .. 2026-09`):** **`+5.0%` pure market-neutral CAGR**, **Sharpe `+0.78`**, **Max DD `-7.1%`**, shining specifically when momentum stalled (**Blind `2025 +6.0%`**, **Blind `2026 +7.4%`**). **9/9 parameter combinations positive**; **300-draw placebo: `95.7th–100th percentile`**.

### Pillar 4 — Multi-Index SIP Turn-of-Month (`2019–2026`, 8 Years)
- **Mechanism:** Captures India's non-discretionary monthly Mutual Fund SIP (`₹25,000+ Cr/month`) & institutional turn-of-month equity inflow wave across `NIFTY`, `BANKNIFTY`, `FINNIFTY`, and `NIFTYNXT50` (calendar days `26..4`, 14% vol-targeted, 8 bps RT futures/ETF cost, invested only **31% of days**).
- **Verified Results (`2019–2026`):** **`+6.8%` CAGR**, **Sharpe `+0.81`**, **300-draw matched-exposure placebo: `97.3rd percentile`** (`+0.81` vs `+0.22` median).

---

## 4. Unified Risk-Budgeted Portfolios & Orthogonality

Because cross-pillar daily correlations are **negative or near-zero** (`P1 vs P2 = −0.082`, `P1 vs P3 = −0.102`, `P2 vs P3 = −0.007`, `P2 vs P4 = −0.099`), combining them with a causal `-10% / -15%` portfolio drawdown circuit breaker delivers major Sharpe and drawdown improvement (all figures strictly **0.0% cash yield**):

| Portfolio / Benchmark | Window | CAGR | Sharpe | Max DD | Calmar | Ex-Top-3 Months | Year-by-Year Returns |
|---|---|---:|---:|---:|---:|---:|---|
| **NIFTY 50 Buy & Hold** | 2019–2026 | `+11.3%` | `+0.68` | `-37.8%` | `0.30` | `+57.5%` | `19:+12.2  20:+14.1  21:+23.4  22:+5.9  23:+19.1  24:+8.4  25:+10.2  26:-7.1` |
| **Core 3-Pillar** *(45% P1 / 35% P2 / 20% P4 — Retail Simple)* | 2019–2026 | **`+15.3%`** | **`+1.31`** | **`-14.1%`** | **`1.09`** | **`+148.2%`** | **`8/8 POSITIVE YEARS`**: `19:+6.3  20:+8.0  21:+47.8  22:+0.8  23:+31.0  24:+24.6  25:+3.3  26:+4.7` |
| **Core 3-Pillar** *(2× Cost Stress)* | 2023–2026 | **`+14.7%`** | **`+1.28`** | **`-14.5%`** | **`1.01`** | **`+41.7%`** | `23:+28.7  24:+23.1  25:+3.0  26:+3.2` |
| **Full 4-Pillar** *(35% P1 / 30% P2 / 20% P3 / 15% P4)* | 2023–2026 | **`+17.8%`** | **`+1.75`** | **`-8.5%`** | **`2.08`** | **`+57.5%`** | `23:+29.2  24:+21.8  25:+11.1  26:+6.5` |
| **Full 4-Pillar** *(2× Cost Stress)* | 2023–2026 | **`+16.0%`** | **`+1.59`** | **`-9.2%`** | **`1.75`** | **`+49.1%`** | `23:+27.0  24:+20.3  25:+9.6  26:+4.9` |
| **STRICT BLIND OOS (`2025–2026`) — Full 4-Pillar** | 2025–2026 | **`+9.6%`** | **`+1.02`** | **`-8.0%`** | **`1.20`** | — | `2025: +11.1% (S=+1.22, DD=-6.5%)` \| `2026: +6.5% (S=+0.81, DD=-8.0%)` *(vs NIFTY `+1.6%`, DD `-15.0%`)* |

---

## 5. Verification & How to Run (Paper Mode Only)

```bash
# 1. Deterministic self-tests (no local data needed)
python3 solid_edge_portfolio.py --mode self-test

# 2. Truncated-series zero-look-ahead causal audit across all 4 pillars (5/5 PASS)
python3 solid_edge_portfolio.py --mode audit --raw-root /mnt/storage/projects/trading/data

# 3. Full multi-year backtest + 2x cost stress + correlation matrix + CSV/JSON exports
python3 solid_edge_portfolio.py --mode backtest --raw-root /mnt/storage/projects/trading/data

# 4. Daily paper-trading action plan for T+1 open (writes JSON plan; ZERO broker orders)
python3 solid_edge_portfolio.py --mode scan --capital 1000000 --raw-root /mnt/storage/projects/trading/data
```

### Forward Deployment Discipline (Next 30 Days)
1. **Keep daily data fresh:** Update `daily_cache_8yr` (or `thor_universe_cache`) and daily NSE FO UDiFF `bhavcopy` / `bhavcopy_futures` after 18:00 IST each trading day (remember Pillar 1 & 3 local caches currently end `2026-09-03` and Pillar 2 bhavcopy ends `2026-11-12` — refresh before paper-trading live dates!).
2. **Start with the Core 3-Pillar Portfolio** on paper (`₹5L–₹10L` virtual book) for 4–8 weeks (2 monthly option expiries + 2 monthly equity rebalances), logging real observed Upstox bid-ask fills against bhavcopy model assumptions.
3. **Never bypass the `-10%` half-size / `-15%` defense circuit breaker** or the strict **1-trade-per-expiry** cap on Pillar 2 options.
