#!/usr/bin/env python3
"""Score NS1-NS6 new index-options setups, Jan-Oct 2026 spot (paper only, no orders).
Implements ONLY the frozen definitions in index_options_newsetup_ns*_frozen.md.
Spot provisional = points x 100 shares - Rs 40/leg. NOT an options-lot profit.
Verification: October Skill S1 must reproduce 8 Nifty / 9 Bank taken; V4 must
reproduce 4 Nifty / 5 Bank uncapped candidates (family C base)."""
import sys, os, math, json
sys.path.insert(0, "/home/hatch/workspace/trading")
import pandas as pd
from daytrader_cash_backtest import bias_of, find_signal, run_day

BASE = os.path.expanduser("~/workspace/trading/data/progressive")
OUT = os.path.expanduser("~/workspace/trading")

def load(sym):
    spot = pd.read_csv(os.path.join(BASE, sym, "spot_5m.csv"))
    daily = pd.read_csv(os.path.join(BASE, sym, "spot_daily.csv"))
    ts = pd.to_datetime(spot["timestamp"])
    if getattr(ts.dt, "tz", None) is not None:
        ts = ts.dt.tz_localize(None)
    spot["timestamp"] = ts
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    daily["date"] = pd.to_datetime(daily["date"]).dt.normalize()
    return spot.sort_values("timestamp"), daily.sort_values("date")

DATA = {}
for sym in ("NIFTY", "BANKNIFTY"):
    DATA[sym] = load(sym)

def day_info(sym, date):
    """Return dict with bars (list of dicts), orh, orl, pdh, pdc, pdl, bias, scale, day_open."""
    spot, daily = DATA[sym]
    dl = daily.to_dict("records")
    idx = next(i for i, r in enumerate(dl) if r["date"] == date)
    if idx == 0:
        return None
    prev = dl[idx - 1]
    day = spot[spot["date"] == date].sort_values("timestamp")
    if day.empty:
        return None
    bars = [{"time": t, "open": float(o), "high": float(h), "low": float(l), "close": float(c)}
            for t, o, h, l, c in zip(day["time"], day["open"], day["high"], day["low"], day["close"])]
    or_c = [b for b in bars if b["time"] < "09:30"]
    if not or_c:
        return None
    orh, orl = max(b["high"] for b in or_c), min(b["low"] for b in or_c)
    bias, _ = bias_of(prev)
    return {"bars": bars, "orh": orh, "orl": orl, "pdh": float(prev["high"]), "pdc": float(prev["close"]),
            "pdl": float(prev["low"]), "bias": bias, "scale": float(prev["close"]) / 55000.0,
            "open": bars[0]["open"]}

def room_ratio(close, direction, info, risk):
    lv = sorted({info["pdh"], info["pdc"], info["pdl"]})
    if direction == "CE":
        nxt = [l for l in lv if l > close]
        room = (min(nxt) - close) if nxt else math.inf
    else:
        nxt = [l for l in lv if l < close]
        room = (close - max(nxt)) if nxt else math.inf
    return room / risk if risk else 0.0, room

def replay(bars, sig_idx, direction):
    """Common spot exit. Returns trade dict or None if no entry bar / risk 0."""
    if sig_idx + 1 >= len(bars):
        return None
    entry = bars[sig_idx + 1]["open"]
    sig = bars[sig_idx]
    stop = sig["low"] if direction == "CE" else sig["high"]
    risk = abs(entry - stop)
    if risk == 0:
        return None
    target = entry + 2 * risk if direction == "CE" else entry - 2 * risk
    for j in range(sig_idx + 1, len(bars)):
        b = bars[j]
        if b["time"] > "15:10":
            break
        if direction == "CE":
            if b["low"] <= stop:
                return {"entry": entry, "entry_time": b["time"], "stop": stop, "target": target,
                        "exit": stop, "exit_time": b["time"], "exit_reason": "stop", "risk": risk}
            if b["high"] >= target:
                return {"entry": entry, "entry_time": b["time"], "stop": stop, "target": target,
                        "exit": target, "exit_time": b["time"], "exit_reason": "target", "risk": risk}
        else:
            if b["high"] >= stop:
                return {"entry": entry, "entry_time": b["time"], "stop": stop, "target": target,
                        "exit": stop, "exit_time": b["time"], "exit_reason": "stop", "risk": risk}
            if b["low"] <= target:
                return {"entry": entry, "entry_time": b["time"], "stop": stop, "target": target,
                        "exit": target, "exit_time": b["time"], "exit_reason": "target", "risk": risk}
        if b["time"] == "15:10":
            return {"entry": entry, "entry_time": b["time"], "stop": stop, "target": target,
                    "exit": b["close"], "exit_time": b["time"], "exit_reason": "square_off", "risk": risk}
    # no 15:10 bar reached (should not happen): square off at last bar <= 15:10
    last = [b for b in bars if b["time"] <= "15:10"][-1]
    return {"entry": entry, "entry_time": bars[sig_idx + 1]["time"], "stop": stop, "target": target,
            "exit": last["close"], "exit_time": last["time"], "exit_reason": "square_off", "risk": risk}

