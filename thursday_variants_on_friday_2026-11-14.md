# THURSDAY'S TESTS ON YESTERDAY — 2026-11-14

Owner order 2026-11-14 08:32 IST: "run the same which was run Thursday on
yesterday." Thursday = 2026-11-12 (the three segment tuning programmes +
the repair programme). Yesterday = Friday 2026-11-13. Every variant below
is replayed under its EXACT Thursday definition (same code paths:
`tuning_bank_2026-11-12.py` transforms / `replay_mod` / locked ladder via
the November helper, extended one day; repair-programme drop-only rules;
the Stock Book's own shadow rules as recorded in Thursday's T-S3 pack).
Descriptive counterfactual only — no book, ledger or job was changed.
November sets no rule. Paper only, real money ₹0.

## CONTROLS — actuals reproduced BEFORE any variant number

- **Bank:** the identity variant of Thursday's own November helper,
  re-run over Nov 2–13, reproduces `november_shadow_stack_bank_log.csv`
  leg-for-leg on all 9 days (per-day assertion in-run) and the window
  total **−₹2,680.00**; yesterday's leg is reproduced exactly: NS3 PE
  60800, in 12:20 @705.00, stop 12:20 @655.00, **−₹1,720.00** ✓
- **Stocks:** the two logged Nov 13 rows sum to the logged day net
  (−₹447.80), and both were candle-verified by the day's own engine
  (`stocks_eve_2026-11-13.py`, to within ₹0.20) ✓
- **Nifty:** the DEC-S1 shadow log carries an explicit no-trade row for
  2026-11-13 and the C3G7 primary log a no-trade row — zero legs in
  every population Thursday's variants act on (verified, §3) ✓

---

## 1. BANK — yesterday: ONE stack leg (legacy frame: no trade)

Leg: **NS3_gapclass PE 60800, entry 12:20 @705.00** (expiry 2026-11-23,
1 lot of 30, ₹220). Incumbent geometry (NS3 P21): stop −50 / trig +90 /
lock +50 / tgt2 +150. The 12:20 entry bar's low crossed the −40, −50
AND −60 premium levels; its premium close was 653.50.

| Variant | Yesterday (Nov 13) | Mechanism |
|---|---|---|
| **Actual — TUNED STACK v2** | **−₹1,720.00** | stop on the entry bar, level fill @655.00 |
| T-B1a LOCK30-TRAIL | −₹1,720.00 | Changes only the target branch (at +90, floor +30 and ride); the leg died on its entry bar — +90 never reached, lock never armed. Identical. |
| T-B1b LOCK10-AT-58 | −₹1,720.00 | +58 arm never reached; −50 stop on the entry bar. Identical. |
| T-B2a PE-STOP40 | **−₹1,420.00** | The entry bar's low crossed the −40 level (665.00) on its way through −50; under the frozen gap-through level-fill convention the −40 stop books its exit AT 665.00 on the same bar — ₹300 less lost. |
| T-B2b PE-STOP60 | **−₹2,020.00** | The wider stop did NOT survive the entry bar: the low also crossed the −60 level (645.00), so it fills at 645.00 on the same 12:20 bar — ₹300 worse. (Contrast Nov 12, where the −60 stop survived the entry bar and exited 12:45.) |
| T-B2c PE-BE50 | −₹1,720.00 | Acts on PLAIN PE legs only; the NS3 leg carries trig/lock params, so the transform does not apply (and the leg stopped before any +50 arm regardless). Identical. |
| T-B3 LADDER-STACK | **−₹1,765.00** | Hard stop on the entry bar: the bar's premium CLOSE 653.50 ≤ entry −20 (685.00) → exit at the close, ₹45 worse than the incumbent's level fill. No spot stage was reached. |

No EVE-06(a) re-entry was derived on Nov 13 under any variant
(no_trigger after the 12:20 stop exit); no v1 add-on legs; no EVE-19
skips. Legacy BNF-PAPER-V1 had no Nov 13 trade (primary log: no-trade
day), so every legacy-frame number below is ₹0 for the day.

### Updated November counterfactuals, Nov 2–13 (Thursday's Nov 2–12 in brackets)

| Book | Nov 2–13 CF | [Nov 2–12] |
|---|---|---|
| Incumbent STACK v2 | **−₹2,680.00** | [−₹960.00] |
| T-B1a | −₹4,480.00 | [−₹2,760.00] |
| T-B1b | −₹5,080.00 | [−₹3,360.00] |
| T-B2a | **−₹1,780.00** | [−₹360.00] |
| T-B2b | −₹3,580.00 | [−₹1,560.00] |
| T-B2c | −₹2,680.00 | [−₹960.00] |
| T-B3 | −₹5,651.50 | [−₹3,886.50] |

T-B2a remains the least-bad November counterfactual — and remains the
second-worst Jan–Oct book of Thursday's gate (−₹34,786 vs incumbent).
Thursday's reading stands, extended one day: the variant that most
improves November is the one the year most condemns.

### Repair programme (2026-11-12) on yesterday

