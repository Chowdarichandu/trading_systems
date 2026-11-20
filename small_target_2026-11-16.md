# SMALL-TARGET EXIT TEST — 2026-11-16

Owner's order (2026-11-16 18:06 IST): on the SAME entries the running
books already take, what happens if the exit books a small fixed target
(+20 / +30 premium points) instead of riding to +90? Spec frozen before
scoring: small_target_SPEC.md. Paper only, real money ₹0.

**Bottom line: the small target wins far more often and makes far less
money — on all three streams, at all three settings. All 9 variants
FAIL the frozen verdict rule (beat the control total AND zero red
months AND beat the placebo). No variant is a PASS, so no forward
shadow was built.**

## Controls — reproduced exactly before any variant was scored

- BANK STACK (TUNED STACK v2): **+₹127,351.50 / 111 legs**, rebuilt
  leg-for-leg against the frozen eve19 file; leg set == books-fix
  anatomy. WR 59.5% · 89 trade-days · ₹1,430.92/trade-day · zero red
  months · ex-top-3 +₹100,528.50.
- BANK LEGACY (v21 frame): **+₹83,650.50 / 99 legs**, replay ==
  recorded exit on every leg; leg set == anatomy. WR 52.5% · 92
  trade-days · ₹909.24/trade-day · ex-top-3 +₹54,610.50 (control itself
  has 3 red months: Apr, Jul, Aug).
- NIFTY TUNED v1: **+₹103,050.25 / 74 legs**, frozen CSV nets; the
  standing-geometry replay from candles reproduced every leg's exit
  time, exit premium and net — **0 mismatches**; leg set == anatomy.
  WR 51.4% · 66 trade-days · ₹1,561.37/trade-day · ex-top-3
  +₹69,585.25 (control itself has 1 red month: Mar −₹1,216.50).

Timing/leak audit on the new exit fills: **0 problems** on all 9
variants (every exit ≥ entry, every fill is the exit bar's own
level/open/close, entry fills == recorded entry premiums on all 284
legs). Independent re-sum of small_target_trades.csv: **exact** for
every stream × variant × period.

## Why the numbers come out this way — the MFE race

Share of Jan–Oct legs whose premium reached the small target before it
reached the −50 stop, measured on each leg's own path over the time the
book actually held it:

| Stream | reached +20 before −50 | reached +30 before −50 | median max run (pts) | p25 / p75 |
|---|---|---|---|---|
| Bank stack | 82.9% | 78.4% | **+93.0** | +36.0 / +135.0 |
| Bank legacy | 79.8% | 74.7% | **+89.9** | +30.0 / +123.9 |
| Nifty v1 | 73.0% | 63.5% | **+52.0** | +18.8 / +108.8 |

That is the whole story. The small target is reached on roughly
three-quarters of trades — so the win rate jumps to 73–83%. But the
typical winning trade in these books travels **+52 to +93 points**, and
half the Bank legs run past +90. The books' profit is the tail: the
runner geometry converts a +90 touch into +90/+150/+180 exits. Capping
the exit at +20 pays ₹380 a win on Bank (20 × 30 − ₹220) where the
control averages **+₹1,147 a leg**; at +30 it pays ₹680. The extra wins
the cap creates (stops converted to small wins) are worth far less than
the tail it cuts off. Tightening the stop to −30 (S30T) makes it worse
again — it cuts recovering legs without adding anything.

## Bank stack (control +₹127,351.50 · WR 59.5% · ₹1,430.92/TD)

| Variant | Total | vs control | WR | ₹/TD | Ex-top-3 | Halves H1/H2 | Placebo | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| S20 (+20/−50) | +₹2,733.00 | −₹124,618.50 | 82.9% | 30.71 | +₹1,593.00 | +9,060 / −6,327 | −₹9,360.00 | May, Jun, Jul, Aug, Oct | FAIL |
| S30 (+30/−50) | +₹18,333.00 | −₹109,018.50 | 78.4% | 205.99 | +₹16,293.00 | +12,360 / +5,973 | −₹12,960.00 | Apr, Aug | FAIL |
| S30T (+30/−30) | +₹1,680.00 | −₹125,671.50 | 63.1% | 18.88 | −₹360.00 | +960 / +720 | −₹16,560.00 | Feb, Mar, Apr, Jun, Jul, Aug | FAIL |

