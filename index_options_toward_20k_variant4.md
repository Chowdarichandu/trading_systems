# Variant 4 — Hit-quality filters on NS1 second legs and NS2 afternoon legs

Paper only, no orders, no stocks. Index OPTIONS only, October 2026 premiums only.
Nifty and Bank Nifty separately, never pooled as a portfolio.
**Nothing is adopted on October alone.** October is in-sample for these filters,
and the filtered subsets are tiny (0–7 legs per index) — one trade swings FT by
14–100 points. November 2026 paper (from 2026-11-02) remains validation, with any
filter frozen as written here, not re-tuned on November.

## Verdict up front — plainly

**No filter lifts full-target (FT) rate to >= 50% while keeping net at or above
the base and frequency at or above 2/week, on either index.**

- **Nifty:** the base full track is 32.0% FT. The best filter, (a-NS), lifts it
  only to 41.2% — still below 50% — and that lift rests on **one kept extra leg**
  (see below). Every other filter leaves Nifty FT at 32.0–38.9%.
- **Bank:** the base full track already passes FT at 58.3% with net +₹17,520.
  Every filter that keeps FT above 50% on Bank does so with net **below** the
  base (best such: (b) at 59.1% FT but net −₹760 below base; (c) at 57.9% FT but
  net −₹4,000 below base; (a) at 52.6% FT but net −₹8,200 below base). No filter
  improves Bank on all criteria together; the unfiltered base is best on Bank.
- On the extra-leg subset alone, **every** filter collapses subset frequency
  below 2/week on at least one index (and on both indices for (a) and (c)).
  On the full track, frequency never falls below 2/week — but only because the
  untouched unified base (4.44 / 5.00 per week) carries it. That is not a
  filter success; it is the base doing the work.

Closest, and still a fail: **(a-NS) on Nifty only** — full FT 32.0% → 41.2%,
full net +₹8,026.50 → +₹19,799.75, full frequency 6.94 → 4.72/week — built on a
single kept leg, while the same filter **hurts Bank** (net +₹17,520 → +₹9,320).
A one-leg, one-index lift that reverses on the other index is a deletion
artefact, not a quality filter. It is recorded here as a watch item for
November paper, not as a keep.

## Frozen rules — written before any filter outcome was computed

### Population and base

- **Extra legs (the only legs any filter touches):** the 15 October premium
  legs in `index_options_newsetup_premium_october_trades.csv` with
  (family NS1, leg `second`) or (family NS2, leg `afternoon_rescan`):
  Nifty 9 (NS1 second 5 + NS2 afternoon 4), Bank 6 (NS1 second 5 + NS2
  afternoon 1). Morning/base legs and unified-base legs are never filtered.
- **Unified base alone (task-given fallback, verified from the source file):**
  34 unique-once trades — Nifty 16, FT 6 (37.5%), net +₹14,169.75, 4.44/week;
  Bank 18, FT 10 (55.6%), net +₹11,040.00, 5.00/week; combined +₹25,209.75.
  Verified by re-parsing `index_options_october_UNIQUE_trades.md` (34 rows,
  totals match to the rupee).
- **Variant-4 base (V4B, primary comparison base):** no other-variant
  unified+NS file was found in `~/workspace/trading/` at run time, so V4B was
  constructed here as unified base **plus** the 15 extra legs counted as
  additional legs. A second trade on a day is a second trade even if it shares
  the date+index+direction key of a unified trade, so V4B is a **legs** track,
  not a unique-keys track — stated, not hidden. V4B: Nifty 25 trades, FT 8
  (32.0%), net +₹8,026.50, 6.94/week; Bank 24 trades, FT 14 (58.3%),
  net +₹17,520.00, 6.67/week. The unified-alone base is shown alongside
  throughout so the construction can be undone.
- **Scoring (unchanged from the premium file):** premium FT = premium target
  exit only; square-off greens never count as FT. Net per 1 lot (Nifty 65,
  Bank 30), −50/+90 overlay, ₹220 assumed cost. Frequency = trades / 18 days
  × 5. No filter is combined with another; each is scored alone.

### Filter (a) — first-leg gate

Two nested readings, both frozen, both reported (not chosen after seeing
results):

- **(a-NS) not-stop:** keep the extra leg iff that day's first leg exited as
  anything except a stop (target or square-off).
- **(a-T) target-only:** keep iff that day's first leg exited as a target.

