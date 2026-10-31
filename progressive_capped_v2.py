"""Capped progressive backtest V2 (Chandu cap 2026-10-29 09:20 IST).
Paper only, no orders. Does NOT overwrite v1 files.
Separate caps, NOT combined: max 3 index trades/week AND max 3 stock
trades/week, max 1 trade per symbol per week, per series (V4, Skill, Unified).
Selection = convicted + high-return only (provisional, NOT Chandu's rule;
he only said convicted + high return):
- Ranking (signal-time / prospective only, never realised outcome):
  setup quality (setup4=3, setup3=2, setup2=1, skill OR=0), then bias-strong,
  then room ratio, then prospective net target (target net of Rs 40 cost).
- Filter: prospective net target >= Rs 500 (primary). Sensitivity at
  Rs 1000 is computed separately and reported, not adopted on one month.
  Prospective net target = direction*(target-entry)*100 - 40, using the
  provisional cash exit (entry = next 5-min open, stop = signal low/high,
  target = entry +/- 2*risk). This is a prospective size, not the realised
  net; a trade can still stop out. Trades with prospective target net
  <= 0 are excluded by the Rs 500 filter automatically (e.g. NHPC -Rs 8/-26
  cases in v1 were targets smaller than cost).
- Same provisional cash rules otherwise: 100 shares, Rs 40/trade,
  signal-candle stop, 2x target, square-off 15:10, Setup 1 skipped,
  short paper-only. Indices vs stocks reported separately, never combined
  as portfolio rupees (index nets are point-scaled).
Reuses candidates logic from progressive_capped.py, with target added.
"""
import sys, os, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, room_ratio, skill_or_outcome, SYMBOLS, SETUP_RANK, metrics, split_net
from daytrader_cash_backtest import find_signal, run_day, bias_of
from daytrader_skill_run import find_skill_signal

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
QTY, COST = 100, 40.0
INDEX = ("NIFTY", "BANKNIFTY")

def is_index(sym):
    return sym in INDEX

