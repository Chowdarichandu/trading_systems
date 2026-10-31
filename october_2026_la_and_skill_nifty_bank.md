# October 2026 — (lA) + Skill, Nifty and Bank Nifty, four separate columns

Paper only. No orders. No live token waited for — cache only.
Window: **2026-10-01 to 2026-10-28, 18 trading days** (cache ends 28 Oct;
29 Oct is excluded, as in every October run).

## Standing correction applied to this report

- **Index = options only for live trading.** This run is a **spot-trigger
  simulation**: spot index points are the trigger/levels only, never the
  traded instrument. No futures trade, no futures total, is in this report.
- **Rupees below are ONLY "per 100 shares, provisional cash translation —
  NOT an options-lot profit and NOT a futures profit"**, with ₹40/trade
  assumed cost. Index points are reported first for every column.
- **No option-premium P&L is computed here.** The cache in
  `~/workspace/trading/data/progressive/{NIFTY,BANKNIFTY}/` contains only
  `spot_5m.csv` + `spot_daily.csv` — there are no option candles in it,
  so an options-lot P&L cannot be honestly computed from this cache.
  Any future options P&L needs option candles with the lot size for that
  expiry stated.
- Columns are **never pooled and never deduped across columns**. A
  "separate systems sum" line is labelled as such; it is **not a
  portfolio P&L** (the same day's move can appear in two columns, e.g.
  8 Oct Nifty appears in both (lA) Nifty and Skill Nifty).

## Definitions (frozen from existing code, not re-tuned)

- **(lA) Nifty** — BN-confirmed rescan morning + band-filtered re-entry
  (`merged_skill_la_october.day_la_nifty`, v4 mode): first Nifty bar
  at/after the Bank Nifty break (first Bank bar 09:30–11:30 closing below
  Bank OR low), closing below Nifty OR low AND below Nifty PDL, OR width
  ≤360×scale, room ≥200×scale; entry next open, stop = signal high,
  target = entry − 2×risk, square-off 15:10. If the morning trade stops,
  a re-entry is scanned: candidates closing below OR low, re-entry risk
  in [10, rescan risk], morning scan-skip to 11:30, afternoon
  stop-on-first-fail to 15:05. Morning + re-entry count as **one**
  candidate per symbol+date, each leg ₹40 in the replay.
- **(lA) Bank mirror (provisional, NOT the original (lA))** —
  `day_la_bank`: roles swapped, confirming index = Nifty (first Nifty
  bar 09:30–11:30 closing below Nifty OR low), rescan = first Bank bar
  ≥ Nifty break, ≤11:30, closing below Bank OR low AND below Bank PDL,
  OR width ≤360×scale_bank (scale = Bank prev close / 55000), room
  ≥200×scale_bank; same replay and re-entry rules as above.
- **Skill Nifty / Skill Bank** — Day Trader skill OR entries only
  (`progressive_capped_v2` candidates): first 5-min close beyond OR high
  (CE) or below OR low (PE) after 09:30 up to 11:30, passing V4-style
  filters (bias-aligned: bearish→PE only, bullish→CE only, neutral→both;
  room ≥200×scale to the next PD level; CE signal close < PDH, PE signal
  close < PDL). Entry next open, stop = signal low/high, target = entry
  ± 2×risk, square-off 15:10. Flag/oversold entries are NOT included.
- **Cap, applied PER COLUMN (not pooled across columns)** —
  prospective target net ≥ ₹500, max 1 trade per symbol per ISO week,
  ranking setup_rank, bias_strong, room_ratio, target_net_rs
  (`merged_skill_la_october.cap_select` order). In October this cap
  changes only one column: Bank (lA) — see §4. Uncapped candidates are
  shown alongside capped totals so the cap effect is visible, not hidden.

## Results — capped, per column (points first)

| Column | Trades | Wins (net>0) | Full targets | Stops | Points | Provisional net (per 100 sh.) | Expectancy (prov.) | Max DD (prov.) |
|---|---|---|---|---|---|---|---|---|
| **(lA) Nifty** | 2 | 2 (100%) | 2 | 0 | **+231.60** | **+₹23,080** | +₹11,540 | ₹0 |
| **(lA) Bank Nifty (mirror)** | 2 | 1 (50%) | 1 | 0* | **+128.05** | **+₹12,725** | +₹6,362.50 | ₹7,475 |
| **Skill Nifty** | 2 | 1 (50%) | 1 | 1 | **+0.50** | **−₹30** | −₹15 | ₹5,470 |
| **Skill Bank Nifty** | 1 | 1 (100%) | 1 | 0 | **+166.80** | **+₹16,640** | +₹16,640 | ₹0 |

