# Stocks EQUITY — Round 5: N4-deep (event-reaction deepening) + November paper spec

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums anywhere in this report. Paper only, no orders.
Real money: ₹0.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade flat cost, unless a sentence says otherwise. Spec frozen
before scoring: `stocks_equity_n4deep_frozen.md`. Engine:
`stocks_equity_n4deep.py`.**

Portfolio rule (user, 2026-10-30 19:33 IST): **uncapped** — every
qualifying stock trades, max 1 trade per stock per event per
variant; the minimum-2-valuable/day rule is a floor, not a cap.
Windows: Jan–Oct 2026 = 203 trading days (Jan–May = 99, Jun–Oct =
104, October = 1–28 Oct, 18 days; 29 Oct missing from cache, stated,
not a zero day).

**Declared primary exit for this round: T125** (target +1.25% /
stop −0.5%), declared in the frozen spec BEFORE scoring, because in
round 4 T125 was the only exit at which base N4 was positive in
both halves. T10 (target +1.0% / stop −0.5%) is reported as the
secondary exit for every variant. **Graduation rule (frozen):**
both halves net-positive at T125 on an adequate sample (≥10 trades
total, ≥3 per half). No variant graduates on T10 alone, a single
half, or October alone.

**Reproducibility anchor:** the round-5 engine's BASE variant
reproduces round 4's N4 exactly — 52 trades, T10 net +₹4,319.24 and
T125 net +₹2,924.79 provisional per 100 shares. All variant numbers
below are read against that verified base.

---

## Verdict first — V3 graduates and carries November paper

- **Three variants are both-halves positive at the primary exit
  T125: BASE, V1b, and V3.** Under the frozen tie-break (highest
  Jan–Oct T125 net), the November paper primary is **V3 — the
  combined event-reaction family** (results + single-news reaction
  days, ≥1% trigger by 09:30, entry 09:35): 56 trades, net
  **+₹7,990.43 provisional per 100 shares** at T125, expectancy
  +₹142.69, halves **+₹5,155.13 (34 trades) / +₹2,835.30
  (22 trades)** provisional per 100 shares — the only variant whose
  second half is strongly positive rather than flat, and the only
  one also both-halves positive at T10 (+₹7,837.42 / +₹746.10
  provisional per 100 shares).
- **V1a (trigger ≥0.5%) fails**: the bigger sample (72 trades)
  destroys the second half (−₹3,517.48 provisional per 100 shares
  at T125). Weak reactions are not the same trade.
- **V1b (trigger ≥1.5%) graduates weakly**: both halves positive at
  T125, but the second half is +₹17.32 provisional per 100 shares
  on 18 trades — zero within noise, the same shape as base.
- **V2 (entry delayed to 10:05) fails decisively**: negative in
  both halves at both exits at T125 and T10 (Jan–Oct −₹3,450.35 /
  −₹5,962.26 provisional per 100 shares). The event-reaction edge,
  such as it is, lives in the immediate 09:35 continuation; waiting
  out the first half-hour removes it.
- **V4 (second-day follow-through) fails decisively** at the
  primary exit: −₹10,736.48 provisional per 100 shares, negative in
  both halves. A reaction day that closes in its trigger direction
  does NOT follow through the next day — it gives back.
- **The standing caveat on everything above:** V3's October slice
  is negative (6 trades, −₹530.69 provisional per 100 shares at
  T125), its sample is 56 trades over 10 months, and 52 of the 56
  are results reactions (the 4 single-news trades contribute
  +₹5,065.64 of the T125 total — two GLENMARK targets do heavy
  lifting). Graduation here means "carried to November paper",
  never "adopted". November is results-heavy, which is exactly the
  fresh sample this family needs.

---

## 1. Variant table — PRIMARY exit T125 (target 1.25% / stop 0.5%)

Every net in this table is provisional per 100 shares.

