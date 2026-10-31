# Stocks v2 highest-tuned — FINAL, Fri 2026-10-30, 09:00 IST deadline

Paper only, cash intraday only, no options, no orders. Rupees ONLY as "per 100 shares, provisional — NOT a lot profit". Index totals never pooled with stocks. 25 stocks: GODREJCP, GLENMARK, ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL, HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC, HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR.

User bar (all together): 1 valuable stock trade/day, net positive, full-target above S2's 19.7%, cumulative rising month by month, no forced trades. Index separate.

## Ranked highest-tuned — Jan–Oct 2026 in-sample (Oct 1–28, 203 trading days)

| Rank | Version | Trades | /day | Win net>0 | Full-target | Net ₹ provisional | Expectancy | Legs passed |
|---|---|---|---|---|---|---|---|---|
| **1 — HIGHEST-TUNED** | **S9 (S8 + event gate, G-TIERED)** | **50** | **0.246** | **50.0%** | **26.0%** | **+₹1,640.00** | **+₹32.80** | Net ✓, Full-target ✓, No-forcing ✓; Frequency ✗, Cumulative ✗ |
| 2 | S8 (previous best kept) | 54 | 0.27 | 50.0% | 22.2% | +₹932.50 | +₹17.27 | Net ✓, Full-target ✓; Frequency ✗, Cumulative ✗ |
| 3 | S7 | 51 | 0.25 | 51.0% | 21.6% | +₹722.50 | +₹14.17 | Net ✓, Full-target ✓; Frequency ✗, Cumulative ✗ |
| 4 | (lA) v2 — no-event, 1/day | 175 | 0.862 | 30.3% | 24.0% | −₹22,093 | −₹126.25 | Full-target ✓ only (+ near-frequency) |
| 5 | V5-stock — no-event, 1/day | 202 | 0.995 | 31.2% | 23.8% | −₹32,850 | −₹162.62 | Full-target ✓, Frequency ✓ (by construction); Net ✗, Cumulative ✗ |
| 6 | Skill v2 (OR-only) — no-event, 1/day | 203 | 1.000 | 30.0% | 23.2% | −₹45,835 | −₹225.79 | Full-target ✓, Frequency ✓ (by construction); Net ✗, Cumulative ✗ |
| 7 | Combined v2 (deduped, 1/day) — no-event | 203 | 1.000 | 30.5% | 22.7% | −₹45,210 | −₹222.71 | Full-target ✓, Frequency ✓ (by construction); Net ✗, Cumulative ✗ |
| 8 | Volrix v2 — no-event, 1/day | 134 | 0.660 | 42.5% | 0% (square-off only, by construction) | −₹40,783 | −₹304.35 | None (full-target 0% by design) |

**Verdict, plainly: NO version meets all legs. Highest-tuned is S9, and S9 is NOT adopted.**
S9 passes net and full-target and honours no-forcing, but fails frequency (0.246/day) and cumulative progression, so it does not go on an adoption-track November log on this evidence. The v2 versions "pass" frequency only because their 1/day capped series picks 1 trade per day from a huge uncapped pool of weak OR signals — that is forcing by construction, and it destroys net (−₹22k to −₹46k). Frequency without conviction is not valuable.

