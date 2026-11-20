# SAPTA (owner's spec) — Final Report · 2026-11-17

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40/trade · no stock options.
**Window:** entries 2025-01-01 → 2026-11-13 · Spec: `sapta_owner_SPEC.md` (frozen before scoring, Amendments A1–A4).

## Verdict — plain

**SAPTA, built exactly to the owner's spec and tuned entity-by-entity as ordered, does NOT pass. No book is declared a SAPTA book. Nothing is armed; no paper run is started.**

- Entities passed: **0 of 14 in Candidate-1, 0 of 14 in Candidate-2, 0 of 14 in Daily.**
- All three books fail the book-level gate as well (0/4, 0/4 and 1/4 legs).
- Against the owner's bar ("equal or more powerful than EKAM"): **all three books fall short** (detail below — the Daily book's tuned form beats EKAM Daily's 2025 net on raw rupees but fails the gate and falls short of its 2026 net, so it does not count).

The tuning programme ran in full: **469 gated scorings** (base + 32 stock replacements + menu tunes, every one with its own 200-draw placebo), and the independent-path audit verified the trades (see §6). The failure is not for lack of tuning — it is that the entries themselves carry no timing edge: on the intraday books, *random entries on the same names and days, using the same exits, beat the strategy's entries almost everywhere* (placebo percentile ≈ 0). Tuning improved the rupee totals (it always can, by fitting), but the gate's placebo and ex-top-3 legs — the owner's own protection against exactly that — reject every entity.

## 1. What was built

**Selection (causal, quarterly):** 15 sectoral indices ranked by trailing 126-trading-day return of an equal-weighted constituent-average **PROXY** series (actual index levels are not fetchable; labelled PROXY everywhere), re-ranked on the first trading day of Jan/Apr/Jul/Oct, top 7 taken. Per index, top 3 stocks by trailing 126-day return subject to: member of Nifty 100 ∪ Nifty Midcap 150 · **in the F&O segment** (Amendment A2, owner's update 2026-11-17 19:23 IST — *"F&O presence is where the liquidity and volatility are"*; source: NSE market-lots file, 220 stock F&O symbols) · median 60-day traded value ≥ ₹5 crore · **price ≤ ₹2,000** (owner's rule) · ≥127 days history. 8 ranking dates, 69 distinct names picked across the window, 14 entities traded (Nifty Media ranked top-7 in 4 quarters but fields **zero** eligible stocks — none of its constituents is in Nifty 100/Midcap 150 — reported as an unfieldable entity per Amendment A1, never back-filled).

**Strategy — the SAPTA alignment stack (indicators only):** Supertrend(7,3), MACD(12,26,9), ADX(14), EMA-20/50, RSI(14), session VWAP. Cand-1: ST + MACD + VWAP agreement, next-bar-open fills, exits = ST flip / +1.0% / −0.7% / 15:15 square-off. Cand-2: Cand-1 + ADX ≥ 20 + EMA-20 side. Daily: long-only ST + MACD + EMA-50 swing, indicator exits. (RSI(14) is computed as specified; the frozen rules do not reference it — disclosed in the SPEC.)

