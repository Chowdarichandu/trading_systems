# MOVER-B4 — Controls + Peak Extension Report (Line B4)

Families frozen in `stocks_moverB4_frozen.md` BEFORE scoring.
Equity cash intraday, LONG/SHORT only, paper only, real money ₹0.
All figures provisional per 100 shares, net = gross − ₹40/trade.
Window Jan–Oct 2026 (Oct = 1–28). Pooled 50 primary.
Engine: `stocks_moverB4.py` (B2 machinery reused verbatim);
results: `stocks_moverB4_results.json`.

**Purpose:** the B-line's measurement slope never turned — net
rose at every scored step through 11:30. Before the B3
candidate's +₹1,623,905.15 is believed, this line tests what
actually causes the profit: the candidate's signal machinery
(discard-first, same-direction V5 signal, timed entries), or
simply the fact that stocks which moved ≥1% by late morning
keep drifting in that direction.

## Anchor validation — PASS

The B3 candidate configuration (measurement 11:30, threshold
1.0%, same-direction, cap 1, T125/S065) reproduced exactly
before any B4 family was scored: pooled 1,694 chains / 1,694
trades / **+₹1,623,905.15**, halves +₹951,573.84 /
+₹672,331.31, October +₹190,471.72, breadth 49/50, expectancy
+₹958.62/chain, max DD −₹11,557.03, no losing month; home
+₹489,399.84 (24/25), ext +₹1,134,505.31 (25/25).

## C1 — Extension: the slope does NOT turn — it steepens

B3 candidate configuration, measurement time only changed:

| Cell | Meas. | Chains | Net ₹ | JM ₹ | JO ₹ | Oct ₹ | Breadth | Exp/chain ₹ | Max DD ₹ | Losing months | Gate vs B3 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| B3 cand. | 11:30 | 1,694 | +1,623,905.15 | +951,573.84 | +672,331.31 | +190,471.72 | 49/50 | +958.62 | −11,557.03 | none | — |
| C1 | 12:00 | 1,875 | +2,102,533.26 | +1,207,782.73 | +894,750.53 | +224,588.31 | 50/50 | +1,121.35 | −10,992.87 | none | PASS |
| C1 | 12:30 | 1,977 | +2,313,430.85 | +1,259,539.42 | +1,053,891.43 | +262,346.47 | 50/50 | +1,170.17 | −4,279.60 | none | PASS |
| C1 | 13:00 | 2,169 | +2,590,570.38 | +1,400,052.49 | +1,190,517.89 | +329,597.43 | 50/50 | +1,194.36 | −9,259.72 | none | PASS |

Splits — 12:00: home +₹574,373.23 (25/25), ext +₹1,528,160.03
(25/25). 12:30: home +₹613,963.90 (25/25), ext +₹1,699,466.95
(25/25). 13:00: home +₹658,128.90 (25/25), ext +₹1,932,441.48
(25/25). Full month tables in `stocks_moverB4_results.json`
(no losing month in any cell).

**Read:** the slope NEVER turns. Net rises at every step —
11:30 → 12:00 (+29.5%) → 12:30 (+10.0%) → 13:00 (+12.0%) —
and so do chain count (1,694 → 2,169) and expectancy/chain
(+₹958.62 → +₹1,194.36). All three cells pass every leg of
the B-line gate against the B3 candidate. But a "measurement
time" whose later values keep winning, without limit, is not
a peak being approached — it is a symptom. Two candidate
explanations, which the controls below exist to separate:
(i) genuine midday drift — stocks that have moved ≥1% by
later in the day really do keep going; (ii) a structural
feature of the inherited machinery — qualification is measured
at the stated time, but the signal search runs over the WHOLE
day from the first bar, so entries are not restricted to
after the measurement time; the later the measurement, the
more of the day's path is "known" when the day is qualified,
while the entry can still sit anywhere in the day. C1 alone
cannot freeze a new candidate: per the frozen B4 rules, a C1
cell may only be frozen if C2/C3 do not undermine the
mechanism. The controls decide.

## C2 — Fixed-time control: captures NONE of the profit