def net_of(tr, direction):
    pts = (tr["exit"] - tr["entry"]) if direction == "CE" else (tr["entry"] - tr["exit"])
    return pts * 100 - 40

def s1_signal(info):
    """First OR break 09:30-11:30. Returns (idx, dir, status) status in taken/blocked/none."""
    bars = info["bars"]
    for i, b in enumerate(bars):
        if b["time"] < "09:30" or b["time"] > "11:30":
            continue
        if b["close"] > info["orh"]:
            if info["bias"] == "bearish":
                return i, "CE", "blocked"
            return i, "CE", "taken"
        if b["close"] < info["orl"]:
            if b["time"] == "09:30" and not (b["close"] < info["pdl"]):
                return i, "PE", "blocked"
            return i, "PE", "taken"
    return None, None, "none"

def s1_trade(info):
    i, d, st = s1_signal(info)
    if st != "taken":
        return None, st, i, d
    tr = replay(info["bars"], i, d)
    if tr is None:
        return None, "none", i, d
    rr, _ = room_ratio(info["bars"][i]["close"], d, info, tr["risk"])
    # NOTE: base S1 has no room gate in its frozen definition; room shown for info only.
    return (tr, i, d, rr), st, i, d

def confirmer_broke(conf_info, direction, t_max, t_min="09:30"):
    """First confirmer break bar time <= t_max (and >= t_min), or None. Direction fixed."""
    for b in conf_info["bars"]:
        if b["time"] < t_min or b["time"] > t_max:
            continue
        if direction == "CE" and b["close"] > conf_info["orh"]:
            return b["time"]
        if direction == "PE" and b["close"] < conf_info["orl"]:
            return b["time"]
    return None

def confirmer_broke_by(conf_info, direction, sig_time):
    for b in conf_info["bars"]:
        if b["time"] < "09:30" or b["time"] > sig_time:
            continue
        if direction == "CE" and b["close"] > conf_info["orh"]:
            return True
        if direction == "PE" and b["close"] < conf_info["orl"]:
            return True
    return False

def make_row(fam, sym, date, leg, sig_time, direction, tr, extra=""):
    return {"family": fam, "index": sym, "date": date, "leg": leg, "direction": direction,
            "signal_time": sig_time, "entry_time": tr["entry_time"], "entry_spot": round(tr["entry"], 2),
            "stop_spot": round(tr["stop"], 2), "target_spot": round(tr["target"], 2),
            "exit_spot": round(tr["exit"], 2), "exit_time": tr["exit_time"],
            "exit_reason": tr["exit_reason"], "full_target": 1 if tr["exit_reason"] == "target" else 0,
            "spot_net_provisional_rs": round(net_of(tr, direction), 2), "note": extra}

