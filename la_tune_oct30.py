#!/usr/bin/env python3
"""(lA) tuning Oct 2026 — frozen definitions in index_options_la_tuned_oct30_frozen.md.
Paper only, no orders, no stocks. One knob per variant. Spot from cache; premiums
from cached candle files only (NOT_COMPUTED if absent; no browser fetch in this run).
"""
import sys, os, math, json, csv
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from pathlib import Path
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn, bn_break_time
from merged_skill_la_october import load_bank, day_data_bank, nifty_break_time
from close_reentry_sweep import replay_pe

T = Path.home() / "workspace/trading"
OUTD = T / "v4_options_oct_data"
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
LEGACY = {"NIFTY_22500PE_2026-10-23_2026-10-27": "candles_Nifty_50_22500PE_2026-10-23.json",
          "NIFTY_22600CE_2026-10-26_2026-10-26.json": "candles_Nifty_50_22600CE_2026-10-26.json",
          "NIFTY_22600CE_2026-10-26_2026-10-27": "candles_Nifty_50_22600CE_2026-10-26.json",
          "BANKNIFTY_54300PE_2026-10-26_2026-10-27": "candles_Nifty_Bank_54300PE_2026-10-26.json",
          "BANKNIFTY_54400PE_2026-10-23_2026-10-27": "candles_Nifty_Bank_54400PE_2026-10-23.json",
          "BANKNIFTY_55200PE_2026-10-21_2026-10-27": "candles_Nifty_Bank_55200PE_2026-10-21.json",
          "NIFTY_22500PE_2026-10-28_2026-11-03": "candles_Nifty_50_22500PE_2026-10-28.json"}
# fix legacy key typo guard: actual file for 26 Oct CE is dated 2026-10-27 expiry
LEGACY["NIFTY_22600CE_2026-10-26_2026-10-27"] = "candles_Nifty_50_22600CE_2026-10-26.json"

def atm(p):
    return int(round(p / 100.0) * 100)

def add5(t):
    h, m = int(t[:2]), int(t[3:5]) + 5
    if m >= 60: h += 1; m -= 60
    return f"{h:02d}:{m:02d}"

def room_below(close, pdh, pdc, pdl):
    lv = [l for l in sorted(set([pdh, pdc, pdl])) if l < close]
    return (close - max(lv)) if lv else math.inf

def or_levels(day_spot):
    oc = day_spot[day_spot["time"] < "09:30"]
    return float(oc["high"].max()), float(oc["low"].min())

def close_at(day_spot, t):
    r = day_spot[day_spot["time"] == t]
    return float(r.iloc[0]["close"]) if len(r) else None

def rescan(dd, bt, cutoff, width_cap_mult, room_gate):
    """Return (signal_dict_or_None, diag). Signal dict has cand, sig_idx, entry, stop, risk, room, ratio."""
    day_spot, pdh, pdc, pdl, bias, scale = dd
    orh, orl = or_levels(day_spot)
    ow = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    diag = {"orl": orl, "or_width": round(ow, 2), "width_cap": round(width_cap_mult * scale, 2),
            "width_fail": ow > width_cap_mult * scale, "first_raw": None, "gate_rejected": []}
    if diag["width_fail"]:
        # still record first raw qualifying close for diagnostics
        for _, c in cand.iterrows():
            if c["time"] < bt or c["time"] > cutoff: continue
            if float(c["close"]) < orl and float(c["close"]) < pdl:
                diag["first_raw"] = c["time"]; break
        return None, diag
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > cutoff or t < bt: continue
        cl = float(c["close"])
        if cl < orl and cl < pdl:
            if diag["first_raw"] is None: diag["first_raw"] = t
            room = room_below(cl, pdh, pdc, pdl)
            if room < 200 * scale:
                continue
            if i + 1 >= len(cand): return None, diag
            entry = float(cand.iloc[i + 1]["open"]); stop = float(c["high"]); risk = stop - entry
            if risk <= 0: continue
            ratio = room / risk if math.isfinite(room) else math.inf
            if room_gate and ratio < 1.5:
                diag["gate_rejected"].append((t, round(risk, 2), round(room, 2) if math.isfinite(room) else None, round(ratio, 3)))
                continue
            return {"cand": cand, "orl": orl, "sig_idx": i, "signal": t, "entry": entry, "stop": stop,
                    "risk": risk, "room": room, "ratio": ratio}, diag
    return None, diag

