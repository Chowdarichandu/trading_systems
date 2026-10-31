# November 2026 paper — BANK NIFTY channel only — U1-B2 (FROZEN)

Separate channel: Bank Nifty only. This spec and its log contain no Nifty
rows, no Nifty verdict and no combined total. Nifty is a different channel
with its own spec and log (`november2026_paper_nifty_u1n1_spec.md`).

Index OPTIONS only, paper only, no orders, no stocks. 1 options lot
(Bank Nifty lot 30, as used in the October premium scoring).
Real money = ₹0 throughout.

## Frozen candidate — U1-B2, exactly as scored Jan–Oct

Source: `index_options_U1_bank_tuning_positive.md` (30 Oct 2026).

U1 components: (lA) v2 + V5 v2 + Skill V3 (CE no-block) + Volrix tuned
intraday (b) at −1.0%. Counting: UNIQUE-ONCE — each date + direction
counted once, at the earliest entry.

Two blocks, applied in this order:
1. Any key whose representative system is Skill V3 and direction is CE
   is blocked.
2. Any remaining key where Skill V3 is the sole system (n_systems = 1)
   and entry_time ≤ 09:55 is blocked.

In-sample record (stage pass only, NOT adopted): Jan–Oct 2026
+₹124,415 mixed (89 trades, 36.0% full-target, 2.19/week); October
+₹13,920 premiums per 1 lot (9 trades, 77.8% FT, 2.50/week);
month-end cumulative green at every month-end Jan–Oct; ex-March still
positive at +₹26,625. Jan–Sep was spot provisional, so no pure-premium
Jan–Oct total exists — November is scored on premiums only.

## November protocol

- Starts Mon 2026-11-02. Log daily after 15:10 IST, one row per
  date + direction key, in `november2026_paper_bank_u1b2_log.csv`.
- Log EVERY signal day, including: blocked Skill-CE keys, blocked
  Skill-solo ≤09:55 keys, no-trade days, and any later
  (lA)/V5/Volrix entry on a blocked key — recorded in its own columns,
  never assumed to be no-trade and never counted as a B2 trade.
- Exit overlay as in October scoring: stop −50 / target +90 option
  points, ₹220 cost per trade, square-off per the source engines.
- No scoring verdict, no re-tuning and no rule change during November.
  Month-end review only.
- Missing data days stay missing and are noted in the log; they are
  not patched from another source.

## November pass bar — Bank only, judged at month-end

All must hold, on Bank premiums alone:
1. November premium net > 0.
2. Month-end cumulative green (this is a single month, so this is the
   November net itself, stated plainly).
3. Full-target rate improved vs the U1 Bank base (55.6% in October).
4. Frequency ≥ 2 trades/week.

Failing any leg = U1-B2 is not adopted; the failure and its reason are
logged at month-end. No mid-November fix is applied to rescue it.
