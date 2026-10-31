# NS1 — Second convicted signal per day — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.

## Common rules (shared by all NS families unless a family states otherwise)
- Spot source: cached 5-min spot (`~/workspace/trading/data/progressive/<INDEX>/spot_5m.csv`) +
  daily (`spot_daily.csv`). OR = bars with time < 09:30 (09:15, 09:20, 09:25 bars);
  ORH = max high, ORL = min low of those bars.
- PDH / PDC / PDL = previous trading day's daily high / close / low. Bias from previous day's
  close position: bearish < 35%, neutral 35–79%, bullish >= 80%.
- Scale = PDC / 55000 (V4 scale convention, carried for room thresholds stated in points).
- Spot exit (provisional): entry = next 5-min open after the signal/trigger bar; stop = trigger-bar
  low (CE) / high (PE); risk = |entry - stop|; if risk == 0, no trade; target = entry +/- 2 x risk;
  stop checked before target on every bar including the entry bar; square-off at the 15:10 close.
- Room rule (hard, never below 1.5x): room = distance from trigger close to the next PD level in
  direction (CE: smallest PD level > close, else infinity; PE: largest PD level < close, else
  infinity); room_ratio = room / risk; trade only if room_ratio >= 1.5.
- Full-target = target exit only. A square-off green, a partial, or a break-even leg is NEVER
  counted as a full target. Spot provisional net = direction points x 100 shares - Rs 40 per leg.
  This is NOT an options-lot profit and NOT a futures profit.
- Premium rule (October only): entry = open of the first 5-min option candle after the signal time;
  stop = entry - 50, target = entry + 90 option points (both CE and PE); square-off 15:10;
  cost Rs 220/trade assumed; 1 lot (Nifty 65, Bank 30, 2026); strike = ATM nearest 100 to entry spot;
  expiry monthly 2026-10-27 for 1-27 Oct, weekly 2026-11-03 for 28 Oct. Rows that cannot be
  fetched = NOT_COMPUTED, never spot-converted.
- A "break bar" (crossing) = a bar whose close is beyond a level while the previous bar's close
  was NOT beyond that same level. The 09:25 OR bar's close is inside [ORL, ORH] by construction,
  so a first close beyond OR is always a crossing.

## NS1 definition
Base first trade = Skill v2 (S1): first close beyond OR in 09:30-11:30; S1 blocks: (a) a 09:30 PE
signal bar is taken ONLY if its close < PDL; (b) CE on a bearish-bias day is blocked. Base exit
is the common spot exit above. If there is no S1 trade taken that day (blocked or no signal),
NS1 contributes nothing that day.

Second trade (at most one per day, cap 2 legs/day/index including the base leg):
- Eligibility: the base leg must have exited by TARGET or STOP, with exit-bar time <= 13:30.
  A base leg still open after 13:30, or exiting via square-off, yields NO second trade.
- Trigger: scan bars strictly after the base exit bar. The second signal is the first break bar
  (crossing, as defined above) beyond EITHER OR level: CE if close > ORH, PE if close < ORL.
  Signal time must be <= 14:30 (so an entry bar exists before square-off).
- Confirmation: none beyond the crossing itself plus the gates below (this is a second signal,
  not a re-entry on the same break: the crossing requirement guarantees price re-crossed the
  level after the base exit; a bar merely still beyond a level does NOT trigger).
- Bias rule: CE second leg blocked on a bearish-bias day. PE second leg has no bias block and
  no PDL gate (the 09:30 PDL rule is a morning S1 rule and does not apply to afternoon legs).
- Room rule: room_ratio >= 1.5 from the second-signal close, else no second trade.
- Stop / target / square-off: common rules, stop = second-signal bar low (CE) / high (PE),
  target = 2 x risk, square-off 15:10.
- Cap: 2 legs/day/index maximum (base + second). The second leg is scored as its own trade for
  frequency, full-target rate and net; the NS1 track total = base leg + second leg.

## What NS1 is NOT
- Not a cap loosening: it adds no trade on days without a qualifying base exit, and never forces
  a trade on a no-setup day. A day with no base trade, a square-off base exit, or a late base
  exit contributes zero NS1 second legs.
- Not Family C2 re-entry: C2-R1 re-scanned for the next SAME-direction signal after a morning
  STOP only. NS1 fires after a target OR a stop, in EITHER direction, and requires a fresh
  crossing of an OR level.
- Not a direct reclaim CE: the CE second leg is a fresh OR-high crossing after the base exit,
  not a retest-hold of a broken multi-day band (Setup 1 / Setup 4 mechanics are not used here).