| Variant | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ | Oct n | Oct net ₹ | Both halves + |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| BASE (≥1%, 09:35, results) | 52 | 36.5 | 32.7 | +2,924.79 | +56.25 | 32 | +2,727.65 | 20 | +197.14 | 5 | −361.74 | **YES** (H2 flat) |
| V1a (trigger ≥0.5%) | 72 | 31.9 | 29.2 | +1,091.20 | +15.16 | 43 | +4,608.68 | 29 | **−3,517.48** | 7 | −2,180.99 | NO |
| V1b (trigger ≥1.5%) | 48 | 37.5 | 33.3 | +3,228.65 | +67.26 | 30 | +3,211.33 | 18 | +17.32 | 5 | −361.74 | **YES** (H2 ≈ 0) |
| V2 (entry 10:05) | 52 | 32.7 | 26.9 | −3,450.35 | −66.35 | 32 | −907.72 | 20 | −2,542.63 | 5 | −301.53 | NO |
| **V3 (results + news, ≥1%)** | **56** | **37.5** | **33.9** | **+7,990.43** | **+142.69** | **34** | **+5,155.13** | **22** | **+2,835.30** | 6 | −530.69 | **YES** |
| V4 (day+1 follow-through) | 46 | 26.1 | 21.7 | −10,736.48 | −233.40 | 28 | −4,958.28 | 18 | −5,778.20 | 3 | +538.06 | NO |

## 2. Variant table — secondary exit T10 (target 1.0% / stop 0.5%)

Every net in this table is provisional per 100 shares. T10 creates
no graduates in this round; it is shown because the frozen spec
requires it and because November logs T10 as shadow.

| Variant | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | Jan–May net ₹ | Jun–Oct net ₹ | Oct net ₹ | Both halves + |
|---|---|---|---|---|---|---|---|---|---|
| BASE | 52 | 40.4 | 38.5 | +4,319.24 | +83.06 | +5,641.88 | −1,322.64 | −478.88 | NO |
| V1a | 72 | 34.7 | 33.3 | +1,471.37 | +20.44 | +6,642.97 | −5,171.60 | −2,298.13 | NO |
| V1b | 48 | 41.7 | 39.6 | +4,711.60 | +98.16 | +6,125.56 | −1,413.96 | −478.88 | NO |
| V2 | 52 | 34.6 | 30.8 | −5,962.26 | −114.66 | −3,231.84 | −2,730.42 | +83.36 | NO |
| **V3** | **56** | **42.9** | **41.1** | **+8,583.52** | **+153.28** | **+7,837.42** | **+746.10** | −647.83 | **YES** |
| V4 | 46 | 32.6 | 30.4 | −4,498.82 | −97.80 | −6,462.40 | +1,963.58 | +359.29 | NO |

## 3. Reading, variant by variant (all nets provisional per 100 shares)

- **BASE — graduates, weakly.** Exactly the round-4 shape carried
  into the declared primary exit: a real first half (+₹2,727.65,
  expectancy +₹85.24) and a second half that is +₹197.14 on
  20 trades (expectancy +₹9.86 — flat within noise). It is a
  graduate under the frozen rule, but nobody should mistake its
  second half for evidence of a live edge in Jun–Oct conditions.
- **V1a — rejected.** Lowering the trigger to 0.5% adds 20 trades
  and the additions are poison in the second half: Jun–Oct swings
  from +₹197.14 (base) to −₹3,517.48, and October alone is
  −₹2,180.99 on 7 trades. Sub-1% early moves on reaction days are
  noise, not reactions. The ≥1% bar is doing real work.
- **V1b — graduates, weakest of the three.** Raising the trigger to
  1.5% drops only 4 trades yet lifts the Jan–Oct T125 net to
  +₹3,228.65 — the trades it drops were net-negative — but its
  second half is +₹17.32 (expectancy +₹0.96), statistically zero.
  Concentration in strong reactions helps the total without
  rescuing the second half. Not chosen for November: under the
  frozen tie-break it loses to V3 on Jan–Oct net, and its H2 is
  flat where V3's is +₹2,835.30.
- **V2 — rejected, and informative.** Same 52 triggers, entry
  30 minutes later: the family goes from +₹2,924.79 to −₹3,450.35
  at T125, negative in both halves at both exits. Whatever moves
  on a reaction day after a ≥1% first-15-minutes move, the part
  that pays is the immediate continuation from the 09:30 close.
  A "let it settle" version of this trade does not exist in this
  data.