On the identical qualifying stock-days (pre-move at 11:30
≥ 1.0%; 1,956 stock-days pooled), the signal stream was
ignored and every qualifying day was traded once: entry at
11:35 (open of the first bar after 11:30) in the pre-move's
direction, exits T125/S065.

| Set | Days | Net ₹ | Exp/day ₹ |
|---|---|---|---|
| Control — ALL qualifying days | 1,956 | **−188,980.02** | −96.62 |
| Candidate — same day set (untraded days = ₹0) | 1,956 | +1,623,905.15 | +830.22 |
| Control — restricted to the 1,694 days the candidate traded | 1,694 | −119,811.61 | −70.72 |
| Candidate — those same 1,694 days | 1,694 | +1,623,905.15 | +958.62 |

Splits: home control −₹62,148.11 over 1,162 qualifying days
(candidate +₹489,399.84 on 982 of them; control on those 982
days −₹24,205.88). Ext control −₹126,831.91 over 794
qualifying days (candidate +₹1,134,505.31 on 712; control on
those 712 days −₹95,605.73). The control as a standalone book:
breadth 17/50, seven losing months, max DD −₹240,566.54,
October −₹37,357.38.

**Verdict on C2: the "big morning moves keep drifting"
hypothesis is REFUTED as the explanation of the candidate.**
Entering every big-morning-move stock at a fixed 11:35 in the
move's direction, with the candidate's own exits, loses money
in both halves (Jan–May −₹17,727.29 / Jun–Oct −₹171,252.73)
and on the very days the candidate traded. The candidate's
profit is therefore NOT the drift of qualifying days in
general: it depends on *which* qualifying days get traded and
*when and in which direction* the entry happens — i.e. on the
signal machinery's selection, not on the qualification alone.
One confound remains, and C4 addresses it: the candidate's
machinery searches signals over the whole day, so some of its
entries may sit before the 11:30 measurement that qualified
the day.

## C3 — Placebo (yesterday's move): collapses completely

The candidate's exact intraday machinery — discard first
signal, trade the next signal agreeing with the reference
direction, cap 1, T125/S065 — but qualified and directed by
**yesterday's** full-day move (≥1.0%, known at today's open)
instead of today's pre-move:

| Set | Qual. days | Chains | Net ₹ | Exp/chain ₹ | JM ₹ | JO ₹ | Breadth |
|---|---|---|---|---|---|---|---|
| Placebo home | 2,680 | 1,264 | −71,479.72 | −56.55 | −42,281.77 | −29,197.95 | 7/25 |
| Placebo ext | 2,259 | 1,046 | −150,905.78 | −144.27 | −49,428.04 | −101,477.74 | 8/25 |
| **Placebo pooled** | **4,939** | **2,310** | **−222,385.50** | **−96.27** | **−91,709.81** | **−130,675.69** | **15/50** |

Pooled max DD −₹287,388.67; seven losing months (October
alone was positive, +₹38,607.52). The placebo earns −13.7%
of the candidate's net — i.e. it loses money at roughly the
mirror rate.

**Verdict on C3:** the machinery is NOT harvesting a generic
volatile-stock/day selection effect. Fed the same signals on
days selected by a big move that is fully known in advance
(yesterday's), it loses in both halves on both universes.
Whatever the candidate exploits is specific to *today's*
move being the qualifier — which is exactly what a genuine
intraday-confirmation effect would predict, and also exactly
what a look-ahead structure would predict. C4 separates
those two readings.

## C4 — Signal-value decomposition: the money is made BEFORE the measurement

The B3 candidate's own 1,694 chains, split by entry time
(frozen buckets):

| Bucket | Chains | Net ₹ | Exp/chain ₹ | Win % | Share of net |
|---|---|---|---|---|---|
| (a) Entry before 12:30 | 1,673 | +1,625,949.51 | +971.88 | 71.2 | 100.1% |
| (b) Entry 12:30–14:00 | 16 | −3,244.67 | −202.79 | 56.2 | −0.2% |
| (c) Entry after 14:00 | 5 | +1,200.31 | +240.06 | 80.0 | +0.1% |

The candidate is a morning strategy: essentially all of its
profit sits in entries before 12:30, and the afternoon
buckets are scratch. That alone is innocent — the strategy
is called Morning-Mover. The decisive cut is finer, against
the candidate's own measurement time (read from the
candidate's dumped trades, `moverB2_B4_BASE_trades.csv` —
a decomposition of the same frozen chains, not a new family):

