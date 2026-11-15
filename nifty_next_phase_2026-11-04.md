# NIFTY NEXT PHASE — tuning DEC-S1 (2026-11-04)

**Direction:** Chandu, 2026-11-04 — tune DEC-S1 to its next phase, the way Bank v21 was tuned to v22 (which applied the same tune-up treatment to Nifty). **DEC-S1 stays frozen as the December candidate** — `nifty_engine_frozen.md`, the adopted leg files and every November book/log are untouched; anything produced here is a NEW candidate. Nothing armed, no crons. Basis throughout: Nifty option premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, paper only, real money ₹0.

**Headline verdict: DEC-S1 stands untuned.** The base was independently verified to the paisa (Step 0). No previously-gated lever is available to assemble (Step 1: the only non-failed item is an exact no-op). The one new lever — the Bank EVE-06(a) re-entry port — **fails as registered** (Step 2): its trigger almost never occurs on this book, every occurrence is blocked by the owner's −₹3,000 day-cap, and even with the cap removed the sensitivity is one scorable leg that ties its own placebo. The assembled book is therefore DEC-S1 itself (Step 3): **97 legs, +₹91,168.50 Jan–Oct 2026, ₹9,116.85/month, gap to the ₹15,000 bracket ₹58,831.50** — unchanged.

**Inherited qualifications (restated, not relitigated):** DEC-S1 was adopted over two FAILED-AND-WAIVED gate legs — FT 34.0% vs the standing book's 34.3%, and March flipping green → red (+₹7,895.00 → −₹11,846.50). Both stand on this book exactly as adopted.

---

## STEP 0 — Base verification (independent route, before anything)

**Store gap found and repaired first (the Bank ladder precedent).** The daily2leg premium stores were built with a KEEP filter retaining only 10:00–15:15 bars (`daily2leg/build_store.py`): 29 of the 97 legs (Component A entries 09:35–09:55) had no entry bar, and no leg had its 15:20 square-off bar. A first scoring pass on the raw stores produced +₹75,428.75 and was **discarded in full** — no figure from it stands. Repair (`nifty_next_phase_backfill.py`, declared sources only — the Nifty engine's exact-tag candle caches in `aggressive_data/`, `v4_options_oct_data/`, `historical_proof_data/`, plus the store builder's own range caches): every source bar overlapping a stored bar was verified to agree exactly (0 disagreements across the 97 contract-days), then **1,294 bars added, 0 altered**, backups at `daily2leg/prem_nifty.json.pre_nextphase_backfill_2026-11-04.bak` and the weekly equivalent. One engine file (2026-02-03, Component B) lacks only the 09:15 bar; that leg enters 10:05, so its path is complete.

**Verification** — the 97 frozen legs (`nifty_engine_r11_decs1_legs.json`) re-scored from the repaired stores under an independent implementation of the frozen S5 geometry (stop −50 before target incl. entry bar; BE arm +50 → stop to entry; tgt1 +90 → runner lock +60, TGT2 +175; square-off at the 15:20 close; entry = entry-bar open). **16/16 fields MATCH the frozen Cycle-168 / adoption record:**

| Field | This run | Frozen record |
|---|---|---|
| Legs / NC | 97 / 0 | 97 / 0 |
| Total | **+₹91,168.50** | +₹91,168.50 |
| Month table | identical all 10 months (Mar −₹11,846.50 incl.) | — |
| Halves (Jan–May / Jun–Oct) | +₹45,393.50 / +₹45,775.00 | same |
| Components A / B / C | 35 / +₹54,102.00 · 49 / +₹33,624.75 · 13 / +₹3,441.75 | same (pair identity holds) |
| FT / frequency | 34.0% (33/97) / 2.39 per wk | same |
| Placebo (+30-min entries) | +₹52,867.25 (beaten) | same |
| Ex-top-3 legs | +₹57,703.50 | same |
| Worst day / worst 3-day / drawdown | 2026-07-14 −₹5,295.50 / −₹10,630.00 / −₹17,360.00 | same (EVE-04 record) |
| Entry + 15:20 bars present | 97/97 | — |

Exit anatomy of the verified base (for Step 2 and the phase-2 arithmetic): runner legs carry the book — runner_square_off 11 legs +₹70,854.50, runner_stop 17 legs +₹62,560.00, runner_target 5 legs +₹55,775.00 (runner complex: 33 legs, +₹189,189.50). The drag: full stops 24 legs −₹83,280.00 (every one exactly −₹3,470.00), plain square-offs 33 legs −₹13,201.00, BE stops 7 legs −₹1,540.00.

