# SAPTA Design 23 — Report · 2026-11-18

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40/trade · no stock options.
**Spec:** `sapta_d23_SPEC.md` (pre-registered 2026-11-18). Design 22's closure clause FIRED (2026 net ₹+28,616.67 inside the ₹21,000–₹30,000 band): the nested gap-fade union line is measured-exhausted, so this design LEAVES the allocation surface entirely — a NEW ENTRY-TIMING SURVEY in the Design 18 method: five streams that enter at different times of day or on different triggers than the first-bar gap (midday range-break, close-location fade/follow next day, second-day continuation, first-hour reversal), raw and uncapped. **No book is built in this design.** A stream passes the survey only if its gross/trade is strictly > ₹40 in BOTH years AND its net is positive in both years (SPEC s.2).

## D23 universe

Rotating construction (Designs 12–22, unchanged): 69 distinct names across the 8 quarters; streams enter only on a name's active days.

## Controls (mandatory, before scoring)

- C-1 clone parity, CAND-T5 on the frozen 25: reproduced = True (2025 {'trades': 1035, 'total': 62164.57, 'wr': 35.56, 'expectancy': 60.06}, 2026 {'trades': 1025, 'total': 63883.6, 'wr': 35.71, 'expectancy': 62.33}).
- C-1 clone parity, S2 on the frozen 25: reproduced = True (2025 {'trades': 621, 'total': 45300.64, 'wr': 34.94, 'expectancy': 72.95}, 2026 {'trades': 615, 'total': 72605.3, 'wr': 36.75, 'expectancy': 118.06}).
- C-2 exit prices vs EKAM `exit_x2p`: 53820 cells, 0 mismatches.
- C-3 vote truncated recompute: frozen-25 314 checked, 0 mismatches; SAPTA union 204 checked, 0 mismatches.
- C-4 daily clone parity: BB+RSI lists match = True; stats match = True; MACD-only lists match = True.
- **C-1..C-4 ALL PASS: True**
- C-23a Design 16 anchor: got 424 trades / ₹+136,826.29 / ₹+24,893.52 vs published 424 / ₹+136,826.29 / ₹+24,893.52; taken set identical to sapta_d16_trades.csv = True; re-TRAIL parity {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0} → reproduced = True.
- C-23b D18 anchor GF-ON1: got 135 trades / gross ₹+59,978.67 (2025), 162 / ₹+3,453.15 (2026) vs published 135 / ₹+59,978.67, 162 / ₹+3,453.15 → reproduced = True.
- C-23b D18 anchor GF-ON2: got 135 trades / gross ₹+62,318.36 (2025), 162 / ₹+7,657.50 (2026) vs published 135 / ₹+62,318.36, 162 / ₹+7,657.50 → reproduced = True.
- C-23b D18 anchor GF-FILL3: got 135 trades / gross ₹+26,392.28 (2025), 160 / ₹+30,078.75 (2026) vs published 135 / ₹+26,392.28, 160 / ₹+30,078.75 → reproduced = True.
- C-23b D18 anchor GF-BAR2: got 135 trades / gross ₹+14,413.05 (2025), 162 / ₹-20,046.85 (2026) vs published 135 / ₹+14,413.05, 162 / ₹-20,046.85 → reproduced = True.
- C-23b D18 anchor GF-LATE: got 44 trades / gross ₹-130.56 (2025), 61 / ₹-1,633.22 (2026) vs published 44 / ₹-130.56, 61 / ₹-1,633.22 → reproduced = True.
- C-23b D18 anchor ORB30-SHORT: got 2042 trades / gross ₹+33,931.29 (2025), 1516 / ₹+30,936.88 (2026) vs published 2042 / ₹+33,931.29, 1516 / ₹+30,936.88 → reproduced = True.
- C-23b D18 anchor VOLSHOCK: got 2437 trades / gross ₹+72,536.63 (2025), 1924 / ₹+53,100.00 (2026) vs published 2437 / ₹+72,536.63, 1924 / ₹+53,100.00 → reproduced = True.
- **ALL CONTROLS PASS: True**

## Ranked stream table (binding year = the weaker gross/trade)

