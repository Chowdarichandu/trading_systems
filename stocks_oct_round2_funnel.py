"""Round 2 funnel diagnosis — S12 (B8-PE pool) October candidate leaks.
STOCKS ONLY cash intraday, paper only, no orders.
All figures provisional per 100 shares, Rs40/trade — NOT premiums, NOT a lot profit.
Diagnosis ONLY: no rule changes. Every pool candidate is re-scored at the
S12 exit (E4: partial 50% @1R, BE, target 3R) so shadow outcomes of
gate-blocked and capped-out candidates are on the same basis as taken trades.
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("stocks_oct_tuning", "/home/hatch/workspace/trading/stocks_oct_tuning.py")
tun = importlib.util.module_from_spec(spec); spec.loader.exec_module(tun)
from stock_system_s9 import build_events, trading_days_list, gate_filter, TIER_RANK
from stock_system_s8 import RANK_SETUP

def rescore3R(pool):
    out = []
    for t in pool:
        candles = tun.day_candles(t["symbol"], t["date"])
        idx = next(j for j, c in enumerate(candles) if c["time"] == t["entry_time"])
        crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
        r = tun.replay_variant(crecs, idx, float(t["entry"]), float(t["stop"]), t["direction"],
                               target_mult=3.0, partial_frac=0.5, lock_R=0.0)
        nt = dict(t); nt.update(r); out.append(nt)
    return out

def cap_trace(survivors):
    """Replicate S9 cap_select_gate, recording why each survivor was dropped."""
    key = lambda t: (-TIER_RANK[t["gate_tier"]], -t["target_net_rs"], -t["room_ratio"],
                     -RANK_SETUP.get(t["setup"], 0), t["date"], t["symbol"])
    ranked = sorted(survivors, key=key)
    picked, days, sym_week, dropped = [], set(), set(), []
    for t in ranked:
        day_block = t["date"] in days
        week_block = (t["symbol"], t["week"]) in sym_week
        if day_block or week_block:
            d = dict(t); d["cap_reason"] = ("day+week" if day_block and week_block else
                                            "day_cap" if day_block else "week_cap")
            dropped.append(d); continue
        picked.append(t); days.add(t["date"]); sym_week.add((t["symbol"], t["week"]))
    return picked, dropped

def agg(rows):
    if not rows: return {"n": 0, "net_rs": 0.0, "wins": 0, "full_targets": 0}
    return {"n": len(rows), "net_rs": round(sum(float(r["net_rs"]) for r in rows), 2),
            "wins": sum(1 for r in rows if float(r["net_rs"]) > 0),
            "full_targets": sum(1 for r in rows if r.get("full_target") in (True, "True"))}

if __name__ == "__main__":
    events = build_events(trading_days_list())
    pool_all = tun.gen_candidates(tnet_min=250.0, room_min=1.25, or_lo=0.0015, or_hi=0.040, second_close=False)
    pool = rescore3R([t for t in pool_all if t["direction"] == "PE"])
    survivors, blocked, tagged = gate_filter(pool, events)
    pool = tagged  # gate_filter tags copies; use tagged rows from here on
    picked, dropped = cap_trace(survivors)
    # validate funnel cap == S12 engine output
    import csv
    s12 = list(csv.DictReader(open(os.path.expanduser("~/workspace/trading/s12_trades_jan_oct_2026.csv"))))
    mine = sorted((t["date"], t["symbol"]) for t in picked)
    theirs = sorted((r["date"], r["symbol"]) for r in s12)
    validation = {"picked_matches_s12_csv": mine == theirs, "picked_n": len(picked), "s12_n": len(s12)}
    net_diff = []
    s12map = {(r["date"], r["symbol"]): float(r["net_rs"]) for r in s12}
    for t in picked:
        k = (t["date"], t["symbol"])
        if k in s12map and abs(float(t["net_rs"]) - s12map[k]) > 0.01:
            net_diff.append((k, t["net_rs"], s12map[k]))
    validation["net_diffs"] = net_diff

    report = {"validation": validation}
    for label, rows in [("pool_PE_all", pool), ("gate_survivors", survivors),
                        ("gate_blocked", blocked), ("capped_picked", picked), ("capped_out", dropped)]:
        report[label + "_janoct"] = agg(rows)
        report[label + "_oct"] = agg([r for r in rows if r["month"] == 10])
        report[label + "_jansep"] = agg([r for r in rows if r["month"] < 10])
    # October detail
    oct_pool = [r for r in pool if r["month"] == 10]
    report["oct_pool_by_tier"] = {}
    for tier in sorted(set(r["gate_tier"] for r in oct_pool)):
        report["oct_pool_by_tier"][tier] = agg([r for r in oct_pool if r["gate_tier"] == tier])
    report["oct_blocked"] = [{k: r.get(k) for k in ("date", "symbol", "setup", "gate_tier", "room_ratio", "target_net_rs", "entry_time", "net_rs", "full_target", "exit_reason")} for r in blocked if r["month"] == 10]
    report["oct_capped_out"] = [{k: r.get(k) for k in ("date", "symbol", "setup", "gate_tier", "room_ratio", "target_net_rs", "entry_time", "net_rs", "full_target", "cap_reason")} for r in dropped if r["month"] == 10]
    report["oct_picked"] = [{k: r.get(k) for k in ("date", "symbol", "setup", "gate_tier", "room_ratio", "target_net_rs", "entry_time", "net_rs", "full_target")} for r in picked if r["month"] == 10]
    report["oct_days_with_pool_candidate"] = len(set(r["date"] for r in oct_pool))
    report["oct_days_with_survivor"] = len(set(r["date"] for r in survivors if r["month"] == 10))
    report["oct_trading_days"] = len(tun.OCT_DAYS)
    report["oct_pool_entry_times"] = {}
    for r in oct_pool:
        report["oct_pool_entry_times"][r["entry_time"]] = report["oct_pool_entry_times"].get(r["entry_time"], 0) + 1
    report["oct_pool_setups"] = {}
    for r in oct_pool:
        report["oct_pool_setups"][r["setup"]] = report["oct_pool_setups"].get(r["setup"], 0) + 1
    report["janoct_pool_setups"] = {}
    for r in pool:
        report["janoct_pool_setups"][r["setup"]] = report["janoct_pool_setups"].get(r["setup"], 0) + 1
    report["capped_out_oct_by_reason"] = {}
    for r in dropped:
        if r["month"] == 10:
            report["capped_out_oct_by_reason"][r["cap_reason"]] = report["capped_out_oct_by_reason"].get(r["cap_reason"], 0) + 1
    report["capped_out_jan_sep_by_reason"] = {}
    for r in dropped:
        if r["month"] < 10:
            k = r["cap_reason"]; report["capped_out_jan_sep_by_reason"][k] = report["capped_out_jan_sep_by_reason"].get(k, 0) + 1
    report["jansep_blocked_shadow"] = agg([r for r in blocked if r["month"] < 10])
    report["jansep_capped_out_shadow"] = agg([r for r in dropped if r["month"] < 10])
    # tier legs on picked (S12) full window
    for tier in sorted(set(r["gate_tier"] for r in picked)):
        report[f"picked_tier_{tier}_janoct"] = agg([r for r in picked if r["gate_tier"] == tier])
        report[f"picked_tier_{tier}_jansep"] = agg([r for r in picked if r["gate_tier"] == tier and r["month"] < 10])
        report[f"picked_tier_{tier}_oct"] = agg([r for r in picked if r["gate_tier"] == tier and r["month"] == 10])
    print(json.dumps(report, indent=2, default=str))
    with open(os.path.expanduser("~/workspace/trading/stocks_oct_round2_funnel.json"), "w") as f:
        json.dump(report, f, indent=2, default=str)
    tun.write_csv(os.path.expanduser("~/workspace/trading/stocks_oct_round2_pool_shadow.csv"), pool)
