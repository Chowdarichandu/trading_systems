# DAILY EARNER BUILD — Skill + B2/NS1 + Volrix (buying only)
### Owner directive 2026-11-13 14:42 IST · Outcome bar correction 14:44 · Sequencing order 14:45
### Deliverable for Monday 2026-11-16, before 09:00 IST

**Paper only. Real money ₹0. No orders. This build edits no running book, job, FREEZE or settlement file — it is a candidate daily layer, gated like everything else.**

**THE BAR (owner, outcome-only):** ₹2,000–3,000/day COMBINED ("below 5000 I am asking; anything above is God's gift"). Investment/capital is NOT part of the target — no capital figure gates, passes or fails any configuration in this report. Verdict math = combined average ₹/day vs the ₹2,000–3,000 zone, plus % of days in/above that zone.

**Systems (only these three, as built in the early days):**
1. **Skill** — Day Trader Skill adaptation, Skill V3 standalone (solo + shared keys, its own exit geometry).
2. **B2/NS1** — the legacy construction, BNF-PAPER-V1 frame (Bank) / its stored pool frame (Nifty), taken as-is.
3. **Volrix** — variant (b) intraday adaptation at −1.0%: prev-day close ≤ −1.0% → buy ATM CE next session 09:20, stop −50 / target +90 premium points, square-off 15:10, 10-session cooldown. (October standalone, verified: Nifty +₹5,630, Bank +₹2,480.)

**Hard rules:** pure option BUYING only (no premium selling anywhere); 1 lot per index (Bank 30 / Nifty 65); cost ₹220/trade inside every net; entries/exits on 5-min closes; UNIQUE-ONCE dedupe across systems (a trade two systems take counts once); real entries producible (full trade lists in the CSVs beside this report).

**Sequencing (owner order):** Bank Nifty first (Milestone 1) → Nifty (Milestone 2) → Stocks verification only, no new book (Milestone 3) → combined daily picture + Monday wiring spec.

---

# MILESTONE 1 — BANK NIFTY

## 1.1 Pre-registration (written before any assembly total was computed)

**Streams (all premium basis, per 1 lot, ₹220/trade inside nets):**
- **LEGACY (B2/NS1 frame):** `bank_engine_r6_v21_trades.csv` — the frozen BNF-PAPER-V1 ledger, 99 legs, independently re-summed in this run before use: **+₹83,650.50** (matches the recorded standing exactly). Taken as-is, frame geometry (runner/lock, SQ 15:20). This stream is the causal rebuild (post-WS0 audit); the voided v19 headline is not used anywhere.
- **SKILL (standalone increment):** Skill V3 keys from the premium-scored B2 pool, `historical_proof_bank_B2_trades.csv` (89 pool legs, G0 geometry = stop −50 / target +90 / SQ 15:10, entry = entry-bar open — the identical geometry the November Skill shadow runs for Bank). Skill stream = pool legs whose `source_systems` include "Skill V3" (70 legs). KNOWN LIMITATION, stated before scoring: the pool holds only keys the frozen B2 rule kept; blocked Skill CE solo keys were never logged in Jan–Oct (BANK-EVE-10, NOT TESTABLE) — so this is the stored Skill population, not a hypothetical complete one.
- **VOLRIX (standalone increment):** Volrix (b) −1.0% legs from the same pool file. Pre-scoring validation: the pool's Volrix-source legs are exactly the 13 published standalone entry days (22 Jan, 20 Feb, 9 Mar, 24 Mar, 10 Apr, 29 Apr, 1 Jun, 24 Jun, 9 Jul, 23 Jul, 2 Sep, 25 Sep, 26 Oct), all CE 09:20, and the October leg reproduces the standalone score exactly (26 Oct +₹2,480.00). The pool scoring (G0) is identical to variant (b)'s frozen exit geometry, so these stored legs ARE the standalone (b) stream.

**Assembly:** Bank book = LEGACY (all 99 legs) + SKILL pool legs whose key is not in the legacy frame + VOLRIX pool legs whose key is not in the legacy frame.
**Dedupe:** key = (date, direction). The pool holds exactly one key per (date, direction) (verified 89/89). A pool leg is dropped if the legacy frame holds a BASE leg with the same (date, direction) — the frame's instance (its own causal entry and geometry) survives. Pool legs are single rows, so a Skill+Volrix co-sourced key enters once, labelled with both sources.
**Costs:** ₹220/trade already inside every stored net; no second cost is applied.

