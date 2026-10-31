# Documented — V5, (lA), and Bank Nifty — so they are not missed

Written 2026-10-29, after Chandu asked for this to be documented.
Paper only throughout. Nothing in this file is adopted for live trading.
All cash-index nets are 100 shares × index points, provisional rules
(₹40/trade, signal-candle stop, 2× target, square-off 15:10, short
paper-only), NOT Chandu's live options rules, unless a section says
options explicitly.

## 1. V5 — what it is

- Request: 2026-10-29 10:13 IST — run V4 index for Bank Nifty and Nifty,
  make it Version 5, taking inputs from Skill index AND V4 index,
  Bank Nifty + Nifty only, no stocks.
- Pool: V4 index candidates + Skill index candidates (Skill = OR-only,
  V4-style filters: bias-aligned, room ≥200×scale, PD bound).
- Dedup, same symbol+date: higher conviction (setup4=3 > setup3=2 >
  setup2=1 > skill OR=0), then higher prospective net target, then
  bias-strong, then room ratio. Filter: prospective net target ≥₹500.
- Cap: max 3 index/week, max 1/symbol/week — caps at 2/week in practice
  with only 2 symbols. Repeats were NOT allowed silently.
- Window: Jan 2026 – 28 Oct 2026 (203 days, Oct = 1–28 only).
- Files: v5_index_banknifty_nifty_jan_oct_2026.md, v5_index.py,
  data/progressive/v5_index_summary_2026-01.json … -10.json.

### V5 results, Jan–Oct 2026

- V5 index: 72 trades, 41.7% win, **+₹64,380**, expectancy +₹894/trade.
- Bank Nifty inside V5: 40 trades, **+₹16,415**, expectancy +₹410.
- Nifty inside V5: 32 trades, **+₹47,965**, expectancy +₹1,499.
- Inputs for comparison: V4 index 62 trades, 43.5%, +₹68,770;
  Skill index 58 trades, 43.1%, +₹40,240.
- **Verdict: NOT adopted.** Net below V4 index, win rate below BOTH
  inputs, trades MORE for a worse result. Without March (+₹99,805),
  V5 is −₹35,425 (V4 index ex-March −₹8,855).
- V5 as defined is, in outcome, the index leg of capped-v2 Unified
  (also 72 trades, 41.7%, +₹64,380) — pooling did not create a new edge.

### V5 Bank Nifty leg, month by month

Jan +₹6,900; Feb −₹24,615; Mar **+₹80,260**; Apr −₹2,090;
May −₹3,710; Jun −₹34,260; Jul −₹14,055; Aug −₹33,655;
Sep −₹1,990; Oct +₹43,630. Total +₹16,415.
March and October carry the Bank leg; June and August drag it.

### V5 October 2026 alone

7 trades, 71.4%, +₹51,825 — identical to V4 index October.
Bank 4 / +₹43,630, Nifty 3 / +₹8,195.

## 2. (lA) — what it is

- (lA) = (lC) = (n3) from the extended-window sweep, the best kept
  Nifty Cluster 1 variant, NOT adopted.
- Definition: BN-confirmed rescan morning + band-filtered re-entry.
  Re-entry risk in [10, rescan risk]. Morning phase scan-skip to
  11:30. Afternoon phase (>11:30) stop-on-first-fail to 15:05:
  the first afternoon candidate failing the band ENDS afternoon
  scanning. Target 2× risk. PE only in its original Cluster 1 form.
- Files: nifty_cluster1_extended_window_sweep.md,
  extended_window_sweep.py, nifty_failing_cases_jan_oct_2026.md.

### (lA) results

- Cluster 1 (8 failing PE trades, Jan–Aug 2026): **5/8 day-green,
  total −₹2,720**. Winners on the same window: 12/14 green, 2 no-trade,
  +₹83,380. Combined +₹80,660.
- Its three Cluster 1 failing days under (lA): 30 Mar −₹2,055,
  2 Apr −₹3,730, 13 May −₹5,075.
- October 2026, Nifty (lA) only: 2 trades, 2/2 green, +₹23,080
  (8 Oct +₹11,690, 23 Oct +₹11,390). No (lA) re-entry fired in October.
- Jan–Oct 2026, (lA)-only (capped): 47 trades, 59.6%, +₹23,435.
  Split: Nifty (original rule) 24 trades, 79.2%, **+₹71,780**;
  Bank mirror 23 trades, 39.1%, **−₹48,345**.
