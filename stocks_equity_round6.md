# Stocks EQUITY — Round 6 — V5 re-entry: chain diagnostic, chain filters, cost/size sensitivity — 2026-10-30

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0. No live trades
were placed.**
**Every rupee figure is provisional per 100 shares unless a table
explicitly states a different share size. Gross = before the frozen
₹40/trade flat cost; net = gross − ₹40/trade. Spec frozen before
Part B scoring: `stocks_equity_round6_frozen.md` (Part A diagnostic
ran first, as specified, and its break is stated in that spec).**

Pool: the frozen V5 re-entry trade chains, Jan–Oct 2026 (203 days,
October = 1–28 Oct), 25 stocks, exits T10 (target +1.0% / stop
−0.5%) and T125 (+1.25% / −0.5%). Skill and (lA) are out of this
round — gross-negative under re-entry. Chain `round` = the entry's
sequence number within its stock-day, taken from the re-entry CSVs.

---

## Verdict first — NO survivor at ₹40/trade. The gross edge is real, located, and smaller than the frozen cost.

- **Where the edge lives (Part A):** round 1 of a chain has ~zero
  gross expectancy; **round 2 is the only strongly gross-positive
  round in both halves at both exits**; rounds 3–4 are
  gross-negative. The edge is in the *second* entry on a stock that
  has already moved once that day — not in first signals, and not
  in chasing beyond two.
- **Best filter (Part B):** R5a = chain cap 2 + ADR≥3% stock-days,
  at T125: gross expectancy **+₹26.25 provisional per 100 shares**
  per trade, gross-positive in both halves (+₹29.78 / +₹15.99),
  October net positive — but net at ₹40 is still **−₹19,541.85
  provisional per 100 shares** over Jan–Oct, negative in both
  halves. No Part B variant is net-positive in both halves at ₹40.
  **Survivor rule: failed by everything.**
- **What decides it (Part C):** R5a × T125 breaks even at a flat
  cost of **₹26.25 per trade at 100 shares**, and is net-positive
  in *both* halves only if the flat-equivalent cost is below
  ~₹16/trade at 100 shares — or, equivalently, at a position size
  above ~**152 shares** if the cost really were ₹40 flat per trade
  regardless of size. **The user's actual broker charges are
  unknown and were not invented anywhere in this round** — that
  single unknown is now the difference between this structure
  failing and passing, and it cannot be resolved from backtest
  data. It is stated as a gap, not filled.

---

## Part A — chain diagnostic (no new rules)

Expectancy per trade, provisional per 100 shares. Gross first,
net in brackets.

### By chain round

**T10** (7,202 trades):

| Round | n (all) | Gross exp all | Gross exp Jan–May | Gross exp Jun–Oct | Net exp all |
|---|---|---|---|---|---|
| 1 | 4,111 | −1.86 | +4.90 | −8.20 | −41.86 |
| **2** | **1,766** | **+53.74** | **+66.01** | **+38.09** | **+13.74** |
| 3 | 696 | −48.59 | −67.31 | −19.23 | −88.59 |
| 4 | 304 | −18.97 | −9.98 | −35.28 | −58.97 |
| 5+ | 325 | +33.74 | +10.17 | +110.96 | −6.26 |

**T125** (6,625 trades):

| Round | n (all) | Gross exp all | Gross exp Jan–May | Gross exp Jun–Oct | Net exp all |
|---|---|---|---|---|---|
| 1 | 4,111 | +2.14 | +4.52 | −0.09 | −37.86 |
| **2** | **1,578** | **+47.44** | **+73.51** | **+13.63** | **+7.44** |
| 3 | 523 | −13.61 | −35.64 | +23.76 | −53.61 |
| 4 | 202 | −7.51 | +27.38 | −77.81 | −47.51 |
| 5+ | 211 | +26.45 | −20.09 | +180.32 | −13.55 |

Reading: round 2 alone is net-positive Jan–Oct at both exits
(T10 net exp +₹13.74, T125 +₹7.44, provisional per 100 shares) —
but a round-2 trade cannot be taken without the round-1 trade
preceding it in live trading, so the tradable unit is the chain,
not the round. Rounds 3+ in aggregate are gross-negative at both
exits (T10 ≈ −₹28.6k gross, T125 ≈ −₹3.1k gross, provisional per
100 shares); the round-5+ pockets rest on 49–325 trades with
opposite signs across halves and are treated as noise.

### By previous exit (re-entries only, gross expectancy, provisional per 100 shares)

| Previous exit | T10 n | T10 Jan–May | T10 Jun–Oct | T125 n | T125 Jan–May | T125 Jun–Oct |
|---|---|---|---|---|---|---|
| target | 1,074 | −9.16 | +91.13 | 670 | −25.05 | +87.92 |
| stop | 2,017 | +36.25 | −10.35 | 1,844 | +59.55 | −5.00 |
| square_off | 0 | — | — | 0 | — | — |

