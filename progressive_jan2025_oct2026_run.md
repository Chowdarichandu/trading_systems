# Progressive backtest — Jan 2025 to 28 Oct 2026 — PROGRESS FILE
Paper only, no orders, no live trading. Proprietary to Chandu, workspace only.

## Rules (labelled, provisional)
- Methods: Day Trader skill entries (Run 1: OR + flag + oversold, provisional definitions from daytrader_skill_run.py) AND V4 entries (Run 2: Setups 2/3/4, Setup 1 skipped, no bands), separately.
- Cash intraday for stocks AND for Nifty/Bank Nifty cash-equivalent. PROVISIONAL, NOT Chandu's rules: 100 shares/trade, ₹40/trade assumed cost, stop = signal-candle low/high, target = 2x stop distance, square-off 15:10, one trade/instrument/day, thresholds scaled by prev-close, short signals paper-only.
- Cash only in this run. NO options track in this file — options rupees are never mixed with cash provisional rupees.
- WARNING on index cash rupees: Nifty/Bank Nifty are index points (~24,000 / ~50,000), so 100-share cash-equivalent nets are point-scaled and dominate any summed total. Index and stocks-only totals are therefore reported SEPARATELY below. Do not read the combined total as a portfolio rupee result.
- X = 2-3 trades/week PORTFOLIO TOTAL + good net + good win rate, all three together. Raw unfiltered runs (every instrument, every day) are reported first; a portfolio cap (best setups first, max 2-3/week) is a V5/unified step, not applied in the raw totals below.
- Bank Nifty Jul-Oct 2026 is NOT carried forward as a forward total in this series. This is a NEW progressive series recomputed from Jan 2025 onward; overlap with earlier Jan-Oct 2026 Bank Nifty work is noted, not mixed into cumulative totals unless this run itself recomputed it.
- Data: Upstox historical 5-min candles only, via ~/workspace/custom-connectors/custom.upstox/bin/upstox.py (verified working 2026-10-29). No fabricated candles. Instrument keys in ~/workspace/trading/data/progressive/keys.json. Engines: ~/workspace/trading/progressive_fetch.py, ~/workspace/trading/progressive_engine.py.
- Versioning: V4 base, Day Trader skill v1 base. A V5 / skill v2 version is adopted ONLY if it progresses on validation (unseen period) on net, win rate, AND frequency together. A decreasing result is NOT adopted.

## Progress log — append after EACH month

### 2025-01 — DONE, all 27 instruments, 22 counted trading days (23 calendar trading days, first day used as prior day only)
- Data: Upstox 5-min, 1,725 bars per instrument (ITC 1,721).
- V4 (cash): 106 trades, 36 targets, 61 stops, 9 square-offs, win 34.0%, net ₹-67,120 (combined, see split below), expectancy ₹-633/trade.
  - Indices only (Nifty + Bank Nifty cash-equivalent): 13 trades, 1 target, net ₹-64,235.
  - Stocks only (25 stocks): 93 trades, 35 targets, net ₹-2,885.
  - Best V4 stocks Jan: GLENMARK 4 trades, 75.0%, +₹1,670; TVSMOTOR +₹2,525; HINDALCO +₹545. Worst: ASTRAL -₹2,010; HINDUNILVR -₹1,925; KALYANKJIL -₹1,845.
- Day Trader skill (cash): 592 trades, 205 targets, win 34.6%, net ₹+24,299 (combined).
  - Indices only: 44 trades, 13 targets, net ₹+8,900.
  - Stocks only: 548 trades, 192 targets, net ₹+15,399.
  - Best skill stocks Jan: TVSMOTOR +₹8,295; OBEROIRLTY +₹4,685; UNITDSPR +₹4,415. Worst: HINDUNILVR -₹5,815; GODREJCP -₹2,280.
- Portfolio trades/week (raw, sum over 27, NO cap): V4 24.09/week, Skill 134.55/week.
- X verdict so far: FAILS frequency for both raw runs (far above 2-3/week portfolio total). Win rate ~34% for both. Net: V4 negative, Skill positive in Jan only — one month is not proof. No V5/skill v2 adoption yet; progression gate not met on frequency.
- Per-instrument table below is the source for the combined totals; full run file in progressive_jan2025_oct2026_run.md.

