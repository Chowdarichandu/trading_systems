# Stocks Progressive Tuning — continuous, paper only

Cash intraday stocks only, 25 stocks, no options, no orders, no live trading.
All rupee totals are **per 100 shares, provisional — NOT a lot profit**.
Index totals are never pooled into stock totals.
Nothing is adopted on in-sample alone — November 2026 paper (from Mon
2026-11-02, separate from the Nifty log, no re-tuning during November)
remains validation, but that does NOT stop tuning now.
User bar (all together): 1 valuable stock trade/day, net positive,
full-target rate above S2's 19.7%, cumulative rising month by month,
no forced trades. 09:00 on 2026-10-30 is NOT a deadline or stop point —
this log is updated every 30 minutes with what was found.

## Baseline (carried forward, verified 2026-10-30)
- S1: 18 trades, 22.2% full-target, -₹1,875.94, 0.42/week
- S2 (best kept before S7): 61 trades, 59.0% net>0, 19.7% full-target, -₹785.98, 1.39/week
- S7: 51 trades, 51.0% net>0, 21.6% full-target, +₹722.50, 0.25/day
- S8: 54 trades, 50.0% net>0, 22.2% full-target, +₹932.50, 0.27/day, 147 no-setup days of 203
- S8 uncapped: 81 trades, -₹922.50 (cap ranking is what makes capped S8 positive)
- Setup2 diagnosis: 0 uncapped survivors — PE fails second close on 47 and
  "no room below" on 45 of 95 find_signal setup2 days; structural, because
  setup2 PE requires a close below PDL, so no PD level below entry exists
  for the room test. Setup2-PE needs a NEW room definition (family after S9).
- Event layer v1: 115 events (100 results + 15 curated non-results);
  S7 in-window 14 trades +₹2,235 vs no-event 37 trades -₹1,512.50, but S2
  reverses it (in-window -₹951.40) — events do NOT cleanly explain moves,
  and do NOT raise candidate frequency (1.44 vs 1.52 per 100 stock-days).

## Progress section — 2026-10-30 ~08:10 IST (Families 1–2)

### Family 1: S9 = S8 + frozen event gate v1 (G-TIERED) — SCORED, NOT ADOPTED
Frozen spec: `new_stock_system_s9_frozen.md` (written before scoring);
engine `stock_system_s9.py`; report `s9_result_oct30.md` (parallel run,
CSV totals re-verified here exactly: 50 trades, +₹1,640.00, 26.0%
full-target, 50.0% net>0). Gate: post-reaction = S8 thresholds;
pre-announcement = same (neutral); no-event = room ≥2.0× OR
prospective ≥₹1,000; single-stock news (CEO, large order, FDA, block
deal, sector policy) = room ≥2.0× any phase; cap ranking tier
post > single > pre > no-event, then target net → room → setup.
- Before (S8 capped): 54 trades, +₹932.50, 22.2% full-target, 0.27/day.
- After (S9 capped): 50 trades, **+₹1,640.00**, 26.0% full-target,
  50.0% net>0, expectancy +₹32.80, **0.246/day**, 1.14/week.
- Funnel: S8 uncapped 81 → gate survivors 69 → gate-blocked 12
  (all no-event PE, shadow net -₹1,802.50) → capped 50 (19 survivors
  capped out, shadow -₹760.00). Days: 50 traded, 147 no S8 candidate,
  5 gate-blocked-all, 1 capped-out = 203.
- Legs: CE 9 trades +₹815.00; PE 41 trades +₹825.00; setup2 0.
  Tier capped: no-event 30 trades -₹885.00 (gate did NOT make the
  no-event leg profitable); post-reaction 8 trades +₹1,050.00
  (January-heavy, 2 targets carry it); pre 9 trades +₹640.00;
  single-news 3 trades +₹835.00 (all PRE-announcement, 2 partial-BE
  wins — reaction-day single-news rule untested in-sample).
  Tier ranking cost: displaced BDL CE 2026-05-05 (+₹710.00, no-event)
  for INDUSTOWER CE same day (-₹435.00, post-reaction).
- Month cumulative: Jan +₹2,375 → Feb +₹1,855 → Mar +₹1,210 →
  Apr +₹425 → May -₹110 → Jun -₹1,050 → Jul +₹765 → Aug +₹1,800 →
  Sep +₹2,160 → Oct +₹1,640. Ex-March +₹2,285, ex-October +₹2,160.