def score_day(sym, date, infos):
    info, conf = infos[sym], infos["BANKNIFTY" if sym == "NIFTY" else "NIFTY"]
    bars = info["bars"]
    rows = {"NS1": [], "NS2": [], "NS3": [], "NS4": [], "NS5a": [], "NS5b": [], "NS6": []}
    # ---- base S1 ----
    s1, s1_status, s1_idx, s1_dir = s1_trade(info)
    # ---- NS1: base + second crossing after target/stop exit <=13:30 ----
    if s1 is not None:
        tr, i, d, _ = s1
        rows["NS1"].append(make_row("NS1", sym, date, "base_S1", bars[i]["time"], d, tr))
        if tr["exit_reason"] in ("target", "stop") and tr["exit_time"] <= "13:30":
            exit_idx = next(j for j, b in enumerate(bars) if b["time"] == tr["exit_time"])
            for j in range(exit_idx + 1, len(bars)):
                b = bars[j]
                if b["time"] > "14:30":
                    break
                prev = bars[j - 1]
                d2 = None
                if b["close"] > info["orh"] and not (prev["close"] > info["orh"]):
                    d2 = "CE"
                elif b["close"] < info["orl"] and not (prev["close"] < info["orl"]):
                    d2 = "PE"
                if d2 is None:
                    continue
                if d2 == "CE" and info["bias"] == "bearish":
                    break  # first crossing blocked -> no second (first-candidate discipline)
                tr2 = replay(bars, j, d2)
                if tr2 is None:
                    break
                rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
                if rr < 1.5:
                    break
                rows["NS1"].append(make_row("NS1", sym, date, "second", b["time"], d2, tr2))
                break
    # ---- NS2: morning S1 + afternoon leg only on no-morning-trade days ----
    if s1 is not None:
        tr, i, d, _ = s1
        rows["NS2"].append(make_row("NS2", sym, date, "morning_S1", bars[i]["time"], d, tr))
    else:
        for j, b in enumerate(bars):
            if b["time"] <= "11:30" or b["time"] > "14:30":
                continue
            d2 = "CE" if b["close"] > info["orh"] else ("PE" if b["close"] < info["orl"] else None)
            if d2 is None:
                continue
            if not confirmer_broke_by(conf, d2, b["time"]):
                continue
            if d2 == "CE" and info["bias"] == "bearish":
                break
            tr2 = replay(bars, j, d2)
            if tr2 is None:
                break
            rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
            if rr < 1.5:
                break
            rows["NS2"].append(make_row("NS2", sym, date, "afternoon_rescan", b["time"], d2, tr2))
            break
    # ---- NS3: gap class ----
    gap = (info["open"] - info["pdc"]) / info["pdc"] * 100
    width = (info["orh"] - info["orl"]) / info["pdc"] * 100
    if gap >= 0.25:
        cls, setup = "gap_up", "NS3-GU"
        for j, b in enumerate(bars):
            if b["time"] < "09:30" or b["time"] > "13:30":
                continue
            if b["close"] < info["orl"] and b["close"] < info["pdc"]:
                tr2 = replay(bars, j, "PE")
                if tr2 is not None:
                    rr, _ = room_ratio(b["close"], "PE", info, tr2["risk"])
                    if rr >= 1.5:
                        rows["NS3"].append(make_row("NS3", sym, date, setup, b["time"], "PE", tr2,
                                                     f"gap={gap:.2f}% width={width:.2f}%"))
                break
    elif gap <= -0.25:
        for j, b in enumerate(bars):
            if b["time"] < "09:30" or b["time"] > "13:30":
                continue
            d2 = None
            if b["close"] > info["orh"] and confirmer_broke_by(conf, "CE", b["time"]):
                d2 = "CE"
            elif b["close"] < info["orl"]:
                d2 = "PE"
            if d2 is None:
                continue
            if d2 == "CE" and info["bias"] == "bearish":
                break
            tr2 = replay(bars, j, d2)
            if tr2 is not None:
                rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
                if rr >= 1.5:
                    rows["NS3"].append(make_row("NS3", sym, date, "NS3-GD", b["time"], d2, tr2,
                                                 f"gap={gap:.2f}% width={width:.2f}%"))
            break
    else:
        if width < 0.35:
            for j, b in enumerate(bars):
                if b["time"] < "09:30" or b["time"] > "13:30":
                    continue
                d2 = "CE" if b["close"] > info["orh"] else ("PE" if b["close"] < info["orl"] else None)
                if d2 is None:
                    continue
                if d2 == "CE" and info["bias"] == "bearish":
                    break
                tr2 = replay(bars, j, d2)
                if tr2 is not None:
                    rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
                    if rr >= 1.5:
                        rows["NS3"].append(make_row("NS3", sym, date, "NS3-FLAT", b["time"], d2, tr2,
                                                     f"gap={gap:.2f}% width={width:.2f}%"))
                break
    # ---- NS4: first break -> inside close -> confirmed re-break ----
    first_idx, first_dir = None, None
    for j, b in enumerate(bars):
        if b["time"] < "09:30" or b["time"] > "13:30":
            continue
        if b["close"] > info["orh"]:
            first_idx, first_dir = j, "CE"
            break
        if b["close"] < info["orl"]:
            first_idx, first_dir = j, "PE"
            break
    if first_idx is not None:
        inside_idx = None
        for j in range(first_idx + 1, len(bars)):
            b = bars[j]
            if b["time"] > "14:30":
                break
            if info["orl"] <= b["close"] <= info["orh"]:
                inside_idx = j
                break
        if inside_idx is not None:
            for j in range(inside_idx + 1, len(bars)):
                b = bars[j]
                if b["time"] > "14:30":
                    break
                prev = bars[j - 1]
                ok = (first_dir == "CE" and b["close"] > info["orh"] and not (prev["close"] > info["orh"])) or \
                     (first_dir == "PE" and b["close"] < info["orl"] and not (prev["close"] < info["orl"]))
                if not ok:
                    continue
                if not confirmer_broke_by(conf, first_dir, b["time"]):
                    continue
                if first_dir == "CE" and info["bias"] == "bearish":
                    break
                tr2 = replay(bars, j, first_dir)
                if tr2 is not None:
                    rr, _ = room_ratio(b["close"], first_dir, info, tr2["risk"])
                    if rr >= 1.5:
                        rows["NS4"].append(make_row("NS4", sym, date, "or_rebreak", b["time"], first_dir, tr2,
                                                     f"first_break={bars[first_idx]['time']} inside={bars[inside_idx]['time']}"))
                break
    # ---- NS5a: confirmer first break <=11:30, then rescan <=13:30 ----
    for d2 in ("CE", "PE"):
        ct = confirmer_broke(conf, d2, "11:30")
        if ct is None:
            continue
        # direction = first confirmer break overall; handle by checking earliest of CE/PE below
        break
    ct_ce = confirmer_broke(conf, "CE", "11:30")
    ct_pe = confirmer_broke(conf, "PE", "11:30")
    if ct_ce is not None or ct_pe is not None:
        if ct_ce is not None and (ct_pe is None or ct_ce <= ct_pe):
            d5, ct = "CE", ct_ce
        else:
            d5, ct = "PE", ct_pe
        for j, b in enumerate(bars):
            if b["time"] < ct or b["time"] > "13:30":
                continue
            if (d5 == "CE" and b["close"] > info["orh"]) or (d5 == "PE" and b["close"] < info["orl"]):
                if d5 == "CE" and info["bias"] == "bearish":
                    break
                if d5 == "PE" and b["time"] == "09:30" and not (b["close"] < info["pdl"]):
                    break
                tr2 = replay(bars, j, d5)
                if tr2 is not None:
                    rr, _ = room_ratio(b["close"], d5, info, tr2["risk"])
                    if rr >= 1.5:
                        rows["NS5a"].append(make_row("NS5a", sym, date, "skill_rescan", b["time"], d5, tr2,
                                                      f"confirmer_break={ct}"))
                break
    # ---- NS5b: confirmer OR-high break <=11:30, rescan close > ORH and > PDH ----
    ct = confirmer_broke(conf, "CE", "11:30")
    if ct is not None and info["bias"] != "bearish":
        for j, b in enumerate(bars):
            if b["time"] < ct or b["time"] > "13:30":
                continue
            if b["close"] > info["orh"] and b["close"] > info["pdh"]:
                tr2 = replay(bars, j, "CE")
                if tr2 is not None:
                    rr, _ = room_ratio(b["close"], "CE", info, tr2["risk"])
                    if rr >= 1.5:
                        rows["NS5b"].append(make_row("NS5b", sym, date, "ce_mirror_rescan", b["time"], "CE", tr2,
                                                      f"confirmer_break={ct}"))
                break
    # ---- NS6: session-range breakout on no-morning-trade days ----
    if s1 is None:
        sess = [b for b in bars if b["time"] <= "13:00"]
        sh, sl = max(b["high"] for b in sess), min(b["low"] for b in sess)
        csess = [b for b in conf["bars"] if b["time"] <= "13:00"]
        csh, csl = max(b["high"] for b in csess), min(b["low"] for b in csess)
        for j, b in enumerate(bars):
            if b["time"] <= "13:00" or b["time"] > "14:30":
                continue
            d2 = "CE" if b["close"] > sh else ("PE" if b["close"] < sl else None)
            if d2 is None:
                continue
            conf_ok = any((cb["time"] >= "09:30" and cb["time"] <= b["time"] and
                           ((d2 == "CE" and cb["close"] > csh) or (d2 == "PE" and cb["close"] < csl)))
                          for cb in conf["bars"])
            if not conf_ok:
                continue
            if d2 == "CE" and info["bias"] == "bearish":
                break
            tr2 = replay(bars, j, d2)
            if tr2 is not None:
                rr, _ = room_ratio(b["close"], d2, info, tr2["risk"])
                if rr >= 1.5:
                    rows["NS6"].append(make_row("NS6", sym, date, "session_range_break", b["time"], d2, tr2))
            break
    return rows