- Jan 2025 – 29 Oct 2026, Nifty (lA) only: 61 trades, 60.7%,
  **+₹99,125** (2025: 37 trades, +₹27,345; Jan–Oct 2026: +₹71,780).
- **Critical Jan–Oct 2026 finding:** (lA) re-entry legs fired 30 times
  pre-cap. Re-entry nets +₹51,300 against morning nets −₹207,425
  on those days, day nets −₹156,125, only 11/30 days green.
  Capped (lA) re-entry days: 22 days, −₹129,975, vs morning-target
  days +₹153,410. The re-entry is where (lA) loses money, concentrated
  in Bank mirror days (29 Jun Bank −₹24,935, 6 Feb Bank −₹22,855).
  No re-entry conclusion may be quoted from October alone.

### Bank (lA) mirror — provisional, NOT the original (lA)

- Roles swapped: Nifty confirms Bank, scale = Bank prev close / 55000,
  all other (lA) parameters carried over. Setup_rank 1 provisional.
- October capped: 2 trades, +₹12,725 (7 Oct −₹7,475, 21 Oct +₹20,200);
  uncapped 3 trades, +₹36,785 (plus 23 Oct +₹24,060, capped out in W43).
- Jan–Oct 2026: 23 trades, 39.1%, −₹48,345. Jan 2025 – Oct 2026
  Bank mirror total (from the long four-column build): 57 trades,
  −₹57,030.
- **Rule going forward: Nifty and Bank Nifty are separate systems.
  Do not pool (lA) Nifty with its Bank mirror, and do not quote a
  pooled (lA) total as an edge.**

## 3. Bank Nifty — all tracks, kept separate

### A. Original options system (V4, Bank Nifty options)

- Jan–Oct 2026, target 50: 42 trades, −₹1,740 (Jan–Jun +₹4,380,
  Jul–Oct −₹6,120). Target 90: −₹11,040.
- October pilot only (18 days, 6 trades): +₹12,180 — an outlier, not
  proof. Jul–Sep alone: 15 trades, 0 wins, −₹22,800.
- No-Setup-2, target 50, Jan–Oct: +₹1,640 (13 trades, 8 wins) — NOT
  adopted (Jan–Jun alone −₹880 on 4 trades, ~0.5/week).
- Costs assumed ₹220/trade in all Bank Nifty options backtests
  (assumption, not actual Upstox charges).
- 29 Oct 2026 forward-paper day: NO TRADE. Day high 54,980.15,
  low 54,047.90, close 54,909.65. Setup 4 CE never fired (low never
  below 54,019); Setup 3 PE did not meet the exact rejection-pin
  definition. Map: Red Band 54,415–54,449, ledge 54,019,
  PDH 54,440.25 / PDC 54,267.40 / PDL 53,626.15.

### B. Cash index, Bank leg (provisional rules)

- Jan–Oct 2026, capped-v2 V4 Bank: 35 trades, **+₹26,360**.
  Jan +₹6,900; Feb −₹24,615; Mar +₹65,340; Apr +₹4,300;
  May +₹9,165; Jun −₹34,260; Jul −₹14,055; Aug −₹33,655;
  Sep +₹3,610; Oct +₹43,630.
- Jan 2025 – 29 Oct 2026, Bank V4: 76 trades, 31.6%, **−₹25,060**
  (2025: 41 trades, −₹51,420). So "V4 best kept" is a Jan–Oct 2026
  statement, not a Jan 2025 – Oct 2026 one.
- Skill Bank, Jan–Oct 2026: 29 trades, −₹9,650.
  Jan 2025 – 29 Oct 2026: 58 trades, 25.9%, −₹96,400.
- October 2026, Bank V4: 4 trades, 75.0%, +₹43,630
  (1 Oct +₹16,640; 13 Oct −₹3,730; 21 Oct +₹20,200; 26 Oct +₹10,520).
  October, Skill Bank: 1 trade, +₹16,640 (same 1 Oct trade).
- This week (26–29 Oct 2026, four columns): Bank V4 1 trade
  (26 Oct +₹10,520); all other Bank columns 0 trades; 29 Oct ₹0 all columns.

### C. Volrix rebound, Bank Nifty (separate system, NOT v4/(lA))

- Spot proxy, Jul 2019 – Oct 2026: 48 positions, 43.75% win,
  net +₹62,737, PF 1.13 net, expectancy +₹1,307, max DD ₹1,30,109.
  Verdict: logic does NOT transfer from Nifty (PF 2.24, 66.7%).
