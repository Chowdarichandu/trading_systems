"""Family (s): frozen c2-A validation on held-out reclaim trades + pure
thin-signal no-trade for untouched Cluster 1 shape. NIFTY only, paper only.
No orders, nothing fabricated. 100 shares, Rs40/trade, square-off 15:10,
stop checked before target per bar.
c2-A FROZEN (from family r, not re-fitted here): entry = open after second
close above L, stop = second-bar low, target = entry + 2x new risk, CE.
L = max(OR high, previous close). If second close <= L: no-trade.
Thin-signal NO-TRADE (pure, no scan to later signal): PE signal close
within <5 points below OR low (0 < ORlow-close < 5) -> whole day no-trade.
No-trade counted separately from green throughout. Green = net > 0.
"""
import os, sys, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
from progressive_engine import load as load_prog
from daytrader_cash_backtest import find_signal, run_day, bias_of
from timing_sweep import load as load_nifty, day_data as day_data_nifty, replay as replay_pe_timing
from reentry_filter_sweep import load_bn, day_data_bn
from combined_confirm_sweep import rescan_trade
from extended_window_sweep import day_variant as day_lA

QTY, COST = 100, 40.0

def replay_ce(candles, start_idx, entry, stop, target):
    risk = entry - stop
    if risk <= 0:
        return {"exit": "invalid_risk", "net": None, "risk": round(risk, 2)}
    for j in range(start_idx, len(candles)):
        c = candles.iloc[j]; hi, lo, cl, t = float(c["high"]), float(c["low"]), float(c["close"]), c["time"]
        if lo <= stop:
            return {"exit": "stop", "exit_time": t, "net": round(-risk*QTY-COST, 2), "risk": round(risk, 2)}
        if hi >= target:
            return {"exit": "target", "exit_time": t, "net": round(2*risk*QTY-COST, 2), "risk": round(risk, 2)}
        if t == "15:10":
            return {"exit": "square_off", "exit_time": t, "net": round((cl-entry)*QTY-COST, 2), "risk": round(risk, 2)}
    c = candles.iloc[-1]
    return {"exit": "square_off", "exit_time": c["time"], "net": round((float(c["close"])-entry)*QTY-COST, 2), "risk": round(risk, 2)}

def reclaim_day(ds, spot, daily):
    """Return dict for a setup4_reclaim day, or None if not that setup."""
    dl = daily.to_dict("records")
    for i, y in enumerate(dl):
        if str(y["date"])[:10] != ds:
            continue
        prev = dl[i-1]; day_spot = spot[spot["date"] == y["date"]]
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        bias, cs = bias_of(prev); scale = pdc/55000.0
        setup, dirn, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
        if setup != "setup4_reclaim":
            return None
        candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
        # sig timestamp match
        matches = candles[candles["timestamp"] == sig["timestamp"]]
        if matches.empty:
            return {"date": ds, "note": "sig timestamp not in >=09:30 candles"}
        sig_idx = int(matches.index[0])
        orh = float(day_spot[day_spot["time"] < "09:30"]["high"].max())
        L = max(orh, pdc)
        orig = run_day(day_spot, pdh, pdc, pdl, bias, scale, 100, 40)
        out = {"date": ds, "signal": sig["time"], "sig_close": float(sig["close"]), "sig_low": float(sig["low"]),
               "sig_high": float(sig["high"]), "sig_range": round(float(sig["high"])-float(sig["low"]), 2),
               "L": round(L, 2), "above_L": round(float(sig["close"])-L, 2), "orh": round(orh, 2), "pdc": round(pdc, 2),
               "bias": bias, "orig_entry": orig["entry_price"], "orig_stop": orig["stop_price"],
               "orig_target": orig["target_price"], "orig_net": orig["net_rs"], "orig_exit": orig["exit_reason"]}
        if sig_idx+2 < len(candles):
            second = candles.iloc[sig_idx+1]
            out["second_close"] = float(second["close"]); out["second_low"] = float(second["low"])
            out["second_above_L"] = round(float(second["close"])-L, 2)
            if float(second["close"]) > L:
                entry = float(candles.iloc[sig_idx+2]["open"]); stop = float(second["low"]); risk = entry-stop
                tr = replay_ce(candles, sig_idx+2, entry, stop, entry+2*risk) if risk > 0 else {"exit": "invalid_risk", "net": None}
                out["c2A"] = {"entry": entry, "stop": stop, "risk": round(risk, 2), "target": round(entry+2*risk, 2) if risk>0 else None, **tr}
            else:
                out["c2A"] = {"result": "no_trade_hold_fails"}
        else:
            out["c2A"] = {"result": "no_trade_no_second_bar"}
        return out
    return None

