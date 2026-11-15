# Bank Nifty Engine — ROUND 6 (2026-11-02)

Basis: premiums per 1 lot of 30, cost ₹220/trade, UNIQUE-ONCE, Jan–Oct 2026,
paper only, real money ₹0. Starting book: v20 = +₹78,250.50 (the CAUSAL book;
gap ₹71,749.50 to the ₹1,50,000 floor pace). 14 cycles (136–149), all six
workstreams gated through. **The floor is NOT met.** Ending book:
**v21 = +₹83,650.50 → ₹8,365.05/month; remaining gap ₹66,349.50.**
Rounds 1–4 magnitudes were computed on mis-timed legs and are cited nowhere
below as evidence; only their constructions were re-tested, on causal times.

Sanity (before any candidate was scored): v20 reproduced exactly through the
Round-5 machinery (+₹78,250.50, 99 legs, FT90 49.5, placebo −₹4,313.50,
NC 0, timing clean, gate PASS vs REF_AUD). Gates below are vs v20 under the
full controls gate (net + FT90 + frequency together, no green month flips
red, halves ≥ 0, placebo beaten, ex-top-3 ≥ 0, NC 0, re-sum).

## WS1 — NS3 CAUSAL DECOMPOSITION + GEOMETRY (Cycles 136–140)

**Cycle 136 — v20 family decomposition at causal times** (standalone nets
inside the assembled book):

| Family | Legs | Net |
|---|---|---|
| BASE | 61 | +₹55,466.00 |
| — of which Volrix (b) regen cd15 | 7 in book | +₹19,910.00 |
| — of which V5 v2 | 21 | +₹15,330.00 |
| — of which (lA) v2 | 11 | +₹11,939.50 |
| — of which Skill V3 | 22 | +₹8,286.50 |
| NS1 second legs | 16 | +₹10,269.50 |
| NS3 (GD+GU @ T90/L65/G175) | 15 | +₹7,755.00 |
| S3-A (S3-R1) | 6 | +₹2,280.00 |
| S3-E (S3-PDC) | 1 | +₹2,480.00 |

NS3 census at causal (signal+5) entries: 58 candidate legs — GD 37, GU 14,
FLAT 7. Admitted under GD+GU: GD 14 legs +₹9,475.00, GU 1 leg −₹1,720.00.

**Geometry re-grid on causal times** (the Round-4 L65/G175 "win" was measured
on mis-timed entries and is not evidence):
- **C137 admission retest — ALL sublegs @ L65/G175: +₹77,558.50, REJECTED**
  (net −₹692 vs v20, FT90 48.5 < 49.5). Admitting FLAT (17 admitted vs 15,
  NS3 net ₹7,063) costs money causally too — **the FLAT exclusion holds.**
- **C138 GD+GU @ lock50/tgt2 175: +₹80,650.50 — BANKED (Δ +₹2,400).**
- **C139 GD+GU @ lock65/tgt2 150: +₹81,100.50 — BANKED (Δ +₹2,850).**
- **C140 GD+GU @ lock50/tgt2 150: +₹83,650.50 — BANKED (Δ +₹5,400).**
  NS3 family net rises ₹7,755 → ₹13,155 on the same 15 admitted legs.
  On causal times the geometry peak is the TIGHTER cell — the opposite
  corner from the mis-timed grid's verdict.

## WS2 — CAUSAL STACK RE-TEST (Cycle 141)

Decomposition verdict: S3-A contributes +₹2,280.00 (6 legs) and S3-E
+₹2,480.00 (1 leg) on the causal book — **both net-positive, so no removal
candidate exists** under the workstream's condition. The S3 stack stands
as certified in Round 5's WS0. Closed.

## WS3 — BANK GAP SLEEVE (Cycles 142–143) — both directions rejected

Pre-registered (in `bank_r6_ws3_ws4.py` before scoring): overnight gap
≥ 0.50% (60 gap days), entry 09:35, ATM at the entry bar, book exits,
sequential admission. Causality certificate: the gap is determined by the
prior close and the 09:15 open print; entry is strictly after both.
- **C142 FOLLOW: sleeve admitted 40 legs, net −₹16,150.00 → book
  +₹62,100.50. REJECTED** (net, June flips green→red, FT90 44.6).
