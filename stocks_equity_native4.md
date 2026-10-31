# Stocks EQUITY — Exploration Round 4: stock-native entry signals

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums anywhere in this report. Paper only, no orders.
Real money: ₹0.**
**Every rupee figure in this report is provisional per 100 shares,
₹40/trade flat cost, unless a sentence says otherwise. Spec frozen
before scoring: `stocks_equity_native4_frozen.md`. Engine:
`stocks_equity_native4.py`.**

Portfolio rule (user, 2026-10-30 19:33 IST): **uncapped** — every
qualifying stock trades, max 1 trade per stock per day per family;
the minimum-2-valuable/day rule is a floor, not a cap. Windows:
Jan–Oct 2026 = 203 trading days (Jan–May = 99, Jun–Oct = 104,
October = 1–28 Oct, 18 days; 29 Oct missing from cache, stated,
not a zero day). Survivor rule (frozen): net positive at the
primary exit in **both** halves. N5 (first-hour range extreme fade)
was excluded in the frozen spec and was not run.

Exits (frozen, identical for all families): **T10** target +1.0% /
stop −0.5% (primary); **T125** target +1.25% / stop −0.5%
(secondary). Stop checked before target on the same candle;
15:10 square-off.

---

## Verdict first — NO survivor; no union scored

- **Zero of the seven families is positive in both halves at the
  primary exit T10.** Per the frozen union rule (two or more
  survivors required), **no union was scored**.
- The transplanted-index-entry failure of rounds 1–3 is therefore
  not the whole story: the stock's own gap, its own opening range,
  and (mostly) its own reaction day also fail the both-halves bar
  at a 1% target / 0.5% stop. Continuation loses outright; the
  opening-range breakout is the worst family tested in any round.
- **Two near-misses, reported as observations only:**
  - **N4 results-reaction momentum** is the only family with a
    positive full-year net at T10: 52 trades, net **+₹4,319.24
    provisional per 100 shares**, expectancy **+₹83.06 provisional
    per 100 shares**. But the halves split the wrong way: Jan–May
    **+₹5,641.88 provisional per 100 shares** (32 trades) against
    Jun–Oct **−₹1,322.64 provisional per 100 shares** (20 trades).
    It fails the frozen rule. (At the secondary exit T125 it is
    positive in both halves — +₹2,727.65 and +₹197.14 provisional
    per 100 shares — but the Jun–Oct half there is +₹9.86
    expectancy on 20 trades, i.e. flat within noise, and the frozen
    spec does not let a secondary exit create a survivor.)
  - **N2a gap fade** has a spectacular October — 61 trades, 50.8%
    win rate, net **+₹17,321.38 provisional per 100 shares** — and a
    Jun–Oct half that is barely above zero (**+₹110.44 provisional
    per 100 shares** on 343 trades, expectancy +₹0.32), against a
    Jan–May half of **−₹15,169.99 provisional per 100 shares**.
    October is one month inside a losing year — the same trap that
    round 2 documented for V5. Observation only.
- **N4b single-news reaction momentum** posted positive halves
  (+₹2,195.54 and +₹2,068.74 provisional per 100 shares) on a total
  of **4 trades** — below the frozen 10-trade minimum sample, so it
  is labelled insufficient-sample and cannot be a survivor. Three
  of its four trades hit the target; that is a curiosity, not
  evidence.

**Conclusion: nothing from round 4 is proposed for November paper
as a primary. The honest open question is N4 (below).**

---

## 1. Family table — primary exit T10 (target 1.0% / stop 0.5%)

