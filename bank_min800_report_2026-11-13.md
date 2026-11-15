# BANK NIFTY — REPORT A: THE ₹800/DAY MINIMUM (2026-11-13)

**Owner's bar (2026-11-13 16:03 IST): Bank Nifty individually, at least ₹800/day, minimum.**
Bank only. Pure option buying, 1 lot, ₹220/trade inside every net, premium basis.
Paper only, real money ₹0. Every figure below was re-summed in this run from the
stored, already-verified ledgers (stack features file, legacy v21 ledger, the
`bank_2000_*` CSVs, the B2 pool ledger). Denominator: **205 trading days, Jan–Oct 2026**.

---

## 1. THE RANKING — every existing Bank configuration vs ₹800/day

Sorted by ₹/day. Gate status is the standing verdict from the run that gated each book.

| # | Configuration | Legs | Jan–Oct total | ₹/day | Days ≥ ₹800 | Days ≥ ₹2,000 | Red months | Gate |
|---|---|---|---|---|---|---|---|---|
| 1 | **TUNED STACK v2** (running primary) | 111 | **+₹127,351.50** | **₹621.23** | 25.4% (52) | 23.4% (48) | 0 | PASS |
| 2 | C1 — Stack + Volrix increment *(new, §2)* | 120 | +₹120,271.50 | ₹586.69 | 24.9% (51) | 22.9% (47) | 1 (Jun) | **FAIL** |
| 3 | Union U1 (stack + legacy, deduped) | 123 | +₹118,111.50 | ₹576.15 | 25.9% (53) | 23.9% (49) | 0 | FAIL |
| 4 | C2 — Stack + Skill on stack's zero days *(new, §2)* | 138 | +₹97,711.50 | ₹476.64 | 27.3% (56) | 25.4% (52) | 2 (Jun, Aug) | **FAIL** |
| 5 | C3 — Stack + Skill + Volrix on zero days *(new, §2)* | 143 | +₹93,311.50 | ₹455.18 | 27.8% (57) | 25.9% (53) | 2 (Jun, Aug) | **FAIL** |
| 6 | Legacy B2/NS1 frame (BNF-PAPER-V1) | 99 | +₹83,650.50 | ₹408.05 | 21.5% (44) | 20.5% (42) | 3 (Apr, Jul, Aug) | PASS |
| 7 | PB4 — union, legs < ₹650 premium | 52 | +₹82,611.50 | ₹402.98 | 13.2% (27) | 11.7% (24) | 1 (Jul) | PASS |
| 8 | PB2 — stack, legs < ₹650 premium | 49 | +₹76,371.50 | ₹372.54 | 12.7% (26) | 11.2% (23) | 1 (Jul) | FAIL (placebo) |
| 9 | PB3 — union, legs < ₹500 premium | 35 | +₹75,989.50 | ₹370.68 | 10.2% (21) | 9.8% (20) | 1 (Aug) | PASS |
| 10 | PB1 — stack, legs < ₹500 premium | 32 | +₹69,749.50 | ₹340.24 | 9.8% (20) | 9.3% (19) | **0** | PASS |
| 11 | PB0 — legacy, legs < ₹500 premium | 27 | +₹59,902.50 | ₹292.21 | 7.8% (16) | 7.8% (16) | 3 (Mar, Jul, Aug) | PASS |
| 12 | Skill V3 standalone (Bank) | 70 | +₹3,596.00 | ₹17.54 | 14.6% (30) | 13.7% (28) | 5 | FAIL |
| 13 | Volrix (b) standalone (Bank) | 13 | +₹2,840.00 | ₹13.85 | 2.9% (6) | 2.9% (6) | 2 (Jun, Jul) | FAIL |

*TUNED SHADOW v2 is the stack's own frame (the stack ledger above is it). TUNED SHADOW v3
exists only as a November shadow line — no Jan–Oct ledger exists for it, so it cannot be ranked.*

**No configuration reaches ₹800/day. The closest is the running stack at ₹621.23/day.**

---

## 2. NEW COMBINATIONS — pre-registered, fully gated in this run

Three combinations that had never been gated in this form (the full 3-system assembly and
the plain union were already closed routes and were **not** retested). Registered before scoring:

- **C1** = TUNED STACK v2 + the Volrix pool legs the stack does not already take (9 legs).
- **C2** = TUNED STACK v2 + Skill pool legs (not already in the stack) admitted **only on days
  the stack itself took no trade** (27 legs) — the frequency-shaped version: fill the stack's idle days.
- **C3** = TUNED STACK v2 + both increments on stack zero-trade days only (32 legs).

