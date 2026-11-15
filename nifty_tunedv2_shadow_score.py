#!/usr/bin/env python3
"""TUNED v2 FORWARD SHADOW SCORER — Nifty (from Mon 2026-11-16).

Forward paper evidence for NIFTY TUNED v2 (EVE-11), set up
2026-11-14 under the owner's tuning programme (free hands). Every
entry-side conditioner tried on TUNED v1 has failed its gate with
measured reasons (confidence global + family-wise; buildup /
speculation / volume pooled, per-family and inverted), so v2 —
Nifty's OTHER gated construction — gets its forward shadow now,
judged at the Nov 30 verdicts like every other candidate. This is
a SCORE-ONLY shadow: NOT a lead line, no running book changes.
The v1-vs-v2 lead question is decided ONLY at the Nov 30 verdicts
(raised once 2026-11-13; not re-raised before then).

THE DEFINITION (EVE-11, GATE PASS 2026-11-05; verbatim from the
frozen build, nifty_900_tradeday_2026-11-13.py — the leg sets it
rebuilds reproduce the gated anchors to the paisa):

    def is_bpe(l): return comp(l) == "B" and l["direction"] == "PE"
    def is_ace(l): return comp(l) == "A" and l["direction"] == "CE"
    def is_cce(l): return comp(l) == "C" and l["direction"] == "CE"
    V2 = [l for l in DECS1
          if not (is_bpe(l) or is_ace(l) or is_cce(l))]

    TUNED v2 = DEC-S1 - B PE - A CE - C CE   (keeps A PE, B CE, C PE)

Jan-Oct anchor: +Rs115,950.75 / 59 legs, WR 59.3%; CLEAN PASS on
the owner's Rs900 trade-day bar (51 trade-days, Rs2,273.54/
trade-day, zero red months, placebo percentile 100.0 —
nifty_900_tradeday_2026-11-13.md). Until now v2 had ZERO November
legs and no standing daily scorer; this file is that scorer.

FORWARD DERIVATION — the repair programme's N1 forward score
(repair_programme_2026-11-12.md, section N1), replicated exactly,
no reinterpretation: v2's forward legs are a DROP-ONLY filter on
the candle-scored DEC-S1 shadow ledger
(november_shadow_decs1_nifty_log.csv, written by the 15:32 shadow
job) — component + direction, fixed at the entry bar, no leg
re-priced. The component is parsed from the ledger's
system_source exactly as nifty_nfix1_score.py parses it
("DEC-S1 B" -> "B"). The DEC-S1 ledger is NEVER modified.

LEDGER: november_shadow_tunedv2_nifty_log.csv — one row per
DEC-S1 leg (KEPT / DROPPED_B_PE / DROPPED_A_CE / DROPPED_C_CE),
plus an explicit NO_V2_LEG row for a source day with no DEC-S1
leg, and an NC_SOURCE row if the DEC-S1 ledger carries no row
for a live date at all (v2 not scored that day — never estimated,
never hand-filled). A leg whose component parses to something
other than A/B/C is NC_COMPONENT — named, never guessed.

VERIFICATION before scheduling (--verify, writes nothing): the
Nov 2-13 derivation must reproduce the N1 forward score EXACTLY —
DEC-S1's November population is B PE x4 + C CE x1, v2 drops both
classes, so v2 = 0 legs, Rs0 (DEC-S1's own November total on those
legs: -Rs443.50). --backfill writes those Nov 2-13 rows labelled
BACKFILL_COUNTERFACTUAL (pre-shadow history, never live
evidence), with the same assertions.

REVIEW BOUND: days after 2026-11-30 are refused (the Nov 30
verdicts decide v2's future), same guard style as the sibling
scorers. Paper only, real money Rs0. Buying only. Lot 65,
Rs220/trade inside the stored DEC-S1 nets. No API calls — this
scorer reads the stored DEC-S1 ledger only.

Usage:
    python3 nifty_tunedv2_shadow_score.py [--date YYYY-MM-DD]
                                          [--backfill] [--verify]
"""
import argparse, csv, sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

