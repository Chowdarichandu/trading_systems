# NEW-DATA INVENTION — ROUND 5 (WEEKEND, 2026-11-14 → 11-15)

**Owner order 2026-11-14 05:24 IST: November work TODAY AND TOMORROW —
no drifting to December.** Objective: a genuinely new INTRADAY data
signal, gated on Jan–Oct NOW and checked against November — without
waiting for the option-chain archive's ~Dec-10 gate. Rounds 1–4 are
closed; D1/T1 (round 4) are NOT retested; the Part 7 IOI freeze is
not edited (if intraday OI proves to exist historically, it is gated
under its own spec, adapted only in data source). **Paper only, real
money ₹0 — no live trades were placed.** Index figures are option
premiums per 1 lot (Bank lot 30), cost ₹220/trade, UNIQUE-ONCE.
Incumbent for every merge: **TUNED STACK v2** — 111 legs,
**+₹127,351.50** Jan–Oct, 89 trade-days, **₹1,430.92/trade-day**.
Futures/spot/option-flow are signal data only — the traded
instrument is always Bank Nifty options, 1 lot, buying only. No
running book, job, or ledger is touched by this round. (One
infrastructure action, recorded here: the Upstox token expired Sat
~03:30 IST — the refresh job is Mon–Fri 03:45 — so the owner's own
existing `upstox-auto-token-refresh` job was triggered once,
off-schedule, to restore the data feed. Its definition was not
modified; no book or ledger was touched.)

**OWNER SIMPLIFICATION LENS (added 2026-11-14 05:25 IST, applies to
Phases 2–3; no frozen rule or gate changes):** the owner's ask —
*"November till now is red — at least more than half days green is
what I asked, simply."* Every gated family and every merged book
additionally reports **green / red / no-trade DAY counts**: (a)
Jan–Oct, on trade-days and on all trading days; (b) the November
counterfactual, day by day. Among candidates that pass the full
gate, selection ranks by Jan–Oct green-day rate — frequent small
green days are the ask; a rare-but-big winner profile is not.
**November baseline, stated up front: the stack's November so far
= 1 green / 3 red / 5 no-trade days across Nov 2–13, MTD −₹2,680.**
November still sets NO rule — counterfactual check only.

---

## PHASE 0 — DATA AUDIT (written FIRST, before any family is frozen or scored)

The prior rounds used futures BASIS (price) and DAY-level OI. They
never used intraday traded VOLUME or per-contract intraday OI.
Round 4's stored futures series was checked first, then the raw
routes themselves.

**(c) What is already on disk.**
- Round 4's stored FUT5 series (`round4_history/FUT5_*.json`):
  **[date, time, O, H, L, C] — 6 fields. NO volume, NO OI.** The
  API returned more; the builder dropped fields 5–6 at storage.
  The stored series cannot serve any flow family — futures flow
  data must be re-fetched if wanted.
- Round 2's daily futures files (`round2_history/FUT_*.json`):
  [date, O, H, L, C, **volume**] — daily volume kept, daily OI
  dropped; daily granularity only.
- Round 1's premium fetch cache (`oi_buildup_data/candles_*.json`,
  1,204 raw API response files, 638 of them BANKNIFTY): the RAW
  responses were stored whole — see (b).

**(b) Expired near-ATM OPTION contract 5-min candles — INTRADAY OI
EXISTS HISTORICALLY. This is the audit's headline.**
Evidence: the 638 BANKNIFTY raw cached responses in
`oi_buildup_data/` — every one fetched 2026-11-13 through the same
expired-instruments 5-minute route this round would use
(`/v2/expired-instruments/historical-candle/{key}/5minute/{day}/{day}`),
spanning 200 distinct Jan–Oct trading days plus November to Nov 12:
- **Every candle in every file is 7 fields wide**:
  [timestamp, O, H, L, C, **volume**, **OI**].
- **Volume**: ≥ 90% of bars nonzero in **638/638** files.
- **OI varies intraday in 638/638 files** — and varies *within the
  morning window* (bars ≤ 10:55) in **638/638**. OI is constant
  across a day in **zero** files. Morning ΔOI (09:15 bar → 10:55
  bar) is nonzero in 40/40 randomly sampled files.
- **It is a genuine intraday series, not the daily figure stamped
  on bars:** a stamped series would be constant (it is not) and its
  last bar would equal the daily-candle OI exactly. Sampled
  last-bar (15:25) OI vs the same contract-day's daily-candle OI
  (the series round 1 cross-validated to the contract against the
  live chain archive): differences of 0.06%–2.5%, last bar always
  slightly ABOVE the daily print — the signature of an as-of-bar
  intraday series vs an end-of-day settled print, not of a copy.
