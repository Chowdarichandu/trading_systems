# WIDE-DAILY — EKAM-DAILY (EKAM-2c) on the full-NSE universe — 2026-11-17

**VERDICT: STOPPED AT THE CONTROL. The wide run was NOT scored.**
The frozen control — the identical EKAM-2c machinery run on the frozen 25
names fed from the parquet dump — does **not** reproduce the published
EKAM-2c totals. Per the frozen spec (`wide_daily_SPEC.md` §1), a control
miss means no wide scoring: a 2,646-name result built on a base that cannot
reproduce its own 25-name book would be meaningless. Everything below is
the miss, its size, and its measured cause.

Basis: equity cash · per 100 shares PROVISIONAL · ₹40/trade · paper only,
real money ₹0. Machinery: `ekam_build.prep` signal construction +
`ekam2c_build.sim2c` + `ekam_build.stats`, verbatim — the only change vs
the published run is the data source (parquet instead of the
`sarvaritu_fwd` stores).

## The control miss

| Year | Parquet-fed 25 (got) | Published EKAM-2c | Difference |
|---|---|---|---|
| 2025 | 79 trades · **+₹63,621.50** | 74 trades · +₹42,954.60 | +5 trades · **+₹20,666.90** |
| 2026 | 102 trades · **+₹1,50,777.40** | 102 trades · +₹1,41,328.40 | 0 trades · **+₹9,449.00** |

