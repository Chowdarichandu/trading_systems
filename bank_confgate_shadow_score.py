#!/usr/bin/env python3
"""CONFIDENCE-GATE SHADOW SCORER — Bank Nifty (from Mon 2026-11-16).

Forward paper evidence for the Phase-2 confidence gate on TUNED
STACK v2 (owner-ordered tuning 2026-11-14 08:54 IST; frozen spec
phase2_tuning_bank_SPEC.md; run record phase2_tuning_bank_2026-11-14.md
+ phase2_tuning_bank_results.json).

THE GATE THAT PASSED (Jan-Oct, pre-registered bars, all seven legs):
composite confidence score >= 0.5 on stack legs — kept 88/111 legs,
+Rs122,337.50, WR 62.5%, Rs1,609.70/trade-day, both halves positive,
ex-top-3 +Rs95,514.50, no red month, placebo 97th percentile.
The >= 1.0 cut FAILED its placebo leg and is NOT implemented here
or anywhere. This scorer is SCORE-ONLY: it reads the stack's own
ledger (november_shadow_stack_bank_log.csv, written by the existing
chain, NEVER modified here), scores each leg, and writes its own
ledger (november_shadow_confgate_bank_log.csv). It changes no
running book, no other ledger, and no job. December adoption is
decided at the Nov 30 verdicts on this forward evidence.

COMPOSITE SCORE — replicated EXACTLY from phase2_tuning_bank_build.py
(score_leg + its November counterfactual block). Entry-bar-knowable
factors, weights frozen in the spec:
- F1 agree: >=2 -> +1.0, =1 -> +0.5, =0 -> 0.
- F2 premium ratio r = entry_premium / 692.50 (book median, a fixed
  constant of the gated store): r<0.75 -> +1.0, <1.0 -> +0.5,
  <1.45 -> 0, else -0.5.
- F3 entry-time bucket (tod): early +0.5, mid 0, late -0.5. The tod
  of an entry time is resolved with the build's own tod_of(): the
  map is rebuilt here from the gated Jan-Oct store (solid60 features
  joined to the books-fix anatomy legs, exactly as the build built
  it); an unseen time takes the tod of the latest known entry time
  at or before it (else the earliest known).
- F4 gap alignment (gap_pct vs side): aligned & |gap|>=0.30% ->
  +0.5; aligned & 0.05%<=|gap|<0.30% -> +0.25; |gap|<0.05% -> 0;
  against side -> -0.5. Gap source, in order: the frozen November
  regime-classification file (november_regime_days_bank.csv — the
  phase-2 run's own source), then the persisted progressive spot
  file (today's 09:15 open vs the previous in-store weekday's last
  close — the B-FIX-1 scorer's derivation; on Nov 2-13 the two
  agree to float noise, ~1e-12). The source used is recorded per
  row. If no gap can be established either way the leg is UNSCORED
  with the reason — never estimated.
- F5 second-leg flag: +0.5 if the leg is a second leg.
- F6 anchor outcome (second legs only): +0.5 / -0.5 by the anchor
  leg's net, 0 when unresolvable.

NOVEMBER FACTOR AVAILABILITY (the phase-2 run's own handling,
replicated factor-by-factor — this is the November basis, not an
approximation of the Jan-Oct basis):
- F1: `agree` is NOT carried in the November shadow stack log.
  The run set F1 to its neutral 0 for every November leg. Same here.
- F5/F6: the shadow log carries no per-leg `second` flag, and the
  run's November block set second=0 (so F5=0) and f6=0.0 for every
  November leg — including the S3-R1 re-entry and NS3 second-leg
  families. Same here: November legs are scored on F2+F3+F4 only,
  exactly as the counterfactual scored them.
- F2/F3/F4 are fully computable from the shadow log + gap file.

CUT: score >= 0.5 -> KEPT; below -> IDLED (the gate stays idle,
per the owner's principle: idle beats a marginal trade).

DRY-RUN VERIFICATION (2026-11-14, --verify, writes nothing):
reproduces the phase-2 November counterfactual to the paisa —
scores Nov 4 = 0.75, Nov 9 = -0.50, Nov 12 = 0.00, Nov 13 = 0.50;
KEPT Nov 4 (+Rs2,480.00) and Nov 13 (-Rs1,720.00); IDLED Nov 9 and
Nov 12 (both -Rs1,720.00); kept-set November total +Rs760.00 vs the
stack's -Rs2,680.00. --backfill writes those Nov 2-13 rows labelled
BACKFILL_COUNTERFACTUAL (they are a counterfactual, never part of
the live forward record).

REVIEW BOUND: days after 2026-11-30 are refused (the Nov 30
verdicts decide the gate's future), same guard style as the
REGIME-REV and B-FIX-1 scorers.

Paper only, real money Rs0. Buying only. No API calls — this
scorer reads stored ledgers/files only.

Usage:
    python3 bank_confgate_shadow_score.py [--date YYYY-MM-DD]
                                          [--backfill] [--verify]
"""
import argparse, csv, sys
from datetime import date as ddate, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
LEDGER = TR / "november_shadow_confgate_bank_log.csv"
REGIME = TR / "november_regime_days_bank.csv"
SPOT = TR / "data/progressive/BANKNIFTY/spot_5m.csv"
FEATURES = TR / "solid60_programme_2026-11-13_bank_A_stack_features.csv"
ANATOMY = TR / "november_books_fix_anatomy_legs.csv"
CUT = 0.5
MEDIAN_PREM = 692.50
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
FIELDS = ["date", "row_type", "family", "rep", "direction", "strike",
          "expiry", "entry_time", "entry_premium", "exit_time",
          "exit_premium", "exit_reason", "stack_net_inr", "gap_pct",
          "gap_source", "tod", "f1_agree", "f2_premium", "f3_tod",
          "f4_gap", "f5_second", "f6_anchor", "score", "decision",
          "kept_net_inr", "kept_running_total_inr", "notes"]