## S9 detail (frozen gate mode G-TIERED, chosen before scoring)
- S8 price design unchanged + Event Gate v1 tiered thresholds: post-reaction days S8 thresholds unchanged; no-event days room ≥2.0× OR prospective ≥₹1,000 provisional; single-stock news days (management_change, large_order, fda_approval, block_deal, sector_policy) room ≥2.0× any phase; pre-announcement neutral, S8 thresholds unchanged; cap ranking post-reaction > single-news > pre-announcement > no-event.
- Funnel: scanned 5,075 → OR pass 4,859 → CE armed 215 → pullback 138 → second-close 56 → S8 uncapped 81 → gate survivors 69 → gate-blocked 12 → capped 50 (19 survivors capped out).
- Exits: 24 stops, 12 stops-after-partial-BE, 13 targets-after-partial, 1 square-off. The 50% net>0 includes 12 partial-BE wins, never counted as targets.
- Setup split: setup3 PE 41, setup4 pullback CE 9, setup2 0. PE +₹825.00; CE +₹815.00 (down from S8 CE +₹1,960 — gate ranking displaced BDL CE 2026-05-05, +₹710, for INDUSTOWER CE same day, −₹435).
- Gate tiers, capped: no-event 30 trades −₹885.00 (still negative despite the stronger bar); post-reaction 8 trades +₹1,050.00 (only 3 wins, driven by two January targets); pre-announcement 9 trades +₹640.00; single-news 3 trades +₹835.00 (all pre-announcement, 2 of 3 partial-BE, no reaction-day single-news trade tested). Blocked shadow (12, all no-event): −₹1,802.50.
- Month cumulative: Jan +₹2,375 → Feb +₹1,855 → Mar +₹1,210 → Apr +₹425 → May −₹110 → Jun −₹1,050 → Jul +₹765 → Aug +₹1,800 → Sep +₹2,160 → Oct +₹1,640. **Not rising month by month.** Ex-March +₹2,285.00; ex-October +₹2,160.00.
- Days: traded 50; no S8 candidate 147; gate-blocked-all 5; capped-out 1 (147+5+1+50=203). No forcing.
- Per-stock: GLENMARK 7 +₹1,545; HINDALCO 2 +₹955; ASTRAL 8 +₹720; OBEROIRLTY 5 +₹660; TVSMOTOR 9 +₹590; BDL 6 +₹575; worst UNITDSPR 5 −₹1,595 (0 targets). Zero-trade (12): IRCTC, ITC, KALYANKJIL, NATIONALUM, NHPC, NTPC, OIL, PFC, RECLTD, TATASTEEL, VEDL, WIPRO.
- Files: [new_stock_system_s9_frozen.md](sandbox://workspace/trading/new_stock_system_s9_frozen.md), [stock_system_s9.py](sandbox://workspace/trading/stock_system_s9.py), [s9_trades_jan_oct_2026.csv](sandbox://workspace/trading/s9_trades_jan_oct_2026.csv), [s9_result_oct30.md](sandbox://workspace/trading/s9_result_oct30.md)

## v2 versions detail (no-news days only, frozen before scoring)
- V5-stock: V4 + Skill-v2 pool, dedup same symbol+date by setup rank (setup4>setup3>setup2>skill_or), prospective ≥₹500.
- Skill v2: "Skill-v2 OR-only" (first 5-min close beyond OR by 11:30, no bias/room) — the variant that passed Jul–Sep in earlier tuning but was NOT adopted.
- (lA) v2-stock: Nifty confirms the stock (not Bank confirming Nifty), earliest pooled signal ≥ Nifty break time and ≤11:30 in Nifty's direction; re-entry max 1/day if morning stops, relative risk band [0.5×, 1.0×] morning risk; afternoon stop-on-first-fail to 15:05. Re-entry leg contributes 0 trades to the capped series and loses uncapped (303 trades, −₹8,276).
- Volrix v2-stock: prev-day close ≤ −2% → next session long only, 09:15 open, 15:10 square-off, no stop/target (frozen, not optimised).
- No-event day = outside ALL calendar windows (±7 trading days around each event). Excluded as event-window trades: V5 450/1,566; Skill v2 1,055/3,985; (lA) v2 565/2,112; Volrix 155/656. The filter removes 24–29% of trades but flips no version's sign.
- Month cumulative rising fails for all v2 versions (only January starts green for V5/Skill/Combined; (lA) v2 ends at −₹22,093 after Jan +₹100).
- Files: [stocks_v2_versions_oct30.md](sandbox://workspace/trading/stocks_v2_versions_oct30.md), [stocks_v2_versions_oct30.py](sandbox://workspace/trading/stocks_v2_versions_oct30.py), per-version trade CSVs in ~/workspace/trading/stocks_v2_*_noevent_*.csv
- Caveat: Volrix uncapped on ALL days (656 trades, −₹9,711, 49.1% net>0) is out of scope for the verdict (includes event days, uncapped, no target) — do not quote it as a pass. Its in-scope no-event 1/day form is the worst expectancy of the four.

## This week Oct 26–29, separately, NOT pooled with Jan–Oct
- **Cache ends 28 Oct 2026. Oct 29 has NO stock data in the cache — reported as missing data, not a zero-trade day.** The Oct 26–29 check therefore covers 26–28 only.
- S9 / S8: 0 uncapped candidates 26–28 Oct, 0 gate survivors, 0 capped trades. Last S8 candidate in October is 12 Oct; 13–28 Oct produced none. Week CSVs are header-only for that reason.
- v2 no-event, 1/day, Oct 26–28 (3 trades each): V5 −₹1,020; Skill v2 −₹4,210; (lA) v2 −₹1,355; Volrix v2 −₹100; Combined −₹4,210. Three days prove nothing alone.
- Sentiment test in this window: S8 has 0 trades on 26, 27, 28 Oct, so risk-on / risk-off / neutral win rates are **undefined (0/0), not 0%**. No sentiment edge, or lack of one, can be claimed from S8 for 26–28 Oct. Sole capped-set trade that week is S6 KALYANKJIL on 26 Oct (neutral day), setup4 CE, stop, −₹740 — n=1, meaningless for sentiment.

## Geopolitics + global sentiment, Oct 26–30 (source + date per tag; verified news kept separate from tags)
- **26 Oct — neutral:** Nifty 22,753.20 (+0.68%) after a weak, risk-off open; Brent >$114, Middle East tensions, Fed-eve caution, VIX up to 17.16; FII −₹1,462.49 cr, DII +₹2,609.57 cr (Moneycontrol, 26 Oct).
- **27 Oct — neutral (HDFCBANK risk-off override):** Nifty 22,749.75 (−0.02%, flat); Brent ~$115.8, Fed eve; FII +₹4,240.39 cr, DII −₹1,250.03 cr (Moneycontrol/CNBC TV18, 27 Oct); pharma/realty/media +2–3%, private banks/IT weak.
- **28 Oct — risk-off (GLENMARK, HDFCBANK neutral overrides):** Nifty 22,698.85 (−0.22%) after intraday −1.11%; Houthi-claimed Saudi Ras Tanura refinery attack (Saudi authorities had not immediately confirmed), Brent ~$115.9, Fed decision day, IT −3.5%; FII +₹871.83 cr, DII +₹643.35 cr (CNBC TV18, 29 Oct reporting 28 Oct).
- **29 Oct — risk-on (TVSMOTOR neutral override, Auto sole faller):** Nifty 22,936.75 (+1.05%), Sensex 74,151.04 (+1.24%); Fed held 3.75–4.00% on 10–2 vote (28 Oct); Brent easing to ~$114; FII −₹943.60 cr, DII +₹1,924.41 cr (CNBC TV18, 29 Oct).
- **30 Oct — risk-off, PRE-MARKET ONLY (written ~08:30 IST, before the open; no close/FII-DII exists yet; replace after the close, do not backfill):** Overnight US 29 Oct: Nasdaq −1.38% to 26,184.72, S&P −0.30%, Dow −0.25% on Alphabet −12.6% AI-spend sell-off, plus Amazon/Intel after-hours falls; Asia down (Kospi −3.96%), GIFT Nifty flat/muted ~23,027–23,028, BOJ decision due later.
- **Company-specific global/geopolitical news for any of the 25 stocks individually: no influencing news found** in the sources checked — CSV factors are market-wide/sector, not company news.
- Conflicts flagged, not smoothed over: rupee closes differ by source (28 Oct: 95.28 vs 95.22; 29 Oct: 95.25 vs 95.26); 28 Oct Sensex MarketsMojo outlier (73,108.25) rejected vs consistent 73,246.03; 30 Oct Brent snapshots conflict ($111.29–$117.40 by time/source) — only "still elevated, above $110" asserted for 30 Oct morning; a low-authority claim of ~₹6,000 cr FII selling on 28 Oct was rejected against provisional exchange figures.
- Files: [stocks_sentiment_oct26_30.md](sandbox://workspace/trading/stocks_sentiment_oct26_30.md), [stocks_sentiment_tags_oct26_30.csv](sandbox://workspace/trading/stocks_sentiment_tags_oct26_30.csv) (125 rows, 25 stocks × 5 days)

## Next family (tuning continues — "till I am satisfied", no tuning-closed)
1. **New setup2-PE room definition, frozen as its own version** (from the S8 diagnosis): setup2 PE requires a close below PDL, so there is no PD level below the entry for the room test — rescuing it needs a structural level below PDL, not room loosening (which has already failed in S2–S6).
2. S9's no-event leg is still negative (−₹885 on 30 trades despite room ≥2.0× / prospective ≥₹1,000) — the next gate iteration must address no-event losses specifically, not just add more event trades.
3. Do NOT adopt S9, and do NOT put S9 on an adoption-track November log on this evidence. November 2026 paper (from Mon 2026-11-02, separate from the Nifty log, no re-tuning during November) remains validation for any version that later passes all legs in-sample. The 30-minute stock reports requested by the user are a parent-agent scheduling decision, not set by this task.