Per-instrument Jan 2025 (V4 trades / win% / net ₹ | Skill trades / win% / net ₹):
NIFTY 6 / 0.0% / -24,045 | 22 / 31.8% / +8,555
BANKNIFTY 7 / 14.3% / -40,190 | 22 / 27.3% / +345
GODREJCP 6 / 50.0% / -75 | 22 / 31.8% / -2,280
GLENMARK 4 / 75.0% / +1,670 | 22 / 31.8% / +35
ITC 2 / 50.0% / -75 | 21 / 33.3% / -675
RECLTD 3 / 33.3% / +245 | 22 / 45.5% / +2,525
TVSMOTOR 5 / 40.0% / +2,525 | 22 / 40.9% / +8,295
UNITDSPR 1 / 100.0% / +400 | 22 / 45.5% / +4,415
OBEROIRLTY 2 / 0.0% / -1,435 | 21 / 42.9% / +4,685
NTPC 4 / 25.0% / -445 | 22 / 36.4% / -460
INDUSTOWER 4 / 25.0% / +535 | 22 / 36.4% / +255
KALYANKJIL 3 / 0.0% / -1,845 | 22 / 45.5% / +1,165
HDFCBANK 6 / 50.0% / -110 | 22 / 27.3% / -1,650
NHPC 6 / 83.3% / -51 | 22 / 36.4% / -852
PFC 2 / 50.0% / +200 | 22 / 45.5% / +1,895
IRCTC 4 / 50.0% / +455 | 22 / 31.8% / +695
WIPRO 4 / 0.0% / -530 | 22 / 31.8% / -825
NATIONALUM 4 / 25.0% / -233 | 22 / 27.3% / -1,220
VEDL 2 / 0.0% / -530 | 22 / 40.9% / +270
HINDCOPPER 6 / 50.0% / +126 | 22 / 40.9% / -674
HINDZINC 2 / 0.0% / -100 | 22 / 36.4% / -635
HINDALCO 5 / 60.0% / +545 | 22 / 22.7% / -945
TATASTEEL 4 / 25.0% / -87 | 22 / 27.3% / -830
ASTRAL 4 / 0.0% / -2,010 | 22 / 36.4% / +3,325
BDL 4 / 25.0% / -915 | 22 / 22.7% / +1,765
OIL 4 / 50.0% / +780 | 22 / 40.9% / +2,935
HINDUNILVR 2 / 0.0% / -1,925 | 22 / 18.2% / -5,815

### 2025-02 — DONE, all 27 instruments, 20 counted trading days
- V4 (cash): 107 trades, 35 targets, win 32.7%, net ₹+73,393 combined; indices +₹75,920, stocks -₹2,527.
- Day Trader skill (cash): 533 trades, 182 targets, win 34.1%, net ₹+42,097 combined; indices +₹44,685, stocks -₹2,588.
- Portfolio trades/week (raw, NO cap): V4 26.75/week, Skill 133.25/week.
- Cumulative Jan-Feb 2025: V4 213 trades, net ₹+6,273 (indices +₹11,685, stocks -₹5,412); Skill 1,125 trades, net ₹+66,396 (indices +₹53,585, stocks +₹12,811).
- X verdict so far: STILL FAILS frequency for both raw runs. Win rate ~33-34% in both months. No V5/skill v2 adoption yet.
- Feb detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 10 / 50.0% / +40,055 | 20 / 40.0% / +29,080; BANKNIFTY 9 / 33.3% / +35,865 | 20 / 30.0% / +15,605; GODREJCP 5 / 0.0% / -1,380 | 20 / 40.0% / +2,705; GLENMARK 5 / 40.0% / +100 | 20 / 25.0% / -1,930; ITC 2 / 0.0% / -180 | 20 / 25.0% / -1,465; RECLTD 3 / 33.3% / -235 | 20 / 30.0% / -930; TVSMOTOR 2 / 50.0% / +1,585 | 20 / 35.0% / +4,495; UNITDSPR 3 / 33.3% / -250 | 20 / 50.0% / +2,050; OBEROIRLTY 3 / 0.0% / -585 | 19 / 21.1% / -4,890; NTPC 1 / 0.0% / -75 | 20 / 30.0% / -745; INDUSTOWER 7 / 28.6% / -285 | 20 / 35.0% / -10; KALYANKJIL 7 / 42.9% / +460 | 19 / 31.6% / -1,275; HDFCBANK 5 / 40.0% / -50 | 20 / 20.0% / -1,720; NHPC 2 / 100.0% / +64 | 20 / 55.0% / -317; PFC 5 / 20.0% / -340 | 20 / 25.0% / -1,545; IRCTC 3 / 0.0% / -615 | 20 / 40.0% / +415; WIPRO 3 / 33.3% / -195 | 20 / 45.0% / +320; NATIONALUM 3 / 66.7% / +92 | 19 / 31.6% / -971; VEDL 1 / 0.0% / -105 | 20 / 40.0% / -680; HINDCOPPER 3 / 100.0% / +962 | 19 / 21.1% / -794; HINDZINC 2 / 0.0% / -290 | 20 / 50.0% / +1,465; HINDALCO 5 / 20.0% / -140 | 20 / 35.0% / -595; TATASTEEL 2 / 50.0% / -50 | 20 / 30.0% / -806; ASTRAL 2 / 50.0% / +395 | 20 / 40.0% / -20; BDL 5 / 40.0% / -5 | 18 / 33.3% / +1,520; OIL 4 / 0.0% / -505 | 19 / 31.6% / +560; HINDUNILVR 5 / 20.0% / -900 | 20 / 30.0% / +2,575.

### NEXT: 2025-03 — not yet run
