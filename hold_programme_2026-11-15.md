# HOLD PROGRAMME — RESULTS · 2026-11-15

Spec: `hold_programme_SPEC.md` (frozen before scoring). Build:
`hold_programme_build.py` · Data: `hold_programme_results.json` ·
Best-cell trades: `hold_programme_best_cell_trades.csv`.
Basis: equity cash, LONG only, frozen 25 names, daily candles to 2026-11-13,
**per 100 shares PROVISIONAL**, ₹40 per completed position, paper only,
real money ₹0. Judged per year, never pooled.

**Rules in one line:** signal at day close → buy next day's open → sell at the
close of day entry+H, no exit signal of any kind. One position per stock.
Windows: entries Jan 1–Oct 31 of each year; exits past the window end are
marked at the window-end close (WMARK: 2025-10-31 / 2026-10-30).

Triggers: **E0** weekly base (buy at the first bar of each week, no signal) ·
**E1** RSI(14) crosses up through 35 · **E2** close back inside the lower
Bollinger(20,2) band (EKAM-daily's BB entry) · **E3** close crosses above the
20-day average.

Construction audit: E2 signal days reproduce EKAM's BB signal array exactly
(checked ASTRAL / HDFCBANK / VEDL); E0-H5 entry cadence hand-checked
(every second Monday at H5). Signals use closes up to the signal day only.

## E0 — weekly base (no signal)

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H3 | 1,050 | +79,560 | 50.5 | +0.31 | −18,860 | −251,731 | 1,050 | −154,371 | 45.1 | −0.17 | −45,165 | −432,619 |
| H5 | 550 | +157,884 | 53.6 | +0.36 | −31,940 | −338,286 | 550 | −16,228 | 44.9 | −0.03 | −41,940 | −286,130 |
| H10 | 350 | +223,908 | 50.9 | +1.10 | −44,080 | −259,104 | 375 | −169,330 | 40.5 | −0.64 | −47,810 | −251,669 |
| H15 | 275 | +218,087 | 52.7 | +1.31 | −32,525 | −232,902 | 275 | −152,227 | 41.1 | −0.53 | −32,540 | −299,753 |
| H20 | 225 | +133,727 | 53.3 | +1.05 | −32,065 | −173,417 | 200 | −136,378 | 38.0 | −1.02 | −38,840 | −242,476 |

## E1 — RSI(14) crosses up through 35

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H3 | 131 | +15,220 | 48.1 | +0.60 | −25,400 | −43,039 | 165 | −1,521 | 44.8 | −0.25 | −11,030 | −52,329 |
| H5 | 118 | −27,786 | 56.8 | +0.47 | −34,150 | −72,994 | 147 | +12,113 | 44.2 | −0.16 | −6,840 | −46,974 |
| H10 | 96 | +13,864 | 61.5 | +1.06 | −21,740 | −59,224 | 121 | −11,306 | 40.5 | −0.31 | −9,390 | −107,798 |
| H15 | 83 | +42,163 | 63.9 | +1.47 | −24,230 | −56,175 | 103 | +83,963 | 41.7 | −0.16 | −9,890 | −88,109 |
| H20 | 73 | +1,020 | 56.2 | +0.98 | −41,750 | −105,455 | 94 | +82,570 | 42.6 | −0.33 | −14,740 | −128,652 |

## E2 — close back inside lower Bollinger(20,2) band

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H3 | 126 | +4,520 | 51.6 | +0.57 | −18,240 | −54,307 | 166 | −85,506 | 39.2 | −0.19 | −42,930 | −121,320 |
| H5 | 114 | −15,276 | 56.1 | +0.78 | −31,940 | −65,638 | 150 | −59,008 | 44.0 | +0.11 | −21,540 | −76,951 |
| H10 | 107 | +72,025 | 57.9 | +1.59 | −16,040 | −41,313 | 139 | −86,237 | 36.0 | −0.24 | −23,540 | −107,655 |
| H15 | 101 | +30,679 | 59.4 | +1.43 | −24,230 | −86,152 | 129 | −123,095 | 38.0 | −0.84 | −29,540 | −134,645 |
| H20 | 95 | +86,496 | 62.1 | +2.68 | −43,680 | −70,155 | 108 | −75,146 | 36.1 | −0.95 | −23,540 | −138,314 |

## E3 — close crosses above the 20-day average

| Hold | 2025 trades | 2025 net ₹ | WR % | avg % | worst ₹ | max DD ₹ | 2026 trades | 2026 net ₹ | WR % | avg % | worst ₹ | max DD ₹ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| H3 | 298 | +80,827 | 50.0 | +0.07 | −28,545 | −64,723 | 245 | −185,286 | 40.8 | −0.65 | −45,290 | −224,601 |
| H5 | 266 | +60,234 | 47.0 | −0.13 | −29,240 | −59,011 | 226 | −220,124 | 39.4 | −0.79 | −42,990 | −248,124 |
| H10 | 218 | +24,228 | 48.6 | −0.17 | −53,045 | −171,826 | 187 | −141,213 | 39.0 | −0.77 | −42,345 | −218,542 |
| H15 | 179 | +5,102 | 46.9 | +0.06 | −58,470 | −177,263 | 160 | −137,387 | 40.6 | −1.08 | −29,940 | −170,794 |
| H20 | 153 | +73,434 | 55.6 | +0.47 | −47,725 | −165,402 | 140 | −222,872 | 37.9 | −2.50 | −39,485 | −227,070 |

## Placebo (best cell of each trigger, by two-year combined net)

Random entries: same stocks, same per-stock counts, same hold, random entry
days; 1,000 draws, seed 20261115. Statistic = two-year combined net.

| Trigger | Best cell | Combined net ₹ | Placebo percentile | Placebo median ₹ |
|---|---|---|---|---|
| E0 | H5 | +141,656 | 95.9 | −143,442 |
| E1 | H15 | +126,126 | 97.6 | −97,448 |
| E2 | H20 | +11,350 | 85.4 | −123,310 |
| E3 | H3 | −104,459 | 39.2 | −77,793 |

## Best overall cell: E0-H5 (buy every week, sell after 5 trading days)

- 2025: 550 trades · **+₹157,884** · WR 53.6% · avg +0.36%/trade · worst −₹31,940 · max DD −₹338,286 · 25 WMARK
- 2026: 550 trades · **−₹16,228** · WR 44.9% · avg −0.03%/trade · worst −₹41,940 · max DD −₹286,130 · 25 WMARK
- Combined: **+₹141,656** · placebo **95.9th percentile** (median −₹143,442)

### Its November trades (Nov 2–13, all entered Mon 2026-11-09, marked FORCED at the 2026-11-13 close — the H5 exit falls on Nov 16, past the data)

| Stock | Entry | Exit (marked) | Net ₹ |
|---|---|---|---|
| ASTRAL | 1,261.60 | 1,254.00 | −800 |
| BDL | 1,069.00 | 1,030.00 | −3,940 |
| GLENMARK | 2,590.00 | 2,640.00 | +4,960 |
| GODREJCP | 852.75 | 870.75 | +1,760 |
| HDFCBANK | 797.00 | 804.00 | +660 |
| HINDALCO | 947.90 | 943.60 | −470 |
| HINDCOPPER | 434.10 | 439.40 | +490 |
| HINDUNILVR | 2,000.00 | 1,992.90 | −750 |
| HINDZINC | 571.00 | 554.85 | −1,655 |
| INDUSTOWER | 383.75 | 396.00 | +1,185 |
| IRCTC | 466.00 | 457.80 | −860 |
| ITC | 283.45 | 285.00 | +115 |
| KALYANKJIL | 595.00 | 697.00 | +10,160 |
| NATIONALUM | 328.00 | 330.00 | +160 |
| NHPC | 81.30 | 75.83 | −587 |
| NTPC | 323.10 | 319.10 | −440 |
| OBEROIRLTY | 1,730.10 | 1,797.60 | +6,710 |
| OIL | 443.30 | 441.50 | −220 |
| PFC | 332.05 | 334.25 | +180 |
| RECLTD | 299.85 | 301.85 | +160 |
| TATASTEEL | 192.50 | 186.68 | −622 |
| TVSMOTOR | 4,479.60 | 4,495.00 | +1,500 |
| UNITDSPR | 1,412.00 | 1,416.80 | +440 |
| VEDL | 263.00 | 259.68 | −372 |
| WIPRO | 197.00 | 194.60 | −280 |
| **Total** | | | **+17,484** |

## Reference — against EKAM-daily 2c (published lines, not rescored)

| Book | 2025 net ₹ | 2026 net ₹ |
|---|---|---|
| HOLD best overall (E0-H5) | +157,884 | −16,228 |
| HOLD best signal cell (E1-H15) | +42,163 | +83,963 |
| EKAM-daily 2c (BB + RSI, signal exits) | +42,954.60 | +1,41,328.40 |

## Reading (numbers only, no verdict added)

- 2025 rewards almost every long hold (E0-H10 +₹223,908 is the single biggest
  cell-year); 2026 punishes almost all of them. The same cell flips sign
  across years in 17 of 20 cells.
- The only trigger positive in both years at the same hold is E1 at H15
  (+₹42,163 / +₹83,963) and H20 is positive in both years too
  (+₹1,020 / +₹82,570) — but E1's 2026 average % move is negative at every
  hold: its ₹ profit rides on high-priced names, not on hit rate
  (WR 41.7–44.8% in 2026).
- E2's entry is EKAM's BB entry; with a fixed hold instead of EKAM's signal
  exits it makes +₹86,496 in 2025 (H20) and loses at every hold in 2026 —
  the exit rule, not the entry, is what carries EKAM-daily.
- E3 (MA-cross trend entries) is the worst family: negative combined at
  every hold, placebo 39.2 — worse than its own random baseline's middle.
- Every cell's max drawdown is large against its net (best cell: −₹338,286 /
  −₹286,130 of DD against +₹157,884 / −₹16,228 of net) — fixed holds carry
  no downside control at all.

