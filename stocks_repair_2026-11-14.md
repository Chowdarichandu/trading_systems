# STOCKS REPAIR — ANATOMY + GATE · 2026-11-14

**Owner order (2026-11-14 12:08 IST): Bank Nifty, Nifty and Stocks
individually, each with repair and confidence lines.** The Stock Book
has never had a repair — the anatomy step that produced B-FIX-1
(Bank) and N-FIX-1 (Nifty) was never run on it. This run mirrors
`november_books_fix_2026-11-14.md`'s method: anatomy on stored legs,
freeze, gate, November reported as description only.

**Real money: ₹0 throughout. Paper only. Every figure: equity cash
intraday, per 100 shares PROVISIONAL, ₹40/trade inside every net.**
Years are judged SEPARATELY — stocks are never pooled for a verdict
(pooled figures below are anatomy description only). Research only —
no book, ledger, or job changed.

Method files: `stocks_repair_anatomy.py` / `stocks_repair_anatomy.json`
(Step 1) · `stocks_repair_SPEC.md` (freeze) · `stocks_repair_gate.py`
(Step 2) · `stocks_repair_results.json` (all numbers).

## CONTROL (reproduced exactly before anything else)

Gated store `stocks_engine_adoptedC_book{2025,2026}_trades.csv`,
Jan–Oct only:
- **2025: 1,064 legs · +₹119,813.44 · WR 45.39% · red months Jul
  (−₹660.91), Oct (−₹4,042.67) · halves +₹98,541.87 / +₹21,271.57**
- **2026: 1,363 legs · +₹247,178.79 · WR 44.75% · ZERO red months ·
  halves +₹149,410.01 / +₹97,768.78**
- November actual (paper log, Nov 2–13): **+₹7,517.94 · 32 trades**

## STEP 1 — ANATOMY (Jan–Oct stored legs)

