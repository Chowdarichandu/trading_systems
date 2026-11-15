#!/usr/bin/env python3
"""EKAM-INTRADAY STOCKS SHADOW SCORER — forward paper evidence for
the two standing EKAM-INTRADAY Stocks candidates (set up
2026-11-14; the books go to the listening stage after 7 tuning
rounds — every entry/selection/side/exit fix measured
window-unstable across years, placebo 100.0 everywhere — so what
decides them now is forward evidence, not another dial).

WHAT THIS IS: a SCORE-ONLY paper shadow. It reads the frozen
25-name intraday stores (data/sarvaritu_fwd/<SYM>/spot_5m.csv —
the same stores the research builds read; this scorer never
writes to them and makes NO API calls), scores ONE completed day
per run for BOTH rows, and writes its own two ledgers. It changes
no running book, no other ledger, and no job. Adoption of either
row is decided at the Nov 30 verdicts on this forward evidence.

THE TWO ROWS (frozen; definitions verbatim in
ekam_intraday_stocks_r2_build.py + ekam_intraday_stocks_r5_build.py):
EKAM-INTRADAY core: six standard indicators clubbed as votes on
completed 5-min bars — VWAP side (equal-weighted typical-price
proxy; the stores carry no volume), EMA(9) vs EMA(21),
Supertrend(7,3), MACD(12,26,9), RSI(14) zone, ADX(14) >= 20 to
the leading side. A stock's first bar of the day reaching >= 5
own-direction votes is its signal; entry = next bar's open; at
most 1 trade per stock per day. Exit stack (both rows): vote-
decay exit at own-direction votes <= 3, hard stop -1.00%, no
profit cap, square-off at the 15:10 bar's close (the builds'
frozen convention — the 15:10-labelled bar closes at 15:15).
Per 100 shares PROVISIONAL, Rs40/trade, equity cash intraday.
- CAND_T5 (the standing candidate): the day's candidate list
  (sorted by signal stamp, then symbol), earliest 5 taken.
  Jan-Oct: 2025 +Rs62,164.57 / 2026 +Rs63,883.60, placebo 100.0
  both years (ekam_intraday_stocks_r2_2026-11-14.md).
- S2 (the strongest thinned form): identical except earliest 3
  taken. Jan-Oct: 2025 +Rs45,300.64 / 2026 +Rs72,605.30, placebo
  100.0 both years; the first row in the family to clear a full
  year (2026, all five bar legs) — but worse than CAND_T5 in
  2025 (ekam_intraday_stocks_r5_2026-11-14.md).

SCORING MACHINERY: the research builds themselves, imported —
ekam_intraday_stocks_build (data, votes, day_candidates),
ekam_intraday_stocks_r2_build (net_of / the parameterised X2
exit — the authoritative net) and ekam_intraday_stocks_r5_build
(the two selectors + contexts_from). Nothing is re-derived here;
an annotated copy of the exit walk supplies exit time/reason for
the ledger and is asserted equal to net_of's exit price on every
scored trade.

MISSING DATA: a stock-day absent from its store, or present but
not tradable (no 15:10 bar / fewer than 30 bars), is UNSCORED
with the reason named in the day's rows — never estimated, never
substituted. A date absent from every store scores as one
UNSCORED day row per ledger. The forward tally counts LIVE rows
only; the Nov 2-13 rows are BACKFILL_COUNTERFACTUAL (pre-shadow
history, excluded from the tally).

REVIEW BOUND: days after 2026-11-30 are refused (the Nov 30
verdicts decide both rows' future), enforced the same way as the
premium-tape shadow scorer.

DRY-RUN VERIFICATION (2026-11-14, --verify, writes nothing):
reproduces the research builds' November lines EXACTLY —
CAND_T5 Nov 2-13 = 45 trades / +Rs24,528.65 and S2 Nov 2-13 =
27 trades / +Rs20,662.60. --seed-backfill writes those Nov 2-13
rows (labelled BACKFILL_COUNTERFACTUAL) only after the same
reproduction passes.

Paper only, real money Rs0. No live orders.

Usage:
    python3 ekam_intraday_shadow_score.py [--date YYYY-MM-DD]
                        [--dry-run] [--verify] [--seed-backfill]
Default date = today (IST). --dry-run computes and prints the
rows but writes NOTHING. --verify is a hard-wired no-write check
over Nov 2-13 (bypasses the start/window guards, never writes).
--seed-backfill writes ONLY the Nov 2-13 BACKFILL_COUNTERFACTUAL
rows, and only if the reproduction passes.
"""
import argparse, csv, math, os, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

