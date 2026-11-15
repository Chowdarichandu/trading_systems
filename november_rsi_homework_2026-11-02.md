# November RSI homework — 2026-11-02 losers: historical frequency of each failure signature

Descriptive diagnosis only (input for the 17:15 RSI engine). No variant scored, no tuning proposed, no log/spec/state modified. Paper only, real money ₹0. All counts from stored files in `~/workspace/trading/`; where a needed source does not exist, that is stated instead of estimated.

---

## 1. Bank Nifty primary — Skill V3 PE, OR-breakdown that failed immediately

**Today's trade:** signal 10:15 (first close below OR low), entry 10:20, stopped 10:25 at −50 premium pts (−₹1,720); spot recovered inside the OR within ~15 minutes and stayed inside for hours.

**Signature used:** a leg in the primary's base pool whose source systems include Skill V3 (the opening-range system — its signal IS an OR break, per `skill_v3_jansep.py`: OR = 09:15–09:30 bars, first close beyond OR in 09:30–11:30), exiting by `stop` with exit_time − entry_time ≤ 10 minutes (stopped within the first 3 five-minute bars, entry bar included; today's hold was 5 min). Spot-recovery leg: the day's 11:00 close (close of the 10:59 1-min bar) back inside that day's OR high/low.

**Files searched:** `historical_proof_bank_B2_trades.csv` (the B2 base pool of BNF-PAPER-V1, premium-scored, Jan–Oct 2026 — the verified October sets in `oct2026_fresh/` derive from this same file, so it is counted once, not twice); `data/1min/BANKNIFTY/spot_1m_*.csv` (stored 1-min spot, only 22 dates exist); `index_options_newsetup_ns1_trades_jan_oct_2026.csv` (secondary line only).

