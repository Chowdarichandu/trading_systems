# OI BUILD-UP PROGRAMME — closing the ₹20,000/month number (2026-11-13)

**Owner order 2026-11-13 05:48 IST: "work on number first."** The number is the
₹20,000/month per-segment target. Stacked standings at the order:
**Bank ₹16,897/mo (gap ₹3,103) · Nifty ₹12,348/mo (gap ₹7,652) · Stocks met.**
This programme tests the only genuinely new information source found this
week — option-chain open interest (feasibility proven this morning,
`option_chain_buildup_2026-11-13.md`). Bank first (owner's sole-earner
priority), Nifty second. **Paper only, real money ₹0. December candidates
only. No frozen book touched.** Index figures are option premiums per 1 lot
(Bank lot 30, Nifty lot 65), cost ₹220/trade, UNIQUE-ONCE.

---

## PART 1 — RECONSTRUCTED DAILY OI HISTORY (Jan–Oct 2026 + November lens)

Method: per-contract **daily candles** (7th candle field = OI) via the v2
expired-instruments API (live expiries via v3 + instruments cache). Per
trading day per index, for the in-force expiry (Bank monthly; Nifty
front/weekly), over the **ATM band = the 11 strikes nearest that day's spot
close**: aggregate CE OI, PE OI, day-over-day changes summed from the *same
contracts'* prior-trading-day OI, PCR(OI), spot close and day change.
Dataset: `oi_history/banknifty_daily_oi.csv`, `oi_history/nifty_daily_oi.csv`;
contract series cached in `oi_history/contracts/`; fetch manifest
`oi_history/fetch_manifest.csv`; builder `oi_history_build.py`.

<!-- RESULTS:COVERAGE -->
**COVERAGE (verified 2026-11-13 evening, closing run):**
- **Bank Nifty dataset: COMPLETE for the gate window.** `oi_history/banknifty_daily_oi.csv`
  = 213 rows, 2026-01-01 → 2026-11-11. Jan–Oct = **205 rows = every one of
  the 205 spot-calendar trading days** (no missing day, no extra day);
  **201 complete + 4 partial** (2026-03-30, 04-08, 06-12, 07-08 — all 22
  band contracts present, 15–21 of 22 same-contract delta pairs; partial
  days never emit a signal under the frozen rule). Per-day fields: in-force
  monthly expiry, spot close/change, ATM, band CE/PE OI, same-contract
  ΔOI per side, PCR(OI). Contract cache: 1,352 daily series on disk
  (1,070 BANKNIFTY + 282 NIFTY).
- **Timing audit of the dataset itself:** every field of row D is built
  from day-D *daily closes* (OI = the contract's day-D daily-candle OI,
  published after day D's close) and day D−1 closes. A signal read from
  row D is therefore knowable only after D's close and is traded on
  D+1 — **0 look-ahead by construction**; the scorer additionally asserts
  signal_date < trade_date on every trade.
- **November rows:** Nov 2, 3, 4 complete; Nov 5, 6, 9, 11 partial (no
  signals); **2026-11-08 is a 14-bar fragment row (not a session — see the
  failure audit), marked complete in the dataset**; Nov 10 = holiday (no
  row); **no Nov 12 row** (dataset ends Nov 11). Consequence: the frozen
  November lens covers trade days Nov 2–12, and its Nov 9 legs derive
  from the Nov 8 fragment row — flagged wherever the lens is reported.
- **Nifty dataset: NOT BUILT.** 282 NIFTY contract series were cached by
  the interrupted earlier build, but `nifty_daily_oi.csv` was never
  assembled and no fetch manifest was written. Nifty is scored only if
  the Bank pipeline validates mechanically end-to-end (Part 5).

<!-- RESULTS:XVAL -->
**CROSS-VALIDATION (run 2026-11-13 evening; `oi_history/xval_bank_report.txt`):**
- **(a) Chain-archive overlap — EXACT.** This morning's pre-open archived
  chain (bucket 05:35, expiry 2026-11-23) embeds Nov 11 close OI as
  `prev_oi`. Summed over the dataset's Nov 11 band (@60800): archive CE
  **2,581,350** vs dataset **2,581,350** (diff 0) · archive PE **2,052,150**
  vs dataset **2,052,150** (diff 0). The reconstructed daily OI matches
  independent chain ground truth to the contract on the one day both
  sources cover.
- **(b) 5-min store last-bar OI vs daily OI — INCONCLUSIVE as designed.**
  The stored intraday files are partial-window fetches (their last bar is
  not an end-of-day bar), so last-bar OI need not equal daily-close OI;
  a strict full-day filter (≥70 bars, last bar ≥15:25) found no qualifying
  sampled file. Not counted for or against the dataset; check (a) is the
  binding validation.

---

## PART 2 — THE FROZEN BUILD-UP FAMILY (registered before scoring)

**Signal (close of day D, dataset row D only — nothing from D+1):**
spot day change *s* (points) and band-aggregate same-contract ΔOI per side.
Quadrants per side (the PE premium's price change is proxied by −*s*, since
put premiums move against spot at index level):

| Side | LONG_BUILDUP | SHORT_BUILDUP | LONG_UNWINDING | SHORT_COVERING |
|---|---|---|---|---|
| CE | s>0, ΔCE>0 | s<0, ΔCE>0 | s<0, ΔCE<0 | s>0, ΔCE<0 |
| PE | s<0, ΔPE>0 | s>0, ΔPE>0 | s>0, ΔPE<0 | s<0, ΔPE<0 |

Either change exactly 0, or a non-complete dataset day → **no signal**.
Example of the registered read: PE SHORT_BUILDUP (put writing into a rise)
+ CE LONG_BUILDUP (call buying) = bullish positioning → CE next day.

**Variant V1 — ALIGNED:** trade CE iff CE = LONG_BUILDUP **and**
PE = SHORT_BUILDUP; trade PE iff CE = SHORT_BUILDUP **and**
PE = LONG_BUILDUP; otherwise no trade.
**Variant V2 — WRITER-LED:** trade CE iff PE = SHORT_BUILDUP; trade PE iff
CE = SHORT_BUILDUP; otherwise no trade. (V1 ⊂ V2 by construction.)

**Trade (both variants, both indices):** next trading day after D, ONE leg.
Entry = **open of the 09:20 5-minute bar**; strike = ATM nearest step
(Bank 100 / Nifty 50) to that bar's spot open; contract = the in-force
expiry of the trade day (Bank monthly / Nifty front weekly).
**Exits — the incumbents', unchanged:** Bank **G0** (stop −50 checked
before target +90 on every bar including the entry bar, fills at the
level, square-off at the 15:10 bar close; lot 30). Nifty **frozen S5**
(stop −50 before target incl. entry bar; BE arm +50 → stop to entry;
tgt1 +90 → runner lock +60 / TGT2 +175; square-off at the 15:20 bar
close; lot 65). Cost ₹220/trade.

