# NS6 — Afternoon session-range breakout on empty days (own idea) — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.
Common rules (OR, PD levels, bias, scale, spot exit, room >= 1.5, full-target, premium rule)
are exactly as in `index_options_newsetup_ns1_second_frozen.md`.

## NS6 definition
NS6 fires ONLY on days with NO Skill v2 (S1) trade taken in the morning (blocked or no morning
signal) — the same empty-day discipline as NS2, but with a different trigger level, so NS2 and
NS6 are alternative afternoon rescans, scored separately and never combined.

- Session range: day high = max high and day low = min low of the traded index's bars from
  09:15 through 13:00 inclusive. The range is fixed at 13:00; later bars do not extend it.
- Entry trigger: first bar with time > 13:00 and <= 14:30 whose close is beyond the session
  range — CE if close > session high, PE if close < session low.
- Confirmation (cross-confirmation, mandatory): the confirming index (other index) must have
  closed beyond its OWN session range (computed identically, 09:15-13:00) in the same direction
  on a bar >= 09:30 at or before the signal bar, same day. No confirmer session-range break
  by the signal bar = no trade.
- Bias rule: CE blocked on a bearish-bias day. PE has no bias block.
- Room rule: room_ratio >= 1.5 from the signal close to the next PD level in direction,
  else no trade.
- Stop / target / square-off: common rules (stop = signal-bar low/high, target = 2 x risk,
  square-off 15:10).
- Cap: at most one NS6 leg per day per index, only on no-morning-trade days. The NS6 track
  total is its own afternoon legs only (morning S1 legs are NOT included in the NS6 track —
  unlike NS2, whose track total includes the morning leg; this difference is stated so the
  two tracks are not compared as if they counted the same thing).

## What NS6 is NOT
- Not NS2 with a new name: NS2 triggers on the morning OR level; NS6 triggers on the full
  morning-to-13:00 session range, a strictly wider level that fewer days break.
- Not a forced afternoon trade: days where neither index breaks its session range, or where
  the confirmer does not confirm, are no-trade days under NS6.
