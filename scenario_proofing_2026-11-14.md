# SCENARIO-PROOFING — 2026-11-14

**Owner order (2026-11-14 07:20 IST, free hands): fix the
November-regime exposure TODAY, so the scenario cannot burn real
money when it recurs in live trading. This is that run's finished
report — all five items, pass or fail.**

**Real money: ₹0. No live trades were placed; nothing was armed
into, merged into, or modified in any running book or ledger.**
Every figure is paper/backtest on option premiums **per 1 lot**
(Bank Nifty lot 30, Nifty lot 65), cost **₹220/trade** inside every
net, option BUYING only. Indices are reported separately, never
pooled. Incumbents: Bank **TUNED STACK v2** (111 legs,
+₹127,351.50, Jan–Oct) and Nifty **TUNED v1** (74 legs,
+₹103,050.25, Jan–Oct). November baseline (Nov 2–13): stack
−₹2,680, 1 green / 3 red / 5 no-trade.

---

## ITEM 1 — NIFTY REGIME-REV: DATA RESCUE + GATE — **GATE RUNS COMPLETE; VERDICT: FAIL**

### The rescue

The frozen gate could score only 3 of 38 fired Nifty regime days:
33 were NC `series_starts_after_0920` and 2 `no_premium_store`
(P1: 73 and 6). The needed contract-days were computed from the
frozen signal logic: **165** (38 regime days × reversal + morning
sides, plus 89 non-regime P1 days). **86 were already complete**
in the shared fetched cache (`oi_buildup_data/`); the remaining
**79 were fetched** via the expired-instruments route
(sequential, gentle pacing, browser User-Agent on every call) —
**79/79 OK, 0 failed, no HTTP 429**. After the fetch, the real
book's NC count is **0 of 38**; P1 scores 89/89, P2 38/38, P3
36/38 (the only NCs left in the whole run are 2 P3
`no_delay_bar` — the delayed-entry bar does not exist before the
15:10 square-off on those days; a placebo-side mechanical NC,
not a data gap).

### One disclosed data-layer repair (no rule changed)

The frozen `prem_store` consults `daily2leg/prem_nifty_weekly.json`
*before* the fetched-candle folders. That store was built by
`daily2leg/fetch_weekly.py` on a **10:00–15:15 grid** (its book
entered at 10:00 — see Item 2), so every series in it starts at
10:00 and the frozen completeness rule (series must start
≤ 09:20) NC'd the day even where the complete series already sat
in the fetched cache — the truncated store shadowed the complete
one. The gate runner (`scenario1_gate.py`) therefore prefers,
among the *same* sources, a series that starts ≤ 09:20 — the
completeness property the frozen rule itself tests. Signal,
geometry, strikes, exits, gate legs: byte-identical to
`november_regime_family.py`. Sanity check: the identical engine
under the *untouched* store order reproduces the frozen NC
structure exactly (33 real `series_starts_after_0920`) and the
original gate's 3 legs (+₹6,480.25) as an exact subset — its 2
extra legs are the formerly `no_premium_store` days, which the
fetch landed in a folder the original order already reads.

### The gate (Nifty, Jan–Oct, lot 65)

**Real book: 38 legs · +₹16,792.40 · ₹441.91/trade-day · win rate
36.8% · 14 green / 24 red days.** Halves: Jan–May **+₹10,084.00**
· Jun–Oct **+₹6,708.40** (both positive). Months: Jan −₹2,628.25 ·
Feb −₹2,884.00 · Mar +₹12,816.00 · Apr +₹3,927.75 · May −₹1,147.50 ·
Jun +₹10,995.25 · Jul −₹8,606.50 · Aug +₹784.90 · Sep +₹3,534.75
(no October fires).

| Gate leg | Result |
|---|---|
| Total > 0 | ✅ +₹16,792.40 |
| Both halves > 0 | ✅ +₹10,084.00 / +₹6,708.40 |
| Ex-top-3 > 0 | ❌ **−₹97.60** |
| Beats P1 (non-regime placebo) on total | ❌ P1 = **+₹25,728.90** (89 legs) |
| Beats P1 on per-leg average | ✅ ₹441.91 vs ₹289.09 |
| Beats P2 (morning side) | ✅ P2 = −₹6,302.75 |
| Beats P3 (delay +30 min) | ✅ P3 = +₹2,567.75 |
| Scoring-NC ≤ 5% of fired days | ✅ 0/38 |
| Timing audit / re-sum | ✅ 0 violations by construction / EXACT |

**Verdict: FAIL — killed by ex-top-3 (−₹97.60, ninety-seven
rupees under the bar) and by the P1-total leg.** The second
failure is the informative one: on Nifty, the *same*
midpoint-reversal logic applied to **non-regime** days earns
+₹25,728.90 with a *positive* ex-top-3 (+₹8,838.90) — the regime
conditioning that carries the Bank book is not what carries
Nifty; if anything it filters out the better half of the signal.
The unfiltered union (127 legs, +₹42,521.30) was never frozen as
a book and is recorded here as an **observation only — not a
candidate, not gated, not promoted**. The frozen REGIME-REV spec
on Nifty is FAIL, and the family now stands: **Bank standalone
PASS (Item 5 shadow), Nifty FAIL**. Trades:
`scenario1_nifty_regimerev_trades.csv`; machine results:
`scenario1_gate_results.json`.

---

## ITEM 2 — NIFTY PERSISTENCE FIX — **DONE (spot already fixed & verified; premium fix implemented & verified)**

### Spot bars — root cause found, fix already in place, verified

