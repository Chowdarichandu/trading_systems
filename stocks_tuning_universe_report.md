# Stocks EQUITY — Tuning Loop LINE 4: Universe Expansion Transfer Test

**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders. Real money ₹0.**
**All figures provisional per 100 shares, ₹40/trade flat cost. Window Jan–Oct 2026 (Oct = 1–28 Oct).**

**Question:** every surviving candidate on the original 25-stock watchlist
concentrates in GLENMARK + TVSMOTOR. Do the frozen rules work on stocks they
were never tuned on? **No rule is modified in this line** — the frozen rules
transfer verbatim or they fail.

Rules under test (frozen specs):
- **DBL-LONG** — `stocks_dbl_candidate_spec.md` (P2 pool + DBL condition, LONG-only, T125/S050)
- **MORNING-MOVER SECOND SIGNAL** — `stocks_vline_v2_candidate_spec.md` (U5b pre-moved skip-first-signal, T125, cap 2)
- **P2F @2.0%** — `stocks_p2f_november_shadow_spec.md` (results reaction ≥2% → R+1 open follow-through, T125)

Gate read (pre-declared): both halves (Jan–May / Jun–Oct) net positive **AND**
breadth ≥ 10/25 = **TRANSFERS**; anything else = **does not transfer**.

---

## Step 1 — New universe build

**New universe (25):** the most liquid Nifty-50 constituents NOT in the original
watchlist, all listed for years (none listed after Jan 2026; TATAMOTORS skipped
for its Oct-2025 demerger ambiguity):
RELIANCE, TCS, ICICIBANK, INFY, BHARTIARTL, SBIN, LT, AXISBANK, KOTAKBANK,
BAJFINANCE, HCLTECH, MARUTI, SUNPHARMA, TITAN, M&M, ULTRACEMCO, NESTLEIND,
POWERGRID, ONGC, COALINDIA, JSWSTEEL, GRASIM, CIPLA, DRREDDY, EICHERMOT.

**Fetch:** same verified Upstox connector path as `fetch_vol_janoct.py`
(`fetch_vol_ext_janoct.py`): 5-min candles WITH volume, Jan–Oct 2026 →
`data/progressive_vol_ext/<SYM>/spot_5m_vol.csv`; daily-endpoint candles
2025-01-01..2026-10-28 → `daily_api.csv`; engine-compat `spot_5m.csv` +
`spot_daily.csv` under `data/progressive_ext/` (2026 daily derived from the
5-min bars exactly as the original cache was built; 2025 rows from the daily
endpoint so the new universe has the same 50DMA/20DMA/ADR lookback the
original universe had). NIFTY 5-min + daily copied from the original cache.

**Instrument keys:** the `/v2/instruments/search` endpoint returns 401 today,
so keys are `NSE_EQ|<ISIN>` with ISINs from the NSE Indices NIFTY-50
constituent list (the 7 ISINs overlapping the original `keys.json` matched
exactly). Four names 400'd on every request because their ISIN **changed
after a stock split** and Upstox serves only the current ISIN; refetched
(`fetch_vol_ext_fixup.py`) with the current ISINs:
KOTAKBANK INE237A01028→INE237A01036 (1:5 split), BAJFINANCE
INE296A01024→INE296A01032 (NSE circular NSE/CML/68472, split ₹2→₹1 w.e.f.
16 Jun 2025), NESTLEIND INE239A01016→INE239A01024 (1:10 split Jan 2024),
DRREDDY INE089A01023→INE089A01031 (1:5 split Oct 2024). The other 21 names
fetched clean on the first pass: **15,375 bars each** (205 trading days × 75).

**Event calendar** (`stock_event_calendar_ext_jan_oct_2026.csv`, built by
`build_ext_calendar.py`): same method as the original — quarterly results
board-meeting dates from Moneycontrol Board Meetings tables, cross-checked
against Financial Express board-meeting tables (the two agreed in every
case); `after_market = unverified` → `reaction_date` = next trading day in
the stock's own fetched daily series; `window_start/end` = ∓7 trading days,
mirroring the original calendar's convention. 99 events (25 stocks × 4
quarters, minus EICHERMOT Q2 FY27 whose board date was not confirmed as of
2026-10-31 — excluded; its R+1 would fall outside the window either way).
Q2 rows dated after 2026-10-28 (8 stocks) are included for completeness and
are excluded by the engines' window filters.

