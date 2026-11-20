# SAPTA Design 24 — SPEC (pre-registered)

**Pre-registered:** 2026-11-18, before any Design 24 scoring.
**Authority:** Design 23's pre-registered seed rule (SPEC
§7, no survey survivor): the entry-timing surface is
surveyed out alongside the allocation surface (Design 22
closure) — Design 24 changes the one surface never yet
changed in this programme: **stock-level cross-sectional
SELECTION**. No intraday timing signal at all: a monthly
rank-and-hold relative-strength book inside the rotating
SAPTA universe.
**Owner's bar (standing):** a SAPTA book that meets or
beats EKAM in BOTH years (Cand-1 +₹62,165/+₹63,884 ·
Cand-2 +₹45,301/+₹72,605, per 100 shares).
**Class:** research only. Nothing armed, no paper run
started, no live book touched. Paper only, real money ₹0.
**Basis:** equity cash, PROVISIONAL per 100 shares. No
stock options (closed surface).

## 0. Why this design (diagnosis carried in)

Twenty-three designs have priced intraday signals on this
universe: the gap-fade family gates six books whose 2026
all lands in the ₹21–29k band (signal-power ceiling,
Design 21's diagnosis), and Design 23's five new entry
timings all failed the survey bar (best CLR-FADE
gross/trade ₹32.12/₹107.82 — one year under the levy).
Every SAPTA book so far is an intraday or few-day book.
What has never been tested here is whether the rotating
universe's names carry a **cross-sectional momentum**
premium at the monthly horizon: buy the names that have
already been rising, hold them while they keep ranking,
let rank decay — not a stop, not a target — decide exits.
If the universe's 2026 weakness is a timing problem, a
selection book sidesteps it; if it is a universe problem,
this design's frozen-25 diagnostic (§5) separates the two.

## 1. Universe and window (selection layer unmoved)

- Selection layer: `sapta_owner_SPEC.md` + Amendments
  A1–A4; stored selections in `sapta_owner_selections.json`
  (quarterly top-7 indices by trailing 126-day PROXY
  return; top-3 picks per index under the Nifty 100 ∪
  Midcap 150 membership, F&O, liquidity ≥ ₹5 cr and ₹2,000
  constraints). The rotating active map of Designs 12–23
  is unchanged: a name is **in the pool** on a date iff
  that date is in its active set.
- **Daily data (new source, disclosed):** daily closes
  from the full-NSE daily dump `universe_daily/<SYM>.parquet`
  (2019-01-01 → 2026-11-13, one row per trading day:
  date/open/high/low/close/volume). The trading calendar
  is RELIANCE's parquet date list. A name with no parquet
  file cannot trade (counted as a data note).
- Window: rebalances from the first trading day of
  January 2025 through the first trading day of November
  2026; every position still open at the window end is
  force-closed at the 2026-11-13 close. A trade's year is
  its ENTRY year (family convention).
- **KNOWN LIMITATION (carried):** current (Nov 2026)
  constituent lists applied to a 2025–2026 backtest carry
  constituent look-ahead / survivorship bias; index series
  are constituent-average PROXY series.

## 2. The book — RS63 (frozen, no free parameters left)

- **Rebalance dates:** the first trading day of each
  calendar month (RELIANCE calendar), 2025-01 → 2026-11
  (23 rebalances). All executions at the rebalance date's
  daily **close**.
- **Rank:** on rebalance date R, for each pool name, the
  trailing **63-trading-day return** on the name's own
  daily series: with closes strictly before R denoted
  c₁…c_m (the name's own trading days), the return is
  c_m / c_{m−63} − 1. A name with m < 64 is **unrankable**
  at R. Ranks are descending by return; ties break by
  symbol ASC (deterministic).
- **Bands:** entry band = ranks **1–7**; hold band =
  ranks **1–14**; maximum holdings = **7**. LONG only,
  100 shares per holding, one position per name.
- **Rebalance procedure at R (in this order):**
  1. Compute ranks over the pool at R.
  2. **Exit** every holding that at R is (a) not in the
     pool → reason `universe_exit`; (b) in the pool but
     unrankable → `unrankable`; or (c) ranked worse than
     14 → `rank_decay`. Exit price = the name's close
     on R; if the name has no close on R, its last close
     strictly before R (counted as a data note).
  3. **Enter**, in rank order, pool names ranked 1–7 not
     already held, until holdings reach 7 or the entry
     band is exhausted. Entry price = close on R; a
     candidate with no close on R is skipped (counted).
- **Window end:** holdings still open after the last
  rebalance are closed at the 2026-11-13 close, reason
  `window_end`.
- **Costs (per the design brief):** ₹40 on **every entry
  AND every exit** — ₹80 per completed trade, heavier
  than the family's ₹40 round-trip convention used by
  the gated intraday books and by EKAM's published
  lines. Net = (exit − entry) × 100 − ₹80. Disclosed
  wherever this book is compared.

## 3. The gate (unmoved — `sapta_owner_engine.gate`)

Applied on the book's final form; all four legs must pass:

- Net positive in **both** 2025 and 2026;
- Beats the **random-selection placebo 90th percentile
  in both years** (200 draws; recipe in §4);
- **Ex-top-3** positive in both years (ex-top-1 if a
  year has <10 trades);
- No month worse than **−₹15,000 at book level** (the
  standing `gate()` convention: month of the trade's
  exit stamp). Month tables are additionally reported
  by entry month;
- **Timing/leak audit clean under an independent-path
  validator** (`sapta_d24_audit.py`, §6).

Reported with the gate: trade count, win rate, max DD,
November 2026 slice (entries 2026-11-01 → 2026-11-13),
October 2025 and October 2026 slices (by entry month),
full month table by entry month, top contributors.

**Fifth line — the owner's EKAM bar:** the book's net
per year against Cand-1 (+₹62,164.57 / +₹63,883.60) and
Cand-2 (+₹45,300.64 / +₹72,605.30). The bar is MET only
if the book's net ≥ the higher EKAM candidate in BOTH
years (2025 ≥ ₹62,164.57 and 2026 ≥ ₹72,605.30);
shortfalls are reported per candidate per year. A gate
pass alone does not answer the bar.

## 4. Placebo (random selection, same holding schedule)

Adaptation of the programme's standing book placebo to a
selection book, frozen here:

- For each entry date, the book's **taken entries that
  date**, each with its realised exit date (the real
  trade's schedule). 200 draws, seed = 24000 + draw
  index.
- Within a draw, real trades are processed in
  (entry date, symbol) order. Each real trade is matched
  to a drawn name: drawn uniformly from that entry
  date's **active pool** (names in the pool that date
  with a parquet series), excluding any name the draw
  already holds over an overlapping window (drawn entry
  ≤ real exit date and drawn exit ≥ real entry date);
  up to 200 attempts per placement, after which the
  placement is skipped and counted.
- The drawn position enters at the drawn name's close
  on the real entry date and exits at its close on the
  real exit date (last close on/before the date if the
  name did not trade that day; a name with no close
  on/before the entry date cannot be drawn). Net per
  drawn trade = (exit − entry) × 100 − ₹80, accumulated
  by entry year into the (200 × 2) array `gate()`
  consumes. This preserves the book's entry dates,
  holding durations and trade counts exactly; only the
  selection is random.

## 5. Diagnostic — RS63-F25 (NOT a second book, NOT gated)

The identical frozen rule (§2: 63-day rank, entry band
1–7, hold band 1–14, max 7 holdings, monthly rebalance,
₹80 round-trip cost) run with the pool = **EKAM's frozen
25** on every rebalance date (the 25 names of
`data/tarang_vol/`). Reported beside the main book:
nets both years, trade count, win rate, max DD, month
table, November and October slices, and the §4 placebo
percentiles as diagnostics only. Its purpose is
separation: if RS63 fails on the rotating universe but
the same rule earns on the frozen 25, the binding
constraint is the universe; if both fail, it is the
selection surface itself. No gate verdict is pronounced
on it and no book is built from it in this design.

## 6. Controls (mandatory, before any Design 24 number is quoted)

- **C-1..C-4 — programme standing controls, verbatim**
  (`sapta_d3_run.controls()`, preceded by
  `sapta_d3_run.load_data()` exactly as in Designs
  19/21/22/23): C-1 clone parity of CAND-T5 and S2 on
  the frozen 25; C-2 exit prices vs EKAM `exit_x2p`;
  C-3 vote truncated recompute (frozen-25 and SAPTA
  union); C-4 daily clone parity. ALL must pass.
- **C-24a — Design 16 anchor:** Design 16's full union
  pipeline (union candidates → `allocate25` → TRAIL
  re-exit) re-run inside this run reproduces SAPTA's
  gated union book exactly: **424 taken trades**, the
  taken (sym, date) set identical to
  `sapta_d16_trades.csv` (book GAPFADE-UNION), nets
  **+₹1,36,826.29 (2025) / +₹24,893.52 (2026)**, re-TRAIL
  parity counters at zero.
- **C-24b — Design 21 RXUNION anchor:** the RXUNION
  build (Design 16 union candidates + Design 19
  GF-FILL3 candidates → `merge_pools` → `allocate21` →
  TRAIL re-exit of the INTRA legs) re-run inside this
  run reproduces Design 21's gated book exactly:
  **423 taken trades**, the taken (sym, date) set
  identical to `sapta_d21_trades.csv` (book RXUNION),
  nets **+₹86,256.44 (2025) / +₹28,448.67 (2026)**,
  re-TRAIL parity counters at zero.

Any control failure aborts the run before book scoring.

## 7. Audit (independent path — `sapta_d24_audit.py`)

Separately written from the scorer; shares no code path
with it beyond the frozen data stores and the stored
selections file. Daily closes loaded from the parquet
dump via an independent reader; the active map rebuilt
independently from `sapta_owner_selections.json` + the
RELIANCE calendar; ranks, rebalances, entries, exits and
nets re-derived from scratch; the written
`sapta_d24_trades.csv` re-summed per book per year
against `sapta_d24_results.json`. As a disclosed data
note (not a gate leg), the audit also cross-checks a
sample of parquet daily closes against the 5-min
stores' last-bar closes. **No Design 24 number is
reported until the audit is CLEAN.**

## 8. What this design does not do

No intraday signal of any kind; no stop, target or
trailing exit; no shorts; no change to any frozen
stream, book, universe or selection; no per-entity
tuning; no Daily line (closed in Design 14); no second
selection variant (one lookback, one band pair, frozen
above). Nothing is armed; no paper run is started by
this design under any outcome.

## 9. Design-25 seed rule (pre-registered)

- If RS63 passes the gate: Design 25 anatomises the
  book (rank-band occupancy, turnover cost share,
  per-quarter and per-entity contribution) and tests
  exactly the one variation the anatomy indicts —
  named in the Design 24 report — under the same gate
  and bar; forward paper only on the owner's explicit
  approval.
- If RS63 fails the gate: the report's diagnosis decides
  the seed — universe-bound failure (diagnostic earns,
  book does not) sends Design 25 at the universe
  construction; selection-bound failure (both fail)
  closes the selection surface and sends Design 25 to
  the one remaining untested surface named in the
  Design 24 report. The seed is written from the
  measured anatomy, never pre-invented here.