def _t2m(t):
    h, m = t.split(":")
    return int(h) * 60 + int(m)


# ---------------- tod map (the build's own construction) -------------
_tod_by_time = None


def tod_by_time():
    """entry_time -> tod, rebuilt exactly as phase2_tuning_bank_build.py
    built it: the gated Jan-Oct legs (solid60 features joined to the
    books-fix anatomy store on (date, entry_time, entry_premium)),
    iterated in entry-time order, first occurrence wins."""
    global _tod_by_time
    if _tod_by_time is not None:
        return _tod_by_time
    feat = {}
    for r in csv.DictReader(open(FEATURES)):
        feat[(r["date"], r["entry_time"],
              float(r["entry_premium"]))] = r
    legs = []
    for r in csv.DictReader(open(ANATOMY)):
        if r["book"] != "BANK_STACK":
            continue
        k = (r["date"], r["entry_time"], float(r["entry_premium"]))
        legs.append((r["entry_time"], feat[k]["tod"]))
    m = {}
    for t, tod in sorted(legs, key=lambda x: _t2m(x[0])):
        m.setdefault(t, tod)
    _tod_by_time = m
    return m


def tod_of(t):
    """The build's tod_of(), verbatim."""
    m = tod_by_time()
    if t in m:
        return m[t]
    mt = _t2m(t)
    known = sorted((_t2m(k), v) for k, v in m.items())
    prev = [v for kt, v in known if kt <= mt]
    return prev[-1] if prev else known[0][1]


# ---------------- gap (phase-2 source first, then the B-FIX-1 derivation)
def gap_pct(day):
    """(gap_pct, source) or (None, None). Primary: the frozen regime
    file — the phase-2 run's own source. Fallback: the progressive
    spot derivation used by bank_bfix1_score.py (identical formula;
    on Nov 2-13 the two agree to ~1e-12). Never estimated."""
    if REGIME.exists():
        for r in csv.DictReader(open(REGIME)):
            if r["date"] == day and r["gap_pct"]:
                return float(r["gap_pct"]), "regime_file"
    if SPOT.exists():
        days = {}
        for r in csv.DictReader(open(SPOT)):
            days.setdefault(r["timestamp"][:10], []).append(r)
        if day in days:
            prev = [d for d in sorted(days) if d < day
                    and ddate.fromisoformat(d).weekday() <= 4]
            if prev:
                prev = prev[-1]
                g = (float(days[day][0]["open"])
                     / float(days[prev][-1]["close"]) - 1.0) * 100.0
                return g, "progressive_spot"
    return None, None


