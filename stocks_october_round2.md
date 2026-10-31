# Stocks — October 2026 optimization, ROUND 2 — 2026-10-30

**STOCKS ONLY — cash intraday, 25 screenshot stocks. Paper only, no
orders. Real money: ₹0. No live trades were placed.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade cost — NOT option premiums, NOT a futures/options lot
profit, NOT a real fill. Stocks are never pooled with index options;
the index (Nifty) is used only as a bias filter inside the system.**

Window: October 2026 = 1–28 Oct 2026 in cache, 18 trading days
(2026-10-29 missing from cache, not a zero-trade day). Jan–Sep 2026 =
185 trading days. All runs in-sample; nothing adopted. November 2026
paper remains the validation step.

## Verdict first — NO new best. S12 is kept. There is no S13.

Under the pre-registered winner rule (progress vs S12 on October net +
win rate + frequency together, AND Jan–Sep net not worse, AND Jan–Sep
max drawdown not deeper), **no Round 2 variant qualifies**. The best
October result remains **S12: October 8 trades, 62.5% win rate, 50.0%
full-target rate, net +₹1,885.00 provisional per 100 shares, expectancy
+₹235.62 provisional per 100 shares, October maxDD −₹1,395.00
provisional per 100 shares, 2.22 trades/week**, with its Jan–Sep check
at **93 trades, 55.9% win rate, net +₹3,607.50 provisional per 100
shares, maxDD −₹9,007.50 provisional per 100 shares**.

The binding wall is **candidate generation**, quantified in §1:
October's entire B8-PE pool is 16 candidates on 8 of 18 days, and
every mechanism that adds October trades adds net-negative shadow
trades, while every mechanism that filters trades removes October
frequency. This is stated plainly rather than manufacturing a winner.

One genuine finding survives (§2, G2): relaxing the weekly cap to
2/stock/week leaves October **exactly unchanged** (net +₹1,885.00
provisional per 100 shares) and improves Jan–Sep to **net +₹6,530.00
provisional per 100 shares, maxDD −₹7,157.50 provisional per 100
shares**. It makes zero October progress, so under the winner rule it
cannot replace S12 — it is recorded as a Jan–Sep-side improvement and
a November-paper design question for the user, not as a new best.

---

## 1. Funnel diagnosis — where October candidates die in S12

Method: the full B8-PE pool was re-scored at the S12 (3R) exit and
gate-tagged; the funnel cap reproduced the S12 trade CSV **exactly**
(101/101 trades, zero net differences), so every shadow figure below
is provisional per 100 shares on the same basis as taken trades.

| Funnel stage (October) | Candidates | Shadow net ₹ | Wins | Full targets |
|---|---|---|---|---|
| B8-PE pool (all) | 16 | −1,000.00 | 7 | 4 |
| Gate-blocked | 2 | −685.00 | 0 | 0 |
| Gate survivors | 14 | −315.00 | 7 | 4 |
| Capped out (1/day, 1/stock/week) | 6 | −2,200.00 | 2 | 0 |
| **Taken (S12)** | **8** | **+1,885.00** | **5** | **4** |

| Funnel stage (Jan–Sep) | Candidates | Shadow net ₹ | Wins | Full targets |
|---|---|---|---|---|
| B8-PE pool (all) | 193 | −1,390.00 | 107 | 36 |
| Gate-blocked | 12 | −1,102.50 | 6 | 2 |
| Gate survivors | 181 | −287.50 | 101 | 34 |
| Capped out | 88 | −3,895.00 | 49 | 13 |
| **Taken (S12)** | **93** | **+3,607.50** | **52** | **21** |

(All shadow nets in both tables are provisional per 100 shares.)

Reading of the leaks, in size order:

1. **Pool size is the binding wall.** October has 16 PE candidates on
   only **8 of 18 trading days** — 10 days generate nothing at all.
   Even taking every gate survivor caps October at 14 trades, and the
   survivor pool as a whole is net −₹315.00 provisional per 100
   shares: the ranking/cap is what makes October positive, by
   selecting 8 of 14. Frequency of ~18 valuable October trades is
   arithmetically impossible inside this pool.
2. **The cap is protective, not wasteful, in October.** All 6
   capped-out October candidates were dropped by the 1/day rule
   (5 pure day-cap, 1 day+week); their shadow net is −₹2,200.00
   provisional per 100 shares (GLENMARK 9 Oct −₹1,040, HINDUNILVR
   9 Oct −₹500, BDL 26 Oct −₹480, UNITDSPR 9 Oct −₹280, and two
   +₹50 partial wins). The one genuine cluster day is 9 Oct, which
   produced 4 candidates — the taken one (OBEROIRLTY) lost −₹790 and
   all three capped alternates also lost.
