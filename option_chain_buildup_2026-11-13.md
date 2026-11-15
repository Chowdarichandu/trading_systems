# Option-Chain Build-Up — Feasibility, Archiver, Classifier Demo
**Date:** Fri 2026-11-13 (~05:37–05:45 IST, pre-open) · **Paper/research only** · Owner question 2026-11-13 05:35: *"what about option chain stuff — long build-up, short build-up, long unwinding, short covering?"*

**Standing fact this answers:** no current book in this workspace uses option-chain OI at all. Everything below was probed live this morning against the Upstox API with the workspace token (browser User-Agent on every call). No HTTP 429 was hit; probe stopped at ~12 calls.

---

## 1. FEASIBILITY VERDICT — YES, the data is obtainable, live and historical

### (a) Live chain snapshot — WORKS, and it carries its own yesterday-baseline
`GET /v2/option/chain?instrument_key=<index>&expiry_date=<front expiry>` returned HTTP 200 for both indices pre-open:

| Index | Front expiry | Strikes | Spot served | Per-strike fields |
|---|---|---|---|---|
| NIFTY | 2026-11-17 (weekly) | 142 | 25,299.35 | strike, expiry, per-strike PCR, spot |
| BANKNIFTY | 2026-11-23 (monthly) | 190 | 61,518.50 | strike, expiry, per-strike PCR, spot |

Each side (CE/PE) carries `market_data`: **ltp, volume, oi, close_price (previous session's close), prev_oi (previous session's OI), bid/ask** — plus option greeks. The critical field is **`prev_oi`**: OI change vs the previous close is embedded in every snapshot, so a build-up classification against yesterday does not need a separate baseline fetch. Pre-open, all values are the last completed session's closes (today: Thu Nov 12); live values flow only during market hours.

### (b) Historical OI — EXISTS per contract (daily and intraday), as candle fields
Upstox candles carry **7 fields** — `[timestamp, open, high, low, close, volume, OI]` — verified live this morning:

- **Daily OI history (live contracts):** v3 daily candles for NIFTY 25300 CE (17-Nov expiry) returned 8 sessions (Nov 3 → Nov 12) with a per-day OI value.
- **Daily OI history (expired contracts):** `/v2/expired-instruments/` lists Nifty expiries back to **2024-10-03**; contracts for the 2026-11-09 expiry (294) and their daily candles with OI all returned 200. So day-over-day OI history is backfillable in principle for ~2 years.
- **Intraday OI history:** v3 5-minute candles carry per-bar OI — a range query for the same 25300 CE returned **324 bars (Nov 6 → Nov 12)** with OI moving bar to bar (470,795 at Nov 6 09:15 → 7,104,370 at Nov 12 15:35, the last value matching this morning's chain OI exactly). The workspace's stored October premium files were fetched the same way and also carry the OI field — it was in the data all along, simply never used. (Quirk recorded: a *single-day* minutes query returned 0 bars while the multi-day range query worked — range queries are the reliable route. The old v2 candle endpoint does not accept a 5-minute interval at all.)

### What does NOT exist — stated plainly
- **No historical chain snapshots.** The chain endpoint is live-only; yesterday's 10:35 chain state can never be re-fetched as a snapshot. Past intraday OI can only be *reconstructed* contract-by-contract from candles — possible, but a heavy build (every strike × every day), and it is **not built**.
- **No precomputed build-up series anywhere** — no labels, no history of the four quadrants. The forward archive (below) is the first one, and it starts today.
- **Therefore:** day-over-day build-up *could* be backtested after a deliberate candle-OI reconstruction build (not started, not claimed); intraday build-up can only be collected **forward** from today. One snapshot proves plumbing only — **no backtest claim is made anywhere in this note.**

---

## 2. THE FORWARD ARCHIVER — built, tested live this morning

**Script:** `~/workspace/trading/option_chain_snapshot.py`
**Command line (exactly this; scheduling is the parent's to add):**
```bash
cd ~/workspace/trading && python3 option_chain_snapshot.py
```
Each invocation: resolves each index's front expiry from the instrument master (day-cached), pulls both full chains (2 API calls), and appends one row per strike to dated CSVs under `~/workspace/trading/option_chain_archive/` (`nifty_YYYY-MM-DD.csv`, `banknifty_YYYY-MM-DD.csv`).

**Columns:** `timestamp_ist, bucket_ist, index, expiry, strike, spot, ce_oi, ce_prev_oi, ce_ltp, ce_close, ce_volume, pe_oi, pe_prev_oi, pe_ltp, pe_close, pe_volume, row_pcr` — the task's required fields plus `prev_oi`/`close`/`volume`, which the classifier needs.

**Safety properties, all verified in this morning's test:**
- Idempotent per 5-minute bucket: the second invocation printed `bucket 05:35 already archived — skipped` for both indices and wrote nothing (file counts unchanged).
- Tolerant of missing strikes/sides (absent market data becomes empty cells, never a crash).
- HTTP 429 → hard stop, nothing written, exit code 3.
- Token read from the workspace `.env`, never printed.

**Rows written on the live test (bucket 05:35 IST, pre-open):** BANKNIFTY 190 strikes (expiry 2026-11-23) · NIFTY 142 strikes (expiry 2026-11-17). First NIFTY row as written:
`2026-11-13T05:38:44+05:30, 2026-11-13T05:35:00+05:30, NIFTY, 2026-11-17, 20850, spot 25299.35, ce_oi 0, ce_prev_oi 0, pe_oi 829920, pe_prev_oi 741260, …`

**Suggested cadence for the parent to schedule:** every 5 minutes during market hours (09:15–15:30 IST, Mon–Fri), plus one pre-open (~09:05) and one post-close (~15:35) run. Cost is 2 API calls per run — light.

---

## 3. BUILD-UP CLASSIFIER — defined, and demonstrated on this morning's snapshot

**Definition** (`classify_buildup(price_change, oi_change)` in the script, applied per leg — CE and PE separately — and aggregated per index):

| Price | OI | Quadrant |
|---|---|---|
| ↑ | ↑ | **LONG_BUILDUP** |
| ↓ | ↑ | **SHORT_BUILDUP** |
| ↓ | ↓ | **LONG_UNWINDING** |
| ↑ | ↓ | **SHORT_COVERING** |
| either is 0 / missing | | FLAT_OR_UNKNOWN |

**Demo baseline:** a yesterday baseline **was obtainable** — it is embedded in the chain itself (`oi` vs `prev_oi`, `ltp` vs `close_price`). So this demo classifies **the last completed session (Thu Nov 12) vs the Nov 11 close**, read off this morning's pre-open chain. It is a plumbing demonstration, not a signal reading.

**BANKNIFTY** (spot 61,518.50; Bank rose +539.85 on Nov 12):
- Aggregate ΔOI vs prev close: **CE +157,830 · PE +1,914,030** · Total OI: CE 16,802,010 / PE 21,455,400 · **PCR(OI) 1.277**
- Near the money (61,300–61,700), every strike reads the same way: **CE LONG_BUILDUP** (e.g. 61,500 CE premium 467.35 → 644.00, ΔOI +157,680) and **PE SHORT_BUILDUP** (premium fell, OI rose — puts written into the rise).
- All 380 legs: SHORT_BUILDUP 115 · SHORT_COVERING 81 · LONG_UNWINDING 63 · LONG_BUILDUP 27 · FLAT_OR_UNKNOWN 94.

**NIFTY** (spot 25,299.35; expiry-week build into Nov 17):
- Aggregate ΔOI vs prev close: **CE +37,026,470 · PE +38,188,670** · Total OI: CE 180,563,890 / PE 153,925,850 · **PCR(OI) 0.852**
- ATM 25,300: **CE SHORT_BUILDUP** (premium 183.70 → 179.10, ΔOI +1,882,595 — call writing into a small rise) and **PE SHORT_BUILDUP** (premium 288.05 → 188.25, ΔOI +1,533,870).
- All 284 legs: SHORT_BUILDUP 141 (dominant) · SHORT_COVERING 47 · LONG_UNWINDING 32 · LONG_BUILDUP 7 · FLAT_OR_UNKNOWN 57.

**Caveats, plainly:** far-OTM legs with zero/stale prices fall into FLAT_OR_UNKNOWN by construction; pre-open values are last-close values, so nothing here describes *today's* positioning — that starts with the 09:15 snapshot.

---

## 4. HONEST FORWARD PLAN

1. **Archive first, claims later.** Run the archiver on the 5-minute cadence from today, Fri 2026-11-13.
2. **Gate no earlier than 20 trading days of archive** — i.e. alongside the SHORT-FOLLOW forward window (Nov 13 → Dec 10). Twenty days × ~75 buckets gives, per index, the intraday ΔOI paths and day-over-day build-up labels needed to join build-up states to subsequent price action and run a first gate under the standing controls gate (timing audit, placebos, halves, ex-top-3). Before that bar: no gating, no signal claims, no book.
3. **Optional accelerant, not started:** a one-time reconstruction of *daily* OI history from per-contract daily candles (expired-instruments API reaches back to Oct 2024) would give day-over-day build-up labels for a faster first look. It is a heavy fetch (hundreds of contracts × hundreds of days), it cannot reproduce intraday chain states, and any result from it would still need the same controls gate. Recommend deciding after the forward archive's first week shows the plumbing is clean.
4. Nothing in this note touches any live book, the December live intention, or tomorrow's chain — it is a data asset being built ahead of any decision that uses it.

*Files: `option_chain_snapshot.py` · `option_chain_archive/nifty_2026-11-13.csv` (142 rows) · `option_chain_archive/banknifty_2026-11-13.csv` (190 rows) · probe chains saved at `/tmp/chain_NIFTY_2026-11-17.json`, `/tmp/chain_BANKNIFTY_2026-11-23.json`.*
