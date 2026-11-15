#!/usr/bin/env python3
"""HOLD L35-H15 SHADOW SCORER — forward paper evidence for the
HOLD programme's found setting (set up 2026-11-15; the radio
rule: a found setting goes to the listening stage — forward
paper — before any adoption question).

WHAT THIS IS: a SCORE-ONLY paper shadow. It reads the frozen
25-name daily stores (data/sarvaritu_fwd/<SYM>/spot_daily.csv —
the same stores the research builds read; this scorer never
writes to them and makes NO API calls), updates the HOLD
L35-H15 position book by ONE completed day per run, and writes
its own ledger (hold_shadow_log.csv). It changes no running
book, no other ledger, and no job. Adoption is decided at the
Nov 30 verdicts on this forward evidence.

THE BOOK (frozen; hold_programme_SPEC.md +
hold_programme_r2_SPEC.md): equity cash, LONG only, frozen 25
names, daily candles. Signal at day t close: RSI(14) Wilder
crosses up through 35 (RSI[t-1] < 35 and RSI[t] >= 35, both
defined). Entry at day t+1's open. One open position per stock;
signals while holding are ignored; scanning resumes at the exit
day's close. Exit at the CLOSE of the 15th trading day after the
entry day (entry day = day 0). Rs40 per completed position, per
100 shares PROVISIONAL, paper only, real money Rs0.

WHY THIS SETTING (hold_programme_r2_2026-11-15.md): L35-H15 is
the local peak of its neighbourhood — Jan-Oct 2025 +Rs42,163
(83 trades, WR 63.9%) / 2026 +Rs83,963 (103 trades, WR 41.7%),
random-entry placebo 97.6th percentile; levels 30 and 40 and
holds 10 and 20 are all worse in at least one year.
Concentration is the standing weakness, recorded not hidden:
2025 ex-top-3 is negative and March 2026 (+Rs100,733) carries
the 2026 year. The Jan-Oct result is a tuning result, not
forward proof — this shadow is the proof stage.

SCORING MACHINERY: the research builds themselves, imported —
indicator_parameter_tuning_stocks_build (NAMES / COST /
load_daily / rsi_wilder) and hold_programme_r2_build.sim_r2
(the exact state machine that produced the published lines),
run per stock over the series capped at the run date. Nothing
is re-derived here. Positions are recomputed deterministically
each run from the stores (the sim is causal — signals use only
closes up to the signal day), so ageing, exits and marks are
always consistent with the data as it stands.

LEDGER (hold_shadow_log.csv): one row per position (keyed by
stock + entry date, updated in place as it ages: OPEN with the
mark at the latest close -> CLOSED at the day-15 close) plus
one DAY row per scored run summarising the day (entries, exits,
open count, signals for the next open, unscored stocks). Rows
for positions entered 2026-11-02..2026-11-13 are
BACKFILL_COUNTERFACTUAL (pre-shadow history, excluded from the
forward tally); positions entered on/after 2026-11-16 are LIVE.
The forward tally counts LIVE CLOSED + MARKED rows only.

REVIEW BOUND: 2026-11-30 (in force, enforced below). On the
2026-11-30 run, positions still open are marked at that close
and labelled MARKED — final for the review. Days after
2026-11-30 are refused: the Nov 30 verdicts decide the book's
future.

MISSING DATA: a stock whose store lacks the run date (or lacks
the store entirely) is UNSCORED for the day — named in the DAY
row's notes, its open positions keep their last mark, never
estimated, never substituted. A date absent from every store
scores as one UNSCORED day row.

DRY-RUN VERIFICATION (2026-11-15, --verify, writes nothing):
reproduces the R2 build's two November open positions EXACTLY —
BDL entered 2026-11-04 @1010.10, marked at the 2026-11-13 close
1030.00, net +Rs1,950.00; HINDCOPPER entered 2026-11-05
@432.00, marked 439.40, net +Rs700.00. --seed-backfill writes
those two rows (labelled BACKFILL_COUNTERFACTUAL) only after
the same reproduction passes.

Paper only, real money Rs0. No live orders.

Usage:
    python3 hold_shadow_score.py [--date YYYY-MM-DD]
                    [--dry-run] [--verify] [--seed-backfill]
Default date = today (IST). --dry-run computes and prints but
writes NOTHING. --verify is a hard-wired no-write check over
Nov 2-13 (series capped at 2026-11-13, bypasses the start /
window guards, never writes). --seed-backfill writes ONLY the
two Nov 2-13 BACKFILL_COUNTERFACTUAL position rows, and only
if the reproduction passes.
"""
import argparse, csv, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import indicator_parameter_tuning_stocks_build as ATLAS
import hold_programme_r2_build as R2

IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
BACKFILL_END = "2026-11-13"
WINDOW_START = "2026-11-02"
LEVEL, HOLD = 35, 15
COST = float(ATLAS.COST)    # 40.0 per completed position
LEDGER = TR / "hold_shadow_log.csv"
FIELDS = ["date", "row_type", "status", "sym", "signal_date",
          "entry_date", "entry_price", "exit_date", "exit_price",
          "exit_kind", "age_days", "mark_price", "net_inr",
          "fwd_running_total_inr", "notes"]
EXPECT = {  # R2 build's November open positions (Nov 2-13)
    "BDL": ("2026-11-04", 1010.10, 1030.00, 1950.00),
    "HINDCOPPER": ("2026-11-05", 432.00, 439.40, 700.00),
}
POS_STATUS = ("OPEN", "CLOSED", "MARKED")


# ---------------- data (capped) + the R2 state machine --------
def prep_capped(sym, cap):
    """ATLAS daily series truncated at `cap`, with the R2 L35
    signal array built exactly as hold_programme_r2_build.prep_r2
    builds it (RSI(14) Wilder cross up through 35)."""
    dates, o, h, l, c = ATLAS.load_daily(sym)
    dates = list(dates)
    keep = 0
    for i, dt in enumerate(dates):
        if dt <= cap:
            keep = i + 1
        else:
            break
    if keep == 0:
        return None
    dates = dates[:keep]
    o = np.asarray(o, dtype=float)[:keep]
    c = np.asarray(c, dtype=float)[:keep]
    r14 = ATLAS.rsi_wilder(c, 14)
    ok = ~np.isnan(r14)
    e = np.zeros(len(dates), dtype=bool)
    e[1:] = (ok[1:] & ok[:-1] & (r14[:-1] < float(LEVEL))
             & (r14[1:] >= float(LEVEL)))
    return dict(sym=sym, dates=dates, o=o, c=c, n=len(dates),
                sig_r2={LEVEL: e})


def compute(cap, marking_day=False):
    """Run the frozen sim per stock over bars <= cap. Returns
    (position_rows, stale_notes, pending_signals, present) where
    position_rows covers every position entered on/after
    WINDOW_START, stale_notes names stocks with no bar at `cap`,
    pending_signals lists (sym) with a signal at the cap close
    while free (entry at the next open), and present is True if
    at least one stock has a bar dated exactly `cap`."""
    rows, stale, signals = [], [], []
    present = False
    for sym in ATLAS.NAMES:
        try:
            d = prep_capped(sym, cap)
        except Exception:
            stale.append(f"{sym}(no_data_in_store)")
            continue
        if d is None:
            stale.append(f"{sym}(no_bars_up_to_{cap})")
            continue
        last = d["dates"][-1]
        if last == cap:
            present = True
        else:
            stale.append(f"{sym}(stale_last_{last})")
        trades = R2.sim_r2(d, LEVEL, HOLD)
        open_now = any(t["kind"] == "FORCED" for t in trades)
        last_i = d["n"] - 1
        for t in trades:
            if t["entry_date"] < WINDOW_START:
                continue
            ei = t["entry_idx"]
            entry = float(t["entry"])
            row = {k: "" for k in FIELDS}
            row["date"] = t["entry_date"]
            row["row_type"] = ("BACKFILL_COUNTERFACTUAL"
                               if t["entry_date"] <= BACKFILL_END
                               else "LIVE")
            row["sym"] = sym
            row["signal_date"] = d["dates"][ei - 1]
            row["entry_date"] = t["entry_date"]
            row["entry_price"] = f"{entry:.2f}"
            if t["kind"] == "HOLD":
                net = float(t["net"])
                row.update(
                    status="CLOSED", exit_date=t["exit_date"],
                    exit_price=f"{float(t['exit']):.2f}",
                    exit_kind="HOLD",
                    age_days=str(t["exit_idx"] - ei),
                    mark_price=f"{float(t['exit']):.2f}",
                    net_inr=f"{net:.2f}",
                    notes=("closed at the day-15 close; per 100 "
                           "shares provisional, Rs40/position"))
            elif marking_day:
                xp = float(d["c"][last_i])
                net = round((xp - entry) * 100.0 - COST, 2)
                row.update(
                    status="MARKED", exit_date=last,
                    exit_price=f"{xp:.2f}", exit_kind="MARKED",
                    age_days=str(last_i - ei),
                    mark_price=f"{xp:.2f}", net_inr=f"{net:.2f}",
                    notes=("still open at the 2026-11-30 review — "
                           "marked at that close, final for the "
                           "review; per 100 shares provisional, "
                           "Rs40/position"))
            else:
                xp = float(d["c"][last_i])
                net = round((xp - entry) * 100.0 - COST, 2)
                row.update(
                    status="OPEN", age_days=str(last_i - ei),
                    mark_price=f"{xp:.2f}", net_inr=f"{net:.2f}",
                    notes=(f"open — marked at the {last} close "
                           f"(unrealised); exit due at the close "
                           f"of day {HOLD} after entry; per 100 "
                           f"shares provisional, Rs40/position"))
            rows.append(row)
        if (not open_now and last == cap
                and bool(d["sig_r2"][LEVEL][last_i])):
            signals.append(sym)
    return rows, stale, signals, present


