# Stocks — October 2026 highly-optimized run — 2026-10-30

**STOCKS ONLY — cash intraday, 25 screenshot stocks. Paper only, no
orders. Real money: ₹0. No live trades were placed.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade cost — NOT option premiums, NOT a futures/options lot
profit, NOT a real fill. Stocks are never pooled with index options;
the index (Nifty) is used only as a bias filter inside the system.**

Window: October 2026 = **1–28 Oct 2026 in cache, 18 trading days**.
2026-10-29 has no cache data and is reported as missing, not as a
zero-trade day. Jan–Oct 2026 = 203 trading days. All runs are
in-sample; nothing here is adopted. November 2026 paper is the
validation step for anything that stage-passes.

Events were checked FIRST, per the standing rule (moves are
event-driven): the gate tiers below come from
`stock_event_calendar_jan_oct_2026.csv`; the November picture is in
`stock_event_watchlist_nov2026.md` (results-driven month — ITC +
NATIONALUM 2 Nov, NHPC 4 Nov, GLENMARK 5 Nov, HINDALCO 6 Nov,
OIL 12 Nov). October's own event context matters below: OBEROIRLTY
reported 2026-10-16 (reaction 2026-10-19), HINDZINC 2026-10-19,
HINDUNILVR's event falls 2026-10-28.

---

## Best October result — S12 candidate (stage pass only, NOT adopted)

The best October variant found is **S12** (= Family E combo F3,
frozen before scoring in `stocks_oct_familyE_combos_frozen.md`,
consolidated in `new_stock_system_s12_frozen.md`, engine
`stock_system_s12.py`, which reproduces the F3 scoring exactly):

- **October 2026: 8 trades, 62.5% win rate, 50.0% full-target rate,
  net +₹1,885.00 provisional per 100 shares, expectancy
  +₹235.62 provisional per 100 shares per trade, max drawdown within
  October −₹1,395.00 provisional per 100 shares, 2.22 trades/week
  (0.44/day).**
- Against the S9 October baseline (1 trade, 0.0% win, net
  −₹520.00 provisional per 100 shares), S12 progresses on all three
  legs in October: net −₹520.00 → +₹1,885.00 provisional per 100
  shares, win rate 0.0% → 62.5%, frequency 0.28 → 2.22 trades/week.
- **Frequency honesty:** 2.22 trades/week is still well below the
  user's 1 valuable trade/day standard (that would be ~18 trades in
  October). The standard is NOT met. It is reported, not faked.
- **Anti-overfit check (Jan–Sep 2026, same frozen rules): 93 trades,
  55.9% win rate, 22.6% full-target rate, net +₹3,607.50 provisional
  per 100 shares, expectancy +₹38.79 provisional per 100 shares,
  max drawdown −₹9,007.50 provisional per 100 shares, 2.51
  trades/week.** Jan–Sep is positive and beats S9's Jan–Sep on net
  (+₹2,160.00 provisional per 100 shares), win rate (51.0%) and
  frequency — so S12 is NOT labelled October-overfit. But its
  Jan–Sep drawdown (−₹9,007.50 provisional per 100 shares) is far
  deeper than S9's (−₹4,415.00 provisional per 100 shares), and its
  no-event tier leg over Jan–Oct loses −₹1,482.50 provisional per
  100 shares (53 trades); the post-reaction tier carries it
  (+₹5,295.00 provisional per 100 shares, 22 trades). January alone
  contributes +₹7,712.50 provisional per 100 shares of the Jan–Oct
  total, and Mar–Jun is a four-month negative stretch. This is a
  stage pass with real fragility, not a robust system.
- Jan–Oct 2026 total for S12: 101 trades, 56.4% win rate, 24.8%
  full-target rate, net +₹5,492.50 provisional per 100 shares,
  max drawdown −₹9,007.50 provisional per 100 shares.

### What S12 is (one structural stack, each layer frozen before its scoring)

1. Entry pool B8: prospective floor ₹500 → ₹250, room floor 1.5× →
   1.25×, OR width 0.25–3.0% → 0.15–4.0%, and the second-close
   confirmation dropped (entry one candle earlier, stop = signal
   candle high for PE).
2. PE legs only (all 101 Jan–Oct S12 trades are setup3
   bounce-rejection PE; CE legs were net-negative in this pool).