**Verification (all 25 stocks, `verify_ext_data.py` →
`universe_ext_verification.json`):**
- **Bars:** every stock exactly **15,375 bars = 205 trading days × 75 bars**;
  **zero days with ≠75 bars** for every stock. (The 205 days are 1 Jan–30 Oct;
  all engines restrict scoring to ≤28 Oct via their frozen window filters,
  exactly as on the original universe — the original cache's in-window span
  is the same 203 trading days, 1 Jan–28 Oct.)
- **OHLC self-consistency (0 tolerance):** for every stock-day, the daily
  row equals first-bar open / max high / min low / last-bar close of its
  5-min bars — **0 violations in 5,125 stock-days**.
- **Zero-volume bars:** 0.807% in every ext stock — exclusively the 15:15
  and 15:20 tail bars on 62 days. The original universe shows the same
  property (RECLTD 0.797%, same two timestamps), i.e. a shared Upstox data
  trait; all rule logic runs 09:15–15:10, so it touches nothing.
- **Daily cross-check (independent source):** the daily-ENDPOINT closes
  differ from the 5-min-derived closes — median |diff| ≈ 0.05–0.07% of
  price, p90 ≈ 0.29%, worst day 1.19% (ULTRACEMCO 2026-03-13). This is the
  exchange official close (closing-session VWAP) vs last-bar close. **Both
  universes use the 5-min-derived daily in every engine** (that is how the
  original cache was built), so the treatment is identical; the difference
  is disclosed here, not hidden. The daily endpoint matches the derived
  series on all 203 in-window dates present in both (it simply ends at
  28 Oct, the requested chunk end).
- **Lookback:** every stock has 249 daily rows in 2025 (full prior year) —
  50DMA/20DMA/ADR lookbacks have the same depth as the original universe.
- **Calendar:** 99 results events built; 89 have an in-window reaction date.

**Step 1 verdict: universe built complete — 25/25 names, no shortfall.**

---

## Step 2 — Transfer tests on the NEW 25 alone (frozen rules verbatim)

All figures provisional per 100 shares, ₹40/trade, paper only.

### (a) DBL-LONG — **DOES NOT TRANSFER**

| | |
|---|---|
| Trades | 61 (old universe: 133) |
| Net | **+₹6,570.64** (expectancy +₹107.72/trade, win 27.9%) |
| Jan–May | +₹9,910.27 (54 trades) |
| Jun–Oct | **−₹3,339.63 (7 trades) — half fails** |
| October | −₹2,755.13 (5 trades) |
| Breadth | **5/25 — fails** |
| Top-3 share | **316.6%** (MARUTI +₹12,142.50 alone = 185% of net; then M&M +₹5,289.26, LT +₹3,368.75; TCS worst −₹3,950.50) |

Why so few trades: the P2 pool itself nearly vanishes on liquid large caps —
237 pool rows vs 918 on the old universe — because the ADR≥3% stock-day gate
rarely passes on RELIANCE/TCS-class names. Context rows: ext INV1 201 trades
+₹35,107.79 but halves +₹46,360.85 / **−₹11,253.06**; ext DBL both-dir 126
trades +₹43,053.69, halves +₹45,004.34 / −₹1,950.65. On this universe the
whole below-trend complex made its money in Jan–May and lost it back in
Jun–Oct — the mirror image of the old universe. The rule does not transfer;
what it was harvesting on the watchlist is not present, in this form, on
liquid large caps in H2.

### (b) MORNING-MOVER SECOND SIGNAL — **TRANSFERS**

| | |
|---|---|
| Chains / trades | 199 chains, 300 trades (old: 424 chains, 698 trades) |
| Net | **+₹164,483.29** — expectancy **+₹826.55/chain**, chain win 59.8% |
| Jan–May | **+₹73,142.55** (126 chains) |
| Jun–Oct | **+₹91,340.74** (73 chains) |
| October | **+₹39,984.55** |
| Breadth | **22/25** |
| Top-3 share | 48.8% (EICHERMOT +₹39,721.48 on 13 chains, LT +₹20,601.19, M&M +₹19,988.47; only 2 stocks negative — JSWSTEEL −₹1,721.18, KOTAKBANK −₹477.87 — and 1 with no qualifying chains, ICICIBANK) |