IST = ZoneInfo("Asia/Kolkata")
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
CAND = dict(D=3, S=0.0100, C=None)   # CAND-T5 exit params (R5, frozen)
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
EXPECT = {"CAND_T5": (45, 24528.65), "S2": (27, 20662.60)}

LEDGERS = {"CAND_T5": TR / "november_shadow_ekam_t5_stocks_log.csv",
           "S2": TR / "november_shadow_ekam_s2_stocks_log.csv"}
SELECTORS = {"CAND_T5": r5.sel_s0, "S2": r5.sel_s2}
FIELDS = ["date", "row_type", "book", "status", "sym", "side",
          "votes", "signal_time", "entry_time", "entry_price",
          "exit_time", "exit_price", "exit_reason", "net_inr",
          "fwd_running_total_inr", "notes"]

_stocks = None
_by_sym = None


def stocks():
    global _stocks, _by_sym
    if _stocks is None:
        _stocks = [r1.build_stock(s) for s in r1.NAMES]
        _by_sym = {S["sym"]: S for S in _stocks}
    return _stocks, _by_sym


# ---------------- annotated exit walk (r2.exit_x2p verbatim + labels)
def exit_annotated(o, h, l, c, entry_li, sq_li, E, side, own_votes,
                   D, S, C):
    """r2.exit_x2p with the exit bar index and a reason label added
    at its own return points — identical branch order, identical
    fills. Returns (exit_price, exit_bar_index, reason)."""
    if side == 1:
        stp = E * (1.0 - S); tgt = E * (1.0 + C) if C is not None else None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj <= stp: return oj, j, "gap_stop"
            if tgt is not None and oj >= tgt: return oj, j, "gap_cap"
            if lj <= stp: return stp, j, "stop"
            if tgt is not None and hj >= tgt: return tgt, j, "cap"
            v = own_votes[j]
            if v is not None and not (isinstance(v, float)
                                      and math.isnan(v)) and v <= D:
                return c[j], j, "decay"
    else:
        stp = E * (1.0 + S); tgt = E * (1.0 - C) if C is not None else None
        for j in range(entry_li, sq_li + 1):
            oj, hj, lj = o[j], h[j], l[j]
            if oj >= stp: return oj, j, "gap_stop"
            if tgt is not None and oj <= tgt: return oj, j, "gap_cap"
            if hj >= stp: return stp, j, "stop"
            if tgt is not None and lj <= tgt: return tgt, j, "cap"
            v = own_votes[j]
            if v is not None and not (isinstance(v, float)
                                      and math.isnan(v)) and v <= D:
                return c[j], j, "decay"
    return c[sq_li], sq_li, "squareoff"


