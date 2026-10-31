# Stock system continued to satisfaction — S2, S3, S4, S5

**Date:** 2026-10-29 evening. **User instruction:** "Continue until you feel satisfied."
**Paper only, no orders, no live trading, cash intraday only, NO options.**
**Window for every number below:** Jan–Oct 2026, October = 1–28 Oct only, 25 stocks,
cache in `~/workspace/trading/data/progressive/` (5,075 stock-days, 44 ISO weeks).
**All Jan–Oct runs are in-sample context only. NOTHING below is adopted.**

## Verdict up front

**No candidate passes the satisfaction bar. Three further iterations (S3, S4, S5) all failed,
so iteration stops here per the brief.**

- **Best kept: S2** — least negative net (−₹785.98, expectancy −₹12.88), closest to break-even,
  but it still fails 4 of 5 legs (see §3). S3/S4/S5 are worse on net than S2, so loosening
  further in those directions did NOT help.
- **There is therefore NO passing candidate for November adoption-track paper.**
  S2 is the frozen reference that may be logged in November as a diagnostic only (it was
  frozen first, for November, before scoring); November alone cannot adopt a system that
  already failed in-sample on net, frequency, direction/setup diversity and full-target rate.
  A genuinely new direction — not another room/Nifty/cap tweak — is needed before any
  stock system is put on an adoption track. The most promising lead is in §5.

## 1. What was frozen

Each version was frozen in its own file **before** scoring, one filter change at a time.
Common to all (from S1, unchanged throughout): setups 2/3/4 only (Setup 1 skipped),
second-close confirmation, structural stop (CE: OR low −0.1% of prev close; PE: OR high
+0.1%), give-back exit (50 shares at 1× risk, rest trailed to breakeven, target entry ±2× risk),
no re-entry, cap 3 stock trades/week, 1/stock/week, prospective target ≥ ₹500,
100 shares, ₹40/trade, 15:10 square-off, cash intraday only.
No timing gates, no OR-high stop, no bounce-bar stops, no target-shrink were used.

| Version | Frozen file | One change from previous | Engine parameters |
|---|---|---|---|
| S2 | `new_stock_system_s2_frozen.md` | Room ≥1.5× risk (was ≥2× in S1); Nifty confirmation OR-side → bias-only (CE on bullish/neutral, PE on bearish/neutral, block only directly opposed; bands bearish <35%, neutral 35–79%, bullish ≥80%) | room_min=1.5, nifty=bias_only, cap=target |
| S3 | `new_stock_system_s3_frozen.md` | Room ≥1.25× risk (was 1.5×) | room_min=1.25, nifty=bias_only, cap=target |
| S4 | `new_stock_system_s4_frozen.md` | Nifty bias relaxed: opposed direction allowed only if room ≥2× risk | room_min=1.25, nifty=bias_relaxed_room2, cap=target |
| S5 | `new_stock_system_s5_frozen.md` | Cap ranking room-ratio DESC first (was target-net DESC) | room_min=1.25, nifty=bias_relaxed_room2, cap=room |

Engine: `stock_system_continued.py` (`run_version` / `cap_select` / `summarise`).
Trade CSVs: `s2_trades_jan_oct_2026.csv`, `s3_trades_jan_oct_2026.csv`,
`s4_trades_jan_oct_2026.csv`, `s5_trades_jan_oct_2026.csv`, plus matching
`*_uncapped_jan_oct_2026.csv` and month JSONs under `data/progressive/*_summary_2026-jan-oct.json`.

## 2. Results — Jan–Oct 2026 in-sample, capped

| Series | Trades | Win net>0 | Full-target rate | Net ₹ | Expectancy ₹ | Freq/week |
|---|---|---|---|---|---|---|
| **S1 (baseline, frozen)** | 18 | 50.0% | 22.2% (4) | **−₹1,875.94** | −₹104.22 | 0.42 |
| **S2** | 61 | 59.0% | 19.7% (12) | **−₹785.98** | −₹12.88 | 1.39 |
| **S3** | 73 | 54.8% | 19.2% (14) | **−₹4,014.07** | −₹54.99 | 1.66 |
| **S4** | 77 | 54.5% | 19.5% (15) | **−₹4,454.31** | −₹57.85 | 1.75 |
| **S5** | 77 | 54.5% | 19.5% (15) | **−₹3,895.61** | −₹50.59 | 1.75 |
| V4 stocks (capped-v2, same window, for comparison) | 132 | — | 22.7% | −₹17,435 | −₹132 | ~3.0 |
| Skill stocks (capped-v2, same window) | 143 | — | 22.4% | −₹21,835 | −₹153 | ~3.3 |