---

## STEP 1 — Inventory: every lever ever gated on the causal book / DEC-S1

Sources: `nifty_engine_log.md` (Cycles 1–169), `nifty_engine_lessons.md`, `november_rsi_nifty_log.md` (EVE runs), the BIG BUILD / combined-rulebook record.

**Already inside DEC-S1 (passed or owner-adopted during construction — not assembly material):** Component A = causal admission (≥2 systems, 2nd-system bar ≤ 09:55; solo (lA) at own bar; EXP0) with the Round-6 banked geometry (lock +60, C124, +₹500.50; square-off 15:20, C129, +₹2,983.50) · Component B = gap-fade 10:05 (C145 form) · Component C = expiry-day sleeve, standing geometry (C138 form). B and C entered over the two waived gate legs named above.

**Failed on this frame — stays failed:**

| Family | Candidates (cycle) | Verdict |
|---|---|---|
| Exit geometry | SO1430 (C2), NP1130 (C4), lock90 (C6), BE40 (C7), RATCHET150 (C11), PSTOP25 (C15), SQ1525 (C21), lock40 (C123), TGT2-150 column (C125–127), sq 14:45 (C128), entry-time lock split (C110–111), adopted-book micro-grid 27 cells (C47–73) | all REJECTED; the adopted geometry point is the peak of its own grid |
| Trailing (owner directive, 3 distinct forms) | TR-N1 −₹5,736.25 and TR-N2 −₹21,599.50 **on DEC-S1** (BIG BUILD); NIFTY-EVE-05 arm-delay +50→+70 −₹4,273.75 (standing book) | FAIL in every form — trailing hurts this book |
| Admission / state gates | SA2D streak (C10), PDROOM (C13, inert), WROOM5 (C14), Bank-spot conditioning (C134–136, C160–161), OR-width terciles (C162–163), day-state terciles (R4 WS4 — no negative tercile), premium-band tails (C98–99), strike axis ITM (C19, C103–104), confirmation permutations (C22–24, C114–118), solo books all four systems (C119–122) | all REJECTED |
| Sleeve additions | EV5 solo non-Skill (C17, −₹16,498.50), S1-44 union (C18, −₹49,965.75), gap-FOLLOW (C132, −₹63,495.40), fade restricted forms (C142/143/144/151 — single-leg refusals; the unrestricted 10:05 form is Component B), (lA) CE mirror (C137, −₹32,862.90), expiry sleeve own-geometry (C146, −₹2,406.25), afternoon-range sleeve (C147, −₹8,056.25), NS1 second-leg transplant (C92–97, −₹10,410.00, 3/3 full stops), WEEKLY carriage (C20), causal (lA) union discards (C155, −₹7,653.00), post-expiry population (C164, adverse tail), solo-Skill November sleeves EVE-01/02b/03b (FAIL; 02b/03b also carry an NC + audit violation on the named 2026-10-28 leg) | all REJECTED |
| DTE pockets | EXP1 skip DTE ≤ 1 (C34), EW-G7 (C35), DTE-0 re-admission under 6 geometries (C105–109/112) | all REJECTED; EXP0 (already in the book) confirmed causally |

**Not a pass:** NIFTY-EVE-04, the realised day-loss cap −₹3,000 on DEC-S1, is an **exact no-op** — 0 skippable legs (on all 9 multi-leg days the later leg enters before any earlier leg exits, so a causal realised-cap skip cannot exist on this book). Assembling it would change ₹0.00; it is recorded here so the assembly's emptiness is evidence, not omission. (The close-based intraday cap overlay from the combined rulebook is an operational bleed guard, not a return lever — its DEC-S1 worst day measured −₹4,232.75 against the −₹3,000 cap — and is likewise not assembly material, exactly as the Bank v22 assembly added no guard.)

