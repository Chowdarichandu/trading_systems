#!/usr/bin/env python3
"""LINE M2 — root-cause diagnosis of the H1 HIT-1 cell.
Cell: 10:00 | thr 0.5% | follow | sig | T125/S065 | all (home 25).
Reproduces anchors from the H1 engine, then compares the October
population vs Jan-Sep on ex-ante dimensions only.
Equity cash, paper only, real Rs0, provisional per 100 shares, Rs40/trade.
"""
import csv, json, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("H1", f"{BASE}/stocks_H1.py")
H1 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["H1"]
spec.loader.exec_module(H1)
sys.argv = _argv
M = H1.M

KEY = "10:00|0.5|follow|sig|T125/S065|all"
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
JAN_SEP = ALL_MONTHS[:9]


def band(pm):
    a = abs(pm)
    if a < 0.75:
        return "0.50-0.75"
    if a < 1.0:
        return "0.75-1.00"
    return ">=1.00"


def ebucket(t):
    h = int(t[:2]) * 60 + int(t[3:5])
    if h < 10 * 60 + 30:
        return "10:00-10:30"
    if h < 11 * 60:
        return "10:30-11:00"
    if h < 12 * 60:
        return "11:00-12:00"
    if h < 13 * 60:
        return "12:00-13:00"
    if h < 14 * 60:
        return "13:00-14:00"
    return "14:00+"


def stats(trades):
    n = len(trades)
    net = round(sum(t["net"] for t in trades), 2)
    return {"trades": n, "net": net,
            "exp": round(net / n, 2) if n else None,
            "win_pct": round(100.0 * sum(1 for t in trades if t["net"] > 0) / n, 1) if n else None}


def split(trades, keyfn):
    g = defaultdict(list)
    for t in trades:
        g[keyfn(t)].append(t)
    return {k: stats(v) for k, v in sorted(g.items())}


