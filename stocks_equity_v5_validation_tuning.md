# Stocks EQUITY — V5 validation (Jan–Sep) + target/stop grid tuning

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums anywhere in this report. Paper only, no orders.
Real money: ₹0.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade flat cost, unless a sentence says otherwise. Spec frozen
before scoring: `stocks_equity_v5_deep_frozen.md`. Engine:
`stocks_equity_v5_deep.py`.**

Portfolio rule applied throughout (user, 2026-10-30 19:33 IST):
**no 1-trade/day portfolio cap** — every qualifying stock is traded,
max 1 trade per stock per day. The uncapped portfolio view is the
primary view everywhere below. The user's floor of a minimum of
~2 valuable trades/day is reported as a trades/day distribution.

Windows: Jan–Sep 2026 = 185 trading days; October 2026 = 1–28 Oct,
18 trading days (29 Oct missing from cache, stated, not a zero day).

---

## Verdict first — Jan–Sep KILLS the V5 × T10 October edge

- Reproduction gate passed exactly: the validation engine reproduces
  the October run to the paisa — V5-stock × T10 in October is 378
  trades, net **+₹6,502.57 provisional per 100 shares**, with the
  no-event subset at 270 trades, net **+₹11,666.99 provisional per
  100 shares**, and the event-window subset at net **−₹5,164.42
  provisional per 100 shares**. The October numbers were real; the
  question was whether they generalise. They do not.
- **Jan–Sep 2026, V5-stock × T10, all days: 3,733 trades, 36.4% win
  rate, 27.2% target-hit rate, net −₹178,594.99 provisional per
  100 shares, expectancy −₹47.84 provisional per 100 shares per
  trade, daily-cumulative max drawdown −₹193,842.28 provisional per
  100 shares.**
- **Jan–Sep 2026, V5-stock × T10, NO-EVENT days only: 2,755 trades,
  37.3% win rate, net −₹111,631.66 provisional per 100 shares,
  expectancy −₹40.52 provisional per 100 shares per trade, max
  drawdown −₹127,754.09 provisional per 100 shares.** The no-event
  filter — October's whole edge — does not rescue Jan–Sep.
- Even before costs it is not there: Jan–Sep no-event gross (adding
  back ₹40 × 2,755 trades = ₹110,200 of costs) is **−₹1,431.66
  provisional per 100 shares** — flat-to-negative gross, so the
  October no-event edge is a one-month phenomenon, not a cost
  artefact and not a stable property of the system.
- **Nothing in the 9-combo grid survives Jan–Sep either** (grid
  section below): every combo's Jan–Sep no-event net is between
  **−₹56,932.39 and −₹122,551.57 provisional per 100 shares**.
- **(lA)-stock × T10 also fails Jan–Sep** (section 4): no-event net
  **−₹54,096.24 provisional per 100 shares**. There is no second
  candidate.
- Frequency was never the problem: the primary (uncapped) view
  averages **20.18 trades/day in Jan–Sep, provisional per 100
  shares basis**, with 2+ qualifying trades on all 185 of 185
  trading days — far above the user's minimum-2/day floor. The
  system trades plenty; it loses a little on most of them.

**Conclusion: V5-stock × T10 is NOT validated. October 2026 was one
good month in a falling market (SHORT-heavy), not an edge. No combo
from this grid is proposed for November paper on this evidence.**

---

## 1. Validation — V5-stock × T10, Jan–Sep 2026 (uncapped, primary view)

Totals (every figure provisional per 100 shares):

| Split | Trades | Win % | Target % | Net ₹ | Expectancy ₹ | Max DD ₹ | Avg %/trade |
|---|---|---|---|---|---|---|---|
| All days | 3,733 | 36.4 | 27.2 | −178,594.99 | −47.84 | −193,842.28 | +0.016 |
| No-event | 2,755 | 37.3 | 27.8 | −111,631.66 | −40.52 | −127,754.09 | +0.028 |
| Event-window | 978 | 34.0 | 25.6 | −66,963.33 | −68.47 | −67,610.51 | −0.018 |

The event split still points the user's way — event-window days are
worse (−₹68.47 expectancy provisional per 100 shares) than no-event
days (−₹40.52 provisional per 100 shares) — but both sides lose, so
the event rule alone cannot make this system viable.

Trades/day distribution vs the minimum-2/day floor (counts of
trading days with 0 / 1 / 2+ trades; nets provisional per
100 shares): all-days view — 0 days with 0 trades, 0 days with
exactly 1, **185 days with 2+**, mean 20.18/day. No-event view —
0 days with 0, 1 day with exactly 1, **184 days with 2+**, mean
14.89/day. The floor is met on essentially every day in both views;
the failure is expectancy, not frequency.

Per month (nets provisional per 100 shares):

