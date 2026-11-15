#!/usr/bin/env python3
"""LIVE SCORER — Bank Nifty TUNED STACK v2, November 2026 evenings.

Scores one or more November days for the TUNED STACK v2 (Bank's
PRIMARY-DESIGNATED book from 2026-11-11; owner orders 2026-11-10)
into november_shadow_stack_bank_log.csv, replacing each day's rows
idempotently, scored_live=YES.

THE BOOK (frozen; bank_aggressive_tune_2026-11-04.md +
bank_positive_tuning_2026-11-10.py BANK-EVE-19):
  = SHADOW v22 frame (v21 assembly + EVE-04 lock + EVE-05 skip)
  + EVE-06(a) re-entry   + c4 runner extension   + v1 NS3/S3 add-ons
  + BANK-EVE-19: NS1_second legs with entry_time < 10:30 are DROPPED
    after the v22-frame assembly and before the re-entry/c4/v1
    layers; the re-entry set is re-derived against the skipped book
    and v1 candidates on a freed (date, direction) key are admitted —
    the gate's exact interactions (bank_positive_tuning_2026-11-10.py
    lines ~667-695), reproduced here by building stack_keys from the
    post-skip book.

MACHINERY: bank_tuned_stack_november_backfill.assemble_day /
find_reentry / v1_addons, reused verbatim (the backfill's v22-only
intermediate was anchor-verified against the written SHADOW v22 log;
the same anchor is re-checked here per day and any mismatch aborts
the day with nothing written). Same-day scoring works because of the
2026-11-12 daily-series-lag repairs in november_shadow_score
(prep_bank_spot_dir enumerates `upto` explicitly; extend_ns_data
synthesizes a lagging day's daily row from its own spot bars).

CONVENTIONS: premiums per 1 lot (30), Rs 220/trade included in nets;
paper only, real money Rs0. A day that cannot be candle-scored gets
ONE row with empty net and a NOT_COMPUTED note — never an estimate.
A scored day with no legs gets ONE no-trade row, so a missing day in
the log always means "not scored", never "quiet day". The shadow
state file is loaded but NEVER saved (november_shadow_score owns its
persistence; mutations stay in memory, exactly as the backfill did).
No frozen primary log/spec is touched.

Usage: python3 bank_tuned_stack_live_score.py YYYY-MM-DD [...]
"""
import csv, json, sys
from pathlib import Path

TR = Path.home() / "workspace/trading"
sys.path.insert(0, str(TR))
import november_shadow_score as S
import bank_tuned_stack_november_backfill as B

STACK_LOG = TR / "november_shadow_stack_bank_log.csv"
HEADER = ["date", "component", "family", "rep", "direction", "strike",
          "expiry", "entry_time", "entry_premium", "exit_time",
          "exit_premium", "exit_reason", "net_inr", "notes",
          "scored_live"]
LIVE_NOTE = ("TUNED STACK v2 — LIVE (v22 frame + EVE-06(a) re-entry "
             "+ c4 runner extension + v1 add-ons; BANK-EVE-19 "
             "applied), candle-scored {today} · paper only, real "
             "money ₹0, 1 lot")


