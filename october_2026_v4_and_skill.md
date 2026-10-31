# October 2026 — V4 along with Day Trader Skill (standalone, 1–28 Oct 2026)

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday only. Provisional rules, NOT Chandu's live options rules:
100 shares/trade, ₹40/trade assumed cost, stop = signal-candle low/high,
target = 2× stop distance, square-off 15:10, Setup 1 skipped, short signals
paper-only, one trade/instrument/day for raw runs.

## Scope and data

- Window: **1–28 October 2026 only. 29 Oct 2026 is NOT included** — it was
  still in progress on the day of this run, so it is not claimed as a full day.
- Trading days in window: **18 days, 5 ISO weeks**.
- Instruments: **27 — Nifty, Bank Nifty, and 25 stocks** (GODREJCP, GLENMARK,
  ITC, RECLTD, TVSMOTOR, UNITDSPR, OBEROIRLTY, NTPC, INDUSTOWER, KALYANKJIL,
  HDFCBANK, NHPC, PFC, IRCTC, WIPRO, NATIONALUM, VEDL, HINDCOPPER, HINDZINC,
  HINDALCO, TATASTEEL, ASTRAL, BDL, OIL, HINDUNILVR).
- Data: already in the Upstox 5-min cache to 2026-10-28, so **no fresh fetch
  was needed and nothing was fabricated**. Engines:
  `progressive_capped.py` (v1 cap) and `progressive_capped_v2.py` (v2 cap).
  Month JSONs: `data/progressive/capped_summary_2026-10.json` (v1) and
  `data/progressive/capped_v2_summary_2026-10.json` (v2, written by this run).
- **Index vs stocks split in every table.** Index nets are 100 shares ×
  index points — point-scaled cash-equivalents, NOT portfolio rupees and
  NOT comparable rupee-for-rupee with stock nets. Totals are shown for
  completeness only; judge stocks progression on the stocks-only column.
- "Win rate" here = targets ÷ trades (square-offs are not counted as wins).

## Raw October — uncapped, one trade/instrument/day

| Series | Trades | Targets / Stops / Sq-off | Win | Total net | Index net | Stocks-only net |
|---|---|---|---|---|---|---|
| V4 raw | 103 | 38 / 64 / 1 | 36.9% | +₹62,431 | +₹70,415 (9 trades, 66.7%) | **−₹7,984** (94 trades, 34.0%) |
| Skill raw, OR signals | 393 signals | — (net not computed for unfiltered signals) | — | — | — | — |
| Skill filtered raw* | 106 | 39 / 60 / 7 | 36.8% | +₹16,366 | +₹16,610 (3 trades, 66.7%) | **−₹244** (103 trades, 35.9%) |

\* Skill "raw" net is the V4-style filtered pool, as in the progressive runs:
OR-only signals passing bias alignment, room ≥ 200×scale, and the PD bound
(CE close < PDH, PE close < PDL). The 393 OR signals before those filters
are counted, but their unfiltered net is NOT claimed — the engine filters
before computing an outcome, so inventing a 393-trade net would be fabrication.

Raw reading: V4 raw total is entirely index-driven (+₹70,415 index vs
−₹7,984 stocks). Skill filtered raw is almost flat on stocks (−₹244) —
better on stocks than either capped version below, which is a warning that
the cap selection, not the raw signals, made October stocks worse.

### Raw best / worst

V4 raw best: BANKNIFTY 2026-10-23 setup2 PE target **+₹24,060**;
BANKNIFTY 2026-10-21 setup2 PE target +₹20,200; BANKNIFTY 2026-10-01
setup4 CE target +₹16,640; NIFTY 2026-10-23 setup2 PE target +₹11,390;
BANKNIFTY 2026-10-26 setup3 PE target +₹10,520.
V4 raw worst: NIFTY 2026-10-26 setup4 CE stop **−₹8,635**; NIFTY 2026-10-28
setup2 PE stop −₹5,470; BANKNIFTY 2026-10-13 setup3 PE stop −₹3,730;
TVSMOTOR 2026-10-08 setup4 CE stop −₹2,360; GLENMARK 2026-10-09 setup3 PE
stop −₹1,040.

