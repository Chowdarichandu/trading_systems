# Progressive CAPPED V2 backtest — Jan 2025 to 28 Oct 2026
Paper only, no orders, no live trading. Proprietary to Chandu, workspace only.
Does NOT overwrite v1 files: v1 is ~/workspace/trading/progressive_capped_jan2025_oct2026_progress.md.
Engine: ~/workspace/trading/progressive_capped_v2.py, reading the same Upstox
5-min cache (~/workspace/trading/data/progressive/, ends 2026-10-28).

## NEW CAP RULE (Chandu, 2026-10-29 09:20 IST, replacing combined 3/week)
- Separate caps, NOT combined: max 3 index trades/week AND max 3 stock trades/week
  = 6 trades/week total, per series (V4, Skill, Unified).
- Max 1 trade per symbol per week still applies.
- STRUCTURAL NOTE, not a rule change: with only 2 index symbols (NIFTY, BANKNIFTY)
  and 1/symbol/week, the index leg can reach at most 2/week, never 3/week.
  So the attainable maximum under this rule as written is 5/week (2 index + 3 stock),
  not 6/week. This is flagged for Chandu to confirm — do not silently allow
  2 trades of one index in a week to force 3 index trades.
- Selection is ONLY more convicted, high-return setups (Chandu's words).
  Provisional implementation (NOT Chandu's rule, he only said convicted + high return):
  rank by setup quality (setup4=3, setup3=2, setup2=1, skill OR=0), then bias-strong,
  then room ratio, then prospective net target. All ranking inputs are signal-time
  / prospective, never realised outcome.
- High-return filter, provisional: prospective net target >= ₹500.
  Prospective net target = direction*(target-entry)*100 - ₹40, provisional cash exit
  (entry = next 5-min open, stop = signal low/high, target = entry +/- 2*risk).
  This is prospective size, not realised net — a trade can still stop out.
  It automatically excludes negative-net targets (v1 NHPC -₹8/-₹26 cases, where
  target distance was smaller than cost).
- Sensitivity at ₹1000 is computed per month and reported, NOT adopted on one month.
- Same provisional cash rules otherwise: 100 shares, ₹40/trade, signal-candle stop,
  2x target, square-off 15:10, Setup 1 skipped, short paper-only.
  Indices vs stocks reported separately, never combined as portfolio rupees:
  index nets are 100 shares x index points, so one index trade is ₹5,000-₹35,000
  in this scale, versus a stock trade at ₹500-₹3,000.
- Results gate NEUTRAL (0) for Jan-Mar 2025, same look-ahead reason as v1:
  v1 patterns are Sep 2025-Jun 2026 quarters, in the future relative to Jan-Mar 2025.

## Progress log — append after EACH month

### 2025-01 — DONE, 22 days, 5 ISO weeks
- Raw candidates: V4 106, skill OR 542, skill after bias+room+PD filter 176.
  Pass ₹500 filter: V4 48, skill 89. Pass ₹1000: V4 26, skill 55.
- Capped-V2 V4: 19 trades (index 7, stocks 12), 3 targets, 14 stops, 2 square-offs,
  win 15.8%, net -₹62,185 (index -₹60,445, stocks -₹1,740), 3.8/week total
  (index 1.4/week, stocks 2.4/week). Avg prospective target net: total ₹8,627,
  stocks-only ₹1,397, index ₹21,023.
- Capped-V2 Skill: 18 trades (index 5, stocks 13), 4 targets, 14 stops,
  win 22.2%, net -₹59,570 (index -₹58,345, stocks -₹1,225), 3.6/week.
  Avg prospective target net: total ₹8,087, stocks-only ₹2,268, index ₹23,218.
- Unified V2: 20 trades (index 7, stocks 13), win 15.0%, net -₹63,200
  (index -₹60,445, stocks -₹2,755), 4.0/week.
- Cumulative V2: V4 -₹62,185, Skill -₹59,570, Unified -₹63,200.
- vs v1 Jan: v1 V4 +₹599 (15 trades, all stocks), v1 Skill -₹275 (15, all stocks).
  V2 is far worse in total because the separate cap FORCES index trades that
  v1 ranked out: Jan index leg is 7 V4 trades, 0 targets, 6 stops, including
  BANKNIFTY stops -₹17,350 (13 Jan), -₹14,450 (24 Jan), -₹14,105 (6 Jan).
  Stocks leg alone is also worse than v1: V4 stocks -₹1,740 vs v1 +₹599,
  Skill stocks -₹1,225 vs v1 -₹275 — the high-return filter selected larger-risk
  stock trades, not better ones, in Jan.
- Sensitivity ₹1000, Jan: V4 17 trades / -₹64,460, Skill 18 / -₹59,570,
  Unified 20 / -₹69,100 — raising the threshold does NOT fix Jan; index leg unchanged.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-01.json

### 2025-02 — DONE, 20 days, 5 ISO weeks
- Raw candidates: V4 107, skill OR 461, skill filtered 172.
  Pass ₹500: V4 55, skill 96. Pass ₹1000: V4 33, skill 59.
- Capped-V2 V4: 22 trades (index 8, stocks 14), 10 targets, 11 stops, 1 square-off,
  win 45.5%, net +₹61,830 (index +₹61,650, stocks +₹180), 4.4/week.
  Avg prospective target net: total ₹7,032, stocks-only ₹936, index ₹17,700.
- Capped-V2 Skill: 20 trades (index 7, stocks 13), 8 targets, 12 stops,
  win 40.0%, net +₹36,370 (index +₹42,795, stocks -₹6,425), 4.0/week.
  Avg prospective target net: total ₹7,333, stocks-only ₹2,223, index ₹16,821.
- Unified V2: 23 trades (index 8, stocks 15), win 43.5%, net +₹60,060
  (index +₹61,650, stocks -₹1,590), 4.6/week.
- Cumulative V2: V4 -₹355 (-₹62,185+₹61,830), Skill -₹23,200, Unified -₹3,140.
  Feb almost exactly erases Jan's V2 total — a swing, not progression.
  Stocks-only cumulative: V4 -₹1,560, Skill -₹7,650, Unified -₹4,345.
- Feb total is again index-driven, now on the upside: V4 index +₹61,650
  (4 targets, 4 stops). Stocks leg Feb is near-flat for V4 (+₹180) and
  negative for Skill (-₹6,425). High-return filtering did NOT produce a
  stocks progression in Feb.
- Sensitivity ₹1000, Feb: V4 18 trades / +₹60,705 (index +₹61,650, stocks -₹945),
  Skill 19 / +₹34,360, Unified 22 / +₹58,070 — same index story, stocks worse.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-02.json

### 2025-03 — DONE, 19 days, 4 ISO weeks
- Raw candidates: V4 102, skill OR 423, skill filtered 59 (stricter month, as in v1).
  Pass ₹500: V4 31, skill 27. Pass ₹1000: V4 17, skill 15.
- Capped-V2 V4: 16 trades (index 4, stocks 12), 6 targets, 9 stops, 1 square-off,
  win 37.5%, net -₹10,285 (index -₹14,200, stocks +₹3,915), 4.0/week.
  Avg prospective target net: total ₹3,473, stocks-only ₹1,111, index ₹10,558.
- Capped-V2 Skill: 13 trades (index 2, stocks 11), 5 targets, 5 stops, 3 square-offs,
  win 38.5%, net -₹1,055 (index -₹7,090, stocks +₹6,035), 3.25/week.
  Avg prospective target net: total ₹3,168, stocks-only ₹1,232, index ₹13,815.
- Unified V2: 16 trades, same as V4 (-₹10,285; index -₹14,200, stocks +₹3,915).
- Cumulative V2: V4 -₹10,640, Skill -₹24,255, Unified -₹13,425.
  Stocks-only cumulative: V4 +₹2,355, Skill -₹1,615, Unified -₹430.
- Mar is the first V2 month where the stocks leg is genuinely positive for
  both series (+₹3,915 V4, +₹6,035 Skill), but totals still fall because
  the index leg loses -₹14,200 / -₹7,090. Mar does NOT restore progression
  in total, and V4 stocks-only (+₹2,355 cumulative) is only marginally above
  v1's Mar stocks cumulative (+₹2,083) after three months of index volatility.
- Sensitivity ₹1000, Mar: V4 13 trades / -₹11,545 (stocks +₹2,655),
  Skill 9 / +₹2,025 (stocks +₹9,115, index -₹7,090), Unified 16 / -₹6,165
  (stocks +₹8,035). At ₹1000, Skill stocks improve in Mar alone — one month,
  NOT an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-03.json

## Cumulative progression (V2, to Mar 2025)
| Series | Jan | Feb | Mar | Trades to Mar | Win to Mar |
|---|---|---|---|---|---|
| V2-V4 total | -₹62,185 | -₹355 | -₹10,640 (FALL) | 57 | 33.3% (19 targets) |
| V2-V4 stocks-only | -₹1,740 | -₹1,560 | +₹2,355 | 57 | — |
| V2-Skill total | -₹59,570 | -₹23,200 | -₹24,255 (FALL) | 51 | 33.3% (17 targets) |
| V2-Skill stocks-only | -₹1,225 | -₹7,650 | -₹1,615 | 51 | — |
| V2-Unified total | -₹63,200 | -₹3,140 | -₹13,425 (FALL) | 59 | 32.2% (19 targets) |
| V2-Unified stocks-only | -₹2,755 | -₹4,345 | -₹430 | 59 | — |

## X verdict under NEW frequency definition (6/week intended, 5/week attainable) — to Mar 2025
- Frequency: PASS on count — 3.25-4.6 trades/week total, never 500+, and
  index/stock legs are separately capped. But the intended 6/week is NOT
  attained: index leg peaks at 1.6/week because only 2 index symbols exist
  under 1/symbol/week. Confirm with Chandu whether 3 index/week means
  allowing a second trade of the same index in a week, or accepting 2/week.
- High-return filtering: YES, prospective target size rises vs v1's ₹300 small wins
  — stocks-only avg prospective target ₹936-₹2,268 per month (vs v1 realised
  targets often ₹60-₹300) — but realised net does NOT follow: Jan-Feb stocks
  legs are negative/flat, and index prospective targets ₹10,558-₹23,218 come
  with equally large stops, so totals swing -₹62k / +₹62k / -₹10k.
  Bigger target alone is not conviction, and it does not create progression.
- Net progression: FAILS in total for all series (V4 -₹10,640, Skill -₹24,255,
  Unified -₹13,425 after 3 months, vs v1 Mar totals V4 +₹2,083, Skill +₹7,576).
  Stocks-only: V4 +₹2,355 is the only positive cumulative, Skill and Unified
  are negative. No series progresses monotonically in total or stocks-only.
- Win rate to Mar: V2 33.3% / 33.3% / 32.2%, below v1 Mar (V4 40.5%, Skill 48.8%).
- NO V2 ADOPTION on Jan-Mar alone: 3 months, index-forced volatility, and
  the ₹500 threshold is provisional. Next test (not adopted): whether
  excluding index point-scaled trades from the same rupee total, or sizing
  index trades by risk rather than 100 shares, changes the verdict — because
  as coded, 100 shares x index points makes one index trade worth ~20 stock trades.
- Next: Apr 2025, then month by month to 28 Oct 2026, same V2 rules.

### 2025-04 — DONE, 19 days, 5 ISO weeks
- Raw: V4 77, skill OR 435, skill filtered 74; pass ₹500: V4 27, Skill 38.
- V2-V4: 17 trades, 5 targets, 8 stops, 4 square-offs, win 29.4%, net **-₹12,077** (indices -₹11,865 / stocks -₹212), 3.4/week. Avg prospective target net ₹5,784.
- V2-Skill: 18 trades, 7 targets, 8 stops, 3 square-offs, win 38.9%, net **+₹46,458** (indices +₹44,855 / stocks +₹1,603), 3.6/week. Avg prospective target net ₹6,164.
- V2-Unified: 21 trades, 6 targets, 10 stops, 5 square-offs, win 28.6%, net **+₹2,002** (indices +₹3,165 / stocks -₹1,163), 4.2/week.
- Cumulative V2: V4 -₹22,717 (FALL), Skill +₹22,203 (rises, first positive total), Unified -₹11,423 (rises, still negative). Stocks-only cumulative: V4 +₹2,143, Skill -₹12, Unified -₹1,593.
- FRAGILITY FLAG, Apr: V4 index leg is three Bank Nifty stops (-₹11,540 on 2025-04-01, -₹10,665 on 2025-04-09, -₹10,070 on 2025-04-23) partly offset by Nifty +₹14,770 on 2025-04-01. Skill total is one Bank Nifty target +₹33,980 on 2025-04-25 plus Nifty +₹15,030 on 2025-04-28; without those two index trades Skill Apr is near flat on stocks (+₹1,603). Apr is NOT a stocks progression for any series.
- Sensitivity ₹1000, Apr: V4 16 / -₹10,145 (stocks +₹1,720), Skill 16 / +₹47,610 (stocks +₹2,755), Unified 20 / +₹3,690 (stocks +₹525). Same index dominance, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-04.json, same V2 rules (separate 3 index/week + 3 stock/week, max 1/symbol/week, prospective net target >= ₹500, ranking conviction > bias > room > net target). Results gate NEUTRAL, same look-ahead reason as Jan-Mar.

### 2025-05 — DONE, 21 days, 5 ISO weeks
- Raw: V4 119, skill OR 451, skill filtered 95; pass ₹500: V4 44, Skill 46.
- V2-V4: 23 trades, 4 targets, 18 stops, 1 square-off, win 17.4%, net **+₹8,325** (indices +₹11,115 / stocks -₹2,790), 4.6/week. Avg prospective target net ₹6,607.
- V2-Skill: 18 trades, 4 targets, 13 stops, 1 square-off, win 22.2%, net **-₹41,853** (indices -₹39,435 / stocks -₹2,418), 3.6/week. Avg prospective target net ₹5,373.
- V2-Unified: 23 trades, same as V2-V4 (+₹8,325; indices +₹11,115 / stocks -₹2,790), 4.6/week.
- Cumulative V2: V4 -₹14,392 (rises, still negative), Skill -₹19,650 (FALLS sharply, erasing Apr), Unified -₹3,098 (rises, still negative). Stocks-only cumulative: V4 -₹647, Skill -₹2,430, Unified -₹4,383. All stocks legs FALL in May.
- FRAGILITY FLAG, May: V4 total is two Bank Nifty targets (+₹27,330 on 2025-05-07, +₹21,930 on 2025-05-15) against Bank Nifty stops -₹13,810 (2025-05-27) and -₹11,300 (2025-05-20). Skill index leg is 5 stops, 0 targets (-₹39,435), worst Bank Nifty -₹11,300 (2025-05-20), -₹10,330 (2025-05-05), -₹9,330 (2025-05-27). May is NOT a stocks progression; stocks-only is negative for every series.
- Sensitivity ₹1000, May: V4 21 / +₹10,356 (stocks -₹759), Skill 18 / -₹46,103 (stocks -₹6,668), Unified 22 / +₹9,116 (stocks -₹1,999). Same pattern, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-05.json, same V2 rules. Results gate NEUTRAL.

### 2025-06 — DONE, 21 days, 5 ISO weeks
- Raw: V4 110, skill OR 481, skill filtered 79; pass ₹500: V4 28, Skill 29.
- V2-V4: 17 trades, 6 targets, 11 stops, win 35.3%, net **+₹7,935** (indices +₹6,125 / stocks +₹1,810), 3.4/week. Avg prospective target net ₹4,265.
- V2-Skill: 13 trades, 7 targets, 5 stops, 1 square-off, win 53.8%, net **+₹2,545** (indices -₹4,685 / stocks +₹7,230), 2.6/week. Avg prospective target net ₹2,344.
- V2-Unified: 18 trades, 7 targets, 11 stops, win 38.9%, net **+₹10,035** (indices +₹6,125 / stocks +₹3,910), 3.6/week.
- Cumulative V2: V4 -₹6,457 (rises, still negative), Skill -₹17,105 (rises, still negative), Unified +₹6,937 (rises, first positive unified total). Stocks-only cumulative: V4 +₹1,163, Skill +₹4,800, Unified -₹473. Jun is the first month where V4 and Skill stocks legs are BOTH positive in the month, but cumulative stocks-only is still small vs index volatility.
- FRAGILITY FLAG, Jun: V4 total still contains the single Nifty target +₹22,260 on 2025-06-06 (same as v1); without it V4 Jun index leg is negative and V4 Jun total is negative. Skill Jun is the cleanest stocks month so far (stocks +₹7,230, 58.3% win on stocks, best UNITDSPR +₹2,100, ASTRAL +₹1,960), but one month is not a validated progression, and its total is dragged by a single Bank Nifty stop -₹4,685 on 2025-06-10.
- Sensitivity ₹1000, Jun: V4 15 / +₹8,165 (stocks +₹2,040), Skill 13 / -₹1,795 (stocks +₹2,890), Unified 18 / +₹7,975 (stocks +₹1,850). Skill flips negative at ₹1000 in Jun alone — threshold sensitivity, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-06.json, same V2 rules. Results gate NEUTRAL.

## Cumulative progression (V2, to Jun 2025)
| Series | Mar | Apr | May | Jun | Trades to Jun | Win to Jun |
|---|---|---|---|---|---|---|
| V2-V4 total | -₹10,640 | -₹22,717 (FALL) | -₹14,392 (rises) | -₹6,457 (rises, still negative) | 114 | 29.8% (34 targets) |
| V2-V4 stocks-only | +₹2,355 | +₹2,143 (FALL) | -₹647 (FALL) | +₹1,163 (rises) | 114 | — |
| V2-Skill total | -₹24,255 | +₹22,203 (rises) | -₹19,650 (FALL) | -₹17,105 (rises, still negative) | 100 | 35.0% (35 targets) |
| V2-Skill stocks-only | -₹1,615 | -₹12 (rises) | -₹2,430 (FALL) | +₹4,800 (rises) | 100 | — |
| V2-Unified total | -₹13,425 | -₹11,423 (rises) | -₹3,098 (rises) | +₹6,937 (rises, first positive) | 121 | 29.8% (36 targets) |
| V2-Unified stocks-only | -₹430 | -₹1,593 (FALL) | -₹4,383 (FALL) | -₹473 (rises, still negative) | 121 | — |

## X verdict under NEW frequency definition (6/week intended, 5/week attainable) — to Jun 2025
- Frequency: PASS on count — 2.6–4.6 trades/week total, never 500+, separately capped. Index leg still peaks at 1.6/week (May V4) because only NIFTY + BANKNIFTY exist under 1/symbol/week; the intended 3 index/week is NOT attained under the written rule. Parent is asking Chandu about this separately — do NOT change the rule silently.
- High-return filtering: prospective targets are high (avg ₹2,344–₹6,607/month), and Jun Skill stocks (+₹7,230, 58.3% win) is the first clean stocks month, but realised stocks-only cumulative to Jun is tiny (V4 +₹1,163, Skill +₹4,800, Unified -₹473) vs index swings of ±₹40k in a month. Bigger prospective target alone still does not create progression.
- Net progression: FAILS as monotonic progression for all series in total and stocks-only. Totals rise May–Jun but remain negative except Unified (+₹6,937, entirely index-driven: Jun Nifty +₹22,260 + May Bank Nifty net); stocks-only Unified is still negative. Skill total swings +₹46k (Apr) to -₹42k (May) — volatility, not progression.
- Win rate to Jun: V2 29.8% / 35.0% / 29.8%, still below v1 Jun (V4 36.8%, Skill 38.4%).
- NO V2 ADOPTION on Jan–Jun: progression on net + win rate + frequency together AND stocks-only net is not met. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. Candidate test (not adopted): exclude/cap index point-scaled size, since index trades dominate every total.
### 2025-07 — DONE, 23 days, 5 ISO weeks
- Raw: V4 134, skill OR 516, skill filtered 125; pass ₹500: V4 35, Skill 56.
- V2-V4: 23 trades (index 9, stocks 14), 10 targets, 12 stops, 1 square-off, win 43.5%, net **+₹18,770** (indices +₹16,965 / stocks +₹1,805), 4.6/week. Avg prospective target net ₹4,967.
- V2-Skill: 22 trades (index 7, stocks 15), 8 targets, 12 stops, 2 square-offs, win 36.4%, net **+₹18,100** (indices +₹14,875 / stocks +₹3,225), 4.4/week. Avg prospective target net ₹4,281.
- V2-Unified: 24 trades (index 9, stocks 15), 11 targets, 12 stops, 1 square-off, win 45.8%, net **+₹20,630** (indices +₹16,965 / stocks +₹3,665), 4.8/week.
- Cumulative V2: V4 +₹12,313 (rises, first positive V4 total), Skill +₹995 (rises, first positive Skill total), Unified +₹27,567 (rises). Stocks-only cumulative: V4 +₹2,968, Skill +₹8,025, Unified +₹3,192 — all three stocks legs rise in Jul, but totals are still index-dominated.
- FRAGILITY FLAG, Jul: V4 index leg is BANKNIFTY +₹12,550 (18 Jul) and +₹10,520 (11 Jul) against BANKNIFTY stops -₹13,485 (31 Jul) and -₹8,020 (4 Jul). Skill index leg is the same two targets. Without the index leg, Jul stocks nets are only +₹1,805 / +₹3,225 / +₹3,665 — positive but small vs index swings.
- Sensitivity ₹1000, Jul: V4 18 / +₹19,365 (stocks +₹2,400), Skill 20 / +₹22,325 (stocks +₹7,450), Unified 24 / +₹25,515 (stocks +₹8,550) — higher threshold improves Jul stocks for Skill/Unified alone, NOT an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-07.json, same V2 rules. Results gate NEUTRAL.

### 2025-08 — DONE, 19 days, 5 ISO weeks
- Raw: V4 116, skill OR 425, skill filtered 147; pass ₹500: V4 37, Skill 54.
- V2-V4: 21 trades (index 8, stocks 13), 5 targets, 16 stops, win 23.8%, net **-₹5,455** (indices +₹1,525 / stocks -₹6,980), 4.2/week. Avg prospective target net ₹4,178.
- V2-Skill: 19 trades (index 6, stocks 13), 7 targets, 11 stops, 1 square-off, win 36.8%, net **+₹6,265** (indices +₹5,665 / stocks +₹600), 3.8/week. Avg prospective target net ₹4,094.
- V2-Unified: 22 trades (index 8, stocks 14), 5 targets, 16 stops, 1 square-off, win 22.7%, net **-₹3,215** (indices +₹1,525 / stocks -₹4,740), 4.4/week.
- Cumulative V2: V4 +₹6,858 (FALLS), Skill +₹7,260 (rises), Unified +₹24,352 (FALLS). Stocks-only cumulative: V4 -₹4,012 (FALLS sharply), Skill +₹8,625 (rises), Unified -₹1,548 (FALLS).
- FRAGILITY FLAG, Aug: V4 stocks leg is 1 target in 13 trades (7.7% win, -₹6,980) — the ₹500 high-return filter selected stock trades that almost all stopped out. Index leg (+₹1,525) is BANKNIFTY +₹12,610 (22 Aug) and NIFTY +₹6,720 (7 Aug) against BANKNIFTY stops -₹12,860 (4 Aug) and -₹5,690 (1 Aug). Aug is NOT a stocks progression for V4/Unified.
- Sensitivity ₹1000, Aug: V4 16 / -₹5,315 (stocks -₹6,840), Skill 19 / +₹4,165 (stocks -₹1,500), Unified 21 / -₹2,165 (stocks -₹3,690) — same pattern, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-08.json, same V2 rules. Results gate NEUTRAL.

### 2025-09 — DONE, 22 days, 5 ISO weeks
- Raw: V4 103, skill OR 415, skill filtered 77; pass ₹500: V4 23, Skill 27.
- V2-V4: 18 trades (index 7, stocks 11), 1 target, 14 stops, 3 square-offs, win 5.6%, net **-₹38,224** (indices -₹35,205 / stocks -₹3,019), 3.6/week. Avg prospective target net ₹4,511.
- V2-Skill: 12 trades (index 2, stocks 10), 2 targets, 7 stops, 3 square-offs, win 16.7%, net **-₹5,549** (indices -₹4,970 / stocks -₹579), 2.4/week. Avg prospective target net ₹1,973.
- V2-Unified: 21 trades (index 7, stocks 14), 2 targets, 15 stops, 4 square-offs, win 9.5%, net **-₹35,854** (indices -₹35,205 / stocks -₹649), 4.2/week.
- Cumulative V2 (verified by summing all 9 capped_v2_summary JSONs Jan–Sep 2025): V4 **-₹31,366** (FALLS sharply), Skill **+₹1,711** (FALLS), Unified **-₹11,502** (FALLS sharply). Stocks-only cumulative: V4 **-₹7,031** (FALLS), Skill **+₹8,046** (FALLS slightly), Unified **-₹2,197** (FALLS).
- FRAGILITY FLAG, Sep: V4 index leg is 7 stops, 0 targets (-₹35,205), worst BANKNIFTY -₹10,905 (5 Sep) and NIFTY -₹7,805 (5 Sep, same day). V4's only target in 18 trades is GLENMARK +₹780; its best stock trade after that is only +₹100. Sep is the worst V2 month on win rate and total for V4/Unified, and it erases all of Jul–Aug total gains. Skill Sep is much smaller (-₹5,549) only because far fewer index candidates passed its filter (2 index trades vs V4's 7).
- Sensitivity ₹1000, Sep: V4 11 / -₹36,825 (stocks -₹1,620), Skill 9 / -₹4,330 (stocks +₹640), Unified 17 / -₹34,885 (stocks +₹320) — raising the threshold does NOT fix Sep; index stops dominate.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-09.json, same V2 rules. Results gate NEUTRAL (v1 patterns are Sep 2025–Jun 2026 quarters, not knowable at Sep signal time; Sep is the first pattern quarter itself).

## Cumulative progression (V2, to Sep 2025)
| Series | Jun | Jul | Aug | Sep | Trades to Sep | Win to Sep |
|---|---|---|---|---|---|---|
| V2-V4 total | -₹6,457 | +₹12,313 (rises) | +₹6,858 (FALL) | -₹31,366 (FALL) | 176 | 28.4% (50 targets) |
| V2-V4 stocks-only | +₹1,163 | +₹2,968 (rises) | -₹4,012 (FALL) | -₹7,031 (FALL) | 176 | — |
| V2-Skill total | -₹17,105 | +₹995 (rises) | +₹7,260 (rises) | +₹1,711 (FALL) | 153 | 34.0% (52 targets) |
| V2-Skill stocks-only | +₹4,800 | +₹8,025 (rises) | +₹8,625 (rises) | +₹8,046 (FALL) | 153 | — |
| V2-Unified total | +₹6,937 | +₹27,567 (rises) | +₹24,352 (FALL) | -₹11,502 (FALL) | 188 | 28.7% (54 targets) |
| V2-Unified stocks-only | -₹473 | +₹3,192 (rises) | -₹1,548 (FALL) | -₹2,197 (FALL) | 188 | — |

## X verdict under NEW frequency definition (6/week intended, 5/week attainable) — to Sep 2025
- Frequency: PASS on count — 2.4–4.8 trades/week total, never 500+, separately capped. Index leg peaks at 1.8/week (Jul V4/Unified); the intended 3 index/week is still NOT attained under 1/symbol/week with only 2 index symbols.
- High-return filtering: prospective targets stay high (avg ₹1,973–₹4,967/month), but realised Sep shows the failure mode clearly: high prospective target + 0 index targets in V4 = -₹35,205 index leg in one month. Bigger target alone is not conviction.
- Net progression: FAILS for all series in total and stocks-only to Sep. V4 and Unified fall Aug and Sep in a row and turn cumulatively negative; Skill total (+₹1,711) is barely positive and its stocks-only (+₹8,046) is the only positive cumulative, but it fell in Sep and is far below its index-driven swings. No series progresses monotonically.
- Win rate to Sep: V2 28.4% / 34.0% / 28.7%, below v1 Sep (V4 31.8%, Skill 36.7% on the combined-cap series).
- NO V2 ADOPTION on Jan–Sep: progression on net + win rate + frequency together AND stocks-only net is not met. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. Candidate test (not adopted): exclude/cap index point-scaled size, since index trades dominate every total in both directions (Jul +₹17k, Sep -₹35k).
### 2025-10 — DONE, 21 days, 5 ISO weeks
- Raw: V4 112, skill OR 454, skill filtered 80; pass ₹500: V4 25, Skill 27.
- V2-V4: 19 trades (index 7, stocks 12), 10 targets, 5 stops, 4 square-offs, win 52.6%, net **+₹71,970** (indices +₹72,090 / stocks -₹120), 3.8/week. Avg prospective target net ₹4,415.
- V2-Skill: 16 trades (index 2, stocks 14), 3 targets, 10 stops, 3 square-offs, win 18.8%, net **+₹8,770** (indices +₹14,045 / stocks -₹5,275), 3.2/week. Avg prospective target net ₹2,248.
- V2-Unified: 22 trades (index 7, stocks 15), 10 targets, 7 stops, 5 square-offs, win 45.5%, net **+₹70,440** (indices +₹72,090 / stocks -₹1,650), 4.4/week.
- Cumulative V2 (Sep base + Oct): V4 +₹40,604 (rises, first large positive total since Jul), Skill +₹10,481 (rises), Unified +₹58,938 (rises). Stocks-only cumulative: V4 -₹7,151 (FALLS slightly), Skill +₹2,771 (FALLS sharply), Unified -₹3,847 (FALLS). All totals rise in Oct, but NO stocks leg rises — Oct is not a stocks progression.
- FRAGILITY FLAG, Oct: V4 index leg is 7 targets, 0 stops (+₹72,090) — BANKNIFTY PE targets +₹20,820 (24 Oct), +₹17,840 (31 Oct), +₹8,760 (8 Oct), NIFTY PE +₹8,130 (24 Oct). This single-month index swing is larger than the entire Jan–Sep V4 total move and reverses Sep's -₹35,205 index leg in the opposite direction. Stocks legs are -₹120 / -₹5,275 / -₹1,650 despite V4's 52.6% overall win rate, because the win rate is carried by index targets. Oct does NOT validate V2 on stocks-only net.
- Sensitivity ₹1000, Oct: V4 13 / +₹71,340 (stocks -₹750), Skill 11 / +₹7,155 (stocks -₹6,890), Unified 19 / +₹67,110 (stocks -₹4,980) — same index dominance, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-10.json, same V2 rules. Results gate NEUTRAL (v1 patterns are Sep 2025–Jun 2026 quarters, not knowable at Oct signal time; Oct is the second pattern quarter itself).
### 2025-11 — DONE, 19 days, 4 ISO weeks
- Raw: V4 111, skill OR 420, skill filtered 115; pass ₹500: V4 30, Skill 35.
- V2-V4: 17 trades (index 5, stocks 12), 0 targets, 15 stops, 2 square-offs, win 0.0%, net **-₹14,240** (indices -₹7,260 / stocks -₹6,980), 4.25/week. Avg prospective target net ₹3,069.
- V2-Skill: 15 trades (index 4, stocks 11), 7 targets, 7 stops, 1 square-off, win 46.7%, net **-₹4,355** (indices -₹10,350 / stocks +₹5,995), 3.75/week. Avg prospective target net ₹3,683.
- V2-Unified: 17 trades, same as V2-V4 (-₹14,240; indices -₹7,260 / stocks -₹6,980).
- Cumulative V2: V4 +₹26,364 (FALLS), Skill +₹6,126 (FALLS), Unified +₹44,698 (FALLS). Stocks-only cumulative: V4 -₹14,131 (FALLS sharply), Skill +₹8,766 (rises — the only rising stocks leg in Nov), Unified -₹10,827 (FALLS sharply).
- FRAGILITY FLAG, Nov: V4 has 0 targets in 17 trades — the ₹500 high-return filter selected trades that all stopped out or squared off, including BANKNIFTY stops -₹5,355 (19 Nov) and -₹3,680 (6 Nov). Its best trade is a NIFTY square-off +₹7,020, not a target. Skill diverges sharply in the same month: 63.6% win on stocks (+₹5,995) but -₹10,350 on indices (BANKNIFTY stops -₹8,335, -₹5,355, -₹3,680). Nov proves V4 and Skill are not interchangeable under V2 ranking — same month, opposite stocks legs.
- Sensitivity ₹1000, Nov: V4 14 / -₹7,710 (stocks -₹450), Skill 14 / -₹10,260 (stocks +₹90), Unified 16 / -₹5,150 (stocks +₹2,110) — raising the threshold softens V4 stocks but does not fix totals; index stops dominate again, not an adoption basis.
- Source: ~/workspace/trading/data/progressive/capped_v2_summary_2025-11.json, same V2 rules. Results gate NEUTRAL.
- Next: Dec 2025, then month by month to 28 Oct 2026, same V2 rules.