**Gate (all legs must pass; bars fixed here, before totals):**
- G1 Total: assembly net > 0, and assembly net > legacy alone (the layer must add, not dilute).
- G2 Halves: Jan–May ≥ 0 AND Jun–Oct ≥ 0.
- G3 Ex-top-3: assembly total minus its 3 best legs > 0.
- G4 Placebos: (a) random-skip — 1,000 draws, each skipping from the legacy book the same number of legs the increment adds; the assembly total must exceed the draws' 90th percentile. (b) delay-1-day — increment legs' nets reassigned to the next trading day and the day-line re-drawn (reported as a timing-luck check, not a pass/fail leg).
- G5 Consistency (owner's test, operationalised here before scoring): red months ≤ 3 of 10 AND best single month ≤ 50% of the Jan–Oct total AND worst month reported by name. A book carried by one month fails even if the total is large.
- G6 Timing audit: every stream is a previously audited causal ledger (v21 = causal rebuild, 0 violations in its own gate; proof pool = entry-bar-open premium scoring of keys generated causally; Volrix trigger uses prev-day close only). Assembly introduces no new timing.
- G7 NC: NOT_COMPUTED legs = 0 in all three streams.

**November check (Nov 2–13, 9 trading days; Nov 10 = Diwali holiday):** LEGACY from `november_paper_bank_log.csv` (final through Nov 12) + Nov 13 from the live watcher record; SKILL from `november_shadow_skill_bank_log.csv`; VOLRIX from a trigger scan of daily closes Nov 2–13 with the continuous cooldown (last (b) entry 26 Oct). Deduped on the same (date, direction) rule, frame instance surviving. Reported day-by-day with the cumulative line — the owner's standard is PROGRESSIVE, not degradative.

## 1.2 The three Bank streams, as stored (Jan–Oct 2026, premium, 1 lot)

| Stream | Legs | Jan–Oct net | Avg / trading day (205 days) |
|---|---|---|---|
| LEGACY — B2/NS1 frame (BNF-PAPER-V1) | 99 | **+₹83,650.50** | ₹408.05 |
| SKILL — Skill V3 standalone (stored pool population) | 70 | +₹3,596.00 | ₹17.54 |
| VOLRIX — (b) intraday −1.0% | 13 | +₹2,840.00 | ₹13.85 |

- **Where Skill and Volrix actually earn is INSIDE the frame.** Of the 76 pool legs carrying a Skill and/or Volrix source, 48 sit on keys the legacy frame also took (dropped from the increment as duplicates) — under G0 scoring those 48 legs are worth **+₹25,659.00**. The legs Skill/Volrix take *outside* the frame's admission are the increment below — and they lose.
- Volrix stream detail: 6 targets (+₹2,480) / 7 stops (−₹1,720), no square-offs; an occasional overlay (13 legs in 10 months), exactly as its October report concluded.
- Skill stream limitation (pre-registered §1.1): blocked CE solo keys were never logged in Jan–Oct, so the stored Skill population is what exists; nothing was reconstructed or estimated.

## 1.3 The full assembly — GATE FAIL

Assembly = 99 legacy legs + 28 increment legs (19 Skill-only, 6 Volrix-only, 3 Skill+Volrix co-sourced) = **127 legs, +₹59,667.50**. The increment is **−₹23,983.00**.

| Gate leg | Bar | Result | Verdict |
|---|---|---|---|
| G1 total + adds over legacy | > 0 and > ₹83,650.50 | +₹59,667.50 | **FAIL** (dilutes the frame by ₹23,983) |
| G2 halves | both ≥ 0 | H1 +₹60,515.00 / H2 **−₹847.50** | **FAIL** |
| G3 ex-top-3 | > 0 | +₹30,627.50 | pass |
| G4 random-subset placebo | increment above p90 of random 28-leg pool subsets | increment −₹23,983 vs p50 +₹5,459 / p90 +₹17,036 → **0.1st percentile** | **FAIL** (random legs beat the selected increment) |
| G5 consistency | red months ≤ 3, best month ≤ 50% | red months **4** (Apr, Jun, Jul, Aug); best month Feb = 38.0% | **FAIL** |
| G6 timing | audited ledgers only | all streams previously audited causal ledgers; assembly adds no new timing | pass |
| G7 NC | 0 | 0 | pass |

Month table (₹):

| Month | Legacy | Full assembly |
|---|---|---|
| Jan | +22,748.00 | +19,308.00 |
| Feb | +20,480.00 | +22,697.00 |
| Mar | +1,120.00 | +1,880.00 |
| Apr | −90.00 | −1,050.00 |
| May | +17,680.00 | +17,680.00 |
| Jun | +560.00 | −6,320.00 |
| Jul | −3,680.00 | −10,560.00 |
| Aug | −873.50 | −6,993.50 |
| Sep | +10,776.50 | +5,616.50 |
| Oct | +14,929.50 | +17,409.50 |

Worst month (assembly): **July, −₹10,560.00**. Delay-1-day timing check (descriptive): shifting the increment legs one trading day later leaves the ≥₹2,000-day count at 41 vs 44 actual — the failure is not a timing artefact. Time-overlap diagnostic: exactly 1 of the 28 increment legs (8 Jul PE, −₹1,720) overlaps a legacy holding window the same day; removing it changes no gate leg.

## 1.4 Fallbacks, gated in order

| Config | Legs | Total | Halves | Ex-top-3 | Red months | Placebo (increment) | Gate |
|---|---|---|---|---|---|---|---|
| A1 Legacy+Skill | 121 | +₹61,587.50 | +59,755 / +1,832.50 | +₹32,547.50 | 4 | −₹22,063, 0.1 pct | **FAIL** (G1, G4, G5) |
| A2 Legacy+Volrix | 108 | +₹76,570.50 | +60,978 / +15,592.50 | +₹47,530.50 | 4 | −₹7,080, 3.2 pct | **FAIL** (G1, G4, G5) |
| A3 Skill+Volrix (no legacy) | 76 | +₹1,676.00 | +26,017 / −24,341 | −₹5,764.00 | 5 | — | **FAIL** (G2, G3, G5) |
| B2 Skill alone | 70 | +₹3,596.00 | +25,257 / −21,661 | −₹3,844.00 | 5 | — | **FAIL** (G2, G3, G5) |
| B3 Volrix alone | 13 | +₹2,840.00 | +6,480 / −3,640 | −₹4,600.00 | 2 | — | **FAIL** (G2, G3; best month = 87.3% of total — one-month-carried) |
| **B1 Legacy alone** | **99** | **+₹83,650.50** | **+61,938 / +21,712.50** | **+₹54,610.50** | **3** (Apr −90, Jul −3,680, Aug −873.50) | n/a (frozen audited book) | **PASS — every leg** |

## 1.5 November 2–13 — day-by-day (Bank)

Parts: LEGACY **−₹1,920.00 · 6 trades** · SKILL shadow **−₹1,160.00 · 8 trades** · VOLRIX **no fires** — the trigger scan (prev-day closes, verified daily closes) shows Bank Nifty rose on every deciding day of the window (+0.58% … +3.33%); the 10-session cooldown from the 26 Oct entry also blocked entries through Nov 9. A rebound system cannot fire into a rally; that is zero trades, not missing data.

Six Skill-shadow legs share a (date, direction) with a legacy leg. Two are the *identical* leg (Nov 2 PE 54800 @10:20; Nov 9 PE 58900 @10:45 — same strike, time, premium in both logs). Four are genuinely different trades the (date, direction) rule would wrongly merge (Nov 3: Skill CE 55500 @10:00 ₹841.85 vs legacy NS1 @10:20 ₹867.60; Nov 4: 55800 @09:35 vs NS1 55900 @13:40; Nov 11: 60700 @09:40 vs NS1 60800 @14:00; Nov 12: 61300 @09:35 vs NS1 61200 @12:45). Both dedupe lines are therefore reported; the trade list CSV flags every row under both rules.

| Day | Pre-registered dedupe (date, direction) | Cumulative | Identical-leg dedupe | Cumulative |
|---|---|---|---|---|
| Nov 2 | −1,720.00 | −1,720.00 | −1,720.00 | −1,720.00 |
| Nov 3 | −1,720.00 | −3,440.00 | −3,440.00 | −5,160.00 |
| Nov 4 | −1,720.00 | −5,160.00 | −3,440.00 | −8,600.00 |
| Nov 5 | +2,480.00 | −2,680.00 | +2,480.00 | −6,120.00 |
| Nov 6 | +2,480.00 | −200.00 | +2,480.00 | −3,640.00 |
| Nov 9 | −1,720.00 | −1,920.00 | −1,720.00 | −5,360.00 |
| Nov 11 | +2,480.00 | +560.00 | +4,960.00 | −400.00 |
| Nov 12 | +2,480.00 | **+3,040.00** | +760.00 | **+360.00** |
| Nov 13 | 0.00 (no trade in any of the three logs at build time) | +3,040.00 | 0.00 | +360.00 |

Shape: a degradative first week (four straight stops across the two books) then a progressive second week — both lines end positive, the pre-registered line at **+₹3,040.00** (₹338/day over 9 days). This is the same two NS1 wins (+₹2,480 × 2, Nov 11–12) the owner pointed at, plus the Skill book's Nov 5–6 targets.

## 1.6 BANK VERDICT

- **Best passing Bank configuration: the B2/NS1 legacy frame ALONE** — +₹83,650.50 Jan–Oct, **₹408.05/day**, gate PASS on every leg. 42 of 205 days (20.5%) reach ≥ ₹2,000 on Bank alone; 27 days land in the ₹2,000–3,000 zone, 15 days above it.
- **The three-system assembly FAILS.** Skill and Volrix earn when the frame's admission selects their keys (+₹25,659 of in-frame value); their outside-the-frame legs lose −₹23,983 and fail the placebo at the 0.1 percentile. Layering them on as independent books makes Bank worse, in backtest and (Nov 3–4, identical-leg line) in November too.
- **Gap to the bar:** Bank's ₹408/day is 20% of the ₹2,000 zone floor — a gap of **₹1,592/day** that Bank alone does not close. No new Bank configuration passes, so **no Monday paper-run wiring is proposed for Bank** (the legacy frame already runs under the settlement as the control line; nothing new to start).
- Trade lists: `daily_earner_bank_janoct_trades.csv` (127 assembly legs, stream-labelled) · `daily_earner_bank_november_trades.csv` (14 logged rows, duplicate flags under both rules).

---

# MILESTONE 2 — NIFTY

## 2.1 Pre-registration (written before any assembly total was computed)

**Streams (all premium basis, per 1 lot of 65, ₹220/trade inside nets):**
- **FRAME (the legacy construction, Nifty form):** the DEC-S1 stored leg set, `nifty_next_phase_trades.csv` — 97 legs, independently re-summed in this run before use: **+₹91,168.50** (matches the adoption record exactly). Components: A (35 legs — the confirmed U1 frame keys; this is the frame's BASE-equivalent), B (49 — gap fades), C (13 — weekly-expiry sleeve), all under the frame's frozen S5 geometry. This is the exact analog of Bank's v21 frame ledger: the frame's own scored ledger, distinct from the G0 pool. **Frame-equivalent forms, gated as singles in the fallback ladder:** TUNED v1 (frame minus Component B PE legs — 74 legs; derived in-run from the same stored set and re-summed: **+₹103,050.25**, matching its EVE-07 gate record) and TUNED v2 (v1 minus A CE and C CE — 59 legs; derived and re-summed: **+₹115,950.75**, matching EVE-11). Both are drop-only filters on this frame with gate PASSes already on record (2026-11-04 / 2026-11-05); they are this segment's tuned frame forms, not separate systems.
- **SKILL (standalone increment):** Skill V3 keys from the premium-scored N1 pool, `historical_proof_nifty_N1_trades.csv` (108 legs, all COMPUTED, re-summed in this run: **+₹25,159.00** — the published U1-N1 premium-only total). Skill stream = pool legs whose `source_systems` include "Skill V3" (99 legs), G0 geometry (stop −50 / target +90 / SQ 15:10, entry = entry-bar open) — the stored Skill population, same construction as Bank's §1.1.
- **VOLRIX (standalone increment):** Volrix (b) −1.0% legs from the same pool file (8 legs). Pre-scoring validation: every Volrix pool leg is a 09:20 CE entry co-sourced with Skill V3 (in the N1 pool the (b) keys are a subset of the Skill keys), and the October leg reproduces the published standalone October score exactly (2026-10-09, +₹5,630.00, target — `volrix_october_2026-11-05.md`: "(b) Nifty: 1 trade, +₹5,630 — reproduced exactly"). The pool scoring (G0) is identical to variant (b)'s frozen exit geometry, so these stored legs ARE the standalone (b) stream.

**Assembly:** Nifty book = FRAME (all 97 legs) + SKILL pool legs whose key is not in the frame's BASE + VOLRIX pool legs whose key is not in the frame's BASE.
**Dedupe:** key = (date, direction). The pool holds exactly one key per (date, direction) (verified 108/108). A pool leg is dropped if the frame's **Component A** holds a leg with the same (date, direction) — A is the frame's BASE-equivalent (all 35 A keys are pool keys, verified in-run), exactly as Bank deduped against the v21 BASE family only. The frame's instance survives. **Pre-registered disclosure:** this frame also holds B/C sleeve legs on (date, direction) keys A does not hold; pool legs colliding only with a B or C key are NOT dropped under the primary rule — a sensitivity line deduping against ALL frame components is reported alongside (the same two-rule disclosure Bank's November section used). Pool legs are single rows, so a Skill+Volrix co-sourced key enters once, labelled with both sources.
**Costs:** ₹220/trade already inside every stored net; no second cost is applied.

**Gate (all legs must pass; bars identical to Bank §1.1, fixed here before totals):**
- G1 Total: assembly net > 0, and assembly net > frame alone (the layer must add, not dilute).
- G2 Halves: Jan–May ≥ 0 AND Jun–Oct ≥ 0.
- G3 Ex-top-3: assembly total minus its 3 best legs > 0.
- G4 Placebos: (a) random-skip — 1,000 draws of random same-size subsets of the 108 pool legs; the increment must exceed the draws' 90th percentile. (b) delay-1-day — increment legs shifted one trading day (timing-luck check, descriptive).
- G5 Consistency (owner's test): red months ≤ 3 of 10 AND best single month ≤ 50% of the Jan–Oct total AND worst month reported by name.
- G6 Timing audit: every stream is a previously audited causal ledger (DEC-S1 leg set = the frozen next-phase re-score, matched 16/16 fields at adoption; N1 pool = entry-bar-open premium scoring of causally generated keys; Volrix trigger uses prev-day close only). Assembly introduces no new timing.
- G7 NC: NOT_COMPUTED legs = 0 in all streams.

**Fallback ladder (gated in this order if the full assembly fails):** A1 frame+Skill · A2 frame+Volrix · A3 Skill+Volrix (no frame) · singles: B1 frame alone (DEC-S1) · B1a TUNED v1 · B1b TUNED v2 · B2 Skill alone · B3 Volrix alone. For singles, the "adds over frame" half of G1 and the increment placebo do not apply (as with Bank's B1); every other leg applies unchanged.

**November check (Nov 2–13, 9 trading days; Nov 10 = Diwali holiday):** FRAME from `november_shadow_decs1_nifty_log.csv` (the DEC-S1 construction's scored November shadow — the frame's live November record); SKILL from `november_shadow_skill_nifty_log.csv`; VOLRIX from the frozen live record — the primary log's daily trigger notes record no trigger on any November day (prev-day changes +0.51 / +1.68 / +1.58 / +0.63 / +2.40 / −0.18 / +0.23 / +0.84, all > −1.0%), the Nov 13 trigger (Nov 12 close change, +0.18% from the verified closes 25,255.05 → 25,299.35) also does not fire, and the 10-session cooldown from the last (b) entry (2026-10-09) expired in October — so Volrix's November line is zero fires by record, not missing data. Deduped on the same (date, direction) rule, frame instance surviving; the identical-leg line is also reported. **Streams that merely ran in November and are NOT in this assembly:** NF-PAPER-C3G7 primary (its own Jan–Oct was never scored — not auditable, so it cannot be a stream here; November: 1 trade, −₹3,470.00) and TUNED v1's forward shadow (+₹3,036.50 · 1 leg — v1's November line is the frame log minus its B PE legs by its defining drop rule, stated for reference in §2.5).

## 2.2 The three Nifty streams, as stored (Jan–Oct 2026, premium, 1 lot)

| Stream | Legs | Jan–Oct net | Avg / trading day (205 days) |
|---|---|---|---|
| FRAME — DEC-S1 stored set (A 35 + B 49 + C 13) | 97 | **+₹91,168.50** | ₹444.72 |
| SKILL — Skill V3 standalone (stored pool population) | 99 | +₹17,135.50 | ₹83.59 |
| VOLRIX — (b) intraday −1.0% | 8 | +₹5,178.75 | ₹25.26 |

- **The same structural finding as Bank, sharper.** Of the 99 pool legs carrying a Skill and/or Volrix source, 28 sit on keys the frame's Component A also took (dropped from the increment as duplicates) — under G0 scoring those 28 legs are worth **+₹30,831.50**. The legs Skill/Volrix take *outside* the frame's admission are the increment below — and they lose. In this pool the frame's admission captures more value (+₹30,831.50) than the entire standalone Skill stream nets (+₹17,135.50).
- Volrix stream detail: all 8 legs are 09:20 CE entries co-sourced with Skill V3 (the (b) keys are a subset of the Skill keys in the N1 pool — there is no Volrix-only population here); 3 targets (+₹5,630), 4 stops (−₹3,470), 1 square-off (+₹1,411.50) and 1 square-off (−₹2,712.75). An occasional overlay, exactly as its October report concluded. Only ONE Volrix key sits outside the frame's A admission: 2026-10-09, the +₹5,630 October target itself.
- Skill stream shape: its ex-top-3 is +₹245.50 — the standalone Skill book's entire Jan–Oct profit rests on its 3 best legs, and April alone is 75.8% of its total (see the fallback table).

## 2.3 The full assembly — GATE FAIL

Assembly = 97 frame legs + 71 increment legs (70 Skill-only, 1 Skill+Volrix — the Oct 9 Volrix target; there are no Volrix-only increment legs) = **168 legs, +₹77,472.50**. The increment is **−₹13,696.00** (Skill-only legs −₹19,326.00, the one co-sourced Volrix leg +₹5,630.00).

| Gate leg | Bar | Result | Verdict |
|---|---|---|---|
| G1 total + adds over frame | > 0 and > ₹91,168.50 | +₹77,472.50 | **FAIL** (dilutes the frame by ₹13,696) |
| G2 halves | both ≥ 0 | H1 +₹37,746.75 / H2 +₹39,725.75 | pass |
| G3 ex-top-3 | > 0 | +₹44,007.50 | pass |
| G4 random-subset placebo | increment above p90 of random 71-leg pool subsets | increment −₹13,696 vs p50 +₹17,268 / p90 +₹40,885 → **5.6th percentile** | **FAIL** (random legs beat the selected increment) |
| G5 consistency | red months ≤ 3, best month ≤ 50% | red months **3** (Mar, May, Jul); best month Apr = 44.3% | pass (at the red-month bar) |
| G6 timing | audited ledgers only | all streams previously audited causal ledgers; assembly adds no new timing | pass |
| G7 NC | 0 | 0 | pass |

Month table (₹):

| Month | Frame (DEC-S1) | Full assembly |
|---|---|---|
| Jan | +19,211.25 | +12,222.00 |
| Feb | +5,038.75 | +2,610.50 |
| Mar | −11,846.50 | −11,236.00 |
| Apr | +28,416.00 | +34,356.25 |
| May | +4,574.00 | −206.00 |
| Jun | −1,331.00 | +5,574.75 |
| Jul | +5,839.00 | −5,810.75 |
| Aug | +841.25 | +3,336.50 |
| Sep | +20,265.25 | +21,244.75 |
| Oct | +20,160.50 | +15,380.50 |

Worst month (assembly): **March, −₹11,236.00**. Delay-1-day timing check (descriptive): shifting the increment legs one trading day later leaves the ≥₹2,000-day count at 42 vs 40 actual — the failure is not a timing artefact. Sensitivity (pre-registered disclosure): deduping against ALL frame components instead of A alone shrinks the increment to 48 legs / −₹24,645.50 and the assembly to +₹66,523.00 — worse under the stricter rule too. Time-overlap diagnostic: 28 of the 71 increment legs overlap a frame leg's holding window on the same day — on those days the assembly's day-net sums two co-held legs (frame leg under S5 geometry, pool leg under G0), each net taken from its own audited ledger; the co-holding is intrinsic to running the two books in parallel and is disclosed here, not adjusted.

## 2.4 Fallbacks, gated in order

| Config | Legs | Total | Halves | Ex-top-3 | Red months | Placebo (increment) | Gate |
|---|---|---|---|---|---|---|---|
| A1 Frame+Skill | 168 | +₹77,472.50 | +37,746.75 / +39,725.75 | +₹44,007.50 | 3 | −₹13,696, 5.2 pct | **FAIL** (G1, G4) — identical to FULL: the only Volrix increment leg is Skill-co-sourced, so A1 and FULL are the same book |
| A2 Frame+Volrix | 98 | +₹96,798.50 | +45,393.50 / +51,405.00 | +₹63,333.50 | 1 | 1 leg +₹5,630 = p90 exactly (75.6 pct) | **FAIL** (G4 — the increment *equals* the 90th percentile of random 1-leg draws; the pre-registered bar is to *exceed* it. The entire A2 edge is one leg — the 2026-10-09 target) |
| A3 Skill+Volrix (no frame) | 99 | +₹17,135.50 | +11,145.50 / +5,990.00 | +₹245.50 | 2 | — | **FAIL** (G5 — best month Apr = 75.8% of total: one-month-carried) |
| **B1 Frame alone (DEC-S1)** | **97** | **+₹91,168.50** | **+45,393.50 / +45,775.00** | **+₹57,703.50** | **2** (Mar −11,846.50, Jun −1,331.00) | n/a (frozen audited book) | **PASS — every leg** |
| **B1a TUNED v1** | **74** | **+₹103,050.25** | **+52,319.25 / +50,731.00** | **+₹69,585.25** | **1** (Mar −1,216.50) | n/a (drop-only filter; EVE-07 gate PASS on record) | **PASS — every leg** |
| **B1b TUNED v2** | **59** | **+₹115,950.75** | **+67,064.25 / +48,886.50** | **+₹82,485.75** | **0** | n/a (drop-only filter; EVE-11 gate PASS on record) | **PASS — every leg** |
| B2 Skill alone | 99 | +₹17,135.50 | +11,145.50 / +5,990.00 | +₹245.50 | 2 | — | **FAIL** (G5 — best month 75.8%; identical book to A3) |
| B3 Volrix alone | 8 | +₹5,178.75 | −3,368.50 / +8,547.25 | −₹11,711.25 | 2 | — | **FAIL** (G2, G3, G5 — best month = 108.7% of total) |

## 2.5 November 2–13 — day-by-day (Nifty)

Parts: FRAME (DEC-S1 shadow) **−₹443.50 · 5 trades** · SKILL shadow **−₹2,966.75 · 7 trades** · VOLRIX **no fires** — verified from the frozen live record (the primary log's daily trigger notes: prev-day changes +0.51 / +1.68 / +1.58 / +0.63 / +2.40 / −0.18 / +0.23 / +0.84 for Nov 2–12, all > −1.0%; the Nov 13 trigger, Nov 12's close change +0.18% from the verified closes 25,255.05 → 25,299.35, also does not fire; the cooldown from the 9 Oct entry expired in October). A rebound system cannot fire into a rising tape; that is zero trades, not missing data.

No Skill-shadow leg shares a (date, direction) with a frame leg in this window (the Nov 9 Skill PE is the leg the primary took and the frame did not; Nov 2/11 pairs are opposite directions), so the pre-registered and identical-leg dedupe lines are the SAME line here — both are reported in the trade CSV and they coincide:

| Day | Assembly (both dedupe rules) | Cumulative |
|---|---|---|
| Nov 2 | −3,690.00 | −3,690.00 |
| Nov 3 | −433.50 | −4,123.50 |
| Nov 4 | 0.00 | −4,123.50 |
| Nov 5 | +1,724.50 | −2,399.00 |
| Nov 6 | +3,030.00 | +631.00 |
| Nov 9 | −3,470.00 | −2,839.00 |
| Nov 11 | +210.00 | −2,629.00 |
| Nov 12 | −3,470.00 | **−6,099.00** |
| Nov 13 | 0.00 (no trade in either log at build time) | −6,099.00 |

Shape: **degradative.** The assembly ends **−₹6,099.00** (−₹678/day over 9 days) — worse than the frame alone (−₹443.50) because Skill's November stops sit outside the frame, the same failure as Jan–Oct in miniature. For reference, the streams that merely ran: **TUNED v1 forward +₹3,036.50 · 1 leg** (the frame log minus its B PE legs — November's only positive Nifty line, positive precisely because the leak class is removed) and the C3G7 primary **−₹3,470.00 · 1 trade** (Nov 9; the same leg as Skill's Nov 9 PE — the primary and the Skill shadow took it, the frame did not).

## 2.6 NIFTY VERDICT

- **Best passing Nifty configuration: TUNED v2** — +₹115,950.75 Jan–Oct, **₹565.61/day**, gate PASS on every leg in this run (and EVE-09/10/11 PASSes on record), **zero red months** (worst month Aug, +₹1,911.75). TUNED v1 also passes every leg (+₹103,050.25, ₹502.68/day, 1 red month) and is the settlement's standing book; the frame alone (DEC-S1) passes too (+₹91,168.50, ₹444.72/day) but stands retired as a standalone December candidate since 2026-11-13 — it is a control line, and this build does not un-retire it.
- **The three-system assembly FAILS on Nifty exactly as on Bank.** Skill and Volrix earn when the frame's admission selects their keys (+₹30,831.50 of in-frame G0 value); their outside-the-frame legs lose −₹13,696 and sit at the 5.6th percentile of random subsets. Layering them on as independent books makes Nifty worse in backtest and in November (−₹6,099 assembled vs +₹3,036.50 for the frame's tuned form).
- **Gap to the bar:** Nifty's best passing ₹565.61/day is 28% of the ₹2,000 zone floor — a gap of **₹1,434.39/day** that Nifty alone does not close. (v1: gap ₹1,497.32/day; frame: ₹1,555.28/day.)
- One structural note for the owner: on Nifty the ₹2,000–3,000 zone is nearly empty by construction — leg sizes are ±₹3,470 / +₹5,630, so a one-target day lands at +₹3,470 or +₹5,630, above the zone (TUNED v2: 26 days ≥ ₹2,000, of which only 2 in the zone and 24 above it). The zone fills only when segments combine (§4).
- Trade lists: `daily_earner_nifty_janoct_trades.csv` (168 assembly legs, stream-labelled) · `daily_earner_nifty_november_trades.csv` (12 logged rows, duplicate flags under both rules).

---

# MILESTONE 3 — STOCKS (verification only — no new book; the Stock Book runs as-is under the settlement)

**Sources (existing verified ledgers only):** the adopted Variant C book dumps — `stocks_engine_adoptedC_book2026_trades.csv`, re-summed in this run before use: **1,363 trades, +₹247,178.79** (matches the adoption record and freeze exactly) — and the November forward paper log `stocks_sarvaritu_paper_log.csv` (30 trades, **+₹7,965.74**, re-summed exact). Basis: equity cash, provisional per 100 shares, ₹40/trade inside nets — the Book's own basis, never mixed with index premium figures. Recorded qualification, not dropped: components (c)/(e) of the adoption gate stand FAILED-AND-WAIVED against the pre-adoption baseline (owner's direction, 2026-11-02); the book's own birth gate (R9-04) passed all ten legs.