**Gate (standing controls gate, per index per variant, Jan–Oct 2026 by
trade date):** (1) total > 0; (2) both halves (Jan–May, Jun–Oct) > 0;
(3) ex-top-3 > 0; (4) total strictly beats all three placebos —
**REVERSED** direction, **COIN-FLIP** direction (seed 42), **SHIFTED**
signal (quadrant of the trading day *before* the signal day, same trade
days); (5) timing audit 0 violations (every trade's signal day strictly
before its trade day; signal uses only day-D closes); (6) NC ≤ 5% of
signal days (NC = signal day whose trade could not be scored from real
candles — excluded, never estimated). Independent re-sum of the trade
file must match to the paisa.
**Owner's lens (not a gate leg):** November counterfactual, trades dated
Nov 2–12, listed per trade. **Gap test:** a PASS is also stated as
₹/month pace (Jan–Oct total ÷ 10) against Bank's ₹3,103 / Nifty's ₹7,652
gap. Bars never moved; a fail closes this route.

Scorer: `oi_buildup_score.py` · trades: `oi_buildup_trades.csv` ·
results: `oi_buildup_results.json`.

---

## PART 2B — VARIANT V3, FROZEN BEFORE ANY SCORING (added 2026-11-13 evening, owner's invention order 19:31)

V1/V2 above were registered this morning and have never been scored.
The owner's evening order — stop re-combining the old candle rules,
invent from the new data — adds ONE more mechanical variant on the same
day-level OI quadrants, using the one quadrant neither V1 nor V2 ever
trades: **SHORT_COVERING** (writers being squeezed out). This spec is
written and frozen **before the scorer is run on any variant**; V1/V2
are untouched by it.

**Variant V3 — SHORT-COVERING SQUEEZE (buying only):**
- Trade **CE** iff CE quadrant = SHORT_COVERING (s>0, ΔCE_OI<0 — call
  writers covering into a rise) **and** PE quadrant ≠ LONG_BUILDUP
  (no fresh put buying against the move).
- Trade **PE** iff PE quadrant = SHORT_COVERING (s<0, ΔPE_OI<0 — put
  writers covering into a fall) **and** CE quadrant ≠ LONG_BUILDUP.
- Otherwise no trade. Same trade construction as V1/V2 in every other
  respect: next trading day, ONE leg, entry at the open of the 09:20
  5-minute bar, ATM strike to that bar's spot open, in-force expiry,
  Bank G0 exits (Nifty S5 if Part 5 runs), cost ₹220/trade.
- Same gate as Part 2, per variant: total > 0; both halves > 0;
  ex-top-3 > 0; strictly beats REVERSED / COIN-FLIP (seed 42) / SHIFTED
  placebos; timing violations = 0; NC ≤ 5% of signal days; independent
  re-sum exact. (66 Jan–Oct signal days by pre-count from the dataset.)

