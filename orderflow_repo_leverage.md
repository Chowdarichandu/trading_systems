# trading_system repo — found 2026-10-29 (made public that morning)
Repo: Chowdarichandu/trading_system, public, created 2026-04-25, 281 commits, commit dfda1a7.
Refresh code EXISTS here (not in order_flow): auto_token_refresh.py (headless Playwright, mobile + PIN + TOTP, cron 03:45 weekdays, --check 08:00, --rescue 08:05, 4 retries, writes .env, local HTTPS 127.0.0.1:8080 callback), refresh_token.py (manual --code version), docs/TOKEN_REFRESH.md (2026-06-07). Creds from .env: UPSTOX_MOBILE, UPSTOX_PIN, UPSTOX_TOTP_SECRET, UPSTOX_API_KEY, UPSTOX_API_SECRET. Token expires ~03:30 IST next day.

# order_flow repo — found 2026-10-29, leverage plan

Repo: Chowdarichandu/order_flow, public, created 2026-10-01, updated 2026-10-02, commit 865b4ac.
README: orderflow-zero — read-only NSE cash-equity market data and research on Upstox. Nothing places orders.

## What is actually built (not 'all system')
- T00 scaffold DONE, T01 simulators/decoders DONE, 30 tests passing, simulated 6h 50-stock benchmark 29,992 ticks/s.
- T02/T03/T04/T05 READY, not yet built. T06-T19 NOT STARTED. Recorder NOT deployable yet.
- BOOTSTRAP.md v2 is source of truth.

## Leverageable now
- Definitions: order flow (footprint, delta, CVD, imbalances, OFI, sweeps, absorption, exhaustion, VPIN, Kyle), volume profile (POC/VAH/VAL, naked POC, IB), VWAP bands/anchors, SMC (swings, BOS/CHoCH, OB, FVG, pools, sweeps), levels (PD/week, OR, gaps), context (index/VIX/sector/breadth/time/liquidity/event).
- Zone engine: cluster levels within 0.25 x ATR(14, 5m), with components, freshness, touches, invalidation — LOCATION, not votes.
- Setups S1-S5 pre-registered, with trade plans: stop beyond zone invalidation + 0.1 x ATR, target next opposing zone, reject if reward/risk < 1.5 or target < 3x round-trip cost, forced exit 15:15.
- Validation rules: history tier 2022 onward, purged walk-forward, costs 10/20/30 bps, folds profitable, loss autopsy, holdout used once, layers only via ablation.
- Data contracts / schema in src/orderflow/schema.py, config in config/default.yaml, simulators in T01 for testing without a live token.

## Upstox refresh — exactly T02
- T02 spec: auth (OAuth, daily refresh to token file), preflight (hard/soft, retries 08:30-09:10), expired/missing/401/403 tests, explicit User-Agent always.
- Permanent rules to follow: token read from a 600-permission file at connect, re-read once on 401/403, no env handoffs, never log/print token, log status + sanitized body on auth failure.
- T18 ops timers (later): refresh 03:45, preflight 08:30, recorder 09:00-15:35, history nightly.
- TOTP + headless browser is an implementation method for T02 daily refresh, not a script already in the repo. Secrets (API key/secret, mobile, PIN, TOTP secret) via Secure Vault only, never in code/chat.
- Tokens expire daily ~03:30 IST per BOOTSTRAP — same daily expiry causing today's 401.

## Fit to current work
- order_flow is NSE CASH equities only — fits Stage 2 stocks cash, and Nifty/Bank Nifty as context indices, NOT Bank Nifty options.
- Clubbed unified engine can borrow: zone clustering, S1-S5 as additional setups to test against v4, context layer, and the validation discipline above. Do not present order_flow layers as proven — T06-T15 are unbuilt.