## Forward shadow — HOLD L35-H15 (set up 2026-11-15, listening stage)

Round 2 found L35-H15 (RSI(14) cross up through 35 → next open; exit at
the close 15 trading days after entry) is the local peak of its
neighbourhood — levels 30/40 and holds 10/20 all worse in at least one
year, placebo 97.6th percentile, concentration noted (2025 ex-top-3
negative; March 2026 carries 2026). Per the radio rule it now collects
forward evidence before any adoption question:

- **Scorer:** `hold_shadow_score.py` — imports the research builds
  verbatim (ATLAS daily data / RSI + `hold_programme_r2_build.sim_r2`),
  makes no API calls, reads `data/sarvaritu_fwd` daily stores only.
  One run per completed day: ages open positions, closes any whose
  day-15 close is that day, records signals at the close for the next
  open. Missing stock data = UNSCORED with the reason named, never
  estimated.
- **Ledger:** `hold_shadow_log.csv` — one row per position (OPEN marked
  at the latest close → CLOSED at the day-15 close) plus one DAY row
  per scored run. Positions entered 2026-11-02..2026-11-13 are
  BACKFILL_COUNTERFACTUAL (excluded from the forward tally); entries
  on/after 2026-11-16 are LIVE. The forward tally counts LIVE
  CLOSED + MARKED rows only.
- **Verified before scheduling:** `--verify` dry run over Nov 2–13
  reproduced the R2 November open positions EXACTLY — BDL in
  2026-11-04 @1010.10 marked 1030.00 (+₹1,950.00) · HINDCOPPER in
  2026-11-05 @432.00 marked 439.40 (+₹700.00). The two rows are
  seeded in the ledger as BACKFILL_COUNTERFACTUAL OPEN positions;
  they age and close inside the ledger as their exits fall due.
- **Job:** `hold-shadow-scorer-daily`, Mon–Fri 20:20 IST, first run
  Mon 2026-11-16 (registration verified).
- **Review bound:** 2026-11-30, stated in the scorer header and
  enforced — days after it are refused. Positions still open at the
  Nov 30 run are marked at that close and labelled MARKED, final for
  the review. Adoption is decided at the Nov 30 verdicts on the
  Nov 16–30 forward record only.