| Stream | Trades 25/26 | Gross/trade 25/26 | Net 2025 | Net 2026 | Full-period net | vs Cand-1 full | vs Cand-2 full | Nov 2026 | Survey |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| CLR-FADE | 845/734 | 32.12 / 107.82 | -6,659 | +49,779 | +43,120 | -82,929 | -74,786 | -6,105 (50) | FAIL |
| MRB | 2739/2086 | 25.56 / 4.82 | -39,552 | -73,383 | -112,936 | -238,984 | -230,842 | +7,973 (75) | FAIL |
| CLR-FOLLOW | 845/734 | 80.65 / -8.78 | +34,349 | -35,802 | -1,453 | -127,501 | -119,359 | -6,455 (50) | FAIL |
| FHR | 1418/1252 | -36.93 / 32.07 | -109,089 | -9,930 | -119,019 | -245,067 | -236,925 | +13,215 (63) | FAIL |
| SDC | 928/937 | 33.64 / -106.14 | -5,898 | -136,937 | -142,835 | -268,883 | -260,741 | -5,803 (47) | FAIL |

EKAM reference: Cand-1 +₹62,165 (2025) / +₹63,884 (2026), full-period +₹1,26,048 · Cand-2 +₹45,301 / +₹72,605, full-period +₹1,17,906. A stream's full-period net is its own 2025+2026 net on SAPTA's rotating universe, uncapped, first signal per name-day.

## CLR-FADE — FAIL

Signals 1579 → taken 1579.
- 2025: trades 845 · gross +27,140.82 · gross/trade +32.12 · net -6,659.18 · net/trade -7.88 · WR 36.9% · LONG gpt 6.36 · SHORT gpt 61.19 · stop share 49.4% · exits: day_close 428 @ +1,006 · stop 417 @ -968
- 2026: trades 734 · gross +79,138.73 · gross/trade +107.82 · net +49,778.73 · net/trade +67.82 · WR 38.3% · LONG gpt 186.72 · SHORT gpt 54.8 · stop share 52.7% · exits: day_close 347 @ +1,073 · stop 387 @ -758
- November 2026 slice: 50 trades · net ₹-6,105.06.
- Top contributors: PHOENIXLTD +29,160 (25 +21,145 / 26 +8,015) · VOLTAS +13,304 (25 +13,304 / 26 +0) · BSE +13,100 (25 +13,100 / 26 +0) · LAURUSLABS +11,439 (25 +7,712 / 26 +3,727) · AUBANK +10,688 (25 +2,944 / 26 +7,744) · TATACONSUM +9,557 (25 +9,557 / 26 +0) · APLAPOLLO +7,767 (25 +7,767 / 26 +0) · CGPOWER +6,395 (25 +0 / 26 +6,395)

## MRB — FAIL

Signals 4979 → taken 4825 (unfilled 154, skipped_days 33).
- 2025: trades 2739 · gross +70,007.62 · gross/trade +25.56 · net -39,552.38 · net/trade -14.44 · WR 41.8% · LONG gpt 62.04 · SHORT gpt -4.05 · stop share 16.7% · exits: squareoff 2282 @ +229 · stop 457 @ -992
- 2026: trades 2086 · gross +10,056.55 · gross/trade +4.82 · net -73,383.45 · net/trade -35.18 · WR 42.8% · LONG gpt -0.89 · SHORT gpt 9.49 · stop share 20.8% · exits: squareoff 1653 @ +204 · stop 433 @ -756
- November 2026 slice: 75 trades · net ₹+7,973.18.
- Top contributors: GODFRYPHLP +18,372 (25 +18,372 / 26 +0) · LODHA +14,130 (25 +11,877 / 26 +2,253) · MFSL +9,074 (25 +9,074 / 26 +0) · SUNPHARMA +9,002 (25 +4,404 / 26 +4,598) · BSE +8,435 (25 +8,435 / 26 +0) · HCLTECH +8,317 (25 +8,317 / 26 +0) · PHOENIXLTD +8,089 (25 +15,333 / 26 -7,244) · ADANIGREEN +6,899 (25 +0 / 26 +6,899)

## CLR-FOLLOW — FAIL

Signals 1579 → taken 1579.
- 2025: trades 845 · gross +68,149.06 · gross/trade +80.65 · net +34,349.06 · net/trade +40.65 · WR 38.0% · LONG gpt 86.89 · SHORT gpt 75.12 · stop share 49.7% · exits: day_close 425 @ +1,128 · stop 420 @ -980
- 2026: trades 734 · gross -6,442.18 · gross/trade -8.78 · net -35,802.18 · net/trade -48.78 · WR 33.4% · LONG gpt -23.96 · SHORT gpt 13.82 · stop share 57.5% · exits: day_close 312 @ +1,040 · stop 422 @ -784
- November 2026 slice: 50 trades · net ₹-6,455.49.
- Top contributors: UNOMINDA +17,733 (25 +6,501 / 26 +11,232) · BSE +17,132 (25 +17,132 / 26 +0) · KALYANKJIL +13,302 (25 +13,302 / 26 +0) · ADANIGREEN +12,235 (25 +0 / 26 +12,235) · LODHA +11,750 (25 +7,990 / 26 +3,760) · UNITDSPR +11,656 (25 +11,656 / 26 +0) · GLENMARK +8,712 (25 +8,712 / 26 +0) · GODFRYPHLP +7,554 (25 +7,554 / 26 +0)

