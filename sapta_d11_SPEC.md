# SAPTA Design 11 — SPEC (pre-registered)

**Pre-registered:** 2026-11-18, before any Design-11 scoring.
**Authority:** the owner's standing mandate (2026-11-17 20:41 IST, reaffirmed
21:14 IST) — SAPTA iterates design-from-diagnosis until a gate pass at EKAM's
standard or the owner's stop. SAPTA is the priority programme.
**Status:** NOT SCORED. No Design-11 parameter has been tuned against any result.

**What is FIXED from Designs 1–10 (unchanged, not re-decided):** the selection
layer of `sapta_owner_SPEC.md` as amended (A1–A4) — quarterly causal ranking
(stored top-7 lists, descending trailing-126-day PROXY return), stock
constraints (Nifty 100 ∪ Midcap 150 membership, F&O-segment filter,
≥ ₹5 cr median-60 traded value, owner's ₹2,000 cap, ≥127-bar history), stored
as `BASE_PICKS` / `PICK_OF` in `sapta_d3_run` and reused verbatim; the GATE
(`sapta_owner_engine.gate`, verbatim); basis — equity cash, PROVISIONAL per
100 shares, ₹40/trade, paper only, real money ₹0, no stock options. Stores:
`data/tarang_vol/`, `data/sapta_vol/`, `data/tarang_wide_vol/` (5-min volume
bars), `universe_daily/` (daily). Windows: entries 2025-01-01 → 2026-11-13;
November slice = entries 2026-11-01 → 2026-11-13. The intraday shells are
EKAM's verbatim (six votes, `day_candidates` first-signal generation, CAND-T5
exit stack D=3, S=1.00%, C=none, base threshold T=5; caps 5 for Cand-1, 3 for
Cand-2). The daily machine is Daily-3's base form (`sim4c_gated`, gate open;
firing set {BB, RSI, MACD} under the EKAM-3 merge rules, upgrade on, RSI exit
70, no stop; native CAP ×1.10, native TIME 60) — the machine whose native run
on the rotating selections reconstructs the published base book
+₹106,654.10/+₹94,279.00, 325 trades (control C-5). **There is NO per-entity
tuning programme and NO stock replacement in Design 11.**

**Design 10's diagnosis (the seed).** Design 10's controls were exact
(C-1…C-5, C-16) and its audit clean, so its measurements are clean:

1. **Intraday:** the transplant fails at every scale now measured — pooled
   (D4–D9), sliced (D3, D8, D9) and standalone (D10: Metal loses before
   costs, gross/trade −₹14.52/−₹2.29; Realty 0/4). One cell remains untested
   before the line is measured-exhausted at every scale: a **two-sector pair
   book** — Realty + Pharma, the two sleeves with repeated p90 timing legs
   across Designs 3–10 — traded as ONE 6-name book under one cap, so the
   shell's cap selection has a small cross-section to select from without
   sector-slicing the whole pool.
2. **Daily:** three explanations of the placebo failure are falsified —
   rotating universe (D9: the failure follows the machine home), loosened
   exits (D8/D9), fixed 5-day entry lag (D10: percentiles 10.0/11.5 →
   8.0/30.0, 2025 net −₹38,585; the signal is regime occupancy, not a
   systematically-early drift marker). The remaining side of the timing
   claim is the EXIT side: the machine's signal exits (band/RSI/MACD,
   CAP, TIME) have never been replaced wholesale by a **fixed horizon**.
   If shifted/fixed exits also match or beat the machine's, the honest
   SAPTA-Daily form is a pure regime-occupancy basket and the timing claim
   is closed on both sides.

**What CHANGES in Design 11 — two moves, one per open surface:**

---

## §1 Intraday-11 — Realty + Pharma pair book

- **Entities (exactly two):** `Nifty Realty` and `Nifty Pharma`.
- **Construction:** the stored open-universe selection layer — rotating
  quarterly top-7 membership (an entity contributes its picks only in
  quarters where it appears in the stored top-7 lists), top-3 picks per
  entity per quarter from `BASE_PICKS` / `PICK_OF`, exactly as Designs
  1–10 stored them. No pool restriction (Design 8's frozen-25 pool layer
  is NOT applied), no freeze (Designs 5/9 are NOT applied).
- **One pair book:** the pair active map is, per name, the UNION of the
  two entities' active date sets. The book is simulated on that union
  with EKAM's shells verbatim (Cand-1 form and Cand-2 form = two books),
  caps binding AT BOOK LEVEL: earliest-5 (Cand-1) / earliest-3 (Cand-2)
  across the pair's signalling names each day, via
  `run_intraday_group` exactly as coded. A name picked by both entities
  in a quarter trades once (it appears once in the union map).
- **Gate (book level; the programme's 4-leg gate):** `gate()` verbatim
  with `worst_month_floor = −₹15,000`, plus `fix_chrono` as in every
  intraday design — net positive both years; beats the random-entry
  placebo p90 in both years (percentiles stated); ex-top-3 positive both
  years; no month worse than −₹15,000. November reported, not gated.
- **Placebo (book):** Design 3's recipe verbatim — per (name, year),
  `placebo_intraday_d3` on the book's trades for that name-year (200
  draws, seeds `stable_seed('D11', book, 'PAIR', name, year)`), draws
  summed across the book's names per year.
