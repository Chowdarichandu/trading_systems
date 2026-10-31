# Index OPTIONS — October Complete Verdict (October 2026 only)

Paper only, no orders, no stocks, no futures. Index OPTIONS only.
Nifty and Bank Nifty separately, never pooled, never deduped across versions/indices.

**User correction applied (2026-10-30 10:01 IST): "First complete October."**
This verdict uses ONLY October 2026, 1–28 Oct, 18 trading days, as defined in all
prior October work. It does NOT start, score, or report any Jan–Oct expansion work.
Jan–Oct comes only after October is complete. Nothing here is adopted on October
alone; November 2026 paper (from Mon 2026-11-02, separate Nifty/Bank logs,
no re-tuning during November) remains validation, but this verdict does not wait
for November.

## Scope limit — read this first

"October complete" here means the 1–28 Oct window, NOT the calendar month to 30 Oct.
29 Oct and 30 Oct are NOT in this verdict: 29 Oct has no complete 5-min cache
(Bank intraday file only, Nifty daily OHLC only) and 30 Oct had not closed when the
October files were scored. Any 29–30 Oct result must be a separate, later addition,
never backfilled into these October numbers.

## October completeness — verified by re-counting the CSVs, not by trusting summaries

| Premium-scored set | File | Legs / trades | NOT_COMPUTED | Dates |
|---|---|---|---|---|
| v2 taken trades — (lA) v2, Skill v2, V5-v2 | [index_options_premium_october_trades.csv](sandbox://workspace/trading/index_options_premium_october_trades.csv) | 31 taken trades | **0** — every row `premium_status = COMPUTED` | 2026-10-01 to 2026-10-28 |
| NS1–NS6 October premium legs | [index_options_newsetup_premium_october_trades.csv](sandbox://workspace/trading/index_options_newsetup_premium_october_trades.csv) | 84 legs | **0** — every row `premium_status = COMPUTED` | 2026-10-01 to 2026-10-28 |
| Volrix v2 (overlay) | [index_options_v2_october_trades.csv](sandbox://workspace/trading/index_options_v2_october_trades.csv) | 0 trades, by design | n/a — 0 triggers, not a missing fetch | full October scan |

Reconciliation notes (so the counts are not misread):
- The v2 October file has 48 rows, NOT 31: 31 taken trades + 15 S1-blocked Skill
  signals (8 Nifty, 7 Bank — blocked rows, correctly never premium-scored) + 2
  Volrix zero-trigger rows. The 38 `NOT_COMPUTED` cells in that older file are the
  blocked rows plus the pre-completion partial premium overlay; they are superseded
  for taken trades by the 31/31 COMPUTED premium-completion file. Do not quote the
  old partial overlay (e.g. V5-v2 Nifty −₹4,804.75 on 2 trades) — the complete
  premium file gives V5-v2 Nifty +₹825.25 on 3 trades.
- 31 + 84 = 115 is LEGS, not unique trades. NS1/NS2 base and morning legs reproduce
  the Skill S1 taken legs (NS1 base: 8 Nifty + 9 Bank = 17; NS2 morning: 8 Nifty +
  9 Bank = 17), so the NS set overlaps the v2 set by construction. Do not add the
  two sets into a portfolio total.
- NS6 Bank has 0 October legs (0 trades), not a NOT_COMPUTED gap: the session-range
  level never fired for Bank in October. NS6 Nifty has 2 legs.
- Premium method (uniform overlay, stated in both premium files): entry = open of
  first 5-min option candle after the spot signal; stop = entry − 50, target =
  entry + 90 option points, both CE and PE; stop before target per bar including
  the entry bar; square-off 15:10; net per 1 lot = (exit − entry) × lot − ₹220
  assumed cost; lot Nifty 65 / Bank 30; strike ATM nearest 100 to entry spot;
  expiry monthly 2026-10-27 for 1–27 Oct, weekly 2026-11-03 for 28 Oct trades.
  This is the V4/V5-v2 options overlay, NOT Skill's or (lA)'s native spot rule
  (spot stop = signal-bar high/low, target = 2× spot risk). Premium rows for
  Skill/(lA)/NS signals are therefore "V4-overlay premium outcome of those spot
  signals", not those versions traded under their native rule. By construction a
  premium target is +₹2,480 (Bank) / +₹5,630 (Nifty) and a premium stop is
  −₹1,720 (Bank) / −₹3,470 (Nifty), so premium ranking is compressed versus spot.
- Early-October trades are on the long-dated monthly 27 Oct contract, not a weekly
  contract — a weekly trader's premiums would differ. This caveat travels with
  every premium number below.

## October-only ranked table — premiums per 1 lot (frequency = legs ÷ 18 days × 5)

Pass legs: net > 0 AND full-target ≥ 50% AND frequency ≥ 5.00/week.
Full-target = premium target exit only; square-off greens do not count.

### v2 versions (premium completion, 31 taken trades)

| Version / index | Trades | Targets | Premium net / 1 lot | Full-target | /week | Legs passed |
|---|---|---|---|---|---|---|
| V5-v2 Bank | 4 | 4 | **+₹9,920.00** | 100.0% | 1.11 | net ✓, FT ✓, freq ✗ |
| (lA) v2 Nifty | 3 | 1 | **+₹6,678.50** | 33.3% | 0.83 | net ✓, FT ✗, freq ✗ |
| Skill v2 Nifty | 8 | 2 | **+₹3,394.50** | 25.0% | 2.22 | net ✓, FT ✗, freq ✗ |
| (lA) v2 Bank | 4 | 2 | **+₹1,520.00** | 50.0% | 1.11 | net ✓, FT ✓, freq ✗ |
| V5-v2 Nifty | 3 | 1 | **+₹825.25** | 33.3% | 0.83 | net ✓, FT ✗, freq ✗ |
| Skill v2 Bank | 9 | 3 | **−₹2,880.00** | 33.3% | 2.50 | net ✗, FT ✗, freq ✗ |
| Volrix v2 Nifty | 0 | — | ₹0 | — | 0.00 | no trigger (min prev-day close −1.64%, 8 Oct) |
| Volrix v2 Bank | 0 | — | ₹0 | — | 0.00 | no trigger (min prev-day close −1.16%, 23 Oct) |

### NS1–NS6 new setups (October premiums, 84 legs)

| Family / index | Legs | Targets | Premium net / 1 lot | Full-target | /week | Legs passed |
|---|---|---|---|---|---|---|
| NS1 Nifty | 13 | 3 | **+₹1,696.50** | 23.1% | 3.61 | net ✓, FT ✗, freq ✗ |
| NS1 Bank | 14 | 6 | **+₹1,120.00** | 42.9% | 3.89 | net ✓, FT ✗, freq ✗ |
| NS2 Nifty | 12 | 3 | **−₹1,050.75** | 25.0% | 3.33 | net ✗, FT ✗, freq ✗ |
| NS2 Bank | 10 | 4 | **−₹400.00** | 40.0% | 2.78 | net ✗, FT ✗, freq ✗ |
| NS3 Nifty | 5 | 0 | **−₹4,395.50** | 0.0% | 1.39 | net ✗, FT ✗, freq ✗ |
| NS3 Bank | 3 | 1 | **−₹960.00** | 33.3% | 0.83 | net ✗, FT ✗, freq ✗ |
| NS4 Nifty | 3 | 1 | **+₹2,885.75** | 33.3% | 0.83 | net ✓, FT ✗, freq ✗ |
| NS4 Bank | 5 | 3 | **+₹4,000.00** | 60.0% | 1.39 | net ✓, FT ✓, freq ✗ |
| NS5a Nifty | 7 | 1 | **+₹8,710.50** | 14.3% | 1.94 | net ✓, FT ✗, freq ✗ |
| NS5a Bank | 6 | 1 | **−₹6,120.00** | 16.7% | 1.67 | net ✗, FT ✗, freq ✗ |
| NS5b Nifty | 2 | 0 | **−₹1,668.50** | 0.0% | 0.56 | net ✗, FT ✗, freq ✗ |
| NS5b Bank | 2 | 0 | **−₹3,440.00** | 0.0% | 0.56 | net ✗, FT ✗, freq ✗ |
| NS6 Nifty | 2 | 0 | **−₹6,940.00** | 0.0% | 0.56 | net ✗, FT ✗, freq ✗ |
| NS6 Bank | 0 | — | ₹0 | — | 0.00 | no trades, not a missing fetch |

Notes on two cells that must not be over-read:
- NS5a Nifty premium net (+₹8,710.50) is positive only through square-off greens;
  its full-target rate is 14.3% (1 of 7), so the FT leg fails and the net does not
  make it a pass. Spot FT for the same legs was 57.1% — the sharpest spot-to-premium
  reversal in October.
- NS1 Bank premium net (+₹1,120.00) is base −₹2,880 rescued by second legs +₹4,000;
  NS1 Nifty premium net (+₹1,696.50) is base +₹3,394.50 dragged by second legs
  −₹1,698. The same second-leg mechanic helps one index and hurts the other in
  October — it is not a consistent October edge.

## Families A–D, October — spot provisional only, NOT premium-ranked

A–D were scored on spot provisional (points × 100 shares − ₹40) and were NOT
premium-scored, so they do not enter the premium ranked table above and cannot
overturn it. Their October spot verdicts, for completeness:
- **A — Parameters:** no variant improves net + full-target + frequency together on
  any track. Closest to frequency: widened-neutral Skill Bank, 3.33/week spot,
  5/12 full-targets (41.7% < 50%), +₹28,690 spot provisional. Discards include
  target 1.5×, target 2.5× / stop 1.25× (destroy Skill Bank), room ≥1.5× as an S1
  filter (kills Skill outright), pooled 1/week cap. Candidates for frozen
  validation only: widened-neutral Skill S1; stop 1.25× for (lA) Bank (single-day
  8 Oct flip — not a rule).
- **B — Indicators:** no indicator family kept as best. EMA discards (kills Skill
  Nifty's biggest winner, net flips to −₹8,130 spot); RSI extremes discard as a
  blanket rule (helps only Skill Bank); ATR stops discard as a general rule;
  extended OR discards as a replacement. VWAP / volume NOT TESTED (cache has no
  volume column).
- **C — Approaches + entry times:** no variant reaches 5/week on any track on spot
  (best: Skill v2 base/R1 Bank, 2.50/week). October-only keeps, nothing combined:
  C1-O1 Skill Bank + (lA) Bank; C2-R1 Skill Nifty / Skill Bank / (lA) Bank (weak);
  C3-pullback Skill Bank only; C4a (lA) Bank only; C4b Skill Nifty only. All
  Family C scoring is spot provisional; premiums were NOT_COMPUTED in that run.
- **D — Different candles:** 5-min kept as the best grid. 1-min audit kept but grid
  discarded (5-min stops are real, 15/16 not ordering artefacts; 1-min outcomes
  shrink targets and flip (lA) Nifty 8 Oct to a stop — fragility warning, 2-day
  subset only). 3-min not scored October-wide (cannot be built without inventing
  bars). 15-min discarded on all tracks (risk-inflated nets, Skill Bank negative
  on spot, (lA) Nifty loses a target).

## October-complete verdict

**NO version passes ALL legs on October premiums alone.**
- Frequency fails on EVERY premium track: the highest October premium frequency is
  NS1 Bank at 3.89/week, then NS1 Nifty at 3.61/week, then NS2 Nifty at 3.33/week.
  No track reaches 5.00/week. A version at 5/week would need 18 legs in 18 days;
  the most any October track produced is 14 (NS1 Bank).
- Two tracks pass net AND full-target but fail frequency only: **V5-v2 Bank**
  (4 trades, 100% full-target, +₹9,920.00, 1.11/week — needs 14 more legs at the
  same quality to reach 5/week) and **NS4 Bank** (5 legs, 60.0% full-target,
  +₹4,000.00, 1.39/week — needs 13 more legs).
- **Closest single family overall: NS1 (second convicted signal per day).** It is
  the only family with net > 0 on BOTH indices on October premiums AND the
  closest to the frequency leg on both indices — but it fails exactly two legs
  on both indices: full-target (Nifty 23.1%, 3 of 13 — needs 7 of 13 to reach 50%;
  Bank 42.9%, 6 of 14 — needs 7 of 14) and frequency (Nifty 3.61/week, needs 5 more
  legs in 18 days; Bank 3.89/week, needs 4 more legs). Frequency was nearly fixed
  by NS1; hit quality was not.
- Closest single track by legs passed: V5-v2 Bank and NS4 Bank (2 of 3 legs each,
  failing frequency only). They are NOT "closest overall" as families, because
  neither passes on the other index (V5-v2 Nifty fails FT; NS4 Nifty fails FT and
  frequency badly).
- Skill v2 Bank, the October frequency leader among v2 versions (2.50/week), is
  net NEGATIVE on premiums (−₹2,880.00) despite being net positive on spot
  (+₹8,675 provisional) — a sign flip. Frequency without premium edge is worthless,
  and spot frequency must not be quoted as premium frequency.

**October is therefore complete in the sense the user asked: every October taken
trade is premium-scored, the ranked table above is the October record, and the
verdict is a clean fail on frequency (and, for most tracks, on full-target too).
Nothing is adopted on October alone.** The next step, only after this October
verdict, is the Jan–Oct expansion work — which is NOT reported here, by the
user's instruction.

## Source files

- [index_options_premium_october_trades.csv](sandbox://workspace/trading/index_options_premium_october_trades.csv) — 31 v2 taken trades, 0 NOT_COMPUTED
- [index_options_newsetup_premium_october_trades.csv](sandbox://workspace/trading/index_options_newsetup_premium_october_trades.csv) — 84 NS legs, 0 NOT_COMPUTED
- [index_options_newsetups_report.md](sandbox://workspace/trading/index_options_newsetups_report.md) — NS1–NS6 frozen definitions, method, and full per-family verdicts
- [index_options_v2_october_trades.csv](sandbox://workspace/trading/index_options_v2_october_trades.csv) — 48 rows: 31 taken + 15 S1-blocked + 2 Volrix zero-trigger rows
- [index_options_progressive_tuning.md](sandbox://workspace/trading/index_options_progressive_tuning.md) — families A–D October spot sections
