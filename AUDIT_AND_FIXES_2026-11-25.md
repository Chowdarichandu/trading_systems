# Independent Quantitative, Code & Operational Audit — `trading_systems-main`

**Audit date:** `2026-11-25` · **Snapshot audited:** `2026-11-20 15:15 IST` (3,562 files: 886 `.py`, 587 `.md`, 1,067 `.csv`, 728 `.json`)  
**Status:** Paper only (`₹0` real money). All code patches listed in §4 were applied cleanly without altering any frozen Jan–Oct strategy rules or historical control assertions.

---

## Executive Verdict (Ahead of `2026-11-30`)

**Recommendation: Hold `₹0` real money through December (`2026-12-31`) while hardening the production core.**

Your research culture (pre-registered specs, zero-estimation `NC` policies, causal audits, honest killing of failed ideas like DIAL / SAPTA / BTST / small-target exits) is genuinely strong. However, this audit found **four structural/statistical blind spots** and **seven live production bugs** that make a `2026-11-30` live launch premature:

1. **EKAM-Intraday's edge and 100th-percentile placebo are confounded by an undetected alphabetical-selection bug** (`cands.sort(key=(signal_stamp, sym))`) plus a broken decay-exit placebo.
2. **Flat `₹40/trade` equity cost modeling on 100 shares understates real NSE taxes + slippage by 4×–10×**, wiping out nearly all intraday equity backtest profits once realistically priced.
3. **Six forward shadow/candidate scorers went 100% `NC`/empty across `Nov 16–19`**, the circuit breaker JSON wrote `currently_paused: false` on the night `HWMDD` tripped, and `TRIO Stocks` headlines cite a different book (`Variant C`) than the live logger (`post-C24`).
4. **Live November index paper (`Nov 2–19`) is flat-to-negative on the heavily mined TRIO leads** (after 1,000+ tuning cycles on a single 10-month 2026 window), showing severe PE-side concentration during a `+7,500 pt (+13.7%)` Bank Nifty uptrend.

---

## 1. Live November Paper Scorecard (Through `2026-11-19/20`)

Most reports stop at `Nov 13–15`. The actual CSV ledgers through `Nov 19–20` show:

| Segment / Book | Role | Jan–Oct In-Sample | Nov 2–13 | **Nov 16–19 (LIVE)** | Nov Total | Finding |
|---|---|---:|---:|---:|---:|---|
| **TRIO Bank (`Stack v2 + B-FIX-1`)** | Lead | +₹1,31,510 (94 legs) | −₹3,440 (2 legs) | **₹0 (0 legs)** | −₹3,440 | 4 consecutive no-trade days (`november_repaired_bfix1_bank_log.csv`) |
| Bank `TUNED STACK v2` (raw) | Control | +₹1,27,352 (111 legs) | −₹2,680 (4 legs) | **₹0 (0 legs)** | −₹2,680 | HWM-DD tripped Nov 13; flat Nov 16–19 |
| Bank `D1` (`B-FIX-1 + Conf ≥ 0.5`) | Shadow | +₹1,26,496 (71 legs) | ₹0 (0 kept) | **₹0 (0 legs)** | ₹0 | 0 live trades; only 3 of 6 factors scored in Nov |
| Bank `BNF-PAPER-V1` (legacy) | Control | +₹83,651 (99 legs) | −₹1,920 (6 legs) | **NOT LOGGED** | −₹1,920* | `november_paper_bank_log.csv` stopped updating after Nov 13 |
| Bank `Skill V3` standalone | Shadow | +₹3,596* (70 stored) | −₹1,160 (8 legs) | **+₹9,920 (4/4 targets)** | **+₹8,760** | Only positive Bank line in Nov (4 consecutive targets) |
| **TRIO Nifty (`TUNED v1 + N-FIX-1`)** | Lead | +₹1,17,170 (66 legs) | ₹0 (0 legs) | **−₹440 (2 BE stops)** | −₹440 | Logged negative stop `-11.20` on Nov 17 CE @ ₹38.80 |
| Nifty `TUNED v1` (raw) | Control | +₹1,03,050 (74 legs) | +₹3,037 (1 leg) | **−₹440 (2 legs)** | +₹2,597 | Only positive gated Nifty line |
| Nifty `TUNED v2` (`EVE-11`) | Shadow | +₹1,15,951 (59 legs) | ₹0 (0 legs) | **−₹220 (1 BE stop)** | −₹220 | Only 1 leg across 13 sessions |
| Nifty `NF-PAPER-C3G7` | Control | *Never scored* | −₹3,470 (1 leg) | **−₹422 (1 sq-off)** | −₹3,892 | Unbenchmarkable primary |
| Nifty `Skill V3` standalone | Shadow | +₹17,136 (99 legs) | −₹6,437 (8 legs) | **+₹6,439 (4 legs)** | +₹2 | Nov 19 CE hit +150 runner (+₹9,530) |
| **TRIO Stocks (Stock Book live)** | Lead | *See §2.3* | +₹7,518 (32 trades) | **+₹782 (4 trades)** | **+₹8,300** | 82% of Nov 2–13 from 2 GLENMARK trades on Nov 6 |
| Stocks `EKAM S2` | Shadow | +₹45.3k / +₹72.6k | +₹20,663 (27 trades) | **+₹4,300 (12 trades)** | +₹4,300 live | Driven by alphabetical 09:15 selection (§2.1) |
| Stocks `EKAM CAND-T5` | Shadow | +₹62.2k / +₹63.9k | +₹24,529 (45 trades) | **MISSING in EOD** | +₹9,177* live | Official EOD CSV stopped Nov 13; intraday live log ran |
| `BTST-IND` / `R4-D1` / `Prem-Tape` / `OI-V3` | Shadows | Various | CF only | **0/4 days scored** | **100% NC** | All 4 failed every live day Nov 16–19 (§4) |
| `TARANG-C1/C2` & `SAPTA-C1/C2` | Forward | +₹22k–₹1.58L | n/a | **0 EOD rows** | **Empty** | Range-route lag left all 4 ledgers header-only |
| `EKAM Daily` | Paper | +₹43.0k / +₹1.41L | Carried ASTRAL | **3/4 UNSCORED** | Open −₹2,840 | 1-day daily-candle publication lag |

