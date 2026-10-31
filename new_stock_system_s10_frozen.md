# S10 — Intraday STOCK system (cash, NOT options) — FROZEN 2026-10-30, BEFORE SCORING

**Status: FROZEN 2026-10-30, before the S10 scoring run. NOT adopted,
NOT a live system. Paper only, no orders.**
**Window: Jan–Oct 2026, October = 1–28 Oct only, 25 stocks, 203 trading days.**
Any Jan–Oct 2026 run of S10 is **in-sample context only**. If S10 passes
ALL adoption legs in-sample (see Verdict rule), its real test is November
2026 paper, logged daily after 15:10, separate from the index logs,
with no re-tuning during November. Adoption only on net + win rate +
frequency together on unseen paper. If S10 fails any leg in-sample, it
is NOT re-tuned on the same window and re-claimed.

## Base design — S9 exactly, ONE change only

S10 = S9 exactly (`new_stock_system_s9_frozen.md`): S8 price design
(CE pullback leg unchanged; PE leg = find_signal PE + second close +
retest-hold stop = max(signal high, confirmation high); target 2× risk;
give-back exit; 100 shares; ₹40/trade; 15:10 square-off; OR width
0.25–3.0%; stock bias filter; Nifty bias-only confirmation; prospective
full-target net ≥ ₹500, per 100 shares provisional — NOT a lot profit)
+ Event Gate v1 G-TIERED unchanged (calendar
`stock_event_calendar_jan_oct_2026.csv`, tiers and thresholds as frozen
in `stock_event_gate_v1_frozen.md`) + gate-ranked cap (max 1 valuable
stock trade/day, max 1/stock/week; cap is a ceiling, not a quota).
The user's stock standard stands: 1 VALUABLE trade/day is enough —
convicted, high-return; no forced trade on a no-setup day.

## THE S10 CHANGE — setup2-PE room definition (only change)

### Diagnosis this fixes

In S8/S9, the PE room test is: room = entry − (highest PD level —
PDH/PDC/PDL — strictly below entry), must be ≥ 1.5× risk. A setup2
OR-breakdown PE signal by construction fires on a close **below PDL**;
by the second-close entry the price is usually still below PDL, so
there is NO PD level below entry and the candidate is discarded
before any room can be measured (`_pe_candidate` returns None on
empty `nxt`). Setup2 PE therefore structurally fails the room test
regardless of how much clear downside the chart actually has. This
was named in the S8 report as needing a new room definition, frozen
as its own version. S10 is that version.

### New room measure — setup2_or_breakdown PE candidates ONLY

For a candidate whose `setup == "setup2_or_breakdown"` and
`direction == "PE"`, the PD-level room test above is REPLACED by a
structural-support room test, defined exactly as:

- Support set S20 = the daily **Low** of each of the **20 trading
  days immediately before today** for that stock (from the cached
  daily data; today and the signal day are not included — the
  previous day IS included, i.e. the 20 daily bars ending with
  yesterday).
- Nearest structural support below entry:
  `support = max { s ∈ S20 : s < entry }`, when that set is non-empty.
- `room_new = entry − support`.
- If no S20 low is below entry (price has broken below every low of
  the last 20 trading days), extend the set to the prior **60
  trading days** (S60) and take `support = max { s ∈ S60 : s < entry }`
  the same way; `room_basis = "swing60"`.
- If still no prior low is below entry within 60 trading days, the
  downside is open: the room test is treated as PASSED,
  `room_basis = "open_downside"`, `room = ""` and `room_ratio`
  recorded as the sentinel **999.0** so the case is auditable and
  countable in the report.
- Otherwise `room_basis = "swing20"`.
- **Pass rule (unchanged threshold): `room_new ≥ 1.5 × risk`.**
  Candidates failing it are discarded, exactly as under the old test.
- The recorded `room` / `room_ratio` fields for a setup2-PE candidate
  are the NEW values, and the unchanged S9 event gate reads the NEW
  `room_ratio` for its tier checks (no_event ≥ 2.0× or prospective
  ≥ ₹1,000; single_news ≥ 2.0×) — the new test replaces the old one
  everywhere for this setup, it is not an extra parallel test.

### What does NOT change

- Setup3 PE and all CE candidates keep the OLD PD-level room test,
  byte for byte.
- Signal generation is unchanged: `find_signal` is NOT modified
  (its own internal 200×scale room check inside setup2 detection
  stays as is — it already treats "no level below" as infinite room,
  which is why the signal fires and only the candidate test killed it).
- Stop, target (2× risk), second-close confirmation, give-back exit,
  prospective ≥ ₹500, OR/bias/Nifty filters, event gate, cap, ranking,
  costs, square-off: all unchanged from S9.
- No loosening of the 1.5× threshold. No other setup gets the new
  test. No timing gates, no re-entry, no second trade of the same
  stock on the same day.

## Verdict rule (pre-registered)

S10 is compared to S9 on the identical window. It is a November-paper
WATCH CANDIDATE only if it progresses on all three together vs S9:
net provisional per 100 shares higher, win rate not lower, AND
frequency materially toward 1 valuable trade/day (report trades/day;
S9 = 0.246/day), AND its month-by-month cumulative does not end lower
than S9's. Otherwise S9 remains the highest-tuned stock version and
S10 goes to the rejected list with the failed leg named. Nothing is
adopted on in-sample alone either way.

## Engine and outputs

`stock_system_s10.py` (S9 gate/cap imported unchanged; PE candidate
generator copied from S8 with ONLY the setup2-PE room branch changed).
Outputs: `s10_trades_jan_oct_2026.csv`, `s10_uncapped_jan_oct_2026.csv`,
`s10_gate_blocked_jan_oct_2026.csv`,
`data/progressive/s10_summary_2026-jan-oct.json`, report
`stocks_resume_s10.md`.