Both gate legs pass with room to spare, and the rule is **stronger on the
new universe than on the one it was tuned on** (+₹826.55/chain vs
+₹199.71/chain; breadth 22/25 vs 16/25). Fewer qualifying days (large caps
pre-move ≥1% before 10:00 less often), but when they do, the second-signal
follow-through is cleaner. Leg split: chains with a second (re-entry) trade
+₹89,198.43 (101 chains); single-trade chains +₹75,284.86 (98) — on this
universe both legs pay (on the old universe the re-entry leg was the weak
one). This is the first rule in the entire stocks search whose edge
**grows** off its home universe.

### (c) P2F @2.0% — **DOES NOT TRANSFER** (gate read, unsoftened)

| | |
|---|---|
| Trades | 51 (old: 48) |
| Net | +₹3,086.69 (expectancy **+₹60.52/trade** vs +₹267.41 on the old universe) |
| Jan–May | **−₹196.26 — half fails** |
| Jun–Oct | +₹3,282.95 |
| October | +₹2,907.21 (7 trades) |
| Breadth | 13/25 positive (23 stocks traded) — breadth leg passes |
| Top-3 share | **438.0%** (EICHERMOT +₹5,936.87, TITAN +₹4,202.50, RELIANCE +₹3,380.87 against a long tail of small losers) |
| T10 shadow column | −₹98.65 total (H1 −₹2,465.16 / H2 +₹2,366.51) |

The total is positive, but the pre-declared gate is both-halves-positive AND
breadth ≥10/25: Jan–May is negative, so the verdict is **does not
transfer**. Disclosed plainly: the H1 shortfall is ₹196.26 — roughly one
trade's cost — but the gate is the gate, and the expectancy collapse
(+₹267 → +₹61) plus a 438% top-3 share say the old universe's P2F edge was
substantially its specific names (GLENMARK/OBEROIRLTY/BDL-class reactions),
not a generic large-cap results-follow-through effect.

---

## Step 3 — Combined 50 (old + new pooled)

| Rule | Net | Jan–May | Jun–Oct | October | Breadth | Top-3 share |
|---|---|---|---|---|---|---|
| DBL-LONG (194 trades) | +₹30,898.01 | +₹25,336.88 | +₹5,561.13 | +₹5,202.82 | 15/50 | **126.5%** |
| Morning-Mover (623 chains, 998 trades) | +₹249,155.03 | +₹126,026.74 | +₹123,128.29 | +₹56,809.97 | 38/50 | **34.1%** |
| P2F (99 trades) | +₹15,922.57 | +₹3,301.84 | +₹12,620.73 | +₹2,804.38 | 27/50 | **95.8%** |

**Does pooling cure the concentration?**
- **DBL-LONG: No.** TVSMOTOR (+₹15,287.54) + GLENMARK (+₹11,666.52) are
  still the top-2 and alone are 87% of the pooled net; MARUTI (+₹12,142.50)
  simply joins them as a third carrier. The pooled halves read positive
  only because the old universe's Jun–Oct carries the new universe's
  Jun–Oct failure (−₹3,339.63 above) — pooling masks the transfer failure,
  it does not repair it.
- **P2F: No.** Top-3 = 95.8% of the pooled net; GLENMARK is still #2. The
  pooled book is the same few reaction names with a second universe's
  near-zero expectancy (+₹60.52) diluting the old one (+₹267.41 → pooled
  +₹160.83).
- **Morning-Mover: concentration was never its disease, and pooling
  improves it further** — top-3 share falls from 60.7% (old) and 48.8%
  (ext) to 34.1%, breadth 38/50, halves balanced (+₹126k / +₹123k). It is the
  only one of the three whose pooled book looks healthier than either half
  alone.

## Bottom line

