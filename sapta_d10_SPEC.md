# SAPTA Design 10 — SPEC (pre-registered)

**Pre-registered:** 2026-11-18, before any Design-10 scoring.
**Authority:** the owner's standing mandate (2026-11-17 20:41 IST, reaffirmed
21:14 IST) — SAPTA iterates design-from-diagnosis until a gate pass at EKAM's
standard or the owner's stop. SAPTA is the priority programme.
**Status:** NOT SCORED. No Design-10 parameter has been tuned against any result.

**What is FIXED from Designs 1–9 (unchanged, not re-decided):** the selection
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
native exit set exactly as Design 8 SPEC §2 — firing set {BB, RSI, MACD}
under the EKAM-3 merge rules, upgrade on, RSI exit 70, no stop; governed
subset = positions whose comps contain RSI plus upgraded ('BB',) positions,
TIME/CAP skipped on the conversion day; native CAP ×1.10, native TIME 60).
**There is NO per-entity tuning programme and NO stock replacement in
Design 10.**

**Design 9's diagnosis (the seed).** Design 9's controls were exact
(C-1…C-5, C-12…C-15) and its audit clean, so its measurements are clean:

1. **Intraday:** the pool × freeze grid is complete and every cell fails.
   Every universe layer is now isolated — shell, cap, rotation, pick rule,
   rank direction, name pool, freeze — and no sector-sliced subset of the
   curated 25 reproduces EKAM's whole-pool edge (Design 3's finding). The
   transplant question is closed at BOOK scale. One scale remains untested:
   the ENTITY scale. Designs 1–9 always gated entities as sleeves inside a
   book or tuned them inside one; two entities have repeatedly posted the
   programme's best sleeve timing legs without ever being run as standalone
   books — **Nifty Metal** (in the top-7 for six of eight quarters) and
   **Nifty Realty** (positive both years in all three books across Designs
   1–3, best timing legs in Designs 5–6, but fields no names under the
   frozen constructions). Design 10 runs exactly those two entities as
   STANDALONE books: *does SAPTA survive as a one-sector book?*