3. **The gate is not an October leak.** It blocks exactly 2 October
   candidates, both no_event, both losers (HINDCOPPER −₹315,
   HINDALCO −₹370, provisional per 100 shares shadow). In Jan–Sep it
   blocks 12 candidates netting −₹1,102.50 provisional per 100
   shares shadow — also protective on balance.
4. **Timing:** all 16 October pool entries are between 09:35 and
   11:20 — the design only ever sees the morning. Family J tests
   whether a later second signal exists (§5).
5. **Tier legs (taken trades, Jan–Oct):** no_event 53 trades,
   −₹1,482.50 provisional per 100 shares (Jan–Sep alone: 50 trades,
   −₹2,762.50 provisional per 100 shares; October alone: 3 trades,
   +₹1,280.00 provisional per 100 shares); post_reaction 22 trades,
   +₹5,295.00 provisional per 100 shares; pre_announcement 21 trades,
   +₹1,120.00 provisional per 100 shares Jan–Oct but October 3 trades,
   −₹895.00 provisional per 100 shares; single_news 5 trades,
   +₹560.00 provisional per 100 shares.

---

## 2. Family G — cap structure (spec frozen before scoring)

October / Jan–Sep, all figures provisional per 100 shares:

| Variant | Oct trades | Oct win % | Oct FT % | Oct net ₹ | Oct exp ₹ | Oct maxDD ₹ | Oct /wk | Jan–Sep trades | Jan–Sep win % | Jan–Sep FT % | Jan–Sep net ₹ | Jan–Sep exp ₹ | Jan–Sep maxDD ₹ | Jan–Sep /wk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| G0 = S12 cap (1/day, 1/wk) | 8 | 62.5 | 50.0 | +1,885.00 | +235.62 | −1,395.00 | 2.22 | 93 | 55.9 | 22.6 | +3,607.50 | +38.79 | −9,007.50 | 2.51 |
| G1 2/day, 1/wk | 11 | 54.5 | 36.4 | +415.00 | +37.73 | −2,435.00 | 3.06 | 132 | 53.0 | 18.2 | −2,590.00 | −19.62 | −12,447.50 | 3.57 |
| **G2 1/day, 2/wk** | **8** | **62.5** | **50.0** | **+1,885.00** | **+235.62** | **−1,395.00** | **2.22** | **94** | **57.4** | **25.5** | **+6,530.00** | **+69.47** | **−7,157.50** | **2.54** |
| G3 2/day, 2/wk | 12 | 58.3 | 33.3 | +465.00 | +38.75 | −2,435.00 | 3.33 | 142 | 52.8 | 19.0 | −1,065.00 | −7.50 | −11,602.50 | 3.84 |

- The 2/day variants (G1/G3) confirm the funnel shadow almost
  exactly: the extra October slots are the losing capped-out
  candidates, October net falls to +₹415.00 / +₹465.00 provisional
  per 100 shares, and Jan–Sep turns negative. **Rejected —
  October-overfit in reverse: more trades, less money, both windows.**
- G2 changes **nothing in October** (no October trade was week-cap
  blocked) and improves Jan–Sep by composition: it swaps 6 Jan–Sep
  trades for 7 (net effect +₹2,922.50 provisional per 100 shares),
  the largest single swap-in being TVSMOTOR 2026-07-15 at +₹1,880.00
  provisional per 100 shares — so the improvement is real but
  concentrated in a handful of swaps, not a broad effect. It fails
  the winner rule on the October-progress leg (identical, not
  better) and is therefore **not named S13**. It is the one change
  Round 2 found that costs October nothing.

## 3. Family H — weak-leg (tier) repair (spec frozen before scoring)

October / Jan–Sep, all figures provisional per 100 shares:

| Variant | Oct trades | Oct win % | Oct FT % | Oct net ₹ | Oct exp ₹ | Oct maxDD ₹ | Oct /wk | Jan–Sep trades | Jan–Sep win % | Jan–Sep FT % | Jan–Sep net ₹ | Jan–Sep exp ₹ | Jan–Sep maxDD ₹ | Jan–Sep /wk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H1 pre tnet ≥₹1,000 | 7 | 71.4 | 57.1 | +2,040.00 | +291.43 | −1,170.00 | 1.94 | 90 | 57.8 | 22.2 | +3,250.00 | +36.11 | −9,115.00 | 2.43 |
| H2 pre room ≥3.0 & tnet ≥₹600 | 7 | 71.4 | 57.1 | +1,860.00 | +265.71 | −1,420.00 | 1.94 | 88 | 56.8 | 21.6 | +725.00 | +8.24 | −8,590.00 | 2.38 |
| H3 no_event AND bar | 5 | 60.0 | 40.0 | +605.00 | +121.00 | −1,015.00 | 1.39 | 53 | 50.9 | 22.6 | +1,130.00 | +21.32 | −9,510.00 | 1.43 |
| H4 no_event tnet ≥₹600 | 8 | 62.5 | 50.0 | +1,885.00 | +235.62 | −1,395.00 | 2.22 | 69 | 53.6 | 21.7 | +3,342.50 | +48.44 | −8,672.50 | 1.86 |

