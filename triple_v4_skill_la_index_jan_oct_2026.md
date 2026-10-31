# Triple merge backtest — V4 + Day Trader Skill + (lA), Bank Nifty + Nifty, Jan–Oct 2026

Paper only. No orders placed, no live trading, no live-trading recommendation.

**NOT a new adopted version.** Jan–Oct is NOT clean validation for this merge: the dual Skill+(lA) definition was already scored on October, and the triple adds V4 to that same definition. A frozen candidate would still need unseen-month (November) validation on net + win rate + frequency together before any adoption claim. Nothing here is mixed into v4 / (lA) totals as an adopted series.

## Interpretation stated before scoring

User asked for 'lA, skill and version' — read as **V4 (the version/system) + Day Trader skill + (lA)**, all three sources pooled. This is an additional comparison on top of the dual Skill+(lA) Jan–Oct run, which was not stopped or replaced. If the user meant a different 'version', this reading must be corrected and the run re-labelled — the numbers below are for V4+Skill+(lA) only.

## Frozen definition (provisional, NOT Chandu's rule)

- **Scope:** NIFTY + BANKNIFTY only, NO stocks. **Jan 2026 to 28 Oct 2026** (203 trading days; Oct = 1–28 only, 29 Oct excluded, not in cache). Data: Upstox 5-min cache in `data/progressive/` — no fresh fetch, no missing day reported.
- **Provisional cash rules (as in the capped runs, NOT Chandu's live options rules):** 100 shares equivalent, ₹40/trade, signal-candle stop, 2× target, square-off 15:10, short paper-only, one trade/instrument/day after dedup. Index nets are point-scaled cash-equivalents (100 × index points), NOT portfolio rupees.
- **Source V4:** V4 index candidates from `progressive_capped_v2.candidates_for_month`, as in the capped-v2 Jan–Oct runs. Setup ranks: setup4=3, setup3=2, setup2=1 (Skill OR=0).
- **Source Skill:** OR-only signals with V4-style filters (bias-aligned, room ≥200×scale, PD bound), setup rank 0, as in the dual merge.
- **Source (lA):** BN-confirmed rescan morning + band-filtered re-entry (risk in [10, rescan risk], morning scan-skip to 11:30, afternoon stop-on-first-fail to 15:05), PE only, one candidate per symbol+date, day net = morning + re-entry if it trades, each leg ₹40. (lA) was defined for **NIFTY PE only**; **Bank (lA) is a MIRROR** (roles swapped, Nifty confirms Bank, scale = Bank prev close / 55000), provisional, not the original (lA). (lA) setup rank = 1 (provisional labelling: morning is a setup2-class breakdown). Prospective target net = morning target net.
- **Dedup same symbol+date:** priority **(lA) first, then V4, then Skill**. Priority decides only which source survives an overlap; cap ranking is still setup_rank → bias-strong → room_ratio → prospective target, so (lA) rank 1 ties with V4 setup2 and sits below V4 setup3/4.
- **Cap and filter, per calendar month** (as in capped-v2 Jan–Oct and the dual Jan–Oct run, so the October slice stays comparable): prospective net target ≥₹500, max 3 index trades/ISO week, max 1 trade/symbol/week (attainable max 2/week with 2 symbols). Results gate NEUTRAL.
- **Win rate = net > 0 (green)** for all series, so (lA) day greens are comparable to V4/Skill targets. (lA) 'targets' in the JSON count only morning-target days with no re-entry, hence (lA) target counts understate its green days.

## Headline — Jan–Oct 2026, capped, per source and merged

| Series | Trades | Green | Net ₹ | Expectancy ₹ | Max DD ₹ |
|---|---|---|---|---|---|
| V4-only | 62 | 27 / 43.5% | 68,770 | 1,109.19 | 87,865 |
| Skill-only | 58 | 25 / 43.1% | 40,240 | 693.79 | 94,390 |
| (lA)-only | 47 | 28 / 59.6% | 23,435 | 498.62 | 81,330 |
| Dual Skill+(lA) | 66 | 34 / 51.5% | -1,600 | -24.24 | 111,495 |
| **Triple V4+Skill+(lA)** | 74 | 35 / 47.3% | 23,355 | 315.61 | 97,220 |

| Series | Nifty trades / net ₹ | Bank Nifty trades / net ₹ |
|---|---|---|
| V4-only | 27 / 42,410 (51.9%) | 35 / 26,360 (37.1%) |
| Skill-only | 29 / 49,890 (55.2%) | 29 / -9,650 (31.0%) |
| (lA)-only | 24 / 71,780 (79.2%) | 23 / -48,345 (39.1%) |
| Dual | 32 / 79,585 (71.9%) | 34 / -81,185 (32.4%) |
| **Triple** | 33 / 71,970 (63.6%) | 41 / -48,615 (34.1%) |

**Triple composition:** 74 capped trades = 41 (lA) + 23 V4 + 10 Skill. By symbol: Nifty 33 / +₹71,970 (63.6% green), Bank Nifty 41 / −₹48,615 (34.1% green). Frequency ≈ 1.7/week over Jan–Oct.

## Comparison — does the triple beat V4?

| Series (Jan–Oct 2026, index only) | Trades | Green | Net ₹ |
|---|---|---|---|
| V4 index (best kept, paper only) | 62 | 43.5% | +₹68,770 |
| Skill index | 58 | 43.1% | +₹40,240 |
| V5 index (pooled V4+Skill, earlier run) | 72 | 41.7% | +₹64,380 |
| (lA)-only capped | 47 | 59.6% | +₹23,435 |
| Dual Skill+(lA) | 66 | 51.5% | −₹1,600 |
| **Triple V4+Skill+(lA)** | **74** | **47.3%** | **+₹23,355** |

**No — the triple does NOT beat V4 on net + win rate + frequency together.** Net is ₹45,415 below V4 (+₹23,355 vs +₹68,770), win rate is higher (47.3% vs 43.5%) but on 12 more trades, and expectancy collapses (+₹316 vs +₹1,109). It also trails V5 (+₹64,380) by ₹41,025. It beats the dual (−₹1,600) by ₹24,955, but that is V4 rescuing the dual, not synergy: the triple is still barely a third of V4 alone.

## By month — capped net ₹ (trades in brackets)

| Month | V4 | Skill | (lA) | Dual | **Triple** |
|---|---|---|---|---|---|
| 2026-01 | 9,650 (6) | 12,890 (7) | 11,875 (5) | 12,330 (7) | **6,065 (7)** |
| 2026-02 | -23,290 (6) | -5,755 (4) | -45,690 (6) | -45,690 (6) | **-29,480 (6)** |
| 2026-03 | 77,625 (6) | 77,640 (7) | 37,940 (6) | 60,120 (9) | **60,120 (9)** |
| 2026-04 | 9,955 (6) | 7,805 (8) | 31,080 (3) | 11,410 (8) | **12,295 (9)** |
| 2026-05 | 5,460 (6) | -27,015 (7) | -11,490 (5) | -28,760 (7) | **-8,705 (7)** |
| 2026-06 | -39,000 (5) | -24,190 (3) | -22,835 (2) | -26,640 (3) | **-45,255 (6)** |
| 2026-07 | -7,140 (9) | 8,010 (7) | -27,205 (5) | -30,790 (7) | **-5,300 (9)** |
| 2026-08 | -26,705 (7) | -26,705 (7) | -815 (8) | -815 (8) | **-17,480 (8)** |
| 2026-09 | 10,390 (4) | 950 (5) | 14,770 (3) | 260 (5) | **495 (5)** |
| 2026-10 | 51,825 (7) | 16,610 (3) | 35,805 (4) | 46,975 (6) | **50,600 (8)** |

Cumulative triple net: Jan +₹6,065 → Feb −₹23,415 → Mar +₹36,705 → Apr +₹49,000 → May +₹40,295 → Jun −₹4,960 → Jul −₹10,260 → Aug −₹27,740 → Sep −₹27,245 → Oct +₹23,355. Cumulative profit does NOT rise month by month — it falls Jun–Sep and is rescued by October, exactly the March/October-dependence pattern that disqualified V5. Triple beats V4 in only 3 months (Apr, May, Jul); V4 beats triple in 6 months (Jan, Feb, Jun, Aug, Sep, Oct); Mar is identical (+₹60,120 both).

## Overlaps — 77 same-day candidate overlaps before cap

Winner by priority: **(lA) 60, V4 17, Skill 0** (Skill never survives an overlap — every Skill date that overlaps another source is displaced by (lA) or V4; this is a consequence of the stated priority, not a measured quality ranking). Overlap is the rule, not the exception: the three sources are largely the same PE breakdown days seen through three lenses, which is why pooling them adds trades but not edge.

October overlaps in detail (the dual merge's blind spot, now covered):
- Bank 13 Oct: V4 setup3 bounce-rejection PE stop −₹3,730 — present in triple, absent from dual (dual has no V4 source).
- Bank 26 Oct: V4 setup3 bounce-rejection PE target +₹10,520 — present in triple, absent from dual.
- Nifty 26 Oct: V4 setup4 reclaim CE stop −₹8,635 — present in triple, absent from dual.
- Bank 23 Oct: V4 setup2 and (lA) mirror are the SAME trade (+₹24,060) — (lA) wins by priority, net unchanged. Likewise Bank 21 Oct (+₹20,200) and Nifty 23 Oct (+₹11,390).
- Nifty 8 Oct: all three sources overlap; (lA) +₹11,690 wins over V4/Skill +₹5,440 (a +₹6,250 same-day difference, as in the dual report).
- Triple October: **8 trades, 62.5% green, +₹50,600** — vs dual October 6 / 66.7% / +₹46,975 and V4 October 7 / 71.4% / +₹51,825. Triple October still trails V4 October by ₹1,225 despite one extra trade: triple = V4 October (₹51,825) − V4 8 Oct ₹5,440 + (lA) 8 Oct ₹11,690 − Bank 7 Oct (lA) stop ₹7,475 = ₹50,600. The Bank 23 Oct (lA) trade is capped out in both dual and triple (see below).
- October cap note: Bank 23 Oct (lA) +₹24,060 is in the triple's ranked pool but capped out in October (W43 already has Bank 21 Oct), exactly as in the dual merge — the triple does not rescue it, because the cap is per symbol/week, not per source.

## (lA) re-entry legs — now actually tested (unlike October)

Across Jan–Oct, **30 (lA) candidates fire a re-entry leg** (before cap), with only **11/30 day-green** and a combined day net of −₹1,56,125 (day net = morning stop + re-entry result). In the capped triple, **20 (lA) trades carry a re-entry leg, net −₹91,090**. The re-entry leg is a drag, not a fix, on this window — and it is concentrated in Bank Nifty: the worst triple trades are (lA) Bank re-entry days (29 Jun Bank −₹24,935; 14 May Bank −₹18,995; 8 Jul Bank −₹14,995). Nifty re-entries are mostly small greens (e.g. 9 Jan Nifty day +₹2,295 after a −₹3,745 morning stop). This is the first window where (lA) re-entry is actually observed at scale, and it does not support the (lA) re-entry rule — but Bank (lA) is a mirror, so this condemns the mirror + re-entry combination, not the original Nifty (lA) alone.

## The split that explains everything

| (lA)-only | Trades | Green | Net ₹ |
|---|---|---|---|
| Nifty (lA) — original rule | 24 | 79.2% | +₹71,780 |
| Bank Nifty (lA) — mirror | 23 | 39.1% | −₹48,345 |

The triple's Nifty leg (+₹71,970) is essentially the Nifty (lA) leg (+₹71,780). The triple's Bank leg (−₹48,615) is essentially the Bank (lA) mirror leg (−₹48,345). Adding V4 and Skill changes the Nifty leg by only +₹190 and the Bank leg by −₹270 versus (lA)-only. **The merge does not create a new system; it inherits (lA)'s split: excellent on Nifty, deeply negative on the unvalidated Bank mirror.** Any future work on (lA) must treat Nifty (lA) and Bank mirror as separate systems — pooling them hides a +₹71,780 leg behind a −₹48,345 leg.

## Validation cross-checks (must travel with the numbers)

- V4 slice reproduces the known capped-v2 Jan–Oct V4 index exactly: 62 trades, 43.5%, +₹68,770 (Nifty 27 / +₹42,410, Bank 35 / +₹26,360).
- Skill slice reproduces the known Skill index exactly: 58 trades, 43.1%, +₹40,240 (Nifty 29 / +₹49,890, Bank 29 / −₹9,650).
- Dual slice computed inside this run matches the dual run's own Jan–Oct aggregate file exactly: 66 trades, 51.5%, −₹1,600 — so the dual Jan–Oct result (−₹1,600, not the October-only +₹46,975) is confirmed by an independent computation path.
- Room ratio is dead for (lA) candidates (rescan close below PDL → infinite room → 1.0), as in the dual report; ranking among (lA) candidates is decided by bias-strong then prospective target.

## Verdict — NOT adopted

**Triple V4+Skill+(lA) Jan–Oct: 74 trades, 47.3% green, +₹23,355, expectancy +₹316, max drawdown ₹97,220.** It fails the adoption bar on net (below V4 by ₹45,415 and below V5 by ₹41,025), on frequency (most trades of any index series for a worse result), and on progression (cumulative falls Jun–Sep). Win rate alone (47.3% > V4's 43.5%) does not pass X, which requires net + win rate + frequency together. The gain over the dual is V4 addition, not synergy. Previous best kept for index remains **V4 index as a separate series, paper only**. If (lA) is pursued further, the honest next step is Nifty (lA) alone (not pooled with its Bank mirror) on unseen months — not another pool.

## Triple capped trade list (74 trades, date order)

| Date | Symbol | Source | Setup | Dir | Exit | Net ₹ |
|---|---|---|---|---|---|---|
| 2026-01-09 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 6,070 |
| 2026-01-09 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 2,295 |
| 2026-01-12 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -6,130 |
| 2026-01-14 | NIFTY | V4 | setup4_reclaim | CE | stop | -2,785 |
| 2026-01-21 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 360 |
| 2026-01-21 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 9,280 |
| 2026-01-30 | NIFTY | Skill | or_breakout | CE | stop | -3,025 |
| 2026-02-02 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -10,655 |
| 2026-02-06 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 1,120 |
| 2026-02-11 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -12,850 |
| 2026-02-13 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -2,645 |
| 2026-02-24 | NIFTY | V4 | setup2_or_breakdown | PE | target | 7,350 |
| 2026-02-27 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -11,800 |
| 2026-03-06 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -1,375 |
| 2026-03-11 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 5,790 |
| 2026-03-11 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 2,420 |
| 2026-03-16 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 24,220 |
| 2026-03-16 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 8,940 |
| 2026-03-23 | BANKNIFTY | Skill | or_breakdown | PE | target | 25,440 |
| 2026-03-23 | NIFTY | Skill | or_breakdown | PE | target | 7,260 |
| 2026-03-30 | BANKNIFTY | Skill | or_breakdown | PE | stop | -10,520 |
| 2026-03-30 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -2,055 |
| 2026-04-01 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -23,515 |
| 2026-04-02 | NIFTY | Skill | or_breakdown | PE | stop | -2,115 |
| 2026-04-10 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -9,405 |
| 2026-04-13 | BANKNIFTY | Skill | or_breakout | CE | stop | -6,390 |
| 2026-04-13 | NIFTY | Skill | or_breakout | CE | target | 7,240 |
| 2026-04-24 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 21,820 |
| 2026-04-24 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 8,820 |
| 2026-04-28 | BANKNIFTY | V4 | setup2_or_breakdown | PE | target | 15,400 |
| 2026-04-30 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 440 |
| 2026-05-05 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 10,540 |
| 2026-05-05 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 5,040 |
| 2026-05-13 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -5,075 |
| 2026-05-14 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -18,995 |
| 2026-05-18 | BANKNIFTY | Skill | or_breakdown | PE | stop | -12,875 |
| 2026-05-18 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -3,000 |
| 2026-05-29 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | target | 15,660 |
| 2026-06-08 | NIFTY | Skill | or_breakout | CE | stop | -3,805 |
| 2026-06-09 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -3,915 |
| 2026-06-16 | BANKNIFTY | V4 | setup2_or_breakdown | PE | stop | -6,075 |
| 2026-06-24 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -8,625 |
| 2026-06-29 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -24,935 |
| 2026-06-29 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 2,100 |
| 2026-07-01 | BANKNIFTY | V4 | setup4_reclaim | CE | target | 15,680 |
| 2026-07-01 | NIFTY | V4 | setup4_reclaim | CE | target | 4,240 |
| 2026-07-08 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -14,995 |
| 2026-07-08 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 955 |
| 2026-07-13 | NIFTY | V4 | setup2_or_breakout | CE | stop | -1,660 |
| 2026-07-15 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -4,560 |
| 2026-07-22 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 6,320 |
| 2026-07-24 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -3,455 |
| 2026-07-30 | BANKNIFTY | V4 | setup2_or_breakdown | PE | stop | -7,825 |
| 2026-08-10 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -3,460 |
| 2026-08-12 | NIFTY | V4 | setup2_or_breakdown | PE | target | 6,250 |
| 2026-08-19 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -3,770 |
| 2026-08-19 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_green | 1,670 |
| 2026-08-25 | BANKNIFTY | V4 | setup4_reclaim | CE | stop | -7,455 |
| 2026-08-27 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 2,980 |
| 2026-08-31 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -10,180 |
| 2026-08-31 | NIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -3,515 |
| 2026-09-02 | BANKNIFTY | V4 | setup2_or_breakout | CE | stop | -4,900 |
| 2026-09-07 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 8,510 |
| 2026-09-08 | NIFTY | V4 | setup2_or_breakdown | PE | stop | -1,305 |
| 2026-09-29 | BANKNIFTY | Skill | or_breakdown | PE | stop | -5,600 |
| 2026-09-29 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 3,790 |
| 2026-10-01 | BANKNIFTY | V4 | setup4_reclaim | CE | target | 16,640 |
| 2026-10-07 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | day_loss | -7,475 |
| 2026-10-08 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 11,690 |
| 2026-10-13 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | stop | -3,730 |
| 2026-10-21 | BANKNIFTY | (lA) | la_pe_rescan_reentry | PE | target | 20,200 |
| 2026-10-23 | NIFTY | (lA) | la_pe_rescan_reentry | PE | target | 11,390 |
| 2026-10-26 | BANKNIFTY | V4 | setup3_bounce_rejection | PE | target | 10,520 |
| 2026-10-26 | NIFTY | V4 | setup4_reclaim | CE | stop | -8,635 |

## Files

- This report: `~/workspace/trading/triple_v4_skill_la_index_jan_oct_2026.md`
- Engine: `~/workspace/trading/triple_v4_skill_la_jan_oct.py` (triple-only outputs; it never writes merged_skill_la_summary_* files)
- Month JSONs: `~/workspace/trading/data/progressive/triple_v4_skill_la_summary_2026-01.json` … `-10.json`, aggregate `triple_v4_skill_la_summary_2026-jan-oct.json`
- Sources: `merged_skill_la_october.py`, `merged_skill_la_index_october_2026.md`, `progressive_capped_v2.py`, `jan_oct_2026_v4_and_skill.md`
