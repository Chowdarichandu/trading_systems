#!/usr/bin/env python3
"""EKAM-2b — exit-ownership small turn on EKAM-2 S0.
Spec: ekam2b_SPEC.md (frozen 2026-11-14 before scoring). Research only; changes
no book/ledger/job. Basis: equity cash, frozen 25 names, per 100 shares
PROVISIONAL, Rs40/trade, paper only, real money Rs0. Judged per year.
The base book, data prep, stats and placebo are the EKAM build's own (imported).
sim2b is an independent implementation of the ownership exit stack (spec s.2).
"""
import csv, json, os, sys
from collections import Counter

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import ekam_build as EKAM

NAMES = EKAM.NAMES
COST = EKAM.COST
ALLOWED = ["BB", "RSI"]

# ---------------------------------------------------------------- EKAM-2b engine
def sim2b(d, events=None):
    """EKAM-2 merge/entry state machine verbatim; the exit stack is built ONLY
    from the position's entering component(s) (spec s.2). Tag BOTH keeps the
    EKAM-2 first-trigger union with EKAM-2 priority (TIME -> CAP -> close
    signals, BB before RSI). No stop (S0)."""
    dates, o, h, l, c, n = d["dates"], d["o"], d["h"], d["l"], d["c"], d["n"]
    trades = []; pos = None; i = 0
    while i < n:
        if pos is None:
            sigs = [k for k in ALLOWED if d["sig_in"][k][i]]
            if sigs and i + 1 < n:
                pos = dict(e=i + 1, E=float(o[i + 1]), comps=tuple(sigs),
                           sig_date=dates[i])
                i += 1; continue
            if sigs and events is not None:
                events.append(("NO_NEXT_DAY", d["sym"], dates[i],
                               "+".join(sigs), None))
            i += 1; continue
        if events is not None:
            held = [k for k in ALLOWED if d["sig_in"][k][i]]
            if held:
                events.append(("IGNORED_HELD", d["sym"], dates[i],
                               "+".join(held), "+".join(pos["comps"])))
        e, E, owners = pos["e"], pos["E"], pos["comps"]
        done = None
        if "RSI" in owners and i - e >= 60 and i > e:
            done = (i, float(o[i]), "TIME")
        if done is None and "RSI" in owners and i >= e:
            lvl = E * 1.10
            if h[i] >= lvl:
                done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
        if done is None:
            fire = None
            for k in owners:
                if d["sig_out"][k][i]:
                    fire = k; break
            if fire is not None:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-" + fire)
                else:
                    done = (i, float(c[i]), "FORCED")
        if done is not None:
            xi, xp, why = done
            trades.append(dict(sym=d["sym"], comps="+".join(owners),
                               signal_date=pos["sig_date"], entry_date=dates[e],
                               exit_date=dates[xi], entry=E, exit=xp,
                               net=round((xp - E) * 100.0 - COST, 2), hold=xi - e,
                               exit_kind=why, forced=(why == "FORCED")))
            pos = None; i = xi; continue
        i += 1
    if pos is not None:
        e, E = pos["e"], pos["E"]
        xp = float(c[n - 1])
        trades.append(dict(sym=d["sym"], comps="+".join(pos["comps"]),
                           signal_date=pos["sig_date"], entry_date=dates[e],
                           exit_date=dates[n - 1], entry=E, exit=xp,
                           net=round((xp - E) * 100.0 - COST, 2), hold=n - 1 - e,
                           exit_kind="FORCED", forced=True))
    return trades

def trade_key(t):
    return (t["sym"], t["comps"], t["signal_date"], t["entry_date"],
            t["exit_date"], t["entry"], t["exit"], t["net"], t["hold"],
            t["exit_kind"], t["forced"])

def norm_stats(s):
    return json.loads(json.dumps(s))

