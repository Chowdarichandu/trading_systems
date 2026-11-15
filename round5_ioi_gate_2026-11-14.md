# ROUND 5 — INTRADAY-OI FAMILY GATE (IOI-1 / IOI-2), BANK NIFTY

**Run date:** 2026-11-14 (the December wait is dead — see §1.0).
**Real money: ₹0.** No live trades were placed; nothing was armed,
merged or modified. Everything below is paper evidence on option
premiums **per 1 lot of 30**, cost **₹220/trade** inside every net,
buying only. Bank Nifty only (Part 7's freeze is Bank-only).

---

## 1. SPEC MAPPING — written BEFORE any scoring

### 1.0 Why this gate runs today, not ~2026-12-10

Part 7 of `oi_buildup_programme_2026-11-13.md` froze the intraday-OI
family against the **option-chain archive** (5-minute snapshots,
collecting only since 2026-11-13) and registered "no scoring before
≥ 20 complete archive days exist". The Track A audit
(`round5_data_audit_2026-11-14.md`) then established that the
**expired-instruments candle route** — a different data source for
the same quantities — returns all seven candle fields (timestamp,
OHLC, **volume**, **open interest**) bar by bar, historically:
futures 205/205 Jan–Oct days; sampled near-ATM option pairs 22/22
complete. The family's *rules* are therefore scored unchanged; only
the data source is swapped, under the mapping in §1.1, each item of
which is written down here, before scoring, as the task requires.
Rounds 1–4 stripped fields 6–7 when storing; this build preserves
all seven fields in its raw store (`round5_ioi_data/`).

### 1.1 The frozen rules (Part 7, unchanged)

- Per side S ∈ {CE, PE}, over an 11-strike near-ATM band:
  ΔOI_S = Σ (OI_S at read − OI_S at baseline); premium index
  P_S = Σ close_S over the band; ΔP_S = P_S(read) − P_S(baseline).
- Quadrant: ΔOI>0, ΔP>0 → LONG_BUILDUP; ΔOI>0, ΔP<0 →
  SHORT_BUILDUP; ΔOI<0, ΔP>0 → SHORT_COVERING; ΔOI<0, ΔP<0 →
  LONG_UNWINDING; ΔOI=0 or ΔP=0 → FLAT.
- **IOI-1 (primary):** buy CE iff CE = LONG_BUILDUP and PE ≠
  LONG_BUILDUP; buy PE iff PE = LONG_BUILDUP and CE ≠ LONG_BUILDUP.
- **IOI-2 (variant):** buy CE iff CE = SHORT_COVERING and PE ≠
  LONG_BUILDUP; buy PE iff PE = SHORT_COVERING and CE ≠ LONG_BUILDUP.
- At most one leg per family per day; IOI-1 and IOI-2 are separate
  books (a day may fire in both — never a combined position).
- Trade: entry = **open of the 11:00 5-minute premium bar**; strike
  = ATM (nearest 100) to the spot close of the 10:55 spot bar;
  contract = in-force monthly expiry; exits = stop **−50 checked
  before target +90** on every bar from the entry bar onward, fills
  at the level, **square-off at the 15:10 bar close**; 1 lot of 30;
  ₹220/trade; buying only. A premium series not covering from
  ≤ 09:20 counts as missing; an unserved series or a missing 11:00
  bar is NC, never estimated.

### 1.2 Mapping: archive snapshots → per-contract 5-minute candles

| Part 7 (archive) | This build (candles) |
|---|---|
| Baseline bucket = earliest snapshot in [09:15, 09:30] | Each band contract's **first 5-min bar of the day (the 09:15 bar)**: baseline OI = that bar's OI field; baseline premium = that bar's close |
| Read bucket = latest snapshot in [10:30, 10:55] | Each band contract's **10:55 bar**: read OI = that bar's OI field; read premium = that bar's close |
| Band = 11 strikes nearest the read bucket's printed spot | 11 strikes nearest the **10:55 spot-bar close** (stored spot series, `daily2leg/spot.json` — the November machinery's series): ATM = round(spot/100)×100, band = ATM ± 5 strikes |
| Day COMPLETE iff all 11 band rows present in both buckets with non-null OI/closes | Day is **NC (band-incomplete)** iff any band contract lacks the 09:15 bar or the 10:55 bar on that day (the audit's completeness warning: fixed far strikes have gaps; each day's band is selected from that day's spot, per §1.1) |
| Read bucket's printed spot cross-checks the spot series (> 5 pts disagreement → NC) | **Dropped, as a documented mapping decision:** the candle route carries no second spot print. The read spot comes from the single stored spot series; band/ATM derive from it alone. The guard's purpose (a bad spot print) is instead covered by the band-completeness requirement itself — a wrong spot would select strikes whose contracts fail completeness |
| Contract = the archive file's (front-monthly) expiry | In-force monthly expiry per the daily-OI dataset's expiry column (cross-validated against the contract master in rounds 1–4); band and traded contracts all from that expiry |
| Gate window = complete archive days, halves split at the window's median trading day | Window = Jan–Oct 2026 (205 trading days); **halves split at the window's median trading day** (the 103rd trading day), exactly the substitution Part 7 registered in advance |

Further mapping decisions, each forced by the data source and
recorded here before scoring:

- **OI semantics.** A candle's OI field is the open interest as of
  that bar. ΔOI therefore measures build-up from the first bar of
  the day to the 10:55 bar — the candle-native equivalent of
  baseline-bucket → read-bucket. The 10:55 bar's fields are known
  at 11:00, when the entry bar opens; the entry bar's own OHLC is
  never an input (the house convention, identical to round 4's
  10:55-bar read). Timing is asserted per trade at scoring.
- **NC accounting.** Two distinct NC kinds, reported separately:
  (a) *band-NC days* — excluded before any signal exists (counted,
  with their share of the window); (b) *scoring-NC* — a day the
  family fired on whose trade cannot be scored (missing 11:00 bar
  or unserved premium series). Part 7's gate leg "NC ≤ 5% of fired
  signal days" is applied to (b): scoring-NC / fired days ≤ 5%.
- **Placebos (Part 7, unchanged):** REVERSED direction (same days,
  same strike, opposite side); COIN-FLIP direction, seed 42 (one
  `Random(42)` stream per family, fired days in chronological
  order); TIME-SHIFTED entry (same signal/direction/strike, entry
  at the open of the **12:00** bar, exits unchanged).
- **Gate legs (Part 7, unchanged):** (1) total > 0; (2) both
  halves > 0; (3) ex-top-3 > 0; (4) total strictly beats all three
  placebos; (5) timing audit = 0 violations; (6) NC leg per above.
  Independent re-sum of the trade file must match to the paisa.
  The owner's ₹900/trade-day figure is stated beside any PASS as a
  lens, not a gate leg.
- **Merge protocol (Part 7 / rounds 1–4, unchanged):** for a
  passing family — or, if none passes, the single strongest
  failing family (highest total) as merge-only evidence —
  INCREMENT = the family's legs on days TUNED STACK v2 placed no
  leg (Jan–Oct stack ledger: `solid60_programme_2026-11-13_bank_A_
  stack_features.csv`, anchored at 111 legs / +₹127,351.50 / 89
  trade days). Merge passes only if the increment alone is net
  positive **and** the merged total beats the stack alone. The
  November counterfactual (Nov 2–13, day by day) runs beside it;
  Nov 13 is NC if its candles are unserved — never estimated.

---

---

## 2. BUILD STATUS — HTTP 429 HARD STOP (no gate verdict exists yet)

**IOI-1 and IOI-2 are NOT SCORED.** The dataset build was halted by
an **HTTP 429 from api.upstox.com** and, per the standing rule
(429 = hard-stop that provider scope, no retry, no route-switch),
this run did not resume it. Scoring the frozen gate on a partial
window would break the freeze, so no totals, placebos or verdicts
exist. What follows is the exact checkpoint state.

- **Fetch plan:** 1,100 contracts / 1,204 chunks (≤30-day windows
  per contract, all seven candle fields preserved in
  `round5_ioi_data/chunks/`).
- **Halt point:** chunk 713 of 1,204 (712 cached, 59.1%), inside
  the 2026-07-28 expiry's contracts, ~10 minutes into the fetch
  (progress file: `rate_limited: true`; 0 chunks had failed before
  the stop). Build log: `round5_ioi_build.log`.
- **Coverage already secured (read back from cache, local files
  only):** expiries 2026-01-27, 2026-02-24, 2026-03-30, 2026-04-28,
  2026-05-26 and 2026-06-30 are fully fetched →
  **104 of 205 Jan–Oct days are band-complete** (Jan 19, Feb 18,
  Mar 17, Apr 16, May 15, Jun 19). **16 Jan–Jun days are genuinely
  band-incomplete in the source data** (a band contract lacks its
  09:15 or 10:55 bar — the audit's known fixed-strike gap pattern;
  Jan 1, Feb 3, Mar 2, Apr 4, May 4, Jun 2 days). They will stand
  as NC_BAND in the final dataset regardless of the resume.
- **Not yet fetched:** the remaining 2026-07-28 contracts and all
  of expiries 2026-08-25, 2026-09-29, 2026-10-27, 2026-11-23 —
  i.e. Jul–Oct days and the whole November counterfactual set.
- **Scorer readiness (smoke-tested on cached data):**
  `round5_ioi_score.py`'s exit replay is byte-identical to the
  frozen `replay_g0` at the 09:20 anchor on a real series
  (2026-01-16, 60100 CE: entry 371.20 → target 461.20, +₹2,480.00,
  both implementations), and its 11:00 / 12:00 anchors execute
  correctly. The scorer is ready to run the moment the dataset
  exists.
- **Resume path (one command, when authorised):**
  `python3 round5_ioi_build.py` — skips all 712 cached chunks,
  fetches the remaining 492, writes `round5_ioi_dataset.csv` —
  then `python3 round5_ioi_score.py` runs the full Part 7 gate,
  the merge test and the November counterfactual, writing
  `round5_ioi_trades.csv` and `round5_ioi_gate_results.json`.
  Neither output file exists yet; nothing has been scored,
  armed or modified.

---

---

## 3. PARTIAL-WINDOW READ — 2026-11-14 (later the same day)

**PARTIAL WINDOW — JAN–JUN, 104 DAYS — NOT THE GATE.** After the
§2 halt, the families were scored on exactly what the local cache
supports, by `round5_ioi_partial_score.py` — a local-only driver
(no network imports at all; **zero api.upstox.com calls**; any
datum not in the cached chunk store is NC, never fetched). The
frozen logic was reused unchanged (band/quadrant aggregation,
direction rules, 11:00-open entry, −50/+90 exits, ₹220/trade,
1 lot of 30, buying only); before scoring, each fired day's
traded ATM contract was verified present in the cache with
full-day coverage including the 15:10 bar. Outputs:
`round5_ioi_partial_results.json`, `round5_ioi_partial_trades.csv`.

Window reproduction, exact against §2: 120 Jan–Jun trading days →
**104 band-complete** (Jan 19, Feb 18, Mar 17, Apr 16, May 15,
Jun 19) + **16 NC_BAND** (Jan 1, Feb 3, Mar 2, Apr 4, May 4,
Jun 2), 0 NC_NO_SPOT. Hygiene: replay equivalence vs the frozen
`replay_g0` OK at the 09:20 anchor; **timing violations 0**;
**scoring-NC 0** for both families; independent re-sum of the
trades file **EXACT for both families**.

### 3.1 IOI-1 — PARTIAL WINDOW — JAN–JUN, 104 DAYS — NOT THE GATE

- Fired 85 days · **85 legs** · **total −₹27,178.00** ·
  **−₹319.74 per fired trade-day** · win rate **34.12%**
  (29 wins / 56 losses; 27 full targets).
- Months: Jan **+₹10,469.00** · Feb −₹1,647.00 · Mar −₹9,000.00 ·
  Apr −₹4,800.00 · May −₹15,680.00 · Jun −₹6,520.00.
- Halves (median split at the 53rd complete day, 2026-03-27):
  first **−₹178.00** (40 legs) / second **−₹27,000.00** (45 legs).
  Calendar quarters are identical: **Q1 (Jan–Mar) −₹178.00 /
  Q2 (Apr–Jun) −₹27,000.00**.
- Ex-top-3: **−₹34,618.00** (top-3 = three +₹2,480.00 target hits).
- Days (of the 104): **29 green / 56 red / 19 no-trade**
  (of all 120 Jan–Jun days: 29 / 56 / 35).

### 3.2 IOI-2 — PARTIAL WINDOW — JAN–JUN, 104 DAYS — NOT THE GATE

- Fired 8 days · **8 legs** · **total +₹2,020.00** ·
  **+₹252.50 per fired trade-day** · win rate **50.00%**
  (4 wins / 4 losses; 3 full targets).
- Months: Jan −₹5,160.00 · Feb **+₹4,700.00** · Jun **+₹2,480.00**
  (no legs in Mar, Apr or May).
- Halves (split 2026-03-27): first **−₹460.00** (7 legs) / second
  **+₹2,480.00** (1 leg). Calendar quarters identical:
  **Q1 −₹460.00 / Q2 +₹2,480.00**.
- Ex-top-3: **−₹5,420.00** — the positive total is carried by its
  three +₹2,480.00 target hits.
- Days (of the 104): **4 green / 4 red / 96 no-trade**
  (of all 120: 4 / 4 / 112).

### 3.3 Merge reads vs TUNED STACK v2, same 104 days — PARTIAL WINDOW — NOT THE GATE

Stack reference on the same 104 days (from the stored stack
ledger; full-ledger anchor re-verified in this run: 111 legs /
+₹127,351.50 / 89 trade-days): **51 legs, +₹73,500.00, 39
trade-days, ₹1,884.62/trade-day**.

- **IOI-1 merge read:** increment = 55 legs on stack-idle days,
  **−₹34,378.00** → merged **₹39,122.00** on 94 trade-days
  (₹416.19/trade-day). Merged months: Jan +₹19,097.00 ·
  Feb +₹7,275.00 · Mar −₹3,480.00 · Apr +₹5,410.00 ·
  May +₹12,380.00 · Jun −₹1,560.00 (2 red). Merged days:
  46 green / 48 red / 10 no-trade. The increment is negative and
  the merged total is below the stack's window total — on this
  partial window the merge read meets neither registered merge
  condition.
- **IOI-2 merge read:** increment = 4 legs on stack-idle days,
  **+₹1,520.00** → merged **₹75,020.00** on 43 trade-days
  (₹1,744.65/trade-day — the total rises; the per-trade-day rate
  is diluted vs the stack's ₹1,884.62 window rate). Merged
  months all positive: Jan +₹10,908.00 · Feb +₹23,802.00 ·
  Mar +₹6,080.00 · Apr +₹12,490.00 · May +₹21,180.00 ·
  Jun +₹560.00. Merged days: 33 green / 10 red / 61 no-trade.
  Both registered merge conditions (increment > 0; merged >
  stack alone) are met **on this partial window only** — IOI-2's
  standalone ex-top-3 is negative and its sample is 8 legs, so
  this is a partial-window observation, **not a pass**, and it
  promotes nothing.

### 3.4 What this read says, and what it does not

On Jan–Jun evidence, IOI-1 decays across the window (Q1 ≈ scratch
at −₹178.00, Q2 −₹27,000.00) and its days run red 56-to-29 — it is
not carrying the family on the partial window. IOI-2 is the only
positive fragment (standalone total and merge increment both
positive) but rests on 8 legs and three target hits, with a
negative ex-top-3.

**NOT COMPUTED here (unchanged from §2): the Jan–Oct gate
verdict, every gate leg and placebo, all Jul–Oct figures, and
the November counterfactual. The gate verdict awaits the
Jul–Oct fetch** (resume path in §2, when authorised). Nothing
was armed, merged or modified by this read.
