# SarvaRitu forward paper test — daily summary
Frozen book, paper only, real Rs0, provisional per 100 shares, Rs40/trade.

- 2026-11-02 | NO MARKET DATA (nifty_missing=True, symbols_missing=25) — nothing logged
- 2026-11-02 | regime DOWN | trades 4 (F4 2, INV-LONG 1, N4-V3 1) | day net +1455.27 | 2026-11 running +1455.27 (4 tr) | DATA_MISSING: none
- 2026-11-02 | regime DOWN | trades 0 (none) | day net +0.00 | 2026-11 running +1455.27 (4 tr) | DATA_MISSING: none
- 2026-11-02 | CORRECTION (fetch-layer repair, same day): the NO MARKET DATA line above records the failed 16:35 run — the v3 range endpoints omit the current day; the logger now tops up from the v3 intraday endpoint. Recovered Day 1: regime DOWN | trades 4 (F4 2, INV-LONG 1, N4-V3 1) | day net +1455.27 | 2026-11 running +1455.27 (4 tr). NTPC N4-V3 LONG 09:35 @ 325.30, stop exit 322.70, net -300.24 — matches the live-shadow producer exactly. GODREJCP P2F correctly NOT taken by the book: reaction -2.27% is below the frozen >=2.5% band (it traded only in the separate P2F shadow scorecard). Idempotency re-run logged 0 new rows (its "trades 0" line above is that verification run).
- 2026-11-03 | regime FLAT | trades 1 (R2-LOWBAND 1) | day net -451.85 | 2026-11 running +1003.42 (5 tr) | DATA_MISSING: none
- 2026-11-04 | regime FLAT | trades 6 (INV-ABOVE 3, P2F 2, R2-LOWBAND 1) | day net -420.94 | 2026-11 running +582.48 (11 tr) | DATA_MISSING: none
- 2026-11-05 | regime FLAT | trades 5 (INV-ABOVE 1, N4-V3 2, P2F-R2 2) | day net -299.28 | 2026-11 running +283.20 (16 tr) | DATA_MISSING: none
- 2026-11-06 | regime FLAT | trades 4 (INV-ABOVE 3, P2F 1) | day net +6577.68 | 2026-11 running +6860.88 (20 tr) | DATA_MISSING: none
- 2026-11-09 | regime UP | trades 4 (INV-ABOVE 2, N4-V3 1, P2F-R2 1) | day net +704.30 | 2026-11 running +7565.18 (24 tr) | DATA_MISSING: none
- 2026-11-10 | NO MARKET DATA (nifty_missing=True, symbols_missing=25) — nothing logged
- 2026-11-11 | regime UP | trades 2 (N4-V3 1, P2F 1) | day net +826.10 | 2026-11 running +8391.28 (26 tr) | DATA_MISSING: none
- 2026-11-12 | regime UP | trades 4 (INV-ABOVE 1, N4-V3 1, P2F 1, P2F-R2 1) | day net -425.54 | 2026-11 running +7965.74 (30 tr) | DATA_MISSING: none
- 2026-11-13 | regime UP | trades 2 (INV-ABOVE 1, N4-V3 1) | day net -447.80 | 2026-11 running +7517.94 (32 tr) | DATA_MISSING: none