**Merge protocol (registered with it, applies to whichever of V1/V2/V3
the merge step uses):** INCREMENT = the family's legs on days the
TUNED STACK v2 placed no leg (stack ledger = the verified 111-leg
Jan–Oct file behind `bank_900_tradeday_2026-11-13.md`); merged book =
stack legs + increment legs, UNIQUE-ONCE by construction (disjoint day
sets). The merge PASSES only if (i) the increment alone is net positive,
(ii) the merged total beats the stack alone (+₹127,351.50), and
(iii) the merged per-trade-day average (owner's ₹900 bar) is stated
beside the stack's ₹1,430.92 — dilution on the total = fail, per the
Stack+Volrix precedent. November counterfactual: merged November =
stack's logged November legs (Nov 4 +₹2,480 · Nov 9 −₹1,720 · Nov 12
−₹1,720 · Nov 13 −₹1,720 = **−₹2,680**) + the family's November legs on
stack-idle days, each leg listed; Nov 13 can only be touched by a
supplementary Nov-12-signal check from the archived chain (the frozen
dataset ends Nov 11), labelled supplementary wherever reported.

**DATA-LAYER REPAIR (recorded 2026-11-13 evening, before the repaired
run):** the closing run's first pass exposed a coverage defect in the
*premium store*, not in any rule: for most contract-days,
`daily2leg/prem_bank.json` holds a **truncated series (64 bars starting
10:00)** — the old books' fetch window — and because the frozen scorer
accepts the first non-empty store source, the truncated series shadowed
its own full-day fetch route, producing NC = 125/132 (V1), 185/194
(V2), 64/66 (V3) signal days, all `replay_none` (no 09:20 bar). That
first pass is **invalidated as a coverage artefact** (its scored subset
was only the days whose strikes the old books happened to store in
full). The repair, applied in the run driver `oi_buildup_run_bank.py`
only: **a premium series whose first bar is later than 09:20 is treated
as missing**, and the scorer's own frozen fetch route (expired-
instruments 5-minute candles, full 75-bar days, cached to
`oi_buildup_data/`) supplies the real candles. No signal, entry, exit,
placebo, or gate rule was changed — verified on a traced case
(2026-01-02, 59900 CE: store series starts 10:00; fetched series
09:15–15:25, replay scores normally). All gate figures below are from
the repaired run.

<!-- RESULTS:GATE -->
**GATE — BANK NIFTY, Jan–Oct 2026 (repaired run, 2026-11-13 evening;
`oi_buildup_run_bank.py` driving the frozen scorer; NC = 0 for every
variant; timing violations = 0; independent re-sum EXACT). Paper only,
real money ₹0. Premiums per 1 lot (30), cost ₹220/trade, UNIQUE-ONCE.**

| Variant | Trades | Total | H1 (Jan–May) | H2 (Jun–Oct) | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| V1 ALIGNED | 132 | **−₹21,178.50** | −₹11,947.00 | −₹9,231.50 | −₹28,618.50 | −₹2,117.85 | −55,719 / −55,596 / −47,962 (beats all 3) | **FAIL** — total, halves, ex-top-3 legs |
| V2 WRITER-LED | 194 | **−₹39,618.50** | −₹12,187.00 | −₹27,431.50 | −₹47,058.50 | −₹3,961.85 | −67,236.50 / **−35,136.50** / −68,882 (coin beats it) | **FAIL** — total, halves, ex-top-3, coin placebo |
| V3 SHORT-COVERING (Part 2B) | 66 | **−₹12,720.00** | **+₹2,240.00** | −₹14,960.00 | −₹20,160.00 | −₹1,272.00 | −14,197.50 / **−4,320** / −21,880 (coin beats it) | **FAIL** — total, halves flip, ex-top-3, coin placebo |

Month tables (₹): V1 — Jan −5,360 · Feb −3,067 · Mar −9,000 · Apr +5,320 ·
May +160 · Jun −6,520 · Jul −3,031.50 · Aug −9,760 · Sep −2,120 · Oct +12,200.
V2 — Jan −1,560 · Feb −8,427 · Mar −15,880 · Apr +8,560 · May +5,120 ·
Jun −7,480 · Jul −6,671.50 · Aug −15,120 · Sep −7,480 · Oct +9,320.
V3 — Jan +6,280 · Feb −5,360 · Mar −6,880 · Apr +3,240 · May +4,960 ·
Jun −2,680 · Jul −3,640 · Aug −5,360 · Sep −2,880 · Oct −400.