\* (lA) Bank's losing day is counted as `day_loss`, not `stop`, because
the column's unit is the whole day (morning + re-entry); its morning leg
did stop (see trade table). Full-target counts for (lA) count days whose
morning leg hit target with no re-entry.

Uncapped totals (same columns, cap removed):

| Column | Trades | Points | Provisional net |
|---|---|---|---|
| (lA) Nifty | 2 | +231.60 | +₹23,080 |
| (lA) Bank mirror | 3 | +369.05 | +₹36,785 |
| Skill Nifty | 2 | +0.50 | −₹30 |
| Skill Bank | 1 | +166.80 | +₹16,640 |

**Separate systems sum, capped — labelled, NOT a portfolio P&L:
+₹52,415 provisional** (23,080 + 12,725 − 30 + 16,640). Uncapped separate
sum: +₹76,475 provisional. Neither is what "we would have made" — the
columns overlap on days, use a provisional cash translation, and October
is 18 days with 1–3 trades per column.

## Trade table (capped trades; uncapped-only trade marked)

| Date | Column | Setup | Dir | Signal | Entry | Stop | Target | Exit | Exit reason | Points | Provisional net |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-01 | Skill Bank | or_breakout | CE | 09:55 | 54,923.50 | 54,840.10 | 55,090.30 | 10:35 target | target | +166.80 | +₹16,640 |
| 2026-10-07 | (lA) Bank | la_pe_rescan_reentry | PE | 09:35 | 54,654.85 | 54,729.20 | 54,506.15 | 09:40 stop | day_loss (morning stop, no re-entry) | −74.35 | −₹7,475 |
| 2026-10-08 | (lA) Nifty | la_pe_rescan_reentry | PE | 11:25 | 22,340.60 | 22,399.25 | 22,223.30 | 14:00 target | target | +117.30 | +₹11,690 |
| 2026-10-08 | Skill Nifty | or_breakdown | PE | 09:40 | 22,473.55 | 22,500.95 | 22,418.75 | 11:20 target | target | +54.80 | +₹5,440 |
| 2026-10-21 | (lA) Bank | la_pe_rescan_reentry | PE | 11:15 | 55,249.15 | 55,350.35 | 55,046.75 | 11:40 target | target | +202.40 | +₹20,200 |
| 2026-10-23 | (lA) Bank — **uncapped only, capped out** | la_pe_rescan_reentry | PE | 09:55 | 54,444.05 | 54,564.55 | 54,203.05 | 10:10 target | target | +241.00 | +₹24,060 |
| 2026-10-23 | (lA) Nifty | la_pe_rescan_reentry | PE | 10:05 | 22,526.25 | 22,583.40 | 22,411.95 | 10:35 target | target | +114.30 | +₹11,390 |
| 2026-10-28 | Skill Nifty | or_breakdown | PE | 10:15 | 22,519.95 | 22,574.25 | 22,411.35 | 10:55 stop | stop | −54.30 | −₹5,470 |

