# Index OPTIONS — Skill-only tuning, 2026-10-30 — FROZEN before scoring

Paper only, no orders, no stocks, no other systems. Skill v2 (S1) only.
Window first: October 2026, 1–28 Oct, 18 trading days. Nifty and Bank separately,
never pooled. Scoring legs (all three together): premium net per 1 lot > 0 AND
premium full-target >= 50% AND frequency >= 5/week (trades / 18 * 5).
Nothing adopted on October/in-sample alone; November paper from Mon 2026-11-02
remains validation. Jan–Oct scored (spot first) only for a variant that passes
October on premiums.

## Base S1 (recomputed from cache, verified against the v2 CSV before variants)
- Source: ~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/spot_5m.csv +
  spot_daily.csv. OR = bars with time < 09:30 (09:15, 09:20, 09:25 bars);
  ORH = max high, ORL = min low of those bars.
- Raw signal = first 5-min close beyond OR (close > ORH = CE, close < ORL = PE)
  in window 09:30–11:30 inclusive. If no such close, no signal that day.
- PDH/PDC/PDL = previous trading day's daily high/close/low. Bias from previous
  day's close position cs = (close-low)/(high-low)*100: bearish cs < 35,
  neutral 35–79, bullish >= 80.
- S1 blocks: (a) a 09:30 PE signal is taken ONLY if its close < PDL; a 09:30 PE
  closing at/above PDL is blocked and the day ends (no later signal).
  (b) CE on a bearish-bias day (cs < 35) is blocked and the day ends.
  A blocked day contributes no trade. A non-09:30 PE has no PDL gate.
- Spot exit (provisional, points x 100 shares - Rs 40/leg, NOT an options profit):
  entry = next 5-min open after the signal bar; stop = signal-bar low (CE) /
  high (PE); risk = |entry - stop|; if risk = 0, no trade; target = entry +/-
  2 x risk; stop checked before target on every bar including the entry bar;
  square-off at the 15:10 bar close.
- Premium exit (options overlay, same as the October premium completion):
  strike = ATM nearest 100 to entry spot; expiry monthly 2026-10-27 for
  1–27 Oct, weekly 2026-11-03 for 28 Oct; entry premium = open of the first
  5-min option candle with time > spot signal time; stop = entry - 50 option
  points, target = entry + 90 option points, both CE and PE; stop checked
  before target on every bar including the entry bar; square-off 15:10 close;
  net per 1 lot = (exit - entry) x lot - Rs 220 assumed cost; lot Nifty 65 /
  Bank 30. Premium full-target = premium target exit only; a square-off green
  is NOT a full target. A variant trade whose contract-day premium file is not
  already cached is reported NOT_COMPUTED (never spot-converted); premium
  totals are shown both as computed-only and with the NOT_COMPUTED count.

## Variants — one change at a time vs base S1, nothing blended
- V1 P-LOW (09:30-PE fix, low-penetration): the 09:30 PE rule is REPLACED, not
  deleted: a 09:30 PE is taken iff its signal-bar LOW < PDL (the bar penetrated
  PDL intraday), regardless of its close. If low >= PDL, blocked, day ends.
  All other S1 rules unchanged.
- V2 P-2ND (09:30-PE fix, second-close): a 09:30 PE with close < PDL is taken
  as base. If its close >= PDL, it is NOT blocked outright: if the next bar
  (09:35) closes < PDL, the PE is taken with signal bar = 09:35, entry 09:40
  open, stop = 09:35 high. If 09:35 also closes >= PDL, blocked, day ends
  (no later scan). All other S1 rules unchanged.
- V3 CE-NOBLOCK: CE bearish block removed; a CE is taken on any bias day.
  The 09:30-PE rule is unchanged. (Diagnostic on the CE block only; the PE
  filter is not deleted in any variant.)
- V4 BIAS-WIDE (widened neutral, Family A spot result, now premium-scored):
  bearish cs < 25, neutral 25–84, bullish >= 85. CE blocked only if cs < 25.
  The 09:30-PE rule is unchanged. No other change.
- V5 OR30: OR = bars with time < 09:45 (09:15–09:40 bars); signal window
  09:45–11:30; S1 blocks adapted by analogy only: a PE signal on the FIRST
  signal bar (09:45) is taken only if its close < PDL, else blocked, day ends;
  later PE signals have no PDL gate; CE blocked on bearish days (cs < 35).
  This is distinct from Family B B6 (OR < 10:00, window 10:00–11:30), which
  was discarded on spot and is NOT re-run.
- V6 OR20: OR = bars with time < 09:25 (09:15, 09:20 bars); signal window
  09:25–11:30; S1 blocks adapted by analogy only: a PE signal on the first
  signal bar (09:25) is taken only if its close < PDL, else blocked, day ends;
  later PE signals have no PDL gate; CE blocked on bearish days (cs < 35).
