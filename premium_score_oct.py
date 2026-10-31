#!/usr/bin/env python3
"""Score October v2 trades on real option premiums (paper only, no orders).
Frozen premium rule (options overlay, stated in premium_completion_oct.py):
entry premium = open of first 5-min option candle with time > spot signal time
(= the entry bar, signal+5min); stop = entry - 50 option points; target =
entry + 90 option points, for BOTH CE and PE (premium falls when wrong, rises
when right, either direction); stop checked before target on every bar
including the entry bar; square-off = 15:10 bar close; net = (exit-entry)*lot
- Rs 220 assumed cost; lot Nifty 65, Bank 30; strike ATM nearest 100 to entry
spot; expiry 2026-10-27 for trades 1-27 Oct, 2026-11-03 for 28 Oct.
This -50/+90 rule is the V4/V5-v2 options rule. It is NOT Skill's or (lA)'s
native spot rule (stop=signal high/low, target=2x spot risk) — those native
rules produce the spot nets shown alongside. Premiums do not move 1:1 with
spot, so no spot-risk translation is attempted.
Validates against the 6 previously computed v4 options trades first.
"""
import json, csv, os
from pathlib import Path

OUT = Path.home() / "workspace/trading/v4_options_oct_data"
LOT = {"NIFTY": 65, "BANKNIFTY": 30}
LEGACY = {"NIFTY_22500PE_2026-10-23_2026-10-27": "candles_Nifty_50_22500PE_2026-10-23.json",
          "NIFTY_22600CE_2026-10-26_2026-10-27": "candles_Nifty_50_22600CE_2026-10-26.json",
          "BANKNIFTY_54300PE_2026-10-26_2026-10-27": "candles_Nifty_Bank_54300PE_2026-10-26.json",
          "BANKNIFTY_54400PE_2026-10-23_2026-10-27": "candles_Nifty_Bank_54400PE_2026-10-23.json",
          "BANKNIFTY_55200PE_2026-10-21_2026-10-27": "candles_Nifty_Bank_55200PE_2026-10-21.json",
          "NIFTY_22500PE_2026-10-28_2026-11-03": "candles_Nifty_50_22500PE_2026-10-28.json"}
KNOWN = {("BANKNIFTY","2026-10-21","55200PE"): (379.95, 469.95, "11:35", "target", 2480.00),
         ("BANKNIFTY","2026-10-23","54400PE"): (321.55, 411.55, "10:05", "target", 2480.00),
         ("NIFTY","2026-10-23","22500PE"): (125.85, 108.70, "15:10", "square_off", -1334.75),
         ("NIFTY","2026-10-26","22600CE"): (197.55, 147.55, "11:05", "stop", -3470.00),
         ("BANKNIFTY","2026-10-26","54300PE"): (275.15, 365.15, "10:35", "target", 2480.00),
         ("NIFTY","2026-10-28","22500PE"): (200.95, 150.95, "11:00", "stop", -3470.00)}

def candles_for(r):
    tag = f"{r['index']}_{r['strike']}{r['direction']}_{r['date']}_{r['expiry']}"
    p = OUT / LEGACY.get(tag, f"candles_premium_{tag}.json")
    d = json.loads(p.read_text())
    cs = sorted(d["data"]["candles"], key=lambda c: c[0])
    return [(c[0][11:16], float(c[1]), float(c[2]), float(c[3]), float(c[4])) for c in cs]

def score(r):
    cs = candles_for(r)
    sig = r["signal_time"]
    entry_bars = [c for c in cs if c[0] > sig]
    if not entry_bars: return None
    etime, entry = entry_bars[0][0], entry_bars[0][1]
    stop, target = entry - 50.0, entry + 90.0
    for (t, o, h, l, cl) in entry_bars:
        if t > "15:10": break
        if l <= stop:
            return {"entry_premium": entry, "entry_time": etime, "stop_premium": stop, "target_premium": target,
                    "exit_premium": stop, "exit_time": t, "exit_reason": "stop"}
        if h >= target:
            return {"entry_premium": entry, "entry_time": etime, "stop_premium": stop, "target_premium": target,
                    "exit_premium": target, "exit_time": t, "exit_reason": "target"}
        if t == "15:10":
            return {"entry_premium": entry, "entry_time": etime, "stop_premium": stop, "target_premium": target,
                    "exit_premium": cl, "exit_time": t, "exit_reason": "square_off"}
    last = entry_bars[-1]
    return {"entry_premium": entry, "entry_time": etime, "stop_premium": stop, "target_premium": target,
            "exit_premium": last[4], "exit_time": last[0], "exit_reason": "square_off"}

def main():
    rows = list(csv.DictReader(open(Path.home() / "workspace/trading/index_options_premium_recon_oct.csv")))
    out = []
    for r in rows:
        s = score(r)
        if s is None:
            out.append({**r, "premium_status": "NOT_COMPUTED", "premium_net": ""}); print("NO_BARS", r); continue
        net = round((s["exit_premium"] - s["entry_premium"]) * LOT[r["index"]] - 220, 2)
        out.append({**r, **s, "premium_net": net, "premium_status": "COMPUTED", "lot": LOT[r["index"]]})
        k = (r["index"], r["date"], f"{r['strike']}{r['direction']}")
        if k in KNOWN:
            ke, kx, kt, kr, kn = KNOWN[k]
            ok = (abs(s["entry_premium"]-ke)<0.01 and abs(s["exit_premium"]-kx)<0.01 and s["exit_time"]==kt and s["exit_reason"]==kr and abs(net-kn)<0.01)
            print(("VALIDATION OK " if ok else "VALIDATION FAIL "), k, s, net, "expected", KNOWN[k])
    fields = list(out[0].keys())
    with open(Path.home() / "workspace/trading/index_options_premium_october_trades.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(out)
    print(f"scored {len(out)} trades, computed {sum(1 for o in out if o['premium_status']=='COMPUTED')}")
    for o in out:
        print(o["version"], o["index"], o["date"], o["setup"], o["direction"], "strike", o["strike"], o["expiry"],
              "entry", o.get("entry_premium"), "@", o.get("entry_time"), "exit", o.get("exit_premium"), "@", o.get("exit_time"),
              o.get("exit_reason"), "prem_net", o["premium_net"], "| spot_net", o["spot_net"], o["spot_exit"])

if __name__ == "__main__": main()
