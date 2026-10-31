#!/usr/bin/env python3
"""LINE O2 — the 11:00 fade as a frozen EXT-ONLY system.
Cells frozen in stocks_O2_frozen.md BEFORE scoring. Machinery is
Line O1's, reused verbatim (stocks_O1.py builders over
stocks_tuning_mover.py). Equity cash, LONG/SHORT, paper only,
real Rs0. Provisional per 100 shares, net = gross - Rs40/trade.

Modes: run (validate anchors -> base -> home control ->
neighbourhood -> placebo -> stress -> gate)
"""
import csv, json, os, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("O1", f"{BASE}/stocks_O1.py")
O1 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["O1"]
spec.loader.exec_module(O1)
sys.argv = _argv
M = O1.M
RESULTS_F = f"{BASE}/stocks_O2_results.json"
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]

CELLS = {
    "O2-BASE": {"T": "11:00", "thr": 0.01, "exits": "T125/S065", "ctx": "all"},
    "O2-N1":   {"T": "11:00", "thr": 0.0125, "exits": "T125/S065", "ctx": "all"},
    "O2-N2":   {"T": "11:00", "thr": 0.015, "exits": "T125/S065", "ctx": "all"},
    "O2-N3":   {"T": "10:45", "thr": 0.01, "exits": "T125/S065", "ctx": "all"},
    "O2-N4":   {"T": "11:15", "thr": 0.01, "exits": "T125/S065", "ctx": "all"},
    "O2-N5":   {"T": "11:00", "thr": 0.01, "exits": "T125/S050", "ctx": "all"},
    "O2-N6":   {"T": "11:00", "thr": 0.01, "exits": "T10/S065", "ctx": "all"},
    "O2-N7":   {"T": "11:00", "thr": 0.01, "exits": "T125/S065", "ctx": "below50"},
}
EXITS = dict(O1.EXITS)
EXITS["T10/S065"] = (1.0, 0.65)  # frozen O2-N6 exit pair (tp, sp) for replay_plain


def days_in(ns, months):
    return sorted({d for (s, d) in ns["DAYCTX"]
                   if any(d.startswith(m) for m in months)})


def run_cell(which, cell, months, lag=False):
    """Run one frozen cell on one universe; returns (trades, audit_delta)."""
    tp, sp = EXITS[cell["exits"]]
    ns = M.get_ns(which)
    days = days_in(ns, months)
    a0 = dict(O1._AUDIT)
    raw = O1.collect_window(which, days, cell["T"], cell["thr"], "fade",
                            "fixed", tp, sp, lag=lag)
    trades = O1.ctx_filter(raw, cell["ctx"])
    a1 = O1._AUDIT
    delta = {"trades": a1["trades"] - a0["trades"],
             "violations": a1["violations"] - a0["violations"]}
    return trades, delta


def per_stock(trades):
    ps = defaultdict(float)
    for t in trades:
        ps[t["symbol"]] += t["net"]
    return {k: round(v, 2) for k, v in ps.items()}


def month_table(trades):
    out = {}
    for m in MONTHS:
        sel = [t for t in trades if t["date"].startswith(m)]
        out[m] = {"trades": len(sel),
                  "net": round(sum(t["net"] for t in sel), 2)}
    return out


def max_dd(trades):
    daily = defaultdict(float)
    for t in trades:
        daily[t["date"]] += t["net"]
    cum = peak = dd = 0.0
    for d in sorted(daily):
        cum += daily[d]
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def extop3(trades):
    ps = per_stock(trades)
    top3 = sorted(ps, key=lambda k: -ps[k])[:3]
    keep = [t for t in trades if t["symbol"] not in top3]
    jm = round(sum(t["net"] for t in keep if t["date"][:7] <= "2026-05"), 2)
    jo = round(sum(t["net"] for t in keep if t["date"][:7] >= "2026-06"), 2)
    return {"top3": {k: ps[k] for k in top3},
            "net": round(sum(t["net"] for t in keep), 2),
            "jan_may": jm, "jun_oct": jo}