Every net in this table is provisional per 100 shares.

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | /day | Jan–May n | Jan–May net ₹ | Jun–Oct n | Jun–Oct net ₹ | Oct n | Oct net ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| N1a gap cont. ≥1% | 464 | 32.1 | 30.4 | −40,495.14 | −87.27 | 2.29 | 287 | −25,567.09 | 177 | −14,928.05 | 40 | −8,965.80 |
| N1b gap cont. ≥2% | 130 | 29.2 | 28.5 | −6,410.56 | −49.31 | 0.64 | 87 | −2,638.82 | 43 | −3,771.74 | 5 | +213.28 |
| N2a gap fade ≥1% | 959 | 35.1 | 33.0 | −15,059.55 | −15.70 | 4.72 | 616 | −15,169.99 | 343 | +110.44 | 61 | **+17,321.38** |
| N2b gap fade ≥2% | 292 | 35.6 | 34.6 | −11,253.50 | −38.54 | 1.44 | 221 | −5,185.13 | 71 | −6,068.37 | 9 | −870.72 |
| N3 stock ORB | 2,437 | 35.3 | 25.6 | −165,554.54 | −67.93 | 12.00 | 1,161 | −86,868.95 | 1,276 | −78,685.59 | 251 | −8,056.76 |
| N4 results reaction | 52 | 40.4 | 38.5 | **+4,319.24** | **+83.06** | 0.26 | 32 | **+5,641.88** | 20 | −1,322.64 | 5 | −478.88 |
| N4b single-news reaction | 4 | 75.0 | 75.0 | +4,264.28 | +1,066.07 | 0.02 | 2 | +2,195.54 | 2 | +2,068.74 | 1 | −168.95 |

## 2. Family table — secondary exit T125 (target 1.25% / stop 0.5%)

Every net in this table is provisional per 100 shares. T125 is
reported per the frozen spec; it does not create survivors.

| Family | Trades | Win % | Tgt % | Net ₹ | Exp ₹ | Jan–May net ₹ | Jun–Oct net ₹ | Oct net ₹ |
|---|---|---|---|---|---|---|---|---|
| N1a gap cont. ≥1% | 464 | 28.2 | 24.4 | −46,751.69 | −100.76 | −27,832.32 | −18,919.37 | −8,054.17 |
| N1b gap cont. ≥2% | 130 | 26.2 | 24.6 | −4,629.34 | −35.61 | −1,273.47 | −3,355.87 | +417.59 |
| N2a gap fade ≥1% | 959 | 30.9 | 26.0 | −29,074.47 | −30.32 | −23,280.37 | −5,794.10 | +23,305.11 |
| N2b gap fade ≥2% | 292 | 31.2 | 28.4 | −15,971.18 | −54.70 | −10,793.10 | −5,178.08 | −730.64 |
| N3 stock ORB | 2,437 | 32.3 | 18.8 | −170,817.29 | −70.09 | −108,303.18 | −62,514.11 | −783.62 |
| N4 results reaction | 52 | 36.5 | 32.7 | +2,924.79 | +56.25 | **+2,727.65** | **+197.14** | −361.74 |
| N4b single-news reaction | 4 | 50.0 | 50.0 | +5,065.64 | +1,266.41 | +2,427.48 | +2,638.16 | −168.95 |

---

## 3. Reading, family by family (all nets provisional per 100 shares)

- **N1 gap continuation — rejected, decisively.** Trading WITH an
  overnight gap loses in both halves at both gap thresholds and
  both exits. The ≥1% version is the second-worst family of the
  round (−₹40,495.14 at T10); its SHORT side alone is −₹34,894.94
  on 252 trades. Bigger gaps (≥2%) lose less per trade but still
  lose in both halves. Whatever a ≥1% gap means on these stocks,
  it does not mean "more of the same today".
- **N2 gap fade — rejected under the frozen rule; the round's
  loudest observation.** Fading the gap is far better than
  continuing it (a swing of roughly ₹25,000 versus N1a at T10 on
  near-mirror entries), and at T10 its Jun–Oct half is +₹110.44 —
  statistically zero — while October alone is +₹17,321.38. The
  monthly split shows why that cannot be trusted: at T10 the fade
  loses in six of the other nine months (Jan −₹14,370.61,
  Apr −₹11,347.19, Aug −₹11,012.80). At the ≥2% threshold (N2b)
  the fade loses in both halves outright. One hot month is not an
  edge; it is recorded as a November-paper *question* only.
