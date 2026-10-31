# Index OPTIONS — Family C: APPROACHES + ENTRY TIMES — October 2026
Paper only, no orders. Frozen definitions: [index_options_familyC_frozen_oct30.md](sandbox://workspace/trading/index_options_familyC_frozen_oct30.md)
Window: 1–28 Oct 2026, 18 trading days. Nifty and Bank separately, never pooled.
Unit: spot provisional = points × 100 shares − ₹40/leg. NOT an options-lot profit, NOT a futures profit.
Premiums NOT_COMPUTED (cache is spot only; no browser fetch was run in this subagent run).
Frequency = trades ÷ 18 × 5. Full-target = exit_reason target AND day net > 0 (a re-entry leg can hit
its own target while the day still nets negative — those do NOT count as full targets).
Nothing here is adopted: no variant reaches 5/week on any track (best 2.50/week, Skill v2 base/R1 Bank).

## Base reconciliation (recomputed from cache, before variants)
- V4 uncapped: Nifty 4 trades +₹2,725; Bank 5 trades +₹67,690 (total 9, +₹70,415).
- V5-v2 = V4 minus the 1/week cap-outs: Nifty 28 Oct and Bank 23 Oct removed → Nifty 3 +₹8,195;
  Bank 4 +₹43,630 (total 7, +₹51,825 — exactly the v2 report). V4 ≠ V5 in October; do not merge them.
- Skill v2 (S1): Nifty 8 +₹8,420; Bank 9 +₹8,675 — exactly the v2 report (15 raw signals blocked).
- (lA) v2 (L1): Nifty 3 +₹28,020; Bank 4 +₹28,275 — exactly the v2 report (all 7 morning replays match).
- Volrix v2: 0 triggers either index → 0 trades in every family below, by design.

## BASE table
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

## C1 — O1 cross-confirmation persistence (PE only; CE kept unchanged)
Filtered = PE trades removed because the confirmer was NOT below its OR low on signal AND entry bars.
| Track | Base → O1 trades | Base net → O1 net | Win | Full-target | Filtered out (losers / winners killed) | Verdict |
|---|---|---|---|---|---|---|
| V4 Nifty | 4 → 2 | +₹2,725 → +₹2,755 | 50% → 50% | 50% → 50% | 1 loss (−₹5,470, 28 Oct) / 1 win (+₹5,440, 8 Oct) | DISCARD — neutral (+₹30), kills a winner for a loser |
| V4 Bank | 5 → 3 | +₹67,690 → +₹60,900 | 80% → 100% | 80% → 100% | 1 loss (−₹3,730, 13 Oct) / 1 win (+₹10,520, 26 Oct) | DISCARD — net falls ₹6,790; win rate up only by deletion |
| Skill v2 Nifty | 8 → 4 | +₹8,420 → +₹15,780 | 37.5% → 50% | 25% → 25% | 3 losses / 1 win (+₹5,440, 8 Oct PE) | DISCARD — FT flat, kills the only PE winner; leaves a CE-only track |
| Skill v2 Bank | 9 → 7 | +₹8,675 → +₹20,790 | 33.3% → 42.9% | 33.3% → 42.9% | 2 losses (−₹7,475, 7 Oct; −₹4,640, 12 Oct) / 0 winners | KEEP as candidate (Oct only) — cleanest O1 track; still 1.94/wk, needs Nov paper |
| (lA) v2 Nifty | 3 → 2 | +₹28,020 → +₹16,330 | 100% → 100% | 100% → 100% | 0 losses / 1 win (+₹11,690, 8 Oct) | DISCARD — filters a winner, no loser; fails O1's own leg |
| (lA) v2 Bank | 4 → 3 | +₹28,275 → +₹35,750 | 50% → 66.7% | 50% → 66.7% | 1 loss (−₹7,475, 7 Oct F1) / 0 winners; 8 Oct L1 loser (−₹8,510) KEPT | KEEP as candidate (Oct only) — filters F1 but NOT the 8 Oct L1 loser; 0.83/wk |
| V5-v2 Nifty | 3 → 2 | +₹8,195 → +₹2,755 | 66.7% → 50% | 66.7% → 50% | 0 losses / 1 win (+₹5,440, 8 Oct) | DISCARD — kills a winner only |
| V5-v2 Bank | 4 → 2 | +₹43,630 → +₹36,840 | 75% → 100% | 75% → 100% | 1 loss (−₹3,730) / 1 win (+₹10,520, 26 Oct) | DISCARD — net falls ₹6,790 |
| Volrix either | 0 → 0 | ₹0 | — | — | — | No effect |

## C2 — Re-entry variants (after a morning STOP only; day net = morning + re-entry, 2× ₹40)
R1 = next same-direction signal, room/risk ≥1.5. R2 = R1 + second-close confirmation on the re-entry.
| Track | R1 day-count (net, win, FT) | R1 re-entries fired | R2 day-count (net, win, FT) | Verdict |
|---|---|---|---|---|
| V4 Nifty | 4, +₹5,795, 50%, 50% | 1: 26 Oct CE −₹8,635 + ₹3,070 = −₹5,565 (day still red) | 4, +₹800, 50%, 50% | DISCARD both — R1 improves net only, day stays red; R2 worse |
| V4 Bank | 5, +₹67,690, 80%, 80% (unchanged) | 0 (13 Oct stop had no qualifying re-signal) | unchanged | DISCARD — no effect |
| Skill v2 Nifty | 8, +₹16,000, 62.5%, 50% | 2, both rescued: 5 Oct −₹2,220→+₹270; 12 Oct −₹4,605→+₹485 | 8, +₹7,485, 37.5%, 25% | R1 KEEP as best for this track (Oct only); R2 DISCARD — all 3 R2 legs lose or shrink |
| Skill v2 Bank | 9, +₹31,320, 55.6%, 55.6% | 3: 6 Oct worsened −₹1,435→−₹4,480; 8 Oct rescued −₹11,070→+₹1,600; 12 Oct rescued −₹4,640→+₹8,380 | 9, −₹7,675, 33.3%, 33.3% | R1 KEEP as best for this track (Oct only); R2 DISCARD — turns the track negative |
| (lA) v2 Nifty | 3, +₹28,020, 100%, 100% (unchanged) | 0 (no stop days) | unchanged | DISCARD — no effect |
| (lA) v2 Bank | 4, +₹40,160, 75%, 50% | 1: 8 Oct −₹8,510 + ₹11,885 = +₹3,375 via square-off (not a target) | 4, +₹36,435, 50%, 50% | R1 KEEP as weak candidate (win+net up, FT flat; rescue is square-off green, not target); R2 DISCARD (day −₹350) |
| V5-v2 Nifty | 3, +₹11,265, 66.7%, 66.7% | 1: same 26 Oct rescue-as-above, day still red | 3, +₹6,270, 66.7%, 66.7% | DISCARD both — net-only improvement, no new green day |
| V5-v2 Bank | 4, +₹43,630, 75%, 75% (unchanged) | 0 | unchanged | DISCARD — no effect |
| Volrix either | 0 | — | 0 | No effect |

## C3 — Pullback entries (dip to OR level + close back; no pullback = no trade; direct reclaim CE NOT re-introduced)
| Track | Trades | Net prov. | Win | Full-target | /wk | No-pullback days | Verdict |
|---|---|---|---|---|---|---|---|
| V4 Nifty | 3 | +₹1,770 | 2/3 (66.7%) | 2 (66.7%) | 0.83 | 23 Oct (base winner +₹11,390 lost) | DISCARD — win/FT up, net down |
| V4 Bank | 1 | +₹7,420 | 1/1 (100%) | 1 (100%) | 0.28 | 13, 21, 23, 26 Oct | DISCARD — frequency destroyed, net collapses |
| Skill v2 Nifty | 5 | +₹4,915 | 3/5 (60%) | 3 (60%) | 1.39 | 5, 7, 27 Oct | DISCARD — win/FT up, net down (26 Oct square-off +₹16,550 becomes +₹2,730) |
| Skill v2 Bank | 7 | +₹21,460 | 4/7 (57.1%) | 4 (57.1%) | 1.94 | 7, 23 Oct | KEEP as best for this track (Oct only) — net, win and FT all up |
| (lA) v2 Nifty | 0 | ₹0 | — | — | 0 | all 3 days | DISCARD — zero trades; (lA) breakdowns never rally back to OR low and close below it again |
| (lA) v2 Bank | 0 | ₹0 | — | — | 0 | all 4 days | DISCARD — zero trades, same reason |
| V5-v2 Nifty | 2 | +₹950 | 1/2 (50%) | 1 (50%) | 0.56 | 23 Oct | DISCARD — net down |
| V5-v2 Bank | 1 | +₹7,420 | 1/1 (100%) | 1 (100%) | 0.28 | 13, 21, 26 Oct | DISCARD — frequency destroyed |
| Volrix either | 0 | ₹0 | — | — | 0 | — | No effect |

## C4 — Second-close variants (C4a: stop from second bar; C4b: stop from original signal bar)
| Track | C4a (trades, net, win, FT) | C4b (trades, net, win, FT) | Verdict |
|---|---|---|---|
| V4 Nifty | 4, +₹7,170, 50%, 50% | 4, −₹16,090, 25%, 25% | DISCARD both — C4a net-only gain by shrinking winners (8 Oct +₹5,440→−₹375 stop; 23 Oct +₹11,390→+₹4,650); C4b deeply negative |
| V4 Bank | 3, +₹30,665, 66.7%, 66.7% | 2, +₹52,775, 100%, 50% | DISCARD both — C4a net down ₹37k; C4b net down, FT down, 2 trades deleted |
| Skill v2 Nifty | 4, −₹11,570, 0%, 0% | 4, +₹9,535, 75%, 75% | C4a DISCARD (destroys the track); C4b KEEP as candidate (Oct only) — all metrics up, but net gain only +₹1,115 and frequency halved |
| Skill v2 Bank | 4, −₹9,420, 25%, 25% | 3, +₹1,265, 33.3%, 33.3% | DISCARD both — both negative vs base on net |
| (lA) v2 Nifty | 3, +₹2,085, 33.3%, 33.3% | 3, +₹7,515, 66.7%, 66.7% | DISCARD both — C4a destroys 3/3 targets; C4b net down ₹20,505 |
| (lA) v2 Bank | 2, +₹36,290, 100%, 100% | 2, +₹52,775, 100%, 50% | C4a KEEP as candidate (Oct only, deletion warning: both losers fail second close, kept winners re-timed — 21 Oct shrinks +₹20,200→+₹11,300); C4b DISCARD (FT flat at 50%, 23 Oct win is square-off not target) |
| V5-v2 Nifty | 3, +₹7,785, 66.7%, 66.7% | 3, −₹10,075, 33.3%, 33.3% | DISCARD both — C4a net down slightly; C4b negative |
| V5-v2 Bank | 2, +₹5,675, 50%, 50% | 1, +₹31,540, 100%, 100% | DISCARD both — C4a net collapses; C4b is a single trade, not a system |
| Volrix either | 0 | 0 | No effect |

## C5 — Time-gated entries (signal time; cumulative gates; PM windows standalone)
Net (trades) per gate. Bold = best gate per track; no gate reaches 5/week anywhere.
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
Verdict C5: DISCARD every gate as a standalone system. Early gates (≤09:30–09:45) are negative or
single-trade for Skill and empty for V4/(lA) — morning-only trading fails in October. ≤10:30 equals
base for V4 Nifty, Skill Nifty and V5 Nifty (all their signals are already ≤10:30), so it is not a
gain. ≤10:30 on Skill Bank TURNS the track negative by deleting its biggest winner (5 Oct +₹25,690,
signal 10:50) while keeping the losers — Skill Bank winners are late, not early. PM windows contain
exactly one base trade in all of October ((lA) Bank 13:15 L1 loser −₹8,510); PM2 is empty everywhere.
(lA) is inherently a late-signal system (signals 09:35–13:15, mostly after 10:00), so early gates
delete it by construction.

## Keeps (October only, none adopted — all still fail 5/week, all need November paper frozen)
- C1-O1: Skill Bank, (lA) Bank.
- C2-R1: Skill Nifty, Skill Bank, (lA) Bank (weak — FT flat, rescue is square-off).
- C3-pullback: Skill Bank only.
- C4a: (lA) Bank only (deletion warning). C4b: Skill Nifty only.
- C5: none.
Discards of note: O1 on (lA) Nifty (kills its only October winner class — the 8 Oct target); R2
everywhere (Skill Bank goes negative); pullback on (lA) both (0 trades); C4a on Skill both and
(lA) Nifty (destroys targets); every early time gate; PM windows (one loser total).
Next family (not run here): combine NOTHING yet — keeps above are separate per track and must each
survive November paper alone before any combination is scored, to avoid stacking October-fitted filters.
