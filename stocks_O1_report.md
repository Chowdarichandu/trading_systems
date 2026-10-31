# Stocks EQUITY — Line O1 report: October-first hunt for ₹50,000 in one month

Equity cash intraday only, LONG/SHORT. **Paper only — real money ₹0,
no orders.** Every figure: **provisional per 100 shares, ₹40/trade**
cost deducted. Scan dimensions and verdict rules were frozen in
`stocks_O1_frozen.md` BEFORE scanning.

**Verdict rules (from the frozen plan):** a cell is an OCTOBER HIT at
pooled October net ≥ +₹50,000. A hit is REAL only if Jan–Sep 2026 is
positive in BOTH halves (Jan–May and Jun–Sep) AND breadth ≥ 35/50 AND
it beats its lag-placebo. October is the discovery month only —
October-only success is the known one-month-luck trap.

---

## October coverage

**Full month: 20 trading days (Oct 1–30) in BOTH universes.**
The 5-min caches held Oct 1–28 (18 days). Oct 29–30 were added from
the already-fetched Upstox 1-min cache (`data/1min_stocks_oct2026/`,
all 50 stocks, full 375-bar days), aggregated to 5-min. The
aggregation was validated against the cached 5-min bars for
Oct 28: **1,875 bars per universe checked, 0 mismatches**. DAYCTX
entries for the two added days were built with the frozen re-entry
head's own construction. The Nifty regime map (INV definition) was
extended to Oct 30 with live-fetched Nifty daily closes, verified
against the cached Oct 28 close; Oct 28–30 are all below-50DMA days.

---

## Phase 1 — October discovery scan

Full frozen grid scanned: **1,344 cells** (336 base × 4 contexts),
58,494 trades generated. **Timing audit: 0 violations** — every
entry at/after its measurement time, every signal-mode entry
strictly after its signal bar.

**17 cells are OCTOBER HITs (pooled net ≥ +₹50,000)** — all of them
in the `fixed` (fixed-time entry) mode; the V5 signal pool produced
none. The top of the table:

| Cell (T \| thr \| dir \| mode \| exit \| ctx) | Oct net ₹ | Trades | Breadth | Home ₹ | Ext ₹ |
|---|---|---|---|---|---|
| 11:00 \| 1.0% \| fade \| fixed \| T125/S065 \| all | **+98,494.46** | 231 | 22/50 | +341.29 | +98,153.17 |
| 11:00 \| 1.0% \| fade \| fixed \| T125/S050 \| all | **+93,914.68** | 231 | 21/50 | −2,534.25 | +96,448.93 |
| 11:00 \| 1.0% \| fade \| fixed \| T10/S050 \| all | +77,338.66 | 231 | 20/50 | +42.19 | +77,296.47 |
| 11:00 \| 0.5% \| fade \| fixed \| T125/S065 \| event | +66,527.75 | 161 | 13/50 | +13,341.54 | +53,186.21 |
| 11:00 \| 1.0% \| fade \| fixed \| T125/S065 \| event | +65,805.32 | 83 | 16/50 | +5,025.49 | +60,779.83 |
| 12:00 \| 0.5% \| follow \| fixed \| T05/S050 \| all | +59,074.10 | 571 | 30/50 | −2,602.73 | +61,676.83 |
| 12:00 \| 0.5% \| follow \| fixed \| T10/S050 \| all | +58,903.66 | 571 | 28/50 | −5.13 | +58,908.79 |
| 11:00 \| 0.5% \| fade \| fixed \| T125/S065 \| all | +52,989.62 | 524 | 18/50 | −2,557.20 | +55,546.82 |

(The `below50` twins of the `all` rows are identical in October —
every qualifying trade fell on a below-50DMA day — and are not
counted as separate hits. The full 107-cell near-zone ≥ +₹20,000
and the whole grid are in `stocks_O1_results.json`.)

Best cell per family: sig|follow +₹33,570.95 (10:00, 0.5%, T10/S050,
noevent); sig|fade +₹8,929.05 (10:30, 0.5%, T125/S065, all);
fixed|follow +₹59,074.10; fixed|fade +₹98,494.46.

