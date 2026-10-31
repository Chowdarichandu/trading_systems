# Stocks — Line U1 report: 11:00 Fade on the broad universe, last 60 trading days

**Universe: target = 501 names (Nifty 500 constituent list as published by NSE, retrieved 2026-10-31) vs achieved = 500 names** (the one drop is a placeholder row inside NSE's own file — see Build log). **Window: 60 trading days, 2026-08-05 → 2026-10-30.** **Verdict up front: the fade does NOT survive the whole market — over these 60 days it loses ₹55,551.83 net on 7,184 trades, and the FOLLOW control on the identical trades makes +₹67,024.68. The effect is a large-cap phenomenon, not a market-wide one.**

Equity cash intraday only, LONG/SHORT. **Paper only — real money
₹0, no orders placed.** Every figure is **provisional per 100
shares, ₹40/trade flat cost**. The rule is the frozen O2
candidate, verbatim (`stocks_U1_frozen.md`): measure the move
from the 09:30 bar's open to the last bar before 11:00; if
|move| ≥ 1.0%, enter at the 11:00 bar's open AGAINST the move;
target +1.25% / stop −0.65%, square-off 15:10. One trade per
stock-day. Window: the last 60 trading days ending Fri
2026-10-30 (exact start date stated when the build completes).

---

## Build log

- 2026-10-31: freeze written (`stocks_U1_frozen.md`) before any
  data was fetched.
- Constituent list: NSE's published Nifty 500 CSV retrieved —
  501 rows / 501 unique symbols (496 EQ series, 2 BE series,
  3 REIT RR series); instrument key per name = `NSE_EQ|<ISIN>`
  from the same file. All 25 ext large caps are in the list.
- Fetch path: Upstox v3 historical-candle, 5-min bars, one
  calendar month per call (the endpoint rejects longer spans),
  2026-08-01 → 2026-10-30, via the registered connector — the
  same path every prior line used.

- Fetch complete: **500 of 501 names built** (5-min bars,
  2026-08-01 → 2026-10-30; 499 names carry the full 62 trading
  days of the span, 1 carries 61). The one dropped name is
  **DUMMYHEG** — the published CSV itself contains it as a
  placeholder row ("Dummy HEG Ltd.", ISIN DUM545A01024, not a
  real ISIN); it has no Upstox instrument and returns 400 on
  every attempt. Dropped and counted, per the freeze.
- Scoring runs the identical O1 fixed-mode builder as the O2
  candidate (fade + follow control), with the built-in timing
  audit plus an independent re-derivation of every trade.

## Results

**Timing audit — CLEAN.** Built-in builder audit: 7,184 fade
trades and 7,184 follow trades, **0 violations**. Independent
re-derivation of every trade's qualifier, direction and entry
bar from the raw bars: 7,184 + 7,184 checked, **0 violations**.
Every entry is the 11:00 bar's open, strictly after the
measurement completes. The rule as scored is real-time
executable, exactly as in the O2 freeze.

### The fade, broad universe (500 stocks, 60 days)

| | Trades | Net ₹ |
|---|---|---|
| **Total** | **7,184** | **−55,551.83** |
| Aug (from Aug 5) | 1,778 | +73,546.06 |
| Sep | 2,245 | −181,381.95 |
| Oct | 3,161 | +52,284.06 |
| First 30 days (Aug 5 – Sep 16) | 2,980 | −108,976.75 |
| Last 30 days (Sep 17 – Oct 30) | 4,204 | +53,424.92 |

- **Expectancy: −₹7.73 per trade** after the ₹40 cost. Before
  costs the fade grosses +₹231,808.17 (+₹32.27/trade) — the
  gross edge is real but thinner than the cost line at this
  breadth, and it is not stable: September alone is −₹181k.
- **Breadth: 176 of 500 stocks net-positive.** The median
  stock loses.
- **Monthly run-rate over the 60 days: ≈ −₹18,517/month**
  (net / 3). There is no positive run-rate to quote.
- Biggest positive contributors: PTCIL +₹137,877.90,
  SOLARINDS +₹96,229.25, SHREECEM +₹86,660.25 — top-3 sum
  +₹320,767.40, top-10 sum +₹643,456.80. (Shares of the total
  are not meaningful against a negative net; the sums are the
  honest form. Note both tails are dominated by high-priced
  stocks — the per-100-shares basis scales with price.)
- **Worst stock: APARINDS −₹143,765.85** (23 trades), then
  NEULANDLAB −₹134,239.55 and POWERINDIA −₹99,718.50. One
  stock's losses exceed the whole book's net loss.

### FOLLOW control — the decisive comparison

Same 7,184 qualifying stock-days, same entries and exits,
direction WITH the morning move instead of against it:
**+₹67,024.68 net** (gross +₹354,384.68). Follow beats fade by
₹122,576.51 — identical before and after costs, since the
trade count is the same. **On the broad universe, the 11:00
move continues more profitably than it fades — the opposite
of the large-cap behaviour.** The control leg of the freeze
fails the fade.

### October slice, honestly placed

Broad-universe October: **+₹52,284.06 on 3,161 trades.** The
ext-25 October anchor is +₹98,153.17 on 104 trades — the 25
large caps alone contributed **more than the entire
500-stock October net**; the other ~475 names netted
−₹45,869.11 in October.

### Consistency check — ext-25 subset inside this broad run

The 25 large caps, cut out of this run's own trades:

| Month | Trades | Net ₹ | vs O2 record |
|---|---|---|---|
| Aug (from Aug 5) | 26 | +15,642.28 | see note |
| Sep | 32 | −2,150.16 | **exact** |
| Oct | 104 | **+98,153.17** | **exact to the paisa** |
| Window total | 162 | +111,645.29 | |

September and October reproduce the O2 candidate's record
exactly — same engine, and this build's native 5-min bars for
Oct 29–30 land on the same numbers as O1/O2's validated
1-min aggregation. The August gap is a window boundary, not
a discrepancy: O2's August includes Aug 3–4 (6 trades,
+₹8,872.45), which fall outside U1's 60-day window;
15,642.28 + 8,872.45 = 24,514.73 = O2's August, to the paisa.
Within the window the ext-25 breadth is 13/25, and the ext 25
netted +₹111,645.29 while the remaining 475 names netted
**−₹167,197.12**.

## Verdict

**The 11:00 fade does not survive contact with the whole
market.** Over the last 60 trading days on 500 stocks it is
net-negative (−₹55,551.83), negative in the first half and
deeply negative in September, positive in only 176 of 500
names, and — decisively — it loses to simply following the
same morning moves on the identical trade set. Whatever the
fade is, it is a **large-cap** behaviour: the 25 ext names
kept making money inside this very run (+₹111,645.29 over
the window, October exact) while everything outside them
lost more than they made. Broadening the universe multiplies
the trade count (~120/day) without adding expectancy — the
per-trade edge that exists in large caps dilutes below the
₹40 cost line in the wider market.

Per the freeze, this line changes nothing about the O2
candidate's own December test, which judges the ext-25 rule
on fresh December data. What U1 removes is any claim that
the fade is a whole-market effect, and any case for running
it beyond the large caps.

Files: `stocks_U1_frozen.md` (freeze), `stocks_U1.py`
(scorer), `stocks_U1_fetch2.py` (build), `stocks_U1_results.json`,
`stocks_U1_fade_trades.csv`, `stocks_U1_follow_trades.csv`,
data under `data/u1/` — all in ~/workspace/trading/.
