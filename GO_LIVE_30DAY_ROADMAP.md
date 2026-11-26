# 30-Day Go-Live Readiness Roadmap & Missing Production Modules

**Prepared:** `2026-11-26` · **Scope:** Moving from `₹0` paper research to real-money NSE trading within 30 days **without** blowing up on hidden execution, data, or software bugs.

> **Core rule:** Never go live on a calendar date — go live when **both** (A) at least one strategy clears realistic NSE costs + matched placebo across multi-year data AND (B) every production safety module below has survived 2 full weeks of live-equivalent paper execution with zero critical faults.

---

## Part 1 — Order Flow, Volume Profile & Footprint (Honest Feed Reality)

Built in `orderflow_footprint_engine.py`:
- **Why Index Futures (`BANKNIFTY FUT`, `NIFTY FUT`) instead of Spot:** NSE spot indices carry **zero volume and zero order book**. Real Volume Profile (`POC`, `VAH`, `VAL`, `HVN`, `LVN`), Footprint `Bid × Ask` ladders, CVD, L2 Order Book Imbalance (`OBI`), and OI buildup only exist on **Near-Month Futures** (plus ATM CE/PE option tape via `--with-options`).
- **Retail Snapshot Limit (Upstox vs NSE TBT Colocation):** Upstox serves ~1–2 aggregated depth snapshots/sec, not exchange tick-by-tick (TBT). Our engine classifies each live incremental `ΔVolume` causally via the **Lee-Ready Quote Rule** against prior-tick best Bid/Ask — giving ~90–95% accurate live proxy Footprint, CVD, 3:1 diagonal/stacked imbalances, and Absorption alerts.
- **Zero Fabrication Policy:** Backfilled 1-min Futures candles seed **Volume Profile only** (`pPOC/pVAH/pVAL` and developing `dPOC/dVAH/dVAL`). Footprint Bid/Ask delta and OBI come **strictly from live snapshots**, archived daily to `data/orderflow_snapshots/YYYY-MM-DD/snapshots.jsonl` so you build a real, replayable Order Flow history.

---

## Part 2 — 30-Day Paper-Trading Protocol Before Real Money

### Week 1 (Days 1–7): Close Data Holes, Start Snapshot Archiving & Run the Kill Gate
1. **Backfill all missing history:**
   - Index spot (2024–2026), all 5 Bank Nifty breadth heavyweights, and 2025–2026 expired/active option candles (`backfill_index_2025_2026.py`).
   - Full Value Tier A + clean Tier B daily equity stores if trading Pillar 1.
2. **Start daily live Order Flow recording** (`orderflow_footprint_engine.py --mode live --with-options`) every session 09:15–15:30 IST to build your real Bid/Ask + Footprint tape.
3. **Run the full honest gate** (`index_apex_lab.py --mode gate` + matched cost-identical placebos):
   - **Kill** every strategy that is negative after realistic NSE taxes + 2 pt/side slippage, negative ex-top-3, or below the 90th-percentile matched placebo.
   - Select **at most 1–2 surviving strategies** to carry into Week 2.

### Week 2 (Days 8–14): Live-Quote Paper Execution ("Zero-Bar-Open-Illusion")
Stop scoring paper trades off idealized 5-minute bar opens! For every paper signal:
1. **Paper entry fill = live Best Ask** (at `signal_time + 2s` realistic execution delay), NOT the 5-min candle open.
2. **Paper exit fill = live Best Bid** (on stop, target, or square-off).
3. **Log exact latency & slippage every trade:**
   - `signal_bar_close_time` vs `decision_timestamp` vs `quote_timestamp`
   - `entry_slippage = live_ask - bar_open`
   - `exit_slippage = bar_close - live_bid`
   - `spread_at_entry = best_ask - best_bid`
4. **Enforce real capital & margin accounting:** Deduct realistic Upstox brokerage, STT, NSE transaction fee, SEBI fee, stamp duty, and 18% GST on every single paper trade (`execution_risk_utils.py`).
5. **Track from flat in one master paper ledger** — no retroactive edits, no cherry-picking which signals count.