| Entry time | Chains | Net ₹ | Exp/chain ₹ | Share of net |
|---|---|---|---|---|
| Before 11:00 | 1,490 | +1,562,467.58 | +1,048.64 | 96.2% |
| 11:00–11:30 | 147 | +50,856.72 | +345.96 | 3.1% |
| **Subtotal: before the 11:30 measurement completes** | **1,637** | **+1,613,324.30** | **+985.53** | **99.3%** |
| 11:30–12:30 | 36 | +12,625.21 | +350.70 | 0.8% |
| 12:30–14:00 | 16 | −3,244.67 | −202.79 | −0.2% |
| After 14:00 | 5 | +1,200.31 | +240.06 | 0.1% |
| **Subtotal: at/after 11:30 (real-time knowable)** | **57** | **+10,580.85** | **+185.63** | **0.7%** |

**This is the finding of the line.** 96.6% of the
candidate's chains — carrying 99.3% of its net — were entered
*before* the 11:30 measurement that qualifies the stock-day
was complete. At the moment those entries were made, nobody
could know the stock would finish the morning ≥1% moved; the
backtest knows, because it qualifies the day on the full
11:30 pre-move and then reaches back into the morning for a
same-direction signal. That is a look-ahead structure, and
it explains every other result in this line:

- **C1's endless slope:** the later the measurement, the
  larger and more certain the already-known morning move,
  and the more reliably the machine can reach back and pick
  the morning signal that rode it. A slope that never turns
  is the fingerprint of this leak, not of a tradable midday
  drift.
- **C2's failure:** entered honestly — after the measurement,
  at a fixed time, in the move's direction — the same
  qualifying days lose ₹188,980.02. The post-measurement
  drift the candidate appears to harvest is not there.
- **C3's failure:** the same reach-back machinery, qualified
  by information that genuinely is known in advance
  (yesterday's move), loses ₹222,385.50. Reach-back plus
  signal selection alone earns nothing; only reach-back
  *plus a qualifier measured after the entries* earns.

## Overall mechanism verdict

**The B3 candidate is DOWNGRADED to UNPROVEN-MECHANISM.**

Stated plainly: as frozen, the B3 candidate cannot be traded
as specified in real time. Its rules qualify a stock-day
using the move through 11:30, but 99.3% of its in-sample
profit comes from entries placed before 11:30 — entries a
live trader could not have known to take. The in-sample
+₹1,623,905.15 is therefore an artefact of look-ahead
selection inside the inherited machinery (the signal search
runs over the whole day regardless of measurement time), not
evidence of a tradable edge. The C1 extension cells (12:00 /
12:30 / 13:00) all pass the arithmetic B-line gate, but per
the frozen B4 rules **no C1 candidate is frozen**: the
controls undermine the mechanism, and the same leak — larger,
not smaller — is what makes the later cells score higher.

The December fresh-window judging written into the B3
candidate spec cannot rescue this as written: run as an
after-close reconstruction it would "pass" by construction
of the same leak; run in real time, its early entries cannot
be taken at all. Any future version of this idea must, at
minimum, restrict entries to at or after the measurement
time — a different rule, requiring its own frozen line and
its own fresh window. (What such a restricted rule would
earn is indicated, though not measured as a candidate, by
the at/after-11:30 slice above: 57 chains, +₹10,580.85 over
ten months — near scratch.)

Scope note: this line scored the B3 candidate (11:30). The
same whole-day signal search exists in the earlier B-line
configurations (10:00 / 10:15 / 10:30, including November's
frozen A/B shadows) with proportionally shorter reach-back
windows; quantifying their pre-measurement profit share was
outside this line's frozen scope, but their fresh results
should be read knowing the question applies to them too.
Nothing in this line changes any November shadow.
