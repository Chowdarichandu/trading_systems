# Line S2 — Volume-Shock Entries — report

Equity cash, LONG/SHORT, paper only, real ₹0. Provisional per
100 shares, ₹40/trade, Jan–Oct 2026. Cells frozen in
`stocks_S2_frozen.md` BEFORE scoring; timing audit + placebo in
the same run as first scoring (controls-first protocol).

## Data verification (pre-scoring)

Both volume caches USABLE. Join of price (`spot_5m.csv`) with
volume (`spot_5m_vol.csv`) on timestamp, window Jan–Oct 2026:

- Home 25: 380,616 price bars joined 100.00%, 203 trading days,
  zero-volume joined bars 0.73%.
- Ext 25: 384,375 price bars joined 100.00%, 205 trading days,
  zero-volume joined bars 0.81%.
- OHLC cross-check (vol file vs price cache, sampled symbols
  both universes): 0 open/close mismatches.

(Results below are appended as the run completes.)

## Timing audit — CLEAN

Asserted over every trade in every cell: entry bar index =
shock bar index + 1 (entry is exactly the next bar's open, the
shock bar fully closed, its prior-20 volume window strictly
before it). S2-A 3,968 trades, S2-B 3,791, S2-C 2,512, placebo
747 — **0 violations anywhere**. The rule is executable in real
time exactly as scored.

## Results — pooled 50 (primary)

| Cell | Trades | Net ₹ | Exp/trade | Win % | Jan–May ₹ | Jun–Oct ₹ | October ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|
| S2-A (3×, T05/S050) | 3,968 | **−186,333.50** | −46.96 | 45.6 | −89,554.52 | −96,778.98 | −7,594.71 | 8/50 |
| S2-B (3×, T125/S050) | 3,791 | **−116,468.35** | −30.72 | 38.1 | −46,775.70 | −69,692.65 | −9,719.90 | 11/50 |
| S2-C (4×, T125/S050) | 2,512 | **+11,400.88** | +4.54 | 37.7 | +9,370.80 | +2,030.08 | −17,348.72 | 12/50 |

Direction split (pooled): S2-A LONG −₹109,996.01 / SHORT
−₹76,337.49 · S2-B LONG −₹67,337.63 / SHORT −₹49,130.72 ·
S2-C LONG −₹8,652.25 / SHORT **+₹20,053.13**.

## Home / ext splits

- **S2-A:** home 2,389 trades, −₹91,860.90 (JM −₹38,477.18 /
  JO −₹53,383.72, Oct −₹19,293.72, breadth 3/25); ext 1,579,
  −₹94,472.60 (JM −₹51,077.34 / JO −₹43,395.26, Oct
  +₹11,699.01, breadth 5/25).
- **S2-B:** home 2,257, −₹62,908.71 (JM −₹45,268.54 / JO
  −₹17,640.17, Oct −₹20,744.98, breadth 4/25); ext 1,534,
  −₹53,559.64 (JM −₹1,507.16 / JO −₹52,052.48, Oct
  +₹11,025.08, breadth 7/25).
- **S2-C:** home 1,526, **−₹36,092.24** (both halves negative,
  Oct −₹14,601.76, breadth 4/25); ext 986, **+₹47,493.12**
  (JM +₹28,044.88 / JO +₹19,448.24, Oct −₹2,746.96, breadth
  8/25). The two universes disagree in sign — the pooled
  positive is an ext-only artefact of pooling, and even there
  October is negative.

Concentration (diagnostic, stated plainly): in S2-C, MARUTI
alone is +₹83,043.50 — over 7× the pooled net; without it the
cell is −₹71,642.62. S2-B has the same shape (MARUTI
+₹80,476.25 against a −₹116,468.35 book). ULTRACEMCO is the
mirror image in the 3× cells (−₹50,607.50 in S2-A, −₹69,210.50
in S2-B). These are single-name swings, not a market-wide
behaviour.

## Placebo — shifted volume (on best cell S2-C)

Identical machinery, volume series shifted from the previous
trading day (same stock, aligned by clock time), today's prices
and entries: 747 trades, **−₹100,422.83** pooled (JM
−₹57,124.93 / JO −₹43,297.90, Oct −₹12,619.47, breadth 9/50,
exp −₹134.43/trade). S2-C's real +₹11,400.88 **beats the
placebo by ₹111,823.71** — so a 4× volume shock is not pure
noise against this control. But beating a deeply negative
placebo is a low bar: the real cell's expectancy is +₹4.54 per
trade (≈ +₹1,140/month over 10 months), against the programme
target bar of ~₹25,000/month.

## Verdict — NO CANDIDATE

Gate legs (pooled both halves > 0, breadth ≥ 35/50, October
> 0, audit clean, placebo beaten):

- S2-A: fails every leg. Dead.
- S2-B: fails every leg. Dead.
- S2-C: passes halves, audit and placebo; **fails breadth
  (12/50 vs 35) and fails October (−₹17,348.72)**. Not a
  candidate. No `stocks_S2_candidate_spec.md` is frozen.

Per the frozen protocol there is no rescue inside this line:
the SHORT-only / ext-only / ex-MARUTI readings above are
diagnostics recorded after the fact, not variants — freezing
any of them would be exactly the post-hoc split this protocol
exists to prevent.

What this closes: a volume shock by itself — at 3× with the
user's small target, at 3× with the standard target, and at 4×
— is not an entry edge on this universe. The 3× books lose in
both halves on both universes; the 4× book's faint positive is
one universe, one direction-lean, one stock (MARUTI) and a
negative October. Volume's honest role in this programme
remains what earlier lines found: at best a gate or a filter on
somebody else's signal — as a standalone trigger it does not
pay the ₹40 cost with breadth. Any future volume idea needs a
genuinely different mechanism (e.g. volume shock relative to
the same clock-time on prior days, or shock + a price-structure
condition declared in advance), frozen before scoring like
this one was.

Files: engine `stocks_S2.py`, `stocks_S2_results.json`, trade
dumps `stocks_S2_S2-A_trades.csv`, `stocks_S2_S2-B_trades.csv`,
`stocks_S2_S2-C_trades.csv`, `stocks_S2_S2-C_PLACEBO_trades.csv`.

