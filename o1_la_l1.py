"""(lA) v2 L1 engine, Jan-Oct 2026 — implemented from the v2 frozen definition
(rescan cutoff 11:30 -> 13:30 ONLY where the confirmer broke before 11:30),
because the merged Jan-Oct JSONs use the base 11:30 rescan_trade and drop
2 October v2 days (Bank 8 Oct 13:15, Nifty 21 Oct 11:35). Paper only.
Nifty: confirmer Bank break = first Bank bar 09:30-11:30 close < Bank OR low.
Bank mirror: confirmer Nifty break = first Nifty bar 09:30-11:30 close < Nifty OR low.
Rescan: first bar >= confirmer break, <= cutoff, close < own OR low AND < own PDL,
OR width <= 360*scale, room >= 200*scale. Re-entry: scan_reentry 'lA'.
Cutoff reading tested: 'before 11:30' = break time < '11:30' (strict).
"""
import sys, os, math, json
sys.path.insert(0, os.path.expanduser("~/workspace/trading"))
import pandas as pd
from progressive_capped import load as load_sym
from timing_sweep import load as load_nifty, day_data as day_data_nifty
from reentry_filter_sweep import load_bn, day_data_bn, bn_break_time
from merged_skill_la_october import load_bank, day_data_bank, nifty_break_time
from close_reentry_sweep import replay_pe
from extended_window_sweep import scan_reentry

QTY, COST = 100, 40.0

def rescan_nifty_l1(dd, day_bn, strict=True):
    day_spot, pdh, pdc, pdl, bias, scale = dd
    bt, bn_orl, bn_orh = bn_break_time(day_bn, day_bn[3], "orl")
    if bt is None: return None
    cutoff = "13:30" if (bt < "11:30" if strict else bt <= "11:30") else "11:30"
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min()); or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > cutoff or t < bt: continue
        cl = float(c["close"])
        if cl < orl and cl < pdl:
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                if i + 1 >= len(cand): return None
                s = cand.iloc[i]; entry = float(cand.iloc[i + 1]["open"]); stop = float(s["high"]); risk = stop - entry
                tr = replay_pe(cand, i + 1, entry, stop, entry - 2 * risk)
                tr.update({"signal": s["time"], "bn_break": bt, "orl": orl})
                return {"candles": cand, "orl": orl, "sig_idx": i, "info": {"risk": risk, "signal": s["time"]}, "trade": tr}
    return None

def rescan_bank_l1(dd_bank, day_nifty, strict=True):
    day_spot, pdh, pdc, pdl, bias, scale = dd_bank
    bt, nf_orl, nf_orh = nifty_break_time(day_nifty)
    if bt is None: return None
    cutoff = "13:30" if (bt < "11:30" if strict else bt <= "11:30") else "11:30"
    or_c = day_spot[day_spot["time"] < "09:30"]
    orh = float(or_c["high"].max()); orl = float(or_c["low"].min()); or_width = orh - orl
    cand = day_spot[day_spot["time"] >= "09:30"].reset_index(drop=True)
    levels = sorted(set([pdh, pdc, pdl]))
    for i, (_, c) in enumerate(cand.iterrows()):
        t = c["time"]
        if t > cutoff or t < bt: continue
        cl = float(c["close"])
        if cl < orl and cl < pdl:
            nxt = [l for l in levels if l < cl]
            room = (cl - max(nxt)) if nxt else math.inf
            if or_width <= 360 * scale and room >= 200 * scale:
                if i + 1 >= len(cand): return None
                s = cand.iloc[i]; entry = float(cand.iloc[i + 1]["open"]); stop = float(s["high"]); risk = stop - entry
                tr = replay_pe(cand, i + 1, entry, stop, entry - 2 * risk)
                tr.update({"signal": s["time"], "nifty_break": bt, "orl": orl})
                return {"candles": cand, "orl": orl, "sig_idx": i, "info": {"risk": risk, "signal": s["time"]}, "trade": tr}
    return None

def day_la(r):
    if r is None: return {"morning": None, "re": None, "day_net": None}
    tr = r["trade"]
    if tr is None or tr.get("net") is None: return {"morning": tr, "re": None, "day_net": None}
    if tr.get("exit") != "stop": return {"morning": tr, "re": None, "day_net": tr["net"]}
    re, skipped = scan_reentry(r["candles"], r["orl"], tr["exit_idx"], r["info"]["risk"], "lA", tr["net"])
    day_net = round(tr["net"] + re["net"], 2) if (re and re["net"] is not None) else tr["net"]
    return {"morning": tr, "re": re, "day_net": day_net}

def run(strict=True):
    spot_n, daily_n = load_nifty()
    bn_spot, bn_daily = load_bn()
    bank_spot, bank_daily = load_bank()
    out = []
    days = [d.date().isoformat() for d in daily_n["date"] if d.year == 2026 and d.month <= 10]
    for ds in days:
        dd_n = day_data_nifty(spot_n, daily_n, ds)
        dbn = day_data_bn(bn_spot, bn_daily, ds)
        dd_b = day_data_bank(bank_spot, bank_daily, ds)
        rn = day_la(rescan_nifty_l1(dd_n, dbn, strict)) if (dd_n and dbn) else {"morning": None, "re": None, "day_net": None}
        day_nifty_tuple = (dd_n[0], dd_n[1], dd_n[2], dd_n[3]) if dd_n else None
        rb = day_la(rescan_bank_l1(dd_b, day_nifty_tuple, strict)) if (dd_b and day_nifty_tuple) else {"morning": None, "re": None, "day_net": None}
        for sym, res in (("NIFTY", rn), ("BANKNIFTY", rb)):
            m = res["morning"]
            if m is None or res["day_net"] is None: continue
            out.append({"method": "(lA)", "symbol": sym, "date": ds,
                        "setup": "la_pe_rescan_reentry", "direction": "PE",
                        "exit_reason": ("target" if res["day_net"] > 0 and res["re"] is None and m["exit"] == "target"
                                        else "day_green" if res["day_net"] > 0 else "day_loss"),
                        "net_rs": round(float(res["day_net"]), 2),
                        "morning_signal": m["signal"], "morning_exit": m["exit"], "morning_net": m["net"],
                        "re_signal": res["re"]["re_signal"] if res["re"] else None,
                        "re_exit": res["re"]["exit"] if res["re"] else None,
                        "re_net": res["re"]["net"] if res["re"] else None})
    return out

if __name__ == "__main__":
    for strict in (True, False):
        out = run(strict)
        oct_n = sorted([(t["date"], t["morning_signal"], t["net_rs"]) for t in out if t["symbol"] == "NIFTY" and t["date"].startswith("2026-10")])
        oct_b = sorted([(t["date"], t["morning_signal"], t["net_rs"]) for t in out if t["symbol"] == "BANKNIFTY" and t["date"].startswith("2026-10")])
        print(f"strict={strict} total={len(out)} Nifty={sum(1 for t in out if t['symbol']=='NIFTY')} Bank={sum(1 for t in out if t['symbol']=='BANKNIFTY')}")
        print("  OCT Nifty:", oct_n, "sum", sum(x[2] for x in oct_n))
        print("  OCT Bank:", oct_b, "sum", sum(x[2] for x in oct_b))
    out = run(True)
    with open("/tmp/la_l1_janoct.json", "w") as f:
        json.dump(out, f, indent=2)