- **N3 stock ORB — rejected, worst family of the round.** Even with
  the frozen room conditions (OR width ≤ 1.5% of price AND
  prior-10-day ADR ≥ 2%, the condition round 3's F1 pocket
  motivated), the stock's own opening-range breakout loses
  −₹165,554.54 at T10, negative in both halves, both directions
  (LONG −₹69,137.96 on 1,091 trades; SHORT −₹96,416.58 on 1,346
  trades), at 12.00 trades/day. Frequency was never the problem;
  expectancy is −₹67.93 per trade. Adding "room to travel" to a
  breakout entry does not create an edge on these stocks.
- **N4 results-reaction momentum — near-miss, the round's only
  positive full-year family.** Trading WITH the reaction-day move
  (≥1% by 09:30, entry at the 09:30 close) is the sole family whose
  sign matches the user's event philosophy over the full year at
  T10 (+₹4,319.24, expectancy +₹83.06 — the best expectancy of any
  family in any of rounds 1–4 at this exit). But it is carried by
  Jan–May (+₹5,641.88 on 32 trades); Jun–Oct is −₹1,322.64 on 20
  trades, and October itself is −₹478.88 on 5 trades. A labelled
  diagnostic (not a rule): the positive side is SHORT reactions —
  33 trades, +₹5,212.88 — while LONG reactions are −₹893.64 on 19
  trades; splitting 52 trades further would be hindsight, and the
  frozen rule already failed, so no sub-filter is claimed. Sample
  size is the second problem: 52 trades in 10 months (0.26/day) is
  a thin base — reaction days with a ≥1% early move are rare.
- **N4b single-news reaction — insufficient sample.** 10 qualifying
  single-news events in the calendar produced only 4 trades with a
  ≥1% move by 09:30: GLENMARK 2026-03-04 SHORT, target,
  +₹2,043.00; WIPRO 2026-04-01 LONG, target, +₹152.54; GLENMARK
  2026-08-20 LONG, target, +₹2,237.69; ITC 2026-10-08 SHORT, stop,
  −₹168.95 (all provisional per 100 shares). Encouraging shape,
  unusable n. It cannot be a survivor under the frozen spec.

## 4. Rejected list (frozen both-halves rule, primary exit T10)

All nets provisional per 100 shares:

- **N1a / N1b (gap continuation)** — negative in both halves at
  both thresholds and both exits. Rejected.
- **N2a (gap fade ≥1%)** — Jan–May −₹15,169.99; Jun–Oct +₹110.44
  is zero within noise and is October-driven (+₹17,321.38 of it in
  one month). Fails the both-halves rule. Rejected as a system;
  retained as an observation.
- **N2b (gap fade ≥2%)** — negative in both halves. Rejected.
- **N3 (stock ORB)** — negative in both halves, both directions,
  both exits; worst expectancy of any high-frequency family
  tested. Rejected.
- **N4 (results-reaction momentum)** — positive full-year
  (+₹4,319.24) but Jun–Oct −₹1,322.64 at T10. Fails the
  both-halves rule. Rejected as a survivor; retained as the
  round's one open question (section 5).
- **N4b (single-news reaction)** — 4 trades, below the frozen
  10-trade minimum sample. Not scored as a candidate. Rejected
  on sample, not on sign.
- **Union** — not scored: fewer than two families survived, per
  the frozen union rule.

## 5. Honest verdict

1. **No stock-native family survives either.** Four rounds have now
   tested, on the same 25 stocks and the same both-halves bar:
   transplanted index entries (rounds 1–2), every selection layer
   on those entries (round 3), and the stock's own gap, opening
   range, and reaction day (round 4). At a 1% target / 0.5% stop
   with ₹40/trade costs, none produces a positive expectancy in
   both halves of Jan–Oct 2026. The common thread is not the signal
   source — it is that a 2:1 %-exit on 5-minute stock moves pays
   the stop too often: target-hit rates sit at 25–39% across every
   family in this round, below the ~34% breakeven the payoff and
   costs demand on lower-priced names, and win rates at 29–40%.
