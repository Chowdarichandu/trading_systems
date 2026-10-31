# Stocks EQUITY — October 2026 — index systems leveraged on stocks, small targets

**EQUITY CASH intraday only. NOT options — there are no premiums
anywhere in this report. LONG = bullish signal bought in equity;
SHORT = bearish signal sold in equity (paper short, intraday
square-off). Paper only, no orders. Real money: ₹0.**
**Every rupee figure is provisional per 100 shares, ₹40/trade flat
cost, unless a sentence says otherwise. Spec frozen before scoring:
`stocks_equity_smalltarget_frozen.md`. Engine:
`stocks_equity_systems_oct.py`.**

Window: October 2026 = 1–28 Oct in cache, 18 trading days.
29 Oct is missing from cache — stated, not treated as a zero day.
Systems: V5-stock, Day Trader Skill, (lA)-stock, Volrix-stock —
the existing index systems applied to the 25 stocks, per the user's
instruction, NOT a new standalone system. Exits (frozen): **T05**
target +0.5% / stop −0.5%; **T10** target +1.0% / stop −0.5%;
**TSYS** target +1.0% / stop = signal-candle extreme capped at
−1.0%. Stop wins a same-candle tie; otherwise 15:10 square-off.
Volrix has no signal candle, so it has no TSYS variant.

---

## Per-system best first

**V5-stock × T10 is the one genuinely positive combination in
October.** Uncapped (max 1 trade/stock/day): 378 trades, 41.8% net-
positive win rate, 34.7% full-target rate, **net +₹6,502.57
provisional per 100 shares**, expectancy +₹17.20 provisional per
100 shares per trade, average +0.102% captured per trade — and it
stays positive after the ₹40/trade cost (gross before costs
+₹21,622.57 provisional per 100 shares; costs took ₹15,120.00 of
it). Its 1-trade/day portfolio-capped view is much weaker: 18
trades, **net +₹682.60 provisional per 100 shares** — the cap
ranking does not select V5's good trades well.

**(lA)-stock × T10 is second.** Uncapped: 183 trades, 42.6% win,
35.0% full targets, **net +₹1,009.24 provisional per 100 shares**,
average +0.109% captured per trade. But its capped view collapses
(16 trades, net −₹6,180.62 provisional per 100 shares) — Nifty-
confirmation helps the broad pool, not the 1/day ranking.

**Skill × T10 loses uncapped but its capped view is positive.**
Uncapped: 450 trades (Skill fires almost every stock-day), 36.7%
win, **net −₹21,952.22 provisional per 100 shares**. Capped 1/day:
18 trades, net +₹997.40 provisional per 100 shares — an 18-trade
selection effect, not a pool edge; reported, not celebrated.

**Volrix-stock loses in October under small targets.** Its best
variant is T05: 26 trades, 38.5% win, **net −₹4,023.21 provisional
per 100 shares**, average −0.077% captured per trade. The rebound
did not arrive within the day in October, and a 0.5% stop cuts
rebounds before they start; T10 is worse (net −₹7,636.08
provisional per 100 shares).

## Full grid (every figure provisional per 100 shares)

| System | Exit | Uncapped trades | Win % | Target % | Uncapped net ₹ | Avg %/trade | Capped 1/day net ₹ |
|---|---|---|---|---|---|---|---|
| V5 | T05 | 378 | 50.8 | 53.2 | −13,108.03 | +0.039 | −2,739.08 |
| V5 | **T10** | 378 | 41.8 | 34.7 | **+6,502.57** | +0.102 | +682.60 |
| V5 | TSYS | 378 | 29.6 | 26.2 | −15,719.96 | +0.033 | −3,414.15 |
| Skill | T05 | 450 | 48.4 | 50.4 | −24,861.50 | +0.011 | −5,226.15 |
| Skill | T10 | 450 | 36.7 | 29.8 | −21,952.22 | +0.026 | +997.40 |
| Skill | TSYS | 450 | 26.0 | 22.9 | −37,301.83 | −0.012 | −2,853.50 |
| (lA) | T05 | 183 | 52.5 | 55.2 | −8,236.39 | +0.052 | −8,059.72 |
| (lA) | **T10** | 183 | 42.6 | 35.0 | **+1,009.24** | +0.109 | −6,180.62 |
| (lA) | TSYS | 183 | 32.2 | 27.3 | −974.63 | +0.063 | −4,679.00 |
| Volrix | T05 | 26 | 38.5 | 42.3 | −4,023.21 | −0.077 | −2,199.48 |
| Volrix | T10 | 26 | 19.2 | 19.2 | −7,636.08 | −0.212 | −3,326.38 |

