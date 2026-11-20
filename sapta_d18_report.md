# SAPTA Design 18 — Report · 2026-11-18

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40/trade · no stock options.
**Spec:** `sapta_d18_SPEC.md` (pre-registered 2026-11-18). The owner rejected the programme's resting state (2026-11-18 ~06:28 IST): results must equal or exceed EKAM, by different approaches, entry points and timings. This design is a STREAM-GROSS SURVEY in the TARANG Design 23 method — seven new streams on SAPTA's rotating universe, raw and uncapped. **No book is built in this design.** A stream passes the survey only if its gross/trade is strictly > ₹40 in BOTH years AND its net is positive in both years (SPEC s.2).

## D18 universe

Rotating construction (Designs 12–17, unchanged): 69 distinct names across the 8 quarters; streams enter only on a name's active days.

## Controls (mandatory, before scoring)

- C-12a EKAM machinery control (tarang19_score.ekam_control): CAND-T5 2025 {'trades': 1035, 'net': 62164.57, 'published': 62164.57, 'diff': 0.0}, 2026 {'trades': 1025, 'net': 63883.6, 'published': 63883.6, 'diff': -0.0}; S2 2025 {'trades': 621, 'net': 45300.64, 'published': 45300.64, 'diff': 0.0}, 2026 {'trades': 615, 'net': 72605.3, 'published': 72605.3, 'diff': -0.0} → reproduced = True.
- C-18a ORB30 on the 127: got 28058 trades / gross ₹+750,127.89 (2025), 24077 / ₹+274,968.75 (2026) vs published 28058 / ₹+750,127.89, 24077 / ₹+274,968.75 → reproduced = True.
- C-18a ORB30-SHORT on the 127: got 15251 trades / gross ₹+482,882.09 (2025), 13003 / ₹+376,773.11 (2026) vs published 15251 / ₹+482,882.09, 13003 / ₹+376,773.11 → reproduced = True.
- C-18a VOLSHOCK on the 127: got 18353 trades / gross ₹+199,327.19 (2025), 16655 / ₹+402,078.96 (2026) vs published 18353 / ₹+199,327.19, 16655 / ₹+402,078.96 → reproduced = True.
- C-18b Design 16 anchor: got 424 trades / ₹+136,826.29 / ₹+24,893.52 vs published 424 / ₹+136,826.29 / ₹+24,893.52; taken set identical to sapta_d16_trades.csv = True; re-TRAIL parity {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0} → reproduced = True.
- **ALL CONTROLS PASS: True**

## Ranked stream table (binding year = the weaker gross/trade)

| Stream | Trades 25/26 | Gross/trade 25/26 | Net 2025 | Net 2026 | Full-period net | vs Cand-1 full | vs Cand-2 full | Survey |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| GF-FILL3 | 135/160 | 195.5 / 187.99 | +20,992 | +23,679 | +44,671 | -81,377 | -73,235 | ⭐ PASS |
| GF-ON2 | 135/162 | 461.62 / 47.27 | +56,918 | +1,178 | +58,096 | -67,952 | -59,810 | ⭐ PASS |
| VOLSHOCK | 2437/1924 | 29.76 / 27.6 | -24,943 | -23,860 | -48,803 | -174,852 | -166,709 | FAIL |
| GF-ON1 | 135/162 | 444.29 / 21.32 | +54,579 | -3,027 | +51,552 | -74,496 | -66,354 | FAIL |
| ORB30-SHORT | 2042/1516 | 16.62 / 20.41 | -47,749 | -29,703 | -77,452 | -203,500 | -195,358 | FAIL |
| GF-LATE | 44/61 | -2.97 / -26.77 | -1,891 | -4,073 | -5,964 | -132,012 | -123,870 | FAIL |
| GF-BAR2 | 135/162 | 106.76 / -123.75 | +9,013 | -26,527 | -17,514 | -143,562 | -135,420 | FAIL |

EKAM reference: Cand-1 +₹62,165 (2025) / +₹63,884 (2026), full-period +₹1,26,048 · Cand-2 +₹45,301 / +₹72,605, full-period +₹1,17,906. A stream's full-period net is its own 2025+2026 net on SAPTA's rotating universe, uncapped, first signal per name-day.

## GF-FILL3 — ⭐ SURVEY PASS

