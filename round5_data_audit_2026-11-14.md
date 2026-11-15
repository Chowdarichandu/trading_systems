# Round 5 — Speed Track A: intraday data audit, Bank Nifty

**Audit date:** 2026-11-14  
**Scope:** Bank Nifty near-month futures and expired near-ATM Bank Nifty options, Jan–Oct 2026 plus Nov 2026. Read-only audit; no ledger or other research file was modified.

## Headline verdict

- **Per-contract intraday OI: YES.** The historical 5-minute candle responses carry an open-interest value on every candle, and that value changes bar by bar. This is **not** merely the option-chain snapshot archive: the expired-instruments candle route returns intraday OI historically.
- **Intraday traded volume: YES.** Every returned futures and option candle also carries a per-5-minute traded-volume value.
- **Futures coverage:** the near-month futures series already fetched by Round 4 covers **205/205 Jan–Oct trading days** in full, and **8/8 valid Nov trading days through 2026-11-12** in full.
- **Option sample coverage:** all **22/22** directly sampled near-ATM CE/PE contract-days (one pair for each of Jan–Oct plus 2026-11-11) returned a complete day of 75 or 77 candles, with both volume and OI.
- **Fixed-pair option range diagnostic:** for one fixed mid-month ATM CE/PE pair per monthly expiry, **359/368 in-force contract-days (97.6%)** returned at least one 5-minute candle — CE **180/184**, PE **179/184**. The gaps are concentrated in fixed strikes that were not that particular day's liquid ATM strike; they are not evidence that the route or that day's actual ATM pair was unavailable. Some returned fixed-strike days are partial, so a strategy builder still needs a full-day completeness check.

## Exact candle schema

Both the expired-instruments route and the current-contract v3 route return `data.candles` as arrays. Every audited candle had exactly **7 positions**:

| Position | Field |
|---:|---|
| 1 | timestamp, ISO 8601 with `+05:30` |
| 2 | open |
| 3 | high |
| 4 | low |
| 5 | close |
| 6 | **volume traded in that 5-minute bar** |
| 7 | **open interest at that bar** |

Identification checks:

- Position 6 behaves as bar volume: for 2026-01-16 60100 PE, the 75 intraday position-6 values sum to **3,203,400**, exactly the corresponding daily candle's volume. For the paired CE they sum to 3,582,720 versus the daily file's 3,582,750 (a 30-unit/one-lot difference).
- Position 7 behaves as a point-in-time OI snapshot: it changes through the day rather than repeating a daily constant. Across the direct samples it had **57–77 distinct values in a 75/77-bar day** for options and **65–76 distinct values** for futures.
- Example, futures on 2026-01-16: first candle `[2026-01-16T09:15:00+05:30, 59833.0, 59900.0, 59800.0, 59897.2, 39030, 1218660]`; last candle `[2026-01-16T15:25:00+05:30, 60191.2, 60210.0, 60172.0, 60210.0, 24780, 1356810]`.

## Routes used

All calls used the required browser User-Agent. **No HTTP 429 was encountered.**

### Futures

- Expired contracts:  
  `GET /v2/expired-instruments/historical-candle/{instrument_key}/5minute/{to}/{from}`
- Nov 2026 live/current contract:  
  `GET /v3/historical-candle/{instrument_key}/minutes/5/{to}/{from}`

The futures instrument keys and route selection were taken from `round2_history/futures_keys.json`, the same source used by `round4_data_build.py`.

### Options

- Expired contract discovery:  
  `GET /v2/expired-instruments/option/contract?instrument_key=NSE_INDEX|Nifty Bank&expiry_date={expiry}`
- Expired option candles:  
  `GET /v2/expired-instruments/historical-candle/{instrument_key}/5minute/{to}/{from}`
- Nov 2026 current-contract candles:  
  `GET /v3/historical-candle/{instrument_key}/minutes/5/{to}/{from}`

This is the same expired-instruments mechanism used by `oi_buildup_score.py`; that scorer reads only timestamp + OHLC from each raw candle and discards positions 6 and 7.

## 1. Futures audit

### Direct one-day samples

One near-month futures contract was sampled in every month. Every sample returned HTTP 200 / `status: success`, a full day, and only 7-wide candles.