- Options translation: only 8/48 entries testable (Oct 2024 onward),
  4 wins, net +₹9,576.55, PF 1.12. Same 8 on spot proxy: +₹83,842.99.
  Bank 24 Mar 2026 call died at expiry (0.15, −₹43,880.18) under
  no-roll, while spot-proxy rolled to +₹15,492.45.
- Files: volrix_banknifty_large_down_rebound_backtest.md,
  volrix_banknifty/ , volrix_banknifty_options/ .

### D. Merged / pooled Bank results (for reference only, NOT adoption)

- Dual Skill+(lA), Jan–Oct 2026: Bank leg in merged total is part of
  merged −₹1,600 (Nifty +₹79,585, Bank −₹81,185).
- Triple V4+Skill+(lA), Jan–Oct 2026: 74 trades, +₹23,355 total;
  Bank leg 41 trades, 34.1%, −₹48,615; Nifty leg +₹71,970.
- Club-all (triple + Volrix options), Jan–Oct 2026: intraday +₹23,355,
  Volrix options +₹14,350.18, mixed-unit combined +₹37,705.18 —
  mixed units, never the adoption metric. Bank combined −₹73,698.54.
- Four columns, Jan 2026 – 29 Oct 2026 (separate systems):
  Nifty (lA) +₹71,780; Bank V4 +₹26,360; Skill Bank −₹9,650;
  Skill Nifty +₹49,890; all-four separate sum +₹138,380.
  Jan 2025 – 29 Oct 2026 all-four sum +₹71,670 — different window,
  do NOT quote it for a Jan 2026 question.

## 4. What NOT to confuse

- V5 ≠ V4. V5 is the pooled V4+Skill index version. V4 index remains
  the previous best kept (Jan–Oct 2026: 62 trades, 43.5%, +₹68,770).
- (lA) ≠ V4, ≠ V5, ≠ Skill. (lA) is a scoped Nifty PE rescan/re-entry
  rule. Its Bank version is a provisional mirror, not the original.
- Bank V4 (cash) ≠ Bank V4 (options). Cash leg Jan–Oct 2026 +₹26,360;
  options leg Jan–Oct 2026 −₹1,740 at target 50. Never mix those rupees.
- October alone ≠ adoption. October had 18 days, 1–4 trades per
  column, cap artefacts, and zero (lA) re-entries.
- A pooled total (V5, dual, triple, club-all) ≠ a portfolio result.
  Columns/systems overlap on some days and use different units
  (cash-equivalent vs option premium).

## 5. Current status, 2026-10-29 evening

- NOTHING is adopted for live trading. Paper only, 1 lot / 100-share
  equivalent, no lot increase.
- Best kept reference: V4 index, Jan–Oct 2026, paper only.
- Most promising single column to paper-forward separately:
  Nifty (lA).
- Bank Nifty: separate, not ready, do not pool with Nifty.
- Next evidence: November 2026 paper, unseen, separate Nifty and
  Bank logs. A version is adopted only if it progresses on net +
  win rate + frequency together on unseen months.
- Next build in progress (2026-10-29 evening): new stock system S1 —
  intraday stocks (cash, NOT options), leveraging the old levels/
  setups and addressing the documented issues (inside-OR stop,
  give-back, re-entry losses, tiny wins, cap crowding). See
  new_stock_system_s1.md when it lands; S1 is not yet a result.

## 6. Source files (do not re-derive from memory)

- v5_index_banknifty_nifty_jan_oct_2026.md, v5_index.py
- nifty_cluster1_extended_window_sweep.md, extended_window_sweep.py
- nifty_failing_cases_jan_oct_2026.md
- jan_oct_2026_v4_and_skill.md, october_2026_v4_and_skill.md
- merged_skill_la_index_october_2026.md, merged_skill_la_index_jan_oct_2026.md
- triple_v4_skill_la_index_jan_oct_2026.md
- club_all_v4_skill_la_volrix_options_jan_oct_2026.md
- october_2026_four_column_nifty_bank_skill.md, october_2026_four_column.csv
- four_column_jan2025_oct2026.md, four_column_jan2025_oct2026.csv
- volrix_banknifty_large_down_rebound_backtest.md
- volrix_nifty_large_down_rebound_backtest.md, volrix_nifty_large_down_rebound_options_backtest.md
- goals/3-blue-line-bank-nifty-backtest/hidden_files/oct29_paper_closeout.md
