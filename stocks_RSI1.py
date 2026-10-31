#!/usr/bin/env python3
"""LINE RSI1 — RSI as an entry mechanism, home 25, Jan-Oct 2026.
Spec frozen in stocks_RSI1_frozen.md BEFORE scoring. Controls-first:
timing audit + stale-RSI placebo in the SAME run. Equity cash,
LONG/SHORT, paper only, real Rs0, provisional per 100 shares,
net = gross - Rs40/trade."""
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
sys.path.insert(0, BASE)
from daytrader_skill_run import rsi_wilder

COST = 40.0
EXITS = {"T05/S050": (0.5, 0.5), "T10/S050": (1.0, 0.5),
         "T125/S065": (1.25, 0.65)}
MECHS = ["RSI-A", "RSI-B", "RSI-C"]
MONTHS = [f"2026-{i:02d}" for i in range(1, 11)]
_AUDIT = {"trades": 0, "violations": 0}

# ------------------------------------------------------------- series ----
def build_series(ns):
    """Per symbol: ordered DAYCTX days, continuous 5-min closes, RSI(14)
    on the continuous series, per-day RSI slices; daily closes extended
    with Oct 29/30 (validated aggregation) and daily RSI(2)."""
    out = {}
    for sym in ns["SYMBOLS"]:
        days = sorted(d for (s, d) in ns["DAYCTX"] if s == sym)
        closes, slices = [], {}
        for day in days:
            raw = ns["DAYCTX"][(sym, day)]["raw"]
            start = len(closes)
            closes.extend(float(c["close"]) for c in raw)
            slices[day] = (start, len(raw))
        rsi14 = rsi_wilder(closes, 14)
        day_rsi = {day: rsi14[a:a + n] for day, (a, n) in slices.items()}
        daily = list(ns["stocks"][sym][1])
        dcloses = {d["date"][:10]: float(d["close"]) for d in daily}
        for extra in ("2026-10-29", "2026-10-30"):
            if extra not in dcloses:
                bars = H1.agg_5min(sym, H1.WHICH, extra)
                if bars:
                    dcloses[extra] = float(bars[-1]["close"])
        ddates = sorted(dcloses)
        rsi2 = rsi_wilder([dcloses[d] for d in ddates], 2)
        rsi2_by_date = {d: rsi2[i] for i, d in enumerate(ddates)}
        out[sym] = {"days": days, "day_rsi": day_rsi,
                    "ddates": ddates, "rsi2_by_date": rsi2_by_date}
    return out

# ------------------------------------------------------------- events ----
def events_ab(raw, rsi_vals, mech):
    """Signal events [(bar_idx, sign)] for RSI-A / RSI-B from an RSI
    slice aligned to raw bars. rsi_vals may be a stale (placebo) slice."""
    ev = []
    day_open = float(raw[0]["open"])
    for j in range(1, len(raw)):
        r0, r1 = rsi_vals[j - 1], rsi_vals[j]
        if r0 is None or r1 is None:
            continue
        if mech == "RSI-A":
            if r0 <= 30 < r1:
                ev.append((j, 1))
            elif r0 >= 70 > r1:
                ev.append((j, -1))
        else:  # RSI-B
            move = float(raw[j]["close"]) / day_open - 1
            if r0 <= 50 < r1 and move > 0:
                ev.append((j, 1))
            elif r0 >= 50 > r1 and move < 0:
                ev.append((j, -1))
    return ev

def run_events(raw, events, tp, sp, day, sym, mech, lag):
    trades, last_exit, count = [], -1, 0
    for j, sign in events:
        if count >= 4 or j <= last_exit:
            continue
        ei = j + 1
        if ei >= len(raw) or raw[ei]["time"] >= "15:10":
            continue
        entry = float(raw[ei]["open"])
        er, ep, et, xi, gross = U.replay_plain(raw, ei, sign, entry, tp, sp)
        _AUDIT["trades"] += 1
        if ei != j + 1 or raw[ei]["time"] <= raw[j]["time"]:
            _AUDIT["violations"] += 1
        trades.append({"date": day, "symbol": sym, "mech": mech,
                       "dir": "LONG" if sign == 1 else "SHORT",
                       "sig_time": raw[j]["time"],
                       "entry_time": raw[ei]["time"],
                       "entry": round(entry, 2), "exit_reason": er,
                       "exit_time": et, "exit": round(ep, 2),
                       "gross": round(gross, 2),
                       "net": round(gross - COST, 2),
                       "placebo": lag})
        last_exit, count = xi, count + 1
    return trades

def trade_c(raw, sign, tp, sp, day, sym, lag, rsi2_val):
    ei = next((i for i, c in enumerate(raw) if c["time"] == "09:35"), None)
    if ei is None:
        return None
    entry = float(raw[ei]["open"])
    er, ep, et, xi, gross = U.replay_plain(raw, ei, sign, entry, tp, sp)
    _AUDIT["trades"] += 1  # date-index assertion done at generation time
    return {"date": day, "symbol": sym, "mech": "RSI-C",
            "dir": "LONG" if sign == 1 else "SHORT",
            "sig_time": "prev_close", "entry_time": raw[ei]["time"],
            "entry": round(entry, 2), "exit_reason": er,
            "exit_time": et, "exit": round(ep, 2),
            "gross": round(gross, 2), "net": round(gross - COST, 2),
            "rsi2_used": None if rsi2_val is None else round(rsi2_val, 2),
            "placebo": lag}