def winsorised(trades):
    ps = per_stock(trades)
    return round(sum(min(v, 2000.0) for v in ps.values()), 2)


def stats(trades):
    mt = month_table(trades)
    ps = per_stock(trades)
    net = round(sum(t["net"] for t in trades), 2)
    return {
        "trades": len(trades), "net": net,
        "jan_may": round(sum(v["net"] for m, v in mt.items() if m <= "2026-05"), 2),
        "jun_oct": round(sum(v["net"] for m, v in mt.items() if m >= "2026-06"), 2),
        "october": mt["2026-10"]["net"],
        "breadth": sum(1 for v in ps.values() if v > 0),
        "exp_per_trade": round(net / len(trades), 2) if trades else None,
        "months": mt,
        "worst_month": min(mt, key=lambda m: mt[m]["net"]),
        "worst_month_net": mt[min(mt, key=lambda m: mt[m]["net"])]["net"],
        "max_dd": max_dd(trades),
        "per_stock": ps,
        "extop3": extop3(trades),
        "winsorised_net": winsorised(trades),
        "top3_share_pct": round(100.0 * sum(sorted(ps.values(), reverse=True)[:3]) / net, 1)
        if net > 0 else None,
    }


def independent_audit(which, cell, trades, lag=False):
    """Re-derive the qualifier pm (trade day's bars < T, or the
    previous trading day's for the lag-placebo) for every dumped
    trade; check the threshold, the fade direction, and that the
    entry bar is exactly the first bar >= T. 0 = clean."""
    ns = M.get_ns(which)
    T, thr = cell["T"], cell["thr"]
    all_days = sorted({d for (s, d) in ns["DAYCTX"]})
    prev_of = {d: all_days[i - 1] for i, d in enumerate(all_days) if i > 0}
    viol = 0
    checked = 0
    pm_cache = {}
    for t in trades:
        qkey = (t["symbol"], prev_of.get(t["date"]) if lag else t["date"])
        if qkey not in pm_cache:
            ctx = ns["DAYCTX"].get(qkey)
            pm_cache[qkey] = M.premove(ctx["candles"], T) if ctx else None
        pm = pm_cache[qkey]
        checked += 1
        if pm is None or abs(pm) < thr - 1e-9:
            viol += 1
            continue
        want = "SHORT" if pm > 0 else "LONG"
        ctx_t = ns["DAYCTX"].get((t["symbol"], t["date"]))
        first_bar = next((c["time"] for c in ctx_t["candles"]
                          if c["time"] >= T), None) if ctx_t else None
        if t["dir"] != want or t["entry_time"] != first_bar:
            viol += 1
    return {"checked": checked, "violations": viol}


