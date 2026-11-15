# Day Trader Skill (Skill V3) — STANDALONE record, October 2026

Scored 2026-11-05 on Chandu's order ("run for Oct"). **Paper only, real money ₹0, no live orders.** 1 lot (Bank 30 / Nifty 65), cost ₹220/trade. This is the UNTUNED book, exactly as defined for the Nov 2–4 standalone scoring — a descriptive run; nothing tuned, nothing armed.

**Definition:** every Skill V3 key the U1 construction generated on each October 2026 trading day — solo legs included, NOTHING blocked by B2/C3 (those are the primaries' filters, not Skill's). Entry premium = open of the entry 5-min premium candle (first premium bar after the spot signal bar). Exits: Bank **G0** (stop −50 / target +90, stop before target incl. entry bar, square-off 15:10); Nifty **G7** (stop −50; +90 → lock entry+50; second target +150; square-off 15:10; phase 2 starts on the bar after the +90 bar). Timing sanity: every entry uses only the signal bar and earlier spot bars — the entry premium bar is the first bar strictly after the signal close.

**Leg set and independent verification:** Oct 1–28 legs are the machinery's own October Skill set (`index_options_skill_tuned_oct30_trades.csv`, variant V3 — the file that fed the U1 Jan–Oct books): **Bank 15 legs, Nifty 14 legs**. Cross-count against the U1 pooled file's `source_systems`: 28 of 29 legs appear there with Skill V3 among sources (Bank 14, Nifty 14); the one absence is Bank Oct 28, which the U1 merge dropped because it only carried premium-COMPUTED rows and that leg was NOT_COMPUTED there too — consistent, not a missing signal. Oct 29–30 legs (2 per index) are from the extension run (`oct2026_fresh/ext29_30/component_legs.json`), whose own controls re-ran Skill V3 over Oct 1–28 and reproduced the frozen leg set exactly (Bank 15/15, Nifty 14/14). **Totals: Bank 17 keys, Nifty 16 keys** over 20 October trading days.

**Premium data:** the machinery's cached contract-day candle files (`v4_options_oct_data/`, the same cache the October books were scored from) plus the ext29_30 fetched file for Bank Oct 30. Expiries used: Oct 1–27 legs → **2026-10-27** (monthly in force); Oct 28 legs → **2026-11-03** (the machinery's stamped next expiry in force after the October monthly expired); Oct 29–30 → Bank **2026-11-23** (November monthly), Nifty **2026-11-03** (expiry in force per the live instruments master). Legs whose premium bars are absent from every on-disk store are NOT_COMPUTED, listed, and excluded from all totals — never estimated.

**Validation:** Bank G0 re-scoring reproduces the tuned file's premium result **exactly on all 14 computed legs** (entry, exit time/price, reason, net), and Bank Oct 28 is NOT_COMPUTED in both. Bank Oct 30 reproduces the extension run's row exactly (entry 762.40 → stop 10:55 @ 712.40, −₹1,720). Nifty legs that never reached +90 match the older file's nets leg-for-leg; where this run differs from that file on Nifty it is only the geometry — the older file's overlay was G0 for both indices, this run applies G7 as specified (e.g. Oct 26: file target +₹5,630 under G0 → runner_lock +₹3,030 under G7).

---

## Bank Nifty — Skill standalone, October 2026

