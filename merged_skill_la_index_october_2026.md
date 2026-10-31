# Merged backtest — Day Trader Skill + (lA), Bank Nifty + Nifty, October 2026 only

Paper only. No orders placed, no live trading, no live-trading recommendation.
**NOT a new adopted version. October alone is NOT adoption** — a merged version
would still need unseen-month validation on net + win rate + frequency together
before any adoption claim. Nothing here is mixed into v4 / (lA) totals as an
adopted series, and nothing here changes the (lA) verdict (best kept, not adopted).

## Frozen merged definition (stated before scoring; provisional, NOT Chandu's rule)

- **Scope:** NIFTY and BANKNIFTY only, NO stocks. **1–28 October 2026 only**
  (18 trading days, 5 ISO weeks W40–W44, same window as the earlier October
  standalone reports). 29 Oct 2026 is excluded — still in progress that day
  and not in the cache. Data: Upstox 5-min cache already in
  `data/progressive/` — no fresh fetch was needed, no day was missing.
- **Provisional cash rules (as in the earlier capped runs, NOT Chandu's live
  options rules):** 100 shares equivalent, ₹40/trade cost, signal-candle stop,
  2× target, square-off 15:10, short paper-only, one trade/instrument/day
  after dedup. Index nets are point-scaled cash-equivalents (100 × index
  points), NOT portfolio rupees.
- **Source A — Day Trader skill index candidates:** OR-only signals passing
  the V4-style filters used in the capped-v2 runs (bias-aligned, room
  ≥ 200×scale to the next PD level, PD bound: CE close < PDH, PE close < PDL),
  recomputed by `progressive_capped_v2.candidates_for_month(2026, 10)`,
  index symbols only. Setup rank 0.
- **Source B — (lA) trades:** exactly as in
  `nifty_cluster1_extended_window_sweep.md` — BN-confirmed rescan morning +
  band-filtered re-entry (re-entry risk in [10, rescan risk], morning
  scan-skip to 11:30, afternoon stop-on-first-fail to 15:05), PE replay
  (entry = next bar open, stop = signal high, target = entry − 2×risk,
  stop before target per bar including the entry bar, square-off 15:10,
  ₹40 per leg). (lA) was defined for **NIFTY PE only**.
  - **Nifty (lA), faithful to the file:** confirming break = first Bank
    Nifty bar 09:30–11:30 closing below Bank OR low; rescan = first Nifty
    bar at/after that break, ≤11:30, closing below Nifty OR low AND below
    PDL, with OR width ≤ 360×scale and room ≥ 200×scale (scale = prev
    close / 55000), v4 mode. If the rescan morning targets, day net =
    morning net (no re-entry). If it stops, the (lA) re-entry scan above
    applies; day net = morning net + re-entry net if a re-entry trades,
    else morning net alone. Each leg carries its own ₹40 cost in the replay.
  - **Bank Nifty (lA), MIRROR — provisional adaptation, NOT the original
    (lA):** roles swapped, every other parameter carried over unchanged.
    Confirming break = first Nifty bar 09:30–11:30 closing below Nifty OR
    low; rescan = first Bank bar at/after that break, ≤11:30, closing
    below Bank OR low AND below Bank PDL, with OR width ≤ 360×scale_bank
    and room ≥ 200×scale_bank (scale_bank = Bank prev close / 55000, the
    same symbol-agnostic formula used in the capped runs). Re-entry:
    candidates closing below Bank OR low, band risk in [10, rescan risk],
    morning scan-skip to 11:30, afternoon stop-on-first-fail to 15:05,
    PE replay. The mirror is reconstructable by this role-swap, so both
    symbols are reported — but it must not be quoted as "original (lA)".
- **(lA) candidate encoding (provisional, frozen before scoring):** one
  candidate per symbol+date where a rescan morning exists, regardless of
  morning exit. Direction PE. Setup rank **1** (morning is a setup2-class
  breakdown; Skill OR is 0 — this rank is a labelling choice, not a
  measured conviction score). Prospective net target = morning target
  net (2 × morning risk × 100 − ₹40, signal-time only). Room ratio =
  `room_ratio` from the capped engine on the rescan signal close (see
  artefact note below). Bias-strong = 1 if that day's bias ≠ neutral.
  Realised net = (lA) day net. Exit shown as morning exit + re-entry exit
  in the trade list, not as a single-leg exit.
