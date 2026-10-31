# Stocks EQUITY — Exploration Round 3: does a selection layer save the pools?

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums anywhere in this report. Paper only, no orders.
Real money: ₹0.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade flat cost, unless a sentence says otherwise. Spec frozen
before scoring: `stocks_equity_explore3_frozen.md`. Engine:
`stocks_equity_explore3.py`.**

Portfolio rule (user, 2026-10-30 19:33 IST): **uncapped** — every
qualifying stock trades, max 1 trade per stock per day; the
minimum-2-valuable/day rule is a floor, not a cap. Windows:
Jan–Oct 2026 = 203 trading days (Oct = 1–28, 29 Oct missing from
cache, stated, not a zero day). Halves: **Jan–May = 99 trading
days, Jun–Oct = 104 trading days.** Reproduction gates passed
exactly: this engine's V5 × T10 Jan–Oct all-days net is
**−₹172,092.42 provisional per 100 shares** (= Jan–Sep
−₹178,594.99 plus October +₹6,502.57 from the prior reports), its
Skill × T10 October slice is 450 trades at **−₹21,952.22
provisional per 100 shares**, and its V5 × T125 October all-days
net is **+₹9,740.09 provisional per 100 shares** — all matching
the round-1/round-2 reports to the paisa.

---

## Verdict first — NO selection layer survives both halves

- **Zero of the 48 family × pool × exit combinations passes the
  frozen test** (both halves positive, or Jun–Oct positive with
  Jan–May expectancy ≥ −₹10/trade provisional per 100 shares).
  Almost every combination is negative in BOTH halves.
- The base pools themselves, Jan–Oct at the primary exit
  (target 1.0% / stop 0.5%): V5 pool 4,111 trades, net
  **−₹172,092.42 provisional per 100 shares** (Jan–May
  −₹69,821.85, Jun–Oct −₹102,270.57); Skill pool 5,064 trades,
  net **−₹356,884.60 provisional per 100 shares** (Jan–May
  −₹169,971.96, Jun–Oct −₹186,912.64). The Skill pool is roughly
  twice as bad per trade (expectancy **−₹70.47 provisional per
  100 shares**) as the V5 pool (**−₹41.86 provisional per 100
  shares**).
- **The one pocket worth naming — and it still fails the frozen
  test:** V5 signals on high-volatility stock-days (F1b, prior-10-
  day average range ≥ 3%) are positive in Jun–Oct at both exits —
  T10: 254 trades, net **+₹9,221.61 provisional per 100 shares**,
  expectancy +₹36.31; T125: 254 trades, net **+₹8,930.05
  provisional per 100 shares** — but Jan–May for the same filter
  is **−₹27,478.76 provisional per 100 shares** at T10
  (expectancy −₹40.71), which is not near-flat by the frozen
  definition. A filter that only works in the second half, on a
  pool whose high-volatility days shrank from 675 trades in
  Jan–May to 254 in Jun–Oct, is a regime observation, not a
  selection rule. It is recorded below as a November-paper
  *question*, not a survivor.
- **Stacking filters makes it worse, not better.** F6 (ADR ≥ 2% +
  no-event + Nifty-regime alignment) on V5 × T10: 919 trades, net
  **−₹41,003.40 provisional per 100 shares**, negative in both
  halves; on Skill × T10: 1,012 trades, net **−₹84,123.22
  provisional per 100 shares**, also negative in both halves.
  Each layer individually removes some losers; combined, they
  concentrate different losers.
- **Frequency is a non-issue everywhere:** every family still
  trades at least ~3/day and the base pools ~20–25/day, far above
  the user's minimum-2/day floor. Selection was never going to
  fail on frequency — it fails on expectancy.

**Conclusion: no selection layer on the V5 or Skill entry pools
creates a Jan–Oct-positive small-target equity system. Nothing
from this round is proposed for November paper as a primary.**

---

## 1. Families — V5 pool (every net provisional per 100 shares)