**Tuning (owner's programme):** per failing entity — stock replacements first (a stock negative in both years with enough trades is replaced by the next-ranked eligible name in the same index; 32 replacements made), then the pre-registered menu (ST multiplier, ADX threshold, exit geometry, VWAP on/off, EMA-50 on/off, 09:45 start), one change at a time, max two layers, every step re-gated. Full log: `sapta_tuning_registry.md`.

## 2. Latest selection — ranking date 2026-10-01

Top 7 indices: **Pharma · Media · Realty · Oil & Gas · Healthcare · Auto · Energy**

| Entity | Stocks |
|---|---|
| Nifty Pharma | LAURUSLABS, ZYDUSLIFE, AUROPHARMA |
| Nifty Media | — *unfieldable (0 eligible stocks)* |
| Nifty Realty | LODHA, PHOENIXLTD, DLF |
| Nifty Oil & Gas | GAIL, PETRONET, BPCL |
| Nifty Healthcare | LAURUSLABS, ZYDUSLIFE, AUROPHARMA |
| Nifty Auto | MOTHERSON, BHARATFORG, UNOMINDA |
| Nifty Energy | BHEL, ADANIGREEN, ADANIENSOL |

So the latest "21 stocks" are 18 distinct names (Media fields none; LAURUSLABS/ZYDUSLIFE/AUROPHARMA serve both Pharma and Healthcare). All 8 quarters' selections are in `sapta_owner_selections.json` and summarised in the registry. F&O-excluded names (top performers skipped by Amendment A2, next eligible took the slot): 50 distinct names across the window, incl. HINDCOPPER, LLOYDSME, JSL, IPCALAB, ATGL, UBL, ZEEL, SUNTV, PVRINOX — full list in the selections file. The F&O filter changed 14 entity-quarters.

## 3. Book results (final tuned form vs base)

| Book | Form | 2025 net | 2026 net | Nov slice | Placebo pct 25/26 | Ex-top-3 25/26 | WR | Max DD | Worst month | Gate |
|---|---|---|---|---|---|---|---|---|---|---|
| Cand-1 | base | −246,843 | −145,987 | +14,575 | 0.0 / 0.0 | −255,572 / −153,068 | 37.8% | −452,690 | Dec-25 −52,309 | 0/4 FAIL |
| Cand-1 | final | −154,015 | −88,188 | +16,502 | 0.0 / 0.0 | −164,525 / −96,883 | 37.3% | −361,787 | Dec-25 −47,283 | 0/4 FAIL |
| Cand-2 | base | −189,152 | −129,456 | +7,291 | 0.0 / 0.0 | −197,479 / −136,455 | 38.0% | −386,627 | May-25 −44,433 | 0/4 FAIL |
| Cand-2 | final | −44,347 | −84,107 | +14,265 | 0.0 / 0.0 | −54,851 / −91,305 | 38.3% | −215,060 | Jun-26 −32,007 | 0/4 FAIL |
| Daily | base | +29,221 | −7,222 | +47,358 | 28.5 / 6.0 | −127,559 / −74,252 | 36.4% | −215,575 | Jan-25 −85,070 | 0/4 FAIL |
| Daily | final | +103,067 | +75,224 | +61,269 | 61.0 / 85.0 | −53,113 / +10,294 | 39.8% | −149,860 | Jan-25 −77,420 | 1/4 FAIL |

## 4. EKAM power comparison (owner's bar — per year, on net)

| SAPTA book (final) | 2025 | EKAM 2025 | 2026 | EKAM 2026 | Verdict |
|---|---|---|---|---|---|
| Cand-1: −154,015 / −88,188 | −154,015 | +62,165 | −88,188 | +63,884 | **falls short** (negative both years) |
| Cand-2: −44,347 / −84,107 | −44,347 | +45,301 | −84,107 | +72,605 | **falls short** (negative both years) |
| Daily: +103,067 / +75,224 | +103,067 | +42,955 | +75,224 | +1,41,328 | **falls short** — beats EKAM's 2025 net, misses 2026 by ~₹66k, and fails the gate (placebo 61/85 vs the >90 bar; ex-top-3 2025 −₹53,113; worst month −₹77,420 vs the −₹15,000 floor) |

No SAPTA book meets or beats its EKAM counterpart under the gate. The Daily book's tuned headline is the kind of number the gate exists to distrust: remove its 3 best trades of 2025 and it is −₹53,113.

## 5. Entities — all 14 named, none passed

Closest (3 of 4 gate legs — positive both years and ex-top-3 positive both years, failing **only** the placebo leg, i.e. random entries with the same exits did as well or better):

- **Nifty Auto — Cand-1** (+6,064 / +12,005; placebo pct 3.5 / 0.5) and **Cand-2** (+5,844 / +28,173; pct 9.5 / 44.5)
- **Nifty Realty — Cand-1** (+35,347 / +9,988; pct 88.0 / 75.5 — the single closest entity in the programme) and **Cand-2** (+18,933 / +11,855; pct 50.0 / 55.0)

Every other entity finished at 1–2 legs. Structural note: because the top-7 rotates quarterly, four entities (Consumer Durables, FMCG, Financial Services, IT) were selected only in 2025 quarters and PSU Bank only in 2026 quarters — they have no trades in the other year, so the positive-both-years leg is unreachable for them by construction; they are counted as failed, not hidden. Full per-entity finals, variants and every tuning step: `sapta_tuning_registry.md`; machine-readable: `sapta_owner_results.json`.

## 6. Integrity — independent-path audit

`sapta_owner_audit.py` (separately written: plain-loop indicators, own-day exit re-derivation from raw bars, entry-fill and net recomputation, square-off regression check) verified **95,632 trade rows**: 94,379 of 94,490 intraday rows and all 1,143 daily rows fully clean; **all 17,996 square-off exits equal their own day's 15:15 close**. The 111 exceptions (0.12%) are all traced to two named conventions, neither affecting any verdict: (i) 107 rows on 2025-01-01 — the two Supertrend implementations seed ATR/direction differently and disagree only in the first morning of day 1 (measured: 16 of 34,676 bars on a sample name, all before 11:00); (ii) 4 rows on 2025-10-21 (Diwali Muhurat session, 12 bars, no 15:15 bar) — the scorer applied the SPEC's "if absent, the day's last bar" square-off before the flip check on the final bar; exit prices identical. OHLC cross-check of the fetched 5-min stores against the existing reference stores: 37 names checked, 0 problems; the 32 new `sapta_vol` names have no reference store and were verified by the audit's own-day re-derivation instead.

## 7. Disclosures

- Index ranking uses an equal-weighted constituent-average **PROXY** (actual index levels unfetchable); constituents are the **current** official lists applied historically (survivorship caveat), and the F&O list is the current (2026-11-17) NSE list applied to all quarters — point-in-time F&O history is not published.
- Nifty Private Bank was dropped from the candidate set: its official constituent list is not retrievable; its names sit inside Nifty Bank.
- Per-entity tuning + replacement is fitting-prone by design (owner's instruction); the unmoved per-entity gate is the defence, and it rejected every fitted form. Failed entities are named above, never hidden inside book totals.
- Daily-book positions open after 2026-11-13 are closed at that close and labelled `window_end` in the trades file.

## 8. Files

`sapta_owner_SPEC.md` · `sapta_owner_select.py` · `sapta_owner_selections.json` (+ `_preA2`) · `sapta_owner_engine.py` · `sapta_owner_run.py` · `sapta_owner_audit.py` · `sapta_tuning_registry.md` · `sapta_owner_results.json` · `sapta_owner_trades.csv` (95,632 rows) · `sapta_audit_report.txt` · data in `data/sapta_vol/`, constituents + F&O list in `sapta_constituents/`.

**Recommendation (for the owner's decision, nothing started):** SAPTA as specified does not earn a forward paper run — the same lesson as TARANG, now confirmed on the owner's own selection and entity-tuning design: indicator-alignment entries on liquid large-caps carry no measurable timing edge over random entries once exits and costs are held equal. EKAM's edge, by contrast, lives in its specific 09:20 vote structure on its curated list, and it remains the stronger family on every gated comparison made today.