Until 2026-11-13 the November EOD path fetched each day's spot
bars for scoring and **threw them away** — no persistence step
existed. The failure audit's fix 2 added `persist_spot_day` into
`day_context` in `november_shadow_score.py` (defined line 164;
called for **both** symbols on every scoring run, lines 237–238).
Verified in the store today: the progressive store holds
**2026-11-11, 11-12 and 11-13 at 75 bars each for BOTH symbols**
(store files written 2026-11-13 ~17:11 IST — Nov 13 persisted on
its own day). No further spot change was needed or made.
**Monday-only remainder:** confirmation that the regular 15:32
job performs this inside the normal chain on Mon 2026-11-16 —
the code path is proven and a live day has been persisted through
it, but the job's ordinary invocation is a live-run fact.

### Premium bars — root cause found (two layers), fix implemented

1. **The standing research stores never held the early bars.**
   `prem_nifty_weekly.json` — the store the gate reads first —
   was built by `daily2leg/fetch_weekly.py` with the filter
   `"10:00" <= t <= "15:15"` (its line 21): the daily2leg book
   entered at 10:00, so its fetcher discarded 09:15–09:55 by
   construction. `prem_nifty.json` (monthly) covers only the
   contracts the R-programmes happened to fetch.
2. **The November machinery's own fetches were written where
   nobody reads.** `november_shadow_fetch.fetch_premium` *did*
   cache every series it fetched — under a **day-before-expiry**
   filename in `november_shadow_data/`, a convention no shared
   consumer uses. Verified before the fix: Bank 60800 PE for
   2026-11-13 was sitting in that cache while
   `oi_buildup_score.store_bars` (the shared lookup) returned
   **None** for it.

**The fix (fetch layer only — no book logic, no ledger format,
no job timing changed):** `mirror_shared()` in
`november_shadow_fetch.py` — every series the fetcher holds is
also written, write-once, under the shared convention
(`oi_buildup_data/candles_<SYM>_<strike><TYP>_<exp>_<day>.json`),
on the CACHED, fresh-fetch and expired-route paths, plus a
one-time `--backfill-shared` mirror of the existing cache:
**23 mirrored, 4 already present, 0 unparsed (29 files)**.
After: `store_bars(BANKNIFTY, 2026-11-23, 60800, PE, 2026-11-13)`
= **76 bars, 09:15–15:30, source 'fetched'** (was None);
`store_bars(NIFTY, 2026-11-23, 23600, CE, 2026-11-03)` = 77 bars.
The edited CACHED branch was exercised post-edit: `('CACHED', 76)`.
**Monday-only remainder:** the first fresh-fetch mirror-write in
the live chain (same verified code path; it fires only when a
new contract is fetched).

---

## ITEM 3 — CIRCUIT-BREAKER VERIFICATION — **WAS NOT COMPUTED BY ANY CODE FOR THE STACK; NOW IMPLEMENTED; REPLAYS BELOW**

### Verification from the machinery

**No code computed the breaker for the current books.** A grep
of the trading tree finds breaker logic only in unrelated
daily2leg / combined-build research variants;
`november_shadow_score.py` and `bank_tuned_stack_live_score.py`
contain none, and there was no state file and no daily record.
The tracker's nightly "circuit breaker: no trigger" lines were
judgements written by the segment-engine agents each evening —
correct ones, as the replays below confirm, but nothing a
December live layer could bind to mechanically.

### Implementation (scoring layer; binds the shadow/December layer only)

`circuit_breaker.py` — one implementation of the owner's rule
(3 consecutive losing days → pause 3 trading days; MTD ≤ −₹5,000
→ pause rest of month), with the semantics fixed in writing:
a losing day is a day whose **realised** net < 0; a no-trade day
is not a losing day and **resets the streak**; the MTD leg is
checked first (it dominates) on the close of a non-paused day;
the streak leg pauses exactly the next 3 trading days and resets
the streak; on paused days the book does not trade (realised 0,
hypothetical recorded as suppressed). `circuit_breaker_stack.py`
recomputes the stack's record from its ledger on every run —
deterministic, idempotent — writing
`circuit_breaker_stack_log.csv` (one row per trading day) and
`breaker_state_stack.json`. A NOT_COMPUTED ledger day halts the
record at the previous day; the state never advances on an
unknown day.

**Semantics control:** the same code over the legacy line's
November PRIMARY sequence **fires at the Nov 4 close** — Nov 2/3/4
losing streak *and* MTD −₹5,160 — the known firing (recorded
2026-11-05, the first paused day). The rule's cost side, priced:
under the breaker the legacy line would have realised **−₹5,160**
instead of −₹1,920 — the rest-of-month pause suppresses Nov 9's
−₹1,720 loss but also the Nov 11/12 +₹2,480 wins (suppressed
hypothetical +₹3,240; breaker effect **−₹3,240** on that line).

### Replay — TUNED STACK v2, Jan–Oct

Exactly **one trip** in ten months: **STREAK at the 2026-07-06
close** (losing days Jul 2 −₹220.00, Jul 3 −₹2,477.00, Jul 6
−₹1,720.00; MTD at trip −₹1,937.00). Paused Jul 7/8/9; suppressed
hypothetical **−₹124.00** (Jul 7's −₹884.00 loss avoided, Jul 8's
+₹760.00 win forgone, Jul 9 no-trade). Ten-month effect:
**+₹124.00** (realised ₹127,475.50 vs ₹127,351.50). The MTD leg
never fired for the stack in Jan–Oct.

### Replay — TUNED STACK v2, November (the required dry verification)

