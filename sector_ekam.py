#!/usr/bin/env python3
"""SECTOR-ADDITIONS TEST — EKAM intraday (CAND-T5 / S2) on the enlarged
37-name universe (frozen 25 + 12 sector additions) vs the frozen-25
controls. Frozen machinery imported verbatim (same route as
wide100_ekam.py): ekam_intraday_stocks_build / _r2_build / _r5_build.
Only changes: symbol list (37) and data root (data/wide100, which holds
all 37 in the frozen layout). Control mode first: the 25-name run on
the default stores must reproduce the published totals exactly or the
script stops. Research only.
Basis: equity cash intraday, per 100 shares PROVISIONAL, Rs40/trade."""
import csv, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/trading")
import ekam_intraday_stocks_build as r1
import ekam_intraday_stocks_r2_build as r2
import ekam_intraday_stocks_r5_build as r5

WS = r1.WS
CAND = r5.CAND
NOV_DATES = r2.NOV_DATES
FROZEN25 = list(r1.NAMES)
ADD12 = ["ULTRACEMCO", "LT", "SBILIFE", "APOLLOHOSP", "ICICIBANK", "SBIN",
         "RELIANCE", "INFY", "M&M", "BHARTIARTL", "SUNPHARMA", "TITAN"]
NAMES37 = FROZEN25 + ADD12
TARGETS = {"CAND-T5": {2025: 62164.57, 2026: 63883.60, "nov": 24528.65},
           "S2": {2025: 45300.64, 2026: 72605.30, "nov": 20662.60}}


def max_drawdown(nets):
    cum = peak = dd = 0.0
    for x in nets:
        cum += x
        peak = max(peak, cum)
        dd = min(dd, cum - peak)
    return round(dd, 2)


def window_stats(ctxs, nets, pred):
    idx = [i for i, t in enumerate(ctxs) if pred(t)]
    sub = [nets[i] for i in idx]
    if not sub:
        return dict(trades=0, net=0.0, wr=None, ex_top3=0.0, max_drawdown=0.0)
    wins = sum(1 for x in sub if x > 0)
    top3 = sum(sorted(sub, reverse=True)[:3])
    return dict(trades=len(sub), net=round(sum(sub), 2),
                wr=round(100.0 * wins / len(sub), 2),
                ex_top3=round(sum(sub) - top3, 2),
                max_drawdown=max_drawdown(sub))


def added_stats(ctxs, nets, pred):
    idx = [i for i, t in enumerate(ctxs)
           if pred(t) and ctxs[i]["sym"] in ADD12]
    sub = [nets[i] for i in idx]
    names = sorted({ctxs[i]["sym"] for i in idx})
    by_name = {}
    for i in idx:
        by_name[ctxs[i]["sym"]] = round(by_name.get(ctxs[i]["sym"], 0.0)
                                        + nets[i], 2)
    return dict(trades=len(sub), net=round(sum(sub), 2),
                names_traded=len(names), names=names, by_name=by_name)


def score(stocks, label):
    by_sym = {S["sym"]: S for S in stocks}
    daymap, _ = r5.collect_day_candidates(stocks)
    res = {}
    for name, sel in (("CAND-T5", r5.sel_s0), ("S2", r5.sel_s2)):
        ctxs = r5.contexts_from(daymap, by_sym, sel)
        nets = [r2.net_of(t, **CAND) for t in ctxs]
        yr = r2.year_rows(ctxs, nets)
        book = {"years": {}, "november": {}}
        for y in (2025, 2026):
            pred = (lambda yy: lambda t: t["date"][:4] == str(yy)
                    and t["date"] <= f"{yy}-10-31")(y)
            ws = window_stats(ctxs, nets, pred)
            ws["ex_top3"] = yr[y]["ex_top3"]
            book["years"][y] = dict(
                stats=ws, added=added_stats(ctxs, nets, pred))
        nov_pred = lambda t: t["date"] in NOV_DATES
        book["november"] = dict(
            stats=window_stats(ctxs, nets, nov_pred),
            added=added_stats(ctxs, nets, nov_pred))
        book["ctxs"] = ctxs
        book["nets"] = nets
        res[name] = book
        print(f"[{label}] {name}: 2025 {book['years'][2025]['stats']} | "
              f"2026 {book['years'][2026]['stats']} | "
              f"NOV {book['november']['stats']}", flush=True)
    return res


def load_stock_wide(sym):
    import numpy as np
    path = os.path.join(WS, "data", "wide100", sym, "spot_5m.csv")
    ts, o, h, l, c = [], [], [], [], []
    with open(path) as f:
        for r in csv.DictReader(f):
            ts.append(r["timestamp"]); o.append(float(r["open"]))
            h.append(float(r["high"])); l.append(float(r["low"]))
            c.append(float(r["close"]))
    return ts, np.array(o), np.array(h), np.array(l), np.array(c)


def main():
    # ---- control: frozen 25, default stores, published targets
    stocks25 = [r1.build_stock(s) for s in FROZEN25]
    ctl = score(stocks25, "CONTROL-25")
    ok = True
    for name in ("CAND-T5", "S2"):
        for y in (2025, 2026):
            got = ctl[name]["years"][y]["stats"]["net"]
            if got != TARGETS[name][y]:
                ok = False
                print(f"CONTROL MISS {name} {y}: got {got}, "
                      f"want {TARGETS[name][y]}")
        got = ctl[name]["november"]["stats"]["net"]
        if got != TARGETS[name]["nov"]:
            ok = False
            print(f"CONTROL MISS {name} NOV: got {got}, "
                  f"want {TARGETS[name]['nov']}")
    print("EKAM CONTROL:", "PASS — all six totals exact" if ok else "FAIL")
    if not ok:
        return 2
    # ---- enlarged: 37 names, wide100 root
    r1.load_stock = load_stock_wide
    stocks37 = [r1.build_stock(s) for s in NAMES37]
    enl = score(stocks37, "ENLARGED-37")
    out = {"control25": {}, "enlarged37": {}, "trades": []}
    for tag, res in (("control25", ctl), ("enlarged37", enl)):
        for name in ("CAND-T5", "S2"):
            b = res[name]
            out[tag][name] = {"years": b["years"], "november": b["november"]}
            if tag == "enlarged37":
                for t, n in zip(b["ctxs"], b["nets"]):
                    out["trades"].append(dict(
                        book=f"EKAM-{name}", run="enlarged37",
                        date=t["date"], sym=t["sym"], side=t["side"],
                        entry=round(t["E"], 2), net=round(n, 2),
                        added=t["sym"] in ADD12))
    json.dump(out, open(f"{WS}/sector_ekam_results.json", "w"), indent=1)
    print("WROTE sector_ekam_results.json", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