**Never tested on this frame:**
- **EVE-06 afternoon-addition** — population was empty on the primary frame; re-checked here on DEC-S1's own frame: the N1 pool contains **0 confirmed (≥2-system) keys with entry ≥ 12:00 at all**, so the not-in-DEC-S1 afternoon population is **0** on this frame too. (DEC-S1's own 4 afternoon legs, 12:10–13:20, come from Component A's solo-(lA)/re-timed admissions, not from the confirmed pool.) NOT TESTABLE — closed on evidence.
- **Re-entry after a stop-out (the Bank EVE-06(a) port)** — never tested on Nifty. Its nearest failed relative is the NS1 second-leg transplant (C92–97); the distinction, in one line: NS1 fired a second leg after *any* resolved morning leg on an afternoon OR re-cross (entries from 11:10, not stop-conditioned, no day-cap), whereas the port fires *only* after a full −50 stop-out, *only* on a ≥ 12:00 close back through the morning-range extreme at/after the stop's own exit bar, max 1/day, under the −₹3,000 realised day-cap. → Step 2.

**Step-1 conclusion: assembly material = nothing.** Every return lever that ever passed on this population is already inside DEC-S1; every other gated lever failed; the one inert item adds zero.

---

## STEP 2 — Re-entry increment (Bank EVE-06(a) port, pre-registered by analogy)

**Spec as registered:** on a DEC-S1 day whose earliest full-stop (−50) leg has exited, if Nifty spot closes back through that morning's range extreme (09:15–11:55 bars) on the stopped leg's side on a 5-min bar at/after 12:00 and at/after the stop's exit bar → re-enter same side at the next bar; strike ATM100 at the entry bar's spot open; expiry = the stopped leg's expiry (its component's contract convention — A/B monthly, C the weekly expiring that day); exits = frozen S5 geometry; max 1/day; skipped if the day's realised DEC-S1 net (legs exited on/before the trigger bar) is already ≤ −₹3,000. Placebo: trigger scan shifted +60 min. Increment gate (the Bank phase-2 standard): total > 0, beats the shifted placebo, both halves ≥ 0, timing clean, NC = 0; ex-top-3 reported as a flag either way. (BE-stop days — 7 — and runner-stop days — 17 — are outside the population by the Bank registration, which anchors on the full −50 stop only; counted here for the record.)

**Result — FAIL, and the failure is structural, not marginal:**