### Exit T10 (target 1.0% / stop 0.5%)

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | /day | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 4,111 | 36.9 | 27.9 | −172,092.42 | −41.86 | 20.25 | 1,989 | −69,821.85 | 2,122 | −102,270.57 |
| F1a ADR≥2% | 3,322 | 36.7 | 29.8 | −145,619.15 | −43.83 | 16.36 | 1,769 | −65,426.08 | 1,553 | −80,193.07 |
| F1b ADR≥3% | 929 | 37.2 | 32.4 | −18,257.15 | −19.65 | 4.58 | 675 | −27,478.76 | 254 | **+9,221.61** |
| F2 regime | 1,497 | 36.8 | 29.1 | −53,170.77 | −35.52 | 7.37 | 755 | −40,932.70 | 742 | −12,238.07 |
| F3 morning | 3,519 | 36.8 | 29.5 | −145,892.55 | −41.46 | 17.33 | 1,724 | −54,494.38 | 1,795 | −91,398.17 |
| F3 afternoon | 592 | 37.8 | 18.8 | −26,199.87 | −44.26 | 2.92 | 265 | −15,327.47 | 327 | −10,872.40 |
| F4 LONG only | 1,450 | 36.2 | 28.3 | −70,525.30 | −48.64 | 7.14 | 702 | −17,288.71 | 748 | −53,236.59 |
| F4 SHORT only | 2,661 | 37.3 | 27.7 | −101,567.12 | −38.17 | 13.11 | 1,287 | −52,533.14 | 1,374 | −49,033.98 |
| F5 no-event | 3,025 | 37.9 | 28.6 | −99,964.67 | −33.05 | 14.90 | 1,406 | −42,286.52 | 1,619 | −57,678.15 |
| F5+F1a no-event | 2,396 | 37.4 | 30.6 | −93,804.79 | −39.15 | 11.80 | 1,222 | −39,232.51 | 1,174 | −54,572.28 |
| F5+F1b no-event | 635 | 38.1 | 33.5 | −14,050.17 | −22.13 | 3.13 | 449 | −20,332.34 | 186 | **+6,282.17** |
| F6 stack | 919 | 37.2 | 31.4 | −41,003.40 | −44.62 | 4.53 | 473 | −17,434.96 | 446 | −23,568.44 |

### Exit T125 (target 1.25% / stop 0.5%)

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | /day | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 4,111 | 34.5 | 21.1 | −155,642.34 | −37.86 | 20.25 | 1,989 | −70,567.49 | 2,122 | −85,074.85 |
| F1a ADR≥2% | 3,322 | 34.0 | 22.9 | −131,132.08 | −39.47 | 16.36 | 1,769 | −67,167.26 | 1,553 | −63,964.82 |
| F1b ADR≥3% | 929 | 34.1 | 25.6 | −13,722.76 | −14.77 | 4.58 | 675 | −22,652.81 | 254 | **+8,930.05** |
| F2 regime | 1,497 | 34.5 | 21.7 | −46,471.67 | −31.04 | 7.37 | 755 | −43,402.39 | 742 | −3,069.28 |
| F3 morning | 3,519 | 34.1 | 22.5 | −132,935.96 | −37.78 | 17.33 | 1,724 | −53,605.18 | 1,795 | −79,330.78 |
| F3 afternoon | 592 | 36.8 | 12.7 | −22,706.38 | −38.36 | 2.92 | 265 | −16,962.31 | 327 | −5,744.07 |
| F4 LONG only | 1,450 | 33.8 | 21.9 | −60,072.41 | −41.43 | 7.14 | 702 | −3,654.71 | 748 | −56,417.70 |
| F4 SHORT only | 2,661 | 34.9 | 20.6 | −95,569.93 | −35.92 | 13.11 | 1,287 | −66,912.78 | 1,374 | −28,657.15 |
| F5 no-event | 3,025 | 35.4 | 21.6 | −87,814.75 | −29.03 | 14.90 | 1,406 | −40,114.47 | 1,619 | −47,700.28 |
| F5+F1a no-event | 2,396 | 34.6 | 23.5 | −82,955.73 | −34.62 | 11.80 | 1,222 | −38,227.85 | 1,174 | −44,727.88 |
| F5+F1b no-event | 635 | 35.1 | 27.1 | −9,534.16 | −15.01 | 3.13 | 449 | −16,416.46 | 186 | **+6,882.30** |
| F6 stack | 919 | 34.8 | 23.9 | −36,041.69 | −39.22 | 4.53 | 473 | −18,119.59 | 446 | −17,922.10 |

