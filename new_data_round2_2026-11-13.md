# NEW-DATA INVENTION — ROUND 2 (2026-11-13 night)

**Owner order 2026-11-13 20:23 IST: "run again — now."** Round 1
(day-level OI quadrants V1/V2/V3) closed tonight with every variant
failing its gate; those variants are NOT retested here. This round
invents from two NEW data surfaces the candle books have never read —
**Bank Nifty futures basis** and **India VIX** — both historically
available for Jan–Oct 2026, so they are gated NOW, not in December.
**Paper only, real money ₹0 — no live trades were placed.** Index
figures are option premiums per 1 lot (Bank lot 30), cost ₹220/trade,
UNIQUE-ONCE. Incumbent for every merge: **TUNED STACK v2** — 111 legs,
**+₹127,351.50** Jan–Oct, 89 trade-days, **₹1,430.92/trade-day**
(anchor re-verified in `bank_900_tradeday_2026-11-13.md`). Spot and
futures are signal data only — the traded instrument is always Bank
Nifty options, 1 lot, buying only. No running book, job, or ledger is
touched by this round.

---

## PART 1 — DATA (built and audited BEFORE any family was frozen or scored)

Builder: `round2_data_build.py` · datasets: `round2_history/`
(`banknifty_basis_daily.csv`, `india_vix_daily.csv`, per-contract
futures series `FUT_<expiry>.json`, `futures_keys.json`,
`build_manifest.json`, `nov12_supplementary.json`).

### Surface A — futures basis