**Reading, plainly:** the whole design space loses money in 2026 —
even the placebos sit at −₹35k…−₹69k, i.e. next-day-open ATM buying
with G0 geometry has a strongly negative base rate this year. The OI
signal is *not* noise: V1 beats all three placebos by ₹27k–₹35k (the
alignment read loses far less than reversed, random, or stale signals).
But "loses less than chance" is not an edge — after the −50/+90
geometry and the ₹220 toll, day-level build-up continuation does not
pay as a standalone book. **No variant passes; the standalone route is
closed by its own pre-registered gate.**

**MERGE vs TUNED STACK v2 (registered protocol, Part 2B; stack anchor
re-verified in-run: 111 legs, +₹127,351.50, 89 trade-days,
₹1,430.92/trade-day):**

| Variant | Increment (stack-idle days) | Merged total | Merged ₹/trade-day | Merged red months | Merge verdict |
|---|---|---|---|---|---|
| V1 | 69 legs, **−₹9,418.50** | ₹117,933.00 (158 TD) | ₹746.41 | Jun, Aug (stack alone: none) | **FAIL — dilution** |
| V2 | 108 legs, **−₹9,298.50** | ₹118,053.00 (197 TD) | ₹599.25 | Jun, Aug | **FAIL — dilution** |
| V3 | 42 legs, **+₹3,360.00** | **₹130,711.50** (131 TD) | ₹997.80 | **none** | **Registered legs PASS — merge-only evidence (see verdict)** |

V3's increment halves: H1 **+₹4,360** / H2 **−₹1,000** — the increment
itself flips sign across halves and earns ₹80/leg on average. That is
a fragment inside a failed standalone book, not a proven edge.

<!-- RESULTS:NOV -->
**NOVEMBER COUNTERFACTUAL (lens Nov 2–12 + stack's logged days;
stack November = Nov 4 +₹2,480 · Nov 9/12/13 −₹1,720 each = −₹2,680):**

Family November legs (all from stored candles): **V1/V2 shared legs** —
Nov 3 CE 55300 entry 819.90 → target 09:35, **+₹2,480** · Nov 4 CE 55700
→ stop, −₹1,720 (stack-busy day) · Nov 5 CE 56900 → stop 09:25, −₹1,720 ·
Nov 9 PE 59100 → entry-bar stop, −₹1,720 (stack-busy day; signal sourced
from the Nov 8 fragment row — flagged, and excluded from every merged
figure by the busy-day rule anyway). **V2 extra leg** — Nov 2 PE 55000
entry 700.00 → target 11:40, **+₹2,480**. **V3's only leg** — the same
Nov 2 PE, **+₹2,480**.

Merged November (family legs on stack-idle days only):
- **Stack + V1 increment (+₹760): −₹1,920** — better, still negative.
- **Stack + V2 increment (+₹3,240): +₹560** — November would have
  flipped green. Recorded as a fact about November, **not** as a reason
  to adopt V2: its Jan–Oct increment is −₹9,298.50 (the small-window
  trap, named in the failure audit as the programme's recurring error).
- **Stack + V3 increment (+₹2,480): −₹200** — near-flat.
- **Nov 13: unchanged under every variant.** The Nov 12 signal (read
  from the archived chain, supplementary): CE LONG_BUILDUP + PE
  SHORT_BUILDUP → V1/V2 would buy CE 61100 — but Nov 13 is a stack-busy
  day (increment rule excludes it), and the trade itself is **NC**:
  Nov 13 intraday premium candles for that contract were not served by
  any store or the API tonight (the documented data lag).

<!-- RESULTS:VERDICT -->
**VERDICT — BANK NIFTY (2026-11-13 evening):**
- **Standalone OI build-up family: FAIL, all three variants**, on a
  fully-covered run (NC = 0, timing clean, re-sum exact, dataset
  cross-validated to the contract). The void the owner named is real —
  the books had never seen positioning data — and it is now closed as
  a *data* matter: the dataset exists, is validated, and the forward
  archive keeps collecting. As a *signal* at day level, build-up
  continuation does not survive the house geometry and costs. This
  route (day-level quadrant continuation, next-day 09:20 ATM, G0) is
  closed; a failed variant is not retested identically.
- **Merge: V1 and V2 dilute (FAIL). V3's increment is the single
  positive fragment** (+₹3,360 on 42 stack-idle days; merged book
  ₹130,711.50, zero red months, ₹997.80/trade-day) — but V3 standalone
  fails its gate and the increment's halves flip (H1 +₹4,360 /
  H2 −₹1,000). Under the standing controls discipline this is a
  **noted observation, merge-only evidence — NOT a pass and NOT
  promoted.** Its honest test is forward: the intraday OI archive
  (≥20 trading days ≈ Dec 10) plus December paper days, judged then
  under a frozen spec — the December-candidate process, not tonight.