- Population: **24 stop days** (24 full-stop legs, −₹83,280.00).
- Reclaim triggers found: **4 of 24 days (17%)** — vs Bank's 16 of 36 (44%). DEC-S1's stopped mornings almost never come back through the whole morning range; its stop-outs are mostly genuine trend days (consistent with the book's runner-harvest anatomy: the money is made by legs that never stop).
- **All 4 triggers were blocked by the day-cap**, because a single Nifty full stop (−₹3,470.00) already breaches the −₹3,000 cap on its own — the realised net at every trigger was −₹3,470.00 or −₹3,690.00 (anchor stop, on two days plus a −₹220 BE stop):

| Date | Anchor leg (component, direction, entry → stop exit) | Trigger | Realised at trigger | Outcome |
|---|---|---|---|---|
| 2026-02-02 | A, CE, 09:35 → 10:05 | 13:00 | −₹3,470.00 | BLOCKED (cap) |
| 2026-03-17 | C, CE, 10:00 → 11:30 | 14:10 | −₹3,690.00 | BLOCKED (cap) |
| 2026-04-27 | A, CE, 09:50 → 11:35 | 13:20 | −₹3,470.00 | BLOCKED (cap) |
| 2026-05-11 | A, PE, 09:40 → 11:40 | 15:00 | −₹3,690.00 | BLOCKED (cap) |

- **Increment as registered: 0 legs, ₹0.00.** Placebo (+60 min): 0 legs, ₹0.00. Halves 0/0. Ex-top-3 ₹0.00. Double-stops (whipsaws): 0 — no re-entry was ever taken. NC: 0. Gate: total > 0 **FAIL**, beats-placebo **FAIL** → **increment REJECTED; nothing assembled.**

**Sensitivity — decision support only, NOT a candidate and NOT assembled:** with the day-cap removed entirely, the same 4 triggers produce exactly **1 scorable leg** (2026-04-27, entry 13:25, square-off **−₹249.25**) — and the +60-min placebo finds the same persistent reclaim and produces the *identical* leg (−₹249.25), so there is no placebo separation at all. The other 3 triggers are NOT_COMPUTED even in the sensitivity: 2026-02-02 and 2026-05-11 (the re-struck ATM contract-day is incomplete in every declared source) and 2026-03-17 (no candles for the re-struck contract exist anywhere — it was never in any fetched population). Removing the cap therefore does not rescue the lever: on this book the re-entry is simultaneously rare, mostly unscorable, and worthless on its one scorable instance. The Bank asymmetry is real economics, not a porting bug: Bank's full stop is −₹1,720 against the same −₹3,000 cap (headroom to re-enter), Nifty's is −₹3,470 (none) — and Bank's stopped mornings reclaim at 44%, Nifty's at 17%.

---

## STEP 3 — Assembly + full gate

Assembly = base + Step-1 passes (none) + Step-2 increment (failed, excluded) = **DEC-S1 unchanged**. The full gate was run on the assembled book in this same run (it is the Step-0 verification, restated as the gate sheet):

| Gate leg | Result |
|---|---|
| Net (assembled) | **+₹91,168.50** (97 legs) — Δ vs base ₹0.00 |
| Monthly pace vs bracket | **₹9,116.85/month vs ₹15,000 — gap ₹58,831.50** |
| Timing audit | clean — 0 violations (base: entries at bar opens, geometry reads bars ≥ entry only; re-entry audit vacuous, 0 legs taken) |
| Placebo (+30-min entries, whole book) | +₹52,867.25 — beaten by ₹38,301.25 |
| Halves | +₹45,393.50 / +₹45,775.00 — both positive |
| Month table / flips | Jan +19,211.25 · Feb +5,038.75 · Mar −11,846.50 · Apr +28,416.00 · May +4,574.00 · Jun −1,331.00 · Jul +5,839.00 · Aug +841.25 · Sep +20,265.25 · Oct +20,160.50 — no green month flips (identical to base by construction); red months remain Mar and Jun, as adopted |
| Ex-top-3 legs / days | +₹57,703.50 / +₹57,703.50 (identical: the top-3 days are each a single +₹11,155 runner-target leg) |
| Worst day / worst 3-day / worst drawdown | −₹5,295.50 (2026-07-14) / −₹10,630.00 / −₹17,360.00 — unchanged vs base |
| % positive days | 51.1% (45 of 88 leg-days) |
| Frequency | 97 legs, 2.39/wk, 9.7 legs/month |
| NC | 0 |
| Independent re-sum (from the written trades CSV, read back cold) | **EXACT** — base ₹91,168.50, re-entry ₹0.00, assembled ₹91,168.50 |

**Verdict: there is no tuned Nifty book to adopt. DEC-S1 stands untuned at ₹9,116.85/month with its ₹58,831.50 gap and its two waived gate legs attached.** This is the Bank afternoon-sleeve precedent applied honestly: a rejected lever is a result, and an empty assembly is reported as empty.

## What a phase 2 would need (arithmetic, from the verified base)

Current capture: **₹939.88/leg** at **9.7 legs/month**. Closing ₹58,831.50 over a Jan–Oct window requires any of:
- **Frequency only:** +62.6 legs at current capture → ~160 legs (16.0/month, 3.93/wk, +65% over the current 2.39/wk);
- **Capture only:** +₹606.51/leg → ₹1,546.39/leg (+64.5%) at the current 97 legs;
- **A mix on the frontier** (legs × ₹/leg ≥ ₹1,50,000): e.g. 128 legs × ₹1,243, or 120 legs × ₹1,300.

Where the room visibly sits in the anatomy — the 24 full stops (−₹83,280) and 33 plain square-offs (−₹13,201) against the runner complex (+₹189,189.50) — every admission, exit, strike, state and sleeve axis over this population has already been gated shut (Step 1 inventory, Rounds 1–11 + EVE). A phase 2 therefore cannot be another tweak of this frame: it needs a genuinely new signal source (the Round-10/11 exhaustion conclusion, now re-confirmed by the re-entry port's failure), or December fresh data judging DEC-S1 as frozen. The one thing this run adds to that record: the afternoon of a Nifty stop-out day is now measured — it reclaims the morning extreme on 4 of 24 days, and those 4 afternoons are worth −₹249.25 on the only scorable instance. There is no frequency hiding there.

## Files

- Scorer: `nifty_next_phase_score.py` · Store repair: `nifty_next_phase_backfill.py` (backups beside the stores) · Diagnostics (no-cap sensitivity, trigger cross-checks): `nifty_next_phase_diag.py`
- Trades: `nifty_next_phase_trades.csv` (97 BASE rows, 0 REENTRY rows) · Results: `nifty_next_phase_results.json`
- Frozen DEC-S1, its leg files, and all November books/logs: unmodified. Nothing armed; no cron created or changed; the November DEC-S1 shadow continues exactly as wired separately.