- **Consequence, per the round's mandate: the Dec-10 wait is
  broken.** The frozen intraday-OI family (OI programme Part 7:
  IOI-1 + IOI-2) is gated NOW on Jan–Oct, under its own spec,
  adapted ONLY in data source: archive chain snapshots → the
  per-contract 5-minute candles of this route (baseline = the
  09:15 bar, read = the 10:55 bar — the same two moments Part 7's
  baseline/read buckets target; band = the 11 strikes nearest the
  10:55 spot close, per Part 7). No rule, threshold, quadrant
  definition, or gate leg of Part 7 changes. Where Part 7's gate
  was written for a forward window (halves split at the window's
  median day; "no scoring before ≥ 20 archive days"), the Jan–Oct
  substitution is the rounds 1–4 standard (halves = Jan–May /
  Jun–Oct) and the coverage leg is satisfied 10× over (205 days) —
  both substitutions are data-source/window adaptations, recorded
  here, not rule changes.

**(a) Near-month FUTURES 5-min candles — fields on the raw route.**
The direct API probe of the futures route was attempted first this
morning and returned HTTP 401 (UDAPI100050): the access token had
expired at ~03:30 IST today (the refresh job runs Mon–Fri 03:45;
the log's last refresh is Fri 2026-11-13 03:42 IST, expiry
2026-11-13T22:00Z). The owner's refresh job was triggered (see the
header note); the futures field audit is completed from the raw
route as soon as the token lands, and its result is appended here
before any futures-dependent step. What is already established
without the probe: the route family is the same v2
expired-instruments historical-candle route whose options leg
provably returns 7-field candles, and round 2's daily futures
fetch through the sibling daily route carried a real volume
field. **No futures-dependent family is frozen until this probe
completes.** (FLOW-VOL is in any case not in this round's family
budget — see Phase 2.)

**Phase-0 verdict:** intraday traded VOLUME and per-contract
intraday OI **exist historically** for Bank Nifty options across
Jan–Oct 2026. The round proceeds on (i) the frozen Part 7 IOI
design scored on historical intraday OI (OI-INTRA) and (ii) an
option traded-volume imbalance family (OPT-FLOW) — at most two
families total, per the mandate. Futures volume thrust (FLOW-VOL)
is not run: the family budget is two, and its agreement half
belongs to the basis surface closed in rounds 2 and 4.

**Phase-0 appendix — direct API probe, completed 2026-11-14 ~05:35
IST (after the token refresh above landed; probe script
`round5_probe.py`, results `round5_history/probe_audit.json`):**
- **Futures (a): CONFIRMED on the raw route.** One mid-month day
  per month, Jan–Oct, in-force contract, expired route: 75–77
  candles/day, **all 7 fields wide**; **volume nonzero on every
  bar** (75/75, 77/77); **OI varies intraday on every sampled day**
  (69–74 distinct values/day; 19–21 distinct within the morning
  alone; e.g. 2026-01-16 OI 09:15 bar 1,218,660 → 10:55 bar
  1,301,310). Futures intraday volume AND intraday OI both exist
  historically.
- **Options (b): re-confirmed on contracts round 1 never cached**
  (far strikes, +700 from ATM, 2026-03-16 and 2026-07-16, CE+PE):
  75 candles, 7 fields, volume nonzero on every bar, OI 66–71
  distinct values/day. The cached-file evidence generalises.
- One quirk of the route, recorded so no later step trips on it:
  the API returns candles in DESCENDING time order; every consumer
  in this round sorts ascending before use (the frozen scorers
  already do).

---

## PHASE 1 — NOVEMBER FORENSIC MAP (descriptive only)

## Phase 1 — November forensic map (descriptive only; no rule derived)

Futures surface (complete — from the FUT7 refetch, which finished
before the provider stop below): morning = bars 09:15–10:55.
"Thrust" = morning futures volume ÷ prior morning's (the frozen
FLOW-VOL trigger, shown here descriptively); Δbasis = the frozen
direction input. Options band surface: **NC on all 9 days** — the
November band contracts sit in the unfetched remainder (see Phase
2), so per-side ΔOI / quadrants / volume share for November are
PENDING-FETCH, not estimated.

