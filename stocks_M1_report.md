# Line M1 — Month-Repair Loop on Chandu's 25 — report

Built under `stocks_M1_frozen.md` (Part A frozen before scoring;
Part B appended after diagnosis, before any fix was scored).
Equity cash intraday, LONG/SHORT. **Paper only — real money ₹0,
no orders.** Provisional per 100 shares, ₹40/trade deducted.
Home 25 only, Jan–Oct 2026.

## Step 1 — Anchors (both bases reproduced before anything was believed)

**Combined REAL book** (INV-LONG + N4-V3 + P2F 2.5%, T1 construction):
recomputed from the three component dumps — **matches T1 to the
paisa**: 344 trades, **+₹47,665.24**.

| Month | Trades | Net ₹ |
|---|---|---|
| Jan | 53 | +6,682.89 |
| Feb | 57 | **−5,533.46** |
| Mar | 62 | +7,283.60 |
| Apr | 42 | +3,339.69 |
| May | 46 | +14,836.37 |
| Jun | 21 | +1,305.20 |
| Jul | 9 | +3,282.63 |
| Aug | 16 | +5,802.73 |
| Sep | 9 | +3,820.20 |
| Oct | 29 | +6,845.39 |

**11:00 fade, home 25:** Jan–Sep reproduced to the paisa from the
O1 validation dump (946 trades, +₹3,901.89); October taken from
O2's own home-control run record (+₹341.29, 127 trades, its audit
counters 0 violations) → 1,073 trades, **+₹4,243.18**. Failing
months: **Feb −2,074.65 · Apr −12,241.39 · Jun −326.34 ·
Jul −5,982.82 · Aug −11,963.12** (5 red months; Sep +12,077.25).

**Timing audits (all clean):** N4-V3 — all 56 entries at 09:35,
trigger complete 09:30, 0 violations. P2F — all entries 09:15 on
exactly R+1 (checked against each stock's own trading calendar),
0 violations. INV-LONG — qualifying condition (Nifty prev close ≤
50DMA) **recomputed independently** from daily data: all 79 trade
dates satisfy it, 0 violations. Fade home — entry/meas fields
11:00 on all rows, 0 violations.

## Step 2 — Base choice (pre-declared rule)

Both bases have October positive (combined +₹6,845.39; fade
+₹341.29). Failing months: combined **1** (Feb) vs fade **5**.
**Working base = the combined REAL book.** No tie-break needed.

**September check (the user's named suspect):** September is
**GREEN on both home bases** (combined +₹3,820.20; fade
+₹12,077.25). September's failure was real — but on the broad
universe (U1: −₹181,381.95 across 500 names) and the large-cap
fade's July, not on his 25. On his stocks there is no September
hole to repair; the loop proceeds to the one failing month,
**February**, per the user's method (worst/only failing month,
debugged the same way).

## Step 3 — February diagnosis (combined book: 57 trades, −₹5,533.46)

- **By component:** INV-LONG 39 trades **−₹9,951.91** (win 10/39) ·
  N4-V3 9 trades +₹1,420.01 · P2F 9 trades +₹2,998.44. The hole is
  INV-LONG alone; the event legs were green in February.
- **By direction:** LONG −₹10,087.88 (43) vs SHORT +₹4,554.42 (14).
- **Date concentration — the whole story:** INV-LONG on
  **Feb 1 + Feb 2 lost −₹9,770.34 in 12 trades with ZERO wins**
  (Feb 1: 9 trades −₹6,805.02; Feb 2: 3 trades −₹2,965.32). The
  rest of February (27 INV trades) nets −₹181.57 — flat. Excluding
  those two days, the combined February is +₹4,236.88.
- **What Feb 1–2 were:** Feb 1 2026 was the **Union Budget Sunday
  session** — Nifty fell −2.16% that day (25,315.8 → 24,768.0),
  then whipsawed +1.26% / +2.53%. INV-LONG's qualifier (Nifty below
  50DMA: 2.17% below on Feb 1, 4.19% below on Feb 2) put it long
  into a news-shock crash and the next day's whipsaw. 29 of its 39
  February trades stopped out (−₹15,574.86 of stops vs +₹4,757.95
  of targets).
- **Why general rules struggle (all-months splits of the base):**
  the *deep-below* band (≥1.5% under the 50DMA) that contains
  Feb 1–2 is INV-LONG's **best** band overall (+₹20,247.65, 170
  trades) — a depth gate would gut the system. The ADR 3–4.5 band
  carries both Feb's loss (−₹11,378.77) and the year's INV profit
  (+₹19,442.94). Event-window INV trades are −₹8,378.38 in Feb but
  **+₹11,651.64 in May** — an event exclusion is not free (see
  MF-1 scoring: it flips June). TVSMOTOR, the year's top payer, is
  Feb's worst INV stock (−₹5,622.95, 0/3) — a blacklist would be
  Feb-fitted and is banned by the guards.