Every S2–S5 version beats S1, V4 stocks and Skill stocks on net (smaller loss), but
**none is net positive**, so none beats them in the sense that matters. The net>0 win
rates (54–59%) are NOT comparable to the old target-based win rates: they include
partial-breakeven wins (partial 50 at 1× risk, rest stopped at breakeven = small positive
after cost). Full-target rate is the comparable figure, and it is **below S1 in every
new version**.

### Month-by-month net ₹ (capped) — cumulative does NOT rise month by month in any version

| Month | S2 trades / net / cum | S3 net / cum | S4 net / cum | S5 net / cum |
|---|---|---|---|---|
| Jan | 7 / −₹763.75 / −₹763.75 | −₹763.75 / −₹763.75 | −₹221.60 / −₹221.60 | +₹1,307.46 / +₹1,307.46 |
| Feb | 8 / −₹604.70 / −₹1,368.45 | −₹1,817.85 / −₹2,581.60 | −₹1,835.19 / −₹2,056.79 | −₹1,835.19 / −₹527.73 |
| Mar | 7 / −₹1,026.74 / −₹2,395.19 | −₹1,462.69 / −₹4,044.29 | −₹1,462.69 / −₹3,519.48 | −₹2,009.43 / −₹2,537.16 |
| Apr | 9 / +₹121.80 / −₹2,273.39 | −₹967.20 / −₹5,011.49 | −₹967.20 / −₹4,486.68 | −₹288.97 / −₹2,826.13 |
| May | 4 / −₹1,114.46 / −₹3,387.85 | −₹1,114.46 / −₹6,125.95 | −₹1,333.41 / −₹5,820.09 | −₹1,968.34 / −₹4,794.47 |
| Jun | 4 / −₹697.40 / −₹4,085.25 | −₹756.53 / −₹6,882.48 | −₹756.53 / −₹6,576.62 | −₹756.53 / −₹5,551.00 |
| Jul | 6 / +₹2,434.45 / −₹1,650.80 | +₹2,594.91 / −₹4,287.57 | +₹2,594.91 / −₹3,981.71 | +₹2,594.91 / −₹2,956.09 |
| Aug | 6 / −₹93.52 / −₹1,744.32 | −₹1,537.52 / −₹5,825.09 | −₹1,537.52 / −₹5,519.23 | −₹1,537.52 / −₹4,493.61 |
| Sep | 8 / +₹1,459.97 / −₹284.35 | +₹1,459.97 / −₹4,365.12 | +₹713.87 / −₹4,805.36 | +₹246.95 / −₹4,246.66 |
| Oct (1–28) | 2 / −₹501.63 / −₹785.98 | +₹351.05 / −₹4,014.07 | +₹351.05 / −₹4,454.31 | +₹351.05 / −₹3,895.61 |

### March / October dependence check

| Version | Full net ₹ | Ex-March net ₹ | Ex-October net ₹ |
|---|---|---|---|
| S2 | −₹785.98 | **+₹240.76** | −₹284.35 |
| S3 | −₹4,014.07 | −₹2,551.38 | −₹4,365.12 |
| S4 | −₹4,454.31 | −₹2,991.62 | −₹4,805.36 |
| S5 | −₹3,895.61 | −₹1,886.18 | −₹4,246.66 |

S2 is the only version whose ex-March total is positive — but that is March-dependence
in reverse (a single −₹1,027 March drags a near-breakeven system negative), not a pass:
ex-October S2 is still negative, and S2's cumulative still falls Jan–Jun before Jul/Sep recoveries.
No version is March- or October-carried to a positive total.

## 3. Satisfaction bar — leg by leg