| Date | Leg | Signal → Entry | Entry @ | Exit | Exit @ | Reason | Net ₹ |
|---|---|---|---|---|---|---|---|
| Thu 2026-10-01 | CE 54900 | 09:55 → 10:00 | 999.15 | 10:30 | 1,089.15 | target | +2,480.00 |
| Mon 2026-10-05 | PE 54700 | 10:50 → 10:55 | 755.00 | 11:50 | 845.00 | target | +2,480.00 |
| Tue 2026-10-06 | CE 55000 | 09:40 → 09:45 | 941.10 | 10:05 | 891.10 | stop | −1,720.00 |
| Wed 2026-10-07 | PE 54700 | 09:35 → 09:40 | 736.90 | 09:40 | 686.90 | stop (entry bar) | −1,720.00 |
| Thu 2026-10-08 | PE 54800 | 11:25 → 11:30 | 717.65 | 11:45 | 667.65 | stop | −1,720.00 |
| Fri 2026-10-09 | CE 55100 | 09:30 → 09:35 | 849.35 | 10:10 | 939.35 | target | +2,480.00 |
| Mon 2026-10-12 | PE 55000 | 09:50 → 09:55 | 609.00 | 09:55 | 559.00 | stop (entry bar) | −1,720.00 |
| Tue 2026-10-13 | CE 55200 | 09:35 → 09:40 | 756.65 | 11:45 | 706.65 | stop | −1,720.00 |
| Wed 2026-10-14 | CE 55500 | 09:30 → 09:35 | 728.00 | 10:05 | 678.00 | stop | −1,720.00 |
| Thu 2026-10-15 | CE 55600 | 09:50 → 09:55 | 669.95 | 10:15 | 759.95 | target | +2,480.00 |
| Wed 2026-10-21 | CE 55800 | 09:30 → 09:35 | 489.80 | 09:45 | 439.80 | stop | −1,720.00 |
| Thu 2026-10-22 | CE 54800 | 10:10 → 10:15 | 499.00 | 10:20 | 589.00 | target | +2,480.00 |
| Fri 2026-10-23 | PE 54600 | 09:45 → 09:50 | 322.70 | 10:00 | 412.70 | target | +2,480.00 |
| Tue 2026-10-27 | CE 54500 | 09:35 → 09:40 | 222.00 | 10:20 | 172.00 | stop | −1,720.00 |
| Wed 2026-10-28 | CE 54000 (exp 2026-11-03) | 09:45 → 09:50 | — | — | — | NOT_COMPUTED — no premium candle file for this contract-day in any on-disk store | — |
| Thu 2026-10-29 | CE 54400 (exp 2026-11-23) | 09:35 → 09:40 | — | — | — | NOT_COMPUTED — premium candles were never fetched for this contract-day; the only store holding it starts at 10:00, after the 09:40 entry bar | — |
| Fri 2026-10-30 | PE 54600 (exp 2026-11-23) | 10:30 → 10:35 | 762.40 | 10:55 | 712.40 | stop | −1,720.00 |

No Skill leg on Oct 16, Oct 19, Oct 26 (no key generated).

**Bank October summary:** 17 keys · **15 trades scored** · 2 NOT_COMPUTED (excluded) · **month total −₹600.00** · win rate **40.0%** (6/15) · full targets **6/15 = 40.0%** · best day **+₹2,480** (Oct 1, and identically Oct 5, 9, 15, 22, 23 — every winning day is one +90 target) · worst day **−₹1,720** (nine days, each a single −50 stop). Every Bank leg is binary under G0: +₹2,480 or −₹1,720, nothing in between.

---

## Nifty — Skill standalone, October 2026

