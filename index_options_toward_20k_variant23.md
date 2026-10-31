# Index OPTIONS — Toward ₹20,000: Variants 2 and 3 (October 2026 premiums)

Paper only, no orders, no stocks. Index OPTIONS only, Nifty and Bank Nifty separately,
never pooled in verdict. Window: 1–28 October 2026 (18 trading days = 3.6 weeks).
**Real money made = ₹0** — no live trades were placed. All nets are paper, per 1 lot,
under the uniform overlay: −50/+90 option points, ₹220 cost per trade,
Nifty lot 65, Bank lot 30. Full-target (FT) = target exit only; square-off greens
are never counted as full targets.

## Base (Variant 0, for reference — not re-scored here)

Unified base from `index_options_october_UNIQUE_trades.md`: earliest signal per
date+index+direction across (lA) v2 + V5 v2 + Skill V3 + Volrix intraday (b) at −1.0%,
counted UNIQUE-ONCE — 34 trades, Nifty +₹14,169.75, Bank +₹11,040.00,
combined +₹25,209.75.

| Index | Trades | Trades/week (18 days) | Full targets | FT % | Net / 1 lot |
|---|---|---|---|---|---|
| NIFTY | 16 | 4.44 | 6 | 37.5% | +₹14,169.75 |
| BANKNIFTY | 18 | 5.00 | 10 | 55.6% | +₹11,040.00 |
| Combined | 34 | — | 16 | 47.1% | +₹25,209.75 |

## Method — one change at a time, nothing stacked silently

- **Variant 2 = base + NS1 second legs only.** Source:
  `index_options_newsetup_premium_october_trades.csv`, family NS1, leg = `second`.
  NS1 base_S1 legs are NOT added (they would double-count the base).
- **Variant 3 = Variant 2 + NS2 afternoon legs only.** Source: same CSV, family NS2,
  leg = `afternoon_rescan`. NS2 morning_S1 legs are NOT added.
- **Distinctness rule (applied to both variants):** an added leg counts only if it
  differs from a leg already in the variant that day in signal time, strike, or
  direction — i.e. it is a genuinely different signal, not a re-listing of a leg
  already counted. A second leg in the same direction and on the same strike as a
  base leg still counts when its signal time, entry premium, and exit differ
  (that is what a "second signal" is: a fresh crossing after the first leg).
  A leg identical in signal time, strike, direction, entry premium, and exit to
  a leg already counted is excluded as a double-count, and is listed below.
- Checks stated for this task, per index separately (combined is a portfolio
  sum, not a pooled verdict): frequency 2–3/week (read as a minimum: at least
  2–3/week), FT ≥ 50%, net > 0, combined ≥ ₹20,000.
- Nothing is adopted on October alone. November 2026 paper remains validation.

## Variant 2 — base + NS1 second legs (10 legs added, all 10 count)

All 10 NS1 second legs are distinct signals from the base leg(s) on their day
(different signal time and, except where noted, different direction or strike):

| Date | Index | Dir | Signal | Strike | Entry prem → Exit prem | Exit | Net / 1 lot | FT |
|---|---|---|---|---|---|---|---|---|
| 2026-10-05 | NIFTY | PE | 10:20 | 22500 | 252.50 → 261.20 | square_off | +₹345.50 | 0 |
| 2026-10-07 | NIFTY | CE | 10:25 | 22700 | 305.50 → 255.50 | stop | −₹3,470.00 | 0 |
| 2026-10-12 | NIFTY | PE | 10:00 | 22500 | 231.95 → 321.95 | target | +₹5,630.00 | 1 |
| 2026-10-27 | NIFTY | CE | 10:00 | 22800 | 72.80 → 22.80 | stop | −₹3,470.00 | 0 |
| 2026-10-28 | NIFTY | CE | 12:40 | 22700 | 190.65 → 182.75 | square_off | −₹733.50 | 0 |
| 2026-10-01 | BANKNIFTY | CE | 11:35 | 55000 | 981.45 → 931.45 | stop | −₹1,720.00 | 0 |
| 2026-10-06 | BANKNIFTY | CE | 10:30 | 55000 | 956.70 → 906.70 | stop | −₹1,720.00 | 0 |
| 2026-10-08 | BANKNIFTY | PE | 12:20 | 54800 | 718.60 → 808.60 | target | +₹2,480.00 | 1 |
| 2026-10-12 | BANKNIFTY | PE | 10:25 | 55000 | 620.00 → 710.00 | target | +₹2,480.00 | 1 |
| 2026-10-27 | BANKNIFTY | PE | 13:05 | 54200 | 107.40 → 197.40 | target | +₹2,480.00 | 1 |

