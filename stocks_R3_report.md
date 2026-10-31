# Stocks EQUITY — LINE R3 — INV-LONG / INV1 TRANSFER TEST — report

**EQUITY CASH intraday only. LONG/SHORT. Paper only, no orders.
Real money ₹0. Every figure provisional per 100 shares, net =
gross − ₹40/trade. Window Jan–Oct 2026 (October = 1–28 Oct).**
**Spec: `stocks_R3_frozen.md` (frozen before scoring). Rules
VERBATIM from the INV tuning loop — no re-tuning on the new
universe.**

## Anchor validation — ALL PASS to the paisa

The R3 engine's home run (original Round 8 machinery, home
universe) reproduced before any ext number was scored:

- **INV1 home:** 694 trades, net **+₹22,964.30**, halves
  +₹7,255.01 / +₹15,709.29.
- **INV-LONG home:** 249 trades, net **+₹24,185.73**, halves
  +₹14,751.12 / +₹9,434.61, October +₹7,691.08, breadth 12/25,
  top-3 share 116.2%.

Machinery note: the NIFTY `spot_daily.csv` in
`data/progressive_ext/` is byte-identical to the home file, so
the INV1 qualifying-day set is identical across universes —
only the traded stocks differ. The transfer test is clean.

## EXT INV-LONG (rule under test) — FAILS, on both legs

90 trades, win 28.9%, net expectancy +₹39.65/trade, net
**+₹3,568.67** — halves **Jan–May +₹15,546.60 (71 trades) /
Jun–Oct −₹11,977.93 (19 trades)**, October **−₹11,393.43
(17 trades)**, breadth **6/25**, top-3 share 661.3%.

- **Halves leg: FAIL.** Jun–Oct is negative.
- **Breadth leg: FAIL.** 6/25 positive, not ≥ 10/25.
- **Verdict: INV-LONG does NOT transfer.** Its total stays
  positive only because Jan–May carries it.

Per-stock shape (ext INV-LONG): MARUTI +₹12,142.50 from just
2 trades, M&M +₹6,509.26, LT +₹4,948.75, DRREDDY +₹3,780.85,
HCLTECH +₹1,061.78, COALINDIA +₹271.88 — and 7 stocks never
traded at all (RELIANCE, ICICIBANK, BHARTIARTL, KOTAKBANK,
SUNPHARMA, GRASIM, CIPLA — 0 trades each). Worst: TCS
−₹11,559.65 (9 trades) alone nearly erases MARUTI's gain.
The ext book is thinner and more concentrated than the home
book, not broader.

Structural reason: the P2 pool starves on large caps. Ext P2
pool = 237 trades vs home's 918 — the ADR≥3% filter, which the
home watchlist clears routinely, fires rarely on large caps
(and the whole ext P2 pool itself flips in Jun–Oct:
+₹72,738.59 / −₹14,735.94). In Jun–Oct the ext INV-LONG pool
produced only 19 trades, 17 of them in October, and October
was a disaster (−₹11,393.43).

## EXT INV1 (both directions, context) — FAILS too

201 trades, net **+₹35,107.79** — halves **+₹46,360.85 /
−₹11,253.06**, October −₹8,997.78 (29 trades), breadth **10/25**,
top-3 share 141.6%. Breadth meets the leg (exactly 10/25);
the halves leg fails — Jun–Oct is negative. The direction
restriction is not what fails the transfer: the combined book
fails on the same half.

Top ext INV1 payers: EICHERMOT +₹20,706.24, MARUTI
+₹15,672.25, LT +₹13,337.90. Worst: TCS −₹12,538.55.
Note the direction story reverses on ext: EICHERMOT's INV1
profit (+₹20,706.24) is mostly SHORT-side (its INV-LONG net
is −₹1,987.38), so the LONG-only restriction that helped at
home hurts this name on ext.

## POOLED-50 INV-LONG — honest number, and it breaks the gate

Home + ext rows combined: 339 trades, win 34.2%, net
expectancy +₹81.87, net **+₹27,754.40** — halves
**Jan–May +₹30,297.72 / Jun–Oct −₹2,543.32**, October
−₹3,702.35, breadth **18/50**, top-3 share 128.6%.

Pooling does NOT rescue the candidate: home's Jun–Oct
(+₹9,434.61) plus ext's Jun–Oct (−₹11,977.93) nets to
**−₹2,543.32** — the pooled book fails the both-halves gate
that the home book passed. Concentration dilutes only
modestly: TVSMOTOR +₹15,287.54 + GLENMARK +₹8,252.87 =
₹23,540.41 = **84.8% of the pooled net** (vs ≈97% at home),
and only because MARUTI added +₹12,142.50 on ext. The pooled
book still rests on three names.

Top-5 pooled per-stock: TVSMOTOR +₹15,287.54, MARUTI
+₹12,142.50, GLENMARK +₹8,252.87, M&M +₹6,509.26, LT
+₹4,948.75.

## Verdicts

1. **INV-LONG transfer: FAILS** — both legs of the frozen
   standard fail on the new 25 (Jun–Oct −₹11,977.93,
   breadth 6/25). INV-LONG's standing is unchanged:
   home-universe-only v2 candidate, exactly as
   `stocks_inv_v2_candidate_spec.md` records it.
2. **INV1 transfer: FAILS** — Jun–Oct −₹11,253.06 on ext.
3. **NO pooled candidate spec is written.** The frozen rule
   permits one only if INV-LONG transfers; it did not.
   The honest pooled-50 INV-LONG number is **+₹27,754.40
   over 10 months with a negative second half** — not a
   candidate, and nowhere near the retracted Morning-Mover
   bar (₹249,155 / ₹464,617 pooled, which were leak
   artefacts, not a real target any honest system has yet
   approached).
4. **What this teaches the hunt:** the INV family's edge, to
   the extent it is real at all, is a small-/mid-cap
   phenomenon tied to the ADR≥3% pool — it does not survive
   contact with large caps, where the pool starves and the
   second half turns. Any future INV work must either find a
   pool filter that fires on large caps or accept the
   home-universe-only scope.

## Files

- Frozen spec: `stocks_R3_frozen.md`
- Engine: `stocks_R3.py`; results: `stocks_R3_results.json`
- Trade CSVs: `R3_ext_inv1_trades.csv`,
  `R3_ext_inv_long_trades.csv`, `R3_pool50_inv_long_trades.csv`
- November INV1 shadow: untouched.