| Month | All trades | All win % | All net ₹ | No-event trades | No-event net ₹ | Event net ₹ |
|---|---|---|---|---|---|---|
| 2026-01 | 421 | 37.8 | **+4,011.06** | 292 | **+6,958.42** | −2,947.36 |
| 2026-02 | 423 | 34.0 | −52,425.82 | 250 | −31,516.60 | −20,909.22 |
| 2026-03 | 395 | 37.7 | −1,577.55 | 383 | −818.42 | −759.13 |
| 2026-04 | 372 | 39.5 | +2,574.82 | 306 | −1,849.22 | +4,424.04 |
| 2026-05 | 378 | 35.2 | −22,404.36 | 175 | −15,060.70 | −7,343.66 |
| 2026-06 | 425 | 37.2 | −27,876.32 | 392 | −25,272.89 | −2,603.43 |
| 2026-07 | 458 | 34.9 | −35,675.05 | 299 | −14,818.65 | −20,856.40 |
| 2026-08 | 428 | 38.1 | −23,170.77 | 253 | −8,116.65 | −15,054.12 |
| 2026-09 | 433 | 33.9 | −22,051.00 | 405 | −21,136.95 | −914.05 |

January is the only clearly positive month (net **+₹4,011.06
provisional per 100 shares** all-days); February alone loses
**−₹52,425.82 provisional per 100 shares**, and May–Sep bleed every
month. October's profit sits in the same class as January — an
occasional good month inside a losing year.

Diagnostics for T10 in Jan–Sep (labelled diagnostics, not rules;
nets provisional per 100 shares): LONG 1,302 trades, net
−₹58,817.27; SHORT 2,431 trades, net −₹119,777.72 — unlike October,
SHORT does not save Jan–Sep. Entries before 11:00: 3,185 trades,
net −₹151,910.62; from 11:00: 548 trades, net −₹26,684.37. Both
halves of every split lose.

---

## 2. Grid — targets 0.75/1.0/1.25% × stops 0.4/0.5/0.75% (V5-stock)

Scored on October AND Jan–Sep under the frozen rules. Every net in
this table is provisional per 100 shares. "Best" by the frozen
ranking (Jan–Sep no-event net + October no-event net) is marked —
it is the least-bad combo, **not** a validated winner.

| Combo (tgt/stop) | Jan–Sep all net ₹ | Jan–Sep no-event win % | Jan–Sep no-event net ₹ | Jan–Sep no-event max DD ₹ | Oct all net ₹ | Oct no-event net ₹ |
|---|---|---|---|---|---|---|
| 0.75 / 0.40 | −142,021.53 | 37.1 | −90,999.83 | −101,944.25 | −7,739.78 | −724.04 |
| 0.75 / 0.50 | −180,282.77 | 41.7 | −122,551.57 | −133,338.81 | +1,746.20 | +10,332.07 |
| 0.75 / 0.75 | −155,751.36 | 49.8 | −114,037.52 | −134,252.67 | +5,126.77 | +2,869.49 |
| 1.00 / 0.40 | −133,930.58 | 33.2 | −67,868.34 | −80,695.45 | +3,763.16 | +7,913.05 |
| 1.00 / 0.50 (= T10) | −178,594.99 | 37.3 | −111,631.66 | −127,754.09 | +6,502.57 | +11,666.99 |
| 1.00 / 0.75 | −147,731.39 | 45.1 | −103,745.73 | −133,936.75 | +6,213.68 | +3,463.73 |
| **1.25 / 0.40 (least-bad)** | −122,552.02 | 30.9 | **−56,932.39** | −68,932.00 | +9,892.22 | +10,279.71 |
| 1.25 / 0.50 | −165,382.43 | 34.9 | −98,102.42 | −111,654.56 | +9,740.09 | +10,287.67 |
| 1.25 / 0.75 | −136,655.83 | 42.7 | −93,171.49 | −117,172.50 | +15,633.56 | +6,534.50 |

Reading: wider stops raise win rate (up to 49.8% no-event win rate
at 0.75/0.75 in Jan–Sep) but not expectancy — losers simply lose
more per trade. The least-bad combo, target 1.25% / stop 0.4%,
still posts a Jan–Oct no-event net of **−₹46,652.68 provisional
per 100 shares** (3,025 trades) and a Jan–Oct all-days net of
**−₹112,659.80 provisional per 100 shares** (4,111 trades). No
combo is carried forward.

## 3. Per-stock table — least-bad combo (1.25% / 0.4%), Jan–Oct combined

Reported only, per the frozen spec — **no stock is dropped by
hindsight**; any per-stock filter is a November-paper question, not
a claim. Every net is provisional per 100 shares.