- This week Oct 26–29: **0 S9 trades, ₹0 on 0 trades (empty slice,
  not a result)** — cache has 26–28 Oct only, 0 S8 candidates those
  days (last S8 candidate in October is 2026-10-12); Oct 29 has NO
  stock 5-min data in cache and is reported as missing, not zero.
- Verdict: net PASS, full-target PASS (26.0% > 19.7%), frequency
  FAIL (0.246/day), cumulative FAIL (falls Jan→Jun, negative May–Jun),
  no forcing PASS. **S9 NOT adopted, no adoption-track November log
  created, no re-tuning on this window.**

### Family 2: Volrix-for-stocks (intraday adaptation) — SCORED, FAILED HARD
Frozen spec: `stocks_family2_volrix_for_stocks_frozen.md` (frozen
before scoring); engine `stocks_family2_volrix.py`; trades
`stocks_family2_volrix_trades_jan_oct_2026.csv` (capped) /
`stocks_family2_volrix_uncapped_jan_oct_2026.csv`.
Rules: trigger prev-day close ≤ -2% vs close before; entry next
trading day 09:15 open; exit 15:10 close; NO stop/target/give-back;
cooldown 10 sessions per stock after an entry; cap 1/day,
1/stock/week, ranking largest prev-day drop first.
- Uncapped: 282 trades, -₹16,334.00, 48.6% win, expectancy -₹57.92,
  113 days with a candidate (trigger days before cooldown/cap: 656).
- Capped: **113 trades, -₹28,612.00, 44.2% win, expectancy -₹253.20,
  0.56/day** — frequency is the closest yet to 1/day, but deeply
  negative, and the cap ranking (largest drop first) makes it WORSE
  than uncapped (-₹28,612 vs -₹16,334): the most oversold stocks
  keep falling intraday. Do NOT use largest-drop ranking again
  without a new frozen family.
- Month cumulative (capped): Jan -₹7,469 → Feb -₹18,693 → Mar
  -₹12,905 → Apr -₹8,005 → May -₹10,900 → Jun -₹23,497 → Jul
  -₹20,926 → Aug -₹19,395 → Sep -₹28,878 → Oct -₹28,612. Never
  positive, never rising month by month.
- Event-phase breakdown (capped, same ±7-trading-day windows):
  no-event 76 trades -₹3,893.00 (47.4% win); post-reaction 26 trades
  -₹14,464.00 (42.3% win); pre-announcement 11 trades -₹10,255.00
  (27.3% win). Events do NOT rescue Volrix-for-stocks — the
  post/pre legs lose MORE than no-event. Worst stocks (capped):
  GLENMARK -₹13,210 (4), BDL -₹9,380 (7), OBEROIRLTY -₹5,100 (5);
  best: HINDALCO +₹5,185 (4), TVSMOTOR +₹3,880 (3). NTPC: 0 triggers
  Jan–Oct 2026.
- This week Oct 26–28 (Oct 29 missing in cache): NHPC 26 Oct
  +₹81.00 (no-event); GODREJCP 27 Oct -₹320.00 (no-event); BDL
  28 Oct -₹820.00 (no-event); week total -₹1,059.00 on 3 trades.
- Verdict: **Volrix-for-stocks intraday (same-day square-off, no
  stop/target) is REJECTED as a standalone stock system.** The
  index Volrix edge (5-session hold, ~30 entries in 7 years) does
  NOT transfer to same-day stock rebounds. Next Volrix question,
  if revisited at all, must be a NEW frozen family (e.g. multi-day
  hold, which is no longer intraday, or a stop/target version) —
  not a tweak to this run's numbers.

### Geopolitics / global sentiment — 26–30 Oct 2026 (sourced, not invented)
- 29 Oct: Fed held rates at 3.75–4.00% (2 members wanted a hike);
  US stocks ended higher (Dow +0.19%, S&P +0.28%, Nasdaq +0.27%
  per DSIJ pre-market 29 Oct); Brent ~$114–115, WTI ~$101–102;
  USD/INR ~95.21–95.25; FII net buyers ₹871.83cr on 28 Oct
  (per ScanX/DSIJ), then net sellers ₹943–944cr on 29 Oct (per
  Economic Times / Reuters 30 Oct). Sentiment tag 29 Oct: MIXED
  (risk-on from Fed hold + earnings rebound, risk-off from oil
  >$110 and FII October outflows ~₹48,760cr).