NS1 second legs alone: Nifty 5 trades, 1 target, −₹1,698.00;
Bank 5 trades, 3 targets, +₹4,000.00. (These match the NS1 report's October
premium leg split: Nifty base +₹3,394.50 dragged by second legs −₹1,698.00;
Bank base −₹2,880 rescued by second legs +₹4,000.00 — the same mechanic helps
one index and hurts the other.)

### Variant 2 score

| Index | Trades | Trades/week | Full targets | FT % | Net / 1 lot | vs base |
|---|---|---|---|---|---|---|
| NIFTY | 21 | 5.83 | 7 | 33.3% | +₹12,471.75 | −₹1,698.00 |
| BANKNIFTY | 23 | 6.39 | 13 | 56.5% | +₹15,040.00 | +₹4,000.00 |
| **Combined** | **44** | — | **20** | **45.5%** | **+₹27,511.75** | **+₹2,302.00** |

### Variant 2 verdict (stated checks)

- **NIFTY — does NOT meet all checks.** Frequency 5.83/week meets the 2–3/week
  minimum; net +₹12,471.75 > 0 passes; combined +₹27,511.75 ≥ ₹20,000 passes;
  but FT 33.3% FAILS the ≥ 50% leg.
- **BANKNIFTY — meets all four stated checks.** Frequency 6.39/week, FT 56.5%,
  net +₹15,040.00 > 0, combined +₹27,511.75 ≥ ₹20,000.
- Variant 2 as a whole therefore does NOT pass on both indices: Nifty's hit
  quality fails even though the combined total rises above the base.

## Variant 3 — Variant 2 + NS2 afternoon legs (4 legs added, 1 excluded)

NS2 has 5 afternoon_rescan legs in October premiums. Four are added; one is
excluded as a double-count (see below).

Added legs:

| Date | Index | Dir | Signal | Strike | Entry prem → Exit prem | Exit | Net / 1 lot | FT |
|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | NIFTY | PE | 12:45 | 22400 | 310.90 → 266.05 | square_off | −₹3,135.25 | 0 |
| 2026-10-14 | NIFTY | PE | 13:10 | 22600 | 246.75 → 196.75 | stop | −₹3,470.00 | 0 |
| 2026-10-23 | NIFTY | PE | 11:35 | 22500 | 148.15 → 98.15 | stop | −₹3,470.00 | 0 |
| 2026-10-21 | BANKNIFTY | PE | 11:35 | 55100 | 443.15 → 533.15 | target | +₹2,480.00 | 1 |

NS2 afternoon legs added alone: Nifty 3 trades, 0 targets, −₹10,075.25;
Bank 1 trade, 1 target, +₹2,480.00.

### Excluded — NS2 Nifty 2026-10-21 PE (NOT counted, would be a double-count)

NS2 afternoon Nifty 21 Oct PE: signal 11:35, strike 22800, entry premium 151.30,
exit 241.30 target, net +₹5,630.00 — identical in signal time, strike, direction,
entry premium, exit, and net to unified base leg #24, the (lA) v2 Nifty 21 Oct PE
(signal 11:35, strike 22800, 151.30 → 241.30 target, +₹5,630.00). The NS2 rescan
fires on the same 11:35 OR break that (lA) already traded. Adding it would count
the same trade twice. (Note a data quirk: the NS2 CSV row shows entry_time 12:00
vs the (lA) row's 11:40, but entry_spot 22841.9, premiums, and exit are identical;
the exclusion rests on signal/strike/premiums/exit identity, not on that column.)
Sensitivity, NOT counted: had this leg been wrongly added, Variant 3 would read
Nifty +₹8,026.50 and combined +₹25,546.50 — i.e. the combined ≥ ₹20,000 check
would flip on a double-count alone. That is why it is excluded.

