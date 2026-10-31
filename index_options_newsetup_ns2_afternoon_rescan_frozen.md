# NS2 — Afternoon rescan extension for Skill OR signals (11:30 -> 15:00) with cross-confirmation — FROZEN before scoring (2026-10-30)

Paper only, no orders. Index OPTIONS only. Nifty and Bank Nifty separately, never pooled.
Window: Jan–Oct 2026 spot first, then October 2026 premiums. Nothing adopted on in-sample alone;
November 2026 paper from 2026-11-02 remains validation.
Common rules (OR, PD levels, bias, scale, spot exit, room >= 1.5, full-target, premium rule,
break-bar definition) are exactly as in `index_options_newsetup_ns1_second_frozen.md` and are
not redefined here except where NS2 states otherwise.

## NS2 definition
Track = Skill v2 (S1) base (morning, 09:30-11:30, S1 blocks as in NS1) PLUS an afternoon leg
that fires ONLY on days with NO S1 trade taken (blocked or no morning signal). On a day where
a morning S1 trade was taken, NS2 adds nothing — the afternoon leg is a rescan of empty days,
not a second trade on traded days (that is NS1's job, scored separately).

Afternoon leg:
- Entry trigger: first close beyond OR in the afternoon window — signal bar time > 11:30 and
  <= 14:30 (so an entry bar exists before square-off). CE if close > ORH, PE if close < ORL.
- Confirmation (cross-confirmation, mandatory): the confirming index (Bank confirms Nifty,
  Nifty confirms Bank) must have closed beyond its own same-direction OR level on a bar with
  time >= 09:30 at or before the signal bar, same day. Confirmer OR is computed identically
  (its own 09:15-09:25 bars). No confirmer break by the signal bar = no trade, however clean
  the traded index's break looks.
- Bias rule: CE afternoon leg blocked on a bearish-bias day. PE afternoon leg has no bias block
  and no PDL gate (the 09:30 PDL rule is a morning S1 rule).
- Room rule: room_ratio >= 1.5 from the afternoon-signal close, else no trade.
- Stop / target / square-off: common rules (stop = signal-bar low/high, target = 2 x risk,
  square-off 15:10).
- Cap: at most one afternoon leg per day per index, and only on no-morning-trade days. The NS2
  track total = morning S1 leg (if any) + afternoon leg (if any); a day contributes at most
  one leg under NS2.

## What NS2 is NOT
- Not Family C5 PM windows: C5 only filtered existing base trades by signal time and found
  exactly one PM base trade in October. NS2 GENERATES new afternoon signals on days the morning
  system was empty, with a cross-confirmation gate C5 did not have.
- Not Family B6 extended OR: B6 redefined OR itself (bars < 10:00) and re-ran the morning signal.
  NS2 keeps the standard 09:15-09:25 OR and only extends the signal window, with cross-confirmation.
- Not a stacking rule: it never adds a second leg to a day that already traded in the morning.
