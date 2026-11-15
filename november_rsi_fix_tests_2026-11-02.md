# November RSI — Fix-Candidate Tests, 2026-11-02

Three pre-diagnosed fix candidates (one per book), each scored through the full controls
gate **in the same run** as its first scoring. Diagnosis source:
`november_rsi_homework_2026-11-02.md`. Paper only, real money ₹0. Frozen November
primaries, specs, official logs and crons untouched. Nothing here is promoted — a passing
candidate gets a drafted shadow spec only; the 17:15 RSI engine does formal promotion.

**Gate set applied identically to all three candidates** (per the backtest-controls-gate skill):
- **G1 Timing audit** — every entry at/after the moment its qualifying information existed; violations counted, not sampled.
- **G2 Independent re-sum** — the stored baseline is reproduced exactly by an independent engine in this run before any variant number is read.
- **G3 Improvement** — variant net > baseline net on the identical leg universe (a fix must fix).
- **G4 Placebo** — variant beats the placebo control clearly.
- **G5 Halves** — variant net ≥ 0 in both halves of the window (Jan–May / Jun–Oct).
- **G6 Concentration** — variant net ex-top-3 ≥ 0.
- **G7 Month integrity** — no month that is green in the baseline turns red in the variant.
- **G8 Targeted metric** — the specific failure count the fix aims at must actually fall.

---

## Candidate 1 — BANK NIFTY: break-hold confirmation for OR-break legs → **REJECTED**

