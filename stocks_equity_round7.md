# Stocks EQUITY — Round 7 — Morning re-entry filters (M1–M5) on the V5 re-entry pool — 2026-10-30

**EQUITY CASH intraday only. LONG/SHORT language only — no options,
no premiums. Paper only, no orders. Real money: ₹0. No live trades
were placed.**
**Every rupee figure is provisional per 100 shares. Gross = before
the frozen ₹40/trade flat cost; net = gross − ₹40/trade. Spec frozen
before scoring: `stocks_equity_round7_frozen.md`. Pool: the frozen
V5 re-entry trade chains, Jan–Oct 2026 (203 days, October = 1–28
Oct), 25 stocks, exits T10 (target +1.0% / stop −0.5%) and T125
(+1.25% / −0.5%). N4-V3 and its November spec were not touched.**

---

## Verdict first — NO survivor. The morning pocket does not survive as a tradable filter at ₹40/trade.

- The Round 6 diagnostic was real but narrow: it described
  **re-entries only** (chain round ≥ 2) entered before 10:30. Every
  variant in this round that must also carry round-1 entries (M1,
  M2, and the stacks built on them) is diluted by those round-1
  entries — round 1 has ~zero gross expectancy at any time of day —
  and lands net-negative in both halves at both exits.
- **M3 (round-2-only)** is net-positive Jan–Oct at both exits but
  **fails the both-halves rule**: its Jun–Oct half is net-negative
  at both exits (T10 −₹1,481.44 provisional per 100 shares — a miss
  by ₹1.91/trade; T125 −₹18,118.10). It is also a pool statistic,
  not a tradable rule: a live chain cannot reach round 2 without
  taking round 1, and the tradable chain form (cap 2) already
  failed in Round 6.
- **M5 (morning + cap 2 + ADR≥3%)** is the mirror image of R5a:
  net-positive Jan–Oct at both exits and strongly net-positive
  Jun–Oct, but Jan–May net-negative at both exits. The morning
  restriction concentrates the ADR edge into the second half
  instead of spreading it across both.
