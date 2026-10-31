# Progressive CAPPED backtest — Jan 2025 to 28 Oct 2026
Paper only, no orders, no live trading. Proprietary to Chandu, workspace only.
STOPPED raw series: the raw progressive run (621 skill trades in July, etc.)
is NOT what Chandu wants. This capped series replaces it for forward work.
The sibling raw agent (Sep 2025 onward) must be stopped by the parent agent —
this subagent cannot stop sibling agents; do not merge raw totals into this file.

## Why raw was too many
July raw skill = 621 trades = 27 instruments × 23 days, i.e. 1 trade per
instrument per day, no filter. V4 in July was only 134 trades because its
filters (bias, PD-level cross, room, rejection, reclaim, one per instrument/day)
block most days. Skill has no such filter, so it trades every day.
Fix here: skill pool is restricted first, then a portfolio cap is applied.

## Capped rules (fixed in advance, signal-time only, no outcome used in ranking)
- Instruments: Nifty, Bank Nifty, 25 stocks (same list as raw run).
- V4 candidates: as in progressive_engine (bias, PD cross, room, rejection/reclaim).
- Skill candidates: OR-only. Flag/oversold dropped as entries (earlier ablation:
  flag adds losing trades, oversold never fired first).
- Skill OR passes ONLY if V4-style filters pass: bias-aligned (bearish->PE only,
  bullish->CE only, neutral->both) AND room >= 200*scale to next PD level AND
  PD bound (CE close < PDH, PE close < PDL).
- Ranking, in order: setup quality (setup4=3, setup3=2, setup2=1, skill OR=0),
  then room ratio, then bias-strong (non-neutral), then results-gate pass.
  Room ratio is capped at 5.0; unbounded room (no next PD level) is scored 1.0,
  NOT top-ranked — an earlier run scored it 99.0 and it wrongly topped the
  skill cap with two huge Bank Nifty stops (-₹31,590 in Jan). That bug was
  found and fixed before Feb/Mar were run; Jan numbers after the fix are
  therefore not pure out-of-sample for that fix, Feb/Mar are unseen for it.
- Portfolio cap: max 3 trades per ISO week TOTAL per series, max 1 trade per
  symbol per week. Series: capped-V4, capped-Skill, unified (best of both,
  deduplicated by symbol+date, same ranking — so unified collapses to capped-V4
  in Jan-Mar because V4 supply exceeds the cap every week; skill never makes
  the unified top 3 in those months. That is a finding, not a bug, under the
  specified ranking order).
- Results gate: NEUTRAL (0) for Jan-Mar 2025. The v1 patterns are derived from
  Sep 2025-Jun 2026 quarters, which are in the FUTURE relative to Jan-Mar 2025,
  so using them there would be look-ahead. The gate can only apply after the
  pattern quarters are known.
