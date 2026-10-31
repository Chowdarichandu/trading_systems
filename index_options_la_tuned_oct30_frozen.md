# (lA) tuning, 2026-10-30 — FROZEN before scoring

Paper only, no orders, no stocks, no other systems. Index OPTIONS only, (lA) only.
Nifty and Bank Nifty separately, never pooled. October 2026 first (1–28 Oct, 18 trading days
in the spot cache); Jan–Oct only if a variant passes October (see working rule below).
Nothing adopted on October/in-sample alone; November paper from Mon 2026-11-02 remains validation.

## Base (lA) v2 L1 — unchanged except the single variant knob
- PE only. Confirmer = the other index. Confirmer break bt = first bar 09:30–11:30 whose close
  is below the confirmer's own OR low (OR = bars with time < 09:30; ORL = min low, ORH = max high).
  "Broke before 11:30" is strict: bt < 11:30.
- Base rescan cutoff: bt < 11:30 → 13:30, else 11:30.
- Rescan signal: first bar at/after bt, at/before cutoff, with close < own ORL AND close < own PDL,
  OR width ≤ 360×scale, room ≥ 200×scale, where room = signal close − max PD level below close
  (∞ if no PD level below), scale = prev-day close / 55000, PD = prev trading day's daily levels.
- Morning exit (spot): entry = next 5-min bar open after signal; stop = signal-bar high;
  risk = stop − entry; target = entry − 2×risk; stop checked before target on every bar including
  the entry bar; square-off at the 15:10 close. Spot provisional = points × 100 shares − ₹40/leg.
  NOT an options-lot profit.
- Base re-entry (scan_reentry "lA"): only after a morning STOP; scan bars after the stop bar,
  time ≤ 15:05; candidate = close < own ORL; entry = next bar open; stop = candidate high;
  risk = stop − entry; band = 10 ≤ risk ≤ morning risk. Morning candidate (≤ 11:30) failing the
  band is SKIPPED and scanning continues. Afternoon candidate (> 11:30) failing the band ENDS
  the scan (stop-on-first-fail). At most one re-entry per day; replay as for the morning leg.
- Base October check (must reproduce before variant scoring): Nifty 3 morning legs
  (8 Oct 11:25, 21 Oct 11:35, 23 Oct 10:05), Bank 4 morning legs (7 Oct 09:35, 8 Oct 13:15,
  21 Oct 11:15, 23 Oct 09:55); base re-entry fires on no October day; spot nets Nifty +₹28,020,
  Bank +₹28,275 (morning legs); premium nets Nifty +₹6,678.50, Bank +₹1,520.00 per 1 lot.

## Room floor for NEW entries (task floor + Family C precedent)
Any leg CREATED by a variant (a later rescan signal, a loosened-width signal, a re-entry leg
under RB/S) must also satisfy room_ratio = room / risk ≥ 1.5, where room is measured from the
leg's signal close to the next PD level in direction (PE: largest PD level below close, ∞ if
none). Otherwise no trade. Candidates rejected only by this gate are counted separately, so the
pure knob effect stays visible. Filter variants (X) keep base trades un-re-gated, and base trades
themselves are never re-gated. Room is never loosened below 1.5× anywhere.

## Premium rule (October only, same −50/+90 overlay as the v2 premium completion)
Strike = ATM nearest 100 to entry spot; expiry monthly 2026-10-27 for 1–27 Oct, weekly
2026-11-03 for 28 Oct. Entry premium = open of the first cached 5-min option candle with time
> signal time, from ~/workspace/trading/v4_options_oct_data/ only. Stop = entry − 50, target =
entry + 90 option points (CE and PE alike); stop before target including the entry bar;
square-off 15:10 close; net per 1 lot = (exit − entry) × lot − ₹220 assumed cost; lot Nifty 65,
Bank 30. If no cached candle file exists for that contract+date, the leg is NOT_COMPUTED —
never spot-converted, never browser-fetched in this run (a subagent cannot run the live-browser
fetch; new premium legs are flagged for a browser-capable parent run).