**Book/basis:** BNF-PAPER-V1's base pool (B2) as stored in
`historical_proof_bank_B2_trades.csv` — index options, premium per 1 lot of 30,
₹220/trade, UNIQUE-ONCE as stored.
**Variant (exact):** an OR-break leg (Skill V3 among the leg's source systems) is taken
ONLY if, after the first 5-min close beyond the OR level (OR = 09:15–09:25 spot bars;
signal reconstructed per skill_v3_jansep.py, window 09:30–11:30), a later 5-min bar
closes still beyond that level **before** any bar closes back inside the OR. Entry =
open of the bar after the confirming close, on the leg's ATM premium candle
(strike = round(spot-open of entry bar / 100) × 100, the original prep rule; expiry =
the leg's stored monthly expiry). G0 exits unchanged (−50/+90, stop before target incl.
entry bar, square-off at the 15:10 close). Non-OR legs (19) pass through unchanged.

**Universe & audit:** 89 stored legs, all premium-COMPUTED. An independent G0 replay of
the stored legs reproduced the stored net and entry premium on **89/89** legs (G2 ✓).
Matched universe = 89 (variant NOT_COMPUTED = 0 — every confirmed leg's premium candles
were found in the official caches; every load verified to be the exact contract file for
its strike+expiry). The reconstructed first-break close matched the stored entry−5 min
on 61/70 OR legs; the other 9 are multi-source legs whose pooled entry came from a
co-source system. Of the 70 OR legs: **52 confirmed, 18 rejected** (first post-signal
close back inside the OR). Confirmation delay on confirmed legs: avg 9.0 min (range
5–55); the delayed entry changed the ATM strike on 27/52 legs.

**Results (matched universe, ₹ per 1 lot):**
| | Net | Trades | FT (target rate) |
|---|---|---|---|
| Baseline B2 pool | **+18,731.50** | 89 | 39/89 = 43.8% |
| Variant (hold confirmation) | **+4,462.00** | 71 | 29/71 = 40.8% |
| Δ | **−14,269.50** | −18 | −3.0 pts |

**Decomposition — the two halves of the fix pull opposite ways:**
- The 18 rejected legs were worth **−₹6,741.00** in the baseline (including 9 of the 14
  quick stops) — the rejection half of the fix genuinely avoids damage.
- But on the 52 confirmed legs, baseline **+₹10,337.00 → variant −₹10,673.50**: the
  confirmation **delay itself cost ₹21,010.50** (premium paid after the move extended,
  follow-through already spent). The delay costs ~3× what the filter saves.

**Controls:**
- G1 timing: **0 violations** — every variant entry bar is strictly after its confirming
  close; entry premium = open of that bar.
- G4 placebo (opposite option type at each confirmed leg's entry bar/strike, same G0
  exits, n=52): **−₹13,831.00** vs variant −₹10,673.50 on the same legs. Variant beats
  the placebo — but both are negative while the baseline on those legs is +₹10,337; the
  placebo pass does not rescue a variant whose damage comes from its own delay.
- G5 halves: H1 +₹32,497.00 → +₹14,366.50; H2 −₹13,765.50 → **−₹9,904.50 (still
  negative — FAIL)**.
- G6 ex-top-3: baseline +₹11,291.50 → variant **−₹2,978.00 (FAIL)**.
- G7 months (baseline → variant): Jan −1,920 → −4,400 · Feb +15,377 → +5,446.50 ·
  Mar +9,720 → +9,720 · Apr +2,080 → +5,520 · **May +7,240 → −1,920 (green→red — FAIL)** ·
  Jun −9,560 → −1,920 · Jul −8,800 → −11,280 · Aug −7,301 → −5,360 · Sep −2,024.50 →
  −4,504.50 · Oct +13,920 → +13,160.
- G8 targeted metric: OR-leg quick stops (≤10 min) 14 → **13** — negligible; the
  filter's quick-stop benefit shows up only inside the rejected set, which is already
  counted in the decomposition.

**Verdict: REJECTED.** Deciding gate **G3** (variant net +₹4,462.00 < baseline
+₹18,731.50 on the identical universe); G5, G6 and G7 also fail.
*Note, not a rescue:* today's (2026-11-02) live PE leg matches the rejected shape per
the homework/watcher record (spot closed back inside the OR on the next bar), so this
filter would have saved today's −₹1,720. Across Jan–Oct the same rule loses ₹14,269.50
net. One day does not overturn the gate.

---

## Candidate 2 — STOCKS P2F family: skip the opening bar → **REJECTED**

**Book/basis:** SarvaRitu stocks book, P2F family — equity cash, provisional per
100 shares, ₹40/trade. Universe = the 87 stored component trades the homework used
(P2F 46 + P2F-R2 34 + R2-LOWBAND 7, Jan–Oct 2026); excluded for missing candles: **0**.
**Variant (exact):** entry moves from the 09:15 open to the open of the second 5-min
bar (09:20), taken only if price is still on the trade's side of the original entry
price at that point (LONG: 09:20 open ≥ 09:15 open; SHORT: ≤); otherwise skipped.
Exits unchanged per component, measured from the new entry.

**Engine audit (G2 ✓, 87/87 exact):** the stored files' exit convention was
reverse-engineered and verified before any variant scoring — range-touch exits scanned
from the bar **after** the entry bar, stop before target, fill at the level price,
square-off at the 15:10 bar close. This engine reproduces every stored trade's exit
reason, price, time and net exactly (87/87). Two findings the RSI engine should note:
1. **The family's stored geometry is NOT uniform:** the P2F (ch1) file ran **T125/S065**
   (stop −0.65% on all 46 trades), while P2F-R2 and R2-LOWBAND ran T125/S050. The test
   brief's "T125/S050" premise is wrong for the ch1 file. Both baseline and variant
   therefore use **each file's own stored geometry**, so the test isolates the entry
   change and nothing else.
2. In the stored convention a trade can never exit inside its entry bar — exits are
   first evaluated on the following bar. (The homework's "entry-bar stop-out" group is,
   in stamp terms, stops stamped 09:20.)

**Results (identical 87-trade universe, ₹ per 100 shares, provisional):**
| | Net | Trades taken | Win rate | Stops ≤15 min |
|---|---|---|---|---|
| Baseline (09:15 open) | **+27,293.58** | 87 | 52.9% | 25 |
| Variant (09:20 + side condition) | **+9,582.00** | 60 | 43.3% | 22 |
| Diagnostic: delay only (09:20, no condition) | +6,568.00 | 87 | — | **32** |
| Placebo: opposite direction at 09:20 open | +786.00 | 87 | — | — |

**Decomposition:** the side condition does identify bad trades — the 27 skipped trades
were worth **−₹3,560.92** in the baseline. But on the 60 kept trades the one-bar delay
cost **₹21,272.50** (baseline +₹30,854.50 → variant +₹9,582.00): the reaction
follow-through is largely spent by 09:20, and the delayed entry sits closer to the
morning reversal — delay-only takes *more* quick stops than the baseline (32 vs 25).

**Controls:**
- G1 timing: the condition uses only the two opens — the 09:15 open (fully known) and
  the 09:20 open, which is the entry print itself, under the same causal convention the
  baseline uses entering at the 09:15 open. No 09:20 range/close is used. **0 violations.**
- G4 placebo: variant +₹9,582.00 beats the opposite-direction placebo (+₹786.00)
  clearly — moot, given G3.
- G5 halves: H1 +₹18,144.86 → +₹3,558.00; H2 +₹9,148.72 → +₹6,024.00 (both stay
  positive, both shrink hard).
- G6 ex-top-3: baseline +₹17,261.96 → variant **−₹348.00 (FAIL)**.
- G7 months (baseline → variant): Jan +4,602.27 → +233.00 · Feb +6,856.13 → +3,444.00 ·
  Apr +399.87 → +236.00 · **May +6,286.59 → −355.00 (green→red — FAIL)** · Jun +2,139.62
  → +3,016.00 · Jul +3,240.21 → +1,427.00 · Aug +2,430.61 → +79.00 · Oct +1,338.28 →
  +1,502.00 (Mar/Sep: no family trades).
- G8 targeted metric: stops within 15 min of entry 25 → 22 only — and the delay-only
  diagnostic shows the delay component alone makes it *worse* (32).
- Breadth: symbols net-positive 16/25 → 13/25. Per component: P2F +₹13,120.32 →
  +₹8,087.00 · P2F-R2 +₹12,912.48 → **+₹490.00** · R2-LOWBAND +₹1,260.78 → +₹1,005.00.

**Verdict: REJECTED.** Deciding gate **G3** (variant net +₹9,582.00 < baseline
+₹27,293.58); G6 and G7 also fail, and G8 barely moves. The opening bar is not the
family's problem — the first bar *is* the follow-through; entering after it throws away
the edge the system exists to capture.

---

## Candidate 3 — STOCKS N4-V3: skip |move by 09:30| ≥ 3.0% → **BANKED-CANDIDATE**

**Book/basis:** SarvaRitu stocks book, N4-V3 component — equity cash, provisional per
100 shares, ₹40/trade. Universe = the standalone N4-V3 stored file
(`eq_n4deep_v3_trades_T125_janoct.csv`, 56 trades, Jan–Oct 2026, each carrying its
recorded move by 09:30) joined 56/56 to the book-exit-basis file
(`stocks_engine_sat15_n4_t150s080_trades.csv`). Results reported on **both** bases:
book (T150/S080) and scorecard (T125/S050).
**Variant (exact):** skip any entry whose recorded move by 09:30 is ≥ 3.0% in absolute
value; everything else unchanged.

**Re-sum (G2 ✓):** baseline book net **+₹19,977.90**, scorecard net **+₹7,990.43**;
bucket sums reproduce the homework's averages exactly (≥3% bucket: n=26, book total
−₹962.38 → avg −₹37.01; scorecard total −₹2,442.50 → avg −₹93.94).

