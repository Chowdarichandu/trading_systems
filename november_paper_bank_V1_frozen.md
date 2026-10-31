# APPROVED PAPER NAME: **BNF-PAPER-V1** (Bank Nifty, Primary) — approved by Chandu 2026-10-30

# November 2026 Paper — BANK NIFTY channel — PRIMARY: V1 — FROZEN (2026-10-30)

**Paper only. No live orders. No stocks. Index OPTIONS only, 1 lot (Bank lot 30). Real money = ₹0.**
This file is the Bank Nifty channel only. Nifty has its own spec (`november_paper_nifty_C3G7_frozen.md`), its own log, and its own verdict. The two channels are never pooled.

## Decision provenance

Decision made 2026-10-30: the user delegated the frequency-vs-quality call ("U know better do"). The assistant's decision: money over frequency. November paper primary in this channel is **V1** (best October net at full frequency in the aggressive run, Jan–Oct premium check above baseline with no red month-end). **U1-B2 runs in the same log as a labelled CONTROL.** Nothing is adopted on in-sample results; November paper is the validation step. No re-tuning during November.

Source definitions: `aggressive_oct_bank.md` (V1, Family 2), `index_options_U1_frozen.md` (U1), `index_options_newsetup_ns1_second_frozen.md` (NS1). Take the definitions from those files; do not re-derive or re-tune them.

## PRIMARY — V1 (verbatim from aggressive_oct_bank.md, Family 2)

**V1 = B2 + NS1 second legs**, under **unique-once per date+index+direction, earliest entry**.

- **B2 = U1-B2**: the U1 Bank pool with (1) Skill V3 Bank CE blocked, and (2) Skill-solo Bank legs with entry ≤09:55 dropped.
  - **U1 — Unified-1** (from `index_options_U1_frozen.md`): a single unified system — components pooled, then deduplicated: (lA) v2 (L1) + V5 v2 + Tuned Skill V3 (CE no-block) + Volrix tuned intraday (b) at −1.0%. Counting is UNIQUE-ONCE only: key = (date, index, direction CE/PE), each key counted once at the earliest entry time among the systems on that key.
- **NS1 second legs**: as frozen in `index_options_newsetup_ns1_second_frozen.md` — at most one second leg per day after the base leg has exited by target or stop with exit-bar time ≤13:30; the second signal is the first fresh crossing of either opening-range level after the base exit bar, signal time ≤14:30, room_ratio ≥1.5, CE blocked on a bearish-bias day. (Premium scoring of those legs follows this spec, not the NS file's spot-provisional scoring.)
- In the aggressive run, V1 and V3 (B2 + NS1 + NS2) were the same October set — Bank's only NS2 add-on was a unique-once duplicate of a base leg. V1 as frozen here contains **no NS2 legs**; if an NS2-type afternoon signal appears in November it is not part of V1 and is not logged as a primary trade.
- Leg selection must reproduce the aggressive run's scored set construction (October: 12 legs; Jan–Oct check: 130 legs). Do not re-interpret during November.

**Exit geometry (primary): G0 baseline** — stop = entry − 50 premium points, target = entry + 90 premium points, both CE and PE; stop checked before target on every bar including the entry bar; square-off 15:10.

**Reference results (in-sample, from aggressive_oct_bank.md):** October premiums **+₹17,160.00** (12 trades, 75.0% FT, 3.33/week); Jan–Oct premium check **+₹23,703.50** (130 trades, 42.3% FT), **no red month-ends** (it fixes B2's red January close).

## CONTROL — U1-B2 exactly (shadow, labelled CONTROL)

U1-B2 exactly as frozen for the earlier November plan: U1 Bank pool + block Skill V3 Bank CE + drop Skill-solo Bank legs with entry ≤09:55; G0 exit geometry (−50/+90). Reference: October premiums +₹13,920.00 (9 trades, 77.8% FT); Jan–Oct premiums +₹18,731.50 with a red January month-end close. Control trades are logged in the same CSV with channel = CONTROL. **Control results are never added to the primary's totals and never count toward the primary's pass rule.**

## Trading parameters (both primary and control)

- Instrument: Bank Nifty index options only. Spot is trigger/levels only, never the traded instrument.
- Lot size: **30** (1 lot). Cost: **₹220 per trade** assumed. Net per trade = (exit premium − entry premium) × 30 − ₹220.
- Entry premium = open of the 5-min option candle at the leg's entry bar (the aggressive-run convention; NS add-on legs are scored at their spot entry bar, same as base legs).
- Strike: ATM nearest 100 to entry spot.
- Expiry: the expiry in force for that trade date, following the October convention (monthly expiry of the trade month; trades after that expiry use the next expiry in force). The expiry used is recorded per trade in the log.
- Full-target % = share of trades exiting at target (+90) only. Square-off greens are not full targets.

## Counting

Unique-once per (date, index, direction), earliest entry, within each of PRIMARY and CONTROL separately. The same underlying signal can therefore appear once as a primary trade and once as a control trade; that is expected and is not double-counting, because the two are never summed.

## What counts as a logged day

- Every NSE trading day in November 2026 is a logged day for this channel. First trading day: **Monday 2026-11-02**.
- Logging happens after 15:10 on the day itself, from that day's data.
- A logged day produces: one row per taken trade (PRIMARY and CONTROL rows separately), plus — on a day with no primary trade — one no-trade row with channel = PRIMARY, system_source = none, and notes stating why (no signal, or every signal filtered/blocked, naming the filter). Blocked/filtered signals are noted, not silently dropped.
- Days the market is closed are not logged days.

## Pre-registered November pass rule — PRIMARY V1, this index alone

V1 passes November paper in the Bank channel only if **all** of these hold on November premiums, 1 lot:

1. November premium net **> ₹0**, AND
2. Full-target rate **≥ 50%**, AND
3. The month **closes green** (November cumulative premium net positive at the final trading day), AND
4. Frequency **≥ 2 trades/week** (trades ÷ November trading days × 5).

Frequency remains a pass/fail leg for the Bank primary. A pass is a November validation pass only — adoption is a separate decision after month-end review. No scoring or re-tuning during November; month-end review only.

## Log file

`~/workspace/trading/november_paper_bank_log.csv` — header: date, channel, system_source, direction, strike, expiry, signal_time, entry_time, entry_premium, stop, target, exit_time, exit_premium, exit_reason, net_inr, notes.