- **Construction:** for each trading day D, the in-force near-month
  BANKNIFTY futures contract (the monthly expiry of the OI dataset's
  own convention — first monthly expiry ≥ D; verified **0 mismatches**
  against the dataset's expiry column on all 220 built days) — futures
  daily close from the Upstox expired-instruments route
  (`/v2/expired-instruments/future/contract` + `historical-candle/day`;
  the live 2026-11-23 contract via the public NSE instruments dump +
  v3 days route). Spot close = last bar of the stored 5-min spot
  series — verified **identical to the OI dataset's spot_close on
  every overlapping day (0 days differ by > 0.01)**.
  basis_pts = futures close − spot close; basis_pct = basis_pts /
  spot close × 100.
- **Coverage: COMPLETE.** 205/205 Jan–Oct trading days have a futures
  close — **zero missing days** (the series runs 2025-12-22 →
  2026-11-11, 220 rows, plus the Nov 12 supplementary row below).
- **Timing audit:** every field of row D is a day-D *close* (futures
  daily candle, spot last bar). A signal read from row D is knowable
  only after D's close and is traded on D+1 — 0 look-ahead by
  construction; the scorer additionally asserts signal_date <
  trade_date on every trade.
- **Two structural artefacts found in the raw series, and the frozen
  handling for each (decided from the signal variable's structure,
  before any trade was scored):**
  1. **Carry decay dominates the basis LEVEL.** Early in a contract's
     life the basis sits at +0.2…+0.49% and decays toward zero into
     expiry (textbook cost-of-carry). A fixed level threshold would
     mostly encode "days since roll", not positioning. Consequence:
     the level family (A2) is defined on the basis's deviation from
     **its own contract's trailing norm** (z-score, Part 2), never on
     the raw level.
  2. **Expiry-day basis prints are not converged** (e.g. 2026-01-27:
     −208.65 pts — futures lagging a violent closing rally in the
     official daily candles). Consequence: the frozen **roll rule** —
     no A-family signal is emitted when the in-force contract expires
     within the next 2 trading days, and every day-over-day basis
     change is computed **only between two closes of the same
     contract** (a contract change makes the change undefined, never
     differenced across the roll).

### Surface B — India VIX

- **Construction:** published India VIX daily close. NSE's historical
  VIX endpoint returned HTTP 403 tonight (recorded in the manifest);
  the series used is **Yahoo Finance `^INDIAVIX`** (public historical
  series), single-source, with these audits passed: every value lies
  in the plausible 2026 range (min 9.15, max 27.89); dates align to
  the trading calendar with **no weekend rows**; coverage below.
  (Round 1's OI dataset enjoyed an exact second-source cross-check;
  VIX has none tonight and the report says so plainly.)
- **Coverage:** 203 of 205 Jan–Oct trading days carry a VIX close.
  Missing: **2026-01-01** and **2026-02-01** (the Sunday Budget
  special session — the US-centric feed skipped both). A signal day
  whose own or prior day's VIX is missing emits **no signal** (the
  same missing-data discipline as round 1's partial OI days) — this
  silences B-family signals on Jan 1, Jan 2, Feb 1 and Feb 2 only.
  Disclosed, never backfilled.
- **Timing audit:** the VIX close of day D is published after D's
  close; signals trade D+1; the scorer asserts signal_date <
  trade_date on every trade.

### November supplementary row (signal day Nov 12 → trade day Nov 13)

The stored 5-min spot calendar ends Nov 11, so — exactly as round 1 —
the main November lens runs on signal days through Nov 11, and Nov 12
is a **labelled supplementary** read: spot close 61,518.50 (official
index daily candle), Nov-23 futures close 61,337.60 → **basis
−180.90 pts (−0.2941%)**; **VIX close 16.62**. Nov 13 is a stack-busy
day, so any Nov-13 family leg is excluded from every merged figure by
the increment rule regardless; the leg itself is scored if real
premium candles exist and reported NC if they do not (round 1 found
them unserved), never estimated.

---

## PART 2 — THE FROZEN FAMILIES (written and frozen BEFORE scoring)

**Common trade construction (all standalone families):** signal at
the close of day D from Part 1 data only; ONE leg on the next trading
day D+1; entry = **open of the 09:20 5-minute bar**; strike = ATM
(nearest 100) to that bar's spot open; contract = the in-force
monthly expiry of the trade day; exits = **G0** (stop −50 checked
before target +90 on every bar including the entry bar, fills at the
level, square-off at the 15:10 bar close; lot 30); cost ₹220/trade.
Buying only.

**A1 — BASIS-EXPANSION CONTINUATION (Surface A, primary).**
Δbasis_D = basis_pct_D − basis_pct_{D−1}, defined only when the same
contract is in force on both days. If Δbasis_D ≥ **+0.05** (futures
premium expanding — aggressive futures length building) → buy **CE**
on D+1. If Δbasis_D ≤ **−0.05** → buy **PE** on D+1. Otherwise no
trade. No signal when the in-force contract expires within the next
2 trading days (Part 1 roll rule).

**A2 — BASIS-EXTREME REVERSAL (Surface A, variant).**
For signal day D, z_D = (basis_pct_D − mean) / std of basis_pct over
the **same in-force contract's prior in-force trading days** (at most
the last 15, at least 8 required — fewer means no signal; the window
never crosses a roll and never includes day D). If z_D ≥ **+1.5**
(premium far above this contract's own norm — crowded futures length)
→ buy **PE** on D+1. If z_D ≤ **−1.5** → buy **CE** on D+1. Same roll
rule as A1.

**B1 — VIX-SPIKE REVERSAL (Surface B, primary).**
ΔVIX_D = (VIX_D − VIX_{D−1}) / VIX_{D−1} over consecutive trading
days of the Part 1 calendar. If ΔVIX_D ≥ **+8%** (a one-day fear
expansion) → buy on D+1 the side **opposite** day D's spot direction:
spot down on D → **CE**; spot up on D → **PE**. Spot unchanged on D,
or ΔVIX < +8%, or either VIX missing → no trade.

**B2 — VIX-REGIME PERMISSION OVERLAY (Surface B, variant).**
Not a standalone book — a permission rule on the incumbent itself.
Book = TUNED STACK v2's 111 Jan–Oct legs, each leg's net taken
verbatim from the verified stack ledger. A leg with trade date T is
**KEPT iff VIX close on the last trading day before T ≤ 20.00**
(the fear regime is removed; the failure audit's hostile patch was a
high-range reversal regime). If VIX_{T−1} is missing, the leg is KEPT
(the overlay removes legs only on positive evidence of the fear
regime — stated here, before scoring). B2's gate is its own (below);
its November read applies the identical rule to the stack's four
logged November legs.

**Gate — standalone families A1 / A2 / B1 (standing controls gate,
Jan–Oct 2026 by trade date, identical to round 1):** (1) total > 0;
(2) both halves (Jan–May, Jun–Oct) > 0; (3) ex-top-3 > 0; (4) total
strictly beats all three placebos — **REVERSED** direction,
**COIN-FLIP** direction (seed 42), **SHIFTED** signal (the family's
signal computed from the trading day *before* the signal day, same
trade-day loop); (5) timing audit 0 violations; (6) NC ≤ 5% of signal
days (NC = a fired signal whose trade could not be scored from real
candles — excluded, never estimated). Independent re-sum of the trade
file must match to the paisa.

**Gate — B2 overlay:** PASS requires ALL of: kept total > stack total
(+₹127,351.50); kept ₹/trade-day > the stack's ₹1,430.92; kept halves
> 0; kept ex-top-3 > 0; kept total strictly beats its three placebos
(REVERSED rule — keep iff VIX_{T−1} > 20; COIN — a random same-count
subset of the 111 legs, seed 42; SHIFTED — the rule read off
VIX_{T−2}). An overlay that merely raises the average by dropping
net-positive legs FAILS on the total leg by construction — that is
the PB-subset trap, fenced here in advance.

**Merge protocol (registered, identical to round 1):** for any
standalone family that PASSES its gate — or, if none passes, for the
single strongest failing standalone family (highest Jan–Oct total;
merge-only evidence, labelled as such) — INCREMENT = the family's
legs on days TUNED STACK v2 placed no leg; merged = stack legs +
increment legs, UNIQUE-ONCE by construction (disjoint day sets). The
merge PASSES only if (i) the increment alone is net positive and
(ii) the merged total beats the stack alone; the merged
₹/trade-day is stated beside ₹1,430.92 and the merged month table
with red months named. **November counterfactual:** merged November
= the stack's logged November legs (Nov 4 +₹2,480 · Nov 9 −₹1,720 ·
Nov 12 −₹1,720 · Nov 13 −₹1,720 = **−₹2,680**) + the family's
November legs on stack-idle days (idle: Nov 2, 3, 5, 6, 11), each leg
listed; the Nov-13 supplementary leg is reported separately and
never counted in a merged figure.