**Results (₹ per 100 shares, provisional):**
| Basis | | Net | Trades | Win rate | Avg/trade |
|---|---|---|---|---|---|
| Book | Baseline | +19,977.90 | 56 | 48.2% | +356.75 |
| Book | **Variant** | **+20,940.28** | 30 | 50.0% | **+698.01** |
| Scorecard | Baseline | +7,990.43 | 56 | 37.5% | +142.69 |
| Scorecard | **Variant** | **+10,432.93** | 30 | 36.7% | **+347.76** |

Δ net: book **+₹962.38**, scorecard **+₹2,442.50** — the variant improves the total on
both bases *while taking 26 fewer trades*; the average outcome per trade roughly doubles.

**Controls:**
- G1 timing: the filter input is the move recorded **by 09:30**; all entries are at
  09:35. Causal by construction — **0 violations**.
- G4 placebos (book basis): **A** — skip the 1–2% bucket instead (n=41 kept):
  +₹8,873.80, H2 −₹4,615.41, ex-top-3 −₹2,411.90. **B** — size-matched neutral skip
  (drop the first 26 trades chronologically, keep 30): +₹3,955.06, ex-top-3 −₹7,622.67.
  The variant (+₹20,940.28) beats both clearly → the gain is specific to the ≥3%
  bucket, not an artefact of trading less.
