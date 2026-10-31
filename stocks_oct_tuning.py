"""Stocks October tuning harness — families A/B/C/D, specs frozen before scoring:
stocks_oct_familyA_exits_frozen.md, stocks_oct_familyB_entry_frozen.md,
stocks_oct_familyCD_frozen.md. STOCKS ONLY cash intraday, paper only.
All figures provisional per 100 shares, Rs40/trade — NOT premiums, NOT a lot profit.
"""
import sys, os, json, csv, math, itertools
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from progressive_capped import load, SYMBOLS
from daytrader_cash_backtest import find_signal, bias_of
from new_stock_system_s1 import nifty_day_map, replay
from stock_system_s8 import STOCKS, RANK_SETUP, metrics as base_metrics
from stock_system_s9 import build_events, trading_days_list, gate_filter, cap_select_gate, tag_candidate
from stock_system_s8 import cap_select_daily

QTY, COST = 100, 40.0
OUTDIR = "/tmp/oct_tuning"; os.makedirs(OUTDIR, exist_ok=True)

# ---------- period helpers ----------
_, nifty_daily = load("NIFTY")
ALL_DAYS = sorted(str(d.date()) for d in nifty_daily["date"] if d.year == 2026 and d.month <= 10)
OCT_DAYS = [d for d in ALL_DAYS if d[5:7] == "10"]
JANSEP_DAYS = [d for d in ALL_DAYS if d[5:7] != "10"]

def ext_metrics(trades, period_days):
    trades = sorted(trades, key=lambda t: t["date"])
    m = base_metrics(trades)
    cum, peak, maxdd = 0.0, 0.0, 0.0
    for t in trades:
        cum = round(cum + t["net_rs"], 2); peak = max(peak, cum); maxdd = min(maxdd, cum - peak)
    weeks = len(period_days) / 5.0
    return {**m, "maxdd_rs": round(maxdd, 2),
            "trades_per_week": round(len(trades) / weeks, 2) if weeks else 0,
            "period_trading_days": len(period_days)}

def split_metrics(capped):
    return {"oct": ext_metrics([t for t in capped if t["month"] == 10], OCT_DAYS),
            "jansep": ext_metrics([t for t in capped if t["month"] < 10], JANSEP_DAYS),
            "janoct": ext_metrics(capped, ALL_DAYS)}

def write_csv(path, rows):
    if not rows:
        with open(path, "w") as f: f.write("")
        return
    fields = []
    for r in rows:
        for k in r.keys():
            if k not in fields: fields.append(k)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)

# ---------- candle cache for exit replays ----------
_SPOT = {}
def day_candles(sym, date_str):
    if sym not in _SPOT:
        spot, _ = load(sym); _SPOT[sym] = spot
    spot = _SPOT[sym]
    d = pd.to_datetime(date_str)
    day = spot[spot["date"] == d]
    return day[day["time"] >= "09:30"].reset_index(drop=True).to_dict("records")

def replay_variant(candles, start_idx, entry, stop, direction, target_mult=2.0, partial_frac=0.5, lock_R=0.0):
    d = 1 if direction == "CE" else -1
    risk = abs(entry - stop)
    target = entry + d * target_mult * risk
    plevel = entry + d * risk
    pq = partial_frac * QTY; rq = QTY - pq
    partial = False
    for i in range(start_idx, len(candles)):
        c = candles[i]; t = c["time"]; hi, lo, cl = float(c["high"]), float(c["low"]), float(c["close"])
        cur_stop = (entry + d * lock_R * risk) if partial else stop
        hit_stop = (lo <= cur_stop) if d == 1 else (hi >= cur_stop)
        if hit_stop:
            if partial:
                net = pq * risk + rq * d * (cur_stop - entry) - COST
                return {"exit_reason": "stop_after_partial", "exit_time": t, "net_rs": round(net, 2), "full_target": False}
            return {"exit_reason": "stop", "exit_time": t, "net_rs": round(-risk * QTY - COST, 2), "full_target": False}
        if not partial and pq > 0:
            if (d == 1 and hi >= plevel) or (d == -1 and lo <= plevel):
                partial = True
                if (d == 1 and hi >= target) or (d == -1 and lo <= target):
                    return {"exit_reason": "target_after_partial", "exit_time": t, "net_rs": round(pq * risk + rq * target_mult * risk - COST, 2), "full_target": True}
        elif (d == 1 and hi >= target) or (d == -1 and lo <= target):
            if partial:
                return {"exit_reason": "target_after_partial", "exit_time": t, "net_rs": round(pq * risk + rq * target_mult * risk - COST, 2), "full_target": True}
            return {"exit_reason": "target", "exit_time": t, "net_rs": round(QTY * target_mult * risk - COST, 2), "full_target": True}
        if t == "15:10":
            base = (pq * risk if partial else 0.0) + (rq if partial else QTY) * d * (cl - entry)
            return {"exit_reason": "square_off", "exit_time": t, "net_rs": round(base - COST, 2), "full_target": False}
    c = candles[-1]; cl = float(c["close"])
    base = (pq * risk if partial else 0.0) + (rq if partial else QTY) * d * (cl - entry)
    return {"exit_reason": "square_off", "exit_time": c["time"], "net_rs": round(base - COST, 2), "full_target": False}