**Counts:**
- Base pool: 89 legs, all premium-COMPUTED. OR-break legs (Skill V3 among source systems): **70** (PE 60, CE 10; in 34 of them Skill V3 is the representative system).
- **Stopped within ≤10 min: 14 of 70 = 20.0%.** Direction: PE 12, CE 2. Hold split: 0 min (stopped on the entry bar itself) ×4, 5 min ×4, 10 min ×6. Every one of the 14 lost the full −₹1,720, the same as today.
- Sensitivity: stopped ≤5 min: 8/70 (11.4%); stopped ≤15 min: 20/70 (28.6%). Context across all 89 pool legs (any system): 17 stopped ≤10 min.
- **Spot recovery by 11:00:** only 3 of the 14 quick-stop dates have a stored 1-min spot file (2026-04-02, 2026-06-29, 2026-07-08) — **all 3 closed back inside the OR by 11:00 (3 of 3 checkable)**. The other 11 dates have no stored spot file, so no recovery count is claimed for them. (Today's trade is a 4th, live-verified instance of the full signature, but it is not counted in this history.)
- Secondary line (different leg family, spot-provisional basis, not premium): NS1 second legs for Bank — 38 of 65 stopped within ≤10 min. Same quick-death shape, weaker data basis; noted, not pooled with the count above.

**Examples (quick-stop OR legs):**
| Date | Dir | Entry → Exit | Hold | Net ₹ | Spot back inside OR by 11:00 |
|---|---|---|---|---|---|
| 2026-04-02 | PE | 10:50 → 10:55 | 5m | −1,720 | Yes (verified from spot file) |
| 2026-06-29 | PE | 09:35 → 09:35 | 0m | −1,720 | Yes (verified) |
| 2026-07-08 | PE | 09:35 → 09:45 | 10m | −1,720 | Yes (verified) |
| 2026-05-27 | PE | 10:00 → 10:00 | 0m | −1,720 | no spot file stored |
| 2026-10-07 | PE | 09:40 → 09:40 | 0m | −1,720 | no spot file stored |

**Judgement: RECURRING cause.** One in five OR-break legs in the primary's own history died at the full stop within 3 bars, and every spot-checkable case (3/3) had already recovered inside the range by 11:00 — today's trade is the same shape, not a one-off.

---

## 2. GODREJCP — P2F shadow SHORT stopped inside the entry bar

**Today's trade:** pre-booked SHORT at the 09:15 open (813.0) after a −2.27% results reaction on Fri 2026-10-30; the entry bar's high (823.0) crossed the +0.5% stop (817.07) — the follow-through reversed against the trade within the first bar.

**Signature used:** a P2F-family entry (P2F = reaction followed next day R+1; P2F-R2 = followed at R+2; R2-LOWBAND = the 2.0–2.5% band at R+2) exiting by `stop` with exit_time − entry_time ≤ 15 minutes. Data-convention note: in these files a stop is stamped at the bar after the hit at the earliest (a 09:15 entry stopped in its own bar is stamped 09:20); no row carries identical entry/exit stamps. The ≤5-minute group (20 of the 25 below) is therefore the entry-bar/first-bar stop-out group — today's trade belongs to it.

**Files searched:** `stocks_engine_ch1_p2fprofile_trades.csv` (P2F, 46 trades), `stocks_engine_sat13_p2fr2_trades.csv` (P2F-R2, 34), `stocks_engine_sat33_r2lowband_trades.csv` (R2-LOWBAND, 7) — the stored component trade files, Jan–Oct 2026. The placebo twin file (`stocks_engine_ch1_p2fplacebo_trades.csv`, same trades with shuffled donors) was excluded. The frozen book dumps (`stocks_engine_v2_c24_book2025/2026_trades.csv`) carry no exit times, so they cannot feed this count; for context they hold 57 P2F-family rows in 2025 (+₹7,050.76) and 67 in 2026 (+₹35,849.32).

**Counts:**
- Pool: **87** family trades. **Stopped within ≤15 min of entry: 25 of 87 = 28.7%.** Hold split: 5 min ×20, 10 min ×3, 15 min ×2. Directions: SHORT 15, LONG 10.
- By component: P2F 13/46 (28.3%), P2F-R2 11/34 (32.4%), R2-LOWBAND 1/7 (14.3%).
- Context: 40 of the 87 family trades exit by stop at any hold time — the ≤15-min group is 25 of those 40, i.e. most family stops happen almost immediately.

**Examples:**
| Date | Comp | Stock | Dir | Reaction | Entry → Exit | Net ₹ |
|---|---|---|---|---|---|---|
| 2026-01-21 | P2F-R2 | WIPRO | SHORT | −7.98% | 09:15 → 09:20 | −159.95 |
| 2026-02-02 | P2F-R2 | VEDL | SHORT | −11.41% | 09:15 → 09:20 | −366.67 |
| 2026-02-09 | P2F | HINDCOPPER | SHORT | −5.52% | 09:15 → 09:20 | −426.26 |
| 2026-01-30 | P2F | TVSMOTOR | SHORT | −2.01% | 09:15 → 09:20 | −2,422.25 |
| 2026-02-10 | P2F | KALYANKJIL | LONG | +14.53% | 09:15 → 09:25 | −326.65 |

**Judgement: RECURRING cause.** More than one in four P2F-family entries is stopped within 15 minutes, and the dominant form (20 of 25) is a stop inside the first 5 minutes — the reaction reversing at the next open, exactly today's GODREJCP shape (a SHORT after a down-reaction, stopped by the first bar's high).

---

## 3. NTPC — N4-V3 reaction-day LONG that faded intraday

**Today's trade:** reaction day, +3.2% by 09:30, LONG entry 09:35 @ 325.35, faded all morning (scorecard stop −0.5% crossed; book stop −0.8% not crossed).

