# Index OPTIONS — Progressive Tuning Log

## October Complete — standalone October verdict (2026-10-30, user: "First complete October")

**October-complete verdict, October 2026 only (1–28 Oct, 18 days): NO version passes
all legs on October premiums alone.** Full standalone report (ranked premium table,
completeness verification, families A–D spot context, closest version with exact
failed legs):
[index_options_october_complete.md](sandbox://workspace/trading/index_options_october_complete.md)
Headline: every October taken trade is premium-scored (31 v2 taken trades +
84 NS legs, 0 NOT_COMPUTED in either premium file); frequency fails on EVERY
premium track (best: NS1 Bank 3.89/week, NS1 Nifty 3.61/week — neither reaches
5/week); closest family overall is NS1, failing full-target (Nifty 23.1%,
Bank 42.9%) and frequency on both indices; closest tracks by legs passed are
V5-v2 Bank and NS4 Bank (net + full-target pass, frequency fail only). Nothing
adopted on October alone. Jan–Oct expansion work is NOT in that verdict and
comes only after it, per the user's instruction.

**Correction, user 2026-10-30 08:06 IST:** 09:00 IST is NOT a deadline or stop point. This is continuous progressive tuning with an hourly report of what was found, until the user says satisfied. Tuning does not close at 09:00. November paper (from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November) remains validation, but does NOT stop October tuning now.

**Scope:** Index OPTIONS only — V4 / Skill v2 / (lA) v2 / V5 / Volrix v2, Nifty and Bank separately, never pooled, paper only, no orders, no futures, spot trigger only.
**Scoring window:** Full October 2026 first (1–28 Oct, 18 days), then Jan–Oct for any family that passes October, per version per index separately.
**Target:** 5 trades/week = 1/day, decent return, decent hits (full targets). No forced trades, no room below 1.5×, no direct reclaim CE re-introduced to rescue frequency, no spot-points-to-premium conversion.
**Units:** Spot provisional = points × 100 shares − ₹40/trade. This is NOT an options-lot profit and NOT a futures profit. Premium net per 1 lot = (exit − entry premium) × lot − ₹220 assumed cost (labelled), lot Nifty 65 / Bank 30, stop −50 / target +90 option points, square-off 15:10. Premiums only via browser-fetch script-token route where candles exist; otherwise spot provisional with the gap stated.

## Ranked highest-tuned table (current)

| Rank | Version / index | Trades | Full-targets | Spot prov. net | /week | Premium-known subset |
|---|---|---|---|---|---|---|
| 1 (Bank) | V5-v2 Bank | 4 | 3 (75%) | +₹43,630 | 1.11 | 2 trades: +₹4,960; 2 NOT_COMPUTED |
| 1 (Nifty) | (lA) v2 Nifty | 3 | 3 targets | +₹28,020 | 0.83 | 1 trade: −₹1,334.75; 2 NOT_COMPUTED |
| 2 (Bank) | (lA) v2 Bank | 4 | 2 targets | +₹28,275 | 1.11 | 2 trades: +₹4,960; 2 NOT_COMPUTED |
| 2 (Nifty) | V5-v2 Nifty | 3 | 2 (67%) | +₹8,195 | 0.83 | 2 trades: −₹4,804.75; 1 NOT_COMPUTED |
| 3 (Bank) | Skill v2 Bank | 9 taken (7 blocked) | 3 (33%) | +₹8,675 | 2.50 | 0 computed |
| 3 (Nifty) | Skill v2 Nifty | 8 taken (8 blocked) | 2 (25%) | +₹8,420 | 2.22 | 1 trade: −₹3,470 premium vs −₹5,470 cash |
| — | Volrix v2 Nifty / Bank | 0 / 0 | — | ₹0 | 0 | 0 triggers |

**Verdict on the baseline:** NO version meets all legs (≥5/week + net > 0 + full-target ≥ 50%). Highest tuned overall: (lA) v2 (7 trades, 5 green, +₹56,295 spot provisional combined across separate tracks — version total, not a portfolio P&L). Nothing adopted on October alone.

## Progress section — 2026-10-30, Family B: Indicators

**Source:** child report, October 2026 (1–28 Oct, 18 days). Detail: [index_options_familyB_indicators_detail.csv](sandbox://workspace/trading/index_options_familyB_indicators_detail.csv), script: [familyB_indicators.py](sandbox://workspace/trading/familyB_indicators.py). Base = (lA) v2 and Skill v2 (S1) from the 09:00 v2 report. Skill base recomputed from cache, not copied — all 17 S1-taken nets match the v2 CSV to the rupee. (lA) day trades/signal times taken verbatim from the v2 CSV; reconstructed morning legs equal day nets on all 7 (lA) days (no re-entry contribution in base October).

**Frozen definitions (one family each, never blended):** Indicators on the continuous 5-min close series per symbol (not reset daily): EMA9/EMA21 (SMA-seeded), RSI14 Wilder, ATR14 Wilder, read at the signal bar inclusive.
- B1 VWAP: PE only if signal close < session VWAP; CE only if close > VWAP.
- B2 EMA trend: PE kept only if close < EMA9 < EMA21; CE kept only if close > EMA9 > EMA21.
- B3 RSI extremes: PE blocked if RSI14 ≤ 30; CE blocked if RSI14 ≥ 70; otherwise kept.
- B4 ATR stops (exit replacement, not a filter): stop = entry ∓ 1.5×ATR14 at signal bar; target unchanged; stop priority; square-off 15:10. Scored fully on Skill; on (lA) scored on the morning leg only (day-net B4 not claimed).
- B5 Volume confirmation: signal-bar volume > 1.5× mean of prior 20 bars.
- B6 OR extension (Skill, full re-score): OR = bars < 10:00 (09:15–09:55); signal = first close outside extended OR, 10:00–11:30; CE blocked if bearish bias; PE blocked if close ≥ PDL; room_ratio ≥ 1.5; base Skill exit; one trade/day max. B6-(lA) is a partial signal-bar re-test only.

**Before / after per track (frequency = trades ÷ 18 × 5; Green = net > 0):**

| Family / track | Trades (before → after) | Full-targets | Green | Net ₹ provisional (before → after) | /week (before → after) |
|---|---|---|---|---|---|
| B2 EMA — Skill Nifty | 8 → 7 | 2 → 2 | 3 → 2 | +8,420 → −8,130 | 2.22 → 1.94 |
| B2 EMA — Skill Bank | 9 → 9 | 3 → 3 | 3 → 3 | +8,675 → +8,675 (no change) | 2.50 → 2.50 |
| B2 EMA — (lA) Nifty | 3 → 3 | 3 → 3 | 3 → 3 | +28,020 → +28,020 (no change) | 0.83 → 0.83 |
| B2 EMA — (lA) Bank | 4 → 4 | 2 → 2 | 2 → 2 | +28,275 → +28,275 (no change) | 1.11 → 1.11 |
| B3 RSI extremes — Skill Nifty | 8 → 4 | 2 → 0 | 3 → 1 | +8,420 → +3,685 | 2.22 → 1.11 |
| B3 RSI extremes — Skill Bank | 9 → 8 | 3 → 3 | 3 → 3 | +8,675 → +16,150 | 2.50 → 2.22 |
| B3 RSI extremes — (lA) Nifty | 3 → 1 | 3 → 1 | 3 → 1 | +28,020 → +4,940 | 0.83 → 0.28 |
| B3 RSI extremes — (lA) Bank | 4 → 2 | 2 → 1 | 2 → 1 | +28,275 → +11,690 | 1.11 → 0.56 |
| B4 ATR stops — Skill Nifty | 8 → 8 | 2 → 2 | 3 → 3 | +8,420 → +457 | 2.22 → 2.22 |
| B4 ATR stops — Skill Bank | 9 → 9 | 3 → 4 | 3 → 4 | +8,675 → +206 | 2.50 → 2.50 |
| B4 ATR stops — (lA) Nifty, morning leg | 3 → 3 | 3 → 3 | 3 → 3 | +28,020 → +28,020 (identical) | 0.83 → 0.83 |
| B4 ATR stops — (lA) Bank, morning leg | 4 → 4 | 2 → 3 | 2 → 3 | +28,275 → +49,965 | 1.11 → 1.11 |
| B6 ext. OR — Skill Nifty | 8 → 5 (new signal set) | 2 → 0 | 3 → 1 | +8,420 → −11,865 | 2.22 → 1.39 |
| B6 ext. OR — Skill Bank | 9 → 1 (new signal set) | 3 → 1 | 3 → 1 | +8,675 → +24,990 | 2.50 → 0.28 |
| B1 VWAP — all tracks | NOT TESTED | — | — | — | — |
| B5 Volume — all tracks | NOT TESTED | — | — | — | — |

**Verdicts:**
- **B2 EMA — DISCARD.** Inert on 3 of 4 tracks. On Skill Nifty its only removal was the biggest winner: 26 Oct CE square-off +₹16,550 (EMA9 < EMA21, so CE blocked) — net flips to −₹8,130. Pure frequency-killer, adds nothing.
- **B3 RSI extremes — DISCARD as a blanket rule.** Inconsistent across tracks. Helps exactly one track: Skill Bank removes only the 7 Oct PE stop −₹7,475 (RSI 23.24), keeping all 3 targets → +₹16,150. Everywhere else it removes winners: Skill Nifty loses both targets (6 Oct CE RSI 71.59; 8 Oct PE RSI 25.39) → 0 targets; (lA) Nifty keeps only 21 Oct (+₹4,940) and loses 8 Oct (+₹11,690) and 23 Oct (+₹11,390) targets; (lA) Bank loses the 23 Oct target (+₹24,060). The PE-at-RSI≤30 block fights this system's own breakdown-continuation edge. The single Bank-Skill improvement is one trade — watch item, not a keep.
- **B4 ATR stops — DISCARD as a general rule.** Skill collapses on both tracks despite Bank targets rising 3→4: Nifty +₹8,420 → +₹457, Bank +₹8,675 → +₹206. Wider 1.5×ATR stops bleed every loser (e.g. Bank 7 Oct −₹7,475 → −₹11,195; 12 Oct −₹4,640 → −₹10,652). (lA) Bank morning leg +₹28,275 → +₹49,965 is one single-trade flip: 8 Oct L1 stop −₹8,510 → target +₹16,900, because the wider ATR stop survives the wick. Single-case observation for the failing-cases log, not a rule change. Caveat: 7 Oct Bank still stops under B4, so a re-entry could theoretically fire after the B4 stop; the B4 Bank day-net is therefore unknown by that one leg, and +₹49,965 is a morning-leg figure.
- **B6 extended OR — DISCARD as a replacement.** Skill Nifty: 5 trades, 0 targets, 1 green, −₹11,865. Skill Bank: 1 trade, the 23 Oct PE target at +₹24,990 — one trade, not a system, at 0.28/week. No-signal days under extended OR: 3 Nifty, 7 Bank; room ≥ 1.5 additionally rejected 2 Nifty and 2 Bank signals. B6-(lA) partial: all 3 Nifty signal bars still close below the extended OR low; Bank 2 of 4 survive (7 Oct fails; 23 Oct fails on the boundary, close exactly equal to ext. OR low, not below). A full (lA) rescan re-run was NOT scored — the confirmer-break window shifts with the OR window too, so new later rescans under extended OR are unknown, not zero.
- **B1 VWAP and B5 Volume — NOT TESTED, not failed.** `spot_5m.csv` has columns timestamp, open, high, low, close only — no volume column in either symbol's cache. VWAP and any volume ratio cannot be computed from this cache, and were not proxied with equal-weighted averages. They need an Upstox intraday fetch with volume before they can be scored.
- **Net verdict, Family B:** No indicator family is kept as best. Filters (B2, B3) cannot add days — they only remove — and in October they mostly removed winners. B4 flipped 2 trades but destroyed Skill net on both tracks. B6 is the only family that can add days, and it added exactly one new green day: Nifty 16 Oct CE square-off +₹2,355 — while losing net on both tracks and collapsing frequency. Nothing here meets net + win + frequency together, and nothing is adopted on October alone.

**Open items from Family B:**
1. B1/B5 need volume data (Upstox intraday with volume) — currently unscored, not discarded on merit.
2. B6-(lA) full rescan re-run (extended OR + shifted confirmer window) is unscored; the partial signal-bar test above is not a trade count.
3. V5-v2 and Volrix v2 were out of scope for Family B (bases were (lA) v2 and Skill v2 only) and were not re-scored under any indicator.

## Progress section — 2026-10-30, Family C: Approaches + Entry Times

**Source:** child report, October 2026 (1–28 Oct, 18 days), paper only, no orders. Frozen definitions before scoring: [index_options_familyC_frozen_oct30.md](sandbox://workspace/trading/index_options_familyC_frozen_oct30.md); full report: [index_options_familyC_oct30.md](sandbox://workspace/trading/index_options_familyC_oct30.md). All rupees are spot provisional = points × 100 shares − ₹40/leg. NOT an options-lot profit, NOT a futures profit. Premiums NOT_COMPUTED for Family C (cache is spot 5-min + daily only; no browser fetch was run in this subagent run). Room never loosened below 1.5×. Direct reclaim CE not re-introduced. Full-target = target exit AND day net > 0 (a re-entry leg hitting its own target while the day still nets negative does not count).

**Base reconciliation (recomputed from cache — one correction to the v2 picture):** V4 uncapped is NOT the same as V5-v2 in October. V5-v2 = V4 minus the 1/week cap-outs (Nifty 28 Oct, Bank 23 Oct).

| Track | Trades | Net prov. | Win | Full-target | /wk |
|---|---|---|---|---|---|
| V4 Nifty | 4 | +₹2,725 | 2/4 (50%) | 2 (50%) | 1.11 |
| V4 Bank | 5 | +₹67,690 | 4/5 (80%) | 4 (80%) | 1.39 |
| Skill v2 Nifty | 8 | +₹8,420 | 3/8 (37.5%) | 2 (25%) | 2.22 |
| Skill v2 Bank | 9 | +₹8,675 | 3/9 (33.3%) | 3 (33.3%) | 2.50 |
| (lA) v2 Nifty | 3 | +₹28,020 | 3/3 (100%) | 3 (100%) | 0.83 |
| (lA) v2 Bank | 4 | +₹28,275 | 2/4 (50%) | 2 (50%) | 1.11 |
| V5-v2 Nifty | 3 | +₹8,195 | 2/3 (66.7%) | 2 (66.7%) | 0.83 |
| V5-v2 Bank | 4 | +₹43,630 | 3/4 (75%) | 3 (75%) | 1.11 |
| Volrix v2 Nifty / Bank | 0 | ₹0 | — | — | 0 |

Skill v2 and (lA) v2 bases reproduce the v2 report exactly; V5-v2 totals also match (+₹51,825). Volrix: 0 triggers either index, so 0 trades in every family below, by design.

**C1 — O1 cross-confirmation persistence (PE only; confirmer below its OR low on BOTH signal and entry bars; CE kept):**

| Track | Base → O1 trades | Base net → O1 net | Win | Full-target | Filtered out | Verdict |
|---|---|---|---|---|---|---|
| V4 Nifty | 4 → 2 | +₹2,725 → +₹2,755 | 50% → 50% | 50% → 50% | 1 loss (−₹5,470, 28 Oct) / 1 win (+₹5,440, 8 Oct) | Discard — neutral (+₹30), kills a winner for a loser |
| V4 Bank | 5 → 3 | +₹67,690 → +₹60,900 | 80% → 100% | 80% → 100% | 1 loss (−₹3,730, 13 Oct) / 1 win (+₹10,520, 26 Oct) | Discard — net falls ₹6,790; win rate up only by deletion |
| Skill v2 Nifty | 8 → 4 | +₹8,420 → +₹15,780 | 37.5% → 50% | 25% → 25% | 3 losses / 1 win (+₹5,440, 8 Oct PE) | Discard — FT flat, kills the only PE winner; leaves a CE-only track |
| Skill v2 Bank | 9 → 7 | +₹8,675 → +₹20,790 | 33.3% → 42.9% | 33.3% → 42.9% | 2 losses (−₹7,475, 7 Oct; −₹4,640, 12 Oct) / 0 winners | Keep as candidate (Oct only) — cleanest O1 track; still 1.94/wk |
| (lA) v2 Nifty | 3 → 2 | +₹28,020 → +₹16,330 | 100% → 100% | 100% → 100% | 0 losses / 1 win (+₹11,690, 8 Oct) | Discard — filters a winner, no loser; fails O1's own leg |
| (lA) v2 Bank | 4 → 3 | +₹28,275 → +₹35,750 | 50% → 66.7% | 50% → 66.7% | 1 loss (−₹7,475, 7 Oct F1) / 0 winners; 8 Oct L1 loser (−₹8,510) kept | Keep as candidate (Oct only) — filters F1 but NOT the 8 Oct L1 loser; 0.83/wk |
| V5-v2 Nifty | 3 → 2 | +₹8,195 → +₹2,755 | 66.7% → 50% | 66.7% → 50% | 0 losses / 1 win (+₹5,440, 8 Oct) | Discard — kills a winner only |
| V5-v2 Bank | 4 → 2 | +₹43,630 → +₹36,840 | 75% → 100% | 75% → 100% | 1 loss (−₹3,730) / 1 win (+₹10,520, 26 Oct) | Discard — net falls ₹6,790 |

**C2 — Re-entry variants (after a morning STOP only; day net = morning + re-entry):**

| Track | R1 (trades, net, win, FT) + fired legs | R2 (trades, net, win, FT) | Verdict |
|---|---|---|---|
| V4 Nifty | 4, +₹5,795, 50%, 50% — 1 fired: 26 Oct CE −₹8,635 + ₹3,070 = −₹5,565 (day still red) | 4, +₹800, 50%, 50% | Discard both — R1 net-only gain, no new green day; R2 worse |
| V4 Bank | 5, +₹67,690, 80%, 80% (unchanged) — 0 fired | unchanged | Discard — no effect |
| Skill v2 Nifty | 8, +₹16,000, 62.5%, 50% — 2 fired, both rescued: 5 Oct −₹2,220→+₹270; 12 Oct −₹4,605→+₹485 | 8, +₹7,485, 37.5%, 25% | R1 keep as best for this track (Oct only); R2 discard |
| Skill v2 Bank | 9, +₹31,320, 55.6%, 55.6% — 3 fired: 6 Oct worsened −₹1,435→−₹4,480; 8 Oct rescued −₹11,070→+₹1,600; 12 Oct rescued −₹4,640→+₹8,380 | 9, −₹7,675, 33.3%, 33.3% | R1 keep as best for this track (Oct only); R2 discard — R2 turns the track negative |
| (lA) v2 Nifty | 3, +₹28,020, 100%, 100% (unchanged) — 0 fired (no stop days) | unchanged | Discard — no effect |
| (lA) v2 Bank | 4, +₹40,160, 75%, 50% — 1 fired: 8 Oct −₹8,510 + ₹11,885 = +₹3,375 via square-off, not a target | 4, +₹36,435, 50%, 50% (day −₹350) | R1 keep as weak candidate (win+net up, FT flat; rescue is square-off green); R2 discard |
| V5-v2 Nifty | 3, +₹11,265, 66.7%, 66.7% — same 26 Oct leg, day still red | 3, +₹6,270, 66.7%, 66.7% | Discard both |
| V5-v2 Bank | 4, +₹43,630, 75%, 75% (unchanged) — 0 fired | unchanged | Discard — no effect |

**C3 — Pullback entries (dip to OR level + close back; no pullback = no trade):**

| Track | Trades | Net prov. | Win | Full-target | /wk | No-pullback days | Verdict |
|---|---|---|---|---|---|---|---|
| V4 Nifty | 3 | +₹1,770 | 2/3 (66.7%) | 2 (66.7%) | 0.83 | 23 Oct (base winner +₹11,390 lost) | Discard — win/FT up, net down |
| V4 Bank | 1 | +₹7,420 | 1/1 (100%) | 1 (100%) | 0.28 | 13, 21, 23, 26 Oct | Discard — frequency destroyed, net collapses |
| Skill v2 Nifty | 5 | +₹4,915 | 3/5 (60%) | 3 (60%) | 1.39 | 5, 7, 27 Oct | Discard — win/FT up, net down (26 Oct square-off +₹16,550 becomes +₹2,730) |
| Skill v2 Bank | 7 | +₹21,460 | 4/7 (57.1%) | 4 (57.1%) | 1.94 | 7, 23 Oct | Keep as best for this track (Oct only) — net, win and FT all up |
| (lA) v2 Nifty | 0 | ₹0 | — | — | 0 | all 3 days | Discard — zero trades; (lA) breakdowns never rally back to OR low and close below it again |
| (lA) v2 Bank | 0 | ₹0 | — | — | 0 | all 4 days | Discard — zero trades, same reason |
| V5-v2 Nifty | 2 | +₹950 | 1/2 (50%) | 1 (50%) | 0.56 | 23 Oct | Discard — net down |
| V5-v2 Bank | 1 | +₹7,420 | 1/1 (100%) | 1 (100%) | 0.28 | 13, 21, 26 Oct | Discard — frequency destroyed |

**C4 — Second-close variants (C4a: stop from second bar; C4b: stop from original signal bar):**

| Track | C4a (trades, net, win, FT) | C4b (trades, net, win, FT) | Verdict |
|---|---|---|---|
| V4 Nifty | 4, +₹7,170, 50%, 50% | 4, −₹16,090, 25%, 25% | Discard both — C4a net-only gain by shrinking winners (8 Oct +₹5,440→−₹375 stop; 23 Oct +₹11,390→+₹4,650); C4b deeply negative |
| V4 Bank | 3, +₹30,665, 66.7%, 66.7% | 2, +₹52,775, 100%, 50% | Discard both — C4a net down ₹37k; C4b net and FT down |
| Skill v2 Nifty | 4, −₹11,570, 0%, 0% | 4, +₹9,535, 75%, 75% | C4a discard (destroys the track); C4b keep as candidate (Oct only) — all metrics up, but net gain only +₹1,115 and frequency halved |
| Skill v2 Bank | 4, −₹9,420, 25%, 25% | 3, +₹1,265, 33.3%, 33.3% | Discard both — both below base on net |
| (lA) v2 Nifty | 3, +₹2,085, 33.3%, 33.3% | 3, +₹7,515, 66.7%, 66.7% | Discard both — C4a destroys 3/3 targets; C4b net down ₹20,505 |
| (lA) v2 Bank | 2, +₹36,290, 100%, 100% | 2, +₹52,775, 100%, 50% | C4a keep as candidate (Oct only, deletion warning: both losers fail second close; 21 Oct winner shrinks +₹20,200→+₹11,300); C4b discard (FT flat at 50%, 23 Oct win is square-off not target) |
| V5-v2 Nifty | 3, +₹7,785, 66.7%, 66.7% | 3, −₹10,075, 33.3%, 33.3% | Discard both |
| V5-v2 Bank | 2, +₹5,675, 50%, 50% | 1, +₹31,540, 100%, 100% | Discard both — C4a net collapses; C4b is a single trade, not a system |

**C5 — Time-gated entries (net, trades; cumulative gates; PM windows standalone):**

| Gate | V4 Nifty | V4 Bank | Skill Nifty | Skill Bank | (lA) Nifty | (lA) Bank | V5 Nifty | V5 Bank |
|---|---|---|---|---|---|---|---|---|
| ≤09:30 | ₹0 (0) | ₹0 (0) | −₹2,220 (1) | −₹16,660 (1) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) |
| ≤09:35 | ₹0 (0) | ₹0 (0) | −₹4,945 (2) | −₹31,370 (3) | ₹0 (0) | −₹7,475 (1) | ₹0 (0) | ₹0 (0) |
| ≤09:40 | +₹5,440 (1) | ₹0 (0) | −₹2,295 (4) | −₹32,805 (4) | ₹0 (0) | −₹7,475 (1) | +₹5,440 (1) | ₹0 (0) |
| ≤09:45 | +₹5,440 (1) | ₹0 (0) | +₹1,945 (5) | −₹17,945 (5) | ₹0 (0) | −₹7,475 (1) | +₹5,440 (1) | ₹0 (0) |
| ≤10:00 | −₹3,195 (2) | +₹40,700 (2) | +₹13,890 (7) | −₹5,945 (7) | ₹0 (0) | +₹16,585 (2) | −₹3,195 (2) | +₹16,640 (1) |
| ≤10:30 | +₹2,725 (4) = base | +₹51,220 (3) | +₹8,420 (8) = base | −₹5,945 (7) | +₹11,390 (1) | +₹16,585 (2) | +₹8,195 (3) = base | +₹27,160 (2) |
| PM1 12:00–13:30 | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | −₹8,510 (1) | ₹0 (0) | ₹0 (0) |
| PM2 13:30–15:00 | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) | ₹0 (0) |

**C5 verdict: discard every gate as a standalone system.** Early gates (≤09:30–09:45) are negative or single-trade for Skill and empty for V4/(lA) — morning-only trading fails in October. ≤10:30 equals base for V4 Nifty, Skill Nifty and V5 Nifty (all their signals are already ≤10:30), so it is not a gain. ≤10:30 on Skill Bank turns the track negative by deleting its biggest winner (5 Oct +₹25,690, signal 10:50) while keeping the losers — Skill Bank winners are late, not early. PM windows contain exactly one base trade in all of October ((lA) Bank 13:15 L1 loser −₹8,510); PM2 is empty everywhere. (lA) is inherently a late-signal system (signals 09:35–13:15, mostly after 10:00), so early gates delete it by construction.

**Overall verdict, Family C — nothing adopted. No variant reaches 5/week on any track** (best: Skill v2 base/R1 Bank at 2.50/week). Keeps, October only, each still needing November 2026 paper with its definition frozen before any adoption claim, and nothing combined yet (keeps are per-track and must survive November alone first, to avoid stacking October-fitted filters):
- C1-O1: Skill Bank, (lA) Bank.
- C2-R1: Skill Nifty, Skill Bank, (lA) Bank (weak — FT flat, rescue is square-off).
- C3-pullback: Skill Bank only.
- C4a: (lA) Bank only (deletion warning). C4b: Skill Nifty only.
- C5: none.
Discards of note: O1 on (lA) Nifty (kills its 8 Oct winner, filters no loser); R2 everywhere (Skill Bank goes negative); pullback on (lA) both (0 trades); C4a on Skill both and (lA) Nifty (destroys targets); every early time gate; PM windows (one loser total).
Caveats: (1) All scoring is spot provisional, not options-lot P&L — premium completion (browser-fetch route) is still outstanding and could reverse spot rankings, as it did for overlapping days in v2. (2) October is 18 days with 1–9 base trades per track; every "keep" above is a small-sample October candidate, not a proven edge. (3) The V4-vs-V5 distinction (uncapped 9 vs capped 7 trades) should be carried into the merge — quoting V5 numbers as V4 numbers, or vice versa, would misstate both tracks.

## Progress section — 2026-10-30, Family D: Different Candles

**Source:** child report, October 2026 (1–28 Oct, 18 days), paper only, no orders. Script (frozen definition + all engines): [family_d_candles.py](sandbox://workspace/trading/family_d_candles.py); full 15-min results JSON: [family_d_candles_results.json](sandbox://workspace/trading/family_d_candles_results.json). All D rupee figures are spot provisional (points × 100 shares − ₹40/leg), NOT options-lot and NOT futures profits; premium P&L for D tracks is entirely NOT_COMPUTED. Room floor (D-primary): no trade with room ratio < 1.5 (room ≥ 300×scale) — a tightening vs base floors (base (lA)/V4/Skill-filtered = 1.0; base S1 had no room filter). A sensitivity row with base room rules is shown alongside, so the pure candle effect is visible separately. Room was never loosened. Replay (all grids): entry = next bar open; stop checked before target on every bar including the entry bar; square-off at the grid bar containing 15:10. Skill S1, (lA) L1, V4, V5-pool and Volrix rules are the base v2 rules re-applied on each grid. Coarsening flagged: a 15-min bucket labelled HH:MM covers HH:MM–HH:MM+15, so 15-min window edges run up to 15 min past the 5-min edge.

**Verdict up front: DISCARD all three candle changes as replacements. Keep 5-min as the best grid. No D track meets the ≥5/week leg, and the 15-min nets that look bigger are mostly bigger risk, not a better signal. Nothing here is adopted.**

**Data availability — stated plainly, no bars invented:**
- 1-min: NOT available October-wide. True 1-min spot exists only for 2026-10-08 and 2026-10-23 per index (`~/workspace/trading/data/1min/`). The 1-min replay below covers those 2 days only — no weekly rate is claimed from it.
- 3-min: CANNOT be built from 5-min bars (a 5-min bar cannot be split into 3-min bars without inventing intra-bar data). October-wide 3-min is therefore not scored. Genuine 3-min bars were built by aggregating the true 1-min files for 8 & 23 Oct only (subset).
- 15-min: clean aggregation (3×5-min bars anchored 09:15; the 09:15 bucket is exactly the 5-min OR). Full-October 15-min scoring is genuine.

**Verification: 5-min reproduction matches base exactly.** The generic engine on the 5-min grid reproduces every base October trade net exactly (Skill S1 taken: 8 Nifty + 9 Bank; (lA) L1 day nets: 3 Nifty + 4 Bank; V4 candidates). Two V4 candidates absent from the V5-v2 CSV are explained by the V5 weekly cap, not by error: V4 Nifty 28 Oct (−₹5,470) loses W44 to V4 26 Oct (setup4 rank 3), and V4 Bank 23 Oct (+₹24,060) loses W43 to V4 21 Oct (bias-strong). Correct V4-uncapped bases are therefore: Nifty 4 trades / +₹2,725; Bank 5 trades / +₹67,690 (not the V5-capped figures).

**(1) 1-min replay + 5-min aggregation audit — are 5-min entry-bar stops real?**
Audit of all 33 base 5-min legs (Skill S1 + V4 + (lA) mornings; no (lA) October day had a re-entry on 5-min): 16 stops, of which 9 fell on the entry bar and only 1 touched both stop and target in its exit bar — Bank Skill 6 Oct (−₹1,435, entry bar, both levels touched). The other 15 stops touched only the stop level in their exit bar, so they are definitively real at any finer grid; no target exit is threatened by ordering. The single both-levels case (Bank 6 Oct) is ordering-ambiguous under 5-min bars and is not in the 1-min subset, so it stays ambiguous — the 5-min stop-first convention may have cost a target there, but it is one small trade, not a systematic artefact.

Genuine 1-min replay (8 & 23 Oct only), vs 5-min same days:

| Track / index | 5-min same 2 days | 1-min (genuine) | What changed |
|---|---|---|---|
| Skill S1 Nifty | 1 trade: 8 Oct target +₹5,440; 23 Oct BLOCKED (S1 09:30-PE) | 2 trades: 8 Oct target +₹5,460; 23 Oct stop −₹1,540 → net +₹3,920 | 23 Oct trade appears only because on 1-min the first breakdown close is 09:33, not the 09:30 bar — the S1 09:30-PE rule nearly vanishes on a finer grid. 8 Oct is essentially identical (+₹5,460 vs +₹5,440): robust. |
| Skill S1 Bank | 2 trades: 8 Oct stop −₹11,070; 23 Oct target +₹14,860 → +₹3,790 | 2 trades: 8 Oct stop −₹5,645; 23 Oct target +₹10,480 → +₹4,835 | Same directions, smaller sizes (tighter 1-min stops → smaller 2× targets). |
| (lA) L1 Nifty | 2 trades: 8 Oct target +₹11,690; 23 Oct target +₹11,390 → +₹23,080 | 2 trades: 8 Oct stop −₹1,595 (signal 11:26, stopped 11:32, no re-entry); 23 Oct target +₹3,180 → +₹1,585 | The 5-min (lA) Nifty result collapses on 1-min. The 8 Oct target depends on the 5-min bar's wider stop; the 1-min signal (11:26 vs 11:25 bucket) stops out immediately. 23 Oct keeps direction but at ~1/4 the size. |
| (lA) L1 Bank | 2 trades: 8 Oct stop −₹8,510; 23 Oct target +₹24,060 → +₹15,550 | 2 trades: 8 Oct stop −₹2,050; 23 Oct target +₹9,280 → +₹7,230 | Same directions, much smaller (tighter stops). |
| V4 Nifty | 2 trades: +₹5,440 + ₹11,390 → +₹16,830 | 2 trades: +₹5,460 + ₹3,180 → +₹8,640 | Same pattern as (lA) Nifty (shared setup2 signals). |
| V4 Bank | 1 trade: 23 Oct +₹24,060 (8 Oct: no V4 trade) | 1 trade: 23 Oct +₹9,280 (8 Oct: no trade) | Same. |

1-min verdict: DISCARD as a replacement grid; KEEP as an audit. The audit proves 5-min stops are mostly not ordering artefacts, but the replay proves 1-min is not a free improvement: it shrinks every (lA)/V4 target via tighter stops and flips the Nifty 8 Oct (lA) target to a stop. Two days cannot generalise to October — this is a fragility warning for (lA) Nifty, not a new adopted grid.

**(2) 3-min signals — subset only (genuine 3-min from 1-min, 8 & 23 Oct):**

| Track / index | 3-min (2 days) | vs 5-min same 2 days |
|---|---|---|
| Skill S1 Nifty | 8 Oct target +₹5,020; 23 Oct stop −₹3,115 → +₹1,905 | Same directions as 1-min; smaller than 5-min (+₹5,440, 23 Oct blocked). |
| Skill S1 Bank | 8 Oct stop −₹11,295; 23 Oct target +₹8,110 → −₹3,185 | Worse than both 5-min (+₹3,790) and 1-min (+₹4,835). |
| (lA) L1 Nifty | 8 Oct target +₹8,920; 23 Oct target +₹6,780 → +₹15,700 | Holds direction (unlike 1-min 8 Oct) but still well below 5-min +₹23,080. |
| (lA) L1 Bank | 8 Oct stop −₹5,100; 23 Oct target +₹21,650 → +₹16,550 | Roughly holds 5-min +₹15,550 — the one 3-min result that does not shrink. |
| V4 Nifty | +₹5,020 + ₹6,780 → +₹11,800 (vs 5-min +₹16,830) | Shrinks. |
| V4 Bank | 23 Oct +₹21,650; 8 Oct no trade (vs 5-min +₹24,060) | Roughly holds. |

3-min verdict: DISCARD as an October-wide claim (impossible from the cache) and not adopted on a 2-day subset. The subset repeats the 1-min lesson: finer grids tighten stops and shrink 2× targets; they do not create frequency (still ≤1 trade/day/index on these days).

**(3) 15-min signals — full October (primary room ≥ 1.5; sensitivity = base room).** "Full-target" = target exit (for (lA), morning target exit, as in the base report); square-offs are green separately, never counted as full targets. Frequency = trades ÷ 18 days × 5.

| Track / index | Base 5-min (trades / targets / green / net / wk) | 15-min PRIMARY (trades / targets / green / net / wk) | 15-min SENSITIVITY (base room) |
|---|---|---|---|
| Skill S1 Nifty | 8 / 2 / 3 / +₹8,420 / 2.22 | 7 / 2 / 5 / +₹23,685 / 1.94 | 9 / 2 / 5 / +₹12,530 / 2.50 |
| Skill S1 Bank | 9 / 3 / 3 / +₹8,675 / 2.50 | 6 / 2 / 2 / −₹10,340 / 1.67 | 10 / 3 / 4 / +₹17,370 / 2.78 |
| (lA) L1 Nifty | 3 / 3 / 3 / +₹28,020 / 0.83 | 3 / 1 / 2 / +₹23,515 / 0.83 | same as primary (no trade dropped by the 1.5 floor) |
| (lA) L1 Bank | 4 / 2 / 2 / +₹28,275 / 1.11 | 3 / 2 / 2 / +₹82,935 / 0.83 | same as primary |
| V4 (uncapped) Nifty | 4 / 2 / 2 / +₹2,725 / 1.11 | 5 / 2 / 3 / +₹22,905 / 1.39 | same as primary |
| V4 (uncapped) Bank | 5 / 4 / 4 / +₹67,690 / 1.39 | 2 / 2 / 2 / +₹84,940 / 0.56 | 5 / 3 / 3 / +₹94,915 / 1.39 |
| V5 (capped) Nifty | 3 / 2 / 2 / +₹8,195 / 0.83 | 3 / 2 / 3 / +₹30,355 / 0.83 | — (pool is primary-only) |
| V5 (capped) Bank | 4 / 3 / 3 / +₹43,630 / 1.11 | 1 / 1 / 1 / +₹36,330 / 0.28 | — |
| Volrix Nifty / Bank | 0 / — / — / ₹0 | 0 / — / — / ₹0 (daily trigger, candle-invariant) | — |

Key 15-min trade-level changes (why the nets move — this is mostly risk, not edge):
- 15-min signal bars are ~2× wider, so 2× targets are ~2× larger in points. Examples: Bank 23 Oct risk 243.25 pts on 15-min vs 74.5 (Skill 5-min) / 120.5 ((lA) 5-min) → target net ₹48,610 vs ₹14,860/₹24,060. Nifty (lA) 8 Oct risk 116.2 vs 58.65; 21 Oct 59.7 vs 24.9; Bank (lA) 21 Oct 181.85 vs 101.2. Comparing raw nets across grids without normalising risk overstates 15-min. Per-risk, 15-min is no better: it wins the same days with more risk staked.
- (lA) Nifty loses its 23 Oct target on 15-min: signal 10:00 bucket, risk 101.75, never reaches target, square-off −₹825 (vs 5-min target +₹11,390). 8 Oct becomes a square-off +₹12,440 (vs target +₹11,690) and 21 Oct a target +₹11,900 (vs +₹4,940). Net falls despite bigger targets.
- Skill Bank primary goes negative on 15-min (−₹10,340 vs base +₹8,675): 15-min admits different, much larger-risk CE stops — 7 Oct CE stop −₹28,580 (risk 285.4) and 14 Oct CE stop −₹23,005 (risk 229.65) — while the 1.5 floor removes the 1 Oct, 5 Oct, 6 Oct and 8 Oct trades, which together net +₹27,710 in the sensitivity run. The floor cost Bank Skill 15-min ₹27,710 in-sample; that is reported, not used to loosen the floor on one month.
- (lA) Bank 15-min +₹82,935 is not a new edge: it is the same 2 target days (21 + 23 Oct) with ~2× risk, plus a 15-min-only re-entry on 8 Oct (morning −₹11,695 + re-entry +₹9,690 = day −₹2,005, vs 5-min day −₹8,510 with no re-entry). The 7 Oct (lA) Bank day disappears entirely on 15-min (no confirmer break on the coarser grid).
- V5-15min Bank picking 1 trade is a cap artefact: after the 1.5 filter only 2 dedup days survive (21 + 23 Oct, both in W43), so the 1/week cap keeps only 21 Oct (+₹36,330). V5-15min Nifty picks 3 (8, 21, 26 Oct; 23 and 28 Oct lose their weeks to 21 and 26 Oct respectively) for +₹30,355, including 26 Oct as a square-off +₹8,095 where the 5-min setup4 stopped out (−₹8,635) — again a wider-stop survival, not a new signal.
- 15-min changes signals, not just stops: e.g. Nifty 7 Oct — the 5-min 09:35 PE breakdown vanishes on 15-min (the 09:30 bucket close stays inside the OR) and a later 10:15 CE fires instead (sensitivity: stop −₹8,860). Nifty 12 Oct flips from a 5-min stop (−₹4,605) to a 15-min target (+₹9,110) on a different signal bar. Nifty 16 Oct gains a new CE square-off (+₹2,355).
- Frequency: no 15-min track reaches 5/week (best: Skill sens Bank 2.78, Skill sens Nifty 2.50; primaries ≤ 1.94). 15-min does not solve the frequency problem — (lA)/V4/V5 stay at 0.28–1.39/week.

15-min verdict: DISCARD for every track. No track meets all legs (≥5/week + net > 0 + full-target ≥ 50%): Skill Nifty primary has 5/7 green but only 2/7 full targets (3 square-offs do the work); Skill Bank primary is net-negative; (lA)/V4/V5 fail frequency at any net. Keep 5-min.

**Overall family-D verdict:**

| Grid | Verdict |
|---|---|
| 1-min | Audit kept, grid discarded. 5-min stops are real (15/16 not ordering artefacts; 1 ambiguous small case flagged). 1-min outcomes shrink targets and flip (lA) Nifty 8 Oct to a stop — fragility warning, 2-day subset only. |
| 3-min | Not scored October-wide (impossible without inventing bars). 2-day subset discarded as an adoption basis; same shrink pattern as 1-min. |
| 15-min | Discarded on all tracks. Nets are risk-inflated, frequency still fails, Skill Bank turns negative, (lA) Nifty loses a target. |
| Volrix | Unchanged: 0 triggers on every grid (daily-close trigger). Not counted toward the daily bar, by construction. |

Kept as best: the 5-min versions from the 09:00 report — (lA) v2 for hits (Nifty 3/3, Bank 2/4 targets), V5-v2 Bank for net — still failing frequency only, still not adopted. The next question is not another candle width: it is why (lA) Nifty's 8 Oct target survives only on a wide 5-min stop, and whether that stop size is a real level or a bar-width accident — that needs the 1-min files for more days, not a grid switch.
Caveats for merging: (a) all D rupee figures are spot provisional (×100 shares − ₹40/leg), NOT options-lot and NOT futures profits; premium P&L for D tracks is entirely NOT_COMPUTED; (b) 1-min/3-min figures cover 8 & 23 Oct only and must not be annualised or weekly-rated; (c) 15-min nets embed ~2× the per-trade risk of 5-min and are not risk-comparable; (d) the single both-levels audit case is Bank Skill 6 Oct (−₹1,435), the only 5-min exit whose ordering is ambiguous.

## Progress section — 2026-10-30, Family A: Parameter Sweep

**Source:** child report, full October 2026 (1–28 Oct, 18 days), paper only, no orders. All rupee figures are spot provisional = index points × 100 shares − ₹40/trade. This is NOT an options-lot profit and NOT a futures profit. Premiums were not recomputed for these variants; the base premium-known subset from the 09:00 v2 report is unchanged and is not re-ranked here. Nifty and Bank are always separate tracks, never pooled. Frequency = trades ÷ 18 × 5 (trades/week). "Green" = net > 0 (includes square-off greens for V4/Skill; for (lA), a day counts as full-target only when the morning leg hits target with no re-entry). Nothing here is adopted — October is in-sample for these variants. Scratch scripts/results were in /tmp (famA.py, famA_run.py, famA_results.json) for re-running; this section carries the full table for merging.

**Base reproduction (verified exact before scoring):** The bar-by-bar recompute from the spot 5-min + daily cache reproduces the v2 report exactly on every track, so before/after comparisons are clean:

| Track (base) | Trades | Full-targets | Green | Spot prov. net | /week |
|---|---|---|---|---|---|
| V4 Nifty (uncapped candidates) | 4 | 2 | 2 | +₹2,725 | 1.11 |
| V4 Bank (uncapped candidates) | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Skill v2 (S1) Nifty | 8 | 2 | 3 | +₹8,420 | 2.22 |
| Skill v2 (S1) Bank | 9 | 3 | 3 | +₹8,675 | 2.50 |
| (lA) v2 (L1) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| (lA) v2 (L1) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| V5-v2 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| V5-v2 Bank | 4 | 3 | 3 | +₹43,630 | 1.11 |
| Volrix v2 Nifty / Bank | 0 | — | — | ₹0 | 0 |

V4 as a standalone track is included because the task lists it; in the v2 report it only appeared inside V5. S1 blocked counts also reproduce: 8 Nifty, 7 Bank.

**Frozen definitions (fixed before scoring, one change at a time):**
- Base (all tracks): entry = next 5-min open after signal; stop = signal-candle low (CE) / high (PE); risk = |entry − stop|; target = entry ± 2×risk; stop checked before target per bar; square-off 15:10 close. V4 signal rules, S1 blocks (09:30 PE only if close < PDL; CE blocked on bearish-bias days), (lA) L1 rescan (confirmer break ≤11:30, rescan ≤13:30, PE only, OR width ≤360×scale, room ≥200×scale, lA re-entry band [10, morning risk], afternoon first-fail ends scan), V5 pool = V4 + Skill-filtered candidates, dedup by setup rank then prospective target net then bias-strong then room ratio, cap 3/week pooled + 1/symbol/week, prospective ≥₹500.
- (1a) Target-only: stop mult = 1.0, target mult = 1.5× / 2.5× (base 2×). (1b) Stop-only: target mult = 2×, stop mult = 0.75× / 1.25× applied to base risk — so the target distance also moves (target = 2× the new risk). This is stated, not hidden.
- (2) Room: signal-time room threshold = 1.5× / 2.0× / 2.5× the 200×scale base (never below 1.5×, as instructed). For V4, Skill-filtered and (lA) the signal search re-runs and may find a later signal. For S1, which has no room gate in its frozen definition, the variant is a post-filter on the S1 taken set (room ratio at signal ≥ threshold) — it can only drop trades, never find later ones. That asymmetry is flagged wherever it matters.
- (3) Prospective filter: drop trades whose signal-time prospective target net (target mult × risk × 100 − ₹40; (lA) = morning leg only) is < ₹1,000 / ₹1,500, vs base ₹500 (V5) / no filter (other tracks, so the filter is applied to their base candidate sets).
- (4) Caps: V5 variants — no cap (dedup pool only), pooled 1/week, 2/symbol/week (3/week pooled). Per-track variants (V4, Skill S1, (lA)) — 1/week per track, 2/week per track, ranked signal-time only (setup rank, bias-strong, room ratio, prospective target net, date).
- (5) Bias bands: base bearish <35%, neutral 35–79%, bullish ≥80% (prev-day close position). Widened neutral: <25% / ≥85%. Narrowed neutral: <45% / ≥70%. Affects allowed directions, the S1 CE-bearish block, and bias-strong ranking. (lA) rescan is PE-only with no bias gate, so it is expected to be unchanged — and it is.
- Volrix v2: no parameter in families (1)–(5) touches its trigger (prev-day close ≤ −2%) or its 5-session hold with no stop/target. It stays 0 trades, ₹0, on both indices under every variant below. It is omitted from the tables for that reason and stated here instead of being silently dropped.

**(1) Stop/target multiples — full table:**

| Variant | Track | Trades | FT | Green | Net | /week |
|---|---|---|---|---|---|---|
| Base (2×, 1×) | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Base | V4 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Base | Skill Nifty | 8 | 2 | 3 | +₹8,420 | 2.22 |
| Base | Skill Bank | 9 | 3 | 3 | +₹8,675 | 2.50 |
| Base | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Base | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Base | V5 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Base | V5 Bank | 4 | 3 | 3 | +₹43,630 | 1.11 |
| 1a target 1.5× | V4 Nifty | 4 | 2 | 2 | −₹1,502 | 1.11 |
| 1a target 1.5× | V4 Bank | 5 | 4 | 4 | +₹49,795 | 1.39 |
| 1a target 1.5× | Skill Nifty | 8 | 3 | 3 | +₹3,468 | 2.22 |
| 1a target 1.5× | Skill Bank | 9 | 4 | 4 | +₹12,335 | 2.50 |
| 1a target 1.5× | (lA) Nifty | 3 | 3 | 3 | +₹20,985 | 0.83 |
| 1a target 1.5× | (lA) Bank | 4 | 2 | 2 | +₹17,190 | 1.11 |
| 1a target 1.5× | V5 Nifty | 3 | 2 | 2 | +₹3,968 | 0.83 |
| 1a target 1.5× | V5 Bank | 4 | 3 | 3 | +₹31,760 | 1.11 |
| 1a target 2.5× | V4 Nifty | 4 | 2 | 2 | +₹6,952 | 1.11 |
| 1a target 2.5× | V4 Bank | 5 | 3 | 3 | +₹56,395 | 1.39 |
| 1a target 2.5× | Skill Nifty | 8 | 2 | 3 | +₹10,860 | 2.22 |
| 1a target 2.5× | Skill Bank | 9 | 1 | 1 | −₹51,215 | 2.50 |
| 1a target 2.5× | (lA) Nifty | 3 | 3 | 3 | +₹35,055 | 0.83 |
| 1a target 2.5× | (lA) Bank | 4 | 2 | 2 | +₹39,360 | 1.11 |
| 1a target 2.5× | V5 Nifty | 3 | 2 | 2 | +₹12,422 | 0.83 |
| 1a target 2.5× | V5 Bank | 4 | 2 | 2 | +₹26,310 | 1.11 |
| 1b stop 0.75× | V4 Nifty | 4 | 1 | 1 | −₹4,161 | 1.11 |
| 1b stop 0.75× | V4 Bank | 5 | 3 | 3 | +₹31,952 | 1.39 |
| 1b stop 0.75× | Skill Nifty | 8 | 2 | 2 | +₹1,705 | 2.22 |
| 1b stop 0.75× | Skill Bank | 9 | 3 | 3 | +₹3,840 | 2.50 |
| 1b stop 0.75× | (lA) Nifty | 3 | 3 | 3 | +₹20,985 | 0.83 |
| 1b stop 0.75× | (lA) Bank | 4 | 2 | 2 | +₹21,166 | 1.11 |
| 1b stop 0.75× | V5 Nifty | 3 | 1 | 1 | −₹49 | 0.83 |
| 1b stop 0.75× | V5 Bank | 4 | 2 | 2 | +₹13,918 | 1.11 |
| 1b stop 1.25× | V4 Nifty | 4 | 2 | 2 | +₹3,446 | 1.11 |
| 1b stop 1.25× | V4 Bank | 5 | 3 | 3 | +₹53,388 | 1.39 |
| 1b stop 1.25× | Skill Nifty | 8 | 3 | 4 | +₹23,576 | 2.22 |
| 1b stop 1.25× | Skill Bank | 9 | 1 | 1 | −₹68,585 | 2.50 |
| 1b stop 1.25× | (lA) Nifty | 3 | 3 | 3 | +₹35,055 | 0.83 |
| 1b stop 1.25× | (lA) Bank | 4 | 3 | 3 | +₹67,146 | 1.11 |
| 1b stop 1.25× | V5 Nifty | 3 | 2 | 2 | +₹10,274 | 0.83 |
| 1b stop 1.25× | V5 Bank | 4 | 2 | 2 | +₹23,302 | 1.11 |

Verdict (1): discard all four variants as replacements; keep base. No variant raises frequency on any track (trade counts never change — only exits move). The mechanisms are instructive and opposite by track: wider stops / farther targets destroy Skill Bank — at stop 1.25× its two big base targets (1 Oct +₹16,640, 5 Oct +₹25,690) both miss the farther target and stop out larger, leaving only 23 Oct green (−₹68,585 total); at target 2.5× the same two targets are missed (−₹51,215). The one eye-catching gain, (lA) Bank at stop 1.25× (+₹67,146, 3/4 green), is a single-day flip: 8 Oct's base stop (−₹8,510) survives the wider stop and reaches target (+₹21,135). One day, in-sample, is not a reason to widen stops. Target 1.5× is uniformly worse on net for V4/(lA)/V5 despite one extra Skill full-target per track — smaller wins, same stops.

**(2) Room thresholds — full table:**

| Variant | Track | Trades | FT | Green | Net | /week |
|---|---|---|---|---|---|---|
| Room 1.5× | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Room 1.5× | V4 Bank | 3 | 3 | 3 | +₹54,780 | 0.83 |
| Room 1.5× | Skill Nifty | 1 | 0 | 0 | −₹4,605 | 0.28 |
| Room 1.5× | Skill Bank | 1 | 0 | 0 | −₹4,640 | 0.28 |
| Room 1.5× | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Room 1.5× | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Room 1.5× | V5 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Room 1.5× | V5 Bank | 2 | 2 | 2 | +₹30,720 | 0.56 |
| Room 2.0× | V4 Nifty | 4 | 2 | 2 | +₹8,080 | 1.11 |
| Room 2.0× | V4 Bank | 2 | 2 | 2 | +₹44,260 | 0.56 |
| Room 2.0× | Skill Nifty | 1 | 0 | 0 | −₹4,605 | 0.28 |
| Room 2.0× | Skill Bank | 0 | 0 | 0 | ₹0 | 0.00 |
| Room 2.0× | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Room 2.0× | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Room 2.0× | V5 Nifty | 3 | 2 | 2 | +₹13,550 | 0.83 |
| Room 2.0× | V5 Bank | 1 | 1 | 1 | +₹20,200 | 0.28 |
| Room 2.5× | V4 Nifty | 3 | 2 | 2 | +₹11,360 | 0.83 |
| Room 2.5× | V4 Bank | 2 | 2 | 2 | +₹44,260 | 0.56 |
| Room 2.5× | Skill Nifty | 0 | 0 | 0 | ₹0 | 0.00 |
| Room 2.5× | Skill Bank | 0 | 0 | 0 | ₹0 | 0.00 |
| Room 2.5× | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Room 2.5× | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Room 2.5× | V5 Nifty | 3 | 2 | 2 | +₹11,360 | 0.83 |
| Room 2.5× | V5 Bank | 1 | 1 | 1 | +₹20,200 | 0.28 |

Verdict (2): discard as a frequency/hits fix; keep base. Room tightening buys full-target rate (100% on the surviving V4/V5 Bank trades) by deleting trades, never by adding them — the opposite of what the frequency leg needs. It annihilates Skill: at 1.5× only one losing trade survives per track (Nifty 12 Oct −₹4,605; Bank 12 Oct −₹4,640); at 2.5× Skill has zero trades on both tracks. (lA) is completely insensitive — identical trade sets at 1.5×/2.0×/2.5×, i.e. all seven (lA) rescan signals already clear 2.5× room, so room is not a binding constraint for (lA). The only net-positive room move, V4 Nifty at 2.0× (+₹8,080 vs +₹2,725), comes from a different 26 Oct signal (stop −₹3,280 instead of −₹8,635) — one signal change, not a pattern, and it still leaves frequency at 1.11/week.

**(3) Prospective target filters — full table (₹1,000 and ₹1,500 identical to base):**

| Variant | Track | Trades | FT | Green | Net | /week |
|---|---|---|---|---|---|---|
| Pros ≥₹1,000 | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Pros ≥₹1,000 | V4 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Pros ≥₹1,000 | Skill Nifty | 8 | 2 | 3 | +₹8,420 | 2.22 |
| Pros ≥₹1,000 | Skill Bank | 9 | 3 | 3 | +₹8,675 | 2.50 |
| Pros ≥₹1,000 | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Pros ≥₹1,000 | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Pros ≥₹1,000 | V5 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Pros ≥₹1,000 | V5 Bank | 4 | 3 | 3 | +₹43,630 | 1.11 |
| Pros ≥₹1,500 | (all 8 tracks) | identical to ≥₹1,000 rows above on every track | | | | |

Verdict (3): inert at these levels; keep base ₹500 (V5) / no filter (others). The smallest prospective target net among all 31 base trades is ₹2,750 (Skill Bank 6 Oct; next smallest ₹4,240). Index point risks are so large that ₹500/₹1,000/₹1,500 filters cannot bite — a filter would need to exceed ₹2,750 before it drops even one October trade. Do not quote ₹1,000/₹1,500 as "tested and passed"; they changed nothing.

**(4) Cap rules — full table:**

| Variant | Track | Trades | FT | Green | Net | /week |
|---|---|---|---|---|---|---|
| V5 no cap (dedup pool only) | V5 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| V5 no cap | V5 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| V5 pooled 1/week | V5 Nifty | 2 | 1 | 1 | −₹3,195 | 0.56 |
| V5 pooled 1/week | V5 Bank | 3 | 2 | 2 | +₹33,110 | 0.83 |
| V5 2/symbol/week | V5 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| V5 2/symbol/week | V5 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Track cap 1/week | V4 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Track cap 1/week | V4 Bank | 4 | 3 | 3 | +₹43,630 | 1.11 |
| Track cap 1/week | Skill Nifty | 3 | 1 | 1 | −₹1,955 | 0.83 |
| Track cap 1/week | Skill Bank | 5 | 2 | 2 | +₹130 | 1.39 |
| Track cap 1/week | (lA) Nifty | 2 | 2 | 2 | +₹16,630 | 0.56 |
| Track cap 1/week | (lA) Bank | 2 | 1 | 1 | +₹12,725 | 0.56 |
| Track cap 2/week | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Track cap 2/week | V4 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Track cap 2/week | Skill Nifty | 5 | 1 | 1 | −₹10,150 | 1.39 |
| Track cap 2/week | Skill Bank | 7 | 3 | 3 | +₹21,180 | 1.94 |
| Track cap 2/week | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Track cap 2/week | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |

Verdict (4): keep base caps; do not loosen or tighten on October evidence. The base V5 cap is a double-edged, track-dependent effect versus no cap: on Nifty it helps (+₹8,195 vs +₹2,725, by dropping the 28 Oct loser −₹5,470), on Bank it hurts badly (+₹43,630 vs +₹67,690, by dropping the 23 Oct winner +₹24,060 under 1/symbol/week). Pooled 1/week is worse on both tracks. Track cap 1/week on V4 reproduces the V5 base numbers exactly (same ranking picks), confirming the cap — not the pool — is what shapes V5. Track cap 2/week lifts Skill Bank to +₹21,180 (7 trades, 1.94/week) but flips Skill Nifty to −₹10,150 (5 trades, 1 green) — cap ranking by prospective size does not reliably pick winners. No cap variant gets any track near 5/week, because the candidate counts themselves are the binding constraint (max uncapped: Skill Bank 9 trades = 2.50/week).

**(5) Bias bands — full table:**

| Variant | Track | Trades | FT | Green | Net | /week |
|---|---|---|---|---|---|---|
| Wide neutral (bear <25%, bull ≥85%) | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Wide neutral | V4 Bank | 5 | 3 | 3 | +₹51,520 | 1.39 |
| Wide neutral | Skill Nifty | 10 | 3 | 4 | +₹5,130 | 2.78 |
| Wide neutral | Skill Bank | 12 | 5 | 5 | +₹28,690 | 3.33 |
| Wide neutral | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Wide neutral | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Wide neutral | V5 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Wide neutral | V5 Bank | 4 | 2 | 2 | +₹31,320 | 1.11 |
| Narrow neutral (bear <45%, bull ≥70%) | V4 Nifty | 4 | 2 | 2 | +₹2,725 | 1.11 |
| Narrow neutral | V4 Bank | 5 | 4 | 4 | +₹67,690 | 1.39 |
| Narrow neutral | Skill Nifty | 8 | 2 | 3 | +₹8,420 | 2.22 |
| Narrow neutral | Skill Bank | 8 | 3 | 3 | +₹10,110 | 2.22 |
| Narrow neutral | (lA) Nifty | 3 | 3 | 3 | +₹28,020 | 0.83 |
| Narrow neutral | (lA) Bank | 4 | 2 | 2 | +₹28,275 | 1.11 |
| Narrow neutral | V5 Nifty | 3 | 2 | 2 | +₹8,195 | 0.83 |
| Narrow neutral | V5 Bank | 4 | 3 | 3 | +₹43,630 | 1.11 |

Verdict (5): widened neutral is the only family with a genuine frequency gain, but it is NOT kept as best — it is the one candidate worth frozen validation, not adoption. Widening neutral unblocks previously bearish-blocked CE signals: Skill gains 15 Oct Nifty target (+₹3,640) and 22 Oct Nifty stop (−₹6,930), plus Bank 13 Oct target (+₹10,170), 15 Oct target (+₹17,370) and 21 Oct stop (−₹7,525) — net up on both tracks (Nifty +₹5,130, Bank +₹28,690) and frequency up to 2.78/3.33 per week, the highest frequency of any variant in this sweep. But it still fails all three legs jointly (Bank full-target rate 5/12 = 42% < 50%; frequency still < 5/week; V4 Bank and V5 Bank nets fall as their allowed-direction sets change). Narrowed neutral is essentially inert except dropping one Skill Bank trade (net +₹10,110 vs +₹8,675). (lA) is identical under both band changes, as predicted by its construction.

**Overall verdict — Family A: keep base, nothing adopted.**
- Best kept per track remains the base definition: (lA) v2 for hits (Nifty 3/3, Bank 2/4), V5-v2 Bank for Bank net (+₹43,630), Skill v2 for frequency (2.22–2.50/week). No parameter variant in families (1)–(5) improves net, win/full-target rate, and frequency together on any track.
- Closest to the 5/week leg: widened-neutral Skill Bank, 3.33/week — still 1.67/week short, with a sub-50% full-target rate. Frequency cannot be fixed by parameters: the uncapped candidate ceiling in October is 9 trades (Skill Bank). Reaching 1/day needs new setup definitions, not parameter loosening — consistent with the v2 report's conclusion.
- Explicit discards: target 1.5× (smaller wins, same stops); target 2.5× and stop 1.25× (destroy Skill Bank); stop 0.75× (more stops, lower nets everywhere); room ≥1.5× as an S1 filter (kills Skill outright); prospective ₹1,000/₹1,500 (inert — do not present as a selectivity improvement); pooled 1/week cap (worse on both V5 tracks); track cap 1/week for Skill/(lA) (drops winners, Skill Nifty goes negative).
- Candidates for frozen out-of-sample validation only (not adoption): (a) widened-neutral bias bands applied to Skill S1; (b) stop 1.25× for (lA) Bank only, flagged as a single-day (8 Oct) flip. Both must be frozen and scored on unseen data (November paper) before any claim.
- Caveats for merging: (i) all variants are spot provisional per 100 shares, not options-lot profits — premium behaviour (notably the 23 Oct spot-target/premium-loss divergence in the base report) could reverse any of these rankings; (ii) October has only 18 days, so every "improvement" above is 1–3 trades wide; (iii) V5 no-cap equalling V4 uncapped means every V4 candidate outranks Skill on shared dates under V5 dedup — the pool adds nothing beyond V4 in October once the cap is removed.

**All four progressive families are now complete (A, B, C, D). Tuning continues — it does not stop here.**
**Next, in order:** (1) Premium completion for all October (lA) v2 / Skill v2 / V5-v2 trades via browser-fetch, so ranking is on premiums, not spot provisional; (2) O1 cross-confirmation persistence scored on Jan–Oct per track; (3) new setup definitions for frequency (not cap/filter loosening); (4) frozen validation candidates only: widened-neutral Skill S1, stop 1.25× (lA) Bank, C1-O1 Skill Bank / (lA) Bank, C2-R1 Skill Nifty / Skill Bank / (lA) Bank, C3-pullback Skill Bank, C4a (lA) Bank, C4b Skill Nifty — each to survive November paper alone before any adoption claim, nothing combined yet.
**Next family after A/D:** Premium completion for all October (lA) v2 / Skill v2 / V5-v2 trades via browser-fetch, then O1 cross-confirmation persistence scored on Jan–Oct per track, then new setup definitions for frequency (not cap/filter loosening).
**Next family after A/C/D:** Premium completion for all October (lA) v2 / Skill v2 / V5-v2 trades via browser-fetch, then O1 cross-confirmation persistence scored on Jan–Oct per track, then new setup definitions for frequency (not cap/filter loosening).

## Progress section — 2026-10-30, Premium Completion (October 2026, all 31 taken trades)

**Scope:** INDEX ONLY, paper only, no orders, no stocks. This is the family after A–D, delivered because the user saw no backtest results and asked what the stopper was. The stopper for premium scoring was the Bank option-chain gap and the missing October option candles — both are now resolved for October (see below); the Muse connector (still 401) was NOT used and NOT waited for.

**Method, frozen before scoring:**
- Spot signals reconstructed from the progressive spot cache for every TAKEN trade in [index_options_v2_october_trades.csv](sandbox://workspace/trading/index_options_v2_october_trades.csv): Skill S1 = first close beyond 09:15–09:30 OR, 09:30–11:30, with S1 blocks; V4/V5 = `find_signal` from `daytrader_cash_backtest.py`; (lA) v2 = signal times verbatim from the v2 CSV. Reconstruction verified: Skill and V5 spot nets match the v2 CSV to the rupee on all 24 recomputed trades (0 mismatches); (lA) nets taken verbatim from the v2 CSV. Script: [premium_completion_oct.py](sandbox://workspace/trading/premium_completion_oct.py), reconstruction: [index_options_premium_recon_oct.csv](sandbox://workspace/trading/index_options_premium_recon_oct.csv).
- Option candles fetched via the existing browser-fetch script-token route (Playwright + localhost forwarder, same pattern as `v4_options_browser_fetch.py`): [premium_fetch_oct.py](sandbox://workspace/trading/premium_fetch_oct.py). Profile check 200. 25 unique contract-days: 6 already cached, 19 newly fetched, every fetch 200 with 77 candles. Raw data under `~/workspace/trading/v4_options_oct_data/` (files `candles_premium_*.json` plus the 6 legacy files).
- Expiry convention (stated, carried from the v4 options report): monthly **2026-10-27** for all trades dated 1–27 Oct, weekly **2026-11-03** for 28 Oct trades. Strike = ATM nearest 100 to entry spot. **Caveat:** early-October trades are therefore scored on a long-dated monthly contract, not a weekly — a weekly trader's premiums would differ. This convention is stated, not hidden.
- Premium exit rule (options overlay, applied uniformly so versions are comparable on premiums): entry premium = open of the first 5-min option candle with time > spot signal time (= signal+5min entry bar); stop = entry − 50 option points; target = entry + 90 option points, for BOTH CE and PE (premium falls when the trade goes wrong, rises when it goes right, either direction); stop checked before target on every bar including the entry bar; square-off = 15:10 bar close; net per 1 lot = (exit − entry) × lot − ₹220 assumed cost; lot Nifty 65 / Bank 30. Scorer: [premium_score_oct.py](sandbox://workspace/trading/premium_score_oct.py). Full trade table: [index_options_premium_october_trades.csv](sandbox://workspace/trading/index_options_premium_october_trades.csv).
- **What this rule is NOT:** it is the V4/V5-v2 options rule from the v2 frozen spec. It is NOT Skill's or (lA)'s native rule (native spot rule: stop = signal-bar high/low, target = 2× spot risk). Premium does not move 1:1 with spot, so no spot-risk translation onto premium was attempted. Skill/(lA) premium rows below are therefore "the V4-overlay premium outcome of their spot signals", NOT "Skill/(lA) as originally defined, traded on premiums". Their native spot nets are shown alongside for exactly that reason. By construction every premium target is +₹2,480 (Bank) / +₹5,630 (Nifty) and every premium stop is −₹1,720 (Bank) / −₹3,470 (Nifty) — premium ranking is compressed versus spot ranking, and must be read that way.
- Validation: 5 of the 6 previously computed v4 options trades reproduce exactly (entry, exit, time, reason, net). The 6th apparent "fail" is a key collision, not a scorer bug: Skill Nifty 26 Oct CE (signal 09:50, entry bar 09:55, premium 132.05 → target 222.05, +₹5,630) and V4 Nifty 26 Oct CE (signal 09:55, entry bar 10:00, premium 197.55 → stop 147.55, −₹3,470) share the same contract (22600CE, 27 Oct) — entry timing alone flips the outcome. The V4 row itself validates OK.
- Bank chain gap: did NOT block October completion. No Bank trade dated 28 Oct is in the taken list (Skill Bank 28 Oct is S1-blocked), so all Bank trades use 27-Oct contracts. Nifty 28 Oct uses the Nov-03 chain, which returned a full chain (104 strikes). The Bank post-October chain gap remains open for any future (November) Bank premium work, not for October.

**Results — premium, per version per index separately, never pooled (frequency = trades ÷ 18 days × 5):**

| Version / index | Trades | Targets | Stops | Sq-offs | Green | Full-target | Premium net / 1 lot | Spot prov. net (same trades) | /week |
|---|---|---|---|---|---|---|---|---|---|
| V5-v2 Bank | 4 | 4 | 0 | 0 | 4 (100%) | 100% | **+₹9,920.00** | +₹43,630 | 1.11 |
| (lA) v2 Nifty | 3 | 1 | 0 | 2 | 2 (66.7%) | 33.3% | **+₹6,678.50** | +₹28,020 | 0.83 |
| Skill v2 Nifty | 8 | 2 | 4 | 2 | 4 (50.0%) | 25.0% | **+₹3,394.50** | +₹8,420 | 2.22 |
| (lA) v2 Bank | 4 | 2 | 2 | 0 | 2 (50.0%) | 50.0% | **+₹1,520.00** | +₹28,275 | 1.11 |
| V5-v2 Nifty | 3 | 1 | 1 | 1 | 1 (33.3%) | 33.3% | **+₹825.25** | +₹8,195 | 0.83 |
| Skill v2 Bank | 9 | 3 | 6 | 0 | 3 (33.3%) | 33.3% | **−₹2,880.00** | +₹8,675 | 2.50 |
| Volrix v2 Nifty / Bank | 0 / 0 | — | — | — | — | — | ₹0 | ₹0 | 0 |

**Ranked on premiums (per index, then overall — version totals across separate tracks are labelled, never a portfolio P&L):**
- Bank: V5-v2 (+₹9,920, 100% targets) > (lA) v2 (+₹1,520, 50%) > Skill v2 (−₹2,880, 33.3%).
- Nifty: (lA) v2 (+₹6,678.50, 33.3% targets but 66.7% green via square-offs) > Skill v2 (+₹3,394.50, 25.0%) > V5-v2 (+₹825.25, 33.3%).
- Version totals (two separate tracks summed for ranking only): V5-v2 +₹10,745.25 (7 trades) > (lA) v2 +₹8,198.50 (7 trades) > Skill v2 +₹514.50 (17 trades). Total across all six separate tracks: premium +₹19,458.25 vs spot provisional +₹125,215 on the same trades — the spot-to-premium ratio is ~0.16, i.e. spot points × 100 shares massively overstate option-lot outcomes, as the 23 Oct case already warned.
- **Verdict: NO version meets all legs on premiums either (≥5/week + net > 0 + full-target ≥ 50%). Nothing adopted on October alone.** Frequency leader is still Skill Bank (2.50/week) — and on premiums it is net negative, so frequency without premium edge is worthless. Best premium hits, V5 Bank (100%), is at 1.11/week. Best premium net per index (V5 Bank, (lA) Nifty) both fail frequency. The spot ranking and the premium ranking agree on the per-index winners (Bank: V5; Nifty: (lA)) but disagree sharply on magnitudes and on Skill Bank (spot +₹8,675 → premium −₹2,880, a sign flip).

**Spot → premium flips (7 of 31 trades change outcome class; the rest keep their class):**
- (lA) Nifty 8 Oct PE: spot target +₹11,690 → premium square-off +₹2,383.25 (entry 247.05, exit 287.10 at 15:10; premium rose only +40, never reached +90 target 337.05, never touched −50 stop).
- (lA) Nifty 23 Oct PE: spot target +₹11,390 → premium square-off −₹1,334.75 (entry 125.85, exit 108.70; premium never reached target 215.85 nor stop 75.85 — the known spot-target/premium-loss divergence, reproduced).
- Skill Nifty 6 Oct CE: spot target +₹4,240 → premium square-off +₹1,801.50 (entry 359.90, exit 391.00; premium rose +31, short of +90).
- Skill Nifty 12 Oct PE: spot stop −₹4,605 → premium square-off +₹4,213.00 (entry 250.80, exit 319.00; premium never fell 50 after entry — the fixed −50 premium stop is wider, in premium terms, than this trade's small spot stop — then premium rose into the close).
- Skill Nifty 26 Oct CE: spot square-off +₹16,550 → premium target +₹5,630 (entry 132.05 at 09:55, target 222.05 at 10:05).
- V5 Bank 13 Oct PE: spot stop −₹3,730 → premium target +₹2,480 (entry 547.35, target 637.35 at 11:45).
- V5 Nifty 23 Oct PE: same trade as (lA) Nifty 23 Oct (shared signal) — spot target +₹11,390 → premium square-off −₹1,334.75.
- All other 24 trades keep their spot outcome class on premiums (target→target, stop→stop, square-off→square-off), but at the compressed fixed premium amounts above.

**What changed vs the pre-completion picture:** before this section, premium-known subsets were 2 trades (V5 Bank +₹4,960), 1 trade ((lA) Nifty −₹1,334.75), 2 trades (V5 Nifty −₹4,804.75), 1 trade (Skill Nifty −₹3,470), and 0 for Skill Bank and (lA) Bank. Now all 31 taken trades are premium-scored and **0 are NOT_COMPUTED** for October. The two trades previously shown as premium losses in isolation (V5 Nifty 23 + 26 Oct = −₹4,804.75) are now joined by the 8 Oct premium target (+₹5,630), giving V5 Nifty +₹825.25 — the earlier subset ranking must not be quoted anymore.

**Task 2 (O1 Jan–Oct) — not scored in this section, by the task's own condition:** the task ordered O1 Jan–Oct only if premium fetch was blocked for a track. It was not blocked for any track (31/31 computed), so O1 Jan–Oct was not run here and is NOT claimed. It remains the next family in order, after premium completion: O1 (confirmer still below its OR low on both signal and entry bars) scored on Jan–Oct per track from cached spot data, frozen before scoring. October-only O1 was already scored in Family C (keeps: Skill Bank, (lA) Bank; discards elsewhere).

**Next, in order (tuning continues, nothing adopted):** (1) O1 cross-confirmation persistence, Jan–Oct per track; (2) new setup definitions for frequency (not cap/filter loosening); (3) frozen validation candidates, each alone on November paper from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November.

## Progress section — 2026-10-30, Point 1 "Complete now": O1 Jan–Oct + New Setups NS1–NS6

Index OPTIONS only, paper only, no orders, no stocks. Target bar: ALL legs together in-sample — net > 0, full-target >= 50%, frequency >= 5/week — on BOTH Jan–Oct 2026 AND October 2026 premiums, per version per index separately. Spot provisional = points x 100 shares - ₹40/leg, NOT an options-lot profit, NOT a futures profit. Premium = per 1 lot, -50/+90 overlay, ₹220 assumed cost, Nifty lot 65 / Bank lot 30.

### O1 Jan–Oct (frozen: index_options_o1_janoct_frozen.md; report: index_options_o1_janoct_report.md; trades: index_options_o1_janoct_trades.csv)
O1 = PE breakdown taken only if confirmer still below its OR low on BOTH signal and entry bars; CE kept. October cross-check passed on all 8 tracks exactly. (lA) base corrected: merged Jan–Oct JSONs (base 11:30 rescan, no L1, dropping Bank 8 Oct 13:15 and Nifty 21 Oct 11:35) were rejected; fresh L1 implementation used.

| Track | Base trades/net prov. | O1 trades/net prov. | O1 win / FT | O1 /wk | Verdict |
|---|---|---|---|---|---|
| V4 Nifty | 46 / +₹33,130 | 24 / +₹29,005 | 50.0% / 50.0% | 0.59 | DISCARD — net falls, frequency halved |
| V4 Bank | 46 / -₹28,635 | 26 / +₹15,755 | 34.6% / 34.6% | 0.64 | KEEP candidate (Jan–Oct only, weak) — sign flip, October-driven (ex-Oct -₹45,145) |
| Skill v2 Nifty | 125 / +₹47,265 | 77 / +₹30,155 | 37.7% / 36.4% | 1.90 | DISCARD |
| Skill v2 Bank | 130 / -₹157,750 | 89 / -₹67,330 | 31.5% / 28.1% | 2.19 | DISCARD — October keep does NOT survive |
| (lA) v2 Nifty | 45 / +₹114,060 | 38 / +₹85,270 | 71.1% / 52.6% | 0.94 | DISCARD — removes winners only (7 filtered, all winners, +₹28,790) |
| (lA) v2 Bank | 39 / -₹21,320 | 34 / +₹29,055 | 44.1% / 32.4% | 0.84 | KEEP candidate (Jan–Oct only) — losers only filtered; ex-Oct -₹6,695 |
| V5-v2 Nifty | 32 / +₹47,965 | 20 / +₹37,610 | 50.0% / 50.0% | 0.49 | DISCARD |
| V5-v2 Bank | 40 / +₹16,415 | 22 / +₹26,145 | 36.4% / 36.4% | 0.54 | DISCARD — marginal gain for halved frequency |

O1 finding: good Bank PE filter trapped in bad tracks — Skill Bank PE leg +₹8,885 → +₹99,305 under O1, but its CE leg (-₹166,635, untouched by a PE-only filter) keeps the track negative. No O1 track reaches 5/week.

### New setups NS1–NS6 (report: index_options_newsetups_report.md; frozen files per family; October premiums: index_options_newsetup_premium_october_trades.csv, 84 legs, 0 NOT_COMPUTED)
Jan–Oct spot (203 days), then October spot + premiums. Scorer reproduces October bases exactly (Skill S1 Nifty 8/+₹8,420, Bank 9/+₹8,675; V4 uncapped Nifty 4/+₹2,725, Bank 5/+₹67,690).

| Family | Jan–Oct Nifty: trades / FT / net prov. / wk | Jan–Oct Bank: trades / FT / net prov. / wk | Oct premium Nifty: net / FT / wk | Oct premium Bank: net / FT / wk | Verdict |
|---|---|---|---|---|---|
| NS1 second signal/day | 201 / 35.8% / +₹56,760 / 4.95 | 195 / 31.8% / +₹14,130 / 4.80 | +₹1,696.50 / 23.1% / 3.61 | +₹1,120.00 / 42.9% / 3.89 | FAILS, CLOSEST — only family near frequency; fails FT everywhere and Oct frequency |
| NS2 afternoon rescan 11:30→15:00 | 152 / 38.8% / +₹63,400 / 3.74 | 146 / 30.1% / -₹120,970 / 3.60 | -₹1,050.75 / 25.0% / 3.33 | -₹400.00 / 40.0% / 2.78 | FAILS — afternoon legs positive Jan–Oct spot (+₹16,135 Nifty, +₹36,780 Bank) but add only 0.67/0.39 per wk, and hurt Oct premiums |
| NS3 gap-class | 73 / 28.8% / -₹49,380 / 1.80 | 58 / 37.9% / +₹82,295 / 1.43 | -₹4,395.50 / 0% / 1.39 | -₹960.00 / 33.3% / 0.83 | FAILS |
| NS4 OR re-break | 60 / 28.3% / -₹19,440 / 1.48 | 60 / 41.7% / +₹98,750 / 1.48 | +₹2,885.75 / 33.3% / 0.83 | +₹4,000.00 / 60.0% / 1.39 | FAILS — Bank Oct premium passes net+FT but fails frequency and Jan–Oct FT |
| NS5a Skill rescan | 95 / 41.1% / +₹34,085 / 2.34 | 90 / 30.0% / -₹52,235 / 2.22 | +₹8,710.50 / 14.3% / 1.94 | -₹6,120.00 / 16.7% / 1.67 | FAILS — sharpest spot→premium reversal (Nifty Oct spot FT 57.1% → premium 14.3%) |
| NS5b CE mirror | 29 / 20.7% / -₹20,770 / 0.71 | 28 / 17.9% / -₹95,040 / 0.69 | -₹1,668.50 / 0% / 0.56 | -₹3,440.00 / 0% / 0.56 | FAILS |
| NS6 session-range | 15 / 13.3% / -₹14,975 / 0.37 | 12 / 33.3% / +₹6,835 / 0.30 | -₹6,940.00 / 0% / 0.56 | 0 trades | FAILS |

NS1 detail: second legs only Jan–Oct — Nifty 76 legs, 31.6% FT, +₹9,495; Bank 65 legs, 40.0% FT, +₹171,880 (concentrated Jan +₹72,270 and Mar +₹57,495, Jun -₹38,350 — rescue, not steady). Oct premiums: Nifty second legs -₹1,698 drag base +₹3,394.50; Bank second legs +₹4,000 rescue base -₹2,880 — same mechanic helps one index, hurts the other.

### Point 1 verdict — NO in-sample candidate passes all legs together
No O1 track and no NS1–NS6 family passes net > 0 AND full-target >= 50% AND frequency >= 5/week on BOTH Jan–Oct AND October premiums, on either index. Closest: NS1 — the only family near frequency (Jan–Oct 4.95/4.80 per wk, net positive both indices in Jan–Oct spot and Oct premiums), but it fails full-target on every window/index (Jan–Oct 35.8%/31.8%, Oct spot 38.5%/42.9%, Oct premium 23.1%/42.9%) and Oct frequency (3.61/3.89). Previous best kept unchanged: Nifty (lA) v2, Bank V5-v2 on October premiums — NOT adopted. NS1 is the only family worth carrying as a frozen November-paper watch candidate, not an adoption. Next direction (not attempted here, by the frozen-then-discard rule): hit quality of second/afternoon legs — why NS1 second legs hit only 31.6%/40.0% Jan–Oct, and why NS5a spot targets do not become premium targets. NOTHING is adopted on in-sample alone: any candidate still needs November paper from Mon 2026-11-02, separate Nifty/Bank logs, no re-tuning during November, before adoption.

## Progress section — 2026-10-30, Volrix tuned (index OPTIONS only, paper only)

**Source:** child report, October 2026 first (1–28 Oct, 18 days), then Jan–Oct spot
check. Full report: [index_options_volrix_tuned_oct30.md](sandbox://workspace/trading/index_options_volrix_tuned_oct30.md);
fetch script: [volrix_tuned_fetch_oct30.py](sandbox://workspace/trading/volrix_tuned_fetch_oct30.py).
Old spot-proxy futures nets (Nifty +₹3,37,730 / Bank +₹62,737 over 7 years) are NOT
results for these variants and are not used below. No unfired trigger is counted
as a trade. Nothing adopted on October/in-sample alone; November paper from
Mon 2026-11-02 remains validation.

**Frozen definitions (before premium scoring):** LONG ATM CALL, 1 lot (Nifty 65 /
Bank 30), cost ₹220, strike ATM nearest 100, expiry monthly 27 Oct (no tuned entry
falls on 28 Oct, so the weekly 3 Nov rule is unexercised), premium entry = open of
first 5-min option candle after the signal time, square-off/exit bar 15:10 (original
code used 15:15; 15:10 matches the October premium convention, stated). Cooldown
10 sessions kept in EVERY variant. Skip-after-expiry quirk NOT simulated in the
Jan–Oct spot check (nil effect in October, stated as a limitation for Jan–Oct).
- (a) Threshold lowered, else original: trigger -1.5% / -1.25% / -1.0% separately,
  5-session hold, NO stop/target, expiry inside hold = exit at expiry, no roll.
- (b) Intraday adaptation: same triggers, entry next session, exit same day 15:10,
  **stop entry-50 / target entry+90 premium points, frozen**, stop before target
  per bar including entry bar, cooldown still applies.
- (c) Primary confirmation: trigger -1.0%, taken Skill S1 CE signal on entry day
  only ((lA) is PE-only and cannot confirm a CE; a blocked S1 CE is NOT
  confirmation), else no trade, 5-session hold as in (a).
- (c-raw) Sensitivity, separate: raw morning OR direction only — 5-min spot close
  above entry-day OR high (09:15–09:55 OR) at or before 11:30, ignoring the S1
  bias block; entry delayed to the first option bar after the confirming signal,
  strike ATM nearest 100 to that entry spot.

**October triggers:** Nifty 8 Oct -1.64% and 19 Oct -1.11%; Bank 23 Oct -1.16%.
October-isolated (fresh state 1 Oct): (a)/(b) Nifty 1 trade at every threshold
(9 Oct only — 21 Oct blocked by cooldown); (a)/(b) Bank 1 trade at -1.0% only
(26 Oct), 0 at -1.25%/-1.5%. **Continuity warning:** in a continuous run Nifty
-1.25%/-1.5% has ZERO October trades (25 Sep entry, trigger 24 Sep -1.63%, still
in cooldown on 9 Oct); their October-isolated 9 Oct premium is scored but must
not be quoted as a continuous-run October trade. Nifty -1.0% and Bank -1.0% are
unaffected.

**October premium table (actual 5-min premiums, 1 lot, -220):**

| Variant / index | Entry | Exit | Net / 1 lot |
|---|---|---|---|
| (a) Nifty (all thresholds, same 9 Oct trade) | 22200 CE / 27 Oct, 398.00 (09:20, 9 Oct) | 796.70 (15 Oct 15:10, 5th-session square-off) | +₹25,695.50 |
| (a) Bank -1.0% | 54300 CE / 27 Oct, 238.55 (09:20, 26 Oct) | 14.10 (27 Oct 15:10, monthly-expiry exit, session 2) | -₹6,953.50 |
| (b) Nifty (all thresholds, same trade) | 22200 CE, 398.00; stop 348 / target 488 | 488.00 (9 Oct 09:45, TARGET) | +₹5,630.00 |
| (b) Bank -1.0% | 54300 CE, 238.55; stop 188.55 / target 328.55 | 328.55 (26 Oct 09:55, TARGET) | +₹2,480.00 |
| (c) primary both indices | — | — | 0 trades. Nifty: 9 Oct S1 CE blocked (S1_CE_bearish). Bank: no taken S1 CE on 26 Oct (raw breakout only 15:25, no entry bar after). |
| (c-raw) Nifty | 22500 CE, 310.30 (10:10, 9 Oct; confirming close 22482.20 above OR high 22480.45) | 533.05 (15 Oct 15:10, square-off) | +₹14,258.75 |
| (c-raw) Bank | — | — | 0 trades (first close above OR high 54357.60 is 15:25, after 11:30). |

**Before / after (October premium; working test = net > 0 AND full-target >= 50%
AND >= 5/week; full-target = target exit only, so (a)/(c) are n/a by construction):**
No variant passes. Closest is (b): net > 0 and full-target 100% (1/1) on both
indices, but frequency 0.28/week (1 trade / 18 days x 5) vs 5/week required.
(a) Nifty passes neither frequency nor the full-target leg (n/a); (a) Bank fails
net as well. (c) and (c-raw) Bank trade zero times; (c-raw) Nifty (+₹14,258.75)
earns LESS than unfiltered (a) on the same hold because the delayed entry takes
the higher 22500 strike — confirmation cost premium in October, it did not add it.

**Jan–Oct 2026 spot check (continuous, cooldown + hold; spot points ONLY, NOT
rupees, NOT an options profit; Jan–Oct premiums NOT scored):**

| Index / threshold | Entries | Freq / week | Spot (a) 5-day pts (wins) | Spot (b) 1-day pts (wins) |
|---|---|---|---|---|
| Nifty -1.0% | 12 (Oct: 9 Oct) | 0.30 | +959.85 (7/12) | +618.25 (9/12) |
| Nifty -1.25% | 8 (Oct: none) | 0.20 | -1,514.20 (3/8) | -45.65 (6/8) |
| Nifty -1.5% | 7 (Oct: none) | 0.17 | -638.20 (3/7) | +363.80 (6/7) |
| Bank -1.0% | 13 (Oct: 26 Oct) | 0.32 | +948.20 on 12 scored, 8 wins (26 Oct 5th session outside 28 Oct CSV) | +2,148.65 (9/13) |
| Bank -1.25% | 9 (Oct: none) | 0.22 | +2,924.30 (7/9) | +3,284.40 (7/9) |
| Bank -1.5% | 7 (Oct: none) | 0.17 | -971.00 (4/7) | +1,393.85 (5/7) |
| (c)/(c-raw) Jan–Oct | NOT scored (confirmation not rescanned Jan–Oct; counts bounded above by the unconfirmed counts above, not claimed as confirmed). |

**Verdict:** No Volrix variant is working. 5/week is impossible for Volrix without
a fundamentally different definition (dropping the prev-day trigger or the
cooldown) — that redefinition is NOT made or scored here. Variant that trades
most often with positive October premium net is (b) intraday at -1.0% (1 trade
per index, both targets, +₹5,630 Nifty / +₹2,480 Bank per 1 lot) — the only
candidate to carry into November paper, frozen as in the full report, labelled
as an occasional overlay on exactly 2 October trades, not a daily system.

## Progress section — 2026-10-30, (lA)-only tuning (October first, new knobs on top of (lA) v2)

Index OPTIONS only, (lA) only, paper only, no orders, no stocks, no other systems, no stacked
variants, Nifty and Bank separately, never pooled. Frozen before scoring:
[index_options_la_tuned_oct30_frozen.md](sandbox://workspace/trading/index_options_la_tuned_oct30_frozen.md);
full report: [index_options_la_tuned_oct30.md](sandbox://workspace/trading/index_options_la_tuned_oct30.md);
script: [la_tune_oct30.py](sandbox://workspace/trading/la_tune_oct30.py);
legs: [index_options_la_tuned_oct30_legs.csv](sandbox://workspace/trading/index_options_la_tuned_oct30_legs.csv).
October premiums = per 1 lot, −50/+90 overlay, ₹220 cost, Nifty lot 65 / Bank lot 30, ATM nearest
100, expiry 2026-10-27 (1–27 Oct) / 2026-11-03 (28 Oct), from cached candles only — 0 NOT_COMPUTED
in any variant (all 7 base legs + all 3 new legs hit cached contracts; no browser fetch was run
or needed). Spot provisional = points × 100 shares − ₹40/leg, NOT an options-lot profit. New
variant-created legs also had to pass room/risk ≥ 1.5; that gate rejected zero candidates in
October, so it is non-binding here. Base reproduction exact: Nifty 3 legs / +₹6,678.50 premium,
Bank 4 legs / +₹1,520.00 premium, matching the October premium file to the rupee; base re-entry
fires on no October day. O1 itself was NOT re-scored (already scored Jan–Oct); X1/X4 score its
two component conditions separately.

| Variant / index | Legs (base → after) | Premium net (base → after) | Premium FT (base → after) | /week (base → after) | Spot net (base → after) | Verdict |
|---|---|---|---|---|---|---|
| W1 = W2 = W3, Nifty | 3 → 4 | +₹6,678.50 → +₹3,208.50 | 33.3% → 25.0% | 0.83 → 1.11 | +₹28,020 → +₹27,100 | DISCARD — one added loser (7 Oct 14:10, spot risk 8.8 pts, premium stop −₹3,470); W2/W3 add nothing over W1, so the three are one trade, not three confirmations |
| W1 = W2 = W3, Bank | 4 → 4 | +₹1,520 (no change) | 50.0% (no change) | 1.11 (no change) | +₹28,275 (no change) | DISCARD — no effect |
| RB1 = RB2, Nifty | 3 → 3 | no change | no change | no change | no change | DISCARD — no effect (no Nifty morning stops in Oct) |
| RB1 = RB2, Bank | 4 → 5 | +₹1,520 → +₹4,000 | 50.0% → 60.0% | 1.11 → 1.39 | +₹28,275 → +₹40,160 | CLOSEST (Bank) — net + FT pass, frequency fails |
| BF1, Nifty / Bank | 3 → 3 / 4 → 4 | no change | no change | no change | no change | DISCARD — no effect; Bank width-fail days (5, 12, 16 Oct) pass the 480 cap but have NO qualifying close at all, so width was not binding |
| BF2, Nifty / Bank | 3 → 1 / 4 → 1 | +₹6,678.50 → −₹1,334.75 / +₹1,520 → +₹2,480 | 33.3% → 0% / 50.0% → 100% | 0.83 → 0.28 / 1.11 → 0.28 | +₹28,020 → +₹11,390 / +₹28,275 → +₹20,200 | DISCARD — frequency killer; Nifty kept leg is premium-negative despite a spot target |
| S1, Nifty | 3 → 3 | no change | no change | no change | no change | DISCARD — no effect |
| S1, Bank | 4 → 5 | +₹1,520 → +₹4,000 | 50.0% → 60.0% | 1.11 → 1.39 | +₹28,275 → +₹36,435 | CLOSEST (Bank) — net + FT pass, frequency fails; same premium as RB, different spot leg (target +₹8,160 vs RB square-off +₹11,885); RB + S1 must NOT be stacked (widened band takes 13:40 first, so S1's 13:45 leg would never be reached) |
| S2, Nifty / Bank | no change | no change | no change | no change | no change | DISCARD — no effect (13:40 fail is after 13:30, so it still ends the scan) |
| X1, Nifty / Bank | no change | no change | no change | no change | no change | DISCARD — no effect; confirmer still below OR low at signal time on all 7 base legs |
| X2, Nifty | 3 → 2 | +₹6,678.50 → +₹4,295.25 | 33.3% → 50.0% | 0.83 → 0.56 | +₹28,020 → +₹16,330 | DISCARD — FT up only by deleting the 8 Oct winner |
| X2, Bank | 4 → 3 | +₹1,520 → +₹3,240 | 50.0% → 66.7% | 1.11 → 0.83 | +₹28,275 → +₹35,750 | DISCARD — net + FT up by deleting the 7 Oct loser, frequency down |
| X3, Nifty | 3 → 0 | +₹6,678.50 → ₹0 | — | 0.83 → 0 | +₹28,020 → ₹0 | DISCARD emphatically — kills the track; confirmer break closes sit above confirmer PDL on 6/7 base days |
| X3, Bank | 4 → 1 | +₹1,520 → −₹1,720 | 50.0% → 0% | 1.11 → 0.28 | +₹28,275 → −₹8,510 | DISCARD emphatically — keeps only the 8 Oct loser |
| X4, Nifty / Bank | 3 → 2 / 4 → 3 | same as X2 both | same as X2 both | same as X2 both | same as X2 both | DISCARD — identical October outcome to X2 (same 2 days dropped); decomposition finding: X4 reproduces O1's October (lA) effect exactly while X1 drops nothing, so O1's October (lA) effect is entirely its entry-bar condition |

New legs (only legs any variant adds): W NIFTY 7 Oct morning 14:10, 22600PE, entry prem 272.15,
stop −₹3,470 premium / −₹920 spot; RB BANK 8 Oct re-entry 13:40, 54600PE, entry prem 689.40,
target +₹2,480 premium / +₹11,885 spot square-off green; S1 BANK 8 Oct re-entry 13:45, 54600PE,
entry prem 702.00, target +₹2,480 premium / +₹8,160 spot target. Base BANK 7 Oct yields no
re-entry under any variant (no later close below OR low after the stop); base BANK 8 Oct
afternoon first candidate 13:40 risk 115.00 vs morning risk 84.70 is the single pivot for RB/S1.

Verdict: NO variant is working (net > 0 + FT ≥ 50% + ≥ 5/week on October premiums, per index).
Closest: BANK RB1/RB2/S1 (net + FT pass, frequency 1.39/week FAIL) and NIFTY X2/X4 (net + FT pass,
frequency 0.56/week FAIL). Nothing adopted on October alone. Structural ceiling: confirmer-break
days in October are only 7 (NIFTY) / 8 (BANK) of 18, and window/band/width knobs do not create
confirmer breaks, so the morning-leg ceiling under this knob set is 1.94 / 2.22 per week before
any quality filter, plus at most one re-entry per stop day (only BANK 8 Oct yields one) — roughly
2.2–2.5/week absolute, less than half the 5/week bar. Reaching 1/day for (lA) alone needs a new
family (a changed confirmer definition or a non-confirmed leg), not another knob here.
Jan–Oct check NOT run, by the task's condition (only for an October passer; there is none) —
Jan–Oct (lA) base/O1 numbers in this log are NOT these variants' Jan–Oct numbers. November paper
from Mon 2026-11-02 remains validation, on the BASE (lA) v2 definition unless the parent freezes
one of the "closest" variants above as a separate November watch candidate.

## Progress section — 2026-10-30, Skill-only tuning (S1 variants, October premiums)

Index OPTIONS only, paper only, no orders, no stocks, no other systems.
Skill v2 (S1) only, one variant at a time, each frozen before scoring:
[index_options_skill_tuned_oct30_frozen.md](sandbox://workspace/trading/index_options_skill_tuned_oct30_frozen.md).
Full report: [index_options_skill_tuned_oct30.md](sandbox://workspace/trading/index_options_skill_tuned_oct30.md);
script: [skill_tune_oct30.py](sandbox://workspace/trading/skill_tune_oct30.py);
fetch script: [skill_tune_fetch_missing.py](sandbox://workspace/trading/skill_tune_fetch_missing.py);
228-leg trade list: [index_options_skill_tuned_oct30_trades.csv](sandbox://workspace/trading/index_options_skill_tuned_oct30_trades.csv).
Pass bar, per index: premium net per 1 lot > 0 AND premium full-target
≥ 50% AND frequency ≥ 5/week (legs / 18 × 5), October 2026 (1–28 Oct,
18 days), premiums via the −50/+90 overlay, ₹220 assumed cost, lot
Nifty 65 / Bank 30, monthly 27 Oct expiry for 1–27 Oct, weekly 3 Nov
for 28 Oct. Base S1 recomputed and verified exact (Nifty 8 / spot
+₹8,420, Bank 9 / spot +₹8,675) before variants.

**October premium results (227/228 legs COMPUTED; only V3 Bank 28 Oct
54000CE is NOT_COMPUTED — Bank Nov-03 chain returns 0 strikes via API):**

| Variant | Nifty: legs / prem net / FT / wk | Bank: legs / prem net / FT / wk | Verdict |
|---|---|---|---|
| BASE S1 | 8 / +₹3,394.50 / 25.0% / 2.22 | 9 / −₹2,880 / 33.3% / 2.50 | Base; Bank premium-negative |
| V1 P-LOW (09:30 PE low < PDL) | 8 / +₹3,394.50 / 25.0% / 2.22 | 9 / −₹2,880 / 33.3% / 2.50 | DISCARD, inert — blocked 09:30 bars never penetrate PDL even on low |
| V2 P-2ND (09:30 PE second-close) | 8 / +₹3,394.50 / 25.0% / 2.22 | 9 / −₹2,880 / 33.3% / 2.50 | DISCARD, inert — 09:35 close also above PDL on every blocked day |
| V3 CE-NOBLOCK | 14 / +₹9,874.50 / 35.7% / 3.89 | 15 (1 NC) / +₹1,120 computed / 42.9% / 4.17 | CLOSEST ON FREQUENCY, not working — FT + freq fail both; Bank spot +₹72,065 collapses to +₹1,120 on premiums |
| V4 BIAS-WIDE (<25% / ≥85%) | 10 / +₹5,554.50 / 30.0% / 2.78 | 12 / −₹3,840 / 33.3% / 3.33 | DISCARD as a premium fix — Family A spot keep does NOT survive premiums on Bank (added legs −₹960: 13 Oct spot target → prem stop) |
| V5 OR30 | 10 / +₹8,239 / 30.0% / 2.78 | 6 / +₹2,280 / 50.0% / 1.67 | DISCARD as a system; Bank passes net+FT only, at 1.67/week |
| V6 OR20 | 9 / +₹9,024.50 / 33.3% / 2.50 | 10 / −₹4,600 / 30.0% / 2.78 | DISCARD — Bank spot −₹25,515, premium still negative |
| V7 R1-PREM (C2-R1 on premiums) | 10 / +₹5,554.50 / 30.0% / 2.78 | 12 / +₹360 / 41.7% / 3.33 | Bank sign fixed only — +₹360, FT + freq fail; 5 Oct Nifty re-entry reverses (spot target → prem stop) |
| V8 R-REV (reversal re-entry) | 11 / −₹463.50 / 18.2% / 3.06 | 11 / −₹2,120 / 36.4% / 3.06 | DISCARD — spot gains (+₹20,455 / +₹13,375) become premium losses on both |
| V9 C3-PREM (pullback on premiums) | 5 / +₹14,695 / 60.0% / 1.39 | 7 / +₹4,760 / 57.1% / 1.94 | PASSES NET+FT BOTH, FAILS FREQ ONLY — closest tracks by legs passed |
| V10 PB-FALLBACK | 8 / +₹4,285 / 37.5% / 2.22 | 9 / +₹1,320 / 44.4% / 2.50 | DISCARD — nets positive, FT + freq fail, frequency unchanged from base |
| V11 P-RESCAN (09:30 PE, PDL close ≤11:30) | 9 / +₹2,059.75 / 22.2% / 2.50 | 9 / −₹2,880 / 33.3% / 2.50 | DISCARD as a premium variant, diagnosis kept — rescues only Nifty 23 Oct (sig 10:05), which is a spot target (+₹11,390) but a premium square-off loss (−₹1,334.75) |

**09:30-PE diagnosis (proper fix, not a deletion):** the blocked 09:30 PE
bars (Nifty 16 + 23 Oct, Bank 16 Oct) never get their low below PDL and
their 09:35 closes stay above PDL, so V1/V2 cannot fire. The real issue
is timing: on 23 Oct Nifty price closes below PDL only at 10:05. V11
retains the PDL filter and relaxes only its timing, and it fires exactly
there — but the trade loses on premiums, so the pilot's 23 Oct "target"
was a spot target, not a premium target (third reproduction of the 23 Oct
spot-target/premium-loss divergence).

**Verdict: NO Skill variant passes October on premiums.** Closest family:
V3 (frequency + both nets positive, FT failing both). Closest tracks:
V9 both indices and V5 Bank (net + FT pass, frequency fail only).
Bank premium-negative is fixed in sign by V3, V5, V7, V9 and V10, but by
none with FT ≥ 50% and 5/week together. **Jan–Oct check: NOT RUN, by the
task's own condition** — it was ordered only for an October passer, and
there is none; V3/V9/V5-Bank are October-closest only, not Jan–Oct
results. Nothing adopted, nothing combined (stacking V3+V9 or V7+V3 on
October would be October-fitting and was not scored). November paper
from Mon 2026-11-02 remains validation.