**Why T05 fails even where T10 wins:** at a 0.5% target with a
0.5% stop the trade is a coin flip (win rates 48–53%), and ₹40 per
100 shares is a large bite of a 0.5% move on lower-priced stocks —
the cost drag turns a gross +₹2,011.97 provisional per 100 shares
(V5 T05) into net −₹13,108.03 provisional per 100 shares. The 1%
target is what gives the winners room to pay for the losers and
the costs. **TSYS fails everywhere**: signal-candle stops on
stocks are usually wider than 0.5%, so losers lose more than the
T05/T10 losers while winners are capped at the same 1%.

## The October pattern — SHORT side paid, LONG side lost (diagnostic)

This split appears in every system and is reported as October's
character, NOT as a new rule (a short-only filter chosen after
seeing October would be hindsight):

- V5 × T10: SHORT 230 trades **+₹18,210.60 provisional per 100
  shares**; LONG 148 trades **−₹11,708.03 provisional per 100
  shares**.
- Skill × T10: SHORT 208 trades +₹13,187.71 provisional per 100
  shares; LONG 242 trades −₹35,139.93 provisional per 100 shares.
- (lA) × T10: SHORT 78 trades +₹11,262.30 provisional per 100
  shares; LONG 105 trades −₹10,253.06 provisional per 100 shares.
- Unified × T10: SHORT 262 trades +₹12,832.95 provisional per 100
  shares; LONG 251 trades −₹39,778.65 provisional per 100 shares.

## Events first — the user's rule holds in the data

Every trade is tagged `no_event` / `event_window` from the event
calendar (±7 trading days). For the best combination, V5 × T10
uncapped: **no-event days: 270 trades, net +₹11,666.99 provisional
per 100 shares; event-window days: 108 trades, net −₹5,164.42
provisional per 100 shares.** The entire V5 edge in October sits
on days with no influencing event for that stock, exactly as the
user's rule predicts; event windows lose.

## Unified (all four systems together)

Dedup: same stock+day+direction across systems, earliest entry
kept. **The union is WORSE than V5 alone** — Skill fires earliest
on most stock-days, so the union mostly inherits Skill's entries:
unified × T10 uncapped: 513 trades, 35.1% win, **net −₹26,945.70
provisional per 100 shares**; capped 1/day: 18 trades, net
−₹1,665.64 provisional per 100 shares. Unified × T05 uncapped net
is −₹31,230.23 provisional per 100 shares and unified × TSYS
uncapped net is −₹32,483.28 provisional per 100 shares. Combining
everything dilutes the one working pool (V5) with the weakest
(Skill raw). **No-event subset of the unified best (T10): 367
trades uncapped, net −₹21,533.22 provisional per 100 shares;
capped net −₹5,282.14 provisional per 100 shares** — removing
event days does not rescue the union, because its problem is
Skill's raw entries, not events.

### Unified best variant (T10), capped 1/day — trade-by-trade
(every figure provisional per 100 shares; full 513-trade uncapped
list is in `eq_unified_oct_trades_T10.csv`)

| Date | Stock | Dir | Setup | Exit | Net ₹ | Event |
|---|---|---|---|---|---|---|
| 2026-10-01 | GLENMARK | LONG | or_breakout | stop | −1,215.65 | no_event |
| 2026-10-05 | KALYANKJIL | SHORT | setup3 | stop | −314.32 | no_event |
| 2026-10-06 | OIL | LONG | setup4_reclaim | stop | −264.18 | no_event |
| 2026-10-07 | KALYANKJIL | LONG | or_breakout | stop | −322.70 | no_event |
| 2026-10-08 | TVSMOTOR | LONG | setup4_reclaim | stop | −2,015.45 | no_event |
| 2026-10-09 | GLENMARK | LONG | or_breakout | stop | −1,155.75 | no_event |
| 2026-10-12 | ASTRAL | LONG | or_breakout | stop | −757.70 | no_event |
| 2026-10-13 | BDL | LONG | setup4_reclaim | target | +1,054.90 | event_window |
| 2026-10-14 | NHPC | LONG | or_breakout | stop | −76.79 | no_event |
| 2026-10-15 | BDL | LONG | setup4_reclaim | stop | −605.95 | event_window |
| 2026-10-16 | NHPC | SHORT | or_breakdown | stop | −76.00 | no_event |
| 2026-10-19 | KALYANKJIL | LONG | or_breakout | stop | −320.83 | no_event |
| 2026-10-21 | HINDUNILVR | SHORT | setup3 | target | +1,826.50 | event_window |
| 2026-10-22 | IRCTC | LONG | setup4_reclaim | stop | −266.90 | no_event |
| 2026-10-23 | HDFCBANK | SHORT | or_breakdown | stop | −385.77 | no_event |
| 2026-10-26 | GLENMARK | LONG | setup4_reclaim | target | +2,129.90 | no_event |
| 2026-10-27 | OBEROIRLTY | LONG | or_breakout | target | +1,556.80 | event_window |
| 2026-10-28 | GODREJCP | LONG | setup4_reclaim | stop | −455.75 | no_event |