def main():
    H1.ensure_prep()
    ns = M.get_ns(H1.WHICH)
    trades = H1.run_cell(KEY, ALL_MONTHS)
    placebo = H1.run_cell(KEY, JAN_SEP, lag=True)

    oct_t = [t for t in trades if t["date"].startswith("2026-10")]
    js_t = [t for t in trades if not t["date"].startswith("2026-10")]
    jm_t = [t for t in trades if t["date"][:7] <= "2026-05"]
    junsep_t = [t for t in trades if "2026-06" <= t["date"][:7] <= "2026-09"]

    # ---- anchors ----
    anch = {
        "oct": stats(oct_t), "jan_sep": stats(js_t),
        "jan_may": stats(jm_t), "jun_sep": stats(junsep_t),
        "placebo_jan_sep": stats(placebo),
        "oct_breadth": len({t["symbol"] for t in oct_t
                            if sum(x["net"] for x in oct_t
                                   if x["symbol"] == t["symbol"]) > 0}),
        "audit": dict(H1._AUDIT),
    }
    anch["oct_event"] = stats([t for t in oct_t if t["event"] == "event_window"])
    anch["oct_noevent"] = stats([t for t in oct_t if t["event"] == "no_event"])
    print("ANCHORS:", json.dumps(anch, indent=1), flush=True)
    assert anch["oct"]["trades"] == 182 and abs(anch["oct"]["net"] - 34124.43) < 0.01, "OCT anchor FAIL"
    assert anch["jan_sep"]["trades"] == 1431 and abs(anch["jan_sep"]["net"] + 63538.43) < 0.01, "JANSEP anchor FAIL"
    assert abs(anch["jan_may"]["net"] + 38658.84) < 0.01, "JM anchor FAIL"
    assert abs(anch["jun_sep"]["net"] + 24879.59) < 0.01, "JS anchor FAIL"
    assert abs(anch["placebo_jan_sep"]["net"] + 18135.89) < 0.01, "PBO anchor FAIL"
    print("ALL ANCHORS PASS", flush=True)

    # ---- enrich trades ----
    for t in trades:
        t["regime"] = "below50" if H1.below50(t["date"]) else "above50"
        t["band"] = band(t["premove_pct"])
        t["ebucket"] = ebucket(t["entry_time"])
        t["month"] = t["date"][:7]

    # ---- monthly volatility context ----
    # mean stock ADR% per month from daily rows; Nifty daily range% per month
    adr = defaultdict(list)
    for sym in ns["SYMBOLS"]:
        for d in ns["stocks"][sym][1]:
            dt = d["date"][:10]
            if dt[:7] in ALL_MONTHS and d["close"]:
                adr[dt[:7]].append(100.0 * (d["high"] - d["low"]) / d["close"])
    nrows = []
    with open(f"{BASE}/data/progressive/NIFTY/spot_daily.csv") as f:
        for r in csv.DictReader(f):
            nrows.append(r)
    nadr = defaultdict(list)
    for r in nrows:
        m = r["date"][:7]
        if m in ALL_MONTHS:
            nadr[m].append(100.0 * (float(r["high"]) - float(r["low"])) / float(r["close"]))
    month_ctx = {}
    mstats = split(trades, lambda t: t["month"])
    for m in ALL_MONTHS:
        month_ctx[m] = {"stock_adr_pct": round(sum(adr[m]) / len(adr[m]), 3),
                        "nifty_range_pct": round(sum(nadr[m]) / len(nadr[m]), 3),
                        "cell": mstats.get(m)}
    print("MONTH CONTEXT:", json.dumps(month_ctx, indent=1), flush=True)
    # correlation: monthly cell expectancy vs monthly stock ADR
    xs, ys = [], []
    for m in ALL_MONTHS:
        c = month_ctx[m]["cell"]
        if c and c["exp"] is not None:
            xs.append(month_ctx[m]["stock_adr_pct"]); ys.append(c["exp"])
    n = len(xs); mx = sum(xs) / n; my = sum(ys) / n
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    vx = sum((x - mx) ** 2 for x in xs); vy = sum((y - my) ** 2 for y in ys)
    corr = round(cov / (vx * vy) ** 0.5, 3) if vx and vy else None
    print(f"corr(month ADR%, month expectancy) = {corr} over {n} months", flush=True)

    periods = {"OCT": oct_t, "JAN_SEP": js_t, "JAN_MAY": jm_t, "JUN_SEP": junsep_t}
    diag = {"anchors": anch, "month_ctx": month_ctx, "corr_adr_exp": corr}
    dims = {
        "direction": lambda t: t["dir"],
        "setup": lambda t: t["setup"],
        "entry_bucket": lambda t: t["ebucket"],
        "band": lambda t: t["band"],
        "regime": lambda t: t["regime"],
        "event": lambda t: t["event"],
        "exit_reason": lambda t: t["exit_reason"],
        "leg": lambda t: t["leg"],
        "symbol": lambda t: t["symbol"],
        "move_sign": lambda t: "up" if t["premove_pct"] > 0 else "down",
    }
    for name, fn in dims.items():
        diag[name] = {p: split(ts, fn) for p, ts in periods.items()}
        print(f"\n== {name} ==")
        for p in ("OCT", "JAN_SEP", "JAN_MAY", "JUN_SEP"):
            print(p, json.dumps(diag[name][p]), flush=True)

    # ---- cross: direction x band, direction x regime (trade-level separator hunt) ----
    for name, fn in {"dir_x_band": lambda t: f"{t['dir']}|{t['band']}",
                     "dir_x_regime": lambda t: f"{t['dir']}|{t['regime']}",
                     "setup_x_dir": lambda t: f"{t['setup']}|{t['dir']}",
                     "band_x_regime": lambda t: f"{t['band']}|{t['regime']}"}.items():
        diag[name] = {p: split(ts, fn) for p, ts in periods.items()}
        print(f"\n== {name} ==")
        for p in ("OCT", "JAN_SEP"):
            print(p, json.dumps(diag[name][p]), flush=True)

    with open(f"{BASE}/stocks_M2_diag.json", "w") as f:
        json.dump(diag, f, indent=1)
    cols = ["date", "symbol", "dir", "setup", "leg", "round", "sig_time",
            "entry_time", "entry", "exit_reason", "exit_time", "exit",
            "gross", "net", "event", "premove_pct", "meas_time", "regime",
            "band", "ebucket"]
    with open(f"{BASE}/stocks_M2_base_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
            w.writerow({c: t.get(c) for c in cols})
    print("\nWROTE stocks_M2_diag.json + stocks_M2_base_trades.csv", flush=True)
    print("audit:", H1._AUDIT, flush=True)


if __name__ == "__main__":
    main()