3. S9 G-TIERED event gate unchanged, cap 1/day and 1/stock/week
   unchanged.
4. Exit E4: partial 50% at 1R, rest to breakeven, target **3R**
   instead of 2R.

### S12 October trade-by-trade (every figure provisional per 100 shares)

| Date | Stock | Setup / Tier | Entry | Entry ₹ | Stop ₹ | Risk ₹ | Room× | Net ₹ | Exit |
|---|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | GLENMARK | setup3 PE / no_event | 09:45 | 2,345.20 | 2,350.70 | 5.50 | 1.909 | **+1,060.00** | target (3R) 10:25 |
| 2026-10-06 | GODREJCP | setup3 PE / no_event | 09:35 | 859.15 | 862.35 | 3.20 | 3.625 | **+600.00** | target (3R) 10:10 |
| 2026-10-09 | OBEROIRLTY | setup3 PE / pre_announcement | 09:45 | 1,682.20 | 1,689.70 | 7.50 | 2.520 | **−790.00** | stop 09:55 |
| 2026-10-12 | ASTRAL | setup3 PE / no_event | 09:40 | 1,425.00 | 1,428.40 | 3.40 | 4.471 | **−380.00** | stop 09:50 |
| 2026-10-15 | HDFCBANK | setup3 PE / pre_announcement | 09:45 | 717.10 | 718.95 | 1.85 | 3.459 | **−225.00** | stop 09:55 |
| 2026-10-21 | HINDUNILVR | setup3 PE / pre_announcement | 09:40 | 1,866.50 | 1,869.70 | 3.20 | 4.156 | **+120.00** | stop after partial (BE) 09:55 |
| 2026-10-22 | OBEROIRLTY | setup3 PE / post_reaction | 11:20 | 1,638.70 | 1,645.00 | 6.30 | 1.587 | **+1,220.00** | target (3R) 12:15 |
| 2026-10-26 | HINDZINC | setup3 PE / post_reaction | 10:40 | 495.85 | 497.45 | 1.60 | 2.406 | **+280.00** | target (3R) 11:45 |

October by tier (all figures provisional per 100 shares):
post_reaction 2 trades, both full targets, +₹1,500.00;
pre_announcement 3 trades, 1 win, −₹895.00; no_event 3 trades,
2 full targets, +₹1,280.00. All 8 October trades are setup3 PE —
there were no CE trades in October under S12.

Caveat on "valuable": two October trades are small by the old ₹500
prospective bar (HINDZINC prospective ₹280 and HDFCBANK ₹330, both
provisional per 100 shares at the 2R basis). They are inside the
result because the B8 floor was frozen at ₹250 before scoring; they
are flagged here, not hidden.

---

## 1. Baseline — S9 October slice (the result the user rejected)

S9 Jan–Oct: 50 trades, 50.0% win, 26.0% full targets, net
+₹1,640.00 provisional per 100 shares. Its **October slice is a
single trade: ASTRAL 2026-10-12 setup3 PE, net −₹520.00 provisional
per 100 shares, 0.0% win rate, 0 full targets, 0.28 trades/week.**

Failing-legs diagnosis (why October failed, before any tweaking):

- The S8 price design produced only **3 uncapped candidates in all
  of October** (18 trading days, 450 stock-days): GODREJCP
  2026-10-06 (+₹217.50 provisional per 100 shares, partial-BE win),
  OBEROIRLTY 2026-10-06 (+₹650.00 provisional per 100 shares, full
  target), ASTRAL 2026-10-12 (−₹520.00 provisional per 100 shares,
  stop).
- **The gate blocked both October winners.** Both were no_event
  trades that failed BOTH no-event bars narrowly (room 1.874× /
  prospective ₹990 and room 1.870× / prospective ₹880, provisional
  per 100 shares, against bars of 2.0× / ₹1,000). The one survivor,
  ASTRAL, passed on room alone (2.875×) with prospective ₹920 —
  and it is the loser: entered 09:45, stopped 09:50, never reached
  the 1R partial. Its October setup/tier cell (setup3 PE, no_event)
  is therefore 1 trade / −₹520.00 provisional per 100 shares;
  every other October cell is empty, which is the whole problem:
  candidate scarcity first, gate second, exits last.

## 2. S11 — scored as frozen (S9 + no-event AND rule)

