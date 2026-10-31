# APPROVED PAPER NAME: **NF-PAPER-C3G7** (Nifty, Primary) — approved by Chandu 2026-10-30

# November 2026 Paper — NIFTY channel — PRIMARY: C3+G7 — FROZEN (2026-10-30)

**Paper only. No live orders. No stocks. Index OPTIONS only, 1 lot (Nifty lot 65). Real money = ₹0.**
This file is the Nifty channel only. Bank Nifty has its own spec (`november_paper_bank_V1_frozen.md`), its own log, and its own verdict. The two channels are never pooled.

## Decision provenance

Decision made 2026-10-30: the user delegated the frequency-vs-quality call ("U know better do"). The assistant's decision: money over frequency. November paper primary in this channel is **C3+G7** (confirmed-only legs + runner-lock50 exit) — the aggressive run's standout: Jan–Oct premiums 2.6× the N1 baseline with no red month-end, and not October-fitted. Its known cost is frequency (~1.1/week October, ~1.38/week Jan–Oct). **The ≥2/week frequency requirement is relaxed for this candidate for November only, per that recorded decision** — frequency is reported, but is not a pass/fail leg for the Nifty primary. **U1-N1 runs in the same log as a labelled CONTROL.** Nothing is adopted on in-sample results; November paper is the validation step. No re-tuning during November.

Source definitions: `aggressive_oct_nifty.md` (C3, Family 4; G7, Family 1; stack C3+G7), `index_options_U1_frozen.md` (U1). Take the definitions from those files; do not re-derive or re-tune them.

## PRIMARY — C3+G7 (verbatim from aggressive_oct_nifty.md)

**C3 = confirmed-only (legs with ≥2 source systems)** — a leg is taken only when at least two of the U1 component systems ((lA) v2 (L1), V5 v2, Tuned Skill V3 (CE no-block), Volrix tuned intraday (b) at −1.0%) signal the same (date, index, direction) key. Solo legs are not taken by the primary. Leg selection must reproduce the aggressive run's scored set (October: 4 legs; Jan–Oct check: 56 legs). Do not re-interpret during November.

**G7 = runner-lock50 exit geometry** (Family 1, verbatim): **after +90, stop → entry+50, second target +150.** In full:

- Initial stop = entry − 50 premium points; first target = entry + 90 premium points, both CE and PE.
- When the premium reaches +90, the stop moves to entry + 50 (locking +50). The leg then runs to the second target, entry + 150.
- Exit reasons in the log must distinguish: `stop` (−50 before +90 is reached), `runner_lock` (exit at entry+50 after +90 was reached), `runner_target` (exit at +150), `square_off` (15:10 close, neither barrier hit).
- Stop is checked before target on every bar including the entry bar; square-off 15:10.
- **Full-target definition for this geometry:** a leg counts as a full target if the premium reached +90 at any point (runner_target and runner_lock exits both count; a square-off that never reached +90 does not).

**Counting:** unique-once per (date, index, direction), earliest entry — the C3 confirmation is a property of the key, and each confirmed key is one trade.

**Reference results (in-sample, from aggressive_oct_nifty.md):** October premiums **+₹18,805.25** (4 trades, 75.0% FT, 1.11/week); Jan–Oct premiums **+₹66,619.25** (56 trades, 37.5% FT, 1.38/week), **no red month-end in either window** (three negative individual months Jan–Oct — May, Aug, Sep — every month-end cumulative green).

## CONTROL — U1-N1 exactly (shadow, labelled CONTROL)

U1-N1 exactly as frozen for the earlier November plan: the U1 Nifty pool with solo + early (entry ≤09:55) keys dropped, any system/direction; baseline G0 exit geometry (stop −50, target +90, square-off 15:10). Reference: October premiums +₹10,775.25 (8 trades, 50.0% FT, 2.22/week); Jan–Oct premiums +₹25,159.00, month-end cumulative green at all ten month-ends. Control trades are logged in the same CSV with channel = CONTROL. **Control results are never added to the primary's totals and never count toward the primary's pass rule.**

## Trading parameters (both primary and control)

- Instrument: Nifty index options only. Spot is trigger/levels only, never the traded instrument.
- Lot size: **65** (1 lot). Cost: **₹220 per trade** assumed. Net per trade = (exit premium − entry premium) × 65 − ₹220.
- Entry premium = open of the 5-min option candle at the leg's entry bar (the aggressive-run convention for this channel's legs).
- Strike: ATM nearest 100 to entry spot.
- Expiry: the expiry in force for that trade date, following the October convention (monthly expiry of the trade month; trades after that expiry use the next expiry in force). The expiry used is recorded per trade in the log.
- Full-target % for the control = share of trades exiting at target (+90) only; square-off greens are not full targets. (For the primary's G7 geometry, use the full-target definition in the G7 section above.)

## What counts as a logged day

- Every NSE trading day in November 2026 is a logged day for this channel. First trading day: **Monday 2026-11-02**.
- Logging happens after 15:10 on the day itself, from that day's data.
- A logged day produces: one row per taken trade (PRIMARY and CONTROL rows separately), plus — on a day with no primary trade — one no-trade row with channel = PRIMARY, system_source = none, and notes stating why (no signal, no confirmed key that day, or every confirmed key filtered, naming the reason). Because the primary is confirmed-only, no-trade days are expected and are logged, not skipped.
- Days the market is closed are not logged days.

## Pre-registered November pass rule — PRIMARY C3+G7, this index alone

C3+G7 passes November paper in the Nifty channel only if **all** of these hold on November premiums, 1 lot:

1. November premium net **> ₹0**, AND
2. Full-target rate **≥ 50%** (per the G7 full-target definition above), AND
3. The month **closes green** (November cumulative premium net positive at the final trading day).

Frequency is **reported but is NOT a pass/fail leg** for the Nifty primary in November (relaxed for this candidate for November only, per the decision recorded above). A pass is a November validation pass only — adoption is a separate decision after month-end review. No scoring or re-tuning during November; month-end review only.

## Log file

`~/workspace/trading/november_paper_nifty_log.csv` — header: date, channel, system_source, direction, strike, expiry, signal_time, entry_time, entry_premium, stop, target, exit_time, exit_premium, exit_reason, net_inr, notes.
