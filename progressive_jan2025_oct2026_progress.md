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

### 2025-03 — DONE, all 27 instruments, 19 counted trading days
- Data: Upstox 5-min via connector, verified working 2026-10-29; cache cumulative to 4,650 bars per instrument (ITC 4,646), 62 daily rows Jan-Mar.
- V4 (cash): 102 trades, 31 targets, 67 stops, 4 square-offs, win 30.4%, net ₹-16,306 combined; indices -₹14,260 (Nifty +₹230, Bank Nifty -₹14,490), stocks -₹2,046.
- Day Trader skill (cash): 512 trades, 166 targets, 324 stops, 22 square-offs, win 32.4%, net ₹+31,149 combined; indices +₹50,225 (Nifty +₹41,685, Bank Nifty +₹8,540), stocks -₹19,076.
- Portfolio trades/week (raw, NO cap): V4 26.84/week, Skill 134.74/week.
- Cumulative Jan-Mar 2025: V4 315 trades, net ₹-10,033 (indices -₹2,575, stocks -₹7,458); Skill 1,637 trades, net ₹+97,545 (indices +₹103,810, stocks -₹6,265).
- X verdict so far: STILL FAILS frequency for both raw runs. Win rate ~30-32% in Mar. No V5/skill v2 adoption yet.
- Mar detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 2 / 50.0% / +230 | 19 / 42.1% / +41,685; BANKNIFTY 3 / 0.0% / -14,490 | 19 / 31.6% / +8,540; GODREJCP 2 / 0.0% / -410 | 19 / 26.3% / +490; GLENMARK 6 / 16.7% / -700 | 19 / 31.6% / -3,180; ITC 2 / 0.0% / -35 | 19 / 21.1% / -1,780; RECLTD 3 / 33.3% / +445 | 19 / 26.3% / -425; TVSMOTOR 6 / 33.3% / +1,430 | 19 / 31.6% / -1,975; UNITDSPR 2 / 0.0% / -820 | 19 / 31.6% / -1,245; OBEROIRLTY 5 / 20.0% / -340 | 19 / 36.8% / +1,380; NTPC 3 / 66.7% / +80 | 19 / 42.1% / -840; INDUSTOWER 5 / 40.0% / +225 | 19 / 42.1% / -205; KALYANKJIL 4 / 0.0% / -820 | 19 / 21.1% / -2,725; HDFCBANK 3 / 33.3% / -50 | 19 / 31.6% / -350; NHPC 4 / 0.0% / -249 | 19 / 21.1% / -967; PFC 4 / 50.0% / +210 | 19 / 52.6% / +2,935; IRCTC 5 / 20.0% / -425 | 19 / 26.3% / -1,460; WIPRO 1 / 0.0% / -115 | 19 / 26.3% / -1,370; NATIONALUM 6 / 16.7% / -343 | 19 / 36.8% / -590; VEDL 5 / 20.0% / -630 | 19 / 31.6% / -1,005; HINDCOPPER 4 / 50.0% / +86 | 19 / 31.6% / -1,386; HINDZINC 6 / 66.7% / +515 | 19 / 31.6% / -1,240; HINDALCO 4 / 50.0% / +375 | 19 / 26.3% / -550; TATASTEEL 3 / 100.0% / +130 | 19 / 42.1% / -148; ASTRAL 3 / 66.7% / +1,005 | 19 / 26.3% / -45; BDL 5 / 20.0% / -1,710 | 18 / 27.8% / -585; OIL 3 / 0.0% / -410 | 19 / 52.6% / +1,330; HINDUNILVR 3 / 33.3% / +510 | 19 / 26.3% / -3,140.

