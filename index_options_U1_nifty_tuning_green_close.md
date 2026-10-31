# U1 Nifty — NIFTY CHANNEL ONLY — diagnosis + tuning to a green month-end close

**SEPARATE CHANNEL: NIFTY ONLY.** This file contains no Bank verdict and no
combined total. Bank is a different channel with its own file/status.
Index OPTIONS only, paper only, no orders, no stocks.
Window: 1 Jan – 28 Oct 2026 (203 trading days; October = 1–28 Oct only).
**Real money = ₹0 throughout. Nothing adopted on in-sample alone.**

Units: Jan–Sep = **spot provisional** (points × 100 shares − ₹40, NOT an
options-lot profit, NOT a futures profit); October = **option premiums per
1 lot** (−50/+90 overlay, ₹220 cost, Nifty lot 65). Jan–Oct totals are
**MIXED totals, labelled as such — never a pure premium total**.

Governing intention (user, 2026-10-30 13:29 IST): per index separately —
that index ends positive, and the month-end CUMULATIVE closes green.
"Month closed green" below means month-end cumulative > 0; an individual
negative month inside a green cumulative close is stated as such, never
hidden.

Source: `index_options_U1_janoct_trades.csv` (Nifty legs only),
`index_options_U1_skillV3_jansep_spot.csv`.

## Base — U1 Nifty (verified from the trades CSV)

179 trades, 4.41/week, 36.3% full-target, **+₹109,319.75 mixed**
(Jan–Sep spot +₹95,150; October premiums +₹14,169.75, 16 trades, 37.5% FT,
4.44/week). Ends positive, but month-end cumulative was **RED in Jan
(−₹11,050) and Feb (−₹4,355)**, and May was a −₹25,560 month. Base does
NOT meet the intention.

Base month-by-month (mixed):

| Month | Trades | Month net | Month-end cumulative | Close |
|---|---|---|---|---|
| Jan | 19 | −₹11,050 | −₹11,050 | 🔴 RED |
| Feb | 19 | +₹6,695 | −₹4,355 | 🔴 RED |
| Mar | 16 | +₹34,890 | +₹30,535 | green |
| Apr | 20 | +₹26,335 | +₹56,870 | green |
| May | 16 | −₹25,560 | +₹31,310 | green (negative month) |
| Jun | 21 | +₹24,195 | +₹55,505 | green |
| Jul | 17 | +₹29,060 | +₹84,565 | green |
| Aug | 16 | +₹2,730 | +₹87,295 | green |
| Sep | 19 | +₹7,855 | +₹95,150 | green |
| Oct (premiums) | 16 | +₹14,169.75 | +₹109,319.75 | green |

## PART 1 — DIAGNOSIS, Nifty only

### By representative component (Jan–Oct mixed)
| Representative | Trades | Net | Full-target |
|---|---|---|---|
| (lA) v2 | 29 | **+₹76,620.25** | 55.2% |
| V5 v2 | 16 | +₹19,370 | 50.0% |
| Volrix (b) | 12 | +₹34,190 | (day-exit legs; FT flag not comparable) |
| Skill V3 | 122 | **−₹20,860.50** | 32.8% |

Only ONE component is negative as representative: Skill V3. (lA) is the
strongest Nifty leg (55.2% FT). This is NOT a whole-system failure.

### By direction
| Direction | Trades | Net | Full-target |
|---|---|---|---|
| CE | 90 | +₹8,256.50 | 27.8% |
| PE | 89 | **+₹101,063.25** | 44.9% |

CE is near-flat with poor hits; PE carries Nifty. Skill-representative
split: Skill CE 73 trades **−₹27,798.50** (30.1% FT); Skill PE 49 trades
+₹6,938 (36.7% FT). Skill standalone Jan–Sep: CE 76 trades −₹46,590
(28.9% FT) vs PE 75 trades +₹51,290 (45.3% FT); early −₹36,480 (94 legs)
vs late +₹41,180 (57 legs).

### Solo vs confirmed — the sharpest split
| | Trades | Net | Full-target |
|---|---|---|---|
| Solo (1 system only) | 123 | **−₹50,975.50** | 31.7% |
| Confirmed (≥2 systems) | 56 | **+₹160,295.25** | 46.4% |
| Skill-rep solo | 111 | −₹52,875.50 | 30.6% |
| Skill-rep confirmed | 11 | +₹32,015 | 54.5% |