For completeness: the other NS2 afternoon leg's distinctness was checked the
same way. Bank 21 Oct PE (signal 11:35, strike 55100, 443.15 → 533.15) differs
from base Bank 21 Oct PE (signal 11:15, strike 55200, 379.95 → 469.95) in signal
time, strike, and premiums, so it counts. Nifty 23 Oct PE (signal 11:35, strike
22500, 148.15 → 98.15 stop) differs from base Nifty 23 Oct PE (signal 10:05,
strike 22500, 125.85 → 108.70 square-off) in signal time, premiums, and exit,
so it counts.

### Variant 3 score

| Index | Trades | Trades/week | Full targets | FT % | Net / 1 lot | vs Variant 2 |
|---|---|---|---|---|---|---|
| NIFTY | 24 | 6.67 | 7 | 29.2% | +₹2,396.50 | −₹10,075.25 |
| BANKNIFTY | 24 | 6.67 | 14 | 58.3% | +₹17,520.00 | +₹2,480.00 |
| **Combined** | **48** | — | **21** | **43.8%** | **+₹19,916.50** | **−₹7,595.25** |

### Variant 3 verdict (stated checks)

- **NIFTY — does NOT meet all checks.** Frequency 6.67/week meets the minimum;
  net +₹2,396.50 > 0 passes but is thin (one Nifty stop away from negative);
  FT 29.2% FAILS ≥ 50%; combined +₹19,916.50 FAILS ≥ ₹20,000, by ₹83.50.
- **BANKNIFTY — passes its per-index legs** (frequency 6.67/week, FT 58.3%,
  net +₹17,520.00 > 0) **but the combined check fails** (+₹19,916.50 < ₹20,000),
  so Variant 3 does NOT meet all four stated checks as a variant.
- Direction of the change: afternoon legs hurt Nifty badly (−₹10,075.25, 0/3
  targets) and help Bank only slightly (+₹2,480.00, 1/1 target). Variant 3 is
  worse than both Variant 2 (+₹27,511.75) and the base (+₹25,209.75) on combined
  net, despite having the most trades (48).

## Summary — one change at a time

| Variant | Nifty net | Bank net | Combined | Nifty FT | Bank FT |
|---|---|---|---|---|---|
| Base (unique, 34 trades) | +₹14,169.75 | +₹11,040.00 | +₹25,209.75 | 37.5% (6/16) | 55.6% (10/18) |
| Variant 2: + NS1 second (44 trades) | +₹12,471.75 | +₹15,040.00 | +₹27,511.75 | 33.3% (7/21) | 56.5% (13/23) |
| Variant 3: + NS2 afternoon (48 trades) | +₹2,396.50 | +₹17,520.00 | +₹19,916.50 | 29.2% (7/24) | 58.3% (14/24) |

Plain reading: NS1 second legs lift the combined total but dilute Nifty hit
quality below 50%; NS2 afternoon legs then drag Nifty's net to near zero and
pull the combined total below ₹20,000. Frequency is not the binding problem
in either variant (5.83–6.67/week, above the 2–3/week minimum and above
5/week); full-target rate on Nifty is. No variant is adopted on October alone,
and no trade was invented: every added leg above is a row of
`index_options_newsetup_premium_october_trades.csv` except the one explicitly
excluded double-count.

## Sources

- `index_options_october_UNIQUE_trades.md` (base, 34 trades)
- `index_options_newsetup_premium_october_trades.csv` (NS1 second, NS2 afternoon)
- `index_options_newsetups_report.md` (NS leg splits cross-checked:
  NS1 second Nifty −₹1,698.00 / Bank +₹4,000.00; NS2 afternoon Nifty
  −₹4,445.25 across 4 legs including the excluded 21 Oct duplicate, Bank
  +₹2,480.00 — consistent with the 3-leg added Nifty figure of −₹10,075.25
  once the +₹5,630.00 duplicate is removed: −₹4,445.25 − ₹5,630.00 = −₹10,075.25)