TR = Path.home() / "workspace/trading"
IST = ZoneInfo("Asia/Kolkata")
DECS1_LOG = TR / "november_shadow_decs1_nifty_log.csv"
LEDGER = TR / "november_shadow_tunedv2_nifty_log.csv"
START = "2026-11-16"
WINDOW_END = "2026-11-30"   # review bound: the Nov 30 verdicts
NOV_DAYS = ["2026-11-02", "2026-11-03", "2026-11-04", "2026-11-05",
            "2026-11-06", "2026-11-09", "2026-11-11", "2026-11-12",
            "2026-11-13"]
FIELDS = ["date", "row_type", "component", "direction", "strike",
          "expiry", "entry_time", "entry_premium", "exit_time",
          "exit_premium", "exit_reason", "decs1_net_inr", "decision",
          "v2_net_inr", "v2_running_total_inr", "notes"]

# The N1 forward record, leg for leg (repair_programme_2026-11-12.md
# + november_shadow_decs1_nifty_log.csv as written). v2 drops every
# one of these classes, so the expected kept set is EMPTY.
VERIFY_EXPECT = [  # (date, comp, dir, strike, decs1 net, decision)
    ("2026-11-02", "B", "PE", "23300", -220.00, "DROPPED_B_PE"),
    ("2026-11-03", "B", "PE", "23600", -3470.00, "DROPPED_B_PE"),
    ("2026-11-03", "C", "CE", "23600", 3036.50, "DROPPED_C_CE"),
    ("2026-11-05", "B", "PE", "24400", -3470.00, "DROPPED_B_PE"),
    ("2026-11-11", "B", "PE", "25400", 3680.00, "DROPPED_B_PE"),
]
DECS1_NOV_TOTAL = -443.50


def _t2m(t):
    if not t:
        return 0
    h, m = t.split(":")
    return int(h) * 60 + int(m)


def _drop_rule(comp, direction):
    """EVE-11, verbatim semantics of the frozen build's is_bpe /
    is_ace / is_cce: returns the drop decision or None (kept)."""
    if comp == "B" and direction == "PE":
        return "DROPPED_B_PE"
    if comp == "A" and direction == "CE":
        return "DROPPED_A_CE"
    if comp == "C" and direction == "CE":
        return "DROPPED_C_CE"
    return None


def decs1_day(day):
    """(source_present, legs) from the DEC-S1 shadow ledger — legs
    are the rows with a non-empty net_inr (nifty_nfix1_score.py's
    filter, verbatim); component parsed its way too."""
    present, legs = False, []
    if not DECS1_LOG.exists():
        return present, legs
    for r in csv.DictReader(open(DECS1_LOG)):
        if r["date"] != day:
            continue
        present = True
        if not r["net_inr"]:
            continue
        r["_comp"] = r["system_source"].replace("DEC-S1", "").strip()
        legs.append(r)
    return present, legs


def score_day(day, row_type):
    present, legs = decs1_day(day)
    rows = []

    def blank():
        return {k: "" for k in FIELDS}

    if not present:
        row = blank()
        row.update(date=day, row_type=row_type, decision="NC_SOURCE",
                   notes="NC_SOURCE: the DEC-S1 shadow ledger carries "
                         "no row for this date — TUNED v2 not scored; "
                         "never estimated, never hand-filled")
        return [row]
    if not legs:
        row = blank()
        row.update(date=day, row_type=row_type, decision="NO_V2_LEG",
                   decs1_net_inr="0.00", v2_net_inr="0.00",
                   notes="DEC-S1 no-trade day (its ledger row: none) "
                         "— TUNED v2 takes nothing")
        return [row]
    for r in legs:
        comp = r["_comp"]
        net = float(r["net_inr"])
        row = blank()
        row.update(date=day, row_type=row_type, component=comp,
                   direction=r["direction"], strike=r["strike"],
                   expiry=r["expiry"], entry_time=r["entry_time"],
                   entry_premium=r["entry_premium"],
                   exit_time=r["exit_time"],
                   exit_premium=r["exit_premium"],
                   exit_reason=r["exit_reason"],
                   decs1_net_inr=f"{net:.2f}")
        if comp not in ("A", "B", "C"):
            row.update(decision="NC_COMPONENT",
                       notes=f"NC_COMPONENT: system_source "
                             f"{r['system_source']!r} does not parse "
                             f"to a DEC-S1 component A/B/C — the leg "
                             f"is not classified; never guessed")
            rows.append(row)
            continue
        drop = _drop_rule(comp, r["direction"])
        if drop is None:
            row.update(decision="KEPT", v2_net_inr=f"{net:.2f}",
                       notes=f"KEPT by EVE-11: {comp} "
                             f"{r['direction']} is a TUNED v2 class "
                             f"(v2 = DEC-S1 - B PE - A CE - C CE)")
        else:
            row.update(decision=drop, v2_net_inr="0.00",
                       notes=f"{drop.replace('_', ' ')}: excluded "
                             f"from TUNED v2 by the EVE-11 definition "
                             f"(the DEC-S1 net stands in DEC-S1's own "
                             f"line only)")
        rows.append(row)
    return rows


