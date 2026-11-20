#!/usr/bin/env python3
"""D1 COMBINED-REPAIR SHADOW SCORER — Bank Nifty (from Mon 2026-11-16).

Forward paper evidence for BANK-FIX dial D1 (bank_fix_SPEC.md, frozen
2026-11-16; run record bank_fix_2026-11-16.md): TUNED STACK v2 kept
only if it survives BOTH proven repairs — (a) not the B-FIX-1 cell
(side = PE AND gap% < 0 AND entry premium in [Rs500, Rs800]), AND
(b) composite confidence score >= 0.5.

JAN-OCT GATE (full factors F1-F6, phase2 score_leg verbatim):
GATE PASS — kept 71/111 legs, +Rs126,496.00, WR 69.0%,
Rs1,976.50/trade-day, halves +77,845 / +48,651, ex-top-3
+Rs99,673.00, no red month, placebo 100th percentile (p95
+Rs100,828.45). The two filters bite DISJOINT leg sets on Jan-Oct
(the 17 B-FIX-1 cell legs all score >= 0.5; the 23 confidence-idled
legs are all outside the cell), so the combination is exactly
additive: 127,351.50 + 4,158.50 - 5,014.00 = 126,496.00. Against
the parents: total is Rs5,014 BELOW B-FIX-1 alone (+Rs131,510) but
Rs/trade-day (1,976.50 vs 1,686.03) and WR (69.0% vs 63.8%) are
both HIGHER — not dominated, so D1 stands as a December candidate
on this forward evidence, decided at the Nov 30 verdicts.

FORWARD BASIS CAVEAT (the same one the confidence-gate shadow
carries, stated wherever these numbers are used): the Jan-Oct gate
scored the FULL six factors. The November shadow log does not
carry `agree` (F1) or a per-leg second flag (F5/F6), so this
forward scorer scores F2+F3+F4 only, with F1/F5/F6 at their
neutral 0 — exactly the phase-2 November basis that
bank_confgate_shadow_score.py implements (its score_factors and
tod_of are reused verbatim here). The forward record is therefore
on the November basis, NOT the full-factor basis; the two are
never mixed in one number.

This scorer is SCORE-ONLY: it reads the stack's own ledger
(november_shadow_stack_bank_log.csv, written by the existing
chain, NEVER modified here), applies both filters, and writes its
own ledger (november_shadow_d1_bank_log.csv). It changes no
running book, no other ledger, and no job. If the day's gap
cannot be established, legs are UNSCORED — never estimated.

REVIEW BOUND: days after 2026-11-30 are refused (the Nov 30
verdicts decide D1's future).

Paper only, real money Rs0. Buying only. No API calls.

Usage:
    python3 bank_d1_shadow_score.py [--date YYYY-MM-DD]
                                    [--backfill] [--verify]
"""
import argparse, csv, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import bank_confgate_shadow_score as CG   # tod_of, score_factors, gap_pct

IST = ZoneInfo("Asia/Kolkata")
STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
LEDGER = TR / "november_shadow_d1_bank_log.csv"
CUT = 0.5
START = "2026-11-16"
WINDOW_END = "2026-11-30"
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
FIELDS = ["date", "row_type", "family", "rep", "direction", "strike",
          "expiry", "entry_time", "entry_premium", "exit_time",
          "exit_premium", "exit_reason", "stack_net_inr", "gap_pct",
          "gap_source", "bfix1_cell", "score_nov_basis", "decision",
          "kept_net_inr", "kept_running_total_inr", "notes"]
NOTE_BASIS = ("November factor basis: F2+F3+F4 scored, F1/F5/F6 "
              "neutral 0 (agree / second flags not carried in the "
              "November shadow log) — the phase-2 November basis")


def _t2m(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def stack_legs(day):
    out = []
    if not STACK_LOG.exists():
        return out
    for r in csv.DictReader(open(STACK_LOG)):
        if r["date"] == day and r.get("entry_premium"):
            out.append(r)
    return out


def score_day(day, row_type):
    rows = []
    g, gsrc = CG.gap_pct(day)
    for r in stack_legs(day):
        row = {k: "" for k in FIELDS}
        row.update(date=day, row_type=row_type, family=r["family"],
                   rep=r["rep"], direction=r["direction"],
                   strike=r["strike"], expiry=r["expiry"],
                   entry_time=r["entry_time"],
                   entry_premium=r["entry_premium"],
                   exit_time=r["exit_time"],
                   exit_premium=r["exit_premium"],
                   exit_reason=r["exit_reason"],
                   stack_net_inr=f"{float(r['net_inr']):.2f}")
        if g is None:
            row.update(decision="UNSCORED",
                       notes="UNSCORED: overnight gap not establishable "
                             "from the regime file or the stored spot; "
                             "neither filter can be applied — never "
                             "estimated")
            rows.append(row)
            continue
        prem = float(r["entry_premium"])
        cell = (r["direction"] == "PE" and g < 0 and 500.0 <= prem <= 800.0)
        f = CG.score_factors(r["direction"], prem, CG.tod_of(r["entry_time"]), g)
        score = f[6]
        if cell:
            decision = "IDLED_BFIX1"
        elif score < CUT:
            decision = "IDLED_CONFGATE"
        else:
            decision = "KEPT"
        row.update(gap_pct=f"{g:.4f}", gap_source=gsrc,
                   bfix1_cell="YES" if cell else "NO",
                   score_nov_basis=f"{score:.2f}", decision=decision,
                   kept_net_inr=(f"{float(r['net_inr']):.2f}"
                                 if decision == "KEPT" else "0.00"),
                   notes=NOTE_BASIS)
        rows.append(row)
    return rows


def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def _key(r):
    return (r["date"], r["entry_time"], r["entry_premium"])


def upsert(rows):
    new_keys = {_key(r) for r in rows}
    kept_rows = [r for r in ledger_rows() if _key(r) not in new_keys]
    all_rows = kept_rows + rows
    all_rows.sort(key=lambda r: (r["date"], _t2m(r["entry_time"]),
                                 float(r["entry_premium"])))
    run = 0.0
    for r in all_rows:
        if r["decision"] == "KEPT":
            run = round(run + float(r["kept_net_inr"]), 2)
        r["kept_running_total_inr"] = f"{run:.2f}"
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)