Skill filtered raw best: BANKNIFTY 2026-10-01 OR CE target **+₹16,640**;
NIFTY 2026-10-08 OR PE target +₹5,440; TVSMOTOR 2026-10-15 OR CE target
+₹5,380; OBEROIRLTY 2026-10-21 OR PE target +₹2,340; TVSMOTOR 2026-10-21
OR PE target +₹2,260.
Skill filtered raw worst: NIFTY 2026-10-28 OR PE stop **−₹5,470**;
TVSMOTOR 2026-10-08 OR CE stop −₹2,360; TVSMOTOR 2026-10-01 OR PE stop
−₹1,730; TVSMOTOR 2026-10-07 OR PE square-off −₹1,520; OBEROIRLTY
2026-10-26 OR CE stop −₹1,450.

Negative-after-cost targets in raw runs (target hit, still loses money
because the target distance was smaller than the ₹40 cost): V4 raw — NHPC
2026-10-01 −₹10, NHPC 2026-10-06 −₹8, NHPC 2026-10-21 −₹8, TATASTEEL
2026-10-19 −₹12. Skill filtered raw — NHPC 2026-10-01 −₹10. These are
exactly the tiny-target failure the ₹500 v2 filter was meant to remove.

## Capped-v2 October — 3 index/week + 3 stock/week, convicted + high-return only

Separate caps, NOT combined: max 3 index trades/week AND max 3 stock
trades/week, max 1/symbol/week, per series. Ranking (signal-time only):
conviction (setup4 > setup3 > setup2 > skill OR), then bias-strong, then
room ratio, then prospective net target. Filter: prospective net target
≥ ₹500 (net of ₹40 cost). Note: with only NIFTY and BANKNIFTY, the index
leg can reach at most 2/week under 1/symbol/week — the intended 3/week
is not attainable without a second trade in the same index in a week.
Observed index leg: V4 1.4/week, Skill 0.6/week.

| Series | Trades | Targets / Stops / Sq-off | Win | Total net | Index net | Stocks-only net | Avg prospective target net |
|---|---|---|---|---|---|---|---|
| V4 capped-v2 | 22 (idx 7, stk 15) | 9 / 12 / 1 | 40.9% | +₹46,570 | +₹51,825 (7 trades, 71.4%) | **−₹5,255** (15 trades, 26.7%) | ₹4,872 |
| Skill capped-v2 | 18 (idx 3, stk 15) | 6 / 10 / 2 | 33.3% | +₹14,240 | +₹16,610 (3 trades, 66.7%) | **−₹2,370** (15 trades, 26.7%) | ₹3,692 |
| Unified capped-v2 | 22 (idx 7, stk 15) | 9 / 12 / 1 | 40.9% | +₹46,570 | +₹51,825 | **−₹5,255** | ₹4,872 |

Candidates passing the ₹500 filter in October: V4 37 of 103, Skill 45 of 106.
Sensitivity at ₹1,000 (not adopted): V4 19 trades / +₹48,870
(idx +₹51,825, stk −₹2,955); Skill 15 / +₹19,710 (idx +₹16,610, stk +₹3,100)
— the ₹1,000 filter flips Skill stocks positive in October alone, on 15
trades, which is one month, not a validated progression.

### Capped-v2 best / worst

V4 capped-v2 best: BANKNIFTY 2026-10-21 setup2 PE target **+₹20,200**;
BANKNIFTY 2026-10-01 setup4 CE target +₹16,640; NIFTY 2026-10-23 setup2 PE
target +₹11,390; BANKNIFTY 2026-10-26 setup3 PE target +₹10,520; NIFTY
2026-10-08 setup2 PE target +₹5,440.
V4 capped-v2 worst: NIFTY 2026-10-26 setup4 CE stop **−₹8,635**;
BANKNIFTY 2026-10-13 setup3 PE stop −₹3,730; TVSMOTOR 2026-10-08 setup4 CE
stop −₹2,360; GLENMARK 2026-10-09 setup3 PE stop −₹1,040; IRCTC
2026-10-01 setup4 CE stop −₹935.
Note: the raw best, BANKNIFTY 2026-10-23 +₹24,060, does NOT appear in
capped-v2 — BANKNIFTY in week W43 was already used by the 2026-10-21
trade, so the 1/symbol/week cap blocked it. Cap behaviour, not missing data.

