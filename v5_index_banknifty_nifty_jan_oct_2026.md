# V5 Index — Bank Nifty and Nifty only, January to October 2026

Paper only. No orders placed, no live trading, no live-trading recommendation.
Cash intraday only, provisional rules, NOT Chandu's live options rules.

## Request

Chandu, 2026-10-29 10:13 IST: run V4 index for Bank Nifty and Nifty,
make it Version 5, taking inputs from Skill index AND V4 index, run ONLY
for Bank Nifty and Nifty (index only, NO stocks).

## V5 engine definition

- Window: **January 2026 to 28 October 2026 only.** October = 1–28 Oct;
  29 Oct 2026 excluded (still in progress that day). Trading days: 203
  (Jan 20, Feb 21, Mar 19, Apr 20, May 19, Jun 21, Jul 23, Aug 21, Sep 21,
  Oct 18).
- Instruments: **NIFTY and BANKNIFTY only. No stocks.**
- Pool: V4 index candidates + Skill index candidates (Skill = OR-only,
  passing V4-style filters: bias-aligned, room ≥ 200×scale, PD bound),
  recomputed from the Upstox 5-min cache to 2026-10-28. Nothing fabricated.
  This is the full candidate pool, not just the already-capped picks —
  a candidate ranked out of its own series' cap can still win in V5 if
  it outranks the other method's candidate that week.
- Dedup, same symbol+date (provisional, NOT Chandu's rule — he only said
  take inputs from both): keep higher conviction (setup4=3 > setup3=2 >
  setup2=1 > skill OR=0), then higher prospective net target, then
  bias-strong, then room ratio.
- Filter (provisional, same as capped-v2): prospective net target
  ≥ ₹500 (net of ₹40 cost).
- Rank (signal-time/prospective only, never realised outcome):
  setup_rank, bias-strong, room_ratio, prospective net target.
- Cap: max 3 index trades/ISO week, max 1 trade/symbol/week. With only
  2 symbols this caps at **2/week in practice**; repeats were NOT allowed
  silently to reach 3/week. Actual V5 frequency is reported below.
- Provisional cash rules: 100 shares equivalent (index points × 100),
  ₹40/trade, signal-candle stop, 2× target, square-off 15:10, Setup 1
  skipped, short paper-only.