def main():
    out = {"basis": "equity cash, frozen 25 names, per 100 shares PROVISIONAL, "
                    "Rs40/trade, paper only, real money Rs0"}
    published = json.load(open(os.path.join(WS, "ekam_results.json")))
    data = {sym: EKAM.prep(sym) for sym in NAMES}

    # ---- CONTROL: EKAM engine EKAM-2 S0 vs published full stats
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
    out["control"] = {"full_stats_match_published": ctrl_ok}
    xtab_ctrl = Counter((t["comps"], t["exit_kind"]) for t in ctrl_tr)
    out["control"]["exit_kind_by_tag"] = {f"{k[0]}|{k[1]}": v
                                          for k, v in sorted(xtab_ctrl.items())}
    print("control full-stats match:", ctrl_ok, flush=True)
    print("control exit-kind x tag:", dict(xtab_ctrl), flush=True)
    if not ctrl_ok:
        out["ABORTED"] = "control mismatch - no EKAM-2b numbers produced"
        with open(os.path.join(WS, "ekam2b_results.json"), "w") as f:
            json.dump(out, f, indent=1)
        return

    # ---- EKAM-2b run
    tr2b = []; ev2b = []
    for sym in NAMES:
        tr2b.extend(sim2b(data[sym], events=ev2b))
    st2b = {yr: EKAM.stats(tr2b, yr) for yr in (2025, 2026)}
    out["EKAM2_S0"] = {yr: ctrl_stats[yr] for yr in (2025, 2026)}
    out["EKAM2b"] = {yr: st2b[yr] for yr in (2025, 2026)}
    xtab_2b = Counter((t["comps"], t["exit_kind"]) for t in tr2b)
    out["EKAM2b"]["exit_kind_by_tag"] = {f"{k[0]}|{k[1]}": v
                                        for k, v in sorted(xtab_2b.items())}
    a = Counter(trade_key(t) for t in ctrl_tr)
    b = Counter(trade_key(t) for t in tr2b)
    only_ctrl = list((a - b).elements()); only_2b = list((b - a).elements())
    out["trade_list_diff"] = dict(control_trades=sum(a.values()),
                                  ekam2b_trades=sum(b.values()),
                                  only_in_control=len(only_ctrl),
                                  only_in_ekam2b=len(only_2b),
                                  differing_control=only_ctrl,
                                  differing_ekam2b=only_2b)
    print(f"trade diff: control {sum(a.values())} vs 2b {sum(b.values())}; "
          f"only-control {len(only_ctrl)}, only-2b {len(only_2b)}", flush=True)

    # ---- PLACEBO: control determinism check, then 2b read off same design
    print("placebo ...", flush=True)
    out["placebo"] = {}
    for yr in (2025, 2026):
        pubp = published["placebo"]["S0"][str(yr)]
        pc = EKAM.placebo(data, yr, ctrl_stats[yr]["trades"], None,
                          ctrl_stats[yr]["total"])
        det_ok = (pc["percentile"] == pubp["percentile"]
                  and pc["draw_mean"] == pubp["draw_mean"]
                  and pc["draw_median"] == pubp["draw_median"])
        p2 = EKAM.placebo(data, yr, st2b[yr]["trades"], None, st2b[yr]["total"])
        out["placebo"][yr] = dict(control_check=pc,
                                  control_reproduces_published=det_ok,
                                  ekam2b=p2)
        print(f"PLACEBO {yr}: control pct {pc['percentile']} (published "
              f"{pubp['percentile']}, match {det_ok}) · 2b pct {p2['percentile']} "
              f"real {p2['real_total']} mean {p2['draw_mean']} median {p2['draw_median']}",
              flush=True)

    # ---- NOVEMBER (descriptive) from the 2b book + events
    last_date = max(d["dates"][-1] for d in data.values())
    entries = [t for t in tr2b if "2026-11-02" <= t["entry_date"] <= "2026-11-13"]
    open_end = [t for t in tr2b if t["forced"] and t["exit_date"] == last_date]
    out["november"] = dict(
        data_last_date=last_date,
        entries_nov2_13=[dict(sym=t["sym"], comps=t["comps"],
                              signal_date=t["signal_date"],
                              entry_date=t["entry_date"], entry=t["entry"],
                              status=("OPEN/MARKED" if t in open_end else "CLOSED"),
                              exit_date=t["exit_date"], exit=t["exit"],
                              net=t["net"], exit_kind=t["exit_kind"])
                         for t in sorted(entries, key=lambda x: x["entry_date"])],
        open_at_nov13=[dict(sym=t["sym"], comps=t["comps"],
                            entry_date=t["entry_date"], entry=t["entry"],
                            mark=t["exit"], marked_net=t["net"])
                       for t in sorted(open_end, key=lambda x: x["entry_date"])],
        signals_no_entry_nov=[e[:4] for e in ev2b
                              if "2026-11-02" <= e[2] <= "2026-11-13"])
    # ---- DIAGNOSTIC: signals ignored while held, by ignored set x holder tag
    diag = Counter((e[3], e[4]) for e in ev2b if e[0] == "IGNORED_HELD")
    out["diagnostic_ignored_held"] = {f"ignored {k[0]} | held by {k[1]}": v
                                      for k, v in sorted(diag.items())}

    with open(os.path.join(WS, "ekam2b_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(WS, "ekam2b_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "sym", "comps", "signal_date", "entry_date",
                    "exit_date", "entry", "exit", "net", "hold", "exit_kind",
                    "forced"])
        for book, tr in (("EKAM2_S0", ctrl_tr), ("EKAM2b", tr2b)):
            for t in sorted(tr, key=lambda x: (x["entry_date"], x["sym"])):
                w.writerow([book, t["sym"], t["comps"], t["signal_date"],
                            t["entry_date"], t["exit_date"], t["entry"],
                            t["exit"], t["net"], t["hold"], t["exit_kind"],
                            t["forced"]])
    for yr in (2025, 2026):
        s0, s2 = ctrl_stats[yr], st2b[yr]
        print(f"{yr} S0 : {s0['trades']}t total {s0['total']} WR {s0['wr']} "
              f"hold {s0['avg_hold']} DD {s0['max_dd']} extop3 {s0['ex_top3']} "
              f"worst {s0['worst']} peak {s0['peak_concurrent']}", flush=True)
        print(f"{yr} 2b : {s2['trades']}t total {s2['total']} WR {s2['wr']} "
              f"hold {s2['avg_hold']} DD {s2['max_dd']} extop3 {s2['ex_top3']} "
              f"worst {s2['worst']} peak {s2['peak_concurrent']}", flush=True)
    print("november:", json.dumps(out["november"], indent=1), flush=True)
    print("diagnostic ignored-held:", out["diagnostic_ignored_held"], flush=True)

if __name__ == "__main__":
    main()