| Variant | Yesterday | Why / updated Nov 2–13 CF |
|---|---|---|
| BV-1 (drop Skill V3 PE base ≥10:15, legacy frame) | ₹0 — no effect | The filtered class produced no leg yesterday (legacy frame had no trade at all). CF unchanged: **+₹1,520.00** |
| BV-2 (drop all Skill V3 PE, legacy frame) | ₹0 — no effect | Same. CF unchanged: **+₹1,520.00** |
| BV-3 (NS1 only if S1 base exited by target) | ₹0 — no effect | No NS1 legs yesterday on either frame. CF unchanged: **−₹960.00** |
| B2-FOLLOWER (stack BASE kept only if a second-leg leg entered earlier that day) | **−₹1,720.00** | Yesterday's only stack leg is itself a second-leg-family leg (NS3_gapclass), not BASE → kept, incumbent geometry. Updated CF Nov 2–13: Nov 4 S3-R1 +₹2,480 kept · Nov 9 BASE −₹1,720 dropped (no earlier second-leg leg that day) · Nov 12 S3-R1 −₹1,720 kept · Nov 13 NS3 −₹1,720 kept = **−₹960.00** |
| B2-LITERAL (observation only — timing-audit FAIL Thursday, not a candidate) | −₹1,720.00 | No BASE legs exist yesterday to filter. November observation on the same leg set: −₹960.00 |
| N1 (TUNED v1 / v2 November forwards) | ₹0 / ₹0 | DEC-S1's Nov 13 population is empty (see §3), so both drop-only derivations are empty. CFs unchanged: v1 +₹3,036.50 · v2 ₹0 (Nov 2–13) |
| NB-1 (B PE conditioned on gap size) | **NOT RERUN** | Thursday itself established this is not testable from stored data: the scored DEC-S1 leg store carries no per-leg gap field. Unchanged. |

---

## 2. NIFTY — yesterday: no leg in any population Thursday's variants touch

Verified from the logs: DEC-S1 shadow log 2026-11-13 = explicit
no-trade row (B: no fade, gap −0.35%; C: not a weekly expiry day);
C3G7 primary log = no-trade row. TUNED v1/v2 and T-N3 derive from the
DEC-S1 population, which is empty.

| Variant | Yesterday (Nov 13) |
|---|---|
| TUNED v1 (incumbent geometry) | ₹0 — no legs |
| T-N1a (v1 @ lock +50) | ₹0 — no legs |
| T-N1b (v1 @ tgt2 +150) | ₹0 — no legs |
| TUNED v2 | ₹0 — no legs |
| T-N3 (v2 + C CE restored) | ₹0 — no legs (no C CE existed yesterday) |
| T-N2 (admission conditioning) | **NOT RERUN** — no variant was ever registered: Thursday skipped T-N2 by design after its field inventory, so there is no definition to reconstruct. |

Precision note: the day's only Nifty leg anywhere was the standing
U1-N1 CONTROL line's Skill V3 CE 25200 (in 10:10 @274.50, stop @224.50,
**−₹3,470.00**). None of Thursday's Nifty variants act on the U1-N1
control book — they are transforms of the DEC-S1/TUNED population — so
it is outside every number above, and it is not part of the primary.

---

## 3. STOCKS — yesterday: 2 Stock Book trades (per 100 shares provisional, ₹40/trade)

Actual (control): IRCTC · N4-V3 · SHORT · +₹230.00 and ASTRAL ·
INV-ABOVE · LONG · −₹677.80 → **day net −₹447.80**.

| Variant | Yesterday (Nov 13) | Mechanism |
|---|---|---|
| **Actual — Stock Book** | **−₹447.80** | — |
| TUNED SHADOW v1 (skip N4-V3 LONGs with 09:30 move ≥ +3.0%) | −₹447.80 | IRCTC is a SHORT (move −2.304%) — the cap is one-sided, SHORTs uncapped, taken identically; ASTRAL is INV-ABOVE, outside the cap's scope. Nothing skipped. The day's own shadow record agrees (both N4 signals taken, no skip). |
| TUNED SHADOW v2 / EVE-20 (drop INV-ABOVE if prior day ≥ +4.0% close-to-close) | −₹447.80 | ASTRAL's prior trading day (Thu Nov 12) close-to-close move was **−0.08%** (verified in the day's own engine record) — far below the +4.0% drop trigger → taken identically. |
| T-S2 @ 0.8% (N4-V3 threshold lowered from 1.0%) | −₹447.80 | No trade is added: yesterday's reaction-day candidates were OIL +0.568% (below even 0.8%), BDL −1.346% and IRCTC −2.304% (both already ≥1.0%). By Thursday's frozen superset property every 1.0% trade is identical at 0.8%, so the day is unchanged. |
| T-S1 (S1 windows inside T2 slot reservation, Stock Engine) | **NOT RERUN** on these trades | By construction T-S1 is a selection layer over the Stock ENGINE's 1,081-name candidate stream (13:30 decision point, chain ≤2 of 6 slots); the two assigned trades are Stock Book component trades, not engine picks, so the variant has no action on them. For the record only: the Stock Engine's own Nov 13 — its final live day before the owner's wind-down — was −₹3,182.52 on 5 picks; that is the engine's actual, not a T-S1 number. |

---

## SCOPE AND NON-RERUNS

- In scope, per the order's definition of Thursday: the three segment
  tuning programmes of 2026-11-12 (`tuning_bank_`, `tuning_nifty_`,
  `tuning_stocks_2026-11-12`) + `repair_programme_2026-11-12.md`.
  Other same-date programmes (Bank fast-exit FE set, daily baseload,
  Family B gate, invention round) are outside that definition and were
  not run.
- NOT RERUN, with reasons: **T-N2** (never registered — no definition
  exists) · **NB-1** (definition exists but not scoreable from the
  stored leg store — Thursday's own finding) · **T-S1** (applies to a
  different book's selection layer; no action possible on the assigned
  trades).
- Every other reconstructed variant was run. Nothing was approximated:
  Bank variants ran through Thursday's own transform/replay/ladder
  code; repair and shadow rules are drop-only on candle-scored logs,
  Thursday's own convention.

Files: `thursday_on_friday_bank_nov.py` (Thursday's November helper
extended to Nov 13; identity asserted in-run), 
...[truncated 738 chars]