---

## 2. Critical Quantitative & Methodology Findings

### 2.1 EKAM-Intraday's Alphabetical-Selection Bug & Invalid Placebo
- In `ekam_intraday_stocks_build.py`, indicators (`EMA 9/21`, `MACD`, `RSI`, `Supertrend`, `ADX`) run continuously across days, so 5 of 6 votes carry over from yesterday's close. At bar 0 (`09:15`), `vwap[0] = (H+L+C)/3`, causing ~10–15 stocks (of 25) and ~40+ stocks (of 100) to hit `≥ 5` votes simultaneously on the `09:15` bar.
- `ekam_intraday_stocks_r5_build.py` line 48 breaks ties by `cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))` and slices `[:5]` (`CAND-T5`) or `[:3]` (`S2`).
- **Result:** Virtually 100% of signals tie at `09:15`, making `EARLIEST-3` / `EARLIEST-5` an **alphabetical ticker filter**:
  - In the 25-name book, `ASTRAL`, `BDL`, `GLENMARK`, `GODREJCP`, `HDFCBANK` absorb nearly all slots; `TATASTEEL`, `TVSMOTOR`, `UNITDSPR`, `VEDL`, `WIPRO` almost never trade.
  - In `wide100_ekam_results.json`, **all Top-5 contributors in both 2025 and 2026 begin with `A` or `B`** (`APARINDS`, `APOLLOHOSP`, `ADANIGREEN`, `ADANIENT`, `BAJAJ-AUTO`, `ASTRAL`, `BSE`). `wide100_2026-11-17.md` misattributed `APARINDS` (₹10,000–₹14,667/share) to being a "habitual early signaller" when it was simply #1 alphabetically.
- **Why the 100th-percentile placebo fails as a control:** `ekam_intraday_stocks_r2_build.py` enters random stocks at random times (`09:20–15:10`) with random sides (`±1`), then applies `exit_x2p` (exit immediately when `own_votes ≤ 3`). Because a random side already has `votes ≤ 3` roughly 80–90% of the time on the entry bar itself, the placebo exits after 5 minutes and bleeds `-₹40 × 1,035 = -₹41,400/yr` in friction while never holding a trend.

### 2.2 Realistic NSE Transaction Costs & Slippage Stress-Test
All equity books assume **`₹40/trade` flat on 100 shares**, ignoring STT, NSE turnover charges, GST, stamp duty, DP charges, and bid-ask/market slippage:

