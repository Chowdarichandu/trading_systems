# LINE RSI1 REPORT — RSI as an entry mechanism, home 25, Jan–Oct 2026

Status: RUNNING. Spec frozen in `stocks_RSI1_frozen.md` before scoring.
Basis: equity cash LONG/SHORT, paper only, real ₹0, provisional per
100 shares, ₹40/trade, home 25 only.

Protocol notes: RSI = programme's `rsi_wilder`. Intraday RSI(14) on the
continuous 5-min close series (causal, completed bars only); daily
RSI(2) from closes known before the day opens. Placebo = RSI series
shifted one trading day back, same run. Timing audit mechanical, same run.

## Controls
Timing audit: **102,332 trades checked, 0 violations** (every A/B entry
is exactly the bar after its signal bar; every C entry uses a daily
RSI(2) from a close strictly before the trade day). October coverage
full (Oct 29–30 via the validated aggregation, through H1's prep).

## Verdict — NO CANDIDATE. RSI, as frozen, does not work on his 25.
All 18 cells lose money in both halves. Expectancy is negative in every
cell (−₹23 to −₹65/trade net; roughly −₹5 to −₹25/trade even before the
₹40 cost) — the RSI cross events carry no exploitable information on
these stocks at 5-minute granularity, the same signature the level
family showed. No cell reaches 9–10 green months (best is 6/10), so
nothing is flagged for the recursive engine either.

The sharpest control result: in ALL SIX RSI-A cells the **stale-RSI
placebo loses less than the real cell** (e.g. T125/S065 all-days: real
−₹491,079.40 vs placebo −₹136,079.37). Trading on today's actual RSI
cross is worse than trading on yesterday's — the cross is
anti-informative, not merely uninformative.

## Per-cell results (net · Jan–May · Jun–Oct · Oct · trades · breadth · exp · green months · placebo net)

**RSI-A intraday reversion (RSI(14) cross 30↑ LONG / 70↓ SHORT):**
- T05/S050 all: −429,486.95 · −183,966.58 · −245,520.37 · −66,027.00 · 8,351 · 1/25 · −51.43 · 0/10 · pbo −223,820.63
- T05/S050 below50: −268,182.51 · −140,336.20 · −127,846.31 · −66,027.00 · 5,642 · 1/25 · −47.53 · 1/10 · pbo −178,211.75
- T10/S050 all: −446,271.09 · −207,765.79 · −238,505.30 · −65,403.19 · 8,180 · 0/25 · −54.56 · 0/10 · pbo −144,110.40
- T10/S050 below50: −271,593.87 · −149,484.64 · −122,109.23 · −65,403.19 · 5,566 · 3/25 · −48.80 · 3/10 · pbo −105,232.74
- T125/S065 all: −491,079.40 · −224,874.05 · −266,205.35 · −80,441.00 · 7,498 · 0/25 · −65.49 · 1/10 · pbo −136,079.37 — months: Jan −68,550.52 · Feb −24,318.64 · Mar −131,411.63 · Apr +7,929.43 · May −8,522.69 · Jun −35,634.03 · Jul −52,200.09 · Aug −59,613.61 · Sep −38,316.62 · Oct −80,441.00
- T125/S065 below50: −295,979.88 · −162,776.60 · −133,203.28 · −80,441.00 · 5,134 · 3/25 · −57.65 · 3/10 · pbo −112,148.98

**RSI-B intraday continuation (RSI(14) cross 50 with day-move agreement):**
- T05/S050 all: −413,283.95 · −167,707.99 · −245,575.96 · −40,055.41 · 9,098 · 0/25 · −45.43 · 0/10 · pbo −381,497.98
- T05/S050 below50: −223,137.67 · −133,487.44 · −89,650.23 · −40,055.41 · 6,148 · 2/25 · −36.29 · 1/10 · pbo −267,465.39
- T10/S050 all: −352,608.00 · −148,377.29 · −204,230.71 · −41,040.06 · 7,971 · 1/25 · −44.24 · 0/10 · pbo −325,504.45
- T10/S050 below50: −173,736.55 · −101,423.31 · −72,313.24 · −41,040.06 · 5,395 · 2/25 · −32.20 · 1/10 · pbo −228,789.10
- T125/S065 all: −294,007.01 · −123,179.26 · −170,827.75 · −24,640.72 · 6,942 · 1/25 · −42.35 · 0/10 · pbo −231,247.70
- T125/S065 below50: −107,989.70 · −85,478.45 · −22,511.25 · −24,640.72 · 4,670 · 4/25 · −23.12 · 4/10 · pbo −159,765.14 — months: Jan −2,238.02 · Feb +1,338.02 · Mar −33,363.12 · Apr −16,990.20 · May −34,225.13 · Jun +2,282.48 · Jul +2,454.15 · Aug +5,089.17 · Sep −7,696.33 · Oct −24,640.72. (The below50 B cells beat their placebos but both sides are deeply negative — no effect to certify.)

**RSI-C daily RSI(2) extreme → 09:35 entry (least-bad family):**
- T05/S050 all: −68,327.95 · −40,512.63 · −27,815.32 · −10,030.58 · 1,348 · 4/25 · −50.69 · 2/10 · pbo −62,174.09
- T05/S050 below50: −53,632.18 · −20,504.56 · −33,127.62 · −10,030.58 · 884 · 2/25 · −60.67 · 2/10 · pbo −19,905.78
- T10/S050 all: −86,614.16 · −48,735.00 · −37,879.16 · **+3,731.20** · 1,348 · 3/25 · −64.25 · 2/10 · pbo −45,252.64
- T10/S050 below50: −44,381.36 · −31,248.57 · −13,132.79 · **+3,731.20** · 884 · 4/25 · −50.21 · 4/10 · pbo +584.34
- T125/S065 all: −57,895.31 · −26,783.36 · −31,111.95 · **+1,794.92** · 1,348 · 2/25 · −42.95 · 4/10 · pbo −32,987.16 — months: Jan +3,732.29 · Feb −21,804.18 · Mar −13,607.44 · Apr −1,972.13 · May +6,868.10 · Jun +7,722.40 · Jul −25,173.61 · Aug −1,525.77 · Sep −13,929.89 · Oct +1,794.92
- T125/S065 below50: **−23,679.90 (the line's ceiling)** · −17,439.17 · −6,240.73 · **+1,794.92** · 884 · 5/25 · −26.79 · **6/10** · pbo +18,948.39 (placebo positive — real cell loses to it) — months: Jan +255.44 · Feb −10,438.00 · Mar −13,607.44 · Apr +5,926.55 · May +424.28 · Jun +8,555.71 · Jul +673.05 · Aug −3,334.52 · Sep −13,929.89 · Oct +1,794.92

## Observation only (not a claim)
RSI-C's October is positive at the wider exits in both contexts
(+₹3,731.20 at T10, +₹1,794.92 at T125) — the daily-extreme idea is the
only RSI form whose October isn't a loss. Against Jan–Sep losses of
−₹48k…−₹90k in those same cells it is the known October-only pattern;
recorded here as an observation, promoted nowhere.

## Files
`stocks_RSI1_frozen.md` (spec) · `stocks_RSI1.py` (engine) ·
`stocks_RSI1_results.json` (all cells, month tables, per-stock) ·
`stocks_RSI1_<CELL>_trades.csv` (18 real-cell dumps). No candidate
spec was frozen — the December board is unchanged, and no RSI
component is offered to the recursive engine.