Of the three frozen candidates, **only the Morning-Mover Second Signal
transfers** to stocks it was never tuned on — decisively (both halves
strongly positive, breadth 22/25, and a higher per-chain expectancy than at
home). **DBL-LONG and P2F do not transfer**: DBL-LONG fails both gate legs
on the new universe (H2 negative, breadth 5/25, one stock = 185% of net),
and P2F fails the halves leg with its expectancy cut by three-quarters and
a 438% top-3 share. The GLENMARK/TVSMOTOR concentration the parent thread
was worried about is therefore **real for DBL-LONG and P2F** — their edges
live in specific names — while the Morning-Mover's edge is a market-wide
intraday behaviour, not a watchlist artefact. Pooling to 50 stocks does not
cure DBL-LONG/P2F concentration; it only averages it with the old book.

**Files:** this report; `stock_event_calendar_ext_jan_oct_2026.csv`;
`universe_ext_verification.json`; engine copies `stocks_equity_reentry_ext.py`,
`stocks_equity_round8_ext.py`, `stocks_reaction_profiles_ext.py` (+
`stocks_reaction_profiles_val.py`); scorer `stocks_tuning_universe.py`;
fetch `fetch_vol_ext_janoct.py` + `fetch_vol_ext_fixup.py`; trade rows
`universe_ext_dbl_long_trades.csv`, `universe_ext_morningmover_trades.csv`,
`universe_ext_profiles_P2_ungated_T125_trades.csv` (old-universe counterparts
`universe_old_*`); data under `data/progressive_ext/` and
`data/progressive_vol_ext/`.

**Machinery reuse (what was reused, exactly):** the frozen engines were
copied by exact string substitution only (`make_universe_copies.py`; every
substitution occurrence-asserted, and reverse-substituting the copies
reproduces the originals **byte-for-byte**):
- `stocks_equity_reentry_ext.py` ← reentry head: data path →
  `data/progressive_ext`, SYMBOLS → new 25, calendar → ext calendar. Nothing
  else. (This is the V5 signal stream — v4 + skill_or detectors, `pool_pick`,
  DAYCTX — it has no watchlist-specific artefacts beyond the symbol list and
  paths being substituted.)
- `stocks_equity_round8_ext.py` ← round8: exec target → reentry_ext, ADR
  paths → `progressive_ext`. `run_chain` / `replay_plain` untouched.
- `stocks_reaction_profiles_ext.py` ← profiles engine: data paths →
  `*_ext`, SYMBOLS → new 25, calendar → ext calendar, output filenames
  prefixed `universe_ext_`. P2 (ungated) logic untouched.
- DBL-LONG / Morning-Mover scoring in `stocks_tuning_universe.py`:
  regime maps, `cond_dbl`, `p2_filter`, `build_cell`, `block` copied from
  `stocks_tuning_inv.py`; `build_chain` / `replay_plain` / `chain_stats`
  copied from `stocks_tuning_vline.py` (breadth denominator parametrized).
  Fresh chain caches (`tuning_universe_cache_ext`) — no old-universe cache
  reuse. **Engine nuance (disclosed):** in the vline code the pre-move is
  measured from the 09:30 bar's open (first DAYCTX candle) to the 09:55 bar's
  close — the code is the authority, as it was for the in-sample anchors.

**Validation before transfer (same machinery, OLD universe — all PASS to
the paisa):**
- Profiles copy (output-prefix-only variant): P1-ungated T125 anchor
  +₹2,924.79 exact; **P2F: 48 trades, +₹12,835.88, halves +₹3,498.10 /
  +₹9,337.78, breadth 14/25; T10 +₹9,301.03** — all exact.
- DBL machinery: INV1 694 / +₹22,964.30 (halves +₹7,255.01 / +₹15,709.29);
  DBL both-dir 390 / +₹16,548.78 (+₹7,861.57 / +₹8,687.21); **DBL-LONG 133 /
  +₹24,327.37 (halves +₹15,426.61 / +₹8,900.76), October +₹7,957.95, breadth
  10/25, top-3 share 129.0%** — all exact.
- Morning-Mover: **424 chains, 698 trades, +₹84,671.74, halves +₹52,884.19 /
  +₹31,787.55, October +₹16,825.42, breadth 16/25** — exact.