# ---------------- ledgers --------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def write_ledger(pos_rows, day_row):
    """Position rows are recomputed deterministically each run —
    replace all of them; replace the DAY/UNSCORED row for the
    run date, keep other days' rows; restamp the forward
    (LIVE CLOSED+MARKED only) running total in exit order."""
    rows = [r for r in ledger_rows() if r["status"] not in POS_STATUS]
    if day_row is not None:
        rows = [r for r in rows if r["date"] != day_row["date"]]
        rows.append(day_row)
    rows.extend(pos_rows)
    done = [r for r in rows
            if r["row_type"] == "LIVE" and r["status"] in ("CLOSED", "MARKED")]
    done.sort(key=lambda r: (r["exit_date"], r["sym"]))
    run = 0.0
    stamp = {}
    for r in done:
        run = round(run + float(r["net_inr"]), 2)
        stamp[(r["sym"], r["entry_date"])] = f"{run:.2f}"
    for r in rows:
        r["fwd_running_total_inr"] = stamp.get(
            (r["sym"], r["entry_date"]), "")
    rows.sort(key=lambda r: (r["date"], r["sym"], r["status"]))
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def tallies(rows):
    live_done = [r for r in rows if r["row_type"] == "LIVE"
                 and r["status"] in ("CLOSED", "MARKED")]
    live_open = [r for r in rows if r["row_type"] == "LIVE"
                 and r["status"] == "OPEN"]
    bf_done = [r for r in rows if r["row_type"] == "BACKFILL_COUNTERFACTUAL"
               and r["status"] in ("CLOSED", "MARKED")]
    bf_open = [r for r in rows if r["row_type"] == "BACKFILL_COUNTERFACTUAL"
               and r["status"] == "OPEN"]
    net = lambda rs: round(sum(float(r["net_inr"]) for r in rs), 2)
    return (len(live_done), net(live_done), len(live_open),
            len(bf_done), net(bf_done), len(bf_open))


# ---------------- verify / seed --------------------------------
def verify_or_seed(seed):
    rows, stale, signals, present = compute(BACKFILL_END)
    got = {}
    for r in rows:
        if r["status"] == "OPEN":
            got[r["sym"]] = (r["entry_date"], float(r["entry_price"]),
                             float(r["mark_price"]), float(r["net_inr"]))
    ok = (got == EXPECT and len(rows) == len(EXPECT))
    det = " · ".join(
        f"{s} in {v[0]} @{v[1]:.2f} marked {v[2]:.2f} "
        f"net {v[3]:+,.2f}" for s, v in sorted(got.items()))
    print(f"HOLD SHADOW VERIFY (Nov 2-13): positions={len(rows)} — "
          f"{det} vs R2 build BDL in 2026-11-04 @1010.10 marked "
          f"1030.00 net +1,950.00 · HINDCOPPER in 2026-11-05 "
          f"@432.00 marked 439.40 net +700.00 — "
          f"{'EXACT' if ok else 'MISMATCH'}")
    if not ok:
        print("VERIFY: MISMATCH — nothing written, do NOT schedule.")
        return 1
    print("VERIFY: EXACT REPRODUCTION of both November open "
          "positions and marks.")
    if seed:
        write_ledger(rows, None)
        print(f"Seeded hold_shadow_log.csv: {len(rows)} November "
              f"BACKFILL_COUNTERFACTUAL OPEN rows into "
              f"{LEDGER.name} (forward tally excludes them).")
    else:
        print("(--verify: nothing written.)")
    return 0