| Sample date | Expiry | Bars | Distinct volume values | Distinct OI values |
|---|---|---:|---:|---:|
| 2026-01-16 | 2026-01-27 | 75 | 71 | 73 |
| 2026-02-13 | 2026-02-24 | 75 | 67 | 74 |
| 2026-03-16 | 2026-03-30 | 75 | 74 | 72 |
| 2026-04-17 | 2026-04-28 | 75 | 68 | 69 |
| 2026-05-15 | 2026-05-26 | 75 | 72 | 70 |
| 2026-06-15 | 2026-06-30 | 75 | 69 | 73 |
| 2026-07-16 | 2026-07-28 | 75 | 65 | 72 |
| 2026-08-17 | 2026-08-25 | 77 | 70 | 73 |
| 2026-09-16 | 2026-09-29 | 77 | 70 | 73 |
| 2026-10-16 | 2026-10-27 | 77 | 67 | 71 |
| 2026-11-11 | 2026-11-23 | 77 | 76 | 72 |

### Full-range coverage already on disk

Round 4 fetched complete futures ranges before transforming them. Counting the in-force contract for each trading day in its stored `round4_history/FUT5_*.json` files gives:

| Month | Trading days with a full futures day | Bars/day |
|---|---:|---:|
| Jan 2026 | 20/20 | 75 |
| Feb 2026 | 21/21 | 75 |
| Mar 2026 | 19/19 | 75 |
| Apr 2026 | 20/20 | 75 |
| May 2026 | 19/19 | 75 |
| Jun 2026 | 21/21 | 75 |
| Jul 2026 | 23/23 | 75 |
| Aug 2026 | 21/21 | 77 |
| Sep 2026 | 21/21 | 77 |
| Oct 2026 | 20/20 | 77 |
| **Jan–Oct total** | **205/205** | — |
| Nov 2026 through Nov 12 | **8/8 valid trading days** | 77 |

Notes:

- The stored FUT5 file also contains a 16-bar fragment dated 2026-11-08; that was a non-session/Sunday fragment and is excluded from the valid trading-day count.
- Round 4 documented that 2026-11-13 futures returned zero candles on the night of Nov 13 (data lag). That does not affect the through-Nov-12 coverage above.
- The bar-count convention changes in the source data: Jan–Jul days have 75 bars (09:15–15:25 in the samples), while Aug–Nov days have 77 bars (09:15–15:35).

## 2. Expired near-ATM options audit

The strike for each monthly sample is the ATM strike recorded for that sample date in `oi_history/banknifty_daily_oi.csv`. For Nov, the sample is 2026-11-11, strike 60800 — the CE strike actually traded by the November legacy book that day.

### Direct one-day samples

Every CE and PE sample returned HTTP 200 / `status: success`, a complete 75- or 77-bar day, and only 7-wide candles.

| Sample date | Expiry | ATM strike | CE bars (distinct vol / OI) | PE bars (distinct vol / OI) |
|---|---|---:|---:|---:|
| 2026-01-16 | 2026-01-27 | 60100 | 75 (75 / 75) | 75 (73 / 74) |
| 2026-02-13 | 2026-02-24 | 60200 | 75 (73 / 72) | 75 (73 / 74) |
| 2026-03-16 | 2026-03-30 | 54300 | 75 (64 / 57) | 75 (62 / 60) |
| 2026-04-17 | 2026-04-28 | 56600 | 75 (69 / 67) | 75 (60 / 59) |
| 2026-05-15 | 2026-05-26 | 53800 | 75 (68 / 73) | 75 (71 / 67) |
| 2026-06-15 | 2026-06-30 | 57200 | 75 (72 / 73) | 75 (71 / 73) |
| 2026-07-16 | 2026-07-28 | 57600 | 75 (69 / 75) | 75 (72 / 73) |
| 2026-08-17 | 2026-08-25 | 57500 | 77 (76 / 75) | 77 (77 / 76) |
| 2026-09-16 | 2026-09-29 | 56300 | 77 (76 / 75) | 77 (75 / 76) |
| 2026-10-16 | 2026-10-27 | 55800 | 77 (76 / 75) | 77 (74 / 76) |
| 2026-11-11 | 2026-11-23 | 60800 | 77 (76 / 76) | 77 (74 / 73) |

### Fixed-pair range diagnostic

To estimate broader retrievability without fetching every strike, I also range-fetched the same fixed CE/PE pair for each monthly expiry and counted dates **only while that contract was in force** (through its expiry). Dates after expiry are not missing coverage: the next monthly contract is then in force.