**The stack never tripped.** Day by day: Nov 9 −₹1,720 (streak 1,
MTD +₹760) · Nov 11 no-trade (streak reset) · Nov 12 −₹1,720
(streak 1) · Nov 13 −₹1,720 (streak 2, **MTD −₹2,680**). Zero
trips, zero paused days — now produced by code and recorded
daily in `circuit_breaker_stack_log.csv`.

### Replay — Nifty TUNED v1, Jan–Oct (feeds Item 4)

**Two MTD trips**: 2026-02-06 (MTD −₹6,940.00) and 2026-05-11
(MTD −₹6,084.25); **28 paused days**; suppressed hypothetical
**+₹26,617.50** → breaker effect **−₹26,617.50** (realised
₹76,432.75 vs ₹103,050.25). On TUNED v1's own history the
breaker is expensive: it parks the book after breaches the book
historically recovered from inside the same month.

---

## ITEM 4 — WORST-WINDOW STRESS TEST — **THE BURN BOUNDS (AND THE BREAKER DOES NOT REDUCE THEM)**

Rolling 10-trading-day windows over the frozen Jan–Oct legs
(196 windows per book; day nets per 1 lot, costs inside).
Regime-concentrated = ≥ 5 regime-like days in the window under
the frozen Phase C classification (Bank 85 such windows, Nifty
86). Drawdown = worst peak-to-trough of the within-window
cumulative curve.

| Book | Worst window | Net | Max DD | Worst day | Regime days |
|---|---|---|---|---|---|
| **Bank STACK v2** | 2026-06-09 → 06-22 | **−₹6,880.00** | −₹6,880.00 | −₹3,440.00 | 4 |
| Bank, worst regime-concentrated | 2026-06-03 → 06-16 | −₹4,400.00 | −₹6,880.00 | −₹3,440.00 | 8 |
| **Nifty TUNED v1** | 2026-03-16 → 03-30 | **−₹13,670.00** | −₹13,670.00 | −₹3,470.00 | 8 |
| Nifty, worst regime-concentrated | 2026-03-16 → 03-30 (same) | **−₹13,670.00** | −₹13,670.00 | −₹3,470.00 | 8 |

(Nifty's worst-drawdown window, 2026-03-13 → 03-27, nets
−₹5,985.00 with the same −₹13,670.00 drawdown inside it.)

### With the Item 3 breaker applied — unchanged, and here is exactly why

Re-running the identical window machinery on the breaker-applied
series (legs on paused days suppressed by the Item 3 simulation)
gives **the same worst windows to the rupee**: Bank −₹6,880.00,
Nifty −₹13,670.00. The breaker never binds inside either bleed:

- **Bank, June:** the window's losses were absorbed by a
  profitable month-to-date — June's realised MTD **trough was
  +₹560.00** (the month ended +₹3,040.00) — and the losing streak
  peaked at **2** (Jun 9/10) before no-trade days reset it. The
  −₹6,880 window is invisible to both legs.
- **Nifty, March:** TUNED v1 entered Mar 16 with March MTD at
  **+₹12,453.50** (the month ended only −₹1,216.50), so the MTD
  leg never came within reach during the −₹13,670 slide, and the
  losing days were interleaved with no-trade days.

**The burn bound for the December ₹1,00,000 live decision, in
numbers: at 1 lot, the worst 10-trading-day patch in either
book's proven history is −₹6,880 (Bank) and −₹13,670 (Nifty) —
and the circuit breaker as specified does NOT reduce either
one.** Its legs are anchored to the calendar month (MTD from
the month's start) and to consecutive traded days (broken by
no-trade days), so a November-style bleed that starts from a
profitable month-to-date passes straight through it. That is
the scenario-proofing gap, stated plainly: the breaker bounds
bad month-*starts* (it would have capped the legacy line's
November at −₹5,160 and cost the stack nothing across Jan–Oct:
+₹124), but it is not a bound on a mid-month regime patch. Any
December decision that wants a hard cap on the patch itself
needs a different leg (e.g. a rolling-window drawdown floor) —
inventing one is a new freeze and a new gate, not part of this
run, and nothing here arms one.

---

## ITEM 5 — REGIME-REV BANK SHADOW, LIVE FROM MONDAY — **SET, DRY-RUN VERIFIED**

- **Scorer:** `regime_rev_shadow_score.py` — the frozen Phase D
  spec (standalone family; **no** stack-idle condition, exactly
  as gated), the gate's own spot/premium sourcing, exits
  identical to the gate's replay, timing asserted per trade. It
  refuses to score dates after **2026-11-30** — the review bound
  is the Nov 30 verdicts.
- **Ledger:** `november_shadow_regimerev_bank_log.csv` (created;
  first scored day Mon 2026-11-16).
- **Schedule:** cron `regime-rev-shadow-scorer-daily`,
  **Mon–Fri 18:35 IST**, first run **Mon 2026-11-16 18:35 IST**,
  reporting to the Bank + Nifty combined-view chat like the
  V3/D1 shadows.
- **Dry run (`--verify`, writes nothing) against November —
  reproduces the frozen gate's November legs to the paisa:**
  Nov 2 PE 54900 target **+₹2,480.00** · Nov 3 PE 55300
  square-off **−₹1,099.00** · Nov 5 CE 57100 target
  **+₹2,480.00** · Nov 11 PE 60700 stop **−₹1,720.00** — family
  November **+₹2,141.00**. Other days: Nov 4/6/9 NO_REGIME,
  Nov 12 NO_CONFIRMATION, Nov 13 NO_REGIME (no leg).
