# Tuning iteration V4 -> V5, Skill v1 -> v2, + Results Intelligence layer

Paper only. No orders. Provisional cash rules throughout (NOT Chandu's
rules): 100 shares/trade, Rs 40/trade assumed cost, stop = signal-candle
low/high, target = 2x stop distance unless a candidate changes it,
square-off 15:10, one trade/instrument/day, V4 thresholds scaled by
prev-close/55,000, Setup 1 skipped, shorts paper-only, capital not shared
so no risk %. Win rate = targets / all trades.
Pre-stated design: tune = Jan-Jun 2026, validation = Jul-Sep 2026 (unseen),
October 2026 = context only, never used to pick a candidate.
Adoption rule: adopt ONLY if, on Jul-Sep validation WITH the portfolio
cap (max 3/ISO week, earliest first), the candidate beats the capped
baseline on net AND win rate AND trades/week no higher. Otherwise FAILED,
previous best kept, failure logged, fix tried again.
Note on implementation: the tuning script re-implements V4 via
daytrader_cash_tuning.find_signal, which differs slightly from
daytrader_cash_backtest.run_day used for the original Run 2. Uncapped
trade counts differ by 3 (Jan-Jun 529 vs 526) and 1 (Jul-Sep 315 vs 314);
capped validation nets therefore differ too (tune baseline +1,467 vs
original Run 2 capped +657). Adoption checks below are against the
tuning-script baseline; the original-baseline comparison is also shown
where it changes the conclusion. It does not: the four Jul-Sep
"passes" below also beat the original capped baseline (+657, 31.0%).

## Stocks — all periods, portfolio (25 stocks)
### Original Run 1 (skill v1: OR+flag+oversold) and Run 2 (V4)
| Period | R1 trades / net / win / tpw | R2 trades / net / win / tpw | Capped (V4, earliest) trades / net / win / tpw |
|---|---|---|---|
| Jan-Jun, 120 days | 2,990 / -197,016 / 30.0% / 124.58 | 526 / -29,075 / 31.4% / 21.92 | 81 / -10,261 / 24.7% / 3.38 |
| Jul-Sep, 65 days | 1,624 / -114,437 / 27.3% / 124.92 | 314 / -8,365 / 30.3% / 24.15 | 42 / +657 / 31.0% / 3.23 |
| Oct, 18 days | 450 / -33,527 / 32.0% / 125.00 | 94 / -7,984 / 34.0% / 26.11 | 15 / +160 / 46.7% / 4.17 |

### V5 / Skill-v2 grid — Jul-Sep validation, capped (the adoption test)
Baseline capped (tuning script): 42 trades, +1,467, 33.3%, 3.23/week.
| Candidate | Jan-Jun capped net / win | Jul-Sep capped net / win / tpw | Oct capped net / win | Adoption |
|---|---|---|---|---|
| V5a ratio 1.5 | -5,324 / 34.6% | -664 / 38.1% / 3.23 | +1,428 / 66.7% | FAILED (validation net down) |
| V5b ratio 3 | -7,536 / 16.0% | +1,491 / 23.8% / 3.23 | +3,114 / 46.7% | FAILED (validation win down) |
| V5c stop 0.5 | -3,850 / 29.6% | +259 / 35.7% / 3.23 | -395 / 40.0% | FAILED (validation net down) |
| V5d stop 1.5 | -10,920 / 21.0% | +7,226 / 28.6% / 3.23 | +4,458 / 53.3% | FAILED (validation win down) |
| V5e room 0 | -8,341 / 30.9% | +4,370 / 35.7% / 3.23 | +1,187 / 46.7% | PASSES Jul-Sep check only — NOT ADOPTED (see below) |
| V5f room 0.0072 | +897 / 30.9% | +5,035 / 38.1% / 3.23 | -48 / 40.0% | PASSES Jul-Sep check only — NOT ADOPTED (see below) |
| V5g bias off | -8,854 / 25.9% | +5,082 / 38.1% / 3.23 | +541 / 53.3% | PASSES Jul-Sep check only — NOT ADOPTED (see below) |
| V5h ratio 1, stop 0.5 | -4,038 / 43.2% | -2,030 / 45.2% / 3.23 | -1,002 / 40.0% | FAILED (validation net down) |
| V5i ratio 3, stop 0.5 | -4,454 / 22.2% | -5,398 / 28.6% / 3.23 | +212 / 40.0% | FAILED (validation net and win down) |
| Skill-v2 OR-only | -11,751 / 22.2% | +2,869 / 35.7% / 3.23 | -4,588 / 33.3% | PASSES Jul-Sep check only — NOT ADOPTED (see below) |

### Why the four Jul-Sep "passes" are NOT adopted
1. Frequency did not improve — it was held equal by the cap (3.23/week
   in every capped run). The adoption rule required progress on all
   three; frequency was neutral, not better.
2. October context contradicts them: V5f goes negative in October
   (-48), Skill-v2 goes to -4,588 in October, V5e/V5g October capped
   nets (+1,187 / +541) are below the tuning-script October baseline
   (+1,625). A version that passes one 42-trade validation window and
   fails the next 15-trade window is not proven.
3. Uncapped, every candidate is still deeply negative in every period
   (e.g. V5f uncapped Jul-Sep -7,594, V5g -5,622, Skill-v2 -72,553).
   The cap is doing the work, not the entry/exit: it drops 85-90% of
   trades. Earliest-first cap selection is arbitrary with respect to
   quality.
