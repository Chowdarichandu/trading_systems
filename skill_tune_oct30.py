#!/usr/bin/env python3
"""Skill-only October tuning, frozen defs in index_options_skill_tuned_oct30_frozen.md.
Paper only, no orders. Spot screen for all variants; premium score from CACHED
contract-day files only (v4_options_oct_data/candles_premium_*.json + legacy).
No browser fetch in this run (subagent cannot run live-browser tasks)."""
import csv, json, math, re
from pathlib import Path
import pandas as pd

BASE = Path.home() / "workspace/trading/data/progressive"
OUTD = Path.home() / "workspace/trading/v4_options_oct_data"
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
OCT = [d for d in pd.bdate_range("2026-10-01", "2026-10-28")]
OCTD = {d.strftime("%Y-%m-%d") for d in OCT}

def load(sym):
    spot = pd.read_csv(BASE / sym / "spot_5m.csv", parse_dates=["timestamp"])
    daily = pd.read_csv(BASE / sym / "spot_daily.csv", parse_dates=["date"])
    spot["timestamp"] = pd.to_datetime(spot["timestamp"]).dt.tz_localize(None)
    daily["date"] = pd.to_datetime(daily["date"]).dt.tz_localize(None).dt.normalize()
    spot["date"] = spot["timestamp"].dt.normalize()
    spot["time"] = spot["timestamp"].dt.strftime("%H:%M")
    return spot, daily

def prev_daily(daily, date):
    prev = daily[daily["date"] < pd.Timestamp(date)]
    return prev.iloc[-1] if len(prev) else None

def bias_cs(prev):
    rng = prev["high"] - prev["low"]
    cs = (prev["close"] - prev["low"]) / rng * 100 if rng else 50.0
    return cs

def replay(day, sig_idx, direction):
    """day: reset df for one date. sig_idx: positional index of signal bar.
    Returns dict or None (risk 0)."""
    sig = day.iloc[sig_idx]
    if sig_idx + 1 >= len(day):
        return None
    entry = float(day.iloc[sig_idx + 1]["open"])
    stop = float(sig["low"]) if direction == "CE" else float(sig["high"])
    risk = abs(entry - stop)
    if risk == 0:
        return None
    target = entry + 2 * risk if direction == "CE" else entry - 2 * risk
    for j in range(sig_idx + 1, len(day)):
        bar = day.iloc[j]; t = bar["time"]
        if t > "15:10":
            break
        lo, hi, cl = float(bar["low"]), float(bar["high"]), float(bar["close"])
        if direction == "CE":
            if lo <= stop:
                return {"entry": entry, "exit": stop, "reason": "stop", "exit_time": t,
                        "net": (stop - entry) * 100 - 40, "entry_time": day.iloc[sig_idx + 1]["time"]}
            if hi >= target:
                return {"entry": entry, "exit": target, "reason": "target", "exit_time": t,
                        "net": (target - entry) * 100 - 40, "entry_time": day.iloc[sig_idx + 1]["time"]}
        else:
            if hi >= stop:
                return {"entry": entry, "exit": stop, "reason": "stop", "exit_time": t,
                        "net": (entry - stop) * 100 - 40, "entry_time": day.iloc[sig_idx + 1]["time"]}
            if lo <= target:
                return {"entry": entry, "exit": target, "reason": "target", "exit_time": t,
                        "net": (entry - target) * 100 - 40, "entry_time": day.iloc[sig_idx + 1]["time"]}
        if t == "15:10":
            ex = cl
            net = (ex - entry) * 100 - 40 if direction == "CE" else (entry - ex) * 100 - 40
            return {"entry": entry, "exit": ex, "reason": "square_off", "exit_time": t, "net": net,
                    "entry_time": day.iloc[sig_idx + 1]["time"]}
    # fallback: last bar <=15:10
    bar = day.iloc[-1]
    ex = float(bar["close"])
    net = (ex - entry) * 100 - 40 if direction == "CE" else (entry - ex) * 100 - 40
    return {"entry": entry, "exit": ex, "reason": "square_off", "exit_time": bar["time"], "net": net,
            "entry_time": day.iloc[sig_idx + 1]["time"]}