# ---------- Family A: exits on S9 capped SAME entries ----------
def family_A(s9_capped):
    variants = {
        "E0_baseline_t2_p50_BE": dict(target_mult=2.0, partial_frac=0.5, lock_R=0.0),
        "E1_nopartial_t2": dict(target_mult=2.0, partial_frac=0.0, lock_R=0.0),
        "E2_t1.5_p50_BE": dict(target_mult=1.5, partial_frac=0.5, lock_R=0.0),
        "E3_t2.5_p50_BE": dict(target_mult=2.5, partial_frac=0.5, lock_R=0.0),
        "E4_t3_p50_BE": dict(target_mult=3.0, partial_frac=0.5, lock_R=0.0),
        "E5_t2_p50_lock0.5": dict(target_mult=2.0, partial_frac=0.5, lock_R=0.5),
        "E6_t2_p25_BE": dict(target_mult=2.0, partial_frac=0.25, lock_R=0.0),
        "E7_t2_p75_BE": dict(target_mult=2.0, partial_frac=0.75, lock_R=0.0),
        "E8_nopartial_t1.5": dict(target_mult=1.5, partial_frac=0.0, lock_R=0.0),
    }
    res = {}
    for name, kw in variants.items():
        out = []
        for t in s9_capped:
            candles = day_candles(t["symbol"], t["date"])
            idx = next(j for j, c in enumerate(candles) if c["time"] == t["entry_time"])
            crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
            r = replay_variant(crecs, idx, float(t["entry"]), float(t["stop"]), t["direction"], **kw)
            nt = dict(t); nt.update(r); out.append(nt)
        res[name] = {"metrics": split_metrics(out), "trades": out}
    # validate E0 reproduces originals
    diffs = [(t["symbol"], t["date"], t["net_rs"], o["net_rs"]) for t, o in
             zip(sorted(s9_capped, key=lambda x: (x["date"], x["symbol"])),
                 sorted(res["E0_baseline_t2_p50_BE"]["trades"], key=lambda x: (x["date"], x["symbol"]))) if abs(float(t["net_rs"]) - o["net_rs"]) > 0.01]
    res["_E0_validation_diffs"] = diffs
    return res