- **Nothing was armed or modified.** The stack runs as before.
- What would change the answer: (i) the intraday archive reaching its
  20-day gate with a *frozen intraday* OI family (a different design
  from today's day-level one — e.g. morning build-up read at 10:30,
  which today's data cannot backtest and must be proven forward);
  (ii) V3-type short-covering increments accumulating positive
  *forward* evidence on stack-idle days in December paper.

---

## PART 5 — NIFTY (run 2026-11-13 night, after Bank validated mechanically end-to-end)

Dataset built by the resume-safe builder (2,976-contract manifest,
stopped_on_429 = false): `oi_history/nifty_daily_oi.csv` = 213 rows;
Jan–Oct = **205 rows (204 complete, 1 partial — 2026-04-08, partial in
both indices)**; November mirrors Bank's structure (incl. the Nov 8
fragment row). **Cross-validation (a) EXACT for Nifty too:** archived
chain Nov 11 band (@25250) CE **37,772,540** = dataset, PE **22,453,730**
= dataset, diff 0 on both sides. Same frozen scorer, same V3 extension,
same data-layer repair; Nifty construction per the frozen spec —
front-weekly expiry, S5 exits, lot 65, cost ₹220/trade. NC = 0 for
every variant; timing violations = 0; re-sum EXACT. Paper, real ₹0.

**GATE — NIFTY, Jan–Oct 2026:**

| Variant | Trades | Total | H1 | H2 | Ex-top-3 | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|
| V1 ALIGNED | 141 | **−₹29,635.50** | −₹26,522.50 | −₹3,113.00 | −₹63,100.50 | **+7,862.35** / −5,484.75 / −27,155.10 | **FAIL — every leg** |
| V2 WRITER-LED | 202 | **−₹57,569.35** | −₹43,413.35 | −₹14,156.00 | −₹91,034.35 | −32,840.75 / **+3,825.10** / −20,370.85 | **FAIL — every leg** |
| V3 SHORT-COVERING | 62 | **−₹28,153.85** | −₹16,890.85 | −₹11,263.00 | −₹61,618.85 | −44,173.10 / −26,074.50 / **+5,410.50** | **FAIL — total, halves, ex-top-3, coin + shifted placebos** |

Month tables (₹): V1 — Jan +18,405 · Feb −24,111.75 · Mar +1,030 ·
Apr −14,384.75 · May −7,461 · Jun −27,201.75 · Jul +3,438.25 ·
Aug −13,948 · Sep +10,820.25 · Oct +23,778.25. V2 — Jan +14,777.90 ·
Feb −32,817 · Mar −9,380 · Apr −6,919.75 · May −9,074.50 ·
Jun −35,589.25 · Jul +7,485 · Aug −20,679.25 · Sep +2,754.25 ·
Oct +31,873.25. V3 — Jan −3,627.10 · Feb −8,705.25 · Mar −10,410 ·
Apr +7,465 · May −1,613.50 · Jun −8,387.50 · Jul +4,046.75 ·
Aug −6,951.25 · Sep −8,066 · Oct +8,095.

**The reversed-placebo fact, stated and fenced:** for Nifty V1 the
REVERSED placebo (trade against the alignment) totals **+₹7,862.35**.
That is evidence *against* the family, recorded as such. It is **not**
a candidate: it was never frozen as one, adopting a placebo post-hoc
is exactly the data-mining the gate exists to prevent — and it would
fail the same gate itself: its halves flip (H1 +₹25,122.60 / H2
−₹17,260.25) and its ex-top-3 is −₹25,602.65 (figures in
`oi_buildup_results.json`). Noted, not chased.

**MERGE vs TUNED v1 (anchor re-verified in-run: 74 legs, +₹103,050.25,
66 trade-days, ₹1,561.37/trade-day):**

| Variant | Increment (v1-idle days) | Merged total | Merged ₹/trade-day | Merged red months | Verdict |
|---|---|---|---|---|---|
| V1 | 96 legs, **−₹41,077.60** | ₹61,972.65 (162 TD) | ₹382.55 | Feb, May, Jun, Aug | **FAIL — severe dilution** |
| V2 | 136 legs, **−₹81,734.10** | ₹21,316.15 (202 TD) | ₹105.53 | Feb, Mar, Apr, May, Jun, Aug | **FAIL — severe dilution** |
| V3 | 41 legs, **−₹40,876.50** | ₹62,173.75 (107 TD) | ₹581.06 | Feb, Mar, Jun, Aug | **FAIL — severe dilution** |

**November counterfactual (TUNED v1's November = +₹3,036.50, one leg
on Nov 3):** family November legs for V1/V2 (identical 6): Nov 2 CE
−₹220 · Nov 3 CE +₹3,680 (v1-busy day, excluded) · Nov 4 CE −₹3,470 ·
Nov 5 CE −₹220 · Nov 9 PE −₹3,470 (signal from the Nov 8 fragment row,
flagged) · Nov 11 CE −₹3,470 → increment −₹10,850 → **merged November
−₹7,813.50** (the merge would have turned Nifty's only positive line
negative). V3 placed **no** November legs → merged November unchanged
at +₹3,036.50.

