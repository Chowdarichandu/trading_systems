# Round 2 Family I — DRAWDOWN CONTROL — FROZEN 2026-10-30, BEFORE SCORING

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade — NOT premiums, NOT a lot profit.

Target: S12's Jan–Sep max drawdown −₹9,007.50 provisional per 100 shares
(peak after January +₹7,712.50 month, trough in the Mar–Jun bleed).
Base: S12 entries exactly (same capped 101 trades); ONLY the exit replay
changes. This isolates the exit effect, as in Round 1 Family A.

- I0 = S12 exit (control): partial 50% @1R, rest to BE, target 3R.
- I1: target 3R, partial 50% @1R, remaining stop locks at +0.5R after the
  partial (instead of BE at entry). NOTE: this is NOT Round 1's rejected
  F6 — F6 was lock-0.5R at a 2R target on a different entry pool; the
  task for Round 2 explicitly lists the 3R + earlier-lock variant.
- I2: time-stop 60 minutes — if the 1R partial has NOT triggered within
  60 minutes of entry, exit the full position at the close of the first
  candle at/after entry+60min. If the partial already triggered, the
  trade continues under I0 rules.
- I3: time-stop 120 minutes — same rule at entry+120min.

Tier-exclusion variants are deliberately NOT in this family: every tier
is net-positive in one window and net-negative in the other (no_event:
Jan–Sep −₹2,762.50 but October +₹1,280; pre_announcement the mirror), so
excluding a tier is a period bet, not drawdown control, and it directly
contradicts the October objective for no_event.

Winner rule (task): beat S12 on October net + win + frequency together
AND Jan–Sep net not worse AND Jan–Sep maxDD not deeper. (An I variant
that only improves drawdown while cutting October net is a drawdown
finding, not a new best.)