Signals 297 → taken 295 (no_exit_day 2).
- 2025: trades 135 · gross +26,392.28 · gross/trade +195.50 · net +20,992.28 · net/trade +155.50 · WR 55.6% · LONG gpt None · SHORT gpt 195.5 · stop share 44.4% · exits: fill 75 @ +1,172 · stop 60 @ -1,025
- 2026: trades 160 · gross +30,078.75 · gross/trade +187.99 · net +23,678.75 · net/trade +147.99 · WR 51.9% · LONG gpt None · SHORT gpt 187.99 · stop share 48.1% · exits: fill 83 @ +850 · stop 77 @ -526
- Top contributors: HINDALCO +6,951 (25 +0 / 26 +6,951) · VEDL +6,468 (25 +0 / 26 +6,468) · MAXHEALTH +6,130 (25 +6,130 / 26 +0) · SBICARD +5,420 (25 +5,420 / 26 +0) · SUNPHARMA +4,465 (25 +3,085 / 26 +1,380) · PHOENIXLTD +4,290 (25 +2,405 / 26 +1,885) · DLF +4,118 (25 +3,508 / 26 +610) · UNOMINDA +4,010 (25 +0 / 26 +4,010)

## GF-ON2 — ⭐ SURVEY PASS

Signals 297 → taken 297.
- 2025: trades 135 · gross +62,318.36 · gross/trade +461.62 · net +56,918.36 · net/trade +421.62 · WR 28.1% · LONG gpt None · SHORT gpt 461.62 · stop share 71.9% · exits: stop 97 @ -1,013 · t2_close 38 @ +4,225
- 2026: trades 162 · gross +7,657.50 · gross/trade +47.27 · net +1,177.50 · net/trade +7.27 · WR 19.1% · LONG gpt None · SHORT gpt 47.27 · stop share 79.6% · exits: stop 129 @ -613 · t2_close 33 @ +2,629
- Top contributors: UNITDSPR +19,310 (25 +19,310 / 26 +0) · HINDALCO +13,690 (25 +0 / 26 +13,690) · KALYANKJIL +11,950 (25 +11,950 / 26 +0) · SBICARD +11,750 (25 +11,750 / 26 +0) · SUNPHARMA +11,125 (25 +13,365 / 26 -2,240) · ADANIGREEN +9,560 (25 +0 / 26 +9,560) · AUBANK +9,477 (25 +6,402 / 26 +3,075) · ADANIENSOL +7,660 (25 +0 / 26 +7,660)

## VOLSHOCK — FAIL

Signals 4695 → taken 4361 (unfilled 334, skipped_days 31).
- 2025: trades 2437 · gross +72,536.63 · gross/trade +29.76 · net -24,943.37 · net/trade -10.24 · WR 40.5% · LONG gpt 52.77 · SHORT gpt 2.26 · stop share 13.8% · exits: squareoff 2100 @ +185 · stop 337 @ -939
- 2026: trades 1924 · gross +53,100.00 · gross/trade +27.60 · net -23,860.00 · net/trade -12.40 · WR 40.3% · LONG gpt 38.02 · SHORT gpt 15.44 · stop share 15.7% · exits: squareoff 1622 @ +176 · stop 302 @ -769
- Top contributors: GODFRYPHLP +23,153 (25 +23,153 / 26 +0) · COFORGE +16,628 (25 +16,628 / 26 +0) · BSE +11,541 (25 +11,541 / 26 +0) · UNITDSPR +11,492 (25 +11,492 / 26 +0) · KALYANKJIL +10,924 (25 +10,924 / 26 +0) · AUBANK +9,836 (25 +111 / 26 +9,726) · PHOENIXLTD +9,507 (25 +7,142 / 26 +2,364) · NESTLEIND +9,240 (25 +9,240 / 26 +0)

## GF-ON1 — FAIL

Signals 297 → taken 297.
- 2025: trades 135 · gross +59,978.67 · gross/trade +444.29 · net +54,578.67 · net/trade +404.29 · WR 34.1% · LONG gpt None · SHORT gpt 444.29 · stop share 63.0% · exits: next_close 50 @ +3,009 · stop 85 @ -1,064
- 2026: trades 162 · gross +3,453.15 · gross/trade +21.32 · net -3,026.85 · net/trade -18.68 · WR 22.8% · LONG gpt None · SHORT gpt 21.32 · stop share 75.3% · exits: next_close 40 @ +1,972 · stop 122 @ -618
- Top contributors: UNITDSPR +15,685 (25 +15,685 / 26 +0) · SBICARD +13,010 (25 +13,010 / 26 +0) · HINDALCO +12,280 (25 +0 / 26 +12,280) · AUBANK +8,927 (25 +5,717 / 26 +3,210) · SUNPHARMA +8,590 (25 +10,830 / 26 -2,240) · ADANIGREEN +8,230 (25 +0 / 26 +8,230) · KALYANKJIL +7,445 (25 +7,445 / 26 +0) · UNOMINDA +7,120 (25 +0 / 26 +7,120)

## ORB30-SHORT — FAIL