def totals(rows):
    kept = [r for r in rows if r["decision"] == "KEPT"]
    return (len(kept),
            round(sum(float(r["kept_net_inr"]) for r in kept), 2))


def fmt_day(day, rows, row_type):
    if not rows:
        return (f"D1 SHADOW {day} ({row_type}): no stack legs today — "
                f"nothing to filter; kept-set totals unchanged")
    parts = []
    for r in rows:
        if r["decision"] == "UNSCORED":
            parts.append(f"UNSCORED {r['direction']} {r['strike']} "
                         f"@{r['entry_premium']} (gap unavailable)")
        else:
            parts.append(
                f"{r['decision']} {r['direction']} {r['strike']} "
                f"@{r['entry_premium']} (B-FIX-1 cell {r['bfix1_cell']}, "
                f"score {r['score_nov_basis']}) net "
                f"{float(r['stack_net_inr']):+,.2f}")
    return f"D1 SHADOW {day} ({row_type}): " + " · ".join(parts)


def print_tallies():
    rows = ledger_rows()
    for label, sel in (("full November (incl. Nov 2-13 counterfactual "
                        "backfill)", lambda r: True),
                       ("LIVE forward rows only (from 2026-11-16)",
                        lambda r: r["row_type"] == "LIVE")):
        sub = [r for r in rows if sel(r)]
        n, tot = totals(sub)
        stack_tot = round(sum(float(r["stack_net_inr"]) for r in sub), 2)
        print(f"D1 kept-set — {label}: kept {n} legs, kept-set total "
              f"{tot:+,.2f} (stack legs on those rows {stack_tot:+,.2f}). "
              f"Paper only, real money Rs0.")


VERIFY_EXPECT = {  # date -> decision on the November basis
    "2026-11-04": "IDLED_BFIX1",    # the +2,480 win is in the B-FIX-1 cell
    "2026-11-09": "IDLED_CONFGATE",  # score -0.50
    "2026-11-12": "IDLED_CONFGATE",  # score 0.00
    "2026-11-13": "IDLED_BFIX1",    # score 0.50 passes, cell drops it
}


def verify():
    got = {}
    stack_tot = 0.0
    for day in NOV_DAYS:
        for row in score_day(day, "VERIFY"):
            got[row["date"]] = row
            stack_tot = round(stack_tot + float(row["stack_net_inr"]), 2)
    ok = True
    for day, ed in VERIFY_EXPECT.items():
        r = got.get(day)
        if r is None:
            print(f"VERIFY {day}: MISSING leg row")
            ok = False
            continue
        match = r["decision"] == ed
        ok = ok and match
        print(f"VERIFY {day}: {r['rep']} {r['direction']} {r['strike']} "
              f"@{r['entry_premium']} cell {r['bfix1_cell']} score "
              f"{r['score_nov_basis']} decision {r['decision']} "
              f"(expect {ed}) net {float(r['stack_net_inr']):+,.2f} "
              f"{'MATCH' if match else 'MISMATCH'}")
    kept_rows = [r for r in got.values() if r["decision"] == "KEPT"]
    kept_tot = round(sum(float(r["kept_net_inr"]) for r in kept_rows), 2)
    print(f"VERIFY kept-set November total: {kept_tot:+,.2f} "
          f"(expect +0.00 — D1 idles all four November legs) · stack "
          f"total: {stack_tot:+,.2f} (expect -2,680.00)")
    ok = ok and kept_tot == 0.00 and stack_tot == -2680.00
    print("VERIFY: " + ("EXACT — safe to schedule."
                        if ok else "MISMATCH — do NOT schedule."))
    return 0 if ok else 3


def backfill():
    all_rows = []
    for day in NOV_DAYS:
        rows = score_day(day, "BACKFILL_COUNTERFACTUAL")
        all_rows.extend(rows)
        print(fmt_day(day, rows, "BACKFILL_COUNTERFACTUAL"))
    upsert(all_rows)
    stack_tot = round(sum(float(r["stack_net_inr"]) for r in all_rows), 2)
    _, kept_tot = totals(all_rows)
    assert stack_tot == -2680.00, stack_tot
    assert kept_tot == 0.00, kept_tot
    print(f"BACKFILL Nov 2-13 written: stack {stack_tot:+,.2f} -> D1 "
          f"kept-set {kept_tot:+,.2f} (counterfactual rows, labelled "
          f"as such; Nov 16 contributes no row — the stack took no "
          f"leg that day).")
    print_tallies()
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--verify", action="store_true")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.backfill:
        return backfill()
    day = a.date or datetime.now(IST).date().isoformat()
    if day > WINDOW_END:
        print(f"D1 SHADOW {day}: November window closed 2026-11-30 — "
              f"D1's fate is decided at the Nov 30 verdicts / December "
              f"adoption. No row written.")
        return 0
    if day < START:
        print(f"D1 SHADOW: {day} is before the shadow start {START} — "
              f"nothing scored (Nov 2-13 live in the ledger as the "
              f"labelled counterfactual backfill).")
        return 0
    rows = score_day(day, "LIVE")
    if rows:
        upsert(rows)
    print(fmt_day(day, rows, "LIVE"))
    print_tallies()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
