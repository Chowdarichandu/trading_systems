# STRATEGIES — every book: what it does, how to use it, when to use it

Status as of 2026-11-15. Money bases: index = premium ₹ per 1 lot (Bank 30, Nifty 65, ₹220/trade); stocks = equity cash per 100 shares provisional (₹40/trade). Paper only, real money ₹0 everywhere. Segments are never pooled.

---

## LEADS — TRIO (from Mon 2026-11-16)

TRIO is one name for the three repaired lead books together (registry: `trio_strategy.md`). Date-wise results: `trio_daily_results_2026-11-14.csv/.md`; month-wise with EKAM: `trio_ekam_monthly_results_2026-11-15.md/.csv`.

### 1. TRIO Bank — TUNED STACK v2 + B-FIX-1 (Bank Nifty options)
- **What:** The tuned multi-leg option-buying stack (Jan–Oct gate PASS: +₹127,351.50, 111 legs, WR 59.5%, zero red months) plus one repair: skip a leg when side = PE **and** the overnight gap is down **and** entry premium is ₹500–800 — the only entry-knowable losing cell (17 legs, −₹4,158.50).
- **How:** scorer `bank_bfix1_score.py` → ledger `november_repaired_bfix1_bank_log.csv`; job `bank-bfix1-scorer-daily` 18:50 IST Mon–Fri. The raw stack scores untouched beside it as the control.
- **When:** This is the Bank **lead line** for November paper. Repaired Jan–Oct: **+₹131,510** (beats 200/200 random stand-down placebos). November counterfactual −₹3,440 vs the raw stack's −₹2,680 — the repair's real test is the Nov 16–30 forward window.

### 2. TRIO Nifty — TUNED v1 + N-FIX-1 (Nifty options)
- **What:** TUNED v1 (EVE-07; Jan–Oct +₹103,050.25, 74 legs, gate PASS) plus one repair: skip a leg when side = CE **and** the overnight gap is up — its rotten cell (8 legs, −₹14,119.75, WR 12.5%).
- **How:** scorer `nifty_nfix1_score.py` → ledger `november_repaired_nfix1_nifty_log.csv`; job `nifty-nfix1-scorer-daily` 19:05 IST Mon–Fri. C3G7, raw v1 and DEC-S1 score beside it as controls.
- **When:** This is the Nifty **lead line** for November paper. Repaired Jan–Oct: **+₹117,170** (beats 199/200 placebos). November counterfactual ₹0 vs v1's actual +₹3,036.50 — again, Nov 16–30 decides.

### 3. TRIO Stocks — the raw Stock Book (equity cash)
- **What:** The frozen 25-name intraday equity book (components F4, INV-LONG, INV-ABOVE, N4-V3, P2F, P2F-R2, R2-LOWBAND). Its repairs (S-FIX-1, S-FIX-2) and its confidence filter both FAILED their gates — no rotten cell exists; the book bleeds evenly — so TRIO's stocks line is the raw book, unchanged.
- **How:** logger `stocks_sarvaritu_logger.py`; log `stocks_sarvaritu_paper_log.csv`; EOD job 16:35 IST. (User-visible name is "Stock Book" only; internal `sarvaritu_*` file names are unchanged.)
- **When:** The stocks **lead line**, running as-is. 2025 **+₹1,19,813.44** · 2026 Jan–Oct **+₹2,47,178.79** · November +₹7,517.94 (32 trades).

---

## CONTROLS — score beside the leads, never traded as leads

### 4. Bank legacy BNF-PAPER-V1 (B2 + NS1)
Frozen v21-frame control line. Jan–Oct **+₹83,650.50**; November −₹1,920 (6 trades). Scored in the 15:32 shadow chain; log `november_shadow_v21_bank_log.csv` family. The Nov 20 checkpoint compares stack vs legacy — report only, no title flip.

### 5. Bank TUNED STACK v2 (raw)
The unrepaired stack — TRIO Bank's control from Nov 16. Jan–Oct +₹127,351.50; November −₹2,680 (4 legs). Scorer `bank_tuned_stack_live_score.py` / `november_shadow_score.py`; logs `november_paper_bank_log.csv`, `november_shadow_stack_bank_log.csv`.

### 6. Nifty NF-PAPER-C3G7
The November primary turned control. November −₹3,470 (1 trade). Its own Jan–Oct table was never scored — not auditable, not a December candidate. Log `november_paper_nifty_log.csv`.

### 7. Nifty TUNED v1 (raw)
TRIO Nifty's control. Jan–Oct +₹103,050.25; the only positive Nifty November line (+₹3,036.50, 1 leg).

### 8. Nifty DEC-S1
**Retired as a December candidate** (proven leak: component-B PE legs −₹11,881.75). Control/scoring line only. Jan–Oct +₹91,168.50 (97 legs, two legs failed-and-waived). November −₹443.50. Log `november_shadow_decs1_nifty_log.csv`.

---

## SHADOWS — score-only forward evidence (all review at the 2026-11-30 verdicts)

A shadow never trades and never changes a running book. Promotion needs forward support + a fresh full gate + the owner's explicit word.