Signals 3589 → taken 3558 (unfilled 31, skipped_days 33).
- 2025: trades 2042 · gross +33,931.29 · gross/trade +16.62 · net -47,748.71 · net/trade -23.38 · WR 41.1% · LONG gpt None · SHORT gpt 16.62 · stop share 30.0% · exits: squareoff 1429 @ +432 · stop 613 @ -952
- 2026: trades 1516 · gross +30,936.88 · gross/trade +20.41 · net -29,703.12 · net/trade -19.59 · WR 41.8% · LONG gpt None · SHORT gpt 20.41 · stop share 35.0% · exits: squareoff 985 @ +417 · stop 531 @ -716
- Top contributors: ADANIGREEN +37,861 (25 +0 / 26 +37,861) · LODHA +21,068 (25 +18,490 / 26 +2,577) · VOLTAS +17,481 (25 +17,481 / 26 +0) · HCLTECH +15,531 (25 +15,531 / 26 +0) · KALYANKJIL +12,838 (25 +12,838 / 26 +0) · COFORGE +12,518 (25 +12,518 / 26 +0) · PHOENIXLTD +11,286 (25 +7,358 / 26 +3,928) · DLF +10,409 (25 +8,114 / 26 +2,295)

## GF-LATE — FAIL

Signals 297 → taken 105 (skipped_retraced 192).
- 2025: trades 44 · gross -130.56 · gross/trade -2.97 · net -1,890.56 · net/trade -42.97 · WR 47.7% · LONG gpt None · SHORT gpt -2.97 · stop share 15.9% · exits: squareoff 37 @ +141 · stop 7 @ -763
- 2026: trades 61 · gross -1,633.22 · gross/trade -26.77 · net -4,073.22 · net/trade -66.77 · WR 37.7% · LONG gpt None · SHORT gpt -26.77 · stop share 19.7% · exits: squareoff 49 @ +85 · stop 12 @ -482
- Top contributors: NESTLEIND +2,510 (25 +2,510 / 26 +0) · COFORGE +2,080 (25 +2,080 / 26 +0) · APLAPOLLO +1,270 (25 +1,270 / 26 +0) · BAJFINANCE +1,195 (25 +1,195 / 26 +0) · HINDALCO +795 (25 +0 / 26 +795) · KALYANKJIL +705 (25 +705 / 26 +0) · AUBANK +600 (25 +190 / 26 +410) · JINDALSTEL +490 (25 +490 / 26 +0)

## GF-BAR2 — FAIL

Signals 297 → taken 297.
- 2025: trades 135 · gross +14,413.05 · gross/trade +106.76 · net +9,013.05 · net/trade +66.76 · WR 34.1% · LONG gpt None · SHORT gpt 106.76 · stop share 52.6% · exits: squareoff 64 @ +1,355 · stop 71 @ -1,018
- 2026: trades 162 · gross -20,046.85 · gross/trade -123.75 · net -26,526.85 · net/trade -163.75 · WR 33.3% · LONG gpt None · SHORT gpt -123.75 · stop share 58.0% · exits: squareoff 68 @ +577 · stop 94 @ -631
- Top contributors: GODFRYPHLP +14,833 (25 +14,833 / 26 +0) · COFORGE +9,582 (25 +9,582 / 26 +0) · AUBANK +6,412 (25 +1,628 / 26 +4,784) · TATACONSUM +4,600 (25 +4,600 / 26 +0) · ADANIENSOL +3,890 (25 +0 / 26 +3,890) · GLENMARK +3,614 (25 +3,614 / 26 +0) · HINDALCO +3,239 (25 +0 / 26 +3,239) · FORTIS +2,794 (25 +4,538 / 26 -1,744)

## Verdict

**2 of 7 streams PASS the survey bar** (gross/trade > ₹40 AND net positive, both years): GF-FILL3, GF-ON2. Each earns a Design 19 book under the full unmoved gate. The failing streams are closed at survey cost — no book, filter or allocator is built on them.

**Design-19 seed:** build the full-gate book for each passing stream (GF-FILL3, GF-ON2) in the rotating construction — caps and allocation as in Designs 12–17, the stream's own exit frozen, placebo and audit per the programme's standing recipe; a book that also meets EKAM in both years answers the owner's bar, a book that only passes the gate does not.


## Audit (independent path — sapta_d18_audit.py)

Counters: {'csv_rows': 9210, 'audit_trades': 9210, 'key_missing_in_audit': 0, 'key_extra_in_audit': 0, 'entry_price_mismatch': 0, 'exit_price_mismatch': 0, 'exit_stamp_mismatch': 0, 'exit_reason_mismatch': 0, 'gross_mismatch': 0, 'gap_mismatch': 0, 'resum_mismatch_streams': 0}. **AUDIT CLEAN — 0 issues.** Every survey trade re-derived from the raw stores via the owner engine's loader, the active map rebuilt from the stored selections, overnight exits resolved on concatenated arrays, same-day exits via the family's audit exit; the written trades CSV re-summed per stream per year against the results file.
