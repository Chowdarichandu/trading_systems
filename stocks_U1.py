#!/usr/bin/env python3
"""LINE U1 - score the frozen 11:00 fade on the broad universe.
Rule verbatim from stocks_U1_frozen.md; machinery is Line O1's
fixed-mode builder (stocks_O1.build_cell) so the code path is
identical to the O2 candidate's. Mode: score
"""
import csv, json, os, sys
from collections import defaultdict
import importlib.util

BASE = "/home/hatch/workspace/trading"
sys.path.insert(0, BASE)
spec = importlib.util.spec_from_file_location("O1", f"{BASE}/stocks_O1.py")
O1 = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["O1"]
spec.loader.exec_module(O1)
sys.argv = _argv
M = O1.M

BARS = f"{BASE}/data/u1/bars"
EXT25 = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN",
         "LT", "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HCLTECH", "MARUTI",
         "SUNPHARMA", "TITAN", "M&M", "ULTRACEMCO", "NESTLEIND", "POWERGRID",
         "ONGC", "COALINDIA", "JSWSTEEL", "GRASIM", "CIPLA", "DRREDDY",
         "EICHERMOT"]
T, THR, TP, SP = "11:00", 0.01, 1.25, 0.65


def load_bars():
    """-> {sym: {day: [bar,...]}} with bar dicts in cache format."""
    out = {}
    for fn in sorted(os.listdir(BARS)):
        if not fn.endswith(".csv"):
            continue
        sym = fn[:-4]
        days = defaultdict(list)
        with open(f"{BARS}/{fn}") as f:
            for r in csv.DictReader(f):
                ts = r["timestamp"][:19]
                days[ts[:10]].append({"timestamp": ts, "time": ts[11:16],
                                      "open": float(r["open"]),
                                      "high": float(r["high"]),
                                      "low": float(r["low"]),
                                      "close": float(r["close"])})
        for d in days:
            days[d].sort(key=lambda b: b["time"])
        out[sym] = dict(days)
    return out


def usable(day_bars):
    if len(day_bars) < 70:
        return False
    times = {b["time"] for b in day_bars}
    return day_bars[0]["time"] == "09:15" and "15:10" in times