def dump(tag, trades):
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "sig_time",
            "entry_time", "entry", "exit_time", "exit", "exit_reason",
            "gross", "net", "event", "premove_pct", "meas_time"]
    with open(f"{BASE}/stocks_O2_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow({c: t.get(c, "") for c in cols})


def gate_legs(s, placebo_net):
    return {
        "net_gt_0": s["net"] > 0,
        "both_halves_gt_0": s["jan_may"] > 0 and s["jun_oct"] > 0,
        "breadth_ge_15": s["breadth"] >= 15,
        "october_gt_0": s["october"] > 0,
        "placebo_beaten": (placebo_net is not None and s["net"] > placebo_net),
        "extop3_gt_0": s["extop3"]["net"] > 0,
    }


def main():
    O1.ensure_prep()
    R = {"nifty_last": O1.NIFTY_LAST,
         "below50_oct28_30": {d: O1.below50(d) for d in
                              ("2026-10-28", "2026-10-29", "2026-10-30")}}
    base = CELLS["O2-BASE"]

    # ---- anchor validation: ext slices of the base cell ----
    ext_full, ad = run_cell("ext", base, MONTHS)
    ext_oct = [t for t in ext_full if t["date"].startswith("2026-10")]
    ext_js = [t for t in ext_full if t["date"][:7] <= "2026-09"]
    R["audit_builtin_base_ext"] = ad
    R["anchors"] = {
        "ext_october": {"got": round(sum(t["net"] for t in ext_oct), 2),
                        "want": 98153.17, "trades": len(ext_oct)},
        "ext_jan_sep": {"got": round(sum(t["net"] for t in ext_js), 2),
                        "want": 206273.84, "trades": len(ext_js)},
    }
    print("ANCHORS:", json.dumps(R["anchors"], indent=1), flush=True)

    # ---- home control (base cell, once) ----
    home_full, ad_home = run_cell("old", base, MONTHS)
    hs = stats(home_full)
    R["home_control"] = {"audit": ad_home, "stats": hs,
                         "jan_sep_net": round(sum(
                             t["net"] for t in home_full
                             if t["date"][:7] <= "2026-09"), 2)}
    print(f"HOME control: Jan-Oct net={hs['net']} JanSep="
          f"{R['home_control']['jan_sep_net']} Oct={hs['october']} "
          f"breadth={hs['breadth']}/25", flush=True)

    # ---- base cell full stats + placebo + audits ----
    bs = stats(ext_full)
    pbo, ad_pbo = run_cell("ext", base, MONTHS, lag=True)
    pbo_net = round(sum(t["net"] for t in pbo), 2)
    ia = independent_audit("ext", base, ext_full)
    ia_pbo = independent_audit("ext", base, pbo, lag=True)
    R["base"] = {"audit_builtin": ad, "stats": bs,
                 "placebo": {"trades": len(pbo), "net": pbo_net,
                             "audit_builtin": ad_pbo},
                 "independent_audit": ia, "independent_audit_placebo": ia_pbo,
                 "gate": gate_legs(bs, pbo_net)}
    R["base"]["gate_pass"] = all(R["base"]["gate"].values())
    dump("BASE", ext_full)
    dump("BASE_PLACEBO", pbo)
    print(f"BASE ext: trades={bs['trades']} net={bs['net']} JM={bs['jan_may']} "
          f"JO={bs['jun_oct']} Oct={bs['october']} breadth={bs['breadth']}/25 "
          f"extop3={bs['extop3']['net']} placebo={pbo_net} "
          f"gate={R['base']['gate_pass']} audit={ia}", flush=True)

    # ---- neighbourhood ----
    R["cells"] = {}
    for tag, cell in CELLS.items():
        if tag == "O2-BASE":
            continue
        tr, ad_c = run_cell("ext", cell, MONTHS)
        s = stats(tr)
        ia_c = independent_audit("ext", cell, tr)
        legs = gate_legs(s, None)
        legs.pop("placebo_beaten")
        entry = {"audit_builtin": ad_c, "stats": s,
                 "independent_audit": ia_c, "gate_legs_no_placebo": legs}
        # full gate only if every non-placebo leg passes
        if all(legs.values()):
            pb, ad_pb = run_cell("ext", cell, MONTHS, lag=True)
            pb_net = round(sum(t["net"] for t in pb), 2)
            entry["placebo"] = {"trades": len(pb), "net": pb_net,
                                "audit_builtin": ad_pb,
                                "independent_audit":
                                    independent_audit("ext", cell, pb, lag=True)}
            entry["gate"] = gate_legs(s, pb_net)
            entry["gate_pass"] = all(entry["gate"].values())
            dump(tag + "_PLACEBO", pb)
        R["cells"][tag] = entry
        dump(tag, tr)
        print(f"{tag}: trades={s['trades']} net={s['net']} JM={s['jan_may']} "
              f"JO={s['jun_oct']} Oct={s['october']} breadth={s['breadth']}/25 "
              f"extop3={s['extop3']['net']} audit={ia_c}", flush=True)

    json.dump(R, open(RESULTS_F, "w"), indent=1)
    print("SAVED", RESULTS_F, flush=True)
    print("DONE run", flush=True)


if __name__ == "__main__":
    main()