Engine `stock_system_s11.py` (S9 copy, one change), trades
`s11_trades_jan_oct_2026.csv`.

- **Jan–Oct 2026: 30 trades, 60.0% win rate, 26.7% full-target
  rate, net +₹5,075.00 provisional per 100 shares, expectancy
  +₹169.17 provisional per 100 shares, max drawdown −₹1,820.00
  provisional per 100 shares, 0.148 trades/day.** On Jan–Oct
  quality (net, win rate, shallow drawdown) S11 is the cleanest
  version scored — but frequency falls from 50 to 30 trades.
- **October slice: 0 trades, net ₹0.00 provisional per 100
  shares.** The AND rule blocks the only S9 October survivor
  (ASTRAL: prospective ₹920 < ₹1,000, provisional per 100 shares),
  and there is no October backfill. An empty month is not a result.
- Verdict: S11 progresses vs S9 on Jan–Oct net + win rate together
  but **fails the frequency leg and produces no October at all** —
  it does not answer the user's October demand. Kept as the
  Jan–Oct quality reference; not adopted.

## 3. Family A — exit variants on S9's SAME entries (effect isolated)

The replay engine first reproduced the baseline exactly (E0 vs
original S9 nets: zero differences on all 50 trades). October's
single S9 leg stopped before any partial, so **every exit variant
scores October identically: 1 trade, net −₹520.00 provisional per
100 shares. Exits were never October's problem.** Jan–Sep on the
same 49 entries (all figures provisional per 100 shares):

| Variant | Jan–Sep net ₹ | Win % | Full-target % |
|---|---|---|---|
| E0 baseline (2R, partial 50%@1R, BE) | +2,160.00 | 51.0 | 26.5 |
| E1 no partial, 2R | +460.00 | 30.6 | 28.6 |
| E2 target 1.5R, partial 50% | +1,240.00 | 51.0 | 32.7 |
| E3 target 2.5R, partial 50% | +4,197.50 | 51.0 | 26.5 |
| **E4 target 3R, partial 50%** | **+5,865.00** | 51.0 | 24.5 |
| E5 2R, partial 50%, lock +0.5R | +2,342.50 | 51.0 | 20.4 |
| E6 2R, partial 25% | +2,290.00 | 51.0 | 26.5 |
| E7 2R, partial 75% | +2,030.00 | 51.0 | 26.5 |
| E8 no partial, 1.5R | −2,380.00 | 34.7 | 32.7 |

Finding carried into Family E: letting the runner run to 3R (with
the 1R partial banked) is worth a great deal on Jan–Sep entries;
removing the partial (E1/E8) destroys win rate.

## 4. Family B — entry filters (gate + cap as S9)

October / Jan–Sep, all figures provisional per 100 shares:

| Variant | Oct trades | Oct win % | Oct FT % | Oct net ₹ | Oct /wk | Jan–Sep trades | Jan–Sep net ₹ | Jan–Sep win % |
|---|---|---|---|---|---|---|---|---|
| B0 baseline (= S9) | 1 | 0.0 | 0.0 | −520.00 | 0.28 | 49 | +2,160.00 | 51.0 |
| B1 prospective ≥₹250 | 4 | 25.0 | 25.0 | −677.50 | 1.11 | 69 | +442.50 | 49.3 |
| B2 room ≥1.25× | 1 | 0.0 | 0.0 | −520.00 | 0.28 | 55 | +4,070.00 | 54.5 |
| B3 room ≥1.0× | 2 | 50.0 | 50.0 | **+565.00** | 0.56 | 59 | +3,910.00 | 54.2 |
| B4 OR width 0.15–4.0% | 2 | 0.0 | 0.0 | −840.00 | 0.56 | 49 | +2,160.00 | 51.0 |
| B5 no second close | 7 | 57.1 | 42.9 | **+600.00** | 1.94 | 68 | +392.50 | 57.4 |
| B6 no Nifty bias block | 2 | 0.0 | 0.0 | −1,890.00 | 0.56 | 59 | −1,980.00 | 50.8 |
| B7 combo loose (B1+B2+B4) | 4 | 25.0 | 25.0 | −677.50 | 1.11 | 75 | +2,370.00 | 52.0 |
| B8 combo (B7 + no second close) | 8 | 62.5 | 50.0 | **+1,055.00** | 2.22 | 106 | **−315.00** | 50.9 |

