# LINE S4 — Two clock-based axes: last-hour momentum + VWAP deviation reversion

Equity cash intraday, LONG/SHORT. Paper only — real money ₹0, no orders.
All figures provisional per 100 shares, net of ₹40/trade. Window Jan–Oct
2026 as cached (home Oct 1–28; ext Oct 1–30). Pooled 50 primary.
Cells frozen in `stocks_S4_frozen.md` BEFORE scoring; timing audit ran
in the SAME run as first scoring, before any score was printed.

## Coverage check

Volume caches: **usable for all 50 stocks.** Both volume caches hold
every stock (home 15,300 bars/stock in 2026, ext 15,375), day sets match
the price caches on every shared day (home volume cache has one extra
day, 2026-10-29, absent from the home price cache — unused; the volume
cache covers 2026 only, so the placebo has no stale level for
2026-01-01 and simply doesn't fire that day). The only zero-volume bars
are 15:15/15:20 on ~62 days — after the 15:10 square-off, never inside
a signal VWAP. Volume-file OHLC matches the price cache exactly on
sampled days. VWAP = price-cache typical price × volume-cache volume,
joined on timestamp.

## Timing audit — CLEAN

**19,236 trades checked (Axis A 13,041 + Axis B 6,195), 0 violations.**
Every trade asserts, programmatically: entry bar index strictly greater
than signal bar index, and entry timestamp strictly after the
information-complete timestamp. Axis A qualifiers use only the day open
and the 14:30 bar close; entries at 14:35. Axis B VWAP at any signal is
the cumulative value through the signal bar only; the target level is
that same signal-bar VWAP (knowable at entry); placebo levels are the
previous trading day's final VWAP (complete at previous day 15:30).
Samples — A: GODREJCP 2026-01-07 SHORT, info 14:30 → entry 14:35 (day
move −2.16%). B: GODREJCP 2026-01-27 LONG, info 11:20 → entry 11:25
(close −1.57% vs intraday VWAP 1179.78).

## Axis A — Last-hour momentum (14:30 qualifier, 14:35 entry)

4,347 qualifying stock-days pooled (day move ≥1% by 14:30).

| Cell | Trades | Net ₹ | Exp/trade | Win% | Jan–May | Jun–Oct | Oct | Breadth | Home | Ext |
|---|---|---|---|---|---|---|---|---|---|---|
| A-MOM-SQ | 4,347 | **+18,406.00** | +4.23 | 46.3 | +167,271.00 | **−148,865.00** | **−69,924.00** | 16/50 | −25,454.00 | +43,860.00 |
| A-MOM-T05 | 4,347 | −91,555.01 | −21.06 | 46.7 | +19,721.00 | −111,276.01 | −35,540.70 | 11/50 | −52,059.65 | −39,495.36 |
| A-FADE-SQ (control) | 4,347 | −366,166.00 | −84.23 | 38.6 | −350,311.00 | −15,855.00 | +32,964.00 | 4/50 | −162,706.00 | −203,460.00 |

- **Control leg passes, everything else fails.** Momentum crushes its
  own fade (+18,406 vs −366,166): the last-70-minutes direction is not
  random. But the primary cell **flips sign between halves**
  (+167,271 → −148,865), October is deeply negative, breadth is 16/50,
  and ULTRACEMCO alone (+70,780) exceeds the whole pooled net.
- **The effect is one-sided:** on down-days the SHORT continuation earns
  **+175,574**; on up-days the LONG side **loses −157,168** — up-moves
  into 14:30 tend to give back into the close, down-moves keep sliding.
  Diagnostic colour only — no short-only rescue variant was frozen.
- The 0.5%/0.5% box (A-MOM-T05) destroys the remainder: 970 stops vs
  1,080 targets but net −₹91,555 — the last-hour path is too choppy for
  a tight symmetric box after costs.
- Best/worst (A-MOM-SQ): ULTRACEMCO +70,780, EICHERMOT +29,050, LT
  +17,630 / MARUTI −37,600, ASTRAL −13,260, SUNPHARMA −7,340.

**Axis A gate: FAIL** (halves, breadth, October legs fail; audit clean
and control beaten are the only legs passed).

## Axis B — VWAP deviation reversion (±1.5% from 11:00)

Target = signal-bar VWAP capped at +/−0.75%, stop 0.5%, 15:10 out.
The frozen skip rule (entry already past the level) fired **0 times**.

| Cell | Trades | Net ₹ | Exp/trade | Win% | Jan–May | Jun–Oct | Oct | Breadth | Home | Ext |
|---|---|---|---|---|---|---|---|---|---|---|
| B-REV-LONG | 581 | −51,514.11 | −88.66 | 38.9 | −32,642.04 | −18,872.07 | −1,387.50 | 17/50 | −19,673.20 | −31,840.91 |
| B-REV-SHORT | 535 | −32,431.80 | −60.62 | 36.4 | −41,544.67 | +9,112.87 | +2,042.05 | 14/50 | −12,640.80 | −19,791.00 |
| B-PBO-LONG (placebo) | 2,693 | −181,352.53 | −67.34 | 39.1 | −85,612.21 | −95,740.32 | −38,731.97 | 12/50 | −81,659.73 | −99,692.80 |
| B-PBO-SHORT (placebo) | 2,386 | **+75,371.13** | +31.59 | 44.0 | +44,337.79 | +31,033.34 | +21,723.81 | 20/50 | −36,803.04 | +112,174.17 |

- **Reversion does not pay after costs.** A close 1.5% away from VWAP
  after 11:00 does not snap back reliably: stops dominate targets in
  both REV cells (LONG 304 stops vs 158 targets; SHORT 286 vs 145),
  and REV-LONG is negative in both halves on both universes.
- **Placebo read kills the short cell outright:** the STALE-level
  placebo short (+75,371, both halves positive) beats the real-VWAP
  short (−32,432) — yesterday's flat level "works" better than today's
  live VWAP, which means the live-VWAP construction adds nothing on
  that side. Combined REV (−83,945.91) tops combined PBO (−105,981.40)
  only because PBO-LONG is catastrophic (MARUTI −124,647 alone).
- The PBO-SHORT number is a **control, not a candidate** — and its
  universes violently disagree (home −36,803 vs ext +112,174; MARUTI
  +105,178 of it). It is recorded as an oddity, nothing more.
- Best/worst (REV-LONG): TITAN +7,898, GLENMARK +3,469 / MARUTI
  −21,144, LT −7,780. (REV-SHORT): MARUTI +16,650, TVSMOTOR +14,923 /
  ULTRACEMCO −12,746, LT −11,837.

**Axis B gate: FAIL** (halves and breadth fail on both REV cells;
B-REV-SHORT also fails its placebo leg).

## Verdict

**Both axes DEAD under the frozen gate. No candidate — no
`stocks_S4_candidate_spec.md` was frozen.** Audit was clean
throughout; these are honest negatives, not artefacts. What the line
actually establishes: (1) last-hour direction is real against a fade
but one-sided (down-days only) and regime-flipping — not a tradable
book as frozen; (2) intraday VWAP deviation at 1.5% is a continuation/
chop signal at these exits, not reversion, and live VWAP adds nothing
over a stale level on the short side.

Files: `stocks_S4_frozen.md`, engine `stocks_S4.py`,
`stocks_S4_results.json`, trade dumps `stocks_S4_<cell>_trades.csv`
(7 cells), all in ~/workspace/trading/.
