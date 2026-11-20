# SECTOR ADDITIONS TEST — the proposed 37-name universe, scored

Owner extension (2026-11-17 07:32 IST): *"Can you add them and see how it's
performing?"* The 12 additions proposed in `sector_coverage_2026-11-17.md`
(ULTRACEMCO · LT · SBILIFE · APOLLOHOSP · ICICIBANK · SBIN · RELIANCE · INFY ·
M&M · BHARTIARTL · SUNPHARMA · TITAN) were scored with the **frozen rules** on
the enlarged 37-name universe against the frozen-25 controls, under the
verdict bar frozen in that document's SPEC ADDENDUM **before** scoring.

**Basis:** equity cash, per 100 shares PROVISIONAL, ₹40/trade, paper only,
real money ₹0. Judged per year (Jan–Oct), never pooled; November separate.
**Data:** all 12 additions already held complete 5-minute stores in the
wide-100 layout (464/464 sessions, 2025-01-01 → 2026-11-13, fetched this
morning via the programme's Upstox route; verified in place —
`sector_fetch_manifest.json`). EKAM-Daily uses the local daily dump
(official-close basis, ₹1 cr / 60-session liquidity screen, both sides).
**Controls:** EKAM intraday control PASS — all six published totals exact.
EKAM-Daily control PASS — raw 25 reproduces the published official-close
control exactly, and the screened 25 is identical (the screen never binds
on the 25). Stock Book same-root control reproduces the published
within-machinery sb25 run **exactly** on every window.

## VERDICT — NOT FIT TO JOIN LIVE as a set

Under the frozen bar (DEGRADES = net worse by >10% **or** max drawdown worse
than 1.5× control, in either year), **7 of 8 book-years DEGRADES** — every
one of them on the **drawdown leg**. Only EKAM-Daily 2025 improves. Headline
nets actually *rose* in 7 of 8 cells; the additions did not fail on profit.
They failed on the shape of the ride: drawdowns deepened to 1.54×–5.66× of
control, and ex-top-3 fell in 6 of 8 cells — the enlarged books are more
top-heavy and deeper-tailed almost everywhere.

| Book · Year | Control net | Enlarged net | Δ net | Control max DD | Enlarged max DD | DD × | Verdict |
|---|---|---|---|---|---|---|---|
| EKAM T5 · 2025 | +62,164.57 | +82,251.41 | +32.3% | −26,599.28 | −48,516.97 | 1.82× | **DEGRADES** (DD) |
| EKAM T5 · 2026 | +63,883.60 | +1,01,550.90 | +59.0% | −37,574.55 | −57,846.75 | 1.54× | **DEGRADES** (DD) |
| EKAM S2 · 2025 | +45,300.64 | +92,519.57 | +104.2% | −27,976.77 | −48,196.30 | 1.72× | **DEGRADES** (DD) |
| EKAM S2 · 2026 | +72,605.30 | +1,06,756.60 | +47.0% | −25,974.35 | −46,834.85 | 1.80× | **DEGRADES** (DD) |
| Stock Book · 2025 | +30,816.98 | +51,061.89 | +65.7% | −14,151.22 | −46,770.02 | 3.31× | **DEGRADES** (DD) |
| Stock Book · 2026 | +2,11,780.49 | +1,85,847.46 | −12.2% | −9,218.96 | −26,750.85 | 2.90× | **DEGRADES** (net + DD) |
| EKAM-Daily · 2025 | +63,621.50 | +5,95,974.00 | +836.7% | −41,990.10 | −40,930.00 | 0.97× | **IMPROVES** |
| EKAM-Daily · 2026 | +1,50,777.40 | +1,90,240.40 | +26.2% | −35,540.00 | −2,01,058.00 | 5.66× | **DEGRADES** (DD) |

## Per book

### EKAM intraday — CAND-T5 (caps bind: trade counts identical, 1,035 / 1,025 — selection substitution, not addition)
- 2025: 1,035 trades · WR 36.52% (ctl 35.56%) · ex-top-3 +19,551.41 (ctl +29,064.57 — **fell**)
- 2026: 1,025 trades · WR 36.78% (ctl 35.71%) · ex-top-3 +20,720.90 (ctl +39,713.60 — **fell**)
- Added names: only **7 of 12 ever traded** (2025), 6 (2026). Subtotal **+₹31,518.95** (2025) ·
  **+₹17,206.90** (2026) — carried by APOLLOHOSP (+19,525.30 / +14,570.00) and BHARTIARTL
  (+15,530.75 / +9,011.70). ULTRACEMCO, SBIN, M&M, SUNPHARMA never traded in this book.
- November: enlarged +₹25,797.60 vs control +₹24,528.65 (added names +₹2,510.00).

