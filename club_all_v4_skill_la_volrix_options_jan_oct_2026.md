# CLUB-ALL BACKTEST — V4 + Skill + (lA) + Volrix OPTIONS, Nifty + Bank Nifty, Jan–Oct 2026

Paper only. No orders placed, no live trading, no live-trading recommendation.
**NOT adopted. NOT clean validation** — see verdict §7.
Interpretation stated so it can be corrected: club ALL previous index systems together, with Volrix represented by its OPTIONS translation, NOT its spot/futures proxy. This is a NEW club-all run, additional to the dual Skill+(lA) and triple V4+Skill+(lA) runs in progress — those were not stopped.

## 1. Frozen definitions — no re-tuning

### 1a. Intraday leg (triple definition, unchanged)
- Scope: NIFTY + BANKNIFTY only, NO stocks, Jan 2026 – 28 Oct 2026, 203 trading days (Oct = 1–28 only; 29 Oct excluded, still in progress that day and not in cache).
- Provisional cash rules (NOT Chandu's live options rules): 100 shares equivalent, ₹40/trade, signal-candle stop, 2× target, square-off 15:10, short paper-only, one intraday trade/instrument/day after dedup.
- Sources: V4 index candidates (capped-v2), Skill OR-only with V4-style filters (bias-aligned, room ≥200×scale, PD bound, rank 0), (lA) BN-confirmed rescan morning + band-filtered re-entry (scan-skip to 11:30, afternoon stop-on-first-fail to 15:05, PE only; Bank (lA) is the provisional mirror, roles swapped, Nifty confirms Bank, scale = Bank prev close / 55000, rank 1).
- Dedup same symbol+date: priority (lA) > V4 > Skill. Cap within each calendar month (as in capped-v2 Jan–Oct): prospective target net ≥₹500, rank setup_rank → bias-strong → room_ratio → prospective target, max 3 index/ISO week, max 1/symbol/week (attainable max 2/week with 2 symbols). Results gate NEUTRAL.
- Intraday leg was recomputed for this report from the triple script (frozen definition, `/tmp/club_triple.py` copy of `triple_v4_skill_la_jan_oct.py`, outputs in `~/workspace/trading/club_all/club_triple_summary_2026-*.json`) so it does not overwrite the triple run's own JSONs. Its Jan–Oct totals reproduce the triple run's own published benchmarks: V4 62 / +₹68,770, Skill 58 / +₹40,240, (lA) 47 / +₹23,435, dual 66 / −₹1,600 — all matching the dual Jan–Oct report, which is the reproduction check.

### 1b. Volrix options leg (standalone definitions, unchanged)
- LONG ATM monthly CALL, 1 lot, no stop, no target, same trigger/cooldown/skip as the Volrix code, entry 09:16 premium, exit 15:15 premium on the 5th session, expiry inside hold = exit at expiry with no roll.
- Nifty: nearest 50-point strike to previous-day spot close (from `volrix_nifty_large_down_rebound_options_backtest.md` / `volrix_options/options_trades.json`). Bank Nifty: nearest 100-point strike (from `volrix_banknifty_large_down_rebound_backtest.md` options section / `volrix_banknifty_options/options_trades.json`).
- **Only entries falling in Jan–Oct 2026 are in scope: 7 trades.** No pre-Oct-2024 option premiums are backfilled, and NO Volrix spot/futures-proxy trades are imported into this leg. The full standalone options universes are Nifty 5 trades (Oct 2024–Jul 2026) and Bank Nifty 8 trades (Oct 2024–Jul 2026); the 2026 subset below is the club-all leg.
- Volrix options trades are separate legs: **intraday trades ARE allowed during a Volrix hold** (default choice, stated here). Overlap is reported in §5, not hidden by blocking intraday trades.

## 2. Intraday leg (triple) — Jan–Oct 2026, capped

- Triple total: 74 trades, 35 green (47.3%), net ₹23,355.00, expectancy ₹315.61, DD ₹97,220.00
- Triple Nifty: 33 trades, 21 green (63.6%), net ₹71,970.00, expectancy ₹2,180.91, DD ₹11,880.00
- Triple Bank Nifty: 41 trades, 14 green (34.1%), net ₹-48,615.00, expectancy ₹-1,185.73, DD ₹106,750.00
- Inside triple by source: (lA) 41 trades, net +₹41,050.00; V4 23 trades, net −₹13,305.00; Skill 10 trades, net −₹4,390.00. (Source nets sum to the triple total; cap ranking, not source alone, decides which trades survive.)
- (lA) re-entry legs inside triple: 20 of the 41 (lA) trades have a re-entry leg (unlike October alone, where zero fired) — so Jan–Oct does test the re-entry rule.
- Frequency: 74 trades / 44 ISO weeks = 1.68/week (attainable max 2/week).

| Month | Triple trades | Green | Triple net ₹ | Nifty net ₹ | Bank Nifty net ₹ |
|---|---|---|---|---|---|
| 2026-01 | 7 | 57.1% | 6,065 | 5,765 | 300 |
| 2026-02 | 6 | 33.3% | -29,480 | 5,825 | -35,305 |
| 2026-03 | 9 | 66.7% | 60,120 | 16,565 | 43,555 |
| 2026-04 | 9 | 55.6% | 12,295 | 14,385 | -2,090 |
| 2026-05 | 7 | 42.9% | -8,705 | -3,035 | -5,670 |
| 2026-06 | 6 | 16.7% | -45,255 | -1,705 | -43,550 |
| 2026-07 | 9 | 44.4% | -5,300 | 9,855 | -15,155 |
| 2026-08 | 8 | 37.5% | -17,480 | 7,385 | -24,865 |
| 2026-09 | 5 | 40.0% | 495 | 2,485 | -1,990 |
| 2026-10 | 8 | 62.5% | 50,600 | 14,445 | 36,155 |

Comparison (same Jan–Oct window, capped, index only): V4 index 62 trades, 43.5%, +₹68,770; Skill index 58, 43.1%, +₹40,240; (lA)-only 47, 59.6%, +₹23,435; dual Skill+(lA) 66, 51.5%, −₹1,600; **triple 74, 47.3%, +₹23,355**. Triple beats dual by ₹24,955 but trails V4 by ₹45,415 while trading 12 more trades. Triple win rate (47.3%) is above V4's (43.5%), but net is below V4 — a higher win rate bought with more, smaller trades, not with better economics. The split is the story again: triple Nifty +₹71,970 vs triple Bank Nifty −₹48,615.

## 3. Volrix options leg — 2026 only (the club-all leg)

- **7 trades, 3 wins (42.9%), gross +₹15,065.50, charges ₹715.32, net +₹14,350.18, expectancy +₹2,050.03.** No max-drawdown is quoted for 7 trades as if it were a drawdown statistic — the worst single trade is Bank Nifty Mar 2026 (−₹43,880.18, expiry death, see below).
- Nifty options 2026: 3 trades, 1 win, gross +₹39,793.00, charges ₹359.28, net +₹39,433.72.
- Bank Nifty options 2026: 4 trades, 2 wins, gross −₹24,727.50, charges ₹356.04, net −₹25,083.54.

| Entry | Symbol | Strike / monthly expiry | Entry → exit premium | Spot move | Exit reason | Net ₹ |
|---|---|---|---|---|---|---|
| 2026-02-02 | BANKNIFTY | BANKNIFTY 58400 CE 24 FEB 26 (lot 30) | 1020.4 → 1981.0 | +1871.40 | 5th_session_close (2026-02-06) | 28,695.41 |
| 2026-03-09 | BANKNIFTY | BANKNIFTY 57800 CE 30 MAR 26 (lot 30) | 659.9 → 105.7 | -1973.30 | 5th_session_close (2026-03-13) | -16,685.30 |
| 2026-03-16 | NIFTY | NIFTY 23150 CE 30 MAR 26 (lot 65) | 493.75 → 348.15 | -39.80 | 5th_session_close (2026-03-20) | -9,548.99 |
| 2026-03-24 | BANKNIFTY | BANKNIFTY 51400 CE 30 MAR 26 (lot 30) | 1460.6 → 0.15 | -755.55 | expiry_close_no_roll (2026-03-30) | -43,880.18 |
| 2026-04-01 | NIFTY | NIFTY 22350 CE 28 APR 26 (lot 65) | 985.0 → 1770.15 | +1162.80 | 5th_session_close (2026-04-08) | 50,839.48 |
| 2026-07-09 | NIFTY | NIFTY 23900 CE 28 JUL 26 (lot 65) | 349.05 → 321.7 | +109.15 | 5th_session_close (2026-07-15) | -1,856.77 |
| 2026-07-09 | BANKNIFTY | BANKNIFTY 56700 CE 28 JUL 26 (lot 30) | 1192.85 → 1422.65 | +680.00 | 5th_session_close (2026-07-15) | 6,786.53 |

By month (options leg): Feb 2026 Bank +₹28,695.41 (1 trade); Mar 2026 −₹70,114.47 (3 trades: Nifty −₹9,548.99, Bank −₹16,685.30 and −₹43,880.18); Apr 2026 Nifty +₹50,839.48 (1); Jul 2026 +₹4,929.76 (2: Nifty −₹1,856.77, Bank +₹6,786.53).

Standalone context (not the club-all leg): Nifty options full testable window 5 trades, 2 wins, +₹76,917.61; Bank Nifty options full window 8 trades, 4 wins, +₹9,576.55. The 2026 subset is therefore most of the Bank window (4/8) and most of the Nifty window (3/5) — but still only 7 trades, and the 2026 Nifty leg is carried by a single Apr trade (+₹50,839.48, larger than the whole combined options net).
Flagged divergences: Nifty Jul 2026 — spot rose +109.15 but the call lost −₹1,856.77 (decay beat a small rebound). Bank Mar 2026 (entry 24 Mar) — the call died at expiry (0.15) under the no-roll rule for −₹43,880.18, while the Bank spot-proxy position for the same entry rolled and turned +₹15,492.45; excluding that one trade, Bank options 2026 would be +₹18,796.64 and the combined options leg +₹58,230.36 — still not a clean win, and the exclusion is disclosed, not adopted.

## 4. Combined total — LABELLED MIX, not a single-portfolio P&L

- Intraday triple leg: 74 trades, 47.3% green, +₹23,355.00 (cash-equivalent rupees: 100 shares × index points, ₹40/trade).
- Volrix options leg: 7 trades, 42.9% wins, +₹14,350.18 (option-premium rupees: premium change × lot, option charges).
- **Combined, labelled mix only: 81 trades, 38 wins (46.9%), +₹37,705.18.** This number mixes two different rupee units and two different risk units (100-share index equivalents vs 1 option lot) and must NOT be quoted as a portfolio return, a capital return, or a live-trading result. It is shown only because the club-all request asked for a combined figure.
- Per symbol, combined (same mixed-unit warning): Nifty intraday +₹71,970.00 + options +₹39,433.72 = +₹111,403.72 (36 trades); Bank Nifty intraday −₹48,615.00 + options −₹25,083.54 = −₹73,698.54 (45 trades). The combined total is Nifty-carried; Bank Nifty is negative on BOTH legs.

## 5. Overlap — intraday trades during Volrix holds

Intraday trades were allowed during Volrix holds (separate legs). 7 triple intraday trades fall inside a Volrix options hold for the same symbol:

| Intraday date | Symbol | Method / setup | Intraday net ₹ | Volrix hold |
|---|---|---|---|---|
| 2026-02-02 | BANKNIFTY | V4 setup3 bounce rejection PE | −₹10,655.00 | Bank Feb 2–6 (options +₹28,695.41) |
| 2026-03-11 | BANKNIFTY | (lA) PE rescan | +₹5,790.00 | Bank Mar 9–13 (options −₹16,685.30) |
| 2026-03-16 | NIFTY | (lA) PE rescan | +₹8,940.00 | Nifty Mar 16–20 (options −₹9,548.99) |
| 2026-03-30 | BANKNIFTY | Skill OR breakdown PE | −₹10,520.00 | Bank Mar 24–30 (options −₹43,880.18, expiry exit) |
| 2026-04-02 | NIFTY | Skill OR breakdown PE | −₹2,115.00 | Nifty Apr 1–8 (options +₹50,839.48) |
| 2026-07-13 | NIFTY | V4 setup2 OR breakout CE | −₹1,660.00 | Nifty Jul 9–15 (options −₹1,856.77) |
| 2026-07-15 | BANKNIFTY | V4 setup3 bounce rejection PE | −₹4,560.00 | Bank Jul 9–15 (options +₹6,786.53) |

Overlap intraday net: Nifty +₹5,165.00 (3 trades), Bank Nifty −₹19,945.00 (4 trades), total −₹14,780.00. Same-day entries (intraday trade on the Volrix entry day itself): Nifty 16 Mar and Bank 2 Feb only. No intraday trade was blocked by a Volrix hold, and no Volrix trade was blocked by an intraday trade — the legs are independent, so the combined total in §4 double-counts calendar exposure, not individual trades.

## 6. Full intraday (triple) trade list — Jan–Oct 2026

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

## 7. Verdict

- **Adding Volrix options does NOT improve the club-all on net + win rate + frequency together.** Intraday triple alone: 74 trades, 47.3%, +₹23,355. With Volrix options: 81 trades, 46.9% (mixed-unit), +₹37,705.18 (mixed-unit) — the net rises only because 7 option trades add ₹14,350.18, while the win rate falls and the trade count rises; the options leg itself is 3/7 wins, carried by one Apr Nifty trade, with Bank options negative. That is adding trades, not adding edge.
- **The club-all intraday leg also does not beat V4 index:** triple +₹23,355 (74 trades) vs V4 +₹68,770 (62 trades) — lower net, more trades, despite a higher win rate. Previous best kept for index remains V4 index as a separate series, paper only.
- **Jan–Oct is NOT clean validation:** October was already scored for the intraday definitions (and the triple October slice reproduces: 8 trades, 62.5%, +₹50,600, vs V4 October 7 / +₹51,825 and dual October 6 / +₹46,975). A frozen club-all candidate would still need unseen-month (November) validation, progressing on net + win rate + frequency together, before any adoption claim — and the mixed-unit combined total must never be the adoption metric; each leg would have to pass on its own unit basis.
- Caveats travelling with this report: Bank (lA) is a provisional mirror, not the original (lA); room ratio is dead among (lA) candidates (infinite room below PDL maps to 1.0); Volrix options 2026 is n=7 with no pre-Oct-2024 premiums; the Bank Mar 2026 expiry-death trade is a no-roll-rule artefact of the options translation, disclosed in §3, not smoothed away; intraday nets are point-scaled cash equivalents, not portfolio rupees.

## 8. Files

- This report: `~/workspace/trading/club_all_v4_skill_la_volrix_options_jan_oct_2026.md`
- Intraday (triple) recomputation for this report: `~/workspace/trading/club_all/club_triple_summary_2026-01.json` … `-10.json`, `club_triple_summary_2026-jan-oct.json`, run log `club_triple_run.log` (the triple run's own JSONs in `data/progressive/triple_*` were not overwritten).
- Volrix options source data (unchanged): `~/workspace/trading/volrix_options/options_trades.json`, `~/workspace/trading/volrix_banknifty_options/options_trades.json`.