**Signature used:** an N4-V3 entry whose reaction move by 09:30 (recorded in the source file's own note, "reaction move by 09:30 ±x%") has |move| ≥ 2%, split into buckets 1–2%, 2–3%, ≥3%; outcome = sign and average of net on two exit bases — the book basis (T150/S080, the basis today's book stop belongs to) and the scorecard basis (T125/S050). Move is signed by price direction; the trade follows the move, so |move| is the strength.

**Files searched:** `eq_n4deep_v3_trades_T125_janoct.csv` (standalone N4-V3, 56 trades, Jan–Oct 2026, carries the 09:30 move per trade) joined 56/56 on (date, stock, direction) to `stocks_engine_sat15_n4_t150s080_trades.csv` (same 56 trades on the book exit basis; identical set to `stocks_engine_ch2_n4_trades.csv`). Context from the frozen dumps: N4-V3 book rows — 2025: 52 rows (17 positive / 35 negative, +₹2,522.40 total); 2026: 35 rows (23 / 12, +₹25,271.54) — the dumps are the post-exclusion book subset and carry no move sizes, so the bucket analysis runs on the 56-trade standalone file.

**Counts:**
- **|Move| ≥ 2% by 09:30: 41 trades → negative 21 / positive 20 (book basis), average net +₹216.43.** (Scorecard basis: negative 23 / positive 18, average +₹240.18.)
- Bucket split (book basis; scorecard average in brackets):
  - 1–2%: n=15, negative 8 / positive 7, **average +₹740.27** [−₹123.80]
  - 2–3%: n=15, negative 7 / positive 8, **average +₹655.75** [+₹819.32]
  - **≥3%: n=26, negative 14 / positive 12, average −₹37.01 [−₹93.94] — the only negative-average bucket on either basis.**
- Honest limit: win/loss counts are near coin-flip in every bucket (≥3% is 14 vs 12, not a landslide). The recurrence is in the *average outcome*: the ≥3% bucket gives back the edge the smaller buckets keep. NTPC's +3.2% sits squarely in that ≥3% bucket.

**Fade examples (|move| ≥ 2%, book net < 0):**
| Date | Stock | Dir | Move by 09:30 | Book net ₹ | Note |
|---|---|---|---|---|---|
| 2026-01-19 | HINDZINC | LONG | +3.21% | −563.52 | near-twin of NTPC: +3.2% LONG, stopped |
| 2026-08-13 | ASTRAL | LONG | +6.76% | −1,310.32 | biggest fade in the file |
| 2026-01-30 | VEDL | SHORT | −7.39% | −616.60 | stopped |
| 2026-04-29 | RECLTD | SHORT | −3.10% | −327.88 | stopped |
| 2026-04-01 | WIPRO | LONG | +3.20% | −194.03 | same move size as NTPC |

**Judgement: RECURRING pattern, with a precise address.** The fade is not spread evenly over N4-V3 — it concentrates in the ≥3%-by-09:30 bucket, the only bucket whose average outcome is negative on both exit bases, while 1–3% entries average clearly positive. NTPC (+3.2%) is a textbook member of that bucket, not bad luck in a healthy one.

---

## Summary of judgements

1. **Bank OR-break quick stop + recovery — RECURRING** (14/70 = 20.0% of OR legs stopped ≤10 min; 3/3 spot-checkable days back inside OR by 11:00).
2. **P2F-family first-minutes stop-out — RECURRING** (25/87 = 28.7% stopped ≤15 min; 20 of the 25 within 5 min).
3. **N4-V3 strong-move fade — RECURRING in the ≥3% bucket** (n=26, average −₹37 book / −₹94 scorecard, vs +₹656…+₹740 averages in the 1–3% buckets; counts 14 neg / 12 pos).

Known gaps, stated not filled: Bank spot 1-min files exist for only 22 dates, so the recovery leg of signature 1 is verified on 3 of 14 cases; the frozen stock dumps carry no exit times, so signature 2's count comes from the component trade files (87 trades, Jan–Oct 2026) rather than the dumps.