### EKAM intraday — S2 (621 / 615 trades, counts identical)
- 2025: WR 39.45% (ctl 34.94%) · ex-top-3 +29,819.57 (ctl +12,200.64 — rose, the one exception)
- 2026: WR 39.02% (ctl 36.75%) · ex-top-3 +25,926.60 (ctl +49,415.30 — **fell**)
- Added names: 6 traded (2025), only **3** (2026). Subtotal **+₹36,255.30** / **+₹28,897.00** —
  again APOLLOHOSP + BHARTIARTL almost alone.
- November: enlarged +₹27,519.50 vs control +₹20,662.60 (added +₹8,116.90).

### Stock Book (build_book machinery, within-machinery)
- 2025: 880 trades (ctl 694) · WR 41.14% · ex-top-3 **+₹1,907.89** vs control +₹19,628.26 —
  strip the top 3 trades and the enlarged 2025 book is nearly flat.
- 2026: 884 trades (ctl 629) · WR 52.60% · net **−12.2% below control** · ex-top-3 +₹1,37,175.96
  (ctl +₹1,93,534.94).
- Added names: **all 12 traded both years.** Subtotal **+₹20,244.91** (2025: M&M +38,979.11 best,
  APOLLOHOSP −20,967.62 worst) and **−₹25,933.03 in 2026** (ULTRACEMCO −27,828.10, M&M −18,503.60,
  APOLLOHOSP −13,276.31 — the 2026 additions were a net drag in this book).
- November: enlarged +₹8,923.84 vs control +₹7,517.94 (added +₹1,405.90).

### EKAM-Daily (EKAM-2c, official-close basis, screened)
- 2025: 115 trades (ctl 79) · WR 81.74% · ex-top-3 +₹3,23,971.50 · DD inside the bar → **IMPROVES**.
  **Concentration caveat, stated plainly:** the added names contributed +₹5,32,352.50 of the
  +₹5,95,974.00, and ULTRACEMCO alone +₹2,52,600.00 — on the per-100-shares basis a band
  reversion in a ₹12,100 stock books ~40× the rupees of the same % move in ITC (₹285). This is
  the basis flattering high-priced names, the same effect flagged in the wide-100 run — it is
  not 9× the edge, and it is not capital-normalised.
- 2026: 142 trades (ctl 102) · WR 62.68% · ex-top-3 collapses to +₹18,865.40 (ctl +₹77,116.40) ·
  max DD **−₹2,01,058.00 (5.66×)** → **DEGRADES**. Added names only +₹39,463.00, 7 of 12 negative;
  ULTRACEMCO flipped to −₹32,780.00.
- November slice: identical both sides (1 entry, still open, marked −₹3,140 — no added name
  entered in Nov 2–13).

## Why this happened — the mechanism

The 12 additions are the market's heavyweights, and most are **high-priced**
(ULTRACEMCO ₹12,100 · APOLLOHOSP ₹8,526 · TITAN ₹4,845 · LT ₹4,144 · M&M ₹3,333).
On the programme's per-100-shares basis, one trade in such a name swings 5–40×
the rupees of a trade in a mid-priced incumbent. Winners scale up (headline
nets rose in 7 of 8 cells) — but so do losing streaks, and the frozen rules'
selection now spends its capped slots on these larger-swing names, displacing
incumbent trades. The result everywhere: bigger totals, deeper drawdowns,
thinner ex-top-3. This is the wide-100 lesson repeating at 37 names, in a
milder dose: **the books' quality lives in the 25's price/scale mix, and
heavyweight additions change the risk shape even when they add profit.**

## What this means, plainly

- **As a set: NOT FIT.** The frozen bar was set before scoring and it is not
  met — 7 of 8 book-years degrade on drawdown.
- **The additions are not dead weight:** their own subtotal is positive in
  EKAM T5 (+₹31,519 / +₹17,207), EKAM S2 (+₹36,255 / +₹28,897) and EKAM-Daily
  (+₹5,32,353 / +₹39,463) in both years — negative only in Stock Book 2026
  (−₹25,933). APOLLOHOSP and BHARTIARTL are the consistent contributors;
  ULTRACEMCO is the largest single source of both the 2025 Daily gain and
  the 2026 Daily drawdown.
- **Sector coverage vs book shape is now a measured trade-off, not a guess:**
  covering every sector costs drawdown depth on the current basis. If the
  owner wants coverage anyway, the honest routes are (a) accept the deeper
  drawdowns knowingly, or (b) a future test with the additions at a
  normalised size — either is his call on this report.
- **Nothing live has changed.** The live universe stays the frozen 25.
  Live addition waits for the owner's word on this report.

Files: `sector_additions_results.json` (full stats + verdicts) ·
`sector_additions_trades.csv` (6,596 enlarged-run trade rows, added names
flagged) · `sector_fetch_manifest.json` (data verification) ·
`sector_coverage_2026-11-17.md` + `sector_coverage.json` (map, gaps,
proposal, frozen bar).