### 9. Bank confidence gate (Phase-2, score ≥ 0.5)
- **What:** A confidence score on stack legs; trade only the confident ones. Kept 88/111 legs for **+₹122,337.50** Jan–Oct (96.1% of the book), WR 62.5%, ₹1,609.70/trade-day, zero red months, placebo 97th pct. November counterfactual **+₹760** vs −₹2,680 actual — the only November-positive Bank line.
- **How:** `bank_confgate_shadow_score.py` → `november_shadow_confgate_bank_log.csv`; job 19:20 IST.
- **When:** Watch line inside TRIO. **Bank-only** — the same idea failed outright on Nifty and on Stocks (their edges are payoff-shaped, not selection-shaped).

### 10. Nifty TUNED v2 (EVE-11)
- **What:** The second tuned Nifty book: **+₹115,950.75** Jan–Oct (59 legs), the cleanest ₹900-trade-day pass (₹2,273.54/trade-day, WR 59.3%, zero red months, placebo 100th pct). Zero November legs so far.
- **How:** `nifty_tunedv2_shadow_score.py` → `november_shadow_tunedv2_nifty_log.csv`; job 19:35 IST.
- **When:** Shadow candidate; the v1-vs-v2 lead question is decided at Nov 30, not before.

### 11. REGIME-REV (Bank)
- **What:** Buys the opposite side after a post-11:00 reversal day-shape. Standalone gate PASS: 31 legs, **+₹15,872** — but ₹512/trade-day is below the ₹900 bar and its merge into the stack failed (−₹2,808 increment).
- **How:** `regime_rev_shadow_score.py` → `november_shadow_regimerev_bank_log.csv`; job 18:35 IST.
- **When:** Shadow only. November counterfactual +₹2,141.