# ---------- parameterised candidate generation (Family B) ----------
def gen_candidates(room_min=1.5, tnet_min=500.0, or_lo=0.0025, or_hi=0.030, second_close=True, nifty_block=True):
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
            if not (or_lo <= (orh - orl) / pdc <= or_hi if pdc else False): continue
            nb = nbias.get(d.date().isoformat())
            if nb is None: continue
            candles = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True).to_dict("records")
            wk = d.isocalendar()[:2]; week = f"{wk[0]}-W{wk[1]:02d}"
            day_open = float(day_spot.iloc[0]["open"])
            day_cands = []
            # ---- PE (S8 path, parameterised) ----
            setup, direction, sig = find_signal(day_spot, pdh, pdc, pdl, bias, scale)
            if setup is not None and direction == "PE":
                sig_idx = next((j for j, c in enumerate(candles) if str(c["timestamp"]) == str(sig["timestamp"])), None)
                if sig_idx is not None:
                    if second_close:
                        ok = sig_idx + 2 < len(candles) and float(candles[sig_idx + 1]["close"]) < float(sig["close"])
                        eidx = sig_idx + 2; stop = max(float(sig["high"]), float(candles[sig_idx + 1]["high"])) if ok else None
                    else:
                        ok = sig_idx + 1 < len(candles); eidx = sig_idx + 1; stop = float(sig["high"])
                    if ok:
                        entry = float(candles[eidx]["open"]); risk = stop - entry
                        if risk > 0:
                            target = entry - 2 * risk
                            levels = sorted(set([pdh, pdc, pdl])); nxt = [l for l in levels if l < entry]
                            room = entry - max(nxt) if nxt else None
                            tnet = round(2 * risk * QTY - COST, 2)
                            if room is not None and room >= room_min * risk and tnet >= tnet_min and not (nifty_block and nb == "bullish"):
                                crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
                                out = replay(crecs, eidx, entry, stop, target, "PE")
                                day_cands.append({"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                                    "setup": setup, "direction": "PE", "bias": bias, "signal_time": str(sig["timestamp"]),
                                    "confirm_time": str(candles[sig_idx + 1]["timestamp"]) if second_close else "",
                                    "entry_time": candles[eidx]["time"], "entry": round(entry, 2), "stop": round(stop, 2),
                                    "target": round(target, 2), "risk": round(risk, 2), "room": round(room, 2),
                                    "room_ratio": round(room / risk, 3), "target_net_rs": tnet, "orh": orh, "orl": orl,
                                    "nifty_bias": nb, **out})
            # ---- CE pullback (S8 path, parameterised) ----
            allowed_ce = not (bias == "bearish")
            if allowed_ce and not (nifty_block and nb == "bearish"):
                levels = sorted(set([pdh, pdc, pdl])); arm_idx = None
                for j, c in enumerate(candles):
                    if c["time"] > "14:30": break
                    close = float(c["close"])
                    if close > orh and close > pdc and close < pdh:
                        nxt = [l for l in levels if l > close]; room = (min(nxt) - close) if nxt else float("inf")
                        if room >= 200 * scale: arm_idx = j; break
                if arm_idx is not None:
                    pb_idx = None
                    for j in range(arm_idx + 1, len(candles)):
                        c = candles[j]
                        if c["time"] > "14:30": break
                        if abs(float(c["low"]) - orh) <= 40 * scale and float(c["close"]) > orh and float(c["close"]) > float(c["open"]):
                            pb_idx = j; break
                    if pb_idx is not None:
                        if second_close:
                            ok = pb_idx + 2 < len(candles) and float(candles[pb_idx + 1]["close"]) > float(candles[pb_idx]["close"])
                            eidx = pb_idx + 2
                        else:
                            ok = pb_idx + 1 < len(candles); eidx = pb_idx + 1
                        if ok:
                            entry = float(candles[eidx]["open"]); stop = float(candles[pb_idx]["low"]); risk = entry - stop
                            if risk > 0:
                                target = entry + 2 * risk; nxt = [l for l in levels if l > entry]
                                room = min(nxt) - entry if nxt else None; tnet = round(2 * risk * QTY - COST, 2)
                                if room is not None and room >= room_min * risk and tnet >= tnet_min:
                                    crecs = [{"time": c["time"], "high": float(c["high"]), "low": float(c["low"]), "close": float(c["close"])} for c in candles]
                                    out = replay(crecs, eidx, entry, stop, target, "CE")
                                    day_cands.append({"symbol": sym, "date": d.date().isoformat(), "month": d.month, "week": week,
                                        "setup": "setup4_pullback", "direction": "CE", "bias": bias, "signal_time": str(candles[pb_idx]["timestamp"]),
                                        "confirm_time": str(candles[pb_idx + 1]["timestamp"]) if second_close else "",
                                        "entry_time": candles[eidx]["time"], "arm_time": candles[arm_idx]["time"],
                                        "entry": round(entry, 2), "stop": round(stop, 2), "target": round(target, 2),
                                        "risk": round(risk, 2), "room": round(room, 2), "room_ratio": round(room / risk, 3),
                                        "target_net_rs": tnet, "orh": orh, "orl": orl, "nifty_bias": nb, **out})
            if day_cands:
                day_cands.sort(key=lambda t: (t["entry_time"], -t["target_net_rs"]))
                cands.append(day_cands[0])
    return cands

# ---------- gate variants (Family D) ----------
def gate_variant(pool, events, mode):
    if mode == "D0_nogate":
        tagged = []
        for c in pool:
            t = dict(c); tier, passed, nt, nd, ph = tag_candidate(c, events)
            t.update({"gate_tier": tier, "gate_pass": True, "nearest_event_type": nt, "nearest_event_date": nd, "event_phase": ph})
            tagged.append(t)
        capped, _ = cap_select_daily(tagged); return tagged, capped
    survivors, blocked, tagged = gate_filter(pool, events)
    if mode == "D1_s9":
        capped, _ = cap_select_gate(survivors); return survivors, capped
    if mode == "D2_s11":
        surv2 = []
        for t in survivors:
            if t["gate_tier"] == "no_event" and not (t["room_ratio"] >= 2.0 and t["target_net_rs"] >= 1000): continue
            surv2.append(t)
        # blocked no-event single-bar passes must also be excluded: gate_filter already passed them under OR;
        # rebuild: survivors under AND = survivors minus no_event failing AND (above) — correct.
        capped, _ = cap_select_gate(surv2); return surv2, capped
    if mode == "D3_noevent_base":
        surv3 = []
        for c in pool:
            tier, passed, nt, nd, ph = tag_candidate(c, events)
            t = dict(c); t.update({"gate_tier": tier, "nearest_event_type": nt, "nearest_event_date": nd, "event_phase": ph})
            # no_event: pass at S8 base (already room>=1.5 in pool); single_news keeps room>=2
            p = True if tier != "single_news" else (c["room_ratio"] >= 2.0)
            t["gate_pass"] = p
            if p: surv3.append(t)
        capped, _ = cap_select_gate(surv3); return surv3, capped
    if mode == "D4_eventonly":
        surv4 = [t for t in survivors if t["gate_tier"] != "no_event"]
        capped, _ = cap_select_gate(surv4); return surv4, capped
    raise ValueError(mode)

