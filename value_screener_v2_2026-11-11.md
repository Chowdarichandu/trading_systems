# Engine 2 — Value-Stock Screener v2 (revised criteria)

**Date of all figures: Wednesday, 11 November 2026** (screener.in company pages fetched 11 Nov 2026, ~11:00–11:06 IST, intraday prices unless noted; one batch of 15 names — marked † — was verified from screener.in search-cache excerpts at the **9 Nov 2026 close** after the live page fetcher hit a rate limit; see §10).
**Source: screener.in** — public screens for the pool plus individual company pages (consolidated governs; standalone used and noted where the consolidated page was empty/stale).
**This is a fundamental shortlist only — no buy/sell recommendation.** The owner does his own price-action confirmation before any investment.

---

## 1. Criteria as applied (owner's v2 spec)

| # | Criterion | Operational rule used |
|---|---|---|
| 1 | P/E < 20 | Screener "Stock P/E" on the company page must be > 0 and < 20 (blank = fail) |
| 2 | Price-to-Book < 3 | P/B = CMP ÷ Book Value per share (company page) < 3.00 |
| 3 | EPS good | EPS (₹) positive and not in a declining trend: no two consecutive yearly declines in the Mar-2023→Mar-2026 series and Mar-2026 EPS not > 25% below Mar-2024. A single dip year that recovered (or a 10–25% dip without consecutive declines) is a **flag (FLAG-DIP)**, not a fail |
| 4 | Profitable 3 years | Net Profit > 0 in **each** of FY24, FY25, FY26 **and** in the latest reported quarter |
| 5 | Clean balance sheet | Non-financials: Debt-to-Equity < 1 (screener's printed ratio was absent from page text, so D/E = Borrowings ÷ (Equity Capital + Reserves), latest balance-sheet column). Banks/NBFCs/HFCs/MFIs/insurers: GNPA < 3% and NNPA < 1.5% **where shown** (blank on many pages — recorded n/s, not failed). Contingent liabilities > net worth = flag. Reserves falling vs Mar-2024 = flag |
| 6 | Good governance | Promoter pledge: **fail if > 10%** of promoter holding, flag if 5–10% (pledge % was visible on the fetched page text for only a minority of names — see caveat §10). Promoter holding down > 10 pp over the window shown = flag. No auditor/fraud red flag visible on the page = pass on this proxy. **Governance is judged on these visible proxies only** |
| 7 | Future growth | Screener's printed Compounded Profit Growth, 3-Year (FY23→FY26 window) must be > 0 for the main list; names passing 1–6 with printed 3-Y profit growth ≤ 0 go to **"Value without growth"** (§6) |

Universe: NSE-listed, market cap ≥ ₹500 cr.

## 2. Method and funnel

- **Pool** = union of three public screener screens fetched in full on 2026-11-11 — (a) screen 2193022 (P/E < 20, P/B < 3, market cap > ₹5,000 cr; 153 names), (b) screen 1416292 (P/B < 1; 90 names), (c) screen 2205120 (P/B < 1, market cap ₹500–10,000 cr, D/E < 1; 159 names) — **plus** a manual checklist of large caps the screens can miss (Reliance, HPCL, Vedanta, JSW Steel, Kotak, IndusInd, IDFC First, RBL, AU SFB, L&T Finance, New India Assurance, Aurobindo, Dr Reddy's, Cyient, ACC, IRB Infra, UPL, Tata Chemicals, GHCL, NFL, Balrampur Chini, LT Foods, West Coast Paper, GIC Housing Finance, Bajaj Finance, Tata Motors, HG Infra, Jindal Steel).
- **178 companies were individually verified** on their screener company pages (every pool name with market cap ≳ ₹2,000 cr, all v1 names, and the manual checklist).
- **Result: 99 companies pass criteria 1–6.** Of these, **86 also pass the growth test (criterion 7)** and **13 sit in "value without growth."** The **main table (§4) shows the top 50 of the 86 by market cap** (cut-off: ₹14,756 cr); the other 36 passers are listed in §5.
- The unverified tail (pool names below ~₹2,000 cr market cap, plus one unverified InvIT, Vertis Infrastructure ~₹17,365 cr) was not page-checked; the market-wide passing total is therefore **at least 99**, not exactly 99.
- Screen-stage exclusions (never page-verified because a fetched screen already showed a hard fail): e.g. Tata Investment Corp (P/E 75), Zee Entertainment (P/E 38), JSW Holdings (P/E 66), Maharashtra Scooters (P/E 46), Coffee Day (P/E 212), Gujarat Alkalies (P/E 34), Reliance Power (P/E 2,283), Embassy Developments (latest-quarter loss), IRB InvIT (P/E 39), Sunflag Iron (P/E 34).

## 3. Reference row — South Indian Bank (owner's holding)

**Verdict: South Indian Bank PASSES the v2 spec — explicitly.** It failed v1 only because v1 demanded P/B < 1; under P/B < 3 it is comfortably in, with rising EPS and three clean profit years.

| CMP | P/E | Book Value | P/B | ROE | PAT FY24 / FY25 / FY26 (₹ cr) | EPS FY24 / FY25 / FY26 (₹) | Latest qtr PAT | 3-Y Sales / Profit growth | Market cap | 52w H/L | GNPA / NNPA |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ₹61.3 | 10.2 | ₹46.1 | 1.33 | 13.5% | 1,070 / 1,303 / 1,456 | 4.09 / 4.98 / 5.56 (rising) | ₹426 cr (Sep-2026) | 11% / 23% | ₹16,067 cr | 61.3 / 33.4 | n/s on this fetch (v1 fetch showed 1.24% / 0.09%) |

- Re-verified 11 Nov 2026: CMP ₹61.3 (v1 fetch: ₹60.6 — same-day intraday drift), P/B 1.33 (v1: 1.31), P/E 10.2 (v1: 10.0), book value unchanged at ₹46.1. No promoter (widely held). Reserves up (₹8,565 cr → ₹11,815 cr).
- On market-cap rank it falls **inside the main table at #48** and is shown there marked REFERENCE.

## 4. Main list — top 50 passers by market cap

All 50 pass criteria 1–7. "EPS dir." = FY24→FY26 direction. D/E for non-financials; GNPA/NNPA for financials ("n/s" = not shown on the page, not a fail). Pledge "n/s" = not visible on the fetched page text (see §10). Promoter shown as latest % (earliest shown, ~Dec-2023). Growth = screener printed compounded 3-Y.

| # | Company | CMP ₹ | P/E | P/B | EPS FY24→FY26 (₹) / dir. | PAT FY24/25/26 (₹ cr) | D/E or GNPA/NNPA | Pledge % | Promoter % | Sales G 3Y | Profit G 3Y | ROE % | MCap ₹ cr | 52w H/L |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | HDFC Bank | 814 | 15.7 | 2.08 | 42.16→46.26→49.39 ↑ | 65,446/73,440/79,219 | n/s | n/s | none | 27% | 18% | 13.6 | 12,56,430 | 1018/669 |
| 2 | ICICI Bank | 1,600 | 19.4 | 2.96 | 63.02→71.65→75.71 ↑ | 46,081/54,569/57,936 | n/s | n/s | none | 17% | 17% | 15.9 | 11,48,775 | 1617/1188 |
| 3 | State Bank of India | 1,070 | 11.5 | 1.47 | 75.17→86.91→90.24 ↑ | 69,543/80,523/86,666 | 2.13/0.52 (Sep-24) | n/s | 55.45 (57.49) | 14% | 14% | 15.4 | 9,87,646 | 1235/934 |
| 4 | Life Insurance Corp (LIC) | 404 | 8.22 | 2.69 | 32.34→38.20→45.42 ↑ | 40,916/48,320/57,453 | insurer | n/s | 90.00 (96.50) | 8% | 17% | 37.8* | 5,11,060 | 461/361 |
| 5 | Axis Bank | 1,347 | 14.0 | 1.83 | 85.49→90.58→84.89 → | 26,492/28,191/26,548 | n/s | n/s | 7.86 (8.20) | 15% | 35% | 13.1 | 4,19,366 | 1418/1150 |
| 6 | ONGC | 236 | 5.98 | 0.74 | 39.06→28.80→32.93 dip | 55,273/38,329/49,793 | 0.47 | n/s | 58.89 | −1% | 1% | 11.6 | 2,96,769 | 308/218 |
| 7 | Shriram Finance | 978 | 18.1 | 2.06 | 39.20→50.81→53.28 ↑ | 7,399/9,576/10,024 | n/s | n/s | 20.30 (25.43) | 16% | 19% | 16.4 | 2,30,097 | 1154/804 |
| 8 | Hindalco Industries | 957 | 9.27 | 1.35 | 45.19→71.20→59.59 ↑† | 10,155/16,002/13,391 | 0.73 | n/s | 34.67 | 7% | 19% | 13.0 | 2,15,149 | 1179/772 |
| 9 | Indian Oil Corporation | 148 | 4.40 | 0.90 | 29.55→9.63→29.81 dip-rec. | 43,161/13,789/43,677 | 0.60 | n/s | 51.50 | −2% | 62% | 20.5 | 2,09,489 | 189/125 |
| 10 | Punjab National Bank | 138 | 6.97 | 0.99 | 8.27→16.08→16.00 ↑ | 9,157/18,553/18,467 | n/s | n/s | 70.08 (73.15) | 15% | 76% | 13.0 | 1,58,085 | 138/98.5 |
| 11 | Union Bank of India | 200 | 6.90 | 1.06 | 18.07→23.62→25.45 ↑ | 13,797/18,027/19,430 | n/s | n/s | 74.76 (76.99) | 10% | 32% | 15.7 | 1,52,519 | 205/146 |
| 12 | Bank of Baroda | 272 | 5.94 | 0.80 | 36.29→40.06→38.38 → | 18,869/20,865/20,070 | n/s | n/s | 63.97 | 13% | 10% | 12.7 | 1,40,480 | 326/224 |
| 13 | BPCL | 320 | 9.90 | 1.37 | 61.91→30.74→59.57 dip-rec. | 26,859/13,337/25,843 | 0.62 | n/s | 52.98 | −1% | 107% | 28.8 | 1,39,027 | 392/267 |
| 14 | Indian Bank | 957 | 9.72 | 1.48 | 62.51→83.61→86.89 ↑ | 8,423/11,264/11,707 | 1.61/0.14 | n/s | 73.84 | 14% | 28% | 15.4 | 1,28,878 | 1001/764 |
| 15 | Bajaj Holdings & Inv. | 11,245 | 13.5 | 1.70 | 652.98→585.90→865.89 dip-rec. | 7,365/6,626/9,789 | 0.00 | n/s | 51.46 | 29% | 19% | 11.9 | 1,25,142 | 12979/8588 |
| 16 | GAIL (India) | 189 | 9.78 | 1.29 | 15.06→18.93→11.53 dip ⚠ | 9,903/12,463/7,582 | 0.25 | n/s | 51.85 | −1% | 10% | 8.71 | 1,24,039 | 190/134 |
| 17 | Canara Bank | 132 | 5.90 | 0.94 | 16.84→19.34→19.70 ↑ | 15,401/17,692/19,712 | 1.33/0.30 | n/s | 62.93 | 14% | 18% | 16.1 | 1,19,279 | 163/115 |
| 18 | Muthoot Finance | 2,928 | 9.64 | 2.68 | 107.71→132.84→263.79 ↑ | 4,468/5,352/10,607 | n/s | n/s | 73.35 | 38% | 43% | 30.9 | 1,17,566 | 4150/2303 |
| 19 | IRFC | 88.9 | 15.8 | 1.92 | 4.91→4.98→5.36 ↑ | 6,412/6,502/7,009 | n/s | n/s | 82.90 (86.36) | 5% | 3% | 12.8 | 1,16,140 | 137/73 |
| 20 | Power Finance Corp | 343 | 4.30 | 0.77 | 59.88→69.67→78.49 ↑ | 26,461/30,514/33,625 | 0.55/0.13 | n/s | 55.99 | 14% | 18% | 20.7 | 1,13,210 | 486/310 |
| 21 | Indus Towers | 388 | 14.4 | 2.59 | 22.40→37.65→27.08 dip ⚠ | 6,036/9,932/7,145 | 0.56 | n/s | 51.26 (68.99) ⚠ | 5% | 47% | 18.6 | 1,02,387 | 482/356 |
| 22 | Federal Bank | 357 | 17.0 | 2.06 | 15.93→16.93→17.63 ↑ | 3,964/4,234/4,491 | 2.11/0.63 (Mar-24) | n/s | none | 19% | 11% | 11.6 | 88,194 | 372/233 |
| 23 | IDBI Bank | 81.3 | 10.5 | 1.21 | 5.38→7.10→8.57 ↑ | 5,814/7,656/9,237 | n/s | n/s | 94.72 | 12% | 35% | 14.1 | 87,460 | 118/61 |
| 24 | REC Ltd | 312 | 5.41 | 0.86 | 53.72→60.32→61.93 ↑ | 14,145/15,884/16,308 | n/s | n/s | 52.63 | 15% | 14% | 20.1 | 82,209 | 388/282 |
| 25 | SAIL | 175 | 12.1 | 1.16 | 7.42→5.74→8.17 dip-rec. | 3,067/2,372/3,373 | 0.50 | n/s | 65.00 | 2% | 26% | 6.57 | 72,160 | 210/124 |
| 26 | Bank of Maharashtra | 90.8 | 8.79 | 1.87 | 5.75→7.21→9.12 ↑ | 4,072/5,542/7,017 | 1.25/0.12 | n/s | 73.60 (86.46) ⚠ | 23% | 39% | 22.6 | 69,839 | 94.5/55.5 |
| 27 | Bank of India | 151 | 5.49 | 0.73 | 14.42→20.97→22.64 ↑ | 6,567/9,552/10,309 | n/s | n/s | 73.38 | 16% | 42% | 12.4 | 68,631 | 178/124 |
| 28 | National Aluminium | 327 | 8.42 | 2.40 | 10.83→28.68→31.56 ↑ | 1,988/5,268/5,797 | 0.00 | n/s | 51.28 | 8% | 59% | 29.4 | 60,095 | 445/249 |
| 29 | GIC Re | 338 | 6.59 | 0.80 | 38.11→42.36→55.08 ↑ | 6,686/7,432/9,662 | insurer | n/s | 77.40 (85.78) | 4% | 12% | 14.6 | 59,211 | 418/308 |
| 30 | Petronet LNG | 330 | 10.7 | 2.04 | 24.35→26.48→26.08 → | 3,652/3,973/3,913 | 0.09 | n/s | 50.00 | −10% | 5% | 18.4 | 49,470 | 330/235 |
| 31 | HDB Financial Services | 564 | 15.8 | 2.11 | 31.03→27.34→30.64 dip-rec. | 2,461/2,176/2,544 | 2.44/1.09 (Mar-26) | n/s | 74.08 | 14% | 9% | 13.9 | 46,855 | 797/494 |
| 32 | M&M Financial Services | 290 | 10.9 | 1.46 | 15.22→17.81→20.54 ↑ | 1,943/2,261/2,861 | n/s | n/s | 52.48 | 18% | 12% | 12.3 | 40,260 | 415/253 |
| 33 | Karur Vysya Bank | 382 | 12.5 | 2.40 | 16.63→20.10→25.97 ↑ | 1,605/1,942/2,510 | 0.69/0.18 | n/s | 1.95 (none) | 19% | 31% | 19.1 | 36,884 | 391/237 |
| 34 | HUDCO | 173 | 7.73 | 1.50 | 10.57→13.53→20.15 ↑ | 2,117/2,709/4,034 | n/s | n/s | 75.00 | 23% | 33% | 20.0 | 34,713 | 247/142 |
| 35 | UCO Bank | 25.1 | 10.6 | 0.91 | 1.38→1.95→2.21 ↑ | 1,654/2,445/2,768 | 1.96/0.18 | n/s | 90.95 (95.39) | 14% | 14% | 8.61 | 31,524 | 32.1/21.3 |
| 36 | LIC Housing Finance | 563 | 5.26 | 0.71 | 86.59→98.94→101.87 ↑ | 4,763/5,443/5,604 | n/s | n/s | 45.24 | 8% | 25% | 14.4 | 30,949 | 598/459 |
| 37 | PNB Housing Finance | 1,138 | 12.6 | 1.47 | 58.06→74.49→87.94 ↑ | 1,508/1,936/2,291 | 0.95/0.58 (Jun-26) | n/s | 28.01 | 9% | 30% | 12.7 | 29,679 | 1225/730 |
| 38 | Central Bank of India | 32.6 | 6.10 | 0.71 | 3.07→4.35→5.00 ↑ | 2,677/3,943/4,531 | 2.40/0.32 | n/s | 81.19 (93.08) ⚠ | 12% | 39% | 11.9 | 29,517 | 40.9/28.3 |
| 39 | IIFL Finance | 678 | 11.6 | 1.87 | 44.90→8.92→39.05 dip ⚠ | 1,974/578/1,817 | 1.55/0.82 (Jun-26) | n/s | 24.76 | 17% | 3% | 12.6 | 28,953 | 705/409 |
| 40 | Cholamandalam Fin. Holdings | 1,454 | 9.89 | 1.59 | 94.39→115.76→130.01 ↑ | 3,851/4,740/5,485 | n/s | n/s | 46.39 | 29% | 24% | 17.5 | 27,299 | 2008/1237 |
| 41 | Apollo Tyres | 425 | 13.1 | 1.54 | 27.11→17.66→21.61 dip ⚠ | 1,722/1,121/1,372 | 0.31 | n/s | 36.93 | 5% | 26% | 13.1 | 27,011 | 540/365 |
| 42 | Redington | 340 | 13.2 | 2.46 | 15.59→20.53→19.06 → | 1,239/1,821/1,284 | 0.59 | n/s | none | 15% | 5% | 16.9 | 26,549 | 420/191 |
| 43 | City Union Bank | 230 | 15.4 | 2.04 | 10.28→11.37→13.39 ↑ | 1,016/1,124/1,326 | 1.44/0.48 | n/s | none shown | 13% | 12% | 13.2 | 22,838 | 249/168 |
| 44 | Gujarat Energy (ex-Gujarat Gas) | 239 | 10.3 | 1.17 | 16.61→59.77→29.33 vol. ⚠ | 1,144/3,979/1,678 | 0.18 | n/s | 38.94 (60.89) ⚠ | 12% | 12% | 10.2 | 22,466 | 385/206 |
| 45 | AWL Agri Business | 169 | 18.8 | 2.02 | 1.14→9.43→8.04 ↑† | 148/1,226/1,045 | 0.27 | n/s | 56.94 (87.88) ⚠ | 9% | 22% | 10.7 | 22,004 | 283/160 |
| 46 | Sagility | 44.9 | 19.8 | 2.06 | 0.53→1.15→1.98 ↑ | 228/539/925 | 0.09 | n/s | 50.95 (82.39) ⚠ | 19% | 86% | 10.6 | 21,014 | 54.3/35.8 |
| 47 | Aadhar Housing Finance | 439 | 16.1 | 2.35 | 18.99→21.14→25.15 ↑ | 750/912/1,096 | 1.31/0.90 (Jun-26) | n/s | 64.51 (76.48) ⚠ | 22% | 25% | 15.9 | 19,248 | 563/414 |
| 48 | **South Indian Bank — REFERENCE** | 61.3 | 10.2 | 1.33 | 4.09→4.98→5.56 ↑ | 1,070/1,303/1,456 | n/s (v1: 1.24/0.09) | n/s | none | 11% | 23% | 13.5 | 16,067 | 61.3/33.4 |
| 49 | Natco Pharma | 816 | 14.0 | 1.60 | 76.87→104.40→78.54 dip ⚠ | 1,388/1,883/1,418 | 0.08 | n/s | 46.22 (49.71) | 15% | 27% | 17.1 | 15,999 | 1217/774 |
| 50 | Jammu & Kashmir Bank | 134 | 6.28 | 0.83 | 16.05→18.91→21.46 ↑ | 1,767/2,082/2,363 | 2.23/0.51 | n/s | 59.40 | 12% | 25% | 15.2 | 14,756 | 202/97.4 |

\* LIC's printed ROE (37.8%) reflects its small equity-capital base; treat with care. † "↑†/dip-rec." = direction vs FY24 with an intervening peak/dip — see CSV for the full EPS series. ⚠ = flag carried (EPS dip, promoter decline, or earnings-quality note in §8).

## 5. Passers beyond the top 50 (36 names — all pass criteria 1–7)

| Company | CMP ₹ | P/E | P/B | ROE % | Profit G 3Y | MCap ₹ cr | Note |
|---|---|---|---|---|---|---|---|
| Tamilnad Mercantile Bank | 862 | 8.66 | 1.27 | 14.0 | 9% | 13,649 | GNPA 0.61/NNPA 0.14 |
| Zensar Technologies | 568 | 16.1 | 2.65 | 17.4 | 34% | 12,930 | EPS dip flag |
| Edelweiss Financial | 131 | 19.8 | 2.68 | 14.2 | 23% | 12,434 | P/E just inside the limit |
| Shipping Corp of India | 268 | 6.21 | 1.21 | 15.0 | 15% | 12,472 | EPS dip flag |
| Home First Finance | 1,093 | 18.4 | 2.45 | 15.7 | 33% | 11,425 | NNPA 1.40% — near limit; promoter −16.6 pp flag |
| JM Financial | 115 | 10.7 | 1.00 | 11.9 | 27% | 10,972 | v1 name, retained |
| Can Fin Homes | 770 | 8.95 | 1.60 | 19.7 | 20% | 10,256 | GNPA 0.87/NNPA 0.42 |
| Powergrid InvIT (PGInvIT) † | 106 | 10.6 | 1.28 | 10.5 | 88% | 9,613 | InvIT; equity declines by design (distributions) |
| Time Technoplast | 200 | 18.9 | 2.31 | 13.1 | 28% | 9,860 | |
| Welspun Enterprises | 690 | 17.0 | 2.85 | 13.6 | 12% | 9,551 | |
| TSF Investments | 422 | 19.3 | 1.55 | 8.23 | 26% | 9,382 | Holdco (Sundaram group) |
| AAVAS Financiers † | 1,137 | 12.8 | 1.67 | 13.9 | 15% | 9,016 | NNPA 0.67% shown; GNPA n/s |
| Finolex Industries † | 145 | 14.8 | 1.19 | 9.04 | 35% | 8,976 | EPS dip flag; net cash |
| KEC International † | 334 | 18.9 | 1.46 | n/s | 55% | 8,883 | D/E borderline if acceptances counted (~1.04) |
| Sandur Manganese † | 177 | 10.0 | 2.32 | 22.5 | 37% | 8,593 | EPS dip flag |
| NCC † | 131 | 10.9 | 1.01 | n/s | 6% | 8,220 | Pledge 3.8% (visible, below flag band) |
| NESCO † | 1,057 | 18.4 | 2.36 | 13.8 | 11% | 7,443 | |
| Intellect Design Arena † | 515 | 19.4 | 2.17 | 11.5 | 11% | 7,226 | ⚠ P/E borderline: screener consolidated 19.4 vs filing mirrors 20.2–20.4 |
| Onemi Technology (Kissht) † | 349 | 18.8 | 2.62 | 24.0 | 117% | 7,142 | ⚠ Partially verified: FY24 PAT and annual EPS row not extractable |
| Birla Corporation | 834 | 12.7 | 0.84 | 7.83 | 134% | 6,423 | v1 name, retained; EPS dip flag |
| Transport Corp of India | 865 | 14.2 | 2.38 | 19.2 | 12% | 6,511 | |
| Sharda Cropchem | 713 | 9.95 | 1.98 | 23.2 | 26% | 6,435 | EPS dip flag |
| FDC | 394 | 19.4 | 2.40 | 11.5 | 13% | 6,407 | |
| Fedbank Financial | 161 | 14.0 | 1.91 | 12.6 | 22% | 6,045 | EPS dip flag; NNPA 1.18% |
| JK Lakshmi Cement | 480 | 18.4 | 1.51 | 10.7 | 5% | 5,962 | EPS dip flag |
| CSB Bank | 314 | 7.89 | 1.05 | 13.5 | 5% | 5,450 | GNPA 1.58/NNPA 0.33 |
| LG Balakrishnan & Bros | 1,685 | 16.8 | 2.36 | 15.5 | 10% | 5,374 | |
| AvenuesAI | 127 | 15.1 | 0.91 | 6.64 | 30% | 4,440 | |
| PTC India | 142 | 9.05 | 0.78 | 10.3 | 11% | 4,208 | v1 name, retained; div yield is special-dividend inflated |
| J Kumar Infraprojects | 442 | 8.57 | 0.99 | 12.4 | 13% | 3,344 | ⚠ Contingent liabilities ₹4,383 cr **exceed** net worth ₹3,369 cr (flag) |
| Vindhya Telelinks | 2,584 | 12.0 | 0.66 | 5.31 | 6% | 3,062 | v1 name, retained; EPS dip flag |
| Satin Creditcare | 264 | 5.47 | 0.92 | 12.3 | 313% | 2,922 | v1 name, retained; MFI risk; EPS dip flag |
| Ramco Industries | 320 | 8.56 | 0.60 | 6.75 | 34% | 2,779 | v1 name, retained |
| Repco Home Finance | 388 | 4.91 | 0.57 | 12.4 | 15% | 2,430 | v1 name, retained |
| India Glycols | 314 | 6.65 | 0.72 | 11.3 | 39% | 2,108 | v1 name, retained |
| Prakash Industries | 117 | 6.74 | 0.59 | 9.65 | 21% | 2,102 | Was v1 Annexure B (unverified); now verified pass |

† Verified from screener.in search-cache excerpts at the 9 Nov 2026 close (see §10) — CMP/market cap are 9 Nov closes for these names.

## 6. Value without growth (13 names — pass criteria 1–6, fail criterion 7)

| Company | CMP ₹ | P/E | P/B | ROE % | PAT FY24/25/26 (₹ cr) | Profit G 3Y (printed) | MCap ₹ cr | Note |
|---|---|---|---|---|---|---|---|---|
| Oil India | 436 | 8.50 | 1.22 | 12.2 | 6,980/7,040/7,551 | −9% | 71,001 | EPS dip flag; profits flat, not falling |
| GE Shipping | 1,444 | 4.71 | 1.09 | 15.9 | 2,614/2,344/2,943 | 0% | 20,611 | Shipping cycle |
| Deepak Fertilizers | 1,236 | 15.9 | 2.28 | 11.1 | 468/945/739 | −15% | 15,604 | |
| Vardhman Textiles | 524 | 14.9 | 1.37 | 7.03 | 637/887/753 | −3% | 15,180 | |
| GSPL ⚠ provisional | 268 | 14.4 | 1.26 | 9.89 | 2,184/1,637/**FY26 n/s** | −12% | 15,141 | **Page stale (May-2026 snapshot) — FY26 unverifiable; provisional only** |
| Galaxy Surfactants † | 2,197 | 18.7 | 2.62 | n/s | 302/305/267 | −10% | 7,800 | EPS dip flag |
| Gujarat Ambuja Exports | 152 | 13.6 | 1.94 | 9.72 | 346/249/304 | −3% | 6,960 | EPS dip flag |
| GNFC | 471 | 6.60 | 0.74 | 9.14 | 497/598/809 | −18% | 6,924 | v1 name; printed 3-Y window starts from high FY23 base (EPS ₹94.68) |
| RCF | 107 | 14.2 | 1.15 | 7.84 | 225/242/427 | −24% | 5,917 | Same FY23-base effect (EPS ₹17.52 in FY23) |
| GSFC | 144 | 10.1 | 0.44 | 5.51 | 564/591/673 | −19% | 5,746 | v1 name; FY23-base effect; low ROE |
| PNC Infratech | 136 | 5.59 | 0.48 | 6.12 | 909/815/832 | −15% | 3,481 | v1 name; sales shrinking (−12% 3-Y) |
| Maithan Alloys | 852 | 5.02 | 0.54 | 0.54* | 349/631/441 | −65% | 2,479 | v1 name; profits dominated by investment fair-value income |
| GIC Housing Finance | 132 | 4.52 | 0.34 | 7.61 | 151/160/155 | −10% | 713 | Flat profits |

## 7. Overlap with v1 (P/B < 1, P/E < 15 spec — 39 main names)

**Retained in v2 main list (22):** ONGC, Indian Oil, PNB, Bank of Baroda, Canara Bank, PFC, REC, Bank of India, GIC Re, UCO Bank, LIC Housing Finance, Central Bank of India, J&K Bank, JM Financial, Birla Corporation, PTC India, J Kumar Infraprojects, Vindhya Telelinks, Satin Creditcare, Ramco Industries, Repco Home Finance, India Glycols.
**Moved to "value without growth" (5):** GNFC, GSFC, PNC Infratech, Maithan Alloys, GSPL (provisional).
**Now FAIL in v2 (12):**

| v1 name | v2 fail reason |
|---|---|
| Jaiprakash Power Ventures | **Governance: promoters pledged 73.0% of holding** + EPS in decline (1.49→1.19→0.66) |
| Patel Engineering | **Governance: promoters pledged 66.8% of holding** + EPS declined two consecutive years |
| Karnataka Bank | EPS declined two consecutive years (34.64→33.68 after 37.77→34.64) despite PAT ~₹1,300 cr every year |
| GR Infraprojects | EPS declined every year (136.90→104.85→93.31) |
| Kama Holdings | EPS decline (272.27→196.86, FY26 recovery to 290.04 still leaves two consecutive declines) |
| Bengal & Assam Co | EPS decline vs the exceptional FY24 base (3,445.53→648.25→721.95) |
| Pilani Investment | EPS collapse (150.34→88.94→28.05); ROE ~0.2% |
| Equitas Small Finance Bank | EPS collapse (7.04→1.29→0.90) — MFI stress profit collapse |
| Jana Small Finance Bank | EPS decline (64.02→47.73→30.99) |
| KNR Constructions | EPS decline (35.62→15.54; FY26 PAT fell to ₹437 cr) |
| Route Mobile | EPS declined two consecutive years (59.74→50.61→37.94) |
| Muthoot Microfin | **FY25 was a loss year (−₹223 cr)** + EPS decline + GNPA 3.38% ≥ 3% |

**v1 near-misses now IN:** Union Bank of India (P/B 1.06 < 3 — main list #11) and SAIL (P/B 1.16 — main list #25, EPS dip flag).
**v1 exclusions stay out:** GIPCL (D/E 1.05 again), HG Infra (D/E 1.52 + EPS decline), Rain Industries (loss years on its Dec year-end + D/E 1.35).
**v1 annexures:** Kirloskar Industries (Annexure A) now fails on EPS decline; Prakash Industries (Annexure B) is now a verified passer (§5); TTK Healthcare (Annexure A) was below the verified market-cap band and was not re-verified.

## 8. Notable large-cap failures (for the record)

| Company | Fail reason |
|---|---|
| Reliance Industries | P/E 22.0 ≥ 20 (P/B 1.92 passes) |
| Bajaj Finance | P/E 30.6 and P/B 5.43 |
| Kotak Mahindra Bank | P/E 22.8 |
| NTPC | D/E 1.33 ≥ 1 (utility leverage, computed) |
| Power Grid Corp | D/E 1.47 ≥ 1 (computed) |
| Coal India | EPS declined two consecutive years (60.69→57.61→50.46) despite PAT > ₹31,000 cr every year |
| Tata Steel | FY24 net loss (−₹4,910 cr) |
| Jindal Steel | P/E 36.9 on the page (and EPS −43% vs FY24) |
| JSW Steel | P/E 21.0 |
| HPCL | P/E 58.9 (TTM hit by the Jun-2026 quarter loss of −₹12,265 cr) and D/E 1.40 |
| Vedanta | P/B 8.04 — screener book value is only ₹32.6/share after the demerger split |
| IndusInd Bank | P/E 23.6, EPS collapse (−90% vs FY24), **promoter pledge 42.8%** |
| Tata Motors (both entities) | TMCV: P/E 23.1, P/B 10.82; TMPV: P/E ~173 (snippet) — post-demerger stub history |
| IDFC First Bank | P/E 23.1 + EPS decline |
| RBL Bank | P/E 50.6 + EPS decline |
| AU Small Finance Bank | P/E 22.9 + P/B 3.36 |
| Aurobindo Pharma / Dr Reddy's / Cyient / ACC | P/E 26.0 / 41.1 / 29.6 / 25.6 |
| L&T Finance / Amara Raja / IRB Infra | P/E 20.2 / 20.2 / 20.5 — marginal P/E fails |
| Kalpataru Projects | P/E exactly 20.0 — fails the < 20 rule |
| NHPC | EPS decline + D/E 1.31 |
| NLC India | D/E 1.21 |
| Bandhan Bank | EPS decline (FY26 PAT halved) + GNPA 3.11% |
| IREDA | GNPA 3.75% ≥ 3% |
| New India Assurance | P/E blank + Sep-2026 quarter loss (−₹1,249 cr) |
| Tata Chemicals | FY26 net loss (−₹1,715 cr), P/E blank |
| UPL | P/E 24.5 + FY24 net loss |
| KPI Green Energy | D/E 1.71 + **promoter pledge 44.7%** |
| Jayaswal Neco | **Promoter pledge 99.9%** + EPS decline |
| Swan Corp | **Promoter pledge 40.7%** + EPS decline |
| SBFC Finance | NNPA 1.55% vs 1.5% limit (marginal) |
| JK Tyre | D/E 1.01 (marginal) |

## 9. Cheap-for-a-reason flags inside the lists

- **IIFL Finance (#39):** FY25 profit collapsed to ₹578 cr (gold-loan regulatory action year); FY26 recovery to ₹1,817 cr is real but EPS is still below FY24.
- **Gujarat Energy (#44):** FY25 PAT/EPS spike (₹3,979 cr / ₹59.77) was an exceptional, negative-tax-rate year; FY26 is the cleaner base. Promoter (GSPC group) holding down 22 pp.
- **AWL Agri (#45):** FY24 profit base was tiny (₹148 cr); promoter transition Adani → Wilmar (−30.9 pp) is a change of control, flagged not failed.
- **Sagility (#46) / Aadhar HF (#47) / Home First (§5):** promoter declines are sponsor (PE) sell-downs post-listing — flagged per rule.
- **Indus Towers (#21):** promoter decline is Bharti's stake restructuring; FY26 EPS off the FY25 peak (Vodafone Idea-related provisions cycle).
- **J Kumar Infra (§5):** contingent liabilities exceed net worth — the only main-list name with that flag.
- **BPCL (#13) / IOCL (#9):** refining-margin cyclicality — BPCL's Jun-2026 quarter was a loss (−₹1,873 cr) inside a profitable year; the rule tests the latest quarter and full years only.
- **UCO Bank (#35) / IDBI Bank (#23):** government holding 91–95% — very thin free float.
- Cyclicals at/near 52-week highs inside the list: Petronet LNG, Karur Vysya Bank, PNB (at high).

## 10. Caveats and source problems

1. **ASM/GSM surveillance status is not shown by screener — unverified for every name** (check on NSE before acting). Same limitation as v1.
2. **Pledge visibility:** screener's page text exposed a pledge figure for only a minority of companies (it caught JP Power 73.0%, Patel Engineering 66.8%, IndusInd 42.8%, KPI Green 44.7%, Jayaswal Neco 99.9%, Swan Corp 40.7%, NCC 3.8%). For all other names pledge is recorded "n/s" — their governance pass rests on promoter-holding trend and absence of visible red flags on the page. **Re-check pledge on the exchange shareholding filing before investing.**
3. **GNPA/NNPA blanks:** on many bank/NBFC pages the NPA rows are blank (premium-gated on screener) — recorded n/s and **not** failed, per the spec's "where shown" wording. Banks passed on this proxy include HDFC Bank, ICICI Bank, PNB, Bank of Baroda, IDBI, Bank of India, REC, IRFC, HUDCO, LIC Housing, M&M Financial, Shriram Finance, Muthoot Finance. Where values were shown they were within limits (worst shown: HDB Financial GNPA 2.44% / NNPA 1.09%).
4. **D/E is computed**, not screener-printed: the fetched page text did not include a labelled Debt-to-Equity ratio, so D/E = Borrowings ÷ (Equity Capital + Reserves) on the latest balance-sheet column, as pre-agreed in the method. Utility names (NTPC, Power Grid, NHPC, NLC) fail on this leverage measure.
5. **Contingent liabilities** were extractable only where the page's Pros/Cons printed them; elsewhere n/s (no flag raised). J Kumar Infra is the one flagged passer.
6. **Rate limits / one batch on cache:** the browser fetcher hit HTTP 429s repeatedly. One batch of 15 names (marked †) was verified from screener.in **search-cache excerpts dated 9 Nov 2026 close**, cross-checked against screener-data mirrors; their CMPs/market caps are 9 Nov closes, and Intellect Design's P/E conflict (19.4 consolidated vs 20.2–20.4 in mirrors) is flagged rather than resolved.
7. **Stale/empty pages:** consolidated pages loaded empty or stale for ~20 names (IRFC, Karur Vysya, Bandhan Bank, UCO Bank, HDB Financial, City Union Bank, CSB Bank, Equitas SFB, Fedbank Financial, Tamilnad Mercantile Bank, Ujjivan SFB, Muthoot Microfin, AU SFB, GIPCL, Prakash Industries, SBFC, Home First, Can Fin Homes, Jana SFB) — the fresh standalone page was used and is noted in the CSV. **GSPL's page is stale at May 2026 on both views** — its FY26 is unverifiable, so GSPL is provisional in §6 and excluded from the headline count of fully-verified passers (99 includes it; fully-verified = 98 + GSPL provisional).
8. **Ticker corrections found during verification:** NALCO → NATIONALUM, LIC → LICI, CPCL → CHENNPETRO, J&K Bank → J&KBANK, Amara Raja → ARE&M, Finolex → FINPIPE, Sandur → SANDUMA, Onemi → KISSHT, Birlasoft → BSOFT, AvenuesAI → CCAVENUE, Archean → ACI, Pilani → PILANIINVS, Jana SFB → JSFB, Kalpataru Projects → KPIL.
9. **Growth-window note:** screener's printed 3-Y compounded growth runs FY23→FY26. Several fertiliser/chemical names (GNFC, GSFC, RCF, Maithan Alloys) had an exceptional FY23, so their printed 3-Y profit growth is negative even though FY24→FY26 profits rose — they sit in §6 by the letter of the rule.
10. **December year-ends:** Rain Industries and CIE Automotive report on a Dec year-end; the 3-year profit test was applied to their last three completed fiscal years (both fail).
11. **Ratios are point-in-time** (11 Nov 2026 intraday). P/E uses screener's TTM EPS, which for cyclicals (HPCL, BPCL, Tata Steel) can swing violently on one quarter.
12. Governance is assessed **only** on the visible proxies in the spec (pledge where shown, promoter trend, page-visible red flags). No auditor-report or exchange-filing review was performed.

**Bottom line:** 99 verified passers of criteria 1–6 (98 fully verified + GSPL provisional); 86 with positive 3-Y profit growth; top 50 tabled in §4. South Indian Bank passes v2. 12 of v1's 39 names now fail, led by the two heavy-pledge names (JP Power, Patel Engineering) and a cluster of EPS-decline names.