def stats_of(trades, window):
    ps = defaultdict(float)
    for t in trades:
        ps[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    pos = sorted(ps.values(), reverse=True)
    months = {}
    for m in sorted({t["date"][:7] for t in trades}):
        sel = [t for t in trades if t["date"][:7] == m]
        months[m] = {"trades": len(sel),
                     "net": round(sum(t["net"] for t in sel), 2)}
    h1d, h2d = set(window[:30]), set(window[30:])
    return {
        "trades": len(trades), "net": net,
        "months": months,
        "first30": {"days": [window[0], window[29]],
                    "net": round(sum(t["net"] for t in trades
                                     if t["date"] in h1d), 2),
                    "trades": sum(1 for t in trades if t["date"] in h1d)},
        "last30": {"days": [window[30], window[-1]],
                   "net": round(sum(t["net"] for t in trades
                                    if t["date"] in h2d), 2),
                   "trades": sum(1 for t in trades if t["date"] in h2d)},
        "breadth": sum(1 for v in ps.values() if v > 0),
        "stocks_traded": len(ps),
        "exp_per_trade": round(net / len(trades), 2) if trades else None,
        "top3_share_pct": round(100 * sum(pos[:3]) / net, 1) if net > 0 else None,
        "top10_share_pct": round(100 * sum(pos[:10]) / net, 1) if net > 0 else None,
        "best5": sorted(ps.items(), key=lambda kv: -kv[1])[:5],
        "worst5": sorted(ps.items(), key=lambda kv: kv[1])[:5],
        "per_stock": {k: round(v, 2) for k, v in ps.items()},
    }


def main():
    raw = load_bars()
    have = {s: d for s, d in raw.items() if d}
    use = {}
    for s, days in have.items():
        u = {d: b for d, b in days.items() if usable(b)}
        if u:
            use[s] = u
    cnt = defaultdict(int)
    for s, u in use.items():
        for d in u:
            cnt[d] += 1
    half = max(1, len(use) // 2)
    tdays = sorted(d for d, c in cnt.items()
                   if c >= half and d <= "2026-10-30")
    window = tdays[-60:]
    wset = set(window)
    print(f"symbols with any data={len(have)} usable={len(use)} "
          f"trading days={len(tdays)} window={window[0]}..{window[-1]} "
          f"({len(window)}d)", flush=True)

    DAYCTX = {}
    for s, u in use.items():
        for d, bars in u.items():
            if d in wset:
                candles = [b for b in bars if b["time"] >= "09:30"]
                if candles:
                    DAYCTX[(s, d)] = {"candles": candles,
                                      "event_status": "no_event"}
    ns = {"DAYCTX": DAYCTX}
    syms = sorted({s for (s, _) in DAYCTX})

    def run(dirmode):
        a0 = dict(O1._AUDIT)
        trades = []
        for s in syms:
            for d in window:
                trades.extend(O1.build_cell(ns, s, d, T, THR, dirmode,
                                            "fixed", TP, SP))
        a1 = O1._AUDIT
        return trades, {"trades": a1["trades"] - a0["trades"],
                        "violations": a1["violations"] - a0["violations"]}

    fade, aud_f = run("fade")
    follow, aud_l = run("follow")

    def indep(trades, dirmode):
        viol = checked = 0
        pm_cache = {}
        for t in trades:
            key = (t["symbol"], t["date"])
            if key not in pm_cache:
                pm_cache[key] = M.premove(DAYCTX[key]["candles"], T)
            pm = pm_cache[key]
            checked += 1
            candles = DAYCTX[key]["candles"]
            fb = next((c for c in candles if c["time"] >= T), None)
            want = ("SHORT" if pm > 0 else "LONG") if dirmode == "fade" \
                else ("LONG" if pm > 0 else "SHORT")
            if (pm is None or abs(pm) < THR - 1e-9 or fb is None
                    or t["dir"] != want or t["entry_time"] != fb["time"]
                    or abs(t["entry"] - fb["open"]) > 0.011):
                viol += 1
        return {"checked": checked, "violations": viol}

    ia_f, ia_l = indep(fade, "fade"), indep(follow, "follow")
    print(f"FADE trades={len(fade)} audit-builtin={aud_f} indep={ia_f}",
          flush=True)
    print(f"FOLLOW trades={len(follow)} audit-builtin={aud_l} indep={ia_l}",
          flush=True)

    sf, sl = stats_of(fade, window), stats_of(follow, window)
    ext_trades = [t for t in fade if t["symbol"] in set(EXT25)]
    se = stats_of(ext_trades, window)
    R = {"window": {"start": window[0], "end": window[-1],
                    "days": len(window),
                    "first30": [window[0], window[29]],
                    "last30": [window[30], window[-1]]},
         "universe": {"symbols_any_data": len(have),
                      "symbols_usable": len(use),
                      "symbols_in_window": len(syms)},
         "audit": {"fade_builtin": aud_f, "follow_builtin": aud_l,
                   "fade_independent": ia_f, "follow_independent": ia_l},
         "fade": sf, "follow": sl, "ext25_subset": se}
    json.dump(R, open(f"{BASE}/stocks_U1_results.json", "w"), indent=1)

    cols = ["date", "symbol", "dir", "setup", "leg", "round", "sig_time",
            "entry_time", "entry", "exit_time", "exit", "exit_reason",
            "gross", "net", "event", "premove_pct", "meas_time"]
    for tag, tr in (("fade", fade), ("follow", follow)):
        with open(f"{BASE}/stocks_U1_{tag}_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for t in sorted(tr, key=lambda x: (x["date"], x["symbol"])):
                w.writerow({c: t.get(c, "") for c in cols})
    print(json.dumps({k: R[k] for k in ("window", "universe", "audit")},
                     indent=1), flush=True)
    print(f"FADE net={sf['net']} trades={sf['trades']} months={sf['months']} "
          f"H1={sf['first30']} H2={sf['last30']} breadth="
          f"{sf['breadth']}/{len(use)} exp={sf['exp_per_trade']} "
          f"top3={sf['top3_share_pct']}% top10={sf['top10_share_pct']}% "
          f"worst={sf['worst5'][:1]}", flush=True)
    print(f"FOLLOW net={sl['net']} trades={sl['trades']}", flush=True)
    print(f"EXT25-in-U1 net={se['net']} trades={se['trades']} "
          f"months={se['months']} breadth={se['breadth']}/25", flush=True)
    print("DONE score", flush=True)


if __name__ == "__main__":
    main()
