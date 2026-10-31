# NS5 — Second index-leg setups (cross-index legs, scored separately, never blended) — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled, and
the two NS5 sub-tracks below are NEVER added together or to any base track. Each sub-track is
scored on its own per index.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.
Common rules (OR, PD levels, bias, scale, spot exit, room >= 1.5, full-target, premium rule)
are exactly as in `index_options_newsetup_ns1_second_frozen.md`.

## NS5a — (lA)-style rescan applied to Skill signals
Idea: a Skill OR-break signal counts only when the confirming index has already broken the
same way, in the (lA) confirmer-break order (confirmer first, traded index rescans after it).
- Confirmer break: the confirming index (other index) closes beyond its same-direction OR level
  (CE: > its ORH; PE: < its ORL) on a bar >= 09:30 with time <= 11:30. No confirmer break by
  11:30 = no NS5a trade that day, whatever the traded index does.
- Rescan signal: the first bar of the traded index at or after the confirmer-break bar, with
  time <= 13:30, whose close is beyond its own OR in the same direction (CE: > ORH; PE: < ORL).
  If the traded index's first OR break preceded the confirmer break, it does NOT count; only a
  close beyond OR at/after the confirmer break counts (the rescan). If no such bar exists by
  13:30, no trade.
- S1 blocks apply to the rescan bar: CE blocked on a bearish-bias day; a rescan bar at 09:30
  for PE is taken only if its close < PDL (in practice a rescan at/after a confirmer break
  rarely sits on the 09:30 bar, but the rule is kept, not waived).
- Room rule: room_ratio >= 1.5 from the rescan close, else no trade.
- Stop / target / square-off: common rules (stop = rescan-bar low/high, target = 2 x risk,
  square-off 15:10). Cap: 1 trade/day/index under NS5a.

## NS5b — CE mirror of the (lA) rescan (the "vice versa" leg)
The (lA) base is PE-only. NS5b mirrors its mechanics to the CE side; it is a separate setup,
not an addition to (lA) totals and not a blend with NS5a.
- Confirmer break: the confirming index closes ABOVE its own ORH on a bar >= 09:30 with
  time <= 11:30. No confirmer OR-high break by 11:30 = no NS5b trade that day.
- Rescan signal: the first bar of the traded index at or after the confirmer-break bar, with
  time <= 13:30, whose close > its own ORH AND close > PDH (prior-day high — a stronger level
  than the OR high alone). A close above ORH but at/below PDH does NOT qualify.
- Bias rule: CE blocked on a bearish-bias day (so NS5b effectively trades on neutral/bullish days).
- Room rule: room_ratio >= 1.5 from the rescan close, where room is measured to the next PD level
  above the close; if no PD level sits above the close (common, since the close already exceeds
  PDH), room = infinity and the room gate passes on that leg — stated, not hidden.
- Stop / target / square-off: common rules (stop = rescan-bar low, target = 2 x risk,
  square-off 15:10). Cap: 1 trade/day/index under NS5b. CE only; there is no NS5b PE leg
  (the PE counterpart already exists as (lA) base).

## What NS5 is NOT
- Not a blend: NS5a and NS5b trades are never summed into one "NS5 total", and neither is
  added to Skill or (lA) base totals in scoring. Any combined figure in the report is labelled
  as a cross-check only.
- Not direct reclaim CE: NS5b's CE requires a confirmer OR-high break AND a close above PDH,
  not a bare OR-high reclaim close, and NS5a's CE requires the confirmer to break first.