### Timing × solo — where the loss actually sits
| | Trades | Net | Full-target |
|---|---|---|---|
| Solo + early (≤09:55) | 71 | **−₹58,820.50** | 28.2% |
| Solo + late | 52 | +₹7,845 | 36.5% |
| Confirmed + early | 40 | +₹130,030 | 42.5% |
| Confirmed + late | 16 | +₹30,265.25 | 56.2% |
| All early | 111 | +₹71,209.50 | 33.3% |
| All late | 68 | +₹38,110.25 | 41.2% |

Early alone is NOT the problem (confirmed-early is strongly positive);
solo alone is bad; **solo AND early together is the losing intersection**.

### Why Jan/Feb closed red, and why May dipped
- **Jan (−₹11,050):** Skill-rep −₹18,625; CE −₹24,545 (PE +₹13,495);
  early legs −₹22,070 vs late +₹11,020. Worst legs are solo Skill stops
  (27 Jan CE −₹8,445; 29 Jan PE −₹5,360).
- **Feb (month +₹6,695, cumulative still red):** Skill-rep −₹21,255 and
  solo legs −₹15,890 — the month only stayed green because Volrix-rep
  contributed +₹17,920. Feb's gain (+₹6,695) was smaller than Jan's hole
  (−₹11,050), so the cumulative close stayed red at −₹4,355.
- **May (−₹25,560, worst month):** 13 of 16 legs entered ≤09:55 and
  early legs netted −₹25,585 (late legs +₹25 on 3 trades — May was, in
  effect, an all-early month); Skill-rep −₹18,620; solo −₹21,340;
  both directions negative (CE −₹15,280, PE −₹10,280).
- Exit profile (Jan–Oct): 93 stops −₹276,775 gross vs 71 target exits
  +₹385,650 — a stop-heavy Skill-solo population, not one blow-up leg.

**Plain diagnosis: Nifty's red closes come from unconfirmed (solo),
early (≤09:55) legs — overwhelmingly Skill-representative — in Jan, Feb
and May. Confirmed legs, (lA), V5, Volrix, PE and late legs are positive.
This differs from Bank (where the poison was specifically Skill CE):
on Nifty, Skill PE is positive standalone, so Bank's CE block must NOT
be copied blindly — the Nifty filter is solo + early, either direction.**

## PART 2 — TUNING, frozen before scoring, one knob at a time

Pass bar ("Nifty closes green"): Jan–Oct mixed net > 0 AND Oct premium
net > 0 AND month-end cumulative green at EVERY month-end Jan–Oct AND
FT improved vs base (36.3% Jan–Oct / 37.5% Oct) AND frequency ≥ 2/week
on both windows.

| Variant (single knob) | Jan–Oct trades / net mixed / FT / week | Oct trades / net premium / FT / week | Red month-end closes | Pass? |
|---|---|---|---|---|
| U1 Nifty base | 179 / +₹109,319.75 / 36.3% / 4.41 | 16 / +₹14,169.75 / 37.5% / 4.44 | Jan, Feb | No |
| **U1-N1: drop solo + early (≤09:55), any system/direction** | **108 / +₹168,140.25 / 41.7% / 2.66** | **8 / +₹10,775.25 / 50.0% / 2.22** | **None** | **YES — best** |
| U1-N2: drop Skill-rep CE (Bank-style block, tested not copied) | 106 / +₹137,118.25 / 40.6% / 2.61 | 7 / +₹12,828.25 / 42.9% / 1.94 | None | No — Oct frequency 1.94 < 2 |
| U1-N3: drop Skill-rep solo | 68 / +₹162,195.25 / 45.6% / 1.67 | 5 / +₹21,185.25 / 80.0% / 1.39 | None | No — frequency collapses |
| U1-N4: confirmed-only (drop all solo) | 56 / +₹160,295.25 / 46.4% / 1.38 | 4 / +₹15,555.25 / 75.0% / 1.11 | Jan (−₹430) | No — Jan still red, frequency collapses |
| U1-N5: drop Skill-rep early (≤09:55) | 104 / +₹116,160.25 / 38.5% / 2.56 | 7 / +₹5,145.25 / 42.9% / 1.94 | None | No — Oct frequency 1.94 < 2 |
| U1-N6: PE-only (drop all CE) | 89 / +₹101,063.25 / 44.9% / 2.19 | 6 / +₹7,198.25 / 33.3% / 1.67 | None | No — Oct FT falls, Oct frequency < 2 |
| U1-N7: drop Skill-rep solo + early | 113 / +₹147,080.25 / 39.8% / 2.78 | 8 / +₹10,775.25 / 50.0% / 2.22 | None | Yes — but weaker than N1 on net, FT and lowest close |
| U1-N8a: drop V5-rep (control) | 163 / +₹89,949.75 / 35.0% / 4.01 | 15 / +₹8,539.75 / 33.3% / 4.17 | Jan (−₹5,240) | No — V5 is not the problem |
| U1-N8b: drop Volrix-rep (control) | 167 / +₹75,129.75 / 38.3% / 4.11 | 15 / +₹8,539.75 / 33.3% / 4.17 | Jan, Feb (−₹17,235) | No — Volrix is not the problem; dropping it re-opens Feb red |

