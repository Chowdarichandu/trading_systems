# Bank Nifty SCALP Engine — PROTOCOL (frozen 2026-10-31, before any scoring)

User order 2026-10-31 21:30 IST: "Start recursive self improvement until we get what
we want — 1 min, 3 min, max holding time 5 mins, quick entry and exit."

## Scope (hard)
- **Bank Nifty ONLY.** Never Nifty, never stocks, never pooled.
- **Paper only. Real money ₹0.** Index options only.
- Basis: **option premiums per 1 lot (30)**, cost **₹220/trade** round trip.
- Separate from the Bank v8 book and from November paper BNF-PAPER-V1 — those files
  are never modified by this engine.

## Data-integrity gate (Phase 0 — passed 2026-10-31)
- Local premium data is 5-min only. **1-min bars are NEVER resampled, split,
  interpolated or simulated from 5-min data.** That would be fabrication.
- Genuine 1-min candles are fetched via the Upstox script-token route
  (browser fetch, `scalp_bulk_fetch.py`): spot/index via v3 `minutes/1`,
  expired option premiums via v2 `expired-instruments/historical-candle/{key}/1minute`.
  Proof window (2026-10-27) verified end-to-end; monthly probes verified Jan–Sep 2026.
- Store: `~/workspace/trading/scalp_1min_data/` (spot_1m_*.csv, options/{expiry}/opt_*.csv,
  fetch_manifest.json). **The scored window = days with genuine spot AND ATM premium
  coverage per the manifest. Every reported figure carries its window label.**
- 3-min decision bars are OHLC aggregations of three consecutive GENUINE 1-min bars
  of the same day (aligned 09:15, 09:18, …) — aggregation of genuine finer data,
  which is legitimate; the reverse (splitting coarser bars) is fabrication and banned.
- Spot VWAP family: index 1-min candles carry volume = 0 (an index does not trade),
  so spot VWAP is **not computable** — that family is skipped unless a genuine
  volume-bearing spot series appears. Option-premium VWAP is a different mechanism
  and must be proposed as its own cycle if used.

## Mechanics (frozen)
- Candle timestamps are bar START times. Index bars run 09:15…15:29.
- A signal is evaluated on a decision bar's CLOSE (the bar is fully known only then).
  A cycle states its decision timeframe: 1-min (native) or 3-min (aggregated).
- **Entry = open of the NEXT 1-min option candle after the signal bar closes.**
  (For a 3-min signal bar spanning [t, t+3), the next 1-min candle starts at t+3.)
- **Exits replay on 1-min premium candles** starting at the entry bar. Within any bar,
  **stop is checked before target** (conservative). Stop fills at the stop price,
  target fills at the target price.
- **HARD max hold = 5 minutes.** Holding window = entry bar E plus E+1…E+4 (five
  1-min bars). Stop/target are checked inside each of those bars. If neither is hit,
  exit at the **open of bar E+5** (the bar starting exactly 5 minutes after the entry
  bar's start). No trade may remain open beyond that.
- **Square-off:** last permitted entry bar start = 15:05 (so the 5-min window ends by
  the 15:10 bar open, where any residual exit would occur). Data after 15:29 is ignored.
- ATM = strike nearest 100 to spot at the signal-bar close. Expiry = expiry in force
  for the date (monthly list: 2026-01-27, 02-24, 03-30, 04-28, 05-26, 06-30, 07-28,
  08-25, 09-29, 10-27).
- Net per trade = (exit − entry premium) × 30 − ₹220.
- If the needed ATM premium series or any bar in the entry/exit window is missing,
  the trade is **NOT_COMPUTED** — excluded from all totals, counted and reported.
  Never estimated.
- **UNIQUE-ONCE** per (mechanism, date, direction, trigger key); across a multi-mechanism
  book, per (date, direction, entry bar) the earliest mechanism wins.
- **Per-day cap is part of every mechanism definition, ≤ 6 trades/day.** Frequency is
  a cost decision: at ₹220/trade, every trade must clear ₹220 ≈ 7.33 premium points
  of gross expectancy just to break even.

## Cycle loop (back-to-back, minutes not hours)
1. Diagnose the current best book's losers at path level (which bars, which exit type,
   what the premium path did inside the 5-min window).
2. Propose ONE new mechanism or ONE frozen fix — written in the log BEFORE scoring.
   Every cycle must engage with why the 5-min versions died (S1 gross ≈ 0 / cost;
   S2, S3 negative gross, placebo-beaten) and what the finer timeframe changes.
3. Score with **FULL CONTROLS IN THE SAME RUN** (no number is reported before they pass):
   - Timing/leak audit on EVERY trade: entry bar strictly after signal-bar end;
     hold ≤ 5 bars; exit ≥ entry. Violations must be 0.
   - Lag placebo: same signals, entry delayed +1 1-min bar, same exits.
   - Random placebo: count-matched random entries (random day/bar/direction, ATM,
     same exit geometry, same cost), 20 seeded draws (seed 42), mean + range.
   - Halves: first half vs second half of the scored window (by trading days).
   - Month table; ex-top-3 stress; independent re-sum from the written trade CSV.
4. **Banking gate:** bank only if the new book's total rises AND both halves ≥ ₹0
   AND it beats both placebos AND audit = 0 violations AND caps respected.
   Otherwise reject, record the lesson, increment consecutive_no_beat.