### 2025-04 — DONE, all 27 instruments, 19 counted trading days
- Data: Upstox 5-min via connector; cache cumulative to ~6,075 bars per instrument (NIFTY 6,079, BANKNIFTY 6,076, ITC 6,071), 81 daily rows Jan-Apr.
- V4 (cash): 77 trades, 19 targets, 52 stops, 6 square-offs, win 24.7%, net ₹-14,893 combined; indices -₹11,865 (Nifty +₹20,410, Bank Nifty -₹32,275), stocks -₹3,028.
- Day Trader skill (cash): 510 trades, 159 targets, 323 stops, 28 square-offs, win 31.2%, net ₹+23,901 combined; indices +₹10,755 (Nifty -₹24,160, Bank Nifty +₹34,915), stocks +₹13,146.
- Portfolio trades/week (raw, NO cap): V4 20.26/week, Skill 134.21/week.
- Cumulative Jan-Apr 2025: V4 392 trades, net ₹-24,926 (indices -₹14,440, stocks -₹10,486); Skill 2,147 trades, net ₹+121,446 (indices +₹114,565, stocks +₹6,881).
- X verdict so far: STILL FAILS frequency for both raw runs. Win rate Apr: V4 24.7%, Skill 31.2%. No V5/skill v2 adoption yet.
- Apr detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 2 / 100.0% / +20,410 | 19 / 21.1% / -24,160; BANKNIFTY 3 / 0.0% / -32,275 | 19 / 31.6% / +34,915; GODREJCP 2 / 0.0% / -861 | 18 / 27.8% / -415; GLENMARK 2 / 50.0% / +70 | 19 / 42.1% / +6,085; ITC 4 / 50.0% / -70 | 19 / 31.6% / -1,270; RECLTD 1 / 0.0% / -220 | 19 / 42.1% / +780; TVSMOTOR 3 / 66.7% / +1,550 | 19 / 31.6% / +5,491; UNITDSPR 3 / 33.3% / +1,840 | 19 / 26.3% / -910; OBEROIRLTY 2 / 50.0% / +230 | 19 / 36.8% / +6,520; NTPC 4 / 25.0% / -295 | 19 / 10.5% / -1,905; INDUSTOWER 1 / 0.0% / -270 | 19 / 21.1% / -1,650; KALYANKJIL 4 / 25.0% / -740 | 19 / 31.6% / -487; HDFCBANK 4 / 25.0% / -400 | 19 / 31.6% / -560; NHPC 4 / 0.0% / -182 | 19 / 36.8% / -315; PFC 3 / 33.3% / -420 | 19 / 31.6% / -50; IRCTC 4 / 0.0% / -670 | 19 / 26.3% / -1,400; WIPRO 2 / 0.0% / -185 | 19 / 10.5% / -1,610; NATIONALUM 3 / 0.0% / -295 | 19 / 26.3% / -935; VEDL 2 / 0.0% / -640 | 19 / 21.1% / -1,105; HINDCOPPER 6 / 16.7% / -506 | 18 / 38.9% / -642; HINDZINC 2 / 50.0% / -145 | 19 / 36.8% / +345; HINDALCO 5 / 20.0% / -310 | 18 / 44.4% / +2,589; TATASTEEL 3 / 0.0% / -206 | 19 / 57.9% / -90; ASTRAL 3 / 33.3% / -1,120 | 19 / 47.4% / +7,030; BDL 2 / 50.0% / +968 | 19 / 26.3% / -3,410; OIL 2 / 50.0% / -5 | 19 / 21.1% / -1,175; HINDUNILVR 1 / 0.0% / -146 | 19 / 31.6% / +2,235.