Skill capped-v2 best: BANKNIFTY 2026-10-01 OR CE target **+₹16,640**;
NIFTY 2026-10-08 OR PE target +₹5,440; OBEROIRLTY 2026-10-21 OR PE target
+₹2,340; TVSMOTOR 2026-10-21 OR PE target +₹2,260; BDL 2026-10-19 OR PE
target +₹1,320.
Skill capped-v2 worst: NIFTY 2026-10-28 OR PE stop **−₹5,470**;
TVSMOTOR 2026-10-01 OR PE stop −₹1,730; TVSMOTOR 2026-10-07 OR PE
square-off −₹1,520; OBEROIRLTY 2026-10-26 OR CE stop −₹1,450;
OBEROIRLTY 2026-10-15 OR PE stop −₹950.

No capped-v2 trade nets negative on a target — the ₹500 filter removed
those cases in October, as designed.

### Single-index fragility (capped-v2)

- V4 capped-v2 total +₹46,570 is entirely index: +₹51,825 index against
  −₹5,255 stocks. Five index targets (₹20,200 + ₹16,640 + ₹11,390 +
  ₹10,520 + ₹5,440) carry the month; two index stops total −₹12,365.
- Skill capped-v2 total +₹14,240 is likewise one Bank Nifty target
  (+₹16,640 on 1 Oct) against −₹2,370 stocks.
- Without the index leg, October is a stocks failure month for every
  capped series, exactly as in v1.

## Verdict: does October alone show progression vs v1 October?

V1 October (combined 3/week cap, for comparison — from
`capped_summary_2026-10.json`): V4 15 trades / 26.7% / +₹11,242 total
(idx +₹16,640, stk **−₹5,398**); Skill 15 / 40.0% / +₹14,389 total
(idx +₹16,640, stk **−₹2,251**).

- **Total: NO, not a real progression.** V2 V4 total (+₹46,570) is much
  higher than v1 (+₹11,242), but only because the separate index cap let
  in 7 index trades instead of v1's index leg of a single +₹16,640 trade.
  V2 Skill total (+₹14,240) is essentially unchanged from v1 (+₹14,389).
- **Stocks-only: NO.** V2 stocks nets (−₹5,255 V4, −₹2,370 Skill) are
  essentially the same losses as v1 (−₹5,398, −₹2,251). The convicted +
  high-return filter raised prospective target size (avg ₹4,872 / ₹3,692)
  and removed negative-after-cost targets, but it did not turn October
  stocks positive — and capped stocks (−₹5,255 / −₹2,370) are worse than
  skill filtered raw stocks (−₹244), so cap selection hurt stocks in
  October rather than helping them.
- **Frequency:** capped-v2 is 4.4/week (V4) and 3.6/week (Skill), within
  the intended 6/week separate cap (attainable max 5/week — see note
  above). Raw is 103 / 106 trades in 18 days and is not a quality
  frequency at all.
- **No V5 / new version adopted on October alone.** October is one
  partial month (18 days, to 28 Oct), index-driven in every version, and
  stocks-negative in every capped version. The ₹1,000 sensitivity that
  flips Skill stocks positive in October is one month on 15 trades and
  is NOT an adoption basis.

## Files

- This report: `~/workspace/trading/october_2026_v4_and_skill.md`
- V2 month JSON: `~/workspace/trading/data/progressive/capped_v2_summary_2026-10.json`
- V1 month JSON (comparison): `~/workspace/trading/data/progressive/capped_summary_2026-10.json`
- Engines: `~/workspace/trading/progressive_capped_v2.py`,
  `~/workspace/trading/progressive_capped.py`