if __name__ == "__main__":
    events = build_events(trading_days_list())
    s9_capped = list(csv.DictReader(open(os.path.expanduser("~/workspace/trading/s9_trades_jan_oct_2026.csv"))))
    for t in s9_capped:
        t["month"] = int(t["month"]); t["net_rs"] = float(t["net_rs"]); t["full_target"] = t["full_target"] in ("True", True)
    results = {}
    print("== Family A ==")
    famA = family_A(s9_capped)
    print("E0 validation diffs:", famA.pop("_E0_validation_diffs"))
    for k, v in famA.items():
        results[f"A_{k}"] = v["metrics"]; print(k, json.dumps(v["metrics"]))
        write_csv(f"{OUTDIR}/A_{k}.csv", v["trades"])
    print("== Family B ==")
    bvars = {
        "B0_baseline": dict(),
        "B1_prosp250": dict(tnet_min=250.0),
        "B2_room125": dict(room_min=1.25),
        "B3_room100": dict(room_min=1.0),
        "B4_orwide": dict(or_lo=0.0015, or_hi=0.040),
        "B5_nosecond": dict(second_close=False),
        "B6_noniftyblock": dict(nifty_block=False),
        "B7_combo_loose": dict(tnet_min=250.0, room_min=1.25, or_lo=0.0015, or_hi=0.040),
        "B8_combo_nosecond_loose": dict(tnet_min=250.0, room_min=1.25, or_lo=0.0015, or_hi=0.040, second_close=False),
    }
    pools = {}
    for name, kw in bvars.items():
        pool = gen_candidates(**kw); pools[name] = pool
        surv, capped = gate_variant(pool, events, "D1_s9")
        results[f"B_{name}"] = split_metrics(capped)
        print(name, "pool", len(pool), json.dumps(results[f"B_{name}"]))
        write_csv(f"{OUTDIR}/B_{name}_capped.csv", capped); write_csv(f"{OUTDIR}/B_{name}_pool.csv", pool)
    print("== Family C (on B0 pool and on best-B pool by Oct net) ==")
    # best B by oct net among B1..B8
    cand_names = [n for n in bvars if n != "B0_baseline"]
    bestB = max(cand_names, key=lambda n: results[f"B_{n}"]["oct"]["net_rs"])
    print("bestB by Oct net:", bestB)
    for src_name, pool in [("B0", pools["B0_baseline"]), ("BESTB", pools[bestB])]:
        for cname, filt in [("C1_PEonly", lambda t: t["direction"] == "PE"), ("C2_CEonly", lambda t: t["direction"] == "CE")]:
            sub = [t for t in pool if filt(t)]
            surv, capped = gate_variant(sub, events, "D1_s9")
            key = f"C_{src_name}_{cname}"; results[key] = split_metrics(capped)
            print(key, json.dumps(results[key])); write_csv(f"{OUTDIR}/{key}_capped.csv", capped)
    print("== Family D (on B0 pool and best-B pool) ==")
    for src_name, pool in [("B0", pools["B0_baseline"]), ("BESTB", pools[bestB])]:
        for mode in ["D0_nogate", "D1_s9", "D2_s11", "D3_noevent_base", "D4_eventonly"]:
            surv, capped = gate_variant(pool, events, mode)
            key = f"D_{src_name}_{mode}"; results[key] = split_metrics(capped)
            print(key, json.dumps(results[key])); write_csv(f"{OUTDIR}/{key}_capped.csv", capped)
    results["_bestB_by_oct_net"] = bestB
    results["_poolsizes"] = {k: len(v) for k, v in pools.items()}
    with open(os.path.expanduser("~/workspace/trading/stocks_oct_tuning_results.json"), "w") as f:
        json.dump(results, f, indent=2, default=str)
    print("done")
