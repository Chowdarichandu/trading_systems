# Bank Nifty SCALPING Feasibility Study — FROZEN DEFINITIONS

Frozen: **2026-10-31 15:54 IST**, BEFORE any scoring was run.
Scope: **Bank Nifty ONLY** (never Nifty, never stocks, never pooled). Paper only, real money ₹0.
Index options only, **premiums per 1 lot (30)**, cost **₹220/trade** (round trip).
Window: Jan–Oct 2026 as supported by local data = **2026-01-01 → 2026-10-27, 192 trading days**
(the local spot/option dataset ends 2026-10-27; Oct 28–30 spot days are absent from it — stated, not approximated).

## Data (all local, pre-existing)

- Spot 5-min: `~/workspace/trading/data/banknifty-2026-*/spot_5m.csv` (unioned, deduped by timestamp).
- Option 5-min premium candles: `~/workspace/trading/data/banknifty-2026-*/option_5m.csv`
  (timestamp, strike, option_type, expiry, OHLC). Each series carries its own monthly expiry.
- Prior-day levels PDH/PDL/PDC: computed from the prior trading day's 5-min spot bars in the same
  unified series (causal by construction).
- Red bands/ledges: `~/workspace/trading/data/banknifty-2026-jul-oct/red_bands_v2.json`
  (`per_date[date] = {master_bands: [{low,high}...], tactical_ledges: [{low,high}...]}`),
  available **2026-07-02 → 2026-10-27 only**. **Jan–Jun 2026 has NO Red-band data locally**, so S2
  runs on PDH/PDL/PDC only for Jan–Jun, and PDH/PDL/PDC + Red bands/ledges for Jul–Oct. Stated here
  before scoring; no levels are invented.

## Common rules (all three techniques)

- Bars are 5-min, timestamped by bar start. A signal is evaluated on a bar's CLOSE (full bar known).
- **Entry = open of the NEXT 5-min option candle after the signal bar.** No same-bar entries.
- ATM = strike nearest 100 to spot at the signal-bar close; expiry = the expiry in force for that
  date per the engine convention (first monthly expiry ≥ date, from the aggressive_score EXPIRIES
  list) — and the option series used must be the stored series for that (strike, type, expiry).
- Exit replay on the option candles, starting at the entry bar: on every bar, **stop checked before
  target**; stop exit fills at the stop price, target exit at the target price; time-stop exits at
  the close of the time-stop bar ("market price"); if still open at the bar starting 15:10, exit at
  that bar's close (square_off).
- If the needed premium candle series is missing (or the entry/exit bars are missing), the trade is
  **NOT_COMPUTED**: excluded from all totals, counted and reported. Never estimated.
- UNIQUE-ONCE per (technique, date, direction, trigger key) as defined per technique below.
- Trades are replayed independently per technique (paper-study convention, as with engine legs);
  the per-day caps and spacing rules below are the only cross-trade constraints.
- Net per trade = (exit premium − entry premium) × 30 − ₹220.

## S1 — OR-BURST

- Opening range: spot high/low over the bars starting 09:15, 09:20, 09:25 (the 09:15–09:30 window).
- Signal: a 5-min spot bar starting ≥09:30 and ≤13:30 whose CLOSE is beyond the OR (above ORH → CE,
  below ORL → PE), where the previous bar's close was NOT beyond the OR on that same side (a fresh
  crossing event; re-breaks after price returns inside the OR are new triggers).
- Trigger key = signal bar start time. Max **3 S1 trades/day**; **≥30 min between S1 entry bars**.
- Exits: **target +25, stop −20** premium points; **time-stop 3 bars** (entry bar = bar 1; exit at
  close of bar 3 if neither hit).

## S2 — LEVEL-REJECT

- Levels for the day: PDH (resistance), PDL (support), PDC (either side), plus — Jul–Oct only —
  Red master bands and tactical ledges: a band/ledge [low, high] contributes its **high as
  resistance** and its **low as support**.
