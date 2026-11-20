# SAPTA Design 4 — SPEC (pre-registered)

**Pre-registered:** 2026-11-17, before any Design-4 scoring.
**Authority:** the owner's standing mandate (2026-11-17 20:41 IST, reaffirmed
21:14 IST) — SAPTA iterates design-from-diagnosis until a gate pass at EKAM's
standard or the owner's stop. SAPTA is the priority programme.
**Status:** NOT SCORED. No Design-4 parameter has been tuned against any result.

**What is FIXED from Designs 1–3 (unchanged, not re-decided):** the selection
layer of `sapta_owner_SPEC.md` as amended (A1–A4) — quarterly causal ranking,
top-7 performing indices (PROXY series), top-3 stocks per index under Nifty 100
∪ Midcap 150 membership, F&O-segment filter, ≥ ₹5 cr median traded value,
owner's ₹2,000 cap; selections reused: `sapta_owner_selections.json` (the same
selection objects as Design 3, imported from `sapta_d3_run`); the GATE
(`sapta_owner_engine.gate`, verbatim; worst-month floor −₹15,000 at book level
only); basis — equity cash, PROVISIONAL per 100 shares, ₹40/trade, paper only,
real money ₹0, no stock options. Stores reused: `data/tarang_vol/`,
`data/sapta_vol/`, `data/tarang_wide_vol/` (5-min volume bars),
`universe_daily/` (daily). Windows: entries 2025-01-01 → 2026-11-13; November
slice = entries 2026-11-01 → 2026-11-13.