def scan_reclaims(spot, daily, year):
    rows = []
    for y in daily.to_dict("records"):
        ds = str(y["date"])[:10]
        if not ds.startswith(str(year)):
            continue
        r = reclaim_day(ds, spot, daily)
        if r is not None:
            rows.append(r)
    return rows

def plain_pe_day(ds, spot, daily, mode):
    """Plain PE trade via timing_sweep.replay gate 09:30, returning signal info."""
    dd = day_data_nifty(spot, daily, ds)
    if dd is None:
        return None
    day_spot, pdh, pdc, pdl, bias, scale = dd
    # timing replay returns trade dict; need signal details separately
    tr = replay_pe_timing(day_spot, pdh, pdc, pdl, bias, scale, "09:30", False, mode)
    if tr is None:
        return {"date": ds, "note": "no plain PE signal"}
    # recompute signal: replay_pe_timing internal signal is first breakdown; recover by scanning
    or_c = day_spot[day_spot["time"] < "09:30"]
    orl = float(or_c["low"].min()); orh = float(or_c["high"].max())
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    # signal bar is the bar before entry bar: entry is open of bar after signal; find bar whose next open == entry and time <=11:30
    sig = None
    for i in range(len(cand)-1):
        if abs(float(cand.iloc[i+1]["open"]) - float(tr["entry"])) < 1e-9:
            # check close below orl/pdl to confirm
            if float(cand.iloc[i]["close"]) < orl:
                sig = cand.iloc[i]; break
    if sig is None:
        return {"date": ds, "trade": tr, "note": "signal bar not recovered"}
    return {"date": ds, "signal": sig["time"], "sig_close": float(sig["close"]), "sig_high": float(sig["high"]),
            "sig_low": float(sig["low"]), "sig_range": round(float(sig["high"])-float(sig["low"]), 2),
            "orl": round(orl, 2), "dist_below_orl": round(orl-float(sig["close"]), 2),
            "thin_lt5": 0 < (orl-float(sig["close"])) < 5,
            "thin_and_narrow": (0 < (orl-float(sig["close"])) < 5) and (float(sig["high"])-float(sig["low"]) < 40),
            "entry": tr["entry"], "stop": tr["stop"], "target": tr["target"], "net": tr["net"], "exit": tr["exit"]}