- **Dedup:** same symbol+date = one trade; **(lA) takes priority over
  Skill** on a conflict (stated before scoring).
- **Cap and filter:** prospective net target ≥ ₹500, then rank by
  setup_rank, bias-strong, room_ratio, prospective net target (V5 order,
  signal-time/prospective only). Cap: max 3 index trades/ISO week, max
  1 trade/symbol/week. With only 2 symbols the attainable max is
  **2/week in practice**, not 3/week. Results gate NEUTRAL.
- **Win rate in this report = net > 0 (green) for ALL series**, so (lA)
  day greens (morning + re-entry combined) are comparable to Skill
  targets. Target/stop/square-off counts are shown for Skill; for (lA)
  the morning and re-entry exits are listed separately. A square-off
  that ends positive would count as green here but would not have
  counted as a target in the capped reports — no such (lA) case occurs
  in October (all (lA) days end in target or stop, see trade list).

## Pools before cap (transparency, not series)

- Skill index candidates in October: **3** (Bank 1 Oct CE, Nifty 8 Oct PE,
  Nifty 28 Oct PE) — identical to the Skill index capped-v2 pool, which
  is why the Skill-only series below reproduces the known October
  Skill index numbers exactly.
- (lA) candidates in October: **5** (Bank 7 Oct, Nifty 8 Oct, Bank 21 Oct,
  Bank 23 Oct, Nifty 23 Oct). All 5 pass the ₹500 prospective filter.
- Pooled, deduped ((lA) wins the one overlap, Nifty 8 Oct): **7**
  candidates. Uncapped pooled net = ₹71,035 (Skill ₹16,610 + (lA)
  ₹59,865 − Skill 8 Oct ₹5,440 dropped by dedup). The cap then drops
  one more trade (see below), giving the merged capped total.
- (lA) days with NO rescan morning (13 of 18 days × 2 symbols, in
  effect): no confirming break, or no qualifying breakdown at/after
  the break. Notable: Nifty 28 Oct has a V4/Skill PE stop (−₹5,470) but
  **no (lA) rescan morning**, so the Skill 28 Oct trade survives in
  the merged series untouched. Nifty 26 Oct is a CE reclaim day, so
  (lA) PE correctly has no trade there.

## (lA) candidates in detail (all 5, before cap)

| Date | Symbol | Rescan signal (confirm break) | Morning exit / net | Re-entry | Day net | Prospective target net |
|---|---|---|---|---|---|---|
| 2026-10-07 | BANKNIFTY | 09:35 (Nifty break 09:35) | stop / −₹7,475 (risk 74.35) | **None** — no bar closes below Bank OR low after the 09:40 stop, to 15:05 | −₹7,475 | ₹14,830 |
| 2026-10-08 | NIFTY | 11:25 (Bank break 11:25) | target / +₹11,690 (risk 58.65) | n/a (morning targets) | +₹11,690 | ₹11,690 |
| 2026-10-21 | BANKNIFTY | 11:15 (Nifty break 10:05) | target / +₹20,200 (risk 101.20) | n/a | +₹20,200 | ₹20,200 |
| 2026-10-23 | BANKNIFTY | 09:55 (Nifty break 09:30) | target / +₹24,060 (risk 120.50) | n/a | +₹24,060 | ₹24,060 |
| 2026-10-23 | NIFTY | 10:05 (Bank break 09:45) | target / +₹11,390 (risk 57.15) | n/a | +₹11,390 | ₹11,390 |

**(lA) uncapped: 5 trades, 4 green, net +₹59,865, expectancy +₹11,973.**
**Key October fact: the (lA) re-entry leg never fires in October.**
Four mornings target outright; the one morning that stops (Bank 7 Oct)
finds no re-entry candidate at all. This merge therefore tests the
(lA) **rescan morning** in October, not the (lA) re-entry rule. Any
claim about the re-entry leg from October would be fabrication.

Note on the 8 Oct Nifty trade: the (lA) rescan trade (+₹11,690, signal
11:25) is NOT the V4/Skill 8 Oct trade (+₹5,440, earlier signal). Same
day, same direction, different signal and risk — dedup keeps the (lA)
version, a +₹6,250 difference on that date, stated here rather than
hidden in the merged total.

## Series results — capped (the series, not the pools)

### Skill-only (index, capped) — reproduces the known October Skill index exactly

