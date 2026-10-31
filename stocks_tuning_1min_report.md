# TUNING LOOP LINE 7 — 1-Minute Granularity: Feasibility + MOVER-A October Pilot

Equity cash, LONG/SHORT, paper only, real ₹0. All figures provisional per
100 shares, net = gross − ₹40/trade. Scope was tightly bounded: feasibility
first, and the pilot ONLY because the data proved complete. No rule was
changed; MOVER-A stays frozen exactly as scored in Lines 2/4/5.

## STEP 1 — FEASIBILITY VERDICT: CLEAN (1-min is genuinely available, deep and complete)

Method: the verified Upstox connector path (`fetch_upstox_via_connector.call`,
v3 historical-candle endpoint, `/minutes/1/{to}/{from}`) — the same endpoint
family as the verified 5-min volume fetch and the index 1-min build
(`fetch_1min_x.py`, which returned 375 bars/day for NIFTY/BANKNIFTY back to
January 2026). Samples: HDFCBANK, GLENMARK, OBEROIRLTY (home universe) +
RELIANCE, TCS (extended universe).

| Test | Result (all 5 samples identical) |
|---|---|
| October 2026, ONE request per stock | **7,500 bars = 20 trading days × exactly 375 bars**, zero partial days, no error, no truncation |
| October days returned | Oct 1, 5–9, 12–16, 19, 21–23, 26–30 — i.e. all 18 days of the 5-min cache **plus Oct 29 and Oct 30**, which the 5-min cache never had |
| February 2026 week (Feb 2–6), one request | **1,875 bars = 5 days × exactly 375 bars**, all 5 trading days present |
| History depth | **Reaches February 2026 cleanly** — no depth wall, no gaps |

The one-month-per-request scale works (7,500 bars in a single response), so
a full Jan–Oct 1-min build for 50 stocks is a ~500-request job if a future
line ever needs it. Nothing about the data forced a stop.

Full-October fetch for the pilot then verified **50/50 stocks at 7,500 bars,
20 days, zero non-375 days** (375,000 bars; `data/1min_stocks_oct2026/`,
verification.json alongside).

## STEP 2 — PILOT: MOVER-A October chains re-resolved at 1-min

**Method.** The recorded legs from `mover_A_old_trades.csv` +
`mover_A_ext_trades.csv` (October rows: **76 chains, 123 legs**, Oct 1–28)
were re-scored with ONE change: entries and exits resolved on 1-min bars.
Same chains, same legs, same entry moments — the entry price is the open of
the first 1-min bar of the recorded 5-min entry slot; exits use the frozen
Mover logic (target +1.25%, stop −0.5%, stop before target within a bar,
square-off at the 15:10 bar's close = the 15:14 minute's close, with the
15:10–15:14 minutes still stop/target-checked first, exactly as the 15:10
5-min bar is).

**Validation before trusting the pilot.** (i) The fetched 1-min bars,
aggregated back to 5-min, reproduce **all 123 recorded legs exactly**
(exit reason, exit price, gross — 0 failures). (ii) First-minute opens match
the recorded entry prices on every leg (max difference 0.0). (iii) The
re-scored 5-min totals reproduce the published October slices to the paisa:
home **+₹16,825.42** (Line 2) and ext **+₹39,984.55** (Line 4).

**Result — the October delta is ₹0.00.**

| Scope | Chains | Legs | Net @5-min | Net @1-min | Delta | Chains changing class |
|---|---|---|---|---|---|---|
| Home 25 (A) | 48 | 77 | +₹16,825.42 | +₹16,825.42 | **₹0.00** | 0 |
| Ext 25 (A) | 28 | 46 | +₹39,984.55 | +₹39,984.55 | **₹0.00** | 0 |
| **Pooled 50** | **76** | **123** | **+₹56,809.97** | **+₹56,809.97** | **₹0.00** | **0** |

- Chain outcomes: 45 win → win, 31 loss → loss, **zero class changes**.
- Leg exit reasons: 50 target → target, 60 stop → stop, 13 square-off →
  square-off — **zero flips**.
- The 1-min scan genuinely ran at minute resolution: in 94/123 legs the
  trigger minute sits strictly inside the recorded 5-min exit bar. Exit
  prices differ from the recorded CSV by at most 0.005 — exactly the CSV's
  2-dp rounding (0.000 on square-offs).

**Why the delta is exactly zero — the mechanism, not a shrug.** Mover exits
are *price-level* exits: a leg leaves at its target price, its stop price,
or a fixed square-off close. Finer resolution can only change money when a
single 5-min bar spans **both** the stop and the target, leaving the order
ambiguous (the 5-min engine assumes the conservative order: stop first).
Checked directly: **0 of 123 legs had a 5-min entry or exit bar spanning
both levels.** The ambiguity the 1-min test existed to expose never occurred
in October — so none of the flagship's October edge is a 5-min aggregation
artefact. What October shows at 5-min, it shows at 1-min, to the paisa.

**Scope limit, stated plainly.** This pilot held the recorded chain
composition fixed (same signals, same entry moments, per the line's brief).
It isolates the resolution of entries/exits only. A full 1-min rebuild —
signals generated on 1-min bars, round-2 legs starting from 1-min exit
times — could in principle produce different chains; that is a different,
larger test, not run here and not needed to answer this line's question.

## Bottom line

1-min stock data on Upstox is complete and deep (February verified, October
flawless across 50 stocks, and it even contains Oct 29–30, two days the
5-min programme never had). Re-resolving MOVER-A's October at 1-min changes
**nothing — delta ₹0.00, zero outcome flips** — because level-priced exits
leave no room for bar aggregation to invent or hide profit, and the one
ambiguity that could have (a bar spanning both stop and target) never
happened in 123 legs. The flagship's October number is real at both
resolutions.

Files: `fetch_1min_feasibility.py`, `line7_feasibility_raw.json`,
`fetch_1min_oct_all.py`, `data/1min_stocks_oct2026/` (50 CSVs +
verification.json), `stocks_tuning_1min_rescore.py`,
`line7_moverA_oct_1min_legs.csv`, `line7_moverA_oct_1min_chains.csv`,
`line7_moverA_oct_1min_results.json` — all in ~/workspace/trading/.
