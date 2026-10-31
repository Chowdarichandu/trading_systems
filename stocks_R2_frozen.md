# LINE R2 — FROZEN CELLS (frozen BEFORE any scoring, 2026-10-31)

Equity cash intraday only, LONG/SHORT language. Paper only, real ₹0, no
orders. All figures provisional per 100 shares, ₹40/trade cost deducted.
Window: Jan–Oct 2026 (home cache Oct = 1–28, 18 trading days, 29 Oct
missing from the 5-min cache — a missing day, never a zero; ext cache
Oct = 1–30, 20 trading days, as cached). POOLED 50 primary; home 25 /
ext 25 splits reported. Target bar (context, not a gate): ~₹25k/month
pooled per 100 shares.

Data: 5-min caches only — home `data/progressive/`, ext
`data/progressive_ext/`. Day open = first 5-min bar (09:15) open; day
close = last 5-min bar (15:25) close; a stock's trading-day sequence =
the dates present in its own cache. Exits replayed with the programme's
frozen `replay_plain` (stop checked before target inside a bar,
square-off at the 15:10 bar close, gross = 100 × sign × (exit − entry)).

## CONTROLS-FIRST PROTOCOL (mandatory, part of the freeze)

- Both axes are leak-proof BY CONSTRUCTION: the qualifier uses only
  information complete strictly before the entry timestamp.
- A timing audit runs IN THE SAME RUN as scoring: every trade carries
  `info_complete` and `entry_dt`; the engine asserts programmatically
  over ALL trades that entry_dt > info_complete, and prints a sample of
  ≥10 trades per axis with both timestamps. If the assertion fails, no
  number from that axis may be quoted.
- One cell scored = one frozen cell. No post-hoc variants.

## AXIS 1 — GENERALISED FOLLOW-THROUGH (FT)

Qualifier: a stock-day D with |close(D) / close(prev cached day) − 1| ≥
threshold is a big-move day; direction = sign of that move.
Information complete: close of day D (audit timestamp: D 15:30).
Trade: enter on the NEXT cached trading day at the 09:15 bar open, in
the SAME direction (LONG if the big move was up, SHORT if down).
One trade per stock per big-move day; a next day that is itself a
big-move day qualifies independently. No trade if D is the last cached
day of the window for that stock (entry day must be ≤ 2026-10-31).

Cells (4):
- FT-20-T125: threshold 2.0%, exits target +1.25% / stop −0.50%
- FT-20-T10:  threshold 2.0%, exits target +1.00% / stop −0.50%
- FT-25-T125: threshold 2.5%, exits target +1.25% / stop −0.50%
- FT-25-T10:  threshold 2.5%, exits target +1.00% / stop −0.50%

## AXIS 2 — OVERNIGHT GAP (GAP)

Qualifier: gap = open(today) / close(prev cached day) − 1, with
|gap| ≥ threshold. The gap is the 09:15 open print itself;
information complete at 09:15 on the entry day.
Trade: enter at the open of the SECOND 5-min bar (09:20) the same day —
strictly after the information exists.
- FOLLOW: trade in the gap's direction (gap up → LONG, gap down → SHORT).
- FADE: trade against the gap's direction.
Exits for all GAP cells: target +1.25% / stop −0.50% (T125/S050).
One trade per stock per qualifying day.

Cells (4 — the 1.5% pair is IN, declared here before scoring):
- GAP-10-FOLLOW: threshold 1.0%, follow
- GAP-10-FADE:   threshold 1.0%, fade
- GAP-15-FOLLOW: threshold 1.5%, follow
- GAP-15-FADE:   threshold 1.5%, fade

## GATE toward candidacy (per cell)

Pooled 50: Jan–May net > 0 AND Jun–Oct net > 0 AND breadth ≥ 35/50
stocks net-positive AND October net > 0 AND timing audit clean.
A passing cell is frozen as `stocks_R2_candidate_spec.md` with a
December fresh-window judging rule (mirroring prior specs: judged on
fresh data only, no re-tuning during the window). Failing cells are
reported in full and closed — no rescue variants inside this line.