First leg, **NS-track reading (primary):** for an NS1 second leg, the first
leg is that day's NS1 `base_S1` premium leg. For an NS2 afternoon leg, **no
morning leg exists by NS2 construction** (afternoon legs fire only on
no-morning-trade days), so under this reading (a) keeps **0 of 5** NS2
afternoon legs. That is a finding about (a), not a gap: (a) is, by
construction, a filter for second legs, not for rescan legs on empty days.

First leg, **unified reading (sensitivity, also frozen):** the earliest
unified-base trade that date+index (by entry time); if no unified trade
exists that date+index, the gate fails. Note: 21 Oct has two unified trades
per index (CE stop, then PE target); this reading uses the **first**
(earliest) one, not the preceding one. The two readings agree on every NS1
second leg and differ on exactly one extra leg (Nifty 23 Oct NS2 afternoon:
NS-track drops it, unified reading keeps it because the unified first leg
that day was a square-off, not a stop).

### Filter (b) — room >= 2x stop distance

Keep iff spot room_ratio >= 2.0, where room = distance from the signal-bar
close to the next PD level in direction (CE: smallest PD level above the
close; PE: largest PD level below the close), PD = previous trading day's
daily high/close/low from `data/progressive/<INDEX>/spot_daily.csv`, and
spot risk = |entry_spot − stop_spot| from the NS Jan–Oct spot file (the
frozen NS spot-risk definition, not the premium 50-point stop). The base NS
gate was >= 1.5; (b) tightens it to >= 2.0. If no PD level lies in direction
(price already beyond all PD levels), room is infinite and the leg **keeps**
— this is the NS definition (room = infinity), and it matters: 5 of the 15
extra legs have infinite room (see appendix).

### Filter (c) — premium not already extended

**Exact frozen rule (no lookahead):** for the traded contract, from its
cached 5-min option candles for that day, let low_to_entry / high_to_entry
be the minimum low / maximum high over candles with time <= the entry
candle (entry candle included). Position =
(entry_premium − low_to_entry) / (high_to_entry − low_to_entry).
**Keep iff position <= 0.67** — i.e. the entry premium is NOT in the top
third of the contract's premium range so far that day. Range 0 keeps (no
extension measurable). The full-day range is **not** used: it is not known
at entry time.

**Entry-candle correction (found while building (c), applied before
scoring):** the premium file's `entry_time` column is **not** the premium
entry candle time. It is inherited from the NS spot file, where
`newsetups_score.replay()` sets `entry_time` to the **exit** bar time.
The premium scorer (`newsetup_premium_score.score_premium`) defines premium
entry as the first option candle with time **> signal_time**, and that is
what (c) uses. Verified for all 15 legs: the first candle after the signal
opens exactly at the file's `entry_premium` (within ₹0.06). The corrected
premium entry times are in the legs CSV (`prem_entry_time`). Using the
file's `entry_time` column for (c) would have measured the wrong candle and
is not done here. This correction does not change any premium net or FT —
those were scored by the original scorer — it only fixes (c)'s range window.

## Base: extra legs unfiltered, and the V4B full track

| Track | Nifty: trades / FT / net / wk | Bank: trades / FT / net / wk |
|---|---|---|
| Unified base alone | 16 / 6 (37.5%) / +₹14,169.75 / 4.44 | 18 / 10 (55.6%) / +₹11,040.00 / 5.00 |
| Extra legs only (NS1 second + NS2 afternoon) | 9 / 2 (22.2%) / −₹6,143.25 / 2.50 | 6 / 4 (66.7%) / +₹6,480.00 / 1.67 |
| — of which NS1 second only | 5 / 1 (20.0%) / −₹1,698.00 / 1.39 | 5 / 3 (60.0%) / +₹4,000.00 / 1.39 |
| — of which NS2 afternoon only | 4 / 1 (25.0%) / −₹4,445.25 / 1.11 | 1 / 1 (100%) / +₹2,480.00 / 0.28 |
| **V4B = unified + extra (primary base)** | **25 / 8 (32.0%) / +₹8,026.50 / 6.94** | **24 / 14 (58.3%) / +₹17,520.00 / 6.67** |

Reading: the extra legs drag Nifty down (unified +₹14,169.75 → V4B +₹8,026.50,
FT 37.5% → 32.0%) and lift Bank up (unified +₹11,040 → V4B +₹17,520, FT
55.6% → 58.3%). Any filter is therefore fighting a different problem on each
index: Nifty needs the extra legs to stop losing; Bank needs them not to be
spoiled. A filter that helps one index and hurts the other — which is what
(a) does — is not a system filter.

## Results — filtered extra subset, and the resulting full track

Full track = unified base (untouched) + filtered extra legs. "Below base"
below means below the V4B full-track net. FT% on subsets of 0–2 legs is
reported as-is and must not be over-read.

