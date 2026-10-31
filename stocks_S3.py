#!/usr/bin/env python3
"""LINE S3 — Volatility-Compression Breakout (NR7 / Inside Day ->
next-day 5-min close-break trigger). Cells frozen in
stocks_S3_frozen.md BEFORE scoring. CONTROLS-FIRST: the timing audit
(entry strictly after pattern-day close; entry = bar after trigger
bar) is asserted over ALL trades in the SAME run as scoring; the run
aborts before printing scores if the audit fails. Equity cash,
LONG/SHORT, paper only, real Rs0. Provisional per 100 shares,
net = gross - Rs40/trade. Window Jan-Oct 2026 (trade day in window).
Pooled 50 primary, home/ext splits.

Exits via the programme's frozen replay_plain (stop-first, 15:10
square-off) from stocks_tuning_universe.py.
"""
import csv, json, sys
import importlib.util
from collections import defaultdict

BASE = "/home/hatch/workspace/trading"
spec = importlib.util.spec_from_file_location("univ", f"{BASE}/stocks_tuning_universe.py")
U = importlib.util.module_from_spec(spec)
_argv = sys.argv
sys.argv = ["univ"]
spec.loader.exec_module(U)
sys.argv = _argv

COST = 40.0
OLD_SYMS = ["GODREJCP", "GLENMARK", "ITC", "RECLTD", "TVSMOTOR", "UNITDSPR", "OBEROIRLTY",
            "NTPC", "INDUSTOWER", "KALYANKJIL", "HDFCBANK", "NHPC", "PFC", "IRCTC", "WIPRO",
            "NATIONALUM", "VEDL", "HINDCOPPER", "HINDZINC", "HINDALCO", "TATASTEEL",
            "ASTRAL", "BDL", "OIL", "HINDUNILVR"]
EXT_SYMS = ["RELIANCE", "TCS", "ICICIBANK", "INFY", "BHARTIARTL", "SBIN", "LT",
            "AXISBANK", "KOTAKBANK", "BAJFINANCE", "HCLTECH", "MARUTI", "SUNPHARMA",
            "TITAN", "M&M", "ULTRACEMCO", "NESTLEIND", "POWERGRID", "ONGC", "COALINDIA",
            "JSWSTEEL", "GRASIM", "CIPLA", "DRREDDY", "EICHERMOT"]
WIN_START, WIN_END = "2026-01-01", "2026-10-31"
RESULTS_F = f"{BASE}/stocks_S3_results.json"
UNIV = [("home", "progressive", OLD_SYMS), ("ext", "progressive_ext", EXT_SYMS)]
EXITS = {"T125": (1.25, 0.50), "T10": (1.00, 0.50)}


def load_days(data_dir, sym):
    path = f"{BASE}/data/{data_dir}/{sym}/spot_5m.csv"
    days = {}
    with open(path) as f:
        for r in csv.DictReader(f):
            d = r["timestamp"][:10]
            days.setdefault(d, []).append(
                {"time": r["timestamp"][11:16], "open": float(r["open"]),
                 "high": float(r["high"]), "low": float(r["low"]),
                 "close": float(r["close"])})
    for d in days:
        days[d].sort(key=lambda c: c["time"])
    return days


def daily(days):
    out = {}
    for d, cs in days.items():
        out[d] = {"open": cs[0]["open"], "high": max(c["high"] for c in cs),
                  "low": min(c["low"] for c in cs), "close": cs[-1]["close"]}
    return out


def patterns(dly):
    """Return dict date -> set of pattern tags ('A' NR7, 'B' inside)."""
    dates = sorted(dly)
    pat = {}
    for i, d in enumerate(dates):
        tags = set()
        rng = dly[d]["high"] - dly[d]["low"]
        if i >= 6 and all(rng <= dly[dates[k]]["high"] - dly[dates[k]]["low"]
                          for k in range(i - 6, i)):
            tags.add("A")
        if i >= 1:
            p = dly[dates[i - 1]]
            if dly[d]["high"] <= p["high"] and dly[d]["low"] >= p["low"]:
                tags.add("B")
        if tags:
            pat[d] = tags
    return pat


