# Engine 2 — Value-Stock Screener (P/B < 1, low P/E)

**Date of all figures: Wednesday, 11 November 2026** (screener.in pages fetched 11 Nov 2026, ~10:17–10:25 IST, prices intraday unless noted).
**Source: screener.in** — two public screens (fetched in full) plus individual company pages. Fallback sources were needed only for cross-checks (see "Data-source problems").
**This is a fundamental shortlist only — no buy/sell recommendation.** The owner does his own price-action confirmation before any investment.

---

## 1. Method and filters

**Universe.** Union of two screener.in screens, every page fetched on 2026-11-11:
- Screen 1416292 "Price to book value less than 1" — 88 results, 4 pages.
- Screen 2205120 "BelowBookStocks" (query: `Price to book value <1 AND Market Capitalization >500 AND Market Capitalization <10000 AND Debt to Equity <1`) — 158 results, 7 pages.

Neither screen alone is the complete P/B < 1 universe (1416292 has unexplained extra filtering; 2205120 caps market cap at ₹10,000 cr), so the pool is the **union** of both.

**Primary filters, applied in order:**
1. NSE-listed equity.
2. **P/B < 1.0** — recomputed at company-page level as CMP ÷ Book Value per share (book values updated to Sep-2026 results). Where a company reports consolidated accounts, the **consolidated** page governs (standalone pages of holding/investment companies are misleading — see §7).
3. **Positive net profit** — latest financial year AND latest reported quarter.
4. **Debt-to-Equity < 1** — banks/NBFCs/HFCs/MFIs/insurers exempt per the brief; for banking names GNPA%/NNPA% are reported instead where screener shows them. For non-financials with market cap ≥ ₹10,000 cr (outside screen 2205120's D/E sieve), D/E was verified individually from the balance sheet (ONGC ≈ 0.08 ✓, IOCL ≈ 0.59 ✓).
5. **Market cap ≥ ₹500 cr.**
6. ASM/GSM surveillance: **not shown by screener — unverified for every name** (check on NSE before acting).

**"Low P/E" presentation rule (disclosed, not silent):** the brief asks to report actual P/E and flag < 15. The **main shortlist = all hard filters passed AND P/E < 15**. Hard-passing names with P/E 15–40 are in Annexure A; P/E > 40 or blank (earnings negligible / exceptional-driven) are excluded entirely.

**Selection for the table:** ≈ 90 names passed all hard filters with P/E < 15 at screen level. The **39 largest by market cap** are tabled below and were **individually verified on their screener company pages** (one exception: GSPL, flagged). The remaining passers are all below ~₹2,100 cr market cap and were not individually page-verified.

**Profit-positive evidence:** for names in both screens, NP (12M) comes from screen 1416292 and NP (latest quarter) from the screens/company pages. For screen-2205120-only names, a present, positive P/E was taken as TTM-profit-positive evidence.

---

## 2. Reference row — the owner's holding

### South Indian Bank (SOUTHBANK) — reference only, no longer passes P/B < 1
| CMP | Book Value | P/B | P/E | ROE | ROCE | Div Yield | Market Cap | 52w High/Low | 1Y Return | GNPA / NNPA | Promoter |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ₹60.6 (+3.15% on 11 Nov) | ₹46.1 | **1.31** | 10.0 | 13.5% | 6.42% | 0.75% | ₹15,866 cr | 60.6 / 33.4 | +51% | 1.24% / 0.09% (Sep-2026 qtr) | None — widely held (FII 25.57%, DII 16.78%, Public 57.65%) |

- Owner's stated CMP (~₹60) **verified**: ₹60.6 intraday on 11 Nov 2026 (₹58.68 close on 9 Nov).
- FY26 net profit ₹1,455 cr; TTM ₹1,586 cr; latest quarter (Sep-2026) ₹426 cr.
- **Key point:** at ~₹60.6 the stock now trades **above** book value (P/B ≈ 1.31) — it no longer passes the P/B < 1 filter itself. At the owner's ~₹41 buy price it did (41 / 46.1 = 0.89). It is the template of what he bought, not a current passer.
- **Source disagreement (footnoted per brief):** some aggregators show P/B ≈ 0.78, implying book value ≈ ₹74. That is internally inconsistent (one such source simultaneously showed P/B 1.27) and is contradicted by the filing-based book value of ₹46.1 (net worth ₹12,077 cr at 30 Sep 2026). The screener.in figure governs.

---

## 3. Main shortlist — 39 names passing ALL primary filters with P/E < 15

Sorted by market cap, largest first. P/B computed as CMP ÷ Book Value from the screener company page (consolidated where applicable). "Exempt" = bank/NBFC/HFC/MFI/insurer, D/E filter not applied per brief. "n/s" = not shown on the screener page.

| # | Company | CMP ₹ | BV ₹ | P/B | P/E | D/E | ROE % | ROCE % | DivY % | MCap ₹ cr | 52w H/L | 1Y % | Promoter % | GNPA/NNPA % | Flags |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | ONGC | 235 | 289 | 0.81 | 6.24 | 0.08 | 10.2 | 13.0 | 5.62 | 2,95,825 | 308/218 | −6 | 58.89 | n/a | — |
| 2 | Indian Oil Corporation | 148 | 154 | 0.96 | 4.87 | 0.59 | 19.0 | 17.3 | 5.59 | 2,08,783 | 189/125 | −15 | 51.50 | n/a | Jun-2026 quarter was a loss (−₹2,661 cr) on refining margins; latest quarter +₹21,630 cr — earnings are cyclical |
| 3 | Punjab National Bank | 135 | 140 | 0.96 | 6.80 | Exempt | 13.0 | 6.13 | 2.22 | 1,55,212 | 135/98.5 | +8 | 70.08 | n/s | Price at its 52-week high |
| 4 | Bank of Baroda | 269 | 312 | 0.86 | 6.20 | Exempt | 13.8 | 5.66 | 3.18 | 1,39,032 | 326/224 | −9 | 63.97 | 1.78/0.37 | — |
| 5 | Canara Bank | 130 | 136 | 0.96 | 6.00 | Exempt | 18.1 | 6.55 | 3.25 | 1,17,964 | 163/115 | −9 | 62.93 | 1.33/0.30 | — |
| 6 | Power Finance Corporation | 342 | 445 | 0.77 | 4.30 | Exempt | 20.7 | 9.71 | 5.42 | 1,12,995 | 486/310 | −10 | 55.99 | 0.55/0.13 | — |
| 7 | REC Ltd | 311 | 362 | 0.86 | 5.40 | Exempt | 20.1 | 9.71 | 5.98 | 81,959 | 388/282 | −16 | 52.63 | n/s | — |
| 8 | Bank of India | 149 | 202 | 0.74 | 5.69 | Exempt | 12.4 | 5.92 | 3.12 | 68,017 | 178/124 | 0 | 73.38 | 1.60/0.42 | — |
| 9 | General Insurance Corp (GIC Re) | 338 | 423 | 0.80 | 6.60 | ~0 | 14.6 | 17.4 | 3.92 | 59,290 | 418/308 | −13 | 77.40 | n/a (insurer) | — |
| 10 | UCO Bank | 25.2 | 27.6 | 0.91 | 10.6 | Exempt | 8.61 | 5.55 | 1.77 | 31,600 | 32.1/21.3 | −23 | 90.95 | 1.96/0.18 | Govt holds 90.95% → very low free float; ROE modest |
| 11 | LIC Housing Finance | 560 | 798 | 0.70 | 5.22 | Exempt | 14.4 | 8.59 | 1.76 | 30,776 | 598/459 | −3 | 45.24 | n/s | — |
| 12 | Central Bank of India | 32.5 | 45.4 | 0.72 | 6.13 | Exempt | 11.6 | 5.61 | 3.73 | 29,417 | 40.9/28.3 | −17 | 81.19 | 2.39/0.31 | — |
| 13 | Jammu & Kashmir Bank | 133 | 161 | 0.83 | 6.24 | Exempt | 15.2 | 5.83 | 0.00 | 14,657 | 202/97.4 | +21 | 59.40 | 2.23/0.51 | — |
| 14 | Karnataka Bank | 346 | 368 | 0.94 | 8.45 | Exempt | 10.4 | 6.06 | 1.45 | 13,111 | 349/174 | +87 | None (widely held) | 2.27/0.74 | Near 52-week high after a +87% 1-year run |
| 15 | JM Financial | 114 | 115 | 0.99 | 10.7 | Exempt | 11.9 | 11.6 | 2.84 | 10,953 | 165/103 | −24 | 57.95 | n/a (NBFC) | P/B borderline (0.99) |
| 16 | Jaiprakash Power Ventures | 14.4 | 19.3 | 0.75 | 8.27 | 0.23 | 3.60 | 6.97 | 0.00 | 9,862 | 24.5/12.4 | −22 | 24.00 | n/a | **CHEAP-FOR-A-REASON RISK: promoters have pledged 73.0% of their holding; ROE only 3.6%** |
| 17 | GR Infraprojects | 801 | 1,037 | 0.77 | 7.47 | 0.60 | 9.20 | 11.9 | 0.32 | 7,751 | 1,159/730 | −31 | 74.69 | n/a | — |
| 18 | Kama Holdings | 2,153 | 2,722 | 0.79 | 5.80 | 0.63 | 12.6 | 14.0 | 1.95 | 6,910 | 3,048/2,062 | −27 | 75.00 | n/a | Core investment co (SRF holdco) — consolidated figures; standalone page shows P/B 4.18 and is misleading |
| 19 | Gujarat Narmada Valley Fertilizers (GNFC) | 470 | 625 | 0.75 | 6.66 | 0.01 | 9.15 | 12.2 | 4.47 | 6,905 | 636/365 | −5 | 41.30 | n/a | — |
| 20 | Bengal & Assam Company | 5,856 | 9,372 | 0.62 | 8.69 | 0.06 | 8.11 | 3.92 | 0.85 | 6,678 | 7,640/5,312 | −22 | 72.87 | n/a | Core investment co (JK group) — holdco discount structure |
| 21 | Equitas Small Finance Bank | 57.2 | 57.3 | 1.00 (0.998) | 9.32 | Exempt | 1.68 | 6.43 | 0.00 | 6,550 | 83.9/47.3 | −4 | None | 2.29/0.70 | **CHEAP-FOR-A-REASON RISK: profits collapsed FY24 ₹799 cr → FY25 ₹147 cr → FY26 ₹103 cr (MFI stress); latest quarter recovered to +₹218 cr; MD & CEO resigned 6 Nov 2026 (interim in place); P/B borderline** |
| 22 | Birla Corporation | 821 | 988 | 0.83 | 12.5 | 0.40 | 7.83 | 9.78 | 1.52 | 6,323 | 1,198/756 | −30 | 62.90 | n/a | Latest-quarter net profit fell ~59% YoY to ₹37 cr |
| 23 | Gujarat State Fertilizers (GSFC) | 144 | 324 | 0.44 | 10.7 | 0.05 | 5.40 | 7.06 | 3.51 | 5,724 | 199/132 | −23 | 37.84 | n/a | ROE only 5.4% — deep discount but low-return business |
| 24 | Pilani Investment & Industries | 4,111 | 16,328 | 0.25 | 13.5 | 0.14 | 0.20 | 1.41 | 0.21 | 4,552 | 5,850/3,672 | −23 | 58.68 | n/a | **CHEAP-FOR-A-REASON RISK: ROE ~0.2%; earnings are lumpy investment fair-value swings with some loss quarters — classic holdco discount (NBFC core investment co, Birla group)** |
| 25 | Jana Small Finance Bank | 412 | 462 | 0.89 | 9.16 | Exempt | 7.60 | 7.45 | 0.00 | 4,362 | 607/330 | −12 | 16.87 | 2.34/1.17 | NNPA rose to 1.17% (from 0.91% in Jun-2026); promoter holding low and falling (22.5% → 16.9%) |
| 26 | PTC India | 142 | 182 | 0.78 | 9.04 | 0.26 | 10.3 | 13.4 | 16.2 | 4,193 | 230/131 | −15 | 16.22 | n/a | Dividend yield 16.2% is special-dividend inflated; earnings include ₹345 cr other income; consolidated BV used (standalone BV ₹138 gives P/B 1.03 — see §7) |
| 27 | PNC Infratech | 135 | 283 | 0.48 | 5.57 | 0.82 | 6.12 | 7.97 | 0.45 | 3,463 | 291/116 | −52 | 56.25 | n/a | Sales shrinking (3Y −12%); contingent liabilities ₹3,729 cr; profits include large other income |
| 28 | Gujarat State Petronet (GSPL) | 110.15* | n/a* | 0.50* | 11.29* | 0.00* | n/a* | 6.64* | 0.00* | 3,445* | n/a* | n/a* | n/a* | n/a | **DATA FLAG: screener company page serves a stale May-2026 snapshot — all figures marked * are from the 11-Nov screens, not a company page. Verify before use** |
| 29 | J Kumar Infraprojects | 441 | 445 | 0.99 | 8.56 | 0.18 | 12.4 | 18.4 | 0.93 | 3,336 | 623/400 | −32 | 46.64 | n/a | P/B borderline (0.99); contingent liabilities ₹4,383 cr exceed net worth; Sep-2026 results due 13 Nov (latest reported quarter Jun-2026) |
| 30 | KNR Constructions | 114 | 177 | 0.64 | 9.38 | 0.49 | 8.84 | 10.4 | 0.22 | 3,205 | 186/96.1 | −37 | 48.81 | n/a | FY26 revenue and profit fell sharply (TTM profit growth −67%); working-capital days stretched to 312 |
| 31 | Vindhya Telelinks | 2,573 | 3,940 | 0.65 | 11.9 | 0.33 | 5.31 | 8.15 | 0.24 | 3,049 | 2,999/960 | +90 | 43.55 | n/a | Price already +90% in 1 year; debtor days 212; consolidated figures (standalone page misleading); Birla Cable amalgamation in progress at NCLT |
| 32 | Satin Creditcare Network | 266 | 287 | 0.93 | 5.50 | Exempt | 12.3 | 13.8 | 0.00 | 2,933 | 274/136 | +71 | 36.17 | n/s | Near 52-week high after +71% 1-year run; NBFC-MFI sector risk |
| 33 | Route Mobile | 461 | 462 | 1.00 (0.998) | 8.33 | 0.01 | 12.6 | 17.4 | 2.38 | 2,906 | 771/407 | −33 | 74.85 | n/a | P/B borderline (~1.0; screener's own text says 0.97×); one loss quarter (Sep-2025, −₹19 cr) in the last eight; promoter is Proximus Group |
| 34 | Muthoot Microfin | 166 | 179 | 0.93 | 8.66 | Exempt | 6.22 | 9.31 | 0.00 | 2,824 | 263/134 | −4 | 55.47 | 3.38/1.05 | **CHEAP-FOR-A-REASON RISK: FY25 was a loss year (−₹223 cr, MFI stress); GNPA peaked at 4.85% (Jun-2025), now 3.38% and improving; FY26 back to profit (+₹170 cr), latest quarter +₹111 cr** |
| 35 | Ramco Industries | 317 | 534 | 0.60 | 8.52 | 0.00 | 6.75 | 4.57 | 0.39 | 2,765 | 396/231 | −2 | 54.84 | n/a | Consolidated figures (page snapshot = 9 Nov close); market value of its investments (₹5,334 cr, mainly Ramco Cements) exceeds its own market cap; standalone BV gives P/B 1.90 and is misleading |
| 36 | Patel Engineering | 25.7 | 47.1 | 0.55 | 6.62 | 0.29 | 8.95 | 13.3 | 0.00 | 2,548 | 37.4/22.0 | −26 | 31.49 | n/a | **CHEAP-FOR-A-REASON RISK: promoters have pledged 66.8% of their holding; promoter stake down from 61.9% (2020) to 31.5%; contingent liabilities ₹2,995 cr** |
| 37 | Maithan Alloys | 858 | 1,567 | 0.55 | 5.45 | 0.09 | −0.49† | 6.08 | 1.97 | 2,498 | 1,210/760 | −23 | 74.96 | n/a | Profits dominated by investment fair-value income (other income ₹305 cr vs operating profit ₹236 cr); Mar-2026 quarter was a loss; latest quarter boosted by a deferred-tax reversal. †Screener's headline ROE prints −0.49% despite FY26 PAT of +₹435 cr — treat earnings quality as the story here, not the ratio |
| 38 | Repco Home Finance | 389 | 684 | 0.57 | 4.93 | Exempt | 12.4 | 10.1 | 1.93 | 2,436 | 444/294 | −10 | 37.13 | n/s | Steady profit record (FY26 ₹475 cr, latest quarter ₹119 cr) |
| 39 | India Glycols | 313 | 438 | 0.71 | 6.63 | 0.58 | 11.3 | 12.4 | 2.40 | 2,101 | 400/168 | +46 | 59.63 | n/a | +46% in 1 year already; demerged IGL Spirits listed 4 Nov 2026; Sep-2026 results due 13 Nov (latest reported quarter Jun-2026) |

*GSPL row: screen-level data only — see flag.

---

## 4. Near-misses — P/B between 1.0 and 1.2, everything else passing (2 names)

These do **not** pass the P/B < 1 filter today. Listed separately, as permitted, because every other primary filter passes.

| Company | CMP ₹ | BV ₹ | P/B | P/E | ROE % | ROCE % | DivY % | MCap ₹ cr | 52w H/L | 1Y % | Promoter % | GNPA/NNPA % | Note |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Union Bank of India | 199 | 189 | 1.05 | 6.89 | 15.7 | 6.30 | 2.52 | 1,51,985 | 205/146 | +29 | 74.76 | n/s | Only the P/B keeps it out; profit growth strong (FY26 NP ₹19,430 cr) |
| Steel Authority of India (SAIL) | 175 | 146 | 1.20 (screener text: 1.16×) | 12.3 | 6.62 | 7.97 | 1.34 | 72,408 | 210/124 | +17 | 65.00 | n/a | D/E 0.52 ✓; at the very top edge of the near-miss band; ROE low |

The reference stock, South Indian Bank (P/B 1.31), sits above even this band.

---

## 5. Annexure A — pass all hard filters but P/E ≥ 15 (not in the main list)

The P/E < 15 cut is a presentation rule from the brief's "flag those < 15", so these are shown separately rather than dropped. This annexure is **not exhaustive** — it lists the names individually verified during enrichment.

| Company | CMP ₹ | BV ₹ | P/B | P/E | ROE % | MCap ₹ cr | Note |
|---|---|---|---|---|---|---|---|
| Kirloskar Industries | 3,506 (9 Nov close) | 7,496 | 0.47 | 15.0 on company page (14.89 on screen) — borderline | 3.77 | 3,687 | Core investment co (Kirloskar Ferrous); D/E 0.18 ✓; ROE low |
| TTK Healthcare | screen data only | — | < 1 (screen) | 18.34 (screen) | — | — | Latest-quarter profit (₹222.97 cr) is most of the full-year figure (₹276.54 cr) — exceptional gain suspected; verify before use |

## 6. Annexure B — passed the screens, could not be fully verified

| Company | What the screen/key-points show | Why it is not in the main list |
|---|---|---|
| Prakash Industries | CMP ₹119, P/E 5.49, BV ₹174, P/B 0.68, ROE 14.1%, DivY 1.54%, MCap ₹2,123 cr, promoter 44.38% | Screener's company page serves stale FY2018 financial tables (only the Key Points header is current), so latest-year/quarter profit and current D/E **could not be verified** from a fetched page. Verify on NSE/Trendlyne before considering. |

## 7. Excluded on final verification (shown so the funnel is auditable)

| Company | Reason |
|---|---|
| Gujarat Industries Power (GIPCL) | Passed the screens, but its Sep-2026 balance sheet gives **D/E = ₹4,156 cr borrowings ÷ ₹3,976 cr equity = 1.05 ≥ 1** (new project debt; CWIP ₹2,516 cr). Fails the D/E filter. (At Mar-2026 it was 0.94 — it crossed 1.0 only in the latest half-year.) |
| HG Infra Engineering, Rain Industries | Appear in the P/B screen but are absent from the D/E < 1 screen — treated as D/E ≥ 1 fails. |
| Coffee Day Enterprises | P/E 212.85 — earnings negligible; excluded by the P/E rule. |
| Prozone Realty | P/E blank while reported profit (NP Qtr ₹566 cr, NP 12M ₹578 cr) is exceptional-item driven — excluded and flagged as a data-quality case. |

---

## 8. Caveats — read before using this list

1. **Point-in-time ratios.** Every figure is as fetched on 11 Nov 2026 (mostly intraday ~10:20 IST). CMPs move; a borderline name (Equitas 0.998, Route Mobile ~1.0, JM Financial 0.99, J Kumar 0.99) can cross P/B = 1 on any given day.
2. **Below book value is a starting point, not a bargain certificate.** A stock trades below book because the market doubts the book — asset quality (banks), low returns on equity, governance, or pledged promoter shares. Names carrying a **"cheap-for-a-reason risk"** flag in the table (Jaiprakash Power, Equitas SFB, Pilani Investment, Muthoot Microfin, Patel Engineering, and earnings-quality flags on Maithan Alloys, PTC India, PNC Infratech, KNR) need the deepest checking before any price-action work.
3. **Book value is an accounting number.** For PSU banks it depends on NPA recognition; for holding companies (Kama, Bengal & Assam, Pilani, Kirloskar, Ramco Industries) the discount to book is structural and can persist for years — the "value" is the underlying listed stakes, not the operating business.
4. **Consolidated vs standalone matters.** Four names (Kama Holdings, PTC India, Vindhya Telelinks, Ramco Industries) show P/B **above** 1 on their standalone pages and below 1 consolidated. This file uses consolidated throughout, consistent with how the screens compute the ratio — but know which book you are looking at before comparing with another source.
5. **Earnings quality varies widely in this list.** Several passers' profits include large "other income" / fair-value gains (Maithan Alloys, PTC India, Pilani, Vindhya, PNC). The filter only required profits to be positive, not clean.
6. **ASM/GSM surveillance status was not verifiable** from screener.in for any name — check the NSE surveillance list before acting on the smaller caps.
7. **GNPA/NNPA** are shown only where screener's page prints them; "n/s" means the page did not show the rows (common on consolidated pages), not that asset quality is clean.
8. Nothing here is a recommendation. The owner's process is: fundamental shortlist (this file) → his own price-action confirmation → decision.

---

## 9. Data-source problems encountered (all on 2026-11-11)

1. **Screener's raw query endpoint returned 404** — the universe was built from two public screens instead (see §1).
2. **Screen 2205120 pagination anomaly:** fetching page 1 with a sort parameter (`?order=asc`) produced duplicates/gaps versus the other pages. Page 1 was refetched with the default sort; the corrected page 1 governs (it changed several D/E readings, e.g. Route Mobile D/E 0.01 confirmed in-screen).
3. **GSPL's company page is stale:** both the standalone and consolidated screener pages serve a snapshot dated 11 May 2026 (CMP ₹268, market cap ₹15,141 cr) that contradicts the 11-Nov screens (CMP ₹110.15, market cap ₹3,445 cr). GSPL is carried on screen data only and flagged in the table.
4. **Muthoot Microfin's consolidated page rendered with every field blank.** The standalone page rendered correctly and was used (its Q2 FY27 PAT of ₹110.8 cr also matches the company's press release carried on the same page).
5. **Prakash Industries' company page serves stale FY2018 financial tables** — moved to Annexure B (unverifiable), not the main list.
6. **Two company pages were 9-Nov close snapshots** (Ramco Industries consolidated, Kirloskar Industries) — crawled 10 Nov; one day stale, noted in their rows.
7. **Jana Small Finance Bank's screener slug is JSFB** — the obvious slugs (JANA, JANASFB) return 404.
8. **South Indian Bank P/B disagreement across aggregators** (≈0.78 vs screener's 1.31) — resolved in favour of the filing-based book value, footnoted in §2.
9. Screener does not display **ASM/GSM** status anywhere used here — left unverified rather than assumed.

---

*Prepared 2026-11-11. Companion file: `value_screener_2026-11-11.csv` (same shortlist in spreadsheet form). Research only — no orders placed, no account accessed.*