- **C143 FADE: sleeve admitted 33 legs, net −₹27,360.00 → book
  +₹50,890.50. REJECTED** (net, March flips green→red, FT90 42.4).
Bank's overnight gap carries neither continuation nor reversal at 09:35
entries in this window — unlike Nifty, where the fade was a real effect.
The family is closed on Bank.

## WS4 — BANK EXPIRY-DAY SLEEVE (Cycle 144) — rejected

Pre-registered: B1 representatives (earliest component leg per key) on the
10 monthly expiry dates, entry 09:15–11:00, book exits, no end-of-day
set-membership test (certificate in the script). Population: **9 legs**
(≥ 8, so the cycle ran). Admitted 4 (5 key-dropped — the book already
holds those keys), **sleeve net −₹6,880.00 → book +₹71,370.50. REJECTED**
(net, June flips green→red, FT90 47.6). The OR-break signals the book
leaves untaken on expiry days are adversely selected; the book's filters
are doing work on those days too. Family closed.

## WS5 — VOLRIX COMPLETION (Cycles 145–148) — banked cell is the peak

One axis at a time from (−1.0%, cd15), NS3 held at v20 geometry:
- C145 cd12: +₹73,080.50 — rejected (net, FT90 49.0).
- C146 cd20: +₹70,600.50 — rejected (net, FT90 48.5).
- C147 trigger −0.9% @ cd15: **exact no-op** (+₹78,250.50, identical book —
  the wider threshold admits the same 11 legs).
- C148 trigger −1.1% @ cd15: +₹68,580.50 — rejected (net, FT90 47.0).
Cooldown 15 at trigger −1.0% is a plateau peak; both Volrix axes are now
closed on the causal book.

## WS6 — COMBINATION / FINAL RE-GATE (Cycle 149)

WS3/WS4/WS5 banked nothing; the round's only banking axis is NS3 geometry,
whose cells are mutually exclusive. The combination is therefore the best
banked variant re-gated whole-book:
**book v21 = v20 with NS3(GD+GU) @ stop −50 / trig +90 / lock +50 /
tgt2 +150** — gate PASS vs v20, PASS chained vs C139, PASS chained vs
C138, independent re-sum exact. Trades: `bank_engine_r6_v21_trades.csv`;
controls: `bank_r6_v21_freeze.json`.

## ENDING SCORECARD

| Book | Net Jan–Oct | Legs | FT90 | /week | Pace/month | Gap to ₹1,50,000 |
|---|---|---|---|---|---|---|
| REF_AUD (causal rebuild) | +₹69,940.50 | 102 | 48.0% | 2.51 | ₹6,994.05 | ₹80,059.50 |
| v20 (Round-5 best) | +₹78,250.50 | 99 | 49.5% | 2.44 | ₹7,825.05 | ₹71,749.50 |
| **v21 (Round-6 best)** | **+₹83,650.50** | **99** | **49.5%** | **2.44** | **₹8,365.05** | **₹66,349.50** |

v21 controls: no red month-ends; months Jan +22,748 · Feb +20,480 ·
Mar +1,120 · Apr −90 · May +17,680 · Jun +560 · Jul −3,680 · Aug −873.50 ·
Sep +10,776.50 · Oct +14,929.50; halves +₹61,938.00 / +₹21,712.50;
placebo −₹4,313.50 (beaten by ₹87,964); ex-top-3 +₹54,610.50;
NOT_COMPUTED 0; timing audit clean (99/99 entry bars); independent
re-sum exact.

**Verdict: Round 6 complete — all six workstreams gated through (14
cycles, 3 bankings on one axis). The floor pace is NOT reached: the
causal Bank book stands at ₹8,365.05/month against the ₹15,000 floor.**
The round's gain (+₹5,400) came from re-gridding, on causal times, a
geometry whose earlier verdict was an artefact of mis-timed entries.
Both new families (gap, expiry-day) are measured and closed; Volrix is
at its local peak. November primary (BNF-PAPER-V1) untouched throughout.