- V7 R1-PREM (Family C C2-R1, spot keep, now premium-scored): base S1 trade
  plus, after a morning STOP only, one re-entry: next same-direction close
  beyond the same OR level after the stop bar, signal <= 14:30, entry next
  open, stop = re-signal high/low, target 2 x risk, room/risk >= 1.5 where
  room = distance from re-signal close to the next PD level in direction;
  if room/risk < 1.5, no re-entry. Day premium net = morning premium net +
  re-entry premium net (two Rs 220 costs); a day counts as full-target only
  if the day's premium net is a target leg? No — full-target is counted per
  LEG for frequency/FT in this report (legs, not days), and day-level FT is
  also shown. To keep it comparable with the base (legs = trades), R1 is
  scored leg-by-leg: legs = morning legs + re-entry legs.
- V8 R-REV (reversal re-entry, NEW): base S1 trade plus, after a morning STOP
  only, one re-entry in the OPPOSITE direction: first close beyond the
  opposite OR level after the stop bar, signal <= 14:30, entry next open,
  stop = re-signal high/low, target 2 x risk, room/risk >= 1.5 (same room
  definition as V7); if room/risk < 1.5, no re-entry. Scored leg-by-leg
  like V7. This is not C2-R1 (same direction) and not NS1 (NS1 fires after a
  target OR a stop, in either direction, on a fresh crossing, with exit
  <= 13:30 — V8 fires after a stop only, opposite direction only).
- V9 C3-PREM (Family C C3 pullback, spot keep for Bank only, now
  premium-scored): after the base signal, the direct entry is REPLACED by a
  pullback entry: wait for a later bar (strictly after the signal bar,
  <= 14:30) with CE low <= ORH and close > ORH, or PE high >= ORL and
  close < ORL; entry next open, stop = pullback-bar low/high, target
  2 x risk, room/risk >= 1.5 from the pullback close (room as in V7);
  no pullback bar or room < 1.5 = no trade that day. Direct reclaim CE is
  not re-introduced (the pullback bar must be strictly after the signal bar).
- V11 P-RESCAN (09:30-PE fix, PDL rescan — added after V1/V2 scored identical
  to base, before V11 scoring): a 09:30 PE with close >= PDL is NOT a day-end
  block. Scan bars 09:35–11:30 for the first close < PDL; if any scanned bar
  closes > ORH first, abort with no trade; if no close < PDL by 11:30, blocked.
  The rescan signal bar is that first close < PDL; entry next open, stop =
  rescan-bar high, target 2 x risk (spot) and the usual premium overlay.
  The PDL filter is RETAINED (a close below PDL is still required) — only its
  timing is relaxed from the 09:30 bar to any bar <= 11:30. A 09:30 PE with
  close < PDL is taken as base. All other S1 rules unchanged. This is not a
  deletion of the filter and not NS2 (afternoon rescan) or a V4 setup2 trade:
  it is the same Skill OR-breakdown day, confirmed by a PDL close.
- V10 PB-FALLBACK (pullback with direct fallback, NEW): after the base
  signal, wait for a pullback bar as in V9 up to 11:30; if one appears with
  room/risk >= 1.5, use the pullback entry; otherwise use the ORIGINAL direct
  entry (base entry/stop/target). No trade is lost for lack of a pullback;
  only the entry changes. Room for the fallback direct entry is not re-gated
  (base S1 has no room gate).

## Already-run families NOT re-run as new (read before scoring)
- Family A parameters (stop/target multiples, room thresholds as an S1
  post-filter, prospective filters, caps, bias bands spot): only V4 above
  carries a Family A result forward, and only to premium-score it.
- Family B indicators (EMA, RSI, ATR, extended OR B6): discarded / not tested
  (VWAP, volume — no volume in cache); B6 is not re-run.
- Family C: C1-O1 (PE-only confirmer), C2-R2, C4 second-close, C5 time gates:
  discarded on spot for Skill except C2-R1 and C3; only R1 (V7) and C3 (V9)
  are carried forward, to premium-score them. C4 is NOT the same as V2:
  C4 required a second close on EVERY signal; V2 applies a second close
  only to the blocked 09:30 PE case.
- Family D candles (1-min audit, 3-min subset, 15-min): 5-min kept; no grid
  change in this run.
- NS1–NS6: separate families, not Skill variants; NS1 second-signal legs are
  not re-counted as Skill re-entries (V7/V8 differ by construction, above).
- Room is never loosened below 1.5x for any NEW entry created by a variant
  (V7, V8, V9, V10 pullback leg). Base S1 trades carry no room gate, as in
  the v2 definition. No forced trades: a variant that finds no signal, no
  pullback, or no qualifying re-entry on a day contributes nothing that day.