4. V6 fix tried: setup-priority cap (Setup 3 first, then Setup 4, then
   Setup 2, signal-time info only, no outcome look-ahead). Jul-Sep:
   +2,071 / 35.7% (vs earliest +1,467 / 33.3%); Jan-Jun: -7,429 (vs
   -7,164); October: -640 (vs +1,625). FAILED — cap ranking is noise,
   not edge. Previous best (capped V4 baseline) is kept.
Conclusion: NO new version adopted. Keep V4 (capped, paper only) as the
previous best. The entry problem is not fixed by exit ratio, stop scale,
room, bias, or cap ranking.

## Results Intelligence layer — context gate, not a standalone entry
Existing engine used: ~/workspace/trading/results_intelligence.py (v1,
already in workspace). It computes, per verified event: pre-week
T-5..T-1 return, after-market gap (reaction open / last pre close),
post-week T+1..T+5 return, volume ratios, and a 3-of-4 pattern rule
per stock. It creates NO entry by itself; it only gates signals.
Calendar: ~/workspace/trading/results_dates.csv — VERIFIED dates only:
ITC Q1 FY27 2026-07-31 (post-market), HDFCBANK Q4 FY26 2026-04-18
(Saturday, gap day 2026-04-20), WIPRO Q4 FY26 2026-04-16 (post-market),
TATASTEEL Q4 FY26 2026-05-15. ITC Q2 FY27 2026-11-02 is scheduled
(future, forward loop only, excluded from backtest classification).
All other 25-stock x 4-quarter cells are MISSING, not estimated.
Limitation, plain: stock 5-min files saved OHLC only, no volume, so
pre_vol_ratio is unavailable and the accumulation flag is False for
every event in this run — accumulation patterns cannot be claimed from
this run. Nifty benchmark was not loaded (excess returns blank).
Events (results_events.csv):
| Stock / quarter | Pre-week % | Gap % | Post-week % | Post direction |
|---|---|---|---|---|
| ITC Q1 FY27 (T 31 Jul) | -1.06 | +1.23 | +1.81 | reversal |
| HDFCBANK Q4 FY26 (T 18 Apr) | +0.25 | -0.36 | -1.86 | reversal |
| WIPRO Q4 FY26 (T 16 Apr) | +3.22 | -2.45 | -3.46 | reversal |
| TATASTEEL Q4 FY26 (T 15 May) | +1.12 | -2.76 | -3.53 | reversal |
Pattern verdict for every stock: INSUFFICIENT_EVENTS (1 verified event
each, rule needs 4). No per-stock pattern is claimed.
Gate test (pre-registered: block V4 signals on trading days T-1..T+1):
only 1 V4 trade in the whole Jan-Oct run falls in any verified window —
ITC 2026-08-03 setup3 PE, -95. Blocking it moves Jul-Sep V4 net from
-9,003 to -8,908 (tuning script) — negligible, and not a portfolio
verdict. Gate NOT adopted as proven; it stays as a context layer.
Continuous loop (not a 15:30-only job): IDENTIFY — add each new results
date to results_dates.csv with source (exchange filing/company notice),
never from price alone; LEARN — recompute pre/gap/post after each
quarter into results_events.csv; FIX — if blocked shadow net turns
positive on a new quarter, suspend the gate and log it, do not keep it
silently. Next loop step: fill the calendar for all 25 stocks x 4
quarters from filings, and re-save 5-min files WITH volume, before any
gate adoption is reconsidered.

## Nifty legs (same provisional cash rules, 100-share equivalent — NOT
comparable in rupees to stocks, and NOT mixed with stock totals)
| Period | Skill R1 trades / net / win | V4 R2 trades / net / win | Capped trades / net / win |
|---|---|---|---|
| Jan-Jun, 120 days | 120 / -50,830 / 30.8% | 23 / -130 / 34.8% | 23 / -130 / 34.8% |
| Jul-Sep, 65 days | 65 / +1,720 / 36.9% | 19 / +30,535 / 57.9% | 18 / +30,760 / 61.1% |
| Oct, 18 days | 18 / +8,565 / 33.3% | 4 / +2,725 / 50.0% | 4 / +2,725 / 50.0% |
Nifty V4 Jul-Sep looks strong on 19 trades, but Nifty Jan-Jun is flat
(-130) and the per-trade rupees are index-scale (100 shares x ~200
points). Do NOT carry Nifty Jul-Sep into a stocks verdict, and do NOT
call it X: skill on Nifty alone is 5.0 trades/week, above the 2-3
portfolio cap, and Nifty + stocks together would be far above it.

## Unified validation / November forward paper — status
NOT RUN YET. November 2026 has not happened; no November forward-paper
result is claimed. When November starts, run the kept version (capped
V4, paper only, max 3/ISO week) forward, paper only, and log each week
against X. No live order, no lot increase, until a version is positive
on fresh data.
Files: stocks_october/tune_stocks.py, stocks_october/tuning_results.json,
stocks_october/tune_v4_trades_{janjun,julsep,october}.csv,
results_intelligence.py, results_dates.csv, results_events.csv,
results_patterns.csv, results_intelligence_data/*.csv,
nifty_{janjun,julsep,october}/*_trades.csv and summaries,
daytrader_stocks_october_run.md (October leg).