| Expiry month | In-force trading days | CE days returned | PE days returned | Notes |
|---|---:|---:|---:|---|
| Jan 2026 | 17 | 17 | 17 | Full 75-bar days |
| Feb 2026 | 18 | 18 | 18 | One PE day has 74 bars |
| Mar 2026 | 19 | 15 | 19 | Fixed 54300 CE absent Mar 2, 4, 5, 6; some CE days partial |
| Apr 2026 | 18 | 18 | 17 | Fixed PE absent Apr 7; one PE day has 50 bars |
| May 2026 | 17 | 17 | 17 | One CE day is partial (13 bars minimum observed) |
| Jun 2026 | 21 | 21 | 17 | Fixed 57200 PE absent Jun 1, 3, 5, 8; some PE days partial |
| Jul 2026 | 20 | 20 | 20 | Full 75-bar days |
| Aug 2026 | 17 | 17 | 17 | Full 77-bar days |
| Sep 2026 | 20 | 20 | 20 | 76–77 bars/day |
| Oct 2026 | 17 | 17 | 17 | Full 77-bar days |
| **Total** | **184** | **180** | **179** | **359/368 contract-days, 97.6%** |

Interpretation of the gaps: the range diagnostic holds one strike fixed for a whole expiry cycle. Spot moves, so that strike is not every day's ATM and can be illiquid or not yet active on some dates. Therefore:

- A missing fixed-strike day must **not** be read as “no intraday OI exists that day.”
- The correct build pattern is the one the books already use: select each day's actual near-ATM strike(s), then fetch that contract-day.
- “At least one candle returned” is not the same as a strategy-ready full day. The partial fixed-strike days (notably Mar CE, May CE, Jun PE) require the existing completeness rule: reject/NC a contract-day that does not cover the required intraday window.

November fixed-pair caution: the 60800 pair was far below the spot early in November (spot rose from about 55k to about 61k). Over Nov 2–12 the CE returned all 8 valid trading days (plus the Nov 8 non-session fragment), while the PE returned only Nov 9, 11 and 12. That is a strike-selection/liquidity effect, not a route failure — on the sampled day, Nov 11, both 60800 CE and PE returned complete 77-bar days with volume and OI.

## 3. What Round 4 stored — and what it discarded

**Round 4's stored FUT5 series does NOT carry volume or OI columns.**

Each `round4_history/FUT5_*.json` row has exactly six entries:

`[date, time, open, high, low, close]`

Stored row counts are nevertheless useful for coverage and are the basis of the futures coverage table above:

| Futures expiry | Stored rows | Unique dates in stored file |
|---|---:|---:|
| 2026-01-27 | 2,925 | 39 |
| 2026-02-24 | 3,075 | 41 |
| 2026-03-30 | 3,000 | 40 |
| 2026-04-28 | 2,775 | 37 |
| 2026-05-26 | 2,850 | 38 |
| 2026-06-30 | 3,000 | 40 |
| 2026-07-28 | 3,075 | 41 |
| 2026-08-25 | 3,184 | 42 |
| 2026-09-29 | 3,157 | 41 |
| 2026-10-27 | 3,003 | 39 |
| 2026-11-23 | 2,403 | 32 |

Why the fields are absent: `round4_data_build.py` receives the raw 7-wide API candles but its `fetch_contract()` explicitly writes only `(date, time, open, high, low, close)` — positions 6 (volume) and 7 (OI) are stripped at build time. So the fields were **available and discarded**, not present-but-ignored in the stored files.

Related stored-data observations:

- The raw response files under `oi_buildup_data/` that contain candles are also 7-wide: **638 non-empty raw response files** were inspected and every candle in them had width 7. However, `oi_buildup_score.py` transforms them to `(time, open, high, low, close)` before scoring, again discarding volume and OI.
- `oi_history/contracts/*.json` are **daily** contract candles with `[date, open, high, low, close, volume, OI]`; they prove day-level OI/volume, not intraday granularity. The intraday proof comes from the direct 5-minute samples above.

## Bottom line for the invention tracks

1. **Stop waiting for an archive to obtain historical intraday OI.** Per-contract 5-minute OI is retrievable historically through the expired-instruments candle route for expired Bank Nifty futures and options, and through v3 for the current Nov contract.
2. **Preserve positions 6 and 7 in every new build.** Existing Round 4 / OI-programme transforms strip them; any new dataset must store `[timestamp, open, high, low, close, volume, oi]` intact.
3. **Build by each day's actual ATM strike and enforce full-window completeness.** Near-ATM liquid contract-days sample complete; fixed far/illiquid strikes can be absent or partial on some days and must be NC, never silently filled.