## Success gate ("what we want")
The frozen scalp book is: net positive after ₹220/trade in **BOTH halves** of the
scored window, beats both placebos, audit clean, and paces **≥ ₹5,000/month**
(premiums per 1 lot) over the scored window. → Freeze verbatim in
`bank_scalp_engine_frozen.md`, terminate SUCCESS.

## Termination
- **SUCCESS** (gate above), or
- **SATURATED** = 3 consecutive no-beat cycles, or
- **BLOCKED-DATA** = genuine 1-min premium coverage < ~2 months obtainable.
On termination: clear cycle_lock, set `terminated` in state with reason + final
window-labelled totals.

---
# ADDENDUM — DESIGN CHARTER v2 (user mandate 2026-10-31 21:42 IST)

Frozen into this protocol 2026-10-31 ~22:15 IST. **Supersedes the mechanics above
wherever they conflict.** Sequencing, stated honestly: Cycles 1 (OR1) and 2 (PV1)
were scored under Charter v1 mechanics (frozen before their scoring) before this
mandate arrived in-session. Both were REJECTED and **nothing was banked** — the book
is still empty, so no banking gate was breached. Cycles 1–2 stand as v1 evidence.
The saturation counter restarts under v2 because the charter orders a new variant
programme that has never been scored (every rung, both setups, both timeframes);
the v1 results and lessons remain in force as evidence.

## Charter mechanics
1. **HOLD:** strictly < 5 min — the frozen 5-minute hard cap and its exit convention stand.
2. **TARGET LADDER — separate frozen variants, never blended:** +2.5 / +10 / +12 /
   +15 / +20 premium points. Every rung is scored and reported separately, for every
   setup. Fixed stop for all ladder rungs: **−9 points**. 5-min time cap as frozen.
3. **TRAILING STOP variant (its own book entry):** initial stop −9; activation when
   a bar's high first reaches ≥ entry **+8**; trailing stop = running peak high − **5**,
   updated AFTER each bar's exit checks (the stop carried into a bar is the one that
   bar is tested against — no intra-bar peak lookahead); no fixed target; 5-min cap.
4. **RE-ENTRY:** after ANY exit, the same setup may re-trigger as a fresh event and
   re-enter — multiple entries/exits per day by design. UNIQUE-ONCE per
   (mechanism, date, direction, trigger bar/level): an event is never double-counted,
   but repeat events are new trades. **Per-day cap = 8 entries per mechanism** —
   frozen WHY: cost control; 8 × ₹220 = ₹1,760/day is the maximum cost drag a single
   mechanism may impose, and one position at a time per mechanism (flat-only
   re-entry: the next entry bar must be after the previous trade's exit bar).
5. **ENTRY SETUPS:** (a) opening-range micro-bursts; (b) level-rejection scalps on
   PDH/PDC/PDL + Red bands/ledges (Red data only from 2026-07-02 — stated wherever
   used; Jan–Jun runs on PDH/PDC/PDL only). Each scored on 1-min AND 3-min decision
   bars, stated per variant. Premium-velocity (PV1, scored under v1) remains a
   diagnosis-driven challenger candidate, not part of the base programme.
6. **COST ARITHMETIC, IN THE OPEN:** breakeven at 1 lot (30) with ₹220/trade =
   **7.33 premium points/trade** before any spread/slippage. The +2.5 rung grosses
   ₹75 against ₹220 cost. No cost assumption may be lowered; no rung may be dropped.
   If small rungs die on costs, that is a plain finding.
7. **DAY-LEVEL GATE:** every variant reports % of traded days ending net-green,
   median day, worst day, best day. A variant banks only if the v1 gate passes
   (total rises vs incumbent, both window-halves ≥ 0, beats lag + random placebos,
   audit clean) **AND** its days-green % ≥ the incumbent book's days-green %.
8. Adoption discipline unchanged: survivors are candidates only; fresh-data
   validation (December) judges adoption.

## Level-rejection definitions under the charter (frozen here)
- Levels per day from the PRIOR trading day's genuine 1-min spot: PDH, PDL, PDC.
  From 2026-07-02, Red master bands + tactical ledges add their high as resistance
  and low as support (red_bands_v2.json, causal per-date).
- 1-min: bar i, 20 ≤ i ≤ 340: resistance reject (→PE): high_i > L, close_{i−1} ≤ L,
  close_i ≤ L + (high_i − L)/2. Support reject (→CE): low_i < L, close_{i−1} ≥ L,
  close_i ≥ L − (L − low_i)/2. Same level: no re-trigger within 60 min.
- 3-min: spot aggregated to 3-min bars (09:15-aligned); identical rule on 3-min
  bars (approach from the previous 3-min bar's close); entry = first 1-min bar
  after the signal 3-min bar closes. Same 60-min level cooldown.
- OR micro-burst under the charter = the Cycle-1 OR1 signal definition (OR 09:15–
  09:29, fresh crosses, bars 15–255), with charter exits (ladder/trailing),
  charter re-entry (flat-only) and the 8/day cap replacing the v1 cap/spacing.

## Challenger families (seed list — invent more as diagnoses demand)
- F1: 1-min opening-range micro-burst (retimed S1).
- F2: 3-min level-rejection at PDH/PDL/PDC + Red bands (retimed S2; Red bands exist
  only from 2026-07-02 — stated wherever used).
- F3: 1-min impulse continuation (retimed S3).
- F4: Premium-velocity trigger — the ATM option premium's OWN 1-min momentum
  (a mechanism the 5-min study never had: trigger lives in premium space, not spot).
- F5: Spot VWAP snap-back — **BLOCKED at protocol level** (index volume = 0); skip.
