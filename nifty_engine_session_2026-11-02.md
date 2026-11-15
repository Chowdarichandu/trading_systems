# Nifty Engine Session — 2026-11-02 (Run 3, Rounds 1 + 2)

**Directive:** Nifty must reach a ₹15,000/month pace on its own = ≥ ₹1,50,000 across Jan–Oct 2026 on the gated book (premiums per 1 lot of 65, cost ₹220/trade, UNIQUE-ONCE). Round 2 added by Chandu's standing order (~12:35 IST): no saturation conclusions accepted — combinations and permutations, minimum 12 cycles.

**Result, plainly: the floor was NOT reached.** 24 gated cycles ran. One cycle banked a real but marginal improvement (+₹208.00). The ending book runs at **₹9,820.90/month vs the ₹15,000 floor — remaining gap ₹51,791.00**. The session's best gated object (+₹114,921.75) is a flagged variant that fails its family's pre-stated conditions; adopting it is Chandu's decision in the Nifty channel, not the engine's.

- Starting book (Run-2 final): C3L + BE50 + lock75 + TGT2-180 + EXP0 = **+₹98,001.00** (59 trades, FT 39.0%, 1.45/wk).
- Ending book: C3L + BE50 + **lock +50 + TGT2 +175** + EXP0 = **+₹98,209.00** (59 trades, FT 39.0%, 1.45/wk).
- Real money ₹0 everywhere; paper only. The frozen November primary (NF-PAPER-C3G7) and all November paper files were not touched.
- Every cycle below ran behind the FULL controls gate in the same run: timing/leak audit, placebo (+30 min entry shift), halves, month table, ex-top-3, independent re-sum. **Every cycle scored with 0 NOT_COMPUTED except cycle 24**, which names its one unscoreable leg explicitly.

## Data work (the session's structural win)

The premium fetch wall that blocked five populations in earlier runs was cleared via the expired-instruments route (browser User-Agent header on every call): 5 EV legs, 21 S1 contracts, 59 ITM ±100 contracts, 59 weekly-expiry contracts fetched and entry-bar verified. A loader trap was caught and fixed: the candle loader's glob fallback silently returned MONTHLY-expiry files for weekly lookups — all Run-3 cycles 19+ and all of Round 2 use exact-tag file loading. One leg remains unfetchable: 2026-10-28, 22500 PE, weekly expiry 2026-11-03 — the registry returned an empty contract list for that expiry on three retries on 2026-11-02 (it had returned contracts for the same expiry earlier the same day). It is NOT_COMPUTED wherever it appears, never estimated.

## Round 1 (cycles 16–21)

| Cycle | Variant | Total (₹) | Trades | FT | /wk | Verdict |
|---|---|---|---|---|---|---|
| 16 | CH3-R: confirmed legs only if entry ≤ 09:55 | 111,684.75 | 44 | 45.5% | 1.08 | NOT BANKED — flagged (August −3,671.00 → −5,187.25; frequency cut) |
| 17 | C3L + EV5 (5 dropped solo non-Skill legs) | 81,502.50 | — | — | — | REJECTED (added legs −16,498.50; all 4 Volrix solos are full stops) |
| 18 | S1-44 union challenger | 48,035.25 | — | 25.7% | 2.49 | REJECTED decisively (added legs −49,965.75) |
| 19 | ITM100 (every leg one strike ITM) | 93,278.75 | — | 42.4% | — | REJECTED (−4,722.25 despite better FT) |
| 20 | WEEKLY (weekly expiry in force) | 81,263.50 | — | 37.3% | — | REJECTED (−16,737.50; March collapses) |
| 21 | SQ1525 (square-off 15:25) | 97,399.75 | 59 | — | — | REJECTED (−601.25, a wash) |

Round 1 banked nothing. All controls clean in every cycle.

## Round 2 (cycles 22–39) — combinations & permutations

### Phase A — C3 confirmation permutations

| Cycle | Variant | Total (₹) | Trades | FT | /wk | Verdict |
|---|---|---|---|---|---|---|
| 22 | P1: pure 2-of-4 (solo-(lA) exception removed) | 88,097.75 | 52 | 38.5% | 1.28 | NOT BANKED — the (lA) exception is worth +9,903.25 |
| 23 | P2: (lA)-mandatory confirmation | 66,003.00 | 41 | 39.0% | 1.01 | NOT BANKED — non-(lA) confirmations are worth +31,998.00 |
| 24 | P3: solo admission, entry ≥ 10:00 gate | 59,663.75 | 101 + 1 NC | 26.7% | 2.49 | NOT BANKED decisively — added legs −38,337.25; July flips green→red. NC leg: 2026-10-28 22500 PE (named above; baseline net −3,470, so its exclusion biases P3 UP) |

### Phase B — G7 exit-geometry grid (lock × second target; 59 trades, FT 39.0%, controls clean in all nine cells)

| Lock \ TGT2 | +130 | +150 | +175 |
|---|---|---|---|
| +40 | 92,196.50 | 91,172.75 | 95,758.50 |
| +50 | 93,997.00 | 93,623.25 | **98,209.00 — BANKED (cycle 30)** |
| +60 | 88,533.75 | 93,360.00 | 97,945.75 |

The surface is a flat plateau (lock 50–75 × TGT2 175–180 ≈ ₹97.9–98.2k). Cycle 30 banked at the plateau's top: **+₹208.00 over ten months**, stated at face value — it is a marginal banking, not a breakthrough. August worsens −₹3,671.00 → −₹4,129.25 inside an already-red month; no green month flips red.

### Phase C — expiry-week day-pockets

