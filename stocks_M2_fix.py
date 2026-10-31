#!/usr/bin/env python3
"""LINE M2 — fix loop scoring. Families frozen in stocks_M2_frozen.md
BEFORE this ran. Each family is REBUILT with the H1 machinery
(sig-mode build mirrored from stocks_H1.build_cell, with the
family's qualification gate added) over the full Jan-Oct 2026,
plus its own lag-placebo on Jan-Sep. Paper only, real Rs0,
provisional per 100 shares, Rs40/trade, home 25 only.
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
M, U = H1.M, H1.U
COST = 40.0
T, TP, SP = "10:00", 1.25, 0.65
ALL_MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]

# prior-day Nifty range% map (range of the previous Nifty row)
_rows = []
with open(f"{BASE}/data/progressive/NIFTY/spot_daily.csv") as f:
    for r in csv.DictReader(f):
        _rows.append((r["date"][:10], float(r["high"]), float(r["low"]),
                      float(r["close"])))
_rows.sort()
PREV_RANGE = {}
for i in range(1, len(_rows)):
    d, h, l, c = _rows[i - 1]
    PREV_RANGE[_rows[i][0]] = 100.0 * (h - l) / c if c else 0.0

_AUDIT = {"trades": 0, "violations": 0}

FAMILIES = {
    "F1_band_cap": {"band_hi": 1.0},
    "F2_regime_below50": {"regime": "below50"},
    "F3_volgate_prevNiftyRange>=1.0": {"volgate": 1.0},
    "F4_state_gate": {"band_hi": 1.0, "regime": "below50"},
}


def build2(ns, sym, day, cfg, pm_override=None):
    ctx = ns["DAYCTX"].get((sym, day))
    if ctx is None:
        return []
    if cfg.get("regime") == "below50" and not H1.below50(day):
        return []
    if cfg.get("volgate") is not None:
        pr = PREV_RANGE.get(day)
        if pr is None or pr < cfg["volgate"]:
            return []
    candles = ctx["candles"]
    pm = pm_override if pm_override is not None else M.premove(candles, T)
    if pm is None or abs(pm) < 0.005:
        return []
    hi = cfg.get("band_hi")
    if hi is not None and abs(pm) >= hi / 100.0:
        return []
    move_dir = 1 if pm > 0 else -1
    want = move_dir  # follow
    trades = []
    start = next((i for i, c in enumerate(candles) if c["time"] >= T), None)
    if start is None:
        return []
    while len(trades) < 2:
        chosen = M.pick(ns, sym, day, ctx, start)
        if chosen is None:
            break
        setup, dirc, sig, idx = chosen
        if idx + 1 >= len(candles):
            break
        sign = 1 if dirc == "CE" else -1
        if sign != want:
            start = idx + 1
            continue
        ei = idx + 1
        entry = float(candles[ei]["open"])
        er, ep, et, xi, gross = U.replay_plain(candles, ei, sign, entry, TP, SP)
        _AUDIT["trades"] += 1
        if candles[ei]["time"] < T or candles[idx]["time"] < T or ei <= idx:
            _AUDIT["violations"] += 1
        trades.append({"date": day, "symbol": sym,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "setup": setup,
                       "leg": "direct" if not trades else "round2",
                       "round": len(trades) + 1,
                       "sig_time": candles[idx]["time"],
                       "entry_time": candles[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "event": ctx["event_status"],
                       "premove_pct": round(100 * pm, 3), "meas_time": T})
        start = xi
    return trades


def collect2(days, cfg, lag=False):
    ns = M.get_ns(H1.WHICH)
    all_days = sorted({d for (s, d) in ns["DAYCTX"]})
    prev_of = {d: all_days[i - 1] for i, d in enumerate(all_days) if i > 0}
    out = []
    for sym in ns["SYMBOLS"]:
        for day in days:
            pm_o = None
            if lag:
                pd = prev_of.get(day)
                pctx = ns["DAYCTX"].get((sym, pd)) if pd else None
                if pctx is None:
                    continue
                pm_o = M.premove(pctx["candles"], T)
                if pm_o is None:
                    continue
            out.extend(build2(ns, sym, day, cfg, pm_override=pm_o))
    return out


def days_of(months):
    ns = M.get_ns(H1.WHICH)
    return sorted({d for (s, d) in ns["DAYCTX"]
                   if any(d.startswith(m) for m in months)})


def summarize(trades):
    per_stock = defaultdict(float)
    months = {}
    for m in ALL_MONTHS:
        sel = [t for t in trades if t["date"].startswith(m)]
        months[m] = {"trades": len(sel),
                     "net": round(sum(t["net"] for t in sel), 2)}
    for t in trades:
        per_stock[t["symbol"]] += t["net"]
    js = [t for t in trades if not t["date"].startswith("2026-10")]
    per_stock_js = defaultdict(float)
    for t in js:
        per_stock_js[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {
        "trades": len(trades), "net": net,
        "jan_may": round(sum(v["net"] for m, v in months.items() if m <= "2026-05"), 2),
        "jun_sep": round(sum(v["net"] for m, v in months.items() if "2026-06" <= m <= "2026-09"), 2),
        "jan_sep": round(sum(t["net"] for t in js), 2),
        "october": months["2026-10"]["net"],
        "months": months,
        "breadth_full": sum(1 for v in per_stock.values() if v > 0),
        "breadth_jansep": sum(1 for v in per_stock_js.values() if v > 0),
        "exp": round(net / len(trades), 2) if trades else None,
        "per_stock": {k: round(v, 2) for k, v in sorted(per_stock.items(), key=lambda kv: -kv[1])},
    }


def main():
    H1.ensure_prep()
    results = {}
    all_days = days_of(ALL_MONTHS)
    js_days = days_of(ALL_MONTHS[:9])
    for name, cfg in FAMILIES.items():
        a0 = dict(_AUDIT)
        trades = collect2(all_days, cfg)
        pbo = collect2(js_days, cfg, lag=True)
        s = summarize(trades)
        ps = summarize(pbo)
        fam_audit = {"trades": _AUDIT["trades"] - a0["trades"],
                     "violations": _AUDIT["violations"] - a0["violations"]}
        legs = {
            "oct_ge_25000": s["october"] >= 25000,
            "both_halves_positive": s["jan_may"] > 0 and s["jun_sep"] > 0,
            "audit_clean": fam_audit["violations"] == 0,
            "beats_own_placebo": s["jan_sep"] > ps["jan_sep"],
            "breadth_ge_15": s["breadth_full"] >= 15,
        }
        legs["ACCEPTED"] = all(legs.values())
        results[name] = {"cfg": cfg, "book": s, "placebo_jan_sep": {
            "trades": ps["trades"], "net": ps["net"], "jan_sep": ps["jan_sep"]},
            "audit": fam_audit, "legs": legs}
        print(f"\n== {name} cfg={cfg}")
        print(f"   trades={s['trades']} net={s['net']} JM={s['jan_may']} "
              f"JS={s['jun_sep']} JanSep={s['jan_sep']} OCT={s['october']} "
              f"breadth={s['breadth_full']}/25 (JanSep {s['breadth_jansep']}) "
              f"exp={s['exp']}")
        print(f"   months={ {m: v['net'] for m, v in s['months'].items()} }")
        print(f"   placebo JanSep={ps['jan_sep']} ({ps['trades']} tr) "
              f"audit={fam_audit} legs={legs}", flush=True)
        if name == "F4_state_gate":
            with open(f"{BASE}/stocks_M2_F4_trades.csv", "w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=list(trades[0].keys()))
                w.writeheader()
                for t in sorted(trades, key=lambda x: (x["date"], x["symbol"])):
                    w.writerow(t)
    with open(f"{BASE}/stocks_M2_results.json", "w") as f:
        json.dump(results, f, indent=1)
    print("\nWROTE stocks_M2_results.json (+ F4 trades)", flush=True)


if __name__ == "__main__":
    main()