Reading (all nets in this paragraph provisional per 100 shares):
F1a barely changes anything — most stock-days already range ≥ 2%.
F1b is the only filter that changes the character of the pool
(target-hit rate rises to 32.4% at T10) and the only one with any
positive half, but its Jan–May is decisively negative at both
exits. F2 strict regime alignment improves expectancy slightly
versus base (−₹35.52 vs −₹41.86 at T10) but both halves stay
negative — alignment with yesterday's Nifty bias does not create
an edge. F3 shows no timing edge in either window (morning and
afternoon both lose in both halves). F4 shows no direction edge
over the full year: LONG and SHORT both lose in both halves at
T10 — October's SHORT-side strength was that month, not a rule.

## 2. Families — Skill pool (every net provisional per 100 shares)

### Exit T10 (target 1.0% / stop 0.5%)

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | /day | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 5,064 | 34.2 | 25.6 | −356,884.60 | −70.47 | 24.95 | 2,465 | −169,971.96 | 2,599 | −186,912.64 |
| F1a ADR≥2% | 4,083 | 33.7 | 27.2 | −313,527.35 | −76.79 | 20.11 | 2,188 | −162,756.36 | 1,895 | −150,770.99 |
| F1b ADR≥3% | 1,166 | 34.1 | 29.2 | −61,808.59 | −53.01 | 5.74 | 855 | −57,877.81 | 311 | −3,930.78 |
| F2 regime | 1,641 | 33.2 | 25.9 | −126,931.22 | −77.35 | 8.08 | 836 | −93,295.09 | 805 | −33,636.13 |
| F3 morning | 4,431 | 34.3 | 26.4 | −310,996.71 | −70.19 | 21.83 | 2,139 | −136,126.53 | 2,292 | −174,870.18 |
| F3 afternoon | 633 | 33.3 | 20.2 | −45,887.89 | −72.49 | 3.12 | 326 | −33,845.43 | 307 | −12,042.46 |
| F4 LONG only | 2,375 | 32.5 | 24.6 | −215,242.68 | −90.63 | 11.70 | 1,167 | −100,051.55 | 1,208 | −115,191.13 |
| F4 SHORT only | 2,689 | 35.6 | 26.5 | −141,641.92 | −52.67 | 13.25 | 1,298 | −69,920.41 | 1,391 | −71,721.51 |
| F5 no-event | 3,739 | 34.7 | 26.0 | −253,748.27 | −67.87 | 18.42 | 1,745 | −112,080.53 | 1,994 | −141,667.74 |
| F5+F1a no-event | 2,951 | 34.2 | 27.8 | −225,857.00 | −76.54 | 14.54 | 1,511 | −108,820.20 | 1,440 | −117,036.80 |
| F5+F1b no-event | 808 | 34.9 | 30.1 | −47,484.18 | −58.77 | 3.98 | 570 | −37,134.74 | 238 | −10,349.44 |
| F6 stack | 1,012 | 33.8 | 28.3 | −84,123.22 | −83.13 | 4.99 | 521 | −48,665.69 | 491 | −35,457.53 |

