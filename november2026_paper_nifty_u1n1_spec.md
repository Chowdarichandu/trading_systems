# November 2026 paper — NIFTY channel only — U1-N1 (FROZEN)

Separate channel: Nifty only. This spec and its log contain no Bank
Nifty rows, no Bank verdict and no combined total. Bank Nifty is a
different channel with its own spec and log
(`november2026_paper_bank_u1b2_spec.md`).

Index OPTIONS only, paper only, no orders, no stocks. 1 options lot
(Nifty lot 65, as used in the October premium scoring).
Real money = ₹0 throughout.

## Frozen candidate — U1-N1, exactly as scored Jan–Oct

Source: `index_options_U1_nifty_tuning_green_close.md` (30 Oct 2026).

U1 components: (lA) v2 + V5 v2 + Skill V3 (CE no-block) + Volrix tuned
intraday (b) at −1.0%. Counting: UNIQUE-ONCE — each date + direction
counted once, at the earliest entry.

One block: any key that is solo (single-system, n_systems = 1) AND
entry_time ≤ 09:55 is blocked — any system, either direction.
In plain words: no unconfirmed trade in the first 40 minutes.

In-sample record (stage pass only, NOT adopted): Jan–Oct 2026
+₹168,140.25 mixed (108 trades, 41.7% full-target, 2.66/week); October
+₹10,775.25 premiums per 1 lot (8 trades, 50.0% FT, 2.22/week);
month-end cumulative green at EVERY month-end Jan–Oct (lowest close
Jan +₹8,710); May was still a negative individual month (−₹9,235).
Jan–Sep was spot provisional, so no pure-premium Jan–Oct total exists —
November is scored on premiums only.

## November protocol

- Starts Mon 2026-11-02. Log daily after 15:10 IST, one row per
  date + direction key, in `november2026_paper_nifty_u1n1_log.csv`.
- Log EVERY signal day, including: blocked solo + early (≤09:55) keys,
  no-trade days, and any later confirmed entry on a blocked day —
  recorded in its own columns, never assumed to be no-trade and never
  counted as an N1 trade.
- Exit overlay as in October scoring: stop −50 / target +90 option
  points, ₹220 cost per trade, square-off per the source engines.
- No scoring verdict, no re-tuning and no rule change during November.
  Month-end review only.
- Missing data days stay missing and are noted in the log; they are
  not patched from another source.

## November pass bar — Nifty only, judged at month-end

All must hold, on Nifty premiums alone:
1. November premium net > 0.
2. Month-end cumulative green (this is a single month, so this is the
   November net itself, stated plainly).
3. Full-target rate improved vs the U1 Nifty base (37.5% in October).
4. Frequency ≥ 2 trades/week.

Failing any leg = U1-N1 is not adopted; the failure and its reason are
logged at month-end. No mid-November fix is applied to rescue it.