| | Trades | Green (net>0) | Net ₹ | Expectancy ₹ |
|---|---|---|---|---|
| **Total** | **3** | **2 / 66.7%** | **+₹16,610** | **+₹5,536.67** |
| Nifty | 2 | 1 / 50.0% | −₹30 | −₹15.00 |
| Bank Nifty | 1 | 1 / 100% | +₹16,640 | +₹16,640.00 |

Trades: Bank 1 Oct OR CE target +₹16,640; Nifty 8 Oct OR PE target
+₹5,440; Nifty 28 Oct OR PE stop −₹5,470. Max drawdown ₹5,470.

### (lA)-only (capped) — 4 of 5 candidates survive the cap

| | Trades | Green (net>0) | Net ₹ | Expectancy ₹ |
|---|---|---|---|---|
| **Total** | **4** | **3 / 75.0%** | **+₹35,805** | **+₹8,951.25** |
| Nifty | 2 | 2 / 100% | +₹23,080 | +₹11,540.00 |
| Bank Nifty | 2 | 1 / 50.0% | +₹12,725 | +₹6,362.50 |

Trades: Bank 7 Oct −₹7,475; Nifty 8 Oct +₹11,690; Bank 21 Oct +₹20,200;
Nifty 23 Oct +₹11,390. Max drawdown ₹7,475.
**Dropped by cap: Bank 23 Oct +₹24,060.** Week W43 already has a Bank
trade (21 Oct), and the 1/symbol/week cap allows only one. Ranking
decides it: both are setup_rank 1 and room_ratio 1.0 (see artefact
below), so **bias-strong breaks the tie — 21 Oct is bias-strong (1),
23 Oct is not (0)** — and the larger prospective target (₹24,060 vs
₹20,200) never gets reached in the ranking order. This is cap
behaviour under the frozen ranking, not a judgement that 21 Oct was
a better trade in hindsight.

### Merged Skill + (lA) (capped) — the requested series

| | Trades | Green (net>0) | Net ₹ | Expectancy ₹ |
|---|---|---|---|---|
| **Total** | **6** | **4 / 66.7%** | **+₹46,975** | **+₹7,829.17** |
| Nifty | 3 | 2 / 66.7% | +₹17,610 | +₹5,870.00 |
| Bank Nifty | 3 | 2 / 66.7% | +₹29,365 | +₹9,788.33 |

Trades, in date order:

| Date | Symbol | Source | Direction / setup | Exit | Net ₹ |
|---|---|---|---|---|---|
| 2026-10-01 | BANKNIFTY | Skill | CE / OR breakout | target | +₹16,640 |
| 2026-10-07 | BANKNIFTY | (lA) mirror | PE / rescan, morning stop, no re-entry | stop (day) | −₹7,475 |
| 2026-10-08 | NIFTY | (lA) | PE / rescan | target | +₹11,690 |
| 2026-10-21 | BANKNIFTY | (lA) mirror | PE / rescan | target | +₹20,200 |
| 2026-10-23 | NIFTY | (lA) | PE / rescan | target | +₹11,390 |
| 2026-10-28 | NIFTY | Skill | PE / OR breakdown | stop | −₹5,470 |

Frequency: 6 trades over 5 ISO weeks = **1.2/week** (W40: 1, W41: 2,
W42: 0, W43: 2, W44: 1). Max drawdown ₹7,475 (peak after 23 Oct
₹52,445, final ₹46,975).
**Reconciliation (exact):** (lA) capped ₹35,805 + Skill capped ₹16,610
− Skill 8 Oct ₹5,440 (dropped by dedup, (lA) 8 Oct kept instead)
= **₹46,975**. The merged total is fully explained by the two capped
series plus that one dedup swap — there is no extra merge gain beyond
it, and the cap drop of Bank 23 Oct (₹24,060) is already inside the
(lA) capped figure, not an additional merged loss.

## Comparison to the already-known October index numbers

| Series (October 2026, index only) | Trades | Win / green | Net ₹ |
|---|---|---|---|
| V4 index capped-v2 (comparison only — V4 is NOT a source in this merge) | 7 | 71.4% targets | +₹51,825 |
| V5 index October (comparison only) | 7 | 71.4% | +₹51,825 |
| Skill index capped-v2 (comparison / Source A alone) | 3 | 66.7% | +₹16,610 |
| **(lA)-only capped (Source B alone)** | **4** | **75.0% green** | **+₹35,805** |
| **Merged Skill + (lA) capped** | **6** | **66.7% green** | **+₹46,975** |