- **V3 — graduates, strongest, carries November.** Pooling the 4
  single-news reaction trades (GLENMARK 2026-03-04 SHORT target
  +₹2,563.75; WIPRO 2026-04-01 LONG stop −₹136.27; GLENMARK
  2026-08-20 LONG target +₹2,807.11; ITC 2026-10-08 SHORT stop
  −₹168.95, all provisional per 100 shares at T125) onto base N4
  does two things: the Jan–Oct net more than doubles versus base,
  AND the second half becomes genuinely positive (+₹2,835.30,
  expectancy +₹128.88 on 22 trades) instead of flat. Honesty
  requires the flip side in the same paragraph: the improvement
  rests on 4 trades, 2 of them large GLENMARK targets; remove them
  and V3 IS base, with its flat second half. The combined family
  is one event-reaction rule (which is the user's philosophy —
  moves are event-driven, results or news), its sample is still
  thin, and its October is negative. It graduates under the rule
  frozen before scoring; it is not proven.
  A labelled diagnostic (not a rule, no filter applied): at T125
  V3's SHORT side is 35 trades / +₹8,964.26 against LONG 21 trades
  / −₹973.83 provisional per 100 shares — the same short-tilt
  round 4 saw in N4. November paper trades both directions as
  specified.
- **V4 — rejected, decisively.** 46 follow-through trades lose
  −₹10,736.48 at T125 (expectancy −₹233.40, the worst of the
  round), negative in both halves; even at T10 the halves split
  (−₹6,462.40 / +₹1,963.58). The reaction move does not persist
  into a second day in a tradeable way. Its positive October
  (+₹538.06 on 3 trades) is exactly the single-month mirage the
  both-halves rule exists to reject. V4 is not part of the
  November spec in any form, per the frozen spec.

## 4. November paper — what was frozen (Part B)

**File: `stocks_n4_november_paper_spec.md`; log:
`stocks_n4_november_paper_log.csv` (header only). No cron or
schedule was created — scheduling is handled separately.**

The paper system is **V3 at T125, with T10 logged as shadow** on
every trade:

- Events: results + single-news (management change, large order,
  FDA approval, block deal, sector policy, pricing, corporate
  action; standalone dividends excluded) from the November
  watchlist PLUS a daily exchange-filing check for all 25 stocks.
- Reaction day: first trading day the outcome is known before the
  open (after-hours / non-trading-day filing → next trading day;
  pre-open filing → same day; intraday filing → next trading day).
- Trigger: |close of 09:25 bar ÷ previous close − 1| ≥ 1.0% on the
  reaction day; direction = sign of the move; entry = close of
  the 09:30 bar (recorded 09:35); exit scan from the next bar,
  stop before target, 15:10 square-off.
- Max 1 trade per stock per event; **all** qualifying trades taken
  (no portfolio cap). No-trigger reaction days are logged as
  `no_trigger` rows so the month's event count is auditable.
- Known November map at freeze time: NTPC reaction 2 Nov; ITC +
  NATIONALUM results 2 Nov; NHPC 4 Nov; GLENMARK + PFC 5 Nov;
  HINDALCO 6 Nov (reaction Mon 9 Nov); TATASTEEL 7 Nov (reaction
  Mon 9 Nov); KALYANKJIL 10 Nov; OIL 12 Nov; BDL 14 Nov (reaction
  Mon 16 Nov); IRCTC 17/18 Nov.
- **No re-tuning during November.**
- Month-end verdict on net + win rate + trade count together at
  T125, and — stated in the spec in so many words — **a positive
  November does not adopt the system alone**: the Jan–Oct record
  behind it is in-sample, October-negative, and 56 trades thin;
  November's verdict is "continue / stop", not "adopt".

## 5. Files

- Frozen deep spec (before scoring):
  `stocks_equity_n4deep_frozen.md`
- This report: `stocks_equity_n4deep.md`
- Engine: `stocks_equity_n4deep.py`
- Results JSON: `stocks_equity_n4deep_results.json`
- Trades: `eq_n4deep_base_trades_T125_janoct.csv`,
  `eq_n4deep_base_trades_T10_janoct.csv`,
  `eq_n4deep_v1a_trades_T125_janoct.csv`,
  `eq_n4deep_v1a_trades_T10_janoct.csv`,
  `eq_n4deep_v1b_trades_T125_janoct.csv`,
  `eq_n4deep_v1b_trades_T10_janoct.csv`,
  `eq_n4deep_v2_trades_T125_janoct.csv`,
  `eq_n4deep_v2_trades_T10_janoct.csv`,
  `eq_n4deep_v3_trades_T125_janoct.csv`,
  `eq_n4deep_v3_trades_T10_janoct.csv`,
  `eq_n4deep_v4_trades_T125_janoct.csv`,
  `eq_n4deep_v4_trades_T10_janoct.csv`
- November paper: `stocks_n4_november_paper_spec.md`,
  `stocks_n4_november_paper_log.csv`
- Prior round: `stocks_equity_native4.md`,
  `stocks_equity_native4_frozen.md`
