# Bank v21 + S/R Rejection Layer — build & gate (2026-11-04)

**Chandu's direction (2026-11-04):** identify support/resistance price-action
rejection patterns and test adding them to Bank v21 "so we have something
solid." Paper only, real money ₹0, 1 lot (30), cost ₹220/trade. Bank Nifty
only — nothing pooled. The frozen v21 December candidate and all November
files are untouched; this produces a SEPARATE candidate if it passes.

Baseline: Bank v21 = **+₹83,650.50**, Jan–Oct 2026, 99 legs
(`bank_engine_r6_v21_trades.csv`; independently re-summed in this run —
exact).

---

## PRE-REGISTERED DEFINITIONS (written before any scoring; not tuned after)

### Levels (all causal — only data available at the time)
1. **Prior-day lines (PD):** prior trading day's high (PDH), low (PDL) and
   close (PDC) from the spot store. Usable from the 09:15 bar.
2. **Opening range (OR):** high/low of the bars starting 09:15–09:40
   (the 09:15–09:45 clock window). Usable for pattern bars starting
   ≥ 09:45.
3. **Intraday swings (SWING):** causal fractal on today's spot 5-min bars —
   a swing high at bar *t* requires bar *t*'s high strictly greater than
   the highs of bars *t−2, t−1, t+1, t+2*; it is confirmed at *t+2* and the
   level is usable only for pattern bars with index ≥ *t+3*. Mirror for
   swing lows. Swing levels live for the rest of the day.

A level's identity is **(price value, role)**: a swing high / a level
approached from below is a *resistance*; a swing low / a level approached
from above is a *support*. The same price can carry both roles (polarity);
each role is tested separately.

### Test and rejection (spot 5-min bars)
- **Resistance test** at level L on bar b: `b.high ≥ L − 5` AND `b.low < L`
  (the bar reaches within 5 spot points of L, or crosses it, approaching
  from below).
- **Support test** at level L on bar b: `b.low ≤ L + 5` AND `b.high > L`.
- **First test only:** the first bar that tests a (level, role) is that
  level's only chance that day. A pattern exists only if that first-test
  bar also rejects:
  - *Support rejection:* lower wick `min(open,close) − low` ≥ 50% of the
    bar's range (range > 0), close in the upper half
    (`close ≥ (high+low)/2`), and close above L.
  - *Resistance rejection:* upper wick `high − max(open,close)` ≥ 50% of
    range, close in the lower half, and close below L.

### Trade construction
- Entry: **next 5-min bar's open on the option premium** (pattern bar
  + 1; pattern bars whose next bar starts after 15:05 generate no trade).
  Support rejection → buy ATM **CE**; resistance rejection → buy ATM
  **PE**. ATM = strike nearest spot (spot open of the entry bar, 100-point
  grid), monthly expiry in force (`store_expiry_for` convention: first
  monthly expiry ≥ date among series with ≥10 chain days — the same
  series as v21's legs).
- Exits: v21's incumbent **G0**, for isolation — stop **−50**, target
  **+90**, premium-bar high/low, **stop checked before target** within a
  bar, entry bar included, fills at the level; square-off at the **15:10
  bar open**.
- Missing premium bars for a pattern leg → **NOT_COMPUTED**: counted and
  named, never estimated. An NC leg consumes one of the day's S/R slots.
- **Day guards:** max **2 S/R legs per day** (both tests). In the combined
  book (B), the standing **−₹3,000 day-loss cap**: an S/R leg is admitted
  only if the combined book's realised day P&L at its pattern bar (legs
  with exit_time ≤ pattern-bar time) is > −₹3,000. Cap-blocked legs are
  counted and do not consume a slot.
- **UNIQUE-ONCE in (B):** an S/R leg with the same (date, direction,
  entry_time) as a v21 leg — or as an earlier S/R leg — is the same trade:
  counted once (the v21 leg stands), removed before slot/cap processing.

### Tests
- **(A) STANDALONE:** S/R legs alone — total, legs, win rate, FT
  (full-target) rate, per-month table.
- **(B) ADDED BOOK:** v21's 99 legs + admitted S/R legs — combined total
  vs +₹83,650.50, and the **increment** = the admitted S/R legs' own P&L
  inside the combined book.

### Full gate (same run, before any number is quoted)
Timing audit (every level timestamped ≤ its pattern bar; swing
confirmations respected; entry premium == store open; independent second
implementation of pattern detection cross-checked event-for-event);
flipped-direction placebo; time-shifted placebo (+30 min); random-entry
placebo matched on count/month (single pre-fixed seed 20261104);
halves H1/H2; ex-top-3; worst drawdown; bleed legs (worst day, days
≤ −₹3,000, negative months); independent re-sum of the combined book
from the written CSVs.

### Verdict rule (pre-registered)
The layer is **ADDED** as a separate candidate ("v21 + S/R") only if the
(B) increment is **positive** AND passes the gate legs: **halves both
≥ −₹2,000, ex-top-3 positive, beats all placebos**. Otherwise it is
**REJECTED** and reported as such. No parameter iteration to rescue it.

---

---

## RESULTS (scored after the pre-registration above; definitions unchanged)

### Detection
- 205 trading days (2026-01-01 → 2026-10-30). **3,772 first tests** of
  (level, role) pairs; **569 first-test rejections** (pattern events):
  SWH 235 · SWL 238 · ORH 24 · ORL 22 · PDC 24 · PDH 11 · PDL 15.