## Metrics and working rule
- Trades = legs (morning + re-entry legs counted separately, as in NS1). Full-target (premium) =
  premium exit_reason = target; full-target (spot) = spot exit = target. A square-off green is
  NEVER a full target. Frequency = legs ÷ 18 days × 5 (per week).
- A variant is "working" only if, on October premiums, net > 0 AND full-target ≥ 50% AND
  frequency ≥ 5/week, per index separately, with EVERY leg premium-computed. If any leg is
  NOT_COMPUTED, the variant cannot be called working on premiums; its premium-known subset is
  reported labelled, alongside the full spot-provisional set. Otherwise the variant is reported
  as closest with the failing leg(s) named.
- If a variant passes October, it is also scored Jan–Oct (spot first, premiums only where
  already fetched; no new Jan–Oct premium fetch unless quick via the existing browser-fetch
  route, with what was/was not premium-scored stated). If no variant passes October, no Jan–Oct
  run is made under this task.

## Variants — one knob each, all else = base above
- W1 rescan window: cutoff 14:30 where bt < 11:30, else 11:30.
- W2 rescan window: cutoff 15:05 where bt < 11:30, else 11:30. (A 15:05 signal enters on the
  15:10 bar; its replay is that bar only.)
- W3 rescan window, tiered by confirmer-break earliness: bt < 10:30 → cutoff 14:30;
  10:30 ≤ bt < 11:30 → cutoff 13:30 (base); bt ≥ 11:30 → 11:30. No extension is given where the
  confirmer did not break early; the confirmer-break window itself (09:30–11:30) is unchanged.
- RB1 re-entry risk band: [10, 1.5 × morning risk]; afternoon stop-on-first-fail retained.
- RB2 re-entry risk band: [5, 2 × morning risk]; afternoon stop-on-first-fail retained.
- BF1 band-filter (OR-width band): morning OR-width cap 360 → 480×scale. Interpretation stated:
  the band filter in the (lA) morning definition is the OR-width cap; loosening it is the only
  additive direction for this knob. Re-entry unchanged.
- BF2 band-filter control: morning OR-width cap 360 → 240×scale (tightening control; expected
  to drop, not add).
- S1 stop-on-first-fail removed (afternoon): an afternoon band-fail SKIPS and scanning continues
  to 15:05 (morning behaviour everywhere); band [10, morning risk] unchanged.
- S2 stop-on-first-fail moved later: an afternoon band-fail at ≤ 13:30 skips and scanning
  continues; the first afternoon band-fail at > 13:30 ends the scan; band unchanged.
- X1 cross-confirmation persistence, signal-bar only: a base morning leg is kept only if the
  confirmer's close at the signal-bar clock time is < confirmer ORL; else the whole day is
  removed (including any re-entry). Distinct from O1 (which required signal AND entry bars);
  O1 itself is NOT re-scored as new.
- X2 cross-confirmation persistence, 2-bar break: a day is eligible only if the confirmer bar
  immediately after its break bar also closes < confirmer ORL; else no rescan that day.
- X3 cross-confirmation depth: the confirmer break-bar close must also be < confirmer PDL
  (in addition to < confirmer ORL); else no rescan that day.
- X4 cross-confirmation persistence, entry-bar only: a base morning leg is kept only if the
  confirmer's close at the entry-bar clock time (signal + 5 min) is < confirmer ORL; else the
  whole day is removed. Distinct from O1 (both bars) and from X1 (signal bar only).
- For X1/X4, a missing confirmer bar at the tested clock time counts as filtered out, and is
  listed, not assumed kept. X variants are filters only: they create no new signal and move no
  entry/stop/target.
- No variant stacks two knobs. No variant is combined with any other variant, with O1, or with
  any Family A–D / NS keep. No direct reclaim CE is introduced anywhere.