**Owner's lens (not a gate leg):** any PASS is also stated as
₹/trade-day against the owner's ₹900 bar. Bars never move mid-run; a
failed variant is never retested identically.

Scorer: `round2_score.py` · trades: `round2_trades.csv` ·
results: `new_data_round2_results.json`.

---

## PART 3 — GATE RESULTS

<!-- RESULTS:GATE -->
**GATE — BANK NIFTY, Jan–Oct 2026 (run 2026-11-13 night;
`round2_score.py` on round 1's frozen machinery; timing violations = 0
for every book; independent re-sum EXACT for every book). Paper only,
real money ₹0. Premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE.**

| Family | Trades | Total | H1 (Jan–May) | H2 (Jun–Oct) | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| A1 BASIS-EXPANSION | 106 | **−₹56,152.00** | −₹27,274.50 | −₹28,877.50 | −₹63,592.00 | −₹5,615.20 | −18,458.50 / −52,925.50 / −18,581.50 | **FAIL — every leg** |
| A2 BASIS-EXTREME (z) | 30 | **−₹7,779.00** | −₹7,379.00 | −₹400.00 | −₹15,219.00 | −₹777.90 | −7,954.50 / −13,800.00 / −26,400.00 (beats all 3) | **FAIL — total, halves, ex-top-3** |
| B1 VIX-SPIKE REVERSAL | 22 | **−₹4,240.00** | +₹1,120.00 | −₹5,360.00 | −₹11,680.00 | −₹424.00 | −8,440.00 / **+4,160.00** / −8,440.00 | **FAIL — total, halves flip, ex-top-3, coin placebo** |
| B2 VIX OVERLAY (on stack) | 92 kept / 111 | **+₹118,031.50** kept | +₹73,762.00 | +₹44,269.50 | +₹91,208.50 | — | +9,320.00 / +101,617.00 / +113,611.50 (beats all 3) | **FAIL — kept total < stack total (₹127,351.50)** |