### Week 3 (Days 15–21): Failure-Injection & Micro-Execution Dry-Run
Before risking ₹1 of strategy capital, deliberately break your own system during paper runs and verify it recovers cleanly:
1. **Token-expiry drill:** Start at 08:45 IST with an expired/missing token → verify your pre-market health check alerts you before 09:00 IST.
2. **Network disconnect / timeout drill:** Disconnect Wi-Fi for 90 seconds while a paper position is open → verify auto-reconnect, no duplicate re-entry, and accurate state reconciliation on recovery.
3. **HTTP 429 rate-limit drill:** Verify clean backoff/halt without leaving an unmonitored open stop-loss.
4. **Kill-switch drill:** Trigger `KILLSWITCH` while 1+ positions are open → verify every open leg flattens cleanly, cancels all resting SL orders, and refuses new entries for the rest of the session.
5. **Broker plumbing sanity test (tiny controlled test):** On 1 share of a ₹50 liquid NSE stock (or Upstox sandbox), verify `place_order`, `modify_order`, `cancel_order`, `get_order_details`, and `get_positions` work end-to-end with your exact auth token and `client_order_id` idempotency.

### Week 4 (Days 22–30): 5-Session Code Freeze & Go/No-Go Sign-Off
1. **Zero code edits for 5 consecutive trading sessions** (Mon–Fri).
2. **Nightly reconciliation every day at 15:45 IST:**
   - `pipeline_watchdog.py` exits **`0`** (zero `CRITICAL`, zero `HIGH` alerts) all 5 days.
   - Paper ledger fills match recorded live Bid/Ask tape within `< 2 pts` on 100% of trades.
   - Realized paper slippage matches or beats backtest cost assumptions.
   - Daily & monthly circuit breakers (`circuit_breaker.py` fixed) verified accurate every evening.
3. **Day 31 Go-Live Sizing Rule:** Start with **1 minimum lot** (or 25% of planned capital) for the first 20 live trades; scale up *only* after live broker contract notes match paper expectations.

---

## Part 3 — The 8 Modules Genuinely Missing Before Real Money

Your repo currently has strong research & paper-scoring scripts, **not** live execution infrastructure. These 8 modules are genuinely missing and required before sending real broker orders:

| # | Missing Module | Why It Is Non-Negotiable Before Live Capital |
|---|---|---|
| **1** | **Order Management System (OMS) & Broker Position Reconciler** | Prevents double orders on retries via unique idempotent `tag` / `client_order_id`; tracks `PENDING → OPEN → PARTIAL → FILLED → REJECTED`; reconciles local `state.json` against Upstox `/v2/portfolio/short-term-positions` & `/v2/order/retrieve-all` every 30s and halts immediately on any mismatch! |
| **2** | **SL-Limit Execution & Gap-Chase / Retry Engine** | NSE/brokers restrict naked SL-M orders on index options. You need an **SL-Limit order manager** with dynamic trigger-to-limit buffer (e.g., `trigger - 5 pts` limit on stop exit) + automatic **reprice/chase loop** if price gaps past the limit so a stop-loss never sits unfilled while losses snowball! |
| **3** | **Pre-Trade Risk Firewall & Margin Guard** | Hard-coded independent safety layer sitting *below* every strategy: checks Upstox `/v2/user/get-funds-and-margin`, enforces max lots per order, NSE freeze-quantity slicing, max daily rupee loss across ALL books combined, max orders/minute runaway-loop breaker, and hard `15:15 IST` auto-flatten. |
| **4** | **08:30 IST Automated Pre-Market Health & Token Verifier** | Verifies Upstox token via `/v2/user/profile`, refreshes `NSE.csv.gz`, checks NSE holiday calendar & active expiry rollover, checks disk space/clock sync, and sends a phone alert BEFORE 09:00 IST if anything is broken. |
| **5** | **Real-Time Alerting & Remote Kill-Switch (Telegram / Webhook)** | Instant push notifications for every order fill, rejection, position mismatch, watchdog alert, and daily PnL summary — plus a remote kill-switch command so you can flatten everything from your phone if your laptop/server glitches. |
| **6** | **Live Slippage, Spread & Latency Telemetry Aggregator** | Summarizes `live_ask - signal_bar_open`, `bid_ask_spread`, and execution latency across every paper & live trade so you immediately spot if broker execution drag is eating your edge. |
| **7** | **EOD Broker Tradebook & Contract-Note Tax Reconciler** | Pulls Upstox `/v2/order/trades/get-trades-for-day` at 15:45 IST, computes exact statutory taxes/charges (brokerage, STT, exchange txn, stamp, GST), and flags any 1-paise discrepancy vs your strategy ledger. |
| **8** | **Clean `prod/` Package Isolation + Frozen Configs + `pytest` Suite** | Extracts ONLY the 1–2 live strategies + OMS + Risk Firewall + Watchdog into a clean, version-pinned `prod/` folder with unit tests and zero `exec()` string-patching — completely isolated from the 3,500+ research files. |