Dimension audit: the gated store carries **component × side ×
entry-time bucket** — that is all a rule may slice on. Buckets:
**B1 ≤09:35** (open wave) · **B2 09:40–10:25** · **B3 ≥10:30**
(second wave; this book enters almost entirely before 11:00, so the
index books' buckets do not apply). **Dropped, stated:** prior-day-move
band (not in the store; per-stock daily bars cannot uniformly
reconstruct it across both years — the confidence run's ruling) and
price band (entry price not in the gated store; the partial store
carrying it joins only 39% of legs). Exit class is not knowable at
entry — never sliced for a rule.

### The headline: there is NO both-years rotten cell

At the screen (≥15 legs in a year or ≥25 pooled, net-negative
somewhere, ex-top-3 also negative), **not one cell is negative in
both years.** Every sizable losing cell flips sign across the years:

| Cell | 2025 | 2026 | Read |
|---|---:|---:|---|
| REXP (whole comp, all SHORT × B2) | 41 legs **+₹14,870.39** (WR 46.3%) | 86 legs **−₹8,399.33** (WR 24.4%, ex-top-3 −₹15,551.46) | The biggest single-year hole in the book — and the mirror of its own 2025 |
| F4 × SHORT | 110 legs **−₹5,090.70** (ex-top-3 −₹13,906.95) | 183 legs **+₹55,706.05** (WR 55.2%) | 2025's loser is 2026's engine |
| F4 (whole comp) | 246 legs +₹91.14 | 355 legs **+₹103,055.93** | The book's centre of gravity moved, it did not rot |
| GAP-FADE | 112 legs +₹32,064.93 (WR 56.3%) | 292 legs +₹4,270.42 (WR 29.1%) | Decayed hard in 2026 — but still positive |
| INV-ABOVE × B1 ≤09:35 | 30 legs **−₹4,100.03** (WR 33.3%, ex-top-3 −₹10,764.68) | 4 legs +₹2,572.66 | Candidate S-FIX-1 |
| INV-LONG × B1 ≤09:35 | 55 legs **−₹2,635.88** (WR 38.2%, ex-top-3 −₹8,296.70) | 30 legs +₹1,289.99 (WR 30.0%, ex-top-3 −₹7,477.50) | Candidate S-FIX-2 |

Both sides earn in both years (LONG +₹93,778.30 / +₹147,858.37;
SHORT +₹26,035.14 / +₹99,320.42) and all three entry buckets earn in
both years. The neighbours of the two candidate cells thrive:
INV-ABOVE × B2 in 2025 = +₹20,345.47/77 legs; INV-LONG × B2 in 2025 =
+₹19,910.23/179 legs. The only pooled-negative cells in the entire
cross are the two INV open-wave cells above — **−₹1,527.37 (34 legs)
and −₹1,345.89 (85 legs) pooled, i.e. ~0.4% of the book's pooled
+₹366,992.23.** Compare the index books: B-FIX-1's cell was
−₹4,158.50 on a +₹127,351.50 book (3.3%); N-FIX-1's was −₹14,119.75
on +₹103,050.25 (13.7%). The Stock Book has no equivalent hole.

REXP and F4 × SHORT were named in the frozen spec and NOT made
candidates: each fails the cross-year gate leg by inspection (REXP
skip degrades 2025 by 12.4%; F4 × SHORT skip degrades 2026 by
22.5%). The two slots went to the only pooled-negative cells.

## STEP 2 — FREEZE + GATE

Spec frozen in `stocks_repair_SPEC.md` after anatomy, before gate
scoring: at most two candidates, each a single mechanical skip rule;
gate per year — (a) improve ≥1 year, other year degrade ≤2%;
(b) no new red month; (c) beat ≥95% of 200 random same-size skip-sets
in each improved year (placebo, seeds 2000–2199); (d) no half of any
year drops by more than 2% of that year's raw total; (e) November
descriptive.

### S-FIX-1 — skip INV-ABOVE legs entered ≤09:35 — **FAIL (leg c)**

| Gate leg | 2025 | 2026 |
|---|---|---|
| Skipped | 30 legs, −₹4,100.03 | 4 legs, +₹2,572.66 |
| Repaired total | **₹123,913.47** (+₹4,100.03) | ₹244,606.13 (−₹2,572.66 = −1.04%) |
| (a) Cross-year | improves | degrades 1.04% ≤ 2% — **PASS** |
| (b) New red months | none (Jul actually flips green, +₹1,180.21) | none — **PASS** |
| (c) Placebo | beats **91.0%** of 200 random 30-leg skips — **FAIL** (bar 95%) | n/a (not an improved year) |
| (d) Halves | +₹99,941.58 / +₹23,971.89 (both halves UP) | H1 −₹2,572.66 within ₹4,943.58 tolerance, H2 unchanged — **PASS** |
| Repaired WR | 45.74% (raw 45.39%) | 44.67% (raw 44.75%) |

November (descriptive): the rule skips 4 of the 32 trades — Nov 4
HINDCOPPER +₹460.12, Nov 6 GLENMARK **+₹3,068.25**, Nov 6 RECLTD
+₹330.31, Nov 9 GLENMARK −₹1,369.00 — skipped net **+₹2,489.68**,
so repaired November = **+₹5,028.26, worse than the actual
+₹7,517.94.** In November the "rotten cell" dealt three winners
against one loser.

### S-FIX-2 — skip INV-LONG legs entered ≤09:35 — **FAIL (leg c)**

| Gate leg | 2025 | 2026 |
|---|---|---|
| Skipped | 55 legs, −₹2,635.88 | 30 legs, +₹1,289.99 |
| Repaired total | **₹122,449.32** (+₹2,635.88) | ₹245,888.80 (−₹1,289.99 = −0.52%) |
| (a) Cross-year | improves | degrades 0.52% ≤ 2% — **PASS** |
| (b) New red months | none | none — **PASS** |
| (c) Placebo | beats **89.0%** of 200 random 55-leg skips — **FAIL** (bar 95%) | n/a |
| (d) Halves | +₹101,177.75 / +₹21,271.57 (H1 up, H2 unchanged) | H1 +₹1,759.44, H2 −₹3,049.43 within tolerance — **PASS** |
| Repaired WR | 45.79% | 45.09% |

November (descriptive): skips 1 trade — Nov 2 HINDCOPPER +₹465.19 —
repaired November = **+₹7,052.75, worse than actual.**

### Why the placebo is the honest killer here

Both candidates pass every structural leg and fail only the
placebo — the same leg that proved B-FIX-1 (200/200) and N-FIX-1
(199/200). The reason is arithmetic, not bad luck: the 2025 book
averages +₹112.61 per leg, so randomly skipping 30–55 legs already
"improves" the year most of the time, and these cells lose only
−₹136.67/leg (S-FIX-1) and −₹47.93/leg (S-FIX-2). The index cells
lost −₹244.62/leg (Bank) and −₹1,764.97/leg (Nifty) against books
averaging far more per leg — that is what separation looks like.
Here, the cells' per-leg bleed is inside the book's ordinary noise:
**not distinguishable from skipping trades at random.** Per the
frozen spec, no third candidate is tried in this run.

## VERDICT

**No repair is adopted for the Stock Book.** Both frozen candidates
FAIL on the placebo leg. The three-lines table therefore carries
S-FIX-1 (the larger pooled improvement, +₹1,527.37 vs +₹1,345.89)
in its "+ REPAIR" column, labelled FAILED — the owner asked for the
comparison visible either way.

**Honest bottom line:** the Stock Book does not have a rotten cell
like the index books did. It bleeds evenly and rotationally: the
component that loses in one year is the one that pays in the other
(REXP +₹14,870 → −₹8,399; F4 × SHORT −₹5,091 → +₹55,706), no
entry-knowable cell is negative in both years, and the worst pooled
cell is 0.4% of the book — inside random noise by the placebo's own
measurement. B-FIX-1 and N-FIX-1 existed because those books each
had one narrow, deep, one-signed hole; this book's losses are the
ordinary toll of a ~45%-win-rate payoff book, spread across
everything it does. **The Stock Book stands unchanged.**