### 2025-05 — DONE, all 27 instruments, 21 counted trading days
- Data: Upstox 5-min via connector, verified working 2026-10-29; cache cumulative to ~7,660 bars per instrument (NIFTY 7,660, BANKNIFTY 7,656, ITC 7,646), 102 daily rows Jan-May.
- V4 (cash): 119 trades, 35 targets, 78 stops, 6 square-offs, win 29.4%, net ₹+2,246 combined; indices +₹3,960 (Nifty -₹13,035, Bank Nifty +₹16,995), stocks -₹1,714.
- Day Trader skill (cash): 566 trades, 154 targets, 391 stops, 21 square-offs, win 27.2%, net ₹-195,058 combined; indices -₹149,340 (Nifty -₹18,065, Bank Nifty -₹131,275 — index cash-equivalent point scaling dominates, see warning at top), stocks -₹45,718.
- Portfolio trades/week (raw, NO cap): V4 28.33/week, Skill 134.76/week.
- Cumulative Jan-May 2025: V4 511 trades, net ₹-22,680 (indices -₹10,480, stocks -₹12,200); Skill 2,713 trades, net ₹-73,612 (indices -₹34,775, stocks -₹38,837).
- X verdict so far: STILL FAILS frequency for both raw runs. Win rate May: V4 29.4%, Skill 27.2%. Skill cumulative flipped negative in May, driven by index cash-equivalent losses; stocks-only Skill also negative in May. No V5/skill v2 adoption yet.
- May detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 4 / 0.0% / -13035 | 21 / 19.0% / -18065; BANKNIFTY 7 / 42.9% / +16995 | 21 / 14.3% / -131275; GODREJCP 5 / 20.0% / -2138 | 21 / 9.5% / -7579; GLENMARK 6 / 33.3% / -2250 | 21 / 14.3% / -9730; ITC 2 / 0.0% / -215 | 21 / 38.1% / -620; RECLTD 6 / 33.3% / -405 | 21 / 23.8% / -1580; TVSMOTOR 4 / 50.0% / +1840 | 21 / 33.3% / -6130; UNITDSPR 3 / 0.0% / -2400 | 21 / 19.0% / -4320; OBEROIRLTY 5 / 40.0% / +410 | 21 / 23.8% / -5850; NTPC 3 / 0.0% / -245 | 21 / 38.1% / -255; INDUSTOWER 3 / 100.0% / +450 | 21 / 38.1% / -1600; KALYANKJIL 4 / 25.0% / -389 | 21 / 23.8% / -1653; HDFCBANK 3 / 0.0% / -760 | 21 / 23.8% / -2000; NHPC 5 / 40.0% / -203 | 21 / 28.6% / -975; PFC 5 / 40.0% / +110 | 21 / 33.3% / -1485; IRCTC 1 / 0.0% / -195 | 21 / 38.1% / +2505; WIPRO 4 / 25.0% / -32 | 21 / 38.1% / -952; NATIONALUM 5 / 0.0% / -539 | 21 / 19.0% / -1305; VEDL 3 / 0.0% / -605 | 21 / 19.0% / -2920; HINDCOPPER 9 / 11.1% / -558 | 21 / 38.1% / -538; HINDZINC 6 / 50.0% / +465 | 21 / 42.9% / +830; HINDALCO 4 / 75.0% / +836 | 21 / 28.6% / -971; TATASTEEL 5 / 40.0% / -226 | 21 / 14.3% / -1455; ASTRAL 3 / 33.3% / -160 | 21 / 28.6% / +2599; BDL 6 / 33.3% / +8240 | 20 / 40.0% / +5820; OIL 4 / 50.0% / +45 | 21 / 14.3% / -2880; HINDUNILVR 4 / 0.0% / -2790 | 21 / 33.3% / -2674.

### 2025-06 — DONE, all 27 instruments, 21 counted trading days
- Data: Upstox 5-min via connector; cache cumulative to ~9,235 bars per instrument (NIFTY 9,235, BANKNIFTY 9,231, ITC 9,221), 123 daily rows Jan-Jun.
- V4 (cash): 110 trades, 32 targets, 77 stops, 1 square-off, win 29.1%, net ₹+1,738 combined; indices +₹6,125 (Nifty +₹16,720, Bank Nifty -₹10,595), stocks -₹4,387.
- Day Trader skill (cash): 567 trades, 140 targets, 405 stops, 22 square-offs, win 24.7%, net ₹-151,668 combined; indices -₹108,510 (Nifty -₹22,485, Bank Nifty -₹86,025), stocks -₹43,158.
- Portfolio trades/week (raw, NO cap): V4 26.19/week, Skill 135.00/week.
- Cumulative Jan-Jun 2025: V4 621 trades, net ₹-20,942 (indices -₹4,355, stocks -₹16,587); Skill 3,280 trades, net ₹-225,280 (indices -₹143,285, stocks -₹81,995).
- X verdict so far: STILL FAILS frequency for both raw runs. Win rate Jun: V4 29.1%, Skill 24.7%. No V5/skill v2 adoption yet — neither version progresses on net + win rate + frequency together on this unseen May-Jun validation stretch.
- Jun detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 3 / 33.3% / +16720 | 21 / 19.0% / -22485; BANKNIFTY 2 / 0.0% / -10595 | 21 / 14.3% / -86025; GODREJCP 2 / 50.0% / +470 | 21 / 14.3% / -5170; GLENMARK 3 / 66.7% / +1990 | 21 / 38.1% / +4350; ITC 3 / 33.3% / +60 | 21 / 33.3% / -635; RECLTD 5 / 20.0% / -440 | 21 / 28.6% / -1435; TVSMOTOR 6 / 33.3% / -610 | 21 / 14.3% / -10830; UNITDSPR 1 / 0.0% / -80 | 21 / 38.1% / +2270; OBEROIRLTY 6 / 33.3% / -290 | 21 / 14.3% / -10160; NTPC 5 / 40.0% / -315 | 21 / 19.0% / -1845; INDUSTOWER 7 / 42.9% / -85 | 21 / 28.6% / -1325; KALYANKJIL 5 / 20.0% / -185 | 21 / 28.6% / -1805; HDFCBANK 3 / 33.3% / +120 | 21 / 33.3% / -940; NHPC 5 / 40.0% / -159 | 21 / 23.8% / -1002; PFC 3 / 66.7% / +285 | 21 / 28.6% / -975; IRCTC 4 / 50.0% / -105 | 21 / 28.6% / -650; WIPRO 4 / 25.0% / -100 | 21 / 14.3% / -1629; NATIONALUM 5 / 0.0% / -431 | 21 / 23.8% / -1151; VEDL 4 / 25.0% / -595 | 21 / 23.8% / -1240; HINDCOPPER 4 / 25.0% / -320 | 21 / 19.0% / -2336; HINDZINC 4 / 25.0% / -505 | 21 / 19.0% / -2530; HINDALCO 5 / 0.0% / -1060 | 21 / 23.8% / -2375; TATASTEEL 3 / 0.0% / -182 | 21 / 19.0% / -1080; ASTRAL 5 / 20.0% / -650 | 21 / 28.6% / -4970; BDL 6 / 50.0% / -400 | 21 / 47.6% / +6610; OIL 5 / 0.0% / -680 | 21 / 14.3% / -2415; HINDUNILVR 2 / 50.0% / -120 | 21 / 38.1% / +110.