**Verdict on October: merged TRAILS V5/V4 October by ₹4,850
(₹46,975 vs ₹51,825), on one fewer trade, at a lower green rate
(66.7% vs 71.4%).** It beats Skill alone by ₹30,365, but that is
almost entirely the (lA) leg, not a synergy: merged = (lA) capped +
Skill capped − one dedup swap (above).
**Is it a genuine merge effect or dedup overlap? Dedup overlap, plus
cap composition — not synergy.** The only same-day overlap is Nifty
8 Oct, where (lA) replaces Skill (+₹6,250 on that date). Everything
else in the merged total is just the two capped series added together,
minus the Bank 23 Oct trade the cap already removed from (lA) alone.
And the merged total trails V4/V5 October mainly because **neither
source contains the V4 setup3 index trades** (Bank 26 Oct +₹10,520,
Bank 13 Oct −₹3,730, both in V4 index October but in neither the
Skill OR pool nor the (lA) PE pool). Comparing a Skill+(lA) pool to a
V4 pool and calling the gap a merge failure would misread the pools;
the honest statement is: on the Skill+(lA) pools, October caps at
₹46,975, and that pool does not contain V4's October setup3 trades.

## Artefacts and caveats that must travel with these numbers

- **Room ratio is dead in this merge.** Every (lA) rescan close is
  below PDL (required by the rescan rule), so there is no PD level
  below the signal close, room is infinite, and the capped engine
  maps infinite room to room_ratio 1.0. All five (lA) candidates (and
  all Skill PE candidates) therefore tie at 1.0, and ranking among
  them is decided by bias-strong, then prospective target. The
  Bank W43 tie (21 Oct over 23 Oct) is a direct consequence.
- **Bank (lA) is a mirror, not the original.** Its October record is
  3 candidates (7 Oct stop, 21 Oct target, 23 Oct target-capped-out),
  2 capped trades, +₹12,725 capped — but it has never been validated
  outside October, and the mirror assumption (Nifty confirmation for
  Bank, same width/room thresholds with Bank scale) is provisional.
- **No (lA) re-entry was tested in October** (see above). The merge
  says nothing about whether the (lA) re-entry rule helps or hurts
  in a month where mornings actually stop and re-entries fire.
- **October is 18 days, index-driven, and small-N.** Merged 6 trades,
  (lA) 4 trades, Skill 3 trades. One trade (Bank 23 Oct, ₹24,060)
  is larger than half the merged total, and it is the trade the cap
  removed. No frequency, win-rate, or net claim from October alone
  survives as an adoption basis.
- **V4 is not a source here.** Do not quote the merged total as
  "V4 + Skill + (lA)" — it is Skill + (lA) only, and V4 October
  (+₹51,825) is a comparison benchmark, not an input.

## Verdict — NOT adopted, next step stated

**No version is adopted on October alone.** Merged Skill+(lA) October
(6 trades, 66.7% green, +₹46,975) trails the October V4/V5 index
benchmark (+₹51,825), beats Skill alone only by adding the (lA) leg,
and contains zero tested (lA) re-entries. Previous best kept for
index remains V4 index as a separate series, paper only.
A merged Skill+(lA) candidate could only be considered after it is
**frozen as defined here (including the Bank mirror and the rank-1
labelling) and run on unseen months**, and it must then progress on
net + win rate + frequency together — not on October, and not by
re-tuning the ranking, the cap, or the mirror on the validation window.

## Files

- This report: `~/workspace/trading/merged_skill_la_index_october_2026.md`
- Engine: `~/workspace/trading/merged_skill_la_october.py`
- Month JSON: `~/workspace/trading/data/progressive/merged_skill_la_summary_2026-10.json`
  (Skill index candidates, (lA) candidates + diagnostics, capped series,
  merged capped trades, ranked pool)
- Sources: `~/workspace/trading/progressive_capped_v2.py`,
  `~/workspace/trading/nifty_cluster1_extended_window_sweep.md`,
  `~/workspace/trading/extended_window_sweep.py`,
  `~/workspace/trading/combined_confirm_sweep.py`,
  `~/workspace/trading/october_2026_v4_and_skill.md`