if __name__ == "__main__":
    spot, daily = load_prog("NIFTY")
    out = {}
    # Part 1: held-out 2025 reclaim scan
    rows25 = scan_reclaims(spot, daily, 2025)
    out["reclaim_2025"] = rows25
    print(f"=== 2025 held-out setup4_reclaim: {len(rows25)} trades ===")
    for r in rows25: print(r)
    g = sum(1 for r in rows25 if r.get("orig_net") is not None and r["orig_net"] > 0)
    tot = sum(r["orig_net"] for r in rows25 if r.get("orig_net") is not None)
    cg = sum(1 for r in rows25 if r.get("c2A", {}).get("net") is not None and r["c2A"]["net"] > 0)
    cnt = sum(1 for r in rows25 if r.get("c2A", {}).get("result", "").startswith("no_trade"))
    ctot = sum(r["c2A"]["net"] for r in rows25 if r.get("c2A", {}).get("net") is not None)
    print(f"2025 original: green {g}/{len(rows25)} total {tot}")
    print(f"2025 c2-A frozen: green {cg}/{len(rows25)} no-trade {cnt} traded-total {ctot}")
    # 2026 fitted reproduction (must match r: 14 Jan, 26 Oct, 1 Jul)
    rows26 = scan_reclaims(spot, daily, 2026)
    out["reclaim_2026"] = rows26
    print(f"\n=== 2026 setup4_reclaim (fitted set, reproduction check): {len(rows26)} trades ===")
    for r in rows26: print(r)
    # Part 2a: plain Cluster1 + PE winners, thin <5 pure no-trade
    spot_n, daily_n = load_nifty()
    cluster1 = ["2026-01-09","2026-02-06","2026-03-30","2026-04-02","2026-05-13","2026-06-29","2026-07-08","2026-08-19"]
    winners = ["2026-01-21","2026-02-24","2026-03-16","2026-03-13","2026-03-23","2026-04-24","2026-05-05","2026-07-22","2026-08-12","2026-08-27","2026-09-29","2026-09-07","2026-10-08","2026-10-23"]
    modes1 = {"2026-04-02": "skill"}; modesw = {"2026-03-23": "skill"}
    for label, days, modes in (("plain_cluster1", cluster1, modes1), ("plain_winners", winners, modesw)):
        rows = []
        for ds in days:
            r = plain_pe_day(ds, spot_n, daily_n, modes.get(ds, "v4"))
            rows.append(r)
        out[label] = rows
        print(f"\n=== {label} plain PE ===")
        for r in rows: print(r)
        traded = [r for r in rows if r.get("net") is not None]
        print(f"{label} baseline: green {sum(1 for r in traded if r['net']>0)}/{len(rows)} total {sum(r['net'] for r in traded)}")
        thin = [r for r in rows if r.get("thin_lt5")]
        print(f"{label} thin<5 days: {[r['date'] for r in thin]}")
        kept = [r for r in rows if not r.get("thin_lt5") and r.get("net") is not None]
        print(f"{label} after pure thin no-trade: traded {len(kept)} green {sum(1 for r in kept if r['net']>0)} total {sum(r['net'] for r in kept)} no-trade {len(thin)}")
        thin_nr = [r for r in rows if r.get("thin_and_narrow")]
        kept2 = [r for r in rows if not r.get("thin_and_narrow") and r.get("net") is not None]
        print(f"{label} after thin+narrow(<40) no-trade: traded {len(kept2)} green {sum(1 for r in kept2 if r['net']>0)} total {sum(r['net'] for r in kept2)} no-trade {len(thin_nr)} days {[r['date'] for r in thin_nr]}")
    # Part 2b: (lA) scope
    bn_spot, bn_daily = load_bn()
    for label, days, modes in (("lA_cluster1", cluster1, modes1), ("lA_winners", winners, modesw)):
        rows = []
        for ds in days:
            dd = day_data_nifty(spot_n, daily_n, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            if dd is None or dbn is None:
                rows.append({"date": ds, "note": "no data"}); continue
            r = rescan_trade(dd, modes.get(ds, "v4"), dbn)
            if r is None:
                rows.append({"date": ds, "note": "no rescan trade"}); continue
            cand = r["candles"]; sig = cand.iloc[r["sig_idx"]]
            dist = round(r["orl"]-float(sig["close"]), 2)
            rows.append({"date": ds, "signal": r["info"]["signal"], "sig_close": float(sig["close"]),
                         "sig_high": float(sig["high"]), "sig_low": float(sig["low"]),
                         "sig_range": round(float(sig["high"])-float(sig["low"]), 2),
                         "orl": round(r["orl"], 2), "dist_below_orl": dist,
                         "thin_lt5": 0 < dist < 5, "thin_and_narrow": (0 < dist < 5) and (float(sig["high"])-float(sig["low"]) < 40),
                         "morning_net": r["trade"]["net"] if r["trade"] else None,
                         "morning_exit": r["trade"]["exit"] if r["trade"] else None})
        out[label] = rows
        print(f"\n=== {label} (lA morning signal) ===")
        for r in rows: print(r)
        print(f"{label} thin<5 days: {[r['date'] for r in rows if r.get('thin_lt5')]}")
        print(f"{label} thin+narrow days: {[r['date'] for r in rows if r.get('thin_and_narrow')]}")
        # day nets from r report / extended: use day_lA for day_net
        dayrows = []
        for ds in days:
            dd = day_data_nifty(spot_n, daily_n, ds); dbn = day_data_bn(bn_spot, bn_daily, ds)
            d = day_lA(dd, modes.get(ds, "v4"), dbn, "lA") if dd and dbn else None
            dayrows.append({"date": ds, "day_net": d["day_net"] if d else None})
        out[label+"_daynets"] = dayrows
        print(f"{label} (lA) day nets: {dayrows} total {sum(x['day_net'] for x in dayrows if x['day_net'] is not None)} green {sum(1 for x in dayrows if x['day_net'] is not None and x['day_net']>0)}")
        thin_dates = {r["date"] for r in rows if r.get("thin_lt5")}
        kept = [x for x in dayrows if x["date"] not in thin_dates and x["day_net"] is not None]
        print(f"{label} after pure thin (lA) no-trade: traded {len(kept)} green {sum(1 for x in kept if x['day_net']>0)} total {sum(x['day_net'] for x in kept)} no-trade {len(thin_dates)}")
    with open(os.path.expanduser("~/workspace/trading/s_sweep_raw.json"), "w") as f:
        json.dump(out, f, indent=2, default=str)
    print("\nWrote ~/workspace/trading/s_sweep_raw.json")