Full stats-dict equality (the spec's pass bar) fails in both years.
Trade-level diff against the published EKAM-2c list:

| Year | Identical | Same entry, different exit | Only in parquet run | Only in published |
|---|---|---|---|---|
| 2025 | 45 of 74 | 12 | 22 | 17 |
| 2026 | 80 of 102 | 12 | 10 | 10 |

One shifted exit changes the next entry (one position per name), so the
two books diverge progressively — e.g. ASTRAL entered 2025-02-18 @ ₹1,381
exits 2025-03-25 in the parquet run vs 2025-04-02 in the published book.

## The cause — the two sources define "close" differently

- The frozen stores' daily close is the **close of the last 5-minute bar
  (15:25)** of the intraday store. Proven directly: ASTRAL 2025-01-01 last
  5m close 1653.0 = store daily close 1653.0; HDFCBANK 2025-06-02 last 5m
  close 965.5 = store daily close 965.5 (two names, four days checked).
- The parquet dump's close is the **exchange official daily close**
  (ASTRAL 2025-01-01: 1651.45; HDFCBANK 2025-06-02: 966.0), which includes
  the closing session after the last intraday bar.
- Across the frozen 25 over the full overlap (13,150 days, dates identical
  in both sources): open/high/low agree almost everywhere (0–4 mismatching
  fields per name), but the **close differs on 9,665 days (73.5%)**, mean
  |difference| 0.169% of price. Bollinger bands and RSI are computed on
  closes and every EKAM signal is close-driven — a 0.17% close difference
  flips borderline band/RSI crosses, and the book forks from there.
- The other candidate cause was isolated and cleared: re-running the 25
  on parquet data truncated to the store's own window (from 2024-10-01)
  gives 2025: 75t / +₹42,490.50 and 2026: 102t / +₹1,50,777.40 — the 2026
  total is identical to the full-history parquet run. The parquet's extra
  pre-2024 warm-up history changes one 2025 trade; it is not the cause.

## Integrity checks that DID pass

- The liquidity gate machinery is faithful: `sim2c_gated` with an
  all-liquid mask reproduces `sim2c` trade-for-trade on all 25 names.
- The extended stats function agrees with `ekam_build.stats` on every
  shared field on the control trades (both years).
- No symbol was estimated or hand-filled; no web fetch was needed.

## What it would take to run the wide test honestly

1. **Store-basis daily bars for all 2,646 names** (last-5m-bar close):
   the intraday stores exist only for the frozen 25 — this data does not
   exist for the wide universe, and building it means fetching 5-minute
   bars for ~2,600 names.
2. **Or a deliberate re-baseline (a decision, not a fix):** accept the
   official-close basis as a new base. On that basis the frozen-25 EKAM-2c
   book reads 2025: 79t / +₹63,621.50 · 2026: 102t / +₹1,50,777.40 —
   *higher* than published in both years — and the wide run (raw +
   ₹1-crore-median-liquidity-screened, placebo, November slice, exactly as
   frozen in the spec) could then be scored against that control. But
   every published EKAM-daily number, including the live forward paper
   started 2026-11-16, stands on the store basis; switching the basis is
   the owner's/parent's call, not something this run may do silently.

## Files

- `wide_daily_SPEC.md` — the frozen spec (control, screen, verdict).
- `wide_daily_build.py` — the build (control + gated sim + wide machinery,
  ready to run the moment a valid control basis exists).
- `wide_daily_results.json` — control detail (full stats, got vs
  published), integrity checks, and the diagnosis block.
- `wide_daily_trades.csv` — the parquet-fed frozen-25 trade list
  (run = CONTROL25_PARQUET), for inspection of the divergence.

---

# PART 2 — THE WIDE RUN, ON THE OFFICIAL-CLOSE BASIS (parent decision 2026-11-17)

Part 1 stopped at the control, as the frozen spec required. The parent then
made the basis decision Part 1 asked for: **the wide run proceeds on the
official-close (parquet) basis, as a research basis only.** The parquet-fed
frozen-25 run from Part 1 is the control for everything below, labelled the
**OFFICIAL-CLOSE control**. It was re-run for this part and reproduces the
Part 1 numbers with full stats-dict equality in both years (2025: 79 trades ·
+₹63,621.50 · 2026: 102 trades · +₹1,50,777.40) — control PASSED on this
basis, and the wide scoring ran exactly as frozen in the spec.

**VERDICT: NOT A SUCCESS under the frozen bar.** The liquidity-screened run
is positive in both years, but the placebo is beaten in **neither** year
(71.5th percentile in 2025, 81.5th in 2026, against the 95 bar), so the
spec's success test fails. **Concentration, in words, as the spec requires:
the screened 2025 result is carried by its biggest trades and names** —
remove the year's top-3 trades and 2025 is −₹9,22,717.30; the top-5 names
alone netted +₹17,40,460 against a year total of just +₹1,32,459.70 (a
1,314% share — the other 1,440 names netted negative together). The screened
2026 result is broader (ex-top-3 and ex-top-10 both stay positive; top-5
names are 51.7% of the year) but still does not clear the placebo.

## Why this part runs on a different basis — in plain words

The two data sources define the daily "close" differently. The live EKAM
book's stores take the close of the day's last 5-minute bar (15:25); the
parquet dump carries the exchange's official daily close, which includes
the closing session after that bar. The two closes differ on 73.5% of days
(mean difference 0.169% of price), and because Bollinger bands and RSI are
computed on closes, the same frozen rules take somewhat different trades on
each basis. So every wide number below is comparable to the OFFICIAL-CLOSE
control (frozen 25 on parquet: +₹63,621.50 / +₹1,50,777.40) — **not** to the
live book's published totals (+₹42,954.60 / +₹1,41,328.40), which stand on
the store basis and are unchanged. The EKAM-daily forward paper started
2026-11-16 is not re-baselined; nothing running was touched.

## Coverage

2,646 parquet files; 2,645 symbols scored. One exclusion: **SUVID-RE** (no
usable OHLC rows) — counted, never estimated. Every scored symbol carried a
volume column, so the no-volume exclusion list is empty.

## Screened run (₹1-crore median-60-session liquidity gate on entries)

| Year | Trades | Net | WR | Ex-top-3 | Ex-top-10 | Max DD | Names |
|---|---|---|---|---|---|---|---|
| 2025 | 4,260 | **+₹1,32,459.70** | 64.4% | −₹9,22,717.30 | −₹22,09,797.30 | −₹47,14,397.40 | 1,445 |
| 2026 | 4,990 | **+₹31,13,300.50** | 66.5% | +₹18,54,170.50 | +₹5,09,380.50 | −₹49,93,408.70 | 1,552 |

- Halves (by entry month): 2025 — H1 (Jan–Jun) 2,446t +₹13,33,654.40 ·
  H2 (Jul–Oct) 1,814t **−₹12,01,194.70**. 2026 — H1 2,617t +₹46,65,425.20 ·
  H2 2,373t **−₹15,52,124.70**. In both years the profit is made in the
  first half and a large part is given back in the second.
- Placebo (200 random-entry draws on the same liquid pool, seed 20261114):
  2025 — real +₹1,32,459.70 sits at the **71.5th percentile** (draw mean
  −₹4,46,898.26, median −₹3,71,034.00). 2026 — real +₹31,13,300.50 sits at
  the **81.5th percentile** (draw mean +₹21,14,861.29, median
  +₹21,99,942.00): in 2026 even random entries on liquid names made money
  on this basis, and the book's margin over them is not enough for the bar.
- Top-5 names 2025 (share 1,314% of the year): 3MINDIA +₹4,79,000 ·
  POWERINDIA +₹3,87,170 · FORCEMOT +₹3,00,820 · PTCIL +₹2,93,090 ·
  MRF +₹2,80,380.
- Top-5 names 2026 (share 51.7%): POWERINDIA +₹4,23,880 · HONAUT
  +₹3,24,380 · SHREECEM +₹3,21,800 · SOLARINDS +₹2,74,680 · BOSCHLTD
  +₹2,65,130.
- Month table (net by entry month):
  2025 — Jan −₹46,46,970.80 · Feb +₹8,83,047.10 · Mar +₹11,76,184.40 ·
  Apr +₹22,11,640.80 · May +₹4,53,011.90 · Jun +₹12,56,741.00 ·
  Jul −₹3,86,375.90 · Aug +₹7,09,895.50 · Sep −₹71,841.40 ·
  Oct −₹14,52,872.90.
  2026 — Jan −₹7,33,344.40 · Feb −₹4,04,710.70 · Mar +₹20,93,314.80 ·
  Apr +₹4,89,796.50 · May +₹16,36,444.80 · Jun +₹15,83,924.20 ·
  Jul +₹5,01,884.70 · Aug −₹27,65,314.30 · Sep −₹9,48,784.20 ·
  Oct +₹16,60,089.10.

## Raw run (all names, no gate)

| Year | Trades | Net | WR | Ex-top-3 | Ex-top-10 | Max DD | Names |
|---|---|---|---|---|---|---|---|
| 2025 | 6,939 | **−₹7,83,283.90** | 61.0% | −₹18,38,460.90 | −₹31,25,540.90 | −₹53,33,028.00 | 2,137 |
| 2026 | 8,667 | **+₹27,70,226.00** | 61.9% | +₹15,11,096.00 | +₹1,66,306.00 | −₹53,84,201.70 | 2,528 |

Unscreened, 2025 loses money outright — the liquidity gate is what turns
2025 positive, and (above) what it turns it into is a concentrated result,
not a proven one. Raw month extremes: 2025 best Apr +₹23,31,523.90, worst
Jan −₹59,74,837.10; 2026 best Mar +₹23,84,933.00, worst Aug
−₹36,33,442.40. (Full month tables in `wide_daily_results.json`.)

## A basis fact the reader must hold

Everything is per 100 shares, so a single trade in a high-priced share
moves lakhs: the biggest winners above are ₹2.7–4.8 lakh each, and the
worst single trades are −₹6,61,090 (2025) and −₹12,39,040 (2026) — the
same in both runs. The wide totals are therefore dominated by expensive
shares at both tails; they are not comparable to a per-rupee-deployed
return, and the frozen-25 book (mid-priced names) never shows swings of
this size.

## November 2026 slice (Nov 2–13 entries; descriptive only, never in the year totals)

- Raw: 162 entries — 76 closed, +₹2,13,198.40; 86 still open at the
  Nov 13 close, marked −₹28,390.00. A further 789 positions entered before
  Nov 2 were still open, marked −₹51,05,232.00.
- Screened: 98 entries — 40 closed, +₹2,16,676.10; 58 still open, marked
  −₹15,104.00. A further 505 earlier positions still open, marked
  −₹46,17,231.00.
- Open marks are the sim's forced marks at the data end (2026-11-13
  close), not exits the rules chose.

## Files (Part 2)

- `wide_daily_run2.py` — the Part 2 driver (control re-check on the
  official-close anchors, chunked wide scoring, finalize/merge).
- `wide_daily_results.json` — Part 1 blocks preserved; added:
  `official_close_control` (passed), `data`, `raw`, `screened` (with
  placebo), `verdict`.
- `wide_daily_trades.csv` — the Part 1 CONTROL25_PARQUET rows (729)
  followed by the wide runs, run-labelled: RAW (54,107 trades) and
  SCREENED (30,166 trades).
- `wide_daily_chunk_*.json`, `wide_daily_part2_checkpoint.json` — the
  per-stage checkpoints the run was built from.