def room_ratio(close, direction, risk, pdh, pdc, pdl):
    lvls = sorted(set([pdh, pdc, pdl]))
    if direction == "CE":
        nxt = [l for l in lvls if l > close]
        room = (min(nxt) - close) if nxt else math.inf
    else:
        nxt = [l for l in lvls if l < close]
        room = (close - max(nxt)) if nxt else math.inf
    return room / risk if risk else 0

def run_variant(sym, variant):
    spot, daily = load(sym)
    trades = []  # each: date, leg, direction, signal_time, entry_spot, spot_net, spot_reason, extra
    raw_log = []
    for dstr in sorted(OCTD):
        day = spot[spot["date"] == pd.Timestamp(dstr)].reset_index(drop=True)
        if len(day) == 0:
            continue
        prev = prev_daily(daily, dstr)
        if prev is None:
            continue
        pdh, pdc, pdl = float(prev["high"]), float(prev["close"]), float(prev["low"])
        cs = bias_cs(prev)
        bear = cs < 35
        # OR window per variant
        if variant == "V5":
            or_mask, win_start = day["time"] < "09:45", "09:45"
        elif variant == "V6":
            or_mask, win_start = day["time"] < "09:25", "09:25"
        else:
            or_mask, win_start = day["time"] < "09:30", "09:30"
        or_c = day[or_mask]
        if or_c.empty:
            continue
        orh, orl = float(or_c["high"].max()), float(or_c["low"].min())
        win = day[(day["time"] >= win_start) & (day["time"] <= "11:30")].reset_index(drop=True)
        # find first signal in win (positional in day)
        sig_pos, sig_dir = None, None
        for k, (_, c) in enumerate(win.iterrows()):
            if float(c["close"]) > orh:
                sig_pos = day.index[day["time"] == c["time"]][0] if False else None
                break
        # simpler: iterate day rows in window order
        sig_idx, sig_dir = None, None
        for i, (_, c) in enumerate(day.iterrows()):
            if c["time"] < win_start or c["time"] > "11:30":
                continue
            if float(c["close"]) > orh:
                sig_idx, sig_dir = i, "CE"; break
            if float(c["close"]) < orl:
                sig_idx, sig_dir = i, "PE"; break
        if sig_idx is None:
            raw_log.append((dstr, "no_signal", "", cs)); continue
        sig = day.iloc[sig_idx]
        stime = sig["time"]
        # --- S1 block handling per variant ---
        take = True; eff_idx, eff_dir = sig_idx, sig_dir; blocked = ""
        first_bar = (stime == win_start)
        if variant == "V11":
            if sig_dir == "PE" and first_bar:
                if float(sig["close"]) < pdl:
                    take = True
                else:
                    # rescan 09:35-11:30 for first close < PDL; abort if close > ORH first
                    found = None
                    for i in range(sig_idx + 1, len(day)):
                        c = day.iloc[i]
                        if c["time"] > "11:30":
                            break
                        if float(c["close"]) > orh:
                            break
                        if float(c["close"]) < pdl:
                            found = i; break
                    if found is not None:
                        eff_idx, eff_dir = found, "PE"; take = True
                    else:
                        take, blocked = False, "P-RESCAN_block"
            elif sig_dir == "CE" and bear:
                take, blocked = False, "CE_bearish"
        elif variant == "V1":
            # 09:30 PE low rule (win_start is 09:30 for V1)
            if sig_dir == "PE" and first_bar:
                take = float(sig["low"]) < pdl
                blocked = "" if take else "P-LOW_block"
            elif sig_dir == "CE" and bear:
                take, blocked = False, "CE_bearish"
        elif variant == "V2":
            if sig_dir == "PE" and first_bar:
                if float(sig["close"]) < pdl:
                    take = True
                else:
                    # next bar
                    if sig_idx + 1 < len(day) and float(day.iloc[sig_idx + 1]["close"]) < pdl:
                        eff_idx, eff_dir = sig_idx + 1, "PE"
                        take = True
                    else:
                        take, blocked = False, "P-2ND_block"
            elif sig_dir == "CE" and bear:
                take, blocked = False, "CE_bearish"
        elif variant == "V3":
            if sig_dir == "PE" and first_bar and float(sig["close"]) >= pdl:
                take, blocked = False, "0930_PE"
            # CE block removed
        elif variant == "V4":
            bear_w = cs < 25
            if sig_dir == "PE" and first_bar and float(sig["close"]) >= pdl:
                take, blocked = False, "0930_PE"
            elif sig_dir == "CE" and bear_w:
                take, blocked = False, "CE_bearish_wide"
        elif variant in ("V5", "V6"):
            if sig_dir == "PE" and first_bar and float(sig["close"]) >= pdl:
                take, blocked = False, "first_PE_PDL"
            elif sig_dir == "CE" and bear:
                take, blocked = False, "CE_bearish"
        else:  # base, V7, V8, V9, V10
            if sig_dir == "PE" and first_bar and float(sig["close"]) >= pdl:
                take, blocked = False, "0930_PE"
            elif sig_dir == "CE" and bear:
                take, blocked = False, "CE_bearish"
        raw_log.append((dstr, sig_dir, stime, round(cs, 2), round(pdl, 2),
                        float(sig["close"]), float(sig["low"]), blocked if not take else "taken"))
        if not take:
            continue
        # --- entry variants ---
        if variant == "V9":
            # pullback replaces direct entry
            pb_idx = None
            for i in range(eff_idx + 1, len(day)):
                c = day.iloc[i]
                if c["time"] > "14:30":
                    break
                if eff_dir == "CE" and float(c["low"]) <= orh and float(c["close"]) > orh:
                    pb_idx = i; break
                if eff_dir == "PE" and float(c["high"]) >= orl and float(c["close"]) < orl:
                    pb_idx = i; break
            if pb_idx is None:
                continue
            r = replay(day, pb_idx, eff_dir)
            if r is None:
                continue
            risk = abs(r["entry"] - (float(day.iloc[pb_idx]["low"]) if eff_dir == "CE" else float(day.iloc[pb_idx]["high"])))
            if room_ratio(float(day.iloc[pb_idx]["close"]), eff_dir, risk, pdh, pdc, pdl) < 1.5:
                continue
            trades.append({"index": sym, "date": dstr, "leg": "base", "direction": eff_dir,
                           "signal_time": day.iloc[pb_idx]["time"], "entry_spot": r["entry"],
                           "spot_net": round(r["net"], 2), "spot_reason": r["reason"],
                           "entry_time": r["entry_time"], "exit_time": r["exit_time"], "variant": variant})
            continue
        if variant == "V10":
            pb_idx = None
            for i in range(eff_idx + 1, len(day)):
                c = day.iloc[i]
                if c["time"] > "11:30":
                    break
                if eff_dir == "CE" and float(c["low"]) <= orh and float(c["close"]) > orh:
                    pb_idx = i; break
                if eff_dir == "PE" and float(c["high"]) >= orl and float(c["close"]) < orl:
                    pb_idx = i; break
            use_idx = eff_idx
            if pb_idx is not None:
                r0 = replay(day, pb_idx, eff_dir)
                if r0 is not None:
                    risk = abs(r0["entry"] - (float(day.iloc[pb_idx]["low"]) if eff_dir == "CE" else float(day.iloc[pb_idx]["high"])))
                    if room_ratio(float(day.iloc[pb_idx]["close"]), eff_dir, risk, pdh, pdc, pdl) >= 1.5:
                        use_idx = pb_idx
            r = replay(day, use_idx, eff_dir)
            if r is None:
                continue
            trades.append({"index": sym, "date": dstr, "leg": "base", "direction": eff_dir,
                           "signal_time": day.iloc[use_idx]["time"], "entry_spot": r["entry"],
                           "spot_net": round(r["net"], 2), "spot_reason": r["reason"],
                           "entry_time": r["entry_time"], "exit_time": r["exit_time"], "variant": variant})
            continue
        # direct entry (base, V1-V6, V7, V8)
        r = replay(day, eff_idx, eff_dir)
        if r is None:
            continue
        trades.append({"index": sym, "date": dstr, "leg": "base", "direction": eff_dir,
                       "signal_time": day.iloc[eff_idx]["time"], "entry_spot": r["entry"],
                       "spot_net": round(r["net"], 2), "spot_reason": r["reason"],
                       "entry_time": r["entry_time"], "exit_time": r["exit_time"], "variant": variant})
        if variant in ("V7", "V8") and r["reason"] == "stop":
            # find exit bar index: bar with time == exit_time, first occurrence after entry
            exit_idx = None
            for i in range(eff_idx + 1, len(day)):
                if day.iloc[i]["time"] == r["exit_time"]:
                    exit_idx = i; break
            if exit_idx is None:
                continue
            # scan after stop bar
            re_idx, re_dir = None, None
            for i in range(exit_idx + 1, len(day)):
                c = day.iloc[i]
                if c["time"] > "14:30":
                    break
                if variant == "V7":
                    if eff_dir == "CE" and float(c["close"]) > orh:
                        re_idx, re_dir = i, "CE"; break
                    if eff_dir == "PE" and float(c["close"]) < orl:
                        re_idx, re_dir = i, "PE"; break
                else:  # V8 opposite
                    if eff_dir == "CE" and float(c["close"]) < orl:
                        re_idx, re_dir = i, "PE"; break
                    if eff_dir == "PE" and float(c["close"]) > orh:
                        re_idx, re_dir = i, "CE"; break
            if re_idx is None:
                continue
            rr = replay(day, re_idx, re_dir)
            if rr is None:
                continue
            risk = abs(rr["entry"] - (float(day.iloc[re_idx]["low"]) if re_dir == "CE" else float(day.iloc[re_idx]["high"])))
            if room_ratio(float(day.iloc[re_idx]["close"]), re_dir, risk, pdh, pdc, pdl) < 1.5:
                continue
            trades.append({"index": sym, "date": dstr, "leg": "reentry", "direction": re_dir,
                           "signal_time": day.iloc[re_idx]["time"], "entry_spot": rr["entry"],
                           "spot_net": round(rr["net"], 2), "spot_reason": rr["reason"],
                           "entry_time": rr["entry_time"], "exit_time": rr["exit_time"], "variant": variant})
    return trades, raw_log