| Equity Position (100 shares) | Brokerage | Statutory Taxes & Charges | Modest 0.05%/side Slippage | **Realistic Cost / Trade** | Assumed |
|---|---:|---:|---:|---:|---:|
| Intraday ₹500 (₹50k) | ₹40 | ~₹20 | ₹50 | **~₹110** | ₹40 |
| Intraday ₹1,000 (₹1.0L) | ₹40 | ~₹40 | ₹100 | **~₹180** | ₹40 |
| Intraday ₹2,500 e.g. GLENMARK (₹2.5L) | ₹40 | ~₹100 | ₹250 | **~₹390** | ₹40 |
| Delivery swing ₹1,000 (₹1.0L) | ₹40 | ~₹235 (0.20% STT + DP) | ₹100 | **~₹375** | ₹40 |

Stress-testing reported equity books at a conservative **₹150/trade** intraday (or **₹350/trade** delivery):

| Strategy | Trades/yr (25 / 26) | Reported Net (@ ₹40) | Gross/tr | **Stress-Tested Net** | Outcome |
|---|---:|---:|---:|---:|---|
| **EKAM CAND-T5** | 1,035 / 1,025 | +₹62,165 / +₹63,884 | ₹100 / ₹102 | **−₹51,685 / −₹48,866** | Fails both years |
| **EKAM S2** | 621 / 615 | +₹45,301 / +₹72,605 | ₹113 / ₹158 | **−₹23,009 / +₹4,955** | Breaks 2025; marginal 2026 |
| **TARANG-C1** | 563 / 548 | +₹1,51,308 / +₹50,275 | ₹309 / ₹132 | **+₹89,378 / −₹10,005** | 2026 negative (before 09:15 open slippage!) |
| **Stock Book (Variant C)** | 1,064 / 1,363 | +₹1,19,813 / +₹2,47,179 | ₹153 / ₹221 | **+₹2,773 / +₹97,249** | 2025 wiped out; 2026 −61% |
| **EKAM Daily 2c (@ ₹350 deliv.)** | 74 / 102 | +₹42,955 / +₹1,41,328 | ₹620 / ₹1,425 | **+₹20,015 / +₹1,09,708** | **Survives real costs cleanly** |

### 2.3 Stock Book Identity Mismatch & Un-Normalized Sizing
- `STRATEGIES.md` and `trio_ekam_monthly_results_2026-11-15.md` display **Adopted Variant C** (`+₹1,19,813` in 2025 / `+₹2,47,179` in 2026, 11 sleeves) directly above the November live paper trades (`+₹7,518`), but `stocks_sarvaritu_logger.py` is running the older **v2 post-C24 7-component book**, whose actual Jan–Oct backtest is only **+₹30,817 in 2025** (`wide100_2026-11-17.md`) and **+₹2,11,780 in 2026**.
- Flat 100-share sizing deploys **₹2.60 lakh** on `GLENMARK` vs **₹8,000** on `NHPC` (a 32.5× capital distortion).
- `EXCL_V2` (`stocks_sarvaritu_logger.py`) hard-codes 11 ticker-specific `(comp, stock, dir)` deletions across 24 tuning cycles — high in-sample memorization risk.

### 2.4 Multiple-Testing Overfit Risk (`Jan–Oct 2026`)
- Over **1,008 cycle/round/programme artifacts** were tuned on the exact same **10-month 2026 window (~203 days)**.
- `B-FIX-1` (17 legs) and `N-FIX-1` (8 legs) sliced Jan–Oct into cells, picked the worst cell, and ran a random-subset placebo *on the same Jan–Oct window*. Removing the worst in-sample cell will always beat 99% of random subsets; unsurprisingly, both repairs **worsened** the `Nov 2–13` counterfactual (removing Bank's Nov 4 win and Nifty's Nov 3 win).
- `TARANG-C1/C2` enters SHORT at the `09:15:00` bar open while referencing `vol_ratio_at` on bar 0's volume (only known at `09:20:00`) and assuming zero opening-bell auction slippage.

---

## 3. Concrete Methods to Increase Accuracy (Without Destroying Tail Expectancy)

Because `FORTY` / `LOCK30` / `TRAIL30` proved early profit-taking destroys 50–85% of option-buying P&L, genuine accuracy gains must target **entry quality, Greek alignment, and volatility normalization**:

1. **Bank Nifty Heavyweight Constituent Breadth Filter:** Require ≥ 60% weighted agreement across `HDFCBANK`, `ICICIBANK`, `SBIN`, `KOTAKBANK`, `AXISBANK` (~75% of Bank Nifty weight) on their own session VWAP / OR side before taking a Bank Nifty breakout. Implemented as a reusable helper in `execution_risk_utils.py`.
2. **Replace Fixed `-50 / +90` Option Points with Spot-Invalidation or Volatility-Normalized Stops:** Fixed `-50` is 5.9% noise at 25 DTE (₹850 premium) and an impossible negative stop at 0 DTE (₹38 premium). Use spot-structure invalidation (breakout candle extreme / OR midline) or `% / ATR`-scaled option stops with a `min_premium >= ₹80` floor.
3. **Signal-Candle Exhaustion Filter:** Skip (or require a 30–50% limit pullback on) 5-min breakout candles whose range already exceeds `1.8×–2.0×` 5-min ATR, directly targeting your November entry-bar stop-outs.
4. **Macro Trend Regime + Asymmetric Moneyness (`ITM CE` / `ATM PE`):** Use Spot vs 20-DMA + slope to stop firing counter-trend PE fades into strong multi-day rallies, re-admit CE trend participation in bull regimes, and test **ITM-100/200 (`delta ~0.65`) for CE** (reducing IV-crush/theta drag in grinding uptrends) vs **ATM (`delta ~0.50`) for PE**.
5. **Intraday Contract-Specific IV & Spread Filter:** Use your live 5-min `option_chain_archive` to block entries immediately after sudden contract IV spikes or when bid-ask spread > 1.5–2.0 pts.
6. **Defined-Risk Vertical Debit Spreads (Optional Buyer-Side Upgrade):** Bull Call / Bear Put Debit Spreads keep max loss strictly capped (smaller than naked buying) while neutralizing 40–60% of theta & IV crush on grinding CE days and low-DTE Nifty sessions.
7. **Equity Swing Core (`EKAM Daily 2c` × Value Tier A/B + Regime + ATR Catastrophe Stop):** Combine fundamental quality (`investing_value_analysis_2026-11-14.md` Tier A + clean Tier B) with `EKAM Daily 2c` entries, a Nifty > 200-DMA sizing filter, fixed-rupee sizing, and a wide `3× Daily ATR` catastrophe stop.

---

## 4. Code Fixes Applied (`2026-11-25`)

All fixes below were applied directly to the repo while preserving 100% backwards-compatibility with frozen Jan–Oct control reproductions:

| File | Fix Applied |
|---|---|
| `circuit_breaker.py` | Added `next_day_paused`, `next_pause_kind`, and `next_pause_days_left` to `simulate()` summary so callers know whether the **next** trading day is paused right after an EOD trip. |
| `circuit_breaker_stack.py` | Fixed `currently_paused` to read `summary["next_day_paused"]` instead of `last["paused"]` (which falsely wrote `false` on `2026-11-13` immediately after `HWMDD` tripped). Added `pause_kind` and `last_day_was_paused`. |
| `btstind_shadow_score.py` | Fixed two bugs causing 100% `NC: futures_unserved`: (1) switched `_fetch_fut_day` expiry routing from `day < today` to **`exp < today`** so unexpired contracts aren't sent to `/v2/expired-instruments/`; (2) added same-day `/v3/historical-candle/intraday/` fallback to both `_fetch_spot_day` and `_fetch_fut_day`. |
| `r4d1_shadow_score.py` | Added same-day `/v3/historical-candle/intraday/` fallback to `_fetch_spot_day` and `_fetch_fut_day`, fixing 100% `NC: futures_unserved` on live runs. |
| `oi_buildup_score.py` | Fixed `fetch_bars()` (shared by `premiumtape`, `btstind`, `r4d1`, `oi_v3`): (1) dynamic `exp < today_s` instead of hardcoded `"2026-11-13"`; (2) live `/v2/option/contract` strike-key fallback when newly ATM strikes (e.g. 61500–62300) are missing from static `instruments_cache.json`; (3) same-day `/v3/historical-candle/intraday/` fallback. |
| `premiumtape_ret_shadow_score.py` | Added same-day `/v3/historical-candle/intraday/` fallback to `_fetch_spot_915`. |
| `oi_v3_shadow_score.py` | Fixed 100% `NC: oi_row_spot_mismatch` caused by comparing 09:05 official weighted spot close against 15:25 5-min bar close at `0.05` tolerance: replaced with a `1.5%` corruption guard and logs exact `official_vs_1525_diff` in `notes`. Added same-day intraday fallback to `spot_0920_open`. |
| `forward_candidates_runner.py` | Applied FIX 2 from `feed_fix_report_2026-11-20.md`: falls back to `/v3/historical-candle/intraday/{enc}/minutes/5` when `target == today` and the v3 range route omits today. |
| `nifty_engine_r5_harness.py` | Added backwards-compatible opt-in guards (`gap_stop_open=False, min_stop_px=None`) to `replay_r5` so realistic runs can enforce `stop >= 0.05` and gap-through open fills without breaking frozen Jan–Oct control assertions. |
| `november_shadow_score.py` | Floored logged `stop` column at `max(entry - 50, 0.05)` with an explicit warning note when `entry <= 50` so negative stop prices (like `-11.20` on Nov 17) are never emitted. |
| `execution_risk_utils.py` *(NEW)* | Shared module with realistic NSE intraday/delivery/option cost calculators, fixed-capital equity sizer, volatility-normalized option stops, gap-aware option replay, signal-bar exhaustion check, and Bank Nifty top-5 breadth helper. |
| `pipeline_watchdog.py` *(NEW)* | Read-only operational health monitor that flags 100% `NC` pipelines, lagging ledgers, negative stop prices, stale live producers, and tripped/inconsistent circuit breakers in one command. |
| `pillar1_value_ekam_swing.py` *(NEW — Option A)* | Quality Value (`Tier A` + clean `Tier B`, 37 names) × `EKAM Daily 2c` swing engine with equal-rupee sizing (`₹1,00,000`), realistic NSE delivery taxes + slippage, Nifty 50 200-DMA regime scaling, `3× ATR` catastrophe stop, max 8 positions / 3 per sector caps, and Upstox v3 intraday synthesis fallback (solves the 1-day daily-candle lag). Supports `--mode selftest`, `--mode backtest`, and `--mode live`. |
| `pillar2_index_options_apex.py` *(NEW — Option B)* | Clean 5-rule Regime-Aware Index Option Convexity Engine (`BANKNIFTY` monthly + `NIFTY` weekly/monthly) with Bank Nifty top-5 constituent breadth (`≥ 60%`), signal-bar exhaustion guard (`> 1.8× 5m ATR`), macro 20-DMA/5d regime filter, ITM CE / ATM PE asymmetric strikes, normalized option stops (`min premium ≥ ₹80`), realistic NSE option costs, optional `--structure debit_spread` mode, and live Bid/Ask slippage telemetry (`pillar2_slippage_log.csv`). Supports `--mode selftest`, `--mode backtest`, `--mode live`, and `--mode score`. |
| `run_apex_tomorrow.py` *(NEW)* | Single-command launcher for `--preflight` (08:45 IST), `--backtest` (one-time historical validation on local stores), `--intraday` (09:30–11:35 IST 5-min Pillar 2 scan), and `--eod` (15:40 IST Pillar 1 + Pillar 2 EOD + circuit breaker + watchdog). |

> **Verification & Live-Machine Follow-Ups:** All 15 patched/new Python scripts passed `py_compile` syntax checks, deterministic offline self-tests (`pillar1_value_ekam_swing.py --mode selftest`, `pillar2_index_options_apex.py --mode selftest`, `circuit_breaker.simulate()`, `replay_r5`, `execution_risk_utils`), and live-snapshot watchdog validation (`pipeline_watchdog.py` caught all 15 alerts). On your live machine (`~/workspace/trading`): (1) run `python3 run_apex_tomorrow.py --preflight` before open, (2) run `python3 run_apex_tomorrow.py --backtest` once against your local `data/` stores to review full 2025–2026 numbers, (3) run `python3 circuit_breaker_stack.py` to refresh `currently_paused=true`, and (4) apply FIX 1 from `feed_fix_report_2026-11-20.md` to `ekam_daily_paper_score.py` (not included in this downloaded snapshot).

---

## 5. The 7 Missing Pieces Required Before Live Capital

