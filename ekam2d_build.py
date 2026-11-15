#!/usr/bin/env python3
"""EKAM-2d — disaster floor on UPGRADED positions only.
Spec: ekam2d_SPEC.md (frozen 2026-11-14 before scoring). Research only; changes
no book/ledger/job. Basis: equity cash, frozen 25 names, per 100 shares
PROVISIONAL, Rs40/trade, paper only, real money Rs0. Judged per year.
Control = EKAM-2c (imported from ekam2c_build, itself EKAM-2 S0 + the RSI
upgrade). sim2d is sim2c verbatim plus ONE change (spec s.2): an upgraded
position exits at the next day's open when a daily close falls to or below
entry x (1 - F), F in {0.10, 0.15}. Non-upgraded positions have no floor.
"""
import csv, json, os, sys
from collections import Counter

WS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, WS)
import ekam_build as EKAM
import ekam2c_build as EKAM2C

NAMES = EKAM.NAMES
COST = EKAM.COST
ALLOWED = ["BB", "RSI"]
ROWS = [("2d-10", 0.10), ("2d-15", 0.15)]

# ---------------------------------------------------------------- EKAM-2d engine
def sim2d(d, floor_pct, events=None):
    """EKAM2C.sim2c verbatim, except the disaster floor in the upgraded
    branch (spec s.2). Floor priority: TIME60 (open) -> CAP (intraday) ->
    FLOOR (close check) -> RSI>=70 close leg. Floor is evaluated on the
    conversion day itself (a close-evaluated leg, like the RSI close leg);
    TIME60/CAP keep the EKAM-2c day-after carve-out."""
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
        # ---- EKAM-2c: RSI upgrade trigger (pure BB positions only)
        converted_today = False
        if comps == ("BB",) and not pos["upgraded"] and "RSI" in held:
            pos["upgraded"] = True; pos["up_idx"] = i; pos["up_date"] = dates[i]
            converted_today = True
            if events is not None:
                events.append(("UPGRADED", d["sym"], dates[i], "RSI", "BB"))
        done = None
        if comps == ("BB",) and pos["upgraded"]:
            # RSI stack (EKAM-2c) + THE ONE CHANGE: the disaster floor.
            if not converted_today:
                if i - e >= 60 and i > e:
                    done = (i, float(o[i]), "TIME")
                if done is None and i >= e:
                    lvl = E * 1.10
                    if h[i] >= lvl:
                        done = (i, float(o[i]) if o[i] >= lvl else lvl, "CAP")
            if done is None and float(c[i]) <= E * (1.0 - floor_pct):
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "FLOOR")
                else:
                    done = (i, float(c[i]), "FLOOR")
            if done is None and d["sig_out"]["RSI"][i]:
                if i + 1 < n:
                    done = (i + 1, float(o[i + 1]), "SIGNAL-RSI")
                else:
                    done = (i, float(c[i]), "FORCED")
        elif "RSI" in comps:
            # RSI-native and BOTH: EKAM union stack verbatim (no floor).
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
            # Pure BB, not (or not yet) upgraded: EKAM stack (no floor).
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
                exit_kind=why,
                forced=(why == "FORCED") or (why == "FLOOR" and i == n - 1),
                floor_exit=(why == "FLOOR"),
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
            exit_kind="FORCED", forced=True, floor_exit=False,
            upgraded=pos["upgraded"], upgrade_date=pos["up_date"],
            upgrade_offset=(pos["up_idx"] - e) if pos["upgraded"] else None,
            counted_upgrade=bool(pos["upgraded"] and (n - 1) > pos["up_idx"])))
    return trades

def norm_stats(s):
    return json.loads(json.dumps(s))