**Design 3's diagnosis (the seed).** Design 3's controls were exact (the build
reproduces EKAM's published CAND-T5 and S2 lines to the paisa on the frozen
25), so its measurements are clean: EKAM's intraday edge does not live in
"first signal of the day, one trade per name" alone — transplanted verbatim
into 3-name entities it lost money almost everywhere (book C1 −₹26,280 /
−₹67,316, C2 −₹20,288 / −₹41,060, 1/14 entities passing — Nifty Auto), because
the earliest-5/3 cap across 25 names *is* the selection mechanism and a 3-name
entity has nothing to select from. The daily machine (EKAM-2c + MACD restored)
is genuinely strong on money (final +₹165,504 / +₹108,959) and weak only on
timing proof: placebo 18.0 / 12.5 (day-shifted entries harvest nearly the same
money — the book rides these names' drift more than its signals) and the
worst-month floor (Jan 2025 −₹68,025, final form).

**What CHANGES in Design 4 — two moves, one per failing mechanism. There is
NO per-entity tuning programme and NO stock replacement in Design 4** (those
were the entity-layer structure Designs 1–3 exhausted; Design 3's diagnosis is
that the entity layer itself is the intraday problem, and the daily problem is
entry context, not per-entity parameters):

1. **Intraday (Cand-1 / Cand-2):** EKAM's candidate shells VERBATIM — the six
   votes, `day_candidates` first-signal generation, the CAND-T5 exit stack
   (D=3, S=1.00%, C=none), base threshold T=5 — but run across the **full
   quarterly universe as ONE book**: per quarter, the union of the top-7
   entities' picks (a name picked by two entities trades once); a name is
   active on the dates of every quarter where it was picked. The earliest-5
   (Cand-1) / earliest-3 (Cand-2) day cap binds **at book level** across the
   whole union — restoring the cross-sectional selection Design 3 isolated.
   Entities are kept as **reporting sleeves** only (§3); the **book gate is
   the verdict**.
2. **Daily-4:** Daily-3's machine FROZEN at its base form — `sim3c_gated`,
   firing set {BB, RSI, MACD} under the EKAM-3 merge rules, upgrade on,
   TIME 60, RSI exit 70, no stop — run per name over the union of its pick
   intervals (book construction), **plus a 200DMA trend gate on entries**
   (§4). The ungated twin (identical run with the gate open) is scored
   alongside as the direct Daily-3-base comparison.

---

## 1. Controls (mandatory, before any Design-4 scoring)

- **C-1…C-4:** Design 3's controls, re-run verbatim (`sapta_d3_run.controls`):
  clone parity of CAND-T5 and S2 on the frozen 25 (published totals 2025
  +₹62,164.57 / 2026 +₹63,883.60 and +₹45,300.64 / +₹72,605.30), exit-price
  identity vs `exit_x2p`, truncated vote recompute on the frozen 25 and the
  SAPTA union, daily clone parity (BB+RSI lists = `sim2c` on all 25, stats =
  published EKAM-2c, MACD-only lists = `EKAM.sim`). Any failure stops the run;
  no Design-4 numbers are produced.
- **C-5 — Daily-3 base book reconstruction.** Design 4's ungated daily run
  (book construction, base form) must reproduce Design 3's published book-base
  line exactly: **325 trades, net 2025 +₹106,654.10, net 2026 +₹94,279.00,
  November +₹17,365.00** (`sapta_d3_results.json`, BOOK DAILY [base] gate).
  Any mismatch stops the run.

## 2. Intraday books — construction

- Variant for every name: (T, D, S, C) = (5, 3, 1.00%, none) — EKAM
  CAND-T5/S2 verbatim. Candidate generation and exits are Design 3's engine
  (`run_intraday_group`, `exit_d3`), unchanged.
- Active map: for each name, the union over entities of its pick-date sets
  (`BASE_PICKS` aggregated across entities — the same objects Design 3
  built). One run per book over the full union; day cap 5 (Cand-1) / 3
  (Cand-2) applied across all candidates of the day, sorted by
  (signal stamp, symbol) — EKAM's own selection rule, now at book level.
- Tradable-day rule, NC days (2025-10-21), warm-up and vote conventions:
  EKAM's, via Design 2's `VoteData` bundles, exactly as Design 3.

## 3. Sleeves (reporting only)

- **Ownership (A4):** a trade on date d belongs to the entity that owns its
  name in the quarter containing d — the highest-ranked entity (earliest in
  that quarter's top-7 order) that picked the name that quarter.
- Per sleeve, reported for the record: trades, net 2025 / 2026, November,
  win rate, max drawdown, ex-top-3 both years, placebo percentile both years,
  and the 4-leg gate core (no month floor at sleeve level — the floor is a
  book-level leg). Sleeve placebos: intraday — per (name, quarter) subsets of
  the book's trades, Design 3's recipe (`placebo_intraday_d3`), summed over
  the sleeve's subsets; the book placebo is the sum over all subsets. Daily —
  per name, `placebo_daily_d4` (§5) over the sleeve's trades of that name,
  summed.
- The **book gate is the verdict** for each book. Sleeve pass counts are
  reported transparently alongside (including whether the owner-spec §6
  majority condition would have been met), but they do not declare the book.

## 4. Daily-4 — the 200DMA trend gate

- For name with daily closes c[·] (its full `universe_daily/` series), the
  gate at signal day i is: **i ≥ 199 AND c[i] > MA200[i]**, where
  MA200[i] = mean(c[i−199 … i]) — 200 closes up to and including the signal
  day, causal. If i < 199 the name is **ineligible that day (short
  history)**; if c[i] ≤ MA200[i] the entry is **vetoed (below trend)**.
- Machine semantics identical to the `active`-day gating in `sim3c_gated`:
  when flat at day i with a non-empty firing set and entry day i+1 active, the
  position opens at i+1's open **only if the gate passes at i**; otherwise the
  machine stays flat and advances — the (single-day) signal is missed, exactly
  as a non-active entry day is missed in Designs 2–3. Upgrade, exit
  governance, TIME/CAP, FORCED and window-end handling are unchanged.
- **Disclosures (mandatory in the report):** (a) the count of entry signals
  vetoed while flat, split by reason (below trend / short history), per year;
  (b) the trade diff vs the ungated twin — entries removed (in ungated, not
  in gated; count and net), entries added by state divergence (in gated, not
  in ungated; count and net); (c) the Jan-2025 month for the ungated twin and
  for Daily-4, on the gate's exit-month basis and on an entry-month basis;
  (d) per-name counts of signal days with < 200 closes in the entries window.

## 5. Placebos (200 draws, D1 `stable_seed` convention)

- **Intraday:** Design 3 §7 verbatim — per real trade (date, name, side
  preserved), entry bar drawn uniformly from that (date, name)'s eligible
  entry bars (tradable day; entry stamp in [09:20, 15:10]); exit by the base
  exit stack on the real bars and vote series; drawn trades independent.
- **Daily-4:** per real trade, an entry day drawn uniformly from the name's
  selected days in the same quarter-window whose **prior day carries a
  non-empty Design-3 firing set (BB or RSI or MACD) AND passes the 200DMA
  gate**, and which is not the series' last day; a standalone gated machine
  (only that entry day allowed, gate active) produces the placebo trade's
  net; an empty sample space contributes 0 for that trade. (The sample space
  is the set of days the Daily-4 machine itself could have entered — the
  placebo randomises timing *within the design's own rules*, gate included;
  disclosed here because it differs from Design 3's ungated space by exactly
  the gate condition.)

## 6. The gate (unmoved) and reporting

`sapta_owner_engine.gate` at book level with worst-month floor −₹15,000;
intraday worst-month / max-DD recomputed chronologically (`fix_chrono`, as
Design 3 — EKAM rows carry time-of-day exit stamps). Legs: net positive in
both 2025 and 2026 · beats the random-entry placebo 90th percentile in both
years (percentiles stated) · ex-top-3 positive in both years · no month worse
than −₹15,000 (book level) · audit clean (§7). November slice reported with
every gate.
**Power comparison:** each book against its EKAM counterpart (Cand-1
+₹62,165/+₹63,884 · Cand-2 +₹45,301/+₹72,605 · Daily +₹42,955/+₹1,41,328),
per year on net, with DD and WR alongside: meets / beats / falls short.
**Per book the report states:** every gate leg, percentiles, WR, trades, max
DD, month table, top contributors, gross/cost/net per trade (gross = net +
₹40 × trades), the sleeve table, and the vs-EKAM verdict. For Daily-4
additionally the §4 disclosures and the ungated twin's full gate line.

## 7. Audit (independent path)

`sapta_d4_audit.py`, written separately from the engine (the Designs 1–3
method): plain-loop indicator implementations; for intraday — FIRST-SIGNAL
verification under the audit's own vote series, entry-fill checks, own-day
exit re-derivation from raw bars, square-off regression (every square-off
exit price = its own date's 15:10 bar close), and the book-cap check (per
day, the taken set equals the earliest-cap candidates under the audit's own
candidate scan); for Daily-4 — independent BB/RSI/MACD recomputation, an
independent MA200, a separate gated state-machine re-run per name, trade
lists compared trade-for-trade, and verification that every gated trade's
signal day passes the gate and every vetoed-while-flat signal in the audit's
own run matches the engine's veto counts by reason. Named conventions from
Designs 1–3 carry over: (i) indicator-seed disagreement, if any, only in the
first morning of a store (2025-01-01), reported by count; (ii) 2025-10-21 is
NC — no intraday trade may be dated 2025-10-21. Any other mismatch = audit
not clean, and the affected gate legs fail honestly.

## 8. Deliverables

`sapta_d4_SPEC.md` (this file) · `sapta_d4_report.md` ·
`sapta_d4_results.json` · `sapta_d4_trades.csv` · a Design-4 section appended
to `sapta_tuning_registry.md` (earlier sections untouched).
