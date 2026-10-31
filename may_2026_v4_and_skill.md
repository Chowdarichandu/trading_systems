# May 2026 — V4 along with Day Trader Skill (standalone, May 2026 only)

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday only. Provisional rules, NOT Chandu's live options rules:
100 shares/trade, ₹40/trade assumed cost, stop = signal-candle low/high,
target = 2× stop distance, square-off 15:10, Setup 1 skipped, short signals
paper-only, one trade/instrument/day for raw runs.

## Scope and data

- Window: **May 2026 only, not May 2025.** May 2025 v2 is already done
  separately and is not included here.
- Trading days in window: **19 days, 4 ISO weeks.**
- Instruments: **27 — Nifty, Bank Nifty, and 25 stocks** (GODREJCP, GLENMARK,
  ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL,
  HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC,
  HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR).
- Data: already in the Upstox 5-min cache for May 2026 (fetched in the v1
  series), so **no fresh fetch was needed and nothing was fabricated**.
  Engines: `progressive_capped.py` (v1 cap) and `progressive_capped_v2.py`
  (v2 cap). Month JSONs: `data/progressive/capped_summary_2026-05.json`
  (v1) and `data/progressive/capped_v2_summary_2026-05.json` (v2, written
  by this run).
- **Index vs stocks split in every table.** Index nets are 100 shares ×
  index points — point-scaled cash-equivalents, NOT portfolio rupees and
  NOT comparable rupee-for-rupee with stock nets. Totals are shown for
  completeness only; judge stocks progression on the stocks-only column.
- "Win rate" here = targets ÷ trades (square-offs are not counted as wins).

## Raw May 2026 — uncapped, one trade/instrument/day

| Series | Trades | Targets / Stops / Sq-off | Win | Total net | Index net | Stocks-only net |
|---|---|---|---|---|---|---|
| V4 raw | 91 | 23 / 63 / 5 | 25.3% | −₹28,985 | −₹23,650 (10 trades, 30.0%) | **−₹5,335** (81 trades, 24.7%) |
| Skill raw, OR signals | 398 signals | — (net not computed for unfiltered signals) | — | — | — | — |
| Skill filtered raw* | 97 | 29 / 63 / 5 | 29.9% | −₹27,331 | −₹31,270 (11 trades, 27.3%) | **+₹3,939** (86 trades, 30.2%) |

\* Skill "raw" net is the V4-style filtered pool, as in the progressive runs:
OR-only signals passing bias alignment, room ≥ 200×scale, and the PD bound
(CE close < PDH, PE close < PDL). The 398 OR signals before those filters
are counted, but their unfiltered net is NOT claimed — the engine filters
before computing an outcome, so inventing a 398-trade net would be fabrication.

Raw reading: both raw totals are index-driven losses. V4 raw loses on both
legs. Skill filtered raw is the only raw series positive on stocks
(+₹3,939), but its index leg (−₹31,270) drags its total to −₹27,331.

### Raw best / worst

V4 raw best: BANKNIFTY 2026-05-29 setup3 PE target **+₹15,660**;
BANKNIFTY 2026-05-05 setup2 PE target +₹10,540; NIFTY 2026-05-05 setup2 PE
target +₹5,040; TVSMOTOR 2026-05-20 setup4 CE target +₹3,860;
GLENMARK 2026-05-04 setup3 PE target +₹1,440.
V4 raw worst: BANKNIFTY 2026-05-11 setup2 PE stop **−₹17,360**;
BANKNIFTY 2026-05-14 setup2 PE stop −₹17,035; NIFTY 2026-05-13 setup2 PE
stop −₹5,075; NIFTY 2026-05-11 setup2 PE stop −₹5,035;
BANKNIFTY 2026-05-27 setup2 PE stop −₹4,395.

Skill filtered raw best: BANKNIFTY 2026-05-12 OR PE target **+₹20,460**;
BANKNIFTY 2026-05-05 OR PE target +₹10,540; NIFTY 2026-05-05 OR PE
target +₹5,040; TVSMOTOR 2026-05-14 OR PE target +₹3,980;
TVSMOTOR 2026-05-20 OR CE target +₹3,860.
Skill filtered raw worst: BANKNIFTY 2026-05-11 OR PE stop **−₹17,360**;
BANKNIFTY 2026-05-13 OR PE stop −₹16,580; BANKNIFTY 2026-05-18 OR PE
stop −₹12,875; NIFTY 2026-05-13 OR PE stop −₹5,075;
NIFTY 2026-05-11 OR PE stop −₹5,035.

Negative-after-cost targets in raw runs (target hit, still loses money
because the target distance was smaller than the ₹40 cost): V4 raw —
NHPC 2026-05-13 −₹34, NHPC 2026-05-22 −₹2. Skill filtered raw — none.
These are exactly the tiny-target failure the ₹500 v2 filter was meant
to remove.

## Capped-v2 May 2026 — 3 index/week + 3 stock/week, convicted + high-return only

Separate caps, NOT combined: max 3 index trades/week AND max 3 stock
trades/week, max 1/symbol/week, per series. Ranking (signal-time only):
conviction (setup4 > setup3 > setup2 > skill OR), then bias-strong, then
room ratio, then prospective net target. Filter: prospective net target
≥ ₹500 (net of ₹40 cost). Note: with only NIFTY and BANKNIFTY, the index
leg can reach at most 2/week under 1/symbol/week — observed 1.5/week
(V4), 1.75/week (Skill); attainable max is 5/week total, not 6.