- Index nets are **point-scaled cash-equivalents, NOT portfolio rupees**.
- Engine: [v5_index.py](sandbox://workspace/trading/v5_index.py).
  Month JSONs: `data/progressive/v5_index_summary_2026-MM.json`
  (MM = 01–10).
- Results gate: NEUTRAL (0), as in the capped-v2 series — no gate rule
  was adopted from the results patterns in this series.

## Month by month — V5 index only

Trades/week below uses calendar weeks in the month (Jan 5, Feb 5, Mar 5,
Apr 5, May 4, Jun 5, Jul 5, Aug 5, Sep 5, Oct 5), not the engine's
candidate-week denominator.

| Month | V5 trades / win / net | Bank Nifty trades / net | Nifty trades / net | Cumulative V5 net | V4 index input (trades / net) | Skill index input (trades / net) |
|---|---|---|---|---|---|---|
| Jan 2026, 20 days | 7 / 28.6% / +₹6,625 | 3 / +₹6,900 | 4 / −₹275 | +₹6,625 | 6 / +₹9,650 | 7 / +₹12,890 |
| Feb 2026, 21 days | 6 / 16.7% / −₹23,290 | 3 / −₹24,615 | 3 / +₹1,325 | −₹16,665 | 6 / −₹23,290 | 4 / −₹5,755 |
| Mar 2026, 19 days | 9 / 77.8% / +₹99,805 | 5 / +₹80,260 | 4 / +₹19,545 | +₹83,140 | 6 / +₹77,625 | 7 / +₹77,640 |
| Apr 2026, 20 days | 9 / 44.4% / +₹8,690 | 5 / −₹2,090 | 4 / +₹10,780 | +₹91,830 | 6 / +₹9,955 | 8 / +₹7,805 |
| May 2026, 19 days | 7 / 42.9% / −₹7,415 | 4 / −₹3,710 | 3 / −₹3,705 | +₹84,415 | 6 / +₹5,460 | 7 / −₹27,015 |
| Jun 2026, 21 days | 6 / 0.0% / −₹42,805 | 4 / −₹34,260 | 2 / −₹8,545 | +₹41,610 | 5 / −₹39,000 | 3 / −₹24,190 |
| Jul 2026, 23 days | 9 / 33.3% / −₹7,140 | 5 / −₹14,055 | 4 / +₹6,915 | +₹34,470 | 9 / −₹7,140 | 7 / +₹8,010 |
| Aug 2026, 21 days | 7 / 28.6% / −₹26,705 | 4 / −₹33,655 | 3 / +₹6,950 | +₹7,765 | 7 / −₹26,705 | 7 / −₹26,705 |
| Sep 2026, 21 days | 5 / 60.0% / +₹4,790 | 3 / −₹1,990 | 2 / +₹6,780 | +₹12,555 | 4 / +₹10,390 | 5 / +₹950 |
| Oct 2026, 18 days (1–28 Oct) | 7 / 71.4% / +₹51,825 | 4 / +₹43,630 | 3 / +₹8,195 | +₹64,380 | 7 / +₹51,825 | 3 / +₹16,610 |

Input legs verified from `data/progressive/capped_v2_summary_2026-MM.json`
(index legs) and [jan_oct_2026_v4_and_skill.md](sandbox://workspace/trading/jan_oct_2026_v4_and_skill.md):
V4 index Jan–Oct = 62 trades, 43.5% win, +₹68,770;
Skill index Jan–Oct = 58 trades, 43.1% win, +₹40,240.

## Cumulative V5 index, to 28 October 2026

| Series | Trades | Targets | Win | Net | Expectancy/trade |
|---|---|---|---|---|---|
| **V5 index (Bank Nifty + Nifty)** | **72** | **30** | **41.7%** | **+₹64,380** | **+₹894** |
| Bank Nifty only (inside V5) | 40 | — | — | +₹16,415 | +₹410 |
| Nifty only (inside V5) | 32 | — | — | +₹47,965 | +₹1,499 |
| V4 index (input, for comparison) | 62 | 27 | 43.5% | +₹68,770 | +₹1,109 |
| Skill index (input, for comparison) | 58 | 25 | 43.1% | +₹40,240 | +₹694 |

Frequency: V5 = 72 trades over 49 calendar weeks = **1.47/week**,
1.0–1.8/week by month, never 3/week (2/week practical cap, as above).
V4 index = 62 trades, Skill index = 58 trades over the same window.

Best V5 trades: Bank Nifty 2026-03-13 setup2 PE +₹27,190;
Bank Nifty 2026-03-23 OR breakdown +₹25,440;
Bank Nifty 2026-10-21 setup2 PE +₹20,200;
Bank Nifty 2026-10-01 setup4 CE +₹16,640.
Worst V5 trades: Bank Nifty 2026-06-29 setup2 PE −₹15,645;
Bank Nifty 2026-08-10 setup2 PE −₹14,370;
Bank Nifty 2026-04-01 setup3 rejection −₹23,515 (partially offset
in-month by Bank Nifty +₹21,820 on 2026-04-24).

## Does V5 progress vs its inputs? NO — on net + win rate + frequency together

- **Net: NO vs the best input.** V5 +₹64,380 is BELOW V4 index
  +₹68,770, though above Skill index +₹40,240. Pooling did not beat
  the best single input.
- **Win rate: NO vs either input.** V5 41.7% is below V4 index 43.5%
  AND below Skill index 43.1%.
- **Frequency: NOT an improvement.** V5 trades MORE (72) than either
  input (62 / 58) for a lower win rate and a lower net than V4 index.
  More trades, worse result — the opposite of progression.
- **March dominance, again.** Without March 2026 (+₹99,805), V5 is
  −₹35,425. Without March, V4 index is −₹8,855 and Skill index is
  −₹37,400. V5 ex-March is worse than V4 index ex-March, so the
  pooled total is carried by one month, not by a stable edge.
- **Bank Nifty vs Nifty inside V5.** Nifty carries V5 (+₹47,965 on
  32 trades); Bank Nifty is barely positive (+₹16,415 on 40 trades)
  despite its March +₹80,260, because Bank Nifty also carries the
  largest stops (Jun −₹34,260, Aug −₹33,655 on its leg).
- **Honest identity check.** V5 as defined here is, in outcome, the
  index leg of the capped-v2 Unified series (same dedup + index cap):
  Unified index Jan–Oct was also 72 trades, 41.7%, +₹64,380. Pooling
  V4 + Skill index under one cap does not create a new index edge
  beyond what Unified already showed; it re-labels it V5.

## Adoption verdict — DO NOT ADOPT V5 on this report alone

V5 is built and measured, but **not adopted**. Adoption requires
progression on net + win rate + frequency together vs both inputs, on
unseen months — V5 fails net vs V4 index and win rate vs both inputs
on the same Jan–Oct 2026 window it was built from, and its total is
March-dependent. Previous best kept for index: V4 index
(+₹68,770 / 62 trades / 43.5%) as a separate series, paper only.
A candidate V5 variant must beat V4 index on net AND win rate, at no
more trades, on a future unseen month (e.g. November 2026 paper)
before adoption — not on this in-sample window. No live order, no lot
increase, on the basis of V5.