Diagnosis per lever: lowering the prospective floor alone (B1)
adds small losers in October; widening the OR (B4) adds a loser;
removing the Nifty bias block (B6) is the worst single change in
both periods — the block is protective, keep it. Room ≥1.0× (B3)
adds exactly one October trade, GLENMARK 2026-10-01, a full target
worth +₹1,085.00 provisional per 100 shares at the 2R exit, whose
room (1.133×) the 1.5× floor was discarding. Dropping the
second-close (B5) is the frequency lever: entries one candle
earlier with tighter stops create genuine October trades on
1, 6, 9, 12, 21, 22 and 26 Oct. B8 stacks the levers and wins
October but its Jan–Sep is negative (−₹315.00 provisional per 100
shares, max drawdown −₹9,537.50 provisional per 100 shares) —
**B8 at the 2R exit is October-overfit and is rejected as-is**;
it only becomes the S12 stage pass after the Family E exit change,
which was frozen independently from Family A's Jan–Sep evidence.

## 5. Family C — setup mix

- On the B0 pool: PE-only reproduces S9 October exactly (1 trade,
  −₹520.00 provisional per 100 shares); CE-only has **0 October
  trades** (net ₹0.00 provisional per 100 shares — an empty slice).
- On the B8 pool: PE-only is identical to B8 in October (8 trades,
  +₹1,055.00 provisional per 100 shares at the 2R exit) because
  every October B8 trade is already PE; in Jan–Sep, PE-only turns
  B8 positive: 93 trades, 55.9% win, net +₹1,592.50 provisional per
  100 shares, vs B8 mixed −₹315.00 provisional per 100 shares.
  **CE legs in the loosened pool are a Jan–Sep drag (−₹3,465.00
  provisional per 100 shares, 27 trades, 29.6% win) — that, not
  October, is why S12 is PE-only.**

## 6. Family D — event-gate variants

On the B0 (S9) pool, October, all figures provisional per 100 shares:
no-gate D0 and loosened-no-event D3 both give 2 trades, 50.0% win,
net −₹302.50 (the cap picks GODREJCP +₹217.50 over OBEROIRLTY on
prospective ranking, plus the ASTRAL loser) — **ungating alone does
not fix October**; event-only D4 and S11-gate D2 both give 0 October
trades (net ₹0.00 provisional per 100 shares, empty). On the B8
pool: D3 (no-event at base bar) keeps October at +₹1,055.00
provisional per 100 shares but worsens Jan–Sep to −₹907.50
provisional per 100 shares; D0 (no gate) drops October to
+₹125.00 provisional per 100 shares (cap ranking without tiers
picks worse October legs) and Jan–Sep to −₹3,287.50 provisional
per 100 shares. **The S9 gate stays in S12 unchanged.**

## 7. Family E — entry × exit combos (frozen before scoring)

October / Jan–Sep, all figures provisional per 100 shares:

| Combo | Oct trades | Oct win % | Oct FT % | Oct net ₹ | Oct maxDD ₹ | Jan–Sep trades | Jan–Sep net ₹ | Jan–Sep maxDD ₹ |
|---|---|---|---|---|---|---|---|---|
| F1 = B3 + 3R exit | 2 | 50.0 | 50.0 | +940.00 | −520.00 | 59 | **+7,465.00** | −6,000.00 |
| F2 = B3 + 2.5R exit | 2 | 50.0 | 50.0 | +752.50 | −520.00 | 59 | +6,137.50 | −5,990.00 |
| **F3 = B8-PE + 3R exit (= S12)** | **8** | **62.5** | **50.0** | **+1,885.00** | −1,395.00 | 93 | +3,607.50 | −9,007.50 |
| F4 = B5 + 3R exit | 7 | 57.1 | 42.9 | +1,350.00 | −1,170.00 | 68 | +1,712.50 | −8,625.00 |
| F5 = B2 + 3R exit | 1 | 0.0 | 0.0 | −520.00 | −520.00 | 55 | **+7,860.00** | −4,000.00 |
| F6 = B3 + lock-0.5R exit | 2 | 50.0 | 0.0 | +2.50 | −520.00 | 59 | +3,742.50 | −6,382.50 |