- **The Nov 13 label, recorded so nobody re-chases it:** the
  brief's "NC_NO_SPOT" tag is the *IOI dataset's*, produced from
  `round5_ioi_build`'s spot source (`oi_history/spot_nov_bars.json`),
  which holds **zero** Nov 13 bars. On the frozen gate's own spot
  source — the one this scorer copies exactly — Nov 13 is a
  complete day whose morning is simply not a regime morning
  (gap −0.354%, morning −0.366%), so it scores as a no-fire day.
  No number differs between the two labels.
- **One gate-chain quirk preserved, not corrected:** the gate's
  spot store holds no 2026-10-29/30 bars, so its Nov 2 gap is
  measured against the Oct 28 close (+1.05%, regime). The
  scorer's spot universe is exactly the gate's (progressive
  store + banknifty-2026-11 overlay + forward cache/fetch), so
  the shadow's chain matches the gate's chain day for day —
  forward gaps from Nov 16 are measured against each prior
  trading day as persisted by the Item 2-verified machinery.

---

## VERDICT SUMMARY

1. **Nifty REGIME-REV: GATE FAIL** (data rescue complete, 0 NC):
   +₹16,792.40 on 38 legs, both halves positive — killed by
   ex-top-3 (−₹97.60) and by its own non-regime placebo earning
   more (+₹25,728.90). The regime conditioning is not the edge
   on Nifty. Nothing promoted; the unfiltered union is an
   observation, not a book.
2. **Persistence: FIXED.** Spot persistence verified working
   (both symbols, Nov 11/12/13 in the store). Premium
   persistence implemented in the fetch layer (shared-convention
   mirror + backfill of 29 series) and verified before/after.
   Two narrow remainders are live-run facts for Monday, stated
   in Item 2.
3. **Circuit breaker: it existed only as nightly narrative;
   now it is code** (`circuit_breaker.py` +
   `circuit_breaker_stack.py`, daily record + state file),
   semantics proven against the legacy line's known Nov 4
   firing. Stack Jan–Oct: one streak trip (2026-07-06), effect
   +₹124. Stack November: never tripped (MTD −₹2,680). TUNED
   v1 Jan–Oct: two MTD trips, effect −₹26,617.50 — the rule is
   expensive on that book's history.
4. **Burn bounds for the December ₹1,00,000 decision:** worst
   10-trading-day windows at 1 lot — **Bank −₹6,880, Nifty
   −₹13,670** — and the breaker as specified **does not reduce
   either**, because both bleeds began from profitable
   month-to-date positions. That gap is now measured, not
   guessed.
5. **REGIME-REV Bank shadow: LIVE from Monday** (18:35 IST
   scorer, own ledger, review at the Nov 30 verdicts), dry-run
   verified to the paisa against the gate's November legs
   (+₹2,141.00).

---

## BREAKER GAP — ROLL10 LEG: FREEZE (written 2026-11-14 BEFORE any test of this leg ran)

**Owner order (2026-11-14, free hands): close the Item 4 gap
TODAY.** Item 4 measured that the owner's breaker bounds only
bad month-*starts*: the worst rolling 10-trading-day windows of
Jan–Oct (Bank stack −₹6,880, 2026-06-09→06-22; Nifty TUNED v1
−₹13,670, 2026-03-16→03-30) pass straight through both legs
because month-to-date was still positive when the bleed began.
This section freezes ONE additional leg and the criteria that
decide it — **before** the overlay test below was run. One shot,
pre-registered: if the criteria fail, the leg is rejected **as
specified** and the threshold/pause shape is NOT retuned in this
run; a differently-shaped leg would be a new proposal.

### The leg — ROLL10 (uniform for both books; no per-book tuning)