def replace_day_rows(day, rows):
    existing = []
    if STACK_LOG.exists():
        existing = [r for r in csv.reader(open(STACK_LOG))
                    if r and r[0] != day and r[0] != "date"]
    with open(STACK_LOG, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(HEADER)
        for r in sorted(existing + rows, key=lambda r: (r[0], r[7])):
            w.writerow(r)


def fmt(x):
    return "" if x is None else f"{x:.2f}"


def score_day(day, st, today):
    asm = B.assemble_day(day, st)
    if "nc_day" in asm:
        note = (f"NOT_COMPUTED — {asm['nc_day']} · day excluded from "
                f"all totals, re-scored when the full day is served · "
                f"TUNED STACK v2 · paper only, real money ₹0, 1 lot")
        row = [day, "none", "", "", "", "", "", "", "", "", "", "",
               "", note, "YES"]
        replace_day_rows(day, [row])
        return {"date": day, "status": "NOT_COMPUTED",
                "reason": asm["nc_day"]}
    # ---- SANITY ANCHOR: v22 + v21 reproduction (as the backfill) --
    log22, skip22 = B.log_trades(TR / "november_shadow_v22_bank_log.csv",
                                 day)
    mine22 = B.row_tuples(asm["kept"], asm["lbk"])
    log21, _ = B.log_trades(TR / "november_shadow_v21_bank_log.csv", day)
    mine21 = B.row_tuples(asm["raw_rows"], asm["lbk"])
    if not (log22 == mine22 and skip22 == len(asm["skipped"])
            and log21 == mine21):
        return {"date": day, "status": "ABORTED — anchor mismatch",
                "log_v22": log22, "mine_v22": mine22,
                "log_skip": skip22, "my_skip": len(asm["skipped"]),
                "log_v21": log21, "mine_v21": mine21}
    lbk = asm["lbk"]
    # ---- BANK-EVE-19: drop pre-10:30 NS1_second legs --------------
    skip_keys = {r["leg_key"] for r in asm["kept"]
                 if r["family"] == "NS1_second"
                 and r["entry_time"] < "10:30"}
    skipped19 = [r for r in asm["kept"] if r["leg_key"] in skip_keys]
    kept = [r for r in asm["kept"] if r["leg_key"] not in skip_keys]
    stack = []
    problems = []
    c4_changed = 0
    # ---- layer 1: v22 rows (post-skip), c4 on PLAIN legs -----------
    for r in kept:
        leg = lbk[r["leg_key"]]
        p = r["_params"]
        row = {"date": day, "component": "v22 (EVE-04/05)",
               "family": r["family"], "rep": r["rep"],
               "direction": r["direction"],
               "strike": int(leg["strike"]), "expiry": leg["expiry"],
               "entry_time": r["entry_time"], "entry": r["entry"],
               "exit_time": r["exit_time"], "exit": r["exit"],
               "exit_reason": r["exit_reason"], "net": r["net"]}
        if p["lock"] is None and day != leg["expiry"]:
            import aggressive_score as A
            cs = A.candles("BANKNIFTY", leg["strike"], leg["direction"],
                           day, leg["expiry"])
            p2 = {**p, "lock": 90.0, "tgt2": 180.0}
            ov = "fc2" if r["family"] == "NS1_second" else None
            res = S.replay_overlay(cs, r["entry_time"], p2,
                                   overlay=ov) if cs else None
            if res is not None:
                if abs(res["net"] - r["net"]) > 0.005 or \
                        res["exit_reason"] != r["exit_reason"]:
                    c4_changed += 1
                row.update({"component": "v22 + c4 runner extension",
                            "entry": res["entry"],
                            "exit_time": res["exit_time"],
                            "exit": res["exit"],
                            "exit_reason": res["exit_reason"],
                            "net": res["net"]})
            else:
                problems.append(
                    f"c4 re-sim NC for {r['family']} {r['direction']} "
                    f"{leg['strike']} — v22 values kept")
        stack.append(row)
    stack_keys = {(day, r["direction"]) for r in stack}
    # ---- layer 2: EVE-06(a) re-entry vs the post-skip book ---------
    ev, rleg = B.find_reentry(day, kept, asm["ctx"]["own"])
    reentry_note = None
    if rleg is not None:
        stack.append(rleg)
        stack_keys.add((day, rleg["direction"]))
    elif ev is not None:
        reentry_note = (f"re-entry: {ev['kind']}"
                        + (f" trig {ev['trig']}" if "trig" in ev else "")
                        + (f" realised {ev['realised']}"
                           if "realised" in ev else "")
                        + (f" — {ev['why']}" if "why" in ev else ""))
        if ev["kind"] == "nc":
            problems.append(f"re-entry NOT_COMPUTED — {ev['why']}")
    # ---- layer 3: v1 add-ons ---------------------------------------
    v1_rows, v1_events = B.v1_addons(day, asm, stack_keys)
    stack.extend(v1_rows)
    for e in v1_events:
        if e.startswith("NOT_COMPUTED"):
            problems.append(e)
    # ---- write ------------------------------------------------------
    note = LIVE_NOTE.format(today=today)
    out = []
    for r in stack:
        n = (f"NOT_COMPUTED — {r['nc']} · TUNED STACK v2 LIVE · "
             f"paper only, real money ₹0, 1 lot") if r.get("nc") else note
        out.append([r["date"], r["component"], r["family"], r["rep"],
                    r["direction"], str(r["strike"]), r["expiry"],
                    r["entry_time"], fmt(r["entry"]), r["exit_time"],
                    fmt(r["exit"]), r["exit_reason"], fmt(r["net"]),
                    n, "YES"])
    if not out:
        nt_note = (
            f"No-trade day for TUNED STACK v2 — v22 assembly "
            f"{len(asm['raw_rows'])} legs, kept {len(kept)} after "
            f"EVE-05/EVE-19 (EVE-19 skipped {len(skipped19)}) · "
            f"{reentry_note or 're-entry: no stopped v22 leg'} · "
            f"v1 events: {'; '.join(v1_events) or 'none'} · "
            f"paper only, real money ₹0, 1 lot")
        out = [[day, "none", "", "", "", "", "", "", "", "", "", "",
                "", nt_note, "YES"]]
    replace_day_rows(day, out)
    return {"date": day, "status": "scored", "anchor": "OK",
            "legs": len([r for r in stack if r["net"] is not None]),
            "net": round(sum(r["net"] for r in stack
                             if r["net"] is not None), 2),
            "eve19_skipped": [
                {"family": r["family"], "direction": r["direction"],
                 "entry_time": r["entry_time"], "net": r["net"]}
                for r in skipped19],
            "c4_changed": c4_changed,
            "reentry": reentry_note or
                       (f"leg {rleg['direction']} {rleg['strike']} "
                        f"trig {rleg['trigger_time']} net {rleg['net']}"
                        if rleg else "no stopped v22 leg"),
            "v1_events": v1_events, "problems": problems,
            "rows_written": len(out)}


def main(argv):
    days = [a for a in argv if not a.startswith("--")]
    if not days:
        print("usage: bank_tuned_stack_live_score.py YYYY-MM-DD [...]")
        return 2
    from datetime import date as ddate
    today = ddate.today().isoformat()
    st = S.load_state()
    S.prep_bank_spot_dir(max(days))
    S._PREPPED_UPTO = max(days)
    results = []
    for day in days:
        try:
            res = score_day(day, st, today)
        except SystemExit as e:  # 429 hard stop inside the machinery
            print(json.dumps({"date": day, "status": f"HARD STOP — {e}"}))
            return 1
        results.append(res)
        print(json.dumps(res, indent=1), flush=True)
        if res["status"].startswith("ABORTED"):
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