### 12. OI-V3 (Bank fragment)
- **What:** Day-level open-interest signal used only on days the stack is idle: increment 42 legs +₹3,360 (merged stack+V3 = ₹130,711.50, but the increment's halves flip).
- **How:** `oi_v3_shadow_score.py` → `oi_v3_shadow_log.csv`; job 18:05 IST. Review after 20 scored opportunities or 2026-12-31.
- **When:** Fragment shadow — evidence for a possible future merge, nothing more.

### 13. R4-D1 (Bank fragment, strongest)
- **What:** Intraday futures-basis morning read, again only on stack-idle days: increment 27 legs **+₹8,973** → merged ₹136,324.50, zero red months, both halves positive. The 11:00 entry window itself carries value (12:00 placebos collapse).
- **How:** `r4d1_shadow_score.py` → `r4d1_shadow_log.csv`; job 18:20 IST.
- **When:** Lead fragment shadow. A Nifty twin exists (+₹13,264.50 increment, ex-top-3 negative — secondary).

### 14. Premium-tape P-RET-120 (Bank)
- **What:** Signals from the **option premium's own chart**, not spot: after a premium-VWAP break, buy only when the premium retests and holds within a 120-minute window. 58 trades, **+₹16,692.50** Jan–Oct, positive in both windows, placebo 99.4th pct. Fragment-grade pace (~₹1,700/month) — honest size, not a segment book.
- **How:** `premiumtape_ret_shadow_score.py` → `november_shadow_premiumtape_bank_log.csv`; job 19:50 IST.
- **When:** Shadow from Nov 16. (The Nifty premium-tape family is **closed**: chase, retest and fade all measured negative.)

### 15. EKAM intraday — CAND-T5 and S2 (stocks)
- **What:** Six standard indicators (VWAP side, EMA 9/21, Supertrend, MACD, RSI zone, ADX) clubbed as **votes** on 5-min bars; exit when the vote decays. CAND-T5 (≤5 trades/day): 2025 **+₹62,164.57** / 2026 **+₹63,883.60**, placebo 100th pct both years. S2 (earliest-3/day): 2025 **+₹45,300.64** / 2026 **+₹72,605.30**. Both carry a Jul–Oct wound — that is why they are shadows, not books. (EKAM on Bank/Nifty options was measured and closed: best Bank row −₹276, best Nifty row −₹82,094.)
- **How:** `ekam_intraday_shadow_score.py` → `november_shadow_ekam_t5_stocks_log.csv` + `november_shadow_ekam_s2_stocks_log.csv`; job 20:05 IST.
- **When:** Listening stage. November backfill: CAND-T5 +₹24,528.65, S2 +₹20,662.60 (counterfactual, labelled as such in the ledgers).

### 16. HOLD L35-H15 (stocks)
- **What:** The fixed-hold swing the owner asked for: buy when RSI(14) crosses up through 35, **sell at the close 15 trading days later** — no exit signal. 2025 **+₹42,163** (83 trades, WR 63.9%) / 2026 **+₹83,963** (103 trades), placebo 97.6th pct; it is the local peak of its grid (levels 30/40 and holds 10/20 are all worse). Concentrated: 2025 ex-top-3 is negative — stated, not hidden.
- **How:** `hold_shadow_score.py` → `hold_shadow_log.csv`; job 20:20 IST.
- **When:** Shadow from Nov 16. Two November positions were open at the seed (BDL, HINDCOPPER — marked, labelled BACKFILL_COUNTERFACTUAL).

---

## RESEARCH — built and gated, not armed

### 17. EKAM daily 2c (stocks, daily swing)
- **What:** The two daily systems that tested good, merged into one book: Bollinger(20,2) band-return + RSI oversold-turn (60-day form), with the RSI-upgrade exit rule (an RSI signal during a Bollinger hold converts that position's exits to the RSI stack). One position per name. Final form after 5 tuning turns — stops and MACD were tested and rejected by the numbers.
- **Numbers:** 2025 **+₹42,954.60** (74 trades, WR 71.6%) · 2026 **+₹1,41,328.40** (102 trades, WR 62.7%). Files: `ekam2c_*` (spec, report, results, trades); registry `ekam_strategy.md`.
- **When:** Research only. A forward-paper start needs the **owner's explicit word** — asked 2026-11-14, still pending. Also the natural entry/exit discipline candidate for the investing discussion.

### 18. Value screener v2 + investing tiers
- **What:** Fundamental screen (P/E < 20, P/B < 3, EPS positive and not declining, profit in each of last 3 years, clean balance sheet, low promoter pledge, growth): **99 names pass**. The 2026-11-14 analysis tiers them **A = 14** (all financials, clean on every field) · **B = 72** · **C = 13** (named flags). South Indian Bank (the owner's holding, bought ~₹41) is Tier B — on price extension, not on business.
- **How:** `value_screener_v2_2026-11-11.md/.csv` (the locked list) + `investing_value_analysis_2026-11-14.md/.csv`.
- **When:** Analysis only — no orders are placed from it. The owner does his own price-action confirmation before investing; promoter-pledge filing checks are still outstanding for most names.

---

## CLOSED — do not revive without the owner's word

### 19. DIAL (standalone indicator system)
Supertrend/VWAP trend + RSI/Bollinger reversion core, identical across segments. **Failed everywhere:** Bank −₹33,719 (311 trades) · Nifty −₹89,487.20 · Stocks −₹1,93,637.97 (2025) / −₹2,92,761.31 (2026). Round-2 seeds also failed. The Parameter Atlas (306 Bank + 306 Nifty + 414 stocks settings) found **zero robust intraday rows**. Registry: `dial_programme.md`. Closed on all three segments.

### 20. SHORT-FOLLOW (R7-M1)
A premium-**selling** pair that passed its backtest gate (+₹49,149.25) and was armed on an inference the owner never gave. Day 1: +₹2,483.75 paper — then **disarmed permanently on the owner's order, 2026-11-13** ("we are option buyers not seller"). Killswitch file `november_shortfollow_KILLSWITCH` stays in place. Selling is banned; this never reopens.

### 21. Stock Engine
Wide-universe (~1,000-name) live paper experiment. November final −₹2,917.46 (8 trades); **wound down 2026-11-13**, job disabled. Closed — no picks ever again unless the owner restarts it.

### 22. BTST (original programme)
Buy-today-sell-tomorrow overnight holds. **Both arms failed** (2026-11-13): Bank options −₹6,436 / 190 trades; stocks −₹2,89,328 / 613 trades, 10 of 10 months red. Overnight long premium is the riskiest shape measured (worst night −₹17,125.50 on 1 lot). Closed — superseded by BTST-2 research below, under much stricter gates.

### 23. Retired headlines (never quote as causal)
Nifty +₹114,921.75 (confirmation-lag artefact) · Bank v19 +₹133,898 · the Morning-Mover line (look-ahead artefact; A2/B2/B3 fell with it). Kept in the record so they are never repeated.

---

## IN PROGRESS (owner's order 2026-11-15 — landing in a follow-up sync)

### 24. BTST-2
Overnight holds rebuilt under strict gates: narrow entry conditions, the circuit breaker applied, worst-night risk capped by construction. Research only until a full gate passes.

### 25. Stock options programme
Single-stock options on the watchlist names (buying only), tested against the equity-cash Stock Book basis.

### 26. VIX strategies
India VIX level and mean-reversion conditioning for the index books — when to stand down, when the premium environment favours buying.

### 27. Nifty long holds
Positional Nifty option buying on the monthly projection: buy today, hold for weeks, on the daily/weekly trend frame (the long-horizon cousin of the HOLD programme).

---

## Infrastructure

- **Circuit breaker** — `circuit_breaker.py` + `circuit_breaker_stack.py`, state `breaker_state_stack.json`, log `circuit_breaker_stack_log.csv`. The HWM-drawdown leg tripped at the 2026-11-13 close for the stack — a December-layer record; November's frozen paper primaries are not paused by it.
- **Option-chain archiver** — `option_chain_snapshot.py`, every 5 min in market hours; the live archive that future OI work reads.
- **Upstox access** — every API call carries a browser User-Agent (a 403 is a Cloudflare header problem, never a token failure). Token tooling lives in `upstox_refresh/` — **local only, never in this repo**.