**VERDICT — NIFTY:** FAIL on every variant, every merge, every leg
that matters — worse than Bank, with the alignment read inverted
against its own reversed placebo. The day-level OI build-up route is
closed for Nifty as well. TUNED v1 runs untouched.

---

## PROGRAMME CLOSE (2026-11-13 night)

The data void is closed as a data matter — permanently: validated
day-level OI datasets for both indices (cross-checked to the contract
against live chain ground truth), a working fetch/score pipeline with
full-day candle coverage, and the intraday archive still collecting
toward its ≥20-day gate (~Dec 10). The day-level build-up signal, in
all three frozen variants and both merges, **does not pay** under the
house geometry and costs — Bank less negatively than chance (signal
present, edge absent), Nifty inverted. The single surviving fragment
is Bank's V3 short-covering increment on stack-idle days (+₹3,360,
merge-only evidence, halves flipped) — a noted observation whose only
honest next test is forward evidence, not another backtest variant.
No book was armed, altered, or merged tonight. Files:
`oi_buildup_run_bank.py` · `oi_buildup_run_nifty.py` ·
`oi_buildup_trades.csv` · `oi_buildup_trades_nifty.csv` ·
`oi_buildup_results.json` · `oi_history/` (datasets, contracts,
manifest, coverage, xval report) · `oi_buildup_data/` (full-day candle
cache).

---

## PART 6 — FORWARD PAPER SHADOW: OI-V3 INCREMENT (setup 2026-11-13 night)

The verdict above stands: V3 standalone FAILS, and its stack-idle
increment (+₹3,360.00 on 42 legs, merged ₹130,711.50, zero red months,
halves flipped H1 +₹4,360 / H2 −₹1,000) is **merge-only evidence, not
a pass**. Its only honest next test is forward evidence. This section
registers that test before it starts; nothing in Parts 1–5 changes.

**The shadow (score-only; never touches any running book):**
- **Rules = the frozen Part 2B V3 spec, verbatim.** Signal from day
  S's close data only, traded on the next trading day T. CE iff CE
  quadrant = SHORT_COVERING and PE ≠ LONG_BUILDUP; PE iff PE quadrant
  = SHORT_COVERING and CE ≠ LONG_BUILDUP; otherwise no leg. Signal
  uses the programme's own code (`oi_buildup_score.py` unmodified +
  the `direction3` extension and the `prem_bars_full` data-layer
  repair exactly as in `oi_buildup_run_bank.py`).
- **Increment condition:** the leg exists ONLY on days TUNED STACK v2
  placed no leg, read from `november_shadow_stack_bank_log.csv`
  (read-only to this shadow). If the stack's status for T cannot be
  determined (no row yet, or a NOT_COMPUTED row), the day is NC —
  idle is never assumed.
- **Geometry:** Bank G0, unchanged — entry at the open of the 09:20
  5-min bar, ATM strike (nearest 100) to that bar's spot open,
  in-force monthly expiry of T, stop −50 before target +90 incl. the
  entry bar, square-off at the 15:10 bar close, 1 lot of 30, cost
  ₹220/trade, **buying only**.