# ---------------- one day, both books ------------------------------
def score_day(day, row_type):
    """Returns {book: [ledger rows]} for the day. Coverage is
    assessed per stock-day; unscored stock-days are named (with
    reasons) in the notes of every row written for the day."""
    S_all, by_sym = stocks()
    unscored = []
    cands = []
    for S in S_all:
        if day not in S["days"]:
            unscored.append(f"{S['sym']}(no_data_in_store)")
            continue
        if not S["days"][day]["tradable"]:
            unscored.append(f"{S['sym']}(incomplete_day)")
            continue
        cd = r1.day_candidates(S, day, 5)
        if cd:
            cands.append(cd)
    cands.sort(key=lambda x: (x["signal_stamp"], x["sym"]))
    scored_n = 25 - len(unscored)
    cov = (f"coverage {scored_n}/25 stock-days scored"
           + (f"; UNSCORED stock-days: {', '.join(unscored)}"
              if unscored else ""))
    out = {}
    for book in ("CAND_T5", "S2"):
        rows = []
        if scored_n == 0:
            row = {k: "" for k in FIELDS}
            row.update(date=day, row_type=row_type, book=book,
                       status="UNSCORED", notes=(
                           "UNSCORED: date absent from every store — "
                           "never estimated; " + cov))
            out[book] = rows + [row]
            continue
        ctxs = r5.contexts_from({day: cands}, by_sym, SELECTORS[book])
        if not ctxs:
            row = {k: "" for k in FIELDS}
            row.update(date=day, row_type=row_type, book=book,
                       status="NO_TRADE",
                       notes="no selected candidate today; " + cov)
            out[book] = rows + [row]
            continue
        for ctx in ctxs:
            Dd = by_sym[ctx["sym"]]["days"][day]
            net = r2.net_of(ctx, **CAND)
            xp, xj, xreason = exit_annotated(
                ctx["o"], ctx["h"], ctx["l"], ctx["c"],
                ctx["entry_li"], ctx["sq_li"], ctx["E"], ctx["side"],
                ctx["own"], CAND["D"], CAND["S"], CAND["C"])
            ref = r2.exit_x2p(ctx["o"], ctx["h"], ctx["l"], ctx["c"],
                              ctx["entry_li"], ctx["sq_li"], ctx["E"],
                              ctx["side"], ctx["own"], CAND["D"],
                              CAND["S"], CAND["C"])
            assert abs(xp - ref) < 1e-9, "annotated exit != net_of exit"
            row = {k: "" for k in FIELDS}
            row.update(
                date=day, row_type=row_type, book=book,
                status="TRADED", sym=ctx["sym"],
                side="LONG" if ctx["side"] == 1 else "SHORT",
                votes=str(ctx["votes"]),
                signal_time=ctx["signal_stamp"],
                entry_time=ctx["entry_stamp"],
                entry_price=f"{ctx['E']:.2f}",
                exit_time=Dd["st"][xj], exit_price=f"{xp:.2f}",
                exit_reason=xreason, net_inr=f"{net:.2f}",
                notes=("per 100 shares provisional, Rs40/trade; "
                       + cov))
            rows.append(row)
        out[book] = rows
    return out


# ---------------- ledgers ------------------------------------------
def ledger_rows(path):
    if not path.exists():
        return []
    with open(path) as f:
        return list(csv.DictReader(f))


def write_book_rows(book, new_rows):
    """Replace this date's rows in the book's ledger, restamp the
    forward (LIVE-only) running total in date order, rewrite."""
    path = LEDGERS[book]
    dates = {r["date"] for r in new_rows}
    rows = [r for r in ledger_rows(path) if r["date"] not in dates]
    rows.extend(new_rows)
    rows.sort(key=lambda r: (r["date"],
                             r["entry_time"] or "99:99",
                             r["sym"]))
    run = 0.0
    for r in rows:
        if r["row_type"] == "LIVE" and r["status"] == "TRADED":
            run = round(run + float(r["net_inr"]), 2)
            r["fwd_running_total_inr"] = f"{run:.2f}"
        else:
            r["fwd_running_total_inr"] = ""
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)


def tallies(book):
    rows = ledger_rows(LEDGERS[book])
    fwd = [r for r in rows if r["row_type"] == "LIVE"
           and r["status"] == "TRADED"]
    bf = [r for r in rows if r["row_type"] == "BACKFILL_COUNTERFACTUAL"
          and r["status"] == "TRADED"]
    fnet = round(sum(float(r["net_inr"]) for r in fwd), 2)
    bnet = round(sum(float(r["net_inr"]) for r in bf), 2)
    return len(fwd), fnet, len(bf), bnet