1. **Multi-Year Walk-Forward Validation (2022–2025 Index Options):** Stop mining `Jan–Oct 2026` alone; freeze rules on 2023–2024 and test blind on 2025–2026.
2. **Explicit Capital & Risk-of-Ruin Budget:** Define exact rupee capital per sleeve, max risk per trade (≤ 1–2% of capital), and hard monthly drawdown caps.
3. **Real-Quote Execution & Slippage Bridge:** Log actual live Ask (entry) / Bid (exit) at signal + 2 seconds, build SL-Limit buffer / retry handling, and measure real vs bar-open slippage before risking capital.
4. **Portfolio-Level Correlation & Daily Kill-Switch:** Enforce a cross-segment daily loss limit and directional exposure cap (Bank Nifty, Nifty, and financial stocks are 0.75–0.90 correlated).
5. **Automated Nightly Health Alerting:** Run `python3 pipeline_watchdog.py` nightly at 20:45 IST and push any non-zero exit directly to your chat.
6. **Clean Production Isolation (`prod/`):** Extract only your 2–3 final production systems into a tested `prod/` directory with zero `exec()` string-patching, and archive the 3,500+ research files.
7. **Complete Governance & Tax Layer:** Automate NSE promoter-pledge, ASM/GSM surveillance, and corporate-action checks for the Value Screener list, plus realistic tax/STT accounting.

---

## 6. Blueprint to Build Something Truly Exceptional ("Apex 3-Pillar Architecture")

Most retail algo programmes fail not because the trader lacks ideas, but because they drown in 15 over-tuned 5-minute strategies fighting transaction costs. You already have the hard parts: an Upstox API pipeline, a 5-min option-chain archive, a strict audit culture, and a solid fundamental screener.

To turn this into something genuinely institutional-grade, **prune from 15 books down to 3 uncorrelated, structurally sound pillars**:

### Pillar 1 — Quality Value + Technical Swing Engine (Compounding Core · 50–60% Capital)
- **Universe:** Your **Value Screener v2 Tier A + clean Tier B** stocks (completed with automated NSE pledge + ASM/GSM + earnings filters) — growing, profitable, reasonable-valuation businesses.
- **Entries & Exits:** **`EKAM Daily 2c`** (Bollinger 20,2 mean-reversion + RSI-14 turn with RSI-upgrade hold), **fixed-capital sizing** (equal ₹ per position, max 8–10 concurrent positions, sector cap ≤ 25%), **Nifty > 200-DMA regime scaling**, and a wide **`3× Daily ATR` catastrophe stop**.
- **Why exceptional:** Low turnover (survives real 0.20% delivery STT + slippage easily), positive long-term drift of Indian equities working *with* you, fundamental downside floor, zero 5-minute microstructure noise, and scalable to any capital size.

### Pillar 2 — Regime-Aware Index Option Trend/Momentum Engine (Asymmetric Convexity · 25–30% Capital)
- **Universe:** Bank Nifty monthly + Nifty weekly/monthly **buying only** (or defined-risk vertical debit spreads on grinding/low-DTE days).
- **Signal (Simple & Non-Overfit — max 4–5 rules total):**
  1. **Opening-Range / Prior-Day Breakout** (your cleanest surviving Bank/Nifty core — strip out all 10-leg cell patches like `B-FIX-1`/`N-FIX-1`).
  2. **Heavyweight Constituent Breadth Confirmation** (≥ 60% Bank Nifty top-5 weight aligned with the breakout).
  3. **Signal-Bar Exhaustion Guard** (skip or limit-pullback if signal bar > `1.8×` 5-min ATR).
  4. **Macro Trend Regime + Asymmetric Moneyness** (no aggressive PE fades into runaway bull thrusts; ITM-100/200 CE when Spot > 20-DMA, ATM PE when Spot < 20-DMA).
  5. **Spot-Structure / Volatility-Scaled Stop** + **Uncapped Runner Exit** (keep the right tail that pays for option buying, with realistic gap-open fills and a `>= ₹80` minimum premium rule).
- **Why exceptional:** Captures explosive directional convexity on trend days (the exact days Pillar 1 is slow) while cutting fakeout whipsaws via constituent breadth and avoiding negative-stop / IV-crush traps.

### Pillar 3 — Event-Driven / Overnight Macro-Neutral Overlay (Uncorrelated Alpha · 10–15% Capital)
- **Focused Post-Earnings Drift (`P2F` / `N4-V3` on Certified Results Only):** Strip out the 24 ticker-specific deletions from the Stock Book and keep *only* the **certified post-results momentum/drift** sleeve — run on **fixed-capital sizing** across liquid NSE F&O names with realistic intraday/3-day swing friction (earnings reactions create genuine multi-day institutional repricing, unlike random 5-minute noise).
- **Unified Risk Engine:** One master portfolio risk layer sitting above all 3 pillars (`circuit_breaker.py` fixed + daily portfolio max-loss stop + correlation cap + `pipeline_watchdog.py` alerting + real-quote slippage telemetry).
