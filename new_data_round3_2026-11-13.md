# NEW-DATA INVENTION — ROUND 3 (2026-11-13 night)

**Owner order 2026-11-13 19:31 / 20:23 IST: keep inventing new-data
systems until one passes and merges profitably.** Rounds 1 (day-level
option-chain OI quadrants) and 2 (futures basis + India VIX) are
closed — every family failed its gate; none is retested here. This
round's surface is **FII/DII participant flow data** — *who* is
positioned, not just how much: NSE's daily F&O participant-wise open
interest (FII index-futures long/short book, FII index-options book,
per-category shares). No existing book has ever read it. It is
day-level and historically retrievable, so it is gated NOW on
Jan–Oct 2026. **Paper only, real money ₹0 — no live trades were
placed.** Index figures are option premiums per 1 lot (Bank lot 30),
cost ₹220/trade, UNIQUE-ONCE. Incumbent for the merge: **TUNED STACK
v2** — 111 legs, **+₹127,351.50** Jan–Oct, 89 trade-days,
**₹1,430.92/trade-day** (anchor file
`solid60_programme_2026-11-13_bank_A_stack_features.csv`, re-asserted
in the scorer). Participant flows are signal data only — the traded
instrument is always Bank Nifty options, 1 lot, buying only. No
running book, job, or ledger is touched by this round.

---

## PART 1 — DATA (built and audited BEFORE any family was frozen or scored)

Builder: `round3_data_build.py` · dataset: `round3_history/`
(`participant_daily.csv`, `fetch_manifest.csv`, `build_summary.json`,
raw files in `round3_history/raw/`).

- **Source: NSE's own archive files, no mirror** —
  `https://archives.nseindia.com/content/nsccl/fao_participant_oi_DDMMYYYY.csv`,
  one file per session: participant-wise open interest (contracts)
  for Client / DII / FII / Pro across futures and options, index and
  stock. Every downloaded file was validated mechanically: all four
  participant rows present **and the TOTAL row exactly equal to the
  participant sum** (Future Index Long check) — **299 valid session
  files, 0 invalid**, spanning **2025-09-01 → 2026-11-13**.
- **Coverage: COMPLETE for the gate window.** The dataset's Jan 1 –
  Oct 31 2026 dates are **205 of 205** — set-identical to the round-1
  OI dataset's 205 Jan–Oct trading days (verified programmatically,
  zero missing). **84 pre-2026 sessions** (Sep–Dec 2025) are included
  so every lag window the frozen families use is full from the first
  gate signal day. November sessions present: Nov 2, 3, 4, 5, 6, 8, 9,
  11, 12, 13 (Nov 10 = Diwali holiday, no file; Nov 8 = the short
  14-bar afternoon session — a participant file exists for it, and
  rounds 1–2's chaining treatment is kept: it can be a signal day,
  and as a trade day it has no 09:20 spot bar, so any leg landing on
  it is NC, never estimated).
- **Independent cross-check (one day, exact):** for 2026-11-12 the
  file's FII index-futures book is Long 70,744 / Short 120,463 →
  net **−49,719 contracts** — identical to the independent mirror
  justticks.in's published 12 Nov figure ("FIIs are net short 49.7K
  index futures contracts"). The source is NSE itself; the mirror
  check validates the parse.
