# November 2026 Paper Trading — MAP (from Monday 2026-11-02)

**Paper only. No live orders. Real money = ₹0.** Window: **Mon 2026-11-02 → Mon 2026-11-30**, every NSE trading day. Two systems, two logs, two verdicts — never pooled. The recursive-engine books (Bank v8, Nifty EXP0 book) do **NOT** trade in November; they are December candidates. November trades only the frozen systems below, exactly as frozen on 2026-10-30 — no re-tuning, no manual overrides during the month.

---

## BANK NIFTY — PRIMARY: BNF-PAPER-V1 (lot 30, cost ₹220/trade)

- **Pool:** B2 + NS1 second legs, UNIQUE-ONCE per (date, index, direction), earliest entry.
  - B2 = U1 Bank pool with Skill V3 Bank CE blocked and Skill-solo Bank legs with entry ≤09:55 dropped.
  - NS1 second legs: at most one per day after the base leg exited (target/stop, exit bar ≤13:30); first fresh opening-range crossing after the exit bar, signal ≤14:30, room_ratio ≥1.5, CE blocked on bearish-bias days. No NS2 legs.
- **Exits (G0):** stop = entry − 50 premium points, target = entry + 90; stop checked before target on every bar including the entry bar; square-off 15:10.
- **Strike / entry:** ATM nearest 100; entry premium = open of the 5-min option candle at the entry bar.
- **Expiry:** in force for the trade date, recorded per trade. November Bank monthly expiry: **Mon 2026-11-23** (verified from the instruments master; Bank has no weekly expiry).
- **CONTROL (shadow, same log, never added to the primary):** U1-B2 exactly.
- **Reference (in-sample premiums):** Jan–Oct +₹23,703.50; October +₹17,160.00 (12 trades, 75.0% FT).
- **November pass rule (Bank alone):** premium net > ₹0 AND full-target ≥ 50% AND month closes green AND frequency ≥ 2 trades/week.
- **Log:** `november_paper_bank_log.csv` · **Spec:** `november_paper_bank_V1_frozen.md` · **Verdict channel:** Bank chat e1c1e00e-144d-458a-8b5c-2c66db778095.

## NIFTY — PRIMARY: NF-PAPER-C3G7 (lot 65, cost ₹220/trade)

- **Pool:** C3 confirmed-only — a leg is taken only when ≥2 of the four U1 component systems signal the same (date, index, direction) key. Solo legs are not taken. UNIQUE-ONCE, earliest entry.
- **Exits (G7 runner-lock50):** initial stop = entry − 50, first target = entry + 90; once +90 is reached, stop moves to entry + 50 and the leg runs to a second target of entry + 150. Stop before target on every bar including the entry bar; square-off 15:10. Exit reasons logged distinctly: stop / runner_lock / runner_target / square_off. A leg counts as a full target if the premium reached +90 at any point.
- **Strike / entry:** ATM nearest 100; entry premium = open of the 5-min option candle at the entry bar.
- **Expiry:** in force for the trade date per the frozen spec, recorded per trade.
- **CONTROL (shadow, same log, never added to the primary):** U1-N1 exactly.
- **Reference (in-sample premiums):** Jan–Oct +₹66,619.25; October +₹18,805.25 (4 trades, 75.0% FT). Expected frequency ~1–1.4 trades/week — **no-trade days are normal for this system and are logged with the reason**, not skipped.
- **November pass rule (Nifty alone):** premium net > ₹0 AND full-target ≥ 50% (G7 definition) AND month closes green. Frequency is reported but is **not** a pass/fail leg for November (the recorded money-over-frequency decision, November only).
- **Log:** `november_paper_nifty_log.csv` · **Spec:** `november_paper_nifty_C3G7_frozen.md` · **Verdict channel:** Nifty chat 202c2254-5191-4e09-927a-263bc8ab5100.

---

## Daily rhythm (both indexes, each in its own log)

1. **During the day:** the frozen systems generate signals; entries happen only per the frozen rules above. Blocked/filtered signals are noted in the log, never silently dropped.
2. **15:10:** square-off for any open paper leg.
3. **~15:20 (Mon–Fri):** the logging job runs and writes the day: one row per taken trade (PRIMARY and CONTROL rows separate), plus a no-trade row for the primary on a no-trade day stating why. Legs whose premium candles cannot be obtained are recorded **NOT_COMPUTED** and kept out of every total — never estimated.
4. **~15:45 (Mon–Fri):** the daily-stats job posts everyday stats to the combined-view chat — per index, in separate sections: today's trades and net, month-to-date trades / FT% / cumulative net, pass-rule progress, and the control shadow on its own line. No pooled total, no daily verdict.
5. **Weekly:** running totals stay per index in their own channels; this combined-view chat shows the two side by side only — no combined total as a verdict.
5. **Mon 2026-11-30 (month-end):** each index gets its own verdict in its own channel against its own pass rule above. A November pass is a validation pass only — adoption is a separate decision after month-end review.

## What does NOT happen in November

- No live orders, no real money, 1 lot per index only.
- No re-tuning, no mid-month rule changes, no engine books (Bank v8 / Nifty EXP0) substituted in.
- No pooled Bank+Nifty total and no joint verdict — each index passes or fails alone.

## Context line (not a November pass rule)

The recursive engines' frozen books stand at Bank +₹77,196.50 and Nifty +₹98,001.00 (Jan–Oct in-sample, ~₹17,520/month combined pace) against Chandu's ₹20,000/month combined target. They are judged on fresh December data, separately from this November paper month.