## FHR — FAIL

Signals 2670 → taken 2670 (skipped_days 33).
- 2025: trades 1418 · gross -52,369.22 · gross/trade -36.93 · net -109,089.22 · net/trade -76.93 · WR 38.4% · LONG gpt -43.19 · SHORT gpt -29.85 · stop share 42.4% · exits: squareoff 816 @ +660 · stop 602 @ -982
- 2026: trades 1252 · gross +40,150.03 · gross/trade +32.07 · net -9,929.97 · net/trade -7.93 · WR 41.9% · LONG gpt 45.3 · SHORT gpt 17.28 · stop share 41.8% · exits: squareoff 729 @ +621 · stop 523 @ -789
- November 2026 slice: 63 trades · net ₹+13,214.52.
- Top contributors: AUROPHARMA +31,149 (25 +0 / 26 +31,149) · BHARATFORG +22,597 (25 +0 / 26 +22,597) · ZYDUSLIFE +15,761 (25 +0 / 26 +15,761) · HCLTECH +6,058 (25 +6,058 / 26 +0) · BAJFINANCE +5,012 (25 +5,012 / 26 +0) · MFSL +4,429 (25 +4,429 / 26 +0) · UNOMINDA +4,067 (25 +2,201 / 26 +1,866) · HAVELLS +3,792 (25 +3,792 / 26 +0)

## SDC — FAIL

Signals 1865 → taken 1865.
- 2025: trades 928 · gross +31,222.09 · gross/trade +33.64 · net -5,897.91 · net/trade -6.36 · WR 32.4% · LONG gpt -95.71 · SHORT gpt 183.45 · stop share 58.6% · exits: day_close 384 @ +1,482 · stop 544 @ -989
- 2026: trades 937 · gross -99,456.87 · gross/trade -106.14 · net -136,936.87 · net/trade -146.14 · WR 27.2% · LONG gpt -138.87 · SHORT gpt -68.54 · stop share 65.5% · exits: day_close 323 @ +1,027 · stop 614 @ -702
- November 2026 slice: 47 trades · net ₹-5,803.24.
- Top contributors: LODHA +27,094 (25 +26,008 / 26 +1,086) · ADANIENSOL +26,164 (25 +0 / 26 +26,164) · PHOENIXLTD +21,158 (25 +19,373 / 26 +1,785) · SBICARD +17,365 (25 +17,365 / 26 +0) · BSE +9,912 (25 +9,912 / 26 +0) · JINDALSTEL +9,472 (25 +9,472 / 26 +0) · KALYANKJIL +7,791 (25 +7,791 / 26 +0) · SBILIFE +7,285 (25 +7,285 / 26 +0)

## Verdict

**No stream passes the survey bar.** The strongest is CLR-FADE (gross/trade 32.12 / 107.82, net -6,659 / +49,779) — reported plainly: on this universe, none of the five new entry timings carries a raw edge above the ₹40 levy in both years, so none earns a book. The gated books (D13/D16/D17/D19-FILL3/D21/D22) stand as the programme's books; 2026 power remains the open wound.

**Design-24 seed (per SPEC s.7, no survivor):** the timing surface is now surveyed out alongside the allocation surface — Design 24 changes the SELECTION surface instead: stock-level cross-sectional relative strength inside the rotating universe (monthly rank of the active names by trailing return, hold the top rank band for the following month, exits by rank decay — no intraday timing signal at all), pre-registered fresh with its own survey bar; the per-stream anatomy above is its starting evidence.


## Audit (independent path — sapta_d23_audit.py)

Counters: {'csv_rows': 12518, 'audit_trades': 12518, 'key_missing_in_audit': 0, 'key_extra_in_audit': 0, 'entry_price_mismatch': 0, 'exit_price_mismatch': 0, 'exit_stamp_mismatch': 0, 'exit_reason_mismatch': 0, 'gross_mismatch': 0, 'sig_value_mismatch': 0, 'resum_mismatch_streams': 0}. **AUDIT CLEAN — 0 issues.** Every survey trade re-derived from the raw stores via the owner engine's loader, the active map rebuilt from the stored selections, intraday exits via the family's audit exit, day-hold exits via a two-phase numpy stop scan; the written trades CSV re-summed per stream per year against the results file.