- **Swap diagnostics (computed, not yet scored as fixes):**
  DBL-LONG leg instead of INV-LONG → book Feb −₹1,555.78 (closer,
  still red; DBL's own Feb slice is −₹5,974.23). INV-LONG@T100 →
  book Feb −₹6,702.13 (worse). Neither greens February.

*(Fix families MF-1…MF-4 were frozen in Part B of
`stocks_M1_frozen.md` after this diagnosis and before scoring.
Scoring follows in the next section.)*

## Step 4 — February fix scoring (each fix applied to ALL months;

acceptance = Feb > 0 AND every other month > 0 AND Feb trades ≥ 23
AND ex-ante inputs only)

**MF-1 — INV-LONG event-window exclusion: REJECTED (breaks June).**
February greens: **+₹2,844.92** on 27 trades (activity ✓). But
June flips to **−₹622.32**: June's INV-LONG no-event slice is
−₹3,699.84 and its event-window slice (+₹1,927.52) was part of what
kept June afloat. Full table in `stocks_M1_results.json`; total
falls to +₹39,691.83. The event exclusion is a real effect in
February and a real cost in June — as a universal rule it fails
the user's own acceptance test.

**MF-2 — DBL-LONG leg swap: REJECTED (February still red).**
February improves −₹5,533.46 → **−₹1,555.78**, every other month
stays green, and the total even rises to +₹47,806.88 — but
February does not cross zero (DBL's own Feb slice is −₹5,974.23;
the DBL condition does not separate Feb 1–2 either). Closest miss
of the four.

**MF-3 — INV-LONG stop widened to −0.65% (S065): REJECTED
(February still red, June breaks).** February −₹3,998.53; June
flips −₹895.70. The wider stop rescues some Feb stop-outs and
gives back more elsewhere.

**MF-4 — INV-LONG high-ADR-only (≥4.5%): REJECTED (activity
guard + October breaks).** February greens mechanically
(+₹5,845.31) — but on **22 trades vs the 23-trade floor** (a
61.4% activity cut: exactly the "green by barely trading" pattern
guard 3 exists to stop), September drops to **zero trades**, and
October flips to **−₹845.69**. Rejected on two legs.

**Not scored, by pre-declared exclusion:** the Budget-calendar
stand-aside (see Part B). It would green February trivially —
that is precisely why it is barred: one in-sample instance, a
date filter in substance, untestable in December.

## Final verdict — February resists honest repair. No candidate.

All four pre-listed, ex-ante fix families are exhausted. The best
honest month table on Chandu's 25 remains the **base combined
book's: 9 of 10 months positive, +₹47,665.24 over Jan–Oct,
October +₹6,845.39 — with February −₹5,533.46.**

Why February cannot be honestly greened, in one paragraph: the
month's entire loss is 12 INV-LONG trades on **Feb 1–2** — the
Union Budget Sunday crash (−2.16%) and the next day's whipsaw —
taken by a below-trend long system whose deep-below-DMA entries
are, across the other nine months, its best earners (+₹20,247.65).
Every general rule that removes those 12 trades also removes good
trades in green months (MF-1 flips June; MF-4 flips October and
starves September; depth/ADR gates gut the system's paying
bands), and the two component swaps leave February red anyway.
The only patch that works is naming the two days — a date filter,
barred by the guards the fake-data failure produced. So it is
reported, not patched.

Secondary finding, stated for the record: **June is the base
book's fragile green** (+₹1,305.20, with INV-LONG's June slice
itself −₹1,772.32, carried by N4-V3 + P2F) — two of four fixes
flipped it. Any future change to this book must be stress-checked
against June first.

What stands unchanged: the combined book remains the best honest
book on his 25 (9/10 months green, both halves positive); its
components face November on their frozen terms (N4-V3 primary,
INV1 + P2F shadows). `stocks_M1_candidate_spec.md` is **not**
frozen — the user's every-month-positive bar is not met, and this
report is the deliverable that says so, with the evidence.

Files: `stocks_M1_frozen.md` (Parts A+B), `stocks_M1.py` (engine:
anchor | diagnose | fix), `stocks_M1_anchor.json`,
`stocks_M1_results.json` (base + all four fix month tables),
this report.

