#!/usr/bin/env python3
"""EKAM-2c — RSI-upgrade turn on EKAM-2 S0.
Spec: ekam2c_SPEC.md (frozen 2026-11-14 before scoring). Research only; changes
no book/ledger/job. Basis: equity cash, frozen 25 names, per 100 shares
PROVISIONAL, Rs40/trade, paper only, real money Rs0. Judged per year.
The base book, data prep, stats and placebo are the EKAM build's own (imported).
sim2c is the EKAM merge/entry state machine verbatim plus ONE change (spec s.2):
a pure-BB position whose name fires an RSI entry signal while held converts,
from that day, to the RSI exit stack only (counted from entry; TIME60/CAP
apply from the day after the trigger — causality carve-out in the spec).
"""
import csv, json, os, sys
from collections import Counter

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import ekam_build as EKAM

NAMES = EKAM.NAMES
COST = EKAM.COST
ALLOWED = ["BB", "RSI"]

# ---------------------------------------------------------------- EKAM-2c engine
def sim2c(d, events=None):
    """EKAM.sim (merged, S0) verbatim, except the exit governance of a pure-BB
    position converts to the RSI stack when an RSI entry signal fires while
    the position is held (spec s.2). RSI-native and BOTH positions run the
    EKAM union rules unchanged. No stop (S0)."""
    dates, o, h, l, c, n = d["dates"], d["o"], d["h"], d["l"], d["c"], d["n"]
    trades = []; pos = None; i = 0
    while i < n:
        if pos is None:
            sigs = [k for k in ALLOWED if d["sig_in"][k][i]]
            if sigs and i + 1 < n:
                pos = dict(e=i + 1, E=float(o[i + 1]), comps=tuple(sigs),
                           sig_date=dates[i], upgraded=False, up_idx=None,
                           up_date=None)
                i += 1; continue
            if sigs and events is not None:
                events.append(("NO_NEXT_DAY", d["sym"], dates[i],
                               "+".join(sigs), None))
            i += 1; continue
        held = [k for k in ALLOWED if d["sig_in"][k][i]]
        if events is not None and held:
            events.append(("IGNORED_HELD", d["sym"], dates[i],
                           "+".join(held), "+".join(pos["comps"])))
        e, E, comps = pos["e"], pos["E"], pos["comps"]
        # ---- THE ONE CHANGE: RSI upgrade trigger (pure BB positions only)
        converted_today = False
        if comps == ("BB",) and not pos["upgraded"] and "RSI" in held:
            pos["upgraded"] = True; pos["up_idx"] = i; pos["up_date"] = dates[i]
            converted_today = True
            if events is not None:
                events.append(("UPGRADED", d["sym"], dates[i], "RSI", "BB"))
        done = None
        if comps == ("BB",) and pos["upgraded"]:
            # RSI stack only. On the conversion day itself, only the close
            # leg is evaluated (spec causality carve-out); TIME60/CAP from
            # the day after the trigger.
            if not converted_today:
                if i - e >= 60 and i > e:
                    done = (i, float(o[i]), "TIME")
                if done is None and i >= e:
                    lvl = E * 1.10
                    if h[i] >= lvl:
                        done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
            if done is None and d["sig_out"]["RSI"][i]:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-RSI")
                else:
                    done = (i, float(c[i]), "FORCED")
        elif "RSI" in comps:
            # RSI-native and BOTH: EKAM union stack verbatim.
            if i - e >= 60 and i > e:
                done = (i, float(o[i]), "TIME")
            if done is None and i >= e:
                lvl = E * 1.10
                if h[i] >= lvl:
                    done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
            if done is None:
                fire = None
                for k in comps:
                    if d["sig_out"][k][i]:
                        fire = k; break
                if fire is not None:
                    if i + 1 < n:
                        done = (i + 1, float(o[i + 1]), "SIGNAL-" + fire)
                    else:
                        done = (i, float(c[i]), "FORCED")
        else:
            # Pure BB, not (or not yet) upgraded: EKAM stack = BB close rule.
            if d["sig_out"]["BB"][i]:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-BB")
                else:
                    done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            trades.append(dict(
                sym=d["sym"], comps="+".join(comps),
                signal_date=pos["sig_date"], entry_date=dates[e],
                exit_date=dates[xi], entry=E, exit=xp,
                net=round((xp - E) * 100.0 - COST, 2), hold=xi - e,
                exit_kind=why, forced=(why == "FORCED"),
                upgraded=pos["upgraded"], upgrade_date=pos["up_date"],
                upgrade_offset=(pos["up_idx"] - e) if pos["upgraded"] else None,
                counted_upgrade=bool(pos["upgraded"] and xi > pos["up_idx"])))
            pos = None; i = xi; continue
        i += 1
    if pos is not None:
        e, E = pos["e"], pos["E"]
        xp = float(c[n - 1])
        trades.append(dict(
            sym=d["sym"], comps="+".join(pos["comps"]),
            signal_date=pos["sig_date"], entry_date=dates[e],
            exit_date=dates[n - 1], entry=E, exit=xp,
            net=round((xp - E) * 100.0 - COST, 2), hold=n - 1 - e,
            exit_kind="FORCED", forced=True,
            upgraded=pos["upgraded"], upgrade_date=pos["up_date"],
            upgrade_offset=(pos["up_idx"] - e) if pos["upgraded"] else None,
            counted_upgrade=bool(pos["upgraded"] and (n - 1) > pos["up_idx"])))
    return trades

