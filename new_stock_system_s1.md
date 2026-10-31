# S1 — New intraday STOCK system (cash, NOT options)

**Status: PROVISIONAL, FROZEN before scoring, NOT adopted, NOT a live system.
Paper only, no orders, no lot increase. November validation is the next step,
not part of this build's adoption claim.**

**Window:** Jan–Oct 2026 primary, October = 1–28 Oct only.
29 Oct 2026 is **excluded and stated separately**: it is not in the
`data/progressive/` cache used here (cache ends 28 Oct), so no S1 29-Oct
trade is claimed. A 29-Oct add-on would need fresh intraday stock data,
not a copy of the Bank Nifty/Nifty close-out verdict.

**Files:**
- Engine (frozen rules in its docstring): `new_stock_system_s1.py`
- Capped trades: `s1_trades_jan_oct_2026.csv` (18 trades)
- Uncapped candidates: `s1_uncapped_jan_oct_2026.csv` (19)
- Month JSONs: `data/progressive/s1_summary_2026-01.json` … `-10.json`,
  aggregate `s1_summary_2026-jan-oct.json`

---

## 1. The old system, plainly (what S1 leverages)

Source files: `3-blue-line-bank-nifty-backtest-spec.md`,
`jan_oct_2026_v4_and_skill.md`, `nifty_failing_cases_jan_oct_2026.md`,
clubbed / progressive reports in `~/workspace/trading/`.

**3-Blue-Line / V4, as Chandu defined it (options origin):**
- **Blue Lines** = previous day's high / close / low: PDH / PDC / PDL.
- **Red bands / ledges** = multi-day structural levels, e.g. Bank Nifty
  54,415–54,449 band, 54,744 and 54,019 ledges. Red bands are NOT supplied
  for stocks in the clubbed work, so Setup 1 was skipped there — S1 does
  the same (see §3).
- **Opening range (OR)** = 09:15–09:30 (bars before 09:30); OR high / low
  = ORH / ORL.
- **Bias** from previous day's close position in its range:
  bearish < 35%, neutral 35–79%, bullish ≥ 80%.
  Bearish → PE (short) only, bullish → CE (long) only, neutral → both.
- **Four setups:**
  1. Multi-day ceiling breakout + retest hold CE (needs Red bands).
  2. Direct OR breakout / breakdown (09:30–11:30 in the cash engine,
     OR-width cap scaled).
  3. Wide-candle (400–580 pts Bank Nifty, scaled by prev close / 55,000
     for stocks) bounce rejection PE.
  4. Gap-down bear-trap reclaim CE, plus pullback variant.
- **Filter 4 = Retest Hold Confirmation**, NOT a DTE gate. (An earlier
  assistant-invented DTE ≥ 4 gate was corrected by Chandu.)
- **Options rules (origin, NOT used for stocks):** strike ATM or 100 pts
  ITM on expiry day; stop −50 option points or setup-specific close
  stop; target +90 to +100, or book 20 points in front of the overhead
  line; one-and-done per day.
