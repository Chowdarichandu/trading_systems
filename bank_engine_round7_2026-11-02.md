# Bank Nifty Engine — ROUND 7 (2026-11-02)

Basis: index-options premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE,
paper only, real money ₹0. Gating reference: **book v21 = +₹83,650.50**
(99 legs, FT90 49.5%, 2.44/week), the causal book frozen at Round 6.
Every candidate below was scored with the full controls gate in the same
run (timing audit + admission/feature-timing audit + delay-6 placebo +
halves + month table + ex-top-3), on causal times only. Opening sanity:
v20 (+₹78,250.50) and v21 (+₹83,650.50) both reproduced exactly before
any scoring (n=99, placebo −₹4,313.50, ex-top-3 +₹54,610.50, NC 0,
timing violations 0, re-sum exact).

**Result: 12 cycles (150–161), ZERO banked. Book v21 stands unchanged.
Ending pace ₹8,365.05/month vs the ₹15,000 floor — gap ₹66,349.50,
floor NOT met.** All six briefed workstreams were gated through; WS6
(combinations) closes vacuously because the banking set is empty.

## WS1 — V5 knobs (Cycles 150–154)

V5 v2's own construction parameters (from the frozen pool spec,
`index_options_U1_frozen.md` + `progressive_capped_v2.cap_select_v2`):
the prospective-target filter `min_target` (frozen ₹500) and the weekly
index cap `cap_index` (frozen 3) are the two material knobs; `cap_stock`
(3) and the 1-per-symbol-week rule bind the stock side of the shared
pool, not Bank's member.

- **Cycle 150 — regeneration validation: PASS.** The frozen-parameter
  regeneration (₹500, cap 3) reproduces the frozen Bank V5 leg set
  EXACTLY (40 legs; 0 unresolved, 0 skipped) — variants are trusted.
- **Cycle 151 — min_target ₹250: EXACT NO-OP.** Book identical to v21
  (+₹83,650.50, n=99, every control identical). Nothing to bank.
- **Cycle 152 — min_target ₹1,000: EXACT NO-OP.** Identical book.
- **Cycle 153 — cap_index 5: EXACT NO-OP.** Identical book.
- **Cycle 154 — cap_index 2: EXACT NO-OP.** Identical book.

The Bank V5 selection is invariant across the entire grid in both
directions: the filter and the cap bind on the shared pool (and on the
pooling competition downstream), never on Bank's own picks. Axis closed.

## WS2 — (lA) CE mirror (Cycle 155)

Built as the exact mirror of the frozen (lA) v2 L1 engine (Nifty
confirmer breaks OR **high** 09:30–11:30; Bank rescan close > own ORH
and > PDH; room to the next PD level above ≥ 200·scale; entry next bar,
stop = signal low, target entry + 2·risk), scored as an add-on sleeve
through the book's own admission machinery. Nifty's mirror verdict was
NOT imported; this is Bank's own population.

- Population 25 legs; admitted 21 (3 key-dropped, 1 band-dropped);
  **sleeve net −₹8,622.00** → book **+₹75,028.50** (n=120, FT90 45.0%,
  placebo −₹19,729.00 beaten, ex-top-3 +₹45,988.50, NC 0).
- **REJECTED**: net (−₹8,622.00), June flips green→red
  (+₹560.00 → −₹5,893.50), FT90 dilution (49.5 → 45.0).
- Bank's (lA) edge is PE-only, measured on Bank data. Family closed.

## WS3 — Skill OR-window variant (Cycles 156–157)

One variant per the brief: OR 09:15–09:45 (signals 09:45–11:30,
first-bar PE rule applied at 09:45), Bank Skill legs only, whole book
re-gated.

- **Cycle 156 — regeneration validation: PASS.** The same generator at
  the frozen window reproduces the frozen Skill sets EXACTLY
  (Jan–Sep 150/150; October 14/14). The frozen file's own unscoreable
  leg (2026-10-28 CE 54000, expiry 2026-11-03 — the Bank Nov-03 chain
  gap) is excluded symmetrically on both sides, named here per protocol.
- **Cycle 157 — OR 09:15–09:45: REJECTED.** The wider OR produces 138
  Skill legs vs 164 at the frozen window; book **+₹77,994.50** (n=100,
  FT90 50.0%, placebo −₹18,585.50 beaten, ex-top-3 +₹48,954.50, NC 0).
  Fails net (−₹5,656.00) and flips June green→red (+₹560.00 → −₹1,160.00).
  The frozen 09:15–09:30 OR stands. Axis closed.