2. **What round 4 did establish:** (a) gap CONTINUATION is simply
   wrong on these stocks — the fade beats it by a wide margin on
   near-identical entries, even though the fade itself does not
   clear the bar; (b) the opening-range breakout, the most obvious
   stock-native momentum entry, is the worst of all — the ADR
   "room" condition does not rescue breakout entries; (c) the
   reaction day is the only place a positive full-year expectancy
   appears at all (+₹83.06 per trade provisional per 100 shares
   for N4 at T10), which supports the user's "moves are
   event-driven" premise directionally — but its second half is
   negative and its sample is 52 trades, so it is a question, not
   a system.
3. **Stage results only.** Nothing here is adopted and nothing
   goes to November paper as a primary. If November paper is run
   for stocks at all, the honest pre-declared questions from all
   four rounds are: N4 results-reaction momentum (does the
   Jan–May behaviour repeat live, on fresh reaction days?), the
   N2a gap fade's October behaviour, and round 3's F1b
   high-volatility pocket — each small, each judged on November
   alone, none of them a validated system.

## Appendix — N4 October trades, trade by trade (observation only)

No family survived, so there is no survivor October table; N4's
five October trades are listed because N4 is the round's near-miss.
Every figure provisional per 100 shares.

| Date | Stock | Direction | Entry ₹ (09:35) | Exit ₹ | Exit time | Exit reason | Net ₹ | Reaction move by 09:30 |
|---|---|---|---|---|---|---|---|---|
| 2026-10-16 | WIPRO | LONG | 180.14 | 181.94 | 10:00 | target | +140.14 | +2.90% |
| 2026-10-19 | HDFCBANK | SHORT | 716.50 | 720.08 | 09:40 | stop | −398.25 | −2.00% |
| 2026-10-21 | HINDZINC | LONG | 549.65 | 546.90 | 09:35 | stop | −314.82 | +2.41% |
| 2026-10-27 | RECLTD | SHORT | 288.45 | 285.57 | 09:35 | target | +248.45 | −3.39% |
| 2026-10-28 | VEDL | LONG | 228.80 | 227.66 | 10:20 | stop | −154.40 | +1.57% |

(Two of the five exits print exit time 09:35 because the stop or
target was touched inside the very first bar after entry; the exit
scan starts on the bar after the entry bar, per the frozen spec.)
October total for N4 at T10: 5 trades, 40.0% win rate, net
**−₹478.88 provisional per 100 shares**.

## Files

- Frozen spec: `stocks_equity_native4_frozen.md`
- Engine: `stocks_equity_native4.py`
- Results JSON: `stocks_equity_native4_results.json`
- Trades: `eq_native4_n1a_trades_T10_janoct.csv`,
  `eq_native4_n1a_trades_T125_janoct.csv`,
  `eq_native4_n1b_trades_T10_janoct.csv`,
  `eq_native4_n1b_trades_T125_janoct.csv`,
  `eq_native4_n2a_trades_T10_janoct.csv`,
  `eq_native4_n2a_trades_T125_janoct.csv`,
  `eq_native4_n2b_trades_T10_janoct.csv`,
  `eq_native4_n2b_trades_T125_janoct.csv`,
  `eq_native4_n3_trades_T10_janoct.csv`,
  `eq_native4_n3_trades_T125_janoct.csv`,
  `eq_native4_n4_trades_T10_janoct.csv`,
  `eq_native4_n4_trades_T125_janoct.csv`,
  `eq_native4_n4b_trades_T10_janoct.csv`,
  `eq_native4_n4b_trades_T125_janoct.csv`
- Prior rounds: `stocks_equity_october_systems.md`,
  `stocks_equity_v5_validation_tuning.md`,
  `stocks_equity_explore3.md`