- Per the frozen rule, concentration checks and October trade
  lists are produced only for a both-halves pass. **No variant
  passed, so none are claimed**; October figures are shown in the
  tables as context (every variant is October net-positive at T10,
  continuing October's outlier pattern from earlier rounds).

Engine check: M3 reproduces Round 6 Part A's round-2 rows exactly
at both exits (trades, gross and net totals, both halves) — the
filter machinery is anchored to the published Round 6 numbers.

---

## Variant tables (all figures provisional per 100 shares)

### T10 (target +1.0% / stop −0.5%)

| Variant | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|---|
| M1 re-entries <10:30 | 5,091 | 37.3 | +9.87 | −153,398.29 | −57,943.41 | −95,454.88 | +29,324.68 |
| M2 morning, cap 2 | 3,761 | 37.6 | +20.68 | −72,669.75 | −28,203.13 | −44,466.62 | +33,671.95 |
| M3 round-2-only | 1,766 | 39.0 | +53.74 | **+24,268.38** | **+25,749.82** | −1,481.44 | +10,310.28 |
| M4 M1 on R5a pool | 1,169 | 36.9 | +28.62 | −13,306.55 | −20,078.42 | +6,771.87 | +9,674.82 |
| M5 M2 + ADR≥3% | 947 | 37.3 | +46.10 | **+5,772.37** | −14,173.30 | **+19,945.67** | +12,004.24 |

### T125 (target +1.25% / stop −0.5%)

| Variant | Trades | Win % | Gross exp ₹ | Net Jan–Oct ₹ | Net Jan–May ₹ | Net Jun–Oct ₹ | Net Oct ₹ |
|---|---|---|---|---|---|---|---|
| M1 re-entries <10:30 | 4,885 | 34.6 | +12.98 | −131,993.52 | −55,696.87 | −76,296.65 | +18,386.47 |
| M2 morning, cap 2 | 3,651 | 34.4 | +21.07 | −69,103.24 | −21,311.38 | −47,791.86 | +18,813.49 |
| M3 round-2-only | 1,578 | 35.5 | +47.44 | **+11,738.78** | **+29,856.88** | −18,118.10 | −4,673.76 |
| M4 M1 on R5a pool | 1,140 | 33.7 | +35.92 | −4,646.11 | −7,807.51 | +3,161.40 | +6,220.18 |
| M5 M2 + ADR≥3% | 918 | 33.4 | +51.61 | **+10,657.81** | −5,035.50 | **+15,693.31** | +8,490.91 |

## Breakeven flat cost per trade at 100 shares (= gross expectancy)

The both-halves breakeven is the smaller half's breakeven: a variant
is net-positive in both halves only if the real flat cost is below
it. Frozen cost is ₹40.

| Variant | T10 BE all | T10 BE Jan–May | T10 BE Jun–Oct | T10 BE both-halves | T125 BE all | T125 BE Jan–May | T125 BE Jun–Oct | T125 BE both-halves |
|---|---|---|---|---|---|---|---|---|
| M1 | 9.87 | 17.66 | 1.77 | **1.77** | 12.98 | 17.46 | 8.39 | **8.39** |
| M2 | 20.68 | 25.32 | 15.83 | **15.83** | 21.07 | 28.59 | 13.21 | **13.21** |
| M3 | 53.74 | 66.01 | 38.09 | **38.09** | 47.44 | 73.51 | 13.63 | **13.63** |
| M4 | 28.62 | 16.79 | 62.28 | **16.79** | 35.92 | 30.76 | 50.72 | **30.76** |
| M5 | 46.10 | 19.69 | 120.10 | **19.69** | 51.61 | 32.57 | 105.39 | **32.57** |

(All breakevens in ₹ per trade, provisional per 100 shares basis.)

## Reading

- **Why M1/M2 fail:** the pocket was re-entries before 10:30
  (gross ≈ +₹59–71/trade). M1 keeps 4,111 round-1 entries whose
  gross expectancy is ~zero, so the blended gross expectancy falls
  to +₹9.87 (T10) / +₹12.98 (T125) — far under the ₹40 cost. M2's
  cap-2 + morning cut raises it to ~+₹21, still roughly half the
  cost. The morning restriction does not create an edge in round 1;
  it only ever described round ≥ 2.
- **M3 is the closest miss and still a miss.** At T10 its Jun–Oct
  gross expectancy (+₹38.09 provisional per 100 shares) sits
  ₹1.91/trade under the frozen cost — the round-2 edge decayed in
  the second half to just below the cost line. At T125 the decay
  is larger (Jun–Oct gross +₹13.63). And M3 cannot be traded
  standalone: its chain cost (the round-1 trade) is excluded by
  construction, which is exactly the cost M1/M2 re-introduce.
- **M4/M5 flip R5a's problem rather than fixing it.** Round 6's
  R5a (cap 2 + ADR≥3%, all day) was gross-positive in both halves
  but net-negative in both. Adding the morning restriction (M5)
  lifts gross expectancy sharply (+₹51.61 at T125 vs R5a's +₹26.25,
  provisional per 100 shares) but concentrates it: Jun–Oct gross
  expectancy +₹105.39 against Jan–May +₹32.57. At ₹40 the first
  half is net-negative, the second strongly positive. That is a
  regime split, not a both-halves structure.
- **October stays an outlier:** M1, M2, M4, M5 are all strongly
  October net-positive at both exits, and M3 is October-positive
  at T10 — the same one-month pattern that has misled every
  October-first read in this series. The both-halves rule is what
  keeps it from being claimed.

## Verdict

1. **No survivor at the frozen basis.** No M-variant is
   net-positive in both halves at ₹40/trade per 100 shares.
   Nothing is adopted; nothing from this round goes to November
   paper, and no new November candidate is created — a candidate
   from this round would need its own frozen paper spec, and none
   earned one.
2. **The morning re-entry pocket is confirmed as a diagnostic and
   closed as a filter family:** as a standalone re-entry pool it
   is gross-strong in both halves, but every tradable chain form
   that includes the round-1 entries needed to reach those
   re-entries is net-negative at ₹40, and the round-2-only pool
   itself decays below cost in Jun–Oct.
3. **The cost question from Round 6 remains the binding one, now
   sharper:** the best both-halves breakevens in this round are
   M3 × T10 at ₹38.09 (untradable standalone) and M5 × T125 at
   ₹32.57 (with a Jan–May/Jun–Oct regime split). At the frozen
   ₹40 both fail; the user's actual broker charges remain unknown
   and are not invented here.

## Files

- Spec (frozen before scoring): `stocks_equity_round7_frozen.md`
- Engine: `stocks_equity_round7.py`
- Results JSON: `stocks_equity_round7_results.json`
- Kept-trade dumps: `eq_round7_v5_{T10,T125}_{M1..M5}.csv`
  (10 files, one per variant per exit)

Stage results only. Nothing here is adopted; nothing here is a
live-trading instruction.