### (a-NS) — first leg not a stop

| | Nifty extra subset | Nifty full track | Bank extra subset | Bank full track |
|---|---|---|---|---|
| Kept | 1 / 9: 12 Oct NS1 second, target, +₹5,630 | 17 trades, FT 7 (41.2%), net +₹19,799.75, 4.72/wk | 1 / 6: 1 Oct NS1 second, stop, −₹1,720 | 19 trades, FT 10 (52.6%), net +₹9,320.00, 5.28/wk |
| vs V4B | subset 0.28/wk (collapses) | FT +9.2 pts, net +₹11,773.25, wk −2.22 | subset 0.28/wk (collapses) | FT −5.7 pts, net −₹8,200.00 (below base) |

Kept legs are NS1 only; NS2 afternoon kept 0/5 under the NS-track reading.
Nifty's FT lift (32.0% → 41.2%) still misses 50%, and it is one leg: the
12 Oct second leg, whose first leg exited via square-off (+₹4,213 premium),
not a target. Bank's kept leg is the opposite story: first leg was a target
(1 Oct base +₹2,480), second leg stopped (−₹1,720). Target-first does not
predict a second target on either index.

### (a-T) — first leg a target only

| | Nifty extra subset | Nifty full track | Bank extra subset | Bank full track |
|---|---|---|---|---|
| Kept | 0 / 9 | = unified alone: 16, FT 6 (37.5%), +₹14,169.75, 4.44/wk | 1 / 6: 1 Oct NS1 second, stop, −₹1,720 | 19 trades, FT 10 (52.6%), net +₹9,320.00, 5.28/wk |

Nifty: no second leg in October follows a target first leg (the only
target-first second leg is Bank 1 Oct, and it stopped). A target-only gate
deletes the entire Nifty extra population without lifting FT anywhere.
**Fail on both indices.**

### (a) under the unified-first-leg reading (sensitivity)

| | Nifty extra subset | Nifty full track | Bank extra subset | Bank full track |
|---|---|---|---|---|
| (a-NS) unified | 2 / 9, FT 1 (50.0%), net +₹2,160.00, 0.56/wk | 18 trades, FT 7 (38.9%), net +₹16,329.75, 5.00/wk | 1 / 6, FT 0 (0%), net −₹1,720.00, 0.28/wk | same as NS-track Bank above |
| (a-T) unified | 0 / 9 | = unified alone | 1 / 6, FT 0, net −₹1,720.00 | same as NS-track Bank above |

The only difference from the NS-track reading is Nifty 23 Oct NS2
afternoon (stop, −₹3,470), kept here because the unified first leg that day
was a square-off. It dilutes the Nifty subset FT from 100% (1/1) to 50.0%
(1/2) and the full FT from 41.2% to 38.9%. Either reading: **no 50% full-track
FT on Nifty, net below base on Bank. Fail.**

### (b) — room_ratio >= 2.0

| | Nifty extra subset | Nifty full track | Bank extra subset | Bank full track |
|---|---|---|---|---|
| Kept | 7 / 9, FT 2 (28.6%), net −₹5,755.25, 1.94/wk | 23 trades, FT 8 (34.8%), net +₹8,414.50, 6.39/wk | 4 / 6, FT 3 (75.0%), net +₹5,720.00, 1.11/wk | 22 trades, FT 13 (59.1%), net +₹16,760.00, 6.11/wk |

Dropped legs: Nifty 5 Oct (ratio 1.703, square-off +₹345.50) and 28 Oct
(1.867, square-off −₹733.50); Bank 1 Oct (1.685, stop −₹1,720) and 8 Oct
(1.874, **target +₹2,480**). Kept legs include all 5 infinite-room legs.
Net effect vs V4B: Nifty +₹388 (dropping a −₹388 pair), Bank −₹760
(dropping a target to save a stop). Nifty FT moves 22.2% → 28.6% on the
subset and 32.0% → 34.8% full — nowhere near 50%. Bank FT stays above 50%
but net falls below base. **Fail on both indices.** Room tightening to 2.0x
is nearly inert here because most extra legs already clear 2.0x or have
infinite room; it is not a hit-quality gate for this population.

### (c) — entry premium not in the top third of the range so far

| | Nifty extra subset | Nifty full track | Bank extra subset | Bank full track |
|---|---|---|---|---|
| Kept | 0 / 9 | = unified alone: 16, FT 6 (37.5%), +₹14,169.75, 4.44/wk | 1 / 6, FT 1 (100%), net +₹2,480.00, 0.28/wk | 19 trades, FT 11 (57.9%), net +₹13,520.00, 5.28/wk |