| Cycle | Variant | Total (₹) | Verdict |
|---|---|---|---|
| 34 | EXP1: skip DTE ≤ 1 | 87,499.50 | NOT BANKED — DTE-1 legs are worth +10,501.50 (the mirror of DTE-0) |
| 35 | EW-G7: DTE 1–4 legs at lock50/TGT2-150 | 94,292.75 | NOT BANKED (−3,708.25) — pocket family closed in both directions |

### Phase D — combinations (full gate + CH3 family clauses: August ≥ −₹3,671.00, frequency ≥ 1.30/wk)

| Cycle | Combination | Total (₹) | Trades | FT | /wk | Verdict |
|---|---|---|---|---|---|---|
| 36 | CH3-R × grid-best (lock50/TGT2-175) | **114,921.75** | 44 | 45.5% | 1.08 | NOT BANKED — **FLAGGED, session's best variant** (standard gate passes; August −5,187.25 and frequency fail the family clauses) |
| 37 | CH3-R × EW-G7 | 108,434.75 | 44 | 45.5% | 1.08 | NOT BANKED (same clause failures) |
| 38 | CH3S: CH3-R ∩ P1 | 101,781.50 | 37 | 45.9% | 0.91 | NOT BANKED (frequency fails hardest) |
| 39 | CH3-R × EXP1 | 105,838.25 | 41 | 46.3% | 1.01 | NOT BANKED (same clause failures) |

## Ending book — full controlled scorecard

**C3L + BE50 arm + runner lock +50 + second target +175 + EXP0 (expiry-day skip)**, premiums per 1 lot (65), cost ₹220/trade, UNIQUE-ONCE, Jan–Oct 2026:

- **Total: +₹98,209.00** — 59 trades, FT 39.0%, 1.45 trades/week, **₹9,820.90/month vs ₹15,000 floor → gap ₹51,791.00**
- Months: Jan +20,064.75 · Feb +14,882.25 · Mar +18,180.00 · Apr +4,240.75 · May −5,793.00 · Jun +7,584.00 · Jul +13,584.50 · Aug −4,129.25 · Sep +5,020.00 · Oct +24,575.00 (no red month-ends, cumulative)
- Halves: Jan–May +₹51,574.75 · Jun–Oct +₹46,634.25 (both positive)
- Ex-top-3: +₹64,744.00 · Placebo (+30 min entries): +₹34,008.50 (beaten) · Timing audit 59/59 clean · Independent re-sum exact · NOT_COMPUTED 0

## Flagged variant — full controlled scorecard (NOT banked; Chandu's call)

**CH3-R × lock50/TGT2-175** (cycle 36): confirmed legs only if entry ≤ 09:55; solo (lA) legs any time; EXP0; BE50 + lock +50 + TGT2 +175.

- **Total: +₹114,921.75** — 44 trades, FT 45.5%, 1.08/week, ₹11,492.18/month (still ₹35,078.25 short of the floor pace if adopted)
- Months: Jan +23,974.75 · Feb +14,882.25 · Mar +21,650.00 · Apr +7,471.50 · May −2,323.00 · Jun +7,584.00 · Jul +17,054.50 · Aug −5,187.25 · Sep +5,020.00 · Oct +24,795.00
- Halves: +₹65,655.50 / +₹49,266.25 · Ex-top-3 +₹81,456.75 · Placebo +₹63,269.50 (beaten) · Audit 44/44 clean · Re-sum exact · NOT_COMPUTED 0
- Why not banked: it fails the CH3 family's own pre-stated conditions — August worsens (−₹3,671.00 → −₹5,187.25) and frequency materially falls (1.45 → 1.08/wk). The engine flags; it does not relax pre-stated clauses to manufacture a banking.

## What saturated (the enumerated space, all premium-scored under the full gate)

Entry side: confirmation permutations (2-of-4 pure / (lA)-mandatory / incumbent union), solo admission at both time gates (early = N1/C3 history; late ≥ 10:00 = cycle 24), time-window filters on confirmed legs (CH3 family), leg additions from three independent sources (EV solos, S1 union, NS-style add-ons in earlier runs), strike shift (ITM100), expiry instrument (weekly), DTE pockets in both directions (skip / early-bank). Exit side: stop and BE-arm variants (earlier runs), the full lock × TGT2 grid, square-off at 15:10 vs 15:25, pocket geometry. Combinations: CH3-R × {grid-best, EW-G7, P1, EXP1} — the full pairwise space over the session's improving objects.

**What remains outside the engine:** (1) Chandu's adoption judgement on the flagged cycle-36 variant; (2) a genuinely new signal source (no unscored premium population from the U1 family remains); (3) December fresh data, which the December-adoption judgement will weigh against both the ending book and the flagged variant.

## Files

- Freezes + verdicts: `nifty_engine_frozen.md` (Run 3 sections, cycles 16–39)
- Log: `nifty_engine_log.md` (Run 3 sections, rounds 1–2) · Lessons 27–40: `nifty_engine_lessons.md` · State: `nifty_engine_state.json` (cycle 39)
- Scripts: `nifty_engine_run3_cycle16.py`, `nifty_engine_run3_cycle17_18.py`, `nifty_engine_run3_cycle19_20.py`, `nifty_engine_run3_cycle21.py`, `nifty_engine_r2_harness.py`, `nifty_engine_r2_diag.py`, `nifty_engine_r2_phases_abc.py`, `nifty_engine_r2_phase_d.py`, fetchers `nifty_engine_run3_fetch*.py`
- Per-cycle gated summaries: `nifty_engine_run3_cycle{16..21}_summary.json`, `nifty_engine_run3r2_cycle{22..39}_summary.json`