- After UNIQUE-ONCE within the S/R set and the 2/day cap: **(A) 290
  scored legs + 48 NOT_COMPUTED** (338 slots used; 163 events over the
  daily cap; 68 duplicate events dropped). All 48 NCs are pre-10:00
  entry bars absent from the premium store for non-v21 strikes (the
  store's earlier backfill covered v21 strikes only) — counted, named in
  the results JSON, and slot-consuming in both tests, per the
  pre-registration.

### (A) STANDALONE — S/R rejection legs alone
| Metric | Value |
|---|---|
| Legs | 290 |
| **Total** | **−₹113,958.50** |
| Mean / leg | −₹392.96 |
| Win rate | 34.5% |
| FT (full-target) rate | 23.1% (67 targets / 165 stops / 58 square-offs) |
| Halves | H1 (Jan–May) −₹67,028.00 · H2 (Jun–Oct) −₹46,930.50 |
| Ex-top-3 legs | −₹121,398.50 |
| Worst day | −₹3,440.00 · days ≤ −₹3,000: 34 · worst drawdown −₹116,969.00 |
| Negative months | 9 of 10 (only Sep +₹211.00) |

Per month: Jan −₹11,494.00 · Feb −₹21,929.50 · Mar −₹11,320.00 ·
Apr −₹9,607.50 · May −₹12,677.00 · Jun −₹11,321.50 · Jul −₹14,535.50 ·
Aug −₹7,342.00 · Sep +₹211.00 · Oct −₹13,942.50.

### (B) ADDED BOOK — v21 + S/R
- S/R events: 70 dropped as UNIQUE-ONCE duplicates of v21/earlier S/R
  legs; **36 blocked by the −₹3,000 day-loss cap**; 136 over the 2/day
  cap; 48 NC (slot-consuming).
- **Increment (279 admitted legs): −₹120,238.50** — mean −₹430.96/leg,
  win 33.7%, FT 21.9%, halves −₹75,988.00 / −₹44,250.50,
  ex-top-3 −₹127,678.50, worst drawdown −₹123,249.00, 9 of 10 months
  negative.
- **Combined book: −₹36,588.00** vs v21 alone **+₹83,650.50**. Adding
  the layer turns v21's profitable book negative.

### Gate table (increment, test B — the population the verdict judges)
| Gate leg | S/R increment | Pass bar | Result |
|---|---|---|---|
| Total | −₹120,238.50 | > 0 | FAIL |
| Halves | −₹75,988.00 / −₹44,250.50 | both ≥ −₹2,000 | FAIL |
| Ex-top-3 | −₹127,678.50 | > 0 | FAIL |
| Flipped placebo | −₹66,763.50 | increment beats it | FAIL |
| Shifted +30 min placebo | −₹67,029.50 | increment beats it | FAIL |
| Random-entry placebo (seed 20261104) | −₹99,814.50 | increment beats it | FAIL |

Standalone (A) fails identically: −₹113,958.50 vs flipped −₹73,083.50,
shifted −₹67,429.50 (276 legs, 14 no-time), random −₹80,603.00.
**The rejection entries are worse than random entries on the same
days** — under G0 geometry (−50/+90), the first-test rejection bar is
more often a pause in the move through the level than a turn: 165 of
290 standalone legs stopped out.

### Anatomy by level source (standalone A; factual only — see verdict note)
| Source | Legs | Total |
|---|---|---|
| SWH (swing-high resistance) | 124 | −₹52,961.50 |
| SWL (swing-low support) | 131 | −₹51,063.50 |
| ORH | 9 | −₹9,798.00 |
| ORL | 14 | +₹12,104.50 |
| PDC | 4 | −₹6,880.00 |
| PDH | 2 | −₹3,440.00 |
| PDL | 6 | −₹1,920.00 |

The bleed is concentrated in the intraday swing levels (255 of 290
legs). ORL's small positive slice (14 legs) is **not** a candidate:
selecting it now would be subset-shopping against the pre-registration.

### Audits
- Timing audit: PASS — every event's level usable-time ≤ its pattern
  bar (swing confirmations at t+2, usable t+3 verified in code);
  entry = pattern bar + 1 for all 569 events; entry premium == store
  open on all 569 scored legs (A + B); all exits within [entry, 15:10].
- Detection cross-check: independent second implementation reproduces
  implementation 1 event-for-event on all 205 days (569/569).
- Manual end-to-end verification of one leg (2026-01-06, SWH 60,305.00):
  fractal strict at 10:15, confirmed 10:25, usable 10:30; first test at
  10:30 (high 60,301.35, within 5 pts; upper wick 26.70 ≥ 50% of range;
  close lower-half, below level); entry 10:35 PE @ 531.35 == store open;
  no bar touched the −50 stop; 14:35 high 628.00 ≥ target → +₹2,480.00.
  Exact.
- Independent re-sum from the written CSVs: PASS — combined −₹36,588.00
  = v21 ₹83,650.50 + increment −₹120,238.50, to the paisa.

## VERDICT — REJECTED

In plain words: **the S/R rejection layer, exactly as pre-registered,
loses money on its own (−₹113,958.50 standalone) and destroys v21 when
added (combined −₹36,588.00 vs +₹83,650.50). It fails every gate leg,
including against random entries. It is not added — there is no
"v21 + S/R" candidate.** Per the pre-registration, no parameters were
iterated to rescue it. v21 stands unchanged as the December candidate.

Files: `bank_sr_score.py` (scorer + gate), `bank_sr_standalone_trades.csv`
(290 legs), `bank_sr_combined_trades.csv` (378 rows: 99 v21 + 279
increment), `bank_sr_results.json` (full gate output, NC list,
cap-blocked list).
