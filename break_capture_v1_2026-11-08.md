# BREAK-CAPTURE v1 — opening-range break capture, two variants, full gate (2026-11-08)

**Research/backtest only. Nothing armed; no frozen book, log, shadow, or cron touched. Real money ₹0 — paper figures, index option premiums per 1 lot (Bank lot 30, Nifty lot 65), cost ₹220/trade, UNIQUE-ONCE.**

**Verdict up front: all four books FAIL the pre-registered gate.** Bank R −₹10,018.80 · Bank H −₹14,136.80 · Nifty R −₹119,064.10 · Nifty H −₹3,076.35 (Jan–Oct 2026). No variant surgery was done after seeing results.

---

## 1. Pre-registered spec (frozen before scoring)

**Signal** (identical to the probability study, `daily2leg/spot.json` 5-min spot): OR = bars 09:15/09:20/09:25; ORH/ORL. BREAK bar = first bar ≥09:30 whose CLOSE is beyond ORH (up) / ORL (down). Each direction is its own sequence, max one per direction per day. Days with <70 spot bars excluded and counted.

**Instrument/conventions** (identical to the v21 / DEC-S1 / daily2leg scorers): ATM option on the break side (CE up / PE down); strike = daily2leg `atm()` of the signal bar's spot close (re-entries: re-break bar close; H: check bar close; SHIFTED placebo: close of the bar before the shifted fill). Bank Nifty MONTHLY and Nifty MONTHLY expiry families; expiry = first listed monthly expiry ≥ trade date. Premium stores: `daily2leg/prem_bank.json` / `prem_nifty.json` only. Entry fill = premium OPEN of the next bar after the signal bar. Missing premium bars for a leg → NOT_COMPUTED, counted and listed, never estimated; a leg needs every premium bar from entry bar through exit bar inclusive.

**Variant R — RE-ENTRY:** enter on the break (next bar open). Exit at the first of: (i) spot FAILURE CLOSE after entry (5-min close ≤ORH for CE / ≥ORL for PE) → exit next bar open; (ii) premium hard stop −50 pts, close-based (premium CLOSE ≤ entry−50) → exit next bar open; (iii) square-off 15:10 at the 15:10 bar's premium CLOSE. If stop and failure trigger on the same close, the exit counts as the STOP exit (fill identical; no re-entry). Re-entry only after a failure-close exit, on a fresh close beyond the same level, max 2 re-entries (3 legs/direction/day). A hard-stop exit ends the sequence. No fixed premium target.

**Variant H — HOLD-60 DELAYED ENTRY:** no entry at the break. Check bar = the bar that closes 60 minutes after the break bar's start (starts at break+55). Enter (next bar open) only if no failure close occurred on any bar since the break AND the check bar's close is still beyond the level; otherwise no trade that direction-day (first break only). Exits identical to R; no re-entry. (One-bar note vs the study: the study's HOLD-60 flag also required no failure close on the bar starting at break+60; v1 follows the task spec — qualification is decided at the check bar's close, and a failure close on the entry bar itself exits under the normal rules.)

**Day guard:** −₹3,000 day-loss cap per index. Convention used, identical across variants and placebos: entries fill in time order; before an entry fills, at its signal bar's close, day P&L = (closed legs' nets) + (open legs marked at their premium close on that signal bar, valued (close−entry)×lot − ₹220 each). If marked P&L ≤ −₹3,000 the entry is blocked and the cap LATCHES for the rest of that index-day in that book; exits are never blocked.

**Owner's ₹500/₹1,000 day-profit ceilings deliberately NOT applied in this v1** — they would truncate the trend days this build exists to capture. Flagged as an open layering question for December; not applied here.

**Windows:** Jan–Oct 2026 primary and Jan–Oct 2025, reported separately per index per variant, never pooled. Per-index verdicts always separate.

