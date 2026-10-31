#!/usr/bin/env python3
"""LINE G1 — state-gate extensions. Cells frozen in
stocks_G1_frozen.md BEFORE scoring. Machinery: stocks_H1 builders
(fixed-time entries), H1.below50 regime map, stocks_M2_fix for the
F4 placebo rebuild. Timing audit + per-cell lag-placebo IN THIS
RUN. Paper only, real Rs0, provisional per 100 shares, Rs40/trade,
home 25 only, Jan-Oct 2026.
"""
import csv, json, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    _argv = sys.argv
    sys.argv = [name]
    spec.loader.exec_module(mod)
    sys.argv = _argv
    return mod

H1 = load("H1", f"{BASE}/stocks_H1.py")
M = H1.M
COST = 40.0
TP, SP = 1.25, 0.65
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
JS_MONTHS = ALL_MONTHS[:9]

def all_days(months):
    ns = M.get_ns(H1.WHICH)
    return sorted({d for (s, d) in ns["DAYCTX"]
                   if any(d.startswith(m) for m in months)})

def band(trades, lo=0.5, hi=1.0):
    return [t for t in trades if lo <= abs(t["premove_pct"]) < hi]

def b50(trades):
    return [t for t in trades if H1.below50(t["date"])]

def a50(trades):
    return [t for t in trades if not H1.below50(t["date"])]

def ev(trades):
    return [t for t in trades if t["event"] == "event_window"]

def ne(trades):
    return [t for t in trades if t["event"] == "no_event"]