2. **Daily:** the placebo failure is a MACHINE property. On EKAM's own
   frozen-25 home universe the native-exit control posts placebo
   60.5/**6.0** — in 2026, ~94% of random shifted entries on the machine's
   own names beat the machine's own timing; the failure follows the machine
   home, and the loosened exits (Design 8's pair) do not travel with it.
   Every entry-side SUBTRACTION has been falsified (Designs 4–7) and every
   exit-side change is spent (Designs 7–9). The one entry-side move never
   tested is not a subtraction but a SHIFT: **delay the entry 5 trading
   days.** If the machine's signals are drift markers whose timing is
   systematically early — exactly what the placebo keeps ruling — entering
   5 days later should keep the drift and drop the early-entry damage.

**What CHANGES in Design 10 — two moves, one per open surface:**

---

## §1 Intraday-10 — single-entity books (Metal, Realty)

- **Entities (exactly two):** `Nifty Metal` and `Nifty Realty`.
- **Construction:** rotating quarterly top-7 membership — an entity is
  active only in quarters where it appears in the stored top-7 lists —
  with the entity's top-3 picks from the **open-universe** selection layer
  (the stored `BASE_PICKS` / `PICK_OF` of Designs 1–7; the Design-9 seed's
  phrase "Design-8 rotating pool form" is read per the Design-10 tasking
  as: D8's rotating-membership construction with open-universe picks —
  the pool-restricted pick layer is NOT applied here, and that reading is
  disclosed in the report).
- **Standalone books:** each entity runs alone — its own (up to) 3 names
  per quarter, EKAM shells verbatim (Cand-1 form and Cand-2 form = four
  books total), caps binding WITHIN the entity: the shell caps (5 for
  Cand-1, 3 for Cand-2) apply across the entity's signalling names each
  day, and EKAM's per-name rule (at most one candidate per name-day) is
  structural in `day_candidates`. With ≤3 names the shell caps bind only
  trivially; they are applied exactly as coded, not adjusted.
- **Gate (per the Design-10 tasking; the programme's 4-leg gate):**
  `gate()` verbatim with `worst_month_floor = −₹15,000` — net positive
  both years; beats the random-entry placebo p90 in both years
  (percentiles stated); ex-top-3 positive both years; no month worse than
  −₹15,000. (The owner SPEC applied the month floor at book level only;
  the Design-10 tasking applies it to these standalone entity books —
  a tightening, disclosed, applied to no other line.) November reported,
  not gated.
- **Placebo:** Design 3's recipe verbatim — per (name, year),
  `placebo_intraday_d3` on the entity's trades (200 draws, seeds
  `stable_seed('D10', book, entity, name, year)`), draws summed across
  the entity's names per year.
- **Controls:** C-1…C-4 (Design 3's, verbatim re-run) must pass before
  any Design-10 intraday number is quoted.

## §2 Daily-10 — the entry-delay line

- **Machine:** the Daily-3 base machine exactly as in Designs 3–9
  (firing set {BB, RSI, MACD}, EKAM-3 merge rules, upgrade on, native
  exits CAP ×1.10 / TIME 60, governed subset as fixed above), on the
  ROTATING SAPTA selections (the union of `BASE_PICKS` — the same active
  map whose native run reconstructs the published base book
  +₹106,654.10/+₹94,279.00, 325 trades; control C-5).
- **The ONE change — entry delay δ = 5 trading days** (on the name's own
  daily series; signal day index s, all indices below are series indices):
  1. **Candidacy (native):** a signal fires on day s while the machine is
     flat, with a non-empty firing set on day s, `s + 1 < n`, and
     `dates[s+1] ∈ active` — exactly the native machine's candidacy.
  2. **Fill:** the entry is filled at the open of day `f = s + 5`, at
     `o[f]`, with the firing set of day s as the position's comps —
     only if `f < n` and `dates[f] ∈ active` (selection governs the
     actual entry day, as it governs the native entry day). Otherwise
     the signal is discarded (counted: `no_room` if `f ≥ n`,
     `fill_gate` if `dates[f] ∉ active`) and scanning resumes at `s + 1`.
  3. **Causal skip check:** before filling, run the HYPOTHETICAL native
     trade — entered at `o[s+1]` with day-s comps, native exit
     governance — over trigger days `s+1 … f−1` ONLY. If any exit
     completes from those trigger days (execution index ≤ f), the
     signal is SKIPPED (counted) and scanning resumes at `s + 1`.
     Causality: every input to this evaluation is a bar of a day
     strictly before f, fully known at the open of day f. An exit
     executing AT the open of day f (a SIGNAL exit triggered by the
     close of day f−1) counts as fired — the native position closes at
     the very open the delayed fill would use. An intraday execution on
     day f itself (CAP on day f's high) is NOT knowable at f's open and
     does not cause a skip. TIME (60) cannot fire inside a 4-day window.
  4. **After a fill:** exit governance runs from day f with the actual
     entry price `o[f]` — CAP ×1.10 from the actual entry, TIME 60
     counted from f, signal exits and the BB→RSI upgrade conversion
     evaluated on held days ≥ f. After an exit at index xi, scanning
     resumes at xi (the native convention). End of series: FORCED at
     the last close (native). One open position per name (structural).
     Disclosed divergence: after a skip/discard the delayed machine
     stays flat and resumes scanning at s+1, where the native machine
     would have been occupied — the delayed book may therefore take
     later signals the native book never sees. That is the design, not
     a defect: the delay line is a new entry rule, not a filter on the
     native trade list.
- **Placebo:** the standing recipe (owner SPEC §7 / Design 8 §4)
  verbatim — per real trade, an entry day drawn uniformly from the
  name's selected days in the same quarter-window whose prior day
  carries a non-empty firing set; a standalone stepper single with the
  book's own (native) exits produces the placebo net; 200 draws, seeds
  `stable_seed('D10', 'DAILY', 'DELAY5', name)`. Placebo entries are
  NOT delayed: the delay is the entry-timing hypothesis under test and
  the null is random immediate entry under identical exit machinery.
- **Controls:** C-1…C-4 and C-5 (base-book reconstruction) as in
  Design 9, plus **C-16 (offset-1 identity):** the delayed driver of
  §2 run at offset 1 — where the skip window is empty and the fill
  gate coincides with candidacy — must reproduce the C-5 base book
  trade-for-trade (325 trades, keyed on (sym, entry_date, exit_date,
  net)). No Daily-10 number is quoted unless C-16 passes.
- **The decisive comparison (pre-registered):** DELAY-5 vs the BASE
  book (native entries, same run, same placebo machinery, seeds
  `stable_seed('D10', 'DAILY', 'BASE', name)`) — nets by year, placebo
  percentiles by year, worst months, ex-top-3. The question is stated
  before scoring: *is the signal a drift marker whose timing is
  systematically early?* The delay line answers it if the delayed
  book's placebo percentiles rise materially above the base's while
  its nets hold or improve; it is falsified if the delay merely
  shrinks the book (fewer trades, same percentiles).

## §3 Gate, reporting, audit

- Gate: `sapta_owner_engine.gate` verbatim, 4 legs, worst-month floor
  −₹15,000 (Daily-10 as in Designs 3–9; Intraday-10 per §1). No leg is
  moved for either line. November slice reported for every book.
- Per book: every leg, percentiles, WR, trades, max DD, month tables,
  top contributors, gross/cost/net per trade, and the power comparison
  against EKAM (Cand-1 +₹62,165/+₹63,884 · Cand-2 +₹45,301/+₹72,605 ·
  Daily +₹42,955/+₹1,41,328). Daily-10 additionally reports the full
  signal funnel (signals / filled / skipped-native-exit / discarded,
  by year) and the base-vs-delayed head-to-head of §2.
- Audit: independent-path verifier (`sapta_d10_audit.py`), separately
  written — intraday exits re-derived from each trade's own-day bars
  plus the square-off-price regression check and per-day entity-cap
  verification; Daily-10 entries re-derived from the raw `sig_in`
  series (signal day, +5 fill, fill gate, skip check re-derived by an
  independent governance transcription), exits re-derived
  trade-for-trade. The verdict is appended to the report only after
  the audit runs.

**Deliverables:** `sapta_d10_SPEC.md` (this file) · `sapta_d10_report.md` ·
`sapta_d10_results.json` · `sapta_d10_trades.csv` · Design-10 section in
`sapta_tuning_registry.md`.
