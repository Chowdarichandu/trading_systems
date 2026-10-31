# Stocks October tuning — Family A: exit management — FROZEN 2026-10-30 BEFORE SCORING

STOCKS ONLY, cash intraday, paper only, no orders. All figures provisional
per 100 shares, ₹40/trade cost, NOT premiums, NOT a lot profit.

Diagnosis first (October S9 slice): S9 October capped = 1 trade
(ASTRAL 2026-10-12 setup3 PE, -₹520 provisional per 100 shares, stop).
S8 uncapped October pool = only 3 candidates (GODREJCP 2026-10-06
+₹217.50 partial-BE win, OBEROIRLTY 2026-10-06 +₹650 target,
ASTRAL 2026-10-12 -₹520 stop). Both October winners were gate-blocked
(no_event OR rule), the loser passed. Exit changes cannot create trades;
this family isolates exit effect on the SAME entry pool (S8 uncapped
entries, gate+cap as in S9) so any net change is exit-only.

Variants (entry, stop, entry time identical; only exit rule changes):
- E0 baseline: partial 50% at 1R, rest to breakeven, target 2R (S8/S9 exit; must reproduce original nets)
- E1 no partial: 100% to target 2R / original stop
- E2 target 1.5R, partial 50% at 1R, rest BE
- E3 target 2.5R, partial 50% at 1R, rest BE
- E4 target 3R, partial 50% at 1R, rest BE
- E5 lock trail: partial 50% at 1R, rest stop trails to entry +0.5R (in trade direction), target 2R
- E6 partial 25% at 1R, rest BE, target 2R
- E7 partial 75% at 1R, rest BE, target 2R
- E8 no partial, target 1.5R

Bar order within a candle: stop first, then partial, then target (as S1 replay).
Square-off 15:10 close. Full-target = exit reached the variant's target
on the remaining/full position after any partial, as in baseline semantics.

Scored on: October 2026 slice AND Jan–Sep 2026 separately (anti-overfit).
No variant is adopted on October alone.