def run_cell(days, dly, pat, want, tp, sp, lag=1):
    """want: set of tags qualifying ('A', 'B', or {'A','B'} union).
    lag: sessions after D on which to trade (1 = real, 6 = placebo)."""
    dates = sorted(days)
    idx = {d: i for i, d in enumerate(dates)}
    trades = []
    for d, tags in pat.items():
        if not (tags & want):
            continue
        j = idx[d] + lag
        if j >= len(dates):
            continue
        td = dates[j]
        if not (WIN_START <= td <= WIN_END):
            continue
        hi, lo = dly[d]["high"], dly[d]["low"]
        candles = days[td]
        trig = None
        for k, c in enumerate(candles):
            if c["close"] > hi:
                trig = (k, 1)
                break
            if c["close"] < lo:
                trig = (k, -1)
                break
        if trig is None:
            continue
        k, sign = trig
        if k + 1 >= len(candles):
            continue
        entry_idx = k + 1
        entry = float(candles[entry_idx]["open"])
        er, ep, et, _j, gross = U.replay_plain(candles, entry_idx, sign, entry, tp, sp)
        trades.append({
            "pattern_date": d, "date": td, "dir": "LONG" if sign == 1 else "SHORT",
            "trig_time": candles[k]["time"], "entry_time": candles[entry_idx]["time"],
            "entry_idx": entry_idx, "trig_idx": k,
            "level_hi": round(hi, 2), "level_lo": round(lo, 2),
            "entry": round(entry, 2), "exit_reason": er, "exit_time": et,
            "exit": round(ep, 2), "gross": round(gross, 2),
            "net": round(gross - COST, 2)})
    return trades


def timing_audit(all_trades):
    """Assert over every trade of every cell. Returns violation count."""
    viol = 0
    for t in all_trades:
        if not (t["date"] > t["pattern_date"]):
            viol += 1
        if not (t["entry_idx"] == t["trig_idx"] + 1 and t["entry_time"] > t["trig_time"]):
            viol += 1
    return viol


def summ(trades, total_stocks, all_syms):
    net = round(sum(t["net"] for t in trades), 2)
    jm = round(sum(t["net"] for t in trades if t["date"][:7] <= "2026-05"), 2)
    jo = round(sum(t["net"] for t in trades if t["date"][:7] >= "2026-06"), 2)
    oct_ = round(sum(t["net"] for t in trades if t["date"][:7] == "2026-10"), 2)
    per = defaultdict(float)
    for t in trades:
        per[t["symbol"]] += t["net"]
    pos = sorted((v for v in per.values() if v > 0), reverse=True)
    breadth = sum(1 for s in all_syms if per.get(s, 0.0) > 0)
    top3 = round(100.0 * sum(pos[:3]) / net, 1) if net > 0 else None
    return {"trades": len(trades), "net": net, "jan_may": jm, "jun_oct": jo,
            "october": oct_, "breadth": breadth, "stocks_total": total_stocks,
            "exp_per_trade": round(net / len(trades), 2) if trades else 0.0,
            "top3_share_pct": top3,
            "per_stock": {s: round(per.get(s, 0.0), 2) for s in all_syms}}