- Resistance rejection (→ PE): a 5-min spot bar with **high > L** (wick through the level) where the
  previous bar's close was ≤ L (approach from below), and the bar **closes at or below the midpoint
  of the penetration**: close ≤ L + (high − L)/2. (I.e. the close retraces at least the upper half of
  the wick above the level — the frozen reading of "close back on the entry side by ≥ the wick's
  midpoint".)
- Support rejection (→ CE): mirror image — **low < L**, previous bar's close ≥ L, and
  **close ≥ L − (L − low)/2**.
- Signal window: bar start 09:35–14:50. Trigger key = level identity (level type + level value) —
  the **same level cannot re-trigger within 60 min**. Max **3 S2 trades/day**.
- Exits: **target +22, stop −18**; **time-stop 4 bars**.

## S3 — IMPULSE

- Signal: a 5-min spot bar starting 09:45–14:30 with **body |close − open| ≥ 0.15% of the bar's
  open**, closing **above the highest high of the previous 3 bars** (→ CE, close > open) or **below
  the lowest low of the previous 3 bars** (→ PE, close < open).
- Trigger key = signal bar start time. Max **4 S3 trades/day**; **≥20 min between S3 entry bars**.
- Exits: **target +22, stop −18**; **time-stop 2 bars**.

## Controls (run in the SAME run as first scoring — no number leaves before they pass)

1. **Timing/leak audit** on every trade: entry bar start strictly after signal bar start;
   signal uses only bars ≤ signal bar. Violations must be 0.
2. **Placebo (a) lag:** same signals, entry delayed 1 extra bar, same exit geometry.
3. **Placebo (b) random:** count-matched random entries (same N as the technique's computed trades;
   random trading day in window, random entry bar start in 09:35–14:55, random direction, ATM,
   same exit geometry, same ₹220 cost), 20 seeded draws (seed 42), mean and range reported.
4. **Halves:** Jan–May and Jun–Oct separately.
5. **Month table** with month-end cumulative closes.
6. **Ex-top-3 stress** (total minus the 3 largest winners).
7. **Independent re-sum** of the total from the written trade CSV.
8. **Cost sensitivity:** total at ₹0 cost shown alongside, labelled as the no-cost counterfactual.

## Gate (pre-registered verdict rule)

A technique is **INTERESTING** only if: net at ₹220/trade > 0 in **BOTH** halves **AND** it beats
**both** placebos **AND** the timing audit shows **0** violations. Otherwise **DEAD** (fails on
economics: net ≤ 0 overall or in a half, or placebos not beaten) or **WEAK** (positive but fails a
gate leg). Expectancy/trade, win rate, trade count, avg hold bars, and cost as % of gross are
reported for every technique either way. The survivor pace is compared with the Bank engine book v8
(+₹77,196.50 Jan–Oct, ~₹7,720/mo) as context only — **no adoption decision is made in this study**.

---
# RESULTS (appended after scoring — see bank_scalp_run.py run of 2026-10-31)

Scored 2026-10-31 by `bank_scalp_run.py` — definitions above were frozen before the run; all controls ran in the same pass. Window actually scored: 2026-01-01 → 2026-10-27 (192 trading days; local spot data ends Oct 27). Premiums per 1 lot (30), cost ₹220/trade.

Controls status (all techniques): **timing/leak audit 0 violations**; independent re-sum from the written CSVs **matched exactly** for all three; NOT_COMPUTED legs were excluded and counted (S1 15/356 signals = 4.2%, S2 21/358 = 5.9%, S3 2/354 = 0.6% — missing ATM premium series on scattered days; no estimation anywhere).

## S1 OR-BURST (+25/−20, time-stop 3 bars)
- Trades computed: **341** (signals 356, NOT_COMPUTED 15); exits: target 134 / stop 174 / time_stop 33.
- **Jan–Oct net (₹220/trade): ₹-75,275.00** | expectancy ₹-220.75/trade | win rate 43.7% | target-hit 39.3% | avg hold 1.57 bars.
- Halves: Jan–May ₹-43,446.50 (n=158) | Jun–Oct ₹-31,828.50 (n=183). Both negative → gate fails.
- No-cost counterfactual (₹0 cost, NOT a result): ₹-255.00 overall (H1 ₹-8,686.50 / H2 ₹8,431.50). Total cost paid: ₹75,020 — for S1 that is ~100% of the loss (gross ≈ 0); 
- Placebos: lag (entry +1 bar) ₹-86,333.00 (n=341); random count-matched ×20 draws: mean ₹-91,177.73, range ₹-108,864.50..₹-71,060.00.
- Ex-top-3 stress: ₹-76,865.00 (removing the 3 best trades changes nothing — the loss is broad-based, not outlier-driven).
- Months (net / month-end cum): 01 -6,003 (cum -6,003) | 02 -14,828 (cum -20,832) | 03 -7,820 (cum -28,652) | 04 -2,520 (cum -31,172) | 05 -12,275 (cum -43,446) | 06 -19,292 (cum -62,738) | 07 -6,249 (cum -68,988) | 08 -6,588 (cum -75,575) | 09 6,448 (cum -69,126) | 10 -6,148 (cum -75,275). Every month-end cumulative close is negative from January onward.
- **VERDICT: DEAD. Net is negative in BOTH halves at the real ₹220 cost, so the pre-registered gate fails on its first leg. The honest nuance: at ₹0 cost S1 is almost exactly breakeven overall (−₹255 on 341 trades) — the OR-break signal itself carries ~no gross edge (Jun–Oct gross +₹8,431.50, Jan–May gross −₹8,686.50), and the entire −₹75,275 loss is the ₹75,020 of cost. It does beat both placebos (lag −₹86,333; random mean −₹91,178) — it loses *less* than random — but 'loses less than random' is not an edge, and the best single random draw (−₹71,060) beat it. Expectancy −₹220.75/trade ≈ exactly −1× the round-trip cost.**

## S2 LEVEL-REJECT (+22/−18, time-stop 4 bars)
- Trades computed: **337** (signals 358, NOT_COMPUTED 21); exits: target 106 / stop 195 / time_stop 36 (triggers: BAND 136, PDC 105, PDH 53, PDL 43).
- **Jan–Oct net (₹220/trade): ₹-104,306.50** | expectancy ₹-309.51/trade | win rate 35.0% | target-hit 31.5% | avg hold 1.65 bars.
- Halves: Jan–May ₹-37,939.50 (n=117) | Jun–Oct ₹-66,367.00 (n=220). Both negative → gate fails.
- No-cost counterfactual (₹0 cost, NOT a result): ₹-30,166.50 overall (H1 ₹-12,199.50 / H2 ₹-17,967.00). Total cost paid: ₹74,140 — and gross is negative too, so cost is not the whole story. 
- Placebos: lag (entry +1 bar) ₹-77,516.50 (n=337); random count-matched ×20 draws: mean ₹-94,050.22, range ₹-112,942.00..₹-72,206.50.
- Ex-top-3 stress: ₹-105,626.50 (removing the 3 best trades changes nothing — the loss is broad-based, not outlier-driven).
- Months (net / month-end cum): 01 -10,400 (cum -10,400) | 02 -8,842 (cum -19,242) | 03 -5,280 (cum -24,522) | 04 -6,857 (cum -31,380) | 05 -6,560 (cum -37,940) | 06 -9,688 (cum -47,628) | 07 -18,052 (cum -65,679) | 08 -20,166 (cum -85,845) | 09 -9,022 (cum -94,866) | 10 -9,440 (cum -104,306). Every month-end cumulative close is negative from January onward.
- **VERDICT: DEAD — the worst of the three. Negative in both halves AND negative gross (−₹30,166.50 even at ₹0 cost): the rejection signal is anti-predictive at a 5-min horizon, not merely cost-killed. Decisive evidence: the lag placebo (same signals entered one bar LATER) loses far less (−₹77,516.50 vs −₹104,306.50) and the random-entry mean (−₹94,050) also beats it — entering on the rejection bar is worse than entering at random. Win rate 35.0% against a +22/−18 geometry that needs ~45%+ before cost.**

## S3 IMPULSE (+22/−18, time-stop 2 bars)
- Trades computed: **352** (signals 354, NOT_COMPUTED 2); exits: target 126 / stop 211 / time_stop 15.
- **Jan–Oct net (₹220/trade): ₹-107,105.50** | expectancy ₹-304.28/trade | win rate 36.9% | target-hit 35.8% | avg hold 1.09 bars.
- Halves: Jan–May ₹-48,226.00 (n=199) | Jun–Oct ₹-58,879.50 (n=153). Both negative → gate fails.
- No-cost counterfactual (₹0 cost, NOT a result): ₹-29,665.50 overall (H1 ₹-4,446.00 / H2 ₹-25,219.50). Total cost paid: ₹77,440 — and gross is negative too, so cost is not the whole story. 
- Placebos: lag (entry +1 bar) ₹-103,817.50 (n=352); random count-matched ×20 draws: mean ₹-95,504.76, range ₹-110,032.00..₹-80,387.50.
- Ex-top-3 stress: ₹-108,425.50 (removing the 3 best trades changes nothing — the loss is broad-based, not outlier-driven).
- Months (net / month-end cum): 01 -9,120 (cum -9,120) | 02 -1,680 (cum -10,800) | 03 -20,390 (cum -31,190) | 04 -5,879 (cum -37,068) | 05 -11,158 (cum -48,226) | 06 -20,809 (cum -69,035) | 07 -11,641 (cum -80,676) | 08 -1,312 (cum -81,988) | 09 -6,280 (cum -88,268) | 10 -18,838 (cum -107,106). Every month-end cumulative close is negative from January onward.
- **VERDICT: DEAD. Negative in both halves and negative gross (−₹29,665.50 at ₹0 cost). Both placebos beat it: lag −₹103,817.50 and random mean −₹95,504.76 (random range −₹110,032..−₹80,388) vs the real −₹107,105.50 — impulse continuation entries are worse than count-matched random entries with identical exits. Win rate collapses in Jun–Oct (29.4%). Avg hold 1.09 bars: the typical impulse trade is decided inside the entry bar, where the −18 stop is noise-dominated.**

## Bottom line
All three scalping techniques are **DEAD** on Jan–Oct 2026 Bank Nifty premiums under the pre-registered gate. There is no survivor to compare: the least-bad, S1, runs at −₹7,528/month versus the engine book v8's +₹7,720/month, and its gross edge is ~zero — at this trade frequency (~1.8/day) the ₹220 round-trip cost alone is ₹75k over 10 months. S2 and S3 lose money even before cost and are beaten by their own placebos, so no exit-geometry tuning can rescue them (tuning a negative-gross, placebo-beaten signal would be curve-fitting a dead mechanism). This confirms, with controls, the standing design intuition: in this channel the edge lives in level-based entries with a +90 target held for hours (book v8), not in 1–2-bar premium scalps. No adoption question arises; November paper BNF-PAPER-V1 is untouched.

Data note: the local dataset fully supported intraday exit scoring (ATM premium series exist for 13–19 strikes/day, 75 bars/day). The only gaps: Oct 28–30 spot days are absent locally (window ends Oct 27) and Red bands exist only from Jul 2 (S2 ran PDH/PDL/PDC-only Jan–Jun, as frozen).