No re-entry follows a square_off (square-off is end-of-day by
construction). The two splits are mirror images across halves —
after-target re-entries pay only in Jun–Oct, after-stop re-entries
pay only in Jan–May — so neither is a both-halves rule on its own.

### By re-entry time of day (gross expectancy, provisional per 100 shares)

| Entry time | T10 n | T10 Jan–May | T10 Jun–Oct | T125 n | T125 Jan–May | T125 Jun–Oct |
|---|---|---|---|---|---|---|
| 09:35–10:30 | 980 | +59.63 | +58.18 | 774 | +70.85 | +70.06 |
| 10:30–12:00 | 1,836 | +1.56 | +9.06 | 1,522 | +19.07 | −12.35 |
| 12:00–13:30 | 159 | +56.99 | +2.15 | 129 | +91.46 | +52.94 |
| 13:30–15:10 | 116 | −65.99 | +7.29 | 89 | −59.20 | +38.08 |

Morning re-entries (before 10:30) are gross-strong in both halves
at both exits and net-positive Jan–Oct (T10 net exp +₹19.08,
T125 +₹30.55, provisional per 100 shares). Per the frozen spec
this is a **diagnostic only — not scored as a filter this round**;
it is the clearest single question for a later round.

---

## Part B — filters on the re-entry pool

R2 (break-informed cap): Part A's break selects cap = 2, identical
by construction to R1a — scored once, labelled R1a/R2, no separate
numbers invented. R5 stacks were scored per the spec's ex-ante
conditions (both R3 and R4 were gross-positive in both halves as
whole pools at both exits, so R5a/R5b/R5c all scored).

### T125 (all figures provisional per 100 shares)

| Variant | Trades | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|
| Unfiltered | 6,625 | +12.17 | −184,394.90 | −77,033.23 | −107,361.67 | +11,875.06 |
| R1a/R2 cap 2 | 5,689 | +14.70 | −143,903.56 | −40,710.61 | −103,192.95 | +5,066.33 |
| R1b cap 3 | 6,212 | +12.32 | −171,939.06 | −65,594.80 | −106,344.26 | +11,959.03 |
| R3 after-target only | 4,585 | +5.90 | −156,342.37 | −83,827.24 | −72,515.13 | +20,551.73 |
| R4 ADR≥3% | 1,894 | +17.05 | −43,459.84 | −36,543.68 | −6,916.16 | +5,602.46 |
| **R5a cap2 + ADR≥3%** | **1,421** | **+26.25** | **−19,541.85** | **−10,801.11** | **−8,740.74** | **+3,975.08** |
| R5b cap2 + R3 | 4,538 | +7.78 | −146,230.14 | −77,331.48 | −68,898.66 | +21,614.27 |
| R5c cap2 + R3 + ADR≥3% | 1,078 | +17.75 | −23,982.96 | −25,810.67 | +1,827.71 | +3,410.58 |

### T10 (all figures provisional per 100 shares)

| Variant | Trades | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|
| Unfiltered | 7,202 | +8.14 | −229,444.79 | −106,904.40 | −122,540.39 | +13,859.32 |
| R1a/R2 cap 2 | 5,877 | +14.85 | −147,824.04 | −44,072.03 | −103,752.01 | +16,812.85 |
| R1b cap 3 | 6,573 | +8.13 | −209,483.51 | −89,680.49 | −119,803.02 | +17,728.61 |
| R3 after-target only | 4,860 | +7.76 | −156,690.44 | −84,746.12 | −71,944.32 | +34,140.48 |
| R4 ADR≥3% | 2,100 | +7.77 | −67,677.07 | −61,888.36 | −5,788.71 | +6,758.21 |
| **R5a cap 2 + ADR≥3%** | **1,471** | **+21.31** | **−27,493.49** | **−26,458.60** | **−1,034.89** | **+7,356.05** |
| R5b cap 2 + R3 | 4,743 | +7.89 | −152,311.66 | −73,597.73 | −78,713.93 | +29,857.17 |
| R5c cap 2 + R3 + ADR≥3% | 1,134 | +17.76 | −25,220.65 | −31,865.03 | +6,644.38 | +7,494.75 |

Reading:
- The chain cap works as Part A said: cap 2 raises gross
  expectancy (T125 +12.17 → +14.70; T10 +8.14 → +14.85,
  provisional per 100 shares); cap 3 gives most of it back by
  readmitting round 3.
- R3 (winner-momentum chains) does **not** help as a pool filter:
  gross expectancy falls below unfiltered at both exits — the
  always-taken round-1 trades dilute it, and Part A's mirror-image
  halves warned of exactly this.
- ADR≥3% is the strongest single filter at T125 (gross exp
  +₹17.05 provisional per 100 shares, both halves gross-positive)
  and the stack R5a is the best structure at both exits: gross
  exp +₹26.25 (T125) / +₹21.31 (T10) provisional per 100 shares,
  gross-positive in both halves, October net-positive at ₹40.
