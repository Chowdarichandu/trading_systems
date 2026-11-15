# trading_systems — PRIVATE backup

Everything built for Chandu's trading programme in one place, so nothing is lost:
Bank Nifty and Nifty **index option buying**, **equity-cash stocks**, the research
programmes around them, and the investing screener. This repository is a snapshot
backup of the live workspace (`~/workspace/trading`), pushed through the GitHub
connector's snapshot flow. It is **private** — only the owner and Muse know it exists.

**Start here:** [STRATEGIES.md](STRATEGIES.md) — every strategy with what it does,
how to use it, when to use it, its status and its headline numbers.
[RUNBOOK.md](RUNBOOK.md) holds the November paper runbook;
`november_paper_MAP.md` is the master map of the running system;
`segment_floor_tracker.md` tracks the per-segment targets
(₹20,000/month per segment target, ₹15,000/month floor, judged per segment, never pooled).

## Basis conventions (read before quoting any number)

- **Index options:** premium rupees per **1 lot** (Bank Nifty 30, Nifty 65), ₹220/trade cost, UNIQUE-ONCE counting, paper only.
- **Stocks:** equity cash, provisional per **100 shares** (a cash-translation unit, never a lot), ₹40/trade cost, paper only.
- A number is only quotable after its controls + timing/leak audit pass in the same run (the controls gate, below).

## Layout (flat root)

- **Scorers and builds** — `*.py`: live/paper scorers (`*_score.py`), research builds (`*_build.py`), fetchers.
- **Specs** — `*_SPEC.md`, `*_frozen.md`: the rules of each book, frozen before scoring. A spec never changes after its run.
- **Reports** — programme reports (`*_2026-11-*.md` and the older dated reports): what was tested, the gate result, the numbers.
- **Result books** — `*_results.json` + `*_trades.csv`: the full trade lists behind every quoted number. Any number can be re-derived from these.
- **Paper logs** — `november_*_log.csv`, `stocks_sarvaritu_paper_log.csv`, shadow ledgers: the forward (November) record, one row per trade or scored day. Legs that cannot be computed are recorded NOT_COMPUTED / UNSCORED with the reason — never estimated.
- **Registries** — `trio_strategy.md` · `ekam_strategy.md` · `dial_programme.md`: the one-name programmes and their standing.
- **Legacy engine output** — `v2_out/`, `v3_out/`: the frozen stocks-engine cycles.
- **Not in this repo:** market-data caches (`data/`, `*_data/`, `*_cache*/`, history stores — ~700 MB, regenerable from the broker API) and all credentials (`upstox_refresh/`, `.env`, token files). The `.gitignore` enforces both, permanently.

## The daily chain (IST, Mon–Fri, trading days)

| Time | Job |
|---|---|
| 03:45 | Upstox token refresh |
| 08:00 / 08:05 | Token check / rescue |
| 09:08 | Live loop morning start |
| Market hours | Intraday watcher (every 1 min — announces entries/exits); option-chain archiver (every 5 min) |
| 15:20 | Index paper logging |
| 15:32 | Shadow scoring (stack / v21 / v22 / skill / DEC-S1 lines) |
| 15:45 | Daily stats to the combined-view chat |
| 16:05 | Evening monitor |
| 16:35 | Stock Book end-of-day logging |
| 17:15 / 17:32 / 17:47 | Segment engines — Bank / Nifty / Stocks (score-only) |
| 18:05 | OI-V3 fragment shadow |
| 18:20 | R4-D1 fragment shadow |
| 18:35 | REGIME-REV shadow (Bank) |
| 18:50 | **Bank repaired lead scorer (TRIO: stack + B-FIX-1)** |
| 19:05 | **Nifty repaired lead scorer (TRIO: TUNED v1 + N-FIX-1)** |
| 19:20 | Bank confidence-gate shadow |
| 19:35 | Nifty TUNED v2 shadow |
| 19:50 | Premium-tape P-RET-120 shadow (Bank) |
| 20:05 | EKAM intraday shadows (CAND-T5 + S2, stocks) |
| 20:20 | HOLD L35-H15 shadow (stocks) |

## Safety rules (standing, owner-set)

- **Paper only.** Real money is ₹0 until the owner decides otherwise (the December live decision is taken at the 2026-11-30 verdicts).
- **Option BUYING only.** Premium selling / short options are banned everywhere, December included (owner, 2026-11-13: "we are option buyers not seller").
- **1 lot only.** No lot increase to chase returns. Spot is trigger/levels only, never the traded instrument.
- **Controls gate:** no number is quoted before the full gate passes in the same run — timing audit, feature-timing audit, placebos, halves, month table, ex-top-3, independent re-sum. Pre-registered pass bars never move; a failed variant is never retested identically.
- **Segments are reported separately** — Bank / Nifty / Stocks are never pooled into one profit verdict.
- **Circuit breaker** (`circuit_breaker.py`, `circuit_breaker_stack.py`) for the December/live layer: MTD ≤ −₹5,000 → pause rest of month · 3 consecutive losing days → pause 3 · fall ≥ ₹5,000 from the month's peak MTD → pause rest of month. Worst-10-day burn with the brake at 1 lot: Bank −₹5,160 / Nifty −₹6,940.
- **No new book arms** without the owner's explicit approval after proof. Score-only shadows collect forward evidence; promotion needs a fresh full gate plus the owner's word.

## Key dates

- **2026-11-16** — TRIO repaired lines lead November paper; all evening shadows live.
- **2026-11-20** — Stack vs legacy checkpoint (report only, no title flip).
- **2026-11-30** — November verdicts per segment; December adoption decisions; the live-money decision.