Notes: N7 passes but is strictly inside N1's logic (N1 applies the
solo+early drop to every system, not only Skill-rep; the extra legs N1
drops — 1 (lA) and 4 Volrix solo-early legs, −₹21,060 — are exactly the
day-loss Volrix solo triggers). N1 is therefore the cleaner single rule:
**no unconfirmed trade in the first 40 minutes, either direction, any
system.** N1 drops 71 legs summing −₹58,820.50 (66 Skill-rep −₹37,760.50,
4 Volrix −₹20,160, 1 (lA) −₹900; CE 48 legs −₹52,873.50, PE 23 legs
−₹5,947). In October N1 drops 8 legs that summed +₹3,394.50 — it gives
up a little October net to fix Jan–Oct; stated, not hidden.

## BEST VARIANT — U1-N1 month-by-month (mixed; October premiums)

| Month | Trades | Month net | Month-end cumulative | Close |
|---|---|---|---|---|
| Jan | 13 | +₹8,710 | **+₹8,710** | ✅ green |
| Feb | 13 | +₹28,755 | **+₹37,465** | ✅ green |
| Mar | 11 | +₹35,620 | **+₹73,085** | ✅ green |
| Apr | 11 | +₹25,660 | **+₹98,745** | ✅ green |
| May | 7 | −₹9,235 | **+₹89,510** | ✅ green (negative month — stated, not hidden) |
| Jun | 9 | +₹16,460 | **+₹105,970** | ✅ green |
| Jul | 12 | +₹24,585 | **+₹130,555** | ✅ green |
| Aug | 11 | +₹10,520 | **+₹141,075** | ✅ green |
| Sep | 13 | +₹16,290 | **+₹157,365** | ✅ green |
| Oct (premiums) | 8 | +₹10,775.25 | **+₹168,140.25** | ✅ green |

- **Every month-end cumulative closes green** under U1-N1; the lowest
  close is January at +₹8,710 (vs base −₹11,050).
- May remains a negative individual month (−₹9,235, 7 trades, 14.3% FT)
  even after filtering — the filter shrinks May's loss from −₹25,560
  but does not turn the month itself green. No variant was forced by
  deleting May.
- Concentration check: no single month dominates — largest month (Mar
  +₹35,620) is 21% of the total; ex-best-month total is +₹132,520.25.
- Frequency 2.66/week Jan–Oct and 2.22/week October — inside the user's
  2–3/week target band on both windows (base was above it at 4.41).
- Full-target improves on both windows (36.3% → 41.7%; 37.5% → 50.0%)
  but Jan–Oct FT (41.7%) is still below 50% — improved toward 50%, not
  at it. Stated as what remains short.
- Trades file: `index_options_U1_N1_nifty_trades.csv` (108 Nifty legs).

## Frozen November-paper NIFTY spec (separate Nifty log only)

From Mon 2026-11-02, separate Nifty log, no scoring/re-tuning during
November, month-end review only: **Nifty = U1-N1 exactly** — U1
components, unique-once per date+direction, with any key that is solo
(single-system) AND entry ≤ 09:55 blocked; log every blocked
solo-early day separately, and log any later confirmed entry on such a
day rather than assuming no-trade. November pass, separately for Nifty:
premium net > 0 AND month-end cumulative green AND FT improved AND
frequency ≥ 2/week.

## Verdict — NIFTY ONLY

**YES — Nifty now ends positive with every month-end closing green,
under U1-N1 (drop solo + early ≤09:55): Jan–Oct +₹168,140.25 mixed
(108 trades, 41.7% FT, 2.66/week) and October +₹10,775.25 premiums
(8 trades, 50.0% FT, 2.22/week), lowest month-end close +₹8,710 (Jan).**
What remains short: Jan–Oct full-target 41.7% is still below 50%;
May is still a negative individual month (cumulative stays green);
Jan–Sep is spot provisional, so no pure-premium Jan–Oct total exists;
and this is in-sample only — nothing is adopted until frozen November
paper validates it. Real money = ₹0.