def collect(ns, S, mech, tp, sp, lag=False):
    out = []
    for sym in ns["SYMBOLS"]:
        info = S[sym]
        days = info["days"]
        prev_of = {d: days[i - 1] for i, d in enumerate(days) if i > 0}
        for day in days:
            ctx = ns["DAYCTX"].get((sym, day))
            if ctx is None:
                continue
            raw = ctx["raw"]
            if mech in ("RSI-A", "RSI-B"):
                if lag:
                    pd = prev_of.get(day)
                    if pd is None:
                        continue
                    rsi_vals = info["day_rsi"][pd]
                    if len(rsi_vals) != len(raw):
                        continue
                else:
                    rsi_vals = info["day_rsi"][day]
                ev = events_ab(raw, rsi_vals, mech)
                out.extend(run_events(raw, ev, tp, sp, day, sym, mech, lag))
            else:  # RSI-C
                prior = [d for d in info["ddates"] if d < day]
                if len(prior) < (2 if lag else 1):
                    continue
                used_date = prior[-2] if lag else prior[-1]
                if not used_date < day:
                    _AUDIT["violations"] += 1
                    continue
                v = info["rsi2_by_date"].get(used_date)
                if v is None:
                    continue
                sign = 1 if v <= 10 else (-1 if v >= 90 else 0)
                if sign == 0:
                    continue
                t = trade_c(raw, sign, tp, sp, day, sym, lag, v)
                if t:
                    out.append(t)
    return out

# ------------------------------------------------------------- stats -----
def summarize(trades):
    months, per_stock = {}, defaultdict(float)
    for m in MONTHS:
        sel = [t for t in trades if t["date"].startswith(m)]
        months[m] = {"trades": len(sel),
                     "net": round(sum(t["net"] for t in sel), 2)}
    for t in trades:
        per_stock[t["symbol"]] += t["net"]
    net = round(sum(t["net"] for t in trades), 2)
    return {"trades": len(trades), "net": net,
            "jan_may": round(sum(v["net"] for m, v in months.items()
                                 if m <= "2026-05"), 2),
            "jun_oct": round(sum(v["net"] for m, v in months.items()
                                 if m >= "2026-06"), 2),
            "october": months["2026-10"]["net"],
            "months": months,
            "months_green": sum(1 for v in months.values() if v["net"] > 0),
            "breadth": sum(1 for v in per_stock.values() if v > 0),
            "exp": round(net / len(trades), 2) if trades else None,
            "per_stock": {k: round(v, 2) for k, v in sorted(
                per_stock.items(), key=lambda kv: -kv[1])}}

def main():
    H1.ensure_prep()
    ns = M.get_ns(H1.WHICH)
    S = build_series(ns)
    results, dumps = {}, {}
    for mech in MECHS:
        for exname, (tp, sp) in EXITS.items():
            real = collect(ns, S, mech, tp, sp, lag=False)
            pbo = collect(ns, S, mech, tp, sp, lag=True)
            for context in ("all", "below50"):
                if context == "below50":
                    rsel = [t for t in real if H1.below50(t["date"])]
                    psel = [t for t in pbo if H1.below50(t["date"])]
                else:
                    rsel, psel = real, pbo
                s, ps = summarize(rsel), summarize(psel)
                gate = {"net_pos": s["net"] > 0,
                        "halves_both_pos": s["jan_may"] > 0 and s["jun_oct"] > 0,
                        "oct_pos": s["october"] > 0,
                        "breadth_ge15": s["breadth"] >= 15,
                        "exp_ge100": (s["exp"] or -1) >= 100,
                        "beats_placebo": s["net"] > ps["net"],
                        "audit_clean": _AUDIT["violations"] == 0}
                gate["CANDIDATE"] = all(gate.values())
                key = f"{mech}|{exname}|{context}"
                results[key] = {"real": s, "placebo": {
                    "trades": ps["trades"], "net": ps["net"],
                    "october": ps["october"]}, "gate": gate}
                dumps[key] = rsel
                print(f"{key}: net={s['net']} JM={s['jan_may']} JO={s['jun_oct']} "
                      f"OCT={s['october']} tr={s['trades']} br={s['breadth']}/25 "
                      f"exp={s['exp']} green={s['months_green']}/10 "
                      f"pbo={ps['net']} CAND={gate['CANDIDATE']}", flush=True)
    results["_audit"] = dict(_AUDIT)
    with open(f"{BASE}/stocks_RSI1_results.json", "w") as f:
        json.dump(results, f, indent=1)
    for key, trades in dumps.items():
        tag = key.replace("|", "_").replace("/", "")
        flat = sorted(trades, key=lambda x: (x["date"], x["symbol"],
                                             x["entry_time"]))
        if not flat:
            continue
        with open(f"{BASE}/stocks_RSI1_{tag}_trades.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(flat[0].keys()))
            w.writeheader()
            for t in flat:
                w.writerow(t)
    print("AUDIT:", _AUDIT, flush=True)
    print("WROTE stocks_RSI1_results.json + dumps", flush=True)

if __name__ == "__main__":
    main()