def morning_leg(sig):
    tr = replay_pe(sig["cand"], sig["sig_idx"] + 1, sig["entry"], sig["stop"], sig["entry"] - 2 * sig["risk"])
    return tr

def scan_reentry(cand, orl, stop_idx, morning_risk, pd_levels, band_lo, band_hi, mode, room_gate):
    """mode: base | skip_all | fail_after_1330. Returns (leg_or_None, diag_list)."""
    pdh, pdc, pdl = pd_levels
    diag = []
    for k in range(stop_idx + 1, len(cand)):
        c = cand.iloc[k]; t = c["time"]
        if t > "15:05": break
        if float(c["close"]) >= orl: continue
        if k + 1 >= len(cand):
            diag.append((t, "no_next_bar")); break
        entry = float(cand.iloc[k + 1]["open"]); stop = float(c["high"]); risk = stop - entry
        afternoon = t > "11:30"
        if not (risk > 0 and band_lo <= risk <= band_hi):
            if afternoon and mode == "base":
                diag.append((t, f"afternoon_first_fail_risk={risk:.2f}_band=[{band_lo},{band_hi:.2f}]_scan_ends")); break
            if afternoon and mode == "fail_after_1330" and t > "13:30":
                diag.append((t, f"afternoon_first_fail_after1330_risk={risk:.2f}_scan_ends")); break
            diag.append((t, f"band_fail_skip_risk={risk:.2f}_band=[{band_lo},{band_hi:.2f}]")); continue
        room = room_below(float(c["close"]), pdh, pdc, pdl)
        ratio = room / risk if math.isfinite(room) else math.inf
        if room_gate and ratio < 1.5:
            diag.append((t, f"room_gate_reject_risk={risk:.2f}_room={room:.2f}_ratio={ratio:.3f}_skip")); continue
        tr = replay_pe(cand, k + 1, entry, stop, entry - 2 * risk)
        tr.update({"signal": t, "entry_spot": entry, "risk": risk, "room": room, "ratio": ratio})
        return tr, diag
    return None, diag