- **Scorer:** `oi_v3_shadow_score.py` · **Ledger:**
  `oi_v3_shadow_log.csv` — one row per scored day (TRADED /
  NO_SIGNAL / STACK_BUSY / NC + the reason named), idempotent per
  date. **Start: Mon 2026-11-16.** Nightly job
  `oi-v3-shadow-scorer-daily`, Mon–Fri 18:05 IST (after the 17:15
  Bank segment engine has written the day's stack row).

**Forward OI feed (the historical dataset ends 2026-11-11 and stays
frozen):** each later day D's row is built from the option-chain
archive — the earliest pre-open bucket (< 09:15 IST) of the first
archive file dated after D carries, per strike, `oi` = D's close OI
and `prev_oi` = D−1's close OI. This is the exact construction the
programme cross-validated to the contract (Nov 13 file's 05:35 bucket:
prev_oi sums over the Nov 11 band = CE 2,581,350 / PE 2,052,150 =
the dataset's Nov 11 row) and the one the Nov-12 supplementary signal
was read from. Band = the 11 strikes nearest D's spot close (the
bucket's spot = D's close); same-contract delta sums over that band;
spot change chains off the previous row's close; status complete iff
all 22 band contracts carry oi AND prev_oi (partial → no signal, per
the frozen rule). Built rows append to a separate file,
`oi_history/banknifty_daily_oi_fwd.csv` (same schema; the frozen
historical file is never modified), each row's spot close
cross-checked against the November machinery's progressive daily
spot store when available. A day whose row cannot be built is NC
with the reason — never estimated, never skipped silently. On
HTTP 429 the run hard-stops and the day is NC `rate_limited`.

**Judging standard (in writing):** this shadow is EVIDENCE-GATHERING
ONLY. A positive forward tally does NOT promote V3, does NOT merge
anything into the stack, and does NOT change any running book.
Promotion would require a fresh full controls gate over the combined
evidence **plus the owner's explicit approval** — neither is implied
by this setup.

**Pre-registered review point:** after **20 scored
trade-opportunities** (days on which V3 produced a direction,
resolved TRADED or STACK_BUSY; NC and no-signal days do not count)
**or 2026-12-31, whichever comes first**. The scorer refuses to
score beyond either bound and reports that the review is due.

**Dry-run verification (2026-11-13 night, before enabling):**
`oi_v3_shadow_score.py --date 2026-11-13 --verify` (hard-wired
no-write) reproduced the programme's known November state exactly:
signal day 2026-11-12 built from the Nov 13 archive pre-open bucket
(spot close 61518.50, change **+726.10**, band @61500, 22/22
complete) → quadrants **CE LONG_BUILDUP / PE SHORT_BUILDUP** —
identical to the supplementary check in `oi_buildup_results.json` —
so V3 direction = none; and Nov 13 is a stack-busy day (stack leg
−₹1,720) → **no increment leg on either ground**, as registered.
Nothing was written by the dry run (no ledger, no forward row); the
frozen dataset and the stack log hashes are unchanged. The nightly
job was created disabled, the dry run verified, then enabled — first
run Mon 2026-11-16 18:05 IST.

---

## PART 7 — INTRADAY-OI BUILD-UP FAMILY, FROZEN IN WRITING (2026-11-13 night; SPEC ONLY — NO SCORING)

Registered in the round-5 queue (new_data_round4_2026-11-13.md
Part 5, item 1) and frozen here, in full, **before** the data that
can judge it exists in sufficient quantity. When the gate date
arrives this is a scoring exercise, not a design exercise: the
rules below do not change at scoring time, and any change after
this writing is a new family with a new freeze, never an edit.

**Why this family exists.** Parts 1–5 closed the day-level
question: build-up quadrants read at a day's close, traded the
next morning, do not pay in any frozen variant on either index.
What no round has tested is build-up **as it forms inside the
morning** — the granularity November's failure mode lives at
(post-11:00 reversals on positioning the candle-only books cannot
see). Round 4 independently established that the late-morning
window itself carries value (its 11:00 entries beat the identical
12:00 entries by ₹33–38k on Bank). This family reads positioning
intraday and trades in that same window. Bank Nifty only in this
freeze (the programme's standing order); the archive collects
Nifty too, but a Nifty freeze is a separate writing.

**Data (the only inputs).** The option-chain archive
(`option_chain_archive/banknifty_<date>.csv`, 5-minute buckets,
front-monthly expiry chain; the archiver
`option_chain_snapshot.py` has collected since 2026-11-13). Per
day T and per strike row the snapshot carries `spot`, `ce_oi`,
`pe_oi`, `ce_close`, `pe_close` (and `ce_prev_oi`/`pe_prev_oi` =
the prior day's close OI — NOT an input to this family; the
baseline below is intraday). Futures, spot candles beyond the
entry strike choice, and day-level OI are not inputs.

**Frozen read construction (per trading day T):**
- **Baseline bucket** = the earliest bucket of T's file with
  bucket time in **[09:15, 09:30]**. **Read bucket** = the latest
  bucket with bucket time in **[10:30, 10:55]**. (The archive's
  real cadence serves both windows — verified on the 2026-11-13
  file: buckets at 09:15/09:20/09:25/09:30 and every 5 minutes
  10:30–10:55.) A day missing either bucket is NC — never
  estimated, never interpolated.
- **Band** = the 11 strikes nearest the spot printed in the READ
  bucket (the same 11-strike near-ATM band as round 1 and the
  Part 6 forward builder). The day is COMPLETE only if all 11
  band strike rows are present in BOTH buckets with non-null
  `ce_oi`, `pe_oi`, `ce_close`, `pe_close`; otherwise NC.
- **Per side S ∈ {CE, PE}, over the band:** ΔOI_S = Σ (oi_S at
  read − oi_S at baseline); premium index P_S = Σ close_S, and
  ΔP_S = P_S(read) − P_S(baseline).
- **Quadrant per side** (the standard build-up quadrants, read
  intraday): ΔOI_S > 0 and ΔP_S > 0 → **LONG_BUILDUP**; ΔOI_S > 0
  and ΔP_S < 0 → **SHORT_BUILDUP**; ΔOI_S < 0 and ΔP_S > 0 →
  **SHORT_COVERING**; ΔOI_S < 0 and ΔP_S < 0 →
  **LONG_UNWINDING**; ΔOI_S = 0 or ΔP_S = 0 → **FLAT** (no
  quadrant).

**The frozen families (at most one leg per day; buying only):**
- **IOI-1 — MORNING BUILD-UP CONTINUATION (primary).** Buy **CE**
  at the 11:00 open iff CE quadrant = LONG_BUILDUP and PE
  quadrant ≠ LONG_BUILDUP. Buy **PE** at the 11:00 open iff PE
  quadrant = LONG_BUILDUP and CE quadrant ≠ LONG_BUILDUP.
  (Both sides building long = a volatility expansion with no
  direction — no trade. Any other combination — no trade.)
- **IOI-2 — WRITER-SQUEEZE CONTINUATION (the one variant; the
  intraday counterpart of Part 2B's V3).** Buy **CE** at the
  11:00 open iff CE quadrant = SHORT_COVERING and PE quadrant ≠
  LONG_BUILDUP. Buy **PE** at the 11:00 open iff PE quadrant =
  SHORT_COVERING and CE quadrant ≠ LONG_BUILDUP. Otherwise no
  trade.
- No other intraday-OI family is frozen by this writing. IOI-1
  and IOI-2 are scored as separate books; a day may fire in both
  books (that is two books' evidence, never a combined position).

**Trade construction (identical for both families):** signal
complete at the read bucket (≤ 10:55); entry = **open of the
11:00 5-minute premium bar**; strike = ATM (nearest 100) to the
spot close of the 10:55 spot bar from the November machinery's
spot series (the read bucket's own printed spot is the recorded
cross-check; a disagreement > 5 points makes the day NC);
contract = the in-force monthly expiry of T (the archive file's
expiry); exits = house intraday geometry — **stop −50 checked
before target +90** on every bar from the entry bar onward, fills
at the level, **square-off at the 15:10 bar close**; **1 lot of
30; cost ₹220/trade; buying only.** Premium candles follow round
1's frozen machinery + the documented full-coverage repair (a
series not covering from ≤ 09:20 counts as missing); an unserved
premium series or a missing 11:00 bar is NC, never estimated.

**Timing discipline (asserted per trade at scoring):** every
signal input is a snapshot bucket at or before 10:55 on day T;
the entry bar's own OHLC is never an input; entry bar time =
11:00. Any violation fails the gate outright, regardless of
totals — the Morning-Mover rule.

**The gate (frozen now; scored once, when the data matures):**
- **Window:** every COMPLETE archive trading day (per the
  completeness definition above) from the first complete day
  through the scoring date. **No scoring before ≥ 20 complete
  archive days exist** — expected on current collection from
  **~2026-12-10**. Days excluded as incomplete are counted and
  named.
- **Legs (the standing controls gate, rounds 1–4 form):**
  (1) total > 0; (2) both halves of the window > 0 (halves split
  at the window's median trading day — a forward window has no
  Jan–Oct halves, and this substitution is registered here, in
  advance, not chosen at scoring time); (3) ex-top-3 > 0;
  (4) total strictly beats all three placebos — **REVERSED**
  direction (same days/strikes), **COIN-FLIP** direction (seed
  42), **TIME-SHIFTED** entry (same signal, direction and strike,
  entry delayed to the open of the **12:00** bar, exits unchanged
  — mandatory in this gate because the family's claim is a
  late-morning-window claim, and round 4 proved an hour's delay
  is exactly where such claims go to die); (5) timing audit =
  0 violations; (6) NC ≤ 5% of fired signal days. Independent
  re-sum of the trade file must match to the paisa. The owner's
  ₹900/trade-day figure is stated beside any PASS as a lens, not
  a gate leg. Bars never move at scoring time; a failed variant
  is never retested identically.
- **Small-sample honesty, registered in advance:** 20–30 forward
  days is a thin window and everyone involved knows it. The gate
  is the gate anyway; a PASS on a thin window earns a forward
  shadow continuation, not adoption, and a FAIL closes the
  family as written.

**Merge test (registered protocol, identical to rounds 1–4):**
for any family that PASSES its gate — or, if none passes, for the
single strongest failing family (highest forward total;
merge-only evidence, labelled as such) — INCREMENT = the family's
legs on days TUNED STACK v2 placed no leg over the same forward
window (stack status read from the stack's shadow log with the
Part 6 NC discipline: no row or NOT_COMPUTED = the day is excluded
from the merge, never assumed idle). The merge PASSES only if
(i) the increment alone is net positive and (ii) the merged total
beats the stack alone over the same window; the merged
₹/trade-day is stated beside the stack's own forward ₹/trade-day
over that window. **The then-current month counterfactual:**
merged arithmetic restricted to the calendar month in progress at
scoring time, every leg listed day by day beside the stack's own
legs for that month.

**Judging standard (in writing):** this freeze authorises
SCORING ONLY when the window matures. It does not arm a book, a
shadow, or a merge. Anything that passes goes to the owner with
the full gate evidence; promotion or forward-shadow arming needs
the owner's explicit approval, exactly as with Parts 2B and 6 and
round 4's Part 6.