### Exit T125 (target 1.25% / stop 0.5%)

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | /day | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ |
|---|---|---|---|---|---|---|---|---|---|---|
| BASE | 5,064 | 31.7 | 18.8 | −348,883.23 | −68.89 | 24.95 | 2,465 | −172,535.87 | 2,599 | −176,347.36 |
| F1a ADR≥2% | 4,083 | 30.8 | 20.3 | −311,503.91 | −76.29 | 20.11 | 2,188 | −169,498.73 | 1,895 | −142,005.18 |
| F1b ADR≥3% | 1,166 | 30.6 | 22.6 | −57,799.14 | −49.57 | 5.74 | 855 | −52,299.91 | 311 | −5,499.23 |
| F2 regime | 1,641 | 30.8 | 18.8 | −122,820.20 | −74.84 | 8.08 | 836 | −88,824.28 | 805 | −33,995.92 |
| F3 morning | 4,431 | 31.7 | 19.4 | −311,396.88 | −70.28 | 21.83 | 2,139 | −144,313.20 | 2,292 | −167,083.68 |
| F3 afternoon | 633 | 31.8 | 15.0 | −37,486.35 | −59.22 | 2.92 | 326 | −28,222.67 | 307 | −9,263.68 |
| F4 LONG only | 2,375 | 30.3 | 18.4 | −203,960.29 | −85.88 | 11.70 | 1,167 | −91,847.20 | 1,208 | −112,113.09 |
| F4 SHORT only | 2,689 | 32.9 | 19.2 | −144,922.94 | −53.89 | 13.25 | 1,298 | −80,688.67 | 1,391 | −64,234.27 |
| F5 no-event | 3,739 | 32.2 | 18.9 | −245,221.05 | −65.58 | 18.42 | 1,745 | −104,920.29 | 1,994 | −140,300.76 |
| F5+F1a no-event | 2,951 | 31.2 | 20.4 | −222,834.50 | −75.51 | 14.54 | 1,511 | −105,873.70 | 1,440 | −116,960.80 |
| F5+F1b no-event | 808 | 31.2 | 23.4 | −42,538.95 | −52.65 | 3.98 | 570 | −30,356.88 | 238 | −12,182.07 |
| F6 stack | 1,012 | 31.0 | 20.7 | −85,579.87 | −84.57 | 4.99 | 521 | −47,251.16 | 491 | −38,328.71 |

Reading (all nets provisional per 100 shares): the Skill pool
fails everywhere, at roughly double the V5 pool's per-trade loss.
F5 for Skill — the specific re-run the round required — is
**−₹253,748.27 at T10** (3,739 trades), negative in both halves;
removing event days does not rescue Skill either. F1b again
shrinks the loss the most (Jun–Oct T10 only −₹3,930.78 on 311
trades, expectancy −₹12.64) but never reaches positive in either
half. No Skill family is interesting under the frozen rule.

## 3. Split-half per-stock persistence — V5 pool × T10

Per-stock net by half (every figure provisional per 100 shares;
full table in `eq_explore3_persistence_v5_t10.csv`):

| Stock | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ | Jan–Oct net ₹ |
|---|---|---|---|---|---|
| HINDUNILVR | 81 | **+19,369.70** | 86 | −4,528.06 | +14,841.64 |
| ASTRAL | 80 | **+6,594.25** | 78 | **+2,705.70** | +9,299.95 |
| IRCTC | 77 | **+4,038.97** | 68 | **+2,912.65** | +6,951.62 |
| VEDL | 77 | **+2,048.88** | 80 | **+2,113.12** | +4,162.00 |
| HINDCOPPER | 67 | **+2,457.53** | 77 | **+459.87** | +2,917.40 |
| BDL | 79 | +6,309.00 | 86 | −3,846.55 | +2,462.45 |
| PFC | 85 | +3,219.95 | 90 | −2,214.32 | +1,005.63 |
| HINDZINC | 76 | −3,919.92 | 79 | +686.13 | −3,233.79 |
| GODREJCP | 79 | −14,398.90 | 88 | +1,810.38 | −12,588.52 |
| TVSMOTOR | 75 | −32,419.75 | 90 | −19,547.05 | −51,966.80 |
| OBEROIRLTY | 85 | −14,514.55 | 92 | −23,375.85 | −37,890.40 |
| HINDALCO | 79 | −10,142.30 | 78 | −9,064.60 | −19,206.90 |

(Remaining 13 stocks are negative in both halves or small-mixed;
see the CSV.)

- **Pearson correlation between half-1 and half-2 per-stock nets:
  r = +0.564.** That number is real but misleading if read as
  "payers persist": it is carried mostly by the LOSERS — 16 of 25
  stocks are negative in BOTH halves, several heavily (TVSMOTOR
  **−₹51,966.80 provisional per 100 shares** Jan–Oct, OBEROIRLTY
  **−₹37,890.40 provisional per 100 shares**). Bad stocks stay
  bad far more reliably than good stocks stay good.
