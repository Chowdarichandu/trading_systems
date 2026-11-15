# PaperDesk LIVE-SHADOW Feed — Schema v1

Paper trading display feed. **Paper only — real money ₹0. No broker orders exist anywhere in this stack.**
The numbers in this feed are a **LIVE-SHADOW** viewing layer. The official November 2026 record is the
end-of-day candle-scored log written at ~15:20 IST by the frozen logging job
(`november_paper_bank_log.csv` / `november_paper_nifty_log.csv`). If a live-shadow number and the
official log ever differ, the official log wins.

## Transport

- Canonical file: `live_feed/feed.json` in the private repo `Chowdarichandu/trading_systems` (branch `main`).
- Intended transport (once a secret Gist exists): the same JSON as `feed.json` in a **secret** GitHub Gist;
  the app polls the gist raw URL. Secret-gist raw URLs are fetchable without auth by anyone holding the URL,
  which is what a phone app needs. A private-repo raw URL is **not** fetchable without auth — see
  `live_shadow_run_plan.md` for the current status and the fix options.
- Update cadence: on every order event (entry/exit), and at least every 60 s while any position is open.
- Producer: `live_feed_update.py` (this directory) reading the runner state file
  `live_shadow_state.json` maintained by `live_shadow_runner.py`.

## JSON schema

```jsonc
{
  "schema_version": 1,
  "mode": "LIVE-SHADOW",                 // constant — display layer, not the official log
  "note": "string",                      // human-readable disclaimer
  "date": "2026-11-02",                  // trading date the feed describes (IST)
  "updated_at": "2026-11-02T10:15:30+05:30",  // ISO-8601 IST, refreshed on every update
  "market_open": true,                   // true while NSE session is live (09:15–15:30 IST, trading day)
  "market_state": "open | pre-market | closed | holiday",
  "indexes": {
    "bank":  { ...IndexBlock },          // Bank Nifty — always its own block, never pooled
    "nifty": { ...IndexBlock }           // Nifty — always its own block, never pooled
  }
}
```

### IndexBlock

```jsonc
{
  "label": "Bank Nifty — BNF-PAPER-V1 (LIVE-SHADOW)",
  "system": "BNF-PAPER-V1",              // bank: BNF-PAPER-V1 (lot 30) · nifty: NF-PAPER-C3G7 (lot 65)
  "lot": 30,
  "cost_per_trade_inr": 220,             // assumed cost, deducted on close only
  "open_positions": [ OpenPosition ],
  "closed_today":  [ ClosedTrade ],
  "day_net_inr": 0                       // sum of closed_today[].net_inr for THIS index only
}
```

### OpenPosition

```jsonc
{
  "id": "bank-2026-11-02-CE-1",          // unique per index+date+direction+sequence
  "direction": "CE",                     // CE | PE (long premium; system is buy-only)
  "strike": 52400,
  "expiry": "2026-11-23",
  "instrument": "BANKNIFTY 52400 CE 23-Nov-2026",  // display string
  "entry_time": "2026-11-02T10:35:00+05:30",
  "entry_premium": 762.40,               // live-shadow fill = latest quote at decision time (see run plan)
  "latest_premium": 801.25,              // most recent quote/candle value the runner has seen
  "latest_at": "2026-11-02T11:02:00+05:30",
  "stop": 712.40,                        // current stop level (moves for Nifty G7 runner after +90)
  "target": 852.40,                      // current target (Nifty G7: first +90, then runner target +150)
  "source": "U1:(lA)+V5"                 // contributing component systems, for display/audit
}
```

App-side live P&L for an open position = `(latest_premium − entry_premium) × lot`
(buy-only systems, so direction does not flip the sign; cost is **not** deducted while open).

### ClosedTrade

```jsonc
{
  // all OpenPosition fields, plus:
  "exit_time": "2026-11-02T11:20:00+05:30",
  "exit_premium": 852.40,
  "exit_reason": "target | runner_target | runner_lock | stop | square_off",
  "net_inr": 2480.00                     // (exit − entry) × lot − 220, THIS index's lot
}
```

## Runner state file (`live_shadow_state.json`) — internal, not the feed

The runner owns this file; the updater only reads it. Shape:

```jsonc
{
  "date": "2026-11-02",
  "indexes": {
    "bank":  { "open_positions": [OpenPosition...], "closed_today": [ClosedTrade...],
               "taken_keys": ["CE", "PE"], "base_leg": {...}|null },
    "nifty": { "open_positions": [...], "closed_today": [...], "taken_keys": ["CE"] }
  }
}
```

`day_net_inr` in the feed is computed by the updater from `closed_today`, never trusted from state.

## Rules that must never change

1. Bank and Nifty blocks are computed and displayed **separately**; there is no combined P&L field anywhere.
2. `mode` is always `LIVE-SHADOW`; nothing in this feed may be labelled as the official November log.
3. No credentials, account data, or personal data in the feed — display data only.
