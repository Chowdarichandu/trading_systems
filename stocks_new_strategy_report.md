# NEW STOCK STRATEGY — three invented mechanisms, full overnight run — 2026-10-31

**EQUITY CASH intraday only. NOT options — no premiums anywhere.
LONG/SHORT equity, paper only, no orders. Real money: ₹0.**
**Every rupee figure is provisional per 100 shares, ₹40/trade cost.**
Window: Jan–Oct 2026 (Oct = 1–28), 25 stocks, 203 trading days.
Specs frozen before scoring: `stocks_new_strategy_frozen.md`
(Mechanism 1 also in `stocks_hunt1_frozen.md`). Engines:
`stocks_hunt1.py` (M1), `stocks_new_strategy.py` (M2, M3).
Data note: the 5-min cache is OHLC only — no volume exists, so no
volume-based mechanism was possible.

**Pass gates (user's requirements):** (1) net positive in BOTH halves
(Jan–May and Jun–Oct); (2) breadth — the strategy must work across
ALL stocks, not a few: stocks net-positive /25, top-3 share, worst-5
reported for every mechanism.

## VERDICT FIRST — no mechanism passes. Nothing is adopted.

Three genuinely distinct mechanisms, 20 families, ~110,000 paper
trades scored. **Not one family is net-positive in both halves**, so
the breadth gate never even comes into play — the best breadth seen
is 7 of 25 stocks net-positive (L-d), attached to a losing total.
The honest near-misses and what each mechanism taught are below.
The hunt pattern the user described IS visible in the data (chains
of 2–5 entries on one stock in a day happen constantly — M1 averages
33.7 entries/day across the watchlist) — it just does not carry an
edge with any of these triggers: later chain rounds are gross-better
than first entries in M1, but not by enough to pay ₹40/trade.

---

## MECHANISM 1 — EXTREME-HUNT (day-so-far breakout, trail, re-entry)

Trigger: 5-min close beyond the day-so-far high/low; trail exit
(activate +0.5%, trail 0.35%); re-entry on every fresh extreme close.

| Family | Trades | Net ₹ | Exp ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | /day |
|---|---|---|---|---|---|---|---|
| F0 base trail cap4 | 6,834 | −283,889.92 | −41.54 | −148,845.96 | −135,043.96 | −8,224.50 | 33.67 |
| F1 fixed 1.0%/0.5% | 6,515 | −348,108.84 | −53.43 | −184,342.45 | −163,766.39 | −15,079.81 | 32.09 |
| F2 fixed 0.5%/0.5% | 7,808 | −299,089.99 | −38.31 | −170,031.60 | −129,058.39 | −6,528.92 | 38.46 |
| F3 60-min range trigger | 12,239 | −437,015.25 | −35.71 | −182,872.69 | −254,142.56 | −70,140.60 | 60.29 |
| F4 uncapped | 6,869 | −285,814.19 | −41.61 | −149,536.56 | −136,277.63 | −8,773.92 | 33.84 |
| F5 stop-out rule | 6,685 | −287,410.10 | −42.99 | −158,597.80 | −128,812.30 | −6,180.82 | 32.93 |
| F6 ADR≥2% filter | 5,672 | −231,082.26 | −40.74 | −129,084.66 | −101,997.60 | −13,687.12 | 27.94 |
| F7 no entries ≥14:30 | 6,187 | −264,507.33 | −42.75 | −155,636.76 | −108,870.57 | **+2,236.28** | 30.48 |
| F8 reclaim re-entries | 7,984 | −316,093.40 | −39.59 | −173,214.41 | −142,878.99 | +1,512.67 | 39.33 |
| F9 clearance ≥0.10% | 4,664 | −188,529.49 | −40.42 | −111,409.79 | −77,119.70 | −22,097.72 | 22.98 |
| F10 wider trail | 6,148 | −287,288.05 | −46.73 | −140,327.57 | −146,960.48 | −12,697.87 | 30.29 |

(All figures provisional per 100 shares. F9's gross expectancy is
−₹0.42/trade — filtering out marginal breakouts removes the noise
and reveals essentially nothing underneath: breakeven cost ≈ ₹0.)

**Chain diagnostics (F0) — the user's hunt pattern, in the data:**
round 1: 4,246 trades, net exp −₹47.65 (gross −₹7.65); round 2:
1,942, −₹32.67 (gross +₹7.33); round 3: 531, −₹17.02 (gross
+₹22.98); round 4: 115, −₹79.08 (gross −₹39.08). Chains do reach
4–5 entries (F4 uncapped: 35 fifth-plus entries) — but round 4 is
the worst round, not the payoff. **Exit anatomy (F0):** trail-stop
exits 2,756 trades net +₹1,069,757.38 (+₹388.16/trade — the trail
itself works when it engages); square-offs 1,224, +₹110,072.00;
hard stops 2,854, −₹1,463,719.30 (−₹512.87/trade). 42% of entries
never reach the +0.5% trail activation and bleed the full stop.
**Breadth (F0): 5/25 stocks net-positive.** Best: HINDUNILVR
+₹12,201, GLENMARK +₹4,742, HINDCOPPER +₹3,201. Worst: TVSMOTOR
−₹48,832, OBEROIRLTY −₹40,098, GODREJCP −₹26,710, HINDALCO
−₹24,438, BDL −₹21,803 (all provisional per 100 shares).
Event-window trades lose less than no-event (−₹29.73 vs −₹45.73
expectancy in F0) but both are negative — no gate there.

## MECHANISM 2 — LADDER (0.4% grid from the day anchor, grid-retrace exit)

| Family | Trades | Net ₹ | Exp ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | /day | Breadth |
|---|---|---|---|---|---|---|---|---|
| L-a grid exit cap6 | 6,617 | −205,558.23 | −31.07 | −55,932.24 | −149,625.99 | −8,422.10 | 32.60 | 5/25 |
| L-b grid exit cap4 | 6,614 | −206,334.03 | −31.20 | −56,283.04 | −150,050.99 | −8,422.10 | 32.58 | 5/25 |
| L-trail trail exit | 8,586 | −326,996.87 | −38.08 | −135,484.30 | −191,512.57 | −32,523.70 | 42.30 | 2/25 |
| **L-c hold-to-close, stop −1.0%** | 5,713 | −139,395.95 | −24.40 | **+4,004.44** | −143,400.39 | +8,016.63 | 28.14 | 6/25 |
| L-d wide trail (stop −1.0%, act 1.0%) | 6,394 | −157,657.59 | −24.66 | −22,512.13 | −135,145.46 | +9,453.98 | 31.50 | 7/25 |

**Diagnosis:** ladder entries DO drift — in L-c, trades reaching
square-off average +₹521.43 gross (Jan–May) / +₹347.75 (Jun–Oct)
per trade, but the −1% stop exits average −₹933/−₹942 gross:
adverse excursions of ~1% are normal for these entries, so the
user's small-stop style is exactly what this entry set cannot
survive — and even held to close, the drift flips sign by half
(LONG gross +₹59.31 in Jan–May → −₹33.74 in Jun–Oct). L-c's Jan–May
is the ONLY net-positive half produced by any new mechanism, and
its Jun–Oct gross expectancy is −₹10.33/trade: no cost level fixes
a negative-gross half. **Breadth (L-c): 6/25.** Best: HINDCOPPER
+₹18,094.61, GLENMARK +₹17,466.71, UNITDSPR +₹13,257.40. Worst:
OBEROIRLTY −₹50,440.90, GODREJCP −₹26,126.90, HINDALCO −₹25,023.45
(all provisional per 100 shares).

## MECHANISM 3 — SNAP (climax-stretch fade) and SURGE-FOLLOW

Stretch = a bar reaching ≥1.2% from the session average price with
≥1.5× average range; fade after a reversal close (SNAP) or follow
after a continuation close (S-f). Both directions of the same idea
were scored — both fail, which is itself the finding: **the climax
bar carries no tradable next-bar information on this universe.**

| Family | Trades | Net ₹ | Exp ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | /day | Breadth |
|---|---|---|---|---|---|---|---|---|
| S-a fade, target 0.75% | 1,066 | −109,480.95 | −102.70 | −60,657.37 | −48,823.58 | −11,296.02 | 5.25 | 3/25 |
| S-b fade, target ½-way to SAP | 832 | −98,221.24 | −118.05 | −57,255.43 | −40,965.81 | −6,081.36 | 4.10 | 2/25 |
| S-cap4 fade cap4 | 1,098 | −116,021.34 | −105.67 | −65,040.55 | −50,980.79 | −11,206.02 | 5.41 | 4/25 |
| S-f surge-follow, trail | 998 | −66,597.17 | −66.73 | −32,069.18 | −34,527.99 | −9,371.01 | 4.92 | 4/25 |

SNAP anatomy: targets +₹682.10 gross/trade (340 trades) but stops
−₹589.94 gross (480 trades) — stretches continue more often than
they snap within the day. **Breadth (S-a): 3/25** — fails the
all-stocks requirement by the widest margin of the three.

---

## What the overnight search actually established

1. **Frequency is solved; expectancy is not.** Every mechanism
   generates 5–60 entries/day across the 25 stocks with the hunt
   loop working exactly as the user described. The missing piece
   was never trade count or the re-entry rule.
2. **Intraday entries from price structure alone (extremes, grids,
   stretches) have gross expectancy between about −₹63 and +₹23
   per trade per 100 shares on this universe** — at or below the
   ₹40 cost in the best pockets, negative in most. The best gross
   pockets (M1 round-3 entries +₹22.98, ladder drift-to-close)
   flip sign between halves.
3. **The trail exit is validated as a component**: when it engages
   it books +₹428 gross/trade (M1). The failure is upstream — 42%
   of breakout entries never reach activation.
4. **No mechanism earns a paper spec from this run.** The nearest
   miss is L-c (one positive half, positive October, 6/25 breadth)
   — reported as a near-miss, not a candidate: its second half is
   gross-negative, so it is a regime artefact until a fresh window
   says otherwise.
5. Nothing here displaces the two families already in November
   paper from the earlier work (event-reaction N4-V3 and the
   below-trend INV1 shadow) — those remain the only both-halves
   net-positive equity results on record, and their November exam
   is unaffected by this run.

## Files

- Specs: `stocks_new_strategy_frozen.md`, `stocks_hunt1_frozen.md`
- Engines: `stocks_hunt1.py`, `stocks_new_strategy.py`
- Trades: `hunt1_F0_trades.csv` … `hunt1_F10_trades.csv`,
  `newstrat_L-a_trades.csv` … `newstrat_S-f_trades.csv`
- Results: `hunt1_results.json`, `newstrat_results.json`
- This report: `stocks_new_strategy_report.md`

---

# PART 2 — VOLUME AXIS (added 2026-10-30 night, after Part 1)

Part 1's mechanisms were blind to participation: the cache was
OHLC-only. Part 2 fetched volume and re-tested the thesis that
volume is the missing input. Spec: the Part 2 section of
`stocks_new_strategy_frozen.md`, frozen before any Part 2 scoring.
Engine: `stocks_new_strategy_vol.py`; fetcher:
`fetch_vol_janoct.py`; trades `newstratvol_V*_trades.csv`; results
`newstratvol_results.json`. All figures provisional per 100 shares,
₹40/trade, equity cash LONG/SHORT, paper only, real money ₹0.

## Volume fetch — verification (Step 1)

- Source: Upstox v3 historical-candle endpoint (the same call the
  original progressive fetch used — it returns a volume column the
  original fetch discarded), one request per symbol-month, Jan–Oct
  2026, saved to `data/progressive_vol/<SYM>/spot_5m_vol.csv`. The
  OHLC cache was NOT overwritten.
- Coverage: **380,616 bars** across the 25 stocks (15,225 per stock;
  VEDL 15,216), exactly matching the Part 1 cache bar-for-bar —
  **0 bars missing**.
- OHLC check: all 380,616 overlapping bars compared against the
  Part 1 cache — **0 mismatches**.
- Zero-volume bars: 2,760 of 380,616 = **0.73%** (120 bars for 23
  stocks, 0 for IRCTC and HINDCOPPER; concentrated placeholder-type
  bars, and on such bars the rolling median is zero, the volume
  ratio is undefined, and no Part 2 mechanism can enter — they
  cannot contaminate a signal). Full table:
  `data/progressive_vol/verification.json`.

## Results — every Part 2 family FAILS the both-halves gate

| Family | Trades | /day | Win% | Gross exp ₹ | Jan–May net ₹ | Jun–Oct net ₹ | Oct net ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|
| V1a hunt + vol ≥1.5× | 3,876 | 19.1 | 45.4 | +0.16 | −98,536.35 | −55,865.38 | −18,525.87 | 3/25 |
| V1b hunt + vol ≥2.0× | 3,355 | 16.5 | 45.6 | −0.19 | −89,984.88 | −44,846.84 | −10,651.21 | 3/25 |
| V2 surge-follow, trail | 3,215 | 15.8 | 44.9 | +5.25 | −38,664.97 | −73,068.88 | −28,735.46 | 3/25 |
| V2 surge-follow, T10 | 3,127 | 15.4 | 39.3 | +22.69 | −2,556.78 | −51,566.94 | −24,476.29 | 6/25 |
| V2 surge-follow, trail, cap4 | 3,213 | 15.8 | 44.9 | +5.14 | −38,924.97 | −73,068.88 | −28,735.46 | 3/25 |
| V3 ladder + vol ≥1.5× | 3,275 | 16.1 | 43.2 | +35.03 | **+45,413.60** | −61,697.60 | −25,724.35 | **10/25** |

Top-3 share of net is not meaningful for any family (every total is
negative); per-stock tables are in `newstratvol_results.json`.
Worst stocks repeat across families (TVSMOTOR −₹29.5k to −₹40.1k in
the V1 families and −₹31.6k in V3; ASTRAL −₹15.2k to −₹19.9k).

## What Part 2 actually established

1. **Volume confirmation helps magnitude, not sign.** Gating the
   breakout hunt on participation cut its loss roughly in half vs
   Part 1's F0 (−₹283,889.92 → −₹154,401.73 at 1.5×) and lifted
   Jun–Oct gross expectancy to +₹11.56/trade — but Jan–May gross
   stayed negative (−₹11.54) and breadth stayed 3/25. Confirmed
   breakouts still don't pay in the first half.
2. **A raw volume surge carries no follow-through edge.** V2's
   gross expectancy is positive (+₹22.69 at the T10 exit) yet both
   halves are net-negative, and its October is the worst of any
   Part 2 family (−₹24k to −₹29k): surge candles in a falling
   month are distribution as often as accumulation, and the data
   cannot separate them at entry.
3. **V3 is the strongest near-miss of the whole search — and it
   still flips.** The volume gate transforms LADDER's first half
   (Jan–May +₹45,413.60 net, vs +₹4,004.44 unfiltered; gross
   +₹68.54/trade) and doubles breadth to 10/25 — then Jun–Oct
   loses −₹61,697.60. The direction diagnostic (from the scored
   trades, reported as diagnosis, not as a variant) shows the
   same fault line as Part 1: V3 LONGs go +₹43,171 (Jan–May) →
   −₹52,032 (Jun–Oct); V2-T10 LONGs +₹25,701 → −₹53,456. The
   upward-drift participation that pays in the first half reverses
   in the second, on both mechanisms, with or without volume.
4. **Chain structure under volume gates:** V1/V2 round-1 and
   round-2 entries are expectancy-negative; only tiny round-3/4
   samples turn positive (V2-T10 round 3 +₹94.84, round 4 +₹155.81
   on 79/13 trades) — the same "later rounds look better" mirage
   as Part 1, on samples too small to carry a rule. V3's chain is
   96% round-1 (the volume gate plus extended band extremes make
   repeat entries rare), so V3 is effectively a single-entry
   mechanism in practice.
5. **Combined verdict across price + volume axes:** participation
   data roughly doubles the quality of the best pockets (V3 gross
   +₹35.03/trade overall is the highest full-sample gross of any
   invented mechanism) but does not cure the core disease found in
   Part 1 — intraday directional drift on this 25-stock universe
   changes sign between halves, and no entry rule frozen in
   advance — price-based or volume-based — has survived both
   halves with breadth. **No Part 2 mechanism earns a paper
   spec.** The remaining untested invention axes, named honestly
   and NOT claimed: (a) information/event-proximity entries —
   inventing around *when* a stock has a reason to move (results
   and news windows) rather than around price/volume shape; the
   only both-halves-positive threads on record (N4-V3, INV1) live
   on that axis and are already in their November exams; (b)
   1-minute granularity, which the 5-min cache cannot test;
   (c) cross-sectional relative-strength selection across the 25
   (trade only the day's strongest/weakest few) — untested as an
   invented mechanism.

---

# PART 3 — EX-ANTE ADAPTATION vs THE DRIFT FLIP (added 2026-10-30 night, after Part 2)

Part 2 left one named disease: intraday directional drift flips sign
between halves, and every fixed-direction rule dies on the flip.
Part 3 tests the obvious cure — adapt ex-ante. Every rule below uses
only data available before the trade (trailing daily windows ending
the previous trading day, or same-day data up to the decision bar).
No calendar-month logic anywhere. Spec: the Part 3 section of
`stocks_new_strategy_frozen.md`, frozen before any Part 3 scoring,
including a numeric breadth gate (≥10/25 stocks positive, top-3 ≤75%
of a positive total). Engine: `stocks_new_strategy_p3.py`; trades
`newstratp3_*_trades.csv`; results `newstratp3_results.json`. All
figures provisional per 100 shares, ₹40/trade, equity cash
LONG/SHORT, paper only, real money ₹0.

**Validation gate (run first):** the Part 3 ladder engine with the
drift rule disabled reproduces the published Part 2 V3 result
EXACTLY — 3,275 trades, net −₹16,284.00, gross expectancy +₹35.03.
The D-family numbers below are anchored to the scored V3, not to a
re-derivation.

## Results — every Part 3 family FAILS the both-halves gate

| Family | Trades | /day | Win% | Gross exp ₹ | Jan–May net ₹ | Jun–Oct net ₹ | Oct net ₹ | Breadth |
|---|---|---|---|---|---|---|---|---|
| D1 kept (V3 + drift-20 gate) | 1,604 | 7.90 | 44.0 | +25.38 | −995.99 | −22,456.33 | −8,987.76 | 10/25 |
| D1 dropped (for reference) | 1,671 | — | 42.4 | +44.29 | **+46,409.59** | −39,241.27 | −16,736.59 | 9/25 |
| D1b kept (drift-10 gate) | 1,636 | 8.06 | 43.5 | +5.94 | −6,752.57 | −48,967.19 | −19,963.13 | 11/25 |
| D2 drift-follow ladder | 1,620 | 7.98 | 43.9 | +24.82 | −2,042.10 | −22,542.68 | −9,517.76 | 10/25 |
| X1 RS, T10 exit | 2,179 | 10.73 | 37.4 | +3.95 | −57,362.02 | −21,192.71 | −11,423.39 | 4/25 |
| X1 RS, hold exit | 2,179 | 10.73 | 42.3 | +9.01 | −46,116.46 | −21,406.13 | −16,392.53 | 6/25 |
| X2 RS + volume pace, T10 | 878 | 4.33 | 36.9 | +33.32 | −15,757.65 | **+9,894.26** | −2,959.05 | 7/25 |
| X2 RS + volume pace, hold | 878 | 4.33 | 40.4 | +27.24 | −23,242.72 | **+12,043.56** | −11,150.93 | 7/25 |

(Unadapted base for comparison — V3 itself: 3,275 trades, Jan–May
+₹45,413.60, Jun–Oct −₹61,697.60, total −₹16,284.00, breadth 10/25.
Top-3 share is not meaningful for any Part 3 family; every total is
negative. Per-stock tables are in `newstratp3_results.json`.)

**Per-direction splits (net ₹, Jan–May / Jun–Oct):**
- D1 kept: LONG +6,936.39 / −22,108.13; SHORT −7,932.38 / −348.20.
  D1 dropped: LONG +36,234.59 / −29,923.89; SHORT +10,175.00 /
  −9,317.38. Even inside the drift-aligned kept set, the LONG side
  itself flips (expectancy +₹19.82 → −₹94.08).
- D2: LONG +5,920.28 / −19,704.48; SHORT −7,962.38 / −2,838.20 —
  statistically the same picture as D1 (the gate-vs-mechanism
  construction difference is immaterial: V3 chains are ~96%
  round-1, so freeing blocked slots changes only 16 trades).
- X1-T10: LONG −21,941.50 / −2,292.94; SHORT −35,420.52 /
  −18,899.77. X1-HOLD: LONG −37,146.20 / −9,433.63; SHORT
  −8,970.26 / −11,972.50. Morning relative strength does not
  continue intraday in either half at the T10 exit, and only
  partly (short side) at the hold exit.
- X2-T10: LONG −5,653.16 / +11,938.78; SHORT −10,104.49 /
  −2,044.52. The volume-pace gate concentrates what little RS
  continuation exists into Jun–Oct LONGs.

**Breadth detail:** D1/D2's 10/25 matches V3's own breadth (best
stocks ASTRAL +₹11,538.90, UNITDSPR +₹8,649.90, HINDCOPPER
+₹7,839.90; worst OBEROIRLTY −₹5,147.70, GODREJCP −₹4,817.90,
HINDALCO −₹4,067.60 — all provisional per 100 shares): adaptation
preserves the breadth and the loss together. X1's breadth is the
worst of Part 3 (4–6/25 — BDL alone is +₹32,900.00 in X1-HOLD
while INDUSTOWER, OIL and HINDZINC each lose ₹8.8–10.7k); X2
reaches 7/25. No family is within reach of the breadth gate on a
positive total, because no total is positive.

## What Part 3 proved about adaptation — the direct answer

**Ex-ante trailing-drift adaptation does NOT beat the fixed rule —
it is worse.** D1's total (−₹23,452.32) and D2's (−₹24,584.78) both
lose MORE than the unadapted V3 (−₹16,284.00) on the identical
window. The reason is visible in the kept/dropped split, and it is
the cleanest negative result of the whole search: **partition V3's
trades by trailing-20-day drift sign and BOTH sides flip.** The
kept (drift-aligned) side goes ≈₹0 → −₹22.5k; the dropped
(counter-drift) side goes +₹46.4k → −₹39.2k. In Jan–May the gate
discarded the single most profitable subset V3 ever produced
(dropped gross expectancy +₹95.98/trade) and kept a breakeven one;
in Jun–Oct it kept the less-bad subset, which still lost. A
shorter window (D1b, 10 days) is worse on both halves. The drift
sign of the last 10–20 days is simply not information about
tomorrow's intraday direction on this universe — in the first half
it is closer to a reversal signal, in the second half to noise —
and the regime that actually flips operates at a scale (the
half-year) that no trailing window can read before it has already
turned. Adaptation at these horizons is curve-following the flip,
not anticipating it.

**Cross-sectional RS has the same disease in purer form.** X1's
gross expectancy flips −₹13.26 (Jan–May) → +₹20.77 (Jun–Oct) at the
T10 exit: whether the morning's strongest stocks keep rising is
itself regime-dependent, ex-ante unreadable from the morning
itself. The volume-pace gate (X2) is Part 3's most effective single
filter — it turns Jun–Oct net-positive at both exits (gross
+₹60.74 / +₹65.25) and lifts X2's overall gross expectancy to
+₹33.32, the best of any Part 3 family — but Jan–May's underlying
RS gross is +₹0.70, so there is nothing for the gate to save in
the first half. (Diagnosis only, not a family: within X2, the
13:00 set-2 entries beat the 10:30 set-1 entries at both exits —
T10 −₹8,103.83 → +₹2,240.44, HOLD −₹26,731.81 → +₹15,532.65 — but
set 2's Jan–May is not separately positive on the X1 evidence, so
this earns no variant.)

**One observation repeated across all three parts, stated once
more as observation, not as a new claim:** event-window trades are
net-positive inside the losing Part 3 families too — D1 kept
+₹8,714.61, D2 +₹7,829.61, X2-T10 +₹13,384.53, X2-HOLD
+₹20,356.67 (all provisional per 100 shares) — while no-event
trades carry the losses. The information/event axis remains the
only one where both-halves-positive results exist on record
(N4-V3, INV1, both already in their November paper exams).

## Combined verdict — Parts 1 + 2 + 3 (final for this search)

Nine mechanism lines, 33 families, ~136,000 paper trades. **No
invented mechanism passes the frozen gates — net positive in both
halves at ₹40 with all-stocks breadth — and no paper spec is
earned by this search.** Part 3 closes the last named invention
axis with a direct test: the drift flip that killed Parts 1–2 is
not an information problem solvable by trailing adaptation; both
partitions of the best mechanism flip, the adapted versions lose
more than the fixed base, and cross-sectional selection flips the
same way. What the search established, in total: (1) frequency and
the re-entry hunt are solved — entries are abundant; (2) the trail
exit is a validated component; (3) volume confirmation roughly
doubles the gross quality of the best pockets and is the most
effective filter found; (4) pure price/volume/RS structure on this
25-stock universe has gross expectancy between about −₹118 and
+₹35 per trade, regime-signed at the half-year scale, and no
ex-ante rule frozen in advance — fixed, gated, or adaptive — has
read that regime correctly in both halves; (5) the only
both-halves net-positive equity threads on record remain the
event-axis systems already running their November paper exams
(N4-V3 primary, INV1 shadow), which this search does not displace.
**The search stops here, cleanly** — the 11:30 delivery reports
this conclusion; any further invention would need a genuinely new
information source (the event axis, or 1-minute data), not another
recombination of price, volume, or trailing statistics.