| Stock | Trades | Win % | Net ₹ | No-event net ₹ |
|---|---|---|---|---|
| HINDUNILVR | 167 | 39.5 | +18,808.89 | +19,805.95 |
| ASTRAL | 158 | 31.6 | +7,120.22 | +24,012.47 |
| IRCTC | 145 | 40.7 | +7,839.83 | +7,665.47 |
| HINDCOPPER | 144 | 35.4 | +4,954.05 | +9,315.58 |
| GLENMARK | 172 | 29.1 | +2,872.90 | +4,818.51 |
| VEDL | 157 | 36.9 | +2,360.08 | +3,244.50 |
| PFC | 175 | 36.0 | +1,950.42 | −178.92 |
| KALYANKJIL | 168 | 31.5 | +879.31 | +3,094.22 |
| OIL | 163 | 33.1 | −1,849.95 | −2,885.78 |
| NATIONALUM | 153 | 30.1 | −1,870.90 | −2,891.54 |
| RECLTD | 172 | 30.8 | −2,801.83 | −2,453.95 |
| ITC | 164 | 36.6 | −3,694.29 | −111.11 |
| WIPRO | 157 | 28.7 | −4,883.67 | −3,501.51 |
| INDUSTOWER | 171 | 28.1 | −4,938.67 | −4,675.71 |
| NTPC | 172 | 31.4 | −5,037.37 | −2,588.31 |
| HINDZINC | 155 | 27.1 | −7,163.19 | −2,893.81 |
| TATASTEEL | 169 | 26.0 | −7,271.55 | −5,352.39 |
| NHPC | 179 | 20.1 | −7,771.12 | −5,808.83 |
| BDL | 165 | 26.1 | −7,863.80 | −7,328.12 |
| UNITDSPR | 172 | 29.7 | −11,217.50 | −5,578.96 |
| HDFCBANK | 167 | 31.1 | −12,267.67 | −8,880.75 |
| HINDALCO | 157 | 26.1 | −12,737.89 | −11,235.32 |
| GODREJCP | 167 | 28.7 | −16,486.28 | −14,603.68 |
| OBEROIRLTY | 177 | 24.3 | −21,659.14 | −19,845.59 |
| TVSMOTOR | 165 | 25.5 | −29,930.68 | −17,795.10 |

Only 8 of 25 stocks are net-positive over Jan–Oct even under the
least-bad combo, and the two biggest no-event payers (ASTRAL
**+₹24,012.47 provisional per 100 shares** no-event; HINDUNILVR
**+₹19,805.95 provisional per 100 shares** no-event) are exactly
the kind of concentrated, hindsight-visible pattern the frozen
spec forbids turning into a filter claim. November-paper question,
recorded: does a small pre-declared stock subset behave differently
live? Not answered here.

Diagnostics for the least-bad combo, Jan–Oct (labelled diagnostics;
nets provisional per 100 shares): entries before 11:00 — 3,519
trades, net −₹92,583.38; from 11:00 — 592 trades, net −₹20,076.42.
LONG 1,450 trades, net −₹49,871.49; SHORT 2,661 trades, net
−₹62,788.31. No split rescues the combo.

## 4. Second-candidate check — (lA)-stock × T10, Jan–Sep 2026

Every figure provisional per 100 shares: all days — 1,524 trades,
34.5% win rate, net **−₹112,697.39**, expectancy −₹73.95 per trade,
max drawdown −₹125,001.88. No-event — 1,119 trades, 35.9% win
rate, net **−₹54,096.24**, max drawdown −₹64,841.19. Event-window —
405 trades, net **−₹58,601.15**. (lA) was October-positive and is
Jan–Sep-negative, the same pattern as V5. **It does not validate
either; there is no surviving second candidate.**

---

## 5. What survives, and what does not

- **Survives:** the event-window penalty is consistent across both
  windows and both systems — event days are the worst days
  (Jan–Sep V5 event expectancy −₹68.47 vs no-event −₹40.52
  provisional per 100 shares). The user's "check events first"
  rule is directionally right; it is just not sufficient to make
  these entries profitable.
- **Survives:** frequency. The uncapped portfolio produces 2+
  qualifying trades on essentially every trading day (mean
  20.18/day in Jan–Sep, provisional per 100 shares basis) — the
  minimum-2/day floor is a non-issue for signal-based systems.
- **Does not survive:** V5-stock entries with %-target exits at any
  tested target/stop, (lA)-stock × T10, and any claim that
  October's +₹11,666.99 no-event result (provisional per 100
  shares) represents a repeatable edge.
- Stage results only; nothing is adopted, and on this evidence
  nothing from this family should go to November paper as a
  primary. If November paper is run at all for stocks, the open
  questions are the per-stock subset question in section 3 and
  whether a different entry family (not V5/Skill-derived morning
  signals) behaves better — both are new work, not tuning of this
  grid.

## Files

- Frozen spec: `stocks_equity_v5_deep_frozen.md`
- Engine: `stocks_equity_v5_deep.py`
- Grid + all results JSON: `stocks_equity_v5_grid_results.json`
- Trades: `eq_v5_jansep_trades_T10.csv` (3,733 Jan–Sep V5 × T10
  trades), `eq_v5_oct_trades_T10_repro.csv` (October reproduction),
  `eq_v5_bestcombo_janoct_trades.csv` (least-bad combo 1.25%/0.4%,
  Jan–Oct), `eq_la_jansep_trades_T10.csv` ((lA) Jan–Sep × T10)
- Prior October run: `stocks_equity_october_systems.md`,
  `stocks_equity_systems_oct.py`