| Day | Stack | Fut morn vol | Thrust | Δbasis | Fut ΔOI | FLOW-VOL would-be |
|---|---|---|---|---|---|---|
| Nov 02 | no-trade | 191,670 | 0.98 | −3.60 | −5,310 | — |
| Nov 03 | no-trade | 464,370 | **2.42** | +5.80 | −28,650 | **CE** |
| Nov 04 | PE +₹2,480 | 331,770 | 0.71 | +10.35 | +51,480 | — |
| Nov 05 | no-trade | 648,840 | **1.96** | +35.90 | +103,170 | **CE** |
| Nov 06 | no-trade | 408,030 | 0.63 | −22.90 | +33,180 | — |
| Nov 09 | PE −₹1,720 | 367,020 | 0.90 | +90.20 | −7,950 | — |
| Nov 11 | no-trade | 536,610 | **1.46** | +104.20 | +31,710 | **CE** |
| Nov 12 | PE −₹1,720 | 318,210 | 0.59 | −6.45 | +71,880 | — |
| Nov 13 | PE −₹1,720 | 314,760 | 0.99 | +18.80 | −52,740 | — |

**One-line conclusion:** on the futures surface the information
existed before the fact — a volume surge with expanding basis fired
on three stack-idle days (Nov 3, 5, 11, all CE) and on none of the
three loss days — but whether those signals would have made money
is a premium question this map does not answer and November cannot
be used to decide; the legs are PENDING-FETCH. Book-level November
forensics and green-day counts are Track B's file
(`round5_forensic_greenday_2026-11-14.md`), cited in Phase 3.
(To be filled: Nov 2–13 morning values of the audited series
beside the stack's day. No rule may be derived from this map;
families are frozen from Jan–Oct logic in Phase 2 and November is
only a counterfactual check.)

---

## PHASE 2 — FROZEN FAMILIES + GATE (Jan–Oct)

## Phase 2 — the freeze (written BEFORE any scoring, 2026-11-14)

Two families, both Bank Nifty, both built only from the audited new
surfaces, both on the house construction: **entry at the OPEN of the
11:00 bar of the ATM contract (nearest 100 to the spot close of the
10:55 bar) on the signal side; exit the first bar, entry bar included,
whose low ≤ entry−50 → stop at entry−50; else the first bar whose
high ≥ entry+90 → target at entry+90 (stop checked first inside a
bar); else the close of the 15:10 bar; 1 lot = 30 units; ₹220/trade;
UNIQUE-ONCE (at most one leg per day by construction); option BUYING
only.** A day is NC if any band contract lacks a 09:15 or 10:55 bar
or has a null OI/close there, or the traded contract lacks an 11:00
bar, a 15:10 bar, or ≥60 bars inside 11:00–15:10. NC days are
counted, never silently dropped.

### Scope change (coordination steer, 2026-11-14 05:37 IST)

Track A's audit landed (`round5_data_audit_2026-11-14.md` — cited
for all field facts; its verdict matches Phase 0 above: per-contract
intraday OI and volume exist on every 5-minute candle, futures
205/205 and options sampled 22/22). A dedicated track now gates the
frozen Part 7 IOI-1/IOI-2 families on Jan–Oct, so **this round does
not score IOI** (the freeze originally written here under the first
mandate is superseded by that steer and preserved in git-less form
as this note — the Part 7 spec itself lives untouched in
`oi_buildup_programme_2026-11-13.md`). This round's two families
are FLOW-VOL and OPT-FLOW. The band candle build already running
when the steer landed is retained because OPT-FLOW's volumes live
in the same candle rows; its OI columns are not scored here.

### Family 1 — FLOW-VOL (new: futures traded-volume thrust)

The one audited surface no round has used as a trigger: futures
traded volume. Round 4's stored futures series dropped the volume
column, so the futures contracts were refetched with all 7 fields
(`round5_history/FUT7_*.json`, 11 contracts, 28–32 days each).
- V_morn(d) = Σ volume of the in-force futures bars 09:15–10:55 on
  day d. All 21 bars must be present with non-null volume, else the
  day is NC.
- p(d) = the previous trading day (for 2026-01-02, 2025-12-31,
  present in the fetched series). V_morn(p(d)) must be > 0, else NC.
- **THRUST fires iff V_morn(d) / V_morn(p(d)) ≥ 1.25** (morning
  futures volume at least 25% above the prior morning — a round
  a-priori surge line, not scanned).
- BASIS(t) = futures close at bar t − spot close at bar t for
  t ∈ {09:15, 10:55} (spot from the stored series; both bars
  required, else NC). ΔBASIS = BASIS(10:55) − BASIS(09:15).
- **Direction: ΔBASIS > 0 → buy CE; ΔBASIS < 0 → buy PE; ΔBASIS = 0
  → no trade. Signal = THRUST fires AND ΔBASIS ≠ 0.** Trade the ATM
  contract of that side on the house construction above.