- **PUBLICATION-TIMING AUDIT (the crux of this surface):** the
  participant file for session D is an end-of-day NSCCL product. Two
  direct observations tonight: (1) the 2026-11-12 file's HTTP
  `Last-Modified` is **Thu, 12 Nov 2026 14:14:03 GMT = 19:44 IST** —
  the same evening, ~4¼ hours after the 15:30 close; (2) the
  2026-11-13 file **already existed at ~20:37 IST on Nov 13** when
  probed. (The public mirror likewise labels the report "Published
  end-of-day".) **Frozen consequence: a signal read from session D's
  file is knowable only on D's evening and is traded at D+1's 09:20
  bar — roughly 13½ hours after publication. Zero look-ahead by
  construction; the scorer additionally asserts signal_date <
  trade_date on every scored trade and counts violations.**
- **FII/DII cash flows: NOT obtainable with honest coverage —
  dropped, documented.** NSE's `api/fiidiiTradeReact` was probed
  tonight and returns only the latest session (13-Nov-2026). No NSE
  daily cash-flow archive for Jan–Oct 2026 exists through that route,
  and no mirror was substituted (an unverifiable mirror would fail
  this round's own audit standard). The executed surface is therefore
  the F&O participant-wise OI file — which carries the assignment's
  core fields: the FII index-futures long/short ratio, the FII
  index-options positioning, and participant category shares.
- **Signal-variable structure (read before freezing, as in round 2):**
  the FII index-futures book is *structurally* short through this
  whole window — FII net index futures ranged **−49,719 …
  −319,669 contracts, never positive** (Sep 2025 – Nov 2026), and
  the long ratio LR = Long/(Long+Short) ranged 0.060–0.370 with
  median 0.120. An absolute LR threshold would therefore encode the
  structural hedge book, not crowding. **Consequence (frozen into
  Part 2): the primary family reads LR only against its own
  trailing distribution** — crowding is relative, never absolute.

---

## PART 2 — THE FROZEN FAMILIES (written and frozen BEFORE scoring)

**Common trade construction (both families):** signal at the close
of session D from Part 1 data only (session D's participant file,
published D evening); ONE leg on the next participant-calendar
session D+1; entry = **open of the 09:20 5-minute bar**; strike =
ATM (nearest 100) to that bar's spot open; contract = the in-force
monthly expiry of the trade day (from the round-1 OI dataset; Nov 12
/ Nov 13 → 2026-11-23); exits = **G0** (stop −50 checked before
target +90 on every bar including the entry bar, fills at the level,
square-off at the 15:10 bar close; lot 30); cost ₹220/trade. Buying
only. A trade day with no 09:20 spot bar (Nov 8) or unserved premium
candles is NC — excluded, never estimated. For trade day Nov 12
(no stored spot series) the strike reference is the fetched index
09:20 bar if the API serves it, else NC; the Nov 12 → Nov 13 leg is
the labelled supplementary (strike reference = the chain archive's
09:15 spot print, as in round 2), reported separately and never
counted in any merged figure (Nov 13 is a stack-busy day).

**F1 — FII INDEX-FUTURES CROWDING REVERSAL (primary).**
LR_D = FII Future Index Long / (Long + Short) from session D's file.
Trailing window W_D = the LR values of the up-to-60 participant
sessions strictly before D (fewer than 40 → no signal).
ρ_D = (number of values in W_D strictly less than LR_D) / |W_D| —
LR_D's empirical percentile rank inside its own recent history.
- ρ_D ≤ **0.20** (FII futures book at its most crowded-short extreme
  — squeeze risk) → buy **CE** on D+1.
- ρ_D ≥ **0.80** (FII book at its least-short / most crowded-long
  extreme relative to its own norm) → buy **PE** on D+1.
- Otherwise no trade.

**F2 — FII FLOW MOMENTUM (variant, the opposite hypothesis).**
NET_D = FII Future Index Long − Short (contracts). ΔNET3_D =
NET_D − NET_{D−3}, where D−3 is the third prior participant session.
- ΔNET3_D > 0 (three sessions of net short-covering / lengthening)
  → buy **CE** on D+1.
- ΔNET3_D < 0 (three sessions of net short-building) → buy **PE**
  on D+1.
- ΔNET3_D = 0 or history missing → no trade.

**Gate (standing controls gate, Jan–Oct 2026 by trade date,
identical to rounds 1–2):** (1) total > 0; (2) both halves (Jan–May,
Jun–Oct) > 0; (3) ex-top-3 > 0; (4) total strictly beats all three
placebos — **REVERSED** direction, **COIN-FLIP** direction (seed 42),
**SHIFTED** signal (the family's signal computed from the session
*before* the signal session, same trade-day loop); (5) timing audit
0 violations (publication-timing proof above + per-trade assertion);
(6) NC ≤ 5% of fired signal days. Independent re-sum of the trade
file must match to the paisa.

**Merge protocol (registered, identical to rounds 1–2):** for any
family that PASSES its gate — or, if none passes, for the single
strongest failing family (highest Jan–Oct total; merge-only
evidence, labelled as such) — INCREMENT = the family's legs on days
TUNED STACK v2 placed no leg; merged = stack legs + increment legs,
UNIQUE-ONCE by construction (disjoint day sets). The merge PASSES
only if (i) the increment alone is net positive and (ii) the merged
total beats the stack alone; the merged ₹/trade-day is stated beside
₹1,430.92 and the merged month table given with red months named.
**November counterfactual:** merged November = the stack's logged
November legs (Nov 4 +₹2,480 · Nov 9 −₹1,720 · Nov 12 −₹1,720 ·
Nov 13 −₹1,720 = **−₹2,680**) + the family's November legs on
stack-idle days (idle: Nov 2, 3, 5, 6, 11), each leg listed; the
Nov-13 supplementary leg is reported separately, never merged.

**Owner's lens (not a gate leg):** any PASS is also stated as
₹/trade-day against the owner's ₹900 bar. Bars never move mid-run; a
failed variant is never retested identically.

Scorer: `round3_score.py` · trades: `round3_trades.csv` ·
results: `new_data_round3_results.json`.

---

## PART 3 — GATE RESULTS

<!-- RESULTS:GATE -->
**GATE — BANK NIFTY, Jan–Oct 2026 (run 2026-11-13 night;
`round3_score.py` on round 1's frozen machinery; timing violations =
0 for every book — the publication-timing proof of Part 1 plus the
per-trade assertion; independent re-sum EXACT for every book). Paper
only, real money ₹0. Premiums per 1 lot (30), cost ₹220/trade,
UNIQUE-ONCE.**

| Family | Trades | Total | H1 (Jan–May) | H2 (Jun–Oct) | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| F1 CROWDING REVERSAL | 87 | **−₹7,047.00** | −₹5,402.50 | −₹1,644.50 | −₹14,487.00 | −₹704.70 | −30,219.00 / −43,968.00 / **−7,047.00** | **FAIL — total, halves, ex-top-3, shifted (tie)** |
| F2 FLOW MOMENTUM | 204 | **−₹65,983.50** | −₹32,339.00 | −₹33,644.50 | −₹73,423.50 | −₹6,598.35 | −41,671.50 / −29,713.50 / −80,259.00 | **FAIL — total, halves, ex-top-3, reversed, coin** |

Month tables (₹). F1 — Jan −7,080 · Feb −3,442.50 · Mar 0 (no
trades) · Apr −1,160 · May +6,280 · Jun +3,800 · Jul −9,044.50 ·
Aug −3,440 · Sep +4,760 · Oct +2,280 (five red months of nine
traded). F2 — Jan +920 · Feb −21,699 · Mar −7,480 · Apr +3,400 ·
May −7,480 · Jun −19,320 · Jul −12,684.50 · Aug −10,920 · Sep
+1,680 · Oct +7,600 (seven red months of ten).

**NC accounting:** each family carries NC = 2, and both sit in the
November lens, not the gate window — signal Nov 6 → trade day Nov 8
(the short session has no 09:20 bar, the rounds 1–2 treatment) and
the Nov 12 → Nov 13 leg inside the main loop (scored separately as
the supplementary below). Gate-window NC = 0 for both families.

**Reading, per family:**
- **F1's direction is real; its size is not.** It beats the reversed
  control by ₹23,172 and the coin by ₹36,921 — knowing which side
  the FII book is crowded on is worth something on Bank. But under
  G0 geometry + ₹220 cost the residue is still −₹7,047, both halves
  are red, and the ex-top-3 is −₹14,487. The shifted leg fails on a
  **tie**: the shifted book totals exactly −₹7,047.00 on a *different*
  trade set (92 trades vs 93 — verified from the trade file, not the
  same book). F1's extremes arrive in multi-day blocks, so
  yesterday's signal books nearly the same trades as today's; on the
  coarse G0 outcome grid (mostly ±₹1,720 / +₹2,480) the two sums land
  on the same paisa. The gate requires a strict beat — a tie fails,
  as registered. "Loses less than the controls" is not an edge; this
  is the same sentence rounds 1 and 2 wrote about OI-V1 and basis-A2.
- **F2 is a cost bleed on a whipsaw.** It fires on 204 of 205 days —
  the ₹220 cost alone is ₹44,880 across the window — and the
  3-session change in FII net futures flips sign too often to carry
  a next-morning ATM position: both halves bleed almost identically
  (−₹32,339 / −₹33,644.50), and a coin flip *and* the reversed book
  both beat it. Day-level FII flow momentum is not a continuation
  signal in 2026.

**GATE — NIFTY, Jan–Oct 2026 (same run, `round3_score_nifty.py`;
S5 exits, lot 65, weekly expiries; timing violations 0; re-sum
EXACT).**

| Family | Trades | Total | H1 | H2 | Ex-top-3 | Pace/mo | Placebos (rev / coin / shifted) | Verdict |
|---|---|---|---|---|---|---|---|---|
| F1 CROWDING REVERSAL | 87 | **−₹54,110.00** | −₹35,619.50 | −₹18,490.50 | −₹87,575.00 | −₹5,411.00 | −7,430.90 / −44,831.25 / −47,190.75 | **FAIL — every leg** |
| F2 FLOW MOMENTUM | 204 | **−₹102,772.25** | −₹31,479.65 | −₹71,292.60 | −₹136,237.25 | −₹10,277.23 | **+8,882.15** / −52,473.95 / −105,634.85 | **FAIL — every leg but shifted** |

Month tables (₹). NIFTY F1 — Jan −20,017.50 · Feb +13,066.75 ·
Mar 0 (no trades) · Apr −4,148.75 · May −24,520 · Jun −6,402.25 ·
Jul −18,629.25 · Aug +2,683.25 · Sep −4,120.50 · Oct +7,978.25.
NIFTY F2 — Jan +25,358.60 · Feb −46,480 · Mar −5,876.50 · Apr
+6,360.75 · May −10,842.50 · Jun −28,712.25 · Jul −36,513.50 ·
Aug −25,689.75 · Sep +13,622.90 · Oct +6,000.

**Reading — Nifty:** the same participant signal is *anti*-predictive
on Nifty. F1 loses to all three placebos (the reversed book loses
₹46,679.10 *less*), and F2's reversed placebo is outright
**positive (+₹8,882.15)** while the frozen momentum book loses
−₹102,772.25. The reversed control was never frozen as a candidate;
adopting it post-hoc is exactly the data-mining the gate exists to
prevent — it is recorded as evidence *against* the F2 family and
fenced, as rounds 1–2 fenced theirs. One index-wide positioning
series cannot be faded on Bank and followed-in-reverse on Nifty
after the fact; both frozen reads are dead on both indices.

## PART 4 — MERGE + NOVEMBER COUNTERFACTUAL

<!-- RESULTS:MERGE -->
**MERGE — BANK (registered protocol; no family passed, so the merge
ran on the strongest failing family — F1, −₹7,047.00 — as merge-only
evidence):**

| | Legs | Total | Trade-days | ₹/trade-day | Red months |
|---|---|---|---|---|---|
| Stack alone | 111 | +₹127,351.50 | 89 | ₹1,430.92 | none |
| F1 increment (stack-idle days) | 42 | **−₹9,447.00** | +42 | — | — |
| **Merged (stack + F1 increment)** | 153 | **+₹117,904.50** | 131 | ₹900.03 | none |

**Merge FAIL — dilution.** The increment alone is negative, so the
merged book makes *less* money than the stack alone (−₹9,447.00).
The merged ₹900.03/trade-day sits a hair above the owner's ₹900 bar
and far below the stack's own ₹1,430.92 — the average is flattered
by spreading a smaller total over more days, the PB-subset trap in
its merge form; the registered legs (increment > 0, merged > stack)
both fail. Unlike rounds 1–2, this round leaves **no positive
fragment**: the complement subset (F1 legs on stack-*busy* days)
sums to +₹2,400, but that is a day-selection artefact of a family
whose total is negative in both halves — the registered merge leg
is the idle-day increment, it is negative, and a busy-day subset of
a failing family is not a promotable fragment under the gate.

**NOVEMBER COUNTERFACTUAL — BANK (stack November = −₹2,680 on
Nov 4/9/12/13):** F1 fired PE on six straight November signal days
and stopped out six straight times — Nov 4 −1,720 · Nov 5 −1,720 ·
Nov 6 −1,720 · Nov 9 −1,720 · Nov 11 −1,720 · Nov 12 −1,720 =
**−₹10,320** (the Nov 12 leg scored from the fetched Nov 12 spot
bar, source labelled in the trade file). The crowding fade spent
November walking PE into a rising tape — the FII book sat at its
least-short extreme while the market rose, and the fade believed
the positioning over the price. Increment legs (stack-idle Nov 5,
6, 11): −₹5,160. **Merged November = −₹7,840** — the merge would
have made November *worse* by ₹5,160. F2's own November: 8 legs,
−₹1,160 (not merged; F1 was the merge family).
**Nov-13 supplementary (Nov 12 signals, stack-busy day — never
merged):** F1 fired PE, F2 fired CE; both legs **NC** — Nov 13
intraday premium candles were not served by any store or the API
tonight, the same documented data lag rounds 1–2 hit. Excluded
everywhere, never estimated.

**MERGE — NIFTY (vs TUNED v1: 74 legs, +₹103,050.25, 66 trade-days,
₹1,561.37/trade-day; F1 again the strongest failing family):**
increment = 60 legs, **−₹64,039.75** → merged **+₹39,010.50** on
126 trade-days = **₹309.61/trade-day**, with merged red months
Jan · Mar · May · Jun (TUNED v1 alone has only March red on a
monthly-net basis). **Merge FAIL — severe dilution.** November:
F1's six Nifty legs (Nov 4 −220 · Nov 5 −3,470 · Nov 6 −3,470 ·
Nov 9 −3,470 · Nov 11 +3,680 · Nov 12 −3,470 = −₹10,420) all fell
on TUNED-v1-idle days, so merged November = +₹3,036.50 − ₹10,420 =
**−₹7,383.50** — the merge would have destroyed the only positive
Nifty November line, the same warning round 1's Nifty merge gave.
Nov-13 supplementary: F1 PE / F2 CE, both NC (premium candles
unserved), never merged.

## PART 5 — VERDICT + THE ROUND-4 QUEUE

<!-- RESULTS:VERDICT -->
**VERDICT — ROUND 3 (2026-11-13 night): NO PASS.**
- **The surface is closed as a data matter — permanently.**
  Participant-wise OI is now on disk for 299 sessions (Sep 2025 –
  Nov 2026), 205/205 in the gate window, TOTAL-validated on every
  file, cross-checked exact against an independent mirror on the
  one overlapping day, with the publication timing *proven* (day
  D's file lands on D's evening — observed Last-Modified 19:44 IST
  for Nov 12; the Nov 13 file existed by ~20:37 IST on Nov 13).
  Signals trade D+1: zero look-ahead, 0 timing violations, re-sum
  EXACT on both indices. Who is positioned is no longer a void.
- **As a signal at day level, it does not pay — on either index,
  under either frozen read.** Crowding reversal (F1): Bank
  −₹7,047 (direction real, size below cost+geometry; shifted tie),
  Nifty −₹54,110 (anti-predictive, beaten by every placebo). Flow
  momentum (F2): Bank −₹65,983.50, Nifty −₹102,772.25 (reversed
  placebo positive on Nifty — fenced, not adopted). Both merges
  dilute (Bank increment −₹9,447; Nifty increment −₹64,039.75), and
  both November counterfactuals get *worse* (−₹2,680 → −₹7,840 on
  Bank; +₹3,036.50 → −₹7,383.50 on Nifty). This route — day-level
  participant flows, next-day 09:20 ATM, house exits — is closed; a
  failed variant is not retested identically.
- **The pattern across three rounds is now the finding.** Every
  day-level, next-morning surface invented so far — option-chain OI
  quadrants (R1), futures basis and VIX (R2), participant flows
  (R3) — has failed its gate on the incumbent's geometry, and the
  only positive residues in three rounds are *idle-day increments*
  (OI-V3 +₹3,360; VIX-B1 +₹4,560), both unpromoted and awaiting
  December forward evidence. November's losses, per the failure
  audit, were PE-side quick stops on reversal mornings — an
  *intraday* shape. No day-level surface can see a reversal that
  happens after 11:00; the remaining queue is therefore intraday
  and forward surfaces, not a fourth day-level read.
- **Nothing was armed or modified.** Both incumbents run as before.

**THE ROUND-4 QUEUE — genuinely-new surfaces still untried (the
map, not a stop):**
1. **Intraday OI build-up** (round 1's registered forward family):
   the option-chain archive reaches its ≥20-trading-day gate around
   **Dec 10**; a frozen intraday design (e.g. morning build-up read
   at 10:30, traded intraday — the first design that can actually
   see November's post-11:00 reversal shape forming) can then be
   proven forward.
2. **Intraday futures basis** — 5-minute Bank Nifty futures candles
   are historically retrievable through the same API, so a *morning*
   basis read (basis at 10:30 vs the open, traded intraday) is a
   different design from round 2's close-to-close family and
   remains honestly testable on Jan–Oct.
3. **Overnight / global pre-open data** — GIFT Nifty's pre-open
   level vs the prior India close, and US close alignment: a
   gap-expectation surface no book here has read. Historically
   available; gateable.
4. **Intraday PCR / OI-wall extremes** from the live chain archive
   — forward-only, matures with #1.
5. **Forward evidence on the two surviving fragments** (OI-V3
   increment, VIX-B1 increment) in December paper under frozen
   specs — not new backtests; the December-candidate process all
   three rounds' verdicts point to.

Files: `round3_data_build.py` · `round3_score.py` ·
`round3_score_nifty.py` · `round3_trades.csv` ·
`round3_trades_nifty.csv` · `new_data_round3_results.json`
(Bank + Nifty) · `new_data_round3_nifty_results.json` ·
`round3_history/` (participant dataset, fetch manifest, build
summary, 299 raw NSE files) · `round3_score.log` ·
`round3_score_nifty.log`.