# ---------------- ledger ----------------------------------------------
def ledger_rows():
    if not LEDGER.exists():
        return []
    with open(LEDGER) as f:
        return list(csv.DictReader(f))


def _key(r):
    return (r["date"], r["entry_time"], r["entry_premium"],
            r["decision"])


def upsert(rows):
    """Replace rows carrying the same (date, entry_time,
    entry_premium, decision) keys, restamp the v2 running November
    total across the whole ledger in (date, entry_time) order,
    rewrite the file — the sibling scorers' mechanics."""
    new_keys = {_key(r) for r in rows}
    kept_rows = [r for r in ledger_rows() if _key(r) not in new_keys]
    all_rows = kept_rows + rows
    all_rows.sort(key=lambda r: (r["date"], _t2m(r["entry_time"]),
                                 float(r["entry_premium"] or 0)))
    run = 0.0
    for r in all_rows:
        if r["decision"] == "KEPT" and r["v2_net_inr"]:
            run = round(run + float(r["v2_net_inr"]), 2)
        r["v2_running_total_inr"] = f"{run:.2f}"
    with open(LEDGER, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)


def totals(rows):
    legs = [r for r in rows if r["decision"] == "KEPT"]
    decs1 = round(sum(float(r["decs1_net_inr"]) for r in rows
                      if r["decs1_net_inr"]), 2)
    return (len(legs),
            round(sum(float(r["v2_net_inr"]) for r in legs), 2),
            decs1)


def fmt_day(day, rows, row_type):
    parts = []
    for r in rows:
        d = r["decision"]
        if d == "KEPT":
            parts.append(f"KEPT {r['component']} {r['direction']} "
                         f"{r['strike']} @{r['entry_premium']} net "
                         f"{float(r['v2_net_inr']):+,.2f}")
        elif d.startswith("DROPPED"):
            parts.append(f"{d} {r['component']} {r['direction']} "
                         f"{r['strike']} @{r['entry_premium']} "
                         f"(DEC-S1 net "
                         f"{float(r['decs1_net_inr']):+,.2f} — not "
                         f"v2's)")
        elif d == "NO_V2_LEG":
            parts.append("no v2 leg (DEC-S1 no-trade day)")
        else:
            parts.append(f"{d} — v2 not scored for this date")
    v2n = round(sum(float(r["v2_net_inr"]) for r in rows
                    if r["v2_net_inr"]), 2)
    return (f"TUNED-V2 SHADOW {day} ({row_type}): "
            + " · ".join(parts)
            + f" · v2 day net {v2n:+,.2f}")


def print_tallies():
    rows = ledger_rows()
    for label, sel in (("full November (incl. Nov 2-13 "
                        "counterfactual backfill)",
                        lambda r: True),
                       ("LIVE forward rows only (from 2026-11-16)",
                        lambda r: r["row_type"] == "LIVE")):
        sub = [r for r in rows if sel(r)]
        n, tot, decs1 = totals(sub)
        print(f"TUNED-V2 SHADOW tally — {label}: v2 kept {n} legs, "
              f"v2 total {tot:+,.2f} (DEC-S1 nets on those rows "
              f"{decs1:+,.2f}). Paper only, real money Rs0.")


