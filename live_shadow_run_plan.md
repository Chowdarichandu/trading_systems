# PaperDesk LIVE-SHADOW — Run Plan (first live day: Mon 2026-11-02)

Paper only. Real money ₹0. No broker orders exist in this stack — the runner only
READS market data and maintains paper state. **Monday's official November record
remains the end-of-day candle-scored logs** (`november_paper_bank_log.csv`,
`november_paper_nifty_log.csv`, written ~15:20 IST) regardless of anything the
live-shadow layer shows during the day.

## Components

| Piece | Path | Role |
|---|---|---|
| Runner | `live_shadow_runner.py` | 09:15–15:30 loop: quotes, paper entries/exits, state |
| State | `live_shadow_state.json` | Runner-owned positions state (schema doc: `live_feed_schema.md`) |
| Signal bridge | `live_shadow_signals.json` | Entry directives from an intraday signal producer (format below) |
| Feed updater | `live_feed_update.py` | State → feed payload → publish target |
| Feed | `live_feed/feed.json` in `Chowdarichandu/trading_systems@main` | What the PaperDesk app polls |
| Kill switch | `live_shadow_KILLSWITCH` | Create the file → runner squares off, pushes final feed, exits |
| Log | `live_shadow_runner.log` | Append-only audit of every runner action |

## Feed transport — current status (read before Monday)

- The Muse **GitHub connector has no Gist tools** (verified 2026-11-01 against its live
  tool catalog), and `gh` on this VM is not authenticated, so a secret Gist could
  not be created in this build. The prescribed fallback was used: `feed.json`
  lives in the repo `Chowdarichandu/trading_systems` at `live_feed/feed.json`
  (created 2026-11-01, commit `321f157`), and `live_feed_update.py` updates it
  through the connector (gist PATCH is already coded for the day a
  `PAPERDESK_GIST_ID` + `GITHUB_TOKEN` exist in the environment).
- ⚠️ That repo is **private**: its raw URL
  (`https://raw.githubusercontent.com/Chowdarichandu/trading_systems/main/live_feed/feed.json`)
  returns 404 without auth, so the iPhone app **cannot poll it as-is**.
  Clean fixes, in order of preference:
  1. Create a **secret Gist** (one-time: authenticate `gh` or enable a gist-capable
     route) and point `FEED_URL` at the gist raw URL — secret-gist raw URLs are
     fetchable without auth by URL-holders only, and the updater already supports it.
  2. Put `feed.json` in a separate **public, feed-only repo** (display data only —
     never make `trading_systems` itself public; it holds all the trading code).
  Until one of these is done, the app installs and runs but shows the bundled
  empty state / connection error. This is a transport blocker, not an app bug.

## The honest signal gap (do not paper over this)

The frozen primaries are built on U1, whose components — (lA) v2, V5 v2, Tuned
Skill V3, Volrix tuned (b) — were scored historically from **stored spot-signal
files produced by separate backtest pipelines** (`aggressive_score.base_legs`
reads `historical_proof_*_trades.csv`). There is **no importable live U1 signal
generator** in `~/workspace/trading`, and re-deriving four systems' intraday
logic would be invention, not reuse. Therefore:

- The runner **never invents entries**. It consumes directives from
  `live_shadow_signals.json` and itself enforces every frozen rule that is
  mechanical: unique-once, Bank B2 filters (Skill V3 CE block; Skill-solo
  ≤09:55 drop), NS1 second-leg conditions (base exited by target/stop ≤13:30,
  signal ≤14:30, room_ratio ≥1.5, bearish-day CE block), Nifty C3 ≥2-source
  confirmation, ATM strike, expiry-in-force, G0/G7 exit state machines,
  15:10 square-off, 1-lot caps.
- Directive format (producer-written, one file per day):
  ```json
  {"date": "2026-11-02", "directives": [
    {"id": "bank-base-1", "index": "bank", "kind": "BASE",
     "direction": "CE", "signal_time": "10:35", "sources": ["(lA)", "V5"]},
    {"id": "bank-ns1-1", "index": "bank", "kind": "NS1_SECOND",
     "direction": "PE", "signal_time": "13:05", "sources": ["NS1"],
     "room_ratio": 1.8, "bias": "bullish"}]}
  ```
- **Monday mode:** run the runner in OBSERVE/bridge mode. If no intraday signal
  producer is wired before 09:15, no live-shadow entries occur — the feed stays
  at its empty state and the day is carried, as designed, by the official EOD
  log. Wiring a producer = any process that writes directives in the format
  above (e.g. Muse's intraday checks); that is a separate, deliberate step,
  not something to improvise mid-session.
- Controls (U1-B2 / U1-N1) are not run live at all; they exist only in the
  official log. The feed's two sections are the two PRIMARIES, labelled LIVE-SHADOW.

## Launch recommendation for Monday

**Recommendation: a systemd user service, not cron-per-minute.**
The runner is a session-long stateful loop (quote polling every ~15 s, exit
checks on every quote, 60 s feed pushes). Cron-per-minute would either miss
intra-minute stop/target crossings or require re-implementing the loop as
stateless minute slices — more failure modes for no benefit. A service gives
one process, clean restart-on-failure, and a journal.

```ini
# ~/.config/systemd/user/paperdesk-live-shadow.service
[Unit]
Description=PaperDesk LIVE-SHADOW runner (paper only)
[Service]
ExecStart=/usr/bin/python3 /home/hatch/workspace/trading/live_shadow_runner.py
Restart=on-failure
RestartSec=30
[Install]
WantedBy=default.target
```
Start it before 09:15 (`systemctl --user start paperdesk-live-shadow`) or add a
timer for 09:10 Mon–Fri. It self-terminates at 15:30. Do NOT enable it today
(Sunday) — first live day is Mon 2026-11-02, after the 03:45 token refresh and
08:00 token check have run.

Pre-open checklist (Monday):
1. `upstox-auto-token-refresh` (03:45) + token check (08:00) green — the runner
   reads `UPSTOX_ACCESS_TOKEN` from `upstox_refresh/.env`.
2. Delete any stale `live_shadow_KILLSWITCH`; delete/ignore any
   `live_shadow_signals.json` not dated today (the runner ignores wrong-date files).
3. Verify the v3 intraday endpoints on the first live morning
   (`/v3/historical-candle/intraday/{key}/minutes/1`, `/v3/market-quote/ltp`) —
   these are the same v3 family the verified 1-min fetches used, but the
   *intraday* variant has not yet been exercised live by this stack.
4. Confirm the instruments-master download resolves Bank expiry 2026-11-23
   (the verified November Bank monthly expiry) before the first entry.

## Live-shadow vs official log — expected differences

| Aspect | LIVE-SHADOW (this stack) | Official EOD log (authoritative) |
|---|---|---|
| Entry premium | Latest LTP quote at decision time | Open of the 5-min option candle at the entry bar |
| Exit trigger | Quote ticks, checked ~every 15 s | 5-min candle bars, stop-before-target per bar |
| Exit premium | LTP at the crossing tick | Candle-based per frozen scoring |
| Signal source | Bridge directives (see gap above) | Full U1 component scoring on the day's data |
| Controls | Not run | U1-B2 / U1-N1 logged as CONTROL |
| Status | Viewing layer, labelled LIVE-SHADOW | The November record; pass/fail judged on it alone |

Small numerical differences between the two are therefore expected and are not
errors. Any large divergence is a bug to investigate after the close — never a
reason to edit the official log.