Gate legs (workspace standard): total > 0 · both halves (Jan–May / Jun–Oct) > 0 · ex-top-3 > 0 ·
red months ≤ 4 · **G1: the combination must beat the stack parent** (no dilution) ·
**G4: the increment must beat the p95 of random same-size subsets** of the 41 non-stack pool legs
(2,000 draws, seed 20261113). Timing: every increment leg is a stored, candle-scored leg from the
timing-audited B2 pool ledger; no leg was re-derived. Re-sum: each combination's total was
re-summed from its leg list independently of its parts.

| Combo | Increment legs | Increment value | Combo total | ₹/day | Halves | Ex-top-3 | Increment placebo rank | Verdict |
|---|---|---|---|---|---|---|---|---|
| C1 | 9 | **−₹7,080.00** | +₹120,271.50 | ₹586.69 | +₹82,122 / +₹38,149.50 | +₹93,448.50 | 28.6th pct (p95 +₹1,320) | **FAIL — G1 + G4** |
| C2 | 27 | **−₹29,640.00** | +₹97,711.50 | ₹476.64 | +₹70,842 / +₹26,869.50 | +₹70,888.50 | 0.8th pct (p95 −₹8,640) | **FAIL — G1 + G4** |
| C3 | 32 | **−₹34,040.00** | +₹93,311.50 | ₹455.18 | +₹69,882 / +₹23,429.50 | +₹66,488.50 | 0.4th pct (p95 −₹13,040) | **FAIL — G1 + G4** |

The pattern is identical to every prior assembly on both indices: the legs Skill and Volrix fire
*outside* the frame lose money. Filling the stack's idle days with them (C2/C3) raises the
*count* of ₹800+ days slightly (27–28% vs 25.4%) while cutting the average — frequency bought
with losing trades is not frequency.

## 3. OI LINE

**OI pending** — the OI history dataset exists, but the build-up programme's results sections
(coverage / gate / November / verdict) are still empty as of this run; no gated OI Bank stream
exists to combine with the stack.

## 4. NOVEMBER 2–12 — top-3 configurations, day by day (cumulative)

Trading days: Nov 2, 3, 4, 5, 6, 9, 11, 12 (Nov 10 = Diwali holiday). Nov 13 excluded — the
stack's live row for today was still pending scoring at the daily-stats run.

| Day | STACK (cum) | C1 (cum) | UNION U1 (cum) |
|---|---|---|---|
| Nov 2 | ₹0 | ₹0 | −₹1,720 |
| Nov 3 | ₹0 | ₹0 | −₹3,440 |
| Nov 4 | +₹2,480 | +₹2,480 | −₹2,680 |
| Nov 5 | +₹2,480 | +₹2,480 | −₹2,680 |
| Nov 6 | +₹2,480 | +₹2,480 | −₹2,680 |
| Nov 9 | +₹760 | +₹760 | −₹4,400 |
| Nov 11 | +₹760 | +₹760 | −₹1,920 |
| Nov 12 | **−₹960** | **−₹960** | **−₹1,160** |

C1's November line is identical to the stack's because Volrix fired **zero** times in November
(verified trigger scan: Bank rose on every deciding day; cooldown blocked through Nov 9).
Character: the stack line is **degradative overall** across the window (peaks +₹2,480 on Nov 4,
gives it back by Nov 12); the union is degradative throughout despite the Nov 11–12 NS1 recovery.

## 5. VERDICT

**₹800/day is NOT reached by any gated Bank configuration.**

- Closest: **TUNED STACK v2, ₹621.23/day** — already running as Bank's primary.
- **Exact gap: ₹178.77/day**, i.e. **₹36,648.50** over Jan–Oct (₹800 × 205 days = ₹164,000 needed;
  the stack produced ₹127,351.50).
- What is missing, in legs: the stack fires **111 legs in 205 days (0.54/day)** at an average of
  **₹1,147.31 per leg**. Closing the gap at that average leg value needs **≈ 32 additional
  stack-quality legs over ten months (~3.2/month, a ~29% frequency increase)** — or, at the
  +₹2,480 target-win size, **≈ 15 additional target wins**. Every stored increment that could
  supply extra legs is negative: Volrix increment −₹7,080 · Skill-on-idle-days −₹29,640 ·
  both −₹34,040 · legacy-only union legs −₹9,240 vs the stack. There is no combination of the
  existing, verified Bank ledgers that adds frequency without subtracting money.
- The only identified source of genuinely new Bank legs is the **OI build-up line**, whose gate
  has not landed. Until it does, ₹621/day is Bank's verified ceiling and ₹800/day is ₹179/day
  beyond everything the stored evidence can produce.

*Sources (all re-summed this run): `solid60_programme_2026-11-13_bank_A_stack_features.csv` ·
`bank_engine_r6_v21_trades.csv` · `historical_proof_bank_B2_trades.csv` ·
`bank_2000_PB0..PB4 / U1` CSVs · `bank_2000_results.json` (November section) ·
`november_shadow_stack_bank_log.csv` / `november_paper_bank_log.csv` (November parents).*