- G5 halves: book H1 +₹21,728.00 → +₹16,882.00, H2 **−₹1,750.10 → +₹4,058.28** (the
  variant repairs the baseline's negative second half); scorecard H1 +₹5,155.13 →
  +₹3,530.53, H2 +₹2,835.30 → +₹6,902.40. Variant ≥ 0 in both halves on both bases ✓.
- G6 ex-top-3: book +₹5,882.25 → **+₹6,844.63**; scorecard **−₹1,783.54 → +₹658.96**
  (the variant turns the scorecard book's concentration stress positive) ✓.
- G7 months (book, baseline → variant): Jan +7,577.35 → +4,914.63 · Feb +6,226.46 →
  +4,306.54 · Mar +3,084.50 → +3,084.50 · Apr −566.91 → −45.00 · May +5,406.60 →
  +4,621.33 · Jun −1,785.76 → 0.00 (its only trade skipped) · Jul −1,962.13 → +1,033.63 ·
  Aug +1,387.74 → +2,807.28 · Oct +610.05 → +217.37 · Sep: no trades either side.
  **No green month flips red** ✓.
- G8 targeted metric: the ≥3% bucket — the only negative-average bucket in the
  diagnosis — is excised by construction; the kept set's average outcome rises on both
  bases (above).

**Verdict: BANKED-CANDIDATE — passes every gate.** Shadow spec drafted:
`november_shadow_candidate_stocks_2026-11-02.md` (spec only, no wiring; formal
promotion is the 17:15 RSI engine's step).
**Honest limits, stated for the promotion decision:** the book-basis net gain is small
(+4.8%) — the ≥3% bucket was only mildly negative on average (14 losers vs 12 winners),
so this candidate's real value is risk-shaping: it repairs the negative H2 and the
scorecard ex-top-3, and doubles the per-trade average. The cost is frequency: 56 → 30
trades over 10 months (~5.6/mo → ~3.0/mo). Scorecard win rate dips 37.5% → 36.7%.
In-sample Jan–Oct evidence only — November forward evidence decides adoption.

---

## Summary

| Candidate | Verdict | Controlling numbers (baseline → variant) | Deciding gate |
|---|---|---|---|
| Bank: OR-break hold confirmation | **REJECTED** | +₹18,731.50 → +₹4,462.00 (per 1 lot) | G3 net improvement (also G5, G6, G7) |
| Stocks P2F: skip opening bar | **REJECTED** | +₹27,293.58 → +₹9,582.00 (per 100 sh, provisional) | G3 net improvement (also G6, G7) |
| Stocks N4-V3: ≥3.0% move cap | **BANKED-CANDIDATE** | book +₹19,977.90 → +₹20,940.28; scorecard +₹7,990.43 → +₹10,432.93 (per 100 sh, provisional) | passes all gates |

Pattern across both rejections: in these two books the first minutes after the signal
carry the edge — any rule that waits, pays for the wait out of the follow-through. The
one pass is a *filter on entry quality* (skip the over-extended entries), not a delay.

Scripts: `fix_test_bank.py`, `fix_test_p2f.py`; working data:
`fix_tests_2026-11-02_cache/` (bank_results.json, p2f_results.json, n4_rows.json).