### 2025-07 — DONE, all 27 instruments, 23 counted trading days
- V4 (cash): 134 trades, 54 targets, 79 stops, 1 square-offs, win 40.3%, net ₹+27,314 combined; indices ₹+29,810 (NIFTY +23910, BANKNIFTY +5900), stocks ₹-2,496.
- Day Trader skill (cash): 621 trades, 186 targets, 410 stops, 25 square-offs, win 30.0%, net ₹-56,411 combined; indices ₹-40,070 (NIFTY +11130, BANKNIFTY -51200), stocks ₹-16,341.
- Portfolio trades/week (raw, NO cap): V4 29.13/week, Skill 135.0/week.
- Cumulative Jan-Jul 2025: V4 755 trades, net ₹+6,372 (indices +₹25,455, stocks -₹19,083 — combined positive is index point-scaling only, stocks-only still negative); Skill 3,901 trades, net ₹-281,691 (indices -₹183,355, stocks -₹98,336).
- X verdict so far: STILL FAILS frequency for both raw runs. V4 July win rate 40.3% is a one-month improvement, not a progression gate — frequency still ~29/week raw, stocks-only net still negative. No V5/skill v2 adoption yet.
- Detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 8 / 75.0% / +23910 | 23 / 39.1% / +11130; BANKNIFTY 6 / 50.0% / +5900 | 23 / 26.1% / -51200; GODREJCP 4 / 25.0% / -420 | 23 / 17.4% / -3770; GLENMARK 4 / 0.0% / -2900 | 23 / 13.0% / -6730; ITC 5 / 60.0% / +90 | 23 / 34.8% / -265; RECLTD 4 / 50.0% / -35 | 23 / 13.0% / -2695; TVSMOTOR 8 / 37.5% / +1980 | 23 / 34.8% / +2140; UNITDSPR 5 / 20.0% / -550 | 23 / 30.4% / -1000; OBEROIRLTY 2 / 0.0% / -730 | 23 / 30.4% / +2740; NTPC 6 / 16.7% / -480 | 23 / 30.4% / -1015; INDUSTOWER 8 / 37.5% / -230 | 23 / 21.7% / -2665; KALYANKJIL 3 / 0.0% / -620 | 23 / 30.4% / -1070; HDFCBANK 6 / 33.3% / -40 | 23 / 26.1% / -780; NHPC 8 / 25.0% / -373 | 23 / 34.8% / -849; PFC 9 / 22.2% / -955 | 23 / 17.4% / -2910; IRCTC 7 / 71.4% / +820 | 23 / 21.7% / -2215; WIPRO 1 / 100.0% / +50 | 23 / 21.7% / -1285; NATIONALUM 2 / 50.0% / -32 | 23 / 34.8% / -723; VEDL 4 / 75.0% / +400 | 23 / 43.5% / +530; HINDCOPPER 4 / 100.0% / +910 | 23 / 43.5% / -40; HINDZINC 5 / 40.0% / +105 | 23 / 52.2% / +690; HINDALCO 4 / 50.0% / +240 | 23 / 26.1% / -2215; TATASTEEL 5 / 0.0% / -411 | 23 / 8.7% / -1429; ASTRAL 4 / 50.0% / +850 | 23 / 34.8% / -610; BDL 3 / 33.3% / -50 | 23 / 34.8% / -1980; OIL 7 / 42.9% / +135 | 23 / 47.8% / +765; HINDUNILVR 2 / 50.0% / -250 | 23 / 39.1% / +11040.