# ---------- premium scoring from cached files ----------
def build_premium_index():
    idx = {}  # (sym, date, strike, dir) -> list of (time, o,h,l,c) sorted
    legacy = {"NIFTY_22500PE_2026-10-23": "candles_Nifty_50_22500PE_2026-10-23.json",
              "NIFTY_22600CE_2026-10-26": "candles_Nifty_50_22600CE_2026-10-26.json",
              "BANKNIFTY_54300PE_2026-10-26": "candles_Nifty_Bank_54300PE_2026-10-26.json",
              "BANKNIFTY_54400PE_2026-10-23": "candles_Nifty_Bank_54400PE_2026-10-23.json",
              "BANKNIFTY_55200PE_2026-10-21": "candles_Nifty_Bank_55200PE_2026-10-21.json",
              "NIFTY_22500PE_2026-10-28": "candles_Nifty_50_22500PE_2026-10-28.json"}
    for f in OUTD.glob("candles_premium_*.json"):
        m = re.match(r"candles_premium_(NIFTY|BANKNIFTY)_(\d+)(CE|PE)_(\d{4}-\d{2}-\d{2})_", f.name)
        if not m:
            continue
        sym, strike, typ, date = m.group(1), int(m.group(2)), m.group(3), m.group(4)
        try:
            cs = json.loads(f.read_text())["data"]["candles"]
        except Exception:
            continue
        bars = sorted([(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs])
        idx[(sym, date, strike, typ)] = bars
    for tag, fn in legacy.items():
        parts = tag.split("_")
        sym, sd = parts[0], parts[2]
        m = re.match(r"(\d+)(CE|PE)", parts[1])
        strike, typ = int(m.group(1)), m.group(2)
        p = OUTD / fn
        if not p.exists():
            continue
        try:
            cs = json.loads(p.read_text())["data"]["candles"]
        except Exception:
            continue
        bars = sorted([(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs])
        idx[(sym, sd, strike, typ)] = bars
    return idx

def strike_of(entry_spot):
    return int(round(entry_spot / 100.0) * 100)

def prem_score(tr, pidx):
    sym, date = tr["index"], tr["date"]
    strike = strike_of(tr["entry_spot"])
    exp = "2026-11-03" if date == "2026-10-28" else "2026-10-27"
    bars = pidx.get((sym, date, strike, tr["direction"]))
    if not bars:
        return {"strike": strike, "expiry": exp, "premium_status": "NOT_COMPUTED"}
    sig = tr["signal_time"]
    eb = [b for b in bars if b[0] > sig]
    if not eb:
        return {"strike": strike, "expiry": exp, "premium_status": "NOT_COMPUTED"}
    etime, entry = eb[0][0], eb[0][1]
    stop, target = entry - 50.0, entry + 90.0
    for (t, o, h, l, cl) in eb:
        if t > "15:10":
            break
        if l <= stop:
            return {"strike": strike, "expiry": exp, "premium_status": "COMPUTED", "entry_premium": entry,
                    "entry_time": etime, "exit_premium": stop, "exit_time": t, "exit_reason": "stop",
                    "premium_net": round((stop - entry) * LOT[sym] - 220, 2)}
        if h >= target:
            return {"strike": strike, "expiry": exp, "premium_status": "COMPUTED", "entry_premium": entry,
                    "entry_time": etime, "exit_premium": target, "exit_time": t, "exit_reason": "target",
                    "premium_net": round((target - entry) * LOT[sym] - 220, 2)}
        if t == "15:10":
            return {"strike": strike, "expiry": exp, "premium_status": "COMPUTED", "entry_premium": entry,
                    "entry_time": etime, "exit_premium": cl, "exit_time": t, "exit_reason": "square_off",
                    "premium_net": round((cl - entry) * LOT[sym] - 220, 2)}
    last = eb[-1]
    return {"strike": strike, "expiry": exp, "premium_status": "COMPUTED", "entry_premium": entry,
            "entry_time": etime, "exit_premium": last[4], "exit_time": last[0], "exit_reason": "square_off",
            "premium_net": round((last[4] - entry) * LOT[sym] - 220, 2)}

def main():
    pidx = build_premium_index()
    print(f"cached premium contract-days: {len(pidx)}")
    variants = ["BASE", "V1", "V2", "V3", "V4", "V5", "V6", "V7", "V8", "V9", "V10", "V11"]
    all_rows = []
    for var in variants:
        for sym in ["NIFTY", "BANKNIFTY"]:
            trades, raw = run_variant(sym, var)
            for tr in trades:
                ps = prem_score(tr, pidx)
                row = {**tr, **ps}
                all_rows.append(row)
            comp = [t for t in trades]
            # summary computed from premium-scored rows only later; spot summary here
            ft_spot = sum(1 for t in trades if t["spot_reason"] == "target")
            print(f"{var} {sym}: legs={len(trades)} spot_net={sum(t['spot_net'] for t in trades):.2f} "
                  f"spot_FT={ft_spot} freq={len(trades)/18*5:.2f}")
            if var == "BASE":
                print("  raw:", raw)
    out = Path.home() / "workspace/trading/index_options_skill_tuned_oct30_trades.csv"
    fields = ["variant", "index", "date", "leg", "direction", "signal_time", "entry_time", "entry_spot",
              "strike", "expiry", "spot_net", "spot_reason", "exit_time", "entry_premium",
              "exit_premium", "exit_reason", "premium_net", "premium_status"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for r in all_rows:
            w.writerow(r)
    print("wrote", out, len(all_rows))
    # premium summaries
    for var in variants:
        for sym in ["NIFTY", "BANKNIFTY"]:
            rows = [r for r in all_rows if r["variant"] == var and r["index"] == sym]
            comp = [r for r in rows if r["premium_status"] == "COMPUTED"]
            nc = len(rows) - len(comp)
            net = sum(r["premium_net"] for r in comp)
            ft = sum(1 for r in comp if r["exit_reason"] == "target")
            print(f"PREM {var} {sym}: legs={len(rows)} computed={len(comp)} NOT_COMPUTED={nc} "
                  f"prem_net_computed={net:.2f} FT={ft}/{len(comp)} "
                  f"FT%={ft/len(comp)*100:.1f}% " if comp else f"PREM {var} {sym}: legs={len(rows)} computed=0",
                  f"freq_all={len(rows)/18*5:.2f} freq_computed={len(comp)/18*5:.2f}")
            for r in rows:
                print(f"   {r['date']} {r['leg']} {r['direction']} sig={r['signal_time']} entry_spot={r['entry_spot']} "
                      f"strike={r['strike']} spot={r['spot_net']}({r['spot_reason']}) prem={r.get('premium_net')}({r.get('exit_reason')},{r['premium_status']})")

if __name__ == "__main__":
    main()
