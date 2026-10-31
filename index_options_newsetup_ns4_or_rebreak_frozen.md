# NS4 — Pullback-inside then cross-confirmed OR re-break — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.
Common rules (OR, PD levels, bias, scale, spot exit, room >= 1.5, full-target, premium rule,
break-bar definition) are exactly as in `index_options_newsetup_ns1_second_frozen.md`.

## NS4 definition (three steps, all required, in order)
- Step 1 — First break: the first bar with time 09:30-13:30 whose close is beyond OR
  (CE-side: close > ORH; PE-side: close < ORL). The side of this first break fixes the
  direction for the rest of the day; the opposite side is closed for the day.
- Step 2 — Pullback-inside: a LATER bar (strictly after the Step 1 bar) whose close is back
  INSIDE the OR (ORL <= close <= ORH). A bar that merely wicks inside without closing inside
  does NOT satisfy Step 2. If no inside close occurs, there is no NS4 trade that day.
- Step 3 — Re-break (the NS4 signal): the first LATER bar (after the Step 2 bar, time <= 14:30)
  whose close is beyond the SAME OR level as Step 1 (CE: close > ORH; PE: close < ORL) AND
  that is a break bar (crossing: previous bar's close was not beyond that level) AND that
  carries cross-confirmation: the confirming index (other index) has closed beyond its own
  same-direction OR level on a bar >= 09:30 at or before the re-break bar, same day.
  Entry = next 5-min open after the re-break bar.

## Gates
- Bias rule: CE re-break blocked on a bearish-bias day. PE re-break has no bias block.
- Room rule: room_ratio >= 1.5 from the re-break close, else no trade.
- Stop / target / square-off: common rules (stop = re-break-bar low/high, target = 2 x risk,
  square-off 15:10).
- Cap: 1 trade/day/index under NS4. NS4 is scored as a standalone track.

## What NS4 is NOT (stated explicitly so it cannot be mistaken for a silent re-introduction)
- NOT Family C3 pullback: C3 entered ON the pullback bar itself (dip touches the OR level and
  closes back beyond it), with no intervening inside close and no cross-confirmation. NS4
  requires a full close back INSIDE the OR first, then a FRESH break bar, plus confirmer break.
- NOT Setup 4 / direct reclaim CE: Setup 4 is a multi-day ceiling breakout plus retest-hold of
  a broken band, or a direct reclaim close on a gap-down day. NS4 uses only the day's own OR,
  requires an inside close and a second break, and requires the second index to break too.
  A CE leg that fails any of those conditions is not taken.
- NOT a trade on a day with no setup: days with no first break, no inside close, or no
  confirmed re-break are no-trade days under NS4.
