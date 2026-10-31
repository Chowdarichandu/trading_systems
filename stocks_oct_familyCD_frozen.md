# Stocks October tuning — Families C+D: setup mix and event gate — FROZEN 2026-10-30 BEFORE SCORING

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade cost, NOT premiums, NOT a lot profit.

Diagnosis first: the two October winners blocked by the gate were both
no_event setup3 PE trades that failed BOTH no-event bars narrowly
(room 1.87×, prospective ₹990 and ₹880 — just under room 2.0× / ₹1,000),
while the October loser (ASTRAL, room 2.875×, prospective ₹920) passed
on room alone. The gate's no-event OR rule, and the S11 AND tightening,
are therefore directly implicated in October — this family tests gate
handling as a system rule (applied to all months identically), never as
a per-trade unblock.

Family C (setup mix, applied as a filter before cap on the given pool):
- C1 PE-only (setup3/setup2 PE legs only)
- C2 CE-only (setup4 CE legs only)

Family D (gate variants, on S8 uncapped pool and on the best Family B pool):
- D0 no gate: all S8 candidates pass; cap = S8 ranking (prospective desc, room, setup rank), 1/day, 1/stock/week
- D1 S9 gate G-TIERED as-is (baseline)
- D2 S11 gate (no_event AND rule)
- D3 no_event loosened to S8 base bar: no_event passes at room ≥1.5× (i.e. no extra no-event bar); other tiers unchanged; cap ranking = gate tier ranking as S9
- D4 event-tiers only: only post_reaction / pre_announcement / single_news tiers pass; no_event blocked entirely; cap ranking as S9

Scored on: October 2026 slice AND Jan–Sep 2026 separately (anti-overfit).
No variant adopted on October alone; stage pass only.
