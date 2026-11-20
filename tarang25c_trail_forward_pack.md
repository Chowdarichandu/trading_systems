# TARANG-T26-C-TRAIL — FORWARD-PAPER PACK (frozen TRAIL rules, prepared 2026-11-17)

**Status: PREPARED, NOT STARTED.** This pack exists so
that, on the owner's explicit word, the TRAIL variant
of T25-C can begin forward paper scoring with zero
further design work. It sits beside the frozen book's
pack (`tarang25c_forward_pack.md`). Nothing here is
scheduled, no cron exists, and the scorer is run only
by hand (or by a future instruction from the owner).
Whether forward paper runs the frozen rules, the TRAIL
variant, or both is the owner's decision, on his word
— Design 26 report S.3.2.

Basis: equity cash, PROVISIONAL per 100 shares,
₹40/trade, paper only, real money ₹0. No stock options.

## The gate record (Design 26 WS3, tarang26_2026-11-17.md)

TARANG-T26-C-TRAIL (trailing-after-half exit on
T25-C's exact entries) — **PASS, 9 of 9 legs:**

| Leg | 2025 | 2026 |
|---|---|---|
| Net | +₹1,58,473.60 | +₹74,939.33 |
| Trades / win rate | 563 / 31.1% | 548 / 28.1% |
| Gross/trade (levy ₹40) | +₹321.48 | +₹176.75 |
| Placebo percentile | 100.0 | 100.0 |
| Ex-top-3 net | +₹1,28,178.60 | +₹45,669.33 |
| Max drawdown (year) | −₹2,25,367.40 | −₹1,95,748.67 |

Worst month Jan 2026 −₹11,897.39 (bar −₹15,000);
November 2026 slice +₹13,626.62 (42 trades); audits
clean (exit parity engine-vs-audit 0 mismatches on
1,111 trades). Direction-flip placebo −₹91,648.93 /
−₹87,694.80. Against the frozen book (Design 25:
+₹1,51,307.50 / +₹50,274.68): TRAIL pays **more in
both years** (+₹7,166.10 / +₹24,664.65) with drawdown
*reduced* in both years. Stated plainly, as in the
Design 26 report: the 2026 monthly pace (₹6,812.67)
is better than the frozen book's (₹4,570.43) and still
below the ₹15,000/month segment floor, and the
per-year drawdowns are large against the nets. The
pass is a gate pass, not a sizing claim.

**Why it pays (the conversion anatomy, Design 26):**
131 frozen stops first retraced half the gap and then
came back; under TRAIL they exit at the breakeven stop
(+₹84,728.75 vs frozen). Against that, 117 frozen
square-offs armed the trail and fell back to breakeven
(−₹52,898.00 — the tax on drift trades that visited H
and reversed). The trail does not cap the drift; it
only refuses to let a trade that has already recovered
half the gap die at −1%.

## Frozen rules — exactly as gated (tarang26_SPEC.md S.4)

**Universe and data:** identical to the frozen pack —
the 127 verified F&O names (`tarang23_score.NAMES23`),
5-min bars from the same stores
(`data/tarang_vol/<SYM>/spot_5m_vol.csv`). A forward
day must be present in those stores (bars through
15:15) to be scored.

**Entries — T25-C's frozen entries, unchanged:**

    gap% = (today's first-bar open / previous trading
            day's last close) − 1

- gap% ≥ **+0.015** → one candidate, **SHORT**, entered
  at the day's first-bar open (bar local 0, the 09:15
  bar). Up-gaps only. A name's first store day produces
  no candidate.
- **Caps:** at most **10 taken trades per day**, at
  most **1 per name-day** (structural). A candidate not
  taken does not defer.
- **Allocation** (binds only when a day has > 10
  candidates): rank by (1) **|gap%| DESC** (exact
  float); (2) **vol_ratio DESC** — vol[first bar] /
  mean(vol over the 20 bars ending at the first bar),
  0 if the mean is 0; (3) **universe order ASC**. Take
  the top 10.

**Exit — TRAILING-AFTER-HALF (the only difference from
the frozen pack):**

For each trade: entry px = the first-bar open;
prev_close = the name's previous store day's last
close; the **half-retrace level** is
**H = (px + prev_close) / 2** (for these SHORT up-gap
fades, H < px always).

- The disaster stop starts at **entry × 1.01**
  (SHORT), stop-first: scanning from the entry bar, a
  bar that opens at or above the stop fills at the
  bar's open; otherwise a bar whose high reaches the
  stop fills at the stop.
- **Arming:** once a bar's favourable extreme reaches
  H (for SHORT, a bar whose **low ≤ H**), the stop
  moves to **breakeven (px)** from the **NEXT bar**
  onward. Arming is evaluated **after** the bar's own
  stop / square-off checks, so a bar never both arms
  and is stopped by the new level.
- From then on the stop check uses px with the same
  fill rules (a bar opening at or above px fills at
  the open; otherwise a bar whose high reaches px
  fills at px).
- Otherwise exit at the **close of the square-off
  bar** — the day's last bar with timestamp ≤ 15:15.
- Exit reasons: **"stop"** (unarmed −1% stop),
  **"trailstop"** (armed breakeven stop), **"squareoff"**.
  There are no other exits. No target.

**Money:** gross = (exit − entry) × side × 100 shares;
net = gross − ₹40. Win = net > 0.

## The scorer

`tarang25c_trail_scorer.py` (this directory). Usage:

    python3 tarang25c_trail_scorer.py --date YYYY-MM-DD
    python3 tarang25c_trail_scorer.py --date YYYY-MM-DD --json out.json
    python3 tarang25c_trail_scorer.py --selftest

It computes the day's T25-C entries through the same
family machinery as the frozen pack (tarang23
prep/day_ctx, tarang24 sig_gapw2, tarang25
allocate25/vol_ratio_at) and scores them with the
TRAIL exit (tarang26 exit26_trail_engine — the engine
whose exits passed Design 26's engine-vs-audit parity
check). With `--json` it writes the taken trades in
the Design 26 trade-row format (line
TARANG-T26-C-TRAIL). `--selftest` runs the same two
pre-registered historical days as the frozen pack
(2025-08-18 and 2026-03-24, both cap-bound 10-trade
days) and verifies the output reproduces the published
Design 26 TRAIL trades for those dates exactly; the
Design 27 report states the self-test result.

**Forward use (only on the owner's word):** after a
trading day's bars are in the stores, run the scorer
for that date and append the taken trades to the
forward ledger. Until that word is given, the scorer
is run for nothing except its self-test.

## What is NOT in this pack

No scheduler, no cron, no live feed hookup, no order
placement of any kind, no position tracking beyond the
same-day score (every trade opens and closes the same
day by construction). This pack does not modify the
frozen T25-C book or its pack; the two packs are
alternatives (or companions) for the owner's
forward-paper decision, nothing more.