Month tables (₹). A1 — Jan −1,160 · Feb −6,394.50 · Mar −13,960 ·
Apr −200 · May −5,560 · Jun −11,280 · Jul −5,360 · Aug −9,760 ·
Sep −6,277.50 · Oct **+3,800** (nine red months of ten).
A2 — Jan −3,440 · Feb −8,499 · Mar +560 · Apr +3,240 · May +760 ·
Jun +2,280 · Jul +760 · Aug 0 (no trades) · Sep 0 (no trades) ·
Oct −3,440.
B1 — Jan +2,480 · Feb +4,960 · Mar −5,360 · Apr +760 · May −1,720 ·
Jun −3,440 · Jul +760 · Aug 0 (no trades) · Sep −5,160 · Oct +2,480.
B2 kept book — Jan +24,028 · Feb +15,284 · Mar **−960** · Apr +10,010 ·
May +25,400 · Jun +3,040 · Jul +4,224 · Aug +2,059.50 · Sep +15,056.50 ·
Oct +19,889.50 (the overlay *creates* a red March: the stack's own
March is +₹8,560).

**NC accounting:** A1 and B1 each carry NC = 1, and it sits in the
November lens, not the gate window (signal day Nov 6 → trade day
Nov 8, the 14-bar fragment day, which has no 09:20 spot bar — the
same fragment round 1 flagged). Gate-window NC = 0 for all three
standalone families; A2 NC = 0 everywhere.

**Reading, per family:**
- **A1 is anti-predictive, not merely weak.** It loses in both halves
  and to *all three* placebos — the reversed control (trade against
  the basis expansion) loses ₹37,693.50 *less*. In 2026, a one-day
  expansion of the futures premium was a fade, not a continuation.
  The reversed control is itself deeply negative (−₹18,458.50, both
  halves red) — recorded as evidence against the family and fenced,
  exactly as round 1 fenced Nifty's reversed OI placebo: it was never
  frozen as a candidate, and adopting it post-hoc is the data-mining
  the gate exists to prevent.
- **A2's reversal read is real but too small.** It beats reversed,
  coin and shifted controls — the z-extreme fade loses less than
  chance — yet it still loses in both halves and its ex-top-3 is
  −₹15,219 on only 30 trades. "Loses less than chance" is not an
  edge, the same sentence round 1 wrote about OI V1.
- **B1's own days convict it.** On the 22 spike days, a coin flip
  made +₹4,160 while the frozen reversal rule lost −₹4,240; the
  halves flip (+₹1,120 → −₹5,360) and the ex-top-3 is −₹11,680.
  Fear-spike fading at the next morning's open does not pay under G0.