### 2025-08 — DONE, all 27 instruments, 19 counted trading days
- V4 (cash): 116 trades, 37 targets, 78 stops, 1 square-offs, win 31.9%, net ₹-2,767 combined; indices ₹+6,250 (NIFTY +8490, BANKNIFTY -2240), stocks ₹-9,017.
- Day Trader skill (cash): 513 trades, 137 targets, 362 stops, 14 square-offs, win 26.7%, net ₹-105,517 combined; indices ₹-75,020 (NIFTY -2275, BANKNIFTY -72745), stocks ₹-30,497.
- Portfolio trades/week (raw, NO cap): V4 30.53/week, Skill 135.0/week.
- Cumulative Jan-Aug 2025: V4 871 trades, net ₹+3,605 (indices +₹31,705, stocks -₹28,100 — combined positive is index point-scaling only, stocks-only still negative); Skill 4,414 trades, net ₹-387,208 (indices -₹258,375, stocks -₹128,833).
- X verdict so far: STILL FAILS frequency for both raw runs. No V5/skill v2 adoption yet — neither version progresses on net + win rate + frequency together on Jul-Aug validation.
- Detail (V4 trades / win% / net ₹ | Skill trades / win% / net ₹): NIFTY 5 / 60.0% / +8490 | 19 / 31.6% / -2275; BANKNIFTY 6 / 33.3% / -2240 | 19 / 21.1% / -72745; GODREJCP 2 / 50.0% / +180 | 19 / 26.3% / +1100; GLENMARK 6 / 33.3% / +1390 | 19 / 15.8% / -2250; ITC 7 / 28.6% / -120 | 19 / 31.6% / -1145; RECLTD 3 / 0.0% / -500 | 19 / 47.4% / -275; TVSMOTOR 3 / 0.0% / -2250 | 19 / 36.8% / +2120; UNITDSPR 2 / 50.0% / +670 | 19 / 15.8% / -2320; OBEROIRLTY 1 / 0.0% / -410 | 19 / 31.6% / -3760; NTPC 3 / 33.3% / -275 | 19 / 21.1% / -1255; INDUSTOWER 3 / 33.3% / +140 | 19 / 26.3% / -950; KALYANKJIL 5 / 20.0% / -670 | 19 / 26.3% / -1233; HDFCBANK 5 / 40.0% / +420 | 19 / 26.3% / -820; NHPC 4 / 50.0% / -215 | 19 / 26.3% / -843; PFC 4 / 25.0% / -170 | 19 / 21.1% / -1635; IRCTC 4 / 50.0% / +490 | 19 / 36.8% / +650; WIPRO 5 / 20.0% / -191 | 19 / 26.3% / -943; NATIONALUM 5 / 40.0% / -239 | 19 / 21.1% / -992; VEDL 6 / 66.7% / -25 | 19 / 31.6% / -1290; HINDCOPPER 3 / 66.7% / +153 | 19 / 10.5% / -1499; HINDZINC 5 / 0.0% / -710 | 19 / 21.1% / -1480; HINDALCO 2 / 0.0% / -445 | 19 / 42.1% / +1645; TATASTEEL 7 / 42.9% / -225 | 19 / 21.1% / -802; ASTRAL 7 / 14.3% / -1180 | 19 / 31.6% / -710; BDL 6 / 16.7% / -2380 | 19 / 26.3% / -5020; OIL 4 / 50.0% / +25 | 19 / 31.6% / -1100; HINDUNILVR 3 / 0.0% / -2480 | 19 / 15.8% / -5690.

### NEXT: 2025-09 — not yet run
