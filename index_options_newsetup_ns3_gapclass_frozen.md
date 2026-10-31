# NS3 — OR-width / gap-class specific setups — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.
Common rules (OR, PD levels, bias, scale, spot exit, room >= 1.5, full-target, premium rule)
are exactly as in `index_options_newsetup_ns1_second_frozen.md`.

## Day classification (frozen thresholds, computed before any signal scan)
- Gap % = (day open - PDC) / PDC x 100, where day open = 09:15 bar open.
- Gap-up day: gap % >= +0.25%. Gap-down day: gap % <= -0.25%. Otherwise flat day.
- OR width % = (ORH - ORL) / PDC x 100. Narrow OR: width % < 0.35%. Wide OR: width % >= 0.35%.
- The three day types are mutually exclusive; exactly one NS3 setup applies per day.

## NS3 setups (one trade per day per index maximum; first qualifying signal wins)
- NS3-GU (gap-up day, PE only): first bar with time 09:30-13:30 whose close < ORL AND close < PDC
  (gap-fill breakdown: price must break the OR low AND fall back below the prior close).
- NS3-GD (gap-down day, first qualifying signal wins):
  - CE: first bar 09:30-13:30 with close > ORH AND the confirming index (other index) has closed
    above its own ORH on a bar >= 09:30 at or before this bar (cross-confirmation mandatory
    for the CE leg). This is a cross-confirmed OR breakout, NOT a direct reclaim: it requires
    the second index to break too, and it uses no multi-day band, no retest-hold, and no
    pullback-to-level entry (Setup 1 / Setup 4 mechanics are not used).
  - PE: first bar 09:30-13:30 with close < ORL (gap-down continuation breakdown).
  Whichever leg's condition is met first on the day is the day's signal; the other leg is
  then closed for the day.
- NS3-FLAT (flat day, narrow OR only): first bar 09:30-13:30 with close beyond OR in either
  direction (CE if close > ORH, PE if close < ORL). A flat day with a WIDE OR (>= 0.35%) gets
  NO NS3 trade — wide flat ranges are explicitly no-trade days under NS3, not forced trades.

## Gates applying to every NS3 leg
- Bias rule: CE legs blocked on a bearish-bias day. PE legs have no bias block.
- Room rule: room_ratio >= 1.5 from the signal close, else no trade (the day is then a no-trade
  day under NS3; no later signal is sought after a room failure — the first qualifying signal
  is the day's only candidate).
- Stop / target / square-off: common rules (stop = signal-bar low/high, target = 2 x risk,
  square-off 15:10).
- Cap: 1 trade/day/index under NS3. NS3 is scored as a standalone track (its own trades only),
  not added to Skill/V4/(lA) totals.

## What NS3 is NOT
- Not a filter loosening: gap-up days cannot take CE, flat-wide days cannot trade at all, and
  the gap-down CE leg carries an extra cross-confirmation gate that base Skill does not have.
- Not Family C time gates or Family A bias bands: the day classification is a gap/width regime
  split decided at the open, not a signal-time filter or a bias-threshold change.
