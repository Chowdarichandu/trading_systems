# SAPTA Design 17 — Report · 2026-11-18

**Basis:** paper only, real money ₹0 · equity cash, PROVISIONAL per 100 shares, ₹40/trade · no stock options.
**Spec:** `sapta_d17_SPEC.md` (pre-registered 2026-11-18). Intraday only — the Daily line closed in Design 14. One book: Design 16's UNION stream restricted to the Nifty Bank, Nifty Healthcare and Nifty Realty sleeves, one cap with TRAIL exits in Design 13's quarterly-rotating construction (SPEC s.2).

## D17 selections

Rotating construction (Designs 13/15/16, unchanged): 69 distinct names across the 8 quarters; quarterly top-7 indices and stored picks as in `sapta_d17_selections.json`. Focus restriction (SPEC s.2): 15 distinct names hold at least one focus-eligible day (A4 owner in Nifty Bank / Nifty Healthcare / Nifty Realty).

## Controls (mandatory, before scoring)

- C-1 clone parity, CAND-T5 on the frozen 25: reproduced = True (2025 {'trades': 1035, 'total': 62164.57, 'wr': 35.56, 'expectancy': 60.06}, 2026 {'trades': 1025, 'total': 63883.6, 'wr': 35.71, 'expectancy': 62.33}).
- C-1 clone parity, S2 on the frozen 25: reproduced = True (2025 {'trades': 621, 'total': 45300.64, 'wr': 34.94, 'expectancy': 72.95}, 2026 {'trades': 615, 'total': 72605.3, 'wr': 36.75, 'expectancy': 118.06}).
- C-2 exit prices vs EKAM `exit_x2p`: 53820 cells, 0 mismatches.
- C-3 vote truncated recompute: frozen-25 314 checked, 0 mismatches; SAPTA union 204 checked, 0 mismatches.
- C-4 daily clone parity: BB+RSI lists match = True; stats match = True; MACD-only lists match = True.
- **C-1..C-4 ALL PASS: True**
- C-12a EKAM machinery control (tarang19_score.ekam_control): CAND-T5 2025 {'trades': 1035, 'net': 62164.57, 'published': 62164.57, 'diff': 0.0}, 2026 {'trades': 1025, 'net': 63883.6, 'published': 63883.6, 'diff': -0.0}; S2 2025 {'trades': 621, 'net': 45300.64, 'published': 45300.64, 'diff': 0.0}, 2026 {'trades': 615, 'net': 72605.3, 'published': 72605.3, 'diff': -0.0} → reproduced = True.
- C-13a T25-C reproduction 2025: got 563 trades / ₹+151,307.50 vs published 563 / ₹+151,307.50 → reproduced = True.
- C-13a T25-C reproduction 2026: got 548 trades / ₹+50,274.68 vs published 548 / ₹+50,274.68 → reproduced = True.
- C-13b TRAIL reproduction 2025: got 563 trades / ₹+158,473.60 vs published 563 / ₹+158,473.60 → reproduced = True.
- C-13b TRAIL reproduction 2026: got 548 trades / ₹+74,939.33 vs published 548 / ₹+74,939.33 → reproduced = True.
- C-13b WS3 parity counters: {'exit_parity_mismatch': 0, 'half_level_mismatch': 0, 'entry_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0}.
- C-15a Design 13 anchor: got 278 trades / ₹+70,321.53 / ₹+21,825.75 vs published 278 / ₹+70,321.53 / ₹+21,825.75; taken set identical to sapta_d13_trades.csv = True → reproduced = True.
- C-16b Design 15 Book B: got 302 trades / ₹+111,140.06 / ₹+21,453.63 vs published 302 / ₹+111,140.06 / ₹+21,453.63; taken set identical to sapta_d15_trades.csv = True → reproduced = True.
- C-17u Design 16 union: got 424 trades / ₹+136,826.29 / ₹+24,893.52 vs published 424 / ₹+136,826.29 / ₹+24,893.52; taken set identical to sapta_d16_trades.csv = True → reproduced = True.
- **ALL CONTROLS PASS: True**

## GAPFADE-FOCUS

Candidates 86 → taken 86 (cap-bound days 0, vol-key decisive days 0, tradable names 69, stream side-conflicts 0). Re-TRAIL parity counters: {'exit_parity_mismatch': 0, 'entry_mismatch': 0, 'half_level_mismatch': 0, 'net_mismatch': 0, 'total_violations': 0}. Frozen-exit nets on the identical entries: 2025 ₹+16,164.45 / 2026 ₹+20,940.10.

Book gate: net25 +25,150 net26 +21,841 nov +16,030 | pct 100.0/100.0 | extop +10,711/+226 | trades 86 WR 31.4% DD -5,855 | legs 4/4 PASS

Sleeve Nifty Bank: net25 +4,928 net26 +4,815 nov +0 | pct 99.5/96.5 | extop -3,752/-6,235 | trades 50 WR 28.0% DD -4,906 | legs 3/4 FAIL (sleeve gate: month floor n/a per SPEC §1)

Sleeve Nifty Healthcare: net25 +16,792 net26 +996 nov +0 | pct 100.0/91.5 | extop +5,208/-1,844 | trades 25 WR 36.0% DD -2,790 | legs 3/4 FAIL (sleeve gate: month floor n/a per SPEC §1)

Sleeve Nifty Realty: net25 +3,430 net26 +16,030 nov +16,030 | pct 88.0/100.0 | extop +750/+5,050 | trades 11 WR 36.4% DD -170 | legs 3/4 FAIL (sleeve gate: month floor n/a per SPEC §1)

## GAPFADE-FOCUS — detail

Month table (entry month): 2025-01 +790 · 2025-02 +5,745 · 2025-03 -40 · 2025-04 +11,101 · 2025-05 +5,380 · 2025-06 +890 · 2025-07 -1,952 · 2025-08 +5,989 · 2025-10 -858 · 2025-11 -1,895 · 2026-01 +825 · 2026-02 -3,480 · 2026-03 +6,106 · 2026-04 +3,402 · 2026-06 -1,042 · 2026-11 +16,030

Top contributors: PHOENIXLTD +16,070 (25 -40 / 26 +16,110) · MAXHEALTH +13,200 (25 +13,200 / 26 +0) · AUBANK +10,431 (25 +4,212 / 26 +6,219) · FORTIS +4,752 (25 +3,757 / 26 +996) · ICICIBANK +2,720 (25 +2,720 / 26 +0) · DLF +2,430 (25 +2,470 / 26 -40) · LAURUSLABS +1,731 (25 +1,731 / 26 +0) · LODHA +960 (25 +1,000 / 26 -40) · FEDERALBNK +520 (25 +0 / 26 +520) · CANBK -529 (25 +0 / 26 -529)

2025: trades 40 · gross +26,750.20 · cost 1,600 · net +25,150.20 · gross/trade 668.75 · net/trade 628.75
2026: trades 46 · gross +23,680.90 · cost 1,840 · net +21,840.90 · gross/trade 514.8 · net/trade 474.8


## Head-to-head — Design 13 gated book vs Design 16 union vs Design 17 focus

| Book | Net 2025 / 2026 | Gross/trade 2025 / 2026 | Ex-top-3 2025 / 2026 | Placebo pct | DD | WR | Trades | Legs |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| D13 GAPFADE-TRAIL (rotating, gated) | +70,322 / +21,826 | 581 / 187 | +42,957 / +7,021 | 100.0 / 98.5 | -9,891 | 32.4% | 278 | 4/4 PASS |
| D16 GAPFADE-UNION (rotating, gated) | +136,826 / +24,894 | 784 / 144 | +104,191 / +2,839 | 100.0 / 99.0 | -21,094 | 31.4% | 424 | 4/4 PASS |
| D17 GAPFADE-FOCUS | +25,150 / +21,841 | 669 / 515 | +10,711 / +226 | 100.0 / 100.0 | -5,855 | 31.4% | 86 | 4/4 PASS |


## Power comparison (owner's bar — equal or more powerful than EKAM)

- **FOCUS vs Cand-1**: SAPTA +25,150 / +21,841 vs EKAM Cand-1 (CAND-T5) +62,165 / +63,884 — 2025 falls short, 2026 falls short. WR 31.4%, DD -5,855.
- **FOCUS vs Cand-2**: SAPTA +25,150 / +21,841 vs EKAM Cand-2 (S2) +45,301 / +72,605 — 2025 falls short, 2026 falls short. WR 31.4%, DD -5,855.


## Audit (independent path — sapta_d17_audit.py)

Focus book GAPFADE-FOCUS: candidates re-derived 86; taken audit 86 vs csv 86; counters {'gap_mismatch': 0, 'entry_fill_mismatch': 0, 'exit_mismatch': 0, 'net_mismatch': 0, 'candidate_mismatch': 0, 'allocation_mismatch': 0, 'cap_day_breach': 0, 'cap_nameday_breach': 0, 'spotcheck_miss': 0, 'focus_owner_breach': 0}; spot-check 30 trades; re-sum {2025: (25150.2, 25150.2), 2026: (21840.9, 21840.9)}.
Issues: 0

**AUDIT CLEAN — 0 issues.**

## Verdict

**FOCUS BOOK GAPFADE-FOCUS — ⭐ PASS, 4/4 — SAPTA's third gated
intraday book.** Design 16's union stream restricted to the
Nifty Bank, Nifty Healthcare and Nifty Realty sleeves (SPEC
§2 — the sleeve set is the only change) nets **+₹25,150 /
+₹21,841** on **86 trades** (candidates 86, cap-bound days **0**,
vol-key decisive days 0, zero stream side-conflicts), with
placebo percentiles **100.0 / 100.0**, ex-top-3 **+₹10,711 /
+₹226**, the month floor passed comfortably (worst month Feb
2026 −₹3,480), the family's shallowest drawdown (**−₹5,855**),
win rate 31.4%, and November **+₹16,030** (all of it Realty —
the PHOENIXLTD sleeve). TRAIL again earns its place on
identical entries (frozen-exit nets +₹16,164 / +₹20,940 →
TRAIL +₹25,150 / +₹21,841). Audit CLEAN, 0 issues (above).

**The seed's two questions, answered plainly:**

1. **Concentration does NOT thicken 2026 in total.** Per trade
   the focus book is far richer — 2026 gross/trade **+₹515**
   against the union's +₹144 — but it fields only **46 trades**
   in 2026 against the union's 240, and its 2026 net (+₹21,841)
   lands slightly **below** the union's (+₹24,894) and level
   with Design 13's (+₹21,826). Slot contention was never the
   constraint: the cap bound on only 9 days in Design 16, and
   the 9 trades the focus book recovers (Bank +6, Healthcare
   +3) netted **−₹3,623 in aggregate** — the focus sleeves are
   worth slightly *less* alone (₹46,991) than the same sleeves
   inside the union (₹50,614). **The union's breadth is itself
   load-bearing**: the other eleven sleeves' candidates were
   not stealing the focus sleeves' money; the day's ranking
   was already giving the focus names their best slots, and
   the breadth around them is what carries the union's totals.
2. **Bank and Healthcare do NOT reach their own sleeve
   passes, and Realty's does not survive the move.** All three
   sleeves read **3/4**: Bank (+₹4,928 / +₹4,815, placebo
   99.5/96.5) and Healthcare (+₹16,792 / +₹996, placebo
   100.0/91.5) fail ex-top-3, as they did inside the union;
   Realty, on the **identical 11 trades** with identical nets
   (+₹3,430 / +₹16,030), reads 3/4 here because its 2025
   placebo percentile is **88.0** against the focus pool
   (Design 16: 90.5 against the full pool) — at 11 trades the
   sleeve-pass line is pool-sensitive; the book-level pass is
   not (100.0/100.0). The owner SPEC §6 entity majority, read
   on this book's three sleeves, is **not met (0/3)**.

**Honest limits, stated as in Designs 13 and 16:** the owner's
power bar is met in **neither** year — 2025's +₹25,150 falls
short of both EKAM candidates' 2025 (+₹62,165 / +₹45,301), the
first gated SAPTA book to miss the bar in both years, and
2026's +₹21,841 (gross/trade +₹515, the family's richest) still
falls short of +₹63,884 / +₹72,605 on only 46 trades. The 2026
ex-top-3 leg passes by **₹226** — the thinnest margin on any
gated SAPTA book. This is a **subset book, not a replacement**:
the union is richer in both years and remains the family's
lead gated book; the focus book is its high-quality,
shallow-drawdown concentration of the same stream.

**Where the programme stands:** SAPTA now holds **three gated
intraday books** — Design 13's GAPFADE-TRAIL (+₹70,322 /
+₹21,826), Design 16's GAPFADE-UNION (+₹1,36,826 / +₹24,894,
the richest, still the lead) and Design 17's GAPFADE-FOCUS
(+₹25,150 / +₹21,841, the shallowest drawdown). Design 16's
seed is fully executed: concentration has been tested and the
answer is measured — breadth carries the family, focus
purifies it, neither lifts 2026 to the owner's EKAM bar. No
further dial follows from this design. Nothing is armed and
no paper run is started; the programme's remaining open item
is the **owner's forward-paper word** — the union in the first
instance, as Design 16 left it.