| Series | Trades | Targets / Stops / Sq-off | Win | Total net | Index net | Stocks-only net | Avg prospective target net |
|---|---|---|---|---|---|---|---|
| V4 capped-v2 | 18 (idx 6, stk 12) | 5 / 12 / 1 | 27.8% | **+₹7,440** | +₹5,460 (6 trades, 50.0%) | **+₹1,980** (12 trades, 16.7%) | ₹5,371 |
| Skill capped-v2 | 17 (idx 7, stk 10) | 5 / 9 / 3 | 29.4% | **−₹24,685** | −₹27,015 (7 trades, 28.6%) | **+₹2,330** (10 trades, 30.0%) | ₹7,161 |
| Unified capped-v2 | 19 (idx 7, stk 12) | 5 / 13 / 1 | 26.3% | **−₹5,435** | −₹7,415 (7 trades, 42.9%) | **+₹1,980** (12 trades, 16.7%) | ₹6,437 |

No capped-v2 trade nets negative on a target — the ₹500 filter removed
those cases.

### Capped-v2 best / worst

V4 capped-v2 best: BANKNIFTY 2026-05-29 setup3 PE target **+₹15,660**;
BANKNIFTY 2026-05-05 setup2 PE target +₹10,540; NIFTY 2026-05-05 setup2 PE
target +₹5,040; TVSMOTOR 2026-05-20 setup4 CE target +₹3,860.
V4 capped-v2 worst: BANKNIFTY 2026-05-14 setup2 PE stop **−₹17,035**;
NIFTY 2026-05-13 setup2 PE stop −₹5,075; NIFTY 2026-05-18 setup2 PE
stop −₹3,670; ASTRAL 2026-05-08 setup4 CE stop −₹860.

Skill capped-v2 best: BANKNIFTY 2026-05-05 OR PE target **+₹10,540**;
NIFTY 2026-05-05 OR PE target +₹5,040; TVSMOTOR 2026-05-19 OR PE
target +₹2,280; BDL 2026-05-11 OR PE square-off +₹1,460.
Skill capped-v2 worst: BANKNIFTY 2026-05-13 OR PE stop **−₹16,580**;
BANKNIFTY 2026-05-18 OR PE stop −₹12,875; NIFTY 2026-05-13 OR PE
stop −₹5,075; BANKNIFTY 2026-05-27 OR PE stop −₹4,395.

### Fragility — capped-v2

- V4 capped-v2 total (+₹7,440) is index-carried in the other direction
  from October: its index leg (+₹5,460) plus a small stocks leg
  (+₹1,980) — but its stocks win rate is only 16.7% (2 targets in
  12 trades), and its max drawdown is ₹28,130, so the positive month
  is not a clean stocks progression.
- Skill capped-v2 total (−₹24,685) is entirely an index story: stocks
  are +₹2,330, index is −₹27,015 on 7 trades. Three Bank Nifty/Nifty
  stops (−₹16,580, −₹12,875, −₹5,075) wipe out the stocks gain.
- Sensitivity at ₹1,000 (not adopted): V4 12 trades / +₹9,510
  (index +₹5,460, stocks +₹4,050); Skill 15 / −₹22,285
  (index −₹27,015, stocks +₹4,730); Unified 17 / −₹2,795
  (index −₹7,415, stocks +₹4,620). Raising the threshold improves
  stocks for all series in May alone, but does not fix Skill's
  index leg, and one month is not an adoption basis.

## Comparison to v1 May 2026 capped (combined 3/week cap)

V1 May 2026 capped, from `capped_summary_2026-05.json` (verified split
[0, net], i.e. all stocks, no index trade made the combined cap):

| Series | V1 trades / win / total | V1 index | V1 stocks-only | V2 trades / win / total | V2 index | V2 stocks-only |
|---|---|---|---|---|---|---|
| V4 | 12 / 8.3% / −₹2,198 | ₹0 | −₹2,198 | 18 / 27.8% / +₹7,440 | +₹5,460 | +₹1,980 |
| Skill | 12 / 33.3% / +₹3,160 | ₹0 | +₹3,160 | 17 / 29.4% / −₹24,685 | −₹27,015 | +₹2,330 |
| Unified | 12 / 8.3% / −₹2,198 | ₹0 | −₹2,198 | 19 / 26.3% / −₹5,435 | −₹7,415 | +₹1,980 |

Reading: on stocks-only, capped-v2 improves V4 in May (−₹2,198 →
+₹1,980) but slightly worsens Skill (+₹3,160 → +₹2,330), and Unified
stocks also improve (−₹2,198 → +₹1,980). On total, V4 improves only
because the separate cap let index trades in (+₹5,460), while Skill
total collapses for the same reason (−₹27,015 index leg). May alone
does not show a total progression for Skill or Unified.

## Verdict — May 2026 only

- Frequency: capped-v2 passes on count (4.25–4.75/week, 17–19 trades),
  not 500+. Raw (91 / 97 trades) does not.
- Stocks-only: capped-v2 is positive for all three series in May
  (+₹1,980 / +₹2,330 / +₹1,980) — the first capped month in this
  standalone pair where that holds — but V4 stocks win rate is only
  16.7%, and the amounts are small against index swings of
  ±₹27,000 in the same month.
- Total: no progression — V4 total is positive only with its index
  leg, Skill and Unified totals are negative because of theirs.
- **No new version adopted on May 2026 alone** — one month, index-driven
  in every version, and Skill's capped-v2 total is worse than its
  v1 total despite better stocks. Paper only, no live order.
