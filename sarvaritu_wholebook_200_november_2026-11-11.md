# SARVARITU — WHOLE BOOK × 200 STOCKS × NOVEMBER 2026 (scored 2026-11-11)

**This is a RETROSPECTIVE scoring (owner order 2026-11-11 17:49 IST) — not live forward evidence.**
Paper only, real money ₹0. Basis: **provisional per 100 shares**, ₹40/trade, square-off 15:10.
**Window: the seven November trading days — Mon 2026-11-02, Tue 03, Wed 04, Thu 05, Fri 06, Mon 09, Wed 11** (Tue 10 = Diwali-Balipratipada holiday). October data (from Sep 30) seeds prior-day reactions/levels only; October rows the machinery builds for seeding are not counted here.
**Universe: the Nifty 200 list as fetched 2026-11-11** (`wide200_universe_2026-11-11.csv`, official niftyindices ind_nifty200list.csv) — exactly **200 names**, applied backwards over seven trading days (constituent drift over one week is negligible; the caveat stands as stated).

## Construction — the whole book exactly as the 25-book runs it
The run uses the frozen November whole-book machinery itself — `stocks_sarvaritu_logger.py`'s `build_book` (the v2 engine book post-C24: **F4 + INV-LONG + INV-ABOVE (Cycle-22 form) + N4-V3 + P2F + P2F-R2 + R2-LOWBAND**, with the full v2 law: mechanism-scoped exclusions, C23 R2-LOWBAND×UP stand-aside, C24 INV-LONG×FLAT stand-aside, RF-1 weekend stand-aside, regime = REGIME-CLASSIFIER-1). The ONLY parameterisations are the universe (25 → 200), the data root, and the event calendar:
- **Data root** (`data/wide200_nov/`): per-symbol 5-min bars from the Sarvasetu bar store (Upstox bars 2026-09-30 → 2026-11-11, the same store the Sarvasetu run scored from); daily bars aggregated from each day's 5-min bars (the same aggregation the logger's own fetch layer uses). **NIFTY is copied wholesale from the live logger's own root** (`data/sarvaritu_fwd`), so the 50DMA regime series is identical to the live book's.
- **Event calendar:** the Sarvasetu merged machinery calendar (union of the live / ext / jan-oct calendars, live precedence — the same event input as the Sarvasetu November subset). Epoch lo = 2026-10-26, the logger's live epoch.

## Verification (run in the same session)
- **Fidelity:** an independent detailed rebuild (retaining entry/exit prices and reasons) reproduces the production `build_book` output **exactly** — same trade multiset, same nets, on all seven days.
- **Anchor:** restricting this run to the frozen 25 watchlist names reproduces the frozen paper log **trade-for-trade: 26 trades · +₹8,391.28, zero differences in either direction.** The machinery, calendar, bars, ADR (10-day lookback off the aggregated dailies) and regime labels therefore behave identically to the live book; the widening is the only change.
- **Coverage:** usable bars (≥50 5-min bars) for **200/200 names on all seven days (100%)**. No event-active name was unscorable on any day — **no NOT_COMPUTED trades, and all seven components were computed** (none had to be marked NOT_COMPUTED).

## Headline — 329 trades · net +₹180,269.75 · win rate 45.3%
**Read the concentration note before the headline:** the per-100-shares basis multiplies every percentage move by the share price, so high-priced names dominate rupee outcomes at any universe width. **The top-3 stocks (POWERINDIA +₹105,992.50 / 3 trades, DIXON +₹38,821.50 / 4, ABB +₹24,555.62 / 3) contribute 94.0% of the total; ex-top-3 the entire run is +₹10,900.13.** One day — Wed Nov 4, a market-wide gap-up day on which the INV-ABOVE pool fired on 89 names at once — contributes +₹131,641.46 (73%). The figure is exact on the stated basis and fully comparable to the two books below (same basis throughout); it is not a diversified 329-trade edge, and it is reported with its concentration attached, per the standing ex-top-3 discipline.

## Per-component (November, 200 names)
| Component | Trades | Net ₹ | Win % |
|---|---|---|---|
| F4 | 31 | −33,061.14 | 74.2 |
| INV-LONG | 29 | +48,745.80 | 62.1 |
| INV-ABOVE | 252 | +152,652.17 | 39.7 |
| N4-V3 | 7 | +5,783.45 | 57.1 |
| P2F | 5 | +3,989.77 | 60.0 |
| P2F-R2 | 3 | +2,811.55 | 33.3 |
| R2-LOWBAND | 2 | −651.85 | 0.0 |
| **Total** | **329** | **+180,269.75** | **45.3** |

- **INV-ABOVE is the width story:** 252 of the 329 trades. The inversion pool fires per-name on above-trend days; at 25 names it produced 9 November trades, at 200 names it produces 252 — Nov 4 alone: 89 trades / +₹131,739.11; Nov 11: 37 / +₹30,564.55; Nov 9: 10 / −₹12,182.60.
- **F4 loses at width despite a 74.2% win rate** — the same price-basis asymmetry as Sarvasetu's ULTRACEMCO: its single BOSCHLTD stop (₹48,080/share, −0.95%) costs −₹45,716.00, more than all its small wins combined.
- The intraday four (N4-V3 + P2F + P2F-R2 + R2-LOWBAND) at 200 width: **17 trades · +₹11,932.92**.

