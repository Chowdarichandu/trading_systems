"""Round 2 Family J — second-signal rescan pool.
Spec frozen BEFORE scoring: stocks_oct_round2_familyJ_frozen.md.
STOCKS ONLY cash intraday, paper only, no orders.
All figures provisional per 100 shares, Rs40/trade — NOT premiums, NOT a lot profit.
"""
import sys, os, json, csv
sys.path.insert(0, "/home/hatch/workspace/trading")
import importlib.util
spec = importlib.util.spec_from_file_location("stocks_oct_tuning", "/home/hatch/workspace/trading/stocks_oct_tuning.py")
tun = importlib.util.module_from_spec(spec); spec.loader.exec_module(tun)
import pandas as pd
from progressive_capped import load
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import replay
from stock_system_s8 import STOCKS
from stock_system_s9 import build_events, trading_days_list, gate_filter, TIER_RANK
from stock_system_s8 import RANK_SETUP

BASE = os.path.expanduser("~/workspace/trading")
QTY, COST = 100, 40.0

def gen_rescan():
    _, ndaily = load("NIFTY"); ndl = ndaily.to_dict("records")
    nbias = {}
    for i, y in enumerate(ndl):
        if i == 0: continue
        b, _ = bias_of(ndl[i - 1]); nbias[y["date"].date().isoformat()] = b
    cands = []
    for sym in STOCKS:
        spot, daily = load(sym); dl = daily.to_dict("records")
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != 2026 or d.month > 10 or i == 0: continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty: continue
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev); scale = pdc / 55000.0 if pdc else 1.0
            or_c = day_spot[day_spot["time"] < "09:30"]
            if or_c.empty: continue
            orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
            if not (0.0015 <= (orh - orl) / pdc <= 0.040 if pdc else False): continue
            nb = nbias.get(d.date().isoformat())
            if nb is None or nb == "bullish": continue  # PE blocked on bullish Nifty (B8 rule)
            setup1, dir1, sig1 = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
            if sig1 is None: continue
            # rescan: OR rows + candles strictly after first signal candle, state reset
            sub = day_spot[(day_spot["time"] < "09:30") | (day_spot["timestamp"] > sig1["timestamp"])]
            if len(sub) <= len(or_c): continue
            setup2, dir2, sig2 = find_signal(sub, pdh, pdc, pdl, bias, scale)
            if setup2 is None or dir2 != "PE": continue
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            sig_idx = next((j for j, c in enumerate(candles) if str(c["timestamp"]) == str(sig2["timestamp"])), None)
            if sig_idx is None or sig_idx + 1 >= len(candles): continue
            eidx = sig_idx + 1
            entry = float(candles[eidx]["open"]); stop = float(sig2["high"]); risk = stop - entry
            if risk <= 0: continue
            target = entry - 2 * risk
            levels = sorted(set([pdh, pdc, pdl])); nxt = [l for l in levels if l < entry]
            if not nxt: continue
            room = entry - max(nxt)
            if room < 1.25 * risk: continue
            tnet = round(2 * risk * QTY - COST, 2)
            if tnet < 250: continue
            wk = d.isocalendar()[:2]; week = f"{wk[0]}-W{wk[1]:02d}"
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
            out = replay(crecs, eidx, entry, stop, target, "PE")
            cands.append({"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                          "setup": setup2, "direction": "PE", "bias": bias, "signal_time": str(sig2["timestamp"]),
                          "confirm_time": "", "entry_time": candles[eidx]["time"], "entry": round(entry, 2),
                          "stop": round(stop, 2), "target": round(target, 2), "risk": round(risk, 2),
                          "room": round(room, 2), "room_ratio": round(room / risk, 3), "target_net_rs": tnet,
                          "orh": orh, "orl": orl, "nifty_bias": nb, "rescan": True, **out})
    return cands

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

def rescore3R(rows):
    out = []
    for t in rows:
        candles = tun.day_candles(t["symbol"], t["date"])
        idx = next(j for j, c in enumerate(candles) if c["time"] == t["entry_time"])
        crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
        r = tun.replay_variant(crecs, idx, float(t["entry"]), float(t["stop"]), t["direction"],
                               target_mult=3.0, partial_frac=0.5, lock_R=0.0)
        nt = dict(t); nt.update(r); out.append(nt)
    return out

if __name__ == "__main__":
    events = build_events(trading_days_list())
    rescan_raw = gen_rescan()
    print("rescan candidates (pre-gate, 2R nets):", len(rescan_raw))
    rescan = rescore3R(rescan_raw)
    # base pool (validated shadow, 3R nets, tagged) — strip tags for re-gating uniformity
    base_rows = list(csv.DictReader(open(f"{BASE}/stocks_oct_round2_pool_shadow.csv")))
    for r in base_rows:
        for k in ("month",): r[k] = int(r[k])
        for k in ("entry", "stop", "target", "risk", "room", "room_ratio", "target_net_rs", "net_rs", "orh", "orl"):
            r[k] = float(r[k])
        r["full_target"] = r["full_target"] in ("True", True)
        r["rescan"] = False
        for k in ("gate_tier", "gate_pass", "nearest_event_type", "nearest_event_date", "event_phase"):
            r.pop(k, None)
    merged = base_rows + rescan
    survivors, blocked, tagged = gate_filter(merged, events)
    results = {"rescan_raw_n": len(rescan_raw),
               "rescan_oct_n": sum(1 for r in rescan_raw if r["month"] == 10),
               "rescan_survivors_n": sum(1 for r in survivors if r.get("rescan")),
               "rescan_blocked_n": sum(1 for r in blocked if r.get("rescan"))}
    for name, (pd_, pw) in {"J1_rescan_cap_s12": (1, 1), "J2_rescan_cap_2day": (2, 1)}.items():
        picked = cap_generic(survivors, pd_, pw)
        results[name] = tun.split_metrics(picked)
        print(name, json.dumps(results[name]))
        tun.write_csv(f"{BASE}/stocks_oct_round2_{name}_trades.csv", picked)
    # rescan shadow outcomes at 3R (all rescan candidates, gate outcome noted)
    tagmap = {(t["date"], t["symbol"], t["entry_time"]): (t["gate_tier"], t["gate_pass"]) for t in tagged}
    rshadow = []
    for r in rescan:
        tier, passed = tagmap.get((r["date"], r["symbol"], r["entry_time"]), ("?", False))
        rshadow.append({"date": r["date"], "month": r["month"], "symbol": r["symbol"], "setup": r["setup"],
                        "entry_time": r["entry_time"], "gate_tier": tier, "gate_pass": passed,
                        "target_net_rs": r["target_net_rs"], "room_ratio": r["room_ratio"], "net_rs_3R": r["net_rs"],
                        "full_target": r["full_target"]})
    results["rescan_shadow"] = rshadow
    tun.write_csv(f"{BASE}/stocks_oct_round2_rescan_candidates.csv", rescan)
    with open(f"{BASE}/stocks_oct_round2_j_results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("done J")
