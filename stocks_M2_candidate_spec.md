# Stocks EQUITY — CANDIDATE SPEC — HIT-1 + State Gate (Line M2, F4)

**FROZEN 2026-10-31. CANDIDATE — for December 2026 fresh-window
judging only. NOT adopted.** Equity cash intraday only,
LONG/SHORT. Paper only — real money ₹0, no orders. Every figure:
provisional per 100 shares, ₹40/trade flat cost. **Home 25 only.**

## The rule (exact)

Base cell (H1 HIT-1): measurement 10:00 · direction FOLLOW ·
entry = first V5 pooled signal at/after 10:00 whose direction
matches the morning pre-move's sign · chain cap 2 per stock-day ·
exits target +1.25% / stop −0.65% (stop-first), 15:10 square-off ·
pre-move = machinery `premove` (close of last bar before 10:00 ÷
open of first post-09:30 bar − 1).

**State gate (the M2 root-cause repair — both conditions, known
before entry):**
1. **Qualifier band:** 0.5% ≤ |pre-move| < 1.0% (a ≥1% morning
   move does NOT qualify the stock-day at all);
2. **Trend regime:** Nifty's previous close ≤ its 50DMA (the
   INV/H1 regime map verbatim — prev close vs mean of the 50
   closes ending the prior day).

Everything else is the base cell verbatim.

## In-sample record (Jan–Oct 2026 — discovery, NOT proof)

Scored by full engine rebuild (`stocks_M2_fix.py`), timing audit
1,081 trades / **0 violations**:

- **717 trades, net +₹42,418.91**, expectancy +₹59.16/trade.
- October **+₹36,166.23** (117 trades) — keeps the base cell's
  October edge.
- Jan–Sep **+₹6,252.68** (600 trades): Jan–May **+₹3,003.36** /
  Jun–Sep **+₹3,249.32** — both halves positive (base cell:
  −₹38,658.84 / −₹24,879.59).
- Own lag-placebo (Jan–Sep): −₹906.88 — beaten.
- Breadth: **16/25** full period; **11/25 on Jan–Sep alone**
  (disclosed — the frozen acceptance leg was measured on the
  full book; the December window must show its own breadth).
- Month table: Jan +9,167.30 · Feb −4,716.39 · Mar +2,670.25 ·
  Apr −11,047.96 · May +6,930.16 · Jun −3,402.16 · Jul −1,130.92 ·
  Aug −4,657.75 · Sep +12,440.15 · Oct +36,166.23. **Five months
  are still negative** — the repair passes the halves test; it
  does not make every month green.

## Mandatory disclosures (part of the frozen record)

- **The gate's two components FAIL standalone.** Band cap alone:
  Jan–Sep −₹23,583.36 (both halves negative). Regime gate alone:
  Jan–Sep −₹40,693.78. Only the joint state passes. The in-sample
  evidence for a two-condition gate selected from diagnosis
  splits is weaker than for a single mechanism — December is the
  real judge, and this spec exists to be judged there, not
  believed here.
- **Concentration.** TVSMOTOR is +₹25,353.25 = ~60% of the
  full-period net; TVSMOTOR + ASTRAL together ≈ 97%. October is
  ~85% of the net. The Jan–Sep edge is thin: +₹10.42/trade over
  600 trades.
- **Root cause it repairs (Line M2 diagnosis):** the ungated cell
  followed ≥1% morning moves — exhaustion moves that lost in
  both halves and even in October (−₹40,532.42 of the Jan–Sep
  hole) — and traded moderate moves on above-trend days, where
  follow-through loses (−₹98.5/trade). The gate confines the
  cell to the only state where its follow-through paid:
  moderate moves on below-trend days.

## December 2026 judging rule (pre-registered)

Score December 2026 fresh data with the rule verbatim (same
machinery definitions; October-style data completion for any
missing days), judged once after December's last trading day:

- **December net > 0 with ≥ 40 trades and a clean timing audit:**
  candidate CONFIRMED for a further frozen decision (second
  fresh window / paper board). Not adopted on one month.
- **December net < 0 with ≥ 40 trades:** candidate KILLED —
  recorded as a diagnosis-selected in-sample artefact; no
  re-tuning of the band or the regime condition after the fact.
- **< 40 trades, or net exactly ₹0:** inconclusive — extends to
  January 2027 under this same rule, judged on the combined
  Dec+Jan sample against the same bar.
- In-sample frequency was ≈72 trades/month, so <40 December
  trades would itself be information (state drought), not a
  pass.

**No parameter changes before or during December:** no change
to the 10:00 measurement, the [0.5%, 1.0%) band, the 50DMA
regime condition, the follow direction, the signal stream, the
chain cap, or the exits.