Bar (all together): (a) net positive; (b) frequency ~2–3 stock trades/week;
(c) CE trades AND setup2/4 trades present (not all PE shorts);
(d) full-target rate above S1's 22.2%, partial-BE wins not counted as targets;
(e) at least some trades from the 14 zero-trade S1 stocks, or a stated per-stock reason.

| Leg | S2 | S3 | S4 | S5 |
|---|---|---|---|---|
| (a) Net positive | ✗ −₹785.98 | ✗ −₹4,014.07 | ✗ −₹4,454.31 | ✗ −₹3,895.61 |
| (b) ~2–3/week | ✗ 1.39 | ✗ 1.66 | ✗ 1.75 | ✗ 1.75 |
| (c) CE + setup2/4 present | ✗ CE 0, setup2 0, setup4 0 — all 61 setup3 PE | ✗ CE 1, setup4 1, setup2 0 | ✗ CE 1, setup4 1, setup2 0 | ✗ CE 1, setup4 1, setup2 0 |
| (d) Full-target > 22.2% | ✗ 19.7% | ✗ 19.2% | ✗ 19.5% | ✗ 19.5% |
| (e) S1 zero-stock trades | ✓ 12 trades, 4 symbols (HDFCBANK, HINDCOPPER, HINDUNILVR, KALYANKJIL) | ✓ 13 trades, same 4 symbols | ✓ 13 trades, same 4 symbols | ✓ 12 trades, same 4 symbols |

Only leg (e) passes, and only narrowly: the same 4 of the 14 zero-trade stocks ever trade
in any version. The other 10 (HINDUNILVR trades, so the remaining zero list is: IRCTC, ITC,
NATIONALUM, NHPC, NTPC, OIL, PFC, RECLTD, TATASTEEL, WIPRO — plus, in S2, the traded set is
14 stocks total) never produce a capped trade under any S2–S5 filter. Per-stock reason is
in §5: it is not the cap, it is the signal/room stack.

## 4. Filter funnels (5,075 stock-days scanned in every version)

| Stage | S1 | S2 | S3 | S4 | S5 |
|---|---|---|---|---|---|
| Stock-days scanned | 5,075 | 5,075 | 5,075 | 5,075 | 5,075 |
| OR filter passed | 4,859 | 4,859 | 4,859 | 4,859 | 4,859 |
| Old V4 signal found | 910 | 910 | 910 | 910 | 910 |
| Second-close passed | 443 | 443 | 443 | 443 | 443 |
| Finite room passed | 140 (≥2×) | 179 (≥1.5×) | 205 (≥1.25×) | 205 (≥1.25×) | 205 (≥1.25×) |
| Nifty confirmation passed | 38 (OR-side) | 167 (bias-only) | 190 (bias-only) | 201 (bias-relaxed) | 201 (bias-relaxed) |
| Prospective target ≥ ₹500 | 19 | 74 | 86 | 92 | 92 |
| After cap (3/week, 1/stock/week) | 18 | 61 | 73 | 77 | 77 |

Reading: loosening room and Nifty confirmation **did** unblock the funnel (19 → 74 → 86 → 92
candidates), and frequency rose (0.42 → 1.39 → 1.66 → 1.75/week), but the extra trades
were predominantly losing setup3 PE trades — net got worse from S2 to S3/S4, and cap
ranking (S5) only recovered ₹559 of S4's loss. The funnel was not the edge; the
candidates it admits are.

## 5. Why CE and setup2/4 never survive — the structural finding

This is the finding that stops further room/Nifty/cap tweaking from being satisfying:

- Raw V4 signals (OR-filtered, Jan–Oct): setup3 PE 589, setup4 reclaim CE 221,
  setup2 breakdown PE 92, setup4 pullback CE 5, setup2 breakout CE 3 (total 910).
- After second-close: setup3 PE 298, setup4 CE 96, setup2 PE 45, setup4 pullback CE 3,
  setup2 CE 1 (total 443).
- After room + Nifty + target + cap (S2): setup3 PE 61, everything else 0.
  After all S3–S5 loosening: still only 1 setup4 CE trade in total, 0 setup2 trades.