def trade_key(t):
    return (t["sym"], t["comps"], t["signal_date"], t["entry_date"],
            t["exit_date"], t["entry"], t["exit"], t["net"], t["hold"],
            t["exit_kind"], t["forced"])

def norm_stats(s):
    return json.loads(json.dumps(s))

def in_year_window(t, yr):
    return (t["entry_date"][:4] == str(yr)
            and 1 <= int(t["entry_date"][5:7]) <= 10)

def main():
    out = {"basis": "equity cash, frozen 25 names, per 100 shares PROVISIONAL, "
                    "Rs40/trade, paper only, real money Rs0"}
    published = json.load(open(os.path.join(WS, "ekam_results.json")))
    data = {sym: EKAM.prep(sym) for sym in NAMES}

    # ---- CONTROL (a): EKAM engine EKAM-2 S0 vs published full stats
    ctrl_tr = []; ctrl_ev = []
    for sym in NAMES:
        ctrl_tr.extend(EKAM.sim(data[sym], ALLOWED, stop_pct=None, merged=True,
                                events=ctrl_ev))
    ctrl_stats = {yr: EKAM.stats(ctrl_tr, yr) for yr in (2025, 2026)}
    ctrl_ok = True
    for yr in (2025, 2026):
        pub = published["EKAM2"]["S0"][str(yr)]
        if norm_stats(ctrl_stats[yr]) != pub:
            ctrl_ok = False
            print(f"CONTROL MISMATCH {yr}:\n got {norm_stats(ctrl_stats[yr])}\n pub {pub}",
                  flush=True)
    print("control (a) full-stats match:", ctrl_ok, flush=True)

    # ---- CONTROL (b): placebo determinism vs published S0
    print("placebo (control determinism check) ...", flush=True)
    det = {}
    det_ok = True
    for yr in (2025, 2026):
        pubp = published["placebo"]["S0"][str(yr)]
        pc = EKAM.placebo(data, yr, ctrl_stats[yr]["trades"], None,
                          ctrl_stats[yr]["total"])
        ok = (pc["percentile"] == pubp["percentile"]
              and pc["draw_mean"] == pubp["draw_mean"]
              and pc["draw_median"] == pubp["draw_median"])
        det[yr] = dict(check=pc, published=pubp, reproduces=ok)
        det_ok = det_ok and ok
        print(f"control (b) {yr}: pct {pc['percentile']} vs {pubp['percentile']}, "
              f"mean {pc['draw_mean']} vs {pubp['draw_mean']}, median "
              f"{pc['draw_median']} vs {pubp['draw_median']} -> {ok}", flush=True)
    out["control"] = {"full_stats_match_published": ctrl_ok,
                      "placebo_determinism": det,
                      "placebo_determinism_ok": det_ok}
    if not (ctrl_ok and det_ok):
        out["ABORTED"] = "control mismatch - no EKAM-2c numbers produced"
        with open(os.path.join(WS, "ekam2c_results.json"), "w") as f:
            json.dump(out, f, indent=1)
        print("CONTROL FAILED - aborting before EKAM-2c scoring", flush=True)
        return

    # ---- EKAM-2c run
    tr2c = []; ev2c = []
    for sym in NAMES:
        tr2c.extend(sim2c(data[sym], events=ev2c))
    st2c = {yr: EKAM.stats(tr2c, yr) for yr in (2025, 2026)}
    out["EKAM2_S0"] = {yr: ctrl_stats[yr] for yr in (2025, 2026)}
    out["EKAM2c"] = {yr: st2c[yr] for yr in (2025, 2026)}

    # ---- trade-list diff (EKAM fields only; 2c comps stay the entry tag)
    a = Counter(trade_key(t) for t in ctrl_tr)
    b = Counter(trade_key(t) for t in tr2c)
    only_ctrl = list((a - b).elements()); only_2c = list((b - a).elements())
    out["trade_list_diff"] = dict(control_trades=sum(a.values()),
                                  ekam2c_trades=sum(b.values()),
                                  only_in_control=len(only_ctrl),
                                  only_in_ekam2c=len(only_2c),
                                  differing_control=only_ctrl,
                                  differing_ekam2c=only_2c)
    print(f"trade diff: control {sum(a.values())} vs 2c {sum(b.values())}; "
          f"only-control {len(only_ctrl)}, only-2c {len(only_2c)}", flush=True)

    # ---- UPGRADE ACCOUNT: counted upgrades, matched back to S0 positions
    s0_by_key = {}
    for t in ctrl_tr:
        s0_by_key[(t["sym"], t["signal_date"], t["entry_date"], t["entry"])] = t
    ups = [t for t in tr2c if t["counted_upgrade"]]
    up = {"total_counted": len(ups), "by_year": {}, "outside_windows": []}
    for yr in (2025, 2026):
        rows = []; unmatched = []
        for t in [x for x in ups if in_year_window(x, yr)]:
            m = s0_by_key.get((t["sym"], t["signal_date"], t["entry_date"],
                               t["entry"]))
            row = dict(sym=t["sym"], signal_date=t["signal_date"],
                       entry_date=t["entry_date"], entry=t["entry"],
                       upgrade_date=t["upgrade_date"],
                       ekam2c_exit_date=t["exit_date"], ekam2c_exit=t["exit"],
                       ekam2c_net=t["net"], ekam2c_exit_kind=t["exit_kind"],
                       ekam2c_hold=t["hold"],
                       s0_matched=m is not None,
                       s0_exit_date=(m["exit_date"] if m else None),
                       s0_exit=(m["exit"] if m else None),
                       s0_net=(m["net"] if m else None),
                       s0_exit_kind=(m["exit_kind"] if m else None),
                       s0_hold=(m["hold"] if m else None))
            (rows if m is not None else unmatched).append(row)
        up["by_year"][yr] = dict(
            count=len(rows) + len(unmatched),
            matched=len(rows),
            ekam2c_net_matched=round(sum(r["ekam2c_net"] for r in rows), 2),
            s0_net_matched=round(sum(r["s0_net"] for r in rows), 2),
            diff_matched=round(sum(r["ekam2c_net"] for r in rows)
                               - sum(r["s0_net"] for r in rows), 2),
            positions=rows, unmatched=unmatched)
        print(f"UPGRADES {yr}: counted {up['by_year'][yr]['count']} "
              f"(matched {up['by_year'][yr]['matched']}) · 2c net "
              f"{up['by_year'][yr]['ekam2c_net_matched']} vs S0 net "
              f"{up['by_year'][yr]['s0_net_matched']} · diff "
              f"{up['by_year'][yr]['diff_matched']}", flush=True)
    for t in ups:
        if not any(in_year_window(t, yr) for yr in (2025, 2026)):
            m = s0_by_key.get((t["sym"], t["signal_date"], t["entry_date"],
                               t["entry"]))
            up["outside_windows"].append(dict(
                sym=t["sym"], signal_date=t["signal_date"],
                entry_date=t["entry_date"], entry=t["entry"],
                upgrade_date=t["upgrade_date"], ekam2c_net=t["net"],
                s0_matched=m is not None,
                s0_net=(m["net"] if m else None)))
    out["upgrades"] = up
    trig_all = [t for t in tr2c if t["upgraded"]]
    out["upgrades"]["triggers_fired_total"] = len(trig_all)
    out["upgrades"]["triggers_not_counted"] = len(trig_all) - len(ups)

    # ---- PLACEBO for EKAM-2c (EKAM design verbatim)
    print("placebo (2c) ...", flush=True)
    out["placebo"] = {}
    for yr in (2025, 2026):
        p2 = EKAM.placebo(data, yr, st2c[yr]["trades"], None, st2c[yr]["total"])
        out["placebo"][yr] = p2
        print(f"PLACEBO 2c {yr}: real {p2['real_total']} pct {p2['percentile']} "
              f"mean {p2['draw_mean']} median {p2['draw_median']} n {p2['n_trades']}",
              flush=True)

    # ---- NOVEMBER (descriptive) from the 2c book + events
    last_date = max(d["dates"][-1] for d in data.values())
    entries = [t for t in tr2c if "2026-11-02" <= t["entry_date"] <= "2026-11-13"]
    open_end = [t for t in tr2c if t["forced"] and t["exit_date"] == last_date]
    earlier_open = [t for t in open_end if t["entry_date"] < "2026-11-02"]
    out["november"] = dict(
        data_last_date=last_date,
        entries_nov2_13=[dict(sym=t["sym"], comps=t["comps"],
                              display_tag=("UPGRADED" if t["counted_upgrade"]
                                           else t["comps"]),
                              signal_date=t["signal_date"],
                              entry_date=t["entry_date"], entry=t["entry"],
                              upgrade_date=t["upgrade_date"],
                              status=("OPEN/MARKED" if t in open_end else "CLOSED"),
                              exit_date=t["exit_date"], exit=t["exit"],
                              net=t["net"], exit_kind=t["exit_kind"])
                         for t in sorted(entries, key=lambda x: x["entry_date"])],
        open_at_nov13=[dict(sym=t["sym"], comps=t["comps"],
                            display_tag=("UPGRADED" if t["counted_upgrade"]
                                         else t["comps"]),
                            entry_date=t["entry_date"], entry=t["entry"],
                            upgrade_date=t["upgrade_date"],
                            mark=t["exit"], marked_net=t["net"])
                       for t in sorted(open_end, key=lambda x: x["entry_date"])],
        entered_earlier_still_open=[dict(sym=t["sym"], comps=t["comps"],
                                         entry_date=t["entry_date"],
                                         entry=t["entry"],
                                         upgrade_date=t["upgrade_date"],
                                         mark=t["exit"], marked_net=t["net"])
                                    for t in sorted(earlier_open,
                                                    key=lambda x: x["entry_date"])],
        signals_no_entry_nov=[e[:4] for e in ev2c
                              if e[0] in ("IGNORED_HELD", "NO_NEXT_DAY")
                              and "2026-11-02" <= e[2] <= "2026-11-13"],
        upgrades_in_nov_window=[e[:4] for e in ev2c if e[0] == "UPGRADED"
                                and "2026-11-02" <= e[2] <= "2026-11-13"],
        upgraded_positions_open_in_nov=[dict(sym=t["sym"],
                                             entry_date=t["entry_date"],
                                             upgrade_date=t["upgrade_date"])
                                        for t in tr2c if t["counted_upgrade"]
                                        and t["entry_date"] <= "2026-11-13"
                                        and t["exit_date"] >= "2026-11-02"])

    with open(os.path.join(WS, "ekam2c_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(WS, "ekam2c_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "sym", "comps", "display_tag", "signal_date",
                    "entry_date", "exit_date", "entry", "exit", "net", "hold",
                    "exit_kind", "forced", "upgrade_date"])
        for book, tr in (("EKAM2_S0", ctrl_tr), ("EKAM2c", tr2c)):
            for t in sorted(tr, key=lambda x: (x["entry_date"], x["sym"])):
                if book == "EKAM2c":
                    disp = "UPGRADED" if t["counted_upgrade"] else t["comps"]
                    upd = t["upgrade_date"] or ""
                else:
                    disp = t["comps"]; upd = ""
                w.writerow([book, t["sym"], t["comps"], disp,
                            t["signal_date"], t["entry_date"], t["exit_date"],
                            t["entry"], t["exit"], t["net"], t["hold"],
                            t["exit_kind"], t["forced"], upd])
    for yr in (2025, 2026):
        s0, s2 = ctrl_stats[yr], st2c[yr]
        print(f"{yr} S0 : {s0['trades']}t total {s0['total']} WR {s0['wr']} "
              f"hold {s0['avg_hold']} DD {s0['max_dd']} extop3 {s0['ex_top3']} "
              f"worst {s0['worst']} peak {s0['peak_concurrent']}", flush=True)
        print(f"{yr} 2c : {s2['trades']}t total {s2['total']} WR {s2['wr']} "
              f"hold {s2['avg_hold']} DD {s2['max_dd']} extop3 {s2['ex_top3']} "
              f"worst {s2['worst']} peak {s2['peak_concurrent']}", flush=True)
    print("november:", json.dumps(out["november"], indent=1), flush=True)

if __name__ == "__main__":
    main()