def prem_score(sym, strike, direction, sig_time, date):
    exp = "2026-10-27" if date <= "2026-10-27" else "2026-11-03"
    tag = f"{sym}_{strike}{direction}_{date}_{exp}"
    p = OUTD / LEGACY.get(tag, f"candles_premium_{tag}.json")
    if not p.exists(): return None, exp
    d = json.loads(p.read_text())
    cs = sorted([(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in d["data"]["candles"]])
    eb = [c for c in cs if c[0] > sig_time]
    if not eb: return None, exp
    etime, entry = eb[0][0], eb[0][1]
    stop, target = entry - 50.0, entry + 90.0
    for (t, o, h, l, cl) in eb:
        if t > "15:10": break
        if l <= stop: return {"entry_premium": entry, "entry_time": etime, "exit_premium": stop, "exit_time": t, "exit_reason": "stop"}, exp
        if h >= target: return {"entry_premium": entry, "entry_time": etime, "exit_premium": target, "exit_time": t, "exit_reason": "target"}, exp
        if t == "15:10": return {"entry_premium": entry, "entry_time": etime, "exit_premium": cl, "exit_time": t, "exit_reason": "square_off"}, exp
    last = eb[-1]
    return {"entry_premium": entry, "entry_time": etime, "exit_premium": last[4], "exit_time": last[0], "exit_reason": "square_off"}, exp

def run_day(dd, dd_conf, sym, date, variant):
    """Returns (legs, diag). legs: list of leg dicts (morning and/or re-entry), spot-scored."""
    day_spot, pdh, pdc, pdl, bias, scale = dd
    _c = tuple(dd_conf) + (None,) * (6 - len(dd_conf))
    conf_spot, cpdh, cpdc, cpdl, cbias, cscale = _c
    if sym == "NIFTY":
        bt, corl, corh = bn_break_time(dd_conf, cpdl, "orl")
    else:
        bt, corl, corh = nifty_break_time((conf_spot, cpdh, cpdc, cpdl))
    diag = {"date": date, "sym": sym, "conf_break": bt, "conf_orl": corl}
    if bt is None: return [], diag
    # X2 / X3 day eligibility
    if variant == "X2":
        conf_cand = conf_spot[conf_spot["time"] >= "09:30"].reset_index(drop=True)
        idx = [i for i, (_, c) in enumerate(conf_cand.iterrows()) if c["time"] == bt]
        ok = False
        if idx and idx[0] + 1 < len(conf_cand):
            ok = float(conf_cand.iloc[idx[0] + 1]["close"]) < corl
        diag["x2_second_close_ok"] = ok
        if not ok: return [], diag
    if variant == "X3":
        bc = close_at(conf_spot, bt)
        ok = bc is not None and bc < cpdl
        diag["x3_break_close"] = bc; diag["x3_conf_pdl"] = cpdl; diag["x3_ok"] = ok
        if not ok: return [], diag
    # cutoff
    if variant == "W1": cutoff = "14:30" if bt < "11:30" else "11:30"
    elif variant == "W2": cutoff = "15:05" if bt < "11:30" else "11:30"
    elif variant == "W3": cutoff = "14:30" if bt < "10:30" else ("13:30" if bt < "11:30" else "11:30")
    else: cutoff = "13:30" if bt < "11:30" else "11:30"
    width_cap = 480 if variant == "BF1" else (240 if variant == "BF2" else 360)
    room_gate = variant in ("W1", "W2", "W3", "BF1", "BF2")
    sig, sdiag = rescan(dd, bt, cutoff, width_cap, room_gate)
    diag.update({k: v for k, v in sdiag.items() if k not in ("orl",)})
    diag["cutoff"] = cutoff
    if sig is None: return [], diag
    # X1 / X4 signal-level filters
    if variant == "X1":
        cc = close_at(conf_spot, sig["signal"])
        diag["x1_conf_close_at_signal"] = cc
        if cc is None or not (cc < corl): return [], diag
    if variant == "X4":
        et = add5(sig["signal"])
        cc = close_at(conf_spot, et)
        diag["x4_conf_close_at_entry"] = cc; diag["x4_entry_time"] = et
        if cc is None or not (cc < corl): return [], diag
    tr = morning_leg(sig)
    legs = [{"leg": "morning", "signal": sig["signal"], "entry_spot": sig["entry"], "stop_spot": sig["stop"],
             "risk": round(sig["risk"], 2), "room": round(sig["room"], 2) if math.isfinite(sig["room"]) else None,
             "ratio": round(sig["ratio"], 3) if math.isfinite(sig["ratio"]) else None,
             "spot_exit": tr["exit"], "spot_exit_time": tr["exit_time"], "spot_net": tr["net"],
             "exit_idx": tr["exit_idx"]}]
    if tr["exit"] == "stop":
        if variant == "RB1": lo, hi, mode = 10, 1.5 * sig["risk"], "base"
        elif variant == "RB2": lo, hi, mode = 5, 2.0 * sig["risk"], "base"
        elif variant == "S1": lo, hi, mode = 10, sig["risk"], "skip_all"
        elif variant == "S2": lo, hi, mode = 10, sig["risk"], "fail_after_1330"
        else: lo, hi, mode = 10, sig["risk"], "base"
        re, rdiag = scan_reentry(sig["cand"], sig["orl"], tr["exit_idx"], sig["risk"], (pdh, pdc, pdl),
                                 lo, hi, mode, room_gate=(variant in ("RB1", "RB2", "S1", "S2", "W1", "W2", "W3", "BF1", "BF2")))
        diag["re_diag"] = rdiag
        if re is not None:
            legs.append({"leg": "reentry", "signal": re["signal"], "entry_spot": re["entry_spot"],
                         "stop_spot": None, "risk": round(re["risk"], 2),
                         "room": round(re["room"], 2) if math.isfinite(re["room"]) else None,
                         "ratio": round(re["ratio"], 3) if math.isfinite(re["ratio"]) else None,
                         "spot_exit": re["exit"], "spot_exit_time": re["exit_time"], "spot_net": re["net"],
                         "exit_idx": re["exit_idx"]})
    return legs, diag

def main():
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    days = [d.date().isoformat() for d in daily_n["date"] if d.year == 2026 and d.month == 10]
    days = sorted(days)
    print("October days in cache:", len(days), days)
    variants = ["BASE", "W1", "W2", "W3", "RB1", "RB2", "BF1", "BF2", "S1", "S2", "X1", "X2", "X3", "X4"]
    all_legs, all_diag, summary = [], {}, {}
    for variant in variants:
        for sym in ("NIFTY", "BANKNIFTY"):
            legs_all = []
            for ds in days:
                dd_n = day_data_nifty(spot_n, daily_n, ds)
                dbn = day_data_bn(bn_spot, bn_daily, ds)
                dd_b = day_data_bank(bank_spot, bank_daily, ds)
                if sym == "NIFTY":
                    if not (dd_n and dbn): continue
                    legs, diag = run_day(dd_n, dbn, sym, ds, variant)
                else:
                    if not (dd_b and dd_n): continue
                    legs, diag = run_day(dd_b, (dd_n[0], dd_n[1], dd_n[2], dd_n[3], dd_n[4], dd_n[5]), sym, ds, variant)
                all_diag.setdefault(variant, {})[f"{sym}_{ds}"] = diag
                for lg in legs:
                    strike = atm(lg["entry_spot"])
                    ps, exp = prem_score(sym, strike, "PE", lg["signal"], ds)
                    row = {"variant": variant, "index": sym, "date": ds, **{k: v for k, v in lg.items() if k != "exit_idx"},
                           "strike": strike, "expiry": exp,
                           "premium_status": "COMPUTED" if ps else "NOT_COMPUTED",
                           "entry_premium": ps["entry_premium"] if ps else "",
                           "entry_time": ps["entry_time"] if ps else "",
                           "exit_premium": ps["exit_premium"] if ps else "",
                           "exit_time": ps["exit_time"] if ps else "",
                           "premium_exit": ps["exit_reason"] if ps else "",
                           "premium_net": round((ps["exit_premium"] - ps["entry_premium"]) * LOT[sym] - 220, 2) if ps else ""}
                    legs_all.append(row); all_legs.append(row)
            n = len(legs_all)
            comp = [r for r in legs_all if r["premium_status"] == "COMPUTED"]
            ft_p = sum(1 for r in comp if r["premium_exit"] == "target")
            ft_s = sum(1 for r in legs_all if r["spot_exit"] == "target")
            summary[(variant, sym)] = {"trades": n, "computed": len(comp),
                "premium_net_computed": round(sum(r["premium_net"] for r in comp), 2),
                "premium_ft": ft_p, "premium_ft_rate_computed": (round(ft_p / len(comp), 3) if comp else None),
                "spot_net": round(sum(r["spot_net"] for r in legs_all), 2), "spot_ft": ft_s,
                "freq_per_week": round(n / 18 * 5, 2),
                "green_spot": sum(1 for r in legs_all if r["spot_net"] > 0)}
            print(f"{variant} {sym}: legs={n} computed={len(comp)} prem_net(comp)={summary[(variant, sym)]['premium_net_computed']} "
                  f"prem_FT={ft_p}/{len(comp)} spot_net={summary[(variant, sym)]['spot_net']} spot_FT={ft_s} freq={summary[(variant, sym)]['freq_per_week']}/wk")
    with open(T / "index_options_la_tuned_oct30_legs.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(all_legs[0].keys())); w.writeheader(); w.writerows(all_legs)
    with open(T / "index_options_la_tuned_oct30_diag.json", "w") as f:
        json.dump(all_diag, f, indent=2, default=str)
    with open(T / "index_options_la_tuned_oct30_summary.json", "w") as f:
        json.dump({f"{k[0]}|{k[1]}": v for k, v in summary.items()}, f, indent=2)
    # base validation vs premium file
    import csv as _csv
    base_prem = {}
    for r in _csv.DictReader(open(T / "index_options_premium_october_trades.csv")):
        if r["version"].startswith("(lA)"):
            base_prem.setdefault(r["index"], []).append(r)
    for sym in ("NIFTY", "BANKNIFTY"):
        mine = [r for r in all_legs if r["variant"] == "BASE" and r["index"] == sym]
        ref = sorted([(r["date"], r["signal_time"], float(r["premium_net"])) for r in base_prem[sym]])
        got = sorted([(r["date"], r["signal"], r["premium_net"]) for r in mine])
        print(f"BASE VALIDATION {sym}: ref={ref}")
        print(f"BASE VALIDATION {sym}: got={got} match={ref == got}")

if __name__ == "__main__":
    main()