- H1 is the October trap in pure form: October net rises to
  +₹2,040.00 provisional per 100 shares and win rate to 71.4%, but
  frequency falls (7 trades) and Jan–Sep net falls to +₹3,250.00
  provisional per 100 shares with a deeper drawdown (−₹9,115.00
  provisional per 100 shares). **Rejected: frequency leg + Jan–Sep
  legs fail.**
- H2 removes the October OBEROIRLTY loser as designed but cap
  backfill and its Jan–Sep damage (net +₹725.00 provisional per 100
  shares) make it worse everywhere that matters. **Rejected.**
- H3 (S11's AND rule on the B8 pool) does not kill October outright
  this time — October keeps 5 trades at +₹605.00 provisional per 100
  shares — but it cuts October net by two-thirds and Jan–Sep net to
  +₹1,130.00 provisional per 100 shares. **Rejected; the S11 caveat
  was warranted.**
- H4 leaves October identical and shallows Jan–Sep drawdown to
  −₹8,672.50 provisional per 100 shares, but Jan–Sep net falls to
  +₹3,342.50 provisional per 100 shares and frequency drops to
  1.86/week. **Rejected: Jan–Sep net leg fails.**
- H5 (H2+H4 combo) was pre-registered only if both parts left
  October net ≥ S12's; H2 did not (+₹1,860.00 < +₹1,885.00
  provisional per 100 shares), so **H5 was not scored**, per spec.

## 4. Family I — drawdown-control exits on S12's same entries (spec frozen)

The control replay (I0) reproduced S12's nets exactly (0 diffs).
October / Jan–Sep, all figures provisional per 100 shares:

| Variant | Oct net ₹ | Oct win % | Oct FT % | Jan–Sep net ₹ | Jan–Sep win % | Jan–Sep FT % | Jan–Sep maxDD ₹ |
|---|---|---|---|---|---|---|---|
| I0 = S12 exit (3R, BE) | +1,885.00 | 62.5 | 50.0 | +3,607.50 | 55.9 | 22.6 | −9,007.50 |
| I1 lock +0.5R after partial, 3R | +1,277.50 | 62.5 | 37.5 | +3,713.75 | 55.9 | 16.1 | −8,823.75 |
| I2 time-stop 60 min | +1,885.00 | 62.5 | 50.0 | +3,405.00 | 55.9 | 22.6 | −8,920.00 |
| I3 time-stop 120 min | +1,885.00 | 62.5 | 50.0 | +3,077.50 | 54.8 | 22.6 | −9,007.50 |

(Frequency is unchanged at 8 October / 93 Jan–Sep trades in all I
variants — same entries.)

- I1 buys a trivially shallower Jan–Sep drawdown (−₹8,823.75 vs
  −₹9,007.50 provisional per 100 shares) at the cost of October net
  (+₹1,277.50 provisional per 100 shares) and full-target rate.
  **Rejected: October leg fails.**
- I2/I3 time-stops barely bind (most S12 trades resolve fast) and
  only subtract Jan–Sep net. **Rejected.** Drawdown control via exits
  is exhausted: S12's drawdown is an entry-composition problem
  (the Mar–Jun bleed), not an exit problem.

## 5. Family J — second-signal rescan (spec frozen before scoring)

The rescan source is real: **142 second-signal candidates Jan–Oct**
(13 in October), re-scored at the 3R exit their shadow net is
−₹997.50 provisional per 100 shares in October and +₹2,842.00
provisional per 100 shares over 129 Jan–Sep candidates (≈ +₹22 per
candidate — thin). October / Jan–Sep, all figures provisional
per 100 shares:

| Variant | Oct trades | Oct win % | Oct FT % | Oct net ₹ | Oct exp ₹ | Oct maxDD ₹ | Oct /wk | Jan–Sep trades | Jan–Sep win % | Jan–Sep FT % | Jan–Sep net ₹ | Jan–Sep exp ₹ | Jan–Sep maxDD ₹ | Jan–Sep /wk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| J1 rescan pool, S12 cap | 10 | 50.0 | 40.0 | +1,265.00 | +126.50 | −1,775.00 | 2.78 | 100 | 57.0 | 23.0 | +4,454.50 | +44.55 | −9,170.00 | 2.70 |
| J2 rescan pool, 2/day cap | 13 | 53.8 | 38.5 | +815.00 | +62.69 | −2,815.00 | 3.61 | 151 | 56.3 | 21.2 | +1,852.00 | +12.26 | −10,787.50 | 4.08 |