- **B2 is the PB-subset trap, caught by its own fence.** Dropping the
  19 stack legs whose prior-day VIX exceeded 20 *raises* the average
  (₹1,532.88/trade-day vs the stack's ₹1,430.92) and passes halves,
  ex-top-3 and all three placebos — but those 19 legs are net
  **+₹9,320.00**, so the kept book makes *less money*
  (₹118,031.50 < ₹127,351.50) and turns March red. The frozen gate
  fails it on the total leg, as designed. The honest residue is an
  observation *against* the overlay's premise: in Jan–Oct the stack
  earned on fear-regime days, it did not bleed on them. (One stack
  leg, 2026-02-02, had a missing prior-day VIX — the Budget-session
  gap — and was kept under the frozen default-allow rule, disclosed
  here as registered.)

## PART 4 — MERGE + NOVEMBER COUNTERFACTUAL

<!-- RESULTS:MERGE -->
**MERGE (registered protocol; no standalone family passed, so the
merge ran on the strongest failing family — B1, −₹4,240.00 — as
merge-only evidence):**

| | Legs | Total | Trade-days | ₹/trade-day | Red months |
|---|---|---|---|---|---|
| Stack alone | 111 | +₹127,351.50 | 89 | ₹1,430.92 | none |
| B1 increment (stack-idle days) | 12 | **+₹4,560.00** | +12 | — | — |
| **Merged (stack + B1 increment)** | 123 | **+₹131,911.50** | 101 | ₹1,306.05 | none |

The two registered numeric merge legs pass (increment > 0; merged
total > stack total, +₹4,560.00) — **and the merge is still NOT a
pass and NOT promoted**, for the reasons the controls discipline
exists: B1 standalone fails its gate (a coin flip beats it on its own
days), and the increment itself is fragile — halves **H1 +₹4,760 /
H2 −₹200** (a flip), ex-top-3 **−₹2,880** (three target wins carry
it), and the merged ₹/trade-day *falls* to ₹1,306.05 (above the
owner's ₹900 bar, below the stack's own ₹1,430.92). The telling
split: B1's 10 legs that fell on stack-*busy* days lost −₹8,800 —
the family's entire positive residue lives on days the stack sat
idle, the same selection pattern as round 1's V3 fragment. This is a
**noted observation, merge-only evidence** — its honest test is
forward evidence (December paper days under a frozen spec), not
another backtest variant. The 12 increment legs, for the record:
Feb 16 CE +2,480 · Mar 4 CE −1,720 · Mar 9 CE −1,720 · Mar 10 CE
−1,720 · Mar 12 CE +2,480 · Mar 24 CE +2,480 · Apr 21 CE +2,480 ·
Jul 9 CE −1,720 · Jul 14 PE +2,480 · Sep 16 CE −1,720 ·
Sep 25 CE −1,720 · Oct 9 CE +2,480.

**NOVEMBER COUNTERFACTUAL (lens Nov 2–12 + the stack's logged days;
stack November = −₹2,680 on Nov 4/9/12/13):**
- **B1 (the merged family): no November legs at all** — no VIX spike
  ≥ +8% preceded a November trade day in the lens. Merged November =
  **−₹2,680, unchanged.**
- **B2 overlay on November:** all four stack legs are KEPT — prior-day
  VIX was 15.72 (Nov 4 leg), 17.47 and 17.56 on the true prior
  sessions for the Nov 9 and Nov 12 legs (the scorer's calendar
  chained the Nov 9 leg through the Nov 8 fragment day, whose VIX is
  missing, and reached the Nov 12 leg's prior day only via the
  supplementary row — both legs are kept under the frozen
  default-allow rule *and* would be kept on the true prior-session
  closes; disclosed so the machinery gap is on the record), and 16.62
  for the Nov 13 leg. Filtered November = **−₹2,680, unchanged.**
- **A1's own November legs (its book record, not a merge):** Nov 2 PE
  55000 +₹2,480 · Nov 4 PE 55700 −₹1,720 (stack-busy day) · Nov 5 CE
  56900 −₹1,720 → November −₹960. A2 placed no November legs.
- **Nov-13 supplementary (Nov 12 signals, stack-busy day — never
  merged):** A1 no signal (Δbasis −0.0398%, inside the ±0.05 band);
  B1 no signal (VIX *fell* 5.35% on Nov 12); **A2 fired CE** (basis z
  = −1.626 — the Nov-23 future sat at a deep discount, −0.2941%) but
  the leg is **NC**: Nov 13 intraday premium candles for the contract
  were not served by any store or the API tonight — the same
  documented data lag round 1 hit. Excluded everywhere, never
  estimated.

## PART 5 — VERDICT + THE ROUND-3 QUEUE

<!-- RESULTS:VERDICT -->
**VERDICT — ROUND 2 (2026-11-13 night): NO PASS.**
- **Surface A (futures basis): FAIL, both families.** The dataset is
  complete (205/205 days, zero missing, timing clean) — the void is
  closed as a *data* matter for futures positioning too, permanently.
  As a signal: close-to-close basis expansion is anti-predictive in
  2026 (A1, −₹56,152, beaten by all three placebos), and basis
  extremes against the contract's own norm fade too weakly to pay
  (A2, −₹7,779, halves and ex-top-3 red). This route — day-level
  basis, next-day 09:20 ATM, G0 — is closed; a failed variant is not
  retested identically.
- **Surface B (India VIX): FAIL, both families.** Spike-fading (B1)
  loses to a coin flip on its own days. The permission overlay (B2)
  fails its fenced total leg: the stack's fear-regime legs are net
  positive (+₹9,320), so filtering them destroys money while
  flattering the average — the exact trap the freeze named in
  advance. VIX at day level, as a direction or permission signal for
  next-day ATM buying, does not pay in 2026.
- **Merge:** the single positive fragment is B1's increment on
  stack-idle days (+₹4,560 on 12 legs; merged ₹131,911.50, zero red
  months) — merge-only evidence with flipped increment halves and a
  negative increment ex-top-3, **not a pass, not promoted**, joining
  round 1's V3 fragment (+₹3,360, same status) as forward-evidence
  candidates for December paper, judged then under frozen specs.
- **November:** neither surface changes November. The merged
  counterfactual is −₹2,680 under B1 (no legs) and under B2 (no leg
  filtered). November's problem, per the failure audit, was never a
  missing day-level regime flag — the books' high-VIX legs were
  fine; the losses were PE-side quick stops on reversal mornings,
  a shape neither new surface speaks to.
- **Nothing was armed or modified.** The stack runs as before.

**THE ROUND-3 QUEUE — genuinely-new surfaces still untried (the map,
not a stop):**
1. **Intraday OI build-up** (round 1's registered forward family):
   the option-chain archive reaches its ≥20-trading-day gate around
   **Dec 10**; a frozen intraday design (e.g. morning build-up read
   at 10:30) can then be proven forward. Today's day-level OI
   failure does not pre-judge it — different data granularity,
   different design.
2. **FII/DII flows** — NSE's published daily participant data: cash
   market net flows *and* F&O participant-wise open interest (index
   futures long/short ratios of FIIs vs proprietary vs clients).
   Day-level, published after the close, historically retrievable —
   buildable and gateable immediately, and it is the positioning
   read closest to who actually moves Bank Nifty.
3. **Intraday futures basis** — 5-minute Bank Nifty futures candles
   are historically retrievable through the same API, so a *morning*
   basis-expansion read (basis at 10:30 vs the open, traded
   intraday) is a different design from tonight's close-to-close
   family and remains honestly testable on Jan–Oct.
4. **Overnight/global pre-open data** — GIFT Nifty's pre-open level
   vs the prior India close, and the US close alignment: a day-level
   gap-expectation surface no book here has read. Historically
   available; gateable.
5. **Put-call intraday extremes** from the live chain archive
   (intraday PCR/OI-wall breaks) — forward-only, matures with #1.
6. **Forward evidence on the two surviving fragments** (OI-V3
   increment, VIX-B1 increment) in December paper under frozen
   specs — not new backtests; the December-candidate process both
   rounds' verdicts already point to.

Files: `round2_data_build.py` · `round2_score.py` ·
`round2_trades.csv` · `new_data_round2_results.json` ·
`round2_history/` (basis + VIX datasets, futures series, keys,
manifest, Nov-12 supplementary row) · `round2_score.log`.