def candidates_for_month(year, month):
    v4, skill_filt = [], []
    skill_raw = 0
    ndays = None
    for sym in SYMBOLS:
        spot, daily = load(sym)
        dl = daily.to_dict("records")
        days = 0
        for i, y in enumerate(dl):
            d = y["date"]
            if d.year != year or d.month != month or i == 0:
                continue
            day_spot = spot[spot["date"] == d]
            if day_spot.empty:
                continue
            days += 1
            prev = dl[i - 1]
            pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
            bias, cs = bias_of(prev)
            scale = pdc / 55000.0 if pdc else 1.0
            allowed = {"PE"} if bias == "bearish" else {"CE"} if bias == "bullish" else {"CE", "PE"}
            week = d.isocalendar()[:2]
            wk = f"{week[0]}-W{week[1]:02d}"
            r = run_day(day_spot, pdh, pdc, pdl, bias, scale, QTY, COST)
            if r["exit_reason"] in ("target", "stop", "square_off"):
                setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
                sig_close = float(sig["close"]) if sig is not None else float(r["entry_price"])
                rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
                dirc = 1 if direction == "CE" else -1
                tnet = round(dirc * (float(r["target_price"]) - float(r["entry_price"])) * QTY - COST, 2)
                v4.append({"method": "V4", "symbol": sym, "date": d.date().isoformat(), "week": wk,
                           "setup": setup, "direction": direction, "exit_reason": r["exit_reason"],
                           "net_rs": round(float(r["net_rs"]), 2), "target_net_rs": tnet,
                           "setup_rank": SETUP_RANK.get(setup, 0),
                           "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                           "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
            raw = day_spot.to_dict("records")
            for c in raw:
                c["timestamp"] = str(c["timestamp"])
            setup, direction, sig = find_skill_signal(raw, ("or",))
            if setup is None:
                continue
            skill_raw += 1
            if direction not in allowed:
                continue
            sig_close = float(sig["close"])
            if direction == "CE" and not (sig_close < pdh):
                continue
            if direction == "PE" and not (sig_close < pdl):
                continue
            rr, room = room_ratio(sig_close, direction, pdh, pdc, pdl, scale)
            if rr < 1.0:
                continue
            out = skill_or_outcome(raw, sig, direction)
            if out is None:
                continue
            dirc = 1 if direction == "CE" else -1
            tnet = round(dirc * (out["target"] - out["entry"]) * QTY - COST, 2)
            skill_filt.append({"method": "Skill", "symbol": sym, "date": d.date().isoformat(), "week": wk,
                               "setup": setup, "direction": direction, "exit_reason": out["exit_reason"],
                               "net_rs": out["net_rs"], "target_net_rs": tnet, "setup_rank": 0,
                               "room_ratio": round(min(rr, 5.0), 3) if rr != float("inf") else 1.0,
                               "bias_strong": 1 if bias != "neutral" else 0, "results_pass": 0})
        if ndays is None:
            ndays = days
    return ndays, v4, skill_raw, skill_filt

def cap_select_v2(cands, min_target=500.0, cap_index=3, cap_stock=3):
    """Separate 3 index + 3 stock per ISO week, 1/symbol/week.
    Rank: setup_rank, bias_strong, room_ratio, target_net_rs (all signal-time/
    prospective), then date/symbol. Filter target_net >= min_target first."""
    pool = [t for t in cands if t["target_net_rs"] >= min_target]
    ranked = sorted(pool, key=lambda t: (-t["setup_rank"], -t["bias_strong"], -t["room_ratio"], -t["target_net_rs"], t["date"], t["symbol"]))
    picked, week_idx, week_stk, sym_week = [], {}, {}, set()
    for t in ranked:
        w = t["week"]
        if is_index(t["symbol"]):
            if week_idx.get(w, 0) >= cap_index:
                continue
        else:
            if week_stk.get(w, 0) >= cap_stock:
                continue
        if (t["symbol"], w) in sym_week:
            continue
        picked.append(t)
        if is_index(t["symbol"]):
            week_idx[w] = week_idx.get(w, 0) + 1
        else:
            week_stk[w] = week_stk.get(w, 0) + 1
        sym_week.add((t["symbol"], w))
    return picked, ranked

def leg_metrics(trades, ndays, nweeks):
    idx = [t for t in trades if is_index(t["symbol"])]
    stk = [t for t in trades if not is_index(t["symbol"])]
    return {"index": metrics(idx, ndays, nweeks), "stocks": metrics(stk, ndays, nweeks)}

def run_v2_month(year, month, min_target=500.0):
    ndays, v4, skill_raw, skill_filt = candidates_for_month(year, month)
    weeks = sorted(set(t["week"] for t in v4 + skill_filt))
    nweeks = len(weeks)
    v4_cap, _ = cap_select_v2(v4, min_target)
    sk_cap, _ = cap_select_v2(skill_filt, min_target)
    pool = {}
    for t in v4 + skill_filt:
        k = (t["symbol"], t["date"])
        if k not in pool or t["setup_rank"] > pool[k]["setup_rank"]:
            pool[k] = t
    uni_cap, _ = cap_select_v2(list(pool.values()), min_target)
    # sensitivity at 1000
    sens = {}
    for name, cands in (("v4", v4), ("skill", skill_filt), ("unified", list(pool.values()))):
        p, _ = cap_select_v2(cands, 1000.0)
        sens[name] = metrics(p, ndays, nweeks)
        sens[name + "_split"] = split_net(p)
    return {"year": year, "month": month, "days": ndays, "weeks": nweeks,
            "raw_v4": len(v4), "raw_skill_or": skill_raw, "filtered_skill": len(skill_filt),
            "v4_pass500": sum(1 for t in v4 if t["target_net_rs"] >= 500),
            "skill_pass500": sum(1 for t in skill_filt if t["target_net_rs"] >= 500),
            "v4_pass1000": sum(1 for t in v4 if t["target_net_rs"] >= 1000),
            "skill_pass1000": sum(1 for t in skill_filt if t["target_net_rs"] >= 1000),
            "v4_capped": metrics(v4_cap, ndays, nweeks), "skill_capped": metrics(sk_cap, ndays, nweeks),
            "unified_capped": metrics(uni_cap, ndays, nweeks),
            "v4_legs": leg_metrics(v4_cap, ndays, nweeks),
            "skill_legs": leg_metrics(sk_cap, ndays, nweeks),
            "unified_legs": leg_metrics(uni_cap, ndays, nweeks),
            "v4_capped_trades": v4_cap, "skill_capped_trades": sk_cap, "unified_capped_trades": uni_cap,
            "v4_split": split_net(v4_cap), "skill_split": split_net(sk_cap), "unified_split": split_net(uni_cap),
            "sensitivity_1000": sens,
            "avg_target_net_v4": round(sum(t["target_net_rs"] for t in v4_cap)/len(v4_cap), 2) if v4_cap else 0,
            "avg_target_net_skill": round(sum(t["target_net_rs"] for t in sk_cap)/len(sk_cap), 2) if sk_cap else 0,
            "avg_target_net_unified": round(sum(t["target_net_rs"] for t in uni_cap)/len(uni_cap), 2) if uni_cap else 0}

if __name__ == "__main__":
    y, m = int(sys.argv[1]), int(sys.argv[2])
    out = run_v2_month(y, m)
    print(f"{y}-{m:02d} days={out['days']} weeks={out['weeks']} raw_v4={out['raw_v4']} raw_skill_OR={out['raw_skill_or']} filtered_skill={out['filtered_skill']} pass500 v4={out['v4_pass500']} skill={out['skill_pass500']} pass1000 v4={out['v4_pass1000']} skill={out['skill_pass1000']}")
    for k in ("v4_capped", "skill_capped", "unified_capped"):
        print(k, out[k], "legs:", out[k.replace("_capped", "_legs")], "avg_target_net:", out["avg_target_net_" + k.split("_")[0]])
    print("sensitivity_1000:", out["sensitivity_1000"])
    with open(f"/home/hatch/workspace/trading/data/progressive/capped_v2_summary_{y}-{m:02d}.json", "w") as f:
        json.dump(out, f, indent=2, default=str)