def main():
    all_rows = {f: [] for f in ("NS1", "NS2", "NS3", "NS4", "NS5a", "NS5b", "NS6")}
    base_s1, base_v4 = [], []
    days = {}
    for sym in ("NIFTY", "BANKNIFTY"):
        _, daily = DATA[sym]
        dates = [d for d in daily["date"] if pd.Timestamp("2026-01-01") <= d <= pd.Timestamp("2026-10-28")]
        days[sym] = len(dates)
        for date in dates:
            ds = date.date().isoformat()
            infos = {}
            ok = True
            for s in ("NIFTY", "BANKNIFTY"):
                infos[s] = day_info(s, date)
                if infos[s] is None:
                    ok = False
            if not ok:
                continue
            r = score_day(sym, ds, infos)
            for f, lst in r.items():
                all_rows[f].extend(lst)
            # baselines (same day, traded index only)
            info = infos[sym]
            s1, st, i, d = s1_trade(info)
            if s1 is not None:
                tr, ii, dd, _ = s1
                base_s1.append(make_row("BASE_S1", sym, ds, "morning_S1", info["bars"][ii]["time"], dd, tr))
            # V4 via imported engine (needs day_spot df with time col)
            spot, daily2 = DATA[sym]
            day = spot[spot["date"] == date].copy()
            day["time"] = day["timestamp"].dt.strftime("%H:%M")
            prev = daily2[daily2["date"] < date].iloc[-1]
            bias, _ = bias_of(prev)
            scale = float(prev["close"]) / 55000.0
            res = run_day(day, float(prev["high"]), float(prev["close"]), float(prev["low"]), bias, scale, 100, 40)
            if res["setup"] not in (None, "no_trade"):
                base_v4.append({"family": "BASE_V4", "index": sym, "date": ds, "leg": res["setup"],
                                "direction": res["direction"], "signal_time": str(res["signal_time"]),
                                "entry_time": "", "entry_spot": res["entry_price"],
                                "exit_reason": res["exit_reason"], "full_target": 1 if res["exit_reason"] == "target" else 0,
                                "spot_net_provisional_rs": round(float(res["net_rs"]), 2), "note": ""})
    import csv
    for f, lst in all_rows.items():
        p = os.path.join(OUT, f"index_options_newsetup_{f.lower()}_trades_jan_oct_2026.csv")
        with open(p, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(lst[0].keys()) if lst else
                               ["family", "index", "date", "leg", "direction", "signal_time"])
            w.writeheader()
            w.writerows(lst)
        print(f, len(lst))
    with open(os.path.join(OUT, "index_options_newsetup_base_s1_trades_jan_oct_2026.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(base_s1[0].keys()))
        w.writeheader(); w.writerows(base_s1)
    with open(os.path.join(OUT, "index_options_newsetup_base_v4_trades_jan_oct_2026.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(base_v4[0].keys()))
        w.writeheader(); w.writerows(base_v4)
    print("BASE_S1", len(base_s1), "BASE_V4", len(base_v4), "days", days)
    # October verification
    for f, lst in list(all_rows.items()) + [("BASE_S1", base_s1), ("BASE_V4", base_v4)]:
        octr = [r for r in lst if "2026-10-01" <= r["date"] <= "2026-10-28"]
        for sym in ("NIFTY", "BANKNIFTY"):
            o = [r for r in octr if r["index"] == sym]
            print(f, "OCT", sym, len(o), "net", round(sum(r["spot_net_provisional_rs"] for r in o), 2),
                  "FT", sum(r["full_target"] for r in o))

if __name__ == "__main__":
    main()