# ---------------- verify / seed ------------------------------------
def _nov_totals():
    per_book = {}
    all_rows = {}
    for day in NOV_DAYS:
        day_rows = score_day(day, "BACKFILL_COUNTERFACTUAL")
        for book, rows in day_rows.items():
            all_rows.setdefault(book, []).extend(rows)
    for book, rows in all_rows.items():
        traded = [r for r in rows if r["status"] == "TRADED"]
        total = round(sum(float(r["net_inr"]) for r in traded), 2)
        per_book[book] = (len(traded), total)
    return per_book, all_rows


def verify_or_seed(seed):
    per_book, all_rows = _nov_totals()
    ok = True
    for book in ("CAND_T5", "S2"):
        n, tot = per_book[book]
        en, etot = EXPECT[book]
        match = (n == en and tot == etot)
        ok = ok and match
        print(f"EKAM-INTRADAY SHADOW VERIFY {book} (Nov 2-13): "
              f"trades={n} total={tot:+.2f} vs research builds "
              f"{en} trades / {etot:+.2f} — "
              f"{'EXACT' if match else 'MISMATCH'}")
    if not ok:
        print("VERIFY: MISMATCH — nothing written, do NOT schedule.")
        return 1
    print("VERIFY: EXACT REPRODUCTION of both November lines.")
    if seed:
        for book in ("CAND_T5", "S2"):
            write_book_rows(book, all_rows[book])
            n, tot = per_book[book]
            print(f"Seeded {book}: Nov 2-13 BACKFILL_COUNTERFACTUAL "
                  f"rows into {LEDGERS[book].name} "
                  f"({n} trades, {tot:+.2f}).")
    else:
        print("(--verify: nothing written.)")
    return 0


# ---------------- main ---------------------------------------------
def fmt_day(book, day, rows, row_type):
    traded = [r for r in rows if r["status"] == "TRADED"]
    if traded:
        tot = round(sum(float(r["net_inr"]) for r in traded), 2)
        legs = " · ".join(
            f"{r['sym']} {r['side']} sig {r['signal_time']} "
            f"ent {r['entry_time']}@{r['entry_price']} "
            f"exit {r['exit_reason']} {float(r['net_inr']):+,.2f}"
            for r in traded)
        return (f"EKAM-INTRADAY SHADOW {book} {day} ({row_type}): "
                f"{len(traded)} trades, day net {tot:+,.2f} — {legs}")
    r = rows[0]
    return (f"EKAM-INTRADAY SHADOW {book} {day} ({row_type}): "
            f"{r['status']} — {r['notes']}")


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check over Nov 2-13")
    ap.add_argument("--seed-backfill", action="store_true",
                    help="write ONLY the Nov 2-13 "
                         "BACKFILL_COUNTERFACTUAL rows, and only "
                         "if the reproduction passes")
    a = ap.parse_args(argv)
    if a.verify:
        return verify_or_seed(False)
    if a.seed_backfill:
        return verify_or_seed(True)
    day = a.date or datetime.now(IST).date().isoformat()
    if day > WINDOW_END:
        print(f"EKAM-INTRADAY SHADOW: {day} is past the review bound "
              f"{WINDOW_END} (the Nov 30 verdicts) — scoring closed; "
              f"the CAND_T5 / S2 review is due, do not score further "
              f"days.")
        return 0
    if day < START:
        print(f"EKAM-INTRADAY SHADOW: {day} is before the shadow "
              f"start {START} — nothing scored (Nov 2-13 live in the "
              f"ledgers as the labelled counterfactual backfill).")
        return 0
    day_rows = score_day(day, "LIVE")
    for book in ("CAND_T5", "S2"):
        rows = day_rows[book]
        if not a.dry_run:
            write_book_rows(book, rows)
        print(fmt_day(book, day, rows, "LIVE")
              + (" (DRY RUN — nothing written)" if a.dry_run else ""))
        if not a.dry_run:
            fn, fnet, bn, bnet = tallies(book)
            print(f"EKAM-INTRADAY SHADOW {book} tally: forward "
                  f"traded={fn} shadow_net={fnet:+.2f} (backfill "
                  f"{bn} trades {bnet:+.2f}, pre-shadow history, "
                  f"excluded) (per 100 shares provisional, paper, "
                  f"real money Rs0)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