The trade-off in plain numbers: S30 raises the win rate 59.5% → 78.4%
and keeps **14%** of the money. November CF (4 legs, shown, never
selecting): control −₹2,680 · S20 −₹4,780 · S30 −₹4,480 · S30T −₹2,680.

## Bank legacy (control +₹83,650.50 · WR 52.5% · ₹909.24/TD)

| Variant | Total | vs control | WR | ₹/TD | Ex-top-3 | Halves H1/H2 | Placebo | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| S20 (+20/−50) | −₹4,380.00 | −₹88,030.50 | 79.8% | −47.61 | −₹5,520.00 | +1,620 / −6,000 | −₹10,680.00 | Apr, May, Jul, Aug, Oct | FAIL |
| S30 (+30/−50) | +₹7,320.00 | −₹76,330.50 | 74.7% | 79.57 | +₹5,280.00 | +3,120 / +4,200 | −₹9,480.00 | Apr, Jul, Aug | FAIL |
| S30T (+30/−30) | −₹1,080.00 | −₹84,730.50 | 61.6% | −11.74 | −₹3,120.00 | −1,080 / 0 | −₹10,080.00 | Mar, Apr, Jun, Jul, Aug | FAIL |

S20 and S30T turn a +₹83,650.50 book negative. November CF (7 legs):
control −₹3,640 · S20 −₹1,540 · S30 −₹2,440 · S30T −₹640 (November's
legs happened to suit small exits better — 7 legs, shown for the
record only; it does not change the Jan–Oct verdict).

## Nifty TUNED v1 (control +₹103,050.25 · WR 51.4% · ₹1,561.37/TD)

| Variant | Total | vs control | WR | ₹/TD | Ex-top-3 | Halves H1/H2 | Placebo | Red months | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| S20 (+20/−50) | +₹3,265.50 | −₹99,784.75 | 73.0% | 49.48 | +₹25.50 | −10,405.75 / +13,671.25 | +₹4,747.50 | Feb, Mar, Apr, May | FAIL |
| S30 (+30/−50) | +₹11,653.75 | −₹91,396.50 | 64.9% | 176.57 | +₹6,463.75 | −11,280 / +22,933.75 | +₹11,439.25 | Feb, Mar, May, Aug | FAIL |
| S30T (+30/−30) | +₹6,193.75 | −₹95,856.50 | 55.4% | 93.84 | +₹1,003.75 | −5,417 / +11,610.75 | −₹6,533.25 | Feb, Mar, May, Jun, Jul, Aug | FAIL |

Nifty S20 also fails the placebo leg outright (its own +30-min shifted
twin made more: +₹4,747.50). S30 beats its twin by only ₹214.50.
November CF (1 leg — the Nov 3 component-C CE that rode to +50.1 pts
by square-off): control +₹3,036.50 · S20 +₹1,080.00 · S30/S30T
+₹1,730.00 — on the month's only v1 winner, the small target would
have banked less than half.

## Verdict

Per the frozen rule, **FAIL on all nine** — every variant loses on
total (keeps between −5% and 18% of its control) and every variant
introduces red months the stack control does not have. The owner's
instinct is half right in the data: the entries DO reach +20/+30 on
73–83% of trades, so a small-target book would feel like winning
constantly. It would also earn roughly a tenth of what the same
entries earn now, because these books are paid by the trades that run
— median run +93 points on Bank — and the small target sells exactly
those trades at +20/+30. This is the same payoff shape the trailing-
stop test measured this morning, from the other side: anything that
truncates the runner truncates the book.

No PASS ⇒ no forward shadow built, no cron line to add. Nothing
running was touched. Files: small_target_SPEC.md ·
small_target_build.py · small_target_results.json ·
small_target_trades.csv (284 Jan–Oct legs × control + 3 variants,
plus the 12 November CF legs, each with entry/exit/fill/reason/net).
