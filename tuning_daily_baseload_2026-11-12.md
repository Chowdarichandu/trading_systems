# DAILY BASE-LOAD FALLBACK — Tuning Programme, 2026-11-12

Owner directive 2026-11-12 20:23 IST ("Tune it — something is missing").
Paper only, real ₹0. December candidates only; frozen November primaries untouched.
Computation: `tuning_daily_baseload_2026-11-12.py` (Jan–Oct, stages `bank` / `nifty`) +
`tuning_daily_baseload_2026-11-12_nov.py` (November counterfactual) →
`tuning_daily_baseload_2026-11-12_{bank,nifty}_results.json`, `_nov_results.json`,
`_bank_trades.csv` / `_nifty_trades.csv` (both empty — see verdicts), `_nov_trades.csv` (empty).

## Verdicts (both FAIL — the variant is vacuous, not merely weak)

| Variant | Incumbent | Fallback legs generated | Combined | Gate |
|---|---|---|---|---|
| BANK — TUNED STACK v2 + fallback | +₹127,351.50 / 111 legs, 89 traded days (8.9/mo) | **0** | +₹127,351.50 (identical) | FAIL (G1, G4a, G4b, G5) |
| NIFTY — TUNED v1 + fallback | +₹103,050.25 / 74 legs, 66 traded days (6.6/mo) | **0** | +₹103,050.25 (identical) | FAIL (G1, G4a, G4b, G5) |

The fallback never fires — not because its legs lose, but because **the population it
harvests does not exist**. This route is closed.

## Frozen spec (fixed before scoring)

Trigger 13:30. On a day where the incumbent has taken no leg by 13:30, take the day's
first causal U1-system signal at/after 13:30 (systems: (lA) v2, V5 v2, Skill V3,
Volrix (b); per-(date, direction) earliest signal per system — the workspace sysmap),
one leg, either direction, both-directions-at-the-same-bar = no leg; an incumbent leg
entering at/before the fallback signal wins the afternoon (race rule, never duplicate,
never displace). Contract atm100 at the signal bar, monthly expiry; Bank exits sim_g0
(−50/+90, SQ 15:10, lot 30), Nifty exits TUNED v1 geometry (STANDING_GEOM, lot 65);
₹220/trade. Gate (pre-registered): combined beats incumbent on total, no new red month,
ex-top-3 not worse, beats delay-6 and random-time placebos, traded-day rate ≥ incumbent
+ 2.0/month; hygiene NC = 0, sysmap re-derivation exact, entry/truncation audits clean,
re-sum exact.

## The evidence — the U1 systems emit no afternoon first-signals

Signal census, Jan–Oct 2026 (sysmap = each system's FIRST signal per direction per day):

| Index | System-signals total | First-signals ≥ 13:30 | First-signals in [13:30, 15:05] |
|---|---|---|---|
| BANKNIFTY | 255 | **1** | 1 |
| NIFTY | 254 | **0** | 0 |

- Bank's single afternoon first-signal in ten months: **2026-07-16, (lA) v2 PE at 13:30** —
  and that day the stack had already taken legs at 10:30 and 13:20, so the day was
  ineligible anyway. Bank had **118 eligible days** (of 205) and the fallback fired on none.
- Nifty had ~139 days with no v1 leg by 13:30 and **zero** afternoon first-signals to take.
- This is structural, not a sampling miss: all four systems are morning constructions —
  (lA) and Skill rescan windows close at 13:30, V5's candidates are morning OR-based,
  Volrix (b) is a prior-day trigger worked in the morning. A system's *first* signal of
  the day in a direction is a morning event by design. (Verified against the raw source
  CSVs directly, not just the sysmap: Bank raw rows ≥ 13:30 across all five source
  files = 1.)
- November corroborates exactly: across Nov 2–12 (8 trading days × 2 indices) the
  producer emitted 16 system-signals, **0 at/after 13:30**.

Gate detail (both variants): G1 FAIL (combined total = incumbent, not above), G2 PASS
(no new red month — combined is the incumbent), G3 PASS (ex-top-3 equal, not worse),
G4a/G4b FAIL (placebo books are the same incumbent book; a zero-leg layer cannot beat
its placebos), G5 FAIL (traded-day rate unchanged: Bank 8.9/mo, Nifty 6.6/mo).

## November counterfactuals (Nov 2–12, from real candles/producer signals)

- **BANK stack:** eligible idle days Nov 2, 3, 5, 6, 11 — no U1 signal ≥ 13:30 on any of
  them → **0 fallback legs**. Counterfactual = recorded book **−₹960** (live-only
  framing **−₹1,720**) — unchanged.
- **NIFTY TUNED v1:** eligible idle days Nov 2, 4, 5, 6, 9, 11, 12 — no U1 signal
  ≥ 13:30 on any of them → **0 fallback legs**. Counterfactual = **+₹3,036.50** — unchanged.

## Audits (all clean)

- Anchors reproduced before any variant scoring: Bank eve19 leg set asserted
  (111 legs, Σ = +₹127,351.50); Nifty TUNED v1 assembly asserted (+₹103,050.25 / 74).
- Nifty premium loader cross-validated: 74/74 incumbent legs reproduced leg-for-leg
  through the fallback scoring path.
- Sysmap re-derivation (independent pandas implementation, Family B pattern) reproduces
  both fallback leg sets exactly (both empty). Entry audit 0 violations; truncation
  spot-proof 0 violations; independent re-sums exact; NC = 0.
- November signal reconstruction cross-validated: 15/15 real Skill V3 legs (both
  indices, Nov 2–12) match the shadow Skill logs exactly, and 4/4 sysmaps recorded in
  the DEC-S1 log's no-trade notes match.
- Bank sysmap disclosure: built by mirroring `build_sysmap` to BANKNIFTY from the same
  five source files with the same October merge rules, minus the NIFTY-only Volrix
  merge hardcode (2026-10-09) — no Bank analogue exists in any stored source, so Bank
  October Volrix (b) is absent from the map (the NIFTY map's October Volrix rests on
  that single hardcode). Immaterial here: October contributes no afternoon signals
  under any reading.

## What this closes — and what the missing layer would actually require

The owner's diagnosis is right (the books idle) but this construction cannot fill the
gap: **a fallback keyed to U1 first-signals has nothing to key to after 13:30.** Two
honest consequences:

1. An afternoon base-load would need the detectors re-run inside a new afternoon
   window — that is a *new system*, not a layer on the U1 books, and it would enter the
   invention queue as such. Expectations should be set by the record: afternoon-entry
   constructions on Bank have now been rejected in five distinct forms (break-capture
   R/H, EVE-12-class routes, BANK-APC pullback-continuation, and the expiry-window
   family on Nifty). Nothing in this programme changes that record.
2. The only daily-frequency index mechanism that exists today is the premium-selling
   SHORT-FOLLOW (gate-passed +₹49,149.25 Jan–Oct; its arming is an owner decision,
   outside this programme). The long-premium signal books remain event books:
   Bank 8.9 traded days/month, Nifty 6.6 — that is their proven shape, and no
   rule layered on their own signals changes it.