- **Payers do NOT persist as a class.** Only 4 of 25 stocks are
  positive in both halves: ASTRAL, IRCTC, VEDL, HINDCOPPER —
  combined **+₹23,330.97 provisional per 100 shares** over 619
  trades, against a pool total of **−₹172,092.42 provisional per
  100 shares**. The two names flagged in earlier rounds split:
  ASTRAL persists (positive both halves, above); HINDUNILVR does
  NOT — it is the biggest Jan–May payer (**+₹19,369.70
  provisional per 100 shares**) and a Jun–Oct loser
  (**−₹4,528.06 provisional per 100 shares**). BDL and PFC also
  flip from positive to negative; GODREJCP and HINDZINC flip the
  other way.
- Per the frozen spec, **no stock whitelist is claimed**. The 4
  both-halves-positive names are a November-paper question only —
  and even a hindsight portfolio of exactly those 4 would have
  earned a small fraction of what the other 21 stocks lost, which
  says the pool, not the stock list, is the problem.

## 4. Rejected list (frozen both-halves rule)

Every family below is negative in both halves at both exits on
the stated pool, unless the exception is named — all nets
provisional per 100 shares:

- **V5 pool:** F1a, F2, F3 morning, F3 afternoon, F4 LONG, F4
  SHORT, F5, F5+F1a, F6 — rejected at T10 and T125.
- **V5 pool, single-half exceptions (still rejected — Jan–May is
  decisively negative, not near-flat):** F1b at T10 (Jun–Oct
  +₹9,221.61 vs Jan–May −₹27,478.76), F1b at T125 (Jun–Oct
  +₹8,930.05 vs Jan–May −₹22,652.81), F5+F1b at T10 (Jun–Oct
  +₹6,282.17 vs Jan–May −₹20,332.34), F5+F1b at T125 (Jun–Oct
  +₹6,882.30 vs Jan–May −₹16,416.46). These four cells are the
  same underlying pocket — high-prior-range stock-days in the
  second half — seen through overlapping filters.
- **Skill pool:** ALL families at both exits — rejected, no
  positive half anywhere; the least-bad cell (F1b, T10, Jun–Oct)
  is still −₹3,930.78.
- **Base pools:** V5 and Skill unfiltered — rejected (section 1).

## 5. Honest verdict

1. **No selection layer survives.** Volatility/room, Nifty-regime
   alignment, timing, direction, event exclusion, and their full
   stack were all tested on both pools at both exits with a
   both-halves bar set in advance. None clears it. The V5/Skill
   morning-signal entries on these 25 stocks do not contain a
   hidden profitable subset that any of these knowable-before-
   entry filters can isolate over Jan–Oct 2026.
2. **What the round did establish:** (a) the failure is in the
   entries, not the stock list — per-stock persistence is a
   loser-persistence story (r = +0.564 driven by 16 both-halves
   losers), and the biggest first-half payer (HINDUNILVR) flips
   negative in the second half; (b) high-range stock-days
   (ADR ≥ 3%) are the least-bad pocket and the only one with a
   positive half — worth ONE pre-declared November-paper question
   (does the Jun–Oct high-volatility behaviour repeat live?),
   explicitly not a validated system; (c) the event-window
   penalty from earlier rounds survives inside every family —
   event days remain worst — but excluding them never turns any
   pool positive.
3. **Stage results only.** Nothing here is adopted and nothing
   goes to November paper as a primary on this evidence. If
   November paper is run for stocks at all, the honest candidates
   are questions, not systems: the F1b high-volatility pocket on
   the V5 pool, and the 4 both-halves-positive stocks — both
   pre-declared, both small, both to be judged on November alone.

## Files

- Frozen spec: `stocks_equity_explore3_frozen.md`
- Engine: `stocks_equity_explore3.py`
- Results JSON: `stocks_equity_explore3_results.json`
- Trades: `eq_explore3_v5_trades_T10_janoct.csv`,
  `eq_explore3_v5_trades_T125_janoct.csv`,
  `eq_explore3_skill_trades_T10_janoct.csv`,
  `eq_explore3_skill_trades_T125_janoct.csv`,
  `eq_explore3_v5_f6_trades_T10_janoct.csv`,
  `eq_explore3_skill_f6_trades_T10_janoct.csv`
- Persistence: `eq_explore3_persistence_v5_t10.csv`
- Prior rounds: `stocks_equity_october_systems.md`,
  `stocks_equity_v5_validation_tuning.md`