# ---------------- verification (dry — writes nothing) ----------------
def verify():
    got = []
    for day in NOV_DAYS:
        for row in score_day(day, "VERIFY"):
            if row["component"]:
                got.append((row["date"], row["component"],
                            row["direction"], row["strike"],
                            float(row["decs1_net_inr"]),
                            row["decision"]))
    ok = True
    for exp in VERIFY_EXPECT:
        match = exp in got
        ok = ok and match
        d, c, dr, s, n, dec = exp
        print(f"VERIFY {d}: {c} {dr} {s} DEC-S1 net {n:+,.2f} -> "
              f"{dec} {'MATCH' if match else 'MISMATCH — not found '
              'in the derivation'}")
    kept = [g for g in got if g[5] == "KEPT"]
    extra = [g for g in got if g not in VERIFY_EXPECT]
    decs1_tot = round(sum(g[4] for g in got), 2)
    print(f"VERIFY: DEC-S1 legs found {len(got)} (expect "
          f"{len(VERIFY_EXPECT)}) · kept by v2 {len(kept)} (expect "
          f"0) · extra/unexpected legs {len(extra)} (expect 0) · "
          f"DEC-S1 November total {decs1_tot:+,.2f} (expect "
          f"{DECS1_NOV_TOTAL:+,.2f}) · TUNED v2 Nov 2-13 = 0 legs, "
          f"Rs0.00")
    for g in extra:
        print(f"VERIFY DISCREPANCY: unexpected leg {g} — the N1 "
              f"derivation did not produce this leg")
    for g in kept:
        print(f"VERIFY DISCREPANCY: KEPT leg {g} — N1's forward "
              f"score kept nothing in Nov 2-13")
    ok = ok and not kept and not extra \
        and decs1_tot == DECS1_NOV_TOTAL and len(got) == len(VERIFY_EXPECT)
    print("VERIFY: " + ("EXACT REPRODUCTION of the repair "
                        "programme's N1 forward score (TUNED v2 "
                        "Nov 2-13: 0 legs, Rs0) — safe to schedule."
                        if ok else
                        "MISMATCH — do NOT schedule; report the "
                        "discrepancy in full."))
    return 0 if ok else 3


def backfill():
    all_rows = []
    for day in NOV_DAYS:
        rows = score_day(day, "BACKFILL_COUNTERFACTUAL")
        all_rows.extend(rows)
        print(fmt_day(day, rows, "BACKFILL_COUNTERFACTUAL"))
    n, tot, decs1 = totals(all_rows)
    assert n == 0 and tot == 0.00, (n, tot)
    assert decs1 == DECS1_NOV_TOTAL, decs1
    upsert(all_rows)
    print(f"BACKFILL Nov 2-13 written: DEC-S1 {decs1:+,.2f} on its "
          f"5 legs -> TUNED v2 kept {n} legs, {tot:+,.2f} "
          f"(counterfactual rows, labelled as such — pre-shadow "
          f"history, never live evidence).")
    print_tallies()
    return 0


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", default=None)
    ap.add_argument("--backfill", action="store_true")
    ap.add_argument("--verify", action="store_true",
                    help="no-write reproduction check against the "
                         "repair programme's N1 forward score")
    a = ap.parse_args(argv)
    if a.verify:
        return verify()
    if a.backfill:
        return backfill()
    day = a.date or datetime.now(IST).date().isoformat()
    if day > WINDOW_END:
        print(f"TUNED-V2 SHADOW {day}: November window closed "
              f"2026-11-30 — TUNED v2's fate is decided at the "
              f"Nov 30 verdicts / December adoption. No row written.")
        return 0
    if day < START:
        print(f"TUNED-V2 SHADOW: {day} is before the shadow start "
              f"{START} — nothing scored (Nov 2-13 live in the "
              f"ledger as the labelled counterfactual backfill).")
        return 0
    rows = score_day(day, "LIVE")
    upsert(rows)
    print(fmt_day(day, rows, "LIVE"))
    print_tallies()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