def main():
    data = {}
    for uname, ddir, syms in UNIV:
        for sym in syms:
            days = load_days(ddir, sym)
            data[sym] = (uname, days, daily(days))
            data[sym] = (uname, days, data[sym][2], patterns(data[sym][2]))

    cells = [("S3-A1", {"A"}, "T125"), ("S3-A2", {"A"}, "T10"),
             ("S3-B1", {"B"}, "T125"), ("S3-B2", {"B"}, "T10"),
             ("S3-U1", {"A", "B"}, "T125"), ("S3-U2", {"A", "B"}, "T10")]
    results = {}
    cell_trades = {}
    audit_pool = []
    for cid, want, ex in cells:
        tp, sp = EXITS[ex]
        per_univ = {}
        pooled = []
        for uname, ddir, syms in UNIV:
            ts = []
            for sym in syms:
                _, days, dly, pat = data[sym]
                for t in run_cell(days, dly, pat, want, tp, sp, lag=1):
                    t["symbol"] = sym
                    ts.append(t)
            per_univ[uname] = summ(ts, 25, syms)
            pooled.extend(ts)
            audit_pool.extend(ts)
        results[cid] = {"config": {"pattern": sorted(want), "exits": ex},
                        "home": per_univ["home"], "ext": per_univ["ext"],
                        "pooled": summ(pooled, 50, OLD_SYMS + EXT_SYMS)}
        cell_trades[cid] = pooled

    viol = timing_audit(audit_pool)
    results["AUDIT"] = {"trades_checked": len(audit_pool), "violations": viol}
    print(f"TIMING AUDIT: {len(audit_pool)} trades checked, violations={viol}", flush=True)
    if viol:
        print("AUDIT FAILED — aborting before scores.", flush=True)
        sys.exit(1)

    for cid, *_ in cells:
        p = results[cid]["pooled"]
        h, e = results[cid]["home"], results[cid]["ext"]
        print(f"{cid}: pooled trades={p['trades']} net={p['net']} JM={p['jan_may']} "
              f"JO={p['jun_oct']} Oct={p['october']} breadth={p['breadth']}/50 "
              f"exp={p['exp_per_trade']} top3={p['top3_share_pct']} | "
              f"home net={h['net']} br={h['breadth']}/25 | ext net={e['net']} br={e['breadth']}/25",
              flush=True)
        flat = sorted(cell_trades[cid], key=lambda x: (x["date"], x["symbol"]))
        cols = ["pattern_date", "date", "symbol", "dir", "trig_time", "entry_time",
                "level_hi", "level_lo", "entry", "exit_time", "exit", "exit_reason",
                "gross", "net"]
        with open(f"{BASE}/stocks_S3_{cid}_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=cols)
            w.writeheader()
            for t in flat:
                w.writerow({c: t.get(c, "") for c in cols})

    best = max(cells, key=lambda c: results[c[0]]["pooled"]["net"])[0]
    want = {"S3-A1": {"A"}, "S3-A2": {"A"}, "S3-B1": {"B"}, "S3-B2": {"B"},
            "S3-U1": {"A", "B"}, "S3-U2": {"A", "B"}}[best]
    ex = results[best]["config"]["exits"]
    tp, sp = EXITS[ex]
    pooled_pl, audit_pl = [], []
    per_univ_pl = {}
    for uname, ddir, syms in UNIV:
        ts = []
        for sym in syms:
            _, days, dly, pat = data[sym]
            for t in run_cell(days, dly, pat, want, tp, sp, lag=6):
                t["symbol"] = sym
                ts.append(t)
        per_univ_pl[uname] = summ(ts, 25, syms)
        pooled_pl.extend(ts)
        audit_pl.extend(ts)
    viol_pl = timing_audit(audit_pl)
    results["PLACEBO"] = {"of_cell": best, "lag_sessions": 6,
                          "home": per_univ_pl["home"], "ext": per_univ_pl["ext"],
                          "pooled": summ(pooled_pl, 50, OLD_SYMS + EXT_SYMS),
                          "audit_violations": viol_pl}
    p = results["PLACEBO"]["pooled"]
    print(f"PLACEBO of {best} (D+6): trades={p['trades']} net={p['net']} JM={p['jan_may']} "
          f"JO={p['jun_oct']} Oct={p['october']} breadth={p['breadth']}/50 "
          f"audit_violations={viol_pl}", flush=True)

    json.dump(results, open(RESULTS_F, "w"), indent=1)
    print("BEST:", best, "pooled net", results[best]["pooled"]["net"], flush=True)
    print("DONE", flush=True)


if __name__ == "__main__":
    main()
