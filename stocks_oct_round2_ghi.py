"""Round 2 families G (cap), H (tier repair), I (drawdown exits).
Specs frozen BEFORE scoring: stocks_oct_round2_familyG_frozen.md,
stocks_oct_round2_familyH_frozen.md, stocks_oct_round2_familyI_frozen.md.
STOCKS ONLY cash intraday, paper only, no orders.
All figures provisional per 100 shares, Rs40/trade — NOT premiums, NOT a lot profit.
G/H reuse the funnel shadow pool: every B8-PE candidate already re-scored
at the S12 (E4 3R) exit and gate-tagged, validated to reproduce S12 exactly.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("stocks_oct_tuning", "/home/hatch/workspace/trading/stocks_oct_tuning.py")
tun = importlib.util.module_from_spec(spec); spec.loader.exec_module(tun)
from stock_system_s9 import TIER_RANK
from stock_system_s8 import RANK_SETUP

BASE = os.path.expanduser("~/workspace/trading")
QTY, COST = 100, 40.0

def load_shadow():
    rows = list(csv.DictReader(open(f"{BASE}/stocks_oct_round2_pool_shadow.csv")))
    for r in rows:
        for k in ("month",): r[k] = int(r[k])
        for k in ("entry", "stop", "target", "risk", "room", "room_ratio", "target_net_rs", "net_rs", "orh", "orl"):
            r[k] = float(r[k])
        r["full_target"] = r["full_target"] in ("True", True)
        r["gate_pass"] = r["gate_pass"] in ("True", True)
    return rows

def cap_generic(survivors, per_day, per_week):
    key = lambda t: (-TIER_RANK[t["gate_tier"]], -t["target_net_rs"], -t["room_ratio"],
                     -RANK_SETUP.get(t["setup"], 0), t["date"], t["symbol"])
    ranked = sorted(survivors, key=key)
    picked, day_count, week_count = [], {}, {}
    for t in ranked:
        if day_count.get(t["date"], 0) >= per_day: continue
        if week_count.get((t["symbol"], t["week"]), 0) >= per_week: continue
        picked.append(t)
        day_count[t["date"]] = day_count.get(t["date"], 0) + 1
        week_count[(t["symbol"], t["week"])] = week_count.get((t["symbol"], t["week"]), 0) + 1
    return picked

def M(rows):
    return tun.split_metrics(rows)

# ---------- Family I replay: S12 exit + lock / time-stop variants ----------
def replay_i(candles, start_idx, entry, stop, direction, lock_R=0.0, time_stop_min=None):
    d = 1 if direction == "CE" else -1
    risk = abs(entry - stop)
    target = entry + d * 3.0 * risk
    plevel = entry + d * risk
    pq, rq = 0.5 * QTY, QTY - 0.5 * QTY
    partial = False
    def mins(t): return int(t[:2]) * 60 + int(t[3:5])
    entry_min = mins(candles[start_idx]["time"])
    for i in range(start_idx, len(candles)):
        c = candles[i]; t = c["time"]; hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        cur_stop = (entry + d * lock_R * risk) if partial else stop
        hit_stop = (lo <= cur_stop) if d == 1 else (hi >= cur_stop)
        if hit_stop:
            if partial:
                return {"exit_reason": "stop_after_partial", "exit_time": t,
                        "net_rs": round(pq * risk + rq * d * (cur_stop - entry) - COST, 2), "full_target": False}
            return {"exit_reason": "stop", "exit_time": t, "net_rs": round(-risk * QTY - COST, 2), "full_target": False}
        if not partial:
            if (d == 1 and hi >= plevel) or (d == -1 and lo <= plevel):
                partial = True
                if (d == 1 and hi >= target) or (d == -1 and lo <= target):
                    return {"exit_reason": "target_after_partial", "exit_time": t,
                            "net_rs": round(pq * risk + rq * 3.0 * risk - COST, 2), "full_target": True}
        elif (d == 1 and hi >= target) or (d == -1 and lo <= target):
            return {"exit_reason": "target_after_partial", "exit_time": t,
                    "net_rs": round(pq * risk + rq * 3.0 * risk - COST, 2), "full_target": True}
        if not partial and time_stop_min is not None and mins(t) - entry_min >= time_stop_min:
            return {"exit_reason": "time_stop", "exit_time": t,
                    "net_rs": round(QTY * d * (cl - entry) - COST, 2), "full_target": False}
        if t == "15:10":
            base = (pq * risk if partial else 0.0) + (rq if partial else QTY) * d * (cl - entry)
            return {"exit_reason": "square_off", "exit_time": t, "net_rs": round(base - COST, 2), "full_target": False}
    c = candles[-1]; cl = float(c["close"])
    base = (pq * risk if partial else 0.0) + (rq if partial else QTY) * d * (cl - entry)
    return {"exit_reason": "square_off", "exit_time": c["time"], "net_rs": round(base - COST, 2), "full_target": False}

def family_I(s12_rows):
    variants = {"I0_s12_exit": dict(), "I1_lock0.5_3R": dict(lock_R=0.5),
                "I2_timestop60": dict(time_stop_min=60), "I3_timestop120": dict(time_stop_min=120)}
    res = {}
    for name, kw in variants.items():
        out = []
        for t in s12_rows:
            candles = tun.day_candles(t["symbol"], t["date"])
            idx = next(j for j, c in enumerate(candles) if c["time"] == t["entry_time"])
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
            r = replay_i(crecs, idx, float(t["entry"]), float(t["stop"]), t["direction"], **kw)
            nt = dict(t); nt.update(r); out.append(nt)
        res[name] = {"metrics": M(out), "trades": out}
    diffs = [(t["symbol"], t["date"]) for t, o in zip(s12_rows, res["I0_s12_exit"]["trades"])
             if abs(float(t["net_rs"]) - o["net_rs"]) > 0.01]
    res["_I0_validation_diffs"] = diffs
    return res

if __name__ == "__main__":
    pool = load_shadow()
    survivors = [r for r in pool if r["gate_pass"]]
    results = {}
    # Family G
    gvars = {"G0_s12_cap": (1, 1), "G1_2day_1week": (2, 1), "G2_1day_2week": (1, 2), "G3_2day_2week": (2, 2)}
    g_trades = {}
    for name, (pd_, pw) in gvars.items():
        picked = cap_generic(survivors, pd_, pw)
        results[name] = M(picked); g_trades[name] = picked
        print(name, json.dumps(results[name]))
    s12_picked = g_trades["G0_s12_cap"]
    # Family H (filter survivors pre-cap, then S12 cap)
    def h_filter(rows, fn): return [r for r in rows if fn(r)]
    hvars = {
        "H1_pre_tnet1000": lambda r: r["gate_tier"] != "pre_announcement" or r["target_net_rs"] >= 1000,
        "H2_pre_room3_tnet600": lambda r: r["gate_tier"] != "pre_announcement" or (r["room_ratio"] >= 3.0 and r["target_net_rs"] >= 600),
        "H3_noevent_AND": lambda r: r["gate_tier"] != "no_event" or (r["room_ratio"] >= 2.0 and r["target_net_rs"] >= 1000),
        "H4_noevent_tnet600": lambda r: r["gate_tier"] != "no_event" or r["target_net_rs"] >= 600,
    }
    h_trades = {}
    for name, fn in hvars.items():
        surv = h_filter(survivors, fn)
        picked = cap_generic(surv, 1, 1)
        results[name] = M(picked); h_trades[name] = picked
        print(name, json.dumps(results[name]))
    # H5 conditional: only if H2 and H4 each leave Oct net >= S12 Oct net
    s12_oct_net = results["G0_s12_cap"]["oct"]["net_rs"]
    if results["H2_pre_room3_tnet600"]["oct"]["net_rs"] >= s12_oct_net and results["H4_noevent_tnet600"]["oct"]["net_rs"] >= s12_oct_net:
        surv = [r for r in survivors if hvars["H2_pre_room3_tnet600"](r) and hvars["H4_noevent_tnet600"](r)]
        picked = cap_generic(surv, 1, 1)
        results["H5_H2plusH4"] = M(picked); h_trades["H5_H2plusH4"] = picked
        print("H5_H2plusH4", json.dumps(results["H5_H2plusH4"]))
    else:
        results["H5_H2plusH4"] = "not_scored_precondition_failed"
    # Family I on S12 capped entries
    famI = family_I(sorted(s12_picked, key=lambda t: t["date"]))
    print("I0 validation diffs:", famI.pop("_I0_validation_diffs"))
    for k, v in famI.items():
        results[k] = v["metrics"]; print(k, json.dumps(v["metrics"]))
        if k != "I0_s12_exit":
            tun.write_csv(f"{BASE}/stocks_oct_round2_{k}_trades.csv", v["trades"])
    for name, picked in {**g_trades, **h_trades}.items():
        if name != "G0_s12_cap":
            tun.write_csv(f"{BASE}/stocks_oct_round2_{name}_trades.csv", picked)
    with open(f"{BASE}/stocks_oct_round2_ghi_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("done GHI")