## Per-day
| Date | Regime | Trades | Net ₹ | Win % | Coverage |
|---|---|---|---|---|---|
| 2026-11-02 | DOWN | 61 | +15,384.42 | 67.2 | 200/200 (100%) |
| 2026-11-03 | FLAT | 32 | +10,060.90 | 43.8 | 200/200 (100%) |
| 2026-11-04 | FLAT | 92 | +131,641.46 | 50.0 | 200/200 (100%) |
| 2026-11-05 | FLAT | 42 | −5,869.47 | 40.5 | 200/200 (100%) |
| 2026-11-06 | FLAT | 51 | +6,405.69 | 29.4 | 200/200 (100%) |
| 2026-11-09 | UP | 12 | −8,743.90 | 25.0 | 200/200 (100%) |
| 2026-11-11 | UP | 39 | +31,390.65 | 33.3 | 200/200 (100%) |

Best trade: 2026-11-11 INV-ABOVE **POWERINDIA** LONG 10:20 @ 29,170.00 → 29,534.62 (target) **+₹36,422.50**
Worst trade: 2026-11-02 F4 **BOSCHLTD** LONG 10:05 @ 48,080.00 → 47,623.24 (stop) **−₹45,716.00**
Exit reasons: target 133 · stop 169 · square-off 27. (Sun Nov 8 Muhurat bars exist in the store; the machinery's day-context construction produces no Nov 8 rows — identical to the frozen log, which also carries none.)

## Construction notes — named, not hidden
- **N4 threshold:** this machinery (the November whole book's own builder, `n4_raw` in `stocks_engine_v2_build.py`) applies **|09:30 move| ≥ 1.0%**, entry at the 09:30 bar close (labelled 09:35), T150/S080. The adopted Variant C FREEZE text also reads ±1.0% admission; the **0.8%** figure on record (stocks RSI log, 2026-11-03, NATIONALUM) belongs to the adopted December-candidate axis, and the FREEZE's FLOOR-2 cap (no N4 LONG ≥ +3.0%) / FLOOR-4 (no HDFCBANK LONG) are carried-population features of the adopted book that the November logger machinery does not carry. This run is the November book's construction — the same one that produced comparison (a) — so the three-way read below is like-for-like.
- **INV-ABOVE form:** the November book runs the Cycle-22 construction (pool population, g1 above-trend gate, T125/S050 chains). The adopted Variant C carries the R2-26 anchored form (re-exited T150/S080) — a different, December-candidate form of the same sleeve, not used here, for the same like-for-like reason.
- **Scope of "seven":** the adopted book additionally carries the stack sleeves GAP-FADE, NE-REV-NU, REXP and INV-R3. They are not part of the November frozen book and not part of the owner's "seven strategies" framing for this run; they are excluded and named here rather than silently dropped.
- **Exclusions at width:** the v2 law's exclusions are name-scoped to the original 25 (e.g. F4's EXCL_DIR, INV base exclusions, the (comp, stock, dir) deletion list). They apply to those names wherever they sit in the 200; no new exclusions were invented for the other ~175 names — the constructions' generic filters (ADR ≥ 3.0, rounds, bands, regime gates) are what discipline the wider names.

## Three-way comparison — same November days, three separate books, NEVER added together
| Book | Trades | Net ₹ (provisional per 100 shares) |
|---|---|---|
| (a) Frozen SarvaRitu — 25 names × 7 components (its own paper log, re-summed and verified) | 26 | **+8,391.28** |
| (b) Sarvasetu — 1,081 names × 4 intraday components (Sarvasetu report) | 25 | **+4,604.01** |
| (c) **This run — 200 names × 7 components** | **329** | **+180,269.75** (ex-top-3: **+10,900.13**) |

The explicit read:
1. **What the EOD sleeves add at 200 width:** F4 + INV-LONG + INV-ABOVE together contribute **+₹168,336.83 over 312 trades** — versus the intraday four's +₹11,932.92 at the same width, and versus Sarvasetu's +₹4,604.01 for the intraday four at 1,081 width. In November, the sleeves Sarvasetu cannot run are where the wide-universe money was — overwhelmingly INV-ABOVE on the post-Diwali trend days.
2. **What the extra ~175 names add vs the 25:** +₹171,878.47 over 303 trades on the headline basis — but with 94% of the whole run concentrated in three high-priced names, the diversified read is the ex-top-3 line: **+₹10,900.13**, the same order of magnitude as the 25-book's +₹8,391.28. Width multiplies exposure to the pool's good days (Nov 4) exactly as much as it multiplies single-name price risk (BOSCHLTD).
3. All three books share the identical money basis; the differences are universe width and component scope only — (a) is reproduced inside (c) trade-for-trade on its 25 names (anchor check above).

## Caveats
- Retrospective scoring of a shadow configuration assembled 2026-11-11; not live forward evidence. The frozen November book's live record is comparison (a) and is untouched by this run — no frozen book, log, producer, or index file was modified; this run wrote only its own root (`data/wide200_nov/`), trades CSV, summary JSON and this report.
- Daily bars for the 200 are aggregated from the same days' 5-min bars (the logger fetch layer's own fallback aggregation); the anchor check confirms this reproduces the live book's inputs on the 25 names exactly for November.
- The per-100-shares basis is a provisional cash-translation unit, never a lot; rupee outcomes scale with share price by construction — see the concentration note.