- 30 Oct (pre-market, Reuters 30 Oct 07:42 IST): GIFT Nifty
  22,981 (+44 vs Nifty close 22,936.75 on 29 Oct) — cautiously
  positive open; Brent rose 2.2% to $117.40 after Houthi attacks
  on Saudi Ras Tanura refinery/airports; Nikkei -~3% ahead of
  BoJ decision, Kospi -~5% on Wall Street AI jitters (Nasdaq
  -1%+ on Alphabet AI cash burn); earnings due 30 Oct from
  Reliance, Sun Pharma, Bharat Electronics. Sentiment tag
  30 Oct: **CAUTIOUSLY POSITIVE / VOLATILE, oil-geopolitics
  risk-off overlay** — do NOT trade 30 Oct stocks on sentiment
  alone; tag only, no sentiment-created entries.
- Geopolitics overlay for Jan–Oct backtests: the calendar's 15
  curated non-results events do NOT include a systematic
  geopolitics series (oil, Fed, Iran/US, trade deal). That is a
  GAP, not a finding: a geopolitics tag series (oil >$100 days,
  Fed/RBI decision days, Iran/US escalation days) is Family 4's
  prerequisite, and must be built from dated public sources
  before any geopolitics filter is scored.
- Stocks with no influencing news found (this week): NHPC,
  GODREJCP (27 Oct), BDL (28 Oct) Volrix trades above are all
  no-event by the calendar — i.e. their moves that week are NOT
  explained by a calendar event. No news was invented for them.

### Ranked highest-tuned table (stocks only, Jan–Oct 2026, per 100 shares provisional)
| Rank | Version | Trades | Full-target | Net ₹ | /day | Verdict |
|---|---|---|---|---|---|---|
| 1 | S9 (S8 + event gate) | 50 | 26.0% | +₹1,640.00 | 0.246 | Best net + best full-target, fails frequency + cumulative — NOT adopted |
| 2 | S8 | 54 | 22.2% | +₹932.50 | 0.27 | Previous best, fails frequency + cumulative — NOT adopted |
| 3 | S7 | 51 | 21.6% | +₹722.50 | 0.25 | Fails frequency + cumulative — NOT adopted |
| 4 | S2 | 61 | 19.7% | -₹785.98 | 0.30 | Bar for full-target rate only |
| 5 | Volrix-for-stocks (Family 2) | 113 | N/A (no target) | -₹28,612.00 | 0.56 | Frequency closest, deeply negative — REJECTED standalone |

### Next families (in order, each frozen before scoring)
- Family 3: Setup2-PE new room definition (from S8 diagnosis):
  replace "room to next PD below" (impossible below PDL) with a
  structural level below PDL — e.g. previous-day low minus OR
  width, or the stock's own 20-day low — frozen as its own spec,
  then scored on the 95 find_signal setup2 days + full window.
- Family 4: Geopolitics/global-sentiment tag series + filter
  test (oil/Fed/Iran/trade-deal days, dated sources only) —
  diagnostic first: do sentiment-risk-off days explain S9's
  losers, or do they just shrink frequency further?
- Family 5: Different candles / indicators — 15-min pullback
  entries and VWAP/ATR-filtered S8 (VWAP confirmation, ATR-based
  room), each as a separate frozen family, never all at once.
- Family 6: V5 / Skill v2 / (lA) v2 for stocks, together and
  individually, on NO-NEWS days only (per the user's rule) —
  after Families 3–4, so their no-news baseline is clean.
- Tuning continues every 30 minutes; next update adds Family 3
  (frozen spec + score) or reports its blocker plainly.


## 2026-10-30 (resume) — Family: setup2-PE new room definition = S10 — REJECTED
S10 = S9 + structural-support room test for setup2_or_breakdown PE only
(nearest prior-20d daily low below entry, extend 60d, open-downside
sentinel; threshold 1.5x unchanged). Frozen before scoring:
new_stock_system_s10_frozen.md. Result Jan-Oct: 53 trades, 0.261/day,
50.9% win, 24.5% FT, +Rs 1,677.50 provisional per 100 shares vs S9
+Rs 1,640.00 — net +Rs 37.50 (noise), frequency still ~0.26/day,
cumulative trough WORSE (Jun -1,765 vs S9 -1,050). Funnel: 92 raw
setup2 PE signals, 45 confirmed, old room test passed 0/45, new test
18/45, only 4 reached the capped set, net -Rs 272.50, 0 FT. Setup2-PE
family CLOSED — room was not the bottleneck; prospective >=500 floor
and confirmation chain are. S9 stays highest-tuned.
Next frozen, NOT scored: S11 = S9 + no-event tier AND rule (room>=2.0x
AND prospective>=1000), new_stock_system_s11_frozen.md. Full report:
stocks_resume_s10.md; Nov watchlist: stock_event_watchlist_nov2026.md.