- Still: **no variant is net-positive in both halves at ₹40.**
  The closest is R5a × T125, roughly −₹10.8k / −₹8.7k per half on
  1,421 trades, provisional per 100 shares. Per the survivor rule,
  R5a goes to Part C — not adopted, not binned.

---

## Part C — cost & size sensitivity

Flat-cost ladder (net, provisional per 100 shares):

**R5a (cap 2 + ADR≥3%) × T125 — 1,421 trades, gross +₹37,298.15:**

| Flat cost/trade | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ |
|---|---|---|---|
| ₹40 | −19,541.85 | −10,801.11 | −8,740.74 |
| ₹30 | −5,331.85 | −231.11 | −5,100.74 |
| ₹20 | +8,878.15 | +10,338.89 | −1,460.74 |
| ₹10 | +23,088.15 | +20,908.89 | +2,179.26 |

**Breakeven flat cost at 100 shares: ₹26.25/trade** (= gross
expectancy). Both halves turn net-positive only below ~₹16/trade
(the Jun–Oct half's own breakeven is ₹15.99).

**R5a × T10 — 1,471 trades, gross +₹31,346.51, breakeven ₹21.31:**
both halves net-positive only below ~₹15.75/trade; at ₹10/trade,
net Jan–Oct +₹16,636.51 provisional per 100 shares
(+₹6,271.40 / +₹10,365.11 by half).

**Unfiltered V5 × T125 — 6,625 trades, gross +₹80,605.10,
breakeven ₹12.17:** even at ₹10/trade the Jun–Oct half stays
negative (net Jan–Oct +₹14,355.10 = Jan–May +₹28,146.77 /
Jun–Oct −₹13,791.67, provisional per 100 shares). The unfiltered
pool does not pass at any cost in the ladder; the filtered R5a
structure is what carries the gross edge.

Size sensitivity — **assuming the flat cost stays ₹40 per TRADE
regardless of position size** (rupee totals at the stated size,
NOT per-100-shares figures):

| Variant | Net at 200 sh | Net at 500 sh | Breakeven size at ₹40 flat |
|---|---|---|---|
| R5a × T125 | +₹17,756.30 | +₹129,650.75 | ≈152 shares |
| R5a × T10 | +₹3,853.02 | +₹97,892.55 | ≈188 shares |
| Unfiltered × T125 | −₹103,789.80 | +₹138,025.50 | ≈329 shares |

**Simplification flags, stated plainly:** the size table holds
cost at ₹40/trade while gross scales linearly — real intraday
equity charges are a mix (flat brokerage is common, but GST,
exchange/SEBI charges and stamp duty partly scale with turnover,
and slippage grows with size; there is no delivery STT on
intraday). **The user's actual broker and charges are unknown;
nothing here assumes or invents them.** If the user's real
flat-equivalent cost per trade at 100 shares is below ~₹16, R5a ×
T125 is net-positive in both halves in-sample; if it is near the
frozen ₹40 at 100-share size, it fails. That question is now a
fact about the user's account, not about the backtest.

---

## Verdict

1. **No survivor at the frozen basis.** Every Part B variant is
   net-negative in both halves at ₹40/trade per 100 shares.
   Nothing is adopted; nothing goes to November paper from this
   round (N4-V3's frozen November paper is unaffected).
2. **The gross edge is located and structured:** V5 re-entry,
   capped at 2 entries per stock-day, on ADR≥3% stock-days, at
   the 1.25% target — gross +₹26.25 provisional per 100 shares
   per trade, both halves, October net-positive even at ₹40.
3. **The binding constraint is cost-vs-size, and the deciding
   input is missing:** the user's real per-trade charges. Below
   ~₹16/trade flat-equivalent at 100 shares (or above ~152
   shares/trade at a true ₹40 flat), R5a × T125 passes the
   both-halves net test in-sample; at the frozen ₹40/100-shares
   basis it does not.
4. **Open diagnostic for a later round (not scored here):**
   morning re-entries (before 10:30) are the single strongest
   gross pocket in Part A — gross-positive both halves at both
   exits, net-positive Jan–Oct on their own.

## Files

- Spec (frozen before Part B scoring; Part A break stated inside):
  `stocks_equity_round6_frozen.md`
- Engine/analysis: `stocks_equity_round6.py`
  (`partA` and `partBC` modes)
- Part A JSON: `stocks_equity_round6_partA.json`
- Results JSON: `stocks_equity_round6_results.json`
- Best-variant trade dumps:
  `eq_round6_v5_T125_best_R5a_cap2_adr3.csv`,
  `eq_round6_v5_T10_best_R5c_cap2_r3_adr3.csv`
  (best by the spec's frozen selection rule — highest net Jan–Oct
  per exit; the gross-expectancy leader at both exits is R5a,
  which Part C covers for both exits)

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.