Full row-level file (including re-entry fields, all empty in October —
no (lA) re-entry fired on any October day):
[october_2026_la_skill_nifty_bank_trades.csv](sandbox://workspace/trading/october_2026_la_skill_nifty_bank_trades.csv)
Recompute script:
[october_2026_la_skill_recompute.py](sandbox://workspace/trading/october_2026_la_skill_recompute.py)
Summary JSON:
[october_2026_la_skill_nifty_bank_summary.json](sandbox://workspace/trading/october_2026_la_skill_nifty_bank_summary.json)

## Verification against the known October four-column file

Source: `october_2026_four_column.csv` (18 days, 1–28 Oct).

- **(lA) Nifty: EXACT match.** 2 trades, +₹23,080 provisional
  (8 Oct +₹11,690, 23 Oct +₹11,390). Recomputed entry/stop/target above
  reproduce both nets to the rupee.
- **Skill Nifty: EXACT match.** 2 trades, −₹30 provisional
  (8 Oct +₹5,440, 28 Oct −₹5,470).
- **Skill Bank: EXACT match.** 1 trade, +₹16,640 provisional
  (1 Oct, same trade as Bank V4 that day in the old file — counted in
  both columns there, and counted here in Skill Bank only because Bank
  V4 is not one of this run's four columns).
- **Bank (lA) mirror: NEW leg (Bank V4 in the old file is NOT (lA), so
  no direct comparison).** Capped: 2 trades, +₹12,725 provisional
  (7 Oct −₹7,475, 21 Oct +₹20,200) — this matches the Bank (lA) mirror
  totals already documented in `DOCUMENTED_V5_LA_BANKNIFTY.md` §2.
  Uncapped: 3 trades, +₹36,785 provisional (adds 23 Oct +₹24,060).
  The old file's Bank V4 October total (+₹43,630 on 4 trades: 1, 13, 21,
  26 Oct) is a different system and must not be compared trade-for-trade
  with Bank (lA).
- **No other difference.** Every capped trade in this run appears in
  either the old four-column file or the documented (lA) mirror totals,
  with the same date, direction, exit and net. The only new number is
  the uncapped Bank (lA) 23 Oct trade, which the old per-column cap had
  removed.

## Diagnosis of the failing October trades (before any tweak)

October's capped failing set is only **2 trades** — too small to tune on
alone, so each is checked against its Jan–Oct recurrence before any
family is proposed. Both failures are the same mechanism: a breakdown
signal that reversed back above the signal bar's high (the stop).

### F1 — (lA) Bank, 7 Oct 2026, −74.35 pts / −₹7,475 provisional

- What happened: rescan PE signal 09:35, entry 54,654.85 (09:40 open),
  stop 54,729.20 (signal high, risk 74.35). The stop was hit **on the
  entry bar itself, 09:40** — the breakdown did not hold for even one
  full bar. No re-entry fired afterwards, so the day stayed −₹7,475.
- Why the confirmation was weak: the confirming Nifty break was a
  one-bar dip. Nifty closed 22,587.60 at 09:35, below its OR low
  22,600.45 by only 12.85 points, then closed **back above** its OR low
  at 09:40 (22,617.10), and by 10:15 Nifty had rallied above its OR high
  (22,692.95). The (lA) rule as coded requires the confirming break to
  have happened *before* the rescan signal — it does **not** require
  the confirming index to stay below its OR low through the entry bar.
  On 7 Oct it did not stay below.
- Does this scenario recur in Jan–Oct? **Yes, and it is the dominant
  Bank (lA) failure mode.** Bank (lA) mirror, Jan–Oct capped: 23 trades,
  16 morning stops, 14 day-losses, −₹48,345 provisional. Uncapped Bank
  (lA): 30 candidates, 21 morning stops. The immediate-stop sub-pattern
  (stop within 10 minutes of the signal) recurs on 21 Jan (signal 10:20,
  stop 10:25, re-entry rescued the day to +₹360), 29 Jun (09:30→09:40,
  day −₹24,935), 19 Aug (09:30→09:40, day −₹3,770), and 7 Oct
  (09:35→09:40, day −₹7,475). The 7 Oct variant — immediate stop **plus
  no re-entry** — recurs only twice more uncapped (12 Jan, day −₹6,130;
  24 Jul, day −₹3,455). So the recurring problem is not "no re-entry";
  it is "a confirmed breakdown that reverses in the first bar(s)".

### F2 — Skill Nifty, 28 Oct 2026, −54.30 pts / −₹5,470 provisional

- What happened: OR breakdown PE signal 10:15 (close 22,517.70 below
  OR low 22,551.90), entry 22,519.95 (10:20 open), stop 22,574.25 (signal
  high, risk 54.30), target 22,411.35. Price dipped to 22,497.70 at
  10:20 but closed 22,510.55, then recovered steadily; the stop was hit
  at 10:55 when the candle high reached 22,575.10 — **0.85 points above
  the stop** — and price then ran to 22,638.80 by 11:30. A marginal,
  failed breakdown, not a wide stop-out.
- Does this scenario recur in Jan–Oct? **Yes, overwhelmingly.** Skill
  Nifty, Jan–Oct capped: 29 trades, 13 stops, +₹49,890 provisional
  overall — but **11 of the 13 stops are exactly this setup** (OR
  breakdown PE): 9 Jan, 6 Feb, 13 Feb, 2 Apr, 30 Apr, 13 May, 18 May,
  29 Jun, 8 Jul, 19 Aug, and 28 Oct. Only 2 Skill Nifty stops are OR
  breakout CE (30 Jan, 8 Jun). So 28 Oct is not an outlier; it is the
  modal Skill Nifty loss.
- Cross-check that sharpens the diagnosis: on 28 Oct, **Bank Nifty
  never broke down at all** — its OR low was 53,626.15 and its lowest
  post-09:30 close was above 53,720. The Skill OR rule has no
  cross-index confirmation, so a Nifty-only breakdown was traded while
  the confirming index was not breaking down. The (lA) rule, which does
  require a confirming break, produced no Nifty trade on 28 Oct.

### What October does NOT diagnose

- **(lA) re-entry did not fire on any October day** (all re-entry fields
  empty in the CSV). October therefore says nothing, good or bad, about
  the re-entry leg — and nothing in this report should be quoted as a
  re-entry conclusion. Jan–Oct, by contrast, is where the re-entry leg
  loses money in the Bank mirror (capped re-entry days −₹129,975 vs
  morning-target days +₹153,410 in the merged Jan–Oct analysis), which
  is why Bank and Nifty must stay separate systems.
- October's 18 days, 7 capped trades, cannot adopt anything. The two
  October winners per column are not evidence of an edge, and the two
  losses above are the only October failures available to diagnose —
  the tuning family below is therefore scoped on the **Jan–Oct failing
  sets**, with October as the first check, not the whole sample.

## Next options tuning family to try — O1, NOT yet run

**Tuning is NOT closed.** Per the 2026-10-30 standing requirement,
intraday options tuning continues family by family until we are ready
for paper trading for the next one month. The next family is O1, scoped
from F1 + F2 above — it is proposed here, frozen-to-be, and **not
scored in this report**.

### O1 — Cross-confirmation persistence (not just a prior break)

- **Rule (to be frozen verbatim before scoring):** a PE breakdown trade
  (both (lA) rescan PE and Skill OR breakdown PE) is taken only if the
  confirming index is **still below its own OR low on the signal bar
  AND on the entry bar** (two consecutive closes below its OR low
  straddling entry). For (lA) Nifty the confirmer is Bank Nifty; for
  (lA) Bank the confirmer is Nifty; for Skill Nifty the confirmer is
  Bank Nifty (new — Skill currently has no confirmer); for Skill Bank
  the confirmer is Nifty. CE trades are out of scope for O1 (all
  October failures are PE; CE confirmation is a later family if needed).
  Everything else — entry next open, stop = signal high, target =
  entry − 2×risk, square-off 15:10, per-column cap — is unchanged.
- **Why this family, from the diagnoses:** F1's confirmer broke for
  exactly one bar and closed back above its OR low on the entry bar —
  O1 filters 7 Oct. F2 had no confirmer break at all — O1 filters
  28 Oct. No other October trade is affected (all October winners had
  a confirmer break before their signal; whether the confirmer *stayed*
  below on the entry bar must be checked bar-by-bar in the O1 run, not
  assumed here).
- **How O1 will be judged (pre-registered, before it is run):**
  1. Run O1 on Jan–Oct 2026, **per column separately** (Nifty (lA),
     Bank (lA) mirror, Skill Nifty, Skill Bank), with the definition
     frozen above and no re-tuning on the window.
  2. Count, per column: failing trades filtered out vs winning trades
     killed by the filter, on the Jan–Oct capped sets (Bank (lA):
     14 day-losses; Skill Nifty: 13 stops, 11 of them OR-breakdown PE).
     O1 passes this leg only if it filters **more failing trades than
     winning trades killed**, in each column it is applied to — a
     filter that kills winners faster than losses is a failure, not a
     fix, and must be reported as such.
  3. Net and win rate must improve **without** the improvement coming
     only from deleting trades (report trades, net and win rate before
     and after O1, side by side, per column).
  4. October is then reported as a consistency check (F1 and F2 should
     both be filtered; October winners must not all be filtered out).
  5. **O1 is not adopted on Jan–Oct alone.** If it passes legs 2–4
     in-sample, it goes to November 2026 paper (from Mon 2026-11-02,
     daily after 15:10, separate Nifty and Bank logs, no re-tuning
     during November) before any adoption claim. If it fails any leg,
     the next family is scoped from the trades O1 still fails — tuning
     continues, it does not stop at O1.
- **Families deliberately NOT chosen next, and why:** a second-close
  confirmation was already swept exhaustively for Nifty Cluster 1 and
  did not turn the failing set green; stop widening / OR-high stops
  were also swept for that set. Repeating those families on October's
  2-trade failing set would be re-tuning on noise. O1 is chosen because
  it targets the one mechanism both October failures share that no
  prior family tested on these legs: **confirmation that does not
  persist through entry**.
- **What O1 does not claim:** it does not fix the Bank (lA) re-entry
  losses (a separate, larger Jan–Oct problem), it does not address CE
  trades, and it does not convert this spot-trigger simulation into an
  options P&L. Those remain open, after O1.

## Verdict on October alone

October alone adopts nothing. (lA) Nifty 2/2, Skill Bank 1/1, and the
Bank (lA) uncapped 23 Oct winner are small-sample results on 18 days.
The honest October output is the diagnosis above and family O1 — not a
system to trade. Live index trading remains **options only, paper only,
1 options lot**, until a version passes on November paper with its
definition frozen.