# ---------------- main ------------------------------------------
def day_summary(day, pos_rows, stale, signals):
    ent = [r for r in pos_rows if r["entry_date"] == day]
    ext = [r for r in pos_rows
           if r["status"] == "CLOSED" and r["exit_date"] == day]
    mrk = [r for r in pos_rows
           if r["status"] == "MARKED" and r["exit_date"] == day]
    opn = [r for r in pos_rows if r["status"] == "OPEN"]
    parts = []
    parts.append("entries: " + (
        ", ".join(f"{r['sym']} @{r['entry_price']}" for r in ent)
        if ent else "none"))
    parts.append("exits: " + (
        ", ".join(f"{r['sym']} {float(r['net_inr']):+,.2f}"
                  for r in ext) if ext else "none"))
    if mrk:
        parts.append("marked at review: " + ", ".join(
            f"{r['sym']} {float(r['net_inr']):+,.2f}" for r in mrk))
    parts.append(f"open: {len(opn)}" + (
        " (" + ", ".join(
            f"{r['sym']} age {r['age_days']} marked "
            f"{float(r['net_inr']):+,.2f}" for r in opn) + ")"
        if opn else ""))
    parts.append("signals for next open: "
                 + (", ".join(signals) if signals else "none"))
    if stale:
        parts.append("UNSCORED stocks (no bar today, never "
                     "estimated): " + ", ".join(stale))
    return "; ".join(parts)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check over Nov 2-13")
    ap.add_argument("--seed-backfill", action="store_true",
                    help="write ONLY the two Nov 2-13 "
                         "BACKFILL_COUNTERFACTUAL position rows, "
                         "and only if the reproduction passes")
    a = ap.parse_args(argv)
    if a.verify:
        return verify_or_seed(False)
    if a.seed_backfill:
        return verify_or_seed(True)
    day = a.date or datetime.now(IST).date().isoformat()
    if day > WINDOW_END:
        print(f"HOLD SHADOW: {day} is past the review bound "
              f"{WINDOW_END} (the Nov 30 verdicts) — scoring "
              f"closed; the HOLD L35-H15 shadow review is due, "
              f"do not score further days.")
        return 0
    if day < START:
        print(f"HOLD SHADOW: {day} is before the shadow start "
              f"{START} — nothing scored (the Nov 2-13 positions "
              f"live in the ledger as the labelled counterfactual "
              f"backfill).")
        return 0
    pos_rows, stale, signals, present = compute(
        day, marking_day=(day == WINDOW_END))
    if not present:
        row = {k: "" for k in FIELDS}
        row.update(date=day, row_type="LIVE", status="UNSCORED",
                   notes=("UNSCORED: date absent from every store "
                          "— never estimated; unscored stocks: "
                          + ", ".join(stale)))
        if not a.dry_run:
            keep = [r for r in ledger_rows()
                    if r["status"] in POS_STATUS]
            write_ledger(keep, row)
        print(f"HOLD SHADOW {day} (LIVE): UNSCORED — date absent "
              f"from every store, never estimated"
              + (" (DRY RUN — nothing written)" if a.dry_run else ""))
        return 0
    summary = day_summary(day, pos_rows, stale, signals)
    row = {k: "" for k in FIELDS}
    row.update(date=day, row_type="LIVE", status="DAY",
               notes=summary + "; per 100 shares provisional, "
                               "Rs40/position, paper")
    if not a.dry_run:
        write_ledger(pos_rows, row)
    print(f"HOLD SHADOW {day} (LIVE): {summary}"
          + (" (DRY RUN — nothing written)" if a.dry_run else ""))
    if not a.dry_run:
        ld, lnet, lo, bd, bnet, bo = tallies(ledger_rows())
        print(f"HOLD SHADOW tally: forward closed/marked={ld} "
              f"shadow_net={lnet:+.2f} · forward open={lo} · "
              f"(backfill closed/marked={bd} {bnet:+.2f}, open="
              f"{bo} — pre-shadow history, excluded) (per 100 "
              f"shares provisional, paper, real money Rs0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