**Placebos** (independent books, own day caps): FLIPPED — identical signals/state machine, opposite option side. SHIFTED — every entry fill delayed +30 min (6 bars); strike = ATM at the close of the bar before the shifted fill; exit rules identical (R re-entries proceed from the shifted book's own failure exits).

**PASS (per variant per index):** 2026 net > 0 AND both halves (Jan–May / Jun–Oct) > 0 AND beats both placebos AND ex-top-3 legs > 0 AND NC ≤ 10% of signal days AND timing violations = 0. 2025 disclosed alongside; if a 2025 net existed and were < −₹5,000 → FAIL-DOUBLE.

---

## 2. Gate tables — Jan–Oct 2026

### Bank Nifty — Variant R (re-entry)
| Gate leg | Result |
|---|---|
| Legs scored | 258 |
| **2026 net** | **−₹10,018.80** ✗ |
| Half 1 (Jan–May) / Half 2 (Jun–Oct) | +₹18,464.50 / **−₹28,483.30** ✗ |
| FLIPPED placebo | −₹76,346.00 (269 legs) — beaten ✓ |
| SHIFTED placebo | −₹38,913.00 (390 legs) — beaten ✓ |
| Ex-top-3 legs | **−₹50,737.80** ✗ |
| Timing violations | 0 ✓ |
| NC | 96 of 255 signal direction-days = **37.65%** ✗ |
| Worst day | −₹5,555.00 (2026-03-20) |
| Worst 3 consecutive active days | −₹13,479.50 (2026-04-30 → 2026-05-05) |
| Cap-hit days (−₹3,000 latch) | 9 |
| Days ≤ −₹3,000 | worst day breaches it; cap latched on 9 days |

Months: Jan −10,733.00 · Feb +697.50 · Mar +19,140.00 · Apr +39,008.50 · May −29,648.50 · Jun +27,811.50 · Jul −22,150.00 · Aug −16,619.30 · Sep −8,780.50 · Oct −8,745.00 (4 of 10 positive).

**VERDICT: FAIL** — failed legs: 2026 net not > 0; halves not both positive; ex-top-3 not positive; NC share > 10%.

### Bank Nifty — Variant H (hold-60)
| Gate leg | Result |
|---|---|
| Legs scored | 74 (of 75 qualified direction-days; 1 blocked by the day cap) |
| **2026 net** | **−₹14,136.80** ✗ |
| Half 1 / Half 2 | +₹498.00 / **−₹14,634.80** ✗ |
| FLIPPED placebo | −₹27,417.00 (75 legs) — beaten ✓ |
| SHIFTED placebo | −₹6,190.00 (73 legs) — **NOT beaten** ✗ |
| Ex-top-3 legs | **−₹50,096.30** ✗ |
| Timing violations | 0 ✓ |
| NC | 0 of 75 qualified direction-days = 0.0% ✓ |
| Worst day | −₹3,701.50 (2026-03-23) |
| Worst 3 consecutive active days | −₹9,237.00 (2026-03-18 → 2026-03-24) |
| Cap-hit days | 1 |

Months: Jan −9,037.00 · Feb +3,544.50 · Mar −1,705.50 · Apr +12,451.00 · May −4,755.00 · Jun +7,617.00 · Jul −6,208.50 · Aug −1,772.30 · Sep −4,399.00 · Oct −9,872.00 (3 of 10 positive).

**VERDICT: FAIL** — failed legs: 2026 net not > 0; halves not both positive; does not beat SHIFTED placebo; ex-top-3 not positive.

### Nifty — Variant R (re-entry)
| Gate leg | Result |
|---|---|
| Legs scored | 298 |
| **2026 net** | **−₹119,064.10** ✗ |
| Half 1 / Half 2 | −₹61,066.50 / −₹57,997.60 ✗ (both negative) |
| FLIPPED placebo | −₹51,901.50 (287 legs) — **NOT beaten** ✗ |
| SHIFTED placebo | −₹160,140.35 (435 legs) — beaten ✓ |
| Ex-top-3 legs | **−₹142,538.60** ✗ |
| Timing violations | 0 ✓ |
| NC | 106 of 269 signal direction-days = **39.41%** ✗ |
| Worst day | −₹5,076.75 (2026-10-22) |
| Worst 3 consecutive act
...[truncated 8184 chars]