def summarize(trades):
    months = {}
    for m in ALL_MONTHS:
        sel = [t for t in trades if t["date"].startswith(m)]
        months[m] = {"trades": len(sel),
                     "net": round(sum(t["net"] for t in sel), 2)}
    per_stock = {s: 0.0 for s in M.get_ns(H1.WHICH)["SYMBOLS"]}
    for t in trades:
        per_stock[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {
        "trades": len(trades), "net": net,
        "jan_may": round(sum(v["net"] for m, v in months.items() if m <= "2026-05"), 2),
        "jun_sep": round(sum(v["net"] for m, v in months.items() if "2026-06" <= m <= "2026-09"), 2),
        "jan_sep": round(sum(v["net"] for m, v in months.items() if m <= "2026-09"), 2),
        "october": months["2026-10"]["net"],
        "months": months,
        "months_green": sum(1 for v in months.values() if v["net"] > 0),
        "breadth": sum(1 for v in per_stock.values() if v > 0),
        "exp": round(net / len(trades), 2) if trades else None,
        "per_stock": {k: round(v, 2) for k, v in
                      sorted(per_stock.items(), key=lambda kv: -kv[1])},
    }

def fixed_build(T, thr, dirmode, days, lag=False):
    a0 = dict(H1._AUDIT)
    tr = H1.collect_window(days, T, thr, dirmode, "fixed", TP, SP, lag=lag)
    a1 = H1._AUDIT
    return tr, {"trades": a1["trades"] - a0["trades"],
                "violations": a1["violations"] - a0["violations"]}

def indep_audit_fixed(trades, T, thr, dirmode, banded=False, lag=False):
    """Re-derive pm from raw bars; verify threshold/band, direction,
    and that the entry bar is exactly the first bar >= T."""
    ns = M.get_ns(H1.WHICH)
    days_sorted = sorted({d for (s, d) in ns["DAYCTX"]})
    prev_of = {d: days_sorted[i - 1] for i, d in enumerate(days_sorted) if i > 0}
    viol = 0
    pm_cache = {}
    for t in trades:
        qday = prev_of.get(t["date"]) if lag else t["date"]
        key = (t["symbol"], qday)
        if key not in pm_cache:
            ctx = ns["DAYCTX"].get(key)
            pm_cache[key] = M.premove(ctx["candles"], T) if ctx else None
        pm = pm_cache[key]
        if pm is None or abs(pm) < thr - 1e-9:
            viol += 1
            continue
        if banded and abs(pm) >= 0.01 - 1e-12:
            viol += 1
            continue
        move = 1 if pm > 0 else -1
        want = move if dirmode == "follow" else -move
        ctx_t = ns["DAYCTX"].get((t["symbol"], t["date"]))
        first_bar = next((c["time"] for c in ctx_t["candles"]
                          if c["time"] >= T), None) if ctx_t else None
        if (("LONG" if want == 1 else "SHORT") != t["dir"]
                or t["entry_time"] != first_bar):
            viol += 1
    return {"checked": len(trades), "violations": viol}

def indep_audit_sd(trades, want_event, lag=False):
    """S-d: verify each trade's day is below50, its 10:00 pm is in
    [0.5%,1.0%) (lag day for placebo), and its event status matches
    the DAYCTX source and the cell restriction."""
    ns = M.get_ns(H1.WHICH)
    days_sorted = sorted({d for (s, d) in ns["DAYCTX"]})
    prev_of = {d: days_sorted[i - 1] for i, d in enumerate(days_sorted) if i > 0}
    viol = 0
    pm_cache = {}
    for t in trades:
        ok = True
        if not H1.below50(t["date"]):
            ok = False
        ctx_t = ns["DAYCTX"].get((t["symbol"], t["date"]))
        if ctx_t is None or ctx_t["event_status"] != t["event"]:
            ok = False
        if t["event"] != want_event:
            ok = False
        qday = prev_of.get(t["date"]) if lag else t["date"]
        key = (t["symbol"], qday)
        if key not in pm_cache:
            ctx = ns["DAYCTX"].get(key)
            pm_cache[key] = M.premove(ctx["candles"], "10:00") if ctx else None
        pm = pm_cache[key]
        if pm is None or not (0.005 - 1e-9 <= abs(pm) < 0.01 - 1e-12):
            ok = False
        if not ok:
            viol += 1
    return {"checked": len(trades), "violations": viol}

def gate(s, placebo_js_net, audit_ok):
    legs = {
        "jan_oct_gt_0": s["net"] > 0,
        "both_halves_gt_0": s["jan_may"] > 0 and s["jun_sep"] > 0,
        "october_gt_0": s["october"] > 0,
        "breadth_ge_15": s["breadth"] >= 15,
        "beats_own_placebo": placebo_js_net is not None and s["jan_sep"] > placebo_js_net,
        "audit_clean": audit_ok,
    }
    legs["PASS"] = all(legs.values())
    return legs

def dump(tag, trades):
    if not trades:
        return
    with open(f"{BASE}/stocks_G1_{tag}_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow(t)

def main():
    H1.ensure_prep()
    days_all = all_days(ALL_MONTHS)
    days_js = all_days(JS_MONTHS)
    R = {"anchors": {}, "cells": {}}

    sa_raw, sa_aud = fixed_build("11:00", 0.01, "fade", days_all)
    sa_pbo_raw, sa_pbo_aud = fixed_build("11:00", 0.01, "fade", days_js, lag=True)
    sb_raw, sb_aud = fixed_build("10:00", 0.005, "fade", days_all)
    sb_pbo_raw, sb_pbo_aud = fixed_build("10:00", 0.005, "fade", days_js, lag=True)
    sc_raw, sc_aud = fixed_build("10:00", 0.005, "follow", days_all)
    sc_pbo_raw, sc_pbo_aud = fixed_build("10:00", 0.005, "follow", days_js, lag=True)

    sa_all_sum = summarize(sa_raw)
    R["anchors"]["SA_ALL_home_fade"] = {
        "got_net": sa_all_sum["net"], "want_net": 4243.18,
        "got_trades": sa_all_sum["trades"], "want_trades": 1073,
        "got_october": sa_all_sum["october"], "want_october": 341.29}
    assert sa_all_sum["net"] == 4243.18 and sa_all_sum["trades"] == 1073, \
        f"SA anchor mismatch: {R['anchors']['SA_ALL_home_fade']}"
    print("ANCHOR SA-ALL ok:", R["anchors"]["SA_ALL_home_fade"], flush=True)

    fixed_cells = {
        "SA-ALL": (sa_raw, sa_pbo_raw, sa_aud, sa_pbo_aud,
                   lambda x: x, "11:00", 0.01, "fade", False),
        "SA-B50": (sa_raw, sa_pbo_raw, sa_aud, sa_pbo_aud,
                   b50, "11:00", 0.01, "fade", False),
        "SA-A50": (sa_raw, sa_pbo_raw, sa_aud, sa_pbo_aud,
                   a50, "11:00", 0.01, "fade", False),
        "SB-ALL": (sb_raw, sb_pbo_raw, sb_aud, sb_pbo_aud,
                   band, "10:00", 0.005, "fade", True),
        "SB-B50": (sb_raw, sb_pbo_raw, sb_aud, sb_pbo_aud,
                   lambda x: b50(band(x)), "10:00", 0.005, "fade", True),
        "SC-ALL": (sc_raw, sc_pbo_raw, sc_aud, sc_pbo_aud,
                   band, "10:00", 0.005, "follow", True),
        "SC-A50": (sc_raw, sc_pbo_raw, sc_aud, sc_pbo_aud,
                   lambda x: a50(band(x)), "10:00", 0.005, "follow", True),
    }
    for name, (raw, pbo_raw, aud, pbo_aud, filt, T, thr, dirmode, banded) \
            in fixed_cells.items():
        tr = filt(raw)
        pbo = filt(pbo_raw)
        s = summarize(tr)
        ps = summarize(pbo)
        ia = indep_audit_fixed(tr, T, thr, dirmode, banded=banded)
        ia_p = indep_audit_fixed(pbo, T, thr, dirmode, banded=banded, lag=True)
        audit_ok = (aud["violations"] == 0 and ia["violations"] == 0)
        R["cells"][name] = {
            "book": s, "placebo_jan_sep": {"trades": ps["trades"],
                                           "net": ps["jan_sep"]},
            "audit_builtin_raw_build": aud, "audit_builtin_placebo_build": pbo_aud,
            "indep_audit": ia, "indep_audit_placebo": ia_p,
            "gate": gate(s, ps["jan_sep"], audit_ok)}
        dump(name.replace("-", "_"), tr)
        print(f"{name}: tr={s['trades']} net={s['net']} JM={s['jan_may']} "
              f"JS={s['jun_sep']} Oct={s['october']} br={s['breadth']}/25 "
              f"green={s['months_green']}/10 pboJS={ps['jan_sep']} "
              f"audit={ia} gate={R['cells'][name]['gate']['PASS']}", flush=True)

    # ---------------- S-d: M2 F4 book restrictions ----------------
    with open(f"{BASE}/stocks_M2_F4_trades.csv") as f:
        f4 = [{**r, "net": float(r["net"]), "gross": float(r["gross"]),
               "premove_pct": float(r["premove_pct"])} for r in csv.DictReader(f)]
    f4_sum = summarize(f4)
    R["anchors"]["F4_book"] = {"got_net": f4_sum["net"], "want_net": 42418.91,
                               "got_trades": f4_sum["trades"], "want_trades": 717,
                               "got_october": f4_sum["october"], "want_october": 36166.23}
    assert f4_sum["net"] == 42418.91 and f4_sum["trades"] == 717, \
        f"F4 anchor mismatch: {R['anchors']['F4_book']}"
    print("ANCHOR F4 ok:", R["anchors"]["F4_book"], flush=True)

    M2F = load("M2F", f"{BASE}/stocks_M2_fix.py")
    M2F.H1.ensure_prep()  # M2_fix carries its own H1 instance; prep its regime map
    f4_pbo = M2F.collect2(days_js, {"band_hi": 1.0, "regime": "below50"}, lag=True)
    f4_pbo_js = round(sum(t["net"] for t in f4_pbo), 2)
    R["anchors"]["F4_placebo_jan_sep"] = {"got": f4_pbo_js, "want": -906.88,
                                          "trades": len(f4_pbo)}
    print("ANCHOR F4 placebo:", R["anchors"]["F4_placebo_jan_sep"], flush=True)

    for name, filt, want_event in (("SD-EV", ev, "event_window"),
                                   ("SD-NE", ne, "no_event")):
        tr = filt(f4)
        pbo = filt(f4_pbo)
        s = summarize(tr)
        ps_js = round(sum(t["net"] for t in pbo), 2)
        ia = indep_audit_sd(tr, want_event)
        ia_p = indep_audit_sd(pbo, want_event, lag=True)
        audit_ok = ia["violations"] == 0 and ia_p["violations"] == 0
        R["cells"][name] = {
            "book": s, "placebo_jan_sep": {"trades": len(pbo), "net": ps_js},
            "indep_audit": ia, "indep_audit_placebo": ia_p,
            "gate": gate(s, ps_js, audit_ok)}
        dump(name.replace("-", "_"), tr)
        print(f"{name}: tr={s['trades']} net={s['net']} JM={s['jan_may']} "
              f"JS={s['jun_sep']} Oct={s['october']} br={s['breadth']}/25 "
              f"green={s['months_green']}/10 pboJS={ps_js} "
              f"audit={ia} gate={R['cells'][name]['gate']['PASS']}", flush=True)

    json.dump(R, open(f"{BASE}/stocks_G1_results.json", "w"), indent=1)
    print("WROTE stocks_G1_results.json", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