- Distinctness, stated plainly: rounds 2 (A1) and 4 (T1) used basis
  direction with NO volume condition anywhere (T1 fired on 120 of
  205 days and lost ₹37,648.50). FLOW-VOL's trigger is the volume
  surge; basis only picks the side on thrust days. If the surge
  subset is what carries the edge, this passes where T1 failed; if
  not, it fails on its own numbers and is not retested.

### Family 2 — OPT-FLOW (new: traded-volume imbalance)

Same band, same window. VOL_S = Σ over band strikes of the summed
bar volumes 09:15–10:55 for side S. share_CE = VOL_CE/(VOL_CE+VOL_PE).
**Buy CE iff share_CE ≥ 0.60 AND ΔP_CE > 0; buy PE iff share_CE ≤
0.40 AND ΔP_PE > 0.** The 0.60/0.40 line is a 3:2 flow majority,
chosen a priori as a round number (not scanned); the premium
confirmation is Part 7's own per-side premium index rising over the
same morning — flow and price must agree.

### The gate (identical for both families, all legs in the same run)

1. Total > 0 AND ≥ ₹900 per trade-day (the owner's operative test).
2. ≥40 trades AND ≥20 trade-days. NC ≤ 5% of the 205 days.
3. Both halves positive — adapted split: H1 = Jan–May, H2 = Jun–Oct
   (Part 7's forward-median split substituted by the calendar split
   on this historical window; recorded here, not hidden).
4. Every month ≥ −₹5,000.
5. Ex-top-3 > 0.
6. Beats ALL placebos at the 95th percentile (200 draws, seed
   20261113): COIN (random side per signal day), REVERSED (opposite
   side, same days), TIME-SHIFTED (same days/sides/contracts, entry
   at the 12:00 bar open instead of 11:00).
7. Timing audit: every signal input is a bar closing ≤10:55; entry
   is the 11:00 bar's open; asserted per trade in the scorer.
8. Independent re-sum of every total from the trades CSV.

**PASS = every leg above.** Anything else is a FAIL with the killing
legs named; a failing family may still contribute merge-only
evidence in Phase 3, labelled as such.

### The owner's lens (steer 2026-11-14 05:25), reported for every family and merged book

Green / red / no-trade DAY counts: (a) Jan–Oct, on trade-days and on
all 205 trading days; (b) November counterfactual, day by day,
against the stack baseline **1 green / 3 red / 5 no-trade, MTD
−₹2,680**. Among full-gate passes, rank by Jan–Oct green-day rate —
frequent small green days are the ask. November sets no rule.
## Phase 2 — gate status: NOT COMPLETED (provider stop, 2026-11-14 ~05:54 IST)

**An Upstox HTTP 429 stopped the band build at 713 of 1,100
contracts after 1,182 calls** (manifest:
`round5_history/build_manifest.json`, `stopped_on_429: true`; the
same provider limit stopped the parallel IOI build in the same
window). Per the standing rule the stop was hard: no retry, no
route-switch, and **no api.upstox.com call of any kind has been made
since** — everything below is stored data only. The futures refetch
(FUT7, 11 contracts) had completed minutes earlier and is complete.

Coverage assembled cache-only (`round5_assemble.py` →
`round5_history/morning_flow.csv`, 214 rows): complete band mornings
Jan 19/20 · Feb 18/21 · Mar 17/19 · Apr 16/20 · May 15/19 · Jun
19/21 · **Jul–Oct 0 · Nov 0 → 104/205 Jan–Oct days (50.7%)**. (The
Jan–Jun shortfall is genuinely partial contract-days — illiquid
band-edge strikes with no 09:15 print — the frozen NC kind, not
fetch gaps.) A gate run on a half-window with the entire second
half missing would break the freeze, so **no gate leg was run for
either family: FLOW-VOL and OPT-FLOW are neither passed nor failed.**

What the stored data does establish (signal censuses — descriptive,
no legs, no P&L; `round5_census.py`, `round5_history/round5_census.json`):
- **FLOW-VOL signals are computable for all 205 days** (futures +
  spot complete): **62 signal days** — every month fires (Jan 6,
  Feb 8, Mar 6, Apr 3, May 4, Jun 6, Jul 9, Aug 7, Sep 8, Oct 5),
  CE 33 / PE 29; **40 of the 62 fall on stack-idle days**, so the
  family is frequent enough to matter as an increment if its legs
  ever pass. November signals: CE on Nov 3, 5, 11 (Phase 1 table).
- **OPT-FLOW census on the 104 complete days only: 24 signals**
  (CE 10 / PE 14) — a ~23% signal rate on covered days, stated with
  its coverage limit attached.

**PENDING-FETCH (exact resume path, in order):** (1) re-run
`round5_data_build.py` in a fresh fetch window — it skips the 713
`.done` contracts and fetches only the remaining 387 (Jul-expiry
remainder + the Aug/Sep/Oct/Nov expiries); (2) re-run
`round5_assemble.py`; (3) run `round5_score.py` exactly as frozen
(both families' full gates, merges, November counterfactuals).
Nothing in the freeze changes on resume.

---

## PHASE 3 — MERGE + NOVEMBER COUNTERFACTUAL

## Phase 3 — merge + November

**This round's families:** merge and November counterfactuals are
**not runnable** — both need the premium legs, which are
PENDING-FETCH (Phase 2). FLOW-VOL's November signals (CE on the
stack-idle days Nov 3, 5, 11) are recorded in Phase 1; no merged
November arithmetic is possible or claimed without the legs.

**The merged-book results of this round come from the parallel
tracks, cited not recomputed:**
- *Track B* (`round5_forensic_greenday_2026-11-14.md`, all unions
  independently re-summed to the paisa): the stack alone runs
  **60 green / 29 red / 116 no-trade** Jan–Oct (67.4% of its
  trade-days green). Merged with the older fragments: +OI-V3 →
  78 G / 53 R / 74 NT and the best November line (2 G / 3 R / 4 NT,
  −₹200 vs the stack's 1/3/5, −₹2,680); +VIX-B1 → 66 G / 35 R
  (65.3% of trade-days, the highest merged share); +R4-D1 →
  73 G / 43 R (62.9%). No configuration is green on more than half
  of ALL 205 days — no-trade days dominate every line.
- *Track C* (`round5_greenday_book_2026-11-14.md`): **Book P**
  (stack + priority increment D1>V3>B1, ≤1/day) totals
  +₹140,844.50 and improves November to 2 G / 3 R / 4 NT (−₹200),
  but its green share of trade-days FALLS to 58.7% (stack: 67.4%)
  and July goes red (−₹176) → **NOT a candidate**. **Book D**
  (stack + D1 only) totals +₹136,324.50 with zero red months, but
  its green share also falls (62.9%) and its November is unchanged
  → **NOT a candidate**. The stack alone remains the book; all
  three fragments stay unpromoted merge-only evidence.

---

## VERDICT

## Verdict

1. **Phase 0 (the question that decided the round): per-contract
   intraday OI EXISTS historically** — every 5-minute candle on the
   expired-instruments route carries volume (field 6) and OI
   (field 7), OI varying bar-by-bar inside the morning itself,
   proven three independent ways (638 stored raw responses audited
   on disk, fresh direct probes after the token refresh, and Track
   A's independent audit, `round5_data_audit_2026-11-14.md`). The
   Dec-10 archive wait is broken; the frozen Part 7 IOI design is
   gateable on Jan–Oct data — that gating belongs to the dedicated
   IOI track (its build hit the same provider stop; its verdict is
   theirs to report).
2. **Two new families were frozen in writing before any scoring** —
   FLOW-VOL (futures volume thrust ≥1.25× prior morning + basis
   direction; the first volume-triggered design in five rounds) and
   OPT-FLOW (band traded-volume imbalance ≥60/40 + premium
   confirmation; no OI anywhere in it).
3. **Neither family is passed or failed: their gates were not run.**
   An Upstox HTTP 429 stopped the options data build at 713/1,100
   contracts (~05:54 IST, hard stop honoured, zero calls since),
   leaving 104/205 scoreable days with Jul–Oct and November entirely
   unfetched. Running a "gate" on that window would have broken the
   freeze; the censuses (FLOW-VOL 62 signal days, 40 on stack-idle
   days; OPT-FLOW 24 signals on covered days) are all the numbers
   this run honestly produces.
4. **November forensic (futures surface):** thrust + expanding
   basis fired CE on the stack-idle days Nov 3, 5, 11 and on no loss
   day — the information existed; the money question stays open
   until the legs are fetched. The round's actual merged-book
   answers are Track C's: neither green-day book is a candidate,
   and the stack alone remains the book.
5. **Resume is mechanical and pre-built:** fresh fetch window →
   `round5_data_build.py` (387 contracts remain) →
   `round5_assemble.py` → `round5_score.py` under the unchanged
   freeze. Nothing was armed, modified, or touched in any running
   book, job, or ledger at any point in this round.