- J1 buys 2 extra October trades (2.78/week) but October net falls
  to +₹1,265.00 provisional per 100 shares, win rate to 50.0%, and
  Jan–Sep drawdown deepens to −₹9,170.00 provisional per 100 shares
  even though Jan–Sep net rises to +₹4,454.50 provisional per 100
  shares. **Rejected: October net + win legs and Jan–Sep drawdown
  leg fail.**
- J2 is worse on every October and drawdown measure. **Rejected.**
- Setup2 (per the task caveat): the B8-timing pool contains **zero**
  setup2 candidates in Jan–Oct (all 209 are setup3 bounce-rejection),
  so there was no B8-pool setup2 leg to test; the S10 closure of
  that family stands.

## 6. Cross-family combo X1 (pre-registered)

Eligibility required a single change to be non-worsening in BOTH
windows. Only **G2** qualified (October identical; Jan–Sep better).
With only one eligible change there is nothing to stack, and G2
alone makes no October progress — so **no X1 was scored and no S13
is named**, per the winner rule.

## 7. Rejected list (with the leg each failed)

- **G1 / G3 (2/day cap)** — October net leg and Jan–Sep net leg:
  extra slots are the losing capped-out shadow trades.
- **G2 (2/stock/week)** — October-progress leg (identical, not
  better). Kept on record as a Jan–Sep improvement, NOT a new best.
- **H1 (pre prospective ≥₹1,000)** — frequency leg + Jan–Sep net and
  drawdown legs, despite the best October net of the round.
- **H2 (pre room/prospective bar)** — October net, Jan–Sep net legs.
- **H3 (no_event AND)** — October net and frequency legs, Jan–Sep net.
- **H4 (no_event floor ₹600)** — Jan–Sep net and frequency legs.
- **I1 (lock +0.5R @3R)** — October net and full-target legs.
- **I2 / I3 (time-stops)** — Jan–Sep net leg; no October progress.
- **J1 / J2 (rescan)** — October net and win legs; J1 also Jan–Sep
  drawdown, J2 also Jan–Sep net.

## 8. Best result — S12 October trade-by-trade (unchanged, kept best)

Every figure provisional per 100 shares:

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

## 9. Verdict

- **S12 remains the best stock version and a stage pass only**
  (October net +₹1,885.00 provisional per 100 shares, 62.5% win,
  2.22/week; Jan–Sep net +₹3,607.50 provisional per 100 shares).
  Nothing in Round 2 beat it under the frozen winner rule.
- **The frequency wall is candidate generation, with numbers:** 16
  October pool candidates on 8/18 days; gate blocks 2 (both losers);
  cap drops 6 (net −₹2,200.00 provisional per 100 shares shadow);
  the one new source found (second-signal rescan, 13 October
  candidates) shadows at −₹997.50 provisional per 100 shares in
  October. Within this design space, ~1 valuable trade/day in
  October is not reachable without taking net-negative trades.
- **Recorded for the user's decision, not adopted:** the G2 weekly-cap
  relaxation (2/stock/week) is October-neutral and Jan–Sep-positive
  (net +₹6,530.00 provisional per 100 shares, maxDD −₹7,157.50
  provisional per 100 shares). Whether November paper runs S12 as-is
  or S12+G2 is the user's call; this report names neither as adopted.
- Validation remains **November 2026 paper, no re-tuning during
  November**, events checked first. Nothing here is a live-trading
  instruction.

## Files

- This report: `stocks_october_round2.md`
- Specs frozen before scoring: `stocks_oct_round2_familyG_frozen.md`,
  `stocks_oct_round2_familyH_frozen.md`,
  `stocks_oct_round2_familyI_frozen.md`,
  `stocks_oct_round2_familyJ_frozen.md`
- Engines: `stocks_oct_round2_funnel.py`, `stocks_oct_round2_ghi.py`,
  `stocks_oct_round2_j.py`
- Raw results: `stocks_oct_round2_results.json` (merged),
  `stocks_oct_round2_ghi_results.json`, `stocks_oct_round2_j_results.json`,
  `stocks_oct_round2_funnel.json`
- Trades: `stocks_oct_round2_pool_shadow.csv` (full pool, 3R shadow),
  `stocks_oct_round2_G1_2day_1week_trades.csv`,
  `stocks_oct_round2_G2_1day_2week_trades.csv`,
  `stocks_oct_round2_G3_2day_2week_trades.csv`,
  `stocks_oct_round2_H1..H4_*_trades.csv`,
  `stocks_oct_round2_I1..I3_*_trades.csv`,
  `stocks_oct_round2_J1_rescan_cap_s12_trades.csv`,
  `stocks_oct_round2_J2_rescan_cap_2day_trades.csv`,
  `stocks_oct_round2_rescan_candidates.csv`
- No S13 engine/spec exists — no variant earned the name.
