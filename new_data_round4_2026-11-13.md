# NEW-DATA INVENTION — ROUND 4 (2026-11-13 night)

**Owner order 2026-11-13: keep inventing new-data systems until one
passes and merges profitably.** Rounds 1–3 are closed — day-level OI
quadrants (R1), close-to-close futures basis + India VIX (R2), and
FII/DII participant flows (R3) all failed their gates; none is
retested here. The cross-round finding: every *day-level,
next-morning* surface has failed on the incumbents' geometry, while
November's damage is an **intraday** shape (failure audit H2: 4 of 8
November days reversed ≥ 0.7% against the morning direction after
11:00, vs a 21.7% Jan–Oct base rate). A signal read from yesterday
cannot see a reversal that forms after 11:00. **This round goes
intraday.** **Paper only, real money ₹0 — no live trades were
placed.** Index figures are option premiums per 1 lot (Bank lot 30),
cost ₹220/trade, UNIQUE-ONCE. Incumbent for the merge: **TUNED STACK
v2** — 111 legs, **+₹127,351.50** Jan–Oct, 89 trade-days,
**₹1,430.92/trade-day** (anchor file
`solid60_programme_2026-11-13_bank_A_stack_features.csv`, re-asserted
in the scorer). Futures and spot are signal data only — the traded
instrument is always Bank Nifty options, 1 lot, buying only. No
running book, job, or ledger is touched by this round.

---

## SURFACE B — GIFT NIFTY PRE-OPEN: AUDITED, DROPPED IN WRITING

The design would need GIFT Nifty's level shortly before the 09:15
NSE open, for every Jan–Oct 2026 session, from a source whose rows
can be verified. Audit (2026-11-13 night):