**Read on Phase 1, stated before validation:** October's ₹50k was
reachable — several times over — but the shape is suspicious in a
familiar way: the top cell's profit is 99.7% ext-universe
(+₹98,153.17 of +₹98,494.46; home is +₹341.29, i.e. zero) and its
breadth is only 22/50. That is exactly the profile of a one-month,
one-universe artefact. Phase 2 decides; nothing here is called real
yet.

## Phase 2 — Jan–Sep validation of the top-2 October cells

Phase-2 timing audit: 6,616 trades, **0 violations**. Both cells'
October re-checks reproduce their Phase-1 numbers **exactly**
(231 trades; +₹98,494.46 and +₹93,914.68).

### HIT-1 — 11:00, thr 1.0%, fade, fixed entry, T125/S065, all days

| Month | Trades | Net ₹ |
|---|---|---|
| Jan | 194 | +66,859.37 |
| Feb | 165 | +6,144.09 |
| Mar | 275 | +21,465.42 |
| Apr | 232 | +21,583.49 |
| May | 174 | +65,033.23 |
| Jun | 142 | +35,062.16 |
| Jul | 163 | −28,450.73 |
| Aug | 100 | +12,551.61 |
| Sep | 97 | +9,927.09 |
| **Jan–Sep** | **1,542** | **+210,175.73** |

- Halves: Jan–May **+₹181,085.60** / Jun–Sep **+₹29,090.13** — both
  positive ✓. 8 of 9 months positive.
- Lag-placebo (Jan–Sep): **−₹20,539.18** — beaten clearly ✓.
- **Breadth: 31/50 — FAILS the frozen ≥35/50 leg ✗.**
- Where the money is: Jan–Sep home **+₹3,901.89** vs ext
  **+₹206,273.84** (98.1% ext). Top-3 stocks — MARUTI +₹67,333.70,
  EICHERMOT +₹66,062.82, M&M +₹18,654.81 — are **72.3%** of the net.
  This is an ext-universe, auto-heavy phenomenon, not a 50-stock
  behaviour.
- True run-rate: Jan–Sep **₹23,353/month**; Jan–Oct (with the
  +₹98,494.46 October) **₹30,867/month** — below the ₹50k bar.

### HIT-2 — 11:00, thr 1.0%, fade, fixed entry, T125/S050, all days

Jan–Sep: 1,542 trades, +₹146,655.74 — but Jan–May +₹179,786.14 /
**Jun–Sep −₹33,130.40** (Jul −₹37,808.14, Sep −₹2,175.40). Breadth
27/50. Placebo −₹30,826.45 (beaten, moot). **FAILS on halves and
breadth.** The tighter stop turns the second half negative — the
October ranking between the two stops does not survive.

## Verdict

**No candidate. October's ₹50,000 was reached in the discovery
month (best cell +₹98,494.46) but was NOT honestly validated at
that level.**

- HIT-1 passes three of the four frozen legs (both halves positive,
  placebo beaten, audit clean) and fails breadth 31/50 — and even
  taken at face value it is a ~₹23–31k/month book concentrated in
  the ext universe's auto names, with a flat home universe. Under
  the rules frozen before scanning, that is not REAL, and no
  candidate spec is frozen. (Freezing it anyway, or re-cutting it
  to ext-only after the fact, would be exactly the hindsight move
  this line exists to avoid.)
- HIT-2 fails outright on Jan–Sep's second half.
- The V5 signal-stream pool produced **no** October hit at all
  (best sig cell +₹33,570.95); every hit came from fixed-time
  entries, and the fade side (betting against the morning move at
  11:00–14:00) dominated October specifically.

**Best validated run-rate found:** none passes all four legs. The
closest, HIT-1, validates at **₹23,353/month over Jan–Sep**
(₹30,867/month including its discovery October) against the
₹50,000/month bar — with the concentration caveats above. The
honest statement for the user: in these families, October's ₹50k
was a strong month for a narrow ext-universe fade effect, not a
₹50k/month system.

Files: `stocks_O1.py` (engine), `stocks_O1_results.json` (full
1,344-cell grid + Phase-2 detail), `stocks_O1_P2_*_trades.csv`
(Phase-2 trade dumps), `stocks_O1_frozen.md` (frozen plan +
Phase-2 addendum).