# ---------------- composite score (the build's score_leg, verbatim) --
def score_factors(side, premium, tod, gap):
    """Returns (f1, f2, f3, f4, f5, f6, total) on the November basis:
    agree=0 and second=0 and f6=0.0 — the phase-2 run's November
    handling (see header). Factor expressions are the build's,
    verbatim."""
    agree, second, f6 = 0, 0, 0.0
    f1 = 1.0 if agree >= 2 else (0.5 if agree == 1 else 0.0)
    r = premium / MEDIAN_PREM
    f2 = 1.0 if r < 0.75 else (0.5 if r < 1.0 else
                              (0.0 if r < 1.45 else -0.5))
    f3 = {"early": 0.5, "mid": 0.0, "late": -0.5}[tod]
    aligned = (side == "CE" and gap > 0) or (side == "PE" and gap < 0)
    against = (side == "CE" and gap < 0) or (side == "PE" and gap > 0)
    ag = abs(gap)
    f4 = 0.0 if ag < 0.05 else (0.5 if (aligned and ag >= 0.30) else
                                (0.25 if aligned else
                                 -0.5 if against else 0.0))
    f5 = 0.5 if second == 1 else 0.0
    return f1, f2, f3, f4, f5, f6, f1 + f2 + f3 + f4 + f5 + f6


# ---------------- stack legs ------------------------------------------
def stack_legs(day):
    """The day's stack legs from the stack's own ledger — rows with a
    non-empty entry_premium, exactly the phase-2 build's filter."""
    out = []
    if not STACK_LOG.exists():
        return out
    for r in csv.DictReader(open(STACK_LOG)):
        if r["date"] == day and r.get("entry_premium"):
            out.append(r)
    return out


def score_day(day, row_type):
    rows = []
    g, gsrc = gap_pct(day)
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
                   stack_net_inr=f"{float(r['net_inr']):.2f}",
                   tod=tod_of(r["entry_time"]))
        if g is None:
            row.update(decision="UNSCORED",
                       notes="UNSCORED: overnight gap not establishable "
                             "from the regime file or the stored spot; "
                             "score not computed on the phase-2 basis — "
                             "never estimated")
            rows.append(row)
            continue
        f1, f2, f3, f4, f5, f6, total = score_factors(
            r["direction"], float(r["entry_premium"]), row["tod"], g)
        kept = total >= CUT
        row.update(gap_pct=f"{g:.4f}", gap_source=gsrc,
                   f1_agree=f"{f1:.2f}", f2_premium=f"{f2:.2f}",
                   f3_tod=f"{f3:.2f}", f4_gap=f"{f4:.2f}",
                   f5_second=f"{f5:.2f}", f6_anchor=f"{f6:.2f}",
                   score=f"{total:.2f}",
                   decision="KEPT" if kept else "IDLED",
                   kept_net_inr=(f"{float(r['net_inr']):.2f}"
                                 if kept else "0.00"),
                   notes=("F1 neutral 0 (agree not carried in the "
                          "November shadow log); F5/F6 neutral 0 "
                          "(no per-leg second flag in the shadow log) "
                          "— the phase-2 November basis"))
        rows.append(row)
    return rows


# ---------------- ledger ----------------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def _key(r):
    return (r["date"], r["entry_time"], r["entry_premium"])


def upsert(rows):
    """Replace the rows for (date, entry_time, entry_premium) keys,
    restamp the kept-set running November total across the whole
    ledger in (date, entry_time) order, rewrite the file."""
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
        return (f"CONF-GATE SHADOW {day} ({row_type}): no stack legs "
                f"today — nothing to gate; kept-set totals unchanged")
    parts = []
    for r in rows:
        if r["decision"] == "UNSCORED":
            parts.append(f"UNSCORED {r['direction']} {r['strike']} "
                         f"@{r['entry_premium']} (gap unavailable)")
        else:
            parts.append(
                f"{r['decision']} {r['direction']} {r['strike']} "
                f"@{r['entry_premium']} score {r['score']} net "
                f"{float(r['stack_net_inr']):+,.2f}")
    return (f"CONF-GATE SHADOW {day} ({row_type}): "
            + " · ".join(parts))