## 3.1 Jan–Oct 2026 — ₹/day distribution and consistency

| Measure | Stock Book |
|---|---|
| Total | **+₹247,178.79** · 1,363 trades · win rate 44.8% |
| Average / trading day (205) | **₹1,205.75** |
| Average / active day (181 days with trades) | ₹1,365.63 |
| Days ≥ ₹2,000 | 57 of 205 (27.8%) — 16 in the ₹2,000–3,000 zone, 41 above it |
| Positive days | 110 of 205 (53.7%) |
| Red months | **0 of 10** — every month green |
| Ex-top-3 trades | +₹228,933.24 (the freeze's harsher ex-top-3-*stocks* cut: +₹55,557.16 — also positive) |

Month table (₹): Jan +28,021.10 · Feb +12,576.14 · Mar +18,225.72 · Apr +46,744.31 · May +43,842.74 · Jun **+6,756.75 (worst — still green)** · Jul +10,284.46 · Aug +10,106.06 · Sep +14,494.14 · Oct +56,127.37 (best).

Consistency verdict: this is the most consistent of the three segments — no red month in 2026, and it earns by payoff asymmetry (44.8% win rate), not by hit rate. Context, labelled as the other year: Jan–Oct **2025** (same adopted book) = +₹119,813.44 · 1,064 trades — positive but at ₹11,981.34/month, below the ₹15,000 floor pace; the floor is met on 2026, not on 2025 (the recorded standing, unchanged).

## 3.2 November 2–13 — day-by-day (Stock Book forward paper)

| Day | Net (₹) | Cumulative |
|---|---|---|
| Nov 2 | +1,455.27 | +1,455.27 |
| Nov 3 | −451.85 | +1,003.42 |
| Nov 4 | −420.94 | +582.48 |
| Nov 5 | −299.28 | +283.20 |
| Nov 6 | +6,577.68 | +6,860.88 |
| Nov 9 | +704.30 | +7,565.18 |
| Nov 11 | +826.10 | +8,391.28 |
| Nov 12 | −425.54 | **+7,965.74** |
| Nov 13 | not yet in the EOD log at build time (lands 16:35) | +7,965.74 |

Shape: four small degradative days, one strong day (Nov 6) that carries the month, then a grind near the high — ends at **+₹7,965.74**, ₹995.72/day over the 8 scored days. Progressive in outcome (it ends near its cumulative high), single-day-dependent in composition.

## 3.3 The early Skill-on-stocks streams — standing

They exist and their only scored window is on record: the October 2026 clubbed run over the same 25 stocks (18 days, cash provisional basis, `daytrader_stocks_october_run.md`) — Day Trader Skill entries alone: 450 trades, **−₹33,527** (win rate 32.0%, expectancy −₹74.50/trade); the portfolio-capped form (max 3 trades/week) was +₹160 — flat, not a profit. The Skill's entries on stocks lost money at full density and added nothing when capped, so no Skill-on-stocks stream was ever adopted into the Stock Book (whose seven components are its own: F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND) and no Jan–Oct Skill-on-stocks ledger exists to assemble. There is nothing to add here — Milestone 3 stays verification-only, as ordered.

## 3.4 STOCKS VERDICT

The Stock Book alone averages **₹1,205.75/day** — 60% of the ₹2,000 zone floor (gap ₹794.25/day), with the strongest consistency of the three segments (0 red months) and a green November forward line. It is the largest single contributor to the combined picture in §4.

---

# §4 — COMBINED DAILY PICTURE (arithmetic totals against the owner's bar)

**Construction:** the passing book of each segment, day lines summed by date — Bank: legacy frame alone (Milestone 1, B1 PASS) · Nifty: TUNED v2 (Milestone 2, best passing single; the TUNED v1 line is computed alongside because v1 is the settlement's standing book) · Stocks: Stock Book as-is. Each segment's own numbers stay visible in §§1–3; the combined figure below is an **arithmetic total for the owner's bar only — never a merged verdict on any segment.**

## 4.1 Jan–Oct 2026 — the three passing books together

| Segment book | Jan–Oct total | Avg / day | Days ≥ ₹2,000 |
|---|---|---|---|
| Bank — legacy frame (B1) | +₹83,650.50 | ₹408.05 | 42 / 205 (20.5%) |
| Nifty — TUNED v2 (B1b) | +₹115,950.75 | ₹565.61 | 26 / 205 (12.7%) |
| Stocks — Stock Book | +₹247,178.79 | ₹1,205.75 | 57 / 205 (27.8%) |
| **COMBINED (v2 line)** | **+₹446,780.04** | **₹2,179.41** | **81 / 205 (39.5%)** |
| COMBINED (v1 line, for reference) | +₹433,879.54 | ₹2,116.49 | 76 / 205 (37.1%) |

- **The combined average sits INSIDE the owner's ₹2,000–3,000 zone**: ₹2,179.41/day on the v2 line, ₹2,116.49/day on the v1 line. Segment averages sum exactly to the combined figure (408.05 + 565.61 + 1,205.75 = 2,179.41) — the arithmetic is the segments, nothing else.
- Day distribution (v2 line): 26 days land in the ₹2,000–3,000 zone itself, 55 days finish **above** ₹3,000 (36 of them ≥ ₹5,000 — the owner's "God's gift" territory), 119 of 205 days positive (58.0%). Worst combined day −₹8,710.96; best +₹25,952.00.
- **The honest limit, stated plainly:** the *average* is in the zone, but the bar as a daily experience — ₹2,000 on the day — is reached on **39.5% of days**, roughly 2 days in 5. The three books fire on different days (Bank 20.5% of days, Nifty 12.7%, Stocks 27.8% reach ₹2,000 alone), so the combined line is carried by whichever segment fires, not by a steady ₹2,000 engine. That is what the gated evidence supports; no assembly of the three early systems changes it — on both indices the assembly *reduced* the total.

## 4.2 November 2–13 — combined day-by-day (the passing books' forward lines)

Bank = legacy frame's own November log · Nifty = TUNED v2 (its drop rule applied to the DEC-S1 shadow log: **0 legs survive in November** — every DEC-S1 November leg was a B PE or C CE leg, both classes v2 excludes) · Stocks = Stock Book paper log (final through Nov 12; Nov 13 lands 16:35).

| Day | Bank legacy | Nifty TUNED v2 | Stocks | Day total | Cumulative |
|---|---|---|---|---|---|
| Nov 2 | −1,720.00 | 0.00 | +1,455.27 | −264.73 | −264.73 |
| Nov 3 | −1,720.00 | 0.00 | −451.85 | −2,171.85 | −2,436.58 |
| Nov 4 | −1,720.00 | 0.00 | −420.94 | −2,140.94 | −4,577.52 |
| Nov 5 | 0.00 | 0.00 | −299.28 | −299.28 | −4,876.80 |
| Nov 6 | 0.00 | 0.00 | +6,577.68 | +6,577.68 | +1,700.88 |
| Nov 9 | −1,720.00 | 0.00 | +704.30 | −1,015.70 | +685.18 |
| Nov 11 | +2,480.00 | 0.00 | +826.10 | +3,306.10 | +3,991.28 |
| Nov 12 | +2,480.00 | 0.00 | −425.54 | +2,054.46 | **+6,045.74** |
| Nov 13 | 0.00 | 0.00 | pending EOD | 0.00 | +6,045.74 |

**Shape, stated plainly: degradative for four days, then progressive — and positive at the end.** The combined line bottoms at −₹4,876.80 on Nov 5 and recovers to **+₹6,045.74** by Nov 12 (₹672/day over the 9 days) on the Stocks Nov 6 day and the Bank NS1 wins of Nov 11–12. On the TUNED v1 line instead (v1 keeps the Nov 3 C CE leg, +₹3,036.50), the same table ends at **+₹9,082.24** (₹1,009/day). Either way November runs **below the bar's pace** — positive, recovering, but not a ₹2,000/day month so far. November's combined shape is the owner's two observations made exact: October and the last eight months are green; this month is a grind that the books are climbing out of, not a collapse — and not yet the daily earner he asked for.

## 4.3 Monday paper-run wiring spec (PREPARED ONLY — nothing is started by this build)

No new trading configuration is wired. Every three-system assembly and pair on both indices FAILED the gate (§§1.3–1.4, 2.3–2.4); starting any of them on Monday would contradict the gate. The passing configurations already run under the 2026-11-13 settlement (Bank legacy = control line; Nifty TUNED v1 = standing book; TUNED v2 = running shadow; DEC-S1 = control line; Stock Book = forward paper). What CAN start Monday without any new trading logic is a **reporting line**:

- **Name:** DAILY EARNER — combined reporting line (reporting only; places no trades, changes no book).
- **Inputs (existing logs only):** Bank — `november_paper_bank_log.csv` PRIMARY-channel legacy rows; Nifty — `november_shadow_decs1_nifty_log.csv` filtered by the TUNED drop rule (v1 line and v2 line both computable from the same log); Stocks — `stocks_sarvaritu_paper_log.csv`.
- **Dedupe:** none needed — the three books trade different instruments; no leg can appear in two logs. Segment lines are always printed separately above the combined line; the combined figure is labelled arithmetic-only.
- **Output:** with the existing daily stats — each segment's day net and MTD, then the combined day net and MTD against the ₹2,000–3,000/day bar (days in zone / above / below counted).
- **The one owner decision flagged, not enacted:** the Nifty reporting lead — **v1** (the standing book; lower gated pace ₹502.68/day, 1 red month, but November's only positive Nifty forward line, +₹3,036.50) vs **v2** (higher gated pace ₹565.61/day, zero red months, but 0 November legs — its edge classes did not fire this month). The settlement made v1 the standing book; this build's gate makes v2 the best passing configuration. Both keep scoring either way; the lead line changes only on the owner's word.

## 4.4 BOTTOM LINE

- **Bank:** assembly FAIL · best passing = legacy frame alone, ₹408.05/day.
- **Nifty:** assembly FAIL · best passing = TUNED v2, ₹565.61/day (TUNED v1 also passes, ₹502.68/day, and holds November's only positive Nifty forward line).
- **Stocks:** Stock Book verified as-is, ₹1,205.75/day, 0 red months, November +₹7,965.74.
- **Combined:** Jan–Oct average **₹2,179.41/day — inside the owner's ₹2,000–3,000 zone** — reached as a daily outcome on 39.5% of days. November to date: **+₹6,045.74** (v2 line) / **+₹9,082.24** (v1 line) — positive and recovering, below the bar's pace.
- The three early systems were never three independent earners: on both indices, Skill and Volrix make their money **inside** the frame's admission and lose outside it (−₹23,983 Bank increment; −₹13,696 Nifty increment; both below the 6th percentile of random subsets). The daily earner the evidence supports is the frames themselves, running as they already run — plus the Stock Book — reported as one combined line from Monday, if the owner wants it.

*End of build report. Evidence: `daily_earner_bank_build.py` / `daily_earner_bank_build2.py` / `daily_earner_bank_final.py` / `daily_earner_nifty_build.py` / `daily_earner_stocks_combined.py`; results `daily_earner_bank_results.json` / `daily_earner_bank_results2.json` / `daily_earner_nifty_results.json` / `daily_earner_combined_results.json`; trade lists `daily_earner_bank_janoct_trades.csv` / `daily_earner_bank_november_trades.csv` / `daily_earner_nifty_janoct_trades.csv` / `daily_earner_nifty_november_trades.csv`.*