def main():
    out = {"basis": "equity cash, frozen 25 names, per 100 shares PROVISIONAL, "
                    "Rs40/trade, paper only, real money Rs0"}
    published2c = json.load(open(os.path.join(WS, "ekam2c_results.json")))
    data = {sym: EKAM.prep(sym) for sym in NAMES}

    # ---- CONTROL (a): EKAM-2c engine vs published EKAM2c full stats
    ctrl_tr = []; ctrl_ev = []
    for sym in NAMES:
        ctrl_tr.extend(EKAM2C.sim2c(data[sym], events=ctrl_ev))
    ctrl_stats = {yr: EKAM.stats(ctrl_tr, yr) for yr in (2025, 2026)}
    ctrl_ok = True
    for yr in (2025, 2026):
        pub = published2c["EKAM2c"][str(yr)]
        if norm_stats(ctrl_stats[yr]) != pub:
            ctrl_ok = False
            print(f"CONTROL MISMATCH {yr}:\n got {norm_stats(ctrl_stats[yr])}\n pub {pub}",
                  flush=True)
    print("control (a) EKAM-2c full-stats match:", ctrl_ok, flush=True)

    # ---- CONTROL (b): placebo determinism vs published EKAM-2c
    print("placebo (control determinism check) ...", flush=True)
    det = {}; det_ok = True
    for yr in (2025, 2026):
        pubp = published2c["placebo"][str(yr)]
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
    out["control"] = {"book": "EKAM-2c",
                      "full_stats_match_published": ctrl_ok,
                      "placebo_determinism": det,
                      "placebo_determinism_ok": det_ok}
    if not (ctrl_ok and det_ok):
        out["ABORTED"] = "control mismatch - no EKAM-2d numbers produced"
        with open(os.path.join(WS, "ekam2d_results.json"), "w") as f:
            json.dump(out, f, indent=1)
        print("CONTROL FAILED - aborting before EKAM-2d scoring", flush=True)
        return
    out["EKAM2c"] = {yr: ctrl_stats[yr] for yr in (2025, 2026)}
    out["EKAM2c_placebo"] = {yr: det[yr]["check"] for yr in (2025, 2026)}

    last_date = max(d["dates"][-1] for d in data.values())
    ctrl_open = [t for t in ctrl_tr if t["forced"] and t["exit_date"] == last_date]
    ctrl_by_key = {(t["sym"], t["signal_date"], t["entry_date"], t["entry"]): t
                   for t in ctrl_tr}
    out["november_ekam2c_open"] = [dict(
        sym=t["sym"], signal_date=t["signal_date"], entry_date=t["entry_date"],
        entry=t["entry"], upgrade_date=t["upgrade_date"], mark=t["exit"],
        marked_net=t["net"])
        for t in sorted(ctrl_open, key=lambda x: x["entry_date"])]
    print(f"EKAM-2c open at {last_date}: {len(ctrl_open)} positions, marked "
          f"{round(sum(t['net'] for t in ctrl_open), 2)}", flush=True)
    # The 8 the EKAM-2c report counts as "entered earlier, still open"
    # (the 9th open position is the Nov 11 ASTRAL entry, tracked separately
    # in each row's November entries).
    ctrl_open_earlier = [t for t in ctrl_open if t["entry_date"] < "2026-11-02"]
    assert len(ctrl_open_earlier) == 8, len(ctrl_open_earlier)
    assert round(sum(t["net"] for t in ctrl_open_earlier), 2) == -23582.00

    out["rows"] = {}
    all_books = {"EKAM2c": ctrl_tr}
    for label, F in ROWS:
        tr = []; ev = []
        for sym in NAMES:
            tr.extend(sim2d(data[sym], F, events=ev))
        all_books[label] = tr
        st = {yr: EKAM.stats(tr, yr) for yr in (2025, 2026)}
        row = {"floor_pct": F, "stats": st}

        # ---- floor exits per year (EKAM entry-year rule)
        row["floor_exits"] = {}
        for yr in (2025, 2026):
            fx = [t for t in tr if t["floor_exit"]
                  and EKAM2C.in_year_window(t, yr)]
            row["floor_exits"][yr] = dict(
                count=len(fx), net=round(sum(t["net"] for t in fx), 2),
                positions=[dict(sym=t["sym"], entry_date=t["entry_date"],
                                entry=t["entry"], upgrade_date=t["upgrade_date"],
                                exit_date=t["exit_date"], exit=t["exit"],
                                net=t["net"], hold=t["hold"])
                           for t in sorted(fx, key=lambda x: x["entry_date"])])
        row["floor_exits_total_all_years"] = dict(
            count=sum(1 for t in tr if t["floor_exit"]),
            net=round(sum(t["net"] for t in tr if t["floor_exit"]), 2))
        row["counted_upgrades"] = sum(1 for t in tr if t["counted_upgrade"])

        # ---- trade-list diff vs EKAM-2c (full EKAM-2c key)
        a = Counter(EKAM2C.trade_key(t) for t in ctrl_tr)
        b = Counter(EKAM2C.trade_key(t) for t in tr)
        row["trade_list_diff"] = dict(
            ekam2c_trades=sum(a.values()), row_trades=sum(b.values()),
            only_in_ekam2c=len(list((a - b).elements())),
            only_in_row=len(list((b - a).elements())))

        # ---- placebo (EKAM design verbatim)
        print(f"placebo ({label}) ...", flush=True)
        row["placebo"] = {}
        for yr in (2025, 2026):
            p = EKAM.placebo(data, yr, st[yr]["trades"], None, st[yr]["total"])
            row["placebo"][yr] = p
            print(f"PLACEBO {label} {yr}: real {p['real_total']} pct "
                  f"{p['percentile']} mean {p['draw_mean']} median "
                  f"{p['draw_median']} n {p['n_trades']}", flush=True)

        # ---- NOVEMBER (descriptive)
        open_end = [t for t in tr if t["forced"] and t["exit_date"] == last_date]
        fate = []
        for t0 in sorted(ctrl_open_earlier, key=lambda x: x["entry_date"]):
            # look the same position (symbol, signal date, entry date, price)
            # up in the row's own book
            m = None
            for t in tr:
                if (t["sym"], t["signal_date"], t["entry_date"], t["entry"]) == \
                   (t0["sym"], t0["signal_date"], t0["entry_date"], t0["entry"]):
                    m = t; break
            if m is None:
                fate.append(dict(sym=t0["sym"], entry_date=t0["entry_date"],
                                 entry=t0["entry"], status="NOT_PRESENT"))
            elif m in open_end:
                fate.append(dict(sym=t0["sym"], entry_date=t0["entry_date"],
                                 entry=t0["entry"], status="OPEN/MARKED",
                                 mark=m["exit"], marked_net=m["net"]))
            elif m["floor_exit"]:
                fate.append(dict(sym=t0["sym"], entry_date=t0["entry_date"],
                                 entry=t0["entry"], status="FLOOR_EXIT",
                                 exit_date=m["exit_date"], exit=m["exit"],
                                 net=m["net"]))
            else:
                fate.append(dict(sym=t0["sym"], entry_date=t0["entry_date"],
                                 entry=t0["entry"], status="EXITED_" + m["exit_kind"],
                                 exit_date=m["exit_date"], exit=m["exit"],
                                 net=m["net"]))
        entries = [t for t in tr if "2026-11-02" <= t["entry_date"] <= "2026-11-13"]
        row["november"] = dict(
            data_last_date=last_date,
            open_at_nov13=[dict(sym=t["sym"], comps=t["comps"],
                                display_tag=("UPGRADED" if t["counted_upgrade"]
                                             else t["comps"]),
                                signal_date=t["signal_date"],
                                entry_date=t["entry_date"], entry=t["entry"],
                                upgrade_date=t["upgrade_date"],
                                mark=t["exit"], marked_net=t["net"],
                                floor_exit=t["floor_exit"])
                           for t in sorted(open_end, key=lambda x: x["entry_date"])],
            open_marked_total=round(sum(t["net"] for t in open_end), 2),
            fate_of_ekam2c_open=fate,
            entries_nov2_13=[dict(sym=t["sym"], comps=t["comps"],
                                  signal_date=t["signal_date"],
                                  entry_date=t["entry_date"], entry=t["entry"],
                                  exit_date=t["exit_date"], exit=t["exit"],
                                  net=t["net"], exit_kind=t["exit_kind"],
                                  forced=t["forced"])
                             for t in sorted(entries, key=lambda x: x["entry_date"])])
        out["rows"][label] = row
        for yr in (2025, 2026):
            s = st[yr]
            print(f"{label} {yr}: {s['trades']}t total {s['total']} WR {s['wr']} "
                  f"hold {s['avg_hold']} DD {s['max_dd']} extop3 {s['ex_top3']} "
                  f"worst {s['worst']} floor {row['floor_exits'][yr]['count']} "
                  f"({row['floor_exits'][yr]['net']})", flush=True)
        print(f"{label} november open: {len(open_end)} marked "
              f"{row['november']['open_marked_total']}", flush=True)

    with open(os.path.join(WS, "ekam2d_results.json"), "w") as f:
        json.dump(out, f, indent=1)
    with open(os.path.join(WS, "ekam2d_trades.csv"), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["book", "sym", "comps", "display_tag", "signal_date",
                    "entry_date", "exit_date", "entry", "exit", "net", "hold",
                    "exit_kind", "forced", "floor_exit", "upgrade_date"])
        for book in ("EKAM2c", "2d-10", "2d-15"):
            for t in sorted(all_books[book], key=lambda x: (x["entry_date"], x["sym"])):
                disp = "UPGRADED" if t["counted_upgrade"] else t["comps"]
                w.writerow([book, t["sym"], t["comps"], disp,
                            t["signal_date"], t["entry_date"], t["exit_date"],
                            t["entry"], t["exit"], t["net"], t["hold"],
                            t["exit_kind"], t["forced"],
                            t.get("floor_exit", False),
                            t["upgrade_date"] or ""])
    print("done", flush=True)

if __name__ == "__main__":
    main()