F1 is the quality runner-up: a thinner but cleaner October
(GLENMARK 2026-10-01 +₹1,460.00 provisional per 100 shares at the
3R exit; ASTRAL −₹520.00 provisional per 100 shares) and the
second-best Jan–Sep. F5 has the best Jan–Sep of the whole run
(+₹7,860.00 provisional per 100 shares, shallowest combo drawdown
−₹4,000.00 provisional per 100 shares) but its October is still
the single ASTRAL loser — room 1.25× alone creates no October
trade, so F5 does not answer the October demand.

## 8. Rejected variants (kept separate, with the leg each failed)

- **S11** — Jan–Oct quality pass, **frequency/October fail**: 0
  October trades. Not the October answer.
- **B8 at the 2R exit** — October +₹1,055.00 provisional per 100
  shares but Jan–Sep −₹315.00 provisional per 100 shares:
  **October-overfit as scored**; only the independently frozen
  3R exit (Family A evidence) rescues its Jan–Sep, as S12.
- **B1 / B7 (prospective-floor loosening)** — October net worsens
  (−₹677.50 provisional per 100 shares); small trades are losers
  in October.
- **B4 (OR widening)** — October −₹840.00 provisional per 100
  shares; adds noise, no October edge.
- **B6 (Nifty bias block removed)** — worst in both periods
  (October −₹1,890.00, Jan–Sep −₹1,980.00, provisional per 100
  shares). The block is protective.
- **B2 alone** — Jan–Sep strong (+₹4,070.00 provisional per 100
  shares) but October unchanged (−₹520.00 provisional per 100
  shares): no October progress.
- **D0 / D3 (gate removed or no-event loosened)** — October
  −₹302.50 provisional per 100 shares on the S9 pool; gate removal
  also worsens the B8 pool in both periods.
- **D4 (event-tiers only) / D2 on B0** — 0 October trades; empty
  months are not results.
- **E1 / E8 (no-partial exits)** — Jan–Sep win rate collapses
  (30.6% / 34.7%); E2 (1.5R target) and E5/E6/E7 are dominated by
  E4 on Jan–Sep.
- **F6 (lock +0.5R trail)** — October collapses to +₹2.50
  provisional per 100 shares: locking early strangles the runner.

## 9. Verdict

- **S12 (F3) is the October winner and a stage pass only**: it
  progresses vs S9 October on net, win rate and frequency together
  (net +₹1,885.00 vs −₹520.00, win 62.5% vs 0.0%, 2.22 vs 0.28
  trades/week — every figure provisional per 100 shares), and its
  Jan–Sep check stays positive (+₹3,607.50 provisional per 100
  shares) rather than destroying the earlier window. It is **NOT
  adopted**: the whole chain is in-sample, its Jan–Sep drawdown
  is deep (−₹9,007.50 provisional per 100 shares), its no-event
  leg still loses over Jan–Oct, and 2.22 trades/week is not the
  user's 1 valuable trade/day.
- **S11 remains the Jan–Oct quality reference** (+₹5,075.00
  provisional per 100 shares, 60.0% win, drawdown −₹1,820.00
  provisional per 100 shares) but with zero October trades it
  cannot be the October system.
- Previous best S9 is kept on the record; S10 stays rejected.
- **Validation, if the user approves: November 2026 paper for
  S12, logged daily, no re-tuning during November**, judged on
  November's own net + win rate + frequency, with the November
  event watchlist checked first (results-heavy month). Nothing
  in this report is a live-trading instruction.

## Files

- This report: `stocks_october_highly_optimized.md`
- Engines: `stock_system_s11.py`, `stock_system_s12.py`,
  harness `stocks_oct_tuning.py`
- Specs frozen before scoring: `stocks_oct_familyA_exits_frozen.md`,
  `stocks_oct_familyB_entry_frozen.md`,
  `stocks_oct_familyCD_frozen.md`,
  `stocks_oct_familyE_combos_frozen.md`,
  `new_stock_system_s12_frozen.md` (consolidation of F3)
- Trades: `s11_trades_jan_oct_2026.csv`,
  `s11_uncapped_jan_oct_2026.csv`, `s12_trades_jan_oct_2026.csv`,
  `stocks_oct_best_s12_oct_trades.csv`
- Raw results: `stocks_oct_tuning_results.json`,
  `stocks_oct_familyE_results.json`,
  `data/progressive/s11_summary_2026-jan-oct.json`,
  `data/progressive/s12_summary_2026-jan-oct.json`
