# EKAM-2d — SPEC (FROZEN 2026-11-14, before scoring)

Programme: EKAM (registry `ekam_strategy.md`). The disaster-floor turn, from
the diagnosis in `ekam2c_2026-11-14.md`: the RSI upgrade improved totals and
placebos in both years, but 2026 drawdown deepened (−Rs35,575.00 vs S0
−Rs29,805.00), 2026 ex-top-3 fell (+Rs67,667.40 vs +Rs85,110.90), 2025
ex-top-3 is still −Rs2,359.90, and the 8 positions still open at the
2026-11-13 close — all upgraded rides — were marked −Rs23,582.00 combined:
the upgraded rides carry the book's open left tail. Research only — no book,
ledger or job is touched. Basis: equity cash · frozen 25-name Stock Book
watchlist · **per 100 shares PROVISIONAL** · Rs40/trade · paper only, real
money Rs0. Judged PER YEAR (2025, 2026), never pooled.

## 0. Base book — EKAM-2c, exactly as built

Everything is `ekam2c_SPEC.md` / `ekam2c_build.py` verbatim, imported, not
re-implemented: same data prep (`ekam_build.prep`), same merge/entry state
machine, same RSI-upgrade conversion (spec §2 of EKAM-2c, including the
causality carve-out), same exit stacks, same fill conventions, same stats
(`ekam_build.stats`) and same placebo (`ekam_build.placebo`, seed 20261114,
200 draws).

## 1. CONTROL (mandatory, before the variant)

(a) Run the EKAM-2c engine and check its per-year stats dicts against
`ekam2c_results.json` (`EKAM2c`) with FULL stats-dict equality, both years.
Headline anchors: 2025 — 74 trades · +Rs42,954.60 · WR 71.62% · avg hold
22.4 d · max DD −Rs44,077.00 · ex-top-3 −Rs2,359.90 · 2026 — 102 trades ·
+Rs141,328.40 · WR 62.75% · avg hold 21.2 d · max DD −Rs35,575.00 ·
ex-top-3 +Rs67,667.40.
(b) Placebo determinism: the EKAM placebo run against the control book
(N = the control's trade count per year) must reproduce the published
EKAM-2c percentiles, draw means and draw medians exactly (2025: 78.5 ·
+Rs15,420.27 · +Rs17,778.00 · 2026: 100.0 · +Rs39,208.93 · +Rs39,371.00).
Any mismatch in (a) or (b) = stop and report it; no EKAM-2d numbers are
produced.

## 2. THE ONE CHANGE — disaster floor on UPGRADED positions only

Applies ONLY to a position that has been UPGRADED under EKAM-2c §2 (entry
tag exactly `BB`, RSI upgrade trigger fired). Non-upgraded positions —
pure BB never upgraded, RSI-tagged, BOTH-tagged — are EKAM-2c verbatim,
with NO floor. (Plain EKAM-2 S0 stops were already tested and rejected
globally; nothing here reopens that. This floor exists only because
upgraded rides are the long holds — avg 21–22 days — and carry the open
left tail.)

- **Trigger.** On any day i from the conversion day onward, while the
  upgraded position is open: daily CLOSE c[i] ≤ entry × (1 − F).
  Two rows scored: **2d-10** (F = 0.10) and **2d-15** (F = 0.15).
- **Fill.** The trigger is known at day i's close, so the exit fills at
  day i+1's OPEN (the same convention as the other close-signal legs).
  If the trigger fires on the last data day, the exit fills at that day's
  close, exit_kind `FLOOR`, flagged forced (the EKAM convention for
  close signals on the last day). exit_kind for floor exits: `FLOOR`.
- **Priority within the day** (upgraded branch only): TIME60 at the open →
  CAP intraday → FLOOR close check → RSI ≥ 70 close leg. (TIME60/CAP keep
  the EKAM-2c causality carve-out: they apply only from the day after the
  conversion trigger. The FLOOR is a close-evaluated leg, so — exactly like
  the RSI ≥ 70 close leg — it IS evaluated on the conversion day itself.)
- **What does NOT change.** Entries, the merge, the conversion trigger,
  every other exit, position counting (`counted_upgrade` as in EKAM-2c),
  and all non-upgraded positions. No other stop anywhere. Because floor
  exits free names earlier, later entries may shift or fire where
  EKAM-2c's did not (the cascade) — that is part of the book, as in
  EKAM-2c vs S0.
- **Counting floor exits.** A floor exit is a closed trade with
  exit_kind `FLOOR`; counted per year by the EKAM entry-year rule
  (entry date in Jan 1 – Oct 31 of the year), with its combined net.

## 3. Reporting (per row — 2d-10, 2d-15 — per year, 2025 and 2026 separately)

Beside EKAM-2c's lines: trades · total · WR · avg hold · month table (net
and trades by entry month, Jan–Oct) · halves (H1 = entries Jan–Jun, H2 =
entries Jul–Oct) · ex-top-3 · equity-curve max drawdown (the EKAM ordering
rule) · worst trade · peak concurrent · forced count · **floor exits:
count and combined net**. Plus the trade-list diff vs EKAM-2c (counts of
trades only in one book, full EKAM-2c key).

## 4. PLACEBO

Same random-entry design as the EKAM run, verbatim (`ekam_build.placebo`,
seed 20261114, 200 draws): per year, N = the row's trade count that year;
percentile of the row's real total among the draw totals, plus draw mean
and median. (The placebo exit stack is the EKAM S0 stack — TIME60 →
middle-band — exactly as in the EKAM, EKAM-2b and EKAM-2c runs.)

## 5. NOVEMBER (descriptive only)

Per row: every position still open at 2026-11-13 (exit_kind FORCED at the
last data date), marked at the 2026-11-13 close, labelled **OPEN/MARKED**
— never counted as closed money (the EKAM year convention counts the
forced marks in the year line, as in EKAM-2c; they are flagged wherever
shown). Plus the fate of EKAM-2c's 8 open positions (matched on symbol,
signal date, entry date, entry price) under each row: still open (mark),
floor-exited (exit date, price, net), exited by another leg, or not
present in the row's book. Plus any entries signalled 2026-11-02 –
2026-11-13 under each row.

## 6. Standing

EKAM-2d arms nothing and replaces nothing. Adoption needs forward evidence
+ the owner's explicit word.