| Date | Leg | Signal → Entry | Entry @ | Exit | Exit @ | Reason | Net ₹ |
|---|---|---|---|---|---|---|---|
| Thu 2026-10-01 | CE 22600 | 10:00 → 10:05 | 360.35 | 12:10 | 310.35 | stop | −3,470.00 |
| Mon 2026-10-05 | CE 22600 | 09:30 → 09:35 | 364.05 | 10:25 | 314.05 | stop | −3,470.00 |
| Tue 2026-10-06 | CE 22600 | 09:45 → 09:50 | 359.90 | 15:10 | 391.00 | square_off | +1,801.50 |
| Wed 2026-10-07 | PE 22600 | 09:35 → 09:40 | 268.45 | 10:20 | 218.45 | stop | −3,470.00 |
| Thu 2026-10-08 | PE 22500 | 09:40 → 09:45 | 270.00 | 15:10 | 390.00 | square_off (runner — +90 reached 12:20, lock never hit) | +7,580.00 |
| Fri 2026-10-09 | CE 22400 | 09:30 → 09:35 | 318.15 | 15:10 | 393.15 | square_off (runner — +90 reached 13:55, lock never hit) | +4,655.00 |
| Mon 2026-10-12 | PE 22500 | 09:50 → 09:55 | 250.80 | 15:10 | 319.00 | square_off | +4,213.00 |
| Tue 2026-10-13 | CE 22500 | 09:30 → 09:35 | 288.60 | 15:10 | 426.30 | square_off (runner — +90 reached 14:35, lock never hit) | +8,730.50 |
| Thu 2026-10-15 | CE 22800 | 09:30 → 09:35 | 213.30 | 12:35 | 363.30 | runner_target (+150) | +9,530.00 |
| Wed 2026-10-21 | CE 23100 | 09:30 → 09:35 | 183.10 | 10:00 | 133.10 | stop | −3,470.00 |
| Thu 2026-10-22 | CE 22700 | 10:20 → 10:25 | 190.45 | 11:45 | 140.45 | stop | −3,470.00 |
| Mon 2026-10-26 | CE 22600 | 09:50 → 09:55 | 132.05 | 10:35 | 182.05 | runner_lock (+50 after +90) | +3,030.00 |
| Tue 2026-10-27 | CE 22800 | 09:40 → 09:45 | 65.00 | 13:10 | 15.00 | stop | −3,470.00 |
| Wed 2026-10-28 | PE 22500 (exp 2026-11-03) | 10:15 → 10:20 | 200.95 | 11:00 | 150.95 | stop | −3,470.00 |
| Thu 2026-10-29 | CE 22800 (exp 2026-11-03) | 09:35 → 09:40 | — | — | — | NOT_COMPUTED — no premium candle file for this contract-day in any on-disk store (the weekly store that holds it starts at 10:00, after the 09:40 entry bar; no monthly-series bars exist for it on disk) | — |
| Fri 2026-10-30 | CE 23000 (exp 2026-11-03) | 09:30 → 09:35 | — | — | — | NOT_COMPUTED — same as Oct 29 (entry bar 09:35 absent from every store) | — |

No Skill leg on Oct 14, Oct 16, Oct 19, Oct 23 (no key generated).

**Nifty October summary:** 16 keys · **14 trades scored** · 2 NOT_COMPUTED (excluded) · **month total +₹15,250.00** · win rate **50.0%** (7/14) · full targets (premium reached +90 at any point, per the frozen G7 definition) **5/14 = 35.7%** — Oct 8, Oct 9, Oct 13 (reached +90 intraday, lock never hit, squared off at the 15:10 close above +90), Oct 15 runner_target, Oct 26 runner_lock · best day **+₹9,530.00** (Oct 15) · worst day **−₹3,470.00** (seven days, each a single −50 stop).

---

## Plain read

October is where the Skill made its money — on the **Nifty side: +₹15,250** over 14 scored trades, carried by the runner geometry letting five legs run past +90 (Oct 13 +137.7 pts and Oct 15 +150 pts at square-off/target are the two big ones). **Bank October was flat: −₹600** over 15 scored trades — six clean +90 targets against nine −50 stops, a coin-flip at G0's 1.8:1 shape needs better than 35.7% targets and it got 40%, almost exactly break-even. Four legs (Bank Oct 28–29, Nifty Oct 29–30) could not be scored from any premium data on disk and are excluded from both totals; Bank Oct 28's spot replay in the machinery was a large spot stop, so Bank's −₹600 is, if anything, flattered by its exclusion.

Leg-level CSV: `skill_standalone_october_2026-11-05_legs.csv`. No primary/shadow log, no `skill_tuning_*` file, and no other system's files were touched.