- **Provisional cash translation (NOT Chandu's rule, used in all clubbed
  / progressive runs and in S1's base signal):** 100 shares/trade,
  ₹40/trade assumed cost (not actual brokerage), entry = next 5-min open
  after the signal close, stop = signal-candle low (long) / high (short),
  target = entry ± 2 × risk, square-off 15:10, short signals paper-only,
  one trade/instrument/day. Capital was never shared, so no risk %.

**What S1 keeps from the old system:** PD levels, OR, bias filter,
setups 2/3/4, 100 shares / ₹40 / 15:10 square-off, one trade/stock/day.
**What S1 changes:** stop, confirmation, room, index filter, give-back
exit, ranking/cap — see §3. Every change is tied to a failure in §2.

---

## 2. Issues the old system actually faced (evidence, not generic claims)

**(a) Stop inside the OR.** For a 09:30–09:35 signal the signal candle's
extreme is still inside the 09:15–09:30 OR, so a modest bounce back into
the OR stops the trade. Nifty failing cases, Jan–Oct 2026
(`nifty_failing_cases_jan_oct_2026.md`): 14 of 16 stops sit inside the OR;
10 of 16 losing trades later reach the target level (8 later close beyond
it) — direction was often right, entry/stop timing failed. Cluster 1
(first OR-breakdown PE bear-trap, 8 trades, −₹24,290): stop inside OR
in all 8, stop within 1–5 bars.

**(b) Bear-trap / reclaim failures and slow give-back.** Cluster 2
(reclaim failure, setup4 CE, 2 trades, −₹11,420, incl. 26 Oct −₹8,635,
risk 85.95 pts). Cluster 3 (slow PE breakdown give-back, 3 trades,
−₹10,585): stop hit late (35, 26, 11 bars), MFE 48–83% of target — the
breakdown worked, then reversed. This is an exit-rule failure, not
entry-direction failure.

**(c) Re-entry legs losing money, Jan–Oct.** In the dual Skill+(lA)
Jan–Oct run, capped (lA) re-entry days net **−₹129,975** (22 days,
9 green) while morning-target days net **+₹153,410** (25 days).
Uncapped: 30 re-entry legs fired, day nets −₹156,125, only 11/30 green.
October alone had **zero** re-entry legs — it could not test this at all.

**(d) Cap crowding / ranking artefacts.** Dual merge Jan–Oct:
Skill + (lA) capped sum to +₹63,675, merged is −₹1,600. Setup-rank-first
ranking let rank-1 (lA) fill each 1/symbol/week slot first, so **8 Skill
trades worth +₹49,925 were dropped entirely** (e.g. Bank 13 Mar +₹27,190,
Bank 13 Jul +₹24,610); Feb and Aug merged contain zero Skill trades.
In October, Bank 23 Oct (lA) +₹24,060 was capped out by the same mechanism.

**(e) Stocks specifically.** Capped Jan–Oct 2026, verified from
`capped_v2_summary_2026-*.json`: **V4 stocks −₹17,435** (132 trades,
22.7% win), **Skill stocks −₹21,835** (143 trades, 22.4% win).
Raw (uncapped) stocks: V4 934 trades / −₹45,424, Skill filtered 1,022 /
−₹59,556 — i.e. 400–500+ trades/month in raw runs, stopped by Chandu
as too aggressive. Tiny wins that do not survive cost were a standing
complaint ("300, 400" nets = 100 shares × a 3–4 rupee move minus ₹40;
some targets net −₹8/−₹26 after cost).

**(f) March / October dependence and single-index stops swamping totals.**
V4 index Jan–Oct +₹68,770 is March-dependent (without March, −₹8,855);
V5 index +₹64,380 is March-dependent (−₹35,425 ex-March). June 2026
V4 index −₹39,000 and August −₹26,705 are single Bank/Nifty stops and
targets, not progression. Cumulative profit does not rise month by month
in any index series.

**(g) Bank mirror of (lA) failing while Nifty (lA) worked — do NOT pool
blindly.** (lA)-only Jan–Oct 2026: Nifty (original) 24 trades, 79.2%,
+₹71,780 vs Bank (mirror) 23 trades, 39.1%, −₹48,345. Triple/dual/club-all
pooled totals hid the strong Nifty leg behind the negative Bank leg.
S1 is therefore stocks-only, with Nifty used only as a confirmation
filter, never pooled into a stock total as if it were the same system.

---

## 3. S1 rules — FROZEN before scoring (provisional, NOT Chandu's rule)

Engine: `new_stock_system_s1.py` (docstring = this list).

| # | S1 rule (exact) | Issue it addresses |
|---|---|---|
| S1-1 | Base signal = old V4 `find_signal` (setups 2/3/4 only; Setup 1 skipped, no bands) + bias filter as old. | Leverages old levels, does not invent new setups. |
| S1-2 | OR filter: OR width / prev close in **[0.25%, 3.0%]**, else no-trade. | Thin/wide OR noise. |
| S1-3 | **Confirmation (second close):** candle after signal must close further in direction than signal close (CE: conf > sig close; PE: conf < sig close). Entry = open of next candle. No rescan, no re-entry that day if it fails. **Caveat / re-test:** second-close was weak on Nifty Cluster 1 PE alone (9 Jan loss −₹3,745 → −₹1,810, not green). Re-tested here because stock ORs are price-scaled differently and it is paired with S1-4/S1-6, not used alone. | First-touch false breaks (a). |
| S1-4 | **Structural stop:** CE stop = OR low − 0.1% of prev close; PE stop = OR high + 0.1% of prev close. NOT the signal candle's extreme. Risk = \|entry − stop\|. | Stop inside OR (a). |
| S1-5 | **Room filter (finite):** room to next PD level in direction must be **finite AND ≥ 2 × risk**; target = entry ± 2 × risk. No PD level beyond entry = FAIL (infinite room is never a pass). | Infinite-room artefact (d) + overhead-level stops. |
| S1-6 | **Index confirmation:** at confirmation time, Nifty's last closed 5-min candle must be on the same OR side (CE: Nifty close > Nifty OR high; PE: Nifty close < Nifty OR low). Nifty inside OR = no trade. | Stock signal against the market morning (g, applied as filter, not pooling). |
| S1-7 | **Give-back exit:** at 1.0 × risk, book **50 shares**; remaining 50 stop trails to **breakeven (entry)**; remaining target stays 2 × risk; square-off 15:10. Bar order: stop first, then partial, then target. **Caveat / re-test:** partial50_trailBE collapsed Nifty morning winners in sweep (o). Here it is 50% only, with S1-4/S1-5, and partial vs full-target splits are reported so any winner-tax is visible. | Slow give-back (b). |
| S1-8 | **No re-entry:** one signal, one trade per stock/day; no second trade after a stop. | Re-entry losses (c). |
| S1-9 | **Convicted cap:** max **3 stock trades/week**, max **1/stock/week**, prospective full-target net **≥ ₹500** (2 × risk × 100 − 40 ≥ 500 ⇒ risk ≥ ₹2.70/share — so no tiny-win fills). **Ranking for cap: prospective target net DESC, then room ratio, then setup rank** — NOT setup-rank first. | Tiny wins + cap crowding (d, e). |
| S1-10 | 100 shares, ₹40/trade, square-off 15:10, short paper-only. Win (primary) = net > 0. Full-target rate reported alongside, because old V4 win = targets/trades and a partial-BE win is not a full target. | Comparability (e). |

**Rules deliberately NOT re-used without the caveat above:** timing gates
(09:45/09:50/10:00/10:30 — best 3/8 on Nifty Cluster 1, damages winners),
OR-high stop (4/8 but total −₹31,910), bounce-bar stops, BN relative
strength (0/8, worst winner-destroyer), target-shrink to tiny wins
(rejected as noise). S1 uses none of them as its stop/exit; the only
re-tests are S1-3 and S1-7, both flagged above.

---

## 4. S1 backtest — Jan–Oct 2026, 25 stocks, cash intraday only

### Headline (capped, as frozen)

| Series | Trades | Win (net>0) | Full-target rate | Net ₹ | Expectancy | Freq/week |
|---|---|---|---|---|---|---|
| **S1 stocks (capped)** | **18** | **9 / 50.0%** | **4 / 22.2%** | **−₹1,875.94** | **−₹104.22** | **0.42** |
| V4 stocks (capped-v2, same window) | 132 | — (targets 22.7%) | 22.7% | −₹17,435 | −₹132 | ~3.0 |
| Skill stocks (capped-v2, same window) | 143 | — (targets 22.4%) | 22.4% | −₹21,835 | −₹153 | ~3.3 |
| S1 uncapped (for reference, not the system) | 19 | 9 / 47.4% | 4 / 21.1% | −₹2,691.31 | −₹141.65 | — |

**Verdict on the three legs together: FAILS.**
- Net: S1 (−₹1,876) **beats both old series on net** (loss is ~90% smaller
  than V4/Skill stocks) — but it is still negative, so it is not a
  positive system.
- Win rate: on the comparable full-target definition S1 is **22.2%**,
  essentially tied with V4 (22.7%) and Skill (22.4%) — no win-rate
  improvement. The 50.0% net>0 rate is **not** comparable to old win
  rate: 5 of the 9 net-positive trades are partial-BE wins
  (+₹108 to +₹148), i.e. the partial rule manufactures small positives.
- Frequency: **0.42/week vs ~3/week capped old** — S1 trades far too
  rarely to be a 2–3/week stock system, and far below its own 3/week cap.
  It does not beat both old series on net + win rate + frequency together.

### Month by month (capped) — cumulative does NOT rise month by month

| Month | Trades | Net>0 | Net ₹ | Cumulative ₹ |
|---|---|---|---|---|
| Jan 2026 | 2 | 2 | +₹1,302.07 | +₹1,302.07 |
| Feb 2026 | 2 | 0 | −₹892.71 | +₹409.36 |
| Mar 2026 | 1 | 0 | −₹421.09 | −₹11.73 |
| Apr 2026 | 1 | 1 | +₹127.93 | +₹116.20 |
| May 2026 | 2 | 0 | −₹864.06 | −₹747.86 |
| Jun 2026 | 2 | 1 | −₹508.60 | −₹1,256.46 |
| Jul 2026 | 1 | 0 | −₹557.30 | −₹1,813.76 |
| Aug 2026 | 5 | 3 | −₹293.07 | −₹2,106.83 |
| Sep 2026 | 2 | 2 | +₹230.89 | −₹1,875.94 |
| Oct 2026 (1–28) | 0 | 0 | ₹0 | −₹1,875.94 |

Max drawdown (chronological, capped): ₹3,853.28. October is empty —
S1 gives nothing in the month the old systems were most active in.

### Per stock (capped, 18 trades; 14 of 25 stocks have ZERO S1 trades)

| Stock | Trades | Net>0 | Net ₹ |
|---|---|---|---|
| BDL | 3 | 3 | +₹995.57 |
| HINDZINC | 1 | 1 | +₹521.77 |
| VEDL | 1 | 1 | +₹127.93 |
| OBEROIRLTY | 1 | 1 | +₹108.14 |
| UNITDSPR | 2 | 1 | −₹15.15 |
| INDUSTOWER | 1 | 0 | −₹60.00 |
| ASTRAL | 2 | 1 | −₹197.62 |
| GODREJCP | 2 | 1 | −₹249.15 |
| HINDALCO | 1 | 0 | −₹421.09 |
| TVSMOTOR | 1 | 0 | −₹621.50 |
| GLENMARK | 3 | 0 | −₹2,064.84 |
Zero-trade stocks (14): HDFCBANK, HINDCOPPER, HINDUNILVR, IRCTC, ITC,
KALYANKJIL, NATIONALUM, NHPC, NTPC, PFC, RECLTD, TATASTEEL, WIPRO, OIL.
(Count check: 11 traded + 14 zero = 25.)

### Exits (capped, 18)

Stop before partial: 8 | Stop after partial (breakeven): 5 |
Target after partial: 4 | Square-off (no partial): 1 | Square-off after
partial: 0. **All 18 trades are setup3 bounce-rejection PE (short).**
No CE trade and no setup2/4 trade survives all S1 filters in Jan–Oct 2026.
S1 as frozen is therefore a **single-setup, single-direction** system in
practice, not a general stock system — a concentration risk that must be
stated, not hidden.

### Filter funnel — why frequency collapsed (5,075 stock-days, Jan–Oct 2026)

| Stage | Count | Lost at this stage |
|---|---|---|
| Stock-days scanned | 5,075 | — |
| OR filter passed | 4,859 | 215 (OR) |
| Old V4 signal found | 910 | 3,949 (no signal) |
| Second-close confirmation passed | 443 | 467 (confirmation) |
| Finite room ≥ 2 × risk passed | 140 | 303 (room — largest filter loss) |
| Nifty OR-side confirmation passed | 38 | 102 (Nifty) |
| Prospective target ≥ ₹500 passed | 19 | 19 (target) |
| After 3/week + 1/stock/week cap | 18 | 1 (GLENMARK 11 Feb, −₹815.37, capped out) |

The cap is **not** the frequency problem — the filters are, in order:
room (303), confirmation (467 from signals, but room is the largest
*conditional* cut after confirmation), and Nifty confirmation (102).
Room ≥ 2 × structural risk is too strict for stocks whose PD levels sit
close to the entry; Nifty OR-side at confirmation time is too strict
for a stock that moves before Nifty leaves its OR.

---

## 5. Issue-by-issue: what S1 fixed, what it did not

| Issue (§2) | S1 result |
|---|---|
| (a) Stop inside OR | **Partly addressed, not solved.** Structural stop is used in all 18 trades, yet 8 stop before any partial and 5 more stop at breakeven after partial — stop-outs still dominate (13/18). Direction-right-then-stopped cannot be checked per trade here as in Nifty Cluster 1, but the stop rate did not collapse. |
| (b) Give-back | **Partly addressed.** 5 partial-BE wins (+₹108–₹148) bank something instead of a full stop, and 4 full targets survive. But partial wins are tiny and do not offset the 8 full stops; no Cluster-3-style MFE analysis was possible on 18 trades. |
| (c) Re-entry losses | **Addressed by construction:** no re-entry leg exists in S1, so no re-entry loss can occur. (This is a design removal, not a fix that turns re-entries profitable.) |
| (d) Cap crowding | **Addressed by construction + ranking change:** only 1 trade was capped out (vs +₹49,925 dropped in the dual merge). But with only 19 candidates, the cap was never really tested. |
| (e) Stocks: negative, too many trades, tiny wins | **Mixed.** Net improves from −₹17k/−₹22k to −₹1.9k and trade count collapses from 132/143 to 18 — but it overshoots into too *few* trades, and partial-BE wins are themselves tiny (+₹108–₹148). Tiny-win problem is not solved, it is re-labelled. |
| (f) March/October dependence | **Not tested / not solved.** S1 has no March spike (Mar −₹421) and no October trades at all; cumulative falls Feb–Aug and only Sep pulls it slightly back. No month-by-month rising cumulative. |
| (g) Pooling | **Addressed by scope:** S1 is stocks-only, Nifty only as a filter. No pooled Nifty+Bank+stock total is claimed. |

---

## 6. Next validation step (NOT an adoption claim)

1. **Do NOT re-tune S1 on Jan–Oct 2026 and re-claim a pass.** Any change
   (room ≥ 1.5 × risk, Nifty confirmation loosened to bias-only, CE
   signal rescue) must be frozen as S2 **before** scoring, and scored
   first on November 2026 paper (unseen), with Jan–Oct reported only as
   in-sample context.
2. If S2 is built, its first diagnostic must be the same funnel:
   it must restore CE and setup2/4 trades and reach ~2–3 stock trades/week
   **without** returning to tiny wins or infinite-room passes.
3. November paper log (separate from Cluster 2/3 log): every S1/S2 stock
   signal, filter stage it failed at (OR / confirmation / room / Nifty /
   target / cap), entry/stop/target, partial, exit, net — logged daily
   after 15:10, no scoring/re-tuning during November.
4. Stocks that never traded under S1 (14/25) need a reason per stock
   (no signal vs filter-killed), not a pooled excuse — the funnel
   above is the starting point, per-stock funnel is the S2 diagnostic.

**Bottom line:** S1 leverages the old levels correctly and cuts the old
stock loss by ~90%, but it is a **failed system as frozen**: negative net,
tied full-target win rate, 0.42 trades/week, single-setup/single-direction
(setup3 PE only), zero trades in October. It is useful as a diagnostic
— it proves the room + Nifty-confirmation stack is too strict for stocks
— not as a system to trade, paper-forward as-is, or tune in-sample.