def print_tallies():
    rows = ledger_rows()
    for label, sel in (("full November (incl. Nov 2-13 counterfactual "
                        "backfill)",
                        lambda r: True),
                       ("LIVE forward rows only (from 2026-11-16)",
                        lambda r: r["row_type"] == "LIVE")):
        sub = [r for r in rows if sel(r)]
        n, tot = totals(sub)
        stack_tot = round(sum(float(r["stack_net_inr"]) for r in sub), 2)
        print(f"CONF-GATE kept-set — {label}: kept {n} legs, kept-set "
              f"total {tot:+,.2f} (stack legs on those rows "
              f"{stack_tot:+,.2f}). Paper only, real money Rs0.")


# ---------------- verification (dry — writes nothing) ------------------
VERIFY_EXPECT = {  # date -> (score, decision) from the phase-2 run
    "2026-11-04": (0.75, "KEPT"),
    "2026-11-09": (-0.50, "IDLED"),
    "2026-11-12": (0.00, "IDLED"),
    "2026-11-13": (0.50, "KEPT"),
}


def verify():
    got = {}
    stack_tot = 0.0
    for day in NOV_DAYS:
        for row in score_day(day, "VERIFY"):
            got[row["date"]] = row
            stack_tot = round(stack_tot
                              + float(row["stack_net_inr"]), 2)
    ok = True
    for day, (es, ed) in VERIFY_EXPECT.items():
        r = got.get(day)
        if r is None:
            print(f"VERIFY {day}: MISSING leg row")
            ok = False
            continue
        match = (r["decision"] != "UNSCORED"
                 and abs(float(r["score"]) - es) < 1e-9
                 and r["decision"] == ed)
        ok = ok and match
        print(f"VERIFY {day}: {r['rep']} {r['direction']} "
              f"{r['strike']} @{r['entry_premium']} score "
              f"{r['score'] or '-'} (expect {es:+.2f}) decision "
              f"{r['decision']} (expect {ed}) net "
              f"{float(r['stack_net_inr']):+,.2f} "
              f"{'MATCH' if match else 'MISMATCH'}")
    kept_rows = [r for r in got.values() if r["decision"] == "KEPT"]
    kept_tot = round(sum(float(r["kept_net_inr"]) for r in kept_rows), 2)
    print(f"VERIFY kept-set November total: {kept_tot:+,.2f} "
          f"(expect +760.00) · stack total: {stack_tot:+,.2f} "
          f"(expect -2,680.00)")
    ok = ok and kept_tot == 760.00 and stack_tot == -2680.00
    print("VERIFY: " + ("EXACT REPRODUCTION of the phase-2 November "
                        "counterfactual — safe to schedule."
                        if ok else
                        "MISMATCH — do NOT schedule; report instead."))
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
    assert kept_tot == 760.00, kept_tot
    print(f"BACKFILL Nov 2-13 written: stack {stack_tot:+,.2f} -> "
          f"confidence-gate kept-set {kept_tot:+,.2f} "
          f"(counterfactual rows, labelled as such).")
    print_tallies()
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check against the "
                         "phase-2 November counterfactual")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.backfill:
        return backfill()
    day = a.date or datetime.now(IST).date().isoformat()
    if day > WINDOW_END:
        print(f"CONF-GATE SHADOW {day}: November window closed "
              f"2026-11-30 — the gate's fate is decided at the Nov 30 "
              f"verdicts / December adoption. No row written.")
        return 0
    if day < START:
        print(f"CONF-GATE SHADOW: {day} is before the shadow start "
              f"{START} — nothing scored (Nov 2-13 live in the ledger "
              f"as the labelled counterfactual backfill).")
        return 0
    rows = score_day(day, "LIVE")
    if rows:
        upsert(rows)
    print(fmt_day(day, rows, "LIVE"))
    print_tallies()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