- **The exchange publishes no usable free archive.** GIFT Nifty
  trades on NSE IX (NSE International Exchange, GIFT City). NSE's
  historical-data products are paid subscriptions (SFTP/online
  platform, per NSE's own market-data pages); no free NSE IX
  bhavcopy/history archive for GIFT Nifty futures was found.
- **What exists publicly is aggregator tables, and they fail the
  audit standard of rounds 1–3 on three counts.** (i) *Depth:*
  the widest public table found (paisaalgo) advertises "last 60
  days" only; the Upstox information page shows a handful of recent
  sessions — neither reaches Jan–Oct 2026. (ii) *Verifiability:*
  both are third-party aggregations (the live dashboards state they
  re-serve a NiftyTrader API feed); no row can be checked against an
  authoritative exchange record, the standard rounds 1–3 required
  (NSE's own files; chain-archive cross-check to the contract).
  (iii) *Wrong field:* the tables carry the GIFT session's daily
  open/close — not a timestamped pre-open print against the prior
  India close, which is the quantity the design trades on.
- **No chart-API history:** Yahoo Finance (the one public historical
  API used in round 2, for VIX) carries no GIFT Nifty futures
  series.

**Verdict: surface B is DROPPED — a Jan–Oct 2026 GIFT Nifty
pre-open history cannot be obtained from a verifiable source, and
nothing is estimated or scraped in its place. Round 4 proceeds with
surface A alone.**

---

## PART 1 — DATA, SURFACE A (built and audited BEFORE any family was frozen or scored)

Builder: `round4_data_build.py` · dataset: `round4_history/`
(`banknifty_morning_basis.csv`, per-contract 5-minute series
`FUT5_<expiry>.json`, `spot_extra.json`, `build_manifest.json`).

- **Construction:** for each trading day D, the in-force near-month
  BANKNIFTY futures contract (round 2's convention — first monthly
  expiry ≥ D; 11 contracts, 2026-01-27 → 2026-11-23), 5-minute
  candles via the Upstox expired-instruments route (the live
  2026-11-23 contract via v3). Spot = the stored 5-minute series
  every prior round used (`daily2leg/spot.json` + November bars);
  Nov 12 spot (absent from the stored series) fetched via v3 and
  cached in `spot_extra.json`. The morning-read row per day:
  **basis_open** = fut close(09:15 bar) − spot close(09:15 bar)
  (knowable at 09:20); **basis_read** = fut close(10:55 bar) − spot
  close(10:55 bar) (knowable at 11:00); **spot_morning_pct** =
  spot close(10:55) / spot open(09:15) − 1; **dbasis_pct** =
  (basis_read − basis_open) / spot close(10:55). Basis is
  bar-close-to-bar-close from a single intraday source at matched
  timestamps — internally consistent by construction. It is *not*
  round 2's series: round 2's futures leg was the official daily
  candle close (a last-30-minutes weighted print), which differs
  from the intraday last-bar close by that construction; the two
  bases are different quantities at different granularity, which is
  precisely this round's design distinction.
- **Coverage: COMPLETE for the gate window.** 205/205 Jan–Oct days
  carry a complete morning row (futures series complete on every
  in-force day — zero short days after per-day retry). November:
  Nov 2, 3, 4, 5, 6, 9, 11, 12 complete; **Nov 8 is the known
  14-bar fragment** (no morning bars exist — it can never be a
  morning-read trade day); **Nov 13: futures and spot 5-minute
  candles both return 0 from the API tonight** — the documented
  same-day data lag rounds 1–3 hit for premium candles. Nov 13 is
  therefore NC in the November lens, never estimated; the lens runs
  Nov 2–12.
- **Timing audit (the crux of an intraday design):** every signal
  input is a CLOSE of a bar ending at or before 11:00 (the 09:15
  and 10:55 bars). The entry is the OPEN of the 11:00 bar — the
  entry bar's own OHLC is never an input, which is the exact
  construction the November scorers use (signal on completed bars,
  entry at the next bar's open) and the opposite of the
  Morning-Mover error. The scorer asserts per trade: every input
  bar time ≤ "10:55", entry bar time = "11:00", and counts
  violations.
- **Signal-variable structure (inputs only, read before freezing —
  no trade outcome had been computed):** Jan–Oct morning spot move:
  median −0.03%, quartiles −0.36% / +0.31%, range −2.04% …
  +1.63%. Morning Δbasis: median +0.003%, quartiles −0.056% /
  +0.047%, range −0.215% … +0.239%. Basis at the open sits at a
  median +0.29% (the carry premium, decaying into expiry as round 2
  documented) — so, exactly as in round 2, no family reads the
  basis LEVEL; both families read its morning CHANGE.

---

## PART 2 — THE FROZEN FAMILIES (written and frozen BEFORE scoring)

**Common trade construction (both families):** signal read at
11:00 from Part 1 morning data only (bars ≤ 10:55); at most ONE leg
per day; entry = **open of the 11:00 5-minute bar**; strike = ATM
(nearest 100) to the spot close of the 10:55 bar (known at entry);
contract = the in-force monthly expiry of the trade day; exits =
intraday house geometry (stop −50 checked before target +90 on
every bar from the entry bar onward, fills at the level, square-off
at the **15:10** bar close; lot 30); cost ₹220/trade. Buying only.
A day with a partial morning row (Nov 8), an unserved premium
series, or no 11:00 premium bar is NC — excluded, never estimated.
Premium series follow round 1's repair: a series not covering from
≤ 09:20 is treated as missing and the frozen full-day fetch route
supplies real candles (the entry is at 11:00, so coverage of the
whole morning is required, not just of the exit window).

**D1 — MORNING BASIS DIVERGENCE → REVERSAL (primary; the shape
that speaks to November's post-11:00 reversals).**
- spot_morning_pct ≥ **+0.35** (a real morning advance — half the
  failure audit's 0.7% reversal yardstick, reached by mid-morning)
  **and** dbasis_pct ≤ **0.000** (the futures premium did not
  expand at all while spot rose — futures length refuses to back
  the move) → buy **PE** at the 11:00 open.
- spot_morning_pct ≤ **−0.35** **and** dbasis_pct ≥ **0.000**
  (premium refuses to contract into a falling morning) → buy
  **CE** at the 11:00 open.
- Otherwise no trade.

**T1 — MORNING BASIS THRUST → CONTINUATION (variant).**
- dbasis_pct ≥ **+0.040** (the futures premium expanded hard
  during the morning — aggressive futures length building;
  intraday counterpart of round 2's ±0.05 close-to-close band,
  tightened for the shorter window) → buy **CE** at the 11:00
  open.
- dbasis_pct ≤ **−0.040** → buy **PE** at the 11:00 open.
- No spot condition. Otherwise no trade.

**Gate (standing controls gate, Jan–Oct 2026 by trade date,
identical in form to rounds 1–3):** (1) total > 0; (2) both halves
(Jan–May, Jun–Oct) > 0; (3) ex-top-3 > 0; (4) total strictly beats
all three placebos — **REVERSED** direction (same days/strikes),
**COIN-FLIP** direction (seed 42), **TIME-SHIFTED** entry (the
intraday shifted control: same signal, same direction, same
strike, entry delayed to the open of the **12:00** bar, exits
unchanged — if the edge lives in the 11:00 timing, an hour's delay
must kill it); (5) timing audit 0 violations (per-trade assertion
above); (6) NC ≤ 5% of fired signal days. Independent re-sum of
the trade file must match to the paisa.

**Merge protocol (registered, identical to rounds 1–3):** for any
family that PASSES its gate — or, if none passes, for the single
strongest failing family (highest Jan–Oct total; merge-only
evidence, labelled as such) — INCREMENT = the family's legs on
days TUNED STACK v2 placed no leg; merged = stack legs + increment
legs, UNIQUE-ONCE by construction (disjoint day sets). The merge
PASSES only if (i) the increment alone is net positive and (ii)
the merged total beats the stack alone; the merged ₹/trade-day is
stated beside ₹1,430.92 and the merged month table given with red
months named. **November counterfactual:** merged November = the
stack's logged November legs (Nov 4 +₹2,480 · Nov 9 −₹1,720 ·
Nov 12 −₹1,720 · Nov 13 −₹1,720 = **−₹2,680**) + the family's
November legs on stack-idle days (idle: Nov 2, 3, 5, 6, 11), each
leg listed day by day; Nov 13 is NC (data unserved) under every
variant and never counted.

**Owner's lens (not a gate leg):** any PASS is also stated as
₹/trade-day against the owner's ₹900 bar. Bars never move mid-run;
a failed variant is never retested identically.

Scorer: `round4_score.py` · trades: `round4_trades.csv` ·
results: `new_data_round4_results.json`.

---

## PART 3 — GATE RESULTS

<!-- RESULTS:GATE -->
**GATE — BANK NIFTY, Jan–Oct 2026 (run 2026-11-13 night;
`round4_score.py` on round 1's frozen premium machinery + repair;
timing violations = 0 for every book — per-trade assertion, Part 1;
NC = 0 for every book; independent re-sum EXACT). Paper only, real
money ₹0. Premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE.**

| Family | Trades | Total | H1 (Jan–May) | H2 (Jun–Oct) | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted +60m) | Verdict |
|---|---|---|---|---|---|---|---|---|
| D1 DIVERGENCE → REVERSAL | 50 | **−₹7,241.00** | −₹4,866.50 | −₹2,374.50 | −₹14,681.00 | −₹724.10 | **−6,200.00** / **+12,664.00** / −45,282.50 | **FAIL — total, halves, ex-top-3, reversed, coin** |
| T1 THRUST → CONTINUATION | 120 | **−₹37,648.50** | −₹26,919.00 | −₹10,729.50 | −₹45,088.50 | −₹3,764.85 | −19,666.50 / −12,834.00 / −70,426.50 (beats shifted only) | **FAIL — every leg but timing/NC/shifted** |

Month tables (₹). D1 — Jan +267.50 · Feb −3,774 · Mar −200 ·
Apr +5,720 · May −6,880 · Jun +6,480 · Jul −6,880 · Aug −1,920 ·
Sep −4,814.50 · Oct +4,760 (six red months of ten; FT 17/50).
T1 — Jan −6,521 · Feb −5,438 · Mar −8,040 · Apr −10,720 ·
May +3,800 · Jun −4,040 · Jul +2,825.50 · Aug −1,160 · Sep −5,275 ·
Oct −3,080 (eight red months of ten; FT 37/120).

**Reading, per family:**
- **D1's direction is worthless on Bank; its window is not.** A
  coin flip on D1's own days made **+₹12,664** and even the
  reversed book (−₹6,200) beat the frozen divergence rule — on
  mornings when spot ran ≥ 0.35% without futures-premium backing,
  fading the move at 11:00 did not pay under the house geometry.
  But the TIME-SHIFTED control collapses to **−₹45,282.50**: the
  identical signals entered one hour later lose ₹38,041.50 more.
  The late-morning window itself carries information (the failure
  audit's flat-afternoon finding, now measured from the other
  side); the morning-basis read simply cannot pick the side. A
  window is not a system — nothing here is promotable, and the
  observation is recorded as a coverage fact for future intraday
  designs, not as a fragment.
- **T1 is anti-predictive at intraday granularity too.** Basis
  thrust continuation loses in both halves and to the reversed
  and coin controls — the reversed book loses less than half as
  much (−₹19,666.50 vs −₹37,648.50). This is round 2's A1 verdict
  (close-to-close basis expansion is a fade in 2026) reproduced
  inside the day: futures-premium expansion was not a continuation
  signal at *any* horizon tested this year. The reversed control
  was never frozen as a candidate; adopting it post-hoc is the
  data-mining the gate exists to prevent — recorded as evidence
  against the family and fenced, as in rounds 1–3.

**GATE — NIFTY, Jan–Oct 2026 (same run, `round4_score_nifty.py`;
identical frozen families and thresholds; S5 exits from the 11:00
entry bar, lot 65, front-weekly expiries; the Bank pipeline
validated mechanically end-to-end first — NC = 0, timing = 0,
re-sum EXACT; Nifty coverage 205/205 gate days, the November
monthly future verified as the 2026-11-23 contract after the
24th proved to be a holiday-shifted date).**

| Family | Trades | Total | H1 | H2 | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| D1 DIVERGENCE → REVERSAL | 43 | **+₹11,219.75** | +₹19,129.75 | −₹7,910.00 | −₹22,245.25 | +₹1,121.97 | +6,845.90 / +845.75 / −4,321.75 (beats all 3) | **FAIL — halves flip, ex-top-3** |
| T1 THRUST → CONTINUATION | 87 | **−₹52,881.50** | −₹54,527.75 | +₹1,646.25 | −₹82,674.00 | −₹5,288.15 | **+9,307.90** / −40,823.35 / −30,462.35 | **FAIL — every leg** |

Month tables (₹). NIFTY D1 — Jan +7,800.75 · Feb −7,251 ·
Mar +4,205 · Apr +7,025 · May +7,350 · Jun +8,384.50 ·
Jul −4,282.75 · Aug +2,491.25 · Sep −8,362.50 · Oct −6,140.50.
NIFTY T1 — Jan −14,611.50 · Feb +7,542.75 · Mar −10,826.25 ·
Apr −21,938.50 · May −14,694.25 · Jun +15,783.50 · Jul −5,823.50 ·
Aug +4,175.50 · Sep −7,363.25 · Oct −5,126 (seven red months).

**Reading — Nifty:** D1 is the round's only positive standalone
total, and it is a concentration artefact with a regime break:
its top-3 trades are three identical **+₹11,155** runner-target
hits (S5's +175 grid) totalling +₹33,465 — remove them and the
book is −₹22,245.25 — and the effect lived in H1 (+₹19,129.75)
and died in H2 (−₹7,910; Jul–Oct mostly red). A first-half effect
carried by three runner hits is not an edge the gate can certify.
T1 fails everything, with its reversed placebo outright positive
(+₹9,307.90) — fenced, as evidence against the family.

## PART 4 — MERGE + NOVEMBER COUNTERFACTUAL

<!-- RESULTS:MERGE -->
**MERGE — BANK (registered protocol; no family passed, so the
merge ran on the strongest failing family — D1, −₹7,241.00 — as
merge-only evidence):**

| | Legs | Total | Trade-days | ₹/trade-day | Red months |
|---|---|---|---|---|---|
| Stack alone | 111 | +₹127,351.50 | 89 | ₹1,430.92 | none |
| D1 increment (stack-idle days) | 27 | **+₹8,973.00** | +27 | — | — |
| **Merged (stack + D1 increment)** | 138 | **+₹136,324.50** | 116 | ₹1,175.21 | none |

The two registered numeric merge legs pass (increment > 0; merged
total > stack total, +₹8,973.00) — **and the merge is still NOT a
pass and NOT promoted.** What is different this round, stated
exactly: D1's increment is the strongest fragment of the four
rounds — its own halves are **both positive** (H1 +₹3,307.50 /
H2 +₹5,665.50) and its own ex-top-3 is **positive** (+₹1,533.00),
where round 1's V3 increment flipped halves and round 2's B1
increment had a negative ex-top-3. What has *not* changed: D1
standalone fails its gate outright (a coin flip beats it by
₹19,905 on its own days), and the family's legs on stack-*busy*
days lose **−₹16,214.00** (both halves negative) — the entire
positive residue again lives in the idle-day selection, and a
family whose total is negative in both halves does not become a
system because the incumbent's calendar flatters a subset of it.
**Classification: noted observation, merge-only evidence — its
honest test is forward evidence (December paper under the frozen
spec), not another backtest variant.** It joins the fragment
queue as its strongest member. (T1's merge, for the record:
increment 70 legs −₹19,171.00 → merged ₹108,180.50 — dilution,
FAIL.)

**NOVEMBER COUNTERFACTUAL — BANK (stack November = −₹2,680 on
Nov 4/9/12/13; lens Nov 2–12, Nov 13 NC — data unserved):**
- **D1:** one November leg — Nov 12 PE 61300, entry 856.90 →
  target 946.90, **+₹2,480** — but Nov 12 is a stack-*busy* day,
  so the increment is empty and **merged November = −₹2,680,
  unchanged.** On the day itself both books were right the same
  way (the stack's own PE leg that day was a different strike and
  stopped; D1's later, cheaper entry reached target) — a fact
  about one day, not a merge case.
- **T1:** three November legs, all targets — Nov 5 CE 57100
  +₹2,480 (idle) · Nov 9 CE 59000 +₹2,480 (busy) · Nov 11 CE 61100
  +₹2,480 (idle) → increment **+₹4,960** → **merged November
  +₹2,280: the month would have flipped green.** Recorded and
  fenced in the same sentence: T1's Jan–Oct increment is
  **−₹19,171.00** and its standalone total −₹37,648.50 — this is
  the small-window trap in its textbook form (round 1's V2 did
  the same trick: November increment +₹3,240 against a −₹9,298.50
  ten-month increment). November does not adopt T1; the gate
  already judged it.

**MERGE — NIFTY (vs TUNED v1: 74 legs, +₹103,050.25, 66
trade-days, ₹1,561.37/trade-day; D1 again the strongest failing
family):**

| | Legs | Total | Trade-days | ₹/trade-day | Red months |
|---|---|---|---|---|---|
| TUNED v1 alone | 74 | +₹103,050.25 | 66 | ₹1,561.37 | Mar (its own) |
| D1 increment (v1-idle days) | 24 | **+₹13,264.50** | +24 | — | — |
| **Merged** | 98 | **+₹116,314.75** | 90 | ₹1,292.39 | Mar (inherited, none created) |

Registered numeric legs pass (increment > 0; merged > v1) — and
again **not a pass, not promoted**: D1 standalone fails (halves
flip; ex-top-3 −₹22,245.25), and the increment itself is
concentrated — its halves are both positive (+₹7,249.75 /
+₹6,014.75) but its ex-top-3 is **−₹8,770.25** (top-3 = +₹11,155 ·
+₹6,510.75 · +₹4,369.00 carry it). Merge-only evidence; forward
test in December, second priority behind the Bank fragment.
(T1's Nifty merge: increment 60 legs −₹58,729.25 → merged
₹44,321.00 — severe dilution, FAIL.) **November — Nifty:** D1
placed no November legs → merged November = **+₹3,036.50,
unchanged.** T1 placed four (Nov 3 CE +₹4,031 — v1-busy,
excluded · Nov 5 CE +₹6,839 · Nov 6 CE +₹11,155 runner target ·
Nov 12 CE −₹3,470) → increment +₹14,524 → merged November
**+₹17,560.50** — the most flattering November any failed family
has produced in four rounds, against a −₹58,729.25 ten-month
increment. The trap, third occurrence tonight; fenced, not
adopted.

## PART 5 — VERDICT + THE ROUND-5 QUEUE

<!-- RESULTS:VERDICT -->
**VERDICT — ROUND 4 (2026-11-13 night): NO PASS.**
- **Surface B (GIFT Nifty pre-open): DROPPED at audit, in
  writing** — no verifiable Jan–Oct 2026 history exists from an
  authoritative source (exchange data is a paid product; public
  aggregator tables reach back ≤ 60 days, cannot be validated
  row-by-row, and carry session OHLC rather than the pre-open
  print the design needs). Nothing was estimated in its place.
- **Surface A (intraday futures basis): the data void is closed
  — the signal does not pay.** The intraday dataset is complete
  and timing-clean on both indices (205/205 gate days, 0
  violations, NC = 0, re-sum EXACT): for the first time the books
  can *see* the morning's futures positioning as it forms, the
  granularity November's failure mode lives at. As a signal
  under this construction — morning basis change, 11:00 ATM
  entry, house intraday geometry — both frozen families fail on
  both indices: divergence D1 (Bank −₹7,241, beaten by a coin
  flip on its own days; Nifty +₹11,219.75 but halves-flipped and
  carried by three runner hits) and thrust T1 (Bank −₹37,648.50,
  Nifty −₹52,881.50 — basis expansion is a fade at intraday
  horizon too, closing the basis question at every granularity
  tested: close-to-close in round 2, morning intraday here).
  This route is closed; a failed variant is not retested
  identically.
- **The round's two durable findings.** (1) *The 11:00 window
  is real even though these reads of it are not:* on Bank, both
  families' time-shifted placebos (same signals, 12:00 entry)
  collapse by ₹33–38k against the 11:00 entries — the
  late-morning entry point carries value that the afternoon
  forfeits, the failure audit's coverage gap measured from the
  other side. Any future intraday design should enter in that
  window; none may claim this observation as its edge. (2)
  *The fragment queue gained its strongest member:* Bank D1's
  idle-day increment (+₹8,973.00 on 27 legs; increment halves
  and ex-top-3 both positive; merged ₹136,324.50, zero red
  months) — merge-only evidence under a failed family gate, so
  its only honest test is December forward evidence, like the
  fragments before it.
- **November, answered day by day (the round's stated point):**
  the intraday read does not rescue November on any gated
  evidence. D1's only Bank November leg fell on a stack-busy day
  (merged −₹2,680 unchanged); on Nifty it fired not at all
  (+₹3,036.50 unchanged). The green November counterfactuals
  belong to T1 (+₹2,280 Bank, +₹17,560.50 Nifty) — the family
  with the worst ten-month increments of the round — and are
  recorded as the small-window trap, not as a case.
- **Nothing was armed or modified.** Both incumbents run as
  before.

**THE ROUND-5 QUEUE — genuinely-new surfaces still untried (the
map, not a stop):**
1. **Intraday OI build-up** (round 1's registered forward
  family; now head of the queue): the option-chain archive
  reaches its ≥20-trading-day gate around **Dec 10**; a frozen
  intraday design — morning build-up read at **10:30**, entry in
  the 11:00 window this round validated as the valuable one,
  traded intraday — can then be proven forward. It is the only
  untried surface that reads *positioning* intraday, the one
  data class November's reversals are made of and no round has
  yet been able to test at that granularity.
2. **Intraday PCR / OI-wall extremes** from the live chain
  archive — forward-only, matures with #1.
3. **December forward evidence on the surviving fragments**
  under frozen specs — now four: OI-V3 increment (+₹3,360),
  VIX-B1 increment (+₹4,560), **R4-D1 Bank increment (+₹8,973 —
  strongest; increment halves and ex-top-3 positive)**, R4-D1
  Nifty increment (+₹13,264.50, increment ex-top-3 negative —
  secondary). Not new backtests; the December-candidate process
  every round's verdict has pointed to.
4. **December's own forward month** as the next fresh window
  for the incumbents themselves (Nov 30 verdicts first) — the
  standing process, unchanged.

Files: `round4_probe.py` · `round4_probe2.py` ·
`round4_data_build.py` · `round4_data_build_nifty.py` ·
`round4_score.py` · `round4_score_nifty.py` · `round4_trades.csv`
· `round4_trades_nifty.csv` · `new_data_round4_results.json`
(Bank + Nifty) · `new_data_round4_nifty_results.json` ·
`round4_history/` (morning-basis datasets for both indices,
per-contract FUT5 series, futures keys, spot extras, build
manifests) · `round4_build.log` · `round4_build_nifty2.log` ·
`round4_score.log` · `round4_score_nifty.log`.


---

## PART 6 — FORWARD PAPER SHADOW: R4-D1 INCREMENT (setup 2026-11-13 night)

The Part 5 verdict stands: D1 standalone FAILS its gate (a coin flip
beats it by ₹19,905 on its own days), and its stack-idle increment
(+₹8,973.00 on 27 legs; increment halves H1 +₹3,307.50 / H2
+₹5,665.50 and increment ex-top-3 +₹1,533.00 both positive; merged
₹136,324.50, zero red months) is **merge-only evidence, not a
pass** — the strongest fragment of the four invention rounds. Its
only honest next test is forward evidence. This section registers
that test before it starts; nothing in Parts 1–5 changes.

**The shadow (score-only; never touches any running book):**
- **Rules = the frozen Part 2 D1 spec, verbatim.** Morning read
  from day T's own 5-minute bars, closes only (basis_open = fut
  close(09:15) − spot close(09:15); basis_read = fut close(10:55)
  − spot close(10:55); spot_morning_pct = spot close(10:55)/spot
  open(09:15) − 1; dbasis_pct = (basis_read − basis_open)/spot
  close(10:55); futures = the in-force near-month contract of T).
  PE iff spot_morning_pct ≥ +0.35% and dbasis_pct ≤ 0; CE iff
  spot_morning_pct ≤ −0.35% and dbasis_pct ≥ 0; otherwise no leg.
- **Increment condition:** the leg exists ONLY on days TUNED STACK
  v2 placed no leg, read from `november_shadow_stack_bank_log.csv`
  (read-only to this shadow). If the stack's status for T cannot
  be determined (no row yet, or a NOT_COMPUTED row), the day is
  NC — idle is never assumed.
- **Geometry:** intraday house geometry, unchanged — entry at the
  open of the 11:00 5-min bar, ATM strike (nearest 100) to the
  spot close of the 10:55 bar, in-force monthly expiry of T, stop
  −50 before target +90 incl. the entry bar, square-off at the
  15:10 bar close, 1 lot of 30, cost ₹220/trade, **buying only**.
  Timing asserted per trade: every signal input is a close of a
  bar ≤ 10:55; the entry bar is 11:00.
- **Scorer:** `r4d1_shadow_score.py` · **Ledger:**
  `r4d1_shadow_log.csv` — one row per scored day (TRADED /
  NO_SIGNAL / STACK_BUSY / NC + the reason named), idempotent per
  date. **Start: Mon 2026-11-16.** Nightly job
  `r4d1-shadow-scorer-daily`, Mon–Fri 18:20 IST (after the 17:15
  Bank segment engine has written the day's stack row, and after
  the 18:05 OI-V3 shadow scorer, so the two never contend for the
  API at the same minute).

**Forward data feed (round 4's builder is the reference):** the
round-4 dataset (`round4_history/banknifty_morning_basis.csv`) is
frozen at Nov 12 and is never modified. Each forward day's morning
read is built by the scorer from the same sources round 4 used:
spot 5-minute bars from round 4's stored series, then the November
machinery's progressive spot store, then the v3 historical-candle
route (cached to `round4_history/r4d1_spot_fwd.json`); futures
5-minute bars from round 4's per-contract cache
(`FUT5_<expiry>.json`), then a forward day cache
(`round4_history/r4d1_fut_fwd.json`), then the single-day fetch via
the contract's route (v3 while live, expired-instruments after
expiry — round 4's `fetch_range` URL shapes). Contract keys come
from `round2_history/futures_keys.json`, extended from the Upstox
instruments master (complete.csv.gz, FUTIDX/BANKNIFTY) into
`round4_history/futures_keys_fwd.json` when a needed expiry is
missing — the master cross-checks exactly (its 2026-11-23 key is
round 2's NSE_FO|61466; December monthly = **2026-12-29**,
NSE_FO|58872, seeded 2026-11-13). A day whose spot or futures
series has < 70 bars is a fragment (the Nov 8 case) and can never
be a morning-read day → NC. Premium candles use round 1's frozen
machinery + the documented full-coverage repair and the intraday
replay, copied verbatim from `round4_score.py`. On HTTP 429 the
run hard-stops and the day is NC `rate_limited` — no retry, no
route switch.

**Judging standard (in writing):** this shadow is
EVIDENCE-GATHERING ONLY. A positive forward tally does NOT promote
D1, does NOT merge anything into the stack, and does NOT change
any running book. Promotion would require a fresh full controls
gate over the combined evidence **plus the owner's explicit
approval** — neither is implied by this setup.

**Pre-registered review point:** after **20 scored
trade-opportunities** (days on which D1 produced a direction,
resolved TRADED or STACK_BUSY; NC and no-signal days do not count)
**or 2026-12-31, whichever comes first**. The scorer refuses to
score beyond either bound and reports that the review is due.

**Dry-run verification (2026-11-13 night, before enabling):**
`r4d1_shadow_score.py --date <day> --verify` (hard-wired no-write)
over every November trading day reproduced round 4's known state:
Nov 2 (+0.0770 / −0.0066), Nov 3 (+0.1993 / +0.0104), Nov 4
(+0.1826 / +0.0186), Nov 5 (−0.0439 / +0.0629), Nov 6 (−0.2390 /
−0.0397), Nov 9 (−0.2966 / +0.1528) and Nov 11 (+0.9733 / +0.1705)
all **NO_SIGNAL** — D1 fired on none of them, exactly as
`round4_trades.csv` records (the Nov 9 and Nov 11 morning reads
match `banknifty_morning_basis.csv` to the fourth decimal).
**Nov 12: direction PE** (spot_morning +0.8197%, dbasis −0.0105%,
both identical to the frozen dataset; the leg round 4 scored was
PE 61300) **and the stack traded that day → STACK_BUSY, no
increment leg** — the registered state, reproduced exactly.
**Nov 13: NC `futures_unserved`** — stated honestly: spot for
Nov 13 has since landed in the progressive store (09:15 and 10:55
bars present), but the Nov contract's 5-minute futures candles
still return 0 from the API tonight (probed directly, and again
inside the scorer), so the morning read cannot be completed and
the day is NC, never estimated — the same disposition round 4
gave it. Nothing was written by the dry run (no ledger created,
no forward caches, stack log and frozen datasets untouched). The
nightly job was created and enabled after this verification —
first run Mon 2026-11-16 18:20 IST.