Positions (entry premium within the range so far) for the 15 legs:
Nifty 0.717, 0.992, 0.760, 0.753, 0.846, 0.850, 0.990, 0.833, 0.804;
Bank 0.776, 0.871, 0.836, 0.890, **0.383** (kept: 27 Oct PE target), 0.865.
**14 of 15 extra-leg entries sit above 0.67** — second/afternoon entries in
October are systematically near the top of their contract's premium range
so far that day (a continuation entry, by construction, buys after the
premium has already moved). A top-third gate is therefore not a filter for
this population; it is close to a ban on second/afternoon legs, keeping
exactly one leg (a Bank target) and deleting five other targets (Nifty
12 Oct and 21 Oct, Bank 8 Oct, 12 Oct, 21 Oct). The kept subset's 100% FT
is 1/1 and meaningless, and subset frequency collapses to 0 / 0.28 per
week. **Fail on both indices.** A usable extension concept, if one exists,
would need a different definition (e.g. premium move vs spot move, or vs
the first leg's premium) — that is a new frozen variant, not a loosening of
this one after seeing the result, and it is not scored here.

## Per-filter verdicts

| Filter | Nifty | Bank | Overall |
|---|---|---|---|
| (a-NS) not-stop | Closest, still fails: full FT 41.2% < 50%; subset 1 leg, 0.28/wk | Fails: full net below base, FT falls | **Fail** — inconsistent across indices, one-leg lift |
| (a-T) target-only | Fails: keeps 0 legs | Fails: keeps 1 stop leg, net below base | **Fail** |
| (a) unified reading | Fails: full FT 38.9% < 50% | Fails: same as NS-track Bank | **Fail** — reading does not change the verdict |
| (b) room >= 2.0x | Fails: full FT 34.8% < 50% | Fails: FT passes but net below base | **Fail** — nearly inert (infinite room + already-clear legs) |
| (c) extension <= 0.67 | Fails: keeps 0 legs | Fails: keeps 1 leg, net below base | **Fail** — top-third gate is a near-ban for this population |

**No filter is kept, recommended, or adopted.** The unfiltered V4B track
(Nifty 32.0% FT, Bank 58.3% FT) remains the comparison base, and on Bank
even V4B is beaten by no filter at all. Nothing here earns November-paper
adoption; at most, (a-NS) as frozen (NS-track reading) could be logged in
November paper alongside the unfiltered track to see whether "first leg
not a stop" predicts second-leg quality out of sample — but a November log
is not a claim, and (a-NS) must not be combined with (b) or (c) on the
strength of October.

## Caveats

1. October is 18 days; the filtered populations are 9 Nifty / 6 Bank extra
   legs, and filtered subsets are 0–7 legs. FT percentages on such counts
   are unstable by construction. The Jan–Oct spot FT problem (NS1 second
   legs 31.6% Nifty / 40.0% Bank) is the weight-bearing evidence; October
   premiums confirm the direction on Nifty (extra legs 22.2%) but Bank's
   October extra legs (66.7%) run against it on 6 legs — neither small
   October cell overturns the Jan–Oct picture.
2. All premium nets are per 1 lot with the assumed ₹220 cost and the
   −50/+90 overlay; they are comparable across filters but are not any
   version's native exit rule. Spot room ratios use the NS spot-risk
   definition, not the premium 50-point stop; a room rule stated in premium
   points (room vs 50) would be a different, unscored filter.
3. (c) uses only cached option candles (14 premium-named files + the
   legacy `candles_Nifty_50_22500PE_2026-10-23.json` for Nifty 23 Oct);
   no new fetch was run and no candle was invented. All 15 legs are
   computed under (c) — zero NOT_COMPUTED.
4. The `entry_time` correction above affects only (c)'s window. It does not
   alter any previously reported premium net, FT, or trade count.
5. Real money made = ₹0. No orders were placed, no positions exist.

## Files delivered

- This report: `index_options_toward_20k_variant4.md`
- Leg-level diagnostics (all 15 extra legs: signal close, PD levels, spot
  risk, room, room_ratio, NS-track and unified first-leg outcomes, premium
  entry time, extension range/position, keep/drop per filter, outcome):
  `index_options_toward_20k_variant4_legs.csv`
- Scoring script (frozen rules in its docstring, before the computation):
  `variant4_score.py`
- Sources (not edited): `index_options_newsetups_report.md`,
  `index_options_newsetup_premium_october_trades.csv`,
  `index_options_progressive_tuning.md`,
  `index_options_october_UNIQUE_trades.md`,
  NS spot files `index_options_newsetup_ns1/ns2_trades_jan_oct_2026.csv`,
  spot cache `data/progressive/<INDEX>/spot_5m.csv` and `spot_daily.csv`,
  cached option candles under `v4_options_oct_data/`.

## Appendix — all 15 extra legs with filter diagnostics

FT = premium full target (1 = target). Room ratio blank = infinite room
(no PD level in direction) → keeps under (b). Ext position blank would mean
no cached candles (none occur). ns_first = NS-track first-leg premium exit
(blank for NS2: no morning leg). uni_first = earliest unified-base trade
that date+index (blank: none).

| Index | Date | Family | Dir | Signal | Prem entry | Exit | FT | Net / 1 lot | Room ratio | ns_first | uni_first | Ext pos | (a-NS) | (a-T) | (b) | (c) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| NIFTY | 2026-10-05 | NS1 second | PE | 10:20 | 10:25 | square_off | 0 | +₹345.50 | 1.703 | stop | stop | 0.717 | DROP | DROP | DROP | DROP |
| NIFTY | 2026-10-07 | NS1 second | CE | 10:25 | 10:30 | stop | 0 | −₹3,470.00 | 2.366 | stop | stop | 0.992 | DROP | DROP | KEEP | DROP |
| NIFTY | 2026-10-12 | NS1 second | PE | 10:00 | 10:05 | target | 1 | +₹5,630.00 | 8.230 | square_off | square_off | 0.760 | KEEP | DROP | KEEP | DROP |
| NIFTY | 2026-10-27 | NS1 second | CE | 10:00 | 10:05 | stop | 0 | −₹3,470.00 | inf | stop | stop | 0.753 | DROP | DROP | KEEP | DROP |
| NIFTY | 2026-10-28 | NS1 second | CE | 12:40 | 12:45 | square_off | 0 | −₹733.50 | 1.867 | stop | stop | 0.846 | DROP | DROP | DROP | DROP |
| BANKNIFTY | 2026-10-01 | NS1 second | CE | 11:35 | 11:40 | stop | 0 | −₹1,720.00 | 1.685 | target | target | 0.776 | KEEP | KEEP | DROP | DROP |
| BANKNIFTY | 2026-10-06 | NS1 second | CE | 10:30 | 10:35 | stop | 0 | −₹1,720.00 | 4.982 | stop | stop | 0.871 | DROP | DROP | KEEP | DROP |
| BANKNIFTY | 2026-10-08 | NS1 second | PE | 12:20 | 12:25 | target | 1 | +₹2,480.00 | 1.874 | stop | stop | 0.836 | DROP | DROP | DROP | DROP |
| BANKNIFTY | 2026-10-12 | NS1 second | PE | 10:25 | 10:30 | target | 1 | +₹2,480.00 | 6.162 | stop | stop | 0.890 | DROP | DROP | KEEP | DROP |
| BANKNIFTY | 2026-10-27 | NS1 second | PE | 13:05 | 13:10 | target | 1 | +₹2,480.00 | 5.891 | stop | stop | 0.383 | DROP | DROP | KEEP | KEEP |
| NIFTY | 2026-10-01 | NS2 afternoon | PE | 12:45 | 12:50 | square_off | 0 | −₹3,135.25 | inf | — | stop | 0.850 | DROP | DROP | KEEP | DROP |
| NIFTY | 2026-10-14 | NS2 afternoon | PE | 13:10 | 13:15 | stop | 0 | −₹3,470.00 | 8.235 | — | — | 0.990 | DROP | DROP | KEEP | DROP |
| NIFTY | 2026-10-21 | NS2 afternoon | PE | 11:35 | 11:40 | target | 1 | +₹5,630.00 | inf | — | stop | 0.833 | DROP | DROP | KEEP | DROP |
| NIFTY | 2026-10-23 | NS2 afternoon | PE | 11:35 | 11:40 | stop | 0 | −₹3,470.00 | inf | — | square_off | 0.804 | DROP (KEEP under unified a-NS) | DROP | KEEP | DROP |
| BANKNIFTY | 2026-10-21 | NS2 afternoon | PE | 11:35 | 11:40 | target | 1 | +₹2,480.00 | inf | — | stop | 0.865 | DROP | DROP | KEEP | DROP |

Note on the (a) columns above: they show the NS-track reading. Under the
unified reading, (a-NS) additionally keeps Nifty 23 Oct NS2 afternoon and
nothing else; (a-T) is unchanged on every leg.