- **Sleeves (reported):** each book trade is attributed to its owning
  entity — the quarter containing the entry date, and among the pair the
  entity appearing EARLIER in that quarter's stored top-7 order whose
  `PICK_OF` contains the name (Amendment A4's ownership convention).
  Sleeve gates use the same `gate()` with per-sleeve placebo draws
  (`placebo_intraday_d3` on the sleeve's per-(name, year) trade subsets,
  seeds `stable_seed('D11', book, entity, name, year)`) and
  `worst_month_floor = None` (owner SPEC §6: the month floor is a
  book-level leg only) — disclosed here, applied to no other line.
- **Controls:** C-1…C-4 (Design 3's, verbatim re-run) must pass before
  any Design-11 intraday number is quoted.

## §2 Daily-11 — the fixed-horizon basket

- **Entries — EXACTLY the base machine's:** the native run of the Daily-3
  base machine (`sim4c_gated`, gate open) on the ROTATING SAPTA
  selections (the union of `BASE_PICKS` — the same active map whose
  native run reconstructs the published base book +₹106,654.10/
  +₹94,279.00, 325 trades; control C-5). Every native entry is taken:
  same name, same signal day, same entry day, same entry price
  (the open of the entry day on the name's own daily series).
- **The ONE change — fixed-horizon exit.** Day-count convention, stated
  exactly: let `e` be the entry day's index in the name's own daily
  series (the entry fills at `o[e]`). **The entry day is day 0. The
  position exits at the CLOSE of series day `e + 20`** — the 20th
  trading day after the entry day, on the name's own series (series
  days, not calendar days). If `e + 20` lies beyond the series end, the
  position exits at the close of the last series day (`n − 1`),
  exit_kind `FORCED` — the programme's window_end convention; otherwise
  exit_kind `HORIZON20`. **No other exit applies:** no band exit, no
  signal exit (BB/RSI/MACD), no CAP, no TIME, no upgrade conversion.
  Net per trade = (exit close − entry open) × 100 − ₹40.
- **Basket form (disclosed):** positions are independent — all 325
  native entries are held to their own horizon even where two positions
  in the same name overlap in time (the native machine's occupancy rule
  does NOT carry into the basket; the native entry set is an input, not
  re-simulated). Overlapping position pairs per name are counted and
  reported.
- **Placebo:** the standing recipe (owner SPEC §7 / Amendment A3 §4)
  with the variant's own exit rule — the fixed horizon: per real trade,
  an entry day drawn uniformly from the name's selected days in the same
  quarter-window (windows as in Designs 8–10) whose prior day carries a
  non-empty firing set (BB or RSI or MACD) and which is not the series'
  last day; the placebo net is the horizon net of that drawn day —
  (close at min(idx + 20, n − 1) − open at the drawn day) × 100 − ₹40;
  an empty sample space contributes 0. 200 draws, seeds
  `stable_seed('D11', 'DAILY', 'HORIZON20', name)`, nets bucketed by the
  REAL trade's entry year. The null is random entry under the SAME exit
  rule, so the placebo leg isolates entry timing given the horizon exit
  — the same construction principle as Design 10 §2 (there the delay was
  under test and the null was immediate entry; here the exit is the
  design's form and both real and placebo trades carry it).
- **Controls:** C-1…C-4 and C-5 as in Design 10, plus **C-17 (horizon
  identity):** (a) every base entry price equals the prepared series
  open at its entry-date index (all base trades, both books' source);
  (b) every Daily-11 trade satisfies exit_index − entry_index = 20, or
  exit_index = n − 1 (series end), and its exit price equals the
  prepared series close at the exit index. No Daily-11 number is
  quoted unless C-5 and C-17 pass.
- **The decisive comparison (pre-registered):** HORIZON-20 vs the BASE
  book (native entries AND native exits, same run, gated with the
  standing native-exit placebo, seeds
  `stable_seed('D11', 'DAILY', 'BASE', name)`) — nets by year, placebo
  percentiles by year, worst months, ex-top-3. The question is stated
  before scoring: *was the machine's exit timing the noise, or is the
  entry signal regime occupancy all the way down?* The fixed-horizon
  form answers it if its placebo percentiles rise materially above the
  base's (~10/11.5 family) while its nets hold or improve; it is
  falsified if the horizon book merely re-prices the same occupancy
  (percentiles unmoved) or pays for gentleness with the harvest.

## §3 Gate, reporting, audit

- Gate: `sapta_owner_engine.gate` verbatim, 4 legs, worst-month floor
  −₹15,000 at book level (Daily-11 as in Designs 3–10; Intraday-11
  book per §1; Intraday-11 sleeves per §1 with floor None). No leg is
  moved for either line. November slice reported for every book.
- Per book: every leg, percentiles, WR, trades, max DD, month tables,
  top contributors, gross/cost/net per trade, and the power comparison
  against EKAM (Cand-1 +₹62,165/+₹63,884 · Cand-2 +₹45,301/+₹72,605 ·
  Daily +₹42,955/+₹1,41,328). Daily-11 additionally reports the
  overlap count and the base-vs-horizon head-to-head of §2; Intraday-11
  additionally reports both sleeve gates per book.
- Audit: independent-path verifier (`sapta_d11_audit.py`), separately
  written — intraday exits re-derived from each trade's own-day bars
  plus the square-off-price regression check and per-day pair-cap
  verification over the finals pair map; Daily-11 re-derived from daily
  parquets loaded directly: the audit-side native machine (offset-1
  delayed driver of the Design-10 audit) reproduces the BASE entry
  set, and the audit applies its own horizon transform (entry index
  from raw dates, close at min(e + 20, n − 1)) and compares
  trade-for-trade. The verdict is appended to the report only after
  the audit runs.

**Deliverables:** `sapta_d11_SPEC.md` (this file) · `sapta_d11_report.md` ·
`sapta_d11_results.json` · `sapta_d11_trades.csv` · Design-11 section in
`sapta_tuning_registry.md`.