Mechanism (stated as the best-supported explanation, not a proven per-trade cause):
for a CE reclaim trade, entry is typically already near the OR high, so the structural
stop (OR low −0.1%) makes risk ≈ the whole OR width, while room to the next PD level
above (usually PDH, close above) is often <1.25–1.5× that risk. For a setup3 PE bounce
at the OR high, entry is near the stop (OR high +0.1%), so risk is small and room down
to PDC/PDL is large. The structural stop + room filter therefore **systematically
favours PE bounce trades and systematically filters out CE trades**, regardless of
whether the CE direction was right. Loosening room to 1.25× admits more PE trades
(whose risk is already small) without rescuing CE trades (whose risk is OR-width-sized).
Any future stock design must address this asymmetry directly — e.g. a CE-specific
stop/room definition, or a different CE entry (pullback to OR low rather than reclaim
at OR high) — and that is a **new design, not a one-filter tweak**, so it was not
attempted inside this S3–S5 round, which was restricted to one-filter changes.

## 6. Best kept: S2 — per-stock (capped, Jan–Oct 2026)

| Stock | Trades | Net>0 | Net ₹ |
|---|---|---|---|
| BDL | 6 | 5 | +₹1,107.27 |
| GLENMARK | 6 | 4 | +₹1,290.37 |
| HINDUNILVR | 6 | 5 | +₹972.30 |
| ASTRAL | 9 | 6 | +₹635.90 |
| HINDALCO | 2 | 2 | +₹571.81 |
| KALYANKJIL | 1 | 1 | +₹110.01 |
| OBEROIRLTY | 5 | 3 | −₹151.76 |
| GODREJCP | 5 | 3 | −₹196.49 |
| HINDZINC | 3 | 1 | −₹245.05 |
| HINDCOPPER | 4 | 1 | −₹758.03 |
| HDFCBANK | 1 | 0 | −₹709.23 |
| UNITDSPR | 6 | 3 | −₹1,354.32 |
| TVSMOTOR | 6 | 2 | −₹1,998.76 |
| INDUSTOWER | 1 | 0 | −₹60.00 |
| Zero-trade in S2 (11): IRCTC, ITC, NATIONALUM, NHPC, NTPC, OIL, PFC, RECLTD, TATASTEEL, WIPRO, VEDL. (14 stocks traded in S2; 11 did not.) |

S2 exits are dominated by setup3 PE stops/partial-BE stops, as in S1; the full trade
list is in `s2_trades_jan_oct_2026.csv`.

## 7. November paper — what happens next (NOT an adoption claim)

- **No version is on an adoption track for November.** S2–S5 all failed in-sample.
- If a November stock log is run at all, log **S2 only** (the frozen-first, least-negative
  version), in the existing template `s2_forward_paper_log.csv`, daily after 15:10,
  separate from the Nifty Cluster 2/3 log, with every signal's filter stage recorded.
  Log it as a **diagnostic**, not as a candidate that November can adopt: a single
  November month cannot overturn a Jan–Oct failure on 4 of 5 legs, and no re-tuning
  during November is permitted.
- **Do not log S3/S4/S5 in November** — they are worse on net than S2 and add nothing
  except more losing PE trades.
- **Next design work (after November, or in parallel as a new frozen design, not a tweak):**
  address the §5 CE asymmetry (CE-specific stop/room or pullback entry), and/or a
  per-stock funnel for the 10 stocks that never trade. That design must be frozen
  before scoring, with Jan–Oct as in-sample context only, and its own November-style
  unseen validation before any adoption claim.

## 8. What was NOT done (guardrails kept)

- No orders, no live trading, no lot increase. Cash intraday only, no options:
  every net above is 100 shares × index/stock points minus ₹40/trade, NOT an option premium profit.
- Index and stock totals were never pooled. Nifty was a filter only, never traded in S2–S5.
- No timing gates, OR-high stop, bounce-bar stops, or target-shrink to tiny wins were used.
- Give-back exit, structural stop and target 2× risk were NOT changed in S3–S5, as instructed.
- No version was re-tuned on the same window to chase a single month: ex-March and
  ex-October totals are reported for every version, and S3–S5 worsening on net is reported
  rather than hidden by picking a favourable month.
