# Line S3 — Volatility-Compression Breakout — REPORT (incremental)

Status: cells frozen in `stocks_S3_frozen.md` before scoring. Engine
`stocks_S3.py`. Paper only, real ₹0, provisional per 100 shares,
₹40/trade, Jan–Oct 2026, pooled 50 primary.

(sections appended as the run lands: audit → cell table → placebo → verdict)

## Timing audit (same run as scoring)

**CLEAN — 9,422 trades checked across all 6 cells, 0 violations.**
Every trade: pattern information complete at day D's close, trade taken
on a strictly later session, entry = open of the bar immediately after
the trigger bar (entry index = trigger index + 1 asserted per trade).
The placebo's 1,292 trades also audited: 0 violations.

## Cell table — pooled 50 (home / ext splits in `stocks_S3_results.json`)

| Cell | Pattern | Exits | Trades | Net ₹ | Jan–May ₹ | Jun–Oct ₹ | Oct ₹ | Breadth | Exp/trade ₹ |
|------|---------|-------|-------:|------:|----------:|----------:|------:|--------:|------------:|
| S3-A1 | NR7 | T125/S050 | 1,413 | **−104,942.40** | +4,465.86 | −109,408.26 | −39,057.50 | 17/50 | −74.27 |
| S3-A2 | NR7 | T10/S050 | 1,413 | **−105,808.34** | −34,845.17 | −70,963.17 | −21,797.19 | 16/50 | −74.88 |
| S3-B1 | Inside | T125/S050 | 1,175 | **+1,224.64** | +115,088.50 | −113,863.86 | −32,389.87 | 20/50 | +1.04 |
| S3-B2 | Inside | T10/S050 | 1,175 | **−899.88** | +87,350.16 | −88,250.04 | −30,199.07 | 19/50 | −0.77 |
| S3-U1 | NR7∪Inside | T125/S050 | 2,123 | **−70,583.70** | +84,843.99 | −155,427.69 | −58,053.40 | 16/50 | −33.25 |
| S3-U2 | NR7∪Inside | T10/S050 | 2,123 | **−87,423.79** | +35,179.58 | −122,603.37 | −40,361.32 | 17/50 | −41.18 |

Home/ext splits of the two least-bad cells: B1 home +₹1,274.53
(breadth 9/25) / ext −₹49.89 (11/25); B2 home −₹8,243.55 / ext
+₹7,343.67. Neither universe carries the pattern on its own.

## Placebo (best cell S3-B1, trade day D+6, same levels/exits)

1,292 trades, pooled **−₹14,889.68** (Jan–May +₹34,698.75 / Jun–Oct
−₹49,588.43, October −₹20,615.18, breadth 19/50). B1's +₹1,224.64 is
nominally above the placebo's −₹14,889.68, but the comparison is moot:
B1 itself fails the gate on three legs, so "beating" this placebo
certifies nothing.

## Verdict — DEAD, no candidate

**No cell passes the gate; `stocks_S3_candidate_spec.md` is NOT
frozen.** The failure pattern is consistent and instructive:

- **NR7 is decisively negative** (−₹105k at both exits) — the purest
  compression pattern is the worst book. Next-day close-breaks out of
  an NR7 day lose in both halves at T10 and collapse in Jun–Oct at
  T125.
- **Inside-day breakouts are a halves coin-flip, not an edge:**
  strongly positive Jan–May (+₹115,088.50 at T125) and almost exactly
  offset negative Jun–Oct (−₹113,863.86), with October deeply
  negative (−₹32,389.87) and breadth 20/50. Whatever paid in the
  first half of 2026 reversed in the second — the same sign-flip
  signature that killed LADDER and the drift gates.
- The union dilutes nothing and rescues nothing (−₹70.6k / −₹87.4k).

Volatility compression → next-day breakout joins the dead list: on
this 50-stock universe, a quiet day's range break the next day has no
durable continuation after ₹40/trade costs.