Capped unified × T10 total: **net −₹1,665.64 provisional per 100
shares** (18 trades, 22.2% win).

## Per-stock breakdown — best variant of each system (uncapped)

**V5 × T10** (net provisional per 100 shares): best — HINDUNILVR
13 trades +₹7,404.45; HINDALCO 15 +₹4,541.63; ASTRAL 12
+₹3,594.45; GLENMARK 15 +₹2,627.10; GODREJCP 15 +₹1,753.81.
Worst — TVSMOTOR 16 −₹5,084.40; UNITDSPR 14 −₹2,500.10;
INDUSTOWER 16 −₹1,951.12; KALYANKJIL 14 −₹1,932.96; HDFCBANK 16
−₹1,788.72. 10 of 25 stocks positive, 15 negative — the pool edge
is real but uneven. Setup mix: skill_or_breakdown 161 trades and
setup3_bounce_rejection 65 carry it; exits: 131 targets, 208
stops, 39 square-offs.

**Skill × T10**: best — HINDALCO 18 trades +₹3,575.57
provisional per 100 shares; TVSMOTOR 18 +₹2,800.45; NATIONALUM
18 +₹1,285.42. Worst — OBEROIRLTY 18 −₹7,962.00 provisional per
100 shares; GLENMARK 18 −₹7,713.30; KALYANKJIL 18 −₹3,001.94.

**(lA) × T10**: best — HINDALCO 7 trades +₹3,859.83 provisional
per 100 shares; GLENMARK 7 +₹1,893.50; ASTRAL 3 +₹1,886.40.
Worst — TVSMOTOR 8 −₹4,241.70 provisional per 100 shares;
UNITDSPR 9 −₹2,530.70; IRCTC 8 −₹1,461.97.

**Volrix × T05**: 26 trades over 25 stocks (max 1–2 per stock):
best singles — HINDUNILVR +₹887.00, GODREJCP +₹376.55, HDFCBANK
+₹314.77, all provisional per 100 shares; worst — TVSMOTOR
−₹2,053.00, ASTRAL −₹730.50, UNITDSPR −₹687.50, all provisional
per 100 shares.

## Reference line and verdict

- Reference only — S12 October (the dropped standalone 3R
  design): 8 trades, **+₹1,885 provisional per 100 shares**.
  V5 × T10 uncapped (+₹6,502.57 provisional per 100 shares, 378
  trades) beats that total but at ~21 trades/day across stocks —
  a completely different frequency profile from S12's 1/day
  design; V5 × T10 capped 1/day (+₹682.60 provisional per 100
  shares) is BELOW the S12 reference. Neither comparison is an
  adoption case; they are different instruments of frequency.
- **What the user asked is what the data shows:** small targets
  work on stocks only at the 1% target (T10), not at 0.5% (cost
  drag kills T05), and only in the V5 pool (and weakly in (lA)).
  Skill raw and Volrix lose in October under every exit.
- **Weak/rejected, kept separate:** Skill (all exits, uncapped),
  Volrix (both exits), TSYS on every system, T05 on every system,
  the four-system union (all exits), and every 1/day capped view
  except V5 × T10 and Skill × T10, which are positive but small
  (18 trades each).
- Nothing here is adopted. October is in-sample, SHORT-side
  dominated, and the uncapped V5 result needs November 2026 paper
  validation — ideally run as V5 × T10 with the no-event tag
  live, since the no-event subset (+₹11,666.99 provisional per
  100 shares on 270 trades) is where the October edge sat.

## Files

- Spec (frozen first): `stocks_equity_smalltarget_frozen.md`
- Engine: `stocks_equity_systems_oct.py`; raw results:
  `stocks_equity_oct_results.json`
- Trades (uncapped, per system × variant): `eq_v5_oct_trades_T05/
  T10/TSYS.csv`, `eq_skill_oct_trades_*.csv`,
  `eq_la_oct_trades_*.csv`, `eq_volrix_oct_trades_T05/T10.csv`,
  `eq_unified_oct_trades_*.csv`,
  `eq_unified_oct_trades_T10_capped.csv`