- Provisional cash rules (NOT Chandu's rules): 100 shares, ₹40/trade, stop =
  signal-candle low/high, target = 2x stop distance, square-off 15:10, short
  paper-only, Setup 1 skipped. Indices vs stocks reported separately, never
  combined as a portfolio rupee result (index cash-equivalents are point-scaled).
- Engine: ~/workspace/trading/progressive_capped.py, reading the same Upstox
  5-min cache as the raw run (~/workspace/trading/data/progressive/).
  Upstox connector tested first 2026-10-29: Bank Nifty search succeeds, no 401.
- PROGRESSION GOAL: cumulative net must progress upward month by month.
  A month where cumulative falls is flagged as a failure to fix, not accepted.

## Progress log — append after EACH month

### 2025-01 — DONE, 22 days, 5 ISO weeks
- Raw candidates: V4 106, skill OR 542, skill after bias+room+PD filter 176.
- Capped-V4: 15 trades, 9 targets, 6 stops, win 60.0%, net +₹599, expectancy +₹39.93, max DD ₹2,509, 3.0/week. Split: indices ₹0, stocks +₹599.
- Capped-Skill: 15 trades, 7 targets, 8 stops, win 46.7%, net -₹275, expectancy -₹18.33, max DD ₹4,065, 3.0/week. Split: indices ₹0, stocks -₹275.
- Unified capped: 15 trades, same as capped-V4 (+₹599) — V4 outranks skill every week.
- Cumulative: V4 +₹599, Skill -₹275, Unified +₹599. Capped trades are stocks-only in Jan (stock candidates outrank index candidates on room/setup; indices ranked out, not judged bad).

### 2025-02 — DONE, 20 days, 5 ISO weeks
- Raw candidates: V4 107, skill OR 461, skill filtered 172.
- Capped-V4: 15 trades, 5 targets, 9 stops, 1 square-off, win 33.3%, net -₹600, 3.0/week. Split: indices ₹0, stocks -₹600.
- Capped-Skill: 14 trades, 6 targets, 7 stops, 1 square-off, win 42.9%, net +₹2,044, 2.8/week (one week had <3 eligible after per-symbol cap). Split: indices ₹0, stocks +₹2,044.
- Unified capped: 15 trades, same as capped-V4 (-₹600).
- Cumulative: V4 -₹1 (₹599-₹600) — FALLS in Feb, flagged as failure to fix. Skill +₹1,769 — rises. Unified -₹1 — falls, same as V4.

### 2025-03 — DONE, 19 days, 4 ISO weeks
- Raw candidates: V4 102, skill OR 423, skill filtered 59 (filter is stricter in Mar: fewer OR signals pass bias+room+PD bound).
- Capped-V4: 12 trades, 3 targets, 6 stops, 3 square-offs, win 25.0%, net +₹2,084, 3.0/week. Split: indices ₹0, stocks +₹2,084.
- Capped-Skill: 12 trades, 7 targets, 3 stops, 2 square-offs, win 58.3%, net +₹5,807, 3.0/week. Split: indices ₹0, stocks +₹5,807.
- Unified capped: 12 trades, same as capped-V4 (+₹2,084).
- Cumulative: V4 +₹2,083, Skill +₹7,576, Unified +₹2,083. Mar recovers V4 above its Jan peak, but the Feb dip remains a flagged failure month.

### 2025-04 — DONE, 19 days, 5 ISO weeks
- Raw candidates: V4 77, skill OR 435, skill after bias+room+PD filter 74.
- Capped-V4: 15 trades, 5 targets, 8 stops, 2 square-offs, win 33.3%, net -₹1,136, expectancy -₹75.73, max DD ₹1,976, 3.0/week. Split: indices ₹0, stocks -₹1,136.
- Capped-Skill: 15 trades, 6 targets, 9 stops, 0 square-offs, win 40.0%, net -₹1,250, expectancy -₹83.33, max DD ₹1,930, 3.0/week. Split: indices ₹0, stocks -₹1,250.
- Unified capped: 15 trades, same as capped-V4 (-₹1,136) — V4 outranks skill every week.
- Cumulative: V4 +₹947 (₹2,083-₹1,136) — FALLS in Apr, flagged as failure to fix. Skill +₹6,326 (₹7,576-₹1,250) — FALLS in Apr, flagged. Unified +₹947 — falls, same as V4.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-04.json, engine ~/workspace/trading/progressive_capped.py, same capped rules as Jan-Mar. Results gate NEUTRAL (0) for Apr 2025, same look-ahead reason as Jan-Mar (v1 patterns are Sep 2025-Jun 2026 quarters, in the future relative to Apr 2025).

### 2025-05 — DONE, 21 days, 5 ISO weeks
- Raw candidates: V4 119, skill OR 451, skill after bias+room+PD filter 95.
- Capped-V4: 15 trades, 3 targets, 12 stops, 0 square-offs, win 20.0%, net +₹1,015, expectancy +₹67.67, max DD ₹18,423, 3.0/week. Split: indices +₹8,120, stocks -₹7,105.
- Capped-Skill: 15 trades, 3 targets, 10 stops, 2 square-offs, win 20.0%, net -₹3,013, expectancy -₹200.87, max DD ₹4,014, 3.0/week. Split: indices ₹0, stocks -₹3,013.
- Unified capped: 15 trades, same as capped-V4 (+₹1,015).
- Cumulative: V4 +₹1,962 (₹947+₹1,015) — rises vs Apr but still BELOW the Mar peak ₹2,083, so progression is not restored. Skill +₹3,313 (₹6,326-₹3,013) — FALLS in May, flagged. Unified +₹1,962 — same as V4.
- FRAGILITY FLAG, May V4: the +₹1,015 month net is a single Bank Nifty point-scaled pair — 2025-05-15 BANKNIFTY setup4_reclaim CE target +₹21,930, offset by 2025-05-27 BANKNIFTY stop -₹13,810. Without those two index trades, V4 May stocks-only is -₹7,105. This is NOT a stocks progression, and index cash-equivalent rupees must not be read as portfolio rupees. Same point-scale warning as the raw series, now inside the capped series.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-05.json, same capped rules. Results gate NEUTRAL (0), same look-ahead reason.

### 2025-06 — DONE, 21 days, 5 ISO weeks
- Raw candidates: V4 110, skill OR 481, skill after bias+room+PD filter 79.
- Capped-V4: 15 trades, 7 targets, 7 stops, 1 square-off, win 46.7%, net +₹25,417, expectancy +₹1,694.47, max DD ₹690, 3.0/week. Split: indices +₹22,260, stocks +₹3,157.
- Capped-Skill: 15 trades, 4 targets, 9 stops, 2 square-offs, win 26.7%, net +₹605, expectancy +₹40.33, max DD ₹1,255, 3.0/week. Split: indices ₹0, stocks +₹605.
- Unified capped: 15 trades, same as capped-V4 (+₹25,417).
- Cumulative: V4 +₹27,379 (₹1,962+₹25,417) — rises in total, but see flag below. Skill +₹3,918 (₹3,313+₹605) — rises vs May, still BELOW the Mar peak ₹7,576, so progression is not restored. Unified +₹27,379 — same as V4.
- FRAGILITY FLAG, Jun V4: the +₹25,417 is again a single index trade — 2025-06-06 NIFTY setup4_reclaim CE target +₹22,260 (100 shares × index points). Stocks-only Jun is +₹3,157, and stocks-only V4 cumulative to Jun is -₹3,001 (Jan +₹599, Feb -₹600, Mar +₹2,084, Apr -₹1,136, May -₹7,105, Jun +₹3,157). So the Jun total spike is NOT a stocks progression; stocks-only V4 cumulative is still negative at Jun.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-06.json, same capped rules. Results gate NEUTRAL (0), same look-ahead reason.

## Cumulative progression (capped, to Mar 2025)
| Series | Jan | Feb | Mar | Trades to Mar | Win to Mar |
|---|---|---|---|---|---|
| Capped-V4 | +₹599 | -₹1 (FALL) | +₹2,083 | 42 | 40.5% (17 targets) |
| Capped-Skill | -₹275 | +₹1,769 | +₹7,576 | 41 | 48.8% (20 targets) |
| Unified | +₹599 | -₹1 (FALL) | +₹2,083 | 42 | 40.5% |

## X verdict to Mar 2025
- Frequency: PASS for capped series — 3.0/week or less, 12-15 trades/month portfolio total, NOT 500+.
- Net progression: Skill capped progresses Feb->Mar (and recovers Jan loss). V4/unified do NOT progress monotonically — Feb cumulative falls.
- Win rate: Skill capped 48.8% to Mar, V4 40.5% to Mar, on only 41-42 trades — small sample, not proof.
- NO V5 / skill v2 adoption yet on this capped series alone: the series is 3 months, the room fix touched Jan, and the results gate is neutral here. Adoption requires progression on validation (unseen months), not just Jan-Mar.
- Next fix to test (V5 candidate, not adopted): Feb V4 dip — test whether tightening V4 room (e.g. room ratio >= 1.5 instead of >= 1.0) or bias-strong-only selection avoids Feb-type months, validated on Apr-Jun, not on Feb itself.

## Cumulative progression (capped, to Jun 2025)
| Series | Jan | Feb | Mar | Apr | May | Jun | Trades to Jun | Win to Jun |
|---|---|---|---|---|---|---|---|---|
| Capped-V4 | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 (below Mar peak) | +₹27,379 (index-driven, see Jun flag) | 87 | 36.8% (32 targets) |
| Capped-Skill | -₹275 | +₹1,769 | +₹7,576 | +₹6,326 (FALL) | +₹3,313 (FALL) | +₹3,918 (below Mar peak) | 86 | 38.4% (33 targets) |
| Unified | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 (below Mar peak) | +₹27,379 (index-driven) | 87 | 36.8% |
Stocks-only cumulative to Jun: V4 -₹3,001, Skill +₹3,918 (skill capped is stocks-only in all months to Jun). V4 total progression to Jun is NOT stocks progression.

## X verdict to Jun 2025 (updated from Mar)
- Frequency: PASS for capped series — 3.0/week, 12-15 trades/month portfolio total, NOT 500+.
- Net progression: NOT monotonic for any series. Skill capped falls Apr, May, and remains below its Mar peak at Jun. V4/unified fall Feb and Apr, stay below Mar peak in May, and Jun's rise is a single Nifty index trade, not stocks.
- Win rate to Jun: Skill capped 38.4% on 86 trades, V4 36.8% on 87 trades — small sample, not proof.
- NO V5 / skill v2 adoption yet on this capped series: progression on validation (unseen months) is not met, and the May/Jun index spikes must not be mistaken for a stocks edge. A V5 candidate must progress on stocks-only net as well as total, or it is not a progression.

### 2025-07 — DONE, 23 days, 5 ISO weeks
- Raw candidates: V4 134, skill OR 516, skill after bias+room+PD filter 125.
- Capped-V4: 15 trades, 5 targets, 10 stops, 0 square-offs, win 33.3%, net -₹1,321, expectancy -₹88.07, max DD ₹2,541, 3.0/week. Split: indices ₹0, stocks -₹1,321.
- Capped-Skill: 15 trades, 5 targets, 9 stops, 1 square-off, win 33.3%, net -₹531, expectancy -₹35.40, max DD ₹2,565, 3.0/week. Split: indices ₹0, stocks -₹531.
- Unified capped: 15 trades, same as capped-V4 (-₹1,321) — V4 outranks skill every week.
- Cumulative: V4 +₹26,058 (₹27,379-₹1,321) — FALLS in Jul, flagged as failure to fix. Skill +₹3,387 (₹3,918-₹531) — FALLS in Jul, flagged, still below Mar peak ₹7,576. Unified +₹26,058 — falls, same as V4.
- Stocks-only cumulative to Jul: V4 -₹4,322 (-₹3,001-₹1,321), Skill +₹3,387 (skill capped is stocks-only in all months to Jul). Jul total is NOT index-driven — no index trade made the cap in Jul, so the Jul fall is a genuine stocks fall, not a point-scale artefact. Best/worst capped-V4 Jul: best TVSMOTOR 2025-07-31 setup4 target +₹1,220, ASTRAL +₹660, OIL +₹370; worst BDL 2025-07-03 setup4 stop -₹940, BDL 2025-07-28 stop -₹750, TVSMOTOR 2025-07-09 stop -₹710. Note: skill capped best/worst overlap V4 on the same symbol+date targets (OIL/ASTRAL/TVSMOTOR) — same signal days, different entry logic.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-07.json, same capped engine/rules. Results gate NEUTRAL (0) for Jul 2025 — v1 patterns are Sep 2025-Jun 2026 quarters, still partly in the future relative to Jul 2025, and no pattern quarter is complete for Jul; do not apply the gate here as if it were known at signal time.

### 2025-08 — DONE, 19 days, 5 ISO weeks
- Raw candidates: V4 116, skill OR 425, skill after bias+room+PD filter 147.
- Capped-V4: 15 trades, 2 targets, 13 stops, 0 square-offs, win 13.3%, net -₹11,682, expectancy -₹778.80, max DD ₹11,682, 3.0/week. Split: indices -₹8,000, stocks -₹3,682.
- Capped-Skill: 15 trades, 3 targets, 9 stops, 3 square-offs, win 20.0%, net -₹391, expectancy -₹26.07, max DD ₹3,700, 3.0/week. Split: indices -₹3,265, stocks +₹2,874.
- Unified capped: 15 trades, same as capped-V4 (-₹11,682).
- Cumulative: V4 +₹14,376 (₹26,058-₹11,682) — FALLS sharply in Aug, flagged. Skill +₹2,996 (₹3,387-₹391) — FALLS in Aug, flagged, still below Mar peak ₹7,576. Unified +₹14,376 — falls, same as V4.
- Stocks-only cumulative to Aug: V4 -₹8,004 (-₹4,322-₹3,682), Skill +₹6,261 (₹3,387+₹2,874). Skill stocks-only rises in Aug even though its total falls, because its Aug index leg is -₹3,265 — split reporting matters here.
- FRAGILITY FLAG, Aug V4: ₹8,000 of the -₹11,682 is two index stops on a single day, 2025-08-01 — BANKNIFTY setup4 stop -₹5,690 and NIFTY setup4 stop -₹2,310. That is point-scaled index cash-equivalent loss, not stocks loss, and it dominates the month. V4 Aug has only 2 targets in 15 trades, and its best capped trade is only +₹370 (KALYANKJIL 2025-08-11 setup3 target); one capped-V4 'target' (NHPC 2025-08-11) nets -₹26 after the ₹40 cost, i.e. a target that still loses money — target distance was smaller than cost. This month is a V4 failure month on win rate, stocks net, and total net alike.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-08.json, same capped engine/rules. Results gate NEUTRAL (0) for Aug 2025, same look-ahead reason as Jul.

### 2025-09 — DONE, 22 days, 5 ISO weeks
- Raw candidates: V4 103, skill OR 415, skill after bias+room+PD filter 77.
- Capped-V4: 15 trades, 3 targets, 11 stops, 1 square-off, win 20.0%, net -₹1,320, expectancy -₹88.00, max DD ₹1,420, 3.0/week. Split: indices ₹0, stocks -₹1,320.
- Capped-Skill: 12 trades, 6 targets, 6 stops, 0 square-offs, win 50.0%, net +₹2,766, expectancy +₹230.50, max DD ₹340, 2.4/week (one week had <3 eligible after per-symbol cap). Split: indices ₹0, stocks +₹2,766.
- Unified capped: 15 trades, same as capped-V4 (-₹1,320).
- Cumulative: V4 +₹13,056 (₹14,376-₹1,320) — FALLS in Sep, flagged, third consecutive falling month (Jul, Aug, Sep). Skill +₹5,762 total (₹2,996+₹2,766) — RISES in Sep total, but still below Mar peak ₹7,576, so progression is not restored. Unified +₹13,056 — falls, same as V4.
- Stocks-only cumulative to Sep: V4 -₹9,324 (-₹8,004-₹1,320), Skill +₹9,027 (₹6,261+₹2,766). This is the key split in Sep: skill capped is the ONLY series whose stocks-only cumulative is positive at Sep, and it rose in Sep on stocks alone (no index trade). V4 stocks-only falls again in Sep. V4 total to Sep (+₹13,056) is still entirely index-driven (Jun Nifty +₹22,260 and May Bank Nifty net, minus Aug index stops) — without indices, V4 cumulative is deeply negative.
- Best/worst Sep: V4 best GODREJCP 2025-09-15 setup4 target +₹260, KALYANKJIL +₹160, HINDCOPPER +₹142 — no large winner, all targets small; worst OBEROIRLTY 2025-09-22 setup4 stop -₹480, TVSMOTOR -₹470, HINDZINC -₹180. Skill best GODREJCP 2025-09-01 OR target +₹1,280, TVSMOTOR +₹1,140, HINDCOPPER +₹678; worst OBEROIRLTY -₹340, INDUSTOWER -₹175, WIPRO -₹127.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-09.json, same capped engine/rules. Results gate NEUTRAL (0) for Sep 2025 — the v1 pattern quarters run Sep 2025-Jun 2026, so Sep 2025 is the first pattern quarter itself, not a quarter known in advance at signal time; applying its own-quarter pattern would be look-ahead.

### 2025-10 — DONE, 21 days, 5 ISO weeks
- Fresh Upstox fetch first (cache previously ended 2025-09-30): Oct 2025 fetched for all 27 instruments, 21 trading days each, no fabrication. Upstox tested first: Bank Nifty search succeeds, no 401. Note: ASTRAL/BDL/OIL/HINDUNILVR caches total 187 days vs 209 for the rest — a pre-existing early-2025 gap for those four, not an Oct gap; Oct itself is complete (21/21) for all 27.
- Raw candidates: V4 112, skill OR 454, skill after bias+room+PD filter 80.
- Capped-V4: 15 trades, 2 targets, 10 stops, 3 square-offs, win 13.3%, net -₹1,941, expectancy -₹129.40, max DD ₹1,941, 3.0/week. Split: indices ₹0, stocks -₹1,941.
- Capped-Skill: 15 trades, 2 targets, 11 stops, 2 square-offs, win 13.3%, net -₹3,110, expectancy -₹207.33, max DD ₹3,288, 3.0/week. Split: indices ₹0, stocks -₹3,110.
- Unified capped: 15 trades, same as capped-V4 (-₹1,941).
- Cumulative: V4 +₹11,115 (₹13,056-₹1,941) — FALLS in Oct, flagged, fourth consecutive falling month (Jul, Aug, Sep, Oct). Skill +₹2,652 total (₹5,762-₹3,110) — FALLS in Oct, flagged, still below Mar peak ₹7,576. Unified +₹11,115 — falls, same as V4.
- Stocks-only cumulative to Oct: V4 -₹11,265 (-₹9,324-₹1,941), Skill +₹5,917 (₹9,027-₹3,110). Skill stocks-only stays positive but falls in Oct; V4 stocks-only falls again. Oct is NOT index-driven — no index trade made either cap, so this is a genuine stocks fall for both series.
- Best/worst Oct: V4 best IRCTC 2025-10-15 setup4 target +₹290, INDUSTOWER +₹90, VEDL +₹90; worst BDL 2025-10-29 setup4 stop -₹720, HINDUNILVR 2025-10-31 -₹560, KALYANKJIL 2025-10-01 -₹305. Skill best OBEROIRLTY 2025-10-15 OR target +₹560, HINDZINC +₹490; worst GLENMARK 2025-10-28 OR stop -₹1,240, GODREJCP 2025-10-23 -₹820.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-10.json, same capped engine/rules. Results gate NEUTRAL (0) for Oct 2025 — v1 patterns are derived from Sep 2025–Jun 2026 quarters and were not knowable at Oct 2025 signal time; applying them in Oct would be look-ahead.

### 2025-11 — DONE, 19 days, 4 ISO weeks
- Fresh Upstox fetch: Nov 2025 fetched for all 27 instruments, 19 trading days each, no fabrication.
- Raw candidates: V4 111, skill OR 420, skill after bias+room+PD filter 115.
- Capped-V4: 12 trades, 3 targets, 6 stops, 3 square-offs, win 25.0%, net -₹3,406, expectancy -₹283.83, max DD ₹3,932, 3.0/week. Split: indices ₹0, stocks -₹3,406.
- Capped-Skill: 12 trades, 3 targets, 6 stops, 3 square-offs, win 25.0%, net -₹1,218, expectancy -₹101.50, max DD ₹2,758, 3.0/week. Split: indices ₹0, stocks -₹1,218.
- Unified capped: 12 trades, same as capped-V4 (-₹3,406).
- Cumulative: V4 +₹7,709 (₹11,115-₹3,406) — FALLS in Nov, flagged, fifth consecutive falling month (Jul–Nov). Skill +₹1,434 total (₹2,652-₹1,218) — FALLS in Nov, flagged, still below Mar peak ₹7,576. Unified +₹7,709 — falls, same as V4.
- Stocks-only cumulative to Nov: V4 -₹14,671 (-₹11,265-₹3,406), Skill +₹4,699 (₹5,917-₹1,218). Nov is NOT index-driven — no index trade made either cap, so this is a genuine stocks fall for both series.
- Best/worst Nov: V4 best INDUSTOWER 2025-11-07 setup4 target +₹310, NATIONALUM +₹216; worst GLENMARK 2025-11-17 setup4 stop -₹2,050 (single largest capped loss in Oct–Nov), TVSMOTOR 2025-11-07 -₹930. Skill best OBEROIRLTY 2025-11-26 OR target +₹1,760, ASTRAL +₹740; worst GLENMARK 2025-11-14 OR stop -₹1,060, GLENMARK 2025-11-17 -₹680.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-11.json, same capped engine/rules. Results gate NEUTRAL (0) for Nov 2025, same look-ahead reason as Oct (v1 patterns derived from Sep 2025–Jun 2026 quarters, not knowable at signal time).

### 2025-12 — DONE, 22 days, 5 ISO weeks
- Fresh Upstox fetch: Dec 2025 fetched for all 27 instruments, 22 trading days each, no fabrication.
- Raw candidates: V4 119, skill OR 492, skill after bias+room+PD filter 116.
- Capped-V4: 15 trades, 4 targets, 9 stops, 2 square-offs, win 26.7%, net +₹652, expectancy +₹43.47, max DD ₹1,348, 3.0/week. Split: indices ₹0, stocks +₹652.
- Capped-Skill: 15 trades, 5 targets, 9 stops, 1 square-off, win 33.3%, net -₹1,107, expectancy -₹73.80, max DD ₹3,195, 3.0/week. Split: indices ₹0, stocks -₹1,107.
- Unified capped: 15 trades, same as capped-V4 (+₹652).
- Cumulative: V4 +₹8,361 (₹7,709+₹652) — RISES in Dec, breaking the Jul–Nov falling streak, but still well below the Sep peak ₹13,056, so progression is not restored. Skill +₹327 total (₹1,434-₹1,107) — FALLS in Dec, flagged, still below Mar peak ₹7,576. Unified +₹8,361 — rises, same as V4.
- Stocks-only cumulative to Dec: V4 -₹14,019 (-₹14,671+₹652), Skill +₹3,592 (₹4,699-₹1,107). Dec is NOT index-driven — no index trade made either cap, so V4's Dec rise is a genuine (small) stocks rise, and Skill's Dec fall is a genuine stocks fall.
- Best/worst Dec: V4 best HINDUNILVR 2025-12-04 setup4 target +₹1,260, GODREJCP 2025-12-09 +₹600, OBEROIRLTY +₹370; worst TVSMOTOR 2025-12-19 setup4 stop -₹650, HINDZINC -₹330. Skill best HINDUNILVR 2025-12-04 OR target +₹1,260 (same signal day as V4), GODREJCP +₹600; worst GLENMARK 2025-12-02 OR stop -₹670, TVSMOTOR -₹650.
- Source: ~/workspace/trading/data/progressive/capped_summary_2025-12.json, same capped engine/rules. Results gate NEUTRAL (0) for Dec 2025, same look-ahead reason as Oct–Nov.

### 2026-01 — DONE, 20 days, 5 ISO weeks
- Fresh Upstox fetch: Jan 2026 fetched for all 27 instruments, 20 trading days each (269 cumulative days; ASTRAL/BDL/OIL/HINDUNILVR 247 — pre-existing early-2025 gap, not a Jan gap), no fabrication. Upstox tested first: Bank Nifty search succeeds, no 401.
- Raw candidates: V4 100, skill OR 452, skill after bias+room+PD filter 106.
- Capped-V4: 15 trades, 1 target, 13 stops, 1 square-off, win 6.7%, net -₹5,155, expectancy -₹343.67, max DD ₹5,330, 3.0/week. Split: indices -₹2,785, stocks -₹2,370.
- Capped-Skill: 15 trades, 1 target, 13 stops, 1 square-off, win 6.7%, net -₹5,180, expectancy -₹345.33, max DD ₹5,835, 3.0/week. Split: indices -₹2,785, stocks -₹2,395.
- Unified capped: 15 trades, same as capped-V4 (-₹5,155).
- Cumulative: V4 +₹3,206 (₹8,361-₹5,155) — FALLS sharply in Jan, flagged, worst capped month on win rate so far. Skill -₹4,853 total (₹327-₹5,180) — FALLS in Jan, flagged, turns cumulatively negative for the first time. Unified +₹3,206 — falls, same as V4.
- Stocks-only cumulative to Jan: V4 -₹16,389 (-₹14,019-₹2,370), Skill +₹1,197 (₹3,592-₹2,395). Skill stocks-only stays positive but falls sharply; V4 stocks-only falls again.
- Jan is partly index-driven: the single NIFTY setup4_reclaim CE stop on 2026-01-14 is -₹2,785 in both series (point-scaled index loss). Even without it, both series are still negative on stocks alone (-₹2,370 / -₹2,395). Best/worst Jan: V4 best HDFCBANK 2026-01-27 square-off +₹915, only target HINDCOPPER +₹160; worst NIFTY -₹2,785, GODREJCP -₹790. Skill best HDFCBANK +₹915 (same day as V4), INDUSTOWER 2026-01-01 target +₹840; worst NIFTY -₹2,785, GODREJCP -₹790.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-01.json, same capped engine/rules. Results gate NEUTRAL (0) for Jan 2026 — v1 patterns are derived from Sep 2025-Jun 2026 quarters, not knowable in full at Jan 2026 signal time; applying them in Jan would be look-ahead.

### 2026-02 — DONE, 21 days, 5 ISO weeks
- Fresh Upstox fetch: Feb 2026 fetched for all 27 instruments, 21 trading days each (290 cumulative days), no fabrication.
- Raw candidates: V4 93, skill OR 447, skill after bias+room+PD filter 103.
- Capped-V4: 15 trades, 7 targets, 8 stops, 0 square-offs, win 46.7%, net -₹320, expectancy -₹21.33, max DD ₹875, 3.0/week. Split: indices ₹0, stocks -₹320.
- Capped-Skill: 15 trades, 5 targets, 10 stops, 0 square-offs, win 33.3%, net -₹12,111, expectancy -₹807.40, max DD ₹12,956, 3.0/week. Split: indices -₹7,080, stocks -₹5,031.
- Unified capped: 15 trades, same as capped-V4 (-₹320).
- Cumulative: V4 +₹2,886 (₹3,206-₹320) — FALLS slightly in Feb, flagged (win rate recovered to 46.7% but targets are small). Skill -₹16,964 total (-₹4,853-₹12,111) — FALLS sharply in Feb, flagged. Unified +₹2,886 — falls, same as V4.
- Stocks-only cumulative to Feb: V4 -₹16,709 (-₹16,389-₹320), Skill -₹3,834 (₹1,197-₹5,031, turns negative). Skill stocks-only falls in Feb on its own, before the index leg.
- FRAGILITY FLAG, Feb Skill: ₹7,080 of the -₹12,111 is a single BANKNIFTY OR breakdown PE stop on 2026-02-11 (point-scaled index loss), plus two TVSMOTOR CE stops (-₹2,790 on 2026-02-02 and -₹1,700 on 2026-02-01, different ISO weeks so both pass the per-symbol/week cap). Feb Skill is therefore index-dominated in total, but its stocks leg (-₹5,031) is itself a genuine stocks failure month. Best/worst Feb: V4 best TVSMOTOR 2026-02-13 target +₹1,020, OBEROIRLTY stop -₹800 worst; Skill best GLENMARK +₹1,340, worst BANKNIFTY -₹7,080. Note two "targets" net negative after the ₹40 cost (NHPC -₹20 in both series, -₹6 in Skill) — target distance smaller than cost.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-02.json, same capped engine/rules. Results gate NEUTRAL (0) for Feb 2026, same look-ahead reason as Jan (v1 patterns derived from Sep 2025-Jun 2026 quarters, not knowable in full at Feb 2026 signal time).

### 2026-03 — DONE, 19 days, 5 ISO weeks
- Fresh Upstox fetch: Mar 2026 fetched for all 27 instruments, 19 trading days each (309 cumulative days), no fabrication.
- Raw candidates: V4 81, skill OR 418, skill after bias+room+PD filter 118.
- Capped-V4: 14 trades, 3 targets, 10 stops, 1 square-off, win 21.4%, net -₹2,479, expectancy -₹177.07, max DD ₹3,089, 2.8/week (one week had <3 eligible). Split: indices -₹2,055, stocks -₹424.
- Capped-Skill: 15 trades, 2 targets, 13 stops, 0 square-offs, win 13.3%, net -₹14,724, expectancy -₹981.60, max DD ₹15,434, 3.0/week. Split: indices -₹10,520, stocks -₹4,204.
- Unified capped: 15 trades, 3 targets, 11 stops, 1 square-off, win 20.0%, net -₹2,854, expectancy -₹190.27, max DD ₹3,464, 3.0/week. Split: indices -₹2,055, stocks -₹799. First month unified differs from capped-V4 (it mixes in skill picks after dedup by symbol+date).
- Cumulative: V4 +₹407 (₹2,886-₹2,479) — FALLS in Mar, flagged, now barely positive in total. Skill -₹31,688 total (-₹16,964-₹14,724) — FALLS sharply in Mar, flagged. Unified +₹32 (₹2,886-₹2,854) — FALLS in Mar, flagged, barely positive.
- Stocks-only cumulative to Mar: V4 -₹17,133 (-₹16,709-₹424), Skill -₹8,038 (-₹3,834-₹4,204), Unified -₹17,508 (-₹16,709-₹799).
- FRAGILITY FLAG, Mar Skill: ₹10,520 of the -₹14,724 is a single BANKNIFTY OR breakdown PE stop on 2026-03-30 (point-scaled index loss, the largest single capped loss in the whole Jan 2025-Mar 2026 series). Even without it, Skill stocks leg (-₹4,204) is a genuine stocks failure month, and V4's NIFTY breakdown stop (-₹2,055, 2026-03-30) similarly dominates its month total while its stocks leg (-₹424) is only mildly negative. Best/worst Mar: V4 best HINDALCO +₹610, worst NIFTY -₹2,055; Skill best ASTRAL PE target +₹760, worst BANKNIFTY -₹10,520.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-03.json, same capped engine/rules. Results gate NEUTRAL (0) for Mar 2026, same look-ahead reason as Jan-Feb (v1 patterns derived from Sep 2025-Jun 2026 quarters, not knowable in full at Mar 2026 signal time).

### 2026-04 — DONE, 20 days, 5 ISO weeks
- Fresh Upstox fetch: Apr 2026 fetched for all 27 instruments, 20 trading days each (329 cumulative days), no fabrication.
- Raw candidates: V4 105, skill OR 393, skill after bias+room+PD filter 96.
- Capped-V4: 15 trades, 3 targets, 11 stops, 1 square-off, win 20.0%, net -₹3,620, expectancy -₹241.33, max DD ₹3,620, 3.0/week. Split: indices ₹0, stocks -₹3,620.
- Capped-Skill: 15 trades, 3 targets, 12 stops, 0 square-offs, win 20.0%, net -₹10,787, expectancy -₹719.13, max DD ₹10,787, 3.0/week. Split: indices -₹7,180, stocks -₹3,607.
- Unified capped: 15 trades, same as capped-V4 (-₹3,620).
- Cumulative: V4 -₹3,213 (₹407-₹3,620) — FALLS in Apr, flagged, turns cumulatively negative in total for the first time. Skill -₹42,475 total (-₹31,688-₹10,787) — FALLS sharply in Apr, flagged. Unified -₹3,213 — falls, same as V4.
- Stocks-only cumulative to Apr: V4 -₹20,753 (-₹17,133-₹3,620), Skill -₹11,645 (-₹8,038-₹3,607), Unified -₹21,128 (-₹17,508-₹3,620).
- FRAGILITY FLAG, Apr Skill: ₹7,180 of the -₹10,787 is a single BANKNIFTY OR breakout CE stop on 2026-04-28 (point-scaled index loss). Even without it, Skill stocks leg (-₹3,607) is itself a genuine stocks failure month, almost identical to V4's all-stocks -₹3,620. Best/worst Apr: V4 best VEDL 2026-04-02 target +₹450, NTPC +₹380; worst HINDUNILVR 2026-04-23 stop -₹1,450, OBEROIRLTY -₹750. Skill best VEDL 2026-04-27 target +₹880, RECLTD +₹260; worst BANKNIFTY -₹7,180, HINDUNILVR -₹1,450 (same day as V4).
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-04.json, same capped engine/rules. Results gate NEUTRAL (0) for Apr 2026 — v1 patterns are derived from Sep 2025-Jun 2026 quarters, not knowable in full at Apr 2026 signal time; applying them in Apr would be look-ahead.

### 2026-05 — DONE, 19 days, 4 ISO weeks
- Fresh Upstox fetch: May 2026 fetched for all 27 instruments, 19 trading days each (348 cumulative days), no fabrication.
- Raw candidates: V4 91, skill OR 398, skill after bias+room+PD filter 97.
- Capped-V4: 12 trades, 1 target, 11 stops, 0 square-offs, win 8.3%, net -₹2,198, expectancy -₹183.17, max DD ₹2,978, 3.0/week. Split: indices ₹0, stocks -₹2,198.
- Capped-Skill: 12 trades, 4 targets, 8 stops, 0 square-offs, win 33.3%, net +₹3,160, expectancy +₹263.33, max DD ₹1,030, 3.0/week. Split: indices ₹0, stocks +₹3,160.
- Unified capped: 12 trades, same as capped-V4 (-₹2,198).
- Cumulative: V4 -₹5,411 (-₹3,213-₹2,198) — FALLS in May, flagged, second consecutive falling month. Skill -₹39,315 total (-₹42,475+₹3,160) — RISES in May, but remains deeply negative and far below any earlier peak, so progression is not restored. Unified -₹5,411 — falls, same as V4.
- Stocks-only cumulative to May: V4 -₹22,951 (-₹20,753-₹2,198), Skill -₹8,485 (-₹11,645+₹3,160), Unified -₹23,326 (-₹21,128-₹2,198). May is entirely stocks — no index trade made either cap, so this is a genuine stocks month, not a point-scale artefact.
- FRAGILITY FLAG, May Skill: the +₹3,160 rise is a single TVSMOTOR OR breakout CE target on 2026-05-20, +₹3,860. Without it, May Skill is -₹700. Best/worst May: V4 best TVSMOTOR 2026-05-05 target +₹780 (its only target), worst ASTRAL 2026-05-08 stop -₹860; Skill best TVSMOTOR +₹3,860, INDUSTOWER +₹470, worst ASTRAL -₹860 (same day as V4).
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-05.json, same capped engine/rules. Results gate NEUTRAL (0) for May 2026 — v1 patterns are derived from Sep 2025-Jun 2026 quarters, not knowable in full at May 2026 signal time; applying them in May would be look-ahead.

### 2026-06 — DONE, 21 days, 5 ISO weeks
- Fresh Upstox fetch: Jun 2026 fetched for all 27 instruments, 21 trading days each (369 cumulative days), no fabrication.
- Raw candidates: V4 104, skill OR 448, skill after bias+room+PD filter 111.
- Capped-V4: 15 trades, 3 targets, 10 stops, 2 square-offs, win 20.0%, net -₹2,850, expectancy -₹190.00, max DD ₹2,850, 3.0/week. Split: indices ₹0, stocks -₹2,850.
- Capped-Skill: 15 trades, 6 targets, 9 stops, 0 square-offs, win 40.0%, net -₹18,958, expectancy -₹1,263.87, max DD ₹18,958, 3.0/week. Split: indices -₹15,645, stocks -₹3,313.
- Unified capped: 15 trades, same as capped-V4 (-₹2,850).
- Cumulative: V4 -₹8,261 (-₹5,411-₹2,850) — FALLS in Jun, flagged, third consecutive falling month. Skill -₹58,273 total (-₹39,315-₹18,958) — FALLS sharply in Jun, flagged, erasing the May rise. Unified -₹8,261 — falls, same as V4.
- Stocks-only cumulative to Jun: V4 -₹25,801 (-₹22,951-₹2,850), Skill -₹11,798 (-₹8,485-₹3,313), Unified -₹26,176 (-₹23,326-₹2,850).
- FRAGILITY FLAG, Jun Skill: ₹15,645 of the -₹18,958 is a single BANKNIFTY OR breakdown PE stop on 2026-06-29 (point-scaled index loss, the largest single capped loss in the whole Jan 2025-Jun 2026 series, above Mar 2026's -₹10,520). Even without it, Skill stocks leg (-₹3,313) is a genuine stocks failure month, and its 40.0% win rate did not save the month because the targets are small. Best/worst Jun: V4 best VEDL 2026-06-11 pullback +₹300, NATIONALUM +₹270; worst OBEROIRLTY 2026-06-29 stop -₹720, BDL -₹480. Skill best VEDL +₹300, NATIONALUM +₹270 (same days as V4); worst BANKNIFTY -₹15,645, GLENMARK -₹1,440.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-06.json, same capped engine/rules. Results gate NEUTRAL (0) for Jun 2026 — v1 patterns are derived from Sep 2025-Jun 2026 quarters, not knowable in full at Jun 2026 signal time (Jun is the last pattern quarter itself); applying them in Jun would be look-ahead.

### 2026-07 — DONE, 23 days, 5 ISO weeks
- Fresh Upstox fetch: Jul 2026 fetched for all 27 instruments, 23 trading days each (392 cumulative days), no fabrication. Upstox tested first: Bank Nifty search succeeds, no 401.
- Raw candidates: V4 120, skill OR 481, skill after bias+room+PD filter 112.
- Capped-V4: 15 trades, 4 targets, 11 stops, 0 square-offs, win 26.7%, net +₹12,859, expectancy +₹857.27, max DD ₹2,821, 3.0/week. Split: indices +₹15,680, stocks -₹2,821.
- Capped-Skill: 15 trades, 6 targets, 7 stops, 2 square-offs, win 40.0%, net +₹27,895, expectancy +₹1,859.67, max DD ₹2,130, 3.0/week. Split: indices +₹28,850, stocks -₹955.
- Unified capped: 15 trades, same as capped-V4 (+₹12,859).
- Cumulative: V4 +₹4,598 (-₹8,261+₹12,859) — RISES in Jul, breaking the Apr–Jun falling streak, but still below the Jun 2025 total peak and entirely index-driven. Skill -₹30,378 total (-₹58,273+₹27,895) — RISES in Jul, still deeply negative. Unified +₹4,598 — rises, same as V4.
- Stocks-only cumulative to Jul: V4 -₹28,622 (-₹25,801-₹2,821), Skill -₹12,753 (-₹11,798-₹955), Unified -₹28,997 (-₹26,176-₹2,821). Jul is a stocks FAILURE month for all series despite the positive totals.
- FRAGILITY FLAG, Jul: V4's +₹12,859 is a single BANKNIFTY setup4_reclaim CE target on 2026-07-01, +₹15,680 — without it, V4 Jul is -₹2,821. Skill's +₹27,895 is a single BANKNIFTY OR breakout CE target on 2026-07-13, +₹24,610, plus a NIFTY OR target +₹4,240 on 2026-07-01 — without the two index trades, Skill Jul is -₹955. Both Jul totals are point-scaled index cash-equivalents and must not be read as portfolio rupees or as stocks progression. Best/worst Jul: V4 best BANKNIFTY +₹15,680, GLENMARK +₹740; worst TVSMOTOR 2026-07-13 stop -₹1,350, UNITDSPR -₹800. Skill best BANKNIFTY +₹24,610, NIFTY +₹4,240; worst GLENMARK 2026-07-10 stop -₹1,230, UNITDSPR -₹800. One V4 "target" (WIPRO 2026-07-08) nets -₹24 after the ₹40 cost — a target smaller than cost.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-07.json, same capped engine/rules. Results gate NEUTRAL (0) for Jul 2026 — v1 patterns are derived from Sep 2025–Jun 2026 quarters, now fully in the past at Jul 2026 signal time, but no gate rule was adopted from them in this series, so the gate stays neutral rather than being applied retroactively without a validated rule.

### 2026-08 — DONE, 21 days, 5 ISO weeks
- Fresh Upstox fetch: Aug 2026 fetched for all 27 instruments, 21 trading days each (413 cumulative days), no fabrication.
- Raw candidates: V4 110, skill OR 454, skill after bias+room+PD filter 128.
- Capped-V4: 15 trades, 1 target, 13 stops, 1 square-off, win 6.7%, net -₹9,286, expectancy -₹619.07, max DD ₹10,756, 3.0/week. Split: indices -₹7,455, stocks -₹1,831.
- Capped-Skill: 15 trades, 2 targets, 11 stops, 2 square-offs, win 13.3%, net -₹23,341, expectancy -₹1,556.07, max DD ₹25,391, 3.0/week. Split: indices -₹21,825, stocks -₹1,516.
- Unified capped: 15 trades, same as capped-V4 (-₹9,286).
- Cumulative: V4 -₹4,688 (+₹4,598-₹9,286) — FALLS in Aug, erasing the Jul total rise. Skill -₹53,719 total (-₹30,378-₹23,341) — FALLS sharply in Aug. Unified -₹4,688 — falls, same as V4.
- Stocks-only cumulative to Aug: V4 -₹30,453 (-₹28,622-₹1,831), Skill -₹14,269 (-₹12,753-₹1,516), Unified -₹30,828 (-₹28,997-₹1,831). Aug is a failure month on total and on stocks-only alike.
- FRAGILITY FLAG, Aug: V4's loss is dominated by a single BANKNIFTY setup4_reclaim CE stop on 2026-08-25, -₹7,455 (point-scaled index loss); without it V4 Aug is still -₹1,831 on stocks. Skill's loss is dominated by two BANKNIFTY stops: OR breakdown PE -₹14,370 on 2026-08-10 and OR breakout CE -₹7,455 on 2026-08-25, totalling -₹21,825 of -₹23,341; without them Skill Aug is still -₹1,516 on stocks. Best/worst Aug: V4 best TVSMOTOR 2026-08-31 square-off +₹1,470, HINDCOPPER +₹330 (its only target); worst BANKNIFTY -₹7,455, OBEROIRLTY -₹820. Skill best TVSMOTOR +₹1,470 (same day as V4), BDL +₹780; worst BANKNIFTY -₹14,370, BANKNIFTY -₹7,455.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-08.json, same capped engine/rules. Results gate NEUTRAL (0) for Aug 2026, same reason as Jul (no gate rule adopted from the v1 patterns in this series).

### 2026-09 — DONE, 21 days, 5 ISO weeks
- Fresh Upstox fetch: Sep 2026 fetched for all 27 instruments, 21 trading days each (434 cumulative days), no fabrication.
- Raw candidates: V4 119, skill OR 455, skill after bias+room+PD filter 133.
- Capped-V4: 15 trades, 5 targets, 10 stops, 0 square-offs, win 33.3%, net +₹2,460, expectancy +₹164.00, max DD ₹1,916, 3.0/week. Split: indices ₹0, stocks +₹2,460.
- Capped-Skill: 15 trades, 2 targets, 13 stops, 0 square-offs, win 13.3%, net -₹7,460, expectancy -₹497.33, max DD ₹10,780, 3.0/week. Split: indices -₹8,910, stocks +₹1,450.
- Unified capped: 15 trades, same as capped-V4 (+₹2,460).
- Cumulative: V4 -₹2,228 total (-₹4,688+₹2,460) — RISES in Sep, but still negative in total. Skill -₹61,179 total (-₹53,719-₹7,460) — FALLS in Sep. Unified -₹2,228 — rises, same as V4.
- Stocks-only cumulative to Sep: V4 -₹27,993 (-₹30,453+₹2,460) — RISES on stocks alone, the first genuine stocks rise since Jun 2026, but still deeply negative. Skill -₹12,819 (-₹14,269+₹1,450) — RISES on stocks alone in Sep, but its total falls. Unified -₹28,368 (-₹30,828+₹2,460) — rises on stocks alone.
- FRAGILITY FLAG, Sep Skill: its total loss is a single BANKNIFTY OR breakout CE stop on 2026-09-01, -₹8,910 (point-scaled index loss); without it Skill Sep is +₹1,450 on stocks. V4 Sep is NOT index-driven — no index trade made the V4 cap, so its +₹2,460 is a genuine stocks rise. Best/worst Sep: V4 best TVSMOTOR 2026-09-29 target +₹3,560, GLENMARK +₹1,260; worst OBEROIRLTY 2026-09-24 stop -₹980, GLENMARK -₹430. Skill best TVSMOTOR +₹3,560 (same day as V4), GLENMARK +₹1,260 (same day); worst BANKNIFTY -₹8,910, OBEROIRLTY -₹980.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-09.json, same capped engine/rules. Results gate NEUTRAL (0) for Sep 2026, same reason as Jul–Aug (no gate rule adopted from the v1 patterns in this series).

## Cumulative progression (capped, to Sep 2026)
| Series | Aug 2026 | Sep 2026 | Trades to Sep 2026 | Win to Sep 2026 |
|---|---|---|---|---|
| Capped-V4 total | -₹4,688 | -₹2,228 (rises, still negative) | 305 | 25.9% (79 targets) |
| Capped-V4 stocks-only | -₹30,453 | -₹27,993 (rises) | 305 | — |
| Capped-Skill total | -₹53,719 | -₹61,179 (FALL) | 301 | 29.2% (88 targets) |
| Capped-Skill stocks-only | -₹14,269 | -₹12,819 (rises) | 301 | — |
| Unified total | -₹4,688 | -₹2,228 (rises, still negative) | 306 | 25.8% (79 targets) |
| Unified stocks-only | -₹30,828 | -₹28,368 (rises) | 306 | — |

## X verdict to Sep 2026
- Frequency: PASS — 3.0/week, 15 trades/month portfolio total, NOT 500+. This is the only X leg that passes consistently.
- Net progression: MIXED in Sep 2026, not a validated progression. V4/Unified rise on total and on stocks-only (+₹2,460, all stocks, no index trade) — a genuine stocks rise, but one month after a long falling run, and cumulative totals are still negative (-₹2,228) and stocks-only deeply negative (-₹27,993 / -₹28,368). Skill rises on stocks-only (+₹1,450) but falls on total (-₹7,460) because of one Bank Nifty stop. One month does not restore progression or adopt a version.
- Win rate to Sep 2026: V4 25.9% on 305 trades, Skill 29.2% on 301 trades, Unified 25.8% on 306 trades — Sep win rates (V4 33.3%, Skill 13.3%) are not proof of edge.
- NO V5 / skill v2 adoption on Jul–Sep 2026: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total, on unseen months. Jul totals were index-driven, Aug failed on all legs, Sep is a single genuine stocks rise for V4 but cumulative remains negative. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. Candidate fix to test (not adopted): exclude index point-scaled trades from the portfolio cap ranking, or cap index stop size — Jul–Sep 2026 again show single Bank Nifty/Nifty trades dominating totals in both directions.

## Cumulative progression (capped, to Aug 2026)
| Series | Jul 2026 | Aug 2026 | Trades to Aug 2026 | Win to Aug 2026 |
|---|---|---|---|---|
| Capped-V4 total | +₹4,598 | -₹4,688 (FALL) | 290 | 25.5% (74 targets) |
| Capped-V4 stocks-only | -₹28,622 | -₹30,453 (FALL) | 290 | — |
| Capped-Skill total | -₹30,378 | -₹53,719 (FALL) | 286 | 30.1% (86 targets) |
| Capped-Skill stocks-only | -₹12,753 | -₹14,269 (FALL) | 286 | — |
| Unified total | +₹4,598 | -₹4,688 (FALL) | 291 | 25.4% (74 targets) |
| Unified stocks-only | -₹28,997 | -₹30,828 (FALL) | 291 | — |

## X verdict to Aug 2026
- Frequency: PASS — 3.0/week, 15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS for all series in Aug 2026 — totals fall and stocks-only falls, and Aug win rates are the worst of 2026 so far (V4 6.7%, Skill 13.3%). Jul's index-driven total rise is fully erased for V4/Unified.
- NO V5 / skill v2 adoption on Aug 2026: adoption requires progression on net + win rate + frequency together AND on stocks-only net on unseen months. Aug fails all three on total and stocks-only. Previous best kept: capped-V4 / capped-Skill as separate series, paper only.

## Cumulative progression (capped, to Jul 2026)
| Series | Jun 2026 | Jul 2026 | Trades to Jul 2026 | Win to Jul 2026 |
|---|---|---|---|---|
| Capped-V4 total | -₹8,261 | +₹4,598 (rises, index-driven) | 275 | 26.5% (73 targets) |
| Capped-V4 stocks-only | -₹25,801 | -₹28,622 (FALL) | 275 | — |
| Capped-Skill total | -₹58,273 | -₹30,378 (rises, index-driven) | 271 | 31.0% (84 targets) |
| Capped-Skill stocks-only | -₹11,798 | -₹12,753 (FALL) | 271 | — |
| Unified total | -₹8,261 | +₹4,598 (rises, index-driven) | 276 | 26.4% (73 targets) |
| Unified stocks-only | -₹26,176 | -₹28,997 (FALL) | 276 | — |

## X verdict to Jul 2026
- Frequency: PASS — 3.0/week, 15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS on stocks-only for all series in Jul 2026. Totals rise only because of single Bank Nifty point-scaled targets (+₹15,680 V4, +₹24,610 Skill); stocks-only falls for V4 (-₹2,821), Skill (-₹955) and Unified (-₹2,821). A total rise driven by one index trade is not profit progression under X.
- Win rate to Jul 2026: V4 26.5% on 275 trades, Skill 31.0% on 271 trades, Unified 26.4% on 276 trades — Jul win rates (V4 26.7%, Skill 40.0%) are not proof of edge when the month's profit is one index trade.
- NO V5 / skill v2 adoption on Jul 2026: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total, on unseen months. Jul fails the stocks-only leg. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. Candidate fix to test (not adopted): exclude index point-scaled trades from the portfolio cap ranking, or cap index stop/target size, so single Bank Nifty/Nifty trades cannot dominate a month — Jul 2026 is the clearest positive-side example of that failure, mirroring Feb–Jun 2026 on the negative side.

## Cumulative progression (capped, to Jun 2026)
| Series | Mar 2026 | Apr 2026 | May 2026 | Jun 2026 | Trades to Jun 2026 | Win to Jun 2026 |
|---|---|---|---|---|---|---|
| Capped-V4 total | +₹407 | -₹3,213 (FALL) | -₹5,411 (FALL) | -₹8,261 (FALL) | 260 | 26.5% (69 targets) |
| Capped-V4 stocks-only | -₹17,133 | -₹20,753 | -₹22,951 | -₹25,801 | 260 | — |
| Capped-Skill total | -₹31,688 | -₹42,475 (FALL) | -₹39,315 (rises, far below peak) | -₹58,273 (FALL) | 256 | 30.5% (78 targets) |
| Capped-Skill stocks-only | -₹8,038 | -₹11,645 | -₹8,485 (rises) | -₹11,798 (FALL) | 256 | — |
| Unified total | +₹32 | -₹3,213 (FALL) | -₹5,411 (FALL) | -₹8,261 (FALL) | 261 | 26.4% (69 targets) |
| Unified stocks-only | -₹17,508 | -₹21,128 | -₹23,326 | -₹26,176 | 261 | — |

## X verdict to Jun 2026
- Frequency: PASS — 3.0/week, 12–15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS badly for all series in Apr–Jun 2026. V4/unified fall three months in a row and are now cumulatively negative in total (-₹8,261) for the first time, stocks-only -₹25,801 / -₹26,176. Skill falls in Apr and Jun, its May rise (+₹3,160) is a single TVSMOTOR trade, and its total (-₹58,273) is dominated by single Bank Nifty point-scaled stops (-₹7,180 Apr, -₹15,645 Jun) but is negative on stocks alone (-₹11,798) as well.
- Win rate to Jun 2026: V4 26.5% on 260 trades, Skill 30.5% on 256 trades, Unified 26.4% on 261 trades — Apr–Jun win rates (V4 20.0%/8.3%/20.0%, Skill 20.0%/33.3%/40.0%) are not proof of edge, and Jun Skill shows a 40.0% win rate can still lose -₹18,958 when one index stop dwarfs the targets.
- NO V5 / skill v2 adoption on Apr–Jun 2026 validation: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total, on unseen months. No series meets it. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. A V5 candidate must beat these capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression. Candidate fixes to test (not adopted): (a) exclude index point-scaled trades from the portfolio cap ranking, or cap index stop size, so single Bank Nifty/Nifty stops cannot dominate a month — Apr, Feb, Mar and Jun Skill months all show this failure; (b) tighten the OR filter (room/bias) for skill, since its win rate without the index leg is still not converting to stocks profit.

## Cumulative progression (capped, to Mar 2026)
| Series | Dec 2025 | Jan 2026 | Feb 2026 | Mar 2026 | Trades to Mar 2026 | Win to Mar 2026 |
|---|---|---|---|---|---|---|
| Capped-V4 total | +₹8,361 | +₹3,206 (FALL) | +₹2,886 (FALL) | +₹407 (FALL) | 218 | 28.4% (62 targets) |
| Capped-V4 stocks-only | -₹14,019 | -₹16,389 | -₹16,709 | -₹17,133 | 218 | — |
| Capped-Skill total | +₹327 | -₹4,853 (FALL) | -₹16,964 (FALL) | -₹31,688 (FALL) | 214 | 30.4% (65 targets) |
| Capped-Skill stocks-only | +₹3,592 | +₹1,197 | -₹3,834 | -₹8,038 | 214 | — |
| Unified total | +₹8,361 | +₹3,206 (FALL) | +₹2,886 (FALL) | +₹32 (FALL) | 219 | 28.3% (62 targets) |
| Unified stocks-only | -₹14,019 | -₹16,389 | -₹16,709 | -₹17,508 | 219 | — |

## X verdict to Mar 2026
- Frequency: PASS — 2.8–3.0/week, 14–15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS badly for all series in Jan–Mar 2026. V4/unified fall three months in a row and are now barely positive in total (+₹407 / +₹32) only because of the May–Jun 2025 index spikes; stocks-only is -₹17,133 / -₹17,508. Skill capped falls three months in a row, total -₹31,688, stocks-only -₹8,038, driven in Feb–Mar by single Bank Nifty point-scaled stops (-₹7,080, -₹10,520) but negative on stocks alone in both months as well.
- Win rate to Mar 2026: V4 28.4% on 218 trades, Skill 30.4% on 214 trades, Unified 28.3% on 219 trades — Jan–Mar 2026 win rates (V4 6.7%/46.7%/21.4%, Skill 6.7%/33.3%/13.3%) are below the 2025 averages and not proof of edge.
- NO V5 / skill v2 adoption on Jan–Mar 2026 validation: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total, on unseen months. No series meets it. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. A V5 candidate must beat these capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression. Two candidate fixes to test (not adopted): (a) exclude index point-scaled trades from the portfolio cap ranking, or cap index stop size, so single Bank Nifty/Nifty stops cannot dominate a month; (b) tighten the OR filter (room/bias) for skill, since Feb–Mar skill win rates collapsed to 33.3%/13.3%.

## Cumulative progression (capped, to Dec 2025)
| Series | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec | Trades to Dec | Win to Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Capped-V4 total | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 | +₹27,379 (index-driven) | +₹26,058 (FALL) | +₹14,376 (FALL) | +₹13,056 (FALL) | +₹11,115 (FALL) | +₹7,709 (FALL) | +₹8,361 (rises, below Sep peak) | 174 | 29.3% (51 targets) |
| Capped-V4 stocks-only | +₹599 | -₹1 | +₹2,083 | +₹947 | -₹6,158 | -₹3,001 | -₹4,322 | -₹8,004 | -₹9,324 | -₹11,265 | -₹14,671 | -₹14,019 | 174 | — |
| Capped-Skill total | -₹275 | +₹1,769 | +₹7,576 | +₹6,326 (FALL) | +₹3,313 (FALL) | +₹3,918 | +₹3,387 (FALL) | +₹2,996 (FALL) | +₹5,762 | +₹2,652 (FALL) | +₹1,434 (FALL) | +₹327 (FALL) | 170 | 33.5% (57 targets) |
| Capped-Skill stocks-only | -₹275 | +₹1,769 | +₹7,576 | +₹6,326 | +₹3,313 | +₹3,918 | +₹3,387 | +₹6,261 | +₹9,027 | +₹5,917 | +₹4,699 | +₹3,592 | 170 | — |
| Unified total | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 | +₹27,379 (index-driven) | +₹26,058 (FALL) | +₹14,376 (FALL) | +₹13,056 (FALL) | +₹11,115 (FALL) | +₹7,709 (FALL) | +₹8,361 (rises, below Sep peak) | 174 | 29.3% |

## X verdict to Dec 2025
- Frequency: PASS — 3.0/week, 12–15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS for both series. V4/unified rise in Dec (+₹652) after five falling months but remain below the Sep peak, and V4 stocks-only is -₹14,019 — the V4 total (+₹8,361) is still entirely index-driven (Jun Nifty +₹22,260 and May Bank Nifty net, minus Aug index stops). Skill capped falls in Oct, Nov, and Dec in a row; its total (+₹327) is barely positive and its stocks-only (+₹3,592) is well below its Sep peak (+₹9,027).
- Win rate to Dec: V4 29.3% on 174 trades, Skill 33.5% on 170 trades — not proof of edge, and Oct–Dec win rates (13.3%, 25.0%, 26.7–33.3%) are below the Jan–Sep averages.
- NO V5 / skill v2 adoption on Oct–Dec validation: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total, on unseen months. Neither series meets it. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. A V5 candidate must beat these capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression.

## Cumulative progression (capped, to Sep 2025)
| Series | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Trades to Sep | Win to Sep |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Capped-V4 total | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 | +₹27,379 (index-driven) | +₹26,058 (FALL) | +₹14,376 (FALL) | +₹13,056 (FALL) | 132 | 31.8% (42 targets, verified from capped_summary JSONs) |
| Capped-V4 stocks-only | +₹599 | -₹1 | +₹2,083 | +₹947 | -₹6,158 | -₹3,001 | -₹4,322 | -₹8,004 | -₹9,324 | 132 (stocks trades only in Jul-Sep; earlier months stocks-only except May/Jun index legs) | — |
| Capped-Skill total | -₹275 | +₹1,769 | +₹7,576 | +₹6,326 (FALL) | +₹3,313 (FALL) | +₹3,918 | +₹3,387 (FALL) | +₹2,996 (FALL) | +₹5,762 | 128 | 36.7% (47 targets, verified from capped_summary JSONs) |
| Capped-Skill stocks-only | -₹275 | +₹1,769 | +₹7,576 | +₹6,326 | +₹3,313 | +₹3,918 | +₹3,387 | +₹6,261 | +₹9,027 | 128 | — |
| Unified total | +₹599 | -₹1 (FALL) | +₹2,083 | +₹947 (FALL) | +₹1,962 | +₹27,379 (index-driven) | +₹26,058 (FALL) | +₹14,376 (FALL) | +₹13,056 (FALL) | 132 | 31.8% |
\* May V4 stocks-only cumulative is recomputed here as ₹947 - ₹7,105 = -₹6,158; Jun is -₹6,158 + ₹3,157 = -₹3,001, matching the Jun file. Sep table uses that verified Jun stocks-only base plus Jul (-₹1,321), Aug (-₹3,682), Sep (-₹1,320).

## X verdict to Sep 2025
- Frequency: PASS for capped series — 2.4–3.0/week, 12–15 trades/month portfolio total, NOT 500+. This is the only X leg that passes.
- Net progression: FAILS for V4/unified — cumulative falls Jul, Aug, and Sep in a row, and total is index-driven, stocks-only -₹9,324. Skill capped rises in Sep and its stocks-only cumulative (+₹9,027) is now above its Mar peak on a stocks-only basis (+₹7,576), but its TOTAL (+₹5,762) is still below the Mar total peak, because Aug index stops drag it. So skill shows a stocks-only recovery in Sep, not a total progression.
- Win rate to Sep: V4 31.8% on 132 trades, Skill 36.7% on 128 trades — small sample, not proof.
- NO V5 / skill v2 adoption on Jul–Sep validation: adoption requires progression on net + win rate + frequency together AND on stocks-only net, not just total. V4 fails all three on stocks-only (net falls, win 20.0% in Sep, frequency already capped). Skill Sep alone (50.0% win, +₹2,766 stocks) is one month, not a validated progression — it does not retroactively adopt a skill v2. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. A V5 candidate must beat the capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression.

## Next
Oct 2026, then to 28 Oct 2026, same capped rules, appended after each month. Raw totals must NOT be merged into this file. NOTE: cache now ends 2026-09-30; Oct 2026 likewise requires a fresh Upstox fetch (chunked, ~30-day range cap) before it can run — do not fabricate data.

### 2026-10 — DONE, PARTIAL to 28 Oct 2026, 18 days, 5 ISO weeks
- Fresh Upstox fetch: Oct 2026 fetched 2026-10-01 to 2026-10-28 only (NOT the full month, NOT Oct 29) for all 27 instruments, 18 trading days each, no fabrication. Upstox tested first: Bank Nifty search succeeds, no 401. Cache now ends 2026-10-28.
- Raw candidates: V4 103, skill OR 393, skill after bias+room+PD filter 106.
- Capped-V4: 15 trades, 4 targets, 10 stops, 1 square-off, win 26.7%, net +₹11,242, expectancy +₹749.47, max DD ₹5,398, 3.0/week. Split: indices +₹16,640, stocks -₹5,398.
- Capped-Skill: 15 trades, 6 targets, 6 stops, 3 square-offs, win 40.0%, net +₹14,389, expectancy +₹959.27, max DD ₹3,428, 3.0/week. Split: indices +₹16,640, stocks -₹2,251.
- Unified capped: 15 trades, same as capped-V4 (+₹11,242).
- Cumulative: V4 +₹9,014 total (-₹2,228+₹11,242) — RISES in Oct, back to positive in total, but still far below the Jun 2025 total peak and entirely index-driven. Skill -₹46,790 total (-₹61,179+₹14,389) — RISES in Oct, still deeply negative. Unified +₹8,639 total (-₹2,603+₹11,242; see correction note below) — RISES in Oct.
- Stocks-only cumulative to Oct 2026 (partial): V4 -₹33,391 (-₹27,993-₹5,398) — FALLS in Oct. Skill -₹15,070 (-₹12,819-₹2,251) — FALLS in Oct. Unified -₹33,766 (-₹28,368-₹5,398) — FALLS in Oct. Oct is a stocks FAILURE month for all series despite the positive totals.
- FRAGILITY FLAG, Oct: the entire positive total in all three series is a single BANKNIFTY target on 2026-10-01, +₹16,640 — V4 setup4_reclaim CE and Skill OR breakout CE on the same day, same point-scaled amount. Without it, V4 Oct is -₹5,398 and Skill Oct is -₹2,251. This is a point-scaled index cash-equivalent, not portfolio rupees and not stocks progression. Best/worst Oct: V4 best BANKNIFTY +₹16,640, HINDCOPPER +₹690; worst TVSMOTOR 2026-10-08 stop -₹2,360, IRCTC -₹935. Skill best BANKNIFTY +₹16,640, HINDCOPPER +₹690; worst TVSMOTOR -₹2,360, IRCTC -₹470. One V4 "target" (NHPC 2026-10-06) nets -₹8 after the ₹40 cost — a target smaller than cost.
- Capped-trade date note: the latest capped trade date in Oct is 2026-10-26, not 2026-10-28. Oct 27-28 were trading days in the data (18 days total), but the ISO-week cap (W44) was already filled by the Oct 26 trades, so Oct 27-28 candidates ranked out under the cap. That is cap behaviour, not missing data.
- Source: ~/workspace/trading/data/progressive/capped_summary_2026-10.json, same capped engine/rules. Results gate NEUTRAL (0) for Oct 2026 — no gate rule was adopted from the v1 patterns in this series, so it is not applied retroactively.

## Cumulative progression (capped, FINAL, Jan 2025 to 28 Oct 2026)
Verified by summing all 22 capped_summary JSONs (2025-01 to 2026-10). This corrects two figures in the Sep-2026 brief: Skill trades to Sep 2026 are 302, not 301, in the JSONs (targets 88, so win 29.1% to Sep, not 29.2%); and Unified total to Sep 2026 is -₹2,603, not -₹2,228, because Mar 2026 unified (-₹2,854) differs from capped-V4 (-₹2,479) — the Sep brief carried V4's total into the unified row. Unified stocks-only to Sep (-₹28,368) was correct.
| Series | Sep 2026 | Oct 2026 (to 28 Oct) | Trades to 28 Oct 2026 | Win to 28 Oct 2026 |
|---|---|---|---|---|
| Capped-V4 total | -₹2,228 | +₹9,014 (rises, index-driven) | 320 | 25.9% (83 targets) |
| Capped-V4 stocks-only | -₹27,993 | -₹33,391 (FALL) | 320 | — |
| Capped-Skill total | -₹61,179 | -₹46,790 (rises, index-driven) | 317 | 29.7% (94 targets) |
| Capped-Skill stocks-only | -₹12,819 | -₹15,070 (FALL) | 317 | — |
| Unified total | -₹2,603 | +₹8,639 (rises, index-driven) | 321 | 25.9% (83 targets) |
| Unified stocks-only | -₹28,368 | -₹33,766 (FALL) | 321 | — |

## X verdict — FINAL, Jan 2025 to 28 Oct 2026
- Frequency: PASS for the whole series — capped at 3.0/week, 12–15 trades/month portfolio total, never 500+. The only X leg that passes consistently.
- Net progression: FAILS. The final totals look positive for V4/Unified only because of single index trades: Jun 2025 Nifty +₹22,260, May 2025 Bank Nifty net, Jul 2026 Bank Nifty +₹15,680, and now Oct 2026 Bank Nifty +₹16,640. On stocks-only — the leg that matters for the 25 stocks — every series is deeply negative at the end: V4 -₹33,391, Skill -₹15,070, Unified -₹33,766, and all three FELL on stocks-only in Oct 2026 even as their totals rose.
- Win rate to 28 Oct 2026: V4 25.9% on 320 trades, Skill 29.7% on 317 trades, Unified 25.9% on 321 trades — not proof of edge. Oct win rates (V4 26.7%, Skill 40.0%) did not convert to stocks profit.
- NO V5 / skill v2 adopted on this full capped series: adoption requires progression on net + win rate + frequency together AND on stocks-only net on unseen months. Oct 2026 fails the stocks-only leg for all series. Previous best kept: capped-V4 / capped-Skill as separate series, paper only. A V5 candidate must beat these capped baselines on a future unseen month on stocks-only net as well as total, or it is not a progression. Candidate fix to test (not adopted): exclude index point-scaled trades from the portfolio cap ranking, or cap index stop/target size — Oct 2026 is the clearest positive-side example, mirroring Jul 2026, Feb–Jun 2026 on the negative side.

## Series complete
Jan 2025 to 28 Oct 2026 capped progressive run is COMPLETE. No further months in this series. Forward work is November 2026 paper validation of a candidate version, not a continuation of this backtest.