## WS4 — Strike axis on the causal book (Cycles 158–159)

Every leg re-scored at 100 pts ITM (CE −100, PE +100) on real ITM
premium candles fetched via the expired-instruments route; the shift
applied to the whole construction (pool, NS1, NS3 candidates, S3
setups), then the frozen pipeline ran unchanged.

- **Cycle 158 — blanket ITM-100: REJECTED.** **+₹74,170.00** (n=101,
  FT90 49.5%, placebo −₹9,024.00 beaten, ex-top-3 +₹45,130.00).
  NC 0 — every ITM candle fetched (still-missing 0), so the cell is a
  clean scored rejection, not an NC report. Net −₹9,480.50 vs v21.
- **Cycle 159 — expiry-day-scoped ITM-100: REJECTED.** **+₹79,450.50**
  (n=99, FT90 48.5%, placebo −₹873.50 beaten, ex-top-3 +₹50,410.50,
  NC 0). Net −₹4,200.00 and FT90 dilutes (49.5 → 48.5). The root
  method's expiry-day ITM rule does not survive premium scoring on
  Bank's causal book. Strike axis closed; ATM stands.

## WS5 — Square-off re-gate on the causal book (Cycles 160–161)

The 15:20 square-off was banked pre-audit (Round 3); re-gated on v21:

- **Cycle 160 — 15:10: REJECTED.** +₹80,329.50 (n=99, FT90 49.5%,
  placebo −₹5,728.30 beaten, ex-top-3 +₹51,289.50, NC 0). Net −₹3,321.00.
- **Cycle 161 — 15:25: REJECTED.** +₹83,388.00 (n=99, FT90 49.5%,
  placebo −₹4,655.50 beaten, ex-top-3 +₹54,348.00, NC 0). Net −₹262.50.
- The incumbent **15:20 is the peak of {15:10, 15:20, 15:25} on causal
  data** — the pre-audit banking is confirmed, not inherited. (Both
  cells' post-restore checks reproduced v21 to the paisa, so the patch
  discipline is verified.)

## WS6 — Combinations

Nothing banked in Round 7, so no combination exists to gate. The
workstream is closed by statement, not skipped silently: any future
banking re-opens it.

## Process disclosures

- WS1's first run re-ran `candidates_for_month` once per variant (an
  un-cached full pass over the candidate universe each time); it was
  killed at ~25 minutes before producing any score, the cache was
  fixed (one pass per month, shared by all variants), and every WS1
  number above comes from the fixed run. No figure from the killed run
  exists or is used.
- Two cosmetic defects in WS4/WS5 post-run check code (a KeyError on a
  reporting key, after the judged lines had printed) did not touch any
  score: both scripts' restore checks printed the exact v21 line
  (+₹83,650.50, n=99) before the defect fired, and WS4 was re-run clean
  end-to-end with identical C158 output.

## Ending scorecard — book v21 (unchanged)

| Measure | Value |
|---|---|
| Jan–Oct 2026 net (premiums, 1 lot) | **+₹83,650.50** |
| Trades | 99 (2.44/week) |
| FT90 | 49.5% |
| Months | Jan +22,748 · Feb +20,480 · Mar +1,120 · Apr −90 · May +17,680 · Jun +560 · Jul −3,680 · Aug −873.50 · Sep +10,776.50 · Oct +14,929.50 (no red month-ends) |
| Halves | +₹61,938.00 / +₹21,712.50 |
| Placebo (delay-6) | −₹4,313.50 — beaten |
| Ex-top-3 | +₹54,610.50 |
| NOT_COMPUTED / timing violations | 0 / 0 |
| Monthly pace vs ₹15,000 floor | **₹8,365.05 — gap ₹66,349.50, NOT met** |

Trades: `bank_engine_r6_v21_trades.csv` (unchanged). Round 7 closes
every axis it opened: V5 knobs (invariant), (lA) mirror (PE-only edge),
Skill OR window (frozen window stands), strike (ATM stands), square-off
(15:20 confirmed). The remaining gap is, as at Round 6's close, outside
every axis measured on causal data — it needs a genuinely new causal
signal family or forward (November+) evidence. The standing order
applies: the engine does not stop; Round 8 is the parent agent's to
launch.