- **Trigger:** at the close of a non-paused trading day, sum the
  book's **realised** day-nets over the trailing **10 calendar
  trading days including today** (paused days contribute their
  realised ₹0; the window spans month boundaries — that is the
  point). If that sum is **≤ −₹5,000** (the same magnitude as the
  owner's MTD leg), the leg trips.
- **Action:** pause the next **3 trading days** (the same pause
  shape as the owner's streak leg); legs on paused days are
  suppressed (realised ₹0, hypothetical recorded as suppressed,
  exactly as the Item 3 semantics).
- **Arming:** the leg can first trip at the close of the 10th
  evaluated trading day of a series (the window is incomplete
  before that).
- **Resumption:** after the pause, evaluation resumes on the
  trailing window **as it stands** — no immunity period is
  frozen; if the trailing-10 realised sum is still ≤ −₹5,000 at
  the next evaluated close, the leg trips again (a fresh 3-day
  pause).

### Interaction with the existing two legs (all frozen)

- All three legs are evaluated at the close of each non-paused
  day, in dominance order: **MTD → ROLL10 → STREAK**; at most
  one trip is recorded per close.
- Pauses **do not stack and do not extend**: trips are evaluated
  only on non-paused days, so a running pause simply runs out;
  an MTD trip (rest-of-month) dominates any 3-day pause, exactly
  as it dominates the streak leg today.
- On a ROLL10 trip the **losing streak resets to 0** — the same
  reset the streak leg applies on its own trip (one 3-day pause
  shape, one reset convention). MTD is untouched by a ROLL10
  trip (it does not move on paused days and is not reset).
- Everything else is Item 3's semantics, unchanged: a losing
  day is a realised net < 0; a no-trade day resets the streak;
  the streak counts across month boundaries; MTD is per
  calendar month.

### Adoption criteria (frozen; ALL must hold for BOTH books)

- **(a) Burn bound:** the worst rolling 10-trading-day window
  of Jan–Oct on the combined-brake realised series (Item 4's
  window machinery, 196 windows) improves to **≥ −₹5,500 for
  Bank** and **≥ −₹7,000 for Nifty**. (Bounds are stated net of
  trip-day overshoot — the floor is a trigger, not a cap; the
  graded window is the realised series, computed honestly.)
- **(b) Cost:** Jan–Oct total with all three legs vs the book's
  standing total (stack **+₹127,351.50**; TUNED v1
  **+₹103,050.25**): the cost (standing − combined) is
  **≤ 10%** of the standing total (Bank ≤ ₹12,735.15; Nifty
  ≤ ₹10,305.03).
- **(c) Trip count:** total trips of the combined three-leg
  brake across Jan–Oct **≤ 6 per book** (per-leg breakdown
  reported alongside) — a brake that fires constantly is a
  strategy change, not a brake.

**ADOPT** into the written December-layer spec only if (a),
(b) and (c) all hold for both books; otherwise **REJECT** as
specified, report the numbers, and leave the Item 3 machinery
exactly as built.

---

## BREAKER GAP — ROLL10 LEG: TEST RESULT (2026-11-14) — **VERDICT: REJECTED**

**Controls first (asserted in-script before any three-leg run):**
with the leg off, the extended `circuit_breaker.simulate`
reproduces Item 3 **exactly** — stack Jan–Oct: one STREAK trip
(2026-07-06), realised +₹127,475.50, suppressed −₹124.00;
TUNED v1: two MTD trips (2026-02-06, 2026-05-11), realised
+₹76,432.75, 28 paused days; stack November: 0 trips, −₹2,680;
legacy November control fires at the Nov 4 close. The leg was
implemented in `circuit_breaker.py` itself (extend, don't fork)
as an optional parameter, **disabled by default**; test driver
`scenario_breaker_gap.py`; machine results
`scenario_breaker_gap_results.json`, merged into
`scenario_proofing_results.json` (key `breaker_gap_roll10_leg`).
Every total below was independently re-summed from the realised
day series by a second code path, and every worst window
recomputed by a brute-force slice-sum implementation — all
exact.

### Bank TUNED STACK v2

- **Trips (combined brake): 2.** ROLL10 at the **2026-06-22
  close** (trailing-10 realised sum −₹6,880.00; June MTD at the
  trip **+₹560.00** — the Item 4 gap, live) → paused
  Jun 23/24/25, suppressed hypothetical **+₹2,480.00** (the
  Jun 24 win). STREAK at 2026-07-06 — unchanged from Item 3 →
  paused Jul 7/8/9, suppressed −₹124.00.
- **Paused days: 6. Totals:** standing **+₹127,351.50** ·
  two-leg +₹127,475.50 · three-leg **+₹124,995.50**. ROLL10's
  marginal effect: **−₹2,480.00** — its only pause suppressed a
  win and avoided no loss.
- **Worst rolling-10 window: −₹6,880.00 (2026-06-09 → 06-22)
  under no brake, the two-leg brake AND the three-leg brake —
  unchanged.** (Worst regime-concentrated window likewise
  unchanged: −₹4,400.00, 2026-06-03 → 06-16.)
- **Why it cannot bind in time (measured day by day):** the
  stack entered the bleed with its trailing window at
  **+₹12,620** (Jun 8 — three +₹2,480 wins inside it, Jun 1–8).
  The bleed (−₹1,720 Jun 9 · −₹3,440 Jun 10 · −₹1,720 Jun 16,
  zero-net days between) dragged the trailing sum +10,900 →
  +7,460 → +2,280 → −200 → −4,400, and it crossed −₹5,000 only
  at the **Jun 22 close** — on a zero-net day, because the Jun 8
  win rolled off the window. The window that fires the leg is
  already fully banked by construction; no later window was
  worse, so there was nothing left for the pause to improve.
- **Criteria: (a) FAIL** — worst window −₹6,880.00 vs required
  ≥ −₹5,500. **(b) PASS** — cost ₹2,356.00 = 1.85% ≤ ₹12,735.15.
  **(c) PASS** — 2 trips ≤ 6.

### Nifty TUNED v1

- **Trips (combined brake): 4.** MTD 2026-02-06 → paused
  Feb 9–27 (15 days), suppressed +₹16,169.25; MTD 2026-05-11 →
  paused May 12–29 (13 days), suppressed +₹10,448.25 — both
  unchanged from Item 3. **ROLL10 2026-03-27** (trailing-10
  −₹5,985.00; March MTD at the trip −₹1,216.50 — the MTD leg
  never came into reach in March) → paused Mar 30 / Apr 1 / 2,
  suppressed **+₹11,155.00** (the Apr 2 win). **ROLL10 again
  2026-04-06** (trailing-10 −₹10,200.00 — worse on paper
  because the masking Mar 13 win had rolled off the window, not
  because of new losses; Apr 6 itself was a zero-net day) →
  paused Apr 7/8/9, suppressed **+₹5,584.50** (the Apr 7 win).
- **Paused days: 34** (28 MTD + 6 ROLL10). **Totals:** standing
  **+₹103,050.25** · two-leg +₹76,432.75 · three-leg
  **+₹59,693.25**. ROLL10's marginal effect: **−₹16,739.50** —
  both of its pauses landed after the bleed, on the recovery.
- **Worst rolling-10 window: −₹13,670.00 (2026-03-16 → 03-30)
  under all three series — unchanged.** Why, in two parts:
  (i) the slide's losses (four −₹3,470 stops Mar 17/19/20/27
  and +₹210 Mar 23) were banked by Mar 27 and Mar 30 was a zero
  day, paused or not; (ii) the trigger was **masked during the
  slide** — Mar 13's +₹7,685 win sat inside the trailing window
  the whole way down, so the trailing *net* at Mar 20's close
  was still +₹735 while the book was already −₹13,670
  peak-to-trough from Mar 13. A trailing-net trigger cannot see
  a slide that starts from a big win inside its own window.
- **Criteria: (a) FAIL** — worst window −₹13,670.00 vs required
  ≥ −₹7,000. **(b) FAIL** — cost ₹43,357.00 = 42.07% vs cap
  ₹10,305.03. **(c) PASS** — 4 trips ≤ 6.

### November verification (stack, combined brake)

**0 trips, 0 paused days, realised −₹2,680.00** — verified two
ways, not assumed: standalone on November's own sequence (the
Item 3 basis), and in a continuous Jan–Nov run (0 trips in the
November segment; the trailing window never crossed −₹5,000 at
a November close).

### Verdict and what stands

**REJECTED as specified** — criterion (a) fails for both books
and (b) fails for Nifty; per the freeze, the threshold/pause
shape was **not** retuned in this run. Consequences:

- **The December-layer breaker spec is unchanged** — the two
  owner legs exactly as Item 3 implemented them; no entry was
  added to `segment_floor_tracker.md`.
- **The burn bounds for the December ₹1,00,000 decision stand
  exactly as Item 4 measured them: worst 10-trading-day windows
  at 1 lot — Bank −₹6,880, Nifty −₹13,670.** It is now a tested
  fact, not a guess, that this leg shape does not reduce either.
- **Machinery left as Item 3 built it:** `circuit_breaker_stack.py`,
  `breaker_state_stack.json` and `circuit_breaker_stack_log.csv`
  are untouched (hashes verified before/after; the stack runner
  in --dry-run still reproduces the November state to the
  rupee). `circuit_breaker.py` carries ROLL10 only as a
  disabled-by-default option, per the extend-don't-fork brief.
- **What this closes and what it names:** it closes THIS leg
  (trailing-10 realised *net* ≤ −₹5,000 → pause 3). The run
  also measures why it failed: a trailing net is masked by wins
  inside the window, and a trigger graded on the same-length
  window it watches fires, at the earliest, at that window's
  final close. A drawdown-of-the-trailing-curve leg or a
  shorter window would be a **different** leg — a new freeze
  and a new gate, not a fix-up of this one; nothing here adopts
  or arms one.

## FILES

- This report: `scenario_proofing_2026-11-14.md` · combined
  machine results: `scenario_proofing_results.json`
- Item 1: `scenario1_fetch.py` (+ `scenario1_fetch.log`,
  `scenario1_fetch_progress.json`), `scenario1_gate.py`,
  `scenario1_gate_results.json`, `scenario1_orig_check.json`,
  `scenario1_nifty_regimerev_trades.csv`
- Item 2: `november_shadow_fetch.py` (mirror fix +
  `--backfill-shared`)
- Item 3: `circuit_breaker.py`, `circuit_breaker_stack.py`,
  `circuit_breaker_stack_log.csv`, `breaker_state_stack.json`
- Items 3–4: `scenario34_breaker_stress.py`,
  `scenario34_results.json`
- Item 5: `regime_rev_shadow_score.py`,
  `november_shadow_regimerev_bank_log.csv`, cron
  `regime-rev-shadow-scorer-daily`
- Breaker gap (ROLL10): `scenario_breaker_gap.py`,
  `scenario_breaker_gap_results.json`,
  `scenario_proofing_results.json` (key `breaker_gap_roll10_leg`),
  `circuit_breaker.py` (ROLL10 extension, disabled by default) —
  leg REJECTED; breaker state/log files and
  `segment_floor_tracker.md` unchanged

---

## BREAKER GAP — HWM-DD LEG: FREEZE (written 2026-11-14 BEFORE any test of this leg ran)

**Owner order (2026-11-14, free hands): one final brake
variant.** ROLL10's rejection (above) was diagnostic, not
parametric: a trailing-10-day **net** window cannot see these
bleeds, because the bleed windows contain big wins — Nifty's
trailing net was still **+₹735** at the 2026-03-20 close while
the book was already **−₹13,670** peak-to-trough, and Bank's
trailing sum crossed −₹5,000 only at the worst window's final
close. The measured quantity was wrong. The owner's own MTD leg
has the same blind spot in mirror image: it anchors to **zero**
at month start, so a bleed that begins from a profitable
month-to-date never trips it (Bank June 2026: MTD trough
+₹560.00 inside a −₹6,880 window; Nifty March 2026: MTD
+₹12,453.50 at the slide's start, month ending only −₹1,216.50).
The leg below anchors the **same ₹5,000** to the month's
**peak** instead — the owner's leg, generalised. **One shot:**
if it fails the criteria frozen here, the brake work STOPS —
no third variant, no retuning — and the Item 4 burn bounds
(Bank −₹6,880, Nifty −₹13,670) stand as the December input.

### The leg — HWM-DD (uniform for both books; no per-book tuning)

- **Definitions.** Within a calendar month, at the close of a
  non-paused day, MTD = the book's realised month-to-date net
  after that close. **HWM** = the highest MTD reached at any
  **prior** close this calendar month, floored at the
  month-start baseline: HWM starts at **0** each month and only
  rises (if MTD never rose above 0, HWM = 0). The trip check
  uses the prior-close HWM; HWM is then updated with today's
  MTD (a new-high day has drawdown ≤ 0 by construction and
  cannot trip). HWM resets to the 0 baseline at each month
  start, together with MTD.
- **Trigger.** If **HWM − MTD ≥ ₹5,000** at the close of a
  non-paused day, the leg trips. (When HWM = 0 the condition is
  exactly MTD ≤ −₹5,000 — the leg reduces to the owner's MTD
  leg, which is checked first and takes the trip label.)
- **Action.** Pause for the **rest of the calendar month** —
  exactly the MTD leg's pause shape. Everything else is Item
  3's semantics, unchanged: legs on paused days are suppressed
  (realised ₹0, hypothetical recorded as suppressed); MTD does
  not move on paused days; **HWM does not move on paused days**
  (it is a function of MTD closes); the losing **streak is not
  reset** by an HWM-DD trip and does not move on paused days —
  the streak treatment is exactly the MTD leg's.
- **Evaluation order and non-stacking.** All legs are evaluated
  at the close of each non-paused day, in dominance order
  **MTD → HWM-DD → STREAK**; at most one trip is recorded per
  close. Pauses never stack and never extend (trips are
  evaluated only on non-paused days; a rest-of-month pause
  dominates any 3-day pause, exactly as the MTD leg does today).
  ROLL10 stays **rejected and disabled**; it plays no part in
  this test (if both optional legs were ever enabled, the
  frozen order would be MTD → HWM-DD → ROLL10 → STREAK).
- **Implementation.** The leg is added to `circuit_breaker.py`
  itself (extend, don't fork) as an optional parameter,
  **disabled by default**, so every Item 3 and ROLL10 replay
  reproduces exactly with the leg off (asserted in-script
  before any three-leg run). It joins the December-layer spec
  and the stack runner only if adopted below.

### Adoption criteria (frozen; ALL must hold for BOTH books)

- **(a) Burn bound:** the worst rolling 10-trading-day window
  of Jan–Oct on the **three-leg realised series** (Item 4's
  window machinery, 196 windows) is **≥ −₹5,500 for Bank**
  TUNED STACK v2 and **≥ −₹7,000 for Nifty** TUNED v1.
- **(b) Cost:** Jan–Oct cost vs the standing totals (stack
  **+₹127,351.50**; TUNED v1 **+₹103,050.25**), scored two
  ways: **combined** (standing − three-leg) and **marginal**
  (two-leg − three-leg — what this leg alone costs on top of
  the owner's standing two-leg brake). **The MARGINAL cost
  governs**, capped at **10% of the standing total** (Bank
  ≤ ₹12,735.15; Nifty ≤ ₹10,305.03). Reason, frozen in advance:
  the two-leg cost is the owner's already-standing spec — it
  already costs TUNED v1 ₹26,617.50 (25.8%) before this leg
  acts — so scoring this leg on the combined figure would fail
  Nifty no matter what HWM-DD does and would price the wrong
  decision. The combined cost is computed and reported
  alongside, not hidden.
- **(c) Trip count:** **HWM-DD trips ≤ 4 per book** across
  Jan–Oct (this leg's trips only; MTD and STREAK trip counts
  reported alongside) — a brake that fires constantly is a
  strategy change, not a brake.

**ADOPT** into the December-layer spec only if (a), (b) and
(c) all hold for both books — then the dated entry goes into
`segment_floor_tracker.md` and the leg is enabled in the stack
runner (default ON, documented). Otherwise **REJECT** as
specified: machinery and tracker untouched, the Item 4 burn
bounds stand, and the brake work stops here.

---

## BREAKER GAP — HWM-DD LEG: TEST RESULT (2026-11-14) — **VERDICT: ADOPTED**

**Controls first (asserted in-script before any scored run):**
(1) with the leg off, the extended `circuit_breaker.simulate`
reproduces Item 3 **exactly** (stack: one STREAK trip
2026-07-06, +₹127,475.50, suppressed −₹124.00; TUNED v1: two
MTD trips, +₹76,432.75, 28 paused days; stack November 0 trips,
−₹2,680; legacy November control fires at the Nov 4 close).
(2) With ROLL10 on and HWM-DD off, the same code reproduces the
**rejected ROLL10 run exactly** (stack +₹124,995.50, trips
ROLL10 2026-06-22 + STREAK 2026-07-06; TUNED v1 +₹59,693.25,
4 trips) — the new parameter disturbs nothing when disabled.
(3) Two synthetic series prove the leg's semantics: a
bleed-from-peak month the two-leg brake never trips on (MTD
never ≤ −₹5,000, losses interleaved) trips **HWMDD only**
(peak +₹8,000 → MTD +₹2,300, drop ₹5,700), and a
never-positive month produces a **byte-identical** run with and
without the leg, its single trip labelled MTD — the leg reduces
to the owner's MTD leg when HWM = 0, as frozen. Every total
below was independently re-summed from the realised day series
by a second code path, and every worst window recomputed by a
brute-force slice-sum implementation — all exact. Test driver
`scenario_breaker_hwm.py`; machine results
`scenario_breaker_hwm_results.json`, merged into
`scenario_proofing_results.json` (key `breaker_gap_hwmdd_leg`).

### Bank TUNED STACK v2

- **HWM-DD trips: 1 — 2026-06-10 close** (HWM **+₹7,440.00**,
  June's peak MTD reached Jun 8; MTD at trip **+₹2,280.00**;
  drop **₹5,160.00**) → paused Jun 11–30 (13 trading days);
  suppressed hypothetical **+₹760.00** net (Jun 16's −₹1,720
  stop avoided, Jun 24's +₹2,480 win forgone). This is the
  Item 4 bleed, caught **eight trading days earlier** than
  ROLL10 managed (Jun 22) — and before its third stop, not
  after its last. The STREAK trip at 2026-07-06 is unchanged.
- **Paused days: 16** (13 HWM-DD + 3 streak). **Totals:**
  standing **+₹127,351.50** · two-leg +₹127,475.50 · three-leg
  **+₹126,715.50**. HWM-DD's marginal effect: **−₹760.00**.
- **Worst rolling-10 window: −₹6,880.00 → −₹5,160.00**
  (the same 2026-06-09 → 06-22 window, truncated by the
  pause). Worst regime-concentrated window likewise improves,
  −₹4,400.00 → −₹3,758.00 (2026-02-26 → 03-12).
- **Criteria: (a) PASS** — −₹5,160.00 ≥ −₹5,500 (margin
  ₹340.00). **(b) PASS** — marginal cost ₹760.00 = 0.60% of
  standing ≤ ₹12,735.15 (combined cost ₹636.00 = 0.50%,
  reported per the freeze). **(c) PASS** — 1 HWM-DD trip ≤ 4.

### Nifty TUNED v1

- **HWM-DD trips: 2.** **2026-03-19 close** (HWM
  **+₹12,453.50**; MTD at trip **+₹5,513.50**; drop
  **₹6,940.00**) → paused Mar 20–30 (6 trading days);
  suppressed hypothetical **−₹6,730.00** — the Mar 20 and
  Mar 27 −₹3,470 stops never happen (Mar 23's +₹210 forgone).
  The Item 4 bleed is cut mid-slide, after two of its four
  stops. **2026-07-14 close** (HWM **+₹12,264.00**; MTD
  **+₹6,968.50**; drop **₹5,295.50**) → paused Jul 15–31
  (13 days); suppressed **+₹3,494.50** (mostly forgone wins —
  the leg's cost side, priced). The MTD trips (2026-02-06,
  2026-05-11) are unchanged from Item 3.
- **Paused days: 47** (28 MTD + 19 HWM-DD). **Totals:**
  standing **+₹103,050.25** · two-leg +₹76,432.75 · three-leg
  **+₹79,668.25**. HWM-DD's marginal effect: **+₹3,235.50** —
  on this book the leg more than pays for itself against the
  two-leg series (March's avoided stops outweigh July's
  forgone wins).
- **Worst rolling-10 window: −₹13,670.00 → −₹6,940.00.** The
  March window itself (2026-03-16 → 03-30, now also the worst
  regime-concentrated window) improves to −₹6,940.00, and the
  graded worst is set by the February window
  (2026-02-01 → 02-12, −₹6,940.00 — the pre-trip slide the
  owner's MTD leg itself bounds). **Criteria: (a) PASS** —
  −₹6,940.00 ≥ −₹7,000, by exactly ₹60.00; the margin is thin
  and is stated, not rounded away. **(b) PASS** — marginal
  cost **−₹3,235.50** (a gain) ≤ ₹10,305.03; combined cost
  ₹23,382.00 = 22.69% is reported per the freeze — it is the
  two-leg brake's pre-existing ₹26,617.50 cost minus this
  leg's ₹3,235.50 gain, and per the frozen governance it does
  not decide this leg. **(c) PASS** — 2 HWM-DD trips ≤ 4
  (4 trips total across all legs).

### November verification (stack, combined three-leg brake)

**The trip count is 1, not 0 — verified two ways, and the
expectation behind the brief is corrected by the measurement.**
November DID have a positive MTD peak: the Nov 4 win took MTD
to **+₹2,480.00** (HWM), and the month then fell through it —
drawdown ₹1,720 at the Nov 9 close, ₹3,440 at Nov 12,
**₹5,160.00 at the Nov 13 close**, where **HWM-DD trips**
(HWM +₹2,480.00, MTD −₹2,680.00). Both the standalone November
run and the continuous Jan–Nov run produce this trip. Paused
days inside the Nov 2–13 record: **0** (the trip lands on the
record's last close) and November's realised total is unchanged
at **−₹2,680.00** — but under the adopted December layer the
stack now stands **paused for the rest of November** from this
trip. The leg fires on the owner's actual live month, on
exactly the bleed-from-a-profitable-peak shape it was built
for; the "no positive peak" assumption does not survive the
Nov 4 win.

### Verdict and what stands

**ADOPTED — all three criteria hold for both books.** Per the
freeze, the December-layer breaker spec now has **three legs**:
the owner's MTD leg (MTD ≤ −₹5,000 → pause rest of month), the
**HWM-DD leg** (peak-anchored: HWM − MTD ≥ ₹5,000 → pause rest
of month), and the owner's streak leg (3 consecutive losing
days → pause 3). Consequences executed with this run:

- **New burn bounds for the December ₹1,00,000 decision** (the
  Item 4 bounds, superseded): worst 10-trading-day windows at
  1 lot **with the combined brake — Bank −₹5,160, Nifty
  −₹6,940** (from −₹6,880 / −₹13,670 unbraked and under the
  two-leg brake).
- The dated adoption entry is added to
  `segment_floor_tracker.md`'s December-layer breaker spec,
  and the leg is **enabled in the stack runner**
  (`circuit_breaker_stack.py`, default ON, documented), so the
  forward daily record (`circuit_breaker_stack_log.csv`,
  `breaker_state_stack.json`) now carries the Nov 13 HWM-DD
  trip and the stack's rest-of-November pause.
- In `circuit_breaker.py` the leg remains an optional
  parameter (extend, don't fork): every Item 3 / ROLL10 replay
  still reproduces exactly with it off — asserted in this run.
- This closes the brake work as ordered: the first variant
  (ROLL10) measured the wrong quantity and was rejected; the
  peak-anchored leg measures the drawdown itself and passes.
  No further brake variant is pending.
